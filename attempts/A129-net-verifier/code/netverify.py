#!/usr/bin/env python3
"""
netverify.py -- A129.  An ALTERNATIVE continuum verifier for the lab's MEASURE certificates
(`measure-certificate-v1` and `case-measure-certificate-v1`), built on a finite NET OF
ORIENTATIONS + SHRUNK SQUARES + an exact TRANSLATION SWEEP, in the style of the
Burns-Massaccesi n=17 certificate (Aug 2026).  It NEVER touches the frozen verifiers; it is a
second, structurally different decision procedure for exactly the same claim.

WHAT IS VERIFIED (identical to attempts/A57-shadow-trees/code/verify_case.py)
    Given atoms p_i with weights w_i >= 0 in [0,s]^2, hypotheses (cores K_j, NO-families F_j) and
    budget b:
        (C)  mu(Q) >= 1 for EVERY closed unit square Q contained in [0,s]^2 that is not exempt,
             where Q is exempt iff Q meets some core K_j, or Q's centre/tilt lies in some NO-family.
    (plus  sum_i w_i < b, checked directly).

HOW (the difference from the frozen verifier: no 3-D (t,cx,cy) branch and bound)
    Fix a finite NET of orientations.  Write t = tan(theta/2) in [0,1] (theta in [0,pi/2] suffices
    because Q(c,theta) = Q(c,theta+pi/2)).  Partition [0,1] into K cells [t_j, t_{j+1}]; in cell j
    put the net orientation t_k = (t_j + t_{j+1})/2 and let

        m_j = max over the cell of |tan((theta - theta_k)/2)|,  computed exactly by the tangent
              subtraction formula  tan((theta-theta_k)/2) = (t - t_k)/(1 + t*t_k),
        B_j = (1 + m_j^2) / (1 + 2 m_j - m_j^2)                                     (SIGMA LEMMA)

    B_j is exactly 1/(cos delta + sin delta) with delta = the cell's angular half-width -- the
    lab's sigma(delta).  LEMMA (proved in notes/method.md):  every unit square Q with tilt in cell
    j contains the CONCENTRIC square S of side B_j at the net orientation theta_k.

    Consequently (C) follows from the finitely many FIXED-ORIENTATION claims

        (N_j)  mu(S) >= 1 for every square S of side B_j at orientation theta_k whose centre lies
               in P_j (the union over the cell of the admissible centre regions) and which is not
               provably exempt.

    Each (N_j) is decided EXACTLY by a 2-D translation sweep.  In the rotated frame
    u = cos*x + sin*y, v = -sin*x + cos*y the mass of S with centre (U,V) is
        M(U,V) = sum_i w_i * [ |u_i - U| <= B/2 ] * [ |v_i - V| <= B/2 ],
    a sum of indicators of axis-aligned closed boxes.  M is piecewise constant on the grid cut by
    the 2N event coordinates u_i +- B/2 (and likewise in v); the minimum of M over any set is
    attained in the interior of a grid cell (M is upper semicontinuous: on a cell boundary every
    summand is >= its value on either side).  So the sweep = a 2-D difference array + two cumulative
    sums, giving the EXACT minimum over every grid cell, in integer arithmetic.

    A grid cell is DISCHARGED if
      (a) its mass reaches NEED = ceil((1+margin) * WD), or
      (b) it does not meet the interior of P_j (no unit square of the cell fits there), or
      (c) it is PROVABLY exempt: all four of its corners lie in the octagon
          {p : S(p) meets core K_j} for one core (that octagon is convex -- an intersection of four
          separating-axis slabs -- so four corners suffice), or all four corners lie in a NO-family
          box whose t-interval contains the whole net cell.
    An undischarged cell is a WITNESS: an explicit fixed orientation and an explicit rectangle of
    centres at which the shrunk square is provably light.

SOUNDNESS OF THE EXEMPTIONS (the only subtle point; see notes/method.md)
    S is CONCENTRIC WITH AND CONTAINED IN every unit square Q of the cell at the same centre.
    Hence  S meets K  =>  Q meets K  =>  Q is exempt.  So skipping cells on which S provably meets a
    core skips only squares Q that the claim exempts anyway.  (The converse fails: Q may meet a core
    while S does not.  That is the price of the shrink and is exactly what the benchmark measures.)

EXACTNESS
    Every geometric decision is over Python Fractions or int64 (weights on a common denominator);
    no floating point enters any accept/reject.  numpy is used only for the integer difference array
    and cumulative sums (int64, exact) and may be disabled with --no-numpy.

USAGE
    python netverify.py cert.json --level L            # K = 2^L net cells
    python netverify.py cert.json --search 0 20        # smallest L in [0,20] that PASSes
    python netverify.py cert.json --level L --emit out.json     # write a net certificate
    exit 0 = PASS, 1 = FAIL, 2 = malformed.
"""
import sys
import os
import json
import time
import math
import argparse
from fractions import Fraction as F

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None

ZERO = F(0)
ONE = F(1)
HALF = F(1, 2)


# ============================================================================ exact primitives
def cos_sin_t(t):
    """cos theta, sin theta for t = tan(theta/2) (exact rationals)."""
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


def sigma_of_cell(t0, t1, tk):
    """(m, B): m = max |tan((theta-theta_k)/2)| over the cell, B = sigma(delta) = 1/(cos d + sin d).

    tan((theta - theta_k)/2) = (t - t_k)/(1 + t t_k) is increasing in t, so the extremes are at the
    cell endpoints.  g(U) = (1 - U^2 + 2U)/(1 + U^2) = cos(eps) + sin|eps| with U = |tan(eps/2)|;
    g is strictly increasing on [0, sqrt2 - 1), so the binding U is m = max(|u0|, |u1|)."""
    u0 = (t0 - tk) / (1 + t0 * tk)
    u1 = (t1 - tk) / (1 + t1 * tk)
    m = max(abs(u0), abs(u1))
    den = 1 + 2 * m - m * m
    if den <= 0 or m >= F(41421, 100000):      # m must stay below sqrt(2)-1 for the monotonicity
        raise ValueError(f"net cell too wide for the sigma lemma (m = {float(m)})")
    return m, (1 + m * m) / den


def half_width(t):
    """h(theta) = (cos theta + sin theta)/2: half the side of the bounding box of a unit square."""
    c, s = cos_sin_t(t)
    return (c + s) / 2


def imul4(a0, a1, b0, b1):
    p = (a0 * b0, a0 * b1, a1 * b0, a1 * b1)
    return min(p), max(p)


def g_inf_over_cell(core, t0, t1):
    """A LOWER bound, valid for every theta in the t-cell, of
    g(theta) = |cos(theta - theta_m)| + |sin(theta - theta_m)|.
    Verbatim the rule of verify_case.core_exempt_frac, so the net verifier's exemption clause is
    exactly the frozen verifier's -- the shrink is applied to the MASS only, never to the
    exemption (see notes/method.md, Lemma N3)."""
    C1_, S0 = cos_sin_t(t0)        # cos is decreasing, sin increasing in t: hi cos, lo sin
    C0, S1 = cos_sin_t(t1)         # lo cos, hi sin
    cm, sm = core.cm, core.sm
    Alo = C0 * cm + S0 * sm
    if Alo < 0:
        Alo = ZERO
    Blo = -S1 * cm + C0 * sm
    Bhi = -S0 * cm + C1_ * sm
    Babs = ZERO if (Blo <= 0 <= Bhi) else min(abs(Blo), abs(Bhi))
    return (C0, C1_, S0, S1), Alo + Babs


def core_exempt_point_float(core, ftrig, fg, x, y, slack=1e-9):
    """Float PRE-FILTER for core_exempt_point.  False => certainly not exempt (the float value
    exceeds the limit by more than the slack, so the exact value exceeds it too); True => the exact
    test must still be run.  No accept decision is ever made here."""
    C0, C1_, S0, S1 = ftrig
    dx, dy = x - core.fkx, y - core.fky
    lim_e = core.fa + fg / 2 + slack
    if abs(dx * core.fcm + dy * core.fsm) > lim_e:
        return False
    if abs(-dx * core.fsm + dy * core.fcm) > lim_e:
        return False
    lim_f = 0.5 + core.fa * fg + slack
    a0, a1 = imul4(C0, C1_, dx, dx)
    b0, b1 = imul4(S0, S1, dy, dy)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1, -S0, dx, dx)
    b0, b1 = imul4(C0, C1_, dy, dy)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


def core_exempt_point(core, trig, g, x, y):
    """True iff the closed UNIT square Q(p, theta) meets the core for EVERY theta in the cell whose
    (trig, g) were passed.  Same predicate as verify_case.core_exempt_frac on the degenerate box
    {(t0,t1)} x {x} x {y}.  Convex in (x,y): a max of linear functions on each side."""
    C0, C1_, S0, S1 = trig
    dx, dy = x - core.kx, y - core.ky
    lim_e = core.a + g / 2
    if abs(dx * core.cm + dy * core.sm) > lim_e:
        return False
    if abs(-dx * core.sm + dy * core.cm) > lim_e:
        return False
    lim_f = HALF + core.a * g
    a0, a1 = imul4(C0, C1_, dx, dx)
    b0, b1 = imul4(S0, S1, dy, dy)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1, -S0, dx, dx)
    b0, b1 = imul4(C0, C1_, dy, dy)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


# ============================================================================ hypotheses
class Core:
    def __init__(self, kx, ky, tm, a):
        self.kx, self.ky, self.a = kx, ky, a
        self.cm, self.sm = cos_sin_t(tm)
        self.tm = tm
        self.fkx, self.fky, self.fa = float(kx), float(ky), float(a)
        self.fcm, self.fsm = float(self.cm), float(self.sm)


class NoFam:
    def __init__(self, x0, x1, y0, y1, tivs):
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.tivs = tivs


# ============================================================================ certificate I/O
def _rat(x):
    if isinstance(x, F):
        return x
    if isinstance(x, bool):
        raise ValueError("boolean is not a number")
    if isinstance(x, int):
        return F(x)
    if isinstance(x, float):
        raise ValueError(f"float {x!r} in certificate: numbers must be exact strings or ints")
    return F(str(x).strip())


def d4_images(x, y, s):
    return [(x, y), (s - x, y), (x, s - y), (s - x, s - y),
            (y, x), (s - y, x), (y, s - x), (s - y, s - x)]


def load_certificate(path, n_override=None):
    with open(path) as fh:
        d = json.load(fh)
    s = _rat(d["s"])
    n = int(n_override if n_override is not None else d.get("n", 11))
    raw = d["atoms"]
    atoms, weights = [], []
    if raw and isinstance(raw[0], dict):
        for a in raw:
            atoms.append((_rat(a["x"]), _rat(a["y"])))
            weights.append(_rat(a["w"]))
    else:
        ws = d["weights"]
        if len(ws) != len(raw):
            raise ValueError("atoms/weights length mismatch")
        for (x, y), w in zip(raw, ws):
            atoms.append((_rat(x), _rat(y)))
            weights.append(_rat(w))
    sym = d.get("symmetry")
    if sym:
        if str(sym).upper() != "D4":
            raise ValueError(f"unknown symmetry {sym!r}")
        ea, ew = [], []
        for (x, y), w in zip(atoms, weights):
            seen = []
            for q in d4_images(x, y, s):
                if q not in seen:
                    seen.append(q)
            for q in seen:
                ea.append(q)
                ew.append(w)
        atoms, weights = ea, ew
    for (x, y), w in zip(atoms, weights):
        if w < 0:
            raise ValueError("negative weight")
        if not (0 <= x <= s and 0 <= y <= s):
            raise ValueError(f"atom ({x},{y}) outside [0,s]^2")
    total = sum(weights, ZERO)
    hyp = d.get("hypotheses", {}) or {}
    cores = [Core(_rat(c["kx"]), _rat(c["ky"]), _rat(c["tm"]), _rat(c["a"])) for c in hyp.get("cores", [])]
    nofams = [NoFam(_rat(f["x0"]), _rat(f["x1"]), _rat(f["y0"]), _rat(f["y1"]),
                    [(_rat(a), _rat(b)) for a, b in f["t_intervals"]]) for f in hyp.get("nofams", [])]
    budget = int(d.get("budget", n))
    if budget != n - len(cores):
        raise ValueError(f"budget {budget} != n - #cores = {n - len(cores)}")
    return {"s": s, "n": n, "atoms": atoms, "weights": weights, "total": total,
            "cores": cores, "nofams": nofams, "budget": budget, "raw": d}


# ============================================================================ convex-polygon helpers
def clip_convex(poly, a, b, c):
    """Sutherland-Hodgman: keep the part of the convex polygon with a*x + b*y <= c (exact)."""
    out = []
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        d0 = a * x0 + b * y0 - c
        d1 = a * x1 + b * y1 - c
        if d0 <= 0:
            out.append((x0, y0))
        if (d0 < 0 < d1) or (d1 < 0 < d0):
            t = d0 / (d0 - d1)
            out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    return out


def poly_area2(poly):
    """twice the signed area (exact)."""
    a = ZERO
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a


def rect_meets_poly_interior(U0, U1, V0, V1, poly):
    """True iff the closed rectangle meets the INTERIOR of the convex polygon in positive area."""
    p = poly
    for (a, b, c) in ((F(1), ZERO, U1), (F(-1), ZERO, -U0), (ZERO, F(1), V1), (ZERO, F(-1), -V0)):
        p = clip_convex(p, a, b, c)
        if len(p) < 3:
            return False
    return abs(poly_area2(p)) > 0


class ConvexChains:
    """Lower and upper boundary of a convex polygon as functions of U (exact).  Used to bound, for a
    U-strip, the V-range of the polygon over that strip -- an OUTER bound, so cells discarded by it
    are certainly outside the polygon."""

    def __init__(self, poly):
        pts = sorted(set(poly))
        self.U0, self.U1 = pts[0][0], pts[-1][0]
        # split the boundary into the lower and upper chain by the line through the two extreme-U vertices
        lo, hi = [], []
        for (u, v) in pts:
            while len(lo) >= 2 and self._cross(lo[-2], lo[-1], (u, v)) <= 0:
                lo.pop()
            lo.append((u, v))
            while len(hi) >= 2 and self._cross(hi[-2], hi[-1], (u, v)) >= 0:
                hi.pop()
            hi.append((u, v))
        self.lower = lo      # convex chain, v as a convex function of u
        self.upper = hi      # concave chain

    @staticmethod
    def _cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    @staticmethod
    def _eval(chain, u):
        if u <= chain[0][0]:
            return chain[0][1]
        if u >= chain[-1][0]:
            return chain[-1][1]
        for i in range(len(chain) - 1):
            (x0, y0), (x1, y1) = chain[i], chain[i + 1]
            if x0 <= u <= x1:
                if x1 == x0:
                    return min(y0, y1)
                return y0 + (y1 - y0) * (u - x0) / (x1 - x0)
        return chain[-1][1]

    def vrange(self, a, b):
        """(vmin, vmax) of the polygon over the U-strip [a,b], or None if the strip misses it."""
        if b <= self.U0 or a >= self.U1:
            return None
        a = max(a, self.U0); b = min(b, self.U1)
        vmin = min(self._eval(self.lower, a), self._eval(self.lower, b))
        for (u, v) in self.lower:
            if a < u < b and v < vmin:
                vmin = v
        vmax = max(self._eval(self.upper, a), self._eval(self.upper, b))
        for (u, v) in self.upper:
            if a < u < b and v > vmax:
                vmax = v
        return vmin, vmax


# ============================================================================ the net verifier
class NetVerifier:
    def __init__(self, cert, margin=ZERO, use_numpy=True, verbose=False,
                 bisect_depth=24, bisect_cap=60000):
        self.s = cert["s"]
        self.n = cert["n"]
        self.atoms = cert["atoms"]
        self.weights = cert["weights"]
        self.total = cert["total"]
        self.cores = cert["cores"]
        self.nofams = cert["nofams"]
        self.budget = cert["budget"]
        self.margin = margin
        self.need = ONE + margin
        self.verbose = verbose
        self.use_numpy = use_numpy and np is not None
        # With no hypotheses there is nothing for a bisection to prove: the mass is CONSTANT on a
        # grid cell, so a light cell that meets the admissible region in positive area is already a
        # genuine hole.  Bisection is only ever needed to resolve the exempt boundary.
        self.bisect_depth = bisect_depth if (self.cores or self.nofams) else 0
        self.bisect_cap = bisect_cap
        WD = 1
        for w in self.weights:
            WD = WD * w.denominator // math.gcd(WD, w.denominator)
        self.WD = WD
        self.WI = [int(w.numerator * (WD // w.denominator)) for w in self.weights]
        nn, dd = self.need.numerator * WD, self.need.denominator
        self.NEED = nn // dd + (1 if nn % dd else 0)
        # int32 when the whole mass (an outer bound for every partial sum of the difference array,
        # weights being non-negative) fits with room to spare; int64 otherwise.  Exact either way.
        self.dtype = (np.int32 if (np is not None and sum(self.WI) < (1 << 30)) else
                      (np.int64 if np is not None else int))
        self.reset_stats()

    def reset_stats(self):
        self.n_cells = 0            # grid cells examined, over all net cells
        self.n_covered = 0
        self.n_outside = 0
        self.n_exempt = 0
        self.n_exempt_core = 0
        self.n_exempt_nofam = 0
        self.n_bisect = 0
        self.witnesses = []
        self.min_mass = None        # the smallest live mass seen (Fraction), over all net cells
        self.min_at = None

    # ------------------------------------------------------------------ one net cell
    def net_cell(self, t0, t1, collect_min=True, max_witnesses=8):
        """Decide (N_j) for the net cell [t0,t1].  Returns (ok, info)."""
        tk = (t0 + t1) / 2
        m, B = sigma_of_cell(t0, t1, tk)
        c, sn = cos_sin_t(tk)
        hb = B / 2
        # ---- admissible centre region P: union over the cell of [h(theta), s-h(theta)]^2.
        # h is unimodal in t; the union is governed by the SMALLEST h, attained at an endpoint.
        hlo = min(half_width(t0), half_width(t1))
        s = self.s
        shi = s - hlo
        if 2 * hlo > s:
            return True, {"vacuous": True, "m": m, "B": B, "cells": 0}
        corners = [(hlo, hlo), (s - hlo, hlo), (s - hlo, s - hlo), (hlo, s - hlo)]
        poly = [(c * x + sn * y, -sn * x + c * y) for (x, y) in corners]
        PU0 = min(p[0] for p in poly); PU1 = max(p[0] for p in poly)
        PV0 = min(p[1] for p in poly); PV1 = max(p[1] for p in poly)
        # ---- rotated atoms
        U = [c * x + sn * y for (x, y) in self.atoms]
        V = [-sn * x + c * y for (x, y) in self.atoms]
        # ---- exemption data, computed once per net cell (uniform over the cell: Lemma N3)
        gcache = [g_inf_over_cell(K, t0, t1) for K in self.cores]
        fgcache = [(tuple(float(z) for z in trig), float(g)) for (trig, g) in gcache]
        # ---- event grids (clamped to P's bounding box; atoms outside contribute nothing there)
        ue = {PU0, PU1}
        ve = {PV0, PV1}
        for i in range(len(U)):
            for e in (U[i] - hb, U[i] + hb):
                if PU0 < e < PU1:
                    ue.add(e)
            for e in (V[i] - hb, V[i] + hb):
                if PV0 < e < PV1:
                    ve.add(e)
        # grid lines along each core's exempt octagon (heuristic only -- soundness does not depend
        # on the event set -- but they stop a single huge grid cell from straddling a core)
        for j, K in enumerate(self.cores):
            trig, g = gcache[j]
            UK = c * K.kx + sn * K.ky
            VK = -sn * K.kx + c * K.ky
            for r in (K.a + g / 2, HALF + K.a * g):
                for e in (UK - r, UK + r):
                    if PU0 < e < PU1:
                        ue.add(e)
                for e in (VK - r, VK + r):
                    if PV0 < e < PV1:
                        ve.add(e)
        for fam in self.nofams:
            for (x, y) in ((fam.x0, fam.y0), (fam.x1, fam.y0), (fam.x0, fam.y1), (fam.x1, fam.y1)):
                e = c * x + sn * y
                if PU0 < e < PU1:
                    ue.add(e)
                e = -sn * x + c * y
                if PV0 < e < PV1:
                    ve.add(e)
        UE = sorted(ue)
        VE = sorted(ve)
        nu, nv = len(UE) - 1, len(VE) - 1
        if nu <= 0 or nv <= 0:
            return True, {"vacuous": True, "m": m, "B": B, "cells": 0}
        # ---- difference array (exact integers)
        import bisect
        if self.use_numpy:
            Dm = np.zeros((nu + 1, nv + 1), dtype=self.dtype)
        else:
            Dm = [[0] * (nv + 1) for _ in range(nu + 1)]
        for i in range(len(U)):
            a0, a1 = U[i] - hb, U[i] + hb
            b0, b1 = V[i] - hb, V[i] + hb
            if a1 <= PU0 or a0 >= PU1 or b1 <= PV0 or b0 >= PV1:
                continue
            iu0 = bisect.bisect_left(UE, a0) if a0 > PU0 else 0
            iu1 = bisect.bisect_left(UE, a1) if a1 < PU1 else nu
            iv0 = bisect.bisect_left(VE, b0) if b0 > PV0 else 0
            iv1 = bisect.bisect_left(VE, b1) if b1 < PV1 else nv
            if iu0 >= iu1 or iv0 >= iv1:
                continue
            w = self.WI[i]
            if self.use_numpy:
                Dm[iu0, iv0] += w; Dm[iu1, iv0] -= w; Dm[iu0, iv1] -= w; Dm[iu1, iv1] += w
            else:
                Dm[iu0][iv0] += w; Dm[iu1][iv0] -= w; Dm[iu0][iv1] -= w; Dm[iu1][iv1] += w
        if self.use_numpy:
            np.cumsum(Dm, axis=0, out=Dm)
            np.cumsum(Dm, axis=1, out=Dm)
            M = Dm[:nu, :nv]
            cellmin = int(M.min()) if M.size else 0
            nlight0 = int((M < self.NEED).sum())
            # mask off the strips/cells that provably miss P (exact convex-chain bound); a masked
            # cell is set to NEED so that it never becomes a light cell.  Sound: the bound is OUTER.
            ch = ConvexChains(poly)
            for iu in range(nu):
                vr = ch.vrange(UE[iu], UE[iu + 1])
                if vr is None:
                    M[iu, :] = self.NEED
                    continue
                vmin, vmax = vr
                j0 = max(0, bisect.bisect_right(VE, vmin) - 1)
                j1 = min(nv, bisect.bisect_left(VE, vmax))
                if j0 > 0:
                    M[iu, :j0] = self.NEED
                if j1 < nv:
                    M[iu, j1:] = self.NEED
            light = np.argwhere(M < self.NEED)
            self.n_outside += nlight0 - len(light)
            if len(light) > 200000:
                light = light[:200000]
        else:
            M = [[0] * nv for _ in range(nu)]
            acc = [0] * (nv + 1)
            light = []
            cellmin = None
            for iu in range(nu):
                run = 0
                for iv in range(nv):
                    acc[iv] += Dm[iu][iv]
                    run += acc[iv]
                    M[iu][iv] = run
                    if cellmin is None or run < cellmin:
                        cellmin = run
                    if run < self.NEED:
                        light.append((iu, iv))
            cellmin = cellmin or 0
        self.n_cells += nu * nv
        self.n_covered += nu * nv - len(light)
        # ---- adjudicate the light cells.  The mass is CONSTANT on a grid cell, so subdividing one
        # can never raise its mass: subdivision serves only to resolve the exempt region and P.
        wits = []
        cmin_live = None
        cmin_at = None
        nbis = 0
        nlive = 0
        for (iu, iv) in light:
            if nlive >= max_witnesses:
                break              # enough refutation for a FAIL verdict; live_min is then a bound
            iu, iv = int(iu), int(iv)
            mass = F(int(M[iu, iv]) if self.use_numpy else M[iu][iv], self.WD)
            # A node carries its (U,V) rectangle AND the (x,y) images of its four corners.  Bisection
            # is then pure averaging of corners -- no further multiplication by cos/sin, which keeps
            # the Fraction denominators from doubling in size at every level.
            Ua, Ub, Va, Vb = UE[iu], UE[iu + 1], VE[iv], VE[iv + 1]
            root = tuple((c * u - sn * v, sn * u + c * v)
                         for (u, v) in ((Ua, Va), (Ub, Va), (Ua, Vb), (Ub, Vb)))
            stack = [(0, Ua, Ub, Va, Vb, root)]
            live = None
            while stack:
                d, U0, U1, V0, V1, pts = stack.pop()
                # ---- admissibility: does this rectangle of centres meet the INTERIOR of the square
                # P = [hlo, s-hlo]^2 in positive area?  Two convex rectangles (one axis-aligned, one
                # at theta_k): by the separating-axis theorem the four edge normals x, y, U, V decide
                # it, and STRICT overlap on all four is exactly positive-area intersection.
                p00, p10, p01, p11 = pts
                Rx0 = min(p00[0], p10[0], p01[0], p11[0])
                Rx1 = max(p00[0], p10[0], p01[0], p11[0])
                Ry0 = min(p00[1], p10[1], p01[1], p11[1])
                Ry1 = max(p00[1], p10[1], p01[1], p11[1])
                if not (Rx1 > hlo and Rx0 < shi and Ry1 > hlo and Ry0 < shi
                        and U1 > PU0 and U0 < PU1 and V1 > PV0 and V0 < PV1):
                    self.n_outside += 1
                    continue
                ex = self.cell_exempt(pts, t0, t1, gcache, fgcache)
                if ex:
                    self.n_exempt += 1
                    if ex == "core":
                        self.n_exempt_core += 1
                    else:
                        self.n_exempt_nofam += 1
                    continue
                if d >= self.bisect_depth or nbis >= self.bisect_cap:
                    live = (U0, U1, V0, V1)
                    break
                nbis += 1
                if U1 - U0 >= V1 - V0:
                    mm = (U0 + U1) / 2
                    m0 = ((p00[0] + p10[0]) / 2, (p00[1] + p10[1]) / 2)
                    m1 = ((p01[0] + p11[0]) / 2, (p01[1] + p11[1]) / 2)
                    stack.append((d + 1, U0, mm, V0, V1, (p00, m0, p01, m1)))
                    stack.append((d + 1, mm, U1, V0, V1, (m0, p10, m1, p11)))
                else:
                    mm = (V0 + V1) / 2
                    m0 = ((p00[0] + p01[0]) / 2, (p00[1] + p01[1]) / 2)
                    m1 = ((p10[0] + p11[0]) / 2, (p10[1] + p11[1]) / 2)
                    stack.append((d + 1, U0, U1, V0, mm, (p00, p10, m0, m1)))
                    stack.append((d + 1, U0, U1, mm, V1, (m0, m1, p01, p11)))
            if live is None:
                continue
            nlive += 1
            U0, U1, V0, V1 = live
            if cmin_live is None or mass < cmin_live:
                cmin_live = mass
                cmin_at = (U0, U1, V0, V1)
            if len(wits) < max_witnesses:
                x = c * ((U0 + U1) / 2) - sn * ((V0 + V1) / 2)
                y = sn * ((U0 + U1) / 2) + c * ((V0 + V1) / 2)
                wits.append({"t_net": str(tk), "theta_deg": math.degrees(2 * math.atan(float(tk))),
                             "B": str(B), "mass": str(mass), "mass_float": float(mass),
                             "centre": [str(x), str(y)],
                             "centre_float": [float(x), float(y)]})
        info = {"m": m, "B": B, "cells": nu * nv, "nu": nu, "nv": nv, "bisections": nbis,
                "grid_min": F(cellmin, self.WD), "live_min": cmin_live, "live_min_at": cmin_at,
                "n_light": len(light), "witnesses": wits}
        self.n_bisect += nbis
        if cmin_live is not None:
            if self.min_mass is None or cmin_live < self.min_mass:
                self.min_mass = cmin_live
                self.min_at = (str(tk), [str(v) for v in cmin_at])
        return (cmin_live is None), info

    # ------------------------------------------------------------------ exemptions
    def cell_exempt(self, pts, t0, t1, gcache, fgcache):
        """'core' / 'nofam' / None.  Four corners suffice: both exempt regions are convex in the
        centre p (a box for a NO-family; a sublevel set of a max of linear forms for a core).  The
        float pass only SHORTLISTS; every accept is re-derived exactly.

        LEMMA N3.  The exemption is decided for the UNIT square, uniformly over the whole net cell
        -- never for the shrunk square.  S(p) is CONTAINED in every Q(p,theta) of the cell, so a p
        at which every Q of the cell meets a core carries only exempt unit squares and may be
        skipped whatever S(p) does.  Using the shrunk square here instead would lose a rim of width
        Theta(1-B) around every core, on which the LP has no reason to have placed any mass."""
        for fam in self.nofams:
            if not any(a <= t0 and t1 <= b for (a, b) in fam.tivs):
                continue
            if all(fam.x0 <= x <= fam.x1 and fam.y0 <= y <= fam.y1 for (x, y) in pts):
                return "nofam"
        if not self.cores:
            return None
        fpts = [(float(x), float(y)) for (x, y) in pts]
        for j, K in enumerate(self.cores):
            ftrig, fg = fgcache[j]
            if not all(core_exempt_point_float(K, ftrig, fg, x, y) for (x, y) in fpts):
                continue
            trig, g = gcache[j]
            if all(core_exempt_point(K, trig, g, x, y) for (x, y) in pts):
                return "core"
        return None

    # ------------------------------------------------------------------ the whole net
    def run(self, level, max_witnesses=8, stop_on_fail=True, progress=0):
        """K = 2^level uniform cells in t on [0,1]."""
        K = 1 << level
        self.reset_stats()
        cells = []
        ok_all = True
        t0 = time.time()
        for j in range(K):
            a, b = F(j, K), F(j + 1, K)
            try:
                ok, info = self.net_cell(a, b, max_witnesses=max_witnesses)
            except ValueError as e:       # net cell wider than the sigma lemma allows: refine
                self.elapsed = time.time() - t0
                self.K = K
                self.cells = cells or [(a, b, {"m": ONE, "B": ZERO, "grid_min": ZERO, "cells": 0})]
                self.too_wide = str(e)
                return False
            cells.append((a, b, info))
            if not ok:
                ok_all = False
                self.witnesses.extend(info["witnesses"])
                if stop_on_fail:
                    break
            if progress and (j + 1) % progress == 0:
                print(f"  ... net cell {j+1}/{K}  min so far "
                      f"{float(min(cc[2]['grid_min'] for cc in cells)):.9f}  {time.time()-t0:.1f}s",
                      flush=True)
        self.elapsed = time.time() - t0
        self.K = K
        self.cells = cells
        return ok_all

    # ------------------------------------------------------------------ adaptive net
    def run_adaptive(self, level0=1, max_level=24, max_witnesses=8, time_budget=None, progress=0):
        """Start from 2^level0 uniform cells and BISECT only the cells that fail, to depth
        max_level.  The net is then as fine as the geometry demands and no finer -- the analogue,
        in one dimension, of the frozen verifier's t-bisection.  Returns (ok, leaves)."""
        self.reset_stats()
        t_start = time.time()
        stack = [(level0, j) for j in reversed(range(1 << level0))]
        leaves = []
        ok_all = True
        self.deepest = level0
        while stack:
            if time_budget and time.time() - t_start > time_budget:
                self.timed_out = True
                ok_all = False
                break
            L, j = stack.pop()
            a, b = F(j, 1 << L), F(j + 1, 1 << L)
            try:
                ok, info = self.net_cell(a, b, max_witnesses=max_witnesses)
            except ValueError:
                ok, info = False, {"m": ONE, "B": ZERO, "cells": 0, "witnesses": []}
            if ok:
                leaves.append((L, j, info))
                continue
            if L >= max_level:
                self.witnesses.extend(info.get("witnesses", []))
                leaves.append((L, j, info))
                ok_all = False
                break
            self.deepest = max(self.deepest, L + 1)
            stack.append((L + 1, 2 * j + 1))
            stack.append((L + 1, 2 * j))
            if time_budget and time.time() - t_start > time_budget:
                ok_all = False
                self.timed_out = True
                break
            if progress and len(leaves) % progress == 0 and leaves:
                print(f"  ... {len(leaves)} net leaves, depth {self.deepest}, "
                      f"{time.time()-t_start:.1f}s", flush=True)
        self.elapsed = time.time() - t_start
        self.leaves = leaves
        self.K = len(leaves)
        self.cells = [(F(j, 1 << L), F(j + 1, 1 << L), info) for (L, j, info) in leaves]
        return ok_all


# ============================================================================ driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cert")
    ap.add_argument("--level", type=int, default=None, help="K = 2^level net cells")
    ap.add_argument("--search", nargs=2, type=int, default=None, metavar=("LO", "HI"),
                    help="smallest level in [LO,HI] that PASSes (doubling search)")
    ap.add_argument("--margin", type=str, default="0")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--no-numpy", action="store_true")
    ap.add_argument("--emit", type=str, default=None, help="write a net certificate JSON here")
    ap.add_argument("--max-witnesses", type=int, default=8)
    ap.add_argument("--progress", type=int, default=0)
    ap.add_argument("--adaptive", nargs=2, type=int, default=None, metavar=("L0", "LMAX"),
                    help="adaptive net: start at 2^L0 cells, bisect failing cells to depth LMAX")
    ap.add_argument("--time-budget", type=float, default=None, help="abandon the search after this many seconds")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    try:                                   # the PI is on the machine: never compete for the CPU
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass

    try:
        cert = load_certificate(a.cert, a.n)
    except Exception as e:
        print(f"MALFORMED certificate: {e}")
        return 2
    v = NetVerifier(cert, margin=F(a.margin), use_numpy=not a.no_numpy, verbose=not a.quiet)
    if not a.quiet:
        print(f"certificate: {a.cert}")
        print(f"s = {cert['s']} (~{float(cert['s']):.10f})  n = {cert['n']}  atoms = {len(cert['atoms'])}  "
              f"total = {float(cert['total']):.9f}  budget = {cert['budget']}  "
              f"cores = {len(cert['cores'])}  nofams = {len(cert['nofams'])}")
    if cert["total"] >= cert["budget"]:
        print(f"FAIL: total mass >= budget: certificate proves nothing")
        return 2

    t_all = time.time()
    results = []
    if a.adaptive is not None:
        L0, LMAX = a.adaptive
        v.timed_out = False
        ok_final = v.run_adaptive(L0, LMAX, max_witnesses=a.max_witnesses,
                                  time_budget=a.time_budget, progress=a.progress)
        Bmin = min((cc[2]["B"] for cc in v.cells), default=ONE)
        results.append({"mode": "adaptive", "L0": L0, "LMAX": LMAX, "deepest": v.deepest,
                        "K": v.K, "pass": bool(ok_final), "wall_s": v.elapsed,
                        "B": str(Bmin), "B_float": float(Bmin), "shrink": float(1 - Bmin),
                        "timed_out": bool(getattr(v, "timed_out", False)),
                        "grid_min_float": float(min((cc[2]["grid_min"] for cc in v.cells
                                                     if "grid_min" in cc[2]), default=ZERO)),
                        "live_min_float": (float(v.min_mass) if v.min_mass is not None else None),
                        "cells": v.n_cells, "bisections": v.n_bisect,
                        "exempt": v.n_exempt, "outside": v.n_outside})
        passed_level = v.deepest if ok_final else None
        if not a.quiet:
            print(f"  adaptive  net leaves = {v.K}  deepest level = {v.deepest}  "
                  f"B_min = {float(Bmin):.9f} (shrink {float(1-Bmin):.2e})  "
                  f"{'PASS' if ok_final else 'FAIL'}  {v.elapsed:.2f}s")
    elif a.search is not None:
        lo, hi = a.search
        passed_level = None
        for L in range(lo, hi + 1):
            ok = v.run(L, max_witnesses=a.max_witnesses, stop_on_fail=True, progress=a.progress)
            wall = v.elapsed
            worst = min((cc[2]["grid_min"] for cc in v.cells), default=ZERO)
            Bmin = min((cc[2]["B"] for cc in v.cells), default=ONE)
            rec = {"level": L, "K": 1 << L, "pass": bool(ok), "wall_s": wall,
                   "B": str(Bmin), "B_float": float(Bmin), "shrink": float(1 - Bmin),
                   "grid_min_float": float(worst),
                   "live_min_float": (float(v.min_mass) if v.min_mass is not None else None),
                   "cells": v.n_cells, "exempt": v.n_exempt, "outside": v.n_outside}
            results.append(rec)
            if not a.quiet:
                print(f"  level {L:2d}  K = {1<<L:7d}  B = {float(Bmin):.9f} (shrink {float(1-Bmin):.2e})  "
                      f"{'PASS' if ok else 'FAIL'}  live_min = "
                      f"{'-' if v.min_mass is None else f'{float(v.min_mass):.9f}'}  "
                      f"{wall:.2f}s", flush=True)
            if ok:
                passed_level = L
                break
            if a.time_budget and time.time() - t_all > a.time_budget:
                if not a.quiet:
                    print(f"  [time budget {a.time_budget}s exhausted at level {L}]")
                break
        ok_final = passed_level is not None
    else:
        L = a.level if a.level is not None else 8
        ok_final = v.run(L, max_witnesses=a.max_witnesses, stop_on_fail=True, progress=a.progress)
        Bmin = min((cc[2]["B"] for cc in v.cells), default=ONE)
        results.append({"level": L, "K": 1 << L, "pass": bool(ok_final), "wall_s": v.elapsed,
                        "B": str(Bmin), "B_float": float(Bmin), "shrink": float(1 - Bmin),
                        "grid_min_float": float(min((cc[2]["grid_min"] for cc in v.cells), default=ZERO)),
                        "live_min_float": (float(v.min_mass) if v.min_mass is not None else None),
                        "cells": v.n_cells, "exempt": v.n_exempt, "outside": v.n_outside})
        passed_level = L if ok_final else None
        if not a.quiet:
            print(f"  level {L}  K = {1<<L}  B = {float(Bmin):.9f}  {'PASS' if ok_final else 'FAIL'}  "
                  f"{v.elapsed:.2f}s")

    if not a.quiet:
        if ok_final:
            print(f"PASS (net): every non-exempt closed unit square in [0,{cert['s']}]^2 has mass >= "
                  f"{v.need}; total {float(cert['total']):.9f} < budget {cert['budget']}  "
                  f"==>  the node is DEAD.  net = {v.K} orientations "
                  f"(deepest level {passed_level}).")
        else:
            print(f"FAIL (net): {len(v.witnesses)} light cells at the deepest level tried.")
            for w in v.witnesses[:5]:
                print(f"    theta = {w['theta_deg']:.6f} deg  centre ~ ({w['centre_float'][0]:.9f}, "
                      f"{w['centre_float'][1]:.9f})  mass = {w['mass_float']:.9f}")

    if a.emit:
        out = {"format": "net-orientation-certificate-v1",
               "source_cert": os.path.abspath(a.cert),
               "s": str(cert["s"]), "n": cert["n"], "budget": cert["budget"],
               "atoms": [[str(x), str(y)] for (x, y) in cert["atoms"]],
               "weights": [str(w) for w in cert["weights"]],
               "total": str(cert["total"]),
               "hypotheses": cert["raw"].get("hypotheses", {}),
               "margin": str(v.margin),
               "net": {"parametrisation": "t = tan(theta/2) in [0,1]",
                       "mode": results[-1].get("mode", "uniform"),
                       "level": passed_level if passed_level is not None else results[-1].get("level"),
                       "K": v.K,
                       "cells": [[str(aa), str(bb)] for (aa, bb, _) in v.cells],
                       "sigma_rule": "B_j = (1+m^2)/(1+2m-m^2), m = max|tan((theta-theta_k)/2)| on cell j",
                       "B_min": results[-1]["B"]},
               "result": "PASS" if ok_final else "FAIL",
               "wall_s": results[-1]["wall_s"],
               "ladder": results,
               "witnesses": v.witnesses[:20]}
        with open(a.emit, "w") as fh:
            json.dump(out, fh, indent=1)
        if not a.quiet:
            print(f"  net certificate written to {a.emit}")
    return 0 if ok_final else 1


if __name__ == "__main__":
    sys.exit(main())
