#!/usr/bin/env python3
"""
dead_region.py -- A23-wastage-oracle: certifier for DEAD regions of a partial configuration.

DEFINITION.  Container = closed square [0,s]^2 (s rational).  Placed squares
P_1..P_k = closed unit squares with rational centre (cx,cy) and rational
t = tan(theta/2) in [0,1] (so cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2) and all
corners are rational).  A candidate region D (CONVEX polygon with rational
vertices, interior-disjoint from every P_i) is DEAD for H = {P_i} if there is NO
closed unit square Q with
    (1) Q subset [0,s]^2,
    (2) int(Q) cap int(P_i) = empty for every i,
    (3) Q cap D != empty.
Placements are parametrised by centre c and t = tan(theta/2) in [0,1]
(theta in [0, 90deg] suffices: Q(c,theta) = Q(c,theta+90deg)).

CONSEQUENCE (budget lemma, see notes.md): in any packing of 11 unit squares
(disjoint interiors) in [0,s]^2 that contains H, no packing square meets any dead
D (its interior would have to meet some int(P_i)); hence sum of areas of
interior-disjoint dead regions <= s^2 - 11.

BRANCH AND BOUND over boxes B = [t0,t1] x [x0,x1] x [y0,y1].
Root: t in [0,1], centre in (bbox(D) inflated by 7072/10000 in the inf-norm)
intersect [1/2, s-1/2]^2.  Sound: every point of Q lies within half-diagonal
sqrt(2)/2 < 7072/10000 of the centre (in 2-norm, hence in inf-norm), so any Q
meeting D has centre in the inflated bbox; and Q subset [0,s]^2 forces
w/2 <= cx,cy <= s - w/2 with w = cos+sin >= 1.
A box is DISCHARGED when one of these holds for ALL (t,c) in B:

 (V) VACUOUS -- no admissible placement in B.  w = cos+sin is unimodal in t
     (increasing then decreasing, max at t = tan(22.5deg)), so
     wLo = min(w(t0), w(t1)) <= w(t) on [t0,t1]; the centre range is clipped to
     [wLo/2, s-wLo/2]; empty => vacuous, else the clipped box (which still
     contains every admissible placement of B) is used downstream.

 (D) DISJOINT FROM D -- a fixed separating axis works for the whole box:
     (a) Q-frame axes: with exact enclosures C = [cos t1, cos t0],
         S = [sin t0, sin t1] (cos decreasing, sin increasing, both >= 0 on [0,1])
         and dx = px - [x0,x1], dy = py - [y0,y1], the body coordinates
         u = C dx + S dy, v = -S dx + C dy of every vertex p of D get interval
         enclosures; if every vertex has u > 1/2 for all params (interval lower
         bound > 1/2), D lies beyond the u=+1/2 edge of Q for every placement in
         B: disjoint.  Same for u < -1/2, v > 1/2, v < -1/2.
     (b) D-frame axes: for each outward edge normal a of D (rational),
         max_D a.p = a.v_edge; Q's support in direction -a is
         a.c - r(a), r(a) = (max|a.e1| + max|a.e2|)/2 over the enclosures of the
         edge vectors e1 = (C,S), e2 = (-S,C); if min_B a.c - r(a) > max_D a.p,
         disjoint.
     Soundness: existence of a separating line implies Q cap D = empty (both
     convex).  (Failing on all axes proves nothing -- that is fine, we bisect.)

 (O) OVERLAPS A PLACED SQUARE -- witness point:
     a rational point p with p in int(P_i), checked exactly once
     (|u_P(p)| < 1/2 and |v_P(p)| < 1/2 STRICTLY in P's own frame), and
     p in Q(c,t) for every (t,c) in B (exact interval containment, the same
     u,v enclosures as in certs/verify_measure.py).
     Soundness: p in int(P) and p in Q (closed) => int(P) cap int(Q) != empty:
     Q is a closed convex body, so Q = closure(int Q) and every neighbourhood of
     p meets int(Q); some neighbourhood of p lies inside int(P).
     NOTE: overlap of the projections on all 4 SAT axes is NECESSARY, not
     SUFFICIENT, for overlap of two convex polygons -- it is NOT used here.
     Special case (cheap): if all four corners of the centre box lie strictly
     inside P, then p = c works (c in Q always).

Otherwise B is bisected along its widest dimension (t-width scaled by tscale);
midpoints are dyadic so Fraction denominators stay 2^depth-bounded.  A box that
reaches depth_max undischarged is a FAIL witness (D not certified dead; either it
truly is reachable there or the sample points were insufficient).

If every box is discharged: THEOREM (for this H and this s): every closed unit
square inside [0,s]^2 that meets D interior-overlaps some P_i  =>  D is dead.

MODES.  mode='float': same logic in IEEE floats with outward safety eps (fast
mapping tool; not a proof).  mode='exact': Fractions everywhere (the certificate).
Witness points are proposed by float geometry (static interior grids + shapely
overlap centroids) but every accept decision in exact mode is exact.

Author: A23-wastage-oracle, 2026-08-20.
"""
from __future__ import annotations

import math
from fractions import Fraction as F

import numpy as np

try:
    from shapely.geometry import Polygon as ShPolygon
except Exception:  # pragma: no cover
    ShPolygon = None

HALF = F(1, 2)
INFLATE = F(7072, 10000)          # > sqrt(2)/2 = 0.70710678...


# ---------------------------------------------------------------- rational trig
def cos_sin(t):
    """exact (cos theta, sin theta) for t = tan(theta/2) (Fraction in, Fraction out)."""
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


def imul(a0, a1, b0, b1):
    p1, p2, p3, p4 = a0 * b0, a0 * b1, a1 * b0, a1 * b1
    return min(p1, p2, p3, p4), max(p1, p2, p3, p4)


class Placed:
    """A placed closed unit square with rational data."""

    def __init__(self, cx, cy, t):
        self.cx, self.cy, self.t = F(cx), F(cy), F(t)
        self.c, self.s = cos_sin(self.t)
        c, s = self.c, self.s
        self.corners = [(self.cx + c * u - s * v, self.cy + s * u + c * v)
                        for (u, v) in ((-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF))]
        self.points = []            # cached certified-interior rational points
        self._fpoly = None

    def body(self, px, py):
        """exact body coordinates (u, v) of a point."""
        dx, dy = F(px) - self.cx, F(py) - self.cy
        return self.c * dx + self.s * dy, -self.s * dx + self.c * dy

    def strictly_inside(self, px, py, margin=F(1, 10000)):
        u, v = self.body(px, py)
        h = HALF - margin
        return -h <= u <= h and -h <= v <= h

    def add_grid_points(self, n=7, edge_layers=(F(1, 100), F(3, 100), F(8, 100))):
        """static interior points: n x n grid plus layers hugging each edge (for
        thin-sliver overlaps).  All exact rationals, all strictly interior."""
        pts = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                u = F(i, n + 1) - HALF
                v = F(j, n + 1) - HALF
                pts.append((u, v))
        m = 17
        for off in edge_layers:
            h = HALF - off
            for i in range(m):
                w = -h + F(i, m - 1) * 2 * h
                pts += [(w, h), (w, -h), (h, w), (-h, w)]
        c, s = self.c, self.s
        for (u, v) in pts:
            self.points.append((self.cx + c * u - s * v, self.cy + s * u + c * v))

    def fpoly(self):
        if self._fpoly is None and ShPolygon is not None:
            self._fpoly = ShPolygon([(float(x), float(y)) for (x, y) in self.corners])
        return self._fpoly


class PlacedBox:
    """A CORE BOX of placed squares: the hypothesis "some packing square has
    (t, cx, cy) in [t0,t1] x [bx0,bx1] x [by0,by1]" (A13/A14 YES-node semantics).
    Duck-types Placed for the certifier, with every test made UNIFORM over the
    core box, so a dead certificate holds for EVERY placement of the core:

    * witness points: only points p certified to lie in int(P) for EVERY core
      placement P are kept (exact interval test at construction / on caching);
    * `corners` (used for cell-disjointness in the mapper) is the AABB HULL of
      all core placements (conservative over-approximation of the union);
    * `strictly_inside(p)` = p in int(P) for all core P (exact intervals).
    """

    def __init__(self, t0, t1, bx0, bx1, by0, by1):
        self.t0, self.t1 = F(t0), F(t1)
        self.bx0, self.bx1, self.by0, self.by1 = F(bx0), F(bx1), F(by0), F(by1)
        c0, s0 = cos_sin(self.t0)
        c1, s1 = cos_sin(self.t1)
        self.Cl, self.Ch = c1, c0          # cos decreasing
        self.Sl, self.Sh = s0, s1          # sin increasing
        # AABB hull: w/2 <= max(w)/2; w unimodal with max at t*=tan(22.5deg)
        tstar = F(414214, 1000000)
        cand = [self.t0, self.t1] + ([tstar] if self.t0 <= tstar <= self.t1 else [])
        wmax = max(sum(cos_sin(t)) for t in cand)
        # NOTE wmax at tstar slightly underestimates sqrt(2); pad by 1/1000
        h = wmax / 2 + F(1, 1000)
        self.corners = [(self.bx0 - h, self.by0 - h), (self.bx1 + h, self.by0 - h),
                        (self.bx1 + h, self.by1 + h), (self.bx0 - h, self.by1 + h)]
        # midpoint placement (for float candidate generation)
        tm = (self.t0 + self.t1) / 2
        self.cx = (self.bx0 + self.bx1) / 2
        self.cy = (self.by0 + self.by1) / 2
        self.t = tm
        self.c, self.s = cos_sin(tm)
        self.wobble = float((self.bx1 - self.bx0) + (self.by1 - self.by0)) / 2             + 1.5 * (float(self.t1) - float(self.t0))
        self.points = []
        self.points_dyn = []
        self._fpoly = None

    def strictly_inside(self, px, py, margin=F(1, 10000)):
        """p in int(P) for EVERY core placement (exact interval arithmetic)."""
        px, py = F(px), F(py)
        dx0, dx1 = px - self.bx1, px - self.bx0
        dy0, dy1 = py - self.by1, py - self.by0
        a0, a1 = imul(self.Cl, self.Ch, dx0, dx1)
        b0, b1 = imul(self.Sl, self.Sh, dy0, dy1)
        h = HALF - F(margin) if margin else HALF
        if not (-h < a0 + b0 and a1 + b1 < h):
            return False
        a0, a1 = imul(-self.Sh, -self.Sl, dx0, dx1)
        b0, b1 = imul(self.Cl, self.Ch, dy0, dy1)
        return -h < a0 + b0 and a1 + b1 < h


    def cell_interior_disjoint(self, verts):
        """True iff the cell (convex rational polygon) is interior-disjoint from
        EVERY core placement (sound interval SAT over the core box)."""
        Cl, Ch, Sl, Sh = self.Cl, self.Ch, self.Sl, self.Sh
        x0, x1, y0, y1 = self.bx0, self.bx1, self.by0, self.by1
        need = 4 * [True]
        for (px, py) in verts:
            dx0, dx1 = F(px) - x1, F(px) - x0
            dy0, dy1 = F(py) - y1, F(py) - y0
            a0, a1 = imul(Cl, Ch, dx0, dx1)
            b0, b1 = imul(Sl, Sh, dy0, dy1)
            ulo, uhi = a0 + b0, a1 + b1
            a0, a1 = imul(-Sh, -Sl, dx0, dx1)
            b0, b1 = imul(Cl, Ch, dy0, dy1)
            vlo, vhi = a0 + b0, a1 + b1
            if need[0] and not (ulo >= HALF):
                need[0] = False
            if need[1] and not (uhi <= -HALF):
                need[1] = False
            if need[2] and not (vlo >= HALF):
                need[2] = False
            if need[3] and not (vhi <= -HALF):
                need[3] = False
        if any(need):
            return True
        # cell-frame axes: every core placement beyond one edge of the cell
        n = len(verts)
        for i in range(n):
            X0, Y0 = F(verts[i][0]), F(verts[i][1])
            X1, Y1 = F(verts[(i + 1) % n][0]), F(verts[(i + 1) % n][1])
            ax, ay = (Y1 - Y0), -(X1 - X0)
            supp = max(ax * F(vx) + ay * F(vy) for (vx, vy) in verts)
            e1lo, e1hi = imul(Cl, Ch, ax, ax)
            t2lo, t2hi = imul(Sl, Sh, ay, ay)
            e1lo, e1hi = e1lo + t2lo, e1hi + t2hi
            e2alo, e2ahi = imul(Sl, Sh, -ax, -ax)
            t3lo, t3hi = imul(Cl, Ch, ay, ay)
            e2lo, e2hi = e2alo + t3lo, e2ahi + t3hi
            r = (max(abs(e1lo), abs(e1hi)) + max(abs(e2lo), abs(e2hi))) / 2
            acmin = (ax * x0 if ax >= 0 else ax * x1) + (ay * y0 if ay >= 0 else ay * y1)
            if acmin - r >= supp:
                return True
        return False

    def body(self, px, py):
        dx, dy = F(px) - self.cx, F(py) - self.cy
        return self.c * dx + self.s * dy, -self.s * dx + self.c * dy

    def add_grid_points(self, n=7, edge_layers=(F(3, 100), F(8, 100), F(15, 100))):
        pts = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                pts.append((F(i, n + 1) - HALF, F(j, n + 1) - HALF))
        m = 17
        for off in edge_layers:
            h = HALF - off
            for i in range(m):
                w = -h + F(i, m - 1) * 2 * h
                pts += [(w, h), (w, -h), (h, w), (-h, w)]
        c, s = self.c, self.s
        for (u, v) in pts:
            p = (self.cx + c * u - s * v, self.cy + s * u + c * v)
            if self.strictly_inside(*p):          # keep only core-uniform points
                self.points.append(p)

    def fpoly(self):
        if self._fpoly is None and ShPolygon is not None:
            mid = ShPolygon([(float(self.cx + self.c * u - self.s * v),
                              float(self.cy + self.s * u + self.c * v))
                             for (u, v) in ((-HALF, -HALF), (HALF, -HALF),
                                            (HALF, HALF), (-HALF, HALF))])
            self._fpoly = mid.buffer(-self.wobble - 1e-3)
        return self._fpoly



class Region:
    """convex polygon, rational CCW vertices."""

    def __init__(self, verts):
        self.verts = [(F(x), F(y)) for (x, y) in verts]
        # ensure CCW
        a = 0
        n = len(self.verts)
        for i in range(n):
            x0, y0 = self.verts[i]
            x1, y1 = self.verts[(i + 1) % n]
            a += x0 * y1 - x1 * y0
        if a < 0:
            self.verts = self.verts[::-1]
            a = -a
        self.area = a / 2
        # outward edge normals with their support values max_D a.p
        self.normals = []
        n = len(self.verts)
        for i in range(n):
            x0, y0 = self.verts[i]
            x1, y1 = self.verts[(i + 1) % n]
            ax, ay = (y1 - y0), -(x1 - x0)          # outward for CCW
            self.normals.append((ax, ay, ax * x0 + ay * y0))
        xs = [v[0] for v in self.verts]
        ys = [v[1] for v in self.verts]
        self.bbox = (min(xs), max(xs), min(ys), max(ys))

    @staticmethod
    def rect(x0, y0, x1, y1):
        return Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


class _FloatRegion:
    """float view of a Region for the float-mode certifier."""
    __slots__ = ('verts', 'normals', 'bbox')

    def __init__(self, D):
        self.verts = [(float(x), float(y)) for (x, y) in D.verts]
        self.normals = [(float(ax), float(ay), float(su)) for (ax, ay, su) in D.normals]
        self.bbox = tuple(float(v) for v in D.bbox)


# ---------------------------------------------------------------- the certifier
class Certifier:
    def __init__(self, s, placed, mode='exact', depth_max=42, tscale=F(3, 2),
                 float_eps=1e-9, max_cached=400):
        self.s = F(s)
        self.placed = placed
        self.mode = mode
        self.depth_max = depth_max
        self.tscale = F(tscale)
        self.eps = float_eps
        self.max_cached = max_cached
        for P in placed:
            if not P.points:
                P.add_grid_points()
            P.points_dyn = []
        self.isf = (mode == 'float')
        if self.isf:
            for P in placed:
                P.f_pts_x = np.array([float(x) for (x, y) in P.points])
                P.f_pts_y = np.array([float(y) for (x, y) in P.points])
                P.f_c, P.f_s = float(P.c), float(P.s)
                P.f_cx, P.f_cy = float(P.cx), float(P.cy)
        self.stats = None

    # -- (V) admissibility clip:  returns clipped centre box or None (vacuous)
    def _clip(self, t0, t1, x0, x1, y0, y1):
        c0, s0 = cos_sin(t0)
        c1, s1 = cos_sin(t1)
        wlo = min(c0 + s0, c1 + s1)
        lo = wlo / 2
        hi = self.s - lo
        x0c, x1c = max(x0, lo), min(x1, hi)
        y0c, y1c = max(y0, lo), min(y1, hi)
        if x0c > x1c or y0c > y1c:
            return None
        return x0c, x1c, y0c, y1c

    # -- interval body coords of point p over the box (C,S enclosures precomputed)
    @staticmethod
    def _uv_intervals(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1):
        dx0, dx1 = px - x1, px - x0
        dy0, dy1 = py - y1, py - y0
        a0, a1 = imul(Cl, Ch, dx0, dx1)
        b0, b1 = imul(Sl, Sh, dy0, dy1)
        ulo, uhi = a0 + b0, a1 + b1
        a0, a1 = imul(-Sh, -Sl, dx0, dx1)
        b0, b1 = imul(Cl, Ch, dy0, dy1)
        return ulo, uhi, a0 + b0, a1 + b1

    # -- (D) disjoint-from-D test
    def _disjoint_from_D(self, D, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
        # Q-frame axes: every vertex beyond one edge of Q, for all params
        need = 4 * [True]        # u>1/2, u<-1/2, v>1/2, v<-1/2 still alive
        for (px, py) in D.verts:
            ulo, uhi, vlo, vhi = self._uv_intervals(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1)
            if need[0] and not (ulo >= half):
                need[0] = False
            if need[1] and not (uhi <= -half):
                need[1] = False
            if need[2] and not (vlo >= half):
                need[2] = False
            if need[3] and not (vhi <= -half):
                need[3] = False
            if not any(need):
                break
        if any(need):
            return True
        # D-frame axes: Q entirely beyond an edge of D
        for (ax, ay, supp) in D.normals:
            e1lo, e1hi = imul(Cl, Ch, ax, ax)
            t2lo, t2hi = imul(Sl, Sh, ay, ay)
            e1lo, e1hi = e1lo + t2lo, e1hi + t2hi          # a.(C,S)
            e2alo, e2ahi = imul(Sl, Sh, -ax, -ax)
            t3lo, t3hi = imul(Cl, Ch, ay, ay)
            e2lo, e2hi = e2alo + t3lo, e2ahi + t3hi        # a.(-S,C)
            r = (max(abs(e1lo), abs(e1hi)) + max(abs(e2lo), abs(e2hi))) / 2
            # min over box of a.c
            acmin = (ax * x0 if ax >= 0 else ax * x1) + (ay * y0 if ay >= 0 else ay * y1)
            if acmin - r >= supp:
                return True
        return False

    # -- (O) overlap-with-placed tests
    def _point_in_Q_whole_box(self, px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
        ulo, uhi, vlo, vhi = self._uv_intervals(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1)
        return -half <= ulo and uhi <= half and -half <= vlo and vhi <= half


    @staticmethod
    def _np_points_in_Q(pxs, pys, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
        """vectorised: mask of points p with p in Q(c,t) for EVERY (t,c) in the box."""
        dx0 = pxs - x1; dx1 = pxs - x0
        dy0 = pys - y1; dy1 = pys - y0
        # interval product [Cl,Ch] (>=0) x [dx0,dx1]
        a0 = np.minimum(Cl * dx0, Ch * dx0); a1 = np.maximum(Cl * dx1, Ch * dx1)
        b0 = np.minimum(Sl * dy0, Sh * dy0); b1 = np.maximum(Sl * dy1, Sh * dy1)
        ulo = a0 + b0; uhi = a1 + b1
        # v = -S dx + C dy ; [-Sh,-Sl] (<=0) x [dx0,dx1]
        c0 = np.minimum(-Sh * dx1, -Sl * dx1); c1 = np.maximum(-Sh * dx0, -Sl * dx0)
        d0 = np.minimum(Cl * dy0, Ch * dy0); d1 = np.maximum(Cl * dy1, Ch * dy1)
        vlo = c0 + d0; vhi = c1 + d1
        return (ulo >= -half) & (uhi <= half) & (vlo >= -half) & (vhi <= half)

    def _centre_box_in_P(self, P, x0, x1, y0, y1, margin):
        if isinstance(P, PlacedBox):
            return all(P.strictly_inside(px, py, margin=F(1, 1000))
                       for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)))
        h = (HALF - margin) if self.mode == 'exact' else (0.5 - margin)
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            dx, dy = px - P.cx, py - P.cy
            u = P.c * dx + P.s * dy
            if not (-h <= u <= h):
                return False
            v = -P.s * dx + P.c * dy
            if not (-h <= v <= h):
                return False
        return True

    def _overlap_certified(self, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half, tm, xm, ym):
        # 1. cheap: centre box strictly inside a placed square
        m = F(1, 1000) if self.mode == 'exact' else 1e-6
        for P in self.placed:
            if self._centre_box_in_P(P, x0, x1, y0, y1, m):
                return True
        # 2. cached / static witness points
        if self.isf:
            for P in self.placed:
                if self._np_points_in_Q(P.f_pts_x, P.f_pts_y, Cl, Ch, Sl, Sh,
                                        x0, x1, y0, y1, half).any():
                    return True
                for (px, py) in P.points_dyn:
                    if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
                        return True
        else:
            for P in self.placed:
                for (px, py) in P.points + P.points_dyn:
                    if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
                        return True
        # 3. float-guided fresh candidate (only for smallish boxes)
        if ShPolygon is None:
            return False
        wx, wy, wt = float(x1 - x0), float(y1 - y0), float(Ch - Cl) + float(Sh - Sl)
        r_need = 0.5 * (wx + wy) + 0.7072 * wt + 1e-6
        if r_need > 0.35:
            return False
        th = 2 * math.atan(float(tm))
        c, s = math.cos(th), math.sin(th)
        cx, cy = float(xm), float(ym)
        Q = ShPolygon([(cx + c * u - s * v, cy + s * u + c * v)
                       for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))])
        Qin = Q.buffer(-r_need)
        if Qin.is_empty:
            return False
        for P in self.placed:
            inter = Qin.intersection(P.fpoly().buffer(-2e-3))
            if inter.is_empty or inter.area <= 0:
                continue
            pt = inter.representative_point()
            px = F(pt.x).limit_denominator(10 ** 7)
            py = F(pt.y).limit_denominator(10 ** 7)
            if not P.strictly_inside(px, py):
                continue
            if not self.mode == 'exact':
                px, py = float(px), float(py)
            if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
                if len(P.points_dyn) < self.max_cached:
                    P.points_dyn.append((px, py))
                return True
        return False

    # -- main entry
    def certify(self, D, max_boxes=2_000_000):
        """Returns dict(passed=bool, boxes=..., witness=... or None)."""
        exact = self.mode == 'exact'
        s = self.s if exact else float(self.s)
        half = HALF if exact else 0.5 - self.eps      # containment: conservative shrink
        halfD = HALF if exact else 0.5 + self.eps     # disjointness: conservative grow
        bx0, bx1, by0, by1 = D.bbox
        infl = INFLATE if exact else float(INFLATE)
        one, zero = (F(1), F(0)) if exact else (1.0, 0.0)
        lo_adm = (one / 2) if exact else 0.5
        x0 = max(bx0 - infl if exact else float(bx0) - infl, lo_adm)
        x1 = min(bx1 + infl if exact else float(bx1) + infl, s - lo_adm)
        y0 = max(by0 - infl if exact else float(by0) - infl, lo_adm)
        y1 = min(by1 + infl if exact else float(by1) + infl, s - lo_adm)
        if exact:
            Dv = D
        else:
            Dv = _FloatRegion(D)
        n_boxes = n_vac = n_dis = n_ovl = 0
        maxdepth = 0
        if x0 > x1 or y0 > y1:
            return dict(passed=True, boxes=0, witness=None, note='no admissible centre near D')
        stack = [(0, zero, one, x0, x1, y0, y1)]
        while stack:
            if n_boxes >= max_boxes:
                return dict(passed=False, boxes=n_boxes, witness='max_boxes',
                            maxdepth=maxdepth)
            depth, t0, t1, x0, x1, y0, y1 = stack.pop()
            n_boxes += 1
            maxdepth = max(maxdepth, depth)
            clip = self._clip_m(t0, t1, x0, x1, y0, y1)
            if clip is None:
                n_vac += 1
                continue
            x0, x1, y0, y1 = clip
            # trig enclosures
            c0, s0 = self._cs(t0)
            c1, s1 = self._cs(t1)
            Cl, Ch = c1, c0
            Sl, Sh = s0, s1
            if not exact:
                Cl -= self.eps; Ch += self.eps; Sl = max(0.0, Sl - self.eps); Sh += self.eps
            if self._disjoint_from_D(Dv, Cl, Ch, Sl, Sh, x0, x1, y0, y1, halfD):
                n_dis += 1
                continue
            tm = (t0 + t1) / 2
            xm = (x0 + x1) / 2
            ym = (y0 + y1) / 2
            if self._overlap_certified(Cl, Ch, Sl, Sh, x0, x1, y0, y1, half, tm, xm, ym):
                n_ovl += 1
                continue
            if depth >= self.depth_max:
                wit = (float(tm), float(xm), float(ym))
                self.stats = dict(boxes=n_boxes, vac=n_vac, dis=n_dis, ovl=n_ovl)
                return dict(passed=False, boxes=n_boxes, witness=wit, maxdepth=depth)
            # bisect widest
            wt = (t1 - t0) * self.tscale if exact else (t1 - t0) * float(self.tscale)
            wx, wy = x1 - x0, y1 - y0
            if wt >= wx and wt >= wy:
                stack.append((depth + 1, t0, tm, x0, x1, y0, y1))
                stack.append((depth + 1, tm, t1, x0, x1, y0, y1))
            elif wx >= wy:
                stack.append((depth + 1, t0, t1, x0, xm, y0, y1))
                stack.append((depth + 1, t0, t1, xm, x1, y0, y1))
            else:
                stack.append((depth + 1, t0, t1, x0, x1, y0, ym))
                stack.append((depth + 1, t0, t1, x0, x1, ym, y1))
        self.stats = dict(boxes=n_boxes, vac=n_vac, dis=n_dis, ovl=n_ovl)
        return dict(passed=True, boxes=n_boxes, witness=None, maxdepth=maxdepth)


    # -- cheap NEGATIVE filter (float; never used for certification):
    def quick_cover(self, px, py, nt=13, na=7, margin=1e-7):
        """try to find a LEGAL placement covering (px,py); returns True/False.
        Finding one proves the point is NOT dead (up to the float margin); not
        finding one proves nothing.  Fully vectorised."""
        sf = float(self.s)
        if not hasattr(self, '_fplaced'):
            # A25 patch: use each obstacle's OWN (normalised) edge normals as SAT
            # axes rather than the midpoint-placement frame.  For a Placed unit
            # square this is identical to A23; for a PlacedBox (whose `corners`
            # are the axis-aligned hull of the core) it is the correct axis set.
            # quick_cover is a NEGATIVE filter only (a reported legal placement
            # merely drops a cell), so either way the mapped area stays a lower
            # bound; the patch simply makes the filter sharper for PlacedBox.
            self._fplaced = []
            for P in self.placed:
                # For a PlacedBox use the MIDPOINT realisation, not the hull:
                # quick_cover is a negative filter, and exhibiting a square legal
                # for ONE realisation of the core already proves the probed point
                # is not dead for the core-box hypothesis.  (Using the hull would
                # be sound too but is far weaker -- it made interior cells cost
                # 1500-box certifications each.)
                PC = np.array([[float(x), float(y)]
                               for (x, y) in getattr(P, 'filter_corners', P.corners)])
                ax = []
                for i in range(len(PC)):
                    e = PC[(i + 1) % len(PC)] - PC[i]
                    n = math.hypot(e[0], e[1])
                    if n > 1e-12:
                        ax.append((-e[1] / n, e[0] / n))
                self._fplaced.append((PC, tuple(ax)))
            g = np.linspace(-0.47, 0.47, na)
            A, B = np.meshgrid(g, g)
            self._qc_ab = np.stack([A.ravel(), B.ravel()], 1)      # (na^2, 2)
            self._qc_uv = np.array([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]])
        px, py = float(px), float(py)
        ab = self._qc_ab
        for t in np.linspace(0.0, 1.0, nt):
            th = 2 * math.atan(t)
            c, sn = math.cos(th), math.sin(th)
            w2 = (c + sn) / 2
            cx = px - (c * ab[:, 0] - sn * ab[:, 1])
            cy = py - (sn * ab[:, 0] + c * ab[:, 1])
            adm = (cx >= w2 + 1e-9) & (cx <= sf - w2 - 1e-9) &                   (cy >= w2 + 1e-9) & (cy <= sf - w2 - 1e-9)
            if not adm.any():
                continue
            cx, cy = cx[adm], cy[adm]
            # corners of all candidate squares: (m,4,2)
            ru = self._qc_uv @ np.array([[c, sn], [-sn, c]])       # rotated offsets (4,2)
            QX = cx[:, None] + ru[None, :, 0]
            QY = cy[:, None] + ru[None, :, 1]
            ok = np.ones(len(cx), dtype=bool)
            for (PC, pax) in self._fplaced:
                gap = np.full(len(cx), -1e18)
                for (ax, ay) in ((c, sn), (-sn, c)) + pax:
                    pa = QX * ax + QY * ay                          # (m,4)
                    pb = PC[:, 0] * ax + PC[:, 1] * ay              # (4,)
                    g1 = pb.min() - pa.max(1)
                    g2 = pa.min(1) - pb.max()
                    gap = np.maximum(gap, np.maximum(g1, g2))
                ok &= gap > margin
                if not ok.any():
                    break
            if ok.any():
                return True
        return False

    # mode-dispatched helpers
    def _cs(self, t):
        if self.mode == 'exact':
            return cos_sin(t)
        tt = t * t
        return (1 - tt) / (1 + tt), 2 * t / (1 + tt)

    def _clip_m(self, t0, t1, x0, x1, y0, y1):
        if self.mode == 'exact':
            return self._clip(t0, t1, x0, x1, y0, y1)
        c0, s0 = self._cs(t0)
        c1, s1 = self._cs(t1)
        wlo = min(c0 + s0, c1 + s1) - self.eps
        lo = wlo / 2
        s = float(self.s)
        hi = s - lo
        x0c, x1c = max(x0, lo), min(x1, hi)
        y0c, y1c = max(y0, lo), min(y1, hi)
        if x0c > x1c or y0c > y1c:
            return None
        return x0c, x1c, y0c, y1c


def _sat_gap(A, ca, sa, B, cb, sb):
    """float SAT signed separation of two unit squares given corner arrays (4,2)."""
    best = -1e18
    for (ax, ay) in ((ca, sa), (-sa, ca), (cb, sb), (-sb, cb)):
        pa = A[:, 0] * ax + A[:, 1] * ay
        pb = B[:, 0] * ax + B[:, 1] * ay
        gap = max(pb.min() - pa.max(), pa.min() - pb.max())
        if gap > best:
            best = gap
    return best


# ---------------------------------------------------------------- config helpers
def tilted_square_on_wall(t, d, X0):
    """square with tan(theta/2) = t whose LOWEST corner is at (X0, d) (bottom wall y=0).
    Returns Placed.  For theta in (0,90deg) the lowest corner is body corner (-1/2,-1/2):
    c = (X0 + (cos-sin)/2 ... ) wait: L = c + R(-1/2,-1/2) = (cx - (cos-sin)/2, cy - (sin+cos)/2)."""
    t = F(t)
    c, s = cos_sin(t)
    cx = F(X0) + (c - s) / 2
    cy = F(d) + (c + s) / 2
    return Placed(cx, cy, t)


def upright_square(x0, y0):
    """upright unit square with lower-left corner (x0, y0)."""
    return Placed(F(x0) + HALF, F(y0) + HALF, 0)


def poly_disjoint_from_placed(D, placed):
    """exact check that region D is interior-disjoint from every placed square
    (separating axis with non-strict inequality: touching allowed)."""
    for P in placed:
        if not _convex_interior_disjoint(D.verts, P.corners):
            return False
    return True


def _convex_interior_disjoint(A, B):
    """True iff convex polygons A, B (rational vertex lists) have disjoint interiors:
    SAT with non-strict separation (a supporting axis with gap >= 0)."""
    for (P1, P2) in ((A, B), (B, A)):
        n = len(P1)
        for i in range(n):
            x0, y0 = P1[i]
            x1, y1 = P1[(i + 1) % n]
            ax, ay = (y1 - y0), -(x1 - x0)
            supp = max(ax * x + ay * y for (x, y) in P1)
            other = min(ax * x + ay * y for (x, y) in P2)
            if other >= supp:
                return True
    return False
