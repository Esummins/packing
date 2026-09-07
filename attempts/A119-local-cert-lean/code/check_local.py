"""A119 T1 -- the INDEPENDENT checker of a local certificate.

    python check_local.py certs/<id>.cert.json[.gz] [more...]

This program does not import a116lib, a119lib, numpy, scipy or any tree code.  It reads a
certificate file and decides, in exact rational arithmetic (`exactiv.Fx`: dyadic intervals with
outward rounding on Python ints -- no float is ever compared, added or multiplied in a decision
path), whether the certificate PROVES

    Dead_{L u P}(N, s0):  no interior-disjoint configuration of the |L| + |P| bodies of N, with
    every body in its box / slack core and the side s in [s_lo, s_hi], has s <= s0.

What is checked, node by node, walking the recorded proof tree from the root cell:

  * COVER of the tilt box: a `bisect` node splits one body's tilt interval at a recorded point
    inside it; the two children carry [lo, mid] and [mid, hi] -- their union is the parent.
  * COVER of the selections: a `branch` node on a pair lists the selections its children assume;
    every OTHER selection of that pair is certified IMPOSSIBLE on the node's cell by the interval
    enclosure sup [g_sigma] < 0, so Lemma SAT leaves no third case.  (Two axis-aligned pins have
    only four distinct axes: the owner-1 selections repeat the owner-0 ones with the opposite
    sign, and are discharged as duplicates.)
  * COVER of the q-range case splits: a `qsplit` node splits the range of the scalar q of one
    pair; the recorded outer ends are checked to contain q's true range over the box, and the
    split point is a genuine case distinction (q <= mid or q >= mid).
  * `imp` / `imp_sel` leaves: the cell admits no interior-disjoint configuration at all (some
    pair has all eight selections impossible), or the selection assumed by the branch is
    impossible on this sub-cell.
  * `dead` leaves: every selection the multipliers lean on is either supplied by a `branch`
    ancestor or FORCED on the leaf cell (all other selections impossible); the relaxed rows named
    by the multipliers are REBUILT here from Lemma RELAX -- this file's own implementation, not
    the generator's -- and the Farkas bound
        min s  >=  -y.b + sum_v min_{v in box} (c + A^T y)_v v
    is evaluated in exact interval arithmetic and required to exceed s0 = 969271/250000.
  * any `live` or `unresolved` leaf, or any node kind not in the list, makes the certificate
    INVALID.

Exit code 0 iff every certificate passes.
"""
from __future__ import annotations

import gzip, hashlib, json, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exactiv import Fx, ZERO, ONE, PI, cos_q, sin_q, cos_iv, sin_iv, w_iv, SCALE  # noqa: E402

S0 = Q(969271, 250000)
SELS8 = [(o, k, e) for o in (0, 1) for k in (0, 1) for e in (1, -1)]


# ---------------------------------------------------------------- affine forms
class Aff:
    """sum_v co[v] * x_v + k, coefficients and constant as Fx intervals."""
    __slots__ = ("co", "k")

    def __init__(self, co=None, k=ZERO):
        self.co = dict(co or {})
        self.k = k

    def __add__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c[v] + a if v in c else a
        return Aff(c, self.k + o.k)

    def __sub__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c[v] - a if v in c else -a
        return Aff(c, self.k - o.k)

    def __neg__(self):
        return Aff({v: -a for v, a in self.co.items()}, -self.k)

    def scale(self, f: Fx):
        return Aff({v: a * f for v, a in self.co.items()}, self.k * f)

    def range_over(self, box):
        """enclosure of the affine form over the variable box."""
        lo = self.k
        for v, a in self.co.items():
            b = box[v]
            lo = lo + a * b
        return lo


def const(x: Fx):
    return Aff({}, x)


def var(v):
    return Aff({v: ONE}, ZERO)


def fx(q):
    return Fx.of_frac(Q(q))


# ---------------------------------------------------------------- bodies / geometry
class Body:
    def __init__(self, d):
        self.name = d["name"]
        self.kind = d["kind"]
        self.vi = d["vi"]
        if self.kind == "free":
            self.x0, self.x1 = Q(d["x0"]), Q(d["x1"])
            self.y0, self.y1 = Q(d["y0"]), Q(d["y1"])
            self.t0, self.t1 = Q(d["t0"]), Q(d["t1"])
            self.ti = d["ti"]
        else:
            self.ax = (Q(d["ax"][0]), Q(d["ax"][1]))
            self.ay = (Q(d["ay"][0]), Q(d["ay"][1]))
            self.hh = Q(d["hh"])
            self.ti = None

    def centre(self):
        """(cx, cy) as affine forms in the LP variables (variable 0 is the side s)."""
        if self.kind == "pin":
            cx = Aff({0: fx(self.ax[1]), self.vi: ONE}, fx(self.ax[0]))
            cy = Aff({0: fx(self.ay[1]), self.vi + 1: ONE}, fx(self.ay[0]))
            return cx, cy
        return var(self.vi), var(self.vi + 1)

    def tilt_cell(self, cells):
        if self.kind == "pin":
            return Q(0), Q(0)
        return cells[self.name]

    def tilt_aff(self):
        if self.kind == "pin":
            return Aff()
        return var(self.ti)

    def xy_range(self, s_lo, s_hi):
        if self.kind == "pin":
            return ((self.ax[0] + self.ax[1] * s_lo - self.hh, self.ax[0] + self.ax[1] * s_hi + self.hh),
                    (self.ay[0] + self.ay[1] * s_lo - self.hh, self.ay[0] + self.ay[1] * s_hi + self.hh))
        return ((self.x0, self.x1), (self.y0, self.y1))


def axis_iv(lo: Q, hi: Q, k):
    c, s = cos_iv(lo, hi), sin_iv(lo, hi)
    return (c, s) if k == 0 else (-s, c)


def axis_pt(t: Q, k):
    c, s = cos_q(t), sin_q(t)
    return (c, s) if k == 0 else (-s, c)


def gap_enclosure(bw, bo, k, eps, cells, s_lo, s_hi):
    """enclosure of g = eps (c_o - c_w).a_k(theta_w) - 1/2 - w(theta_w - theta_o)/2 over the
    cell and the boxes (Lemma SAT's row); the same object a116lib.gap_sel_iv encloses."""
    twl, twh = bw.tilt_cell(cells)
    tol, toh = bo.tilt_cell(cells)
    ax, ay = axis_iv(twl, twh, k)
    (xwl, xwh), (ywl, ywh) = bw.xy_range(s_lo, s_hi)
    (xol, xoh), (yol, yoh) = bo.xy_range(s_lo, s_hi)
    dx = Fx.of_frac(xol) - Fx.of_frac(xwh)
    dxh = Fx.of_frac(xoh) - Fx.of_frac(xwl)
    dy = Fx.of_frac(yol) - Fx.of_frac(ywh)
    dyh = Fx.of_frac(yoh) - Fx.of_frac(ywl)
    DX = Fx(dx.lo, dxh.hi)
    DY = Fx(dy.lo, dyh.hi)
    proj = DX * ax + DY * ay
    w = w_iv(twl - toh, twh - tol)
    e = Fx.of_int(eps)
    return e * proj - Fx.of_frac(Q(1, 2)) - w * Fx.of_frac(Q(1, 2))


# ---------------------------------------------------------------- affine lower bounds of w
def kink_in(lo: Q, hi: Q):
    """the multiple of pi/2 strictly inside (lo, hi), as (j, [k_lo, k_hi]); None if there is
    none.  Raises if the enclosure of pi cannot decide (never happens at our granularity)."""
    out = None
    jlo = int((lo * 2 / Q(PI.lo, SCALE)).__floor__()) - 2
    jhi = int((hi * 2 / Q(PI.hi, SCALE)).__ceil__()) + 2
    for j in range(jlo, jhi + 1):
        klo = Q(PI.lo, SCALE) * j / 2
        khi = Q(PI.hi, SCALE) * j / 2
        if j < 0:
            klo, khi = khi, klo
        if khi <= lo or klo >= hi:
            continue
        if klo <= lo or khi >= hi:
            raise ValueError("pi enclosure cannot decide the kink at j=%d in [%s, %s]" % (j, lo, hi))
        if out is not None:
            raise ValueError("two interior kinks: the cell is wider than 90 deg")
        out = (j, klo, khi)
    return out


def w_lower_bounds(lo: Q, hi: Q, scale: Q):
    """affine lower bounds [(m, c)] of scale * w(t) = scale (|cos t| + |sin t|) on [lo, hi],
    m, c exact rationals, each verified:

      * no interior kink -> w is concave on the cell, so the chord through two rational LOWER
        bounds of w at the ends lies below w everywhere on [lo, hi];
      * an interior kink at k = j pi/2 -> the two V-lines
            w(t) >= cos h' +- (sin h' / h') (t - k),   h' = max(hi - k, k - lo),
        from cos d >= cos h' and |sin d| >= |d| sin h'/h' for |d| <= h' (w has period pi/2 and
        w(k + d) = |cos d| + |sin d|).  k is irrational, so the line is written about a rational
        kappa in [k_lo, k_hi] and lowered by |m| (k_hi - k_lo).
    """
    kk = kink_in(lo, hi)
    if kk is None:
        A = Q(w_iv(lo, lo).lo, SCALE) * scale
        B = Q(w_iv(hi, hi).lo, SCALE) * scale
        if hi == lo:
            return [(Q(0), A)]
        m = (B - A) / (hi - lo)
        c = A - m * lo
        return [(m, c)]
    j, klo, khi = kk
    hp = max(hi - klo, khi - lo)
    if hp <= 0:
        return [(Q(0), Q(w_iv(lo, hi).lo, SCALE) * scale)]
    cb = Q(cos_q(hp).lo, SCALE)                      # <= cos h'
    sr = Q(sin_q(hp).lo, SCALE) / hp                 # <= sin h' / h'   (sin h' > 0 for 0 < h' < pi)
    if sr < 0:
        sr = Q(0)
    kappa = (klo + khi) / 2
    dk = (khi - klo) / 2
    out = []
    for sg in (1, -1):
        m = scale * sg * sr
        c = scale * cb - m * kappa - abs(m) * dk
        out.append((m, c))
    return out


def check_w_lower(m: Q, c: Q, lo: Q, hi: Q, scale: Q):
    """independent re-verification that scale*w(t) >= m t + c at the two ends AND (for the
    V-lines) at the kink -- a cheap guard against an algebra slip above."""
    for t in (lo, hi, (lo + hi) / 2):
        if Q(w_iv(t, t).lo, SCALE) * scale < m * t + c:
            return False
    return True


# ---------------------------------------------------------------- the relaxed rows (Lemma RELAX)
class LeafRows:
    """rebuilds, from the leaf's (cell, selections, q-ranges), the relaxed rows named by the
    Farkas keys -- this file's own implementation of Lemma RELAX."""

    def __init__(self, meta, bodies, cells, sel, qr, box):
        self.meta, self.bodies, self.cells, self.sel, self.qr, self.box = meta, bodies, cells, sel, qr, box
        self.s_lo, self.s_hi = Q(meta["s_lo"]), Q(meta["s_hi"])
        self.by = {b.name: b for b in bodies}

    # -- walls
    def wall(self, name, xy, side, wb):
        b = self.by[name]
        cx, cy = b.centre()
        c = cx if xy == "x" else cy
        if b.kind == "pin":
            hbs = [(Q(0), Q(1, 2))]
        else:
            lo, hi = self.cells[name]
            hbs = w_lower_bounds(lo, hi, Q(1, 2))
            for (m, cc) in hbs:
                assert check_w_lower(m, cc, lo, hi, Q(1, 2)), "wall h-bound not verified"
        m, cc = hbs[wb]
        t = b.tilt_aff()
        hb = t.scale(fx(m)) + const(fx(cc))          # h(t) >= hb
        if side == "lo":                              # c >= hb  ->  -c + hb <= 0
            return (-c) + hb
        return c - var(0) + hb                        # s - c >= hb  ->  c - s + hb <= 0

    # -- one selection's relaxed rows, keyed exactly as the generator keys them
    def sel_rows(self, ow, ot, k, eps):
        bw, bo = self.by[ow], self.by[ot]
        cxw, cyw = bw.centre()
        cxo, cyo = bo.centre()
        dcx, dcy = cxo - cxw, cyo - cyw
        twl, twh = bw.tilt_cell(self.cells)
        tol, toh = bo.tilt_cell(self.cells)
        tmid = (twl + twh) / 2
        hw = (twh - twl) / 2
        Ax, Ay = axis_pt(tmid, k)
        Px, Py = -Ay, Ax
        E = Fx.of_int(eps)
        p = (dcx.scale(Ax) + dcy.scale(Ay)).scale(E)
        q = (dcx.scale(Px) + dcy.scale(Py)).scale(E)
        pr = p.range_over(self.box)
        qrng = q.range_over(self.box)
        qlo, qhi = Q(qrng.lo, SCALE), Q(qrng.hi, SCALE)
        qrec = self.qr.get("%s|%s" % (ow, ot))
        if qrec is None:
            qrec = self.qr.get("%s|%s" % (ot, ow))
        rows = {}
        if qrec is not None:
            a_, b_ = Q(qrec[0]), Q(qrec[1])
            rows[("q", ow, ot, k, eps, "lo")] = (-q) + const(fx(a_))
            rows[("q", ow, ot, k, eps, "hi")] = q - const(fx(b_))
            qlo, qhi = max(qlo, a_), min(qhi, b_)
            if qlo > qhi:
                qlo, qhi = qhi, qlo
        # the support term w(t_w - t_o)
        if bw.kind == "pin" and bo.kind == "pin":
            wbs = [(Q(0), Q(1))]
        else:
            dlo, dhi = twl - toh, twh - tol
            wbs = w_lower_bounds(dlo, dhi, Q(1))
            for (m, cc) in wbs:
                assert check_w_lower(m, cc, dlo, dhi, Q(1)), "support w-bound not verified"
        dcoef = bw.tilt_aff() - bo.tilt_aff()
        # corr >= max(0, -p_lo) (1 - cos hw)
        plo = Q(pr.lo, SCALE)
        one_m_cos = Q(1) - Q(cos_q(hw).lo, SCALE)
        corr = max(Q(0), -plo) * one_m_cos
        # (A) |q| by its chord over [qlo, qhi]; sin hw by a rational upper bound
        if qlo >= 0:
            mq, cq = Q(1), Q(0)
        elif qhi <= 0:
            mq, cq = Q(-1), Q(0)
        else:
            mq = (qhi + qlo) / (qhi - qlo)
            cq = -2 * qlo * qhi / (qhi - qlo)
        sh = Q(sin_q(hw).hi, SCALE)
        if sh < 0:
            sh = Q(0)
        Us = [(q.scale(fx(sh * mq)) + const(fx(sh * cq)), "A")]
        if bw.kind == "free" and hw > 0:
            e3 = max(abs(qlo), abs(qhi)) * hw ** 3 / 6
            phi = bw.tilt_aff() - const(fx(tmid))
            Us.append((phi.scale(fx(qhi)) - q.scale(fx(hw)) + const(fx(qhi * hw + e3)), "B1"))
            Us.append((phi.scale(fx(qlo)) + q.scale(fx(hw)) + const(fx(-qlo * hw + e3)), "B2"))
        for wb, (wm, wc) in enumerate(wbs):
            # true row: p_exact - 1/2 - w/2 >= 0 with p_exact <= p + corr + U and w >= wm*d + wc
            #   =>  (U - p) + (wm*d + wc)/2 + 1/2 - corr <= 0
            base = (dcoef.scale(fx(wm)) + const(fx(wc))).scale(fx(Q(1, 2))) \
                + const(fx(Q(1, 2) - corr)) - p
            for (U, nm) in Us:
                rows[("s", ow, ot, k, eps, wb, nm)] = base - U
        return rows


# ---------------------------------------------------------------- the walk
class Checker:
    def __init__(self, cert):
        self.c = cert
        self.meta = cert["meta"]
        self.bodies = [Body(d) for d in self.meta["bodies"]]
        self.by = {b.name: b for b in self.bodies}
        self.nv = self.meta["nv"]
        self.s_lo, self.s_hi = Q(self.meta["s_lo"]), Q(self.meta["s_hi"])
        self.box = {}
        self.box[0] = Fx(Fx.of_frac(self.s_lo).lo, Fx.of_frac(self.s_hi).hi)
        for b in self.bodies:
            if b.kind == "free":
                self.box[b.vi] = Fx(Fx.of_frac(b.x0).lo, Fx.of_frac(b.x1).hi)
                self.box[b.vi + 1] = Fx(Fx.of_frac(b.y0).lo, Fx.of_frac(b.y1).hi)
            else:
                self.box[b.vi] = Fx(Fx.of_frac(-b.hh).lo, Fx.of_frac(b.hh).hi)
                self.box[b.vi + 1] = self.box[b.vi]
        self.n = dict(dead=0, imp=0, imp_sel=0, bisect=0, qsplit=0, branch=0, rows=0, mult=0,
                      forced=0, excluded=0, infeas=0)
        self.errors = []
        self.min_bound = None
        self.depth = 0
        self.capture_max = 0          # gen_local_lean.py sets this to keep leaf contexts
        self.capture = []

    # -- root cell from the bodies' tilt boxes
    def root_cells(self):
        return {b.name: (b.t0, b.t1) for b in self.bodies if b.kind == "free"}

    def cellbox(self, cells):
        bx = dict(self.box)
        for b in self.bodies:
            if b.kind == "free":
                lo, hi = cells[b.name]
                bx[b.ti] = Fx(Fx.of_frac(lo).lo, Fx.of_frac(hi).hi)
        return bx

    def pair_of(self, nm1, nm2):
        return self.by[nm1], self.by[nm2]

    def excluded_ok(self, cells, nm1, nm2, keep):
        """every selection of the pair NOT in `keep` is impossible on this cell."""
        b1, b2 = self.pair_of(nm1, nm2)
        for (o, k, e) in SELS8:
            if (o, k, e) in keep:
                continue
            if b1.kind == "pin" and b2.kind == "pin" and o == 1:
                continue                       # duplicate axis: (1,k,e) is (0,k,-e)
            bw, bo = (b1, b2) if o == 0 else (b2, b1)
            g = gap_enclosure(bw, bo, k, e, cells, self.s_lo, self.s_hi)
            self.n["excluded"] += 1
            if g.hi >= 0:
                return False, (o, k, e), g
        return True, None, None

    def walk(self, node, cells, fixed, qacc, qrec):
        k = node.get("k")
        self.depth += 1
        if k == "bisect":
            self.n["bisect"] += 1
            nm = node["body"]
            lo, hi = cells[nm]
            rlo, rmid, rhi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            if (rlo, rhi) != (lo, hi) or not (lo <= rmid <= hi):
                return self.fail("bisect cell mismatch at %s" % nm)
            # q is measured on the owner's midpoint axis: a split made before this bisection no
            # longer covers, so it must be dropped (A119 finding F1)
            def owner_of(kp):
                a, b = kp.split("|")
                return a if fixed.get(kp, (0,))[0] == 0 else b
            q2 = {kp: v for kp, v in qrec.items() if owner_of(kp) != nm}
            qa2 = {kp: v for kp, v in qacc.items() if owner_of(kp) != nm}
            for (a, b) in ((rlo, rmid), (rmid, rhi)):
                c2 = dict(cells); c2[nm] = (a, b)
                if not self.walk(node["ch"][0 if a == rlo else 1], c2, fixed, qa2, q2):
                    return False
            return True
        if k == "qsplit":
            self.n["qsplit"] += 1
            nm1, nm2 = node["pair"]
            kp = "%s|%s" % (nm1, nm2)
            rlo, rmid, rhi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            if not (rlo <= rmid <= rhi):
                return self.fail("qsplit point outside its range")
            sel = fixed.get(kp)
            if sel is None:
                rec = node.get("sel")
                if rec is None or not node.get("forced"):
                    return self.fail("qsplit on a pair with no justified selection")
                sel = tuple(rec)
                ok, bad, g = self.excluded_ok(cells, nm1, nm2, {sel})
                self.n["forced"] += 1
                if not ok:
                    return self.fail("qsplit selection %s of %s is not forced (rival %s)" % (sel, kp, bad))
            elif node.get("sel") is not None and tuple(node["sel"]) != sel:
                return self.fail("qsplit selection disagrees with the branch")
            lo_t, hi_t = self.q_true_range(cells, nm1, nm2, sel)
            A_, B_ = qacc.get(kp, (None, None))
            lo_ok = max(lo_t, A_) if A_ is not None else lo_t
            hi_ok = min(hi_t, B_) if B_ is not None else hi_t
            if rlo > lo_ok or rhi < hi_ok:
                return self.fail("qsplit outer range does not contain q on the cell")
            for idx, (a, b) in enumerate(((rlo, rmid), (rmid, rhi))):
                q2 = dict(qrec); q2[kp] = (a, b)
                qa2 = dict(qacc)
                qa2[kp] = (max(A_, a) if A_ is not None else a, min(B_, b) if B_ is not None else b)
                if not self.walk(node["ch"][idx], cells, fixed, qa2, q2):
                    return False
            return True
        if k == "branch":
            self.n["branch"] += 1
            nm1, nm2 = node["pair"]
            keep = {tuple(s) for s in node["sels"]}
            ok, bad, g = self.excluded_ok(cells, nm1, nm2, keep)
            if not ok:
                return self.fail("branch on %s|%s omits a possible selection %s (sup g = %s)"
                                 % (nm1, nm2, bad, g))
            for idx, s in enumerate(node["sels"]):
                f2 = dict(fixed); f2["%s|%s" % (nm1, nm2)] = tuple(s)
                if not self.walk(node["ch"][idx], cells, f2, qacc, qrec):
                    return False
            return True
        if k == "imp":
            self.n["imp"] += 1
            nm1, nm2 = node["pair"]
            ok, bad, g = self.excluded_ok(cells, nm1, nm2, set())
            if not ok:
                return self.fail("imp node: selection %s of %s|%s is possible (sup g = %s)"
                                 % (bad, nm1, nm2, g))
            return True
        if k == "imp_sel":
            self.n["imp_sel"] += 1
            nm1, nm2 = node["pair"]
            s = tuple(node["sel"])
            ok, bad, g = self.excluded_ok(cells, nm1, nm2, set(SELS8) - {s})
            if not ok:
                return self.fail("imp_sel: %s of %s|%s is not impossible" % (s, nm1, nm2))
            return True
        if k == "dead":
            return self.dead(node, cells, fixed, qrec)
        return self.fail("unclosed leaf of kind %r" % k)

    def q_true_range(self, cells, nm1, nm2, sel):
        o, k, eps = sel
        b1, b2 = self.pair_of(nm1, nm2)
        bw, bo = (b1, b2) if o == 0 else (b2, b1)
        cxw, cyw = bw.centre(); cxo, cyo = bo.centre()
        twl, twh = bw.tilt_cell(cells)
        tmid = (twl + twh) / 2
        Ax, Ay = axis_pt(tmid, k)
        q = ((cxo - cxw).scale(-Ay) + (cyo - cyw).scale(Ax)).scale(Fx.of_int(eps))
        r = q.range_over(self.cellbox(cells))
        return Q(r.lo, SCALE), Q(r.hi, SCALE)

    def dead(self, node, cells, fixed, qrec):
        self.n["dead"] += 1
        sel = {kp: tuple(v) for kp, v in node.get("sel", {}).items()}
        forced = set(node.get("forced", []))
        # every selection the multipliers use is either from a branch ancestor or FORCED here
        for kp, s in sel.items():
            if kp in fixed:
                if fixed[kp] != s:
                    return self.fail("dead leaf uses a selection the branch did not fix")
                continue
            if kp not in forced:
                return self.fail("dead leaf uses an unjustified selection %s %s" % (kp, s))
            nm1, nm2 = kp.split("|")
            ok, bad, g = self.excluded_ok(cells, nm1, nm2, {s})
            self.n["forced"] += 1
            if not ok:
                return self.fail("selection %s of %s is not forced (rival %s has sup g = %s)"
                                 % (s, kp, bad, g))
        # rebuild the rows named by the multipliers
        box = self.cellbox(cells)
        LR = LeafRows(self.meta, self.bodies, cells, sel, qrec, box)
        want = {}
        for ks, val in node["y"].items():
            parts = ks.split("|")
            v = Q(val)
            if v < 0:
                return self.fail("negative Farkas multiplier")
            if parts[0] == "w":
                key = ("w", parts[1], parts[2], parts[3], int(parts[4]))
            elif parts[0] == "s":
                key = ("s", parts[1], parts[2], int(parts[3]), int(parts[4]), int(parts[5]), parts[6])
            elif parts[0] == "q":
                key = ("q", parts[1], parts[2], int(parts[3]), int(parts[4]), parts[5])
            else:
                return self.fail("unknown row key %r" % ks)
            want[key] = v
        rows = {}
        for key in want:
            if key[0] == "w":
                rows[key] = LR.wall(key[1], key[2], key[3], key[4])
            else:
                ow, ot, k, eps = key[1], key[2], key[3], key[4]
                kp = "%s|%s" % (ow, ot)
                kp2 = "%s|%s" % (ot, ow)
                if kp not in sel and kp2 not in sel:
                    return self.fail("row %s has no recorded selection" % (key,))
                got = LR.sel_rows(ow, ot, k, eps)
                for kk, vv in got.items():
                    rows[kk] = vv
        for key in want:
            if key not in rows:
                return self.fail("row %s could not be rebuilt" % (key,))
        # the Farkas bound: min s >= -y.b + sum_v min_box (c + A^T y)_v v, rows written  f <= 0
        # with f = A.x - b, so the accumulated form is  c.x + sum y_r f_r  and its minimum over
        # the box is a lower bound on s whenever y >= 0.
        infeas = bool(node.get("infeas"))
        acc = Aff({}, ZERO) if infeas else Aff({0: ONE}, ZERO)
        for key, v in want.items():
            acc = acc + rows[key].scale(fx(v))
            self.n["mult"] += 1
        self.n["rows"] += len(want)
        lb = acc.range_over(box)
        if infeas:
            # a Farkas RAY: sum y_r f_r > 0 on the whole box means no point of the box satisfies
            # every row, i.e. the cell carries no interior-disjoint configuration at all.
            self.n["infeas"] += 1
            if Q(lb.lo, SCALE) <= 0:
                return self.fail("infeasibility ray gives %s <= 0" % float(Q(lb.lo, SCALE)))
            return True
        val = Q(lb.lo, SCALE)
        if len(self.capture) < self.capture_max:
            self.capture.append(dict(cells=dict(cells), sel=dict(sel), qrec=dict(qrec),
                                     rows={k: rows[k] for k in want}, y=dict(want), box=box,
                                     bound=val, node=node))
        if self.min_bound is None or val < self.min_bound:
            self.min_bound = val
        if val <= S0:
            return self.fail("dead leaf bound %s <= s0 (recorded %r)" % (float(val), node.get("bound")))
        return True

    def fail(self, msg):
        self.errors.append("depth %d: %s" % (self.depth, msg))
        return False


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(paths):
    sys.setrecursionlimit(100000)
    ok_all = True
    out = []
    for p in paths:
        t0 = time.time()
        cert = load(p)
        C = Checker(cert)
        ok = C.walk(cert["root"], C.root_cells(), {}, {}, {})
        wall = time.time() - t0
        rec = dict(file=os.path.basename(p), id=cert["meta"]["id"], ok=bool(ok),
                   sha256=sha256_of(p), seconds=round(wall, 1),
                   bytes=os.path.getsize(p), counts=dict(C.n),
                   certified_min=(None if C.min_bound is None else float(C.min_bound)),
                   s0=float(S0), errors=C.errors[:5])
        out.append(rec)
        print("%-34s %s  cells(bisect) %-7d branch %-4d imp %-6d dead-leaves %-7d rows %-8d "
              "min bound %.9f  %.1f s  %s" %
              (rec["id"], "VALID  " if ok else "INVALID", C.n["bisect"], C.n["branch"],
               C.n["imp"] + C.n["imp_sel"] + C.n["infeas"], C.n["dead"], C.n["rows"],
               rec["certified_min"] or float("nan"), wall, "" if ok else C.errors[:1]))
        ok_all = ok_all and ok
    res = os.path.join(HERE, "..", "results", "check_local.json")
    prev = []
    if os.path.exists(res):
        try:
            prev = json.load(open(res, encoding="utf-8")).get("runs", [])
        except Exception:
            prev = []
    with open(res, "w", encoding="utf-8") as f:
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out, previous=prev[:20]), f, indent=1)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
