"""m4_geom.py -- A35 / M4: FAST float64 geometry for escape-route following.

[NUM] throughout.  Rigour is M2's job; this module is the float path-following
engine.  Conventions are IDENTICAL to a22lib / t3lib / strata_lib:

    z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=theta_i (i=0..10), z[33]=s, NV=34.
    HALF[k] = body-frame corner k,  NHAT[e] = body-frame outward normal of
    edge e (edge e joins corner e -> e+1).

Rows are the same three kinds as A22: 'wall', 'edge', 'dist'.  The SAT gap of
a pair is computed in EXACTLY the same row language as t3lib.pair_sep_iv:

    gap(i,j) = max over owner o in {i,j}, edge e of o, of
                 [ min over corners k of the other square p of
                     n_e(theta_o) . (q_k(p) - c_o) - 1/2 ]

which equals max over the 4 SAT axes of max(lo_p - hi_o, lo_o - hi_p).
The argmax (o,e) and argmin k identify the smooth 'edge' row that realises the
gap, so the gap gradient is the a22 'edge'-row gradient of that triple.

Validated against strata_lib / t3lib mpmath.iv values at z-hat (see selfcheck()).
"""
from __future__ import annotations

import numpy as np

NV = 34
NSQ = 11
S_IDX = 33

HALF = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])
NHAT = np.array([[0.0, -1.0], [1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')

ALL_PAIRS = [(i, j) for i in range(NSQ) for j in range(i + 1, NSQ)]   # 55


# --------------------------------------------------------------- basic frames

def unpack(z):
    C = np.empty((NSQ, 2))
    C[:, 0] = z[0:33:3]
    C[:, 1] = z[1:33:3]
    th = z[2:33:3]
    return C, th


def corners(z):
    """Q[i,k,:] = world position of corner k of square i."""
    C, th = unpack(z)
    c, s = np.cos(th), np.sin(th)
    R = np.empty((NSQ, 2, 2))
    R[:, 0, 0] = c; R[:, 0, 1] = -s
    R[:, 1, 0] = s; R[:, 1, 1] = c
    return C[:, None, :] + np.einsum('iab,kb->ika', R, HALF)


def normals(z):
    """N[i,e,:] = world outward normal of edge e of square i."""
    _, th = unpack(z)
    c, s = np.cos(th), np.sin(th)
    R = np.empty((NSQ, 2, 2))
    R[:, 0, 0] = c; R[:, 0, 1] = -s
    R[:, 1, 0] = s; R[:, 1, 1] = c
    return np.einsum('iab,eb->iea', R, NHAT)


# ------------------------------------------------------------------- row eval

_SAT_CACHE = {}


def sat_cached(z):
    key = z.tobytes()
    hit = _SAT_CACHE.get(key)
    if hit is None:
        if len(_SAT_CACHE) > 8:
            _SAT_CACHE.clear()
        hit = sat_all(z)
        _SAT_CACHE[key] = hit
    return hit


def row_val(z, c):
    k = c['kind']
    if k == 'sat':
        gap, _ = sat_cached(z)
        return float(gap[c['i'], c['j']])
    if k == 'wall':
        i, cn, w = c['i'], c['corner'], c['wall']
        th = z[3 * i + 2]
        co, si = np.cos(th), np.sin(th)
        hx, hy = HALF[cn]
        qx = z[3 * i] + co * hx - si * hy
        qy = z[3 * i + 1] + si * hx + co * hy
        if w == 'x=0':
            return qx
        if w == 'y=0':
            return qy
        if w == 'x=s':
            return z[S_IDX] - qx
        return z[S_IDX] - qy
    if k == 'edge':
        i, j, cn, e = c['i'], c['j'], c['corner'], c['edge']
        thi, thj = z[3 * i + 2], z[3 * j + 2]
        ci, si_ = np.cos(thi), np.sin(thi)
        hx, hy = HALF[cn]
        qx = z[3 * i] + ci * hx - si_ * hy
        qy = z[3 * i + 1] + si_ * hx + ci * hy
        cj, sj = np.cos(thj), np.sin(thj)
        nhx, nhy = NHAT[e]
        nx = cj * nhx - sj * nhy
        ny = sj * nhx + cj * nhy
        return nx * (qx - z[3 * j]) + ny * (qy - z[3 * j + 1]) - 0.5
    if k == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - 1.0
    raise ValueError(k)


def row_grad(z, c, out=None):
    g = np.zeros(NV) if out is None else out
    k = c['kind']
    if k == 'sat':
        i, j = c['i'], c['j']
        _, wit = sat_cached(z)
        o, e, kk = sat_pair_witness(wit, i, j)
        p = j if o == i else i
        return row_grad(z, {'kind': 'edge', 'i': p, 'j': o,
                            'corner': kk, 'edge': e}, out=g)
    if k == 'wall':
        i, cn, w = c['i'], c['corner'], c['wall']
        th = z[3 * i + 2]
        co, si = np.cos(th), np.sin(th)
        hx, hy = HALF[cn]
        dqx = -si * hx - co * hy
        dqy = co * hx - si * hy
        if w == 'x=0':
            g[3 * i] = 1.0; g[3 * i + 2] = dqx
        elif w == 'y=0':
            g[3 * i + 1] = 1.0; g[3 * i + 2] = dqy
        elif w == 'x=s':
            g[3 * i] = -1.0; g[3 * i + 2] = -dqx; g[S_IDX] = 1.0
        else:
            g[3 * i + 1] = -1.0; g[3 * i + 2] = -dqy; g[S_IDX] = 1.0
        return g
    if k == 'edge':
        i, j, cn, e = c['i'], c['j'], c['corner'], c['edge']
        thi, thj = z[3 * i + 2], z[3 * j + 2]
        ci, si_ = np.cos(thi), np.sin(thi)
        cj, sj = np.cos(thj), np.sin(thj)
        hx, hy = HALF[cn]
        nhx, nhy = NHAT[e]
        nx = cj * nhx - sj * nhy
        ny = sj * nhx + cj * nhy
        qx = z[3 * i] + ci * hx - si_ * hy
        qy = z[3 * i + 1] + si_ * hx + ci * hy
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx = -si_ * hx - ci * hy
        dhy = ci * hx - si_ * hy
        dnx = -sj * nhx - cj * nhy
        dny = cj * nhx - sj * nhy
        g[3 * i] = nx; g[3 * i + 1] = ny
        g[3 * j] = -nx; g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if k == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        g[3 * i] = 2 * dx; g[3 * i + 1] = 2 * dy
        g[3 * j] = -2 * dx; g[3 * j + 1] = -2 * dy
        return g
    raise ValueError(k)


def rows_val(z, cons):
    return np.array([row_val(z, c) for c in cons])


def rows_jac(z, cons):
    A = np.zeros((len(cons), NV))
    for k, c in enumerate(cons):
        row_grad(z, c, out=A[k])
    return A


# ------------------------------------------------------------------ SAT gaps

def sat_all(z):
    """(gapmat, witness) for all 11x11 ordered owner/probe combinations.

    gap[i,j] = gap[j,i] = SAT separation of squares i and j (float).
    witness[i][j] = (owner, edge, corner) realising it.
    """
    Q = corners(z)                      # (11,4,2)
    C, _ = unpack(z)
    N = normals(z)                      # (11,4,2)
    # W[o,p,k,:] = q_k(p) - c_o
    W = Q[None, :, :, :] - C[:, None, None, :]
    P = np.einsum('oea,opka->oepk', N, W) - 0.5       # (11,4,11,4)
    kmin = P.argmin(axis=3)                            # (11,4,11)
    Pmin = np.take_along_axis(P, kmin[:, :, :, None], axis=3)[:, :, :, 0]
    emax = Pmin.argmax(axis=1)                         # (11,11) best edge per (o,p)
    Pbest = np.take_along_axis(Pmin, emax[:, None, :], axis=1)[:, 0, :]  # (11,11)
    gap = np.maximum(Pbest, Pbest.T)
    return gap, (Pbest, emax, kmin)


def sat_pair_witness(wit, i, j):
    """Return (owner, edge, corner) realising gap(i,j)."""
    Pbest, emax, kmin = wit
    if Pbest[i, j] >= Pbest[j, i]:
        o, p = i, j
    else:
        o, p = j, i
    e = int(emax[o, p])
    k = int(kmin[o, e, p])
    return o, e, k


def gained_row(o, e, k, p):
    """The a22 'edge' row whose value equals the SAT gap near this witness."""
    return {'kind': 'edge', 'i': p, 'j': o, 'corner': k, 'edge': e,
            'name': 'G%dc%d-%de%d' % (p, k, o, e)}


def sat_vec(z, pairs):
    gap, _ = sat_all(z)
    return np.array([gap[i, j] for (i, j) in pairs])


# ------------------------------------------------------- containment (176 rows)

def containment_min(z):
    """min over all 11*4 corners of (qx, qy, s-qx, s-qy)."""
    Q = corners(z)
    s = z[S_IDX]
    return float(min(Q[:, :, 0].min(), Q[:, :, 1].min(),
                     (s - Q[:, :, 0]).min(), (s - Q[:, :, 1]).min()))
