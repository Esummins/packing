"""A217 local side-minimisation of 11 unit squares (SLSQP on the selected SAT rows, outer loop
re-selecting axes), optional tilt box on the corner squares (the no-settled-corner constraint),
active-set FJ residual by NNLS, D4 canonical signature.
"""
import math
import os
import sys
import json
import time

import numpy as np
from scipy.optimize import minimize, nnls

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G

PI2 = math.pi / 2
E_S = np.zeros(G.NV)
E_S[G.S_IDX] = 1.0


# ------------------------------------------------------------------ penalty feasibility phase
def penalty(z):
    """sum of squared violations (walls + SAT gaps); s fixed inside z."""
    gw, Jw = G.wall_rows(z)
    sel, gaps = G.best_selection(z)
    gp, Jp = G.pair_rows(z, sel)
    vw = np.minimum(gw, 0.0)
    vp = np.minimum(gp, 0.0)
    f = float(vw @ vw + vp @ vp)
    grad = 2 * (vw @ Jw + vp @ Jp)
    grad[G.S_IDX] = 0.0
    return f, grad


def feasible_start(z0, iters=200):
    z = np.array(z0, float)
    for _ in range(6):
        r = minimize(penalty, z, jac=True, method='L-BFGS-B', options={'maxiter': iters})
        z = r.x
        if r.fun < 1e-20:
            break
        z[G.S_IDX] += 0.3                         # widen the container and retry
    return z


def random_start(rng, S=5.0):
    z = np.zeros(G.NV)
    z[0::3][:11] = rng.uniform(0.75, S - 0.75, 11)
    z[1::3][:11] = rng.uniform(0.75, S - 0.75, 11)
    z[2::3][:11] = rng.uniform(0, PI2, 11)
    z[G.S_IDX] = S
    return feasible_start(z)


# ------------------------------------------------------------------ the local optimiser
def corner_squares(z, size=1.0):
    out = set()
    for c in G.CORNER_NAMES:
        out.update(G.corner_meeters(z, c, size))
    return out


def local_opt(z0, tmin=None, max_outer=40, ftol=1e-14, tol_step=1e-9, verbose=False, extra=None):
    """Minimise s.  tmin: if not None every square meeting a corner box gets theta in
    [tmin, pi/2 - tmin] (the no-settled-corner constraint); other squares unbounded.
    extra: optional callable z -> (fun, jac) giving further smooth rows g >= 0 (fixed per outer
    iteration; the crowd rows of crowd217)."""
    z = G.wrap_theta(np.array(z0, float))
    hist = []
    for outer in range(max_outer):
        sel, gaps = G.best_selection(z)
        efun, ejac = extra(z) if extra is not None else (None, None)
        csq = corner_squares(z) if tmin is not None else set()
        bounds = []
        for i in range(G.N):
            bounds += [(None, None), (None, None)]
            bounds.append((tmin, PI2 - tmin) if i in csq else (None, None))
        bounds.append((2.5, 9.0))
        for i in csq:                               # push into the box before SLSQP
            z[3 * i + 2] = min(max(z[3 * i + 2], tmin), PI2 - tmin)

        def cons(x):
            parts = [G.wall_rows(x)[0], G.pair_rows(x, sel)[0]]
            if efun is not None:
                parts.append(efun(x))
            return np.concatenate(parts)

        def jcons(x):
            parts = [G.wall_rows(x)[1], G.pair_rows(x, sel)[1]]
            if ejac is not None:
                parts.append(ejac(x))
            return np.vstack(parts)

        r = minimize(lambda x: x[G.S_IDX], z, jac=lambda x: E_S, method='SLSQP', bounds=bounds,
                     constraints=[{'type': 'ineq', 'fun': cons, 'jac': jcons}],
                     options={'maxiter': 400, 'ftol': ftol})
        znew = G.wrap_theta(r.x)
        sel2, gaps2 = G.best_selection(znew)
        step = max(np.abs(znew[0::3][:11] - z[0::3][:11]).max(), np.abs(znew[1::3][:11] - z[1::3][:11]).max(),
                   abs(znew[G.S_IDX] - z[G.S_IDX]),
                   max(G.axis_dev(a - b) for a, b in zip(znew[2::3][:11], z[2::3][:11])))
        hist.append((outer, float(znew[G.S_IDX]), float(step), int(r.status)))
        if verbose:
            print(outer, znew[G.S_IDX], step, r.status, r.message, flush=True)
        z = znew
        if sel2 == sel and step < tol_step:
            break
    return z, hist


# ------------------------------------------------------------------ active rows + FJ residual
def active_rows(z, tol=1e-7):
    """All rows active at z (walls: every corner within tol of a wall; pairs: every axis whose
    min-corner projection is within tol of 0, its corner rows within tol).  Returns
    list of row dicts and the jacobian matrix (m, 34)."""
    rows, J = [], []
    gw, Jw = G.wall_rows(z)
    gw = gw.reshape(G.N, 4, 4)
    Jw = Jw.reshape(G.N, 4, 4, G.NV)
    for i in range(G.N):
        for k in range(4):
            for w in range(4):
                if abs(gw[i, k, w]) <= tol:
                    rows.append({'kind': 'wall', 'i': i, 'corner': k, 'wall': G.WALLS[w]})
                    J.append(Jw[i, k, w])
    table = G.sat_table(z)
    for (i, j) in G.PAIRS:
        t = table[(i, j)]
        if t.min(axis=2).max() > tol:
            continue
        for a in range(2):
            o, p = (i, j) if a == 0 else (j, i)
            for e in range(4):
                if abs(t[a, e].min()) <= tol:
                    gp, Jp = _pair_rows_one(z, o, e, p)
                    for k in range(4):
                        if abs(gp[k]) <= tol:
                            rows.append({'kind': 'edge', 'i': p, 'corner': k, 'j': o, 'edge': e})
                            J.append(Jp[k])
    return rows, (np.array(J) if J else np.zeros((0, G.NV)))


def _pair_rows_one(z, o, e, p):
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    nn = G.normals(z)[o, e]
    c = np.stack([cx, cy], -1)
    Jn = np.array([-nn[1], nn[0]])
    g = np.zeros(4)
    J = np.zeros((4, G.NV))
    for k in range(4):
        r = q[p, k] - c[o]
        g[k] = nn @ r - 0.5
        rp = q[p, k] - c[p]
        J[k, 3 * p] = nn[0]
        J[k, 3 * p + 1] = nn[1]
        J[k, 3 * p + 2] = nn[0] * (-rp[1]) + nn[1] * rp[0]
        J[k, 3 * o] = -nn[0]
        J[k, 3 * o + 1] = -nn[1]
        J[k, 3 * o + 2] = Jn @ r
    return g, J


def fj_residual(z, tol=1e-7, tmin=None, btol=1e-7, extra_active=None):
    """NNLS: min |A^T lam - e_s|, lam >= 0 over the active rows (+ active tilt-bound rows when
    tmin is given, + extra_active = (rows, jac) e.g. crowd217's active crowd rows)."""
    rows, A = active_rows(z, tol)
    if extra_active is not None and len(extra_active[0]):
        rows = rows + list(extra_active[0])
        A = np.vstack([A, np.asarray(extra_active[1])])
    if tmin is not None:
        for i in corner_squares(z):
            th = z[3 * i + 2]
            for sign, b in ((1.0, tmin), (-1.0, PI2 - tmin)):
                if abs(th - b) <= btol:
                    g = np.zeros(G.NV)
                    g[3 * i + 2] = sign
                    rows.append({'kind': 'tiltbound', 'i': i, 'bound': b, 'sign': sign})
                    A = np.vstack([A, g])
    if A.shape[0] == 0:
        return 1.0, np.zeros(0), rows
    lam, res = nnls(A.T, E_S, maxiter=50 * A.shape[0])
    return float(res), lam, rows


# ------------------------------------------------------------------ D4 canonical signature
def d4_images(z):
    cx, cy, th, s = G.unpack(z)
    out = []
    for k in range(4):
        for refl in (False, True):
            x, y, t = cx.copy(), cy.copy(), th.copy()
            if refl:
                x, y, t = y, x, PI2 - t
            for _ in range(k):
                x, y, t = s - y, x, t + PI2
            out.append((x, y, t % PI2, s, k, refl))
    return out


def canonical(z, nd=4):
    best = None
    for x, y, t, s, k, refl in d4_images(z):
        sig = sorted(zip(np.round(x, nd), np.round(y, nd), np.round(t, nd)))
        sig = [tuple(float(v) for v in row) for row in sig]
        if best is None or sig < best[0]:
            best = (sig, k, refl)
    return best


def summary(z, tmin=None, extra_active=None):
    cx, cy, th, s = G.unpack(z)
    res, lam, rows = fj_residual(z, tmin=tmin, extra_active=extra_active)
    out = {'s': float(s), 'z': [float(v) for v in z], 'fj_res': res,
           'n_rows': len(rows), 'n_wall_rows': sum(r['kind'] == 'wall' for r in rows),
           'n_edge_rows': sum(r['kind'] == 'edge' for r in rows),
           'n_tiltbound_active': sum(r['kind'] == 'tiltbound' for r in rows),
           'n_crowd_active': sum(r['kind'] == 'crowd' for r in rows),
           'crowd_lam': [float(l) for r, l in zip(rows, lam) if r['kind'] == 'crowd'],
           'tilts_deg': [float(math.degrees(t % PI2)) for t in th],
           'min_pair_gap': float(min(G.pair_gaps(z).values())), 'min_wall_gap': float(G.wall_rows(z)[0].min()),
           'settled': {c: G.settled(z, c, 1e-6) for c in G.CORNER_NAMES},
           'meeters': {c: G.corner_meeters(z, c) for c in G.CORNER_NAMES}}
    out['n_settled'] = sum(v is not None for v in out['settled'].values())
    out['k0'] = out['n_settled'] == 0
    out['sig'] = canonical(z)[0]
    return out
