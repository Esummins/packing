"""A261 verifier arithmetic (numpy only): outward-rounded intervals, and first-order MEAN-VALUE quantities
    q = (B, Cn, G):  B  an enclosure of q over the tilt box (natural extension),
                     Cn an enclosure of q at the box centre,
                     G  enclosures over the box of the four partial derivatives (None = identically 0),
so that  q(phi) in Cn + sum_w G_w * [-r_w, r_w]  for every phi in the box (mean value theorem; for |.| the
generalised derivative [-1, 1] at a sign change).  Every elementary operation rounds outward (nextafter); cos / sin
values get an absolute pad of 2e-15 (>= 4 ulp at magnitude <= 2), so libm's sub-ulp error is covered.
"""
import numpy as np

INF = np.inf
PAD = 2e-15
PI4 = 0.7853981633974483


def dn(x):
    return np.nextafter(x, -INF)


def up(x):
    return np.nextafter(x, INF)


def iadd(a, b):
    return dn(a[0] + b[0]), up(a[1] + b[1])


def isub(a, b):
    return dn(a[0] - b[1]), up(a[1] - b[0])


def ineg(a):
    return -a[1], -a[0]


def imul(a, b):
    p = np.stack(np.broadcast_arrays(a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]))
    return dn(p.min(0)), up(p.max(0))


def iscale(y, a):
    """y >= 0, exact."""
    return dn(y * a[0]), up(y * a[1])


def icos(a):
    lo, hi = a
    cl, ch = np.cos(lo), np.cos(hi)
    mx = np.where(lo >= 0, cl, np.where(hi <= 0, ch, 1.0))
    mn = np.where(lo >= 0, ch, np.where(hi <= 0, cl, np.minimum(cl, ch)))
    return np.maximum(mn - PAD, -1.0), np.minimum(mx + PAD, 1.0)


def isin(a):                                   # arguments stay inside [-90, 90] degrees (+ 1e-15): monotone
    return np.maximum(np.sin(a[0]) - PAD, -1.0), np.minimum(np.sin(a[1]) + PAD, 1.0)


def iabs(a):
    lo, hi = a
    return np.where(lo >= 0, lo, np.where(hi <= 0, -hi, 0.0)), np.maximum(np.abs(lo), np.abs(hi))


def angle(tlo, thi):
    return dn(tlo * PI4 * (1 - 1e-15)), up(thi * PI4 * (1 + 1e-15))


# ------------------------------------------------------------------ mean-value quantities
def const(v):
    return ((v, v), (v, v), [None] * 4)


def gadd(g, h, sign=1.0):
    out = []
    for a, b in zip(g, h):
        if b is not None and sign < 0:
            b = ineg(b)
        out.append(a if b is None else b if a is None else iadd(a, b))
    return out


def qadd(p, q):
    return iadd(p[0], q[0]), iadd(p[1], q[1]), gadd(p[2], q[2])


def qsub(p, q):
    return isub(p[0], q[0]), isub(p[1], q[1]), gadd(p[2], q[2], -1.0)


def qneg(p):
    return ineg(p[0]), ineg(p[1]), [None if g is None else ineg(g) for g in p[2]]


def qmul(p, q):
    G = []
    for a, b in zip(p[2], q[2]):
        t1 = None if a is None else imul(a, q[0])
        t2 = None if b is None else imul(p[0], b)
        G.append(t1 if t2 is None else t2 if t1 is None else iadd(t1, t2))
    return imul(p[0], q[0]), imul(p[1], q[1]), G


def qscale(y, p):
    return iscale(y, p[0]), iscale(y, p[1]), [None if g is None else iscale(y, g) for g in p[2]]


def qcos(p):
    s = ineg(isin(p[0]))
    return icos(p[0]), icos(p[1]), [None if g is None else imul(s, g) for g in p[2]]


def qsin(p):
    c = icos(p[0])
    return isin(p[0]), isin(p[1]), [None if g is None else imul(c, g) for g in p[2]]


def qabs(p):
    lo, hi = p[0]
    sg = (np.where(lo >= 0, 1.0, -1.0), np.where(hi <= 0, -1.0, 1.0))
    return iabs(p[0]), iabs(p[1]), [None if g is None else imul(sg, g) for g in p[2]]


def wall(w, phi, mid, l):
    """the tilt variable of wall w and its monotone wall terms on [0, 45 deg]: cos, sin, w = cos + sin (increasing),
    d = cos - sin (decreasing), kappa = (l-1) sec + w (increasing; kappa' = (l-1) sec tan + d), with derivative
    enclosures taken from monotonicity, not from the generic rules."""
    lo, hi = phi
    one = [None] * 4

    def G(iv):
        g = list(one)
        g[w] = iv
        return g

    def f(fun, inc, dfun):
        a, b, m = fun(lo), fun(hi), fun(mid)
        B = (a - 2 * PAD, b + 2 * PAD) if inc else (b - 2 * PAD, a + 2 * PAD)
        return B, (m - 2 * PAD, m + 2 * PAD), G(dfun)
    c_, s_ = lambda x: np.cos(x), lambda x: np.sin(x)
    cosB, sinB = (c_(hi) - PAD, c_(lo) + PAD), (s_(lo) - PAD, s_(hi) + PAD)
    wB = (c_(lo) + s_(lo) - 2 * PAD, c_(hi) + s_(hi) + 2 * PAD)
    dB = (c_(hi) - s_(hi) - 2 * PAD, c_(lo) - s_(lo) + 2 * PAD)
    sectan = lambda x: np.sin(x) / np.cos(x) ** 2
    dk = ((l - 1) * sectan(lo) + dB[0] - 4 * PAD, (l - 1) * sectan(hi) + dB[1] + 4 * PAD)
    var = (phi, (mid, mid), G((1.0, 1.0)))
    return dict(var=var, cos=f(c_, False, ineg(sinB)), sin=f(s_, True, cosB),
                w=f(lambda x: c_(x) + s_(x), True, dB), d=f(lambda x: c_(x) - s_(x), False, ineg(wB)),
                kap=f(lambda x: (l - 1) / c_(x) + c_(x) + s_(x), True, dk))


def lower(p, r):
    """a lower bound of q over the box: the better of the natural one and the mean-value one."""
    mv = p[1][0]
    for g, rw in zip(p[2], r):
        if g is not None:
            mv = dn(mv - up(np.maximum(np.abs(g[0]), np.abs(g[1])) * rw))
    return np.maximum(p[0][0], mv)
