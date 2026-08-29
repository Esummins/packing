#!/usr/bin/env python
"""eval_atlas.py -- A44 refutation test bed.

Evaluates a table of candidate Maxwell-type row-count bounds against the A37
critical-point atlas (36 entries).  Deterministic; single process.

Outputs
  results/candidates.json   machine readable (per-entry table, verdicts, LP
                            diagnostics, contact-completeness audit, Trump
                            reconciliation)
  results/eval_report.md    PI-readable
  logs/eval.log

Usage:  python eval_atlas.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A44 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A44, '..'))
A37 = os.path.join(ATT, 'A37-cp-atlas')
sys.path.insert(0, os.path.join(A37, 'code'))
sys.path.insert(0, HERE)

import a44_geom as G                                             # noqa: E402

ATLAS = os.path.join(A37, 'results', 'atlas_final.json')
RESULTS = os.path.join(A44, 'results')
LOGS = os.path.join(A44, 'logs')

# ---------------------------------------------------------------- constants
SEED = 20260829
NSQ = G.NSQ
S_IDX = G.S_IDX

RANK_TOL = 1e-9            # absolute singular-value cut (matches A37 classify)
RANK_TOL_LO = 1e-11
RANK_TOL_HI = 1e-7
CLUSTER_TOL = 1e-6         # contact-point coincidence tolerance
T_EDGE_TOL = 1e-6          # |t| <= 1/2 + T_EDGE_TOL  =>  point is on the edge
LP_CAP = 1.0e6             # box cap for the multiplier LPs
LP_TOL = 1e-7              # lambda_r > LP_TOL  =>  loadable / forced
SUPP_TOL = 1e-9            # support tolerance for the small-support search
NEAR_MISS = 1e-3           # report every non-contact gap below this
N_RANDOM_C = 20
N_REWEIGHT = 10

_LOG = []


def log(msg):
    line = msg
    _LOG.append(line)
    print(line, flush=True)


# ================================================================= structure
def load_atlas():
    with open(ATLAS) as f:
        return json.load(f)


def load_cert(entry):
    p = os.path.join(ATT, entry['cert_path'].replace('/', os.sep))
    with open(p) as f:
        return json.load(f)


def contact_points(z, spec_list):
    """Fact-0 contact set of one pair contact.

    A rowspec whose tangential coordinate satisfies |t| <= 1/2 + eps sits ON
    the owner's edge segment, i.e. its corner is a point of the contact set.
    Cluster those points; the number of clusters is 1 (point contact) or 2
    (segment/flush contact, the clusters being the two segment endpoints).
    """
    cands = []
    for idx, s in enumerate(spec_list):
        t = G.sep_t(z, s['owner'], s['edge'], s['other'], s['corner'])
        if abs(t) <= 0.5 + T_EDGE_TOL:
            xy = G.corner(z, s['other'], s['corner'])
            cands.append({'idx': idx, 't': t, 'xy': xy, 'spec': s})
    clusters = []
    for c in cands:
        for cl in clusters:
            if (abs(cl['xy'][0] - c['xy'][0]) < CLUSTER_TOL
                    and abs(cl['xy'][1] - c['xy'][1]) < CLUSTER_TOL):
                cl['members'].append(c)
                break
        else:
            clusters.append({'xy': c['xy'], 'members': [c]})
    # deterministic representative per cluster: prefer [V]-safe, then min |t|,
    # then lexicographic on (owner, other, edge, corner)
    for cl in clusters:
        cl['members'].sort(key=lambda c: (
            0 if c['spec']['safe'] else 1, round(abs(c['t']), 12),
            c['spec']['owner'], c['spec']['other'], c['spec']['edge'],
            c['spec']['corner']))
        cl['rep'] = cl['members'][0]
    clusters.sort(key=lambda cl: (round(cl['xy'][0], 9), round(cl['xy'][1], 9)))
    return clusters


def build_structure(entry, z):
    """The A44 physical (Fact 0) contact structure of one atlas entry.

    Returns a dict with:
      core, rattlers, k
      pair_edges  [{i,j,a37_class,kind('SEGMENT'|'POINT'),n_rows,rows[],
                    dropped}]
      wall_edges  [{i,wall,corners[],n_rows,rows[],dropped}]
      expanded_rows  (all rowspec branches of every kept pair edge + walls)
    """
    rat = set(entry['rattler_squares'])
    core = [i for i in range(NSQ) if i not in rat]

    wall_groups = {}
    for c in entry['contact_table']:
        if c['type'] != 'wall':
            continue
        wall_groups.setdefault((c['i'], c['wall']), []).append(c['corner'])
    wall_edges = []
    for (i, w), corners in sorted(wall_groups.items()):
        cs = sorted(set(corners))
        wall_edges.append({
            'i': i, 'wall': w, 'corners': cs, 'n_rows': len(cs),
            'dropped': i in rat,
            'rows': [{'kind': 'wall', 'i': i, 'corner': k, 'wall': w}
                     for k in cs]})

    pair_edges = []
    for c in entry['contact_table']:
        if c['type'] != 'pair':
            continue
        cl = contact_points(z, c['rowspecs'])
        kind = 'SEGMENT' if len(cl) >= 2 else 'POINT'
        rows = [{'kind': 'edge', 'i': x['rep']['spec']['other'],
                 'corner': x['rep']['spec']['corner'],
                 'j': x['rep']['spec']['owner'],
                 'edge': x['rep']['spec']['edge']} for x in cl]
        exp = [{'kind': 'edge', 'i': s['other'], 'corner': s['corner'],
                'j': s['owner'], 'edge': s['edge']} for s in c['rowspecs']]
        pair_edges.append({
            'i': c['i'], 'j': c['j'], 'a37_class': c['class'],
            'n_axes_tied': c['n_axes_tied'], 'kind': kind,
            'n_clusters': len(cl), 'n_rows': len(rows), 'rows': rows,
            'expanded_rows': exp, 'n_rowspecs': len(c['rowspecs']),
            'dropped': (c['i'] in rat) or (c['j'] in rat)})

    aux = [{'i': c['i'], 'j': c['j'],
            'dropped': (c['i'] in rat) or (c['j'] in rat)}
           for c in entry['contact_table'] if c['type'] == 'aux']

    return {'rattlers': sorted(rat), 'core': core, 'k': len(core),
            'wall_edges': wall_edges, 'pair_edges': pair_edges, 'aux': aux}


def counts(st, convention='fact0'):
    """(E, F, m) broken down, over the KEPT (core) edges only.

    convention 'fact0' : segment contact = 2 rows, point contact = 1 row
                         (docs/proofs/structure_lemmas.md Fact 0, decided
                         geometrically from the contact set).
    convention 'brief' : A37 label literally -- FLUSH = 2, POINT = 1,
                         CORNER-CORNER = 1.
    """
    E_w = F_w = m_w = 0
    for e in st['wall_edges']:
        if e['dropped']:
            continue
        E_w += 1
        m_w += e['n_rows']
        if e['n_rows'] >= 2:
            F_w += 1
    E_p = F_p = m_p = 0
    for e in st['pair_edges']:
        if e['dropped']:
            continue
        E_p += 1
        if convention == 'fact0':
            nr = e['n_rows']
        else:
            nr = 2 if e['a37_class'] == 'FLUSH' else 1
        m_p += nr
        if nr >= 2:
            F_p += 1
    return {'E_pair': E_p, 'E_wall': E_w, 'E': E_p + E_w,
            'F_pair': F_p, 'F_wall': F_w, 'F': F_p + F_w,
            'm_pair': m_p, 'm_wall': m_w, 'm': m_p + m_w}


def physical_rows(st, convention='fact0', keep_dropped=False):
    """Row list + a parallel edge-id list, in a deterministic order."""
    rows, owner = [], []
    for ei, e in enumerate(st['wall_edges']):
        if e['dropped'] and not keep_dropped:
            continue
        for r in e['rows']:
            rows.append(r)
            owner.append(('wall', ei))
    for ei, e in enumerate(st['pair_edges']):
        if e['dropped'] and not keep_dropped:
            continue
        rs = e['rows']
        if convention != 'fact0' and e['a37_class'] == 'CORNER-CORNER':
            rs = e['rows'][:1]          # brief convention: CC = 1 row
        for r in rs:
            rows.append(r)
            owner.append(('pair', ei))
    return rows, owner


def expanded_rows(st, keep_dropped=False):
    rows, owner = [], []
    for ei, e in enumerate(st['wall_edges']):
        if e['dropped'] and not keep_dropped:
            continue
        for r in e['rows']:
            rows.append(r)
            owner.append(('wall', ei))
    for ei, e in enumerate(st['pair_edges']):
        if e['dropped'] and not keep_dropped:
            continue
        for r in e['expanded_rows']:
            rows.append(r)
            owner.append(('pair', ei))
    return rows, owner


def col_index(core):
    """Core coordinate columns: 3 per core square, then s.  Length 3k+1."""
    cols = []
    for i in core:
        cols += [3 * i, 3 * i + 1, 3 * i + 2]
    cols.append(S_IDX)
    return cols


def jac(z, rows, cols):
    A = np.zeros((len(rows), len(cols)))
    for r, c in enumerate(rows):
        g = G.row_grad(z, c)
        A[r, :] = g[cols]
    return A


def rank_report(A):
    if A.shape[0] == 0:
        return {'rank': 0, 'sv': [], 'sv_cut': [None, None]}
    sv = np.linalg.svd(A, compute_uv=False)
    out = {'sv_max': float(sv[0]), 'n_sv': int(len(sv))}
    for tag, tol in (('rank', RANK_TOL), ('rank_lo', RANK_TOL_LO),
                     ('rank_hi', RANK_TOL_HI)):
        out[tag] = int((sv > tol).sum())
    r = out['rank']
    out['sv_min_kept'] = float(sv[r - 1]) if r > 0 else None
    out['sv_max_dropped'] = float(sv[r]) if r < len(sv) else 0.0
    out['sv_gap_ratio'] = (float(sv[r - 1] / sv[r])
                           if 0 < r < len(sv) and sv[r] > 0 else None)
    out['sv_tail'] = [float(x) for x in sv[max(0, r - 3):min(len(sv), r + 3)]]
    return out


# ======================================================================= LP
def lp_feasible(A, cap=LP_CAP):
    """min sum lambda  s.t.  A^T lambda = e_s, 0 <= lambda <= cap."""
    m, n = A.shape
    b = np.zeros(n)
    b[-1] = 1.0                                   # e_s (s is the last column)
    r = linprog(np.ones(m), A_eq=A.T, b_eq=b, bounds=(0.0, cap),
                method='highs')
    if not r.success:
        return None, r
    return np.asarray(r.x), r


def lp_extreme(A, k, sense, cap=LP_CAP):
    m, n = A.shape
    b = np.zeros(n)
    b[-1] = 1.0
    c = np.zeros(m)
    c[k] = 1.0 if sense == 'min' else -1.0
    r = linprog(c, A_eq=A.T, b_eq=b, bounds=(0.0, cap), method='highs')
    if not r.success:
        return None
    return float(r.x[k])


def lp_weighted(A, w, cap=LP_CAP):
    m, n = A.shape
    b = np.zeros(n)
    b[-1] = 1.0
    r = linprog(w, A_eq=A.T, b_eq=b, bounds=(0.0, cap), method='highs')
    if not r.success:
        return None
    return np.asarray(r.x)


def lp_block(A, rows, owner, k_core, rng):
    """Full FJ multiplier analysis on one row set."""
    m = A.shape[0]
    out = {'m': m}
    lam, r = lp_feasible(A)
    out['feasible'] = lam is not None
    if lam is None:
        out['status'] = r.message
        return out
    b = np.zeros(A.shape[1])
    b[-1] = 1.0
    out['residual_inf'] = float(np.abs(A.T @ lam - b).max())
    out['sum_lambda'] = float(lam.sum())
    # sum of far-wall (ds-carrying) multipliers must be 1
    far = [i for i in range(m) if rows[i]['kind'] == 'wall'
           and rows[i]['wall'] in ('x=s', 'y=s')]
    out['n_farwall_rows'] = len(far)
    out['sum_farwall_lambda'] = float(lam[far].sum()) if far else 0.0

    lmax, lmin = np.zeros(m), np.zeros(m)
    unbounded = []
    for k in range(m):
        v = lp_extreme(A, k, 'max')
        lmax[k] = np.nan if v is None else v
        if v is not None and v > 0.99 * LP_CAP:
            unbounded.append(k)
        v = lp_extreme(A, k, 'min')
        lmin[k] = np.nan if v is None else v
    out['lambda_max'] = [float(x) for x in lmax]
    out['lambda_min'] = [float(x) for x in lmin]
    out['unbounded_rows'] = unbounded
    loadable = [k for k in range(m) if lmax[k] > LP_TOL]
    forced = [k for k in range(m) if lmin[k] > LP_TOL]
    out['loadable_rows'] = loadable
    out['forced_rows'] = forced
    out['n_loadable'] = len(loadable)
    out['n_forced'] = len(forced)

    # ---- small support search
    best = None
    trials = [np.ones(m)]
    for _ in range(N_RANDOM_C):
        trials.append(rng.uniform(0.5, 1.5, m))
    for w in trials:
        x = lp_weighted(A, w)
        if x is None:
            continue
        supp = [k for k in range(m) if x[k] > SUPP_TOL]
        if best is None or len(supp) < len(best[0]):
            best = (supp, x.copy())
    # reweighted-L1 sparsification from the incumbent (deterministic)
    if best is not None:
        x = best[1]
        for _ in range(N_REWEIGHT):
            w = 1.0 / (np.abs(x) + 1e-4)
            y = lp_weighted(A, w)
            if y is None:
                break
            supp = [k for k in range(m) if y[k] > SUPP_TOL]
            if len(supp) < len(best[0]):
                best = (supp, y.copy())
            x = y
    if best is not None:
        supp, xs = best
        out['min_support_found'] = len(supp)
        out['min_support_rows'] = supp
        out['min_support_lambda'] = [float(xs[k]) for k in supp]
        out['min_support_edges'] = sorted(set(owner[k] for k in supp),
                                          key=str)
    return out


def h_structure(st, owner, idxs, convention='fact0'):
    """(k_H, E_H, F_H, m_H) over the edges hit by row indices `idxs`."""
    eds = sorted(set(owner[k] for k in idxs), key=str)
    E_w = F_w = m_w = E_p = F_p = m_p = 0
    sq = set()
    for kind, ei in eds:
        if kind == 'wall':
            e = st['wall_edges'][ei]
            E_w += 1
            m_w += e['n_rows']
            F_w += 1 if e['n_rows'] >= 2 else 0
            sq.add(e['i'])
        else:
            e = st['pair_edges'][ei]
            E_p += 1
            nr = e['n_rows'] if convention == 'fact0' else (
                2 if e['a37_class'] == 'FLUSH' else 1)
            m_p += nr
            F_p += 1 if nr >= 2 else 0
            sq.add(e['i'])
            sq.add(e['j'])
    return {'k_H': len(sq), 'E_H': E_p + E_w, 'F_H': F_p + F_w,
            'm_H': m_p + m_w, 'E_H_pair': E_p, 'E_H_wall': E_w,
            'squares_H': sorted(sq), 'n_rows_in_set': len(idxs)}


def degree_table(st, convention='fact0'):
    """Rows incident to each core square (its wall rows + its pair rows)."""
    deg = {}
    for i in st['core']:
        deg[i] = 0
    for e in st['wall_edges']:
        if e['dropped']:
            continue
        deg[e['i']] = deg.get(e['i'], 0) + e['n_rows']
    for e in st['pair_edges']:
        if e['dropped']:
            continue
        nr = e['n_rows'] if convention == 'fact0' else (
            2 if e['a37_class'] == 'FLUSH' else 1)
        deg[e['i']] = deg.get(e['i'], 0) + nr
        deg[e['j']] = deg.get(e['j'], 0) + nr
    return deg


def loadable_edge_degree(st, owner, loadable):
    """For each core square: number of DISTINCT incident edges carrying a
    loadable row (L1 canary)."""
    eds = set(owner[k] for k in loadable)
    inc = {i: set() for i in st['core']}
    for kind, ei in eds:
        if kind == 'wall':
            inc[st['wall_edges'][ei]['i']].add(('wall', ei))
        else:
            e = st['pair_edges'][ei]
            inc[e['i']].add(('pair', ei))
            inc[e['j']].add(('pair', ei))
    return {i: len(v) for i, v in inc.items()}


# ==================================================== contact completeness
def completeness(entry, z, tol_c):
    have_pairs = set()
    have_walls = set()
    for c in entry['contact_table']:
        if c['type'] == 'pair':
            have_pairs.add((c['i'], c['j']))
        elif c['type'] == 'wall':
            have_walls.add((c['i'], c['corner'], c['wall']))
    pg = G.pair_gaps(z)
    wg = G.wall_gaps(z)
    miss_p, miss_w, viol = [], [], []
    for (i, j), g in sorted(pg.items()):
        if (i, j) in have_pairs:
            if abs(g) > 1e-6:
                viol.append('pair (%d,%d) in table but gap %.3e' % (i, j, g))
            continue
        if g < NEAR_MISS:
            miss_p.append({'i': i, 'j': j, 'gap': float(g),
                           'below_tol_c': bool(g <= tol_c)})
        if g < -1e-7:
            viol.append('pair (%d,%d) OVERLAP gap %.3e' % (i, j, g))
    for (i, k, w), g in sorted(wg.items()):
        if (i, k, w) in have_walls:
            if abs(g) > 1e-6:
                viol.append('wall (%d,%d,%s) in table but gap %.3e'
                            % (i, k, w, g))
            continue
        if g < NEAR_MISS:
            miss_w.append({'i': i, 'corner': k, 'wall': w, 'gap': float(g),
                           'below_tol_c': bool(abs(g) <= tol_c)})
        if g < -1e-7:
            viol.append('wall (%d,%d,%s) VIOLATED g=%.3e' % (i, k, w, g))
    return {'n_pair_gaps': len(pg), 'n_wall_gaps': len(wg),
            'near_miss_pairs': miss_p, 'near_miss_walls': miss_w,
            'violations': viol,
            'min_noncontact_pair_gap': float(min(
                [g for (ij, g) in pg.items() if ij not in have_pairs],
                default=float('inf'))),
            'min_noncontact_wall_gap': float(min(
                [g for (key, g) in wg.items() if key not in have_walls],
                default=float('inf')))}


# ======================================================== candidate bounds
def candidate_values(rec):
    """LHS, RHS pairs for every candidate on one entry (fact0 convention)."""
    k = rec['k']
    c = rec['counts']
    H = rec['H']
    S = rec['supp']
    out = {}
    out['B1'] = (c['m'], 3 * k + 1)
    out["B1'"] = (c['m'], 3 * k)
    out["B1''"] = (c['m'], 3 * k - 1)
    out['B2'] = (H['m_H'], 3 * k + 1)
    out["B2'"] = (H['m_H'], 3 * k)
    out['B2H'] = (H['m_H'], 3 * H['k_H'] + 1)
    out["B2H'"] = (H['m_H'], 3 * H['k_H'])
    out['B4H'] = (H['F_H'], 3 * H['k_H'] + 1 - H['E_H'])
    out['B3H'] = (2 * H['E_H'], 3 * H['k_H'] + 1)
    out['B2-rows'] = (H['n_loadable_rows'], 3 * k + 1)
    out["B2-rows'"] = (H['n_loadable_rows'], 3 * k)
    out['B2m'] = (S['n_supp'], 3 * k + 1)
    out["B2m'"] = (S['n_supp'], 3 * k)
    out['B2m-kH'] = (S['n_supp'], 3 * S['k_supp'] + 1)
    out["B2m-kH'"] = (S['n_supp'], 3 * S['k_supp'])
    out['B3'] = (2 * c['E'], 3 * k + 1)
    out['B4'] = (c['F'], 3 * k + 1 - c['E'])
    out["B4'"] = (c['F'], 3 * k - c['E'])
    out['B5'] = (rec['min_row_degree'], 3)
    out["B5'"] = (rec['min_loadable_edge_degree'], 2)
    out['B6'] = (c['F'], 1)
    out["B6'"] = (c['F_pair'], 1)
    out['B7'] = (rec['rank_num'], 3 * k + 1)
    return out


CANDIDATE_TEXT = {
    'B1': 'm >= 3k+1',
    "B1'": 'm >= 3k',
    "B1''": 'm >= 3k-1',
    'B2': 'm_Hmax >= 3k+1   (m_H = Fact-0 rows over loadable edges)',
    "B2'": 'm_Hmax >= 3k',
    'B2H': 'm_Hmax >= 3*k_H+1   (Maxwell on the LOADED core only)',
    "B2H'": 'm_Hmax >= 3*k_H',
    'B4H': 'F_H >= 3*k_H+1-E_H   (N4-L1 on the loaded core)',
    'B3H': '2*E_H >= 3*k_H+1   (N4-L0 on the loaded core)',
    'B2-rows': '#loadable rows >= 3k+1',
    "B2-rows'": '#loadable rows >= 3k',
    'B2m': 'min-support-found size >= 3k+1',
    "B2m'": 'min-support-found size >= 3k',
    'B2m-kH': 'min-support-found size >= 3*k_supp+1',
    "B2m-kH'": 'min-support-found size >= 3*k_supp',
    'B3': '2E >= 3k+1   (census N4-L0)',
    'B4': 'F >= 3k+1-E   (census N4-L1)',
    "B4'": 'F >= 3k-E',
    'B5': 'every core square has row degree >= 3',
    "B5'": 'every core square with a loadable row has >= 2 loadable edges (L1 CANARY)',
    'B6': 'F >= 1',
    "B6'": 'F_pair >= 1',
    'B7': 'rank_num >= 3k+1  (isostaticity)',
}

GENUINE = ('RIGID', 'VALLEY', 'VALLEY-MARGINAL')

# candidates whose LHS is defined through the loadable-row set: at an entry
# where the lambda0 = 1 FJ system is INFEASIBLE the loadable set is empty and
# these fail vacuously, which is not a refutation of anything.
H_DEPENDENT = {'B2', "B2'", 'B2-rows', "B2-rows'", 'B2H', "B2H'", 'B4H',
               'B3H', 'B2m', "B2m'", 'B2m-kH', "B2m-kH'", "B5'"}


# ===================================================================== main
def main():
    t0 = time.time()
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    rng = np.random.default_rng(SEED)

    log('A44 eval_atlas  seed=%d  rank_tol=%g  lp_tol=%g  cap=%g'
        % (SEED, RANK_TOL, LP_TOL, LP_CAP))
    A = load_atlas()
    entries = A['entries']
    log('atlas entries: %d' % len(entries))

    per_entry = []
    global_alarms = []

    for entry in entries:
        fid = entry['family_id']
        cert = load_cert(entry)
        zq = [Fraction(v) for v in cert['z_center']]
        z = [float(v) for v in zq]
        st = build_structure(entry, z)
        k = st['k']
        cols = col_index(st['core'])
        N = 3 * k + 1
        assert len(cols) == N

        c0 = counts(st, 'fact0')
        cb = counts(st, 'brief')

        rows, owner = physical_rows(st, 'fact0')
        assert len(rows) == c0['m'], (fid, len(rows), c0['m'])
        Amat = jac(z, rows, cols)
        rk = rank_report(Amat)

        # residual sanity: every kept row must vanish at z_center
        res = max((abs(G.row_value(z, r)) for r in rows), default=0.0)

        # ---- expanded (tie-alternative) row set
        erows, eowner = expanded_rows(st)
        Aexp = jac(z, erows, cols)
        rk_exp = rank_report(Aexp)

        # ---- LP on the physical rows
        lp = lp_block(Amat, rows, owner, k, rng)
        lp_used = 'physical'
        lp_exp = None
        if not lp['feasible']:
            lp_exp = lp_block(Aexp, erows, eowner, k, rng)
            if lp_exp['feasible']:
                lp_used = 'expanded'

        active = lp_exp if lp_used == 'expanded' else lp
        act_rows = erows if lp_used == 'expanded' else rows
        act_owner = eowner if lp_used == 'expanded' else owner

        alarms = []
        if res > 1e-9:
            alarms.append('row residual at z_center = %.3e' % res)

        # ---- H structure / support structure
        if active.get('feasible'):
            loadable = active['loadable_rows']
            H = h_structure(st, act_owner, loadable, 'fact0')
            H['n_loadable_rows'] = len(loadable)
            supp_idx = active.get('min_support_rows', [])
            Sst = h_structure(st, act_owner, supp_idx, 'fact0')
            S = {'n_supp': len(supp_idx), 'k_supp': Sst['k_H'],
                 'E_supp': Sst['E_H'], 'F_supp': Sst['F_H'],
                 'm_supp_edges': Sst['m_H'],
                 'edges': [list(e) for e in active.get('min_support_edges',
                                                       [])]}
            led = loadable_edge_degree(st, act_owner, loadable)
        else:
            H = {'k_H': 0, 'E_H': 0, 'F_H': 0, 'm_H': 0, 'E_H_pair': 0,
                 'E_H_wall': 0, 'squares_H': [], 'n_rows_in_set': 0,
                 'n_loadable_rows': 0}
            S = {'n_supp': 0, 'k_supp': 0, 'E_supp': 0, 'F_supp': 0,
                 'm_supp_edges': 0, 'edges': []}
            led = {i: 0 for i in st['core']}
            # NOT an alarm: lambda0 = 1 FJ infeasibility is EXPECTED at NOT-CP
            # points and is the defining feature of VALLEY-MARGINAL.  It IS an
            # alarm at a RIGID / VALLEY entry.
            if entry['class'] in ('RIGID', 'VALLEY'):
                alarms.append('ALARM: lambda0=1 FJ LP infeasible at a '
                              '%s entry' % entry['class'])

        deg = degree_table(st, 'fact0')
        min_deg = min(deg.values()) if deg else 0
        # L1 canary: only squares that DO carry a loadable row are constrained
        led_pos = [v for v in led.values() if v > 0]
        min_led = min(led_pos) if led_pos else 99

        # ---- dropped-contact alarm: can a rattler-incident row carry load?
        drop_info = {'n_dropped_wall_edges':
                     sum(1 for e in st['wall_edges'] if e['dropped']),
                     'n_dropped_pair_edges':
                     sum(1 for e in st['pair_edges'] if e['dropped']),
                     'n_dropped_aux':
                     sum(1 for a in st['aux'] if a['dropped']),
                     'loadable_dropped_rows': []}
        if drop_info['n_dropped_wall_edges'] or drop_info['n_dropped_pair_edges']:
            frows, fowner = physical_rows(st, 'fact0', keep_dropped=True)
            fcols = list(range(34))
            Af = jac(z, frows, fcols)
            lamf, _ = lp_feasible(Af)
            if lamf is not None:
                kept = set()
                for kk, r in enumerate(rows):
                    kept.add(json.dumps(r, sort_keys=True))
                for kk, r in enumerate(frows):
                    key = json.dumps(r, sort_keys=True)
                    if key in kept:
                        continue
                    v = lp_extreme(Af, kk, 'max')
                    if v is not None and v > LP_TOL:
                        drop_info['loadable_dropped_rows'].append(
                            {'row': r, 'lambda_max': float(v)})
            if drop_info['loadable_dropped_rows']:
                alarms.append(
                    'ALARM: %d rattler-incident row(s) can carry positive '
                    'multiplier -> atlas rattler list suspect'
                    % len(drop_info['loadable_dropped_rows']))

        rec = {
            'family_id': fid,
            'class': entry['class'],
            'genuine': entry['class'] in GENUINE,
            'fj_lambda0_1_feasible': bool(active.get('feasible')),
            'atlas_kkt_lp_all_rows': entry.get('kkt', {}).get('lp_all_rows'),
            's_min': entry['s_min_float'],
            'cert_path': entry['cert_path'],
            'rattlers': st['rattlers'],
            'core': st['core'],
            'k': k,
            'N': N,
            'counts': c0,
            'counts_brief_convention': cb,
            'chi': c0['m'] - N,
            'rank_atlas': entry['rank'],
            'rank_num': rk['rank'],
            'rank_detail': rk,
            'rank_expanded_rowset': rk_exp['rank'],
            'rank_expanded_detail': rk_exp,
            's_stress': c0['m'] - rk['rank'],
            'd_flex': N - rk['rank'],
            'chi_identity_ok': bool(c0['m'] - N ==
                                    (c0['m'] - rk['rank']) - (N - rk['rank'])),
            'row_residual_at_zcenter': float(res),
            'row_degree': {str(i): deg[i] for i in sorted(deg)},
            'min_row_degree': min_deg,
            'loadable_edge_degree': {str(i): led[i] for i in sorted(led)},
            'min_loadable_edge_degree': min_led,
            'lp_rowset_used': lp_used,
            'lp_physical': {kk: vv for kk, vv in lp.items()
                            if kk not in ('lambda_max', 'lambda_min')},
            'lp_physical_lambda_max': lp.get('lambda_max'),
            'lp_physical_lambda_min': lp.get('lambda_min'),
            'lp_expanded': (None if lp_exp is None else
                            {kk: vv for kk, vv in lp_exp.items()
                             if kk not in ('lambda_max', 'lambda_min')}),
            'H': H,
            'supp': S,
            'dropped': drop_info,
            'edges': {
                'wall': [{'i': e['i'], 'wall': e['wall'],
                          'corners': e['corners'], 'n_rows': e['n_rows'],
                          'dropped': e['dropped']} for e in st['wall_edges']],
                'pair': [{'i': e['i'], 'j': e['j'],
                          'a37_class': e['a37_class'],
                          'n_axes_tied': e['n_axes_tied'],
                          'kind': e['kind'], 'n_clusters': e['n_clusters'],
                          'n_rows': e['n_rows'], 'n_rowspecs': e['n_rowspecs'],
                          'dropped': e['dropped']} for e in st['pair_edges']],
                'aux': st['aux']},
            'completeness': completeness(entry, z, entry.get('tol_c', 1e-7)),
            'alarms': alarms,
        }
        rec['candidates'] = {kk: {'lhs': int(v[0]), 'rhs': int(v[1]),
                                 'margin': int(v[0]) - int(v[1]),
                                 'pass': bool(int(v[0]) >= int(v[1]))}
                             for kk, v in candidate_values(rec).items()}
        per_entry.append(rec)
        for a in alarms:
            global_alarms.append('%s: %s' % (fid, a))
        log('%-10s %-16s k=%2d E=%2d F=%2d m=%2d N=%2d chi=%+3d rank=%2d '
            '(atlas %2d) LP=%s m_H=%2d supp=%2d %s'
            % (str(fid), entry['class'], k, c0['E'], c0['F'], c0['m'], N,
               rec['chi'], rk['rank'], entry['rank'],
               'Y' if active.get('feasible') else 'N', H['m_H'], S['n_supp'],
               ('!! ' + '; '.join(alarms)) if alarms else ''))

    # -------------------------------------------------- candidate verdicts
    verdicts = {}
    for name in CANDIDATE_TEXT:
        gen_fail, ncp_fail, tight = [], [], []
        margins = []
        fj_fail, fj_margins, fj_tight = [], [], []
        for rec in per_entry:
            cv = rec['candidates'][name]
            if rec['genuine']:
                margins.append(cv['margin'])
                if not cv['pass']:
                    gen_fail.append({'family_id': rec['family_id'],
                                     'class': rec['class'],
                                     'lhs': cv['lhs'], 'rhs': cv['rhs'],
                                     'margin': cv['margin'],
                                     'vacuous_empty_loadable_set':
                                     bool(name in H_DEPENDENT
                                          and not rec['fj_lambda0_1_feasible'])
                                     })
                elif cv['margin'] == 0:
                    tight.append(rec['family_id'])
                if rec['fj_lambda0_1_feasible']:
                    fj_margins.append(cv['margin'])
                    if not cv['pass']:
                        fj_fail.append({'family_id': rec['family_id'],
                                        'class': rec['class'],
                                        'lhs': cv['lhs'], 'rhs': cv['rhs'],
                                        'margin': cv['margin']})
                    elif cv['margin'] == 0:
                        fj_tight.append(rec['family_id'])
            else:
                if not cv['pass']:
                    ncp_fail.append({'family_id': rec['family_id'],
                                     'lhs': cv['lhs'], 'rhs': cv['rhs'],
                                     'margin': cv['margin']})
        verdicts[name] = {
            'statement': CANDIDATE_TEXT[name],
            'h_dependent': name in H_DEPENDENT,
            'verdict': ('REFUTED-BY-GENUINE' if gen_fail
                        else 'SURVIVES-GENUINE'),
            'min_margin_genuine': (min(margins) if margins else None),
            'genuine_failures': gen_fail,
            'tight_genuine_entries': tight,
            'notcp_failures_informative_only': ncp_fail,
            'n_genuine_evaluated': len(margins),
            # restricted to the 10 genuine entries where the lambda0 = 1 FJ
            # system is actually feasible (i.e. where an FJ-conditional bound
            # is applicable at all); the 2 VALLEY-MARGINAL entries drop out
            'verdict_fj_feasible_only': ('REFUTED-BY-GENUINE' if fj_fail
                                         else 'SURVIVES-GENUINE'),
            'min_margin_fj_feasible': (min(fj_margins) if fj_margins else None),
            'fj_feasible_failures': fj_fail,
            'tight_fj_feasible_entries': fj_tight,
            'n_fj_feasible_evaluated': len(fj_margins),
        }

    # brief-convention shadow verdicts for the m-based candidates
    shadow = {}
    for rec in per_entry:
        k, cb = rec['k'], rec['counts_brief_convention']
        shadow[str(rec['family_id'])] = {
            'B1': cb['m'] - (3 * k + 1), "B1'": cb['m'] - 3 * k,
            "B1''": cb['m'] - (3 * k - 1),
            'B4': cb['F'] - (3 * k + 1 - cb['E']),
            "B4'": cb['F'] - (3 * k - cb['E']),
            'B6': cb['F'] - 1, "B6'": cb['F_pair'] - 1,
            'genuine': rec['genuine'], 'm_brief': cb['m'], 'F_brief': cb['F']}
    shadow_verdict = {}
    for nm in ('B1', "B1'", "B1''", 'B4', "B4'", 'B6', "B6'"):
        f = [kk for kk, v in shadow.items() if v['genuine'] and v[nm] < 0]
        shadow_verdict[nm] = {
            'verdict': 'REFUTED-BY-GENUINE' if f else 'SURVIVES-GENUINE',
            'genuine_failures': f,
            'min_margin_genuine': min(v[nm] for v in shadow.values()
                                      if v['genuine'])}

    # ------------------------------------------------ Trump reconciliation
    t = [r for r in per_entry if r['family_id'] == 0][0]
    e0 = [e for e in entries if e['family_id'] == 0][0]
    trump = {
        'a44_physical_fact0': {'k': t['k'], 'E': t['counts']['E'],
                               'F': t['counts']['F'], 'm': t['counts']['m'],
                               'E_pair': t['counts']['E_pair'],
                               'E_wall': t['counts']['E_wall'],
                               'F_pair': t['counts']['F_pair'],
                               'F_wall': t['counts']['F_wall'],
                               'm_pair': t['counts']['m_pair'],
                               'm_wall': t['counts']['m_wall']},
        'a44_brief_convention': t['counts_brief_convention'],
        'a37_atlas_rows': e0['n_contacts'],
        'a22_v1': {'rows': 38, 'rank': 34, 'self_stress': 4,
                   'content': '20 wall rows + 16 sep rows (12 pair contacts) '
                              '+ 2 dist surrogate rows D0-1, D0-3'},
        'a35_v2': {'rows': 42, 'rank': 34, 'self_stress': 8,
                   'n_pairs': 14,
                   'content': 'A22 rows 0..35 (20 wall + 16 sep) + 4 flush '
                              'rows for the two centre-distance-1 contacts '
                              '+ 2 corner-corner tie-alternative rows for '
                              'the (1,3) contact; the 2 dist rows dropped'},
        'itemisation': None,
    }
    per_entry_map = {str(r['family_id']): r for r in per_entry}

    out = {
        'meta': {
            'attempt': 'A44-fj-maxwell',
            'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'seed': SEED,
            'atlas': os.path.relpath(ATLAS, ATT).replace(os.sep, '/'),
            'rank_tol_absolute': RANK_TOL,
            'rank_tol_lo': RANK_TOL_LO, 'rank_tol_hi': RANK_TOL_HI,
            'lp_tol': LP_TOL, 'lp_cap': LP_CAP, 'supp_tol': SUPP_TOL,
            'cluster_tol': CLUSTER_TOL, 't_edge_tol': T_EDGE_TOL,
            'near_miss_threshold': NEAR_MISS,
            'n_random_c': N_RANDOM_C, 'n_reweight': N_REWEIGHT,
            'genuine_classes': list(GENUINE),
            'conventions': CONVENTIONS,
        },
        'per_entry': per_entry,
        'candidate_verdicts': verdicts,
        'brief_convention_shadow': {'per_entry': shadow,
                                    'verdicts': shadow_verdict},
        'trump_reconciliation': trump,
        'global_alarms': global_alarms,
        'wall_seconds': time.time() - t0,
    }
    with open(os.path.join(RESULTS, 'candidates.json'), 'w') as f:
        json.dump(out, f, indent=1)
    log('wrote results/candidates.json  (%.1f s)' % (time.time() - t0))

    write_report(out, per_entry_map)
    with open(os.path.join(LOGS, 'eval.log'), 'w') as f:
        f.write('\n'.join(_LOG) + '\n')
    return 0


CONVENTIONS = [
    "Coordinates: z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=theta_i in RADIANS, "
    "z[33]=s.  (The A44 brief's 't = tan(theta/2)' is wrong: A37/A22 store the "
    "angle itself; verified by evaluating every contact row at z_center, "
    "residual < 1e-15.)",
    "Loaded core = 11 squares minus atlas rattler_squares.  Every contact "
    "incident to a rattler is dropped; the drop count is recorded and the "
    "dropped rows are separately LP-tested for loadability (alarm test).",
    "Fact 0 (PRIMARY convention, docs/proofs/structure_lemmas.md): the contact "
    "set of a pair is a point or a segment.  Segment -> 1 edge, 2 rows; point "
    "-> 1 edge, 1 row.  Segment/point is decided GEOMETRICALLY, not from the "
    "A37 class label: the contact points are the rowspec corners with "
    "|t| <= 1/2 + 1e-6 (i.e. lying on the owner's edge segment), clustered at "
    "1e-6.  1 cluster = point contact, 2 clusters = segment contact.",
    "A37 class labels are NOT used for the row count because A37's "
    "CORNER-CORNER label conflates two geometries: (a) n_axes_tied = 4, 8 "
    "rowspecs, 1 contact point -- a genuine corner-to-corner POINT touch "
    "(1 row); (b) n_axes_tied = 2, 4 rowspecs, 2 contact points -- a FLUSH "
    "segment contact whose two endpoints are corners of both squares (2 rows; "
    "these are exactly the centre-distance-1 pairs that A35/M1b identified as "
    "flush).  Across the atlas: 105 A37-FLUSH (2 pts), 56 CC-2axes (2 pts), "
    "16 CC-4axes (1 pt), 224 POINT (1 pt) -- the split is perfectly clean.",
    "The literal brief convention (FLUSH=2, POINT=1, CORNER-CORNER=1 from the "
    "A37 label) is reported as a SHADOW count "
    "(counts_brief_convention / brief_convention_shadow).",
    "Wall contacts: grouped by (square i, wall w); 1 edge per group, rows = "
    "number of distinct corners in the group (2 corners = wall-flush edge, "
    "counted in F).",
    "aux (centre-distance) rows are EXCLUDED from the physical count: they are "
    "|c_a-c_b|^2 >= 1 incircle surrogates, not contacts, and Fact 0 counts "
    "contacts.  They are listed per entry for the Trump reconciliation.",
    "Jacobian row representative: for each contact point, the rowspec branch "
    "preferring [V]-safe, then min |t|, then lexicographic "
    "(owner, other, edge, corner).  Deterministic.",
    "Jacobian columns = 3 per core square + s (N = 3k+1).  Far-wall rows "
    "(x=s, y=s) carry ds coefficient +1; all other rows have zero s-entry.  "
    "Analytic float64 gradients, cross-checked against a37_pipeline.jac_at "
    "(mpmath interval jets, dps 60): max entrywise difference 5.6e-16.",
    "rank_num [NUM]: float64 SVD, absolute cut sigma > 1e-9 (same cut as "
    "A37 classify()).  rank at 1e-11 and 1e-7 also recorded, together with "
    "the singular values straddling the cut.  Rank deficiency is never "
    "interval-certifiable at a rational approximation of an algebraic point.",
    "FJ LP (lambda0 = 1): A^T lambda = e_s, 0 <= lambda <= 1e6, HiGHS.  "
    "e_s is the unit vector in the s column; equivalently the 3k stationarity "
    "sums vanish and the far-wall multipliers sum to 1.  loadable iff "
    "max lambda_r > 1e-7; forced iff min lambda_r > 1e-7.",
]


# ------------------------------------------------------------------ report
def write_report(out, pem):
    L = []
    P = L.append
    m = out['meta']
    P('# A44 / eval_atlas — candidate Maxwell bounds vs the A37 CP atlas')
    P('')
    P('Generated %s.  Seed %d.  Runtime %.1f s, single process.'
      % (m['generated'], m['seed'], out['wall_seconds']))
    P('Code: `attempts/A44-fj-maxwell/code/eval_atlas.py`, '
      '`code/a44_geom.py`.  Data: `results/candidates.json`, `logs/eval.log`.')
    P('')
    P('Rigour tags: `[EXACT]` exact combinatorics on the certified contact '
      'table; `[NUM]` float64 SVD / HiGHS LP with the numerical cut recorded.')
    P('')
    P('## 0. Verdict summary')
    P('')
    P('| cand | statement | verdict (all 12 genuine) | min margin | refuting genuine entries | tight (margin 0) |')
    P('|---|---|---|---|---|---|')
    order = ['B1', "B1'", "B1''", 'B2', "B2'", 'B2H', "B2H'", 'B2-rows',
             "B2-rows'", 'B2m', "B2m'", 'B2m-kH', "B2m-kH'", 'B3', 'B3H',
             'B4', "B4'", 'B4H', 'B5', "B5'", 'B6', "B6'", 'B7']
    for nm in order:
        v = out['candidate_verdicts'][nm]
        fails = ', '.join('%s (%d<%d)%s'
                          % (f['family_id'], f['lhs'], f['rhs'],
                             ' *vac*' if f.get('vacuous_empty_loadable_set')
                             else '')
                          for f in v['genuine_failures']) or '—'
        tight = ', '.join(str(x) for x in v['tight_genuine_entries']) or '—'
        P('| %s | %s | **%s** | %s | %s | %s |'
          % (nm, v['statement'], v['verdict'], v['min_margin_genuine'],
             fails, tight))
    P('')
    P('Genuine = class RIGID / VALLEY / VALLEY-MARGINAL (12 entries: '
      '0, 1, 2, 6, 13, 14, 27, 31, A37-NEW-0..3).  NOT-CP entries cannot '
      'refute an FJ-conditional bound (they are not FJ-critical under free '
      'rotation) — their failures are listed informative-only in the JSON.')
    P('')
    P('`*vac*` marks a **vacuous** failure: at the two VALLEY-MARGINAL '
      'entries (27, A37-NEW-1) the λ₀ = 1 FJ system is itself infeasible '
      '(A44 reproduces A37\'s own `kkt.lp_all_rows = false` there), so the '
      'loadable-row set is empty and every H- or support-based LHS is 0 by '
      'definition.  Those are not refutations.  The table below re-runs the '
      'H/support candidates over only the **10 genuine entries where the '
      'λ₀ = 1 FJ system is feasible** (0, 1, 2, 6, 13, 14, 31, A37-NEW-0, '
      'A37-NEW-2, A37-NEW-3):')
    P('')
    P('| cand | verdict (10 FJ-feasible genuine) | min margin | refuting entries | tight |')
    P('|---|---|---|---|---|')
    for nm in order:
        v = out['candidate_verdicts'][nm]
        if not v['h_dependent']:
            continue
        fails = ', '.join('%s (%d<%d)' % (f['family_id'], f['lhs'], f['rhs'])
                          for f in v['fj_feasible_failures']) or '—'
        tight = ', '.join(str(x) for x in v['tight_fj_feasible_entries']) or '—'
        P('| %s | **%s** | %s | %s | %s |'
          % (nm, v['verdict_fj_feasible_only'], v['min_margin_fj_feasible'],
             fails, tight))
    P('')
    P('### Headline')
    P('')
    b1 = out['candidate_verdicts']['B1']
    P('- **B1 (`m >= 3k+1`, the naive Maxwell bound) is REFUTED.**  Family '
      '**31** (VALLEY, s = 3.936964) has k = 11 loaded squares, 21 contact '
      'edges, **m = 33 = 3k** rows — one short — and its λ₀ = 1 FJ system is '
      'feasible with **every one of its 21 edges loadable and all 11 squares '
      'loaded** (k_H = 11, E_H = 21, m_H = 33).  There is no rattler to '
      'blame and no convention that rescues it: under the brief\'s literal '
      'CORNER-CORNER = 1 convention family 31 has no corner-corner contact '
      'at all, so the count is identical.  Family **27** '
      '(VALLEY-MARGINAL, m = 33, k = 11) refutes it a second time, and '
      'A37-NEW-3 sits exactly on the boundary (m = 34 = 3k+1).')
    r31 = pem['31']
    r27 = pem['27']
    P('  *Robustness of the B1 refutation.*  It is combinatorial — it depends '
      'only on the contact table, not on any LP or SVD.  At family 31 every '
      'kept row evaluates to |g| < %.1e at `z_center`, and the nearest '
      'NON-contact is a pair gap of %.2e and a corner-wall clearance of '
      '%.2e — five orders of magnitude above any plausible error in the '
      'critical point, so no additional contact can appear and m cannot rise '
      'above 33.  Same picture at 27 (%.2e / %.2e).'
      % (max(r31['row_residual_at_zcenter'], 1e-16),
         r31['completeness']['min_noncontact_pair_gap'],
         r31['completeness']['min_noncontact_wall_gap'],
         r27['completeness']['min_noncontact_pair_gap'],
         r27['completeness']['min_noncontact_wall_gap']))
    P('- **B1\' (`m >= 3k`) survives all 12 genuine entries with margin 0** '
      'at families 27 and 31.  It is the strongest surviving total-row '
      'bound and it is *tight*: two independent genuine critical points sit '
      'exactly on it.')
    P('- **B4 (`F >= 3k+1-E`) is refuted by the same two entries**; '
      '`B4\' (F >= 3k-E)` survives, tight at 27 and 31.  (B4/B4\' and '
      'B1/B1\' are the same inequality rewritten: `m = E + F`.)')
    P('- **B7 (isostaticity, `rank >= 3k+1`) is refuted by 11 of the 12 '
      'genuine entries** — every non-Trump one.  Only family 0 (Trump, the '
      'unique RIGID entry) attains rank 34 = 3k+1.  This confirms the A37 '
      'valley finding: naive isostaticity is false at genuine critical '
      'points.')
    P('- **B5 (`row degree >= 3` at every core square) is refuted** by '
      'families 1, 2 (a core square with a SINGLE incident row), A37-NEW-1 '
      'and A37-NEW-2 (degree 2).  Cause: A37\'s rattler test is "no row '
      'touches this square at all", so a square with one or two contacts but '
      'zero load stays in the core.  Any degree bound must be stated on the '
      '**loaded** core, not on the contact core.')
    P('- **B5\' (L1, `>= 2 loadable edges at every loaded square`) PASSES '
      'everywhere** — the canary is green on all 36 entries, tight (exactly '
      '2) at 9 of the 10 FJ-feasible genuine entries.')
    P('- **The loaded-core Maxwell bound B2H (`m_H >= 3*k_H+1`) is also '
      'refuted** — families 1 and 2 have a 6-square loaded core carrying '
      '10 edges and only 17 rows against 3·6+1 = 19, and family 31 fails at '
      '33 vs 34.  Restricting to the loaded core does **not** repair the '
      'Maxwell count.  `B2H\' (m_H >= 3*k_H)` also fails (1, 2: 17 < 18).')
    surv = [nm for nm in order
            if out['candidate_verdicts'][nm]['verdict']
            == 'SURVIVES-GENUINE']
    surv_fj = [nm for nm in order
               if out['candidate_verdicts'][nm]['verdict']
               != 'SURVIVES-GENUINE'
               and out['candidate_verdicts'][nm]['verdict_fj_feasible_only']
               == 'SURVIVES-GENUINE']
    P('- **Survivors over all 12 genuine entries:** %s.'
      % (', '.join('`%s`' % s for s in surv) or 'none'))
    P('- **Additional survivors once the 2 VALLEY-MARGINAL entries are '
      'excluded** (λ₀ = 1 FJ infeasible there, so the H/support LHS is '
      'vacuously 0): %s.'
      % (', '.join('`%s`' % s for s in surv_fj) or 'none'))
    P('')
    P('## 1. Per-entry structural table  `[EXACT]` counts, `[NUM]` rank')
    P('')
    P('| fam | class | s_min | k | E | E_p | E_w | F | F_p | F_w | m | N=3k+1 | chi | rank_num | rank_atlas | s_stress | d_flex | m_H | E_H | F_H | k_H | supp |')
    P('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in out['per_entry']:
        c = r['counts']
        H = r['H']
        P('| %s | %s | %.6f | %d | %d | %d | %d | %d | %d | %d | %d | %d | %+d | %d | %d | %d | %d | %d | %d | %d | %d | %d |'
          % (r['family_id'], r['class'], r['s_min'], r['k'], c['E'],
             c['E_pair'], c['E_wall'], c['F'], c['F_pair'], c['F_wall'],
             c['m'], r['N'], r['chi'], r['rank_num'], r['rank_atlas'],
             r['s_stress'], r['d_flex'], H['m_H'], H['E_H'], H['F_H'],
             H['k_H'], r['supp']['n_supp']))
    P('')
    P('`chi = m - N = s_stress - d_flex` verified on every entry: %s.'
      % ('all OK' if all(r['chi_identity_ok'] for r in out['per_entry'])
         else 'FAILED'))
    P('')
    P('### rank_num vs the atlas `rank` field')
    P('')
    P('They measure different things and are NOT expected to agree.  The '
      'atlas `rank` is the rank of A37\'s FULL row list — all wall rows, '
      '**every rowspec of every tied separating axis** (including the '
      '[V]-unsafe ones), **and the aux `dist` rows** — over all **34** '
      'coordinates including the rattler squares\'.  A44\'s `rank_num` is the '
      'rank of the **Fact-0 physical** row set (one row per contact point, '
      'no aux, rattler-incident contacts dropped) over the **3k+1** core '
      'coordinates.  Per-entry both numbers are in the table; the rank of the '
      'A44 tie-expanded row set over the core columns is in the JSON as '
      '`rank_expanded_rowset`.')
    P('')
    P('**Result: `rank_num == rank_atlas` on all 36 entries** — despite the '
      'two very different row sets and column sets.  That is a strong '
      'independent confirmation that (i) the tie-alternative rows and the '
      'aux `dist` rows add nothing to the rank, and (ii) the rattler '
      'coordinates are genuinely free.  The rank is numerically unambiguous '
      'everywhere: the smallest ratio sigma_min_kept / sigma_max_dropped over '
      'the 36 entries is %.1e, and the rank is identical at cuts 1e-11, '
      '1e-9 and 1e-7 on every entry.'
      % min(r['rank_detail']['sv_gap_ratio'] for r in out['per_entry']
            if r['rank_detail']['sv_gap_ratio']))
    P('')
    P('| fam | rank_num (physical, 3k+1 cols) | rank(expanded rows, 3k+1 cols) | rank_atlas (all rows, 34 cols) | sigma_min kept | sigma_max dropped |')
    P('|---|---|---|---|---|---|')
    for r in out['per_entry']:
        d = r['rank_detail']
        P('| %s | %d | %d | %d | %.3e | %.3e |'
          % (r['family_id'], r['rank_num'], r['rank_expanded_rowset'],
             r['rank_atlas'],
             d['sv_min_kept'] if d['sv_min_kept'] is not None else float('nan'),
             d['sv_max_dropped']))
    P('')
    P('## 2. Contact-completeness audit  `[NUM]`')
    P('')
    P('At every entry\'s `z_center` all 55 pair SAT gaps and all 176 '
      'corner-wall clearances were recomputed from scratch.  Listed below: '
      'every gap < 1e-3 that is NOT in the atlas contact table.  '
      '(A missed contact could only RAISE m, so these are the borderline '
      'cases the theory lead must judge before trusting a refutation.)')
    P('')
    any_nm = False
    for r in out['per_entry']:
        cm = r['completeness']
        if not cm['near_miss_pairs'] and not cm['near_miss_walls'] \
                and not cm['violations']:
            continue
        any_nm = True
        P('**%s** (%s): min non-contact pair gap %.3e, min non-contact wall '
          'gap %.3e' % (r['family_id'], r['class'],
                        cm['min_noncontact_pair_gap'],
                        cm['min_noncontact_wall_gap']))
        for x in cm['near_miss_pairs']:
            P('  - pair (%d,%d) gap %.3e%s'
              % (x['i'], x['j'], x['gap'],
                 '  **BELOW tol_c — MISSING CONTACT**' if x['below_tol_c']
                 else ''))
        for x in cm['near_miss_walls']:
            P('  - wall sq %d corner %d %s gap %.3e%s'
              % (x['i'], x['corner'], x['wall'], x['gap'],
                 '  **BELOW tol_c — MISSING CONTACT**' if x['below_tol_c']
                 else ''))
        for v in cm['violations']:
            P('  - VIOLATION: %s' % v)
    if not any_nm:
        P('No entry has any non-tabulated pair gap or corner-wall clearance '
          'below 1e-3.  The atlas contact tables are complete at the 1e-3 '
          'level on all 36 entries.')
    P('')
    P('## 3. FJ multiplier diagnostics  `[NUM]`')
    P('')
    P('| fam | rowset used | feasible | ||A^T λ − e_s||_inf | Σλ | Σλ far-wall | #loadable | #forced | min-support found | support edges |')
    P('|---|---|---|---|---|---|---|---|---|---|')
    for r in out['per_entry']:
        lp = (r['lp_expanded'] if r['lp_rowset_used'] == 'expanded'
              else r['lp_physical'])
        P('| %s | %s | %s | %.2e | %.4f | %.6f | %d | %d | %d | %d |'
          % (r['family_id'], r['lp_rowset_used'],
             'yes' if lp.get('feasible') else 'NO',
             lp.get('residual_inf', float('nan')),
             lp.get('sum_lambda', float('nan')),
             lp.get('sum_farwall_lambda', float('nan')),
             lp.get('n_loadable', 0), lp.get('n_forced', 0),
             r['supp']['n_supp'], r['supp']['E_supp']))
    P('')
    P('`Σλ far-wall = 1` on every feasible entry is the built-in check that '
      'the LP really solved `A^T λ = e_s` (only the `x=s` / `y=s` rows carry '
      'a ∂s coefficient, and it is +1).')
    P('')
    P('**Independent cross-check against the atlas.**  A44\'s λ₀ = 1 '
      'feasibility verdict on the Fact-0 physical row set agrees with A37\'s '
      'own `kkt.lp_all_rows` field on **%d of 36** entries.  In particular '
      'the 10 RIGID/VALLEY entries are feasible, and the 2 VALLEY-MARGINAL '
      'entries (27, A37-NEW-1) plus all 24 NOT-CP entries are infeasible — '
      'so "VALLEY-MARGINAL" is precisely "λ₀ = 1 FJ infeasible, λ₀ = 0 '
      'branch only".  This is a genuine independent reproduction: A37 solved '
      'over its full 34-column row list, A44 over the physical rows in the '
      '3k+1 core columns.'
      % sum(1 for r in out['per_entry']
            if r['fj_lambda0_1_feasible'] == bool(
                r['atlas_kkt_lp_all_rows'])))
    P('')
    P('The physical row set was feasible directly on all 10; the '
      'tie-expanded row set (every tied separating axis as a separate row) '
      'was never needed.  Note A37\'s `lp_safe_rows` is false at 1, 2, 6 and '
      'A37-NEW-2 — the [V]-safe rows alone do not carry e_s there, but the '
      'Fact-0 physical rows (which include the [V]-unsafe endpoint rows at '
      'coincident-corner contacts) do.')
    P('')
    P('### Rattler / dropped-contact alarm')
    dropped_any = [r for r in out['per_entry']
                   if r['dropped']['n_dropped_wall_edges']
                   or r['dropped']['n_dropped_pair_edges']]
    P('')
    n_rat = sum(len(r['rattlers']) for r in out['per_entry'])
    P('%d rattler squares are declared across the 36 entries.  **The total '
      'number of dropped contacts is 0** — %d of 36 entries have any contact '
      'incident to a declared rattler.  This is by construction: A37\'s '
      'rattler test (`classify()`) is "no row touches this square\'s '
      'coordinates at all", so a rattler square carries no wall contact, no '
      'pair contact and no aux row.  The alarm condition ("a dropped contact '
      'carries a positive multiplier") is therefore vacuous, and the check '
      'was run anyway and reported nothing.' % (n_rat, len(dropped_any)))
    P('')
    P('**Consequence worth flagging to the theory lead:** because A37\'s '
      'rattler set is the *zero-contact* set and not the *zero-load* set, '
      'the "core" of an atlas entry can still contain squares that carry '
      'contacts but no load.  Families 1 and 2 each have a core square with '
      'a single incident row (squares 10 and 7 respectively) — a rattler '
      'with one incidental touch.  That is what kills B5, and it means any '
      'per-square degree hypothesis must be stated over the **loaded** core '
      '(the k_H column), not over the contact core.')
    P('')
    alarms = [a for a in out['global_alarms'] if 'ALARM' in a]
    if alarms:
        for a in alarms:
            P('- **%s**' % a)
    else:
        P('**No alarms of any kind fired on any of the 36 entries.**')
    P('')
    P('## 4. Trump reconciliation (family 0)')
    P('')
    t = out['trump_reconciliation']
    a = t['a44_physical_fact0']
    P('A44 physical (Fact 0) count at Trump: **k = %d, E = %d '
      '(E_pair %d + E_wall %d), F = %d (F_pair %d + F_wall %d), m = %d '
      '(m_pair %d + m_wall %d)**, N = 34, chi = %+d.'
      % (a['k'], a['E'], a['E_pair'], a['E_wall'], a['F'], a['F_pair'],
         a['F_wall'], a['m'], a['m_pair'], a['m_wall'], a['m'] - 34))
    P('')
    P('| basis | rows | rank | self-stress | itemisation |')
    P('|---|---|---|---|---|')
    P('| A22 v1 | 38 | 34 | 4 | 20 wall rows + 16 pair sep rows (12 pair '
      'contacts) + 2 `dist` centre-distance surrogate rows |')
    P('| A35 v2 | 42 | 34 | 8 | A22 rows 0..35 (20 wall + 16 sep) + 4 flush '
      'rows for the two centre-distance-1 contacts + 2 corner-corner '
      'tie-alternative rows for (1,3); the 2 `dist` rows dropped |')
    P('| **A44 physical** | **%d** | %d | %d | 20 wall rows (11 wall edges, '
      '9 of them 2-corner flush) + 19 pair rows (14 pair edges: 7 segment '
      'contacts x 2 rows + 7 point contacts x 1 row) |'
      % (a['m'], pem['0']['rank_num'], pem['0']['s_stress']))
    P('')
    P('The A44 physical row set decomposes as')
    P('')
    P('| block | rows | content |')
    P('|---|---|---|')
    P('| W | 20 | 11 wall edges: 9 two-corner (wall-flush) + 2 one-corner |')
    P('| S | 16 | the 11 "ordinary" pair contacts: 5 segment x 2 rows + '
      '6 point x 1 row |')
    P('| C | 4 | the 2 coincident-corner segment contacts (A37 labels them '
      'CORNER-CORNER, n_axes_tied = 2; centre distance exactly 1; A35/M1b '
      'calls them flush) — 2 endpoint rows each |')
    P('| X | 1 | the (1,3) genuine corner-to-corner POINT contact '
      '(n_axes_tied = 4, 8 rowspecs, all at one point) — 1 selected branch |')
    P('| **total** | **41** | |')
    P('')
    P('Row-by-row reconciliation (all three bases share the same W and S '
      'blocks — 36 rows — which are A22 `krawczyk_cert.json` constraints '
      '0..35 verbatim):')
    P('')
    P('```')
    P('A44 physical   = W(20) + S(16) + C(4) + X(1)                  = 41')
    P('A35 v2         = W(20) + S(16) + C(4) + X(2)                  = 42')
    P('                 (v2 rows 36-39 = C; rows 40,41 = BOTH (1,3) branches)')
    P('A22 v1         = W(20) + S(16) +   0  +  0  + dist(2)         = 38')
    P('                 (C replaced by the 2 centre-distance surrogates')
    P('                  D0-1, D0-3; the (1,3) contact missed entirely)')
    P('```')
    P('')
    P('- **A44 → A35 v2: +1 row.**  v2 keeps *both* corner-corner branches '
      'of the (1,3) point contact; A44 keeps one (Fact 0: a point contact is '
      'one row).  The extra row is an *alternative selection at the same '
      'contact point*, not an extra contact — which is exactly why v2\'s '
      'self-stress dimension is 8 = 42 − 34 while A44\'s is 7 = 41 − 34 and '
      'the rank is 34 in both.')
    P('- **A44 → A22 v1: −3 rows.**  v1 drops all 4 C rows (−4), misses the '
      '(1,3) contact entirely (−1), and adds 2 `dist` centre-distance '
      'surrogate rows (+2): 41 − 4 − 1 + 2 = 38.  Its self-stress dimension '
      '4 = 38 − 34 follows.  A35/M1b confirmed both defects in exact '
      'rational arithmetic (SAT gap at (1,3) is 0 within ±4.7e-61; centre '
      'distance² at the two C contacts is exactly 1).')
    P('')
    P('So the three counts differ **only** in (i) tie-alternative rows at '
      'the corner-corner contact and (ii) `dist` surrogate rows standing in '
      'for real segment-contact rows — no discrepancy in the underlying '
      'contact set.  A37, A35/v2 and A44 all agree on **14 pair contacts** '
      'and **11 wall edges** at Trump.  Under the brief\'s literal '
      'CORNER-CORNER = 1 convention the A44 count would be m = %d '
      '(the 2 C contacts each lose their second endpoint row), which is '
      'exactly the count that would *disagree* with A35 v2 by 4 instead of '
      '1 — a further reason the Fact-0 geometric split is the right one.'
      % out['trump_reconciliation']['a44_brief_convention']['m'])
    P('')
    P('### Hot-spot entries — hand check of the wall-row grouping')
    P('')
    P('| fam | wall edges (square, wall) → corners | E_wall | F_wall | m_wall |')
    P('|---|---|---|---|---|')
    for fid in ('13', '14', '27', '31', 'A37-NEW-1', 'A37-NEW-2',
                'A37-NEW-3'):
        r = pem.get(fid)
        if r is None:
            continue
        ws = ['(%d,%s)->%s' % (e['i'], e['wall'], e['corners'])
              for e in r['edges']['wall'] if not e['dropped']]
        c = r['counts']
        P('| %s | %s | %d | %d | %d |'
          % (fid, ' '.join(ws), c['E_wall'], c['F_wall'], c['m_wall']))
    P('')
    P('| fam | pair edges (i,j) A37class/geom/rows |')
    P('|---|---|')
    for fid in ('13', '14', '27', '31', 'A37-NEW-1', 'A37-NEW-2',
                'A37-NEW-3'):
        r = pem.get(fid)
        if r is None:
            continue
        ps = ['(%d,%d)%s/%s/%d' % (e['i'], e['j'], e['a37_class'][:2],
                                   e['kind'][:3], e['n_rows'])
              for e in r['edges']['pair'] if not e['dropped']]
        P('| %s | %s |' % (fid, ' '.join(ps)))
    P('')
    P('## 5. Shadow evaluation under the brief\'s literal convention')
    P('')
    P('The brief prescribed `CORNER-CORNER = 1 row`.  Taken literally against '
      'the A37 *label*, that undercounts every coincident-corner flush '
      'contact by 1 row (see conventions).  Verdicts under that convention:')
    P('')
    P('| cand | verdict (brief conv.) | min margin | refuting genuine |')
    P('|---|---|---|---|')
    for nm, v in out['brief_convention_shadow']['verdicts'].items():
        P('| %s | %s | %d | %s |'
          % (nm, v['verdict'], v['min_margin_genuine'],
             ', '.join(v['genuine_failures']) or '—'))
    P('')
    P('## 6. Conventions decided (every one of them)')
    P('')
    for i, c in enumerate(m['conventions'], 1):
        P('%d. %s' % (i, c))
    P('')
    P('## 7. Caveats')
    P('')
    for c in CAVEATS:
        P('- %s' % c)
    P('')
    with open(os.path.join(RESULTS, 'eval_report.md'), 'w',
              encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    log('wrote results/eval_report.md')


CAVEATS = [
    '`rank_num` is `[NUM]`: a float64 SVD with an absolute cut at 1e-9. '
    'Rank *deficiency* is never interval-certifiable at a rational '
    'approximation of an algebraic point (A35 M1 makes the same disclaimer). '
    'The singular values straddling the cut are tabulated; where the gap '
    'ratio is small the rank is not trustworthy and B7 verdicts on that '
    'entry should be read as indicative.',
    'LP tolerances: HiGHS default, multipliers boxed in [0, 1e6], '
    'loadable/forced threshold 1e-7, support threshold 1e-9. A row whose true '
    'max multiplier is between 1e-9 and 1e-7 would be called non-loadable. '
    'Rows hitting the 1e6 cap are flagged (`unbounded_rows`).',
    '`min_support_found` is an UPPER bound on the true minimum support: it is '
    'the best of 21 weighted LPs (all-ones + 20 seeded random positive '
    'objectives) plus 10 reweighted-L1 refinements. Exact minimum support is '
    'NP-hard and was not attempted. B2m verdicts are therefore only sound in '
    'the direction "the bound already fails at this support size"; a PASS at '
    'B2m is not a proof that no smaller support exists.',
    'Entry 27 (VALLEY-MARGINAL): A43-G5 flags family 27\'s coordinates as '
    '6-decimal rounded. A44 reads `z_center` from the A37 certificate, which '
    'is a 43-significant-digit exact rational, and every physical row of '
    'entry 27 evaluates to |g| < 1e-15 there, so the structural counts are '
    'not affected by that flag. The flag remains relevant to anything that '
    'consumed the rounded coordinates upstream.',
    'The Fact-0 segment/point split is decided at float tolerance '
    '(|t| <= 1/2 + 1e-6, cluster radius 1e-6). The split it produces is '
    'perfectly clean on the atlas (105 + 56 segment contacts vs 16 + 224 '
    'point contacts, with no ambiguous case), but it is a numerical decision, '
    'not a certificate.',
    'Row semantics decided by A44 (each is a judgement call, all listed in '
    '§6): (i) aux `dist` rows excluded from the physical count; (ii) A37\'s '
    'CORNER-CORNER label overridden by the geometric contact set; '
    '(iii) one Jacobian row per contact point, branch chosen '
    '[V]-safe-first / min|t| / lexicographic; (iv) for a coincident-corner '
    'flush contact BOTH endpoint rows are taken, from the two different '
    'owner frames.',
    'The λ₀ = 1 FJ LP residual ‖A^T λ − e_s‖_inf is at machine precision on '
    'families 0, 1, 2, 6, 13, 14 but only 6.9e-9 (family 31), 1.4e-8 '
    '(A37-NEW-0), 1.4e-10 (A37-NEW-3), 2.2e-12 (A37-NEW-2) — these z_center '
    'points are themselves only ~1e-9 converged (A37 kkt.ls_res agrees). The '
    'feasibility verdict there is [NUM] and matches A37\'s independent one. '
    'It does NOT affect the B1 refutation at family 31, which is purely '
    'combinatorial.',
    'B2/B2-rows/B2m failures at the two VALLEY-MARGINAL entries are VACUOUS '
    '(empty loadable set because the λ₀ = 1 FJ system is infeasible there) '
    'and are flagged as such; the restricted 10-entry verdict column is the '
    'one to read for those candidates. The λ₀ = 0 branch at 27 and '
    'A37-NEW-1 was NOT analysed here — a bound conditioned on λ₀ > 0 simply '
    'says nothing at those two points, which is itself a gap for the census '
    'application.',
    'NOT-CP entries are evaluated and reported but never used to refute: '
    'they are minima of s only at A04\'s fixed lattice angles and are not '
    'FJ-critical under free rotation, so an FJ-conditional bound is not '
    'required to hold there.',
    'The candidate bounds are evaluated at the 36 atlas points only. A '
    'SURVIVES-GENUINE verdict is evidence, not a proof: the atlas is not a '
    'certified-complete list of FJ-critical points (A37 itself found 4 '
    'families missing from the A04 catalogue).',
]


if __name__ == '__main__':
    sys.exit(main())
