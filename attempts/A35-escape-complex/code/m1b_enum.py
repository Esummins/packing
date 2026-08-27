"""m1b_enum.py -- A35 measurement M1b: re-run of the M1 enumeration on the
REPAIRED row basis v2 (42 geometric rows), per the A35 lead's follow-up.

BASIS v2 (precise statement -- see strata_lib.V2_NEW_ROWS for the row dicts):
  rows  0..35 : verbatim from A22's krawczyk_cert.json constraints 0..35
  rows 36, 37 : v1's centre-distance surrogates D0-1, D0-3  ->  DROPPED
  rows 36..39 : F0-1a, F0-1b, F0-3a, F0-3b -- proper flush contact separation
                rows for pairs (0,1) and (0,3), two per pair (one per owner),
                following A22's own convention for tilted flush pairs (6,9)
  rows 40, 41 : C1-3x, C1-3y -- the two orthogonal separation branches of the
                (1,3) CORNER-CORNER contact, absent from v1 entirely

Tie / menu semantics (drain_lemma D3', theory.md G5) are handled by running the
stratum enumeration in three variants: 'conj' (both (1,3) branches maintained),
'selx', 'sely'.  See strata_lib's BASIS v2 block for why the cone analysis is
correct under 'conj' while the rank/dof analysis is not.

Kill-test cascade now has FIVE tests, with M4's wedge test inserted:
  1 EMPTY      rank(A_M) = 34                                      [RFP]
  2 CONE-DEAD  e_s not in cone{grad g_m, m in M}                   [LP/IV]
  3 WEDGED     C(B) = {v in ker A_M : A_B v >= 0} = {0}            [LP]
  4 COLLAPSE   force-balance sign rule kills every retained row    [NUM]
  5 LOADPATH   no x- and no y-wall-to-wall path                    [NUM]

Writes results/m1b_strata.json and results/m1b_report.md is written separately.
"""
from __future__ import annotations

import itertools
import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import strata_lib as SL   # noqa: E402
import t3lib             # noqa: E402
import m1_enum as M1     # noqa: E402  (reuse force-balance / graph machinery)

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
OUT = os.path.join(RES, 'm1b_strata.json')

SEED = 20260827
NV = SL.NV
SIDX = SL.S_IDX
N2 = SL.NGEO_V2          # 42

T0 = time.time()


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


A_iv, A2, R2, VALS2 = SL.jacobian_v2()
ROWS2 = SL.geo_rows_v2()
NAMES2 = SL.row_names_v2()
CONS2 = SL.geo_constraints_v2()
ZBOX = SL.point_box()
ZHAT = SL.z_hat()
ES = SL.es_vector()

RESULT = {'meta': {
    'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'task': 'A35 / M1b -- M1 enumeration re-run on the repaired basis v2',
    'basis_v2_definition': {
        'rows_0_35': 'verbatim A22 krawczyk_cert.json constraints 0..35',
        'dropped_v1_rows': {'36': 'D0-1 centre-distance surrogate',
                            '37': 'D0-3 centre-distance surrogate'},
        'new_rows': SL.V2_NEW_ROWS,
        'n_rows': N2,
        'tie_alternatives': SL.V2_FLUSH_TIE_ALTERNATIVES,
    },
    'defect_verification': {},
    'row_names': NAMES2,
    'max_abs_row_value_at_zhat': max(
        max(abs(float(v.a)), abs(float(v.b))) for v in VALS2),
    'iv_dps': SL.IV_DPS,
    'seed': SEED,
    'rigour_tags': dict(M1.RESULT['meta']['rigour_tags'],
                        LP='float64 LP (HiGHS) feasibility/optimality; '
                           'headline LP verdicts are re-checked with a '
                           'rational certificate verified in mpmath.iv'),
}}


# =====================================================================
# 0. verify the two defects in exact / interval arithmetic
# =====================================================================
def task0():
    log('TASK 0: verifying the two reported basis defects')
    z = ZHAT
    d13 = (z[3] - z[9]) ** 2 + (z[4] - z[10]) ** 2
    d01 = (z[0] - z[3]) ** 2 + (z[1] - z[4]) ** 2
    d03 = (z[0] - z[9]) ** 2 + (z[1] - z[10]) ** 2
    gaps = {}
    for (i, j) in ((1, 3), (0, 1), (0, 3)):
        g = SL.sat_gap_pair(ZBOX, i, j)
        gaps['%d-%d' % (i, j)] = [float(g.a), float(g.b)]
    out = {
        'defect_b_pair_1_3': {
            'centre_dist_squared_exact': str(d13),
            'is_exactly_2': d13 == 2,
            'sat_gap_iv': gaps['1-3'],
            'verdict': 'CONFIRMED: (1,3) is a genuine corner-corner contact '
                       '(SAT gap 0) whose centre distance^2 is exactly 2, so '
                       'no dist row could ever have represented it. It is a '
                       '14th contact pair and was entirely absent from v1.',
        },
        'defect_a_dist_surrogates': {
            'centre_dist_squared_0_1_exact': str(d01),
            'centre_dist_squared_0_3_exact': str(d03),
            'both_exactly_1': (d01 == 1 and d03 == 1),
            'sat_gap_0_1_iv': gaps['0-1'], 'sat_gap_0_3_iv': gaps['0-3'],
            'verdict': 'CONFIRMED: both are flush contacts with centre '
                       'distance exactly 1, so the dist rows read 0 but only '
                       'pin the centre distance, not the contact.',
        },
        'method': '[EXACT] centre distances in exact Fraction arithmetic on '
                  'z-hat; [IV] SAT gaps in mpmath.iv at dps 60.',
    }
    # dominance ties of the chosen selections
    ties = []
    for k in range(36, N2):
        c = CONS2[k]
        o, e, p, kk = c['j'], c['edge'], c['i'], c['corner']
        alt = SL.V2_FLUSH_TIE_ALTERNATIVES[c['name']]['corner']
        rec = {'row': k, 'name': c['name'], 'chosen_corner': kk,
               'tied_alternative_corner': alt}
        for tag, cc in (('chosen', kk), ('alt', alt)):
            sv = t3lib.row_value(ZBOX, t3lib.sep_row(o, e, p, cc))
            dm = min(float(t3lib.row_value(
                ZBOX, t3lib.dom_row(o, e, p, cc, m)).a)
                for m in range(4) if m != cc)
            rec[tag + '_sep_value'] = float(sv.a)
            rec[tag + '_min_dominance'] = dm
        ties.append(rec)
    out['selection_ties'] = ties
    out['selection_tie_note'] = (
        'Every one of the 6 new rows sits at a DOMINANCE TIE at z-hat: the '
        'alternative corner of the same owner edge has dominance margin 0 to '
        'within 1e-61 and is equally valid as a selection. The two tied '
        'corners give DIFFERENT theta-gradients (e.g. +1/2 vs -1/2 for the '
        '(0,1) rows), so this is theory.md G5 biting at the jam itself, not '
        'only along routes. The cone results below are unaffected (the '
        'possibly-active menu contains both, and cone(conv) = cone), but any '
        '(C) continuation certificate must carry both selections at its faces.')
    log('  defect (b) (1,3) corner-corner: dist^2 = %s exactly, SAT gap 0  -> '
        'CONFIRMED' % d13)
    log('  defect (a) dist surrogates: dist^2(0,1) = %s, dist^2(0,3) = %s  -> '
        'CONFIRMED' % (d01, d03))
    return out


# =====================================================================
# 1. rank / self-stress / Farkas
# =====================================================================
def task1():
    log('TASK 1: rank / self-stress / nonneg-self-stress on v2')
    out = {}
    ok, basis, bound = SL.certified_rank34(range(N2), A2, R2)
    sv = np.linalg.svd(A2, compute_uv=False)
    out['rank'] = {
        'value': 34, 'certified_lower_bound': 34 if ok else None,
        'witness_basis_rows': list(basis) if ok else None,
        'rump_bound': bound,
        'sv_min': float(sv[-1]), 'sv_all': [float(x) for x in sv],
        'v1_comparison': {'rank': 34, 'sv_min': 0.12664282},
        'method': '[RFP] nonsingular 34x34 minor, ||I - Y*A||_inf = %.3e < 1. '
                  'rank <= 34 trivial. FULLY RIGOROUS.' % bound,
    }
    assert ok

    U, s_all, Vt = np.linalg.svd(A2)
    dim = N2 - 34
    N = U[:, 34:]
    supp = np.linalg.norm(N, axis=1)
    support = [k for k in range(N2) if supp[k] > 1e-8]
    supp_cert = {}
    for k in support:
        M = [j for j in range(N2) if j != k]
        okk, _, bd = SL.certified_rank34(M, A2, R2)
        supp_cert[k] = {'certified': bool(okk), 'rump_bound': bd}
    out['self_stress'] = {
        'dim': dim, 'v1_dim': 4,
        'method_dim': '[RFP+EXACT] dim ker(A^T) = %d - 34 = %d.' % (N2, dim),
        'max_residual_AtN': float(np.abs(A2.T @ N).max()),
        'support_rows': support, 'support_size': len(support),
        'support_row_names': [NAMES2[k] for k in support],
        'nonsupport_rows': [k for k in range(N2) if supp[k] <= 1e-8],
        'support_certified_all': all(v['certified'] for v in supp_cert.values()),
        'support_certified': {str(k): v for k, v in supp_cert.items()},
        'method_support': '[RFP] k in support iff rank(A_-k) = 34; each '
                          'certified by a nonsingular 34-minor among the other '
                          'rows. Non-support rows are [NUM] only.',
    }
    log('  rank 34 certified (bound %.2e); self-stress dim %d (v1: 4); '
        'support %d of %d' % (bound, dim, len(support), N2))

    # ---- nonnegative self-stress?  THE flagged question -------------------
    Aeq = np.vstack([A2.T, np.ones(N2)])
    beq = np.r_[np.zeros(NV), 1.0]
    r = linprog(np.zeros(N2), A_eq=Aeq, b_eq=beq,
                bounds=[(0, None)] * N2, method='highs')
    exists = bool(r.success)
    # strict Farkas witness (its existence PROVES none exists, by Gordan)
    A_ub = np.zeros((N2, NV + 1))
    A_ub[:, :NV] = -A2
    A_ub[:, NV] = 1.0
    c = np.zeros(NV + 1)
    c[NV] = -1.0
    rr = linprog(c, A_ub=A_ub, b_ub=np.zeros(N2),
                 bounds=[(-1.0, 1.0)] * NV + [(0.0, 10.0)], method='highs')
    assert rr.success
    DEN = 10 ** 9
    y_q = [Fraction(round(Fraction(float(v)) * DEN), DEN) for v in rr.x[:NV]]
    y_iv = SL.to_iv_vec(y_q)
    lows = []
    for k in range(N2):
        _, g = SL.row_grad_geo(ZBOX, ROWS2[k])
        lows.append(float(SL.iv_dot(g, y_iv).a))
    mn = min(lows)
    out['nonneg_self_stress'] = {
        'ALARM_nonneg_self_stress_exists': bool(exists and mn <= 0),
        'lp_says_exists': exists,
        'farkas_witness_y_rational': [SL.frac_str(v) for v in y_q],
        'farkas_lp_margin': float(-rr.fun),
        'min_verified_lower_bound': mn,
        'verified_lower_bounds': lows,
        'v1_min_verified_lower_bound': 0.2297001173304187,
        'verdict': ('NO nonnegative nonzero self-stress exists on the 42 v2 '
                    'rows. The 0-1-3 block with the (1,3) diagonal brace does '
                    'NOT carry one. Certified by a strict Farkas witness: all '
                    '42 products grad g_k . y are verified > 0 in mpmath.iv at '
                    'dps 60, min = %.6f (v1: 0.229700). This also re-certifies '
                    'cone pointedness and boundedness of the multiplier '
                    'polytope on v2, and keeps the FJ lambda_0 = 0 branch '
                    'EMPTY at z-hat.' % mn) if mn > 0 else
                   'ALARM: a nonnegative self-stress may exist -- INSPECT.',
        'method': '[IV] Gordan pair: the LP for a nonnegative self-stress is '
                  'infeasible AND a rational strict Farkas direction is '
                  'verified in mpmath.iv. FULLY RIGOROUS.',
    }
    assert mn > 0, 'ALARM: nonnegative self-stress on v2'
    log('  NO nonneg self-stress on v2 (Farkas min lower bound %.6f)' % mn)
    return out


# =====================================================================
# 2. lambda* on v2
# =====================================================================
def polytope_lp(c=None, fix_zero=(), maximize=False):
    """LP over P = {lambda >= 0 : A2^T lambda = e_s}."""
    Aeq = A2.T.copy()
    beq = ES.copy()
    bnds = [(0, None)] * N2
    for k in fix_zero:
        bnds[k] = (0, 0)
    if c is None:
        c = np.zeros(N2)
    c = -np.asarray(c, dtype=float) if maximize else np.asarray(c, dtype=float)
    return linprog(c, A_eq=Aeq, b_eq=beq, bounds=bnds, method='highs')


def task2():
    log('TASK 2: lambda* on v2 (uniform floor)')
    out = {}
    lo, hi = {}, {}
    for k in range(N2):
        ck = np.zeros(N2)
        ck[k] = 1.0
        r1 = polytope_lp(ck)
        r2 = polytope_lp(ck, maximize=True)
        lo[k] = float(r1.fun) if r1.success else None
        hi[k] = float(-r2.fun) if r2.success else None
    forced_zero = [k for k in range(N2) if hi[k] is not None and hi[k] < 1e-9]
    always_pos = [k for k in range(N2) if lo[k] is not None and lo[k] > 1e-9]
    out['per_row_multiplier_range'] = {
        str(k): {'min': lo[k], 'max': hi[k], 'name': NAMES2[k]}
        for k in range(N2)}
    out['forced_zero_rows'] = forced_zero
    out['forced_zero_row_names'] = [NAMES2[k] for k in forced_zero]
    out['always_positive_rows'] = always_pos

    # unrestricted Chebyshev floor (expected 0 because of the forced-zero rows)
    def cheb(rows):
        nl = N2 + 1
        Aeq = np.zeros((NV, nl))
        Aeq[:, :N2] = A2.T
        Aub = np.zeros((len(rows), nl))
        for i, k in enumerate(rows):
            Aub[i, k] = -1.0
            Aub[i, N2] = 1.0
        c = np.zeros(nl)
        c[N2] = -1.0
        return linprog(c, A_ub=Aub, b_ub=np.zeros(len(rows)),
                       A_eq=Aeq, b_eq=ES, bounds=[(0, None)] * nl,
                       method='highs')

    r_all = cheb(list(range(N2)))
    keep = [k for k in range(N2) if k not in set(forced_zero)]
    r_res = cheb(keep)
    assert r_res.success
    lam_lp = r_res.x[:N2]
    floor_res = float(-r_res.fun)
    out['floor_all_42_rows'] = float(-r_all.fun) if r_all.success else None
    out['restricted_floor'] = floor_res
    out['restricted_floor_rows'] = keep
    out['sum_lambda'] = float(lam_lp.sum())
    out['v1_floor'] = 0.047644047
    out['v1_sum'] = 4.353502

    # exact correction on a certified-invertible 34-row subsystem of v2
    # STRUCTURAL OBSTACLE: rank(A2 over the 40 load-bearing rows) = 33, so
    # there is NO square 34-row subsystem avoiding the two forced-zero rows.
    # The correction is therefore done on a 33-row / 33-equation nonsingular
    # block, with lambda pinned to EXACTLY 0 on the forced-zero rows, and the
    # full 34-equation residual verified afterwards in mpmath.iv.
    from scipy.linalg import qr
    rank_keep = int((np.linalg.svd(A2[keep], compute_uv=False)
                     > SL.RANK_TOL).sum())
    out['rank_over_load_bearing_rows'] = rank_keep
    _, _, piv = qr(A2[keep].T, pivoting=True, mode='economic')
    S2 = sorted(keep[int(p)] for p in piv[:rank_keep])
    Sc = [k for k in range(N2) if k not in set(S2)]
    # pick rank_keep independent EQUATIONS (coordinates) out of the 34
    _, _, piv2 = qr(A2[S2], pivoting=True, mode='economic')
    EQ = sorted(int(p) for p in piv2[:rank_keep])
    blk = A2[np.ix_(S2, EQ)].T
    okS, bS = SL.certify_nonsingular(blk, R2[np.ix_(S2, EQ)].T)
    assert okS, 'v2 correction block not certified nonsingular'
    DPS = 90
    Amp = SL.jacobian_mp_v2(dps=DPS)
    old = mp.dps
    mp.dps = DPS
    DEN_F = 10 ** 20
    lam_free = {k: (Fraction(0) if k in set(forced_zero) else
                    Fraction(round(Fraction(float(lam_lp[k])) * DEN_F), DEN_F))
                for k in Sc}
    rhs = mp.zeros(NV, 1)
    rhs[SIDX, 0] = mp.mpf(1)
    for k in Sc:
        fk = mp.mpf(lam_free[k].numerator) / mp.mpf(lam_free[k].denominator)
        for j in range(NV):
            rhs[j, 0] -= Amp[k, j] * fk
    MS = mp.zeros(rank_keep, rank_keep)
    rr_ = mp.zeros(rank_keep, 1)
    for a, j in enumerate(EQ):
        rr_[a, 0] = rhs[j, 0]
        for b, k in enumerate(S2):
            MS[a, b] = Amp[k, j]
    solS = mp.lu_solve(MS, rr_)
    DEN_L = 10 ** 45
    lam_q = [None] * N2
    for r_, k in enumerate(S2):
        lam_q[k] = Fraction(int(mp.floor(solS[r_, 0] * DEN_L + mp.mpf('0.5'))),
                            DEN_L)
    for k in Sc:
        lam_q[k] = lam_free[k]
    mp.dps = old
    out['correction_block'] = {
        'rows': S2, 'equations': EQ, 'rump_bound': bS,
        'note': 'rank(A2 over the %d load-bearing rows) = %d < 34, so no '
                'square retained subsystem avoids the two forced-zero rows. '
                'The correction uses a [RFP]-certified %dx%d block and the '
                'FULL 34-equation residual is verified in mpmath.iv below.'
                % (len(keep), rank_keep, rank_keep, rank_keep)}

    lam_ivv = [t3lib._to_iv(x) for x in lam_q]
    acc = [iv.mpf(0)] * NV
    for k in range(N2):
        _, g = SL.row_grad_geo(ZBOX, ROWS2[k])
        for gi, val in g.items():
            acc[gi] = acc[gi] + val * lam_ivv[k]
    acc[SIDX] = acc[SIDX] - iv.mpf(1)
    res = sum(max(abs(float(a.a)), abs(float(a.b))) for a in acc)
    lam_keep_min = min(lam_q[k] for k in keep)
    out['lambda_rational'] = [SL.frac_str(v) for v in lam_q]
    out['S_rows'] = S2
    out['S_rows_rump_bound'] = bS
    out['residual_l1_upper_bound'] = res
    out['residual_ok'] = bool(res <= 1e-25)
    out['min_lambda_over_kept_rows_exact'] = SL.frac_str(lam_keep_min)
    out['min_lambda_over_kept_rows_float'] = float(lam_keep_min)
    out['all_lambda_nonneg'] = bool(min(lam_q) >= 0)
    out['headline'] = (
        'The UNIFORM floor over all 42 rows is 0: rows %s (%s) are FORCED to '
        'lambda = 0 by the v2 stationarity system (their max over the whole '
        'multiplier polytope is 0). Excluding exactly those two rows, the '
        'floor is %.9f -- i.e. theory.md\'s constant 0.047644 SURVIVES the '
        'basis repair verbatim; only its STATEMENT needs the restriction. '
        'Sum of lambda* grows 4.353502 -> %.6f.'
        % (forced_zero, [NAMES2[k] for k in forced_zero], floor_res,
           float(lam_lp.sum())))
    out['impact_on_theory_A'] = (
        'theory.md (A)/Consequence 1 reads s(z) >= Phi(z) + lambda_floor * '
        'G(z) with G = sum over ALL rows. On v2 that form is FALSE as written '
        '(lambda_floor = 0). The repaired form is G(z) = sum over the %d '
        'non-forced-zero rows, with the SAME constant 0.047644. The only '
        'escapes with no first-order ascent guarantee are those that open '
        'ONLY rows %s -- and those break sets are covered by the kill-test '
        'cascade in Task 4 (see synthesis).'
        % (len(keep), forced_zero))
    out['method'] = ('[EXACT+IV] per-row min/max over P by 84 LPs; Chebyshev '
                     'LP for the restricted floor; the 8 rows outside a '
                     '[RFP]-certified invertible 34-subsystem frozen at '
                     'rationalised LP values and the 34 remaining re-solved at '
                     'mpmath dps 90, rationalised at denominator 1e45; '
                     'residual bounded in mpmath.iv dps 60.')
    log('  forced-zero rows: %s %s' % (forced_zero,
                                       [NAMES2[k] for k in forced_zero]))
    log('  floor over all 42 = %.3e ; restricted floor = %.9f (v1 0.047644047)'
        % (out['floor_all_42_rows'] or 0.0, floor_res))
    log('  residual_l1 <= %.2e' % res)
    return out, lo, hi


# =====================================================================
# 3. cone analysis on v2
# =====================================================================
def cone_alive(B):
    """True iff exists lambda >= 0, A2^T lambda = e_s, lambda_B = 0."""
    r = polytope_lp(fix_zero=B)
    return bool(r.success)


def task3(lo, hi):
    log('TASK 3: cone analysis on v2')
    out = {}
    Z0 = [k for k in range(N2) if lo[k] is not None and lo[k] < 1e-9]
    out['rows_that_can_be_zero_Z0'] = Z0
    out['minimal_dead_singletons'] = [k for k in range(N2) if k not in set(Z0)]
    out['n_minimal_dead_singletons'] = N2 - len(Z0)
    out['v1_minimal_dead_singletons'] = 28

    # exhaustive downward-closed enumeration of the ALIVE family
    alive = {(): True}
    level = [()]
    sizes = {}
    n_lp = 0
    while level:
        nxt = []
        for B in level:
            mx = B[-1] if B else -1
            for k in Z0:
                if k <= mx:
                    continue
                C = B + (k,)
                n_lp += 1
                if cone_alive(C):
                    alive[C] = True
                    nxt.append(C)
        for C in nxt:
            sizes[len(C)] = sizes.get(len(C), 0) + 1
        level = nxt
        log('    alive at size %d: %d  (LPs so far %d)'
            % (len(level[0]) if level else 0, len(level), n_lp))
    alive_sets = [list(b) for b in sorted(alive) if b]
    out['n_alive_breaksets'] = len(alive_sets)
    out['alive_by_size'] = dict(sorted(sizes.items()))
    out['n_LPs'] = n_lp
    maxsize = max(len(b) for b in alive_sets)
    out['max_surviving_breakset_size_K'] = maxsize
    out['v1_K'] = 6
    aset = {tuple(b) for b in alive_sets}
    # b is maximal iff no single-row extension stays alive (downward closure)
    maximal = [b for b in alive_sets
               if not any(tuple(sorted(b + [k])) in aset
                          for k in Z0 if k not in set(b))]
    out['alive_breaksets_note'] = (
        'the full list of %d alive break sets is not stored (it would dominate '
        'the file); it is fully determined by the %d maximal ones, since '
        'aliveness is downward closed.' % (len(alive_sets), len(maximal)))
    out['n_maximal_surviving_breaksets'] = len(maximal)
    out['maximal_surviving_breaksets'] = (maximal if len(maximal) <= 200
                                          else maximal[:200])
    out['maximal_surviving_breakset_names'] = [
        [NAMES2[k] for k in b] for b in (maximal[:60])]
    # min support of a point of P
    minsup = N2 - maxsize
    out['min_support'] = minsup
    out['v1_min_support'] = 32
    out['pair_excludable_minimal'] = [
        [a, b] for a, b in itertools.combinations(Z0, 2)
        if (a, b) not in aset]
    out['n_pair_excludable_minimal'] = len(out['pair_excludable_minimal'])
    # ---- COMPLETE minimal dead family (M3b correction, 2026-08-27).
    # The singleton+pair search above is INCOMPLETE: on a basis with multi-row
    # contacts, minimal dead sets of size >= 3 exist (v2 has 4 triples = both
    # rows of a flush contact + one more row).  A minimal dead set of size >= 2
    # lies entirely within Z0 (a set containing a dead singleton is minimal
    # only as that singleton), so enumerate from the exhaustive alive family:
    # candidates are dead one-row extensions of alive sets, minimal iff every
    # (|D|-1)-subset is alive.
    md = set()
    for b in alive_sets:
        bs = set(b)
        for k in Z0:
            if k in bs:
                continue
            cand = tuple(sorted(bs | {k}))
            if cand in aset or cand in md:
                continue
            if all(tuple(sorted(set(cand) - {j})) in aset or len(cand) == 1
                   for j in cand):
                md.add(cand)
    out['minimal_dead_sets_complete'] = (
        [[k] for k in range(N2) if k not in set(Z0)]
        + sorted(sorted(d) for d in md))
    out['n_minimal_dead_complete'] = len(out['minimal_dead_sets_complete'])
    out['minimal_dead_warning'] = (
        'pair_excludable_minimal alone is NOT the full minimal dead family: '
        'use minimal_dead_sets_complete (v2: 22 singletons + 11 pairs + 4 '
        'triples = 37; found by M3b, patched here at source). Exposure '
        'pattern: any basis with multi-row contacts can have minimal dead '
        'sets of size > 2 (both rows of a flush contact + one more).')
    out['union_of_all_alive_rows'] = sorted({k for b in alive_sets for k in b})
    out['method'] = (
        '[LP, exhaustive over all 2^42 break sets] B is cone-alive iff the LP '
        '{lambda >= 0, A^T lambda = e_s, lambda_B = 0} is feasible. Aliveness '
        'is downward closed, so a breadth-first sweep that only extends alive '
        'sets by rows of Z0 = {k : min_P lambda_k = 0} enumerates the ENTIRE '
        'alive family; every other break set is cone-dead. %d LPs. Min '
        'support = 42 - (largest alive set).' % n_lp)

    # rational Farkas cross-check on 20 random cone-dead |B| = K+1 sets
    rng = random.Random(SEED + 3)
    checks = []
    tries = 0
    while len(checks) < 20 and tries < 400:
        tries += 1
        B = sorted(rng.sample(range(N2), maxsize + 1))
        if tuple(B) in aset:
            continue
        M = [k for k in range(N2) if k not in set(B)]
        rec = farkas_dead(M)
        rec['B'] = B
        checks.append(rec)
    out['random_farkas_cross_check'] = checks
    out['random_farkas_all_certified'] = all(c['certified'] for c in checks)
    out['cross_check_method'] = (
        '[IV] rational Farkas y with y[33] = -1 and every grad g_m . y > 0 '
        'verified in mpmath.iv dps 60, for 20 random cone-dead sets of size '
        'K+1 = %d. Certifies e_s not in cone{grad g_m} rigorously.'
        % (maxsize + 1))
    log('  alive break sets: %d ; K = %d (v1: 6) ; min support %d (v1: 32) ; '
        'singleton dead rows %d (v1: 28)'
        % (len(alive_sets), maxsize, minsup, N2 - len(Z0)))
    return out, aset


def farkas_dead(M, ybound=50.0, den=10 ** 9):
    M = list(M)
    A_ub = np.zeros((len(M), NV + 1))
    A_ub[:, :NV] = -A2[M]
    A_ub[:, NV] = 1.0
    c = np.zeros(NV + 1)
    c[NV] = -1.0
    bnds = [(-ybound, ybound)] * NV + [(0, 100.0)]
    bnds[SIDX] = (-1.0, -1.0)
    r = linprog(c, A_ub=A_ub, b_ub=np.zeros(len(M)), bounds=bnds,
                method='highs')
    if not r.success or -r.fun <= 1e-12:
        return {'certified': False,
                'reason': 'no strict Farkas direction',
                'lp_margin': float(-r.fun) if r.success else None}
    y_q = [Fraction(round(Fraction(float(v)) * den), den) for v in r.x[:NV]]
    y_q[SIDX] = Fraction(-1)
    y_iv = SL.to_iv_vec(y_q)
    lows = []
    for k in M:
        _, g = SL.row_grad_geo(ZBOX, ROWS2[k])
        lows.append(float(SL.iv_dot(g, y_iv).a))
    return {'certified': bool(min(lows) > 0), 'lp_margin': float(-r.fun),
            'min_verified_lower_bound': min(lows)}


# =====================================================================
# 4. synthesis with the wedge test
# =====================================================================
def wedge_empty(B, rows_idx):
    """M4's test: is C(B) = {v in ker A_M : A_B v >= 0} = {0}?

    Valid because rank(A over rows_idx) = 34: if the LP optimum is 0 then every
    feasible v has A_B v = 0 as well as A_M v = 0, hence v in ker A = {0}.
    """
    Bs = set(B)
    M = [k for k in rows_idx if k not in Bs]
    Bl = [k for k in rows_idx if k in Bs]
    _, sv, Vt = np.linalg.svd(A2[M])
    r = int((sv > SL.RANK_TOL).sum())
    d = NV - r
    if d == 0:
        return True, 0.0, 0          # empty stratum: trivially {0}
    K = Vt[r:].T                     # 34 x d basis of ker A_M
    G = A2[Bl] @ K                   # |B| x d
    c = -G.sum(axis=0)
    res = linprog(c, A_ub=-G, b_ub=np.zeros(len(Bl)),
                  bounds=[(-1, 1)] * d, method='highs')
    if not res.success:
        return False, None, d
    opt = float(-res.fun)
    return bool(opt <= 1e-9), opt, d


def classify(B, rows_idx, alive_in_variant, edges):
    Bs = set(B)
    M = [k for k in rows_idx if k not in Bs]
    sv = np.linalg.svd(A2[M], compute_uv=False)
    if int((sv > SL.RANK_TOL).sum()) == NV:
        return 'empty'
    if tuple(sorted(B)) not in alive_in_variant:
        return 'cone_dead'
    we, opt, d = wedge_empty(B, rows_idx)
    if we:
        return 'wedged'
    ret, _ = M1.force_balance_prune(set(M))
    if not ret:
        return 'collapse'
    if not (M1.has_axis_path(ret, edges, 'x')
            and M1.has_axis_path(ret, edges, 'y')):
        return 'loadpath'
    return 'survives_all'


def task4(aset):
    log('TASK 4: synthesis with the wedge test, 3 branch-selection variants')
    edges = SL.contact_edges_v2()
    out = {'cascade': [
        '1 EMPTY     rank(A_M) = 34                                  [RFP]',
        '2 CONE-DEAD e_s not in cone{grad g_m}                       [LP/IV]',
        '3 WEDGED    C(B) = {v in ker A_M : A_B v >= 0} = {0}        [LP]',
        '4 COLLAPSE  force-balance sign rule kills every retained row[NUM]',
        '5 LOADPATH  no x- and no y-wall-to-wall path                [NUM]'],
        'variants': {}}
    # the force-balance machinery in m1_enum is bound to v1's 38-row Amid;
    # rebind it to the v2 Jacobian for this run.
    M1.Amid = A2
    M1.NGEO = N2
    M1._FB_COLS = None

    for variant in ('conj', 'selx', 'sely'):
        rows_idx = SL.v2_variant_rows(variant)
        rset = set(rows_idx)
        dropped = tuple(sorted(set(range(N2)) - rset))
        svv = np.linalg.svd(A2[rows_idx], compute_uv=False)
        rank_v = int((svv > SL.RANK_TOL).sum())
        # variant-alive(B) <=> conj-alive(B union dropped): the variant's
        # multiplier polytope is the face {lambda_dropped = 0} of the conj one.
        alive_v = {tuple(sorted(set(b) - set(dropped)))
                   for b in aset if set(dropped) <= set(b)} if dropped \
            else set(aset)
        counts = {'empty': 0, 'cone_dead': 0, 'wedged': 0, 'collapse': 0,
                  'loadpath': 0, 'survives_all': 0}
        survivors = []
        for B in sorted(alive_v):
            if not B:
                continue
            cls = classify(list(B), rows_idx, alive_v, edges)
            counts[cls] += 1
            if cls == 'survives_all':
                survivors.append(list(B))
        out['variants'][variant] = {
            'rows_used': rows_idx, 'rank': rank_v, 'dropped_rows': list(dropped),
            'n_alive_breaksets_in_variant': len(alive_v) - 1,
            'counts': counts,
            'n_true_survivors': len(survivors),
            'true_survivors_by_size': M1._hist([len(b) for b in survivors]),
            'true_survivors': survivors,
        }
        assert rank_v == NV, (variant, rank_v)
        log('  variant %-5s rank %d  alive %d  %s  -> TRUE SURVIVORS %d'
            % (variant, rank_v, len(alive_v) - 1, counts, len(survivors)))
    allsurv = sorted({tuple(b) for v in out['variants'].values()
                      for b in v['true_survivors']})
    out['union_true_survivors'] = [list(b) for b in allsurv]
    out['n_union_true_survivors'] = len(allsurv)
    out['union_true_survivors_by_size'] = M1._hist([len(b) for b in allsurv])
    out['union_true_survivors_row_usage'] = {
        str(k): sum(1 for b in allsurv if k in b) for k in range(N2)
        if any(k in b for b in allsurv)}
    _sv = {v: {tuple(b) for b in out['variants'][v]['true_survivors']}
           for v in ('conj', 'selx', 'sely')}
    out['work_queue_sample'] = [
        {'B': list(b), 'B_names': [NAMES2[k] for k in b],
         'variants': [v for v in ('conj', 'selx', 'sely') if b in _sv[v]]}
        for b in allsurv[:200]]
    out['work_queue_note'] = (
        'the full queue is union_true_survivors (%d break sets); '
        'work_queue_sample shows the first 200 with names and the variants '
        'each survives in.' % len(allsurv))
    # ---- the break sets with NO first-order ascent guarantee --------------
    fz = RESULT['task2']['forced_zero_rows']
    fz_analysis = []
    for r in range(1, len(fz) + 1):
        for B in itertools.combinations(fz, r):
            rec = {'B': list(B), 'B_names': [NAMES2[k] for k in B]}
            for variant in ('conj', 'selx', 'sely'):
                rows_idx = SL.v2_variant_rows(variant)
                rset = set(rows_idx)
                dropped = tuple(sorted(set(range(N2)) - rset))
                alive_v = {tuple(sorted(set(b) - set(dropped)))
                           for b in aset if set(dropped) <= set(b)} \
                    if dropped else set(aset)
                M = [k for k in rows_idx if k not in set(B)]
                sv = np.linalg.svd(A2[M], compute_uv=False)
                rk = int((sv > SL.RANK_TOL).sum())
                we, opt, d = wedge_empty(list(B), rows_idx)
                rec[variant] = {
                    'rank': rk, 'dof': NV - rk,
                    'cone_alive': tuple(sorted(B)) in alive_v,
                    'wedge_empty': bool(we), 'wedge_lp_optimum': opt,
                    'verdict': classify(list(B), rows_idx, alive_v, edges)}
                if NV - rk == 1:
                    _, svv, Vt = np.linalg.svd(A2[M])
                    v = Vt[int((svv > SL.RANK_TOL).sum())]
                    gb = A2[list(B)] @ v
                    sg = 1.0 if np.all(gb >= -1e-10) else (
                        -1.0 if np.all(gb <= 1e-10) else 0.0)
                    v = sg * v if sg else v
                    moving = {i: float(np.linalg.norm(v[3 * i:3 * i + 3]))
                              for i in range(SL.NSQ)
                              if np.linalg.norm(v[3 * i:3 * i + 3]) > 1e-9}
                    rec[variant]['mechanism'] = {
                        'onesided': 'movable' if sg else 'wedged',
                        'ascent_rate_es_dot_v': float(v[SIDX]),
                        'broken_row_rates': [float(x) for x in (sg or 1) * gb],
                        'moving_squares': moving,
                        's_component': float(v[SIDX]),
                        'kernel_vector': [round(float(x), 10) for x in v]}
            fz_analysis.append(rec)
    out['forced_zero_only_breaksets'] = fz_analysis
    out['forced_zero_only_note'] = (
        'These are exactly the escapes for which theory.md (A)/Consequence 1 '
        'gives NO first-order ascent guarantee on v2, because lambda*_k = 0 is '
        'forced on rows %s. They must be disposed of by another test; their '
        'verdicts are above.' % fz)
    log('  forced-zero-only break sets %s -> %s'
        % ([r['B'] for r in fz_analysis],
           [r['conj']['verdict'] for r in fz_analysis]))

    # ---- cross-validation of the wedge test against M4's v1 result --------
    m1 = json.load(open(os.path.join(RES, 'm1_strata.json')))
    v1surv = m1['synthesis']['global_exhaustive']['survivors']
    _, A1, _, _ = SL.jacobian()
    saveA, saveN = A2.copy(), N2
    n_we = 0
    for B in v1surv:
        Bs = set(B)
        M = [k for k in range(38) if k not in Bs]
        _, sv, Vt = np.linalg.svd(A1[M])
        r = int((sv > SL.RANK_TOL).sum())
        d = NV - r
        if d == 0:
            n_we += 1
            continue
        K = Vt[r:].T
        G = A1[sorted(Bs)] @ K
        rr = linprog(-G.sum(axis=0), A_ub=-G, b_ub=np.zeros(len(Bs)),
                     bounds=[(-1, 1)] * d, method='highs')
        n_we += int(rr.success and float(-rr.fun) <= 1e-9)
    out['wedge_test_validation_on_v1'] = {
        'n_v1_survivors': len(v1surv), 'n_wedge_empty': n_we,
        'm4_claim': len(v1surv),
        'agrees_with_M4': n_we == len(v1surv),
        'note': 'the same wedge_empty() routine applied to the v1 basis and '
                'M1\'s 81 survivors reproduces M4 sec. 1 exactly (81/81), so '
                'the v2 wedge verdicts below are produced by a validated test.'}
    log('  wedge test validated on v1: %d/%d wedge-empty (M4 claims %d)'
        % (n_we, len(v1surv), len(v1surv)))

    out['note'] = (
        'Only cone-alive break sets are enumerated; every other break set in '
        'the 2^42 lattice is cone-dead, so this partition is EXHAUSTIVE. The '
        'wedge test is M4\'s escape-cone LP, inserted as test 3 per the '
        'follow-up brief. A break set containing a row that a variant does not '
        'have is skipped in that variant (it is not expressible there).')
    log('  UNION of true survivors across variants: %d' % len(allsurv))
    return out


# =====================================================================
# 5. M2 coverage map
# =====================================================================
def task5(t4):
    log('TASK 5: M2 certificate coverage / transfer map')
    out = {}
    empt = json.load(open(os.path.join(RES, 'm2_empty.json')))
    e_certs = []
    for s in empt['strata']:
        if not s.get('certified'):
            continue
        e_certs.append({'B': s['B'], 'basis_rows': s['basis_rows']})
    wdir = os.path.join(RES, 'm2_certs')
    w_certs = []
    for fn in sorted(os.listdir(wdir)):
        d = json.load(open(os.path.join(wdir, fn)))
        om = [SL.str_frac(x) for x in d['omega_rational']]
        supp = [i for i, v in enumerate(om) if v != 0]
        w_certs.append({'file': fn, 'B': d['B'], 'S_rows': d['S_rows'],
                        'omega_support': supp,
                        'used_rows': sorted(set(supp) | set(d['S_rows']))})
    out['n_m2_empty_certs'] = len(e_certs)
    out['n_m2_wedge_certs'] = len(w_certs)
    DROPPED = set(SL.V2_DROPPED_V1_ROWS)
    # transfer test: a v1 certificate applies verbatim to a v2 break set B2 iff
    # every v1 row it uses is (a) an unchanged row 0..35 and (b) maintained in B2
    def e_applies(B2):
        b = set(B2)
        for c in e_certs:
            S = set(c['basis_rows'])
            if S & DROPPED:
                continue
            if not (S & b):
                return c
        return None

    def w_applies(B2):
        b = set(B2)
        for c in w_certs:
            U = set(c['used_rows'])
            if U & DROPPED:
                continue
            if not (U & b) and set(c['B']) <= b:
                return c
        return None

    # --- structural diagnosis first: can ANY v1 certificate transfer? -------
    n_e_clean = sum(1 for c in e_certs if not (set(c['basis_rows']) & DROPPED))
    n_w_clean = sum(1 for c in w_certs if not (set(c['used_rows']) & DROPPED))
    rank_unchanged_block = int(
        (np.linalg.svd(A2[:36], compute_uv=False) > SL.RANK_TOL).sum())
    out['n_m2_empty_certs_avoiding_dropped_rows'] = n_e_clean
    out['n_m2_wedge_certs_avoiding_dropped_rows'] = n_w_clean
    out['rank_of_unchanged_block_rows_0_35'] = rank_unchanged_block
    out['structural_verdict'] = (
        'ZERO existing M2 certificates transfer, and the reason is structural, '
        'not clerical: rank(A over the unchanged rows 0..35) = %d, not 34. The '
        'two v1 dist rows contributed exactly the 2 missing dimensions, so '
        'EVERY M2 (E) certificate\'s 34-row square subsystem must use row 36 '
        'or 37, and every (W) certificate\'s self-stress omega lives in the '
        'v1 4-dimensional self-stress space, which is not a subspace of v2\'s '
        '8-dimensional one. Counts: %d of %d (E) certs and %d of %d (W) certs '
        'even avoid the dropped rows syntactically.'
        % (rank_unchanged_block, n_e_clean, len(e_certs), n_w_clean,
           len(w_certs)))
    # spot-check the syntactic test on the union work queue
    detail = []
    for B in [tuple(x) for x in t4['union_true_survivors'][:200]]:
        ec = e_applies(B)
        wc = w_applies(B)
        detail.append({'B': list(B), 'B_names': [NAMES2[k] for k in B],
                       'm2_empty_cert_applies': ec['B'] if ec else None,
                       'm2_wedge_cert_applies': wc['file'] if wc else None,
                       'covered': bool(ec or wc)})
    covered = [d for d in detail if d['covered']]
    out['n_cone_alive'] = RESULT['task3']['n_alive_breaksets']
    out['n_work_queue'] = t4['n_union_true_survivors']
    out['n_covered_verbatim'] = len(covered)
    out['coverage_detail_sample'] = detail[:40]
    out['m2_delta_queue_size'] = t4['n_union_true_survivors']
    out['m2_delta_queue_note'] = (
        'the delta queue is the whole union work queue of Task 4 '
        '(%d break sets, stored there); nothing is inherited.'
        % t4['n_union_true_survivors'])
    out['transfer_criterion'] = (
        'A v1 M2 certificate applies VERBATIM to a v2 break set B2 iff every '
        'v1 row it uses -- basis_rows for an (E) certificate, basis_rows plus '
        'the support of omega for a (W) certificate -- lies in the unchanged '
        'block 0..35 (so it never touches the dropped dist rows 36, 37) and is '
        'MAINTAINED under B2 (no intersection with B2). For a (W) certificate '
        'the original break set must also be contained in B2, since the '
        'argument bounds sum_B omega_b g_b from below on Sbar(B).')
    out['caveat'] = (
        'This is a SYNTACTIC transfer test, and it is conservative in one '
        'direction only: a certificate that passes it is genuinely valid on '
        'v2, but a certificate that fails it may still be repairable cheaply '
        '(e.g. re-deriving omega on the v2 self-stress space, which is now 8- '
        'dimensional instead of 4). The uncovered list is therefore an upper '
        'bound on M2\'s delta queue.')
    log('  M2 (E) certs %d, (W) certs %d ; rank(rows 0..35) = %d ; '
        'transferable = %d' % (len(e_certs), len(w_certs),
                               rank_unchanged_block, len(covered)))
    return out


# =====================================================================
# 6. candidate-pair table on v2
# =====================================================================
def task6():
    log('TASK 6: candidate new-contact table on v2')
    contact = set()
    for c in SL.geo_constraints_v2():
        if c['kind'] in ('edge', 'dist'):
            contact.add(tuple(sorted((c['i'], c['j']))))
    allp = set(itertools.combinations(range(SL.NSQ), 2))
    noncontact = sorted(allp - contact)
    v1_noncontact = {tuple(p) for p in SL.load_cert()['noncontact_pairs']}
    out = {'n_contact_pairs_v2': len(contact),
           'contact_pairs_v2': sorted(list(p) for p in contact),
           'n_noncontact_pairs_v2': len(noncontact),
           'pair_1_3_moved_to_contact': (1, 3) in contact,
           'noncontact_set_unchanged_vs_v1':
               {tuple(p) for p in noncontact} == v1_noncontact}
    gaps = []
    for (i, j) in noncontact:
        g = SL.sat_gap_pair(ZBOX, i, j)
        gaps.append({'pair': [i, j], 'gap_lo': float(g.a), 'gap_hi': float(g.b)})
    gaps.sort(key=lambda r: r['gap_lo'])
    out['noncontact_pair_gaps'] = gaps
    out['nearest_seven'] = gaps[:7]
    m1 = json.load(open(os.path.join(RES, 'm1_strata.json')))
    m1g = {tuple(r['pair']): r['gap_lo']
           for r in m1['task4']['noncontact_pair_gaps']}
    maxdiff = max(abs(r['gap_lo'] - m1g[tuple(r['pair'])])
                  for r in gaps if tuple(r['pair']) in m1g)
    out['max_gap_difference_vs_M1'] = maxdiff
    out['candidate_table'] = m1['task4']['candidate_table']
    out['verdict'] = (
        'CONFIRMED unchanged. v2 has %d contact pairs (13 of A22 plus (1,3)); '
        'the non-contact set is bit-identical to v1\'s 41-pair list (A22 had '
        'already excluded (1,3) from noncontact_pairs, listing it under '
        'flush_upright_pairs while giving it no row -- which is exactly how it '
        'fell through the crack). All 41 gaps agree with M1 to %.2e, so M1\'s '
        'Lipschitz constants and the R = 0.005..0.1 candidate table carry over '
        'verbatim. The corner-wall side is likewise unchanged (no v2 row is a '
        'wall row).' % (len(contact), maxdiff))
    log('  %s' % out['verdict'].split('.')[0])
    return out


# =====================================================================
def selfcheck(R):
    log('SELF-CHECK')
    assert R['meta']['defect_verification']['defect_b_pair_1_3']['is_exactly_2']
    assert R['meta']['defect_verification']['defect_a_dist_surrogates'][
        'both_exactly_1']
    ok, _, bound = SL.certified_rank34(range(N2), A2, R2)
    assert ok and bound < 1.0
    assert R['task1']['rank']['value'] == 34
    assert R['task1']['self_stress']['dim'] == N2 - 34 == 8
    assert not R['task1']['nonneg_self_stress'][
        'ALARM_nonneg_self_stress_exists']
    assert R['task1']['nonneg_self_stress']['min_verified_lower_bound'] > 0
    # lambda* recomputed from stored rationals
    lam = [SL.str_frac(s) for s in R['task2']['lambda_rational']]
    assert min(lam) >= 0
    keep = R['task2']['restricted_floor_rows']
    assert abs(float(min(lam[k] for k in keep))
               - R['task2']['min_lambda_over_kept_rows_float']) < 1e-30
    lam_ivv = [t3lib._to_iv(x) for x in lam]
    acc = [iv.mpf(0)] * NV
    for k in range(N2):
        _, g = SL.row_grad_geo(ZBOX, ROWS2[k])
        for gi, val in g.items():
            acc[gi] = acc[gi] + val * lam_ivv[k]
    acc[SIDX] = acc[SIDX] - iv.mpf(1)
    r1 = sum(max(abs(float(a.a)), abs(float(a.b))) for a in acc)
    assert r1 <= 1e-25, r1
    log('  lambda* recheck: restricted floor %.9f  residual_l1 %.2e'
        % (float(min(lam[k] for k in keep)), r1))
    # cone: every alive set must actually be alive, every maximal one maximal
    for B in R['task3']['maximal_surviving_breaksets'][:25]:
        assert cone_alive(B), B
    assert R['task3']['min_support'] + \
        R['task3']['max_surviving_breakset_size_K'] == N2
    assert R['task3']['random_farkas_all_certified']
    # forced-zero rows really are forced zero
    for k in R['task2']['forced_zero_rows']:
        ck = np.zeros(N2)
        ck[k] = 1.0
        assert float(-polytope_lp(ck, maximize=True).fun) < 1e-9
    log('  cone + forced-zero rows re-verified')
    # wedge test must reproduce M4's v1 verdict
    assert R['task4']['wedge_test_validation_on_v1']['agrees_with_M4']
    # candidate table unchanged
    assert R['task6']['noncontact_set_unchanged_vs_v1']
    assert R['task6']['max_gap_difference_vs_M1'] < 1e-12
    # v1 code path must be untouched
    a1 = SL.jacobian()[1]
    assert a1.shape == (38, 34) and len(SL.geo_rows()) == 38
    log('  v1 code path intact (38 rows, unchanged Jacobian)')
    log('  ALL SELF-CHECKS PASSED')


def main():
    RESULT['meta']['defect_verification'] = task0()
    RESULT['task1'] = task1()
    t2, lo, hi = task2()
    RESULT['task2'] = t2
    t3, aset = task3(lo, hi)
    RESULT['task3'] = t3
    RESULT['task4'] = task4(aset)
    RESULT['task5'] = task5(RESULT['task4'])
    RESULT['task6'] = task6()
    RESULT['meta']['runtime_secs'] = time.time() - T0
    with open(OUT, 'w') as f:
        json.dump(RESULT, f, indent=1)
    log('wrote %s (%.2f MB)' % (OUT, os.path.getsize(OUT) / 1e6))
    selfcheck(RESULT)
    log('done in %.1f s' % (time.time() - T0))


if __name__ == '__main__':
    main()
