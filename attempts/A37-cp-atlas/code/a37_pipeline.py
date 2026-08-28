#!/usr/bin/env python
"""a37_pipeline.py -- A37 CP atlas: family-generic audit -> classify -> 3R/3S
-> certificate emitter.  Implements notes/cookbook.md steps 1,2,3R,3S,5.

Read-only inputs
  attempts/A04-upper-search/families_catalogue.json     (best_x per family)

Machinery: the row language and the order-2 interval jets are A30 t3lib /
A35 strata_lib / A36 a36_lib semantics, transcribed here so that the module is
self-contained (A35/A36 hard-wire the Trump point z-hat through the A22
certificate, so they cannot be called family-generically).

VARIABLE LAYOUT
  A04 best_x   : centres INTERLEAVED  c_i = (x[2i], x[2i+1]), i = 0..10
                 thetas BLOCKED       th_i = x[22+i]
                 s = x[33]
  A22/t3lib z  : z[3i] = cx_i, z[3i+1] = cy_i, z[3i+2] = th_i, z[33] = s
  load_family() converts A04 -> A22 order.

ROW LANGUAGE (A22 constraint dicts, all written g >= 0)
  {'kind':'wall','i':sq,'corner':k,'wall':'x=0'|'y=0'|'x=s'|'y=s'}
      -> corner coordinate >= 0, or s - coordinate >= 0.  GLOBALLY VALID.
  {'kind':'edge','i':p,'corner':k,'j':o,'edge':e}
      -> n_e(th_o) . (q_k(p) - c_o) - 1/2 >= 0.  Valid on a box only under the
         [V] test below.
  {'kind':'dist','i':a,'j':b}
      -> |c_a - c_b|^2 - 1 >= 0.  GLOBALLY VALID (disjoint incircles of radius
         1/2), for EVERY pair, not just flush ones.

[V] BOX-VALIDITY OF A SEP ROW  (the only non-global validity used anywhere)
  In the owner frame write the corner q = q_k(p) as (t, d),
      t = tperp_e(th_o).(q - c_o),   d = n_e(th_o).(q - c_o),   g = d - 1/2.
  If over the whole box   sup|t| < 1/2   and   inf d > -1/2,
  then for every INTERIOR-DISJOINT configuration in the box we must have
  |d| >= 1/2 (else q would be in the open square o, and q is a corner of p),
  hence d >= 1/2, hence g >= 0.  Uses ONLY pairwise interior-disjointness --
  no SAT selection, no dominance rows, no branch enumeration, no stratum.
  Rows failing [V] (endpoint ties, corner-corner) get omega = 0 (cookbook
  step 1, "dropping is FINE").

Rigour tags: [IV] mpmath.iv dps 60 (rigorous); [RFP] rigorous float64;
[LP]/[NUM] float64 design heuristics whose output is re-verified in [IV].
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.linalg import qr
from scipy.optimize import linprog

iv.dps = 60
mp.dps = 60

HERE = os.path.dirname(os.path.abspath(__file__))
A37 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A37, '..'))
RESULTS = os.path.join(A37, 'results')
CERTDIR = os.path.join(RESULTS, 'certs')
CATALOGUE = os.path.join(ATT, 'A04-upper-search', 'families_catalogue.json')

NV = 34
NSQ = 11
S_IDX = 33
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]        # outward normal of edge e
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')

TOL_C = 1e-7            # contact tolerance (cookbook step 1)
TOL_TIE = 1e-7          # dominance / axis tie tolerance
VAR_CAP = 256           # cookbook amendment A7: refuse beyond 256 variants


# ----------------------------------------------------------------- numerics
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


def fs(x):
    return '%d/%d' % (x.numerator, x.denominator)


def sfrac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


# ----------------------------------------------------- order-2 interval jets
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
            vs.append(S_IDX)
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


def point_box(z0):
    return [cnum(x) for x in z0]


# ----------------------------------------------------------- geometry helpers
def corner_iv(box, i, k):
    hx, hy = cnum(HALF[k][0]), cnum(HALF[k][1])
    th = box[3 * i + 2]
    c, s = iv.cos(th), iv.sin(th)
    return (box[3 * i] + (c * hx - s * hy),
            box[3 * i + 1] + (s * hx + c * hy))


def normal_iv(box, o, e):
    nhx, nhy = NHAT[e]
    c, s = iv.cos(box[3 * o + 2]), iv.sin(box[3 * o + 2])
    return (c * iv.mpf(nhx) - s * iv.mpf(nhy),
            s * iv.mpf(nhx) + c * iv.mpf(nhy))


def sep_td(box, con):
    """[IV] (t, d) of a sep row: tangential and normal coordinate of corner
    q_{corner}(i) in the frame of edge `edge` of square `j`."""
    i, j, k, e = con['i'], con['j'], con['corner'], con['edge']
    qx, qy = corner_iv(box, i, k)
    nx, ny = normal_iv(box, j, e)
    wx, wy = qx - box[3 * j], qy - box[3 * j + 1]
    t = -ny * wx + nx * wy
    d = nx * wx + ny * wy
    return t, d


def v_margins(box, con):
    """[IV] ([V]-test margins) (wt, wd): wt = 1/2 - sup|t|, wd = 1/2 + inf d."""
    t, d = sep_td(box, con)
    return 0.5 - mag(t), 0.5 + inf(d)


# --------------------------------------------------------------- family load
_CAT = None


def catalogue():
    global _CAT
    if _CAT is None:
        with open(CATALOGUE) as f:
            _CAT = json.load(f)
    return _CAT


def filtered_families(cut=3.95):
    F = catalogue()['families']
    sub = [(i, f) for i, f in enumerate(F) if f['s_min'] < cut]
    sub.sort(key=lambda t: t[1]['s_min'])
    return sub


def load_family(fidx):
    """fidx = index in the <3.95 s_min-sorted order (cookbook numbering).

    Lead patch: fidx >= 1000 loads drain-discovered family A37-NEW-(fidx-1000)
    from results/drain.json (z already in A22-interleaved order, verified)."""
    if fidx >= 1000:
        with open(os.path.join(RESULTS, 'drain.json')) as f:
            nf = json.load(f)['new_families'][fidx - 1000]
        z = [Fraction(v) for v in nf['z']]
        assert len(z) == NV
        nc = nf['n_contacts']
        npair, nwall = int(nc['pairs']), int(nc['walls'])
        fam = {'s_min': nf['s'], 'n_pair_contacts': npair,
               'n_wall_contacts': nwall,
               'tilt_pattern_deg': nf['tilt_signature_deg'],
               'count': len(nf['members']), 'drain_id': nf['id']}
        return z, fam, -1
    sub = filtered_families()
    cat_idx, fam = sub[fidx]
    x = fam['best_x']
    z = []
    for i in range(NSQ):
        z += [Fraction(x[2 * i]), Fraction(x[2 * i + 1]), Fraction(x[22 + i])]
    z.append(Fraction(x[33]))
    assert len(z) == NV
    return z, fam, cat_idx


# ================================================================== STEP 1
def audit(z0, tol=TOL_C):
    """Cookbook step 1.  Full gap spectrum + contact classification."""
    pb = point_box(z0)
    out = {'tol': tol, 'walls': [], 'pairs': [], 'wall_spectrum': [],
           'pair_spectrum': [], 'surprises': []}

    # --- 176 corner-wall clearances
    for i in range(NSQ):
        for k in range(4):
            for w in WALLS:
                con = {'kind': 'wall', 'i': i, 'corner': k, 'wall': w}
                v = row_jet(pb, con, 0)[0].v
                g = (inf(v) + sup(v)) / 2.0
                out['wall_spectrum'].append(g)
                if abs(g) <= tol:
                    out['walls'].append({'i': i, 'corner': k, 'wall': w,
                                         'g': g})
                if sup(v) < -1e-9:
                    out['surprises'].append(
                        'containment VIOLATED %d/%d/%s g=%.3e' % (i, k, w, g))

    # --- 55 pair SAT gaps, per-axis
    for i in range(NSQ):
        for j in range(i + 1, NSQ):
            axes = []
            for o, p in ((i, j), (j, i)):
                for e in range(4):
                    nx, ny = normal_iv(pb, o, e)
                    proj = []
                    for k in range(4):
                        qx, qy = corner_iv(pb, p, k)
                        v = (nx * (qx - pb[3 * o]) + ny * (qy - pb[3 * o + 1])
                             - cnum(Fraction(1, 2)))
                        proj.append((inf(v) + sup(v)) / 2.0)
                    axes.append({'o': o, 'p': p, 'e': e, 'proj': proj,
                                 'gap': min(proj)})
            best = max(a['gap'] for a in axes)
            out['pair_spectrum'].append(best)
            if best > tol:
                continue
            rec = classify_contact(pb, i, j, axes, best, tol)
            out['pairs'].append(rec)
            for s in rec.get('surprises', []):
                out['surprises'].append('pair (%d,%d): %s' % (i, j, s))

    # --- centre-distance-1 pairs (aux rows are active there)
    out['aux'] = []
    for i in range(NSQ):
        for j in range(i + 1, NSQ):
            con = {'kind': 'dist', 'i': i, 'j': j}
            v = row_jet(pb, con, 0)[0].v
            g = (inf(v) + sup(v)) / 2.0
            if abs(g) <= tol:
                out['aux'].append({'i': i, 'j': j, 'g': g})

    # --- gap-spectrum hygiene: anything in (tol, 100*tol] means tol_c is
    # cutting through a cluster and the contact set is tolerance-dependent.
    near_w = [g for g in out['wall_spectrum'] if tol < abs(g) <= 100 * tol]
    near_p = [g for g in out['pair_spectrum'] if tol < g <= 100 * tol]
    if near_w:
        out['surprises'].append(
            'gap spectrum: %d wall clearances in (tol, 100 tol]: %s'
            % (len(near_w), ['%.2e' % v for v in sorted(near_w)[:4]]))
    if near_p:
        out['surprises'].append(
            'gap spectrum: %d pair gaps in (tol, 100 tol]: %s'
            % (len(near_p), ['%.2e' % v for v in sorted(near_p)[:4]]))
    inside = [g for g in out['pair_spectrum'] if g <= tol]
    if inside and max(inside) > 1e-8:
        out['surprises'].append(
            'gap spectrum: largest ACCEPTED pair gap is %.2e (A04 point is '
            'only ~1e-8 converged on that contact)' % max(inside))
    return out


T_INSIDE = 1e-6          # |t| must be <= 1/2 - T_INSIDE for a [V]-safe row


def classify_contact(pb, i, j, axes, best, tol):
    """Classify one contact pair and enumerate its candidate sep rows.

    Rows are taken from EVERY tied separating axis (an axis whose gap is 0
    within tol) and EVERY corner of the other square that is active on that
    axis.  By the L1.1 over-estimate principle any corner row of a separating
    axis is >= 0; box-validity of a particular row is then decided by the [V]
    test, which needs |t| < 1/2 -- so the safe flag is set from the tangential
    coordinate, NOT from dominance.
    """
    tied = [a for a in axes if a['gap'] >= best - tol]
    a = max(axes, key=lambda a: a['gap'])
    o, p, e = a['o'], a['p'], a['e']
    mn = min(a['proj'])
    dom = [k for k in range(4) if a['proj'][k] <= mn + TOL_TIE]
    rec = {'i': i, 'j': j, 'gap': best, 'owner': o, 'other': p, 'edge': e,
           'proj': a['proj'], 'n_dom': len(dom), 'dom': dom,
           'n_axes_tied': len(tied),
           'tied_axes': [(x['o'], x['e'], x['gap']) for x in tied],
           'surprises': [], 'rowspecs': [], 'endpoint': False,
           'corner_corner': False}
    tvals, specs = [], []
    for ax in tied:
        for k in range(4):
            if abs(ax['proj'][k]) > tol:
                continue                      # not active on this axis
            con = {'kind': 'edge', 'i': ax['p'], 'corner': k, 'j': ax['o'],
                   'edge': ax['e']}
            t, d = sep_td(pb, con)
            tv = (inf(t) + sup(t)) / 2.0
            sf = abs(tv) <= 0.5 - T_INSIDE
            specs.append({'owner': ax['o'], 'other': ax['p'], 'edge': ax['e'],
                          'corner': k, 't': tv, 'safe': bool(sf),
                          'g': ax['proj'][k]})
            if ax is a:
                tvals.append(tv)
            if abs(abs(tv) - 0.5) <= 1e-6:
                rec['endpoint'] = True
    rec['rowspecs'] = specs
    rec['t'] = tvals
    rec['n_safe_rows'] = sum(1 for s in specs if s['safe'])
    # corner-corner: an active corner of p coincides with a corner of o
    cc = []
    for k in dom:
        qx, qy = corner_iv(pb, p, k)
        for m in range(4):
            rx, ry = corner_iv(pb, o, m)
            dd = math.hypot((inf(qx) + sup(qx)) / 2 - (inf(rx) + sup(rx)) / 2,
                            (inf(qy) + sup(qy)) / 2 - (inf(ry) + sup(ry)) / 2)
            if dd <= 1e-6:
                cc.append([k, m, dd])
    if cc:
        rec['corner_corner'] = True
        rec['cc'] = cc
    if rec['corner_corner']:
        rec['class'] = 'CORNER-CORNER'
    elif len(dom) >= 2:
        rec['class'] = 'FLUSH'
    elif rec['endpoint']:
        rec['class'] = 'ENDPOINT'
    else:
        rec['class'] = 'POINT'
    if rec['class'] in ('CORNER-CORNER', 'ENDPOINT'):
        rec['surprises'].append('%s (t = %s, %d tied axes, %d [V]-safe rows)'
                                % (rec['class'], ['%.6f' % v for v in tvals],
                                   len(tied), rec['n_safe_rows']))
    if rec['class'] == 'FLUSH' and rec['n_safe_rows'] < len(tied):
        rec['surprises'].append(
            'FLUSH with only %d [V]-safe rows over %d tied axes (a flush '
            'corner projects outside the owner edge: t = %s)'
            % (rec['n_safe_rows'], len(tied), ['%.4f' % v for v in tvals]))
    if len(tied) > 2:
        rec['surprises'].append('%d tied separating axes' % len(tied))
    if len(dom) > 2:
        rec['surprises'].append('%d dominant corners (degenerate)' % len(dom))
    if rec['n_safe_rows'] == 0:
        rec['surprises'].append('NO [V]-safe row for this contact -> omega = 0')
    return rec


def build_rows(aud):
    """The full row list + safety flags.  Cookbook step 1 output."""
    rows, meta = [], []
    for w in aud['walls']:
        rows.append({'kind': 'wall', 'i': w['i'], 'corner': w['corner'],
                     'wall': w['wall']})
        meta.append({'src': 'wall', 'safe': True, 'why': 'global'})
    for rec in aud['pairs']:
        for s in rec['rowspecs']:
            rows.append({'kind': 'edge', 'i': s['other'], 'corner': s['corner'],
                         'j': s['owner'], 'edge': s['edge']})
            meta.append({'src': 'pair', 'pair': (rec['i'], rec['j']),
                         'class': rec['class'], 'safe': bool(s['safe']),
                         't': s['t'],
                         'why': 'V-test' if s['safe'] else '|t| >= 1/2'})
    for a in aud['aux']:
        rows.append({'kind': 'dist', 'i': a['i'], 'j': a['j']})
        meta.append({'src': 'aux', 'safe': True, 'why': 'global (incircles)'})
    return rows, meta


# ================================================================== STEP 2
def jac_at(z, rows, order=1):
    """[IV] (mid, rad) float64 of the len(rows) x 34 Jacobian at point z."""
    pb = point_box(z) if not isinstance(z[0], iv.mpf) else z
    n = len(rows)
    mid = np.zeros((n, NV))
    rad = np.zeros((n, NV))
    for k, c in enumerate(rows):
        j, vs = row_jet(pb, c, 1)
        for loc, gi in enumerate(vs):
            a, b = float(j.g[loc].a), float(j.g[loc].b)
            mid[k, gi] = (a + b) / 2.0
            rad[k, gi] = max(b - (a + b) / 2.0, (a + b) / 2.0 - a) + 5e-324
    return mid, rad


def certify_nonsingular(Amid, Arad):
    """[RFP] Rump-style rigorous float64 nonsingularity of [Amid +- Arad]."""
    n = Amid.shape[0]
    try:
        Y = np.linalg.inv(Amid)
    except np.linalg.LinAlgError:
        return False, float('inf')
    if not np.all(np.isfinite(Y)):
        return False, float('inf')
    E = np.eye(n) - Y @ Amid
    eps = float(np.finfo(float).eps) / 2.0
    gamma = (n + 2) * eps / (1.0 - (n + 2) * eps)
    aY = np.abs(Y)
    err = gamma * (aY @ np.abs(Amid)) + aY @ Arad
    return bool(np.max(np.sum(np.abs(E) + err, axis=1)) < 1.0), \
        float(np.max(np.sum(np.abs(E) + err, axis=1)))


def classify(z0, rows, meta):
    """Cookbook step 2: RIGID / RATTLER-CORE / VALLEY."""
    mid, rad = jac_at(z0, rows)
    sv = np.linalg.svd(mid, compute_uv=False)
    rank = int((sv > 1e-9).sum())
    gap = (float(sv[rank - 1]) if rank else float('inf'),
           float(sv[rank]) if rank < len(sv) else 0.0)
    # loaded coordinates
    touched = set()
    for k, c in enumerate(rows):
        for gi in row_vars(c):
            if abs(mid[k, gi]) > 1e-12:
                touched.add(gi)
    free_sq = [i for i in range(NSQ)
               if not ({3 * i, 3 * i + 1, 3 * i + 2} & touched)]
    under = []
    for i in range(NSQ):
        cnt = sum(1 for c in rows if i in (c.get('i'), c.get('j')))
        if cnt < 3:
            under.append((i, cnt))
    out = {'rank': rank, 'n_rows': len(rows), 'sv_min_kept': gap[0],
           'sv_max_dropped': gap[1], 'rattler_squares': free_sq,
           'under_contacted': under, 'sv': [float(x) for x in sv]}
    out['n_loaded_coords'] = len(touched)
    if rank == NV:
        piv = qr(mid.T, pivoting=True, mode='economic')[2]
        basis = sorted(int(p) for p in piv[:NV])
        ok, bnd = certify_nonsingular(mid[basis], rad[basis])
        out['minor'] = basis
        out['rfp_ok'] = ok
        out['rfp_bound'] = bnd
        out['class'] = 'RIGID' if ok else 'VALLEY'
        if not ok:
            out['note'] = ('[RFP] failed on the QR-selected minor '
                           '(bound %.3e)' % bnd)
    elif free_sq and rank == len(touched):
        # the loaded core is rigid; the free squares are rattlers
        sub = mid[:, sorted(touched)]
        piv = qr(sub.T, pivoting=True, mode='economic')[2]
        basis = sorted(int(p) for p in piv[:rank])
        ok, bnd = certify_nonsingular(sub[basis], rad[:, sorted(touched)][basis])
        out['minor'] = basis
        out['core_coords'] = sorted(touched)
        out['rfp_ok'] = ok
        out['rfp_bound'] = bnd
        out['class'] = 'RATTLER-CORE' if ok else 'VALLEY'
    else:
        out['class'] = 'VALLEY'
    return out


# --------------------------------------------------------------- multiplier LP
def omega_lp(mid, safe, mode='feas', pin=None, cvec=None, w=None, hh=0.0,
             cap=1e4):
    """[LP] omega >= 0 supported on `safe` rows with A^T omega = e_s.

    mode 'feas'    : any feasible omega, min sum omega.
    mode 'maxform' : maximise t - hh*(1/2) sum_r w_r omega_r  s.t.
                     omega_r >= c_r t for r in pin  (=> kappa_eff <= 1/t).
    """
    n = mid.shape[0]
    es = np.zeros(NV)
    es[S_IDX] = 1.0
    if mode == 'feas':
        Aeq = mid.T.copy()
        c = np.ones(n)
        bounds = [((0.0, cap) if safe[k] else (0.0, 0.0)) for k in range(n)]
        r = linprog(c, A_eq=Aeq, b_eq=es, bounds=bounds, method='highs')
        if not r.success:
            return None
        return np.array(r.x)
    # max-form
    nv = n + 1
    Aeq = np.zeros((NV, nv))
    Aeq[:, :n] = mid.T
    Aub, bub = [], []
    for idx, rr in enumerate(pin):
        row = np.zeros(nv)
        row[rr] = -1.0
        row[n] = float(cvec[idx])
        Aub.append(row)
        bub.append(0.0)
    c = np.zeros(nv)
    c[n] = -1.0
    c[:n] += 0.5 * hh * np.asarray(w)
    bounds = [((0.0, cap) if safe[k] else (0.0, 0.0)) for k in range(n)]
    bounds.append((0.0, cap))
    r = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), A_eq=Aeq, b_eq=es,
                bounds=bounds, method='highs')
    if not r.success:
        return None
    return np.array(r.x[:n])


def row_hessian_mass(box, rows):
    """[IV] w_r = sum_ij sup_box |d2 g_r / dz_i dz_j| for each row."""
    w = np.zeros(len(rows))
    for k, c in enumerate(rows):
        j, vs = row_jet(box, c, 2)
        w[k] = sum_up([mag(j.h[a][b]) for a in range(len(vs))
                       for b in range(len(vs))])
    return w


def barrier_constants(z, rows, om, h):
    """[IV] (eps_0, eps_w, Hbar) for W = sum om_r g_r on box(z, h)."""
    pb = point_box(z)
    e0 = sum_up([abs(float(om[k])) * mag(row_jet(pb, rows[k], 0)[0].v)
                 for k in range(len(rows)) if om[k] != 0])
    acc = [iv.mpf(0)] * NV
    for k in range(len(rows)):
        if om[k] == 0:
            continue
        ok = cnum(om[k])
        j, vs = row_jet(pb, rows[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + ok * j.g[loc]
    ew = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
                 for gi in range(NV)])
    box = box_of(z, h)
    Hd = {}
    for k in range(len(rows)):
        if om[k] == 0:
            continue
        ok = cnum(om[k])
        j, vs = row_jet(box, rows[k], 2)
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                t = ok * j.h[a][b]
                Hd[(ga, gb)] = t if (ga, gb) not in Hd else Hd[(ga, gb)] + t
    Hbar = sum_up([mag(x) for x in Hd.values()]) / 2.0
    return e0, ew, Hbar


# ============================================== STEP 1.5  (COOKBOOK AMENDMENT)
def gn_refine(z0, rows, dps=70, itf=30, itm=6):
    """Gauss-Newton (min-norm) refinement of z0 onto {g_r = 0, r in rows}.

    The A04 float points are only ~1e-9..1e-12 converged, which makes the
    Step-2 rank/spectral-gap verdict unreliable (singular values of 1e-10 are
    indistinguishable from noise).  Refine FIRST, audit and classify at the
    refined point.  float64 Gauss-Newton (pinv) then mp polish.
    """
    z = np.array([float(x) for x in z0])

    def Fnp(zz):
        pb = [iv.mpf(float(v)) for v in zz]
        F = np.zeros(len(rows))
        A = np.zeros((len(rows), NV))
        for k, c in enumerate(rows):
            j, vs = row_jet(pb, c, 1)
            F[k] = (float(j.v.a) + float(j.v.b)) / 2
            for loc, gi in enumerate(vs):
                A[k, gi] = (float(j.g[loc].a) + float(j.g[loc].b)) / 2
        return F, A

    for _ in range(itf):
        F, A = Fnp(z)
        if np.abs(F).max() < 1e-15:
            break
        z = z - np.linalg.pinv(A, rcond=1e-10) @ F
    zf = [Fraction(float(v)) for v in z]
    # independent row subset (the full active set is massively redundant --
    # rank 15..34 out of 20..65 rows -- and normal equations on it are
    # numerically singular; Newton on a maximal independent subset with
    # minimum-norm steps drives the DEPENDENT rows to zero too whenever the
    # system is consistent, which is exactly the test we want).
    _, A0 = Fnp(z)
    rk = int(np.linalg.matrix_rank(A0, tol=1e-9))
    piv = qr(A0.T, pivoting=True, mode='economic')[2]
    sel = sorted(int(p) for p in piv[:rk])
    srows = [rows[k] for k in sel]
    # ---- mp polish: Gauss-Newton min-norm steps at dps
    old, oldiv = mp.dps, iv.dps
    mp.dps = iv.dps = dps
    try:
        zm = [mp.mpf(x.numerator) / mp.mpf(x.denominator) for x in zf]
        for _ in range(itm):
            pb = [iv.mpf(v) for v in zm]
            m = len(srows)
            A = mp.zeros(m, NV)
            F = mp.zeros(m, 1)
            for k, c in enumerate(srows):
                j, vs = row_jet(pb, c, 1)
                F[k] = (mp.mpf(j.v.a) + mp.mpf(j.v.b)) / 2
                for loc, gi in enumerate(vs):
                    A[k, gi] = (mp.mpf(j.g[loc].a) + mp.mpf(j.g[loc].b)) / 2
            y = mp.lu_solve(A * A.T, -F)
            d = A.T * y
            zm = [zm[i] + d[i] for i in range(NV)]
        pb = [iv.mpf(v) for v in zm]
        res = max(mag(row_jet(pb, c, 0)[0].v) for c in rows)
        zh = [Fraction(round(Fraction(mp.nstr(v, dps - 5)) * 10 ** 45),
                       10 ** 45) for v in zm]
    finally:
        mp.dps, iv.dps = old, oldiv
    disp = max(abs(float(zh[i] - z0[i])) for i in range(NV))
    return zh, float(res), disp


# ================================== BRANCH DISJUNCTION  (generic A36 L1.2)
def axis_killable(box, o, e, p):
    """[IV] True if axis (owner o, edge e) provably does NOT separate (o,p)
    anywhere on the box: some corner row of the axis has sup g < 0.  Then, by
    separating-axis completeness, some OTHER axis must separate."""
    best = -1e18
    for k in range(4):
        v = sup(row_jet(box, {'kind': 'edge', 'i': p, 'corner': k, 'j': o,
                              'edge': e}, 0)[0].v)
        best = max(best, -v)
    return best > 0, best


def branch_set(box, i, j):
    """The axes of pair (i,j) that survive the kill test on the box.
    L1.2 disjunction: some surviving axis separates the pair."""
    live, kill = [], 1e18
    for o, p in ((i, j), (j, i)):
        for e in range(4):
            ok, m = axis_killable(box, o, e, p)
            if ok:
                kill = min(kill, m)
            else:
                live.append((o, e, p))
    return live, kill


def variant_structure(zh, aud, rows, meta, h):
    """Which contact pairs need branching, their live axis sets, and the row
    index owned by each (pair, axis).  Returns (branched, variants, axis_rows,
    kill_margin)."""
    box = box_of(zh, h)
    axis_rows = {}
    for k, m in enumerate(meta):
        if m['src'] != 'pair':
            continue
        c = rows[k]
        axis_rows.setdefault((m['pair'], (c['j'], c['edge'])), []).append(k)
    branched, kill = [], 1e18
    for rec in aud['pairs']:
        pr = (rec['i'], rec['j'])
        mine = [k for k, m in enumerate(meta)
                if m['src'] == 'pair' and m['pair'] == pr]
        if any(meta[k]['safe'] for k in mine):
            # at least one row of this pair is unconditionally box-valid by
            # the [V] test; the pair's non-[V]-safe rows are simply DROPPED
            # (omega = 0) and no branching is needed.  Branch ONLY the pairs
            # with no [V]-safe row at all (corner-corner / endpoint).
            continue
        live, km = branch_set(box, rec['i'], rec['j'])
        kill = min(kill, km)
        axes = sorted(set((o, e) for (o, e, p) in live))
        branched.append({'pair': pr, 'axes': axes})
    n = 1
    for b in branched:
        n *= max(1, len(b['axes']))
    return branched, n, axis_rows, kill


def variant_masks(rows, meta, branched, axis_rows, choice):
    """[V]-safe / global rows are always valid; a branched pair contributes
    only the rows of the chosen axis."""
    ok = []
    branched_pairs = {b['pair']: choice[i] for i, b in enumerate(branched)}
    for k, m in enumerate(meta):
        if m['src'] in ('wall', 'aux'):
            ok.append(True)
            continue
        if m['safe']:
            ok.append(True)
            continue
        pr = m['pair']
        if pr not in branched_pairs:
            ok.append(False)
            continue
        c = rows[k]
        ok.append((c['j'], c['edge']) == branched_pairs[pr])
    return ok


# ================================================================== STEP 3R
def newton_refine(z0, rows, P, iters=40, dps=70):
    """Newton on the square subsystem F = (g_r)_{r in P} = 0 at mp precision."""
    old = mp.dps
    mp.dps = dps
    old_iv = iv.dps
    iv.dps = dps
    try:
        z = [mp.mpf(x.numerator) / mp.mpf(x.denominator) for x in z0]
        for _ in range(iters):
            pb = [iv.mpf(v) for v in z]
            A = mp.zeros(NV, NV)
            F = mp.zeros(NV, 1)
            for r, k in enumerate(P):
                j, vs = row_jet(pb, rows[k], 1)
                F[r] = (mp.mpf(j.v.a) + mp.mpf(j.v.b)) / 2
                for loc, gi in enumerate(vs):
                    A[r, gi] = (mp.mpf(j.g[loc].a) + mp.mpf(j.g[loc].b)) / 2
            try:
                dz = mp.lu_solve(A, -F)
            except Exception:
                break
            z = [z[i] + dz[i] for i in range(NV)]
            if max(abs(dz[i]) for i in range(NV)) < mp.mpf(10) ** (-dps + 8):
                break
        res = max(abs(F[r]) for r in range(NV))
        out = [Fraction(round(Fraction(mp.nstr(v, dps - 5)) * 10 ** 45),
                        10 ** 45) for v in z]
    finally:
        mp.dps = old
        iv.dps = old_iv
    return out, float(res)


def krawczyk(zh, rows, P, Y, r):
    """[IV] one Krawczyk step for F = (g_r)_{r in P} on box(zh, r).

    Returns (contracted: bool, K offsets (34 iv), max ratio).
    """
    B = box_of(zh, r)
    pb = point_box(zh)
    Fc = [row_jet(pb, rows[k], 0)[0].v for k in P]
    Jr = []
    for k in P:
        j, vs = row_jet(B, rows[k], 1)
        Jr.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
    Yiv = [[cnum(v) for v in row] for row in Y]
    rad = cnum(r)
    dbox = iv.mpf([(-rad).a, rad.b])
    ok = True
    ratio = 0.0
    K = []
    for i in range(NV):
        acc = iv.mpf(0)
        for rr in range(NV):
            if Y[i][rr] != 0:
                acc = acc + Yiv[i][rr] * Fc[rr]
        Ki = -acc
        for j2 in range(NV):
            s = iv.mpf(0)
            for rr in range(NV):
                v = Jr[rr].get(j2)
                if v is not None and Y[i][rr] != 0:
                    s = s + Yiv[i][rr] * v
            m = (iv.mpf(1) if i == j2 else iv.mpf(0)) - s
            if not (float(m.a) == 0.0 and float(m.b) == 0.0):
                Ki = Ki + m * dbox
        K.append(Ki)
        hi = max(abs(float(Ki.a)), abs(float(Ki.b)))
        ratio = max(ratio, hi / float(r))
        if not (Ki.a > (-rad).a and Ki.b < rad.b):
            ok = False
    return ok, K, ratio


def make_Y(mid, P, den=10 ** 24):
    Yf = np.linalg.inv(mid[list(P)])
    return [[Fraction(round(Fraction(float(v)) * den), den) for v in row]
            for row in Yf]


def beta_kappa(zh, rows, P, Y, h):
    """[IV] beta = ||I - Y A_P(box(h))||_inf, kappa = ||Y||_inf."""
    box = box_of(zh, h)
    grads = []
    for k in P:
        j, vs = row_jet(box, rows[k], 1)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
    Yiv = [[cnum(v) for v in row] for row in Y]
    beta = 0.0
    for i in range(NV):
        rs = []
        for j2 in range(NV):
            s = iv.mpf(0)
            for rr in range(NV):
                v = grads[rr].get(j2)
                if v is not None and Y[i][rr] != 0:
                    s = s + Yiv[i][rr] * v
            rs.append(mag((iv.mpf(1) if i == j2 else iv.mpf(0)) - s))
        beta = max(beta, sum_up(rs))
    kappa = max(sum_up([abs(float(Y[i][r])) for r in range(NV)])
                for i in range(NV))
    return beta, kappa


def rationalise_omega(zh, rows, P, om_f, den_f=10 ** 12, den_s=10 ** 45):
    """Free entries rounded at den_f; pin block re-solved at dps 90."""
    n = len(rows)
    Pset = set(P)
    om = [Fraction(0)] * n
    for k in range(n):
        if k not in Pset and om_f[k] != 0:
            om[k] = Fraction(round(Fraction(float(om_f[k])) * den_f), den_f)
    old, oldiv = mp.dps, iv.dps
    mp.dps = iv.dps = 90
    try:
        pb = point_box(zh)
        AS = mp.zeros(NV, NV)
        rhs = mp.zeros(NV, 1)
        rhs[S_IDX] = mp.mpf(1)
        for c, k in enumerate(P):
            j, vs = row_jet(pb, rows[k], 1)
            for loc, gi in enumerate(vs):
                AS[gi, c] = (mp.mpf(j.g[loc].a) + mp.mpf(j.g[loc].b)) / 2
        for k in range(n):
            if om[k] == 0:
                continue
            j, vs = row_jet(pb, rows[k], 1)
            wk = mp.mpf(om[k].numerator) / mp.mpf(om[k].denominator)
            for loc, gi in enumerate(vs):
                rhs[gi] -= wk * (mp.mpf(j.g[loc].a) + mp.mpf(j.g[loc].b)) / 2
        ws = mp.lu_solve(AS, rhs)
    finally:
        mp.dps, iv.dps = old, oldiv
    for c, k in enumerate(P):
        om[k] = Fraction(round(Fraction(mp.nstr(ws[c], 60)) * den_s), den_s)
    return om


def validity_margins(zh, rows, om, h, safe):
    """[IV] min ([V]) margins over the omega-loaded sep rows on box(zh,h)."""
    box = box_of(zh, h)
    wt = wd = 1e9
    bad = []
    for k, c in enumerate(rows):
        if om[k] == 0 or c['kind'] != 'edge':
            continue
        if not safe[k]:
            bad.append(k)
        a, b = v_margins(box, c)
        wt, wd = min(wt, a), min(wd, b)
    return wt, wd, bad


# ================================================================== driver
def process_family(fidx, args):
    t0 = time.time()
    z0, fam, cat_idx = load_family(fidx)
    log = ['', '=' * 74,
           'FAMILY %d (catalogue %d)  s_min = %.15f' % (fidx, cat_idx,
                                                        fam['s_min']),
           'catalogue: %d pair contacts, %d wall contacts, tilt %s, count %d'
           % (fam['n_pair_contacts'], fam['n_wall_contacts'],
              fam['tilt_pattern_deg'], fam['count'])]

    # ---- STEP 1 + 1.5: tolerance LADDER (cookbook amendment).
    # The A04 points are converged to anywhere between 1e-12 and 1e-6, so a
    # single tol_c is wrong.  For each candidate tol we audit, Gauss-Newton
    # refine, and score by (a) refinement consistency and (b) whether e_s
    # lands in the cone.  The smallest tol that is both consistent and KKT-
    # feasible wins; the whole ladder is recorded in the atlas.
    ta = time.time()
    ladder = []
    pick = None
    es = np.zeros(NV)
    es[S_IDX] = 1.0
    for tol0 in args.tol0:
        aud0 = audit(z0, tol=tol0)
        rows0, _ = build_rows(aud0)
        zc, gnres, disp = gn_refine(z0, rows0)
        audc = audit(zc, tol=args.tol1)
        rowsc, metac = build_rows(audc)
        midc, _ = jac_at(zc, rowsc)
        lp = omega_lp(midc, [True] * len(rowsc), mode='feas') is not None
        ls = float(np.linalg.norm(
            midc.T @ np.linalg.lstsq(midc.T, es, rcond=None)[0] - es))
        rec = {'tol0': tol0, 'n_rows': len(rowsc), 'gn_residual': gnres,
               'displacement': disp, 'kkt_lp': lp, 'ls_res': ls,
               'n_pairs': len(audc['pairs']), 'n_walls': len(audc['walls'])}
        ladder.append(rec)
        log.append('  LADDER tol %.0e: %d rows (%d pairs/%d wall rows), GN '
                   'res %.2e, |dz| %.2e, ls_res %.2e, KKT LP %s'
                   % (tol0, len(rowsc), len(audc['pairs']),
                      len(audc['walls']), gnres, disp, ls, lp))
        if pick is None and gnres <= 1e-40 and lp:
            pick = (tol0, zc, audc, rowsc, metac, aud0)
    if pick is None:
        # priority: KKT-feasible (smallest tol) > consistent (smallest tol) >
        # smallest least-squares residual
        cand = ([r for r in ladder if r['kkt_lp']] or
                [r for r in ladder if r['gn_residual'] <= 1e-40] or
                sorted(ladder, key=lambda r: r['ls_res'])[:1])
        best = cand[0]
        tol0 = best['tol0']
        aud0 = audit(z0, tol=tol0)
        rows0, _ = build_rows(aud0)
        zc, gnres, disp = gn_refine(z0, rows0)
        audc = audit(zc, tol=args.tol1)
        rowsc, metac = build_rows(audc)
        pick = (tol0, zc, audc, rowsc, metac, aud0)
        log.append('  LADDER: no tol is both consistent and KKT-feasible; '
                   'falling back to tol %.0e' % tol0)
    tol0, zh, aud, rows, meta, aud0 = pick
    _, gnres, disp = gn_refine(z0, build_rows(audit(z0, tol=tol0))[0])
    safe = [m['safe'] for m in meta]
    aud['surprises'] = (
        ['tolerance ladder chose tol_c = %.0e (see ladder record)' % tol0] +
        aud0['surprises'] + ['[post-refine] ' + s for s in aud['surprises']])
    log.append('AUDIT+REFINE (%.1fs): tol_c %.0e, GN residual %.3e, '
               '|zhat - z0|_inf = %.3e -> %d wall rows, %d contact pairs, '
               '%d aux rows, %d rows (%d [V]-safe)'
               % (time.time() - ta, tol0, gnres, disp, len(aud['walls']),
                  len(aud['pairs']), len(aud['aux']), len(rows), sum(safe)))
    if gnres > 1e-40:
        log.append('  SURPRISE: GN residual %.2e -- the contact set is '
                   'INCONSISTENT (over-determined); the classification point '
                   'is the least-squares point' % gnres)
        aud['surprises'].append(
            'contact set inconsistent at %.2e after refinement' % gnres)
    z0 = zh
    ws = sorted(abs(g) for g in aud['wall_spectrum'])
    ps = sorted(aud['pair_spectrum'])
    log.append('  wall |g| spectrum: %s | next above tol: %.3e'
               % (' '.join('%.2e' % v for v in ws[:4]),
                  next((v for v in ws if v > TOL_C), float('nan'))))
    log.append('  pair gap spectrum (low 6): %s | first above tol: %.3e'
               % (' '.join('%.2e' % v for v in ps[:6]),
                  next((v for v in ps if v > TOL_C), float('nan'))))
    for rec in aud['pairs']:
        log.append('  pair (%2d,%2d) %-13s gap %+.2e owner %d edge %d '
                   'dom %s t %s axes_tied %d'
                   % (rec['i'], rec['j'], rec['class'], rec['gap'],
                      rec['owner'], rec['edge'], rec['dom'],
                      ['%.4f' % v for v in rec['t']], rec['n_axes_tied']))
    if aud['surprises']:
        for s in aud['surprises']:
            log.append('  SURPRISE: %s' % s)

    # ---- STEP 2
    cls = classify(z0, rows, meta)
    log.append('CLASSIFY: %s  rank %d/%d  sv_min_kept %.3e  sv_max_dropped '
               '%.3e  rattlers %s'
               % (cls['class'], cls['rank'], NV, cls['sv_min_kept'],
                  cls['sv_max_dropped'], cls['rattler_squares']))
    if cls.get('rfp_ok') is not None:
        log.append('  [RFP] 34x34 minor certified: %s (bound %.3e)'
                   % (cls['rfp_ok'], cls['rfp_bound']))

    mid, rad = jac_at(z0, rows)
    om_f = omega_lp(mid, safe, mode='feas')
    om_all = omega_lp(mid, [True] * len(rows), mode='feas')
    es = np.zeros(NV)
    es[S_IDX] = 1.0
    lsres = float(np.linalg.norm(
        mid.T @ np.linalg.lstsq(mid.T, es, rcond=None)[0] - es))
    th = [3 * i + 2 for i in range(NSQ)]
    keep = [k for k in range(NV) if k not in th]
    lsres_nt = float(np.linalg.norm(
        mid.T[keep] @ np.linalg.lstsq(mid.T[keep], es[keep], rcond=None)[0]
        - es[keep]))
    log.append('KKT: e_s in row space res %.2e (theta rows dropped: %.2e); '
               'LP on [V]-safe rows %s; LP on all active rows %s'
               % (lsres, lsres_nt, om_f is not None, om_all is not None))
    notcp = None
    if om_all is None:
        notcp = (
            'NOT-CP: e_s is NOT in the cone of ANY active row gradient '
            '(least-squares residual %.2e); dropping the 11 theta equations '
            'makes it feasible (%.2e), i.e. the A04 point is a local minimum '
            'only at FIXED ANGLES -- s strictly decreases under rotation. Not '
            'a drain; only the trivial coordinate bound s(z) >= s(zhat) - h '
            'is available here.' % (lsres, lsres_nt))
        cls['class'] = 'NOT-CP'
        cls['kkt'] = {'ls_res': lsres, 'ls_res_no_theta': lsres_nt}
        aud['surprises'].append(notcp)
        log.append('  ** %s' % notcp)
    if om_f is None and om_all is not None:
        log.append('  [V]-safe rows alone cannot reproduce e_s -> the branch '
                   'disjunction (endpoint / corner-corner rows) is LOAD-'
                   'BEARING for this family')

    if cls['class'] == 'RIGID' and not args.soft_only:
        entry, lg = step3R(fidx, cat_idx, fam, z0, aud, cls, rows, meta, safe,
                           mid, om_f, args)
        log += lg
        if entry is not None:
            entry['tol_ladder'] = ladder
            entry['tol_c'] = tol0
            entry['kkt'] = {'ls_res': lsres, 'ls_res_no_theta': lsres_nt,
                            'lp_safe_rows': om_f is not None,
                            'lp_all_rows': om_all is not None}
            entry['refine'] = {'gn_residual': gnres, 'displacement': disp}
            entry['wall_secs'] = time.time() - t0
            return entry, log
        log.append('3R failed -> falling back to 3S')
    entry, lg = step3S(fidx, cat_idx, fam, z0, aud, cls, rows, meta, safe,
                       mid, om_f, args)
    log += lg
    entry['tol_ladder'] = ladder
    entry['tol_c'] = tol0
    entry['kkt'] = {'ls_res': lsres, 'ls_res_no_theta': lsres_nt,
                    'lp_safe_rows': om_f is not None,
                    'lp_all_rows': om_all is not None}
    entry['refine'] = {'gn_residual': gnres, 'displacement': disp}
    if notcp:
        entry['notes'] = notcp
    entry['wall_secs'] = time.time() - t0
    return entry, log


def base_entry(fidx, cat_idx, fam, aud, cls, rows, meta, z=None):
    return {
        'family_id': fidx,
        'catalogue_index': cat_idx,
        's_min_float': fam['s_min'],
        'class': cls['class'],
        'n_contacts': {'pairs': len(aud['pairs']), 'walls': len(aud['walls']),
                       'aux': len(aud['aux']), 'rows': len(rows),
                       'safe_rows': sum(1 for m in meta if m['safe']),
                       'catalogue_pairs': fam['n_pair_contacts'],
                       'catalogue_walls': fam['n_wall_contacts']},
        'rank': cls['rank'],
        'sv_gap': [cls['sv_min_kept'], cls['sv_max_dropped']],
        'rattler_squares': cls['rattler_squares'],
        'audit_surprises': aud['surprises'],
        'tol_ladder': None,
        'contact_table': contact_table(aud, z),
        'canonical_sig': None,
    }


def corner_xy(z, i, k):
    """float64 (x, y) of corner k of square i at the point z."""
    cx, cy, th = float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])
    hx, hy = float(HALF[k][0]), float(HALF[k][1])
    c, s = math.cos(th), math.sin(th)
    return (cx + c * hx - s * hy, cy + s * hx + c * hy)


def contact_table(aud, z=None):
    """Cookbook step 5 / lead amendment: the contact table carries square
    COORDINATES and a canonical (D4-reduced) geometric signature per contact,
    not just family-local indices -- family-local orderings are ambiguous
    (cf. the lead's correction to the pilot's Trump audit note)."""
    R = None
    if z is not None:
        _, refl, rot = canonical_sig(z, want_frame=True)
        s = float(z[S_IDX])

        def R(x, y):                                        # noqa: E306
            X, Y = (s - x, y) if refl else (x, y)
            for _ in range(rot):
                X, Y = s - Y, X
            return [round(X, 9), round(Y, 9)]

    def pt(i, k):
        if R is None:
            return None, None
        x, y = corner_xy(z, i, k)
        return [round(x, 9), round(y, 9)], R(x, y)

    def ctr(i):
        if R is None:
            return None, None
        x, y = float(z[3 * i]), float(z[3 * i + 1])
        return [round(x, 9), round(y, 9)], R(x, y)

    tab = []
    for w in aud['walls']:
        xy, xyc = pt(w['i'], w['corner'])
        tab.append({'type': 'wall', 'i': w['i'], 'corner': w['corner'],
                    'wall': w['wall'], 'xy': xy, 'xy_canon': xyc,
                    'geom_sig': None if xyc is None else
                    'wall@%.6f,%.6f' % (xyc[0], xyc[1])})
    for rec in aud['pairs']:
        specs = []
        for s_ in rec['rowspecs']:
            xy, xyc = pt(s_['other'], s_['corner'])
            specs.append({'owner': s_['owner'], 'other': s_['other'],
                          'edge': s_['edge'], 'corner': s_['corner'],
                          't': s_['t'], 'safe': s_['safe'],
                          'xy': xy, 'xy_canon': xyc})
        dom = rec.get('dom') or [0]
        xy, xyc = pt(rec['other'], dom[0])
        tab.append({'type': 'pair', 'i': rec['i'], 'j': rec['j'],
                    'class': rec['class'], 'gap': rec['gap'],
                    'n_axes_tied': rec['n_axes_tied'],
                    'xy': xy, 'xy_canon': xyc,
                    'geom_sig': None if xyc is None else
                    '%s@%.6f,%.6f' % (rec['class'], xyc[0], xyc[1]),
                    'rowspecs': specs})
    for a in aud['aux']:
        xy_i, xyc_i = ctr(a['i'])
        xy_j, xyc_j = ctr(a['j'])
        tab.append({'type': 'aux', 'i': a['i'], 'j': a['j'],
                    'xy': [xy_i, xy_j], 'xy_canon': [xyc_i, xyc_j],
                    'geom_sig': None if xyc_i is None else
                    'aux@%s|%s' % (tuple(xyc_i), tuple(xyc_j))})
    return tab


def rows_from_table(tab):
    """Rebuild the row list from the contact table (the checker does the same
    thing independently)."""
    rows, safe = [], []
    for e in tab:
        if e['type'] == 'wall':
            rows.append({'kind': 'wall', 'i': e['i'], 'corner': e['corner'],
                         'wall': e['wall']})
            safe.append(True)
    for e in tab:
        if e['type'] == 'pair':
            for s in e['rowspecs']:
                rows.append({'kind': 'edge', 'i': s['other'],
                             'corner': s['corner'], 'j': s['owner'],
                             'edge': s['edge']})
                safe.append(bool(s['safe']))
    for e in tab:
        if e['type'] == 'aux':
            rows.append({'kind': 'dist', 'i': e['i'], 'j': e['j']})
            safe.append(True)
    return rows, safe


# ---------------------------------------------------------------- step 3R
def step3R(fidx, cat_idx, fam, z0, aud, cls, rows, meta, safe, mid, om_f,
           args):
    log = []
    # pin set: prefer safe rows; QR-pivot for a well-conditioned 34-minor
    cand = [k for k in range(len(rows)) if safe[k]]
    sub = mid[cand]
    if np.linalg.matrix_rank(sub, tol=1e-9) < NV:
        log.append('  3R: safe rows have rank %d < 34 -> no safe pin basis'
                   % np.linalg.matrix_rank(sub, tol=1e-9))
        return None, log
    piv = qr(sub.T, pivoting=True, mode='economic')[2]
    P = sorted(cand[int(p)] for p in piv[:NV])
    ok, bnd = certify_nonsingular(mid[P], np.zeros((NV, NV)))
    log.append('  3R pin set P: %d safe rows, [RFP] bound %.3e' % (len(P), bnd))

    zh, res = newton_refine(z0, rows, P)
    log.append('  3R Newton: residual %.3e, |zh - z0|_inf = %.3e'
               % (res, max(abs(float(zh[i] - z0[i])) for i in range(NV))))
    midh, radh = jac_at(zh, rows)
    Y = make_Y(midh, P)

    # Krawczyk existence + uniqueness
    rN = None
    for r in [Fraction(1, 2000), Fraction(1, 10 ** 4), Fraction(1, 10 ** 5),
              Fraction(1, 10 ** 6)]:
        okk, K, ratio = krawczyk(zh, rows, P, Y, r)
        log.append('  3R Krawczyk r=%-10s contracted %-5s ratio %.4f'
                   % (fs(r), okk, ratio))
        if okk:
            rN = r
            break
    if rN is None:
        log.append('  3R: Krawczyk failed at every radius')
        return None, log
    # tight value enclosure
    _, K2, _ = krawczyk(zh, rows, P, Y, Fraction(1, 10 ** 30))
    v_lo = inf(cnum(zh[S_IDX]) + K2[S_IDX])
    v_hi = sup(cnum(zh[S_IDX]) + K2[S_IDX])
    log.append('  3R value enclosure: [%.18f, %.18f] width %.2e'
               % (v_lo, v_hi, v_hi - v_lo))

    # ---- max-form barrier, h-bisection
    cvec_full = [max(abs(float(Y[i][r])) for i in range(NV))
                 for r in range(NV)]
    best = None
    hi = Fraction(1, 100)
    lo = Fraction(0)
    for it in range(args.bisect):
        h = (lo + hi) / 2 if it else hi
        r = try_radius(zh, rows, safe, midh, P, Y, cvec_full, h, log,
                       verbose=(it < 2))
        if r is not None:
            best = r
            lo = h
        else:
            hi = h
        if it == 0 and r is not None:
            break
    if best is None:
        log.append('  3R: no radius certified')
        return None, log
    h = best['h']
    x_star = best['x_star']
    V = Fraction(v_lo) - Fraction(1, 10 ** 40)   # x* < 1e-40, exact rationals
    log.append('  3R CERTIFIED h = %s (%.3e), x* = %.3e, psi/h = %.4f, '
               'V = %.18f' % (fs(h), float(h), x_star, best['psi_over_h'],
                              float(V)))

    entry = base_entry(fidx, cat_idx, fam, aud, cls, rows, meta, z0)
    entry['mode'] = '3R'
    entry['value'] = {'v_lo': v_lo, 'v_hi': v_hi, 'V': float(V),
                      'x_star': x_star}
    entry['h_certified'] = fs(h)
    cert = {
        'family_id': fidx, 'catalogue_index': cat_idx, 'mode': '3R',
        's_min_float': fam['s_min'], 'class': cls['class'],
        'contact_table': entry['contact_table'],
        'active_tol': args.tol1,
        'z_center': [fs(x) for x in zh],
        'P': P, 'Y': [[fs(v) for v in row] for row in Y],
        'r_N': fs(rN),
        'omega_rational': [fs(x) for x in best['om']],
        'h': fs(h),
        'claims': {'eps_0': best['e0'], 'eps_w': best['ew'],
                   'Hbar': best['Hbar'], 'beta': best['beta'],
                   'kappa': best['kappa'], 'kappa_eff': best['keff'],
                   'g_max': best['gmax'], 'psi': best['psi'],
                   'x_star': x_star, 'v_lo': v_lo, 'v_hi': v_hi,
                   'V': fs(V), 'wt': best['wt'], 'wd': best['wd']},
        'claim_text': ('every interior-disjoint 11-square packing z with '
                       '|z - z_center|_inf <= h has s(z) >= V'),
    }
    path = os.path.join(CERTDIR, 'fam%02d_3R.json' % fidx)
    with open(path, 'w') as f:
        json.dump(cert, f, indent=1)
    entry['cert_path'] = os.path.relpath(path, ATT).replace('\\', '/')
    return entry, log


def try_radius(zh, rows, safe, midh, P, Y, cvec_full, h, log, verbose=False):
    box = box_of(zh, h)
    w = row_hessian_mass(box, rows)
    beta, kappa = beta_kappa(zh, rows, P, Y, h)
    if beta >= 1.0:
        if verbose:
            log.append('  3R h=%.3e: beta = %.4f >= 1' % (float(h), beta))
        return None
    cvec = [cvec_full[list(P).index(k)] if k in P else 0.0
            for k in range(len(rows))]
    om_f = omega_lp(midh, safe, mode='maxform', pin=P,
                    cvec=[cvec_full[i] for i in range(NV)], w=w,
                    hh=float(h) / (1.0 - beta))
    if om_f is None or min(om_f[k] for k in P) <= 0:
        if verbose:
            log.append('  3R h=%.3e: max-form LP infeasible / pin omega <= 0'
                       % float(h))
        return None
    om = rationalise_omega(zh, rows, P, om_f)
    if any(om[k] < 0 for k in range(len(rows))) or \
       any(om[k] <= 0 for k in P) or \
       any(om[k] != 0 for k in range(len(rows)) if not safe[k]):
        if verbose:
            log.append('  3R h=%.3e: rationalised omega violates sign '
                       'discipline' % float(h))
        return None
    e0, ew, Hbar = barrier_constants(zh, rows, om, h)
    pb = point_box(zh)
    gmax = max(mag(row_jet(pb, rows[k], 0)[0].v) for k in P)
    keff = max(cvec_full[i] / float(om[P[i]]) for i in range(NV))
    hf = float(h)
    E = e0 + ew * hf + Hbar * hf * hf
    psi = (keff * E + kappa * gmax) / (1.0 - beta)
    wt, wd, bad = validity_margins(zh, rows, om, h, safe)
    if verbose:
        log.append('  3R h=%.3e: beta %.5f kappa %.3f keff %.3f Hbar %.3f '
                   'psi/h %.4f wt %.5f wd %.5f'
                   % (hf, beta, kappa, keff, Hbar, psi / hf, wt, wd))
    if not (psi < hf and wt > 0 and wd > 0 and not bad):
        return None
    x = hf
    C = keff / (1.0 - beta)
    for _ in range(800):
        x = C * (e0 + ew * x + Hbar * x * x) + kappa * gmax / (1.0 - beta)
    if not (x < hf):
        return None
    return {'h': h, 'om': om, 'e0': e0, 'ew': ew, 'Hbar': Hbar, 'beta': beta,
            'kappa': kappa, 'keff': keff, 'gmax': gmax, 'psi': psi,
            'psi_over_h': psi / hf, 'x_star': x, 'wt': wt, 'wd': wd}


# ---------------------------------------------------------------- step 3S
SOFT_H = [Fraction(5, 10 ** 4), Fraction(1, 10 ** 3), Fraction(2, 10 ** 3)]
V_TARGET = 3.877084          # the incumbent s(11) upper bound (A33)


def variant_omega(zh, rows, mid, ok_mask, w):
    """[LP]+rationalisation: omega >= 0 on the variant's valid rows with
    A^T omega = e_s, minimising the Hessian mass sum w_r omega_r.
    Returns (omega rationals, feasible flag)."""
    n = len(rows)
    es = np.zeros(NV)
    es[S_IDX] = 1.0
    bounds = [((0.0, 1e4) if ok_mask[k] else (0.0, 0.0)) for k in range(n)]
    r = linprog(np.asarray(w) + 1e-6, A_eq=mid.T, b_eq=es, bounds=bounds,
                method='highs')
    if not r.success:
        return [Fraction(0)] * n, False
    om = [Fraction(round(Fraction(float(v)) * 10 ** 12), 10 ** 12)
          if v > 1e-13 else Fraction(0) for v in r.x]
    for k in range(n):
        if not ok_mask[k]:
            om[k] = Fraction(0)
    return om, True


def soft_constants(zh, rows, om):
    """[IV] (W0, r_res) at the centre."""
    pb = point_box(zh)
    W0 = sum_up([abs(float(om[k])) * mag(row_jet(pb, rows[k], 0)[0].v)
                 for k in range(len(rows)) if om[k] != 0])
    acc = [iv.mpf(0)] * NV
    for k in range(len(rows)):
        if om[k] == 0:
            continue
        okk = cnum(om[k])
        j, vs = row_jet(pb, rows[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + okk * j.g[loc]
    r_res = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
                    for gi in range(NV)])
    return W0, r_res


def v_soft_at(zh, rows, meta, om, W0, r_res, h):
    """[IV] V_soft(h) for one variant + its [V] margins."""
    hf = float(h)
    _, _, Hbar = barrier_constants(zh, rows, om, h)
    box = box_of(zh, h)
    wt = wd = 1e9
    for k, c in enumerate(rows):
        if om[k] == 0 or c['kind'] != 'edge' or not meta[k]['safe']:
            continue
        a, b = v_margins(box, c)
        wt, wd = min(wt, a), min(wd, b)
    V = float(zh[S_IDX]) - W0 - r_res * hf - Hbar * hf * hf
    return V, Hbar, wt, wd


def step3S(fidx, cat_idx, fam, zh, aud, cls, rows, meta, safe, mid, om_f,
           args):
    log = []
    n = len(rows)
    s0 = float(zh[S_IDX])
    h_probe = Fraction(args.hmax_num, args.hmax_den)  # lead patch: was 1/20
    branched, nvar, axis_rows, kill = variant_structure(zh, aud, rows, meta,
                                                        h_probe)
    log.append('  3S branch structure at h_probe=%.3g: %d branched pairs %s '
               '-> %d variants; min kill margin %.4f'
               % (float(h_probe), len(branched),
                  [(b['pair'], b['axes']) for b in branched], nvar, kill))
    if kill <= 0:
        log.append('  3S: kill test FAILED at h_probe -> branch disjunction '
                   'not established; falling back to omega = 0 only')
        branched, nvar = [], 1
    elif nvar > VAR_CAP:
        # cookbook amendment A7: refuse beyond the cap and report.  The
        # branch-free certificate ([V]-safe rows only, omega = 0 if that LP is
        # infeasible) is still sound, so we emit it rather than failing.
        log.append('  3S: %d variants EXCEEDS the cap %d -> REFUSED; emitting '
                   'the branch-free ([V]-safe rows only) certificate instead'
                   % (nvar, VAR_CAP))
        aud['surprises'].append(
            'variant count %d exceeds cap %d (%d branched pairs): branch '
            'disjunction refused, branch-free certificate emitted'
            % (nvar, VAR_CAP, len(branched)))
        branched, nvar = [], 1
    axis_lists = [b['axes'] for b in branched]
    import itertools
    choices = list(itertools.product(*axis_lists)) if axis_lists else [()]

    w = row_hessian_mass(box_of(zh, Fraction(1, 100)), rows)
    vinfo = []
    for ci, ch in enumerate(choices):
        mask = variant_masks(rows, meta, branched, axis_rows, ch)
        om, feas = variant_omega(zh, rows, mid, mask, w)
        W0, r_res = soft_constants(zh, rows, om)
        vinfo.append({'choice': [list(x) for x in ch], 'om': om,
                      'feasible': feas, 'W0': W0, 'r_res': r_res,
                      'l1': float(sum(abs(float(x)) for x in om))})
    nf = sum(1 for v in vinfo if not v['feasible'])
    log.append('  3S variants: %d total, %d with an infeasible multiplier LP '
               '(those fall back to omega = 0, i.e. the trivial bound '
               's(z) >= s(zhat) - h)' % (len(vinfo), nf))
    log.append('  3S max ||omega||_1 = %.3f, max r_res = %.2e, max W0 = %.2e'
               % (max(v['l1'] for v in vinfo), max(v['r_res'] for v in vinfo),
                  max(v['W0'] for v in vinfo)))

    def Vmin(h):
        worst = None
        det = []
        for v in vinfo:
            V, Hbar, wt, wd = v_soft_at(zh, rows, meta, v['om'], v['W0'],
                                        v['r_res'], h)
            if not (wt > 0 and wd > 0):
                V = min(V, s0 - float(h))     # [V] rows unusable: trivial bd
            det.append({'V': V, 'Hbar': Hbar, 'wt': wt, 'wd': wd})
            worst = V if worst is None else min(worst, V)
        return worst, det

    # ---- cookbook table
    table = []
    for h in SOFT_H:
        V, det = Vmin(h)
        table.append({'h': fs(h), 'h_float': float(h), 'V_soft': V,
                      'Hbar_max': max(d['Hbar'] for d in det),
                      'wt_min': min(d['wt'] for d in det),
                      'wd_min': min(d['wd'] for d in det)})
        log.append('  3S h=%.1e: V_soft %.15f (Hbar<=%.3f, wt>=%.5f)'
                   % (float(h), V, table[-1]['Hbar_max'], table[-1]['wt_min']))

    # ---- h-maximisation against the incumbent (COOKBOOK AMENDMENT)
    lo, hi = Fraction(1, 10 ** 4), h_probe
    Vlo, _ = Vmin(lo)
    if Vlo < V_TARGET:
        hbest, Vbest = None, Vlo
    else:
        Vh, _ = Vmin(hi)
        if Vh >= V_TARGET:
            hbest, Vbest = hi, Vh
        else:
            for _ in range(args.bisect):
                m = (lo + hi) / 2
                Vm, _ = Vmin(m)
                if Vm >= V_TARGET:
                    lo, Vlo = m, Vm
                else:
                    hi = m
            hbest, Vbest = lo, Vlo
    log.append('  3S h_max vs incumbent %.6f: h = %s (%.4e), V = %.12f'
               % (V_TARGET, fs(hbest) if hbest else None,
                  float(hbest) if hbest else float('nan'), Vbest))

    entry = base_entry(fidx, cat_idx, fam, aud, cls, rows, meta, zh)
    entry['mode'] = '3S'
    entry['n_variants'] = len(vinfo)
    entry['value'] = {'V_soft_table': table,
                      'V_soft_at_1e-3': [t['V_soft'] for t in table
                                         if t['h_float'] == 1e-3][0],
                      'h_max_vs_incumbent': fs(hbest) if hbest else None,
                      'V_at_h_max': Vbest, 'V_target': V_TARGET}
    entry['h_certified'] = fs(hbest) if hbest else None
    cert = {
        'family_id': fidx, 'catalogue_index': cat_idx, 'mode': '3S',
        's_min_float': fam['s_min'], 'class': cls['class'],
        'contact_table': entry['contact_table'],
        'active_tol': args.tol1,
        'z_center': [fs(x) for x in zh],
        's_center': repr(float(zh[S_IDX])),
        'branched': [{'pair': list(b['pair']),
                      'axes': [list(a) for a in b['axes']]}
                     for b in branched],
        'kill_margin': kill, 'h_probe': fs(h_probe),
        'variants': [{'choice': v['choice'], 'feasible': v['feasible'],
                      'omega_rational': [fs(x) for x in v['om']],
                      'W0': v['W0'], 'r_res': v['r_res']} for v in vinfo],
        'h_table': [t['h'] for t in table] +
                   ([fs(hbest)] if hbest else []),
        'claims': {'s_center': s0, 'table': table,
                   'h_max': fs(hbest) if hbest else None, 'V_max': Vbest,
                   'V_target': V_TARGET},
        'claim_text': ('every interior-disjoint 11-square packing z with '
                       '|z - z_center|_inf <= h has s(z) >= V_soft(h); '
                       'V_soft(h) = min over the branch variants of '
                       's_center - W0 - r_res h - Hbar(h) h^2, and the '
                       'trivial bound s_center - h is used where a variant '
                       'has no multiplier'),
    }
    path = os.path.join(CERTDIR, 'fam%02d_3S.json' % fidx)
    with open(path, 'w') as f:
        json.dump(cert, f, indent=1)
    entry['cert_path'] = os.path.relpath(path, ATT).replace('\\', '/')
    return entry, log


# ---------------------------------------------------------------- dedupe sig
def canonical_sig(z0, want_frame=False):
    """D4 + square-relabel canonical signature (rounded), for atlas dedupe.
    With want_frame, also return the (refl, rot) achieving it, so that the
    contact table can be written in the same canonical frame."""
    s = float(z0[S_IDX])
    P = [(float(z0[3 * i]), float(z0[3 * i + 1]), float(z0[3 * i + 2]))
         for i in range(NSQ)]
    best = None
    bframe = (0, 0)
    for refl in (0, 1):
        for rot in range(4):
            pts = []
            for (x, y, th) in P:
                X, Y_ = (s - x, y) if refl else (x, y)
                T = (-th) if refl else th
                for _ in range(rot):
                    X, Y_ = s - Y_, X
                    T = T + math.pi / 2
                pts.append((round(X, 6), round(Y_, 6),
                            round(T % (math.pi / 2), 6)))
            sig = tuple(sorted(pts))
            if best is None or sig < best:
                best = sig
                bframe = (refl, rot)
    if want_frame:
        return best, bframe[0], bframe[1]
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fam', type=int, nargs='+', required=True)
    ap.add_argument('--bisect', type=int, default=14)
    ap.add_argument('--hmax-num', type=int, default=1, dest='hmax_num')
    ap.add_argument('--hmax-den', type=int, default=20, dest='hmax_den')
    ap.add_argument('--tol0', type=float, nargs='+',
                    default=[1e-7, 1e-6, 1e-5, 1e-4],
                    help='contact-tolerance ladder at the raw A04 point')
    ap.add_argument('--tol1', type=float, default=1e-9,
                    help='contact tolerance at the refined point')
    ap.add_argument('--soft-only', action='store_true')
    ap.add_argument('--atlas', default=os.path.join(RESULTS, 'atlas.json'))
    args = ap.parse_args()
    os.makedirs(CERTDIR, exist_ok=True)

    atlas = {'entries': []}
    if os.path.exists(args.atlas):
        with open(args.atlas) as f:
            atlas = json.load(f)
    byid = {e['family_id']: i for i, e in enumerate(atlas['entries'])}

    for fidx in args.fam:
        entry, log = process_family(fidx, args)
        z0, _, _ = load_family(fidx)
        sig = canonical_sig(z0)
        entry['canonical_sig'] = [list(p) for p in sig]
        merges = [e['family_id'] for e in atlas['entries']
                  if e['family_id'] != fidx and e.get('canonical_sig') and
                  max(abs(a - b) for p, q in zip(e['canonical_sig'], sig)
                      for a, b in zip(p, q)) < 1e-6]
        entry['dedupe_merges'] = merges
        print('\n'.join(log))
        print('  wall time %.1fs' % entry['wall_secs'])
        if fidx in byid:
            atlas['entries'][byid[fidx]] = entry
        else:
            byid[fidx] = len(atlas['entries'])
            atlas['entries'].append(entry)
        if fidx == 0:
            entry['cross_reference'] = {
                'note': 'family 0 = the Trump/Stromquist 11-square packing; '
                        'already certified independently by A22 (local '
                        'rigidity, Krawczyk r_N = 1/2000) and A36 (16 (V\') '
                        'max-form barriers, per-variant h = 3.779e-3, '
                        'branch-free universal h = 3.689e-3).  The A37 entry '
                        'is a FROM-SCRATCH reproduction by the family-generic '
                        'pipeline and agrees: same value enclosure, Krawczyk '
                        'contraction at r_N = 1/2000 (ratio 0.0566), '
                        'h = 3.759e-3 (99.5% of A36) -- and it needs NO '
                        'branch variants, because the [V] test discharges '
                        'every loaded row unconditionally.',
                'a22': 'attempts/A22-local-rigidity/results/krawczyk_cert.json',
                'a36': 'attempts/A36-levers/results/a36_certs/',
                'a36_h_variant': 0.003779, 'a36_h_universal': 0.003689,
                'a36_x_star': 6.111671549307892e-58,
            }
        atlas['entries'].sort(key=lambda e: e['family_id'])
        atlas['meta'] = {
            'attempt': 'A37-cp-atlas',
            'spec': 'attempts/A37-cp-atlas/notes/cookbook.md',
            'producer': 'attempts/A37-cp-atlas/code/a37_pipeline.py',
            'checker': 'attempts/A37-cp-atlas/code/a37_check.py',
            'source': 'attempts/A04-upper-search/families_catalogue.json',
            'family_index': 'index in the s_min-sorted list of A04 families '
                            'with s_min < 3.95 (0 = Trump)',
            'best_x_layout': 'centres interleaved x[2i],x[2i+1]; thetas '
                             'blocked x[22+i]; s = x[33]  -> converted to the '
                             'A22 order z[3i],z[3i+1],z[3i+2],z[33]',
            'V_target': V_TARGET,
            'claim': 'for each entry: every interior-disjoint 11-square '
                     'packing z with |z - z_center|_inf <= h_certified has '
                     's(z) >= V (3R) or >= V_soft(h) (3S)',
        }
        with open(args.atlas, 'w') as f:
            json.dump(atlas, f, indent=1)
        print('  checkpointed atlas -> %s' % args.atlas)
    return 0


if __name__ == '__main__':
    sys.exit(main())
