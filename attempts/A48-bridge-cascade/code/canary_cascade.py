#!/usr/bin/env python
"""A48 CANARY -- cascade-theory premises vs ALL 36 A37 atlas entries.

FLOAT-ONLY (the atlas stores theta in radians; every number below is float64).
This is an EMPIRICAL consistency canary, never an input to a certified verdict.

Checks
  1. all 36 entries: family_id + class; the 24 NOT-CP entries are marked
     "vacuous (not a critical point)".
  2. the 12 genuine entries (RIGID / VALLEY / VALLEY-MARGINAL): reconstruct the
     contact classification with A46's task1 machinery (WF/FL/CE/WC/CC) and
     count the FLUSH rows.  Every genuine entry must have >= 1 flush row, so
     the flush-free hypothesis of every A48 statement is VACUOUS on it.
  3. THE REAL CANARY -- Theorem W1.2 (A46 notes/w1_theory.md sect. 2).  Fix ONE
     FJ certificate (the lambda0 = 1 min-sum LP vertex, A44 convention).  For
     every LOADED CE or WC row (a, b) with corner q, and every other loaded row
     k involving a, compute tau_k = cross(p_k - q, n_k) with n_k the unit force
     direction ON a.  Then either both signs occur among the loaded tau
     (a blocker exists) or all loaded tau vanish (pencil).  W1.2 is a THEOREM
     at any FJ point, so a failure = a sign-convention bug here.
     Two independent tau computations are compared:
       tau_geo  = cross(p_k - q, n_k)                     (W1.1 statement)
       tau_grad = contraction of grad_a g_k with the rotation flow about q
                  = -gx*(cay-qy) + gy*(cax-qx) + gth      (W1.1 proof)
     plus the identity residual  |Sum_k lambda_k tau_k|  (must be ~ 0).
  4. NEGATIVE CONTROL: rerun check 3 with n_k negated on RECEIVED rows (another
     body's corner resting on a's edge).  The dichotomy must then FAIL.
  5. blocker-type tally: what actually blocks near-flush contacts here.

Reads:  attempts/A37-cp-atlas/results/atlas_final.json (via A44 eval_atlas)
Writes: attempts/A48-bridge-cascade/results/canary_cascade.json
        attempts/A48-bridge-cascade/logs/canary_run.txt (appended)

No file outside attempts/A48-bridge-cascade is written or modified.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A48 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A48, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..'))
A44C = os.path.join(ATT, 'A44-fj-maxwell', 'code')
A46C = os.path.join(ATT, 'A46-balanced-wedge', 'code')
sys.path.insert(0, A44C)
sys.path.insert(0, A46C)

import a44_geom as G                                          # noqa: E402
import eval_atlas as EA                                       # noqa: E402
import task1_audit as T1                                      # noqa: E402

RES = os.path.join(A48, 'results')
LOGS = os.path.join(A48, 'logs')
GENUINE = ('RIGID', 'VALLEY', 'VALLEY-MARGINAL')

TOL_C = 1e-6          # contact / geometric tolerance (A46 task 1)
LP_TOL = 1e-7         # lambda_k > LP_TOL  =>  row is LOADED in this certificate
TAU_TOL = 1e-7        # |tau| <= TAU_TOL  =>  torque is zero (unit torques)
IDENT_TOL = 1e-6      # |Sum lambda tau| tolerance

WALL_IN = {'x=0': (1.0, 0.0), 'y=0': (0.0, 1.0),
           'x=s': (-1.0, 0.0), 'y=s': (0.0, -1.0)}


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


# ------------------------------------------------------- row -> (p, n, owner)
def row_actors(z, r):
    """Squares whose coordinates the row touches, each with (p, n_on_that_sq).

    p = contact point, n = UNIT force direction ON that square.
      wall row : square i, p = its corner, n = inward wall normal.
      edge row : corner `corner` of square i rests on edge `edge` of owner j.
                 force on i is the owner's outward edge normal nu (points INTO
                 i); force on j is -nu, applied at the same point p.
    """
    if r['kind'] == 'wall':
        p = G.corner(z, r['i'], r['corner'])
        return {r['i']: (p, WALL_IN[r['wall']], 'rest_wall')}
    if r['kind'] == 'edge':
        p = G.corner(z, r['i'], r['corner'])
        nu = G.normal(z, r['j'], r['edge'])
        return {r['i']: (p, nu, 'rest'),
                r['j']: (p, (-nu[0], -nu[1]), 'recv')}
    raise ValueError(r['kind'])


def tau_geo(z, r, a, q, flip_recv=False):
    """cross(p - q, n) for the force on square a; None if a is not in the row."""
    act = row_actors(z, r)
    if a not in act:
        return None, None
    p, n, role = act[a]
    if flip_recv and role == 'recv':
        n = (-n[0], -n[1])
    return cross((p[0] - q[0], p[1] - q[1]), n), role


def tau_grad(z, r, a, q):
    """W1.1 by contraction: rotate a alone about q with omega = 1."""
    g = G.row_grad(z, r)
    cax, cay = z[3 * a], z[3 * a + 1]
    return (-g[3 * a] * (cay - q[1]) + g[3 * a + 1] * (cax - q[0])
            + g[3 * a + 2])


# ------------------------------------------------------- per-entry machinery
def certificate(entry, z):
    """One FJ certificate at lambda0 = 1 (A44 min-sum LP vertex).

    Returns (rows, owner, lam, st, lp_used) or (..., None, ..., 'infeasible').
    """
    st = EA.build_structure(entry, z)
    cols = EA.col_index(st['core'])
    rows, owner = EA.physical_rows(st, 'fact0')
    A = EA.jac(z, rows, cols)
    lam, _ = EA.lp_feasible(A)
    if lam is not None:
        return rows, owner, lam, st, 'physical', A
    rows, owner = EA.expanded_rows(st)
    A = EA.jac(z, rows, cols)
    lam, _ = EA.lp_feasible(A)
    if lam is not None:
        return rows, owner, lam, st, 'expanded', A
    return rows, owner, None, st, 'infeasible', A


def contact_classes(z, s):
    """A46 task-1 geometric classification, keyed by edge.

    ('pair', i, j) -> record ; ('wall', i, wall) -> record
    """
    sq = [T1.Sq(z[3 * i], z[3 * i + 1], z[3 * i + 2], i) for i in range(11)]
    out = {}
    for i in range(11):
        for c in T1.wall_contacts(sq[i], s):
            out[('wall', i, c['wall'])] = c
    for i in range(11):
        for j in range(i + 1, 11):
            c = T1.classify_pair(sq[i], sq[j])
            if c is not None:
                out[('pair', i, j)] = c
    return out, sq


def edge_key(st, ow):
    kind, ei = ow
    if kind == 'wall':
        e = st['wall_edges'][ei]
        return ('wall', e['i'], e['wall'])
    e = st['pair_edges'][ei]
    return ('pair', min(e['i'], e['j']), max(e['i'], e['j']))


def row_type(st, ow, cls):
    """Contact type of the edge a row belongs to (Fact-0 row count is the
    authority on flushness; the A46 label is cross-checked)."""
    kind, ei = ow
    key = edge_key(st, ow)
    e = st['wall_edges'][ei] if kind == 'wall' else st['pair_edges'][ei]
    fact0_flush = e['n_rows'] >= 2
    lab = cls.get(key, {}).get('type')
    if fact0_flush:
        return ('WF' if kind == 'wall' else 'FL'), lab
    if kind == 'wall':
        return 'WC', lab
    return (lab if lab in ('CE', 'CC') else 'PT'), lab


def analyse(entry):
    cert = EA.load_cert(entry)
    z = [float(Fraction(v)) for v in cert['z_center']]
    s = z[G.S_IDX]
    rows, owner, lam, st, lp_used, A = certificate(entry, z)
    cls, sq = contact_classes(z, s)

    # ---------- check 2: flush inventory (over KEPT / non-rattler edges)
    n_WF = sum(1 for e in st['wall_edges']
               if not e['dropped'] and e['n_rows'] >= 2)
    n_FL = sum(1 for e in st['pair_edges']
               if not e['dropped'] and e['n_rows'] >= 2)
    n_WC = sum(1 for e in st['wall_edges']
               if not e['dropped'] and e['n_rows'] == 1)
    # A46-label agreement on the same kept edges
    agree = dis = 0
    for ei, e in enumerate(st['pair_edges']):
        if e['dropped']:
            continue
        t, lab = row_type(st, ('pair', ei), cls)
        if lab is None:
            dis += 1
        elif (lab == 'FL') == (e['n_rows'] >= 2):
            agree += 1
        else:
            dis += 1
    lab_counts = {}
    for ei, e in enumerate(st['pair_edges']):
        if e['dropped']:
            continue
        t, lab = row_type(st, ('pair', ei), cls)
        lab_counts[t] = lab_counts.get(t, 0) + 1
    for ei, e in enumerate(st['wall_edges']):
        if e['dropped']:
            continue
        t, lab = row_type(st, ('wall', ei), cls)
        lab_counts[t] = lab_counts.get(t, 0) + 1

    rec = {
        'family_id': entry['family_id'], 'class': entry['class'],
        's': s, 'lp_rowset': lp_used, 'rattlers': st['rattlers'],
        'k_core': st['k'], 'n_rows': len(rows),
        'flush': {'n_WF_wall_flush_edges': n_WF, 'n_FL_pair_flush_edges': n_FL,
                  'n_flush_edges': n_WF + n_FL,
                  'n_flush_rows_fact0': 2 * (n_WF + n_FL),
                  'n_WC_wall_corner_edges': n_WC,
                  'has_flush': bool(n_WF + n_FL >= 1)},
        'edge_type_counts': lab_counts,
        'a46_label_agreement': {'agree': agree, 'disagree': dis},
    }
    if lam is None:
        rec['dichotomy'] = {'status': 'NO-CERTIFICATE (lambda0=1 infeasible '
                                     'on physical AND expanded rows)'}
        rec['negative_control'] = {'n_fail': 0, 'n_checked': 0, 'n_pencil': 0,
                                   'example_fail': None,
                                   'note': 'no certificate -- not checked'}
        rec['rows_detail'] = []
        return rec

    loaded = [k for k in range(len(rows)) if lam[k] > LP_TOL]
    loaded_set = set(loaded)
    rec['n_loaded_rows'] = len(loaded)
    rec['lambda_max'] = float(lam.max())

    # rows incident to each square
    inc = {}
    for k, r in enumerate(rows):
        for a in row_actors(z, r):
            inc.setdefault(a, []).append(k)

    # ---------- checks 3 / 4 / 5
    def run(flip_recv):
        results = []
        max_ident = 0.0
        max_gg = 0.0
        for k in loaded:
            r = rows[k]
            ow = owner[k]
            t, lab = row_type(st, ow, cls)
            if t not in ('CE', 'WC'):
                continue
            if r['kind'] == 'wall':
                a = r['i']
                q = G.corner(z, r['i'], r['corner'])
            else:
                a = r['i']                       # the CORNER square of a CE row
                q = G.corner(z, r['i'], r['corner'])
            self_tau, _ = tau_geo(z, r, a, q, flip_recv)
            others = []
            ident = 0.0
            for kk in inc[a]:
                tg, role = tau_geo(z, rows[kk], a, q, flip_recv)
                td = tau_grad(z, rows[kk], a, q)
                if not flip_recv:
                    max_gg = max(max_gg, abs(tg - td))
                    ident += lam[kk] * tg
                tt, tlab = row_type(st, owner[kk], cls)
                others.append({'row': kk, 'tau': float(tg), 'role': role,
                               'type': tt, 'lam': float(lam[kk]),
                               'edge': list(map(str, edge_key(st, owner[kk]))),
                               'loaded': kk in loaded_set, 'is_self': kk == k})
            if not flip_recv:
                max_ident = max(max_ident, abs(ident))
            oth = [o for o in others if o['loaded'] and not o['is_self']]
            pos = [o for o in oth if o['tau'] > TAU_TOL]
            neg = [o for o in oth if o['tau'] < -TAU_TOL]
            if pos and neg:
                status = 'blocker'
            elif not pos and not neg:
                status = 'pencil'
            else:
                status = 'FAIL'
            delta = cls.get(edge_key(st, ow), {}).get('delta')
            results.append({
                'row': k, 'type': t, 'a': a, 'q': [float(q[0]), float(q[1])],
                'lam': float(lam[k]), 'edge': list(map(str, edge_key(st, ow))),
                'delta_deg': (None if delta is None else float(delta)),
                'self_tau': float(self_tau), 'status': status,
                'loaded_rows_at_a': [{'type': o['type'], 'role': o['role'],
                                      'tau': o['tau'], 'lam': o['lam'],
                                      'edge': o['edge']} for o in oth],
                'n_loaded_at_a': len(oth),
                'max_pos_tau': (max(o['tau'] for o in pos) if pos else None),
                'min_neg_tau': (min(o['tau'] for o in neg) if neg else None),
                'max_abs_tau': (max(abs(o['tau']) for o in oth) if oth else 0.0),
                'blockers': [{'type': o['type'], 'role': o['role'],
                              'tau': o['tau'], 'edge': o['edge']}
                             for o in pos],
            })
        return results, max_ident, max_gg

    res, max_ident, max_gg = run(False)
    res_flip, _, _ = run(True)

    ceq = [r for r in res if r['type'] == 'CE']
    wcq = [r for r in res if r['type'] == 'WC']
    bl = [r for r in res if r['status'] == 'blocker']
    pen = [r for r in res if r['status'] == 'pencil']
    bad = [r for r in res if r['status'] == 'FAIL']
    rec['dichotomy'] = {
        'status': 'PASS' if not bad else 'FAIL',
        'n_loaded_CE': len(ceq), 'n_loaded_WC': len(wcq),
        'n_blocker_ok': len(bl), 'n_pencil': len(pen), 'n_fail': len(bad),
        'min_blocker_margin': (min(r['max_pos_tau'] for r in bl)
                               if bl else None),
        'min_closer_margin': (min(-r['min_neg_tau'] for r in bl)
                              if bl else None),
        'max_self_tau': (max(abs(r['self_tau']) for r in res) if res else 0.0),
        'max_pencil_abs_tau': (max(r['max_abs_tau'] for r in pen)
                               if pen else None),
        'pencil_min_n_loaded_at_a': (min(r['n_loaded_at_a'] for r in pen)
                                     if pen else None),
        'n_pencil_with_empty_L_a': sum(1 for r in pen
                                       if r['n_loaded_at_a'] == 0),
        'max_torque_identity_residual': float(max_ident),
        'max_tau_geo_minus_tau_grad': float(max_gg),
        'failures': bad[:8],
    }
    bad_f = [r for r in res_flip if r['status'] == 'FAIL']
    rec['negative_control'] = {
        'n_fail': len(bad_f), 'n_checked': len(res_flip),
        'n_pencil': sum(1 for r in res_flip if r['status'] == 'pencil'),
        'example_fail': (None if not bad_f else
                         {kk: bad_f[0][kk] for kk in
                          ('row', 'type', 'a', 'edge', 'max_pos_tau',
                           'min_neg_tau')}),
    }
    rec['rows_detail'] = res
    return rec


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    log = []

    def P(msg):
        log.append(msg)
        print(msg, flush=True)

    P('A48 canary_cascade  tol_c=%g lp_tol=%g tau_tol=%g' % (TOL_C, LP_TOL,
                                                             TAU_TOL))
    atlas = EA.load_atlas()
    entries = atlas['entries']
    per_entry, genuine = [], []
    for e in entries:
        if e['class'] not in GENUINE:
            per_entry.append({'family_id': e['family_id'], 'class': e['class'],
                              'verdict': 'vacuous (not a critical point)'})
            continue
        r = analyse(e)
        r['verdict'] = 'genuine'
        per_entry.append(r)
        genuine.append(r)
        d = r['dichotomy']
        P('fam %-10s %-16s flush(WF=%d,FL=%d)=%2d rows=%2d | CE=%2d WC=%2d '
          'blk=%2d pen=%2d fail=%2d minmarg=%s | negctl fail=%d/%d'
          % (str(r['family_id']), r['class'], r['flush']['n_WF_wall_flush_edges'],
             r['flush']['n_FL_pair_flush_edges'], r['flush']['n_flush_edges'],
             r['flush']['n_flush_rows_fact0'], d.get('n_loaded_CE', -1),
             d.get('n_loaded_WC', -1), d.get('n_blocker_ok', -1),
             d.get('n_pencil', -1), d.get('n_fail', -1),
             ('%.3e' % d['min_blocker_margin']
              if d.get('min_blocker_margin') is not None else 'n/a'),
             r['negative_control']['n_fail'],
             r['negative_control']['n_checked']))

    # ---------------------------------------------------------- aggregation
    fl = {str(r['family_id']): r['flush']['n_flush_edges'] for r in genuine}
    flrows = {str(r['family_id']): r['flush']['n_flush_rows_fact0']
              for r in genuine}
    vac_ok = all(v >= 1 for v in fl.values())

    dich = {}
    tot = dict(CE=0, WC=0, blk=0, pen=0, fail=0)
    margins, idents, ggs = [], [], []
    for r in genuine:
        d = r['dichotomy']
        dich[str(r['family_id'])] = {
            'n_loaded_CE': d.get('n_loaded_CE'), 'n_loaded_WC': d.get('n_loaded_WC'),
            'n_blocker_ok': d.get('n_blocker_ok'), 'n_pencil': d.get('n_pencil'),
            'n_fail': d.get('n_fail'), 'status': d.get('status'),
            'min_blocker_margin': d.get('min_blocker_margin'),
            'max_torque_identity_residual': d.get(
                'max_torque_identity_residual'),
            'lp_rowset': r['lp_rowset']}
        if d.get('status') is None or 'NO-CERT' in str(d.get('status')):
            continue
        tot['CE'] += d['n_loaded_CE']
        tot['WC'] += d['n_loaded_WC']
        tot['blk'] += d['n_blocker_ok']
        tot['pen'] += d['n_pencil']
        tot['fail'] += d['n_fail']
        if d['min_blocker_margin'] is not None:
            margins.append(d['min_blocker_margin'])
        idents.append(d['max_torque_identity_residual'])
        ggs.append(d['max_tau_geo_minus_tau_grad'])

    tally, tally_ce = {}, {}
    n_ce_with_blocker = 0
    for r in genuine:
        for row in r.get('rows_detail', []):
            if row['status'] != 'blocker':
                continue
            if row['type'] == 'CE':
                n_ce_with_blocker += 1
            for b in row['blockers']:
                key = b['type'] + ('/' + b['role'] if b['type'] in
                                   ('CE', 'CC', 'FL', 'PT') else '')
                tally[key] = tally.get(key, 0) + 1
                if row['type'] == 'CE':
                    tally_ce[key] = tally_ce.get(key, 0) + 1

    # ---- what supports the PENCIL branch here (A48's live question)
    pen_sup, pen_flush, pen_tot = {}, 0, 0
    pen_deltas = []
    for r in genuine:
        for row in r.get('rows_detail', []):
            if row['status'] != 'pencil':
                continue
            pen_tot += 1
            if row['delta_deg'] is not None:
                pen_deltas.append(round(row['delta_deg'], 4))
            sig = tuple(sorted(o['type'] + '/' + o['role']
                               for o in row['loaded_rows_at_a']))
            pen_sup['+'.join(sig) if sig else '(empty)'] = \
                pen_sup.get('+'.join(sig) if sig else '(empty)', 0) + 1
            if any(o['type'] in ('FL', 'WF') for o in row['loaded_rows_at_a']):
                pen_flush += 1

    # ---- near-flush (small-mismatch) blocker tally
    nf = {}
    for thr in (2.0, 5.0, 10.0):
        t2, n_rows_thr, n_pen_thr = {}, 0, 0
        for r in genuine:
            for row in r.get('rows_detail', []):
                d = row.get('delta_deg')
                if d is None or d > thr:
                    continue
                n_rows_thr += 1
                if row['status'] == 'pencil':
                    n_pen_thr += 1
                for b in row['blockers']:
                    key = b['type'] + ('/' + b['role'] if b['type'] in
                                       ('CE', 'CC', 'FL', 'PT') else '')
                    t2[key] = t2.get(key, 0) + 1
        nf['delta_le_%g_deg' % thr] = {'n_loaded_CE_WC_rows': n_rows_thr,
                                       'n_pencil': n_pen_thr,
                                       'blocker_types': t2}

    # ---- agreement with the A46 task-1 audit on the same 12 entries
    a46p = os.path.join(ATT, 'A46-balanced-wedge', 'results',
                        'atlas_mismatch_audit.json')
    a46cmp = {'file': 'attempts/A46-balanced-wedge/results/'
                      'atlas_mismatch_audit.json'}
    try:
        A46J = json.load(open(a46p))
        same = diff = 0
        det = {}
        mine = {str(r['family_id']): r['edge_type_counts'] for r in genuine}
        for e in A46J['entries']:
            fid = str(e['family_id'])
            theirs = dict(e['summary']['type_counts'])
            ours = dict(mine.get(fid, {}))
            if theirs == ours:
                same += 1
            else:
                diff += 1
                det[fid] = {'a46': theirs, 'a48': ours}
        a46cmp.update({'n_entries_compared': len(A46J['entries']),
                       'identical_type_counts': same, 'differing': diff,
                       'differences': det,
                       'note': 'A46 counts non-rattler-incident CONTACTS; A48 '
                               'counts kept contact EDGES -- the same objects. '
                               'Flushness in A48 is decided by the A44 Fact-0 '
                               'row count, in A46 by the geometric FL/WF test; '
                               'they agree edge-for-edge (see '
                               'a46_label_agreement per entry).'})
    except Exception as exc:                                  # pragma: no cover
        a46cmp['error'] = repr(exc)

    nc_fail = sum(r['negative_control']['n_fail'] for r in genuine)
    nc_chk = sum(r['negative_control']['n_checked'] for r in genuine)
    nc_entries = [str(r['family_id']) for r in genuine
                  if r['negative_control']['n_fail'] > 0]

    ok = (vac_ok and tot['fail'] == 0
          and all(i <= IDENT_TOL for i in idents)
          and all(g <= 1e-9 for g in ggs)
          and nc_fail > 0)
    verdict = 'PASS' if ok else 'FAIL'
    detail = []
    if not vac_ok:
        detail.append('some genuine entry has 0 flush rows')
    if tot['fail']:
        detail.append('%d W1.2 dichotomy failures' % tot['fail'])
    if idents and max(idents) > IDENT_TOL:
        detail.append('torque identity residual %.3e' % max(idents))
    if ggs and max(ggs) > 1e-9:
        detail.append('tau_geo != tau_grad, max diff %.3e' % max(ggs))
    if nc_fail == 0:
        detail.append('NEGATIVE CONTROL DID NOT FIRE (checker may be vacuous)')
    if detail:
        verdict = 'FAIL: ' + '; '.join(detail)

    out = {
        'what': 'A48 canary: cascade-theory premises (flush-vacuity + W1.2 '
                'blocking dichotomy + blocker taxonomy) checked against all 36 '
                'A37 critical-point atlas entries, with a sign-flip corruption '
                'gate.  Empirical, float64, never an input to a certified '
                'verdict.',
        'float_only': True,
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'inputs': {
            'atlas': 'attempts/A37-cp-atlas/results/atlas_final.json',
            'machinery': ['attempts/A44-fj-maxwell/code/eval_atlas.py',
                          'attempts/A44-fj-maxwell/code/a44_geom.py',
                          'attempts/A46-balanced-wedge/code/task1_audit.py'],
            'theory': 'attempts/A46-balanced-wedge/notes/w1_theory.md sect. 2 '
                      '(Theorem W1.2), sect. 1 (Lemma W1.1)'},
        'tolerances': {'contact': TOL_C, 'lp_loaded': LP_TOL,
                       'tau_zero': TAU_TOL, 'identity': IDENT_TOL},
        'conventions': [
            'Certificate: ONE FJ multiplier vector at lambda0 = 1 -- the '
            'min-sum-lambda HiGHS vertex of A^T lambda = e_s, 0 <= lambda <= '
            '1e6 on the A44 Fact-0 physical row set (expanded row set as '
            'fallback where the physical set is infeasible: the two '
            'VALLEY-MARGINAL entries).  W1.2 is per-certificate, so LOADED '
            'means lambda_k > 1e-7 in THIS vector, not "loadable".',
            'Force direction ON square a: wall row -> inward wall normal; '
            'a-corner-on-j-edge (resting) -> j\'s outward edge normal (points '
            'into a); other-corner-on-a-edge (received) -> MINUS a\'s outward '
            'edge normal.  Identical to grad_{c_a} g_k, which is how it is '
            'cross-checked (tau_geo vs tau_grad).',
            'tau_k = cross(p_k - q, n_k); the row (a,b) itself has p = q so '
            'tau = 0 (reported as max_self_tau).',
            'Flushness is decided by the A44 Fact-0 row count (2 rows = '
            'segment contact = flush); the A46 task-1 geometric label is '
            'computed independently and the agreement is reported.',
            'A flush edge contributes its TWO contact points as two rows, '
            'each with its own tau.'],
        'n_entries': len(entries),
        'n_genuine': len(genuine),
        'n_not_cp': len(entries) - len(genuine),
        'vacuity': {
            'statement': 'every genuine entry carries >= 1 flush contact, so '
                         'the flush-free hypothesis of every A48 statement is '
                         'VACUOUS on all 36 atlas entries (the 24 NOT-CP '
                         'entries are vacuous for a second, independent '
                         'reason: they are not critical points).',
            'flush_edges_per_entry': fl,
            'flush_rows_per_entry': flrows,
            'min_flush_edges': min(fl.values()),
            'max_flush_edges': max(fl.values()),
            'all_at_least_one': vac_ok},
        'dichotomy': dich,
        'dichotomy_totals': {
            'n_loaded_CE_rows_checked': tot['CE'],
            'n_loaded_WC_rows_checked': tot['WC'],
            'n_blocker_ok': tot['blk'], 'n_pencil': tot['pen'],
            'n_fail': tot['fail'],
            'global_min_blocker_margin': (min(margins) if margins else None),
            'max_torque_identity_residual': (max(idents) if idents else None),
            'max_tau_geo_minus_tau_grad': (max(ggs) if ggs else None)},
        'negative_control': {
            'perturbation': 'n_k negated on RECEIVED rows (another body\'s '
                            'corner resting on a\'s edge) only; everything '
                            'else identical.',
            'n_rows_checked': nc_chk, 'n_dichotomy_failures': nc_fail,
            'entries_that_fail': nc_entries,
            'fired': bool(nc_fail > 0)},
        'blocker_tally': {
            'note': 'blocker rows (tau > tol) found at loaded CE/WC rows; '
                    'role rest = a\'s corner pushing on a partner edge, '
                    'recv = a partner corner pushing on a\'s edge, '
                    'rest_wall = a container wall.',
            'all_CE_and_WC': tally,
            'CE_only': tally_ce,
            'n_loaded_CE_rows_with_blocker': n_ce_with_blocker,
            'by_mismatch_threshold': nf},
        'pencil_support': {
            'note': 'for every loaded CE/WC row landing in the W1.2 PENCIL '
                    'branch, the multiset of the OTHER loaded rows at the '
                    'corner square a (all of which have tau = 0).',
            'n_pencil': pen_tot,
            'n_pencil_supported_by_a_flush_row': pen_flush,
            'signature_tally': pen_sup,
            'pencil_mismatch_deltas_deg': sorted(pen_deltas),
            'min_pencil_delta_deg': (min(pen_deltas) if pen_deltas else None)},
        'near_flush_rows': [
            {'family_id': r['family_id'], 'edge': row['edge'],
             'type': row['type'], 'delta_deg': row['delta_deg'],
             'status': row['status'], 'lam': row['lam'],
             'blockers': row['blockers'],
             'loaded_rows_at_a': row['loaded_rows_at_a']}
            for r in genuine for row in r.get('rows_detail', [])
            if row.get('delta_deg') is not None and row['delta_deg'] <= 10.0],
        'a46_audit_agreement': a46cmp,
        'per_entry': per_entry,
        'verdict': verdict,
        'wall_seconds': time.time() - t0,
    }
    p = os.path.join(RES, 'canary_cascade.json')
    with open(p, 'w') as f:
        json.dump(out, f, indent=1)

    P('')
    P('flush edges over 12 genuine entries: %d..%d (all >= 1: %s)'
      % (min(fl.values()), max(fl.values()), vac_ok))
    P('W1.2: loaded CE=%d WC=%d -> blocker %d, pencil %d, FAIL %d'
      % (tot['CE'], tot['WC'], tot['blk'], tot['pen'], tot['fail']))
    P('  min blocker margin %s ; max identity residual %.2e ; '
      'max |tau_geo - tau_grad| %.2e'
      % (('%.3e' % min(margins)) if margins else 'n/a',
         max(idents) if idents else 0.0, max(ggs) if ggs else 0.0))
    P('negative control: %d/%d rows fail on %d entries -> fired=%s'
      % (nc_fail, nc_chk, len(nc_entries), nc_fail > 0))
    P('blocker tally (CE only): %s' % json.dumps(tally_ce, sort_keys=True))
    P('blocker tally (CE+WC)  : %s' % json.dumps(tally, sort_keys=True))
    P('near-flush (delta<=5deg): %s' % json.dumps(nf['delta_le_5_deg'],
                                                  sort_keys=True))
    P('pencil support: %d/%d pencils have a FLUSH row among the loaded rows '
      'at a; min pencil mismatch %s deg; signatures %s'
      % (pen_flush, pen_tot,
         ('%.2f' % min(pen_deltas)) if pen_deltas else 'n/a',
         json.dumps(pen_sup, sort_keys=True)))
    P('A46 audit type-count agreement: %s/%s identical'
      % (a46cmp.get('identical_type_counts'),
         a46cmp.get('n_entries_compared')))
    P('VERDICT: %s   (%.1f s)' % (verdict, time.time() - t0))
    P('-> %s' % os.path.relpath(p, REPO).replace(os.sep, '/'))

    with open(os.path.join(LOGS, 'canary_run.txt'), 'a') as f:
        f.write('\n=== %s  canary_cascade.py ===\n'
                % time.strftime('%Y-%m-%dT%H:%M:%S'))
        f.write('\n'.join(log) + '\n')
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
