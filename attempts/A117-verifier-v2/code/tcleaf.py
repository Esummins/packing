"""A117 T2 -- Lemma TC (tilt coherence) as a CERTIFIED LEAF: the exact check.

LEMMA TC (docs/known_results.md 26c; A111 notes/leaf_shape.md).  Two interior-disjoint closed unit
squares with centre distance c and tilt difference D reduced mod 90 deg satisfy

        (1 + cos D + sin D) / 2  <=  c .

Proof sketch (the Lean statement of T2(b)): w(D) = |cos D| + |sin D| is the support half-width of a
unit square in the direction of the OTHER square's edge normal; interior-disjointness gives a
separating axis, and on any of the four edge normals of either square the separation of the centres
is at least 1/2 + w(D)/2.  The minimum over directions is attained on an edge normal (the face-to-
face placement), giving (1 + w(D))/2.

THE LEAF.  For two conditioned bins B1, B2 (a centre box x a tilt interval each) the leaf fires iff
EVERY pose pair overlaps.  TC gives the sufficient condition

        max centre distance over the two centre boxes  <  (1 + cos D_min + sin D_min) / 2

with D_min the MINIMUM tilt difference (mod 90, reduced to [0,45]) over the two tilt intervals.
A fire means: no packing has one square with its pose in B1 and a different square with its pose
in B2.

EXACTNESS.  Everything below is rational (`fractions.Fraction`) except cos and sin of D_min, which
are enclosed from BELOW by truncated alternating Taylor series evaluated at a rational enclosure of
D_min * pi / 180 (pi enclosed by a 50-digit truncation, so PI_LO < pi < PI_HI exactly).  cos is
decreasing and sin is increasing on [0, pi/2], so evaluating cos at the UPPER end and sin at the
LOWER end of the radian enclosure gives a valid lower bound for the whole enclosure.  The
comparison is then `cmax^2 < need_lo^2` between two exact rationals: the check can only UNDER-fire.

DOMAIN (A111 bug ii).  `tight_a` / the reduced-difference formula are stated for tilt intervals
inside [0, 90].  A box whose tilt interval straddles a multiple of 90 -- and, in particular, the
NEGATIVE interval a D4 reflection produces -- is split into its [0, 90] branches first, and the
leaf fires only if it fires for EVERY branch pair.  `normalise` asserts the domain and refuses
anything it cannot put inside [0, 90].

DISTINCTNESS.  Two boxes that share a pose may be witnessed by the SAME square, and then an
overlap statement proves nothing about a packing.  `pose_disjoint` is an exact rational check and
is part of the leaf hypothesis, exactly as in A111/A112's `octagon.pair_kill`.
"""
from __future__ import annotations

import math
import os
import random
import sys
from fractions import Fraction as F

os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

# pi, truncated (never rounded up) at 50 decimals: PI_LO < pi < PI_HI, exactly.
_PI_DIGITS = 314159265358979323846264338327950288419716939937510
PI_LO = F(_PI_DIGITS, 10 ** 50)
PI_HI = F(_PI_DIGITS + 1, 10 ** 50)
NINETY = F(90)
FORTYFIVE = F(45)
HALF = F(1, 2)
ZERO = F(0)
ONE = F(1)
_NTERMS = 12                    # alternating-series terms; |u| <= pi/4 < 1, terms fall like u^n/n!


class TCDomainError(ValueError):
    """the tilt interval could not be put inside [0, 90] (A111 bug ii)."""


# ------------------------------------------------------------------ exact trig lower bounds
def cos_lower(u):
    """A rational LOWER bound for cos(u), 0 <= u <= 1.  cos u = sum (-1)^k u^2k/(2k)!; the terms
    decrease for |u| <= 1, so a partial sum ENDING ON A SUBTRACTED TERM is a lower bound."""
    assert 0 <= u <= 1
    s = ONE
    term = ONE
    for k in range(1, 2 * _NTERMS + 2):          # last k is odd => last term subtracted
        term = term * u * u / ((2 * k - 1) * (2 * k))
        s = s - term if k % 2 else s + term
    return s


def sin_lower(u):
    """A rational LOWER bound for sin(u), 0 <= u <= 1, by the same alternating-series argument."""
    assert 0 <= u <= 1
    s = u
    term = u
    for k in range(1, 2 * _NTERMS + 2):
        term = term * u * u / ((2 * k) * (2 * k + 1))
        s = s - term if k % 2 else s + term
    return s


def need_lower(d_deg):
    """A rational LOWER bound for (1 + cos D + sin D)/2 at D = d_deg degrees, 0 <= D <= 45.
    D * pi/180 lies in [x_lo, x_hi]; cos decreases and sin increases on [0, pi/2]."""
    if not (ZERO <= d_deg <= FORTYFIVE):
        raise TCDomainError("reduced tilt difference %s outside [0, 45]" % d_deg)
    x_lo = d_deg * PI_LO / 180
    x_hi = d_deg * PI_HI / 180
    return (ONE + cos_lower(x_hi) + sin_lower(x_lo)) / 2


# ------------------------------------------------------------------ boxes
class Bin:
    """a conditioned bin: centre box [x0,x1] x [y0,y1] and tilt interval [th0, th1] in DEGREES.
    All five numbers are exact Fractions."""

    __slots__ = ("x0", "x1", "y0", "y1", "th0", "th1", "name")

    def __init__(self, x0, x1, y0, y1, th0, th1, name=""):
        self.x0, self.x1 = F(x0), F(x1)
        self.y0, self.y1 = F(y0), F(y1)
        self.th0, self.th1 = F(th0), F(th1)
        self.name = name
        if self.x1 < self.x0 or self.y1 < self.y0 or self.th1 < self.th0:
            raise TCDomainError("inverted bin %r" % name)

    def __repr__(self):
        return ("Bin(%s: x[%.6f,%.6f] y[%.6f,%.6f] th[%.6f,%.6f])"
                % (self.name, self.x0, self.x1, self.y0, self.y1, self.th0, self.th1))


def theta_branches(th0, th1):
    """[th0, th1] (degrees, ANY offset) as a list of intervals inside [0, 90].  Same rule as
    A111/A112 `octagon.theta_intervals`, but exact and with the domain ASSERTED afterwards."""
    th0, th1 = F(th0), F(th1)
    if th1 < th0:
        raise TCDomainError("inverted tilt interval [%s, %s]" % (th0, th1))
    if th1 - th0 >= NINETY:
        out = [(ZERO, NINETY)]
    else:
        a = th0 - NINETY * (th0 // NINETY)       # exact floor-mod, correct for negatives
        b = a + (th1 - th0)
        out = [(a, b)] if b <= NINETY else [(a, NINETY), (ZERO, b - NINETY)]
    for (u, v) in out:                            # A111 bug ii: the domain, asserted
        if not (ZERO <= u <= v <= NINETY):
            raise TCDomainError("branch [%s, %s] outside [0, 90]" % (u, v))
    return out


def normalise(b):
    """the bin as a list of bins with tilt inside [0, 90]; a claim about the bin holds only if it
    holds for EVERY branch."""
    return [Bin(b.x0, b.x1, b.y0, b.y1, u, v, b.name) for (u, v) in theta_branches(b.th0, b.th1)]


def pose_disjoint(a, b):
    """True if NO single pose lies in both bins, so the two bins cannot be the same square.
    Tilt is compared mod 90 (theta and theta + 90 are the same square).  Exact."""
    if a.x1 < b.x0 or b.x1 < a.x0 or a.y1 < b.y0 or b.y1 < a.y0:
        return True
    for off in (F(-180), F(-90), ZERO, F(90), F(180)):
        if not (a.th1 < b.th0 + off or b.th1 + off < a.th0):
            return False
    return True


def tilt_dev_min(a, b):
    """the exact MINIMUM over the two tilt intervals of the tilt difference reduced to [0, 45].
    f(d) = min(d mod 90, 90 - d mod 90) is piecewise linear with minima 0 at the multiples of 90
    and maximum 45 in between, so on an interval containing no multiple of 90 the minimum is at an
    endpoint."""
    lo, hi = a.th0 - b.th1, a.th1 - b.th0
    if hi - lo >= NINETY:
        return ZERO
    k = -((-lo) // NINETY)                        # ceil(lo / 90), exact
    if k * NINETY <= hi:                          # a multiple of 90 is attainable: tilts can agree
        return ZERO
    out = FORTYFIVE
    for d in (lo, hi):
        m = d - NINETY * (d // NINETY)
        out = min(out, m, NINETY - m)
    return out


def centre_dist_max_sq(a, b):
    """the exact SQUARED maximum of |c_a - c_b| over the two centre boxes (per axis the maximum is
    at opposite corners)."""
    dx = max(a.x1 - b.x0, b.x1 - a.x0, ZERO)
    dy = max(a.y1 - b.y0, b.y1 - a.y0, ZERO)
    return dx * dx + dy * dy


# ------------------------------------------------------------------ the leaf
def tc_fires(b1, b2, require_distinct=True):
    """Does Lemma TC prove that no packing has one square with its pose in b1 and a DIFFERENT
    square with its pose in b2?  Exact; one-sided (False = undecided, never a counter-proof).

    Returns (fired, detail).  detail carries, per [0,90] branch pair, the exact D_min, the exact
    lower bound for (1 + cos D + sin D)/2 and the exact max centre distance (squared)."""
    A, B = normalise(b1), normalise(b2)
    if require_distinct and not pose_disjoint(b1, b2):
        return False, dict(rule=None, reason="bins share a pose (same square possible)")
    cmax_sq = centre_dist_max_sq(b1, b2)
    branches = []
    fired = True
    for ba in A:
        for bb in B:
            d_min = tilt_dev_min(ba, bb)
            need_lo = need_lower(d_min)
            ok = cmax_sq < need_lo * need_lo
            branches.append(dict(a_tilt=[str(ba.th0), str(ba.th1)],
                                 b_tilt=[str(bb.th0), str(bb.th1)],
                                 dtheta_min_deg=str(d_min),
                                 dtheta_min_float=float(d_min),
                                 need_lower=str(need_lo), need_lower_float=float(need_lo),
                                 cmax_float=math.sqrt(float(cmax_sq)),
                                 slack_float=float(need_lo) - math.sqrt(float(cmax_sq)),
                                 fires=ok))
            fired = fired and ok
    return fired, dict(rule="TC", branches=branches, n_branch_pairs=len(branches),
                       cmax_sq=str(cmax_sq), cmax_float=math.sqrt(float(cmax_sq)),
                       min_slack_float=min(br["slack_float"] for br in branches),
                       pose_disjoint=True)


# ------------------------------------------------------------------ the sampling control
def _sq_axes(th_deg):
    r = math.radians(th_deg)
    c, s = math.cos(r), math.sin(r)
    return (c, s), (-s, c)


def _overlap_gap(p1, p2):
    """SAT on two unit squares given as (cx, cy, theta_deg).  Returns the max over the four edge
    normals of (|projected centre offset| - 1/2 - support half-width); < 0 means they overlap."""
    (c1x, c1y, t1), (c2x, c2y, t2) = p1, p2
    dx, dy = c2x - c1x, c2y - c1y
    worst = -1e18
    for (ax, ay) in _sq_axes(t1) + _sq_axes(t2):
        d = abs(dx * ax + dy * ay)
        r1 = (abs(ax * math.cos(math.radians(t1)) + ay * math.sin(math.radians(t1)))
              + abs(-ax * math.sin(math.radians(t1)) + ay * math.cos(math.radians(t1)))) / 2
        r2 = (abs(ax * math.cos(math.radians(t2)) + ay * math.sin(math.radians(t2)))
              + abs(-ax * math.sin(math.radians(t2)) + ay * math.cos(math.radians(t2)))) / 2
        worst = max(worst, d - r1 - r2)
    return worst


def sample_confirm(b1, b2, n=10000, seed=1117):
    """Confirm a fire by dense sampling: n pose pairs drawn uniformly from the two bins (corners
    and tilt endpoints forced in), each pair checked for overlap.  Returns
    (counterexamples, worst_gap, n)."""
    rng = random.Random(seed)
    f = lambda q: float(q)                                        # noqa: E731
    x0, x1, y0, y1 = f(b1.x0), f(b1.x1), f(b1.y0), f(b1.y1)
    u0, u1, v0, v1 = f(b2.x0), f(b2.x1), f(b2.y0), f(b2.y1)
    t0, t1 = f(b1.th0), f(b1.th1)
    s0, s1 = f(b2.th0), f(b2.th1)
    forced = [(a, b, c, d, e, g)
              for a in (x0, x1) for b in (y0, y1) for c in (t0, t1)
              for d in (u0, u1) for e in (v0, v1) for g in (s0, s1)]
    worst = -1e18
    bad = 0
    for i in range(n):
        if i < len(forced):
            a, b, c, d, e, g = forced[i]
        else:
            a = rng.uniform(x0, x1); b = rng.uniform(y0, y1); c = rng.uniform(t0, t1)
            d = rng.uniform(u0, u1); e = rng.uniform(v0, v1); g = rng.uniform(s0, s1)
        gap = _overlap_gap((a, b, c), (d, e, g))
        worst = max(worst, gap)
        if gap >= 0:
            bad += 1
    return bad, worst, n
