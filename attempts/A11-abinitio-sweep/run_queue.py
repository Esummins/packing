#!/usr/bin/env python3
"""
run_queue.py -- background job queue for the A11 ab-initio sweep.

  python run_queue.py jobs.json [--par 4] [--workers 4]

jobs.json: [{"n": 17, "angles": [0,45], "time": 600, "fix_s": null, "tag": "..."} ...]
Each job runs milp_pack.py (CP-SAT) as a subprocess; on completion the result JSON is compared with the
record (records.json), summarised and APPENDED to results.jsonl (one line per job, written immediately).
Jobs whose result file already exists are skipped (so the queue can be re-run / extended).
Matches (|s - record| <= 1e-6) and beats (s < record - 1e-9) trigger make_cert.py (exact verification);
beats additionally copy the certificate to NEW_RECORD_n<N>.json (+PNG).
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
RECORDS = json.load(open(os.path.join(HERE, 'records.json')))


def job_id(j):
    ang = '_'.join(f'{a:g}' for a in j['angles'])
    mode = f"fix{j['fix_s']:.6f}" if j.get('fix_s') is not None else 'free'
    return f"n{j['n']}_a{ang}_{mode}" + (f"_{j['tag']}" if j.get('tag') else '')


def launch(j, workers):
    jid = job_id(j)
    out = os.path.join(HERE, 'results', jid + '.json')
    png = os.path.join(HERE, 'plots', jid + '.png')
    log = open(os.path.join(HERE, 'logs', jid + '.log'), 'w')
    cmd = [PY, os.path.join(HERE, 'milp_pack.py'), '--n', str(j['n']), '--angles', ','.join(str(a) for a in j['angles']),
           '--solver', 'cpsat', '--threads', str(workers), '--time', str(j['time']), '--out', out, '--png', png,
           '--seed', str(j.get('seed', 0)), '--hint']
    if j.get('fix_s') is not None:
        cmd += ['--fix-s', repr(j['fix_s'])]
    if j.get('smax') is not None:
        cmd += ['--smax', repr(j['smax'])]
    if j.get('counts'):
        cmd += ['--counts', j['counts']]
    p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=HERE)
    return {'job': j, 'id': jid, 'proc': p, 'log': log, 'out': out, 'png': png, 't0': time.time()}


def finish(r):
    j = r['job']
    r['log'].close()
    rec = RECORDS[str(j['n'])]['record']
    summary = {'id': r['id'], 'n': j['n'], 'angles': j['angles'], 'time_limit': j['time'], 'fix_s': j.get('fix_s'),
               'record': rec, 'wall': time.time() - r['t0'], 'returncode': r['proc'].returncode}
    if os.path.exists(r['out']):
        res = json.load(open(r['out']))
        s = res.get('s')
        summary.update({'status': res.get('status'), 'bound': res.get('bound'), 's': s,
                        's_solver': res.get('s_solver'), 'structure': res.get('structure'),
                        'solver_time': res.get('time'), 'min_sep': res.get('polished_min_sep'),
                        'min_margin': res.get('polished_min_margin')})
        if s is not None:
            summary['gap'] = s - rec
            summary['match'] = abs(s - rec) <= 1e-6
            summary['beat'] = s < rec - 1e-9
            if summary['match'] or summary['beat']:
                cp = subprocess.run([PY, os.path.join(HERE, 'make_cert.py'), r['out']], capture_output=True, text=True, cwd=HERE)
                summary['cert_rc'] = cp.returncode
                summary['cert_tail'] = cp.stdout[-300:]
                cert = r['out'].replace('.json', '_cert.json')
                if summary['beat'] and cp.returncode == 0:
                    shutil.copy(cert, os.path.join(HERE, f"NEW_RECORD_n{j['n']}.json"))
                    if os.path.exists(r['png']):
                        shutil.copy(r['png'], os.path.join(HERE, f"NEW_RECORD_n{j['n']}.png"))
                    summary['NEW_RECORD'] = True
    else:
        summary['status'] = 'NO_OUTPUT'
    with open(os.path.join(HERE, 'results.jsonl'), 'a') as f:
        f.write(json.dumps(summary) + '\n')
    print(f"[done] {r['id']}: s={summary.get('s')} record={rec} gap={summary.get('gap')} "
          f"status={summary.get('status')} struct={summary.get('structure')} wall={summary['wall']:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('jobs')
    ap.add_argument('--par', type=int, default=4)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    jobs = json.load(open(a.jobs))
    pending = []
    for j in jobs:
        if os.path.exists(os.path.join(HERE, 'results', job_id(j) + '.json')):
            print('[skip]', job_id(j))
            continue
        pending.append(j)
    running = []
    while pending or running:
        while pending and len(running) < a.par:
            r = launch(pending.pop(0), a.workers)
            running.append(r)
            print(f"[start] {r['id']} (T={r['job']['time']}s)", flush=True)
        time.sleep(5)
        still = []
        for r in running:
            if r['proc'].poll() is None:
                still.append(r)
            else:
                finish(r)
        running = still
    print('[queue empty]', flush=True)


if __name__ == '__main__':
    main()
