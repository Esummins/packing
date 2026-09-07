"""A119 T1 -- exact dyadic interval arithmetic for `check_local.py`.

Everything here is INTEGER arithmetic: a real number is carried as a pair of integers
(lo, hi) meaning the interval [lo / 2^P, hi / 2^P], and every operation rounds OUTWARD, so an
`Fx` always encloses the exact real value.  There are no floats in any decision path: floats
enter only through `of_float`, which is exact (an IEEE double IS a dyadic rational) whenever the
exponent fits, and rounds outward otherwise.

Provided: +, -, *, /, abs, min/max, comparison; rigorous cos / sin of a rational point (Taylor
with the alternating-series remainder) and of an interval (the product form
cos(m + d) = cos m cos d - sin m sin d, so the enclosure is second order in the interval width);
rigorous pi (Machin, alternating arctan series); and the support function
w(d) = |cos d| + |sin d| with its exact floor 1.
"""
from __future__ import annotations

from fractions import Fraction

P = 96                       # scale: a value v is stored as round(v * 2^P)
SCALE = 1 << P


def _floor(num, den):        # floor(num/den), den > 0
    return num // den


def _ceil(num, den):         # ceil(num/den), den > 0
    return -((-num) // den)


class Fx:
    """[lo, hi] / 2^P, lo <= hi, both Python ints."""
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = lo
        self.hi = lo if hi is None else hi
        assert self.lo <= self.hi

    # ---------- constructors
    @staticmethod
    def of_int(n):
        return Fx(n * SCALE)

    @staticmethod
    def of_frac(fr):
        fr = Fraction(fr)
        n, d = fr.numerator * SCALE, fr.denominator
        lo = n // d
        hi = lo if lo * d == n else lo + 1
        return Fx(lo, hi)

    @staticmethod
    def of_float(x):
        return Fx.of_frac(Fraction(x))

    def q_lo(self):
        return Fraction(self.lo, SCALE)

    def q_hi(self):
        return Fraction(self.hi, SCALE)

    def __repr__(self):
        return "[%.17g, %.17g]" % (self.lo / SCALE, self.hi / SCALE)

    def mid_float(self):
        return (self.lo + self.hi) / 2 / SCALE

    # ---------- arithmetic (outward)
    def __add__(self, o):
        return Fx(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        return Fx(self.lo - o.hi, self.hi - o.lo)

    def __neg__(self):
        return Fx(-self.hi, -self.lo)

    def __mul__(self, o):
        a, b, c, d = self.lo, self.hi, o.lo, o.hi
        ps = (a * c, a * d, b * c, b * d)          # products at scale 2^(2P)
        return Fx(_floor(min(ps), SCALE), _ceil(max(ps), SCALE))

    def scale_int(self, n):
        v = (self.lo * n, self.hi * n)
        return Fx(min(v), max(v))

    def div_int(self, n):
        assert n != 0
        a, b = (self.lo, self.hi) if n > 0 else (-self.hi, -self.lo)
        m = abs(n)
        return Fx(_floor(a, m), _ceil(b, m))

    def __truediv__(self, o):
        assert o.lo > 0 or o.hi < 0, "division by an interval containing 0"
        # 1/o then multiply
        inv = Fx(_floor(SCALE * SCALE, o.hi), _ceil(SCALE * SCALE, o.lo))
        return self * inv

    def abs_(self):
        if self.lo >= 0:
            return self
        if self.hi <= 0:
            return -self
        return Fx(0, max(-self.lo, self.hi))

    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def is_neg(self):
        return self.hi < 0

    def is_pos(self):
        return self.lo > 0


ZERO = Fx(0)
ONE = Fx.of_int(1)

HALF = Fx.of_frac(Fraction(1, 2))


def imin(a, b):
    return Fx(min(a.lo, b.lo), min(a.hi, b.hi))


def imax(a, b):
    return Fx(max(a.lo, b.lo), max(a.hi, b.hi))


def hull(a, b):
    return Fx(min(a.lo, b.lo), max(a.hi, b.hi))


# ---------------------------------------------------------------- pi (Machin)
def _arctan_inv(n, terms):
    """enclosure of arctan(1/n) from the alternating series sum (-1)^k / ((2k+1) n^(2k+1));
    the truncation error is bounded by the first omitted term."""
    s_lo = 0
    s_hi = 0
    acc = Fraction(0)
    x = Fraction(1, n)
    x2 = x * x
    term = x
    for k in range(terms):
        acc += term / (2 * k + 1) * (1 if k % 2 == 0 else -1) / 1
        term *= x2
    err = term / (2 * terms + 1)
    lo = Fx.of_frac(acc - err)
    hi = Fx.of_frac(acc + err)
    s_lo, s_hi = lo.lo, hi.hi
    return Fx(s_lo, s_hi)


PI = _arctan_inv(5, 60).scale_int(16) - _arctan_inv(239, 40).scale_int(4)
SQ2_HI = Fx.of_frac(Fraction(1414213562373095049, 10 ** 18)).hi + 1   # > sqrt 2
PI_HALF = PI.div_int(2)
TWO_PI = PI.scale_int(2)


# ---------------------------------------------------------------- cos / sin at a point
def _nterm(x):
    return 12 + int(4 * abs(x)) + 1


_NTERM = None


def cos_q(x: Fraction, nt=None):
    """enclosure of cos(x) for a rational x with |x| <= 8 (Taylor, alternating remainder)."""
    nt = nt or _nterm(x)
    xf = Fx.of_frac(x)
    x2 = xf * xf
    term = ONE
    acc = ONE
    for k in range(1, nt + 1):
        term = term * x2
        term = term.div_int((2 * k - 1) * (2 * k))
        acc = acc + (term if k % 2 == 0 else -term)
    # remainder bounded by the next term
    nxt = term * x2
    nxt = nxt.div_int((2 * nt + 1) * (2 * nt + 2))
    e = max(abs(nxt.lo), abs(nxt.hi))
    out = Fx(max(acc.lo - e, -SCALE), min(acc.hi + e, SCALE))
    return out


def sin_q(x: Fraction, nt=None):
    nt = nt or _nterm(x)
    xf = Fx.of_frac(x)
    x2 = xf * xf
    term = xf
    acc = xf
    for k in range(1, nt + 1):
        term = term * x2
        term = term.div_int((2 * k) * (2 * k + 1))
        acc = acc + (term if k % 2 == 0 else -term)
    nxt = term * x2
    nxt = nxt.div_int((2 * nt + 2) * (2 * nt + 3))
    e = max(abs(nxt.lo), abs(nxt.hi))
    return Fx(max(acc.lo - e, -SCALE), min(acc.hi + e, SCALE))


def _mults_in(lo: Fraction, hi: Fraction, den: int):
    """every integer m for which m * pi / den MIGHT lie in [lo, hi] (the enclosure of pi is used
    conservatively: an undecidable m is INCLUDED, which only widens the range enclosures below).
    Returns the list of such m."""
    plo, phi = Fraction(PI.lo, SCALE), Fraction(PI.hi, SCALE)
    step_lo, step_hi = plo / den, phi / den
    m0 = int((lo / step_lo).__floor__()) - 2
    m1 = int((hi / step_lo).__ceil__()) + 2
    out = []
    for m in range(m0, m1 + 1):
        a, b = m * step_lo, m * step_hi
        if m < 0:
            a, b = b, a
        if b >= lo and a <= hi:
            out.append(m)
    return out


def cos_iv(lo: Fraction, hi: Fraction):
    """EXACT range of cos over [lo, hi] (outward rounded): the extrema are at the endpoints and
    at the multiples of pi inside (cos = +1 at even multiples, -1 at odd)."""
    if hi - lo >= 2 * Fraction(PI.lo, SCALE):
        return Fx(-SCALE, SCALE)
    a, b = cos_q(lo), cos_q(hi)
    l, h = min(a.lo, b.lo), max(a.hi, b.hi)
    for m in _mults_in(lo, hi, 1):
        if m % 2 == 0:
            h = SCALE
        else:
            l = -SCALE
    return Fx(l, h)


def sin_iv(lo: Fraction, hi: Fraction):
    """EXACT range of sin over [lo, hi]: extrema at the endpoints and at the odd multiples of
    pi/2 inside (+1 at 1 mod 4, -1 at 3 mod 4)."""
    if hi - lo >= 2 * Fraction(PI.lo, SCALE):
        return Fx(-SCALE, SCALE)
    a, b = sin_q(lo), sin_q(hi)
    l, h = min(a.lo, b.lo), max(a.hi, b.hi)
    for m in _mults_in(lo, hi, 2):
        if m % 2 == 0:
            continue
        if m % 4 == 1:
            h = SCALE
        else:
            l = -SCALE
    return Fx(l, h)


def w_iv(lo: Fraction, hi: Fraction):
    """EXACT range of w(d) = |cos d| + |sin d| on [lo, hi] (a111lib.w_range, in exact arithmetic).
    w has period pi/2, equals 1 at the multiples of pi/2 and sqrt2 at pi/4 + k pi/2, and is
    monotone between consecutive multiples of pi/4, so the extrema are at the endpoints and at
    the multiples of pi/4 inside."""
    def at(t):
        return cos_q(t).abs_() + sin_q(t).abs_()
    a, b = at(lo), at(hi)
    l, h = min(a.lo, b.lo), max(a.hi, b.hi)
    for m in _mults_in(lo, hi, 4):
        if m % 2 == 0:                     # a multiple of pi/2: w = 1 exactly (the global min)
            l = min(l, SCALE)
        else:                              # pi/4 + k pi/2: w = sqrt2 exactly (the global max)
            h = max(h, SQ2_HI)
    return Fx(max(l, SCALE), min(h, SQ2_HI))
