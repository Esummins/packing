"""t3lib.py -- A30 T3 pilot: per-cell exclusion machinery for the drain lemma.

Implements the three exclusion tests of the T3 specification
(docs/proofs/drain_lemma.md v2) on a configuration CELL

    C = prod_i (cx_i-box x cy_i-box x theta_i-box)  x  s-box

using A22's variable layout (z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=theta_i,
z[33]=s; NV=34) and mpmath.iv validated interval arithmetic throughout.

  (a) infeasibility     : interval SAT certifies a pair overlaps on ALL of C,
                          or a containment row is < 0 on all of C.
  (b) D2 uniform slack  : every pair gap and every containment clearance has a
                          POSITIVE interval lower bound on C.
  (c) FJ exclusion      : for every selection S in C's menu, the Fritz John
                          system FJ(S) has no solution in C.

For (c) two sound tests are provided:

  (c1) FARKAS / improving-direction LP.  With the correct sign convention for
       "min s subject to g_k >= 0" the FJ stationarity row is

              lambda_0 * grad s  -  sum_k lambda_k grad g_k = 0,
              lambda >= 0, lambda_0 >= 0, lambda_0 + sum lambda_k = 1.

       If there is a vector y in R^34 with  grad s . y < 0  and
       grad g_k(z) . y > 0 for EVERY z in C and every row k that can be
       active on C, then dotting the stationarity row with y gives
       lambda_0*(<0) = sum lambda_k*(>0), forcing lambda_0 = 0 AND all
       lambda_k = 0, contradicting the normalisation.  So no FJ point of ANY
       menu selection lies in C.  One LP + one interval verification kills the
       whole menu at once (no menu enumeration).  This also covers the
       lambda_0 = 0 branch for free.

  (c2) interval KRAWCZYK on the square FJ system in the 35+m unknowns
       (z, lambda_0, lambda_1..lambda_m) for one selection S.  Needs second
       derivatives of the constraints, supplied by a small interval jet
       (value/gradient/Hessian) forward-AD.

Rows.  Containment needs no selection (176 rows: every corner coordinate in
[0,s]).  A pair separation selection is a triple (owner o, edge e of o,
dominant corner k* of the other square p) giving one SEPARATION row
       g = n_e(theta_o) . (q_{k*}(p) - c_o) - 1/2 >= 0
plus three DOMINANCE rows
       g = n_e(theta_o) . (q_m(p) - q_{k*}(p)) >= 0,  m != k*.
Dominance makes the selected row equal to true SAT separation, so S-feasible
=> interior-disjoint (soundness), and every configuration is S-feasible for at
least one selection (completeness).
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction

from mpmath import iv

IVDPS = 30
iv.dps = IVDPS

NV = 34
NSQ = 11

HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]   # outward normal of edge k
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------- jets

def _zeros(d):
    return [iv.mpf(0)] * d


class Jet:
    """value + (optionally) gradient + Hessian w.r.t. d local variables."""
    __slots__ = ('v', 'g', 'h', 'd', 'o')

    def __init__(self, v, g, h, d, o):
        self.v = v
        self.g = g
        self.h = h
        self.d = d
        self.o = o

    @staticmethod
    def const(c, d, o):
        return Jet(c, _zeros(d) if o >= 1 else None,
                   [_zeros(d) for _ in range(d)] if o >= 2 else None, d, o)

    @staticmethod
    def var(val, k, d, o):
        g = None
        if o >= 1:
            g = _zeros(d)
            g[k] = iv.mpf(1)
        h = [_zeros(d) for _ in range(d)] if o >= 2 else None
        return Jet(val, g, h, d, o)

    def __add__(self, b):
        if not isinstance(b, Jet):
            return Jet(self.v + b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        g = [self.g[i] + b.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[self.h[i][j] + b.h[i][j] for j in range(d)] for i in range(d)]
        return Jet(self.v + b.v, g, h, d, o)

    def __sub__(self, b):
        if not isinstance(b, Jet):
            return Jet(self.v - b, self.g, self.h, self.d, self.o)
        d, o = self.d, self.o
        g = [self.g[i] - b.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[self.h[i][j] - b.h[i][j] for j in range(d)] for i in range(d)]
        return Jet(self.v - b.v, g, h, d, o)

    def __neg__(self):
        d, o = self.d, self.o
        g = [-self.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[-self.h[i][j] for j in range(d)] for i in range(d)]
        return Jet(-self.v, g, h, d, o)

    def __mul__(self, b):
        d, o = self.d, self.o
        if not isinstance(b, Jet):
            g = [self.g[i] * b for i in range(d)] if o >= 1 else None
            h = None
            if o >= 2:
                h = [[self.h[i][j] * b for j in range(d)] for i in range(d)]
            return Jet(self.v * b, g, h, d, o)
        g = None
        if o >= 1:
            g = [self.g[i] * b.v + self.v * b.g[i] for i in range(d)]
        h = None
        if o >= 2:
            h = [[self.h[i][j] * b.v + self.g[i] * b.g[j]
                  + self.g[j] * b.g[i] + self.v * b.h[i][j]
                  for j in range(d)] for i in range(d)]
        return Jet(self.v * b.v, g, h, d, o)

    __rmul__ = __mul__

    def _chain(self, f, df, d2f):
        d, o = self.d, self.o
        g = [df * self.g[i] for i in range(d)] if o >= 1 else None
        h = None
        if o >= 2:
            h = [[df * self.h[i][j] + d2f * self.g[i] * self.g[j]
                  for j in range(d)] for i in range(d)]
        return Jet(f, g, h, d, o)

    def cos(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._chain(c, -s, -c)

    def sin(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._chain(s, c, -s)


# ------------------------------------------------------------------- rows
# A row is a dict; 'vars' is the tuple of GLOBAL variable indices it touches,
# in the order used by its local jet indices.

def wall_row(i, corner, wall):
    vs = (3 * i, 3 * i + 1, 3 * i + 2) + ((33,) if wall in ('x=s', 'y=s') else ())
    return {'kind': 'wall', 'i': i, 'corner': corner, 'wall': wall, 'vars': vs}


def sep_row(o, e, p, kstar):
    """separation: n_e(theta_o) . (q_kstar(p) - c_o) - 1/2 >= 0"""
    return {'kind': 'sep', 'o': o, 'e': e, 'p': p, 'k': kstar,
            'vars': (3 * o, 3 * o + 1, 3 * o + 2, 3 * p, 3 * p + 1, 3 * p + 2)}


def dom_row(o, e, p, kstar, m):
    """dominance: n_e(theta_o) . (q_m(p) - q_kstar(p)) >= 0"""
    return {'kind': 'dom', 'o': o, 'e': e, 'p': p, 'k': kstar, 'm': m,
            'vars': (3 * o + 2, 3 * p + 2)}


def row_key(r):
    if r['kind'] == 'wall':
        return ('W', r['i'], r['corner'], r['wall'])
    if r['kind'] == 'sep':
        return ('S', r['o'], r['e'], r['p'], r['k'])
    return ('D', r['o'], r['e'], r['p'], r['k'], r['m'])


def row_name(r):
    k = row_key(r)
    return '-'.join(str(x) for x in k)


_HALF_IV = None


def _hiv(x):
    return iv.mpf(x.numerator) / iv.mpf(x.denominator)


def eval_row(box, r, order=1):
    """Interval jet of row r on interval box `box` (list of 34 iv.mpf).

    Returns Jet with local variable order r['vars'].
    """
    vs = r['vars']
    d = len(vs)
    o = order
    loc = {gi: k for k, gi in enumerate(vs)}
    V = [Jet.var(box[gi], k, d, o) for k, gi in enumerate(vs)]
    half = iv.mpf(1) / iv.mpf(2)

    if r['kind'] == 'wall':
        i = r['i']
        cx, cy, th = V[0], V[1], V[2]
        hx, hy = _hiv(HALF[r['corner']][0]), _hiv(HALF[r['corner']][1])
        c, s = th.cos(), th.sin()
        qx = cx + (c * hx - s * hy)
        qy = cy + (s * hx + c * hy)
        w = r['wall']
        if w == 'x=0':
            return qx
        if w == 'y=0':
            return qy
        S = V[3]
        return (S - qx) if w == 'x=s' else (S - qy)

    if r['kind'] == 'sep':
        cox, coy, tho, cpx, cpy, thp = V
        nhx, nhy = NHAT[r['e']]
        co, so = tho.cos(), tho.sin()
        nx = co * nhx - so * nhy
        ny = so * nhx + co * nhy
        hx, hy = _hiv(HALF[r['k']][0]), _hiv(HALF[r['k']][1])
        cp, sp = thp.cos(), thp.sin()
        qx = cpx + (cp * hx - sp * hy)
        qy = cpy + (sp * hx + cp * hy)
        return nx * (qx - cox) + ny * (qy - coy) - half

    if r['kind'] == 'dom':
        tho, thp = V
        nhx, nhy = NHAT[r['e']]
        co, so = tho.cos(), tho.sin()
        nx = co * nhx - so * nhy
        ny = so * nhx + co * nhy
        dx = _hiv(HALF[r['m']][0] - HALF[r['k']][0])
        dy = _hiv(HALF[r['m']][1] - HALF[r['k']][1])
        cp, sp = thp.cos(), thp.sin()
        vx = cp * dx - sp * dy
        vy = sp * dx + cp * dy
        return nx * vx + ny * vy

    raise ValueError(r['kind'])


def row_value(box, r):
    return eval_row(box, r, order=0).v


def row_grad(box, r):
    """(value, {global index: iv})"""
    j = eval_row(box, r, order=1)
    return j.v, {gi: j.g[k] for k, gi in enumerate(r['vars'])}


def row_grad_hess(box, r):
    j = eval_row(box, r, order=2)
    vs = r['vars']
    g = {gi: j.g[k] for k, gi in enumerate(vs)}
    h = {}
    for a, ga in enumerate(vs):
        for b, gb in enumerate(vs):
            h[(ga, gb)] = j.h[a][b]
    return j.v, g, h


# ------------------------------------------------------------------- cells

def box_from(center, radius):
    """center: list of 34 Fraction/float; radius: scalar or list."""
    if not isinstance(radius, (list, tuple)):
        radius = [radius] * NV
    out = []
    for x, r in zip(center, radius):
        lo, hi = _to_iv(x - r), _to_iv(x + r)
        out.append(iv.mpf([lo.a, hi.b]))
    return out


def _to_iv(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def clip_s(box, s0):
    """Intersect the s-component with (-inf, s0]; also raise its lower bound
    to the certified minimum of sigma over the cell."""
    b = list(box)
    s0i = _to_iv(s0)
    lo = b[33].a
    hi = min(b[33].b, s0i.b)
    # sigma(z) >= every corner coordinate, so s >= max over corners of inf(q)
    best = None
    for i in range(NSQ):
        for c in range(4):
            for w in ('x=0', 'y=0'):
                v = row_value(box, wall_row(i, c, w))
                if best is None or v.a > best:
                    best = v.a
    if best is not None and best > lo:
        lo = best
    if lo > hi:
        return None
    b[33] = iv.mpf([lo, hi])
    return b


def iv_min(a, b):
    return iv.mpf([min(a.a, b.a), min(a.b, b.b)])


def iv_max(a, b):
    return iv.mpf([max(a.a, b.a), max(a.b, b.b)])


def corner_pos_iv(box, i, corner):
    hx, hy = _hiv(HALF[corner][0]), _hiv(HALF[corner][1])
    th = box[3 * i + 2]
    c, s = iv.cos(th), iv.sin(th)
    return box[3 * i] + (c * hx - s * hy), box[3 * i + 1] + (s * hx + c * hy)


def pair_sep_iv(box, i, j):
    """Interval enclosure of the SAT separation max over the 4 candidate axes."""
    ci = [corner_pos_iv(box, i, c) for c in range(4)]
    cj = [corner_pos_iv(box, j, c) for c in range(4)]
    best = None
    for sq in (i, j):
        th = box[3 * sq + 2]
        co, si = iv.cos(th), iv.sin(th)
        for nhx, nhy in ((1, 0), (0, 1)):
            nx = co * nhx - si * nhy
            ny = si * nhx + co * nhy
            pi = [nx * qx + ny * qy for qx, qy in ci]
            pj = [nx * qx + ny * qy for qx, qy in cj]
            lo_i = hi_i = pi[0]
            lo_j = hi_j = pj[0]
            for p in pi[1:]:
                lo_i = iv_min(lo_i, p); hi_i = iv_max(hi_i, p)
            for p in pj[1:]:
                lo_j = iv_min(lo_j, p); hi_j = iv_max(hi_j, p)
            gap = iv_max(lo_j - hi_i, lo_i - hi_j)
            best = gap if best is None else iv_max(best, gap)
    return best


# ------------------------------------------------------- tests (a) and (b)

def test_ab(box):
    """Returns dict with keys: infeasible (bool + reason), d2 (bool, delta),
    wall_rows (straddling containment rows), pair_state per pair."""
    res = {'infeasible': False, 'reason': None, 'd2': False, 'delta': None,
           'wall_straddle': [], 'pairs': {}}
    min_clear = None
    for i in range(NSQ):
        for c in range(4):
            for w in WALLS:
                r = wall_row(i, c, w)
                v = row_value(box, r)
                if v.b < 0:
                    res['infeasible'] = True
                    res['reason'] = 'containment %s' % row_name(r)
                    return res
                if v.a <= 0:
                    res['wall_straddle'].append(r)
                if min_clear is None or v.a < min_clear:
                    min_clear = v.a
    min_gap = None
    for i in range(NSQ):
        for j in range(i + 1, NSQ):
            g = pair_sep_iv(box, i, j)
            if g.b < 0:
                res['infeasible'] = True
                res['reason'] = 'pair %d-%d certainly overlapping' % (i, j)
                return res
            st = 'separated' if g.a > 0 else 'straddle'
            res['pairs'][(i, j)] = (st, float(g.a), float(g.b))
            if min_gap is None or g.a < min_gap:
                min_gap = g.a
    # ---- D2, CENTROID form.
    # The advisor's draft asks for "every pairwise SAT-gap AND every
    # bounding-box clearance >= delta".  The second half is VACUOUS: sigma is
    # the side of the MINIMAL enclosing square, so the extremal corners have
    # clearance exactly 0 at every configuration.  What the proof actually
    # needs is only the pairwise gaps, with the shrink taken about the centre
    # m = (sigma/2, sigma/2) instead of the origin:
    #   c_i -> m + (c_i - m)(1 - eta),   eta = delta / (2 sqrt2 sigma).
    # Relative centre displacement is |c_i-c_j| eta <= sqrt2 sigma eta = delta/2,
    # so every gap stays >= delta/2 > 0 (interiors still disjoint); and the
    # owner of the max-x corner has c_x >= sigma_x_max - sqrt2/2 > sigma/2
    # while the owner of the min-x corner has c_x < sigma/2 whenever
    # sigma > sqrt2, so BOTH extents strictly decrease and sigma strictly
    # drops.  sigma >= 3 on every cell of interest here, so the side condition
    # is free.  Hence: min pairwise gap > 0 uniformly on C  =>  no minimiser.
    res['delta'] = float(min_gap)
    res['d2'] = float(min_gap) > 0
    res['min_gap'] = float(min_gap)
    res['min_clear'] = float(min_clear)
    return res


# ------------------------------------------------------------------ menus

def pair_menu(box, i, j):
    """All (owner, edge, dominant corner) selections for pair (i,j) that are
    not certified inconsistent on the cell, with the interval status of their
    4 rows.  Returns list of dicts."""
    out = []
    for o, p in ((i, j), (j, i)):
        for e in range(4):
            for k in range(4):
                rows = [sep_row(o, e, p, k)] + [dom_row(o, e, p, k, m)
                                                for m in range(4) if m != k]
                vals = [row_value(box, r) for r in rows]
                if any(v.b < 0 for v in vals):
                    continue        # certified S-infeasible on all of C
                out.append({'o': o, 'e': e, 'p': p, 'k': k, 'rows': rows,
                            'vals': vals,
                            'straddle': [rr for rr, vv in zip(rows, vals)
                                         if vv.a <= 0]})
    return out


def build_menu(box, ab):
    """Per-pair menus for pairs that straddle activity + the union of all rows
    that can be active anywhere in the menu."""
    menus = {}
    union = {}
    for r in ab['wall_straddle']:
        union[row_key(r)] = r
    for (i, j), (st, lo, hi) in ab['pairs'].items():
        if st == 'separated':
            continue
        m = pair_menu(box, i, j)
        menus[(i, j)] = m
        for sel in m:
            for r in sel['straddle']:
                union[row_key(r)] = r
    # An EMPTY pair menu certifies infeasibility, and is strictly stronger than
    # the interval-SAT test in test_ab: if every one of the 32 selections for a
    # pair has a row that is < 0 on ALL of C, then by completeness of the
    # selection menu no z in C has that pair interior-disjoint, so C n D_0 = 0.
    empty = [k for k, v in menus.items() if not v]
    size = 1
    for m in menus.values():
        size *= len(m)
    return {'menus': menus, 'union': list(union.values()),
            'menu_size': size,
            'empty_pairs': empty,
            'n_straddle_pairs': len(menus),
            'per_pair': {k: len(v) for k, v in menus.items()}}


# ----------------------------------------------------------- (c1) Farkas LP

def farkas_lp(box, rows, ybound=1.0):
    """Look for y in R^34 with y[33] <= -eps and inf_{C} grad g_r . y >= eps
    for every row r in `rows`.  Returns (ok, y, eps, info)."""
    import numpy as np
    from scipy.optimize import linprog
    G = []
    for r in rows:
        _, g = row_grad(box, r)
        lo = np.zeros(NV); hi = np.zeros(NV)
        for gi, val in g.items():
            lo[gi] = float(val.a); hi[gi] = float(val.b)
        G.append((lo, hi))
    n = 2 * NV + 1
    A = []; b = []
    for lo, hi in G:
        row = np.zeros(n)
        row[:NV] = -lo
        row[NV:2 * NV] = hi
        row[-1] = 1.0
        A.append(row); b.append(0.0)
    row = np.zeros(n)
    row[33] = 1.0; row[NV + 33] = -1.0; row[-1] = 1.0
    A.append(row); b.append(0.0)
    c = np.zeros(n); c[-1] = -1.0
    bounds = [(0, ybound)] * (2 * NV) + [(0, 1.0)]
    r = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=bounds,
                method='highs')
    if not r.success:
        return False, None, 0.0, {'status': r.message}
    eps = -r.fun
    y = r.x[:NV] - r.x[NV:2 * NV]
    return eps > 1e-12, y, float(eps), {'status': 'ok'}


def grad_cache(box, rows):
    """{row key: (lo array, hi array, {gi: iv})} for reuse across selections."""
    import numpy as np
    out = {}
    for r in rows:
        _, g = row_grad(box, r)
        lo = np.zeros(NV); hi = np.zeros(NV)
        for gi, val in g.items():
            lo[gi] = float(val.a); hi[gi] = float(val.b)
        out[row_key(r)] = (lo, hi, g)
    return out


def farkas_lp_cached(cache, keys, ybound=1.0):
    """Farkas LP using precomputed interval gradients (keys = rows to beat)."""
    import numpy as np
    from scipy.optimize import linprog
    n = 2 * NV + 1
    A = np.zeros((len(keys) + 1, n)); b = np.zeros(len(keys) + 1)
    for i, k in enumerate(keys):
        lo, hi, _ = cache[k]
        A[i, :NV] = -lo
        A[i, NV:2 * NV] = hi
        A[i, -1] = 1.0
    A[-1, 33] = 1.0; A[-1, NV + 33] = -1.0; A[-1, -1] = 1.0
    c = np.zeros(n); c[-1] = -1.0
    bounds = [(0, ybound)] * (2 * NV) + [(0, 1.0)]
    r = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if not r.success:
        return False, None, 0.0
    eps = -r.fun
    return eps > 1e-12, r.x[:NV] - r.x[NV:2 * NV], float(eps)


def verify_farkas_cached(cache, keys, y):
    """Rigorous interval check of a Farkas direction using cached gradients."""
    yiv = [_to_iv(Fraction(float(v)).limit_denominator(10 ** 12)) for v in y]
    if not (yiv[33].b < 0):
        return False, None
    worst = None
    for k in keys:
        g = cache[k][2]
        acc = iv.mpf(0)
        for gi, val in g.items():
            acc = acc + val * yiv[gi]
        if worst is None or acc.a < worst:
            worst = float(acc.a)
        if not (acc.a > 0):
            return False, float(acc.a)
    return True, worst


def verify_farkas(box, rows, y):
    """Rigorous interval verification of a Farkas direction y."""
    yiv = [_to_iv(Fraction(float(v)).limit_denominator(10 ** 12)) for v in y]
    if not (yiv[33].b < 0):
        return False, None
    worst = None
    for r in rows:
        _, g = row_grad(box, r)
        acc = iv.mpf(0)
        for gi, val in g.items():
            acc = acc + val * yiv[gi]
        if worst is None or acc.a < worst:
            worst = acc.a
        if not (acc.a > 0):
            return False, float(acc.a)
    return True, float(worst)


# ------------------------------------------------- (c2) Krawczyk on FJ(S)

def fj_system_rows(box, sel_rows, wall_rows):
    """Rows entering the FJ system for one selection: containment rows that
    straddle + the selection's straddling rows."""
    return list(wall_rows) + list(sel_rows)


def fj_eval(box, rows, lam0, lam, order=2, cache=None, mode='compl'):
    """F and J of the FJ system at interval point (box, lam0, lam).

    Unknown order: z[0..33], lam0, lam[0..m-1].  n = 35 + m.
    F = [ lam0*e_s - sum lam_k grad g_k   (34)
          lam_k * g_k                      (m)
          lam0 + sum lam_k - 1             (1) ]
    """
    m = len(rows)
    n = NV + 1 + m
    if cache is None:
        cache = [row_grad_hess(box, r) if order >= 2 else row_grad(box, r) + ({},)
                 for r in rows]
    F = [iv.mpf(0)] * n
    J = [dict() for _ in range(n)]
    # stationarity
    for j in range(NV):
        F[j] = lam0 if j == 33 else iv.mpf(0)
    for k, (v, g, h) in enumerate(cache):
        lk = lam[k]
        for gi, val in g.items():
            F[gi] = F[gi] - lk * val
            J[gi][NV + 1 + k] = -val
        if order >= 2:
            for (ga, gb), val in h.items():
                cur = J[ga].get(gb)
                J[ga][gb] = (cur if cur is not None else iv.mpf(0)) - lk * val
    J[33][NV] = iv.mpf(1)
    # complementarity ('compl': lam_k g_k = 0) or fixed active set ('active': g_k = 0)
    for k, (v, g, h) in enumerate(cache):
        idx = NV + k
        if mode == 'active':
            F[idx] = v
            for gi, val in g.items():
                J[idx][gi] = val
        else:
            F[idx] = lam[k] * v
            for gi, val in g.items():
                J[idx][gi] = lam[k] * val
            J[idx][NV + 1 + k] = v
    # normalisation
    idx = NV + m
    acc = lam0 - iv.mpf(1)
    for k in range(m):
        acc = acc + lam[k]
    F[idx] = acc
    J[idx][NV] = iv.mpf(1)
    for k in range(m):
        J[idx][NV + 1 + k] = iv.mpf(1)
    return F, J, n


def fj_range_exclude(box, rows, lam0_box, lam_box, mode='compl'):
    """Cheap dimension-agnostic exclusion: if the interval evaluation of some
    FJ component does not contain 0, FJ(S) has no solution in the box."""
    F, _, _ = fj_eval(box, rows, lam0_box, lam_box, order=1,
                      cache=[row_grad(box, r) + ({},) for r in rows], mode=mode)
    for i, f in enumerate(F):
        if f.a > 0 or f.b < 0:
            return True, i
    return False, None


def _mid(x):
    """Python float midpoint of an interval (x.a / x.b are degenerate ivs)."""
    return (float(x.a) + float(x.b)) / 2.0


def krawczyk_fj(box, rows, lam0_box, lam_box, verbose=False, mode='compl'):
    """One Krawczyk step on FJ(S) over the box (box x lam0_box x lam_box).

    Returns dict with 'excluded' (K ∩ N = empty), 'isolated' (K ⊂ int N),
    'ratio' (max width ratio) and timing.
    """
    import time
    import numpy as np
    t0 = time.time()
    m = len(rows)
    n = NV + 1 + m
    N = list(box) + [lam0_box] + list(lam_box)
    mid = [_mid(x) for x in N]
    midbox = [iv.mpf(x) for x in mid]

    # midpoint F and J (thin)
    cache_mid = [row_grad_hess(midbox[:NV], r) for r in rows]
    Fm, Jm, _ = fj_eval(midbox[:NV], rows, midbox[NV], midbox[NV + 1:],
                        order=2, cache=cache_mid, mode=mode)
    Jf = np.zeros((n, n))
    for i in range(n):
        for j, val in Jm[i].items():
            Jf[i, j] = float(_mid(val))
    try:
        Y = np.linalg.inv(Jf)
        cond = float(np.linalg.cond(Jf))
    except np.linalg.LinAlgError:
        return {'excluded': False, 'isolated': False, 'singular': True,
                'cond': float('inf'), 'n': n, 'secs': time.time() - t0}
    if not np.isfinite(cond) or cond > 1e14:
        singular = True
    else:
        singular = False

    # interval F at midpoint, interval J over N
    cache_box = [row_grad_hess(box, r) for r in rows]
    _, JN, _ = fj_eval(box, rows, N[NV], N[NV + 1:], order=2, cache=cache_box,
                       mode=mode)
    Yiv = [[iv.mpf(float(Y[i][j])) for j in range(n)] for i in range(n)]

    # rigorous enclosure of N - mid (mid is an exact binary float)
    rad = [N[i] - iv.mpf(mid[i]) for i in range(n)]

    # K_i = mid_i - (Y F(mid))_i + sum_j (I - Y J)_ij * rad_j
    YF = [iv.mpf(0)] * n
    for i in range(n):
        acc = iv.mpf(0)
        for j in range(n):
            if Y[i][j] != 0.0:
                acc = acc + Yiv[i][j] * Fm[j]
        YF[i] = acc
    # (Y J)_ij : J is sparse by rows
    YJ = [dict() for _ in range(n)]
    for r in range(n):
        Jr = JN[r]
        if not Jr:
            continue
        for i in range(n):
            yir = Y[i][r]
            if yir == 0.0:
                continue
            yv = Yiv[i][r]
            di = YJ[i]
            for j, val in Jr.items():
                cur = di.get(j)
                di[j] = (cur + yv * val) if cur is not None else yv * val
    excluded = False
    isolated = True
    worst = 0.0
    for i in range(n):
        Ki = iv.mpf(mid[i]) - YF[i]
        di = YJ[i]
        for j in range(n):
            w = rad[j]
            if float(w.a) == 0.0 and float(w.b) == 0.0:
                continue
            coef = di.get(j)
            e = (iv.mpf(1) if i == j else iv.mpf(0))
            coef = (e - coef) if coef is not None else e
            if float(coef.a) == 0.0 and float(coef.b) == 0.0:
                continue
            Ki = Ki + coef * w
        if Ki.b < N[i].a or Ki.a > N[i].b:
            excluded = True
        if not (Ki.a > N[i].a and Ki.b < N[i].b):
            isolated = False
        hw = (float(N[i].b) - float(N[i].a)) / 2.0
        if hw > 0:
            worst = max(worst, max(abs(float(Ki.a) - mid[i]),
                                   abs(float(Ki.b) - mid[i])) / hw)
    return {'excluded': bool(excluded), 'isolated': bool(isolated and not singular),
            'singular': bool(singular), 'cond': cond, 'n': n,
            'ratio': worst, 'secs': time.time() - t0}


# ---------------------------------------------------------------- loading

def frac_str(x):
    return '%d/%d' % (x.numerator, x.denominator)


def str_frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def load_trump():
    p = os.path.join(HERE, '..', 'A03-upper-reconstruct', 'trump11_exact.json')
    from decimal import Decimal, getcontext
    getcontext().prec = 200
    d = json.load(open(p))
    z = []
    for sq in d['squares']:
        for k in ('cx', 'cy', 'theta'):
            z.append(Fraction(Decimal(sq[k])))
    z.append(Fraction(Decimal(d['s'])))
    return z, d


def load_a22_cert():
    p = os.path.join(HERE, '..', 'A22-local-rigidity', 'results',
                     'krawczyk_cert.json')
    return json.load(open(p))
