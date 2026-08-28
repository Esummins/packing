#!/usr/bin/env python3
"""
A24 level1.py -- LEVEL 1 of the composed tree under the CERTIFIED root lemma.

ROOT (certified, `certs_wip/thm_interior_occupancy.json`, exact verify_case.py PASS):
  every packing of 11 unit squares in a square of side <= 96/25 = 3.84 has a square
  whose centre lies in the closed INTERIOR ZONE  Z = [11/10, 137/50]^2.
  (LP: tau = 8.000 vs budget 11, certificate total 1030019/125000 = 8.240152.)

D4 WLOG (valid: the root hypothesis set is empty, A14 §1).  Z is invariant under the
symmetry group D4 of the container ([0,s]^2 and Z share the centre (s/2, s/2)), so we
may rotate/reflect the packing until the witness square's centre lies in the closed
fundamental triangle
      T = { (x, y) : s/2 <= y <= x <= s/2 + cw }      (cw = 0.82 = half-width of Z)
whose 8 D4 images cover Z.  Orientations stay in [0,90] (a rotation fixes theta mod 90,
a reflection maps theta -> 90 - theta).

LEVEL 1 = a closed cover of T x [0,90] by parameter boxes.  Each box B gives the node
"some packing square has (c, theta) in B" (budget 10).  If EVERY box node is dead --
by T1 (coverage LP, certified by verify_case.py) or T2 (wastage ledger, exact
dead-area certificate) -- then s(11) >= 3.84.

  python level1.py --nx 2 --nth 3 --workers 6 --time_limit 900
"""
from __future__ import annotations

import argparse, json, math, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpbox
import caselp
from caselp import Box, Hyp, solve_node, warm_from_result
from kill_tests import wastage_test, budget_rat, check_disjoint

CW = 0.6          # zone half-margin: Z = [0.5+cw, s-0.5-cw]^2


def cover(s, nx, nth, cw=CW):
    """closed cover of T x [0,90] by grid boxes that meet the fundamental triangle T."""
    a, b = 0.5 + cw, s - 0.5 - cw          # Z = [a, b]^2
    m = (a + b) / 2.0                       # container/zone centre
    h = (b - a) / 2.0                       # = b - m
    out = []
    for i in range(nx):
        x0, x1 = m + h * i / nx, m + h * (i + 1) / nx
        for j in range(i + 1):              # j <= i : boxes meeting {y <= x}
            y0, y1 = m + h * j / nx, m + h * (j + 1) / nx
            for k in range(nth):
                th0, th1 = 90.0 * k / nth, 90.0 * (k + 1) / nth
                B = Box(x0, x1, y0, y1, th0, th1)
                if B.vacuous(s) or B.core() is None:
                    continue
                out.append(B)
    return out, (a, b, m, h)


def check_cover(s, boxes, nx, nth, cw=CW):
    """exact check (rationals) that the 8 D4 images of the grid boxes cover Z x [0,90]:
    the grid cells {[m+h*i/nx, m+h*(i+1)/nx] x [m+h*j/nx, ...] : j <= i} tile T, the 8
    images of T tile Z, and the theta cuts 90k/nth partition [0,90]."""
    a, b = F(s).limit_denominator(10 ** 6), None
    A = F(1, 2) + F(cw).limit_denominator(10 ** 6)
    B_ = F(s).limit_denominator(10 ** 6) - F(1, 2) - F(cw).limit_denominator(10 ** 6)
    m, h = (A + B_) / 2, (B_ - A) / 2
    # theta cuts share endpoints
    cuts = [F(90 * k, nth) for k in range(nth + 1)]
    ok_th = (cuts[0] == 0 and cuts[-1] == 90 and
             all(cuts[k] < cuts[k + 1] for k in range(nth)))
    # grid cuts share endpoints and reach the corner of T
    gc = [m + h * F(i, nx) for i in range(nx + 1)]
    ok_g = (gc[0] == m and gc[-1] == B_ and all(gc[i] < gc[i + 1] for i in range(nx)))
    # every (i,j) with j <= i is present for every k (unless vacuous, which we forbid)
    have = {(round(bx.x0, 9), round(bx.y0, 9), round(bx.th0, 9)) for bx in boxes}
    ok_all = True
    for i in range(nx):
        for j in range(i + 1):
            for k in range(nth):
                key = (round(float(gc[i]), 9), round(float(gc[j]), 9), round(float(cuts[k]), 9))
                if key not in have:
                    ok_all = False
    return dict(theta_partition=ok_th, grid_partition=ok_g, all_cells_present=ok_all,
                Z=[str(A), str(B_)], m=str(m), h=str(h), n_boxes=len(boxes),
                ok=bool(ok_th and ok_g and ok_all))


def _work(args):
    (idx, s, bjson, tl, eps_geo, t2_min_cell, warm) = args
    t0 = time.time()
    rec = dict(idx=idx, box=bjson)
    try:
        B = Box.from_json(bjson)
        hyp = Hyp([B], ())
        budget = 10
        out = os.path.join(HERE, 'results', 'l1', f'n{idx}.json')
        lp = os.path.join(HERE, 'logs', 'l1', f'n{idx}.log')
        # --- T2 (wastage ledger)
        try:
            r2 = wastage_test(F(s).limit_denominator(10 ** 6), hyp=hyp,
                              min_cell=F(1, t2_min_cell), cell0=F(20, 100), mode='float',
                              depth_max=24, max_boxes_per_cell=1200, verbose=False)
            dj, _ = check_disjoint(r2['cells'])
            rec['t2'] = dict(area=r2['area_float'], budget=r2['budget_float'],
                             dead=bool(r2['dead_node'] and dj), n_cells=len(r2['cells']))
            json.dump(r2, open(out.replace('.json', '_t2.json'), 'w'), indent=1)
        except Exception:
            rec['t2'] = dict(error=traceback.format_exc()[-400:])
        if rec['t2'].get('dead'):
            rec['status'] = 'dead(T2)'
            rec['seconds'] = time.time() - t0
            return rec
        # --- T1 (coverage LP)
        if eps_geo is not None:
            lpbox.EPS_GEO = eps_geo

        def log(*a):
            with open(lp, 'a') as f:
                f.write(' '.join(str(x) for x in a) + '\n')
        log(f"### L1 node {idx} {B!r} budget={budget} EPS_GEO={lpbox.EPS_GEO}")
        w = None
        if warm and os.path.exists(warm):
            w = warm_from_result(json.load(open(warm)))
        res = solve_node(s, hyp, budget, sym_kind='C1', warm=w, time_limit=tl, out=out, log=log,
                         max_rows_add=1500, max_cols_add=1500, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=out.replace('.json', '_state.json'),
                         prune=6, prune_cols=2, alternate=True)
        rec.update(tau=res['tau'], slack=res['tau'] - budget, converged=res['converged'],
                   minmass=res['minmass'], maxcov=res['maxcov'], n_rows=res['n_rows'])
        if res['converged'] and rec['slack'] < -1e-6:
            rec['status'] = 'dead(T1)'
        elif rec['slack'] < -0.03 and res['minmass'] >= 0.97:
            rec['status'] = 'dead?(T1)'
        else:
            rec['status'] = 'alive'
        rec['seconds'] = time.time() - t0
        log('RESULT ' + json.dumps({k: v for k, v in rec.items() if k != 'box'}))
        return rec
    except Exception:
        rec['error'] = traceback.format_exc()[-1200:]
        rec['seconds'] = time.time() - t0
        rec['status'] = 'error'
        return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', type=float, default=3.84)
    ap.add_argument('--nx', type=int, default=2)
    ap.add_argument('--nth', type=int, default=3)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--time_limit', type=float, default=900)
    ap.add_argument('--eps_geo', type=float, default=1e-4)
    ap.add_argument('--t2_min_cell', type=int, default=16)
    ap.add_argument('--tag', default='l1')
    ap.add_argument('--warm', default='')
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'results', 'l1'), exist_ok=True)
    os.makedirs(os.path.join(HERE, 'logs', 'l1'), exist_ok=True)
    boxes, geo = cover(a.s, a.nx, a.nth)
    chk = check_cover(a.s, boxes, a.nx, a.nth)
    print(f"cover: {len(boxes)} boxes over T x [0,90] (nx={a.nx}, nth={a.nth}); "
          f"exact cover check: {chk}", flush=True)
    assert chk['ok'], chk
    jobs = [(i, a.s, B.to_json(), a.time_limit, a.eps_geo, a.t2_min_cell, a.warm)
            for i, B in enumerate(boxes)]
    outp = os.path.join(HERE, 'results', f'{a.tag}_{a.nx}x{a.nth}.json')
    res = []
    t0 = time.time()
    with mp.Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(_work, jobs):
            res.append(r)
            print(json.dumps({k: v for k, v in r.items()
                              if k in ('idx', 'status', 'tau', 'slack', 'converged',
                                       'minmass', 'seconds')}) +
                  f"  box={Box.from_json(r['box'])!r}" if 'box' in r else json.dumps(r), flush=True)
            json.dump(dict(s=a.s, nx=a.nx, nth=a.nth, cover_check=chk, geo=str(geo),
                           budget_area=str(budget_rat(F(a.s).limit_denominator(10 ** 6))),
                           elapsed=time.time() - t0, nodes=res), open(outp, 'w'), indent=1)
    st = {}
    for r in res:
        st[r.get('status')] = st.get(r.get('status'), 0) + 1
    print(f"LEVEL1 DONE {st} in {time.time()-t0:.0f}s -> {outp}")


if __name__ == '__main__':
    main()
