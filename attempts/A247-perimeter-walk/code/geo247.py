"""A247: the twelve border cells as a RING, the D4 symmetry on cell names, the corner
neighbourhoods N_c, the free-square windows, and interval enclosures of the SAT overlap depth
of a unit square against a cell whose rectangle depends on the (interval) side s.

Cells (A244 cells244): in corner c's frame (u, v) = distances from its two walls,
c00 = (0,1)^2, c01 = (0,1) x (1,2) up c's VERTICAL wall, c10 = (1,2) x (0,1) along its
HORIZONTAL wall.  Ring order: BL00 BL10 BR10 BR00 BR01 TR01 TR00 TR10 TL10 TL00 TL01 BL01.
The interval arithmetic is A246's interval246 (read-only import): enclosures without directed
rounding, every verdict keeps the guard GUARD = 1e-9 (A246 test246 measured the accumulated
error at ~1e-13 on 15 000 samples; verify247 repeats that test here).
"""
import itertools
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A246-construct-towards', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import interval246 as IV          # noqa: E402
import cells244 as C              # noqa: E402

GUARD = IV.GUARD
SHAT = 3.877084
S_LO = 3.82
RING = ('BL00', 'BL10', 'BR10', 'BR00', 'BR01', 'TR01', 'TR00', 'TR10', 'TL10', 'TL00', 'TL01', 'BL01')
SLOT_RING = tuple(c for c in RING if not c.endswith('00'))     # 8 slots in ring order
CORNERS = ('BL', 'BR', 'TR', 'TL')
BOXES = tuple('%s00' % c for c in CORNERS)
# N_c: the five ring cells centred at c00 (the far slot of each of c's walls included)
NBR = {c: tuple(RING[(RING.index('%s00' % c) + k) % 12] for k in (-2, -1, 0, 1, 2)) for c in CORNERS}
SLOTS_OF = {c: tuple(x for x in NBR[c] if not x.endswith('00')) for c in CORNERS}   # 4 slots around c
WINDOWS = {c: SLOTS_OF[c] for c in CORNERS}                                            # free-square windows


# ---------------------------------------------------------------- rectangles (interval side)
def rect_coeffs(name):
    """cell rectangle as (a0, b0, a1, b1, c0, d0, c1, d1): x0 = a0 + b0 s, x1 = a1 + b1 s, ..."""
    c, k = name[:2], name[2:]
    u0, u1, v0, v1 = C.BOX[k]
    if c in ('BL', 'TL'):
        X = (u0, 0, u1, 0)
    else:
        X = (-u1, 1, -u0, 1)
    if c in ('BL', 'BR'):
        Y = (v0, 0, v1, 0)
    else:
        Y = (-v1, 1, -v0, 1)
    return X + Y


def rect_at(name, s):
    a0, b0, a1, b1, c0, d0, c1, d1 = rect_coeffs(name)
    return (a0 + b0 * s, a1 + b1 * s, c0 + d0 * s, c1 + d1 * s)


def rect_i(name, s):
    """the four interval endpoints of the cell at the interval side s = (lo, hi) arrays."""
    a0, b0, a1, b1, c0, d0, c1, d1 = rect_coeffs(name)
    one = np.ones_like(s[0])

    def lin(a, b):
        return IV.add(IV.I(a * one), IV.scale(s, b)) if b else IV.I(a * one)
    return lin(a0, b0), lin(a1, b1), lin(c0, d0), lin(c1, d1)


def proj_rect_i(R, n):
    x0, x1, y0, y1 = R
    pts = [IV.add(IV.mul(n[0], X), IV.mul(n[1], Y)) for X in (x0, x1) for Y in (y0, y1)]
    return IV.hull(*pts)


def depth_cell_loose(pose, R):
    """A246-style enclosure (independent cos/sin intervals) -- kept as the cross-check of enc247."""
    cx, cy, th = pose
    hw = IV.scale(IV.add(IV.cos_i(th), IV.sin_i(th)), 0.5)
    ox = IV.overlap((IV.sub(cx, hw), IV.add(cx, hw)), (R[0], R[1]))
    oy = IV.overlap((IV.sub(cy, hw), IV.add(cy, hw)), (R[2], R[3]))
    vals = [ox, oy]
    for n in IV.axes(th):
        vals.append(IV.overlap(IV.proj_square(pose, n), proj_rect_i(R, n)))
    return IV.hull(*vals)[0]


def depth_pair_loose(pa, pb):
    return IV.depth_pair(pa, pb)


def extent_loose(pose):
    return IV.extent(pose)


import enc247 as E                # noqa: E402  the tight enclosures used by every verdict
depth_cell, depth_pair, extent = E.depth_cell, E.depth_pair, E.extent


# ---------------------------------------------------------------- point evaluation (floats)
def depth_cell_pt(pose, name, s):
    return C.overlap_depth(pose[0], pose[1], pose[2], rect_at(name, s))


def depth_pair_pt(a, b):
    return IV.depth_pair_pt(a, b)


def cells_met_pt(pose, s, tol=0.0):
    return tuple(n for n in RING if depth_cell_pt(pose, n, s) > tol)


# ---------------------------------------------------------------- D4 on cell names
def _apply(g, name):
    """g in {'r', 'mx', 'my', 'd'}: rotation by 90 deg CCW, mirror x -> s-x, mirror y -> s-y,
    diagonal x <-> y.  Rotation and the diagonal swap the kinds 01 <-> 10."""
    c, k = name[:2], name[2:]
    flip = {'01': '10', '10': '01', '00': '00'}
    if g == 'r':
        return CORNERS[(CORNERS.index(c) + 1) % 4] + flip[k]
    if g == 'mx':
        return {'BL': 'BR', 'BR': 'BL', 'TR': 'TL', 'TL': 'TR'}[c] + k
    if g == 'my':
        return {'BL': 'TL', 'TL': 'BL', 'BR': 'TR', 'TR': 'BR'}[c] + k
    if g == 'd':
        return {'BL': 'BL', 'TR': 'TR', 'BR': 'TL', 'TL': 'BR'}[c] + flip[k]
    raise ValueError(g)


def d4_maps():
    """the 8 permutations of RING (as dicts name -> name) generated by r and mx."""
    maps = {}
    ident = {n: n for n in RING}
    frontier = [ident]
    while frontier:
        m = frontier.pop()
        key = tuple(m[n] for n in RING)
        if key in maps:
            continue
        maps[key] = m
        for g in ('r', 'mx'):
            frontier.append({n: _apply(g, m[n]) for n in RING})
    return list(maps.values())


D4 = d4_maps()


def check_d4(s=3.85):
    """every D4 map sends each cell's rectangle onto the image cell's rectangle (numeric check)."""
    gens = {'r': lambda x, y: (s - y, x), 'mx': lambda x, y: (s - x, y),
            'my': lambda x, y: (x, s - y), 'd': lambda x, y: (y, x)}
    for g, f in gens.items():
        for n in RING:
            x0, x1, y0, y1 = rect_at(n, s)
            pts = [f(x, y) for x in (x0, x1) for y in (y0, y1)]
            xs, ys = sorted(p[0] for p in pts), sorted(p[1] for p in pts)
            img = rect_at(_apply(g, n), s)
            if max(abs(xs[0] - img[0]), abs(xs[-1] - img[1]), abs(ys[0] - img[2]), abs(ys[-1] - img[3])) > 1e-12:
                return False, (g, n)
    return len(D4) == 8, None


# ---------------------------------------------------------------- the catalogue's combinatorial layer
def in_some_nbr(cells):
    return any(set(cells) <= set(NBR[c]) for c in CORNERS)


def free_sets():
    """nonempty slot sets inside some window (a free square meets no box: MAX-FIVE gives <= 4 cells
    of one corner's neighbourhood)."""
    out = set()
    for c in CORNERS:
        w = WINDOWS[c]
        for r in range(1, 5):
            for comb in itertools.combinations(w, r):
                out.add(tuple(sorted(comb, key=RING.index)))
    return sorted(out, key=lambda t: (len(t), [RING.index(x) for x in t]))


def meeter_sets(c):
    """designated sets of a meeter of corner c: {c00} + any subset of its four slots."""
    out = []
    for r in range(0, 5):
        for comb in itertools.combinations(SLOTS_OF[c], r):
            out.append(('%s00' % c,) + tuple(sorted(comb, key=RING.index)))
    return out


def canon_cells(cells):
    return tuple(sorted(cells, key=RING.index))


# ---------------------------------------------------------------- canonical keys under D4
def map_spec(m, spec):
    """the image of a square spec ('M', corner, cells) / ('F', cells) under the D4 map m."""
    if spec[0] == 'M':
        cells = canon_cells(m[c] for c in spec[2])
        corner = [c for c in cells if c.endswith('00')][0][:2]
        return ('M', corner, cells)
    return ('F', canon_cells(m[c] for c in spec[1]))


def spec_str(spec):
    return ('M:%s:' % spec[1] if spec[0] == 'M' else 'F:') + '+'.join(spec[2] if spec[0] == 'M' else spec[1])


def tuple_key(specs):
    """canonical key of an unordered tuple of specs (pairs, triples) under D4 and relabelling."""
    best = None
    for m in D4:
        imgs = sorted(spec_str(map_spec(m, sp)) for sp in specs)
        k = ' | '.join(imgs)
        if best is None or k < best:
            best = k
    return best
