#!/usr/bin/env python3
"""
verify_param.py -- A56 T2(C).  The 4D (t, cx, cy, s) verifier for parametric-kill-certificate-v1.

WHAT IS PROVED (soundness.md P3, verbatim).  Certificate C declares, for each s, the atomic
measure mu_s = sum_i w_i delta_{p_i(s)} with p_i(s) = (ax_i + bx_i s, ay_i + by_i s) and the
core (pin) squares K_j(s) centred at (akx_j + bkx_j s, aky_j + bky_j s), half-side a_j, tilt tm_j.
A PASS on the root [0,1] x [1/2, s_hi-1/2]^2 x [s_lo, s_hi] certifies

    for every s in [s_lo, s_hi] and every closed unit square Q admissible in [0,s]^2 that meets
    no core K_j(s):   mu_s(Q) >= 1 + margin,

together with the s-free inequality sum_i w_i < budget = n - #cores.  By A13/A53-L5 this is the
kill of the stratum for EVERY s in the window (soundness theorem [S] of notes/soundness.md).

REUSED, UNMODIFIED, FROM attempts/A53-simple-strata/code/verify_case.py (imported, not copied,
so the audited integer core is literally the same code):
    imul4, trig_int, box_trig            interval/trig integer primitives
    vacuous_int, clip_int                admissibility, rule (V) and (CL) -- called with s = b
    cos_sin_t, atom_inside_frac, mass_at_frac, core_exempt_frac      Fraction reference / witnesses
    CoreH, merge_stats, _rat
NEW HERE (the only new exact predicates; each is the A53 one with a POINT replaced by an
outward INTERVAL, so the enclosure can only grow):
    atom_inside_int_iv    atom_inside_int with px in [PXlo,PXhi]/PD, py in [PYlo,PYhi]/PD
    core_exempt_frac_iv   core_exempt_frac with kx in [kxlo,kxhi], ky in [kylo,kyhi]
    core_exempt_float_iv  the float pre-filter for the above (shortlist only; never decides)

DISCHARGE RULES on B = [t0,t1] x [x0,x1] x [y0,y1] x [a,b]  (P3):
  (V)  vacuous: vacuous_int with the wall at s = b (the largest container of the cell);
  (CL) clip:    clip_int with the wall at s = b -- lower bound floor(wmin/2), upper ceil(b-wmin/2);
  (E)  exempt:  core_exempt_frac_iv with kx,ky widened to [alpha+beta*a, alpha+beta*b];
  (C)  covered: sum of w_i over atoms whose whole s-interval box is inside Q for every (t,c) in B,
                compared with ceil((1+margin)*WD) in integers;
  else split the widest of t (x --tscale), x, y, s (x --sscale); an undischarged box at --depth
  is a FAIL witness and records its s-range.

INTEGER GRID.  One grid for x, y AND s:  D = 250000 * 2^(depth+2)  (250000 = den(s0), and
den(s_lo) = 50 divides it).  s_lo -> 955000*2^(depth+2), s0 -> 969271*2^(depth+2); the odd span
969271-955000 = 14271 is therefore bisectable exactly depth+2 times, far beyond any use.  t is on
2^K, K = depth+1, exactly as in A53.  Every accept decision is exact integer/Fraction arithmetic;
numpy is used only to shortlist atoms and to pick sample placements for witnesses.

USAGE
    python verify_param.py PARAM.json [--slo 191/50] [--shi 969271/250000] [--depth D]
        [--sscale 8] [--tscale 2] [--split k] [--jobs J] [--strict-margin m] [--report [path]]
        [--max-witnesses K] [--max-witnesses-per-box k] [--no-float-prepass] [--quiet]
    python verify_param.py --selftest
    exit 0 = PASS, 1 = FAIL, 2 = malformed.
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as F

_A53 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "A53-simple-strata", "code"))
if _A53 not in sys.path:
    sys.path.insert(0, _A53)
import verify_case as VC                                    # the audited fixed-s verifier
from verify_case import (imul4, trig_int, box_trig, vacuous_int, clip_int, cos_sin_t,
                         atom_inside_frac, mass_at_frac, core_exempt_frac, CoreH,
                         merge_stats, _rat)

try:
    import numpy as np
except Exception:                                            # pragma: no cover
    np = None

HALF = F(1, 2)
ONE = F(1)
ZERO = F(0)

S0 = F(969271, 250000)
S_LO_WINDOW = F(191, 50)
S_DEN = 250000                                               # den(s0); den(s_lo) = 50 divides it


# ===================================================================== new exact predicates
def atom_inside_int_iv(PXlo, PXhi, PYlo, PYhi, PD, D, Clo, Chi, Slo, Shi, E, X0, X1, Y0, Y1):
    """True iff EVERY point (px,py) with px in [PXlo,PXhi]/PD, py in [PYlo,PYhi]/PD lies in
    Q(c,theta) for EVERY cx in [X0,X1]/D, cy in [Y0,Y1]/D, cos in [Clo,Chi]/E, sin in [Slo,Shi]/E.
    Identical to A53 atom_inside_int with the point (PXn,PYn) replaced by an interval box; the
    resulting dx, dy enclosures are wider, so the test is at least as strict (sound)."""
    dxlo = PXlo * D - X1 * PD
    dxhi = PXhi * D - X0 * PD
    dylo = PYlo * D - Y1 * PD
    dyhi = PYhi * D - Y0 * PD
    lim = E * PD * D
    a0, a1 = imul4(Clo, Chi, dxlo, dxhi)
    b0, b1 = imul4(Slo, Shi, dylo, dyhi)
    if 2 * (a1 + b1) > lim or 2 * (a0 + b0) < -lim:          # u = C*dx + S*dy
        return False
    a0, a1 = imul4(-Shi, -Slo, dxlo, dxhi)
    b0, b1 = imul4(Clo, Chi, dylo, dyhi)
    if 2 * (a1 + b1) > lim or 2 * (a0 + b0) < -lim:          # v = -S*dx + C*dy
        return False
    return True


class CoreP:
    """core with an s-affine centre; .at(a,b) gives the exact centre interval over [a,b]."""

    def __init__(self, akx, bkx, aky, bky, tm, a):
        self.akx, self.bkx, self.aky, self.bky = akx, bkx, aky, bky
        self.tm, self.a = tm, a
        self.cm, self.sm = cos_sin_t(tm)
        self.fcm, self.fsm, self.fa = float(self.cm), float(self.sm), float(a)

    def at(self, sa, sb):
        kx0, kx1 = self.akx + self.bkx * sa, self.akx + self.bkx * sb
        ky0, ky1 = self.aky + self.bky * sa, self.aky + self.bky * sb
        if kx0 > kx1:
            kx0, kx1 = kx1, kx0
        if ky0 > ky1:
            ky0, ky1 = ky1, ky0
        return kx0, kx1, ky0, ky1

    def frozen(self, s):
        return CoreH(self.akx + self.bkx * s, self.aky + self.bky * s, self.tm, self.a)


def core_exempt_frac_iv(core, kx0, kx1, ky0, ky1, t0, t1, x0, x1, y0, y1):
    """True iff for EVERY (t, cx, cy) in the box AND EVERY core centre (kx,ky) in
    [kx0,kx1] x [ky0,ky1] the closed unit square Q(c,theta(t)) meets the core square.
    Exactly A53 core_exempt_frac with dx in [x0-kx1, x1-kx0], dy in [y0-ky1, y1-ky0]."""
    C1_, S0_ = cos_sin_t(t0)                                 # cos decreasing, sin increasing in t
    C0_, S1_ = cos_sin_t(t1)
    cm, sm, a = core.cm, core.sm, core.a
    Alo = C0_ * cm + S0_ * sm
    if Alo < 0:
        Alo = ZERO
    Blo = -S1_ * cm + C0_ * sm
    Bhi = -S0_ * cm + C1_ * sm
    if Blo <= 0 <= Bhi:
        Babs = ZERO
    else:
        Babs = min(abs(Blo), abs(Bhi))
    g_inf = Alo + Babs
    dxlo, dxhi = x0 - kx1, x1 - kx0
    dylo, dyhi = y0 - ky1, y1 - ky0
    lim_e = a + g_inf / 2                                    # core axes e1 = (cm,sm), e2 = (-sm,cm)
    lo = dxlo * cm + dylo * sm
    hi = dxhi * cm + dyhi * sm
    if max(abs(lo), abs(hi)) > lim_e:
        return False
    lo = -dxhi * sm + dylo * cm
    hi = -dxlo * sm + dyhi * cm
    if max(abs(lo), abs(hi)) > lim_e:
        return False
    lim_f = HALF + a * g_inf                                 # Q axes f1 = (C,S), f2 = (-S,C)
    a0, a1 = imul4(C0_, C1_, dxlo, dxhi)
    b0, b1 = imul4(S0_, S1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1_, -S0_, dxlo, dxhi)
    b0, b1 = imul4(C0_, C1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


def core_exempt_float_iv(core, fkx0, fkx1, fky0, fky1, ft0, ft1, fx0, fx1, fy0, fy1, slack=1e-7):
    """float pre-filter for core_exempt_frac_iv: False => certainly not provably exempt."""
    C1_ = (1 - ft0 * ft0) / (1 + ft0 * ft0)
    S0_ = 2 * ft0 / (1 + ft0 * ft0)
    C0_ = (1 - ft1 * ft1) / (1 + ft1 * ft1)
    S1_ = 2 * ft1 / (1 + ft1 * ft1)
    cm, sm, a = core.fcm, core.fsm, core.fa
    Alo = max(0.0, C0_ * cm + S0_ * sm)
    Blo = -S1_ * cm + C0_ * sm
    Bhi = -S0_ * cm + C1_ * sm
    Babs = 0.0 if Blo <= 0 <= Bhi else min(abs(Blo), abs(Bhi))
    g = Alo + Babs
    dxlo, dxhi = fx0 - fkx1, fx1 - fkx0
    dylo, dyhi = fy0 - fky1, fy1 - fky0
    lim_e = a + g / 2 + slack
    if max(abs(dxlo * cm + dylo * sm), abs(dxhi * cm + dyhi * sm)) > lim_e:
        return False
    if max(abs(-dxhi * sm + dylo * cm), abs(-dxlo * sm + dyhi * cm)) > lim_e:
        return False
    lim_f = 0.5 + a * g + slack
    a0, a1 = imul4(C0_, C1_, dxlo, dxhi)
    b0, b1 = imul4(S0_, S1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    a0, a1 = imul4(-S1_, -S0_, dxlo, dxhi)
    b0, b1 = imul4(C0_, C1_, dylo, dyhi)
    if max(abs(a0 + b0), abs(a1 + b1)) > lim_f:
        return False
    return True


# ===================================================================== per-s-cell geometry
class SCell:
    """exact integer/float data of the atoms and cores on one s-cell [SA,SB]/D."""
    __slots__ = ("PXlo", "PXhi", "PYlo", "PYhi", "PD", "fPXlo", "fPXhi", "fPYlo", "fPYhi",
                 "cores_iv", "fcores_iv")

    def __init__(self, v, SA, SB):
        D = v.D
        sa, sb = F(SA, D), F(SB, D)
        self.PXlo, self.PXhi, self.PYlo, self.PYhi, self.PD = [], [], [], [], []
        for (ax, bx, ay, by) in v.aff:
            x0, x1 = ax + bx * sa, ax + bx * sb
            y0, y1 = ay + by * sa, ay + by * sb
            if x0 > x1:
                x0, x1 = x1, x0
            if y0 > y1:
                y0, y1 = y1, y0
            pd = 1
            for q in (x0, x1, y0, y1):
                pd = pd * q.denominator // math.gcd(pd, q.denominator)
            self.PXlo.append(x0.numerator * (pd // x0.denominator))
            self.PXhi.append(x1.numerator * (pd // x1.denominator))
            self.PYlo.append(y0.numerator * (pd // y0.denominator))
            self.PYhi.append(y1.numerator * (pd // y1.denominator))
            self.PD.append(pd)
        if np is not None:
            self.fPXlo = np.array([a / b for a, b in zip(self.PXlo, self.PD)])
            self.fPXhi = np.array([a / b for a, b in zip(self.PXhi, self.PD)])
            self.fPYlo = np.array([a / b for a, b in zip(self.PYlo, self.PD)])
            self.fPYhi = np.array([a / b for a, b in zip(self.PYhi, self.PD)])
        self.cores_iv = [c.at(sa, sb) for c in v.cores]
        self.fcores_iv = [tuple(float(q) for q in iv) for iv in self.cores_iv]


# ===================================================================== the 4D search
class PVerifier:
    def __init__(self, aff, weights, cores, slo, shi, margin=ZERO, depth=48, tscale=2, sscale=8,
                 use_float=True, max_witnesses=200, verbose=True, progress_every=200000,
                 cache_cap=256):
        if not (S_LO_WINDOW <= slo <= shi <= S0):
            raise ValueError(f"s-window [{slo},{shi}] not inside the census window "
                             f"[{S_LO_WINDOW},{S0}] (canary C3)")
        self.slo, self.shi = slo, shi
        self.margin = margin
        self.need = ONE + margin
        self.depth = depth
        self.tscale = int(tscale) if F(tscale).denominator == 1 else F(tscale)
        self.sscale = int(sscale) if F(sscale).denominator == 1 else F(sscale)
        self.max_witnesses = max_witnesses
        self.verbose = verbose
        self.progress_every = progress_every
        order = sorted(range(len(aff)), key=lambda i: -weights[i])
        self.aff = [aff[i] for i in order]
        self.weights = [weights[i] for i in order]
        self.cores = list(cores)
        # ---- one integer grid for x, y and s
        self.K = depth + 1
        self.T_ROOT = 1 << self.K
        self.D = S_DEN << (depth + 2)
        for q in (slo, shi):
            if (self.D % q.denominator) != 0:
                raise ValueError(f"s endpoint {q} not on the grid")
        self.SA_ROOT = slo.numerator * (self.D // slo.denominator)
        self.SB_ROOT = shi.numerator * (self.D // shi.denominator)
        # weights as integers over a common denominator
        WD = 1
        for w in self.weights:
            WD = WD * w.denominator // math.gcd(WD, w.denominator)
        self.WD = WD
        self.WI = [w.numerator * (WD // w.denominator) for w in self.weights]
        num = self.need.numerator * WD
        self.NEED = num // self.need.denominator + (1 if num % self.need.denominator else 0)
        self.use_float = use_float and np is not None and len(aff) > 0
        if np is not None:
            self.fW = np.array([float(w) for w in self.weights])
        self.fneed = float(self.need) - 1e-9
        self._cache = {}
        self._cache_cap = cache_cap
        self.reset_stats()

    # -- per-cell geometry (cached)
    def cell(self, SA, SB):
        key = (SA, SB)
        c = self._cache.get(key)
        if c is None:
            if len(self._cache) >= self._cache_cap:
                self._cache.clear()
            c = SCell(self, SA, SB)
            self._cache[key] = c
            self.n_cells_built += 1
            self.scells.add(key)
        return c

    def reset_stats(self):
        self.n_boxes = 0
        self.n_vac = 0
        self.n_cov = 0
        self.n_split = 0
        self.n_split_s = 0
        self.n_exact = 0
        self.n_float_reject = 0
        self.n_exempt = 0
        self.n_cells_built = 0
        self.scells = set()
        self.hist_cov = {}
        self.witnesses = []
        self.max_depth_seen = 0
        self.max_sdepth_seen = 0

    def root_boxes(self, k):
        lo = self.D >> 1
        hi = self.SB_ROOT - lo                # the largest container of the window
        m = 1 << k
        span = hi - lo
        step = span >> k
        assert step << k == span, "split too fine for the integer scale"
        out = []
        for i in range(m):
            for j in range(m):
                out.append((2 * k, 0, self.T_ROOT, lo + step * i, lo + step * (i + 1),
                            lo + step * j, lo + step * (j + 1),
                            self.SA_ROOT, self.SB_ROOT, (), 0, 0))
        return out

    def float_candidates(self, cell, ft0, ft1, fx0, fx1, fy0, fy1):
        eps = 1e-9
        C0 = max(0.0, (1 - ft1 * ft1) / (1 + ft1 * ft1) - eps)
        C1 = (1 - ft0 * ft0) / (1 + ft0 * ft0) + eps
        S0_ = max(0.0, 2 * ft0 / (1 + ft0 * ft0) - eps)
        S1 = 2 * ft1 / (1 + ft1 * ft1) + eps
        dx0 = cell.fPXlo - fx1
        dx1 = cell.fPXhi - fx0
        dy0 = cell.fPYlo - fy1
        dy1 = cell.fPYhi - fy0
        a_hi = np.maximum(C0 * dx1, C1 * dx1)
        a_lo = np.minimum(C0 * dx0, C1 * dx0)
        b_hi = np.maximum(S0_ * dy1, S1 * dy1)
        b_lo = np.minimum(S0_ * dy0, S1 * dy0)
        ok = (a_hi + b_hi <= 0.5 + eps) & (a_lo + b_lo >= -0.5 - eps)
        a_hi = np.maximum(-S1 * dx0, -S0_ * dx0)
        a_lo = np.minimum(-S1 * dx1, -S0_ * dx1)
        b_hi = np.maximum(C0 * dy1, C1 * dy1)
        b_lo = np.minimum(C0 * dy0, C1 * dy0)
        ok &= (a_hi + b_hi <= 0.5 + eps) & (a_lo + b_lo >= -0.5 - eps)
        return np.nonzero(ok)[0]

    def exempt(self, cell, T0, T1, X0, X1, Y0, Y1):
        if not self.cores:
            return False
        r, D = self.T_ROOT, self.D
        t0, t1 = F(T0, r), F(T1, r)
        x0, x1, y0, y1 = F(X0, D), F(X1, D), F(Y0, D), F(Y1, D)
        ft0, ft1, fx0, fx1, fy0, fy1 = T0 / r, T1 / r, X0 / D, X1 / D, Y0 / D, Y1 / D
        for core, iv, fiv in zip(self.cores, cell.cores_iv, cell.fcores_iv):
            if (core_exempt_float_iv(core, fiv[0], fiv[1], fiv[2], fiv[3],
                                     ft0, ft1, fx0, fx1, fy0, fy1)
                    and core_exempt_frac_iv(core, iv[0], iv[1], iv[2], iv[3],
                                            t0, t1, x0, x1, y0, y1)):
                return True
        return False

    def covered(self, cell, T0, T1, X0, X1, Y0, Y1, known, kmass):
        if self.use_float:
            r, D = self.T_ROOT, self.D
            cand = self.float_candidates(cell, T0 / r, T1 / r, X0 / D, X1 / D, Y0 / D, Y1 / D)
            idx = cand.tolist()
            if self.fW[cand].sum() < self.fneed:
                self.n_float_reject += 1
                if len(idx) == len(known):
                    return False, known, kmass
        else:
            idx = range(len(self.aff))
        Clo, Chi, Slo, Shi, E = box_trig(T0, T1, self.K)
        D = self.D
        PXlo, PXhi, PYlo, PYhi, PD, WI = (cell.PXlo, cell.PXhi, cell.PYlo, cell.PYhi,
                                          cell.PD, self.WI)
        acc = kmass
        new = list(known)
        kset = set(known)
        NEED = self.NEED
        for i in idx:
            if i in kset:
                continue
            self.n_exact += 1
            if atom_inside_int_iv(PXlo[i], PXhi[i], PYlo[i], PYhi[i], PD[i], D,
                                  Clo, Chi, Slo, Shi, E, X0, X1, Y0, Y1):
                acc += WI[i]
                new.append(i)
                if acc >= NEED:
                    return True, None, None
        return False, tuple(new), acc

    # -- witnesses
    def atoms_at(self, s):
        return [(ax + bx * s, ay + by * s) for (ax, bx, ay, by) in self.aff]

    def exact_mass_at(self, s, t, cx, cy):
        pts = self.atoms_at(s)
        idx = None
        if np is not None:
            fx = np.array([float(p[0]) for p in pts])
            fy = np.array([float(p[1]) for p in pts])
            idx = np.nonzero(VC.f_mass_mask(fx, fy, float(t), float(cx), float(cy), 1e-9))[0].tolist()
        return mass_at_frac(pts, self.weights, t, cx, cy, idx)

    def make_witness(self, d, T0, T1, X0, X1, Y0, Y1, SA, SB):
        r, D = self.T_ROOT, self.D
        t0, t1 = F(T0, r), F(T1, r)
        x0, x1, y0, y1 = F(X0, D), F(X1, D), F(Y0, D), F(Y1, D)
        sa, sb = F(SA, D), F(SB, D)
        w = {"depth": d,
             "box": {"t": [str(t0), str(t1)], "cx": [str(x0), str(x1)], "cy": [str(y0), str(y1)],
                     "s": [str(sa), str(sb)]},
             "s_range_float": [float(sa), float(sb)]}
        best = None
        for ss in dict.fromkeys((sa, sb, (sa + sb) / 2)):
            for tt in dict.fromkeys(((t0 + t1) / 2, t0, t1)):
                c, sn = cos_sin_t(tt)
                h = (c + sn) / 2
                for fx in dict.fromkeys(((x0 + x1) / 2, x0, x1)):
                    if fx < h or fx > ss - h:
                        continue
                    for fy in dict.fromkeys(((y0 + y1) / 2, y0, y1)):
                        if fy < h or fy > ss - h:
                            continue
                        m = self.exact_mass_at(ss, tt, fx, fy)
                        if best is None or m < best[0]:
                            best = (m, ss, tt, fx, fy)
        if best is None:
            w["placement"] = None
            w["kind"] = "undecided"
            return w
        m, ss, tt, fx, fy = best
        w["placement"] = {"s": str(ss), "t": str(tt), "cx": str(fx), "cy": str(fy),
                          "s_float": float(ss), "t_float": float(tt),
                          "theta_deg": math.degrees(2 * math.atan(float(tt))),
                          "cx_float": float(fx), "cy_float": float(fy)}
        w["exact_mass"] = str(m)
        w["float_mass"] = float(m)
        w["kind"] = "hole" if m < self.need else "undecided"
        return w

    # -- driver
    def run(self, boxes, per_box_cap=None):
        D, K = self.D, self.K
        tscale, sscale = self.tscale, self.sscale
        need_stop = False
        tstart = time.time()
        for box in boxes:
            if need_stop:
                break
            stack = [box]
            nw0 = len(self.witnesses)
            while stack:
                d, T0, T1, X0, X1, Y0, Y1, SA, SB, known, kmass, sd = stack.pop()
                self.n_boxes += 1
                if d > self.max_depth_seen:
                    self.max_depth_seen = d
                if sd > self.max_sdepth_seen:
                    self.max_sdepth_seen = sd
                # (V) + (CL) with the wall at s = b  (SB): the largest container of the cell
                clipped = clip_int(SB, D, K, T0, T1, X0, X1, Y0, Y1)
                if clipped is None:
                    self.n_vac += 1
                    continue
                X0, X1, Y0, Y1 = clipped
                cell = self.cell(SA, SB)
                if self.exempt(cell, T0, T1, X0, X1, Y0, Y1):
                    self.n_exempt += 1
                    continue
                ok, known, kmass = self.covered(cell, T0, T1, X0, X1, Y0, Y1, known, kmass)
                if ok:
                    self.n_cov += 1
                    self.hist_cov[d] = self.hist_cov.get(d, 0) + 1
                    continue
                if d >= self.depth:
                    self.witnesses.append(self.make_witness(d, T0, T1, X0, X1, Y0, Y1, SA, SB))
                    if len(self.witnesses) >= self.max_witnesses:
                        need_stop = True
                        break
                    if per_box_cap is not None and len(self.witnesses) - nw0 >= per_box_cap:
                        break
                    continue
                self.n_split += 1
                wt = (T1 - T0) * tscale * D
                wx = (X1 - X0) * self.T_ROOT
                wy = (Y1 - Y0) * self.T_ROOT
                ws = (SB - SA) * sscale * self.T_ROOT
                if SB - SA == 0 or (SA + SB) & 1:
                    ws = -1                      # s not splittable exactly: never pick it
                order = sorted(((wx, 0), (wy, 1), (wt, 2), (ws, 3)), key=lambda p: -p[0])
                ax = order[0][1]
                if ax == 0:
                    m = (X0 + X1) >> 1
                    stack.append((d + 1, T0, T1, m, X1, Y0, Y1, SA, SB, known, kmass, sd))
                    stack.append((d + 1, T0, T1, X0, m, Y0, Y1, SA, SB, known, kmass, sd))
                elif ax == 1:
                    m = (Y0 + Y1) >> 1
                    stack.append((d + 1, T0, T1, X0, X1, m, Y1, SA, SB, known, kmass, sd))
                    stack.append((d + 1, T0, T1, X0, X1, Y0, m, SA, SB, known, kmass, sd))
                elif ax == 2:
                    m = (T0 + T1) >> 1
                    stack.append((d + 1, m, T1, X0, X1, Y0, Y1, SA, SB, known, kmass, sd))
                    stack.append((d + 1, T0, m, X0, X1, Y0, Y1, SA, SB, known, kmass, sd))
                else:
                    m = (SA + SB) >> 1
                    self.n_split_s += 1
                    stack.append((d + 1, T0, T1, X0, X1, Y0, Y1, m, SB, known, kmass, sd + 1))
                    stack.append((d + 1, T0, T1, X0, X1, Y0, Y1, SA, m, known, kmass, sd + 1))
                if self.verbose and self.n_boxes % self.progress_every == 0:
                    print(f"  ... {self.n_boxes} boxes ({self.n_cov} cov, {self.n_vac} vac, "
                          f"{self.n_exempt} exempt, {self.n_split_s} s-splits, "
                          f"{len(self.witnesses)} witnesses), stack {len(stack)}, "
                          f"{time.time()-tstart:.0f}s", flush=True)
        self.stopped_early = need_stop
        return len(self.witnesses) == 0

    def stats(self):
        return {"boxes": self.n_boxes, "covered": self.n_cov, "vacuous": self.n_vac,
                "exempt": self.n_exempt, "split": self.n_split, "s_splits": self.n_split_s,
                "exact_atom_checks": self.n_exact, "float_rejects": self.n_float_reject,
                "max_depth": self.max_depth_seen, "max_s_depth": self.max_sdepth_seen,
                "s_cells": len(self.scells), "s_cells_built": self.n_cells_built,
                "depth_hist_covered": dict(sorted(self.hist_cov.items())),
                "witnesses": len(self.witnesses)}


# ===================================================================== certificate I/O
def load_param(path):
    with open(path) as fh:
        p = json.load(fh)
    if p.get("format") != "parametric-kill-certificate-v1":
        raise ValueError(f"unexpected format {p.get('format')!r}")
    if p["hypotheses"].get("nofams"):
        raise ValueError("nofams unsupported")
    aff, weights = [], []
    for a in p["atoms"]:
        aff.append((_rat(a["ax"]), _rat(a["bx"]), _rat(a["ay"]), _rat(a["by"])))
        w = _rat(a["w"])
        if w < 0:
            raise ValueError("negative weight")
        weights.append(w)
    cores = []
    for c in p["hypotheses"]["cores"]:
        cores.append(CoreP(_rat(c["akx"]), _rat(c["bkx"]), _rat(c["aky"]), _rat(c["bky"]),
                           _rat(c["tm"]), _rat(c["a"])))
        if not (0 <= cores[-1].tm <= 1) or cores[-1].a <= 0:
            raise ValueError("bad core")
    n = int(p.get("n", 11))
    budget = int(p["budget"])
    if budget != n - len(cores):
        raise ValueError(f"budget {budget} != n - #cores")
    total = sum(weights, ZERO)
    if _rat(p["total"]) != total:
        print(f"WARNING: declared total {p['total']} != computed {total}", file=sys.stderr)
    return p, n, budget, aff, weights, cores, total


# ===================================================================== self test
def selftest(n_iter=1500, seed=7):
    """Cross-check the interval predicates against POINTWISE Fraction evaluation at random
    (t, c, s) inside random 4D boxes:
        inside-for-box  =>  the atom at that s is inside Q at that (t,c)   (via mass_at_frac)
        exempt-for-box  =>  A53 core_exempt_frac holds for the degenerate box at that (t,c)
                            with the core frozen at that s.
    Also checks the degenerate-s case against A53 atom_inside_int."""
    import random
    rng = random.Random(seed)
    depth = 14
    bad = 0
    n_ins = n_exm = n_deg = 0
    for it in range(n_iter):
        i0 = rng.randint(955000, 969271)
        i1 = i0 if rng.random() < 0.2 else rng.randint(i0, 969271)
        slo, shi = F(i0, S_DEN), F(i1, S_DEN)     # endpoints on the 1/250000 grid
        ax = F(rng.randint(0, 3000), 1000)
        ay = F(rng.randint(0, 3000), 1000)
        bx = F(rng.choice([0, 1, 1, 2]), 2)
        by = F(rng.choice([0, 1, 1, 2]), 2)
        aff = [(ax - bx * S0, bx, ay - by * S0, by)]     # p(s0) = (ax, ay), moves with beta
        core = CoreP(F(rng.choice([1, 3, 5]), 2) - F(rng.choice([0, 1])) * S0,
                     F(rng.choice([0, 1])), F(rng.choice([1, 3, 5]), 2), F(0),
                     F(1, 33554432), F(rng.randint(300, 499), 1000))
        v = PVerifier(aff, [ONE], [core], slo, shi, depth=depth, use_float=False, verbose=False)
        D, K, R = v.D, v.K, v.T_ROOT
        T0 = rng.randint(0, R - 1)
        T1 = rng.randint(T0 + 1, R)
        lo, hi = D >> 1, v.SB_ROOT - (D >> 1)
        X0 = rng.randint(lo, hi - 1)
        X1 = rng.randint(X0 + 1, hi)
        Y0 = rng.randint(lo, hi - 1)
        Y1 = rng.randint(Y0 + 1, hi)
        if rng.random() < 0.6:
            X1 = min(hi, X0 + rng.randint(1, D // 40 + 1))
            Y1 = min(hi, Y0 + rng.randint(1, D // 40 + 1))
            T1 = min(R, T0 + rng.randint(1, R // 20 + 1))
        SA, SB = v.SA_ROOT, v.SB_ROOT
        if rng.random() < 0.5 and SB > SA:
            SA = rng.randint(SA, SB - 1)
            SB = rng.randint(SA + 1, SB)
        cell = v.cell(SA, SB)
        Clo, Chi, Slo, Shi, E = box_trig(T0, T1, K)
        ins = atom_inside_int_iv(cell.PXlo[0], cell.PXhi[0], cell.PYlo[0], cell.PYhi[0],
                                 cell.PD[0], D, Clo, Chi, Slo, Shi, E, X0, X1, Y0, Y1)
        iv = cell.cores_iv[0]
        exm = core_exempt_frac_iv(core, iv[0], iv[1], iv[2], iv[3], F(T0, R), F(T1, R),
                                  F(X0, D), F(X1, D), F(Y0, D), F(Y1, D))
        n_ins += bool(ins)
        n_exm += bool(exm)
        # degenerate-s consistency with the A53 point predicate
        if SA == SB:
            n_deg += 1
            pd = cell.PD[0]
            if ins != VC.atom_inside_int(cell.PXlo[0], cell.PYlo[0], pd, D, Clo, Chi, Slo, Shi,
                                         E, X0, X1, Y0, Y1):
                bad += 1
                print("DEGENERATE-S MISMATCH vs A53 atom_inside_int")
        for _ in range(4):
            SS = rng.randint(SA, SB)
            ss = F(SS, D)
            tt = F(rng.randint(T0, T1), R)
            cx = F(rng.randint(X0, X1), D)
            cy = F(rng.randint(Y0, Y1), D)
            px = aff[0][0] + aff[0][1] * ss
            py = aff[0][2] + aff[0][3] * ss
            if ins:
                if mass_at_frac([(px, py)], [ONE], tt, cx, cy) != 1:
                    bad += 1
                    print("UNSOUND (C): inside-for-box but atom outside at a sample")
                if not atom_inside_frac(px, py, tt, tt, cx, cx, cy, cy):
                    bad += 1
                    print("UNSOUND (C): atom_inside_frac disagrees at a sample")
            if exm:
                if not core_exempt_frac(core.frozen(ss), tt, tt, cx, cx, cy, cy):
                    bad += 1
                    print("UNSOUND (E): exempt-for-box but A53 core_exempt_frac fails at a sample")
    print(f"selftest: {n_iter} random 4D boxes, {bad} problems  "
          f"(inside-for-box hits {n_ins}, exempt-for-box hits {n_exm}, degenerate-s cells {n_deg})")
    return bad == 0


# ===================================================================== parallel driver
def merge_stats_p(acc, st):
    """A53 merge_stats, except that every max_* key is MAXed (A53 special-cases only max_depth)
    and s_cells is summed over workers -- i.e. an UPPER bound on the number of distinct s-cells,
    since two workers may build the same cell."""
    for k, val in st.items():
        if isinstance(val, dict):
            dd = acc.setdefault(k, {})
            for kk, vv in val.items():
                dd[kk] = dd.get(kk, 0) + vv
        elif k.startswith("max_"):
            acc[k] = max(acc.get(k, 0), val)
        else:
            acc[k] = acc.get(k, 0) + val
    return acc


_G = {}


def _worker_init(aff, weights, cores, slo, shi, margin, depth, tscale, sscale, use_float,
                 max_w, per_box_cap):
    _G["v"] = PVerifier(aff, weights, cores, slo, shi, margin=margin, depth=depth, tscale=tscale,
                        sscale=sscale, use_float=use_float, max_witnesses=max_w, verbose=False)
    _G["cap"] = per_box_cap


def _worker(box):
    v = _G["v"]
    v.reset_stats()
    v.run([box], per_box_cap=_G["cap"])
    return v.stats(), v.witnesses


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cert", nargs="?")
    ap.add_argument("--slo", default=str(S_LO_WINDOW))
    ap.add_argument("--shi", default=str(S0))
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--sscale", default="8", help="weight of the s-width when choosing the axis")
    ap.add_argument("--tscale", default="2")
    ap.add_argument("--split", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--strict-margin", default="0")
    ap.add_argument("--report", nargs="?", const="__auto__", default=None)
    ap.add_argument("--witness-file", default=None)
    ap.add_argument("--max-witnesses", type=int, default=200)
    ap.add_argument("--max-witnesses-per-box", type=int, default=8)
    ap.add_argument("--no-float-prepass", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return 0 if selftest() else 1
    if not a.cert:
        ap.error("certificate path required")

    t_start = time.time()
    try:
        p, n, budget, aff, weights, cores, total = load_param(a.cert)
        slo, shi = F(a.slo), F(a.shi)
    except Exception as e:
        print(f"MALFORMED certificate: {e}")
        return 2
    if total >= budget:
        print(f"FAIL: total {float(total):.6f} >= budget {budget}: certificate proves nothing")
        return 2
    margin = F(a.strict_margin)
    verbose = not a.quiet
    print(f"parametric certificate: {a.cert}  ({p.get('name')})")
    print(f"s in [{slo}, {shi}]  (~[{float(slo):.9f}, {float(shi):.9f}], width "
          f"{float(shi-slo):.9f}), n = {n}, atoms = {len(aff)}, cores = {len(cores)}, "
          f"budget = {budget}, total = {total} (~{float(total):.9f}), margin = {margin}")
    print(f"anchoring: {p.get('anchoring')}")

    use_float = not a.no_float_prepass
    v0 = PVerifier(aff, weights, cores, slo, shi, margin=margin, depth=a.depth,
                   tscale=F(a.tscale), sscale=F(a.sscale), use_float=use_float,
                   max_witnesses=a.max_witnesses, verbose=verbose)
    boxes = v0.root_boxes(a.split)
    stats, witnesses = {}, []
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs, initializer=_worker_init,
                     initargs=(aff, weights, cores, slo, shi, margin, a.depth, F(a.tscale),
                               F(a.sscale), use_float, a.max_witnesses,
                               a.max_witnesses_per_box)) as pool:
            done = 0
            for st, ws in pool.imap_unordered(_worker, boxes):
                merge_stats_p(stats, st)
                witnesses.extend(ws)
                done += 1
                if verbose and (done % max(1, len(boxes) // 16) == 0):
                    print(f"  ... {done}/{len(boxes)} top boxes, {stats['boxes']} boxes, "
                          f"{len(witnesses)} witnesses, {time.time()-t_start:.0f}s", flush=True)
                if len(witnesses) >= a.max_witnesses:
                    pool.terminate()
                    break
        # s_cells is summed over workers: an UPPER bound on the number of distinct s-cells touched
    else:
        v0.run(boxes, per_box_cap=a.max_witnesses_per_box)
        stats = v0.stats()
        witnesses = v0.witnesses
    stats["witnesses"] = len(witnesses)
    elapsed = time.time() - t_start
    passed = len(witnesses) == 0

    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  vacuous = {stats['vacuous']}  "
          f"exempt = {stats['exempt']}  split = {stats['split']}  s-splits = {stats['s_splits']}  "
          f"s-cells = {stats['s_cells']}  max depth = {stats['max_depth']}  "
          f"max s-depth = {stats['max_s_depth']}  time = {elapsed:.1f}s")
    if passed:
        print(f"PASS: for EVERY s in [{slo}, {shi}], every admissible closed unit square in "
              f"[0,s]^2 disjoint from all {len(cores)} cores has mu_s >= {ONE + margin}; "
              f"total {total} < budget {budget}  ==>  the stratum is empty for every s in the "
              f"window (node DEAD on the whole window)")
    else:
        holes = [w for w in witnesses if w.get("kind") == "hole"]
        print(f"FAIL: {len(witnesses)} witness boxes at depth {a.depth} ({len(holes)} HOLES)"
              + ("  [stopped at --max-witnesses]" if len(witnesses) >= a.max_witnesses else ""))
        pick = min(witnesses, key=lambda w: w.get("float_mass", 9e9))
        if pick.get("placement"):
            q = pick["placement"]
            print(f"  worst witness: s = {q['s']} (~{q['s_float']:.9f}), theta = "
                  f"{q['theta_deg']:.6f} deg, centre = ({q['cx_float']:.9f}, {q['cy_float']:.9f}), "
                  f"exact mass = {pick['exact_mass']} (~{pick['float_mass']:.12f})")
        srs = [w["s_range_float"] for w in witnesses if "s_range_float" in w]
        if srs:
            print(f"  witness s-ranges: [{min(r[0] for r in srs):.9f}, "
                  f"{max(r[1] for r in srs):.9f}] over {len(srs)} boxes")
        wf = a.witness_file or (os.path.splitext(a.cert)[0] + ".witnesses.json")
        with open(wf, "w") as fh:
            json.dump({"cert": a.cert, "slo": str(slo), "shi": str(shi), "depth": a.depth,
                       "margin": str(margin), "witnesses": witnesses}, fh, indent=1)
        print(f"  witnesses written to {wf}")
    if a.report is not None:
        rp = a.report if a.report != "__auto__" else os.path.splitext(a.cert)[0] + ".report.json"
        srs = [w["s_range_float"] for w in witnesses if "s_range_float" in w]
        with open(rp, "w") as fh:
            json.dump({"cert": a.cert, "name": p.get("name"), "slo": str(slo), "shi": str(shi),
                       "n": n, "budget": budget, "atoms": len(aff), "cores": len(cores),
                       "total": str(total), "margin": str(margin), "depth": a.depth,
                       "tscale": a.tscale, "sscale": a.sscale, "jobs": a.jobs, "split": a.split,
                       "anchoring": p.get("anchoring"),
                       "result": "PASS" if passed else "FAIL", "time_s": elapsed, "stats": stats,
                       "witness_s_range": ([min(r[0] for r in srs), max(r[1] for r in srs)]
                                           if srs else None),
                       "witnesses_preview": witnesses[:10]}, fh, indent=1)
        print(f"  report written to {rp}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
