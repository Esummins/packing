"""A135 -- the EXACT rational axis core of a parameter box, certified vertex-by-vertex.

Motivation (A132 T2 / notes/lp_effect.md).  A57's `caselp.Box.core()` builds the core square

    K(a) = (kx, ky, tm, a),   a = (1/2 - hd) / (1 + (t1 - t0)),   hd = half DIAGONAL of the centre box,

which for a PIN box (th0 = th1 = 0, centre half-width h = delta/sqrt(2)) gives a = 1/2 - delta,
because hd = h*sqrt(2) = delta.  But for a zero-tilt box the intersection of the unit squares over
the box is EXACTLY the axis square of half-side 1/2 - h = 1/2 - delta/sqrt(2), so the emitted pin
core is short by delta*(1 - 1/sqrt(2)) ~ 0.00293 per side -- a 0.6 % enlargement that A132 measured
at 21 % of the K'-excluded dual weight on A57, and that on `k5_11_interior_Y1038` is the WHOLE kill.

This module produces, for any box, the LARGEST rational half-side a at the box's own (kx, ky, tm)
whose four corners pass A132's exact rational vertex test `polycore.vertex_ok`.  Two properties
matter:

  * SOUNDNESS is not inherited from the search.  a is found by bisection on a rational grid and then
    the four corners of K(a) are certified EXACTLY (two quadratics in t = tan(theta/2) per corner of
    the centre rectangle per edge normal), exactly as A132 certifies a polygon's vertices.  The
    bisection is a heuristic; the corner test is the proof.
  * The result is a SQUARE at the box's own tilt tm, i.e. it fits the FROZEN certificate schema
    (`{kx, ky, tm, a}`) with no verifier change.  It is contained in A132's polygon core K'(B) --
    it is the largest inscribed square of that pose -- so it buys a strict subset of K''s effect,
    for free.

`vertex_ok` certifies CLOSED containment (|R(-th) d|_inf <= 1/2), which is exactly the frozen
certificate's hypothesis ("some square Q0 of the packing CONTAINS K"; verify_case.py :12-14).
`strict=True` shrinks by one grid step so the corners are in the OPEN square, which is what the
T5 logic kill needs (K subset interior Q, A132 spec Sec.1).

Read-only imports of A57's caselp and A132's polycore.  Nothing here is wired into any driver.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees", "code")
A132 = os.path.join(ROOT, "A132-polygon-core", "code")
for _p in (A57, A132, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, Core, cos_sin_t, t_lo, t_hi          # noqa: E402  (read-only)
import polycore                                              # noqa: E402  (read-only)

HALF = Fr(1, 2)
ADEN = 1 << 40          # rational grid the half-side is searched on (~9.1e-13)


def core_corners(kx, ky, cm, sm, a):
    """the four corners of the square (kx, ky, tilt tm, half-side a), exact rationals."""
    return [(kx + a * (i * cm - j * sm), ky + a * (i * sm + j * cm))
            for i, j in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def a_ok(box, kx, ky, cm, sm, a, t0, t1):
    """EXACT: is K(kx,ky,tm,a) contained in Q(c, theta) for every (c, theta) in `box`?

    K is convex and Q(c,theta) is convex, so corner containment is containment."""
    if a <= 0:
        return False
    for (vx, vy) in core_corners(kx, ky, cm, sm, a):
        if not polycore.vertex_ok(vx, vy, box, t0, t1):
            return False
    return True


def exact_a(box, aden=ADEN, strict=False):
    """The largest a on the 1/aden grid with K(a) certified inside every pose of `box`.

    Returns (a, a_stock, cert_ok).  `a_stock` is caselp.Box.core()'s half-side (the deployed one).
    Never returns something smaller than a_stock: a_stock is itself certified first, and if the
    corpus's own core somehow fails the exact test that is reported (cert_ok False) rather than
    silently repaired."""
    k = box.core()
    if k is None:
        return None, None, False
    t0, t1 = t_lo(box.th0), t_hi(box.th1)
    kx, ky, cm, sm = k.kx, k.ky, k.cm, k.sm
    a_stock = k.a
    if not a_ok(box, kx, ky, cm, sm, a_stock, t0, t1):
        return None, a_stock, False                     # the DEPLOYED core fails: report, do not fix
    lo = Fr(math.floor(float(a_stock) * aden), aden)     # certified
    hi = Fr(math.ceil(0.5 * aden), aden)                 # 1/2: never certifiable (no unit square)
    if a_ok(box, kx, ky, cm, sm, hi, t0, t1):
        return hi, a_stock, True                         # cannot happen; guarded, not assumed
    while hi - lo > Fr(1, aden):
        mid = Fr(round((lo + hi) / 2 * aden), aden)
        if mid <= lo or mid >= hi:
            break
        if a_ok(box, kx, ky, cm, sm, mid, t0, t1):
            lo = mid
        else:
            hi = mid
    a = lo
    if strict:
        a = a - Fr(1, aden)
    if a < a_stock:
        a = a_stock
    assert a_ok(box, kx, ky, cm, sm, a, t0, t1), "exact_a: final value not certified"
    return a, a_stock, True


def exact_core(box, aden=ADEN, strict=False):
    """A caselp.Core at the box's own (kx, ky, tm) carrying the certified maximal half-side."""
    k = box.core()
    if k is None:
        return None
    a, _a0, ok = exact_a(box, aden=aden, strict=strict)
    if not ok:
        raise RuntimeError(f"exactcore: deployed core of {box!r} fails the exact vertex test")
    return Core(k.kx, k.ky, k.tm, a, box)


def pin_boxes(slots, hh):
    return [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in slots]


# --------------------------------------------------------------------------- soundness gate (T23)
def cores_pairwise_disjoint(cores):
    """The certificate's bridge needs the #cores witnesses to be DISTINCT squares; A57's gate for
    the pins is that the pin cores stay pairwise disjoint (tree57.build_children docstring, T23).
    Enlarging a is only sound while that still holds.  Axis-aligned squares (tm ~ 0): they are
    disjoint iff separated on x or on y.  Returns (ok, worst_pair, worst_gap)."""
    worst, wp = None, None
    for i in range(len(cores)):
        for j in range(i + 1, len(cores)):
            ci, cj = cores[i], cores[j]
            gap = max(abs(ci.kx - cj.kx), abs(ci.ky - cj.ky)) - (ci.a + cj.a)
            if worst is None or gap < worst:
                worst, wp = gap, (i, j)
    return (worst is None or worst > 0), wp, worst
