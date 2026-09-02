#!/usr/bin/env python3
"""a40_check_exact.py -- EXACT-RATIONAL re-checker for A40's basin-surgery
certificate store (results/certs_a40/ring_*/*.json).

A76 rung: what A70's a36_check_exact.py did for A36, this does for A40 --
mpmath.iv is taken OUT of the decision path.  Same store, same row language,
same S1-S7 checks, same [COV]/[CHAIN] logic and the same 5 corruption gates as
the frozen attempts/A40-basin-surgery/code/a40_check.py (which is NOT modified
and NOT imported), but every accept/reject decision is made in exact rational
arithmetic:

  * intervals are pairs of Fractions, OUTWARD-rounded to the dyadic grid
    2^-PREC after every operation (rounding only widens -- sound);
  * cos/sin enclosures over rational intervals use certified alternating
    Taylor partial sums (|x| <= 1 asserted; consecutive-term ratio
    x^2/((2k+1)(2k+2)) < 1 from k = 0, so partial sums bracket) plus
    monotonicity/evenness -- NO mpmath, NO floats in any accept decision;
  * the float fudges of the original (`math.nextafter` inflation in
    mag/sup/inf, `Fraction(float)` re-quantisation of interval endpoints,
    iv dps-60 outward rounding) are replaced by the exact endpoints, which
    are sharper upper/lower bounds, so every original PASS must persist;
  * certificates carry float claims (V0_sup, eps_w, Hbar, margin) in
    cert['claims'].  The frozen a40_check.py never reads them: it recomputes
    V0, eps_w, Hbar and the margin from scratch and decides MARGIN > 0 on the
    recomputed value.  This checker does the same -- the claims are compared
    only for the informational summary written to the report, never gating.

stdlib only: fractions + json + glob + os + sys + time.  The order-2 interval
jets (class J), the exact IV kernel and the cos/sin enclosures are transcribed
from attempts/A70-lean-wave4/code/a36_check_exact.py; the row language, the
S1-S7 checks, the [ROW]/[M]/[COV]/[CHAIN] logic and the corruption modes are
transcribed from attempts/A40-basin-surgery/code/a40_check.py (A36/A35
lineage).  Where the two differ, A40's SEMANTICS win and A70's ARITHMETIC wins.

WHAT IS VERIFIED (A40 notes/theory.md S1-S7), per certificate:

 [O]  all multipliers >= 0 (rows and cuts), rationals parse.
 [F]  the face cut matches the certificate's face (coord, sign, value -h_in);
      tie cuts have +-1 coefficients on two theta coordinates and value -+tau.
 [ROW] every loaded row's validity claim re-verified over the claimed scope
      box (ring box(h_out), or the face sub-box): wall / aux / V (S1) /
      safe (S4a) / forced (S4b) / branch (S3) / floor (S7) / relfloor (S7').
 [M]  the margin chain recomputed from scratch (anchor / leaf-empty / empty),
      with V0 the signed interval value sum, eps_w the exact l1 gradient
      residual and Hbar the accumulated interval Hessian over box(h_out),
      off-diagonals by magnitude, diagonals by positive part (S5).
 [COV] per (ring, face): the certificates form a covering split tree.
 [CHAIN] rings tile [h0 = 37/10000, h_reached]; every face certified in
      every ring.

Corruption controls (each MUST make the checker fail):
    omega-sign   flip the sign of one loaded row multiplier
    h-big        grow h_out by 8x without re-deriving
    drop-anchor  zero the face-cut multiplier of an anchor certificate
    floor-raise  raise one floor row's claimed lower bound by 0.01
    drop-sibling delete one branched certificate (coverage must fail)

Usage:  python a40_check_exact.py [certdir] [krawczyk_cert.json]
                                  [--corrupt {omega-sign,h-big,drop-anchor,
                                              floor-raise,drop-sibling}]
                                  [--report PATH]
Exit 0 = all PASS (or, under --corrupt, failed as required).
"""
import glob
import json
import os
import sys
import time
from fractions import Fraction

PREC = 330                     # dyadic grid 2^-PREC for outward rounding
GRID = 1 << PREC
NV = 34
S_IDX = 33
H0 = Fraction(37, 10000)
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]      # outward normal of edge k


def frac(s):
    """A40's frac: 'n/d' string, or anything Fraction() accepts (incl. float,
    which becomes the EXACT rational that float denotes)."""
    if isinstance(s, str) and '/' in s:
        n, d = s.split('/')
        return Fraction(int(n), int(d))
    return Fraction(s)


# --------------------------------------------------------------- exact kernel
# (transcribed from A70's a36_check_exact.py)
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
        """exact replacement for a40's mag() (which inflated by nextafter)."""
        return max(abs(self.lo), abs(self.hi))


IZERO = IV.point(Fraction(0))
IONE = IV.point(Fraction(1))


def _cos_pt(x):
    """certified bracket of cos x at a rational point, |x| <= 1: alternating
    Taylor partial sums with strictly decreasing terms bracket the value."""
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
    """certified bracket of sin x at a rational point, |x| <= 1."""
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


# ---- order-2 forward jets over exact intervals (structure = a40_check.J)
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


# ------------------------------------------------------ row language (A40)
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


def _row_jet_raw(box, c, order):
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


def con_key(c):
    if c['kind'] == 'wall':
        return ('wall', c['i'], c['corner'], c['wall'])
    if c['kind'] == 'edge':
        return ('edge', c['i'], c['corner'], c['j'], c['edge'])
    if c['kind'] == 'dist':
        return ('dist', c['i'], c['j'])
    raise ValueError(c['kind'])


# Memo caches.  Jets are pure functions of (box, constraint, order) and the J
# objects are never mutated, so memoising changes nothing but the runtime.
_JET = {}
_TD = {}
_KILL = {}


class Box(object):
    """a box plus a hashable token identifying it (for jet memoisation)."""
    __slots__ = ('v', 'tok')

    def __init__(self, v, tok):
        self.v, self.tok = v, tok

    def __getitem__(self, k):
        return self.v[k]


def row_jet(box, c, order):
    key = (box.tok, con_key(c), order)
    out = _JET.get(key)
    if out is None:
        out = _row_jet_raw(box.v, c, order)
        _JET[key] = out
    return out


def td_of(box, o, e, p, k):
    """(t, d) of corner k of p in owner o's edge-e frame (S1's coords)."""
    key = (box.tok, o, e, p, k)
    out = _TD.get(key)
    if out is not None:
        return out
    b = box.v
    hx, hy = HALF[k]
    cp, sp = cos_iv(b[3 * p + 2]), sin_iv(b[3 * p + 2])
    qx = b[3 * p] + (cp * hx - sp * hy)
    qy = b[3 * p + 1] + (sp * hx + cp * hy)
    nhx, nhy = NHAT[e]
    co, so = cos_iv(b[3 * o + 2]), sin_iv(b[3 * o + 2])
    nx = co * nhx - so * nhy
    ny = so * nhx + co * nhy
    wx, wy = qx - b[3 * o], qy - b[3 * o + 1]
    out = ((-ny) * wx + nx * wy, nx * wx + ny * wy - Fraction(1, 2))
    _TD[key] = out
    return out


def axis_killed(box, o, e, p):
    """True iff some corner row of the axis has sup < 0 on box (S3 kill)."""
    key = (box.tok, o, e, p)
    out = _KILL.get(key)
    if out is not None:
        return out
    out = False
    for k in range(4):
        if td_of(box, o, e, p, k)[1].hi < 0:
            out = True
            break
    _KILL[key] = out
    return out


def pair_axes(i, j):
    return [(i, e, j) for e in range(4)] + [(j, e, i) for e in range(4)]


def box_of(z0, r):
    return Box([IV(x - r, x + r) for x in z0], ('R', r))


def point_box(z0):
    return Box([IV.point(x) for x in z0], ('P',))


def face_box(z0, i, sgn, h_in, h_out):
    out = []
    for q in range(NV):
        lo, hi = z0[q] - h_out, z0[q] + h_out
        if q == i:
            if sgn > 0:
                lo = z0[q] + h_in
            else:
                hi = z0[q] - h_in
        out.append(IV(lo, hi))
    return Box(out, ('F', i, sgn, h_in, h_out))


class Check(object):
    def __init__(self, log):
        self.fails = []
        self.lines = []
        self.n = 0
        self.log = log

    def __call__(self, name, ok, detail=''):
        self.n += 1
        if not ok:
            self.fails.append(name)
            line = '  [FAIL] %s %s' % (name, detail)
            self.lines.append(line)
            self.log(line)
        return ok


def axis_of_edge_con(c):
    return (c['j'], c['edge'], c['i'])


def pair_of_edge_con(c):
    return tuple(sorted((c['i'], c['j'])))


def check_cert(cert, z0, K, ck, stats):
    name = os.path.basename(cert['_file'])
    h_in = frac(cert['h_in'])
    h_out = frac(cert['h_out'])
    fc = cert['face']
    i, sgn = fc['coord'], fc['sign']
    rbox = box_of(z0, h_out)
    fbox = face_box(z0, i, sgn, h_in, h_out)
    pbox = point_box(z0)

    def scope_box(scope):
        return rbox if scope == 'ring' else fbox

    if cert['type'] == 'A40-empty':
        c = cert['empty_row']['con']
        ck('%s wall kind' % name, c['kind'] == 'wall')
        v, _ = row_jet(fbox, c, 0)
        ck('%s empty sup<0' % name, v.v.hi < 0, 'sup=%g' % float(v.v.hi))
        return

    is_anchor = cert['type'] == 'A40-anchor'
    scope = cert.get('facts_scope', 'ring')
    sbox = scope_box(scope if scope == 'ring' else 'face')

    # [O] multipliers, [F] cuts
    rows = cert['rows']
    oms = [frac(r['omega']) for r in rows]
    ck('%s omega>=0' % name, all(q >= 0 for q in oms))
    cuts = cert.get('cuts', [])
    ocs = [frac(c.get('omega', '0')) for c in cuts]
    ck('%s cut omega>=0' % name, all(q >= 0 for q in ocs))
    branch_ctx = {tuple(b['pair']): tuple(b['branch_axis'])
                  for b in cert.get('branched_pairs', [])}
    if is_anchor:
        fcuts = [c for c in cuts if c['label'].startswith('face:')]
        ck('%s one face cut' % name, len(fcuts) == 1)
        if fcuts:
            c = fcuts[0]
            ok = (c['coeffs'] == {str(i): sgn} and
                  frac(c['value']) == -h_in)
            ck('%s face cut spec' % name, ok)
    for c in cuts:
        if c['label'].startswith('face:'):
            continue
        cf = {int(k): v for k, v in c['coeffs'].items()}
        ok = (len(cf) == 2 and sorted(cf.values()) == [-1, 1] and
              all(k < 33 and k % 3 == 2 for k in cf))
        ck('%s tie cut coeffs %s' % (name, c['label']), ok)

    # [ROW] validity claims + collect jets at z-hat and over box
    V0 = IZERO
    acc = {}
    accH = {}
    for r, q in zip(rows, oms):
        if q == 0:
            continue
        c = r['con']
        val = r['validity']
        mode = val['mode']
        rsbox = scope_box(val.get('scope', 'ring'))
        if mode == 'wall':
            ck('%s wall row kind' % name, c['kind'] == 'wall')
        elif mode == 'aux':
            ok = c['kind'] == 'dist' and \
                any(c['i'] == a and c['j'] == b for a, b in
                    ((0, 1), (1, 0), (0, 3), (3, 0)))
            ck('%s aux row is A22 aux' % name, ok)
        elif mode == 'V':
            t, d = td_of(rsbox, c['j'], c['edge'], c['i'], c['corner'])
            ck('%s V row %s' % (name, r['tag']),
               t.mag() < Fraction(1, 2) and d.lo > Fraction(-1, 2),
               '|t|=%g d_inf=%g' % (float(t.mag()), float(d.lo)))
        elif mode == 'safe':
            o, e, p = axis_of_edge_con(c)
            glo = min(td_of(rsbox, o, e, p, k)[1].lo for k in range(4))
            ck('%s safe axis %s' % (name, r['tag']), glo >= 0,
               'gap_inf=%g' % float(glo))
        elif mode == 'forced':
            o, e, p = axis_of_edge_con(c)
            pr = pair_of_edge_con(c)
            others = [a for a in pair_axes(*pr) if a != (o, e, p)]
            ck('%s forced axis %s' % (name, r['tag']),
               all(axis_killed(rsbox, *a) for a in others))
        elif mode == 'branch':
            ax = axis_of_edge_con(c)
            pr = pair_of_edge_con(c)
            ck('%s branch row axis matches ctx %s' % (name, r['tag']),
               branch_ctx.get(pr) == ax,
               '%s vs %s' % (branch_ctx.get(pr), ax))
        elif mode == 'floor':
            lb = frac(val['lower_bound'])
            v, _ = row_jet(rbox, c, 0)
            ck('%s floor lb %s' % (name, r['tag']), v.v.lo >= lb,
               'inf=%g lb=%g' % (float(v.v.lo), float(lb)))
        elif mode == 'relfloor':
            # S7': g_a - g_b = nhat_e . R(theta_p - theta_o) (h_ka - h_kb),
            # with the sibling g_b pointwise-[V]-valid on the face sub-box.
            rc = val['ref_con']
            ok = (rc['kind'] == 'edge' and c['kind'] == 'edge' and
                  rc['j'] == c['j'] and rc['edge'] == c['edge'] and
                  rc['i'] == c['i'] and rc['corner'] != c['corner'])
            ck('%s relfloor same axis %s' % (name, r['tag']), ok)
            t, d = td_of(fbox, rc['j'], rc['edge'], rc['i'], rc['corner'])
            ck('%s relfloor sibling V %s' % (name, r['tag']),
               t.mag() < Fraction(1, 2) and d.lo > Fraction(-1, 2))
            o, e, p = rc['j'], rc['edge'], rc['i']
            # delta interval from the ring box, refined by this cert's cuts
            dlo, dhi = -2 * h_out, 2 * h_out
            for ct2 in cuts:
                cf = {int(kq): vq for kq, vq in ct2['coeffs'].items()}
                if set(cf) != {3 * o + 2, 3 * p + 2}:
                    continue
                vv = frac(ct2['value'])
                if cf[3 * p + 2] == 1:
                    dlo = max(dlo, -vv)
                else:
                    dhi = min(dhi, vv)
            dstar = z0[3 * p + 2] - z0[3 * o + 2]
            dd = IV.point(dstar) + IV(dlo, dhi)
            ux = HALF[c['corner']][0] - HALF[rc['corner']][0]
            uy = HALF[c['corner']][1] - HALF[rc['corner']][1]
            cd, sd = cos_iv(dd), sin_iv(dd)
            rx = cd * ux - sd * uy
            ry = sd * ux + cd * uy
            nhx, nhy = NHAT[e]
            f = nhx * rx + nhy * ry
            lb = frac(val['lower_bound'])
            ck('%s relfloor lb %s' % (name, r['tag']), f.lo >= lb,
               'inf f=%g lb=%g' % (float(f.lo), float(lb)))
        else:
            ck('%s known mode' % name, False, mode)
        # numeric ledger
        qi = IV.point(q)
        j0, vs = row_jet(pbox, c, 1)
        vz = j0.v
        if mode in ('floor', 'relfloor'):
            vz = vz - IV.point(frac(val['lower_bound']))
        V0 = V0 + qi * vz
        for loc, gi in enumerate(vs):
            acc[gi] = acc.get(gi, IZERO) + qi * j0.g[loc]
        j2, vs2 = row_jet(rbox, c, 2)
        for a in range(len(vs2)):
            for b in range(len(vs2)):
                key = (vs2[a], vs2[b])
                t = qi * j2.h[a][b]
                accH[key] = t if key not in accH else accH[key] + t

    # branched pairs: every axis not listed alive must be killed on scope
    for b in cert.get('branched_pairs', []):
        pr = tuple(b['pair'])
        alive = {tuple(a) for a in b['alive_axes']}
        ck('%s branch axis in alive %s' % (name, pr),
           tuple(b['branch_axis']) in alive)
        for a in pair_axes(*pr):
            if a not in alive:
                ck('%s killed axis %s %s' % (name, pr, a),
                   axis_killed(sbox, *a))

    # [M] margin chain
    CV = sum((q * frac(c['value']) for q, c in zip(ocs, cuts)), Fraction(0))
    for q, c in zip(ocs, cuts):
        if q == 0:
            continue
        for k, cf in c['coeffs'].items():
            gi = int(k)
            acc[gi] = acc.get(gi, IZERO) + IV.point(q * cf)
    if is_anchor:
        acc[S_IDX] = acc.get(S_IDX, IZERO) - IONE
    eps_w = sum((v.mag() for v in acc.values()), Fraction(0))
    hsum = Fraction(0)
    for (a, b), v in accH.items():
        if a == b:
            hsum += max(Fraction(0), v.hi)
        else:
            hsum += v.mag()
    Hbar = hsum / 2
    cl = cert.get('claims', {})
    if is_anchor:
        margin = (-CV - V0.hi - eps_w * h_out - Hbar * h_out * h_out)
        ck('%s margin>0' % name, margin > 0, 'margin=%g' % float(margin))
        stats.note(cert, name, V0.hi, eps_w, Hbar, margin, cl)
    else:
        ck('%s no cuts loaded' % name, all(q == 0 for q in ocs))
        umax = V0.hi + eps_w * h_out + Hbar * h_out * h_out
        ck('%s leaf-empty sup<0' % name, umax < 0, 'sup=%g' % float(umax))
        stats.note(cert, name, V0.hi, eps_w, Hbar, None, cl)


class Stats(object):
    """informational only -- NEVER gates a decision."""
    def __init__(self):
        self.min_margin = None
        self.min_margin_cert = None
        self.max_rel = {}      # claim key -> (relative excess, cert)

    def note(self, cert, name, v0sup, eps_w, Hbar, margin, cl):
        if margin is not None:
            if self.min_margin is None or margin < self.min_margin:
                self.min_margin, self.min_margin_cert = margin, name
        for key, got in (('V0_sup', v0sup), ('eps_w', eps_w),
                         ('Hbar', Hbar), ('margin', margin)):
            if margin is None and key == 'margin':
                continue
            if key not in cl:
                continue
            want = frac(cl[key])
            if want == 0:
                continue
            rel = float(abs(got - want) / abs(want))
            cur = self.max_rel.get(key)
            if cur is None or rel > cur[0]:
                self.max_rel[key] = (rel, name)


def leaf_key(cert):
    ctx = tuple(sorted((tuple(b['pair']), tuple(b['branch_axis']))
                       for b in cert.get('branched_pairs', [])))
    tcuts = tuple(sorted(
        (c['label'], c['value']) for c in cert.get('cuts', [])
        if not c['label'].startswith('face:')))
    return ctx, tcuts


def check_coverage(certs, z0, ck, ringface):
    """[COV] the certificates of one (ring, face) form a covering tree."""
    leaves = [leaf_key(c) for c in certs]

    def rec(idx, fixed_pairs, fixed_cuts, depth):
        if depth > 12:
            return False
        if len(idx) == 1:
            ctx, tcuts = leaves[idx[0]]
            return (len(ctx) == len(fixed_pairs) and
                    len(tcuts) == len(fixed_cuts))
        # try a pair split: a pair present in every leaf (beyond fixed)
        cands = None
        for q in idx:
            prs = {pr for pr, ax in leaves[q][0] if pr not in fixed_pairs}
            cands = prs if cands is None else (cands & prs)
        for pr in sorted(cands or ()):
            groups = {}
            for q in idx:
                ax = dict(leaves[q][0])[pr]
                groups.setdefault(ax, []).append(q)
            # alive set of pr per the certificates must equal group keys
            alive = None
            for q in idx:
                for b in certs[q].get('branched_pairs', []):
                    if tuple(b['pair']) == pr:
                        al = {tuple(a) for a in b['alive_axes']}
                        alive = al if alive is None else (alive | al)
            if alive is None or set(groups) != alive:
                continue
            if all(rec(g, fixed_pairs | {pr}, fixed_cuts, depth + 1)
                   for g in groups.values()):
                return True
        # try a tie-cut split: a functional whose two sides partition idx
        labels = {}
        for q in idx:
            for lab, v in leaves[q][1]:
                if (lab, v) in fixed_cuts:
                    continue
                base = lab.rsplit(':', 1)[0]
                labels.setdefault((base, abs(frac(v))), set()).add((lab, v))
        for (base, tau), sides in labels.items():
            if len(sides) != 2:
                continue
            g1, g2 = [], []
            s1, s2 = sorted(sides)
            for q in idx:
                l1 = dict(leaves[q][1])
                if s1[0] in l1 and l1[s1[0]] == s1[1]:
                    g1.append(q)
                elif s2[0] in l1 and l1[s2[0]] == s2[1]:
                    g2.append(q)
                else:
                    g1 = None
                    break
            if not g1 or not g2:
                continue
            if rec(g1, fixed_pairs, fixed_cuts | {s1}, depth + 1) and \
                    rec(g2, fixed_pairs, fixed_cuts | {s2}, depth + 1):
                return True
        return False

    ck('COV %s tree covers' % ringface,
       rec(list(range(len(certs))), set(), set(), 0),
       '%d leaves' % len(certs))


# ------------------------------------------------------------------- corrupt
def apply_corrupt(cert, mode):
    if mode == 'omega-sign':
        for r in cert['rows']:
            if frac(r['omega']) > 0:
                r['omega'] = '-' + r['omega']
                break
    elif mode == 'h-big':
        h8 = frac(cert['h_out']) * 8
        cert['h_out'] = '%d/%d' % (h8.numerator, h8.denominator)
    elif mode == 'drop-anchor':
        for c in cert['cuts']:
            if c['label'].startswith('face:'):
                c['omega'] = '0'
    elif mode == 'floor-raise':
        for r in cert.get('rows', []):
            if r['validity'].get('mode') == 'floor':
                lb = frac(r['validity']['lower_bound']) + Fraction(1, 100)
                r['validity']['lower_bound'] = '%d/%d' % (lb.numerator,
                                                          lb.denominator)
                return True
        return False
    return True


def main():
    t0 = time.time()
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    report_path = None
    if '--corrupt' in args:
        q = args.index('--corrupt')
        corrupt = args[q + 1]
        del args[q:q + 2]
    if '--report' in args:
        q = args.index('--report')
        report_path = args[q + 1]
        del args[q:q + 2]
    cdir = args[0] if args else os.path.join(here, '..', '..',
                                             'A40-basin-surgery', 'results',
                                             'certs_a40')
    kpath = (args[1] if len(args) > 1 else
             os.path.join(here, '..', '..', 'A22-local-rigidity', 'results',
                          'krawczyk_cert.json'))
    if corrupt not in (None, 'omega-sign', 'h-big', 'drop-anchor',
                       'floor-raise', 'drop-sibling'):
        print('unknown corruption %s' % corrupt)
        return 1

    def log(s):
        sys.stdout.write(s + '\n')
        sys.stdout.flush()

    K = json.load(open(kpath))
    z0 = [frac(x) for x in K['z0']]
    rings = sorted(glob.glob(os.path.join(cdir, 'ring_*')))
    if not rings:
        print('no rings in %s' % cdir)
        return 1
    ck = Check(log)
    log('EXACT re-check of %s (PREC = %d, dyadic grid 2^-%d; no mpmath)'
        % (os.path.abspath(cdir), PREC, PREC))

    # ---- pass A: metadata only (chain, face census, corruption targeting).
    #      Reproduces the frozen checker's sorted(certs_by_rf) ordering.
    chain = []
    ring_faces = {}          # ring -> {label: [file, ...]} in file order
    tgt_anchor = None        # first anchor in sorted (ring, face) order
    tgt_floor = None         # first cert carrying a floor row
    tgt_sibling = None       # last cert of the first multi-cert face
    for rd in rings:
        rn = os.path.basename(rd)
        files = sorted(glob.glob(os.path.join(rd, '*.json')))
        ring_h = set()
        faces = {}
        anchors = {}
        floors = {}
        for fn in files:
            cert = json.load(open(fn))
            lab = cert['face']['label']
            faces.setdefault(lab, []).append(fn)
            anchors[fn] = (cert['type'] == 'A40-anchor')
            floors[fn] = any(r['validity'].get('mode') == 'floor'
                             for r in cert.get('rows', []))
            ring_h.add((cert['h_in'], cert['h_out']))
            del cert
        ck('CHAIN %s single (h_in,h_out)' % rn, len(ring_h) == 1, str(ring_h))
        chain.append(sorted(ring_h)[0])
        ring_faces[rn] = faces
        for lab in sorted(faces):
            fl = faces[lab]
            if tgt_sibling is None and len(fl) > 1:
                tgt_sibling = fl[-1]
            for fn in fl:
                if tgt_anchor is None and anchors[fn]:
                    tgt_anchor = fn
                if tgt_floor is None and floors[fn]:
                    tgt_floor = fn

    if corrupt:
        log('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
        if corrupt in ('omega-sign', 'h-big', 'drop-anchor'):
            if tgt_anchor is None:
                log('no anchor certificates; corruption not applicable')
                return 1
        elif corrupt == 'floor-raise' and tgt_floor is None:
            log('no floor rows found; corruption not applicable')
            return 1
        elif corrupt == 'drop-sibling' and tgt_sibling is None:
            log('no branched faces found; corruption not applicable')
            return 1

    # ---- chain tiling
    ck('CHAIN starts at A36 h0', frac(chain[0][0]) == H0, chain[0][0])
    for a, b in zip(chain, chain[1:]):
        ck('CHAIN contiguous', frac(a[1]) == frac(b[0]),
           '%s -> %s' % (a[1], b[0]))
    want = {'sq%d.%s%s' % (q, ax, sg)
            for q in range(11) for ax in 'xyt' for sg in '+-'} | {'s-'}
    for rd in rings:
        rn = os.path.basename(rd)
        have = set(ring_faces[rn])
        ck('CHAIN faces complete %s' % rn, want <= have,
           str(sorted(want - have))[:200])

    # ---- pass B: per-cert numerics + per-face coverage, one ring at a time
    stats = Stats()
    nc = 0
    for rd in rings:
        rn = os.path.basename(rd)
        _JET.clear()
        _TD.clear()
        _KILL.clear()
        for lab in sorted(ring_faces[rn]):
            cs = []
            for fn in ring_faces[rn][lab]:
                if corrupt == 'drop-sibling' and fn == tgt_sibling:
                    continue
                cert = json.load(open(fn))
                cert['_file'] = fn
                if corrupt in ('omega-sign', 'h-big', 'drop-anchor') \
                        and fn == tgt_anchor:
                    apply_corrupt(cert, corrupt)
                if corrupt == 'floor-raise' and fn == tgt_floor:
                    apply_corrupt(cert, corrupt)
                cs.append(cert)
            for cert in cs:
                check_cert(cert, z0, K, ck, stats)
                nc += 1
            if len(cs) > 1 or cs[0].get('branched_pairs') or \
                    any(not c['label'].startswith('face:')
                        for c in cs[0].get('cuts', [])):
                check_coverage(cs, z0, ck, '%s/%s' % (rn, lab))
            del cs
        log('  ring %s done (%d certs, %d checks, %d failures, %.1f s)'
            % (rn, nc, ck.n, len(ck.fails), time.time() - t0))

    wall = time.time() - t0
    log('checked %d certificates, %d checks, %d failures'
        % (nc, ck.n, len(ck.fails)))
    if stats.min_margin is not None:
        log('  min anchor margin (EXACT) = %.6e  [%s]'
            % (float(stats.min_margin), stats.min_margin_cert))
    for key in ('V0_sup', 'eps_w', 'Hbar', 'margin'):
        if key in stats.max_rel:
            rel, nm = stats.max_rel[key]
            log('  max |exact-claimed|/|claimed| for %-7s = %.3e  [%s]'
                % (key, rel, nm))
    verdict = None
    rc = 0
    if corrupt:
        ok = len(ck.fails) > 0
        verdict = ('corruption %s: checker %s => %s'
                   % (corrupt, 'FAILED as required' if ok else 'passed (BAD)',
                      'PASS' if ok else 'FAIL'))
        log(verdict)
        rc = 0 if ok else 1
    else:
        rc = 0 if not ck.fails else 1
        verdict = 'ALL CHECKS PASS' if not ck.fails else 'FAILURES'
        log('=> %s' % verdict)
    log('wall %.1f s' % wall)
    if report_path:
        rep = {
            'n_certs': nc,
            'n_checks': ck.n,
            'n_failures': len(ck.fails),
            'failure_lines': ck.lines[:200],
            'exact': True,
            'PREC': PREC,
            'wall_seconds': round(wall, 1),
            'verdict': verdict,
        }
        if stats.min_margin is not None:
            rep['min_anchor_margin_exact'] = float(stats.min_margin)
            rep['min_anchor_margin_cert'] = stats.min_margin_cert
            rep['max_rel_dev_vs_claims'] = {
                k: {'rel': v[0], 'cert': v[1]}
                for k, v in stats.max_rel.items()}
        with open(report_path, 'w') as fh:
            json.dump(rep, fh, indent=2)
    return rc


if __name__ == '__main__':
    sys.exit(main())
