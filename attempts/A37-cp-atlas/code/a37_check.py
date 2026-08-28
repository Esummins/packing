#!/usr/bin/env python
"""a37_check.py -- STANDALONE re-checker for A37 certificates
(results/certs/fam*_3R.json, fam*_3S.json).   Cookbook step 4.

Imports ONLY  mpmath.iv + fractions + json + math + glob + os + sys.  It uses
NO producer library: not a37_pipeline, not a36_lib, not strata_lib, not
t3lib, not numpy, not scipy.  The order-2 interval jets and the row language
below are transcribed (with attribution) from A36's own standalone re-checker
attempts/A36-levers/code/a36_check.py, which in turn transcribes A35's
m2_check_inflation.py.

The checker does NOT trust the producer's row list, safety flags, branch sets
or omega support.  From the certificate's CONTACT TABLE alone it

  [R] rebuilds every row and compares with the producer's implied row order;
  [C] re-verifies that every row is ACTIVE at z_center;
  [S] recomputes the [V] safety flag of every sep row from the tangential
      coordinate at z_center (a producer that marked an endpoint row "safe"
      fails here);
  [B] recomputes the branch structure: for every pair carrying a non-[V]-safe
      row it re-runs the kill test on box(z_center, h_probe) and checks that
      the certificate's live-axis set CONTAINS every axis the checker cannot
      kill, and that the certificate enumerates the full product of live axes;
  [O] sign discipline: omega >= 0, omega = 0 on every row not valid in that
      variant (rows outside the variant's chosen axis, or non-safe rows of an
      unbranched pair);
  [W] W0 = sum |omega_r| |g_r(z_center)|;
  [G] r_res = ||A(z_center)^T omega - e_s||_1;
  [H] Hbar(h) = (1/2) sum_ij sup_box |d^2 W / dz_i dz_j|;
  [V] tangential/depth margins of every omega-loaded sep row on box(h);
  [X] V_soft(h) = min over variants of  s_center - W0 - r_res h - Hbar h^2
      (with the trivial coordinate bound s_center - h substituted whenever a
      variant's [V] margins fail), and V_claimed <= V_recomputed.

For a 3R certificate it additionally checks the A36 max-form chain
  [K] beta = sup ||I - Y A_P||_inf < 1, kappa = ||Y||_inf;
  [E] kappa_eff = max_{r in P} (max_i |Y_ir|) / omega_r;
  [P] psi(h) = (kappa_eff E(h) + kappa g_max)/(1-beta) < h and the least fixed
      point x* of x -> kappa_eff E(x)/(1-beta) + kappa g_max/(1-beta) is <= h;
  [F] V <= v_lo - x*.

SOUNDNESS NOTES (what the arithmetic above is allowed to conclude)
  * wall rows and dist rows are valid for EVERY interior-disjoint packing:
    containment, and disjoint incircles of radius 1/2 => |c_i - c_j| >= 1.
  * a sep row  g = n_e(th_o).(q_k(p) - c_o) - 1/2  is valid on the box as soon
    as sup|t| < 1/2 and inf d > -1/2 there ([V]): a corner of p with both
    frame coordinates strictly inside would be interior to o.
  * a sep row of a BRANCH axis is valid on the sub-box where that axis
    separates the pair (the L1.1 over-estimate principle: any corner row of an
    axis is >= that axis' gap), and the kill test [B] plus separating-axis
    completeness makes the union of the branches exhaustive.

Corruption gates (each MUST make the checker fail):
    omega-sign, h-big, drop-aux, drop-branch, value-inflate
Usage:
    python a37_check.py [certdir] [--corrupt MODE]
Exit 0 = all PASS (or, under --corrupt, the checker failed as required).
"""
import glob
import itertools
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

iv.dps = 60

NV = 34
NSQ = 11
S_IDX = 33
HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]
T_INSIDE = 1e-6
ACTIVE_TOL = 1e-20


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


# ---- order-2 forward jets (transcribed from a36_check.py, A36 / A35)
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


def sep_td(box, c):
    i, j, k, e = c['i'], c['j'], c['corner'], c['edge']
    hx, hy = cnum(HALF[k][0]), cnum(HALF[k][1])
    ci, si = iv.cos(box[3 * i + 2]), iv.sin(box[3 * i + 2])
    qx = box[3 * i] + (ci * hx - si * hy)
    qy = box[3 * i + 1] + (si * hx + ci * hy)
    nhx, nhy = NHAT[e]
    cj, sj = iv.cos(box[3 * j + 2]), iv.sin(box[3 * j + 2])
    nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
    ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
    wx, wy = qx - box[3 * j], qy - box[3 * j + 1]
    return (-ny * wx + nx * wy), (nx * wx + ny * wy)


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


def rebuild(tab):
    """[R] rows + [S]-independent safety placeholder, from the contact table."""
    rows, kind = [], []
    for e in tab:
        if e['type'] == 'wall':
            rows.append({'kind': 'wall', 'i': e['i'], 'corner': e['corner'],
                         'wall': e['wall']})
            kind.append(('wall', None, None))
    for e in tab:
        if e['type'] == 'pair':
            for s in e['rowspecs']:
                rows.append({'kind': 'edge', 'i': s['other'],
                             'corner': s['corner'], 'j': s['owner'],
                             'edge': s['edge']})
                kind.append(('pair', (e['i'], e['j']),
                             (s['owner'], s['edge'])))
    for e in tab:
        if e['type'] == 'aux':
            rows.append({'kind': 'dist', 'i': e['i'], 'j': e['j']})
            kind.append(('aux', None, None))
    return rows, kind


def live_axes(box, i, j):
    """[B] axes of pair (i,j) that the checker cannot kill on the box."""
    live = []
    for o, p in ((i, j), (j, i)):
        for e in range(4):
            best = max(-sup(row_jet(box, {'kind': 'edge', 'i': p, 'corner': k,
                                          'j': o, 'edge': e}, 0)[0].v)
                       for k in range(4))
            if not (best > 0):
                live.append((o, e))
    return live


def hess_mass(box, rows, om):
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
    return sum_up([mag(x) for x in Hd.values()]) / 2.0


def check_cert(cert, ck, verbose=True):
    z0 = [frac(x) for x in cert['z_center']]
    pb = [cnum(x) for x in z0]
    tab = cert['contact_table']
    rows, kind = rebuild(tab)
    n = len(rows)
    tag = 'fam%02d/%s' % (cert['family_id'], cert['mode'])

    # [C] every rebuilt row is active at the centre
    gz = [mag(row_jet(pb, c, 0)[0].v) for c in rows]
    atol = max(ACTIVE_TOL, float(cert.get('active_tol', ACTIVE_TOL)))
    ck('C %s all rebuilt rows active at z_center (tol %.0e)' % (tag, atol),
       max(gz) <= atol, 'max |g| = %.3e' % max(gz))

    # [S] recompute the [V] safety flag from the tangential coordinate
    safe = []
    for k, c in enumerate(rows):
        if c['kind'] != 'edge':
            safe.append(True)
            continue
        t, d = sep_td(pb, c)
        safe.append(mag(t) <= 0.5 - T_INSIDE)
    declared = []
    for e in tab:
        if e['type'] == 'pair':
            declared += [bool(s['safe']) for s in e['rowspecs']]
    got = [safe[k] for k in range(n) if kind[k][0] == 'pair']
    ck('S %s [V] safety flags reproduce the certificate' % tag,
       got == declared,
       'checker %s vs cert %s' % (got[:8], declared[:8]))

    # [B] branch structure
    hprobe = frac(cert['h_probe']) if 'h_probe' in cert else None
    branched = {tuple(b['pair']): [tuple(a) for a in b['axes']]
                for b in cert.get('branched', [])}
    # a pair must be branched exactly when some NON-[V]-safe row of it is
    # actually LOADED (omega != 0) in some variant; rows with omega = 0 need
    # no validity argument at all.
    if cert['mode'] == '3S':
        omsets = [[frac(x) for x in v['omega_rational']]
                  for v in cert['variants']]
    else:
        omsets = [[frac(x) for x in cert['omega_rational']]]
    need = set()
    for om in omsets:
        for k in range(n):
            if kind[k][0] == 'pair' and not safe[k] and om[k] != 0:
                need.add(kind[k][1])
    ck('B %s every pair loading a non-[V]-safe row is branched' % tag,
       need <= set(branched), 'unbranched: %s' % sorted(need - set(branched)))
    if hprobe is not None and branched:
        bx = box_of(z0, hprobe)
        for pr, axes in branched.items():
            la = live_axes(bx, pr[0], pr[1])
            ck('B %s pair %s live axes covered' % (tag, pr),
               set(la) <= set(axes), 'checker live %s vs cert %s' % (la, axes))
        want = [tuple(tuple(a) for a in c)
                for c in itertools.product(*[branched[tuple(b['pair'])]
                                             for b in cert['branched']])]
        got_v = [tuple(tuple(a) for a in v['choice'])
                 for v in cert['variants']]
        ck('B %s variant list = full product of live axes' % tag,
           sorted(got_v) == sorted(want),
           '%d cert variants vs %d expected' % (len(got_v), len(want)))

    if cert['mode'] == '3S':
        return check_soft(cert, ck, rows, kind, safe, z0, pb, gz, branched,
                          tag, verbose)
    return check_rigid(cert, ck, rows, kind, safe, z0, pb, gz, tag, verbose)


def valid_mask(rows, kind, safe, branched, choice):
    """[O] rows valid in this variant."""
    sel = {}
    for i, pr in enumerate(sorted(branched)):
        sel[pr] = tuple(choice[i])
    ok = []
    for k in range(len(rows)):
        if kind[k][0] in ('wall', 'aux') or safe[k]:
            ok.append(True)
        elif kind[k][1] in sel:
            ok.append(kind[k][2] == sel[kind[k][1]])
        else:
            ok.append(False)
    return ok


def check_soft(cert, ck, rows, kind, safe, z0, pb, gz, branched, tag, verbose):
    n = len(rows)
    s0 = float(z0[S_IDX])
    ck('X %s s_center matches z_center[33]' % tag,
       abs(s0 - cert['claims']['s_center']) < 1e-12)
    order = [tuple(tuple(a) for a in b['axes']) for b in cert['branched']]
    prs = [tuple(b['pair']) for b in cert['branched']]
    vres = []
    for v in cert['variants']:
        om = [frac(x) for x in v['omega_rational']]
        ck('O %s omega length' % tag, len(om) == n)
        sel = dict(zip(prs, [tuple(a) for a in v['choice']]))
        ok = []
        for k in range(n):
            if kind[k][0] in ('wall', 'aux') or safe[k]:
                ok.append(True)
            elif kind[k][1] in sel:
                ok.append(kind[k][2] == sel[kind[k][1]])
            else:
                ok.append(False)
        ck('O %s omega >= 0' % tag, all(x >= 0 for x in om))
        ck('O %s omega = 0 outside the variant valid set' % tag,
           all(om[k] == 0 for k in range(n) if not ok[k]),
           'loaded invalid rows: %s' % [k for k in range(n)
                                        if not ok[k] and om[k] != 0][:6])
        # [W] W0
        W0 = sum_up([abs(float(om[k])) * gz[k] for k in range(n)
                     if om[k] != 0])
        ck('W %s W0' % tag, W0 <= v['W0'] * 1.0000001 + 1e-300,
           'recomputed %.3e vs claimed %.3e' % (W0, v['W0']))
        # [G] r_res
        acc = [iv.mpf(0)] * NV
        for k in range(n):
            if om[k] == 0:
                continue
            okk = cnum(om[k])
            j, vs = row_jet(pb, rows[k], 1)
            for loc, gi in enumerate(vs):
                acc[gi] = acc[gi] + okk * j.g[loc]
        rres = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
                       for gi in range(NV)])
        ck('G %s r_res' % tag, rres <= v['r_res'] * 1.0000001 + 1e-300,
           'recomputed %.3e vs claimed %.3e' % (rres, v['r_res']))
        vres.append((om, W0, rres))

    # [H][V][X] the value table
    for row in cert['claims']['table']:
        h = frac(row['h'])
        hf = float(h)
        box = box_of(z0, h)
        worst = None
        for (om, W0, rres) in vres:
            Hbar = hess_mass(box, rows, om)
            wt = wd = 1e9
            for k in range(n):
                if om[k] == 0 or rows[k]['kind'] != 'edge' or not safe[k]:
                    continue
                t, d = sep_td(box, rows[k])
                wt = min(wt, 0.5 - mag(t))
                wd = min(wd, 0.5 + inf(d))
            V = s0 - W0 - rres * hf - Hbar * hf * hf
            if not (wt > 0 and wd > 0):
                V = min(V, s0 - hf)
            worst = V if worst is None else min(worst, V)
        ck('X %s V_soft(h=%s)' % (tag, row['h']),
           row['V_soft'] <= worst + 1e-13,
           'claimed %.15f vs recomputed %.15f' % (row['V_soft'], worst))
        if verbose:
            print('  [ok] %s h=%-12s V_soft >= %.12f' % (tag, row['h'], worst))
    hm = cert['claims'].get('h_max')
    if hm:
        h = frac(hm)
        hf = float(h)
        box = box_of(z0, h)
        worst = None
        for (om, W0, rres) in vres:
            Hbar = hess_mass(box, rows, om)
            wt = wd = 1e9
            for k in range(n):
                if om[k] == 0 or rows[k]['kind'] != 'edge' or not safe[k]:
                    continue
                t, d = sep_td(box, rows[k])
                wt = min(wt, 0.5 - mag(t))
                wd = min(wd, 0.5 + inf(d))
            V = s0 - W0 - rres * hf - Hbar * hf * hf
            if not (wt > 0 and wd > 0):
                V = min(V, s0 - hf)
            worst = V if worst is None else min(worst, V)
        ck('X %s V(h_max) >= V_max claim' % tag,
           cert['claims']['V_max'] <= worst + 1e-13,
           'claimed %.15f vs recomputed %.15f' % (cert['claims']['V_max'],
                                                  worst))
        ck('X %s V(h_max) beats the incumbent %.6f' % (tag,
                                                       cert['claims']['V_target']),
           worst >= cert['claims']['V_target'],
           'recomputed %.12f' % worst)
        if verbose:
            print('  [ok] %s h_max=%-12s (%.4e) V >= %.12f'
                  % (tag, hm, hf, worst))
    return {'mode': '3S', 'tag': tag}


def check_rigid(cert, ck, rows, kind, safe, z0, pb, gz, tag, verbose):
    n = len(rows)
    P = list(cert['P'])
    Y = [[frac(v) for v in r] for r in cert['Y']]
    om = [frac(x) for x in cert['omega_rational']]
    h = frac(cert['h'])
    hf = float(h)
    cl = cert['claims']
    box = box_of(z0, h)
    ck('O %s omega >= 0' % tag, all(x >= 0 for x in om))
    ck('O %s omega > 0 on every pin row' % tag, all(om[k] > 0 for k in P))
    ck('O %s omega = 0 on non-[V]-safe rows' % tag,
       all(om[k] == 0 for k in range(n) if not safe[k]))
    e0 = sum_up([abs(float(om[k])) * gz[k] for k in range(n) if om[k] != 0])
    gmax = max(gz[k] for k in P)
    ck('Z %s eps_0' % tag, e0 <= cl['eps_0'] * 1.0000001 + 1e-300)
    ck('Z %s g_max' % tag, gmax <= cl['g_max'] * 1.0000001 + 1e-300)
    acc = [iv.mpf(0)] * NV
    for k in range(n):
        if om[k] == 0:
            continue
        okk = cnum(om[k])
        j, vs = row_jet(pb, rows[k], 1)
        for loc, gi in enumerate(vs):
            acc[gi] = acc[gi] + okk * j.g[loc]
    ew = sum_up([mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
                 for gi in range(NV)])
    ck('G %s eps_w' % tag, ew <= cl['eps_w'] * 1.0000001 + 1e-300)
    Hbar = hess_mass(box, rows, om)
    ck('H %s Hbar' % tag, Hbar <= cl['Hbar'] * 1.0000001,
       'recomputed %.6f vs claimed %.6f' % (Hbar, cl['Hbar']))
    grads = []
    for k in P:
        j, vs = row_jet(box, rows[k], 1)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(vs)})
    Yiv = [[cnum(v) for v in r] for r in Y]
    beta = 0.0
    for i in range(NV):
        rs = []
        for j2 in range(NV):
            s = iv.mpf(0)
            for rr in range(NV):
                v = grads[rr].get(j2)
                if v is not None:
                    s = s + Yiv[i][rr] * v
            rs.append(mag((iv.mpf(1) if i == j2 else iv.mpf(0)) - s))
        beta = max(beta, sum_up(rs))
    kappa = max(sum_up([abs(float(Y[i][r])) for r in range(NV)])
                for i in range(NV))
    ck('K %s beta < 1' % tag, beta < 1.0 and beta <= cl['beta'] * 1.0000001,
       'recomputed %.8f vs claimed %.8f' % (beta, cl['beta']))
    ck('K %s kappa' % tag, kappa <= cl['kappa'] * 1.0000001)
    cvec = [max(abs(float(Y[i][r])) for i in range(NV)) for r in range(NV)]
    INF = float('inf')
    keff = (INF if any(om[P[i]] <= 0 for i in range(NV))
            else max(cvec[i] / float(om[P[i]]) for i in range(NV)))
    ck('E %s kappa_eff' % tag, keff <= cl['kappa_eff'] * 1.0000001,
       'recomputed %.6g' % keff)
    E = e0 + ew * hf + Hbar * hf * hf
    psi = ((keff * E + kappa * gmax) / (1.0 - beta)
           if (beta < 1.0 and keff < INF) else INF)
    ck('P %s psi(h) < h' % tag, psi < hf, 'psi/h = %.4g' % (psi / hf))
    x = INF
    if beta < 1.0 and keff < INF:
        x = hf
        C = keff / (1.0 - beta)
        for _ in range(800):
            x = C * (e0 + ew * x + Hbar * x * x) + kappa * gmax / (1.0 - beta)
            if not math.isfinite(x):
                x = INF
                break
    ck('P %s fixed point x* < h' % tag, x < hf, 'x* = %.4g' % x)
    wt = wd = 1e9
    for k in range(n):
        if om[k] == 0 or rows[k]['kind'] != 'edge':
            continue
        t, d = sep_td(box, rows[k])
        wt = min(wt, 0.5 - mag(t))
        wd = min(wd, 0.5 + inf(d))
    ck('V %s loaded sep rows valid on box(h)' % tag, wt > 0 and wd > 0,
       'tangential %.6f, depth+1/2 %.6f' % (wt, wd))
    ck('F %s V <= v_lo - x*' % tag,
       math.isfinite(x) and frac(cl['V']) <= Fraction(cl['v_lo']) - Fraction(x),
       'V %.18f vs v_lo - x* = %.6g' % (float(frac(cl['V'])), cl['v_lo'] - x))
    if verbose:
        print('  [ok] %s h=%-12s beta=%.5f Hbar=%.3f keff=%.3f psi/h=%.4f '
              'x*=%.2e V=%.12f' % (tag, cert['h'], beta, Hbar, keff, psi / hf,
                                   x, float(frac(cl['V']))))
    return {'mode': '3R', 'tag': tag}


def corrupt_cert(cert, mode):
    if cert['mode'] == '3S':
        vs = cert['variants']
        if mode == 'omega-sign':
            for v in vs:
                for k, x in enumerate(v['omega_rational']):
                    if x != '0/1':
                        v['omega_rational'][k] = '-' + x
                        break
        elif mode == 'h-big':
            for t in cert['claims']['table']:
                g = frac(t['h']) * 8
                t['h'] = '%d/%d' % (g.numerator, g.denominator)
            if cert['claims'].get('h_max'):
                g = frac(cert['claims']['h_max']) * 8
                cert['claims']['h_max'] = '%d/%d' % (g.numerator, g.denominator)
        elif mode == 'drop-aux':
            idx = [k for k, e in enumerate(cert['contact_table'])
                   if e['type'] == 'aux']
            rows, kind = rebuild(cert['contact_table'])
            pos = [k for k in range(len(rows)) if kind[k][0] == 'aux']
            # Applicability must be by LOAD, not by position: zeroing an aux
            # row that already carries omega = 0 is a no-op, and reporting it
            # as an applied corruption would overstate the gate's coverage.
            # (Batch A, 2026-08-27: NO 3S certificate loads an aux row, so
            # drop-aux bites only the 3R certificates.)
            if not any(frac(v['omega_rational'][k]) != 0
                       for v in vs for k in pos):
                return False
            for v in vs:
                for k in pos:
                    v['omega_rational'][k] = '0/1'
        elif mode == 'drop-branch':
            rows, kind = rebuild(cert['contact_table'])
            prs = set(tuple(b['pair']) for b in cert['branched'])
            pos = [k for k in range(len(rows))
                   if kind[k][0] == 'pair' and kind[k][1] in prs]
            if not pos:
                return False
            for v in vs:
                for k in pos:
                    v['omega_rational'][k] = '0/1'
        elif mode == 'value-inflate':
            for t in cert['claims']['table']:
                t['V_soft'] += 1e-3
            if cert['claims'].get('V_max') is not None:
                cert['claims']['V_max'] += 1e-3
        else:
            raise SystemExit('unknown corruption mode %s' % mode)
        return True
    # 3R
    if mode == 'omega-sign':
        cert['omega_rational'][cert['P'][0]] = \
            '-' + cert['omega_rational'][cert['P'][0]]
    elif mode == 'h-big':
        g = frac(cert['h']) * 8
        cert['h'] = '%d/%d' % (g.numerator, g.denominator)
    elif mode == 'drop-aux':
        rows, kind = rebuild(cert['contact_table'])
        pos = [k for k in range(len(rows)) if kind[k][0] == 'aux']
        if not any(frac(cert['omega_rational'][k]) != 0 for k in pos):
            return False          # applicability by LOAD, not by position
        for k in pos:
            cert['omega_rational'][k] = '0/1'
    elif mode == 'drop-branch':
        return False
    elif mode == 'value-inflate':
        v = Fraction(round(Fraction(frac(cert['claims']['V']) + Fraction(1,
                     1000)) * 10 ** 30), 10 ** 30)
        cert['claims']['V'] = '%d/%d' % (v.numerator, v.denominator)
    else:
        raise SystemExit('unknown corruption mode %s' % mode)
    return True


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    args = list(sys.argv[1:])
    corrupt = None
    if '--corrupt' in args:
        i = args.index('--corrupt')
        corrupt = args[i + 1]
        del args[i:i + 2]
    cdir = args[0] if args else os.path.join(here, '..', 'results', 'certs')
    files = sorted(glob.glob(os.path.join(cdir, 'fam*.json')))
    if not files:
        print('no certificates in %s' % os.path.abspath(cdir))
        return 1
    if corrupt:
        print('*** CORRUPTION TEST: %s (this run MUST fail) ***' % corrupt)
    print('re-checking %d certificates in %s'
          % (len(files), os.path.abspath(cdir)))
    ck = Check()
    applied = 0
    for f in files:
        cert = json.load(open(f))
        if corrupt:
            if not corrupt_cert(cert, corrupt):
                print('  (%s: corruption %s not applicable)'
                      % (os.path.basename(f), corrupt))
                continue
            applied += 1
        check_cert(cert, ck, verbose=True)
    if corrupt:
        if applied == 0:
            print('corruption test %s: NOT APPLICABLE to any certificate'
                  % corrupt)
            return 3
        bad = bool(ck.fails)
        print('corruption test %s: %s' % (
            corrupt, 'OK (checker failed as required)' if bad
            else 'PROBLEM: checker still passes!'))
        return 0 if bad else 2
    print('  %d certificates, %d checks' % (len(files), ck.n))
    print('=> %s' % ('ALL CHECKS PASS' if not ck.fails
                     else 'FAILURES: %s' % sorted(set(ck.fails))[:8]))
    return 0 if not ck.fails else 1


if __name__ == '__main__':
    sys.exit(main())
