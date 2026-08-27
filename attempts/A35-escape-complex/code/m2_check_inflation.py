#!/usr/bin/env python
"""Standalone re-checker for results/m2_inflation.json  (A35 / M2 Task 1).

recheck.py style: uses ONLY mpmath.iv + fractions + json.  It does NOT import
strata_lib / t3lib / a22lib / numpy -- the row language, the order-2 interval
jets, the Krawczyk operator and the norm bounds are all re-implemented here from
the constraint SPEC in A22's krawczyk_cert.json, so a bug shared with the
producing code cannot hide.

What it verifies, for every radius r in the certificate's grid:

  [L]  lambda* >= 0 and its residual at z-hat:
       ||A(z-hat)^T lambda* - e_s||_1 <= r_res(0) as claimed.
  [R]  r_res(r) := sup_{box(r)} ||A(z)^T lambda* - e_s||_1  <=  claimed value.
  [H]  Hsum(r) := sum_{i,j} sup_{box(r)} |d2 Phi/dz_i dz_j| <= claimed value,
       Hinf(r) := max_i sum_j sup|...|                      <= claimed value,
       for Phi = s - sum_k lambda*_k g_k  (order-2 interval jets).
  [K]  beta(r) := sup ||I - Y A_S(box(r))||_inf <= claimed, kappa = ||Y||_inf.
  [C]  the Consequence-2 inequality with the recomputed constants:
       rho_1(r) = kappa (Hbar r^2 + r_res r)/(lambda_floor (1-beta)) <= r_N,
       in both variants (A: r_res = box sup; B: r_res = centre residual).
  [V]  edge-selection validity over box(r): |tangential| < 1/2 and depth > -1/2
       for every 'edge' row (without this the edge rows are not valid lower
       bounds for the true SAT separation and the whole argument is void).
  [1]  the declared r_1 really is the largest grid radius passing [C]+[V].

Exit 0 = all PASS.
Usage: python m2_check_inflation.py [results/m2_inflation.json] [path/to/krawczyk_cert.json]
"""
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

iv.dps = 60

NV = 34
NSQ = 11
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def cnum(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def mag(x):
    """Rigorous float64 upper bound of |x| over the interval x.

    float() of an mpmath endpoint rounds to nearest (error <= 0.5 ulp); one
    nextafter upward makes the result a certified upper bound.
    """
    x = iv.mpf(x)
    return max(math.nextafter(abs(float(x.a)), math.inf),
               math.nextafter(abs(float(x.b)), math.inf))


def up(x):
    """Rigorous float64 upper bound of the interval x (its supremum)."""
    return math.nextafter(float(iv.mpf(x).b), math.inf)


def sum_up(xs):
    """Rigorous float64 upper bound of a sum of nonnegative float bounds.

    34-term float64 summation has relative error <= 34*2^-53 < 4e-15; the
    inflation factor 1 + 1e-12 covers it with three orders of magnitude to
    spare (and the +1e-300 covers the underflow corner).
    """
    return sum(xs) * (1.0 + 1e-12) + 1e-300


# ------------------------------------------------------------------- jets
# Independent order-2 forward-mode jet over d local variables.

class J(object):
    __slots__ = ('v', 'g', 'h', 'd', 'o')

    def __init__(self, v, g, h, d, o):
        self.v, self.g, self.h, self.d, self.o = v, g, h, d, o

    @staticmethod
    def con(c, d, o):
        z = [iv.mpf(0)] * d
        return J(c, list(z) if o >= 1 else None,
                 [[iv.mpf(0)] * d for _ in range(d)] if o >= 2 else None, d, o)

    @staticmethod
    def var(val, k, d, o):
        g = None
        if o >= 1:
            g = [iv.mpf(0)] * d
            g[k] = iv.mpf(1)
        return J(val, g, [[iv.mpf(0)] * d for _ in range(d)] if o >= 2 else None,
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

    def __neg__(self):
        d, o = self.d, self.o
        return J(-self.v,
                 [-self.g[i] for i in range(d)] if o >= 1 else None,
                 [[-self.h[i][j] for j in range(d)]
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
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._ch(c, -s, -c)

    def sin(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._ch(s, c, -s)


def row_vars(c):
    """Global variable indices touched by constraint c, in local jet order."""
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
    half = cnum(Fraction(1, 2))
    if c['kind'] == 'wall':
        cx, cy, th = V[0], V[1], V[2]
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
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
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        ci, si = thi.cos(), thi.sin()
        qx = cix + (ci * hx - si * hy)
        qy = ciy + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = thj.cos(), thj.sin()
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        return (nx * (qx - cjx) + ny * (qy - cjy)) - half, vs
    if c['kind'] == 'dist':
        dx = V[0] - V[2]
        dy = V[1] - V[3]
        return (dx * dx + dy * dy) - iv.mpf(1), vs
    raise ValueError(c['kind'])


def box_of(z0, r):
    out = []
    for x in z0:
        a = cnum(x - r)
        b = cnum(x + r)
        out.append(iv.mpf([a.a, b.b]))
    return out


# ------------------------------------------------------------------ checks

class Check(object):
    def __init__(self):
        self.fails = []

    def __call__(self, name, ok, detail=''):
        print('  [%s] %s %s' % ('PASS' if ok else 'FAIL', name, detail))
        if not ok:
            self.fails.append(name)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    cpath = (sys.argv[1] if len(sys.argv) > 1 else
             os.path.join(here, '..', 'results', 'm2_inflation.json'))
    kpath = (sys.argv[2] if len(sys.argv) > 2 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    C = json.load(open(cpath))
    K = json.load(open(kpath))

    z0 = [frac(x) for x in K['z0']]
    cons = K['constraints'][:38]
    S = C['S_rows']
    assert S == K['S'], 'S row list differs from A22 cert'
    Y = [[frac(v) for v in row] for row in K['Y']]
    rN = frac(K['r_N'])
    lam = [frac(x) for x in C['lambda_star_rational']]
    floor = min(lam)

    ck = Check()
    print('re-checking %s' % os.path.abspath(cpath))
    print('  38 geometric rows, |S| = %d, r_N = %s' % (len(S), K['r_N']))

    # [L] lambda* nonnegativity + declared floor + centre residual
    ck('L lambda* >= 0', all(x >= 0 for x in lam),
       'min = %.12f' % float(floor))
    ck('L lambda_floor matches', abs(float(floor) -
                                     C['meta']['lambda_floor_float']) < 1e-15)
    pbox = [cnum(x) for x in z0]
    acc = [iv.mpf(0)] * NV
    for k, c in enumerate(cons):
        j, vs = row_jet(pbox, c, 1)
        lk = cnum(lam[k])
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + lk * j.g[loc]
    res0 = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == 33 else iv.mpf(0)))
                   for gi in range(NV)])
    ck('L centre residual ||A^T lam - e_s||_1',
       res0 <= C['meta']['r_res_at_centre'] * 1.0000001,
       'recomputed %.3e <= claimed %.3e'
       % (res0, C['meta']['r_res_at_centre']))

    # centre row values (should be ~0)
    maxg = max(mag(row_jet(pbox, c, 0)[0].v) for c in cons)
    ck('L g_k(z-hat) = 0', maxg < 1e-40, 'max |g_k(z-hat)| = %.2e' % maxg)
    ck('L g_max claimed', maxg <= C['meta']['g_max_at_zhat'] * 1.0000001,
       'recomputed %.2e <= claimed %.2e' % (maxg, C['meta']['g_max_at_zhat']))

    kappa_claim = None
    kappa = max(sum(abs(float(Y[i][r])) for r in range(NV)) for i in range(NV))

    entries = C['grid']
    passing = []
    for ent in entries:
        r = frac(ent['r'])
        rf = float(r)
        box = box_of(z0, r)
        print('  --- r = %s (%.4g)' % (ent['r'], rf))

        # [R] box residual  +  [H] Hessian sums, one order-2 sweep
        accg = [iv.mpf(0)] * NV
        H = {}
        for k, c in enumerate(cons):
            j, vs = row_jet(box, c, 2)
            lk = cnum(lam[k])
            for a, ga in enumerate(vs):
                accg[ga] = accg[ga] + lk * j.g[a]
                for b, gb in enumerate(vs):
                    key = (ga, gb)
                    t = lk * j.h[a][b]
                    H[key] = t if key not in H else H[key] + t
        rres = sum_up([mag(accg[gi] - (iv.mpf(1) if gi == 33 else iv.mpf(0)))
                       for gi in range(NV)])
        rowmags = [[] for _ in range(NV)]
        allm = []
        for (a, b), x in H.items():
            m = mag(x)
            allm.append(m)
            rowmags[a].append(m)
        Hsum = sum_up(allm)
        Hinf = max(sum_up(rm) if rm else 0.0 for rm in rowmags)
        ck('R r_res(r)', rres <= ent['r_res_l1_upper_box'] * 1.0000001,
           'recomputed %.6e <= claimed %.6e'
           % (rres, ent['r_res_l1_upper_box']))
        ck('H Hsum(r)', Hsum <= ent['Hsum_upper'] * 1.0000001,
           'recomputed %.6f <= claimed %.6f' % (Hsum, ent['Hsum_upper']))
        ck('H Hinf(r)', Hinf <= ent['Hinf_upper'] * 1.0000001,
           'recomputed %.6f <= claimed %.6f' % (Hinf, ent['Hinf_upper']))
        ck('H Hsum <= 34*Hinf', Hsum <= 34.0 * Hinf + 1e-12)

        # [K] beta over box(r) for the S-subsystem with A22's Y
        grads = []
        for k in S:
            j, vs = row_jet(box, cons[k], 1)
            grads.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
        Yiv = [[cnum(v) for v in row] for row in Y]
        beta = 0.0
        for i in range(NV):
            rs = []
            for j2 in range(NV):
                ssum = iv.mpf(0)
                for rr in range(NV):
                    v = grads[rr].get(j2)
                    if v is not None:
                        ssum = ssum + Yiv[i][rr] * v
                e = (iv.mpf(1) if i == j2 else iv.mpf(0)) - ssum
                rs.append(mag(e))
            beta = max(beta, sum_up(rs))
        ck('K beta(r) = ||I - Y A_S(box)||_inf',
           beta <= ent['beta_upper'] * 1.0000001 and
           ((beta < 1.0) == (ent['beta_upper'] < 1.0)),
           'recomputed %.8f <= claimed %.8f' % (beta, ent['beta_upper']))
        ck('K kappa = ||Y||_inf', abs(kappa - ent['kappa_Yinf']) < 1e-9,
           'recomputed %.6f' % kappa)

        # [V] edge-selection validity over box(r)
        wt, wd = 1e9, 1e9
        for c in cons:
            if c['kind'] != 'edge':
                continue
            i, j2 = c['i'], c['j']
            hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
            thi = box[3 * i + 2]
            ci, si = iv.cos(thi), iv.sin(thi)
            qx = box[3 * i] + (ci * hx - si * hy)
            qy = box[3 * i + 1] + (si * hx + ci * hy)
            nhx, nhy = NHAT[c['edge']]
            thj = box[3 * j2 + 2]
            cj, sj = iv.cos(thj), iv.sin(thj)
            nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
            ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
            wx, wy = qx - box[3 * j2], qy - box[3 * j2 + 1]
            dep = nx * wx + ny * wy
            tan = -ny * wx + nx * wy
            wt = min(wt, 0.5 - mag(tan))
            wd = min(wd, -math.nextafter(float(-iv.mpf(dep).a), math.inf) + 0.5)
        vok = (wt > 0.0 and wd > 0.0)
        ck('V edge selection valid on box(r)', vok == ent['edge_selection_valid'],
           'tangential margin %.6f, depth+1/2 %.6f (claimed valid=%s)'
           % (wt, wd, ent['edge_selection_valid']))

        # [C] Consequence 2, recomputed from the RECOMPUTED constants
        Hbar = Hsum / 2.0
        fl = float(floor)
        okA = okB = False
        if beta < 1.0:
            TA = (Hbar * rf * rf + rres * rf) / fl + maxg
            TB = (Hbar * rf * rf + res0 * rf) / fl + maxg
            rhoA = kappa * TA / (1.0 - beta)
            rhoB = kappa * TB / (1.0 - beta)
            okA = rhoA <= float(rN)
            okB = rhoB <= float(rN)
        else:
            rhoA = rhoB = float('inf')
        ck('C variant A verdict reproduced', okA == ent['holds_variantA'],
           'rho_1^A = %.6e (r_N = %.4e) -> %s' % (rhoA, float(rN), okA))
        ck('C variant B verdict reproduced', okB == ent['holds_variantB'],
           'rho_1^B = %.6e (r_N = %.4e) -> %s' % (rhoB, float(rN), okB))
        okC = bool(beta < 1.0 and rhoB < rf)
        if okC:
            Ck = kappa / ((1.0 - beta) * fl)
            xc = rf
            for _ in range(400):
                xc = Ck * (Hbar * xc * xc + res0 * xc) + kappa * maxg / (1 - beta)
            okC = bool(xc <= float(rN))
        ck('C variant C (iterated dichotomy) verdict reproduced',
           okC == ent['holds_variantC'],
           'rho_1^B/r = %.6g -> %s' % (rhoB / rf, okC))
        ck('C variant BC = B or C reproduced',
           (okB or okC) == ent['holds_variantBC'])
        if (okB or okC) and vok:
            passing.append(rf)

    # [1] r_1 is the largest passing grid radius (variant B)
    got = max(passing) if passing else None
    want = C.get('r_1_variantBC_float')
    ck('1 declared r_1 (variant BC) is the max passing grid radius',
       (got is None and want is None) or
       (got is not None and want is not None and abs(got - want) < 1e-15),
       'recomputed %s, claimed %s' % (got, want))
    ck('1 r_1 <= r_N reported honestly',
       want is None or want <= float(rN),
       'r_1 = %s, r_N = %.4e' % (want, float(rN)))

    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
