#!/usr/bin/env python3
"""a36_check_exact.py -- EXACT-RATIONAL re-checker for A36's basin certificates
(A70, depgraph E.A36 / checklist F6 rung (a): mpmath.iv OUT of the decision path).

Same chain, same certificates, same corruption gates as the frozen
attempts/A36-levers/code/a36_check.py (which is NOT modified), but every decision
is made in exact rational arithmetic:

  * intervals are pairs of Fractions, OUTWARD-rounded to the dyadic grid 2^-PREC
    after every operation (rounding only widens -- sound);
  * cos/sin enclosures over rational intervals use certified alternating Taylor
    partial sums (|x| <= 1 asserted; consecutive-term ratio x^2/((2k+1)(2k+2)) < 1
    from k = 0, so partial sums bracket), plus monotonicity on the sign-split
    interval -- NO mpmath, NO floats in any accept decision;
  * the float upward-rounding fudges of the original (`math.nextafter`, `sum_up`'s
    (1+1e-12) inflation, iv outward rounding) are replaced by exact values, which
    are sharper upper bounds; the fixed-point iteration [P] rounds its iterate UP
    to the dyadic grid each step (the map is monotone with nonnegative
    coefficients, so the limit stays an upper bound of the true least fixed point);
  * claimed float quantities from the certificates are converted to the exact
    rationals those floats denote; the tolerance gates keep the original's
    factors (x1.0000001 + 1e-300) as exact rationals.

stdlib only: fractions + json + glob + os + sys.  The row language, axis tables
and the [S][N][A][O][Z][G][H][K][E][P][V][L] chain are transcribed from
a36_check.py (A36), itself transcribed from A35's m2_check_inflation.py.

Usage:
    python a36_check_exact.py [certdir] [krawczyk_cert.json]
                              [--corrupt {omega-sign,h-big,drop-aux,drop-branch,
                                          wrong-branch}]
Exit 0 = all PASS (or, under --corrupt, the checker failed as required).
"""
import glob
import json
import os
import sys
from fractions import Fraction

PREC = 330                     # dyadic grid 2^-PREC for outward rounding
GRID = 1 << PREC
NV = 34
S_IDX = 33
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]      # outward normal of edge k

# ------------------------------------------------- BASIS v3 spec (transcribed)
AXES = [
    ('A01a',  0, 1, 1, 3, 36),
    ('A01b',  1, 3, 0, 2, 37),
    ('A03a',  0, 2, 3, 0, 38),
    ('A03b',  3, 0, 0, 3, 39),
    ('B13x',  1, 3, 3, 1, 40),
    ("B13x'", 3, 1, 1, 3, 42),
    ('B13y',  3, 0, 1, 3, 41),
    ("B13y'", 1, 2, 3, 1, 43),
]
AUX_POS = (44, 45)
EXTRA0 = 46
NEXT3 = 70
CONTACT_AXES = [[0, 1], [2, 3], [4, 5, 6, 7]]
NEW_V3_POS = (42, 43)
KILLED_AXES = (
    [('(0,1)', 0, e, 1) for e in (0, 2, 3)] +
    [('(0,1)', 1, e, 0) for e in (0, 1, 2)] +
    [('(0,3)', 0, e, 3) for e in (0, 1, 3)] +
    [('(0,3)', 3, e, 0) for e in (1, 2, 3)] +
    [('(1,3)', 1, e, 3) for e in (0, 1)] +
    [('(1,3)', 3, e, 1) for e in (2, 3)]
)


def axis_corner_positions(ax):
    _, o, e, p, kc, base = AXES[ax]
    out = {kc: base}
    for j, k in enumerate([k for k in range(4) if k != kc]):
        out[k] = EXTRA0 + 3 * ax + j
    return out


def axis_rows(ax):
    return sorted(axis_corner_positions(ax).values())


def build_constraints(K):
    out = [dict(c) for c in K['constraints'][:36]] + [None] * 34
    for ax, (nm, o, e, p, kc, base) in enumerate(AXES):
        for k, pos in axis_corner_positions(ax).items():
            out[pos] = {'kind': 'edge', 'i': p, 'corner': k, 'j': o,
                        'edge': e, 'name': '%s[k%d]' % (nm, k)}
    out[44] = dict(K['constraints'][36])
    out[45] = dict(K['constraints'][37])
    assert all(c is not None for c in out) and len(out) == NEXT3
    return out


def variant_rows(axes):
    rows = set(range(36)) | set(AUX_POS)
    for ax in axes:
        rows |= set(axis_rows(ax))
    return sorted(rows)


# --------------------------------------------------------------- exact numerics
def frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def rdown(x):
    """round a Fraction DOWN to the dyadic grid."""
    return Fraction((x.numerator * GRID) // x.denominator, GRID)


def rup(x):
    """round a Fraction UP to the dyadic grid."""
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
            b = IV.point(b)
        return IV(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __sub__(self, b):
        if not isinstance(b, IV):
            b = IV.point(b)
        return IV(self.lo - b.hi, self.hi - b.lo)

    def __rsub__(self, b):
        return IV.point(b) - self

    def __neg__(self):
        return IV(-self.hi, -self.lo, rnd=False)

    def __mul__(self, b):
        if not isinstance(b, IV):
            b = IV.point(b)
        ps = (self.lo * b.lo, self.lo * b.hi, self.hi * b.lo, self.hi * b.hi)
        return IV(min(ps), max(ps))

    __rmul__ = __mul__

    def mag(self):
        return max(abs(self.lo), abs(self.hi))


IZERO = IV.point(Fraction(0))
IONE = IV.point(Fraction(1))


def _cos_pt(x):
    """certified bracket of cos x at a rational point, |x| <= 1: alternating
    Taylor partial sums with strictly decreasing terms (ratio
    x^2/((2k+1)(2k+2)) <= 1/2 from k = 0) bracket the value; the recorded
    odd/even partial sums are a valid [lo, hi]."""
    x = abs(x)
    assert x <= 1
    xx = x * x
    term = Fraction(1)
    s = Fraction(0)
    lo = hi = None
    k = 0
    while True:
        s = s + (term if k % 2 == 0 else -term)
        if k % 2 == 0:
            hi = s
        else:
            lo = s
        k += 1
        term = term * xx / ((2 * k - 1) * (2 * k))
        if lo is not None and hi is not None \
                and term < Fraction(1, 1 << (PREC + 20)):
            break
        if k > 400:
            raise RuntimeError('cos Taylor did not converge')
    return lo, hi


def _sin_pt(x):
    """certified bracket of sin x at a rational point, |x| <= 1 (odd; for
    x >= 0 the alternating partial sums bracket as for cos)."""
    if x < 0:
        lo, hi = _sin_pt(-x)
        return -hi, -lo
    if x == 0:
        return Fraction(0), Fraction(0)
    assert x <= 1
    xx = x * x
    term = Fraction(x)
    s = Fraction(0)
    lo = hi = None
    k = 0
    while True:
        s = s + (term if k % 2 == 0 else -term)
        if k % 2 == 0:
            hi = s
        else:
            lo = s
        k += 1
        term = term * xx / ((2 * k) * (2 * k + 1))
        if lo is not None and hi is not None \
                and term < Fraction(1, 1 << (PREC + 20)):
            break
        if k > 400:
            raise RuntimeError('sin Taylor did not converge')
    return lo, hi


_CPT, _SPT, _CIV, _SIV = {}, {}, {}, {}


def cos_iv(v):
    """enclosure of cos over the interval v (|endpoints| <= 1); cos is even and
    decreasing in |x|: max at the point of smallest |x|."""
    key = (v.lo, v.hi)
    out = _CIV.get(key)
    if out is not None:
        return out
    a, b = v.lo, v.hi
    if a not in _CPT:
        _CPT[a] = _cos_pt(a)
    if b not in _CPT:
        _CPT[b] = _cos_pt(b)
    ca, cb = _CPT[a], _CPT[b]
    lo = min(ca[0], cb[0])
    if a <= 0 <= b:
        hi = Fraction(1)
    else:
        hi = max(ca[1], cb[1])
    out = IV(lo, hi)
    _CIV[key] = out
    return out


def sin_iv(v):
    """enclosure of sin over the interval v (|endpoints| <= 1); monotone."""
    key = (v.lo, v.hi)
    out = _SIV.get(key)
    if out is not None:
        return out
    if v.lo not in _SPT:
        _SPT[v.lo] = _sin_pt(v.lo)
    if v.hi not in _SPT:
        _SPT[v.hi] = _sin_pt(v.hi)
    sa, sb = _SPT[v.lo], _SPT[v.hi]
    out = IV(sa[0], sb[1])
    _SIV[key] = out
    return out


# ---- order-2 forward jets over exact intervals (structure = a36_check.J)
class J(object):
    __slots__ = ('v', 'g', 'h', 'd', 'o')

    def __init__(self, v, g, h, d, o):
        self.v, self.g, self.h, self.d, self.o = v, g, h, d, o

    @staticmethod
    def var(val, k, d, o):
        g = None
        if o >= 1:
            g = [IZERO] * d
            g[k] = IONE
        return J(val, g, [[IZERO] * d for _ in range(d)] if o >= 2 else None,
                 d, o)

    def __add__(self, b):
        if not isinstance(b, J):
            return J(self.v + b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        return J(self.v + b.v,
                 [self.g[i] + b.g[i] for i in range(d)] if o >= 1 else None,
                 [[self.h[i][j] + b.h[i][j] for j in range(d)]
                  for i in range(d)] if o >= 2 else None, d, o)

    def __sub__(self, b):
        if not isinstance(b, J):
            return J(self.v - b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        return J(self.v - b.v,
                 [self.g[i] - b.g[i] for i in range(d)] if o >= 1 else None,
                 [[self.h[i][j] - b.h[i][j] for j in range(d)]
                  for i in range(d)] if o >= 2 else None, d, o)

    def __mul__(self, b):
        d, o = self.d, self.o
        if not isinstance(b, J):
            return J(self.v * b,
                     [self.g[i] * b for i in range(d)] if o >= 1 else None,
                     [[self.h[i][j] * b for j in range(d)]
                      for i in range(d)] if o >= 2 else None, d, o)
        g = [self.g[i] * b.v + self.v * b.g[i]
             for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[self.h[i][j] * b.v + self.g[i] * b.g[j] + self.g[j] * b.g[i]
                  + self.v * b.h[i][j] for j in range(d)] for i in range(d)]
        return J(self.v * b.v, g, h, d, o)

    __rmul__ = __mul__

    def _ch(self, f, df, d2f):
        d, o = self.d, self.o
        g = [df * self.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[df * self.h[i][j] + d2f * self.g[i] * self.g[j]
                  for j in range(d)] for i in range(d)]
        return J(f, g, h, d, o)

    def cos(self):
        c, s = cos_iv(self.v), sin_iv(self.v)
        return self._ch(c, -s, -c)

    def sin(self):
        c, s = cos_iv(self.v), sin_iv(self.v)
        return self._ch(s, c, -s)


def row_vars(c):
    if c['kind'] == 'wall':
        i = c['i']
        vs = [3 * i, 3 * i + 1, 3 * i + 2]
        if c['wall'] in ('x=s', 'y=s'):
            vs.append(33)
        return vs
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        return [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        return [3 * i, 3 * i + 1, 3 * j, 3 * j + 1]
    raise ValueError(c['kind'])


def row_jet(box, c, order):
    vs = row_vars(c)
    d = len(vs)
    V = [J.var(box[gi], k, d, order) for k, gi in enumerate(vs)]
    half = Fraction(1, 2)
    if c['kind'] == 'wall':
        cx, cy, th = V[0], V[1], V[2]
        hx, hy = HALF[c['corner']]
        co, si = th.cos(), th.sin()
        qx = cx + (co * hx - si * hy)
        qy = cy + (si * hx + co * hy)
        w = c['wall']
        if w == 'x=0':
            return qx, vs
        if w == 'y=0':
            return qy, vs
        S = V[3]
        return ((S - qx) if w == 'x=s' else (S - qy)), vs
    if c['kind'] == 'edge':
        cix, ciy, thi, cjx, cjy, thj = V
        hx, hy = HALF[c['corner']]
        ci, si = thi.cos(), thi.sin()
        qx = cix + (ci * hx - si * hy)
        qy = ciy + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = thj.cos(), thj.sin()
        nx = cj * nhx - sj * nhy
        ny = sj * nhx + cj * nhy
        return (nx * (qx - cjx) + ny * (qy - cjy)) - half, vs
    if c['kind'] == 'dist':
        dx = V[0] - V[2]
        dy = V[1] - V[3]
        return (dx * dx + dy * dy) - 1, vs
    raise ValueError(c['kind'])


def box_of(z0, r):
    return [IV(x - r, x + r) for x in z0]


def sep_value(box, o, e, p, k):
    return row_jet(box, {'kind': 'edge', 'i': p, 'corner': k, 'j': o,
                         'edge': e}, 0)[0].v


def ffloat(x):
    """exact rational denoted by a JSON float claim."""
    return Fraction(x)


TOL = Fraction(10000001, 10000000)
TINY = Fraction(1, 10 ** 300)


# ----------------------------------------------------------------- checking
class Check(object):
    def __init__(self):
        self.fails = []
        self.n = 0

    def __call__(self, name, ok, detail=''):
        self.n += 1
        if not ok:
            self.fails.append(name)
            print('  [FAIL] %s %s' % (name, detail))
        return ok


def check_cert(cert, K, ck, verbose):
    z0 = [frac(x) for x in K['z0']]
    Y = [[frac(v) for v in row] for row in K['Y']]
    rN = frac(K['r_N'])
    cons = build_constraints(K)
    om = [frac(x) for x in cert['omega_rational']]
    h = frac(cert['h'])
    cl = cert['claims']
    universal = bool(cert.get('universal'))
    tag = ('UNIVERSAL' if universal else '-'.join(cert['variant']))

    # [S] pin set == A22's S mapped
    P_spec = [k if k < 36 else (44 if k == 36 else 45) for k in K['S']]
    P = list(cert['P'])
    ck('S %s pin set = A22 S (mapped)' % tag, P == P_spec)

    RV = (sorted(set(range(36)) | set(AUX_POS)) if universal
          else variant_rows(cert['variant_axes']))
    ck('O %s valid_rows = spec R_V' % tag, sorted(cert['valid_rows']) == RV)

    pbox = [IV.point(x) for x in z0]
    box = box_of(z0, h)
    gz = [row_jet(pbox, cons[k], 0)[0].v.mag() for k in range(NEXT3)]

    # [N] the two NEW v3 rows vanish at z-hat; loaded rows are active
    ck('N %s new v3 rows B13x\',B13y\' zero at z-hat (<1e-59)' % tag,
       max(gz[k] for k in NEW_V3_POS) < Fraction(1, 10 ** 59),
       'max |g| = %.3e' % float(max(gz[k] for k in NEW_V3_POS)))
    ck('N %s every loaded row is active at z-hat (<1e-40)' % tag,
       all(gz[k] < Fraction(1, 10 ** 40) for k in range(NEXT3) if om[k] != 0),
       'max = %.3e' % float(max([gz[k] for k in range(NEXT3)
                                 if om[k] != 0])))
    # [A] aux rows active
    ck('A %s aux rows active at z-hat' % tag,
       max(gz[p] for p in AUX_POS) < Fraction(1, 10 ** 40))

    # [O] sign discipline
    ck('O %s omega >= 0 on R_V' % tag, all(om[k] >= 0 for k in RV))
    ck('O %s omega = 0 outside R_V' % tag,
       all(om[k] == 0 for k in range(NEXT3) if k not in set(RV)),
       'nonzero outside: %s' % [k for k in range(NEXT3)
                                if k not in set(RV) and om[k] != 0][:6])
    ck('O %s omega > 0 on every pin row' % tag, all(om[k] > 0 for k in P))
    if not universal:
        loaded = []
        for ax in cert['variant_axes']:
            loaded.append(any(om[k] > 0 for k in axis_rows(ax)))
        ck('O %s every branch axis carries omega > 0 (non-vacuity)' % tag,
           all(loaded), 'per-axis: %s' % loaded)

    # [Z] eps_0, g_max
    e0 = sum(abs(om[k]) * gz[k] for k in range(NEXT3) if om[k] != 0)
    gmax = max(gz[k] for k in P)
    ck('Z %s eps_0' % tag, e0 <= ffloat(cl['eps_0']) * TOL + TINY,
       'recomputed %.3e vs claimed %.3e' % (float(e0), cl['eps_0']))
    ck('Z %s g_max' % tag, gmax <= ffloat(cl['g_max']) * TOL + TINY,
       'recomputed %.3e vs claimed %.3e' % (float(gmax), cl['g_max']))

    # [G] eps_w
    acc = [IZERO] * NV
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        j, vs = row_jet(pbox, cons[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + om[k] * j.g[loc]
    ew = sum((acc[gi] - (IONE if gi == S_IDX else IZERO)).mag()
             for gi in range(NV))
    ck('G %s eps_w' % tag, ew <= ffloat(cl['eps_w']) * TOL + TINY,
       'recomputed %.3e vs claimed %.3e' % (float(ew), cl['eps_w']))

    # [H] Hbar
    Hd = {}
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        j, vs = row_jet(box, cons[k], 2)
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                t = om[k] * j.h[a][b]
                Hd[key] = t if key not in Hd else Hd[key] + t
    Hbar = sum(x.mag() for x in Hd.values()) / 2
    ck('H %s Hbar' % tag, Hbar <= ffloat(cl['Hbar']) * TOL,
       'recomputed %.6f vs claimed %.6f' % (float(Hbar), cl['Hbar']))

    # [K] beta, kappa
    grads = []
    for k in P:
        j, vs = row_jet(box, cons[k], 1)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
    beta = Fraction(0)
    for i in range(NV):
        rs = Fraction(0)
        for j2 in range(NV):
            ssum = IZERO
            for rr in range(NV):
                v = grads[rr].get(j2)
                if v is not None:
                    ssum = ssum + Y[i][rr] * v
            rs += ((IONE if i == j2 else IZERO) - ssum).mag()
        beta = max(beta, rs)
    kappa = max(sum(abs(Y[i][r]) for r in range(NV)) for i in range(NV))
    ck('K %s beta < 1' % tag, beta < 1 and beta <= ffloat(cl['beta']) * TOL,
       'recomputed %.8f vs claimed %.8f' % (float(beta), cl['beta']))
    ck('K %s kappa' % tag, kappa <= ffloat(cl['kappa']) * TOL,
       'recomputed %.6f' % float(kappa))

    # [E] kappa_eff
    cvec = [max(abs(Y[i][r]) for i in range(NV)) for r in range(NV)]
    bad = any(om[P[i]] <= 0 for i in range(NV))
    keff = None if bad else max(cvec[i] / om[P[i]] for i in range(NV))
    ck('E %s kappa_eff' % tag,
       (not bad) and keff <= ffloat(cl['kappa_eff']) * TOL,
       'recomputed %s vs claimed %.6f'
       % ('inf' if bad else '%.6f' % float(keff), cl['kappa_eff']))

    # [P] dichotomy + iterated pinning (exact; iterate rounded UP each step)
    ok_pre = (beta < 1) and (not bad)
    psi = None
    if ok_pre:
        E = e0 + ew * h + Hbar * h * h
        psi = (keff * E + kappa * gmax) / (1 - beta)
    ck('P %s contraction psi(h) < h' % tag, ok_pre and psi < h,
       'psi = %.6e vs h = %.6e (ratio %.4f)'
       % (float(psi or 0), float(h), float((psi or 0) / h)))
    xstar_ok = False
    x = h
    if ok_pre:
        C = keff / (1 - beta)
        D0 = kappa * gmax / (1 - beta)
        for _ in range(800):
            x = rup(C * (e0 + ew * x + Hbar * x * x) + D0)
            if x > 1:
                break          # diverging (as the float original would, to inf);
                               # x stays > r_N so the gate below fails -- sound
        xstar_ok = x <= rN
    ck('P %s fixed point x* <= r_N' % tag, xstar_ok,
       'x* = %.4e vs r_N = %.4e' % (float(x), float(rN)))

    # [V] A22 rows 0..35 SAT-selection validity on box(h)
    wt, wd = None, None
    for c in cons[:36]:
        if c['kind'] != 'edge':
            continue
        i, j2 = c['i'], c['j']
        hx, hy = HALF[c['corner']]
        ci, si = cos_iv(box[3 * i + 2]), sin_iv(box[3 * i + 2])
        qx = box[3 * i] + (ci * hx - si * hy)
        qy = box[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = cos_iv(box[3 * j2 + 2]), sin_iv(box[3 * j2 + 2])
        nx = cj * nhx - sj * nhy
        ny = sj * nhx + cj * nhy
        wx, wy = qx - box[3 * j2], qy - box[3 * j2 + 1]
        t1 = Fraction(1, 2) - (-ny * wx + nx * wy).mag()
        d1 = Fraction(1, 2) + (nx * wx + ny * wy).lo
        wt = t1 if wt is None else min(wt, t1)
        wd = d1 if wd is None else min(wd, d1)
    ck('V %s A22 rows 0..35 SAT selection valid on box(h)' % tag,
       wt > 0 and wd > 0,
       'tangential %.6f, depth+1/2 %.6f' % (float(wt), float(wd)))

    # [L] L1: the 16 impossible axes are refuted on box(h)
    kmin = None
    for lab, o, e, p in KILLED_AXES:
        best = max(-(sep_value(box, o, e, p, k).hi) for k in range(4))
        kmin = best if kmin is None else min(kmin, best)
    ck('L %s L1 killed axes refuted on box(h)' % tag, kmin > 0,
       'min kill margin %.6f' % float(kmin))

    if verbose:
        print('  [ok] %-26s h=%-12s beta=%.5f Hbar=%.3f keff=%.3f psi/h=%.4f'
              ' x*=%.2e' % (tag, cert['h'], float(beta), float(Hbar),
                            float(keff) if keff is not None else float('inf'),
                            float((psi or 0) / h), float(x)))
    return dict(h=h, beta=beta, Hbar=Hbar, keff=keff,
                psi_over_h=(psi / h if psi is not None else None),
                x_star=x, tan=wt, kill=kmin, universal=universal)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in args:
        i = args.index('--corrupt')
        corrupt = args[i + 1]
        del args[i:i + 2]
    cdir = args[0] if args else os.path.join(
        here, '..', '..', 'A36-levers', 'results', 'a36_certs')
    kpath = (args[1] if len(args) > 1 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    K = json.load(open(kpath))
    files = sorted(glob.glob(os.path.join(cdir, 'G3_*.json')))
    if not files:
        print('no certificates found in %s' % cdir)
        return 1
    if corrupt:
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        files = [f for f in files
                 if 'UNIVERSAL' not in os.path.basename(f)][:1]
    print('re-checking %d certificates in %s (EXACT rational arithmetic)'
          % (len(files), os.path.abspath(cdir)))
    ck = Check()
    rows = []
    for i, f in enumerate(files):
        cert = json.load(open(f))
        if corrupt == 'omega-sign':
            r = cert['P'][0]
            cert['omega_rational'][r] = '-' + cert['omega_rational'][r]
        elif corrupt == 'h-big':
            g = frac(cert['h']) * 8
            cert['h'] = '%d/%d' % (g.numerator, g.denominator)
        elif corrupt == 'drop-aux':
            for p in AUX_POS:
                cert['omega_rational'][p] = '0/1'
        elif corrupt == 'drop-branch':
            for p in cert['branch_rows']:
                cert['omega_rational'][p] = '0/1'
        elif corrupt == 'wrong-branch':
            ax = cert['variant_axes']
            other = [a for a in CONTACT_AXES[2] if a != ax[2]][0]
            cert['variant_axes'] = [ax[0], ax[1], other]
            cert['variant'] = [AXES[a][0] for a in cert['variant_axes']]
            cert['valid_rows'] = variant_rows(cert['variant_axes'])
        elif corrupt is not None:
            raise SystemExit('unknown corruption mode')
        rows.append(check_cert(cert, K, ck, verbose=(corrupt or i % 6 == 0)))
    if corrupt:
        bad = bool(ck.fails)
        print('corruption test %s: %s' % (
            corrupt, 'OK (checker failed as required)' if bad else
            'PROBLEM: checker still passes!'))
        return 0 if bad else 2
    U = [r for r in rows if r['universal']]
    Vv = [r for r in rows if not r['universal']]
    print('  %d certificates, %d checks' % (len(rows), ck.n))
    if Vv:
        print("  (V') per-variant %d: h = %.6g, max psi/h = %.4f, "
              'max x* = %.2e' % (len(Vv), float(max(r['h'] for r in Vv)),
                                 float(max(r['psi_over_h'] for r in Vv)),
                                 float(max(r['x_star'] for r in Vv))))
    if U:
        print("  (V') branch-free UNIVERSAL: h = %.6g, psi/h = %.4f, x* = %.2e"
              % (float(U[0]['h']), float(U[0]['psi_over_h']),
                 float(U[0]['x_star'])))
    print('  min A22 tangential margin 0..35 = %.6f (must be > 0)'
          % float(min(r['tan'] for r in rows)))
    print('  min L1 kill margin              = %.6f (must be > 0)'
          % float(min(r['kill'] for r in rows)))
    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))[:8]))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
