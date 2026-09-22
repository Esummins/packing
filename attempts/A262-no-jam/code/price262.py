"""A262: Monte-Carlo TRUTH TEST + PRICE of the JAM-corner certificate (cert262.check_box) on the BASIC-JAM domain:
    d0 in (0,1), alpha in (0,45];  X touches x = 0, yX in [1, SMAX - 1], phiX in (0,45];  C any pose in [0, 1 + sqrt2]^2
    HARD conditions: A, X, C pairwise interior-disjoint; C meets the open box and floats; X meets C's drop to the wall
    (T_u) and A meets C's drop to the floor (T_v)  [the blockers of A261 s.1.2];  X inside [0, SMAX].
(a box that is PRUNE -- off the domain or cores overlapping -- counts as closed, as in the tree.)
Per accepted sample: does the POINT certify (if not: the room statement is FALSE or thin there -- the sample is kept as a
counterexample candidate with its margin), and the largest dyadic radius at which the box around it certifies.
Price = domain volume x mean(1 / leaf volume) x seconds per box  (crude, heavy-tailed: a bound on the order only).
    python price262.py [--n 150] [--seed 1]    -> results/price262.json
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cert262 as K2                                                  # noqa: E402
Z = K2.Z
W = np.array([1, 2, 1, 2, 1, 1, 2.0])
LO = np.array([0.0, 0.0, 1.0, 0.0, 0.5, 0.5, 0.0])
HI = np.array([1.0, math.pi / 4, K2.SMAX - 1.0, math.pi / 4, 1.0 + math.sqrt(2), 1.0 + math.sqrt(2), math.pi / 2])


def accept(p):
    A, A2, X, C = K2.squares(p, K2.SMAX)
    if X[:, 1].max() > K2.SMAX or C.min() <= 0 or -Z.poly_gap(C, K2.BOXP) <= 0:
        return False
    if min(Z.poly_gap(C, A), Z.poly_gap(C, X), Z.poly_gap(A, X), Z.poly_gap(C, A2)) < 0:
        return False
    Tu = C - np.array([C[:, 0].min(), 0.0])
    Tv = C - np.array([0.0, C[:, 1].min()])
    return Z.poly_gap(X, Tu) < 0 and Z.poly_gap(A, Tv) < 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=150)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--budget', type=float, default=100.0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    t0, tried, rows, nbox, tbox = time.time(), 0, [], 0, 0.0
    while len(rows) < a.n and time.time() - t0 < a.budget:
        p = LO + (HI - LO) * rng.uniform(size=7)
        tried += 1
        if not accept(p):
            continue
        t1 = time.time()
        st, m = K2.check_box(p, p)
        rad = None
        if st == 'CERT':
            for k in range(3, 12):
                h = 2.0 ** (-k)
                nbox += 1
                if K2.check_box(p - h / W, p + h / W)[0] in ('CERT', 'PRUNE'):
                    rad = h
                    break
        tbox += time.time() - t1
        rows.append(dict(p=[float(v) for v in p], point=st, margin=m, cert_radius=rad))
    acc = len(rows) / max(tried, 1)
    vol = float(np.prod(HI - LO)) * acc
    ok = [r for r in rows if r['cert_radius']]
    leafvol = [float(np.prod(2 * r['cert_radius'] / W)) for r in ok]
    sec_per_box = tbox / max(nbox + len(rows), 1)
    leaves = vol * float(np.mean([1.0 / v for v in leafvol])) if ok else None          # heavy-tailed
    leaves_med = vol / float(np.median(leafvol)) if ok else None
    summ = dict(tried=tried, accepted=len(rows), acceptance=acc, domain_volume=vol,
                point_fail=sum(r['point'] != 'CERT' for r in rows),
                worst_point_margin=max((r['margin'] for r in rows if r['margin'] is not None), default=None),
                radius_hist={str(h): sum(r['cert_radius'] == h for r in ok) for h in sorted({r['cert_radius'] for r in ok})},
                est_leaves=leaves, est_leaves_median=leaves_med, sec_per_box=sec_per_box,
                est_cpu_hours=None if leaves is None else leaves * sec_per_box / 3600.0)
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(ATT, 'results', 'price262.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
