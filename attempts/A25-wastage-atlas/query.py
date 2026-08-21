#!/usr/bin/env python3
"""
query.py -- A25 wastage atlas lookup (this is the file A24 imports).

    from query import Atlas
    at = Atlas('results/atlas_single_3.84.json')
    lb, regions = at.lookup(cx=(F(7,10), F(3,4)), cy=(F(7,10), F(3,4)),
                            theta_deg=(30, 32))
    # lb: Fraction, a CERTIFIED lower bound on the dead (permanently empty) area
    #     stranded by ANY unit square whose centre lies in cx x cy and whose tilt
    #     lies in theta_deg (interpreted mod 90 deg).  0 means "no information".
    # regions: list of pairwise interior-disjoint rectangles (Fractions), already
    #     mapped back into the QUERY frame, realising that area.  They are
    #     interior-disjoint from every placement allowed by the query box.

Budget lemma (A23 notes.md Lemma 2): if a case-tree node fixes squares in boxes
K_1..K_k and the returned region lists are pairwise interior-disjoint ACROSS the
k squares (use `disjoint_regions`), then any packing of n unit squares in [0,s]^2
satisfying the node hypothesis obeys  sum_i lb_i <= s^2 - n.  In particular
sum_i lb_i > s^2 - 11  kills the node.

D4 CONVENTION.  The atlas is stored on a fundamental domain of the container's
symmetry group D4 (order 8) acting on placements (c, theta):
    r : (x, y) -> (s - y, x),        theta -> theta      (a 90 deg rotation of the
                                                          container maps a square
                                                          to a square of the same
                                                          tilt: theta is mod 90)
    m : (x, y) -> (y, x),            theta -> 90 - theta
Stored domain = { centre in the QUADRANT [0, s/2]^2 } x { theta in [0 deg, 45 deg] }.
This is a fundamental domain: the four rotations bring any centre into the
quadrant, and the residual stabiliser of the quadrant is the diagonal reflection
m, which is exactly what the restriction theta <= 45 deg consumes.
(NB: reducing the centre to an OCTANT *and* theta to [0,45] would be a double
count -- |D4| = 8 = 4 (quadrant) x 2 (theta), not 8 x 2; see notes.md sect.2.)
A lookup maps the query box through all 8 group elements, keeps the parts landing
in the stored domain, and returns the MINIMUM value over every atlas cell they
meet (0 if any part is uncovered), so the answer is a lower bound valid uniformly
over the whole query box.
"""
from __future__ import annotations

import json
import math
from fractions import Fraction as F

# ------------------------------------------------------------------ D4 on boxes


class Sym:
    """(x,y) -> M (x,y) + t*s ; flip = True means theta -> 90 - theta."""

    def __init__(self, M, t, flip):
        self.M, self.t, self.flip = M, t, flip

    def pt(self, x, y, s):
        (a, b), (c, d) = self.M
        return a * x + b * y + self.t[0] * s, c * x + d * y + self.t[1] * s

    def box(self, x0, x1, y0, y1, s):
        pts = [self.pt(x, y, s) for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), max(xs), min(ys), max(ys)

    def inv(self):
        (a, b), (c, d) = self.M
        det = a * d - b * c
        Mi = ((d // det, -b // det), (-c // det, a // det))
        # t_inv = -Mi t
        ti = (-(Mi[0][0] * self.t[0] + Mi[0][1] * self.t[1]),
              -(Mi[1][0] * self.t[0] + Mi[1][1] * self.t[1]))
        return Sym(Mi, ti, self.flip)


def _mul(A, B):
    """A after B."""
    (a, b), (c, d) = A.M
    (e, f), (g, h) = B.M
    M = ((a * e + b * g, a * f + b * h), (c * e + d * g, c * f + d * h))
    t = (a * B.t[0] + b * B.t[1] + A.t[0], c * B.t[0] + d * B.t[1] + A.t[1])
    return Sym(M, t, A.flip != B.flip)


ID = Sym(((1, 0), (0, 1)), (0, 0), False)
ROT = Sym(((0, -1), (1, 0)), (1, 0), False)          # (x,y) -> (s-y, x)
MIR = Sym(((0, 1), (1, 0)), (0, 0), True)            # (x,y) -> (y, x), th -> 90-th

D4 = []
_r = ID
for _k in range(4):
    D4.append(_r)
    D4.append(_mul(_r, MIR))
    _r = _mul(ROT, _r)


# ------------------------------------------------------------------ the atlas
class Atlas:
    def __init__(self, path):
        with open(path) as f:
            self.raw = json.load(f)
        self.s = F(self.raw['s'])
        g = self.raw['grid']
        self.h = F(g['h'])
        self.dtheta = float(g['dtheta_deg'])
        self.theta_max = float(g['theta_range'][1])
        self.nmax = int(g['n_centre'])
        self.kind = self.raw.get('kind', 'single')
        self.tab = {}
        for c in self.raw['cells']:
            i = int(F(c['cx'][0]) / self.h)
            j = int(F(c['cy'][0]) / self.h)
            k = int(round(c['theta_deg'][0] / self.dtheta))
            self.tab[(k, i, j)] = c

    # -- grid indices of the atlas cells meeting a box (half-open convention)
    def _idx(self, lo, hi, step, n):
        a = int(math.floor(float(F(lo) / step) + 1e-12))
        b = int(math.ceil(float(F(hi) / step) - 1e-12)) - 1
        if b < a:
            b = a
        if a < 0 or b >= n:
            return None
        return range(a, b + 1)

    def lookup(self, cx, cy, theta_deg, want_regions=True):
        """certified lower bound (Fraction) + realising regions in the query frame."""
        th0, th1 = float(theta_deg[0]) % 90.0, float(theta_deg[1])
        th1 = th0 + (float(theta_deg[1]) - float(theta_deg[0]))
        if th1 - th0 >= 90.0:
            return F(0), []
        best = None
        regions = []
        pieces = [(th0, th1)] if th1 <= 90.0 else [(th0, 90.0), (0.0, th1 - 90.0)]
        for (a0, a1) in pieces:
            v, rg = self._lookup_1(cx, cy, (a0, a1), want_regions)
            if v == 0:
                return F(0), []
            best = v if best is None else min(best, v)
            regions += rg
        return (best or F(0)), regions

    def _lookup_1(self, cx, cy, theta_deg, want_regions):
        x0, x1 = F(cx[0]), F(cx[1])
        y0, y1 = F(cy[0]), F(cy[1])
        a0, a1 = float(theta_deg[0]), float(theta_deg[1])
        lim = self.nmax * self.h
        vals, regs = [], []
        seen_any = False
        for g in D4:
            gx0, gx1, gy0, gy1 = g.box(x0, x1, y0, y1, self.s)
            ga0, ga1 = (90.0 - a1, 90.0 - a0) if g.flip else (a0, a1)
            # keep the part inside the stored domain
            qx0, qx1 = max(gx0, F(0)), min(gx1, lim)
            qy0, qy1 = max(gy0, F(0)), min(gy1, lim)
            qa0, qa1 = max(ga0, 0.0), min(ga1, self.theta_max)
            if qx0 > qx1 or qy0 > qy1 or qa0 > qa1:
                continue
            seen_any = True
            I = self._idx(qx0, qx1, self.h, self.nmax)
            J = self._idx(qy0, qy1, self.h, self.nmax)
            K = self._idx(qa0, qa1, F(self.dtheta).limit_denominator(1000),
                          int(round(self.theta_max / self.dtheta)))
            if I is None or J is None or K is None:
                return F(0), []
            ginv = g.inv()
            for k in K:
                for i in I:
                    for j in J:
                        c = self.tab.get((k, i, j))
                        if c is None:
                            return F(0), []          # uncovered -> no information
                        vals.append(F(c['dead_lb']))
                        if want_regions:
                            for r in c['regions']:
                                rx0, ry0, rx1, ry1 = (F(r[0]), F(r[1]), F(r[2]), F(r[3]))
                                regs.append(ginv.box(rx0, rx1, ry0, ry1, self.s))
        if not seen_any or not vals:
            return F(0), []
        m = min(vals)
        if m == 0:
            return F(0), []
        # regions of the MINIMISING cells only (they are the ones the bound uses)
        return m, regs

    # -- convenience: query by a plain (centre, theta) point with zero width
    def at(self, cx, cy, theta_deg):
        return self.lookup((cx, cx), (cy, cy), (theta_deg, theta_deg),
                           want_regions=False)[0]


def rect_disjoint(a, b):
    return a[1] <= b[0] or b[1] <= a[0] or a[3] <= b[2] or b[3] <= a[2]


def disjoint_regions(groups):
    """True iff the region lists of different squares are pairwise
    interior-disjoint (the side condition of the budget lemma when the values of
    several atlas entries are ADDED)."""
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            for a in groups[i]:
                for b in groups[j]:
                    if not rect_disjoint(a, b):
                        return False
    return True


if __name__ == '__main__':
    import sys
    at = Atlas(sys.argv[1] if len(sys.argv) > 1 else 'results/atlas_single_3.84.json')
    print(f"atlas s={at.s} ({float(at.s):.6f}) cells={len(at.tab)} "
          f"grid h={at.h} dtheta={at.dtheta}")
    QS = [('corner, fundamental domain', (F(7, 10), F(3, 4)), (F(7, 10), F(3, 4)), (30, 33)),
          ('same cell rotated by 90deg  ', (F(309, 100), F(157, 50)), (F(7, 10), F(3, 4)), (30, 33)),
          ('same cell mirrored, th->90-t', (F(7, 10), F(3, 4)), (F(7, 10), F(3, 4)), (57, 60)),
          ('deep interior               ', (F(19, 10), F(39, 20)), (F(19, 10), F(39, 20)), (20, 23)),
          ('box straddling 2 atlas cells', (F(7, 10), F(9, 10)), (F(7, 10), F(3, 4)), (30, 33)),
          ('inadmissible (against wall) ', (F(3, 10), F(2, 5)), (F(3, 10), F(2, 5)), (30, 33))]
    for (tag, qx, qy, qt) in QS:
        v, r = at.lookup(qx, qy, qt)
        print(f"  {tag}  cx=[{float(qx[0]):.2f},{float(qx[1]):.2f}] "
              f"cy=[{float(qy[0]):.2f},{float(qy[1]):.2f}] th={qt} "
              f"-> {float(v):.4f}  ({len(r)} rects)")
