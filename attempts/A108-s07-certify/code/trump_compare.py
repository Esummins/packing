"""A108 T2 - S07 against Trump, square by square, and the barrier between them.

The two configurations have the SAME eleven-square skeleton in the same D4 frame: six uprights
(the BL column of three, BL(1,0), BR(0,0), TR(0,0)) plus five equal-tilt squares in the middle.
They differ in exactly two places - the tilt (45 deg vs 40.18 deg) and Trump's BL(0,2) upright,
which is lifted 0.0326 off its slot.

Barrier.  The side of a NORMALISED configuration (u = c/s, theta) is the exact function
`a108lib.sigma`: the smallest s at which unit squares at centres s*u with those angles are
pairwise interior-disjoint and inside [0, s]^2.  Every constraint is monotone in s, so sigma is a
closed-form max/min of thresholds - no optimisation, no local minima to worry about.  It reproduces
s-hat on Trump to 1.6e-15 and s* on the exact S07 configuration to 2e-15.  Along the straight
segment (1-t)*S07 + t*Trump in (u, theta) space, max sigma > max(sigma(S07), sigma(Trump)) means a
barrier: the two are different local minima, not two points of one basin.

A second, much more generous path is also measured: at each t the five tilted squares are held at
the interpolated common tilt and EVERYTHING else (all eleven centres, the six upright tilts, s) is
re-minimised.  That is the lowest barrier any tilt-monotone path can have, so it is the honest
number to quote.

Outputs results/trump_compare.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize

import a108lib as A
from a108lib import L, MZ
import exact as EX

NV = 34
CONS = MZ.make_cons((), 11)


def tilt_align(t_from, t_to):
    """Representative of t_to modulo 90 deg nearest to t_from (squares have 4-fold symmetry)."""
    q = math.pi / 2
    return t_to + q * round((t_from - t_to) / q)


def pair_up(s07, cfg07, st, cfgt):
    """Nearest-centre bijection S07 -> Trump, checked against all eight D4 images of Trump."""
    best = None
    for nm, f in L.d4_ops(st):
        img = [f(x, y, t) for (x, y, t) in cfgt]
        used, perm, cost = [False] * 11, [None] * 11, 0.0
        ok = True
        for i, p in enumerate(cfg07):
            cand = sorted((math.hypot(p[0] - img[j][0], p[1] - img[j][1]), j)
                          for j in range(11) if not used[j])
            if not cand:
                ok = False
                break
            d, j = cand[0]
            used[j] = True
            perm[i] = j
            cost += d
        if ok and (best is None or cost < best[0]):
            best = (cost, nm, perm, img)
    return best


def sigma_path(uA, tA, uB, tB, n=2001):
    ts = np.linspace(0.0, 1.0, n)
    out = []
    for t in ts:
        u = (1 - t) * uA + t * uB
        th = (1 - t) * tA + t * tB
        out.append(A.sigma(u, th))
    return ts, np.array(out)


def relaxed_barrier(s07, cfg07, st, cfgt, perm, imgt, n=41):
    """At each tilt on the way from 45 deg to 40.18 deg, hold the five tilted squares at that
    common tilt and minimise s over everything else (all centres, the upright tilts, s)."""
    tiltA = cfg07[0][2]
    tiltB = tilt_align(tiltA, imgt[perm[0]][2])
    rows = []
    zA = A.to107(s07, cfg07)
    zB = A.to107(st, [imgt[perm[i]] for i in range(11)])
    for k in range(n):
        a = k / (n - 1)
        th = (1 - a) * tiltA + a * tiltB
        z0 = (1 - a) * zA + a * zB
        z0[0] = max(s07, st) + 0.02
        lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
        hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
        for i in range(5):                       # the five tilted squares: tilt pinned
            lo[3 + 3 * i] = hi[3 + 3 * i] = th
            z0[3 + 3 * i] = th
        best = None
        for trial in range(4):
            z = z0.copy()
            if trial:
                rng = np.random.RandomState(100 * k + trial)
                for i in range(11):
                    z[1 + 3 * i] += rng.uniform(-0.03, 0.03)
                    z[2 + 3 * i] += rng.uniform(-0.03, 0.03)
            z = np.clip(z, lo, hi)
            r = minimize(lambda v: v[0], z, jac=lambda v: np.eye(1, NV, 0)[0], method='SLSQP',
                         constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                         options={'maxiter': 500, 'ftol': 1e-14})
            if CONS(r.x).min() >= -1e-7:
                ss, cc = A.from107(r.x)
                sg = float(A.sigma(*A.normalise(ss, cc)))
                if best is None or sg < best:
                    best = sg
        rows.append(dict(tilt_deg=math.degrees(th), s=best))
    return rows


def main():
    t0 = time.time()
    out = {}
    s07, cfg07 = EX.exact_float()
    st, cfgt, order = A.load_trump()

    cost, opname, perm, imgt = pair_up(s07, cfg07, st, cfgt)
    out['d4_alignment'] = dict(op=opname, total_centre_distance=cost, perm=perm)
    print(f'best D4 alignment of Trump onto S07: "{opname}", total centre distance {cost:.6f}')

    # ---------------- square by square
    tab = []
    for i, nm in enumerate(A.NAMES):
        p = cfg07[i]
        q = imgt[perm[i]]
        qt = tilt_align(p[2], q[2])
        tab.append(dict(name=nm,
                        s07=[p[0], p[1], math.degrees(p[2])],
                        trump=[q[0], q[1], math.degrees(qt)],
                        d_centre=math.hypot(p[0] - q[0], p[1] - q[1]),
                        d_tilt_deg=math.degrees(p[2] - qt)))
    out['square_by_square'] = tab
    print(f"{'square':9s} {'S07 (x, y, deg)':34s} {'Trump (x, y, deg)':34s} {'dC':>9s} {'dTilt':>8s}")
    for r in tab:
        print(f"{r['name']:9s} ({r['s07'][0]:8.5f},{r['s07'][1]:8.5f},{r['s07'][2]:7.3f})       "
              f"({r['trump'][0]:8.5f},{r['trump'][1]:8.5f},{r['trump'][2]:7.3f})       "
              f"{r['d_centre']:9.5f} {r['d_tilt_deg']:8.3f}")
    dpose = max(max(abs(r['s07'][0] - r['trump'][0]), abs(r['s07'][1] - r['trump'][1]),
                    abs(math.radians(r['d_tilt_deg']))) for r in tab)
    out['pose_distance_linf'] = dpose
    print(f'L-inf pose distance S07 -> Trump: {dpose:.6f}  '
          f'(the tilt gap {max(abs(r["d_tilt_deg"]) for r in tab):.4f} deg dominates)')

    # ---------------- the straight segment in normalised pose space
    uA, tA = A.normalise(s07, cfg07)
    tB_cfg = [(imgt[perm[i]][0], imgt[perm[i]][1], tilt_align(cfg07[i][2], imgt[perm[i]][2]))
              for i in range(11)]
    uB, tB = A.normalise(st, tB_cfg)
    ts, sig = sigma_path(uA, tA, uB, tB, n=4001)
    k = int(np.argmax(sig))
    out['segment_normalised'] = dict(
        sigma_A=float(sig[0]), sigma_B=float(sig[-1]),
        sigma_max=float(sig[k]), t_max=float(ts[k]),
        barrier_over_S07=float(sig[k] - sig[0]), barrier_over_trump=float(sig[k] - sig[-1]),
        samples=[[float(ts[i]), float(sig[i])] for i in range(0, len(ts), 100)])
    print(f'\nstraight segment (normalised): sigma(0) = {sig[0]:.9f}  sigma(1) = {sig[-1]:.9f}  '
          f'MAX {sig[k]:.9f} at t = {ts[k]:.4f}')
    print(f'   barrier above S07 {sig[k]-sig[0]:+.6f}, above Trump {sig[k]-sig[-1]:+.6f}')

    # ---------------- the same segment in absolute pose space (centres, not centre/s)
    cA = np.array([[c[0], c[1]] for c in cfg07])
    cB = np.array([[c[0], c[1]] for c in tB_cfg])
    sig2 = []
    for t in np.linspace(0, 1, 4001):
        c = (1 - t) * cA + t * cB
        th = (1 - t) * tA + t * tB
        sl = (1 - t) * s07 + t * st
        sig2.append(A.sigma(c / sl, th))
    sig2 = np.array(sig2)
    k2 = int(np.argmax(sig2))
    out['segment_absolute'] = dict(sigma_max=float(sig2[k2]), t_max=float(k2 / 4000.0),
                                   barrier_over_S07=float(sig2[k2] - sig2[0]))
    print(f'straight segment (absolute centres): MAX {sig2[k2]:.9f} at t = {k2/4000.0:.4f}')

    # ---------------- the generous path: common tilt pinned, everything else re-minimised
    rows = relaxed_barrier(s07, cfg07, st, cfgt, perm, imgt, n=41)
    vals = [r['s'] for r in rows if r['s'] is not None]
    out['relaxed_tilt_path'] = rows
    out['relaxed_tilt_path_max'] = max(vals) if vals else None
    print('\nrelaxed path (common tilt pinned, everything else free):')
    for r in rows[::4]:
        print(f"   tilt {r['tilt_deg']:7.3f} deg -> s = "
              f"{'infeasible' if r['s'] is None else format(r['s'], '.9f')}")
    print(f'   MAX over the path {max(vals):.9f}  (+{max(vals)-s07:.6f} over S07, '
          f'+{max(vals)-A.SHAT:.6f} over Trump)')

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'trump_compare.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote results/trump_compare.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
