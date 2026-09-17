"""A253: the FLUSH LIMIT of the all-ADJ ring (tau -> 0) and the room in it -- proved, not searched.

The minimum-tilt question has an exact answer at its boundary.  Along the pinwheel sign pattern
sigma = 00110011 (A249's ring: corners BL, TR with both tilts near 0, corners BR, TL with both near
90 deg) every parameter tends, as tau -> 0, to an axis-aligned limit, and the limit ring is the
FOUR-CORNER DOMINO PINWHEEL (A226's crowd structure, A250's corner dominoes) at side s:

    wall x = 0 :  [0, 1] x [1, 2]            and  [0, 1] x [2, 3]              (one 1 x 2 block)
    wall y = 0 :  [s-3, s-2] x [0, 1]        and  [s-2, s-1] x [0, 1]
    wall x = s :  [s-1, s] x [s-3, s-2]      and  [s-1, s] x [s-2, s-1]
    wall y = s :  [1, 2] x [s-1, s]          and  [2, 3] x [s-1, s]

(the two squares of a wall touch; the limit is a boundary point of the family -- each corner box is
met by ONE square only, so it is not itself all-ADJ).  Its pocket splits EXACTLY into

    the central hole  [1, s-1]^2,  a square of side s - 2 < 2,
    four dead notches  1 x (s - 3),  each isolated, each too narrow for a unit square (s < 4),

and the slot-overlap RIBBON [0, 1] x [s-2, 2] of the wall x = 0 lies inside the wall block
[0, 1] x [1, 3]: in the limit the ring's own touchers close the ribbon and the POKER dies.  That is
the PI's mechanism, at tau = 0 exactly.

[T] Lemma HOLE-ONE (any n).  In a square container of side sigma <= 2 every unit square contains
the container centre, so at most ONE fits.  Proof: a unit square of tilt theta inside [0, sigma]^2
has centre q in [w/2, sigma - w/2]^2 with w = cos theta + sin theta; for the container centre p and
either edge direction u of the square, |(p - q).u| <= ((sigma - w)/2) w <= 1/2, because
(2 - w) w <= 1 for all w (equivalently (w - 1)^2 >= 0).  []

[T] Lemma NOTCH-NARROW (any n).  A unit square has width >= 1 in every direction, so it does not
fit in a rectangle with a side < 1; the limit notches have side s - 3 < 1 for s < 4.  []

Hence the flush-limit ring's pocket has capacity EXACTLY 1 (the central hole has side s - 2 >= 1.82
on the window, so one square does fit): 8 + 1 = 9 < 11, with no search at all.

    python limit253.py [--sides 3.82,3.877084,3.99]   -> results/limit253.json
"""
import argparse
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom253 as Z                                                   # noqa: E402
import geom237 as G237                                                # noqa: E402
import cert253 as CT                                                  # noqa: E402

RES = os.path.join(ATT, 'results')


def limit_ring(s):
    """the eight axis-aligned limit squares as rational rectangles (x0, x1, y0, y1)."""
    one, two, three = Fr(1), Fr(2), Fr(3)
    return [(Fr(0), one, one, two), (Fr(0), one, two, three),
            (s - three, s - two, Fr(0), one), (s - two, s - one, Fr(0), one),
            (s - one, s, s - three, s - two), (s - one, s, s - two, s - one),
            (one, two, s - one, s), (two, three, s - one, s)]


def names():
    return ['B_BL', 'B_TL', 'A_BL', 'A_BR', 'B_BR', 'B_TR', 'A_TL', 'A_TR']


def rect_pts(r):
    x0, x1, y0, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def verify(s_float):
    """exact checks on the limit ring at side s: unit squares, contained, interior-disjoint, the
    pocket decomposition, and the ribbon covered by the wall block."""
    s = Fr(round(s_float * 10 ** 6), 10 ** 6)
    R = limit_ring(s)
    out = {'side': float(s), 'unit': all(r[1] - r[0] == 1 and r[3] - r[2] == 1 for r in R),
           'contained': all(0 <= r[0] and r[1] <= s and 0 <= r[2] and r[3] <= s for r in R)}
    gaps = [CT.exact_gap(rect_pts(R[i]), rect_pts(R[j])) for i in range(8) for j in range(i)]
    out['min_gap'] = float(min(gaps))
    out['disjoint'] = bool(min(gaps) >= 0)
    # the ribbon of each wall is inside that wall's 1 x 2 block
    blocks = {0: (Fr(0), Fr(1), Fr(1), Fr(3)), 1: (s - 3, s - 1, Fr(0), Fr(1)),
              2: (s - 1, s, s - 3, s - 1), 3: (Fr(1), Fr(3), s - 1, s)}
    rib = {w: CT.ribbon(s, w) for w in range(4)}
    out['ribbon_in_block'] = {w: bool(blocks[w][0] <= rib[w][0] and rib[w][1] <= blocks[w][1]
                                      and blocks[w][2] <= rib[w][2] and rib[w][3] <= blocks[w][3])
                              for w in range(4)}
    out['ribbon'] = {w: [float(v) for v in rib[w]] for w in range(4)}
    # the pocket, exactly
    hole = (Fr(1), s - 1, Fr(1), s - 1)
    notch = [(Fr(0), s - 3, Fr(0), Fr(1)), (s - 1, s, Fr(0), s - 3),
             (Fr(3), s, s - 1, s), (Fr(0), Fr(1), Fr(3), s)]
    out['hole_side'] = float(s - 2)
    out['notch_dims'] = [[float(n[1] - n[0]), float(n[3] - n[2])] for n in notch]
    out['area_check'] = float(hole_area(hole) + sum(hole_area(n) for n in notch) - (s * s - 8))
    # cross-check against shapely
    P = G237.pocket([((r[0] + r[1]) / 2, (r[2] + r[3]) / 2, 0.0) for r in
                     [[float(v) for v in q] for q in R]], float(s))
    parts = sorted((p.area for p in G237.polys_of(P)), reverse=True)
    out['shapely_components'] = [float(a) for a in parts]
    out['shapely_pocket_area'] = float(P.area)
    out['capacity_le_1'] = bool(s - 2 <= 2)
    out['hole_one_slack'] = float(min(2 - (s - 2), Fr(1)))
    out['notch_narrow'] = bool(s - 3 < 1)
    out['capacity'] = 1 if (s - 2 >= 1 and s - 2 <= 2) else None
    return out


def hole_area(r):
    return (r[1] - r[0]) * (r[3] - r[2])


def hole_one_check(sigma, grid=901):
    """[M] Lemma HOLE-ONE, measured: over the tilts, max |(p - q).u| for the worst admissible q."""
    worst = 0.0
    for k in range(grid):
        th = (k / (grid - 1)) * math.pi / 2
        w = math.cos(th) + math.sin(th)
        if sigma - w < 0:
            continue
        worst = max(worst, 0.5 * (sigma - w) * w)
    return worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sides', default='3.82,3.877084,3.90,3.95,3.99,3.999')
    a = ap.parse_args()
    Z.belownormal()
    out = {}
    for s in [float(v) for v in a.sides.split(',')]:
        r = verify(s)
        r['hole_one_measured'] = hole_one_check(s - 2)
        out['%.6f' % s] = r
        print('s=%.6f  disjoint %s (min gap %+.0e)  hole side %.4f  notch %.4f x 1  '
              'ribbon in block %s  HOLE-ONE max |(p-q).u| %.5f (<= 0.5)'
              % (s, r['disjoint'], r['min_gap'], r['hole_side'], r['notch_dims'][0][0],
                 all(r['ribbon_in_block'].values()), r['hole_one_measured']), flush=True)
        print('   pocket components (shapely): %s  == hole %.4f + 4 notches %.4f'
              % ([round(v, 4) for v in r['shapely_components']], r['hole_side'] ** 2,
                 r['notch_dims'][0][0]), flush=True)
    json.dump(out, open(os.path.join(RES, 'limit253.json'), 'w', encoding='utf-8'), indent=1)
    print('LIMIT DONE', flush=True)


if __name__ == '__main__':
    main()
