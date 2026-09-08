"""A153 -- the COVER NUMBER of the feasible-centre region.

THE LEMMA (Lemma CN).  Let Q1, Q2 be unit squares (any tilts) with disjoint interiors and centres
c1, c2.  Then |c1 - c2| >= 1.
    Proof.  A unit square contains the open disk of radius 1/2 about its centre (the distance from
    the centre to each of the four side lines is exactly 1/2).  If |c1 - c2| < 1 then the midpoint
    m = (c1 + c2)/2 has |m - ci| < 1/2, so m lies in both open disks, hence in both interiors --
    contradiction.  []

THE LEAF (Leaf CN).  Let a node have `budget` unit squares still to place and let F_outer be ANY
set containing every centre they could take (A148's certified outer approximation of the
feasible-centre region is one).  If

        F_outer  is contained in  S_1 u ... u S_k     with  diam(S_i) < 1  for every i,

then at most k of them can be placed: two centres in one S_i would be < 1 apart, contradicting
Lemma CN.  So `k < budget` KILLS the node, with no LP.

PIECES.  Axis-aligned squares of side d have diameter d*sqrt2, so `2 d^2 < 1` is the exact rational
admissibility test.  A148's grid has pitch p = s0/n, and a piece is taken to be a K x K block of
grid cells, K = the largest integer with 2 (K p)^2 < 1 -- at n = 194 that is K = 35, side
0.699474 <= 0.7, the PI's side-0.7 squares.  F_outer is a union of grid cells, so "the pieces cover
F_outer" is the finite integer statement "every non-BLOCKED cell lies in some K x K block".

LEMMA TC (conditional, the tilt-coherent branch).  If two interior-disjoint unit squares have the
SAME tilt t, their centre difference has L-infinity norm >= 1 in the frame rotated by t (in that
frame both are axis-aligned unit squares, and axis-aligned unit squares with |dx| < 1 and |dy| < 1
overlap).  So under the hypothesis "every remaining square has tilt t" the pieces may be squares of
side < 1 IN THE t-FRAME.  If t is only known to lie in a window of half-width delta, a square of
side d in the mid-frame has width d(cos delta + sin delta) <= d(1 + delta) in every frame of the
window, so `d (1 + delta) < 1` makes the piece admissible for the whole window.

LOWER BOUNDS (a cover number can only be trusted from above, but a node is only interesting if the
cover can be small, so both directions are reported):
    LB_area   = ceil( area(F_outer) / d^2 )            -- pieces are squares of area d^2;
    LB_indep  = a set of cells pairwise L-infinity >= K apart in cell units (no piece holds two);
    FLOOR     = a 1-separated set of points OF F_outer (greedy) -- a lower bound on the true packing
                number, so a certificate that no cover-style leaf can ever bound this node below it.

Everything here is read-only on A148/A132/A135/A57/A60: geo148 is imported for the region, nothing
is written outside attempts/A153-cover-number/.
"""
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A142-a57-review-gallery", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo148 as G                                                    # noqa: E402

S0 = G.S0
S0_FR = Fr(969271, 250000)


# ===================================================================== the region
def region_of(boxes, is_pin=None, pitch=G.PITCH_TARGET, ntilt=G.NTILT):
    """A148's certified three-valued centre map, verbatim (geo148 is imported, never edited)."""
    obst, onames, kinds, _ = G.obstacles_of(boxes, is_pin)
    reg = G.feasible_region(S0, obst, pitch, ntilt)
    return reg, obst, onames, kinds


def piece_K(reg):
    """the largest K with a K x K block of cells admissible: 2 (K p)^2 < 1, exactly in rationals."""
    n = reg.green.shape[0]
    p = S0_FR / n
    K = 0
    while 2 * ((K + 1) * p) ** 2 < 1:
        K += 1
    return K, p


# ===================================================================== covers of a cell set
def _integral(mask):
    S = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), np.int64)
    S[1:, 1:] = np.cumsum(np.cumsum(mask.astype(np.int64), 0), 1)
    return S


def _window_counts(mask, K):
    """counts[j0, i0] = number of True cells in the K x K block anchored at (i0, j0)."""
    S = _integral(mask)
    ny, nx = mask.shape
    my, mx = ny - K + 1, nx - K + 1
    return (S[K:K + my, K:K + mx] - S[0:my, K:K + mx]
            - S[K:K + my, 0:mx] + S[0:my, 0:mx])


def pad_for(mask, K):
    """pad by K-1 on every side so a covering block may hang off the region's bounding box.
    Returns (padded, off) with cell (i, j) of `mask` at (i + off, j + off) of `padded`."""
    off = K - 1
    ny, nx = mask.shape
    out = np.zeros((ny + 2 * off, nx + 2 * off), bool)
    out[off:off + ny, off:off + nx] = mask
    return out, off


def greedy_cover(mask, K):
    """repeatedly take the block covering the most still-uncovered cells."""
    U = mask.copy()
    pieces = []
    while U.any():
        cnt = _window_counts(U, K)
        j0, i0 = np.unravel_index(int(np.argmax(cnt)), cnt.shape)
        if cnt[j0, i0] <= 0:
            break
        U[j0:j0 + K, i0:i0 + K] = False
        pieces.append((int(i0), int(j0)))
    return pieces


def prune_cover(mask, K, pieces):
    """drop any piece whose cells are covered by the others (greedy leaves a few)."""
    out = list(pieces)
    i = 0
    while i < len(out):
        trial = out[:i] + out[i + 1:]
        cov = np.zeros_like(mask)
        for (a, b) in trial:
            cov[b:b + K, a:a + K] = True
        if not (mask & ~cov).any():
            out = trial
        else:
            i += 1
    return out


def greedy_independent(mask, K):
    """cells pairwise L-infinity >= K apart in cell units: no K x K block holds two of them, so
    their number is a LOWER bound on the cover number."""
    U = mask.copy()
    pts = []
    while U.any():
        j, i = (int(v) for v in np.unravel_index(int(np.argmax(U)), U.shape))
        pts.append((i, j))
        U[max(0, j - K + 1):j + K, max(0, i - K + 1):i + K] = False
    return pts


def separated_floor(reg, mask, sep=1.0):
    """a greedy 1-separated set of CELL CENTRES inside the region: a lower bound on how many unit
    squares could conceivably still be placed, hence on any cover number."""
    U = mask.copy()
    X, Y = np.meshgrid(reg.xs, reg.ys)
    pts = []
    while U.any():
        j, i = (int(v) for v in np.unravel_index(int(np.argmax(U)), U.shape))
        cx, cy = reg.xs[i], reg.ys[j]
        pts.append((float(cx), float(cy)))
        U &= ~(((X - cx) ** 2 + (Y - cy) ** 2) < sep * sep)
    return pts


def separated_floor_tc(reg, mask, th):
    """the Lemma-TC analogue of `separated_floor`: a greedy set of cell centres of F_outer pairwise
    at L-infinity distance >= 1 IN THE FRAME th.  Its size is a lower bound on how many same-tilt-t
    squares the region could hold, hence on every TC cover number at that tilt."""
    jj, ii = np.nonzero(mask)
    if len(ii) == 0:
        return []
    x = reg.xs[ii]
    y = reg.ys[jj]
    c, s = math.cos(th), math.sin(th)
    u = x * c + y * s
    v = -x * s + y * c
    live = np.ones(len(u), bool)
    pts = []
    while live.any():
        k = int(np.argmax(live))
        pts.append((float(x[k]), float(y[k])))
        live &= ~((np.abs(u - u[k]) < 1.0) & (np.abs(v - v[k]) < 1.0))
    return pts


# ===================================================================== exact minimum cover
def min_cover(mask, K, limit, node_cap=60000):
    """EXACT minimum number of K x K blocks covering `mask`, by iterative deepening + branch and
    bound.  Returns (k, pieces) with k <= limit, or (None, None) if the minimum exceeds `limit`
    (or the node cap was hit -- then `hit_cap` is set on the returned dict-free tuple via the
    module-level MIN_COVER_STATS).

    Canonicalisation.  Let (i, j) be the uncovered cell with the smallest column, ties by row.
    Every cell with a smaller column is already covered, so any block covering (i, j) may be slid
    right until its left edge is at column i without losing an uncovered cell: WLOG i0 = i.  For
    the row anchor, j0 ranges over the rows [j - K + 1, j] that carry an uncovered cell inside the
    column band -- at most K branches per level.
    """
    global MIN_COVER_STATS
    ny, nx = mask.shape
    lb0 = len(greedy_independent(mask, K))
    stats = dict(lb_indep=lb0, nodes=0, hit_cap=False)

    def first_uncovered(U):
        cols = U.any(0)
        w = np.flatnonzero(cols)
        if len(w) == 0:
            return None
        i = int(w[0])
        j = int(np.flatnonzero(U[:, i])[0])
        return i, j

    def lb(U):
        c = 0
        V = U.copy()
        while V.any():
            j, i = (int(v) for v in np.unravel_index(int(np.argmax(V)), V.shape))
            V[max(0, j - K + 1):j + K, max(0, i - K + 1):i + K] = False
            c += 1
        return c

    def rec(U, budget, acc):
        stats["nodes"] += 1
        if stats["nodes"] > node_cap:
            stats["hit_cap"] = True
            return None
        fu = first_uncovered(U)
        if fu is None:
            return list(acc)
        if budget <= 0:
            return None
        if lb(U) > budget:
            return None
        i, j = fu
        i0 = min(i, nx - K)
        band = U[:, i0:i0 + K]
        rows = np.flatnonzero(band.any(1))
        rows = [int(r) for r in rows if j - K + 1 <= r <= j]
        cand = sorted(set(min(max(0, r), ny - K) for r in rows), reverse=True)
        for j0 in cand:
            keep = U[j0:j0 + K, i0:i0 + K].copy()
            U[j0:j0 + K, i0:i0 + K] = False
            r = rec(U, budget - 1, acc + [(i0, j0)])
            U[j0:j0 + K, i0:i0 + K] = keep
            if r is not None:
                return r
        return None

    for k in range(lb0, limit + 1):
        stats["nodes"] = 0
        res = rec(mask.copy(), k, [])
        if res is not None:
            MIN_COVER_STATS = dict(stats, optimal=k)
            return k, res
        if stats["hit_cap"]:
            MIN_COVER_STATS = dict(stats, optimal=None)
            return None, None
    MIN_COVER_STATS = dict(stats, optimal=None)
    return None, None


MIN_COVER_STATS = {}


# ===================================================================== the tilted (Lemma TC) cover
def rotated_mask(reg, mask, th, pitch=None):
    """rasterise F_outer into the frame rotated by `th`: a rotated cell is marked OPEN whenever it
    meets the bounding box of some open axis cell's image, so the result CONTAINS the image of
    F_outer (sound over-approximation).  Returns (mask2, u0, v0, p2)."""
    p = reg.pitch if pitch is None else pitch
    c, s = math.cos(th), math.sin(th)
    n = mask.shape[0]
    jj, ii = np.nonzero(mask)
    if len(ii) == 0:
        return np.zeros((1, 1), bool), 0.0, 0.0, p
    x0 = ii * p
    y0 = jj * p
    xs = np.stack([x0, x0 + p, x0, x0 + p], 1)
    ys = np.stack([y0, y0, y0 + p, y0 + p], 1)
    U = xs * c + ys * s
    V = -xs * s + ys * c
    umin, umax = U.min(1), U.max(1)
    vmin, vmax = V.min(1), V.max(1)
    u0, v0 = float(umin.min()), float(vmin.min())
    nu = int(math.ceil((float(umax.max()) - u0) / p)) + 2
    nv = int(math.ceil((float(vmax.max()) - v0) / p)) + 2
    m2 = np.zeros((nv, nu), bool)
    a = np.floor((umin - u0) / p).astype(int)
    b = np.ceil((umax - u0) / p).astype(int)
    cc = np.floor((vmin - v0) / p).astype(int)
    d = np.ceil((vmax - v0) / p).astype(int)
    for k in range(len(a)):
        m2[cc[k]:d[k] + 1, a[k]:b[k] + 1] = True
    return m2, u0, v0, p


def tc_K(p, delta, eps=1e-9):
    """largest K with a K x K block of pitch-p cells admissible for Lemma TC over a tilt window of
    half-width `delta`: side K p, and K p (1 + delta) < 1."""
    return max(0, int(math.floor((1.0 - eps) / (p * (1.0 + delta)))))


def tc_cover(reg, mask, th, delta, exact_limit=0):
    """cover number of F_outer by squares of side K*p in the frame `th`, sound for every common
    tilt within `delta` of `th`."""
    m2, u0, v0, p2 = rotated_mask(reg, mask, th)
    K = max(1, tc_K(p2, delta))
    mp, off = pad_for(m2, K)
    pieces = prune_cover(mp, K, greedy_cover(mp, K))
    lb = len(greedy_independent(mp, K))
    out = dict(theta=float(th), delta=float(delta), K=int(K), side=float(K * p2),
               ub=len(pieces), lb_indep=int(lb),
               lb_area=int(math.ceil(float(m2.sum()) * p2 * p2 / (K * p2) ** 2)))
    if exact_limit and lb <= exact_limit:
        k, pc = min_cover(mp, K, min(exact_limit, len(pieces)))
        out["exact"] = k
        out["exact_stats"] = dict(MIN_COVER_STATS)
        if k is not None:
            pieces = pc
            out["ub"] = min(out["ub"], k)
    out["pieces"] = [dict(u=float(u0 + (i0 - off) * p2), v=float(v0 + (j0 - off) * p2),
                          du=float(K * p2), dv=float(K * p2)) for (i0, j0) in pieces]
    return out


# ===================================================================== the node-level price
def price_node(boxes, budget, is_pin=None, exact_limit=8, with_tc=None, floor=True,
               pitch=G.PITCH_TARGET, ntilt=G.NTILT):
    """the whole T1/T2 price of one node."""
    reg, obst, onames, kinds = region_of(boxes, is_pin, pitch, ntilt)
    mask = ~reg.blocked
    K, p = piece_K(reg)
    side = K * p
    ub_pieces = prune_cover(mask, K, greedy_cover(mask, K))
    lb_ind = len(greedy_independent(mask, K))
    area = float(mask.sum()) * reg.pitch ** 2
    lb_area = int(math.ceil(area / float(side) ** 2))
    lb = max(lb_ind, lb_area)
    out = dict(n=int(mask.shape[0]), pitch=float(reg.pitch), margin=float(reg.margin),
               ntilt=int(reg.ntilt), K=int(K), side=float(side),
               side_num=int(side.numerator), side_den=int(side.denominator),
               admissible=bool(2 * side ** 2 < 1),
               area_open=area, area_green=reg.area_green(),
               budget=int(budget), lb_area=lb_area, lb_indep=lb_ind, lb=lb,
               ub_greedy=len(ub_pieces), pieces=[[int(a), int(b)] for a, b in ub_pieces])
    if lb <= exact_limit and lb <= len(ub_pieces):
        k, pc = min_cover(mask, K, min(exact_limit, len(ub_pieces)))
        out["exact"] = k
        out["exact_stats"] = dict(MIN_COVER_STATS)
        if k is not None:
            out["pieces"] = [[int(a), int(b)] for a, b in pc]
            out["ub_greedy"] = min(out["ub_greedy"], k)
    cover = out.get("exact") or out["ub_greedy"]
    out["cover"] = int(cover)
    out["kills"] = bool(cover < budget)
    out["margin_vs_budget"] = int(cover) - int(budget)
    if floor:
        fl = separated_floor(reg, mask)
        out["floor_green"] = len(separated_floor(reg, reg.green))
        out["floor_1sep"] = len(fl)
        out["floor_pts"] = [[round(x, 6), round(y, 6)] for x, y in fl[:20]]
        out["floor_kills_leaf"] = bool(len(fl) >= budget)
    if with_tc is not None:
        out["tc"] = []
        for (th, dl) in with_tc["frames"]:
            r = tc_cover(reg, mask, th, dl, exact_limit=with_tc.get("exact_limit", 0))
            r["floor_tc"] = len(separated_floor_tc(reg, mask, th))
            r["cover"] = int(r.get("exact") or r["ub"])
            r["kills"] = bool(r["cover"] < budget)
            out["tc"].append(r)
        best = min(x["cover"] for x in out["tc"])
        worst = max(x["cover"] for x in out["tc"])
        out["tc_cover_min"], out["tc_cover_max"] = int(best), int(worst)
        out["tc_floor_min"] = int(min(x["floor_tc"] for x in out["tc"]))
        out["tc_kills_sound"] = bool(worst < budget)
    return out, reg, obst, onames, kinds
