#!/usr/bin/env python3
"""
charge.py -- A26 task 2: the CHARGED WALL FUNCTIONAL.

A profile is a list of hypothesis cells, each = (centre box) x (tilt box), i.e.
exactly A25's atlas cells.  `profile_charge` returns a CERTIFIED LOWER BOUND on
the area of the UNION of the dead regions of all the squares in the profile,
valid uniformly over every realisation of the profile.

Soundness (A23 Lemma 1+2, A25 sect.1).  A25's atlas entry for cell K supplies
rational rectangles R_1..R_m that are, for EVERY placement P with parameters in
K: pairwise interior-disjoint, interior-disjoint from P, and dead for {P}.  By
monotonicity they stay dead for the whole packing.  A region dead for {P_i} is
automatically interior-disjoint from every OTHER packing square P_j (P_j is a
legal placement for {P_i}), so the only side condition left is CROSS-SQUARE
disjointness of the rectangle lists -- which we enforce here by taking a
maximum-weight subfamily of pairwise region-disjoint squares (exact rational
rectangle tests).  Hence

    profile_charge(profile)  <=  |union of dead regions|  <=  s^2 - 11
and profile_charge > s^2 - 11 kills the profile.

Since we want a LOWER bound on the charge of the CHEAPEST profile, we always
take the MINIMUM certified value over all atlas cells compatible with a class.

Convention.  Everything is done in A25's fundamental domain
    centre in the quadrant [0, s/2]^2,  theta in [0,45] deg,
which is legitimate because every statement we make is D4-invariant (the class
of a square is defined by its distance to the NEAREST wall and by |tilt| mod 90
folded into [0,45]).  In the quadrant, dist(centre, nearest wall) = min(cx,cy).

Run:  python charge.py            (validation + the sensitivity tables)
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'A25-wastage-atlas'))
from query import Atlas, rect_disjoint            # noqa: E402

S = F(96, 25)
BUDGET = S * S - 11                                # 2341/625 = 3.7456
REACH = F(134711, 100000)   # > 0.64 + sqrt2/2 = 1.3471067811..., see band.py
#   (upper bound, so 'D < 0.64+h(theta) <= 0.64+sqrt2/2' implies 'D <= REACH')

COARSE = os.path.join(HERE, '..', 'A25-wastage-atlas', 'results',
                      'atlas_single_3.84.json')
FINE = os.path.join(HERE, '..', 'A25-wastage-atlas', 'results',
                    'atlas_single_fine_3.84.json')
PAIR = os.path.join(HERE, '..', 'A25-wastage-atlas', 'results',
                    'atlas_pair_3.84.json')


# ------------------------------------------------------------------ cells
def wlo_rat(th0_deg):
    """rational LOWER bound on min_{theta in bin}(cos+sin) (bins inside [0,45])."""
    v = math.cos(math.radians(th0_deg)) + math.sin(math.radians(th0_deg))
    return F(int(v * 10 ** 9), 10 ** 9)


class CellSet:
    """all admissible cells of one atlas, in the fundamental domain."""

    def __init__(self, path):
        self.raw = json.load(open(path))
        g = self.raw['grid']
        self.h = F(g['h'])
        self.n = int(g['n_centre'])
        self.dth = float(g['dtheta_deg'])
        self.have = {}
        for c in self.raw['cells']:
            i = int(F(c['cx'][0]) / self.h)
            j = int(F(c['cy'][0]) / self.h)
            k = int(round(c['theta_deg'][0] / self.dth))
            self.have[(k, i, j)] = c
        self.ks = sorted(set(k for (k, i, j) in self.have))

    def admissible(self, i, j, k):
        w = wlo_rat(k * self.dth)
        lo, hi = w / 2, S - w / 2
        x0, x1 = i * self.h, (i + 1) * self.h
        y0, y1 = j * self.h, (j + 1) * self.h
        return max(x0, lo) <= min(x1, hi) and max(y0, lo) <= min(y1, hi)

    def iter_cells(self, band_only=True):
        """(k,i,j, d_lo, theta0, value F, regions) over ADMISSIBLE cells.
        d_lo = min(cx0,cy0) = certified lower bound of dist(centre, wall)."""
        for k in self.ks:
            for i in range(self.n):
                for j in range(self.n):
                    d_lo = min(i, j) * self.h
                    if band_only and d_lo > REACH:
                        continue
                    if not self.admissible(i, j, k):
                        continue
                    c = self.have.get((k, i, j))
                    v = F(c['dead_lb']) if c else F(0)
                    rg = ([(F(r[0]), F(r[2]), F(r[1]), F(r[3])) for r in c['regions']]
                          if c else [])
                    yield (k, i, j, d_lo, k * self.dth, v, rg)


# ------------------------------------------------------------------ union charge
def rect_area(r):
    return (r[1] - r[0]) * (r[3] - r[2])


def max_disjoint_charge(groups):
    """groups = list of (value, rectangles).  Return the largest sum of values
    over a subfamily whose rectangle lists are PAIRWISE interior-disjoint --
    a certified lower bound on the area of the union of all the dead regions.
    Exact for <= 20 groups (bitmask DP over the conflict graph)."""
    n = len(groups)
    conf = [0] * n
    for a in range(n):
        for b in range(a + 1, n):
            bad = False
            for r in groups[a][1]:
                for q in groups[b][1]:
                    if not rect_disjoint(r, q):
                        bad = True
                        break
                if bad:
                    break
            if bad:
                conf[a] |= 1 << b
                conf[b] |= 1 << a
    best = F(0)
    if n <= 22:
        for mask in range(1 << n):
            ok = True
            m = mask
            while m:
                b = (m & -m).bit_length() - 1
                if conf[b] & mask:
                    ok = False
                    break
                m &= m - 1
            if ok:
                v = sum(groups[b][0] for b in range(n) if mask >> b & 1)
                if v > best:
                    best = v
        return best
    # greedy fallback
    order = sorted(range(n), key=lambda b: -groups[b][0])
    chosen = 0
    for b in order:
        if not (conf[b] & chosen):
            chosen |= 1 << b
            best += groups[b][0]
    return best


# ------------------------------------------------------------------ validation
def validate():
    print('--- validation of charge.py against A23/A25 published numbers ---')
    at = Atlas(COARSE)
    atf = Atlas(FINE)
    tests = [
        ('A25 near-corner L-moat (1.20-1.35)^2, th 0-3   [A25: 1.4648]',
         at, (F(6, 5), F(27, 20)), (F(6, 5), F(27, 20)), (0, 3), 1.4648),
        ('A25 fine near-corner (1.275,1.35)^2, th 15-20  [A25: 1.5977]',
         atf, (F(51, 40), F(27, 20)), (F(51, 40), F(27, 20)), (15, 20), 1.5977),
        ('A25 head max at d=0.45, th 0-3: cell (1.20,1.35)x(0.45,0.60) [0.5078]',
         at, (F(6, 5), F(27, 20)), (F(9, 20), F(3, 5)), (0, 3), 0.5078),
        ('mid-wall flush cell (0.45,0.60)x(1.65,1.80), th 0-3 -> genuine 0',
         at, (F(9, 20), F(3, 5)), (F(33, 20), F(9, 5)), (0, 3), 0.0),
        ('flush CORNER cell (0.45,0.60)^2 th 0-3  [A23 corners4: 0.0000]',
         at, (F(9, 20), F(3, 5)), (F(9, 20), F(3, 5)), (0, 3), 0.0),
        ('deep interior (1.80,1.95)^2, th 21-24          [A25: 0 by design]',
         at, (F(9, 5), F(39, 20)), (F(9, 5), F(39, 20)), (21, 24), 0.0),
        ('D4 image of the corner cell (rotated)          [same value]',
         at, (S - F(27, 20), S - F(6, 5)), (F(6, 5), F(27, 20)), (0, 3), 1.4648),
    ]
    ok = True
    for name, a, cx, cy, th, expect in tests:
        v, rg = a.lookup(cx, cy, th)
        good = abs(float(v) - expect) < 5e-3
        ok &= good
        print(f'  {"PASS" if good else "FAIL"}  {name}: got {float(v):.4f} '
              f'({len(rg)} rects)')
    # region areas add up to the value
    v, rg = at.lookup((F(6, 5), F(27, 20)), (F(6, 5), F(27, 20)), (0, 3))
    tot = sum(rect_area(r) for r in rg)
    print(f'  region-area sum = {float(tot):.4f} vs dead_lb {float(v):.4f} '
          f'{"PASS" if tot == v else "(regions of several cells: >=)"}')
    # four flush corner squares strand ~0 (A23 corners4 = 0.0000)
    g = []
    for (cx, cy) in [(F(1, 2), F(1, 2))]:
        vv, rr = at.lookup((cx, cx + F(3, 20)), (cy, cy + F(3, 20)), (0, 3))
        g.append((vv, rr))
    print(f'  flush corner cell [0.50,0.65]^2 x [0,3]deg -> {float(g[0][0]):.4f} '
          f'(A23 exact flush corner square: 0.0000; the atlas value is the '
          f'BOX-uniformity moat, not a wedge)')
    return ok


# ------------------------------------------------------------------ tables
def sensitivity(cs_coarse, cs_fine):
    """min / median / max certified charge over admissible BAND cells,
    as a function of a tilt floor and a wall-distance floor."""
    rows = []
    for tag, cs in (('coarse 0.15x0.15x3deg', cs_coarse),
                    ('fine   0.075x0.075x5deg (th>=15)', cs_fine)):
        cells = list(cs.iter_cells(band_only=True))
        rows.append((tag, cells))
    return rows


def main():
    os.chdir(HERE)
    print('=' * 78)
    print('A26 task 2 -- the charged wall functional  (budget s^2-11 = '
          f'{BUDGET} = {float(BUDGET):.4f})')
    print('=' * 78)
    okv = validate()

    cs_c = CellSet(COARSE)
    cs_f = CellSet(FINE)

    print('\n--- SENSITIVITY: min certified charge over admissible BAND cells ---')
    print('    (band = dist(centre, nearest wall) <= 1.3471; a cell qualifies if its')
    print('     lower corner min(cx0,cy0) <= 1.3471.  min over cells = the value the')
    print('     ledger may assume for ONE forced band square.)')
    res = {}
    for tag, cs, thmin_list in (('coarse', cs_c, [0, 3, 6, 9, 12, 15, 21, 27, 33, 39]),
                                ('fine', cs_f, [15, 20, 25, 30, 35, 40])):
        cells = list(cs.iter_cells(band_only=True))
        print(f'\n  atlas={tag}  ({len(cells)} admissible band cells)')
        print('   tilt floor \\ wall-dist floor d0:   ' +
              '  '.join(f'{float(d):>5.2f}' for d in
                        [F(0), F(3, 4), F(9, 10), F(21, 20), F(6, 5)]))
        tab = {}
        for thmin in thmin_list:
            line = []
            for d0 in [F(0), F(3, 4), F(9, 10), F(21, 20), F(6, 5)]:
                sel = [c for c in cells if c[4] >= thmin - 1e-9 and c[3] >= d0]
                if not sel:
                    line.append('  --  ')
                    continue
                mn = min(c[5] for c in sel)
                tab[(thmin, str(d0))] = (float(mn), len(sel))
                line.append(f'{float(mn):6.3f}')
            print(f'    theta >= {thmin:2d} deg               ' + '  '.join(line))
        res[tag] = {f'{k[0]}|{k[1]}': v for k, v in tab.items()}

    print('\n  n_required = ceil(budget / c) squares of that minimum charge needed to kill:')
    for tag in res:
        for key, (mn, cnt) in sorted(res[tag].items()):
            nreq = math.ceil(float(BUDGET) / mn) if mn > 0 else None
            print(f'    {tag:6s} {key:>12s}: c={mn:.4f} -> n_required='
                  f'{nreq if nreq else "inf"}'
                  f'{"  <= 11 REACHABLE" if nreq and nreq <= 11 else ""}  ({cnt} cells)')

    json.dump(res, open('results/sensitivity.json', 'w'), indent=1)
    print('\n  wrote results/sensitivity.json;  validation', 'PASS' if okv else 'FAIL')


if __name__ == '__main__':
    main()
