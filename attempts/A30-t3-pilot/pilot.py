"""A30 T3 pilot driver.  Usage:  python pilot.py P1 [P2 P3 ...] [--workers 6]

Every test checkpoints to state/<name>.json as soon as it finishes, and to
results/pilot_report.json at the end of each test, so the run is resumable
(re-running skips tests whose checkpoint already exists unless --force).
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv
from scipy.optimize import linprog

import t3lib as T

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'state')
RESULTS = os.path.join(HERE, 'results')
os.makedirs(STATE, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

MAXW = 6                      # hard cap on heavy workers (box OOM'd at 9)
MEM_FLOOR_GB = 3.0            # refuse to spawn below this much free RAM


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
    n = min(req, MAXW, os.cpu_count() or 1)
    fg = free_gb()
    allow = max(1, int((fg - MEM_FLOOR_GB) // 1.0))    # ~1 GB budget/worker
    return max(1, min(n, allow))


def save(name, obj):
    with open(os.path.join(STATE, name + '.json'), 'w') as f:
        json.dump(obj, f, indent=1, default=str)


def loadck(name):
    p = os.path.join(STATE, name + '.json')
    return json.load(open(p)) if os.path.exists(p) else None


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
        return {'feasible': False, 't': None}
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


# -------------------------------------------------------------- cell report

def spec_of(z, R, s0):
    return {'z': [T.frac_str(x) if hasattr(x, 'numerator') else str(x) for x in z],
            'R': T.frac_str(R), 's0': T.frac_str(s0)}


def box_of_spec(sp):
    z = [T.str_frac(x) for x in sp['z']]
    return build_cell(z, T.str_frac(sp['R']), T.str_frac(sp['s0']))


def _sweep_chunk(arg):
    """Worker: per-selection Farkas over menu indices [lo, hi)."""
    import itertools
    sp, lo, hi = arg
    box = box_of_spec(sp)
    ab = T.test_ab(box)
    mn = T.build_menu(box, ab)
    cache = T.grad_cache(box, mn['union'])
    wallkeys = [T.row_key(r) for r in ab['wall_straddle']]
    pairs = sorted(mn['menus'].keys())
    opts = [[[T.row_key(r) for r in s['straddle']] for s in mn['menus'][p]]
            for p in pairs]
    n_done = n_killed = n_alive = 0
    examples = []
    t0 = time.time()
    for idx, combo in enumerate(itertools.product(*opts)):
        if idx < lo:
            continue
        if idx >= hi:
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
        if len(examples) < 3:
            examples.append({'idx': idx, 'n_rows': len(keys), 'eps': eps})
    return n_done, n_killed, n_alive, examples, time.time() - t0


def menu_sweep_par(sp, total, cap, workers):
    """Parallel per-selection Farkas sweep (<= MAXW workers, memory guarded)."""
    import multiprocessing as mp
    n = min(total, cap)
    w = n_workers(workers)
    step = max(1, (n + w - 1) // w)
    chunks = [(sp, i, min(i + step, n)) for i in range(0, n, step)]
    t0 = time.time()
    if len(chunks) == 1:
        res = [_sweep_chunk(chunks[0])]
    else:
        with mp.Pool(min(w, len(chunks)), maxtasksperchild=1) as pool:
            res = pool.map(_sweep_chunk, chunks)
    dt = time.time() - t0
    nd = sum(r[0] for r in res); nk = sum(r[1] for r in res)
    na = sum(r[2] for r in res)
    ex = [e for r in res for e in r[3]][:5]
    cpu = sum(r[4] for r in res)
    return {'menu_total': total, 'n_tested': nd, 'n_killed': nk, 'n_alive': na,
            'complete': nd >= total, 'wall_secs': dt, 'cpu_secs': cpu,
            'workers': len(chunks),
            'cpu_secs_per_selection': (cpu / nd) if nd else None,
            'alive_examples': ex}


def menu_sweep(box, ab, mn, cap):
    """Enumerate menu selections (up to `cap`) and try the per-selection
    Farkas exclusion on each.  Rigorously verifies every success."""
    import itertools
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
    lp_times = []
    for idx, combo in enumerate(itertools.product(*opts)):
        if n_done >= cap:
            break
        keys = list(wallkeys)
        for c in combo:
            keys += c
        keys = list(dict.fromkeys(keys))
        t1 = time.time()
        ok, y, eps = T.farkas_lp_cached(cache, keys)
        lp_times.append(time.time() - t1)
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
    return {'menu_total': total, 'n_tested': n_done, 'n_killed': n_killed,
            'n_alive': n_alive, 'complete': n_done >= total,
            't_cache': t_cache, 't_sweep': dt,
            'secs_per_selection': (dt / n_done) if n_done else None,
            'alive_examples': alive_examples}


def cell_report(box, tag, sample_sel=0, seed=0, do_krawczyk=True,
                lam_rad=1e-3, sweep_cap=0, spec=None, workers=6):
    """Full T3 pass over one cell.  Returns a JSON-able dict."""
    out = {'tag': tag}
    t0 = time.time()
    ab = T.test_ab(box)
    out['t_ab'] = time.time() - t0
    out['infeasible'] = ab['infeasible']
    out['infeasible_reason'] = ab['reason']
    if ab['infeasible']:
        out['verdict'] = 'excluded(a)'
        out['t_total'] = time.time() - t0
        return out
    out['min_gap'] = ab['min_gap']
    out['min_clear'] = ab['min_clear']
    out['d2'] = ab['d2']
    out['n_wall_straddle'] = len(ab['wall_straddle'])
    out['n_pairs_straddle'] = sum(1 for v in ab['pairs'].values()
                                  if v[0] == 'straddle')
    if ab['d2']:
        out['verdict'] = 'excluded(b)'
        out['delta'] = ab['delta']
        out['t_total'] = time.time() - t0
        return out

    t1 = time.time()
    mn = T.build_menu(box, ab)
    out['t_menu'] = time.time() - t1
    out['menu_size'] = mn['menu_size']
    out['menu_log2'] = math_log2(mn['menu_size'])
    if mn['empty_pairs']:
        out['infeasible'] = True
        out['infeasible_reason'] = ('empty selection menu for pair %s'
                                    % (mn['empty_pairs'][0],))
        out['verdict'] = 'excluded(a-menu)'
        out['t_total'] = time.time() - t0
        return out
    out['n_union_rows'] = len(mn['union'])
    out['per_pair_menu'] = {str(k): v for k, v in sorted(mn['per_pair'].items())}

    # ---- (c1) union Farkas LP: kills the WHOLE menu with one certificate
    t1 = time.time()
    ok, y, eps, info = T.farkas_lp(box, mn['union'])
    t_lp = time.time() - t1
    out['t_farkas_lp'] = t_lp
    out['farkas_eps'] = eps
    out['farkas_ok'] = bool(ok)
    if ok:
        t1 = time.time()
        vok, worst = T.verify_farkas(box, mn['union'], y)
        out['t_farkas_verify'] = time.time() - t1
        out['farkas_verified'] = bool(vok)
        out['farkas_min_slope'] = worst
        if vok:
            out['verdict'] = 'excluded(c1-union-Farkas)'
            out['t_total'] = time.time() - t0
            return out
    out['verdict'] = 'NOT excluded by (a)/(b)/(c1-union)'

    # ---- (c1') per-selection Farkas sweep over the menu
    if sweep_cap:
        if spec is not None:
            out['sweep'] = menu_sweep_par(spec, mn['menu_size'], sweep_cap,
                                          workers)
        else:
            out['sweep'] = menu_sweep(box, ab, mn, sweep_cap)
        if out['sweep'].get('complete') and out['sweep']['n_alive'] == 0:
            out['verdict'] = 'excluded(c1-per-selection-Farkas)'

    # ---- diagnostics on the Trump-style "consistent" selections
    if sample_sel:
        out['selections'] = sample_selections(box, ab, mn, sample_sel, seed,
                                              do_krawczyk, lam_rad)
    out['t_total'] = time.time() - t0
    return out


def math_log2(x):
    import math
    return float(math.log2(x)) if x > 0 else None


def sample_selections(box, ab, mn, k, seed, do_krawczyk, lam_rad):
    rng = random.Random(seed)
    pairs = sorted(mn['menus'].keys())
    seen = set()
    recs = []
    for _ in range(k):
        choice = tuple(rng.randrange(len(mn['menus'][p])) for p in pairs)
        if choice in seen:
            continue
        seen.add(choice)
        sel_rows = []
        for p, ci in zip(pairs, choice):
            s = mn['menus'][p][ci]
            sel_rows += s['straddle']
        rows = list(ab['wall_straddle']) + sel_rows
        rec = {'sel': list(choice), 'm': len(rows), 'n_fj': 35 + len(rows)}
        t0 = time.time()
        A = grad_matrix(box, rows)
        rec['t_grad'] = time.time() - t0
        t0 = time.time()
        mu = fj_multipliers(A)
        rec['t_mult_lp'] = time.time() - t0
        rec.update({'fj_feasible': mu['feasible'], 'min_lam': mu.get('t'),
                    'mult_support': mu.get('support'),
                    'mult_poly_dim': mu.get('poly_dim'),
                    'grad_rank': mu.get('rank')})
        t0 = time.time()
        rec['lam0_zero_branch'] = fj_lam0_zero(A)
        rec['t_lam0_lp'] = time.time() - t0
        # per-selection Farkas LP (weaker rows than the union LP)
        t0 = time.time()
        ok, y, eps, _ = T.farkas_lp(box, rows)
        rec['t_sel_farkas'] = time.time() - t0
        rec['sel_farkas_eps'] = eps
        rec['sel_farkas_ok'] = bool(ok)
        if ok:
            vok, w = T.verify_farkas(box, rows, y)
            rec['sel_farkas_verified'] = bool(vok)
        if do_krawczyk and mu['feasible']:
            # (c2) complementarity form -- expected singular when the
            # multiplier polytope has positive dimension
            lam = np.array(mu['lam']); z = 1.0 + lam.sum()
            lamn = lam / z; lam0n = 1.0 / z
            lb = [iv.mpf([float(v) - lam_rad, float(v) + lam_rad]) for v in lamn]
            l0 = iv.mpf([lam0n - lam_rad, lam0n + lam_rad])
            t0 = time.time()
            kc = T.krawczyk_fj(box, rows, l0, lb, mode='compl')
            rec['krawczyk_compl'] = {'n': kc['n'], 'singular': kc['singular'],
                                     'cond': kc['cond'], 'excluded': kc['excluded'],
                                     'isolated': kc['isolated'],
                                     'ratio': kc.get('ratio'),
                                     'secs': time.time() - t0}
            # (c2') active-set sub-branch: a |A| = 34 vertex
            t0 = time.time()
            v = find_vertex(A, tries=60, seed=seed)
            rec['t_vertex_search'] = time.time() - t0
            rec['vertex_found'] = v is not None
            if v is not None:
                minlam, supp, lamv = v
                zc = [T._mid(x) for x in box]
                xp, resid = polish(zc, rows, supp, lamv, 1.0)
                arows = [rows[i] for i in supp]
                # polish() already solved the normalised FJ system: use as is
                al = [xp[T.NV + 1 + q] for q in range(len(supp))]
                l0v = xp[T.NV]
                lb = [iv.mpf([v - lam_rad, v + lam_rad]) for v in al]
                l0 = iv.mpf([l0v - lam_rad, l0v + lam_rad])
                t0 = time.time()
                ka = T.krawczyk_fj(box, arows, l0, lb, mode='active')
                rec['krawczyk_active'] = {'n': ka['n'], 'cond': ka['cond'],
                                          'excluded': ka['excluded'],
                                          'isolated': ka['isolated'],
                                          'ratio': ka.get('ratio'),
                                          'min_lam': minlam,
                                          'newton_resid': resid,
                                          'secs': time.time() - t0}
        recs.append(rec)
    return recs


# --------------------------------------------------------------- the tests

def trump_cell(radius, s_slack=Fraction(1, 10 ** 6), offset=None):
    z0, _ = T.load_trump()
    if offset is not None:
        z0 = [x + Fraction(o).limit_denominator(10 ** 15)
              for x, o in zip(z0, offset)]
    box = T.box_from(z0, radius)
    box = T.clip_s(box, z0[33] + s_slack)
    return z0, box


def test_P1(args):
    """Positive control: A22's box (radius 5e-4 around Trump), s0 = s^ + 1e-6."""
    out = {'name': 'P1', 'desc': 'positive control at Trump, radius 5e-4'}
    R = Fraction(1, 2000)
    z0, _ = T.load_trump()
    s0 = z0[33] + Fraction(1, 10 ** 6)
    box = build_cell(z0, R, s0)
    sp = spec_of(z0, R, s0)
    out['radius'] = float(R)
    out['s0'] = float(s0)
    out['s_box'] = [float(box[33].a), float(box[33].b)]
    rep = cell_report(box, 'P1-main', sample_sel=args.samples, seed=1,
                      do_krawczyk=True, lam_rad=1e-3,
                      sweep_cap=args.sweep_cap, spec=sp, workers=args.workers)
    out['cell'] = rep
    save('P1_main', out)

    # does the exact Trump point survive every menu selection?  (D3' says yes)
    pt = [T._to_iv(x) for x in z0]
    abp = T.test_ab(pt); mnp = T.build_menu(pt, abp)
    out['point_menu_size'] = mnp['menu_size']
    out['point_union_rows'] = len(mnp['union'])
    okp, yp, epsp, _ = T.farkas_lp(pt, mnp['union'])
    out['point_farkas_eps'] = epsp
    out['point_farkas_ok'] = bool(okp)

    # contraction radius scan for the active-set FJ Krawczyk
    scan = []
    ab = T.test_ab(box); mn = T.build_menu(box, ab)
    sel_rows = []
    for p in sorted(mn['menus'].keys()):
        for s in mn['menus'][p]:
            vals = [T.row_value(pt, r) for r in s['rows']]
            if all(v.b > -1e-20 for v in vals):
                sel_rows += [r for r, v in zip(s['rows'], vals)
                             if abs(float(v.a)) < 1e-20]
                break
    rows = list(ab['wall_straddle']) + sel_rows
    A = grad_matrix(box, rows)
    v = find_vertex(A, tries=400, seed=7)
    out['trump_sel_rows'] = len(rows)
    out['trump_sel_rank'] = int(np.linalg.matrix_rank(A, tol=1e-9))
    out['trump_mult_poly_dim'] = len(rows) - out['trump_sel_rank']
    if v is not None:
        minlam, supp, lamv = v
        out['vertex_min_lam'] = minlam
        arows = [rows[i] for i in supp]
        zc = [T._mid(x) for x in box]
        xp, resid = polish(zc, rows, supp, lamv, 1.0, iters=4)
        al = [xp[T.NV + 1 + q] for q in range(len(supp))]
        l0v = xp[T.NV]
        out['newton_resid'] = resid
        out['fj_lam0'] = float(l0v)
        out['fj_min_lam'] = float(min(al))
        for den in (1000, 2000, 3000, 5000, 10000, 50000):
            RR = Fraction(1, den)
            b2 = build_cell(z0, RR, s0)
            lr = max(2.0 * float(RR), 1e-8)
            lb = [iv.mpf([q - lr, q + lr]) for q in al]
            l0 = iv.mpf([l0v - lr, l0v + lr])
            k = T.krawczyk_fj(b2, arows, l0, lb, mode='active')
            scan.append({'radius': float(RR), 'ratio': k['ratio'],
                         'isolated': k['isolated'], 'cond': k['cond'],
                         'secs': k['secs'], 'n': k['n']})
    out['krawczyk_radius_scan'] = scan
    save('P1', out)
    return out


def renormalise(z, pad=0.0):
    """Translate a configuration so its minimum corner coordinate is `pad`
    (D_0 normalises the min corner to the origin; without this, offsetting a
    wall-touching reference point kills the cell by a trivial containment
    violation rather than by geometry)."""
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


def build_cell(zc, R, s0):
    """Cell = 33 configuration coordinates boxed by R, s in [sigma_min, s0]."""
    box = T.box_from(zc, R)
    box[33] = iv.mpf([3.0, float(s0) + 1e-15])
    return T.clip_s(box, s0)


def test_P2(args):
    """Negative control: same-radius cells offset by ~10x the radius."""
    out = {'name': 'P2', 'desc': 'negative control, 10x-radius offsets'}
    R = Fraction(1, 2000)
    D = 10 * float(R)
    z0, _ = T.load_trump()
    dirs = []

    # (i) uniform expansion of all centres about the container centre
    off = [0.0] * T.NV
    ctr = float(z0[33]) / 2
    sc = D / max(abs(float(z0[i]) - ctr) for i in range(0, 33, 3))
    for i in range(11):
        off[3 * i] = (float(z0[3 * i]) - ctr) * sc
        off[3 * i + 1] = (float(z0[3 * i + 1]) - ctr) * sc
    dirs.append(('expand', off))
    dirs.append(('contract', [-v for v in off]))

    # (ii) random directions of length D (per-coordinate) in configuration space
    rng = random.Random(11)
    for k in range(args.p2_random):
        d = [rng.gauss(0, 1) for _ in range(33)]
        nrm = max(abs(x) for x in d)
        d = [x / nrm * D for x in d]
        dirs.append(('rand%d' % k, d + [0.0]))

    # (iii) expansion magnitude scan: at what slack does D2 (b) start to fire?
    exp_scan = []
    for eps in (2.6e-3, 5e-3, 1e-2, 2e-2, 4e-2):
        o = [0.0] * T.NV
        for i in range(11):
            o[3 * i] = (float(z0[3 * i]) - ctr) * eps
            o[3 * i + 1] = (float(z0[3 * i + 1]) - ctr) * eps
        exp_scan.append(('exp%.4g' % eps, o, eps))

    recs = []
    for s0tag, s0 in (('s0=shat+1e-6', z0[33] + Fraction(1, 10 ** 6)),
                      ('s0=shat+1e-2', z0[33] + Fraction(1, 100)),
                      ('s0=shat+2e-1', z0[33] + Fraction(2, 10))):
        todo = dirs if s0tag != 's0=shat+2e-1' else [(t, o) for t, o, _ in exp_scan]
        for tag, o in todo:
            zz = [x + Fraction(v).limit_denominator(10 ** 15)
                  for x, v in zip(z0, o)]
            zz = renormalise(zz, pad=float(R))
            box = build_cell(zz, R, s0)
            if box is None:
                recs.append({'tag': 'P2-%s-%s' % (s0tag, tag), 's0': float(s0),
                             'verdict': 'excluded(a: sigma_min > s0)'})
                print('  %-28s excluded(a: sigma_min > s0)'
                      % ('%s %s' % (s0tag, tag)), flush=True)
                continue
            rep = cell_report(box, 'P2-%s-%s' % (s0tag, tag),
                              sample_sel=(args.samples if tag == 'expand' else 0),
                              seed=3, do_krawczyk=True,
                              sweep_cap=args.sweep_cap,
                              spec=spec_of(zz, R, s0), workers=args.workers)
            rep['s0'] = float(s0)
            recs.append(rep)
            save('P2_partial', recs)
            print('  %-28s %s' % ('%s %s' % (s0tag, tag), rep['verdict']),
                  flush=True)
    out['cells'] = recs
    save('P2', out)
    return out


def family_config(s_min):
    """A04 catalogue layout: x = [(cx_i, cy_i) x 11, theta_i x 11, s]."""
    p = os.path.join(HERE, '..', 'A04-upper-search', 'families_catalogue.json')
    d = json.load(open(p))
    f = min((q for q in d['families'] if abs(q['s_min'] - s_min) < 1e-5),
            key=lambda q: q['s_min'])
    x = f['best_x']
    z = []
    for i in range(11):
        z += [Fraction(x[2 * i]).limit_denominator(10 ** 12),
              Fraction(x[2 * i + 1]).limit_denominator(10 ** 12),
              Fraction(x[22 + i]).limit_denominator(10 ** 12)]
    z.append(Fraction(x[33]).limit_denominator(10 ** 12))
    return z


def max_corner(z):
    pt = [T._to_iv(q) for q in z]
    m = None
    for i in range(11):
        for c in range(4):
            qx, qy = T.corner_pos_iv(pt, i, c)
            v = max(float(qx.b), float(qy.b))
            m = v if m is None else max(m, v)
    return m


def loose_config(s_target=3.9, s_min=3.8856181):
    """A DISTINCT (non-Trump) local optimum, expanded about the container
    centre until its bounding square reaches s_target.  This is the loosest
    configuration of that structure available at s_target: every pairwise gap
    opens by ~eta * (centre separation)."""
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


def test_P3(args):
    """Generic cell: half-width ~0.01 around a perturbed non-critical config."""
    out = {'name': 'P3', 'desc': 'generic cell around a perturbed 5x45 packing at s=3.9'}
    z, eta = loose_config(3.898)
    rng = random.Random(5)
    amp = 5e-4
    zp = [q + Fraction(rng.uniform(-amp, amp)).limit_denominator(10 ** 12)
          for q in z[:33]] + [Fraction(39, 10)]
    zp = renormalise(zp, pad=1e-9)
    out['perturbation'] = amp
    out['base_family'] = ('5x45deg (A04 s_min=3.8856181), expanded about the '
                          'container centre by eta=%.5f to fill s=3.9, then '
                          'randomly perturbed by +-0.002' % eta)
    out['expansion_eta'] = eta
    # certify the base configuration is feasible
    pt = [T._to_iv(q) for q in zp]
    abp = T.test_ab(pt)
    out['base_feasible'] = (not abp['infeasible'])
    out['base_min_gap'] = abp.get('min_gap')
    out['base_min_clear'] = abp.get('min_clear')

    recs = []
    for hw in args.p3_widths:
        R = Fraction(hw).limit_denominator(10 ** 9)
        box = build_cell(zp, R, Fraction(39, 10))
        if box is None:
            recs.append({'tag': 'P3-hw%.4g' % hw, 'half_width': hw,
                         'verdict': 'excluded(a: sigma_min > s0)'})
            continue
        rep = cell_report(box, 'P3-hw%.4g' % hw,
                          sample_sel=(args.samples if hw == max(args.p3_widths) else 0),
                          seed=9, do_krawczyk=True, sweep_cap=args.sweep_cap,
                          spec=spec_of(zp, R, Fraction(39, 10)),
                          workers=args.workers)
        rep['half_width'] = hw
        recs.append(rep)
        save('P3_partial', recs)
        print('  hw=%-8g %s  (menu %s, union %s)'
              % (hw, rep['verdict'], rep.get('menu_size'),
                 rep.get('n_union_rows')), flush=True)
    # ---- how far does D2 reach?  Loosest configuration of this family as a
    # function of the container slack, and the cell half-width at which the
    # interval min-gap is still positive.
    reach = []
    for st in (3.88, 3.90, 3.95, 4.0, 4.2):
        try:
            zl, e = loose_config(st - 0.002)
            zl[33] = Fraction(st).limit_denominator(10 ** 6)
        except Exception:
            continue
        pt = [T._to_iv(q) for q in zl]
        abl = T.test_ab(pt)
        if abl['infeasible']:
            reach.append({'s_target': st, 'eta': e, 'infeasible': True})
            continue
        g0 = abl['min_gap']
        hw = None
        for h in (0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 5e-4, 2e-4, 1e-4, 5e-5):
            b = build_cell(zl, Fraction(h).limit_denominator(10 ** 9),
                           Fraction(st).limit_denominator(10 ** 6))
            if b is None:
                continue
            a2 = T.test_ab(b)
            if (not a2['infeasible']) and a2['d2']:
                hw = h
                break
        reach.append({'s_target': st, 'eta': e, 'point_min_gap': g0,
                      'largest_d2_half_width': hw})
    out['d2_reach'] = reach
    out['cells'] = recs
    save('P3', out)
    return out


TESTS = {'P1': test_P1, 'P2': test_P2, 'P3': test_P3}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('tests', nargs='*', default=['P1', 'P2', 'P3'])
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--samples', type=int, default=8)
    ap.add_argument('--p2-random', type=int, default=12)
    ap.add_argument('--p3-widths', type=float, nargs='*',
                    default=[0.01, 0.003, 0.001, 0.0003])
    ap.add_argument('--sweep-cap', type=int, default=20000)
    ap.add_argument('--x-dirs', type=int, default=24)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()
    args.workers = n_workers(args.workers)
    print('workers=%d free_ram=%.1fGB' % (args.workers, free_gb()), flush=True)
    report = loadck('report') or {}
    for t in args.tests:
        if t in report and not args.force:
            print('%s already done, skipping' % t); continue
        print('=== %s ===' % t, flush=True)
        t0 = time.time()
        report[t] = TESTS[t](args)
        report[t]['wall_secs'] = time.time() - t0
        save('report', report)
        with open(os.path.join(RESULTS, 'pilot_report.json'), 'w') as f:
            json.dump(report, f, indent=1, default=str)
        print('%s done in %.1f s' % (t, time.time() - t0), flush=True)




# ----------------------------------------------------- X: extrapolation scan

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


def _dkill(arg):
    """Smallest offset delta along direction u at which a cell of half-width R
    centred at zhat + delta*u is discharged by (a)/(b)/(c1)."""
    z0s, u, R, s0, hi = arg
    z0 = [T.str_frac(x) for x in z0s]
    R = T.str_frac(R); s0 = T.str_frac(s0)

    def at(d):
        zz = [x + Fraction(v * d).limit_denominator(10 ** 15)
              for x, v in zip(z0, list(u) + [0.0])]
        return cell_excluded(zz, R, s0)

    lo = 0.0
    if at(hi) is None:
        return {'R': float(R), 'delta_kill': None, 'reason': None,
                'searched_to': hi}
    for _ in range(22):
        mid = (lo + hi) / 2
        if at(mid) is None:
            lo = mid
        else:
            hi = mid
    return {'R': float(R), 'delta_kill': hi, 'reason': at(hi)}


def test_X(args):
    """How big is the region around zhat that no T3 test can discharge?
    delta_kill(h) / h is the linear branching overhead of the T3 tree."""
    import multiprocessing as mp
    out = {'name': 'X', 'desc': 'survival radius around Trump vs cell size'}
    z0, _ = T.load_trump()
    rng = random.Random(23)
    dirs = []
    for _ in range(args.x_dirs):
        d = [rng.gauss(0, 1) for _ in range(33)]
        n = max(abs(v) for v in d)
        dirs.append([v / n for v in d])
    rows = []
    for s0tag, s0 in (('shat+1e-6', z0[33] + Fraction(1, 10 ** 6)),
                      ('shat+1e-3', z0[33] + Fraction(1, 1000))):
        for den in (200, 1000, 2000, 10000):
            R = Fraction(1, den)
            jobs = [([T.frac_str(x) for x in z0], u, T.frac_str(R),
                     T.frac_str(s0), 2.0) for u in dirs]
            w = n_workers(args.workers)
            t0 = time.time()
            with mp.Pool(min(w, len(jobs)), maxtasksperchild=2) as pool:
                res = pool.map(_dkill, jobs)
            dk = [r['delta_kill'] for r in res if r['delta_kill'] is not None]
            reasons = {}
            for r in res:
                reasons[r['reason']] = reasons.get(r['reason'], 0) + 1
            rec = {'s0': s0tag, 'half_width': float(R), 'n_dirs': len(dirs),
                   'n_killed': len(dk),
                   'delta_kill_min': min(dk) if dk else None,
                   'delta_kill_median': sorted(dk)[len(dk) // 2] if dk else None,
                   'delta_kill_max': max(dk) if dk else None,
                   'ratio_median': (sorted(dk)[len(dk) // 2] / float(R)) if dk else None,
                   'reasons': reasons, 'wall_secs': time.time() - t0}
            rows.append(rec)
            print('  %-10s h=%-8g  delta_kill med=%-10.5g  med/h=%-8.3g  %s'
                  % (s0tag, float(R), rec['delta_kill_median'] or -1,
                     rec['ratio_median'] or -1, reasons), flush=True)
            save('X_partial', rows)
    out['scan'] = rows
    save('X', out)
    return out


TESTS['X'] = test_X


if __name__ == '__main__':
    main()
