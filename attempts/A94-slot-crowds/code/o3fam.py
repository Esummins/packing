"""A89-O3 -- the SHALLOW-corner NO-family builder (Lemma ID's exempt boxes).

Object.  For a corner c and a >= 0 let
    R_c(a) := {(c_Q, theta) : int Q(c_Q,theta) meets the open box (0,a)^2 in c's frame}.
Lemma ID's SHALLOW(delta) hypothesis at side m says exactly "no square of the packing has a
pose in R_c(1-delta)".  A caselp NoFam is a rect x union-of-theta-intervals, so a SOUND
representation of the hypothesis is any family F with F subset R_c(a): "no square has a pose
in F" is then implied.  This module builds a small union of such families.

Exactness.  f(u,v,theta) := min over Q(u,v,theta) of max(x,y) (corner85.f_min_max, exact in
Fractions from t = tan(theta/2)).  Q meets the open box (0,a)^2 iff f < a (the "iff" uses
Q subset [0,m]^2, so every point of int Q has both coordinates > 0).  f is
  * nondecreasing in u and in v separately (max(p_x+d, p_y) >= max(p_x,p_y) for d >= 0), so
    the max of f over a rect [u0,u1]x[v0,v1] is attained at (u1,v1);
  * (sqrt(2)/2)-Lipschitz in theta (radians): rotating Q moves each of its points by at most
    (sqrt2/2)|dtheta| and max(x,y) is 1-Lipschitz in the sup norm.
Hence  F = [0.5,U] x [0.5,V] x [T0,T1]  satisfies  F subset R_c(a)  as soon as
    max_i f(U, V, t_i) + (sqrt2/2)*dtheta/2  <  a
over a grid t_i of [t(T0), t(T1)] of step dtheta (radians).  That is the certified test below
(`fam_ok`), evaluated in exact Fractions.

Window validity (Lemma B-NO / K0-WIDEN).  A certificate at s0 must discharge every side
m in [3.82, s0].  With lambda = s0/m in [1, lambda_max], lambda_max = s0/3.82 = 969271/955000
= 1.014943455..., the transported hypothesis uses the CONTRACTED box
    a_win(delta) = (1-delta)/lambda_max
(A63 Lemma B-NO: "occupancy transfers with the zone contracted 1/lambda").  a_win <= 1-delta,
so a_win is also sound under the centre-dilation convention (the dilated centre lambda*c is
further from the corner than c, so a pose meeting (0,a_win)^2 after dilation came from a pose
meeting (0,a_win)^2 <= (0,1-delta)^2 before).  Runs are done at a = a_win (window-valid) and,
for the gap, at a = 1-delta (s0 only).

Anchoring at 0.5.  Every rect is anchored at the DOMAIN boundary of admissible centres
(x0 = y0 = 0.5 in the corner frame), where caselp.NoFam.inside_many applies NO safety margin;
only the outer edges U, V pay the EPS_ZONE = 2e-3 erosion.  Theta intervals are widened by
PAD_TH on interior ends so that after the EPS_TH = 0.3 deg erosion the eroded intervals still
tile [0,90].
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from corner85 import f_min_max, T_EDGES
from caselp import NoFam, EPS_ZONE, EPS_TH, t_lo, t_hi

S = Fr("969271/250000")
SF = float(S)
M_LO = Fr(382, 100)                       # 3.82, the window floor
LAM_MAX = S / M_LO                        # 969271/955000
LIP = math.sqrt(0.5)
PAD_TH = 0.35                             # deg, > EPS_TH/2 + slack
NTH_CERT = 257                            # exact theta grid for the certified test
NTH_FLOAT = 257                           # float theta grid for the staircase search
CORNERS = ("BL", "BR", "TL", "TR")


def a_win(delta):
    return (Fr(1) - Fr(delta).limit_denominator(10 ** 6)) / LAM_MAX


def a_s0(delta):
    return Fr(1) - Fr(delta).limit_denominator(10 ** 6)


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


# ---------------------------------------------------------------- float f (search only)
def f_float(u, v, th_deg):
    c, s = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
    e1 = (0.5 * c, 0.5 * s)
    e2 = (-0.5 * s, 0.5 * c)
    V = [(u + a * e1[0] + b * e2[0], v + a * e1[1] + b * e2[1])
         for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    best = min(max(x, y) for (x, y) in V)
    for i in range(4):
        px, py = V[i]
        qx, qy = V[(i + 1) % 4]
        dx, dy = qx - px, qy - py
        if abs(dx - dy) < 1e-15:
            continue
        t = (py - px) / (dx - dy)
        if 0.0 <= t <= 1.0:
            best = min(best, px + t * dx)
    return best


def fmax_float(u, v, t0, t1, n=NTH_FLOAT):
    A, B = deg_of_t(t0), deg_of_t(t1)
    return max(f_float(u, v, A + (B - A) * i / (n - 1.0)) for i in range(n))


def theta_slack(T0, T1):
    """the two Lipschitz pads (float search grid + exact certificate grid) of a bin."""
    rad = math.radians(T1 - T0)
    return LIP * rad / (NTH_FLOAT - 1) / 2.0 + LIP * rad / (NTH_CERT - 1) / 2.0 + 1e-7


# ---------------------------------------------------------------- certified test
def fmax_exact_ub(U, V, t0, t1, n=NTH_CERT):
    """rigorous upper bound on max over theta in [t0,t1] of f(U,V,theta)."""
    Uq, Vq = Fr(U).limit_denominator(10 ** 9), Fr(V).limit_denominator(10 ** 9)
    best = None
    for i in range(n):
        t = t0 + (t1 - t0) * Fr(i, n - 1)
        val = f_min_max(Uq, Vq, t)
        if best is None or val > best:
            best = val
    dth = 2.0 * (math.atan(float(t1)) - math.atan(float(t0))) / (n - 1)
    return float(best) + LIP * dth / 2.0


def fam_ok(U, V, T0, T1, a):
    """certified: every pose in [0.5,U]x[0.5,V]x[T0,T1] meets the open box (0,a)^2."""
    t0, t1 = t_lo(T0), t_hi(T1)
    if t1 > 1:
        t1 = Fr(1)
    ub = fmax_exact_ub(U, V, t0, t1)
    return ub < float(a), ub


# ---------------------------------------------------------------- staircase per theta bin
def U_of_v(v, T0, T1, a, hi=3.0):
    """largest U (float, conservative) with fmax_float(U, v, bin) < a - (Lipschitz slack)."""
    af = float(a) - theta_slack(T0, T1)
    if fmax_float(0.5, v, t_lo(T0), t_hi(T1)) >= af:
        return None
    lo, up = 0.5, hi
    if fmax_float(up, v, t_lo(T0), t_hi(T1)) < af:
        return up
    for _ in range(50):
        mid = 0.5 * (lo + up)
        if fmax_float(mid, v, t_lo(T0), t_hi(T1)) < af:
            lo = mid
        else:
            up = mid
    return lo


def staircase(T0, T1, a, nsteps=10, snap=10 ** 6):
    """rects [0.5,U_j] x [0.5,V_j] covering the down-set {fmax over the bin < a}."""
    v_top = U_of_v(0.5, T0, T1, a)          # by symmetry of the roles, the reach in v at u=0.5
    if v_top is None:
        return []
    lo, up = 0.5, 3.0
    # largest v with U_of_v(v) defined
    if U_of_v(up, T0, T1, a) is not None:
        v_max = up
    else:
        for _ in range(40):
            mid = 0.5 * (lo + up)
            if U_of_v(mid, T0, T1, a) is not None:
                lo = mid
            else:
                up = mid
        v_max = lo
    out = []
    for j in range(nsteps):
        v = 0.5 + (v_max - 0.5) * (j + 1) / float(nsteps)
        U = U_of_v(v, T0, T1, a)
        if U is None or U <= 0.5 + 1e-9:
            continue
        Uq = math.floor(U * snap) / snap
        Vq = math.floor(v * snap) / snap
        if Uq <= 0.5 or Vq <= 0.5:
            continue
        out.append((Uq, Vq))
    # drop dominated rects
    out.sort(key=lambda r: (-r[0], r[1]))
    keep = []
    for (U, V) in out:
        if any(U <= u2 + 1e-12 and V <= v2 + 1e-12 for (u2, v2) in keep):
            continue
        keep.append((U, V))
    return keep


# Theta bins.  EVERY edge is a multiple of 1/4 degree, so 90.0 - edge is EXACT in binary
# floating point; that is what makes the family set bit-exactly D4-closed (caselp's
# d4_rect_images reflects theta by the raw float 90 - b, and Hyp.is_symmetric_D4 matches the
# theta tuples with ==, not to a tolerance).  The edge set 0, 14.25, 28.25, 41.25, 48.75,
# 61.75, 75.75, 90 mirrors corner85's sigma-closed T_EDGES and is symmetric about 45; the bins
# are widened by 0.5 deg (> EPS_TH = 0.3) on interior ends so the ERODED bins still tile [0,90].
TH_BINS = [(0.0, 14.75), (13.75, 28.75), (27.75, 41.75), (40.75, 49.25),
           (48.25, 62.25), (61.25, 76.25), (75.25, 90.0)]


def bins(pad=PAD_TH):
    return list(TH_BINS)


def sigma_bin(b):
    return (90.0 - b[1], 90.0 - b[0])


def build_bl(a, nsteps=10, verbose=True):
    """the sigma-closed BL family list: [(U, V, (T0, T1)), ...]."""
    B = bins()
    raw = {}
    for b in B:
        raw[b] = staircase(b[0], b[1], a, nsteps=nsteps)
    fams = []
    for b in B:
        sb = sigma_bin(b)
        base = list(raw[b])
        mirror = [(V, U) for (U, V) in raw.get(sb, [])]
        seen = set()
        for (U, V) in base + mirror:
            k = (round(U, 6), round(V, 6))
            if k in seen:
                continue
            seen.add(k)
            fams.append((k[0], k[1], b))
    return fams


def certify_bl(fams, a):
    """exact check of every family; returns (all_ok, rows)."""
    rows, ok = [], True
    for (U, V, (T0, T1)) in fams:
        good, ub = fam_ok(U, V, T0, T1, a)
        ok = ok and good
        rows.append(dict(U=U, V=V, T0=T0, T1=T1, fmax_ub=ub, a=float(a),
                         margin=float(a) - ub, ok=bool(good)))
    return ok, rows


# ---------------------------------------------------------------- corner placement
def corner_fams(fams, corner):
    """map BL families to `corner`; returns list of NoFam."""
    out = []
    for (U, V, (T0, T1)) in fams:
        if corner == "BL":
            r = (0.5, U, 0.5, V)
            th = [(T0, T1)]
        elif corner == "BR":
            r = (SF - U, SF - 0.5, 0.5, V)
            th = [(90.0 - T1, 90.0 - T0)]
        elif corner == "TL":
            r = (0.5, U, SF - V, SF - 0.5)
            th = [(90.0 - T1, 90.0 - T0)]
        else:
            r = (SF - U, SF - 0.5, SF - V, SF - 0.5)
            th = [(T0, T1)]
        out.append(NoFam(r[0], r[1], r[2], r[3], th))
    return out


def nofams_for(pattern, fams):
    out = []
    for c in pattern:
        out += corner_fams(fams, c)
    return out


# ---------------------------------------------------------------- coverage by sampling
def coverage(fams, a, n=20000, seed=12345, eroded=True):
    """fraction of R_BL(a) covered by the (eroded) family union, by uniform sampling of the
    pose box [0.5, 0.5+RCH] x [0.5, 0.5+RCH] x t in [0,1]."""
    import random
    rnd = random.Random(seed)
    RCH = 2.2
    inR = 0
    cov = 0
    af = float(a)
    ez = EPS_ZONE if eroded else 0.0
    et = EPS_TH if eroded else 0.0
    for _ in range(n):
        u = 0.5 + RCH * rnd.random()
        v = 0.5 + RCH * rnd.random()
        t = rnd.random()
        th = deg_of_t(t)
        if f_float(u, v, th) >= af:
            continue
        inR += 1
        hit = False
        for (U, V, (T0, T1)) in fams:
            lo = T0 + (et if T0 > 1e-9 else 0.0)
            hi = T1 - (et if T1 < 90 - 1e-9 else 0.0)
            if not (lo <= th <= hi):
                continue
            if u <= U - ez and v <= V - ez:
                hit = True
                break
        cov += 1 if hit else 0
    return dict(n_sampled=n, n_in_R=inR, n_covered=cov,
                fraction=(cov / inR if inR else None), eroded=bool(eroded),
                rect=[0.5, 0.5 + RCH])


def report(delta, window=True, nsteps=10, cov_n=20000):
    a = a_win(delta) if window else a_s0(delta)
    fams = build_bl(a, nsteps=nsteps)
    ok, rows = certify_bl(fams, a)
    cov = coverage(fams, a, n=cov_n, eroded=True)
    cov0 = coverage(fams, a, n=cov_n, eroded=False)
    return dict(delta=delta, window=bool(window), a=float(a), a_rat=str(a),
                lambda_max=str(LAM_MAX), lambda_max_float=float(LAM_MAX),
                n_fams_BL=len(fams), all_sound=bool(ok), fams=rows,
                coverage_eroded=cov, coverage_raw=cov0)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--deltas", default="0.3,0.1,0.05")
    ap.add_argument("--nsteps", type=int, default=10)
    ap.add_argument("--cov", type=int, default=20000)
    ap.add_argument("--out", default="o3_fams.json")
    A = ap.parse_args()
    res = []
    for d in [float(x) for x in A.deltas.split(",")]:
        for w in (True, False):
            r = report(d, window=w, nsteps=A.nsteps, cov_n=A.cov)
            res.append(r)
            print("delta=%.3g window=%d a=%.6f nfam_BL=%d sound=%s cov_eroded=%.4f cov_raw=%.4f"
                  % (d, w, r["a"], r["n_fams_BL"], r["all_sound"],
                     r["coverage_eroded"]["fraction"], r["coverage_raw"]["fraction"]), flush=True)
    json.dump(dict(s=str(S), lambda_max=str(LAM_MAX), reports=res),
              open(os.path.join(BASE, "results", A.out), "w"), indent=1)
