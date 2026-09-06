"""A108 T1 - is s* = 2 + 4 sqrt2 / 3 really a local MINIMUM of the side, and in what sense is the
configuration rigid?

Three things are separated here, because at S07 they give three different answers:

  (a) FIRST-ORDER Fritz-John.  It FAILS: nnls(J^T, e_s) leaves a residual 0.152 concentrated on
      f1.theta and f2.theta.  The reason is geometric, not numerical: a unit square at EXACTLY
      45 deg touching a wall has zero first-order torque from that wall - its touching vertex sits
      at the top of its own rotation circle, so d(vertex_y)/d(theta) = 0 and the containment gap is
      quadratic in theta.  Equivalently the containment half-width (|cos t| + |sin t|)/2 is
      MAXIMAL at 45 deg.  Every first-order test is therefore blind in the tilt directions, which
      is exactly the second-order trap A107 flagged.

  (b) SECOND-ORDER profile.  Pin one coordinate at v +/- delta, re-minimise s over everything else
      (all eleven squares free).  A local minimum shows s(delta) >= s* with quadratic growth.  This
      is run on every tilt coordinate and along the Fritz-John residual direction.

  (c) RIGIDITY.  Two notions, both reported: the two-sided flex space (nullspace of the active
      incidence Jacobian at fixed s) and the one-sided flex cone {v : J v >= 0} (the packing is
      first-order rigid iff that cone is trivial), computed by LP.

Outputs results/localmin.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from scipy.optimize import minimize, linprog, nnls

import a108lib as A
from a108lib import AN, MZ
import exact as EX

CONS = MZ.make_cons((), 11)
NV = 34


def solve_pinned(z0, pins=(), maxiter=400, trust=None, centre=None):
    """Minimise s over the 34 variables.

    pins  = [(index, value)] held fixed.
    trust = radius rho of an L-infinity TRUST REGION on the 33 pose coordinates around `centre`
            (default: z0).  This is what makes the test a LOCAL one: without it SLSQP is free to
            walk out of the basin and land on a different structure, which is how a naive
            "perturb and re-minimise" reports a spurious descent.
    """
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
        return None, feas
    ss, cc = A.from107(r.x)
    return float(A.sigma(*A.normalise(ss, cc))), feas


def active_jacobian(s, cfg, tol=1e-7):
    z = A.to107(s, cfg)
    sq = AN.build_squares((), 11)
    J, lab = [], []
    for i in range(11):
        for j in range(i + 1, 11):
            if AN.pair_gap(sq[i], sq[j], z) < tol:
                rows, kinds, kind = AN.contact_rows(sq[i], sq[j], z, NV)
                for r in rows:
                    J.append(r)
                    lab.append((A.NAMES[i], A.NAMES[j], kind))
    for i in range(11):
        rows, names = AN.wall_rows(sq[i], z, s, NV)
        for r, nm in zip(rows, names):
            J.append(r)
            lab.append((A.NAMES[i], nm[1], 'wall'))
    return np.array(J), lab


def main():
    t0 = time.time()
    out = {}
    s, cfg = EX.exact_float()
    out['s_star'] = s

    # ---------------- (a) first-order Fritz-John, and where it fails
    J, lab = active_jacobian(s, cfg)
    e = np.zeros(NV); e[0] = 1.0
    Jn = J / np.linalg.norm(J, axis=1)[:, None]
    lam, res = nnls(Jn.T, e)
    resid = Jn.T @ lam - e
    names = ['s'] + [f'{A.NAMES[i]}.{c}' for i in range(11) for c in ('x', 'y', 'th')]
    worst = sorted(range(NV), key=lambda k: -abs(resid[k]))[:6]
    out['fritz_john'] = dict(rows=int(J.shape[0]), residual=float(res),
                             worst=[[names[k], float(resid[k])] for k in worst],
                             forces=sorted([[lab[i][0], lab[i][1], lab[i][2], float(lam[i])]
                                            for i in range(len(lam)) if lam[i] > 1e-9],
                                           key=lambda t: -t[3]))
    print(f'Fritz-John residual {res:.4f}; concentrated on ' +
          ', '.join(f'{names[k]} {resid[k]:+.3f}' for k in worst[:3]))

    # the geometric reason: d(top-wall gap)/d(theta) for a 45 deg square
    d = {}
    for dt in (1e-3, 1e-2, 3e-2):
        w = lambda t: (abs(math.cos(t)) + abs(math.sin(t))) / 2.0
        d[dt] = [w(math.pi / 4) - w(math.pi / 4 + dt), w(math.pi / 4) - w(math.pi / 4 - dt)]
    out['halfwidth_is_maximal_at_45'] = {str(k): v for k, v in d.items()}
    print('half-width loss when a 45 deg square is rotated by +/-dt:',
          {k: [round(x, 9) for x in v] for k, v in d.items()})

    # ---------------- (b0) the decisive test: minimise s inside an L-inf trust region of radius rho
    z_star = A.to107(s, cfg)
    tr = []
    for rho in (1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1):
        best = None
        rng0 = np.random.RandomState(97)
        starts = [z_star.copy()]
        for k in range(12):                     # random starts INSIDE the trust region
            z = z_star.copy()
            z[1:] += rng0.uniform(-rho, rho, 33)
            z[0] = s + 0.5 * rho
            starts.append(z)
        for z0 in starts:
            sv, feas = solve_pinned(z0, trust=rho, centre=z_star)
            if sv is not None and (best is None or sv < best):
                best = sv
        tr.append(dict(rho=rho, s_min=best, drop=(None if best is None else best - s)))
        print(f'  trust region rho={rho:.0e}: min s = '
              f"{'n/a' if best is None else format(best, '.9f')}  "
              f"({'n/a' if best is None else format(best - s, '+.2e')})")
    out['trust_region'] = tr

    # ---------------- (b) second-order profiles: pin one coordinate, re-minimise everything else
    prof = {}
    targets = [('f0.th', 3), ('f1.th', 6), ('f2.th', 9), ('f4.th', 15),
               ('f0.x', 1), ('f0.y', 2), ('f4.x', 13)]
    for nm, idx in targets:
        base = z_star[idx]
        row = []
        for dv in (-3e-2, -1e-2, -3e-3, -1e-3, 1e-3, 3e-3, 1e-2, 3e-2):
            sv, feas = solve_pinned(z_star, pins=[(idx, base + dv)],
                                    trust=max(10 * abs(dv), 3e-2), centre=z_star)
            row.append(dict(delta=dv, s=sv, feas=feas, rise=(None if sv is None else sv - s)))
        prof[nm] = row
        print(f'  profile {nm:6s}: ' + '  '.join(
            f"{r['delta']:+.0e}:{'infeas' if r['s'] is None else format(r['rise'], '+.2e')}"
            for r in row))
    out['profiles'] = prof

    # ---------------- descent hunt along the Fritz-John residual direction
    u = -resid.copy(); u[0] = 0.0
    n = np.linalg.norm(u)
    hunt = []
    if n > 0:
        u /= n
        for t in (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, -1e-4, -1e-3, -1e-2, -3e-2):
            z = z_star + t * u
            z[0] = s
            sv, feas = solve_pinned(z, trust=max(10 * abs(t), 3e-3), centre=z_star)
            hunt.append(dict(t=t, s=sv, rise=(None if sv is None else sv - s)))
    out['residual_direction_hunt'] = hunt
    print('  hunt along the FJ residual direction: ' + '  '.join(
        f"{h['t']:+.0e}:{'infeas' if h['s'] is None else format(h['rise'], '+.2e')}" for h in hunt))

    # ---------------- (c) rigidity: two-sided nullspace and one-sided cone
    Jf = J[:, 1:]
    sv = np.linalg.svd(Jf, compute_uv=False)
    rank = int((sv > max(Jf.shape) * sv[0] * 1e-10).sum())
    U, Sg, Vt = np.linalg.svd(Jf)
    null = Vt[rank:]
    # one-sided cone: maximise sum(Jf v) s.t. Jf v >= 0, |v|_inf <= 1, v orthogonal to nullspace
    Aub = np.vstack([-Jf, null, -null])
    bub = np.zeros(Aub.shape[0])
    r = linprog(c=-(Jf.sum(axis=0)), A_ub=Aub, b_ub=bub,
                bounds=[(-1, 1)] * 33, method='highs')
    onesided = float(-r.fun) if r.status == 0 else None
    out['rigidity'] = dict(rows=int(J.shape[0]), vars_fixed_s=33, rank_fixed_s=rank,
                           two_sided_flexes=33 - rank,
                           one_sided_lp_value=onesided,
                           one_sided_v=(r.x.tolist() if r.status == 0 else None))
    print(f'  rank at fixed s {rank}/33 -> {33-rank} two-sided flexes; '
          f'one-sided LP objective {onesided}')
    if r.status == 0 and onesided is not None and onesided > 1e-9:
        big = sorted(range(33), key=lambda k: -abs(r.x[k]))[:6]
        out['rigidity']['one_sided_support'] = [[names[1 + k], float(r.x[k])] for k in big]
        print('     one-sided flex lives on: ' +
              ', '.join(f'{names[1+k]} {r.x[k]:+.2f}' for k in big))

    # ---------------- basin probe: perturb, then re-minimise with NO trust region (global walk)
    #                  amplitude-resolved, so the escape radius of the basin is visible
    rng = np.random.RandomState(4711)
    probe = {}
    for amp in (0.002, 0.01, 0.03, 0.08, 0.2):
        land = []
        for k in range(40):
            z = z_star.copy()
            z[1:] += rng.uniform(-amp, amp, 33) * np.tile([1.0, 1.0, 0.8], 11)
            z[0] = s
            svv, feas = solve_pinned(z)
            if svv is not None:
                land.append(round(svv, 7))
        probe[str(amp)] = dict(n=len(land), spectrum=sorted(set(land))[:12],
                               n_below=sum(1 for v in land if v < s - 1e-8),
                               n_at_shat=sum(1 for v in land if abs(v - A.SHAT) < 1e-5),
                               lowest=(min(land) if land else None))
        print(f'  basin probe amp={amp:.3f}: {len(land)} feasible, lowest '
              f"{'n/a' if not land else format(min(land), '.9f')}, "
              f"{probe[str(amp)]['n_below']} below s*, {probe[str(amp)]['n_at_shat']} at s-hat")
    out['basin_probe'] = probe

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'localmin.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote results/localmin.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
