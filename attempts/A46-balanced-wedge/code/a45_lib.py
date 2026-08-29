#!/usr/bin/env python3
"""
a45_lib.py -- A45 interface charge table: frames, moat ladder, charge maps.

Everything here is built on top of A23's certifier (dead_region.py) and A25's
tiling patterns (atlas_lib.py / wastage.py), COPIED verbatim into this directory.
Nothing in A25 is modified.

FRAMES (spec sect.5).  Big container S = 20, contact point p FIXED in the frame
(so that the moat box B(p,rho) is a fixed rational box while the hypothesis
squares move over the bin).  Lemma P' margin asserted per run.

  WC(phi-bin): square a with its lowest corner at p = (10, 0) on the BOTTOM wall
      of [0,20]^2, tilt phi in the bin.  Hypothesis = {a} + the bottom wall (which
      is the container constraint itself).  The other three walls are unreachable
      (asserted).
  CE(d-bin, u-bin): a's lowest corner at p = (10,10), tilt d; b upright with its
      TOP EDGE on the line y = 10 and centre (10 - u, 9.5), so p = b_topedge
      midpoint + (u, 0).  u in [-1/2,1/2].
  CC(delta-bin): a upright with its corner at p = (10,10) (a = [10,11]^2);
      b with a corner at p occupying the cone [delta, delta+90], delta in [90,180].

All three are PLANE-MODE certificates (Lemma P/P'); CE and CC are additionally
rotation-reduced (plane mode is isometry invariant, so only the RELATIVE angles
matter -- that is why CE has 2 parameters and CC has 1).

BIN UNIFORMITY.  A bin is covered by `nsub` sub-boxes; a moat / tile counts for
the bin only if it certifies on EVERY sub-box.  Each sub-box is a PlacedBox
(A25 core-box-uniform semantics), built by OUTWARD-rounded rational interval
arithmetic on (cos, sin) -- a hull relaxation, which only weakens.

Author: A45 agent A, 2026-08-29.
"""
from __future__ import annotations

import math
import time
from fractions import Fraction as F

import numpy as np

from dead_region import (Certifier, Placed, PlacedBox, Region, cos_sin,
                         _convex_interior_disjoint)
from atlas_lib import tanhalf, _mid_corners, merge_rects
from wastage import _cell_disjoint_placed

HALF = F(1, 2)
S_BIG = F(20)
PX = F(10)
PY = F(10)
INFL = F(7072, 10000)                     # > sqrt(2)/2, the certifier's root inflation
LADDER = [F(1, 4), F(3, 16), F(1, 8), F(3, 32), F(1, 16)]
RMAX = F(1, 8)                            # = max(LADDER)/2: master charge-box radius


# ------------------------------------------------------------------ intervals
def cs_iv(t0, t1):
    """outward (in fact exact) enclosure (cl,ch,sl,sh) of (cos,sin) over
    t = tan(theta/2) in [t0,t1] subset [0,1] (theta in [0,90]):
    cos is decreasing, sin increasing."""
    c0, s0 = cos_sin(F(t0))
    c1, s1 = cos_sin(F(t1))
    return c1, c0, s0, s1


def deg_t(d0, d1):
    """rational t-interval OUTWARD-rounding the degree interval [d0,d1]."""
    return tanhalf(d0, up=False), tanhalf(d1, up=True)


# ------------------------------------------------------------------ frames
def wc_box(t0, t1):
    """PlacedBox for the WC square: lowest corner at p=(10,0), t in [t0,t1]."""
    cl, ch, sl, sh = cs_iv(t0, t1)
    A = PlacedBox(t0, t1, PX + (cl - sh) / 2, PX + (ch - sl) / 2,
                  (cl + sl) / 2, (ch + sh) / 2)
    A.filter_corners = _mid_corners(A)
    return A


def ce_boxes(t0, t1, u0, u1):
    """(a-box, b-box) for CE: a's lowest corner at p=(10,10) with tilt-t in
    [t0,t1]; b upright, top edge on y=10, centre (10-u, 9.5), u in [u0,u1]."""
    cl, ch, sl, sh = cs_iv(t0, t1)
    A = PlacedBox(t0, t1, PX + (cl - sh) / 2, PX + (ch - sl) / 2,
                  PY + (cl + sl) / 2, PY + (ch + sh) / 2)
    B = PlacedBox(0, 0, PX - F(u1), PX - F(u0), PY - HALF, PY - HALF)
    A.filter_corners = _mid_corners(A)
    B.filter_corners = _mid_corners(B)
    return A, B


def cc_boxes(t0, t1):
    """(a, b-box) for CC: a = upright [10,11]^2 (corner at p, cone [0,90]);
    b has a corner at p and occupies the cone [delta, delta+90] where
    delta = 90 + theta_b, theta_b = 2*atan(t), t in [t0,t1]."""
    A = Placed(PX + HALF, PY + HALF, 0)
    cl, ch, sl, sh = cs_iv(t0, t1)
    # centre_b = p + R_delta(1/2,1/2), cos delta = -sin th, sin delta = cos th
    #          = p + ( (-s-c)/2 , (c-s)/2 )
    B = PlacedBox(t0, t1, PX + (-sh - ch) / 2, PX + (-sl - cl) / 2,
                  PY + (cl - sh) / 2, PY + (ch - sl) / 2)
    B.filter_corners = _mid_corners(B)
    return A, B


def subbins(lo, hi, n):
    lo, hi = F(lo), F(hi)
    return [(lo + (hi - lo) * i / n, lo + (hi - lo) * (i + 1) / n) for i in range(n)]


def build_configs(kind, bin_, nsub=1, nsub_u=1):
    """Return a list of dicts {placed, tag, meta} whose union of hypotheses
    CONTAINS the bin.  A certificate holding on every element holds on the bin."""
    out = []
    if kind == 'WC':
        d0, d1 = bin_['phi']
        for (a0, a1) in subbins(d0, d1, nsub):
            t0, t1 = deg_t(float(a0), float(a1))
            out.append(dict(placed=[wc_box(t0, t1)], t=(t0, t1), deg=(a0, a1)))
    elif kind == 'CE':
        d0, d1 = bin_['d']
        u0, u1 = bin_['u']
        for (a0, a1) in subbins(d0, d1, nsub):
            t0, t1 = deg_t(float(a0), float(a1))
            for (v0, v1) in subbins(u0, u1, nsub_u):
                A, B = ce_boxes(t0, t1, v0, v1)
                out.append(dict(placed=[A, B], t=(t0, t1), deg=(a0, a1), u=(v0, v1)))
    elif kind == 'CC':
        d0, d1 = bin_['delta']
        for (a0, a1) in subbins(d0, d1, nsub):
            t0, t1 = deg_t(float(a0) - 90.0, float(a1) - 90.0)
            A, B = cc_boxes(t0, t1)
            out.append(dict(placed=[A, B], t=(t0, t1), deg=(a0, a1)))
    else:
        raise ValueError(kind)
    return out


CONTACT_P = dict(WC=(PX, F(0)), CE=(PX, PY), CC=(PX, PY))
CLIP_Y0 = dict(WC=F(0), CE=None, CC=None)


# ------------------------------------------------------------------ Lemma P'
def assert_margin(kind, region_bbox):
    """Lemma P' duty: bbox(D) inflated by INFLATE must sit > 1 from every wall of
    [0,S]^2 that is NOT the hypothesis wall.  Raises AssertionError otherwise."""
    x0, x1, y0, y1 = region_bbox
    lo_x, hi_x = x0 - INFL, x1 + INFL
    lo_y, hi_y = y0 - INFL, y1 + INFL
    assert lo_x > 1, f'{kind}: left wall margin {float(lo_x)}'
    assert hi_x < S_BIG - 1, f'{kind}: right wall margin {float(S_BIG - hi_x)}'
    assert hi_y < S_BIG - 1, f'{kind}: top wall margin {float(S_BIG - hi_y)}'
    if kind != 'WC':
        assert lo_y > 1, f'{kind}: bottom wall margin {float(lo_y)}'
    return dict(left=str(lo_x), right=str(S_BIG - hi_x), top=str(S_BIG - hi_y),
                bottom=('WALL (hypothesis)' if kind == 'WC' else str(lo_y)))


# ------------------------------------------------------------------ realisability
def realisable(kind, bin_):
    """Exhibit ONE exactly-touching rational realisation inside the bin hull, and
    check the pair's interiors are disjoint EXACTLY.  Returns (ok, detail)."""
    if kind == 'WC':
        d0, d1 = bin_['phi']
        t = tanhalf((float(d0) + float(d1)) / 2, up=False)
        if t <= 0:
            return False, 'phi = 0: WF not WC'
        A = Placed(PX + (cos_sin(t)[0] - cos_sin(t)[1]) / 2,
                   (cos_sin(t)[0] + cos_sin(t)[1]) / 2, t)
        # corner exactly on the wall y = 0, and the square inside y >= 0
        touch = min(c[1] for c in A.corners) == 0
        return bool(touch), dict(t=str(t), corner_on_wall=bool(touch))
    if kind == 'CE':
        d0, d1 = bin_['d']
        u0, u1 = bin_['u']
        t = tanhalf((float(d0) + float(d1)) / 2, up=False)
        u = (F(u0) + F(u1)) / 2
        c, s = cos_sin(t)
        A = Placed(PX + (c - s) / 2, PY + (c + s) / 2, t)
        B = Placed(PX - u, PY - HALF, 0)
        low = min(A.corners, key=lambda q: (q[1], q[0]))
        on_edge = (low[1] == PY) and (PX - u - HALF <= low[0] <= PX - u + HALF)
        dis = _convex_interior_disjoint(A.corners, B.corners)
        strict = (PX - u - HALF < low[0] < PX - u + HALF)
        return bool(on_edge and dis and strict), dict(
            t=str(t), u=str(u), corner=[str(low[0]), str(low[1])],
            on_edge=bool(on_edge), strict_interior_of_edge=bool(strict),
            interiors_disjoint=bool(dis))
    if kind == 'CC':
        d0, d1 = bin_['delta']
        t = tanhalf((float(d0) + float(d1)) / 2 - 90.0, up=False)
        A, _ = cc_boxes(t, t)
        c, s = cos_sin(t)
        B = Placed(PX + (-s - c) / 2, PY + (c - s) / 2, t)
        share = (PX, PY) in A.corners and (PX, PY) in B.corners
        dis = _convex_interior_disjoint(A.corners, B.corners)
        return bool(share and dis), dict(t=str(t), shared_corner=bool(share),
                                         interiors_disjoint=bool(dis))
    raise ValueError(kind)


# ------------------------------------------------------------------ Lemma K
def keeper_wc(configs):
    """WC: region must sit inside slab(wall, bbox_along_wall(a)) for EVERY
    realisation -- x in [max(10 - sin phi), min(10 + cos phi)], 0 <= y <= min h(a).
    Both bounds taken over the whole bin (intersection of the slabs)."""
    xlo = max(PX - cs_iv(*cfg['t'])[2] for cfg in configs)       # 10 - min sin
    xhi = min(PX + cs_iv(*cfg['t'])[0] for cfg in configs)       # 10 + min cos
    yhi = min(cs_iv(*cfg['t'])[0] + cs_iv(*cfg['t'])[2] for cfg in configs)

    def keep(x0, y0, x1, y1):
        return x0 >= xlo and x1 <= xhi and y0 >= 0 and y1 <= yhi
    keep.info = dict(rule='slab', xlo=str(xlo), xhi=str(xhi), yhi=str(yhi))
    return keep


def _guaranteed_points(configs, kind):
    """A set S of points with S subset (a cup b) for EVERY realisation of the bin.
    conv(S) subset conv(a cup b), so `region subset conv(S)` implies Lemma K."""
    p = CONTACT_P[kind]
    pts = [p]
    if kind == 'CE':
        # b is upright with top edge y=10; the guaranteed rectangle is the
        # intersection over the u-range.
        bx0 = max(cfg['placed'][1].bx1 for cfg in configs) - HALF
        bx1 = min(cfg['placed'][1].bx0 for cfg in configs) + HALF
        if bx1 > bx0:
            pts += [(bx0, PY - 1), (bx1, PY - 1), (bx0, PY), (bx1, PY)]
        boxes = [cfg['placed'][0] for cfg in configs]
    else:                                              # CC: a is FIXED
        pts += [(PX, PY), (PX + 1, PY), (PX + 1, PY + 1), (PX, PY + 1)]
        boxes = [cfg['placed'][1] for cfg in configs]
    # points of the moving square certified interior for every sub-box
    for lam in (F(97, 100), F(9, 10), F(3, 4), HALF):
        for (u, v) in ((-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF),
                       (0, -HALF), (0, HALF), (-HALF, 0), (HALF, 0)):
            B0 = boxes[0]
            q = (B0.cx + B0.c * (u * lam) - B0.s * (v * lam),
                 B0.cy + B0.s * (u * lam) + B0.c * (v * lam))
            if all(B.strictly_inside(q[0], q[1], margin=0) for B in boxes):
                pts.append(q)
    return pts


def _hull(pts):
    """monotone-chain convex hull of exact rational points, CCW."""
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2:
                (x0, y0), (x1, y1) = out[-2], out[-1]
                if (x1 - x0) * (q[1] - y0) - (y1 - y0) * (q[0] - x0) <= 0:
                    out.pop()
                else:
                    break
            out.append(q)
        return out
    lo = half(pts)
    hi = half(pts[::-1])
    return lo[:-1] + hi[:-1]


def keeper_hull(configs, kind):
    """CE/CC: region subset conv(S) with S a guaranteed subset of a cup b."""
    H = _hull(_guaranteed_points(configs, kind))
    n = len(H)
    edges = []
    for i in range(n):
        x0, y0 = H[i]
        x1, y1 = H[(i + 1) % n]
        ax, ay = (y1 - y0), -(x1 - x0)          # OUTWARD normal for CCW
        edges.append((ax, ay, ax * x0 + ay * y0))

    def keep(x0, y0, x1, y1):
        for (ax, ay, su) in edges:
            for (qx, qy) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
                if ax * qx + ay * qy > su:
                    return False
        return True
    keep.info = dict(rule='conv(guaranteed subset of a cup b)',
                     hull=[[str(x), str(y)] for (x, y) in H])
    return keep


def make_keeper(kind, configs):
    return keeper_wc(configs) if kind == 'WC' else keeper_hull(configs, kind)


# ------------------------------------------------------------------ certifiers
class FastExactCertifier(Certifier):
    """A23's EXACT certifier with one performance-only change: the static witness
    points are pre-screened in floats before the exact test.

    SOUNDNESS.  The float screen only chooses WHICH candidate point to test; the
    ACCEPT decision is still the exact `_point_in_Q_whole_box`, and the screen is
    deliberately GENEROUS (half = 1/2 + 1e-7 against float errors of order 1e-15,
    box and trig endpoints widened), so no point that would pass the exact test is
    ever screened out.  Discharge rules (V), (D), the cheap centre-box test and the
    shapely-guided fresh candidate are the parent's, unchanged.  Worst case the
    screen lets a point through that then fails exactly -- identical behaviour to
    the parent, just slower.  Motivation: in exact mode the parent spends ~500
    big-Fraction point tests per B&B box, which dominates everything else.
    """

    _FEPS = 1e-7

    def _fpts(self, P):
        if not hasattr(P, '_a45_fx'):
            P._a45_fx = np.array([float(x) for (x, y) in P.points])
            P._a45_fy = np.array([float(y) for (x, y) in P.points])
        return P._a45_fx, P._a45_fy

    def _overlap_certified(self, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half, tm, xm, ym):
        for P in self.placed:                       # (1) cheap centre-box test
            if self._centre_box_in_P(P, x0, x1, y0, y1, F(1, 1000)):
                return True
        e = self._FEPS
        fCl, fCh = float(Cl) - e, float(Ch) + e
        fSl, fSh = float(Sl) - e, float(Sh) + e
        fx0, fx1 = float(x0) - e, float(x1) + e
        fy0, fy1 = float(y0) - e, float(y1) + e
        fhalf = 0.5 + e
        for P in self.placed:                       # (2) screened witness points
            if P.points:
                fx, fy = self._fpts(P)
                m = self._np_points_in_Q(fx, fy, fCl, fCh, fSl, fSh,
                                         fx0, fx1, fy0, fy1, fhalf)
                for idx in np.flatnonzero(m):
                    px, py = P.points[int(idx)]
                    if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh,
                                                  x0, x1, y0, y1, half):
                        return True
            for (px, py) in P.points_dyn:
                if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh,
                                              x0, x1, y0, y1, half):
                    return True
        return self._fresh_candidate(Cl, Ch, Sl, Sh, x0, x1, y0, y1, half, tm, xm, ym)

    def _fresh_candidate(self, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half, tm, xm, ym):
        """the parent's step 3 verbatim (shapely-guided, exact accept)."""
        from dead_region import ShPolygon
        if ShPolygon is None:
            return False
        wx, wy = float(x1 - x0), float(y1 - y0)
        wt = float(Ch - Cl) + float(Sh - Sl)
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
            if self._point_in_Q_whole_box(px, py, Cl, Ch, Sl, Sh, x0, x1, y0, y1, half):
                if len(P.points_dyn) < self.max_cached:
                    P.points_dyn.append((px, py))
                return True
        return False


def certifiers(configs, mode, depth_max, fast_exact=True):
    cls = FastExactCertifier if (mode == 'exact' and fast_exact) else Certifier
    return [cls(S_BIG, cfg['placed'], mode=mode, depth_max=depth_max)
            for cfg in configs]


def region_ok_all(D, certs, max_boxes):
    for c in certs:
        if not c.certify(D, max_boxes=max_boxes)['passed']:
            return False
    return True


# ------------------------------------------------------------------ moat ladder
def moat(kind, configs, rho, mode='float', depth_max=30, max_boxes=40000):
    """Certify D = B(p,rho) cap container dead for the whole bin.
    Returns dict(passed, seconds, boxes)."""
    px, py = CONTACT_P[kind]
    y0 = px * 0 + (py - rho)
    if CLIP_Y0[kind] is not None:
        y0 = max(y0, CLIP_Y0[kind])
    bbox = (px - rho, px + rho, y0, py + rho)
    margin = assert_margin(kind, bbox)
    D = Region.rect(bbox[0], bbox[2], bbox[1], bbox[3])
    t0 = time.time()
    boxes = 0
    cls = FastExactCertifier if mode == 'exact' else Certifier
    for cfg in configs:
        c = cls(S_BIG, cfg['placed'], mode=mode, depth_max=depth_max)
        r = c.certify(D, max_boxes=max_boxes)
        boxes += r['boxes']
        if not r['passed']:
            return dict(passed=False, rho=str(rho), seconds=round(time.time() - t0, 2),
                        boxes=boxes, witness=r.get('witness'), margin=margin,
                        failed_sub=[str(v) for v in cfg.get('deg', ())],
                        failed_sub_u=[str(v) for v in cfg.get('u', ())])
    return dict(passed=True, rho=str(rho), seconds=round(time.time() - t0, 2),
                boxes=boxes, margin=margin)


def moat_ladder(kind, configs, ladder=LADDER, mode='float', depth_max=30,
                max_boxes=40000, log=None):
    """Largest rho in the ladder whose moat certifies.  Returns (rho or None, runs)."""
    runs = []
    for rho in ladder:
        r = moat(kind, configs, rho, mode=mode, depth_max=depth_max, max_boxes=max_boxes)
        runs.append(r)
        if log:
            log(f'    moat rho={rho} -> {"PASS" if r["passed"] else "fail"} '
                f'({r["seconds"]}s, {r["boxes"]} boxes)')
        if r['passed']:
            return rho, runs
    return None, runs


# ------------------------------------------------------------------ charge map
def _tiles(px, py, R, cell0, clip_y0):
    n = int(R / cell0)
    assert n * cell0 == R, 'cell0 must divide R'
    out = []
    for i in range(-n, n):
        for j in range(-n, n):
            x0, x1 = px + i * cell0, px + (i + 1) * cell0
            y0, y1 = py + j * cell0, py + (j + 1) * cell0
            if clip_y0 is not None:
                y0 = max(y0, clip_y0)
                y1 = max(y1, clip_y0)
            if x1 > x0 and y1 > y0:
                out.append((x0, y0, x1, y1))
    return out


def charge_map(kind, configs, R=RMAX, cell0=F(1, 32), min_cell=F(1, 256),
               mode='float', depth_max=26, max_boxes=3000, keeper=None,
               work_budget=4000):
    """Certified dead tiles inside B(p,R) (cap the container), uniformly over the
    bin, each passing the Lemma-K keeper.  Returns dict(area, cells, stats)."""
    px, py = CONTACT_P[kind]
    clip_y0 = CLIP_Y0[kind]
    keeper = keeper or make_keeper(kind, configs)
    bbox = (px - R, px + R, (py - R if clip_y0 is None else max(py - R, clip_y0)), py + R)
    margin = assert_margin(kind, bbox)
    certs = certifiers(configs, mode, depth_max)
    placed_all = [cfg['placed'] for cfg in configs]
    area = F(0)
    cells = []
    n_pass = n_drop = n_occ = n_key = 0
    work = 0
    t0 = time.time()
    stack = list(_tiles(px, py, R, cell0, clip_y0))
    while stack:
        x0, y0, x1, y1 = stack.pop()
        w, h = x1 - x0, y1 - y0
        if not keeper(x0, y0, x1, y1):
            if max(w, h) > min_cell:
                xm, ym = x0 + w / 2, y0 + h / 2
                stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)]
            else:
                n_key += 1
            continue
        if any(all(P.strictly_inside(qx, qy, margin=0) for (qx, qy) in
                   ((x0, y0), (x1, y0), (x1, y1), (x0, y1))) for pl in placed_all
               for P in pl):
            n_occ += 1
            continue
        if not all(_cell_disjoint_placed(x0, y0, x1, y1, pl) for pl in placed_all):
            if max(w, h) > min_cell:
                xm, ym = x0 + w / 2, y0 + h / 2
                stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                          (x0, ym, xm, y1), (xm, ym, x1, y1)]
            else:
                n_occ += 1
            continue
        if work >= work_budget:
            n_drop += 1
            continue
        work += 1
        alive = False
        if mode == 'float':
            xm, ym = x0 + w / 2, y0 + h / 2
            for (qx, qy) in ((xm, ym), (x0 + w / 4, y0 + h / 4), (x1 - w / 4, y1 - h / 4),
                             (x0 + w / 4, y1 - h / 4), (x1 - w / 4, y0 + h / 4)):
                if any(c.quick_cover(qx, qy) for c in certs):
                    alive = True
                    break
        if not alive:
            D = Region.rect(x0, y0, x1, y1)
            alive = not region_ok_all(D, certs, max_boxes)
        if not alive:
            area += (x1 - x0) * (y1 - y0)
            cells.append((x0, y0, x1, y1))
            n_pass += 1
        elif max(w, h) > min_cell:
            xm, ym = x0 + w / 2, y0 + h / 2
            stack += [(x0, y0, xm, ym), (xm, y0, x1, ym),
                      (x0, ym, xm, y1), (xm, ym, x1, y1)]
        else:
            n_drop += 1
    return dict(area=area, cells=cells,
                stats=dict(n_pass=n_pass, n_drop=n_drop, n_occ=n_occ, n_key=n_key,
                           work=work, seconds=round(time.time() - t0, 2),
                           margin=margin, keeper=getattr(keeper, 'info', None)))


def clip_cells(cells, px, py, R, clip_y0=None):
    """restrict a certified dead tile list to B(p,R): subsets of dead sets are
    dead, so this is sound.  Returns (area, cells)."""
    out = []
    a = F(0)
    lo_x, hi_x, lo_y, hi_y = px - R, px + R, py - R, py + R
    if clip_y0 is not None:
        lo_y = max(lo_y, clip_y0)
    for (x0, y0, x1, y1) in cells:
        u0, u1 = max(x0, lo_x), min(x1, hi_x)
        v0, v1 = max(y0, lo_y), min(y1, hi_y)
        if u1 > u0 and v1 > v0:
            out.append((u0, v0, u1, v1))
            a += (u1 - u0) * (v1 - v0)
    return a, out


def recert_exact(kind, configs, cells, depth_max=40, max_boxes=400000):
    """Fraction re-certification of an identical tile list."""
    certs = certifiers(configs, 'exact', depth_max)
    area = F(0)
    failed = []
    t0 = time.time()
    for (x0, y0, x1, y1) in cells:
        D = Region.rect(x0, y0, x1, y1)
        if region_ok_all(D, certs, max_boxes):
            area += (x1 - x0) * (y1 - y0)
        else:
            failed.append([str(x0), str(y0), str(x1), str(y1)])
    return dict(area=area, failed=failed, seconds=round(time.time() - t0, 2))


# ------------------------------------------------------------------ diagnostics
def full_dead_map(kind, configs, R=HALF, cell0=F(1, 16), min_cell=F(1, 64),
                  mode='float', depth_max=26, max_boxes=3000, work_budget=3000):
    """UNRESTRICTED dead map out to radius R (no Lemma-K keeper): diagnostic only.
    Reports area and the realised extent (bbox of the certified tiles)."""
    r = charge_map(kind, configs, R=R, cell0=cell0, min_cell=min_cell, mode=mode,
                   depth_max=depth_max, max_boxes=max_boxes,
                   keeper=_always, work_budget=work_budget)
    if r['cells']:
        xs0 = min(c[0] for c in r['cells']); xs1 = max(c[2] for c in r['cells'])
        ys0 = min(c[1] for c in r['cells']); ys1 = max(c[3] for c in r['cells'])
        r['extent'] = [str(xs0), str(ys0), str(xs1), str(ys1)]
        px, py = CONTACT_P[kind]
        r['extent_rel'] = [float(xs0 - px), float(ys0 - py), float(xs1 - px), float(ys1 - py)]
    else:
        r['extent'] = None
    return r


def _always(x0, y0, x1, y1):
    return True


_always.info = dict(rule='none (diagnostic)')


def jcells(cells):
    return [[str(a) for a in c] for c in cells]
