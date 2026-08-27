#!/usr/bin/env python
"""a36_check.py -- STANDALONE re-checker for results/a36_certs/*.json.

recheck.py / m2b_check.py style.  Uses ONLY  mpmath.iv + fractions + json +
math + glob + os + sys.  It imports NO producer library: not a36_lib, not
strata_lib, not m2_lib, not t3lib, not a22lib, not numpy, not scipy.  The
order-2 interval jets and the row language below are transcribed (with
attribution) from A35's own standalone re-checker
`attempts/A35-escape-complex/code/m2_check_inflation.py`.

The checker does NOT trust the producer's row list.  It REBUILDS all 70
extended v3 rows from

  * A22's krawczyk_cert.json constraints 0..35 (verbatim), and
  * the BASIS v3 axis table transcribed below from A36's documented spec, and
  * A22's constraints 36, 37 verbatim as the two auxiliary dist rows,

and it rebuilds the pin set P from A22's own `S` and the preconditioner Y from
A22's own `Y`.  A disagreement between the producer's row set / pin set and the
documented spec therefore shows up as a failure.

------------------------------------------------------------------ THE CHAIN
Verified, at the certificate's radius h, over box(z-hat, h):

 [S] P equals A22's S mapped into v3 positions (36->44, 37->45).
 [N] the two NEW v3 rows B13x' (42), B13y' (43) vanish at z-hat within 1e-59;
     every row carrying omega != 0 is ACTIVE at z-hat (|g| <= 1e-40).
 [A] the two aux rows 44, 45 are active at z-hat.
 [O] sign discipline: omega_r >= 0 on R_V, omega_r = 0 outside R_V, and
     omega_r > 0 on every pin row.  R_V is RECOMPUTED by the checker from the
     certificate's declared variant using the checker's own axis table.
     Non-vacuity: for a per-variant certificate, every one of the three
     branch axes must carry omega > 0 on at least one of its corner rows.
 [Z] eps_0 = sum_r |omega_r| |g_r(z-hat)|, g_max = max_{r in P} |g_r(z-hat)|.
 [G] eps_w = || A(z-hat)^T omega - e_s ||_1.
 [H] Hbar = (1/2) sum_ij sup_box |d^2 W/dz_i dz_j|,  W = sum_r omega_r g_r.
 [K] beta = sup_box ||I - Y A_P||_inf < 1,  kappa = ||Y||_inf.
 [E] kappa_eff = max_{r in P} (max_i |Y_ir|)/omega_r.
 [P] psi(h) = (kappa_eff E(h) + kappa g_max)/(1-beta) < h  with
     E(x) = eps_0 + eps_w x + Hbar x^2, and the least fixed point of
     x -> kappa_eff E(x)/(1-beta) + kappa g_max/(1-beta)  is <= r_N.
 [V] A22 rows 0..35 SAT-selection validity on box(h): tangential margin > 0
     and depth + 1/2 > 0.
 [L] L1 (levers.md L1.2/L1.4): each of the 16 axis/side combinations declared
     IMPOSSIBLE is refuted on box(h) by exhibiting a corner k of that axis with
     sup_box g_{e,k} < 0 (the true axis gap is min_k g_{e,k}, so one negative
     corner kills the axis).  With separating-axis completeness this leaves
     exactly the 8 branch axes, hence the disjunction that the 16 variants
     cover every feasible z in box(h).

Corruption controls (each MUST make the checker fail):
    omega-sign, h-big, drop-aux, drop-branch, wrong-branch
Usage:
    python a36_check.py [certdir] [krawczyk_cert.json]
                        [--corrupt {omega-sign,h-big,drop-aux,drop-branch,
                                    wrong-branch}]
Exit 0 = all PASS (or, under --corrupt, the checker failed as required).
"""
import glob
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

iv.dps = 60

NV = 34
S_IDX = 33
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]      # outward normal of edge k

# ------------------------------------------------- BASIS v3 spec (transcribed)
# (name, owner o, owner edge e, other square p, canonical corner, base position)
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
NEW_V3_POS = (42, 43)                 # the two rows A36 adds to basis v2
# the 16 axis/side combinations L1.2 declares impossible  (pair, o, e, p)
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
    """The 70 v3 constraint dicts, rebuilt from A22's cert + the axis table."""
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


# --------------------------------------------------------------- numerics
def frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def cnum(x):
    if isinstance(x, Fraction):
        return iv.mpf(x.numerator) / iv.mpf(x.denominator)
    return iv.mpf(x)


def mag(x):
    x = iv.mpf(x)
    return max(math.nextafter(abs(float(x.a)), math.inf),
               math.nextafter(abs(float(x.b)), math.inf))


def sup(x):
    return math.nextafter(float(iv.mpf(x).b), math.inf)


def inf(x):
    return -math.nextafter(float((-iv.mpf(x)).b), math.inf)


def sum_up(xs):
    return sum(xs) * (1.0 + 1e-12) + 1e-300


# ---- order-2 forward jets (transcribed from m2_check_inflation.py, A35)
class J(object):
    __slots__ = ('v', 'g', 'h', 'd', 'o')

    def __init__(self, v, g, h, d, o):
        self.v, self.g, self.h, self.d, self.o = v, g, h, d, o

    @staticmethod
    def var(val, k, d, o):
        g = None
        if o >= 1:
            g = [iv.mpf(0)] * d
            g[k] = iv.mpf(1)
        return J(val, g, [[iv.mpf(0)] * d for _ in range(d)] if o >= 2
                 else None, d, o)

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
        c, s = iv.cos(self.v), iv.sin(self.v)
        return self._ch(c, -s, -c)

    def sin(self):
        c, s = iv.cos(self.v), iv.sin(self.v)
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


def sep_value(box, o, e, p, k):
    return row_jet(box, {'kind': 'edge', 'i': p, 'corner': k, 'j': o,
                         'edge': e}, 0)[0].v


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
    hf = float(h)
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

    pbox = [cnum(x) for x in z0]
    box = box_of(z0, h)
    gz = [mag(row_jet(pbox, cons[k], 0)[0].v) for k in range(NEXT3)]

    # [N] the two NEW v3 rows vanish at z-hat; loaded rows are active
    ck('N %s new v3 rows B13x\',B13y\' zero at z-hat (<1e-59)' % tag,
       max(gz[k] for k in NEW_V3_POS) < 1e-59,
       'max |g| = %.3e' % max(gz[k] for k in NEW_V3_POS))
    ck('N %s every loaded row is active at z-hat (<1e-40)' % tag,
       all(gz[k] < 1e-40 for k in range(NEXT3) if om[k] != 0),
       'max = %.3e' % max([gz[k] for k in range(NEXT3) if om[k] != 0]))
    # [A] aux rows active
    ck('A %s aux rows active at z-hat' % tag,
       max(gz[p] for p in AUX_POS) < 1e-40)

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
    e0 = sum_up([abs(float(om[k])) * gz[k] for k in range(NEXT3)
                 if om[k] != 0])
    gmax = max(gz[k] for k in P)
    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300,
       'recomputed %.3e vs claimed %.3e' % (e0, cl['eps_0']))
    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300,
       'recomputed %.3e vs claimed %.3e' % (gmax, cl['g_max']))

    # [G] eps_w
    acc = [iv.mpf(0)] * NV
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = row_jet(pbox, cons[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + ok_ * j.g[loc]
    ew = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
                 for gi in range(NV)])
    ck('G %s eps_w' % tag, ew <= cl['eps_w'] * 1.0000001 + 1e-300,
       'recomputed %.3e vs claimed %.3e' % (ew, cl['eps_w']))

    # [H] Hbar
    Hd = {}
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        ok_ = cnum(om[k])
        j, vs = row_jet(box, cons[k], 2)
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                t = ok_ * j.h[a][b]
                Hd[key] = t if key not in Hd else Hd[key] + t
    Hbar = sum_up([mag(x) for x in Hd.values()]) / 2.0
    ck('H %s Hbar' % tag, Hbar <= cl['Hbar'] * 1.0000001,
       'recomputed %.6f vs claimed %.6f' % (Hbar, cl['Hbar']))

    # [K] beta, kappa
    grads = []
    for k in P:
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
            rs.append(mag((iv.mpf(1) if i == j2 else iv.mpf(0)) - ssum))
        beta = max(beta, sum_up(rs))
    kappa = max(sum_up([abs(float(Y[i][r])) for r in range(NV)])
                for i in range(NV))
    ck('K %s beta < 1' % tag, beta < 1.0 and beta <= cl['beta'] * 1.0000001,
       'recomputed %.8f vs claimed %.8f' % (beta, cl['beta']))
    ck('K %s kappa' % tag, kappa <= cl['kappa'] * 1.0000001,
       'recomputed %.6f' % kappa)

    # [E] kappa_eff
    cvec = [max(abs(float(Y[i][r])) for i in range(NV)) for r in range(NV)]
    keff = (float('inf') if any(om[P[i]] <= 0 for i in range(NV)) else
            max(cvec[i] / float(om[P[i]]) for i in range(NV)))
    ck('E %s kappa_eff' % tag, keff <= cl['kappa_eff'] * 1.0000001,
       'recomputed %.6f vs claimed %.6f' % (keff, cl['kappa_eff']))

    # [P] dichotomy + iterated pinning
    E = e0 + ew * hf + Hbar * hf * hf
    psi = ((keff * E + kappa * gmax) / (1.0 - beta)
           if (beta < 1 and keff < float("inf")) else float("inf"))
    ck('P %s contraction psi(h) < h' % tag, psi < hf,
       'psi = %.6e vs h = %.6e (ratio %.4f)' % (psi, hf, psi / hf))
    x = hf
    if beta < 1.0:
        C = keff / (1.0 - beta)
        for _ in range(800):
            x = C * (e0 + ew * x + Hbar * x * x) + kappa * gmax / (1.0 - beta)
    ck('P %s fixed point x* <= r_N' % tag, x <= float(rN),
       'x* = %.4e vs r_N = %.4e' % (x, float(rN)))

    # [V] A22 rows 0..35 SAT-selection validity on box(h)
    wt, wd = 1e9, 1e9
    for c in cons[:36]:
        if c['kind'] != 'edge':
            continue
        i, j2 = c['i'], c['j']
        hx, hy = cnum(HALF[c['corner']][0]), cnum(HALF[c['corner']][1])
        ci, si = iv.cos(box[3 * i + 2]), iv.sin(box[3 * i + 2])
        qx = box[3 * i] + (ci * hx - si * hy)
        qy = box[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = iv.cos(box[3 * j2 + 2]), iv.sin(box[3 * j2 + 2])
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        wx, wy = qx - box[3 * j2], qy - box[3 * j2 + 1]
        wt = min(wt, 0.5 - mag(-ny * wx + nx * wy))
        wd = min(wd, 0.5 + inf(nx * wx + ny * wy))
    ck('V %s A22 rows 0..35 SAT selection valid on box(h)' % tag,
       wt > 0 and wd > 0,
       'tangential %.6f, depth+1/2 %.6f' % (wt, wd))

    # [L] L1: the 16 impossible axes are refuted on box(h)
    kmin = 1e9
    for lab, o, e, p in KILLED_AXES:
        best = max(-sup(sep_value(box, o, e, p, k)) for k in range(4))
        kmin = min(kmin, best)
    ck('L %s L1 killed axes refuted on box(h)' % tag, kmin > 0,
       'min kill margin %.6f' % kmin)

    if verbose:
        print('  [ok] %-26s h=%-12s beta=%.5f Hbar=%.3f keff=%.3f psi/h=%.4f'
              ' x*=%.2e' % (tag, cert['h'], beta, Hbar, keff, psi / hf, x))
    _mn = min(float(om[k]) for k in P)
    return dict(h=hf, beta=beta, Hbar=Hbar, keff=keff, psi_over_h=psi / hf,
                x_star=x, tan=wt, kill=kmin, universal=universal,
                psi_A35=(kappa * (E / _mn + gmax) /
                (1 - beta) / hf) if _mn > 0 else float("inf"))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in args:
        i = args.index('--corrupt')
        corrupt = args[i + 1]
        del args[i:i + 2]
    cdir = args[0] if args else os.path.join(here, '..', 'results',
                                             'a36_certs')
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
    print('re-checking %d certificates in %s'
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
              'max x* = %.2e' % (len(Vv), max(r['h'] for r in Vv),
                                 max(r['psi_over_h'] for r in Vv),
                                 max(r['x_star'] for r in Vv)))
    if U:
        print("  (V') branch-free UNIVERSAL: h = %.6g, psi/h = %.4f, x* = %.2e"
              % (U[0]['h'], U[0]['psi_over_h'], U[0]['x_star']))
    print('  min A22 tangential margin 0..35 = %.6f (must be > 0)'
          % min(r['tan'] for r in rows))
    print('  min L1 kill margin              = %.6f (must be > 0)'
          % min(r['kill'] for r in rows))
    print('  A35 (alpha-form) psi/h would be  = %.3f  (>1 => the max-form is '
          'what makes these radii possible)' % max(r['psi_A35'] for r in rows))
    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))[:8]))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
