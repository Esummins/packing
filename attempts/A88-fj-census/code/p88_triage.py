"""triage88.py -- A88 TIER 1: cheap per-structure triage.

T1a  combinatorial : recompute m, k_H, chi = m - (3 k_H + 1), rigid-possible.
T1b  realisability relaxation (the "realisability LP").

  With the tilt CLASSES confined to interval bins every row of H is
  INTERVAL-LINEAR in the centres and s:

      row(v) = sum_i a_i v_i + K ,   a_i in [a_i^-, a_i^+],  K in [K^-, K^+]

  (a_i and K enclose the trig entries over the tilt bins).  Split each
  coefficient interval into midpoint + radius, a_i = ac_i +- r_i, and bound the
  radius part by its worst case over the CENTRE BOX:

      | row(v) - (sum ac_i v_i + Kc) |  <=  sum_i r_i * Vmax_i + Krad  =:  E

  where Vmax_i = max(|lo_i|, |hi_i|) over the variable's box range.  The
  equality row = 0 is therefore RELAXED to the two linear inequalities

      sum ac_i v_i + Kc <= E      and     -(sum ac_i v_i + Kc) <= E .

  Every genuine realisation of H with tilts in the bins satisfies both, so LP
  infeasibility => H has NO realisation in that tilt bin.  This is a sound
  OUTER relaxation (it can only fail to kill; it can never kill a realisable
  structure).

  Containment rows use the one-sided sound bound: q = v + A with A in [Al, Ah]
  and the true A somewhere inside, so q >= 0 implies v + Ah >= 0 and q <= s
  implies v + Al <= s.

  The LP actually solved is the margin form

      max t   s.t.   (relaxed rows) + t <= rhs,   t in [-10, 1]

  which is always feasible, so HiGHS always returns a dual; t* < -1e-9 is the
  KILL and |t*| is the kill margin.  The duals on the row inequalities are the
  Farkas weights and are aggregated by row family.

KILL TYPE: a killing leaf is re-solved with s in [1, 5] instead of
[3.82, s-hat_hi].  Still infeasible => CONTAINMENT-type (unrealisable at any
side, A59's diagnosis).  Feasible => S-HAT-type (the kill uses the side bound).

No certificate is emitted: fastiv float intervals with outward padding.
"""
from __future__ import annotations

import math
import time

import numpy as np
from scipy.optimize import linprog

import p88_iv as F
import p88_rows as R
import p88_struct as S

HALFPI = math.pi / 2.0
KILL_TOL = 1e-9


def lp_index(st):
    """LP variables = centres + s (tilts are bins, not LP variables)."""
    idx = {}
    n = 0
    for i in st.loaded:
        idx[st.ix[('cx', i)]] = n; n += 1
        idx[st.ix[('cy', i)]] = n; n += 1
    idx[st.ix[('s',)]] = n; n += 1
    return idx, n


def build_lp(st, box, lpidx, nv, ztol=1e-12):
    """Returns (A_ub, b_ub, bounds, fams) or None if a coefficient-free row is
    already violated (immediate infeasibility)."""
    bounds = [None] * (nv + 1)
    vmax = [0.0] * nv
    for core, j in lpidx.items():
        lo, hi = box[core]
        bounds[j] = (lo, hi)
        vmax[j] = max(abs(lo), abs(hi))
    bounds[nv] = (-10.0, 1.0)

    A = []; b = []; fams = []
    for r in st.rows:
        coef, K = R.lin_row(st, box, r)
        if not coef:
            if not F.contains0(K, ztol):
                return None, ('dom_row', r['kind'])
            continue
        row = np.zeros(nv + 1)
        E = 0.5 * (K[1] - K[0]) + ztol
        Kc = 0.5 * (K[0] + K[1])
        for core, a in coef.items():
            j = lpidx[core]
            row[j] = 0.5 * (a[0] + a[1])
            E += 0.5 * (a[1] - a[0]) * vmax[j]
        row[nv] = 1.0
        A.append(row.copy()); b.append(E - Kc); fams.append(r['kind'])
        row2 = -row; row2[nv] = 1.0
        A.append(row2); b.append(E + Kc); fams.append(r['kind'])

    # inequality rows (rebuilt t3lib dominance rows): g >= 0, so the SOUND
    # necessary condition is that the UPPER end of the relaxed value be >= 0
    for r in getattr(st, 'ineq', ()):
        coef, K = R.lin_row(st, box, r)
        E = 0.5 * (K[1] - K[0]) + ztol
        Kc = 0.5 * (K[0] + K[1])
        if not coef:
            if K[1] + ztol < 0.0:
                return None, ('dom_ineq', r['kind'])
            continue
        row = np.zeros(nv + 1)
        for core, a in coef.items():
            j = lpidx[core]
            row[j] = -0.5 * (a[0] + a[1])
            E += 0.5 * (a[1] - a[0]) * vmax[j]
        row[nv] = 1.0
        A.append(row); b.append(E + Kc); fams.append('ineq_' + r['kind'])

    # containment: every corner of every LOADED square in [0, s]
    js = lpidx[st.ix[('s',)]]
    for i in st.loaded:
        for c in range(4):
            for axis in ('x', 'y'):
                core, Aiv = R.corner_lin(st, box, i, c, axis)
                j = lpidx[core]
                row = np.zeros(nv + 1); row[j] = -1.0; row[nv] = 1.0
                A.append(row); b.append(Aiv[1]); fams.append('contain_lo')
                row = np.zeros(nv + 1); row[j] = 1.0; row[js] -= 1.0
                row[nv] = 1.0
                A.append(row); b.append(-Aiv[0]); fams.append('contain_hi')
    return (np.array(A), np.array(b), bounds, fams), None


def solve_leaf(st, box, lpidx, nv, want_dual=False, ztol=1e-12):
    built, why = build_lp(st, box, lpidx, nv, ztol)
    if built is None:
        return {'infeasible': True, 'margin': float('inf'), 'reason': why[0]}
    A, b, bounds, fams = built
    c = np.zeros(nv + 1); c[nv] = -1.0
    r = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if not r.success:
        return {'infeasible': True, 'margin': float('inf'), 'reason': 'lp_' + str(r.status)}
    t = -r.fun
    out = {'infeasible': bool(t < -KILL_TOL), 'margin': float(t), 'reason': 'lp'}
    if want_dual and out['infeasible']:
        try:
            mg = np.abs(np.asarray(r.ineqlin.marginals))
            agg = {}
            for f, w in zip(fams, mg):
                agg[f] = agg.get(f, 0.0) + float(w)
            # variable-BOUND duals: the wall-tightened centre box and the
            # s-hat side bound enter as bounds, not as rows
            js = lpidx[st.ix[('s',)]]
            bl = np.abs(np.asarray(r.lower.marginals))
            bu = np.abs(np.asarray(r.upper.marginals))
            agg['box_s'] = float(bl[js] + bu[js])
            agg['box_centre'] = float(bl.sum() + bu.sum() - agg['box_s']
                                      - bl[nv] - bu[nv])
            tot = sum(agg.values())
            out['dual_by_family'] = {k: (v / tot if tot > 0 else 0.0)
                                     for k, v in sorted(agg.items())}
            resid = float(np.max(A.dot(np.append(r.x[:nv], r.x[nv])) - b))
            out['dual_residual'] = resid
        except Exception as e:                                   # pragma: no cover
            out['dual_err'] = str(e)
    return out


def bisect_class(st, box, c):
    """Split the bin of free class c in half; returns two boxes."""
    j = st.ix[('th', c)]
    lo, hi = box[j]
    mid = 0.5 * (lo + hi)
    a = list(box); a[j] = (lo, mid)
    b = list(box); b[j] = (mid, hi)
    return a, b


def triage_structure(st, s_lo=S.S_LO, s_hi=S.S_HAT_HI, max_levels=3,
                     max_leaves=64, want_dual=True, ztol=1e-12):
    t0 = time.time()
    lpidx, nv = lp_index(st)
    root = st.core_box(s_lo, s_hi)
    frontier = [(root, 0)]
    leaves = 0
    killed = 0
    order_pruned = 0
    survivor_box = None
    dual_fam = {}
    margins = []
    while frontier:
        box, lvl = frontier.pop()
        if not st.order_consistent(box):
            order_pruned += 1
            leaves += 1
            continue
        res = solve_leaf(st, box, lpidx, nv, want_dual=want_dual, ztol=ztol)
        margins.append(res['margin'] if math.isfinite(res['margin']) else 1e9)
        if res['infeasible']:
            leaves += 1
            killed += 1
            for k, v in (res.get('dual_by_family') or {}).items():
                dual_fam[k] = dual_fam.get(k, 0.0) + v
            continue
        if lvl >= max_levels or leaves + len(frontier) + 2 > max_leaves \
                or not st.free_cls:
            leaves += 1
            survivor_box = box
            break
        # bisect the widest free class bin
        c = max(st.free_cls, key=lambda cc: box[st.ix[('th', cc)]][1]
                - box[st.ix[('th', cc)]][0])
        if box[st.ix[('th', c)]][1] - box[st.ix[('th', c)]][0] < 1e-6:
            leaves += 1
            survivor_box = box
            break
        a, b = bisect_class(st, box, c)
        frontier.append((a, lvl + 1)); frontier.append((b, lvl + 1))
    ms = 1000.0 * (time.time() - t0)
    verdict = 'KILL' if survivor_box is None else 'SURVIVE'
    tot = sum(dual_fam.values()) or 1.0
    return {'verdict': verdict, 'ms': ms, 'leaves': leaves,
            'killed_leaves': killed, 'order_pruned': order_pruned,
            'best_margin': (max(margins) if margins else None),
            'dual_by_family': {k: v / tot for k, v in sorted(dual_fam.items())},
            'survivor_box': survivor_box}


def kill_type(st, max_levels=3, max_leaves=64, ztol=1e-12):
    """Re-run the triage with the s-hat side bound dropped (s in [1, 5])."""
    r = triage_structure(st, s_lo=1.0, s_hi=5.0, max_levels=max_levels,
                         max_leaves=max_leaves, want_dual=False, ztol=ztol)
    return ('CONTAINMENT' if r['verdict'] == 'KILL' else 'S-HAT'), r


def run(st, max_levels=3, max_leaves=64, ztol=1e-12):
    out = {'tag': st.tag, 'ztol': ztol}
    out.update(st.summary())
    t1 = triage_structure(st, max_levels=max_levels, max_leaves=max_leaves,
                          ztol=ztol)
    out['t1b'] = {k: v for k, v in t1.items() if k != 'survivor_box'}
    out['verdict'] = t1['verdict']
    if t1['verdict'] == 'KILL':
        kt, r2 = kill_type(st, max_levels, max_leaves, ztol)
        out['kill_type'] = kt
        out['t1b_nosbound'] = {k: v for k, v in r2.items()
                               if k not in ('survivor_box', 'dual_by_family')}
        out['ms_total'] = t1['ms'] + r2['ms']
    else:
        out['kill_type'] = None
        out['ms_total'] = t1['ms']
    return out
