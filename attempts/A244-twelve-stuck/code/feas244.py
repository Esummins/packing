"""A244: find a feasible 12-stuck (or 4-stuck) packing and push its side down.

Phase A -- feasibility with the side FREE (the twelve-cell condition is infeasible for LARGE s as
well as for small s: 24 incidences over 11 squares need cells inside one square's reach, so
widening never helps by itself).  Phase B -- halving descent on s, re-polishing at each side.
A polish is accepted only when the penalty is exactly 0, i.e. the configuration is a packing with
every constrained cell met by two squares to depth >= delta.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast244 as F
import cells244 as C

OPT = {'maxiter': 1200, 'ftol': 1e-20, 'gtol': 1e-16, 'maxcor': 20}


def bounds(free_s, smin=2.5, smax=7.0):
    b = [(None, None)] * F.NV
    b[F.S_IDX] = (smin, smax) if free_s else (None, None)
    return b


def polish(z, cells, delta, free_s=False, smin=2.5, smax=7.0):
    r = minimize(F.penalty, z, args=(cells, delta, free_s, 0.0), jac=True, method='L-BFGS-B',
                 bounds=bounds(free_s, smin, smax), options=OPT)
    return np.array(r.x, float), float(r.fun)


def jitter(z, rng, pos=0.06, tilt=4.0, s=0.0):
    w = np.array(z, float)
    w[0:33:3] += rng.normal(0, pos, F.N)
    w[1:33:3] += rng.normal(0, pos, F.N)
    w[2:33:3] += np.radians(rng.normal(0, tilt, F.N))
    if s:
        w[F.S_IDX] += rng.normal(0, s)
    return w


def phase_a(z0, cells, delta, rng, tries=6, smax=7.0):
    """feasibility with the side free; returns (z, ok)."""
    z, f = polish(z0, cells, delta, free_s=True, smax=smax)
    best = (f, z)
    for k in range(tries):
        if best[0] == 0.0:
            break
        z2, f2 = polish(jitter(best[1], rng, 0.10, 8.0, 0.12), cells, delta, free_s=True, smax=smax)
        if f2 < best[0]:
            best = (f2, z2)
    return best[1], best[0] == 0.0


def phase_b(z, cells, delta, rng, step0=0.12, tol=1e-7, retries=3):
    """halving descent on s from a feasible z."""
    s = float(z[F.S_IDX])
    step = step0
    best = np.array(z, float)
    while step > tol:
        s2 = s - step
        lam = s2 / s
        cand = np.array(best, float)
        cand[0:33:3] *= lam
        cand[1:33:3] *= lam
        cand[F.S_IDX] = s2
        got = None
        for k in range(retries + 1):
            start = cand if k == 0 else jitter(cand, rng, 0.03 * k, 2.0 * k)
            start[F.S_IDX] = s2
            w, f = polish(start, cells, delta)
            if f == 0.0:
                got = w
                break
        if got is None:
            step /= 2
        else:
            best, s = got, s2
    return best, s


def run(z0, cells, delta, rng, smax=7.0, step0=0.12, tol=1e-7):
    z, ok = phase_a(z0, cells, delta, rng, smax=smax)
    if not ok:
        return None, float(z[F.S_IDX]), F.worst(z, cells, delta)
    z, s = phase_b(z, cells, delta, rng, step0=step0, tol=tol)
    return z, s, F.worst(z, cells, delta)


def random_start(rng, S):
    z = np.zeros(F.NV)
    z[0:33:3] = rng.uniform(0.6, S - 0.6, F.N)
    z[1:33:3] = rng.uniform(0.6, S - 0.6, F.N)
    z[2:33:3] = rng.uniform(0, math.pi / 2, F.N)
    z[F.S_IDX] = S
    return z


def border_start(rng, S):
    """a start that already puts squares where the twelve cells are: two per corner near the
    frame point (1,1), one per wall, three loose."""
    z = np.zeros(F.NV)
    pts = []
    for (ax, ay) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        px = 1.0 if ax > 0 else S - 1.0
        py = 1.0 if ay > 0 else S - 1.0
        for _ in range(2):
            pts.append((px + rng.normal(0, 0.35), py + rng.normal(0, 0.35)))
    m = S / 2
    for (px, py) in ((m, 0.5), (S - 0.5, m), (m, S - 0.5)):
        pts.append((px + rng.normal(0, 0.3), py + rng.normal(0, 0.3)))
    for i, (x, y) in enumerate(pts[:F.N]):
        z[3 * i], z[3 * i + 1] = x, y
        z[3 * i + 2] = rng.uniform(0, math.pi / 2)
    z[F.S_IDX] = S
    return z


def grid_start(rng, S):
    cells = [(i + 0.5, j + 0.5) for i in range(4) for j in range(4)]
    border = [c for c in cells if c[0] in (0.5, 3.5) or c[1] in (0.5, 3.5)]
    keep = [border[k] for k in rng.permutation(len(border))[:11]]
    f = S / 4.0
    z = np.zeros(F.NV)
    for i, (x, y) in enumerate(keep):
        z[3 * i] = x * f + rng.normal(0, 0.12)
        z[3 * i + 1] = y * f + rng.normal(0, 0.12)
        z[3 * i + 2] = np.radians(rng.normal(0, 10))
    z[F.S_IDX] = S
    return z


STARTS = {'random': random_start, 'border': border_start, 'grid': grid_start}
CELLSETS = {'twelve': list(C.CELLS), 'four': list(C.BOXES), 'slots': list(C.SLOTS),
            'none': []}          # 'none' = the packing-only baseline of the probe
