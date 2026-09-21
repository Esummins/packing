"""A262: rings with SEVERAL JAM corners.  jam = tuple of walls whose END square is replaced by a FLOATER (wall w's END
corner is corner (w+1) % 4; corner k = the START corner of wall k; corner 0 = BL).  Every wall keeps its START square.
Parameters p = (delta_0..3, phi_0..3) + for each JAM wall (in the order of `jam`) the floater's pose (cx, cy, th) in
the LOCAL frame of its corner (the frame in which that corner is BL) -- so A261's witness C can be copied verbatim.
Squares in order: per wall its START (+ END if the wall is a row), then the floaters.
"""
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
Z = G.Z


def verts(p, s, jam):
    Vs, wall, role = [], [], []
    for k in range(4):
        row = Z.row_verts(p[k], p[4 + k], s, k)
        Vs.append(row[0]); wall.append(k); role.append('S%d' % k)
        if k not in jam:
            Vs.append(row[1]); wall.append(k); role.append('E%d' % k)
    for i, w in enumerate(jam):
        c = p[8 + 3 * i: 11 + 3 * i]
        Vs.append(Z.rot_k(Z.sq_verts(c[0], c[1], c[2]), s, (w + 1) % 4)); wall.append(None); role.append('C%d' % w)
    return Vs, wall, role


def local_triple(Vs, role, s, w):
    """(C, A, X) of the JAM corner of wall w, rotated into the BL frame (for jam261.J_of)."""
    k = (w + 1) % 4
    back = (4 - k) % 4
    get = lambda name: Z.rot_k(Vs[role.index(name)], s, back)
    return [get('C%d' % w), get('S%d' % k), get('S%d' % w)]


def terms(p, s, jam):
    Vs, wall, role = verts(p, s, jam)
    n = len(Vs)
    t = [G.contain_far(V, s, wall[i]) for i, V in enumerate(Vs)]
    for i in range(n):
        for j in range(i):
            if not (wall[i] is not None and wall[i] == wall[j]):
                t.append(Z.poly_gap(Vs[i], Vs[j]))
    for k in range(4):
        t += [p[4 + k], 45 * Z.DEG - p[4 + k], 1.0 - p[k]]
        if k not in jam:
            t.append(p[k] + Z.span(p[4 + k]) - (s - 1.0))
    for w in jam:
        C = local_triple(Vs, role, s, w)[0]
        t += [G.depth_in_box(C), float(C[:, 0].min()), float(C[:, 1].min())]
    return t, Vs, role


def objective(p, s, jam):
    t, Vs, role = terms(p, s, jam)
    m = float(min(t))
    if m < -0.05:
        return m
    import jam261 as J
    for w in jam:
        m = min(m, -J.J_of(local_triple(Vs, role, s, w))[0])
    return m


def start_from_witness(pA, pC, pX, s, jam):
    """every JAM corner gets the witness triple; the remaining rows: delta 0.8, the witness tilt of A."""
    a_th, x_th = pA[2], pX[2]
    dA = pA[0] - 0.5 * (math.cos(a_th) + math.sin(a_th))
    dX = s - (pX[1] + 0.5 * (math.cos(x_th) + math.sin(x_th)))
    d, f = [0.8] * 4, [a_th] * 4
    for w in jam:
        d[w], f[w] = dX, x_th
    for w in jam:
        k = (w + 1) % 4
        if k not in jam:
            d[k], f[k] = dA, a_th
    return np.array(d + f + [v for _ in jam for v in pC], float)
