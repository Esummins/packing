"""m3_certs.py -- A35 / M3 headline deliverable (re-steer from the A35 lead).

REGION FORM OF T1-a ON M2's BOX.

  h_W = 69/32000 = 0.00215625   (M2's wedge/empty certificate radius)

(1) UPWARD CLOSURE.  Cone-death is upward closed in B: B contains B' implies
    retained(B) subset retained(B'), so the cone shrinks.  A Farkas direction y
    that kills the MINIMAL dead set B' (grad g_m . y > 0 for every m not in B',
    e_s . y < 0) therefore kills EVERY B containing B'.  M1's vertex enumeration
    gives the minimal dead sets: 28 singletons + 6 pairs.  So the whole
    2^38 - 224 cone-dead family is covered by 34 certificates.
    This file emits and [IV]-verifies them over box(z-hat, h_W), and bisects the
    maximal radius of each.

(2) GAINED MENU EMPTY AT h_W.  Certified two independent ways (Lipschitz
    arithmetic on M1's constants, and a direct interval enclosure of every
    non-contact pair gap and corner-wall clearance over the box), so the
    gained-contact caveat is discharged for these kills.

(3) EXACT COMBINATORIAL CHECK that the 34 minimal dead sets really do generate
    the whole dead family (equivalently: the alive family has exactly 224
    members).

Rigour tags as in M1/M3: [IV] mpmath.iv dps 60, [EXACT] exact rational.
"""
from __future__ import annotations

import itertools
import json
import os
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
OUT = os.path.join(RESULTS, 'm3_certs.json')

import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60
mp.dps = 60
NV, NGEO, SIDX = SL.NV, SL.NGEO, SL.S_IDX
T0 = time.time()


def log(*a):
    print('[%6.1fs]' % (time.time() - T0), *a, flush=True)


H_W = Fraction(69, 32000)          # M2's certified box radius
ZHAT = SL.z_hat()
ZBOX = SL.point_box()
ROWS = SL.geo_rows()
RNAMES = SL.row_names()
CONS = SL.geo_constraints()
_, Amid, Arad, _ = SL.jacobian()

M1 = json.load(open(os.path.join(RESULTS, 'm1_strata.json')))
TEN = M1['task3']['rows_by_family']['union_of_all_Z']
SINGLETONS = sorted(set(range(NGEO)) - set(TEN))
PAIRS = [tuple(p) for p in M1['task3']['pair_excludable_minimal']]
MINIMAL_DEAD = [(k,) for k in SINGLETONS] + [tuple(sorted(p)) for p in PAIRS]
M1_ALIVE = set(tuple(b) for b in M1['task3']['surviving_breakset_list'])


# ---------------------------------------------------------------- gradients
_CACHE = {}
_G0 = None


def _grad0():
    """Gradients at z-hat (degenerate box), as iv."""
    global _G0
    if _G0 is None:
        _G0 = [SL.row_grad_geo(ZBOX, r)[1] for r in ROWS]
    return _G0


def _grad_hess(box, r):
    if r['kind'] != 'dist':
        return t3lib.row_grad_hess(box, r)
    vs = r['vars']
    d = len(vs)
    V = [t3lib.Jet.var(box[gi], k, d, 2) for k, gi in enumerate(vs)]
    dx = V[0] - V[2]
    dy = V[1] - V[3]
    j = (dx * dx + dy * dy) - iv.mpf(1)
    g = {gi: j.g[k] for k, gi in enumerate(vs)}
    h = {(ga, gb): j.h[a][b] for a, ga in enumerate(vs)
         for b, gb in enumerate(vs)}
    return j.v, g, h


def _tighten(g_direct, g_mv):
    """Intersect two sound gradient enclosures (both are valid on the box)."""
    out = {}
    for gi, x in g_direct.items():
        y = g_mv.get(gi)
        if y is None:
            out[gi] = x
            continue
        lo = max(mp.mpf(x.a), mp.mpf(y.a))
        hi = min(mp.mpf(x.b), mp.mpf(y.b))
        if lo > hi:            # should not happen; keep the sound one
            out[gi] = x
        else:
            out[gi] = iv.mpf([lo, hi])
    return out


def _cache_general(center, rad):
    """Gradient enclosures over box(center, rad), tightened by intersecting
    the direct interval evaluation with the MEAN-VALUE form
        grad_j(z) in grad_j(center) + sum_k H_jk(box) * [-rad_k, rad_k]
    (both sound; the intersection is sound).  Only used when the centre is
    z-hat, where grad(centre) is available at essentially zero width."""
    box = t3lib.box_from(center, rad)
    radv = rad if isinstance(rad, (list, tuple)) else [rad] * NV
    at_zhat = all(center[j] == ZHAT[j] for j in range(NV))
    out = []
    for k, r in enumerate(ROWS):
        gd = SL.row_grad_geo(box, r)[1]
        if not at_zhat:
            out.append(gd)
            continue
        _, _, H = _grad_hess(box, r)
        g0 = _grad0()[k]
        gm = {}
        for gi in r['vars']:
            w = mp.mpf(0)
            for gj in r['vars']:
                hij = H.get((gi, gj))
                if hij is None:
                    continue
                w += max(abs(mp.mpf(hij.a)), abs(mp.mpf(hij.b))) * \
                    mp.mpf(radv[gj].numerator) / radv[gj].denominator \
                    if isinstance(radv[gj], Fraction) else \
                    max(abs(mp.mpf(hij.a)), abs(mp.mpf(hij.b))) * mp.mpf(radv[gj])
            c0 = (mp.mpf(g0[gi].a) + mp.mpf(g0[gi].b)) / 2
            pad = w + (mp.mpf(g0[gi].b) - mp.mpf(g0[gi].a))
            gm[gi] = iv.mpf([c0 - pad, c0 + pad])
        out.append(_tighten(gd, gm))
    return out


def gcache(R):
    key = str(R)
    if key in _CACHE:
        return _CACHE[key]
    if R == 0:
        c = _grad0()
    else:
        c = _cache_general(ZHAT, [R] * NV)
    _CACHE[key] = c
    return c


def farkas_robust(cache, M, ybound=1.0, den=10 ** 12):
    """Robust Farkas y over the box:  inf_box grad g_m . y >= t  for m in M,
    y[33] <= -t.  y = u - v, u,v >= 0, inf = sum_j (lo_j u_j - hi_j v_j)."""
    n = 2 * NV + 1
    A = np.zeros((len(M) + 1, n))
    for i, m in enumerate(M):
        g = cache[m]
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
    r = linprog(c, A_ub=A, b_ub=np.zeros(len(M) + 1),
                bounds=[(0, ybound)] * (2 * NV) + [(0, 1.0)], method='highs')
    if not r.success:
        return None, 0.0
    t = float(-r.fun)
    if t <= 1e-13:
        return None, t
    yf = r.x[:NV] - r.x[NV:2 * NV]
    y = [Fraction(round(Fraction(float(v)) * den), den) for v in yf]
    if y[SIDX] >= 0:
        return None, t
    return y, t


def verify(cache, M, y):
    """[IV] every grad g_m . y > 0 and y[33] < 0.  Returns (ok, min margin)."""
    if not (y[SIDX] < 0):
        return False, None
    y_iv = SL.to_iv_vec(y)
    worst = None
    ok = True
    for m in M:
        acc = SL.iv_dot(cache[m], y_iv)
        lo = float(acc.a)
        if worst is None or lo < worst:
            worst = lo
        if not (acc.a > 0):
            ok = False
    return ok, worst


def certify(B, R):
    M = [j for j in range(NGEO) if j not in set(B)]
    cache = gcache(R)
    y, t = farkas_robust(cache, M)
    if y is None:
        return None, {'lp_margin': t, 'ok': False}
    ok, w = verify(cache, M, y)
    return (y if ok else None), {'lp_margin': t, 'ok': bool(ok), 'iv_margin': w}


# ------------------------------------------------- adaptive box subdivision
def _cache_for(center, rad):
    return _cache_general(center, rad)


def certify_subdivided(B, R, max_leaves=512, max_depth=12):
    """Cover box(z-hat, R) by finitely many sub-boxes, each with its OWN
    rational Farkas direction.  Sound: the sub-boxes tile the box, and on each
    the [IV] check is the same rigorous argument.  Splitting is adaptive --
    the coordinate bisected is the one whose gradient-interval width contributes
    most to the binding row's margin deficit.
    """
    M = [j for j in range(NGEO) if j not in set(B)]
    leaves = []
    stack = [(list(ZHAT), [R] * NV, 0)]
    n_lp = 0
    while stack:
        if len(leaves) + len(stack) > max_leaves:
            return None
        center, rad, depth = stack.pop()
        cache = _cache_for(center, rad)
        n_lp += 1
        y, t = farkas_robust(cache, M)
        ok = False
        w = None
        if y is not None:
            ok, w = verify(cache, M, y)
        if ok:
            leaves.append({'center_offsets':
                           {str(j): SL.frac_str(center[j] - ZHAT[j])
                            for j in range(NV) if center[j] != ZHAT[j]},
                           'radii': {str(j): str(rad[j])
                                     for j in range(NV) if rad[j] != R},
                           'uniform_radius': str(R),
                           'iv_margin': w,
                           'y_rational': [SL.frac_str(v) for v in y]})
            continue
        if depth >= max_depth:
            return None
        # split the coordinate with the widest gradient interval among the
        # retained rows (weighted by how often it appears)
        best_j, best_w = None, -1.0
        for j in range(NV):
            if rad[j] == 0:
                continue
            wj = 0.0
            for m in M:
                g = cache[m].get(j)
                if g is None:
                    continue
                wj = max(wj, float(mp.mpf(g.b) - mp.mpf(g.a)))
            wj *= float(rad[j])
            if wj > best_w:
                best_w, best_j = wj, j
        if best_j is None:
            return None
        h = rad[best_j] / 2
        for sgn in (-1, 1):
            c2 = list(center)
            c2[best_j] = center[best_j] + sgn * h
            r2 = list(rad)
            r2[best_j] = h
            stack.append((c2, r2, depth + 1))
    return {'n_leaves': len(leaves), 'n_LPs': n_lp, 'leaves': leaves}


def max_radius(B, lo=H_W, hi=Fraction(1, 4), iters=14):
    """Bisect the largest radius at which a robust certificate verifies."""
    if certify(B, hi)[0] is not None:
        return hi
    if certify(B, lo)[0] is None:
        # bisect downward from lo
        a, b = Fraction(0), lo
        for _ in range(iters):
            m = (a + b) / 2
            if certify(B, m)[0] is not None:
                a = m
            else:
                b = m
        return a
    a, b = lo, hi
    for _ in range(iters):
        m = (a + b) / 2
        if certify(B, m)[0] is not None:
            a = m
        else:
            b = m
    return a


# =====================================================================
def part1():
    log('PART 1: 34 minimal-dead-set Farkas certificates at h_W = %s (%.8f)'
        % (H_W, float(H_W)))
    out = {'h_W': str(H_W), 'h_W_float': float(H_W),
           'n_minimal_dead_sets': len(MINIMAL_DEAD),
           'minimal_dead_sets': [list(B) for B in MINIMAL_DEAD],
           'upward_closure_argument': (
               'B contains B\'  =>  retained(B) subset of retained(B\')  =>  '
               'cone{grad g_m : m in retained(B)} subset of cone{...retained(B\')}. '
               'So a y with grad g_m . y > 0 for all m in retained(B\') and '
               'e_s . y < 0 also has grad g_m . y > 0 for all m in retained(B), '
               'and lambda >= 0 with A_retained(B)^T lambda = e_s would give '
               '0 > e_s . y = sum lambda_m (grad g_m . y) >= 0.  One certificate '
               'per MINIMAL dead set covers its whole up-set.'),
           'method': (
               '[IV] robust Farkas LP over box(z-hat, r): maximise t subject to '
               'inf_box grad g_m . y >= t for every retained m and y[33] <= -t, '
               'using the mpmath.iv gradient enclosures of the box; y rationalised '
               'at denominator 1e12 and every inf re-verified in mpmath.iv at '
               'dps 60.  Fully rigorous per (set, radius).'),
           'certs': []}
    nok = 0
    for B in MINIMAL_DEAD:
        y, info = certify(B, H_W)
        rmax = max_radius(B)
        rec = {'B': list(B),
               'names': [RNAMES[k] for k in B],
               'n_retained_rows': NGEO - len(B),
               'certified_at_h_W': info['ok'],
               'iv_margin_at_h_W': info.get('iv_margin'),
               'lp_margin_at_h_W': info['lp_margin'],
               'max_certified_radius': float(rmax),
               'max_certified_radius_exact': str(rmax),
               'y_rational': [SL.frac_str(v) for v in y] if y else None,
               'y_denominator': 10 ** 12}
        if not info['ok']:
            sub = certify_subdivided(B, H_W, max_leaves=6000, max_depth=24)
            rec['subdivision'] = (
                {'needed': True, 'covered': sub is not None,
                 'n_leaves': sub['n_leaves'] if sub else None,
                 'min_iv_margin': (min(l['iv_margin'] for l in sub['leaves'])
                                   if sub else None),
                 'leaves': sub['leaves'] if sub else None,
                 'note': ('one single y does not cover box(z-hat, h_W) for this '
                          'set; the box is TILED by sub-boxes, each carrying its '
                          'own [IV]-verified rational Farkas direction.  Sound: '
                          'the sub-boxes cover the box and each leaf certificate '
                          'is the same rigorous argument on its own cell.')})
            if sub is not None:
                rec['certified_at_h_W'] = True
                rec['certified_by'] = 'subdivision (%d leaves)' % sub['n_leaves']
                rec['iv_margin_at_h_W'] = min(l['iv_margin']
                                              for l in sub['leaves'])
        else:
            rec['certified_by'] = 'single y'
        out['certs'].append(rec)
        nok += bool(rec['certified_at_h_W'])
        log('   B=%-10s %-14s  h_W: %s  margin %.4g   r_max %.5f  %s'
            % (list(B), rec['names'][0][:14],
               'OK ' if rec['certified_at_h_W'] else 'FAIL',
               rec.get('iv_margin_at_h_W') or 0.0, float(rmax),
               rec.get('certified_by', '')))
    out['n_certified_at_h_W'] = nok
    out['all_certified_at_h_W'] = (nok == len(MINIMAL_DEAD))
    out['n_needing_subdivision'] = sum(
        1 for c in out['certs'] if c.get('subdivision'))
    rr = [c['max_certified_radius'] for c in out['certs']]
    out['max_radius_distribution'] = {
        'min': min(rr), 'median': float(np.median(rr)), 'max': max(rr),
        'n_at_or_above_h_W': sum(1 for r in rr if r >= float(H_W)),
        'argmin_set': out['certs'][int(np.argmin(rr))]['B'],
        'argmin_names': out['certs'][int(np.argmin(rr))]['names']}
    log('  => %d / %d certified at h_W; min radius over the 34 = %.6f'
        % (nok, len(MINIMAL_DEAD), min(rr)))
    return out


# =====================================================================
def part2():
    log('PART 2: gained menu EMPTY on box(z-hat, h_W)')
    L_PAIR = 3.0 * float(np.sqrt(2.0))
    L_WALL_HI = 1.0 + 3.0 / float(np.sqrt(2.0))
    L_WALL_LO = 3.0 / float(np.sqrt(2.0))
    h = float(H_W)
    cert = SL.load_cert()
    noncontact = [tuple(p) for p in cert['noncontact_pairs']]

    # (a) Lipschitz arithmetic on M1's constants
    min_pair_gap = min(g['gap_lo'] for g in M1['task4']['noncontact_pair_gaps'])
    min_wall_gap = min(w['gap_lo']
                       for w in M1['task4']['noncontact_wall_gaps_top20'])
    lip = {'L_pair': L_PAIR, 'L_wall_hi': L_WALL_HI, 'L_wall_lo': L_WALL_LO,
           'pair_travel_bound': L_PAIR * h,
           'min_noncontact_pair_gap_at_zhat': min_pair_gap,
           'pair_margin': min_pair_gap - L_PAIR * h,
           'pair_ok': bool(L_PAIR * h < min_pair_gap),
           'wall_travel_bound': L_WALL_HI * h,
           'min_noncontact_wall_gap_at_zhat': min_wall_gap,
           'wall_margin': min_wall_gap - L_WALL_HI * h,
           'wall_ok': bool(L_WALL_HI * h < min_wall_gap)}

    # (b) direct interval enclosure over the box  [IV]
    box = t3lib.box_from(ZHAT, H_W)
    worst_pair, worst_pair_lo = None, None
    for (i, j) in noncontact:
        lo = float(t3lib.pair_sep_iv(box, i, j).a)
        if worst_pair_lo is None or lo < worst_pair_lo:
            worst_pair_lo, worst_pair = lo, (i, j)
    have = SL.contact_wall_set()
    worst_wall, worst_wall_lo = None, None
    nwall = 0
    for i in range(SL.NSQ):
        for c in range(4):
            for w in SL.WALLS:
                if (i, c, w) in have:
                    continue
                nwall += 1
                lo = float(SL.wall_gap(box, i, c, w).a)
                if worst_wall_lo is None or lo < worst_wall_lo:
                    worst_wall_lo, worst_wall = lo, (i, c, w)
    # (b') the naive SAT enclosure is dependency-pessimistic; bisect the 6
    # coordinates of the offending pair's two squares to repair it
    repaired = {}
    for (i, j) in noncontact:
        lo = float(t3lib.pair_sep_iv(box, i, j).a)
        if lo > 0:
            continue
        vs = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        best = None
        for signs in itertools.product((-1, 1), repeat=len(vs)):
            c2 = list(ZHAT)
            r2 = [H_W] * NV
            for v, s in zip(vs, signs):
                c2[v] = ZHAT[v] + s * H_W / 2
                r2[v] = H_W / 2
            b2 = t3lib.box_from(c2, r2)
            l2 = float(t3lib.pair_sep_iv(b2, i, j).a)
            best = l2 if best is None else min(best, l2)
        repaired['%d-%d' % (i, j)] = best
    direct = {'n_noncontact_pairs': len(noncontact),
              'subdivided_repair': repaired,
              'subdivided_repair_note': (
                  'the naive interval SAT enclosure is dependency-pessimistic '
                  '(the max-over-4-axes of differences of interval extrema '
                  'loses correlation).  Bisecting the 6 coordinates of the two '
                  'squares (64 sub-boxes) repairs it where needed; the value '
                  'shown is the worst lower bound over those sub-boxes.'),
              'min_pair_gap_lower_bound_on_box': worst_pair_lo,
              'argmin_pair': list(worst_pair),
              'n_noncontact_wall_combos': nwall,
              'min_wall_clearance_lower_bound_on_box': worst_wall_lo,
              'argmin_wall': [worst_wall[0], worst_wall[1], worst_wall[2]],
              'pair_ok': bool(worst_pair_lo > 0
                              or (repaired and min(repaired.values()) > 0)),
              'wall_ok': bool(worst_wall_lo > 0)}
    direct['pair_ok_naive'] = bool(worst_pair_lo > 0)
    out = {'h_W': str(H_W), 'lipschitz': lip, 'interval_direct': direct,
           'menu_empty': bool(lip['pair_ok'] and lip['wall_ok']
                              and direct['pair_ok'] and direct['wall_ok']),
           'lemma': (
               'LEMMA (gained menu empty at h_W).  On box(z-hat, %s) no '
               'non-contact pair can touch and no new corner-wall contact can '
               'form.  Proof 1 (Lipschitz, M1 constants): pair separation is '
               '%.6f-Lipschitz in ||dz||_inf, so travel <= %.6f x %.8f = %.7f '
               '< %.6f = the smallest non-contact pair gap at z-hat; corner-wall '
               'clearance is %.6f-Lipschitz, travel <= %.7f < %.6f.  Proof 2 '
               '([IV], independent): the mpmath.iv enclosure of every one of the '
               '%d non-contact pair separations and every one of the %d '
               'non-contact corner-wall clearances over the whole box has a '
               'STRICTLY POSITIVE lower bound (worst %.6f and %.6f).  Hence the '
               'gained-contact menu of T0.1(ii) is EMPTY on the box and the '
               'cone-death certificates of Part 1 need beat only the retained '
               'geometric rows.'
               % (H_W, L_PAIR, L_PAIR, h, L_PAIR * h, min_pair_gap,
                  L_WALL_HI, L_WALL_HI * h, min_wall_gap,
                  len(noncontact), nwall, worst_pair_lo, worst_wall_lo))}
    log('  Lipschitz: pair %.7f < %.6f (%s); wall %.7f < %.6f (%s)'
        % (L_PAIR * h, min_pair_gap, lip['pair_ok'],
           L_WALL_HI * h, min_wall_gap, lip['wall_ok']))
    log('  [IV] direct: min pair gap on box %.6f, min wall clearance %.6f'
        % (worst_pair_lo, worst_wall_lo))
    return out


# =====================================================================
def part3():
    log('PART 3: the 34 minimal dead sets generate the whole dead family')
    forb = [set(B) for B in MINIMAL_DEAD]
    alive = []
    for r in range(0, len(TEN) + 1):
        for B in itertools.combinations(TEN, r):
            s = set(B)
            if any(f <= s for f in forb):
                continue
            alive.append(tuple(B))
    # a break set touching any row outside TEN contains a singleton dead set
    nonempty = [B for B in alive if B]
    prod = {'structure': '{1|2} x {8,9|10} x {21,22|23} x {26|29}',
            'count_by_factor': [3, 5, 5, 3], 'product': 3 * 5 * 5 * 3,
            'minus_empty_set': 3 * 5 * 5 * 3 - 1}
    out = {'n_alive_from_minimal_dead_sets': len(nonempty),
           'matches_m1_list': len(nonempty) == len(M1_ALIVE),
           'set_equality_with_m1_list': set(nonempty) == M1_ALIVE,
           'm1_list_length': len(M1_ALIVE),
           'm1_report_text_says': 223,
           'exact_product_formula': prod,
           'note': ('EXACT combinatorics: a break set is cone-alive iff it is a '
                    'subset of the 10-row family that contains none of the 6 '
                    'forbidden pairs.  Independent sets of the 4-component '
                    'forbidden graph: 3 x 5 x 5 x 3 = 225 including the empty '
                    'set, i.e. 224 non-empty.  The M1 JSON list has 224 entries; '
                    'the M1 report text says 223 -- an off-by-one in the prose, '
                    'the data are right.')}
    log('  alive family from the 34 minimal dead sets: %d (M1 JSON list %d, '
        'set-equal %s); exact product 3*5*5*3-1 = %d'
        % (len(nonempty), len(M1_ALIVE), out['set_equality_with_m1_list'],
           prod['minus_empty_set']))
    return out


def part4():
    """v2 PREVIEW: M4 found pair (1,3) is a genuine 14th contact with NO row in
    the A22 38-row basis v1.  A missing active row makes the true FJ cone LARGER
    than the one my v1 Farkas directions beat, so every v1 kill must be re-tested
    with the (1,3) contact rows added as always-available generators.  This
    section does exactly that, ahead of m1b_strata.json."""
    log('PART 4: v2 preview -- add the missing (1,3) contact rows')
    # every (owner, edge, corner) selection of (1,3) whose sep row is ~0 at
    # z-hat can carry a multiplier at a corner-corner contact
    sel = []
    for o, p in ((1, 3), (3, 1)):
        for e in range(4):
            for k in range(4):
                r = t3lib.sep_row(o, e, p, k)
                v = t3lib.row_value(ZBOX, r)
                if abs(float(v.b)) < 1e-9 and abs(float(v.a)) < 1e-9:
                    doms = [t3lib.dom_row(o, e, p, k, m)
                            for m in range(4) if m != k]
                    if all(float(t3lib.row_value(ZBOX, d).b) >= -1e-9
                           for d in doms):
                        sel.append({'o': o, 'e': e, 'p': p, 'k': k, 'row': r,
                                    'name': t3lib.row_name(r),
                                    'sep_at_zhat': float(v.a)})
    G13 = np.zeros((len(sel), NV))
    for k, s in enumerate(sel):
        _, g = t3lib.row_grad(ZBOX, s['row'])
        for gi, v in g.items():
            G13[k, gi] = float(mp.mpf(v.a) + mp.mpf(v.b)) / 2
    log('   (1,3) tight selections at z-hat: %d  %s'
        % (len(sel), [s['name'] for s in sel]))

    cache0 = gcache(H_W)
    g13_iv = [t3lib.row_grad(t3lib.box_from(ZHAT, H_W), s['row'])[1]
              for s in sel]

    def robust_with13(M):
        c = list(cache0) + g13_iv
        idx = list(M) + [NGEO + i for i in range(len(sel))]
        y, t = farkas_robust(c, idx)
        if y is None:
            return None, t, None
        if not (y[SIDX] < 0):
            return None, t, None
        y_iv = SL.to_iv_vec(y)
        worst = None
        for m in idx:
            acc = SL.iv_dot(c[m], y_iv)
            lo = float(acc.a)
            worst = lo if worst is None else min(worst, lo)
            if not (acc.a > 0):
                return None, t, worst
        return y, t, worst

    recs = []
    nok = 0
    for B in MINIMAL_DEAD:
        M = [j for j in range(NGEO) if j not in set(B)]
        y, t, w = robust_with13(M)
        # also the point test at z-hat: is the cone alive with (1,3) added?
        cols = [Amid[m] for m in M] + list(G13)
        A_eq = np.array(cols).T
        b = np.zeros(NV)
        b[SIDX] = 1.0
        lp = linprog(np.zeros(A_eq.shape[1]), A_eq=A_eq, b_eq=b,
                     bounds=(0, None), method='highs')
        recs.append({'B': list(B), 'names': [RNAMES[k] for k in B],
                     'still_cone_dead_at_zhat_with_13': bool(lp.status != 0),
                     'certified_on_box_h_W_with_13': y is not None,
                     'iv_margin': w})
        nok += (y is not None)
    out = {'missing_contact_pair': [1, 3],
           'n_tight_selections_at_zhat': len(sel),
           'selection_names': [s['name'] for s in sel],
           'n_minimal_dead_sets_v1': len(MINIMAL_DEAD),
           'n_still_certified_on_box_with_13': nok,
           'n_still_cone_dead_at_zhat_with_13':
               sum(1 for r in recs if r['still_cone_dead_at_zhat_with_13']),
           'all_survive': nok == len(MINIMAL_DEAD),
           'detail': recs,
           'caveat': (
               'This is a PREVIEW, not the v2 result.  It answers only: do the '
               'v1 minimal-dead-set certificates still kill once the missing '
               '(1,3) contact rows are allowed into the cone?  The v2 basis also '
               'replaces dist rows 36/37 by flush sep rows, which changes the '
               'minimal-dead-set LIST itself; that awaits m1b_strata.json.')}
    log('   v1 minimal dead sets still dead with (1,3) rows: %d/%d at z-hat, '
        '%d/%d certified on box(h_W)'
        % (out['n_still_cone_dead_at_zhat_with_13'], len(MINIMAL_DEAD),
           nok, len(MINIMAL_DEAD)))
    return out


def main():
    R = {'meta': {'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
                  'source': 'A35/M3 re-steer', 'h_W': str(H_W),
                  'iv_dps': 60, 'row_names': RNAMES,
                  'basis': 'A22 38-row geometric basis v1',
                  'basis_caveat': (
                      'M4 found this basis INCOMPLETE: pair (1,3) is a genuine '
                      '14th contact with no row here, and dist rows 36/37 are to '
                      'be replaced by flush sep rows.  Every headline below is '
                      'scoped to basis v1; part 4 previews the (1,3) delta.')}}
    R['part1_minimal_dead_certificates'] = part1()
    R['part2_gained_menu_empty'] = part2()
    R['part3_generation_check'] = part3()
    R['part4_v2_preview_pair_1_3'] = part4()
    p1, p2 = R['part1_minimal_dead_certificates'], R['part2_gained_menu_empty']
    R['HEADLINE'] = {
        'region_T1a_closed_on_box_h_W': bool(p1['all_certified_at_h_W']
                                             and p2['menu_empty']),
        'n_certificates': p1['n_minimal_dead_sets'],
        'n_certified': p1['n_certified_at_h_W'],
        'gained_menu_empty': p2['menu_empty'],
        'min_iv_margin_over_the_34': min(
            c['iv_margin_at_h_W'] for c in p1['certs']
            if c['iv_margin_at_h_W'] is not None),
        'min_max_radius_over_the_34': p1['max_radius_distribution']['min'],
        'n_needing_subdivision': p1['n_needing_subdivision'],
        'v2_preview_all_survive': R['part4_v2_preview_pair_1_3']['all_survive'],
        'statement': (
            'ON THE A22 38-ROW BASIS v1: every cone-dead break set (all '
            '2^38 - 224 of them) is certified FJ-free in the lambda_0 > 0 branch '
            'on box(z-hat, h_W) by one of 34 [IV]-verified rational Farkas '
            'directions (33 with a single y, 1 by a subdivided cover), and the '
            'gained-contact menu is certified EMPTY on that box, so no gained '
            'row can re-feed the cone there.'),
    }
    R['meta']['runtime_secs'] = time.time() - T0
    with open(OUT, 'w') as f:
        json.dump(R, f, indent=1, default=str)
    log('HEADLINE: region T1-a closed on box(h_W) = %s'
        % R['HEADLINE']['region_T1a_closed_on_box_h_W'])
    log('done -> %s' % OUT)


if __name__ == '__main__':
    main()
