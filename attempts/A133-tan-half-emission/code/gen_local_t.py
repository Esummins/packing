"""A133 T1 -- re-emit a local certificate with the tilt in t = tan(theta/2).

    python gen_local_t.py <A119 certificate id> [more...]   [--min-cell 2e-4] [--cap 400000]

The neighbourhood `N` is READ from A119's certificate file (`meta`: the bodies, their centre
boxes, their tilt cells and the side window) and re-expressed in the Lean tilt parameter
`t = tan(theta/2)`; the selection tree, the interval census, the Farkas leaves and the emitted
certificate are then rebuilt here from scratch, in EXACT RATIONAL ARITHMETIC, by
`a133lib`.  No pi, no Taylor series, no dyadic interval kernel: `cos theta` and `sin theta` are
rational functions of `t`, so every enclosure the certificate needs is the exact range of a
rational function over a rational cell, and every constant in a relaxed row is a rational number
of the cell endpoints.

Differences from A119's generator, all of them consequences of the parametrisation:

  * the tilt cell of a body is a t-interval with DYADIC endpoints, bisected at the exact
    rational midpoint -- so the cover of the tilt box is exact rational data (A126's (C1));
  * `w = |cos D| + |sin D|` is lower-bounded by the TWO smooth branches `cos D +- sin D`,
    which are valid on the whole cell and whose maximum is `w` -- A119's V-lines without the
    kink location, hence without `pi` (A119's `kink_in` disappears);
  * `h(t) = (cos + sin)/2` is CONCAVE on `t in [0, 1]`, so its affine lower bound is the exact
    chord through the two endpoint values;
  * `sin(theta(t) - theta(t*))` is a rational function of `t` and is enclosed between two affine
    functions of `t` with the same (secant) slope, second order in the cell width;
  * every one of those envelopes is certified by a BERNSTEIN test on an exact rational
    polynomial -- decidable, and the same test the independent checker and the Lean checker run;
  * A119's finding E2 cannot happen here: a leaf is recorded by the SAME code path whether its
    Farkas vector is a side bound or an infeasibility ray (`_close`), and the emitted count is
    asserted against the tree's own dead-leaf counter before the file is written;
  * A119's finding E3 does not arise: a tilt cell that leaves the fundamental domain
    `theta in [0 deg, 90 deg]` is clipped to its inside part HERE, at the definition of `N`, so
    the emitted `N` is exactly the `N` the certificate is about.

READ-ONLY on A119: `certs/*.cert.json.gz` are read and `code/fastlp.py` is imported.  Nothing
outside `attempts/A133-tan-half-emission/` is written.
"""
from __future__ import annotations

import argparse, gzip, json, math, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A119C = os.path.abspath(os.path.join(BASE, "..", "A119-local-cert-lean", "code"))
A119CERT = os.path.abspath(os.path.join(BASE, "..", "A119-local-cert-lean", "certs"))
sys.path.insert(0, HERE)
sys.path.insert(0, A119C)

import a133lib as L                                    # noqa: E402
from a133lib import IQ                                 # noqa: E402
import numpy as np                                     # noqa: E402
import fastlp                                          # noqa: E402  (A119, imported read-only)

S0 = Q(969271, 250000)
SELS8 = [(o, k, e) for o in (0, 1) for k in (0, 1) for e in (1, -1)]
TBITS = 24                     # the root t-cell endpoints are multiples of 2^-TBITS
ROWDEN = 10 ** 12              # the emitted rows sit on this denominator


# ------------------------------------------------------------------ affine forms
class Aff:
    """sum_v co[v] x_v + k, exact rationals."""
    __slots__ = ("co", "k")

    def __init__(self, co=None, k=Q(0)):
        self.co = dict(co or {})
        self.k = Q(k)

    def __add__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c.get(v, Q(0)) + a
        return Aff(c, self.k + o.k)

    def __sub__(self, o):
        c = dict(self.co)
        for v, a in o.co.items():
            c[v] = c.get(v, Q(0)) - a
        return Aff(c, self.k - o.k)

    def scale(self, f):
        f = Q(f)
        if f == 0:
            return Aff()
        return Aff({v: a * f for v, a in self.co.items()}, self.k * f)

    def range_over(self, box):
        lo = hi = self.k
        for v, a in self.co.items():
            bl, bh = box[v]
            if a >= 0:
                lo += a * bl; hi += a * bh
            else:
                lo += a * bh; hi += a * bl
        return IQ(lo, hi)

    def min_over(self, box):
        return self.range_over(box).lo

    def dense(self, nv):
        c = [0.0] * nv
        for v, a in self.co.items():
            c[v] = float(a)
        return c


def var(v):
    return Aff({v: Q(1)}, Q(0))


def const(x):
    return Aff({}, Q(x))


# ------------------------------------------------------------------ bodies
def tan_half(theta: float) -> float:
    return math.tan(theta / 2.0)


def dyadic_up(x: float, bits: int) -> Q:
    return Q(math.ceil(x * (1 << bits)), 1 << bits)


def dyadic_down(x: float, bits: int) -> Q:
    return Q(math.floor(x * (1 << bits)), 1 << bits)


class BodyT:
    def __init__(self, d):
        self.name, self.kind, self.vi = d["name"], d["kind"], d["vi"]
        if self.kind == "free":
            self.ti = d["ti"]
            self.x0, self.x1 = Q(d["x0"]), Q(d["x1"])
            self.y0, self.y1 = Q(d["y0"]), Q(d["y1"])
            # the ANGLE cell of A119, clipped to the fundamental domain and rounded INWARD:
            # N shrinks, LocalHyp becomes harder to satisfy, LocalDead weaker -- the sound way.
            t0 = max(0.0, tan_half(d["t0"]))
            t1 = min(1.0, tan_half(d["t1"]))
            self.t0 = max(Q(0), dyadic_up(t0, TBITS))
            self.t1 = min(Q(1), dyadic_down(t1, TBITS))
            self.clipped = (d["t0"] < -1e-15) or (d["t1"] > math.pi / 2 + 1e-15)
            if self.t0 >= self.t1:
                raise SystemExit("body %s: empty t cell" % self.name)
        else:
            self.ti = None
            self.ax = (Q(d["ax"][0]), Q(d["ax"][1]))
            self.ay = (Q(d["ay"][0]), Q(d["ay"][1]))
            self.hh = Q(d["hh"])
            self.clipped = False

    def centre(self):
        if self.kind == "pin":
            return (Aff({0: self.ax[1], self.vi: Q(1)}, self.ax[0]),
                    Aff({0: self.ay[1], self.vi + 1: Q(1)}, self.ay[0]))
        return var(self.vi), var(self.vi + 1)

    def tcell(self, cells):
        return (Q(0), Q(0)) if self.kind == "pin" else cells[self.name]

    def taff(self):
        return Aff() if self.kind == "pin" else var(self.ti)

    def xy_range(self, s_lo, s_hi):
        if self.kind == "pin":
            return ((self.ax[0] + self.ax[1] * s_lo - self.hh, self.ax[0] + self.ax[1] * s_hi + self.hh),
                    (self.ay[0] + self.ay[1] * s_lo - self.hh, self.ay[0] + self.ay[1] * s_hi + self.hh))
        return ((self.x0, self.x1), (self.y0, self.y1))


# ------------------------------------------------------------------ the exact census
class Geo:
    """the exact rational geometry of one neighbourhood, with the per-cell caches."""

    def __init__(self, bodies, nv, s_lo, s_hi):
        self.bodies, self.nv = bodies, nv
        self.s_lo, self.s_hi = s_lo, s_hi
        self.by = {b.name: b for b in bodies}
        self.free = [b for b in bodies if b.kind == "free"]
        self.box0 = {0: (s_lo, s_hi)}
        for b in bodies:
            if b.kind == "free":
                self.box0[b.vi] = (b.x0, b.x1)
                self.box0[b.vi + 1] = (b.y0, b.y1)
            else:
                self.box0[b.vi] = (-b.hh, b.hh)
                self.box0[b.vi + 1] = (-b.hh, b.hh)
        self.xyr = {b.name: b.xy_range(s_lo, s_hi) for b in bodies}
        self._wc, self._sc, self._hc, self._gc = {}, {}, {}, {}
        # the ENVELOPE TABLE: every affine envelope Lemma RELAX uses, keyed by the cell it is
        # stated on, so that the checker (and the Lean checker) VERIFY the constants this
        # generator chose instead of having to re-derive them to the same sharpness.
        self.env_h, self.env_S, self.env_w = {}, {}, {}

    def root_cells(self):
        return {b.name: (b.t0, b.t1) for b in self.free}

    def cellbox(self, cells):
        bx = dict(self.box0)
        for b in self.free:
            bx[b.ti] = cells[b.name]
        return bx

    # -- caches
    def h_chord(self, a, b):
        v = self._hc.get((a, b))
        if v is None:
            v = L.chord_h(a, b)
            self._hc[(a, b)] = v
            self.env_h["%s|%s" % (a, b)] = [str(v[0]), str(v[1])]
        return v

    def S_env(self, a, b):
        v = self._sc.get((a, b))
        if v is None:
            v = L.aff_bounds_S((a + b) / 2, a, b)
            self._sc[(a, b)] = v
            self.env_S["%s|%s" % (a, b)] = [str(v[0]), str(v[1]), str(v[2])]
        return v

    def w_env(self, eps, aw, bw, ao, bo):
        key = (eps, aw, bw, ao, bo)
        v = self._wc.get(key)
        if v is None:
            v = L.aff_lower_w(eps, aw, bw, ao, bo)
            self._wc[key] = v
            self.env_w["%d|%s|%s|%s|%s" % (eps, aw, bw, ao, bo)] = \
                [str(v[0]), str(v[1]), str(v[2])]
        return v

    # -- the selection gap enclosure (Lemma SAT's row) over a cell
    def gap(self, bw, bo, k, eps, cells):
        key = (bw.name, bo.name, k, eps, cells[bw.name] if bw.kind == "free" else None,
               cells[bo.name] if bo.kind == "free" else None)
        v = self._gc.get(key)
        if v is not None:
            return v
        (twl, twh) = bw.tcell(cells)
        (tol, toh) = bo.tcell(cells)
        ax, ay = L.axis_range(twl, twh, k)
        (xwl, xwh), (ywl, ywh) = self.xyr[bw.name]
        (xol, xoh), (yol, yoh) = self.xyr[bo.name]
        DX = IQ(xol - xwh, xoh - xwl)
        DY = IQ(yol - ywh, yoh - ywl)
        w = L.w_range_cell(twl, twh, tol, toh)
        g = IQ(eps) * (DX * ax + DY * ay) - IQ(Q(1, 2)) - IQ(Q(1, 2)) * w
        self._gc[key] = g
        return g

    def census(self, cells):
        near, far, imp = {}, [], []
        nb = len(self.bodies)
        for i in range(nb):
            for j in range(i + 1, nb):
                bi, bj = self.bodies[i], self.bodies[j]
                poss, isfar = [], False
                for (o, k, e) in SELS8:
                    if bi.kind == "pin" and bj.kind == "pin" and o == 1:
                        continue
                    bw, bo = (bi, bj) if o == 0 else (bj, bi)
                    g = self.gap(bw, bo, k, e, cells)
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

    def excluded_cert(self, cells, pr, keep):
        i, j = pr
        bi, bj = self.bodies[i], self.bodies[j]
        out = []
        for (o, k, e) in SELS8:
            if (o, k, e) in keep:
                continue
            if bi.kind == "pin" and bj.kind == "pin" and o == 1:
                out.append(dict(sel=[o, k, e], dup=True))
                continue
            bw, bo = (bi, bj) if o == 0 else (bj, bi)
            g = self.gap(bw, bo, k, e, cells)
            out.append(dict(sel=[o, k, e], hi=float(g.hi)))
        return out


# ------------------------------------------------------------------ Lemma RELAX in t
class RowsT:
    """the relaxed rows of one node, EXACT.  Keys:

        ("w", body, "x"|"y", "lo"|"hi")                    wall row (h's chord)
        ("s", owner, other, k, eps, weps, "A"|"B1"|"B2")   selection row
    """

    def __init__(self, geo: Geo, cells, fixed):
        self.g, self.cells, self.fixed = geo, cells, fixed
        self.box = geo.cellbox(cells)
        self.rows = {}
        self._walls()
        for (i, j), sel in fixed.items():
            self._selection(i, j, sel)

    # -- wall rows: c >= h(t) and s - c >= h(t)
    def _walls(self):
        for b in self.g.bodies:
            cx, cy = b.centre()
            if b.kind == "pin":
                m, c = Q(0), Q(1, 2)
            else:
                a, bb = self.cells[b.name]
                m, c = self.g.h_chord(a, bb)
            hb = b.taff().scale(m) + const(c)                 # h(t) >= hb
            for (cc, nm) in ((cx, "x"), (cy, "y")):
                self.rows[("w", b.name, nm, "lo")] = const(0) - cc + hb
                self.rows[("w", b.name, nm, "hi")] = cc - var(0) + hb

    # -- one selection's relaxed rows
    def _selection(self, i, j, sel):
        (o, k, eps) = sel
        bw, bo = (self.g.bodies[i], self.g.bodies[j]) if o == 0 else \
                 (self.g.bodies[j], self.g.bodies[i])
        cxw, cyw = bw.centre()
        cxo, cyo = bo.centre()
        dcx, dcy = cxo - cxw, cyo - cyw
        (aw, bwid) = bw.tcell(self.cells)
        (ao, boh) = bo.tcell(self.cells)
        tm = (aw + bwid) / 2
        Ax, Ay = L.axis_pt(tm, k)
        Px, Py = -Ay, Ax
        P = (dcx.scale(Ax) + dcy.scale(Ay)).scale(eps)        # eps d.a_k(theta(tm))
        QQ = (dcx.scale(Px) + dcy.scale(Py)).scale(eps)       # eps d.a_k'(theta(tm))
        pr = P.range_over(self.box)
        qr = QQ.range_over(self.box)
        qlo, qhi = qr.lo, qr.hi

        # phi = theta(t_w) - theta(tm); u = tan(phi/2) = (t_w - tm)/(1 + t_w tm)
        if bw.kind == "pin" or aw == bwid:
            corr = Q(0)
            Us = [(Aff(), "A")]
        else:
            uiv = L.u_range(aw, bwid, tm, tm)
            U = max(abs(uiv.lo), abs(uiv.hi))
            one_m_cos = 2 * U * U / (1 + U * U)               # max of 1 - cos phi on the cell
            corr = max(Q(0), -pr.lo) * one_m_cos
            Slo = L.sinT(uiv.lo) if uiv.lo >= 0 else -L.sinT(-uiv.lo)
            Shi = L.sinT(uiv.hi) if uiv.hi >= 0 else -L.sinT(-uiv.hi)
            Slo, Shi = min(Slo, Shi), max(Slo, Shi)
            Sabs = max(abs(Slo), abs(Shi))
            alpha, bup, blo = self.g.S_env(aw, bwid)
            Sup = var(bw.ti).scale(alpha) + const(bup)        # S(t_w) <= Sup
            Sdn = var(bw.ti).scale(alpha) + const(blo)        # S(t_w) >= Sdn
            # (A)  Q S <= |Q| Sabs <= Sabs (mq Q + cq),  the chord of |Q| over [qlo, qhi]
            if qlo >= 0:
                mq, cq = Q(1), Q(0)
            elif qhi <= 0:
                mq, cq = Q(-1), Q(0)
            else:
                mq = (qhi + qlo) / (qhi - qlo)
                cq = -2 * qlo * qhi / (qhi - qlo)
            Us = [((QQ.scale(mq) + const(cq)).scale(Sabs), "A")]
            # (B) McCormick on Q S with S in [Slo, Shi]:
            #     (Q - qhi)(S - Slo) <= 0  and  (Q - qlo)(S - Shi) <= 0
            Us.append(((Sup if qhi >= 0 else Sdn).scale(qhi) + QQ.scale(Slo)
                       + const(-qhi * Slo), "B1"))
            Us.append(((Sup if qlo >= 0 else Sdn).scale(qlo) + QQ.scale(Shi)
                       + const(-qlo * Shi), "B2"))

        # w's affine lower bounds over the cell product
        if bw.kind == "pin" and bo.kind == "pin":
            wbs = [(Q(0), Q(0), Q(1), 0)]
        else:
            wbs = []
            for widx, we in ((0, 1), (1, -1)):
                mw, mo, c = self.g.w_env(we, aw, bwid, ao, boh)
                wbs.append((mw, mo, c, widx))
        tw_aff, to_aff = bw.taff(), bo.taff()
        base_key = ("s", bw.name, bo.name, k, eps)
        for (mw, mo, c, widx) in wbs:
            Wlb = tw_aff.scale(mw) + to_aff.scale(mo) + const(c)
            # true: P + corr + U >= Proj >= 1/2 + w/2 >= 1/2 + Wlb/2
            base = Wlb.scale(Q(1, 2)) + const(Q(1, 2) - corr) - P
            for (Uf, nm) in Us:
                self.rows[base_key + (widx, nm)] = base - Uf

    # -- LP interface
    def lp(self, nv):
        keys = sorted(self.rows, key=lambda t: tuple(str(v) for v in t))
        A = [self.rows[k].dense(nv) for k in keys]
        b = [float(-self.rows[k].k) for k in keys]
        bounds = [(float(self.box[v][0]), float(self.box[v][1])) for v in range(nv)]
        return keys, A, b, bounds

    def dual_bound(self, ydict, infeas=False):
        acc = Aff() if infeas else var(0)
        for kk, v in ydict.items():
            if v < 0:
                return None
            acc = acc + self.rows[kk].scale(v)
        return acc.min_over(self.box)


# ------------------------------------------------------------------ the tree
class TreeT:
    def __init__(self, geo: Geo, min_cell=Q(1, 5000), node_cap=600000, time_cap=3600.0,
                 margin=Q(1, 10 ** 8), round_bits=40, log=print):
        self.g = geo
        self.min_cell = Q(min_cell)
        self.node_cap, self.time_cap = node_cap, time_cap
        self.kill = S0 + margin
        self.round_bits = round_bits
        self.log = log
        self.name = {i: b.name for i, b in enumerate(geo.bodies)}
        self.contact = set()
        self.reset()

    def reset(self):
        self.stats = dict(nodes=0, imp=0, imp_sel=0, dead=0, dead_infeas=0, bisect=0, branch=0,
                          lp_calls=0, dual_short=0, unresolved=0, rows=0, mult=0,
                          census_calls=0, census_hits=0)
        self.leaves = []
        self.unresolved = []
        self.min_bound = None
        self._cc = {}
        self.t0 = time.time()
        self.capped = False

    def census(self, cells):
        key = tuple(sorted((n, a, b) for n, (a, b) in cells.items()))
        c = self._cc.get(key)
        if c is None:
            self.stats["census_calls"] += 1
            c = self.g.census(cells)
            self._cc[key] = c
        else:
            self.stats["census_hits"] += 1
        return c

    def widest(self, cells):
        best, nm = Q(-1), None
        for n, (a, b) in cells.items():
            if b - a > best:
                best, nm = b - a, n
        return best, nm

    def run(self):
        self.reset()
        root = {}
        stack = [(self.g.root_cells(), {}, root, frozenset())]
        while stack:
            if self.stats["nodes"] >= self.node_cap or time.time() - self.t0 > self.time_cap:
                self.capped = True
                break
            self._node(stack, *stack.pop())
        return root

    def _node(self, stack, cells, fixed, node, bfix):
        self.stats["nodes"] += 1
        near, far, imp = self.census(cells)
        if imp:
            self.stats["imp"] += 1
            i, j = imp[0]
            node.update(k="imp", pair=[self.name[i], self.name[j]],
                        cert=self.g.excluded_cert(cells, (i, j), set()))
            return
        fx = dict(fixed)
        bad = [(pr, s) for pr, s in fx.items() if pr in near and s not in near[pr]]
        if bad:
            self.stats["imp_sel"] += 1
            (i, j), s = bad[0]
            node.update(k="imp_sel", pair=[self.name[i], self.name[j]], sel=list(s),
                        cert=self.g.excluded_cert(cells, (i, j), set(SELS8) - {s}))
            return
        for pr in list(fx):
            if pr not in near:
                del fx[pr]
        for pr, poss in near.items():
            if pr not in fx and len(poss) == 1:
                fx[pr] = poss[0]
        R = RowsT(self.g, cells, fx)
        keys, A, b, bounds = R.lp(self.g.nv)
        v, x, y = fastlp.solve(A, b, bounds, self.g.nv)
        self.stats["lp_calls"] += 1
        if v == math.inf:
            tau, yv = fastlp.solve_phase1(A, b, bounds, self.g.nv)
            yd = self._round(keys, yv)
            if yd:
                lb = R.dual_bound(yd, infeas=True)
                if lb is not None and lb > 0:
                    self.stats["dead_infeas"] += 1
                    self._close(node, cells, fx, R, yd, bfix, lb, True)
                    return
            self.stats["dual_short"] += 1
        elif v > float(self.kill):
            yd = self._round(keys, y)
            if yd:
                lb = R.dual_bound(yd, infeas=False)
                if lb is not None and lb > self.kill:
                    self.stats["dead"] += 1
                    self._close(node, cells, fx, R, yd, bfix, lb, False)
                    return
            self.stats["dual_short"] += 1
        unfixed = [pr for pr in near if pr not in fx]
        if unfixed:
            self.stats["branch"] += 1
            pr = min(unfixed, key=lambda q: (len(near[q]), q))
            ch = []
            for sel in near[pr]:
                f2 = dict(fx); f2[pr] = sel
                c = {}; ch.append(c)
                stack.append((cells, f2, c, bfix | {pr}))
            node.update(k="branch", pair=[self.name[pr[0]], self.name[pr[1]]],
                        sels=[list(s) for s in near[pr]],
                        excluded=self.g.excluded_cert(cells, pr, set(near[pr])), ch=ch)
            return
        width, wname = self.widest(cells)
        if width <= self.min_cell:
            self.stats["unresolved"] += 1
            self.unresolved.append(dict(cells={n: [float(a), float(bb)] for n, (a, bb) in cells.items()},
                                        value=v, fixed={"%s|%s" % (self.name[i], self.name[j]): list(s)
                                                        for (i, j), s in fx.items()}))
            node.update(k="unresolved", value=v)
            return
        self.stats["bisect"] += 1
        a, bb = cells[wname]
        m = (a + bb) / 2
        ch = []
        for lohi in ((a, m), (m, bb)):
            c2 = dict(cells); c2[wname] = lohi
            c = {}; ch.append(c)
            stack.append((c2, fx, c, bfix))
        node.update(k="bisect", body=wname, lo=str(a), mid=str(m), hi=str(bb), ch=ch)

    def _round(self, keys, y):
        if y is None:
            return None
        sc = 1 << self.round_bits
        out = {}
        for r, val in enumerate(y):
            if val > 1e-12:
                q = Q(max(0, round(float(val) * sc)), sc)
                if q > 0:
                    out[keys[r]] = q
        return out

    def _close(self, node, cells, fx, R, yd, bfix, lb, infeas):
        """the ONE recording path for a closed leaf, taken by a side bound and by an
        infeasibility ray alike (A126's finding E2 cannot recur here)."""
        sup_pairs = set()
        for kk in yd:
            if kk[0] == "s":
                for (i, j) in fx:
                    if {self.name[i], self.name[j]} == {kk[1], kk[2]}:
                        sup_pairs.add((i, j))
        self.stats["rows"] += len(yd)
        self.stats["mult"] += len(yd)
        if not infeas and (self.min_bound is None or lb < self.min_bound):
            self.min_bound = lb
        node.update(k="dead", infeas=bool(infeas), bound=(None if infeas else str(lb)),
                    sel={"%s|%s" % (self.name[i], self.name[j]): list(fx[(i, j)])
                         for (i, j) in sorted(sup_pairs)},
                    forced=sorted("%s|%s" % (self.name[i], self.name[j])
                                  for (i, j) in sup_pairs if (i, j) not in bfix),
                    y={"|".join(str(t) for t in kk): str(v) for kk, v in yd.items()},
                    leaf=len(self.leaves))
        self.leaves.append(dict(cells={n: (a, b) for n, (a, b) in cells.items()},
                                infeas=bool(infeas), rows=R.rows, y=dict(yd), box=dict(R.box),
                                bound=lb))


# ------------------------------------------------------------------ emission
def quantise_leaf(leaf, nv, den=ROWDEN):
    """the leaf's rows and multipliers on one denominator, rounded so that the EMITTED row is
    implied by the true relaxed row on the leaf's box: coefficients to the nearest multiple of
    1/den, the constant LOWERED by the total rounding slack over the box."""
    box = leaf["box"]
    out = []
    for kk, v in sorted(leaf["y"].items(), key=lambda t: tuple(str(z) for z in t[0])):
        row = leaf["rows"][kk]
        co = {}
        slack = Q(0)
        for var_i, a in row.co.items():
            r = Q(round(a * den), den)
            co[var_i] = r
            bl, bh = box[var_i]
            d = r - a
            slack += (d * bh if d >= 0 else d * bl)
        kconst = Q(math.floor((row.k - slack) * den), den)
        yq = Q(round(v * den), den)
        if yq < 0:
            yq = Q(0)
        out.append((kk, co, kconst, yq))
    # the Farkas bound RE-EVALUATED from the emitted (rounded) integers, exactly
    acc = Aff() if leaf["infeas"] else var(0)
    for (kk, co, kc, yq) in out:
        acc = acc + Aff(co, kc).scale(yq)
    return out, acc.min_over(box)


def emit(cert_id, geo, tree, root, meta, path, wall):
    nv = geo.nv
    leaves = []
    worst = None
    for li, leaf in enumerate(tree.leaves):
        rows, qbound = quantise_leaf(leaf, nv)
        floor_ = Q(0) if leaf["infeas"] else S0
        if qbound <= floor_:
            raise AssertionError("leaf %d: the QUANTISED Farkas bound %s does not clear %s"
                                 % (li, float(qbound), float(floor_)))
        marg = qbound - floor_
        worst = marg if worst is None else min(worst, marg)
        box = [[str(leaf["box"][v][0]), str(leaf["box"][v][1])] for v in range(nv)]
        leaves.append(dict(infeas=bool(leaf["infeas"]), box=box,
                           rows=[dict(key="|".join(str(t) for t in kk),
                                      co={str(v): str(a) for v, a in co.items() if a != 0},
                                      k=str(kc), y=str(yq)) for (kk, co, kc, yq) in rows]))
    meta["worst_quantised_margin"] = (None if worst is None else str(worst))
    out = dict(meta=meta, root=root, leaves=leaves,
               env=dict(h=geo.env_h, S=geo.env_S, w=geo.env_w),
               stats=dict(tree.stats), seconds=round(wall, 1),
               certified_min=(None if tree.min_bound is None else str(tree.min_bound)))
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def run_one(cid, args):
    src = os.path.join(args.certdir or A119CERT, cid + ".cert.json.gz")
    with gzip.open(src, "rt", encoding="utf-8") as f:
        a119 = json.load(f)
    m = a119["meta"]
    bodies = [BodyT(d) for d in m["bodies"]]
    s_lo, s_hi = Q(m["s_lo"]), Q(m["s_hi"])
    geo = Geo(bodies, m["nv"], s_lo, s_hi)
    tree = TreeT(geo, min_cell=Q(args.min_cell), node_cap=args.cap, time_cap=args.time_cap)
    t0 = time.time()
    root = tree.run()
    wall = time.time() - t0
    dead = (not tree.capped) and tree.stats["unresolved"] == 0
    meta = dict(id=cid, format="local-cert-t-v1", source=os.path.relpath(src, os.path.join(BASE, "..", "..")),
                tag=m["tag"], cls=m["cls"], r=m["r"], rho_deg=m["rho_deg"],
                nv=m["nv"], L=m["L"], P=m["P"], s_lo=str(s_lo), s_hi=str(s_hi),
                s0=[969271, 250000], row_denominator=ROWDEN, t_bits=TBITS,
                bern_depth=[L.DEPTH1, L.DEPTH2],
                tilt_param="t = tan(theta/2)",
                min_cell_t=str(Q(args.min_cell)),
                generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                generator="attempts/A133-tan-half-emission/code/gen_local_t.py",
                bodies=[dict(name=b.name, kind=b.kind, vi=b.vi, ti=b.ti,
                             **(dict(x0=str(b.x0), x1=str(b.x1), y0=str(b.y0), y1=str(b.y1),
                                     t0=str(b.t0), t1=str(b.t1), clipped=b.clipped)
                                if b.kind == "free" else
                                dict(ax=[str(b.ax[0]), str(b.ax[1])],
                                     ay=[str(b.ay[0]), str(b.ay[1])], hh=str(b.hh))))
                        for b in bodies],
                dead=bool(dead))
    path = os.path.join(BASE, "certs", cid + ".tcert.json.gz")
    out = emit(cid, geo, tree, root, meta, path, wall)
    print("%-28s %s  nodes %-7d bisect %-6d branch %-4d dead %-6d (rays %d) rows %-7d "
          "unres %-4d  min %s  %.1f s  %.2f MB"
          % (cid, "DEAD   " if dead else ("CAPPED " if tree.capped else "OPEN   "),
             tree.stats["nodes"], tree.stats["bisect"], tree.stats["branch"],
             tree.stats["dead"] + tree.stats["dead_infeas"], tree.stats["dead_infeas"],
             tree.stats["rows"], tree.stats["unresolved"],
             ("%.9f" % float(tree.min_bound)) if tree.min_bound is not None else "-",
             wall, os.path.getsize(path) / 1e6))
    if tree.unresolved:
        print("   first unresolved:", json.dumps(tree.unresolved[0])[:400])
    assert len(tree.leaves) == tree.stats["dead"] + tree.stats["dead_infeas"], \
        "emitted leaf count != tree dead-leaf count"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=600000)
    ap.add_argument("--time-cap", type=float, default=5400.0)
    ap.add_argument("--certdir", default=None,
                    help="directory of the SOURCE certificates (default A119's); A125's S33/S38 "
                         "live in attempts/A125-*/certs")
    args = ap.parse_args()
    for cid in args.ids:
        run_one(cid, args)


if __name__ == "__main__":
    main()
