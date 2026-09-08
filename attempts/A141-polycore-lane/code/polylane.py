"""A141 -- the LANE test with POLYGON cores: K' in place of A96's axis-aligned K(a).

A118's leaf is unchanged in logic:

    LANE_K'(C) := max # of pairwise interior-disjoint unit squares, none of them a conditioned
                  square of the node, whose poses lie in R'(C);
    M(C)       := # of the node's conditioned squares that CAN meet int C;
    LANE_K'(C) + M(C) <= 1   ==>   the corner cell C is met by <= 1 square   ==>   K0-FREE
                                   (teleport, Lean `teleport_packing`) ==> the cell is DEAD.

What is stronger is the geometry: a free square must avoid, not the axis-aligned core K(a) of
each conditioned box, but the whole polygon core K'(B) = INTERSECTION over poses in B of Q(pose)
(A132 `polycore.build`, vertices certified exactly).

THE DISCHARGE IS A SINGLE RATIONAL POINT, NOT A POLYGON.  For a box b of the pose cover and a
conditioned box B_j it suffices to exhibit ONE rational point w with

    (i)  w in Q(c, th) for every (c, th) in b        (`polycore.vertex_ok(w, b)`, exact)
    (ii) w in Q(c, th) for every (c, th) in B_j      (`polycore.vertex_ok(w, B_j)`, exact)

Then a square with pose in b and the conditioned square j share the point w, so by
`Zones.core_meet_same_square` (Lean; A135 `PolyCoreT5.shared_point_same_square`) they are THE SAME
square -- impossible for a free square, and impossible for a second conditioned square i != j.
K'(B_j) never appears in the certificate; it is only where the search for w looks.

FRAME.  Everything is at side s0, on the DILATED family F = D_lambda P (Lemma B.0), which is where
the k0 hypothesis boxes are stated.  The corner cell is the WIDENED corner box of Lemma K0-WIDEN,

    C_w := [s0 - 1 - w0, s0]^2  at TR  (and the three D4 images),  w0 = (lam_max - 1)(1 + 1/sqrt2)
         = 0.02550919...,      lam_max = s0 / 3.82,

so that "<= 1 square of F meets int C_w(s0)" implies "<= 1 square of P meets int B_c(m)" for every
m in [3.82, s0] -- the hypothesis Lemma K0-FREE consumes.  (A118 ran the same count pulled back to
side m in the corner frame; the widened-at-s0 form is used here because A140's certified K' live
at s0.)

SOUNDNESS.  Every prune below is an interval statement over a whole box, always in the direction
that ENLARGES the reachable set:
  (a) `box_outside_container` -- every pose leaves [0, s0]^2;
  (b) `box_misses_cell`       -- every pose's square misses int C_w (one separating axis, the
                                 cell's own, certified over the box);
  (c) `witness`               -- the shared rational point above.
A box that survives all three is bisected; a leaf that survives the budget makes the verdict
UNDECIDED, never a kill.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A118 = os.path.join(ROOT, "attempts", "A118-lane-count", "code")
A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (A118, A132, A57):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402  (must precede numpy)
import numpy as np  # noqa: E402

import lanelib as L                      # noqa: E402  READ-ONLY import of A118
import polycore as PC                    # noqa: E402  READ-ONLY import of A132
from caselp import Box, t_lo, t_hi       # noqa: E402  READ-ONLY import of A57

SQ2 = math.sqrt(2.0)
S0 = 969271.0 / 250000.0                 # 3.877084
WLO = 3.82
LAM_MAX = S0 / WLO
W0 = (LAM_MAX - 1.0) * (1.0 + 1.0 / SQ2)          # Lemma K0-WIDEN, 0.025509...
VDEN = 10 ** 9

CORNERS = ("BL", "BR", "TR", "TL")


# --------------------------------------------------------------------- the widened corner cell
def corner_cell(corner, s=S0, w=W0):
    """(X0, X1, Y0, Y1) of the widened corner box B_c^w(s) of Lemma K0-WIDEN."""
    lo, hi = 0.0, 1.0 + w
    if corner == "BL":
        return (lo, hi, lo, hi)
    if corner == "BR":
        return (s - hi, s - lo, lo, hi)
    if corner == "TR":
        return (s - hi, s - lo, s - hi, s - lo)
    if corner == "TL":
        return (lo, hi, s - hi, s - lo)
    raise ValueError(corner)


def centre_window(cell, s=S0):
    """Bounding rectangle of the centres of poses whose square can meet int(cell) and lie inside
    [0, s]^2.  |c_x - cell_x| <= 1/2 (cell half-width) + sqrt2/2, intersected with [1/2, s - 1/2]
    (the container's centre domain, since h(theta) >= 1/2)."""
    X0, X1, Y0, Y1 = cell
    return (max(0.5, X0 - SQ2 / 2.0), min(s - 0.5, X1 + SQ2 / 2.0),
            max(0.5, Y0 - SQ2 / 2.0), min(s - 0.5, Y1 + SQ2 / 2.0))


# --------------------------------------------------------------------- sound box prunes
def box_outside_container(b, s=S0, eps=1e-12):
    """True if EVERY pose in b puts the square outside [0, s]^2."""
    hmin = 0.5 * L.min_cs(b.th0, b.th1)
    return (b.x1 < hmin - eps or b.y1 < hmin - eps
            or b.x0 > s - hmin + eps or b.y0 > s - hmin + eps)


def box_misses_cell(b, cell, eps=1e-12):
    """True if EVERY pose in b gives a square with int Q disjoint from int(cell).

    One separating axis certified over the whole box suffices; the cell is axis-aligned, so its
    own two normals are used (sound, possibly incomplete)."""
    X0, X1, Y0, Y1 = cell
    hmax = 0.5 * L.max_cs(b.th0, b.th1)
    return (b.x0 - hmax >= X1 - eps or b.x1 + hmax <= X0 + eps
            or b.y0 - hmax >= Y1 - eps or b.y1 + hmax <= Y0 + eps)


def point_margin(w, b):
    """m(w, b) = 1/2 - max over (c, theta) in b of |R(-theta)(w - c)|_inf.

    m > 0  <=>  the point w lies in the OPEN square Q(c, theta) for every pose in b.  The maximum
    is exact: c enters affinely (so a corner of the centre rectangle attains it -- Lean
    `PolyCoreT5.biaffine_bound`) and the theta maximum of |d . e(theta)| is at an endpoint or at
    theta = arg(d) mod 90 deg (`lanelib._max_abs_proj`)."""
    wx, wy = float(w[0]), float(w[1])
    D = (wx - b.x1, wx - b.x0, wy - b.y1, wy - b.y0)
    return 0.5 - L._max_abs_proj(D, b.th0, b.th1)


_HALFPI = 0.5 * math.pi


def _gmax(alpha, beta):
    """max over psi in [alpha, beta] of max(|cos psi|, |sin psi|).

    f(psi) = max(|cos|, |sin|) is 1 at every multiple of 90 deg and V-shaped in between, so the
    max over an interval is 1 if the interval straddles a multiple of pi/2 and is attained at an
    endpoint otherwise.  Vectorised."""
    straddle = np.ceil(alpha / _HALFPI) <= beta / _HALFPI + 1e-15
    fa = np.maximum(np.abs(np.cos(alpha)), np.abs(np.sin(alpha)))
    fb = np.maximum(np.abs(np.cos(beta)), np.abs(np.sin(beta)))
    return np.where(straddle, 1.0, np.maximum(fa, fb))


def point_margin_many(W, b):
    """point_margin for many candidate points at once.  W is (n, 2)."""
    W = np.asarray(W, float).reshape(-1, 2)
    a0, a1 = math.radians(b.th0), math.radians(b.th1)
    worst = np.zeros(len(W))
    for (cx, cy) in ((b.x0, b.y0), (b.x1, b.y0), (b.x1, b.y1), (b.x0, b.y1)):
        dx = W[:, 0] - cx
        dy = W[:, 1] - cy
        R = np.hypot(dx, dy)
        phi = np.arctan2(dy, dx)
        worst = np.maximum(worst, R * _gmax(a0 - phi, a1 - phi))
    return 0.5 - worst


def best_shared_point(b, bj, rounds=7, ngrid=9):
    """Maximise  f(w) = min(point_margin(w, b), point_margin(w, bj))  over w in the plane.

    Both margins are CONCAVE in w (1/2 minus a max of absolute values of affine forms), so f is
    concave and a shrinking-grid refinement converges to the global maximum.  Returns (w, f, mb,
    mj).  f > 0 means the two boxes' poses all share the point w -- the T5''' discharge."""
    lo = np.array([max(b.x0 - SQ2 / 2, bj.x0 - SQ2 / 2), max(b.y0 - SQ2 / 2, bj.y0 - SQ2 / 2)])
    hi = np.array([min(b.x1 + SQ2 / 2, bj.x1 + SQ2 / 2), min(b.y1 + SQ2 / 2, bj.y1 + SQ2 / 2)])
    if np.any(hi <= lo):
        return None, -1.0, -1.0, -1.0
    ctr = 0.5 * (lo + hi)
    half = 0.5 * (hi - lo)
    best = (None, -1e9, -1e9, -1e9)
    for _ in range(rounds):
        gx = np.linspace(ctr[0] - half[0], ctr[0] + half[0], ngrid)
        gy = np.linspace(ctr[1] - half[1], ctr[1] + half[1], ngrid)
        GX, GY = np.meshgrid(gx, gy, indexing="ij")
        W = np.column_stack([GX.ravel(), GY.ravel()])
        mb = point_margin_many(W, b)
        mj = point_margin_many(W, bj)
        f = np.minimum(mb, mj)
        k = int(np.argmax(f))
        if f[k] > best[1]:
            best = ((float(W[k, 0]), float(W[k, 1])), float(f[k]), float(mb[k]), float(mj[k]))
        ctr = W[k]
        half = half * (2.0 / (ngrid - 1))
    return best


def rationalise(w):
    return (Fr(round(float(w[0]) * VDEN), VDEN), Fr(round(float(w[1]) * VDEN), VDEN))


def certify_point(wq, b):
    """EXACT (Fraction) form of `point_margin(wq, b) > 0` for the CLOSED square: A132's
    `vertex_ok`, i.e. Lean's `checkVertexInPBox`.  The tilt range used is [t_lo(th0), t_hi(th1)],
    an OUTWARD-rounded superset of the box's own -- conservative."""
    return PC.vertex_ok(wq[0], wq[1], b)


# --------------------------------------------------------------------- witness points
def witness_pool(pc, ngrid=13):
    """Candidate rational points inside K'(B): the polygon's vertices pulled a hair inwards, its
    centroid, and a grid over its bounding box kept inside the polygon.  Only a SEARCH space --
    every candidate is certified exactly before it is used."""
    P = pc.P
    cx, cy = float(P[:, 0].mean()), float(P[:, 1].mean())
    out = [(cx, cy)]
    for (vx, vy) in P:
        out.append((0.85 * float(vx) + 0.15 * cx, 0.85 * float(vy) + 0.15 * cy))
        out.append((0.5 * float(vx) + 0.5 * cx, 0.5 * float(vy) + 0.5 * cy))
    lo, hi = P.min(0), P.max(0)
    E = np.roll(P, -1, axis=0) - P
    for gx in np.linspace(lo[0], hi[0], ngrid):
        for gy in np.linspace(lo[1], hi[1], ngrid):
            if np.all(E[:, 0] * (gy - P[:, 1]) - E[:, 1] * (gx - P[:, 0]) >= 1e-9):
                out.append((float(gx), float(gy)))
    return out


class CondSq:
    """One conditioned square of the cell: its box, its certified polygon core, and the pool of
    candidate witness points inside that core."""

    def __init__(self, idx, box, pc=None, pool=None):
        self.idx = idx
        self.box = box
        self.pc = pc
        self.pool = pool if pool is not None else []
        # the same margin test, precomputed for the conditioned box itself
        self.pool_margin = [point_margin(w, box) for w in self.pool]


def container_hull(b, s=S0):
    """The smallest box containing every CONTAINER-ADMISSIBLE pose of b.

    A pose is admissible only if h(theta) <= c <= s - h(theta) with h = (|cos|+|sin|)/2 >=
    min_cs/2 over the box's tilt range, so the centre rectangle may be clipped to
    [hmin, s - hmin]^2.  Sound (the actual square IS admissible); returns None if b holds no
    admissible pose at all."""
    hmin = 0.5 * L.min_cs(b.th0, b.th1)
    x0, x1 = max(b.x0, hmin), min(b.x1, s - hmin)
    y0, y1 = max(b.y0, hmin), min(b.y1, s - hmin)
    if x1 < x0 or y1 < y0:
        return None
    return Box(x0, x1, y0, y1, b.th0, b.th1)


def build_cond(boxes, n_grid=129, ngrid=13, verbose=False, tighten=True, s=S0):
    """[CondSq] for a list of caselp.Box hypothesis boxes, with certified K'(B) each."""
    out = []
    for i, b0 in enumerate(boxes):
        b = (container_hull(b0, s) or b0) if tighten else b0
        pc = PC.build(b, n_grid=n_grid)
        assert pc.certified
        pool = witness_pool(pc, ngrid)
        pool = [w for w in pool if point_margin(w, b) > 1e-7]
        out.append(CondSq(i, b, pc, pool))
        if verbose:
            print(f"    K'(B{i}) verts={len(pc.verts)} area={pc.area():.6f} pool={len(pool)}",
                  flush=True)
    return out


MARGIN = 1e-7


def find_witness(b, conds, skip=None, exact=True):
    """A rational point shared by every pose of `b` and every pose of some conditioned box.

    Returns (j, [str(x), str(y)], margin_b, margin_j) or None.  Two stages: the precomputed pool
    inside each K'(B_j) (cheap, catches the bulk), then the concave refinement `best_shared_point`
    (exhaustive, catches the shallow slivers).  The float margins only PICK the candidate;
    `certify_point` -- A132's exact rational `vertex_ok`, Lean's `checkVertexInPBox` -- is what
    makes it a certificate."""
    cands = []
    for cs in conds:
        if skip is not None and cs.idx == skip:
            continue
        if not cs.pool:
            continue
        mb = point_margin_many(cs.pool, b)
        mj = np.asarray(cs.pool_margin)
        f = np.minimum(mb, mj)
        k = int(np.argmax(f))
        if f[k] > MARGIN:
            cands.append((float(f[k]), cs, tuple(cs.pool[k]), float(mb[k]), float(mj[k])))
    if not cands:
        for cs in conds:
            if skip is not None and cs.idx == skip:
                continue
            w, f, mb, mj = best_shared_point(b, cs.box)
            if w is not None and f > MARGIN:
                cands.append((f, cs, w, mb, mj))
    if not cands:
        return None
    cands.sort(key=lambda z: -z[0])
    for (_, cs, w, mb, mj) in cands:
        wq = rationalise(w)
        if (not exact) or (certify_point(wq, b) and certify_point(wq, cs.box)):
            return (cs.idx, [str(wq[0]), str(wq[1])], mb, mj)
    return None


# --------------------------------------------------------------------- the cover, as a tree
def split_box(b):
    """The deterministic bisection the certificate replays: widest of (x, y, theta/60)."""
    wx, wy, wt = b.x1 - b.x0, b.y1 - b.y0, (b.th1 - b.th0) / 60.0
    if wx >= wy and wx >= wt:
        m = 0.5 * (b.x0 + b.x1)
        return (Box(b.x0, m, b.y0, b.y1, b.th0, b.th1),
                Box(m, b.x1, b.y0, b.y1, b.th0, b.th1))
    if wy >= wt:
        m = 0.5 * (b.y0 + b.y1)
        return (Box(b.x0, b.x1, b.y0, m, b.th0, b.th1),
                Box(b.x0, b.x1, m, b.y1, b.th0, b.th1))
    m = 0.5 * (b.th0 + b.th1)
    return (Box(b.x0, b.x1, b.y0, b.y1, b.th0, m),
            Box(b.x0, b.x1, b.y0, b.y1, m, b.th1))


def box_json(b):
    return [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]


def cover_empty(root, cell, conds, s=S0, skip=None, max_leaves=200000, max_depth=44,
                exact=True, max_open=2500):
    """Prove that NO pose of `root` survives (container, meets int cell, avoids every conditioned
    square other than `skip`) -- i.e. the reachable set is EMPTY.

    Returns dict(ok, leaves=[{path, box, why, ...}], n_leaves, depth, open=[...]).  Every leaf
    carries the reason it is discharged; the union of the leaf boxes is exactly `root`, so the
    leaves are a finite cover and the verdict is the conjunction of finitely many interval facts.
    """
    leaves = []
    stack = [("", root)]
    n_open = []
    depth = 0
    while stack:
        path, b = stack.pop()
        depth = max(depth, len(path))
        if box_outside_container(b, s):
            leaves.append(dict(path=path, box=box_json(b), why="container"))
            continue
        if box_misses_cell(b, cell):
            leaves.append(dict(path=path, box=box_json(b), why="misses_cell"))
            continue
        w = find_witness(b, conds, skip=skip, exact=exact)
        if w is not None:
            j, pt, mb, mj = w
            leaves.append(dict(path=path, box=box_json(b), why="witness", j=j, w=pt,
                               margin_box=mb, margin_cond=mj))
            continue
        if len(path) >= max_depth or len(leaves) + len(stack) > max_leaves:
            n_open.append(dict(path=path, box=box_json(b)))
            if len(n_open) > max_open:
                return dict(ok=False, complete=False, leaves=leaves, n_leaves=len(leaves),
                            depth=depth, open=n_open, reason="open-leaf budget exhausted")
            continue
        b0, b1 = split_box(b)
        stack.append((path + "0", b0))
        stack.append((path + "1", b1))
    if n_open:
        return dict(ok=False, complete=True, leaves=leaves, n_leaves=len(leaves), depth=depth,
                    open=n_open, reason="undischarged leaves")
    return dict(ok=True, complete=True, leaves=leaves, n_leaves=len(leaves), depth=depth,
                open=[])


def _discharge(b, cell, conds, s, skip, exact):
    """(why, extra) for one box, or None if it survives all three prunes."""
    if box_outside_container(b, s):
        return ("container", {})
    if box_misses_cell(b, cell):
        return ("misses_cell", {})
    w = find_witness(b, conds, skip=skip, exact=exact)
    if w is not None:
        j, pt, mb, mj = w
        return ("witness", dict(j=j, w=pt, margin_box=mb, margin_cond=mj))
    return None


def lane_cover(root, cell, conds, s=S0, skip=None, exact=True, depth0=20, max_depth=40,
               max_open=1500, rounds=8, rng=None):
    """LANE_K'(C) <= 1 by A118 sec 1.2, with the K' discharge.

    Build a COMPLETE cover of the pose window: every box is either discharged (container / misses
    the cell / shares a point with a conditioned square) or kept open.  Then test every pair of
    open boxes with the octagon/Minkowski bound `pairs_always_overlap_matrix` -- no separating axis
    exists for ANY pose pair drawn from the two boxes, so two squares in them always overlap.  All
    pairs passing (the diagonal included) means no two interior-disjoint free squares can both
    reach C: LANE <= 1.  An empty open set is LANE = 0.  Failing pairs are bisected and re-pruned.
    """
    leaves = []
    hist = []
    open_ = []
    stack = [("", root)]
    while stack:
        p, bb = stack.pop()
        d = _discharge(bb, cell, conds, s, skip, exact)
        if d is not None:
            why, extra = d
            leaves.append(dict(path=p, box=box_json(bb), why=why, **extra))
            continue
        if len(p) >= depth0:
            open_.append((p, bb))
        else:
            b0, b1 = split_box(bb)
            stack.append((p + "0", b0))
            stack.append((p + "1", b1))
        if len(open_) + len(stack) > max_open:
            return dict(lane=None, complete=False, leaves=leaves, open=[], hist=hist,
                        reason="open budget exhausted")
    hist.append(len(open_))
    for it in range(rounds + 1):
        if not open_:
            return dict(lane=0, complete=True, leaves=leaves, open=[], hist=hist)
        if len(open_) > max_open:
            return dict(lane=None, complete=False, leaves=leaves, open=[], hist=hist,
                        reason="open budget exhausted")
        bxs = [bb for (_, bb) in open_]
        BAD = ~L.pairs_always_overlap_matrix(bxs)
        if BAD.any():
            # the vectorised screen uses the coarse |n.d| <= |d| bound; re-test the survivors
            # with A118's SHARP per-normal bound `pair_always_overlap` before splitting.
            ii, jj = np.nonzero(np.triu(BAD))
            if len(ii) <= 60000:
                for (u, v) in zip(ii.tolist(), jj.tolist()):
                    if L.pair_always_overlap(bxs[u], bxs[v]):
                        BAD[u, v] = BAD[v, u] = False
        if not BAD.any():
            return dict(lane=1, complete=True, leaves=leaves,
                        open=[dict(path=p, box=box_json(bb)) for (p, bb) in open_], hist=hist)
        if it == rounds:
            break
        bad = set(np.nonzero(BAD.any(axis=1))[0].tolist())
        new = []
        for k, (p, bb) in enumerate(open_):
            if k not in bad or len(p) >= max_depth:
                new.append((p, bb))
                continue
            for (pp, nb) in zip((p + "0", p + "1"), split_box(bb)):
                d = _discharge(nb, cell, conds, s, skip, exact)
                if d is not None:
                    why, extra = d
                    leaves.append(dict(path=pp, box=box_json(nb), why=why, **extra))
                else:
                    new.append((pp, nb))
        if len(new) == len(open_):
            break                                    # nothing left to refine
        open_ = new
        hist.append(len(open_))
    return dict(lane=None, complete=True, leaves=leaves,
                open=[dict(path=p, box=box_json(bb)) for (p, bb) in open_], hist=hist,
                reason="refinement budget exhausted")


# --------------------------------------------------------------------- M: which conditioned
# squares can meet the cell
def cond_can_meet(cs, cell, conds, s=S0, max_leaves=60000, max_depth=40, exact=True,
                  max_open=600):
    """Can the conditioned square `cs` meet int(cell)?  Sound EXCLUSION: cover its own box and
    discharge every sub-box by (container) / (misses the cell) / (shares a rational point with a
    DIFFERENT conditioned box, so the two would be the same square).  ok=True means EXCLUDED."""
    return cover_empty(cs.box, cell, conds, s=s, skip=cs.idx, max_leaves=max_leaves,
                       max_depth=max_depth, exact=exact, max_open=max_open)


# --------------------------------------------------------------------- sampling
def sample_meeting(cell, s, n, rng):
    """Uniform poses in the centre window x [0, 90) that lie in the container and whose square
    meets int(cell).  Returns (C, TH radians)."""
    x0, x1, y0, y1 = centre_window(cell, s)
    C = np.column_stack([rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)])
    TH = rng.uniform(0.0, 0.5 * math.pi, n)
    h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
    X0, X1, Y0, Y1 = cell
    ok = ((C[:, 0] >= h) & (C[:, 0] <= s - h) & (C[:, 1] >= h) & (C[:, 1] <= s - h))
    ok &= rect_square_meets(cell, C, TH)
    return C[ok], TH[ok]


def sample_free(cell, s, conds, n, rng):
    """Poses in R'(C): container + meets int(cell) + interior-disjoint from every K'(B_j)."""
    C, TH = sample_meeting(cell, s, n, rng)
    if not len(C):
        return C, TH
    ok = np.ones(len(C), bool)
    for cs in conds:
        if not ok.any():
            break
        ok &= (PC.poly_square_depth(cs.pc.P, C, TH) <= 0.0)
    return C[ok], TH[ok]


# --------------------------------------------------------------------- the pair contradiction
def pair_incompatible(bi, bj, s=S0, max_leaves=120000, max_depth=44, exact=True):
    """Is the node's hypothesis "square i in box bi AND square j in box bj, i != j" CONTRADICTORY?

    Sound test: cover bi and discharge every sub-box either because every pose of it leaves the
    container, or because it shares a rational point with EVERY pose of bj -- in which case a
    square with that pose and the square in bj are the same square (`shared_point_same_square`),
    contradicting i != j.  ok=True is the kill.

    This is strictly stronger than A140's K'(bi)-meets-K'(bj) test (which compares the two
    INTERSECTIONS over the whole boxes) and than A118's full-box octagon pair test, because the
    sub-boxes have much fatter polygon cores and because the CONTAINER prune removes the corner of
    bi where a separating axis exists."""
    cj = CondSq(0, bj, None, [])
    return cover_empty(bi, (-1e9, 1e9, -1e9, 1e9), [cj], s=s, skip=None,
                       max_leaves=max_leaves, max_depth=max_depth, exact=exact)


def _sample_screen(cell, conds, s, rng, n):
    """The cheap screen, run BEFORE any cover: sampled lower bounds on LANE and on M.

    `free` poses realise LANE >= 1 (and a disjoint pair realises LANE >= 2); a sampled pose of
    box j that meets the cell and avoids every OTHER K' realises "j can meet" (M >= that count).
    Lower bounds cannot kill, but they say when a kill is impossible, and the expensive covers are
    then skipped."""
    Cs, Ts = sample_meeting(cell, s, n, rng)
    sm = dict(drawn=n, meeting=int(len(Cs)), lane_lb=0, cond_lb=[])
    if len(Cs):
        hit = np.zeros(len(Cs), bool)
        per = {}
        for cs in conds:
            h = PC.poly_square_depth(cs.pc.P, Cs, Ts) > 0.0
            per[cs.idx] = int(h.sum())
            hit |= h
        sm.update(overlapping_some_core=int(hit.sum()), per_core=per, free=int((~hit).sum()))
        FC, FT = Cs[~hit][:800], Ts[~hit][:800]
        if len(FC):
            sm["lane_lb"] = 1
            sm["free_pose"] = [float(FC[0, 0]), float(FC[0, 1]), float(FT[0])]
        if len(FC) >= 2:
            G = L.pair_gaps(FC, FT)
            np.fill_diagonal(G, -1e9)
            k = int(np.argmax(G))
            a, b_ = divmod(k, len(FC))
            sm["max_pair_gap"] = float(G[a, b_])
            if G[a, b_] > 0.0:
                sm["lane_lb"] = 2
                sm["witness_pair"] = [float(FC[a, 0]), float(FC[a, 1]), float(FT[a]),
                                      float(FC[b_, 0]), float(FC[b_, 1]), float(FT[b_])]
    # M lower bound, per conditioned box
    for cs in conds:
        b = cs.box
        m = max(400, n // 8)
        C = np.column_stack([rng.uniform(b.x0, b.x1, m), rng.uniform(b.y0, b.y1, m)])
        T = np.radians(rng.uniform(b.th0, b.th1, m))
        h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
        ok = ((C[:, 0] >= h) & (C[:, 0] <= s - h) & (C[:, 1] >= h) & (C[:, 1] <= s - h))
        ok &= rect_square_meets(cell, C, T)
        for o in conds:
            if o.idx == cs.idx or not ok.any():
                continue
            ok &= (PC.poly_square_depth(o.pc.P, C, T) <= 0.0)
        sm["cond_lb"].append(dict(j=cs.idx, can_meet=bool(ok.any()), n=int(ok.sum())))
    sm["M_lb"] = sum(1 for e in sm["cond_lb"] if e["can_meet"])
    return sm


def lane_corner(corner, conds, s=S0, w=W0, **kw):
    """The K' lane test at one corner of a k0 cell (the widened corner box of Lemma K0-WIDEN)."""
    out = lane_corner_generic(corner_cell(corner, s, w), conds, s=s, **kw)
    out["corner"] = corner
    return out


def lane_corner_generic(cell, conds, s=S0, meeters=None, rng=None, max_leaves=120000,
                        max_depth=34, keep_cert=True, sample=20000, max_open=1500,
                        screen=True, lane_depth0=20, bound_when_dead=True):
    """The K' lane test at an arbitrary axis-aligned cell rectangle.

    `meeters` = the indices of the conditioned squares that COUNT towards M (for a pinned class
    the pins are obstacles only: SLOT-CROWD gives >= 2 NON-PIN meeters).  Default: all."""
    x0, x1, y0, y1 = centre_window(cell, s)
    mset = set(c.idx for c in conds) if meeters is None else set(meeters)
    out = dict(cell=list(cell), root=[x0, x1, y0, y1, 0.0, 90.0],
               lane_ub=None, lane_lb=None, M=None, meeters=None, verdict="UNDECIDED")
    if x1 <= x0 or y1 <= y0:
        out.update(lane_ub=0, lane_lb=0, M=0, meeters=[], verdict="KILL",
                   reason="empty centre window")
        return out
    rng = rng if rng is not None else np.random.default_rng(141)
    sm = _sample_screen(cell, conds, s, rng, sample) if screen else dict(lane_lb=0, M_lb=0,
                                                                        cond_lb=[])
    out["sample"] = sm
    out["lane_lb"] = sm["lane_lb"]
    lane_lb = sm["lane_lb"]
    M_lb = sum(1 for e in sm.get("cond_lb", []) if e["can_meet"] and e["j"] in mset)
    if lane_lb + M_lb >= 2:                      # a kill is impossible; skip the covers
        out.update(M=M_lb, M_exact=False,
                   meeters=[e["j"] for e in sm["cond_lb"] if e["can_meet"] and e["j"] in mset],
                   verdict=("LANE>=2" if lane_lb >= 2 else "NEAR-MISS-OR-WORSE"),
                   skipped_covers=True, M_lb=M_lb)
        if lane_lb <= 1 and bound_when_dead:      # still worth the certified LANE bound
            root = Box(x0, x1, y0, y1, 0.0, 90.0)
            cov = lane_cover(root, cell, conds, s=s, depth0=lane_depth0, max_depth=max_depth,
                             max_open=max_open)
            out.update(lane_ub=cov["lane"], cover_leaves=len(cov["leaves"]),
                       cover_open=len(cov["open"]),
                       verdict=("NEAR-MISS" if (cov["lane"] is not None
                                                and cov["lane"] + M_lb == 2)
                                else out["verdict"]))
            if keep_cert and cov["lane"] is not None:
                out["cover_cert"] = cov["leaves"]
                out["cover_open_cert"] = cov["open"]
        return out

    root = Box(x0, x1, y0, y1, 0.0, 90.0)
    cov = lane_cover(root, cell, conds, s=s, depth0=lane_depth0, max_depth=max_depth,
                     max_open=max_open)
    lane_ub = cov["lane"]
    Mex = []
    for cs in conds:
        if cs.idx not in mset:
            continue
        lb = next((e for e in sm.get("cond_lb", []) if e["j"] == cs.idx), None)
        if lb is not None and lb["can_meet"]:
            Mex.append(dict(j=cs.idx, excluded=False, leaves=0, cert=None, by="sample"))
            continue
        r = cond_can_meet(cs, cell, conds, s=s, max_leaves=max_leaves, max_depth=max_depth,
                          max_open=max_open)
        Mex.append(dict(j=cs.idx, excluded=bool(r["ok"]), leaves=r["n_leaves"],
                        cert=(r["leaves"] if (keep_cert and r["ok"]) else None), by="cover"))
    M = sum(0 if e["excluded"] else 1 for e in Mex)
    out.update(lane_ub=lane_ub, M=M, M_exact=True,
               M_detail=[dict(j=e["j"], excluded=e["excluded"], by=e["by"]) for e in Mex],
               cover_leaves=len(cov["leaves"]), cover_open=len(cov["open"]),
               cover_hist=cov["hist"],
               verdict=("KILL" if (lane_ub is not None and lane_ub + M <= 1)
                        else ("NEAR-MISS" if (lane_ub is not None and lane_ub + M == 2)
                              else "UNDECIDED")),
               meeters=[e["j"] for e in Mex if not e["excluded"]])
    if keep_cert:
        out["cover_cert"] = cov["leaves"] if lane_ub is not None else None
        out["cover_open_cert"] = cov["open"] if lane_ub is not None else None
        out["M_cert"] = [e["cert"] for e in Mex]
    if lane_ub is not None and out["lane_lb"] is not None and out["lane_lb"] > lane_ub:
        out["verdict"] = "INCONSISTENT"          # loud: a certified bound below a realised one
    return out


def lane_corner_split(cell, conds, j, s=S0, meeters=None, rng=None, max_pieces=96,
                      max_depth=8, sample=8000, max_open=2500, lane_depth0=20,
                      keep_cert=True):
    """The JOINT count (the PI's refinement): apply the leaf on a finite PARTITION of the
    conditioned square j's own parameter box.

    `LANE_K'(C) = 1, M = 1` is not a kill only because the two are counted separately.  Partition
    `B_j` into sub-boxes `B_1 … B_N` (a complete binary subdivision, so the actual pose of square
    j is in exactly one of them) and run the leaf on each piece with `K'(B_k)` — which is STRICTLY
    BIGGER than `K'(B_j)` — in place of `K'(B_j)`:

      * if every pose of `B_k` misses `int C` (`box_misses_cell`), square j is not a meeter there,
        so `m_k = 0` and `LANE_k <= 1` suffices;
      * otherwise `m_k = 1` and the piece needs `LANE_k = 0`: `C` is then met by square j alone.

    In every case `C` is met by at most one square, so `C` is singly met for EVERY realisation —
    K0-FREE, the cell is dead.  This is the ordinary leaf, applied `N` times; the only new content
    is the finite cover of `B_j`, the same `path_cover_complete` obligation the pose cover needs.
    """
    rng = rng if rng is not None else np.random.default_rng(141)
    others = [c for c in conds if c.idx != j]
    mset = set(c.idx for c in conds) if meeters is None else set(meeters)
    other_meet = sorted(mset - {j})
    pieces = [("", conds[j].box)]
    done, opens = [], []
    while pieces:
        path, b = pieces.pop()
        try:
            pc = build_cond([b], tighten=False)[0]
        except Exception:                                       # noqa: BLE001
            opens.append(dict(path=path, box=box_json(b), why="polycore build failed"))
            continue
        pc.idx = j
        cs = others + [pc]
        misses = box_misses_cell(b, cell)
        res = lane_corner_generic(cell, cs, s=s, meeters=other_meet, rng=rng, sample=sample,
                                  max_open=max_open, lane_depth0=lane_depth0,
                                  keep_cert=keep_cert, bound_when_dead=True)
        m_j = 0 if misses else 1
        tot = None if res["lane_ub"] is None else res["lane_ub"] + (res["M"] or 0) + m_j
        rec = dict(path=path, box=box_json(b), misses_cell=bool(misses), m_j=m_j,
                   lane_ub=res["lane_ub"], M_other=res["M"], total=tot,
                   verdict=res["verdict"], root=res["root"],
                   cond_boxes=[box_json(c.box) for c in cs],
                   cond_index=[c.idx for c in cs])
        if keep_cert:
            rec["lane_leaves"] = res.get("cover_cert")
            rec["lane_open"] = res.get("cover_open_cert")
            rec["M_cert"] = res.get("M_cert")
            rec["M_index"] = [e["j"] for e in (res.get("M_detail") or [])]
        if tot is not None and tot <= 1:
            done.append(rec)
            continue
        if len(path) >= max_depth or len(done) + len(pieces) >= max_pieces:
            opens.append(rec)
            continue
        b0, b1 = split_box(b)
        pieces.append((path + "0", b0))
        pieces.append((path + "1", b1))
    return dict(ok=(not opens), pieces=done, open=opens, n_pieces=len(done) + len(opens),
                split_index=j)


def rect_square_meets(cell, C, TH):
    """Exact SAT: int Q(c, theta) meets int(rect)?  (4 axes: the rect's two and the square's two.)"""
    X0, X1, Y0, Y1 = cell
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    ct, st = np.cos(TH), np.sin(TH)
    hx = 0.5 * (np.abs(ct) + np.abs(st))
    ok = (C[:, 0] - hx < X1) & (C[:, 0] + hx > X0) & (C[:, 1] - hx < Y1) & (C[:, 1] + hx > Y0)
    RV = np.array([[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]], float)
    for (ax, ay) in ((ct, st), (-st, ct)):
        pr = RV[:, 0][:, None] * ax[None, :] + RV[:, 1][:, None] * ay[None, :]
        qc = C[:, 0] * ax + C[:, 1] * ay
        ok &= (pr.max(0) > qc - 0.5) & (pr.min(0) < qc + 0.5)
    return ok
