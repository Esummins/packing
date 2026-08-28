#!/usr/bin/env python3
"""
A24 kill_tests.py -- the COMPOSED node kill test for the s(11) case tree.

At a node with hypothesis H = (core boxes B_1..B_m, NO-families F_1..F_j) the node
is DEAD if EITHER of two logically independent tests fires:

  (T1) COVERAGE LP (A14 caselp.solve_node): tau_H < 11 - m  (converged, with the
       certification margins) -- certificate = a measure with the node's exemptions,
       checked by A14's exact verify_case.py.

  (T2) WASTAGE LEDGER (A23 budget lemma): certified pairwise interior-disjoint dead
       regions D_1..D_r with  sum area(D_i) > s^2 - 11  -- certificate = the cell
       list + the dead_region.py branch-and-bound (exact Fraction mode).

This module implements T2 on top of A14's hypothesis objects.

SEMANTICS / SOUNDNESS of T2 at a tree node
------------------------------------------
* A YES hypothesis "some packing square has (c, theta) in B" is turned into
  dead_region.PlacedBox(t(th0), t(th1), x0, x1, y0, y1): every certificate produced
  is UNIFORM over the box, i.e. it holds simultaneously for every placement in B.
  NOTE this is STRONGER than what the LP node uses (the LP only exempts rows that
  overlap the rational CORE K(B) subset of every placement of B); T2 uses the whole
  box, which is the honest reading of the YES hypothesis.
* A NO hypothesis "no packing square has centre in zone Z with theta in Theta" is
  passed to the certifier as an extra DISCHARGE rule (see Certifier._in_nozone):
  a parameter box entirely inside the family contains no legal continuation
  placement.  Sound because ALL 11 squares of the packing avoid the family.
* Interior-disjointness of the dead regions (required by the budget lemma) is
  enforced STRUCTURALLY: all cells come from ONE quadtree over ONE window, so they
  are pairwise interior-disjoint by construction, and wastage.dead_map checks each
  cell exactly interior-disjoint from every placed core.  `check_disjoint()` below
  re-verifies this from the stored cell list (exact rational sweep) so a certificate
  file can be audited on its own.
* Budget: s^2 - 11 in exact rationals (3.84 -> 2341/625 = 3.7456).

Usage:
  python kill_tests.py --validate            # reproduce A23's known cases
  python kill_tests.py --config <name>       # A24 configs (see configs.py)
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dead_region import Certifier, PlacedBox, Placed, Region, cos_sin
import wastage
import caselp
from caselp import Box, NoFam, Hyp, t_lo, t_hi, q, q_up


# ------------------------------------------------------------------ budget
def budget_rat(s_rat, n=11):
    """empty-area budget s^2 - n, exact."""
    return F(s_rat) * F(s_rat) - n


# ------------------------------------------------------------------ H -> certifier data
def placedbox_of_box(b: Box) -> PlacedBox:
    """A14 Box (floats, degrees) -> A23 PlacedBox (exact rationals, t = tan(theta/2)).
    Rounding is OUTWARD in every direction so the PlacedBox contains every placement
    of the Box: t_lo <= tan(th0/2), t_hi >= tan(th1/2), centre range widened to the
    nearest exact decimal."""
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    x0, x1 = q(b.x0), q(b.x1)
    y0, y1 = q(b.y0), q(b.y1)
    # widen by 1e-9 to absorb the float->rational rounding of q()
    e = F(1, 10 ** 9)
    return PlacedBox(t0, t1, x0 - e, x1 + e, y0 - e, y1 + e)


def nozone_of_nofam(f: NoFam):
    """A14 NoFam -> (x0,x1,y0,y1,[(tlo,thi)..]) with INWARD rounding of the zone and
    of the theta intervals (conservative: the discharge rule must only fire on
    parameter boxes that provably lie in the family)."""
    e = F(1, 10 ** 9)
    x0, x1 = q(f.x0) + e, q(f.x1) - e
    y0, y1 = q(f.y0) + e, q(f.y1) - e
    tints = []
    for (a, b) in f.thetas:
        a = max(0.0, a)
        b = min(90.0, b)
        if b <= a:
            continue
        # inward: [t_hi(a), t_lo(b)] subset of [tan(a/2), tan(b/2)]
        ta, tb = t_hi(a), t_lo(b)
        if tb > ta:
            tints.append((ta, tb))
    if not tints or x1 <= x0 or y1 <= y0:
        return None
    return (x0, x1, y0, y1, tints)


def hyp_to_cert_data(hyp: Hyp):
    placed = [placedbox_of_box(b) for b in hyp.boxes]
    noz = [nozone_of_nofam(f) for f in hyp.nofams]
    return placed, [z for z in noz if z is not None]


# ------------------------------------------------------------------ T2
def wastage_test(s_rat, hyp=None, placed=None, nozones=(), window=None,
                 cell0=F(4, 25), min_cell=F(1, 64), mode='float', depth_max=26,
                 max_boxes_per_cell=1500, n=11, verbose=True):
    """T2.  Returns dict with the certified dead area (exact rational string), the
    budget, the verdict and the cell list (the certificate payload)."""
    s_rat = F(s_rat)
    if placed is None:
        placed, noz2 = hyp_to_cert_data(hyp)
        nozones = list(nozones) + list(noz2)
    if window is None:
        window = (F(0), s_rat, F(0), s_rat)
    res = wastage.dead_map(placed, s_rat, window, cell0=cell0, min_cell=min_cell,
                           mode=mode, depth_max=depth_max,
                           max_boxes_per_cell=max_boxes_per_cell, verbose=verbose,
                           nozones=nozones)
    bud = budget_rat(s_rat, n)
    area = F(res['area'])
    res['budget'] = str(bud)
    res['budget_float'] = float(bud)
    res['dead_node'] = bool(area > bud)
    res['fraction_of_budget'] = float(area / bud)
    res['mode'] = mode
    res['s'] = str(s_rat)
    res['n_cores'] = len(placed)
    res['n_nozones'] = len(nozones)
    return res


# ------------------------------------------------------------------ certificate audit
def check_disjoint(cells):
    """exact check that a cell list is pairwise interior-disjoint (axis-aligned
    rectangles).  O(k^2) with a cheap x-sweep; k is a few hundred."""
    R = [(F(a), F(b), F(c), F(d)) for (a, b, c, d) in cells]      # (x0,y0,x1,y1)
    R.sort(key=lambda r: r[0])
    k = len(R)
    for i in range(k):
        x0, y0, x1, y1 = R[i]
        for j in range(i + 1, k):
            X0, Y0, X1, Y1 = R[j]
            if X0 >= x1:
                break
            if min(x1, X1) > max(x0, X0) and min(y1, Y1) > max(y0, Y0):
                return False, (R[i], R[j])
    return True, None


def sum_area(cells):
    tot = F(0)
    for (a, b, c, d) in cells:
        tot += (F(c) - F(a)) * (F(d) - F(b))
    return tot


# ------------------------------------------------------------------ validation
def _val_configs():
    """A23's known cases, re-created here through the A24 entry points."""
    S385, S386 = F(77, 20), F(193, 50)
    T33 = F(295521, 1000000)          # tan(16.5 deg)
    out = {}

    # (1) corners4: four flush corner squares at 3.85 -- must give EXACTLY 0
    pl = [Placed(F(1, 2), F(1, 2), 0), Placed(S385 - F(1, 2), F(1, 2), 0),
          Placed(S385 - F(1, 2), S385 - F(1, 2), 0), Placed(F(1, 2), S385 - F(1, 2), 0)]
    out['corners4'] = dict(placed=pl, s=S385, window=(F(0), S385, F(0), F(6, 5)),
                           expect=0.0, tol=1e-9, note='A23: strands exactly 0')

    # (2) pair: the two adjacent 33 deg pinwheel squares at 3.86 -- A23: 1.8834
    a = Placed(F(2459700, 1000000), F(2540486, 1000000), T33)
    from dead_region import _convex_interior_disjoint
    b = None
    for k in range(60):
        off = F(k, 2000)
        cand = Placed(F(1319514, 1000000) - off, F(2459700, 1000000) - off, T33)
        if _convex_interior_disjoint(a.corners, cand.corners):
            b = cand
            break
    cx = (float(a.cx) + float(b.cx)) / 2
    cy = (float(a.cy) + float(b.cy)) / 2
    win = (F(int((cx - 1.45) * 100), 100), F(int((cx + 1.45) * 100), 100),
           F(int((cy - 1.45) * 100), 100), S386)
    out['pair'] = dict(placed=[a, b], s=S386, window=win, expect=1.8834, tol=0.02,
                       note='A23: 1.8834 (adjacent pinwheel pair)')

    # (3) pair_box: the CORE-BOX-uniform version -- A23: 1.3837
    t0, t1 = F(287000, 1000000), F(305500, 1000000)
    d = F(1, 100)
    ax, ay = F(2459700, 1000000), F(2540486, 1000000)
    bx, by = F(1319514, 1000000), F(2459700, 1000000)
    out['pair_box'] = dict(placed=[PlacedBox(t0, t1, ax - d, ax + d, ay - d, ay + d),
                                   PlacedBox(t0, t1, bx - d, bx + d, by - d, by + d)],
                           s=S386, window=(F(73, 100), F(303, 100), F(135, 100), S386),
                           expect=1.3837, tol=0.02, note='A23: 1.3837 (PlacedBox pair)')

    # (4) corner_box: A14 alive-node corner square, core-uniform -- A23: 0.5285
    out['corner_box'] = dict(placed=[PlacedBox(F(354119, 1000000), F(373885, 1000000),
                                               F(18, 25), F(37, 50), F(18, 25), F(37, 50))],
                             s=S385, window=(F(0), F(21, 10), F(0), F(21, 10)),
                             expect=0.5285, tol=0.02, note='A23: 0.5285 (PlacedBox corner)')
    return out


def validate(names=None, min_cell=64):
    cfgs = _val_configs()
    names = names or list(cfgs)
    ok = True
    report = {}
    for nm in names:
        c = cfgs[nm]
        t0 = time.time()
        r = wastage_test(c['s'], placed=c['placed'], window=c['window'],
                         min_cell=F(1, min_cell), mode='float', depth_max=24,
                         max_boxes_per_cell=1500, verbose=False)
        a = float(F(r['area']))
        good = abs(a - c['expect']) <= c['tol']
        dj, bad = check_disjoint(r['cells'])
        good = good and dj
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {nm:12s} area={a:.4f} (expect {c['expect']:.4f}) "
              f"cells={len(r['cells'])} disjoint={dj} {time.time()-t0:.0f}s   {c['note']}")
        report[nm] = dict(area=a, expect=c['expect'], pass_=good, disjoint=dj,
                          n_cells=len(r['cells']), seconds=time.time() - t0)
    return ok, report


# ------------------------------------------------------------------ NO-zone unit test
def nozone_unit_test():
    """Sanity for the (N) discharge: with the hypothesis "NO square has its centre
    anywhere in the admissible domain" every region is dead (vacuously, since a
    packing cannot exist); with a small zone it must NOT fire on far-away regions."""
    s = F(96, 25)
    lo, hi = F(1, 2), s - F(1, 2)
    allzone = (lo - 1, hi + 1, lo - 1, hi + 1, [(F(0), F(1))])
    cert = Certifier(s, [], mode='exact', depth_max=20, nozones=[allzone])
    r1 = cert.certify(Region.rect(F(1), F(1), F(11, 10), F(11, 10)))
    cert2 = Certifier(s, [], mode='exact', depth_max=20,
                      nozones=[(F(1, 2), F(6, 10), F(1, 2), F(6, 10), [(F(0), F(1))])])
    r2 = cert2.certify(Region.rect(F(19, 10), F(19, 10), F(2), F(2)))
    print(f"  [{'PASS' if r1['passed'] else 'FAIL'}] nozone-all: every region dead   (passed={r1['passed']})")
    print(f"  [{'PASS' if not r2['passed'] else 'FAIL'}] nozone-small: centre region NOT dead (passed={r2['passed']})")
    return r1['passed'] and not r2['passed']


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--validate', action='store_true')
    ap.add_argument('--only', default=None)
    ap.add_argument('--min_cell', type=int, default=64)
    a = ap.parse_args()
    if a.validate:
        print("A24 kill_tests validation (T2 = A23 wastage ledger through A24 entry points)")
        okn = nozone_unit_test()
        ok, rep = validate(a.only.split(',') if a.only else None, min_cell=a.min_cell)
        rep['nozone_unit'] = okn
        rep['ALL_PASS'] = bool(ok and okn)
        json.dump(rep, open(os.path.join(HERE, 'results', 'validation.json'), 'w'), indent=1)
        print("ALL PASS" if (ok and okn) else "SOME FAILED")
