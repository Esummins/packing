#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_pair.py -- reference verifier for format `pair-certificate-v1`.

Written FROM docs/specs/pair_certificate_v1.md (sections 2 and 3 are normative).
This verifier is NOT part of the frozen TCB (verify_measure.py / verify_case.py /
verify_param.py are untouched by this file).

WHAT A PASS ESTABLISHES (spec section 1)
----------------------------------------
  (P1')  W2 = sum_i w_i  <  C(N,2) + beta*m,  N = n - k
  (P2')  for every unordered pair {Q,Q'} of closed unit squares in [0,s]^2 (any
         orientations) with (i) neither Q nor Q' meeting any core K_j and
         (ii) int Q ^ int Q' = empty, the collected mass
             mu2{Q,Q'} = sum{ w_i : (p_i in Q and p'_i in Q') or (p_i in Q' and p'_i in Q) }
         satisfies mu2 >= 1 + beta*m2(Q,Q').

ARITHMETIC
----------
Whole decision path is exact `fractions.Fraction`.  There is NO float shortcut on the
decision path at all (floats appear only in witness rendering, progress output, and in
--selftest, which is a cross-check harness, never an acceptor).  Hence floats cannot
cause a spurious PASS or a spurious FAIL here.

ORIENTATION PARAMETRISATION (as in case-lp-certificate-v1)
----------------------------------------------------------
  t = tan(theta/2) in [0,1],  theta in [0, pi/2]
  cos theta = (1 - t^2)/(1 + t^2)      -- DECREASING in t on [0,1]
  sin theta = 2t/(1 + t^2)             -- INCREASING in t on [0,1]
so over a t-interval [t0,t1] the exact enclosures are
  cos in [cos(t1), cos(t0)],  sin in [sin(t0), sin(t1)].

WIDTH FUNCTION w(t) = cos + sin  --  BOUND CHOICES (declared, per task):
  * LOWER bound on [t0,t1]:  w_lo = min(w(t0), w(t1)).
    (w is unimodal on [0,1] with its single maximum at t* = sqrt(2)-1, so the minimum
    over any subinterval is attained at an endpoint.)
  * UPPER bound on [t0,t1]:  if the interval provably excludes t* then w is monotone
    there and w_hi = max(w(t0), w(t1)); otherwise w_hi = SQRT2_UB = 19601/13860.
    19601^2 = 384199201 > 384199200 = 2*13860^2, so 19601/13860 > sqrt(2) >= w.
    t* is bracketed exactly by  408/985 < t* < 5741/13860
    (from 1393/985 < sqrt 2 < 19601/13860, both verified by cross-multiplication:
     1393^2 = 1940449 < 1940450 = 2*985^2).
  NOTE (spec ambiguity resolved): the task text suggested "e.g. 181/128" as a rational
  >= sqrt(2); 181/128 = 1.4140625 < sqrt(2) = 1.41421356..., so it is NOT an upper
  bound and would be UNSOUND.  We use 19601/13860 instead.

BODY-FRAME SIGN CONVENTION (spec section 3.4 of case-lp-certificate-v1 does not pin the
sign; declared here).  Q(c, theta) = c + R(theta) * [-1/2,1/2]^2, so
    p in Q(c,theta)  <=>  |u| <= 1/2 and |v| <= 1/2,  (u,v) = R(-theta) (p - c),
    u =  C*dx + S*dy,   v = -S*dx + C*dy,   d = p - c.
The mirror convention (u,v) = R(+theta)(p-c) is the reflection of this one in the x-axis,
a symmetry of [0,s]^2; the two agree on every reflection-symmetric certificate (both toys)
but NOT on a general atom list, so a real certificate must be emitted in this convention.

NONDISJOINT half-widths.  For the normal u1 = (cos th1, sin th1) the half-width of Q1 is
exactly 1/2, and that of Q2 is g/2 with g = |cos(th1-th2)| + |sin(th1-th2)| >= 1 (same g on
all four normals, by symmetry).  We use the exact enclosure of g floored at 1.

DISCHARGE ORDER (spec section 3): VACUOUS, EXEMPT-core, NONDISJOINT, COVERED, else SPLIT.

CONSERVATIVITY LEDGER (spec section 3, four items -- all error directions make PASS harder):
  * VACUOUS clips OUTWARD (uses w_lo, so the clip contains every admissible placement).
  * EXEMPT-core is granted only when the four SAT non-separation inequalities hold for
    EVERY parameter of the factor box (sup of |offset| vs w_lo-based thresholds).
  * NONDISJOINT is granted only when all four edge-normal directions certainly fail to
    weakly separate over the WHOLE pair box (sup |dc.u| < inf half-width sum, strict).
  * COVERED under-counts mass (certain membership only) and over-counts the bonus
    requirement (U counts boxes only POSSIBLY met, an upper bound for m2).

EXIT CODES: 0 PASS, 1 FAIL, 2 malformed / (P1') violated.
"""

import sys
import os
import json
import time
import argparse
import hashlib
import random
from fractions import Fraction as Fr

# --------------------------------------------------------------------------------------
# exact constants
# --------------------------------------------------------------------------------------
HALF = Fr(1, 2)
ONE = Fr(1)
SQRT2_UB = Fr(19601, 13860)      # > sqrt(2)
TSTAR_LO = Fr(408, 985)          # < sqrt(2) - 1
TSTAR_HI = Fr(5741, 13860)       # > sqrt(2) - 1


# --------------------------------------------------------------------------------------
# exact interval arithmetic on Fractions.  An interval is a 2-tuple (lo, hi), lo <= hi.
# --------------------------------------------------------------------------------------
def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def imul(a, b):
    p1 = a[0] * b[0]
    p2 = a[0] * b[1]
    p3 = a[1] * b[0]
    p4 = a[1] * b[1]
    return (min(p1, p2, p3, p4), max(p1, p2, p3, p4))


def isq(a):
    lo, hi = a
    if lo <= 0 <= hi:
        return (Fr(0), max(lo * lo, hi * hi))
    q1 = lo * lo
    q2 = hi * hi
    return (min(q1, q2), max(q1, q2))


def iabsmax(a):
    """sup |x| over the enclosure -- an UPPER bound on sup |expr|."""
    return max(abs(a[0]), abs(a[1]))


def iabsmin(a):
    """inf |x| over the enclosure -- a LOWER bound on inf |expr|."""
    lo, hi = a
    if lo <= 0 <= hi:
        return Fr(0)
    return min(abs(lo), abs(hi))


# --------------------------------------------------------------------------------------
# orientation
# --------------------------------------------------------------------------------------
def cos_t(t):
    return (1 - t * t) / (1 + t * t)


def sin_t(t):
    return (2 * t) / (1 + t * t)


def w_t(t):
    return cos_t(t) + sin_t(t)


def w_lower(t0, t1):
    """Lower bound of w on [t0,t1] (exact; attained at an endpoint by unimodality)."""
    return min(w_t(t0), w_t(t1))


def w_upper(t0, t1):
    """Upper bound of w on [t0,t1]."""
    if t1 <= TSTAR_LO or t0 >= TSTAR_HI:
        return max(w_t(t0), w_t(t1))
    return SQRT2_UB


def cs_encl(t0, t1):
    """Exact enclosures (C, S) of (cos theta, sin theta) over t in [t0,t1] c [0,1]."""
    return ((cos_t(t1), cos_t(t0)), (sin_t(t0), sin_t(t1)))


# --------------------------------------------------------------------------------------
# rational parsing (spec section 2: exact rational strings; JSON floats rejected)
# --------------------------------------------------------------------------------------
class Malformed(Exception):
    pass


def _no_floats(x):
    raise Malformed("JSON float literal encountered; all numbers must be exact "
                    "rational STRINGS (e.g. \"199/100\", \"3.877084\")")


def rat(x, what="value"):
    if isinstance(x, bool):
        raise Malformed("bad %s: boolean" % what)
    if isinstance(x, int):
        return Fr(x)
    if isinstance(x, str):
        s = x.strip()
        try:
            return Fr(s)
        except (ValueError, ZeroDivisionError):
            raise Malformed("bad rational string for %s: %r" % (what, x))
    raise Malformed("bad %s: %r (expected rational string)" % (what, x))


def as_int(x, what, default=None):
    if x is None:
        if default is None:
            raise Malformed("missing integer field %s" % what)
        return default
    if isinstance(x, bool) or not isinstance(x, int):
        raise Malformed("field %s must be a JSON integer" % what)
    return x


# --------------------------------------------------------------------------------------
# certificate
# --------------------------------------------------------------------------------------
class Cert(object):
    __slots__ = ("s", "n", "k", "m", "beta", "cores", "boxes", "P", "Q", "W",
                 "W2", "N", "threshold", "path")

    def __init__(self, path):
        self.path = path
        with open(path, "r") as fh:
            raw = fh.read()
        try:
            obj = json.loads(raw, parse_float=_no_floats)
        except Malformed:
            raise
        except Exception as exc:
            raise Malformed("unparseable JSON: %s" % exc)
        if not isinstance(obj, dict):
            raise Malformed("top level must be an object")
        fmt = obj.get("format")
        if fmt != "pair-certificate-v1":
            raise Malformed("format must be \"pair-certificate-v1\" (got %r)" % (fmt,))

        self.s = rat(obj.get("s"), "s")
        if self.s <= 0:
            raise Malformed("s must be > 0")
        self.n = as_int(obj.get("n"), "n", 11)
        self.k = as_int(obj.get("k"), "k")
        self.m = as_int(obj.get("m"), "m")
        self.beta = rat(obj.get("beta", "0"), "beta")
        if self.beta < 0:
            raise Malformed("beta must be >= 0")

        cores = obj.get("cores", [])
        if not isinstance(cores, list):
            raise Malformed("cores must be a list")
        self.cores = []
        for j, c in enumerate(cores):
            if not isinstance(c, dict):
                raise Malformed("cores[%d] must be an object" % j)
            a = rat(c.get("a"), "cores[%d].a" % j)
            if a < 0:
                raise Malformed("cores[%d].a must be >= 0" % j)
            self.cores.append((rat(c.get("kx"), "cores[%d].kx" % j),
                               rat(c.get("ky"), "cores[%d].ky" % j), a))
        if len(self.cores) != self.k:
            raise Malformed("k = %d but %d cores given" % (self.k, len(self.cores)))

        boxes = obj.get("boxes", [])
        if not isinstance(boxes, list):
            raise Malformed("boxes must be a list")
        self.boxes = []
        for j, b in enumerate(boxes):
            if not isinstance(b, dict):
                raise Malformed("boxes[%d] must be an object" % j)
            h = rat(b.get("h"), "boxes[%d].h" % j)
            if h < 0:
                raise Malformed("boxes[%d].h must be >= 0" % j)
            self.boxes.append((rat(b.get("bx"), "boxes[%d].bx" % j),
                               rat(b.get("by"), "boxes[%d].by" % j), h))
        if len(self.boxes) != self.m:
            raise Malformed("m = %d but %d boxes given" % (self.m, len(self.boxes)))

        atoms = obj.get("atoms", [])
        if not isinstance(atoms, list):
            raise Malformed("atoms must be a list")
        self.P = []
        self.Q = []
        self.W = []
        for i, at in enumerate(atoms):
            if not isinstance(at, dict):
                raise Malformed("atoms[%d] must be an object" % i)
            w = rat(at.get("w"), "atoms[%d].w" % i)
            if w < 0:
                raise Malformed("atoms[%d].w must be >= 0" % i)
            self.P.append((rat(at.get("px"), "atoms[%d].px" % i),
                           rat(at.get("py"), "atoms[%d].py" % i)))
            self.Q.append((rat(at.get("qx"), "atoms[%d].qx" % i),
                           rat(at.get("qy"), "atoms[%d].qy" % i)))
            self.W.append(w)

        self.W2 = sum(self.W, Fr(0))
        tot = obj.get("total")
        if tot is not None:
            if rat(tot, "total") != self.W2:
                sys.stderr.write("warning: declared total != sum of weights; "
                                 "computed value governs\n")
        self.N = self.n - self.k
        if self.N < 0:
            raise Malformed("N = n - k must be >= 0")
        self.threshold = Fr(self.N * (self.N - 1), 2) + self.beta * self.m


# --------------------------------------------------------------------------------------
# factor boxes.  A factor box is the 6-tuple (t0,t1,x0,x1,y0,y1) of Fractions,
# ALWAYS stored in clipped (canonical) form.
# --------------------------------------------------------------------------------------
class World(object):
    """Everything derived from the certificate that the B&B needs, plus caches."""

    def __init__(self, cert):
        self.c = cert
        self.fcache = {}

    # ---- canonical construction (rule 1: VACUOUS / outward clip) ----------------------
    def make_factor(self, t0, t1, x0, x1, y0, y1):
        """Return the clipped factor box, or None if it has no admissible placement."""
        wlo = w_lower(t0, t1)
        lo = wlo / 2
        hi = self.c.s - wlo / 2
        nx0 = x0 if x0 > lo else lo
        nx1 = x1 if x1 < hi else hi
        if nx0 > nx1:
            return None
        ny0 = y0 if y0 > lo else lo
        ny1 = y1 if y1 < hi else hi
        if ny0 > ny1:
            return None
        return (t0, t1, nx0, nx1, ny0, ny1)

    # ---- cached per-factor data ------------------------------------------------------
    def fdata(self, f):
        d = self.fcache.get(f)
        if d is None:
            d = FactorData(self, f)
            self.fcache[f] = d
        return d


class FactorData(object):
    __slots__ = ("f", "C", "S", "wlo", "whi", "dx", "dy",
                 "exempt", "certP", "certQ", "possible")

    def __init__(self, world, f):
        c = world.c
        t0, t1, x0, x1, y0, y1 = f
        self.f = f
        self.C, self.S = cs_encl(t0, t1)
        self.wlo = w_lower(t0, t1)
        self.whi = w_upper(t0, t1)
        self.dx = (x0, x1)
        self.dy = (y0, y1)
        self.exempt = self._exempt_core(c)
        self.certP = self._certain_points(c.P)
        self.certQ = self._certain_points(c.Q)
        self.possible = self._possible_boxes(c)

    # rule 2: EXEMPT-core -------------------------------------------------------------
    def _exempt_core(self, c):
        C, S = self.C, self.S
        wlo = self.wlo
        for (kx, ky, a) in c.cores:
            dx = (self.dx[0] - kx, self.dx[1] - kx)
            dy = (self.dy[0] - ky, self.dy[1] - ky)
            thr_axis = a + wlo / 2
            if iabsmax(dx) > thr_axis:
                continue
            if iabsmax(dy) > thr_axis:
                continue
            thr_body = HALF + a * wlo
            u = iadd(imul(dx, C), imul(dy, S))
            if iabsmax(u) > thr_body:
                continue
            v = isub(imul(dy, C), imul(dx, S))
            if iabsmax(v) > thr_body:
                continue
            return True
        return False

    # rule 4 (mass): certain point-in-square membership over the whole factor box ------
    def _certain_points(self, pts):
        C, S = self.C, self.S
        x0, x1 = self.dx
        y0, y1 = self.dy
        out = set()
        for i, (px, py) in enumerate(pts):
            dx = (px - x1, px - x0)
            dy = (py - y1, py - y0)
            u = iadd(imul(dx, C), imul(dy, S))
            if u[0] < -HALF or u[1] > HALF:
                continue
            v = isub(imul(dy, C), imul(dx, S))
            if v[0] < -HALF or v[1] > HALF:
                continue
            out.add(i)
        return frozenset(out)

    # rule 4 (bonus): boxes POSSIBLY met (negation of certain interior separation) -----
    def _possible_boxes(self, c):
        if not c.boxes or c.beta == 0:
            return frozenset()
        C, S = self.C, self.S
        whi = self.whi
        out = set()
        for j, (bx, by, h) in enumerate(c.boxes):
            dx = (self.dx[0] - bx, self.dx[1] - bx)
            dy = (self.dy[0] - by, self.dy[1] - by)
            thr_axis = h + whi / 2
            if iabsmin(dx) >= thr_axis:
                continue
            if iabsmin(dy) >= thr_axis:
                continue
            thr_body = HALF + h * whi
            u = iadd(imul(dx, C), imul(dy, S))
            if iabsmin(u) >= thr_body:
                continue
            v = isub(imul(dy, C), imul(dx, S))
            if iabsmin(v) >= thr_body:
                continue
            out.add(j)
        return frozenset(out)


# --------------------------------------------------------------------------------------
# rule 3: NONDISJOINT
# --------------------------------------------------------------------------------------
def dc_encl(d1, d2):
    """Exact enclosure of dc = c2 - c1 over the pair box."""
    return ((d2.dx[0] - d1.dx[1], d2.dx[1] - d1.dx[0]),
            (d2.dy[0] - d1.dy[1], d2.dy[1] - d1.dy[0]))


def g_lower(d1, d2):
    """Lower bound of g = |cos(th1-th2)| + |sin(th1-th2)|.  Mathematically g >= 1."""
    cc = iadd(imul(d1.C, d2.C), imul(d1.S, d2.S))          # cos(th1 - th2) >= 0
    ss = isub(imul(d1.S, d2.C), imul(d1.C, d2.S))          # sin(th1 - th2)
    g = cc[0] + iabsmin(ss)
    return g if g > ONE else ONE


def nondisjoint(d1, d2):
    """True iff EVERY pair of placements in the pair box certainly has overlapping
    interiors (SAT converse on the four edge normals, outward enclosures)."""
    dcx, dcy = dc_encl(d1, d2)
    # fast sufficient pre-test: sup ||dc||^2 < 1 (inscribed open disks of radius 1/2 meet)
    if iadd(isq(dcx), isq(dcy))[1] < ONE:
        return True
    bound = HALF + g_lower(d1, d2) / 2
    for (C, S) in ((d1.C, d1.S), (d2.C, d2.S)):
        if iabsmax(iadd(imul(dcx, C), imul(dcy, S))) >= bound:   # |dc . u|
            return False
        if iabsmax(isub(imul(dcy, C), imul(dcx, S))) >= bound:   # |dc . v|
            return False
    return True


def nd_margins(d1, d2):
    """The four (bound - sup|dc.n|) margins; all > 0 is exactly the NONDISJOINT test."""
    dcx, dcy = dc_encl(d1, d2)
    bound = HALF + g_lower(d1, d2) / 2
    out = []
    for (C, S) in ((d1.C, d1.S), (d2.C, d2.S)):
        out.append(bound - iabsmax(iadd(imul(dcx, C), imul(dcy, S))))
        out.append(bound - iabsmax(isub(imul(dcy, C), imul(dcx, S))))
    return out


# --------------------------------------------------------------------------------------
# the branch and bound
# --------------------------------------------------------------------------------------
class Run(object):
    def __init__(self, cert, depth, split, tscale, max_witnesses=8, progress=0):
        self.c = cert
        self.world = World(cert)
        self.depth = depth
        self.split = split
        self.tscale = tscale
        self.max_witnesses = max_witnesses
        self.progress = progress
        self.counts = dict(pairs_examined=0, vacuous=0, exempt_core=0, nondisjoint=0,
                           covered=0, split=0, max_depth=0, pairs_root=0)
        self.witnesses = []
        self.nd_samples = []      # reservoir of NONDISJOINT-discharged pair boxes
        self.ex_samples = []      # reservoir of EXEMPT-core-discharged factor boxes

    # ---- root ------------------------------------------------------------------------
    def roots(self):
        c = self.c
        w = self.world
        wmin = w_lower(Fr(0), Fr(1))                # = 1
        lo = wmin / 2
        hi = c.s - wmin / 2
        g = 2 ** self.split
        facs = []
        nvac = 0
        if lo <= hi:
            span = hi - lo
            for ia in range(g):
                xa = lo + span * Fr(ia, g)
                xb = lo + span * Fr(ia + 1, g)
                for ib in range(g):
                    ya = lo + span * Fr(ib, g)
                    yb = lo + span * Fr(ib + 1, g)
                    f = w.make_factor(Fr(0), Fr(1), xa, xb, ya, yb)
                    if f is None:
                        nvac += 1
                    else:
                        facs.append(f)
        out = []
        for i in range(len(facs)):
            for j in range(i, len(facs)):
                out.append((facs[i], facs[j], 0))
        self.counts["pairs_root"] = len(out) + nvac
        self.counts["vacuous"] += nvac
        return out

    # ---- children --------------------------------------------------------------------
    def children(self, f1, f2):
        ts = self.tscale
        w1 = ((f1[1] - f1[0]) * ts, f1[3] - f1[2], f1[5] - f1[4])
        w2 = ((f2[1] - f2[0]) * ts, f2[3] - f2[2], f2[5] - f2[4])
        widths = (w1[0], w1[1], w1[2], w2[0], w2[1], w2[2])
        best = 0
        for idx in range(1, 6):
            if widths[idx] > widths[best]:
                best = idx
        if widths[best] == 0:
            return None                              # degenerate point box
        which = 0 if best < 3 else 1
        dim = best % 3
        f = f1 if which == 0 else f2
        lo = f[2 * dim]
        hi = f[2 * dim + 1]
        mid = (lo + hi) / 2
        kids = []
        for (a, b) in ((lo, mid), (mid, hi)):
            v = list(f)
            v[2 * dim] = a
            v[2 * dim + 1] = b
            nf = self.world.make_factor(*v)
            if nf is None:
                self.counts["vacuous"] += 1
                continue
            kids.append((nf, f2, ) if which == 0 else (f1, nf))
        return kids

    # ---- main loop -------------------------------------------------------------------
    def solve(self):
        c = self.c
        w = self.world
        need_base = ONE
        beta = c.beta
        W = c.W
        stack = self.roots()
        cnt = self.counts
        t_last = time.time()
        while stack:
            f1, f2, d = stack.pop()
            cnt["pairs_examined"] += 1
            if d > cnt["max_depth"]:
                cnt["max_depth"] = d
            if self.progress and cnt["pairs_examined"] % self.progress == 0:
                now = time.time()
                sys.stderr.write("  ... %d pairs, stack %d, depth %d, %.1fs\n"
                                 % (cnt["pairs_examined"], len(stack), d, now - t_last))
                sys.stderr.flush()
            d1 = w.fdata(f1)
            d2 = w.fdata(f2)

            # 2. EXEMPT-core
            if d1.exempt or d2.exempt:
                cnt["exempt_core"] += 1
                if len(self.ex_samples) < 400:
                    self.ex_samples.append(f1 if d1.exempt else f2)
                continue

            # 3. NONDISJOINT
            if nondisjoint(d1, d2):
                cnt["nondisjoint"] += 1
                if len(self.nd_samples) < 400:
                    self.nd_samples.append((f1, f2))
                continue

            # 4. COVERED
            mass = Fr(0)
            a1p, a1q, a2p, a2q = d1.certP, d1.certQ, d2.certP, d2.certQ
            for i in (a1p & a2q) | (a1q & a2p):
                mass += W[i]
            if beta:
                U = len(d1.possible & d2.possible)
                need = need_base + beta * U
            else:
                U = 0
                need = need_base
            if mass >= need:
                cnt["covered"] += 1
                continue

            # 5. SPLIT
            if d >= self.depth:
                self.record_witness(f1, f2, d, mass, need, U)
                if len(self.witnesses) >= self.max_witnesses:
                    return False
                continue
            kids = self.children(f1, f2)
            if kids is None:
                self.record_witness(f1, f2, d, mass, need, U, degenerate=True)
                if len(self.witnesses) >= self.max_witnesses:
                    return False
                continue
            cnt["split"] += 1
            for (g1, g2) in kids:
                stack.append((g1, g2, d + 1))
        return len(self.witnesses) == 0

    def record_witness(self, f1, f2, d, mass, need, U, degenerate=False):
        d1 = self.world.fdata(f1)
        d2 = self.world.fdata(f2)
        gaps = nd_margins(d1, d2)
        self.witnesses.append(dict(
            depth=d, degenerate=degenerate,
            F=[str(x) for x in f1], Fp=[str(x) for x in f2],
            F_float=[float(x) for x in f1], Fp_float=[float(x) for x in f2],
            certain_mass=str(mass), required=str(need), U=U,
            deficit=str(need - mass), deficit_float=float(need - mass),
            sat_margins=[str(g) for g in gaps],
            sat_margins_float=[float(g) for g in gaps],
            confirm=confirm_disjoint_witness(self.c, f1, f2),
        ))


# --------------------------------------------------------------------------------------
# witness confirmation: exhibit a CONCRETE admissible pair of squares in the witness box
# whose interiors are disjoint (exact arithmetic), with the separating-axis gap.
# --------------------------------------------------------------------------------------
def _placements(cert, f):
    """A few concrete admissible placements inside the factor box (exact)."""
    t0, t1, x0, x1, y0, y1 = f
    out = []
    for t in (t0, (t0 + t1) / 2, t1):
        wt = w_t(t)
        lo = wt / 2
        hi = cert.s - wt / 2
        if lo > hi:
            continue
        for cx in (x0, (x0 + x1) / 2, x1):
            cxc = lo if cx < lo else (hi if cx > hi else cx)
            for cy in (y0, (y0 + y1) / 2, y1):
                cyc = lo if cy < lo else (hi if cy > hi else cy)
                out.append((t, cxc, cyc))
    return out


def sat_gap(t1v, c1, t2v, c2):
    """max over the 4 edge normals of (|dc.n| - (hw1 + hw2)).  >= 0  <=>  interiors
    disjoint (exact)."""
    C1, S1 = cos_t(t1v), sin_t(t1v)
    C2, S2 = cos_t(t2v), sin_t(t2v)
    dx = c2[0] - c1[0]
    dy = c2[1] - c1[1]
    g = abs(C1 * C2 + S1 * S2) + abs(S1 * C2 - C1 * S2)   # |cos dth| + |sin dth|
    bound = HALF + g / 2
    best = None
    for (C, S) in ((C1, S1), (C2, S2)):
        for p in (abs(dx * C + dy * S), abs(dy * C - dx * S)):
            v = p - bound
            if best is None or v > best:
                best = v
    return best


def confirm_disjoint_witness(cert, f1, f2):
    """Search the witness pair box for a concrete admissible, interior-disjoint,
    core-free pair.  Returns the best (largest gap) find, or None."""
    best = None
    for (t1v, x1v, y1v) in _placements(cert, f1):
        for (t2v, x2v, y2v) in _placements(cert, f2):
            gap = sat_gap(t1v, (x1v, y1v), t2v, (x2v, y2v))
            if gap < 0:
                continue
            if best is None or gap > best[0]:
                best = (gap, (t1v, x1v, y1v), (t2v, x2v, y2v))
    if best is None:
        return None
    gap, a, b = best
    return dict(
        sat_gap=str(gap), sat_gap_float=float(gap),
        square1=dict(t=str(a[0]), cx=str(a[1]), cy=str(a[2]),
                     cos=str(cos_t(a[0])), sin=str(sin_t(a[0])),
                     w=str(w_t(a[0])), admissible=bool(
                         w_t(a[0]) / 2 <= a[1] <= cert.s - w_t(a[0]) / 2 and
                         w_t(a[0]) / 2 <= a[2] <= cert.s - w_t(a[0]) / 2)),
        square2=dict(t=str(b[0]), cx=str(b[1]), cy=str(b[2]),
                     cos=str(cos_t(b[0])), sin=str(sin_t(b[0])),
                     w=str(w_t(b[0])), admissible=bool(
                         w_t(b[0]) / 2 <= b[1] <= cert.s - w_t(b[0]) / 2 and
                         w_t(b[0]) / 2 <= b[2] <= cert.s - w_t(b[0]) / 2)),
        note="interiors are disjoint iff sat_gap >= 0 (exact rational)",
    )


# --------------------------------------------------------------------------------------
# selftest: random float cross-checks of the three exact accept predicates
# --------------------------------------------------------------------------------------
def _rr(rng, a, b, den=1 << 14):
    return a + (b - a) * Fr(rng.randrange(den + 1), den)


def _square_contains_float(t, cx, cy, px, py):
    tt = float(t)
    C = (1.0 - tt * tt) / (1.0 + tt * tt)
    S = (2.0 * tt) / (1.0 + tt * tt)
    dx = float(px) - float(cx)
    dy = float(py) - float(cy)
    u = dx * C + dy * S
    v = dy * C - dx * S
    return max(abs(u), abs(v))


def selftest(nsamp=2000, seed=20260901, verbose=True):
    rng = random.Random(seed)
    res = {}
    TOL = 1e-9

    # ---- (a) certain point-in-square membership --------------------------------------
    hits = 0
    viol = 0
    cert = Cert.__new__(Cert)
    cert.s = Fr(4)
    cert.cores = []
    cert.boxes = []
    cert.beta = Fr(0)
    guard = 0
    while hits < nsamp and guard < 4000000:
        guard += 1
        t0 = _rr(rng, Fr(0), Fr(9, 10))
        t1 = t0 + _rr(rng, Fr(0), Fr(1, 20))
        cx = _rr(rng, Fr(1), Fr(3))
        cy = _rr(rng, Fr(1), Fr(3))
        hw = _rr(rng, Fr(0), Fr(1, 20))
        f = (t0, t1, cx - hw, cx + hw, cy - hw, cy + hw)
        px = cx + _rr(rng, Fr(-2, 5), Fr(2, 5))
        py = cy + _rr(rng, Fr(-2, 5), Fr(2, 5))
        cert.P = [(px, py)]
        cert.Q = [(px, py)]
        cert.W = [Fr(1)]
        w = World(cert)
        fd = FactorData(w, f)
        if 0 not in fd.certP:
            continue
        # claimed certain: check random parameters in the box
        for _ in range(3):
            if hits >= nsamp:
                break
            t = _rr(rng, t0, t1)
            ccx = _rr(rng, f[2], f[3])
            ccy = _rr(rng, f[4], f[5])
            hits += 1
            mf = _square_contains_float(t, ccx, ccy, px, py)
            if mf > 0.5 + TOL:
                # exact confirmation of the violation
                C, S = cos_t(t), sin_t(t)
                dx, dy = px - ccx, py - ccy
                u = dx * C + dy * S
                v = dy * C - dx * S
                if max(abs(u), abs(v)) > HALF:
                    viol += 1
    res["membership"] = dict(samples=hits, violations=viol)

    # ---- (b) NONDISJOINT --------------------------------------------------------------
    hits = 0
    viol = 0
    cert2 = Cert.__new__(Cert)
    cert2.s = Fr(4)
    cert2.cores = []
    cert2.boxes = []
    cert2.beta = Fr(0)
    cert2.P = []
    cert2.Q = []
    cert2.W = []
    w2 = World(cert2)
    guard = 0
    while hits < nsamp and guard < 4000000:
        guard += 1
        a0 = _rr(rng, Fr(0), Fr(9, 10))
        a1 = a0 + _rr(rng, Fr(0), Fr(1, 10))
        ax = _rr(rng, Fr(1), Fr(3))
        ay = _rr(rng, Fr(1), Fr(3))
        ahw = _rr(rng, Fr(0), Fr(1, 10))
        fa = (a0, a1, ax - ahw, ax + ahw, ay - ahw, ay + ahw)
        b0 = _rr(rng, Fr(0), Fr(9, 10))
        b1 = b0 + _rr(rng, Fr(0), Fr(1, 10))
        bhw = _rr(rng, Fr(0), Fr(1, 10))
        bx = ax + _rr(rng, Fr(-3, 4), Fr(3, 4))
        by = ay + _rr(rng, Fr(-3, 4), Fr(3, 4))
        fb = (b0, b1, bx - bhw, bx + bhw, by - bhw, by + bhw)
        da = w2.fdata(fa)
        db = w2.fdata(fb)
        if not nondisjoint(da, db):
            continue
        for _ in range(3):
            if hits >= nsamp:
                break
            ta = _rr(rng, fa[0], fa[1])
            ca = (_rr(rng, fa[2], fa[3]), _rr(rng, fa[4], fa[5]))
            tb = _rr(rng, fb[0], fb[1])
            cb = (_rr(rng, fb[2], fb[3]), _rr(rng, fb[4], fb[5]))
            hits += 1
            gap = sat_gap(ta, ca, tb, cb)      # exact; float rendering cross-checked
            if float(gap) >= -1e-12 and gap >= 0:
                viol += 1                      # claimed overlapping, actually separated
    res["nondisjoint"] = dict(samples=hits, violations=viol)

    # ---- (c) EXEMPT-core --------------------------------------------------------------
    hits = 0
    viol = 0
    guard = 0
    while hits < nsamp and guard < 4000000:
        guard += 1
        kx = _rr(rng, Fr(1), Fr(3))
        ky = _rr(rng, Fr(1), Fr(3))
        a = _rr(rng, Fr(0), Fr(1, 2))
        cert3 = Cert.__new__(Cert)
        cert3.s = Fr(4)
        cert3.cores = [(kx, ky, a)]
        cert3.boxes = []
        cert3.beta = Fr(0)
        cert3.P = []
        cert3.Q = []
        cert3.W = []
        w3 = World(cert3)
        t0 = _rr(rng, Fr(0), Fr(9, 10))
        t1 = t0 + _rr(rng, Fr(0), Fr(1, 10))
        cx = kx + _rr(rng, Fr(-1), Fr(1))
        cy = ky + _rr(rng, Fr(-1), Fr(1))
        hw = _rr(rng, Fr(0), Fr(1, 10))
        f = (t0, t1, cx - hw, cx + hw, cy - hw, cy + hw)
        fd = w3.fdata(f)
        if not fd.exempt:
            continue
        for _ in range(3):
            if hits >= nsamp:
                break
            t = _rr(rng, f[0], f[1])
            cc = (_rr(rng, f[2], f[3]), _rr(rng, f[4], f[5]))
            hits += 1
            # exact SAT: Q(t,cc) meets the axis core iff no axis separates strictly
            C, S = cos_t(t), sin_t(t)
            wv = C + S
            dxv = cc[0] - kx
            dyv = cc[1] - ky
            sep = (abs(dxv) > a + wv / 2 or abs(dyv) > a + wv / 2
                   or abs(dxv * C + dyv * S) > HALF + a * wv
                   or abs(dyv * C - dxv * S) > HALF + a * wv)
            if sep:
                viol += 1
    res["exempt_core"] = dict(samples=hits, violations=viol)

    if verbose:
        for kk, vv in res.items():
            print("selftest %-12s samples=%d violations=%d"
                  % (kk, vv["samples"], vv["violations"]))
    total_viol = sum(v["violations"] for v in res.values())
    ok = total_viol == 0 and all(v["samples"] >= nsamp for v in res.values())
    print("SELFTEST %s (total violations %d)" % ("OK" if ok else "FAILED", total_viol))
    return 0 if ok else 1


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description="verify a pair-certificate-v1 certificate")
    ap.add_argument("cert", nargs="?", help="certificate JSON")
    ap.add_argument("--depth", type=int, default=40)
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--tscale", default="2")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--progress", type=int, default=0,
                    help="print a progress line every N pair boxes (0 = off)")
    ap.add_argument("--max-witnesses", type=int, default=8)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(args.selftest_n, args.seed)

    if not args.cert:
        ap.error("certificate path required (or --selftest)")

    try:
        tscale = Fr(args.tscale)
        if tscale <= 0:
            raise Malformed("tscale must be > 0")
        if args.split < 0 or args.depth < 0:
            raise Malformed("split/depth must be >= 0")
        cert = Cert(args.cert)
    except Malformed as exc:
        print("MALFORMED: %s" % exc)
        return 2
    except IOError as exc:
        print("MALFORMED: %s" % exc)
        return 2

    print("cert            %s" % os.path.abspath(args.cert))
    print("s = %s   n = %d  k = %d  m = %d  beta = %s  N = %d"
          % (cert.s, cert.n, cert.k, cert.m, cert.beta, cert.N))
    print("W2 = %s   threshold C(N,2)+beta*m = %s" % (cert.W2, cert.threshold))
    print("atoms %d  cores %d  boxes %d" % (len(cert.W), cert.k, cert.m))
    print("settings: depth=%d split=%d tscale=%s" % (args.depth, args.split, tscale))

    if cert.W2 >= cert.threshold:
        print("(P1') VIOLATED: W2 >= C(N,2) + beta*m -- the certificate proves nothing")
        return 2
    print("(P1') OK")

    t0 = time.time()
    run = Run(cert, args.depth, args.split, tscale,
              max_witnesses=args.max_witnesses, progress=args.progress)
    ok = run.solve()
    elapsed = time.time() - t0
    c = run.counts
    print("pairs_root      %d" % c["pairs_root"])
    print("pairs_examined  %d" % c["pairs_examined"])
    print("vacuous         %d" % c["vacuous"])
    print("exempt_core     %d" % c["exempt_core"])
    print("nondisjoint     %d" % c["nondisjoint"])
    print("covered         %d" % c["covered"])
    print("split           %d" % c["split"])
    print("max_depth       %d" % c["max_depth"])
    print("wall            %.3f s" % elapsed)

    if ok:
        print("VERDICT: PASS")
    else:
        print("VERDICT: FAIL  (%d witness(es) reported, first below)" % len(run.witnesses))
        w0 = run.witnesses[0]
        print("  witness depth %d" % w0["depth"])
        print("  F  = t[%s,%s] x[%s,%s] y[%s,%s]" % tuple(w0["F"]))
        print("  F' = t[%s,%s] x[%s,%s] y[%s,%s]" % tuple(w0["Fp"]))
        print("  F  ~ t[%.6f,%.6f] x[%.6f,%.6f] y[%.6f,%.6f]" % tuple(w0["F_float"]))
        print("  F' ~ t[%.6f,%.6f] x[%.6f,%.6f] y[%.6f,%.6f]" % tuple(w0["Fp_float"]))
        print("  certain mass %s  required %s  U=%d  deficit %s (~%.6f)"
              % (w0["certain_mass"], w0["required"], w0["U"], w0["deficit"],
                 w0["deficit_float"]))
        cf = w0["confirm"]
        if cf:
            print("  CONFIRMED disjoint placement inside the witness box:")
            print("    Q1: t=%s c=(%s,%s)  [cos=%s sin=%s w=%s admissible=%s]"
                  % (cf["square1"]["t"], cf["square1"]["cx"], cf["square1"]["cy"],
                     cf["square1"]["cos"], cf["square1"]["sin"], cf["square1"]["w"],
                     cf["square1"]["admissible"]))
            print("    Q2: t=%s c=(%s,%s)  [cos=%s sin=%s w=%s admissible=%s]"
                  % (cf["square2"]["t"], cf["square2"]["cx"], cf["square2"]["cy"],
                     cf["square2"]["cos"], cf["square2"]["sin"], cf["square2"]["w"],
                     cf["square2"]["admissible"]))
            print("    SAT gap = %s (~%.9f) >= 0  =>  interiors disjoint"
                  % (cf["sat_gap"], cf["sat_gap_float"]))
        else:
            print("  (no concrete disjoint placement found in the witness box by the "
                  "corner/midpoint probe -- witness may be an interval-slop artefact)")

    if args.report:
        rp = os.path.splitext(args.cert)[0] + ".report.json"
        rep = dict(
            format="pair-certificate-v1",
            verifier=os.path.basename(__file__),
            verifier_sha256=sha256_of(os.path.abspath(__file__)),
            certificate=os.path.abspath(args.cert),
            settings=dict(depth=args.depth, split=args.split, tscale=str(tscale),
                          jobs=1, arithmetic="exact fractions.Fraction"),
            s=str(cert.s), n=cert.n, k=cert.k, m=cert.m, beta=str(cert.beta), N=cert.N,
            W2=str(cert.W2), W2_float=float(cert.W2),
            threshold=str(cert.threshold), threshold_float=float(cert.threshold),
            p1_prime_ok=True,
            counts=dict(vacuous=c["vacuous"], exempt_core=c["exempt_core"],
                        nondisjoint=c["nondisjoint"], covered=c["covered"],
                        split=c["split"], max_depth=c["max_depth"],
                        pairs_root=c["pairs_root"],
                        pairs_examined=c["pairs_examined"]),
            wall_seconds=elapsed,
            verdict="PASS" if ok else "FAIL",
            witnesses=run.witnesses,
        )
        with open(rp, "w") as fh:
            json.dump(rep, fh, indent=1, sort_keys=True)
        print("report          %s" % os.path.abspath(rp))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
