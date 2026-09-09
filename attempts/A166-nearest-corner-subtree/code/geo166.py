"""A166 -- the geometric stages of the nearest-corner sub-tree.

Every kill below is a NECESSARY condition on a k0_00 packing that satisfies the node's hypothesis

    (H)      some square of F has pose in B_H            (the interior cell, A38/A115)
    (BLOCK)  two DISTINCT squares of F meet int B_c^w     (K0-BLOCKED at the corner c, K0-WIDEN pad w)

so discarding a cell / a pair cell is sound.  The stages, in the order they are applied and with the
exact statement each one proves:

  R  (A161 reach, exact)     `chordlane.box_misses_cell_exact(G, corner_rect)`: EVERY pose of the
        corner cell `G` gives a square whose interior misses the interior of the corner box.  Then no
        pose of `G` is a meeter and the cell cannot be one of the two.  This is A155's `clip_box`
        reach test STRENGTHENED: `clip_box` separates only along the corner box's own two normals
        (the `h(theta)` bound), `box_misses_cell_exact` also uses the SQUARE's two normals.

  H2 (centre distance, H vs the corner cell)   `maxdist(B_H, G) < 1`: two unit squares with centre
        distance < 1 overlap (any separating direction `n` gives |d.n| >= h1(n) + h2(n) >= 1).  So
        EVERY square realising `G` overlaps EVERY square realising `B_H`, hence `Q_G = H` (a packing's
        squares are interior-disjoint, so overlapping squares are equal).

  H1 (K' vs K', H vs the corner cell)   `K'(B_H)` meets `K'(G)` (A132 exact polygon cores): same
        conclusion, `Q_G = H`.

  Verdict of H2/H1: if `B_H` and `G` are DISJOINT as parameter boxes then `Q_G = H` is impossible and
  the cell is DEAD (a (C) leaf).  If they intersect, the cell survives only in the DEGENERATE
  sub-case `Q_G = H`, whose hypothesis is `H in B_H ∩ G` with budget 11 - 2 = 9 (one fewer square).

  CLIP (A131 pin-clip with A158's rule)   `pinclip.clip_node(G, slots=[K'(B_H) centre],
        a_pin = the largest axis-aligned square inscribed in K'(B_H) about B_H's midpoint)`.
        A centre in A131's octagon at every tilt of the sub-bin gives a square that overlaps that
        inscribed core -- hence `K'(B_H)`, hence `H` -- at every admissible tilt, so again `Q_G = H`.
        Where `B_H ∩ G = ∅` those centres are DISCARDED; the clipped box is the sound hypothesis of
        the non-degenerate sub-case.  The inscribed axis core is strictly smaller than `K'(B_H)`, so
        the clip removes LESS than the truth: sound, and A131's certified machinery is used unchanged.

  P2 / P1 / P1s (A143's pair chain, on the CLIPPED boxes)   the two corner squares are distinct, so
        `maxdist < 1`, `K'(A)` meets `K'(B)`, or every surviving tilt sub-pair contradictory, kills
        the pair cell.  Run on the clipped boxes it is strictly stronger than A143/A155's version.

  MUT (A158 mutual clip)   each of the two clipped corner boxes clipped against the OTHER's inscribed
        axis core.  The two corner squares are distinct by (BLOCK), so this clip is a plain discard;
        if either box empties the pair cell is dead.

  DIST (the budget gate)   the three EXACT cores `K(B_H)`, `K(A)`, `K(B)` (A135 `exact_a`) must be
        pairwise interior-disjoint for the frozen certificate's bridge to give three DISTINCT
        witnesses at budget 8.  Checked here with a from-scratch exact rational SAT over the four
        edge normals of the two cores (NOT `exactcore.cores_pairwise_disjoint`, whose x/y-only test
        is written for axis-aligned pin cores and is not sound for tilted ones).
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A131-pin-clip", "code"),
           os.path.join(ATT, "A141-polycore-lane", "code"),
           os.path.join(ATT, "A161-chord-lane", "code"),
           os.path.join(ATT, "A155-exact-cell-corner-band", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                            # noqa: F401,E402  (before numpy)
import numpy as np                                      # noqa: E402
import polycore as PC                                   # noqa: E402  READ-ONLY (A132)
import exactcore as EC                                  # noqa: E402  READ-ONLY (A135)
import pinclip as PCLIP                                 # noqa: E402  READ-ONLY (A131)
import cells166 as C                                    # noqa: E402
from caselp import Box, Core, cos_sin_t, t_lo, t_hi     # noqa: E402  READ-ONLY (A57)

MAXV = 16
NSUB_PAIR = 4
S0 = C.S0
HALF = Fr(1, 2)

# A161's exact reach test, imported lazily: chordlane pulls in A118's corpus, which is heavy.
_CL = None


def chordlane():
    global _CL
    if _CL is None:
        import chordlane as CL                          # noqa: E402  READ-ONLY (A161)
        _CL = CL
    return _CL


# --------------------------------------------------------------------- cores
def kprime(box):
    return PC.build(box, max_v=MAXV)


def exact_core(box):
    """A135's certified exact axis core of a box, as a caselp.Core (raises if the vertex test
    fails)."""
    k = box.core()
    a, _a0, ok = EC.exact_a(box)
    if not ok:
        raise RuntimeError("exact core vertex test fails for %r" % (box,))
    return Core(k.kx, k.ky, k.tm, a, box)


def inside_poly(P, x, y):
    E = np.roll(P, -1, axis=0) - P
    return bool(np.all(E[:, 0] * (y - P[:, 1]) - E[:, 1] * (x - P[:, 0]) >= 0.0))


def axis_core_in(pc, kx, ky, hi=0.5, iters=48):
    """A158's rule: the largest half-side `a` with [kx +- a] x [ky +- a] inside K'.  Monotone in
    `a`, so bisection is exact to 2^-iters; 0 if the midpoint is outside K' at all."""
    P = pc.P
    if not inside_poly(P, kx, ky):
        return 0.0
    lo, hi_ = 0.0, hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi_)
        if all(inside_poly(P, kx + sx * mid, ky + sy * mid)
               for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)):
            lo = mid
        else:
            hi_ = mid
    return lo


# --------------------------------------------------------------------- box relations
def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return math.hypot(dx, dy)


def boxes_intersect(b1, b2, tol=0.0):
    """as PARAMETER boxes (centre rectangle and tilt window, tilt taken mod 90 with the wrap)."""
    if min(b1.x1, b2.x1) < max(b1.x0, b2.x0) - tol:
        return False
    if min(b1.y1, b2.y1) < max(b1.y0, b2.y0) - tol:
        return False
    for sh in (-90.0, 0.0, 90.0):
        if min(b1.th1, b2.th1 + sh) >= max(b1.th0, b2.th0 + sh) - tol:
            return True
    return False


def box_intersection(b1, b2):
    x0, x1 = max(b1.x0, b2.x0), min(b1.x1, b2.x1)
    y0, y1 = max(b1.y0, b2.y0), min(b1.y1, b2.y1)
    best = None
    for sh in (-90.0, 0.0, 90.0):
        t0, t1 = max(b1.th0, b2.th0 + sh), min(b1.th1, b2.th1 + sh)
        if t1 >= t0 and (best is None or (t1 - t0) > (best[1] - best[0])):
            best = (t0, t1)
    if x1 < x0 or y1 < y0 or best is None:
        return None
    return Box(x0, x1, y0, y1, best[0], best[1])


# --------------------------------------------------------------------- exact core-vs-core SAT
def _core_verts_frac(c):
    """the four vertices of an exact core, as exact Fractions (cos_sin_t(tm) is rational)."""
    cm, sm = c.cm, c.sm
    a = c.a
    e1 = (a * cm, a * sm)
    e2 = (-a * sm, a * cm)
    return [(c.kx + i * e1[0] + j * e2[0], c.ky + i * e1[1] + j * e2[1])
            for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def cores_disjoint_exact(c1, c2):
    """EXACT: True iff the interiors of the two core squares are disjoint.  SAT over the four edge
    normals (two per square) is complete for convex polygons; a normal on which the projections
    are separated (<=, closed touching allowed) proves interior-disjointness.  Returns
    (ok, best_gap as a Fraction)."""
    V1 = _core_verts_frac(c1)
    V2 = _core_verts_frac(c2)
    best = None
    for (cm, sm) in ((c1.cm, c1.sm), (c2.cm, c2.sm)):
        for (nx, ny) in ((cm, sm), (-sm, cm)):
            a = [p[0] * nx + p[1] * ny for p in V1]
            b = [p[0] * nx + p[1] * ny for p in V2]
            # the normals are NOT unit (|n|^2 = cm^2 + sm^2), so normalise the gap by |n|^2 only
            # for reporting; the SIGN is what decides and is scale-free.
            g = min(max(a), max(b)) - max(min(a), min(b))
            best = g if best is None else min(best, g)
    return (best <= 0), best


# --------------------------------------------------------------------- the reach test (A161)
def cell_can_meet(box, rect):
    """(can_meet, detail).  can_meet = False is the SOUND statement 'no pose of `box` meets
    int(rect)' (A161 `box_misses_cell_exact`, the full SAT over the parameter box)."""
    CL = chordlane()
    misses, det = CL.box_misses_cell_exact(box, tuple(rect))
    return (not misses), det


# --------------------------------------------------------------------- the H clip (A131 + A158)
def clip_against_core(box, kx, ky, a_axis, nsub=1):
    """A131 clip_node with ONE 'pin' = an axis-aligned core of half-side `a_axis` at (kx, ky)."""
    if a_axis <= 0.0:
        return dict(refused=True, reason="empty_axis_core", union_rect=None, empty=False,
                    kept_union=1.0, kept_vol=1.0, n_empty=0)
    # the pin half-side must be a STRICT UNDER-estimate of the inscribed axis core: rounding it up
    # would let A131's octagon claim an overlap that need not happen, i.e. an unsound clip.  `Fr`
    # of a float is exact and `axis_core_in` already returns a feasible (hence under-) value, so
    # floor onto a 1e-12 grid and keep the exact binary value if it is already smaller.
    a_q = min(Fr(a_axis), Fr(int(a_axis * 10 ** 12), 10 ** 12))
    return PCLIP.clip_node(box, [(Fr(kx), Fr(ky))], nsub=nsub, s_rat=PCLIP.S_RAT, a_pin=a_q)


def rect_to_box(rect, th0, th1):
    return Box(float(rect[0]), float(rect[1]), float(rect[2]), float(rect[3]), th0, th1)
