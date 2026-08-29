#!/usr/bin/env python3
"""A47 leg (b) TASK (iii) -- PAIR-IN-CORNER PILOT (float-first, exploratory).

Patterned on A23 notes 4c (the pinwheel near-tangency pair, whose realised
shadow was 1.88 for a FIXED pair and 1.38 for the continuum-core version).
Here the pair is anchored at a container CORNER:

  square a : centre in [7/10, 9/10]^2, tilt in (30, 45]   (the A47 corner cell
             x1 x x1 at the strongest tilt bin)
  square b : centre in a + (21/20, 21/20), i.e. [7/4, 39/20]^2, tilt in (30,45]
             INDEPENDENTLY of a  --  "adjacent along the diagonal".

The diagonal offset 21/20 is the smallest that makes EVERY placement pair of the
two boxes provably interior-disjoint (see `legality`): the SAT projection of the
centre offset on a's axis must exceed 1/2 + (|cos D| + |sin D|)/2 with
D = theta_b - theta_a the relative tilt, which the 21/20 offset clears with
margin.  A smaller offset (the true corner-to-corner tangency, ~0.72) would put
overlapping configurations inside the hypothesis box and make the primitive
vacuous.

nsub = 3 per square (5-deg sub-bins), so 9 PlacedBox pairs; a tile counts only
if it certifies on all 9.  Window [0, 5/2]^2.  FLOAT map; exact re-certification
is run ONLY if the float area exceeds 1.0 (per the brief).
"""
from __future__ import annotations

import json
import math
import os
import time
from fractions import Fraction as F

from dead_region import PlacedBox
from atlas_lib import _mid_corners

import a47_lib as L

ACELL = (F(7, 10), F(9, 10))
OFFSET = F(21, 20)
BCELL = (ACELL[0] + OFFSET, ACELL[1] + OFFSET)
BIN = (F(30), F(45))
NSUB = 3
WINDOW = (F(0), F(0), F(5, 2), F(5, 2))


def legality():
    """min over the hypothesis of (offset projection on a's axes) minus the
    required separation 1/2 + (|cos D| + |sin D|)/2.  > 0 => every placement
    pair of the two boxes is interior-disjoint.  Floats (diagnostic)."""
    off_lo = float(BCELL[0] - ACELL[1])          # min per-axis centre offset
    worst = None
    for i in range(NSUB):
        for j in range(NSUB):
            a0 = float(BIN[0]) + (float(BIN[1]) - float(BIN[0])) * i / NSUB
            a1 = float(BIN[0]) + (float(BIN[1]) - float(BIN[0])) * (i + 1) / NSUB
            b0 = float(BIN[0]) + (float(BIN[1]) - float(BIN[0])) * j / NSUB
            b1 = float(BIN[0]) + (float(BIN[1]) - float(BIN[0])) * (j + 1) / NSUB
            wmin = min(math.cos(math.radians(t)) + math.sin(math.radians(t))
                       for t in (a0, a1))
            dmax = max(abs(b1 - a0), abs(b0 - a1))
            need = 0.5 + (abs(math.cos(math.radians(dmax)))
                          + abs(math.sin(math.radians(dmax)))) / 2
            slack = off_lo * wmin - need
            if worst is None or slack < worst[0]:
                worst = (slack, (a0, a1), (b0, b1))
    return dict(min_offset_per_axis=off_lo, worst_slack=worst[0],
                worst_subbins=[list(worst[1]), list(worst[2])],
                legal=bool(worst[0] > 0))


def build():
    out = []
    for i in range(NSUB):
        d0 = BIN[0] + (BIN[1] - BIN[0]) * F(i, NSUB)
        d1 = BIN[0] + (BIN[1] - BIN[0]) * F(i + 1, NSUB)
        ta0, ta1 = L.deg_t(d0, d1)
        lo = L.wlo_of(ta0, ta1) / 2
        ax0, ay0 = max(ACELL[0], lo), max(ACELL[0], lo)
        if ax0 > ACELL[1]:
            continue
        A = PlacedBox(ta0, ta1, ax0, ACELL[1], ay0, ACELL[1])
        A.filter_corners = _mid_corners(A)
        for j in range(NSUB):
            e0 = BIN[0] + (BIN[1] - BIN[0]) * F(j, NSUB)
            e1 = BIN[0] + (BIN[1] - BIN[0]) * F(j + 1, NSUB)
            tb0, tb1 = L.deg_t(e0, e1)
            B = PlacedBox(tb0, tb1, BCELL[0], BCELL[1], BCELL[0], BCELL[1])
            B.filter_corners = _mid_corners(B)
            out.append(dict(placed=[A, B], deg=(d0, d1), deg_b=(e0, e1)))
    return out


def main():
    t0 = time.time()
    lg = legality()
    cfg = build()
    r = L.dead_map(cfg, WINDOW, mode='float', work_budget=8000)
    a_f = float(r['area'])
    rec = dict(what='A47 leg (b) task (iii): pair-in-corner pilot',
               status='FLOAT',
               a_cell=[str(ACELL[0]), str(ACELL[1])],
               b_cell=[str(BCELL[0]), str(BCELL[1])],
               diagonal_offset=str(OFFSET),
               tilt_bin_deg=[str(BIN[0]), str(BIN[1])],
               tilts_independent=True, nsub_per_square=NSUB,
               n_configs=len(cfg),
               window=[str(v) for v in WINDOW],
               cell0=str(L.CELL0), min_cell=str(L.MIN_CELL),
               legality_check=lg,
               area_float=str(r['area']), area_float_f=a_f,
               n_tiles=len(r['cells']), stats=r['stats'],
               radial={k: str(v) for k, v in L.radial_corner(r['cells']).items()},
               radial_f={k: float(v) for k, v in
                         L.radial_corner(r['cells']).items()},
               cells_FLOAT_ONLY=L.jcells(L.merge_rects(r['cells'])),
               exact_recert_rule='exact recertification run only if float area '
                                 '> 1.0 (brief)',
               exact_recert_run=False)
    if a_f > 1.0:
        cfg2 = build()
        e = L.recert_tiles(cfg2, r['cells'])
        rec.update(status='EXACT', exact_recert_run=True,
                   area_exact=str(e['area']), area_exact_f=float(e['area']),
                   n_failed=len(e['failed']), recert_seconds=e['seconds'],
                   cells_EXACT=L.jcells(L.merge_rects(e['cells'])))
    rec['seconds'] = round(time.time() - t0, 2)
    L.save(os.path.join(L.RES, 'pair_pilot.json'), rec)
    print(json.dumps({k: v for k, v in rec.items()
                      if 'cells' not in k}, indent=1))


if __name__ == '__main__':
    main()
