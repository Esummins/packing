"""A255 geometry: the n-general border-cell system (A254 s.1.1), the SENSE of a square, wall
touching, the corner's LOCAL neighbourhood and its admissible families (Lemma CELLS test).

SENSE (the brief's "tilt mod 90 measured the same way round the perimeter").  The perimeter frames
of the four walls differ by quarter turns, and a quarter turn fixes a square's tilt mod 90; so the
perimeter-consistent sense is simply the sign of the GLOBAL tilt
    phi(Q) := ((theta + 45) mod 90) - 45  in (-45, 45] degrees,
sense +1 (phi > 0, "CCW"), -1 (phi < 0, "CW"), 0 (flat, |phi| <= FLAT_DEG).  A C4 / C2 pinwheel has
ONE sense; a reflection of the container flips every sense.  |phi| = 45 has no sense (flagged 'X').

CELLS, n-general: m := ceil(s) (s in (m-1, m]); the four boxes c00 and per corner c and per wall of c
the chain cells L_j = [j, j+1] x [0, 1] (wall coordinate from c), j = 1 .. m-3.  For m = 4 these are
A244's twelve (c01 = chain 'v' cell 1 up the corner's vertical wall, c10 = chain 'h' cell 1).
Cell key: (corner, kind, j), kind in {'00', 'v', 'h'}.
LOCAL NEIGHBOURHOOD N_c: c00, c's two chains, and the FACING chains of c's two walls (the cells of the
adjacent corners running towards c) -- for m = 4 the five-cell neighbourhood of PROJECTION (A247).
"""
import itertools
import math

import numpy as np

CORNERS = ('BL', 'BR', 'TR', 'TL')
FLAT_DEG = 0.05            # |phi| below this is FLAT (corpus flats are < 0.01 deg; tilt-bounded runs >= 5 deg)
TOUCH = 1e-6               # wall-touch tolerance
MEET = 1e-9                # a square MEETS a cell iff SAT depth > MEET
# the adjacent corner along c's vertical wall / horizontal wall
ADJ_V = {'BL': 'TL', 'TL': 'BL', 'BR': 'TR', 'TR': 'BR'}
ADJ_H = {'BL': 'BR', 'BR': 'BL', 'TL': 'TR', 'TR': 'TL'}
WALL_V = {'BL': 'x0', 'TL': 'x0', 'BR': 'x1', 'TR': 'x1'}
WALL_H = {'BL': 'y0', 'BR': 'y0', 'TL': 'y1', 'TR': 'y1'}


def m_of(s):
    return int(math.ceil(s - 1e-12))


def cell_rect(key, s):
    c, kind, j = key
    if kind == '00':
        u0, u1, v0, v1 = 0.0, 1.0, 0.0, 1.0
    elif kind == 'v':
        u0, u1, v0, v1 = 0.0, 1.0, float(j), j + 1.0
    else:
        u0, u1, v0, v1 = float(j), j + 1.0, 0.0, 1.0
    x0, x1 = (u0, u1) if c in ('BL', 'TL') else (s - u1, s - u0)
    y0, y1 = (v0, v1) if c in ('BL', 'BR') else (s - v1, s - v0)
    return (x0, x1, y0, y1)


def cell_name(key):
    c, kind, j = key
    if kind == '00':
        return c + '00'
    return '%s%s' % (c, ('0%d' % j) if kind == 'v' else ('%d0' % j))


def all_cells(s):
    m = m_of(s)
    out = [(c, '00', 0) for c in CORNERS]
    for c in CORNERS:
        for kind in ('v', 'h'):
            out += [(c, kind, j) for j in range(1, m - 2)]
    return out


def neighbourhood(c, s):
    m = m_of(s)
    out = [(c, '00', 0)]
    for j in range(1, m - 2):
        out += [(c, 'v', j), (c, 'h', j), (ADJ_V[c], 'v', j), (ADJ_H[c], 'h', j)]
    return out


def corners_of(cx, cy, th):
    c, sn = math.cos(th), math.sin(th)
    return np.array([[cx + 0.5 * (a * c - b * sn), cy + 0.5 * (a * sn + b * c)]
                     for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def depth(cx, cy, th, R):
    """SAT overlap depth of the square with the axis rectangle R = (x0, x1, y0, y1); > 0 iff interiors meet."""
    V = corners_of(cx, cy, th)
    P = np.array([[R[0], R[2]], [R[1], R[2]], [R[1], R[3]], [R[0], R[3]]])
    c, sn = math.cos(th), math.sin(th)
    best = float('inf')
    for ax in ((1.0, 0.0), (0.0, 1.0), (c, sn), (-sn, c)):
        a = np.array(ax)
        pv, pp = V @ a, P @ a
        best = min(best, min(pv.max(), pp.max()) - max(pv.min(), pp.min()))
    return best


def overlap_rects(a, b):
    return min(min(a[1], b[1]) - max(a[0], b[0]), min(a[3], b[3]) - max(a[2], b[2]))


def phi_deg(th):
    return ((math.degrees(th) + 45.0) % 90.0) - 45.0


def sense(th):
    p = phi_deg(th)
    if abs(abs(p) - 45.0) < FLAT_DEG:
        return 'X'
    if abs(p) <= FLAT_DEG:
        return 0
    return 1 if p > 0 else -1


def touches(cx, cy, th, s, tol=TOUCH):
    V = corners_of(cx, cy, th)
    out = set()
    if V[:, 0].min() < tol:
        out.add('x0')
    if V[:, 0].max() > s - tol:
        out.add('x1')
    if V[:, 1].min() < tol:
        out.add('y0')
    if V[:, 1].max() > s - tol:
        out.add('y1')
    return out


def poses_of_z(z, n=None):
    n = n if n is not None else (len(z) - 1) // 3
    return [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(n)]


def pose_of_poly(V):
    V = np.asarray(V, float)
    e = V[1] - V[0]
    return (float(V[:, 0].mean()), float(V[:, 1].mean()), math.atan2(e[1], e[0]) % (math.pi / 2))


def meeter_table(poses, s, cells, tol=MEET):
    return {k: [i for i, p in enumerate(poses) if depth(p[0], p[1], p[2], cell_rect(k, s)) > tol] for k in cells}


def scope_cells(c, s, level):
    """L0 = N_c; L1 = N_c + the two adjacent corner boxes; L2 = N_c u N_c' u N_c''; L3 = every border cell."""
    if level == 0:
        return neighbourhood(c, s)
    if level == 1:
        return neighbourhood(c, s) + [(ADJ_V[c], '00', 0), (ADJ_H[c], '00', 0)]
    if level == 2:
        out = []
        for d in (c, ADJ_V[c], ADJ_H[c]):
            out += [k for k in neighbourhood(d, s) if k not in out]
        return out
    return all_cells(s)


def smallest_reducing(cells, s, table):
    """the smallest family Pi of pairwise interior-disjoint cells among `cells` with |M(Pi)| <= |Pi|
    (Lemma CELLS applies), or None: DFS over the independent sets of the conflict graph, bitmask unions."""
    n = len(cells)
    rects = [cell_rect(k, s) for k in cells]
    conf = [0] * n
    for i, j in itertools.combinations(range(n), 2):
        if overlap_rects(rects[i], rects[j]) > 1e-12:
            conf[i] |= 1 << j
            conf[j] |= 1 << i
    mm = [sum(1 << q for q in table[k]) for k in cells]
    best = [None]

    def rec(start, chosen, banned, union):
        size = len(chosen)
        if size and bin(union).count('1') <= size and (best[0] is None or size < len(best[0][0])):
            best[0] = (tuple(chosen), union)
        if best[0] is not None and size + 1 >= len(best[0][0]):
            return
        for i in range(start, n):
            if not (banned >> i) & 1:
                rec(i + 1, chosen + [i], banned | conf[i], union | mm[i])

    rec(0, [], 0, 0)
    if best[0] is None:
        return None
    fam, union = best[0]
    return [cell_name(cells[i]) for i in fam], [q for q in range(union.bit_length()) if (union >> q) & 1]
