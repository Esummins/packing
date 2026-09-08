"""A92 -- the CROWD family builder (chore_crowd_cert.md sec 1).

Objects built here, all exact in Fractions:

  a_w(delta) = lambda_max * (1 - delta) + (lambda_max - 1) * 7072/10000   (rounded UP to 1e-5)

  F_c(a)  = {admissible (cx,cy,theta) at s0 : f_c(cx,cy,t) <= a},  f = corner85.f_min_max
            (Q meets the CLOSED box [0,a]^2 in c's frame iff f <= a).

  G_c     OUTER cover of F_c(a_w): a union of (centre rect) x (theta bin) boxes.  f is
          nondecreasing in both corner-frame centre coordinates and (sqrt2/2)-Lipschitz in theta,
          so a cell [x_i,x_{i+1}] x [y_j,y_{j+1}] x [T0,T1] is PROVABLY DISJOINT from F(a) iff
              min over an exact theta grid of f(x_i, y_j, t) - (sqrt2/2)*dtheta/2  >  a .
          G keeps every cell that is NOT provably disjoint, so G contains F.  The kept set is a
          DOWN-set in (x,y) (f nondecreasing), i.e. a staircase; it is stored per theta bin as
          J[i] = the largest kept cell index in column i, and merged losslessly by run length.

  E       COMPLEMENT cover: caselp NoFam boxes covering [0.45, s0-0.45]^2 x [0,90] minus G, each
          one EXACTLY certified disjoint from F_c(a_w) for all four corners c (the property that
          soundness of run B actually needs; it implies E n G_c = empty in the interior).

The theta bins are o3fam's: every edge is a multiple of 1/4 deg (so 90 - edge is exact in binary)
and the bins overlap by 0.5-1 deg so that no verifier box can straddle a bin boundary forever.
Bins are sigma-closed (sigma(T0,T1) = (90-T1, 90-T0)), which makes the family set D4-closed.

All tests are inflated by EPSC = 1e-8 in the centre coordinates (f nondecreasing), so the
1e-9 outward rounding that caselp.make_certificate applies to the emitted NoFam corners cannot
break the certified disjointness.
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np
from corner85 import f_min_max
from caselp92 import NoFam, EPS_ZONE, EPS_TH, t_lo, t_hi

S = Fr("969271/250000")
SF = float(S)
M_LO = Fr(382, 100)
LAM_MAX = S / M_LO                       # 969271/955000
SQ2H = Fr(7072, 10000)                   # >= sqrt(2)/2 = 0.70710678...
LIP = math.sqrt(0.5)
GRID = Fr(2, 100)
XLO = Fr(45, 100)                        # anchored BELOW the admissible centre floor 0.5
EPSC = Fr(1, 10 ** 8)
NTH = 193                                # exact theta grid per bin
CORNERS = ("BL", "BR", "TL", "TR")
# A92 follow-up: cache-format / builder version of the E cover.  1 = the first campaign's ABUTTING
# y-strips (the verifier can never exempt a box that straddles a shared strip edge, and such a box
# sits deep inside E where the measure carries only 1, so it can never be covered either -> run B
# holes on every seam).  2 = the one-cell y-overlap of build().  A cached fam json of version 1
# MUST be rebuilt; get_fam/certify92 refuse to use one.
FAM_BUILD = 2
TH_BINS = [(0.0, 14.75), (13.75, 28.75), (27.75, 41.75), (40.75, 49.25),
           (48.25, 62.25), (61.25, 76.25), (75.25, 90.0)]


def a_w(delta):
    d = Fr(delta).limit_denominator(10 ** 6)
    v = LAM_MAX * (1 - d) + (LAM_MAX - 1) * SQ2H
    return Fr(math.ceil(v * 10 ** 5), 10 ** 5)


def sigma_bin(b):
    return (90.0 - b[1], 90.0 - b[0])


_TG = {}


def theta_grid(b):
    """(t-grid, Lipschitz pad, t0, t1) for a bin; t0/t1 are EXACTLY the interval that
    caselp.make_certificate will write into the certificate (t_lo/t_hi of the bin edges)."""
    if b in _TG:
        return _TG[b]
    T0, T1 = b
    t0 = t_lo(T0)
    t1 = t_hi(T1)
    if t1 > 1:
        t1 = Fr(1)
    ts = [t0 + (t1 - t0) * Fr(i, NTH - 1) for i in range(NTH)]
    dth = 2.0 * (math.atan(float(t1)) - math.atan(float(t0))) / (NTH - 1)
    pad = Fr(math.ceil(LIP * dth / 2 * 10 ** 9) + 1, 10 ** 9)
    _TG[b] = (ts, pad, t0, t1)
    return _TG[b]


def disjoint(x, y, b, a):
    """EXACT: True iff every pose with corner-frame centre >= (x,y) and theta in bin b has
    f > a, i.e. is provably outside F(a).  (min over the bin of f >= min_i f - pad.)"""
    ts, pad, _, _ = theta_grid(b)
    thr = a + pad
    xx, yy = x - EPSC, y - EPSC
    for t in ts:
        if f_min_max(xx, yy, t) <= thr:
            return False
    return True


def grids(a):
    hi = a + Fr(3, 4)                    # a pose meeting [0,a]^2 has centre coords <= a + sqrt2/2
    n = int(math.ceil(float((hi - XLO) / GRID)))
    xs = [XLO + GRID * k for k in range(n + 1)]
    return xs, list(xs)


def staircase(b, a, xs, ys):
    """J[i] = largest cell index j with cell (i,j) NOT provably disjoint from F(a); -1 if none."""
    NX, NY = len(xs) - 1, len(ys) - 1
    J, j = [], NY - 1
    for i in range(NX):
        while j >= 0 and disjoint(xs[i], ys[j], b, a):
            j -= 1
        J.append(j)
    return J


def _bfun(J, xs, NY):
    """B[j] = xs[max{i : J[i] >= j} + 1] (or xs[0]): the exact x-reach of the staircase on the
    open strip (ys[j], ys[j+1]].  Nonincreasing in j."""
    NX = len(J)
    out = []
    for j in range(NY):
        idx = -1
        for i in range(NX):
            if J[i] >= j:
                idx = i
        out.append(xs[idx + 1] if idx >= 0 else xs[0])
    return out


# ---------------------------------------------------------------- the build
def build(delta, verbose=True, log=print):
    a = a_w(delta)
    xs, ys = grids(a)
    NX, NY = len(xs) - 1, len(ys) - 1
    SC = {}
    for b in TH_BINS:
        SC[b] = staircase(b, a, xs, ys)
        assert SC[b][0] <= NY - 2, "y-grid too small for bin %s" % (b,)
        assert SC[b][-1] == -1, "x-grid too small for bin %s" % (b,)
    # ---- G: run-length merged staircase rects per bin (BL frame)
    G_BL = {}
    for b in TH_BINS:
        J = SC[b]
        out, i = [], 0
        while i < NX:
            if J[i] < 0:
                i += 1
                continue
            k = i
            while k + 1 < NX and J[k + 1] == J[i]:
                k += 1
            out.append((xs[i], xs[k + 1], ys[0], ys[J[i] + 1]))
            i = k + 1
        G_BL[b] = out
    n_g_per_corner = sum(len(v) for v in G_BL.values())
    # ---- E: complement strips per bin
    jt = max(max(SC[b]) for b in TH_BINS) + 1
    assert jt <= NY - 1
    B = {b: _bfun(SC[b], xs, NY) for b in TH_BINS}
    E = []
    for b in TH_BINS:
        sb = sigma_bin(b)
        Bb, Bs = B[b], B[sb]
        j = 0
        while j < jt:
            k = j
            while k + 1 < jt and Bb[k + 1] == Bb[j] and Bs[k + 1] == Bs[j]:
                k += 1
            # OVERLAP: extend the strip ONE grid cell further in y.  The verifier can only exempt
            # a box that is inside ONE family, so ABUTTING strips leave an unexemptable seam at
            # every shared edge -- and those seams sit deep inside E where the measure carries
            # only 1, not 1+e, so they cannot be covered either (that is exactly how run B failed
            # in the first campaign: every hole was on a strip seam).  Extending upward keeps the
            # strip's MIN corner unchanged, so the exact F-disjointness certificate is unaffected,
            # and consecutive strips now overlap by a full cell (0.02) > any box that reaches them.
            k2 = min(k + 2, NY)
            x0, x1 = Bb[j], S - Bs[j]
            if x0 < x1:
                E.append((x0, x1, ys[j], ys[k2], b))                      # lower band
                E.append((Bs[j], S - Bb[j], S - ys[k2], S - ys[j], b))    # upper band (reflected)
            j = k + 1
        E.append((XLO, S - XLO, ys[jt], S - ys[jt], b))               # middle band
    # ---- exact certification of every E box against all four corners
    bad = []
    for (x0, x1, y0, y1, b) in E:
        sb = sigma_bin(b)
        ok = (disjoint(x0, y0, b, a) and disjoint(S - x1, y0, sb, a)
              and disjoint(x0, S - y1, sb, a) and disjoint(S - x1, S - y1, b, a))
        if not ok:
            bad.append((float(x0), float(x1), float(y0), float(y1), b))
    if verbose:
        log("  fams: a_w=%s (%.6f) grid %dx%d bins=%d  G/corner=%d  E=%d  E-sound=%s"
            % (str(a), float(a), NX, NY, len(TH_BINS), n_g_per_corner, len(E), not bad))
    assert not bad, "UNSOUND E boxes (not provably disjoint from F): %s" % bad[:3]
    return dict(delta=float(delta), a=a, xs=xs, ys=ys, SC=SC, G_BL=G_BL, E=E,
                NX=NX, NY=NY, jt=jt, n_g_per_corner=n_g_per_corner, n_e=len(E),
                fam_build=FAM_BUILD)


# ---------------------------------------------------------------- per-corner materialisation
def corner_rects(fam, corner):
    """G_c as float (x0,x1,y0,y1,T0,T1) tuples, o3fam.corner_fams-style D4 mapping."""
    out = []
    for b, rects in fam["G_BL"].items():
        T0, T1 = b
        s0, s1 = sigma_bin(b)
        for (x0, x1, y0, y1) in rects:
            U0, U1, V0, V1 = float(x0), float(x1), float(y0), float(y1)
            if corner == "BL":
                out.append((U0, U1, V0, V1, T0, T1))
            elif corner == "BR":
                out.append((SF - U1, SF - U0, V0, V1, s0, s1))
            elif corner == "TL":
                out.append((U0, U1, SF - V1, SF - V0, s0, s1))
            else:
                out.append((SF - U1, SF - U0, SF - V1, SF - V0, T0, T1))
    return out


def d4_closure_defect(fam):
    """max coordinate mismatch when the four corner rect lists are matched to each other under D4."""
    ref = sorted(corner_rects(fam, "BL"))
    d = 0.0
    for c in ("BR", "TL", "TR"):
        oth = corner_rects(fam, c)
        back = []
        for (x0, x1, y0, y1, T0, T1) in oth:
            if c == "BR":
                back.append((SF - x1, SF - x0, y0, y1, 90.0 - T1, 90.0 - T0))
            elif c == "TL":
                back.append((x0, x1, SF - y1, SF - y0, 90.0 - T1, 90.0 - T0))
            else:
                back.append((SF - x1, SF - x0, SF - y1, SF - y0, T0, T1))
        back.sort()
        for p, q in zip(ref, back):
            d = max(d, max(abs(u - v) for u, v in zip(p, q)))
    return d


def nofams_E(fam):
    """the complement cover as caselp NoFam objects (run B's hypotheses)."""
    out = []
    for (x0, x1, y0, y1, b) in fam["E"]:
        out.append(NoFam(float(x0), float(x1), float(y0), float(y1), [(b[0], b[1])]))
    return out


# ---------------------------------------------------------------- the LP row rhs
class GTest:
    """membership in the DILATED G (centre by EPS_ZONE, theta by EPS_TH), evaluated in each
    corner frame -- hence exactly D4-invariant.  Conservative: a pose counts as in G unless its
    centre is outside every G-rect of its corner by EPS_ZONE or its theta outside the bin by
    EPS_TH, i.e. MORE rows at 1+e, never fewer."""

    def __init__(self, fam, eps_zone=EPS_ZONE, eps_th=EPS_TH):
        self.xs = np.array([float(x) for x in fam["xs"]])
        ys = fam["ys"]
        self.NX = fam["NX"]
        self.ytop = {b: np.array([float(ys[J + 1]) if J >= 0 else -1e18 for J in fam["SC"][b]])
                     for b in fam["SC"]}
        self.bins = list(fam["SC"])
        self.ez, self.et = eps_zone, eps_th

    def __call__(self, C, th_deg, extra=0.0):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        out = np.zeros(len(C), dtype=bool)
        th = th_deg % 90.0
        ez = self.ez + extra
        for corner in CORNERS:
            u = C[:, 0] if corner in ("BL", "TL") else SF - C[:, 0]
            v = C[:, 1] if corner in ("BL", "BR") else SF - C[:, 1]
            thc = th if corner in ("BL", "TR") else 90.0 - th
            uu, vv = u - ez, v - ez
            # the cell of (u - eps); ytop is nonincreasing in i, so the LOWER index is the
            # conservative (largest-reach) choice for the dilated rect union
            i0 = np.clip(np.searchsorted(self.xs, uu, side="right") - 1, 0, self.NX - 1)
            inx = uu <= self.xs[-1]
            for b in self.bins:
                if not (b[0] - self.et <= thc <= b[1] + self.et):
                    continue
                out |= inx & (vv <= self.ytop[b][i0])
        return out

    def cells(self, cx, cy, tol, th_deg):
        """does the arrangement cell (back-rotated centre (cx,cy), half-diagonal tol) meet the
        dilated G?  Used by lpbox92.RHS_CELL to restrict the widened-threshold oracle pass."""
        return self(np.stack([np.asarray(cx, float), np.asarray(cy, float)], 1), th_deg,
                    extra=np.asarray(tol, float))


# Dilation of G used by the LP row rhs.  The spec's EPS_ZONE = 2e-3 / EPS_TH = 0.3 deg is the
# MINIMUM (conservative direction: more rows at 1+e, never fewer).  We use one grid cell in the
# centre and 1 deg in theta instead, because the exact verifier resolves a box straddling the
# boundary of the complement cover E only when the WHOLE box carries mass >= 1+e, i.e. only when
# the box is smaller than the dilation; 0.02 keeps that at ~8 bisections per axis instead of ~11.
EPS_ZONE_G = 0.02
EPS_TH_G = 1.0


def rhs_mult(fam, e, eps_zone=EPS_ZONE_G, eps_th=EPS_TH_G):
    """(RHS_MULT, RHS_MAX, RHS_CELL) for lpbox92, at crowd weight e."""
    g = GTest(fam, eps_zone=eps_zone, eps_th=eps_th)
    ef = float(e)

    def f(C, th_deg):
        return 1.0 + ef * g(C, th_deg).astype(float)
    return f, 1.0 + ef, g.cells


def install_rhs(fam, e, lp):
    """set the three A92 hooks on the lpbox92 module `lp` (or clear them if e is None)."""
    if e is None:
        lp.RHS_MULT, lp.RHS_MAX, lp.RHS_CELL = None, 1.0, None
        return 1.0
    m, mx, ck = rhs_mult(fam, e)
    lp.RHS_MULT, lp.RHS_MAX, lp.RHS_CELL = m, mx, ck
    return mx


# ---------------------------------------------------------------- diagnostics
def overshoot(fam, n=20000, seed=20926):
    """exact-sampling estimate of vol(G_BL)/vol(F_BL(a_w)) - 1 over [0.45, xmax]^2 x [0,90]."""
    import random
    rnd = random.Random(seed)
    a = fam["a"]
    xs, ys, SC = fam["xs"], fam["ys"], fam["SC"]
    xmax = float(xs[-1])
    lo = float(xs[0])
    ytop = {b: [float(ys[J + 1]) if J >= 0 else -1e18 for J in SC[b]] for b in SC}
    xf = [float(x) for x in xs]
    nF = nG = nFnotG = 0
    for _ in range(n):
        u = lo + (xmax - lo) * rnd.random()
        v = lo + (xmax - lo) * rnd.random()
        t = Fr(rnd.randrange(10 ** 9), 10 ** 9)
        thd = math.degrees(2.0 * math.atan(float(t)))
        uq = Fr(round(u * 10 ** 9), 10 ** 9)
        vq = Fr(round(v * 10 ** 9), 10 ** 9)
        inF = f_min_max(uq, vq, t) <= a
        inG = False
        i = min(max(int((u - lo) / float(GRID)), 0), fam["NX"] - 1)
        while i > 0 and xf[i] > u:
            i -= 1
        for b in SC:
            if b[0] <= thd <= b[1] and v <= ytop[b][i]:
                inG = True
                break
        nF += inF
        nG += inG
        nFnotG += (inF and not inG)
    return dict(n=n, n_in_F=nF, n_in_G=nG, n_in_F_not_G=nFnotG,
                overshoot=(nG / nF - 1.0) if nF else None)


def image_crowd_counts(a):
    """per-image, per-corner count of Trump placements with f_c <= a (exact)."""
    import class85 as K85
    C = K85.load_class("k0_00", K85.DELTA_PIN)
    rows = []
    for im in C["images"]:
        row = dict(image=im["key"])
        for c in CORNERS:
            cnt, fs = 0, []
            for (x, y, th) in im["placements"]:
                xq = Fr(round(x * 10 ** 12), 10 ** 12)
                yq = Fr(round(y * 10 ** 12), 10 ** 12)
                t = Fr(round(math.tan(th / 2.0) * 2 ** 30), 2 ** 30)
                u = (S - xq) if c in ("BR", "TR") else xq
                v = (S - yq) if c in ("TL", "TR") else yq
                tt = t if c in ("BL", "TR") else (1 - t) / (1 + t)
                f = f_min_max(u, v, tt)
                fs.append(float(f))
                cnt += (f <= a)
            row[c] = cnt
            row[c + "_fmin"] = round(min(fs), 6)
        row["realises"] = all(row[c] >= 2 for c in CORNERS)
        rows.append(row)
    return rows


# ---------------------------------------------------------------- persistence
def to_json(fam):
    return dict(delta=fam["delta"], a=str(fam["a"]), a_float=float(fam["a"]),
                fam_build=fam.get("fam_build", FAM_BUILD),
                lambda_max=str(LAM_MAX), s=str(S),
                xs=[str(x) for x in fam["xs"]], ys=[str(y) for y in fam["ys"]],
                SC={"%g_%g" % b: fam["SC"][b] for b in fam["SC"]},
                NX=fam["NX"], NY=fam["NY"], jt=fam["jt"],
                n_g_per_corner=fam["n_g_per_corner"], n_e=fam["n_e"],
                G_BL={"%g_%g" % b: [[str(z) for z in r] for r in fam["G_BL"][b]] for b in fam["G_BL"]},
                E=[[str(x0), str(x1), str(y0), str(y1), b[0], b[1]] for (x0, x1, y0, y1, b) in fam["E"]])


def from_json(d):
    def kb(k):
        p = k.split("_")
        return (float(p[0]), float(p[1]))
    return dict(delta=d["delta"], a=Fr(d["a"]), xs=[Fr(x) for x in d["xs"]],
                ys=[Fr(y) for y in d["ys"]], SC={kb(k): v for k, v in d["SC"].items()},
                G_BL={kb(k): [tuple(Fr(z) for z in r) for r in v] for k, v in d["G_BL"].items()},
                E=[(Fr(r[0]), Fr(r[1]), Fr(r[2]), Fr(r[3]), (r[4], r[5])) for r in d["E"]],
                NX=d["NX"], NY=d["NY"], jt=d["jt"], fam_build=d.get("fam_build", 1),
                n_g_per_corner=d["n_g_per_corner"], n_e=d["n_e"])


if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--deltas", default="0.3,0.25,0.2,0.15,0.1,0.05")
    ap.add_argument("--cov", type=int, default=20000)
    ap.add_argument("--out", default="crowd92_fams.json")
    A = ap.parse_args()
    res = []
    for d in [float(x) for x in A.deltas.split(",")]:
        t0 = time.time()
        fam = build(d)
        ov = overshoot(fam, n=A.cov)
        can = image_crowd_counts(fam["a"])
        d4 = d4_closure_defect(fam)
        print("delta=%.3g a_w=%s (%.6f) G/corner=%d E=%d overshoot=%.4f F-not-G=%d d4=%.2e "
              "canary_realising=%d  %.0fs"
              % (d, str(fam["a"]), float(fam["a"]), fam["n_g_per_corner"], fam["n_e"],
                 ov["overshoot"], ov["n_in_F_not_G"], d4,
                 sum(1 for r in can if r["realises"]), time.time() - t0), flush=True)
        j = to_json(fam)
        j.update(overshoot=ov, canary=can, d4_defect=d4)
        res.append(j)
    json.dump(dict(s=str(S), lambda_max=str(LAM_MAX), fams=res),
              open(os.path.join(BASE, "results", A.out), "w"))
