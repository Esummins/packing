#!/usr/bin/env python3
"""
A27 refine.py -- refinement levels of the interior-first case tree.

A node is identified by a PATH string:  "<level1 idx>" for a level-1 box, "<idx>_<abc>" for one of
its 8 children (a,b,c in {0,1} = lower/upper half in x, y, theta), "<idx>_<abc>_<def>" for a
grandchild, and so on.  The 8 children of a box exactly tile it (the split points are the exact
midpoints), which `verify_tree2.py` re-checks in exact rationals.

Usage
  python refine.py children --parents 89,95,101 --tag l2            # write the child node list
  python refine.py solve    --tag l2 --workers 9 --time_limit 2400  # solve them to convergence
"""
from __future__ import annotations

import argparse, json, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpbox
from caselp import Box, Hyp, solve_node, warm_from_result
from level1 import cover
from run_l1 import classify
from prefilter import dead_by_band, Rlo

S = 3.84


def split8(B):
    """the 8 children of B (halve in x, y and theta); they exactly tile B."""
    xm, ym, tm = (B.x0 + B.x1) / 2, (B.y0 + B.y1) / 2, (B.th0 + B.th1) / 2
    out = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                x0, x1 = (B.x0, xm) if a == 0 else (xm, B.x1)
                y0, y1 = (B.y0, ym) if b == 0 else (ym, B.y1)
                t0, t1 = (B.th0, tm) if c == 0 else (tm, B.th1)
                out.append((f"{a}{b}{c}", Box(x0, x1, y0, y1, t0, t1)))
    return out


def box_of_path(path):
    """resolve a path string to its Box (level-1 index, then successive 8-way splits)."""
    boxes, _ = cover(S, 8, 6)
    parts = path.split('_')
    B = boxes[int(parts[0])]
    for p in parts[1:]:
        d = dict(split8(B))
        B = d[p]
    return B


def _work(args):
    (path, bjson, tl, eps_geo, tag, resume, warm_path) = args
    t0 = time.time()
    recp = os.path.join(HERE, 'results', tag, f'rec_{path}.json')
    if resume and os.path.exists(recp):
        try:
            return json.load(open(recp))
        except Exception:
            pass
    rec = dict(path=path, box=bjson)
    try:
        B = Box.from_json(bjson)
        hyp = Hyp([B], ())
        budget = 10
        rec['Rlo'] = Rlo(B, S)
        dead_band, why = dead_by_band([B], S)
        rec['band_prefilter'] = dict(dead=dead_band, why=why)
        if dead_band:
            rec['status'] = 'dead(A26.1)'
            rec['seconds'] = time.time() - t0
            json.dump(rec, open(recp, 'w'), indent=1)
            return rec
        out = os.path.join(HERE, 'results', tag, f'n_{path}.json')
        lp = os.path.join(HERE, 'logs', tag, f'n_{path}.log')
        lpbox.EPS_GEO = eps_geo

        def log(*a):
            with open(lp, 'a') as f:
                f.write(' '.join(str(x) for x in a) + '\n')
        log(f"### A27 node {path} {B!r} budget={budget} EPS_GEO={lpbox.EPS_GEO} tl={tl}")
        w = None
        for cand in (out, warm_path):
            if cand and os.path.exists(cand):
                try:
                    w = warm_from_result(json.load(open(cand)))
                    log(f"# warm start from {cand}: {len(w['atoms'])} atoms {len(w['rows'])} rows")
                    break
                except Exception:
                    w = None
        res = solve_node(S, hyp, budget, sym_kind='C1', warm=w, time_limit=tl, out=out, log=log,
                         max_rows_add=1500, max_cols_add=1500, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=out.replace('.json', '_state.json'),
                         prune=6, prune_cols=2, alternate=True, max_iter=1000)
        ht = res.get('hist_tail') or [{}]
        rec.update(tau=res['tau'], slack=res['tau'] - budget, converged=res['converged'],
                   minmass=res['minmass'], maxcov=res['maxcov'], n_rows=res['n_rows'],
                   last_added_rows=ht[-1].get('added_rows'), last_added_cols=ht[-1].get('added_cols'),
                   iters=ht[-1].get('it'))
        rec['status'] = classify(res, budget)
        rec['seconds'] = time.time() - t0
        log('RESULT ' + json.dumps({k: v for k, v in rec.items() if k != 'box'}))
    except Exception:
        rec['error'] = traceback.format_exc()[-1500:]
        rec['seconds'] = time.time() - t0
        rec['status'] = 'error'
    json.dump(rec, open(recp, 'w'), indent=1)
    return rec


def cmd_children(a):
    os.makedirs(os.path.join(HERE, 'results', a.tag), exist_ok=True)
    nodes = []
    for p in a.parents.split(','):
        p = p.strip()
        if not p:
            continue
        B = box_of_path(p)
        for suf, C in split8(B):
            nodes.append(dict(path=f"{p}_{suf}", box=C.to_json(), parent=p))
    fn = os.path.join(HERE, 'results', a.tag, 'nodes.json')
    json.dump(nodes, open(fn, 'w'), indent=1)
    print(f"{len(nodes)} children -> {fn}")


def cmd_solve(a):
    os.makedirs(os.path.join(HERE, 'results', a.tag), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', a.tag), exist_ok=True)
    nodes = json.load(open(os.path.join(HERE, 'results', a.tag, 'nodes.json')))
    if a.only:
        want = set(a.only.split(','))
        nodes = [n for n in nodes if n['path'] in want]
    jobs = []
    for n in nodes:
        par = n.get('parent', '')
        wp = None
        for cand in (os.path.join(HERE, 'results', a.parent_tag, f'n_{par}.json'),
                     os.path.join(HERE, 'results', 'l1', f'n{par}.json')):
            if os.path.exists(cand):
                wp = cand
                break
        jobs.append((n['path'], n['box'], a.time_limit, a.eps_geo, a.tag, not a.no_resume, wp))
    outp = os.path.join(HERE, 'results', f'{a.tag}_summary.json')
    res, t0 = [], time.time()
    with mp.Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(_work, jobs):
            res.append(r)
            print(f"[{len(res)}/{len(jobs)}] {r['path']} {r.get('status')} tau={r.get('tau')} "
                  f"conv={r.get('converged')} mm={r.get('minmass')} {r.get('seconds',0):.0f}s", flush=True)
            st = {}
            for x in res:
                st[x.get('status')] = st.get(x.get('status'), 0) + 1
            json.dump(dict(s=S, stats=st, elapsed=time.time() - t0, nodes=res),
                      open(outp, 'w'), indent=1)
    st = {}
    for r in res:
        st[r.get('status')] = st.get(r.get('status'), 0) + 1
    print(f"A27 {a.tag} DONE {st} in {time.time()-t0:.0f}s -> {outp}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('children'); c.add_argument('--parents', required=True); c.add_argument('--tag', default='l2')
    s = sub.add_parser('solve')
    s.add_argument('--tag', default='l2'); s.add_argument('--parent_tag', default='l2')
    s.add_argument('--workers', type=int, default=9); s.add_argument('--time_limit', type=float, default=2400)
    s.add_argument('--eps_geo', type=float, default=1e-4); s.add_argument('--only', default=None)
    s.add_argument('--no_resume', action='store_true')
    a = ap.parse_args()
    (cmd_children if a.cmd == 'children' else cmd_solve)(a)


if __name__ == '__main__':
    main()
