#!/usr/bin/env python3
"""A43-H2: outward-rounded interval arithmetic + degree trigonometry.

SOUNDNESS CONTRACT.  Every routine here returns an interval that CONTAINS the true
value set.  Widening is always OUTWARD, so a downstream emptiness test can only
UNDER-kill (a kill is certain; a survival may be spurious).  Two mechanisms:

  * arithmetic: each float operation is pushed out by one ULP with math.nextafter;
  * transcendentals (cos/sin/atan/sqrt): after exact-in-degrees monotonicity
    analysis, endpoints are widened by SLOP_TRIG = 1e-9 (>= 1e-9 as the brief
    requires; the true libm error for cos/sin on |x| < 1e4 rad is < 1e-15, so 1e-9
    is ~6 orders of margin).  Degree-to-radian conversion error is inside that
    margin as well (|x| <= 4e2 deg -> 7 rad, ulp 8.9e-16, times pi/180 rounding).

h(phi) = (cos phi + sin phi)/2 is evaluated as (sqrt2/2) * cos(phi - 45 deg),
which is EXACT as a range (a single monotone-analysed cosine), not as an
independent sum of two intervals.
"""
from __future__ import annotations

import math

INF = math.inf
SLOP_TRIG = 1e-9


def dn(x):
    return math.nextafter(x, -INF)


def up(x):
    return math.nextafter(x, INF)


class I:
    """A closed real interval [lo, hi] with outward-rounded operations."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        if lo > hi:
            lo, hi = hi, lo
        self.lo = float(lo)
        self.hi = float(hi)

    def __repr__(self):
        return 'I(%.12g, %.12g)' % (self.lo, self.hi)

    def __add__(self, o):
        o = _co(o)
        return I(dn(self.lo + o.lo), up(self.hi + o.hi))

    def __sub__(self, o):
        o = _co(o)
        return I(dn(self.lo - o.hi), up(self.hi - o.lo))

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __mul__(self, o):
        o = _co(o)
        p = [self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi]
        return I(dn(min(p)), up(max(p)))

    __rmul__ = __mul__
    __radd__ = __add__

    def __rsub__(self, o):
        return _co(o) - self

    def maxabs(self):
        return max(abs(self.lo), abs(self.hi))

    def width(self):
        return up(self.hi - self.lo)

    def meets(self, o):
        o = _co(o)
        return self.lo <= o.hi and o.lo <= self.hi

    def inter(self, o):
        o = _co(o)
        lo, hi = max(self.lo, o.lo), min(self.hi, o.hi)
        return None if lo > hi else I(lo, hi)

    def hull(self, o):
        o = _co(o)
        return I(min(self.lo, o.lo), max(self.hi, o.hi))

    def contains(self, x):
        return self.lo <= x <= self.hi

    def as_list(self):
        return [self.lo, self.hi]


def _co(o):
    return o if isinstance(o, I) else I(o)


# --------------------------------------------------------------- constants
SQRT2 = I(dn(math.sqrt(2.0)), up(math.sqrt(2.0)))
SQRT2H = SQRT2 * I(0.5, 0.5)                       # sqrt(2)/2
# certified rational bracket, used by the self-tests
assert SQRT2.lo ** 2 < 2.0 < SQRT2.hi ** 2


# --------------------------------------------------------------- degree trig
def cos_deg(a, b):
    """Enclosure of {cos(x deg) : x in [a, b]} (a <= b).  Exact monotonicity
    analysis performed in DEGREES so no rad-conversion error can move an
    extremum across an endpoint."""
    if b < a:
        a, b = b, a
    if b - a >= 360.0:
        return I(-1.0, 1.0)
    vals = [math.cos(math.radians(a)), math.cos(math.radians(b))]
    n0 = math.ceil(a / 180.0)
    n1 = math.floor(b / 180.0)
    n = int(n0)
    while n <= n1:
        vals.append(1.0 if n % 2 == 0 else -1.0)
        n += 1
    lo = max(-1.0, min(vals) - SLOP_TRIG)
    hi = min(1.0, max(vals) + SLOP_TRIG)
    return I(lo, hi)


def sin_deg(a, b):
    return cos_deg(a - 90.0, b - 90.0)


def h_deg(a, b):
    """Enclosure of h(phi) = (cos phi + sin phi)/2 = (sqrt2/2) cos(phi - 45) over
    phi in [a, b] degrees.  Range on [0, 90] is [1/2, sqrt2/2]."""
    return SQRT2H * cos_deg(a - 45.0, b - 45.0)


def tan_half_deg(a, b):
    """Enclosure of t = tan(phi/2) over phi in [a, b] subset [0, 90]; monotone."""
    lo = math.tan(math.radians(max(0.0, a) / 2.0))
    hi = math.tan(math.radians(min(90.0, b) / 2.0))
    return I(max(0.0, dn(lo) - SLOP_TRIG), up(hi) + SLOP_TRIG)


# --------------------------------------------------------------- self-tests
def _selftest():
    out = []
    h0 = h_deg(0.0, 0.0)
    out.append(('h(0)=1/2', h0.lo <= 0.5 <= h0.hi and h0.width() < 1e-8))
    h45 = h_deg(45.0, 45.0)
    out.append(('h(45)=sqrt2/2',
                h45.lo <= math.sqrt(0.5) <= h45.hi and h45.width() < 1e-8))
    hfull = h_deg(0.0, 90.0)
    out.append(('h range [1/2, sqrt2/2]',
                hfull.lo <= 0.5 and hfull.hi >= math.sqrt(0.5)))
    c = cos_deg(-10.0, 10.0)
    out.append(('cos over 0 attains 1', c.hi >= 1.0 - 1e-12))
    c = cos_deg(170.0, 190.0)
    out.append(('cos over 180 attains -1', c.lo <= -1.0 + 1e-12))
    return out


if __name__ == '__main__':
    for name, ok in _selftest():
        print(('PASS ' if ok else 'FAIL ') + name)
