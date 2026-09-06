"""A108 T2 - refine the crest of the relaxed (common-tilt) path between S07 and Trump.

trump_compare.py's 41-point sweep puts the crest between 41.1 and 41.7 deg, where the pinned
minimisation switches branch.  This re-runs the same constrained minimisation on a 0.05 deg grid
over [39.8, 43.0] with more restarts (including the previous grid point's own solution as a warm
start, walked in both directions, which is what keeps the branch from being lost), and records the
crest.  Updates results/trump_compare.json in place with the key `relaxed_tilt_path_fine`.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize

import a108lib as A
from a108lib import MZ
import exact as EX

NV = 34
CONS = MZ.make_cons((), 11)


def solve_at_tilt(th, z0, ntry=6, seed=0):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    for i in range(5):
        lo[3 + 3 * i] = hi[3 + 3 * i] = th
    best = None
    for trial in range(ntry):
        z = np.array(z0, float).copy()
        if trial:
            rng = np.random.RandomState(seed * 977 + trial)
            for i in range(11):
                z[1 + 3 * i] += rng.uniform(-0.02, 0.02)
                z[2 + 3 * i] += rng.uniform(-0.02, 0.02)
        for i in range(5):
            z[3 + 3 * i] = th
        z[0] = max(z[0], 3.86)
        z = np.clip(z, lo, hi)
        r = minimize(lambda v: v[0], z, jac=lambda v: np.eye(1, NV, 0)[0], method='SLSQP',
                     constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                     options={'maxiter': 600, 'ftol': 1e-14})
        if CONS(r.x).min() >= -1e-7:
            ss, cc = A.from107(r.x)
            sg = float(A.sigma(*A.normalise(ss, cc)))
            if best is None or sg < best[0]:
                best = (sg, r.x.copy())
    return best


def main():
    t0 = time.time()
    path = os.path.join(A.RES, 'trump_compare.json')
    doc = json.load(open(path, encoding='utf-8'))
    s07, cfg07 = EX.exact_float()
    st, cfgt, _ = A.load_trump()
    perm = doc['d4_alignment']['perm']
    zA = A.to107(s07, cfg07)
    q = math.pi / 2
    tB = [(cfgt[perm[i]][0], cfgt[perm[i]][1],
           cfgt[perm[i]][2] + q * round((cfg07[i][2] - cfgt[perm[i]][2]) / q)) for i in range(11)]
    zB = A.to107(st, tB)

    grid = [round(x, 4) for x in np.arange(43.0, 39.79, -0.05)]
    res = {}
    warm = zA.copy()
    for k, deg in enumerate(grid):                       # downhill sweep, warm-started
        th = math.radians(deg)
        a = (math.radians(45.0) - th) / (math.radians(45.0) - math.radians(40.181937290329714))
        seed = (1 - min(max(a, 0.0), 1.0)) * zA + min(max(a, 0.0), 1.0) * zB
        b = None
        for z0 in (warm, seed):
            r = solve_at_tilt(th, z0, seed=k)
            if r is not None and (b is None or r[0] < b[0]):
                b = r
        if b is not None:
            warm = b[1]
            res[deg] = b[0]
        print(f'   {deg:6.2f} deg -> {"n/a" if b is None else format(b[0], ".9f")}', flush=True)
    warm = zB.copy()
    for k, deg in enumerate(reversed(grid)):             # uphill sweep from Trump's side
        th = math.radians(deg)
        r = solve_at_tilt(th, warm, seed=5000 + k)
        if r is not None:
            warm = r[1]
            if deg not in res or r[0] < res[deg]:
                res[deg] = r[0]

    rows = [dict(tilt_deg=d, s=res[d]) for d in sorted(res)]
    crest = max(rows, key=lambda r: r['s'])
    doc['relaxed_tilt_path_fine'] = rows
    doc['relaxed_tilt_path_fine_crest'] = crest
    doc['relaxed_tilt_path_fine_barrier_over_S07'] = crest['s'] - s07
    doc['relaxed_tilt_path_fine_barrier_over_trump'] = crest['s'] - A.SHAT
    json.dump(doc, open(path, 'w', encoding='utf-8'), indent=1)
    print(f"\ncrest of the relaxed path: s = {crest['s']:.9f} at tilt {crest['tilt_deg']} deg")
    print(f"   barrier over S07  +{crest['s']-s07:.6f}")
    print(f"   barrier over Trump +{crest['s']-A.SHAT:.6f}")
    print('updated results/trump_compare.json in', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
