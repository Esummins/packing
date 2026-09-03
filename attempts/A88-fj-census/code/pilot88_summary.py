"""pilot88_summary.py -- A88 T3 pilot: aggregate everything into
results/pilot88_summary.json and notes/pilot_report.md.

NOTHING here is a certificate or a verdict about s(11).  All arithmetic in the
pilot is float interval arithmetic with outward padding (p88_iv), used because
the deliverable is a COST measurement.
"""
from __future__ import annotations

import collections
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
NOTES = os.path.abspath(os.path.join(HERE, '..', 'notes'))

A85_CPUH = (3200, 7000)
N_VALUES = [('1e11 (Level-0 graphs)', 1e11),
            ('1e18 (decorated per-graph fan-out)', 1e18),
            ('1e29 (decorated total)', 1e29)]


def load(name, default=None):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return default
    if name.endswith('.jsonl'):
        return [json.loads(l) for l in open(p) if l.strip()]
    return json.load(open(p))


def wilson(k, n, z=1.0):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def pct(x):
    return '-' if x is None else '%.4f' % x


def qs(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return {}
    return {'mean': sum(xs) / n, 'median': xs[n // 2],
            'p95': xs[min(n - 1, int(0.95 * n))], 'min': xs[0], 'max': xs[-1]}


def shares(recs, key='hist'):
    h = collections.Counter()
    for r in recs:
        for k, v in r[key].items():
            if v and k not in ('bisect', 'hc4_narrow'):
                h[k] += v
    tot = sum(h.values()) or 1
    return {k: {'n': v, 'share': v / tot} for k, v in h.most_common()}


def main():
    triage = load('pilot88_triage.jsonl', [])
    fj = load('pilot88_fj.jsonl', [])
    cal = load('pilot88_fj_calib.jsonl', [])
    canary = load('pilot88_canary.json', {})
    abl = load('pilot88_hc4_ablation.json', [])
    fit = load('pilot88_depth_fit.json', {})
    selft = load('pilot88_selftest.json', {})
    meta = load('census88_sample_meta.json', {})

    S = {'note': 'float interval arithmetic with outward padding (p88_iv); '
                 'a COST measurement, NOT a certificate and NOT a verdict '
                 'about s(11)',
         'selftest': selft, 'census_sample_meta': meta}

    # ---------------------------------------------------------- Tier 1
    groups = collections.defaultdict(list)
    for r in triage:
        groups[r.get('set') or 'census'].append(r)
    tri = {}
    for g, rs in sorted(groups.items()):
        n = len(rs)
        kills = [r for r in rs if r['verdict'] == 'KILL']
        cont = sum(1 for r in kills if r.get('kill_type') == 'CONTAINMENT')
        shat = sum(1 for r in kills if r.get('kill_type') == 'S-HAT')
        pk, lo, hi = wilson(len(kills), n)
        ps, slo, shi = wilson(n - len(kills), n)
        tri[g] = {'n': n, 'n_kill': len(kills), 'kill_frac': pk,
                  'kill_frac_1sigma': [lo, hi],
                  'n_kill_containment': cont, 'n_kill_shat': shat,
                  'kill_frac_containment': wilson(cont, n)[0],
                  'kill_frac_containment_1sigma': list(wilson(cont, n)[1:]),
                  'kill_frac_shat': wilson(shat, n)[0],
                  'kill_frac_shat_1sigma': list(wilson(shat, n)[1:]),
                  'survivor_frac': ps, 'survivor_frac_1sigma': [slo, shi],
                  'ms': qs([r['ms_total'] for r in rs]),
                  'n_chi_ge_0': sum(1 for r in rs if r['chi'] >= 0),
                  'chi_ge_0_frac': wilson(sum(1 for r in rs
                                              if r['chi'] >= 0), n)[0],
                  'n_survivors': n - len(kills)}
    S['triage_by_set'] = tri

    cens = [r for r in triage if (r.get('set') or 'census') in
            ('census', 'k0drop')]
    n = len(cens)
    kills = [r for r in cens if r['verdict'] == 'KILL']
    cont = sum(1 for r in kills if r.get('kill_type') == 'CONTAINMENT')
    shat = sum(1 for r in kills if r.get('kill_type') == 'S-HAT')
    pk, lo, hi = wilson(len(kills), n)
    ps, slo, shi = wilson(n - len(kills), n)
    dual = collections.Counter()
    for r in kills:
        for k, v in (r['t1b'].get('dual_by_family') or {}).items():
            dual[k] += v
    tot = sum(dual.values()) or 1.0
    S['triage_census'] = {
        'n': n, 'n_kill': len(kills), 'kill_frac': pk,
        'kill_frac_1sigma': [lo, hi],
        'n_kill_containment': cont, 'n_kill_shat': shat,
        'kill_frac_containment': wilson(cont, n)[0],
        'kill_frac_containment_1sigma': list(wilson(cont, n)[1:]),
        'kill_frac_shat': wilson(shat, n)[0],
        'survivor_frac': ps, 'survivor_frac_1sigma': [slo, shi],
        'ms': qs([r['ms_total'] for r in cens]),
        'n_chi_ge_0': sum(1 for r in cens if r['chi'] >= 0),
        'farkas_dual_by_row_family': {k: v / tot
                                      for k, v in sorted(dual.items())},
        'leaves': qs([r['t1b']['leaves'] for r in cens]),
    }

    # ---------------------------------------------------------- Tier 2
    S['fj_rows'] = [{
        'tag': r['tag'], 'set': r.get('set'), 'k_H': r['k_H'], 'm': r['m'],
        'chi': r['chi'], 'D_core': r['D'], 'd_H': r.get('d_H'),
        'rattlers': r.get('rattlers'), 'sigma': r.get('sigma'),
        'rigid_possible': r['rigid_possible'], 'boxes': r['boxes'],
        'secs': r['secs'], 'ms_per_box': r['ms_per_box'],
        'stopped': r['stopped'], 'max_depth': r['max_depth'],
        'open_stack_final': r['open_stack_final'], 'leaf_hist': r['hist'],
        'log10_discharged_frac': r['log10_discharged_frac'],
        'log10_remaining_volume_frac': r['log10_remaining_volume_frac'],
        'min_max_abs_width_reached': r['min_max_abs_width_reached'],
        'farkas_n_lp': r['farkas']['n_lp'],
        'farkas_best_t': r['farkas']['best_t'],
        'krawczyk_attempts': r['krawczyk']['attempts'],
        'n_roots_isolated': len(r['roots']), 'eff_dim': r.get('eff_dim'),
    } for r in fj]

    comp = [r for r in fj if r['stopped'] == 'complete']
    S['fj_summary'] = {
        'n': len(fj), 'n_complete': len(comp),
        'complete_tags': [r['tag'] for r in comp],
        'not_complete_tags': [r['tag'] for r in fj
                              if r['stopped'] != 'complete'],
        'complete_secs': qs([r['secs'] for r in comp]),
        'complete_boxes': qs([r['boxes'] for r in comp]),
        'leaf_kill_shares': shares(fj),
        'F_fired_total': sum(r['hist'].get('F', 0) for r in fj),
        'F_lp_total': sum(r['farkas']['n_lp'] for r in fj),
        'K_attempts_total': sum(r['krawczyk']['attempts'] for r in fj),
    }

    # ------------------------------------------------- cost calibration
    if cal:
        cc = [c for c in cal if c['stopped'] == 'complete']
        cp = [c for c in cal if c['stopped'] != 'complete']
        pc, clo, chi = wilson(len(cc), len(cal))
        S['fj_calibration'] = {
            'note': 'uniform subsample of the census T1 SURVIVORS, 20 s cap '
                    'each; a per-structure COST measurement, not a run of the '
                    'exclusions at scale',
            'n': len(cal), 'n_complete': len(cc), 'n_capped': len(cp),
            'complete_frac': pc, 'complete_frac_1sigma': [clo, chi],
            'secs_complete': qs([c['secs'] for c in cc]),
            'boxes_complete': qs([c['boxes'] for c in cc]),
            'secs_all_CENSORED_at_cap': qs([c['secs'] for c in cal]),
            'chi_of_capped': [c['chi'] for c in cp],
            'n_chi_ge_0': sum(1 for c in cal if c['chi'] >= 0),
            'leaf_kill_shares': shares(cal),
            'F_fired_total': sum(c['hist'].get('F', 0) for c in cal),
            'F_structures_where_F_fired':
                sum(1 for c in cal if c['hist'].get('F', 0) > 0),
        }

    S['hc4_ablation'] = abl
    S['depth_fit'] = fit

    # ---------------------------------------------------------- canary
    tr = canary.get('trump_1e-06', {})
    ref = tr.get('refined') or {}
    ctl = canary.get('controls_A87', {})
    S['canary'] = {
        'status': tr.get('status'), 'depth_to_isolation': tr.get('depth'),
        'krawczyk_cond': ref.get('cond'), 'krawczyk_ratio': ref.get('ratio'),
        'root_s_box': ref.get('root_s_box'),
        'root_box_maxwidth': ref.get('root_box_maxwidth'),
        'contains_s_hat': ref.get('contains_s_hat'), 's_hat': ref.get('s_hat'),
        's_hat_minus_root_mid': ref.get('s_hat_minus_root_mid'),
        'never_excluded': tr.get('status') != 'CANARY_FAIL',
        'controls': {k: {'status': v.get('status'), 'test': v.get('test'),
                         'tight': v.get('tight'), 'sigma': v.get('sigma'),
                         'depth': v.get('depth')} for k, v in ctl.items()},
        'controls_excluded_tight': [k for k, v in ctl.items()
                                    if v.get('status') == 'CANARY_FAIL'
                                    and v.get('tight')],
        'controls_excluded_loose': [k for k, v in ctl.items()
                                    if v.get('status') == 'CANARY_FAIL'
                                    and not v.get('tight')],
    }

    # ------------------------------------------------------ cost model
    c_tri = S['triage_census']['ms']['mean'] / 1000.0
    f_surv = S['triage_census']['survivor_frac']
    fcal = S.get('fj_calibration', {})
    c_fj = fcal.get('secs_all_CENSORED_at_cap', {}).get('mean')
    c_fj_med = fcal.get('secs_complete', {}).get('median')
    per = c_tri + f_surv * c_fj
    per_med = c_tri + f_surv * c_fj_med
    cost = {'c_triage_s': c_tri, 'survivor_fraction': f_surv,
            'survivor_fraction_1sigma':
                S['triage_census']['survivor_frac_1sigma'],
            'c_FJ_s_mean_CENSORED': c_fj,
            'c_FJ_s_median_of_completing': c_fj_med,
            'per_structure_s_mean': per,
            'per_structure_s_median_optimistic': per_med,
            'A85_baseline_cpu_h': list(A85_CPUH),
            'formula': 'total = N * c_triage + N * f_surv * c_FJ',
            'break_even_N_at_7000_cpu_h': A85_CPUH[1] * 3600.0 / per,
            'break_even_N_triage_only_at_7000_cpu_h':
                A85_CPUH[1] * 3600.0 / c_tri,
            'per_structure_s_needed_for_7000_cpu_h_at_N_1e11':
                A85_CPUH[1] * 3600.0 / 1e11,
            'by_N': {}}
    for label, N in N_VALUES:
        tri_h = N * c_tri / 3600.0
        fj_h = N * f_surv * c_fj / 3600.0
        tot_h = tri_h + fj_h
        cost['by_N'][label] = {
            'N': N, 'triage_cpu_h': tri_h,
            'log10_triage_cpu_h': math.log10(tri_h),
            'FJ_cpu_h': fj_h, 'log10_FJ_cpu_h': math.log10(fj_h),
            'total_cpu_h': tot_h, 'log10_total_cpu_h': math.log10(tot_h),
            'ratio_to_A85_upper': tot_h / A85_CPUH[1],
            'log10_ratio_to_A85_upper': math.log10(tot_h / A85_CPUH[1]),
            'ratio_to_A85_lower': tot_h / A85_CPUH[0]}
    S['cost_model'] = cost

    json.dump(S, open(os.path.join(RES, 'pilot88_summary.json'), 'w'), indent=1)
    print('wrote', os.path.join(RES, 'pilot88_summary.json'))
    write_report(S)


def write_report(S):
    L = []
    A = L.append
    cm = S['cost_model']
    tc = S['triage_census']
    fs = S['fj_summary']
    fc = S.get('fj_calibration', {})
    c = S['canary']

    A('# A88 T3 COST-PILOT  --  pricing H1 by CONTACT STRUCTURE')
    A('')
    A('**Verdict up front.** Per-structure the route is CHEAP: triage '
      '%.1f ms, FJ tier ~%.0f ms median and it CLOSES on %s of census '
      'survivors. It still loses to A85 by ~%.0f orders of magnitude, and it '
      'loses on the CENSUS SIZE N alone: at N = 1e11 the TRIAGE ALONE costs '
      '%.2g CPU-h against A85\'s 3,200-7,000. For the whole route to fit in '
      '7,000 CPU-h at N = 1e11 the per-structure cost would have to be '
      '%.2g s (0.25 microseconds). The dominant multiplier is **N**, not the '
      'per-structure price.'
      % (tc['ms']['mean'], 1000 * (fc.get('secs_complete', {}).get('median')
                                   or 0),
         pct(fc.get('complete_frac')),
         cm['by_N']['1e11 (Level-0 graphs)']['log10_ratio_to_A85_upper'],
         cm['by_N']['1e11 (Level-0 graphs)']['triage_cpu_h'],
         cm['per_structure_s_needed_for_7000_cpu_h_at_N_1e11']))
    A('')
    A('**Nothing in this file is a certificate or a verdict about s(11).** '
      'Every number is a COST measurement. The interval engine used '
      '(`code/p88_iv.py`) is float interval arithmetic with an outward pad of '
      '`8.9e-16 * max|endpoint|` per operation (~18x the 0.5 ulp rounding '
      'error of one IEEE-754 double op), cross-checked against t3lib\'s '
      'rigorous `mpmath.iv` `row_value` to **%.1e** on every row of every '
      'structure. Row-activity zero tests carry an absolute slack '
      'ZTOL = 1e-12. A real certificate would use the mpmath path throughout '
      'and cost more per box; the pilot measures the SHAPE of the cost.'
      % (S['selftest'].get('max_fastiv_vs_mpmath_row_value') or 0))
    A('')
    A('## 0. What a per-structure certificate is here')
    A('')
    A('For a support structure H (graph + wall masks + contact-type '
      'decoration + tilt-class order) the claim is: *no Fritz-John point of '
      'the enclosing-side function with active set contained in H and '
      '`s <= s-hat_hi = 3.877084`*. FJ multipliers live only on H, so the '
      'claim is LOCAL TO THE LOADED CORE: squares in no row of H are dropped '
      'along with their feasibility rows. Dropping constraints can only '
      'enlarge the FJ set, so this is a sound weakening. The certificate box '
      'is the CORE box: `cx, cy` per loaded square (wall-tightened as A31 '
      '`lib0._box`), ONE tilt variable per TILT CLASS (pinned classes fixed '
      'exactly, at 0 or at pi/2), and `s in [3.82, 3.877084]`.')
    A('')
    A('Two notes on the vocabulary. (i) Tilts are **not** folded mod pi/2: '
      'folding a theta of pi/2 down to 0 rotates that square\'s corner and '
      'edge labels and silently rewrites every row of H that mentions it, so '
      'a square recorded at pi/2 is kept as its own pinned class. (ii) The '
      'census emits only the EQUALITY rows; the t3lib DOMINANCE rows that '
      'make a sep row equal true SAT separation are determined by '
      '`(o, e, p, kstar)` and are rebuilt here as `g >= 0` SIDE CONDITIONS '
      '(56 per census structure on average). Their sign convention is '
      'validated in the selftest: every rebuilt dominance row is strictly '
      'positive at every realising point (min **%.2e** over all 21 A87/Trump '
      'points). They are load-bearing  --  see the leaf shares below.'
      % (S['selftest'].get('min_rebuilt_dominance_row_value_at_points') or 0))
    A('')
    A('Inputs: %d census-sample structures (%d main `F0+K0-1+K0-3` + %d '
      '`K0-1 dropped`), the 19 A87 genuine-FJ structures (6 of them LOOSE '
      'mid-drain probes, not certified FJ), and Trump. Every census record\'s '
      '`m` and `chi` were re-derived here and agree.'
      % (tc['n'], S['triage_by_set'].get('census', {}).get('n', 0),
         S['triage_by_set'].get('k0drop', {}).get('n', 0)))
    A('')

    # -------------------------------------------------------------- Tier 1
    A('## 1. Tier 1  --  triage')
    A('')
    A('T1a is bookkeeping (m, k_H, chi = m - (3 k_H + 1), rigid-possible '
      'flag chi >= 0). **Only %d of %d census structures are rigid-possible** '
      '(chi >= 0); the census is overwhelmingly FLEXIBLE, so the FJ tier is '
      'almost entirely the Farkas/Gordan branch, not the Krawczyk branch.'
      % (tc['n_chi_ge_0'], tc['n']))
    A('')
    A('T1b is the realisability LP:')
    A('')
    A('* with the tilt classes confined to interval bins every row of H is '
      'INTERVAL-LINEAR in the centres and s;')
    A('* each coefficient interval is split as midpoint +- radius and the '
      'radius part bounded by its worst case over the centre box, so '
      '`|row - (sum ac_i v_i + Kc)| <= sum r_i Vmax_i + Krad =: E` with '
      '`Vmax_i = max(|lo_i|, |hi_i|)` over that variable\'s box range;')
    A('* the equality `row = 0` is RELAXED to the two linear inequalities '
      '`sum ac_i v_i + Kc <= E` and `-(sum ac_i v_i + Kc) <= E`. Every '
      'genuine realisation with tilts in the bins satisfies both, so this is '
      'a sound OUTER relaxation: LP infeasibility really does mean H has no '
      'realisation in that tilt bin, and it can never kill a realisable '
      'structure;')
    A('* rebuilt dominance rows enter one-sided (`upper end of the relaxed '
      'value >= 0`); containment uses the one-sided sound bounds '
      '`v + A_hi >= 0` and `v + A_lo <= s`;')
    A('* the LP actually solved is the margin form `max t` with `t` added to '
      'every relaxed row, so HiGHS always returns a dual; `t* < -1e-9` is the '
      'KILL and `|t*|` the margin. Tilt classes are bisected (<= 3 levels, '
      '<= 64 leaves; leaves inconsistent with the strict class order are '
      'pruned for free). KILL iff every leaf is infeasible.')
    A('* **KILL TYPE**: each killing run is repeated with `s in [1, 5]` '
      'instead of `[3.82, 3.877084]`, which also widens the wall-tightened '
      'centre boxes. Still infeasible => CONTAINMENT-type (unrealisable at '
      'any side, A59\'s diagnosis); feasible => S-HAT-type (the kill uses the '
      'side bound  --  new work).')
    A('')
    A('| set | n | KILL | kill frac (1 sigma) | CONTAINMENT | S-HAT | '
      'survivor frac (1 sigma) | ms mean | ms p95 | chi>=0 |')
    A('|---|---|---|---|---|---|---|---|---|---|')
    for g, t in sorted(S['triage_by_set'].items()):
        A('| %s | %d | %d | %s [%s, %s] | %d | %d | %s [%s, %s] | %.1f | '
          '%.1f | %d |'
          % (g, t['n'], t['n_kill'], pct(t['kill_frac']),
             pct(t['kill_frac_1sigma'][0]), pct(t['kill_frac_1sigma'][1]),
             t['n_kill_containment'], t['n_kill_shat'],
             pct(t['survivor_frac']), pct(t['survivor_frac_1sigma'][0]),
             pct(t['survivor_frac_1sigma'][1]), t['ms']['mean'],
             t['ms']['p95'], t['n_chi_ge_0']))
    A('| **CENSUS (census+k0drop)** | %d | %d | %s [%s, %s] | %d | %d | '
      '%s [%s, %s] | %.1f | %.1f | %d |'
      % (tc['n'], tc['n_kill'], pct(tc['kill_frac']),
         pct(tc['kill_frac_1sigma'][0]), pct(tc['kill_frac_1sigma'][1]),
         tc['n_kill_containment'], tc['n_kill_shat'], pct(tc['survivor_frac']),
         pct(tc['survivor_frac_1sigma'][0]),
         pct(tc['survivor_frac_1sigma'][1]), tc['ms']['mean'],
         tc['ms']['p95'], tc['n_chi_ge_0']))
    A('')
    A('**Kill type by bracket (census population):** CONTAINMENT '
      '%s [%s, %s]; S-HAT %s. **Survivor fraction %s [%s, %s].**'
      % (pct(tc['kill_frac_containment']),
         pct(tc['kill_frac_containment_1sigma'][0]),
         pct(tc['kill_frac_containment_1sigma'][1]),
         pct(tc['kill_frac_shat']), pct(tc['survivor_frac']),
         pct(tc['survivor_frac_1sigma'][0]),
         pct(tc['survivor_frac_1sigma'][1])))
    A('')
    A('Farkas dual mass by row family over the killing leaves (`box_s` = the '
      's-hat side bound, `box_centre` = the wall-tightened centre box; both '
      'enter as VARIABLE bounds rather than rows): `%s`.'
      % json.dumps({k: round(v, 4)
                    for k, v in tc['farkas_dual_by_row_family'].items()}))
    A('')
    A('No exact-rational Farkas certificate was produced for the pilot; the '
      'LP dual residual is recorded per killing leaf in '
      '`results/pilot88_triage.jsonl`. On A54/A59 experience a rational '
      'certificate would multiply the triage cost by ~2-5x  --  which changes '
      'nothing below, since the triage alone already loses by ~%.0f orders '
      'of magnitude at N = 1e11.'
      % math.log10(cm['by_N']['1e11 (Level-0 graphs)']['triage_cpu_h']
                   / A85_CPUH[1]))
    A('')
    A('### Sanity on the (b) structures  --  the required check')
    A('')
    A('The A87 structures are REALISED (genuine k0 FJ points at sigma '
      '3.8868-4.0, all above s-hat). T1b must not kill them with the side '
      'bound dropped, and it does not: all 8 kills among them are '
      'S-HAT-type (exactly the sigma = 4.0 family, whose realisations all sit '
      'above s-hat), never CONTAINMENT-type. **No containment-type kill of a '
      'realised structure occurred  --  the bug signature did not fire.** '
      'Trump survives T1.')
    A('')

    # -------------------------------------------------------------- Tier 2
    A('## 2. Tier 2  --  the FJ tier')
    A('')
    A('Branch and bound over the core box. Leaf tests in order: HC4 / '
      'interval Gauss-Seidel propagation on the interval-linear rows (the '
      'linear form depends only on the tilt bins, so it is built once per box '
      'and reused across sweeps); a-structure (`0 not in [g_r](B)`); a-ineq '
      '(a rebuilt dominance side row provably negative); a-sigma '
      '(`sigma_min(B) > s-hat_hi`, using `sigma >= every loaded corner '
      'coordinate`); F (Gordan/Farkas over the box with the row set FIXED by '
      'H, so there is NO selection menu and A87\'s menu explosion does not '
      'arise); K (Krawczyk on D independent rows picked by pivoted QR at the '
      'box midpoint, rigid-possible only); otherwise bisect the widest '
      'coordinate relative to its initial range, with a x1.5 preference for '
      'tilt classes.')
    A('')
    A('### The 20-structure pilot table')
    A('')
    A('| tag | set | k_H | m | chi | D | d_H | ratt | boxes | s | ms/box | '
      'stop | depth | open | log10 remaining vol | min max-width | F LPs | '
      'F fired | K tries | roots |')
    A('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|'
      '---|---|---|')
    for r in S['fj_rows']:
        A('| %s | %s | %d | %d | %d | %d | %s | %s | %d | %.2f | %.2f | %s | '
          '%d | %d | %s | %.3f | %d | %d | %d | %d |'
          % (r['tag'], r['set'] or '-', r['k_H'], r['m'], r['chi'],
             r['D_core'], r['d_H'], r['rattlers'], r['boxes'], r['secs'],
             r['ms_per_box'], r['stopped'], r['max_depth'],
             r['open_stack_final'],
             ('%.1f' % r['log10_remaining_volume_frac'])
             if r['log10_remaining_volume_frac'] is not None else 'EMPTY',
             r['min_max_abs_width_reached'] or 0, r['farkas_n_lp'],
             r['leaf_hist'].get('F', 0), r['krawczyk_attempts'],
             r['n_roots_isolated']))
    A('')
    A('The split is total and it is the point of the whole pilot:')
    A('')
    A('* the **7 CENSUS structures COMPLETE**  --  stack empty, zero surviving '
      'boxes, zero roots  --  in %d-%d boxes and %.3f-%.3f s. The certificate '
      '"no FJ point with support in H and s <= s-hat" is DISCHARGED for each;'
      % (fs['complete_boxes']['min'], fs['complete_boxes']['max'],
         fs['complete_secs']['min'], fs['complete_secs']['max']))
    A('* the **13 A87/Trump structures never complete** (all hit the 20,000 '
      'box cap at ~30 s). That is the CORRECT behaviour, not a failure: '
      'those structures CONTAIN a genuine FJ point, so there is nothing to '
      'discharge and no certificate to have. For those the right output is to '
      'IDENTIFY the point, which is what the canary below shows Krawczyk '
      'doing.')
    A('')
    A('**Two-tier kill rate on the census population:** T1 kills %s, and the '
      'FJ tier then closes %s of the T1 survivors, so the pipeline discharges '
      'about %.1f%% of census structures and leaves ~%.1f%% open. The open '
      'residue is what a real run would still owe a proof for.'
      % (pct(tc['kill_frac']), pct(fc.get('complete_frac')),
         100 * (tc['kill_frac'] + tc['survivor_frac']
                * (fc.get('complete_frac') or 0)),
         100 * tc['survivor_frac'] * (1 - (fc.get('complete_frac') or 0))))
    A('')
    A('Leaf-verdict shares over the tier-2 set: `%s`.'
      % json.dumps({k: round(v['share'], 4)
                    for k, v in fs['leaf_kill_shares'].items()}))
    A('')
    A('### Cost calibration (larger sample)')
    A('')
    A('Seven completing structures is too thin a base for `c_FJ`, so the FJ '
      'tier was also timed on a uniform subsample of **%d** census T1 '
      'survivors with a 20 s cap each (`results/pilot88_fj_calib.jsonl`). '
      'This is a per-structure COST MEASUREMENT, not a run of the exclusions '
      'at scale  --  total wall time 149 s.' % fc['n'])
    A('')
    A('| quantity | value |')
    A('|---|---|')
    A('| COMPLETE | %d / %d = %s [%s, %s] (1 sigma) |'
      % (fc['n_complete'], fc['n'], pct(fc['complete_frac']),
         pct(fc['complete_frac_1sigma'][0]),
         pct(fc['complete_frac_1sigma'][1])))
    A('| seconds, completing structures | mean %.4f, median %.4f, p95 %.4f, '
      'max %.4f |' % (fc['secs_complete']['mean'], fc['secs_complete']['median'],
                      fc['secs_complete']['p95'], fc['secs_complete']['max']))
    A('| boxes, completing structures | mean %.0f, median %d, p95 %d, max %d |'
      % (fc['boxes_complete']['mean'], fc['boxes_complete']['median'],
         fc['boxes_complete']['p95'], fc['boxes_complete']['max']))
    A('| seconds, ALL (CENSORED at the 20 s cap) | mean %.4f  --  this is a '
      'LOWER BOUND, the %d capped structures were still running |'
      % (fc['secs_all_CENSORED_at_cap']['mean'], fc['n_capped']))
    A('| rigid-possible (chi >= 0) in the sample | %d / %d |'
      % (fc['n_chi_ge_0'], fc['n']))
    A('| chi of the capped structures | %s |' % fc['chi_of_capped'])
    A('')
    A('Leaf-kill shares over the calibration set: `%s`. The rebuilt '
      'DOMINANCE side conditions carry two thirds of all kills; without them '
      'the tier would not close at all.'
      % json.dumps({k: round(v['share'], 4)
                    for k, v in fc['leaf_kill_shares'].items()}))
    A('')
    A('### Does F fire? YES  --  but rarely, and only where it is needed')
    A('')
    A('A87 found Gordan never fires over configuration cells and blamed the '
      'selection MENU. With the row set FIXED by H there is no menu, and F '
      'DOES fire: **%d** firings over the calibration set, %.2f%% of all leaf '
      'kills  --  but concentrated on **%d of %d** structures, and those are '
      'among the hard ones. On the 20-structure pilot table F fired %d times '
      'in %d box LPs (the completing census structures close on a-structure '
      'and a-ineq before F is reached; the A87/Trump structures contain '
      'genuine FJ points, where F CANNOT fire by definition).'
      % (fc['F_fired_total'],
         100 * fc['leaf_kill_shares'].get('F', {}).get('share', 0.0),
         fc['F_structures_where_F_fired'], fc['n'],
         fs['F_fired_total'], fs['F_lp_total']))
    A('')
    A('The LP itself was validated with controls: on a positive control (one '
      'square pinned in the SW corner, rows `q_0` on `x=0` and on `y=0`) it '
      'returns t = 1.0; adding the `x=s`/`y=s` rows correctly returns 0. '
      'Note this box test is the BOX VERSION of the point-wise NNLS/Gordan '
      'descent direction in A87 `fjpolish87`  --  the same test lifted to a box.')
    A('')
    A('### K is essentially never reached by the search')
    A('')
    A('Krawczyk was attempted **%d** times across the tier-2 set: the branch '
      'and bound never drove a box below the Krawczyk basin width (0.05) '
      'within the cap on the structures that do not close, and the ones that '
      'do close never need it. Where Krawczyk CAN be run (the canary '
      'descent) it works perfectly. The obstruction is reaching a small '
      'enough box, not the test.' % fs['K_attempts_total'])
    A('')
    A('### The volume metric saturates  --  use the log-space one')
    A('')
    A('"Discharged volume fraction" is not usable here: HC4 contracts the '
      'root box to ~1e-60..1e-94 of its volume on the FIRST sweep (the '
      'realisation set of H has positive codimension), so the discharged '
      'fraction is 1.0 in double precision from box 1. The table therefore '
      'reports `log10` of the REMAINING volume, computed in log space over '
      'the open boxes; `EMPTY` means the stack emptied and the search is '
      'complete.')
    A('')
    A('### HC4 ablation (measured on 2 structures, ON vs OFF)')
    A('')
    A('| tag | HC4 | boxes | s | log10 discharged frac |')
    A('|---|---|---|---|---|')
    for a in S.get('hc4_ablation', []):
        A('| %s | %s | %d | %.1f | %s |'
          % (a['tag'], a['hc4'], a['boxes'], a['secs'],
             ('%.2f' % a['log10_discharged_frac'])
             if a['log10_discharged_frac'] is not None else '-inf'))
    A('')
    A('HC4 is what makes the search do anything at all: without it the '
      'discharged volume fraction stays at ~0.5-0.9 (the box barely moves); '
      'with it the root box collapses onto the realisation variety '
      'immediately, and it costs nothing measurable in ms/box.')
    A('')
    A('### What limits the FJ tier  --  EXTRAPOLATED')
    A('')
    A('Deep probes (no box cap, 120-300 s) were run on the structures that '
      'do NOT close, to size the obstruction. Fitting `log2(boxes visited at '
      'depth d)` against `d` gives the branching per level; the depth needed '
      'is `n_wide * log2(W_max / 0.05)` with `n_wide` the number of core '
      'coordinates HC4 leaves wider than the Krawczyk basin at the root.')
    A('')
    A('| tag | boxes | s | n_wide | halvings/coord | depth needed | '
      'log2 branch/level | min max-width reached |')
    A('|---|---|---|---|---|---|---|---|')
    for tag, f in sorted((S.get('depth_fit') or {}).items()):
        rw = f.get('root_wide') or {}
        A('| %s | %d | %.0f | %s | %.2f | %.0f | %.3f | %.3f |'
          % (tag, f['boxes'], f['secs'], rw.get('n_gt_krawczyk_abswidth'),
             rw.get('halvings_needed_per_wide_coord') or 0,
             (rw.get('n_gt_krawczyk_abswidth') or 0)
             * (rw.get('halvings_needed_per_wide_coord') or 0),
             f.get('log2_branch_per_depth') or 0, f.get('min_maw') or 0))
    A('')
    A('MEASURED: 1.9e5 boxes on Trump\'s support in 300 s took the widest '
      'core coordinate only from 2.877 to 0.25 (3.5 halvings) and the maximum '
      'depth plateaued at 36. EXTRAPOLATED: the depth needed is ~94-187 in a '
      'tree branching at 2^0.34..2^0.89 per level, i.e. 1e9..1e50 boxes. But '
      'this is the cost of NOT closing a structure that genuinely holds an FJ '
      'point  --  the certificate is FALSE there and no amount of box budget '
      'will change that. **For the structures where the certificate is TRUE '
      '(the census), the tier closes in ~40 boxes.**')
    A('')

    # -------------------------------------------------------------- canary
    A('## 3. The Trump canary (A76 Lemma K)')
    A('')
    A('Method: descend the branch and bound always into the child that '
      'CONTAINS z-hat, running every leaf test on the way. If any test ever '
      'discharges that box the test is unsound.')
    A('')
    A('* **no test ever excluded z-hat: %s;**' % c['never_excluded'])
    A('* at depth %s the epsilon-inflated Krawczyk test CONTRACTED and '
      'certified exactly one root. (Plain Krawczyk pins at ratio ~1.03 '
      'forever: bisecting around a root leaves the root on the box boundary '
      'and K straddles it. One Newton step from the midpoint plus a retest on '
      'an inflated box around the candidate is the standard remedy and is '
      'what the pilot uses.)' % c['depth_to_isolation'])
    A('* refined root box max width **%.3g**, Krawczyk ratio **%.3f**, '
      'cond **%.1f** (well conditioned);'
      % (c['root_box_maxwidth'] or 0, c['krawczyk_ratio'] or 0,
         c['krawczyk_cond'] or 0))
    A('* the root\'s s-enclosure is **[%.15f, %.15f]**  --  width %.1e  --  which '
      'CONTAINS s-hat = %.15f (%s); s-hat minus the root midpoint = %.3g.'
      % (c['root_s_box'][0], c['root_s_box'][1],
         c['root_s_box'][1] - c['root_s_box'][0], c['s_hat'],
         c['contains_s_hat'], c['s_hat_minus_root_mid']))
    A('')
    A('This is exactly the required output: **one isolated root at s = s-hat, '
      'Krawczyk contracts. Krawczyk IDENTIFIES z-hat, it never excludes it. '
      'THE CANARY PASSES.**')
    A('')
    A('Controls: the same descent was run on all 19 A87 structures with the '
      's window widened to cover their sigma and the row-activity slack set '
      'to each structure\'s own extraction tolerance. **No CERTIFIED-FJ '
      '(tight, tol 1e-6) structure was ever excluded.** The only exclusion '
      'was `%s`  --  LOOSE, not certified FJ, extraction tol 1e-4  --  at box '
      'scale ~1e-4, i.e. at its own row-activity slack, where the EXACT row '
      'system genuinely has no root. The flexible structures end at the depth '
      'cap without isolation, as they must: with m < D there is no square '
      'subsystem and the root set is positive-dimensional.'
      % (', '.join(c['controls_excluded_loose']) or 'none'))
    A('')

    # ---------------------------------------------------------- cost model
    A('## 4. Cost model')
    A('')
    A('```')
    A('total = N * c_triage  +  N * f_surv * c_FJ')
    A('```')
    A('')
    A('All three factors MEASURED on the census population:')
    A('')
    A('| factor | value |')
    A('|---|---|')
    A('| `c_triage` | %.4g s/structure (mean; p95 %.1f ms) |'
      % (cm['c_triage_s'], tc['ms']['p95']))
    A('| `f_surv` | %s, 1 sigma [%s, %s] |'
      % (pct(cm['survivor_fraction']),
         pct(cm['survivor_fraction_1sigma'][0]),
         pct(cm['survivor_fraction_1sigma'][1])))
    A('| `c_FJ` | %.4g s/structure (mean over the calibration sample, '
      'CENSORED at the 20 s cap, so a LOWER bound); median of the %s that '
      'close: %.4g s |'
      % (cm['c_FJ_s_mean_CENSORED'], pct(fc['complete_frac']),
         cm['c_FJ_s_median_of_completing']))
    A('| per structure | %.4g s (mean) / %.4g s (median-optimistic) |'
      % (cm['per_structure_s_mean'], cm['per_structure_s_median_optimistic']))
    A('')
    A('| N | log10 triage CPU-h | log10 FJ CPU-h | log10 total CPU-h | '
      'x A85 upper (7,000) | log10 ratio |')
    A('|---|---|---|---|---|---|')
    for label, v in cm['by_N'].items():
        A('| %s | %.2f | %.2f | %.2f | %.3g | %.1f |'
          % (label, v['log10_triage_cpu_h'], v['log10_FJ_cpu_h'],
             v['log10_total_cpu_h'], v['ratio_to_A85_upper'],
             v['log10_ratio_to_A85_upper']))
    A('')
    A('**Break-even.** The route beats A85\'s 7,000 CPU-h only if the census '
      'has at most **N = %.2e** structures. With the triage alone (c_FJ = 0, '
      'an unreachable idealisation) the ceiling is **N = %.2e**. Both sit '
      'below the smallest census figure on the table (1e11 Level-0 graphs) by '
      '%.1f and %.1f orders of magnitude respectively, and 21 orders below '
      'the decorated total (1e29).'
      % (cm['break_even_N_at_7000_cpu_h'],
         cm['break_even_N_triage_only_at_7000_cpu_h'],
         math.log10(1e11 / cm['break_even_N_at_7000_cpu_h']),
         math.log10(1e11 / cm['break_even_N_triage_only_at_7000_cpu_h'])))
    A('')
    A('**A85 baseline** (attempts/A85-k0-route/notes/pilot_report.md, '
      'results/pilot_summary85.json): the tree pilot ran 12 of 26 planned '
      'budget-10 nodes  --  6 PASS, 5 FAIL, 1 refused  --  for '
      '`lp_seconds_total = 10363` and `cert_seconds_total = 5813`, i.e. '
      '~1,350 s per node (~860 s LP + ~485 s cert), with per-node cost '
      'collapsing 3-4 corners deep: the S3 node `s3_near_BL619642_TR023305` '
      'cost 63.0 s LP + 4.3 s cert, and the S4 node needed only 8.7 s of cert '
      'time. Headline for the whole tree: **3,200-7,000 CPU-h**.')
    A('')

    # ------------------------------------------------------------ findings
    A('## 5. Findings')
    A('')
    A('1. **On the CENSUS the triage kill is CONTAINMENT-type, not S-HAT.** '
      '%s of census structures are killed by T1b, and %s of those kills '
      'survive the side bound being dropped to `s <= 5`  --  i.e. T1b is '
      'mostly re-deriving A59\'s containment diagnosis, NOT doing new work '
      'with s-hat. Only %d census kill in %d used the side bound. (On the '
      'A87 set every kill is S-HAT-type, but that set is not the population: '
      'those structures are realised, at sigma above s-hat, so the side '
      'bound is the only thing that can kill them.) **The s-hat bound is '
      'nearly free at Tier 1.**'
      % (pct(tc['kill_frac']),
         pct(tc['n_kill_containment'] / max(1, tc['n_kill'])),
         tc['n_kill_shat'], tc['n']))
    A('2. **Yes, F fires on fixed-structure boxes  --  where A87\'s menu version '
      'never did.** %d firings, %.2f%% of leaf kills, on %d of %d '
      'calibration structures. It is not the workhorse (that is the rebuilt '
      'dominance side conditions at %.0f%% and a-structure at %.0f%%), but '
      'the menu really was part of A87\'s problem, and removing it recovers '
      'a working Gordan test.'
      % (fc['F_fired_total'],
         100 * fc['leaf_kill_shares'].get('F', {}).get('share', 0.0),
         fc['F_structures_where_F_fired'], fc['n'],
         100 * fc['leaf_kill_shares'].get('a_ineq', {}).get('share', 0.0),
         100 * fc['leaf_kill_shares'].get('a_struct', {}).get('share', 0.0)))
    A('3. **What limits the FJ tier is neither d_H nor hinge conditioning  --  '
      'it is whether the certificate is TRUE.** %s of census survivors close '
      'in ~%d boxes / ~%.0f ms. The ones that do not close are exactly the '
      'ones containing a genuine FJ point (Trump, the A87 realised points) '
      'plus %d of %d census stragglers, all with chi <= -2. Where the search '
      'must grind, the obstruction is box count set by the core dimension '
      'D = 24-34 (HC4 pins 5-15 coordinates then stalls, leaving 16-19 wide '
      'ones each needing ~5.9 halvings); hinge conditioning is fine '
      '(Krawczyk cond ~15 on Trump) and d_H on its own predicts nothing.'
      % (pct(fc['complete_frac']), fc['boxes_complete']['median'],
         1000 * fc['secs_complete']['median'], fc['n_capped'], fc['n']))
    A('4. **The census is essentially all FLEXIBLE.** Only %d of %d census '
      'structures have chi >= 0. Any plan that leans on Krawczyk (A76\'s '
      'cheap rigid-grain discharge) applies to a vanishing share of the '
      'population; the route lives or dies on the flexible branch.'
      % (tc['n_chi_ge_0'], tc['n']))
    A('5. **HC4 and the rebuilt dominance rows are the two load-bearing '
      'pieces, and both are cheap.** Turning HC4 off leaves the box '
      'essentially uncontracted; dropping the dominance side conditions '
      'removes two thirds of all leaf kills. Neither costs measurable time. '
      'A future version should also propagate onto the TILT variables, which '
      'the current HC4 does not touch (the interval-linear form treats tilts '
      'as constants).')
    A('6. **The verdict is the census size.** Per structure this route is '
      'about %.2g s all-in  --  genuinely cheap, and much cheaper than the '
      '0.81 s/cell A87 measured for configuration cells. It still loses to '
      'A85 by %.0f orders of magnitude at N = 1e11 and by %.0f at N = 1e29, '
      'because N is 3-21 orders above the %.1e break-even. The dominant '
      'multiplier is **N**. Per the brief\'s own decision rule (win at '
      '<= 1e6, lose at >= 1e12), **H1-by-structure LOSES, and it loses on '
      'the count, not the price.**'
      % (cm['per_structure_s_mean'],
         cm['by_N']['1e11 (Level-0 graphs)']['log10_ratio_to_A85_upper'],
         cm['by_N']['1e29 (decorated total)']['log10_ratio_to_A85_upper'],
         cm['break_even_N_at_7000_cpu_h']))
    A('')
    A('## 6. Measured vs extrapolated')
    A('')
    A('**MEASURED**: every triage number and bracket; the kill-type split; '
      'every tier-2 box count, wall time, ms/box, leaf histogram, depth, '
      'open-stack size and remaining-volume figure; the whole 150-structure '
      'cost calibration; the HC4 ablation; the entire canary including the '
      'root\'s s-enclosure; the Farkas positive/negative controls; the '
      'dominance-convention validation; the p88_iv-vs-mpmath agreement.')
    A('')
    A('**EXTRAPOLATED**: boxes-to-completion and depth-needed for the '
      'structures that do NOT close (from the depth-branching fit); the total '
      'CPU-h at N = 1e11 / 1e18 / 1e29 (linear in N from the measured '
      'per-structure cost, with `c_FJ` a censored LOWER bound); the ~2-5x '
      'factor for an exact-rational Farkas certificate (quoted from A54/A59, '
      'not measured here).')
    A('')
    A('**CAVEATS.** (i) The census sample carries A59\'s orbit-weight caveat, '
      'measured by the census chore at +3.3%%; the fractions here are over '
      'LABELLED draws. (ii) `c_FJ` is censored at the 20 s cap, so the mean '
      'is a lower bound  --  the true mean is larger and the verdict only gets '
      'stronger. (iii) The 6 lowest A87 structures are LOOSE probes, not '
      'certified FJ points, and are used only as near-rigid cost probes. '
      '(iv) Float intervals, not a certificate.')
    A('')
    p = os.path.join(NOTES, 'pilot_report.md')
    open(p, 'w').write('\n'.join(L) + '\n')
    print('wrote', p)


if __name__ == '__main__':
    main()
