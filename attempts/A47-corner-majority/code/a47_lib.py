#!/usr/bin/env python3
"""a47_lib.py -- A47 leg (b): the I-L18 CORNER / SIDE primitive tables.

Everything is built on A23's certifier (dead_region.py) and the A45/A46 harness
(a45_lib.py, wastage.py, atlas_lib.py, clip_util.py), all COPIED VERBATIM into
this directory.  Nothing outside attempts/A47-corner-majority is modified.

FRAME.  Unlike A45/A46 (plane-mode certificates in a big S = 20 container) the
I-L18 primitives are CONTAINER primitives: the real container [0, s0]^2 with
s0 = 969271/250000, the reference corner at the ORIGIN and the reference wall
x = 0.  So `Certifier(s0, [PlacedBox], ...)` is used directly and the
container-containment constraint (centre in [w/2, s0 - w/2]^2) is part of the
certificate.  No Lemma-P transport is needed or claimed; instead the four
container corners / four walls are related by the exact D4 symmetry of the
container, which is what the canary D4-map uses.

HYPOTHESIS.  ONE unit square with centre in a rational position cell and tilt
in a degree bin, PLACEMENT-UNIFORM: a `PlacedBox` per tilt sub-box, so every
certificate holds for EVERY placement of the hypothesis (A25/A14 core-box
semantics).  The tilt bin is covered by `nsub >= 4` sub-boxes whose rational
(cos, sin) hulls are OUTWARD-rounded (`atlas_lib.tanhalf`).

FEASIBILITY.  A placement inside the container needs cx, cy in [w/2, s0 - w/2]
with w = cos + sin.  Over a tilt sub-box [t0,t1], w >= wlo := min(w(t0), w(t1))
(w is unimodal with its max at t* = tan 22.5 deg, so its min over an interval is
at an endpoint).  Every realisable placement of the sub-box therefore has
cx, cy >= wlo/2, and the centre box may be shrunk to
    [max(x0, wlo/2), x1] x [max(y0, wlo/2), y1]
without excluding any realisable placement (SOUND: the shrunk box still
CONTAINS every placement of the hypothesis that can occur in the container).
If the shrunk box is empty the sub-box carries no realisable placement and is
DROPPED (again sound -- it is vacuous).  If every sub-box drops, the whole
(cell x bin) entry is INFEASIBLE: near-corner cells force near-upright tilts.

KEEPER.  A tile is kept iff it lies in the window, is interior-disjoint from
EVERY placement of the hypothesis (`PlacedBox.cell_interior_disjoint`, exact
interval SAT over the core box) and is certified dead for EVERY retained tilt
sub-box.  Tiles that reach `min_cell` undecided are DROPPED, so every shipped
area is a certified LOWER bound.

EXACTNESS.  The map is run in float mode (outward eps guards) for SEARCH; the
identical shipped tile list is then re-certified in pure Fractions
(`recert_tiles`).  Only the exact area is shipped.

Author: A47 agent (leg b), 2026-08-29.
"""
from __future__ import annotations

import json
import os
import time
from fractions import Fraction as F

from dead_region import (Certifier, Placed, PlacedBox, Region, cos_sin)
from atlas_lib import tanhalf, _mid_corners, merge_rects
from wastage import _cell_disjoint_placed
from a45_lib import FastExactCertifier, region_ok_all

HERE = os.path.dirname(os.path.abspath(__file__))
A47 = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(A47, 'results')
WORK = os.path.join(A47, 'work')

S0 = F(969271, 250000)                  # 3.877084 exactly
B0 = S0 * S0 - 11                       # 4.031780343056
WIN = F(13, 8)                          # 1.625, the dead-area window radius
CELL0 = F(1, 8)
MIN_CELL = F(1, 64)
TSTAR = F(414214, 1000000)

# ---- A21 occupancy zones, ENLARGED to cover the s0/3.88 scale-back ----------
# A21's THM1/THM2 zones live in the 3.88-normalised frame; mapping to side s0
# scales centres by s0/(97/25) = 969271/970000 = 0.999249 TOWARD the corner, so
# an occupant's centre can sit slightly below 1/2 (>= 0.49963).  The position
# boxes below CONTAIN the mapped zones.
XCELLS = [(F(49, 100), F(7, 10)), (F(7, 10), F(9, 10)), (F(9, 10), F(11, 10))]
XNAMES = ['x0', 'x1', 'x2']
YCELLS_SIDE = [(F(109, 100), F(9, 5)), (F(9, 5), F(139, 50))]
YNAMES_SIDE = ['y0', 'y1']

CORNER_BINS = [(F(0), F(1)), (F(1), F(5)), (F(5), F(15)),
               (F(15), F(30)), (F(30), F(40)), (F(40), F(45))]
CORNER_BIN_NAMES = ['b0_1', 'b1_5', 'b5_15', 'b15_30', 'b30_40', 'b40_45']
SIDE_BINS = [(F(0), F(1)), (F(1), F(15)), (F(15), F(45))]
SIDE_BIN_NAMES = ['s0_1', 's1_15', 's15_45']

RADII = [F(1, 2), F(3, 4), F(1), F(5, 4), F(13, 8)]


# ------------------------------------------------------------------ rationals
def wlo_of(t0, t1):
    """min over [t0,t1] of w = cos + sin (unimodal, max at TSTAR => min at an
    endpoint)."""
    c0, s0 = cos_sin(F(t0))
    c1, s1 = cos_sin(F(t1))
    return min(c0 + s0, c1 + s1)


def deg_t(d0, d1):
    """rational t-interval OUTWARD-rounding the degree interval [d0,d1]."""
    return tanhalf(float(d0), up=False), tanhalf(float(d1), up=True)


def nsub_for(d0, d1, base=4, wmax=3.0):
    n = base
    while float(d1 - d0) / n > wmax:
        n += 1
    return n


# ------------------------------------------------------------------ configs
def build_configs(xcell, ycell, degbin, nsub=None):
    """PlacedBox sub-boxes covering (position cell) x (tilt bin), each shrunk to
    its feasible part.  Returns (configs, info)."""
    x0, x1 = xcell
    y0, y1 = ycell
    a0, a1 = degbin
    if nsub is None:
        nsub = nsub_for(a0, a1)
    out, dropped, kept = [], [], []
    for i in range(nsub):
        d0 = a0 + (a1 - a0) * F(i, nsub)
        d1 = a0 + (a1 - a0) * F(i + 1, nsub)
        t0, t1 = deg_t(d0, d1)
        lo = wlo_of(t0, t1) / 2
        bx0, bx1 = max(x0, lo), x1
        by0, by1 = max(y0, lo), y1
        if bx0 > bx1 or by0 > by1:
            dropped.append(dict(deg=[str(d0), str(d1)], reason='infeasible',
                                w_lo_half=str(lo)))
            continue
        B = PlacedBox(t0, t1, bx0, bx1, by0, by1)
        B.filter_corners = _mid_corners(B)
        out.append(dict(placed=[B], deg=(d0, d1), t=(t0, t1),
                        box=(bx0, bx1, by0, by1)))
        kept.append(dict(deg=[str(d0), str(d1)],
                         centre_box=[str(bx0), str(bx1), str(by0), str(by1)],
                         shrunk=bool(bx0 > x0 or by0 > y0)))
    info = dict(nsub=nsub, n_kept=len(out), n_dropped=len(dropped),
                kept=kept, dropped=dropped,
                feasible=('EMPTY' if not out else
                          ('PARTIAL' if dropped or any(k['shrunk'] for k in kept)
                           else 'FULL')))
    return out, info


# ------------------------------------------------------------------ tiling
def grid_tiles(x0, y0, x1, y1, cell0):
    """cell0-grid tiles ANCHORED AT THE ORIGIN covering [x0,x1] x [y0,y1]."""
    i0 = int(F(x0) // cell0)
    i1 = int(-((-F(x1)) // cell0))
    j0 = int(F(y0) // cell0)
    j1 = int(-((-F(y1)) // cell0))
    out = []
    for i in range(i0, i1):
        for j in range(j0, j1):
            a0, a1 = max(F(x0), i * cell0), min(F(x1), (i + 1) * cell0)
            b0, b1 = max(F(y0), j * cell0), min(F(y1), (j + 1) * cell0)
            if a1 > a0 and b1 > b0:
                out.append((a0, b0, a1, b1))
    return out


# ------------------------------------------------------------------ the mapper
def dead_map(configs, window, s=S0, cell0=CELL0, min_cell=MIN_CELL,
             mode='float', depth_max=26, max_boxes=4000, work_budget=100000):
    """Certified-dead tile map of `window` under the bin-uniform hypothesis.
    Returns dict(area, cells, stats).  Area is a certified LOWER bound."""
    cls = FastExactCertifier if mode == 'exact' else Certifier
    certs = [cls(s, cfg['placed'], mode=mode, depth_max=depth_max)
             for cfg in configs]
    placed_all = [cfg['placed'] for cfg in configs]
    area = F(0)
    cells = []
    n_pass = n_drop = n_occ = n_qc = 0
    work = 0
    t_start = time.time()
    stack = grid_tiles(*window, cell0)
    while stack:
        x0, y0, x1, y1 = stack.pop()
        w, h = x1 - x0, y1 - y0
        # (1) tile fully inside SOME core placement hull -> occupied
        if any(all(P.strictly_inside(qx, qy, margin=0) for (qx, qy) in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
               for pl in placed_all for P in pl):
            n_occ += 1
            continue
        # (2) keeper: must be interior-disjoint from EVERY placement
        if not all(_cell_disjoint_placed(x0, y0, x1, y1, pl) for pl in placed_all):
            if max(w, h) > min_cell:
                xm, ym = x0 + w / 2, y0 + h / 2
                stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)]
            else:
                n_occ += 1
            continue
        if work >= work_budget:
            n_drop += 1
            continue
        work += 1
        alive = False
        if mode == 'float':
            xm, ym = x0 + w / 2, y0 + h / 2
            for (qx, qy) in ((xm, ym),
                             (x0 + w / 4, y0 + h / 4), (x1 - w / 4, y1 - h / 4),
                             (x0 + w / 4, y1 - h / 4), (x1 - w / 4, y0 + h / 4)):
                if any(c.quick_cover(qx, qy) for c in certs):
                    alive = True
                    n_qc += 1
                    break
        if not alive:
            D = Region.rect(x0, y0, x1, y1)
            alive = not region_ok_all(D, certs, max_boxes)
        if not alive:
            area += w * h
            cells.append((x0, y0, x1, y1))
            n_pass += 1
        elif max(w, h) > min_cell:
            xm, ym = x0 + w / 2, y0 + h / 2
            stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                      (x0, ym, xm, y1), (xm, ym, x1, y1)]
        else:
            n_drop += 1
    return dict(area=area, cells=cells,
                stats=dict(n_pass=n_pass, n_drop=n_drop, n_occ=n_occ,
                           n_quickcover=n_qc, work=work,
                           seconds=round(time.time() - t_start, 2)))


def recert_tiles(configs, cells, s=S0, depth_max=40, max_boxes=400000):
    """pure-Fraction re-certification of an identical tile list."""
    certs = [FastExactCertifier(s, cfg['placed'], mode='exact',
                                depth_max=depth_max) for cfg in configs]
    area = F(0)
    ok = []
    failed = []
    t0 = time.time()
    for (x0, y0, x1, y1) in cells:
        D = Region.rect(x0, y0, x1, y1)
        if region_ok_all(D, certs, max_boxes):
            area += (x1 - x0) * (y1 - y0)
            ok.append((x0, y0, x1, y1))
        else:
            failed.append([str(x0), str(y0), str(x1), str(y1)])
    return dict(area=area, cells=ok, failed=failed,
                seconds=round(time.time() - t0, 2))


# ------------------------------------------------------------------ profiles
def clip_rect_area(cells, x0, y0, x1, y1):
    a = F(0)
    for (u0, v0, u1, v1) in cells:
        p0, p1 = max(u0, x0), min(u1, x1)
        q0, q1 = max(v0, y0), min(v1, y1)
        if p1 > p0 and q1 > q0:
            a += (p1 - p0) * (q1 - q0)
    return a


def radial_corner(cells, radii=RADII):
    """exact tile area within sup-distance r of the corner (0,0)."""
    return {str(r): clip_rect_area(cells, F(0), F(0), r, r) for r in radii}


def radial_wall(cells, radii=RADII):
    """exact tile area within distance r of the wall x = 0."""
    out = {}
    for r in radii:
        a = F(0)
        for (u0, v0, u1, v1) in cells:
            p1 = min(u1, r)
            if p1 > u0:
                a += (p1 - u0) * (v1 - v0)
        out[str(r)] = a
    return out


# ------------------------------------------------------------------ io
def jcells(cells):
    return [[str(a) for a in c] for c in cells]


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)
