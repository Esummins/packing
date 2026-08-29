#!/usr/bin/env python3
"""A47 leg (b) TABLE (i) -- the CORNER primitive table.

Container [0,s0]^2, reference corner at the ORIGIN.  Hypothesis: ONE unit square
with centre in a position cell of [49/100, 11/10]^2 (the A21 corner occupancy
zone, enlarged to cover the s0/3.88 scale-back of A21's normalised frame) and
tilt in a degree bin of [0,45], PLACEMENT-UNIFORM over the whole cell x bin.

Grid: 3 x 3 position cells x 6 tilt bins = 54 entries.  ALL NINE cells are
computed, because the container's diagonal symmetry sigma:(x,y)->(y,x) maps
(cellA, cellB, theta-bin) to (cellB, cellA, 90 - theta bin) -- it does NOT fix
the theta bin, so the 9 x 6 grid over theta in [0,45] has no internal
redundancy.  It is exactly what a consumer needs: a square with tilt
theta in (45,90) is sigma-mapped to (cellY, cellX, 90 - theta) with
90 - theta in [0,45].  The delta-indexed table (delta = dist(theta, 90 Z)) is
derived exactly afterwards by intersecting the two theta-components.

Checkpoint per entry in work/corner/<id>.json (skipped on rerun).
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as F

import a47_lib as L

WORKD = os.path.join(L.WORK, 'corner')


def run_entry(ix, iy, ib, force=False):
    eid = 'C_%s_%s_%s' % (L.XNAMES[ix], L.XNAMES[iy], L.CORNER_BIN_NAMES[ib])
    path = os.path.join(WORKD, eid + '.json')
    if os.path.exists(path) and not force:
        return json.load(open(path))
    xc, yc, db = L.XCELLS[ix], L.XCELLS[iy], L.CORNER_BINS[ib]
    cfg, info = L.build_configs(xc, yc, db)
    rec = dict(id=eid, table='corner', ix=ix, iy=iy, ib=ib,
               x_cell=[str(xc[0]), str(xc[1])], y_cell=[str(yc[0]), str(yc[1])],
               tilt_bin_deg=[str(db[0]), str(db[1])],
               feasibility=info)
    if not cfg:
        rec.update(status='INFEASIBLE', area_exact='0', area_float=0.0,
                   n_tiles=0, radial={}, cells=[])
        L.save(path, rec)
        return rec
    t0 = time.time()
    r = L.dead_map(cfg, (F(0), F(0), L.WIN, L.WIN), mode='float')
    cfg2, _ = L.build_configs(xc, yc, db)
    e = L.recert_tiles(cfg2, r['cells'])
    rec.update(status='OK',
               area_float_map=str(r['area']), area_float_map_f=float(r['area']),
               area_exact=str(e['area']), area_float=float(e['area']),
               n_tiles=len(e['cells']), n_failed=len(e['failed']),
               failed=e['failed'],
               radial={k: str(v) for k, v in L.radial_corner(e['cells']).items()},
               radial_f={k: float(v) for k, v in L.radial_corner(e['cells']).items()},
               stats=r['stats'], recert_seconds=e['seconds'],
               seconds=round(time.time() - t0, 2),
               cells=L.jcells(L.merge_rects(e['cells'])),
               cells_raw=L.jcells(e['cells']))
    L.save(path, rec)
    return rec


def main():
    os.makedirs(WORKD, exist_ok=True)
    sel = sys.argv[1] if len(sys.argv) > 1 else 'all'
    todo = []
    for ix in range(3):
        for iy in range(3):
            for ib in range(6):
                todo.append((ix, iy, ib))
    if sel == 'even':
        todo = [t for i, t in enumerate(todo) if i % 2 == 0]
    elif sel == 'odd':
        todo = [t for i, t in enumerate(todo) if i % 2 == 1]
    for (ix, iy, ib) in todo:
        r = run_entry(ix, iy, ib)
        print('%-22s %-12s area=%s  tiles=%s  %ss'
              % (r['id'], r['status'], r.get('area_float'), r.get('n_tiles'),
                 r.get('seconds')), flush=True)


if __name__ == '__main__':
    main()
