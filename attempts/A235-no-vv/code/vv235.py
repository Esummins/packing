"""A235 -- vertex-on-vertex (VV) contacts at a witness, n-general: detection and classification of every
touching pair (VE = vertex on edge interior, VV = the two touching vertices coincide, PAR = parallel squares:
flush edge-edge or a lattice corner-to-corner coincidence), the load carried by each contact over the whole FJ
multiplier polytope, and Lemma NO-VV's TWO-SELECTION test at every tilted VV contact:
    the feasible set of the pair near a VV contact is the UNION {g_A >= 0} u {g_B >= 0} (g_A: B's vertex vs
    A's separating edge line, g_B: A's vertex vs B's), not their intersection; a minimiser is a local minimum
    of NLP(S_A) AND of NLP(S_B) (D1 / D3'), so BOTH selections must be Fritz-John (lam0 = 1, or a self-stress).
Witness dicts as stress234 (name, cls, n, z, rows, A, lam).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('A234-handedness', 'A219-wall-torque', 'A217-torque-probe'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import stress234 as ST        # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
TOL_PT = 1e-6          # coincident vertices
TOL_PAR = 2e-3         # parallel tilts (mod pi/2), radians: 0.11 deg -- SLSQP's residual on a lattice pair is <= 0.08 deg
LOAD_TOL = 1e-6
LP_CAP = 1e4


# ---------------------------------------------------------------- contacts
def tilt_gap(th_i, th_j):
    """distance of th_i - th_j from the nearest multiple of pi/2."""
    d = (th_i - th_j) % (math.pi / 2)
    return min(d, math.pi / 2 - d)


def pair_contacts(w):
    """per touching pair (i, j): {'type': 'VE' | 'VV' | 'PAR', 'rows': [row indices], 'points': [...],
    'rowA': index of (owner i, corner of j) row at the VV point, 'rowB': (owner j, corner of i), 'P': the
    common vertex, 'tilt_gap_deg'}.  Line rows (corner on the extended edge line, off the segment) are ignored
    for the geometry but listed."""
    z, rows = w['z'], w['rows']
    cx, cy, th, s, n = ST.unpack(z)
    q = ST.verts(z)
    pairs = {}
    for k, r in enumerate(rows):
        if r['kind'] != 'edge':
            continue
        key = (min(r['i'], r['j']), max(r['i'], r['j']))
        pairs.setdefault(key, []).append(k)
    out = {}
    for (i, j), idx in pairs.items():
        on = [k for k in idx if rows[k].get('on_segment', True)]
        pts = [(k, q[rows[k]['i'], rows[k]['corner']]) for k in on]
        d = {'rows': idx, 'n_line_rows': len(idx) - len(on), 'tilt_gap_deg': math.degrees(tilt_gap(th[i], th[j]))}
        if tilt_gap(th[i], th[j]) <= TOL_PAR:
            d['type'] = 'PAR'
            allp = np.array([p for _, p in pts]) if pts else np.zeros((0, 2))
            d['par_point'] = bool(len(allp) and np.ptp(allp, axis=0).max() <= TOL_PT)
            out[(i, j)] = d
            continue
        vv = None
        for ka, pa in pts:
            for kb, pb in pts:
                if rows[ka]['j'] == i and rows[kb]['j'] == j and np.abs(pa - pb).max() <= TOL_PT:
                    vv = (ka, kb, pa)
        if vv is not None:
            d.update({'type': 'VV', 'rowA': vv[0], 'rowB': vv[1], 'P': [float(v) for v in vv[2]]})
        else:
            d['type'] = 'VE'
        out[(i, j)] = d
    return out


# ---------------------------------------------------------------- multipliers
def fj_status(A, slack=0.0):
    """'KKT' if lam >= 0 with A^T lam = e_s (lam0 = 1, |.|_inf <= slack), else 'self-stress' if A^T lam = 0,
    sum lam = 1 has a solution, else 'none' (not Fritz-John).  Returns (status, lam)."""
    m, nv = A.shape
    if m == 0:
        return 'none', None
    e = ST.e_s(nv)
    if slack > 0:
        Aeq = np.hstack([A.T, np.eye(nv)])
        r = linprog(np.concatenate([np.ones(m), np.zeros(nv)]), A_eq=Aeq, b_eq=e,
                    bounds=[(0, LP_CAP)] * m + [(-slack, slack)] * nv, method='highs')
    else:
        r = linprog(np.ones(m), A_eq=A.T, b_eq=e, bounds=(0, LP_CAP), method='highs')
    if r.success:
        return 'KKT', np.asarray(r.x)[:m]
    Aeq = np.vstack([A.T, np.ones((1, m))])
    beq = np.concatenate([np.zeros(nv), [1.0]])
    if slack > 0:
        Aeq = np.hstack([Aeq, np.vstack([np.eye(nv), np.zeros((1, nv))])])
        r = linprog(np.zeros(m + nv), A_eq=Aeq, b_eq=beq, bounds=[(0, LP_CAP)] * m + [(-slack, slack)] * nv, method='highs')
    else:
        r = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq, bounds=(0, LP_CAP), method='highs')
    if r.success:
        return 'self-stress', np.asarray(r.x)[:m]
    return 'none', None


def load_range(A, idx, slack=0.0):
    """[min, max] of sum_{k in idx} lam_k over the lam0 = 1 polytope (None if empty)."""
    c = np.zeros(A.shape[0])
    c[idx] = 1.0
    if slack > 0:
        return ST.lp_range(A, c)
    out = []
    for sg in (1.0, -1.0):
        r = linprog(sg * c, A_eq=A.T, b_eq=ST.e_s(A.shape[1]), bounds=(0, LP_CAP), method='highs')
        if not r.success:
            return None
        out.append(sg * float(r.fun))
    return out


def in_span(A, k, others, tol=1e-7):
    """is row k of A in the span of the rows `others`?  (relative least-squares residual <= tol)"""
    if not others:
        return False, 1.0
    M = A[others].T
    x, res, rk, sv = np.linalg.lstsq(M, A[k], rcond=None)
    rel = float(np.linalg.norm(M @ x - A[k]) / max(np.linalg.norm(A[k]), 1e-300))
    return rel <= tol, rel


# ---------------------------------------------------------------- the census entry
def analyse(w, slack=None):
    """contact census of one witness + the two-selection test at every tilted VV pair."""
    A, rows, lam = w['A'], w['rows'], w['lam']
    if slack is None:
        slack = 0.0 if w['cls'] in ('HELD', 'CROWD', 'SETTLED', 'K0FREE', 'BOXK0') else ST.EPS
    cts = pair_contacts(w)
    o = {'name': w['name'], 'rid': w.get('rid'), 'cls': w['cls'], 'n': w['n'], 's': float(w['z'][-1]), 'n_rows': len(rows),
         'stationary': lam is not None, 'n_pairs': len(cts)}
    cnt = {}
    for d in cts.values():
        loaded = lam is not None and any(lam[k] > LOAD_TOL for k in d['rows'])
        key = d['type'] + ('-point' if d.get('par_point') else '') + ('/loaded' if loaded else '/free')
        cnt[key] = cnt.get(key, 0) + 1
    o['contacts'] = cnt
    o['rank_deficiency'] = int(len(rows) - np.linalg.matrix_rank(A, tol=1e-9)) if len(rows) else 0
    vv = []
    for (i, j), d in cts.items():
        if d['type'] != 'VV':
            continue
        ka, kb = d['rowA'], d['rowB']
        e = {'pair': [i, j], 'P': d['P'], 'tilt_gap_deg': d['tilt_gap_deg'], 'rowA': ka, 'rowB': kb,
             'lam_A_l1': float(lam[ka]) if lam is not None else None,
             'lam_B_l1': float(lam[kb]) if lam is not None else None}
        e['loaded_l1'] = lam is not None and (lam[ka] > LOAD_TOL or lam[kb] > LOAD_TOL)
        rng = load_range(A, [ka, kb], slack) if lam is not None else None
        e['load_range'] = rng
        e['loadable'] = bool(rng is not None and rng[1] > LOAD_TOL)
        e['necessarily_loaded'] = bool(rng is not None and rng[0] > LOAD_TOL)
        keepA = [k for k in range(len(rows)) if k != kb]
        keepB = [k for k in range(len(rows)) if k != ka]
        stA, lamA = fj_status(A[keepA], slack)
        stB, lamB = fj_status(A[keepB], slack)
        e['sel_A'] = stA
        e['sel_B'] = stB
        e['lam_A_in_selA'] = float(lamA[keepA.index(ka)]) if lamA is not None else None
        e['lam_B_in_selB'] = float(lamB[keepB.index(kb)]) if lamB is not None else None
        others = [k for k in range(len(rows)) if k not in (ka, kb)]
        e['gA_in_span'], e['gA_span_res'] = in_span(A, ka, others + [kb])
        e['gB_in_span'], e['gB_span_res'] = in_span(A, kb, others + [ka])
        e['first_order'] = 'EXCL-1' if 'none' in (stA, stB) else ('PASS-1' if stA == 'KKT' and stB == 'KKT' else 'PASS-1(self-stress)')
        vv.append(e)
    o['vv'] = vv
    o['n_vv'] = len(vv)
    allvv = [k for e in vv for k in (e['rowA'], e['rowB'])]
    o['vv_total_range'] = load_range(A, allvv, slack) if (vv and lam is not None) else None
    o['vv_free_stress'] = bool(o['vv_total_range'] is not None and o['vv_total_range'][0] <= LOAD_TOL)
    o['n_vv_loaded_l1'] = sum(e['loaded_l1'] for e in vv)
    o['n_vv_loadable'] = sum(e['loadable'] for e in vv)
    o['n_vv_excl1'] = sum(e['first_order'] == 'EXCL-1' for e in vv)
    return o, cts
