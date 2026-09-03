"""A87 follow-up: FJ-POLISHED k0 critical-point search.

A87/J3 found that 13 of the 14 lowest k0 "optima" of A85's cp85_k0_search.json
admit NO feasible Fritz-John multipliers: e_s is outside the cone of the active
constraint gradients, so Gordan gives a STRICT feasible descent direction and
the landing is not a critical point at all.

This driver re-runs every k0 landing (262 optima + rotated-Trump seeds) through

  (1) exact contact classification at a tolerance ladder 1e-6 .. 1e-3
      (t3lib rows: containment + one consistent SAT selection per contact pair);
  (2) an active-set FEASIBLE-DESCENT flow: NNLS on the unit-normalised cone
      system  A^T lam = e_s, lam >= 0.  Its residual r = A^T lam* - e_s
      satisfies  A r >= 0  and  e_s . r = -||r||^2 < 0  (NNLS KKT), i.e. r IS
      the Gordan descent direction: every active constraint is non-decreasing
      and the side strictly decreases.  Backtracking line search on the true
      (non-penalised) constraints; the tolerance is widened on a stall;
  (3) a Newton polish of the ACTIVE-set FJ system at the landing point of the
      flow, accepted only if it keeps the packing feasible and does not raise
      the side;
  (4) the FJ verdict at the polished point: lam >= 0, not all zero (the
      lam0 = 1 branch is the cone test; the lam0 = 0 branch is tested too),
      plus the k0 hypothesis (no square both axis-aligned and on a corner slot).

No LP solver is used: cone membership is decided by NNLS (a projection).
Engine: t3lib.py (A30 verbatim, already copied into A87) + pilot87.py helpers.

Usage:  python fjpolish87.py {probe|run|report}
BLAS pinned before numpy import.  Single process.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv
from scipy.optimize import nnls

import t3lib as T
import pilot87 as P
import jobs87 as J

RESULTS = P.RESULTS
S0F = float(P.S0)
S_HAT = 3.877083590022814
TOL_LADDER = (1e-6, 1e-5, 1e-4, 1e-3)
ROT_PHIS = (5e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2)
HALFPI = math.pi / 2.0

CONE_TOL = 1e-7          # NNLS residual on the unit-row-normalised system
FEAS_EPS = 1e-12         # allowed SAT / containment violation
MAXIT = 800              # flow iterations
SEED_SECS = 14.0         # wall-clock cap per seed
RECLASS_EVERY = 12
NEWTON_IT = 25

_SG = np.array([[1., 1.], [1., -1.], [-1., -1.], [-1., 1.]])
_IJ = [(i, j) for i in range(11) for j in range(i + 1, 11)]


# ------------------------------------------------------------ float geometry

def zsplit(z):
    a = np.asarray(z, float)
    return np.stack([a[0:33:3], a[1:33:3]], axis=1), a[2:33:3], a[33]


def corners(c, th):
    ct, st = np.cos(th), np.sin(th)
    u = np.stack([ct, st], axis=1) * 0.5
    v = np.stack([-st, ct], axis=1) * 0.5
    return (c[:, None, :] + _SG[None, :, 0, None] * u[:, None, :]
            + _SG[None, :, 1, None] * v[:, None, :])


def enclosing_side(z):
    c, th, _ = zsplit(z)
    q = corners(c, th).reshape(-1, 2)
    return float(max(q[:, 0].max() - q[:, 0].min(), q[:, 1].max() - q[:, 1].min()))


def pair_gaps(z):
    """Per-pair SAT gap (>=0 disjoint); same convention as t3lib.pair_sep_iv."""
    c, th, _ = zsplit(z)
    q = corners(c, th)
    out = np.empty(len(_IJ))
    for t, (i, j) in enumerate(_IJ):
        best = -np.inf
        for o, p in ((i, j), (j, i)):
            for e in range(4):
                a = th[o] + e * HALFPI
                n = np.array([math.cos(a), math.sin(a)])
                best = max(best, float((q[p] @ n).min() - c[o] @ n - 0.5))
        out[t] = best
    return out


def sat_gap(z):
    return float(pair_gaps(z).min())


def container_slack(z, s):
    c, th, _ = zsplit(z)
    q = corners(c, th)
    return float(min(q[:, :, 0].min(), q[:, :, 1].min(),
                     s - q[:, :, 0].max(), s - q[:, :, 1].max()))


def wall_gaps(z, s):
    c, th, _ = zsplit(z)
    q = corners(c, th)
    return np.concatenate([q[:, :, 0].ravel(), q[:, :, 1].ravel(),
                           (s - q[:, :, 0]).ravel(), (s - q[:, :, 1]).ravel()])


def k0_census(z, s, tol_th=1e-6, tol_c=1e-6):
    """cp85's operational k-count: axis-aligned AND centred on a corner slot."""
    c, th, _ = zsplit(z)
    d = np.abs(np.mod(th + math.pi / 4.0, HALFPI) - math.pi / 4.0)
    aa = d <= tol_th
    slots = np.array([[.5, .5], [s - .5, .5], [.5, s - .5], [s - .5, s - .5]])
    dmin = np.abs(c[:, None, :] - slots[None, :, :]).max(axis=2).min(axis=1)
    return int((aa & (dmin <= tol_c)).sum()), int(aa.sum()), float(dmin.min())


PAD = 1e-9   # keeps the interval evaluation of the wall rows strictly feasible


def canonical(z):
    """Shift the bounding box to PAD and set s = enclosing side + 2*PAD.

    The PAD is the same device pilot87.normalise_config uses: an exactly flush
    corner makes t3lib's interval wall row straddle 0 and test_ab call the
    point infeasible.  PAD = 1e-9 is far below every contact tolerance used.
    """
    c, th, _ = zsplit(z)
    q = corners(c, th).reshape(-1, 2)
    dx, dy = q[:, 0].min() - PAD, q[:, 1].min() - PAD
    out = np.asarray(z, float).copy()
    out[0:33:3] -= dx
    out[1:33:3] -= dy
    out[33] = float(max(q[:, 0].max() - dx, q[:, 1].max() - dy)) + PAD
    return out


# ------------------------------------------------------------- FJ cone tests

def cone_nnls(A):
    """min_{lam>=0} ||A_n^T lam - e_s||.  Returns (residual, lam, r_vector).

    NNLS KKT gives  A_n r >= 0  and  e_s . r = -||r||^2, so r is the Gordan
    descent direction whenever the residual is non-zero.
    """
    m = A.shape[0]
    if m == 0:
        d = np.zeros(T.NV); d[33] = -1.0
        return float('inf'), None, d
    nrm = np.linalg.norm(A, axis=1)
    nrm[nrm == 0] = 1.0
    An = A / nrm[:, None]
    b = np.zeros(T.NV); b[33] = 1.0
    lam, res = nnls(An.T, b)
    r = An.T @ lam - b
    return float(res), (lam / nrm), r


def lam0_zero_test(A):
    """Is there lam >= 0, sum lam = 1, A^T lam = 0?  (the lambda_0 = 0 branch)"""
    m = A.shape[0]
    if m == 0:
        return False, float('inf')
    nrm = np.linalg.norm(A, axis=1)
    nrm[nrm == 0] = 1.0
    An = A / nrm[:, None]
    M = np.vstack([An.T, np.ones((1, m))])
    b = np.zeros(T.NV + 1); b[-1] = 1.0
    _, res = nnls(M, b)
    return bool(res <= 1e-6), float(res)


def classify(z, tol):
    """t3lib active rows at the (degenerate) point z."""
    zf = [Fraction(float(v)).limit_denominator(10 ** 15) for v in z]
    return J.active_rows_at_point(zf, tol)


def gradA(z, rows):
    return P.grad_matrix([T._to_iv(float(v)) for v in z], rows)


def rowvals(z, rows):
    pt = [T._to_iv(float(v)) for v in z]
    return np.array([T._mid(T.row_value(pt, r)) for r in rows])


GAP_FLOOR = 1e-11


def inflate(z, target=GAP_FLOOR):
    """Scale the centres about the bounding-box centre until every pair gap is
    >= target.  Scaling by (1+eps) opens the gap of a contacting pair by about
    eps*|c_i - c_j| ~ eps, at a cost of eps*sigma in the side, so repairing a
    violation v costs O(4v) -- which is why the line search below is allowed to
    accept a violation of at most 5% of the side it just gained."""
    z = canonical(z)
    g = pair_gaps(z).min()
    if g >= target:
        return z
    m = float(z[33]) / 2.0
    eps = max(1e-14, (target - g))
    for _ in range(40):
        w = np.asarray(z, float).copy()
        w[0:33:3] = m + (w[0:33:3] - m) * (1.0 + eps)
        w[1:33:3] = m + (w[1:33:3] - m) * (1.0 + eps)
        w = canonical(w)
        if pair_gaps(w).min() >= target:
            return w
        eps *= 2.0
    return canonical(z)


def contact_target(vals, rows):
    """Feasibility floor for each active row: a contact may BREAK (its value
    may rise freely), it may not be violated.  Floor = min(value, 1e-10)."""
    t = np.minimum(np.asarray(vals, float), 1e-10)
    return np.maximum(t, GAP_FLOOR)


def restore(z, rows, A, target, nround=2):
    """ONE-SIDED SQP restoration: least-norm correction in the 33 configuration
    coordinates lifting only those active SEPARATION rows that have fallen
    BELOW their feasibility floor.  Rows that rose (contacts breaking, which is
    exactly what a Gordan descent step does) are left alone; corner-dominance
    ties and wall rows are free too (canonical() pins the extremal walls)."""
    sep = np.array([k for k, r in enumerate(rows) if r['kind'] == 'sep'], int)
    if not len(sep):
        return canonical(z)
    for _ in range(nround):
        v = rowvals(z, rows)[sep]
        e = target[sep] - v
        bad = e > 0
        if not bad.any():
            break
        M = A[sep[bad]][:, :33]
        try:
            d, *_ = np.linalg.lstsq(M, e[bad], rcond=1e-12)
        except np.linalg.LinAlgError:
            break
        if not np.all(np.isfinite(d)) or np.max(np.abs(d)) > 0.05:
            break
        w = np.asarray(z, float).copy()
        w[:33] += d
        z = canonical(w)
    return canonical(z)


# ------------------------------------------------------- feasible-descent flow

def wtol_of(step):
    """epsilon-active working tolerance: a constraint whose gap is below the
    distance the step travels can block the descent, so it must be IN the
    descent set.  Clamped to the ladder [1e-6, 1e-3]."""
    return float(min(max(20.0 * step, TOL_LADDER[0]), TOL_LADDER[-1]))


def flow(z0, verbose=False):
    """Gordan descent to a Fritz-John point.  Returns (z, info)."""
    t_start = time.time()
    z = inflate(canonical(z0))
    sig0 = enclosing_side(z)
    step = 1e-5
    wtol = wtol_of(step)
    rows, info = classify(z, wtol)
    if rows is None:
        return z, {'status': 'seed_infeasible', 'reason': info.get('point_reason'),
                   'sigma0': sig0}
    target = contact_target(rowvals(z, rows), rows)
    wcap = TOL_LADDER[-1]      # the working tolerance may only RATCHET DOWN
    n_class = 1
    it = 0
    res = float('inf')
    res_tight = None
    fails = 0

    def done(st):
        return z, {'status': st, 'iters': it, 'res': res, 'tol': wtol,
                   'res_tight': res_tight, 'n_classify': n_class,
                   'sigma0': sig0, 'step': step, 'sigma': enclosing_side(z),
                   'secs': time.time() - t_start}

    def reclass(w):
        nonlocal rows, info, target, n_class, wtol, z
        wtol = float(min(max(wtol_of(step), TOL_LADDER[0]), w))
        z = inflate(z)
        rows, info = classify(z, wtol)
        n_class += 1
        if rows is None:
            return False
        target = contact_target(rowvals(z, rows), rows)
        return True

    for it in range(1, MAXIT + 1):
        if time.time() - t_start > SEED_SECS:
            return done('time_cap')
        A = gradA(z, rows)
        res, lam, r = cone_nnls(A)
        if res <= CONE_TOL:
            if wtol <= TOL_LADDER[0] * 1.001:
                return done('fj')
            # FJ at the working tolerance only -- re-check at the tight end
            rt, _i = classify(z, TOL_LADDER[0])
            n_class += 1
            if rt is None:
                return done('went_infeasible')
            res_tight, _, _ = cone_nnls(gradA(z, rt))
            if res_tight <= CONE_TOL:
                return done('fj')
            # ratchet the working tolerance down and keep descending
            wcap = max(wtol / 10.0, TOL_LADDER[0])
            step = wcap / 20.0
            if not reclass(wcap):
                return done('went_infeasible')
            fails = 0
            continue
        d = r / max(np.max(np.abs(r)), 1e-300)
        s_cur = enclosing_side(z)
        moved = False
        t = step
        for _ in range(45):
            w = np.asarray(z, float).copy()
            w[:33] += t * d[:33]
            z2 = restore(canonical(w), rows, A, target, nround=2)
            ds = s_cur - enclosing_side(z2)
            if ds > 0 and pair_gaps(z2).min() >= -0.05 * ds:
                z3 = inflate(z2)
                if enclosing_side(z3) < s_cur - 1e-16:
                    z = z3
                    moved = True
                    break
            t *= 0.5
            if t < 1e-15:
                break
        if moved:
            fails = 0
            step = min(t * 1.7, 0.02)
        else:
            fails += 1
            # the trial that failed is informative: retry from just below it
            step = max(t * 4.0, 1e-14)
            if fails >= 3:
                if wcap > TOL_LADDER[0] * 1.001:
                    wcap = max(wcap / 10.0, TOL_LADDER[0])
                    step = max(step, wcap / 20.0)
                    fails = 0
                else:
                    return done('stuck')
        need = (not moved) or (it % RECLASS_EVERY == 0) \
            or wtol_of(step) < wtol * 0.5 \
            or int((pair_gaps(z) <= wtol).sum()) != info.get('n_contact_pairs', -1)
        if need and not reclass(wcap):
            return done('went_infeasible')
    return done('maxit')


# ------------------------------------------------------------ Newton polish

def newton_polish(z, rows, lam, maxit=NEWTON_IT):
    """Damped Newton on the ACTIVE-set FJ system; accepted only if the packing
    stays feasible and the side does not increase."""
    m = len(rows)
    n = T.NV + 1 + m
    lam = np.asarray(lam, float)
    sc = 1.0 + float(lam.sum())
    x = np.concatenate([np.asarray(z, float), [1.0 / sc], lam / sc])
    s_ref = float(z[33])
    best = (np.asarray(z, float), float('inf'))
    for it in range(1, maxit + 1):
        zb = [iv.mpf(float(v)) for v in x[:T.NV]]
        cache = [T.row_grad_hess(zb, r) for r in rows]
        lb = [iv.mpf(float(v)) for v in x[T.NV + 1:]]
        F, Jc, _ = T.fj_eval(zb, rows, iv.mpf(float(x[T.NV])), lb,
                             order=2, cache=cache, mode='active')
        Ff = np.array([T._mid(f) for f in F])
        fres = float(np.max(np.abs(Ff)))
        zc = canonical(x[:T.NV])
        if (fres < best[1] and pair_gaps(zc).min() >= -FEAS_EPS
                and float(zc[33]) <= s_ref + 1e-12):
            best = (zc, fres)
        if fres < 1e-12:
            break
        Jf = np.zeros((n, n))
        for i in range(n):
            for jx, v in Jc[i].items():
                Jf[i, jx] = T._mid(v)
        try:
            dx, *_ = np.linalg.lstsq(Jf, -Ff, rcond=1e-12)
        except np.linalg.LinAlgError:
            break
        if not np.all(np.isfinite(dx)):
            break
        st = np.max(np.abs(dx[:T.NV]))
        if st > 1e-3:
            dx = dx * (1e-3 / st)
        x = x + dx
        if np.max(np.abs(dx)) < 1e-16:
            break
    return best


# ------------------------------------------------------------ verdict at a pt

def verdict(z, tag):
    """FJ verdict at z over the whole tolerance ladder."""
    out = {}
    z = inflate(canonical(z))
    sig = enclosing_side(z)          # true side, PAD-free
    out['sigma'] = sig
    out['s_var'] = float(z[33])
    out['sat_gap'] = sat_gap(z)
    out['container_slack'] = container_slack(z, float(z[33]))
    out['packing_feasible'] = bool(out['sat_gap'] >= -1e-9
                                   and out['container_slack'] >= -1e-9)
    kf, naa, dslot = k0_census(z, float(z[33]))
    out['k_flush_corner'] = kf
    out['n_axis_aligned'] = naa
    out['min_corner_slot_dist'] = dslot
    out['k0'] = bool(kf == 0)
    lad = []
    for tol in TOL_LADDER:
        rows, info = classify(z, tol)
        if rows is None:
            lad.append({'tol': tol, 'point_infeasible': True,
                        'reason': info.get('point_reason')})
            continue
        A = gradA(z, rows)
        res, lam, _ = cone_nnls(A)
        l0, l0r = lam0_zero_test(A)
        touched = set()
        for r in rows:
            if r['kind'] == 'wall':
                touched.add(r['i'])
            else:
                touched.add(r['o']); touched.add(r['p'])
        pos = lam[lam > 1e-12] if lam is not None else np.array([])
        lad.append({
            'tol': tol, 'm_active': len(rows),
            'n_wall_active': info.get('n_wall_active'),
            'n_contact_pairs': info.get('n_contact_pairs'),
            'n_pairs_no_consistent_selection':
                info.get('n_pairs_no_consistent_selection'),
            'cone_residual': res, 'fj_feasible': bool(res <= CONE_TOL),
            'support': int(len(pos)), 'min_lam': float(pos.min()) if len(pos) else 0.0,
            'max_lam': float(pos.max()) if len(pos) else 0.0,
            'rank': int(np.linalg.matrix_rank(A, tol=1e-9)),
            'rank33': int(np.linalg.matrix_rank(A[:, :33], tol=1e-9)),
            'lam0_zero_branch': l0, 'lam0_zero_residual': l0r,
            'n_rattlers': 11 - len(touched)})
    out['ladder'] = lad
    ok = [e for e in lad if e.get('fj_feasible')]
    out['fj_feasible_any_tol'] = bool(ok)
    if ok:
        out['fj_tol'] = ok[0]['tol']
        out['fj'] = ok[0]
    out['genuine'] = bool(ok and out['packing_feasible'] and out['k0'])
    # the honest criterion: FJ at the TIGHT end of the ladder (exact contacts)
    out['fj_at_tight_tol'] = bool(lad[0].get('fj_feasible'))
    out['genuine_tight'] = bool(out['fj_at_tight_tol'] and out['packing_feasible']
                                and out['k0'])
    return out


def process(tag, z0, meta):
    t0 = time.time()
    rec = {'tag': tag}
    rec.update(meta)
    zs = canonical(np.array([float(v) for v in z0]))
    rec['sigma_seed'] = enclosing_side(zs)
    rec['Delta_seed'] = rec['sigma_seed'] - S0F
    v0 = verdict(zs, tag + ':seed')
    rec['seed_fj_feasible'] = v0['fj_feasible_any_tol']
    rec['seed_fj_tol'] = v0.get('fj_tol')
    rec['seed_cone_residual_1e-6'] = v0['ladder'][0].get('cone_residual')
    rec['seed_m_active_1e-6'] = v0['ladder'][0].get('m_active')

    z1, fi = flow(zs)
    rec['flow'] = fi
    rec['sigma_flow'] = enclosing_side(canonical(z1))
    rec['flow_drop'] = rec['sigma_seed'] - rec['sigma_flow']
    rec['drift_linf'] = float(np.max(np.abs(canonical(z1) - zs)))

    # terminal Newton polish on the active set that carried the flow
    zp = inflate(canonical(z1))
    rec['newton'] = None
    tol = min(max(fi.get('tol', TOL_LADDER[0]), TOL_LADDER[0]), TOL_LADDER[-1])
    rows, _info = classify(zp, tol)
    if rows:
        A = gradA(zp, rows)
        _res, lam, _r = cone_nnls(A)
        zn, fres = newton_polish(zp, rows, lam)
        rec['newton'] = {'tol': tol, 'm_rows': len(rows), 'fres': fres,
                         'sigma': float(zn[33]),
                         'accepted': bool(fres < float('inf'))}
        if fres < 1e-9:
            zp = inflate(canonical(zn))

    v1 = verdict(zp, tag + ':polished')
    rec['final'] = v1
    rec['sigma_polished'] = v1['sigma']
    rec['survivor'] = v1['genuine']
    rec['survivor_tight'] = v1['genuine_tight']
    if v1['genuine']:
        rec['z_polished'] = [T.frac_str(Fraction(float(v)).limit_denominator(10 ** 15))
                             for v in canonical(zp)]
    rec['secs'] = time.time() - t0
    return rec


# ------------------------------------------------------------------- driver

def seeds():
    opt, _ = J.load_optima()
    items = []
    for i, o in enumerate(opt):
        items.append(('o%03d' % i, J.conf_of(o),
                      {'kind': 'a85_optimum', 'idx': i, 's_cp85': o['s'],
                       'n_axis_aligned_cp85': o['n_axis_aligned'],
                       'n_pair_contacts_cp85': o['contacts']['n_pair_contacts'],
                       'n_wall_contacts_cp85': o['contacts']['n_wall_contacts']}))
    for phi in ROT_PHIS:
        items.append(('rot_%g' % phi, P.rotated_trump(phi),
                      {'kind': 'rot_trump', 'phi': phi}))
    return items


def cmd_probe():
    items = seeds()
    print('n_seeds = %d' % len(items), flush=True)
    for tag, z, meta in [items[0], items[1], items[12], items[-1], items[-7]]:
        t1 = time.time()
        r = process(tag, z, meta)
        print('%-10s sig_seed=%.9f -> sig_pol=%.9f drop=%.2e flow=%s it=%s '
              'res=%.2e surv=%s  %.1fs'
              % (tag, r['sigma_seed'], r['sigma_polished'], r['flow_drop'],
                 r['flow'].get('status'), r['flow'].get('iters'),
                 r['flow'].get('res', float('nan')), r['survivor'],
                 time.time() - t1), flush=True)
        print('    seedFJ=%s  final ladder: %s'
              % (r['seed_fj_feasible'],
                 [(e['tol'], round(e.get('cone_residual', -1), 10),
                   e.get('m_active')) for e in r['final']['ladder']]), flush=True)


def cmd_run():
    items = seeds()
    path = os.path.join(RESULTS, 'cp87_fj_polished.jsonl')
    done = set()
    if os.path.exists(path):
        for ln in open(path):
            try:
                done.add(json.loads(ln)['tag'])
            except Exception:
                pass
    todo = [x for x in items if x[0] not in done]
    t0 = time.time()
    for n, (tag, z, meta) in enumerate(todo, 1):
        try:
            r = process(tag, z, meta)
        except Exception as e:
            r = {'tag': tag, 'error': repr(e), 'survivor': False}
            r.update(meta)
        with open(path, 'a') as f:
            f.write(json.dumps(r, default=str) + '\n')
        if n % 10 == 0 or r.get('survivor'):
            print('[%7.1fs] %3d/%3d %-10s sig=%s surv=%s'
                  % (time.time() - t0, n, len(todo), tag,
                     ('%.9f' % r['sigma_polished']) if 'sigma_polished' in r
                     else '?', r.get('survivor')), flush=True)
    print('run done: %d seeds, %.1f s' % (len(todo), time.time() - t0), flush=True)


def cmd_report():
    path = os.path.join(RESULTS, 'cp87_fj_polished.jsonl')
    recs = [json.loads(ln) for ln in open(path) if ln.strip()]
    recs = [r for r in recs if 'error' not in r]
    opt_recs = [r for r in recs if r.get('kind') == 'a85_optimum']
    surv = [r for r in recs if r.get('survivor')]
    surv_opt = [r for r in surv if r.get('kind') == 'a85_optimum']
    tight = [r for r in recs if r.get('survivor_tight')]
    tight_opt = [r for r in tight if r.get('kind') == 'a85_optimum']
    below = [r for r in surv if r['sigma_polished'] <= S_HAT + 1e-12]
    below_tight = [r for r in tight if r['sigma_polished'] <= S_HAT + 1e-12]
    below_s0 = [r for r in surv if r['sigma_polished'] <= S0F]
    # every point the flow visits is a FEASIBLE 11-square packing, and sigma is
    # monotone decreasing along it, so the least sigma ever reached is the real
    # test of "did anything get under s-hat" -- valid even for unconverged flows
    k0_pts = [r for r in recs if r['final'].get('k0')
              and r['final'].get('packing_feasible')]
    floor_all = min((r['sigma_polished'] for r in recs), default=None)
    floor_k0 = min((r['sigma_polished'] for r in k0_pts), default=None)

    fstat = {}
    for r in recs:
        k = r.get('flow', {}).get('status', '?')
        fstat[k] = fstat.get(k, 0) + 1
    bins = [(3.87, 3.88), (3.88, 3.90), (3.90, 3.95), (3.95, 4.00),
            (4.00, 4.10), (4.10, 4.30), (4.30, 99.0)]

    def dist(rs, key):
        return {'[%g,%g)' % (a, b): sum(1 for r in rs if a <= r[key] < b)
                for a, b in bins}

    tolc = {}
    for r in surv:
        t = r['final'].get('fj_tol')
        tolc[str(t)] = tolc.get(str(t), 0) + 1
    out = {
        'attempt': 'A87-drain-flow, FJ-polish re-run of the A85 k0 landings',
        'inputs': {'cp85_k0_search': 'attempts/A85-k0-route/results/cp85_k0_search.json',
                   'n_a85_optima': len(opt_recs),
                   'rot_trump_phis': list(ROT_PHIS)},
        'method': {'descent': 'NNLS-Gordan feasible descent (residual = descent dir)',
                   'polish': 'damped Newton on the active-set FJ system (mode=active)',
                   'fj_test': 'NNLS cone membership, unit-row-normalised, tol %g' % CONE_TOL,
                   'lam0_zero_branch': 'NNLS on [A^T;1^T] lam = [0;1]',
                   'tol_ladder': list(TOL_LADDER),
                   'k0_rule': 'no square both axis-aligned (1e-6) and within 1e-6 '
                              'L_inf of a corner slot',
                   'no_lp_solver': True},
        'constants': {'s_hat': S_HAT, 's0': S0F},
        'headline': {
            'any_genuine_k0_FJ_point_le_s_hat': bool(below),
            'any_genuine_k0_FJ_point_le_s_hat_TIGHT_TOL': bool(below_tight),
            'n_genuine_le_s_hat': len(below),
            'n_genuine_le_s0': len(below_s0),
            'min_survivor_side': min((r['sigma_polished'] for r in surv),
                                     default=None),
            'min_survivor_tag': min(surv, key=lambda r: r['sigma_polished'])['tag']
                                if surv else None,
            'n_survivors': len(surv),
            'n_survivors_of_262': len(surv_opt),
            'n_survivors_tight_tol_1e-6': len(tight),
            'n_survivors_tight_of_262': len(tight_opt),
            'min_survivor_side_tight': min((r['sigma_polished'] for r in tight),
                                           default=None),
            'lowest_feasible_packing_reached_any_seed': floor_all,
            'lowest_feasible_k0_packing_reached': floor_k0,
            'margin_of_that_floor_above_s_hat':
                (floor_k0 - S_HAT) if floor_k0 is not None else None,
            'n_seeds': len(recs)},
        'seed_fj_feasible_count': sum(1 for r in recs if r.get('seed_fj_feasible')),
        'flow_status_counts': fstat,
        'survivor_fj_tol_counts': tolc,
        'survivor_side_distribution': dist(surv, 'sigma_polished'),
        'seed_side_distribution': dist(recs, 'sigma_seed'),
        'survivor_rate_by_seed_side_bin': {
            '[%g,%g)' % (a, b): [sum(1 for r in surv if a <= r['sigma_seed'] < b),
                                 sum(1 for r in recs if a <= r['sigma_seed'] < b)]
            for a, b in bins},
        'flow_drop_stats': {
            'median': float(np.median([r['flow_drop'] for r in recs])) if recs else None,
            'max': float(max((r['flow_drop'] for r in recs), default=0.0)),
            'n_zero': sum(1 for r in recs if r['flow_drop'] <= 1e-15)},
        'survivors': [
            {'tag': r['tag'], 'kind': r['kind'],
             'sigma_seed': r['sigma_seed'], 'sigma_polished': r['sigma_polished'],
             'Delta_vs_s0': r['sigma_polished'] - S0F,
             'delta_vs_s_hat': r['sigma_polished'] - S_HAT,
             'flow_drop': r['flow_drop'], 'drift_linf': r['drift_linf'],
             'fj_tol': r['final'].get('fj_tol'),
             'm_active': r['final']['fj']['m_active'],
             'n_wall_contacts': r['final']['fj']['n_wall_active'],
             'n_pair_contacts': r['final']['fj']['n_contact_pairs'],
             'rank': r['final']['fj']['rank'],
             'rank33': r['final']['fj']['rank33'],
             'flat_dim_33': 33 - r['final']['fj']['rank33'],
             'support': r['final']['fj']['support'],
             'min_lam': r['final']['fj']['min_lam'],
             'cone_residual': r['final']['fj']['cone_residual'],
             'lam0_zero_branch': r['final']['fj']['lam0_zero_branch'],
             'n_rattlers': r['final']['fj']['n_rattlers'],
             'n_axis_aligned': r['final']['n_axis_aligned'],
             'sat_gap': r['final']['sat_gap'],
             'container_slack': r['final']['container_slack'],
             'k_flush_corner': r['final']['k_flush_corner'],
             'tight': bool(r.get('survivor_tight')),
             'flow_status': r['flow'].get('status'),
             'flow_iters': r['flow'].get('iters')}
            for r in sorted(surv, key=lambda r: r['sigma_polished'])],
        'non_survivor_reasons': {},
        'wall_secs': sum(r.get('secs', 0.0) for r in recs),
    }
    nr = {}
    for r in recs:
        if r.get('survivor'):
            continue
        f = r['final']
        why = ('not_fj' if not f['fj_feasible_any_tol']
               else ('not_k0' if not f['k0'] else 'infeasible_packing'))
        nr[why] = nr.get(why, 0) + 1
    out['non_survivor_reasons'] = nr
    json.dump(out, open(os.path.join(RESULTS, 'cp87_fj_polished.json'), 'w'),
              indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != 'survivors'},
                     indent=1, default=str))
    print('\nsurvivors (%d):' % len(surv))
    for s in out['survivors'][:60]:
        print(' %-10s sig=%.9f d(shat)=%+.4e tol=%g m=%d w/p=%d/%d rk=%d fd=%d '
              'sup=%d minlam=%.2e drop=%.2e' %
              (s['tag'], s['sigma_polished'], s['delta_vs_s_hat'], s['fj_tol'],
               s['m_active'], s['n_wall_contacts'], s['n_pair_contacts'],
               s['rank'], s['flat_dim_33'], s['support'], s['min_lam'],
               s['flow_drop']))


def verify_exact(zfrac, dps=80):
    """RIGOROUS re-verification of a candidate packing from its exact rational
    configuration: interval (outward-rounded) enclosures at high precision.

    Returns certified LOWER bounds on every pairwise SAT gap and a certified
    UPPER bound on the enclosing side.  A packing is certified below s_hat iff
    min_gap_lower > 0 and side_upper < s_hat.
    """
    from mpmath import mp
    old = mp.dps
    mp.dps = dps
    try:
        pt = [T._to_iv(v) for v in zfrac]
        lo = [None, None]; hi = [None, None]
        for i in range(11):
            for c in range(4):
                qx, qy = T.corner_pos_iv(pt, i, c)
                for k, q in enumerate((qx, qy)):
                    lo[k] = float(q.a) if lo[k] is None else min(lo[k], float(q.a))
                    hi[k] = float(q.b) if hi[k] is None else max(hi[k], float(q.b))
        side_up = max(hi[0] - lo[0], hi[1] - lo[1])
        gmin = None
        worst = None
        for i in range(11):
            for j in range(i + 1, 11):
                g = float(T.pair_sep_iv(pt, i, j).a)
                if gmin is None or g < gmin:
                    gmin, worst = g, (i, j)
        return {'side_upper_bound': side_up, 'min_pair_gap_lower_bound': gmin,
                'worst_pair': worst, 'dps': dps,
                'disjoint_certified': bool(gmin > 0),
                'below_s_hat_certified': bool(side_up < S_HAT),
                'below_s0_certified': bool(side_up < S0F)}
    finally:
        mp.dps = old


def cmd_verify():
    """Exact-rational re-verification of every survivor at or under s_hat."""
    path = os.path.join(RESULTS, 'cp87_fj_polished.jsonl')
    recs = [json.loads(ln) for ln in open(path) if ln.strip()]
    cands = [r for r in recs if r.get('z_polished')
             and r.get('sigma_polished', 9e9) <= S_HAT + 1e-9]
    print('candidates at or below s_hat = %.15f : %d' % (S_HAT, len(cands)))
    out = []
    for r in cands:
        z = [T.str_frac(x) for x in r['z_polished']]
        v = verify_exact(z)
        v['tag'] = r['tag']
        v['sigma_float'] = r['sigma_polished']
        v['survivor_tight'] = r.get('survivor_tight')
        v['k0'] = r['final'].get('k0')
        out.append(v)
        print(json.dumps(v, indent=1, default=str))
    json.dump({'s_hat': S_HAT, 's0': S0F, 'n_candidates': len(cands),
               'verifications': out},
              open(os.path.join(RESULTS, 'cp87_below_shat_verify.json'), 'w'),
              indent=1, default=str)
    if not cands:
        print('NO survivor reached s_hat: nothing to verify.')


CMDS = {'probe': cmd_probe, 'run': cmd_run, 'report': cmd_report,
        'verify': cmd_verify}

if __name__ == '__main__':
    for c in sys.argv[1:]:
        print('=== %s ===' % c, flush=True)
        t0 = time.time()
        CMDS[c]()
        print('=== %s done in %.1f s ===' % (c, time.time() - t0), flush=True)
