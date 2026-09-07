"""A111 -- the OCTAGON (common-inscribed-core) pair test, and Lemma TC, as free logic kills.

Two exact, LP-free tests that decide "every pose in box A overlaps every pose in box B", i.e. that
no packing has a square in A and a different square in B.  Both are A57/A96 machinery, reused:

 (O) CORE-MEET (A57 `pinguard.classify`'s contradictory case, with A96's TIGHT core `kill_core`,
     control 583/583 on the deployed cover).  K(B) is a square contained in EVERY unit square whose
     pose lies in B (A96's tight half-side a = (1/2 - h M_c)/M_t).  If K(A) and K(B) intersect then
     every Q_A and every Q_B intersect, so A and B cannot hold two squares of a packing.  The test
     is the separating-axis test on two rotated squares -- `pinguard.cores_meet`, unchanged.

 (TC) TILT-COUPLING.  Two DISJOINT unit squares whose tilts differ by D (reduced to [0, 45]) have
     centres at least (1 + cos D + sin D)/2 apart: the minimum is the face-to-face placement, where
     the separation along the owner's normal is 1/2 + w(D)/2, w = |cos| + |sin|.  Hence if the two
     boxes force a centre distance <= c_max and a tilt difference >= D_min with
     c_max < (1 + cos D_min + sin D_min)/2, no two squares of a packing can occupy them.
     (Equivalently: centre distance c forces |dtheta| <= D(c), (1 + cos D + sin D)/2 = c.)

Both are ONE-SIDED: they can only prove emptiness.  A pair they do not kill is undecided.

A pair killed this way makes the whole YES region EMPTY (a certified kill of the leaf, no LP), and
the same test applied to a node's conditioned box against the class pins TRIMS that box (A96's tilt
trimming): a sub-box whose core meets a pin core holds no admissible witness, so dropping it only
strengthens the node hypothesis and can only lower tau.
"""
from __future__ import annotations

import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L                      # noqa: F401  (BLAS pin first)
from caselp import Box
from pinguard import kill_core, cores_meet


def as_box(b):
    return b if isinstance(b, Box) else Box(b["x0"], b["x1"], b["y0"], b["y1"], b["th0"], b["th1"])


def boxes_pose_disjoint(a, b, tol=1e-12):
    """True if no single pose lies in both boxes (so they cannot be the SAME square).  Tilt is
    compared mod 90 because theta and theta + 90 are the same square."""
    a, b = as_box(a), as_box(b)
    if (a.x1 < b.x0 - tol or b.x1 < a.x0 - tol or a.y1 < b.y0 - tol or b.y1 < a.y0 - tol):
        return True
    for off in (-180.0, -90.0, 0.0, 90.0, 180.0):
        if not (a.th1 < b.th0 + off - tol or b.th1 + off < a.th0 - tol):
            return False
    return True


def theta_intervals(th0, th1):
    """[th0, th1] (degrees, ANY offset) as a union of intervals inside [0, 90] -- the domain
    `caselp.Box.core` / `pinguard.tight_a` are stated on.  Identical to t2_no.theta_intervals."""
    if th1 - th0 >= 90.0:
        return [(0.0, 90.0)]
    a = th0 % 90.0
    b = a + (th1 - th0)
    if b <= 90.0:
        return [(a, b)]
    return [(a, 90.0), (0.0, b - 90.0)]


def normalised(b):
    """the box as a list of boxes with tilt inside [0, 90].  A box whose tilt interval straddles a
    multiple of 90 is TWO boxes, and a claim about the box holds only if it holds for both."""
    b = as_box(b)
    return [Box(b.x0, b.x1, b.y0, b.y1, t0, t1) for (t0, t1) in theta_intervals(b.th0, b.th1)]


def safe_kill_core(b):
    """kill_core with its domain enforced.  `tight_a`'s bound is stated for 0 <= th0 <= th1 <= 90;
    fed a negative interval (which is exactly what a D4 REFLECTION produces) it can return a
    half-side > 1/2, i.e. a 'core' that is not inside the square at all.  Reject that outright."""
    c = kill_core(b)
    if c is None:
        return None
    if not (0.0 <= b.th0 <= b.th1 <= 90.0 + 1e-9):
        return None
    if float(c.a) > 0.5 + 1e-12:
        return None
    return c


def core_meet_kill(a, b):
    """(O): every pose of a overlaps every pose of b.  With the tilt intervals normalised into
    [0, 90] the claim must hold for EVERY pair of tilt branches."""
    A, B = normalised(a), normalised(b)
    hi_a = hi_b = 0.0
    for ba in A:
        ca = safe_kill_core(ba)
        if ca is None:
            return False, None
        hi_a = max(hi_a, float(ca.a))
        for bb in B:
            cb = safe_kill_core(bb)
            if cb is None:
                return False, None
            hi_b = max(hi_b, float(cb.a))
            if not cores_meet(ca, cb):
                return False, None
    return True, dict(rule="CORE-MEET", a_half=hi_a, b_half=hi_b,
                      branches=[len(A), len(B)])


def _w(d_deg):
    r = math.radians(d_deg)
    return abs(math.cos(r)) + abs(math.sin(r))


def tilt_dev_min(a, b):
    """min over the two tilt intervals of the tilt difference reduced to [0, 45] degrees.
    The reduced difference f(d) = min(d mod 90, 90 - d mod 90) is piecewise linear with minima 0 at
    the multiples of 90 and maximum 45 at 45 mod 90, so on an interval containing no multiple of 90
    the minimum is at an endpoint."""
    a, b = as_box(a), as_box(b)
    lo, hi = a.th0 - b.th1, a.th1 - b.th0
    if hi - lo >= 90.0:
        return 0.0
    k = math.ceil(lo / 90.0)
    if k * 90.0 <= hi + 1e-12:                 # a multiple of 90 inside: the tilts can agree
        return 0.0
    out = 45.0
    for d in (lo, hi):
        m = d % 90.0
        out = min(out, m, 90.0 - m)
    return out


def centre_dist_max(a, b):
    """max |c_a - c_b| over the two centre boxes (per axis the max is at opposite corners)."""
    a, b = as_box(a), as_box(b)
    dx = max(a.x1 - b.x0, b.x1 - a.x0, 0.0)
    dy = max(a.y1 - b.y0, b.y1 - a.y0, 0.0)
    return math.hypot(dx, dy)


def tc_kill(a, b):
    """(TC): the boxes force |dtheta| >= D_min while the centres cannot get (1+cos+sin)/2 apart."""
    d_min = tilt_dev_min(a, b)
    need = (1.0 + _w(d_min)) / 2.0
    cmax = centre_dist_max(a, b)
    if cmax < need - 1e-12:
        return True, dict(rule="TC", dtheta_min_deg=round(d_min, 5),
                          need_centre_dist=round(need, 6), max_centre_dist=round(cmax, 6))
    return False, None


def pair_kill(a, b, require_distinct=True):
    """Does the pair (a, b) admit two DISTINCT squares of a packing?  Returns (killed, info)."""
    if require_distinct and not boxes_pose_disjoint(a, b):
        # the two boxes share a pose: they may be witnessed by the SAME square, so an overlap
        # test proves nothing about a packing.  (This is pinguard's "parent" case, one level up.)
        return False, dict(rule=None, note="boxes share a pose (same square possible)")
    ok, info = core_meet_kill(a, b)
    if ok:
        return True, info
    ok, info = tc_kill(a, b)
    if ok:
        return True, info
    return False, None


def region_kill(boxes, pin_boxes):
    """Is the YES region (one square in each of `boxes`, plus the class pins) EMPTY by logic?
    boxes: dict name -> box dict; pin_boxes: dict name -> caselp.Box (the A57 slack pin boxes)."""
    names = list(boxes)
    hits = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            ok, info = pair_kill(boxes[names[i]], boxes[names[j]])
            if ok:
                hits.append(dict(pair=[names[i], names[j]], **info))
    for n in names:
        for p, pb in pin_boxes.items():
            ok, info = pair_kill(boxes[n], pb)
            if ok:
                hits.append(dict(pair=[n, "pin:" + p], **info))
    return (len(hits) > 0), hits
