#!/usr/bin/env python3
"""
A24 sweep.py -- the WASTAGE SCALING LAW at s = 3.84 (and 3.83).

The scientific question that decides whether the composed tree can close:
  how much certified dead area does a node hypothesis with k interior mid-tilt
  CORE BOXES strand, as a function of k and of the core box size?
The tree cost is (#boxes needed to cover the branch family)^k, which grows like
(1/size)^(3k); the kill needs sum dead > s^2 - 11 = 2341/625 = 3.7456 at 3.84.
So the pair (size, k) that first exceeds the budget IS the feasibility verdict.

Configurations: the A12 interior pinwheel 4-cycle (the structure that holds
tau* = 11 for every LP relaxation, A10/A12/A14/A19), rescaled to the target s,
with each member replaced by a PlacedBox core of centre half-width d and
orientation half-width a degrees.  k = 1, 2, 3, 4 members.

Every number is a certified LOWER bound (float-interval mode with outward guards;
the flagship rows are re-certified in exact Fraction mode by recheck.py).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

from dead_region import PlacedBox, Placed, cos_sin, _convex_interior_disjoint
from kill_tests import wastage_test, budget_rat, check_disjoint

S386 = F(193, 50)
S384 = F(96, 25)
S383 = F(383, 100)
T33 = F(295521, 1000000)               # tan(16.5 deg) = t of theta = 33 deg


def deg_t(th):
    import math
    return F(round(math.tan(math.radians(th) / 2) * 10 ** 7), 10 ** 7)


def pinwheel_centres(s):
    """the A12 interior 4-cycle TRANSLATED (not scaled) from the 3.86 container into
    the side-s container.  Scaling by s/3.86 < 1 would shrink the mutual gaps (which
    are only +2.4e-4 at 3.86) and make the members overlap -- at 3.84 the 4-cycle
    can only be realised RIGIDLY.  A rigid translation preserves exact pairwise
    disjointness; the 4-cycle's footprint (centres in [1.3195, 2.5405] + half-diag
    0.7072 = [0.612, 3.248]) fits inside [0, 3.84]^2 and inside [0, 3.83]^2."""
    sh = (F(s) - S386) / 2
    base = [(F(2459700, 1000000), F(2540486, 1000000)),
            (S386 - F(2540486, 1000000), F(2459700, 1000000)),
            (S386 - F(2459700, 1000000), S386 - F(2540486, 1000000)),
            (F(2540486, 1000000), S386 - F(2459700, 1000000))]
    return [(x + sh, y + sh) for (x, y) in base]


def cfg_pinwheel(s, k, d, a_deg, order=(0, 1, 2, 3)):
    """k core boxes on the rescaled pinwheel; d = centre half-width, a_deg = theta
    half-width in degrees around 33 deg.  d = 0 gives exact Placed squares."""
    s = F(s)
    C = pinwheel_centres(s)
    idx = list(order)[:k]
    if d == 0 and a_deg == 0:
        pl = [Placed(C[i][0], C[i][1], T33) for i in idx]
        for i in range(len(pl)):
            for j in range(i + 1, len(pl)):
                assert _convex_interior_disjoint(pl[i].corners, pl[j].corners), (i, j)
        return pl
    t0, t1 = deg_t(33 - a_deg), deg_t(33 + a_deg)
    d = F(d)
    return [PlacedBox(t0, t1, C[i][0] - d, C[i][0] + d, C[i][1] - d, C[i][1] + d) for i in idx]


def one(job):
    name, s, k, d, a_deg, min_cell, cell0, order = job
    t0 = time.time()
    try:
        placed = cfg_pinwheel(s, k, d, a_deg, order)
        r = wastage_test(s, placed=placed, min_cell=F(1, min_cell), cell0=F(cell0, 100),
                         mode='float', depth_max=24, max_boxes_per_cell=1500, verbose=False)
        dj, _ = check_disjoint(r['cells'])
        r.update(name=name, k=k, d=float(d), a_deg=a_deg, disjoint=dj,
                 wall=time.time() - t0, min_cell=min_cell)
        out = os.path.join(HERE, 'results', f'sweep_{name}.json')
        json.dump(r, open(out, 'w'), indent=1)
        return dict(name=name, s=str(s), k=k, d=float(d), a_deg=a_deg,
                    area=r['area_float'], budget=r['budget_float'],
                    frac=r['fraction_of_budget'], dead=r['dead_node'],
                    cells=len(r['cells']), disjoint=dj, seconds=time.time() - t0)
    except Exception as e:
        import traceback
        return dict(name=name, error=traceback.format_exc()[-800:], seconds=time.time() - t0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--min_cell', type=int, default=32)
    ap.add_argument('--tag', default='law384')
    ap.add_argument('--s', default='96/25')
    a = ap.parse_args()
    s = F(a.s)
    jobs = []
    # (i) the k-scaling at the finest core (d = 0.01, a = 1 deg) and at exact placements
    for k in (1, 2, 3, 4):
        jobs.append((f'{a.tag}_k{k}_exact', s, k, 0, 0, a.min_cell, 16, (0, 1, 2, 3)))
        jobs.append((f'{a.tag}_k{k}_d010_a10', s, k, F(1, 100), 1.0, a.min_cell, 16, (0, 1, 2, 3)))
    # (ii) the core-size scaling at k = 4 (the kill) and k = 2
    for (d, an, ad) in ((F(3, 100), 'd030', 3.0), (F(6, 100), 'd060', 5.0),
                        (F(10, 100), 'd100', 7.5), (F(15, 100), 'd150', 11.25)):
        jobs.append((f'{a.tag}_k4_{an}', s, 4, d, ad, a.min_cell, 16, (0, 1, 2, 3)))
        jobs.append((f'{a.tag}_k2_{an}', s, 2, d, ad, a.min_cell, 16, (0, 1, 2, 3)))
    log = os.path.join(HERE, 'logs', f'sweep_{a.tag}.log')
    with open(log, 'a') as f:
        f.write(f"### sweep {a.tag} s={s} budget={float(budget_rat(s)):.4f} "
                f"{len(jobs)} jobs min_cell=1/{a.min_cell}\n")
    res = []
    with mp.Pool(a.workers) as pool:
        for r in pool.imap_unordered(one, jobs):
            res.append(r)
            line = json.dumps(r)
            print(line, flush=True)
            with open(log, 'a') as f:
                f.write(line + "\n")
            json.dump(res, open(os.path.join(HERE, 'results', f'sweep_{a.tag}.json'), 'w'), indent=1)
    with open(log, 'a') as f:
        f.write("SWEEP DONE\n")
    print("SWEEP DONE")


if __name__ == '__main__':
    main()
