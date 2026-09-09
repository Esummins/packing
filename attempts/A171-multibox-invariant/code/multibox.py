"""A171 -- MULTIBOX: the multi-box clipping rule, as CODE.

WHY THIS MODULE EXISTS.  A165 and A168 both built multi-box case trees on the k0 cell l1_104 and
both drew/solved boxes that had never been clipped: pose unions escaping the container, and pose
unions overlapping another box's certified core.  The PI caught both by eye.  A rule that lives in a
brief is a rule that gets skipped; this module makes it a function call that every multi-box
construction has to make before it draws a figure, prices a chord row, runs a lane cover or hands
boxes to an LP.

--------------------------------------------------------------------------------------------------
THE OBJECT
--------------------------------------------------------------------------------------------------
A `Node` is a named collection of parameter boxes  B_name = [x0,x1] x [y0,y1] x [th0,th1],  each
carrying the hypothesis "some square of the packing has (centre, tilt) in B_name", the boxes naming
DISTINCT squares.  Two facts about a packing are then available for free and are what the clip uses:

    (CONTAINER)  every square lies inside [0, s]^2, so a pose (c, th) needs
                 w(th)/2 <= c <= s - w(th)/2 in each coordinate, w(th) = |cos th| + |sin th|;
    (DISJOINT)   the squares are interior-disjoint, and K'(B) (A132's certified polygon core) is
                 contained in EVERY pose of B, so a pose of box A whose square meets int K'(B) is
                 IMPOSSIBLE.

Each box is carried as a list of PIECES  (t-sub-bin [t0,t1], rational centre rect),  t = tan(th/2)
as everywhere in this repo (A57 `caselp`).  A piece is an over-approximation: it CONTAINS every
still-possible pose whose tilt lies in its sub-bin.  Clipping only ever removes poses that (CONTAINER)
or (DISJOINT) has just proved impossible, so the union of the pieces is a sound replacement for the
box at every stage.  A box that loses every piece has no possible pose at all -- the node is DEAD by
the pair leaf (`shared_point_same_square`, A135) -- and `normalise` raises `EmptyBox(name)`.

--------------------------------------------------------------------------------------------------
THE TWO CLIPS, AND EXACTLY WHAT EACH IS ALLOWED TO REMOVE
--------------------------------------------------------------------------------------------------
Both clips remove a centre only when it is dead FOR EVERY TILT IN ITS PIECE'S SUB-BIN.  That is the
only rule a (rect x tilt-interval) representation may use: a centre killed at some tilts but alive
at others still carries a pose of the piece.

  1. CONTAINER CLIP (sound).  Over a sub-bin the least restrictive container window is the one at
     w_min (w = cos + sin is concave on [0, 90], so its minimum is at an endpoint -- exact).  A
     centre outside [w_min/2, s - w_min/2]^2 admits no tilt in the sub-bin and is discarded.  This
     is A131 `pinclip.clip_rect`'s container step, verbatim.

     STRICT CONTAINER (`strict_container=True`, the default, and what "all poses inside [0,s]^2"
     means): additionally clip to [w_max/2, s - w_max/2]^2, so that EVERY pose of the piece is
     inside the container.  This is a genuine narrowing of the hypothesis and it is NOT free: the
     poses it drops (centre feasible at the low-w tilts of the sub-bin only) are real.  It is
     recorded as a `container_sliver` step in the trace, WITH ITS AREA, and `assert_invariant`
     reports `sliver_area` per box.  A caller who needs the full hypothesis passes
     `strict_container=False` and gets only the sound clip; a caller who wants a tight, drawable,
     row-able node passes the default and must either refine the tilt bins until the slivers are
     negligible or discharge them separately.  The slivers shrink like (w_max - w_min)/2 over the
     sub-bin, i.e. like 1/nsub^2 near a tilt where w is smooth -- refining `nsub` is the fix.
     Nothing is ever dropped silently.

  2. MUTUAL CLIP (sound, no caveat).  For an ordered pair (A, B) the DEAD SET of A against B is

         D_B(t0,t1) = { c : Q(c, th) meets int K'(B) for every th with tan(th/2) in [t0,t1] }.

     Every centre in D_B carries no pose of the piece, so the piece may be clipped by D_B.  D_B is
     CONVEX -- it is an intersection over th of Minkowski sums int K'(B) (+) (-Q(0,th)) of convex
     sets -- which is what makes the clip cheap and certifiable: if the four corners of a rectangle
     are in D_B then the whole rectangle is, so the axis slabs hanging off each side are found by
     bisection on two corner points and certified exactly (A131's `_bisect_boundary`, reused).

     The exact membership test `dead_poly` is a SUFFICIENT condition for c in D_B (never the
     converse), so the clip removes less than the truth -- the sound direction.  Details in
     `dead_poly`'s docstring.  `mode="core"` uses A135's exact axis core of B instead of A132's
     polygon; that is a subset of K'(B), hence also sound, and it is A131's own octagon predicate
     transported into the core's frame (`_frames`).

  The two clips are iterated to a fixed point.  After each pass, K'(B) and the exact axis core are
  RECOMPUTED from the surviving pieces: dropping poses from B can only ENLARGE K'(B) (an
  intersection over fewer poses), which clips the other boxes harder.  That cascade is the whole
  point -- it is what A165/A168 skipped.

  K'(B) IS BUILT FROM THE PIECES, NOT FROM THEIR HULL (A172).  The first version of this module
  rebuilt K' from `union_box()`, the smallest axis box x tilt hull containing the survivors; a hull
  forgets a clip that removes different slabs in different tilt sub-bins, so K' hardly grew and the
  cascade hardly bit.  K'(B) is now the EXACT rational intersection of the per-piece K', with every
  vertex re-certified against every piece by `polycore.vertex_ok` -- see the A172 block above
  `MBox`.  `kmode="union"` restores the old behaviour as a fallback/diagnostic.

--------------------------------------------------------------------------------------------------
THE INVARIANT
--------------------------------------------------------------------------------------------------
`assert_invariant()` is exact rational arithmetic throughout and raises `InvariantError` listing
EVERY failure it found (never just the first):

    K-CONTAINER   every vertex of every K'(B) lies in [0, s]^2.
    K-DISJOINT    every pair K'(A), K'(B) is interior-disjoint (exact rational SAT over the edge
                  normals of both polygons -- complete for convex polygons).
    POSE-CONTAINER   every piece's rect is inside [w_min/2, s - w_min/2]^2 (sound clip reached).
    POSE-CONTAINER-STRICT (strict=True)  every piece's rect is inside [w_max/2, s - w_max/2]^2,
                  i.e. EVERY POSE of the node is inside the container.  This is the check that
                  catches A168's D.
    CLIP-FIXPOINT  re-running the mutual clip on every piece changes nothing, i.e. no centre of any
                  box is dead against another box's core.

It also returns (never raises on) the tightness diagnostics `sliver_area`, `escape_frac` and
`core_meet_frac` -- the last two sampled -- because the residual "pose meets another core at SOME
tilt of its sub-bin" cannot be driven to zero by a rectangle-times-interval representation, only
made small by refining `nsub`.

--------------------------------------------------------------------------------------------------
READ-ONLY IMPORTS
--------------------------------------------------------------------------------------------------
A131 pinclip, A132 polycore, A135 exactcore, A141 polylane, A144 guardline, A161 chordlane, A57
caselp.  Nothing in this module writes outside attempts/A171-multibox-invariant.
"""
import itertools
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
_PATHS = [
    os.path.join(ATT, "A141-polycore-lane", "code"),      # blas1 first (single-thread guard)
    os.path.join(ATT, "A57-shadow-trees", "code"),
    os.path.join(ATT, "A131-pin-clip", "code"),
    os.path.join(ATT, "A132-polygon-core", "code"),
    os.path.join(ATT, "A135-polycore-verifier", "code"),
    os.path.join(ATT, "A144-guard-lines", "code"),
    os.path.join(ATT, "A161-chord-lane", "code"),
    os.path.join(ATT, "A118-lane-count", "code"),
]
for _p in _PATHS:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1  # noqa: F401,E402   READ-ONLY (A141) -- must precede numpy
import numpy as np  # noqa: E402

from caselp import Box, Core, cos_sin_t, t_lo, t_hi          # noqa: E402  READ-ONLY (A57)
import pinclip as PIN                                        # noqa: E402  READ-ONLY (A131)
import polycore as PC                                        # noqa: E402  READ-ONLY (A132)
import exactcore as EC                                       # noqa: E402  READ-ONLY (A135)

S_RAT = Fr(969271, 250000)          # s0 = 3.877084
HALF = Fr(1, 2)
VDEN = 10 ** 9
ADEN_DEFAULT = 1 << 28              # exact-core bisection grid (A135 uses 1<<40; 1<<28 ~ 3.7e-9)


class EmptyBox(Exception):
    """A box lost every pose: the node is dead by the pair leaf."""

    def __init__(self, name, detail=None):
        self.name = name
        self.detail = detail or {}
        super().__init__(f"EmptyBox({name}): every pose is impossible -- the case is dead "
                         f"by the pair leaf")


class InvariantError(Exception):
    """The multi-box invariant does not hold.  `failures` lists every violation found."""

    def __init__(self, failures):
        self.failures = failures
        head = "; ".join(f"{f['check']}:{f['what']}" for f in failures[:6])
        more = "" if len(failures) <= 6 else f" (+{len(failures) - 6} more)"
        super().__init__(f"{len(failures)} invariant failure(s): {head}{more}")


# ==================================================================== exact rational helpers
def _fr(x):
    return x if isinstance(x, Fr) else Fr(str(x)) if isinstance(x, float) else Fr(x)


def sqrt_lo(q, den=1 << 30):
    """rational LOWER bound of sqrt(q) for q >= 0 (exact integer sqrt on a fixed grid)."""
    q = _fr(q)
    if q <= 0:
        return Fr(0)
    n = math.isqrt(int(q * den * den))
    return Fr(n, den)


def _cs_at(t):
    """(cos th, sin th) at t = tan(th/2), exact."""
    return cos_sin_t(t)


def w_min_max(t0, t1):
    """(w_min, w_max) of w(th) = cos th + sin th over the sub-bin, exact rationals; w_max is an
    UPPER bound (sqrt2 is bracketed from above when the bin contains 45 deg)."""
    c0, s0 = _cs_at(t0)
    c1, s1 = _cs_at(t1)
    w0, w1 = c0 + s0, c1 + s1
    wmin = min(w0, w1)                      # w concave on [0,90]: min at an endpoint
    # w_max = sqrt2 iff the bin contains 45 deg, i.e. t = sqrt2 - 1
    tlo = SQ2_LO - 1
    thi = SQ2_HI - 1
    wmax = SQ2_HI if (t0 <= thi and t1 >= tlo) else max(w0, w1)
    return wmin, wmax


SQ2_LO = Fr(1414213562373095048801688, 10 ** 24)      # < sqrt 2
SQ2_HI = SQ2_LO + Fr(1, 10 ** 24)                      # > sqrt 2


def rect_area(rect):
    if rect is None:
        return Fr(0)
    x0, x1, y0, y1 = rect
    if x1 <= x0 or y1 <= y0:
        return Fr(0)
    return (x1 - x0) * (y1 - y0)


def sub_bins(t0, t1, n):
    """n rational t-sub-bins covering [t0, t1] exactly."""
    if t1 <= t0 or n <= 1:
        return [(t0, t1)]
    return [(t0 + (t1 - t0) * Fr(i, n), t0 + (t1 - t0) * Fr(i + 1, n)) for i in range(n)]


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def t_of_deg(d):
    return math.tan(math.radians(d) / 2.0)


# ==================================================================== the obstacle
_OBS_UID = itertools.count(1)               # unique, never-reused obstacle keys (A173 fix)


class Obstacle:
    """A convex rational polygon K contained in every pose of some box, precompiled for the exact
    dead-set test.  `K` is A132's certified K'(B) (mode "poly") or the four corners of A135's exact
    axis core (mode "core"); either is a subset of every pose of B, which is all soundness needs."""

    __slots__ = ("verts", "fV", "edges", "name", "kind", "uid")

    def __init__(self, verts, name="", kind="poly"):
        self.uid = next(_OBS_UID)           # NEVER reused; see Bin.radii (A173 fix)
        self.verts = [(_fr(a), _fr(b)) for (a, b) in verts]
        self.fV = np.array([[float(a), float(b)] for a, b in self.verts])
        self.name = name
        self.kind = kind
        # outward edge normals of the ccw polygon, with the polygon's exact support interval
        E = []
        m = len(self.verts)
        for i in range(m):
            (ax, ay) = self.verts[i]
            (bx, by) = self.verts[(i + 1) % m]
            nx, ny = (by - ay), -(bx - ax)          # outward for ccw
            if nx == 0 and ny == 0:
                continue
            pr = [nx * px + ny * py for (px, py) in self.verts]
            E.append((nx, ny, min(pr), max(pr)))
        self.edges = E


def obstacle_from_poly(pc, name=""):
    return Obstacle(pc.verts, name=name, kind="poly")


def obstacle_from_core(core, name=""):
    v = EC.core_corners(core.kx, core.ky, core.cm, core.sm, core.a)
    # core_corners returns (1,1),(1,-1),(-1,-1),(-1,1) -- that is CLOCKWISE in the core frame;
    # reverse to counter-clockwise so the edge normals point outward.
    return Obstacle(list(reversed(v)), name=name, kind="core")


# ==================================================================== the exact dead-set test
def _radius_lo(nx, ny, c0, s0, c1, s1):
    """rational LOWER bound of  min over the sub-bin of  (|n.u| + |n.v|)/2,  n = (nx, ny).

    n.u = nx cos + ny sin, n.v = -nx sin + ny cos; writing n = |n|(cos phi, sin phi) these are
    |n| cos(th - phi) and -|n| sin(th - phi), so the quantity is |n|(|cos psi| + |sin psi|)/2 with
    psi = th - phi.  |cos| + |sin| has its minima exactly where psi is a multiple of 90 deg, i.e.
    where n.u or n.v vanishes -- an exact sign test on the two endpoints.  If neither changes sign
    the minimum is at an endpoint (exact); otherwise it is |n|/2, for which a rational lower bound
    of |n| is used.  A LOWER bound is the sound direction (see `dead_poly`)."""
    u0 = nx * c0 + ny * s0
    v0 = -nx * s0 + ny * c0
    u1 = nx * c1 + ny * s1
    v1 = -nx * s1 + ny * c1
    if (u0 > 0) != (u1 > 0) or (v0 > 0) != (v1 > 0) or u0 == 0 or u1 == 0 or v0 == 0 or v1 == 0:
        return sqrt_lo(nx * nx + ny * ny) / 2
    e0 = (abs(u0) + abs(v0)) / 2
    e1 = (abs(u1) + abs(v1)) / 2
    return min(e0, e1)


class Bin:
    """one t-sub-bin, with the exact endpoint (cos, sin) and the float twins."""

    __slots__ = ("t0", "t1", "c0", "s0", "c1", "s1", "fc0", "fs0", "fc1", "fs1",
                 "wmin", "wmax", "_rlo")

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
        self.c0, self.s0 = _cs_at(t0)
        self.c1, self.s1 = _cs_at(t1)
        self.fc0, self.fs0 = float(self.c0), float(self.s0)
        self.fc1, self.fs1 = float(self.c1), float(self.s1)
        self.wmin, self.wmax = w_min_max(t0, t1)
        self._rlo = {}

    def radii(self, obs):
        """per-edge rational lower radius bounds, cached per obstacle.

        KEYED BY `obs.uid`, NOT `id(obs)`.  A173 found the bug: `normalise` builds a FRESH obstacle
        per box per pass and drops the previous pass's, so CPython reuses the freed address and a
        long-lived `Bin` would answer the new obstacle with the OLD obstacle's radii -- wrong bounds
        in the exact dead test, in either direction, i.e. UNSOUND.  It bit nondeterministically
        (2 aliases in test (a) alone, which is why `a2.invariant_after` flickered).  `uid` comes
        from a monotone counter, so a key is never reused."""
        key = obs.uid
        r = self._rlo.get(key)
        if r is None:
            r = [_radius_lo(nx, ny, self.c0, self.s0, self.c1, self.s1)
                 for (nx, ny, _lo, _hi) in obs.edges]
            self._rlo[key] = r
        return r


def dead_poly(cx, cy, obs, bn):
    """EXACT, SUFFICIENT: does Q(c, th) meet int K for EVERY th in the sub-bin?  Fractions in.

    Q(c,th) and K are convex, so their interiors meet iff no candidate axis separates them; the
    candidate axes are K's edge normals and the square's own two, u(th) and v(th).  "For every th"
    distributes over the conjunction of axes, so each axis is handled on its own.

      * K's edge normal n (a FIXED rational direction).  K projects to [lo, hi]; the square projects
        to [c.n - r(th), c.n + r(th)] with r(th) = (|n.u| + |n.v|)/2.  Overlap at every th follows
        from  c.n - r_lo < hi  and  c.n + r_lo > lo  with r_lo <= min_th r(th) (`_radius_lo`).
        Using a LOWER bound makes both inequalities harder, i.e. declares FEWER centres dead.

      * the square's own axes u(th), v(th).  K projects to [min_p p.u, max_p p.u] over its vertices;
        overlap is  max_p (p-c).u > -1/2  and  min_p (p-c).u < 1/2.  "for every th" of a max over
        vertices does not distribute, so the sufficient form is used: SOME single vertex p works for
        every th.  Each such statement is one sinusoid inequality over the sub-bin, decided exactly
        by A131's `_m_lt_half` (at most one interior critical point when the bin is under 180 deg;
        the comparison r < 1/2 is done as r^2 < 1/4, so nothing leaves the rationals).

    The result is a SUFFICIENT condition for membership in the true dead set D_K, never the
    converse.  That is what the clip needs in two ways: the slab it removes is justified by
    CONVEXITY OF D_K (four corners in D_K => the rectangle they span is in D_K), and a centre this
    test cannot certify is simply kept."""
    m = PIN._m_lt_half
    c0, s0, c1, s1 = bn.c0, bn.s0, bn.c1, bn.s1
    # --- family A: K's edge normals
    R = bn.radii(obs)
    for k, (nx, ny, lo, hi) in enumerate(obs.edges):
        p = nx * cx + ny * cy
        r = R[k]
        if not (p - r < hi and p + r > lo):
            return False
    # --- family B: the square's own two axes, four one-sided statements
    for (swap, sign) in ((0, 1), (0, -1), (1, 1), (1, -1)):
        ok = False
        for (px, py) in obs.verts:
            P, Q = px - cx, py - cy
            if swap:
                P, Q = Q, -P                  # (p - c).v  =  P' cos + Q' sin  with (P', Q') = (Q, -P)
            if m(sign * P, sign * Q, c0, s0, c1, s1):     # max over th of  sign*(p-c).axis  < 1/2
                ok = True
                break
        if not ok:
            return False
    return True


def _dead_poly_f(cx, cy, obs, bn):
    """float twin of `dead_poly`, used ONLY to search for a slab boundary -- never to decide."""
    m = PIN._m_lt_half_f
    c0, s0, c1, s1 = bn.fc0, bn.fs0, bn.fc1, bn.fs1
    for (nx, ny, lo, hi) in obs.edges:
        fnx, fny = float(nx), float(ny)
        p = fnx * cx + fny * cy
        u0, v0 = fnx * c0 + fny * s0, -fnx * s0 + fny * c0
        u1, v1 = fnx * c1 + fny * s1, -fnx * s1 + fny * c1
        r = min(abs(u0) + abs(v0), abs(u1) + abs(v1)) / 2.0
        if not (p - r < float(hi) and p + r > float(lo)):
            return False
    for (swap, sign) in ((0, 1), (0, -1), (1, 1), (1, -1)):
        ok = False
        for (px, py) in obs.fV:
            P, Q = px - cx, py - cy
            if swap:
                P, Q = Q, -P
            if m(sign * P, sign * Q, c0, s0, c1, s1):
                ok = True
                break
        if not ok:
            return False
    return True


# ==================================================================== the clip of one rect
def _clip_rect_obstacle(rect, obs, bn, stats, trace=None, tag=""):
    """clip a rational rect against ONE obstacle's dead set over ONE sub-bin.  -> rect or None.

    Structurally A131 `pinclip._clip_one_pin`, with the pin octagon replaced by the general exact
    predicate above and A131's `_bisect_boundary` reused verbatim.  Every removal is recorded as a
    replayable step; a checker replays a slab step by verifying the four corners (from/to) x (y0/y1)
    are dead, which proves the slab dead by convexity of the dead set."""
    x0, x1, y0, y1 = rect

    def dq(px, py):
        stats["exact_calls"] += 1
        return dead_poly(px, py, obs, bn)

    def df(px, py):
        return _dead_poly_f(px, py, obs, bn)

    def rec(side, frm, to):
        if trace is not None and to != frm:
            trace.append(dict(op="slab", obs=tag, side=side,
                              **{"from": str(frm)}, to=str(to)))

    if dq(x0, y0) and dq(x1, y0) and dq(x0, y1) and dq(x1, y1):
        if trace is not None:
            trace.append(dict(op="empty", obs=tag, rect=[str(v) for v in rect]))
        return None
    if dq(x0, y0) and dq(x0, y1):
        nx = PIN._bisect_boundary(True, x0, x1,
                                  lambda v: df(v, float(y0)) and df(v, float(y1)),
                                  lambda v: dq(v, y0) and dq(v, y1), stats)
        rec("x0", x0, nx)
        x0 = nx
    if dq(x1, y0) and dq(x1, y1):
        neg = PIN._bisect_boundary(True, -x1, -x0,
                                   lambda v: df(-v, float(y0)) and df(-v, float(y1)),
                                   lambda v: dq(-v, y0) and dq(-v, y1), stats)
        rec("x1", x1, -neg)
        x1 = -neg
    if x1 <= x0:
        if trace is not None:
            trace.append(dict(op="collapse", obs=tag, axis="x"))
        return None
    if dq(x0, y0) and dq(x1, y0):
        ny = PIN._bisect_boundary(True, y0, y1,
                                  lambda v: df(float(x0), v) and df(float(x1), v),
                                  lambda v: dq(x0, v) and dq(x1, v), stats)
        rec("y0", y0, ny)
        y0 = ny
    if dq(x0, y1) and dq(x1, y1):
        neg = PIN._bisect_boundary(True, -y1, -y0,
                                   lambda v: df(float(x0), -v) and df(float(x1), -v),
                                   lambda v: dq(x0, -v) and dq(x1, -v), stats)
        rec("y1", y1, -neg)
        y1 = -neg
    if x1 <= x0 or y1 <= y0:
        if trace is not None:
            trace.append(dict(op="collapse", obs=tag, axis="y"))
        return None
    return (x0, x1, y0, y1)


def split_piece(bn, rect):
    """bisect a piece on its widest coordinate (x, y or t, the t-width weighted 1.5 per 90 deg,
    which is A141 `polylane.split_box`'s convention).  A tautologous split: the two children cover
    the parent exactly, so dropping a child the clip proves DEAD loses nothing."""
    x0, x1, y0, y1 = rect
    wx, wy = x1 - x0, y1 - y0
    wt = (bn.t1 - bn.t0) * Fr(3, 2)
    if wx >= wy and wx >= wt:
        m = (x0 + x1) / 2
        return [(bn, (x0, m, y0, y1)), (bn, (m, x1, y0, y1))]
    if wy >= wt:
        m = (y0 + y1) / 2
        return [(bn, (x0, x1, y0, m)), (bn, (x0, x1, m, y1))]
    m = (bn.t0 + bn.t1) / 2
    return [(Bin(bn.t0, m), rect), (Bin(m, bn.t1), rect)]


def container_clip(rect, bn, s, strict=True, trace=None):
    """(rect|None, sliver_area).  Sound clip at w_min, then -- if `strict` -- the narrowing clip at
    w_max that puts EVERY pose inside [0,s]^2, with the sacrificed sliver's area recorded."""
    x0, x1, y0, y1 = rect
    h = bn.wmin / 2
    nx0, ny0 = max(x0, h), max(y0, h)
    nx1, ny1 = min(x1, s - h), min(y1, s - h)
    if trace is not None and (nx0, nx1, ny0, ny1) != (x0, x1, y0, y1):
        trace.append(dict(op="container", w="min", w_val=str(bn.wmin),
                          rect=[str(v) for v in (nx0, nx1, ny0, ny1)]))
    if nx1 <= nx0 or ny1 <= ny0:
        return None, Fr(0)
    sound = (nx0, nx1, ny0, ny1)
    if not strict:
        return sound, Fr(0)
    H = bn.wmax / 2
    sx0, sy0 = max(nx0, H), max(ny0, H)
    sx1, sy1 = min(nx1, s - H), min(ny1, s - H)
    if sx1 <= sx0 or sy1 <= sy0:
        if trace is not None:
            trace.append(dict(op="container_sliver", w="max", w_val=str(bn.wmax),
                              sliver_area=str(rect_area(sound)), rect=None))
        return None, rect_area(sound)
    strict_rect = (sx0, sx1, sy0, sy1)
    sl = rect_area(sound) - rect_area(strict_rect)
    if sl > 0 and trace is not None:
        trace.append(dict(op="container_sliver", w="max", w_val=str(bn.wmax),
                          sliver_area=str(sl), rect=[str(v) for v in strict_rect]))
    return strict_rect, sl


# ==================================================================== THE LONELY CLIP  (A173)
#
# WHY (PI, 2026-09-09).  A169's Theorem B (`docs/proofs/sideband.md` sec 3, consumption row R3 in
# sec 6) says that a corner meeter pose admitting NO second meeter of the widened corner box -- a
# LONELY pose -- is IMPOSSIBLE in a K0-BLOCKED packing: if such a pose occurred, that corner would
# be met by one square only at the widened box, and K0-WIDEN + K0-FREE kill the packing.  So the
# lonely set L_{c'} is a NO-family at the root of the tree, hence at every node, and R3's stated
# consumption is "(iii) a conditioned box B_H is clipped to B_H \ L_{c'}" -- a CLIP.
#
# A168 consumes it only as a whole-role KILL (`resume168.lonely_role`: every piece of the role must
# be lonely).  A role that is 90 % lonely therefore keeps all of its poses, its K' never grows from
# them, and the cascade into the other boxes is lost.  The coordinator's measurement on the TR
# corner shows the granularity is much finer than a role: an axis-aligned D flush with the right
# wall slid down any amount is NOT lonely (a partner exists in the top band left of it), while D at
# tilt 15 deg slid 0.1, or D at tilt 30 deg pressed, IS lonely.  What Theorem B removes is TILT
# SUB-BINS AND CENTRE SLABS.
#
# WHAT THIS CODE IS.  `lonely_local` is a PORT of `resume168.lonely_box` -- the maths copied, with
# attribution, never imported at runtime (A168 is read-only, and a library must not depend on an
# attempt).  `tests/test_multibox.py` case (f) cross-checks the port against `resume168.lonely_box`
# on 500 random boxes and requires IDENTICAL verdicts.  The criterion, in BL-local coordinates of
# the corner (a reflection; a single reflection also maps th -> 90 - th):
#
#   (W)  fails everywhere on the box  <=  for all z in [0, 90]:
#        -x1 sin z + y0 cos z + g_min(z + 90) >= c cos z - sin^2 z
#   (S)  the mirror image, with (y1, x0);
#   (NE) fails everywhere            <=  for all a: x0 cos a + y0 sin a + g_min(a) >= c(cos a + sin a)
#   (P)  fails                       <=  the pressed square [0,1]^2 is NOT a second meeter, i.e.
#        EVERY pose of the box has interior meeting int [0,1]^2 -- decided by A131's exact clip of
#        the centre rect against the axis core (1/2, 1/2, 1/2 - 1e-6) per tilt sub-bin: the clip
#        returning EMPTY means every centre is dead against that core, i.e. every pose meets it.
#
# with g_min(n) >= 1/2 a lower bound of the half-width w(angle - th)/2 over the box's tilt range
# (Lipschitz margin 1/sqrt2 in th), and the three one-parameter inequalities decided on a
# 2001-point z-grid with a Lipschitz margin.  A168 tags the clause grid [S] (supported, not [T]);
# THE CLIP INHERITS EXACTLY THAT GRADE -- no better and no worse than the R3 kills A168 has already
# booked.  The (P) clause is exact (A131 rational arithmetic).
#
# WHY THE CLIP IS SOUND.  `lonely_rect` is a SUFFICIENT condition for "every pose of the piece is
# lonely" (each clause is checked with the box corner that minimises it and a lower bound of g, so a
# TRUE verdict certifies the whole piece).  Hence: a slab the test calls lonely contains only
# impossible poses and may be removed; a slab it cannot certify is KEPT.  That is the sound
# direction, and it is why the slab is tested DIRECTLY (unlike the mutual clip, which tests four
# corner points and appeals to convexity of the dead set -- the lonely set is not convex).
# Monotonicity, which is what makes the bisection legal: SHRINKING the rect raises every clause
# function (x1, y1 decrease and x0, y0 increase, all with nonnegative coefficients) and NARROWING
# the tilt bin raises g_min and enlarges (P)'s dead set, so every sub-rect and sub-bin of a
# certified-lonely piece is itself certified lonely.
#
# The constant c: the K0-WIDEN box side 1 + w, reproduced here EXACTLY as A168's `cas168.W0_RAT`
# (A141's float pad rounded up to a rational, so the box is never narrower than the float one).
WLO_A168 = Fr(382, 100)                                   # cas168.WLO
LAM_MAX_A168 = S_RAT / WLO_A168                           # cas168.LAM_MAX
W0_RAT = (LAM_MAX_A168 - 1) * (1 + 1 / SQ2_LO)            # cas168.W0_RAT  = 0.0255100742139405...
C_WIDEN = 1 + W0_RAT                                      # resume168.C_RAT
C_UNIT = Fr(1)

INV_SQ2 = 1.0 / math.sqrt(2.0)
_ZGRID = np.linspace(0.0, 0.5 * math.pi, 2001)            # resume168.GRID
_COSG, _SING = np.cos(_ZGRID), np.sin(_ZGRID)
_HSTEP = float(_ZGRID[1] - _ZGRID[0])
_GCACHE = {}
PRESSED_CORE = (Fr(1, 2), Fr(1, 2), Fr(1, 2) - Fr(1, 10 ** 6))    # resume168's pressed-square pin
CORNERS = ("BL", "BR", "TR", "TL")


def _new_lonely_stats():
    return dict(clause_calls=0, p_calls=0, drops=0, slabs=0, exact_calls=0, backoffs=0)


def _clause_fails_everywhere(f, L):
    """PORT of resume168._clause_fails_everywhere: f >= 0 on the whole interval, with the sound
    Lipschitz margin L*h/2 for the 2001-point grid."""
    return bool(np.all(f >= 0.5 * L * _HSTEP + 1e-9))


def _gmin(angle_grid, th0, th1, nth=64):
    """PORT of resume168._gmin: lower bound of g(n) = (|cos(alpha - th)| + |sin(alpha - th)|)/2 over
    th in [th0, th1] (degrees), per grid angle alpha (radians) -- a th-grid minimum minus the
    Lipschitz margin (|dg/dth| <= 1/sqrt2), never below 1/2."""
    ths = np.radians(np.linspace(th0, th1, nth)) if th1 > th0 else np.radians(np.array([th0]))
    ph = angle_grid[:, None] - ths[None, :]
    g = 0.5 * (np.abs(np.cos(ph)) + np.abs(np.sin(ph))).min(axis=1)
    hth = (ths[1] - ths[0]) if len(ths) > 1 else 0.0
    return np.maximum(0.5, g - 0.5 * INV_SQ2 * hth)


def _gtriple(th0, th1):
    """(gW, gS, gN) for one local tilt range, cached (they depend on the tilt bin only)."""
    key = (th0, th1)
    v = _GCACHE.get(key)
    if v is None:
        v = (_gmin(_ZGRID + 0.5 * math.pi, th0, th1),           # n_W(z)  = (-sin z, cos z)
             _gmin(-_ZGRID, th0, th1),                          # n_S(z)  = (cos z, -sin z)
             _gmin(_ZGRID, th0, th1))                           # n_NE(a) = (cos a, sin a)
        if len(_GCACHE) > 8192:
            _GCACHE.clear()
        _GCACHE[key] = v
    return v


def _pressed_not_a_meeter(x0, x1, y0, y1, th0, th1, nsub=4, s=None):
    """clause (P) FAILS on the whole box: the pressed square [0,1]^2 is not a second meeter, i.e.
    every pose of the box has interior meeting int [0,1]^2.  PORT of resume168.lonely_box's (P)
    branch, which is `roles168.clip_piece(piece, [pressed core])` returning EMPTY on every tilt
    sub-bin -- A131's exact rational clip against the axis core (1/2, 1/2, 1/2 - 1e-6).

    A DEGENERATE rect (a slab boundary probe, zero width) is padded OUTWARD by 1e-12 first: A131's
    clip reports an empty rect for a degenerate input, which would be read as 'dead' and would be
    UNSOUND here.  The pad only ever enlarges the box, so the verdict stays sufficient, and it
    leaves every non-degenerate box (every box the A168 cross-check sees) bit-identical."""
    s = S_RAT if s is None else s
    if x1 <= x0:
        x1 = x0 + 1e-12
    if y1 <= y0:
        y1 = y0 + 1e-12
    kx, ky, a = PRESSED_CORE
    edges = ([th0 + (th1 - th0) * k / nsub for k in range(nsub + 1)] if th1 > th0
             else [th0, th1])
    for k in range(len(edges) - 1):
        b = Box(x0, x1, y0, y1, edges[k], edges[k + 1])
        t0, t1 = t_lo(b.th0), t_hi(b.th1)
        o = PIN.Oct(t0, t1, a)
        rect, _ = PIN.clip_rect(PIN.outer_rect(b), [(kx, ky)], o, s)
        if rect is None:
            continue
        cx0, cx1 = max(b.x0, float(rect[0])), min(b.x1, float(rect[1]))
        cy0, cy1 = max(b.y0, float(rect[2])), min(b.y1, float(rect[3]))
        if cx1 > cx0 and cy1 > cy0:
            return False                                       # a surviving centre => (P) may hold
    return True


def lonely_local(x0, x1, y0, y1, th0, th1, c=None, nsub=4, s=None, stats=None):
    """SOUND: every pose with centre in [x0,x1] x [y0,y1] and tilt in [th0, th1] (DEGREES) is LONELY
    at the widened box of side c, the box given in BL-LOCAL coordinates of its corner.

    PORT of `attempts/A168-cascade-fable/code/resume168.py::lonely_box` (A169 Theorem B, clauses
    (W), (S), (NE), (P)), identical in its arithmetic; the only differences are the degenerate pad
    in (P) documented above and the cached g's.  Returns (bool, detail)."""
    c = float(C_WIDEN if c is None else c)
    if stats is not None:
        stats["clause_calls"] += 1
    gW, gS, gN = _gtriple(th0, th1)
    det = {}
    fW = -x1 * _SING + y0 * _COSG + gW - c * _COSG + _SING ** 2
    det["W"] = _clause_fails_everywhere(fW, x1 + y0 + c + 1.0 + INV_SQ2)
    fS = -y1 * _SING + x0 * _COSG + gS - c * _COSG + _SING ** 2
    det["S"] = _clause_fails_everywhere(fS, y1 + x0 + c + 1.0 + INV_SQ2)
    fN = x0 * _COSG + y0 * _SING + gN - c * (_COSG + _SING)
    det["NE"] = _clause_fails_everywhere(fN, x0 + y0 + 2 * c + INV_SQ2)
    if not (det["W"] and det["S"] and det["NE"]):
        det["P"] = None
        return False, det
    if stats is not None:
        stats["p_calls"] += 1
    det["P"] = _pressed_not_a_meeter(x0, x1, y0, y1, th0, th1, nsub=nsub, s=s)
    return bool(det["P"]), det


def to_local(x0, x1, y0, y1, t0, t1, corner, s=S_RAT):
    """the piece in BL-local coordinates of `corner` (distance from that corner's two walls), EXACT.
    PORT of resume168.to_local; the tilt reflection th -> 90 - th is done on t = tan(th/2) by
    t -> (1 - t)/(1 + t) (= tan(45 - th/2)), which is exact on the rationals."""
    rx = corner in ("BR", "TR")
    ry = corner in ("TL", "TR")
    if rx:
        x0, x1 = s - x1, s - x0
    if ry:
        y0, y1 = s - y1, s - y0
    if rx != ry:
        t0, t1 = (1 - t1) / (1 + t1), (1 - t0) / (1 + t0)
    return x0, x1, y0, y1, t0, t1


def lonely_rect(rect, bn, corner, c=None, s=S_RAT, nsub=4, stats=None):
    """SOUND: every pose of the piece (rational centre rect x the t-sub-bin `bn`) is LONELY at
    `corner`.  The rational piece is reflected into the corner's local frame EXACTLY and then
    rounded OUTWARD into the floats `lonely_local` consumes: a larger rect and a wider tilt range
    only make the criterion harder to satisfy, so a TRUE verdict still certifies the true piece."""
    lx0, lx1, ly0, ly1, lt0, lt1 = to_local(_fr(rect[0]), _fr(rect[1]), _fr(rect[2]), _fr(rect[3]),
                                            bn.t0, bn.t1, corner, s=s)
    th0 = math.nextafter(deg_of_t(lt0), -math.inf)
    th1 = math.nextafter(deg_of_t(lt1), math.inf)
    ok, _det = lonely_local(_f_down(lx0), _f_up(lx1), _f_down(ly0), _f_up(ly1), th0, th1,
                            c=c, nsub=nsub, s=s, stats=stats)
    return ok


def lonely_box(box, corner, c=None, nsub=4, s=S_RAT):
    """the cross-check entry point: `resume168.lonely_box`'s signature on a caselp.Box in CONTAINER
    coordinates and DEGREES.  Returns (bool, detail)."""
    sr = _fr(s)
    lx0, lx1, ly0, ly1, _t0, _t1 = to_local(_fr(box.x0), _fr(box.x1), _fr(box.y0), _fr(box.y1),
                                            Fr(0), Fr(0), corner, s=sr)
    if (corner in ("BR", "TL")):
        th0, th1 = 90.0 - box.th1, 90.0 - box.th0
    else:
        th0, th1 = box.th0, box.th1
    return lonely_local(float(lx0), float(lx1), float(ly0), float(ly1), th0, th1,
                        c=c, nsub=nsub, s=sr)


# -------------------------------------------------------------------- the slab clip
def _clip_rect_lonely(rect, bn, corner, c, s, nsub, stats, trace=None):
    """clip ONE piece's centre rect by the lonely set over its own tilt sub-bin.  -> rect or None.

    Structurally A171's `_clip_rect_obstacle` / A131's `_clip_one_pin`, with the point-wise dead
    test replaced by the RECT-WISE `lonely_rect` (the lonely set is not convex, so the slab must be
    certified as a whole, not by its four corners).  `PIN._bisect_boundary` is reused verbatim: it
    finds the largest v with the predicate true and CERTIFIES the returned value, so what is dropped
    is always a slab the criterion has just proved lonely."""
    x0, x1, y0, y1 = rect

    def L(a, b, cc, dd):
        return lonely_rect((a, b, cc, dd), bn, corner, c=c, s=s, nsub=nsub, stats=stats)

    def rec(side, frm, to):
        if trace is not None and to != frm:
            stats["slabs"] += 1
            trace.append(dict(op="lonely_slab", corner=corner, side=side,
                              **{"from": str(frm)}, to=str(to)))

    if L(x0, x1, y0, y1):
        stats["drops"] += 1
        if trace is not None:
            trace.append(dict(op="lonely_empty", corner=corner,
                              rect=[str(v) for v in rect]))
        return None
    if L(x0, x0, y0, y1):
        nx = PIN._bisect_boundary(True, x0, x1, lambda v: L(x0, _fr(v), y0, y1),
                                  lambda v: L(x0, v, y0, y1), stats)
        rec("x0", x0, nx)
        x0 = nx
    if L(x1, x1, y0, y1):
        neg = PIN._bisect_boundary(True, -x1, -x0, lambda v: L(_fr(-v), x1, y0, y1),
                                   lambda v: L(-v, x1, y0, y1), stats)
        rec("x1", x1, -neg)
        x1 = -neg
    if x1 <= x0:
        if trace is not None:
            trace.append(dict(op="lonely_collapse", corner=corner, axis="x"))
        return None
    if L(x0, x1, y0, y0):
        ny = PIN._bisect_boundary(True, y0, y1, lambda v: L(x0, x1, y0, _fr(v)),
                                  lambda v: L(x0, x1, y0, v), stats)
        rec("y0", y0, ny)
        y0 = ny
    if L(x0, x1, y1, y1):
        neg = PIN._bisect_boundary(True, -y1, -y0, lambda v: L(x0, x1, _fr(-v), y1),
                                   lambda v: L(x0, x1, -v, y1), stats)
        rec("y1", y1, -neg)
        y1 = -neg
    if x1 <= x0 or y1 <= y0:
        if trace is not None:
            trace.append(dict(op="lonely_collapse", corner=corner, axis="y"))
        return None
    return (x0, x1, y0, y1)


def lonely_clip(mbox, corner, c=None, s=S_RAT, nsub=4, refine=0, max_pieces=192, stats=None,
                pass_=None):
    """THE LONELY CLIP.  Remove from `mbox`'s pieces every centre slab and tilt sub-bin that
    Theorem B certifies LONELY at `corner` for the box of side `c` (default the K0-WIDEN 1 + w).

    Every removal is justified by R3: a lonely pose is impossible in a K0-BLOCKED packing, so the
    surviving pieces still contain every possible pose of the box -- the same soundness contract as
    the container and mutual clips.  With `refine > 0` a piece that is only PARTLY lonely first has
    its tilt sub-bin bisected (tautologous: the two halves cover the parent exactly), which is what
    catches "lonely above 15 deg, not below".

    Raises `EmptyBox(name)` if the box loses every piece -- that is A168's R3 KILL, recovered as the
    limiting case of the clip.  Returns a report dict."""
    c = C_WIDEN if c is None else c
    st = _new_lonely_stats() if stats is None else stats
    rep = dict(box=mbox.name, corner=corner, c=float(c),
               area_before=float(sum(rect_area(r) * (b.t1 - b.t0) for (b, r) in mbox.pieces)),
               n_before=len(mbox.pieces), dropped_pieces=0, split=0)
    work = list(mbox.pieces)
    # --- tautologous tilt refinement, dropping the halves that are wholly lonely
    for _lvl in range(max(0, refine)):
        if len(work) * 2 > max_pieces:
            break
        new = []
        for (bn, r) in work:
            m = (bn.t0 + bn.t1) / 2
            for b2 in (Bin(bn.t0, m), Bin(m, bn.t1)):
                if lonely_rect(r, b2, corner, c=c, s=s, nsub=nsub, stats=st):
                    st["drops"] += 1
                    rep["dropped_pieces"] += 1
                    mbox.trace.append(dict(
                        lonely=True, pass_=pass_, t=[str(b2.t0), str(b2.t1)],
                        steps=[dict(op="lonely_empty", corner=corner,
                                    rect=[str(v) for v in r],
                                    area=float(rect_area(r) * (b2.t1 - b2.t0)))]))
                    continue
                new.append((b2, r))
        rep["split"] += 1
        work = new
        if not work:
            break
    # --- the slab clip on every surviving piece
    keep = []
    for (bn, r) in work:
        tr = []
        nr = _clip_rect_lonely(r, bn, corner, c, s, nsub, st, trace=tr)
        if tr:
            lost = float((rect_area(r) - rect_area(nr)) * (bn.t1 - bn.t0))
            for stp in tr:
                stp["area"] = lost
            mbox.trace.append(dict(lonely=True, pass_=pass_, t=[str(bn.t0), str(bn.t1)], steps=tr))
        if nr is None:
            rep["dropped_pieces"] += 1
            continue
        keep.append((bn, nr))
    mbox.pieces = keep
    rep["n_after"] = len(keep)
    rep["area_after"] = float(sum(rect_area(r) * (b.t1 - b.t0) for (b, r) in keep))
    rep["removed"] = rep["area_before"] - rep["area_after"]
    rep["stats"] = dict(st)
    mbox.lonely_removed = getattr(mbox, "lonely_removed", 0.0) + rep["removed"]
    if not keep:
        raise EmptyBox(mbox.name, dict(reason="lonely", corner=corner, c=float(c),
                                       rule="A169 Theorem B / R3 (sideband.md sec 3, sec 6)"))
    return rep


# ==================================================================== K' FROM THE PIECES  (A172)
#
# WHY (A172, PI finding).  `MBox.rebuild` used to recompute K'(B) from `union_box()` -- the smallest
# axis box x tilt hull containing every surviving piece.  That hull FORGETS the shape of the
# survivors: a clip that removes different slabs in different tilt sub-bins barely moves the hull,
# so K' barely grows on the side opposite the clip, and the cascade (a larger K'(B) clips the other
# boxes harder) is much weaker than the truth.  On A168's S2 node after normalise(nsub=4, refine=3)
# the union hull gives K' areas H 0.658 / B1 0.798 / D 0.740 where the exact intersection of the
# per-piece K' gives H 0.709336 / B1 0.799343 / D 0.774356, and one further clip pass with the
# per-piece obstacles takes the kept fractions H 0.4408 -> 0.3816 and D 0.0882 -> 0.0725.
#
# WHAT IS PROVED, AND BY WHAT.  K'(B) has to be a convex set contained in EVERY pose of B.  The
# proof is NOT the construction -- it is `polycore.vertex_ok`, run on EVERY vertex of the result
# against EVERY piece (exact rational, two quadratics in t per corner per edge normal).  A vertex
# that passes lies in Q(c, th) for every (c, th) in that piece's box; the pieces cover every
# surviving pose; Q(c, th) is convex, so the convex hull of certified vertices lies in every pose.
# The per-piece polygons, their exact intersection and the inward simplification are only how a good
# candidate is FOUND.  Every step of the search is nevertheless kept sound-by-shape:
#
#   * `piece_box` rounds the piece's six coordinates OUTWARD (float, then nextafter) so the Box
#     handed to A132 CONTAINS the rational piece -- a narrower box would certify too much;
#   * the intersection is Sutherland-Hodgman in Fractions (no floats, no epsilons);
#   * `_simplify_frac` only ever DELETES a vertex of a convex polygon, which cuts a triangle OFF --
#     inward, never outward;
#   * the final rounding to the 1e-9 grid is done after an inward shrink about the centroid, and if
#     the rounded polygon does not certify the shrink is raised (the same retry ladder A132 uses).
#
# The union-hull K' is kept as `MBox.union_pc()` -- the fallback when the per-piece build cannot be
# certified, and the diagnostic the A172 test measures against.
def _f_down(v):
    """the largest float <= the exact rational v."""
    f = float(v)
    return f if Fr(f) <= v else math.nextafter(f, -math.inf)


def _f_up(v):
    """the smallest float >= the exact rational v."""
    f = float(v)
    return f if Fr(f) >= v else math.nextafter(f, math.inf)


def piece_box(bn, rect):
    """(Box, t0, t1) for one piece, the Box CONTAINING it: floats rounded outward, and the t
    interval A132 will actually use (`t_lo/t_hi` of the degree endpoints) asserted to contain the
    piece's own rational sub-bin."""
    x0, x1, y0, y1 = rect
    b = Box(_f_down(x0), _f_up(x1), _f_down(y0), _f_up(y1), deg_of_t(bn.t0), deg_of_t(bn.t1))
    pt0, pt1 = t_lo(b.th0), t_hi(b.th1)
    if not (pt0 <= bn.t0 and pt1 >= bn.t1):
        raise RuntimeError(f"piece_box: t interval [{pt0},{pt1}] does not contain "
                           f"[{bn.t0},{bn.t1}]")
    return b, pt0, pt1


def _clip_frac(poly, nx, ny, b):
    """Sutherland-Hodgman clip of a convex rational polygon by  nx*x + ny*y <= b.  EXACT."""
    if not poly:
        return poly
    out = []
    m = len(poly)
    for i in range(m):
        px, py = poly[i]
        qx, qy = poly[(i + 1) % m]
        dp = nx * px + ny * py - b
        dq = nx * qx + ny * qy - b
        if dp <= 0:
            out.append((px, py))
        if (dp > 0) != (dq > 0):
            t = dp / (dp - dq)
            out.append((px + t * (qx - px), py + t * (qy - py)))
    return out


def _dedupe_frac(P):
    out = []
    for p in P:
        if not out or p != out[-1]:
            out.append(p)
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def _tri2_frac(a, b, c):
    return abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _simplify_frac(P, max_v):
    """delete vertices of a convex ccw polygon until it has at most `max_v` of them.  Deleting a
    vertex REMOVES the triangle it spans with its neighbours: the polygon can only shrink, never
    grow, so the result stays inside every pose that contained the original."""
    P = _dedupe_frac(list(P))
    while len(P) > 3:
        m = len(P)
        ar = [_tri2_frac(P[(i - 1) % m], P[i], P[(i + 1) % m]) for i in range(m)]
        j = min(range(m), key=lambda i: ar[i])
        if len(P) > max_v or ar[j] == 0:
            P.pop(j)
        else:
            break
    return P


def poly_area_frac(P):
    """exact rational area of a simple polygon."""
    a = Fr(0)
    m = len(P)
    for i in range(m):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % m]
        a += x0 * y1 - x1 * y0
    return abs(a) / 2


def intersect_frac(polys, max_v=16, work_v=28):
    """EXACT intersection of convex ccw rational polygons ([] if empty or degenerate)."""
    if not polys:
        return []
    P = list(polys[0])
    for Q in polys[1:]:
        m = len(Q)
        for i in range(m):
            ax, ay = Q[i]
            bx, by = Q[(i + 1) % m]
            nx, ny = (by - ay), -(bx - ax)              # outward normal of a ccw polygon
            if nx == 0 and ny == 0:
                continue
            P = _clip_frac(P, nx, ny, nx * ax + ny * ay)
            if len(P) < 3:
                return []
        P = _simplify_frac(P, work_v)
        if len(P) < 3:
            return []
    return _simplify_frac(P, max_v)


def _round_grid_inward(P, shrink, den=VDEN):
    """shrink the polygon about its centroid by the factor `shrink`, then round every vertex to the
    1/den grid and re-hull.  The rounding can move a vertex outward by at most 1/(2 den) per
    coordinate, which is why the caller certifies afterwards and raises `shrink` on failure."""
    n = len(P)
    cx = sum(p[0] for p in P) / n
    cy = sum(p[1] for p in P) / n
    out = []
    for (x, y) in P:
        x = cx + (x - cx) * (1 - shrink)
        y = cy + (y - cy) * (1 - shrink)
        out.append((Fr(round(x * den), den), Fr(round(y * den), den)))
    return PC._hull_frac(_dedupe_frac(out))


K_SHRINKS = (Fr(0), Fr(1, 10 ** 8), Fr(1, 10 ** 6), Fr(1, 10 ** 4), Fr(1, 10 ** 3))


def certify_verts(verts, boxes):
    """[i] of the vertices NOT certified inside every pose of every piece.  This is the proof."""
    bad = []
    for i, (vx, vy) in enumerate(verts):
        for (pb, pt0, pt1) in boxes:
            if not PC.vertex_ok(vx, vy, pb, pt0, pt1):
                bad.append(i)
                break
    return bad


def pieces_poly(pieces, n_grid=97, max_v=16, cache=None):
    """K'(B) as the certified exact intersection of the per-piece K'.  -> (verts|None, info).

    `cache` is an optional dict keyed by the piece, so that the pieces a clip pass leaves untouched
    are not rebuilt (the fixed-point loop rebuilds K' after every pass)."""
    boxes, polys = [], []
    for (bn, r) in pieces:
        pb, pt0, pt1 = piece_box(bn, r)
        boxes.append((pb, pt0, pt1))
        key = (bn.t0, bn.t1, r, n_grid, max_v)
        pc = None if cache is None else cache.get(key)
        if pc is None:
            pc = PC.build(pb, n_grid=n_grid, max_v=max_v)
            if cache is not None:
                cache[key] = pc
        polys.append(pc.verts)
    P = intersect_frac(polys, max_v=max_v)
    if len(P) < 3:
        return None, dict(reason="empty intersection", n_pieces=len(pieces)), boxes
    for sh in K_SHRINKS:
        V = _round_grid_inward(P, sh)
        if len(V) < 3:
            continue
        if not certify_verts(V, boxes):
            return V, dict(shrink=str(sh), shrink_f=float(sh), n_pieces=len(pieces), nv=len(V),
                           area=float(poly_area_frac(V))), boxes
    return None, dict(reason="no certified rounding", n_pieces=len(pieces)), boxes


def axis_core_pieces(V, boxes, tm, aden=ADEN_DEFAULT, den=VDEN):
    """the largest square at tilt tm about the CENTROID of V that fits inside V, its four corners
    then certified against every piece (A135's pattern: the formula is the search, `vertex_ok` is
    the proof).  -> (kx, ky, a) or None.

    Inside a convex polygon the largest such square about a fixed centre k is exact:
    a = min over the edges (b_e - n_e.k) / (|n_e.e1| + |n_e.e2|), e1 = (cos tm, sin tm),
    e2 = (-sin tm, cos tm) -- the support of the square in the direction n_e is a(|n.e1| + |n.e2|)."""
    n = len(V)
    kx = Fr(round(sum(p[0] for p in V) / n * den), den)
    ky = Fr(round(sum(p[1] for p in V) / n * den), den)
    cm, sm = _cs_at(tm)
    a = None
    for i in range(n):
        ax, ay = V[i]
        bx, by = V[(i + 1) % n]
        nx, ny = (by - ay), -(bx - ax)
        if nx == 0 and ny == 0:
            continue
        slack = (nx * ax + ny * ay) - (nx * kx + ny * ky)
        if slack <= 0:
            return None                                   # the centroid is not strictly inside
        sup = abs(nx * cm + ny * sm) + abs(-nx * sm + ny * cm)
        if sup <= 0:
            continue
        v = slack / sup
        a = v if a is None else min(a, v)
    if a is None or a <= 0:
        return None
    a = Fr(math.floor(a * aden), aden)
    for _try in range(4):
        if a <= 0:
            return None
        if not certify_verts(EC.core_corners(kx, ky, cm, sm, a), boxes):
            return kx, ky, a
        a = Fr(int(a * aden) * 999999 // 1000000, aden)
    return None


# ==================================================================== a box of the node
class MBox:
    """one named box of a Node: its pieces, its certified polygon core, its exact axis core."""

    def __init__(self, name, box):
        self.name = name
        self.box0 = box                              # the box as handed in (never mutated)
        t0, t1 = t_lo(box.th0), t_hi(box.th1)
        self.t0, self.t1 = t0, t1
        self.pieces = [(Bin(t0, t1), PIN.outer_rect(box))]
        self.pc = None                               # K'(B): A172's per-piece intersection
        self.core = None                             # the exact axis core (A135's pattern)
        self.obs = None                              # the compiled obstacle
        self.kept = 1.0
        self.trace = []
        self.sliver_area = Fr(0)
        self.area0 = rect_area(PIN.outer_rect(box)) * (t1 - t0)
        self.kmode = "pieces"                        # "pieces" (A172) or "union" (A171 fallback)
        self.k_source = None                         # what the CURRENT pc/core actually came from
        self.k_info = {}
        self._pcache = {}                            # per-piece K', keyed by the piece

    # ---------------------------------------------------------------- geometry
    def union_box(self):
        """the smallest caselp.Box containing every surviving piece (tilt hull included)."""
        if not self.pieces:
            return None
        xs0 = min(r[0] for (_b, r) in self.pieces)
        xs1 = max(r[1] for (_b, r) in self.pieces)
        ys0 = min(r[2] for (_b, r) in self.pieces)
        ys1 = max(r[3] for (_b, r) in self.pieces)
        tt0 = min(b.t0 for (b, _r) in self.pieces)
        tt1 = max(b.t1 for (b, _r) in self.pieces)
        return Box(float(xs0), float(xs1), float(ys0), float(ys1),
                   deg_of_t(tt0), deg_of_t(tt1))

    def union_pc(self, n_grid=97, max_v=16, aden=ADEN_DEFAULT):
        """A171's K': A132's polygon on the UNION HULL of the surviving pieces.  Kept as the
        fallback and as the diagnostic A172 measures the per-piece K' against.  -> (pc, core)."""
        b = self.union_box()
        if b is None:
            raise EmptyBox(self.name)
        self.ubox = b
        pc = PC.build(b, n_grid=n_grid, max_v=max_v)
        return pc, self.union_core(b, aden=aden)

    @staticmethod
    def union_core(b, aden=ADEN_DEFAULT):
        """A135's exact axis core of the union hull (never smaller than the stock core)."""
        try:
            return EC.exact_core(b, aden=aden)
        except Exception:
            return b.core()

    def piece_boxes(self):
        """[(Box, t0, t1)] -- one outward-rounded Box per surviving piece."""
        return [piece_box(bn, r) for (bn, r) in self.pieces]

    def rebuild(self, n_grid=97, max_v=16, aden=ADEN_DEFAULT, kmode=None):
        """recompute K'(B) and the exact axis core from the SURVIVING pieces.

        kmode "pieces" (A172, the default): K' is the EXACT intersection of the per-piece K',
        every vertex re-certified with `polycore.vertex_ok` against EVERY piece, and the axis core
        is the largest square about that polygon's centroid whose corners certify the same way.
        kmode "union" (A171): K' is A132's polygon on the union hull of the pieces -- sound, but it
        forgets everything the clip removed unevenly across the tilt sub-bins, so it is only the
        fallback (used automatically when the per-piece build will not certify) and the diagnostic.
        """
        kmode = self.kmode if kmode is None else kmode
        b = self.union_box()
        if b is None:
            raise EmptyBox(self.name)
        self.ubox = b
        if kmode == "pieces":
            V, info, boxes = pieces_poly(self.pieces, n_grid=n_grid, max_v=max_v,
                                         cache=self._pcache)
            if V is not None:
                stock = b.core()
                tm = stock.tm if stock is not None else Fr(0)
                ac = axis_core_pieces(V, boxes, tm, aden=aden)
                core_u = self.union_core(b, aden=aden)
                self.pc = PC.PolyCore(b, V, n_grid, info["shrink_f"], True)
                if ac is not None and (core_u is None or ac[2] >= core_u.a):
                    self.core = Core(ac[0], ac[1], tm, ac[2], None)
                    info["axis"] = "pieces"
                else:                     # never regress on the deployed core: both are sound
                    self.core = core_u
                    info["axis"] = "union"
                info["axis_a"] = float(self.core.a) if self.core is not None else None
                self.k_source, self.k_info = "pieces", info
                return self.pc
            self.k_info = dict(info)
            self.k_info["fallback"] = "union"
        self.pc, self.core = self.union_pc(n_grid=n_grid, max_v=max_v, aden=aden)
        self.k_source = "union" if kmode == "union" else "union(fallback)"
        return self.pc

    def obstacle(self, mode="poly"):
        return (obstacle_from_poly(self.pc, self.name) if mode == "poly"
                else obstacle_from_core(self.core, self.name))

    def kept_fraction(self):
        if self.area0 <= 0:
            return 0.0
        v = sum(rect_area(r) * (b.t1 - b.t0) for (b, r) in self.pieces)
        return float(v / self.area0)

    def sample(self, n, rng):
        """(C, TH) uniform over the surviving pieces (t uniform inside each sub-bin)."""
        if not self.pieces:
            return np.zeros((0, 2)), np.zeros(0)
        wts = np.array([float(rect_area(r) * (b.t1 - b.t0)) for (b, r) in self.pieces])
        if wts.sum() <= 0:
            wts = np.ones(len(self.pieces))
        wts = wts / wts.sum()
        idx = rng.choice(len(self.pieces), size=n, p=wts)
        C = np.zeros((n, 2))
        TH = np.zeros(n)
        for k, (bn, r) in enumerate(self.pieces):
            sel = np.flatnonzero(idx == k)
            if not len(sel):
                continue
            x0, x1, y0, y1 = (float(v) for v in r)
            C[sel, 0] = rng.uniform(x0, x1, len(sel))
            C[sel, 1] = rng.uniform(y0, y1, len(sel))
            t = rng.uniform(float(bn.t0), float(bn.t1), len(sel))
            TH[sel] = 2.0 * np.arctan(t)
        return C, TH

    def to_json(self):
        return dict(name=self.name, box0=self.box0.to_json(),
                    union_box=(self.ubox.to_json() if getattr(self, "ubox", None) else None),
                    kept=self.kept, n_pieces=len(self.pieces),
                    sliver_area=float(self.sliver_area),
                    lonely_removed=float(getattr(self, "lonely_removed", 0.0)),
                    k_source=self.k_source, k_info=self.k_info,
                    axis_a=(float(self.core.a) if self.core is not None else None),
                    poly_area=(self.pc.area() if self.pc is not None else None),
                    pieces=[dict(t0=str(b.t0), t1=str(b.t1),
                                 th=[deg_of_t(b.t0), deg_of_t(b.t1)],
                                 rect=[str(v) for v in r]) for (b, r) in self.pieces],
                    trace=self.trace)


# ==================================================================== the node
def mk_box(x0, x1, y0, y1, a, b, t=False):
    """a caselp.Box from (x0,x1,y0,y1) and either a DEGREE tilt interval or (t=True) a t-interval."""
    if t:
        return Box(x0, x1, y0, y1, deg_of_t(_fr(a)), deg_of_t(_fr(b)))
    return Box(x0, x1, y0, y1, a, b)


def as_box(v):
    if isinstance(v, Box):
        return v
    if isinstance(v, dict):
        return mk_box(v["x0"], v["x1"], v["y0"], v["y1"],
                      v.get("th0", v.get("t0")), v.get("th1", v.get("t1")),
                      t=("t0" in v and "th0" not in v))
    return Box(*list(v)[:6])


class Node:
    """A named collection of parameter boxes for DISTINCT squares of one packing."""

    def __init__(self, boxes, s=S_RAT, name=""):
        self.name = name
        self.s = _fr(s)
        self.boxes = {}
        for k, v in boxes.items():
            self.boxes[k] = MBox(k, as_box(v))
        self.normalised = False
        self.stats = {"exact_calls": 0, "backoffs": 0, "passes": 0}

    # ---------------------------------------------------------------- accessors
    @property
    def names(self):
        return list(self.boxes)

    def __getitem__(self, k):
        return self.boxes[k]

    def kept(self):
        return {k: b.kept_fraction() for k, b in self.boxes.items()}

    def build_cores(self, **kw):
        for b in self.boxes.values():
            b.rebuild(**kw)
        return self

    # ---------------------------------------------------------------- THE RULE
    def normalise(self, s=None, nsub=4, max_iter=10, strict_container=True, mode="poly",
                  n_grid=97, max_v=16, aden=ADEN_DEFAULT, refine=2, max_pieces=96,
                  kmode="pieces", corners=None, lonely_nsub=4, lonely_refine=0,
                  verbose=False):
        """Container clip + LONELY clip + mutual clip to a fixed point.  Returns self.

        Every multi-box construction MUST call this before it draws a figure, prices a chord row,
        runs a lane cover or hands boxes to an LP.  Raises `EmptyBox(name)` the moment a box loses
        every pose -- that is a KILL, and the caller should record the pair leaf, not retry.

        `kmode` selects how K' is rebuilt after every pass: "pieces" (A172, the default) is the
        certified exact intersection of the per-piece K', "union" is A171's union-hull polygon --
        sound, but blind to a clip that removes different slabs in different tilt sub-bins, so it
        under-drives the cascade (see the A172 block above `MBox`).

        `refine` levels of TAUTOLOGOUS bisection are interleaved with the clip (`split_piece`): the
        two halves cover the parent exactly, so a half the clip proves wholly dead is dropped with
        no loss.  Refinement is what makes the clip bite where the dead region is a diagonal band
        that shrinks no side of the rectangle (A131 conservatism (c)); without it the residual
        "poses that still meet another core" stays large.  `max_pieces` caps the pieces per box.

        `corners` (A173) turns on the LONELY CLIP per box:  corners={"D": ("TR", c), "B": "BR"} --
        either (corner, c) or just the corner name, in which case c = `C_WIDEN` = 1 + w, the
        K0-WIDEN box.  The named box is then clipped by A169's Theorem B (row R3: a lonely pose
        admits no second meeter of that corner box, so it cannot occur in a K0-BLOCKED packing)
        AT EVERY PASS, BEFORE the mutual clip of that pass -- which is the point: the lonely clip
        shrinks the pieces, K' is rebuilt larger from the survivors at the top of the next pass, and
        the CASCADE carries that growth into the other boxes.  `lonely_refine` bisects a partly
        lonely piece's tilt sub-bin first (tautologous).  A box that loses every piece raises
        `EmptyBox` -- A168's R3 kill, recovered as the limiting case of the clip."""
        s = self.s if s is None else _fr(s)
        self.s = s
        cspec = {}
        for k, v in (corners or {}).items():
            if k not in self.boxes:
                raise KeyError(f"normalise(corners=...): no box named {k!r} in this node")
            cspec[k] = (v, C_WIDEN) if isinstance(v, str) else (v[0], _fr(v[1]))
        self.corners = cspec
        self.lonely = {k: [] for k in cspec}

        def _lonely_pass(tag):
            """the lonely clip on every box that has a corner spec.  Returns True if anything moved."""
            moved = False
            for k, (corner, cc) in cspec.items():
                mb = self.boxes[k]
                rep = lonely_clip(mb, corner, c=cc, s=s, nsub=lonely_nsub,
                                  refine=lonely_refine, max_pieces=max_pieces * 2, pass_=tag)
                rep["stage"] = tag
                self.lonely[k].append(rep)
                if rep["removed"] > 0 or rep["dropped_pieces"]:
                    moved = True
            return moved
        # ---- 1. split every box into nsub tilt sub-bins
        for mb in self.boxes.values():
            mb.kmode = kmode
            r0 = PIN.outer_rect(mb.box0)
            mb.pieces = [(Bin(a, b), r0) for (a, b) in sub_bins(mb.t0, mb.t1, nsub)]
            mb.trace = []
            mb.sliver_area = Fr(0)
            mb.lonely_removed = 0.0
        # ---- 2. container clip (independent of the other boxes; do it once, up front)
        for mb in self.boxes.values():
            keep = []
            for (bn, r) in mb.pieces:
                tr = []
                nr, sl = container_clip(r, bn, s, strict=strict_container, trace=tr)
                mb.sliver_area += sl
                if tr:
                    mb.trace.append(dict(pass_=0, t=[str(bn.t0), str(bn.t1)], steps=tr))
                if nr is not None:
                    keep.append((bn, nr))
            if not keep:
                raise EmptyBox(mb.name, dict(reason="container"))
            mb.pieces = keep
        # ---- 2b. the LONELY clip (A173), before anything reads K': it only shrinks the pieces,
        #          so every K' rebuilt below is already the larger, post-Theorem-B one
        if cspec:
            _lonely_pass("container")
        # ---- 3. interleaved refinement: bisect, drop the dead halves, clip the rest
        names = self.names
        for lvl in range(max(0, refine)):
            if cspec:
                _lonely_pass(f"refine{lvl + 1}")
            for mb in self.boxes.values():
                mb.rebuild(n_grid=n_grid, max_v=max_v, aden=aden)
            obst = {k: self.boxes[k].obstacle(mode) for k in names}
            for k in names:
                mb = self.boxes[k]
                if len(mb.pieces) * 2 > max_pieces:
                    continue
                new = []
                for (bn, r) in mb.pieces:
                    for (bn2, r2) in split_piece(bn, r):
                        tr = []
                        cur, sl = container_clip(r2, bn2, s, strict=strict_container, trace=tr)
                        mb.sliver_area += sl
                        for j in names:
                            if j == k or cur is None:
                                continue
                            cur = _clip_rect_obstacle(cur, obst[j], bn2, self.stats,
                                                      trace=tr, tag=j)
                        if tr:
                            mb.trace.append(dict(refine=lvl + 1,
                                                 t=[str(bn2.t0), str(bn2.t1)], steps=tr))
                        if cur is not None:
                            new.append((bn2, cur))
                if not new:
                    raise EmptyBox(mb.name, dict(reason="refine", level=lvl + 1))
                mb.pieces = new
            if verbose:
                print(f"  refine {lvl + 1}: " +
                      " ".join(f"{k}={self.boxes[k].kept_fraction():.4f}"
                               f"({len(self.boxes[k].pieces)}p)" for k in names), flush=True)
        # ---- 4. LONELY clip + mutual clip to a fixed point, rebuilding K' after every pass
        for it in range(max_iter):
            lonely_moved = _lonely_pass(f"pass{it + 1}") if cspec else False
            for mb in self.boxes.values():
                mb.rebuild(n_grid=n_grid, max_v=max_v, aden=aden)
            obst = {k: self.boxes[k].obstacle(mode) for k in names}
            changed = bool(lonely_moved)
            for k in names:
                mb = self.boxes[k]
                keep = []
                for (bn, r) in mb.pieces:
                    tr = []
                    cur = r
                    for j in names:
                        if j == k or cur is None:
                            continue
                        cur = _clip_rect_obstacle(cur, obst[j], bn, self.stats,
                                                  trace=tr, tag=j)
                    if tr:
                        mb.trace.append(dict(pass_=it + 1, t=[str(bn.t0), str(bn.t1)], steps=tr))
                        changed = True
                    if cur is not None:
                        keep.append((bn, cur))
                if not keep:
                    raise EmptyBox(mb.name, dict(reason="mutual", pass_=it + 1))
                mb.pieces = keep
            self.stats["passes"] = it + 1
            if verbose:
                print(f"  pass {it + 1}: kept " +
                      " ".join(f"{k}={self.boxes[k].kept_fraction():.4f}" for k in names),
                      flush=True)
            if not changed:
                break
        for mb in self.boxes.values():
            mb.rebuild(n_grid=n_grid, max_v=max_v, aden=aden)
            mb.kept = mb.kept_fraction()
        self.normalised = True
        return self

    # ---------------------------------------------------------------- THE INVARIANT
    def assert_invariant(self, s=None, strict=True, sample=4000, seed=171, raise_on_fail=True,
                         mode="poly"):
        """Exact rational checks; raises `InvariantError` listing EVERY failure.  Returns the
        report dict (which the figure prints on the page)."""
        s = self.s if s is None else _fr(s)
        for mb in self.boxes.values():
            if mb.pc is None:
                mb.rebuild()
        fails = []
        rep = dict(s=str(s), boxes=self.names, checks={}, diagnostics={})

        # --- K-CONTAINER: every K' vertex inside [0, s]^2
        kc = []
        for k, mb in self.boxes.items():
            bad = [[str(a), str(b)] for (a, b) in mb.pc.verts
                   if not (0 <= a <= s and 0 <= b <= s)]
            if bad:
                kc.append(dict(box=k, n_bad=len(bad), worst=bad[0]))
                fails.append(dict(check="K-CONTAINER", what=k,
                                  detail=f"{len(bad)} K' vertices outside [0,{float(s):.6f}]^2, "
                                         f"e.g. {bad[0]}"))
        rep["checks"]["K-CONTAINER"] = dict(ok=not kc, bad=kc)

        # --- K-DISJOINT: exact rational SAT between every pair of polygon cores
        kd = []
        names = self.names
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                ok, ax, gap = polys_disjoint_exact(self.boxes[a].pc.verts, self.boxes[b].pc.verts)
                if not ok:
                    kd.append(dict(pair=[a, b], depth=float(-gap)))
                    fails.append(dict(check="K-DISJOINT", what=f"{a}|{b}",
                                      detail=f"K'({a}) and K'({b}) interiors meet, "
                                             f"SAT depth {float(-gap):.9f}"))
        rep["checks"]["K-DISJOINT"] = dict(ok=not kd, bad=kd)

        # --- POSE-CONTAINER (sound) and POSE-CONTAINER-STRICT (all poses inside)
        pcv, psv = [], []
        for k, mb in self.boxes.items():
            for (bn, r) in mb.pieces:
                h, H = bn.wmin / 2, bn.wmax / 2
                ex = max(h - r[0], r[1] - (s - h), h - r[2], r[3] - (s - h))
                if ex > 0:
                    pcv.append(dict(box=k, excess=float(ex), th=[deg_of_t(bn.t0), deg_of_t(bn.t1)]))
                    fails.append(dict(check="POSE-CONTAINER", what=k,
                                      detail=f"centre rect leaves [w_min/2, s-w_min/2] by "
                                             f"{float(ex):.9f} on tilt "
                                             f"[{deg_of_t(bn.t0):.3f},{deg_of_t(bn.t1):.3f}]"))
                exS = max(H - r[0], r[1] - (s - H), H - r[2], r[3] - (s - H))
                if exS > 0:
                    psv.append(dict(box=k, excess=float(exS),
                                    th=[deg_of_t(bn.t0), deg_of_t(bn.t1)]))
                    if strict:
                        fails.append(dict(check="POSE-CONTAINER-STRICT", what=k,
                                          detail=f"poses escape [0,s]^2: centre rect exceeds "
                                                 f"[w_max/2, s-w_max/2] by {float(exS):.9f} on "
                                                 f"tilt [{deg_of_t(bn.t0):.3f},"
                                                 f"{deg_of_t(bn.t1):.3f}]"))
        rep["checks"]["POSE-CONTAINER"] = dict(ok=not pcv, bad=pcv)
        rep["checks"]["POSE-CONTAINER-STRICT"] = dict(ok=not psv, bad=psv, enforced=bool(strict))

        # --- CLIP-FIXPOINT: re-running the mutual clip must change nothing
        fx = []
        obst = {k: self.boxes[k].obstacle(mode) for k in names}
        st = {"exact_calls": 0, "backoffs": 0}
        for k in names:
            mb = self.boxes[k]
            for (bn, r) in mb.pieces:
                cur = r
                for j in names:
                    if j == k or cur is None:
                        continue
                    cur = _clip_rect_obstacle(cur, obst[j], bn, st)
                if cur != r:
                    lost = float(rect_area(r) - rect_area(cur))
                    fx.append(dict(box=k, th=[deg_of_t(bn.t0), deg_of_t(bn.t1)],
                                   lost_area=lost, emptied=(cur is None)))
                    fails.append(dict(check="CLIP-FIXPOINT", what=k,
                                      detail=("box is EMPTIED by the mutual clip"
                                              if cur is None else
                                              f"the mutual clip still removes area {lost:.9f} on "
                                              f"tilt [{deg_of_t(bn.t0):.3f},"
                                              f"{deg_of_t(bn.t1):.3f}] -- normalise() not run")))
        rep["checks"]["CLIP-FIXPOINT"] = dict(ok=not fx, bad=fx)

        # --- tightness diagnostics (reported, never raised)
        rep["diagnostics"] = self.diagnostics(s=s, sample=sample, seed=seed)
        rep["kept"] = self.kept()
        rep["sliver_area"] = {k: float(b.sliver_area) for k, b in self.boxes.items()}
        rep["lonely_removed"] = {k: float(getattr(b, "lonely_removed", 0.0))
                                 for k, b in self.boxes.items()}
        rep["failures"] = fails
        rep["ok"] = not fails
        self.report = rep
        if fails and raise_on_fail:
            raise InvariantError(fails)
        return rep

    def diagnostics(self, s=None, sample=4000, seed=171):
        """sampled tightness numbers: what fraction of the node's poses still escape the container
        or still meet another box's polygon core."""
        s = self.s if s is None else _fr(s)
        rng = np.random.default_rng(seed)
        fs = float(s)
        out = {}
        for k, mb in self.boxes.items():
            C, TH = mb.sample(sample, rng)
            if not len(C):
                out[k] = dict(escape_frac=0.0, core_meet_frac=0.0, drawn=0)
                continue
            h = 0.5 * (np.abs(np.cos(TH)) + np.abs(np.sin(TH)))
            esc = ~((C[:, 0] >= h) & (C[:, 0] <= fs - h) &
                    (C[:, 1] >= h) & (C[:, 1] <= fs - h))
            hit = np.zeros(len(C), bool)
            for j, ob in self.boxes.items():
                if j == k or ob.pc is None:
                    continue
                hit |= PC.poly_square_depth(ob.pc.P, C, TH) > 0.0
            out[k] = dict(drawn=int(len(C)), escape_frac=float(esc.mean()),
                          core_meet_frac=float(hit.mean()))
        return out

    # ---------------------------------------------------------------- consumers
    def chord_rows(self, lines, s=None):
        """A144's guard-line chord row over the node's (normalised) boxes.

        For each line:  rhs = s - sum_j minchord(B_j, l),  beta = floor(rhs)  -- the number of FREE
        squares whose chord on l is >= 1.  Refuses to run on an un-normalised node."""
        self._require_normalised("chord_rows")
        import chordlane as CL                                   # READ-ONLY (A161)
        s = self.s if s is None else _fr(s)
        boxes = [self.boxes[k].ubox for k in self.names]
        out = []
        for ln in lines:
            rhs, beta, terms = CL.guard_rhs(boxes, ln, s=s)
            out.append(dict(orient=ln.orient, off=str(ln.off), off_float=float(ln.off),
                            rhs=str(rhs), rhs_float=float(rhs), beta=beta,
                            minchord={self.names[i]: terms[i]["minchord_float"]
                                      for i in range(len(self.names))}))
        return out

    def lane(self, cell, line=None, s=None, max_depth=34, max_open=2500, deadline=None,
             band_mode="out"):
        """A141's lane cover with A161's exact miss test, restricted to the node's cores.

        `cell` = (X0, X1, Y0, Y1).  Returns A161's cover dict (`lane` = 0, 1 or None)."""
        self._require_normalised("lane")
        import chordlane as CL                                   # READ-ONLY (A161)
        import polylane as P                                     # READ-ONLY (A141)
        s = float(self.s if s is None else _fr(s))
        conds = P.build_cond([self.boxes[k].ubox for k in self.names], tighten=False)
        return CL.lane_out(cell, conds, line, s=s, max_depth=max_depth, max_open=max_open,
                           deadline=deadline, band_mode=band_mode)

    def misses_cell(self, cell):
        """A161's exact separating-axis miss test, per box of the node."""
        import chordlane as CL                                   # READ-ONLY (A161)
        out = {}
        for k, mb in self.boxes.items():
            ok, det = CL.box_misses_cell_exact(mb.ubox if getattr(mb, "ubox", None) else mb.box0,
                                               cell)
            out[k] = dict(misses=bool(ok), detail=det)
        return out

    def _require_normalised(self, what):
        if not self.normalised:
            raise RuntimeError(
                f"Node.{what}() refuses to run on an un-normalised node: call node.normalise(s) "
                f"first (A171; this is the A165/A168 failure mode)")

    # ---------------------------------------------------------------- figure
    def figure(self, path, s=None, extras=None, title=None, nsample=60):
        """A148-style SVG panel: container, every K' solid, pose unions as thin outlines, names,
        kept fractions, and the invariant's verdict printed on the page."""
        return _figure(self, path, s=s, extras=extras, title=title, nsample=nsample)

    def to_json(self):
        return dict(name=self.name, s=str(self.s), normalised=self.normalised,
                    stats=self.stats,
                    corners={k: [v[0], str(v[1])] for k, v in getattr(self, "corners", {}).items()},
                    lonely=getattr(self, "lonely", {}),
                    boxes={k: b.to_json() for k, b in self.boxes.items()},
                    report=getattr(self, "report", None))


# ==================================================================== exact polygon SAT
def polys_disjoint_exact(V1, V2):
    """EXACT rational SAT: are the INTERIORS of two convex rational polygons disjoint?

    Complete for convex polygons: the interiors are disjoint iff some edge normal of one of them
    separates them (with a >= 0 gap -- a touch is interior-disjoint).  Returns (ok, axis, gap) with
    `gap` the best (largest) separation, negative when they overlap."""
    P = [(_fr(a), _fr(b)) for (a, b) in V1]
    Q = [(_fr(a), _fr(b)) for (a, b) in V2]
    best, bax = None, None
    for (A, B, tag) in ((P, Q, "P"), (Q, P, "Q")):
        m = len(A)
        for i in range(m):
            (ax, ay) = A[i]
            (bx, by) = A[(i + 1) % m]
            nx, ny = (by - ay), -(bx - ax)
            if nx == 0 and ny == 0:
                continue
            n2 = sqrt_lo(nx * nx + ny * ny)
            pa = [nx * px + ny * py for (px, py) in A]
            pb = [nx * px + ny * py for (px, py) in B]
            gap = max(min(pb) - max(pa), min(pa) - max(pb))
            g = gap / n2 if n2 > 0 else gap
            if best is None or g > best:
                best, bax = g, f"{tag}{i}"
    return (best is not None and best >= 0), bax, (best if best is not None else Fr(0))


# ==================================================================== the figure
def _svg_poly(P, fill, stroke, w=1.2, op=0.55, dash=""):
    d = " ".join(f"{x:.3f},{y:.3f}" for (x, y) in P)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
            f'stroke-width="{w}"{da}/>')


def _svg_txt(x, y, t, size=11, col="#111", bold=False, anchor="start"):
    t = (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial,sans-serif" '
            f'font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{t}</text>')


_PALETTE = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b",
            "#17becf", "#e377c2"]


def _pose_outlines(mb, cap=24):
    """the EXTREME poses of the box -- each corner of each piece's centre rect at each endpoint of
    its tilt sub-bin -- as individual unit squares.  Drawn as thin outlines, they ARE poses of the
    node (not a hull, not an envelope), so what the eye sees is what the hypothesis contains."""
    out = []
    for (bn, r) in mb.pieces:
        x0, x1, y0, y1 = (float(v) for v in r)
        for t in (float(bn.t0), float(bn.t1)):
            th = 2.0 * math.atan(t)
            c, s = math.cos(th), math.sin(th)
            for cx in (x0, x1):
                for cy in (y0, y1):
                    out.append([(cx + 0.5 * (i * c - j * s), cy + 0.5 * (i * s + j * c))
                                for (i, j) in ((1, 1), (1, -1), (-1, -1), (-1, 1))])
    if len(out) <= cap:
        return out
    step = max(1, len(out) // cap)
    return out[::step][:cap]


def _figure(node, path, s=None, extras=None, title=None, nsample=60):
    s = float(node.s if s is None else _fr(s))
    for mb in node.boxes.values():
        if mb.pc is None:
            mb.rebuild()
    rep = getattr(node, "report", None)
    if rep is None:
        rep = node.assert_invariant(raise_on_fail=False)
    PAD, SCALE, RIGHT = 34.0, 150.0, 300.0
    W = PAD * 2 + s * SCALE + RIGHT
    H = PAD * 2 + s * SCALE + 26

    def X(x):
        return PAD + x * SCALE

    def Y(y):
        return PAD + (s - y) * SCALE

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{int(H)}" '
           f'viewBox="0 0 {int(W)} {int(H)}">',
           f'<rect width="{int(W)}" height="{int(H)}" fill="#ffffff"/>']
    out.append(_svg_txt(PAD, PAD - 14, title or (node.name or "A171 multi-box node"),
                        size=13, bold=True))
    # container
    out.append(f'<rect x="{X(0):.2f}" y="{Y(s):.2f}" width="{s * SCALE:.2f}" '
               f'height="{s * SCALE:.2f}" fill="none" stroke="#000" stroke-width="2.2"/>')
    out.append(_svg_txt(X(0), Y(0) + 15, f"container [0,s]^2, s = {s:.6f}", size=10, col="#444"))
    for i, (k, mb) in enumerate(node.boxes.items()):
        col = _PALETTE[i % len(_PALETTE)]
        for sq in _pose_outlines(mb, nsample):
            out.append(_svg_poly([(X(x), Y(y)) for (x, y) in sq], "none", col,
                                 w=0.55, op=0.0, dash="3,2"))
        out.append(_svg_poly([(X(float(a)), Y(float(b))) for (a, b) in mb.pc.verts],
                             col, col, w=1.4, op=0.55))
        for (bn, r) in mb.pieces:
            x0, x1, y0, y1 = (float(v) for v in r)
            out.append(f'<rect x="{X(x0):.2f}" y="{Y(y1):.2f}" width="{(x1 - x0) * SCALE:.2f}" '
                       f'height="{(y1 - y0) * SCALE:.2f}" fill="none" stroke="{col}" '
                       f'stroke-width="0.7" stroke-opacity="0.9"/>')
        cx = sum(float(a) for (a, _b) in mb.pc.verts) / len(mb.pc.verts)
        cy = sum(float(b) for (_a, b) in mb.pc.verts) / len(mb.pc.verts)
        out.append(_svg_txt(X(cx), Y(cy) + 4, k, size=12, col="#fff", bold=True, anchor="middle"))
    # legend / verdict
    tx = PAD + s * SCALE + 18
    ty = PAD + 6
    out.append(_svg_txt(tx, ty, "A171 multi-box invariant", size=12, bold=True))
    ty += 18
    out.append(_svg_txt(tx, ty, f"normalised: {node.normalised}   passes: "
                                f"{node.stats.get('passes', 0)}", size=10, col="#333"))
    ty += 16
    verdict = "INVARIANT HOLDS" if rep.get("ok") else "INVARIANT FAILS"
    out.append(_svg_txt(tx, ty, verdict, size=12, bold=True,
                        col=("#1a7f37" if rep.get("ok") else "#c02020")))
    ty += 6
    for cname, c in rep["checks"].items():
        ty += 15
        out.append(_svg_txt(tx + 6, ty, f"{'OK ' if c['ok'] else 'BAD'}  {cname}", size=10,
                            col=("#1a7f37" if c["ok"] else "#c02020")))
    ty += 20
    out.append(_svg_txt(tx, ty, "box: kept  K'area  axis a  esc  meet", size=10, bold=True))
    dg = rep.get("diagnostics", {})
    for i, (k, mb) in enumerate(node.boxes.items()):
        ty += 15
        d = dg.get(k, {})
        out.append(_svg_txt(tx + 6, ty,
                            f"{k}: {mb.kept_fraction():.4f}  {mb.pc.area():.4f}  "
                            f"{float(mb.core.a) if mb.core is not None else 0:.4f}  "
                            f"{d.get('escape_frac', 0):.3f}  {d.get('core_meet_frac', 0):.3f}",
                            size=10, col=_PALETTE[i % len(_PALETTE)]))
    if not rep.get("ok"):
        ty += 20
        out.append(_svg_txt(tx, ty, "failures:", size=10, bold=True, col="#c02020"))
        for f in rep["failures"][:10]:
            ty += 14
            out.append(_svg_txt(tx + 6, ty, f"{f['check']} [{f['what']}] {f['detail'][:52]}",
                                size=9, col="#c02020"))
    for line in (extras or []):
        ty += 15
        out.append(_svg_txt(tx, ty, str(line), size=10, col="#333"))
    ty += 22
    srcs = sorted({(mb.k_source or "?") for mb in node.boxes.values()})
    out.append(_svg_txt(tx, ty, "solid = K'(B) = intersection of per-piece K', certified"
                        if srcs == ["pieces"] else
                        f"solid = K'(B), certified  [source: {', '.join(srcs)}]",
                        size=9, col="#666"))
    ty += 13
    out.append(_svg_txt(tx, ty, "dashed = extreme POSES of the box (thin outlines)",
                        size=9, col="#666"))
    ty += 13
    out.append(_svg_txt(tx, ty, "thin rects = clipped centre pieces", size=9, col="#666"))
    out.append("</svg>")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    return path


# ==================================================================== self-test
if __name__ == "__main__":
    import json
    import time
    t0 = time.time()
    nd = Node({"H": (2.5674485, 2.67226625, 2.357813, 2.46263075, 45.0, 60.0),
               "B1": (3.127084, 3.1733821433529026, 1.5015011950128963, 1.5785397484754269,
                      45.0, 50.625),
               "D": (3.223006893074939, 3.377084, 3.211365683498047, 3.377084, 0.0, 11.25)},
              name="A168 BR139/TRH-25")
    nd.build_cores()
    r0 = nd.assert_invariant(raise_on_fail=False)
    print("before normalise: ok =", r0["ok"], "  failures =", len(r0["failures"]))
    for f in r0["failures"]:
        print("   ", f["check"], f["what"], f["detail"])
    nd.normalise(nsub=4, verbose=True)
    r1 = nd.assert_invariant(raise_on_fail=False)
    print("after normalise:  ok =", r1["ok"], "  kept =",
          {k: round(v, 6) for k, v in r1["kept"].items()})
    print(json.dumps(r1["diagnostics"], indent=1))
    print(f"{time.time() - t0:.1f} s, exact calls {nd.stats['exact_calls']}")
