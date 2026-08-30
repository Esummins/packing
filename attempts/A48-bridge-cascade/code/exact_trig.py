# A48 exact rational trig: angles are rational points on the unit circle.
# (cos, sin) = ((1-t^2)/(1+t^2), 2t/(1+t^2)) for rational t = tan(angle/2).
# All downstream identities are polynomial in (cos, sin) -> exact Fractions.
from fractions import Fraction as F


def cs(t):
    """(cos, sin) of the angle with tan(half) = t (rational). Exact."""
    t = F(t)
    den = 1 + t * t
    return ((1 - t * t) / den, 2 * t / den)


def add(a, b):
    """Angle addition on (cos, sin) pairs. Exact."""
    (ca, sa), (cb, sb) = a, b
    return (ca * cb - sa * sb, sa * cb + ca * sb)


def sub(a, b):
    (cb, sb) = b
    return add(a, (cb, -sb))


def on_circle(a):
    (c, s) = a
    return c * c + s * s == 1


def gt(a, b):
    """a > b as angles in (0, 90), via sin(a-b) > 0. Both in first quadrant."""
    (c, s) = sub(a, b)
    return s > 0


def cross(p, q):
    return p[0] * q[1] - p[1] * q[0]


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1]
