#!/usr/bin/env python3
"""a46_lib.py -- A46 balanced-wedge table: FULL dead-region maps in the A45 frames.

Difference from A45: NO moat, NO rho_min clip.  We map the WHOLE dead region in
a rectangular window around the contact point and keep every tile that passes
the Lemma-K keeper.  The certified number per bin is then a lower bound on the
dead area OWNED BY THAT CONTACT'S SLAB, uniformly over the bin.

Soundness chain (unchanged from A45 / A23):
  * A23 Lemma 2 (budget): pairwise interior-disjoint dead regions, interior-
    disjoint from the packing squares, have total area <= s^2 - n.
  * Lemma P/P' (plane mode): certificates are run in the big container S = 20
    with the hypothesis square local and the margin asserted, so they transfer
    to ANY container and ANY along-wall position of the contact.
  * Lemma K (containment, WC form): every kept tile lies in
    slab(wall, along-wall bbox of the square) = [10 - min sin phi,
    10 + min cos phi] x [0, min(cos phi + sin phi)], intersected over the bin.
    Tiles outside are DROPPED (sound: fewer regions).  This is what makes the
    per-contact region container-independent and lets task 5 disjointify along
    the wall by a Voronoi truncation.
  * Bin uniformity: the bin is covered by `nsub` PlacedBox sub-boxes with
    outward-rounded rational (cos, sin) hulls; a tile counts only if it
    certifies on EVERY sub-box.
  * Every dropped / unrefined / work-capped tile only LOWERS the number.

Author: A46 agent W2, 2026-08-29.
"""
from __future__ import annotations

import time
from fractions import Fraction as F

from dead_region import Region
from wastage import _cell_disjoint_placed

import a45_lib as L

PX = L.PX            # 10
PY = L.PY


def wc_keeper(configs):
    """A45's Lemma-K WC slab keeper, VERBATIM, with its bbox exposed so that
    window_map can reject far tiles without refining them."""
    k = L.keeper_wc(configs)
    i = k.info
    k.bbox = (F(i['xlo']), F(0), F(i['xhi']), F(i['yhi']))
    return k


def hull_keeper(configs, kind):
    """A45's Lemma-K conv(a cup b) keeper for CE/CC, VERBATIM, with the hull's
    bounding box exposed for fast rejection of far tiles."""
    k = L.keeper_hull(configs, kind)
    H = [(F(x), F(y)) for (x, y) in k.info['hull']]
    k.bbox = (min(p[0] for p in H), min(p[1] for p in H),
              max(p[0] for p in H), max(p[1] for p in H))
    return k


# ------------------------------------------------------------------ windows
def rect_tiles(x0, x1, y0, y1, cell0):
    """dyadic-ish grid of cell0-squares covering [x0,x1] x [y0,y1] exactly.
    Requires (x1-x0) and (y1-y0) to be integer multiples of cell0."""
    nx = (x1 - x0) / cell0
    ny = (y1 - y0) / cell0
    assert nx.denominator == 1 and ny.denominator == 1, (nx, ny)
    out = []
    for i in range(int(nx)):
        for j in range(int(ny)):
            out.append((x0 + i * cell0, y0 + j * cell0,
                        x0 + (i + 1) * cell0, y0 + (j + 1) * cell0))
    return out


def window_map(kind, configs, window, cell0=F(1, 8), min_cell=F(1, 64),
               mode='float', depth_max=26, max_boxes=3000, keeper=None,
               work_budget=100000, log=None):
    """Certified dead tiles inside `window` (a rational rect), uniformly over the
    bin, each passing the Lemma-K keeper.  Quadtree: mixed / alive cells are
    split down to min_cell then dropped."""
    keeper = keeper if keeper is not None else L.make_keeper(kind, configs)
    x0w, y0w, x1w, y1w = window
    margin = L.assert_margin(kind, (x0w, x1w, y0w, y1w))
    certs = L.certifiers(configs, mode, depth_max)
    placed_all = [cfg['placed'] for cfg in configs]
    area = F(0)
    cells = []
    n_pass = n_drop = n_occ = n_key = 0
    work = 0
    t0 = time.time()
    stack = rect_tiles(x0w, x1w, y0w, y1w, cell0)
    while stack:
        x0, y0, x1, y1 = stack.pop()
        w, h = x1 - x0, y1 - y0

        def split():
            xm, ym = x0 + w / 2, y0 + h / 2
            stack.extend([(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)])

        if not keeper(x0, y0, x1, y1):
            # cheap rejection: a tile DISJOINT from the keeper's own bbox can
            # never contribute, so it is dropped without refinement (sound --
            # dropping only lowers the area).
            kb = getattr(keeper, 'bbox', None)
            if kb is not None and (x1 <= kb[0] or x0 >= kb[2]
                                   or y1 <= kb[1] or y0 >= kb[3]):
                n_key += 1
            elif max(w, h) > min_cell:
                split()
            else:
                n_key += 1
            continue
        if any(all(P.strictly_inside(qx, qy, margin=0) for (qx, qy) in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1))) for pl in placed_all
               for P in pl):
            n_occ += 1
            continue
        if not all(_cell_disjoint_placed(x0, y0, x1, y1, pl) for pl in placed_all):
            if max(w, h) > min_cell:
                split()
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
            for (qx, qy) in ((xm, ym), (x0 + w / 4, y0 + h / 4),
                             (x1 - w / 4, y1 - h / 4), (x0 + w / 4, y1 - h / 4),
                             (x1 - w / 4, y0 + h / 4)):
                if any(c.quick_cover(qx, qy) for c in certs):
                    alive = True
                    break
        if not alive:
            alive = not L.region_ok_all(Region.rect(x0, y0, x1, y1), certs,
                                        max_boxes)
        if not alive:
            area += w * h
            cells.append((x0, y0, x1, y1))
            n_pass += 1
        elif max(w, h) > min_cell:
            split()
        else:
            n_drop += 1
    return dict(area=area, cells=cells,
                stats=dict(n_pass=n_pass, n_drop=n_drop, n_occ=n_occ,
                           n_key=n_key, work=work,
                           seconds=round(time.time() - t0, 2), margin=margin,
                           keeper=getattr(keeper, 'info', None)))


# --------------------------------------------------------------- utilities
def clip_area(cells, x0, y0, x1, y1):
    """exact area of the tile list inside the rational rect [x0,x1]x[y0,y1]."""
    a = F(0)
    out = []
    for (u0, v0, u1, v1) in cells:
        p0, p1 = max(u0, x0), min(u1, x1)
        q0, q1 = max(v0, y0), min(v1, y1)
        if p1 > p0 and q1 > q0:
            a += (p1 - p0) * (q1 - q0)
            out.append((p0, q0, p1, q1))
    return a, out


def radial_profile(cells, p, radii, y_floor=None):
    """exact area within SUP-distance r of p, for each r (tiles clipped)."""
    px, py = p
    prof = {}
    for r in radii:
        y0 = py - r if y_floor is None else max(py - r, y_floor)
        a, _ = clip_area(cells, px - r, y0, px + r, py + r)
        prof[str(r)] = a
    return prof
