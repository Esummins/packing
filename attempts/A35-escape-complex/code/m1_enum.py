"""m1_enum.py -- A35 measurement M1: stratum enumerator at Trump's jam.

Tasks (see attempts/A35-escape-complex/BRIEF.md and notes/theory.md):
 1. certify rank(A)=34, self-stress dim 4, NO nonnegative self-stress
    (strict Farkas witness), and lambda* with a uniform floor.
 2. codim-graded stratum classification (exhaustive k<=3, sampled k=4..10).
 3. K=6 cone truncation: exact min-support of the multiplier polytope by
    vertex enumeration of its 4-dim cap.
 4. candidate new contacts with an honest travel bound.
 5. load-path cuts with force-balance refinement (T1-b).

Writes results/m1_strata.json and (via m1_report.md, written separately) the
narrative.  Every recorded quantity carries a "method" note.

Rigour tags: [IV] mpmath.iv dps 60 (rigorous); [RFP] rigorous float64
preconditioned nonsingularity; [EXACT] rational arithmetic; [NUM] float64
with reported spectral gap (NOT rigorous).
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
import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
os.makedirs(RES, exist_ok=True)
OUT = os.path.join(RES, 'm1_strata.json')

SEED = 20260827
NGEO = SL.NGEO
NV = SL.NV
SIDX = SL.S_IDX

T0 = time.time()


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


# =====================================================================
# shared objects
# =====================================================================
A_iv, Amid, Arad, VALS = SL.jacobian()
NAMES = SL.row_names()
ROWS = SL.geo_rows()
ZBOX = SL.point_box()
ZHAT = SL.z_hat()
ES = SL.es_vector()

RESULT = {'meta': {
    'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'source_cert': 'attempts/A22-local-rigidity/results/krawczyk_cert.json',
    'rows': '38 geometric rows = cert constraints 0..37 (20 wall, 16 edge, 2 dist)',
    'layout': 'z[3i]=cx_i, z[3i+1]=cy_i, z[3i+2]=theta_i, z[33]=s; NV=34',
    'iv_dps': SL.IV_DPS,
    'seed': SEED,
    'row_names': NAMES,
    'max_abs_row_value_at_zhat': max(
        max(abs(float(v.a)), abs(float(v.b))) for v in VALS),
    'max_jacobian_entry_radius_iv': float(Arad.max()),
    'rigour_tags': {
        'IV': 'mpmath.iv at dps 60 over the degenerate point box at z-hat',
        'RFP': 'rigorous float64: ||I - Y A||_inf < 1 with explicit rounding '
               'bound + IV entry radii (Rump); certifies NONSINGULARITY only',
        'EXACT': 'exact rational arithmetic',
        'NUM': 'float64 SVD, spectral gap reported; rank-DEFICIENCY claims '
               'are of this kind and are NOT rigorous',
    }}}


# =====================================================================
# TASK 1
# =====================================================================
def task1():
    log('TASK 1: rank / self-stress / Farkas / lambda*')
    out = {}

    # ---- 1a rank + self-stress dimension -----------------------------------
    ok, basis, bound = SL.certified_rank34(range(NGEO), Amid, Arad)
    sv = np.linalg.svd(Amid, compute_uv=False)
    out['rank'] = {
        'value': 34,
        'certified_lower_bound': 34 if ok else None,
        'upper_bound_reason': 'A has 34 columns',
        'witness_basis_rows': list(basis) if ok else None,
        'rump_bound': bound,
        'singular_values_float': [float(x) for x in sv],
        'method': '[RFP] nonsingular 34x34 minor (rows above) certified by '
                  '||I - Y*A||_inf = %.3e < 1 with rounding + IV-radius bound; '
                  'rank <= 34 is trivial (34 columns). FULLY RIGOROUS.' % bound,
    }
    assert ok, 'rank-34 certification failed'

    # self-stress space = left kernel of A, dim = 38 - rank = 4 (exact given rank)
    U, s_all, Vt = np.linalg.svd(Amid)
    N = U[:, 34:38]                      # 38 x 4, orthonormal, A^T N ~ 0
    resid_N = float(np.abs(Amid.T @ N).max())
    supp_norm = np.linalg.norm(N, axis=1)
    support = [k for k in range(NGEO) if supp_norm[k] > 1e-8]
    nonsupport = [k for k in range(NGEO) if supp_norm[k] <= 1e-8]

    # certify membership in the support: row k in supp <=> rank(A_{-k}) = 34
    supp_cert = {}
    for k in support:
        M = [j for j in range(NGEO) if j != k]
        okk, bk, bd = SL.certified_rank34(M, Amid, Arad)
        supp_cert[k] = {'certified': bool(okk), 'rump_bound': bd}
    out['self_stress'] = {
        'dim': 4,
        'method_dim': '[RFP+EXACT] dim ker(A^T) = 38 - rank(A) = 38 - 34 = 4, '
                      'rank certified above. FULLY RIGOROUS.',
        'basis_38x4_float': [[float(x) for x in N[k]] for k in range(NGEO)],
        'max_residual_AtN': resid_N,
        'support_rows': support,
        'support_size': len(support),
        'nonsupport_rows': nonsupport,
        'row_norms_in_kernel': [float(x) for x in supp_norm],
        'support_certified': {str(k): v for k, v in supp_cert.items()},
        'method_support': '[RFP] row k lies in the support of some self-stress '
                          'iff rank(A_{-k}) = 34; each listed support row has a '
                          'certified nonsingular 34-minor among the other 37 '
                          'rows. The %d NON-support rows are [NUM] only '
                          '(rank(A_{-k}) = 33 is a rank-deficiency claim).'
                          % len(nonsupport),
    }

    # ---- 1b strict Farkas witness (no nonnegative self-stress; pointedness) --
    # find y with grad g_k . y >= t > 0 for ALL 38 rows.
    nlp = NV + 1
    A_ub = np.zeros((NGEO, nlp))
    A_ub[:, :NV] = -Amid
    A_ub[:, NV] = 1.0
    c = np.zeros(nlp)
    c[NV] = -1.0
    bnds = [(-1.0, 1.0)] * NV + [(0.0, 10.0)]
    r = linprog(c, A_ub=A_ub, b_ub=np.zeros(NGEO), bounds=bnds, method='highs')
    assert r.success, r.message
    y_f = r.x[:NV]
    t_lp = float(-r.fun)
    # rationalise and verify in mpmath.iv over the degenerate point box
    DEN = 10 ** 9
    y_q = [Fraction(round(Fraction(float(v)) * DEN), DEN) for v in y_f]
    y_iv = SL.to_iv_vec(y_q)
    lows = []
    for k in range(NGEO):
        _, g = SL.row_grad_geo(ZBOX, ROWS[k])
        d = SL.iv_dot(g, y_iv)
        lows.append(float(d.a))
    min_low = min(lows)
    out['farkas_no_nonneg_selfstress'] = {
        'exists': bool(min_low > 0),
        'y_rational': [SL.frac_str(v) for v in y_q],
        'y_denominator': DEN,
        'lp_margin': t_lp,
        'verified_lower_bounds': lows,
        'min_verified_lower_bound': min_low,
        'consequences': [
            'no nonzero nonnegative self-stress on the 38 rows '
            '(Gordan: sum_k y_k grad g_k = 0 with y >= 0, y != 0 would give '
            '0 = sum_k y_k (grad g_k . y) > 0)',
            'cone{grad g_k} is POINTED (all 38 generators lie in the open '
            'halfspace {w . y > 0})',
            'the multiplier polytope {lambda >= 0 : A^T lambda = e_s} is BOUNDED',
        ],
        'method': '[IV] LP-found direction rationalised at denominator 1e9; '
                  'all 38 products grad g_k . y verified > 0 in mpmath.iv at '
                  'dps 60 over the degenerate point box at z-hat. '
                  'min_k lower bound = %.6f. FULLY RIGOROUS.' % min_low,
    }
    assert min_low > 0

    # ---- 1c Chebyshev lambda* with uniform floor ---------------------------
    nl = NGEO + 1
    A_eq = np.zeros((NV, nl))
    A_eq[:, :NGEO] = Amid.T
    b_eq = ES.copy()
    A_ub2 = np.zeros((NGEO, nl))
    for k in range(NGEO):
        A_ub2[k, k] = -1.0
        A_ub2[k, NGEO] = 1.0
    c2 = np.zeros(nl)
    c2[NGEO] = -1.0
    r2 = linprog(c2, A_ub=A_ub2, b_ub=np.zeros(NGEO), A_eq=A_eq, b_eq=b_eq,
                 bounds=[(0, None)] * NGEO + [(0, None)], method='highs')
    assert r2.success, r2.message
    lam_lp = r2.x[:NGEO]
    floor_lp = float(-r2.fun)
    log('  Chebyshev LP floor = %.9f  sum = %.6f' % (floor_lp, lam_lp.sum()))

    # exact-ish correction on the 34-row invertible subsystem S (A22's)
    Sset = SL.load_cert()['S']
    assert len(Sset) == 34 and max(Sset) < NGEO
    okS, bS = SL.certify_nonsingular(Amid[Sset], Arad[Sset])
    assert okS, 'A_S not certified nonsingular'
    Sc = [k for k in range(NGEO) if k not in set(Sset)]

    DPS = 90
    Amp = SL.jacobian_mp(dps=DPS)
    old = mp.dps
    mp.dps = DPS
    DEN_F = 10 ** 20
    lam_free = {k: Fraction(round(Fraction(float(lam_lp[k])) * DEN_F), DEN_F)
                for k in Sc}
    rhs = mp.zeros(NV, 1)
    rhs[SIDX, 0] = mp.mpf(1)
    for k in Sc:
        fk = mp.mpf(lam_free[k].numerator) / mp.mpf(lam_free[k].denominator)
        for j in range(NV):
            rhs[j, 0] -= Amp[k, j] * fk
    MS = mp.zeros(NV, NV)
    for r_, k in enumerate(Sset):
        for j in range(NV):
            MS[j, r_] = Amp[k, j]          # (A_S)^T
    solS = mp.lu_solve(MS, rhs)
    DEN_L = 10 ** 45
    lam_q = [None] * NGEO
    for r_, k in enumerate(Sset):
        lam_q[k] = Fraction(int(mp.floor(solS[r_, 0] * DEN_L + mp.mpf('0.5'))),
                            DEN_L)
    for k in Sc:
        lam_q[k] = lam_free[k]
    mp.dps = old

    # residual ||A^T lambda* - e_s||_1 verified in mpmath.iv
    lam_ivv = [t3lib._to_iv(x) for x in lam_q]
    acc = [iv.mpf(0)] * NV
    for k in range(NGEO):
        _, g = SL.row_grad_geo(ZBOX, ROWS[k])
        for gi, val in g.items():
            acc[gi] = acc[gi] + val * lam_ivv[k]
    acc[SIDX] = acc[SIDX] - iv.mpf(1)
    res_l1_hi = 0.0
    for j in range(NV):
        res_l1_hi += max(abs(float(acc[j].a)), abs(float(acc[j].b)))
    lam_min = min(lam_q)
    lam_sum = sum(lam_q)
    kmin = [k for k in range(NGEO) if lam_q[k] == lam_min]
    out['lambda_star'] = {
        'lambda_rational': [SL.frac_str(v) for v in lam_q],
        'denominator_S_rows': DEN_L,
        'denominator_free_rows': DEN_F,
        'S_rows': Sset,
        'free_rows': Sc,
        'residual_l1_upper_bound': res_l1_hi,
        'residual_target': 1e-25,
        'residual_ok': bool(res_l1_hi <= 1e-25),
        'min_lambda_exact': SL.frac_str(lam_min),
        'min_lambda_float': float(lam_min),
        'argmin_rows': kmin,
        'sum_lambda_float': float(lam_sum),
        'all_positive': bool(lam_min > 0),
        'chebyshev_lp_floor': floor_lp,
        'method': '[EXACT+IV] Chebyshev LP (max t s.t. lambda >= t, '
                  'A^T lambda = e_s) in float64; the 4 rows outside A22\'s '
                  'invertible subsystem S frozen at rationalised LP values; '
                  'the 34 S-rows re-solved at mpmath dps 90 and rationalised '
                  'at denominator 1e45.  ||A^T lambda* - e_s||_1 then bounded '
                  'in mpmath.iv (dps 60) at z-hat: %.3e.' % res_l1_hi,
    }
    log('  lambda* floor = %.9f  sum = %.6f  residual_l1 <= %.2e'
        % (float(lam_min), float(lam_sum), res_l1_hi))
    return out, np.array([float(v) for v in lam_q]), N


# =====================================================================
# TASK 2
# =====================================================================
def analyse_stratum(B, lam_f, want_kernel):
    Bs = set(B)
    M = [k for k in range(NGEO) if k not in Bs]
    sub = Amid[M]
    _, sv, Vt = np.linalg.svd(sub)
    r = int((sv > SL.RANK_TOL).sum())
    dof = NV - r
    rec = {'B': list(B), 'rank': r, 'dof': dof,
           'sv_min_kept': float(sv[r - 1]) if r > 0 else None,
           'sv_max_dropped': float(sv[r]) if r < len(sv) else 0.0}
    if dof == 0:
        rec['class'] = 'empty'
    else:
        rec['class'] = 'mechanism'
    if dof == 1:
        v = Vt[r]
        gb = Amid[list(B)] @ v
        pos = bool(np.all(gb >= -1e-10))
        neg = bool(np.all(-gb >= -1e-10))
        if pos or neg:
            sgn = 1.0 if pos else -1.0
            rec['onesided'] = 'movable'
            rec['movable_sign'] = int(sgn)
            rec['ascent_rate_es_dot_v'] = float(sgn * v[SIDX])
            rec['broken_row_rates'] = [float(sgn * x) for x in gb]
            rec['lambda_identity_check'] = float(
                np.dot(lam_f[list(B)], sgn * gb) - sgn * v[SIDX])
        else:
            rec['onesided'] = 'wedged'
            rec['broken_row_rates'] = [float(x) for x in gb]
    if want_kernel and dof > 0:
        rec['kernel'] = [[round(float(x), 12) for x in Vt[r + i]]
                         for i in range(dof)]
        rec['kernel_note'] = '[NUM] float64 SVD nullspace, orthonormal rows'
    return rec


def task2(lam_f):
    log('TASK 2: codim-graded classification')
    rng = random.Random(SEED)
    out = {'method': '[NUM] dof = 34 - rank(A_M) from float64 SVD with '
                     'threshold 1e-9; the spectral gap is recorded per '
                     'stratum (sv_min_kept vs sv_max_dropped).  dof = 0 '
                     '("empty") entries are additionally [RFP]-CERTIFIED for '
                     'k <= 3 by a nonsingular 34-row minor.  dof > 0 claims '
                     'are rank-deficiency claims and are [NUM] only.',
           'tables': {}, 'k1': [], 'k2': [], 'samples': {}}

    tables = {}
    cert_stats = {}
    for k in (1, 2, 3):
        recs = []
        t0 = time.time()
        for B in itertools.combinations(range(NGEO), k):
            recs.append(analyse_stratum(B, lam_f, want_kernel=(k <= 2)))
        tab = {}
        for rc in recs:
            key = 'empty' if rc['dof'] == 0 else (
                'wedged' if rc.get('onesided') == 'wedged'
                else 'dof%d' % rc['dof'])
            tab[key] = tab.get(key, 0) + 1
        tables['k=%d' % k] = tab
        # certify the empty ones
        nc = 0
        for rc in recs:
            if rc['dof'] == 0:
                M = [j for j in range(NGEO) if j not in set(rc['B'])]
                ok, bas, bd = SL.certified_rank34(M, Amid, Arad)
                rc['empty_certified'] = bool(ok)
                rc['empty_witness_basis'] = list(bas) if ok else None
                nc += int(ok)
        cert_stats['k=%d' % k] = {'n_empty': tab.get('empty', 0),
                                  'n_empty_certified': nc}
        if k == 1:
            out['k1'] = recs
        elif k == 2:
            out['k2'] = recs
        else:
            out['k3_summary_only'] = True
            out['k3_empty_sets'] = [rc['B'] for rc in recs if rc['dof'] == 0]
            out['k3_wedged_sets'] = [rc['B'] for rc in recs
                                     if rc.get('onesided') == 'wedged']
        log('  k=%d  n=%d  %s  (%.1fs)' % (k, len(recs), tab, time.time() - t0))

    NS = 2000
    for k in range(4, 11):
        seen = set()
        recs = []
        t0 = time.time()
        while len(recs) < NS:
            B = tuple(sorted(rng.sample(range(NGEO), k)))
            if B in seen:
                continue
            seen.add(B)
            recs.append(analyse_stratum(B, lam_f, want_kernel=False))
        tab = {}
        for rc in recs:
            key = 'empty' if rc['dof'] == 0 else (
                'wedged' if rc.get('onesided') == 'wedged'
                else 'dof%d' % rc['dof'])
            tab[key] = tab.get(key, 0) + 1
        tables['k=%d (sampled %d of %d)' % (k, NS, _binom(NGEO, k))] = tab
        out['samples']['k=%d' % k] = {
            'n_sampled': NS, 'n_total': _binom(NGEO, k), 'counts': tab,
            'dof_histogram': _hist([rc['dof'] for rc in recs]),
            'n_wedged': sum(1 for rc in recs if rc.get('onesided') == 'wedged'),
            'ascent_rates_dof1': [rc['ascent_rate_es_dot_v'] for rc in recs
                                  if rc.get('onesided') == 'movable'],
        }
        log('  k=%d  sampled %d  %s  (%.1fs)' % (k, NS, tab, time.time() - t0))

    out['tables'] = tables
    out['empty_certification'] = cert_stats
    # dof-1 ascent-rate summary at k=1,2
    for nm, recs in (('k1', out['k1']), ('k2', out['k2'])):
        rates = [rc['ascent_rate_es_dot_v'] for rc in recs
                 if rc.get('onesided') == 'movable']
        ident = [abs(rc['lambda_identity_check']) for rc in recs
                 if rc.get('onesided') == 'movable']
        out[nm + '_dof1_summary'] = {
            'n_movable': len(rates),
            'n_wedged': sum(1 for rc in recs if rc.get('onesided') == 'wedged'),
            'min_ascent_rate': min(rates) if rates else None,
            'max_ascent_rate': max(rates) if rates else None,
            'max_lambda_identity_residual': max(ident) if ident else None,
            'identity_note': 'e_s.v = sum_{b in B} lambda*_b (grad g_b . v) '
                             'must hold for every retained-kernel v; the '
                             'residual is a consistency check on lambda*.',
        }
    return out


def _binom(n, k):
    from math import comb
    return comb(n, k)


def _hist(vals):
    h = {}
    for v in vals:
        h[str(v)] = h.get(str(v), 0) + 1
    return dict(sorted(h.items(), key=lambda kv: int(kv[0])))


# =====================================================================
# TASK 3
# =====================================================================
def task3(lam_f, N):
    log('TASK 3: K=6 cone truncation (multiplier-polytope vertex enumeration)')
    out = {}
    # polytope P = {lambda >= 0 : A^T lambda = e_s} = {lam_f + N u : u in R^4}
    # cap C = {u in R^4 : lam_f + N u >= 0}.  Vertices of C: 4 tight rows.
    idx = np.array(list(itertools.combinations(range(NGEO), 4)))
    log('  4-subsets: %d' % len(idx))
    Nb = N[idx]                                   # (m,4,4)
    rhs = -lam_f[idx]                             # (m,4)
    det = np.linalg.det(Nb)
    good = np.abs(det) > 1e-10
    Ng = Nb[good]
    rg = rhs[good]
    u = np.linalg.solve(Ng, rg[..., None])[..., 0]      # (m',4)
    lam = lam_f[None, :] + u @ N.T                      # (m',38)
    TOL = 1e-9
    feas = lam.min(axis=1) > -TOL
    V = lam[feas]
    Vu = u[feas]
    Vidx = idx[good][feas]
    log('  candidate vertices (with repeats): %d' % len(V))
    # dedupe
    keyset = {}
    for i in range(len(V)):
        key = tuple(np.round(Vu[i], 9))
        if key not in keyset:
            keyset[key] = i
    uniq = sorted(keyset.values())
    Uv = Vu[uniq]

    # --- independent vertex enumeration: qhull halfspace intersection ------
    # P in u-coordinates: {u : -N u - lambda* <= 0}; u = 0 is strictly interior
    # because min_k lambda*_k = 0.0476 > 0.
    from scipy.spatial import HalfspaceIntersection
    hs = np.hstack([-N, -lam_f[:, None]])
    hsi = HalfspaceIntersection(hs, np.zeros(4))
    Uq = np.unique(np.round(hsi.intersections, 9), axis=0)
    # --- independent vertex enumeration: random-objective LPs --------------
    rng0 = np.random.default_rng(SEED)
    Ulp = set()
    Aub_u = -N
    bub_u = lam_f.copy()
    for _ in range(4000):
        cdir = rng0.normal(size=4)
        rr = linprog(cdir, A_ub=Aub_u, b_ub=bub_u,
                     bounds=[(-100, 100)] * 4, method='highs')
        if rr.success:
            Ulp.add(tuple(np.round(rr.x, 8)))
    def _match(a, b, tol=1e-6):
        a = np.atleast_2d(np.asarray(a, dtype=float))
        b = np.atleast_2d(np.asarray(b, dtype=float))
        if len(a) != len(b):
            return False
        d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
        return bool(np.all(d.min(axis=1) < tol) and np.all(d.min(axis=0) < tol))
    Ulp_a = np.array(sorted(Ulp)) if Ulp else np.zeros((0, 4))
    agree = _match(Uv, Uq) and _match(Uq, Ulp_a)
    log('  vertices: combinatorial %d, qhull %d, random-LP %d, agree=%s'
        % (len(Uv), len(Uq), len(Ulp), agree))
    out['vertex_enumeration_cross_check'] = {
        'n_combinatorial_C38_4': int(len(Uv)),
        'n_qhull_halfspace_intersection': int(len(Uq)),
        'n_random_objective_LPs': int(len(Ulp)),
        'all_three_agree': bool(agree),
        'note': 'three independent enumerations of the 4-dim multiplier '
                'polytope; the C(38,4) sweep can in principle miss a '
                'degenerate vertex whose every 4-subset is singular, so it is '
                'cross-checked against qhull and 4000 random-objective LPs.'}
    Vv = np.clip(lam_f[None, :] + Uq @ N.T, 0.0, None)
    supports = [frozenset(np.nonzero(Vv[i] > TOL)[0].tolist())
                for i in range(len(Vv))]
    sizes = [len(s) for s in supports]
    minsup = min(sizes)
    out['n_vertices'] = len(Vv)
    out['support_size_histogram'] = _hist(sizes)
    out['min_support'] = minsup
    out['max_breakset_preserving_cone'] = NGEO - minsup
    # maximal surviving (NON-excludable) break sets = maximal Z(v) = complements
    zsets = sorted({frozenset(range(NGEO)) - s for s in supports},
                   key=lambda z: (-len(z), sorted(z)))
    maximal = []
    for z in zsets:
        if not any(z < w for w in zsets):
            maximal.append(sorted(z))
    out['n_maximal_surviving_breaksets'] = len(maximal)
    out['maximal_surviving_breaksets'] = (maximal if len(maximal) <= 200
                                          else maximal[:200])
    out['maximal_surviving_truncated'] = len(maximal) > 200
    out['max_surviving_size'] = max(len(z) for z in maximal)
    # minimal EXCLUDABLE break sets: B excludable  <=>  B not subset of any Z(v)
    zlist = [set(z) for z in zsets]
    always_pos = [k for k in range(NGEO)
                  if not any(k in z for z in zlist)]
    out['rows_positive_at_every_vertex'] = always_pos
    out['n_singleton_excludable'] = len(always_pos)
    rest = [k for k in range(NGEO) if k not in set(always_pos)]
    pairs = []
    for a, b in itertools.combinations(rest, 2):
        if not any(a in z and b in z for z in zlist):
            pairs.append([a, b])
    out['n_pair_excludable_minimal'] = len(pairs)
    out['pair_excludable_minimal'] = pairs if len(pairs) <= 200 else pairs[:200]
    # EXACT count, for every k, of break sets that do NOT kill the cone
    surv = set()
    for z in maximal:
        for r in range(len(z) + 1):
            for ss in itertools.combinations(z, r):
                surv.add(ss)
    bysize = {}
    for ss in surv:
        bysize[len(ss)] = bysize.get(len(ss), 0) + 1
    tab = {}
    for k in range(0, 12):
        tot = _binom(NGEO, k)
        ns = bysize.get(k, 0)
        tab['k=%d' % k] = {'n_total': tot, 'n_surviving': ns,
                           'n_excludable': tot - ns,
                           'frac_excludable': (tot - ns) / tot}
    out['exact_excludability_by_k'] = tab
    out['exact_excludability_method'] = (
        '[EXACT combinatorics on the vertex set] a break set B fails to kill '
        'the cone iff B avoids the support of some vertex, i.e. iff B is a '
        'subset of some Z(v). Enumerating all subsets of the %d maximal Z(v) '
        'gives the exact count of surviving break sets at every size. Uses '
        'the retained rows ONLY -- gained contacts are not in the menu.'
        % len(maximal))
    out['surviving_breakset_list'] = sorted(
        [list(s) for s in surv if s], key=lambda s: (len(s), s))
    out['rows_by_family'] = {
        'union_of_all_Z': sorted({k for z in maximal for k in z}),
        'note': 'every surviving break set is drawn from these rows alone; '
                'breaking ANY row outside this list already kills the cone.'}
    out['method_a'] = (
        '[NUM->verified] the multiplier polytope P = {lambda>=0 : A^T lambda '
        '= e_s} is bounded (Task 1b) and its affine hull is lambda* + '
        'ker(A^T), dim 4. All C(38,4) = %d 4-subsets solved for the tight '
        'vertex; feasible ones deduped. Min support of a vertex = min support '
        'over all of P (the minimal-support face contains a vertex). '
        'Vertex arithmetic is float64; the extremal vertices are re-verified '
        'below in mpmath.' % len(idx))

    # re-verify the minimal-support vertices at high precision
    minsup_ix = [i for i in range(len(Vv)) if sizes[i] == minsup]
    ver = []
    Amp = SL.jacobian_mp(dps=60)
    old = mp.dps
    mp.dps = 60
    for i in minsup_ix[:20]:
        sup = sorted(supports[i])
        Z = sorted(set(range(NGEO)) - set(sup))
        # solve A_sup^T mu = e_s in least squares at high precision
        Msys = mp.zeros(NV, len(sup))
        for c_, k in enumerate(sup):
            for j in range(NV):
                Msys[j, c_] = Amp[k, j]
        rhs2 = mp.zeros(NV, 1)
        rhs2[SIDX, 0] = mp.mpf(1)
        # normal equations at dps 60 (Msys is 34 x |sup|, full column rank)
        try:
            MtM = Msys.T * Msys
            sol = mp.lu_solve(MtM, Msys.T * rhs2)
            err = None
        except Exception as exc:                       # pragma: no cover
            sol, err = None, repr(exc)
        if sol is None:
            ver.append({'zero_set': Z, 'status': 'solve_failed', 'error': err})
            continue
        mn = min(sol[j, 0] for j in range(len(sup)))
        rr = Msys * sol - rhs2
        ver.append({'zero_set': Z,
                    'support_size': len(sup),
                    'min_multiplier': float(mn),
                    'residual_inf': float(max(abs(rr[j, 0])
                                              for j in range(NV)))})
    mp.dps = old
    out['minimal_support_vertices_verified'] = ver
    out['n_minimal_support_vertices'] = len(minsup_ix)

    # ---- (b) cross-check: random |B| = 7 sets get a Farkas witness ---------
    rng = random.Random(SEED + 7)
    checks = []
    tried = 0
    while len(checks) < 20 and tried < 200:
        tried += 1
        B = sorted(rng.sample(range(NGEO), 7))
        M = [k for k in range(NGEO) if k not in set(B)]
        rec = farkas_cone_dead(M)
        rec['B'] = B
        checks.append(rec)
    out['random_B7_farkas'] = checks
    out['random_B7_all_certified'] = all(c['certified'] for c in checks)
    out['method_b'] = (
        '[IV] for each |B| = 7 the LP  max t s.t. grad g_m . y >= t (m in M), '
        'e_s . y = y[33] = -1, |y| <= 50  is solved; y is rationalised at '
        'denominator 1e9 and every grad g_m . y is verified > 0 in mpmath.iv '
        'at dps 60.  Then lambda >= 0 with A_M^T lambda = e_s would give '
        '0 > e_s.y = sum lambda_m (grad g_m . y) >= 0.  FULLY RIGOROUS per set.')
    return out


def farkas_cone_dead(M, ybound=50.0, den=10 ** 9):
    """Certify e_s not in cone{grad g_m : m in M} by a rational Farkas y."""
    M = list(M)
    n = NV
    A_ub = np.zeros((len(M), n + 1))
    A_ub[:, :n] = -Amid[M]
    A_ub[:, n] = 1.0
    c = np.zeros(n + 1)
    c[n] = -1.0
    bnds = [(-ybound, ybound)] * n + [(0, 100.0)]
    bnds[SIDX] = (-1.0, -1.0)
    r = linprog(c, A_ub=A_ub, b_ub=np.zeros(len(M)), bounds=bnds, method='highs')
    if not r.success:
        return {'certified': False, 'reason': 'LP failed: %s' % r.message}
    y_f = r.x[:n]
    t = float(-r.fun)
    if t <= 1e-12:
        return {'certified': False, 'reason': 'no strict Farkas direction',
                'lp_margin': t}
    y_q = [Fraction(round(Fraction(float(v)) * den), den) for v in y_f]
    y_q[SIDX] = Fraction(-1)
    y_iv = SL.to_iv_vec(y_q)
    lows = []
    for k in M:
        _, g = SL.row_grad_geo(ZBOX, ROWS[k])
        lows.append(float(SL.iv_dot(g, y_iv).a))
    mn = min(lows)
    return {'certified': bool(mn > 0), 'lp_margin': t,
            'min_verified_lower_bound': mn,
            'y_rational': [SL.frac_str(v) for v in y_q]}


# =====================================================================
# TASK 4
# =====================================================================
SQRT2 = float(np.sqrt(2.0))
L_CORNER = 3.0 / SQRT2            # corner motion per unit ||dz||_inf
L_PAIR = 2.0 * L_CORNER           # = 3*sqrt(2) ~ 4.2426
L_WALL_LO = L_CORNER              # x=0, y=0
L_WALL_HI = 1.0 + L_CORNER        # x=s, y=s (s moves too)


def task4():
    log('TASK 4: candidate new contacts')
    cert = SL.load_cert()
    noncontact = [tuple(p) for p in cert['noncontact_pairs']]
    have_wall = SL.contact_wall_set()
    out = {'lipschitz_derivation': [
        'corner q_i = c_i + R(theta_i) h,  |h| = sqrt(2)/2 = 1/sqrt(2).',
        '|dq_i| <= |dc_i|_2 + |dtheta_i| * |h| <= sqrt(2) R + R/sqrt(2) '
        '= (3/sqrt2) R ~ 2.12132 R   for ||dz||_inf <= R.',
        'square i as a set moves at most (3/sqrt2) R in Hausdorff distance '
        '(a square is the convex hull of its 4 corners).',
        'the Euclidean separation dist(K_i, K_j) is 1-Lipschitz in the '
        'Hausdorff perturbation of each body, so it changes by at most '
        'L_pair * R with L_pair = 2*(3/sqrt2) = 3*sqrt(2) ~ 4.24264.',
        'the reported pair gap is the SAT max-over-edge-normals value, which '
        'is a LOWER bound on dist and is 0 exactly at contact -- so using it '
        'in the screen is conservative.',
        'wall rows: x=0 / y=0 gap changes by <= (3/sqrt2) R ~ 2.12132 R; '
        'x=s / y=s also carry ds, so <= (1 + 3/sqrt2) R ~ 3.12132 R.',
        'NOTE the brief\'s suggested 2*sqrt(2) R = 2.82843 R sits between the '
        'per-square constant 2.12132 and the pair constant 4.24264; the '
        'larger (conservative) constants are used here.'],
        'L_corner': L_CORNER, 'L_pair': L_PAIR,
        'L_wall_lo': L_WALL_LO, 'L_wall_hi': L_WALL_HI}

    pair_gap = {}
    for (i, j) in noncontact:
        g = SL.sat_gap_pair(ZBOX, i, j)
        pair_gap[(i, j)] = (float(g.a), float(g.b))
    order = sorted(pair_gap, key=lambda p: pair_gap[p][0])
    out['noncontact_pair_gaps'] = [
        {'pair': list(p), 'gap_lo': pair_gap[p][0], 'gap_hi': pair_gap[p][1]}
        for p in order]
    out['noncontact_pair_gaps_method'] = (
        '[IV] SAT separation (max over the 8 edge-normal axes) enclosed in '
        'mpmath.iv at dps 60 over the degenerate point box at z-hat.')

    wall_gap = {}
    for i in range(SL.NSQ):
        for c in range(4):
            for w in SL.WALLS:
                if (i, c, w) in have_wall:
                    continue
                v = SL.wall_gap(ZBOX, i, c, w)
                wall_gap[(i, c, w)] = (float(v.a), float(v.b))
    worder = sorted(wall_gap, key=lambda k: wall_gap[k][0])
    out['noncontact_wall_gaps_top20'] = [
        {'square': k[0], 'corner': k[1], 'wall': k[2],
         'gap_lo': wall_gap[k][0], 'gap_hi': wall_gap[k][1]}
        for k in worder[:20]]
    out['n_noncontact_wall_combos'] = len(wall_gap)

    table = {}
    for R in (0.005, 0.01, 0.02, 0.05, 0.1):
        Rf = Fraction(round(R * 10 ** 6), 10 ** 6)
        box = SL.frac_box(ZHAT, Rf)
        lip_pairs, iv_pairs = [], []
        for p in order:
            if pair_gap[p][0] <= L_PAIR * R:
                lip_pairs.append(list(p))
            g = SL.sat_gap_pair(box, p[0], p[1])
            if float(g.a) <= 0:
                iv_pairs.append(list(p))
        lip_walls, iv_walls = [], []
        for k in worder:
            L = L_WALL_HI if k[2] in ('x=s', 'y=s') else L_WALL_LO
            if wall_gap[k][0] <= L * R:
                lip_walls.append(list(k))
            if len(lip_walls) < 40:      # interval scan only where plausible
                pass
        for k in worder[:60]:
            v = SL.wall_gap(box, k[0], k[1], k[2])
            if float(v.a) <= 0:
                iv_walls.append(list(k))
        comb_p = [p for p in lip_pairs if p in iv_pairs]
        comb_w = [w for w in lip_walls if w in iv_walls]
        table['R=%g' % R] = {
            'lipschitz_screen_pairs': lip_pairs,
            'lipschitz_screen_walls': lip_walls,
            'interval_certified_candidate_pairs': iv_pairs,
            'interval_certified_candidate_walls': iv_walls,
            'candidate_pairs': comb_p,
            'candidate_walls': comb_w,
            'n_lip_pairs': len(lip_pairs), 'n_lip_walls': len(lip_walls),
            'n_iv_pairs': len(iv_pairs), 'n_iv_walls': len(iv_walls),
            'n_candidate_pairs': len(comb_p), 'n_candidate_walls': len(comb_w),
        }
        log('  R=%g: lipschitz pairs %d walls %d | interval pairs %d walls %d'
            % (R, len(lip_pairs), len(lip_walls), len(iv_pairs), len(iv_walls)))
    out['candidate_table'] = table
    out['candidate_definition'] = (
        'BOTH screens are NECESSARY conditions for the pair/row to reach '
        'contact within travel R, so the sound candidate set is their '
        'INTERSECTION ("candidate_pairs" / "candidate_walls"). The Lipschitz '
        'screen is sharper at small R (it uses the exact gap at z-hat); the '
        'interval scan is sharper at large R (it sees the true geometry '
        'rather than a worst-case constant).')
    out['candidate_table_method'] = (
        'lipschitz_screen: gap(z-hat) <= L * R with the constants above '
        '(necessary condition for contact, sound). '
        'interval_certified: the SAT gap / wall gap enclosed by mpmath.iv over '
        'the FULL box(z-hat, R) has lower bound <= 0, i.e. contact is not '
        'excluded on the box. The interval scan is dependency-pessimistic, so '
        'it is a SUPERSET of the true candidates and is also sound; the '
        'Lipschitz screen is the sharper of the two at small R. Wall combos '
        'are interval-scanned only for the 60 smallest gaps (the rest exceed '
        '0.5 and cannot close at R <= 0.1 by the Lipschitz bound).')
    return out


# =====================================================================
# TASK 5
# =====================================================================
def build_axis_graph(retained, edges, axis):
    """networkx graph for one axis. axis in ('x','y')."""
    import networkx as nx
    G = nx.Graph()
    src, snk = ('x=0', 'x=s') if axis == 'x' else ('y=0', 'y=s')
    G.add_node(src)
    G.add_node(snk)
    for e in edges:
        rows = [r for r in e['rows'] if r in retained]
        if not rows:
            continue
        if e['type'] == 'wall':
            if e['wall'] not in (src, snk):
                continue           # orthogonal wall carries no load on this axis
            u, v = e['a'], e['wall']
        else:
            u, v = e['a'], e['b']
        if G.has_edge(u, v):
            G[u][v]['capacity'] += len(rows)
            G[u][v]['rows'] = tuple(sorted(set(G[u][v]['rows']) | set(rows)))
        else:
            G.add_edge(u, v, capacity=len(rows), rows=tuple(sorted(rows)))
    return G, src, snk


FB_TOL = 1e-9

# precomputed sign structure of the coordinate-stationarity columns
_FB_COLS = None


def _fb_cols():
    global _FB_COLS
    if _FB_COLS is None:
        cols = []
        for i in range(SL.NSQ):
            for a, nm in ((0, 'cx'), (1, 'cy'), (2, 'theta')):
                col = 3 * i + a
                pos = frozenset(k for k in range(NGEO) if Amid[k, col] > FB_TOL)
                neg = frozenset(k for k in range(NGEO) if Amid[k, col] < -FB_TOL)
                if pos or neg:
                    cols.append((i, nm, col, pos, neg))
        _FB_COLS = cols
    return _FB_COLS


def force_balance_prune(retained):
    """T1-b force-balance refinement (implemented at z-hat).

    For every square i and every coordinate c in {cx_i, cy_i, theta_i}, the FJ
    stationarity row for that coordinate reads sum_k lambda_k * A[k, c] = 0
    with lambda >= 0 (the objective s touches only z[33]).  If every NONZERO
    coefficient among the retained rows has the same sign, all those
    multipliers vanish -- the rows are load-dead and are removed.  Iterated to
    a fixed point.  Returns (pruned set, list of firings).
    """
    R = set(retained)
    fired = []
    changed = True
    while changed:
        changed = False
        for i, nm, col, pos, neg in _fb_cols():
            ap = pos & R
            an = neg & R
            if ap and not an:
                kill = ap
            elif an and not ap:
                kill = an
            else:
                continue
            fired.append({'square': i, 'coord': nm,
                          'killed_rows': sorted(kill),
                          'min_abs_coeff': float(min(abs(Amid[k, col])
                                                     for k in kill))})
            R -= kill
            changed = True
    return R, fired


def has_axis_path(retained, edges, axis):
    """Union-find connectivity of the two axis walls (fast path for sampling)."""
    src, snk = ('x=0', 'x=s') if axis == 'x' else ('y=0', 'y=s')
    par = {}

    def find(a):
        while par.get(a, a) != a:
            par[a] = par.get(par[a], par[a])
            a = par[a]
        return a

    def uni(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb

    par[src] = src
    par[snk] = snk
    for e in edges:
        if not any(r in retained for r in e['rows']):
            continue
        if e['type'] == 'wall':
            if e['wall'] not in (src, snk):
                continue
            u, v = e['a'], e['wall']
        else:
            u, v = e['a'], e['b']
        par.setdefault(u, u)
        par.setdefault(v, v)
        uni(u, v)
    return find(src) == find(snk)


def min_cut_axis(retained, edges, axis):
    import networkx as nx
    G, src, snk = build_axis_graph(retained, edges, axis)
    if src not in G or snk not in G or not nx.has_path(G, src, snk):
        return 0, [], False
    val, (S, T) = nx.minimum_cut(G, src, snk)
    rows = []
    for u in S:
        for v in G[u]:
            if v in T:
                rows.extend(G[u][v]['rows'])
    return int(val), sorted(set(rows)), True


def joint_cut_milp(retained, edges):
    """min |R| such that removing R cuts every x-path AND every y-path.

    Binary MILP: x_r (row selected), p_v / q_v (side of v in the x- / y-cut).
    For every graph edge (u,v) and every row r of it: x_r >= p_u - p_v and
    x_r >= p_v - p_u (an edge survives while ANY of its rows survives, so a
    cut edge needs ALL its rows removed).
    """
    from scipy.optimize import milp, LinearConstraint, Bounds
    import numpy as _np
    Gx, sx, tx = build_axis_graph(retained, edges, 'x')
    Gy, sy, ty = build_axis_graph(retained, edges, 'y')
    nodes_x = list(Gx.nodes())
    nodes_y = list(Gy.nodes())
    ix = {n: i for i, n in enumerate(nodes_x)}
    iy = {n: i for i, n in enumerate(nodes_y)}
    nr = NGEO
    off_x = nr
    off_y = nr + len(nodes_x)
    n = nr + len(nodes_x) + len(nodes_y)
    rowsA, lb, ub = [], [], []

    def add(coefs, lo, hi):
        v = _np.zeros(n)
        for j, c in coefs:
            v[j] += c
        rowsA.append(v)
        lb.append(lo)
        ub.append(hi)

    for (G, off, imap, s_, t_) in ((Gx, off_x, ix, sx, tx),
                                   (Gy, off_y, iy, sy, ty)):
        add([(off + imap[s_], 1)], 0, 0)
        add([(off + imap[t_], 1)], 1, 1)
        for u, v, d in G.edges(data=True):
            for r in d['rows']:
                add([(r, 1), (off + imap[u], -1), (off + imap[v], 1)], 0, _np.inf)
                add([(r, 1), (off + imap[u], 1), (off + imap[v], -1)], 0, _np.inf)
    A = _np.array(rowsA)
    con = LinearConstraint(A, _np.array(lb), _np.array(ub))
    c = _np.zeros(n)
    c[:nr] = 1.0
    res = milp(c=c, constraints=[con], integrality=_np.ones(n),
               bounds=Bounds(0, 1))
    if not res.success:
        return None, None
    sel = sorted(int(i) for i in range(nr) if res.x[i] > 0.5)
    return len(sel), sel


def axis_cut_milp(retained, edges, axis):
    from scipy.optimize import milp, LinearConstraint, Bounds
    import numpy as _np
    G, s_, t_ = build_axis_graph(retained, edges, axis)
    nodes = list(G.nodes())
    imap = {nd: i for i, nd in enumerate(nodes)}
    nr = NGEO
    n = nr + len(nodes)
    rowsA, lb, ub = [], [], []

    def add(coefs, lo, hi):
        v = _np.zeros(n)
        for j, c in coefs:
            v[j] += c
        rowsA.append(v)
        lb.append(lo)
        ub.append(hi)
    add([(nr + imap[s_], 1)], 0, 0)
    add([(nr + imap[t_], 1)], 1, 1)
    for u, v, d in G.edges(data=True):
        for r in d['rows']:
            add([(r, 1), (nr + imap[u], -1), (nr + imap[v], 1)], 0, _np.inf)
            add([(r, 1), (nr + imap[u], 1), (nr + imap[v], -1)], 0, _np.inf)
    A = _np.array(rowsA)
    res = milp(c=_np.concatenate([_np.ones(nr), _np.zeros(len(nodes))]),
               constraints=[LinearConstraint(A, _np.array(lb), _np.array(ub))],
               integrality=_np.ones(n), bounds=Bounds(0, 1))
    if not res.success:
        return None, None
    sel = sorted(int(i) for i in range(nr) if res.x[i] > 0.5)
    return len(sel), sel


def task5():
    log('TASK 5: load-path cuts with force-balance refinement')
    import networkx as nx
    edges = SL.contact_edges()
    allrows = set(range(NGEO))
    pruned, fired = force_balance_prune(allrows)
    out = {
        'contact_edges': edges,
        'force_balance_rule': (
            'For square i and coordinate c in {cx_i, cy_i, theta_i}: FJ '
            'stationarity gives sum_k lambda_k A[k,c] = 0 with lambda >= 0 '
            '(grad s = e_s touches only z[33], so this holds for BOTH the '
            'lambda_0 > 0 and lambda_0 = 0 branches). If all nonzero '
            'coefficients share a sign, those lambda_k are 0 and the rows are '
            'load-dead. Iterated to a fixed point. This SUBSUMES theory.md '
            'T1-b\'s corner-square rule (two orthogonal wall normals +x, +y).'),
        'force_balance_firings_at_zhat': fired,
        'rows_killed_at_zhat': sorted(allrows - pruned),
        'rows_alive_at_zhat': sorted(pruned),
        'not_proved': [
            'the sign test is evaluated at z-hat; the min |coefficient| that '
            'fires is recorded per firing so a neighbourhood statement can be '
            'made, but no interval extension over a region is done here (M3).',
            'no torque/rotation propagation beyond the single-coordinate sign '
            'rule; no use of the magnitudes (a genuine static solve).',
            'square-square edges are kept in BOTH axis graphs regardless of '
            'their normal direction (theory.md only removes orthogonal WALL '
            'edges). This is the conservative direction: it keeps more paths, '
            'so the reported cuts are valid but possibly not minimal.',
            'gained (new) contacts are not in the graph; a stratum could '
            'reconnect a cut axis by acquiring a contact (Task 4 bounds which).',
        ],
    }

    for tag, ret in (('unpruned', allrows), ('pruned', pruned)):
        d = {}
        for ax in ('x', 'y'):
            v_mf, rows_mf, conn = min_cut_axis(ret, edges, ax)
            v_ip, rows_ip = axis_cut_milp(ret, edges, ax)
            d[ax] = {'connected': conn, 'maxflow_mincut': v_mf,
                     'maxflow_cut_rows': rows_mf,
                     'milp_mincut': v_ip, 'milp_cut_rows': rows_ip}
        jv, jrows = joint_cut_milp(ret, edges)
        d['joint'] = {'size': jv, 'rows': jrows}
        out[tag] = d
        log('  %-9s x-cut %s %s | y-cut %s %s | joint %s %s'
            % (tag, d['x']['milp_mincut'], d['x']['milp_cut_rows'],
               d['y']['milp_mincut'], d['y']['milp_cut_rows'], jv, jrows))

    # per-k connectivity fractions
    rng = random.Random(SEED + 5)
    perk = {}
    for k in range(1, 13):
        tot = _binom(NGEO, k)
        if tot <= 2000:
            samples = list(itertools.combinations(range(NGEO), k))
            mode = 'exhaustive'
        else:
            seen = set()
            samples = []
            while len(samples) < 2000:
                B = tuple(sorted(rng.sample(range(NGEO), k)))
                if B in seen:
                    continue
                seen.add(B)
                samples.append(B)
            mode = 'sampled 2000'
        nx_path = ny_path = nboth = nneither = 0
        rx_path = ry_path = rneither = 0
        ncollapse = npartial = 0
        for B in samples:
            raw = allrows - set(B)
            ret, _ = force_balance_prune(raw)
            if not ret:
                ncollapse += 1
            elif len(ret) < len(raw):
                npartial += 1
            px = has_axis_path(ret, edges, 'x')
            py = has_axis_path(ret, edges, 'y')
            nx_path += px
            ny_path += py
            nboth += (px and py)
            nneither += (not px and not py)
            qx = has_axis_path(raw, edges, 'x')
            qy = has_axis_path(raw, edges, 'y')
            rx_path += qx
            ry_path += qy
            rneither += (not qx and not qy)
        m = len(samples)
        perk['k=%d' % k] = {
            'mode': mode, 'n': m, 'n_total': tot,
            'frac_x_path': nx_path / m, 'frac_y_path': ny_path / m,
            'frac_both': nboth / m,
            'frac_dead_by_loadpath': nneither / m,
            'frac_x_path_no_prune': rx_path / m,
            'frac_y_path_no_prune': ry_path / m,
            'frac_dead_by_loadpath_no_prune': rneither / m,
            'frac_total_multiplier_collapse': ncollapse / m,
            'frac_partial_prune': npartial / m}
        log('  k=%2d %-14s x %.3f y %.3f dead %.3f | no-prune x %.3f y %.3f '
            'dead %.3f | collapse %.3f'
            % (k, mode, nx_path / m, ny_path / m, nneither / m,
               rx_path / m, ry_path / m, rneither / m, ncollapse / m))
    out['per_k_loadpath'] = perk
    out['per_k_note'] = (
        'frac_dead_by_loadpath = fraction of strata whose retained rows (after '
        'force-balance pruning) have NEITHER an x-wall-to-wall path NOR a '
        'y-wall-to-wall path. By T1-b those strata are FJ-free for '
        'lambda_0 > 0; the lambda_0 = 0 branch is empty at z-hat by Task 1b. '
        '"no_prune" repeats the count with the RAW L6 graph (theory.md T1-b '
        'as written, no force-balance refinement) so the two effects can be '
        'separated. frac_total_multiplier_collapse = the sign rule cascades '
        'until NO retained row can carry a multiplier: those strata are '
        'FJ-free outright, lambda_0 = 0 branch included, with no graph '
        'argument needed. All at z-hat gradients.')
    out['theory_md_cross_check'] = {
        'claimed_y_cut': [22, 23, 25], 'claimed_y_cut_size': 3,
        'claimed_x_cut_size': 5, 'claimed_joint_size': 8,
        'claimed_y_cut_is_valid': not has_axis_path(
            allrows - {22, 23, 25}, edges, 'y'),
        'found_x_cut_size': out['pruned']['x']['milp_mincut'],
        'found_y_cut_size': out['pruned']['y']['milp_mincut'],
        'found_joint_size': out['pruned']['joint']['size'],
        'note': 'theory.md records x = 5, y = 3 ({22,23,25}), joint = 8 from '
                'the float recon. {22,23,25} IS a valid y-cut but it is not '
                'minimal: the MILP (and max-flow) minimum is smaller. The '
                'recon numbers appear to have cut the wall node directly '
                'rather than searching all cuts.'}
    return out


# =====================================================================
# SYNTHESIS: which kill-test disposes of which stratum
# =====================================================================
def synthesis(R):
    log('SYNTHESIS: joint kill-test coverage')
    edges = SL.contact_edges()
    allrows = set(range(NGEO))
    alive = {tuple(s) for s in R['task3']['surviving_breakset_list']}
    rng = random.Random(SEED + 99)
    tab = {}
    for k in range(1, 9):
        tot = _binom(NGEO, k)
        if tot <= 10000:
            samples = list(itertools.combinations(range(NGEO), k))
            mode = 'exhaustive'
        else:
            seen, samples = set(), []
            while len(samples) < 4000:
                B = tuple(sorted(rng.sample(range(NGEO), k)))
                if B in seen:
                    continue
                seen.add(B)
                samples.append(B)
            mode = 'sampled 4000'
        c = {'empty': 0, 'cone_dead': 0, 'collapse': 0, 'loadpath': 0,
             'survives_all': 0}
        surv_examples = []
        for B in samples:
            M = [j for j in range(NGEO) if j not in set(B)]
            sv = np.linalg.svd(Amid[M], compute_uv=False)
            if int((sv > SL.RANK_TOL).sum()) == NV:
                c['empty'] += 1
                continue
            if B not in alive:
                c['cone_dead'] += 1
                continue
            ret, _ = force_balance_prune(allrows - set(B))
            if not ret:
                c['collapse'] += 1
                continue
            if not (has_axis_path(ret, edges, 'x')
                    and has_axis_path(ret, edges, 'y')):
                c['loadpath'] += 1
                continue
            c['survives_all'] += 1
            if len(surv_examples) < 40:
                surv_examples.append(list(B))
        m = len(samples)
        tab['k=%d' % k] = {'mode': mode, 'n': m, 'n_total': tot,
                           'counts': c,
                           'frac_survives_all': c['survives_all'] / m,
                           'survivor_examples': surv_examples}
        log('  k=%d %-14s %s  survivors %d/%d' % (k, mode, c,
                                                  c['survives_all'], m))
    # ---- EXHAUSTIVE over ALL 2^38 break sets ------------------------------
    # only cone-alive break sets can survive, and those are exactly the
    # subsets of the 16 maximal Z(v) -- a finite list.  Test every one.
    globl = {'empty': [], 'collapse': [], 'loadpath': [], 'survives_all': []}
    for s in sorted(alive, key=lambda s: (len(s), s)):
        if not s:
            continue
        M = [j for j in range(NGEO) if j not in set(s)]
        sv = np.linalg.svd(Amid[M], compute_uv=False)
        if int((sv > SL.RANK_TOL).sum()) == NV:
            okc, _, _ = SL.certified_rank34(M, Amid, Arad)
            globl['empty'].append(list(s))
            globl.setdefault('empty_certified', 0)
            globl['empty_certified'] += int(okc)
            continue
        ret, _ = force_balance_prune(allrows - set(s))
        if not ret:
            globl['collapse'].append(list(s))
            continue
        if not (has_axis_path(ret, edges, 'x')
                and has_axis_path(ret, edges, 'y')):
            globl['loadpath'].append(list(s))
            continue
        globl['survives_all'].append(list(s))
    log('  GLOBAL over all 2^38 break sets: %d cone-alive; of those %d empty, '
        '%d collapse, %d load-path, %d SURVIVE EVERYTHING'
        % (len(alive) - 1, len(globl['empty']), len(globl['collapse']),
           len(globl['loadpath']), len(globl['survives_all'])))
    return {'per_k': tab,
            'global_exhaustive': {
                'n_cone_alive_breaksets': len(alive) - 1,
                'n_empty': len(globl['empty']),
                'n_empty_RFP_certified': globl.get('empty_certified', 0),
                'n_total_collapse': len(globl['collapse']),
                'n_loadpath_dead': len(globl['loadpath']),
                'n_survives_all': len(globl['survives_all']),
                'survivors': globl['survives_all'],
                'empty_and_cone_alive': globl['empty'],
                'note': 'EXHAUSTIVE over all 2^38 - 1 nonempty break sets: '
                        'only the %d subsets of the 16 maximal Z(v) can be '
                        'cone-alive, so the four tests can be applied to every '
                        'break set in finite time. The listed survivors are '
                        'the COMPLETE set of strata that need a real (V)/(C)/'
                        '(F) certificate at the z-hat linearization with '
                        'retained rows only.' % (len(alive) - 1)},
            'order': [
        '1. EMPTY  (rank(A_M) = 34, dof 0): Krawczyk isolation, [RFP]-certified',
        '2. CONE-DEAD (T1-a): e_s not in cone{grad g_m, m in M}, exact from '
        'the vertex enumeration of Task 3 -- RETAINED rows only',
        '3. TOTAL COLLAPSE (T1-b refined): the force-balance sign rule '
        'cascades to lambda = 0 on every retained row; kills lambda_0 = 0 too',
        '4. LOAD-PATH (T1-b as written): no x- and no y-wall-to-wall path '
        'after pruning; kills lambda_0 > 0',
        'survives_all: none of the four fires -- these need a real (V)/(C)/(F) '
        'certificate from M2/M3.'],
        'caveat': 'tests 2-4 use the RETAINED rows at z-hat only; GAINED '
                  'contacts (Task 4) can re-feed the cone and reconnect the '
                  'load paths, and the gradients drift along the stratum. '
                  'M3 must extend them over a region.'}


# =====================================================================
# SELF-CHECK
# =====================================================================
def selfcheck(R):
    log('SELF-CHECK')
    # rank / self-stress
    ok, basis, bound = SL.certified_rank34(range(NGEO), Amid, Arad)
    assert ok and bound < 1.0
    assert R['task1']['rank']['value'] == 34
    assert R['task1']['self_stress']['dim'] == 4
    assert len(R['task1']['self_stress']['support_rows']) == \
        R['task1']['self_stress']['support_size']
    # k=1 empty count must equal the self-stress support size
    n_empty_k1 = R['task2']['tables']['k=1'].get('empty', 0)
    assert n_empty_k1 == R['task1']['self_stress']['support_size'], \
        (n_empty_k1, R['task1']['self_stress']['support_size'])
    # Farkas
    assert R['task1']['farkas_no_nonneg_selfstress']['min_verified_lower_bound'] > 0
    # lambda* floor + residual, recomputed from the stored rationals
    lam = [SL.str_frac(s) for s in R['task1']['lambda_star']['lambda_rational']]
    assert min(lam) > 0
    assert abs(float(min(lam)) - R['task1']['lambda_star']['min_lambda_float']) < 1e-30
    lam_ivv = [t3lib._to_iv(x) for x in lam]
    acc = [iv.mpf(0)] * NV
    for k in range(NGEO):
        _, g = SL.row_grad_geo(ZBOX, ROWS[k])
        for gi, val in g.items():
            acc[gi] = acc[gi] + val * lam_ivv[k]
    acc[SIDX] = acc[SIDX] - iv.mpf(1)
    r1 = sum(max(abs(float(a.a)), abs(float(a.b))) for a in acc)
    assert r1 <= 1e-25, r1
    log('  lambda* recheck: floor %.9f  residual_l1 %.2e'
        % (float(min(lam)), r1))
    # min support / K
    assert R['task3']['min_support'] == 32, R['task3']['min_support']
    assert R['task3']['min_support'] + R['task3']['max_breakset_preserving_cone'] == NGEO
    assert R['task3']['max_surviving_size'] == R['task3']['max_breakset_preserving_cone'] == 6
    assert R['task3']['vertex_enumeration_cross_check']['all_three_agree']
    ex = R['task3']['exact_excludability_by_k']
    assert ex['k=7']['frac_excludable'] == 1.0
    assert ex['k=6']['n_surviving'] == 4
    assert R['task3']['random_B7_all_certified']
    # every surviving break set must avoid the 28 always-positive rows
    ap = set(R['task3']['rows_positive_at_every_vertex'])
    for z in R['task3']['maximal_surviving_breaksets']:
        assert not (set(z) & ap), z
    assert len(ap) == 28
    # cuts
    edges = SL.contact_edges()
    allrows = set(range(NGEO))
    pruned, _ = force_balance_prune(allrows)
    for tag, ret in (('unpruned', allrows), ('pruned', pruned)):
        for ax in ('x', 'y'):
            v, rows, conn = min_cut_axis(ret, edges, ax)
            assert v == R['task5'][tag][ax]['maxflow_mincut'], (tag, ax, v)
            # a cut must actually disconnect
            import networkx as nx
            G2, s_, t_ = build_axis_graph(ret - set(R['task5'][tag][ax]['milp_cut_rows']),
                                          edges, ax)
            assert not (s_ in G2 and t_ in G2 and nx.has_path(G2, s_, t_)), (tag, ax)
    jrows = R['task5']['pruned']['joint']['rows']
    import networkx as nx
    for ax in ('x', 'y'):
        G2, s_, t_ = build_axis_graph(pruned - set(jrows), edges, ax)
        assert not (s_ in G2 and t_ in G2 and nx.has_path(G2, s_, t_))
    log('  cuts verified to disconnect both axes')
    # travel bound sanity
    assert R['task4']['L_pair'] > R['task4']['L_corner'] > 2.0
    # every k=1 stratum must be disposed of (empty or cone-dead)
    s1 = R['synthesis']['per_k']['k=1']['counts']
    assert s1['survives_all'] == 0 and s1['empty'] + s1['cone_dead'] == 38, s1
    log('  k=1 fully disposed: %d empty + %d cone-dead = 38'
        % (s1['empty'], s1['cone_dead']))
    log('  ALL SELF-CHECKS PASSED')
    return True


# =====================================================================
def main():
    t1, lam_f, N = task1()
    RESULT['task1'] = t1
    RESULT['task2'] = task2(lam_f)
    RESULT['task3'] = task3(lam_f, N)
    RESULT['task4'] = task4()
    RESULT['task5'] = task5()
    RESULT['synthesis'] = synthesis(RESULT)
    RESULT['meta']['basis_certifications'] = {
        'n_distinct_bases': len(SL.basis_cache()),
        'n_certified': sum(1 for v in SL.basis_cache().values() if v[0]),
        'max_rump_bound_among_certified': max(
            [v[1] for v in SL.basis_cache().values() if v[0]] or [0.0]),
    }
    RESULT['meta']['runtime_secs'] = time.time() - T0
    with open(OUT, 'w') as f:
        json.dump(RESULT, f, indent=1)
    log('wrote %s (%.1f MB)' % (OUT, os.path.getsize(OUT) / 1e6))
    selfcheck(RESULT)
    log('done in %.1f s' % (time.time() - T0))


if __name__ == '__main__':
    main()
