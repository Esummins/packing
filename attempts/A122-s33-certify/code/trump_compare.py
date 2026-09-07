"""A122 T3 - S33min against Trump and against A108's S07, square by square, and the barrier.

Correspondence: nearest-centre bijection minimised over all eight D4 images of the target, so the
comparison is frame-independent; tilts are compared modulo 90 deg.

Two paths are measured, as in A108:
  * the STRAIGHT SEGMENT in normalised pose space, with sigma evaluated on 401 points - no
    optimiser, so the number cannot be an artefact of a solver;
  * the RELAXED tilt path: at each t the five free tilts are pinned to the linear interpolation
    between S33min's tilt vector and the target's, and all eleven centres, the six upright tilts
    and s are re-minimised, warm-started along the sweep in BOTH directions.  Run twice, once
    unconstrained and once inside an L-infinity TRUST REGION of radius rho around the interpolated
    seed, because without one SLSQP leaves the corridor and the number stops describing the path
    between the two points (A108 sec 6's trap, in its path form).

Outputs results/trump_compare.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize

import a122lib as A
from a122lib import MZ, L

NV = 34
CONS = MZ.make_cons((), 11)


def best_d4(cfgA, sA, cfgB, sB):
    """Nearest-centre bijection minimised over the eight D4 images of B."""
    best = None
    for name, op in L.d4_ops(sB).items() if isinstance(L.d4_ops(sB), dict) else \
            enumerate(L.d4_ops(sB)):
        img = []
        for (x, y, t) in cfgB:
            r = op((x, y, t)) if callable(op) else None
            img.append(r)
        if any(v is None for v in img):
            return None
        perm, tot, dt = A.match_configs(cfgA, img)
        if best is None or tot < best[1]:
            best = (name, tot, perm, img, dt)
    return best


def solve_pinned_tilts(tilts, z0, trust=None, centre=None, ntry=3, seed=0):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    if trust is not None:
        c = np.asarray(centre, float)
        lo[1:] = np.maximum(lo[1:], c[1:] - trust)
        hi[1:] = np.minimum(hi[1:], c[1:] + trust)
    for i in range(5):
        lo[3 + 3 * i] = hi[3 + 3 * i] = tilts[i]
    best = None
    for trial in range(ntry):
        z = np.array(z0, float).copy()
        if trial:
            rng = np.random.RandomState(seed * 977 + trial)
            for i in range(11):
                z[1 + 3 * i] += rng.uniform(-0.02, 0.02)
                z[2 + 3 * i] += rng.uniform(-0.02, 0.02)
        for i in range(5):
            z[3 + 3 * i] = tilts[i]
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


def compare(tag, sA, cfgA, namesA, sB, cfgB, labelB, out, rho=0.15, npts=31):
    q = math.pi / 2
    perm, tot, dt = A.match_configs(cfgA, cfgB)
    matched = [cfgB[perm[i]] for i in range(11)]
    matched = [(c[0], c[1], c[2] + q * round((cfgA[i][2] - c[2]) / q))
               for i, c in enumerate(matched)]
    rows = []
    for i in range(11):
        rows.append(dict(name=namesA[i],
                         a=[cfgA[i][0], cfgA[i][1], A.tmod(cfgA[i][2])],
                         b=[matched[i][0], matched[i][1], A.tmod(matched[i][2])],
                         d_centre=math.hypot(cfgA[i][0] - matched[i][0],
                                             cfgA[i][1] - matched[i][1]),
                         d_tilt_deg=min(abs(A.tmod(cfgA[i][2]) - A.tmod(matched[i][2])),
                                        90 - abs(A.tmod(cfgA[i][2]) - A.tmod(matched[i][2])))))
    print(f'\n=== S33min vs {labelB}: total centre distance {tot:.4f}')
    for r in rows:
        print(f"   {r['name']:9s} ({r['a'][0]:.4f},{r['a'][1]:.4f},{r['a'][2]:7.3f}) vs "
              f"({r['b'][0]:.4f},{r['b'][1]:.4f},{r['b'][2]:7.3f})   "
              f"d_c {r['d_centre']:.4f}  d_tilt {r['d_tilt_deg']:6.3f}")

    zA, zB = A.to107(sA, cfgA), A.to107(sB, matched)
    seg = []
    for t in np.linspace(0, 1, 401):
        z = (1 - t) * zA + t * zB
        ss, cc = A.from107(z)
        u = np.array([[c[0], c[1]] for c in cc]) / ((1 - t) * sA + t * sB)
        seg.append([float(t), float(A.sigma(u, np.array([c[2] for c in cc])))])
    smax = max(seg, key=lambda r: r[1])
    print(f'  straight segment: crest {smax[1]:.9f} at t = {smax[0]:.3f}   '
          f'(+{smax[1]-sA:.6f} over S33min, +{smax[1]-sB:.6f} over {labelB})')

    ts = np.linspace(0, 1, npts)
    paths = {}
    for mode, trust in (('free', None), (f'trust_{rho}', rho)):
        res = {}
        warm = zA.copy()
        for k, t in enumerate(ts):                       # forward
            seed = (1 - t) * zA + t * zB
            tl = [(1 - t) * zA[3 + 3 * i] + t * zB[3 + 3 * i] for i in range(5)]
            b = None
            for z0 in (warm, seed):
                r = solve_pinned_tilts(tl, z0, trust=trust, centre=seed, seed=k)
                if r is not None and (b is None or r[0] < b[0]):
                    b = r
            if b is not None:
                warm = b[1]
                res[float(t)] = b[0]
        warm = zB.copy()
        for k, t in enumerate(reversed(ts)):             # backward
            seed = (1 - t) * zA + t * zB
            tl = [(1 - t) * zA[3 + 3 * i] + t * zB[3 + 3 * i] for i in range(5)]
            r = solve_pinned_tilts(tl, warm, trust=trust, centre=seed, seed=5000 + k)
            if r is not None:
                warm = r[1]
                if float(t) not in res or r[0] < res[float(t)]:
                    res[float(t)] = r[0]
        rr = [dict(t=t, s=res[t]) for t in sorted(res)]
        cr = max(rr, key=lambda r: r['s'])
        paths[mode] = dict(points=rr, crest=cr,
                           barrier_over_S33=cr['s'] - sA, barrier_over_target=cr['s'] - sB)
        print(f'  relaxed tilt path [{mode}]: crest {cr["s"]:.9f} at t = {cr["t"]:.3f}   '
              f'(+{cr["s"]-sA:.6f} over S33min, +{cr["s"]-sB:.6f} over {labelB})')

    out[tag] = dict(target=labelB, s_target=sB, total_centre_distance=tot, perm=perm,
                    square_by_square=rows, segment=seg, segment_crest=smax,
                    segment_barrier_over_S33=smax[1] - sA,
                    segment_barrier_over_target=smax[1] - sB,
                    relaxed=paths)


def main():
    t0 = time.time()
    out = {}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    b = d['entries']['S33']['best']
    sA, cfgA = b['sigma'], [tuple(c) for c in b['cfg']]
    namesA = A.names_for('S33')

    st, cfgt = A.load_trump()
    s07, cfg07 = A.load_s07_exact()
    print(f'S33min s* = {sA:.12f}; Trump {st:.12f}; S07 {s07:.12f}')

    compare('vs_trump', sA, cfgA, namesA, st, cfgt, 'Trump', out)
    compare('vs_s07', sA, cfgA, namesA, s07, cfg07, 'S07', out)

    # is the SKELETON the same?  the six upright squares and their cells
    def cells(s, cfg):
        return sorted((round(c[0] - 0.5, 3), round(c[1] - 0.5, 3))
                      for c in cfg if min(A.tmod(c[2]), 90 - A.tmod(c[2])) < 1e-6)
    out['skeleton'] = dict(
        S33min_upright_cells=cells(sA, cfgA), trump_upright_cells=cells(st, cfgt),
        s07_upright_cells=cells(s07, cfg07),
        S33min_n_upright=len(cells(sA, cfgA)), trump_n_upright=len(cells(st, cfgt)),
        s07_n_upright=len(cells(s07, cfg07)))
    print('\nupright cells (x0, y0 of the lower-left corner):')
    for k in ('S33min_upright_cells', 'trump_upright_cells', 's07_upright_cells'):
        print(f'   {k}: {out["skeleton"][k]}')

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'trump_compare.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/trump_compare.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
