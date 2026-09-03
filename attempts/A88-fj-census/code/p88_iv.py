"""fastiv.py -- A88: fast float interval arithmetic with outward padding.

NOT a certificate engine.  Every operation pads its result outward by
    PAD_REL * max(|lo|,|hi|) + PAD_ABS
with PAD_REL = 4*eps (eps = 2.22e-16) and PAD_ABS = 1e-300, which dominates the
<= 0.5 ulp rounding error of one IEEE-754 double operation by a factor ~ 18.
This is used because the A88 deliverable is a COST measurement; the rigorous
mpmath.iv path (t3lib.row_grad) is used only for spot cross-checks.

Rows are evaluated in the CORE variable layout of p88_struct.Structure:
value + gradient w.r.t. the D core variables, both as intervals.
"""
from __future__ import annotations

import math

PAD_REL = 8.9e-16
PAD_ABS = 1e-300


def _pad(lo, hi):
    r = PAD_REL * max(abs(lo), abs(hi)) + PAD_ABS
    return (lo - r, hi + r)


def add(a, b):
    return _pad(a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return _pad(a[0] - b[1], a[1] - b[0])


def neg(a):
    return (-a[1], -a[0])


def mul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return _pad(min(p), max(p))


def smul(a, c):
    if c >= 0:
        return _pad(a[0] * c, a[1] * c)
    return _pad(a[1] * c, a[0] * c)


def contains0(a, tol=0.0):
    return a[0] - tol <= 0.0 <= a[1] + tol


def width(a):
    return a[1] - a[0]


def mid(a):
    return 0.5 * (a[0] + a[1])


def isect(a, b):
    lo = max(a[0], b[0]); hi = min(a[1], b[1])
    return None if lo > hi else (lo, hi)


_TWOPI = 2.0 * math.pi
_HALFPI = math.pi / 2.0


def icos(t):
    """Enclosure of cos over [t0,t1]."""
    lo, hi = t
    if hi - lo >= _TWOPI:
        return (-1.0, 1.0)
    a = math.cos(lo); b = math.cos(hi)
    mn = min(a, b); mx = max(a, b)
    # extrema of cos at multiples of pi
    k0 = math.ceil(lo / math.pi)
    k = k0
    while k * math.pi <= hi and k < k0 + 4:
        v = 1.0 if (k % 2 == 0) else -1.0
        mn = min(mn, v); mx = max(mx, v)
        k += 1
    return _pad(max(-1.0, mn), min(1.0, mx))


def isin(t):
    return icos((t[0] - _HALFPI, t[1] - _HALFPI))
