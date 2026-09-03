"""k0dir87.py -- A87 chore: DIRECTED critical-point search seeded INSIDE K0-BLOCKED.

Question: does ANY Fritz-John point of the enclosing-side function live in
K0-BLOCKED (every one of the four closed unit corner slots met by >= 2 squares,
so no single-square removal + teleport turns the point into a k >= 1 point)?

The 167 certified k0 FJ points are all K0-FREE by teleport (notes/k0blocked87.md).
This module attacks the question from the other side: build packings that ARE
K0-BLOCKED by construction, push the side down, and see whether the descent can
reach a critical point without leaving the region.

Pipeline per seed
  (0) SEED.  For each of the 4 corners, two disjoint unit squares both meeting the
      OPEN unit corner slot, drawn from A85's BL pair census
      (A85/results/a85_pairs_BL.json, level-2 survivors) and carried to the other
      three corners by the D4 corner maps; the remaining 3 squares are rejection
      sampled in the middle.  s starts in [4.5, 5.5].  (An axis-aligned PAIR cannot
      both intrude -- the census only contains pairs with a tilted member.)
  (1) GUARDED FREE DESCENT.  cp85's penalty/L-BFGS descent on the side, run in
      short chunks; after each chunk the K0-BLOCKED test is re-run on the TIGHT
      bounding box.  On a violation the step is bisected to the exit point, the
      exit (corner, sigma, mode) is recorded and the seed stops.
  (2) CONSTRAINED DESCENT.  From the last K0-BLOCKED point, SLSQP on the side with
      the two deepest intruders per corner pinned to depth >= EPS_KEEP (fixed SAT
      branch, re-selected each outer round) plus the usual pair/container rows.
      If the K0 rows come out SLACK the local minimum is INTERIOR to K0-BLOCKED.
  (3) FJ POLISH.  Survivors go through the fjpolish87 ladder (tol 1e-6) and the
      polished point is re-tested with the EXACT interval teleport test of
      k0blocked87 (and exact-verified for feasibility).

Writes only  results/k0dir87.{jsonl,json}  and  notes/k0dir87.md.
Usage: python k0dir87.py {selftest|canary|run [N]|report|all}
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

import cp85                       # noqa: E402  (A85 float geometry, A04 lineage)
import fjpolish87 as F            # noqa: E402
import k0blocked87 as KB          # noqa: E402
import t3lib as T                 # noqa: E402

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
LOGS = os.path.join(A87, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

OUT_JL = os.path.join(RESULTS, 'k0dir87.jsonl')
OUT_JS = os.path.join(RESULTS, 'k0dir87.json')
OUT_MD = os.path.join(NOTES, 'k0dir87.md')
PAIRS = os.path.join(A85, 'results', 'a85_pairs_BL.json')

N = 11
H = 0.5
HALFPI = math.pi / 2.0
CORNERS = ('BL', 'BR', 'TL', 'TR')
# (sx, sy):  anchor = (xlo + sx*(W-1), ylo + sy*(Hh-1)) of the tight bbox
CSGN = {'BL': (0, 0), 'BR': (1, 0), 'TL': (0, 1), 'TR': (1, 1)}

EPS_KEEP = 1e-4          # depth floor imposed by the constrained phase
SLACK_TOL = 1e-6         # a K0 row counts as SLACK if depth > EPS_KEEP + this
# A square blocks a slot only if their INTERIORS genuinely meet, and by more than
# floating-point noise.  A tangency (gap 0, e.g. Trump's square 3 sitting on the
# top edge of the BL slot, which the float catalogue realises at -1.3e-15) is
# interior-disjoint and must NOT count.  The SAME floor is used by the exact
# interval test, where it is the sound direction: "certified depth > TOL_BLOCK"
# implies "interiors meet".
TOL_BLOCK = 1e-9
S_HAT = F.S_HAT
S0F = F.S0F


# ============================================================ float geometry

def sq_corners(c, th):
    ct, st = np.cos(th), np.sin(th)
    u = np.stack([ct, st], axis=1) * H
    v = np.stack([-st, ct], axis=1) * H
    sg = np.array([[1., 1.], [1., -1.], [-1., -1.], [-1., 1.]])
    return (c[:, None, :] + sg[None, :, 0, None] * u[:, None, :]
            + sg[None, :, 1, None] * v[:, None, :])


def tight_bbox(x):
    c, th, _ = cp85.unpack(x)
    q = sq_corners(c, th).reshape(-1, 2)
    return q[:, 0].min(), q[:, 0].max(), q[:, 1].min(), q[:, 1].max()


def enclosing_side_x(x):
    xlo, xhi, ylo, yhi = tight_bbox(x)
    return float(max(xhi - xlo, yhi - ylo))


# ------------------------------------------------------- slot / square SAT
# gap = max over the 8 (axis, branch) separations; gap >= 0 <=> interior-disjoint.
# The 8 rows are, per square i and slot anchor (ax, ay):
#   0: ax - (cx + e)                    1: (cx - e) - (ax + 1)
#   2: ay - (cy + e)                    3: (cy - e) - (ay + 1)
#   4: (q2 - e) - (p2 + 1/2)            5: (p2 - 1/2) - (q2 + e)      n = ( co, si)
#   6: (q3 - e) - (p3 + 1/2)            7: (p3 - 1/2) - (q3 + e)      n = (-si, co)
# with e = (|co| + |si|)/2 the common projection radius of BOTH the unit slot and
# the unit square onto the tilted axes (and of the square onto the axis ones).

def slot_rows(c, th, anchor, dsx=0.0, dsy=0.0):
    """Values and gradients (d/dcx, d/dcy, d/dth, d/ds) of the 8 SAT rows.

    anchor = (ax, ay) as floats; dsx, dsy = d ax/ds, d ay/ds."""
    n = len(th)
    cx, cy = c[:, 0], c[:, 1]
    ax, ay = anchor
    co, si = np.cos(th), np.sin(th)
    e = H * (np.abs(co) + np.abs(si))
    de = H * (-np.sign(co) * si + np.sign(si) * co)
    mx, my = ax + H, ay + H          # slot centre
    p2 = cx * co + cy * si
    dp2 = -cx * si + cy * co
    q2 = mx * co + my * si
    dq2 = -mx * si + my * co
    ds_q2 = dsx * co + dsy * si
    p3 = -cx * si + cy * co
    dp3 = -cx * co - cy * si
    q3 = -mx * si + my * co
    dq3 = -mx * co - my * si
    ds_q3 = -dsx * si + dsy * co

    V = np.empty((n, 8))
    G = np.zeros((n, 8, 4))
    one = np.ones(n)
    zero = np.zeros(n)
    # row 0
    V[:, 0] = ax - cx - e
    G[:, 0] = np.stack([-one, zero, -de, dsx * one], axis=1)
    # row 1
    V[:, 1] = cx - e - ax - 1.0
    G[:, 1] = np.stack([one, zero, -de, -dsx * one], axis=1)
    # row 2
    V[:, 2] = ay - cy - e
    G[:, 2] = np.stack([zero, -one, -de, dsy * one], axis=1)
    # row 3
    V[:, 3] = cy - e - ay - 1.0
    G[:, 3] = np.stack([zero, one, -de, -dsy * one], axis=1)
    # row 4 / 5  (axis (co, si))
    V[:, 4] = q2 - e - p2 - H
    G[:, 4] = np.stack([-co, -si, dq2 - de - dp2, ds_q2 * one], axis=1)
    V[:, 5] = p2 - H - q2 - e
    G[:, 5] = np.stack([co, si, dp2 - de - dq2, -ds_q2 * one], axis=1)
    # row 6 / 7  (axis (-si, co))
    V[:, 6] = q3 - e - p3 - H
    G[:, 6] = np.stack([si, -co, dq3 - de - dp3, ds_q3 * one], axis=1)
    V[:, 7] = p3 - H - q3 - e
    G[:, 7] = np.stack([-si, co, dp3 - de - dq3, -ds_q3 * one], axis=1)
    return V, G


def slot_gaps(x, use_bbox=True):
    """gaps[c, i] and the argmax row index arg[c, i]."""
    c, th, s = cp85.unpack(x)
    if use_bbox:
        xlo, xhi, ylo, yhi = tight_bbox(x)
        anch = {'BL': (xlo, ylo), 'BR': (xhi - 1.0, ylo),
                'TL': (xlo, yhi - 1.0), 'TR': (xhi - 1.0, yhi - 1.0)}
        dss = {k: (0.0, 0.0) for k in CORNERS}
    else:
        anch = {'BL': (0.0, 0.0), 'BR': (s - 1.0, 0.0),
                'TL': (0.0, s - 1.0), 'TR': (s - 1.0, s - 1.0)}
        dss = {k: (float(CSGN[k][0]), float(CSGN[k][1])) for k in CORNERS}
    gaps = np.empty((4, N))
    args = np.empty((4, N), dtype=int)
    grads = np.empty((4, N, 4))
    for ci, cn in enumerate(CORNERS):
        V, G = slot_rows(c, th, anch[cn], *dss[cn])
        k = np.argmax(V, axis=1)
        gaps[ci] = V[np.arange(N), k]
        args[ci] = k
        grads[ci] = G[np.arange(N), k]
    return gaps, args, grads, anch


def k0_state(x):
    """The float K0-BLOCKED test on the TIGHT bounding box.

    depth = -gap;  a square BLOCKS a slot iff gap < 0.  K0-BLOCKED iff every one
    of the four slots has >= 2 blockers (so no single removal frees any slot)."""
    gaps, _a, _g, anch = slot_gaps(x, use_bbox=True)
    depth = -gaps
    nb = (gaps < -TOL_BLOCK).sum(axis=1)
    order = np.argsort(-depth, axis=1)
    m1 = np.array([depth[k, order[k, 0]] for k in range(4)])
    m2 = np.array([depth[k, order[k, 1]] for k in range(4)])
    top2 = [(int(order[k, 0]), int(order[k, 1])) for k in range(4)]
    blockers = [sorted(int(j) for j in range(N) if gaps[k, j] < -TOL_BLOCK)
                for k in range(4)]
    return dict(n_block=[int(v) for v in nb], depth=depth, m1=m1, m2=m2,
                top2=top2, blockers=blockers,
                blocked=bool(nb.min() >= 2), min_m2=float(m2.min()),
                anchors={k: [float(v) for v in anch[k]] for k in CORNERS})


def is_blocked(x):
    return k0_state(x)['blocked']


def feas(x):
    ov, cv = cp85.feasibility(x)
    return ov, cv


# ============================================================ seed construction

_CENSUS = None


def census():
    global _CENSUS
    if _CENSUS is None:
        d = json.load(open(PAIRS))
        _CENSUS = d['surviving_level2']
    return _CENSUS


def _sample_box(b, rng):
    return (rng.uniform(b['x0'], b['x1']), rng.uniform(b['y0'], b['y1']),
            math.radians(rng.uniform(b['th0'], b['th1'])))


def _meets_unit_slot(cx, cy, t):
    """Does Q(c, t) meet the OPEN box (0,1)^2?  (BL corner frame.)"""
    q = sq_corners(np.array([[cx, cy]]), np.array([t]))[0]
    a = np.array([[0., 0.], [1., 0.], [1., 1.], [0., 1.]])
    co, si = math.cos(t), math.sin(t)
    axes = [(1., 0.), (0., 1.), (co, si), (-si, co)]
    for nx, ny in axes:
        pa = a @ np.array([nx, ny]); pq = q @ np.array([nx, ny])
        if pa.min() >= pq.max() or pq.min() >= pa.max():
            return False
    return True


def _pair_disjoint(c1, t1, c2, t2):
    C = np.array([c1, c2]); TH = np.array([t1, t2])
    q = sq_corners(C, TH)
    for o, p in ((0, 1), (1, 0)):
        for k in range(4):
            a = TH[o] + k * HALFPI
            n = np.array([math.cos(a), math.sin(a)])
            if (q[p] @ n).min() - C[o] @ n - H >= 0:
                return True
    return False


def _corner_map(cn, cx, cy, t, s):
    """D4 corner maps of the container [0,s]^2 taking the BL frame to corner cn."""
    if cn == 'BL':
        return cx, cy, t
    if cn == 'BR':
        return s - cx, cy, -t
    if cn == 'TL':
        return cx, s - cy, -t
    return s - cx, s - cy, t


def _inside_corner(cx, cy, t):
    """The square must stay inside the container: only the two near walls bind."""
    e = H * (abs(math.cos(t)) + abs(math.sin(t)))
    return cx - e >= 0.0 and cy - e >= 0.0


def draw_corner_pair(rng, tries=20000):
    """Two disjoint unit squares in the BL frame, both meeting the OPEN unit slot
    and both inside the container.

    A uniform draw from a census box pair is accepted about 0.45% of the time (the
    boxes are the level-2 SURVIVORS of the pruning, not certified placements, and
    the container walls are not part of the census), so the pairs are pooled once
    and reused."""
    C = census()
    for _ in range(tries):
        e = C[rng.randrange(len(C))]
        a = _sample_box(e['box_i'], rng)
        b = _sample_box(e['box_j'], rng)
        if rng.random() < 0.5:          # in-corner transpose (x,y,t) -> (y,x,pi/2-t)
            a = (a[1], a[0], HALFPI - a[2])
            b = (b[1], b[0], HALFPI - b[2])
        if not (_meets_unit_slot(*a) and _meets_unit_slot(*b)):
            continue
        if not (_inside_corner(*a) and _inside_corner(*b)):
            continue
        if not _pair_disjoint((a[0], a[1]), a[2], (b[0], b[1]), b[2]):
            continue
        return a, b
    return None


_POOL = None
POOL_SIZE = 2500


def pool(rng, n=None, log=None):
    global _POOL
    if _POOL is None:
        n = n or POOL_SIZE
        t0 = time.time()
        _POOL = []
        while len(_POOL) < n:
            p = draw_corner_pair(rng)
            if p is not None:
                _POOL.append(p)
        if log:
            log('corner-pair pool: %d pairs in %.0fs' % (len(_POOL), time.time() - t0))
    return _POOL


def build_seed(rng, s=None, tries=500, outer=8):
    """11 squares: 2 per corner (both intruding) + 3 in the middle, no overlap."""
    P = pool(rng)
    for _o in range(outer):
        ss = s if s is not None else rng.uniform(4.5, 5.5)
        cs, ts = [], []
        for cn in CORNERS:
            a, b = P[rng.randrange(len(P))]
            for (cx, cy, t) in (a, b):
                X, Y, T_ = _corner_map(cn, cx, cy, t, ss)
                cs.append([X, Y]); ts.append(T_)
        # cross-corner disjointness of the 8 corner squares
        bad = False
        for i in range(8):
            for j in range(i + 1, 8):
                if i // 2 == j // 2:
                    continue          # same corner: already disjoint by census
                if not _pair_disjoint((cs[i][0], cs[i][1]), ts[i],
                                      (cs[j][0], cs[j][1]), ts[j]):
                    bad = True; break
            if bad:
                break
        if bad:
            continue
        ok = True
        for _k in range(3):
            got = False
            for _t in range(tries):
                T_ = rng.uniform(0.0, HALFPI)
                ee = H * (abs(math.cos(T_)) + abs(math.sin(T_)))
                X = rng.uniform(ee, ss - ee); Y = rng.uniform(ee, ss - ee)
                if all(_pair_disjoint((X, Y), T_, (cs[q][0], cs[q][1]), ts[q])
                       for q in range(len(cs))):
                    cs.append([X, Y]); ts.append(T_); got = True
                    break
            if not got:
                ok = False; break
        if not ok:
            continue
        x = cp85.pack(np.array(cs), np.array(ts), float(ss))
        ov, cv = feas(x)
        if ov > 1e-12 or cv > 1e-12:
            continue
        if not is_blocked(x):
            continue
        return x
    return None


# ======================================================= K0-keeping constraints

def k0_cons(x, sel):
    """depth - EPS_KEEP >= 0 for the pinned (corner, square, SAT row) selection,
    in the CONTAINER frame (the slot anchors are 0 / s-1, so d/ds is exact)."""
    c, th, s = cp85.unpack(x)
    val = np.empty(len(sel)); J = np.zeros((len(sel), 3 * N + 1))
    anch = {'BL': (0.0, 0.0), 'BR': (s - 1.0, 0.0),
            'TL': (0.0, s - 1.0), 'TR': (s - 1.0, s - 1.0)}
    for m, (cn, i, row) in enumerate(sel):
        sx, sy = CSGN[cn]
        V, G = slot_rows(c[i:i + 1], th[i:i + 1], anch[cn], float(sx), float(sy))
        val[m] = -V[0, row] - EPS_KEEP
        g = -G[0, row]
        J[m, 2 * i] = g[0]; J[m, 2 * i + 1] = g[1]
        J[m, 2 * N + i] = g[2]; J[m, 3 * N] = g[3]
    return val, J


def select_k0(x):
    """The two deepest intruders per corner, with their active SAT row pinned."""
    gaps, args, _g, _a = slot_gaps(x, use_bbox=False)
    sel = []
    for ci, cn in enumerate(CORNERS):
        order = np.argsort(gaps[ci])       # most negative first = deepest
        for j in order[:2]:
            sel.append((cn, int(j), int(args[ci, int(j)])))
    return sel


# ------------------------------------------------------------------ SQP flow
# The A04 penalty ladder passes through wildly infeasible configurations at low
# mu, so "check K0-BLOCKED after each accepted step" is only meaningful along a
# FEASIBLE path.  The flow used here is therefore SLSQP on the side with ALL 55
# pair rows and all 44 container rows pinned to their current SAT axis, plus (in
# the constrained flow) the two deepest intruders per corner pinned to depth
# >= EPS_KEEP.  Every accepted iterate is strictified (fjpolish87.inflate) so the
# whole path is a path of genuine packings.

TRUST0 = 0.12            # initial trust-region radius (L_inf, all 34 coords)
TRUST_MIN = 2e-7
ROUNDS = 60
ROUNDS_FREE = 22         # flow A: free descent from the seed
ROUNDS_CONF = 34         # flow B: descent confined to K0-BLOCKED
ROUNDS_REL = 14          # flow C: K0 rows released at the confined endpoint
ROUNDS_DEEP = 120        # phase-2 deep re-run on the best endpoints
DEEP_N = 18              # how many endpoints get the deep re-run
POLISH_N = 26            # how many points go through the fjpolish87 ladder
EPS_LADDER = (1e-4, 1e-5, 1e-6, 1e-7, 1e-8)   # depth floors walked down in the deep pass


def strictify(x):
    """Nearest strictly-feasible canonical packing (fjpolish87.inflate)."""
    z = F.inflate(F.canonical(x_to_z(x)))
    y = z_to_x(z)
    ov, cv = feas(y)
    return y, float(F.enclosing_side(z)), ov, cv


_I, _J = cp85.I_IDX, cp85.J_IDX
_NP = cp85.NP
_PR = np.arange(_NP)


def pair_con_fast(x, kfix):
    """Vectorised cp85._pair_con_fixed (identical values and Jacobian)."""
    ov, aux = cp85.pair_overlaps(x)
    val = -ov[_PR, kfix]
    Jm = np.zeros((_NP, 3 * N + 1))
    nn = aux['n'][_PR, kfix]; nnp = aux['npr'][_PR, kfix]; dn = aux['dn'][_PR, kfix]
    sg = np.sign(dn); d = aux['d']; rp = aux['rp']
    ownerA = kfix < 2
    dnp = np.einsum('mj,mj->m', d, nnp)
    g_al = rp - np.where(ownerA, sg * dnp, 0.0)
    g_be = -rp - np.where(~ownerA, sg * dnp, 0.0)
    ga = -(sg)[:, None] * nn
    Jm[_PR, 2 * _I] = -ga[:, 0]
    Jm[_PR, 2 * _I + 1] = -ga[:, 1]
    Jm[_PR, 2 * _J] = ga[:, 0]
    Jm[_PR, 2 * _J + 1] = ga[:, 1]
    Jm[_PR, 2 * N + _I] = -g_al
    Jm[_PR, 2 * N + _J] = -g_be
    return val, Jm


_IDXN = np.arange(N)


def cont_con_fast(x):
    """Vectorised cp85._cont_con."""
    c, th, s = cp85.unpack(x)
    cth, sth = np.cos(th), np.sin(th)
    e = H * (np.abs(cth) + np.abs(sth))
    de = H * (-np.sign(cth) * sth + np.sign(sth) * cth)
    val = np.concatenate([c[:, 0] - e, s - c[:, 0] - e, c[:, 1] - e, s - c[:, 1] - e])
    Jm = np.zeros((4 * N, 3 * N + 1))
    Jm[_IDXN, 2 * _IDXN] = 1.0
    Jm[_IDXN, 2 * N + _IDXN] = -de
    Jm[N + _IDXN, 2 * _IDXN] = -1.0
    Jm[N + _IDXN, 2 * N + _IDXN] = -de
    Jm[N + _IDXN, 3 * N] = 1.0
    Jm[2 * N + _IDXN, 2 * _IDXN + 1] = 1.0
    Jm[2 * N + _IDXN, 2 * N + _IDXN] = -de
    Jm[3 * N + _IDXN, 2 * _IDXN + 1] = -1.0
    Jm[3 * N + _IDXN, 2 * N + _IDXN] = -de
    Jm[3 * N + _IDXN, 3 * N] = 1.0
    return val, Jm


class _Cache:
    """SLSQP asks for the value and the Jacobian in separate calls at the same
    point; evaluate once."""

    def __init__(self, f):
        self.f = f; self.key = None; self.out = None

    def __call__(self, z):
        k = z.tobytes()
        if k != self.key:
            self.key = k; self.out = self.f(z)
        return self.out

    def val(self, z):
        return self(z)[0]

    def jac(self, z):
        return self(z)[1]


def sqp_step(x, keep_k0, delta, maxiter=35):
    """One TRUST-REGION SLSQP move: minimise the side subject to all 55 pair rows
    and 44 container rows pinned to their current SAT axis (plus, when keep_k0,
    the two deepest intruders per corner at depth >= EPS_KEEP), inside the L_inf
    ball of radius delta.  Small steps keep the pinned axes valid and make the
    K0-BLOCKED exit, when it happens, a sharply located event."""
    ov, _aux = cp85.pair_overlaps(x)
    kfix = np.argmin(ov, axis=1)
    cp = _Cache(lambda z, k=kfix: pair_con_fast(z, k))
    cc = _Cache(cont_con_fast)
    cons = [dict(type='ineq', fun=cp.val, jac=cp.jac),
            dict(type='ineq', fun=cc.val, jac=cc.jac)]
    sel = select_k0(x)
    if keep_k0:
        ck = _Cache(lambda z, q=sel: k0_cons(z, q))
        cons.append(dict(type='ineq', fun=ck.val, jac=ck.jac))
    bnds = [(v - delta, v + delta) for v in x]
    e = np.eye(3 * N + 1)[3 * N]
    try:
        res = minimize(lambda z: z[3 * N], x, jac=lambda z: e, constraints=cons,
                       bounds=bnds, method='SLSQP',
                       options=dict(maxiter=maxiter, ftol=1e-14))
    except Exception:
        return None, sel
    y = res.x.copy()
    if not np.all(np.isfinite(y)):
        return None, sel
    return y, sel


def _blocked_feasible(w):
    """Strictify w and report (point, side, blocked)."""
    ws, sg, ov, cv = strictify(w)
    good = bool(np.isfinite(sg) and ov <= 1e-11 and cv <= 1e-9)
    return ws, sg, good, (good and is_blocked(ws))


def _bisect_exit_t(x, y, nit=44):
    """Largest t whose strictified iterate is still K0-BLOCKED, and the first
    that is not."""
    lo, hi = 0.0, 1.0
    for _ in range(nit):
        m = 0.5 * (lo + hi)
        _w, _s, good, blk = _blocked_feasible(x + m * (y - x))
        if good and blk:
            lo = m
        else:
            hi = m
    a = _blocked_feasible(x + lo * (y - x))
    b = _blocked_feasible(x + hi * (y - x))
    return a, b


def exit_mode(st0, st1):
    """Which corner freed, and how."""
    freed = [CORNERS[k] for k in range(4) if st1['n_block'][k] < 2]
    out = {'corners_freed': freed}
    modes = []
    for cn in freed:
        k = CORNERS.index(cn)
        b0 = set(st0['blockers'][k]); b1 = set(st1['blockers'][k])
        lost = sorted(b0 - b1); kept = sorted(b0 & b1); gained = sorted(b1 - b0)
        if gained:
            m = 'slot_rearranged'
        elif len(lost) == 1 and len(kept) >= 1:
            m = 'blocker_slid_away'
        elif len(lost) >= 2:
            m = 'slot_emptied'
        else:
            m = 'other'
        modes.append({'corner': cn, 'mode': m, 'lost': lost, 'kept': kept,
                      'gained': gained})
    out['modes'] = modes
    out['mode'] = modes[0]['mode'] if modes else 'none'
    return out


def _exit_record(x_ok, y_bad):
    a, b = _bisect_exit_t(x_ok, y_bad)
    xe, sge, ok_e, blk_e = a
    xb, sgb, ok_b, _blk_b = b
    st0 = k0_state(xe); st1 = k0_state(xb)
    em = exit_mode(st0, st1)
    em['sigma_exit'] = float(sge)
    em['sigma_after_exit'] = float(sgb)
    em['exit_feasible'] = bool(ok_e)
    em['exit_blocked'] = bool(blk_e)
    em['n_block_exit'] = st0['n_block']
    em['n_block_after'] = st1['n_block']
    em['m1_exit'] = [float(v) for v in st0['m1']]
    em['m2_exit'] = [float(v) for v in st0['m2']]
    return em, xe


def sqp_flow(x0, keep_k0, rounds=ROUNDS, delta0=TRUST0):
    """Feasible trust-region descent on the enclosing side.

    Every accepted iterate is a strictly feasible packing.  keep_k0 = False is
    the FREE flow (the K0-BLOCKED test is only a monitor: the flow stops and the
    exit is recorded the first time a step would leave the region); keep_k0 =
    True confines the flow to K0-BLOCKED by constraint and shrinks the step
    instead of leaving.

    Returns (end point, best feasible K0-BLOCKED point, exit record or None,
    accepted steps, last K0 selection)."""
    x, cur, ov, cv = strictify(x0)
    best = (cur, x.copy()) if (ov <= 1e-11 and cv <= 1e-9 and is_blocked(x)) else None
    em = None
    nstep = 0
    delta = delta0
    last_sel = select_k0(x)
    for _r in range(rounds):
        if delta < TRUST_MIN:
            break
        y, sel = sqp_step(x, keep_k0, delta)
        last_sel = sel
        if y is None:
            delta *= 0.4
            continue
        ws, sg, good, blk = _blocked_feasible(y)
        if not good or sg > cur - 1e-12:
            delta *= 0.4
            continue
        if not blk:
            if em is None:
                em, _xe = _exit_record(x, y)
            if not keep_k0:
                return x, best, em, nstep, last_sel
            delta *= 0.4
            continue
        x = ws; cur = sg; nstep += 1
        if best is None or sg < best[0]:
            best = (sg, ws.copy())
        delta = min(delta0, delta * 1.6)
    return x, best, em, nstep, last_sel


# ============================================================ conversions

def x_to_z(x):
    c, th, s = cp85.unpack(x)
    z = np.empty(34)
    z[0:33:3] = c[:, 0]; z[1:33:3] = c[:, 1]; z[2:33:3] = th
    z[33] = float(s)
    return z


def z_to_x(z):
    z = np.asarray(z, float)
    c = np.stack([z[0:33:3], z[1:33:3]], axis=1)
    return cp85.pack(c, z[2:33:3], float(z[33]))


def zfrac_of(z):
    return [Fraction(float(v)).limit_denominator(10 ** 15) for v in z]


# ------------------------------------------------- exact INNER-slot blocked test
# k0blocked87 pushes each slot INWARD by the interval width and counts
# n_block = |certified overlaps| + |UNKNOWN|.  Both choices are conservative for
# asserting K0-FREE and both are the WRONG way round for asserting K0-BLOCKED
# (an exact tangency such as Trump's square 3 on the top edge of the BL slot comes
# out as a certified overlap of the pushed slot).  So the blocked direction gets
# its own slot: the rational rectangle contained in the true slot for EVERY
# realisation of the interval bounding box,
#     BL: x in [xlo.b, xlo.a + 1]      BR: x in [xhi.b - 1, xhi.a]
# (and likewise in y), which is a SUBSET of the true unit slot; a certified
# overlap with it is therefore a certified overlap with the true slot.

def _rect_square_gap(rect, qs, th):
    """SAT gap between the exact rational rectangle and the interval square."""
    x0, x1, y0, y1 = [T._to_iv(v) for v in rect]
    sc = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    co, si = KB.iv.cos(th), KB.iv.sin(th)
    axes = [(KB.iv.mpf(1), KB.iv.mpf(0)), (KB.iv.mpf(0), KB.iv.mpf(1)),
            (co, si), (-si, co)]
    best = None
    for nx, ny in axes:
        ps = [nx * x + ny * y for x, y in sc]
        pj = [nx * x + ny * y for x, y in qs]
        los = his = ps[0]
        for p in ps[1:]:
            los = T.iv_min(los, p); his = T.iv_max(his, p)
        loj = hij = pj[0]
        for p in pj[1:]:
            loj = T.iv_min(loj, p); hij = T.iv_max(hij, p)
        gap = T.iv_max(loj - his, los - hij)
        best = gap if best is None else T.iv_max(best, gap)
    return best


def exact_blocked_test(zfrac, ladder=KB.DPS_LADDER):
    """Certified per-corner blocker counts against the INNER slot."""
    for dps in ladder:
        KB.set_dps(dps)
        pt = KB.ivpt(zfrac)
        Q = KB.all_corners_iv(pt)
        xlo, xhi, ylo, yhi = KB.bbox_iv(Q)
        one = Fraction(1)
        XA, XB = KB._lo_frac(xlo), KB._hi_frac(xlo)
        XC, XD = KB._lo_frac(xhi), KB._hi_frac(xhi)
        YA, YB = KB._lo_frac(ylo), KB._hi_frac(ylo)
        YC, YD = KB._lo_frac(yhi), KB._hi_frac(yhi)
        xs = {0: (XB, XA + one), 1: (XD - one, XC)}
        ys = {0: (YB, YA + one), 1: (YD - one, YC)}
        per = {}
        unknown = 0
        for cn in CORNERS:
            sx, sy = CSGN[cn]
            rect = (xs[sx][0], xs[sx][1], ys[sy][0], ys[sy][1])
            blockers, unk, gaps = [], [], []
            for j in range(11):
                g = _rect_square_gap(rect, Q[j], pt[3 * j + 2])
                gaps.append(float(T._mid(g)))
                if g.b < -TOL_BLOCK:
                    blockers.append(j)
                elif g.a >= -TOL_BLOCK:
                    continue
                else:
                    unk.append(j)
            unknown += len(unk)
            per[cn] = {'blockers': blockers, 'unknown': unk,
                       'n_block_certified': len(blockers),
                       'rect': [str(v) for v in rect],
                       'min_gap': min(gaps)}
        if unknown == 0:
            break
    KB.set_dps(30)
    cert = [per[c]['n_block_certified'] for c in CORNERS]
    return {'per_corner': per, 'dps': dps, 'n_unknown': unknown,
            'n_block_certified': cert,
            'n_unknown_per_corner': [len(per[c]['unknown']) for c in CORNERS],
            'min_n_block_certified': min(cert),
            'K0_BLOCKED_certified': bool(min(cert) >= 2)}


def exact_k0_test(z):
    """Exact verdicts on a rational config: the k0blocked87 FREE test (for
    reference) and the sound INNER-slot BLOCKED test, plus exact feasibility."""
    zf = zfrac_of(z)
    tel = KB.teleport_test(zf)
    blk = exact_blocked_test(zf)
    ver = F.verify_exact(zf)
    out = dict(blk)
    out['K0_FREE_k0blocked87'] = tel['K0_FREE']
    out['n_block_k0blocked87'] = [tel['per_corner'][c]['n_block'] for c in CORNERS]
    out['K0_FREE_0'] = tel['K0_FREE_0']
    out['K0_FREE_teleport'] = tel['K0_FREE_teleport']
    out['K0_FREE'] = tel['K0_FREE']
    return out, ver


# ============================================================ per-seed driver

def run_seed(tag, rng, meta=None):
    t0 = time.time()
    rec = {'tag': tag}
    if meta:
        rec.update(meta)
    x0 = None
    for _ in range(40):
        x0 = build_seed(rng)
        if x0 is not None:
            break
    if x0 is None:
        rec['status'] = 'seed_failed'
        rec['secs'] = time.time() - t0
        return rec, None
    st0 = k0_state(x0)
    rec['sigma_seed'] = enclosing_side_x(x0)
    rec['seed_n_block'] = st0['n_block']
    rec['seed_m2'] = [float(v) for v in st0['m2']]

    # ---- flow A: the FREE descent, halted at the K0-BLOCKED boundary
    xf, best_free, em, nf, _sf = sqp_flow(x0, keep_k0=False, rounds=ROUNDS_FREE)
    rec['free_exit'] = em
    rec['free_exited'] = bool(em is not None)
    rec['sigma_free_best'] = best_free[0] if best_free else None
    rec['free_steps'] = nf

    # ---- flow B: the same descent CONFINED to K0-BLOCKED
    xc, best_c, em2, nc, sel = sqp_flow(x0, keep_k0=True, rounds=ROUNDS_CONF)
    rec['confined_exit_attempt'] = em2
    rec['confined_steps'] = nc
    rec['sigma_confined'] = best_c[0] if best_c else None
    xb = best_c[1] if best_c else xc

    # ---- flow C: RELEASE the K0 rows at the confined endpoint.  If the side can
    # still be driven down there, the endpoint is not a critical point of the side
    # -- it was only held up by the K0 constraint, i.e. it sits ON the boundary of
    # K0-BLOCKED and is not an FJ point of the enclosing-side function.
    xr, best_r, em3, nr, _s3 = sqp_flow(xb, keep_k0=False, rounds=ROUNDS_REL)
    rec['release_steps'] = nr
    rec['release_exit'] = em3
    rec['sigma_release_end'] = float(enclosing_side_x(xr))
    rec['release_drop'] = float((rec['sigma_confined'] or 0.0)
                                - rec['sigma_release_end']) \
        if rec['sigma_confined'] else None
    rec['critical_in_region'] = bool(rec['release_drop'] is not None
                                     and rec['release_drop'] < 1e-7
                                     and nr == 0)
    val, _J = k0_cons(xb, select_k0(xb))
    rec['constrained'] = {
        'k0_row_values': [float(v) for v in val],
        'min_k0_row': float(val.min()) if len(val) else None,
        'k0_rows_slack': bool(len(val) and val.min() > SLACK_TOL),
        'sel': [[c, i, r] for (c, i, r) in select_k0(xb)]}

    cands = []
    for lbl, bb in (('free', best_free), ('confined', best_c)):
        if bb is not None:
            cands.append((bb[0], lbl, bb[1]))
    cands.sort(key=lambda t: t[0])
    xbest = cands[0][2] if cands else xf
    rec['sigma_best_blocked'] = float(cands[0][0]) if cands else None
    rec['best_from'] = cands[0][1] if cands else None
    st = k0_state(xbest)
    rec['blocked_at_best'] = bool(st['blocked'])
    rec['best_n_block'] = st['n_block']
    rec['best_m1'] = [float(v) for v in st['m1']]
    rec['best_m2'] = [float(v) for v in st['m2']]
    ovb, cvb = feas(xbest)
    rec['best_ov'] = float(ovb); rec['best_cv'] = float(cvb)
    rec['status'] = 'ok'
    rec['secs'] = time.time() - t0
    return rec, xbest


def polish_to_fj(tag, x, meta=None):
    """fjpolish87 ladder + exact K0-BLOCKED re-test of the polished point."""
    z = F.canonical(x_to_z(x))
    out = {'tag': tag}
    if meta:
        out.update(meta)
    # fjpolish87.process only stores z_polished for its GENUINE points, and the
    # question here needs the polished configuration in every case, so the same
    # ladder (flow -> inflate -> Newton on the carrying active set -> verdict) is
    # run here directly out of fjpolish87's own pieces.
    try:
        out['sigma_in_polish'] = F.enclosing_side(z)
        z1, fi = F.flow(z)
        out['flow'] = {k: fi.get(k) for k in ('tol', 'it', 'reason', 'status')
                       if k in fi}
        out['sigma_flow'] = F.enclosing_side(F.canonical(z1))
        zp = F.inflate(F.canonical(z1))
        tol = min(max(fi.get('tol', F.TOL_LADDER[0]), F.TOL_LADDER[0]),
                  F.TOL_LADDER[-1])
        rows, _info = F.classify(zp, tol)
        out['newton'] = None
        if rows:
            A = F.gradA(zp, rows)
            _res, lam, _r = F.cone_nnls(A)
            zn, fres = F.newton_polish(zp, rows, lam)
            out['newton'] = {'tol': tol, 'm_rows': len(rows), 'fres': float(fres)}
            if fres < 1e-9:
                zp = F.inflate(F.canonical(zn))
        v1 = F.verdict(zp, tag + ':polished')
    except Exception as ex:
        out['polish_error'] = repr(ex)[:200]
        return out
    out['sigma_polished'] = v1['sigma']
    out['fj_feasible_any_tol'] = v1['fj_feasible_any_tol']
    out['fj_at_tight_tol'] = v1['fj_at_tight_tol']
    out['packing_feasible'] = v1['packing_feasible']
    out['k_flush_corner'] = v1['k_flush_corner']
    out['genuine'] = v1['genuine']
    out['genuine_tight'] = v1['genuine_tight']
    lad0 = v1['ladder'][0]
    out['cone_residual_1e-6'] = lad0.get('cone_residual')
    out['m_active_1e-6'] = lad0.get('m_active')
    out['n_rattlers'] = lad0.get('n_rattlers')
    zz = np.asarray(F.canonical(zp), float)
    out['has_z'] = True
    if zz is not None:
        xp = z_to_x(zz)
        st = k0_state(xp)
        out['polished_n_block'] = st['n_block']
        out['polished_m2'] = [float(v) for v in st['m2']]
        out['polished_blocked_float'] = st['blocked']
        try:
            tel, ver = exact_k0_test(zz)
            out['exact_n_block'] = tel['n_block_certified']
            out['exact_n_unknown'] = tel['n_unknown_per_corner']
            out['exact_min_n_block'] = tel['min_n_block_certified']
            out['exact_K0_FREE'] = tel['K0_FREE']
            out['exact_K0_BLOCKED'] = tel['K0_BLOCKED_certified']
            out['verify'] = ver
            out['z_polished'] = [T.frac_str(v) for v in zfrac_of(zz)] \
                if tel['K0_BLOCKED_certified'] else None
        except Exception as ex:
            out['exact_error'] = repr(ex)[:200]
    return out


# ============================================================ selftest / canary

def trump_x():
    P, s = None, None
    import atlas85
    A, s = atlas85.trump_placements()
    A = np.asarray(A, float)
    return cp85.pack(A[:, :2], A[:, 2].copy(), float(s))


def canary(log=print):
    """Trump: TL is a genuine 2-crowd (depths ~0.168 / 0.155), the other three
    corner slots hold exactly ONE square each (so they are K0-FREE by teleport).
    Then the 'nick' perturbation of the three slot squares must be handled."""
    ok = True
    x = trump_x()
    st = k0_state(x)
    log('canary: Trump s = %.12f' % enclosing_side_x(x))
    for k, cn in enumerate(CORNERS):
        log('   %s n_block=%d blockers=%s m1=%.6f m2=%.6f'
            % (cn, st['n_block'][k], st['blockers'][k], st['m1'][k], st['m2'][k]))
    exp = {'BL': 1, 'BR': 1, 'TL': 2, 'TR': 1}
    for k, cn in enumerate(CORNERS):
        if st['n_block'][k] != exp[cn]:
            log('   FAIL %s: n_block %d expected %d' % (cn, st['n_block'][k], exp[cn]))
            ok = False
    kTL = CORNERS.index('TL')
    d = sorted([st['m1'][kTL], st['m2'][kTL]], reverse=True)
    if not (abs(d[0] - 0.168) < 6e-3 and abs(d[1] - 0.155) < 6e-3):
        log('   FAIL TL depths %.6f / %.6f, expected ~0.168 / 0.155' % (d[0], d[1]))
        ok = False
    else:
        log('   TL 2-crowd depths %.6f / %.6f  (expected 0.168 / 0.155)  OK' % (d[0], d[1]))
    if not st['blocked']:
        log('   Trump is NOT K0-BLOCKED (BL/BR/TR each hold one square)  OK')
    else:
        log('   FAIL: Trump reported K0-BLOCKED'); ok = False

    # ---- the perturbed seed: nudge the three flush slot squares (0, 2, 5) so they
    # only NICK their slots, repair the packing with fjpolish87.inflate, and check
    # the verdict; then undo the perturbation and check the verdict is restored.
    c, th, s = cp85.unpack(x)
    stp = None
    for amp in (3e-3, 1e-2, 3e-2, 1e-1):
        c2 = c.copy(); th2 = th.copy()
        for i, (dx, dy, dt) in ((0, (1.4, 1.0, 1.8)), (2, (-1.2, 1.0, -1.6)),
                                (5, (-1.0, -1.2, 2.2))):
            c2[i] = c2[i] + amp * np.array([dx, dy])
            th2[i] = th2[i] + amp * dt
        xp = cp85.pack(c2, th2, s)
        ovp0, _cv0 = feas(xp)
        xp = z_to_x(F.inflate(F.canonical(x_to_z(xp))))
        stp = k0_state(xp)
        ovp, cvp = feas(xp)
        log('canary: nicked Trump amp=%.0e  sigma %.9f  overlap %.2e -> %.2e  '
            'n_block %s  blocked %s'
            % (amp, enclosing_side_x(xp), ovp0, ovp, stp['n_block'], stp['blocked']))
        for k, cn in enumerate(CORNERS):
            log('     %s blockers=%s m1=%.6f m2=%.6f'
                % (cn, stp['blockers'][k], stp['m1'][k], stp['m2'][k]))
        if ovp > 1e-9 or cvp > 1e-9:
            log('   FAIL: nicked canary seed is not feasible'); ok = False
        if stp['blocked']:
            log('   FAIL: nicking a 1-crowd cannot make it a 2-crowd'); ok = False
        if amp <= 1e-2 and stp['n_block'][CORNERS.index('TL')] != 2:
            log('   FAIL: TL lost its 2-crowd under a %.0e nick' % amp); ok = False
    # undo
    st3 = k0_state(trump_x())
    if st3['n_block'] != st['n_block'] or st3['blockers'] != st['blockers']:
        log('   FAIL: undoing the perturbation did not restore the verdict'); ok = False
    else:
        log('   perturbation undone -> verdict restored exactly  OK')

    # exact interval cross-check of the Trump verdict (certified blockers only)
    tel, _ver = exact_k0_test(x_to_z(trump_x()))
    ex = tel['n_block_certified']
    unk = tel['n_unknown_per_corner']
    log('   EXACT interval test: certified n_block = %s, UNKNOWN = %s (float %s)'
        % (ex, unk, st['n_block']))
    if ex != st['n_block']:
        log('   FAIL: float and exact certified tests disagree on Trump'); ok = False
    if tel['K0_BLOCKED_certified']:
        log('   FAIL: exact test calls Trump K0-BLOCKED'); ok = False
    log('canary: %s' % ('PASS' if ok else 'FAIL'))
    return ok, {'trump_n_block': st['n_block'],
                'trump_blockers': st['blockers'],
                'trump_TL_depths': [float(d[0]), float(d[1])],
                'perturbed_n_block': stp['n_block'],
                'perturbed_blocked': stp['blocked'],
                'exact_n_block': ex, 'exact_unknown': unk, 'pass': ok}


def selftest(log=print):
    ok = True
    rng = random.Random(12345)
    # 1. slot_rows gradients vs finite differences
    c = np.array([[0.7, 0.62]]); th = np.array([0.4])
    s = 4.8
    for cn in CORNERS:
        sx, sy = CSGN[cn]
        anch = (0.0 if sx == 0 else s - 1.0, 0.0 if sy == 0 else s - 1.0)
        V, G = slot_rows(c, th, anch, float(sx), float(sy))
        h = 1e-6
        for row in range(8):
            num = []
            for k in range(4):
                cc = c.copy(); tt = th.copy(); ss = s
                if k == 0: cc[0, 0] += h
                elif k == 1: cc[0, 1] += h
                elif k == 2: tt[0] += h
                else: ss = s + h
                aa = (0.0 if sx == 0 else ss - 1.0, 0.0 if sy == 0 else ss - 1.0)
                V2, _ = slot_rows(cc, tt, aa, float(sx), float(sy))
                num.append((V2[0, row] - V[0, row]) / h)
            err = np.max(np.abs(np.array(num) - G[0, row]))
            if err > 2e-5:
                log('FAIL grad %s row %d err %.2e' % (cn, row, err)); ok = False
    log('selftest: slot_rows gradients OK' if ok else 'selftest: gradient FAIL')

    # 2. SAT gap sign vs a brute-force sampling overlap test for random squares
    bad = 0
    for _ in range(4000):
        cx = rng.uniform(-0.6, 1.9); cy = rng.uniform(-0.6, 1.9)
        t = rng.uniform(0, HALFPI)
        V, _ = slot_rows(np.array([[cx, cy]]), np.array([t]), (0.0, 0.0))
        g = V[0].max()
        meet = _meets_unit_slot(cx, cy, t)
        if abs(g) > 1e-9 and (g < 0.0) != meet:
            bad += 1
    if bad:
        log('FAIL SAT/meet disagreement on %d/4000 samples' % bad); ok = False
    else:
        log('selftest: SAT gap sign == open-slot meet on 4000 samples OK')

    # 3. seed builder produces K0-BLOCKED feasible packings
    n_try, n_ok = 40, 0
    for i in range(n_try):
        x = build_seed(rng)
        if x is not None:
            n_ok += 1
            st = k0_state(x)
            assert st['blocked'] and min(st['n_block']) >= 2
    log('selftest: seed builder %d/%d K0-BLOCKED feasible' % (n_ok, n_try))
    if n_ok < n_try // 2:
        log('FAIL: seed yield too low'); ok = False

    # 4. exact vs float agreement on a random seed
    x = None
    while x is None:
        x = build_seed(rng)
    tel, _v = exact_k0_test(x_to_z(x))
    ex = tel['n_block_certified']
    fl = k0_state(x)['n_block']
    log('selftest: random seed exact certified n_block %s (unknown %s) vs float %s'
        % (ex, tel['n_unknown_per_corner'], fl))
    if ex != fl:
        log('NOTE: certified count may lag the float count by an UNKNOWN row')
        if any(abs(e - f) > 1 for e, f in zip(ex, fl)):
            log('FAIL: exact and float differ by more than one UNKNOWN'); ok = False
    log('selftest: %s' % ('PASS' if ok else 'FAIL'))
    return ok


# ============================================================ campaign

def run(nseeds=520, seed=20260903, wall=9000.0, log=print):
    rng = random.Random(seed)
    t0 = time.time()
    recs = []
    best = None            # (sigma, x, tag)  lowest-sigma feasible K0-BLOCKED packing
    fj_inputs = []
    with open(OUT_JL, 'w') as fh:
        for i in range(nseeds):
            if time.time() - t0 > wall:
                log('wall clock cap reached after %d seeds' % i)
                break
            tag = 's%04d' % i
            rec, xb = run_seed(tag, rng)
            if xb is not None and rec.get('sigma_best_blocked') is not None \
                    and rec.get('blocked_at_best') and rec['best_ov'] <= 1e-9 \
                    and rec['best_cv'] <= 1e-9:
                sg = rec['sigma_best_blocked']
                if best is None or sg < best[0]:
                    best = (sg, xb.copy(), tag)
                fj_inputs.append((sg, tag, xb.copy(),
                                  bool(rec['constrained'].get('k0_rows_slack'))))
            fh.write(json.dumps(rec) + '\n'); fh.flush()
            recs.append(rec)
            if (i + 1) % 25 == 0:
                log('  %4d seeds, %.0fs, best K0-BLOCKED sigma = %s'
                    % (i + 1, time.time() - t0,
                       ('%.9f' % best[0]) if best else 'none'))
    log('descent phase: %d seeds in %.0fs' % (len(recs), time.time() - t0))

    # ---- phase 2: DEEP re-run of the confined flow on the lowest endpoints
    fj_inputs.sort(key=lambda t: t[0])
    deep = []
    for sg, tag, xb, slack in fj_inputs[:DEEP_N]:
        if time.time() - t0 > wall + 1200:
            log('deep cap reached'); break
        # The confined flow presses against the artificial depth floor EPS_KEEP,
        # so the floor is walked down: each stage re-converges with a thinner
        # required intrusion, tracing sigma_min(K0-BLOCKED with depth >= eps).
        best_d = None
        xcur = xb
        ladder = []
        for eps in EPS_LADDER:
            globals()['EPS_KEEP'] = eps
            xd, bd, emd, nd, _sd = sqp_flow(xcur, keep_k0=True,
                                            rounds=ROUNDS_DEEP, delta0=0.04)
            if bd is None:
                break
            best_d = bd
            xcur = bd[1]
            ladder.append({'eps': eps, 'sigma': float(bd[0]), 'steps': nd})
        globals()['EPS_KEEP'] = EPS_LADDER[0]
        if best_d is None:
            continue
        sgd, xdb = best_d
        nd = sum(r['steps'] for r in ladder)
        xr, _br, _emr, nrel, _sr = sqp_flow(xdb, keep_k0=False, rounds=ROUNDS_REL)
        drop = sgd - enclosing_side_x(xr)
        val, _J = k0_cons(xdb, select_k0(xdb))
        d = {'tag': tag, 'sigma_in': sg, 'sigma_deep': float(sgd),
             'deep_steps': nd, 'release_steps': nrel, 'release_drop': float(drop),
             'min_k0_row': float(val.min()), 'k0_rows_slack': bool(val.min() > SLACK_TOL),
             'critical_in_region': bool(nrel == 0 and drop < 1e-7),
             'eps_ladder': ladder,
             'n_block': k0_state(xdb)['n_block'],
             'm1': [float(v) for v in k0_state(xdb)['m1']],
             'm2': [float(v) for v in k0_state(xdb)['m2']]}
        deep.append((sgd, tag, xdb.copy(), d))
        if best is None or sgd < best[0]:
            best = (sgd, xdb.copy(), tag)
        log('  deep %s %.6f -> %.9f (%d steps) [%s], release drop %.2e (%d steps), '
            'min k0 row %.2e'
            % (tag, sg, sgd, nd,
               ' '.join('%.0e:%.7f' % (r['eps'], r['sigma']) for r in ladder),
               drop, nrel, val.min()))
    deep.sort(key=lambda t: t[0])
    with open(os.path.join(RESULTS, 'k0dir87.deep.jsonl'), 'w') as fh:
        for _sg, _tg, _x, d in deep:
            fh.write(json.dumps(d) + '\n')

    # ---- FJ polish: the deep endpoints first, then the interior (slack) ones.
    fj_inputs = [(sg, tag, xx, bool(d['k0_rows_slack']))
                 for sg, tag, xx, d in deep] + fj_inputs
    seen = set()
    ded = []
    for it in fj_inputs:
        k = (it[1], round(it[0], 9))
        if k in seen:
            continue
        seen.add(k); ded.append(it)
    fj_inputs = ded
    picked = fj_inputs[:POLISH_N]
    log('FJ polish on %d candidates (%d with slack K0 rows)'
        % (len(picked), sum(1 for p in picked if p[3])))
    pol = []
    for sg, tag, xb, slack in picked:
        if time.time() - t0 > wall + 2400:
            log('polish cap reached'); break
        p = polish_to_fj(tag, xb, {'sigma_in': sg, 'k0_rows_slack': slack})
        pol.append(p)
        log('  %s sigma_in %.6f -> polished %s  FJ(1e-6) %s  exact_min_n_block %s'
            % (tag, sg, ('%.9f' % p['sigma_polished']) if 'sigma_polished' in p else '-',
               p.get('fj_at_tight_tol'), p.get('exact_min_n_block')))

    # ---- the record holder: exact verification
    rec_best = None
    if best is not None:
        sg, xb, tag = best
        z = F.canonical(x_to_z(xb))
        zi = F.inflate(z)
        xi = z_to_x(zi)
        st = k0_state(xi)
        tel, ver = exact_k0_test(zi)
        rec_best = {
            'tag': tag, 'sigma_float': float(sg),
            'sigma_inflated': F.enclosing_side(zi),
            'blocked_after_inflate': st['blocked'],
            'n_block': st['n_block'],
            'm1': [float(v) for v in st['m1']], 'm2': [float(v) for v in st['m2']],
            'exact_n_block': tel['n_block_certified'],
            'exact_n_unknown': tel['n_unknown_per_corner'],
            'exact_min_n_block': tel['min_n_block_certified'],
            'exact_K0_BLOCKED': tel['K0_BLOCKED_certified'],
            'verify': ver,
            'z': [T.frac_str(v) for v in zfrac_of(zi)]}
        log('lowest K0-BLOCKED packing: sigma %.12f (tag %s), exact n_block %s, '
            'disjoint_certified %s, side_upper %.12f'
            % (rec_best['sigma_inflated'], tag, rec_best['exact_n_block'],
               ver['disjoint_certified'], ver['side_upper_bound']))

    summ = summarise(recs, pol, rec_best, deep)
    json.dump(summ, open(OUT_JS, 'w'), indent=1)
    with open(os.path.join(RESULTS, 'k0dir87.polish.jsonl'), 'w') as fh:
        for p in pol:
            fh.write(json.dumps(p) + '\n')
    write_md(summ)
    return summ


def summarise(recs, pol, rec_best, deep=()):
    ok = [r for r in recs if r.get('status') == 'ok']
    exits = [r['free_exit'] for r in ok if r.get('free_exit')]
    ex_sig = sorted(e['sigma_exit'] for e in exits)
    modes = {}
    corners_freed = {}
    for e in exits:
        for m in e['modes']:
            modes[m['mode']] = modes.get(m['mode'], 0) + 1
            corners_freed[m['corner']] = corners_freed.get(m['corner'], 0) + 1
    sig_best = [r['sigma_best_blocked'] for r in ok
                if r.get('sigma_best_blocked') is not None]
    slack = [r for r in ok if r.get('constrained', {}).get('k0_rows_slack')]
    fj_blocked = [p for p in pol if p.get('exact_K0_BLOCKED')]
    fj_any = [p for p in pol if p.get('fj_at_tight_tol')]
    fj_both = [p for p in fj_blocked if p.get('fj_at_tight_tol')]
    dd = [d for _a, _b, _c, d in deep]
    rel = sorted(r['release_drop'] for r in ok if r.get('release_drop') is not None)
    return {
        'n_seeds_attempted': len(recs),
        'n_seeds_built': len(ok),
        'n_seed_failed': sum(1 for r in recs if r.get('status') == 'seed_failed'),
        'n_exited': len(exits),
        'n_no_exit': len(ok) - len(exits),
        'exit_sigma': {
            'min': ex_sig[0] if ex_sig else None,
            'p10': ex_sig[len(ex_sig) // 10] if ex_sig else None,
            'median': ex_sig[len(ex_sig) // 2] if ex_sig else None,
            'p90': ex_sig[9 * len(ex_sig) // 10] if ex_sig else None,
            'max': ex_sig[-1] if ex_sig else None,
            'hist': hist(ex_sig)},
        'exit_modes': modes,
        'exit_corner': corners_freed,
        'sigma_best_blocked': {
            'min': min(sig_best) if sig_best else None,
            'median': sorted(sig_best)[len(sig_best) // 2] if sig_best else None,
            'hist': hist(sorted(sig_best))},
        'n_constrained_slack': len(slack),
        'n_critical_in_region': sum(1 for r in ok if r.get('critical_in_region')),
        'release_drop': {
            'min': rel[0] if rel else None,
            'median': rel[len(rel) // 2] if rel else None,
            'max': rel[-1] if rel else None,
            'n_below_1e-7': sum(1 for v in rel if v < 1e-7)},
        'deep': {
            'n': len(dd),
            'min_sigma': min((d['sigma_deep'] for d in dd), default=None),
            'n_k0_rows_slack': sum(1 for d in dd if d['k0_rows_slack']),
            'n_critical_in_region': sum(1 for d in dd if d['critical_in_region']),
            'min_release_drop': min((d['release_drop'] for d in dd), default=None),
            'rows': sorted(dd, key=lambda d: d['sigma_deep'])[:12]},
        'n_polished': len(pol),
        'n_fj_at_tight_tol': len(fj_any),
        'n_polished_still_K0_BLOCKED_exact': len(fj_blocked),
        'n_fj_points_K0_BLOCKED_exact': len(fj_both),
        'lowest_sigma_K0_BLOCKED_FJ':
            min((p['sigma_polished'] for p in fj_both), default=None),
        'K0_BLOCKED_FJ_rows': sorted(
            [{'tag': p['tag'], 'sigma': p.get('sigma_polished'),
              'n_block': p.get('exact_n_block'), 'm2': p.get('polished_m2'),
              'verify': p.get('verify')} for p in fj_both],
            key=lambda r: (r['sigma'] if r['sigma'] is not None else 9e9))[:10],
        'polished_min_sigma': min((p.get('sigma_polished', 9e9) for p in pol),
                                  default=None),
        'polished_exact_min_n_block_hist':
            hist_int([p.get('exact_min_n_block') for p in pol
                      if p.get('exact_min_n_block') is not None]),
        'record_K0_BLOCKED_packing': rec_best,
        's_hat': S_HAT, 's0': S0F}


def hist(xs, nb=12):
    if not xs:
        return []
    lo, hi = xs[0], xs[-1]
    if hi <= lo:
        return [[lo, hi, len(xs)]]
    out = []
    for k in range(nb):
        a = lo + (hi - lo) * k / nb
        b = lo + (hi - lo) * (k + 1) / nb
        n = sum(1 for v in xs if (a <= v < b) or (k == nb - 1 and v == b))
        out.append([a, b, n])
    return out


def hist_int(xs):
    d = {}
    for v in xs:
        d[str(v)] = d.get(str(v), 0) + 1
    return d


def write_md(s):
    L = []
    L.append('# A87 chore: directed critical-point search INSIDE K0-BLOCKED\n')
    L.append('## Headline\n')
    L.append('* Fritz-John points found inside K0-BLOCKED: **%d**.'
             % s['n_fj_points_K0_BLOCKED_exact'])
    lo = s['lowest_sigma_K0_BLOCKED_FJ']
    L.append('* Lowest sigma of a K0-BLOCKED FJ point: **%s**.'
             % ('%.12f' % lo if lo is not None else 'None (none exists in the sample)'))
    rb = s.get('record_K0_BLOCKED_packing')
    if rb:
        L.append('* Lowest sigma reached by ANY K0-BLOCKED packing along any flow: '
                 '**%.12f** (tag %s), exact per-corner n_block %s, pair-disjointness '
                 'certified %s, certified side upper bound %.12f.'
                 % (rb['sigma_inflated'], rb['tag'], rb['exact_n_block'],
                    rb['verify']['disjoint_certified'],
                    rb['verify']['side_upper_bound']))
    L.append('* s_hat = %.12f, s0 = %.12f.\n' % (s['s_hat'], s['s0']))
    L.append('## Counts\n')
    L.append('| quantity | value |')
    L.append('| --- | ---: |')
    for k in ('n_seeds_attempted', 'n_seeds_built', 'n_seed_failed', 'n_exited',
              'n_no_exit', 'n_constrained_slack', 'n_critical_in_region',
              'n_polished', 'n_fj_at_tight_tol',
              'n_polished_still_K0_BLOCKED_exact',
              'n_fj_points_K0_BLOCKED_exact'):
        L.append('| %s | %s |' % (k, s.get(k)))
    d = s.get('deep', {})
    for k in ('n', 'min_sigma', 'n_k0_rows_slack', 'n_critical_in_region',
              'min_release_drop'):
        L.append('| deep.%s | %s |' % (k, d.get(k)))
    L.append('')
    L.append('## Deep re-runs (lowest confined endpoints, K0 rows then released)\n')
    L.append('| tag | sigma_deep | steps | min k0 row | release drop | rel steps '
             '| n_block | depths (m2) |')
    L.append('| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |')
    for r in d.get('rows', []):
        L.append('| %s | %.9f | %d | %.2e | %.2e | %d | %s | %s |'
                 % (r['tag'], r['sigma_deep'], r['deep_steps'], r['min_k0_row'],
                    r['release_drop'], r['release_steps'], r['n_block'],
                    ' '.join('%.4f' % v for v in r['m2'])))
    L.append('')
    L.append('## Exit sigmas\n')
    e = s['exit_sigma']
    L.append('| stat | sigma |')
    L.append('| --- | ---: |')
    for k in ('min', 'p10', 'median', 'p90', 'max'):
        L.append('| %s | %s |' % (k, ('%.9f' % e[k]) if e[k] is not None else '-'))
    L.append('')
    L.append('| bin lo | bin hi | count |')
    L.append('| ---: | ---: | ---: |')
    for a, b, n in e['hist']:
        L.append('| %.6f | %.6f | %d |' % (a, b, n))
    L.append('')
    L.append('## Exit modes / corner\n')
    L.append('| mode | count |')
    L.append('| --- | ---: |')
    for k, v in sorted(s['exit_modes'].items(), key=lambda t: -t[1]):
        L.append('| %s | %d |' % (k, v))
    L.append('')
    L.append('| corner freed | count |')
    L.append('| --- | ---: |')
    for k, v in sorted(s['exit_corner'].items(), key=lambda t: -t[1]):
        L.append('| %s | %d |' % (k, v))
    L.append('')
    L.append('## Lowest K0-BLOCKED sigma per seed\n')
    b = s['sigma_best_blocked']
    L.append('min %s, median %s\n'
             % (('%.9f' % b['min']) if b['min'] is not None else '-',
                ('%.9f' % b['median']) if b['median'] is not None else '-'))
    L.append('| bin lo | bin hi | count |')
    L.append('| ---: | ---: | ---: |')
    for a, bb, n in b['hist']:
        L.append('| %.6f | %.6f | %d |' % (a, bb, n))
    L.append('')
    L.append('## Polished points: exact min_n_block over the four slots\n')
    L.append('| min_n_block | count |')
    L.append('| ---: | ---: |')
    for k, v in sorted(s['polished_exact_min_n_block_hist'].items()):
        L.append('| %s | %d |' % (k, v))
    L.append('')
    open(OUT_MD, 'w').write('\n'.join(L) + '\n')


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if cmd == 'selftest':
        sys.exit(0 if selftest() else 1)
    elif cmd == 'canary':
        ok, _ = canary()
        sys.exit(0 if ok else 1)
    elif cmd == 'run':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 520
        w = float(sys.argv[3]) if len(sys.argv) > 3 else 9000.0
        lf = open(os.path.join(LOGS, 'k0dir87.log'), 'w', buffering=1)

        def log(*a):
            m = ' '.join(str(v) for v in a)
            lf.write(m + '\n'); lf.flush()
            print(m, flush=True)
        ok1 = selftest(log)
        ok2, cn = canary(log)
        if not (ok1 and ok2):
            log('SELFTEST/CANARY FAILED -- not running the campaign')
            sys.exit(1)
        s = run(n, wall=w, log=log)
        s['canary'] = cn
        json.dump(s, open(OUT_JS, 'w'), indent=1)
        write_md(s)
    elif cmd == 'report':
        write_md(json.load(open(OUT_JS)))
    elif cmd == 'dh':
        # post-hoc: flat dimension d_H = 33 - rank33 of the active gradient matrix
        # at every polished point that came out EXACTLY K0-BLOCKED.
        path = os.path.join(RESULTS, 'k0dir87.polish.jsonl')
        rows = [json.loads(ln) for ln in open(path) if ln.strip()]
        out = []
        for r in rows:
            if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
                continue
            z = np.array([float(Fraction(v)) for v in r['z_polished']])
            v = F.verdict(z, r['tag'])
            l0 = v['ladder'][0]
            e = {'tag': r['tag'], 'sigma': v['sigma'],
                 'fj_at_tight_tol': v['fj_at_tight_tol'],
                 'cone_residual': l0.get('cone_residual'),
                 'm_active': l0.get('m_active'), 'rank33': l0.get('rank33'),
                 'd_H': (33 - l0['rank33']) if l0.get('rank33') is not None else None,
                 'n_rattlers': l0.get('n_rattlers'),
                 'n_block': r.get('exact_n_block'), 'm2': r.get('polished_m2')}
            out.append(e)
            print(json.dumps(e))
        json.dump(out, open(os.path.join(RESULTS, 'k0dir87.dh.json'), 'w'), indent=1)
        print('%d K0-BLOCKED polished points' % len(out))
    else:
        ok1 = selftest()
        ok2, _ = canary()
        if not (ok1 and ok2):
            print('SELFTEST/CANARY FAILED -- not running the campaign')
            sys.exit(1)
        run()


if __name__ == '__main__':
    main()
