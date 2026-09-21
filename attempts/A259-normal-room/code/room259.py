"""A259 room of a normal ring, by the exact per-tilt CENTRE SET (A222 / A237's configuration space):
    C(theta) = {q : q + Q_theta inside [0,s]^2 minus the eight ring squares}
             = [h, s-h]^2  minus  U_i (member_i (+) Q_theta),      h = (cos + sin)/2.
PIERCE(1) by the container centre O  <=>  for every theta, C(theta) inside O + int Q_theta  (Q symmetric)
    <=>  G(theta) := max over the vertices of C(theta) of max(|(q-O).u|, |(q-O).v|)  <  1/2   (a convex function on a
    polygon is maximal at a vertex).   pierce_O(x, s) returns max_theta G - 1/2  (< 0: every sampled-tilt free square
    contains O) with the worst witness pose.  This is a MEASUREMENT on a tilt grid ([M]); the box-valid form is cert259.
"""
import math
import sys
import os

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom259 as Z                                                   # noqa: E402

DEG = math.pi / 180.0


def polys_of(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g] if g.area > 1e-14 else []
    return [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon' and p.area > 1e-14]


def centre_set(Vs, s, th, half=0.5):
    """C(theta) for the square of half-side `half` and tilt th against the member vertex arrays Vs."""
    h = half * (abs(math.cos(th)) + abs(math.sin(th)))
    if s - 2 * h <= 0:
        return Polygon()
    q0 = Z.sq_verts(0.0, 0.0, th, half)
    sums = [Polygon([(a[0] + b[0], a[1] + b[1]) for a in V for b in q0]).convex_hull for V in Vs]
    return sbox(h, h, s - h, s - h).difference(unary_union(sums))


def gmax(C, s, th):
    """(G, q): the largest max(|(q-O).u|, |(q-O).v|) over C's vertices and where."""
    u = np.array([math.cos(th), math.sin(th)])
    v = np.array([-math.sin(th), math.cos(th)])
    O = np.array([s / 2, s / 2])
    best, arg = -1.0, None
    for P in polys_of(C):
        for ring in [P.exterior] + list(P.interiors):
            A = np.array(ring.coords)[:-1] - O
            g = np.maximum(np.abs(A @ u), np.abs(A @ v))
            i = int(g.argmax())
            if g[i] > best:
                best, arg = float(g[i]), (float(A[i, 0] + O[0]), float(A[i, 1] + O[1]))
    return best, arg


def pierce_O(x, s, step_deg=1.0, Vs=None):
    Vs = Z.ring_verts(x, s) if Vs is None else Vs
    worst, pose, ncomp = -1.0, None, 0
    th = 0.0
    while th < 90.0 - 1e-9:
        C = centre_set(Vs, s, th * DEG)
        ps = polys_of(C)
        ncomp = max(ncomp, len(ps))
        if ps:
            g, q = gmax(C, s, th * DEG)
            if g > worst:
                worst, pose = g, (q[0], q[1], th * DEG)
        th += step_deg
    return worst - 0.5, pose, ncomp


def free_margin(pose, Vs, s):
    """exact-geometry check of one free square: min(containment, SAT gaps to the ring)."""
    V = Z.sq_verts(*pose)
    m = Z.contain_margin(V, s)
    for W in Vs:
        m = min(m, Z.poly_gap(V, W))
    return m


def contains_O(pose, s):
    th = pose[2]
    d = np.array([s / 2 - pose[0], s / 2 - pose[1]])
    return 0.5 - max(abs(d @ np.array([math.cos(th), math.sin(th)])), abs(d @ np.array([-math.sin(th), math.cos(th)])))


if __name__ == '__main__':
    s = Z.SHAT
    for deg in (2, 6, 10, 14.545, 20, 25, 30):
        lo, hi = Z.delta_range_c4(deg * DEG, s)
        for d in (lo + 1e-4, 0.5 * (lo + hi), hi - 1e-4):
            x = Z.c4(d, deg * DEG)
            m = Z.ring_margin(x, s)
            w, pose, nc = pierce_O(x, s, 1.0)
            print('phi %6.3f delta %.4f ringmargin %+.5f pierceO %+.5f comps %d pose %s' %
                  (deg, d, m, w, nc, None if pose is None else tuple(round(t, 4) for t in pose)))
