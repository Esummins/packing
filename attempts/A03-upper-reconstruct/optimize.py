"""
optimize.py -- multi-start penalised optimisation for packing n unit squares in a square.

Variables z = (cx_0, cy_0, th_0, ..., cx_{n-1}, cy_{n-1}, th_{n-1}, s)  (3n+1 numbers).
Objective: minimise s.
Constraints (all >= 0):
  * for every pair i<j : SAT separation  max_axes gap_axis(i,j)   (55 for n=11)
  * for every square   : min_x corners >= 0, min_y >= 0, s - max_x >= 0, s - max_y >= 0

Analytic gradients / Jacobians (piecewise-smooth: the active axis / extreme corners are
frozen at the current point, which is exact away from ties and works fine in practice).

Pipeline per start:  penalty method with L-BFGS-B (mu = 1e2 ... 1e6)  ->  SLSQP polish
with the true inequality constraints (ftol 1e-16).

Usage:  python optimize.py --starts 200 --workers 8 --out runs.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'code'))
from squares import all_corners, pair_separations, containment_margin, normalise_angles  # noqa: E402

N = 11
_HALF = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])
PAIRS = np.array(list(itertools.combinations(range(N), 2)))
NV = 3 * N + 1


def unpack(z):
    return z[:3 * N].reshape(N, 3), z[3 * N]


def rot_and_deriv(th):
    c, s = np.cos(th), np.sin(th)
    R = np.empty((len(th), 2, 2))
    R[:, 0, 0] = c; R[:, 0, 1] = -s; R[:, 1, 0] = s; R[:, 1, 1] = c
    dR = np.empty_like(R)
    dR[:, 0, 0] = -s; dR[:, 0, 1] = -c; dR[:, 1, 0] = c; dR[:, 1, 1] = -s
    return R, dR


def constraints(z):
    """Return (g, J): all constraint values (m,) and Jacobian (m, NV)."""
    X, s = unpack(z)
    th = X[:, 2]
    R, dR = rot_and_deriv(th)
    P = X[:, None, :2] + np.einsum('kj,nij->nki', _HALF, R)      # (n,4,2) corners
    dP = np.einsum('kj,nij->nki', _HALF, dR)                      # d corners / d theta (n,4,2)
    # normals: axis 0 = R e1 = (c,s); axis 1 = R e2 = (-s,c); derivatives dR e1, dR e2
    A = np.stack([R[:, :, 0], R[:, :, 1]], 1)                     # (n,2,2)  [n, axis, xy]
    dA = np.stack([dR[:, :, 0], dR[:, :, 1]], 1)

    m_pairs = len(PAIRS)
    g = np.empty(m_pairs + 4 * N)
    J = np.zeros((m_pairs + 4 * N, NV))

    i, j = PAIRS[:, 0], PAIRS[:, 1]
    AX = np.concatenate([A[i], A[j]], 1)                          # (m,4,2)
    dAX = np.concatenate([dA[i], dA[j]], 1)
    owner = np.stack([i, i, j, j], 1)                             # (m,4) which square owns axis
    pi = np.einsum('mkd,mad->mak', P[i], AX)                      # (m,4ax,4corner)
    pj = np.einsum('mkd,mad->mak', P[j], AX)
    gap1 = pj.min(2) - pi.max(2)      # j above i
    gap2 = pi.min(2) - pj.max(2)      # i above j
    gap = np.maximum(gap1, gap2)      # (m,4)
    a_star = gap.argmax(1)            # active axis
    rows = np.arange(m_pairs)
    g[:m_pairs] = gap[rows, a_star]
    use1 = gap1[rows, a_star] >= gap2[rows, a_star]
    ax = AX[rows, a_star]             # (m,2)
    dax = dAX[rows, a_star]
    own = owner[rows, a_star]
    # B = "upper" square, A = "lower" square along axis
    Bsq = np.where(use1, j, i)
    Asq = np.where(use1, i, j)
    pB = np.where(use1[:, None], pj[rows, a_star], pi[rows, a_star])   # projections (m,4)
    pA = np.where(use1[:, None], pi[rows, a_star], pj[rows, a_star])
    cB = pB.argmin(1)
    cA = pA.argmax(1)
    PB = P[Bsq, cB]                    # extreme corner points (m,2)
    PA = P[Asq, cA]
    dPB = dP[Bsq, cB]
    dPA = dP[Asq, cA]
    # d/dc_B = ax ; d/dc_A = -ax
    J[rows, 3 * Bsq] += ax[:, 0]; J[rows, 3 * Bsq + 1] += ax[:, 1]
    J[rows, 3 * Asq] -= ax[:, 0]; J[rows, 3 * Asq + 1] -= ax[:, 1]
    # d/dtheta_B, d/dtheta_A via corner motion
    J[rows, 3 * Bsq + 2] += np.einsum('md,md->m', ax, dPB)
    J[rows, 3 * Asq + 2] -= np.einsum('md,md->m', ax, dPA)
    # axis rotation term for owner
    J[rows, 3 * own + 2] += np.einsum('md,md->m', dax, PB - PA)

    # wall constraints
    base = m_pairs
    for k in range(N):
        x = P[k, :, 0]; y = P[k, :, 1]
        cx0 = x.argmin(); cy0 = y.argmin(); cx1 = x.argmax(); cy1 = y.argmax()
        r = base + 4 * k
        g[r] = x[cx0];       J[r, 3 * k] = 1;   J[r, 3 * k + 2] = dP[k, cx0, 0]
        g[r + 1] = y[cy0];   J[r + 1, 3 * k + 1] = 1; J[r + 1, 3 * k + 2] = dP[k, cy0, 1]
        g[r + 2] = s - x[cx1]; J[r + 2, 3 * k] = -1; J[r + 2, 3 * k + 2] = -dP[k, cx1, 0]; J[r + 2, NV - 1] = 1
        g[r + 3] = s - y[cy1]; J[r + 3, 3 * k + 1] = -1; J[r + 3, 3 * k + 2] = -dP[k, cy1, 1]; J[r + 3, NV - 1] = 1
    return g, J


def penalty_obj(z, mu):
    g, J = constraints(z)
    v = np.minimum(g, 0.0)
    f = z[-1] + mu * np.dot(v, v)
    grad = 2 * mu * (v @ J)
    grad[-1] += 1.0
    return f, grad


def check_jacobian(seed=0):
    rng = np.random.default_rng(seed)
    z = np.concatenate([rng.uniform(0.5, 3.5, 3 * N), [4.0]])
    z[2::3] = rng.uniform(0, 1.5, N)
    g, J = constraints(z)
    Jn = np.zeros_like(J)
    h = 1e-7
    for k in range(NV):
        zp = z.copy(); zp[k] += h
        zm = z.copy(); zm[k] -= h
        Jn[:, k] = (constraints(zp)[0] - constraints(zm)[0]) / (2 * h)
    err = np.abs(J - Jn).max()
    print('max Jacobian error (finite differences):', err)
    return err


def penalty_fixed_s(x, s, mu):
    z = np.concatenate([x, [s]])
    f, grad = penalty_obj(z, mu)
    return f - s, grad[:-1]


BOUNDS = [(-0.5, 6.5), (-0.5, 6.5), (None, None)] * N + [(3.5, 6.0)]


def solve_from(z0, seed=None, mus=(1e2, 1e3, 1e4, 1e5, 1e6), verbose=False, fixed_s_stage=True):
    """Penalty method (optionally starting with s frozen at z0[-1]) then SLSQP polish.
    Returns (X (n,3) with angles in [0,pi/2), s, max constraint violation)."""
    z = np.array(z0, dtype=float)
    if fixed_s_stage:
        x = z[:-1]
        for mu in (1e1, 1e2, 1e3):
            res = minimize(penalty_fixed_s, x, args=(z[-1], mu), jac=True, method='L-BFGS-B',
                           bounds=BOUNDS[:-1], options={'maxiter': 2000, 'ftol': 1e-14, 'gtol': 1e-9})
            x = res.x
        z = np.concatenate([x, [z[-1]]])
        if verbose:
            g, _ = constraints(z)
            print(f'  fixed-s stage: s={z[-1]:.4f} maxviol={-min(g.min(), 0):.2e}')
    for mu in mus:
        res = minimize(penalty_obj, z, args=(mu,), jac=True, method='L-BFGS-B', bounds=BOUNDS,
                       options={'maxiter': 3000, 'ftol': 1e-15, 'gtol': 1e-10})
        z = res.x
        if verbose:
            g, _ = constraints(z)
            print(f'  mu={mu:.0e}  s={z[-1]:.9f}  maxviol={-min(g.min(), 0):.2e}')
    # SLSQP polish
    cons = [{'type': 'ineq', 'fun': lambda z: constraints(z)[0], 'jac': lambda z: constraints(z)[1]}]
    best = None
    for attempt in range(4):
        res = minimize(lambda z: z[-1], z, jac=lambda z: np.eye(NV)[-1], method='SLSQP',
                       constraints=cons, options={'maxiter': 1000, 'ftol': 1e-16})
        z = res.x
        g, _ = constraints(z)
        viol = -min(g.min(), 0.0)
        if verbose:
            print(f'  SLSQP #{attempt}: s={z[-1]:.12f} viol={viol:.2e} status={res.status} nit={res.nit}')
        if best is None or z[-1] + 1e3 * viol < best[0][-1] + 1e3 * best[1]:
            best = (z.copy(), viol)
        if viol < 1e-11 and res.status == 0:
            break
        if viol > 1e-9:   # SLSQP got stuck: re-run high-mu penalty then retry
            for mu in (1e7, 1e8):
                res2 = minimize(penalty_obj, z, args=(mu,), jac=True, method='L-BFGS-B', bounds=BOUNDS,
                                options={'maxiter': 3000, 'ftol': 1e-15, 'gtol': 1e-10})
                z = res2.x
    z, viol = best
    X, s = unpack(z)
    return normalise_angles(X), float(s), float(viol)


def solve_with_kicks(z0, rng, kicks=3, verbose=False):
    """solve_from + `kicks` random perturbations of the result (angles of tilted squares
    N(0,0.05), all positions N(0,0.01)) followed by re-solves; the 45-degree packings are
    nonsmooth traps for SLSQP and this escapes them.  Returns best (X, s, viol) and the list
    of all distinct converged (X, s, viol) seen."""
    X, s, viol = solve_from(z0, verbose=verbose)
    seen = [(X, s, viol)]
    best = (X, s, viol)
    for k in range(kicks):
        Y = best[0].copy()
        Y[:, 2] += rng.normal(0, 0.05, N)
        Y[:, :2] += rng.normal(0, 0.01, (N, 2))
        z = np.concatenate([Y.ravel(), [best[1]]])
        try:
            X2, s2, v2 = solve_from(z, fixed_s_stage=False)
        except Exception:
            continue
        seen.append((X2, s2, v2))
        if v2 < 1e-9 and s2 < best[1] - 1e-9 and s2 > 3.5:
            best = (X2, s2, v2)
    return best, seen


def random_start(rng, s0=None):
    if s0 is None:
        s0 = rng.uniform(3.80, 3.95)
    X = np.empty((N, 3))
    X[:, 0] = rng.uniform(0.5, s0 - 0.5, N)
    X[:, 1] = rng.uniform(0.5, s0 - 0.5, N)
    X[:, 2] = rng.uniform(0, math.pi / 2, N)
    return np.concatenate([X.ravel(), [s0]])


def seeded_start(rng, kind, jitter=0.05):
    """Trump-like seeds: two L-triominoes of uprights in opposite corners + 5 tilted squares in
    a diagonal band.  kind 0: L's at bottom-left / top-right, band along the anti-diagonal.
    kind 1: uprights along two walls (bottom row of 3 + left column) + band."""
    s0 = 3.9
    th = math.radians(40.18)
    if kind == 2:
        # the Gobel/Stromquist 45-degree layout (s = 2 + 2 sqrt(8/9)) with angles kicked to ~40 deg
        X = np.array(X45_LAYOUT)
        X[6:, 2] = th
        X[:, :2] += rng.normal(0, jitter, (N, 2))
        X[:, 2] += rng.normal(0, jitter, N)
        return np.concatenate([X.ravel(), [3.8856]])
    if kind == 0:
        # L of 5 uprights on bottom/left walls, one upright in the top-right corner,
        # 5 tilted squares in a two-rail ladder along the anti-diagonal
        up = [(0.5, 0.5), (1.5, 0.5), (2.53, 0.5), (0.5, 1.5), (0.5, 2.53), (s0 - 0.5, s0 - 0.5)]
        u = np.array([math.cos(math.radians(130.18)), math.sin(math.radians(130.18))])
        p = np.array([math.cos(math.radians(40.18)), math.sin(math.radians(40.18))])
        base = np.array([3.2, 0.8])
        sign = 1 if rng.uniform() < 0.5 else -1
        tilt = [tuple(base), tuple(base + 1.3 * u), tuple(base + 2.6 * u),
                tuple(base + sign * 1.03 * p + 0.65 * u), tuple(base + sign * 1.03 * p + 1.95 * u)]
    else:
        # same uprights, tilted squares scattered in the band
        up = [(0.5, 0.5), (1.5, 0.5), (2.53, 0.5), (0.5, 1.5), (0.5, 2.53), (s0 - 0.5, s0 - 0.5)]
        tilt = [(rng.uniform(1.2, 3.2), 0.0) for _ in range(5)]
        tilt = [(x, rng.uniform(max(0.7, 3.6 - x), min(3.3, 5.0 - x))) for x, _ in tilt]
    X = np.empty((N, 3))
    for k, (x, y) in enumerate(up):
        X[k] = (x, y, 0.0)
    for k, (x, y) in enumerate(tilt):
        X[6 + k] = (x, y, th)
    X[:, :2] += rng.normal(0, jitter, (N, 2))
    X[:, 2] += rng.normal(0, jitter, N)
    return np.concatenate([X.ravel(), [s0]])


X45_LAYOUT = [[0.5, 0.5, 0.0], [1.5, 0.5, 0.0], [3.3856, 0.5, 0.0], [0.5, 1.5, 0.0], [0.5, 2.5, 0.0],
              [3.3856, 3.3856, 0.0], [2.4477, 1.2692, 0.7854], [1.7071, 1.9428, 0.7854],
              [3.1782, 1.9532, 0.7854], [2.4142, 2.6499, 0.7854], [1.5286, 3.1785, 0.7854]]


def worker(task):
    idx, kind, seed = task
    rng = np.random.default_rng(seed)
    if kind == 'random':
        z0 = random_start(rng)
    elif kind == 'seedA':
        z0 = seeded_start(rng, 0)
    elif kind == 'seedB':
        z0 = seeded_start(rng, 1)
    else:
        z0 = seeded_start(rng, 2)
    t0 = time.time()
    try:
        (X, s, viol), seen = solve_with_kicks(z0, rng)
    except Exception as e:   # pragma: no cover
        return {'idx': idx, 'kind': kind, 'seed': seed, 'error': repr(e)}
    return {'idx': idx, 'kind': kind, 'seed': seed, 's': s, 'viol': viol,
            'X': X.tolist(), 'time': time.time() - t0,
            'seen': [{'s': a[1], 'viol': a[2], 'X': a[0].tolist()} for a in seen]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--starts', type=int, default=100)
    ap.add_argument('--seeded', type=int, default=10)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--seed', type=int, default=12345)
    ap.add_argument('--out', default='runs.json')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    if args.check:
        check_jacobian()
        return
    tasks = []
    k = 0
    for j in range(args.seeded):
        tasks.append((k, 'seedA', args.seed + k)); k += 1
        tasks.append((k, 'seedB', args.seed + k)); k += 1
        tasks.append((k, 'seedC', args.seed + k)); k += 1
    for j in range(args.starts):
        tasks.append((k, 'random', args.seed + k)); k += 1
    from multiprocessing import Pool
    t0 = time.time()
    results = []
    with Pool(args.workers) as pool:
        for r in pool.imap_unordered(worker, tasks):
            results.append(r)
            if 's' in r:
                print(f"[{len(results)}/{len(tasks)}] {r['kind']:7s} s={r['s']:.10f} viol={r['viol']:.1e} ({r['time']:.1f}s)", flush=True)
            else:
                print(r, flush=True)
    results.sort(key=lambda r: r.get('s', 99))
    with open(args.out, 'w') as f:
        json.dump(results, f, indent=1)
    print('total time', time.time() - t0)


if __name__ == '__main__':
    main()
