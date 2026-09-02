"""
crowdfam.py -- maximum-incidence disjoint-family search ("crowd-saturated pseudo-packings")
============================================================================================

A65-low-k-closure / H10.  For each Young class listed in
``attempts/A65-low-k-closure/results/h10_boxspec.json`` we look for

    N = 11 - k   pairwise interior-disjoint unit squares (free centre + free tilt)
    inside the container [0,s0]^2, s0 = 969271/250000 = 3.877084,
    each also interior-disjoint from the k axis-aligned unit "pin" squares,

maximising the incidence count

    I = sum over family squares q of #{ listed boxes B : int(B) cap int(q) != empty }.

The decisive threshold is I >= R (R is given per class in the spec).

Geometry conventions match ``code/squares.py``: a square is (cx, cy, theta), its
corners are c + R(theta) * (+-1/2, +-1/2).  A "box" is the CLOSED axis-aligned unit
square centred at its slot.  Touching is allowed everywhere (interior-disjointness),
so all disjointness tests are ``separation >= 0`` on some separating axis (SAT).

Search
------
Note (important, and the reason the search is cheap):  N + k = 11 always, so a
feasible family is exactly an 11-square packing of [0,s0]^2 that contains the k pins.
s0 is the record packing side; the A03/A04 local-optimum catalogues (702 distinct
local optima) contain exactly ONE optimum with s <= s0, namely Trump's packing at
s = 3.8770835900228136.  The feasible set at s0 is therefore a ~4.1e-7 shell around
Trump's configuration (and its 8 container symmetries).  The search accordingly has
two engines:

  (A) SEEDED.  Take Trump's packing, scale all centres by lambda = s0/s_trump (this
      turns every contact of the rigid packing into a gap of ~(lambda-1)/2 ~ 5.3e-8
      and keeps unit squares), apply each of the 8 container symmetries, test whether
      the k pin slots are covered by upright squares of the image, snap those pins to
      their exact rational slots, and polish the remaining N squares by a max-min-
      margin least-squares "inflation".  Incidence is then read off.

  (B) BLIND.  Multistart penalty minimisation over (cx,cy,theta) of the N free
      squares, energy = overlap penalty - soft incidence reward, L-BFGS-B with
      numerical gradients, random and box-seeded starts.  This is the honest search
      that would find a non-Trump family if one existed.  Time-boxed per class.

For the corners4 class (k4_13) engine (A) has no seed at all (no symmetry image of
Trump has four axis-aligned corner squares), so we additionally run a
"minimum container side" study: minimise s subject to the four corner pins at
(1/2,1/2), (1/2,s-1/2), (s-1/2,1/2), (s-1/2,s-1/2) plus 7 free unit squares.  The best
s found quantifies how far the class is from being realisable at s0.

Exact verification
------------------
The best family per class is re-verified with ``fractions.Fraction``:
  * theta is represented by t = tan(theta/2) rounded to a rational with denominator D,
    so cos = (1-t^2)/(1+t^2) and sin = 2t/(1+t^2) are exact rationals;
  * (cx,cy) are rounded to rationals with denominator D;
  * (1) every family corner lies in [0,s0] x [0,s0]        -- exact;
  * (2) family-family and family-pin interior-disjointness -- exact SAT, some axis
        with separation >= 0;
  * (3) every claimed incidence carries an exact rational witness point p, checked to
        be strictly inside the open box AND to have both body-frame coordinates
        strictly inside (-1/2, 1/2).
Only exactly-verified incidences are counted in ``best_I_exact``.

D is escalated over 10^6, 10^8, 10^10, 10^12, 10^14 and the first D that verifies is
reported.  D = 10^6 (the nominal request) CANNOT work for any class here: the whole
feasible set is a 4.1e-7-thick shell around a rigid packing, while snapping to the
10^-6 grid displaces corners by up to ~7e-7.  This is a property of the problem, not
of the code, and is recorded in the log and in the JSON (`denominator` field).

Usage
-----
    python crowdfam.py                    # all 9 requested classes
    python crowdfam.py --classes k4_13 k4_08
    python crowdfam.py --blind-budget 40  # seconds of blind search per class
Outputs (all inside attempts/A65-low-k-closure/):
    results/crowdfam.json, logs/crowdfam.log

Single process, BLAS pinned to one thread (set at import time, before numpy loads).
"""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import argparse
import itertools
import json
import math
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import least_squares, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A65 = os.path.abspath(os.path.join(HERE, ".."))
SPEC = os.path.join(A65, "results", "h10_boxspec.json")
TRUMP = os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")
OUT_JSON = os.path.join(A65, "results", "crowdfam.json")
OUT_LOG = os.path.join(A65, "logs", "crowdfam.log")

TARGET_CLASSES = ["k4_13", "k4_08", "k4_11", "k4_03",
                  "k3_05", "k3_02", "k2_01", "k1_00", "k0_00"]

_HALF = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])

_LOG = []


def log(msg):
    line = "%8.1fs  %s" % (time.time() - _T0, msg)
    _LOG.append(line)
    print(line, flush=True)


# --------------------------------------------------------------------------- #
# float geometry                                                              #
# --------------------------------------------------------------------------- #
def corners(X):
    """X (n,3) -> (n,4,2) corner coordinates."""
    X = np.asarray(X, dtype=float).reshape(-1, 3)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    R = np.empty((len(X), 2, 2))
    R[:, 0, 0], R[:, 0, 1], R[:, 1, 0], R[:, 1, 1] = c, -s, s, c
    return X[:, None, :2] + np.einsum("kj,nij->nki", _HALF, R)


def normals(X):
    """X (n,3) -> (n,2,2) the two unit edge normals per square."""
    X = np.asarray(X, dtype=float).reshape(-1, 3)
    c, s = np.cos(X[:, 2]), np.sin(X[:, 2])
    return np.stack([np.stack([c, s], -1), np.stack([-s, c], -1)], 1)


def sat_gap_sets(Ci, Ni, Cj, Nj):
    """Signed SAT separation between two convex quads, > 0 disjoint, < 0 penetration."""
    best = -np.inf
    for ax in np.vstack([Ni, Nj]):
        pa, pb = Ci @ ax, Cj @ ax
        g = max(pb.min() - pa.max(), pa.min() - pb.max())
        if g > best:
            best = g
    return best


def _pairgap(Ca, Na, Cb, Nb):
    """Vectorised SAT separation for m quad pairs: (m,4,2)/(m,2,2) arrays -> (m,)."""
    AX = np.concatenate([Na, Nb], axis=1)                     # (m,4,2)
    pa = np.einsum("mkd,mad->mak", Ca, AX)                    # (m,4ax,4corners)
    pb = np.einsum("mkd,mad->mak", Cb, AX)
    return np.maximum(pb.min(2) - pa.max(2), pa.min(2) - pb.max(2)).max(1)


def gaps(Xf, Cp, Np_, s0):
    """Constraint vector for the free family Xf (n,3) against walls, itself and pins.

    Every entry must be >= 0 for a legal family.  Cp/Np_ are the pin corner/normal
    arrays (may be empty)."""
    Cf, Nf = corners(Xf), normals(Xf)
    n = len(Cf)
    parts = [np.concatenate([Cf[:, :, 0].min(1), Cf[:, :, 1].min(1),
                             s0 - Cf[:, :, 0].max(1), s0 - Cf[:, :, 1].max(1)])]
    if n >= 2:
        I, J = np.triu_indices(n, 1)
        parts.append(_pairgap(Cf[I], Nf[I], Cf[J], Nf[J]))
    if len(Cp):
        I = np.repeat(np.arange(n), len(Cp))
        J = np.tile(np.arange(len(Cp)), n)
        parts.append(_pairgap(Cf[I], Nf[I], Cp[J], Np_[J]))
    return np.concatenate(parts)


def box_overlaps(Xf, boxes):
    """(n, nb) min-over-axes projection overlap of each family square with each box.
    > 0 iff the open interiors meet."""
    Cf, Nf = corners(Xf), normals(Xf)
    n, nb = len(Cf), len(boxes)
    BC = np.array([[[x0, y0], [x1, y0], [x1, y1], [x0, y1]] for (x0, y0, x1, y1) in boxes])
    BN = np.tile(np.array([[[1.0, 0.0], [0.0, 1.0]]]), (nb, 1, 1))
    I = np.repeat(np.arange(n), nb)
    J = np.tile(np.arange(nb), n)
    AX = np.concatenate([Nf[I], BN[J]], axis=1)
    pa = np.einsum("mkd,mad->mak", Cf[I], AX)
    pb = np.einsum("mkd,mad->mak", BC[J], AX)
    ov = np.minimum(pa.max(2), pb.max(2)) - np.maximum(pa.min(2), pb.min(2))
    return ov.min(1).reshape(n, nb)


def incidence_count(Xf, boxes, tol):
    ov = box_overlaps(Xf, boxes)
    return int(np.sum(ov > tol)), ov


# --------------------------------------------------------------------------- #
# engine A -- Trump seeds                                                     #
# --------------------------------------------------------------------------- #
def trump_scaled(s0):
    T = json.load(open(TRUMP))
    X = np.array(T["X"], dtype=float)
    st = float(T["s"])
    lam = s0 / st
    Y = X.copy()
    Y[:, :2] *= lam           # unit squares, centres blown up: every contact opens
    return Y, st, lam


def symmetry(Y, k, s):
    """The 8 container symmetries; k bit0 = x-flip, bit1 = y-flip, bit2 = transpose."""
    x, y, th = Y[:, 0].copy(), Y[:, 1].copy(), Y[:, 2].copy()
    if k & 1:
        x, th = s - x, -th
    if k & 2:
        y, th = s - y, -th
    if k & 4:
        x, y, th = y.copy(), x.copy(), math.pi / 2 - th
    return np.stack([x, y, np.mod(th, math.pi / 2)], 1)


def polish(Xf, Cp, Np_, s0, m, maxiter=200):
    """Push the free squares until every constraint gap is >= m (max-min inflation)."""
    def res(v):
        return np.maximum(0.0, m - gaps(v.reshape(-1, 3), Cp, Np_, s0))
    r = least_squares(res, Xf.ravel(), method="trf", diff_step=1e-9,
                      xtol=3e-16, ftol=3e-16, gtol=3e-16, max_nfev=maxiter)
    return r.x.reshape(-1, 3)


def inflate(Xf, Cp, Np_, s0, ladder=(1.2e-7, 8e-8, 5e-8, 3e-8, 1.5e-8, 6e-9, 2e-9)):
    """Try successively smaller target margins; return (config, achieved margin)."""
    best, bestm = Xf, gaps(Xf, Cp, Np_, s0).min()
    for m in ladder:
        Y = polish(Xf, Cp, Np_, s0, m)
        gm = gaps(Y, Cp, Np_, s0).min()
        if gm > bestm:
            best, bestm = Y, gm
        if bestm >= 0.9 * m:
            break
    return best, bestm


# --------------------------------------------------------------------------- #
# engine B -- blind multistart penalty search                                 #
# --------------------------------------------------------------------------- #
def blind_search(N, Cp, Np_, s0, boxes, budget, rng, log_prefix=""):
    """Multistart L-BFGS-B on  energy = 1e4*sum(min(g,0)^2) - soft incidence.
    Returns (best feasible config or None, best_I, best_min_gap_seen)."""
    nb = len(boxes)
    W = 1.0e4

    def energy(v):
        Y = v.reshape(-1, 3)
        g = gaps(Y, Cp, Np_, s0)
        viol = float(np.sum(np.minimum(g, 0.0) ** 2))
        ov = box_overlaps(Y, boxes)
        inc = float(np.sum(np.clip(ov, 0.0, 0.02))) / 0.02
        return W * viol - 0.02 * inc

    best_cfg, best_I, best_gap = None, -1, -np.inf
    t_end = time.time() + budget
    starts = 0
    while time.time() < t_end:
        starts += 1
        # seed: 2 squares poking each box (greedy), spares random
        seeds = []
        for b in range(nb):
            x0, y0, x1, y1 = boxes[b]
            for _ in range(2):
                seeds.append([0.5 * (x0 + x1) + rng.uniform(-.4, .4),
                              0.5 * (y0 + y1) + rng.uniform(-.4, .4),
                              rng.uniform(0, math.pi / 2)])
        while len(seeds) < N:
            seeds.append([rng.uniform(.5, s0 - .5), rng.uniform(.5, s0 - .5),
                          rng.uniform(0, math.pi / 2)])
        rng.shuffle(seeds)
        v0 = np.array(seeds[:N], dtype=float).ravel()
        r = minimize(energy, v0, method="L-BFGS-B",
                     options=dict(maxiter=300, maxfun=5000))
        Y = r.x.reshape(-1, 3)
        Y = polish(Y, Cp, Np_, s0, 0.0, maxiter=80)   # feasibility repair
        gm = gaps(Y, Cp, Np_, s0).min()
        if gm > best_gap:
            best_gap = gm
        if gm >= 0.0:
            I, _ = incidence_count(Y, boxes, 1e-6)
            if I > best_I:
                best_I, best_cfg = I, Y.copy()
    log("%sblind: %d starts, best min-gap %.3e, best feasible I=%s"
        % (log_prefix, starts, best_gap, best_I if best_I >= 0 else "none"))
    return best_cfg, best_I, best_gap


_CATALOGUE = None


def catalogue_scan(cl, s0):
    """Smallest container side among the 702 catalogued distinct local optima
    (A04-upper-search) that realises this class's pin pattern (any of the 8 container
    symmetries).  Slot coordinates are re-based: 1/2, 3/2, 5/2 stay put, s0-1/2 and
    s0-3/2 follow the optimum's own side.  A large value (or None) says how much
    container excess the pin pattern costs among all known rigid 11-packings."""
    global _CATALOGUE
    if _CATALOGUE is None:
        path = os.path.join(ROOT, "attempts", "A04-upper-search", "local_optima.json")
        opts = json.load(open(path))["optima"]
        _CATALOGUE = sorted(
            [(o["s"], np.column_stack([np.array(o["centres"]), np.array(o["thetas_rad"])]))
             for o in opts], key=lambda z: z[0])

    def slotval(v, s):
        v = float(Fr(v))
        if abs(v - (s0 - 0.5)) < 1e-9:
            return s - 0.5
        if abs(v - (s0 - 1.5)) < 1e-9:
            return s - 1.5
        return v

    for s, X in _CATALOGUE:
        pins = [(slotval(p[0], s), slotval(p[1], s)) for p in cl["pins"]]
        for k in range(8):
            Z = symmetry(X, k, s)
            up = [i for i in range(11) if min(Z[i, 2], math.pi / 2 - Z[i, 2]) < 1e-7]
            used, ok = set(), True
            for (px, py) in pins:
                m = [i for i in up if abs(Z[i, 0] - px) < 1e-6
                     and abs(Z[i, 1] - py) < 1e-6 and i not in used]
                if not m:
                    ok = False
                    break
                used.add(m[0])
            if ok:
                return s
    return None


def _c4_pins(s):
    P = np.array([[.5, .5, 0.], [.5, s - .5, 0.], [s - .5, .5, 0.], [s - .5, s - .5, 0.]])
    return corners(P), normals(P)


def corners4_side_study(budget, rng):
    """Minimise the container side s for {4 corner pins} + 7 free unit squares.

    Shrink-and-repair basin hopping: hold a feasible (X,s), try s - step, repair the
    7 free squares by max-min inflation, accept if feasible, otherwise perturb."""
    N = 7
    # structured + random seeds at a comfortably feasible side
    s = 4.10
    seeds = []
    grid = [(1.5, .5), (2.5, .5), (1.5, 1.5), (2.5, 1.5), (1.5, 2.5), (2.5, 2.5), (.5, 1.5)]
    seeds.append(np.array([[gx, gy, 0.0] for gx, gy in grid]))
    seeds.append(np.array([[gx, gy, 0.0] for gx, gy in
                           [(1.5, .5), (2.5, .5), (.5, 1.5), (3.6, 1.5),
                            (1.5, 1.6), (2.5, 1.6), (2.05, 2.7)]]))
    X = None
    for S in seeds:
        Y = polish(S, *_c4_pins(s), s, 1e-3, maxiter=300)
        if gaps(Y, *_c4_pins(s), s).min() >= 0:
            X = Y
            break
    if X is None:
        log("corners4 side study: no feasible seed at s = %.3f" % s)
        return (np.inf, None)
    best_s, best_X = s, X.copy()
    step, t_end, tries = 0.02, time.time() + budget, 0
    while time.time() < t_end:
        tries += 1
        s_try = best_s - step
        Y = best_X + np.concatenate(
            [rng.normal(0, 0.02, (N, 2)), rng.normal(0, 0.05, (N, 1))], 1) \
            if tries % 3 == 0 else best_X.copy()
        Y = polish(Y, *_c4_pins(s_try), s_try, 5e-9, maxiter=250)
        if gaps(Y, *_c4_pins(s_try), s_try).min() >= 0:
            best_s, best_X = s_try, Y.copy()
            step = min(step * 1.3, 0.05)
        else:
            step *= 0.7
            if step < 1e-6:
                step = 0.01 * rng.random()
    log("corners4 side study: %d shrink steps, best feasible side s = %.7f "
        "(s0 = %.6f, excess = %.5f)" % (tries, best_s, S0F, best_s - S0F))
    return (best_s, best_X)


# --------------------------------------------------------------------------- #
# exact verification (Fractions)                                              #
# --------------------------------------------------------------------------- #
def exact_corners(cx, cy, t):
    """Exact rational corners of the unit square (cx,cy) with tan(theta/2) = t."""
    d = 1 + t * t
    co, si = (1 - t * t) / d, (2 * t) / d
    h = Fr(1, 2)
    out = []
    for ux, uy in ((-h, -h), (h, -h), (h, h), (-h, h)):
        out.append((cx + co * ux - si * uy, cy + si * ux + co * uy))
    return out, co, si


def exact_sat_disjoint(Ca, axa, Cb, axb):
    """True iff some axis separates: max over axes of gap >= 0 (touching allowed)."""
    for ax in list(axa) + list(axb):
        pa = [ax[0] * p[0] + ax[1] * p[1] for p in Ca]
        pb = [ax[0] * p[0] + ax[1] * p[1] for p in Cb]
        if min(pb) - max(pa) >= 0 or min(pa) - max(pb) >= 0:
            return True
    return False


def exact_verify(fam, pins, boxes_fr, s0, witnesses):
    """fam: list of (cx,cy,t) Fractions; pins: list of (px,py) Fractions (upright unit
    squares); boxes_fr: list of (x0,y0,x1,y1) Fractions; witnesses: {(q,b): (wx,wy)}.
    Returns (ok_geometry, verified_incidences, notes)."""
    notes = []
    C, AX = [], []
    for (cx, cy, t) in fam:
        cs, co, si = exact_corners(cx, cy, t)
        C.append(cs)
        AX.append([(co, si), (-si, co)])
    # (1) containment
    for i, cs in enumerate(C):
        for (x, y) in cs:
            if not (0 <= x <= s0 and 0 <= y <= s0):
                notes.append("square %d outside container" % i)
    # pins
    h = Fr(1, 2)
    PC, PAX = [], []
    for (px, py) in pins:
        PC.append([(px - h, py - h), (px + h, py - h), (px + h, py + h), (px - h, py + h)])
        PAX.append([(Fr(1), Fr(0)), (Fr(0), Fr(1))])
    # (2) disjointness
    for i, j in itertools.combinations(range(len(C)), 2):
        if not exact_sat_disjoint(C[i], AX[i], C[j], AX[j]):
            notes.append("family %d-%d overlap" % (i, j))
    for i in range(len(C)):
        for j in range(len(PC)):
            if not exact_sat_disjoint(C[i], AX[i], PC[j], PAX[j]):
                notes.append("family %d - pin %d overlap" % (i, j))
    # (3) incidence witnesses
    good = []
    for (q, b), (wx, wy) in sorted(witnesses.items()):
        x0, y0, x1, y1 = boxes_fr[b]
        if not (x0 < wx < x1 and y0 < wy < y1):
            notes.append("witness (%d,%d) not strictly inside box" % (q, b))
            continue
        cx, cy, t = fam[q]
        (co, si) = AX[q][0]
        dx, dy = wx - cx, wy - cy
        u = co * dx + si * dy
        v = -si * dx + co * dy
        if -h < u < h and -h < v < h:
            good.append([q, b, [str(wx), str(wy)]])
        else:
            notes.append("witness (%d,%d) not strictly inside square" % (q, b))
    return (len(notes) == 0 or all(n.startswith("witness") for n in notes)), good, notes


def to_rational(Xf, D):
    """Round a float family to (cx,cy,t) rationals with denominator D."""
    out = []
    for (cx, cy, th) in Xf:
        t = math.tan(th / 2.0)
        out.append((Fr(round(cx * D), D), Fr(round(cy * D), D), Fr(round(t * D), D)))
    return out


def witness_points(Xf, boxes, ov, tol, Dw=10 ** 6):
    """Rational witness points, one per positive overlap: centroid of the clipped
    intersection polygon, snapped to the 1/Dw grid."""
    W = {}
    Cf = corners(Xf)
    for i in range(len(Xf)):
        for b, (x0, y0, x1, y1) in enumerate(boxes):
            if ov[i, b] <= tol:
                continue
            poly = [tuple(p) for p in Cf[i]]
            for (nx, ny, c) in ((1, 0, x0), (-1, 0, -x1), (0, 1, y0), (0, -1, -y1)):
                new = []
                for k in range(len(poly)):
                    p, q = poly[k], poly[(k + 1) % len(poly)]
                    dp = nx * p[0] + ny * p[1] - c
                    dq = nx * q[0] + ny * q[1] - c
                    if dp >= 0:
                        new.append(p)
                    if (dp > 0) != (dq > 0):
                        a = dp / (dp - dq)
                        new.append((p[0] + a * (q[0] - p[0]), p[1] + a * (q[1] - p[1])))
                poly = new
                if not poly:
                    break
            if not poly:
                continue
            gx = sum(p[0] for p in poly) / len(poly)
            gy = sum(p[1] for p in poly) / len(poly)
            W[(i, b)] = (Fr(round(gx * Dw), Dw), Fr(round(gy * Dw), Dw))
    return W


# --------------------------------------------------------------------------- #
# per-class driver                                                            #
# --------------------------------------------------------------------------- #
def run_class(name, cl, s0_fr, blind_budget, rng):
    s0 = float(s0_fr)
    k, N, R = cl["k"], cl["N"], cl["R"]
    pins_fr = [(Fr(p[0]), Fr(p[1])) for p in cl["pins"]]
    pins_f = np.array([[float(a), float(b), 0.0] for (a, b) in pins_fr]).reshape(-1, 3)
    Cp = corners(pins_f) if len(pins_f) else np.zeros((0, 4, 2))
    Np_ = normals(pins_f) if len(pins_f) else np.zeros((0, 2, 2))
    boxes, boxes_fr = [], []
    for bx in cl["boxes"]:
        sx, sy = Fr(bx["slot"][0]), Fr(bx["slot"][1])
        boxes_fr.append((sx - Fr(1, 2), sy - Fr(1, 2), sx + Fr(1, 2), sy + Fr(1, 2)))
        boxes.append(tuple(float(z) for z in boxes_fr[-1]))
    log("=== %s : k=%d N=%d R=%d  (%d boxes)" % (name, k, N, R, len(boxes)))
    cmin = catalogue_scan(cl, s0)
    log("  catalogue: smallest rigid 11-packing realising the pin pattern: %s"
        % ("s = %.10f (excess over s0 = %+.3e)" % (cmin, cmin - s0) if cmin
           else "NONE of the 702 known local optima"))

    # ---- engine A: Trump seeds ------------------------------------------- #
    Y0, st, lam = trump_scaled(s0)
    cands = []
    for sk in range(8):
        Z = symmetry(Y0, sk, s0)
        up = [i for i in range(11) if min(Z[i, 2], math.pi / 2 - Z[i, 2]) < 1e-9]
        used, ok = [], True
        for (px, py) in pins_fr:
            m = [i for i in up if abs(Z[i, 0] - float(px)) < 1e-5
                 and abs(Z[i, 1] - float(py)) < 1e-5 and i not in used]
            if not m:
                ok = False
                break
            used.append(m[0])
        if not ok:
            continue
        fam = [i for i in range(11) if i not in used]
        Xf = Z[fam].copy()
        Xf, gm = inflate(Xf, Cp, Np_, s0)
        if gm < 0:
            log("  sym %d: seed infeasible after inflation (min gap %.2e)" % (sk, gm))
            continue
        I, ov = incidence_count(Xf, boxes, 1e-6)
        log("  sym %d: feasible, min gap %.3e, I = %d" % (sk, gm, I))
        cands.append((I, gm, Xf, ov, sk))
    if not cands:
        log("  no Trump embedding for %s (pin pattern not realised by any symmetry)" % name)

    # ---- engine B: blind multistart --------------------------------------- #
    bcfg, bI, bgap = blind_search(N, Cp, Np_, s0, boxes, blind_budget, rng, "  ")
    if bcfg is not None:
        cands.append((bI, bgap, bcfg, box_overlaps(bcfg, boxes), -1))

    if not cands:
        log("  %s: NO FEASIBLE FAMILY FOUND -> I = 0" % name)
        return dict(N=N, R=R, k=k, best_I_float=0, best_I_exact=0, family=[],
                    incidence_list=[], verified=False, denominator=None,
                    source="none", min_gap=None, catalogue_min_side=cmin,
                    note="no feasible family of %d squares found (engine A: no Trump "
                         "embedding of the pin pattern; engine B: blind multistart "
                         "found no feasible configuration, best min-gap %.3e)" % (N, bgap))

    cands.sort(key=lambda c: (-c[0], -c[1]))
    I, gm, Xf, ov, sk = cands[0]
    src = "trump-sym%d" % sk if sk >= 0 else "blind"
    log("  best float: I = %d (%s), min gap %.3e" % (I, src, gm))

    # ---- exact verification ----------------------------------------------- #
    W = witness_points(Xf, boxes, ov, 1e-6)
    verified, good, Dused, notes = False, [], None, []
    for D in (10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12, 10 ** 14):
        fam = to_rational(Xf, D)
        ok, good_D, notes = exact_verify(fam, pins_fr, boxes_fr, s0_fr, W)
        geom_ok = not any(not n.startswith("witness") for n in notes)
        if geom_ok:
            verified, good, Dused = True, good_D, D
            log("  exact: D = 1e%d OK -- %d/%d incidences verified"
                % (int(round(math.log10(D))), len(good_D), I))
            break
        log("  exact: D = 1e%d FAILS (%d geometric violations)"
            % (int(round(math.log10(D))), sum(1 for n in notes if not n.startswith('witness'))))
    fam = to_rational(Xf, Dused if Dused else 10 ** 14)
    cover = [sum(1 for g in good if g[1] == b) for b in range(len(boxes))]
    tags = ["%s%s" % (bx["corner"], tuple(bx["cell"])) for bx in cl["boxes"]]
    log("  box coverage (target 2 each): %s"
        % ", ".join("%s=%d" % (t, c) for t, c in zip(tags, cover)))
    log("  deficient boxes: %s"
        % ([t for t, c in zip(tags, cover) if c < 2] or "none"))
    return dict(N=N, R=R, k=k, best_I_float=I, best_I_exact=len(good),
                box_tags=tags, box_coverage=cover,
                deficient_boxes=[t for t, c in zip(tags, cover) if c < 2],
                family=[dict(cx=str(a), cy=str(b), t=str(c)) for (a, b, c) in fam],
                incidence_list=good, verified=bool(verified and len(good) == I),
                catalogue_min_side=cmin,
                denominator=Dused, source=src, min_gap=float(gm),
                note="" if verified else "; ".join(notes[:6]))


def main():
    global _T0, S0F
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="*", default=TARGET_CLASSES)
    ap.add_argument("--blind-budget", type=float, default=40.0)
    ap.add_argument("--corners4-budget", type=float, default=240.0)
    ap.add_argument("--seed", type=int, default=20260901)
    args = ap.parse_args()

    _T0 = time.time()
    spec = json.load(open(SPEC))
    s0 = Fr(spec["s0"])
    S0F = float(s0)
    rng = np.random.default_rng(args.seed)
    log("crowdfam: s0 = %s = %.6f, classes = %s" % (spec["s0"], S0F, args.classes))
    Y0, st, lam = trump_scaled(S0F)
    log("Trump seed: s_trump = %.16f, slack s0 - s_trump = %.4e, lambda = %.12f"
        % (st, S0F - st, lam))

    res = {}
    for name in args.classes:
        res[name] = run_class(name, spec["classes"][name], s0, args.blind_budget, rng)
        r = res[name]
        log("  --> %s: I_exact = %d vs R = %d (%s)"
            % (name, r["best_I_exact"], r["R"],
               "SATURATED" if r["best_I_exact"] >= r["R"]
               else "SHORT by %d" % (r["R"] - r["best_I_exact"])))

    if "k4_13" in args.classes and args.corners4_budget > 0:
        log("--- corners4 (k4_13) minimum-side study ---")
        s_best, Yb = corners4_side_study(args.corners4_budget, rng)
        res["k4_13"]["corners4_min_side_found"] = None if Yb is None else float(s_best)

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    os.makedirs(os.path.dirname(OUT_LOG), exist_ok=True)
    json.dump(dict(s0=spec["s0"], generated_by="crowdfam.py", classes=res),
              open(OUT_JSON, "w"), indent=1)
    open(OUT_LOG, "w").write("\n".join(_LOG) + "\n")
    print("\nwrote %s\nwrote %s" % (OUT_JSON, OUT_LOG))


_T0 = time.time()
S0F = 3.877084
if __name__ == "__main__":
    main()
