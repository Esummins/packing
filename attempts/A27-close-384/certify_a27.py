#!/usr/bin/env python3
"""
A27 certify_a27.py -- certify every dead node of the A27 tree (level 1 and refinements).

For each node result n<idx>.json / n_<path>.json with a dead or near-dead LP, run A14's
certify.py: re-solve the node LP with the robustness margin EPS_GEO = 3e-3, build a rational
measure certificate (weights x scale, atoms on a 1e-6 grid) and verify it with the EXACT
verifier verify_case.py; on failure feed the witness placements back as rows and retry.

Two-stage scale policy:
  stage 1  --scale 1.03   (A24's setting: 3% headroom on every weight)
  stage 2  --scale 0      (auto: the largest scale in [1.005, 1.03] leaving 0.5% headroom under
                           the budget), used only if stage 1 reports "total >= budget" or FAILs.

Writes certs/casetree_3.84/leaf_<name>.json (+ .report.json) and results/certs_<tag>.json.

  python certify_a27.py --tag l1 --workers 9
"""
from __future__ import annotations

import argparse, glob, json, os, re, subprocess, sys, time
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'certs', 'casetree_3.84')


def _run(cmd, cwd=HERE):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def _one(args):
    name, node_json, s_rat, eps_geo, rounds, time_limit, depth, stages, resolve_time = args
    out = os.path.join(OUT, f'leaf_{name}.json')
    logd = os.path.join(HERE, 'logs', 'cert')
    os.makedirs(logd, exist_ok=True)
    t0 = time.time()
    txt_all = []
    ok = False
    used = None
    for scale in stages:
        cmd = [sys.executable, os.path.join(HERE, 'certify.py'), node_json,
               '--s_rat', s_rat, '--eps_geo', str(eps_geo), '--scale', str(scale),
               '--rounds', str(rounds), '--jobs', '1', '--depth', str(depth),
               '--time_limit', str(time_limit), '--resolve_time', str(resolve_time),
               '--max_cols', '800', '--out', out]
        rc, txt = _run(cmd)
        txt_all.append(f"##### scale={scale} rc={rc}\n" + txt)
        if 'CERTIFIED:' in txt:
            ok, used = True, scale
            break
    with open(os.path.join(logd, f'{name}.log'), 'w') as f:
        f.write('\n'.join(txt_all))
    total = None
    rep = out.replace('.json', '.report.json')
    if ok and os.path.exists(rep):
        try:
            total = json.load(open(rep)).get('total')
        except Exception:
            pass
    if not ok and os.path.exists(out):
        os.remove(out)          # never leave an unverified certificate in the certs directory
    tail = ''
    for ln in reversed('\n'.join(txt_all).strip().splitlines()):
        if ln.strip():
            tail = ln.strip()[:300]
            break
    return dict(name=name, certified=bool(ok), scale=used, total=total,
                seconds=time.time() - t0, node=node_json, tail=tail)


def collect(tag, slack_max, only=None):
    """(name, node_json) for every solved node of `tag` whose LP slack is below slack_max."""
    jobs = []
    if tag == 'l1':
        recs = sorted(glob.glob(os.path.join(HERE, 'results', 'l1', 'rec*.json')))
        for p in recs:
            r = json.load(open(p))
            name = str(r['idx'])
            nj = os.path.join(HERE, 'results', 'l1', f"n{r['idx']}.json")
            if r.get('slack') is not None and r['slack'] < slack_max and os.path.exists(nj):
                jobs.append((name, nj, r))
    else:
        recs = sorted(glob.glob(os.path.join(HERE, 'results', tag, 'rec_*.json')))
        for p in recs:
            r = json.load(open(p))
            name = r['path']
            nj = os.path.join(HERE, 'results', tag, f"n_{name}.json")
            if r.get('slack') is not None and r['slack'] < slack_max and os.path.exists(nj):
                jobs.append((name, nj, r))
    if only:
        want = set(only.split(','))
        jobs = [j for j in jobs if j[0] in want]
    jobs.sort(key=lambda j: j[2].get('slack', 0))        # easiest (most negative slack) first
    return [(n, p) for n, p, _ in jobs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='l1')
    ap.add_argument('--s_rat', default='96/25')
    ap.add_argument('--eps_geo', type=float, default=0.003)
    ap.add_argument('--rounds', type=int, default=3)
    ap.add_argument('--time_limit', type=float, default=400)
    ap.add_argument('--resolve_time', type=float, default=200)
    ap.add_argument('--depth', type=int, default=56)
    ap.add_argument('--workers', type=int, default=9)
    ap.add_argument('--slack_max', type=float, default=-0.02)
    ap.add_argument('--nodes_dir', default=None)
    ap.add_argument('--only', default=None)
    ap.add_argument('--skip_done', action='store_true', default=True)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    todo = collect(a.tag, a.slack_max, a.only)
    if a.skip_done:
        todo = [(n, p) for n, p in todo
                if not os.path.exists(os.path.join(OUT, f'leaf_{n}.json'))]
    stages = (1.03, 0)
    jobs = [(n, p, a.s_rat, a.eps_geo, a.rounds, a.time_limit, a.depth, stages, a.resolve_time)
            for n, p in todo]
    print(f"certifying {len(jobs)} nodes of tag {a.tag} with {a.workers} workers", flush=True)
    outp = os.path.join(HERE, 'results', f'certs_{a.tag}.json')
    res, t0 = [], time.time()
    if not jobs:
        json.dump(dict(n=0, results=[]), open(outp, 'w'), indent=1)
        return
    with mp.Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(_one, jobs):
            res.append(r)
            nok = sum(1 for x in res if x['certified'])
            print(f"[{len(res)}/{len(jobs)}] {r['name']}: {'PASS' if r['certified'] else 'FAIL'} "
                  f"scale={r['scale']} total={r['total']} {r['seconds']:.0f}s ({nok} ok)", flush=True)
            json.dump(dict(n=len(jobs), done=len(res), certified=nok,
                           elapsed=time.time() - t0, results=res), open(outp, 'w'), indent=1)
    nok = sum(1 for x in res if x['certified'])
    print(f"CERT DONE {nok}/{len(jobs)} certified in {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
