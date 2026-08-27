"""m3_gained.py -- A35 / M3: codim profile with GAINED contacts + interval extension.

Closes M1's gaps G-a (gained rows re-feed the cone), G-b (everything was at
z-hat only), G-e (the force-balance cascade was not interval-extended).

  Task 1  GAINED-MENU RE-SCREEN   -> corrected cone-alive family / work queue,
                                     as a function of the travel cap R
  Task 2  FARKAS INTERVAL RADIUS  -> certified radius of the cone kills,
                                     with and without the gained menu
  Task 3  CASCADE INTERVAL RADIUS -> radius of validity of the force-balance rule
  Task 4  COMPLETENESS            -> what escapes cone+gained+empty+collapse+D2

RIGOUR TAGS (M1 convention):
  [IV]    mpmath.iv, dps 60, over box(z-hat, r).  Rigorous.
  [RFP]   Rump preconditioned nonsingularity.  Rigorous mod IEEE-754.
  [EXACT] exact rational / exact combinatorics.
  [NUM]   float64 LP / SVD.  Used for SEARCH and for counting; every kill
          verdict that carries weight is re-verified [IV] (Task 2).

HONESTY NOTE threaded through: gradients of GAINED rows are evaluated at z-hat
even though the contact they describe forms elsewhere in the box.  Task 1
records the [IV] gradient DRIFT of every gained row over box(z-hat, R) next to
every conclusion drawn from it; Task 2 redoes the kills with interval gradients
over the whole box, which is drift-free.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
RESULTS = os.path.abspath(os.path.join(HERE, '..', 'results'))
os.makedirs(RESULTS, exist_ok=True)
OUT_JSON = os.path.join(RESULTS, 'm3_screen.json')

import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60
mp.dps = 60

NV, NGEO, SIDX = SL.NV, SL.NGEO, SL.S_IDX
SEED = 20260827
T0 = time.time()


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


# ======================================================================
# shared data
# ======================================================================
ZHAT = SL.z_hat()
ZBOX = SL.point_box()
ROWS = SL.geo_rows()
RNAMES = SL.row_names()
CONS = SL.geo_constraints()
_, Amid, Arad, _ = SL.jacobian()

PAIR_ROWS = [k for k, c in enumerate(CONS) if c['kind'] in ('edge', 'dist')]
WALL_ROWS = [k for k, c in enumerate(CONS) if c['kind'] == 'wall']
assert len(PAIR_ROWS) == 18

M1 = json.load(open(os.path.join(RESULTS, 'm1_strata.json')))
M1_ALIVE = set(tuple(b) for b in M1['task3']['surviving_breakset_list'])
M1_SURV = set(tuple(b) for b in M1['synthesis']['global_exhaustive']['survivors'])
TEN_FAMILY = M1['task3']['rows_by_family']['union_of_all_Z']
M1_SINGLETON_KILLERS = sorted(set(range(NGEO)) - set(TEN_FAMILY))

RLIST = [Fraction(1, 200), Fraction(1, 100), Fraction(1, 50), Fraction(1, 20)]
R_MAIN = Fraction(1, 20)                                   # the brief's 0.05
RADII = sorted(set([Fraction(1, 1000) * 2 ** j for j in range(8)])
               | set(RLIST))                               # 1e-3 .. 0.128


def fkey(R):
    return '%g' % float(R)


# ======================================================================
# GAINED MENU, as a function of the travel cap R
# ======================================================================
def _mv_bounds(row, R, box):
    """Mean-value enclosure of row value over box(z-hat,R):
       row(z) in row(z-hat) +/- ||grad||_1,box * R.     [IV], sound
    (Much tighter than the naive interval evaluation of the expression, which
    is dependency-pessimistic; both are sound, the tighter one is used.)"""
    v0 = t3lib.row_value(ZBOX, row)
    _, g = t3lib.row_grad(box, row)
    L = sum(max(abs(mp.mpf(x.a)), abs(mp.mpf(x.b))) for x in g.values())
    d = L * (mp.mpf(R.numerator) / R.denominator)
    return mp.mpf(v0.a) - d, mp.mpf(v0.b) + d, float(L)


def build_menu(R):
    """Gained-contact rows admissible at travel cap R.

    TWO independent necessary conditions, intersected (both sound):
      (1) PAIR GATE: the pair's SAT gap must be able to reach 0 on box(z-hat,R)
          -- M1's task-4 candidate table (Lipschitz screen AND interval scan).
          A gained row can only be active where its pair actually touches:
          sep = 0 together with dom >= 0 forces contact.
      (2) SELECTION GATE: for each of the 32 (owner, edge, corner) selections
          of the pair, every one of its 4 rows must be able to be >= 0 on the
          box, and its SEP row must be able to reach 0 there -- both via the
          mean-value enclosure above.
    """
    box = t3lib.box_from(ZHAT, R)
    pairs = [tuple(p) for p in
             M1['task4']['candidate_table']['R=%s' % fkey(R)]['candidate_pairs']]
    sel = []
    dom = []
    per_pair = {}
    for (i, j) in pairs:
        cnt = 0
        for o, p in ((i, j), (j, i)):
            for e in range(4):
                for k in range(4):
                    rows = ([t3lib.sep_row(o, e, p, k)]
                            + [t3lib.dom_row(o, e, p, k, m)
                               for m in range(4) if m != k])
                    bnds = [_mv_bounds(r, R, box) for r in rows]
                    if any(b[1] < 0 for b in bnds):
                        continue                    # certified infeasible on box
                    lo, hi, L = bnds[0]
                    if not (lo <= 0 <= hi):
                        continue                    # sep cannot reach 0
                    cnt += 1
                    sel.append({'pair': [i, j], 'o': o, 'e': e, 'p': p, 'k': k,
                                'row': rows[0],
                                'name': t3lib.row_name(rows[0]),
                                'sep_at_zhat': float(t3lib.row_value(ZBOX, rows[0]).b),
                                'grad_1norm_on_box': L,
                                'mv_range_on_box': [float(lo), float(hi)]})
                    for r, b in zip(rows[1:], bnds[1:]):
                        if b[0] <= 0 <= b[1]:
                            dom.append({'row': r, 'name': t3lib.row_name(r)})
        per_pair['%d-%d' % (i, j)] = cnt
    seen, dm = set(), []
    for d in dom:
        kk = t3lib.row_key(d['row'])
        if kk not in seen:
            seen.add(kk)
            dm.append(d)
    return {'R': R, 'pairs': pairs, 'sel': sel, 'dom': dm, 'per_pair': per_pair}


def grads_at_zhat(rows):
    A = np.zeros((len(rows), NV))
    for k, r in enumerate(rows):
        _, g = t3lib.row_grad(ZBOX, r)
        for gi, v in g.items():
            A[k, gi] = float(mp.mpf(v.a) + mp.mpf(v.b)) / 2.0
    return A


MENUS = {}
for _R in RLIST:
    m = build_menu(_R)
    m['rows'] = [s['row'] for s in m['sel']]
    m['G'] = grads_at_zhat(m['rows'])
    m['domrows'] = [d['row'] for d in m['dom']]
    m['GD'] = grads_at_zhat(m['domrows'])
    MENUS[fkey(_R)] = m
    log('menu R=%s: pairs %s -> %d sep rows %s, %d straddling dom rows'
        % (fkey(_R), m['pairs'], len(m['sel']), m['per_pair'], len(m['dom'])))

MENU_MAIN = MENUS[fkey(R_MAIN)]


def menu_for_radius(r):
    """The menu appropriate to a verification box of radius r (the smallest
    tabulated cap >= r; for r above the largest cap, the largest menu)."""
    for R in RLIST:
        if r <= R:
            return MENUS[fkey(R)]
    return MENUS[fkey(RLIST[-1])]


# ======================================================================
# cone tests
# ======================================================================
def cone_alive(M, G=None, extra=None):
    """Is e_s in cone{grad g_m : m in M} + cone{rows of G}?   [NUM] LP."""
    cols = [Amid[m] for m in M]
    if G is not None and len(G):
        cols += list(G)
    if extra is not None and len(extra):
        cols += list(extra)
    if not cols:
        return False, None
    A_eq = np.array(cols).T
    b = np.zeros(NV)
    b[SIDX] = 1.0
    r = linprog(np.zeros(A_eq.shape[1]), A_eq=A_eq, b_eq=b, bounds=(0, None),
                method='highs')
    return bool(r.status == 0), (r.x if r.status == 0 else None)


def farkas_direction(M, G=None, extra=None, ybound=50.0, den=10 ** 9):
    """Max-margin Farkas y at z-hat, rationalised at denominator `den`."""
    rowsA = [Amid[m] for m in M]
    if G is not None and len(G):
        rowsA += list(G)
    if extra is not None and len(extra):
        rowsA += list(extra)
    A_ub = np.zeros((len(rowsA), NV + 1))
    A_ub[:, :NV] = -np.array(rowsA)
    A_ub[:, NV] = 1.0
    c = np.zeros(NV + 1)
    c[NV] = -1.0
    bnds = [(-ybound, ybound)] * NV + [(0, 100.0)]
    bnds[SIDX] = (-1.0, -1.0)
    r = linprog(c, A_ub=A_ub, b_ub=np.zeros(len(rowsA)), bounds=bnds,
                method='highs')
    if not r.success:
        return None, 0.0
    t = float(-r.fun)
    if t <= 1e-12:
        return None, t
    y = [Fraction(round(Fraction(float(v)) * den), den) for v in r.x[:NV]]
    y[SIDX] = Fraction(-1)
    return y, t


# ---- interval gradient caches, one per radius ------------------------------
_GC = {}


def grad_cache(R):
    key = fkey(R) if R else '0'
    if key in _GC:
        return _GC[key]
    box = ZBOX if not R else t3lib.box_from(ZHAT, R)
    c = {}
    for k, r in enumerate(ROWS):
        c[('g', k)] = SL.row_grad_geo(box, r)[1]
    for rk, mm in MENUS.items():
        for k, r in enumerate(mm['rows']):
            c[('n', rk, k)] = t3lib.row_grad(box, r)[1]
    _GC[key] = c
    return c


def verify_farkas_keys(cache, keys, y_iv):
    worst = None
    for k in keys:
        acc = SL.iv_dot(cache[k], y_iv)
        lo = float(acc.a)
        if worst is None or lo < worst:
            worst = lo
        if not (acc.a > 0):
            return False, worst
    return True, worst


def farkas_robust(cache, keys, ybound=1.0, den=10 ** 9):
    """ROBUST Farkas direction for a whole box: maximise t subject to
        inf_{box} grad g . y >= t   for every key,      e_s . y = y[33] <= -t,
    using the INTERVAL gradients of the box (t3lib.farkas_lp's formulation:
    y = u - v with u,v >= 0, inf_box grad.y = sum_j (lo_j u_j - hi_j v_j)).
    This is the certificate that a single y must satisfy to kill the stratum on
    the whole box -- as opposed to a y optimised only at z-hat, which carries no
    robustness margin at all.  Returned y is rationalised at denominator `den`
    and then re-verified [IV]."""
    n = 2 * NV + 1
    A = np.zeros((len(keys) + 1, n))
    for i, k in enumerate(keys):
        g = cache[k]
        lo = np.zeros(NV)
        hi = np.zeros(NV)
        for gi, val in g.items():
            lo[gi] = float(mp.mpf(val.a))
            hi[gi] = float(mp.mpf(val.b))
        A[i, :NV] = -lo
        A[i, NV:2 * NV] = hi
        A[i, -1] = 1.0
    A[-1, SIDX] = 1.0
    A[-1, NV + SIDX] = -1.0
    A[-1, -1] = 1.0
    c = np.zeros(n)
    c[-1] = -1.0
    r = linprog(c, A_ub=A, b_ub=np.zeros(len(keys) + 1),
                bounds=[(0, ybound)] * (2 * NV) + [(0, 1.0)], method='highs')
    if not r.success:
        return None, 0.0
    t = float(-r.fun)
    if t <= 1e-12:
        return None, t
    yf = r.x[:NV] - r.x[NV:2 * NV]
    y = [Fraction(round(Fraction(float(v)) * den), den) for v in yf]
    if y[SIDX] >= 0:
        return None, t
    return y, t


# ======================================================================
# force-balance cascade  (point and interval forms)
# ======================================================================
FB_TOL = 1e-9
COLS = list(range(33))            # cx,cy,theta of the 11 squares -- NOT s


def cascade_point(retained_geo, mkey=None):
    """M1's sign rule at z-hat, optionally with the gained menu in the row set."""
    Rg = set(retained_geo)
    Rn = set(range(len(MENUS[mkey]['rows']))) if mkey else set()
    Gm = MENUS[mkey]['G'] if mkey else None
    fired = []
    changed = True
    while changed:
        changed = False
        for col in COLS:
            pos = [('g', k) for k in Rg if Amid[k, col] > FB_TOL]
            neg = [('g', k) for k in Rg if Amid[k, col] < -FB_TOL]
            if mkey:
                pos += [('n', k) for k in Rn if Gm[k, col] > FB_TOL]
                neg += [('n', k) for k in Rn if Gm[k, col] < -FB_TOL]
            if pos and not neg:
                kill = pos
            elif neg and not pos:
                kill = neg
            else:
                continue
            for tag, k in kill:
                (Rg if tag == 'g' else Rn).discard(k)
            fired.append({'col': col, 'killed': [[t, int(k)] for t, k in kill]})
            changed = True
    return Rg, Rn, fired


_STRUCT_G = [set(r['vars']) for r in ROWS]
_STRUCT_N = {rk: [set(r['vars']) for r in mm['rows']]
             for rk, mm in MENUS.items()}
_ZERO = mp.mpf(0)


def cascade_iv(retained_geo, cache, mkey=None):
    """INTERVAL form, sound on the whole box.

    On box(z-hat,r) column c fires iff no retained row can have a coefficient of
    the opposite sign there.  Rows whose coefficient interval merely CONTAINS 0
    are not killed (their multiplier is not forced to vanish) and do not block.
    Structurally absent entries are exactly 0.  Iterated to a fixed point.  [IV]
    """
    Rg = set(retained_geo)
    Rn = set(range(len(MENUS[mkey]['rows']))) if mkey else set()
    fired = []
    changed = True
    while changed:
        changed = False
        for col in COLS:
            ent = []
            for k in Rg:
                if col in _STRUCT_G[k]:
                    x = cache[('g', k)][col]
                    ent.append((('g', k), mp.mpf(x.a), mp.mpf(x.b)))
            if mkey:
                for k in Rn:
                    if col in _STRUCT_N[mkey][k]:
                        x = cache[('n', mkey, k)][col]
                        ent.append((('n', k), mp.mpf(x.a), mp.mpf(x.b)))
            if not ent:
                continue
            if all(lo >= _ZERO for _, lo, hi in ent):
                kill = [t for t, lo, hi in ent if lo > _ZERO]
            elif all(hi <= _ZERO for _, lo, hi in ent):
                kill = [t for t, lo, hi in ent if hi < _ZERO]
            else:
                continue
            if not kill:
                continue
            for tag, k in kill:
                (Rg if tag == 'g' else Rn).discard(k)
            fired.append({'col': col, 'killed': [[t, int(k)] for t, k in kill]})
            changed = True
    return Rg, Rn, fired


# ======================================================================
# TASK 1
# ======================================================================
APRIORI_CAP = 150000


def apriori_alive(free, G, cap=APRIORI_CAP, tcap=420.0):
    """EXHAUSTIVE level-wise enumeration of the cone-alive family.

    cone-alive is DOWNWARD CLOSED in B (dropping a broken row only adds a
    generator to the cone), so a candidate of size k need only be tested when
    all k of its (k-1)-subsets are alive.  Complete over all 2^38 break sets
    when it runs to exhaustion.
    """
    t0 = time.time()
    levels = {0: [()]}
    prev, prevset = [()], {()}
    k, total, nlp = 0, 0, 0
    truncated = False
    while prev:
        k += 1
        cand = set()
        for B in prev:
            hi = B[-1] if B else -1
            for r in free:
                if r > hi:
                    cand.add(B + (r,))
        nxt = []
        for B in sorted(cand):
            if k > 1 and any((B[:d] + B[d + 1:]) not in prevset
                             for d in range(k)):
                continue
            M = [j for j in range(NGEO) if j not in set(B)]
            nlp += 1
            if cone_alive(M, G)[0]:
                nxt.append(B)
        levels[k] = nxt
        prevset = set(nxt)
        prev = nxt
        total += len(nxt)
        if total > cap or (time.time() - t0) > tcap:
            truncated = True
            break
    return levels, total, nlp, truncated


def sampled_alive_estimate(free, G, nper=1500, rng=None):
    """Stratified estimate of |cone-alive family| when apriori is truncated."""
    rng = rng or random.Random(SEED + 11)
    n = len(free)
    est, det = 0.0, {}
    zeros = 0
    for k in range(1, n + 1):
        tot = math.comb(n, k)
        ns = min(nper, tot)
        seen = set()
        alive = 0
        for _ in range(ns):
            B = tuple(sorted(rng.sample(free, k)))
            seen.add(B)
            M = [j for j in range(NGEO) if j not in set(B)]
            if cone_alive(M, G)[0]:
                alive += 1
        p = alive / ns
        det[str(k)] = {'n_total': tot, 'n_sampled': ns, 'p_alive': p,
                       'est_alive': p * tot}
        est += p * tot
        zeros = zeros + 1 if alive == 0 else 0
        if zeros >= 3:
            break
    return est, det


def task1():
    log('TASK 1: gained-menu re-screen')
    out = {'travel_caps': [fkey(R) for R in RLIST], 'per_R': {}}

    # gradient drift, per menu and for the 38 geometric rows themselves
    def drift(rows, R):
        box = t3lib.box_from(ZHAT, R)
        o = []
        for r in rows:
            _, g0 = SL.row_grad_geo(ZBOX, r)
            _, gb = SL.row_grad_geo(box, r)
            d = 0.0
            for gi in r['vars']:
                a0 = (mp.mpf(g0[gi].a) + mp.mpf(g0[gi].b)) / 2
                d = max(d, float(max(abs(mp.mpf(gb[gi].b) - a0),
                                     abs(a0 - mp.mpf(gb[gi].a)))))
            o.append(d)
        return o

    rng = random.Random(SEED)
    for R in RLIST:
        rk = fkey(R)
        mm = MENUS[rk]
        G = mm['G']
        rec = {
            'R': rk,
            'menu': {
                'candidate_pairs': [list(p) for p in mm['pairs']],
                'n_sep_rows': len(mm['sel']),
                'per_pair_selections': mm['per_pair'],
                'n_straddling_dom_rows': len(mm['dom']),
                'rows': [{k: s[k] for k in
                          ('pair', 'name', 'o', 'e', 'p', 'k', 'sep_at_zhat',
                           'grad_1norm_on_box', 'mv_range_on_box')}
                         for s in mm['sel']],
                'method': (
                    'pair gate (M1 task-4 candidate table: the pair SAT gap must '
                    'be able to reach 0 on box(z-hat,R)) INTERSECTED with a '
                    'per-selection gate: every one of the 4 rows of the '
                    '(owner,edge,corner) selection must be able to be >= 0 on the '
                    'box and its SEP row must be able to reach 0, both via the '
                    '[IV] mean-value enclosure  row(z-hat) +/- ||grad||_{1,box}*R. '
                    'sep = 0 with dom >= 0 forces the pair to touch, so the pair '
                    'gate is legitimate.'),
            },
        }
        dg = drift(mm['rows'], R) if mm['rows'] else [0.0]
        dgeo = drift(ROWS, R)
        rec['gradient_drift'] = {
            'note': ('[IV] max_entry |grad over box(z-hat,R) - grad(z-hat)|. '
                     'This is the honest error made by evaluating a gained-row '
                     'gradient at z-hat when its contact forms elsewhere.'),
            'gained_max': max(dg), 'gained_median': float(np.median(dg)),
            'geometric_rows_max': max(dgeo),
            'geometric_rows_median': float(np.median(dgeo)),
            'M1_farkas_margin_for_scale': 0.22970,
            'M1_min_firing_coeff_for_scale': 0.0594,
        }

        # singleton screen
        free, killers, revived = [], [], []
        for k in range(NGEO):
            M = [j for j in range(NGEO) if j != k]
            a1 = cone_alive(M, G)[0]
            (free if a1 else killers).append(k)
            if a1 and k in M1_SINGLETON_KILLERS:
                revived.append(k)
        rec['singleton_screen'] = {
            'n_killers': len(killers), 'killers': killers,
            'n_free_rows': len(free), 'free_rows': free,
            'free_row_names': [RNAMES[k] for k in free],
            'n_revived_vs_M1': len(revived), 'revived_rows': revived,
            'M1_n_killers': len(M1_SINGLETON_KILLERS),
        }

        # exhaustive apriori (or truncated + sampled estimate)
        levels, total, nlp, trunc = apriori_alive(free, G)
        rec['cone_alive_family'] = {
            'n_by_k': {str(kk): len(v) for kk, v in levels.items()},
            'n_total_nonempty': total,
            'K_max_alive_k': max((kk for kk, v in levels.items() if v and kk),
                                 default=0),
            'exhaustive': not trunc,
            'n_LPs': nlp,
            'method': ('downward-closed apriori enumeration; complete over all '
                       '2^38 break sets when not truncated'),
        }
        if trunc:
            est, det = sampled_alive_estimate(free, G, rng=rng)
            rec['cone_alive_family']['truncated_at'] = total
            rec['cone_alive_family']['stratified_estimate_total'] = est
            rec['cone_alive_family']['stratified_detail'] = det
        else:
            rec['cone_alive_family']['sets'] = [list(B) for v in levels.values()
                                                for B in v if B]
        log('  R=%s: %d free rows, cone-alive %s%d (K=%d)'
            % (rk, len(free), '' if not trunc else '>= ', total,
               rec['cone_alive_family']['K_max_alive_k']))

        # revival attribution: which gained rows do the reviving
        if len(mm['sel']):
            sets = ([tuple(B) for v in levels.values() for B in v if B]
                    if not trunc else
                    [tuple(B) for v in levels.values() for B in v if B][:4000])
            newly = [B for B in sets if B not in M1_ALIVE]
            used = [0] * len(mm['sel'])
            ess = [0] * len(mm['sel'])
            for B in newly[:600]:
                M = [j for j in range(NGEO) if j not in set(B)]
                a, sol = cone_alive(M, G)
                if not a:
                    continue
                for t in range(len(mm['sel'])):
                    if sol[len(M) + t] > 1e-9:
                        used[t] += 1
                for t in range(len(mm['sel'])):
                    sub = np.delete(G, t, axis=0)
                    if not cone_alive(M, sub)[0]:
                        ess[t] += 1
            rec['revival'] = {
                'n_newly_alive_vs_M1': len(newly),
                'n_attributed': min(len(newly), 600),
                'gained_row_usage': [
                    {'name': mm['sel'][t]['name'], 'pair': mm['sel'][t]['pair'],
                     'n_using': used[t], 'n_where_ESSENTIAL': ess[t]}
                    for t in range(len(mm['sel']))],
                'note': ('"essential" = deleting that one gained row from the '
                         'menu makes the set cone-dead again.'),
            }
            for t in sorted(range(len(mm['sel'])), key=lambda t: -used[t])[:6]:
                log('     %-20s pair %s used %d essential %d'
                    % (mm['sel'][t]['name'], mm['sel'][t]['pair'],
                       used[t], ess[t]))
        else:
            rec['revival'] = {'n_newly_alive_vs_M1': 0,
                              'note': 'empty menu -- M1 stands verbatim'}

        # conservative sensitivity: also let the straddling dominance rows load
        if len(mm['dom']):
            fr2 = [k for k in range(NGEO)
                   if cone_alive([j for j in range(NGEO) if j != k], G,
                                 extra=mm['GD'])[0]]
            rec['sensitivity_with_dominance_rows'] = {
                'n_free_rows': len(fr2),
                'note': ('conservative: also lets the %d straddling dominance '
                         'rows carry multipliers.  Dominance rows touch only '
                         'theta columns, never z[33].' % len(mm['dom'])),
            }
        out['per_R'][rk] = rec

    # ---- the brief's explicit screens, as independent cross-checks ---------
    mm = MENU_MAIN
    G = mm['G']
    aliveset = set()
    fam = out['per_R'][fkey(R_MAIN)]['cone_alive_family']
    if fam.get('sets') is not None:
        aliveset = set(tuple(b) for b in fam['sets'])
    cross = {'menu_R': fkey(R_MAIN)}
    n = 0
    for rsz in range(1, len(TEN_FAMILY) + 1):
        for B in itertools.combinations(TEN_FAMILY, rsz):
            if cone_alive([j for j in range(NGEO) if j not in set(B)], G)[0]:
                n += 1
    cross['ten_row_family_alive'] = n
    cross['ten_row_family_total'] = 2 ** len(TEN_FAMILY) - 1
    for kk in (1, 2, 3):
        c = sum(1 for B in itertools.combinations(range(NGEO), kk)
                if cone_alive([j for j in range(NGEO) if j not in set(B)], G)[0])
        cross['k=%d_alive_exhaustive' % kk] = c
        cross['k=%d_total' % kk] = math.comb(NGEO, kk)
    rng2 = random.Random(SEED + 5)
    ra = 0
    miss = 0
    for _ in range(5000):
        kk = rng2.randint(4, 12)
        B = tuple(sorted(rng2.sample(range(NGEO), kk)))
        if cone_alive([j for j in range(NGEO) if j not in set(B)], G)[0]:
            ra += 1
            if aliveset and B not in aliveset:
                miss += 1
    cross['random_k4_12_n'] = 5000
    cross['random_k4_12_alive'] = ra
    cross['random_k4_12_missed_by_enumeration'] = miss if aliveset else None
    out['cross_checks'] = cross
    log('  cross-checks: %s' % cross)
    return out


# ======================================================================
# TASK 2
# ======================================================================
def _keys_for(M, mode, r):
    base = [('g', m) for m in M]
    if mode == 'none':
        return base
    if mode == 'fixed':
        return base + [('n', fkey(R_MAIN), t)
                       for t in range(len(MENU_MAIN['rows']))]
    mm = menu_for_radius(r)
    return base + [('n', fkey(mm['R']), t) for t in range(len(mm['rows']))]


def certified_radius(B, mode):
    """mode: 'none'   -> y must beat retained rows only (M1-style kill)
             'fixed'  -> retained + the whole R=0.05 menu at every radius
             'matched'-> retained + menu(r): the rows that can actually be
                         active on box(z-hat,r).  Self-consistent certificate.

    Two protocols are reported for each mode:
      zhat_y  : the brief's literal protocol -- y from the max-margin LP AT
                z-hat, rationalised, then verified over growing boxes;
      robust_y: y re-optimised on box(z-hat,r) itself via the interval-gradient
                LP (still ONE rational y per (stratum, radius), still one
                [IV]-verified certificate).  This is the number that answers
                "can one certificate cover the stratum over the working region".
    """
    M = [j for j in range(NGEO) if j not in set(B)]
    out = {'B': list(B), 'k': len(B)}

    # ---- protocol 1: y optimised at z-hat only -----------------------------
    G = None if mode == 'none' else MENU_MAIN['G']
    y, margin = farkas_direction(M, G)
    best = fail = wbest = None
    ok0 = False
    w0 = None
    if y is not None:
        y_iv = SL.to_iv_vec(y)
        ok0, w0 = verify_farkas_keys(grad_cache(None), _keys_for(M, mode, 0),
                                     y_iv)
        for r in RADII:
            ok, w = verify_farkas_keys(grad_cache(r), _keys_for(M, mode, r),
                                       y_iv)
            if ok:
                if best is None or r > best:
                    best, wbest = r, w
            elif fail is None or r < fail:
                fail = r
    out['zhat_y'] = {'lp_margin': margin if y is not None else 0.0,
                     'certified_at_zhat': bool(ok0), 'margin_at_zhat': w0,
                     'certified_radius': float(best) if best is not None else 0.0,
                     'margin_at_certified_radius': wbest,
                     'first_failing_radius': float(fail) if fail else None}

    # ---- protocol 2: y re-optimised robustly on each box -------------------
    best = fail = wbest = None
    per_r = {}
    for r in RADII:
        cache = grad_cache(r)
        keys = _keys_for(M, mode, r)
        yr, tr = farkas_robust(cache, keys)
        ok = False
        w = None
        if yr is not None:
            ok, w = verify_farkas_keys(cache, keys, SL.to_iv_vec(yr))
        per_r['%g' % float(r)] = {'lp_margin': tr,
                                  'iv_verified': bool(ok), 'iv_margin': w}
        if ok:
            if best is None or r > best:
                best, wbest = r, w
        elif fail is None or r < fail:
            fail = r
    out['robust_y'] = {
        'certified_radius': float(best) if best is not None else 0.0,
        'margin_at_certified_radius': wbest,
        'first_failing_radius': float(fail) if fail else None,
        'per_radius': per_r}
    out['certified_radius'] = out['robust_y']['certified_radius']
    return out


def task2():
    log('TASK 2: interval extension radius of the cone kills')
    rng = random.Random(SEED + 2)
    out = {'radii_tested': [float(r) for r in RADII],
           'method': (
               'y from the max-margin LP at z-hat (|y| <= 50, y[33] = -1, so '
               'e_s . y = -1 < 0), rationalised at denominator 1e9.  For each r '
               'the [IV] lower bound of grad g . y over box(z-hat, r) must be '
               '> 0 for EVERY row y has to beat.  Rigorous per (set, r): '
               'lambda >= 0 with A^T lambda = e_s would give '
               '0 > e_s.y = sum lambda_k (grad g_k . y) >= 0.'),
           'modes': {
               'none': 'retained rows only (M1-style kill, ignores gained contacts)',
               'fixed': 'retained + the whole R=0.05 gained menu at every radius',
               'matched': 'retained + menu(r): the rows that can actually be '
                          'active on box(z-hat,r).  This is the self-consistent '
                          'certificate and is the headline number.'}}

    def dead(B, G=None):
        return not cone_alive([j for j in range(NGEO) if j not in set(B)], G)[0]

    groups = {'a_singleton_killers': [(k,) for k in M1_SINGLETON_KILLERS]}
    b7 = []
    while len(b7) < 30:
        B = tuple(sorted(rng.sample(range(NGEO), 7)))
        if B not in b7 and dead(B):
            b7.append(B)
    groups['b_random_k7_dead'] = b7
    b8 = []
    while len(b8) < 30:
        B = tuple(sorted(rng.sample(range(NGEO), rng.randint(8, 15))))
        if B not in b8 and dead(B):
            b8.append(B)
    groups['c_random_k8_15_dead'] = b8

    def summ(rs, proto):
        rad = [x[proto]['certified_radius'] for x in rs]
        return {'n': len(rs), 'min': min(rad), 'median': float(np.median(rad)),
                'max': max(rad), 'n_zero': sum(1 for r in rad if r == 0.0),
                'n_reaching_0.005': sum(1 for r in rad if r >= 0.005),
                'n_reaching_0.05': sum(1 for r in rad if r >= 0.05),
                'histogram': {'%g' % float(r):
                              sum(1 for x in rad if x == float(r))
                              for r in RADII}}

    for gname, sets in groups.items():
        rec = {'sets': [list(B) for B in sets]}
        for mode in ('none', 'fixed', 'matched'):
            det = [certified_radius(B, mode) for B in sets]
            rec[mode] = {'summary_robust_y': summ(det, 'robust_y'),
                         'summary_zhat_y': summ(det, 'zhat_y'),
                         'detail': det}
        out[gname] = rec
        log('  %-22s robust-y med r: none %.4g | fixed %.4g | matched %.4g'
            % (gname, rec['none']['summary_robust_y']['median'],
               rec['fixed']['summary_robust_y']['median'],
               rec['matched']['summary_robust_y']['median']))
        log('  %-22s zhat-y   med r: none %.4g | matched %.4g'
            % ('', rec['none']['summary_zhat_y']['median'],
               rec['matched']['summary_zhat_y']['median']))

    ov = {}
    for mode in ('none', 'fixed', 'matched'):
        for proto in ('robust_y', 'zhat_y'):
            rad = [x[proto]['certified_radius'] for g in groups
                   for x in out[g][mode]['detail']]
            ov['%s/%s' % (mode, proto)] = {
                'n': len(rad), 'min': min(rad),
                'median': float(np.median(rad)), 'max': max(rad),
                'n_zero': sum(1 for r in rad if r == 0.0),
                'n_reaching_0.005': sum(1 for r in rad if r >= 0.005),
                'n_reaching_0.05': sum(1 for r in rad if r >= 0.05)}
    out['overall'] = ov
    return out


# ======================================================================
# TASK 3
# ======================================================================
def task3():
    log('TASK 3: force-balance cascade interval extension')
    rng = random.Random(SEED + 3)
    out = {'radii_tested': [float(r) for r in RADII],
           'rule': (
               'For every square i and coordinate c in {cx_i, cy_i, theta_i}, FJ '
               'stationarity gives sum_k lambda_k A[k,c] = 0 with lambda >= 0 '
               '(grad s touches only z[33], so this holds in BOTH the lambda_0 > 0 '
               'and lambda_0 = 0 branches).  INTERVAL FORM on box(z-hat,r): if '
               'every retained row has A_box[k,c] >= 0 (or every one <= 0), then '
               'every row with a strictly signed interval has lambda_k = 0 on the '
               'WHOLE box.  Rows whose interval contains 0 are neither killed nor '
               'blocking.  Structurally absent entries are exactly 0.  Iterated to '
               'a fixed point.  [IV], sound on the box.')}

    samples = []
    per = {}
    for kk in range(2, 13):
        want = 5 if kk <= 10 else 4
        got, tries = 0, 0
        while got < want and tries < 6000:
            tries += 1
            B = tuple(sorted(rng.sample(range(NGEO), kk)))
            M = [j for j in range(NGEO) if j not in set(B)]
            if cascade_point(M)[0]:
                continue
            samples.append((kk, B))
            got += 1
        per[str(kk)] = got
    out['n_samples'] = len(samples)
    out['samples_per_k'] = per

    det = []
    for kk, B in samples:
        M = [j for j in range(NGEO) if j not in set(B)]
        Rg0, _, fired0 = cascade_point(M)
        minc = min(min(abs(Amid[k, f['col']]) for t, k in f['killed'])
                   for f in fired0)
        best, fail = None, None
        for r in RADII:
            if not cascade_iv(M, grad_cache(r))[0]:
                if best is None or r > best:
                    best = r
            elif fail is None or r < fail:
                fail = r
        # gained menu in the row set: point form at each cap, interval matched
        gained_ok = {}
        for R in RLIST:
            rk = fkey(R)
            if not MENUS[rk]['rows']:
                gained_ok[rk] = True
                continue
            Rg, Rn, _ = cascade_point(M, rk)
            gained_ok[rk] = (not Rg) and (not Rn)
        bestG = None
        for r in RADII:
            mm = menu_for_radius(r)
            rk = fkey(mm['R'])
            g, n, _ = cascade_iv(M, grad_cache(r), rk if mm['rows'] else None)
            if not g and not n:
                if bestG is None or r > bestG:
                    bestG = r
        det.append({'k': kk, 'B': list(B), 'n_firings_at_zhat': len(fired0),
                    'min_abs_firing_coeff_at_zhat': minc,
                    'max_valid_radius': float(best) if best else 0.0,
                    'first_failing_radius': float(fail) if fail else None,
                    'collapse_survives_gained_menu_at_zhat': gained_ok,
                    'max_valid_radius_with_matched_menu':
                        float(bestG) if bestG else 0.0})
    rad = [d['max_valid_radius'] for d in det]
    radG = [d['max_valid_radius_with_matched_menu'] for d in det]
    out['detail'] = det
    out['summary'] = {
        'without_gained': {
            'min': min(rad), 'median': float(np.median(rad)), 'max': max(rad),
            'n_zero': sum(1 for r in rad if r == 0),
            'histogram': {'%g' % float(r): sum(1 for x in rad if x == float(r))
                          for r in RADII}},
        'with_matched_gained_menu': {
            'min': min(radG), 'median': float(np.median(radG)), 'max': max(radG),
            'n_zero': sum(1 for r in radG if r == 0)},
        'n_collapse_surviving_gained_menu_at_zhat': {
            fkey(R): sum(1 for d in det
                         if d['collapse_survives_gained_menu_at_zhat'][fkey(R)])
            for R in RLIST},
        'n_samples': len(det),
        'min_abs_firing_coeff_over_samples':
            min(d['min_abs_firing_coeff_at_zhat'] for d in det),
    }
    log('  cascade radius (no gained): min %.4g med %.4g max %.4g'
        % (min(rad), float(np.median(rad)), max(rad)))
    log('  collapse survives gained menu at z-hat: %s of %d'
        % (out['summary']['n_collapse_surviving_gained_menu_at_zhat'], len(det)))
    return out


# ======================================================================
# TASK 4
# ======================================================================
def task4(t1):
    log('TASK 4: completeness of the cone+gained+empty+collapse+D2 layers')
    out = {'per_R': {}}
    rng = random.Random(SEED + 4)
    SUBCAP = 20000
    for R in RLIST:
        rk = fkey(R)
        fam = t1['per_R'][rk]['cone_alive_family']
        mm = MENUS[rk]
        exhaustive = bool(fam.get('exhaustive'))
        if not exhaustive:
            # classify the enumerated prefix instead, plus a random sample of
            # cone-alive sets drawn from the free family
            sets = []
            free = t1['per_R'][rk]['singleton_screen']['free_rows']
            tries = 0
            while len(sets) < 3000 and tries < 60000:
                tries += 1
                kk = rng.randint(1, min(12, len(free)))
                B = tuple(sorted(rng.sample(free, kk)))
                if B in sets:
                    continue
                if cone_alive([j for j in range(NGEO) if j not in set(B)],
                              mm['G'])[0]:
                    sets.append(B)
            sets = sorted(set(sets))
        else:
            sets = [tuple(b) for b in fam.get('sets', [])]
            if len(sets) > SUBCAP:
                sets = sorted(rng.sample(sets, SUBCAP))
        rows = []
        for B in sets:
            Bs = set(B)
            M = [j for j in range(NGEO) if j not in Bs]
            st = SL.stratum(B, Amid)
            empty = st['dof'] == 0
            cert = SL.certified_rank34(M, Amid, Arad)[0] if empty else False
            c0 = not cascade_point(M)[0]
            if mm['rows']:
                g, n, _ = cascade_point(M, rk)
                cg = (not g) and (not n)
            else:
                cg = c0
            rows.append({'B': list(B), 'k': len(B), 'dof': st['dof'],
                         'empty': bool(empty), 'empty_RFP': bool(cert),
                         'cone_alive_no_gained': tuple(B) in M1_ALIVE,
                         'collapse_no_gained': bool(c0),
                         'collapse_with_gained': bool(cg),
                         'all_18_pair_rows_broken_D2': bool(set(PAIR_ROWS) <= Bs),
                         'in_M1_survivor_list': tuple(B) in M1_SURV})
        surv = [r for r in rows if not r['empty'] and not r['collapse_with_gained']
                and not r['all_18_pair_rows_broken_D2']]
        newly = [r for r in surv if not r['cone_alive_no_gained']]
        esc = [r for r in newly if not r['collapse_no_gained']]
        by_k = {}
        for r in surv:
            by_k[str(r['k'])] = by_k.get(str(r['k']), 0) + 1
        out['per_R'][rk] = {
            'exhaustive': exhaustive,
            'classified_is_sample': (not exhaustive),
            'n_cone_alive_family': (fam['n_total_nonempty'] if exhaustive
                                    else '>= %d (est %s)'
                                    % (fam['n_total_nonempty'],
                                       fam.get('stratified_estimate_total'))),
            'n_classified': len(sets),
            'n_cone_alive_with_gained': len(sets),
            'n_empty': sum(1 for r in rows if r['empty']),
            'n_empty_RFP_certified': sum(1 for r in rows if r['empty_RFP']),
            'n_collapse_with_gained': sum(1 for r in rows
                                          if r['collapse_with_gained']),
            'n_all_pairs_broken_D2': sum(1 for r in rows
                                         if r['all_18_pair_rows_broken_D2']),
            'n_survivors_corrected': len(surv),
            'survivors_by_k': by_k,
            'max_survivor_k': max([r['k'] for r in surv], default=0),
            'n_M1_survivors_still_here': sum(1 for r in surv
                                             if r['in_M1_survivor_list']),
            'escaping_class': {
                'definition': ('cone-dead WITHOUT the gained menu, cone-ALIVE '
                               'with it, not empty, not killed by the '
                               'force-balance cascade (gained rows in the row '
                               'set), and not covered by the D2/slack layer.  '
                               'Exactly the strata M1 truncated away wrongly.'),
                'size': len(esc),
                'by_k': {str(k): sum(1 for r in esc if r['k'] == k)
                         for k in sorted(set(r['k'] for r in esc))},
                'sets': [r['B'] for r in esc][:500],
                'truncated_listing': len(esc) > 500,
            },
            'survivors': [r['B'] for r in surv][:2000],
            'per_set': rows if len(rows) <= 5000 else rows[:5000],
        }
        log('  R=%s: cone-alive %d -> survivors %d (M1: 81); escaping class %d'
            % (rk, len(sets), len(surv), len(esc)))
    out['M1_baseline'] = {'n_cone_alive': len(M1_ALIVE),
                          'n_survivors': len(M1_SURV)}
    return out


# ======================================================================
def main():
    R = {'meta': {'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
                  'source': 'A35/M3', 'seed': SEED, 'iv_dps': 60,
                  'travel_caps': [fkey(x) for x in RLIST],
                  'radii': [float(x) for x in RADII],
                  'inputs': ['A22 krawczyk_cert.json', 'A35 m1_strata.json',
                             'A30 t3lib.py'],
                  'row_names': RNAMES}}

    def save():
        with open(OUT_JSON, 'w') as f:
            json.dump(R, f, indent=1, default=str)

    t1 = task1()
    R['task1_gained_menu_rescreen'] = t1
    save()
    R['task2_farkas_radius'] = task2()
    save()
    R['task3_cascade_radius'] = task3()
    save()
    R['task4_completeness'] = task4(t1)
    R['meta']['runtime_secs'] = time.time() - T0
    save()
    log('done -> %s' % OUT_JSON)


if __name__ == '__main__':
    main()
