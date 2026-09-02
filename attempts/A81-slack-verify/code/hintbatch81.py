#!/usr/bin/env python
# -*- coding: ascii -*-
"""hintbatch81.py -- A81 level-synchronous (batched, vectorised) float B&B that builds a
COMPLETE spec-s4 hint tree for a pair-certificate-v1/v2/v2.1 file, and censuses its leaves.

Copy of A77 hintbatch.py extended to beta > 0 certificates (class boxes -> the U bonus of
spec 3.7) and to the v2.1 "urow" discount block (per-image gamma credited when the two
factors are pinned into two DIFFERENT slots of the same image).  The beta = 0 / no-urow
path is byte-for-byte the A77 behaviour (thresholds collapse to the constant 1).

Leaf census (what the verifier will see at each hint leaf, which is emitted as null so
the verifier's own clause table discharges it in one step):
  COV   float-certain mass >= 1 + beta*U - sum_g gamma_g*bzc_g   (integer-exact sums)
  VAC   VACUOUS-CONTAIN (float mirror of spec 3.3 1b) or an empty admissibility clip
  EX    a core certainly overlapped (float mirror of the verifier's own pre-screen)
  ND    NONDISJOINT (float mirror of nondisjoint_certain)
  HOLE  float-possible mass < the LOW target AND a float-admissible interior-disjoint
        placement pair inside the box collects < 1 + beta*m2 - sum_g gamma_g*bz_g
  OPEN  undecided at the depth cap / node budget / degenerate widths (verifier residue)
  AMB   possible < low target but no admissible probe pair found at the depth cap

Everything here is heuristic; the frozen verifiers re-prove every leaf.  Hint cuts are
short dyadic rationals strictly interior to the (float-mirrored, clipped) interval.

Usage: python hintbatch81.py CERT.json OUT.json [--cap N/root] [--maxdepth D] [--jobs J]
                             [--holes HOLES.json] [--chunk C]
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import math
import sys
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A73-pair-v2", "code"))
import verify_pair2 as vp            # frozen reference, import-only (roots/clip)

MG = 1e-9                            # certain-slack margin
ETA0 = 0.02                          # soft-mass grading scale
TSCALE = 0.7                         # t width weight in the tie-break
MILLION = 10 ** 6
K_VAC, K_EX, K_ND, K_COV, K_HOLE, K_OPEN, K_AMB, K_SPLIT = 1, 2, 3, 4, 5, 6, 7, 0
KNAMES = {K_SPLIT: "split", K_VAC: "vac", K_EX: "ex", K_ND: "nd", K_COV: "cov",
          K_HOLE: "hole", K_OPEN: "open", K_AMB: "amb"}

# float mirrors of the frozen exact brackets (verify_pair2 lines 27-29)
TSTAR_LO_F = 408.0 / 985.0
TSTAR_HI_F = 5741.0 / 13860.0
W_HI_GLOBAL_F = 19601.0 / 13860.0

TOL_SEP = 1e-9      # separation tests: err toward "possibly meets" (bigger U)
TOL_CM = 1e-9       # certain-meet tests: err toward "not certainly met" (smaller M2LO)
TOL_ZONE = 1e-12    # zone containment: err toward "not contained" (smaller discount)


# ------------------------------------------------------------------ kernels
def _qmin(A, B, C, t0, t1):
    f0 = A * t0 * t0 + B * t0 + C
    f1 = A * t1 * t1 + B * t1 + C
    m = np.minimum(f0, f1)
    inner = (A > 0) & (2 * A * t0 + B < 0) & (2 * A * t1 + B > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = C - B * B / (4 * np.where(A > 0, A, 1.0))
    return np.where(inner, np.minimum(m, v), m)


def _qmax(A, B, C, t0, t1):
    f0 = A * t0 * t0 + B * t0 + C
    f1 = A * t1 * t1 + B * t1 + C
    m = np.maximum(f0, f1)
    inner = (A < 0) & (2 * A * t0 + B > 0) & (2 * A * t1 + B < 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = C - B * B / (4 * np.where(A < 0, A, -1.0))
    return np.where(inner, np.maximum(m, v), m)


def _qnonneg(A, B, C, t0, t1):
    f0 = A * t0 * t0 + B * t0 + C
    f1 = A * t1 * t1 + B * t1 + C
    ok = (f0 >= 0) & (f1 >= 0)
    inner = (A > 0) & (2 * A * t0 + B < 0) & (2 * A * t1 + B > 0)
    return ok & (~inner | (4 * A * C - B * B >= 0))


def slack(F, PX, PY):
    """(n,M): min over the 4 corner-pinned membership quadratics (Lemma M, float)."""
    t0, t1 = F[:, 0:1], F[:, 1:2]
    x0, x1, y0, y1 = F[:, 2:3], F[:, 3:4], F[:, 4:5], F[:, 5:6]
    px, py = PX[None, :], PY[None, :]
    dx, dy = px - x0, py - y0
    s = _qmin(0.5 + dx, -2 * dy, 0.5 - dx, t0, t1)
    dx, dy = px - x1, py - y1
    s = np.minimum(s, _qmin(0.5 - dx, 2 * dy, 0.5 + dx, t0, t1))
    dx, dy = px - x1, py - y0
    s = np.minimum(s, _qmin(0.5 + dy, 2 * dx, 0.5 - dy, t0, t1))
    dx, dy = px - x0, py - y1
    s = np.minimum(s, _qmin(0.5 - dy, -2 * dx, 0.5 + dy, t0, t1))
    return s


def possible(F, PX, PY):
    """(n,M) bool: p may lie in SOME square of the box (opposite-corner pins)."""
    t0, t1 = F[:, 0:1], F[:, 1:2]
    x0, x1, y0, y1 = F[:, 2:3], F[:, 3:4], F[:, 4:5], F[:, 5:6]
    px, py = PX[None, :], PY[None, :]
    dx, dy = px - x1, py - y1
    ok = _qmax(0.5 + dx, -2 * dy, 0.5 - dx, t0, t1) >= -1e-12
    dx, dy = px - x0, py - y0
    ok &= _qmax(0.5 - dx, 2 * dy, 0.5 + dx, t0, t1) >= -1e-12
    dx, dy = px - x0, py - y1
    ok &= _qmax(0.5 + dy, 2 * dx, 0.5 - dy, t0, t1) >= -1e-12
    dx, dy = px - x1, py - y0
    ok &= _qmax(0.5 - dy, -2 * dx, 0.5 + dy, t0, t1) >= -1e-12
    return ok


def _exc_quads(F, kx, ky, a):
    """the 8 corner-pinned overlap quadratics of the v1 exemption pre-screen."""
    x0, x1, y0, y1 = F[:, 2], F[:, 3], F[:, 4], F[:, 5]
    return ((a - (x1 - kx) - 0.5, 1.0, a - (x1 - kx) + 0.5),
            (a + (x0 - kx) - 0.5, 1.0, a + (x0 - kx) + 0.5),
            (a - (y1 - ky) - 0.5, 1.0, a - (y1 - ky) + 0.5),
            (a + (y0 - ky) - 0.5, 1.0, a + (y0 - ky) + 0.5),
            (0.5 - a + (x1 - kx), 2 * a - 2 * (y1 - ky), 0.5 + a - (x1 - kx)),
            (0.5 - a - (x0 - kx), 2 * a + 2 * (y0 - ky), 0.5 + a + (x0 - kx)),
            (0.5 - a + (y1 - ky), 2 * a + 2 * (x0 - kx), 0.5 + a - (y1 - ky)),
            (0.5 - a - (y0 - ky), 2 * a - 2 * (x1 - kx), 0.5 + a + (y0 - ky)))


def exempt(F, cores):
    """(n,) bool: some core certainly overlapped by every square of F (float _exc_f)."""
    t0, t1, x0, x1, y0, y1 = (F[:, i] for i in range(6))
    out = np.zeros(len(F), dtype=bool)
    for (kx, ky, a) in cores:
        ok = np.ones(len(F), dtype=bool)
        for (A, B, C) in ((a - (x1 - kx) - 0.5, 1.0, a - (x1 - kx) + 0.5),
                          (a + (x0 - kx) - 0.5, 1.0, a + (x0 - kx) + 0.5),
                          (a - (y1 - ky) - 0.5, 1.0, a - (y1 - ky) + 0.5),
                          (a + (y0 - ky) - 0.5, 1.0, a + (y0 - ky) + 0.5),
                          (0.5 - a + (x1 - kx), 2 * a - 2 * (y1 - ky), 0.5 + a - (x1 - kx)),
                          (0.5 - a - (x0 - kx), 2 * a + 2 * (y0 - ky), 0.5 + a + (x0 - kx)),
                          (0.5 - a + (y1 - ky), 2 * a + 2 * (x0 - kx), 0.5 + a - (y1 - ky)),
                          (0.5 - a - (y0 - ky), 2 * a - 2 * (x1 - kx), 0.5 + a + (y0 - ky))):
            ok &= _qnonneg(A, np.broadcast_to(B, ok.shape) if np.isscalar(B) else B,
                           C, t0, t1)
        out |= ok
    return out


def certain_meets_mat(F, boxes, mg=TOL_CM):
    """(n,m) bool: class box j certainly overlapped by EVERY square of factor i.

    Same 8 quadratics as exempt() with the core half-side a replaced by the class-box
    half-side h; the margin mg makes 'certainly met' strictly harder in float, so the
    count is a lower bound on the exact predicate (conservative for M2LO)."""
    n = len(F)
    out = np.zeros((n, len(boxes)), dtype=bool)
    if not len(boxes):
        return out
    t0, t1 = F[:, 0], F[:, 1]
    for bi, (bx, by, h) in enumerate(boxes):
        ok = np.ones(n, dtype=bool)
        for (A, B, C) in _exc_quads(F, bx, by, h):
            ok &= _qnonneg(A, np.broadcast_to(B, ok.shape) if np.isscalar(B) else B,
                           C - mg, t0, t1)
        out[:, bi] = ok
    return out


def certain_meets_count(F, boxes, mg=TOL_CM):
    """(n,) int: how many class boxes are certainly met by every square of factor i."""
    return certain_meets_mat(F, boxes, mg).sum(axis=1).astype(np.int64)


def vac_contain(F, s):
    t0, t1, x0, x1, y0, y1 = (F[:, i] for i in range(6))

    def side(v):
        A, C = v + 0.5, v - 0.5
        return (A * t0 * t0 - t0 + C < 0) & (A * t1 * t1 - t1 + C < 0)
    return side(x1) | side(s - x0) | side(y1) | side(s - y0)


def _imul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (np.minimum(np.minimum(p[0], p[1]), np.minimum(p[2], p[3])),
            np.maximum(np.maximum(p[0], p[1]), np.maximum(p[2], p[3])))


def _iadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _isub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def _iabs(a):
    lo = np.where((a[0] <= 0) & (a[1] >= 0), 0.0, np.minimum(np.abs(a[0]), np.abs(a[1])))
    return (lo, np.maximum(np.abs(a[0]), np.abs(a[1])))


def _cs(t0, t1):
    d0, d1 = 1 + t0 * t0, 1 + t1 * t1
    return ((1 - t1 * t1) / d1, (1 - t0 * t0) / d0), (2 * t0 / d0, 2 * t1 / d1)


def nondisjoint(FA, FB):
    """(n,) bool: float mirror of nondisjoint_certain (v1 3.3)."""
    dX = (FB[:, 2] - FA[:, 3], FB[:, 3] - FA[:, 2])
    dY = (FB[:, 4] - FA[:, 5], FB[:, 5] - FA[:, 4])
    ax, ay = _iabs(dX), _iabs(dY)
    pre = ax[1] * ax[1] + ay[1] * ay[1] < 1
    C1, S1 = _cs(FA[:, 0], FA[:, 1])
    C2, S2 = _cs(FB[:, 0], FB[:, 1])
    cc = _iadd(_imul(C1, C2), _imul(S1, S2))
    ss = _isub(_imul(S1, C2), _imul(C1, S2))
    g = _iadd(_iabs(cc), _iabs(ss))
    bound = 0.5 + np.maximum(g[0], 1.0) / 2
    ok = np.ones(len(FA), dtype=bool)
    for (U, V) in ((C1, S1), ((-S1[1], -S1[0]), C1), (C2, S2), ((-S2[1], -S2[0]), C2)):
        proj = _iadd(_imul(dX, U), _imul(dY, V))
        ok &= _iabs(proj)[1] < bound
    return pre | ok


def w_of(t):
    return (1 - t * t + 2 * t) / (1 + t * t)


def w_hi_of(t0, t1):
    """float mirror of verify_pair2.w_bounds()[1]; biased upward (conservative)."""
    w0, w1 = w_of(t0), w_of(t1)
    local = (t1 <= TSTAR_LO_F - 1e-12) | (t0 >= TSTAR_HI_F + 1e-12)
    return np.where(local, np.maximum(w0, w1), W_HI_GLOBAL_F) + 1e-12


def clip(F, s):
    """float mirror of clip_factor: returns (F', alive)."""
    F = F.copy()
    w_lo = np.minimum(w_of(F[:, 0]), w_of(F[:, 1]))
    lo, hi = w_lo / 2, s - w_lo / 2
    F[:, 2] = np.maximum(F[:, 2], lo)
    F[:, 3] = np.minimum(F[:, 3], hi)
    F[:, 4] = np.maximum(F[:, 4], lo)
    F[:, 5] = np.minimum(F[:, 5], hi)
    alive = (F[:, 2] <= F[:, 3]) & (F[:, 4] <= F[:, 5]) & (lo <= hi)
    return F, alive


# ------------------------------------------------------------------ U bound (spec 3.7)
def possibly_meets_mat(F, boxes, tol=TOL_SEP):
    """(n,m) bool: negation of certain interior separation (v1 3.4 / v2 3.7), float.

    Each separation test is weakened by `tol`, so float never claims 'certainly
    separated' where the exact code would not: the count is an upper bound on the
    exact possibly-meets count, hence U is >= the exact U (conservative)."""
    n = len(F)
    out = np.zeros((n, len(boxes)), dtype=bool)
    if not len(boxes):
        return out
    t0, t1 = F[:, 0], F[:, 1]
    C, S = _cs(t0, t1)
    nS = (-S[1], -S[0])
    w_hi = w_hi_of(t0, t1)
    for bi, (bx, by, h) in enumerate(boxes):
        ex = (F[:, 2] - bx, F[:, 3] - bx)
        ey = (F[:, 4] - by, F[:, 5] - by)
        sep = _iabs(ex)[0] >= h + w_hi / 2 + tol
        sep |= _iabs(ey)[0] >= h + w_hi / 2 + tol
        pu = _iadd(_imul(ex, C), _imul(ey, S))
        sep |= _iabs(pu)[0] >= 0.5 + h * w_hi + tol
        pv = _iadd(_imul(ex, nS), _imul(ey, C))
        sep |= _iabs(pv)[0] >= 0.5 + h * w_hi + tol
        out[:, bi] = ~sep
    return out


# ------------------------------------------------------------- urow discount (v2.1)
def zone_slot_mask(F, zones, nslot, tol=TOL_ZONE):
    """(n,nslot) bool: factor i is contained in some zone box of slot j."""
    M = np.zeros((len(F), nslot), dtype=bool)
    for (sl, zt0, zt1, zx0, zx1, zy0, zy1) in zones:
        c = ((F[:, 0] >= zt0 + tol) & (F[:, 1] <= zt1 - tol) &
             (F[:, 2] >= zx0 + tol) & (F[:, 3] <= zx1 - tol) &
             (F[:, 4] >= zy0 + tol) & (F[:, 5] <= zy1 - tol))
        M[:, sl] |= c
    return M


def bzc_fire(FA, FB, zones, nslot):
    """(n,) bool: FA pinned into slot j, FB into slot j' != j, of the same image."""
    MA = zone_slot_mask(FA, zones, nslot)
    MB = zone_slot_mask(FB, zones, nslot)
    pa, pb = MA.sum(axis=1), MB.sum(axis=1)
    common = (MA & MB).sum(axis=1)
    return (pa > 0) & (pb > 0) & (pa + pb - common > 1)


def box_targets(FA, FB):
    """(thr_box, thr_lo, n_boosted) in MILLION-scaled integer units.

    thr_box = 1e6*(1 + beta*U) - sum_g gamma_g*1e6*bzc_g      (COVERED target, high)
    thr_lo  = 1e6*(1 + beta*M2LO) - sum_g gamma_g*1e6*bzc_g   (probe trigger, low)
    """
    BN, BD = G["BN"], G["BD"]
    BOXES, IMAGES = G["BOXES"], G["IMAGES"]
    if BN == 0 and not IMAGES:
        return MILLION, MILLION, 0
    n = len(FA)
    U = np.zeros(n, dtype=np.int64)
    M2LO = np.zeros(n, dtype=np.int64)
    if BN and BOXES:
        U = (possibly_meets_mat(FA, BOXES) & possibly_meets_mat(FB, BOXES)).sum(axis=1)
        U = U.astype(np.int64)
        M2LO = (certain_meets_mat(FA, BOXES) & certain_meets_mat(FB, BOXES)).sum(axis=1)
        M2LO = M2LO.astype(np.int64)
    disc = np.zeros(n, dtype=np.int64)
    for (name, gf, gi, zones, nslot) in IMAGES:
        disc += gi * bzc_fire(FA, FB, zones, nslot).astype(np.int64)
    hi = -((-(MILLION * BN) * U) // BD)          # ceil  (target up = conservative)
    lo = (MILLION * BN * M2LO) // BD             # floor (trigger down = conservative)
    thr_box = MILLION + hi - disc
    thr_lo = MILLION + lo - disc
    return thr_box, thr_lo, int(np.count_nonzero(thr_box > MILLION))


# ------------------------------------------------------------------ atoms (worker globals)
G = {}


RULE = "soft"


def _init(px, py, qx, qy, w, wint, cores, s, beta_num, beta_den, boxes, images,
          rule="soft"):
    global RULE
    RULE = rule
    imgs = []
    for (name, gf, gi, zones) in images:
        nslot = max([int(z[0]) for z in zones]) + 1 if zones else 0
        imgs.append((name, float(gf), int(gi),
                     [(int(z[0]),) + tuple(float(v) for v in z[1:]) for z in zones],
                     nslot))
    G.update(PX=px, PY=py, QX=qx, QY=qy, W=w, WINT=wint, CORES=cores, S=s,
             BN=int(beta_num), BD=int(beta_den), BETAF=float(beta_num) / float(beta_den),
             BOXES=list(boxes), IMAGES=imgs)


def cert_masks(FA, FB):
    PX, PY, QX, QY = G["PX"], G["PY"], G["QX"], G["QY"]
    cAp = slack(FA, PX, PY) >= MG
    cAq = slack(FA, QX, QY) >= MG
    cBp = slack(FB, PX, PY) >= MG
    cBq = slack(FB, QX, QY) >= MG
    return cAp, cAq, cBp, cBq


def mass_of(cAp, cAq, cBp, cBq):
    return ((cAp & cBq) | (cAq & cBp)).astype(np.int64) @ G["WINT"]


def possible_mass(FA, FB):
    PX, PY, QX, QY = G["PX"], G["PY"], G["QX"], G["QY"]
    pAp, pAq = possible(FA, PX, PY), possible(FA, QX, QY)
    pBp, pBq = possible(FB, PX, PY), possible(FB, QX, QY)
    return ((pAp & pBq) | (pAq & pBp)).astype(np.int64) @ G["WINT"]


# ------------------------------------------------------------------ hole probe (per box)
_FR = np.array([0.5, 0.25, 0.75])


def probe_points(F, s, cores):
    """float-admissible core-free placements on the 3x3x3 fractional grid of F."""
    t = F[0] + (F[1] - F[0]) * _FR
    x = F[2] + (F[3] - F[2]) * _FR
    y = F[4] + (F[5] - F[4]) * _FR
    T, X, Y = np.meshgrid(t, x, y, indexing="ij")
    T, X, Y = T.ravel(), X.ravel(), Y.ravel()
    d = 1 + T * T
    C, S = (1 - T * T) / d, 2 * T / d
    h = (C + S) / 2
    ok = (X >= h) & (X <= s - h) & (Y >= h) & (Y <= s - h)
    w = C + S
    for (kx, ky, a) in cores:
        ex, ey = X - kx, Y - ky
        ov = (np.abs(ex) <= a + w / 2) & (np.abs(ey) <= a + w / 2) \
            & (np.abs(ex * C + ey * S) <= 0.5 + a * w) \
            & (np.abs(-ex * S + ey * C) <= 0.5 + a * w)
        ok &= ~ov
    return T[ok], X[ok], Y[ok], C[ok], S[ok]


def in_square(PX, PY, T, X, Y, C, S):
    """(nplace, M) bool membership (closed)."""
    dx = PX[None, :] - X[:, None]
    dy = PY[None, :] - Y[:, None]
    u = C[:, None] * dx + S[:, None] * dy
    v = -S[:, None] * dx + C[:, None] * dy
    return (np.abs(u) <= 0.5 + 1e-12) & (np.abs(v) <= 0.5 + 1e-12)


def open_meets_boxes(X, Y, C, S, boxes):
    """(nplace, m) bool: OPEN interior of the unit square at (X,Y,t) meets class box j."""
    out = np.zeros((len(X), len(boxes)), dtype=bool)
    if not len(boxes):
        return out
    w = C + S
    for bi, (bx, by, h) in enumerate(boxes):
        ex, ey = X - bx, Y - by
        out[:, bi] = ((np.abs(ex) < h + w / 2) & (np.abs(ey) < h + w / 2)
                      & (np.abs(ex * C + ey * S) < 0.5 + h * w)
                      & (np.abs(-ex * S + ey * C) < 0.5 + h * w))
    return out


def point_slot_mask(T, X, Y, zones, nslot):
    """(nplace, nslot) bool: point (t,x,y) inside some zone box of slot j (closed)."""
    M = np.zeros((len(T), nslot), dtype=bool)
    for (sl, zt0, zt1, zx0, zx1, zy0, zy1) in zones:
        c = ((T >= zt0) & (T <= zt1) & (X >= zx0) & (X <= zx1)
             & (Y >= zy0) & (Y <= zy1))
        M[:, sl] |= c
    return M


def probe_hole(FA, FB):
    """min-mass float-admissible interior-disjoint pair in FA x FB, or None."""
    s, cores = G["S"], G["CORES"]
    TA, XA, YA, CA, SA = probe_points(FA, s, cores)
    TB, XB, YB, CB, SB = probe_points(FB, s, cores)
    if len(TA) == 0 or len(TB) == 0:
        return None
    dx = XB[None, :] - XA[:, None]
    dy = YB[None, :] - YA[:, None]
    cc = CA[:, None] * CB[None, :] + SA[:, None] * SB[None, :]
    ss = SA[:, None] * CB[None, :] - CA[:, None] * SB[None, :]
    bound = 0.5 + (np.abs(cc) + np.abs(ss)) / 2
    disj = np.zeros(dx.shape, dtype=bool)
    for (ux, uy) in ((CA[:, None], SA[:, None]), (-SA[:, None], CA[:, None]),
                     (CB[None, :], SB[None, :]), (-SB[None, :], CB[None, :])):
        disj |= np.abs(dx * ux + dy * uy) >= bound + 1e-12
    if not disj.any():
        return None
    PX, PY, QX, QY, W = G["PX"], G["PY"], G["QX"], G["QY"], G["W"]
    Ap = in_square(PX, PY, TA, XA, YA, CA, SA)
    Aq = in_square(QX, QY, TA, XA, YA, CA, SA)
    Bp = in_square(PX, PY, TB, XB, YB, CB, SB)
    Bq = in_square(QX, QY, TB, XB, YB, CB, SB)
    o0 = (Ap * W) @ Bq.T.astype(float)
    o1 = (Aq * W) @ Bp.T.astype(float)
    both = ((Ap & Aq) * W) @ (Bq & Bp).T.astype(float)
    mass = o0 + o1 - both
    BETAF, BOXES, IMAGES = G["BETAF"], G["BOXES"], G["IMAGES"]
    trivial = (BETAF == 0.0 or not BOXES) and not IMAGES
    m2 = np.zeros(mass.shape, dtype=np.int64)
    bzs = {}
    if trivial:
        # exactly the A77 path (beta = 0, no urow): target is the constant 1
        mm = np.where(disj, mass, np.inf)
        k = int(np.argmin(mm))
        ia, ib = divmod(k, mass.shape[1])
        hit = mass[ia, ib] < 1 - 1e-9
        tgt = 1.0
    else:
        if BETAF != 0.0 and BOXES:
            OA = open_meets_boxes(XA, YA, CA, SA, BOXES)
            OB = open_meets_boxes(XB, YB, CB, SB, BOXES)
            m2 = OA.astype(np.int64) @ OB.T.astype(np.int64)
        thr = 1.0 + BETAF * m2.astype(float)
        for (name, gf, gi, zones, nslot) in IMAGES:
            ZA = point_slot_mask(TA, XA, YA, zones, nslot)
            ZB = point_slot_mask(TB, XB, YB, zones, nslot)
            pa, pb = ZA.sum(axis=1), ZB.sum(axis=1)
            common = ZA.astype(np.int64) @ ZB.T.astype(np.int64)
            un = pa[:, None] + pb[None, :] - common
            fire = (pa[:, None] > 0) & (pb[None, :] > 0) & (un > 1)
            bzs[name] = fire
            thr = thr - gf * fire.astype(float)
        sc = np.where(disj, mass - thr, np.inf)
        k = int(np.argmin(sc))
        ia, ib = divmod(k, mass.shape[1])
        hit = mass[ia, ib] < thr[ia, ib] - 1e-9
        tgt = float(thr[ia, ib])
    if hit:
        return dict(mass=float(mass[ia, ib]),
                    A=[float(TA[ia]), float(XA[ia]), float(YA[ia])],
                    B=[float(TB[ib]), float(XB[ib]), float(YB[ib])],
                    m2=int(m2[ia, ib]), target=tgt,
                    bz={nm: int(fm[ia, ib]) for nm, fm in bzs.items()})
    return None


# ------------------------------------------------------------------ dyadic cut
def dyadic_cut(lo, hi):
    """short dyadics strictly inside [lo,hi] (arrays), near the midpoints."""
    w = np.maximum(hi - lo, 1e-300)
    k = np.maximum(np.ceil(np.log2(64.0 / w)), 1.0)
    step = np.exp2(-k)
    mid = 0.5 * (lo + hi)
    at = np.round(mid / step) * step
    return np.where((lo < at) & (at < hi), at, mid)


# ------------------------------------------------------------------ per-root BFS
def build_root(job):
    ri, key, FA0, FB0, cap, maxdepth, chunk, keep_open = job
    s, cores = G["S"], G["CORES"]
    t0 = time.time()
    # node table
    cut_f, cut_d, cut_at, lo_id, hi_id, kind = [], [], [], [], [], []

    def new_node():
        cut_f.append(-1); cut_d.append(-1); cut_at.append(0.0)
        lo_id.append(-1); hi_id.append(-1); kind.append(K_SPLIT)
        return len(kind) - 1

    root = new_node()
    frontier_F = np.array([list(FA0) + list(FB0)], dtype=float)
    frontier_id = np.array([root], dtype=np.int64)
    depth = 0
    holes, opens = [], []
    census = {k: 0 for k in KNAMES}
    census_depth = {}
    budget_hit = False
    n_boosted = 0
    while len(frontier_F):
        nxt_F, nxt_id = [], []
        for c0 in range(0, len(frontier_F), chunk):
            F = frontier_F[c0:c0 + chunk]
            ids = frontier_id[c0:c0 + chunk]
            n = len(F)
            FA, FB = F[:, :6], F[:, 6:]
            k = np.zeros(n, dtype=np.int8)
            vc = vac_contain(FA, s) | vac_contain(FB, s)
            k[vc] = K_VAC
            ex = exempt(FA, cores) | exempt(FB, cores)
            k[(k == 0) & ex] = K_EX
            nd = nondisjoint(FA, FB)
            k[(k == 0) & nd] = K_ND
            PX, PY, QX, QY, WINT = G["PX"], G["PY"], G["QX"], G["QY"], G["WINT"]
            # possible masks on the full atom set; the chunk's union of possible
            # atoms is the working subset for every later (certain) evaluation
            pAp, pAq = possible(FA, PX, PY), possible(FA, QX, QY)
            pBp, pBq = possible(FB, PX, PY), possible(FB, QX, QY)
            poss = (pAp & pBq) | (pAq & pBp)
            pm = poss.astype(np.int64) @ WINT
            sub_idx = np.nonzero(poss.any(axis=0))[0]
            sPX, sPY, sQX, sQY, sW = PX[sub_idx], PY[sub_idx], QX[sub_idx], QY[sub_idx], WINT[sub_idx]

            def smass(a, b, c, d):
                return ((a & b) | (c & d)).astype(np.int64) @ sW
            sAp, sAq = slack(FA, sPX, sPY), slack(FA, sQX, sQY)
            sBp, sBq = slack(FB, sPX, sPY), slack(FB, sQX, sQY)
            cAp, cAq, cBp, cBq = sAp >= MG, sAq >= MG, sBp >= MG, sBq >= MG
            mass = smass(cAp, cBq, cAq, cBp)
            thr_box, thr_lo, nb = box_targets(FA, FB)
            n_boosted += nb
            k[(k == 0) & (mass >= thr_box)] = K_COV
            und = np.nonzero((k == 0) & (pm < thr_lo))[0]
            for i in und:
                h = probe_hole(FA[i], FB[i])
                if h is not None:
                    k[i] = K_HOLE
                    h.update(depth=depth, root=key, pm=int(pm[i]),
                             cm=int(mass[i]), F=F[i].tolist())
                    holes.append(h)
                elif depth >= maxdepth:
                    k[i] = K_AMB
            if depth >= maxdepth or budget_hit:
                k[k == 0] = K_OPEN
            # census + open records
            for kk in np.unique(k):
                cnt = int((k == kk).sum())
                census[int(kk)] += cnt
                dd = census_depth.setdefault(depth, {})
                dd[KNAMES[int(kk)]] = dd.get(KNAMES[int(kk)], 0) + cnt
            for i in np.nonzero((k == K_OPEN) | (k == K_AMB))[0]:
                if len(opens) < keep_open:
                    opens.append(dict(F=F[i].tolist(), depth=depth, cm=int(mass[i]),
                                      pm=int(pm[i]), kind=KNAMES[int(k[i])], root=key))
            for i in range(n):
                kind[int(ids[i])] = int(k[i])
            # ---- lookahead split for k == 0: max-min over the 6 midpoint cuts of the
            # SOFT certain mass (atoms graded by slack/eta0, so the score has a gradient
            # even where nothing is certain yet; ties -> widest scaled dimension)
            sp = np.nonzero(k == 0)[0]
            if not len(sp):
                continue
            FAs, FBs = FA[sp], FB[sp]
            sWf = sW.astype(float) / MILLION

            def soft(sl):
                if RULE == "certain":
                    return (sl >= MG).astype(float)
                return np.clip((sl + ETA0) / ETA0, 0.0, 1.0)
            fAp, fAq, fBp, fBq = soft(sAp[sp]), soft(sAq[sp]), soft(sBp[sp]), soft(sBq[sp])

            def softmass(a, b, c, d):
                return np.maximum(a * b, c * d) @ sWf
            best_score = np.full(len(sp), -1.0)
            best_cut = np.zeros((len(sp), 3))          # fac, dim, at
            best_valid = np.zeros(len(sp), dtype=bool)
            for fac in (0, 1):
                Fx = FAs if fac == 0 else FBs
                for dim in range(3):
                    lo, hi = Fx[:, 2 * dim], Fx[:, 2 * dim + 1]
                    wd = hi - lo
                    valid = wd > 1e-7
                    if not valid.any():
                        continue
                    at = dyadic_cut(lo, hi)
                    ms = []
                    for side in (0, 1):
                        Fc = Fx.copy()
                        if side == 0:
                            Fc[:, 2 * dim + 1] = at
                        else:
                            Fc[:, 2 * dim] = at
                        f_p = soft(slack(Fc, sPX, sPY))
                        f_q = soft(slack(Fc, sQX, sQY))
                        if RULE == "widest":
                            ms.append(np.zeros(len(sp)))
                            continue
                        if fac == 0:
                            m = softmass(f_p, fBq, f_q, fBp)
                        else:
                            m = softmass(fAp, f_q, fAq, f_p)
                        ms.append(m)
                    score = (np.minimum(ms[0], ms[1]) * 1e3 + (ms[0] + ms[1])
                             + 1e-6 * wd * (TSCALE if dim == 0 else 1.0))
                    score = np.where(valid, score, -1.0)
                    better = score > best_score
                    best_score = np.where(better, score, best_score)
                    best_cut[better, 0] = fac
                    best_cut[better, 1] = dim
                    best_cut[better, 2] = at[better]
                    best_valid |= better & valid
            # ---- children
            for a, i in enumerate(sp):
                nid = int(ids[i])
                if not best_valid[a]:
                    kind[nid] = K_OPEN
                    census[K_OPEN] += 1
                    continue
                fac, dim, at = int(best_cut[a, 0]), int(best_cut[a, 1]), float(best_cut[a, 2])
                cut_f[nid], cut_d[nid], cut_at[nid] = fac, dim, at
                base = 6 * fac + 2 * dim
                for side in (0, 1):
                    Fc = F[i].copy()
                    if side == 0:
                        Fc[base + 1] = at
                    else:
                        Fc[base] = at
                    fac_box = Fc[6 * fac:6 * fac + 6][None, :]
                    fc, alive = clip(fac_box, s)
                    if not alive[0]:
                        census[K_VAC] += 1
                        continue
                    Fc[6 * fac:6 * fac + 6] = fc[0]
                    cid = new_node()
                    if side == 0:
                        lo_id[nid] = cid
                    else:
                        hi_id[nid] = cid
                    nxt_F.append(Fc)
                    nxt_id.append(cid)
        depth += 1
        if not nxt_F:
            break
        frontier_F = np.array(nxt_F)
        frontier_id = np.array(nxt_id, dtype=np.int64)
        if len(kind) + 2 * len(frontier_F) > cap and not budget_hit:
            budget_hit = True          # next level is evaluated but not split
    return dict(root=ri, key=key, nodes=len(kind), maxdepth=depth,
                census={KNAMES[k]: v for k, v in census.items()},
                census_depth=census_depth, holes=holes, opens=opens,
                budget_hit=budget_hit, seconds=time.time() - t0, n_boosted=n_boosted,
                table=(np.array(cut_f, dtype=np.int8), np.array(cut_d, dtype=np.int8),
                       np.array(cut_at, dtype=float), np.array(lo_id, dtype=np.int64),
                       np.array(hi_id, dtype=np.int64), np.array(kind, dtype=np.int8)))


# ------------------------------------------------------------------ certificate
def _reject_float(x):
    raise ValueError("JSON float literal rejected (numbers must be rational strings)")


def _rat(x, what="number"):
    if isinstance(x, str):
        return Fr(x)
    if isinstance(x, int):
        return Fr(x)
    raise ValueError("expected rational string for %s, got %r" % (what, x))


class _NS(object):
    """minimal stand-in for vp.Cert: vp.roots() only reads `.s`."""

    def __init__(self, s):
        self.s = s


class Cert81(object):
    """pair-certificate v1 / v2 / v2.1 reader (exact rationals; beta >= 0)."""

    FORMATS = ("pair-certificate-v1", "pair-certificate-v2", "pair-certificate-v2.1")

    def __init__(self, path):
        with open(path, "r") as fh:
            doc = json.load(fh, parse_float=_reject_float,
                            parse_constant=_reject_float)
        if not isinstance(doc, dict):
            raise ValueError("top level must be an object")
        self.doc = doc
        self.format = doc.get("format")
        if self.format not in self.FORMATS:
            raise ValueError("bad format %r" % (self.format,))
        self.s = _rat(doc.get("s"), "s")
        if self.s <= 0:
            raise ValueError("s must be positive")
        self.n = int(doc.get("n", 11))
        self.k = int(doc.get("k", 0))
        self.m = int(doc.get("m", 0))
        self.beta = _rat(doc.get("beta", "0"), "beta")
        if self.beta < 0:
            raise ValueError("beta must be >= 0")
        cores = doc.get("cores", [])
        boxes = doc.get("boxes", [])
        if len(cores) != self.k:
            raise ValueError("k=%d but %d cores" % (self.k, len(cores)))
        if len(boxes) != self.m:
            raise ValueError("m=%d but %d boxes" % (self.m, len(boxes)))
        self.cores = [(_rat(c["kx"], "kx"), _rat(c["ky"], "ky"), _rat(c["a"], "a"))
                      for c in cores]
        self.boxes = [(_rat(b["bx"], "bx"), _rat(b["by"], "by"), _rat(b["h"], "h"))
                      for b in boxes]
        self.atoms = doc.get("atoms", [])
        # -------- optional v2.1 urow discount block
        self.urow = None
        self.images = []                 # (name, gamma_float, gamma_int, zones)
        u = doc.get("urow")
        if u:
            self.urow = dict(rung=int(u.get("rung", 0)), cap=int(u.get("cap", 0)))
            for name in sorted(u.get("images", {})):
                img = u["images"][name]
                gam = _rat(img["gamma"], "gamma")
                if (gam * MILLION).denominator != 1:
                    raise ValueError("gamma %s not on the 1e-6 grid" % gam)
                if gam < 0:
                    raise ValueError("gamma must be >= 0")
                zones = []
                for z in img.get("zones", []):
                    zones.append((int(z["slot"]),
                                  _rat(z["t0"], "t0"), _rat(z["t1"], "t1"),
                                  _rat(z["x0"], "x0"), _rat(z["x1"], "x1"),
                                  _rat(z["y0"], "y0"), _rat(z["y1"], "y1")))
                self.images.append((name, float(gam), int(gam * MILLION), zones))


# ------------------------------------------------------------------ JSON streaming
def write_tree(fh, table):
    cut_f, cut_d, cut_at, lo_id, hi_id, kind = table
    if cut_f[0] < 0:
        fh.write("null")
        return
    stack = [(0, 0)]
    dn = "txy"
    while stack:
        nid, phase = stack.pop()
        if phase == 0:
            if nid < 0 or cut_f[nid] < 0:
                fh.write("null")
                continue
            fh.write('{"cut":{"f":%d,"d":"%s","at":"%s"},"lo":'
                     % (cut_f[nid], dn[cut_d[nid]], Fr(float(cut_at[nid]))))
            stack.append((nid, 1))
            stack.append((int(lo_id[nid]), 0))
        elif phase == 1:
            fh.write(',"hi":')
            stack.append((nid, 2))
            stack.append((int(hi_id[nid]), 0))
        else:
            fh.write("}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("out")
    ap.add_argument("--cap", type=int, default=200000, help="nodes per root pair")
    ap.add_argument("--maxdepth", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--chunk", type=int, default=1024)
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--holes", default="")
    ap.add_argument("--keep_open", type=int, default=2000)
    ap.add_argument("--roots", default="", help="comma list of root indices (debug)")
    ap.add_argument("--no_tree", action="store_true")
    ap.add_argument("--rule", default="soft", choices=["soft", "certain", "widest"])
    ap.add_argument("--root_order", default="python", choices=["python", "rust"],
                    help="root-factor enumeration order of the target verifier")
    args = ap.parse_args()

    cert = Cert81(args.cert)
    doc = cert.doc
    at = cert.atoms
    px = np.array([float(Fr(a["px"])) for a in at])
    py = np.array([float(Fr(a["py"])) for a in at])
    qx = np.array([float(Fr(a["qx"])) for a in at])
    qy = np.array([float(Fr(a["qy"])) for a in at])
    wq = [Fr(a["w"]) for a in at]
    assert all((w * MILLION).denominator == 1 for w in wq), "weights not on the 1e-6 grid"
    wint = np.array([int(w * MILLION) for w in wq], dtype=np.int64)
    w = wint.astype(float) / MILLION
    cores = [(float(c[0]), float(c[1]), float(c[2])) for c in cert.cores]
    boxes = [(float(b[0]), float(b[1]), float(b[2])) for b in cert.boxes]
    s = float(cert.s)
    bn, bd = cert.beta.numerator, cert.beta.denominator
    assert MILLION * bn * max(1, cert.m) < 2 ** 62, "beta too large for int64 targets"
    images = [(nm, gf, gi, [tuple([z[0]] + [float(v) for v in z[1:]]) for z in zs])
              for (nm, gf, gi, zs) in cert.images]
    factors, pairs = vp.roots(_NS(cert.s), args.split)
    if args.root_order == "rust":
        # the compiled verifier enumerates the centre grid iy-major (bb.rs build_roots:
        # index = iy*2^k + ix); the reference enumerates ix-major (index = ix*2^k + iy).
        # Spec 3.1/4 are silent, so "i,j" hint keys are NOT portable between the two
        # frozen implementations (A77 finding).  Re-order the factors to match.
        g = 1 << args.split
        factors = [factors[ix * g + iy] for iy in range(g) for ix in range(g)]
    clipped = [vp.clip_factor(F, cert.s) for F in factors]
    jobs = []
    sel = set(int(x) for x in args.roots.split(",") if x) if args.roots else None
    for ri, (i, j) in enumerate(pairs):
        if sel is not None and ri not in sel:
            continue
        FA, FB = clipped[i], clipped[j]
        if FA is None or FB is None:
            continue
        jobs.append((ri, "%d,%d" % (i, j), tuple(float(v) for v in FA),
                     tuple(float(v) for v in FB), args.cap, args.maxdepth, args.chunk,
                     args.keep_open))
    t0 = time.time()
    init = (px, py, qx, qy, w, wint, cores, s, bn, bd, boxes, images, args.rule)
    results = []
    if args.jobs > 1:
        from multiprocessing import Pool
        with Pool(args.jobs, initializer=_init, initargs=init) as pool:
            for r in pool.imap_unordered(build_root, jobs):
                results.append(r)
                print("  root %s: nodes=%d depth=%d census=%s holes=%d budget_hit=%s (%.0fs)"
                      % (r["key"], r["nodes"], r["maxdepth"], json.dumps(r["census"]),
                         len(r["holes"]), r["budget_hit"], r["seconds"]), flush=True)
    else:
        _init(*init)
        for jb in jobs:
            r = build_root(jb)
            results.append(r)
            print("  root %s: nodes=%d depth=%d census=%s holes=%d budget_hit=%s (%.0fs)"
                  % (r["key"], r["nodes"], r["maxdepth"], json.dumps(r["census"]),
                     len(r["holes"]), r["budget_hit"], r["seconds"]), flush=True)
    results.sort(key=lambda r: r["root"])
    tot = {k: 0 for k in KNAMES.values()}
    nodes = 0
    boosted = 0
    holes, opens = [], []
    per_root = []
    cd = {}
    for r in results:
        for k, v in r["census"].items():
            tot[k] += v
        nodes += r["nodes"]
        boosted += r.get("n_boosted", 0)
        holes += r["holes"]
        opens += r["opens"]
        for d, h in r["census_depth"].items():
            for k, v in h.items():
                cd.setdefault(int(d), {}).setdefault(k, 0)
                cd[int(d)][k] += v
        per_root.append(dict(key=r["key"], nodes=r["nodes"], maxdepth=r["maxdepth"],
                             census=r["census"], holes=len(r["holes"]),
                             budget_hit=r["budget_hit"], seconds=round(r["seconds"], 1),
                             n_boosted=r.get("n_boosted", 0)))
    retention = {}
    for d in sorted(cd):
        if d == 0:
            continue
        prev = cd.get(d - 1, {}).get("split", 0)
        if prev:
            retention[str(d)] = round(cd[d].get("split", 0) / (2.0 * prev), 6)
    summary = dict(cert=args.cert, cap=args.cap, maxdepth=args.maxdepth, nodes=nodes,
                   roots=len(results), census=tot, n_holes=len(holes),
                   n_open=tot["open"] + tot["amb"], n_boosted=boosted,
                   beta=str(cert.beta), m=cert.m,
                   urow=(cert.urow if cert.urow else None),
                   budget_roots=sum(1 for r in results if r["budget_hit"]),
                   seconds=round(time.time() - t0, 1), per_root=per_root,
                   census_by_depth={str(d): cd[d] for d in sorted(cd)},
                   retention=retention)
    print("TOTAL nodes=%d census=%s holes=%d open=%d budget_roots=%d boosted=%d (%.0fs)"
          % (nodes, json.dumps(tot), len(holes), summary["n_open"],
             summary["budget_roots"], boosted, time.time() - t0), flush=True)
    print("RETENTION %s" % json.dumps(retention), flush=True)
    if args.holes:
        json.dump(dict(summary=summary, holes=holes, opens=opens),
                  open(args.holes, "w"))
    if not args.no_tree:
        # certificate with hints, streamed (no float literals anywhere: cut_at as Fr)
        base = {k: v for k, v in doc.items() if k != "hints"}
        base.setdefault("provenance", {})["hints"] = dict(
            tool="A81 hintbatch81.py (A77 hintbatch + beta/U/urow targets)",
            split=args.split, cap=args.cap, maxdepth=args.maxdepth,
            root_order=args.root_order, stats={k: int(v) for k, v in tot.items()}, nodes=int(nodes),
            n_holes=len(holes), seconds=str(summary["seconds"]))
        with open(args.out, "w") as fh:
            body = json.dumps(base, sort_keys=True)
            assert body.endswith("}")
            fh.write(body[:-1])
            fh.write(',"hints":{"trees":{')
            first = True
            for r in results:
                if r["table"][0][0] < 0:
                    continue
                if not first:
                    fh.write(",")
                first = False
                fh.write('"%s":' % r["key"])
                write_tree(fh, r["table"])
            fh.write("}}}")
        print("wrote %s" % args.out, flush=True)


if __name__ == "__main__":
    main()
