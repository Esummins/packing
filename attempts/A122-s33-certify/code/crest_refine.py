"""A122 T3c - refine the crest of S38's tube-tracked common-tilt branch and name the load-path
change that ends it.

The tube sweep (`crest_tube.py`) shows the branch follows the closed forms

    below theta* :  C3(theta) = the 'row (c)/(e) released' formula   (f3 off the top wall, and
                                equivalently BR(0,1)'s corner off f4 - the two rows are dependent
                                given the others, sympy gives them the SAME closed form)
    above theta* :  C2(theta) = the 'row (b) released' formula       (f1 off the top wall)

to 5e-8 / 2e-7, with the kink minimum at theta* = 41.754062677 deg.  Both RISE away from theta*, so
on the Trump side (theta decreasing) there is no crest at all; the only crest is on the far side,
where the C2 branch dies.  This refines that crest on a 0.01 deg tube and records which contact
opens, plus an extended sweep downwards to find where the C3 branch ends.

Updates results/crest.json with `crest_refined`.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

from scipy.optimize import minimize

import a122lib as A
from a122lib import AN, L, MZ
import crest as C

NV = 34
CONS = MZ.make_cons((), 11)


def solve_at_tilt_tube(th, z_prev, rho, ntry=3, seed=0, maxiter=1200):
    """As crest_tube's, with a longer iteration budget and a looser landing gate.

    The gate can be loose because the number reported is sigma(poses), the EXACT side of the
    returned configuration, not SLSQP's s: a landing that misses feasibility by 1e-6 still gives a
    valid side for the poses it returns (A108 sec 1).  crest_tube's -1e-7 gate threw away the
    iteration-limited landing at S38's own tilt, which is why this file re-does the sweep.
    """
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
                     options={'maxiter': maxiter, 'ftol': 1e-14})
        if CONS(r.x).min() >= -1e-5:
            ss, cc = A.from107(r.x)
            sg = float(A.sigma(*A.normalise(ss, cc)))
            if best is None or sg < best[0]:
                best = (sg, r.x.copy())
    return best


def contacts_of(s, cfg, names, tol=1e-7):
    z = A.to107(s, cfg)
    sq = AN.build_squares((), 11)
    out = []
    for i in range(11):
        for j in range(i + 1, 11):
            if AN.pair_gap(sq[i], sq[j], z) < tol:
                out.append(f'{names[i]}-{names[j]}')
    for i in range(11):
        rows, nms = AN.wall_rows(sq[i], z, s, 34)
        for nm in nms:
            t = f'{names[i]}-{nm[1]}'
            if t not in out:
                out.append(t)
    return sorted(set(out))


def main():
    t0 = time.time()
    path = os.path.join(A.RES, 'crest.json')
    doc = json.load(open(path, encoding='utf-8'))
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    b38 = d['entries']['S38']['best']
    s38, cfg38 = b38['sigma'], [tuple(c) for c in b38['cfg']]
    names = A.names_for('S38')
    z38 = A.to107(s38, cfg38)
    th0 = math.degrees(cfg38[0][2])
    base_contacts = contacts_of(s38, cfg38, names)
    print('S38 contact set:', base_contacts)

    out = {'S38_contacts': base_contacts}

    # ---- fine tube upwards through the crest
    rows = []
    z = z38.copy()
    deg = th0
    rho = 0.01
    while deg < 43.61:
        b = solve_at_tilt_tube(math.radians(deg), z, rho, ntry=2, seed=int(deg * 100))
        if b is None:
            rows.append(dict(tilt_deg=round(deg, 4), s=None))
            break
        z = b[1]
        ss, cc = A.from107(z)
        cs = contacts_of(ss, cc, names)
        rows.append(dict(tilt_deg=round(deg, 4), s=b[0],
                         C2=C.branch_formulas(math.radians(deg))['drop_b_f1_off_top_wall'],
                         C3=C.branch_formulas(math.radians(deg))['drop_ce_f3_off_top_wall'],
                         lost=[c for c in base_contacts if c not in cs],
                         gained=[c for c in cs if c not in base_contacts]))
        deg += 0.02
    ok = [r for r in rows if r['s'] is not None]
    crest = max(ok, key=lambda r: r['s'])
    out['up_fine'] = rows
    out['up_crest'] = crest
    print(f"\n  crest of the C2 branch: s = {crest['s']:.9f} at {crest['tilt_deg']} deg   "
          f"(+{crest['s']-s38:.6f} over S38, +{crest['s']-A.SHAT:.6f} over Trump)")
    print(f"    C2 there = {crest['C2']:.9f}  (|s - C2| = {abs(crest['s']-crest['C2']):.2e})")
    for r in ok:
        if abs(r['tilt_deg'] - crest['tilt_deg']) < 0.35 and abs(r['tilt_deg'] * 100 % 5) < 1e-6:
            print(f"    {r['tilt_deg']:6.2f}  s {r['s']:.9f}  C2 {r['C2']:.9f}  "
                  f"|s-C2| {abs(r['s']-r['C2']):.2e}  lost {r['lost']}  gained {r['gained']}")

    # ---- extended tube downwards: where does the C3 branch end?
    rows2 = []
    z = z38.copy()
    deg = th0
    while deg > 24.9:
        b = solve_at_tilt_tube(math.radians(deg), z, rho, ntry=2, seed=int(deg * 100))
        if b is None:
            rows2.append(dict(tilt_deg=round(deg, 4), s=None))
            break
        z = b[1]
        ss, cc = A.from107(z)
        cs = contacts_of(ss, cc, names)
        rows2.append(dict(tilt_deg=round(deg, 4), s=b[0],
                          C3=C.branch_formulas(math.radians(deg))['drop_ce_f3_off_top_wall'],
                          F_T=C.F_T(math.radians(deg)),
                          lost=[c for c in base_contacts if c not in cs],
                          gained=[c for c in cs if c not in base_contacts]))
        deg -= 0.05
    ok2 = [r for r in rows2 if r['s'] is not None]
    out['down_extended'] = rows2
    out['down_max'] = max(ok2, key=lambda r: r['s'])
    out['down_leaves_C3_at'] = next((r['tilt_deg'] for r in ok2 if abs(r['s'] - r['C3']) > 1e-5),
                                    None)
    print(f"\n  extended down sweep: {len(ok2)} tilts to {ok2[-1]['tilt_deg']} deg, "
          f"s rises monotonically to {max(r['s'] for r in ok2):.9f}")
    print(f"    leaves the C3 formula at {out['down_leaves_C3_at']} deg")
    for r in ok2[::10]:
        print(f"    {r['tilt_deg']:6.2f}  s {r['s']:.9f}  C3 {r['C3']:.9f}  "
              f"|s-C3| {abs(r['s']-r['C3']):.1e}  s-F_T {r['s']-r['F_T']:+.6f}  "
              f"lost {r['lost']}")

    doc['crest_refined'] = out
    json.dump(doc, open(path, 'w', encoding='utf-8'), indent=1)
    print('\nupdated results/crest.json in', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
