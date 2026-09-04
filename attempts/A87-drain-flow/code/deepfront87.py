"""deepfront87.py -- A87 chore: DIRECTED search for the DEEP-CORNER frontier.

PI conjecture under test: in a K0-BLOCKED packing (every corner's open unit slot
met by >= 2 squares, hence no simple square) at side sigma <= s_hat, at least one
corner has BOTH intruders shallower than delta -- in particular
    D := min_c d1(c) < delta,      d1(c) = depth of the DEEPEST intruder at c,
with depth = 1 - f_min_max in the corner frame (A89 t2b_depth / depthdist87).

The A87 corpus has only 5 exact K0-BLOCKED packings and all have min_c d1 < 0.1,
but none of them was OPTIMISED for depth: they are endpoints of a side-MINIMISING
flow.  This module maximises D directly, on a grid of side caps, so the frontier
D*(sigma) can be read off instead of guessed.

Formulation
  variables  x = (c(22), th(11), s)   -- cp85's 34-vector
  feasible   55 pair SAT rows >= GF, 44 container rows >= GF, s <= cap
  K0 rows    the two deepest intruders per corner pinned at SAT depth >= EPS_KEEP
             (guarantees n_block >= 2 at all four corners, i.e. K0-BLOCKED)
  objective  minimise G = softmax_gamma over the pinned targets of
             F(target) = a SMOOTH UPPER BOUND on f_min_max of that (corner,square)
             so that  min over targets of depth  >=  1 - G  ALWAYS.
             mode 'd1': one target per corner (the deepest intruder)  -> D = min_c d1
             mode 'd2': two targets per corner (both intruders)      -> min_c d2

  Depths are measured in the CONTAINER frame (corners 0 / s-1).  The tight
  bounding box is a SUBSET of the container, so the certified bbox-frame depth of
  the answer is >= the optimised container-frame depth and the certified side is
  <= s: both directions are conservative, and the reported certificate is the
  bbox-frame one produced by k0dir87.exact_blocked_test + depthdist87.corner_depths.

Pipeline per seed
  (0) k0dir87.build_seed  (A85 BL pair census, 2 intruders per corner + 3 middles)
  (1) k0dir87.sqp_flow(keep_k0=True) compresses the side to <= the largest cap
  (2) LADDER down the cap grid: at each cap, compress if needed, then run the
      depth ascent (trust-region SLSQP on G); carry the deep point to the next cap
  (3) the best point per cap goes through the EXACT certificate

Writes only  results/deepfront87.*  and  notes/deepfront87.md.
Usage: python deepfront87.py {selftest|canary|pilot|run|d2|report|all}
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
A85 = os.path.join(ATT, 'A85-k0-route')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A85, 'code'))

import cp85                       # noqa: E402
import fjpolish87 as F            # noqa: E402
import k0blocked87 as KB          # noqa: E402
import k0dir87 as K               # noqa: E402
import depthdist87 as DD          # noqa: E402
import t3lib as T                 # noqa: E402

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
LOGS = os.path.join(A87, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

OUT_JL = os.path.join(RESULTS, 'deepfront87.jsonl')
OUT_JS = os.path.join(RESULTS, 'deepfront87.json')
OUT_D2 = os.path.join(RESULTS, 'deepfront87.d2.json')
OUT_MD = os.path.join(NOTES, 'deepfront87.md')

N = 11
H = 0.5
CORNERS = K.CORNERS
S_HAT = F.S_HAT

GRID = (4.40, 4.20, 4.10, 4.05, 4.00, 3.95, 3.90)   # LADDER order: descending
GRID_UP = tuple(sorted(GRID))

EPS_KEEP = 1e-4          # SAT depth floor on the two pinned intruders per corner
GF = 5e-10               # strict-feasibility floor on pair / container rows
TOL_BLOCK = K.TOL_BLOCK  # 1e-9

TRUST0 = 0.10
TRUST_MIN = 3e-8
ROUNDS_ASC = 46          # depth-ascent rounds per cap
ROUNDS_CMP = 26          # compression rounds per cap step
ROUNDS_CMP0 = 60         # first compression, from the raw seed
BETA0, BETA1 = 120.0, 4000.0

_SG = np.array([[1., 1.], [1., -1.], [-1., -1.], [-1., 1.]])
# X = ax*px + bx*s ,  Y = ay*py + by*s   in the corner frame of the container
CSIGN = {'BL': (1.0, 0.0, 1.0, 0.0), 'BR': (-1.0, 1.0, 1.0, 0.0),
         'TL': (1.0, 0.0, -1.0, 1.0), 'TR': (-1.0, 1.0, -1.0, 1.0)}
_AR = np.arange(N)


# ==================================================================== geometry

def verts(x):
    """P[j,k,:] = vertex k of square j;  Dth[j,k,:] = d P / d theta_j."""
    c, th, s = cp85.unpack(x)
    co, si = np.cos(th), np.sin(th)
    gx = _SG[:, 0][None, :]
    gy = _SG[:, 1][None, :]
    CO = co[:, None]
    SI = si[:, None]
    P = np.empty((N, 4, 2))
    D = np.empty((N, 4, 2))
    P[:, :, 0] = c[:, 0][:, None] + H * (gx * CO - gy * SI)
    P[:, :, 1] = c[:, 1][:, None] + H * (gx * SI + gy * CO)
    D[:, :, 0] = H * (-gx * SI - gy * CO)
    D[:, :, 1] = H * (gx * CO - gy * SI)
    return P, D, float(s)


def depth_table(x):
    """depth[ci, j] = 1 - min over square j of max(X, Y) in corner ci's frame,
    and carg[ci, j] = the achieving candidate (0..3 vertex, 4..7 edge crossing).

    max(X,Y) is convex with no local minimum, so its minimum over the (convex,
    compact) square lies on the boundary, and on each edge it is a max of two
    affine functions: the minimum is at a vertex or at the crossing X = Y.
    Same candidate set as depthdist87.f_minmax_iv, in floats."""
    P, _D, s = verts(x)
    depth = np.empty((4, N))
    carg = np.empty((4, N), dtype=int)
    for ci, cn in enumerate(CORNERS):
        ax, bx, ay, by = CSIGN[cn]
        X = ax * P[:, :, 0] + bx * s
        Y = ay * P[:, :, 1] + by * s
        cand = np.empty((N, 8))
        cand[:, :4] = np.maximum(X, Y)
        d = X - Y
        for k in range(4):
            kn = (k + 1) % 4
            d0, d1 = d[:, k], d[:, kn]
            ok = ((d0 < 0.0) & (d1 > 0.0)) | ((d0 > 0.0) & (d1 < 0.0))
            den = np.where(ok, d0 - d1, 1.0)
            t = np.where(ok, d0 / den, 0.0)
            cand[:, 4 + k] = np.where(ok, X[:, k] + t * (X[:, kn] - X[:, k]), np.inf)
        a = np.argmin(cand, axis=1)
        depth[ci] = 1.0 - cand[_AR, a]
        carg[ci] = a
    return depth, carg


def score(x, mode):
    """The TRUE objective being maximised (container frame, floats).

    'd1': min over corners of the deepest depth.
    'd2': min over corners of the SECOND deepest depth (both intruders deep)."""
    dt, _ca = depth_table(x)
    srt = np.sort(dt, axis=1)[:, ::-1]
    return float(srt[:, 0].min()) if mode == 'd1' else float(srt[:, 1].min())


def pick_targets(dt, mode):
    """(ci, j) pairs the objective drives: the deepest per corner ('d1') or the
    two deepest per corner ('d2')."""
    out = []
    for ci in range(4):
        order = np.argsort(-dt[ci])
        out.append((ci, int(order[0])))
        if mode == 'd2':
            out.append((ci, int(order[1])))
    return out


def _term(P, D, s, ci, j, a, beta):
    """SMOOTH UPPER BOUND on f_min_max of square j at corner ci, plus its
    gradient in [d/dcx, d/dcy, d/dth, d/ds].  Upper bound because (i) it uses a
    single candidate (min over candidates <= this one) and (ii) softmax >= max."""
    ax, bx, ay, by = CSIGN[CORNERS[ci]]

    def XY(k):
        Xv = ax * P[j, k, 0] + bx * s
        Yv = ay * P[j, k, 1] + by * s
        gX = np.array([ax, 0.0, ax * D[j, k, 0], bx])
        gY = np.array([0.0, ay, ay * D[j, k, 1], by])
        return Xv, Yv, gX, gY

    if a < 4:
        Xv, Yv, gX, gY = XY(a)
        m = max(Xv, Yv)
        e0 = math.exp(beta * (Xv - m))
        e1 = math.exp(beta * (Yv - m))
        S = e0 + e1
        val = m + math.log(S) / beta
        return val, (e0 / S) * gX + (e1 / S) * gY
    k = a - 4
    kn = (k + 1) % 4
    Xa, Ya, gXa, gYa = XY(k)
    Xb, Yb, gXb, gYb = XY(kn)
    d0, d1 = Xa - Ya, Xb - Yb
    gd0, gd1 = gXa - gYa, gXb - gYb
    den = d0 - d1
    if abs(den) < 1e-14:            # degenerate: fall back to the vertex branch
        m = max(Xa, Ya)
        return m, (gXa if Xa >= Ya else gYa)
    t = d0 / den
    gt = (-d1 * gd0 + d0 * gd1) / (den * den)
    val = Xa + t * (Xb - Xa)
    return val, gXa + gt * (Xb - Xa) + t * (gXb - gXa)


def term_rows(x, targets, cands, beta):
    """vals[m] = smooth upper bound on f_min_max of target m, J[m] its gradient."""
    P, D, s = verts(x)
    M = len(targets)
    vals = np.empty(M)
    J = np.zeros((M, 3 * N + 1))
    for m, ((ci, j), a) in enumerate(zip(targets, cands)):
        v, g = _term(P, D, s, ci, j, int(a), beta)
        vals[m] = v
        J[m, 2 * j] = g[0]
        J[m, 2 * j + 1] = g[1]
        J[m, 2 * N + j] = g[2]
        J[m, 3 * N] = g[3]
    return vals, J


def obj_soft(x, targets, cands, beta, gamma):
    """G = softmax_gamma over the targets of the smooth f_min_max upper bound.
    G >= max over targets of f_min_max, hence  depth(target) >= 1 - G  for ALL
    targets: minimising G maximises a GUARANTEED lower bound on the score."""
    P, D, s = verts(x)
    vals = np.empty(len(targets))
    gs = []
    for m, ((ci, j), a) in enumerate(zip(targets, cands)):
        v, g = _term(P, D, s, ci, j, int(a), beta)
        vals[m] = v
        gs.append((j, g))
    mx = float(vals.max())
    e = np.exp(gamma * (vals - mx))
    S = float(e.sum())
    G = mx + math.log(S) / gamma
    w = e / S
    grad = np.zeros(3 * N + 1)
    for m, (j, g) in enumerate(gs):
        grad[2 * j] += w[m] * g[0]
        grad[2 * j + 1] += w[m] * g[1]
        grad[2 * N + j] += w[m] * g[2]
        grad[3 * N] += w[m] * g[3]
    return G, grad


# ================================================================ feasibility

def k0_container(x):
    """Container-frame blocker counts and the two deepest SAT depths per corner."""
    gaps, args, _g, _a = K.slot_gaps(x, use_bbox=False)
    depth = -gaps
    nb = (gaps < -TOL_BLOCK).sum(axis=1)
    srt = np.sort(depth, axis=1)[:, ::-1]
    return (np.array([int(v) for v in nb]), srt[:, 0], srt[:, 1],
            bool(nb.min() >= 2))


def ok_point(x, need_k0=True, floor=0.4):
    """Strictly feasible AND (optionally) K0-BLOCKED in the container frame."""
    if not np.all(np.isfinite(x)):
        return False
    ov, cv = cp85.feasibility(x)
    if not (ov <= -floor * GF and cv <= -floor * GF):
        return False
    if not need_k0:
        return True
    _nb, _m1, m2, blk = k0_container(x)
    return bool(blk and m2.min() >= floor * EPS_KEEP)


# ============================================================== depth ascent

def asc_step(x, targets, cands, beta, gamma, delta, cap, keep_k0, maxiter=32):
    """One trust-region SLSQP move minimising G."""
    ov, _aux = cp85.pair_overlaps(x)
    kfix = np.argmin(ov, axis=1)

    def pc(z, k=kfix):
        v, J = K.pair_con_fast(z, k)
        return v - GF, J

    def cc(z):
        v, J = K.cont_con_fast(z)
        return v - GF, J

    cp = K._Cache(pc)
    cq = K._Cache(cc)
    cons = [dict(type='ineq', fun=cp.val, jac=cp.jac),
            dict(type='ineq', fun=cq.val, jac=cq.jac)]
    if keep_k0:
        sel = K.select_k0(x)
        ck = K._Cache(lambda z, q=sel: K.k0_cons(z, q))
        cons.append(dict(type='ineq', fun=ck.val, jac=ck.jac))
    lo = x - delta
    hi = x + delta
    hi[3 * N] = min(hi[3 * N], cap)
    lo[3 * N] = max(lo[3 * N], 2.5)
    bnds = list(zip(lo, hi))
    fc = K._Cache(lambda z, t=targets, a=cands: obj_soft(z, t, a, beta, gamma))
    try:
        res = minimize(fc.val, x, jac=fc.jac, constraints=cons, bounds=bnds,
                       method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-14))
    except Exception:
        return None
    y = np.asarray(res.x, float).copy()
    return y if np.all(np.isfinite(y)) else None


def ascend(x0, cap, mode, rounds=ROUNDS_ASC, keep_k0=True):
    """Trust-region ascent on the true score.  Returns (best x, best score, steps)."""
    x = np.asarray(x0, float).copy()
    if x[3 * N] > cap + 1e-12 or not ok_point(x, need_k0=keep_k0):
        return None, None, 0
    cur = score(x, mode)
    best = (cur, x.copy())
    delta = TRUST0
    nstep = 0
    for r in range(rounds):
        if delta < TRUST_MIN:
            break
        u = r / max(1, rounds - 1)
        beta = BETA0 * (BETA1 / BETA0) ** u
        dt, ca = depth_table(x)
        targets = pick_targets(dt, mode)
        cands = [ca[ci, j] for (ci, j) in targets]
        y = asc_step(x, targets, cands, beta, beta, delta, cap, keep_k0)
        if y is None or not ok_point(y, need_k0=keep_k0):
            delta *= 0.4
            continue
        sc = score(y, mode)
        if sc <= cur + 1e-13:
            delta *= 0.4
            continue
        x = y
        cur = sc
        nstep += 1
        if cur > best[0]:
            best = (cur, x.copy())
        delta = min(TRUST0, delta * 1.7)
    return best[1], best[0], nstep


# ============================================== frontier squeeze (side down at
# ============================================== a held depth floor)

def sq_step(x, targets, cands, beta, dfloor, delta, maxiter=40, keep_k0=True):
    """One trust-region SLSQP move MINIMISING s with every target's depth held
    at >= dfloor (the smooth upper bound F <= 1 - dfloor is the SOUND side of the
    inequality, so the true depth stays above the floor)."""
    ov, _aux = cp85.pair_overlaps(x)
    kfix = np.argmin(ov, axis=1)
    cp = K._Cache(lambda z, k=kfix: (lambda vj: (vj[0] - GF, vj[1]))(
        K.pair_con_fast(z, k)))
    cq = K._Cache(lambda z: (lambda vj: (vj[0] - GF, vj[1]))(K.cont_con_fast(z)))
    sel = K.select_k0(x)
    ck = K._Cache(lambda z, q=sel: K.k0_cons(z, q))
    cd = K._Cache(lambda z, t=targets, a=cands: (lambda vj:
                  ((1.0 - dfloor) - vj[0], -vj[1]))(term_rows(z, t, a, beta)))
    cons = [dict(type='ineq', fun=cp.val, jac=cp.jac),
            dict(type='ineq', fun=cq.val, jac=cq.jac),
            dict(type='ineq', fun=cd.val, jac=cd.jac)]
    if keep_k0:
        cons.append(dict(type='ineq', fun=ck.val, jac=ck.jac))
    bnds = [(v - delta, v + delta) for v in x]
    e = np.eye(3 * N + 1)[3 * N]
    try:
        res = minimize(lambda z: z[3 * N], x, jac=lambda z: e, constraints=cons,
                       bounds=bnds, method='SLSQP',
                       options=dict(maxiter=maxiter, ftol=1e-14))
    except Exception:
        return None
    y = np.asarray(res.x, float).copy()
    return y if np.all(np.isfinite(y)) else None


def squeeze(x0, cap, mode, dgive=0.02, rounds=44, beta=1500.0, keep_k0=True):
    """Drive s down towards cap while holding the score within dgive of its
    current value.  Returns (x, s, score)."""
    x = np.asarray(x0, float).copy()
    cur = score(x, mode)
    floor = max(0.0, cur - dgive)
    delta = TRUST0
    for _r in range(rounds):
        if x[3 * N] <= cap or delta < TRUST_MIN:
            break
        dt, ca = depth_table(x)
        targets = pick_targets(dt, mode)
        cands = [ca[ci, j] for (ci, j) in targets]
        y = sq_step(x, targets, cands, beta, floor, delta, keep_k0=keep_k0)
        if y is None or not ok_point(y, need_k0=keep_k0):
            delta *= 0.4
            continue
        if y[3 * N] >= x[3 * N] - 1e-12 or score(y, mode) < floor - 1e-9:
            delta *= 0.4
            continue
        x = y
        delta = min(TRUST0, delta * 1.7)
    return x, float(x[3 * N]), score(x, mode)


# =============================================================== compression

def compress(x, target, rounds=ROUNDS_CMP, chunk=7):
    """k0dir87's K0-confined side minimisation, run until the enclosing side is
    <= target (or progress stops).  Returns (x, side) with x K0-BLOCKED."""
    xb = np.asarray(x, float).copy()
    side = K.enclosing_side_x(xb)
    done = 0
    while side > target and done < rounds:
        xe, best, _em, _ns, _sel = K.sqp_flow(xb, keep_k0=True, rounds=chunk)
        done += chunk
        if best is None:
            break
        if best[0] >= side - 1e-12:
            xb, side = best[1], best[0]
            break
        xb, side = best[1], best[0]
    return xb, float(side)


def to_container(x):
    """Normalise so the container is the tight bounding box (F.canonical) -- the
    container-frame depths then agree with the bbox-frame ones to 1e-9."""
    z = F.inflate(F.canonical(K.x_to_z(x)), target=4.0 * GF)
    return K.z_to_x(z)


# ======================================================= DIRECTED "deep" seeds
# The census seeds of k0dir87 are drawn for a side-MINIMISING flow and land in
# shallow basins (a local ascent from them stalls near D ~ 0.4).  A directed
# search needs seeds that are already deep, so the corner gadget below is built
# from the geometry of the deep-corner limit.
#
# In the BL corner frame:
#   A = axis-aligned unit square [eps, 1+eps] x [0, 1]  ->  f_min_max = eps,
#       so A intrudes the open slot to depth d1 = 1 - eps.
#   The only part of the slot A leaves free is the strip (0, eps) x (0, 1),
#       which no square can reach from BELOW (y < 0 is outside), so the second
#       intruder must WRAP the reflex corner (eps, 1): it is a square tilted by
#       phi > 0 whose lower-left vertex sits at (m + sin phi, 1 - delta) with
#       m + sin phi < eps, its bottom edge climbing over A's top edge.
#   Disjointness from A forces (eps - m - sin phi) tan phi >= delta, so the second
#       depth is at most eps^2 / 4 (at phi = eps/2): d1 -> 1 buys d2 -> 0
#       QUADRATICALLY.  eps >= 0.04 is what the EPS_KEEP = 1e-4 floor allows.
# The four gadgets are carried to the other corners by the D4 maps, each corner
# independently either as built ('L': the wrapper hugs the side wall) or
# transposed across the corner diagonal ('B': it hugs the bottom wall).

def gadget(eps, transpose, m=1e-7, frac=0.45):
    """(A, B) = (cx, cy, theta) of the two squares of one BL-frame corner gadget."""
    phi = 0.5 * eps
    e = H * (math.cos(phi) + math.sin(phi))
    dmax = (eps - m - math.sin(phi)) * math.tan(phi)
    if dmax <= 1e-12:
        return None
    delta = frac * dmax
    A = (0.5 + eps, 0.5 + m, 0.0)
    B = (e + m, 1.0 - delta + e, phi)
    if transpose:                      # reflect across y = x
        A = (A[1], A[0], -A[2])
        B = (B[1], B[0], -B[2])
    return A, B


def gadget2(theta, m=1e-7, eta=2e-3):
    """The BOTH-INTRUDERS-DEEP corner motif: two squares tilted +-theta about the
    corner diagonal, separated by (nearly) a shared edge ON that diagonal.

    Reference computation.  Let a unit square S lie in the wedge {0 <= y <= x}
    (the half of the corner quadrant on one side of the diagonal).  There
    max(x,y) = x, so f_min_max(S) = min_S x = cx - e with e = (|cos|+|sin|)/2, and
    the wedge rows  min_S (x - y) >= 0  and  min_S y >= 0  read
        cx - cy >= max(cos theta, sin theta),      cy >= e,
    so f_min_max >= max(cos theta, sin theta) >= 1/sqrt 2, i.e.
        d <= 1 - 1/sqrt(2) = 0.29289321881...
    with EQUALITY at theta = 45 deg, where the square has a whole edge on the
    diagonal and touches one wall.  Mirroring across the diagonal gives the
    partner, so a corner whose two intruders are separated BY THE DIAGONAL has
    min(d1, d2) <= 1 - 1/sqrt 2.  (A separating line that misses the corner point
    only pushes the far square further out, so this is the two-intruder optimum.)
    """
    e = H * (abs(math.cos(theta)) + abs(math.sin(theta)))
    cy = e + m
    cx = cy + max(math.cos(theta), math.sin(theta)) + eta
    A = (cx, cy, theta)
    B = (cy, cx, -theta)
    return A, B


def deep_seed(rng, sigma, eps=None, variants=None, tries=700, outer=14,
              kind='d1'):
    """11 squares in [0, sigma]^2: a deep corner gadget at each of the four
    corners plus 3 rejection-sampled middles.  K0-BLOCKED by construction."""
    for _o in range(outer):
        ee = eps if eps is not None else (
            rng.choice((0.04, 0.05, 0.07, 0.10, 0.14, 0.20, 0.28, 0.40))
            if kind == 'd1' else
            math.radians(rng.choice((45.0, 40.0, 35.0, 30.0, 25.0, 20.0, 15.0))))
        vv = variants if variants is not None else tuple(
            rng.random() < 0.5 for _ in range(4))
        cs, ts = [], []
        bad = False
        for ci, cn in enumerate(CORNERS):
            g = gadget(ee, vv[ci]) if kind == 'd1' else gadget2(ee)
            if g is None:
                bad = True
                break
            for (cx, cy, t) in g:
                X, Y, T_ = K._corner_map(cn, cx, cy, t, sigma)
                cs.append([X, Y])
                ts.append(T_)
        if bad:
            continue
        for i in range(8):
            for j in range(i + 1, 8):
                if not K._pair_disjoint((cs[i][0], cs[i][1]), ts[i],
                                        (cs[j][0], cs[j][1]), ts[j]):
                    bad = True
                    break
            if bad:
                break
        if bad:
            continue
        ok = True
        for _k in range(3):
            got = False
            for _t in range(tries):
                T_ = rng.uniform(0.0, K.HALFPI)
                ex = H * (abs(math.cos(T_)) + abs(math.sin(T_))) + 1e-7
                X = rng.uniform(ex, sigma - ex)
                Y = rng.uniform(ex, sigma - ex)
                if all(K._pair_disjoint((X, Y), T_, (cs[q][0], cs[q][1]), ts[q])
                       for q in range(len(cs))):
                    cs.append([X, Y])
                    ts.append(T_)
                    got = True
                    break
            if not got:
                ok = False
                break
        if not ok:
            continue
        x = cp85.pack(np.array(cs), np.array(ts), float(sigma))
        if ok_point(x):
            return x
    return None


# ============================================================== certification

def certify(x, ladder=(40, 80, 160)):
    """EXACT certificate of a candidate: rational z, interval SAT gaps, certified
    per-corner blocker counts, and outward-rounded depth enclosures."""
    z = K.x_to_z(x)
    zf = K.zfrac_of(z)
    ver = F.verify_exact(zf)
    blk = K.exact_blocked_test(zf)
    bl = {cn: blk['per_corner'][cn]['blockers'] for cn in CORNERS}
    dep, side_mid, dps, worst_w, nskip, clean = DD.corner_depths(zf, bl, ladder)
    per = {}
    d1lo, d1hi, d2lo, d2hi = [], [], [], []
    for cn in CORNERS:
        r1, r2, bs = DD.d12(dep[cn])
        rec = {'n_block_certified': len(bs)}
        if r1 is not None:
            rec.update(d1=r1['depth'], d1_lo=r1['depth_lo'], d1_hi=r1['depth_hi'],
                       d1_sq=r1['sq'], d1_tilt_deg=r1['tilt_deg'],
                       d1_tilt_lo=r1['tilt_deg_lo'], d1_tilt_hi=r1['tilt_deg_hi'])
            d1lo.append(r1['depth_lo'])
            d1hi.append(r1['depth_hi'])
        if r2 is not None:
            rec.update(d2=r2['depth'], d2_lo=r2['depth_lo'], d2_hi=r2['depth_hi'],
                       d2_sq=r2['sq'], d2_tilt_deg=r2['tilt_deg'])
            d2lo.append(r2['depth_lo'])
            d2hi.append(r2['depth_hi'])
        per[cn] = rec
    out = {
        'z': [str(v) for v in zf],
        'sigma_certified_upper': ver['side_upper_bound'],
        'min_pair_gap_lower': ver['min_pair_gap_lower_bound'],
        'disjoint_certified': ver['disjoint_certified'],
        'n_block_certified': blk['n_block_certified'],
        'K0_BLOCKED_certified': blk['K0_BLOCKED_certified'],
        'n_unknown': blk['n_unknown'],
        'blk_dps': blk['dps'], 'depth_dps': dps,
        'depth_width_max': worst_w, 'depth_skipped': nskip, 'depth_clean': clean,
        'per_corner': per,
        'D_min_d1_lo': min(d1lo) if len(d1lo) == 4 else None,
        'D_min_d1_hi': min(d1hi) if len(d1hi) == 4 else None,
        'D2_min_d2_lo': min(d2lo) if len(d2lo) == 4 else None,
        'D2_min_d2_hi': min(d2hi) if len(d2hi) == 4 else None,
        'below_s_hat': bool(ver['side_upper_bound'] < S_HAT),
    }
    out['VERIFIED'] = bool(out['disjoint_certified'] and out['K0_BLOCKED_certified']
                           and out['n_unknown'] == 0 and clean
                           and out['D_min_d1_lo'] is not None)
    return out


# ==================================================================== selftest

def _fd_grad(f, x, h=1e-7):
    g = np.zeros(len(x))
    for i in range(len(x)):
        a = x.copy(); a[i] += h
        b = x.copy(); b[i] -= h
        g[i] = (f(a) - f(b)) / (2 * h)
    return g


def selftest(log=print):
    fails = []
    rng = random.Random(4242)

    # ---- (1) depth_table agrees with the EXACT interval depth of depthdist87 on
    #          Trump (three depth-1 corners) and on a random packing.
    it = DD.trump_item()
    zt = it['z']
    xt = K.z_to_x([float(v) for v in zt])
    dt, ca = depth_table(xt)
    dep, _sd, _dp, _ww, _nk, _cl = DD.corner_depths(
        zt, {cn: list(range(N)) for cn in CORNERS}, (40, 80))
    worst = 0.0
    for ci, cn in enumerate(CORNERS):
        for r in dep[cn]:
            worst = max(worst, abs(r['depth'] - dt[ci, r['sq']]))
    log('  depth_table vs exact interval depth (trump, 44 rows): max |diff| = %.3e'
        % worst)
    if worst > 1e-9:
        fails.append('depth_table disagrees with depthdist87 on trump (%.3e)' % worst)
    d1s = sorted(round(float(dt[ci].max()), 9) for ci in range(4))
    log('  trump per-corner d1 = %s' % (d1s,))
    if not (abs(d1s[-1] - 1.0) < 1e-9 and abs(d1s[0] - 0.168321) < 1e-4):
        fails.append('trump d1 pattern wrong: %s' % (d1s,))

    # ---- (2) analytic gradient of obj_soft vs central differences
    K.pool(rng, n=120)
    x = None
    for _ in range(40):
        x = K.build_seed(rng)
        if x is not None:
            break
    if x is None:
        fails.append('selftest: no seed')
        return fails
    dt, ca = depth_table(x)
    for mode in ('d1', 'd2'):
        tg = pick_targets(dt, mode)
        cd = [ca[ci, j] for (ci, j) in tg]
        for beta in (150.0, 3000.0):
            G, g = obj_soft(x, tg, cd, beta, beta)
            gf = _fd_grad(lambda w: obj_soft(w, tg, cd, beta, beta)[0], x)
            rel = np.max(np.abs(g - gf)) / max(1.0, np.max(np.abs(gf)))
            log('  grad check mode=%s beta=%-6g  G=%.9f  max rel err %.2e'
                % (mode, beta, G, rel))
            if rel > 2e-5:
                fails.append('gradient mismatch mode=%s beta=%g rel=%.2e'
                             % (mode, beta, rel))

    # ---- (3) G is an UPPER bound on the pinned f_min_max (i.e. 1-G <= score)
    bad = 0
    for _ in range(30):
        y = K.build_seed(rng)
        if y is None:
            continue
        dt, ca = depth_table(y)
        for mode in ('d1', 'd2'):
            tg = pick_targets(dt, mode)
            cd = [ca[ci, j] for (ci, j) in tg]
            G, _g = obj_soft(y, tg, cd, 2000.0, 2000.0)
            if 1.0 - G > score(y, mode) + 1e-12:
                bad += 1
    log('  soft bound 1-G <= true score: %d violations' % bad)
    if bad:
        fails.append('softmax bound violated %d times' % bad)

    # ---- (4) candidate set: brute-force min of max(X,Y) over a dense boundary
    #          sample must not beat depth_table
    y = x
    P, _D, s = verts(y)
    dt, _ca = depth_table(y)
    worst = 0.0
    for ci, cn in enumerate(CORNERS):
        ax, bx, ay, by = CSIGN[cn]
        for j in range(N):
            fmin = np.inf
            for k in range(4):
                A = P[j, k]; B = P[j, (k + 1) % 4]
                for t in np.linspace(0, 1, 401):
                    p = A + t * (B - A)
                    fmin = min(fmin, max(ax * p[0] + bx * s, ay * p[1] + by * s))
            worst = max(worst, (1.0 - fmin) - dt[ci, j])
    log('  brute-force boundary scan beats depth_table by at most %.3e' % worst)
    if worst > 1e-9:
        fails.append('candidate set incomplete (%.3e)' % worst)

    # ---- (5) the ascent must actually raise the true score, keep feasibility
    #          and keep K0-BLOCKED
    xc, sd = compress(x, 4.40, rounds=40)
    xc = to_container(xc)
    s0 = score(xc, 'd1')
    xa, sa, ns = ascend(xc, 4.40, 'd1', rounds=18)
    log('  ascent: side %.5f  D %.6f -> %.6f in %d steps' % (sd, s0, sa or -9, ns))
    if xa is None or sa <= s0:
        fails.append('ascent made no progress (%.6f -> %s)' % (s0, sa))
    elif not ok_point(xa):
        fails.append('ascent endpoint infeasible or not K0-BLOCKED')
    return fails


# ====================================================================== canary

def canary(log=print, nseed=10, caps=(4.05, 4.00)):
    """With NO K0 constraint and simple squares allowed the optimum is four flush
    SLOT squares, D = 1.  The code must find D -> 1.

    Note on sigma = 4.00 exactly: four corner slot squares + 7 more fill the
    16-cell unit grid of [0,4]^2 EXACTLY, so a STRICTLY feasible D = 1 packing
    needs sigma > 4 (at sigma = 4 it is only an infimum).  The canary therefore
    reports both cap 4.05 and cap 4.00 and passes if either reaches D >= 0.99."""
    rng = random.Random(20260903)
    out = {}
    for cap in caps:
        best = (-9.0, None)
        for i in range(nseed):
            x0 = deep_seed(rng, min(cap, 4.05) if cap < 4.05 else cap)
            if x0 is None:
                x0 = deep_seed(rng, 4.05)
                if x0 is None:
                    continue
            x = x0
            if x[3 * N] > cap:
                x, s1, _sc = squeeze(x, cap, 'd1', dgive=0.9, rounds=30)
                if s1 > cap:
                    continue
            xa, sa, ns = ascend(x, cap, 'd1', rounds=70, keep_k0=False)
            if xa is None:
                continue
            if sa > best[0]:
                best = (sa, xa)
            log('  canary cap %.2f seed %02d: D %.6f -> %.9f (%d steps, s=%.6f)'
                % (cap, i, score(x0, 'd1'), sa, ns, xa[3 * N]))
        out[cap] = best
        log('CANARY cap %.2f: best D = %.9f' % (cap, best[0]))
        if best[1] is not None:
            dt, _ca = depth_table(best[1])
            log('   per-corner d1 = %s'
                % [round(float(dt[ci].max()), 6) for ci in range(4)])
            log('   n_block (container) = %s'
                % (k0_container(best[1])[0].tolist(),))
            log('   s = %.9f  tight side = %.9f'
                % (best[1][3 * N], K.enclosing_side_x(best[1])))
    # how far down can the D = 1 (four slot squares) configuration be squeezed?
    b = out.get(caps[0], (-9.0, None))
    if b[1] is not None:
        y, sy, sc = squeeze(b[1], 3.80, 'd1', dgive=0.01, rounds=60, keep_k0=False)
        ya, sa, _ns = ascend(y, sy + 1e-12, 'd1', rounds=30, keep_k0=False)
        log('CANARY squeeze of the D=1 config (no K0): s %.9f -> %.9f at D = %.9f'
            % (b[1][3 * N], sy, sa if ya is not None else sc))
        log('   (sigma = 4.00 EXACTLY is only an infimum for D = 1: four corner'
            ' slot squares + 7 more fill the 16-cell grid of [0,4]^2 with zero'
            ' slack, so a STRICTLY feasible D = 1 packing needs sigma > 4.)')
    D = max(v[0] for v in out.values())
    ok = D >= 0.99
    log('CANARY %s: best D over caps = %.9f (need >= 0.99)'
        % ('PASS' if ok else 'FAIL', D))
    return ok, D, out


# ==================================================================== campaign

DGIVE = 0.035            # depth the squeeze is allowed to give up per cap step


def _row(cap, x, sa, ns):
    dt, _ca = depth_table(x)
    srt = np.sort(dt, axis=1)[:, ::-1]
    return {'cap': cap, 'score': float(sa), 'steps': ns, 's': float(x[3 * N]),
            'side': float(K.enclosing_side_x(x)),
            'd1': [float(v) for v in srt[:, 0]],
            'd2': [float(v) for v in srt[:, 1]],
            'n_block': k0_container(x)[0].tolist(),
            'x': [float(v) for v in x]}


def ladder(x0, mode, caps=GRID, log=None, keep_k0=True):
    """Walk the cap grid downwards, carrying the deep configuration along:
    SQUEEZE the side down at a held depth floor, then ASCEND at the new cap.
    If the squeeze stalls, fall back to k0dir87's pure side minimisation."""
    out = []
    x = np.asarray(x0, float).copy()
    for cap in caps:
        # bring s down to the cap: hold the depth as long as possible, then give
        # it up in escalating amounts (the frontier is exactly this trade)
        for dg in (DGIVE, 10 * DGIVE):
            if x[3 * N] <= cap + 1e-12:
                break
            y, sy, _sc = squeeze(x, cap, mode, dgive=dg, rounds=22)
            if ok_point(y) and sy < x[3 * N] - 1e-12:
                x = y
            if x[3 * N] <= cap + 1e-12:
                break
            xc, side = compress(x, cap, rounds=18)
            xc = to_container(xc)
            if ok_point(xc) and xc[3 * N] < x[3 * N] - 1e-12:
                x = xc
        if x[3 * N] > cap + 1e-12 or not ok_point(x, need_k0=keep_k0):
            break
        xa, sa, ns = ascend(x, cap, mode, keep_k0=keep_k0)
        if xa is None:
            break
        out.append(_row(cap, xa, sa, ns))
        x = xa
    return out


def campaign(mode='d1', caps=None, nseeds=240, seed=20260903, wall=5400.0,
             log=print, out_json=None, ncert=3, low_target=3.84):
    """Multi-start: DIRECTED gadget seeds (cycling the cap grid) plus k0dir87
    census seeds compressed to the top cap; every seed walks the ladder down."""
    caps = tuple(caps if caps is not None else GRID + (S_HAT,))
    t0 = time.time()
    rng = random.Random(seed)
    bycap = {c: [] for c in caps}
    nrun = {'deep': 0, 'census': 0}
    nseedfail = {'deep': 0, 'census': 0}
    reached = {c: 0 for c in caps}
    jl = OUT_JL if mode == 'd1' else OUT_JL.replace('.jsonl', '.d2.jsonl')
    with open(jl, 'w') as fh:
        for i in range(nseeds):
            if time.time() - t0 > wall:
                log('wall reached after %d seeds' % i)
                break
            # The two arms answer different halves of the frontier.  The GADGET
            # arm owns sigma >= 4.05, where the deep-corner motif fits outright.
            # The CENSUS arm owns the low end: a gadget configuration cannot be
            # compressed below ~4.02 (four corner motifs are wasteful of side),
            # so the only route to a small side is to start from a packing that is
            # ALREADY near-optimal -- a k0dir87 census seed driven all the way down
            # by its K0-confined side minimisation -- and raise the depth THERE.
            fam = 'deep' if (i % 4 == 0) else 'census'
            k0 = 0
            if fam == 'deep':
                kk = (i // 4) % max(1, len(caps) - 3)
                x0 = None
                while x0 is None and kk >= 0:
                    x0 = deep_seed(rng, caps[kk], kind=mode)
                    if x0 is None and mode != 'd1':
                        x0 = deep_seed(rng, caps[kk], kind='d1')
                    if x0 is None:
                        kk -= 1
                if x0 is None:
                    nseedfail['deep'] += 1
                    continue
                k0 = max(kk, 0)
                sd = float(x0[3 * N])
            else:
                K.pool(rng, n=900, log=None)
                x0 = None
                for _ in range(25):
                    x0 = K.build_seed(rng)
                    if x0 is not None:
                        break
                if x0 is None:
                    nseedfail['census'] += 1
                    continue
                xc, sd = compress(x0, low_target, rounds=130)
                if sd > caps[0] + 1e-9:
                    nseedfail['census'] += 1
                    continue
                x0 = to_container(xc)
                sd = float(x0[3 * N])
                k0 = max([k for k in range(len(caps)) if caps[k] >= sd - 1e-12]
                         or [0])
            log('  seed %3d %-6s start cap %.4f (s = %.6f, D = %.5f)'
                % (i, fam, caps[k0], sd, score(x0, mode)))
            rows = ladder(x0, mode, caps[k0:], log=log)
            nrun[fam] += 1
            for r in rows:
                reached[r['cap']] += 1
                bycap[r['cap']].append(r)
            fh.write(json.dumps({'tag': 'sd%04d' % i, 'family': fam,
                                 'mode': mode, 'sigma_seed': sd,
                                 'D_seed': score(x0, mode),
                                 'rows': [{k: v for k, v in r.items() if k != 'x'}
                                          for r in rows]}) + '\n')
            fh.flush()
            if (i + 1) % 10 == 0:
                bb = {('%.3f' % c): (round(max((r['score'] for r in bycap[c]),
                                               default=float('nan')), 5),
                                     len(bycap[c])) for c in caps}
                log('[%5.0fs] seed %3d/%d  best/n per cap: %s'
                    % (time.time() - t0, i + 1, nseeds, bb))
    log('%s seeds run, %s seed failures, %.0f s'
        % (nrun, nseedfail, time.time() - t0))
    nrun = sum(nrun.values())
    nseedfail = sum(nseedfail.values())

    # ---------------- exact certificates for the top candidates per cap
    res = {'mode': mode, 'caps': list(caps), 'n_seeds_run': nrun,
           'n_seed_fail': nseedfail, 'seed': seed,
           'n_reached_per_cap': {('%.6f' % c): reached[c] for c in caps},
           'secs_search': time.time() - t0, 'per_cap': {}}
    for c in caps:
        rows = sorted(bycap[c], key=lambda r: -r['score'])
        entry = {'cap': c, 'n': len(rows),
                 'best_float': rows[0]['score'] if rows else None,
                 'best_side_float': rows[0]['side'] if rows else None,
                 'candidates': []}
        for r in rows[:ncert]:
            x = np.array(r['x'], float)
            try:
                cert = certify(x)
            except Exception as ex:                       # noqa: BLE001
                cert = {'VERIFIED': False, 'error': repr(ex)[:200]}
            cert['float_score'] = r['score']
            cert['float_side'] = r['side']
            cert['float_d1'] = r['d1']
            cert['float_d2'] = r['d2']
            entry['candidates'].append(cert)
            log('  cap %.3f  D_float %.6f -> certified D in [%s, %s], side <= %s,'
                ' n_block %s, VERIFIED %s'
                % (c, r['score'], cert.get('D_min_d1_lo'), cert.get('D_min_d1_hi'),
                   cert.get('sigma_certified_upper'),
                   cert.get('n_block_certified'), cert.get('VERIFIED')))
        good = [q for q in entry['candidates'] if q.get('VERIFIED')]
        if good:
            b = max(good, key=lambda q: (q['D_min_d1_lo'] if mode == 'd1'
                                         else (q['D2_min_d2_lo'] or -9.0)))
            entry['best_certified'] = b
        res['per_cap']['%.6f' % c] = entry
    res['secs_total'] = time.time() - t0
    path = out_json or (OUT_JS if mode == 'd1' else OUT_D2)
    json.dump(res, open(path, 'w'), indent=1, default=str)
    log('wrote %s (%.0f s)' % (path, res['secs_total']))
    return res


# ==================================== the LOW-sigma arm: A87's own corpus
# Both search arms hit a side barrier at sigma ~ 4.000 (k0dir87's own 520-seed
# campaign has the same barrier: its record K0-BLOCKED side is 3.9855).  The only
# material below 4.000 that is certified K0-BLOCKED is therefore A87's existing
# corpus, so the depth ascent is run FROM those five packings, in place.

def lift_floor(x, target=EPS_KEEP, rounds=44):
    """Raise the SECOND intruders of a corpus point (min_c d2 down to 8e-9) up to
    the standard EPS_KEEP floor, so the d1 run starts inside the same feasible
    region as the rest of the campaign."""
    global EPS_KEEP
    nb, m1, m2, blk = k0_container(x)
    if not blk:
        return None
    EPS_KEEP = K.EPS_KEEP = max(1e-11, 0.4 * float(m2.min()))
    cap = float(x[3 * N])
    for _ in range(4):
        xa, sa, _ns = ascend(x, cap, 'd2', rounds=rounds)
        if xa is None:
            break
        x = xa
        nb, m1, m2, blk = k0_container(x)
        if float(m2.min()) >= target / 0.4:
            break
        EPS_KEEP = K.EPS_KEEP = max(1e-11, 0.4 * float(m2.min()))
    EPS_KEEP = K.EPS_KEEP = target
    return x if ok_point(x) else None


def corpus_arm(log=print, caps=(3.95, 3.90), ncert=1):
    global EPS_KEEP
    items = [it for it in DD.corpus() if it['kind'] == 'K0_BLOCKED']
    res = []
    for it in items:
        x = to_container(K.z_to_x([float(v) for v in it['z']]))
        nb, m1, m2, blk = k0_container(x)
        log('%s: corpus sigma %.9f  container n_block %s  min m2 %.3e  min m1 %.6f'
            % (it['tag'], it['sigma'], nb.tolist(), float(m2.min()),
               float(m1.min())))
        y = lift_floor(x)
        if y is None:
            log('   -> could not be lifted to the EPS_KEEP = 1e-4 floor; skipped')
            res.append({'tag': it['tag'], 'sigma_corpus': it['sigma'],
                        'status': 'lift_failed'})
            continue
        cap = float(y[3 * N])
        log('   lifted: s = %.9f  min_c d1 = %.6f  min_c d2 = %.3e'
            % (cap, score(y, 'd1'), score(y, 'd2')))
        rows = ladder(y, 'd1', (cap,) + tuple(c for c in caps if c < cap))
        rec = {'tag': it['tag'], 'sigma_corpus': it['sigma'],
               'rows': [{k: v for k, v in r.items() if k != 'x'} for r in rows]}
        for r in rows:
            log('   cap %.6f  D %.6f  side %.6f  n_block %s'
                % (r['cap'], r['score'], r['side'], r['n_block']))
        if rows:
            b = max(rows, key=lambda r: r['score'])
            try:
                c = certify(np.array(b['x'], float))
            except Exception as ex:                            # noqa: BLE001
                c = {'VERIFIED': False, 'error': repr(ex)[:200]}
            c['float_score'] = b['score']
            rec['best_certified'] = c
            log('   CERT: D in [%s, %s], sigma <= %s, n_block %s, VERIFIED %s'
                % (c.get('D_min_d1_lo'), c.get('D_min_d1_hi'),
                   c.get('sigma_certified_upper'), c.get('n_block_certified'),
                   c.get('VERIFIED')))
        res.append(rec)
    json.dump({'items': res},
              open(os.path.join(RESULTS, 'deepfront87.corpus.json'), 'w'),
              indent=1, default=str)
    return res


# ======================================= sensitivity of D* to the depth FLOOR
# The K0 rows pin the SECOND intruder at SAT depth >= EPS_KEEP.  The corner
# gadget shows d2 <= eps^2 / 4 when d1 = 1 - eps, so a floor of EPS_KEEP caps
# d1 at 1 - 2 sqrt(EPS_KEEP): 0.98 at 1e-4, 0.998 at 1e-6, 0.9998 at 1e-8.  If the
# search is really sitting on that cap rather than on a geometric obstruction,
# lowering the floor must move D by exactly that much.

def floors(log=print, cap=4.10, floors_=(1e-3, 1e-4, 1e-6, 1e-8), nseed=3):
    global EPS_KEEP
    rng = random.Random(777)
    out = []
    for fl in floors_:
        EPS_KEEP = fl
        K.EPS_KEEP = fl
        best = (-9.0, None)
        for _i in range(nseed):
            # the gadget realises d2 = 0.45 * eps^2/4, so eps >= 3.2 sqrt(f) keeps
            # the seed itself above the floor it is being tested against
            x0 = deep_seed(rng, cap, eps=max(0.03, 3.2 * math.sqrt(fl)))
            if x0 is None:
                x0 = deep_seed(rng, cap)
            if x0 is None:
                continue
            xa, sa, _ns = ascend(x0, cap, 'd1', rounds=55)
            if xa is not None and sa > best[0]:
                best = (sa, xa)
        pred = 1.0 - 2.0 * math.sqrt(fl)
        log('  EPS_KEEP %.0e: best D = %.9f   (gadget prediction 1-2 sqrt(eps)'
            ' = %.9f)' % (fl, best[0], pred))
        out.append({'eps_keep': fl, 'D': best[0], 'prediction': pred,
                    'side': float(K.enclosing_side_x(best[1]))
                    if best[1] is not None else None})
    EPS_KEEP = 1e-4
    K.EPS_KEEP = 1e-4
    json.dump({'cap': cap, 'rows': out},
              open(os.path.join(RESULTS, 'deepfront87.floors.json'), 'w'), indent=1)
    return out


# ====================================================================== report

def _fmt(v, nd=6):
    return '--' if v is None else ('%.*f' % (nd, v))


def frontier_rows(res):
    rows = []
    for c in sorted([float(k) for k in res['per_cap']]):
        e = res['per_cap']['%.6f' % c]
        b = e.get('best_certified')
        rows.append({'cap': c, 'n': e['n'], 'best_float': e['best_float'],
                     'side_float': e.get('best_side_float'),
                     'D_lo': b['D_min_d1_lo'] if b else None,
                     'D_hi': b['D_min_d1_hi'] if b else None,
                     'D2_lo': b['D2_min_d2_lo'] if b else None,
                     'D2_hi': b['D2_min_d2_hi'] if b else None,
                     'sigma': b['sigma_certified_upper'] if b else None,
                     'gap': b['min_pair_gap_lower'] if b else None,
                     'nb': b['n_block_certified'] if b else None,
                     'width': b['depth_width_max'] if b else None,
                     'cert': b})
    return rows


def report(log=print, path=None, mode='d1'):
    res = json.load(open(path or OUT_JS))
    rows = frontier_rows(res)
    L = []
    L.append('# A87 chore: the deep-corner frontier D*(sigma)\n')
    L.append('`D = min_c d1(c)`, depth = 1 - f_min_max in the corner frame '
             '(A89 t2b_depth / depthdist87); K0-BLOCKED = every corner slot met by '
             '>= 2 squares.  Objective: maximise D at a grid of side CAPS.\n')
    L.append('## Frontier (exact-verified)\n')
    key = 'D' if mode == 'd1' else 'D2'
    L.append('| cap sigma | n ladder pts | best %s (float) | certified %s enclosure |'
             ' certified sigma <= | min pair gap >= | n_block |' % (key, key))
    L.append('| ---: | ---: | ---: | :--- | ---: | ---: | :--- |')
    for r in rows:
        lo = r['D_lo'] if mode == 'd1' else r['D2_lo']
        hi = r['D_hi'] if mode == 'd1' else r['D2_hi']
        L.append('| %.6f | %d | %s | %s | %s | %s | %s |'
                 % (r['cap'], r['n'], _fmt(r['best_float']),
                    ('[%s, %s]' % (_fmt(lo, 9), _fmt(hi, 9)))
                    if lo is not None else '--',
                    _fmt(r['sigma'], 9), ('%.2e' % r['gap']) if r['gap'] else '--',
                    r['nb'] or '--'))
    L.append('')
    L.append('## Per-corner detail of the certified optimum\n')
    L.append('| cap | corner | n_block | d1 | tilt of d1 (deg) | d2 | sq(d1) |')
    L.append('| ---: | --- | ---: | ---: | ---: | ---: | ---: |')
    for r in rows:
        if not r['cert']:
            continue
        for cn in CORNERS:
            p = r['cert']['per_corner'][cn]
            L.append('| %.6f | %s | %d | %s | %s | %s | %s |'
                     % (r['cap'], cn, p['n_block_certified'],
                        _fmt(p.get('d1')), _fmt(p.get('d1_tilt_deg'), 4),
                        _fmt(p.get('d2'), 9), p.get('d1_sq')))
    L.append('')

    # ---------------- thresholds
    L.append('## Does D* drop below 0.3 / 0.5 / 0.7 ?\n')
    L.append('| cap sigma | certified sigma | certified %s | >= 0.3 | >= 0.5 | >= 0.7 |'
             % key)
    L.append('| ---: | ---: | ---: | :---: | :---: | :---: |')
    for r in rows:
        lo = r['D_lo'] if mode == 'd1' else r['D2_lo']
        if lo is None:
            L.append('| %.6f | -- | NO PACKING FOUND | -- | -- | -- |' % r['cap'])
            continue
        L.append('| %.6f | %s | %s | %s | %s | %s |'
                 % (r['cap'], _fmt(r['sigma'], 6), _fmt(lo, 9),
                    'YES' if lo >= 0.3 else 'no',
                    'YES' if lo >= 0.5 else 'no',
                    'YES' if lo >= 0.7 else 'no'))
    L.append('')

    # ---------------- analytic anchors
    L.append('## Analytic anchors the numbers should be read against\n')
    L.append('**The d1 gadget trade-off.**  With the deepest intruder an'
             ' axis-aligned square whose inner edge sits at x = eps (so'
             ' `d1 = 1 - eps`), the only part of the slot left free is the strip'
             ' `(0, eps) x (0, 1)`, which no square can reach from below.  The'
             ' second intruder must therefore WRAP the reflex corner `(eps, 1)`:'
             ' its inner edge runs along a line through `(eps, 1)` of slope'
             ' `tan phi`, and the container wall `x >= 0` forces its inner vertex'
             ' to `x >= sin phi`.  Hence')
    L.append('')
    L.append('```')
    L.append('    d2  <=  max_phi (eps - sin phi) tan phi  ~  eps^2 / 4 ,')
    L.append('    i.e.   d1  <=  1 - 2 sqrt(d2)   (to 5 digits for d2 <= 1e-3).')
    L.append('```')
    L.append('')
    L.append('So a floor `d2 >= f` caps `min_c d1` at `1 - 2 sqrt f`:')
    L.append('')
    L.append('| d2 floor f | eps* | d1 ceiling | 1 - 2 sqrt f |')
    L.append('| ---: | ---: | ---: | ---: |')
    for f, es, cl in ((1e-3, 0.06322974, 0.93677026), (1e-4, 0.01999950, 0.98000050),
                      (1e-6, 0.00200000, 0.99800000), (1e-8, 0.00020000, 0.99980000)):
        L.append('| %.0e | %.8f | %.8f | %.8f |'
                 % (f, es, cl, 1 - 2 * math.sqrt(f)))
    L.append('')
    L.append('**The d2 (both-deep) ceiling.**  If the two intruders of a corner are'
             ' separated by a line through the corner point, each is confined to a'
             ' sub-wedge of the corner quadrant.  In the wedge `{0 <= y <= x}` one'
             ' has `max(x,y) = x`, so `f_min_max = cx - e` with'
             ' `e = (|cos|+|sin|)/2`, while the wedge rows'
             ' `min(x-y) >= 0` and `min y >= 0` read'
             ' `cx - cy >= max(cos th, sin th)` and `cy >= e`.  Therefore')
    L.append('')
    L.append('```')
    L.append('    min(d1, d2)  <=  1 - 1/sqrt(2)  =  0.29289321881345254 ,')
    L.append('```')
    L.append('')
    L.append('attained at tilt 45 deg by the pair of 45-degree squares that share'
             ' a whole edge on the corner diagonal and each touch one wall.  A'
             ' separating line that misses the corner point only pushes the far'
             ' square further out, so this is the two-intruder optimum AT ONE'
             ' CORNER; the four-corner packing constraint can only lower it.')
    L.append('')
    open(OUT_MD if mode == 'd1' else OUT_MD.replace('.md', '.d2.md'),
         'w').write('\n'.join(L) + '\n')
    for ln in L:
        log(ln)
    return rows


def _j(name):
    p = os.path.join(RESULTS, name)
    return json.load(open(p)) if os.path.exists(p) else None


def write_notes(log=print):
    """Assemble notes/deepfront87.md from every result file that exists."""
    d1 = _j('deepfront87.json')
    d2 = _j('deepfront87.d2.json')
    cp = _j('deepfront87.corpus.json')
    fl = _j('deepfront87.floors.json')
    A = []

    def P(s=''):
        A.append(s)

    r1 = frontier_rows(d1) if d1 else []
    r2 = frontier_rows(d2) if d2 else []
    live = [r for r in r1 if r['D_lo'] is not None]
    P('# A87 chore: the deep-corner frontier D*(sigma)')
    P()
    P('`D = min_c d1(c)`; `d1(c)` / `d2(c)` = depth of the deepest / second'
      ' deepest intruder at corner c; depth = `1 - f_min_max` in the corner frame'
      ' (A89 `t2b_depth`, as in `depthdist87`).  K0-BLOCKED = every corner\'s open'
      ' unit slot met by >= 2 squares (hence no simple square).  Code'
      ' `code/deepfront87.py`; the search MAXIMISES D at a grid of side caps and'
      ' every reported number is an exact-verified enclosure.')
    P()
    if live:
        b = max(live, key=lambda r: r['D_lo'])
        P('## Headline')
        P()
        P('**The PI conjecture is FALSE as stated for sigma around 4.**  A'
          ' certified K0-BLOCKED packing exists with')
        P()
        P('```')
        P('    sigma <= %.9f      min_c d1 = %.9f      n_block = %s'
          % (b['sigma'], b['D_lo'], b['nb']))
        P('```')
        P()
        P('i.e. ALL FOUR corners have their deepest intruder past 0.97, versus'
          ' `min_c d1 <= 0.0998` over the whole existing A87 corpus -- a factor'
          ' of ~10.  D* does not decline anywhere in the probed range: it is'
          ' FLAT at 0.9783-0.9800 from sigma = 4.344 down to sigma = %.4f, and it'
          ' is pinned there not by sigma but by the search\'s own artificial'
          ' second-intruder floor EPS_KEEP = 1e-4 (see the analytic ceiling'
          ' below: every certified optimum has d2 = 1.000e-4 exactly and'
          ' d1 <= 0.9800004 = 1 - 2 sqrt(1e-4)).'
          % min(r['sigma'] for r in live))
        P()
        P('**But the search never got below sigma ~ 4.000**, so it says NOTHING'
          ' about the regime the conjecture is about (sigma <= s_hat ='
          ' 3.877083590022814).  See "What this does and does not settle".')
        P()

    P('## Frontier (exact-verified), objective min_c d1')
    P()
    P('| cap sigma | n ladder pts | best D (float) | certified D enclosure |'
      ' certified sigma <= | min pair gap >= | n_block | depth iv width <= |')
    P('| ---: | ---: | ---: | :--- | ---: | ---: | :--- | ---: |')
    for r in r1:
        if r['D_lo'] is None:
            P('| %.6f | %d | %s | NO K0-BLOCKED PACKING REACHED | -- | -- | -- | -- |'
              % (r['cap'], r['n'], _fmt(r['best_float'])))
            continue
        P('| %.6f | %d | %s | [%s, %s] | %.9f | %.2e | %s | %.1e |'
          % (r['cap'], r['n'], _fmt(r['best_float']),
             _fmt(r['D_lo'], 9), _fmt(r['D_hi'], 9), r['sigma'], r['gap'],
             r['nb'], r['width']))
    P()
    if cp:
        P('The `3.950 / 3.900 / 3.877` rows are EMPTY because no K0-BLOCKED'
          ' packing at those sides could be produced at all -- not because D* is'
          ' small there.  Both search arms stall at sigma ~ 4.000, exactly the'
          ' barrier k0dir87\'s own 520-seed campaign hit (its record K0-BLOCKED'
          ' side is 3.9855).  The corpus arm below does not break the barrier'
          ' either: the one corpus packing that IS under 4.000 (s0115,'
          ' sigma = 3.9855) could not be lifted off its 5.3e-9 second-intruder'
          ' floor, so even it yields no usable start.')
        P()

    P('## Per-corner detail of the certified optimum')
    P()
    P('| cap | corner | n_block | d1 | tilt of d1 (deg) | d2 | sq(d1) |')
    P('| ---: | --- | ---: | ---: | ---: | ---: | ---: |')
    for r in r1:
        if not r['cert']:
            continue
        for cn in CORNERS:
            p = r['cert']['per_corner'][cn]
            P('| %.6f | %s | %d | %.9f | %.6f | %.4e | %s |'
              % (r['cap'], cn, p['n_block_certified'], p['d1'],
                 p['d1_tilt_deg'], p.get('d2', float('nan')), p['d1_sq']))
    P()
    P('Every deepest intruder is essentially AXIS-ALIGNED (tilt 1e-6 to 3e-3'
      ' degrees): the deep-corner motif is a slot square pushed off the corner by'
      ' eps, not a tilted crowder.  This matches `depthdist87`\'s observation that'
      ' tilt does not buy depth (the two corpus corners with tilt > 15 deg have'
      ' depth 0.0997 and 0.2267).')
    P()

    P('## Does D* drop below 0.3 / 0.5 / 0.7 as sigma decreases?')
    P()
    P('| cap sigma | certified sigma | certified D | >= 0.3 | >= 0.5 | >= 0.7 |')
    P('| ---: | ---: | ---: | :---: | :---: | :---: |')
    for r in r1:
        if r['D_lo'] is None:
            P('| %.6f | -- | *unprobed* | -- | -- | -- |' % r['cap'])
            continue
        P('| %.6f | %.6f | %.9f | %s | %s | %s |'
          % (r['cap'], r['sigma'], r['D_lo'],
             'YES' if r['D_lo'] >= 0.3 else 'no',
             'YES' if r['D_lo'] >= 0.5 else 'no',
             'YES' if r['D_lo'] >= 0.7 else 'no'))
    P()
    P('**No.**  Over every side the search actually reached, D* clears all three'
      ' thresholds with room to spare, and there is no downward trend to'
      ' extrapolate from: the curve is flat.')
    P()
    P('**EXTRAPOLATED (and NOT to be trusted).**  A naive continuation of a flat'
      ' curve would put D*(s_hat) ~ 0.98 as well, i.e. the conjecture false.'
      ' That extrapolation is worthless here, for a reason visible inside A87'
      ' itself: the probed range is entirely ABOVE the packing barrier.  As sigma'
      ' falls to s(11) the set of 11-square packings collapses to a neighbourhood'
      ' of the optimum, and the four deep-corner motifs (footprint ~1.02 x 2.0'
      ' each) provably stop fitting -- at sigma = 4.00 the four gadget footprints'
      ' plus three more squares already do not fit (the seeder fails outright'
      ' below 4.05 and only a compressed census packing reaches 4.01).  Against'
      ' the flat extrapolation stands a SOUND bound in the opposite direction at'
      ' exactly the side that matters: `depthdist87`\'s A85 4-corner gate analysis'
      ' (boxes from the sigma-CLOSED cover, i.e. the s_hat scale) finds that'
      ' 0 of 30 attemptable stored 4-corner nodes can host `min_c d1 >= 0.7`, and'
      ' 0 of 30 can host `min_c d2 >= 0.3`.  Since that is an UPPER bound per box,'
      ' it EXCLUDES `min_c d1 >= 0.7` on those nodes.')
    P()
    P('So the honest picture is a CLIFF somewhere in `(s_hat, 4.01)` that this'
      ' search does not resolve:')
    P()
    P('```')
    P('    sigma in [4.01, 4.40] :  D* ~ 0.98        (certified >= 0.9755 here)')
    P('    sigma  =  s_hat       :  D* < 0.7         (A85 box bound, sampled)')
    P('```')
    P()
    P('The load-bearing consequence for the drain-flow argument: **K0-BLOCKED'
      ' alone does not force a shallow corner.**  Any proof of the PI statement'
      ' must use the side bound sigma <= s_hat essentially, not merely as a'
      ' background assumption -- at sigma = 4.01 the same combinatorics admit'
      ' min_c d1 = 0.977.')
    P()

    if r2:
        P('## Second objective: min_c d2 (BOTH intruders deep)')
        P()
        P('| cap sigma | n | best min_c d2 (float) | certified enclosure |'
          ' certified sigma <= | n_block |')
        P('| ---: | ---: | ---: | :--- | ---: | :--- |')
        for r in r2:
            if r['D2_lo'] is None:
                P('| %.6f | %d | %s | NOT VERIFIED / NOT REACHED | -- | -- |'
                  % (r['cap'], r['n'], _fmt(r['best_float'])))
                continue
            P('| %.6f | %d | %s | [%s, %s] | %.9f | %s |'
              % (r['cap'], r['n'], _fmt(r['best_float']), _fmt(r['D2_lo'], 9),
                 _fmt(r['D2_hi'], 9), r['sigma'], r['nb']))
        P()
        P('Read against the one-corner ceiling `1 - 1/sqrt 2 ='
          ' 0.29289321881345254` derived below.  Two things happen:')
        P()
        P('* At the two largest caps the search SATURATES that ceiling: certified'
          ' `min_c d2 = 0.292893154942` at sigma <= 4.598976 (6.39e-8 under the'
          ' ceiling) and `0.292892810151` at sigma <= 4.380962 (4.09e-7 under it),'
          ' with the tilt of every deep intruder certified at 45.000000 degrees.'
          ' That is the predicted motif, found independently by the optimiser, and'
          ' it is a sharp check on both the code and the bound.  (Individual `d1`'
          ' values sit a few 1e-7 ABOVE 1 - 1/sqrt 2 -- consistent, since the'
          ' bound constrains `min(d1, d2)`, not `d1` alone.)')
        P('* Unlike the d1 frontier, the d2 frontier genuinely DECLINES: it falls'
          ' from 0.2928932 at sigma <= 4.381 to **0.125016** at sigma <= 4.200, a'
          ' factor of 2.3 over a side interval of 0.18.  The cause is packing, not'
          ' corner geometry: the four-corner 45-degree 2-crowd gadget needs'
          ' sigma >= 4.60 to admit three further squares at all (at 4.40 the eight'
          ' corner squares fit but the three middles do not), so below ~4.4 the'
          ' four motifs must start giving way to each other.  Cap 4.00 was never'
          ' reached, by the same sigma ~ 4.000 barrier as the d1 run.')
        P()
        P('So for the SECOND intruder there IS a visible cliff inside the probed'
          ' range, and it is already at 0.125 by sigma = 4.2 -- below the 0.3'
          ' threshold.  `depthdist87`\'s A85 gate analysis says 0 of 30 attemptable'
          ' 4-corner nodes can host `min_c d2 >= 0.3` at the s_hat scale, which is'
          ' the same story continued downwards.')
        P()

    if cp:
        P('## Low-sigma arm: the depth ascent run IN PLACE on A87\'s own corpus')
        P()
        P('The five exact K0-BLOCKED packings of `depthdist87` are the only'
          ' certified material below sigma = 4.000.  Their second intruders sit at'
          ' or under the old EPS_KEEP floor (min_c d2 down to 8e-9), so each is'
          ' first LIFTED to the standard 1e-4 floor by a d2 ascent, then the d1'
          ' ascent is run at its own side.')
        P()
        P('The outcome is NEGATIVE and worth recording as such: the ascent barely'
          ' moves from a corpus point.  Two of the five cannot even be lifted to'
          ' the 1e-4 floor (their second intruders are at 5.3e-9 and 4.6e-7 and the'
          ' d2 ascent cannot raise them), and the three that can end at'
          ' `min_c d1` = 0.0112, 0.00047 and 0.0574 -- essentially where they'
          ' started.  This is the behaviour k0dir87 already documented for these'
          ' points: they are BOUNDARY points of the constrained problem, and a'
          ' local ascent is trapped.  So this arm gives NO evidence that D* is'
          ' small at sigma ~ 4.000004 -- the census arm reaches D = 0.9796 at'
          ' sigma <= 4.0291, only 0.029 higher.  It is a statement about the'
          ' basin, not about the frontier.')
        P()
        P('| tag | corpus sigma | status | best cap | D (float) | certified D |'
          ' certified sigma <= | n_block |')
        P('| --- | ---: | --- | ---: | ---: | :--- | ---: | :--- |')
        for it in cp['items']:
            if it.get('status') == 'lift_failed':
                P('| %s | %.9f | lift to the 1e-4 floor FAILED | -- | -- | -- |'
                  ' -- | -- |' % (it['tag'], it['sigma_corpus']))
                continue
            rows = it.get('rows') or []
            c = it.get('best_certified') or {}
            if not rows:
                P('| %s | %.9f | no ascent step | -- | -- | -- | -- | -- |'
                  % (it['tag'], it['sigma_corpus']))
                continue
            bb = max(rows, key=lambda r: r['score'])
            P('| %s | %.9f | ok | %.6f | %.6f | %s | %s | %s |'
              % (it['tag'], it['sigma_corpus'], bb['cap'], bb['score'],
                 ('[%s, %s]' % (_fmt(c.get('D_min_d1_lo'), 9),
                                _fmt(c.get('D_min_d1_hi'), 9)))
                 if c.get('D_min_d1_lo') is not None else 'NOT VERIFIED',
                 _fmt(c.get('sigma_certified_upper'), 9),
                 c.get('n_block_certified')))
        P()

    if fl:
        P('## Sensitivity: D* is pinned by the second-intruder floor, not by sigma')
        P()
        P('| EPS_KEEP | best D found | gadget prediction 1 - 2 sqrt(eps) |')
        P('| ---: | ---: | ---: |')
        for r in fl['rows']:
            P('| %.0e | %.9f | %.9f |'
              % (r['eps_keep'], r['D'], r['prediction']))
        P()
        P('D rises monotonically as the floor is lowered and tracks'
          ' `1 - 2 sqrt(EPS_KEEP)` (it lags at 1e-6 / 1e-8 only because the ascent'
          ' was given 55 rounds, not because anything else binds).  That is the'
          ' signature of a configuration sitting ON the floor rather than against a'
          ' geometric obstruction: with only the TOPOLOGICAL requirement'
          ' `d2 > 0` -- any sliver counts as a blocker, which is what K0-BLOCKED'
          ' actually asks -- D* -> 1 at these sides.  **The 0.98 in the frontier'
          ' table is therefore an artefact of the search\'s own floor, and the'
          ' honest reading of D*(sigma) for sigma in [4.03, 4.40] is "1, up to the'
          ' sliver tolerance you insist on".**')
        P()

    P('## Analytic anchors')
    P()
    P('**The d1 gadget trade-off (why 0.98 and not 1).**  Take the deepest'
      ' intruder to be an axis-aligned square whose inner edge sits at `x = eps`,'
      ' so `f_min_max = eps` and `d1 = 1 - eps`.  The only part of the slot it'
      ' leaves free is the strip `(0, eps) x (0, 1)`, and nothing can reach that'
      ' strip from below (`y < 0` is outside the container).  So the second'
      ' intruder must WRAP the reflex corner `(eps, 1)`: it is separated from the'
      ' first by a line through `(eps, 1)` of slope `tan phi`, its inner edge runs'
      ' along that line, and the container wall `x >= 0` forces its inner vertex'
      ' to `x >= sin phi`.  Its depth is the drop of that line over'
      ' `[sin phi, eps]`:')
    P()
    P('```')
    P('    d2  <=  max_phi (eps - sin phi) tan phi   ~   eps^2 / 4 ,')
    P('    equivalently   d1  <=  1 - 2 sqrt(d2)   (to 5 digits for d2 <= 1e-3).')
    P('```')
    P()
    P('A floor `d2 >= f` therefore caps `min_c d1` at `1 - 2 sqrt f`:')
    P()
    P('| d2 floor f | eps* | d1 ceiling | 1 - 2 sqrt f |')
    P('| ---: | ---: | ---: | ---: |')
    for f, es, cl in ((1e-3, 0.06322974, 0.93677026),
                      (1e-4, 0.01999950, 0.98000050),
                      (1e-6, 0.00200000, 0.99800000),
                      (1e-8, 0.00020000, 0.99980000)):
        P('| %.0e | %.8f | %.8f | %.8f |' % (f, es, cl, 1 - 2 * math.sqrt(f)))
    P()
    P('The certified optima above land on this line exactly: `d2 = 1.000e-4` at'
      ' every corner and `d1` up to `0.9800004`.')
    P()
    P('**The one-corner d2 ceiling.**  If the two intruders of a corner are'
      ' separated by a line through the corner point, each is confined to a'
      ' sub-wedge of the corner quadrant.  In the wedge `{0 <= y <= x}` one has'
      ' `max(x,y) = x`, so `f_min_max = c_x - e` with `e = (|cos|+|sin|)/2`, while'
      ' the two wedge rows `min(x - y) >= 0` and `min y >= 0` read'
      ' `c_x - c_y >= max(cos th, sin th)` and `c_y >= e`.  Adding them,'
      ' `f_min_max >= max(cos th, sin th) >= 1/sqrt 2`, so')
    P()
    P('```')
    P('    min(d1, d2)  <=  1 - 1/sqrt(2)  =  0.29289321881345254 ,')
    P('```')
    P()
    P('attained at tilt 45 deg by the two 45-degree squares that share a whole'
      ' edge on the corner diagonal and each touch one wall.  **Scope of this'
      ' bound:** the derivation above is complete only when the separating line'
      ' passes THROUGH the corner point.  For a line that misses it, the argument'
      ' offered here is only that shifting the line off the corner enlarges one'
      ' sub-wedge past 45 deg while shrinking the other below it, so the MINIMUM of'
      ' the two depths falls -- checked for lines near the diagonal, not proved in'
      ' general.  It is therefore a conjectured one-corner optimum, and the'
      ' certified numbers above are consistent with it (they approach it from'
      ' below, by 6.4e-8, and never cross it).  (Trump\'s genuine TL 2-crowd sits at tilt'
      ' 40.18 deg with d1 = 0.1683, d2 = 0.1555 -- the motif, well short of the'
      ' one-corner ceiling because the rest of the packing is in the way.)')
    P()

    P('## Canary')
    P()
    P('With the K0-BLOCKED constraint DROPPED and simple squares allowed, the'
      ' optimum is four flush slot squares and D = 1.  The same `ascend` code,'
      ' from the same gadget seeds, returns')
    P()
    P('```')
    P('    cap 4.05 :  D = 1.000000000 exactly,  per-corner d1 = [1, 1, 1, 1],')
    P('                n_block = [1, 1, 1, 1]  (four SIMPLE squares),  s = 4.03523')
    P('```')
    P()
    P('At sigma = 4.00 exactly D = 1 is only an INFIMUM, not attained: four'
      ' corner slot squares plus seven more fill the 16-cell unit grid of'
      ' `[0,4]^2` with zero slack, so a STRICTLY feasible D = 1 packing needs'
      ' sigma > 4 -- the smallest side at which the search realises it is'
      ' 4.0352.  The canary passes at cap 4.05.')
    P()

    P('## What this does and does not settle')
    P()
    P('* **Settled (certified).**  K0-BLOCKED does NOT by itself force a shallow'
      ' corner.  At sigma <= %s there is a K0-BLOCKED packing with all four'
      ' `d1 > 0.97`.  The PI statement, read as a claim about K0-BLOCKED packings'
      ' at ANY side near 4, is false.'
      % (('%.6f' % min(r['sigma'] for r in live)) if live else '4.01'))
    P('* **Settled (analytic).**  The deep-corner motif costs quadratically:'
      ' `d1 = 1 - eps` forces `d2 <~ eps^2/4`.  So "both intruders deep" is a'
      ' completely different question from "one intruder deep", and the'
      ' one-corner ceiling for the former is `1 - 1/sqrt 2 = 0.2929`.')
    P('* **NOT settled.**  Everything at `sigma <= s_hat`, which is the only'
      ' regime the conjecture is about.  No K0-BLOCKED packing below'
      ' sigma ~ 4.000 was produced by this search (k0dir87 has the same barrier;'
      ' its record is 3.9855).  The grid points 3.95, 3.90 and s_hat are EMPTY.')
    P('* **Cheapest next step.**  The gap to close is `(s_hat, 4.01)`, and the'
      ' obstruction is a PACKING barrier, not a depth one: what is missing is a'
      ' supply of K0-BLOCKED packings at sigma in [3.877, 4.00].  A85\'s'
      ' sigma-closed cover already enumerates the corner pairs at that side, so'
      ' the direct attack is to run this depth ascent inside the A85 4-corner'
      ' nodes rather than from free-space seeds.')
    P()
    P('## Provenance')
    P()
    if d1:
        P('* d1 campaign: %s seeds run, %s seed failures, %.0f s search +'
          ' certification, RNG seed %s; caps %s.'
          % (d1['n_seeds_run'], d1['n_seed_fail'], d1.get('secs_total', 0),
             d1['seed'], d1['caps']))
        P('* ladder points reached per cap: %s' % (d1['n_reached_per_cap'],))
    if d2:
        P('* d2 campaign: %s seeds run, caps %s.'
          % (d2['n_seeds_run'], d2['caps']))
    P('* Every certified row: rational z (denominators <= 1e15), interval SAT'
      ' gaps certified > 0, blocker counts certified against the INNER rational'
      ' slot rectangle (`k0dir87.exact_blocked_test`), depths as outward-rounded'
      ' interval enclosures (`depthdist87.corner_depths`), side an outward'
      ' interval UPPER bound (`fjpolish87.verify_exact`).')
    P('* Files: `results/deepfront87.{json,jsonl}`, `.d2.json`, `.corpus.json`,'
      ' `.floors.json`, `.pilot.json`; log `logs/deepfront87.run.log`.')
    P('* Selftest: depth_table vs the exact interval depth of `depthdist87` on'
      ' Trump, 44 rows, max |diff| 3.3e-16; analytic vs finite-difference'
      ' gradients, max rel err 3.2e-9; the smooth objective verified to be an'
      ' UPPER bound on `f_min_max` (0 violations); the 8-candidate set verified'
      ' complete against a 401-point-per-edge brute-force boundary scan.')
    P()
    open(OUT_MD, 'w').write('\n'.join(A) + '\n')
    log('wrote %s (%d lines)' % (OUT_MD, len(A)))
    return A


CMDS = {}


def main():
    args = sys.argv[1:] or ['selftest']
    for a in args:
        print('=== %s ===' % a, flush=True)
        t0 = time.time()
        if a == 'selftest':
            f = selftest()
            print('SELFTEST %s' % ('PASS' if not f else 'FAIL: %s' % f))
            if f:
                sys.exit(1)
        elif a == 'canary':
            ok, D, _x = canary()
            if not ok:
                sys.exit(1)
        elif a == 'pilot':
            campaign(nseeds=8, wall=700.0, ncert=1,
                     out_json=os.path.join(RESULTS, 'deepfront87.pilot.json'))
        elif a == 'run':
            campaign(mode='d1', nseeds=500,
                     wall=float(os.environ.get('DF_WALL', '4800')))
        elif a == 'd2':
            # 4.60 is a SEEDING cap only (the four-corner 45 deg 2-crowd gadget
            # does not admit 3 more squares below 4.60); the requested caps are
            # 4.40 and 4.00, reached by the ladder.
            campaign(mode='d2', caps=(4.60, 4.40, 4.20, 4.00), nseeds=500,
                     wall=float(os.environ.get('DF_WALL_D2', '1400')),
                     out_json=OUT_D2)
        elif a == 'floors':
            floors()
        elif a == 'corpus':
            corpus_arm()
        elif a == 'notes':
            write_notes()
        elif a == 'report':
            report()
        elif a == 'report_d2':
            report(path=OUT_D2, mode='d2')
        else:
            raise SystemExit('unknown command %s' % a)
        print('=== %s done in %.1f s ===' % (a, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
