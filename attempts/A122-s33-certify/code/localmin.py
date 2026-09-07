"""A122 T1 - are the A122 landings genuine LOCAL MINIMA of the side, and are S33min and S35min
two points or one?

A108's trap, recorded verbatim: the naive "perturb, then re-minimise with no trust region" reports
a spurious descent because SLSQP repairs the infeasibility by walking out of the basin.  Every
number here therefore comes from a minimisation inside an L-infinity TRUST REGION around the point
under test, plus pinned-coordinate profiles inside a trust region.

Three questions:
  (a) trust region: min s over the 34 variables with ||pose - pose*||inf <= rho, from the point and
      from random starts inside the region.  A local minimum returns s* for every small rho.
  (b) pinned profiles: pin one coordinate at v +/- delta, re-minimise the rest inside a trust
      region.  A local minimum shows rise >= 0 growing like delta^2.
  (c) the S33min <-> S35min question: a trust region big enough to contain BOTH points, started at
      each, plus the straight segment between them evaluated with sigma (no optimiser).

Outputs results/localmin.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize, linprog, nnls

import a122lib as A
from a122lib import AN, MZ

CONS = MZ.make_cons((), 11)
NV = 34


def solve_pinned(z0, pins=(), maxiter=400, trust=None, centre=None):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    z0 = np.asarray(z0, float).copy()
    if trust is not None:
        c = np.asarray(centre if centre is not None else z0, float)
        lo[1:] = np.maximum(lo[1:], c[1:] - trust)
        hi[1:] = np.minimum(hi[1:], c[1:] + trust)
    z0 = np.clip(z0, lo, hi)
    for i, v in pins:
        lo[i] = hi[i] = v
        z0[i] = v
    r = minimize(lambda z: z[0], z0, jac=lambda z: np.eye(1, NV, 0)[0], method='SLSQP',
                 constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                 options={'maxiter': maxiter, 'ftol': 1e-14})
    feas = float(CONS(r.x).min())
    if feas < -1e-7:
        return None, feas, r.x
    ss, cc = A.from107(r.x)
    return float(A.sigma(*A.normalise(ss, cc))), feas, r.x


def active_jacobian(s, cfg, names, tol=1e-7):
    z = A.to107(s, cfg)
    sq = AN.build_squares((), 11)
    J, lab = [], []
    for i in range(11):
        for j in range(i + 1, 11):
            if AN.pair_gap(sq[i], sq[j], z) < tol:
                rows, kinds, kind = AN.contact_rows(sq[i], sq[j], z, NV)
                for r in rows:
                    J.append(r)
                    lab.append((names[i], names[j], kind))
    for i in range(11):
        rows, nms = AN.wall_rows(sq[i], z, s, NV)
        for r, nm in zip(rows, nms):
            J.append(r)
            lab.append((names[i], nm[1], 'wall'))
    return np.array(J), lab


def study(tag, s, cfg, names, out, rhos=(1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1)):
    z_star = A.to107(s, cfg)
    e = {'s_star': s}
    J, lab = active_jacobian(s, cfg, names)
    Jn = J / np.linalg.norm(J, axis=1)[:, None]
    ev = np.zeros(NV); ev[0] = 1.0
    lam, res = nnls(Jn.T, ev)
    resid = Jn.T @ lam - ev
    nm = ['s'] + [f'{names[i]}.{c}' for i in range(11) for c in ('x', 'y', 'th')]
    worst = sorted(range(NV), key=lambda k: -abs(resid[k]))[:6]
    e['fritz_john'] = dict(rows=int(J.shape[0]), residual=float(res),
                           worst=[[nm[k], float(resid[k])] for k in worst],
                           forces=sorted([[lab[i][0], lab[i][1], lab[i][2], float(lam[i])]
                                          for i in range(len(lam)) if lam[i] > 1e-9],
                                         key=lambda t: -t[3]))
    print(f'  [{tag}] Fritz-John residual {res:.3e}  (S07 for contrast: 0.152)')

    tr = []
    for rho in rhos:
        best = None
        rng0 = np.random.RandomState(97)
        starts = [z_star.copy()]
        for k in range(12):
            z = z_star.copy()
            z[1:] += rng0.uniform(-rho, rho, 33)
            z[0] = s + 0.5 * rho
            starts.append(z)
        for z0 in starts:
            sv, feas, _ = solve_pinned(z0, trust=rho, centre=z_star)
            if sv is not None and (best is None or sv < best):
                best = sv
        tr.append(dict(rho=rho, s_min=best, drop=(None if best is None else best - s)))
        print(f'    trust region rho={rho:.0e}: min s = '
              f"{'n/a' if best is None else format(best, '.10f')}  "
              f"({'n/a' if best is None else format(best - s, '+.2e')})")
    e['trust_region'] = tr

    prof = {}
    tg = [(f'{names[i]}.th', 3 + 3 * i) for i in range(5)]
    tg += [(f'{names[4]}.y', 2 + 3 * 4), (f'{names[0]}.y', 2)]
    for name, idx in tg:
        base = z_star[idx]
        row = []
        for dv in (-3e-2, -1e-2, -3e-3, -1e-3, 1e-3, 3e-3, 1e-2, 3e-2):
            sv, feas, _ = solve_pinned(z_star, pins=[(idx, base + dv)],
                                       trust=max(10 * abs(dv), 3e-2), centre=z_star)
            row.append(dict(delta=dv, s=sv, rise=(None if sv is None else sv - s)))
        prof[name] = row
        print(f'    profile {name:12s}: ' + '  '.join(
            f"{r['delta']:+.0e}:{'infeas' if r['s'] is None else format(r['rise'], '+.1e')}"
            for r in row))
    e['profiles'] = prof
    out[tag] = e
    return e


def main():
    t0 = time.time()
    out = {}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    pts = {}
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        pts[tag] = (b['sigma'], [tuple(c) for c in b['cfg']], A.names_for(sid))
        print(f'\n=== {tag}  s* = {b["sigma"]:.12f}')
        study(tag, *pts[tag], out)

    # ------------------------------------------------ S33min vs S35min: one basin or two?
    print('\n=== S33min <-> S35min: separate basins?')
    sA, cA, _ = pts['S33min']
    sB, cB, _ = pts['S35min']
    zA, zB = A.to107(sA, cA), A.to107(sB, cB)
    # match S35's labelling to S33's so the segment joins corresponding squares
    perm, tot, dt = A.match_configs(cA, cB)
    cBp = [cB[perm[i]] for i in range(11)]
    q = math.pi / 2
    cBp = [(c[0], c[1], c[2] + q * round((cA[i][2] - c[2]) / q)) for i, c in enumerate(cBp)]
    zBp = A.to107(sB, cBp)
    linf = float(np.abs(zBp[1:] - zA[1:]).max())
    print(f'  matched pose distance |.|inf = {linf:.4f}  (centre total {tot:.4f})')

    seg = []
    for t in np.linspace(0, 1, 201):
        z = (1 - t) * zA + t * zBp
        ss, cc = A.from107(z)
        u = np.array([[c[0], c[1]] for c in cc]) / ((1 - t) * sA + t * sB)
        seg.append([float(t), float(A.sigma(u, np.array([c[2] for c in cc])))])
    smax = max(seg, key=lambda r: r[1])
    print(f'  straight segment (sigma, no optimiser): crest {smax[1]:.9f} at t = {smax[0]:.3f}'
          f'   barrier over S33min +{smax[1]-sA:.6f}, over S35min +{smax[1]-sB:.6f}')

    both = []
    for rho in (0.02, 0.05, 0.08, 0.12, 0.2, 0.3):
        r1, _, _ = solve_pinned(zA, trust=rho, centre=zA)
        r2, _, _ = solve_pinned(zBp, trust=rho, centre=zBp)
        both.append(dict(rho=rho, from_S33=r1, from_S35=r2))
        print(f'    rho={rho:.2f}: from S33min -> {r1}   from S35min -> {r2}')
    out['S33_vs_S35'] = dict(matched_pose_linf=linf, centre_total=tot, max_tilt_deg=max(dt),
                             segment=seg, segment_crest=smax,
                             barrier_over_S33=smax[1] - sA, barrier_over_S35=smax[1] - sB,
                             trust_growth=both, perm=perm)

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'localmin.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/localmin.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
