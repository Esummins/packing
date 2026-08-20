"""
a22lib.py -- shared machinery for A22-local-rigidity.

Rigorous strict local optimality of Trump packing (n = 11).

Variable vector z in R^34:
    z[3i+0] = cx_i, z[3i+1] = cy_i, z[3i+2] = theta_i   (i = 0..10),  z[33] = s.

Curated smooth constraint set (all written as g(z) >= 0, all ACTIVE at Trump):
  wall  : corner coordinate vs wall,  g = q_x, q_y, s - q_x or s - q_y.
  edge  : corner q of square i against edge e of square j,
          g = n . (q - c_j) - 1/2,  n = outward unit normal of edge e of square j.
  dist  : ||c_i - c_j||^2 - 1  (flush upright pairs; valid for ANY pair of
          interior-disjoint unit squares by the support-function argument).

Validity (why every feasible packing in a box N satisfies g >= 0):
  wall  : containment (global).
  dist  : support function: disjoint interiors => centre distance >= 1 (global).
  edge  : LOCAL; needs on all of N:  n.(q-c_j) > -1/2  and |t.(q-c_j)| < 1/2
          (t = the other body axis of square j).  Then g < 0 => corner q lies in
          int(square j) => interiors of i and j meet => infeasible.

Numeric contexts: mpmath.mp (point arithmetic) and mpmath.iv (validated
intervals, outward rounding).  Centres are exact Fractions from A03 60-digit
strings.
"""
from __future__ import annotations

import json
import os
from decimal import Decimal, getcontext
from fractions import Fraction

from mpmath import mp, iv

HERE = os.path.dirname(os.path.abspath(__file__))
EXACT_JSON = os.path.join(HERE, '..', 'A03-upper-reconstruct', 'trump11_exact.json')

getcontext().prec = 200

HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]   # edge k joins corner k -> k+1
EDGE_NAMES = ['bottom', 'right', 'top', 'left']

NV = 34


def dec_to_frac(sd):
    return Fraction(Decimal(sd))


def load_z0(limit_digits=None):
    with open(EXACT_JSON) as f:
        d = json.load(f)
    z = []
    for sq in d['squares']:
        for key in ('cx', 'cy', 'theta'):
            z.append(dec_to_frac(sq[key]))
    z.append(dec_to_frac(d['s']))
    if limit_digits is not None:
        q = 10 ** limit_digits
        z = [Fraction(round(x * q), q) for x in z]
    return z, d


def curated_constraints(exact):
    """wall contacts (20) + interior corner-on-edge contacts (16) + the two
    flush upright pair distance constraints.  Degenerate corner-at-edge-end
    contacts and the corner-to-corner pair (1,3) are intentionally unused."""
    cons = []
    for k, c in enumerate(exact['contacts']):
        if c['type'] == 'wall':
            cons.append({'kind': 'wall', 'i': c['square'], 'corner': c['corner'],
                         'wall': c['wall'], 'a03_index': k})
        else:
            if not c['at_edge_end']:
                cons.append({'kind': 'edge', 'i': c['square'], 'corner': c['corner'],
                             'j': c['other'], 'edge': c['edge'], 'a03_index': k})
    cons.append({'kind': 'dist', 'i': 0, 'j': 1, 'a03_index': None})
    cons.append({'kind': 'dist', 'i': 0, 'j': 3, 'a03_index': None})
    return cons


def con_name(c):
    if c['kind'] == 'wall':
        return 'W{}c{}[{}]'.format(c['i'], c['corner'], c['wall'])
    if c['kind'] == 'edge':
        return 'E{}c{}-{}e{}'.format(c['i'], c['corner'], c['j'], c['edge'])
    return 'D{}-{}'.format(c['i'], c['j'])


# ---------------------------------------------------------------- generic eval

def cnum(ctx, x):
    """Exact Fraction/int -> ctx number (iv: rigorous enclosure)."""
    if isinstance(x, Fraction):
        return ctx.mpf(x.numerator) / ctx.mpf(x.denominator)
    return ctx.mpf(x)


def rot(ctx, th, vx, vy):
    c, s = ctx.cos(th), ctx.sin(th)
    return vx * c - vy * s, vx * s + vy * c


def drot(ctx, th, vx, vy):
    c, s = ctx.cos(th), ctx.sin(th)
    return -vx * s - vy * c, vx * c - vy * s


def corner_pos(ctx, z, i, corner):
    hx, hy = cnum(ctx, HALF[corner][0]), cnum(ctx, HALF[corner][1])
    rx, ry = rot(ctx, z[3 * i + 2], hx, hy)
    return z[3 * i] + rx, z[3 * i + 1] + ry


def eval_g(ctx, z, c):
    half = cnum(ctx, Fraction(1, 2))
    if c['kind'] == 'angeq':
        return z[3 * c['i'] + 2] - z[3 * c['j'] + 2]
    if c['kind'] == 'wall':
        qx, qy = corner_pos(ctx, z, c['i'], c['corner'])
        w = c['wall']
        if w == 'x=0':
            return qx
        if w == 'y=0':
            return qy
        if w == 'x=s':
            return z[33] - qx
        if w == 'y=s':
            return z[33] - qy
        raise ValueError(w)
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        qx, qy = corner_pos(ctx, z, i, c['corner'])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = rot(ctx, z[3 * j + 2], ctx.mpf(nhx), ctx.mpf(nhy))
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        return nx * wx + ny * wy - half
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - ctx.mpf(1)
    raise ValueError(c['kind'])


def grad_g(ctx, z, c):
    """Sparse gradient: dict {var_index: ctx number}."""
    g = {}
    if c['kind'] == 'angeq':
        g[3 * c['i'] + 2] = ctx.mpf(1)
        g[3 * c['j'] + 2] = ctx.mpf(-1)
        return g
    if c['kind'] == 'wall':
        i = c['i']
        hx, hy = cnum(ctx, HALF[c['corner']][0]), cnum(ctx, HALF[c['corner']][1])
        dx, dy = drot(ctx, z[3 * i + 2], hx, hy)
        w = c['wall']
        if w == 'x=0':
            g[3 * i] = ctx.mpf(1); g[3 * i + 2] = dx
        elif w == 'y=0':
            g[3 * i + 1] = ctx.mpf(1); g[3 * i + 2] = dy
        elif w == 'x=s':
            g[3 * i] = ctx.mpf(-1); g[3 * i + 2] = -dx; g[33] = ctx.mpf(1)
        elif w == 'y=s':
            g[3 * i + 1] = ctx.mpf(-1); g[3 * i + 2] = -dy; g[33] = ctx.mpf(1)
        return g
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        thi, thj = z[3 * i + 2], z[3 * j + 2]
        hx, hy = cnum(ctx, HALF[c['corner']][0]), cnum(ctx, HALF[c['corner']][1])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = rot(ctx, thj, ctx.mpf(nhx), ctx.mpf(nhy))
        qx, qy = corner_pos(ctx, z, i, c['corner'])
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx, dhy = drot(ctx, thi, hx, hy)
        dnx, dny = drot(ctx, thj, ctx.mpf(nhx), ctx.mpf(nhy))
        g[3 * i] = nx; g[3 * i + 1] = ny
        g[3 * j] = -nx; g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        two = ctx.mpf(2)
        g[3 * i] = two * dx; g[3 * i + 1] = two * dy
        g[3 * j] = -two * dx; g[3 * j + 1] = -two * dy
        return g
    raise ValueError(c['kind'])


def edge_aux(ctx, z, c):
    """(depth, tangential) = (n.(q-c_j), t.(q-c_j)); t = n rotated +90 deg."""
    i, j = c['i'], c['j']
    qx, qy = corner_pos(ctx, z, i, c['corner'])
    nhx, nhy = NHAT[c['edge']]
    nx, ny = rot(ctx, z[3 * j + 2], ctx.mpf(nhx), ctx.mpf(nhy))
    tx, ty = -ny, nx
    wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
    return nx * wx + ny * wy, tx * wx + ty * wy


# ---------------------------------------------------------------- boxes

def z_point(ctx, z0):
    return [cnum(ctx, x) for x in z0]


def z_box(z0, r):
    """Interval box around rational centre z0, rational radius r (scalar/list)."""
    if not isinstance(r, (list, tuple)):
        r = [r] * NV
    out = []
    for x, ri in zip(z0, r):
        lo, hi = x - ri, x + ri
        a = cnum(iv, lo)
        b = cnum(iv, hi)
        out.append(iv.mpf([a.a, b.b]))
    return out


def iv_min(a, b):
    return iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def iv_max(a, b):
    return iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def pair_sep_iv(z, i, j):
    """Interval SAT separation of squares i, j on an interval configuration z:
    max over the 4 candidate axes of the projection gap.  Lower bound > 0
    proves the pair strictly disjoint everywhere on the box."""
    ci = [corner_pos(iv, z, i, c) for c in range(4)]
    cj = [corner_pos(iv, z, j, c) for c in range(4)]
    best = None
    for sq in (i, j):
        th = z[3 * sq + 2]
        for nhx, nhy in ((1, 0), (0, 1)):
            nx, ny = rot(iv, th, iv.mpf(nhx), iv.mpf(nhy))
            pi = [nx * qx + ny * qy for qx, qy in ci]
            pj = [nx * qx + ny * qy for qx, qy in cj]
            lo_i = pi[0]; hi_i = pi[0]; lo_j = pj[0]; hi_j = pj[0]
            for p in pi[1:]:
                lo_i = iv_min(lo_i, p); hi_i = iv_max(hi_i, p)
            for p in pj[1:]:
                lo_j = iv_min(lo_j, p); hi_j = iv_max(hi_j, p)
            gap = iv_max(lo_j - hi_i, lo_i - hi_j)
            best = gap if best is None else iv_max(best, gap)
    return best


# ---------------------------------------------------------------- rational IO

def frac_str(x):
    return '{}/{}'.format(x.numerator, x.denominator)


def str_frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))
