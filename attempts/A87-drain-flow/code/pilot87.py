"""A87 H1 pilot driver -- helpers copied from A30's pilot.py (no cross-attempt import).

BLAS is pinned BEFORE numpy is imported.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import itertools
import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from mpmath import iv
from scipy.optimize import linprog

import t3lib as T

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # attempts/A87-drain-flow
RESULTS = os.path.join(ROOT, 'results')
LOGS = os.path.join(ROOT, 'logs')
os.makedirs(RESULTS, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

S0 = Fraction(969271, 250000)                      # 3.877084


# ------------------------------------------------------------------ helpers

def free_gb():
    try:
        import ctypes
        k = ctypes.windll.kernel32

        class MS(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong),
                        ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong),
                        ('ullTotalPageFile', ctypes.c_ulonglong),
                        ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong),
                        ('ullAvailVirtual', ctypes.c_ulonglong),
                        ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
        m = MS(); m.dwLength = ctypes.sizeof(MS)
        k.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPhys / 2 ** 30
    except Exception:
        return 99.0


def n_workers(req):
    return 1


def math_log2(x):
    return float(math.log2(x)) if x > 0 else None


def jl(path, rec):
    with open(os.path.join(RESULTS, path), 'a') as f:
        f.write(json.dumps(rec, default=str) + '\n')


# ---------------------------------------------------- FJ multiplier tooling

def grad_matrix(box, rows):
    """Midpoint gradient matrix (m x 34) of the rows over the box."""
    A = np.zeros((len(rows), T.NV))
    for k, r in enumerate(rows):
        _, g = T.row_grad(box, r)
        for gi, val in g.items():
            A[k, gi] = T._mid(val)
    return A


def fj_multipliers(A):
    """max-min-lambda LP for  A^T lam = e_s, lam >= 0.  Returns dict."""
    m = A.shape[0]
    c = np.zeros(m + 1); c[-1] = -1.0
    Aeq = np.zeros((T.NV, m + 1)); Aeq[:, :m] = A.T
    beq = np.eye(T.NV)[:, 33]
    Aub = np.zeros((m, m + 1))
    for k in range(m):
        Aub[k, k] = -1.0; Aub[k, -1] = 1.0
    r = linprog(c, A_ub=Aub, b_ub=np.zeros(m), A_eq=Aeq, b_eq=beq,
                bounds=[(0, None)] * m + [(None, None)], method='highs')
    if not r.success:
        return {'feasible': False, 't': None,
                'rank': int(np.linalg.matrix_rank(A, tol=1e-9))}
    lam = r.x[:m]
    supp = np.where(lam > 1e-9)[0]
    dim = int(len(supp) - np.linalg.matrix_rank(A[supp], tol=1e-9)) if len(supp) else 0
    return {'feasible': True, 't': float(-r.fun), 'lam': lam.tolist(),
            'support': len(supp), 'poly_dim': dim,
            'rank': int(np.linalg.matrix_rank(A, tol=1e-9))}


def fj_lam0_zero(A):
    """Is there lam >= 0, sum lam = 1, A^T lam = 0?  (the lambda_0 = 0 branch)"""
    m = A.shape[0]
    Aeq = np.vstack([A.T, np.ones((1, m))])
    beq = np.zeros(T.NV + 1); beq[-1] = 1.0
    r = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * m,
                method='highs')
    return bool(r.success)


def find_vertex(A, tries=200, seed=0, stop_at=1e-2):
    """A |A|=34 vertex of {lam>=0, A^T lam = e_s} with independent gradients."""
    m = A.shape[0]
    if m < T.NV:
        return None
    rng = np.random.default_rng(seed)
    beq = np.eye(T.NV)[:, 33]
    best = None
    for _ in range(tries):
        c = rng.normal(size=m)
        r = linprog(c, A_eq=A.T, b_eq=beq, bounds=[(0, None)] * m, method='highs')
        if not r.success:
            continue
        lam = r.x
        supp = np.where(lam > 1e-10)[0]
        if len(supp) != T.NV:
            continue
        B = A[supp]
        if abs(np.linalg.det(B)) < 1e-8:
            continue
        v = lam[supp].min()
        if best is None or v > best[0]:
            best = (float(v), supp.tolist(), lam.tolist())
        if best[0] > stop_at:
            break
    return best


def polish(box_center, rows, supp, lam, lam0, iters=3):
    """Float Newton polish of the ACTIVE-set FJ system (reduces F(mid))."""
    z = np.array([float(x) for x in box_center])
    arows = [rows[i] for i in supp]
    al = np.array([lam[i] for i in supp])
    x = np.concatenate([z, [lam0], al])
    m = len(arows)
    n = T.NV + 1 + m
    Ff = np.zeros(n)
    for _ in range(iters):
        zb = [iv.mpf(float(v)) for v in x[:T.NV]]
        cache = [T.row_grad_hess(zb, r) for r in arows]
        lb = [iv.mpf(float(v)) for v in x[T.NV + 1:]]
        F, J, _ = T.fj_eval(zb, arows, iv.mpf(float(x[T.NV])), lb,
                            order=2, cache=cache, mode='active')
        Ff = np.array([T._mid(f) for f in F])
        Jf = np.zeros((n, n))
        for i in range(n):
            for j, v in J[i].items():
                Jf[i, j] = T._mid(v)
        try:
            dx = np.linalg.solve(Jf, -Ff)
        except np.linalg.LinAlgError:
            break
        x = x + dx
        if np.max(np.abs(dx)) < 1e-14:
            break
    return x, float(np.max(np.abs(Ff)))


# --------------------------------------------------------- cells / configs

def renormalise(z, pad=0.0):
    """Translate a configuration so its minimum corner coordinate is `pad`."""
    pt = [T._to_iv(x) for x in z]
    mx = my = None
    for i in range(11):
        for c in range(4):
            qx, qy = T.corner_pos_iv(pt, i, c)
            mx = float(qx.a) if mx is None else min(mx, float(qx.a))
            my = float(qy.a) if my is None else min(my, float(qy.a))
    dx = Fraction(pad - mx).limit_denominator(10 ** 15)
    dy = Fraction(pad - my).limit_denominator(10 ** 15)
    out = list(z)
    for i in range(11):
        out[3 * i] = out[3 * i] + dx
        out[3 * i + 1] = out[3 * i + 1] + dy
    return out


def max_corner(z):
    pt = [T._to_iv(q) for q in z]
    m = None
    for i in range(11):
        for c in range(4):
            qx, qy = T.corner_pos_iv(pt, i, c)
            v = max(float(qx.b), float(qy.b))
            m = v if m is None else max(m, v)
    return m


def build_cell(zc, R, s0):
    """Cell = 33 configuration coordinates boxed by R, s in [sigma_min, s0]."""
    box = T.box_from(zc, R)
    box[33] = iv.mpf([3.0, float(s0) + 1e-15])
    return T.clip_s(box, s0)


def spec_of(z, R, s0):
    return {'z': [T.frac_str(x) if hasattr(x, 'numerator') else str(x) for x in z],
            'R': T.frac_str(R), 's0': T.frac_str(s0)}


def box_of_spec(sp):
    z = [T.str_frac(x) for x in sp['z']]
    return build_cell(z, T.str_frac(sp['R']), T.str_frac(sp['s0']))


def a04_to_a22(x, den=10 ** 12):
    """A04 layout (cx_0,cy_0,...,cx_10,cy_10, th_0..th_10, s) -> A22 layout."""
    z = []
    for i in range(11):
        z += [Fraction(x[2 * i]).limit_denominator(den),
              Fraction(x[2 * i + 1]).limit_denominator(den),
              Fraction(x[22 + i]).limit_denominator(den)]
    z.append(Fraction(x[33]).limit_denominator(den))
    return z


def normalise_config(z):
    """renormalise to min corner at 1e-9 and set z[33] = exact bounding side."""
    z = renormalise(list(z), pad=1e-9)
    mc = max_corner(z)
    z[33] = Fraction(mc).limit_denominator(10 ** 15) + Fraction(1, 10 ** 12)
    return z


def rotated_trump(phi):
    """Rotate every centre about (shat/2, shat/2) by phi, add phi to theta."""
    from mpmath import mp
    old = mp.dps
    mp.dps = 80
    z0, _ = T.load_trump()
    m = mp.mpf(z0[33].numerator) / mp.mpf(z0[33].denominator) / 2
    ph = mp.mpf(phi)
    c, s_ = mp.cos(ph), mp.sin(ph)
    z = list(z0)
    D = 10 ** 45
    for i in range(11):
        px = mp.mpf(z0[3 * i].numerator) / mp.mpf(z0[3 * i].denominator) - m
        py = mp.mpf(z0[3 * i + 1].numerator) / mp.mpf(z0[3 * i + 1].denominator) - m
        nx = m + c * px - s_ * py
        ny = m + s_ * px + c * py
        z[3 * i] = Fraction(mp.nstr(nx, 60, strip_zeros=False)).limit_denominator(D)
        z[3 * i + 1] = Fraction(mp.nstr(ny, 60, strip_zeros=False)).limit_denominator(D)
        z[3 * i + 2] = z0[3 * i + 2] + Fraction(
            mp.nstr(ph, 60, strip_zeros=False)).limit_denominator(D)
    mp.dps = old
    return normalise_config(z)


# ------------------------------------------------------------ menu sweeping

def menu_sweep(box, ab, mn, cap):
    """Per-selection Farkas exclusion over up to `cap` menu selections."""
    t0 = time.time()
    allrows = list(mn['union'])
    cache = T.grad_cache(box, allrows)
    t_cache = time.time() - t0
    wallkeys = [T.row_key(r) for r in ab['wall_straddle']]
    pairs = sorted(mn['menus'].keys())
    opts = [[[T.row_key(r) for r in s['straddle']] for s in mn['menus'][p]]
            for p in pairs]
    total = 1
    for o in opts:
        total *= max(len(o), 1)
    t0 = time.time()
    n_done = n_killed = n_alive = 0
    alive_examples = []
    for idx, combo in enumerate(itertools.product(*opts)):
        if n_done >= cap:
            break
        keys = list(wallkeys)
        for c in combo:
            keys += c
        keys = list(dict.fromkeys(keys))
        ok, y, eps = T.farkas_lp_cached(cache, keys)
        n_done += 1
        if ok:
            vok, _ = T.verify_farkas_cached(cache, keys, y)
            if vok:
                n_killed += 1
                continue
        n_alive += 1
        if len(alive_examples) < 5:
            alive_examples.append({'idx': idx, 'n_rows': len(keys), 'eps': eps})
    dt = time.time() - t0
    sps = (dt / n_done) if n_done else None
    return {'menu_total': total, 'n_tested': n_done, 'n_killed': n_killed,
            'n_alive': n_alive, 'complete': n_done >= total,
            't_cache': t_cache, 't_sweep': dt,
            'secs_per_selection': sps, 'cpu_secs_per_selection': sps,
            'alive_examples': alive_examples}


# -------------------------------------------------------------- cell report

def cell_report(box, tag, sweep_cap=0, sweep_menu_log2_cap=40.0):
    """Full cheap-path T3 pass over one cell + optional per-selection sweep.

    Verdicts: 'a', 'a-menu', 'b', 'c1-union', 'c1-sweep', 'alive'.
    (Caller emits 'a-sigma' when build_cell returned None.)
    """
    out = {'tag': tag}
    t0 = time.time()
    ab = T.test_ab(box)
    out['t_ab'] = time.time() - t0
    out['infeasible_reason'] = ab['reason']
    if ab['infeasible']:
        out['verdict'] = 'a'
        out['t_total'] = time.time() - t0
        return out
    out['min_gap'] = ab['min_gap']
    out['min_clear'] = ab['min_clear']
    out['n_wall_straddle'] = len(ab['wall_straddle'])
    out['n_pairs_straddle'] = sum(1 for v in ab['pairs'].values()
                                  if v[0] == 'straddle')
    if ab['d2']:
        out['verdict'] = 'b'
        out['delta'] = ab['delta']
        out['t_total'] = time.time() - t0
        return out

    t1 = time.time()
    mn = T.build_menu(box, ab)
    out['t_menu'] = time.time() - t1
    out['menu_log2'] = math_log2(mn['menu_size'])
    if mn['empty_pairs']:
        out['infeasible_reason'] = ('empty selection menu for pair %s'
                                    % (mn['empty_pairs'][0],))
        out['verdict'] = 'a-menu'
        out['t_total'] = time.time() - t0
        return out
    out['n_union_rows'] = len(mn['union'])

    t1 = time.time()
    ok, y, eps, info = T.farkas_lp(box, mn['union'])
    out['t_farkas_lp'] = time.time() - t1
    out['farkas_eps'] = eps
    out['farkas_ok'] = bool(ok)
    if ok:
        t1 = time.time()
        vok, worst = T.verify_farkas(box, mn['union'], y)
        out['t_farkas_verify'] = time.time() - t1
        out['farkas_verified'] = bool(vok)
        out['farkas_min_slope'] = worst
        if vok:
            out['verdict'] = 'c1-union'
            out['t_total'] = time.time() - t0
            return out
    out['verdict'] = 'alive'

    if sweep_cap:
        if out['menu_log2'] is not None and out['menu_log2'] > sweep_menu_log2_cap:
            out['sweep_skipped'] = 'menu_log2=%.1f > %.0f' % (out['menu_log2'],
                                                              sweep_menu_log2_cap)
        else:
            out['sweep'] = menu_sweep(box, ab, mn, sweep_cap)
            if out['sweep']['complete'] and out['sweep']['n_alive'] == 0:
                out['verdict'] = 'c1-sweep'
    out['t_total'] = time.time() - t0
    return out


def run_cell(z, R, s0, tag, sweep_cap=0):
    t0 = time.time()
    box = build_cell(z, R, s0)
    if box is None:
        return {'tag': tag, 'verdict': 'a-sigma', 't_ab': time.time() - t0,
                't_total': time.time() - t0}
    rep = cell_report(box, tag, sweep_cap=sweep_cap)
    rep['s_box'] = [float(box[33].a), float(box[33].b)]
    return rep


def cell_excluded(zc, R, s0, use_farkas=True):
    """Cheap verdict: 'a', 'a-menu', 'b', 'c1', or None (survives)."""
    box = build_cell(zc, R, s0)
    if box is None:
        return 'a'
    ab = T.test_ab(box)
    if ab['infeasible']:
        return 'a'
    if ab['d2']:
        return 'b'
    mn = T.build_menu(box, ab)
    if mn['empty_pairs']:
        return 'a-menu'
    if use_farkas:
        ok, y, eps, _ = T.farkas_lp(box, mn['union'])
        if ok:
            vok, _ = T.verify_farkas(box, mn['union'], y)
            if vok:
                return 'c1'
    return None


# ------------------------------------------------- A04 family (selftest use)

def family_config(s_min):
    p = os.path.join(HERE, '..', '..', 'A04-upper-search',
                     'families_catalogue.json')
    d = json.load(open(p))
    f = min((q for q in d['families'] if abs(q['s_min'] - s_min) < 1e-5),
            key=lambda q: q['s_min'])
    return a04_to_a22(f['best_x'])


def loose_config(s_target=3.9, s_min=3.8856181):
    z = family_config(s_min)
    s = float(z[33])
    m = s / 2.0

    def expand(eta):
        zz = list(z)
        for i in range(11):
            zz[3 * i] = z[3 * i] + Fraction((float(z[3 * i]) - m) * eta
                                            ).limit_denominator(10 ** 12)
            zz[3 * i + 1] = z[3 * i + 1] + Fraction((float(z[3 * i + 1]) - m) * eta
                                                    ).limit_denominator(10 ** 12)
        return renormalise(zz, pad=1e-9)

    lo, hi = 0.0, 0.2
    for _ in range(50):
        eta = (lo + hi) / 2
        if max_corner(expand(eta)) > s_target:
            hi = eta
        else:
            lo = eta
    zz = expand(lo)
    zz[33] = Fraction(s_target).limit_denominator(10 ** 12)
    return zz, lo
