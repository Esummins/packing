"""A122 T3b - the S38 common-tilt path AGAIN, this time inside a continuation TUBE.

`crest.py`'s first relaxed sweep pinned the five tilts and released everything else with no trust
region.  It reports 3.902308 at S38's OWN tilt, i.e. 0.0266 BELOW S38's minimum: the tilt pin alone
does not hold S38's structure and SLSQP walked out of the basin at the very first grid point.  That
is A108's trap in its path form, and the number it produces is the tilt-pinned FLOOR of the whole
corridor, not the barrier between S38 and Trump.

Here the sweep is a continuation: at each tilt step every pose coordinate is confined to
||z - z_prev||inf <= rho of the SOLUTION AT THE PREVIOUS TILT, so the branch is tracked.  Two
sweeps (down from S38 and up from S38) at two tube radii; the barrier is the crest of the tracked
branch before it dies.

Updates results/crest.json in place with `tube_path`.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize

import a122lib as A
from a122lib import MZ

NV = 34
CONS = MZ.make_cons((), 11)


def solve_at_tilt_tube(th, z_prev, rho, ntry=2, seed=0):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    lo[1:] = np.maximum(lo[1:], z_prev[1:] - rho)
    hi[1:] = np.minimum(hi[1:], z_prev[1:] + rho)
    for i in range(5):
        lo[3 + 3 * i] = hi[3 + 3 * i] = th
    best = None
    for trial in range(ntry):
        z = np.array(z_prev, float).copy()
        if trial:
            rng = np.random.RandomState(seed * 977 + trial)
            z[1:] += rng.uniform(-rho / 3, rho / 3, 33)
        for i in range(5):
            z[3 + 3 * i] = th
        z = np.clip(z, lo, hi)
        r = minimize(lambda v: v[0], z, jac=lambda v: np.eye(1, NV, 0)[0], method='SLSQP',
                     constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                     options={'maxiter': 400, 'ftol': 1e-14})
        if CONS(r.x).min() >= -1e-7:
            ss, cc = A.from107(r.x)
            sg = float(A.sigma(*A.normalise(ss, cc)))
            if best is None or sg < best[0]:
                best = (sg, r.x.copy())
    return best


def F_T(th):
    c, s = math.cos(th), math.sin(th)
    return 2 + (2 + s) / (c + s)


def Lam(th):
    c, s = math.cos(th), math.sin(th)
    return 2 + 2 * (c + s) / (1 + s * c)


def run(z0, th0_deg, target_deg, step, rho, tag):
    n = int(abs(target_deg - th0_deg) / step)
    sgn = 1.0 if target_deg > th0_deg else -1.0
    z = np.array(z0, float)
    rows = []
    for k in range(n + 1):
        deg = th0_deg + sgn * step * k
        b = solve_at_tilt_tube(math.radians(deg), z, rho, seed=k)
        if b is None:
            rows.append(dict(tilt_deg=round(deg, 4), s=None, note='infeasible in the tube'))
            break
        z = b[1]
        rows.append(dict(tilt_deg=round(deg, 4), s=b[0], F_T=F_T(math.radians(deg)),
                         Lambda=Lam(math.radians(deg))))
    ok = [r for r in rows if r['s'] is not None]
    print(f'  [{tag} rho={rho}] {len(ok)} tilts, s from {ok[0]["s"]:.9f} to {ok[-1]["s"]:.9f}, '
          f'max {max(r["s"] for r in ok):.9f}')
    return rows


def main():
    t0 = time.time()
    path = os.path.join(A.RES, 'crest.json')
    doc = json.load(open(path, encoding='utf-8'))
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    b38 = d['entries']['S38']['best']
    s38, cfg38 = b38['sigma'], [tuple(c) for c in b38['cfg']]
    z38 = A.to107(s38, cfg38)
    th0 = math.degrees(cfg38[0][2])
    print(f'S38 at {th0:.6f} deg, s* = {s38:.12f}')

    out = {}
    for rho in (0.01, 0.03):
        down = run(z38, th0, 38.5, 0.05, rho, f'down')
        up = run(z38, th0, 44.5, 0.05, rho, f'up')
        okd = [r for r in down if r['s'] is not None]
        oku = [r for r in up if r['s'] is not None]
        crest_d = max(okd, key=lambda r: r['s'])
        crest_u = max(oku, key=lambda r: r['s'])
        out[str(rho)] = dict(down=down, up=up, crest_down=crest_d, crest_up=crest_u,
                             died_down=(len(down) != len(okd)), died_up=(len(up) != len(oku)),
                             barrier_down_over_S38=crest_d['s'] - s38,
                             barrier_up_over_S38=crest_u['s'] - s38,
                             barrier_down_over_trump=crest_d['s'] - A.SHAT)
        print(f'   rho={rho}: crest DOWN (toward Trump) {crest_d["s"]:.9f} at '
              f'{crest_d["tilt_deg"]} deg (+{crest_d["s"]-s38:.6f} over S38, '
              f'+{crest_d["s"]-A.SHAT:.6f} over Trump); crest UP {crest_u["s"]:.9f} at '
              f'{crest_u["tilt_deg"]} deg')
        for r in okd[::10]:
            print(f'     {r["tilt_deg"]:6.2f}  s {r["s"]:.9f}   F_T {r["F_T"]:.6f}  '
                  f'Lam {r["Lambda"]:.6f}   s-F_T {r["s"]-r["F_T"]:+.6f}')

    doc['tube_path'] = out
    doc['tube_note'] = ('the no-trust-region sweep of `relaxed_path` leaves S38 s basin at the very '
                        'first grid point (3.902308 at S38 s own tilt, 0.0266 BELOW s*), so its '
                        'numbers are the tilt-pinned floor of the corridor, not a barrier')
    json.dump(doc, open(path, 'w', encoding='utf-8'), indent=1)
    print('\nupdated results/crest.json in', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
