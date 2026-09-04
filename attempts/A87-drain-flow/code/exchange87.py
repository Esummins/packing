r"""exchange87.py -- A87 chore: CORNER EXCHANGE at fixed side.

PI question: can every K0-BLOCKED packing be converted to a k >= 1 packing at
the SAME side by a non-rigid exchange?

Procedure, per corner c of each packing (side m fixed throughout):

  (1) REMOVE the corner's two intruders A, B (the squares meeting the OPEN unit
      slot at c, i.e. depth > 0 in c's frame, per A90 t3_90's corner census).
      If more than two meet it, remove the two DEEPEST and record.
  (2) SLOT: place the axis-aligned unit square exactly in the corner slot.
      Check interior-disjointness from the remaining 9 (interval SAT on exact
      rational input).  If it fails -> 'slot blocked by third square', stop.
  (3) RELAX: repeat -- for each of the remaining 9 squares search for a feasible
      rigid motion at fixed side (translations in 16 directions with step
      halving; rotations +/- about the centre and about contact points) that
      keeps the packing valid and INCREASES

          V = area of the largest connected free component of
              [0,m]^2 \ (all 10 squares) that meets the zone vacated by A,B

      (raster 1/400).  Apply the best improving move; stop when none improves.
  (4) FIT TEST: search the free region for a placement of ONE unit square at any
      tilt (centres on a 1/200 grid x tilt step 1 deg, then local refinement),
      and VERIFY any found placement exactly (rational coordinates, interval SAT
      gaps > 0 against all 10 squares and the container).  On failure record the
      largest inscribable square side found.

      The fit scan computes, for every grid centre p and tilt theta, the exact
      largest lambda such that the lambda-square at (p,theta) is interior-
      disjoint from all 10 squares and inside the container:

          lambda_j(p) = max over the 4 SAT axes n of
                        (|n.(p-c_j)| - r_j(n)) / r_S(n),
          Lambda(p) = min( 2*min(p_x,p_y,m-p_x,m-p_y)/(|cos|+|sin|),
                           min_j lambda_j(p) ).

      Success iff Lambda >= 1 somewhere; otherwise max Lambda is the shortfall.

Data
  (a) the 5 exact K0-BLOCKED packings:
      results/k0dir87.json  record_K0_BLOCKED_packing (s0115, 3.98548)
      results/k0dir87.polish.jsonl  4 stuck endpoints (exact_K0_BLOCKED true)
  (b) results/d2front87.jsonl anchored candidates -- SEE NOTE in the report:
      that file stores only per-node scalars (cap/s/side/d1/d2/n_block), no
      configuration vectors, so no extra samples can be drawn from it.
  (c) CANARY: Trump (A03 trump11_exact.json, exact), TL corner, intruders
      sq4 + sq6.  The exchange MUST FAIL.

One process, OMP_NUM_THREADS=1.  Writes only results/exchange87.* and
notes/exchange87.md.
Usage: python exchange87.py [all|canary|quick]
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import time
from decimal import Decimal, getcontext
from fractions import Fraction

import numpy as np
from scipy import ndimage
from mpmath import iv

getcontext().prec = 220
iv.dps = 40

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
os.makedirs(RESULTS, exist_ok=True)
os.makedirs(NOTES, exist_ok=True)

OUT_JS = os.path.join(RESULTS, 'exchange87.json')
OUT_JL = os.path.join(RESULTS, 'exchange87.jsonl')
OUT_MD = os.path.join(NOTES, 'exchange87.md')
LOG = os.path.join(RESULTS, 'exchange87.log')

CORNERS = ('BL', 'BR', 'TR', 'TL')
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TL': (1.0, -1.0), 'TR': (-1.0, -1.0)}
TOL_BLOCK = 1e-9            # a tangency is NOT a block (k0dir87 floor)
TOL_CONTACT = 1e-6

H_RAST = 1.0 / 400.0        # relaxation void raster
H_FIT = 1.0 / 200.0         # fit-test centre grid
MOVE_MARGIN = 1e-10         # a currently-slack row must stay >= this
SLACK = 1e-13               # float-noise tolerance on a contact row
MAX_ROUNDS = 12
DV_MIN = 1e-6               # minimum void-area gain to accept a move
RELAX_SECS = float(os.environ.get('EX87_RELAX_SECS', 240.0))
GLOBAL_BUDGET = float(os.environ.get('EX87_BUDGET', 2.55 * 3600.0))

T0 = time.time()
_fh = open(LOG, 'a')


def log(*a):
    m = ' '.join(str(v) for v in a)
    print(m, flush=True)
    _fh.write('[%7.1f] %s\n' % (time.time() - T0, m))
    _fh.flush()


def budget_left():
    return GLOBAL_BUDGET - (time.time() - T0)


# ============================================================ float geometry

def verts_f(cx, cy, th):
    ct, st = math.cos(th), math.sin(th)
    ux, uy = 0.5 * ct, 0.5 * st
    vx, vy = -0.5 * st, 0.5 * ct
    return ((cx + ux + vx, cy + uy + vy), (cx + ux - vx, cy + uy - vy),
            (cx - ux - vx, cy - uy - vy), (cx - ux + vx, cy - uy + vy))


def axes_f(th):
    ct, st = math.cos(th), math.sin(th)
    return ((ct, st), (-st, ct))


def pair_gap_f(a, b):
    """SAT gap of two unit squares a=(cx,cy,th): > 0 iff interior-disjoint."""
    dx, dy = a[0] - b[0], a[1] - b[1]
    best = -1e30
    for th, other in ((a[2], b[2]), (b[2], a[2])):
        ct, st = math.cos(th), math.sin(th)
        co, so = math.cos(other), math.sin(other)
        # projection radius of the other square onto axis n
        for nx, ny in ((ct, st), (-st, ct)):
            # r_self = 0.5 ; r_other = 0.5*(|n.e1|+|n.e2|)
            p1 = abs(nx * co + ny * so)
            p2 = abs(-nx * so + ny * co)
            g = abs(nx * dx + ny * dy) - 0.5 - 0.5 * (p1 + p2)
            if g > best:
                best = g
    return best


def clearance_f(sq, m):
    """min over the 4 vertices of min(qx, qy, m-qx, m-qy)."""
    c = 1e30
    for qx, qy in verts_f(*sq):
        c = min(c, qx, qy, m - qx, m - qy)
    return c


def depth_at_corner(sq, cn, m):
    """A90 depth: 1 - min over the square of max(p_x,p_y) in c's frame."""
    ox, oy = (0.0, 0.0) if cn == 'BL' else (m, 0.0) if cn == 'BR' else \
        (m, m) if cn == 'TR' else (0.0, m)
    sx, sy = FSGN[cn]
    W = [(sx * (qx - ox), sy * (qy - oy)) for qx, qy in verts_f(*sq)]
    cand = list(W)
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    fmin = min(max(p[0], p[1]) for p in cand)
    return max(0.0, 1.0 - fmin)


def slot_square(cn, m):
    """Exact axis-aligned unit square in corner cn's slot (Fractions)."""
    half = Fraction(1, 2)
    mx = m
    cx = half if cn in ('BL', 'TL') else mx - half
    cy = half if cn in ('BL', 'BR') else mx - half
    return (cx, cy, Fraction(0))


# ========================================================== interval geometry

def _f2iv(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def _ivmin(a, b):
    return iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def _ivmax(a, b):
    return iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def iv_pose(sq):
    cx, cy = _f2iv(sq[0]), _f2iv(sq[1])
    t = sq[2]
    if (isinstance(t, Fraction) and t == 0) or (not isinstance(t, Fraction)
                                                and t == 0):
        # exact axis-aligned square (the corner slot square): cos/sin are exact,
        # so do not let iv.cos(0) widen the rows to +/-1e-41 and turn an exactly
        # flush container row into an apparently negative clearance.
        return cx, cy, iv.mpf(1), iv.mpf(0)
    th = _f2iv(t)
    return cx, cy, iv.cos(th), iv.sin(th)


def iv_verts(P):
    cx, cy, c, s = P
    half = iv.mpf(1) / iv.mpf(2)
    out = []
    for hx, hy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        HX, HY = half * hx, half * hy
        out.append((cx + (c * HX - s * HY), cy + (s * HX + c * HY)))
    return out


def iv_pair_gap(sqa, sqb):
    """Interval enclosure of the SAT gap; .a > 0 certifies interior-disjoint."""
    Pa, Pb = iv_pose(sqa), iv_pose(sqb)
    Va, Vb = iv_verts(Pa), iv_verts(Pb)
    best = None
    for P in (Pa, Pb):
        c, s = P[2], P[3]
        for nhx, nhy in ((1, 0), (0, 1)):
            nx = c * nhx - s * nhy
            ny = s * nhx + c * nhy
            pa = [nx * qx + ny * qy for qx, qy in Va]
            pb = [nx * qx + ny * qy for qx, qy in Vb]
            lo_a = hi_a = pa[0]
            lo_b = hi_b = pb[0]
            for p in pa[1:]:
                lo_a, hi_a = _ivmin(lo_a, p), _ivmax(hi_a, p)
            for p in pb[1:]:
                lo_b, hi_b = _ivmin(lo_b, p), _ivmax(hi_b, p)
            g = _ivmax(lo_b - hi_a, lo_a - hi_b)
            best = g if best is None else _ivmax(best, g)
    return best


def iv_clearance(sq, m):
    M = _f2iv(m)
    lo = None
    for qx, qy in iv_verts(iv_pose(sq)):
        for v in (qx, qy, M - qx, M - qy):
            lo = v if lo is None else _ivmin(lo, v)
    return lo


def clearance_info(sq, m):
    """(lower bound, certified >= 0).  An EXACTLY axis-aligned square with
    rational centre has rational container rows, so they are evaluated in exact
    rational arithmetic -- routing them through iv.mpf(num)/iv.mpf(den) would
    round the two sides independently and report a spurious -1e-41 clearance for
    a square that is flush by construction (e.g. the corner slot square)."""
    if isinstance(sq[2], Fraction) and sq[2] == 0 and \
            isinstance(sq[0], Fraction) and isinstance(sq[1], Fraction) and \
            isinstance(m, Fraction):
        h = Fraction(1, 2)
        v = min(sq[0] - h, sq[1] - h, m - sq[0] - h, m - sq[1] - h)
        return float(v), bool(v >= 0)
    c = iv_clearance(sq, m)
    return float(c.a), bool(c.a >= 0)


def certify_config(sqs, m):
    """Interval certificate for a whole configuration."""
    gmin = None
    worst = None
    for i in range(len(sqs)):
        for j in range(i + 1, len(sqs)):
            g = iv_pair_gap(sqs[i], sqs[j])
            if gmin is None or g.a < gmin:
                gmin = float(g.a)
                worst = [i, j]
    cmin, cok = None, True
    for i, sq in enumerate(sqs):
        v, ok = clearance_info(sq, m)
        cok = cok and ok
        if cmin is None or v < cmin:
            cmin = v
    return {'min_pair_gap_lb': gmin, 'worst_pair': worst,
            'min_clearance_lb': cmin,
            'disjoint_certified': bool(gmin is not None and gmin > 0),
            'contained_certified': bool(cok)}


# ================================================================== raster

class Raster:
    """1/400 occupancy raster of [0,m]^2 with per-square add/remove."""

    def __init__(self, m, h=H_RAST):
        self.m = m
        self.h = h
        self.N = int(math.ceil(m / h))
        self.xs = (np.arange(self.N) + 0.5) * h
        self.cnt = np.zeros((self.N, self.N), dtype=np.int16)   # [iy, ix]
        self.inside = self.xs <= m                              # all True by ceil
        self.slabs = {}

    def _mask(self, sq):
        cx, cy, th = sq
        r = 0.5 * (abs(math.cos(th)) + abs(math.sin(th))) + self.h
        i0 = max(0, int((cx - r) / self.h))
        i1 = min(self.N, int((cx + r) / self.h) + 2)
        j0 = max(0, int((cy - r) / self.h))
        j1 = min(self.N, int((cy + r) / self.h) + 2)
        if i0 >= i1 or j0 >= j1:
            return None
        X = self.xs[i0:i1][None, :] - cx
        Y = self.xs[j0:j1][:, None] - cy
        ct, st = math.cos(th), math.sin(th)
        u = np.abs(X * ct + Y * st)
        v = np.abs(-X * st + Y * ct)
        msk = (u <= 0.5) & (v <= 0.5)
        return (j0, j1, i0, i1, msk)

    def add(self, sq, sign=1):
        r = self._mask(sq)
        if r is None:
            return None
        j0, j1, i0, i1, msk = r
        self.cnt[j0:j1, i0:i1] += (sign * msk).astype(np.int16)
        return r

    def sub_region(self, r):
        j0, j1, i0, i1, msk = r
        self.cnt[j0:j1, i0:i1] -= msk.astype(np.int16)

    def add_region(self, r):
        j0, j1, i0, i1, msk = r
        self.cnt[j0:j1, i0:i1] += msk.astype(np.int16)

    def cells_of(self, sq):
        r = self._mask(sq)
        out = np.zeros((self.N, self.N), dtype=bool)
        if r is not None:
            j0, j1, i0, i1, msk = r
            out[j0:j1, i0:i1] = msk
        return out

    def void(self, seed):
        """area of largest connected free component meeting `seed`."""
        free = self.cnt == 0
        lab, n = ndimage.label(free)
        if n == 0:
            return 0.0
        ids = np.unique(lab[seed & free])
        ids = ids[ids > 0]
        if ids.size == 0:
            return 0.0
        sz = np.bincount(lab.ravel(), minlength=n + 1)
        return float(sz[ids].max()) * self.h * self.h


# ================================================================ relaxation

def base_rows(sqs, k, m):
    """the constraint values square k currently realises (its own rows only)."""
    return {'cl': clearance_f(sqs[k], m),
            'g': {j: pair_gap_f(sqs[k], sqs[j])
                  for j in range(len(sqs)) if j != k}}


def config_valid(sqs, k, m, base):
    """Validity after moving square k, by NON-DEGRADATION: every row of k must
    end at least as large as min(its current value, MOVE_MARGIN), up to SLACK.

    A row that is currently slack must stay positive (>= MOVE_MARGIN, so the
    exact interval check can certify it); a row that is currently a CONTACT
    (flush wall, touching pair) may stay a contact but may not get worse.  A
    strict positive margin would freeze every wall-flush square, which is what
    an earlier version of this file wrongly did."""
    if clearance_f(sqs[k], m) < min(base['cl'], MOVE_MARGIN) - SLACK:
        return False
    for j, g0 in base['g'].items():
        if pair_gap_f(sqs[k], sqs[j]) < min(g0, MOVE_MARGIN) - SLACK:
            return False
    return True


def contact_pivots(sqs, k, m, maxp=2):
    """up to maxp contact points of square k (with squares or walls)."""
    piv = []
    A = sqs[k]
    VA = verts_f(*A)
    for j in range(len(sqs)):
        if j == k:
            continue
        if pair_gap_f(A, sqs[j]) < TOL_CONTACT:
            VB = verts_f(*sqs[j])
            best = None
            for p in VA:
                for q in VB:
                    d = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
                    if best is None or d < best[0]:
                        best = (d, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
            # also vertex-of-B to A's centre and vice versa
            piv.append(best[1])
    for p in VA:
        for v in (p[0], p[1], m - p[0], m - p[1]):
            if v < TOL_CONTACT:
                piv.append(p)
                break
    # dedupe
    out = []
    for p in piv:
        if not any(abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9 for q in out):
            out.append(p)
        if len(out) >= maxp:
            break
    return out


def max_feasible_step(sqs, k, m, apply_fn, t0, base, nhalv=13):
    t = t0
    orig = sqs[k]
    for _ in range(nhalv):
        sqs[k] = apply_fn(orig, t)
        if config_valid(sqs, k, m, base):
            sqs[k] = orig
            return t
        t *= 0.5
    sqs[k] = orig
    return 0.0


def relax(sqs, movable, m, seed, rast, deadline, probe=None):
    """greedy void-maximising relaxation.  sqs mutated in place."""
    V = rast.void(seed)
    V0 = V
    nmoves = 0
    moved = {}
    rounds = 0
    trace = []
    dirs = [(math.cos(2 * math.pi * i / 16), math.sin(2 * math.pi * i / 16))
            for i in range(16)]
    while rounds < MAX_ROUNDS and time.time() < deadline:
        rounds += 1
        best = None   # (V, k, pose)
        for k in movable:
            if time.time() >= deadline:
                break
            orig = sqs[k]
            base = base_rows(sqs, k, m)
            reg0 = rast._mask(orig)
            cands = []
            # translations
            for dx, dy in dirs:
                def ap(o, t, dx=dx, dy=dy):
                    return (o[0] + t * dx, o[1] + t * dy, o[2])
                t = max_feasible_step(sqs, k, m, ap, 0.5, base)
                if t > 1e-7:
                    cands.append(ap(orig, t))
                    if t > 4e-7:
                        cands.append(ap(orig, t / 3.0))
            # rotations about centre and contact points
            pivots = [(orig[0], orig[1])] + contact_pivots(sqs, k, m)
            for px, py in pivots:
                for sgn in (1.0, -1.0):
                    def ar(o, t, px=px, py=py, sgn=sgn):
                        a = sgn * t
                        ca, sa = math.cos(a), math.sin(a)
                        dx, dy = o[0] - px, o[1] - py
                        return (px + ca * dx - sa * dy, py + sa * dx + ca * dy,
                                o[2] + a)
                    t = max_feasible_step(sqs, k, m, ar, 0.25, base)
                    if t > 1e-7:
                        cands.append(ar(orig, t))
                        if t > 4e-7:
                            cands.append(ar(orig, t / 3.0))
            if not cands:
                continue
            rast.sub_region(reg0)
            for pose in cands:
                reg = rast.add(pose)
                if reg is None:
                    continue
                v = rast.void(seed)
                rast.sub_region(reg)
                if v > (best[0] if best else V) + DV_MIN:
                    best = (v, k, pose)
            rast.add_region(reg0)
        if best is None:
            break
        v, k, pose = best
        reg0 = rast._mask(sqs[k])
        rast.sub_region(reg0)
        sqs[k] = pose
        rast.add(pose)
        V = v
        nmoves += 1
        moved[k] = moved.get(k, 0) + 1
        ent = {'round': rounds, 'sq': int(k), 'V': v}
        if probe is not None:
            ent['lam_coarse'] = probe(sqs)
        trace.append(ent)
    return {'V0': V0, 'V': V, 'n_moves': nmoves, 'rounds': rounds,
            'moved_squares': {str(k): v for k, v in sorted(moved.items())},
            'trace': trace[:40],
            'timed_out': bool(time.time() >= deadline)}


# ================================================================== fit test

def fit_scan(sqs, m, tilts_deg, h=H_FIT, pre=None):
    """max over (p on the h-grid, theta in tilts) of the largest lambda that
    fits.  Returns (best_lambda, theta_rad, px, py)."""
    N = int(math.ceil(m / h))
    xs = (np.arange(N) + 0.5) * h
    if pre is None:
        pre = []
        for (cx, cy, th) in sqs:
            DX = xs[None, :] - cx
            DY = xs[:, None] - cy
            ct, st = math.cos(th), math.sin(th)
            A1 = np.abs(DX * ct + DY * st)
            A2 = np.abs(-DX * st + DY * ct)
            pre.append((DX, DY, A1, A2, th))
    # container factor
    dx_edge = np.minimum(xs, m - xs)
    CB = 2.0 * np.minimum(dx_edge[None, :], dx_edge[:, None])
    best = (-1e30, 0.0, 0.0, 0.0)
    for td in tilts_deg:
        th = math.radians(td)
        ct, st = math.cos(th), math.sin(th)
        w0 = abs(ct) + abs(st)
        L = CB / w0
        for (DX, DY, A1, A2, thj) in pre:
            d = th - thj
            w = abs(math.cos(d)) + abs(math.sin(d))
            lj = np.maximum((A1 - 0.5) / (0.5 * w), (A2 - 0.5) / (0.5 * w))
            B1 = np.abs(DX * ct + DY * st)
            B2 = np.abs(-DX * st + DY * ct)
            np.maximum(lj, 2.0 * B1 - w, out=lj)
            np.maximum(lj, 2.0 * B2 - w, out=lj)
            np.minimum(L, lj, out=L)
        k = int(np.argmax(L))
        v = float(L.flat[k])
        if v > best[0]:
            iy, ix = divmod(k, N)
            best = (v, th, float(xs[ix]), float(xs[iy]))
    return best, pre


def lam_at(sqs, m, px, py, th):
    """exact-formula lambda at a single (p, theta) -- float."""
    ct, st = math.cos(th), math.sin(th)
    w0 = abs(ct) + abs(st)
    L = 2.0 * min(px, py, m - px, m - py) / w0
    for (cx, cy, thj) in sqs:
        dx, dy = px - cx, py - cy
        cj, sj = math.cos(thj), math.sin(thj)
        d = th - thj
        w = abs(math.cos(d)) + abs(math.sin(d))
        a1 = abs(dx * cj + dy * sj)
        a2 = abs(-dx * sj + dy * cj)
        b1 = abs(dx * ct + dy * st)
        b2 = abs(-dx * st + dy * ct)
        lj = max((a1 - 0.5) / (0.5 * w), (a2 - 0.5) / (0.5 * w),
                 2.0 * b1 - w, 2.0 * b2 - w)
        if lj < L:
            L = lj
    return L


def fit_refine(sqs, m, seed):
    """local refinement of (lambda, theta, p) by nested grid search."""
    lam, th, px, py = seed
    step_p, step_t = H_FIT, math.radians(1.0)
    for _ in range(14):
        improved = False
        for dt in (-step_t, 0.0, step_t):
            for dx in (-step_p, 0.0, step_p):
                for dy in (-step_p, 0.0, step_p):
                    p2 = (px + dx, py + dy, th + dt)
                    v = lam_at(sqs, m, p2[0], p2[1], p2[2])
                    if v > lam + 1e-12:
                        lam, px, py, th = v, p2[0], p2[1], p2[2]
                        improved = True
        if not improved:
            step_p *= 0.35
            step_t *= 0.35
    return lam, th, px, py


def verify_placement(sqs, m, px, py, th):
    """exact verification: rational coords, interval SAT gaps > 0."""
    cand = (Fraction(px), Fraction(py), Fraction(th))
    gmin = None
    for sq in sqs:
        g = iv_pair_gap(cand, sq)
        gmin = float(g.a) if gmin is None else min(gmin, float(g.a))
    cl, cl_ok = clearance_info(cand, m)
    return {'cx': '%d/%d' % (cand[0].numerator, cand[0].denominator),
            'cy': '%d/%d' % (cand[1].numerator, cand[1].denominator),
            'theta': '%d/%d' % (cand[2].numerator, cand[2].denominator),
            'cx_f': px, 'cy_f': py, 'theta_f': th,
            'min_pair_gap_lb': gmin, 'clearance_lb': cl,
            'VERIFIED': bool(gmin is not None and gmin > 0 and cl_ok)}


# ================================================================== packings

def load_packings():
    out = []
    d = json.load(open(os.path.join(RESULTS, 'k0dir87.json')))
    rec = d['record_K0_BLOCKED_packing']
    z = [Fraction(int(a.split('/')[0]), int(a.split('/')[1])) for a in rec['z']]
    out.append({'name': 'record_%s' % rec['tag'], 'src': 'k0dir87.json',
                'sigma': rec['sigma_float'], 'z': z})
    rows = [json.loads(l) for l in
            open(os.path.join(RESULTS, 'k0dir87.polish.jsonl'))]
    for i, r in enumerate(rows):
        if not r.get('exact_K0_BLOCKED') or not r.get('z_polished'):
            continue
        z = [Fraction(int(a.split('/')[0]), int(a.split('/')[1]))
             for a in r['z_polished']]
        out.append({'name': 'polish%02d_%s' % (i, r['tag']),
                    'src': 'k0dir87.polish.jsonl#%d' % i,
                    'sigma': r['sigma_polished'], 'z': z})
    return out


def load_anchored():
    """Dataset (b): the ANCHORED candidates of d2front87.  NOTE -- these live in
    results/d2front87.json (own_side_anchored / per_cap_anchored .candidates),
    not in d2front87.jsonl, whose rows carry only scalars (cap/s/side/d1/d2/
    n_block).  They come with EXACT rational z and their own certificate
    (disjoint_certified, K0_BLOCKED_certified, n_block [2,2,2,2]), so no extra
    float feasibility screen is needed beyond re-verifying it here."""
    d = json.load(open(os.path.join(RESULTS, 'd2front87.json')))
    src_list = [('own_side_anchored', d['own_side_anchored'])]
    src_list += [('cap' + k, v) for k, v in sorted(d['per_cap_anchored'].items())]
    seen, order = set(), []
    for src, v in src_list:
        if not v.get('anchored_only'):
            continue
        for c in v.get('candidates', []):
            key = tuple(c['z'])
            if key in seen:
                continue
            seen.add(key)
            order.append((src, c))
    out = []
    for i, (src, c) in enumerate(order):
        z = [Fraction(int(a.split('/')[0]), int(a.split('/')[1])) for a in c['z']]
        out.append({'name': 'anchored%d_%s' % (i, c['tag']),
                    'src': 'd2front87.json:%s' % src,
                    'sigma': float(c['sigma_certified_upper']),
                    'K0_BLOCKED_certified': c.get('K0_BLOCKED_certified'),
                    'z': z})
    return out


def load_trump():
    p = os.path.join(ATT, 'A03-upper-reconstruct', 'trump11_exact.json')
    d = json.load(open(p))
    z = []
    for sq in d['squares']:
        for k in ('cx', 'cy', 'theta'):
            z.append(Fraction(Decimal(sq[k])))
    z.append(Fraction(Decimal(d['s'])))
    return {'name': 'TRUMP_canary', 'src': 'A03/trump11_exact.json',
            'sigma': float(Fraction(Decimal(d['s']))), 'z': z}


def z_to_sqs(z):
    return [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11)], z[33]


# =================================================================== driver

def run_case(pk, cn, sqsQ, m, mf, out_rows):
    t_case = time.time()
    sqs_f = [(float(a), float(b), float(c)) for a, b, c in sqsQ]
    dep = [depth_at_corner(s, cn, mf) for s in sqs_f]
    intr = sorted([i for i in range(11) if dep[i] > TOL_BLOCK],
                  key=lambda i: -dep[i])
    rec = {'packing': pk['name'], 'src': pk['src'], 'sigma': pk['sigma'],
           'corner': cn, 'n_intruders': len(intr),
           'intruders_by_depth': [int(i) for i in intr],
           'depths': [round(dep[i], 12) for i in intr],
           'more_than_two_intruders': bool(len(intr) > 2)}
    if len(intr) < 2:
        rec['status'] = 'fewer_than_two_intruders'
        out_rows.append(rec)
        log('  %-4s %s' % (cn, rec['status']))
        return rec
    A, B = intr[0], intr[1]
    rec['removed'] = [int(A), int(B)]
    rec['extra_intruders_left_in_place'] = [int(i) for i in intr[2:]]

    keep = [i for i in range(11) if i not in (A, B)]
    slot = slot_square(cn, m)
    # ---- step 2: slot placement, exact/interval SAT vs the remaining 9
    gmin = None
    blockers = []
    for i in keep:
        g = iv_pair_gap(slot, sqsQ[i])
        gv = float(g.a)
        gmin = gv if gmin is None else min(gmin, gv)
        if float(g.b) <= 0:
            blockers.append(int(i))
    rec['slot_min_gap_lb'] = gmin
    rec['slot_blockers'] = blockers
    if blockers:
        rec['status'] = 'slot_blocked_by_third_square'
        rec['slot_blocked'] = True
        out_rows.append(rec)
        log('  %-4s SLOT BLOCKED by %s (min gap lb %.3e)' % (cn, blockers, gmin))
        return rec
    rec['slot_blocked'] = False

    # ---- configuration of 10: the 9 kept + the slot square (index 9)
    sqs10 = [sqs_f[i] for i in keep] + [(float(slot[0]), float(slot[1]), 0.0)]
    sqsQ10 = [sqsQ[i] for i in keep] + [slot]
    exact10 = list(range(9))   # which entries are still exact rationals

    # ---- fit test BEFORE relaxation (full 1-deg scan)
    tilts = list(range(0, 90))
    sqs_pre = list(sqs10)
    b0, _ = fit_scan(sqs10, mf, tilts)
    lam0, th0, px0, py0 = fit_refine(sqs10, mf, b0)
    rec['fit_before_relax'] = {'lambda_max': lam0, 'theta_deg': math.degrees(th0),
                               'cx': px0, 'cy': py0}
    log('  %-4s slot ok (gap lb %.2e); pre-relax lambda_max = %.6f'
        % (cn, gmin, lam0))

    stages = [('before_relax', sqs_pre, (lam0, th0, px0, py0))]

    if lam0 >= 1.0:
        rec['relaxation'] = {'skipped': 'fit_already_succeeds_before_relax',
                             'n_moves': 0, 'rounds': 0, 'moved_squares': {}}
    else:
        # ---- step 3: relaxation (V = void area, per the brief), while also
        # tracking the trajectory point with the best COARSE fit, since a
        # bigger void is not the same thing as a bigger inscribable square.
        rast = Raster(mf)
        for s in sqs10:
            rast.add(s)
        seed = (rast.cells_of(sqs_f[A]) | rast.cells_of(sqs_f[B])) & \
            (~rast.cells_of(sqs10[9]))
        rec['vacated_cells'] = int(seed.sum())
        best_traj = {'lam': -1e30, 'sqs': None}

        def probe(cur):
            bb, _p = fit_scan(cur, mf, list(range(0, 90, 10)))
            if bb[0] > best_traj['lam']:
                best_traj['lam'] = bb[0]
                best_traj['sqs'] = list(cur)
            return bb[0]

        dl = time.time() + min(RELAX_SECS, max(20.0, budget_left() - 300.0))
        rl = relax(sqs10, list(range(9)), mf, seed, rast, dl, probe=probe)
        rec['relaxation'] = rl
        log('  %-4s relax: %d moves in %d rounds, V %.4f -> %.4f%s'
            % (cn, rl['n_moves'], rl['rounds'], rl['V0'], rl['V'],
               ' (TIMEOUT)' if rl['timed_out'] else ''))
        if rl['n_moves']:
            b1, _ = fit_scan(sqs10, mf, tilts)
            stages.append(('after_relax', list(sqs10),
                           fit_refine(sqs10, mf, b1)))
            bt = best_traj['sqs']
            if bt is not None and bt != sqs10:
                b2, _ = fit_scan(bt, mf, tilts)
                stages.append(('best_on_trajectory', bt, fit_refine(bt, mf, b2)))

    rec['stages'] = {nm: {'lambda_max': v[0], 'theta_deg': math.degrees(v[1]),
                          'cx': v[2], 'cy': v[3]} for nm, _s, v in stages}
    nm, sqsW, (lam, th, px, py) = max(stages, key=lambda t: t[2][0])
    rec['best_stage'] = nm
    rec['fit_after_relax'] = rec['stages'].get(
        'after_relax', rec['fit_before_relax'])
    rec['largest_inscribable_side'] = lam
    sqsQ_win = [sqsQ10[i] if sqsW[i] == sqs_pre[i] else
                (Fraction(sqsW[i][0]), Fraction(sqsW[i][1]),
                 Fraction(sqsW[i][2])) for i in range(10)]
    rec['config_cert'] = certify_config(sqsQ_win, m)
    if lam >= 1.0:
        ver = verify_placement(sqsQ_win, m, px, py, th)
        rec['placement'] = ver
        rec['fit_success'] = bool(ver['VERIFIED'])
        rec['status'] = 'EXCHANGE_SUCCESS' if ver['VERIFIED'] else \
            'fit_found_but_exact_verify_failed'
    else:
        rec['fit_success'] = False
        rec['status'] = 'fit_failed'
    rec['secs'] = time.time() - t_case
    out_rows.append(rec)
    log('  %-4s %s  lambda_max = %.6f  [%s]  (%.0fs)'
        % (cn, rec['status'], lam, nm, rec['secs']))
    return rec


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    suffix = ''
    if mode == 'anchored':
        packings = load_anchored()
        suffix = '.anchored'
    elif mode == 'canary':
        packings = [load_trump()]
    else:
        packings = load_packings() + [load_trump()]
    out_js = OUT_JS.replace('.json', suffix + '.json')
    out_jl = OUT_JL.replace('.jsonl', suffix + '.jsonl')

    rows = []
    summary = {'cases': [], 'n_success': 0}
    for pk in packings:
        sqsQ, m = z_to_sqs(pk['z'])
        mf = float(m)
        sqs_f = [(float(a), float(b), float(c)) for a, b, c in sqsQ]
        cert = certify_config(sqsQ, m)
        log('%s  m=%.12f  cert %s' % (pk['name'], mf, cert))
        pk['input_cert'] = cert
        corners = ('TL',) if pk['name'].startswith('TRUMP') else CORNERS
        for cn in corners:
            if budget_left() < 120:
                log('BUDGET EXHAUSTED before %s/%s' % (pk['name'], cn))
                break
            run_case(pk, cn, sqsQ, m, mf, rows)
    for r in rows:
        if r.get('fit_success'):
            summary['n_success'] += 1
    summary['n_cases'] = len(rows)
    summary['cases'] = [dict({k: r.get(k) for k in
                              ('packing', 'corner', 'sigma', 'status',
                               'slot_blocked', 'removed', 'best_stage',
                               'largest_inscribable_side', 'fit_success')},
                             n_moves=(r.get('relaxation') or {}).get('n_moves'),
                             moved=(r.get('relaxation') or {}).get(
                                 'moved_squares'))
                        for r in rows]
    tr = [r for r in rows if r['packing'].startswith('TRUMP')]
    summary['canary'] = tr[0] if tr else None
    summary['canary_OK'] = bool(tr and not tr[0].get('fit_success'))
    summary['secs'] = time.time() - T0
    with open(out_jl, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    with open(out_js, 'w') as f:
        json.dump(summary, f, indent=1)
    log('DONE: %d/%d (packing,corner) exchanges succeed; canary_OK=%s; %.0fs'
        % (summary['n_success'], summary['n_cases'], summary['canary_OK'],
           summary['secs']))


if __name__ == '__main__':
    main()
