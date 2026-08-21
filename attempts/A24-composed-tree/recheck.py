#!/usr/bin/env python3
"""
A24 recheck.py -- EXACT (pure Fraction) re-certification of a float dead-area map,
parallel over cells, targeting the budget.

The float map is only "certified modulo IEEE rounding"; the certificate proper is
the exact-mode branch-and-bound.  We do not need the whole map: it is enough to
exact-certify a SUBSET of the (pairwise interior-disjoint) cells whose total area
already exceeds s^2 - 11.  Cells are taken largest-first until the target is met,
with a safety surplus.

  python recheck.py --src results/sweep_law384_law384_k4_d030.json --k 4 --d 0.03 --a 3 \
                    --s 96/25 --workers 6 --surplus 0.15
"""
from __future__ import annotations

import argparse, json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import multiprocessing as mp
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dead_region import Certifier, Region
from kill_tests import budget_rat, check_disjoint
from sweep import cfg_pinwheel

_CERT = None
_CFG = None


def _init(cfg):
    global _CERT, _CFG
    _CFG = cfg
    placed = cfg_pinwheel(F(cfg['s']), cfg['k'], F(cfg['d']), cfg['a_deg'])
    _CERT = Certifier(F(cfg['s']), placed, mode='exact', depth_max=cfg['depth_max'])


def _cell(c):
    x0, y0, x1, y1 = (F(v) for v in c)
    D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    t0 = time.time()
    r = _CERT.certify(D, max_boxes=_CFG['max_boxes'])
    return (c, bool(r['passed']), str(D.area), r.get('boxes'), time.time() - t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--k', type=int, required=True)
    ap.add_argument('--d', default='0')
    ap.add_argument('--a', type=float, default=0.0)
    ap.add_argument('--s', default='96/25')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--surplus', type=float, default=0.15)
    ap.add_argument('--depth_max', type=int, default=42)
    ap.add_argument('--max_boxes', type=int, default=300000)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    src = json.load(open(a.src))
    cells = [tuple(c) for c in src['cells']]
    ok, bad = check_disjoint(cells)
    assert ok, f"cells not interior-disjoint: {bad}"
    bud = budget_rat(F(a.s))
    target = bud + F(a.surplus).limit_denominator(1000)
    # largest cells first (fewest B&B calls for the area)
    cells.sort(key=lambda c: -(F(c[2]) - F(c[0])) * (F(c[3]) - F(c[1])))
    sel, tot = [], F(0)
    for c in cells:
        if tot >= target:
            break
        sel.append(c)
        tot += (F(c[2]) - F(c[0])) * (F(c[3]) - F(c[1]))
    cfg = dict(s=a.s, k=a.k, d=a.d, a_deg=a.a, depth_max=a.depth_max, max_boxes=a.max_boxes)
    out = a.out or a.src.replace('.json', '_exact.json')
    print(f"budget={float(bud):.4f} target={float(target):.4f} selected {len(sel)}/{len(cells)} cells "
          f"(float area {float(tot):.4f}) workers={a.workers}", flush=True)
    t0 = time.time()
    area = F(0)
    passed, failed = [], []
    with mp.Pool(a.workers, initializer=_init, initargs=(cfg,)) as pool:
        for i, (c, ok_, ar, nb, dt) in enumerate(pool.imap_unordered(_cell, sel, chunksize=4)):
            if ok_:
                area += F(ar)
                passed.append(c)
            else:
                failed.append(c)
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(sel)} exact area={float(area):.4f} "
                      f"failed={len(failed)} {time.time()-t0:.0f}s", flush=True)
                json.dump(dict(area=str(area), area_float=float(area), n_sel=len(sel),
                               n_done=i + 1, n_failed=len(failed), cells=passed,
                               failed=failed, budget=str(bud), cfg=cfg,
                               dead=bool(area > bud), seconds=time.time() - t0),
                          open(out, 'w'), indent=1)
    res = dict(area=str(area), area_float=float(area), n_sel=len(sel), n_done=len(sel),
               n_failed=len(failed), cells=passed, failed=failed, budget=str(bud),
               budget_float=float(bud), cfg=cfg, dead=bool(area > bud),
               seconds=time.time() - t0, src=a.src)
    json.dump(res, open(out, 'w'), indent=1)
    print(f"EXACT DONE area={float(area)} ({area}) budget={float(bud)} "
          f"DEAD={res['dead']} failed={len(failed)} {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()
