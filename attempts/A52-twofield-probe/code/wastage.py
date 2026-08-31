#!/usr/bin/env python3
"""
wastage.py -- quadtree dead-area mapper on top of dead_region.Certifier.

dead_map(placed, s, window, ...) certifies dead area cell-by-cell:
  * cells are axis-aligned squares with DYADIC rational corners (so the identical
    cell list can be re-certified in exact mode later);
  * a cell counts only if it is interior-disjoint from every placed square
    (exact SAT check) -- dead area must be EMPTY area for the budget lemma;
  * a cell counts as dead only if the certifier PASSes on it (mode float by
    default: fast map; mode exact: certificate);
  * failing / mixed cells are split down to min_cell and then dropped
    => the reported area is a (mode-)certified LOWER bound on the dead area.

Union soundness: a point x is dead iff no legal Q covers x; cell PASS means no
legal Q meets the cell, i.e. every point of the cell is dead; unions of dead
cells are dead, and interior-disjoint from each other and from the placed
squares, so the areas add in the budget lemma.
"""
from __future__ import annotations

import json
import time
from fractions import Fraction as F

from dead_region import Certifier, Region, _convex_interior_disjoint


def _cell_disjoint_placed(x0, y0, x1, y1, placed):
    verts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for P in placed:
        if hasattr(P, 'cell_interior_disjoint'):
            if not P.cell_interior_disjoint(verts):
                return False
        elif not _convex_interior_disjoint(verts, P.corners):
            return False
    return True


def dead_map(placed, s, window, cell0=F(4, 25), min_cell=F(1, 64), mode='float',
             depth_max=30, max_boxes_per_cell=1500, verbose=True, certifier=None, nozones=()):
    """window = (x0, x1, y0, y1) rationals.  Returns dict with certified cells + area."""
    cert = certifier or Certifier(s, placed, mode=mode, depth_max=depth_max, nozones=nozones)
    for P in placed:      # placed squares must be inside the container (exact)
        if hasattr(P, 'cell_interior_disjoint'):
            continue          # PlacedBox: `corners` is an AABB HULL, may stick out; admissibility handled by _clip
        for (px, py) in P.corners:
            assert 0 <= px <= F(s) and 0 <= py <= F(s), "placed square outside container"
    X0, X1, Y0, Y1 = [F(v) for v in window]
    # initial grid of cell0 cells covering the window (dyadic-friendly: use cell0 steps)
    cells = []
    nx = int((X1 - X0) / cell0) + 1
    ny = int((Y1 - Y0) / cell0) + 1
    stack = []
    for i in range(nx):
        for j in range(ny):
            cx0, cy0 = X0 + i * cell0, Y0 + j * cell0
            cx1, cy1 = min(cx0 + cell0, X1), min(cy0 + cell0, Y1)
            if cx1 > cx0 and cy1 > cy0:
                stack.append((cx0, cy0, cx1, cy1))
    area = F(0)
    n_pass = n_drop = n_occ = 0
    t_start = time.time()
    while stack:
        x0, y0, x1, y1 = stack.pop()
        w = x1 - x0
        h = y1 - y0
        if any(all(P.strictly_inside(px, py, margin=0) for (px, py) in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1))) for P in placed):
            n_occ += 1
            continue
        if not _cell_disjoint_placed(x0, y0, x1, y1, placed):
            if max(w, h) > min_cell:
                xm, ym = x0 + w / 2, y0 + h / 2
                stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)]
            else:
                n_occ += 1
            continue
        # cheap negative probe: a legal placement covering an interior point => not dead
        probe_fail = False
        if mode == 'float':
            xm, ym = x0 + w / 2, y0 + h / 2
            for (qx, qy) in ((xm, ym), (x0 + w / 4, y0 + h / 4), (x1 - w / 4, y1 - h / 4),
                             (x0 + w / 4, y1 - h / 4), (x1 - w / 4, y0 + h / 4)):
                if cert.quick_cover(qx, qy):
                    probe_fail = True
                    break
        if probe_fail:
            if max(w, h) > min_cell:
                xm, ym = x0 + w / 2, y0 + h / 2
                stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)]
            else:
                n_drop += 1
            continue
        D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        r = cert.certify(D, max_boxes=max_boxes_per_cell)
        if r['passed']:
            area += D.area
            cells.append([str(x0), str(y0), str(x1), str(y1)])
            n_pass += 1
        elif max(w, h) > min_cell:
            xm, ym = x0 + w / 2, y0 + h / 2
            stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                      (x0, ym, xm, y1), (xm, ym, x1, y1)]
        else:
            n_drop += 1
    dt = time.time() - t_start
    if verbose:
        print(f"  dead_map: area={float(area):.6f} pass={n_pass} drop={n_drop} "
              f"occluded={n_occ} {dt:.0f}s")
    return dict(area=str(area), area_float=float(area), cells=cells,
                n_pass=n_pass, n_drop=n_drop, seconds=dt)


def recheck_exact(placed, s, cells, depth_max=42, max_boxes_per_cell=300000, verbose=True, nozones=()):
    """re-certify a float-mapped cell list in exact mode; returns exact-certified area."""
    cert = Certifier(s, placed, mode='exact', depth_max=depth_max, nozones=nozones)
    area = F(0)
    failed = []
    t0 = time.time()
    for (x0, y0, x1, y1) in cells:
        x0, y0, x1, y1 = F(x0), F(y0), F(x1), F(y1)
        D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        r = cert.certify(D, max_boxes=max_boxes_per_cell)
        if r['passed']:
            area += D.area
        else:
            failed.append([str(x0), str(y0), str(x1), str(y1), str(r.get('witness'))])
    dt = time.time() - t0
    if verbose:
        print(f"  recheck_exact: area={float(area):.6f} of {len(cells)} cells, "
              f"{len(failed)} failed, {dt:.0f}s")
    return dict(area=str(area), area_float=float(area), n_cells=len(cells),
                failed=failed, seconds=dt)


def save(path, obj):
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1)
