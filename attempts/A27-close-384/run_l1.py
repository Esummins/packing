#!/usr/bin/env python3
"""
A27 run_l1.py -- CONVERGE the level-1 nodes of A24's interior-first case tree at s = 96/25.

Level 1 (A24 section 5b, unchanged): under the certified root lemma A24.1 ("every packing of 11
unit squares in a square of side <= 96/25 has a square centred in Z = [11/10,137/50]^2") plus the
D4 WLOG, the fundamental triangle T = {(x,y): 48/25 <= y <= x <= 137/50} times [0,90] is covered by
216 parameter boxes (8x8 grid on T restricted to j<=i, 6 tilt bins of 15 deg).  Each box B is the
node "some packing square has (centre, theta) in B", budget 10.

Differences from A24's level1.py (COPIED here unmodified; it still supplies cover/check_cover):
  * T2 (wastage ledger) is NOT run per node.  A24 section 5c measured it: a single core strands at
    most 1.2812 of the 3.7456 area budget over the whole 216-box cover (A25 atlas), so T2 can never
    kill a one-core node.  Skipping it gives the LP the whole time budget.
  * warm start from A24's node result when it exists (A24 results/l1/n<idx>.json);
  * long time limit and a SOUND status rule (see classify).

  python run_l1.py --workers 9 --time_limit 1500
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
from level1 import cover, check_cover

A24 = os.path.abspath(os.path.join(HERE, '..', 'A24-composed-tree'))


def classify(res, budget):
    """SOUND status rule.

    The node LP is  min sum(w) over atom measures s.t. every legal placement covers mass >= 1.
    Restricting the ROWS (placements) under-estimates tau; restricting the COLUMNS (atoms)
    over-estimates it.  Hence:
      * a KILL needs a FEASIBLE measure of total < budget: no violated row in the last iteration
        (added_rows == 0 and minmass >= 1), which makes tau an attained, valid value.  An
        unconverged tau < budget is NOT a kill (A24 section 8).
      * 'alive' needs the full LP optimum: converged (no violated row AND no wanted column).
    Everything else is 'undecided'.
    """
    ht = res.get('hist_tail') or []
    last = ht[-1] if ht else {}
    feasible = (res.get('minmass') is not None and res['minmass'] >= 1 - 1e-6
                and last.get('added_rows', 1) == 0)
    tau = res['tau']
    if feasible and tau < budget - 1e-6:
        return 'dead(T1)'
    if res.get('converged') and tau >= budget - 1e-6:
        return 'alive'
    if feasible and tau >= budget - 1e-6:
        return 'alive?'
    return 'undecided'


def _work(args):
    (idx, s, bjson, tl, eps_geo, resume, tag) = args
    t0 = time.time()
    recp = os.path.join(HERE, 'results', tag, 'rec%d.json' % idx)
    if resume and os.path.exists(recp):
        try:
            return json.load(open(recp))
        except Exception:
            pass
    rec = dict(idx=idx, box=bjson)
    try:
        B = Box.from_json(bjson)
        hyp = Hyp([B], ())
        budget = 10
        out = os.path.join(HERE, 'results', tag, 'n%d.json' % idx)
        lp = os.path.join(HERE, 'logs', tag, 'n%d.log' % idx)
        lpbox.EPS_GEO = eps_geo

        def log(*a):
            with open(lp, 'a') as f:
                f.write(' '.join(str(x) for x in a) + '\n')
        log("### A27 L1 node %d %r budget=%d EPS_GEO=%s tl=%s" % (idx, B, budget, lpbox.EPS_GEO, tl))
        w = None
        for cand in (out, os.path.join(A24, 'results', 'l1', 'n%d.json' % idx)):
            if os.path.exists(cand):
                try:
                    w = warm_from_result(json.load(open(cand)))
                    log("# warm start from %s: %d atoms %d rows" % (cand, len(w['atoms']), len(w['rows'])))
                    break
                except Exception:
                    w = None
        res = solve_node(s, hyp, budget, sym_kind='C1', warm=w, time_limit=tl, out=out, log=log,
                         max_rows_add=1500, max_cols_add=1500, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=out.replace('.json', '_state.json'),
                         prune=6, prune_cols=2, alternate=True, max_iter=1000)
        ht = res.get('hist_tail') or [{}]
        rec.update(tau=res['tau'], slack=res['tau'] - budget, converged=res['converged'],
                   minmass=res['minmass'], maxcov=res['maxcov'], n_rows=res['n_rows'],
                   n_orbits=res['n_orbits'], last_added_rows=ht[-1].get('added_rows'),
                   last_added_cols=ht[-1].get('added_cols'), iters=ht[-1].get('it'))
        rec['status'] = classify(res, budget)
        rec['seconds'] = time.time() - t0
        log('RESULT ' + json.dumps({k: v for k, v in rec.items() if k != 'box'}))
    except Exception:
        rec['error'] = traceback.format_exc()[-1500:]
        rec['seconds'] = time.time() - t0
        rec['status'] = 'error'
    json.dump(rec, open(recp, 'w'), indent=1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', type=float, default=3.84)
    ap.add_argument('--nx', type=int, default=8)
    ap.add_argument('--nth', type=int, default=6)
    ap.add_argument('--workers', type=int, default=9)
    ap.add_argument('--time_limit', type=float, default=1500)
    ap.add_argument('--eps_geo', type=float, default=1e-4)
    ap.add_argument('--tag', default='l1')
    ap.add_argument('--lo', type=int, default=0)
    ap.add_argument('--hi', type=int, default=10 ** 6)
    ap.add_argument('--only', default=None)
    ap.add_argument('--no_resume', action='store_true')
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'results', a.tag), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', a.tag), exist_ok=True)
    boxes, geo = cover(a.s, a.nx, a.nth)
    chk = check_cover(a.s, boxes, a.nx, a.nth)
    print("cover: %d boxes; exact cover check ok=%s" % (len(boxes), chk['ok']), flush=True)
    assert chk['ok'], chk
    want = set(int(x) for x in a.only.split(',')) if a.only else None
    jobs = [(i, a.s, B.to_json(), a.time_limit, a.eps_geo, not a.no_resume, a.tag)
            for i, B in enumerate(boxes)
            if (want is None and a.lo <= i < a.hi) or (want is not None and i in want)]
    prev = {}
    p24 = os.path.join(A24, 'results', 'l1g_8x6.json')
    if os.path.exists(p24):
        for n in json.load(open(p24))['nodes']:
            prev[n['idx']] = n.get('tau') or 0.0
    jobs.sort(key=lambda j: -prev.get(j[0], 9.5))
    outp = os.path.join(HERE, 'results', '%s_summary.json' % a.tag)
    res, t0 = [], time.time()
    with mp.Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(_work, jobs):
            res.append(r)
            print("[%d/%d] idx=%s %s tau=%s conv=%s mm=%s cov=%s %.0fs"
                  % (len(res), len(jobs), r['idx'], r.get('status'), r.get('tau'),
                     r.get('converged'), r.get('minmass'), r.get('maxcov'), r.get('seconds', 0)),
                  flush=True)
            st = {}
            for x in res:
                st[x.get('status')] = st.get(x.get('status'), 0) + 1
            json.dump(dict(s=a.s, nx=a.nx, nth=a.nth, cover_check=chk, stats=st,
                           elapsed=time.time() - t0, nodes=res), open(outp, 'w'), indent=1)
    st = {}
    for r in res:
        st[r.get('status')] = st.get(r.get('status'), 0) + 1
    print("A27 L1 DONE %s in %.0fs -> %s" % (st, time.time() - t0, outp))


if __name__ == '__main__':
    main()
