"""A116 -- the local certificate: a selection tree around a known minimum.

Shared library.  READ-ONLY on every campaign; nothing here writes outside
attempts/A116-local-selection-tree/{results,logs}.

Objects
  * Body: a unit square whose pose is confined to a box -- FREE (centre box x tilt interval,
    two LP variables x, y) or PIN (centre alpha + beta*s + (u, v), |u|,|v| <= h, tilt exactly 0,
    two LP variables u, v).  Walls are rows, not bodies.
  * the eight signed separating-axis selections of a pair: (owner, axis k, sign eps), row
        eps * (c_other - c_owner) . a_k(theta_owner)  >=  1/2 + w(theta_owner - theta_other)/2,
    w(d) = |cos d| + |sin d|.  Interval enclosure (a111lib.IV / iv_cos / w_range) over a cell;
    affine relaxation over a cell by the CHORD of max(eps*d*A.lo, eps*d*A.hi) in each centre
    component (exact when the sign of the component is constant on the cell -- second-order loss,
    unlike A111's first-order R*Delta chord bound); exact row at a tilt point.
  * the selection tree (Theorem LOCAL): nodes = (tilt cell, partial selection); census -> LP ->
    branch on a near pair -> bisect the tilt cell at full selection; leaves IMPOSSIBLE / DEAD /
    LIVE-LOW (an exact witness packing of L u P at side <= s0) / UNRESOLVED.
  * the stability radii of the minimum's contacts (the PI's route): the largest per-square
    perturbation within which the minimum's selection is FORCED on every disjoint configuration
    (interval bisection over the pair's 6-D pose box), the far radius of a non-contact pair, and
    the first-order estimates from the tangential slack.
  * dense sampling + a box-constrained local minimiser as the measured check of every verdict.
"""
from __future__ import annotations

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  MUST precede numpy

import itertools, json, math, time
import numpy as np
from scipy.optimize import linprog, minimize

BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
for d in (RES, LOGS):
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "attempts", "A111-loadpath-branch", "code"))
import a111lib as L11  # noqa: E402  (IV, iv_cos, iv_sin, w_range, shadows, d4_ops -- read-only)

IV = L11.IV
iv_cos, iv_sin, w_range = L11.iv_cos, L11.iv_sin, L11.w_range

S0 = 969271.0 / 250000.0
SHAT = 3.877083590022814
S_LO = 3.82                       # the window floor
S_HI_DEFAULT = S0 + 0.02          # the LP's side cap: values above it are reported as ">= s0+0.02"
PIN_SLACK = 1e-2 / math.sqrt(2.0)  # A57's delta-cores, half-width delta/sqrt2, delta = 1e-2
THETA_T = 40.181937290329716      # Trump's tilt (A03)

CLASS_PINS = {
    "k5_11": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "BR(0,0)"),
    "k5_16": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BR(0,0)", "TR(0,0)"),
    "trump5": ("BL(0,0)", "BL(1,0)", "BL(0,1)", "BR(0,0)", "TR(0,0)"),
}
# load-bearing squares per shadow (A110 sec 2; slot squares that are load-bearing but not pins of
# the class become FREE bodies with an axis-aligned anchor)
LOADBEARING = {
    "S02": ("f1", "f2", "f3"),                 # + BR(0,1) unless pinned; f0 is the strut
    "S07": ("f0", "f2", "f4"),                 # the x-chain; f1 optional (y-chain, not needed: Lambda >= s*)
}


# ------------------------------------------------------------------ closed forms (A110)
def Lambda(th):
    t = math.cos(th) + math.sin(th)
    return 2 + 4 * t / (t * t + 1)


def F_T(th):
    return 2 + (2 + math.sin(th)) / (math.cos(th) + math.sin(th))


def D_chain(th):
    return 2 + (2 + math.cos(th)) / (math.cos(th) + math.sin(th))


def Y_chain(th):
    c, s = math.cos(th), math.sin(th)
    return (1 + 3 * c + s + 2 * c * s + 2 * s * s) / (1 + c * s)


# ------------------------------------------------------------------ float geometry
def axis(th, k):
    return (math.cos(th), math.sin(th)) if k == 0 else (-math.sin(th), math.cos(th))


def wfun(d):
    return abs(math.cos(d)) + abs(math.sin(d))


def gap_sel(ci, ti, cj, tj, owner, k, eps):
    """signed selection gap; owner 0 = square i."""
    (cw, tw), (co, to) = ((ci, ti), (cj, tj)) if owner == 0 else ((cj, tj), (ci, ti))
    a = axis(tw, k)
    proj = (co[0] - cw[0]) * a[0] + (co[1] - cw[1]) * a[1]
    return eps * proj - 0.5 - 0.5 * wfun(tw - to)


SELS = [(o, k, e) for o in (0, 1) for k in (0, 1) for e in (1, -1)]


def sat_gap(ci, ti, cj, tj):
    return max(gap_sel(ci, ti, cj, tj, o, k, e) for (o, k, e) in SELS)


def sat_best(ci, ti, cj, tj):
    return max(((gap_sel(ci, ti, cj, tj, o, k, e), (o, k, e)) for (o, k, e) in SELS), key=lambda t: t[0])


def corners(c, th):
    co, si = math.cos(th), math.sin(th)
    return [(c[0] + 0.5 * (dx * co - dy * si), c[1] + 0.5 * (dx * si + dy * co))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def half_width(th):
    return 0.5 * wfun(th)


# ------------------------------------------------------------------ interval helpers
def iv_axis(thIV, k):
    return (iv_cos(thIV), iv_sin(thIV)) if k == 0 else (-iv_sin(thIV), iv_cos(thIV))


def w_iv(dIV):
    lo, hi = w_range(dIV.lo, dIV.hi)
    return IV(lo, hi)


def gap_sel_iv(Bi, Bj, owner, k, eps):
    """(interval of the signed selection gap).  B = (xIV, yIV, thIV)."""
    (xw, yw, tw), (xo, yo, to) = (Bi, Bj) if owner == 0 else (Bj, Bi)
    ax, ay = iv_axis(tw, k)
    proj = (xo - xw) * ax + (yo - yw) * ay
    w = w_iv(tw - to)
    g = IV(eps) * proj - IV(0.5) - IV(0.5) * w
    return g


# ------------------------------------------------------------------ bodies
class Body:
    __slots__ = ("name", "kind", "x0", "x1", "y0", "y1", "t0", "t1", "ax", "ay", "hh", "vi", "ti", "anchor")

    def __init__(self, name, kind, **kw):
        self.name, self.kind = name, kind
        for k in ("x0", "x1", "y0", "y1", "t0", "t1", "ax", "ay", "hh", "vi", "ti", "anchor"):
            setattr(self, k, kw.get(k))

    def tilt(self, cells=None):
        if self.kind == "pin":
            return IV(0.0)
        if cells and self.name in cells:
            return IV(*cells[self.name])
        return IV(self.t0, self.t1)

    def xrange(self, s_lo, s_hi):
        if self.kind == "pin":
            return (IV(self.ax[0] + self.ax[1] * s_lo - self.hh, self.ax[0] + self.ax[1] * s_hi + self.hh),
                    IV(self.ay[0] + self.ay[1] * s_lo - self.hh, self.ay[0] + self.ay[1] * s_hi + self.hh))
        return IV(self.x0, self.x1), IV(self.y0, self.y1)

    def pose_iv(self, s_lo, s_hi, cells=None):
        xr, yr = self.xrange(s_lo, s_hi)
        return (xr, yr, self.tilt(cells))

    def centre_affine(self, nv):
        """(coef_x, const_x, coef_y, const_y) as affine maps of the LP variables."""
        cx = np.zeros(nv); cy = np.zeros(nv)
        if self.kind == "pin":
            cx[0] = self.ax[1]; cy[0] = self.ay[1]
            cx[self.vi] = 1.0; cy[self.vi + 1] = 1.0
            return cx, self.ax[0], cy, self.ay[0]
        cx[self.vi] = 1.0; cy[self.vi + 1] = 1.0
        return cx, 0.0, cy, 0.0


def slot_affine(name):
    corner, ij = name[:2], name[3:-1].split(",")
    i, j = int(ij[0]), int(ij[1])
    ax = (0.5 + i, 0.0) if corner in ("BL", "TL") else (-0.5 - i, 1.0)
    ay = (0.5 + j, 0.0) if corner in ("BL", "BR") else (-0.5 - j, 1.0)
    return ax, ay


def slot_xy(name, s):
    ax, ay = slot_affine(name)
    return (ax[0] + ax[1] * s, ay[0] + ay[1] * s)


# ------------------------------------------------------------------ the shadows, anchored
def shadow_poses(tag):
    """(s*, {name: (x, y, theta_rad)}) of the exact minimum, all eleven squares."""
    s, names, cfg, slots, free, lp = L11.shadow(tag)
    return s, {n: cfg[i] for i, n in enumerate(names)}, list(slots), list(free)


def anchored(tag, anchor_side):
    """The shadow's poses in the class frame at side `anchor_side`: free squares DILATED by
    anchor_side/s* (the s0 anchor of the brief), slot squares at their slot positions at
    anchor_side.  anchor_side = s* reproduces the shadow exactly."""
    s_sh, P, slots, free = shadow_poses(tag)
    lam = anchor_side / s_sh
    out = {}
    for n, (x, y, t) in P.items():
        if n in slots:
            out[n] = (slot_xy(n, anchor_side)[0], slot_xy(n, anchor_side)[1], 0.0)
        else:
            out[n] = (x * lam, y * lam, t)
    return s_sh, out, slots, free


def build_bodies(tag, cls, r, rho_deg, anchor_side=S0, pin_slack=PIN_SLACK, extra_free=(),
                 tilt_floor_deg=None, tilt_ceil_deg=None, loadbearing=None, slot_radius=None):
    """Bodies of the local certificate: the class pins (slack cores) + one FREE box per
    load-bearing square (dilated anchor, radius r, tilt half-width rho), the non-pinned load-
    bearing slot squares as axis-aligned free boxes.  tilt_floor/ceil cut the tilt boxes of the
    TILTED free squares (the Trump-boundary cut)."""
    s_sh, P, slots, free = anchored(tag, anchor_side)
    pins = list(CLASS_PINS[cls])
    lb = list(loadbearing if loadbearing is not None else LOADBEARING[tag]) + list(extra_free)
    # load-bearing slot squares that are not pins of the class
    lb_slots = {"S02": ["BR(0,1)"], "S07": []}[tag]
    for sl in lb_slots:
        if sl not in pins and sl not in lb:
            lb.append(sl)
    bodies = []
    nv = 1
    rho = math.radians(rho_deg)
    for n in lb:
        x, y, t = P[n]
        t0, t1 = t - rho, t + rho
        if n not in slots:
            if tilt_floor_deg is not None:
                t0 = max(t0, math.radians(tilt_floor_deg))
            if tilt_ceil_deg is not None:
                t1 = min(t1, math.radians(tilt_ceil_deg))
        if t1 < t0:
            raise ValueError("empty tilt box for %s" % n)
        rr = r if (n not in slots or slot_radius is None) else min(r, slot_radius)
        bodies.append(Body(n, "free", x0=x - rr, x1=x + rr, y0=y - rr, y1=y + rr, t0=t0, t1=t1,
                           vi=nv, anchor=(x, y, t)))
        nv += 2
    for p in pins:
        ax, ay = slot_affine(p)
        bodies.append(Body(p, "pin", ax=ax, ay=ay, hh=pin_slack, vi=nv,
                           anchor=(slot_xy(p, anchor_side)[0], slot_xy(p, anchor_side)[1], 0.0)))
        nv += 2
    for bd in bodies:                       # the tilt variables of the free bodies
        if bd.kind == "free":
            bd.ti = nv; nv += 1
    return bodies, nv, s_sh, P


# ------------------------------------------------------------------ census
def census(bodies, s_lo, s_hi, cells=None):
    """For every pair: 'far' (some selection holds on the whole cell), or the list of possible
    selections (gap enclosure reaches 0).  Returns (near: {(i,j): [sels]}, far: [(i,j)],
    impossible: [(i,j)] with no possible selection)."""
    poses = [b.pose_iv(s_lo, s_hi, cells) for b in bodies]
    near, far, imp = {}, [], []
    nb = len(bodies)
    for i in range(nb):
        for j in range(i + 1, nb):
            poss = []
            isfar = False
            for (o, k, e) in SELS:
                if bodies[i].kind == "pin" and bodies[j].kind == "pin" and o == 1:
                    continue        # two axis-aligned squares: the owner's axes coincide
                g = gap_sel_iv(poses[i], poses[j], o, k, e)
                if g.lo >= 0:
                    isfar = True
                    break
                if g.hi >= 0:
                    poss.append((o, k, e))
            if isfar:
                far.append((i, j))
            elif not poss:
                imp.append((i, j))
            else:
                near[(i, j)] = poss
    return near, far, imp


# ------------------------------------------------------------------ rows
KINK = math.pi / 2


def interior_kink(lo, hi):
    """The multiple of pi/2 strictly inside (lo, hi) (where w = |cos| + |sin| has its kink
    minimum), or None.  A kink at an endpoint leaves the function concave on the closed cell."""
    k = math.ceil(lo / KINK)
    if k * KINK <= lo + 1e-12:
        k += 1
    return k * KINK if k * KINK < hi - 1e-12 else None


def lower_bounds(f, lo, hi, scale=1.0):
    """Affine lower bounds [(m, c)] of f(t) = scale * (|cos t| + |sin t|) on [lo, hi]: the chord
    when f is concave on the cell (no interior kink), else the two V-lines through the kink
    k: f(t) >= scale * (cos h' +/- (sin h'/h') (t - k)), h' = max distance from k to an end
    (from |sin d| >= d sin h'/h' and cos d >= cos h' for |d| <= h'; second-order loss)."""
    k = interior_kink(lo, hi)
    if k is None:
        return [concave_chord_lower(f, lo, hi)]
    hp = max(hi - k, k - lo)
    base = math.cos(hp) * (1 - 1e-12) - 1e-12
    sl = math.sin(hp) / hp
    return [(scale * sl, scale * (base - sl * k)), (-scale * sl, scale * (base + sl * k))]


def concave_chord_lower(f, lo, hi):
    """(m, c): f(t) >= m t + c on [lo, hi] for f concave there (the chord), outward-rounded."""
    if hi - lo < 1e-12:
        v = f(lo) - 1e-12
        return 0.0, v
    flo, fhi = f(lo), f(hi)
    m = (fhi - flo) / (hi - lo)
    c = flo - m * lo - 1e-12 * (1 + abs(flo) + abs(fhi))
    return m, c


class Rows:
    """An LP: min s over the relaxed rows.  A_ub x <= b_ub, with metadata per row.
    Variables: s (0); (x, y) per free body / (u, v) per pin; then t (the tilt) per free body.
    The tilt variables carry the cell as bounds; the trigonometric terms are relaxed to affine
    functions of them (chords of the concave pieces of w = |cos| + |sin|; McCormick envelope of
    the bilinear term q*phi), so that the loss is second order in the cell width except for the
    McCormick term, whose loss is (range of q) x (cell width) / 4 and is cut by q-range splits."""

    def __init__(self, bodies, nv, s_lo, s_hi, cells=None, qranges=None):
        self.bodies, self.nv, self.s_lo, self.s_hi = bodies, nv, s_lo, s_hi
        self.cells = cells or {}
        self.qranges = qranges or {}
        self.A, self.b, self.meta = [], [], []
        self.losses = {}
        self.qeff = {}
        self.bounds = [(s_lo, s_hi)] + [None] * (nv - 1)
        for bd in bodies:
            if bd.kind == "free":
                self.bounds[bd.vi] = (bd.x0, bd.x1); self.bounds[bd.vi + 1] = (bd.y0, bd.y1)
                t = bd.tilt(self.cells)
                self.bounds[bd.ti] = (t.lo, t.hi)
            else:
                self.bounds[bd.vi] = (-bd.hh, bd.hh); self.bounds[bd.vi + 1] = (-bd.hh, bd.hh)
        assert all(bb is not None for bb in self.bounds)

    def add(self, coef, rhs, meta):
        self.A.append(np.asarray(coef, dtype=float)); self.b.append(float(rhs)); self.meta.append(meta)

    # -- the tilt of a body as an affine map (coef, const) of the variables
    def tilt_affine(self, bd):
        c = np.zeros(self.nv)
        if bd.kind == "pin":
            return c, 0.0
        c[bd.ti] = 1.0
        return c, 0.0

    def walls(self, exact_theta=None):
        for bd in self.bodies:
            cx, x0, cy, y0 = bd.centre_affine(self.nv)
            if bd.kind == "pin":
                hm, hc = 0.0, 0.5                          # h = 1/2 exactly
            elif exact_theta is not None:
                hm, hc = 0.0, half_width(exact_theta[bd.name])
            else:
                t = bd.tilt(self.cells)
                hbs = lower_bounds(half_width, t.lo, t.hi, scale=0.5)
            if bd.kind == "pin" or exact_theta is not None:
                hbs = [(hm, hc)]
            tc, _ = self.tilt_affine(bd)
            for (hm, hc) in hbs:
                for (c, c0, nm) in ((cx, x0, "x"), (cy, y0, "y")):
                    # c.v + c0 >= hm*t + hc  ->  -c.v + hm*t <= c0 - hc
                    self.add(-c + hm * tc, c0 - hc, ("wall", bd.name, nm + "-lo"))
                    # s - (c.v + c0) >= hm*t + hc  ->  c.v - s + hm*t <= -hc - c0
                    row = c.copy(); row[0] -= 1.0
                    self.add(row + hm * tc, -hc - c0, ("wall", bd.name, nm + "-hi"))

    def selection(self, i, j, sel, exact_theta=None):
        """The relaxed (over the cell) or exact (at exact_theta) rows of selection sel for pair
        (i, j).  Records the McCormick loss of the pair in self.losses."""
        (o, k, eps) = sel
        bw, bo = (self.bodies[i], self.bodies[j]) if o == 0 else (self.bodies[j], self.bodies[i])
        cxw, x0w, cyw, y0w = bw.centre_affine(self.nv)
        cxo, x0o, cyo, y0o = bo.centre_affine(self.nv)
        dcx, dx0 = cxo - cxw, x0o - x0w
        dcy, dy0 = cyo - cyw, y0o - y0w
        tag = ("sel", bw.name, bo.name, k, eps)
        if exact_theta is not None:
            tw = 0.0 if bw.kind == "pin" else exact_theta[bw.name]
            to = 0.0 if bo.kind == "pin" else exact_theta[bo.name]
            Ax, Ay = axis(tw, k)
            coef = -eps * (dcx * Ax + dcy * Ay)
            rhs = eps * (dx0 * Ax + dy0 * Ay) - 0.5 - 0.5 * wfun(tw - to)
            self.add(coef, rhs, tag)
            return 0.0
        tw = bw.tilt(self.cells); to = bo.tilt(self.cells)
        tmid = 0.5 * (tw.lo + tw.hi); hw = 0.5 * (tw.hi - tw.lo)
        assert hw <= math.radians(60.0), "cell too wide for the relaxation"
        Ax, Ay = axis(tmid, k)
        Px, Py = -Ay, Ax                       # a* perp
        xw, yw = bw.xrange(self.s_lo, self.s_hi)
        xo, yo = bo.xrange(self.s_lo, self.s_hi)
        dxr, dyr = xo - xw, yo - yw
        pr = IV(eps) * (dxr * IV(Ax) + dyr * IV(Ay))
        qr = IV(eps) * (dxr * IV(Px) + dyr * IV(Py))
        pc = eps * (dcx * Ax + dcy * Ay); p0 = eps * (dx0 * Ax + dy0 * Ay)
        qc = eps * (dcx * Px + dcy * Py); q0 = eps * (dx0 * Px + dy0 * Py)
        qlo, qhi = qr.lo, qr.hi
        if (i, j) in self.qranges:                     # a q-range split of this pair (LP rows)
            a_, b_ = self.qranges[(i, j)]
            qlo, qhi = max(qlo, a_), min(qhi, b_)
            if qlo > qhi:
                qlo, qhi = qhi, qlo
            # q >= a_ : -(qc.v + q0) <= -a_ ;  q <= b_ : qc.v + q0 <= b_
            self.add(-qc, q0 - a_, ("qrange", bw.name, bo.name, k, eps, "lo", a_))
            self.add(qc, b_ - q0, ("qrange", bw.name, bo.name, k, eps, "hi", b_))
        # the support term: w(Delta), Delta = t_w - t_o, relaxed to an affine LOWER bound
        dr = tw - to
        tcw, _ = self.tilt_affine(bw); tco, _ = self.tilt_affine(bo)
        dcoef = tcw - tco
        if bw.kind == "pin" and bo.kind == "pin":
            wbs = [(0.0, 1.0)]
        else:
            wbs = lower_bounds(wfun, dr.lo, dr.hi)
        corr = max(0.0, -pr.lo) * (1 - math.cos(hw)) * (1 + 1e-12) + 1e-12
        # (A) tilt-free: q sin(phi) <= |q| sin(hw), |q| <= chord over [qlo, qhi]
        if qlo >= 0:
            mq, cq = 1.0, 0.0
        elif qhi <= 0:
            mq, cq = -1.0, 0.0
        else:
            mq = (qhi + qlo) / (qhi - qlo); cq = -2.0 * qlo * qhi / (qhi - qlo)
        sh = math.sin(hw) * (1 + 1e-12)
        Us = [(sh * mq * qc, sh * (mq * q0 + cq), "A")]
        lossA = cq * sh
        # (B) McCormick on q*phi, phi = t_w - tmid in [-hw, hw], sin(phi) = phi + O(hw^3/6)
        if bw.kind == "free" and hw > 0:
            e3 = max(abs(qlo), abs(qhi)) * hw ** 3 / 6 * (1 + 1e-12) + 1e-12
            phic = tcw.copy(); phi0 = -tmid
            # q*phi <= qhi*phi + q*(-hw) - qhi*(-hw) = qhi*phi - hw*q + qhi*hw
            Us.append((qhi * phic - hw * qc, qhi * phi0 - hw * q0 + qhi * hw + e3, "B1"))
            # q*phi <= qlo*phi + q*hw - qlo*hw
            Us.append((qlo * phic + hw * qc, qlo * phi0 + hw * q0 - qlo * hw + e3, "B2"))
            lossB = (qhi - qlo) * 2 * hw / 4
        else:
            lossB = 0.0
        # rows: p - (wm*Delta + wc)/2 + corr >= 1/2 + U  for every w-bound and every U
        for (wm, wc) in wbs:
            base_coef = -(pc - 0.5 * wm * dcoef)
            base_rhs = p0 + corr - 0.5 * wc - 0.5
            for (Uc, U0, nm) in Us:
                self.add(base_coef - Uc, base_rhs + U0, tag + (nm,))
        self.losses[(i, j)] = min(lossA, lossB) if bw.kind == "free" else 0.0
        self.qeff[(i, j)] = (qlo, qhi)
        return self.losses[(i, j)]

    def qrange_of(self, pr):
        return self.qeff[pr]

    def solve(self):
        c = np.zeros(self.nv); c[0] = 1.0
        A = np.array(self.A) if self.A else np.zeros((0, self.nv))
        b = np.array(self.b) if self.b else np.zeros(0)
        res = linprog(c, A_ub=A, b_ub=b, bounds=self.bounds, method="highs")
        if res.status == 2:
            return math.inf, None, None
        if not res.success:
            return -math.inf, None, None
        y = -res.ineqlin.marginals if len(self.A) else np.zeros(0)
        return float(res.fun), res.x, y

    def support(self, y, tol=1e-7):
        return [(self.meta[r], float(y[r])) for r in range(len(self.meta)) if y[r] > tol]

    def dual_bound(self, res_x, y):
        """The certified lower bound re-derived from the multipliers (float check of the Farkas
        certificate; the rational form is O4): min over the variable box of (c + A^T y).v - y.b."""
        if y is None or not len(self.A):
            return None
        A = np.array(self.A); b = np.array(self.b)
        c = np.zeros(self.nv); c[0] = 1.0
        red = c + A.T @ y
        lb = -float(y @ b)
        for v in range(self.nv):
            lo, hi = self.bounds[v]
            lb += red[v] * (lo if red[v] > 0 else hi)
        return lb


def build_lp(bodies, nv, s_lo, s_hi, fixed, cells=None, exact_theta=None, qranges=None):
    R = Rows(bodies, nv, s_lo, s_hi, cells=cells, qranges=qranges)
    R.walls(exact_theta)
    for (i, j), sel in fixed.items():
        R.selection(i, j, sel, exact_theta)
    return R


# ------------------------------------------------------------------ the shadow's own selections
def shadow_selections(bodies, P, tol=1e-6):
    """For every pair in contact at the minimum: the selection(s) with gap ~ 0 (a flush pair has two)."""
    out = {}
    nb = len(bodies)
    for i in range(nb):
        for j in range(i + 1, nb):
            pi, pj = P[bodies[i].name], P[bodies[j].name]
            gs = [(gap_sel(pi[:2], pi[2], pj[:2], pj[2], o, k, e), (o, k, e)) for (o, k, e) in SELS]
            best = max(g for g, _ in gs)
            if best < tol:
                out[(i, j)] = [sel for g, sel in gs if g > best - tol]
    return out


# ------------------------------------------------------------------ exact witness check
def config_from_x(bodies, x, theta):
    s = x[0]
    cfg = {}
    for bd in bodies:
        if bd.kind == "pin":
            cfg[bd.name] = (bd.ax[0] + bd.ax[1] * s + x[bd.vi], bd.ay[0] + bd.ay[1] * s + x[bd.vi + 1], 0.0)
        else:
            cfg[bd.name] = (x[bd.vi], x[bd.vi + 1], theta[bd.name])
    return s, cfg


def check_packing(s, cfg, tol=-1e-9):
    """(worst pair SAT gap, worst wall gap) -- a packing iff both >= tol."""
    names = list(cfg)
    wp = math.inf
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            pa, pb = cfg[names[a]], cfg[names[b]]
            wp = min(wp, sat_gap(pa[:2], pa[2], pb[:2], pb[2]))
    ww = math.inf
    for n, (x, y, t) in cfg.items():
        h = half_width(t)
        ww = min(ww, x - h, s - x - h, y - h, s - y - h)
    return wp, ww


# ------------------------------------------------------------------ the selection tree
class Tree:
    """Nodes = (tilt cell, partial selection, q-range splits).  A node is closed DEAD when its
    relaxed LP has min s > s0 (infeasible included); the verdict for N is DEAD iff every node is
    closed dead or IMPOSSIBLE (phase 1).  Phase 2 (optional, tighten_cap nodes) re-opens the
    closed leaves whose bound is below `target` and refines them so that the certified minimum
    over the final cover approaches the true chain minimum (the brief's 10% criterion)."""

    def __init__(self, bodies, nv, s_lo=S_LO, s_hi=S_HI_DEFAULT, contact_pairs=None,
                 min_cell_deg=0.05, node_cap=400000, time_cap=1800.0, target=None,
                 tighten_cap=0, qsplit_min=2e-4, exact_check_deg=1.0, log=None):
        self.bodies, self.nv, self.s_lo, self.s_hi = bodies, nv, s_lo, s_hi
        self.contact = set(contact_pairs or [])
        self.min_cell = math.radians(min_cell_deg)
        self.node_cap, self.time_cap = node_cap, time_cap
        self.target = S0 if target is None else max(S0, target)
        self.tighten_cap, self.qsplit_min = tighten_cap, qsplit_min
        self.exact_check = math.radians(exact_check_deg)
        self.log = log or (lambda *a: None)
        self.free = [b for b in bodies if b.kind == "free"]
        self.tilted = {b.name for b in self.free if abs(b.anchor[2]) > 1e-9}
        self._census_cache = {}
        self.reset()

    def reset(self):
        self.stats = dict(nodes=0, impossible=0, dead_lp=0, live_low=0, unresolved=0, bisect=0,
                          qsplit=0, branch=0, full_leaves=0, lp_calls=0, tighten_nodes=0,
                          tighten_refined=0)
        self.witnesses, self.unresolved = [], []
        self.closed = []                    # closed dead leaves: dict(value, state, alive)
        self.near_root = None
        self.ratio_samples = []
        self.t_start = time.time()
        self.capped = False
        self._census_cache = {}

    def root_cells(self):
        return {b.name: (b.t0, b.t1) for b in self.free}

    def _cells_deg(self, cells):
        return {n: [round(math.degrees(a), 4), round(math.degrees(b), 4)] for n, (a, b) in cells.items()}

    def _fixed_named(self, fx):
        return {"%s|%s" % (self.bodies[i].name, self.bodies[j].name): list(sel) for (i, j), sel in fx.items()}

    def _census(self, cells):
        key = tuple(sorted((n, a, b) for n, (a, b) in cells.items()))
        c = self._census_cache.get(key)
        if c is None:
            c = census(self.bodies, self.s_lo, self.s_hi, cells)
            if len(self._census_cache) < 200000:
                self._census_cache[key] = c
        return c

    def _width(self, cells):
        """weighted widest tilt cell: an axis-aligned box square (kink at 0, exact V-bounds) counts half."""
        best, name = 0.0, None
        for n, (a, b) in cells.items():
            w = (b - a) * (1.0 if n in self.tilted else 0.5)
            if w > best:
                best, name = w, n
        return best, name

    def run(self):
        self.reset()
        cells = self.root_cells()
        near, far, imp = self._census(cells)
        self.near_root = dict(near=near, far=far, impossible=imp)
        stack = [(cells, {}, {})]
        self._loop(stack, tightening=False)
        if not self.capped and self.tighten_cap > 0:
            loose = [c for c in self.closed if c["alive"] and c["value"] < self.target]
            loose.sort(key=lambda c: c["value"])
            for c in loose:
                c["alive"] = False
            stack = [c["state"] + (c["value"],) for c in reversed(loose)]
            self._loop(stack, tightening=True)
        return self.verdict()

    def _loop(self, stack, tightening):
        t_phase = time.time()
        while stack:
            if tightening:
                if self.stats["tighten_nodes"] >= self.tighten_cap or time.time() - t_phase > self.time_cap:
                    # leave the remaining states closed as they were (they are all dead)
                    for st in stack:
                        self.closed.append(dict(value=(st[3] if len(st) > 3 and st[3] is not None else S0), state=st[:3], alive=True, leftover=True))
                    return
                self.stats["tighten_nodes"] += 1
            elif self.stats["nodes"] >= self.node_cap or time.time() - self.t_start > self.time_cap:
                self.capped = True
                return
            st = stack.pop()
            cells, fixed, qsigns = st[0], st[1], st[2]
            self.stats["nodes"] += 1
            near, far, imp = self._census(cells)
            if imp:
                self.stats["impossible"] += 1
                continue
            fx = dict(fixed)
            if any(pr in near and sel not in near[pr] for pr, sel in fx.items()):
                self.stats["impossible"] += 1
                continue
            for pr in list(fx):
                if pr not in near:            # became FAR in this cell: no row needed
                    del fx[pr]
            for pr, poss in near.items():
                if pr not in fx and len(poss) == 1:
                    fx[pr] = poss[0]
            qs = {pr: rg for pr, rg in qsigns.items() if pr in fx}
            R = build_lp(self.bodies, self.nv, self.s_lo, self.s_hi, fx, cells, qranges=qs)
            v, x, y = R.solve()
            self.stats["lp_calls"] += 1
            unfixed = [pr for pr in near if pr not in fx]
            width, wname = self._width(cells)
            if v > S0 + 1e-12:
                if tightening and v < self.target:
                    kind = self._refine_kind(R, cells, width)
                    if kind is not None:
                        self.stats["tighten_refined"] += 1
                        self._push_refined(stack, kind, cells, fx, qs, wname, v)
                        continue
                self.stats["dead_lp"] += 1
                self.closed.append(dict(value=v, state=(cells, fx, qs), alive=True, nunfixed=len(unfixed),
                                        support=(None if y is None else R.support(y)),
                                        dual_bound=(None if y is None else R.dual_bound(x, y))))
                continue
            if unfixed:
                self.stats["branch"] += 1
                pr = min(unfixed, key=lambda q: (0 if q in self.contact else 1, len(near[q]), q))
                for sel in near[pr]:
                    f2 = dict(fx); f2[pr] = sel
                    stack.append((cells, f2, qs))
                continue
            # full selection with relaxed value <= s0
            self.stats["full_leaves"] += 1
            vx, xx, yx, Rx, thx = math.inf, None, None, None, None
            if width <= self.exact_check or v < S0 - 0.005 or width <= self.min_cell:
                for lam in (0.5, 0.0, 1.0):
                    th = {n: a + lam * (b - a) for n, (a, b) in cells.items()}
                    R2 = build_lp(self.bodies, self.nv, self.s_lo, self.s_hi, fx, cells, exact_theta=th)
                    v2, x2, y2 = R2.solve()
                    self.stats["lp_calls"] += 1
                    if v2 < vx:
                        vx, xx, yx, Rx, thx = v2, x2, y2, R2, th
            rec = dict(value_relaxed=v, value_exact_best=(None if vx == math.inf else vx),
                       width_deg=math.degrees(width), nfixed=len(fx), cells=self._cells_deg(cells),
                       fixed=self._fixed_named(fx),
                       qranges={"%s|%s" % (self.bodies[i].name, self.bodies[j].name): list(rg) for (i, j), rg in qs.items()},
                       support=(None if yx is None else Rx.support(yx)))
            if vx <= S0 + 1e-9 and xx is not None:
                s_w, cfg = config_from_x(self.bodies, xx, thx)
                wp, ww = check_packing(s_w, cfg)
                rec.update(witness_side=s_w, witness_worst_pair=wp, witness_worst_wall=ww,
                           witness_cfg={n: [p[0], p[1], math.degrees(p[2])] for n, p in cfg.items()},
                           witness_valid=bool(wp >= -1e-7 and ww >= -1e-7))
                self.witnesses.append(rec)
                self.stats["live_low"] += 1
                if rec["witness_valid"]:
                    # a checked packing of L u P at side <= s0 settles the verdict: N is not dead
                    return
                continue
            if vx < math.inf:
                self.ratio_samples.append((vx - v) / max(vx - S0, 1e-12))
            kind = self._refine_kind(R, cells, width)
            if kind is None:
                self.stats["unresolved"] += 1
                self.unresolved.append(rec)
                continue
            self._push_refined(stack, kind, cells, fx, qs, wname)

    def _refine_kind(self, R, cells, width):
        """('q', pair, range) to halve the q-range of the row with the dominant McCormick loss,
        ('t',) to bisect the widest tilt cell, None if nothing is left."""
        total = sum(R.losses.values()) if R.losses else 0.0
        if R.losses:
            pr, loss = max(R.losses.items(), key=lambda t: t[1])
            if loss > self.qsplit_min and (loss > 0.6 * total or width <= self.min_cell) and width <= math.radians(1.0):
                return ("q", pr, R.qrange_of(pr))
        if width > self.min_cell:
            return ("t",)
        return None

    def _push_refined(self, stack, kind, cells, fx, qs, wname, pv=None):
        if kind[0] == "q":
            self.stats["qsplit"] += 1
            lo, hi = kind[2]
            m = 0.5 * (lo + hi)
            for rg in ((lo, m), (m, hi)):
                q2 = dict(qs); q2[kind[1]] = rg
                stack.append((cells, fx, q2, pv))
        else:
            self.stats["bisect"] += 1
            a, b = cells[wname]
            m = 0.5 * (a + b)
            for lohi in ((a, m), (m, b)):
                c2 = dict(cells); c2[wname] = lohi
                stack.append((c2, fx, qs, pv))

    def certified(self):
        alive = [c for c in self.closed if c["alive"]]
        if not alive:
            return None, None
        c = min(alive, key=lambda q: q["value"])
        return c["value"], dict(value=c["value"], cells=self._cells_deg(c["state"][0]),
                                fixed=self._fixed_named(c["state"][1]), support=c.get("support"),
                                dual_bound=c.get("dual_bound"), nunfixed=c.get("nunfixed"))

    def verdict(self):
        dead = (not self.capped) and self.stats["live_low"] == 0 and self.stats["unresolved"] == 0
        cm, cl = self.certified()
        return dict(dead=dead, capped=self.capped, stats=dict(self.stats),
                    seconds=round(time.time() - self.t_start, 1),
                    n_near=len(self.near_root["near"]), n_far=len(self.near_root["far"]),
                    near_pairs={"%s|%s" % (self.bodies[i].name, self.bodies[j].name): len(p)
                                for (i, j), p in self.near_root["near"].items()},
                    leaves_after_interval=int(np.prod([len(p) for p in self.near_root["near"].values()])) if self.near_root["near"] else 1,
                    n_closed=len([c for c in self.closed if c["alive"]]),
                    certified_min=(None if cm == math.inf else cm), certified_min_leaf=cl,
                    relax_ratio_max=(max(self.ratio_samples) if self.ratio_samples else None),
                    relax_ratio_median=(float(np.median(self.ratio_samples)) if self.ratio_samples else None))


# ------------------------------------------------------------------ sampling + local minimiser
def sample_check(bodies, nv, n_samples=10000, seed=1, s_lo=S_LO, s_hi=S0, n_side=30):
    """Uniform poses in N (free boxes, pin offsets); each sample is checked at n_side sides in
    [s_lo, s_hi]: is it a packing of L u P (all pairs SAT-disjoint, all contained)?  Any hit is a
    counterexample to 'N dead'.  Returns counts and the nearest miss."""
    rng = np.random.default_rng(seed)
    free = [b for b in bodies if b.kind == "free"]
    pins = [b for b in bodies if b.kind == "pin"]
    sides = np.linspace(s_lo, s_hi, n_side)
    hits = []
    best_gap = -math.inf
    n_pairs_ok = 0
    for it in range(n_samples):
        poses = {}
        for b in free:
            poses[b.name] = (rng.uniform(b.x0, b.x1), rng.uniform(b.y0, b.y1), rng.uniform(b.t0, b.t1))
        offs = {b.name: (rng.uniform(-b.hh, b.hh), rng.uniform(-b.hh, b.hh)) for b in pins}
        # pairs among free bodies are s-independent
        gfree = math.inf
        fn = [b.name for b in free]
        for a in range(len(fn)):
            for c in range(a + 1, len(fn)):
                pa, pb = poses[fn[a]], poses[fn[c]]
                gfree = min(gfree, sat_gap(pa[:2], pa[2], pb[:2], pb[2]))
        if gfree < -1e-9:
            best_gap = max(best_gap, gfree)
            continue
        n_pairs_ok += 1
        found = None
        for s in sides[::-1]:          # from s_hi downward: the first infeasible side ends the scan
            cfg = dict(poses)
            for b in pins:
                cfg[b.name] = (b.ax[0] + b.ax[1] * s + offs[b.name][0], b.ay[0] + b.ay[1] * s + offs[b.name][1], 0.0)
            wp, ww = check_packing(s, cfg)
            if min(wp, ww) >= -1e-9:
                found = (s, wp, ww)
            else:
                break
        if found is not None:
            hits.append(dict(side=found[0], poses={n: [p[0], p[1], math.degrees(p[2])] for n, p in poses.items()},
                             offsets=offs))
            if len(hits) > 50:
                break
    return dict(n_samples=n_samples, free_pairs_disjoint=n_pairs_ok, hits=len(hits),
                examples=hits[:3], worst_free_overlap_of_rejects=(None if best_gap == -math.inf else best_gap))


def local_min(bodies, nv, starts=100, seed=2, s_lo=3.5, s_hi=4.6, shadow_start=None):
    """Box-constrained SLSQP on the exact SAT gaps from random starts inside N (+ the anchor):
    the measured minimum side over N (an upper bound on the true minimum)."""
    rng = np.random.default_rng(seed)
    free = [b for b in bodies if b.kind == "free"]
    pins = [b for b in bodies if b.kind == "pin"]
    nf, npn = len(free), len(pins)

    def unpack(z):
        s = z[0]
        Q = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(nf)]
        off = z[1 + 3 * nf:]
        Pn = [(p.ax[0] + p.ax[1] * s + off[2 * i], p.ay[0] + p.ay[1] * s + off[2 * i + 1], 0.0)
              for i, p in enumerate(pins)]
        return s, Q, Pn

    def cons(z):
        s, Q, Pn = unpack(z)
        out = []
        for i in range(nf):
            cx, cy, th = Q[i]
            w = half_width(th)
            out += [cx - w, s - w - cx, cy - w, s - w - cy]
            for j in range(i + 1, nf):
                out.append(sat_gap((cx, cy), th, Q[j][:2], Q[j][2]))
            for q in Pn:
                out.append(sat_gap((cx, cy), th, q[:2], 0.0))
        for i in range(npn):
            out += [Pn[i][0] - 0.5, s - 0.5 - Pn[i][0], Pn[i][1] - 0.5, s - 0.5 - Pn[i][1]]
            for j in range(i + 1, npn):
                out.append(sat_gap(Pn[i][:2], 0.0, Pn[j][:2], 0.0))
        return np.array(out)

    bnds = [(s_lo, s_hi)]
    for b in free:
        bnds += [(b.x0, b.x1), (b.y0, b.y1), (b.t0, b.t1)]
    for p in pins:
        bnds += [(-p.hh, p.hh), (-p.hh, p.hh)]
    Z = []
    z0 = [S0]
    for b in free:
        z0 += [min(max(b.anchor[0], b.x0), b.x1), min(max(b.anchor[1], b.y0), b.y1), min(max(b.anchor[2], b.t0), b.t1)]
    z0 += [0.0] * (2 * npn)
    Z.append(np.array(z0))
    for _ in range(starts):
        z = [rng.uniform(3.82, 4.05)]
        for b in free:
            z += [rng.uniform(b.x0, b.x1), rng.uniform(b.y0, b.y1), rng.uniform(b.t0, b.t1)]
        for p in pins:
            z += [rng.uniform(-p.hh, p.hh), rng.uniform(-p.hh, p.hh)]
        Z.append(np.array(z))
    best = None
    for z in Z:
        try:
            r = minimize(lambda v: v[0], z, method="SLSQP", constraints=[{"type": "ineq", "fun": cons}],
                         bounds=bnds, options=dict(maxiter=300, ftol=1e-12))
        except Exception:
            continue
        if cons(r.x).min() >= -1e-9 and (best is None or r.x[0] < best[0]):
            best = (float(r.x[0]), [float(v) for v in r.x])
    if best is None:
        return None
    s, Q, Pn = unpack(np.array(best[1]))
    return dict(side=best[0], free={b.name: [Q[i][0], Q[i][1], math.degrees(Q[i][2])] for i, b in enumerate(free)},
                pins={p.name: [Pn[i][0], Pn[i][1]] for i, p in enumerate(pins)})


# ------------------------------------------------------------------ Trump
def trump_poses():
    p = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")
    return json.load(open(p))["X"]


def trump_in_N(bodies, pin_slack=PIN_SLACK):
    """Does some D4 image of Trump's packing satisfy the hypothesis of N (every pin core at
    Trump's side and every free box, by distinct squares)?"""
    X = trump_poses()
    hits = []
    for op, f in L11.d4_ops(SHAT).items():
        Pn = [f(x, y, t) for (x, y, t) in X]
        cand = {}
        ok = True
        for b in bodies:
            cs = []
            for j, (x, y, t) in enumerate(Pn):
                td = math.degrees(t) % 90.0
                if b.kind == "pin":
                    px, py = b.ax[0] + b.ax[1] * SHAT, b.ay[0] + b.ay[1] * SHAT
                    if abs(x - px) <= b.hh and abs(y - py) <= b.hh and min(td, 90 - td) <= 1e-6:
                        cs.append(j)
                else:
                    if b.x0 <= x <= b.x1 and b.y0 <= y <= b.y1 and any(b.t0 <= math.radians(td + o) <= b.t1 for o in (-90, 0, 90)):
                        cs.append(j)
            if not cs:
                ok = False; break
            cand[b.name] = cs
        if not ok:
            continue
        names = [b.name for b in bodies]
        for perm in itertools.permutations(range(len(Pn)), len(names)):
            if all(perm[i] in cand[names[i]] for i in range(len(names))):
                hits.append(op); break
    return dict(inside=bool(hits), ops=hits)


# ------------------------------------------------------------------ stability radii (PI route)
def pair_box(bi, bj, delta, rho, s_lo, s_hi):
    """The pair's 6-D pose box for per-square radius delta / tilt half-width rho around the anchors."""
    def one(b):
        x, y, t = b.anchor
        if b.kind == "pin":
            return [IV(b.ax[0] + b.ax[1] * s_lo - b.hh, b.ax[0] + b.ax[1] * s_hi + b.hh),
                    IV(b.ay[0] + b.ay[1] * s_lo - b.hh, b.ay[0] + b.ay[1] * s_hi + b.hh), IV(0.0)]
        return [IV(x - delta, x + delta), IV(y - delta, y + delta), IV(t - rho, t + rho)]
    return one(bi) + one(bj)


def forced_test(box, sels_star, node_cap=60000):
    """Interval bisection: TRUE iff over `box` (6 intervals) every disjoint configuration
    satisfies one of sels_star (the minimum's selection(s)).  A sub-box is cleared when some
    sel in sels_star holds throughout (g.lo >= 0), or when every OTHER selection is impossible
    (g.hi < 0) -- then a disjoint configuration, which needs SOME separating axis, must use
    one of sels_star."""
    others = [s for s in SELS if s not in sels_star]
    stack = [box]
    n = 0
    while stack:
        if n >= node_cap:
            return False, n
        bx = stack.pop(); n += 1
        Bi, Bj = tuple(bx[:3]), tuple(bx[3:])
        if any(gap_sel_iv(Bi, Bj, *s).lo >= 0 for s in sels_star):
            continue
        if all(gap_sel_iv(Bi, Bj, *s).hi < 0 for s in others):
            continue
        # bisect the widest dimension (tilts scaled by 1/sqrt2 ~ the arm of a vertex)
        widths = [(bx[d].hi - bx[d].lo) * (0.7071 if d in (2, 5) else 1.0) for d in range(6)]
        d = max(range(6), key=lambda q: widths[q])
        if widths[d] < 1e-6:
            return False, n
        m = 0.5 * (bx[d].lo + bx[d].hi)
        for lohi in ((bx[d].lo, m), (m, bx[d].hi)):
            b2 = list(bx); b2[d] = IV(*lohi)
            stack.append(b2)
    return True, n


def far_test(box):
    Bi, Bj = tuple(box[:3]), tuple(box[3:])
    return any(gap_sel_iv(Bi, Bj, *s).lo >= 0 for s in SELS)


def radius_search(test, dmax=0.4, tol=2e-3):
    """Largest delta in [0, dmax] passing `test` (monotone assumed), by bisection."""
    if not test(tol):
        return 0.0
    lo, hi = tol, dmax
    if test(dmax):
        return dmax
    while hi - lo > tol:
        m = 0.5 * (lo + hi)
        if test(m):
            lo = m
        else:
            hi = m
    return lo


def contact_geometry(bi, bj, P, sel):
    """For a contact pair with selection sel = (owner, k, eps): the riding vertex of the other
    square, its tangential coordinate tau along the owner's edge (from the edge midpoint), the
    slack 1/2 - |tau| to the nearer end, the relative tilt and its margin to a multiple of 90 deg."""
    (o, k, eps) = sel
    bw, bo = (bi, bj) if o == 0 else (bj, bi)
    pw, po = P[bw.name], P[bo.name]
    a = axis(pw[2], k)
    n = (eps * a[0], eps * a[1])                 # outward normal of the owner's contact edge
    t = (-n[1], n[0])                            # tangent
    # the owner's edge: centre + n/2, spanning tau in [-1/2, 1/2] along t
    cs = corners(po[:2], po[2])
    # the riding vertex = the other's extreme vertex in direction -n
    depth = [-(c[0] * n[0] + c[1] * n[1]) for c in cs]
    order = sorted(range(4), key=lambda q: -depth[q])
    v = cs[order[0]]
    tie = abs(depth[order[0]] - depth[order[1]]) < 1e-6
    tau = (v[0] - pw[0]) * t[0] + (v[1] - pw[1]) * t[1]
    rel = (pw[2] - po[2]) % (math.pi / 2)
    margin = min(rel, math.pi / 2 - rel)
    out = dict(owner=bw.name, other=bo.name, k=k, eps=eps, tau=tau, slack=0.5 - abs(tau),
               dtheta_margin_deg=math.degrees(margin), flush=tie)
    if tie:
        v2 = cs[order[1]]
        tau2 = (v2[0] - pw[0]) * t[0] + (v2[1] - pw[1]) * t[1]
        lo_, hi_ = sorted((tau, tau2))
        out.update(tau_lo=lo_, tau_hi=hi_, overlap=min(hi_, 0.5) - max(lo_, -0.5),
                   slack=min(0.5 - lo_, hi_ + 0.5))     # slide until the overlap closes
    return out
