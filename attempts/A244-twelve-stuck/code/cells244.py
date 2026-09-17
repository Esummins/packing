"""A244: the TWELVE BORDER CELLS (4 corner boxes + 8 wall slots) of the container [0,s]^2,
the meeting test (interiors overlap) and the overlap depth, for 11 unit squares.

Cell naming follows A243 notes/wall_slot243.md: in the corner frame (u, v) of corner c
(u, v = the distances from c's two walls),
    c00 = [0,1] x [0,1]   the corner box
    c01 = [0,1] x [1,2]   the wall slot UP c's wall (the u = 0 wall)
    c10 = [1,2] x [0,1]   the wall slot ALONG c's floor (the v = 0 wall)
Twelve cells: BL00 BL01 BL10 BR00 BR01 BR10 TR00 TR01 TR10 TL00 TL01 TL10.
Every frame map is a signed diagonal, so every cell is a global axis-aligned rectangle.

A square MEETS a cell iff their INTERIORS overlap.  For two convex polygons of which one is an
axis-aligned rectangle the separating-axis set is {e_x, e_y, n_0(th), n_1(th)}; the overlap depth
is the min over those four axes of the projection overlap, and is > 0 iff the interiors meet.
"""
import math

import numpy as np

CORNERS = ('BL', 'BR', 'TR', 'TL')
KINDS = ('00', '01', '10')
CELLS = tuple('%s%s' % (c, k) for c in CORNERS for k in KINDS)     # 12, in this fixed order
NCELL = len(CELLS)
BOX = {'00': (0.0, 1.0, 0.0, 1.0), '01': (0.0, 1.0, 1.0, 2.0), '10': (1.0, 2.0, 0.0, 1.0)}


def cell_rect(name, s):
    """(x0, x1, y0, y1) of cell `name` in global coordinates at side s."""
    c, k = name[:2], name[2:]
    u0, u1, v0, v1 = BOX[k]
    if c == 'BL':
        return (u0, u1, v0, v1)
    if c == 'BR':
        return (s - u1, s - u0, v0, v1)
    if c == 'TR':
        return (s - u1, s - u0, s - v1, s - v0)
    if c == 'TL':
        return (u0, u1, s - v1, s - v0)
    raise ValueError(name)


def cell_rect_ds(name):
    """d(x0,x1,y0,y1)/ds of cell `name` (a constant 0/1 vector)."""
    c = name[:2]
    return {'BL': (0, 0, 0, 0), 'BR': (1, 1, 0, 0), 'TR': (1, 1, 1, 1), 'TL': (0, 0, 1, 1)}[c]


def square_corners(cx, cy, th):
    """(4,2) corners of the unit square with centre (cx,cy) and tilt th."""
    co, si = math.cos(th), math.sin(th)
    h = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
    return np.array([(cx + co * a - si * b, cy + si * a + co * b) for a, b in h])


def square_normals(th):
    """the two distinct edge-normal directions of a square at tilt th."""
    co, si = math.cos(th), math.sin(th)
    return np.array([(co, si), (-si, co)])


def overlap_depth(cx, cy, th, rect):
    """min over the four separating axes of the projection overlap of the unit square and the
    axis-aligned rect.  > 0 iff the interiors meet; <= 0 iff they are interior-disjoint."""
    x0, x1, y0, y1 = rect
    q = square_corners(cx, cy, th)
    best = min(min(q[:, 0].max(), x1) - max(q[:, 0].min(), x0),
               min(q[:, 1].max(), y1) - max(q[:, 1].min(), y0))
    box = np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    for n in square_normals(th):
        pa, pb = q @ n, box @ n
        best = min(best, min(pa.max(), pb.max()) - max(pa.min(), pb.min()))
    return float(best)


def meets(cx, cy, th, rect, tol=0.0):
    return overlap_depth(cx, cy, th, rect) > tol


def depth_table(z, n=11):
    """(12, n) overlap depths of every square against every cell.  z = A217's 34-vector."""
    z = np.asarray(z, float)
    s = float(z[33])
    out = np.zeros((NCELL, n))
    for k, name in enumerate(CELLS):
        r = cell_rect(name, s)
        for i in range(n):
            out[k, i] = overlap_depth(z[3 * i], z[3 * i + 1], z[3 * i + 2], r)
    return out


def meeter_sets(z, n=11, tol=0.0):
    d = depth_table(z, n)
    return {name: [i for i in range(n) if d[k, i] > tol] for k, name in enumerate(CELLS)}


def stuck_report(z, n=11, tol=0.0):
    """which of the twelve cells are doubly met, and the worst second-deepest depth."""
    d = depth_table(z, n)
    ms = {}
    worst = float('inf')
    for k, name in enumerate(CELLS):
        idx = np.argsort(-d[k])
        ms[name] = [int(i) for i in idx if d[k, i] > tol]
        second = float(d[k, idx[1]])
        worst = min(worst, second)
    return {'meeters': ms, 'n_doubly_met': sum(len(v) >= 2 for v in ms.values()),
            'worst_second_depth': worst,
            'twelve_stuck': all(len(v) >= 2 for v in ms.values()),
            'four_stuck': all(len(ms['%s00' % c]) >= 2 for c in CORNERS)}


# ---------------------------------------------------------------- which cells share a wall
WALL_CELLS = {'y=0': ('BL00', 'BL10', 'BR10', 'BR00'), 'x=s': ('BR00', 'BR01', 'TR01', 'TR00'),
              'y=s': ('TR00', 'TR10', 'TL10', 'TL00'), 'x=0': ('TL00', 'TL01', 'BL01', 'BL00')}
SLOTS = tuple(c for c in CELLS if not c.endswith('00'))
BOXES = tuple(c for c in CELLS if c.endswith('00'))


def supply_kind(cell, i, ms):
    """how cell `cell` is supplied by square i: OWN (a meeter of its own corner's box),
    ADJ (a meeter of the adjacent corner's box on the same wall), FAR (any other corner box),
    FREE (i meets no corner box)."""
    own = cell[:2]
    boxes_met = [b for b in BOXES if i in ms.get(b, ())]
    if not boxes_met:
        return 'FREE'
    if '%s00' % own in boxes_met:
        return 'OWN'
    wall = [w for w, cs in WALL_CELLS.items() if cell in cs]
    adj = set()
    for w in wall:
        adj.update(c for c in WALL_CELLS[w] if c.endswith('00'))
    if any(b in adj for b in boxes_met):
        return 'ADJ'
    return 'FAR'
