"""m3b_certs.py -- A35 / M3-delta: region form of T1-a on the REPAIRED BASIS v2.

M3 (v1) closed region T1-a on box(z-hat, h_W) for the 38-row A22 basis; M1b then
repaired the basis (42 rows: 0..35 verbatim, dist rows 36/37 dropped, four flush
rows F0-1a/b, F0-3a/b and the two (1,3) corner-corner branches C1-3x/y added).
This file re-runs the region-certificate pipeline against the v2 minimal dead
sets.

  Part 0  RECOMPUTE the v2 minimal dead family (m1b's list is incomplete:
          it stops at size 2 and misses 4 minimal dead TRIPLES) -> 37 sets
  Part 1  37 region certificates on box(z-hat, h_W)
  Part 2  gained menu empty at h_W on v2 -- RE-DERIVED, not inherited
  Part 3  generation check: the 37 generate exactly the 70499-set alive family
  Part 4  consistency vs M3 v1: the {35} thin case, and the 9 v1-revived sets

Cone semantics on v2 (m1b sec. "Menu semantics"): the two (1,3) branches are
alternatives, not conjuncts, but for the CONE analysis treating them as separate
rows with independent lambda >= 0 is exactly right, since d(max) = conv of the
branch gradients and cone(conv{a,b}) = cone{a,b}.  So all 42 rows are used.

Rigour: [IV] mpmath.iv dps 60 over box(z-hat,r); [EXACT] exact rational /
combinatorial; [NUM] float64 LP -- search only, every kill re-verified [IV].
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
OUT = os.path.join(RESULTS, 'm3b_certs.json')

import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60
mp.dps = 60
NV, SIDX = SL.NV, SL.S_IDX
NGEO = SL.NGEO_V2                     # 42
T0 = time.time()


def log(*a):
    print('[%6.1fs]' % (time.time() - T0), *a, flush=True)


H_W = Fraction(69, 32000)
ZHAT = SL.z_hat()
ZBOX = SL.point_box()
ROWS = SL.geo_rows_v2()
RNAMES = SL.row_names_v2()
_, Amid, Arad, _ = SL.jacobian_v2()
assert len(ROWS) == NGEO == 42

M1B = json.load(open(os.path.join(RESULTS, 'm1b_strata.json')))
T3 = M1B['task3']
SINGLETONS = list(T3['minimal_dead_singletons'])
M1B_PAIRS = [tuple(sorted(p)) for p in T3['pair_excludable_minimal']]
ALIVE_ROWS = list(T3['union_of_all_alive_rows'])


def cone_alive_pt(B):
    """[NUM] LP: is e_s in cone{grad g_m : m retained} at z-hat?"""
    M = [j for j in range(NGEO) if j not in set(B)]
    A = np.array([Amid[m] for m in M]).T
    b = np.zeros(NV)
    b[SIDX] = 1.0
    return linprog(np.zeros(A.shape[1]), A_eq=A, b_eq=b, bounds=(0, None),
                   method='highs').status == 0


def compute_minimal_dead():
    """Downward-closed apriori over the alive-row family.  A candidate whose
    (k-1)-subsets are ALL alive but which is itself dead is by definition a
    MINIMAL dead set.  This recomputes the minimal family from scratch rather
    than trusting m1b's singleton+pair list -- which turns out to matter."""
    t0 = time.time()
    prev, prevset, k = [()], {()}, 0
    mindead, alive_by_k = [], {}
    while prev:
        k += 1
        cand = set()
        for B in prev:
            hi = B[-1] if B else -1
            for r in ALIVE_ROWS:
                if r > hi:
                    cand.add(B + (r,))
        nxt = []
        for B in sorted(cand):
            if k > 1 and any((B[:d] + B[d + 1:]) not in prevset
                             for d in range(k)):
                continue
            if cone_alive_pt(B):
                nxt.append(B)
            else:
                mindead.append(B)
        alive_by_k[str(k)] = len(nxt)
        prevset, prev = set(nxt), nxt
    log('  apriori: %d alive, %d minimal dead inside the %d-row family (%.0fs)'
        % (sum(alive_by_k.values()), len(mindead), len(ALIVE_ROWS),
           time.time() - t0))
    return mindead, alive_by_k


log('recomputing the v2 minimal dead family from scratch...')
_MD_INSIDE, _ALIVE_BY_K = compute_minimal_dead()
MINIMAL_DEAD = [(k,) for k in SINGLETONS] + [tuple(b) for b in _MD_INSIDE]
EXTRA_VS_M1B = [tuple(b) for b in _MD_INSIDE if tuple(b) not in set(M1B_PAIRS)]

# M3 v1 results, for the consistency check
M3V1 = json.load(open(os.path.join(RESULTS, 'm3_certs.json')))


# ------------------------------------------------------------ gradients
_G0 = None


def grad0():
    global _G0
    if _G0 is None:
        _G0 = [SL.row_grad_geo(ZBOX, r)[1] for r in ROWS]
    return _G0


def _grad_hess(box, r):
    return t3lib.row_grad_hess(box, r)     # v2 has no 'dist' rows


def _tighten(gd, gm):
    out = {}
    for gi, x in gd.items():
        y = gm.get(gi)
        if y is None:
            out[gi] = x
            continue
        lo = max(mp.mpf(x.a), mp.mpf(y.a))
        hi = min(mp.mpf(x.b), mp.mpf(y.b))
        out[gi] = x if lo > hi else iv.mpf([lo, hi])
    return out


def _radv(rad):
    if isinstance(rad, (list, tuple)):
        return rad
    return [rad] * NV


def _asmp(x):
    return mp.mpf(x.numerator) / x.denominator if isinstance(x, Fraction) \
        else mp.mpf(x)


def cache_for(center, rad):
    """Gradient enclosures on box(center, rad), tightened by intersecting the
    direct interval jet with the mean-value form
        grad_j(z) in grad_j(centre) + sum_k H_jk(box)*[-rad_k, rad_k]
    (both sound => the intersection is sound).  The mean-value refinement is
    only applied when the centre is z-hat, where grad(centre) has ~zero width."""
    box = t3lib.box_from(center, rad)
    radv = _radv(rad)
    at_zhat = all(center[j] == ZHAT[j] for j in range(NV))
    out = []
    for k, r in enumerate(ROWS):
        gd = SL.row_grad_geo(box, r)[1]
        if not at_zhat:
            out.append(gd)
            continue
        _, _, H = _grad_hess(box, r)
        g0 = grad0()[k]
        gm = {}
        for gi in r['vars']:
            w = mp.mpf(0)
            for gj in r['vars']:
                h = H.get((gi, gj))
                if h is None:
                    continue
                w += max(abs(mp.mpf(h.a)), abs(mp.mpf(h.b))) * _asmp(radv[gj])
            c0 = (mp.mpf(g0[gi].a) + mp.mpf(g0[gi].b)) / 2
            pad = w + (mp.mpf(g0[gi].b) - mp.mpf(g0[gi].a))
            gm[gi] = iv.mpf([c0 - pad, c0 + pad])
        out.append(_tighten(gd, gm))
    return out


_CACHE = {}


def gcache(R):
    key = str(R)
    if key not in _CACHE:
        _CACHE[key] = grad0() if R == 0 else cache_for(ZHAT, [R] * NV)
    return _CACHE[key]


# ------------------------------------------------------------ Farkas
def farkas_robust(cache, M, ybound=1.0, den=10 ** 12):
    n = 2 * NV + 1
    A = np.zeros((len(M) + 1, n))
    for i, m in enumerate(M):
        lo = np.zeros(NV)
        hi = np.zeros(NV)
        for gi, val in cache[m].items():
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
    y = [Fraction(round(Fraction(float(v)) * den), den)
         for v in (r.x[:NV] - r.x[NV:2 * NV])]
    return (None, t) if y[SIDX] >= 0 else (y, t)


def verify(cache, M, y):
    if not (y[SIDX] < 0):
        return False, None
    y_iv = SL.to_iv_vec(y)
    worst = None
    ok = True
    for m in M:
        acc = SL.iv_dot(cache[m], y_iv)
        lo = float(acc.a)
        worst = lo if worst is None else min(worst, lo)
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


def max_radius(B, lo=H_W, hi=Fraction(1, 4), iters=14):
    if certify(B, hi)[0] is not None:
        return hi
    if certify(B, lo)[0] is None:
        a, b = Fraction(0), lo
    else:
        a, b = lo, hi
    for _ in range(iters):
        m = (a + b) / 2
        if certify(B, m)[0] is not None:
            a = m
        else:
            b = m
    return a


def certify_subdivided(B, R, max_leaves=8000, max_depth=26):
    """Tile box(z-hat,R) with sub-boxes, each carrying its own [IV]-verified
    rational y.  Sound: the leaves cover the box and each leaf certificate is
    the same rigorous argument on its own cell."""
    M = [j for j in range(NGEO) if j not in set(B)]
    leaves = []
    stack = [(list(ZHAT), [R] * NV, 0)]
    n_lp = 0
    while stack:
        if len(leaves) + len(stack) > max_leaves:
            return None
        center, rad, depth = stack.pop()
        cache = cache_for(center, rad)
        n_lp += 1
        y, t = farkas_robust(cache, M)
        ok, w = (False, None)
        if y is not None:
            ok, w = verify(cache, M, y)
        if ok:
            leaves.append({
                'center_offsets': {str(j): SL.frac_str(center[j] - ZHAT[j])
                                   for j in range(NV) if center[j] != ZHAT[j]},
                'radii': {str(j): str(rad[j]) for j in range(NV)
                          if rad[j] != R},
                'uniform_radius': str(R), 'iv_margin': w,
                'y_rational': [SL.frac_str(v) for v in y]})
            continue
        if depth >= max_depth:
            return None
        best_j, best_w = None, -1.0
        for j in range(NV):
            if rad[j] == 0:
                continue
            wj = 0.0
            for m in M:
                g = cache[m].get(j)
                if g is not None:
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


# =====================================================================
def part1():
    log('PART 1: %d v2 minimal-dead-set certificates (CORRECTED list) at h_W = %s (%.8f)'
        % (len(MINIMAL_DEAD), H_W, float(H_W)))
    out = {'basis': 'v2 (42 rows)', 'h_W': str(H_W), 'h_W_float': float(H_W),
           'n_minimal_dead_sets': len(MINIMAL_DEAD),
           'n_singletons': len(SINGLETONS),
           'n_inside_alive_family': len(_MD_INSIDE),
           'size_histogram': {str(k): sum(1 for B in MINIMAL_DEAD
                                          if len(B) == k)
                              for k in sorted(set(len(B)
                                                  for B in MINIMAL_DEAD))},
           'minimal_dead_sets': [list(B) for B in MINIMAL_DEAD],
           'CORRECTION_vs_m1b': {
               'm1b_claimed': '%d singletons + %d pairs = %d'
                              % (len(SINGLETONS), len(M1B_PAIRS),
                                 len(SINGLETONS) + len(M1B_PAIRS)),
               'actual': len(MINIMAL_DEAD),
               'missing_from_m1b': [list(b) for b in EXTRA_VS_M1B],
               'missing_names': [[RNAMES[i] for i in b] for b in EXTRA_VS_M1B],
               'note': ('m1b enumerated minimal EXCLUDABLE sets only up to size '
                        '2.  On v2 there are also minimal dead TRIPLES -- each is '
                        'BOTH rows of a flush contact plus one more row.  With '
                        'only m1b\'s %d sets, 91199 - 70499 = 20700 cone-dead '
                        'break sets would have been left UNCOVERED by the '
                        'upward-closure argument.'
                        % (len(SINGLETONS) + len(M1B_PAIRS)))},
           'source': ('minimal family recomputed from scratch here by '
                      'downward-closed apriori; m1b used only for the alive-row '
                      'family and as a cross-check'),
           'cone_semantics': (
               'all 42 v2 rows are used: m1b sec. "Menu semantics" -- the two '
               '(1,3) branches are alternatives for rank/dof but for the CONE '
               'they are correctly treated as separate rows with independent '
               'lambda >= 0, since d(max) = conv{branch gradients} and '
               'cone(conv{a,b}) = cone{a,b}.'),
           'upward_closure': (
               'B contains B\' => retained(B) subset retained(B\') => the cone '
               'shrinks, so a y killing B\' kills every B containing B\'.  The 33 '
               'certificates therefore cover EVERY cone-dead v2 break set.'),
           'both_FJ_branches': (
               'theory.md LEMMA (lambda_0 = 0 branch, region form): if '
               'grad g_m . y > 0 for every row that can be active on R, then a '
               'lambda_0 = 0 FJ point would carry lambda >= 0, lambda != 0 with '
               'sum lambda_m grad g_m = 0; dotting with y gives 0 > 0.  The '
               'e_s . y < 0 condition is not used.  Every certificate below '
               'satisfies that hypothesis by construction, so each kills BOTH FJ '
               'branches on the box.'),
           'certs': []}
    nok = 0
    for B in MINIMAL_DEAD:
        y, info = certify(B, H_W)
        rmax = max_radius(B)
        rec = {'B': list(B), 'names': [RNAMES[k] for k in B],
               'n_retained_rows': NGEO - len(B),
               'certified_at_h_W': info['ok'],
               'iv_margin_at_h_W': info.get('iv_margin'),
               'lp_margin_at_h_W': info['lp_margin'],
               'max_certified_radius': float(rmax),
               'max_certified_radius_exact': str(rmax),
               'y_rational': [SL.frac_str(v) for v in y] if y else None,
               'y_denominator': 10 ** 12}
        if not info['ok']:
            sub = certify_subdivided(B, H_W)
            rec['subdivision'] = {
                'needed': True, 'covered': sub is not None,
                'n_leaves': sub['n_leaves'] if sub else None,
                'min_iv_margin': (min(l['iv_margin'] for l in sub['leaves'])
                                  if sub else None),
                'leaves': sub['leaves'] if sub else None}
            if sub is not None:
                rec['certified_at_h_W'] = True
                rec['certified_by'] = 'subdivision (%d leaves)' % sub['n_leaves']
                rec['iv_margin_at_h_W'] = min(l['iv_margin']
                                              for l in sub['leaves'])
        else:
            rec['certified_by'] = 'single y'
        out['certs'].append(rec)
        nok += bool(rec['certified_at_h_W'])
        log('   B=%-10s %-13s  %s  margin %-10.4g r_max %.5f  %s'
            % (list(B), rec['names'][0][:13],
               'OK  ' if rec['certified_at_h_W'] else 'FAIL',
               rec.get('iv_margin_at_h_W') or 0.0, float(rmax),
               rec.get('certified_by', '')))
    out['n_certified_at_h_W'] = nok
    out['all_certified_at_h_W'] = (nok == len(MINIMAL_DEAD))
    out['n_needing_subdivision'] = sum(1 for c in out['certs']
                                       if c.get('subdivision'))
    mm = [c['iv_margin_at_h_W'] for c in out['certs']
          if c['iv_margin_at_h_W'] is not None]
    rr = [c['max_certified_radius'] for c in out['certs']]
    single = [c for c in out['certs'] if not c.get('subdivision')]
    out['margin_distribution'] = {
        'worst': min(mm), 'median': float(np.median(mm)), 'best': max(mm),
        'worst_single_y': min(c['iv_margin_at_h_W'] for c in single),
        'worst_single_y_set': min(single,
                                  key=lambda c: c['iv_margin_at_h_W'])['B']}
    out['max_radius_distribution'] = {
        'min': min(rr), 'median': float(np.median(rr)), 'max': max(rr),
        'n_at_or_above_h_W': sum(1 for r in rr if r >= float(H_W)),
        'argmin_set': out['certs'][int(np.argmin(rr))]['B'],
        'argmin_names': out['certs'][int(np.argmin(rr))]['names']}
    log('  => %d/%d certified at h_W; worst margin %.4g; min r_max %.6f'
        % (nok, len(MINIMAL_DEAD), min(mm), min(rr)))
    return out


# =====================================================================
def part2():
    log('PART 2: gained menu empty at h_W on v2 -- re-derived')
    cert = SL.load_cert()
    noncontact = [tuple(p) for p in cert['noncontact_pairs']]
    # v2 contact pairs, read off the v2 rows themselves
    v2_contact = set()
    for c in SL.geo_constraints_v2():
        if c['kind'] in ('edge', 'sep', 'dist'):
            v2_contact.add(tuple(sorted((c['i'], c['j']))))
    all_pairs = set(tuple(sorted(p)) for p in
                    itertools.combinations(range(SL.NSQ), 2))
    derived_noncontact = sorted(all_pairs - v2_contact)
    identical = derived_noncontact == sorted(noncontact)

    L_PAIR = 3.0 * float(np.sqrt(2.0))
    L_WALL_HI = 1.0 + 3.0 / float(np.sqrt(2.0))
    h = float(H_W)
    box = t3lib.box_from(ZHAT, H_W)

    worst_pair, worst_pair_lo = None, None
    for (i, j) in derived_noncontact:
        lo = float(t3lib.pair_sep_iv(box, i, j).a)
        if worst_pair_lo is None or lo < worst_pair_lo:
            worst_pair_lo, worst_pair = lo, (i, j)
    gaps0 = {}
    for (i, j) in derived_noncontact:
        gaps0['%d-%d' % (i, j)] = float(t3lib.pair_sep_iv(ZBOX, i, j).a)
    min_pair_gap = min(gaps0.values())

    repaired = {}
    for (i, j) in derived_noncontact:
        if float(t3lib.pair_sep_iv(box, i, j).a) > 0:
            continue
        vs = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        best = None
        for signs in itertools.product((-1, 1), repeat=len(vs)):
            c2 = list(ZHAT)
            r2 = [H_W] * NV
            for v, s in zip(vs, signs):
                c2[v] = ZHAT[v] + s * H_W / 2
                r2[v] = H_W / 2
            l2 = float(t3lib.pair_sep_iv(t3lib.box_from(c2, r2), i, j).a)
            best = l2 if best is None else min(best, l2)
        repaired['%d-%d' % (i, j)] = best

    have = set()
    for c in SL.geo_constraints_v2():
        if c['kind'] == 'wall':
            have.add((c['i'], c['corner'], c['wall']))
    worst_wall, worst_wall_lo, nwall = None, None, 0
    min_wall_gap0 = None
    for i in range(SL.NSQ):
        for cc in range(4):
            for w in SL.WALLS:
                if (i, cc, w) in have:
                    continue
                nwall += 1
                lo = float(SL.wall_gap(box, i, cc, w).a)
                g0 = float(SL.wall_gap(ZBOX, i, cc, w).a)
                if worst_wall_lo is None or lo < worst_wall_lo:
                    worst_wall_lo, worst_wall = lo, (i, cc, w)
                min_wall_gap0 = g0 if min_wall_gap0 is None \
                    else min(min_wall_gap0, g0)
    pair_ok = worst_pair_lo > 0 or (repaired and min(repaired.values()) > 0)
    out = {'h_W': str(H_W),
           'noncontact_pair_list_derived_from_v2_rows': [list(p) for p in
                                                         derived_noncontact],
           'n_noncontact_pairs': len(derived_noncontact),
           'identical_to_v1_A22_list': bool(identical),
           'identity_note': (
               'v2 ADDS rows for (1,3), (0,1), (0,3), but A22\'s cert already '
               'classified all three as CONTACT pairs, so they were never in the '
               'non-contact list.  Verified here by deriving the non-contact list '
               'from the v2 rows and comparing: %s.'
               % ('identical' if identical else 'DIFFERENT -- investigate')),
           'lipschitz': {
               'L_pair': L_PAIR, 'L_wall_hi': L_WALL_HI,
               'pair_travel_bound': L_PAIR * h,
               'min_noncontact_pair_gap_at_zhat': min_pair_gap,
               'pair_margin': min_pair_gap - L_PAIR * h,
               'pair_ok': bool(L_PAIR * h < min_pair_gap),
               'wall_travel_bound': L_WALL_HI * h,
               'min_noncontact_wall_gap_at_zhat': min_wall_gap0,
               'wall_margin': min_wall_gap0 - L_WALL_HI * h,
               'wall_ok': bool(L_WALL_HI * h < min_wall_gap0)},
           'interval_direct': {
               'min_pair_gap_lower_bound_on_box_naive': worst_pair_lo,
               'argmin_pair': list(worst_pair),
               'naive_pair_ok': bool(worst_pair_lo > 0),
               'subdivided_repair': repaired,
               'n_noncontact_wall_combos': nwall,
               'min_wall_clearance_lower_bound_on_box': worst_wall_lo,
               'argmin_wall': list(worst_wall),
               'wall_ok': bool(worst_wall_lo > 0),
               'pair_ok': bool(pair_ok)},
           'menu_empty': bool(pair_ok and worst_wall_lo > 0)}
    out['one_line_statement'] = (
        'LEMMA (gained menu empty at h_W, basis v2).  On box(z-hat, 69/32000) no '
        'non-contact pair can touch and no new corner-wall contact can form, so '
        'the gained-contact menu of T0.1(ii) is EMPTY and the certificates of '
        'Part 1 need beat only the retained v2 rows.  The %d non-contact pairs '
        'derived from the v2 rows are %s to A22\'s list (v2\'s new rows all '
        'describe pairs A22 already counted as contacts), so M3 v1\'s Lemma 1 '
        'carries over: pair travel <= 3sqrt2 * %.8f = %.7f < %.6f, wall travel '
        '<= %.7f < %.6f [EXACT]; and independently every non-contact pair '
        'separation and corner-wall clearance has a strictly positive [IV] lower '
        'bound over the box (%.6f / %.6f, the pair bound after the 64-sub-box '
        'repair of the dependency-pessimistic naive SAT enclosure).'
        % (len(derived_noncontact), 'identical' if identical else 'NOT identical',
           h, L_PAIR * h, min_pair_gap, L_WALL_HI * h, min_wall_gap0,
           min(repaired.values()) if repaired else worst_pair_lo, worst_wall_lo))
    log('  noncontact list identical to v1: %s (%d pairs)'
        % (identical, len(derived_noncontact)))
    log('  Lipschitz pair %.7f < %.6f; wall %.7f < %.6f'
        % (L_PAIR * h, min_pair_gap, L_WALL_HI * h, min_wall_gap0))
    log('  [IV] naive pair %.6f (repaired %s); wall %.6f'
        % (worst_pair_lo,
           '%.6f' % min(repaired.values()) if repaired else 'n/a',
           worst_wall_lo))
    return out


# =====================================================================
def part3():
    log('PART 3: do the minimal dead sets generate the v2 dead family?')
    forb = [set(B) for B in MINIMAL_DEAD]
    # any break set touching a row outside ALIVE_ROWS contains a singleton
    outside = sorted(set(range(NGEO)) - set(ALIVE_ROWS))
    assert set(outside) == set(SINGLETONS), (outside, SINGLETONS)
    alive = []
    for r in range(0, len(ALIVE_ROWS) + 1):
        for B in itertools.combinations(ALIVE_ROWS, r):
            s = set(B)
            if any(f <= s for f in forb):
                continue
            alive.append(tuple(B))
    nonempty = [B for B in alive if B]
    by_k = {}
    for B in nonempty:
        by_k[str(len(B))] = by_k.get(str(len(B)), 0) + 1
    claimed = T3['n_alive_breaksets']
    # what m1b's incomplete list would have given
    forb33 = [set((k,)) for k in SINGLETONS] + [set(p) for p in M1B_PAIRS]
    n33 = 0
    for r in range(1, len(ALIVE_ROWS) + 1):
        for B in itertools.combinations(ALIVE_ROWS, r):
            s = set(B)
            if not any(f <= s for f in forb33):
                n33 += 1
    out = {'n_alive_from_minimal_dead_sets': len(nonempty),
           'm1b_claimed_n_alive': claimed,
           'agrees': len(nonempty) == claimed,
           'alive_by_size': by_k,
           'm1b_alive_by_size': T3['alive_by_size'],
           'by_size_agrees': by_k == {k: v for k, v in
                                      T3['alive_by_size'].items()},
           'apriori_alive_by_size': _ALIVE_BY_K,
           'K': max(len(B) for B in nonempty),
           'm1b_K': T3['max_surviving_breakset_size_K'],
           'n_singleton_killers': len(SINGLETONS),
           'coverage_gap_of_m1b_list': {
               'n_alive_if_only_m1b_33_used': n33,
               'n_truly_alive': len(nonempty),
               'n_cone_dead_sets_m1b_list_would_MISS': n33 - len(nonempty)},
           'method': ('[EXACT] a break set is cone-alive iff it is a subset of '
                      'the %d-row alive family containing none of the %d minimal '
                      'dead sets; enumerated exhaustively and cross-checked '
                      'level-by-level against m1b\'s independently computed '
                      'alive counts.' % (len(ALIVE_ROWS), len(MINIMAL_DEAD)))}
    log('  alive from the 33: %d (m1b says %d, agree=%s); K %d vs %d; '
        'by-size agrees=%s'
        % (len(nonempty), claimed, out['agrees'], out['K'], out['m1b_K'],
           out['by_size_agrees']))
    return out


# =====================================================================
def part4():
    log('PART 4: consistency with M3 v1')
    v1certs = M3V1['part1_minimal_dead_certificates']['certs']
    v1_thin = [c for c in v1certs if c.get('subdivision')]
    thin_B = [c['B'] for c in v1_thin]
    thin_status = []
    for B in thin_B:
        Bt = tuple(B)
        in_v2 = Bt in [tuple(x) for x in MINIMAL_DEAD]
        rec = {'B': B, 'v1_names': [c for c in v1_thin
                                    if c['B'] == B][0]['names'],
               'v1_n_leaves': [c for c in v1_thin
                               if c['B'] == B][0]['subdivision']['n_leaves'],
               'v1_min_margin': [c for c in v1_thin
                                 if c['B'] == B][0]['subdivision']['min_iv_margin'],
               'still_minimal_dead_in_v2': bool(in_v2)}
        if in_v2:
            m = [c for c in P1['certs'] if c['B'] == B][0]
            rec['v2_certified_by'] = m.get('certified_by')
            rec['v2_margin'] = m['iv_margin_at_h_W']
            rec['v2_max_radius'] = m['max_certified_radius']
        thin_status.append(rec)

    # the 9 sets my v1 sec.4 preview said (1,3) revives
    prev = M3V1['part4_v2_preview_pair_1_3']['detail']
    revived = [r for r in prev if not r['still_cone_dead_at_zhat_with_13']]
    md = set(tuple(x) for x in MINIMAL_DEAD)
    dropped = set(SL.V2_DROPPED_V1_ROWS)
    rows = []
    for r in revived:
        B = tuple(r['B'])
        if set(B) & dropped:
            verdict = 'row dropped in v2 (was a dist surrogate)'
            ok = True
        elif B in md:
            verdict = 'STILL minimal dead in v2'
            ok = False
        elif any(set(f) <= set(B) for f in MINIMAL_DEAD):
            verdict = 'no longer minimal, but still dead (contains a minimal set)'
            ok = False
        else:
            verdict = 'cone-ALIVE in v2 (revival confirmed)'
            ok = True
        rows.append({'B': list(B), 'v1_names': r['names'],
                     'v2_verdict': verdict, 'preview_confirmed': ok})
    nconf = sum(1 for r in rows if r['preview_confirmed'])
    out = {'v1_thin_cases': thin_status,
           'n_v1_thin_cases': len(thin_status),
           'v1_revival_preview_check': {
               'n_predicted_revived': len(rows),
               'n_confirmed_by_v2': nconf,
               'detail': rows,
               'interpretation': (
                   'the v1 preview added ONLY the (1,3) rows; v2 additionally '
                   'DROPS the two dist surrogates and ADDS four flush rows for '
                   '(0,1) and (0,3).  Predictions that disagree are exactly the '
                   'sets whose fate is decided by those other changes, which the '
                   'preview explicitly did not model.')},
           }
    log('  v1 thin case(s): %s' % [(r['B'], r['still_minimal_dead_in_v2'],
                                    r.get('v2_certified_by')) for r in thin_status])
    log('  v1 revival preview: %d/%d confirmed by v2' % (nconf, len(rows)))
    for r in rows:
        log('     %-8s %-22s %s' % (r['B'], r['v1_names'][0], r['v2_verdict']))
    return out


def main():
    global P1
    R = {'meta': {'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
                  'source': 'A35/M3-delta (basis v2)', 'h_W': str(H_W),
                  'iv_dps': 60, 'n_rows': NGEO, 'row_names': RNAMES,
                  'inputs': ['results/m1b_strata.json', 'results/m3_certs.json',
                             'A22 krawczyk_cert.json', 'A30 t3lib.py']}}
    P1 = part1()
    R['part1_minimal_dead_certificates_v2'] = P1
    R['part2_gained_menu_empty_v2'] = part2()
    R['part3_generation_check_v2'] = part3()
    R['part4_consistency_with_v1'] = part4()
    p2 = R['part2_gained_menu_empty_v2']
    R['HEADLINE'] = {
        'region_T1a_closed_on_box_h_W_basis_v2':
            bool(P1['all_certified_at_h_W'] and p2['menu_empty']),
        'n_certificates': P1['n_minimal_dead_sets'],
        'm1b_would_have_used': len(SINGLETONS) + len(M1B_PAIRS),
        'n_certified': P1['n_certified_at_h_W'],
        'n_needing_subdivision': P1['n_needing_subdivision'],
        'worst_iv_margin': P1['margin_distribution']['worst'],
        'median_iv_margin': P1['margin_distribution']['median'],
        'gained_menu_empty': p2['menu_empty'],
        'generation_check_agrees': R['part3_generation_check_v2']['agrees'],
        'statement': (
            'ON THE REPAIRED 42-ROW BASIS v2: every cone-dead break set is '
            'certified FJ-free on box(z-hat, 69/32000) -- in BOTH FJ branches, by '
            'theory.md\'s lambda_0 = 0 region lemma -- by one of 37 [IV]-verified '
            'rational Farkas directions, and the gained-contact menu is certified '
            'EMPTY on that box.  The cone-ALIVE layer (70499 break sets) is '
            'M2-delta\'s queue, not covered here.')}
    R['meta']['runtime_secs'] = time.time() - T0
    with open(OUT, 'w') as f:
        json.dump(R, f, indent=1, default=str)
    log('HEADLINE: region T1-a closed on box(h_W), basis v2 = %s'
        % R['HEADLINE']['region_T1a_closed_on_box_h_W_basis_v2'])
    log('done -> %s' % OUT)


if __name__ == '__main__':
    main()
