"""A281 geometry: corner frames, the two roles per corner (floor toucher A, wall toucher B; th = 0 is the flat),
float SAT margins for the optimiser and EXACT (Fraction) verification of every witness.
Corner c in 0..3 = BL, BR, TR, TL (ccw).  Corner frame (u, v): u along the corner's OUTGOING wall F_c = wall c
(BL: the floor), v along its INCOMING wall W_c = wall c-1 (BL: the left wall x = 0).  A249's parametrisation:
floor toucher A(th, d): vertices V=(d+si,0), V+(co,si), V+(co-si,si+co), (d,co);  wall toucher B(th, d): L=(0,d+co),
V=(si,d), V+(co,si), V+(co-si,si+co).  th = 0 gives the flats [d,1+d]x[0,1] and [0,1]x[d,1+d]."""
import math
from fractions import Fraction

import numpy as np

SHAT = 3.877083590022814
CORNERS = ('BL', 'BR', 'TR', 'TL')


def cs(th):
    return math.cos(th), math.sin(th)


def frame_square(kind, th, d, co=None, si=None):
    """vertices in the corner frame; co/si may be Fractions (exact)."""
    if co is None:
        co, si = cs(th)
    if kind == 'A':
        V = (d + si, 0 * si)
    else:
        V = (si, d)
    return [V, (V[0] + co, V[1] + si), (V[0] + co - si, V[1] + si + co), (V[0] - si, V[1] + co)]


def to_global(P, c, s):
    if c == 0:
        return [(u, v) for u, v in P]
    if c == 1:
        return [(s - v, u) for u, v in P]
    if c == 2:
        return [(s - u, s - v) for u, v in P]
    return [(v, s - u) for u, v in P]


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def gap(P, Q):
    """SAT gap, exact for Fractions / float for floats (unnormalised normals for Fractions)."""
    best = None
    exact = isinstance(P[0][0], Fraction) or isinstance(Q[0][0], Fraction)
    for poly in (P, Q):
        for k in range(4):
            e = (poly[(k + 1) % 4][0] - poly[k][0], poly[(k + 1) % 4][1] - poly[k][1])
            n = (e[1], -e[0])
            if not exact:
                L = math.hypot(*n)
                n = (n[0] / L, n[1] / L)
            a = [p[0] * n[0] + p[1] * n[1] for p in P]
            b = [q[0] * n[0] + q[1] * n[1] for q in Q]
            g = max(min(b) - max(a), min(a) - max(b))
            best = g if best is None or g > best else best
    return best


def meets(P, R):
    """int P meets int R (both convex quadrilaterals) iff SAT gap < 0."""
    return gap(P, R) < 0


def cells(s, c):
    """the three border cells of corner c in GLOBAL coordinates: c00 (box), c01 (wall slot, along W_c), c10 (floor slot)."""
    box = to_global(rect(0, 1, 0, 1), c, s)
    slot_wall = to_global(rect(0, 1, 1, 2), c, s)      # up the incoming wall (v in (1,2), u in (0,1))
    slot_floor = to_global(rect(1, 2, 0, 1), c, s)     # along the outgoing wall
    return {'c00': box, 'c01': slot_wall, 'c10': slot_floor}


def in_container(P, s):
    return all(0 <= p[0] <= s and 0 <= p[1] <= s for p in P)


def rational(x, den=10 ** 7):
    return Fraction(round(x * den), den)


def exact_square(kind, th, d, c, s_frac, den=10 ** 7):
    t = rational(math.tan(th / 2), den)
    co, si = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    return to_global(frame_square(kind, None, rational(d, den), co, si), c, s_frac)


def float_square(kind, th, d, c, s):
    return to_global(frame_square(kind, th, d), c, s)
