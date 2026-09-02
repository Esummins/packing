#!/usr/bin/env python3
"""grainlib.py -- A76 grain-discharge machinery in t = tan(theta/2) coordinates.

Configuration z in R^34: z[3i] = cx_i, z[3i+1] = cy_i, z[3i+2] = t_i (i = 0..10),
z[33] = s (container side).  Rational trigonometry:
    cosT(t) = (1 - t^2)/(1 + t^2),   sinT(t) = 2t/(1 + t^2)     (theta = 2 arctan t).
Corner k of square i: q_k(i) = c_i + R(t_i) h_k, h_k in {(-1/2,-1/2),(1/2,-1/2),(1/2,1/2),(-1/2,1/2)}.

Row functions g(z) (rows written g >= 0 where they are inequalities):
  wall  : q_k(i)_x, q_k(i)_y, s - q_k(i)_x, s - q_k(i)_y            (containment)
  edge  : n_e(t_j) . (q_k(i) - c_j) - 1/2                              (corner k of i beyond edge e of j)
  dist  : |c_i - c_j|^2 - 1
  teq   : t_i - t_j                                                    (angle equality; equality only)
  pinx/piny : cx_i - (alpha + beta s) / cy_i - (alpha + beta s)        (slot pin; equality only)
  pint  : t_i                                                          (upright pin; equality only)

Two evaluation modes share the same code: exact points (Fraction), exact intervals (IV, the
outward-rounded dyadic kernel of A70's a36_check_exact.py), and floats (for design only).
Interval cos/sin/derivative enclosures use MONOTONICITY of the four rational functions
(proved in docstrings), no Taylor series.

Nothing here is trusted code: the certificates emitted with this library are re-checked by
certs/verify_grain.py (stdlib, standalone).  This module is the PRODUCER side + exploration.
"""
import json
import os
from fractions import Fraction

PREC = 330
GRID = 1 << PREC
NV = 34
S_IDX = 33
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]      # outward normal of edge e (body frame)
HERE = os.path.dirname(os.path.abspath(__file__))


def frac(s):
    return Fraction(s)


def fstr(x):
    x = Fraction(x)
    return '%d/%d' % (x.numerator, x.denominator)


# ------------------------------------------------------------------ exact interval kernel
def rdown(x):
    return Fraction((x.numerator * GRID) // x.denominator, GRID)


def rup(x):
    return Fraction(-((-x.numerator * GRID) // x.denominator), GRID)


class IV(object):
    """[lo, hi] with Fraction endpoints, outward-rounded to the 2^-PREC grid."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi, rnd=True):
        if rnd:
            lo, hi = rdown(lo), rup(hi)
        assert lo <= hi
        self.lo, self.hi = lo, hi

    @staticmethod
    def point(x):
        return IV(x, x)

    def __add__(self, b):
        if not isinstance(b, IV):
            b = IV.point(Fraction(b))
        return IV(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __sub__(self, b):
        if not isinstance(b, IV):
            b = IV.point(Fraction(b))
        return IV(self.lo - b.hi, self.hi - b.lo)

    def __rsub__(self, b):
        return IV.point(Fraction(b)) - self

    def __neg__(self):
        return IV(-self.hi, -self.lo, rnd=False)

    def __mul__(self, b):
        if not isinstance(b, IV):
            b = IV.point(Fraction(b))
        ps = (self.lo * b.lo, self.lo * b.hi, self.hi * b.lo, self.hi * b.hi)
        return IV(min(ps), max(ps))

    __rmul__ = __mul__

    def mag(self):
        return max(abs(self.lo), abs(self.hi))

    def width(self):
        return self.hi - self.lo

    def mid(self):
        return (self.lo + self.hi) / 2

    def __repr__(self):
        return 'IV(%.6g, %.6g)' % (float(self.lo), float(self.hi))


IZERO = IV.point(Fraction(0))
IONE = IV.point(Fraction(1))


# ------------------------------------------------------------------ rational trig
def cosT_pt(t):
    return (1 - t * t) / (1 + t * t)


def sinT_pt(t):
    return 2 * t / (1 + t * t)


def dcosT_pt(t):
    u = 1 + t * t
    return -4 * t / (u * u)


def dsinT_pt(t):
    u = 1 + t * t
    return 2 * (1 - t * t) / (u * u)


def _absmax(a, b):
    return max(abs(a), abs(b))


def _absmin(a, b):
    if a <= 0 <= b:
        return Fraction(0)
    return min(abs(a), abs(b))


def cosT_iv(v):
    """cosT(t) = (1-t^2)/(1+t^2) is even and strictly decreasing in |t| (d/dt = -4t/(1+t^2)^2):
    enclosure [cosT(max|t|), cosT(min|t|)]."""
    a, b = v.lo, v.hi
    return IV(cosT_pt(_absmax(a, b)), cosT_pt(_absmin(a, b)))


def sinT_iv(v):
    """sinT(t) = 2t/(1+t^2) is strictly increasing on [-1, 1] (d/dt = 2(1-t^2)/(1+t^2)^2 > 0)."""
    a, b = v.lo, v.hi
    assert -1 <= a and b <= 1
    return IV(sinT_pt(a), sinT_pt(b))


def dcosT_iv(v):
    """dcosT(t) = -4t/(1+t^2)^2 has derivative -4(1-3t^2)/(1+t^2)^3 < 0 for t^2 < 1/3:
    strictly decreasing on |t| < 1/sqrt(3); enclosure [dcosT(hi), dcosT(lo)]."""
    a, b = v.lo, v.hi
    assert 3 * a * a < 1 and 3 * b * b < 1, 'dcosT monotonicity needs |t| < 1/sqrt3'
    return IV(dcosT_pt(b), dcosT_pt(a))


def dsinT_iv(v):
    """dsinT(t) = 2(1-t^2)/(1+t^2)^2 has derivative -4t(3-t^2)/(1+t^2)^3, sign = -sign(t) on
    |t| < sqrt3: even, decreasing in |t|; enclosure [dsinT(max|t|), dsinT(min|t|)]."""
    a, b = v.lo, v.hi
    assert abs(a) < 1 and abs(b) < 1
    return IV(dsinT_pt(_absmax(a, b)), dsinT_pt(_absmin(a, b)))


def trig(t):
    """(cos, sin, dcos, dsin) for a Fraction, IV, or float t."""
    if isinstance(t, IV):
        return cosT_iv(t), sinT_iv(t), dcosT_iv(t), dsinT_iv(t)
    return cosT_pt(t), sinT_pt(t), dcosT_pt(t), dsinT_pt(t)


# ------------------------------------------------------------------ rows
def row_name(c):
    k = c['kind']
    if k == 'wall':
        return 'W%dc%d[%s]' % (c['i'], c['corner'], c['wall'])
    if k == 'edge':
        return 'E%dc%d-%de%d' % (c['i'], c['corner'], c['j'], c['edge'])
    if k == 'dist':
        return 'D%d-%d' % (c['i'], c['j'])
    if k == 'teq':
        return 'T%d-%d' % (c['i'], c['j'])
    if k == 'pinx':
        return 'PX%d' % c['i']
    if k == 'piny':
        return 'PY%d' % c['i']
    if k == 'pint':
        return 'PT%d' % c['i']
    if k == 'es':
        return 'ES'
    raise ValueError(k)


def corner_pos(z, i, corner):
    hx, hy = HALF[corner]
    co, si, _, _ = trig(z[3 * i + 2])
    return z[3 * i] + (hx * co - hy * si), z[3 * i + 1] + (hx * si + hy * co)


def dcorner_dt(z, i, corner):
    hx, hy = HALF[corner]
    _, _, dc, ds = trig(z[3 * i + 2])
    return hx * dc - hy * ds, hx * ds + hy * dc


def normal(z, j, edge):
    nhx, nhy = NHAT[edge]
    co, si, _, _ = trig(z[3 * j + 2])
    return nhx * co - nhy * si, nhx * si + nhy * co


def dnormal_dt(z, j, edge):
    nhx, nhy = NHAT[edge]
    _, _, dc, ds = trig(z[3 * j + 2])
    return nhx * dc - nhy * ds, nhx * ds + nhy * dc


def eval_row(z, c):
    k = c['kind']
    if k == 'wall':
        qx, qy = corner_pos(z, c['i'], c['corner'])
        w = c['wall']
        if w == 'x=0':
            return qx
        if w == 'y=0':
            return qy
        if w == 'x=s':
            return z[S_IDX] - qx
        if w == 'y=s':
            return z[S_IDX] - qy
        raise ValueError(w)
    if k == 'edge':
        i, j = c['i'], c['j']
        qx, qy = corner_pos(z, i, c['corner'])
        nx, ny = normal(z, j, c['edge'])
        return nx * (qx - z[3 * j]) + ny * (qy - z[3 * j + 1]) - Fraction(1, 2)
    if k == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - 1
    if k == 'teq':
        return z[3 * c['i'] + 2] - z[3 * c['j'] + 2]
    if k == 'pinx':
        return z[3 * c['i']] - (Fraction(c['alpha']) + Fraction(c['beta']) * z[S_IDX])
    if k == 'piny':
        return z[3 * c['i'] + 1] - (Fraction(c['alpha']) + Fraction(c['beta']) * z[S_IDX])
    if k == 'pint':
        return z[3 * c['i'] + 2]
    if k == 'es':
        return z[S_IDX] - z[S_IDX]
    raise ValueError(k)


def grad_row(z, c):
    """sparse gradient {index: value} of the row at z (point/interval/float)."""
    k = c['kind']
    one = IONE if isinstance(z[0], IV) else Fraction(1)
    mone = -one
    g = {}
    if k == 'wall':
        i = c['i']
        dx, dy = dcorner_dt(z, i, c['corner'])
        w = c['wall']
        if w == 'x=0':
            g[3 * i] = one
            g[3 * i + 2] = dx
        elif w == 'y=0':
            g[3 * i + 1] = one
            g[3 * i + 2] = dy
        elif w == 'x=s':
            g[3 * i] = mone
            g[3 * i + 2] = -dx
            g[S_IDX] = one
        elif w == 'y=s':
            g[3 * i + 1] = mone
            g[3 * i + 2] = -dy
            g[S_IDX] = one
        return g
    if k == 'edge':
        i, j = c['i'], c['j']
        nx, ny = normal(z, j, c['edge'])
        qx, qy = corner_pos(z, i, c['corner'])
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx, dhy = dcorner_dt(z, i, c['corner'])
        dnx, dny = dnormal_dt(z, j, c['edge'])
        g[3 * i] = nx
        g[3 * i + 1] = ny
        g[3 * j] = -nx
        g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if k == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        g[3 * i] = 2 * dx
        g[3 * i + 1] = 2 * dy
        g[3 * j] = -2 * dx
        g[3 * j + 1] = -2 * dy
        return g
    if k == 'teq':
        g[3 * c['i'] + 2] = one
        g[3 * c['j'] + 2] = mone
        return g
    if k == 'pinx':
        g[3 * c['i']] = one
        if Fraction(c['beta']) != 0:
            g[S_IDX] = -Fraction(c['beta']) * one
        return g
    if k == 'piny':
        g[3 * c['i'] + 1] = one
        if Fraction(c['beta']) != 0:
            g[S_IDX] = -Fraction(c['beta']) * one
        return g
    if k == 'pint':
        g[3 * c['i'] + 2] = one
        return g
    if k == 'es':
        g[S_IDX] = one
        return g
    raise ValueError(k)


def edge_aux(z, c):
    """(depth, tangential) owner-frame coordinates of the corner for an edge row."""
    i, j = c['i'], c['j']
    qx, qy = corner_pos(z, i, c['corner'])
    nx, ny = normal(z, j, c['edge'])
    wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
    return nx * wx + ny * wy, -ny * wx + nx * wy


# ------------------------------------------------------------------ boxes
def box(z0, r):
    """r: Fraction (uniform) or list of 34 Fractions (per coordinate)."""
    if isinstance(r, (list, tuple)):
        return [IV(x - ri, x + ri) for x, ri in zip(z0, r)]
    return [IV(x - r, x + r) for x in z0]


def radii(rc, rt, rs):
    """per-coordinate radii: centres rc, tilts rt, side rs."""
    out = []
    for i in range(11):
        out += [Fraction(rc), Fraction(rc), Fraction(rt)]
    out.append(Fraction(rs))
    return out


# ------------------------------------------------------------------ Trump data
def load_z0():
    d = json.load(open(os.path.join(HERE, '..', 'results', 'z0_t.json')))
    return [Fraction(x) for x in d['z0_t']]


def a22_rows():
    """A22's 42 curated rows (38 inequality-valid + 4 angle equalities), t-version."""
    d = json.load(open(os.path.join(HERE, '..', '..', 'A22-local-rigidity', 'results',
                                    'krawczyk_cert.json')))
    rows = []
    for c in d['constraints']:
        c = dict(c)
        if c['kind'] == 'angeq':
            c['kind'] = 'teq'
        c.pop('name', None)
        rows.append(c)
    return rows, d


TRUMP_SLOTS = {0: (Fraction(1, 2), 0, Fraction(1, 2), 0),
               1: (Fraction(3, 2), 0, Fraction(1, 2), 0),
               3: (Fraction(1, 2), 0, Fraction(3, 2), 0),
               2: (Fraction(-1, 2), 1, Fraction(1, 2), 0),
               5: (Fraction(-1, 2), 1, Fraction(-1, 2), 1)}   # (alpha_x, beta_x, alpha_y, beta_y)


def pin_rows(squares):
    out = []
    for i in squares:
        ax, bx, ay, by = TRUMP_SLOTS[i]
        out.append({'kind': 'pinx', 'i': i, 'alpha': fstr(ax), 'beta': str(bx)})
        out.append({'kind': 'piny', 'i': i, 'alpha': fstr(ay), 'beta': str(by)})
        out.append({'kind': 'pint', 'i': i})
    return out


def all_candidate_rows():
    """every corner-wall row and every corner-edge row (the completeness universe)."""
    out = []
    for i in range(11):
        for k in range(4):
            for w in ('x=0', 'y=0', 'x=s', 'y=s'):
                out.append({'kind': 'wall', 'i': i, 'corner': k, 'wall': w})
    for i in range(11):
        for j in range(11):
            if i == j:
                continue
            for k in range(4):
                for e in range(4):
                    out.append({'kind': 'edge', 'i': i, 'corner': k, 'j': j, 'edge': e})
    return out


# ------------------------------------------------------------------ Krawczyk
def jac_rows(z, rows):
    return [grad_row(z, c) for c in rows]


def krawczyk(z0, r, rows, Y, verbose=False):
    """K(B) = -Y F(z0) + (I - Y [J](B)) (B - z0) on box(z0, r) for the square system `rows`
    (len 34).  Returns (contracts, max|K_i|/r_i)."""
    B = box(z0, r)
    rr = r if isinstance(r, (list, tuple)) else [Fraction(r)] * NV
    zc = [IV.point(x) for x in z0]
    Fc = [eval_row(zc, c) for c in rows]
    Jrows = [grad_row(B, c) for c in rows]
    n = len(rows)
    assert n == NV
    # precompute the column entries: colvals[j] = list of (row index rr, value)
    cols = [[] for _ in range(NV)]
    for ri, g in enumerate(Jrows):
        for j, v in g.items():
            cols[j].append((ri, v))
    ok = True
    worst = Fraction(0)
    for i in range(NV):
        acc = IZERO
        Yi = Y[i]
        for k in range(n):
            if Yi[k] != 0:
                acc = acc + Yi[k] * Fc[k]
        Ki = -acc
        for j in range(NV):
            ssum = IZERO
            for (rr_, v) in cols[j]:
                if Yi[rr_] != 0:
                    ssum = ssum + Yi[rr_] * v
            m = IONE if i == j else IZERO
            Ki = Ki + (m - ssum) * IV(-rr[j], rr[j])
        ratio = Ki.mag() / rr[i]
        worst = max(worst, ratio)
        if not (Ki.lo > -rr[i] and Ki.hi < rr[i]):
            ok = False
    return ok, worst


# ------------------------------------------------------------------ float helpers
def to_float_z(z0):
    return [float(x) for x in z0]


def grad_matrix_float(z0f, rows):
    import numpy as np
    A = np.zeros((len(rows), NV))
    for ri, c in enumerate(rows):
        for j, v in grad_row(z0f, c).items():
            A[ri, j] = v
    return A


def rationalize_matrix(M, denom=10 ** 40):
    out = []
    for row in M:
        out.append([Fraction(int(round(float(v) * denom)), denom) for v in row])
    return out


def interval_grad_widths(z0, r, rows):
    """for each row: (dict of interval gradient entries over box, L1 half-width sum)."""
    B = box(z0, r)
    out = []
    for c in rows:
        g = grad_row(B, c)
        w = sum(v.width() / 2 for v in g.values())
        out.append((g, w))
    return out


# ------------------------------------------------------------------ certificate residual
def cert_residual(z0, r, rows, i, sigma, mu, nu, Gcache=None):
    """beta contribution: || sigma e_i + nu e_s - sum_k mu_k [grad g_k](box) ||_1 (interval mags).
    mu: dict {row index: Fraction}."""
    if Gcache is None:
        B = box(z0, r)
        Gcache = {k: grad_row(B, rows[k]) for k in mu}
    acc = {}
    for k, m in mu.items():
        if m == 0:
            continue
        for j, v in Gcache[k].items():
            acc[j] = acc.get(j, IZERO) + m * v
    l1 = Fraction(0)
    for j in range(NV):
        target = Fraction(sigma if j == i else 0) + (Fraction(nu) if j == S_IDX else 0)
        rho = IV.point(target) - acc.get(j, IZERO)
        l1 += rho.mag()
    return l1
