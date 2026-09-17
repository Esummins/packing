"""A244 side-minimisation with the twelve-cell witness-point crowd rows.

Same scheme as A217's opt217 (SLSQP on the selected SAT rows, outer loop re-selecting the axes)
on the extended vector w = [z (34), witness points (2M)].  The crowd designation `des` is FIXED
for a run; the caller re-designates between rounds.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import opt217 as O
import crowd244 as W

PI2 = math.pi / 2


def pad(J, NW):
    out = np.zeros((J.shape[0], NW))
    out[:, :G.NV] = J
    return out


def rows_all(w, sel, des, delta):
    NW = len(w)
    z = w[:G.NV]
    gw, Jw = G.wall_rows(z)
    gp, Jp = G.pair_rows(z, sel)
    gc, Jc = W.crowd_rows(w, des, delta)
    return (np.concatenate([gw, gp, gc]),
            np.vstack([pad(Jw, NW), pad(Jp, NW), Jc]))


def penalty(w, des, delta, free_s=True, wpen=1e-3):
    """squared violation of walls + pairs + crowd rows.  With free_s the side is a variable and
    is charged wpen * s, so the phase settles at the smallest side it can make feasible -- the
    twelve-cell rows are infeasible for LARGE s as well as small (24 incidences over 11 squares
    need cells within one square's reach), so widening alone never finds the window."""
    z = w[:G.NV]
    sel, _ = G.best_selection(z)
    g, J = rows_all(w, sel, des, delta)
    v = np.minimum(g, 0.0)
    f = float(v @ v)
    grad = 2 * (v @ J)
    if free_s:
        f += wpen * float(w[G.S_IDX])
        grad[G.S_IDX] += wpen
    else:
        grad[G.S_IDX] = 0.0
    return f, grad


def feasible_start(w0, des, delta, iters=500, tries=(0.0, 0.3, -0.3, 0.8), smax=9.0, rng=None):
    """penalty phase with s free, restarted from a few side offsets."""
    bounds = [(None, None)] * len(w0)
    bounds[G.S_IDX] = (2.5, smax)
    best = (np.inf, np.array(w0, float))
    for off in tries:
        w = np.array(w0, float)
        if off:
            w = _rescale(w, off)
        r = minimize(penalty, w, args=(des, delta, True, 1e-3), jac=True, method='L-BFGS-B',
                     bounds=bounds, options={'maxiter': iters})
        w = r.x
        r2 = minimize(penalty, w, args=(des, delta, False, 0.0), jac=True, method='L-BFGS-B',
                      bounds=bounds, options={'maxiter': iters})
        if r2.fun < best[0]:
            best = (float(r2.fun), r2.x)
        if r2.fun < 1e-20:
            return r2.x, True
    return best[1], False


def _rescale(w, step):
    """widen the side by `step` and blow the configuration up about the origin."""
    s = float(w[G.S_IDX])
    lam = (s + step) / s
    w = np.array(w, float)
    for i in range(G.N):
        w[3 * i] *= lam
        w[3 * i + 1] *= lam
    w[G.NV:] *= lam
    w[G.S_IDX] = s + step
    return w


def restore(w0, des, delta, smax=9.0, margin=1e-6, max_outer=12):
    """Phase-1: maximise t subject to (all rows) >= t, t <= margin, with the SAT axis selection
    refreshed each outer round.  The start is feasible for the phase-1 problem for t small enough,
    so SLSQP can always begin; it returns a STRICTLY feasible point when t reaches margin."""
    w = np.array(w0, float)
    NW = len(w)
    obj = np.zeros(NW + 1)
    obj[NW] = -1.0
    bounds = [(None, None)] * NW + [(None, margin)]
    bounds[G.S_IDX] = (2.5, smax)
    t = float(min(rows_all(w, G.best_selection(w[:G.NV])[0], des, delta)[0].min(), 0.0)) - 1e-3
    x = np.concatenate([w, [t]])
    for _ in range(max_outer):
        sel, _ = G.best_selection(x[:G.NV])

        def cons(y):
            return rows_all(y[:NW], sel, des, delta)[0] - y[NW]

        def jcons(y):
            J = rows_all(y[:NW], sel, des, delta)[1]
            return np.hstack([J, -np.ones((J.shape[0], 1))])

        r = minimize(lambda y: -y[NW], x, jac=lambda y: obj, method='SLSQP', bounds=bounds,
                     constraints=[{'type': 'ineq', 'fun': cons, 'jac': jcons}],
                     options={'maxiter': 200, 'ftol': 1e-12})
        x = np.array(r.x, float)
        x[:G.NV] = G.wrap_theta(x[:G.NV])
        g = rows_all(x[:NW], G.best_selection(x[:G.NV])[0], des, delta)[0]
        if g.min() >= 0.0:
            return x[:NW], True, float(g.min())
        x[NW] = min(float(g.min()), margin) - 1e-9
    return x[:NW], False, float(g.min())


def local_opt(w0, des, delta, max_outer=40, ftol=1e-14, tol_step=1e-9, smax=9.0, verbose=False,
              tmin=None):
    """tmin (radians): if given, every DESIGNATED meeter's tilt is confined to
    [tmin, pi/2 - tmin] -- the tilt floor, A217's no-settled-corner constraint generalised to the
    twelve cells."""
    w = np.array(w0, float)
    w[:G.NV] = G.wrap_theta(w[:G.NV])
    NW = len(w)
    e = np.zeros(NW)
    e[G.S_IDX] = 1.0
    hist = []
    sel = None
    floored = sorted({i for _, i in des}) if tmin is not None else []
    for i in floored:
        w[3 * i + 2] = min(max(w[3 * i + 2], tmin), PI2 - tmin)
    for outer in range(max_outer):
        sel, _ = G.best_selection(w[:G.NV])
        bounds = [(None, None)] * NW
        bounds[G.S_IDX] = (2.5, smax)
        for i in floored:
            bounds[3 * i + 2] = (tmin, PI2 - tmin)
        r = minimize(lambda x: x[G.S_IDX], w, jac=lambda x: e, method='SLSQP', bounds=bounds,
                     constraints=[{'type': 'ineq',
                                   'fun': lambda x: rows_all(x, sel, des, delta)[0],
                                   'jac': lambda x: rows_all(x, sel, des, delta)[1]}],
                     options={'maxiter': 250, 'ftol': ftol})
        wn = np.array(r.x, float)
        wn[:G.NV] = G.wrap_theta(wn[:G.NV])
        sel2, _ = G.best_selection(wn[:G.NV])
        step = max(np.abs(wn[:33:3] - w[:33:3]).max(), np.abs(wn[1:33:3] - w[1:33:3]).max(),
                   abs(wn[G.S_IDX] - w[G.S_IDX]),
                   max(G.axis_dev(a - b) for a, b in zip(wn[2:33:3], w[2:33:3])))
        hist.append((outer, float(wn[G.S_IDX]), float(step), int(r.status)))
        if verbose:
            print(outer, wn[G.S_IDX], step, r.status, flush=True)
        w = wn
        if sel2 == sel and step < tol_step:
            break
    return w, hist


def quality(w, des, delta):
    """feasibility residuals of the final point (all rows are written g >= 0)."""
    z = w[:G.NV]
    sel, _ = G.best_selection(z)
    gw = G.wall_rows(z)[0]
    gp = G.pair_rows(z, sel)[0]
    gc = W.crowd_rows(w, des, delta)[0]
    return {'min_wall_gap': float(gw.min()), 'min_pair_gap': float(min(G.pair_gaps(z).values())),
            'min_pair_row': float(gp.min()), 'min_crowd_row': float(gc.min())}


def fj(w, des, delta, tmin=None):
    """A217's Fritz-John residual at the pose part, with the ACTIVE crowd rows added as
    external (artificial) rows -- as in A217's crowd runs."""
    z = w[:G.NV]
    labels, A = W.active_crowd(w, des, delta)
    res, lam, rows = O.fj_residual(z, tmin=tmin, extra_active=(labels, A))
    return {'fj_res': float(res), 'n_rows': len(rows),
            'n_crowd_active': sum(r['kind'] == 'crowd' for r in rows),
            'crowd_lam_sum': float(sum(l for r, l in zip(rows, lam) if r['kind'] == 'crowd')),
            'n_wall_rows': sum(r['kind'] == 'wall' for r in rows),
            'n_edge_rows': sum(r['kind'] == 'edge' for r in rows)}


def fj_free(z, tmin=None):
    """the FREE FJ residual (no crowd rows): 0 means the packing is a genuine FJ point."""
    res, lam, rows = O.fj_residual(np.asarray(z, float)[:G.NV], tmin=tmin)
    loaded = set()
    for r, l in zip(rows, lam):
        if l > 1e-9:
            loaded.add(r['i'])
            if 'j' in r:
                loaded.add(r['j'])
    return {'fj_free_res': float(res), 'fj_free_rows': len(rows), 'loaded': sorted(loaded)}
