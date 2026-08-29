#!/usr/bin/env python
"""a44_geom.py -- float64 geometry + row language for A44.

Row language is EXACTLY A37's (a37_pipeline.row_jet):

  wall row  {'kind':'wall','i','corner','wall'}   g = corner coord (or s - coord)
  edge row  {'kind':'edge','i'=other,'corner','j'=owner,'edge'}
                                                  g = n_e(th_j).(q_corner(i) - c_j) - 1/2
  dist row  {'kind':'dist','i','j'}               g = |c_i - c_j|^2 - 1     (NOT used
                                                  in the A44 physical count)

Coordinate layout (A22 / A37):  z[3i] = cx_i, z[3i+1] = cy_i, z[3i+2] = theta_i
(RADIANS -- NOT tan(theta/2); the A44 brief's "t = tan(theta/2)" is wrong, see
eval_report.md conventions section), z[33] = s.

All gradients here are analytic float64.  They are cross-checked against
a37_pipeline.jac_at (mpmath interval jets, dps 60) by eval_atlas.py's self-check.
"""
from __future__ import annotations

import math

import numpy as np

NSQ = 11
NV = 34
S_IDX = 33
HALF = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
NHAT = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')


def corner(z, i, k):
    cx, cy, th = z[3 * i], z[3 * i + 1], z[3 * i + 2]
    hx, hy = HALF[k]
    c, s = math.cos(th), math.sin(th)
    return (cx + c * hx - s * hy, cy + s * hx + c * hy)


def dcorner_dth(z, i, k):
    th = z[3 * i + 2]
    hx, hy = HALF[k]
    c, s = math.cos(th), math.sin(th)
    return (-s * hx - c * hy, c * hx - s * hy)


def normal(z, j, e):
    th = z[3 * j + 2]
    nhx, nhy = NHAT[e]
    c, s = math.cos(th), math.sin(th)
    return (c * nhx - s * nhy, s * nhx + c * nhy)


def dnormal_dth(z, j, e):
    th = z[3 * j + 2]
    nhx, nhy = NHAT[e]
    c, s = math.cos(th), math.sin(th)
    return (-s * nhx - c * nhy, c * nhx - s * nhy)


# ------------------------------------------------------------------ row value
def row_value(z, c):
    if c['kind'] == 'wall':
        qx, qy = corner(z, c['i'], c['corner'])
        w = c['wall']
        if w == 'x=0':
            return qx
        if w == 'y=0':
            return qy
        if w == 'x=s':
            return z[S_IDX] - qx
        if w == 'y=s':
            return z[S_IDX] - qy
        raise ValueError(w)
    if c['kind'] == 'edge':
        qx, qy = corner(z, c['i'], c['corner'])
        nx, ny = normal(z, c['j'], c['edge'])
        return nx * (qx - z[3 * c['j']]) + ny * (qy - z[3 * c['j'] + 1]) - 0.5
    if c['kind'] == 'dist':
        dx = z[3 * c['i']] - z[3 * c['j']]
        dy = z[3 * c['i'] + 1] - z[3 * c['j'] + 1]
        return dx * dx + dy * dy - 1.0
    raise ValueError(c['kind'])


def row_grad(z, c):
    """Analytic float64 gradient, returned as a dense length-34 vector."""
    g = np.zeros(NV)
    if c['kind'] == 'wall':
        i, k, w = c['i'], c['corner'], c['wall']
        dqx, dqy = dcorner_dth(z, i, k)
        if w == 'x=0':
            g[3 * i] = 1.0
            g[3 * i + 2] = dqx
        elif w == 'y=0':
            g[3 * i + 1] = 1.0
            g[3 * i + 2] = dqy
        elif w == 'x=s':
            g[S_IDX] = 1.0
            g[3 * i] = -1.0
            g[3 * i + 2] = -dqx
        elif w == 'y=s':
            g[S_IDX] = 1.0
            g[3 * i + 1] = -1.0
            g[3 * i + 2] = -dqy
        else:
            raise ValueError(w)
        return g
    if c['kind'] == 'edge':
        i, k, j, e = c['i'], c['corner'], c['j'], c['edge']
        qx, qy = corner(z, i, k)
        nx, ny = normal(z, j, e)
        dqx, dqy = dcorner_dth(z, i, k)
        dnx, dny = dnormal_dth(z, j, e)
        g[3 * i] += nx
        g[3 * i + 1] += ny
        g[3 * i + 2] += nx * dqx + ny * dqy
        g[3 * j] += -nx
        g[3 * j + 1] += -ny
        g[3 * j + 2] += dnx * (qx - z[3 * j]) + dny * (qy - z[3 * j + 1])
        return g
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        g[3 * i] = 2 * dx
        g[3 * i + 1] = 2 * dy
        g[3 * j] = -2 * dx
        g[3 * j + 1] = -2 * dy
        return g
    raise ValueError(c['kind'])


# ------------------------------------------------------------- gap spectra
def wall_gaps(z):
    """All 11*4*4 = 176 corner-wall clearances.  key (i, corner, wall)."""
    out = {}
    for i in range(NSQ):
        for k in range(4):
            for w in WALLS:
                out[(i, k, w)] = row_value(z, {'kind': 'wall', 'i': i,
                                               'corner': k, 'wall': w})
    return out


def pair_axes(z, i, j):
    """The 8 SAT axes of pair (i, j) with per-corner projections."""
    axes = []
    for o, p in ((i, j), (j, i)):
        for e in range(4):
            nx, ny = normal(z, o, e)
            proj = []
            for k in range(4):
                qx, qy = corner(z, p, k)
                proj.append(nx * (qx - z[3 * o]) + ny * (qy - z[3 * o + 1])
                            - 0.5)
            axes.append({'o': o, 'p': p, 'e': e, 'proj': proj,
                         'gap': min(proj)})
    return axes


def pair_gaps(z):
    """All 55 pair SAT gaps (max over the 8 axes).  key (i, j), i < j."""
    out = {}
    for i in range(NSQ):
        for j in range(i + 1, NSQ):
            out[(i, j)] = max(a['gap'] for a in pair_axes(z, i, j))
    return out


def sep_t(z, o, e, p, k):
    """Tangential coordinate of corner k of p in the frame of edge e of o."""
    qx, qy = corner(z, p, k)
    nx, ny = normal(z, o, e)
    wx, wy = qx - z[3 * o], qy - z[3 * o + 1]
    return -ny * wx + nx * wy
