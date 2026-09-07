"""A131 T1 -- PIN-CLIP: shrink a node's centre box to the pin-feasible region, per tilt sub-bin.

OFFLINE / MEASUREMENT + IN-VITRO.  Nothing here is wired into A57's emission; nothing here writes
outside attempts/A131-pin-clip.  tree57.py, trim57.py, pinguard.py and the frozen verifiers are
read-only for this attempt.

------------------------------------------------------------------------------------------------
THE RULE (T5''' -- pin-clip), and why it is sound
------------------------------------------------------------------------------------------------
A node's hypothesis is "some square Q0 of the packing has (centre, tilt) in the box
B = [x0,x1] x [y0,y1] x [th0,th1]", on top of k pinned squares fixed by the class.  Pin i
contributes its GUARANTEED CORE K_i: the axis-aligned square of half-side a_P = 1/2 - delta
centred at the slot, contained in the pinned square wherever that square sits inside its slack
box (delta = 1e-2 as deployed; A57's slack box has half-width delta/sqrt(2), so a_P = 1/2 - delta
is conservative by 0.003).

For a fixed tilt theta, the unit square Q(c, theta) and K_i have interiors that MEET iff all four
separating-axis tests fail, i.e. (writing d = c - slot, w = |cos| + |sin|, u = (cos, sin),
v = (-sin, cos)):

    |d_x| < A,  |d_y| < A,  |d.u| < B,  |d.v| < B,      A = w/2 + a_P,  B = 1/2 + a_P w

-- c lies in the interior of an OCTAGON about the slot (the Minkowski sum K_i (+) -Q(theta)).
Strict inequalities: a mere touch is interior-disjoint and carries no contradiction.

T5'' (trim57) kills a whole tilt sub-interval when the WHOLE centre box lies in ONE pin's octagon
for every tilt in it.  PIN-CLIP is the same geometry applied pointwise instead of box-wise:

    D_i(t0,t1) := { d : d is in pin i's octagon at EVERY tilt in the sub-bin }

    a centre c with c - slot_i in D_i for some i admits NO tilt in the sub-bin, so it carries no
    packing under the node's hypothesis and may be DISCARDED.

The node then carries (clipped centre box, tilt sub-bin) -- the same object T5'' produces, with
the centre box narrowed too.  The frozen verifiers see an ordinary (smaller) box; the certificate
format is unchanged.

D_i is CONVEX: it is the intersection of the two slabs |d_x| <= A_min, |d_y| <= A_min with the two
sets max_theta |d.u(theta)| <= B_min and max_theta |d.v(theta)| <= B_min, each a max of linear
functionals, hence convex.  Convexity is what makes the clip cheap: a vertical segment of the
centre box lies in D_i iff both its endpoints do, so the dead slab hanging off each side of the
box is found by bisection on two corner points.

CONSERVATISMS (all in the sound direction -- the clip removes less than the truth):
  (a) only SINGLE-pin domination.  A centre killed by pin 1 at low tilts and pin 2 at high tilts
      is kept.  (Fixing this needs the union-over-pins-of-octagons intersected over tilts, which
      is not convex.)
  (b) NONE -- the intersection over tilts is computed EXACTLY (see dead_q); the first version of
      this module used the sub-bin worst case (A, B at w_min against max |d.n|), which is sound
      but loses 34 of the 674 T5' logic kills at nsub = 1.  See notes/lemmas-T5triple.md.
  (c) only the four AXIS-ALIGNED dead slabs are removed; a dead region strictly inside the box
      does not shrink the bounding box.
  (d) the rational tilt interval [t_lo(th0), t_hi(th1)] is a SUPERSET of the node's tilt range,
      so "dead at every tilt" is tested over more tilts than the node actually carries.
  (e) the rational centre box is a SUPERSET of the float box (endpoints rounded outward).
Finer sub-bins strictly help: (b) tightens as the sub-bin narrows.

CONTAINER.  A centre also needs w(theta)/2 <= c <= s - w(theta)/2 in each coordinate to sit in
[0,s]^2 at that tilt.  Over the sub-bin the least restrictive of these is at w_min, so centres
outside [w_min/2, s - w_min/2]^2 are discardable too.  (On A57's interior boxes this never binds;
it is included because a deployed rule must have it.)

PARENT GUARD (the one soundness trap, and trim57 does not carry it because tree57 calls
pinguard.classify first).  If a pin's placement (px, py, 0 deg) lies in the box and the tilt bin
touches 0 or 90 -- theta = 90 is the SAME square as theta = 0 -- then the square witnessing the
box may BE that pin, and "Q meets K_i" is not a contradiction.  clip_node() REFUSES to clip such
a node and returns reason "parent".  A57's interior census has zero parent boxes (lemmas.md T5),
so this never fires there, but a deployed rule must assert it.

------------------------------------------------------------------------------------------------
ARITHMETIC -- exact rational, no transcendentals
------------------------------------------------------------------------------------------------
Tilts are carried as t = tan(theta/2), which is how A57's cover is built (lemmas.md T2), so
cos theta = (1 - t^2)/(1 + t^2) and sin theta = 2t/(1 + t^2) are EXACT rationals at every sub-bin
endpoint (caselp.cos_sin_t).  Hence A, B, w_min, every projection d.u, d.v and every comparison
is exact Fraction arithmetic.  There is no epsilon anywhere in the decision; the only float in the
pipeline is the BISECTION SEARCH for the slab boundary, and every boundary it proposes is then
CERTIFIED by the exact predicate (and walked back until it certifies).  `--engine exact` runs the
bisection in Fractions too, for cross-checking.

w_min over a sub-bin: w = cos + sin = sqrt(2) sin(theta + 45 deg) is concave on [0, 90] and t is
increasing in theta, so the minimum over a sub-interval is at an endpoint -- exact.

max_theta |d.u(theta)|: d.u(theta) = r cos(theta - phi), whose extremum in theta is where
d.v(theta) = 0.  With the sub-bin narrower than 180 deg there is at most one such theta, and it
lies inside iff d.v changes sign between the endpoints -- an exact sign test.  There the value is
+-|d|, so the comparison against B is done as r^2 <= B^2, again exact.  Otherwise the max is at an
endpoint.  Symmetrically for d.v, whose extremum is where d.u = 0.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
A57_CODE = os.path.abspath(os.path.join(HERE, "..", "..", "A57-shadow-trees", "code"))
if A57_CODE not in sys.path:
    sys.path.insert(0, A57_CODE)

from caselp import t_lo, t_hi, cos_sin_t          # noqa: E402  (read-only import of A57's helpers)

DELTA = Fr(1, 100)                 # pin slack as deployed (tree57 --pin_delta 0.01)
A_PIN = Fr(1, 2) - DELTA           # 49/100: half-side of a pin's guaranteed core
S_RAT = Fr(969271, 250000)         # s0 = 3.877084
XDEN = 10 ** 9                     # centre-coordinate rounding grid (matches caselp.XDEN)
BISECT = 44                        # bisection steps for a slab boundary
BACKOFF = Fr(1, 10 ** 9)           # step by which a float-proposed boundary is walked back


# ------------------------------------------------------------------ rational box plumbing
def q_dn(x):
    """rational <= x on the 1e-9 grid."""
    return Fr(math.floor(float(x) * XDEN) - 1, XDEN)


def q_up(x):
    """rational >= x on the 1e-9 grid."""
    return Fr(math.ceil(float(x) * XDEN) + 1, XDEN)


def outer_rect(box):
    """the rational rectangle CONTAINING the float centre box (conservatism (e))."""
    return (q_dn(box.x0), q_up(box.x1), q_dn(box.y0), q_up(box.y1))


def area(rect):
    if rect is None:
        return Fr(0)
    x0, x1, y0, y1 = rect
    if x1 <= x0 or y1 <= y0:
        return Fr(0)
    return (x1 - x0) * (y1 - y0)


def sub_bins(th0, th1, n):
    """n rational tilt sub-bins in t = tan(theta/2), covering [t_lo(th0), t_hi(th1)] exactly.

    The union is a SUPERSET of the node's tilt range (conservatism (d))."""
    T0, T1 = t_lo(th0), t_hi(th1)
    if T1 <= T0:
        return [(T0, T1)]
    return [(T0 + (T1 - T0) * Fr(i, n), T0 + (T1 - T0) * Fr(i + 1, n)) for i in range(n)]


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


# ------------------------------------------------------------------ octagon parameters
class Oct:
    """the sub-bin's octagon parameters for one pin-independent tilt range (exact)."""

    __slots__ = ("A", "c0", "s0", "c1", "s1", "wmin", "t0", "t1", "a_pin",
                 "fA", "fa_pin", "fc0", "fs0", "fc1", "fs1")

    def __init__(self, t0, t1, a_pin=A_PIN):
        self.t0, self.t1, self.a_pin = t0, t1, a_pin
        c0, s0 = cos_sin_t(t0)
        c1, s1 = cos_sin_t(t1)
        self.c0, self.s0, self.c1, self.s1 = c0, s0, c1, s1
        self.wmin = min(c0 + s0, c1 + s1)          # concave in theta on [0,90]: min at an endpoint
        self.A = self.wmin / 2 + a_pin
        self.fA, self.fa_pin = float(self.A), float(a_pin)
        self.fc0, self.fs0 = float(c0), float(s0)
        self.fc1, self.fs1 = float(c1), float(s1)


_HALF = Fr(1, 2)
_QUARTER = Fr(1, 4)


def _m_lt_half(P, Q, c0, s0, c1, s1):
    """EXACT: is max over theta in the sub-bin of (P cos theta + Q sin theta) < 1/2 ?

    g(theta) = P cos + Q sin = r cos(theta - phi) has g'(theta) = Q cos - P sin.  With the sub-bin
    narrower than 180 deg there is at most one interior critical point; it is a MAXIMUM iff g'
    goes + -> -, and there g = +r.  Otherwise the maximum is at an endpoint.  The comparison
    r < 1/2 is done as r^2 < 1/4, so nothing leaves the rationals."""
    d0 = Q * c0 - P * s0
    d1 = Q * c1 - P * s1
    if d0 >= 0 and d1 <= 0 and (d0 > 0 or d1 < 0):
        return P * P + Q * Q < _QUARTER
    v0 = P * c0 + Q * s0
    v1 = P * c1 + Q * s1
    return (v0 if v0 > v1 else v1) < _HALF


def dead_q(dx, dy, o):
    """EXACT: is d = (dx, dy) in pin's octagon at EVERY tilt of the sub-bin?  Fractions in.

    The four separating axes of Q(c, theta) vs the pin core (0, 90, theta, theta+90) fail
    simultaneously iff, with a = a_P and w = cos + sin (both cos, sin >= 0 on [0, 90]):

        |d_x| < w/2 + a          <=>  |d_x| < w_min/2 + a            (exact: min w at an endpoint)
        |d_y| < w/2 + a          <=>  |d_y| < w_min/2 + a
        |d.u| < 1/2 + a w        <=>  ( d_x - a) cos + ( d_y - a) sin < 1/2  and
                                      (-d_x - a) cos + (-d_y - a) sin < 1/2
        |d.v| < 1/2 + a w        <=>  ( d_y - a) cos + (-d_x - a) sin < 1/2  and
                                      (-d_y - a) cos + ( d_x - a) sin < 1/2

    Each of the last four is a single sinusoid in theta, so its max over the sub-bin is exact and
    the whole test is the EXACT intersection over tilts of the forbidden octagons -- no
    sub-bin-worst-case conservatism at all."""
    if not (-o.A < dx < o.A) or not (-o.A < dy < o.A):
        return False
    a = o.a_pin
    c0, s0, c1, s1 = o.c0, o.s0, o.c1, o.s1
    return (_m_lt_half(dx - a, dy - a, c0, s0, c1, s1) and
            _m_lt_half(-dx - a, -dy - a, c0, s0, c1, s1) and
            _m_lt_half(dy - a, -dx - a, c0, s0, c1, s1) and
            _m_lt_half(-dy - a, dx - a, c0, s0, c1, s1))


def _m_lt_half_f(P, Q, c0, s0, c1, s1):
    d0 = Q * c0 - P * s0
    d1 = Q * c1 - P * s1
    if d0 >= 0.0 and d1 <= 0.0 and (d0 > 0.0 or d1 < 0.0):
        return P * P + Q * Q < 0.25
    v0 = P * c0 + Q * s0
    v1 = P * c1 + Q * s1
    return (v0 if v0 > v1 else v1) < 0.5


def dead_f(dx, dy, o):
    """float twin of dead_q, used ONLY to search for the slab boundary (never to decide)."""
    if not (-o.fA < dx < o.fA) or not (-o.fA < dy < o.fA):
        return False
    a = o.fa_pin
    c0, s0, c1, s1 = o.fc0, o.fs0, o.fc1, o.fs1
    return (_m_lt_half_f(dx - a, dy - a, c0, s0, c1, s1) and
            _m_lt_half_f(-dx - a, -dy - a, c0, s0, c1, s1) and
            _m_lt_half_f(dy - a, -dx - a, c0, s0, c1, s1) and
            _m_lt_half_f(-dy - a, dx - a, c0, s0, c1, s1))


# ------------------------------------------------------------------ the clip
def _bisect_boundary(dead_lo, lo, hi, pred_f, pred_q, stats):
    """largest v in [lo, hi] with pred(v) true, given pred(lo) true.

    Search in float, then CERTIFY with the exact predicate, walking back by BACKOFF until it
    certifies (at most 4 walks; otherwise return lo, i.e. no clip beyond the known-dead point)."""
    flo, fhi = float(lo), float(hi)
    if pred_f(fhi):
        cand = hi
    else:
        a, b = flo, fhi
        for _ in range(BISECT):
            m = 0.5 * (a + b)
            if pred_f(m):
                a = m
            else:
                b = m
        cand = Fr(math.floor(a * XDEN * 1024), XDEN * 1024)   # rational just below the float root
        if cand < lo:
            cand = lo
    for _ in range(5):
        stats["exact_calls"] += 1
        if pred_q(cand):
            return cand
        stats["backoffs"] += 1
        cand -= BACKOFF
        if cand <= lo:
            return lo
    return lo


def _clip_one_pin(rect, slot, o, stats):
    """clip `rect` against ONE pin's dead set D_i.  -> rect or None (EMPTY)."""
    sx, sy = slot
    x0, x1, y0, y1 = rect

    def dq(px, py):
        return dead_q(px - sx, py - sy, o)

    def df(px, py):
        return dead_f(px - float(sx), py - float(sy), o)

    stats["exact_calls"] += 4
    if dq(x0, y0) and dq(x1, y0) and dq(x0, y1) and dq(x1, y1):
        return None                                             # whole rect dead: T5''-style kill

    # left / right: a vertical segment {x} x [y0,y1] is in D_i iff both endpoints are (convexity)
    if dq(x0, y0) and dq(x0, y1):
        x0 = _bisect_boundary(True, x0, x1,
                              lambda v: df(v, float(y0)) and df(v, float(y1)),
                              lambda v: dq(v, y0) and dq(v, y1), stats)
    if dq(x1, y0) and dq(x1, y1):
        neg = _bisect_boundary(True, -x1, -x0,
                               lambda v: df(-v, float(y0)) and df(-v, float(y1)),
                               lambda v: dq(-v, y0) and dq(-v, y1), stats)
        x1 = -neg
    if x1 <= x0:
        return None
    # bottom / top on the (possibly narrowed) rect
    if dq(x0, y0) and dq(x1, y0):
        y0 = _bisect_boundary(True, y0, y1,
                              lambda v: df(float(x0), v) and df(float(x1), v),
                              lambda v: dq(x0, v) and dq(x1, v), stats)
    if dq(x0, y1) and dq(x1, y1):
        neg = _bisect_boundary(True, -y1, -y0,
                               lambda v: df(float(x0), -v) and df(float(x1), -v),
                               lambda v: dq(x0, -v) and dq(x1, -v), stats)
        y1 = -neg
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, x1, y0, y1)


def clip_rect(rect, slots, o, s_rat=S_RAT, passes=3, stats=None):
    """clip a rational rect against every pin and the container, for one tilt sub-bin."""
    if stats is None:
        stats = {"exact_calls": 0, "backoffs": 0}
    half = o.wmin / 2
    x0, x1, y0, y1 = rect
    x0, y0 = max(x0, half), max(y0, half)
    x1, y1 = min(x1, s_rat - half), min(y1, s_rat - half)
    if x1 <= x0 or y1 <= y0:
        return None, stats
    rect = (x0, x1, y0, y1)
    for _ in range(passes):
        before = rect
        for sl in slots:
            rect = _clip_one_pin(rect, sl, o, stats)
            if rect is None:
                return None, stats
        if rect == before:
            break
    return rect, stats


def realizes_pin(box, slots, tol=1e-9):
    """the pinguard 'parent' case: a pin placement (px, py, 0 deg) inside the box."""
    th_ok = (box.th0 - 1e-9 <= 0.0 <= box.th1 + 1e-9) or (box.th0 - 1e-9 <= 90.0 <= box.th1 + 1e-9)
    if not th_ok:
        return None
    for (px, py) in slots:
        if box.x0 - tol <= float(px) <= box.x1 + tol and box.y0 - tol <= float(py) <= box.y1 + tol:
            return (px, py)
    return None


def clip_node(box, slots, nsub=1, s_rat=S_RAT, a_pin=A_PIN):
    """PIN-CLIP one node at one sub-bin resolution.

    -> dict(refused, reason, bins=[(t0,t1,rect|None)], kept_vol, kept_union, union_rect, empty,
            n_empty, stats)

    kept_vol   : fraction of the (centre x tilt) volume kept, summed over sub-bins
    kept_union : area(bounding box of the union of the clipped rects) / area(original), i.e. what
                 the node keeps if the tree wants ONE child instead of nsub of them
    """
    slots_q = [(Fr(str(px)), Fr(str(py))) for (px, py) in slots]   # slots are exact decimals
    if realizes_pin(box, slots) is not None:
        return dict(refused=True, reason="parent", bins=[], kept_vol=1.0, kept_union=1.0,
                    union_rect=None, empty=False, n_empty=0,
                    stats={"exact_calls": 0, "backoffs": 0})
    rect0 = outer_rect(box)
    A0 = area(rect0)
    bins = sub_bins(box.th0, box.th1, nsub)
    Ttot = bins[-1][1] - bins[0][0]
    stats = {"exact_calls": 0, "backoffs": 0}
    out, kept_vol, n_empty = [], Fr(0), 0
    ux0 = ux1 = uy0 = uy1 = None
    for (t0, t1) in bins:
        o = Oct(t0, t1, a_pin)
        r, _ = clip_rect(rect0, slots_q, o, s_rat, stats=stats)
        out.append((t0, t1, r))
        wgt = (t1 - t0) / Ttot if Ttot > 0 else Fr(1, len(bins))
        if r is None:
            n_empty += 1
            continue
        kept_vol += wgt * (area(r) / A0 if A0 > 0 else Fr(0))
        if ux0 is None:
            ux0, ux1, uy0, uy1 = r
        else:
            ux0, ux1 = min(ux0, r[0]), max(ux1, r[1])
            uy0, uy1 = min(uy0, r[2]), max(uy1, r[3])
    union = None if ux0 is None else (ux0, ux1, uy0, uy1)
    return dict(refused=False, reason=None, bins=out, kept_vol=float(kept_vol),
                kept_union=(float(area(union) / A0) if union is not None and A0 > 0 else 0.0),
                union_rect=union, empty=(union is None), n_empty=n_empty, stats=stats)


# ------------------------------------------------------------------ pointwise feasibility (sampling)
def pin_free(cx, cy, th_deg, slots, a_pin=float(A_PIN), s=float(S_RAT)):
    """float: is Q(c, theta) interior-disjoint from every pin core AND inside [0,s]^2?"""
    r = math.radians(th_deg)
    c, sn = math.cos(r), math.sin(r)
    w = abs(c) + abs(sn)
    if cx < w / 2 or cy < w / 2 or cx > s - w / 2 or cy > s - w / 2:
        return False
    A = w / 2 + a_pin
    B = 0.5 + a_pin * w
    for (px, py) in slots:
        dx, dy = cx - float(px), cy - float(py)
        if abs(dx) >= A or abs(dy) >= A:
            continue
        if abs(dx * c + dy * sn) >= B or abs(dy * c - dx * sn) >= B:
            continue
        return False                                   # interiors meet this pin core
    return True


def pin_depth(cx, cy, th_deg, slots, a_pin=float(A_PIN)):
    """float: max over pins of the SAT overlap depth between Q(c, theta) and the pin core.

    <= 0 means interior-disjoint from every pin.  A stored LP support column may show a POSITIVE
    depth up to caselp.EPS_CORE = 2e-3: the LP drops a row only when it penetrates a core by more
    than that on every axis (caselp's module docstring), so shallow penetration is a deliberate
    conservatism of the row filter, not a violation."""
    r = math.radians(th_deg)
    c, sn = math.cos(r), math.sin(r)
    w = abs(c) + abs(sn)
    A = w / 2 + a_pin
    B = 0.5 + a_pin * w
    best = -1e9
    for (px, py) in slots:
        dx, dy = cx - float(px), cy - float(py)
        d = min(A - abs(dx), A - abs(dy),
                B - abs(dx * c + dy * sn), B - abs(dy * c - dx * sn))
        best = max(best, d)
    return best
