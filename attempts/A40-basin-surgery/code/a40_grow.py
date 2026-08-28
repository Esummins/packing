#!/usr/bin/env python
"""a40_grow.py -- A40 T2: the iterative basin-growth loop.

Implements notes/theory.md exactly:

  rings [h_k, h_{k+1}] from A36's h_0 = 3.7e-3 toward 0.03; per ring, per face
  (i, sgn) of the shell (S6 cover), one of:
    TRIVIAL   the s+ face (S5 remark iv);
    EMPTY     a wall row with sup < 0 on the face sub-box (S5 remark iii);
    ANCHOR    an S5 anchor certificate on unconditionally valid rows;
    BRANCHED  S3 surgery on the pairs whose conditional rows the LP loads:
              per branch combination, an S5 anchor certificate.

  Validity modes per loaded row (recorded in the certificate):
    wall/aux  global ([EX]);
    V         pointwise [V]-rule margins on box(h_out)  (S1) [IV];
    safe      axis inf gap >= 0 on box(h_out)           (S4a) [IV];
    forced    all 7 other axes killed on box(h_out)     (S4b) [IV];
    branch    row of the branch axis; other alive axes are sibling branches,
              killed axes certified                      (S3) [IV].

  Every certificate's MARGIN is assembled in exact Fraction arithmetic from
  [IV] upper bounds:  margin = omega_b h_in - V0 - eps_w h_out - Hbar h_out^2
  and must be > 0.  Hessian masses are [IV] over box(H_REF = 0.035) >= any
  ring box (monotone), per-row triangle bound Hbar <= 0.5 sum omega_r w_r.

Output: results/growth.json + results/certs_a40/ring_XX/*.json
"""
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A40 = os.path.abspath(os.path.join(HERE, '..'))
RESULTS = os.path.join(A40, 'results')
CERTS = os.path.join(RESULTS, 'certs_a40')
sys.path.insert(0, os.path.join(A40, '..', 'A36-levers', 'code'))
sys.path.insert(0, HERE)

import a36_lib as L                       # noqa: E402
import strata_lib as SL                   # noqa: E402
import m2_lib as M                        # noqa: E402
import t3lib                              # noqa: E402
from a40_margins import corner_frame, sup, inf                 # noqa: E402

iv.dps = 60

H0 = Fraction(37, 10000)                 # A36 composed radius 3.7e-3
H_TARGET = Fraction(3, 100)
H_REF = Fraction(35, 1000)               # mass reference box
CHECKPOINTS = [Fraction(1, 100), Fraction(2, 100), Fraction(3, 100)]
RHO0, RHO_MIN = 1.5, 1.02
CAP_W, CAP_B = 200.0, 50.0
OMEGA_DEN = 10 ** 12

CONTACT_PAIRS = [(0, 1), (0, 3), (1, 3), (1, 8), (2, 8), (3, 7), (4, 6),
                 (4, 7), (5, 9), (6, 9), (7, 8), (7, 9), (8, 10), (9, 10)]
NEAR_PAIRS = [(6, 7), (8, 9), (3, 4), (7, 10)]
ALL_PAIRS = CONTACT_PAIRS + NEAR_PAIRS


def pair_axes(i, j):
    return [(i, e, j) for e in range(4)] + [(j, e, i) for e in range(4)]


def fs(x):
    x = Fraction(x)
    return '%d/%d' % (x.numerator, x.denominator)


# ------------------------------------------------------------- the arsenal

class Arsenal:
    def __init__(self):
        K = SL.load_cert()
        self.rows = []                    # (tag, con, kind, pair, axis)
        for r, c in enumerate(K['constraints'][:36]):
            kind = 'wall' if c['kind'] == 'wall' else 'a22edge'
            pr = ax = None
            if kind == 'a22edge':
                pr = tuple(sorted((c['i'], c['j'])))
                ax = (c['j'], c['edge'], c['i'])
            self.rows.append(('a22_%d' % r, dict(c), kind, pr, ax))
        self.rows.append(('aux44', dict(K['constraints'][36]), 'aux',
                          None, None))
        self.rows.append(('aux45', dict(K['constraints'][37]), 'aux',
                          None, None))
        for (i, j) in ALL_PAIRS:
            for (o, e, p) in pair_axes(i, j):
                for k in range(4):
                    tag = 'sep_%d-%d_o%de%dk%d' % (i, j, o, e, k)
                    # skip exact duplicates of a22 edge rows
                    dup = any(c.get('kind') == 'edge' and c['j'] == o and
                              c['edge'] == e and c['i'] == p and
                              c['corner'] == k
                              for (_, c, kk, _, _) in self.rows[:36])
                    if dup:
                        continue
                    self.rows.append((tag, L.edge_con(o, e, p, k), 'sep',
                                      (i, j), (o, e, p)))
        self.n = len(self.rows)
        self.t3 = [SL.to_t3_row(c) for (_, c, _, _, _) in self.rows]
        pb = SL.point_box()
        self.gval_iv = []
        self.jac_iv = []                 # list of dict gi -> iv
        self.A = np.zeros((self.n, 34))
        self.gmid = np.zeros(self.n)
        for k, r in enumerate(self.t3):
            j1 = SL.eval_geo(pb, r, order=1)
            self.gval_iv.append(j1.v)
            self.gmid[k] = 0.5 * (float(iv.mpf(j1.v).a) +
                                  float(iv.mpf(j1.v).b))
            d = {}
            for loc, gi in enumerate(r['vars']):
                d[gi] = j1.g[loc]
                self.A[k, gi] = 0.5 * (float(iv.mpf(j1.g[loc]).a) +
                                       float(iv.mpf(j1.g[loc]).b))
            self.jac_iv.append(d)
        self._mass = {}
        self._hess = {}
        self.by_axis = {}
        for k, (_, _, kind, pr, ax) in enumerate(self.rows):
            if ax is not None:
                self.by_axis.setdefault(ax, []).append(k)

    def masses(self, h_out):
        """Hessian masses (triangle bound) over box(h_out).  [IV] cached,
        together with the per-row interval Hessian entries (self._hess)."""
        key = fs(h_out)
        if key in self._mass:
            return self._mass[key]
        bx = M.box_around(SL.z_hat(), h_out)
        w = np.zeros(self.n)
        hh = []
        for k, r in enumerate(self.t3):
            j2 = SL.eval_geo(bx, r, order=2)
            tot = 0.0
            d = {}
            vs = r['vars']
            for a in range(len(vs)):
                for b in range(len(vs)):
                    tot += M.iv_mag(j2.h[a][b])
                    d[(vs[a], vs[b])] = j2.h[a][b]
            w[k] = tot
            hh.append(d)
        self._mass[key] = w
        self._hess[key] = hh
        return w

    def hessians(self, h_out):
        self.masses(h_out)
        return self._hess[fs(h_out)]


# ------------------------------------------------- per-ring validity pass

class Facts:
    """[IV] validity facts over a given interval box (the full ring box, or a
    face sub-box -- S3 kills and S1 [V] margins are certified on whatever
    region enclosure the certificate declares)."""

    def __init__(self, ars, bx, scope):
        self.scope = scope               # 'ring' or a face label
        self.V_ok = {}
        self.V_margin = {}
        for k, (tag, c, kind, pr, ax) in enumerate(ars.rows):
            if kind not in ('a22edge', 'sep'):
                continue
            t, d = corner_frame(bx, c['j'], c['edge'], c['i'], c['corner'])
            mt = 0.5 - M.iv_mag(t)
            md = 0.5 + inf(d)
            self.V_ok[k] = bool(mt > 0 and md > 0)
            self.V_margin[k] = (mt, md)
        # per-axis gap bounds
        self.axis = {}
        for (i, j) in ALL_PAIRS:
            for (o, e, p) in pair_axes(i, j):
                los, his = [], []
                for k in range(4):
                    _, d = corner_frame(bx, o, e, p, k)
                    los.append(inf(d))
                    his.append(sup(d))
                # witness corner for a kill: the corner with the most
                # negative sup
                kw = int(np.argmin(his))
                self.axis[(o, e, p)] = {
                    'gap_inf': min(los), 'gap_sup': min(his),
                    'killed': bool(min(his) < 0),
                    'safe': bool(min(los) >= 0),
                    'kill_witness_corner': kw,
                    'kill_margin': -his[kw]}
        # pair classification
        self.pair_class = {}
        for (i, j) in ALL_PAIRS:
            axs = pair_axes(i, j)
            alive = [a for a in axs if not self.axis[a]['killed']]
            safes = [a for a in axs if self.axis[a]['safe']]
            if safes:
                cls = ('SAFE', safes, alive)
            elif len(alive) == 1:
                cls = ('FORCED', alive, alive)
            else:
                cls = ('BRANCH', alive, alive)
            self.pair_class[(i, j)] = cls

    def row_status(self, ars, k):
        """'uncond', 'cond', or 'dead' + validity record."""
        tag, c, kind, pr, ax = ars.rows[k]
        if kind in ('wall', 'aux'):
            return 'uncond', {'mode': kind}
        if self.V_ok.get(k):
            return 'uncond', {'mode': 'V', 'scope': self.scope,
                              'tangential_margin': self.V_margin[k][0],
                              'depth_margin': self.V_margin[k][1]}
        cls, sel, alive = self.pair_class[pr]
        if cls == 'SAFE' and ax in sel:
            return 'uncond', {'mode': 'safe', 'scope': self.scope,
                              'gap_inf': self.axis[ax]['gap_inf']}
        if cls == 'FORCED' and ax in sel:
            return 'uncond', {'mode': 'forced', 'scope': self.scope,
                              'axis': list(ax),
                              'killed_axes': self.killed_list(pr)}
        if not self.axis[ax]['killed']:
            return 'cond', {'mode': 'branch', 'scope': self.scope,
                            'axis': list(ax), 'pair': list(pr)}
        return 'dead', {}

    def killed_list(self, pr):
        return [{'axis': list(a),
                 'witness_corner': self.axis[a]['kill_witness_corner'],
                 'kill_margin': self.axis[a]['kill_margin']}
                for a in pair_axes(*pr) if self.axis[a]['killed']]


# ------------------------------------------------------------------ faces

def face_label(i, sgn):
    lab = 's' if i == 33 else 'sq%d.%s' % (i // 3, 'xyt'[i % 3])
    return '%s%s' % (lab, '+' if sgn > 0 else '-')


def face_subbox(i, sgn, h_in, h_out):
    z = SL.z_hat()
    out = []
    for q in range(34):
        lo, hi = z[q] - h_out, z[q] + h_out
        if q == i:
            if sgn > 0:
                lo = z[q] + h_in
            else:
                hi = z[q] - h_in
        out.append(iv.mpf([t3lib._to_iv(lo).a, t3lib._to_iv(hi).b]))
    return out


def try_empty(ars, i, sgn, h_in, h_out):
    bxf = face_subbox(i, sgn, h_in, h_out)
    for k, (tag, c, kind, pr, ax) in enumerate(ars.rows[:36]):
        if kind != 'wall':
            continue
        v = SL.eval_geo(bxf, ars.t3[k], order=0).v
        if sup(v) < 0:
            return {'row': k, 'tag': tag, 'con': c, 'sup': sup(v)}
    return None


ES = np.zeros(34)
ES[33] = 1.0


def face_cut(i, sgn, h_in):
    return {'coeffs': {i: sgn}, 'value': -Fraction(h_in),
            'label': 'face:%s' % face_label(i, sgn)}


def tie_cuts(pr, s, tau):
    """The two sides of the tie split  s*(theta_a - theta_b - ref) <> tau."""
    a, b = pr
    anchor = {'coeffs': {3 * a + 2: s, 3 * b + 2: -s},
              'value': -Fraction(tau),
              'label': 'tie(%d,%d)%+d:anchor' % (a, b, s)}
    cost = {'coeffs': {3 * a + 2: -s, 3 * b + 2: s},
            'value': +Fraction(tau),
            'label': 'tie(%d,%d)%+d:cost' % (a, b, s)}
    return anchor, cost


def anchor_lp(ars, w, cols, cuts, h_out):
    """max  -sum_m omc_m v_m - sum omega_r gval'_r - 0.5 (w.omega) h_out^2
       s.t. A^T omega + sum_m omc_m grad(c_m) = e_s ; bounds.  [LP design]

    cols: list of (k, lb) -- lb None loads row k itself (validity from the
    facts/branch bookkeeping); lb a Fraction loads the FLOOR-SHIFTED row
    g_k - lb (valid on the whole box since lb <= inf_box g_k [IV]), whose
    anchor value is gval_k - lb."""
    m = len(cols)
    nc = len(cuts)
    ks = [c[0] for c in cols]
    Aeq = np.zeros((34, m + nc))
    Aeq[:, :m] = ars.A[ks].T
    for j, ct in enumerate(cuts):
        for q, cf in ct['coeffs'].items():
            Aeq[q, m + j] = cf
    c = np.zeros(m + nc)
    c[:m] = ars.gmid[ks] + 0.5 * w[ks] * float(h_out) ** 2
    for jj, (k, lb, _rf) in enumerate(cols):
        if lb is not None:
            c[jj] -= float(lb)
    for j, ct in enumerate(cuts):
        c[m + j] = float(ct['value'])
    res = linprog(c, A_eq=Aeq, b_eq=ES,
                  bounds=[(0, CAP_W)] * m + [(0, CAP_B)] * nc,
                  method='highs')
    if not res.success:
        return None, None, None
    return -res.fun, res.x[:m], res.x[m:]


def certify(ars, facts, w, cols, om, cuts, omc, i, sgn, h_in, h_out,
            branch_ctx):
    """[IV]+[EX] certification of one anchor certificate.  Returns dict or
    None if the certified margin is not positive."""
    omq = [Fraction(float(x)).limit_denominator(OMEGA_DEN) for x in om]
    ocq = [Fraction(float(x)).limit_denominator(OMEGA_DEN) for x in omc]
    loaded = [(c[0], c[1], c[2], q) for c, q in zip(cols, omq)
              if q > 0]
    # V0 (signed interval sum over geometric rows; floored rows shifted)
    V0 = iv.mpf(0)
    for k, lb, rf_, q in loaded:
        val = ars.gval_iv[k]
        if lb is not None:
            val = val - t3lib._to_iv(lb)
        V0 = V0 + t3lib._to_iv(q) * val
    V0_sup = sup(V0)
    # cut ledger: exact rational  sum_m omc_m * c_m(z-hat)
    cutval = sum((q * ct['value'] for q, ct in zip(ocq, cuts)), Fraction(0))
    # eps_w
    acc = {}
    for k, lb, rf_, q in loaded:
        qi = t3lib._to_iv(q)
        for gi, g in ars.jac_iv[k].items():
            acc[gi] = acc.get(gi, iv.mpf(0)) + qi * g
    for q, ct in zip(ocq, cuts):
        for gi, cf in ct['coeffs'].items():
            acc[gi] = acc.get(gi, iv.mpf(0)) + t3lib._to_iv(q * cf)
    acc[33] = acc.get(33, iv.mpf(0)) - iv.mpf(1)
    eps_w = sum(Fraction(M.iv_mag(v)) for v in acc.values())
    # Hbar: accumulated interval Hessian of W over box(h_out) with the
    # signed-diagonal refinement -- the Taylor remainder needs an UPPER
    # bound of d^T H_W(xi) d, so off-diagonals contribute |.| and diagonals
    # only their positive part
    hh = ars.hessians(h_out)
    accH = {}
    for k, lb, rf_, q in loaded:
        qi = t3lib._to_iv(q)
        for key, v in hh[k].items():
            t = qi * v
            accH[key] = t if key not in accH else accH[key] + t
    hsum = Fraction(0)
    for (a, b), v in accH.items():
        if a == b:
            hsum += Fraction(max(0.0, sup(v)))
        else:
            hsum += Fraction(M.iv_mag(v))
    Hbar = hsum / 2
    margin = (-cutval - Fraction(V0_sup) - eps_w * h_out
              - Hbar * h_out * h_out)
    if margin <= Fraction(1, 10 ** 9):
        return None
    rows_out = []
    for k, lb, rf_, q in loaded:
        if rf_ is not None:
            val = {'mode': 'relfloor', 'lower_bound': fs(lb),
                   'ref_tag': ars.rows[rf_][0],
                   'ref_con': ars.rows[rf_][1],
                   'axis': list(ars.rows[k][4]),
                   'cut_labels': [c['label'] for c in cuts
                                  if not c['label'].startswith('face:')]}
        elif lb is not None:
            val = {'mode': 'floor', 'lower_bound': fs(lb),
                   'scope': 'ring'}
        else:
            st, val = facts.row_status(ars, k)
            if st == 'cond':
                ax = tuple(val['axis'])
                assert branch_ctx is not None and \
                    tuple(branch_ctx.get(tuple(val['pair']), ())) == ax
            assert st != 'dead'
        rows_out.append({'tag': ars.rows[k][0], 'con': ars.rows[k][1],
                         'omega': fs(q), 'validity': val})
    branched = []
    if branch_ctx:
        for pr, ax in branch_ctx.items():
            cls, sel, alive = facts.pair_class[pr]
            branched.append({
                'pair': list(pr), 'branch_axis': list(ax),
                'alive_axes': [list(a) for a in alive],
                'killed_axes': facts.killed_list(pr)})
    claims_eps_w = float(eps_w)
    claims_Hbar = float(Hbar)
    cuts_out = [{'label': ct['label'],
                 'coeffs': {str(q): cf for q, cf in ct['coeffs'].items()},
                 'value': fs(ct['value']), 'omega': fs(qq)}
                for qq, ct in zip(ocq, cuts)]
    return {'type': 'A40-anchor', 'face': {'coord': i, 'sign': sgn,
                                           'label': face_label(i, sgn)},
            'h_in': fs(h_in), 'h_out': fs(h_out),
            'h_in_float': float(h_in), 'h_out_float': float(h_out),
            'h_mass_box': fs(h_out),
            'facts_scope': facts.scope,
            'cuts': cuts_out,
            'rows': rows_out,
            'branched_pairs': branched,
            'claims': {'V0_sup': V0_sup, 'cut_ledger': fs(cutval),
                       'eps_w': claims_eps_w,
                       'Hbar': claims_Hbar, 'margin': float(margin),
                       'margin_frac': fs(margin)}}


NEAR_MISS = 0.35


def empty_lp(ars, w, idx, h_out):
    """[LP] design for the leaf-emptiness certificate: find omega >= 0 on
    leaf-valid rows, sum omega = 1, minimising
        sum omega (gval + 0.5 w h^2) + h ||A^T omega||_1 ;
    optimum < 0 means sup_box sum omega_r g_r < 0 is plausible."""
    m = len(idx)
    hf = float(h_out)
    # vars: omega (m), t (34)
    c = np.zeros(m + 34)
    c[:m] = ars.gmid[idx] + 0.5 * w[idx] * hf * hf
    c[m:] = hf
    Aub = np.zeros((68, m + 34))
    Aub[:34, :m] = ars.A[idx].T
    Aub[:34, m:] = -np.eye(34)
    Aub[34:, :m] = -ars.A[idx].T
    Aub[34:, m:] = -np.eye(34)
    Aeq = np.zeros((1, m + 34))
    Aeq[0, :m] = 1.0
    res = linprog(c, A_ub=Aub, b_ub=np.zeros(68), A_eq=Aeq, b_eq=[1.0],
                  bounds=[(0, None)] * (m + 34), method='highs')
    if not res.success:
        return None, None
    return -res.fun, res.x[:m]


def certify_empty(ars, facts, w, idx, om, i, sgn, h_in, h_out, branch_ctx,
                  extra_cuts):
    """[IV] leaf-emptiness: sup over box(h_out) of sum omega_r g_r < 0 while
    every loaded row is valid (>= 0 on feasible z) on the leaf => the leaf
    region contains no feasible point."""
    omq = [Fraction(float(x)).limit_denominator(OMEGA_DEN) for x in om]
    loaded = [(k, q) for k, q in zip(idx, omq) if q > 0]
    if not loaded:
        return None
    V0 = iv.mpf(0)
    for k, q in loaded:
        V0 = V0 + t3lib._to_iv(q) * ars.gval_iv[k]
    V0_sup = sup(V0)
    acc = {}
    for k, q in loaded:
        qi = t3lib._to_iv(q)
        for gi, g in ars.jac_iv[k].items():
            acc[gi] = acc.get(gi, iv.mpf(0)) + qi * g
    eps_w = sum(Fraction(M.iv_mag(v)) for v in acc.values())
    hh = ars.hessians(h_out)
    accH = {}
    for k, q in loaded:
        qi = t3lib._to_iv(q)
        for key, v in hh[k].items():
            t = qi * v
            accH[key] = t if key not in accH else accH[key] + t
    hsum = Fraction(0)
    for (a, b), v in accH.items():
        if a == b:
            hsum += Fraction(max(0.0, sup(v)))
        else:
            hsum += Fraction(M.iv_mag(v))
    Hbar = hsum / 2
    margin = (-Fraction(V0_sup) - eps_w * h_out - Hbar * h_out * h_out)
    if margin <= Fraction(1, 10 ** 9):
        return None
    rows_out = []
    for k, q in loaded:
        st, val = facts.row_status(ars, k)
        if st == 'cond':
            ax = tuple(val['axis'])
            if branch_ctx is None or \
                    tuple(branch_ctx.get(tuple(val['pair']), ())) != ax:
                return None
        assert st != 'dead'
        rows_out.append({'tag': ars.rows[k][0], 'con': ars.rows[k][1],
                         'omega': fs(q), 'validity': val})
    branched = []
    if branch_ctx:
        for pr, ax in branch_ctx.items():
            cls, sel, alive = facts.pair_class[pr]
            branched.append({
                'pair': list(pr), 'branch_axis': list(ax),
                'alive_axes': [list(a) for a in alive],
                'killed_axes': facts.killed_list(pr)})
    cuts_out = [{'label': ct['label'],
                 'coeffs': {str(q): cf for q, cf in ct['coeffs'].items()},
                 'value': fs(ct['value']), 'omega': '0'}
                for ct in extra_cuts]
    return {'type': 'A40-leaf-empty',
            'face': {'coord': i, 'sign': sgn, 'label': face_label(i, sgn)},
            'h_in': fs(h_in), 'h_out': fs(h_out),
            'h_in_float': float(h_in), 'h_out_float': float(h_out),
            'h_mass_box': fs(h_out), 'facts_scope': facts.scope,
            'cuts': cuts_out, 'rows': rows_out, 'branched_pairs': branched,
            'claims': {'V0_sup': V0_sup, 'eps_w': float(eps_w),
                       'Hbar': float(Hbar), 'margin': float(margin),
                       'margin_frac': fs(margin)}}


def attempt(ars, facts, w, cols, cuts, i, sgn, h_in, h_out, ctx):
    """LP + certification; certification is attempted even on a small
    design-LP deficit because the certified Hbar (accumulated interval
    Hessian, signed diagonal) is sharper than the LP's triangle masses."""
    m, x, c = anchor_lp(ars, w, cols, cuts, h_out)
    if m is None:
        return None, None
    ks = [c[0] for c in cols]
    quad = 0.5 * float(np.dot(w[ks], x)) * float(h_out) ** 2
    if m <= -NEAR_MISS * quad:
        return None, m
    cert = certify(ars, facts, w, cols, x, cuts, c, i, sgn, h_in, h_out, ctx)
    return cert, m


def floor_cols(ars, floors, status, exclude):
    """Floor-shifted columns for every non-unconditional row with a usable
    interval lower bound (Lemma S7): g_k - lb >= 0 on the whole ring box."""
    out = []
    for k in range(ars.n):
        if k in exclude or status[k] == 'uncond':
            continue
        lb = floors[k]
        if lb is not None:
            out.append((k, lb, None))
    return out


# ------------------------------------------------ relative floors (S7')
# For two corner rows of the SAME axis (o, e, p):
#   g_a - g_b = n_e(theta_o) . R(theta_p) (h_ka - h_kb) = f(delta),
#   delta = theta_p - theta_o,   f exact 1-D trig.
# If the sibling g_b is unconditionally valid on the leaf, then for feasible
# z in the leaf:  g_a >= g_b + inf f >= lb_rel := inf_{delta-interval} f.
# The delta-interval comes from the box (+-2 h_out around delta*) refined by
# any tie cut of the leaf on the same angle pair.

def delta_interval(o, p, h_out, extra_cuts):
    z = SL.z_hat()
    dstar = z[3 * p + 2] - z[3 * o + 2]
    lo, hi = -2 * h_out, 2 * h_out          # delta - dstar range
    for ct in extra_cuts:
        cf = ct['coeffs']
        if set(cf) != {3 * o + 2, 3 * p + 2}:
            continue
        # c = sum cf_q (z_q - zhat_q) + value >= 0 on the leaf
        s_p = cf[3 * p + 2]
        v = ct['value']
        if s_p == 1:
            lo = max(lo, -v)                 # (delta-dstar) >= -value
        else:
            hi = min(hi, v)                  # -(delta-dstar) >= -value
    return dstar, lo, hi


def rel_floor(ars, o, e, p, ka, kb, dstar, dlo, dhi):
    """[IV] inf of f over delta in dstar + [dlo, dhi]."""
    ux = HALF[ka][0] - HALF[kb][0]
    uy = HALF[ka][1] - HALF[kb][1]
    nhx, nhy = NHAT[e]
    dd = t3lib._to_iv(dstar) + iv.mpf([t3lib._to_iv(dlo).a,
                                       t3lib._to_iv(dhi).b])
    cd, sd = iv.cos(dd), iv.sin(dd)
    # n_hat . R(delta) u  (both in owner body frame)
    rx = cd * t3lib._to_iv(ux) - sd * t3lib._to_iv(uy)
    ry = sd * t3lib._to_iv(ux) + cd * t3lib._to_iv(uy)
    f = iv.mpf(nhx) * rx + iv.mpf(nhy) * ry
    return Fraction(inf(f))


HALF = M.HALF
NHAT = M.NHAT


def relfloor_cols(ars, facts, status, exclude, h_out, extra_cuts):
    """S7' columns: (k, lb_rel, ref_k) for conditional/dead sep rows whose
    axis has a pointwise-[V]-valid sibling corner row (the checker re-verifies
    the sibling by S1 on the face sub-box)."""
    out = []
    for ax, rows_of_ax in ars.by_axis.items():
        sibs = [k for k in rows_of_ax
                if status[k] == 'uncond' and facts.V_ok.get(k)]
        if not sibs:
            continue
        # the sibling with the best chance is any uncond one; take first
        o, e, p = ax
        dstar, dlo, dhi = delta_interval(o, p, h_out, extra_cuts)
        if dlo > dhi:
            continue
        for k in rows_of_ax:
            if k in exclude or status[k] == 'uncond':
                continue
            kb = sibs[0]
            ka = ars.rows[k][1]['corner']
            kbc = ars.rows[kb][1]['corner']
            lb = rel_floor(ars, o, e, p, ka, kbc, dstar, dlo, dhi)
            if lb > Fraction(-35, 100):
                out.append((k, lb, kb))
    return out


def do_face(ars, rf, w, floors, i, sgn, h_in, h_out):
    """Returns (mode, certs, info) or (None, None, failure-info)."""
    if i == 33 and sgn > 0:
        return 'TRIVIAL', [], {}
    er = try_empty(ars, i, sgn, h_in, h_out)
    if er is not None:
        cert = {'type': 'A40-empty',
                'face': {'coord': i, 'sign': sgn,
                         'label': face_label(i, sgn)},
                'h_in': fs(h_in), 'h_out': fs(h_out),
                'h_in_float': float(h_in), 'h_out_float': float(h_out),
                'empty_row': {'tag': er['tag'], 'con': er['con'],
                              'sup': er['sup']}}
        return 'EMPTY', [cert], {}
    fcut = [face_cut(i, sgn, h_in)]
    # tier 1: ring-level unconditional rows + floor-shifted rows (S7)
    status = {k: rf.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    cols = ([(k, None, None) for k in unc]
            + floor_cols(ars, floors, status, set(unc)))
    cert, mA = attempt(ars, rf, w, cols, fcut, i, sgn, h_in, h_out, None)
    if cert is not None:
        return 'ANCHOR', [cert], {'design_margin': mA}
    # tier 2: face-level facts (kills/[V] on the face SUB-box; S3 on the
    # actual region is sharper than on the full ring box)
    ff = Facts(ars, face_subbox(i, sgn, h_in, h_out), face_label(i, sgn))
    status = {k: ff.row_status(ars, k)[0] for k in range(ars.n)}
    unc = [k for k in range(ars.n) if status[k] == 'uncond']
    cols = ([(k, None, None) for k in unc]
            + floor_cols(ars, floors, status, set(unc)))
    cert, mA = attempt(ars, ff, w, cols, fcut, i, sgn, h_in, h_out, None)
    if cert is not None:
        return 'ANCHOR-F', [cert], {'design_margin': mA}
    # tier 3: recursive branch-and-certify (pair surgery + tie cuts)
    _deadline[0] = time.time() + FACE_BUDGET
    res = branch_certify(ars, ff, w, floors, status, unc, {}, [], i, sgn,
                         h_in, h_out, 0, {})
    _deadline[0] = None
    if isinstance(res, dict):
        return None, None, res
    prs = sorted({tuple(b['pair']) for c in res for b in c['branched_pairs']})
    ncut = max((len(c['cuts']) for c in res), default=1) - 1
    return 'BRANCHED', res, {'pairs': [list(p) for p in prs],
                             'n_branches': len(res), 'max_tie_cuts': ncut}


MAX_DEPTH = 14
MAX_LEAVES = 512
PAIR_TRIES = 3
FACE_BUDGET = 90.0                    # seconds of tier-3 search per face
_deadline = [None]


def branch_certify(ars, ff, w, floors, status, unc, ctx, extra_cuts, i, sgn,
                   h_in, h_out, depth, memo):
    """Memoising wrapper: identical (ctx, cuts) subproblems reached along
    different search orders are solved once."""
    if _deadline[0] is not None and time.time() > _deadline[0]:
        return {'fail': 'face search budget exhausted',
                'branch': {str(pr): list(ax) for pr, ax in ctx.items()}}
    key = (frozenset(ctx.items()),
           frozenset((c['label'], str(c['value'])) for c in extra_cuts))
    if key in memo:
        return memo[key]
    res = _branch_certify(ars, ff, w, floors, status, unc, ctx, extra_cuts,
                          i, sgn, h_in, h_out, depth, memo)
    if not (isinstance(res, dict) and
            res.get('fail') == 'face search budget exhausted'):
        memo[key] = res
    return res


def _branch_certify(ars, ff, w, floors, status, unc, ctx, extra_cuts, i, sgn,
                    h_in, h_out, depth, memo):
    """Certify the face region restricted to branch context ctx (pair ->
    chosen axis) and the tie cuts in extra_cuts.  Returns a list of
    certificates, or a failure dict."""
    sel = list(unc)
    for pr, ax in ctx.items():
        sel += [k for k in ars.by_axis.get(ax, ())
                if status[k] == 'cond']
    cols = ([(k, None, None) for k in sel]
            + floor_cols(ars, floors, status, set(sel))
            + relfloor_cols(ars, ff, status, set(sel), h_out, extra_cuts))
    cuts = [face_cut(i, sgn, h_in)] + extra_cuts
    cert, mC = attempt(ars, ff, w, cols, cuts, i, sgn, h_in, h_out,
                       ctx or None)
    if cert is not None:
        return [cert]
    # leaf-emptiness certificate: a nonneg combination of leaf-valid rows
    # provably negative on the whole sub-box => no feasible point in leaf
    mE, xE = empty_lp(ars, w, sel, h_out)
    if mE is not None and mE > -5e-5:
        certE = certify_empty(ars, ff, w, sel, xE, i, sgn, h_in, h_out,
                              ctx or None, extra_cuts)
        if certE is not None:
            return [certE]
    fail = {'fail': 'branch margin <= 0',
            'branch': {str(pr): list(ax) for pr, ax in ctx.items()},
            '_pairs': list(ctx.keys()),
            'cuts': [c['label'] for c in extra_cuts],
            'margin': mC}
    if depth >= MAX_DEPTH:
        fail['fail'] = 'branch margin <= 0 at max depth'
        return fail
    # option (a): extend with conditional rows of pairs not yet branched.
    # SAFE pairs are never branch candidates: their safe-axis rows are
    # already unconditional and their remaining alive axes are typically
    # unkillable (well-separated directions), so branching them explodes
    # the tree for no gain -- their other rows remain reachable as floors.
    others = [k for k in range(ars.n)
              if status[k] == 'cond' and ars.rows[k][3] not in ctx and
              ff.pair_class[ars.rows[k][3]][0] != 'SAFE']
    full_cols = cols + [(k, None, None) for k in others]
    mD, xD, _ = anchor_lp(ars, w, full_cols, cuts, h_out)
    weight = {}
    if xD is not None:
        for (k, lb, _rf), q in zip(full_cols, xD):
            if lb is None and q > 1e-9 and status[k] == 'cond' and \
                    ars.rows[k][3] not in ctx:
                weight[ars.rows[k][3]] = \
                    weight.get(ars.rows[k][3], 0.0) + q
    if mD is not None and mD > 0:
        for pr_new in sorted(weight, key=weight.get,
                             reverse=True)[:PAIR_TRIES]:
            alive = ff.pair_class[pr_new][2]
            out = []
            sub_fail = None
            for ax in alive:
                ctx2 = dict(ctx)
                ctx2[pr_new] = ax
                sub = branch_certify(ars, ff, w, floors, status, unc, ctx2,
                                     extra_cuts, i, sgn, h_in, h_out,
                                     depth + 1, memo)
                if isinstance(sub, dict):
                    sub_fail = sub
                    break
                out += sub
                if len(out) > MAX_LEAVES:
                    return {'fail': 'branch leaf cap', 'n': len(out)}
            if sub_fail is None:
                return out
            fail = sub_fail
    # option (b): tie-cut surgery -- split on a relative-angle functional
    # (restricted to pairs touching the face's square, plus branched pairs;
    # near the top of the tree, or when option (a) provably cannot help --
    # the all-conditional LP is itself non-positive)
    if len(extra_cuts) < 2 and (len(ctx) <= 1 or mD is None or mD <= 0):
        sq = i // 3 if i < 33 else None
        wpairs = sorted(weight, key=weight.get, reverse=True)
        # pairs whose raw conditional rows the mixed LP wants, then the
        # pairs of the failing subtree (deepest first), then face pairs
        fp = list(reversed(fail.get('_pairs', [])))
        already_cut = {tuple(sorted((int(q) - 2) // 3
                                    for q in c['coeffs']))
                       for c in extra_cuts}
        cand_pairs = []
        for pr in wpairs + fp + [pr for pr in ALL_PAIRS if sq in pr]:
            if pr not in cand_pairs and pr not in already_cut:
                cand_pairs.append(pr)
        cand_pairs = cand_pairs[:5]
        taus = (2, 8) if len(ctx) <= 1 else (8,)
        for pr in cand_pairs:
            for s in (+1, -1):
                for tau_div in taus:
                    tau = h_in / tau_div
                    anc, cst = tie_cuts(pr, s, tau)
                    ok_both = []
                    for side in (anc, cst):
                        sub = branch_certify(
                            ars, ff, w, floors, status, unc, ctx,
                            extra_cuts + [side], i, sgn, h_in, h_out,
                            max(depth + 1, MAX_DEPTH - 1), memo)
                        if isinstance(sub, dict):
                            ok_both = None
                            break
                        ok_both += sub
                    if ok_both is not None:
                        return ok_both
    return fail


FLOOR_MIN = -0.35


def ring_floors(ars, h_out):
    """[IV] lower bound of every row over box(h_out); the floor-shifted row
    g - lb is then valid on the whole box (Lemma S7)."""
    bx = M.box_around(SL.z_hat(), h_out)
    out = []
    for k, r in enumerate(ars.t3):
        v = SL.eval_geo(bx, r, order=0).v
        lo = inf(v)
        out.append(Fraction(lo) if lo > FLOOR_MIN else None)
    return out


def main():
    t0 = time.time()
    os.makedirs(CERTS, exist_ok=True)
    # wipe stale certificates (rings are rewritten from scratch each run)
    import shutil
    for d in sorted(os.listdir(CERTS)):
        p = os.path.join(CERTS, d)
        if d.startswith('ring_') and os.path.isdir(p):
            shutil.rmtree(p)
    print('building arsenal...')
    ars = Arsenal()
    print('  %d rows (%.1f s)' % (ars.n, time.time() - t0))
    h = H0
    ring = 0
    rho = RHO0
    log = {'meta': {'task': 'A40 basin growth', 'dps': 60, 'h0': fs(H0),
                    'target': fs(H_TARGET), 'mass_ref': fs(H_REF),
                    'omega_denominator': OMEGA_DEN},
           'rings': [], 'saturation': None}
    while h < H_TARGET:
        h_next = min(Fraction(h * Fraction(rho).limit_denominator(100)
                              ).limit_denominator(10 ** 6), H_TARGET)
        for cp in CHECKPOINTS:
            if h < cp < h_next:
                h_next = cp
        t1 = time.time()
        rf = Facts(ars, M.box_around(SL.z_hat(), h_next), 'ring')
        wm = ars.masses(h_next)
        floors = ring_floors(ars, h_next)
        ringrec = {'ring': ring, 'h_in': fs(h), 'h_out': fs(h_next),
                   'h_in_float': float(h), 'h_out_float': float(h_next),
                   'faces': {}, 'n_certs': 0}
        ok = True
        fail_info = None
        for i in range(34):
            for sgn in (+1, -1):
                mode, certs, info = do_face(ars, rf, wm, floors, i, sgn,
                                            h, h_next)
                if mode is None:
                    ok = False
                    fail_info = {'face': face_label(i, sgn), **info}
                    break
                ringrec['faces'][face_label(i, sgn)] = {
                    'mode': mode, 'n_certs': len(certs), **info}
                ringrec['n_certs'] += len(certs)
                ringrec.setdefault('_certs', []).append(certs)
            if not ok:
                break
        if not ok:
            if rho > RHO_MIN:
                rho = max(RHO_MIN, math.sqrt(rho))
                print('ring %d at h_out=%.5f FAILED (%s); retry rho=%.3f'
                      % (ring, float(h_next), fail_info, rho))
                continue
            log['saturation'] = {'h': float(h), 'h_frac': fs(h),
                                 'detail': fail_info}
            print('SATURATION at h = %.6f: %s' % (float(h), fail_info))
            break
        # persist ring certificates
        rdir = os.path.join(CERTS, 'ring_%02d' % ring)
        os.makedirs(rdir, exist_ok=True)
        minmarg = None
        for certs in ringrec.pop('_certs'):
            for c in certs:
                nm = c['face']['label'].replace('.', '_')
                suffix = ''
                if c.get('branched_pairs'):
                    suffix = '_' + '-'.join(
                        'b%d%d_o%de%d' % (b['pair'][0], b['pair'][1],
                                          b['branch_axis'][0],
                                          b['branch_axis'][1])
                        for b in c['branched_pairs'])
                for ct in c.get('cuts', []):
                    if ct['label'].startswith('face:'):
                        continue
                    suffix += '_' + (ct['label'].replace('(', '')
                                     .replace(')', '').replace(',', '_')
                                     .replace(':', '_').replace('+', 'p')
                                     .replace('-', 'm'))
                fn = os.path.join(rdir, '%s%s.json' % (nm, suffix))
                with open(fn, 'w') as f:
                    json.dump(c, f, indent=1)
                if c['type'] == 'A40-anchor':
                    mm = c['claims']['margin']
                    minmarg = mm if minmarg is None else min(minmarg, mm)
        ringrec['min_anchor_margin'] = minmarg
        ringrec['wall_s'] = time.time() - t1
        log['rings'].append(ringrec)
        nmodes = {}
        for v in ringrec['faces'].values():
            nmodes[v['mode']] = nmodes.get(v['mode'], 0) + 1
        print('ring %2d  [%.5f -> %.5f]  %s  certs=%d  minmarg=%.3g  %.1fs'
              % (ring, float(h), float(h_next), nmodes, ringrec['n_certs'],
                 minmarg if minmarg is not None else float('nan'),
                 ringrec['wall_s']))
        h = h_next
        ring += 1
        if rho < RHO0:
            rho = min(RHO0, rho * 1.15)
    log['h_reached'] = float(h)
    log['h_reached_frac'] = fs(h)
    log['n_rings'] = ring
    log['n_certs_total'] = sum(r['n_certs'] for r in log['rings'])
    log['meta']['wall_seconds'] = time.time() - t0
    with open(os.path.join(RESULTS, 'growth.json'), 'w') as f:
        json.dump(log, f, indent=1)
    print('h reached: %.6f  rings=%d  certs=%d  wall=%.1fs'
          % (log['h_reached'], ring, log['n_certs_total'],
             log['meta']['wall_seconds']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
