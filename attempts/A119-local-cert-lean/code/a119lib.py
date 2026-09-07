"""A119 -- the local certificate as a frozen object.

This module re-implements A116's relaxed-LP row builder with (a) a UNIQUE STRUCTURED KEY per
row, so that a Farkas multiplier vector can be exported and re-checked by an independent
program, and (b) a subset builder, so that a candidate multiplier vector can be evaluated
without constructing the whole LP.  On top of it sits a selection tree that

  * records the whole proof object (the split structure + one Farkas vector per closed leaf),
  * inherits the parent's Farkas vector into each child and closes the child with it whenever
    it still certifies -- no LP call at all (the "shared cell / shared dual" of T3), and
  * shares one tilt-cell census across every leaf that meets the cell.

READ-ONLY on A116 (a116lib is imported for the bodies, the interval arithmetic, the shadow
poses, the samplers and the witness checks); nothing outside attempts/A119-local-cert-lean is
written by this module.

The row formulas are Lemma RELAX of docs/proofs/local_certificate.md §3.1 and are IDENTICAL to
a116lib.Rows (regression-checked by code/xcheck119.py, which compares LP values row-for-row).
"""
from __future__ import annotations

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
A116C = os.path.abspath(os.path.join(HERE, "..", "..", "A116-local-selection-tree", "code"))
sys.path.insert(0, A116C)
import a116lib as A  # noqa: E402  (imports blas1 before numpy)

import math, time  # noqa: E402
import numpy as np  # noqa: E402
import fastlp  # noqa: E402

BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
LOGS = os.path.join(BASE, "logs")
for d in (RES, CERTS, LOGS):
    os.makedirs(d, exist_ok=True)

IV = A.IV
S0 = A.S0
SELS = A.SELS


# ------------------------------------------------------------------ keyed rows
class KRows:
    """min s over the relaxed rows of one node.  Rows carry a unique key:

        ("w", body, "x"|"y", "lo"|"hi", wb)          wall row, wb = index of the h-lower-bound
        ("s", owner, other, k, eps, wb, "A"|"B1"|"B2")   selection row
        ("q", owner, other, k, eps, "lo"|"hi")       q-range split row

    `only` (a set of keys) restricts construction to those rows -- the fast path used when a
    candidate multiplier vector is evaluated.
    """

    def __init__(self, bodies, nv, s_lo, s_hi, cells=None, qranges=None, only=None):
        self.bodies, self.nv, self.s_lo, self.s_hi = bodies, nv, s_lo, s_hi
        self.cells = cells or {}
        self.qranges = qranges or {}
        self.only = only
        self.A, self.b, self.keys = [], [], []
        self.losses, self.qeff = {}, {}
        self.bounds = [(s_lo, s_hi)] + [None] * (nv - 1)
        for bd in bodies:
            if bd.kind == "free":
                self.bounds[bd.vi] = (bd.x0, bd.x1); self.bounds[bd.vi + 1] = (bd.y0, bd.y1)
                t = bd.tilt(self.cells)
                self.bounds[bd.ti] = (t.lo, t.hi)
            else:
                self.bounds[bd.vi] = (-bd.hh, bd.hh); self.bounds[bd.vi + 1] = (-bd.hh, bd.hh)
        assert all(bb is not None for bb in self.bounds)

    def _want(self, key):
        return self.only is None or key in self.only

    def add(self, coef, rhs, key):
        self.A.append(np.asarray(coef, dtype=float)); self.b.append(float(rhs)); self.keys.append(key)

    def tilt_affine(self, bd):
        c = np.zeros(self.nv)
        if bd.kind == "pin":
            return c, 0.0
        c[bd.ti] = 1.0
        return c, 0.0

    # -- walls: c.v + c0 >= h(t), s - (c.v + c0) >= h(t), h relaxed to affine lower bounds
    def walls(self, exact_theta=None):
        for bd in self.bodies:
            cx, x0, cy, y0 = bd.centre_affine(self.nv)
            if bd.kind == "pin":
                hbs = [(0.0, 0.5)]
            elif exact_theta is not None:
                hbs = [(0.0, A.half_width(exact_theta[bd.name]))]
            else:
                t = bd.tilt(self.cells)
                hbs = A.lower_bounds(A.half_width, t.lo, t.hi, scale=0.5)
            tc, _ = self.tilt_affine(bd)
            for wb, (hm, hc) in enumerate(hbs):
                for (c, c0, nm) in ((cx, x0, "x"), (cy, y0, "y")):
                    k1 = ("w", bd.name, nm, "lo", wb)
                    if self._want(k1):
                        self.add(-c + hm * tc, c0 - hc, k1)
                    k2 = ("w", bd.name, nm, "hi", wb)
                    if self._want(k2):
                        row = c.copy(); row[0] -= 1.0
                        self.add(row + hm * tc, -hc - c0, k2)

    # -- one pair's selection rows (Lemma RELAX)
    def selection(self, i, j, sel, exact_theta=None):
        (o, k, eps) = sel
        bw, bo = (self.bodies[i], self.bodies[j]) if o == 0 else (self.bodies[j], self.bodies[i])
        cxw, x0w, cyw, y0w = bw.centre_affine(self.nv)
        cxo, x0o, cyo, y0o = bo.centre_affine(self.nv)
        dcx, dx0 = cxo - cxw, x0o - x0w
        dcy, dy0 = cyo - cyw, y0o - y0w
        base = ("s", bw.name, bo.name, k, eps)
        if exact_theta is not None:
            tw = 0.0 if bw.kind == "pin" else exact_theta[bw.name]
            to = 0.0 if bo.kind == "pin" else exact_theta[bo.name]
            Ax, Ay = A.axis(tw, k)
            self.add(-eps * (dcx * Ax + dcy * Ay),
                     eps * (dx0 * Ax + dy0 * Ay) - 0.5 - 0.5 * A.wfun(tw - to), base + (0, "X"))
            return 0.0
        tw = bw.tilt(self.cells); to = bo.tilt(self.cells)
        tmid = 0.5 * (tw.lo + tw.hi); hw = 0.5 * (tw.hi - tw.lo)
        assert hw <= math.radians(60.0), "cell too wide for the relaxation"
        Ax, Ay = A.axis(tmid, k)
        Px, Py = -Ay, Ax
        xw, yw = bw.xrange(self.s_lo, self.s_hi)
        xo, yo = bo.xrange(self.s_lo, self.s_hi)
        dxr, dyr = xo - xw, yo - yw
        pr = IV(eps) * (dxr * IV(Ax) + dyr * IV(Ay))
        qr = IV(eps) * (dxr * IV(Px) + dyr * IV(Py))
        pc = eps * (dcx * Ax + dcy * Ay); p0 = eps * (dx0 * Ax + dy0 * Ay)
        qc = eps * (dcx * Px + dcy * Py); q0 = eps * (dx0 * Px + dy0 * Py)
        qlo, qhi = qr.lo, qr.hi
        if (i, j) in self.qranges:
            a_, b_ = self.qranges[(i, j)]
            qlo, qhi = max(qlo, a_), min(qhi, b_)
            if qlo > qhi:
                qlo, qhi = qhi, qlo
            kq1 = ("q", bw.name, bo.name, k, eps, "lo")
            if self._want(kq1):
                self.add(-qc, q0 - a_, kq1)
            kq2 = ("q", bw.name, bo.name, k, eps, "hi")
            if self._want(kq2):
                self.add(qc, b_ - q0, kq2)
        dr = tw - to
        tcw, _ = self.tilt_affine(bw); tco, _ = self.tilt_affine(bo)
        dcoef = tcw - tco
        if bw.kind == "pin" and bo.kind == "pin":
            wbs = [(0.0, 1.0)]
        else:
            wbs = A.lower_bounds(A.wfun, dr.lo, dr.hi)
        corr = max(0.0, -pr.lo) * (1 - math.cos(hw)) * (1 + 1e-12) + 1e-12
        if qlo >= 0:
            mq, cq = 1.0, 0.0
        elif qhi <= 0:
            mq, cq = -1.0, 0.0
        else:
            mq = (qhi + qlo) / (qhi - qlo); cq = -2.0 * qlo * qhi / (qhi - qlo)
        sh = math.sin(hw) * (1 + 1e-12)
        Us = [(sh * mq * qc, sh * (mq * q0 + cq), "A")]
        lossA = cq * sh
        if bw.kind == "free" and hw > 0:
            e3 = max(abs(qlo), abs(qhi)) * hw ** 3 / 6 * (1 + 1e-12) + 1e-12
            phic = tcw.copy(); phi0 = -tmid
            Us.append((qhi * phic - hw * qc, qhi * phi0 - hw * q0 + qhi * hw + e3, "B1"))
            Us.append((qlo * phic + hw * qc, qlo * phi0 + hw * q0 - qlo * hw + e3, "B2"))
            lossB = (qhi - qlo) * 2 * hw / 4
        else:
            lossB = 0.0
        for wb, (wm, wc) in enumerate(wbs):
            base_coef = -(pc - 0.5 * wm * dcoef)
            base_rhs = p0 + corr - 0.5 * wc - 0.5
            for (Uc, U0, nm) in Us:
                key = base + (wb, nm)
                if self._want(key):
                    self.add(base_coef - Uc, base_rhs + U0, key)
        self.losses[(i, j)] = min(lossA, lossB) if bw.kind == "free" else 0.0
        self.qeff[(i, j)] = (qlo, qhi)
        return self.losses[(i, j)]

    def solve(self):
        return fastlp.solve(self.A, self.b, self.bounds, self.nv)

    def dual_bound_vec(self, y):
        """min over the variable box of (c + A^T y).v - y.b -- a valid lower bound on min s for
        any y >= 0 (weak LP duality).  y is a numpy vector aligned with self.keys."""
        if y is None or not len(self.A):
            return -math.inf
        Am = np.array(self.A); bm = np.array(self.b)
        c = np.zeros(self.nv); c[0] = 1.0
        red = c + Am.T @ y
        lb = -float(y @ bm)
        for v in range(self.nv):
            lo, hi = self.bounds[v]
            lb += red[v] * (lo if red[v] > 0 else hi)
        return lb

    def infeas_bound_dict(self, ydict):
        """min over the box of (A^T y).x - y.b  (NO objective row): > 0 certifies that the rows
        are contradictory, i.e. the node's cell carries no configuration at all."""
        if not len(self.A):
            return -math.inf
        y = np.array([ydict.get(k, 0.0) for k in self.keys])
        if (y < -1e-15).any():
            return -math.inf
        Am = np.array(self.A); bm = np.array(self.b)
        red = Am.T @ y
        lb = -float(y @ bm)
        for v in range(self.nv):
            lo, hi = self.bounds[v]
            lb += red[v] * (lo if red[v] > 0 else hi)
        return lb

    def farkas_infeasible(self, tol=1e-9, round_bits=40):
        """(bound, y) with y a rational (denominator 2^round_bits) Farkas vector proving the rows
        infeasible, or (None, None)."""
        tau, y = fastlp.solve_phase1(self.A, self.b, self.bounds, self.nv)
        if y is None:
            return None, None
        yd = {self.keys[r]: float(y[r]) for r in range(len(self.keys)) if y[r] > 1e-12}
        if round_bits:
            sc = float(1 << round_bits)
            yr = {k: max(0.0, round(v * sc) / sc) for k, v in yd.items()}
            yr = {k: v for k, v in yr.items() if v > 0.0}
            if yr and self.infeas_bound_dict(yr) > tol:
                yd = yr
        lb = self.infeas_bound_dict(yd) if yd else -math.inf
        return (lb, yd) if lb > tol else (None, None)

    def dual_bound_dict(self, ydict):
        """as dual_bound_vec, for a {key: value} multiplier map (missing keys = 0)."""
        y = np.array([ydict.get(k, 0.0) for k in self.keys])
        if (y < -1e-15).any():
            return -math.inf
        return self.dual_bound_vec(np.maximum(y, 0.0))

    def support_dict(self, y, tol=1e-9):
        return {self.keys[r]: float(y[r]) for r in range(len(self.keys)) if y[r] > tol}


def build_krows(bodies, nv, s_lo, s_hi, fixed, cells=None, exact_theta=None, qranges=None, only=None):
    R = KRows(bodies, nv, s_lo, s_hi, cells=cells, qranges=qranges, only=only)
    R.walls(exact_theta)
    for (i, j), sel in fixed.items():
        R.selection(i, j, sel, exact_theta)
    return R


# ------------------------------------------------------------------ the recording tree
def key_str(k):
    return "|".join(str(v) for v in k)


class RecTree:
    """A116's Theorem-LOCAL tree with three additions:

    * DUAL INHERITANCE: a child first tries its parent's Farkas vector (restricted to the rows
      that still exist); the child's cell is narrower, so the relaxation loss is smaller and the
      same multipliers usually still certify.  A hit costs one sparse row build (~10 rows) and no
      LP.  A miss falls back to the full relaxed LP.
    * CELL SHARING: the interval census depends on the tilt cell alone, never on the selections,
      so it is computed once per cell and shared by every leaf that meets the cell (an explicit
      dict, unbounded, with the cell's canonical key).
    * RECORDING: the whole proof object -- the split tree (bisect / q-split / selection branch
      with the excluded selections' interval certificates) and one Farkas vector per closed leaf.

    `record=False` skips the proof object (T3's throughput runs); `record=True` builds it (T1).
    """

    def __init__(self, bodies, nv, s_lo=A.S_LO, s_hi=A.S_HI_DEFAULT, contact_pairs=None,
                 min_cell_deg=0.05, node_cap=2000000, time_cap=900.0, qsplit_min=2e-4,
                 exact_check_deg=0.25, record=False, log=None, inherit=False, margin=1e-8, round_bits=40, qdrop=True):
        self.bodies, self.nv, self.s_lo, self.s_hi = bodies, nv, s_lo, s_hi
        self.contact = set(contact_pairs or [])
        self.min_cell = math.radians(min_cell_deg)
        self.node_cap, self.time_cap = node_cap, time_cap
        self.qsplit_min = qsplit_min
        self.exact_check = math.radians(exact_check_deg)
        self.record, self.inherit = record, inherit
        self.margin = margin
        self.kill = S0 + margin
        self.round_bits = round_bits
        self.qdrop = qdrop   # False reproduces A116's (unsound, finding F1) q-range carry-over
        self.log = log or (lambda *a: None)
        self.free = [b for b in bodies if b.kind == "free"]
        self.tilted = {b.name for b in self.free if abs(b.anchor[2]) > 1e-9}
        self.name = {i: b.name for i, b in enumerate(bodies)}
        self.reset()

    def reset(self):
        self.stats = dict(nodes=0, impossible=0, dead_lp=0, dead_inherited=0, live_low=0,
                          unresolved=0, bisect=0, qsplit=0, branch=0, full_leaves=0, lp_calls=0,
                          census_calls=0, census_hits=0, qdrop=0, dual_short=0, dead_infeas=0)
        self.witnesses, self.unresolved = [], []
        self.closed = []
        self.near_root = None
        self._cc = {}
        self.t_start = time.time()
        self.capped = False
        self.proof = None
        self.last_y = None

    # -- cell census, shared across leaves
    def _census(self, cells):
        key = tuple(sorted((n, a, b) for n, (a, b) in cells.items()))
        c = self._cc.get(key)
        if c is None:
            self.stats["census_calls"] += 1
            c = A.census(self.bodies, self.s_lo, self.s_hi, cells)
            self._cc[key] = c
        else:
            self.stats["census_hits"] += 1
        return c

    def root_cells(self):
        return {b.name: (b.t0, b.t1) for b in self.free}

    def _cells_deg(self, cells):
        return {n: [math.degrees(a), math.degrees(b)] for n, (a, b) in cells.items()}

    def _width(self, cells):
        best, name = 0.0, None
        for n, (a, b) in cells.items():
            w = (b - a) * (1.0 if n in self.tilted else 0.5)
            if w > best:
                best, name = w, n
        return best, name

    def _excluded_cert(self, cells, pr, keep):
        """for a selection branch: the interval enclosure of every EXCLUDED selection of the pair,
        proving sup [g] < 0 (so Lemma SAT forces one of `keep`)."""
        i, j = pr
        poses = [self.bodies[q].pose_iv(self.s_lo, self.s_hi, cells) for q in (i, j)]
        out = []
        for (o, k, e) in SELS:
            if (o, k, e) in keep:
                continue
            if self.bodies[i].kind == "pin" and self.bodies[j].kind == "pin" and o == 1:
                out.append(dict(sel=[o, k, e], reason="pin-pin duplicate axis"))
                continue
            g = A.gap_sel_iv(poses[0], poses[1], o, k, e)
            out.append(dict(sel=[o, k, e], hi=g.hi))
        return out

    # -- the main loop
    def run(self):
        self.reset()
        cells = self.root_cells()
        near, far, imp = self._census(cells)
        self.near_root = dict(near=near, far=far, impossible=imp)
        root = {}
        stack = [(cells, {}, {}, None, root, frozenset())]
        self._loop(stack)
        self.proof = root if self.record else None
        return self.verdict()

    def _loop(self, stack):
        while stack:
            if self.stats["nodes"] >= self.node_cap or time.time() - self.t_start > self.time_cap:
                self.capped = True
                return
            cells, fixed, qsigns, ypar, node, bfix = stack.pop()
            self.stats["nodes"] += 1
            near, far, imp = self._census(cells)
            if imp:
                self.stats["impossible"] += 1
                if self.record:
                    i, j = imp[0]
                    node.update(k="imp", pair=[self.name[i], self.name[j]],
                                cert=self._excluded_cert(cells, (i, j), set()))
                continue
            fx = dict(fixed)
            bad = [(pr, sel) for pr, sel in fx.items() if pr in near and sel not in near[pr]]
            if bad:
                self.stats["impossible"] += 1
                if self.record:
                    (i, j), sel = bad[0]
                    node.update(k="imp_sel", pair=[self.name[i], self.name[j]], sel=list(sel),
                                cert=self._excluded_cert(cells, (i, j), set(SELS) - {sel}))
                continue
            for pr in list(fx):
                if pr not in near:
                    del fx[pr]
            for pr, poss in near.items():
                if pr not in fx and len(poss) == 1:
                    fx[pr] = poss[0]
            qs = {pr: rg for pr, rg in qsigns.items() if pr in fx}

            # -- fast path: a Farkas vector that already certified a NEARBY node (the last closed
            # leaf in DFS order, then this node's parent).  Sibling cells of a bisection are
            # killed by the same chain, so the same multipliers usually still certify; a hit
            # costs one sparse row build (the support only) and no LP call.
            if self.inherit:
                hit = False
                for cand in (self.last_y, ypar):
                    if not cand:
                        continue
                    keys = set(cand)
                    Rs = build_krows(self.bodies, self.nv, self.s_lo, self.s_hi, fx, cells,
                                     qranges=qs, only=keys)
                    if set(Rs.keys) != keys:
                        continue
                    lb = Rs.dual_bound_dict(cand)
                    if lb > self.kill:
                        self.stats["dead_inherited"] += 1
                        self._close(node, cells, fx, qs, lb, cand, bfix, inherited=True)
                        hit = True
                        break
                if hit:
                    continue

            R = build_krows(self.bodies, self.nv, self.s_lo, self.s_hi, fx, cells, qranges=qs)
            v, x, y = R.solve()
            self.stats["lp_calls"] += 1
            unfixed = [pr for pr in near if pr not in fx]
            width, wname = self._width(cells)
            if v == math.inf:
                # INFEASIBLE cell: certify it with a Farkas ray (phase 1), never on the solver's
                # word alone -- the exported vector must reproduce the contradiction.
                ib, yi = R.farkas_infeasible()
                if ib is not None:
                    self.stats["dead_infeas"] += 1
                    self._close(node, cells, fx, qs, math.inf, yi, bfix, inherited=False, infeas=True)
                    continue
                self.stats["dual_short"] += 1
            elif v > self.kill:
                # close on the FARKAS VECTOR, not on the LP value: the exported multipliers must
                # certify the bound on their own (weak duality, so this is never optimistic).
                yd = R.support_dict(y) if y is not None else {}
                if yd and self.round_bits:
                    sc = float(1 << self.round_bits)
                    yr = {k: max(0.0, round(v * sc) / sc) for k, v in yd.items()}
                    yr = {k: v for k, v in yr.items() if v > 0.0}
                    if yr and R.dual_bound_dict(yr) > self.kill:
                        yd = yr                     # a rational vector with denominator 2^rb
                lb = R.dual_bound_dict(yd) if yd else (v if v == math.inf else -math.inf)
                if lb > self.kill:
                    self.stats["dead_lp"] += 1
                    self._close(node, cells, fx, qs, lb, yd, bfix, inherited=False)
                    continue
                self.stats["dual_short"] += 1
            if unfixed:
                self.stats["branch"] += 1
                pr = min(unfixed, key=lambda q: (0 if q in self.contact else 1, len(near[q]), q))
                ch = []
                for sel in near[pr]:
                    f2 = dict(fx); f2[pr] = sel
                    c = {}
                    ch.append(c)
                    stack.append((cells, f2, qs, y_of(R, y), c, bfix | {pr}))
                if self.record:
                    node.update(k="branch", pair=[self.name[pr[0]], self.name[pr[1]]],
                                sels=[list(s) for s in near[pr]],
                                excluded=self._excluded_cert(cells, pr, set(near[pr])), ch=ch)
                continue
            # full selection, relaxed value <= s0: exact LPs at three tilt points (witness?)
            self.stats["full_leaves"] += 1
            vx, xx, thx = math.inf, None, None
            if width <= self.exact_check or v < S0 - 0.05 or width <= self.min_cell:
                for lam in (0.5, 0.0, 1.0):
                    th = {n: a + lam * (b - a) for n, (a, b) in cells.items()}
                    R2 = build_krows(self.bodies, self.nv, self.s_lo, self.s_hi, fx, cells, exact_theta=th)
                    v2, x2, y2 = R2.solve()
                    self.stats["lp_calls"] += 1
                    if v2 < vx:
                        vx, xx, thx = v2, x2, th
            rec = dict(value_relaxed=v, value_exact_best=(None if vx == math.inf else vx),
                       width_deg=math.degrees(width), cells=self._cells_deg(cells),
                       fixed={"%s|%s" % (self.name[i], self.name[j]): list(s) for (i, j), s in fx.items()})
            if vx <= S0 + 1e-9 and xx is not None:
                s_w, cfg = A.config_from_x(self.bodies, xx, thx)
                wp, ww = A.check_packing(s_w, cfg)
                rec.update(witness_side=s_w, witness_worst_pair=wp, witness_worst_wall=ww,
                           witness_cfg={n: [p[0], p[1], math.degrees(p[2])] for n, p in cfg.items()},
                           witness_valid=bool(wp >= -1e-7 and ww >= -1e-7))
                self.witnesses.append(rec)
                self.stats["live_low"] += 1
                if self.record:
                    node.update(k="live", side=s_w, valid=rec["witness_valid"])
                if rec["witness_valid"]:
                    return
                continue
            kind = self._refine_kind(R, cells, width)
            if kind is None:
                self.stats["unresolved"] += 1
                self.unresolved.append(rec)
                if self.record:
                    node.update(k="unresolved", value_relaxed=v)
                continue
            self._push(stack, kind, cells, fx, qs, wname, y_of(R, y), node, bfix)

    def _close(self, node, cells, fx, qs, lb, yd, bfix, inherited, infeas=False):
        self.last_y = yd or None
        self.closed.append(dict(value=lb, cells=cells, fixed=fx, qs=qs, inherited=inherited))
        if not self.record:
            return
        # the selections the LP actually leans on, and which of them a branch ancestor supplied
        sup_pairs = set()
        for kk in yd:
            if kk[0] in ("s", "q"):
                for (i, j) in fx:
                    if {self.name[i], self.name[j]} == {kk[1], kk[2]}:
                        sup_pairs.add((i, j))
        node.update(k="dead", bound=(None if lb == math.inf else lb), infeas=bool(infeas),
                    sel={"%s|%s" % (self.name[i], self.name[j]): list(fx[(i, j)]) for (i, j) in sorted(sup_pairs)},
                    forced=sorted("%s|%s" % (self.name[i], self.name[j])
                                  for (i, j) in sup_pairs if (i, j) not in bfix),
                    y={key_str(k): v for k, v in yd.items()})

    def _refine_kind(self, R, cells, width):
        total = sum(R.losses.values()) if R.losses else 0.0
        if R.losses:
            pr, loss = max(R.losses.items(), key=lambda t: t[1])
            if loss > self.qsplit_min and (loss > 0.6 * total or width <= self.min_cell) and width <= math.radians(1.0):
                return ("q", pr, R.qeff[pr])
        if width > self.min_cell:
            return ("t",)
        return None

    def _push(self, stack, kind, cells, fx, qs, wname, ypar, node, bfix):
        ch = []
        if kind[0] == "q":
            self.stats["qsplit"] += 1
            lo, hi = kind[2]
            m = 0.5 * (lo + hi)
            for rg in ((lo, m), (m, hi)):
                q2 = dict(qs); q2[kind[1]] = rg
                c = {}; ch.append(c)
                stack.append((cells, fx, q2, ypar, c, bfix))
            if self.record:
                i, j = kind[1]
                node.update(k="qsplit", pair=[self.name[i], self.name[j]], sel=list(fx[kind[1]]),
                            forced=bool(kind[1] not in bfix), lo=lo, mid=m, hi=hi, ch=ch)
        else:
            self.stats["bisect"] += 1
            a, b = cells[wname]
            m = 0.5 * (a + b)
            # SOUNDNESS: q is measured on the OWNER's axis at the cell midpoint, so bisecting the
            # owner's tilt cell redefines q -- a q-range case split made before the bisection would
            # no longer cover (A119 finding F1).  Drop the q-ranges whose owner is the bisected
            # body; the others are untouched.
            qs2 = ({pr: rg for pr, rg in qs.items()
                    if self.name[pr[0] if fx[pr][0] == 0 else pr[1]] != wname}
                   if self.qdrop else dict(qs))
            if len(qs2) != len(qs):
                self.stats["qdrop"] += 1
            for lohi in ((a, m), (m, b)):
                c2 = dict(cells); c2[wname] = lohi
                c = {}; ch.append(c)
                stack.append((c2, fx, qs2, ypar, c, bfix))
            if self.record:
                node.update(k="bisect", body=wname, lo=a, mid=m, hi=b, ch=ch)

    def certified(self):
        if not self.closed:
            return None
        return min(c["value"] for c in self.closed)

    def verdict(self):
        dead = (not self.capped) and self.stats["live_low"] == 0 and self.stats["unresolved"] == 0
        cm = self.certified()
        return dict(dead=dead, capped=self.capped, stats=dict(self.stats),
                    seconds=round(time.time() - self.t_start, 1),
                    n_near=len(self.near_root["near"]), n_far=len(self.near_root["far"]),
                    leaves_after_interval=int(np.prod([len(p) for p in self.near_root["near"].values()]))
                    if self.near_root["near"] else 1,
                    n_closed=len(self.closed),
                    certified_min=(None if cm is None or cm == math.inf else cm))


def y_of(R, y):
    """the parent's Farkas vector as a {key: value} dict, for inheritance."""
    if y is None:
        return None
    return R.support_dict(y)
