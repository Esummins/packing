#!/usr/bin/env python3
"""
atlas_lib.py -- A25-wastage-atlas: continuum wastage atlas over BOXES of placements.

An atlas CELL is a hypothesis box K = [t0,t1] x [cx0,cx1] x [cy0,cy1] ("some
packing square has tan(theta/2) in [t0,t1] and centre in the given box").  The
atlas stores a rational number dead_lb(K) with the certified meaning

    for EVERY placement P with parameters in K, the regions listed for K are
    pairwise interior-disjoint, interior-disjoint from P, and dead for {P};
    hence (budget lemma, A23 notes Lemma 2) any packing of n unit squares in
    [0,s]^2 containing such a P has  sum(dead) <= s^2 - n.

Uniformity is inherited from A23's `PlacedBox` (every discharge -- witness-point
interiority, interval SAT separation -- is taken over the whole core box).

EFFICIENCY IDEA (the point of A25).  We do NOT want the maximal dead area, only
a certified lower bound big enough to be useful.  So per cell we
  (1) build a SMALL number of candidate windows -- the wall/corner shadow strips
      (single) and additionally the inter-square window (pair) identified by A23,
  (2) tile them with a COARSE dyadic grid (cell0 = 1/8, refined at most twice to
      min_cell = 1/32) instead of A23's 1/64 quadtree over the whole container,
  (3) visit tiles nearest the square first, and STOP at a work budget (or an
      area target).
Dropping tiles only lowers the reported number, so every cap keeps the result a
certified LOWER bound.  A23 estimated ~1 CPU-day per corner box exhaustively;
this brings a cell down to seconds.

Author: A25-wastage-atlas, 2026-08-20.
"""
from __future__ import annotations

import math
import time
from fractions import Fraction as F

from dead_region import (Certifier, Placed, PlacedBox, Region, cos_sin,
                         _convex_interior_disjoint)

HALF = F(1, 2)


def _mid_corners(B):
    """corners of the MIDPOINT realisation of a core box (a genuine placement of
    the hypothesis) -- used only as the obstacle of the negative filter."""
    c, s = B.c, B.s
    return [(B.cx + c * u - s * v, B.cy + s * u + c * v)
            for (u, v) in ((-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF))]
from wastage import _cell_disjoint_placed

HREACH = F(7072, 10000)          # > sqrt(2)/2: reach of any square point from its centre
TSTAR = F(414214, 1000000)       # tan(22.5 deg), where w = cos+sin is maximal


# ------------------------------------------------------------------ rationals
def tanhalf(deg, up):
    """rational bound on tan(deg/2) rounded OUTWARD (up=True -> >=, else <=)."""
    v = math.tan(math.radians(deg) / 2.0)
    n = v * 10 ** 7
    i = math.floor(n) + (1 if up else 0)
    return max(F(0), F(int(i), 10 ** 7))


def wlo_of(t0, t1):
    """min over [t0,t1] of w = cos+sin (w is unimodal, max at TSTAR)."""
    c0, s0 = cos_sin(F(t0))
    c1, s1 = cos_sin(F(t1))
    return min(c0 + s0, c1 + s1)


def clip_box(t0, t1, x0, x1, y0, y1, s):
    """clip a centre box to the admissible range [w/2, s-w/2]^2 (uses wLo, so the
    clipped box still contains EVERY admissible placement of the cell).
    Returns None if the cell contains no admissible placement."""
    lo = wlo_of(t0, t1) / 2
    hi = F(s) - lo
    a0, a1 = max(F(x0), lo), min(F(x1), hi)
    b0, b1 = max(F(y0), lo), min(F(y1), hi)
    if a0 > a1 or b0 > b1:
        return None
    return a0, a1, b0, b1


# ------------------------------------------------------------------ rectangles
def rect_diff(A, B):
    """A minus B as a list of disjoint rectangles (x0,x1,y0,y1)."""
    ax0, ax1, ay0, ay1 = A
    bx0, bx1, by0, by1 = B
    if bx1 <= ax0 or bx0 >= ax1 or by1 <= ay0 or by0 >= ay1:
        return [A]
    out = []
    if bx0 > ax0:
        out.append((ax0, bx0, ay0, ay1))
    if bx1 < ax1:
        out.append((bx1, ax1, ay0, ay1))
    mx0, mx1 = max(ax0, bx0), min(ax1, bx1)
    if by0 > ay0:
        out.append((mx0, mx1, ay0, by0))
    if by1 < ay1:
        out.append((mx0, mx1, by1, ay1))
    return [r for r in out if r[1] > r[0] and r[3] > r[2]]


def disjointify(rects):
    """make a list of rectangles pairwise disjoint (keep earlier ones intact)."""
    out = []
    for r in rects:
        pieces = [r]
        for q in out:
            nxt = []
            for p in pieces:
                nxt += rect_diff(p, q)
            pieces = nxt
            if not pieces:
                break
        out += pieces
    return out


def snap(rects, cell0, s):
    """snap rectangles outward onto the global cell0 grid, clip to [0,s]^2."""
    out = []
    S = F(s)
    for (x0, x1, y0, y1) in rects:
        a0 = max(F(0), F(math.floor(float(F(x0) / cell0))) * cell0)
        a1 = min(S, F(math.ceil(float(F(x1) / cell0))) * cell0)
        b0 = max(F(0), F(math.floor(float(F(y0) / cell0))) * cell0)
        b1 = min(S, F(math.ceil(float(F(y1) / cell0))) * cell0)
        if a1 > a0 and b1 > b0:
            out.append((a0, a1, b0, b1))
    return out


def merge_rects(cells):
    """greedy merge of a list of (x0,y0,x1,y1) cells into fewer rectangles
    (rows first, then vertical stacking).  Output rectangles are exactly the
    union of the input cells, hence still pairwise interior-disjoint."""
    rows = {}
    for (x0, y0, x1, y1) in cells:
        rows.setdefault((y0, y1), []).append((x0, x1))
    strips = []
    for (y0, y1), xs in rows.items():
        xs.sort()
        cur = None
        for (a, b) in xs:
            if cur is not None and a == cur[1]:
                cur = (cur[0], b)
            else:
                if cur:
                    strips.append((cur[0], y0, cur[1], y1))
                cur = (a, b)
        if cur:
            strips.append((cur[0], y0, cur[1], y1))
    # vertical merge of identical x-spans
    cols = {}
    for (x0, y0, x1, y1) in strips:
        cols.setdefault((x0, x1), []).append((y0, y1))
    out = []
    for (x0, x1), ys in cols.items():
        ys.sort()
        cur = None
        for (a, b) in ys:
            if cur is not None and a == cur[1]:
                cur = (cur[0], b)
            else:
                if cur:
                    out.append((x0, cur[0], x1, cur[1]))
                cur = (a, b)
        if cur:
            out.append((x0, cur[0], x1, cur[1]))
    return out


# ------------------------------------------------------------------ windows
def wall_rects(bx0, bx1, by0, by1, s, along=F(7, 10), gap_max=F(1, 1),
               depth_cap=F(3, 2), R=HREACH):
    """candidate dead-area windows for a core centre box near the container walls.

    A wall is 'in reach' iff the square could come within `gap_max` of it (only
    then can the strip between square and wall be dead: a gap >= 1 admits an
    upright square).  The window is the strip from the wall out to the far side
    of the square (capped), and `along` past the square's reach sideways -- the
    two wedges of A23 sect.4a live exactly there.  Windows are made pairwise
    disjoint, so the certified tiles inside them are automatically pairwise
    interior-disjoint (needed for the budget lemma)."""
    S = F(s)
    bx0, bx1, by0, by1 = F(bx0), F(bx1), F(by0), F(by1)
    out = []
    if by0 - R < gap_max:                                    # bottom wall
        d = min(by1 + R, depth_cap)
        out.append((bx0 - R - along, bx1 + R + along, F(0), d))
    if (S - by1) - R < gap_max:                              # top wall
        d = min((S - by0) + R, depth_cap)
        out.append((bx0 - R - along, bx1 + R + along, S - d, S))
    if bx0 - R < gap_max:                                    # left wall
        d = min(bx1 + R, depth_cap)
        out.append((F(0), d, by0 - R - along, by1 + R + along))
    if (S - bx1) - R < gap_max:                              # right wall
        d = min((S - bx0) + R, depth_cap)
        out.append((S - d, S, by0 - R - along, by1 + R + along))
    return out


def between_rect(boxes, s, pad=F(35, 100), R=HREACH):
    """window covering the two cores and the space between/around them."""
    x0 = min(b[0] for b in boxes) - R - pad
    x1 = max(b[1] for b in boxes) + R + pad
    y0 = min(b[2] for b in boxes) - R - pad
    y1 = max(b[3] for b in boxes) + R + pad
    return (x0, x1, y0, y1)


# ------------------------------------------------------------------ the mapper
def map_windows(placed, s, rects, order_from, cell0=F(1, 8), min_cell=F(1, 32),
                mode='float', depth_max=24, max_boxes_per_cell=1500,
                work_budget=2500, area_target=None, cert=None,
                min_cell_occ=F(1, 16)):
    """certify dead area over a list of DISJOINT rectangles, tiles nearest
    `order_from` first, stopping at `work_budget` certifier calls (or when
    `area_target` is reached).  Returns a certified LOWER bound (dropped and
    unvisited tiles simply do not count)."""
    S = F(s)
    cert = cert or Certifier(S, placed, mode=mode, depth_max=depth_max)
    tops = []
    for (x0, x1, y0, y1) in rects:
        i0 = int(math.floor(float(F(x0) / cell0)))
        i1 = int(math.ceil(float(F(x1) / cell0)))
        j0 = int(math.floor(float(F(y0) / cell0)))
        j1 = int(math.ceil(float(F(y1) / cell0)))
        for i in range(i0, i1):
            for j in range(j0, j1):
                a0, a1 = max(F(x0), i * cell0), min(F(x1), (i + 1) * cell0)
                b0, b1 = max(F(y0), j * cell0), min(F(y1), (j + 1) * cell0)
                if a1 > a0 and b1 > b0:
                    tops.append((a0, a1, b0, b1))
    ox, oy = float(order_from[0]), float(order_from[1])
    tops.sort(key=lambda r: (float(r[0] + r[1]) / 2 - ox) ** 2
                            + (float(r[2] + r[3]) / 2 - oy) ** 2)
    area = F(0)
    cells = []
    work = n_pass = n_drop = n_occ = n_probe = 0
    truncated = False
    t_start = time.time()
    key = lambda c: (int(math.floor(float(c[0] / cell0) + 1e-9)),
                     int(math.floor(float(c[2] / cell0) + 1e-9)))

    def split(c):
        x0, x1, y0, y1 = c
        xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
        return [(x0, xm, y0, ym), (xm, x1, y0, ym),
                (x0, xm, ym, y1), (xm, x1, ym, y1)]

    def probe(c, n):
        """quick_cover at up to n points; True = a legal cover was FOUND
        (the tile is provably not dead -- negative filter only)."""
        nonlocal n_probe
        x0, x1, y0, y1 = c
        w, h = x1 - x0, y1 - y0
        pts = [(x0 + w / 2, y0 + h / 2), (x0 + w / 4, y0 + h / 4),
               (x1 - w / 4, y1 - h / 4), (x0 + w / 4, y1 - h / 4),
               (x1 - w / 4, y0 + h / 4)]
        for (qx, qy) in pts[:n]:
            n_probe += 1
            if cert.quick_cover(qx, qy):
                return True
        return False

    # ---- LEVEL 0: every tile at resolution cell0, ONE probe each (cheap screen)
    alive, passed, refine = {}, set(), []
    for c in tops:
        if work >= work_budget or (area_target is not None and area >= area_target):
            truncated = True
            break
        x0, x1, y0, y1 = c
        if any(all(P.strictly_inside(px, py, margin=0) for (px, py) in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1))) for P in placed):
            n_occ += 1
            continue
        if not _cell_disjoint_placed(x0, y0, x1, y1, placed):
            if max(x1 - x0, y1 - y0) > min_cell_occ:
                refine += split(c)
            else:
                n_occ += 1
            continue
        work += 1
        if mode == 'float' and probe(c, 1):
            alive[key(c)] = c
            continue
        D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        if cert.certify(D, max_boxes=max_boxes_per_cell)['passed']:
            area += D.area
            cells.append((x0, y0, x1, y1))
            passed.add(key(c))
            n_pass += 1
        elif max(x1 - x0, y1 - y0) > min_cell:
            refine += split(c)
        else:
            n_drop += 1
    # boundary refinement: an alive tile touching a certified-dead tile may still
    # have dead corners -- refine exactly those (this is where the wedge edges are)
    for k, c in alive.items():
        if any((k[0] + dx, k[1] + dy) in passed for (dx, dy) in
               ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))):
            refine += split(c)
        else:
            n_drop += 1
    # ---- LEVEL 1+: refine queue (full 5-point probe), down to min_cell
    while refine and not truncated:
        nxt = []
        for c in refine:
            if work >= work_budget or (area_target is not None and area >= area_target):
                truncated = True
                break
            x0, x1, y0, y1 = c
            wd, ht = x1 - x0, y1 - y0
            if any(all(P.strictly_inside(px, py, margin=0) for (px, py) in
                       ((x0, y0), (x1, y0), (x1, y1), (x0, y1))) for P in placed):
                n_occ += 1
                continue
            if not _cell_disjoint_placed(x0, y0, x1, y1, placed):
                if max(wd, ht) > min_cell_occ:
                    nxt += split(c)
                else:
                    n_occ += 1
                continue
            work += 1
            if mode == 'float' and probe(c, 5):
                if max(wd, ht) > min_cell:
                    nxt += split(c)
                else:
                    n_drop += 1
                continue
            D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
            if cert.certify(D, max_boxes=max_boxes_per_cell)['passed']:
                area += D.area
                cells.append((x0, y0, x1, y1))
                n_pass += 1
            elif max(wd, ht) > min_cell:
                nxt += split(c)
            else:
                n_drop += 1
        refine = nxt
    return dict(area=area, cells=cells, work=work, n_pass=n_pass, n_drop=n_drop,
                n_occ=n_occ, n_probe=n_probe, truncated=truncated,
                seconds=time.time() - t_start, n_tops=len(tops))


# ------------------------------------------------------------------ atlas cells
def single_cell(s, tbox, xbox, ybox, params=None):
    """certified uniform dead area for ONE core box.  Returns a result dict or
    None if the cell holds no admissible placement."""
    p = dict(cell0=F(1, 8), min_cell=F(1, 16), min_cell_occ=F(1, 16),
             work_budget=1200, depth_max=24, max_boxes_per_cell=1500,
             along=F(7, 10), gap_max=F(1, 1), depth_cap=F(3, 2),
             area_target=None, mode='float')
    p.update(params or {})
    S = F(s)
    t0, t1 = F(tbox[0]), F(tbox[1])
    cl = clip_box(t0, t1, xbox[0], xbox[1], ybox[0], ybox[1], S)
    if cl is None:
        return None
    bx0, bx1, by0, by1 = cl
    B = PlacedBox(t0, t1, bx0, bx1, by0, by1)
    B.filter_corners = _mid_corners(B)
    rects = wall_rects(bx0, bx1, by0, by1, S, along=p['along'],
                       gap_max=p['gap_max'], depth_cap=p['depth_cap'])
    if not rects:
        return dict(area=F(0), cells=[], work=0, n_pass=0, n_drop=0, n_occ=0,
                    truncated=False, seconds=0.0, n_tops=0, screened='no wall in reach',
                    box=(bx0, bx1, by0, by1))
    rects = disjointify(snap(rects, p['cell0'], S))
    r = map_windows([B], S, rects, ((bx0 + bx1) / 2, (by0 + by1) / 2),
                    cell0=p['cell0'], min_cell=p['min_cell'], mode=p['mode'],
                    depth_max=p['depth_max'],
                    max_boxes_per_cell=p['max_boxes_per_cell'],
                    work_budget=p['work_budget'], area_target=p['area_target'],
                    min_cell_occ=p['min_cell_occ'])
    r['box'] = (bx0, bx1, by0, by1)
    return r


def pair_cell(s, tboxA, xboxA, yboxA, tboxB, xboxB, yboxB, params=None):
    """certified uniform dead area for TWO core boxes (the hypothesis 'two
    packing squares lie in these two cores').  Windows = the wall strips of both
    cores plus the inter-square window; all made disjoint."""
    p = dict(cell0=F(1, 8), min_cell=F(1, 16), min_cell_occ=F(1, 16),
             work_budget=2200, depth_max=24, max_boxes_per_cell=1500,
             along=F(7, 10), gap_max=F(1, 1), depth_cap=F(3, 2), pad=F(35, 100),
             area_target=None, mode='float')
    p.update(params or {})
    S = F(s)
    out = []
    for (tb, xb, yb) in ((tboxA, xboxA, yboxA), (tboxB, xboxB, yboxB)):
        cl = clip_box(tb[0], tb[1], xb[0], xb[1], yb[0], yb[1], S)
        if cl is None:
            return None
        out.append((F(tb[0]), F(tb[1])) + cl)
    boxes = [(o[2], o[3], o[4], o[5]) for o in out]
    # feasibility: two interior-disjoint unit squares have centre distance >= 1
    dmax = math.hypot(max(abs(float(boxes[0][1] - boxes[1][0])),
                          abs(float(boxes[1][1] - boxes[0][0]))),
                      max(abs(float(boxes[0][3] - boxes[1][2])),
                          abs(float(boxes[1][3] - boxes[0][2]))))
    if dmax < 1.0:
        return dict(infeasible=True)
    P = [PlacedBox(o[0], o[1], o[2], o[3], o[4], o[5]) for o in out]
    for B in P:
        B.filter_corners = _mid_corners(B)
    rects = []
    for b in boxes:
        rects += wall_rects(b[0], b[1], b[2], b[3], S, along=p['along'],
                            gap_max=p['gap_max'], depth_cap=p['depth_cap'])
    rects.append(between_rect(boxes, S, pad=p['pad']))
    rects = [(max(F(0), a), min(S, b), max(F(0), c), min(S, d))
             for (a, b, c, d) in rects]
    rects = [r for r in rects if r[1] > r[0] and r[3] > r[2]]
    rects = disjointify(snap(rects, p['cell0'], S))
    ctr = ((boxes[0][0] + boxes[0][1] + boxes[1][0] + boxes[1][1]) / 4,
           (boxes[0][2] + boxes[0][3] + boxes[1][2] + boxes[1][3]) / 4)
    r = map_windows(P, S, rects, ctr, cell0=p['cell0'], min_cell=p['min_cell'],
                    mode=p['mode'], depth_max=p['depth_max'],
                    max_boxes_per_cell=p['max_boxes_per_cell'],
                    work_budget=p['work_budget'], area_target=p['area_target'],
                    min_cell_occ=p['min_cell_occ'])
    r['boxes'] = boxes
    return r
