#!/usr/bin/env python
# -*- coding: ascii -*-
"""verify_pair2.py -- reference implementation of pair-certificate-v2.

Written FROM docs/specs/pair_certificate_v2.md by the A73 theory lead (Fable).
The decision path is exact (fractions.Fraction over cross-multiplied integers);
floats appear only as a fail-fast pre-screen (a float "no" skips work whose exact
confirmation could only fail; every discharge is exactly confirmed) and in the
selftest harness / witness rendering.

Exit codes: 0 PASS, 1 FAIL, 2 malformed / (P1') violated.

Non-normative extras (do not affect the verdict): --faildump N collects up to N
undischarged-leaf witnesses instead of stopping at the first.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as Fr

# exact sqrt(2)-related brackets (spec 3.1)
TSTAR_LO = Fr(408, 985)          # < tan(pi/8)
TSTAR_HI = Fr(5741, 13860)       # > tan(pi/8)
W_HI_GLOBAL = Fr(19601, 13860)   # > sqrt(2) exactly

HALF = Fr(1, 2)
ONE = Fr(1)


# ------------------------------------------------------------------ parsing
class Malformed(Exception):
    pass


def _reject_float(x):
    raise Malformed("JSON float literal rejected (all numbers must be rational strings)")


def rat(x, what="number"):
    if isinstance(x, str):
        try:
            return Fr(x)
        except (ValueError, ZeroDivisionError):
            raise Malformed("bad rational string %r for %s" % (x, what))
    if isinstance(x, int):
        return Fr(x)
    raise Malformed("expected rational string for %s, got %r" % (what, x))


class Cert(object):
    def __init__(self, path):
        with open(path, "r") as fh:
            try:
                doc = json.load(fh, parse_float=_reject_float,
                                parse_constant=_reject_float)
            except Malformed:
                raise
            except ValueError as e:
                raise Malformed("JSON parse error: %s" % e)
        if not isinstance(doc, dict):
            raise Malformed("top level must be an object")
        self.format = doc.get("format")
        if self.format not in ("pair-certificate-v1", "pair-certificate-v2"):
            raise Malformed("bad format %r" % (self.format,))
        self.s = rat(doc.get("s"), "s")
        if self.s <= 0:
            raise Malformed("s must be positive")
        self.n = int(doc.get("n", 11))
        self.k = int(doc.get("k", 0))
        self.m = int(doc.get("m", 0))
        self.beta = rat(doc.get("beta", "0"), "beta")
        if self.beta < 0:
            raise Malformed("beta must be >= 0")
        self.N = self.n - self.k
        cores = doc.get("cores", [])
        boxes = doc.get("boxes", [])
        if len(cores) != self.k:
            raise Malformed("k=%d but %d cores" % (self.k, len(cores)))
        if len(boxes) != self.m:
            raise Malformed("m=%d but %d boxes" % (self.m, len(boxes)))
        self.cores = [(rat(c["kx"], "kx"), rat(c["ky"], "ky"), rat(c["a"], "a"))
                      for c in cores]
        for _, _, a in self.cores:
            if a < 0:
                raise Malformed("core half-side < 0")
        self.boxes = [(rat(b["bx"], "bx"), rat(b["by"], "by"), rat(b["h"], "h"))
                      for b in boxes]
        atoms = doc.get("atoms", [])
        self.atoms = []
        self.warn_coincident = 0
        for a in atoms:
            px, py = rat(a["px"], "px"), rat(a["py"], "py")
            qx, qy = rat(a["qx"], "qx"), rat(a["qy"], "qy")
            w = rat(a["w"], "w")
            if w < 0:
                raise Malformed("atom weight < 0")
            if (px, py) == (qx, qy):
                self.warn_coincident += 1
            self.atoms.append((px, py, qx, qy, w))
        self.W2 = sum(a[4] for a in self.atoms) if self.atoms else Fr(0)
        if "total" in doc:
            if rat(doc["total"], "total") != self.W2:
                raise Malformed("total != sum of atom weights")
        self.threshold = Fr(self.N * (self.N - 1) // 2) + self.beta * self.m
        self.hints = doc.get("hints") or None

    def p1prime_ok(self):
        return self.W2 < self.threshold


# ------------------------------------------------------------------ Lemma Q
def q_nonneg(A, B, C, t0, t1):
    """Exact: A t^2 + B t + C >= 0 on [t0,t1] (Lemma Q)."""
    if A * t0 * t0 + B * t0 + C < 0:
        return False
    if A * t1 * t1 + B * t1 + C < 0:
        return False
    if A <= 0:
        return True
    if 2 * A * t0 + B >= 0:
        return True
    if 2 * A * t1 + B <= 0:
        return True
    return 4 * A * C - B * B >= 0


def q_min(A, B, C, t0, t1):
    """Exact minimum of the quadratic on [t0,t1]."""
    m = min(A * t0 * t0 + B * t0 + C, A * t1 * t1 + B * t1 + C)
    if A > 0:
        d0, d1 = 2 * A * t0 + B, 2 * A * t1 + B
        if d0 < 0 < d1:
            m = min(m, C - B * B / (4 * A))
    return m


def q_nonneg_f(A, B, C, t0, t1):
    """Float pre-screen mirror of q_nonneg (used only to fail fast)."""
    if A * t0 * t0 + B * t0 + C < 0.0:
        return False
    if A * t1 * t1 + B * t1 + C < 0.0:
        return False
    if A <= 0.0:
        return True
    if 2.0 * A * t0 + B >= 0.0:
        return True
    if 2.0 * A * t1 + B <= 0.0:
        return True
    return 4.0 * A * C - B * B >= 0.0


# ------------------------------------------------------------------ Lemma M
# membership slack quadratics for point p over factor F=(t0,t1,x0,x1,y0,y1):
#   list of (A, B, C) pinned at the worst corner, order g1..g4.
def mem_quads(px, py, F):
    t0, t1, x0, x1, y0, y1 = F
    out = []
    dx, dy = px - x0, py - y0            # g1 corner (x0,y0)
    out.append((HALF + dx, -2 * dy, HALF - dx))
    dx, dy = px - x1, py - y1            # g2 corner (x1,y1)
    out.append((HALF - dx, 2 * dy, HALF + dx))
    dx, dy = px - x1, py - y0            # g3 corner (x1,y0)
    out.append((HALF + dy, 2 * dx, HALF - dy))
    dx, dy = px - x0, py - y1            # g4 corner (x0,y1)
    out.append((HALF - dy, -2 * dx, HALF + dy))
    return out


def mem_certain(px, py, F):
    t0, t1 = F[0], F[1]
    for (A, B, C) in mem_quads(px, py, F):
        if not q_nonneg(A, B, C, t0, t1):
            return False
    return True


# unpinned affine form of membership constraint sigma in {0..3} for point p:
# slack(cx,cy,t) = K(t) + cx*X(t) + cy*Y(t), each a quadratic (A,B,C) in t.
def mem_affine(px, py, sigma):
    if sigma == 0:    # u <= 1/2: (1/2)(1+t^2) - (px-cx)(1-t^2) - 2t(py-cy)
        K = (HALF + px, -2 * py, HALF - px)
        X = (Fr(-1), Fr(0), ONE)         # cx * (1-t^2) -> t^2*(-1)+1 ... times +1
        Y = (Fr(0), Fr(2), Fr(0))        # cy * 2t
    elif sigma == 1:  # u >= -1/2: (1/2)(1+t^2) + (px-cx)(1-t^2) + 2t(py-cy)
        K = (HALF - px, 2 * py, HALF + px)
        X = (ONE, Fr(0), Fr(-1))
        Y = (Fr(0), Fr(-2), Fr(0))
    elif sigma == 2:  # v <= 1/2: (1/2)(1+t^2) + 2t(px-cx) - (py-cy)(1-t^2)
        K = (HALF + py, 2 * px, HALF - py)
        X = (Fr(0), Fr(-2), Fr(0))
        Y = (ONE, Fr(0), Fr(-1))
    else:             # v >= -1/2: (1/2)(1+t^2) - 2t(px-cx) + (py-cy)(1-t^2)
        K = (HALF - py, -2 * px, HALF + py)
        X = (Fr(0), Fr(2), Fr(0))
        Y = (Fr(-1), Fr(0), ONE)
    return K, X, Y


# ------------------------------------------------------------------ Lemma E
def exc_quads(core, F):
    """8 pinned slack quadratics E1+,E1-,E2+,E2-,E3+,E3-,E4+,E4- (spec 3.5)."""
    kx, ky, a = core
    t0, t1, x0, x1, y0, y1 = F
    out = []
    ex = x1 - kx    # E1+
    out.append((a - ex - HALF, ONE, a - ex + HALF))
    ex = x0 - kx    # E1-
    out.append((a + ex - HALF, ONE, a + ex + HALF))
    ey = y1 - ky    # E2+
    out.append((a - ey - HALF, ONE, a - ey + HALF))
    ey = y0 - ky    # E2-
    out.append((a + ey - HALF, ONE, a + ey + HALF))
    ex, ey = x1 - kx, y1 - ky   # E3+
    out.append((HALF - a + ex, 2 * a - 2 * ey, HALF + a - ex))
    ex, ey = x0 - kx, y0 - ky   # E3-
    out.append((HALF - a - ex, 2 * a + 2 * ey, HALF + a + ex))
    ex, ey = x0 - kx, y1 - ky   # E4+
    out.append((HALF - a + ey, 2 * a + 2 * ex, HALF + a - ey))
    ex, ey = x1 - kx, y0 - ky   # E4-
    out.append((HALF - a - ey, 2 * a - 2 * ex, HALF + a + ey))
    return out


def exc_certain(core, F):
    t0, t1 = F[0], F[1]
    for (A, B, C) in exc_quads(core, F):
        if not q_nonneg(A, B, C, t0, t1):
            return False
    return True


# unpinned affine form of exemption constraint sigma in {0..7} for core:
def exc_affine(core, sigma):
    kx, ky, a = core
    Z = (Fr(0), Fr(0), Fr(0))
    wq = (-HALF, ONE, HALF)  # (1 - t^2 + 2t)/2
    aw = (HALF - a, 2 * a, HALF + a)   # (1/2)(1+t^2) + a(1-t^2+2t)
    if sigma == 0:   # E1+: (a - (cx-kx))(1+t^2) + wq
        K = (a + kx - HALF, ONE, a + kx + HALF)
        X = (Fr(-1), Fr(0), Fr(-1))
        Y = Z
    elif sigma == 1:  # E1-: (a + (cx-kx))(1+t^2) + wq
        K = (a - kx - HALF, ONE, a - kx + HALF)
        X = (ONE, Fr(0), ONE)
        Y = Z
    elif sigma == 2:
        K = (a + ky - HALF, ONE, a + ky + HALF)
        X, Y = Z, (Fr(-1), Fr(0), Fr(-1))
    elif sigma == 3:
        K = (a - ky - HALF, ONE, a - ky + HALF)
        X, Y = Z, (ONE, Fr(0), ONE)
    elif sigma == 4:  # E3+: aw - (cx-kx)(1-t^2) - 2t(cy-ky)
        K = (aw[0] + kx, aw[1] + 2 * ky, aw[2] - kx)
        X = (ONE, Fr(0), Fr(-1))
        Y = (Fr(0), Fr(-2), Fr(0))
    elif sigma == 5:  # E3-: aw + (cx-kx)(1-t^2) + 2t(cy-ky)
        K = (aw[0] - kx, aw[1] - 2 * ky, aw[2] + kx)
        X = (Fr(-1), Fr(0), ONE)
        Y = (Fr(0), Fr(2), Fr(0))
    elif sigma == 6:  # E4+: aw + 2t(cx-kx) - (cy-ky)(1-t^2)
        K = (aw[0] + ky, aw[1] - 2 * kx, aw[2] - ky)
        X = (Fr(0), Fr(2), Fr(0))
        Y = (ONE, Fr(0), Fr(-1))
    else:             # E4-: aw - 2t(cx-kx) + (cy-ky)(1-t^2)
        K = (aw[0] - ky, aw[1] + 2 * kx, aw[2] + ky)
        X = (Fr(0), Fr(-2), Fr(0))
        Y = (Fr(-1), Fr(0), ONE)
    return K, X, Y


# --------------------------------------------------------- interval helpers
def imul(a, b):
    ps = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(ps), max(ps))


def iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def iabs(a):
    if a[0] >= 0:
        return a
    if a[1] <= 0:
        return (-a[1], -a[0])
    return (Fr(0), max(-a[0], a[1]))


def cs_intervals(t0, t1):
    """Exact enclosures of C=cos, S=sin over [t0,t1] (C decreasing, S increasing)."""
    d0, d1 = 1 + t0 * t0, 1 + t1 * t1
    C = ((1 - t1 * t1) / d1, (1 - t0 * t0) / d0)
    S = (2 * t0 / d0, 2 * t1 / d1)
    return C, S


def w_bounds(t0, t1):
    """(w_lo, w_hi) per spec 3.1: w_lo by quasiconcavity, w_hi with sqrt2 rule."""
    def w(t):
        d = 1 + t * t
        return (1 - t * t) / d + 2 * t / d
    w0, w1 = w(t0), w(t1)
    w_lo = min(w0, w1)
    if t1 <= TSTAR_LO or t0 >= TSTAR_HI:
        w_hi = max(w0, w1)
    else:
        w_hi = W_HI_GLOBAL
    return w_lo, w_hi


# ------------------------------------------------------------- NONDISJOINT
def nondisjoint_certain(FA, FB):
    """v1 3.3: every pair in the box has intersecting interiors."""
    dX = (FB[2] - FA[3], FB[3] - FA[2])
    dY = (FB[4] - FA[5], FB[5] - FA[4])
    # disk pre-test: sup ||dc||^2 < 1
    ax = iabs(dX)
    ay = iabs(dY)
    if ax[1] * ax[1] + ay[1] * ay[1] < 1:
        return True
    C1, S1 = cs_intervals(FA[0], FA[1])
    C2, S2 = cs_intervals(FB[0], FB[1])
    cc = iadd(imul(C1, C2), imul(S1, S2))
    ss = isub(imul(S1, C2), imul(C1, S2))
    g = iadd(iabs(cc), iabs(ss))
    g_lo = max(g[0], ONE)                       # floor at 1 (spec/v1)
    bound = HALF + g_lo / 2
    for (U, V) in ((C1, S1), ((-S1[1], -S1[0]), C1),
                   (C2, S2), ((-S2[1], -S2[0]), C2)):
        proj = iadd(imul(dX, U), imul(dY, V))
        if iabs(proj)[1] >= bound:
            return False
    return True


# ------------------------------------------------------------------ U bound
def possibly_meets(F, box, w_hi):
    """Negation of certain interior separation (v1 3.4)."""
    bx, by, h = box
    t0, t1, x0, x1, y0, y1 = F
    ex = (x0 - bx, x1 - bx)
    ey = (y0 - by, y1 - by)
    if iabs(ex)[0] >= h + w_hi / 2:
        return False
    if iabs(ey)[0] >= h + w_hi / 2:
        return False
    C, S = cs_intervals(t0, t1)
    pu = iadd(imul(ex, C), imul(ey, S))
    if iabs(pu)[0] >= HALF + h * w_hi:
        return False
    pv = iadd(imul(ex, ((-S[1], -S[0]))), imul(ey, C))
    if iabs(pv)[0] >= HALF + h * w_hi:
        return False
    return True


def u_bound(cert, FA, FB):
    if cert.beta == 0 or cert.m == 0:
        return 0
    _, whA = w_bounds(FA[0], FA[1])
    _, whB = w_bounds(FB[0], FB[1])
    U = 0
    for box in cert.boxes:
        if possibly_meets(FA, box, whA) and possibly_meets(FB, box, whB):
            U += 1
    return U


# --------------------------------------------------------------- clip/roots
def clip_factor(F, s):
    """VACUOUS admissibility clip (v1 3.1). Returns clipped factor or None."""
    t0, t1, x0, x1, y0, y1 = F
    w_lo, _ = w_bounds(t0, t1)
    lo, hi = w_lo / 2, s - w_lo / 2
    x0, x1 = max(x0, lo), min(x1, hi)
    y0, y1 = max(y0, lo), min(y1, hi)
    if x0 > x1 or y0 > y1 or lo > hi:
        return None
    return (t0, t1, x0, x1, y0, y1)


def roots(cert, split):
    s = cert.s
    lo, hi = HALF, s - HALF          # w_min = 1 on t in [0,1]
    ncell = 1 << split
    step = (hi - lo) / ncell
    factors = []
    for ix in range(ncell):
        for iy in range(ncell):
            F = (Fr(0), ONE,
                 lo + ix * step, lo + (ix + 1) * step,
                 lo + iy * step, lo + (iy + 1) * step)
            factors.append(F)
    pairs = []
    for i in range(len(factors)):
        for j in range(i, len(factors)):
            pairs.append((i, j))
    return factors, pairs


# ------------------------------------------------------ discharge machinery
class Stats(object):
    def __init__(self):
        self.examined = 0
        self.vacuous = 0
        self.exempt = 0
        self.nondisjoint = 0
        self.covered = 0
        self.covered_f = 0
        self.split = 0
        self.hint_misses = 0
        self.max_depth = 0
        self.definitive = 0


def float_factor(F):
    return tuple(float(v) for v in F)


def covered_try(cert, FA, FB, thr_num):
    """COVERED: returns (ok, certain_mass, certain_set)."""
    mass = Fr(0)
    certain = []
    fFA, fFB = float_factor(FA), float_factor(FB)
    for idx, (px, py, qx, qy, w) in enumerate(cert.atoms):
        if w == 0:
            continue
        got = None
        # float pre-screen then exact
        if _mem_f(float(px), float(py), fFA) and _mem_f(float(qx), float(qy), fFB):
            if mem_certain(px, py, FA) and mem_certain(qx, qy, FB):
                got = 0
        if got is None and _mem_f(float(qx), float(qy), fFA) and \
                _mem_f(float(px), float(py), fFB):
            if mem_certain(qx, qy, FA) and mem_certain(px, py, FB):
                got = 1
        if got is not None:
            mass += w
            certain.append((idx, got))
            if mass >= thr_num:
                return True, mass, certain
    return mass >= thr_num, mass, certain


def _mem_f(px, py, F):
    t0, t1, x0, x1, y0, y1 = F
    for (A, B, C) in (
            (0.5 + (px - x0), -2 * (py - y0), 0.5 - (px - x0)),
            (0.5 - (px - x1), 2 * (py - y1), 0.5 + (px - x1)),
            (0.5 + (py - y0), 2 * (px - x1), 0.5 - (py - y0)),
            (0.5 - (py - y1), -2 * (px - x0), 0.5 + (py - y1))):
        if not q_nonneg_f(A, B, C, t0, t1):
            return False
    return True


def _mem_slacks_f(px, py, F):
    """Float minima of the 4 pinned slacks (heuristics only)."""
    t0, t1, x0, x1, y0, y1 = F
    quads = ((0.5 + (px - x0), -2 * (py - y0), 0.5 - (px - x0)),
             (0.5 - (px - x1), 2 * (py - y1), 0.5 + (px - x1)),
             (0.5 + (py - y0), 2 * (px - x1), 0.5 - (py - y0)),
             (0.5 - (py - y1), -2 * (px - x0), 0.5 + (py - y1)))
    out = []
    for (A, B, C) in quads:
        m = min(A * t0 * t0 + B * t0 + C, A * t1 * t1 + B * t1 + C)
        if A > 0:
            d0, d1 = 2 * A * t0 + B, 2 * A * t1 + B
            if d0 < 0 < d1:
                m = min(m, C - B * B / (4 * A))
        out.append(m)
    return out


def pinned_from_affine(K, X, Y, xlo, xhi, ylo, yhi, corner):
    cx = xhi if corner & 1 else xlo
    cy = yhi if corner & 2 else ylo
    return tuple(K[i] + cx * X[i] + cy * Y[i] for i in range(3))


def sum_nonneg_joint(aff1, aff2, F):
    """Exact: min over F-box of (g1+g2) >= 0, both constraints on SAME factor."""
    t0, t1, x0, x1, y0, y1 = F
    K = tuple(aff1[0][i] + aff2[0][i] for i in range(3))
    X = tuple(aff1[1][i] + aff2[1][i] for i in range(3))
    Y = tuple(aff1[2][i] + aff2[2][i] for i in range(3))
    for corner in range(4):
        A, B, C = pinned_from_affine(K, X, Y, x0, x1, y0, y1, corner)
        if not q_nonneg(A, B, C, t0, t1):
            return False
    return True


def slack_min_exact(aff, F):
    """Exact min over F-box of a single affine-form constraint."""
    t0, t1, x0, x1, y0, y1 = F
    best = None
    for corner in range(4):
        A, B, C = pinned_from_affine(aff[0], aff[1], aff[2], x0, x1, y0, y1, corner)
        v = q_min(A, B, C, t0, t1)
        best = v if best is None else min(best, v)
    return best


def covered_f_try(cert, FA, FB, thr_num, base_mass, base_set):
    """COVERED-F greedy search (spec 3.6). Returns (ok, add_mass, used)."""
    need = thr_num - base_mass
    if need <= 0:
        return True, Fr(0), []
    fFA, fFB = float_factor(FA), float_factor(FB)
    base_idx = set(i for i, _ in base_set)
    # MEM candidates: failing set of size 1..MAXFAIL (spec 3.6 failing sets)
    MAXFAIL = 2
    cands = []
    for idx, (px, py, qx, qy, w) in enumerate(cert.atoms):
        if w == 0 or idx in base_idx:
            continue
        for o in (0, 1):
            e0 = (px, py) if o == 0 else (qx, qy)
            e1 = (qx, qy) if o == 0 else (px, py)
            sl0 = _mem_slacks_f(float(e0[0]), float(e0[1]), fFA)
            sl1 = _mem_slacks_f(float(e1[0]), float(e1[1]), fFB)
            failsf = [(0, s, i) for i, s in enumerate(sl0) if s < 0.0] + \
                     [(1, s, i) for i, s in enumerate(sl1) if s < 0.0]
            if not (1 <= len(failsf) <= MAXFAIL):
                continue
            if min(s for _, s, _ in failsf) < -0.6:
                continue
            # exact: verify the complementary (certain) constraints; build the
            # exact failing set (a float-fail may be exactly certain: re-check)
            fails = []
            certain = True
            for fac, F, pt in ((0, FA, e0), (1, FB, e1)):
                qs = mem_quads(pt[0], pt[1], F)
                flagged = set(i for (fc, _, i) in failsf if fc == fac)
                for i in range(4):
                    if q_nonneg(*qs[i], F[0], F[1]):
                        continue
                    if i in flagged:
                        fails.append((fac, i, mem_affine(pt[0], pt[1], i)))
                    else:
                        certain = False
                        break
                if not certain:
                    break
            if not certain or not fails:
                continue
            fsl = min(s for _, s, _ in failsf)
            cands.append({"idx": idx, "o": o, "fails": fails, "w": w,
                          "fsl": fsl})
    if not cands:
        return False, Fr(0), []
    # EXC candidates: core x factor with failing set of size 1..MAXFAIL+1
    excs = []
    for ci, core in enumerate(cert.cores):
        for fac, F in ((0, FA), (1, FB)):
            qs = exc_quads(core, F)
            t0, t1 = F[0], F[1]
            failed = [i for i in range(8) if not q_nonneg(*qs[i], t0, t1)]
            if 1 <= len(failed) <= MAXFAIL + 1:
                excs.append({"core": ci, "fac": fac,
                             "fails": [(fac, i, exc_affine(core, i))
                                       for i in failed]})

    def cross_ok(fails1, fails2):
        for (f1, s1, aff1) in fails1:
            for (f2, s2, aff2) in fails2:
                if f1 == f2:
                    if not sum_nonneg_joint(aff1, aff2, FA if f1 == 0 else FB):
                        return False
                else:
                    if (slack_min_exact(aff1, FA if f1 == 0 else FB) +
                            slack_min_exact(aff2, FA if f2 == 0 else FB)) < 0:
                        return False
        return True

    cands.sort(key=lambda c: -float(c["w"]))
    used_idx = set()
    add = Fr(0)
    used = []
    # MEM/EXC pairs first (full weight)
    for c in cands:
        if add >= need:
            break
        if c["idx"] in used_idx:
            continue
        for e in excs:
            if cross_ok(c["fails"], e["fails"]):
                add += c["w"]
                used_idx.add(c["idx"])
                used.append(("mex", c["idx"], c["o"],
                             [f[:2] for f in c["fails"]], e["core"], e["fac"],
                             [f[1] for f in e["fails"]]))
                break
    # MEM/MEM pairs
    ncand = len(cands)
    for i in range(ncand):
        if add >= need:
            break
        ci = cands[i]
        if ci["idx"] in used_idx:
            continue
        for j in range(i + 1, ncand):
            cj = cands[j]
            if cj["idx"] in used_idx or cj["idx"] == ci["idx"]:
                continue
            # cheap float gate: worst slacks must be roughly balanced
            if ci["fsl"] + cj["fsl"] < -0.25:
                continue
            if cross_ok(ci["fails"], cj["fails"]):
                add += min(ci["w"], cj["w"])
                used_idx.add(ci["idx"])
                used_idx.add(cj["idx"])
                used.append(("mm", ci["idx"], ci["o"],
                             [f[:2] for f in ci["fails"]],
                             cj["idx"], cj["o"],
                             [f[:2] for f in cj["fails"]]))
                break
    return add >= need, add, used


# ---------------------------------------------- exact point-wise machinery
def point_cs(t):
    d = 1 + t * t
    return (1 - t * t) / d, 2 * t / d


def point_in_square(px, py, cx, cy, t):
    C, S = point_cs(t)
    dx, dy = px - cx, py - cy
    u = C * dx + S * dy
    v = -S * dx + C * dy
    return -HALF <= u <= HALF and -HALF <= v <= HALF


def point_admissible(cx, cy, t, s):
    C, S = point_cs(t)
    h = (C + S) / 2
    return h <= cx <= s - h and h <= cy <= s - h


def point_core_overlap(core, cx, cy, t):
    """Exact closed SAT overlap of Q(c,theta(t)) with the axis core."""
    kx, ky, a = core
    C, S = point_cs(t)
    w = C + S
    ex, ey = cx - kx, cy - ky
    if abs(ex) > a + w / 2 or abs(ey) > a + w / 2:
        return False
    if abs(ex * C + ey * S) > HALF + a * w:
        return False
    if abs(-ex * S + ey * C) > HALF + a * w:
        return False
    return True


def pair_interior_disjoint(cxA, cyA, tA, cxB, cyB, tB):
    """Exact: int Q_A and int Q_B disjoint iff some axis weakly separates."""
    CA, SA = point_cs(tA)
    CB, SB = point_cs(tB)
    dx, dy = cxB - cxA, cyB - cyA
    cc = CA * CB + SA * SB
    ss = SA * CB - CA * SB
    bound = HALF + (abs(cc) + abs(ss)) / 2
    for (ux, uy) in ((CA, SA), (-SA, CA), (CB, SB), (-SB, CB)):
        if abs(dx * ux + dy * uy) >= bound:
            return True
    return False


def _factor_probe_points(F, s, cert, denom=8):
    """Candidate admissible core-free placements (exact rationals) in F."""
    t0, t1, x0, x1, y0, y1 = F
    pts = []
    fracs = (Fr(1, 2), Fr(1, 4), Fr(3, 4), Fr(1, 8), Fr(7, 8))
    for ft in fracs[:3]:
        t = t0 + (t1 - t0) * ft
        for fx in fracs[:3]:
            cx = x0 + (x1 - x0) * fx
            for fy in fracs[:3]:
                cy = y0 + (y1 - y0) * fy
                if not point_admissible(cx, cy, t, s):
                    continue
                if any(point_core_overlap(c, cx, cy, t) for c in cert.cores):
                    continue
                pts.append((cx, cy, t))
                if len(pts) >= 6:
                    return pts
    return pts


def collected_at(cert, plA, plB):
    """Exact collected mass and m2 at a concrete placement pair."""
    mass = Fr(0)
    for (px, py, qx, qy, w) in cert.atoms:
        if w == 0:
            continue
        if (point_in_square(px, py, plA[0], plA[1], plA[2]) and
                point_in_square(qx, qy, plB[0], plB[1], plB[2])):
            mass += w
            continue
        if (point_in_square(qx, qy, plA[0], plA[1], plA[2]) and
                point_in_square(px, py, plB[0], plB[1], plB[2])):
            mass += w
    m2 = 0
    if cert.beta > 0 and cert.m:
        for (bx, by, h) in cert.boxes:
            # strict interior overlap of Q with axis box: SAT with strict ineqs
            if (_int_overlap_box(plA, bx, by, h) and
                    _int_overlap_box(plB, bx, by, h)):
                m2 += 1
    return mass, m2


def _int_overlap_box(pl, bx, by, h):
    cx, cy, t = pl
    C, S = point_cs(t)
    w = C + S
    ex, ey = cx - bx, cy - by
    if abs(ex) >= h + w / 2 or abs(ey) >= h + w / 2:
        return False
    if abs(ex * C + ey * S) >= HALF + h * w:
        return False
    if abs(-ex * S + ey * C) >= HALF + h * w:
        return False
    return True


def probe_deficient(cert, FA, FB):
    """Try to exhibit an exact admissible core-free interior-disjoint pair in the
    box whose collected mass is < 1 + beta*m2: a concrete (P2') counterexample."""
    ptsA = _factor_probe_points(FA, cert.s, cert)
    ptsB = _factor_probe_points(FB, cert.s, cert)
    for plA in ptsA:
        for plB in ptsB:
            if not pair_interior_disjoint(plA[0], plA[1], plA[2],
                                          plB[0], plB[1], plB[2]):
                continue
            mass, m2 = collected_at(cert, plA, plB)
            thr = 1 + cert.beta * m2
            if mass < thr:
                return {"kind": "definitive",
                        "plA": [str(v) for v in plA],
                        "plB": [str(v) for v in plB],
                        "collected": str(mass), "m2": m2,
                        "deficit": str(thr - mass)}
    return None


def q_max_f(A, B, C, t0, t1):
    m = max(A * t0 * t0 + B * t0 + C, A * t1 * t1 + B * t1 + C)
    if A < 0:
        d0, d1 = 2 * A * t0 + B, 2 * A * t1 + B
        if d0 > 0 > d1:
            m = max(m, C - B * B / (4 * A))
    return m


def possible_mem_f(px, py, F):
    """Float necessary condition for 'p in Q for SOME placement in F':
    each constraint's max over the box >= 0 (pin at the opposite corner)."""
    t0, t1, x0, x1, y0, y1 = F
    quads = ((0.5 + (px - x1), -2 * (py - y1), 0.5 - (px - x1)),
             (0.5 - (px - x0), 2 * (py - y0), 0.5 + (px - x0)),
             (0.5 + (py - y1), 2 * (px - x0), 0.5 - (py - y1)),
             (0.5 - (py - y0), -2 * (px - x1), 0.5 + (py - y0)))
    for (A, B, C) in quads:
        if q_max_f(A, B, C, t0, t1) < -1e-12:
            return False
    return True


def possible_mass_f(cert, FA, FB):
    fFA, fFB = float_factor(FA), float_factor(FB)
    tot = 0.0
    for (px, py, qx, qy, w) in cert.atoms:
        if w == 0:
            continue
        fp = (float(px), float(py))
        fq = (float(qx), float(qy))
        if (possible_mem_f(fp[0], fp[1], fFA) and
                possible_mem_f(fq[0], fq[1], fFB)) or \
           (possible_mem_f(fq[0], fq[1], fFA) and
                possible_mem_f(fp[0], fp[1], fFB)):
            tot += float(w)
    return tot


# ------------------------------------------------------------ split choice
def choose_split(cert, FA, FB, tscale):
    """Margin-aware: aim at the best JOINTLY-reachable atom's worst constraint.
    Candidates must be possibly collectable in BOTH factors (else splitting
    toward them can never reach COVERED)."""
    fFA, fFB = float_factor(FA), float_factor(FB)
    best = None   # (score, fac, dim)
    for (px, py, qx, qy, w) in cert.atoms:
        if w == 0:
            continue
        fp = (float(px), float(py))
        fq = (float(qx), float(qy))
        for o in (0, 1):
            e0 = fp if o == 0 else fq
            e1 = fq if o == 0 else fp
            if not (possible_mem_f(e0[0], e0[1], fFA) and
                    possible_mem_f(e1[0], e1[1], fFB)):
                continue
            sl0 = _mem_slacks_f(e0[0], e0[1], fFA)
            sl1 = _mem_slacks_f(e1[0], e1[1], fFB)
            worst = min(min(sl0), min(sl1))
            if worst >= 0.0:
                continue          # certain already (or numerically so)
            shrink = -sum(s for s in sl0 + sl1 if s < 0.0)
            score = float(w) / (1e-6 + shrink)
            if best is None or score > best[0]:
                fac = 0 if min(sl0) <= min(sl1) else 1
                sl = sl0 if fac == 0 else sl1
                sigma = min(range(4), key=lambda i: sl[i])
                pt = e0 if fac == 0 else e1
                F = fFA if fac == 0 else fFB
                tm = 0.5 * (F[0] + F[1])
                # impact of each dim on constraint sigma
                cxc = abs(1.0 - tm * tm)
                cyc = abs(2.0 * tm)
                if sigma >= 2:
                    cxc, cyc = cyc, cxc
                A, B, _ = _mem_quad_f(pt, F, sigma)
                dt = abs(2.0 * A * tm + B)
                imp = [(dt * (F[1] - F[0]) * tscale, 0),
                       (cxc * (F[3] - F[2]), 1),
                       (cyc * (F[5] - F[4]), 2)]
                imp.sort(reverse=True)
                best = (score, fac, imp[0][1])
    if best is not None:
        return best[1], best[2]
    return widest_split(FA, FB, tscale)


def widest_split(FA, FB, tscale):
    cand = []
    for fac, F in ((0, float_factor(FA)), (1, float_factor(FB))):
        cand.append(((F[1] - F[0]) * tscale, fac, 0))
        cand.append((F[3] - F[2], fac, 1))
        cand.append((F[5] - F[4], fac, 2))
    cand.sort(reverse=True)
    return cand[0][1], cand[0][2]


def _mem_quad_f(pt, F, sigma):
    px, py = float(pt[0]), float(pt[1])
    x0, x1, y0, y1 = F[2], F[3], F[4], F[5]
    if sigma == 0:
        dx, dy = px - x0, py - y0
        return 0.5 + dx, -2 * dy, 0.5 - dx
    if sigma == 1:
        dx, dy = px - x1, py - y1
        return 0.5 - dx, 2 * dy, 0.5 + dx
    if sigma == 2:
        dx, dy = px - x1, py - y0
        return 0.5 + dy, 2 * dx, 0.5 - dy
    dx, dy = px - x0, py - y1
    return 0.5 - dy, -2 * dx, 0.5 + dy


def split_box(FA, FB, fac, dim, at=None):
    F = FA if fac == 0 else FB
    base = {0: (0, 1), 1: (2, 3), 2: (4, 5)}[dim]
    lo, hi = F[base[0]], F[base[1]]
    cut = at if at is not None else (lo + hi) / 2
    if not (lo < cut < hi):
        return None
    Fl = list(F)
    Fh = list(F)
    Fl[base[1]] = cut
    Fh[base[0]] = cut
    Fl, Fh = tuple(Fl), tuple(Fh)
    if fac == 0:
        return (Fl, FB), (Fh, FB)
    return (FA, Fl), (FA, Fh)


# ------------------------------------------------------------------- B&B
def contain_vacuous(F, s):
    """VACUOUS-CONTAIN (spec 3.3 1b): every placement of F violates containment
    on one side. Exact endpoint tests (positive leading coefficient)."""
    t0, t1, x0, x1, y0, y1 = F
    def side(v):     # slack pinned at its maximizer v: (v+1/2)t^2 - t + (v-1/2) < 0
        A, C = v + HALF, v - HALF
        return (A * t0 * t0 - t0 + C < 0) and (A * t1 * t1 - t1 + C < 0)
    return side(x1) or side(s - x0) or side(y1) or side(s - y0)


def discharge(cert, FA, FB, stats, use_cf=True):
    """Try all clauses; return clause name or None."""
    for F in (FA, FB):
        if contain_vacuous(F, cert.s):
            stats.vacuous += 1
            return "VACUOUS_CONTAIN"
    for fac, F in ((0, FA), (1, FB)):
        for core in cert.cores:
            # float pre-screen
            if _exc_f(core, float_factor(F)):
                if exc_certain(core, F):
                    stats.exempt += 1
                    return "EXEMPT"
    if nondisjoint_certain(FA, FB):
        stats.nondisjoint += 1
        return "NONDISJOINT"
    U = u_bound(cert, FA, FB)
    thr = 1 + cert.beta * U
    ok, mass, certain = covered_try(cert, FA, FB, thr)
    if ok:
        stats.covered += 1
        return "COVERED"
    if use_cf:
        okf, _, _ = covered_f_try(cert, FA, FB, thr, mass, certain)
        if okf:
            stats.covered_f += 1
            return "COVERED_F"
    return None


def _exc_f(core, F):
    kx, ky, a = float(core[0]), float(core[1]), float(core[2])
    t0, t1, x0, x1, y0, y1 = F
    quads = ((a - (x1 - kx) - 0.5, 1.0, a - (x1 - kx) + 0.5),
             (a + (x0 - kx) - 0.5, 1.0, a + (x0 - kx) + 0.5),
             (a - (y1 - ky) - 0.5, 1.0, a - (y1 - ky) + 0.5),
             (a + (y0 - ky) - 0.5, 1.0, a + (y0 - ky) + 0.5),
             (0.5 - a + (x1 - kx), 2 * a - 2 * (y1 - ky), 0.5 + a - (x1 - kx)),
             (0.5 - a - (x0 - kx), 2 * a + 2 * (y0 - ky), 0.5 + a + (x0 - kx)),
             (0.5 - a + (y1 - ky), 2 * a + 2 * (x0 - kx), 0.5 + a - (y1 - ky)),
             (0.5 - a - (y0 - ky), 2 * a - 2 * (x1 - kx), 0.5 + a + (y0 - ky)))
    for (A, B, C) in quads:
        if not q_nonneg_f(A, B, C, t0, t1):
            return False
    return True


def witness(cert, FA, FB, depth):
    U = u_bound(cert, FA, FB)
    thr = 1 + cert.beta * U
    _, mass, _ = covered_try(cert, FA, FB, thr)
    return {"depth": depth,
            "FA": [str(v) for v in FA], "FB": [str(v) for v in FB],
            "U": U, "certain_mass": str(mass),
            "deficit": str(thr - mass)}


def run_bnb(cert, args, stats):
    factors, pairs = roots(cert, args.split)
    clipped = []
    for F in factors:
        clipped.append(clip_factor(F, cert.s))
    stack = []
    only = None
    if getattr(args, "only_root", None):
        a, b = args.only_root.split(",")
        only = (int(a), int(b))
    for (i, j) in pairs:
        if only is not None and (i, j) != only:
            continue
        FA, FB = clipped[i], clipped[j]
        if FA is None or FB is None:
            stats.vacuous += 1
            continue
        tree = None
        if cert.hints and "trees" in cert.hints:
            tree = cert.hints["trees"].get("%d,%d" % (i, j))
        stack.append((FA, FB, 0, tree))
    stats.roots = len(stack)
    failures = []
    t_start = time.time()
    while stack:
        FA, FB, depth, tree = stack.pop()
        stats.examined += 1
        stats.max_depth = max(stats.max_depth, depth)
        if args.nodes and stats.examined > args.nodes:
            failures.append(witness(cert, FA, FB, depth))
            break
        if tree is not None and "cut" in tree:
            cut = tree["cut"]
            try:
                at = rat(cut["at"], "hint cut")
                res = split_box(FA, FB, int(cut["f"]),
                                {"t": 0, "x": 1, "y": 2}[cut["d"]], at)
            except (Malformed, KeyError):
                res = None
            if res is None:
                stats.hint_misses += 1
                tree = None
            else:
                stats.split += 1
                for (child, sub) in zip(res, (tree.get("lo"), tree.get("hi"))):
                    A0c = clip_factor(child[0], cert.s)
                    B0c = clip_factor(child[1], cert.s)
                    if A0c is None or B0c is None:
                        stats.vacuous += 1
                        continue
                    stack.append((A0c, B0c, depth + 1, sub))
                continue
        cl = discharge(cert, FA, FB, stats, use_cf=not args.no_cf)
        if cl is not None:
            continue
        # DEFICIENT-EARLY: if even the possible mass cannot reach threshold,
        # try to exhibit an exact counterexample row (kind "definitive").
        pm = possible_mass_f(cert, FA, FB)
        thr_f = 1.0 + float(cert.beta) * (u_bound(cert, FA, FB) if cert.beta else 0)
        deficient = pm < thr_f - 1e-9
        if deficient:
            wit = probe_deficient(cert, FA, FB)
            if wit is not None:
                wit.update(witness(cert, FA, FB, depth))
                failures.append(wit)
                stats.definitive += 1
                if not args.survey and len(failures) >= max(1, args.faildump):
                    break
                continue
        if depth >= args.depth:
            w = witness(cert, FA, FB, depth)
            w["kind"] = "cap"
            failures.append(w)
            if not args.survey and len(failures) >= max(1, args.faildump):
                break
            continue
        if len(failures) >= max(1, args.faildump):
            break
        if deficient:
            fac, dim = widest_split(FA, FB, args.tscale)
        else:
            fac, dim = choose_split(cert, FA, FB, args.tscale)
        res = split_box(FA, FB, fac, dim)
        if res is None:
            failures.append(witness(cert, FA, FB, depth))
            break
        stats.split += 1
        for (A0, B0) in res:
            A0c = clip_factor(A0, cert.s)
            B0c = clip_factor(B0, cert.s)
            if A0c is None or B0c is None:
                stats.vacuous += 1
                continue
            stack.append((A0c, B0c, depth + 1, None))
        if args.progress and stats.examined % args.progress == 0:
            el = time.time() - t_start
            sys.stderr.write("[%8.1fs] examined=%d stack=%d fails=%d\n"
                             % (el, stats.examined, len(stack), len(failures)))
    return failures


# ---------------------------------------------------------------- selftest
def _sample_uv(px, py, t, cx, cy):
    th = 2.0 * math.atan(t)
    C, S = math.cos(th), math.sin(th)
    dx, dy = px - cx, py - cy
    return C * dx + S * dy, -S * dx + C * dy


def selftest(seed=73, draws=2500):
    rng = random.Random(seed)
    bad = 0
    # Lemma Q fuzz
    for _ in range(draws):
        A = Fr(rng.randint(-50, 50), rng.randint(1, 20))
        B = Fr(rng.randint(-50, 50), rng.randint(1, 20))
        C = Fr(rng.randint(-50, 50), rng.randint(1, 20))
        t0 = Fr(rng.randint(0, 900), 1000)
        t1 = t0 + Fr(rng.randint(1, 1000 - int(t0 * 1000)), 1000)
        pred = q_nonneg(A, B, C, t0, t1)
        fA, fB, fC = float(A), float(B), float(C)
        ft0, ft1 = float(t0), float(t1)
        mn = min(fA * t * t + fB * t + fC
                 for t in [ft0 + (ft1 - ft0) * k / 60.0 for k in range(61)])
        if pred and mn < -1e-7:
            bad += 1
        if not pred and mn > 1e-7:
            bad += 1
    # Lemma M fuzz
    for _ in range(draws):
        t0 = Fr(rng.randint(0, 900), 1000)
        t1 = t0 + Fr(rng.randint(1, min(200, 1000 - int(t0 * 1000))), 1000)
        x0 = Fr(rng.randint(0, 3000), 1000)
        x1 = x0 + Fr(rng.randint(1, 300), 1000)
        y0 = Fr(rng.randint(0, 3000), 1000)
        y1 = y0 + Fr(rng.randint(1, 300), 1000)
        F = (t0, t1, x0, x1, y0, y1)
        px = Fr(rng.randint(-500, 3500), 1000)
        py = Fr(rng.randint(-500, 3500), 1000)
        pred = mem_certain(px, py, F)
        viol = False
        for _ in range(40):
            t = float(t0) + rng.random() * float(t1 - t0)
            cx = float(x0) + rng.random() * float(x1 - x0)
            cy = float(y0) + rng.random() * float(y1 - y0)
            u, v = _sample_uv(float(px), float(py), t, cx, cy)
            if abs(u) > 0.5 + 1e-9 or abs(v) > 0.5 + 1e-9:
                viol = True
        if pred and viol:
            bad += 1
    # Lemma E fuzz
    for _ in range(draws):
        t0 = Fr(rng.randint(0, 900), 1000)
        t1 = t0 + Fr(rng.randint(1, min(200, 1000 - int(t0 * 1000))), 1000)
        x0 = Fr(rng.randint(0, 3000), 1000)
        x1 = x0 + Fr(rng.randint(1, 300), 1000)
        y0 = Fr(rng.randint(0, 3000), 1000)
        y1 = y0 + Fr(rng.randint(1, 300), 1000)
        F = (t0, t1, x0, x1, y0, y1)
        core = (Fr(rng.randint(0, 3000), 1000), Fr(rng.randint(0, 3000), 1000),
                Fr(rng.randint(100, 700), 1000))
        pred = exc_certain(core, F)
        if pred:
            for _ in range(40):
                t = float(t0) + rng.random() * float(t1 - t0)
                cx = float(x0) + rng.random() * float(x1 - x0)
                cy = float(y0) + rng.random() * float(y1 - y0)
                if not _sat_overlap_f(core, t, cx, cy):
                    bad += 1
                    break
    # NONDISJOINT fuzz
    for _ in range(draws):
        FA = _rand_factor(rng)
        FB = _rand_factor(rng)
        if nondisjoint_certain(FA, FB):
            for _ in range(40):
                pa = _rand_place(rng, FA)
                pb = _rand_place(rng, FB)
                if _sat_gap_f(pa, pb) >= 0.0:
                    bad += 1
                    break
    return bad


def _rand_factor(rng):
    t0 = Fr(rng.randint(0, 900), 1000)
    t1 = t0 + Fr(rng.randint(1, min(300, 1000 - int(t0 * 1000))), 1000)
    x0 = Fr(rng.randint(0, 3000), 1000)
    x1 = x0 + Fr(rng.randint(1, 400), 1000)
    y0 = Fr(rng.randint(0, 3000), 1000)
    y1 = y0 + Fr(rng.randint(1, 400), 1000)
    return (t0, t1, x0, x1, y0, y1)


def _rand_place(rng, F):
    return (float(F[0]) + rng.random() * float(F[1] - F[0]),
            float(F[2]) + rng.random() * float(F[3] - F[2]),
            float(F[4]) + rng.random() * float(F[5] - F[4]))


def _sat_overlap_f(core, t, cx, cy):
    """Float SAT: does Q(c,theta(t)) meet the axis core? (closed overlap)"""
    kx, ky, a = float(core[0]), float(core[1]), float(core[2])
    th = 2.0 * math.atan(t)
    C, S = math.cos(th), math.sin(th)
    w = abs(C) + abs(S)
    ex, ey = cx - kx, cy - ky
    if abs(ex) > a + w / 2 + 1e-12 or abs(ey) > a + w / 2 + 1e-12:
        return False
    if abs(ex * C + ey * S) > 0.5 + a * w + 1e-12:
        return False
    if abs(-ex * S + ey * C) > 0.5 + a * w + 1e-12:
        return False
    return True


def _sat_gap_f(pa, pb):
    """max over 4 axes of |proj| - halfwidth-sum; >= 0 means separated."""
    ta, xa, ya = pa
    tb, xb, yb = pb
    tha, thb = 2.0 * math.atan(ta), 2.0 * math.atan(tb)
    dx, dy = xb - xa, yb - ya
    g = abs(math.cos(tha - thb)) + abs(math.sin(tha - thb))
    bound = 0.5 + g / 2
    best = -1e18
    for th in (tha, tha + math.pi / 2, thb, thb + math.pi / 2):
        proj = abs(dx * math.cos(th) + dy * math.sin(th))
        best = max(best, proj - bound)
    return best


# --------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cert", nargs="?")
    ap.add_argument("--depth", type=int, default=60)
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--nodes", type=int, default=0)
    ap.add_argument("--tscale", type=float, default=2.0)
    ap.add_argument("--report", default=None)
    ap.add_argument("--faildump", type=int, default=1)
    ap.add_argument("--progress", type=int, default=0)
    ap.add_argument("--no-cf", action="store_true", dest="no_cf")
    ap.add_argument("--survey", action="store_true")
    ap.add_argument("--only-root", dest="only_root", default=None,
                    help="restrict to one root pair 'i,j' (cost-law measurement; "
                         "verdict then covers only that root)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        bad = selftest()
        print("selftest violations: %d" % bad)
        return 0 if bad == 0 else 2

    if not args.cert:
        print("no certificate given")
        return 2
    t0 = time.time()
    try:
        cert = Cert(args.cert)
    except Malformed as e:
        print("MALFORMED: %s" % e)
        return 2
    if cert.warn_coincident:
        sys.stderr.write("WARNING: %d coincident atoms (uncollectable weight)\n"
                         % cert.warn_coincident)
    if not cert.p1prime_ok():
        print("P1' VIOLATED: W2 = %s >= threshold %s" % (cert.W2, cert.threshold))
        return 2
    stats = Stats()
    failures = run_bnb(cert, args, stats)
    wall = time.time() - t0
    verdict = "PASS" if not failures else "FAIL"
    print("VERDICT %s  W2=%s < %s  examined=%d vac=%d ex=%d nd=%d cov=%d cf=%d "
          "split=%d maxd=%d misses=%d  %.1fs (%.0f nodes/s)"
          % (verdict, cert.W2, cert.threshold, stats.examined, stats.vacuous,
             stats.exempt, stats.nondisjoint, stats.covered, stats.covered_f,
             stats.split, stats.max_depth, stats.hint_misses, wall,
             stats.examined / max(wall, 1e-9)))
    if args.report:
        src = open(os.path.abspath(__file__), "rb").read()
        rep = {"format_seen": cert.format,
               "verdict": verdict,
               "settings": {"depth": args.depth, "split": args.split,
                            "nodes": args.nodes, "jobs": 1,
                            "arithmetic": "python-Fraction exact "
                                          "(float fail-fast pre-screen)",
                            "hinted": bool(cert.hints)},
               "counts": {"pairs_root": getattr(stats, "roots", 0),
                          "pairs_examined": stats.examined,
                          "vacuous": stats.vacuous, "exempt_core": stats.exempt,
                          "nondisjoint": stats.nondisjoint,
                          "covered": stats.covered,
                          "covered_f": stats.covered_f, "split": stats.split,
                          "hint_misses": stats.hint_misses,
                          "definitive": stats.definitive,
                          "max_depth": stats.max_depth},
               "W2": str(cert.W2), "threshold": str(cert.threshold),
               "wall_s": wall,
               "failures": failures,
               "verifier_sha256": hashlib.sha256(src).hexdigest()}
        with open(args.report, "w") as fh:
            json.dump(rep, fh, indent=1, sort_keys=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
