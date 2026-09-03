"""Emit notes/pilot_report.md from results/*.jsonl (tables only)."""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_v] = '1'
import json
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, 'results')
L = []


def w(s=''):
    L.append(s)


def jl(n):
    return [json.loads(x) for x in open(os.path.join(R, n)) if x.strip()]


j1 = jl('j1_ladder.jsonl')
j2 = jl('j2_survey.jsonl')
j3 = json.load(open(os.path.join(R, 'j3_degeneracy.json')))
j2s = json.load(open(os.path.join(R, 'j2_summary.json')))
j4 = json.load(open(os.path.join(R, 'j4_projection.json')))
H = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 5e-4, 2e-4, 1e-4]
HX = [1e-5, 1e-6, 1e-7, 3e-8, 1e-8]

w('# A87 H1 pilot report')
w()
w('Engine: `code/t3lib.py` (A30 verbatim, two data paths repointed) + `code/pilot87.py`.')
w('`code/selftest30.py`: **ALL PASS, 7/7** (incl. 3 corruption gates + adversarial sampling)'
  ' -- `logs/selftest.log`.  s0 = 969271/250000 = 3.877084; every cell s-box = [sigma_min(cell), s0].')
w()

# ---------------------------------------------------------- per-cell costs
w('## 1. Per-cell cost (measured, single process, BLAS pinned)')
w()
w('| stage | secs/cell | n | A30 reference |')
w('|---|---|---|---|')
a30 = j4['A30_reference']['cost_per_cell_secs']
alive = [r for r in j1 + j2 if r['verdict'] != 'a-sigma']


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else None


w('| build_cell + clip_s only (verdict a-sigma) | %.4f | %d | -- |'
  % (mean([r['t_total'] for r in j1 + j2 if r['verdict'] == 'a-sigma']),
     sum(1 for r in j1 + j2 if r['verdict'] == 'a-sigma')))
w('| test_ab (a)+(b) | %.4f | %d | %.2f |'
  % (mean([r['t_ab'] for r in alive]), len(alive), a30['a_and_b']))
w('| build_menu | %.4f | %d | %.2f |'
  % (mean([r.get('t_menu') for r in alive]),
     sum(1 for r in alive if r.get('t_menu') is not None), a30['menu_build']))
w('| union Farkas LP | %.4f | %d | %.3f |'
  % (mean([r.get('t_farkas_lp') for r in alive]),
     sum(1 for r in alive if r.get('t_farkas_lp') is not None),
     a30['union_farkas_lp']))
w('| **cheap path total** (a/b/menu/c1-union) | **%.3f** | %d | %.2f |'
  % (mean([r['t_total'] - (r.get('sweep', {}) or {}).get('t_sweep', 0.0)
           - (r.get('sweep', {}) or {}).get('t_cache', 0.0) for r in alive]),
     len(alive), a30['cheap_path_total']))
sw = [r['sweep'] for r in j1 + [x for x in j3 if x.get('hmin_sweep')]
      if isinstance(r, dict) and r.get('sweep')]
sps = [s['secs_per_selection'] for s in sw]
w('| per-selection Farkas (sweep) | %.5f | %d selections | %.4f |'
  % (med(sps), sum(s['n_tested'] for s in sw), a30['per_selection_farkas']))
w('| sweep cell total (cap 3000 selections) | %.2f | %d | -- |'
  % (med([r['t_total'] for r in j1 if r.get('sweep')]),
     sum(1 for r in j1 if r.get('sweep'))))
w()
w('Mean per-cell cost over the whole J2 survey (1380 cells, a-sigma-dominated): '
  '**%.4f s**; over sigma-feasible cells only (74): **%.3f s**.'
  % (j4['cheap_path_mean_secs_all_cells'],
     j4['cheap_path_mean_secs_sigma_ok_cells']))
w()

# ---------------------------------------------------------------- J1 ladder
w('## 2. J1 -- discharge-scale ladder h*(Delta)  (`results/j1_ladder.jsonl`)')
w()
cfgs = []
for tag in ('r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7'):
    rs = [r for r in j1 if r['config'] == tag]
    if rs:
        cfgs.append((tag, rs))
w('| cfg | description | sigma | Delta = sigma - s0 | contacts | ' +
  ' | '.join('h=%g' % h for h in H) + ' |')
w('|---|---|---|---|---|' + '---|' * len(H))
CODE = {'a-sigma': 'A-s', 'a': 'A', 'a-menu': 'A-m', 'b': 'B',
        'c1-union': 'C1u', 'c1-sweep': 'C1s', 'alive': '.'}
for tag, rs in cfgs:
    d = {r['h']: r['verdict'] for r in rs}
    r0 = rs[0]
    w('| %s | %s | %.9f | %+.4e | %s | %s |'
      % (tag, r0['desc'], r0['sigma'], r0['Delta'],
         r0['n_contacts'] if r0['n_contacts'] is not None else '-',
         ' | '.join(CODE.get(d.get(h), '-') for h in H)))
w()
w('Legend: `A-s` = a-sigma (sigma_min(cell) > s0), `A` = interval infeasible, '
  '`A-m` = empty selection menu, `B` = D2 slack, `C1u` = union Farkas, '
  '`C1s` = complete per-selection sweep 0-alive, `.` = alive.')
w()
w('r7 extension (Delta < 0, the rotational ghost):')
w()
w('| cfg | ' + ' | '.join('h=%g' % h for h in HX) + ' |')
w('|---|' + '---|' * len(HX))
d7 = {r['h']: r['verdict'] for r in j1 if r['config'] == 'r7'}
w('| r7 | ' + ' | '.join(CODE.get(d7.get(h), '-') for h in HX) + ' |')
w()
w('| cfg | Delta | h* (largest h excluded) | by test | h*/Delta | sweep at largest alive h |')
w('|---|---|---|---|---|---|')
for tag, rs in cfgs:
    kk = sorted([r for r in rs if r['verdict'] != 'alive'],
                key=lambda q: -q['h'])
    hs = '--' if not kk else '%g' % kk[0]['h']
    by = '--' if not kk else kk[0]['verdict']
    ratio = ('--' if (not kk or rs[0]['Delta'] <= 0)
             else '%.3f' % (kk[0]['h'] / rs[0]['Delta']))
    swr = [r for r in rs if r.get('sweep')]
    swr.sort(key=lambda q: -q['h'])
    if swr:
        s = swr[0]['sweep']
        sd = ('h=%g: %d/%s tested, %d alive (%s)'
              % (swr[0]['h'], s['n_tested'],
                 ('2^%.0f' % math.log2(s['menu_total'])
                  if s['menu_total'] > 1e6 else s['menu_total']),
                 s['n_alive'], 'complete' if s['complete'] else 'capped'))
    else:
        sd = 'sweep skipped (menu_log2 > 40)' if any(
            r.get('sweep_skipped') for r in rs) else '--'
    w('| %s | %+.4e | %s | %s | %s | %s |'
      % (tag, rs[0]['Delta'], hs, by, ratio, sd))
w()

# --------------------------------------------------------------------- J2
w('## 3. J2 -- near-feasible survey, 262 optima x 5 h (+14 offset cells) = %d cells'
  % j2s['n_rows'])
w('(`results/j2_survey.jsonl`, `results/j2_summary.json`)')
w()
w('### 3a. Verdict counts by h')
w()
verd = ['a', 'a-menu', 'a-sigma', 'b', 'c1-union', 'alive']
w('| h | ' + ' | '.join(verd) + ' | total |')
w('|---|' + '---|' * (len(verd) + 1))
for h in sorted(j2s['by_h'], key=float, reverse=True):
    row = j2s['by_h'][h]
    w('| %s | %s | %d |' % (h, ' | '.join(str(row.get(v, 0)) for v in verd),
                            sum(row.values())))
w()
w('### 3b. Verdict counts by Delta-bin')
w()
w('| Delta bin | ' + ' | '.join(verd) + ' | total |')
w('|---|' + '---|' * (len(verd) + 1))
for b in ('[0.01,0.02)', '[0.02,0.05)', '[0.05,0.1)', '[0.1,0.3)', '[0.3,inf)'):
    row = j2s['by_delta_bin'].get(b, {})
    w('| %s | %s | %d |' % (b, ' | '.join(str(row.get(v, 0)) for v in verd),
                            sum(row.values())))
w()
w('### 3c. Key number -- "excluded with no FJ solve" rate')
w()
k = j2s['key_number_overall']
w('| quantity | value |')
w('|---|---|')
w('| cells with sigma_min(cell) <= s0 (NOT killed by a-sigma) | %d / %d |'
  % (k['n_sigma_ok'], j2s['n_rows']))
w('| of those, killed by (b) or (c1-union) | **%d  (%.1f%%)** |'
  % (k['n_b_or_c1'], 100 * k['frac_b_or_c1']))
w('| of those, killed by (a) or (a-menu) | %d |' % k['n_a_or_amenu'])
w('| of those, alive after the whole cheap path | **%d (100%%)** |' % k['n_alive'])
w()
w('| h | sigma-feasible cells | killed by (b)/(c1-union) | rate |')
w('|---|---|---|---|')
for h in sorted(j2s['key_number_by_h'], key=float, reverse=True):
    v = j2s['key_number_by_h'][h]
    w('| %s | %d | %d | %s |' % (h, v['n_sigma_ok'], v['n_b_or_c1'],
                                 '--' if v['frac'] is None else '%.1f%%'
                                 % (100 * v['frac'])))
w()
w('### 3d. h* vs Delta (largest h at which the centred cell is excluded)')
w()
per = {}
for r in j2:
    if r['offset']:
        continue
    per.setdefault(r['opt'], []).append(r)
rows = []
for kk, rs in per.items():
    rs.sort(key=lambda q: -q['h'])
    ok = [q for q in rs if q['verdict'] != 'alive']
    if ok:
        rows.append((ok[0]['Delta'], ok[0]['h'], ok[0]['verdict']))
BINS = [(0.01, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.3), (0.3, 1e9)]
w('| Delta bin | n | h* median | h*/Delta median | h*/Delta min | h*/Delta max | reason |')
w('|---|---|---|---|---|---|---|')
for a, b in BINS:
    sub = [x for x in rows if a <= x[0] < b]
    if not sub:
        continue
    rr = sorted(x[1] / x[0] for x in sub)
    hh = sorted(x[1] for x in sub)
    reasons = sorted(set(x[2] for x in sub))
    w('| [%g,%g) | %d | %g | %.3f | %.3f | %.3f | %s |'
      % (a, b, len(sub), hh[len(hh) // 2], rr[len(rr) // 2], rr[0], rr[-1],
         ','.join(reasons)))
unc = [x for x in rows if x[1] < 0.05]
rr = sorted(x[1] / x[0] for x in unc)
w()
w('All 262: h*/Delta median %.3f, min %.3f, max %.3f; reason mix %s.  '
  '%d of 262 are CENSORED at the ladder top (h* = 0.05 = largest h tested).'
  % (j2s['hstar_over_Delta']['median'], j2s['hstar_over_Delta']['min'],
     j2s['hstar_over_Delta']['max'], j2s['hstar_reason_mix'],
     j4['h_star_censored_at_ladder_top']))
w('Uncensored subset (h* < 0.05, n = %d): h*/Delta median %.3f, min %.3f, max %.3f.'
  % (len(unc), rr[len(rr) // 2], rr[0], rr[-1]))
w()
off = [r for r in j2 if r['offset']]
offv = {}
for r in off:
    offv[r['verdict']] = offv.get(r['verdict'], 0) + 1
w('Offset cells (14 optima with s < 3.9, +-h/2 per coordinate, rng 87, n = %d): %s.'
  % (len(off), offv))
w()

# --------------------------------------------------------------------- J3
w('## 4. J3 -- FJ degeneracy at the under-contacted k0 optima (`results/j3_degeneracy.json`)')
w()
w('| id | sigma | Delta | pair/wall contacts (cp85) | m active rows | grad rank | rank on 33 cfg coords | flat dim | rattlers | FJ multipliers feasible | lam0=0 branch | Krawczyk compl (h=1e-4, lam-rad 1e-3) |')
w('|---|---|---|---|---|---|---|---|---|---|---|---|')
for r in j3:
    kw = r.get('krawczyk') or {}
    if 'skipped' in kw:
        ks = kw['skipped']
    else:
        ks = ('n=%d, singular=%s, cond=%.2e, excluded=%s'
              % (kw['n'], kw['singular'], kw['cond'], kw['excluded']))
    w('| %s | %.7f | %.4e | %s/%s | %s | %s | %s | %s | %s | %s | %s | %s |'
      % (r['tag'], r['sigma'], r['Delta'],
         r.get('n_pair_contacts', '-'), r.get('n_wall_contacts', '-'),
         r.get('m_active', '-'), r.get('grad_rank', '-'), r.get('rank_33', '-'),
         r.get('flat_dim_33', '-'), r.get('n_rattlers', '-'),
         r.get('fj_feasible', '-'), r.get('lam0_zero_branch', '-'), ks))
w()
w('| id | h=1e-3 cell verdict | sweep class at h=1e-3 | smallest non-a-sigma h | verdict there | menu log2 | sweep (cap 3000) |')
w('|---|---|---|---|---|---|---|')
for r in j3:
    s = r.get('hmin_sweep')
    sd = ('%d tested / 2^%.0f, %d alive (%s)'
          % (s['tested'], math.log2(s['total']), s['alive'],
             'complete' if s['complete'] else 'capped')) if s else \
        r.get('hmin_sweep_class', '--')
    w('| %s | %s | %s | %s | %s | %s | %s |'
      % (r['tag'], r['h1e3_verdict'], r['h1e3_sweep_class'],
         r.get('h_min_non_sigma', '-'), r.get('hmin_verdict', '-'),
         ('%.1f' % r['hmin_menu_log2']) if r.get('hmin_menu_log2') else '-', sd))
w()

# --------------------------------------------------------------------- J4
w('## 5. J4 -- projections (computed from the measured costs; `results/j4_projection.json`)')
w()
w('Inputs: h*_median (J2) = %g (censored: %d/%d optima sit at the ladder top); '
  'cheap-path cost = %.3f s/cell on sigma-feasible cells, %.4f s/cell averaged '
  'over the survey; sweep cell = %.2f s (cap 3000, %.5f s/selection); '
  'symmetry divisor 8*11! = %d.'
  % (j4['h_star_median_from_J2'], j4['h_star_censored_at_ladder_top'],
     j4['h_star_n'], j4['cheap_path_mean_secs_sigma_ok_cells'],
     j4['cheap_path_mean_secs_all_cells'], j4['sweep_cell_total_secs_median'],
     j4['sweep_secs_per_selection_median'], j4['symmetry_divisor']))
w()
w('### (i) uniform 33-dim cover of D0, centres in [0,s0]^2, theta in [0,pi/2), / 8*11!')
w()
w('| h | cells | A30 reference |')
w('|---|---|---|')
a30c = j4['A30_reference']['cell_count_model']['uniform_cover']
for k2, v in sorted(j4['i_uniform_cover_log10'].items(),
                    key=lambda q: -float(q[0].split('=')[1])):
    w('| %s | 1e%.1f | %s |' % (k2.split('=')[1], v,
                                a30c.get(k2.replace('h=', 'h='), '--')))
w()
w('A30 (same model): h=0.1 -> 1e30, h=0.01 -> 1e63, h=5e-4 -> 1e106, h=1.75e-4 -> 1e121.')
w()
w('### (ii)/(iii) cells to cover one box, and CPU-h')
w()
w('| target | radius | h | cells | CPU-h cheap path | CPU-h with sweep | cell discharged by T3? |')
w('|---|---|---|---|---|---|---|')
for name, lab in (('ii_A85_landing_box_r1.6e-3', 'A85 landing box'),
                  ('iii_ghost_drain_box_r5e-3', 'ghost drain box')):
    b = j4[name]
    for hk in ('h=0.05', 'h=0.001', 'h=0.000175', 'h=0.0001'):
        g = b['grid'][hk]
        w('| %s | %g | %s | 1e%.1f | 1e%.1f | 1e%.1f | NO |'
          % (lab, b['radius'], hk.split('=')[1], g['n_cells_log10'],
             g['cpu_hours_cheap_log10'], g['cpu_hours_sweep_log10']))
w()
w('At h = h*_median = 0.05 one cell covers either box, but that cell is NOT '
  'discharged by any T3 test (J1/J2: no sigma-feasible cell was ever killed), '
  'so the CPU-h entries at h=0.05 are the cost of a test that returns "alive".')
w()
w('### (v) cost ratio to A85')
w()
w('| quantity | value |')
w('|---|---|')
w('| A87 cheap-path cell (sigma-feasible) | %.3f s |'
  % j4['cheap_path_mean_secs_sigma_ok_cells'])
w('| A85 measured LP node | %.0f s |' % j4['A85_LP_node_secs'])
w('| ratio A87 cell / A85 LP node | **%.2e** (1 LP node = %.0f cheap cells) |'
  % (j4['v_ratio_cheap_cell_to_A85_LP_node'],
     1.0 / j4['v_ratio_cheap_cell_to_A85_LP_node']))
w('| A30 floor, cheap path only | 1.1e5 CPU-h |')
w('| A30 floor, per-selection sweep | 4.9e7 CPU-h |')
w()

nsw = [r for r in j1 if r.get('sweep')] + [r for r in j3 if r.get('hmin_sweep')]
tot_sel = (sum(r['sweep']['n_tested'] for r in j1 if r.get('sweep'))
           + sum(r['hmin_sweep']['tested'] for r in j3 if r.get('hmin_sweep')))
w('## 6. Findings (measured)')
w()
w('1. Every excluded cell in the pilot was excluded by **a-sigma** '
  '(sigma_min(cell) > s0): 1351 of 1448 cells; (b) D2-slack fired 0 times, '
  '(c1) union-Farkas 0 times, (a)/(a-menu) 0 times.  Of the 74 J2 cells with '
  'sigma_min <= s0, **0 (0.0%) were killed by (b) or (c1-union)** -- the '
  '"excluded with no FJ solve" rate is 0, not high.')
w('2. h* is linear in Delta and is a pure s-clip effect: h*/Delta = 0.465 '
  'median (0.350-0.496) on the 17 optima whose h* is uncensored, i.e. '
  'h* ~ Delta/2.15; 245/262 optima are censored at the ladder top h = 0.05.  '
  'For Delta <= 0 (r7, the rotational ghost at sigma = s0 - 2.2e-7) NO h down '
  'to 1e-8 excludes the cell.')
w('3. The per-selection Farkas sweep killed nothing: %d selections over %d '
  'cells, 3000-alive-of-3000 in every case, with menu sizes 2^16 - 2^34, so '
  'no sweep can complete (cap 3000).' % (tot_sel, len(nsw)))
w('4. FJ degeneracy at the under-contacted optima: 14 of 15 points admit **no '
  'feasible FJ multiplier** at tol 1e-6 (grad s is outside the cone of the '
  '19-27 active rows); rank on the 33 configuration coordinates is 17-23, so '
  'the flat dimension is 10-16, with 0-4 rattler squares.  Only o012 has FJ '
  'multipliers, and it also admits the lambda_0 = 0 branch.  Every h=1e-3 '
  'cell around these points is already a-sigma, so no Krawczyk/sweep verdict '
  'is reachable there.')
w('5. Cost: 0.813 s per sigma-feasible cell (A30: 0.50 s), 0.0147 s for an '
  'a-sigma cell, 0.0025 s per swept selection; the cheap-path cell is '
  '4.8e-4 of an A85 LP node (1 LP node = 2092 cells).  The uniform cover '
  'reproduces A30: 1e62.7 vs 1e63 at h = 0.01.')
w()

out = os.path.join(ROOT, 'notes', 'pilot_report.md')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
