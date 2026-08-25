#!/usr/bin/env python3
"""
A29 finish.py -- one resumable, unattended pipeline that finishes the case tree at s = 96/25.

  stage 1  certify the open level-1 cells                (certify_a27.py, easiest first)
  stage 2  seed the refinement queue from the closure verdict
  stage 3  certify-or-refine the frontier, depth by depth (drive.py)
  stage 4  EXACT end-to-end re-verification of the whole tree (verify_tree2.py, leaves in a pool)
  stage 5  certificate manifest

Every stage is idempotent and every verdict is a file on disk, so the machine can be powered off
at any point and `python finish.py` restarted with the same arguments.

  python finish.py --workers 9 --max_depth 4
"""
from __future__ import annotations

import argparse, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, 'logs')
WORK = os.path.join(HERE, 'results', 'a29')


def say(*a):
    print(f'[{time.strftime("%H:%M:%S")}]', *a, flush=True)


def run(cmd, log):
    say('RUN', ' '.join(str(c) for c in cmd), '->', os.path.basename(log))
    with open(log, 'a') as f:
        f.write(f'\n===== {time.strftime("%Y-%m-%d %H:%M:%S")} {" ".join(map(str, cmd))}\n')
        f.flush()
        p = subprocess.run(cmd, cwd=HERE, stdout=f, stderr=subprocess.STDOUT)
    say('   rc =', p.returncode)
    return p.returncode


def phaseA_done():
    p = os.path.join(HERE, 'results', 'certs_l1.json')
    if not os.path.exists(p):
        return False
    try:
        d = json.load(open(p))
    except Exception:
        return False
    return d.get('done') is not None and d['done'] >= d.get('n', 10 ** 9)


def phaseA_alive():
    """True while an EARLIER, still-running certify_a27.py owns the level-1 stage (this pipeline is
    started while that run is already in flight).  Process-table based, so a reboot -- after which
    nothing is running -- correctly reports False and the stage is simply resumed."""
    p = os.path.join(LOGS, 'phaseA.out')
    if os.path.exists(p) and 'CERT DONE' in open(p, errors='ignore').read():
        return False
    try:
        q = subprocess.run(['wmic', 'process', 'where', "name='python.exe'", 'get', 'commandline'],
                           capture_output=True, text=True, timeout=120)
        return any('certify_a27.py' in l for l in q.stdout.splitlines())
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=9)
    ap.add_argument('--max_depth', type=int, default=4)
    ap.add_argument('--resolve_time', type=float, default=400)
    ap.add_argument('--time_limit', type=float, default=400)
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--max_cols', type=int, default=400)
    ap.add_argument('--a_resolve_time', type=float, default=500)
    ap.add_argument('--skip_phaseA', action='store_true')
    a = ap.parse_args()
    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(WORK, exist_ok=True)
    py = sys.executable
    t0 = time.time()

    # ---------- stage 1: the open level-1 cells -------------------------------------------
    if not a.skip_phaseA:
        miss = 0
        while miss < 5:            # 5 consecutive negatives: never race a still-running stage 1
            miss = 0 if phaseA_alive() else miss + 1
            if miss:
                time.sleep(20)
            else:
                time.sleep(60)
        if not phaseA_done():
            only = os.path.join(HERE, 'results', 'phaseA_only.txt')
            args = [py, 'certify_a27.py', '--tag', 'l1', '--workers', str(a.workers),
                    '--resolve_time', str(a.a_resolve_time), '--time_limit', '500',
                    '--rounds', '3', '--slack_max', '-0.01']
            if os.path.exists(only):
                args += ['--only', open(only).read().strip()]
            run(args, os.path.join(LOGS, 'phaseA.out'))
        say('stage 1 (level-1 certification) complete')

    # ---------- stages 2+3: refine the frontier --------------------------------------------
    run([py, 'drive.py', 'seed'], os.path.join(LOGS, 'drive.out'))
    run([py, 'drive.py', 'run', '--workers', str(a.workers), '--max_depth', str(a.max_depth),
         '--resolve_time', str(a.resolve_time), '--time_limit', str(a.time_limit),
         '--rounds', str(a.rounds), '--max_cols', str(a.max_cols)],
        os.path.join(LOGS, 'drive.out'))
    say('stage 3 (refinement) complete')

    # ---------- stage 4: exact end-to-end verification -------------------------------------
    rc = run([py, 'verify_tree2.py', '--pool', str(a.workers), '--jobs', '1',
              '--out', os.path.join(HERE, 'results', 'verify_tree2_final.json')],
             os.path.join(LOGS, 'verify_final.out'))
    say('stage 4 (exact verification) rc =', rc)

    # ---------- stage 5: manifest -----------------------------------------------------------
    run([py, 'make_manifest.py'], os.path.join(LOGS, 'manifest.out'))

    rep = json.load(open(os.path.join(HERE, 'results', 'verify_tree2_final.json')))
    cl = rep['checks']['closure']
    say(f'FINISH: integrity={rep["ok"]} closed={rep["closed"]} '
        f'{cl["n_covered"]}/{cl["n_cells"]} cells; open={cl["missing"]}')
    say(f'total wall time {(time.time()-t0)/3600:.2f} h')


if __name__ == '__main__':
    main()
