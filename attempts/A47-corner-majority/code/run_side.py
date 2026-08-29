#!/usr/bin/env python3
"""A47 leg (b) TABLE (ii) -- the SIDE (left-wall) primitive table.

Reference wall x = 0 of the container [0,s0]^2.  Hypothesis: ONE unit square
with centre in [49/100, 11/10] x (a cy cell of [109/100, 139/50]) and tilt in a
degree bin of [0,45], PLACEMENT-UNIFORM.

REFINEMENT (recorded as a judgment call).  The brief's two COARSE cy cells
[109/100, 9/5] and [9/5, 139/50] are 0.71 and 0.98 tall.  A tile counts only if
it is dead for EVERY placement of the hypothesis, and over a 0.7-tall centre
range no tile in the window survives: a pilot at cx=[7/10,9/10],
cy=[109/100,9/5], tilt (15,45] certifies EXACTLY 0.  So the table is computed on
SEVEN refined cy cells of height 0.21-0.25, and the coarse-cell entry is derived
EXACTLY afterwards as the intersection of the refined dead sets (Dead(coarse)
= intersection over sub-cells of Dead(sub-cell), because the coarse hypothesis
is the union of the sub-cell hypotheses).  The composition-relevant number is
`min over sub-cells`, which is what a "the square is somewhere in the side zone"
premise licenses.

Window: [0, 13/8] x [cy_lo - 13/8, cy_hi + 13/8], clipped to the container.
Keeper: x <= 13/8, certified dead, interior-disjoint from every placement.
Radial profile: tile area with x <= r, r in {1/2, 3/4, 1, 5/4, 13/8}.

Checkpoint per entry in work/side/<id>.json.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as F

import a47_lib as L

WORKD = os.path.join(L.WORK, 'side')

YCELLS = [(F(109, 100), F(13, 10)), (F(13, 10), F(31, 20)), (F(31, 20), F(9, 5)),
          (F(9, 5), F(41, 20)), (F(41, 20), F(23, 10)), (F(23, 10), F(127, 50)),
          (F(127, 50), F(139, 50))]
YNAMES = ['c%d' % i for i in range(7)]
# refined cells c0..c2 tile the brief's coarse cell [109/100, 9/5];
# c3..c6 tile the brief's coarse cell [9/5, 139/50].
COARSE = {'Y0': [0, 1, 2], 'Y1': [3, 4, 5, 6]}
NSUB = {0: 4, 1: 4, 2: 6}          # per SIDE_BINS index
WORK_BUDGET = 5000                 # cost cap; overflow tiles are DROPPED (sound)


def run_entry(ix, iy, ib, force=False):
    eid = 'S_%s_%s_%s' % (L.XNAMES[ix], YNAMES[iy], L.SIDE_BIN_NAMES[ib])
    path = os.path.join(WORKD, eid + '.json')
    if os.path.exists(path) and not force:
        return json.load(open(path))
    xc, yc, db = L.XCELLS[ix], YCELLS[iy], L.SIDE_BINS[ib]
    cfg, info = L.build_configs(xc, yc, db, nsub=NSUB[ib])
    win = (F(0), max(F(0), yc[0] - L.WIN), L.WIN, min(L.S0, yc[1] + L.WIN))
    rec = dict(id=eid, table='side', ix=ix, iy=iy, ib=ib,
               x_cell=[str(xc[0]), str(xc[1])], y_cell=[str(yc[0]), str(yc[1])],
               tilt_bin_deg=[str(db[0]), str(db[1])],
               window=[str(v) for v in win], feasibility=info)
    if not cfg:
        rec.update(status='INFEASIBLE', area_exact='0', area_float=0.0,
                   n_tiles=0, radial={}, cells=[])
        L.save(path, rec)
        return rec
    t0 = time.time()
    r = L.dead_map(cfg, win, mode='float', work_budget=WORK_BUDGET)
    cfg2, _ = L.build_configs(xc, yc, db, nsub=NSUB[ib])
    e = L.recert_tiles(cfg2, r['cells'])
    rec.update(status='OK',
               area_float_map=str(r['area']), area_float_map_f=float(r['area']),
               area_exact=str(e['area']), area_float=float(e['area']),
               n_tiles=len(e['cells']), n_failed=len(e['failed']),
               failed=e['failed'],
               radial={k: str(v) for k, v in L.radial_wall(e['cells']).items()},
               radial_f={k: float(v) for k, v in L.radial_wall(e['cells']).items()},
               stats=r['stats'], recert_seconds=e['seconds'],
               seconds=round(time.time() - t0, 2),
               cells=L.jcells(L.merge_rects(e['cells'])),
               cells_raw=L.jcells(e['cells']))
    L.save(path, rec)
    return rec


def main():
    os.makedirs(WORKD, exist_ok=True)
    sel = sys.argv[1] if len(sys.argv) > 1 else 'all'
    todo = [(ix, iy, ib) for ib in range(3) for ix in range(3) for iy in range(7)]
    if sel == 'even':
        todo = [t for i, t in enumerate(todo) if i % 2 == 0]
    elif sel == 'odd':
        todo = [t for i, t in enumerate(todo) if i % 2 == 1]
    for (ix, iy, ib) in todo:
        r = run_entry(ix, iy, ib)
        print('%-22s %-12s area=%s tiles=%s %ss'
              % (r['id'], r['status'], r.get('area_float'), r.get('n_tiles'),
                 r.get('seconds')), flush=True)


if __name__ == '__main__':
    main()
