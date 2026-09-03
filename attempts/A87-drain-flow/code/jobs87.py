"""A87 H1 pilot jobs J1-J4.  Usage: python jobs87.py {probe|j1|j2|j3|j4}"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
import random
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv

import t3lib as T
import pilot87 as P

ROOT = P.ROOT
RESULTS = P.RESULTS
CP85 = os.path.join(ROOT, '..', 'A85-k0-route', 'results', 'cp85_k0_search.json')
S0 = P.S0
S0F = float(S0)

H_LADDER = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 5e-4, 2e-4, 1e-4]
H_R7_EXTRA = [1e-5, 1e-6, 1e-7, 3e-8, 1e-8]
H_J2 = [0.05, 0.02, 0.01, 0.005, 0.002]


def load_optima():
    d = json.load(open(CP85))
    return d['optima'], d


def conf_of(o):
    return P.normalise_config(P.a04_to_a22(o['x']))


def frac(h):
    return Fraction(h).limit_denominator(10 ** 12)


# ---------------------------------------------------------------- reference

def references():
    opt, _ = load_optima()
    idx = sorted(range(len(opt)), key=lambda i: opt[i]['s'])
    refs = []
    r1 = idx[0]
    refs.append(('r1', r1, 'best k0 optimum'))
    zeros = [i for i in idx if opt[i]['n_axis_aligned'] == 0]
    r2 = zeros[0]
    refs.append(('r2', r2, 'smallest-side optimum with n_axis_aligned=0'))
    for tag, targ in (('r3', 3.95), ('r4', 4.00), ('r5', 4.20)):
        j = min(range(len(opt)), key=lambda i: abs(opt[i]['s'] - targ))
        refs.append((tag, j, 's closest to %.2f' % targ))
    out = []
    for tag, i, desc in refs:
        z = conf_of(opt[i])
        out.append({'tag': tag, 'kind': 'optimum', 'idx': i, 'desc': desc,
                    'z': z, 'sigma': float(z[33]), 's_cp85': opt[i]['s'],
                    'n_axis_aligned': opt[i]['n_axis_aligned'],
                    'n_contacts': (opt[i]['contacts']['n_pair_contacts']
                                   + opt[i]['contacts']['n_wall_contacts'])})
    for tag, phi in (('r6', 1e-3), ('r7', 5e-8)):
        z = P.rotated_trump(phi)
        out.append({'tag': tag, 'kind': 'rot-trump', 'idx': None,
                    'desc': 'Trump rotated by phi=%g' % phi,
                    'z': z, 'sigma': float(z[33]), 's_cp85': None,
                    'n_axis_aligned': None, 'n_contacts': None, 'phi': phi})
    for r in out:
        r['Delta'] = r['sigma'] - S0F
    return out


def cmd_probe():
    refs = references()
    for r in refs:
        print('%-3s sigma=%.9f  Delta=%.3e  %s' %
              (r['tag'], r['sigma'], r['Delta'], r['desc']))
    opt, d = load_optima()
    lo = [o for o in opt if o['s'] < 3.9]
    print('n_optima=%d  n_s_lt_3.9=%d' % (len(opt), len(lo)))
    ds = sorted(o['s'] - S0F for o in opt)
    print('Delta min=%.5f max=%.5f' % (ds[0], ds[-1]))
    bins = [(0.01, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.3), (0.3, 1e9)]
    for a, b in bins:
        print('  [%g,%g): %d' % (a, b, sum(1 for x in ds if a <= x < b)))


# ------------------------------------------------------------------ J1

def cmd_j1():
    refs = references()
    path = 'j1_ladder.jsonl'
    done = set()
    p = os.path.join(RESULTS, path)
    if os.path.exists(p):
        for ln in open(p):
            try:
                r = json.loads(ln)
                done.add((r['config'], r['h']))
            except Exception:
                pass
    for r in refs:
        hs = list(H_LADDER) + (H_R7_EXTRA if r['tag'] == 'r7' else [])
        for h in hs:
            if (r['tag'], h) in done:
                continue
            t0 = time.time()
            rep = P.run_cell(r['z'], frac(h), S0,
                             '%s-h%.3g' % (r['tag'], h), sweep_cap=3000)
            rec = {'job': 'J1', 'config': r['tag'], 'kind': r['kind'],
                   'desc': r['desc'], 'sigma': r['sigma'], 'Delta': r['Delta'],
                   'n_axis_aligned': r['n_axis_aligned'],
                   'n_contacts': r['n_contacts'],
                   'h': h, 'wall_secs': time.time() - t0}
            rec.update(rep)
            P.jl(path, rec)
            print('  %-3s h=%-8g %-9s t=%.2fs menu_log2=%s' %
                  (r['tag'], h, rep['verdict'], rec['wall_secs'],
                   rep.get('menu_log2')), flush=True)


# ------------------------------------------------------------------ J2

def cmd_j2():
    opt, _ = load_optima()
    path = 'j2_survey.jsonl'
    done = set()
    p = os.path.join(RESULTS, path)
    if os.path.exists(p):
        for ln in open(p):
            try:
                r = json.loads(ln)
                done.add((r['opt'], r['h'], r['offset']))
            except Exception:
                pass
    rng = random.Random(87)
    lowset = set(i for i, o in enumerate(opt) if o['s'] < 3.9)
    for i, o in enumerate(opt):
        z = None
        for h in H_J2:
            variants = [False] + ([True] if i in lowset else [])
            for off in variants:
                if (i, h, off) in done:
                    if off:
                        rng.random()
                    continue
                if z is None:
                    z = conf_of(o)
                if off:
                    zz = [q + Fraction(rng.uniform(-h / 2, h / 2)
                                       ).limit_denominator(10 ** 12)
                          for q in z[:33]] + [z[33]]
                    zz = P.normalise_config(zz)
                else:
                    zz = z
                t0 = time.time()
                rep = P.run_cell(zz, frac(h), S0, 'o%03d-h%.3g%s'
                                 % (i, h, '-off' if off else ''), sweep_cap=0)
                rec = {'job': 'J2', 'opt': i, 'h': h, 'offset': off,
                       's': o['s'], 'sigma': float(zz[33]),
                       'Delta': float(zz[33]) - S0F,
                       'n_axis_aligned': o['n_axis_aligned'],
                       'n_contacts': (o['contacts']['n_pair_contacts']
                                      + o['contacts']['n_wall_contacts']),
                       'wall_secs': time.time() - t0}
                rec.update(rep)
                P.jl(path, rec)
        if i % 20 == 0:
            print('  optimum %d/%d' % (i, len(opt)), flush=True)


def bin_of(D):
    for a, b in ((0.01, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.3),
                 (0.3, float('inf'))):
        if a <= D < b:
            return '[%g,%g)' % (a, b)
    return '<0.01' if D < 0.01 else '?'


def cmd_j2sum():
    p = os.path.join(RESULTS, 'j2_survey.jsonl')
    rows = [json.loads(ln) for ln in open(p)]
    by_h = {}
    by_bin = {}
    for r in rows:
        by_h.setdefault(r['h'], {}).setdefault(r['verdict'], 0)
        by_h[r['h']][r['verdict']] += 1
        b = bin_of(r['Delta'])
        by_bin.setdefault(b, {}).setdefault(r['verdict'], 0)
        by_bin[b][r['verdict']] += 1
    # largest h killed per optimum (centred cells only)
    per = {}
    for r in rows:
        if r['offset']:
            continue
        per.setdefault(r['opt'], []).append(r)
    hstar = {}
    for k, rs in per.items():
        rs.sort(key=lambda q: -q['h'])
        killed = [q for q in rs if q['verdict'] != 'alive']
        if killed:
            hstar[k] = {'h': killed[0]['h'], 'reason': killed[0]['verdict'],
                        'Delta': killed[0]['Delta']}
    ratios = sorted(v['h'] / v['Delta'] for v in hstar.values())
    reasonmix = {}
    for v in hstar.values():
        reasonmix[v['reason']] = reasonmix.get(v['reason'], 0) + 1
    # the key number: among cells NOT killed by a-sigma, fraction killed by b or c1
    nz = [r for r in rows if r['verdict'] != 'a-sigma']
    nz_kill = [r for r in nz if r['verdict'] in ('b', 'c1-union')]
    nz_a = [r for r in nz if r['verdict'] in ('a', 'a-menu')]
    nz_alive = [r for r in nz if r['verdict'] == 'alive']
    # per h
    keynum = {}
    for h in sorted(set(r['h'] for r in rows)):
        sub = [r for r in rows if r['h'] == h and r['verdict'] != 'a-sigma']
        k = [r for r in sub if r['verdict'] in ('b', 'c1-union')]
        keynum[str(h)] = {'n_sigma_ok': len(sub), 'n_b_or_c1': len(k),
                          'frac': (len(k) / len(sub)) if sub else None}
    tsum = {}
    tn = {}
    for r in rows:
        tsum[r['verdict']] = tsum.get(r['verdict'], 0.0) + r.get('t_total', 0.0)
        tn[r['verdict']] = tn.get(r['verdict'], 0) + 1
    cost = {k: {'n': tn[k], 'mean_secs': tsum[k] / tn[k]} for k in tn}
    out = {'n_rows': len(rows), 'by_h': by_h, 'by_delta_bin': by_bin,
           'hstar_n': len(hstar), 'hstar_reason_mix': reasonmix,
           'hstar_over_Delta': {
               'median': ratios[len(ratios) // 2] if ratios else None,
               'min': ratios[0] if ratios else None,
               'max': ratios[-1] if ratios else None},
           'key_number_overall': {
               'n_sigma_ok': len(nz), 'n_b_or_c1': len(nz_kill),
               'n_a_or_amenu': len(nz_a), 'n_alive': len(nz_alive),
               'frac_b_or_c1': (len(nz_kill) / len(nz)) if nz else None},
           'key_number_by_h': keynum,
           'cost_by_verdict': cost}
    json.dump(out, open(os.path.join(RESULTS, 'j2_summary.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1)[:4000])


# ------------------------------------------------------------------ J3

def active_rows_at_point(z, tol=1e-6):
    """Active rows at the exact point: |value| <= tol.

    Wall rows, plus for every pair whose SAT gap is <= tol the straddling rows
    of the FIRST selection consistent at the point (all rows >= -tol).
    """
    pt = [T._to_iv(x) for x in z]
    ab = T.test_ab(pt)
    info = {'point_infeasible': ab['infeasible'], 'point_reason': ab['reason']}
    if ab['infeasible']:
        info['min_gap'] = ab.get('min_gap')
        return None, info
    info['min_gap'] = ab['min_gap']
    info['min_clear'] = ab['min_clear']
    rows = []
    for i in range(11):
        for c in range(4):
            for w in T.WALLS:
                r = T.wall_row(i, c, w)
                if abs(float(T.row_value(pt, r).a)) <= tol:
                    rows.append(r)
    info['n_wall_active'] = len(rows)
    contact_pairs = [p for p, v in ab['pairs'].items() if v[1] <= tol]
    info['n_contact_pairs'] = len(contact_pairs)
    nsel = 0
    n_nosel = 0
    for (i, j) in sorted(contact_pairs):
        got = False
        for o, p in ((i, j), (j, i)):
            if got:
                break
            for e in range(4):
                if got:
                    break
                for k in range(4):
                    rr = [T.sep_row(o, e, p, k)] + [T.dom_row(o, e, p, k, m)
                                                    for m in range(4) if m != k]
                    vals = [T.row_value(pt, r) for r in rr]
                    if all(float(v.a) >= -tol for v in vals):
                        add = [r for r, v in zip(rr, vals)
                               if abs(float(v.a)) <= tol]
                        rows += add
                        nsel += len(add)
                        got = True
                        break
        if not got:
            n_nosel += 1
    info['n_sel_active'] = nsel
    info['n_pairs_no_consistent_selection'] = n_nosel
    return rows, info


def cmd_j3():
    opt, _ = load_optima()
    low = [(i, o) for i, o in enumerate(opt) if o['s'] < 3.9]
    refs = references()
    r6 = [r for r in refs if r['tag'] == 'r6'][0]
    items = [('o%03d' % i, conf_of(o), o) for i, o in low]
    items.append(('r6', r6['z'], None))
    out = []
    for tag, z, o in items:
        t0 = time.time()
        rec = {'tag': tag, 'sigma': float(z[33]),
               'Delta': float(z[33]) - S0F}
        if o is not None:
            rec['s_cp85'] = o['s']
            rec['n_axis_aligned'] = o['n_axis_aligned']
            rec['n_pair_contacts'] = o['contacts']['n_pair_contacts']
            rec['n_wall_contacts'] = o['contacts']['n_wall_contacts']
        rows, info = active_rows_at_point(z)
        rec.update(info)
        if rows is not None and len(rows) == 0:
            rec['m_active'] = 0
            rec['note'] = 'no active row within tol'
            rows = None
        if rows is not None:
            pt = [T._to_iv(x) for x in z]
            A = P.grad_matrix(pt, rows)
            rec['m_active'] = len(rows)
            mu = P.fj_multipliers(A)
            rec['grad_rank'] = mu.get('rank')
            rec['fj_feasible'] = mu['feasible']
            rec['fj_min_lam'] = mu.get('t')
            rec['fj_support'] = mu.get('support')
            rec['fj_poly_dim'] = mu.get('poly_dim')
            rec['lam0_zero_branch'] = P.fj_lam0_zero(A)
            touched = set()
            for r in rows:
                if r['kind'] == 'wall':
                    touched.add(r['i'])
                else:
                    touched.add(r['o']); touched.add(r['p'])
            rec['n_rattlers'] = 11 - len(touched)
            rec['rattlers'] = sorted(set(range(11)) - touched)
            A33 = A[:, :33]
            rk33 = int(np.linalg.matrix_rank(A33, tol=1e-9)) if len(rows) else 0
            rec['rank_33'] = rk33
            rec['flat_dim_33'] = 33 - rk33
            # Krawczyk 'compl' probe, half-width 1e-4, lam radius 1e-3
            if mu['feasible']:
                b = P.build_cell(z, frac(1e-4), S0)
                if b is None:
                    rec['krawczyk'] = {'skipped': 'a-sigma at h=1e-4'}
                else:
                    lam = np.array(mu['lam']); zz = 1.0 + lam.sum()
                    lamn = lam / zz; lam0n = 1.0 / zz
                    lb = [iv.mpf([float(v) - 1e-3, float(v) + 1e-3]) for v in lamn]
                    l0 = iv.mpf([lam0n - 1e-3, lam0n + 1e-3])
                    kc = T.krawczyk_fj(b, rows, l0, lb, mode='compl')
                    rec['krawczyk'] = {'n': kc['n'], 'singular': kc['singular'],
                                       'cond': kc['cond'],
                                       'excluded': kc['excluded'],
                                       'isolated': kc['isolated'],
                                       'ratio': kc.get('ratio'),
                                       'secs': kc['secs']}
            else:
                rec['krawczyk'] = {'skipped': 'FJ infeasible'}
        # h = 1e-3 cell sweep
        rep = P.run_cell(z, frac(1e-3), S0, tag + '-h1e-3', sweep_cap=3000)
        sw = rep.get('sweep')
        rec['h1e3_verdict'] = rep['verdict']
        rec['h1e3_menu_log2'] = rep.get('menu_log2')
        if sw:
            rec['h1e3_sweep'] = {'tested': sw['n_tested'], 'alive': sw['n_alive'],
                                 'complete': sw['complete'],
                                 'total': sw['menu_total'],
                                 'secs_per_selection': sw['secs_per_selection']}
            rec['h1e3_sweep_class'] = ('0-alive' if sw['n_alive'] == 0 and sw['complete']
                                       else ('0-alive-capped' if sw['n_alive'] == 0
                                             else ('all-alive'
                                                   if sw['n_alive'] == sw['n_tested']
                                                   else 'partial')))
        elif rep.get('sweep_skipped'):
            rec['h1e3_sweep_class'] = 'skipped(' + rep['sweep_skipped'] + ')'
        else:
            rec['h1e3_sweep_class'] = 'n/a (' + rep['verdict'] + ')'
        # supplementary: smallest ladder h whose cell is NOT a-sigma
        hmin = None
        for h in sorted(H_LADDER):
            if P.build_cell(z, frac(h), S0) is not None:
                hmin = h
                break
        rec['h_min_non_sigma'] = hmin
        if hmin is not None:
            r2 = P.run_cell(z, frac(hmin), S0, tag + '-hmin', sweep_cap=3000)
            s2 = r2.get('sweep')
            rec['hmin_verdict'] = r2['verdict']
            rec['hmin_menu_log2'] = r2.get('menu_log2')
            if s2:
                rec['hmin_sweep'] = {'tested': s2['n_tested'],
                                     'alive': s2['n_alive'],
                                     'complete': s2['complete'],
                                     'total': s2['menu_total'],
                                     'secs_per_selection': s2['secs_per_selection']}
                rec['hmin_sweep_class'] = (
                    '0-alive' if s2['n_alive'] == 0 and s2['complete'] else
                    ('0-alive-capped' if s2['n_alive'] == 0 else
                     ('all-alive' if s2['n_alive'] == s2['n_tested'] else 'partial')))
            elif r2.get('sweep_skipped'):
                rec['hmin_sweep_class'] = 'skipped(' + r2['sweep_skipped'] + ')'
            else:
                rec['hmin_sweep_class'] = 'n/a (' + r2['verdict'] + ')'
        rec['wall_secs'] = time.time() - t0
        out.append(rec)
        P.jl('j3_degeneracy.jsonl', rec)
        print('  %-6s rank=%s flat=%s rat=%s fj=%s h1e3=%s' %
              (tag, rec.get('grad_rank'), rec.get('flat_dim_33'),
               rec.get('n_rattlers'), rec.get('fj_feasible'),
               rec.get('h1e3_verdict')), flush=True)
    json.dump(out, open(os.path.join(RESULTS, 'j3_degeneracy.json'), 'w'),
              indent=1, default=str)


# ------------------------------------------------------------------ J4

def cmd_j4():
    j2 = json.load(open(os.path.join(RESULTS, 'j2_summary.json')))
    hmed = j2['hstar_over_Delta']['median']
    # h*_median from J2 = median of the largest h killed
    p = os.path.join(RESULTS, 'j2_survey.jsonl')
    rows = [json.loads(ln) for ln in open(p) if ln.strip()]
    per = {}
    for r in rows:
        if r['offset']:
            continue
        per.setdefault(r['opt'], []).append(r)
    hs = []
    for k, rs in per.items():
        rs.sort(key=lambda q: -q['h'])
        kk = [q for q in rs if q['verdict'] != 'alive']
        if kk:
            hs.append(kk[0]['h'])
    hs.sort()
    h_med = hs[len(hs) // 2] if hs else None
    cost = j2['cost_by_verdict']
    n_all = sum(v['n'] for v in cost.values())
    cheap_mean = sum(v['n'] * v['mean_secs'] for v in cost.values()) / n_all
    # cheap-path cost on cells that actually reach the LP (not a-sigma)
    nz = {k: v for k, v in cost.items() if k != 'a-sigma'}
    cheap_nz = (sum(v['n'] * v['mean_secs'] for v in nz.values())
                / max(1, sum(v['n'] for v in nz.values())))
    # sweep cost per cell from J1
    j1 = [json.loads(ln) for ln in
          open(os.path.join(RESULTS, 'j1_ladder.jsonl')) if ln.strip()]
    sw = [r['sweep'] for r in j1 if r.get('sweep')]
    sps = [s['secs_per_selection'] for s in sw if s['secs_per_selection']]
    sps_med = sorted(sps)[len(sps) // 2] if sps else None
    sweep_cell = [r['t_total'] for r in j1 if r.get('sweep')]
    sweep_cell_med = (sorted(sweep_cell)[len(sweep_cell) // 2]
                      if sweep_cell else None)

    sym = 8 * math.factorial(11)
    h = h_med

    def log10_uniform(hh):
        # centres in [0,s0]^2 per square, theta in [0, pi/2)
        n_c = math.log10(S0F / (2 * hh)) * 22
        n_t = math.log10((math.pi / 2) / (2 * hh)) * 11
        return n_c + n_t - math.log10(sym)

    def cells_for_box(radius, hh):
        return max(1.0, (radius / hh) ** 33)

    out = {'h_star_median_from_J2': h_med,
           'h_star_censored_at_ladder_top': sum(1 for x in hs if x >= 0.05),
           'h_star_n': len(hs),
           'h_star_over_Delta_median': hmed,
           'cheap_path_mean_secs_all_cells': cheap_mean,
           'cheap_path_mean_secs_sigma_ok_cells': cheap_nz,
           'sweep_secs_per_selection_median': sps_med,
           'sweep_cell_total_secs_median': sweep_cell_med,
           'symmetry_divisor': sym}
    out['i_uniform_cover_log10'] = {
        'h=%g' % h: log10_uniform(h),
        'h=0.01': log10_uniform(0.01),
        'h=0.001': log10_uniform(0.001)}
    for name, radius in (('ii_A85_landing_box_r1.6e-3', 1.6e-3),
                         ('iii_ghost_drain_box_r5e-3', 5e-3)):
        rows_ = {}
        for hh in (h, 1e-3, 1.75e-4, 1e-4):
            n = cells_for_box(radius, hh)
            rows_['h=%g' % hh] = {
                'n_cells_log10': math.log10(n),
                'cpu_hours_cheap_log10': math.log10(n * cheap_nz / 3600.0),
                'cpu_hours_sweep_log10': (math.log10(n * sweep_cell_med / 3600.0)
                                          if sweep_cell_med else None),
                'covering_cell_excluded_by_T3': False}
        out[name] = {'radius': radius, 'grid': rows_,
                     'note': ('h*=%g exceeds the box radius, so one cell covers '
                              'the box; but NO measured h excludes a cell whose '
                              'sigma_min <= s0, so the box is not discharged at '
                              'any h in the ladder' % h)}
    A85_LP_NODE = 1700.0
    out['v_ratio_cheap_cell_to_A85_LP_node'] = cheap_nz / A85_LP_NODE
    out['A85_LP_node_secs'] = A85_LP_NODE
    a30 = json.load(open(os.path.join(ROOT, '..', 'A30-t3-pilot', 'results',
                                      'pilot_report.json')))
    out['A30_reference'] = {
        'cost_per_cell_secs': a30['findings']['cost_per_cell_secs'],
        'cell_count_model': a30['findings']['cell_count_model']}
    json.dump(out, open(os.path.join(RESULTS, 'j4_projection.json'), 'w'),
              indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:5000])


CMDS = {'probe': cmd_probe, 'j1': cmd_j1, 'j2': cmd_j2, 'j2sum': cmd_j2sum,
        'j3': cmd_j3, 'j4': cmd_j4}

if __name__ == '__main__':
    for c in sys.argv[1:]:
        print('=== %s ===' % c, flush=True)
        t0 = time.time()
        CMDS[c]()
        print('=== %s done in %.1f s ===' % (c, time.time() - t0), flush=True)
