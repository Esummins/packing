"""
Reduced-parameter families: squares are assigned to angle groups; each group has ONE shared angle
(group 0 = upright, fixed at 0).  Optimise centres + group angles + s with the penalty method,
then release all angles and polish in the full space.
"""
import numpy as np
from scipy.optimize import minimize
import pack11 as P
from pack11 import N, unpack, pack, obj_grad, penalty_solve


def build_x(y, groups, ngroups):
    """y = (centres 2N, group angles ngroups-1 (group 0 fixed to 0), s)."""
    c = y[:2 * N]
    gang = np.concatenate([[0.0], y[2 * N:2 * N + ngroups - 1]])
    th = gang[groups]
    s = y[2 * N + ngroups - 1]
    return np.concatenate([c, th, [s]])


def reduce_g(g, groups, ngroups):
    gth = g[2 * N:3 * N]
    gg = np.zeros(ngroups)
    np.add.at(gg, groups, gth)
    return np.concatenate([g[:2 * N], gg[1:], [g[3 * N]]])


def obj_grad_red(y, mu, groups, ngroups):
    x = build_x(y, groups, ngroups)
    F, g = obj_grad(x, mu)
    return F, reduce_g(g, groups, ngroups)


def penalty_solve_red(y0, groups, ngroups, mus=(10., 100., 1e3, 1e4, 1e5, 1e6), maxiter=400):
    y = y0.copy()
    for mu in mus:
        res = minimize(obj_grad_red, y, args=(mu, groups, ngroups), jac=True, method='L-BFGS-B',
                       options=dict(maxiter=maxiter, maxcor=20, ftol=1e-15, gtol=1e-9))
        y = res.x
        y[2 * N:2 * N + ngroups - 1] = np.mod(y[2 * N:2 * N + ngroups - 1], np.pi / 2)
    return y


def family_start(rng, k, ngroups=2, s0=None, tilt=None, grid_uprights=True):
    """k uprights (group 0), remaining squares split among ngroups-1 tilted groups."""
    if s0 is None:
        s0 = rng.uniform(3.9, 4.25)
    groups = np.zeros(N, dtype=int)
    rest = np.arange(k, N)
    if ngroups > 2:
        groups[rest] = rng.integers(1, ngroups, size=len(rest))
        # make sure each group non-empty
        for gI in range(1, ngroups):
            if not np.any(groups == gI) and len(rest) >= ngroups - 1:
                groups[rest[gI - 1]] = gI
    else:
        groups[rest] = 1
    c = rng.uniform(0.6, s0 - 0.6, size=(N, 2))
    if grid_uprights and rng.random() < 0.7:
        # place uprights on a loose grid near the walls
        cells = [(i + 0.5, j + 0.5) for i in range(4) for j in range(4)
                 if i in (0, 3) or j in (0, 3)]
        idx = rng.choice(len(cells), size=min(k, len(cells)), replace=False)
        for m, ci in enumerate(idx):
            c[m] = np.array(cells[ci]) * (s0 / 4.0) + rng.normal(0, 0.05, 2)
    if tilt is None:
        gang = rng.uniform(np.radians(15), np.radians(75), size=ngroups - 1)
    else:
        gang = np.radians(np.atleast_1d(tilt)) + rng.normal(0, 0.05, size=ngroups - 1)
    y0 = np.concatenate([c.ravel(), gang, [s0]])
    return y0, groups


def run_family(rng, k, ngroups=2, tilt=None):
    y0, groups = family_start(rng, k, ngroups, tilt=tilt)
    y = penalty_solve_red(y0, groups, ngroups)
    x = build_x(y, groups, ngroups)
    return x, groups


if __name__ == '__main__':
    import time
    rng = np.random.default_rng(5)
    t0 = time.time()
    for m in range(20):
        k = int(rng.integers(4, 9))
        x, groups = run_family(rng, k, ngroups=2)
        # release
        x2 = penalty_solve(x, mus=(1e5, 1e6, 1e7, 1e8), maxiter=1000)
        print(k, '%.6f -> %.6f' % (x[3 * N], x2[3 * N]), P.feasibility(x2), P.canonical(x2)[1])
    print('per start', (time.time() - t0) / 20)
