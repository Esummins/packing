#!/usr/bin/env python3
"""
pair_sliver.py -- task 2b: the sliver between two adjacent tilted squares of the
A12 quarter-pinwheel (interior support of results/analysis_s3.86.json), realised
as ACTUAL disjoint placements (the fractional 4-cycle overlaps by ~2e-4; we
separate along the SAT axis and rationalise), s = 3.86.

Also: ledger configs (task 3):
  --config pair        : the two adjacent pinwheel squares alone
  --config corner_tilt : one tilted square in A14's alive on-corner box
                         (centre (0.65,0.65), theta 40deg approx) at s = 3.85
  --config corners4    : the four exact corner squares at 3.85 (A14 x_corners4)
  --config tenpack     : 4 corners + 4 side uprights + 1 tilted + 1 interior
                         upright (A12's alpha=10 independent set) at 3.86,
                         windowed over the WHOLE container.
"""
import argparse
import json
import math
from fractions import Fraction as F

import numpy as np

from dead_region import Placed, PlacedBox, Certifier, cos_sin, _sat_gap, _convex_interior_disjoint
from wastage import dead_map, save

T33 = F(296213, 1000000)          # tan(16.5 deg): theta = 33.0000 deg (to 5e-5)
T05 = F(4363, 1000000)            # tan(0.25 deg): theta = 0.4999 deg
T40 = F(363970, 1000000)          # tan(20 deg):   theta = 40.000 deg
S386 = F(193, 50)
S385 = F(77, 20)


def fgap(P, Q):
    A = np.array([[float(x), float(y)] for (x, y) in P.corners])
    B = np.array([[float(x), float(y)] for (x, y) in Q.corners])
    return _sat_gap(A, float(P.c), float(P.s), B, float(Q.c), float(Q.s))


def sep_pair():
    """the two adjacent pinwheel squares, exactly disjoint (rational)."""
    # A12 images (float): (2.4597004, 2.5404858, 33deg) and its C4 rotation
    # (1.3195142, 2.4597004, 33deg).  They overlap by ~2e-4 (4-cycle).  Push the
    # second one away along the centre-to-centre direction until the exact SAT
    # gap is >= 0, then rationalise.
    a = Placed(F(2459700, 1000000), F(2540486, 1000000), T33)
    for k in range(60):
        off = F(k, 2000)          # 0.0005 steps
        b = Placed(F(1319514, 1000000) - off, F(2459700, 1000000) - off, T33)
        if _convex_interior_disjoint(a.corners, b.corners):
            return a, b, float(off)
    raise RuntimeError("could not separate")



def clamp_admissible(P, s):
    """return a Placed with the same t whose centre is clamped into [w/2, s-w/2]^2."""
    from dead_region import cos_sin
    c, sn = cos_sin(P.t)
    h = (c + sn) / 2
    cx = min(max(P.cx, h), F(s) - h)
    cy = min(max(P.cy, h), F(s) - h)
    return Placed(cx, cy, P.t)


def config(name):
    if name == 'pair':
        a, b, off = sep_pair()
        print(f"pair separated by off={off}, float gap={fgap(a, b):.6f}")
        # window around the contact zone: bbox of the two centres +- 1.1
        cx = (float(a.cx) + float(b.cx)) / 2
        cy = (float(a.cy) + float(b.cy)) / 2
        win = (F(int((cx - 1.45) * 100), 100), F(int((cx + 1.45) * 100), 100),
               F(int((cy - 1.45) * 100), 100), S386)   # shadow reaches the top wall
        return [a, b], win, S386, dict(kind='pair', s='193/50', off=off)
    if name == 'corner_tilt':
        # A14 alive on-corner node representative: centre in [0.5,0.8]^2, theta 40deg.
        # w(40deg)/2 = 0.70457 so the centre must be >= that: use (0.72, 0.72)
        # (corner gap d = 0.0154 to both walls).
        P = Placed(F(18, 25), F(18, 25), T40)
        win = (F(0), F(21, 10), F(0), F(21, 10))
        return [P], win, S385, dict(kind='corner_tilt', s='77/20', theta=40,
                                    centre='0.72')
    if name == 'pinwheel4':
        # the full 33-deg pinwheel 4-cycle of A12's s=3.86 interior support:
        # ALREADY pairwise exactly disjoint at the raw rational coordinates
        # (the 2e-4 overlaps are between the 33 and 32-deg sub-orbits).
        s = S386
        placed = [Placed(*p) for p in (
            (F(2459700, 1000000), F(2540486, 1000000), T33),
            (s - F(2540486, 1000000), F(2459700, 1000000), T33),
            (s - F(2459700, 1000000), s - F(2540486, 1000000), T33),
            (F(2540486, 1000000), s - F(2459700, 1000000), T33))]
        for i in range(4):
            for j in range(i + 1, 4):
                assert _convex_interior_disjoint(placed[i].corners, placed[j].corners)
        win = (F(0), s, F(0), s)
        return placed, win, s, dict(kind='pinwheel4', s='193/50')
    if name == 'pair_box':
        # CONTINUUM version of the pair: two core BOXES around the adjacent
        # pinwheel placements (cx,cy +- 0.01, theta 33 +- 1 deg); a dead
        # certificate holds for EVERY pair of placements in the two cores.
        t0, t1 = F(287000, 1000000), F(305500, 1000000)   # tan(16deg)..tan(17deg) ~ 32..34deg
        d = F(1, 100)
        ax, ay = F(2459700, 1000000), F(2540486, 1000000)
        bx, by = F(1319514, 1000000), F(2459700, 1000000)
        A = PlacedBox(t0, t1, ax - d, ax + d, ay - d, ay + d)
        B = PlacedBox(t0, t1, bx - d, bx + d, by - d, by + d)
        win = (F(73, 100), F(303, 100), F(135, 100), S386)
        return [A, B], win, S386, dict(kind='pair_box', s='193/50',
                                       core='centres +-0.01, theta in [32.1,33.9]deg')
    if name == 'pinwheel4_sp':
        # pinwheel4 rescaled to s' = 3.8770836 (Trump side, optimality frame):
        # centres scaled by s'/3.86 (gaps scale up: still exactly disjoint; re-checked).
        sp = F(38770836, 10000000)
        lam = sp / S386
        base = [(F(2459700, 1000000), F(2540486, 1000000)),
                (S386 - F(2540486, 1000000), F(2459700, 1000000)),
                (S386 - F(2459700, 1000000), S386 - F(2540486, 1000000)),
                (F(2540486, 1000000), S386 - F(2459700, 1000000))]
        placed = [Placed((x * lam).limit_denominator(10 ** 7),
                         (y * lam).limit_denominator(10 ** 7), T33) for (x, y) in base]
        for i in range(4):
            for j in range(i + 1, 4):
                assert _convex_interior_disjoint(placed[i].corners, placed[j].corners)
        win = (F(0), sp, F(0), sp)
        return placed, win, sp, dict(kind='pinwheel4_sp', s="3.8770836")
    if name == 'corner_box':
        # CORE-BOX-UNIFORM version of corner_tilt: the A14 YES-node hypothesis
        # "some square has centre in [0.72,0.74]^2 and theta in [39,41]deg"
        # (a refined child of A14's alive node [0.5,0.8]^2 x [30,60]deg; the
        # admissible part at 40deg forces cx, cy >= w/2 = 0.7046).
        B = PlacedBox(F(354119, 1000000), F(373885, 1000000),
                      F(18, 25), F(37, 50), F(18, 25), F(37, 50))
        win = (F(0), F(21, 10), F(0), F(21, 10))
        return [B], win, S385, dict(kind='corner_box', s='77/20',
                                    core='[0.72,0.74]^2 x [39,41]deg')
    if name == 'corners4':
        s = S385
        placed = [Placed(F(1, 2), F(1, 2), 0), Placed(s - F(1, 2), F(1, 2), 0),
                  Placed(s - F(1, 2), s - F(1, 2), 0), Placed(F(1, 2), s - F(1, 2), 0)]
        win = (F(0), s, F(0), F(6, 5))            # bottom strip (D4 symmetry: x4 NOT taken)
        return placed, win, s, dict(kind='corners4', s='77/20', note='bottom strip only')
    if name == 'tenpack':
        s = S386
        placed = [Placed(F(1, 2), F(1, 2), 0), Placed(s - F(1, 2), F(1, 2), 0),
                  Placed(s - F(1, 2), s - F(1, 2), 0), Placed(F(1, 2), s - F(1, 2), 0)]
        # A12 side uprights: mixed positions found by exact search (see notes):
        # right/top/bottom = HIGH flush position (3.36, 2.3243, 0deg)-orbit,
        # left = LOW position (0.504, 2.257, 0.5deg); tilted = 32deg image
        # (1.38396, 1.33050); interior upright (2.35513, 2.35613, 0.5deg).
        sy = F(2324324, 1000000)
        placed += [Placed(s - F(1, 2), sy, 0),            # right wall
                   Placed(s - sy, s - F(1, 2), 0),        # top wall
                   Placed(s - F(3356000, 1000000), s - F(1603000, 1000000), T05),  # left
                   Placed(sy, F(1, 2), 0)]                # bottom wall
        T32 = F(286745, 1000000)
        placed += [Placed(s - F(2476039, 1000000), s - F(2529499, 1000000), T32),
                   Placed(F(2355132, 1000000), F(2356134, 1000000), T05)]
        placed = [clamp_admissible(P, s) for P in placed]
        # exact pairwise disjointness check (after clamping)
        n = len(placed)
        for i in range(n):
            for j in range(i + 1, n):
                assert _convex_interior_disjoint(placed[i].corners, placed[j].corners), (i, j)
        win = (F(0), s, F(0), s)
        return placed, win, s, dict(kind='tenpack', s='193/50')
    raise ValueError(name)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='pair')
    ap.add_argument('--min_cell', type=int, default=64)
    ap.add_argument('--cell0_num', type=int, default=4)
    args = ap.parse_args()
    placed, win, s, meta = config(args.config)
    res = dead_map(placed, s, win, cell0=F(args.cell0_num, 25),
                   min_cell=F(1, args.min_cell), mode='float',
                   depth_max=24, max_boxes_per_cell=1500)
    res['meta'] = meta
    save(f"results/{args.config}.json", res)
    print(json.dumps(dict(config=args.config, area=res['area_float']), indent=1))
