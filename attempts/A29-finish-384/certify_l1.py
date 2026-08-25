#!/usr/bin/env python3
"""
A24 certify_l1.py -- certify every dead leaf of level 1 (parallel over leaves).

For each leaf node result `results/l1/n<i>.json` with status dead(T1), run A14's
certify.py: re-solve the node LP with the robustness margin EPS_GEO = 3e-3, build a
rational measure certificate (weights x1.03), and verify it with the EXACT verifier
`verify_case.py`; on failure feed the witness placements back as rows and retry.

Writes certs/casetree_3.84/leaf_<i>.json (+ .report.json) and a manifest.
"""
from __future__ import annotations

import argparse, json, os, subprocess, sys, time
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'certs', 'casetree_3.84')


def _one(args):
    idx, node_json, s_rat, eps_geo, rounds, time_limit, depth, scale = args
    out = os.path.join(OUT, f'leaf_{idx}.json')
    log = os.path.join(HERE, 'logs', 'l1cert', f'leaf_{idx}.log')
    cmd = [sys.executable, os.path.join(HERE, 'certify.py'), node_json,
           '--s_rat', s_rat, '--eps_geo', str(eps_geo), '--scale', str(scale),
           '--rounds', str(rounds), '--jobs', '1', '--depth', str(depth),
           '--time_limit', str(time_limit), '--max_cols', '600', '--out', out]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE)
    txt = p.stdout + p.stderr
    with open(log, 'w') as f:
        f.write(txt)
    ok = 'CERTIFIED:' in txt
    rep = out.replace('.json', '.report.json')
    total = None
    if os.path.exists(rep):
        try:
            total = json.load(open(rep)).get('total')
        except Exception:
            pass
    return dict(idx=idx, certified=bool(ok), total=total, seconds=time.time() - t0,
                cert=out if ok else None,
                tail=txt.strip().splitlines()[-1][:300] if txt.strip() else '')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--l1', default=os.path.join(HERE, 'results', 'l1f_8x6.json'))
    ap.add_argument('--s_rat', default='96/25')
    ap.add_argument('--eps_geo', type=float, default=0.003)
    ap.add_argument('--scale', type=float, default=1.03)
    ap.add_argument('--rounds', type=int, default=3)
    ap.add_argument('--time_limit', type=float, default=200)
    ap.add_argument('--depth', type=int, default=56)
    ap.add_argument('--workers', type=int, default=7)
    ap.add_argument('--only', default=None, help='comma list of leaf indices')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', 'l1cert'), exist_ok=True)
    L = json.load(open(a.l1))
    want = set(int(x) for x in a.only.split(',')) if a.only else None
    jobs = []
    for n in L['nodes']:
        if want is not None and n['idx'] not in want:
            continue
        if not str(n.get('status', '')).startswith('dead'):
            continue
        nj = os.path.join(HERE, 'results', 'l1', f"n{n['idx']}.json")
        if os.path.exists(nj):
            jobs.append((n['idx'], nj, a.s_rat, a.eps_geo, a.rounds, a.time_limit,
                         a.depth, a.scale))
    print(f"certifying {len(jobs)} dead leaves with {a.workers} workers", flush=True)
    res = []
    t0 = time.time()
    outp = os.path.join(HERE, 'results', 'l1_certs.json')
    with mp.Pool(min(a.workers, max(1, len(jobs)))) as pool:
        for r in pool.imap_unordered(_one, jobs):
            res.append(r)
            nok = sum(1 for x in res if x['certified'])
            print(f"[{len(res)}/{len(jobs)}] leaf {r['idx']}: "
                  f"{'PASS' if r['certified'] else 'FAIL'} total={r['total']} "
                  f"{r['seconds']:.0f}s  ({nok} certified so far)", flush=True)
            json.dump(dict(n=len(jobs), done=len(res), certified=nok,
                           elapsed=time.time() - t0, results=res),
                      open(outp, 'w'), indent=1)
    nok = sum(1 for x in res if x['certified'])
    print(f"CERT DONE {nok}/{len(jobs)} certified in {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
