"""A31: assemble results/count_report.json (ablation tables, fan-out, projection,
gap list) from the Level 0/1/1b/2 outputs."""
import os, sys, json, math
import numpy as np

ROWS = [
    ('R0', 'no filter (simple graphs, k squares + 4 walls, no wall-wall edges)'),
    ('R2', '+ L5(b)  wall-degree <= 2 and the two walls adjacent'),
    ('R3', '+ L1     every loaded square has degree >= 2'),
    ('R4', '+ L5(d)  square-square degree <= 12'),
    ('R5', '+ L4(a)  Euler edge bound |E| + 4 <= 3(k+4)-6'),
    ('R6', '+ L5(a)  metric / hop-distance consistency (broad phase)'),
    ('R7', '+ L3     no floating component (self-stress branch split off)'),
    ('R8', '+ L6     some H-component joins two opposite walls (lam0=0 branch split off)'),
    ('R9', '+ L4(b)  full planarity of H + wall 4-cycle'),
    ('R10', '+ L7     (implied by L6 here; see gap G1)'),
]


def main():
    here = os.path.dirname(__file__)
    outdir = os.path.join(here, '..', 'results')
    L0 = {}
    for k in range(2, 12):
        p = os.path.join(outdir, 'level0_k%d.json' % k)
        if os.path.exists(p):
            L0[k] = json.load(open(p))
    L1 = json.load(open(os.path.join(outdir, 'level1.json')))
    L1b = {}
    p = os.path.join(outdir, 'level1b.json')
    if os.path.exists(p):
        L1b = json.load(open(p))
    L2 = json.load(open(os.path.join(outdir, 'level2.json')))
    ks = sorted(L0)

    abl = {}
    for k in ks:
        d = L0[k]
        vals = [d['R0_no_filter'], d['R2_L5b']] + list(d['cum'])
        abl[k] = {ROWS[i][0]: int(vals[i]) for i in range(len(ROWS))}
        abl[k]['_hard_survivors_MAIN'] = d['branch']['main']
    marg = {}
    for k in ks:
        d = L0[k]
        b = d['marg'][3]
        marg[k] = dict(
            base_after_L5a=b,
            L3_alone=d['marg'][4], L6_alone=d['marg'][5],
            L4b_with_wall_cycle=d['marg'][6], L4b_graph_only=d['marg'][7],
            frac_L6=(d['marg'][5] / b if b else None),
            frac_planar_wallcycle=(d['marg'][6] / b if b else None),
            frac_planar_graphonly=(d['marg'][7] / b if b else None))
    branches = {k: dict(L0[k]['branch']) for k in ks}
    for k in ks:
        branches[k]['main_non_thin'] = (L0[k]['branch']['main'] -
                                        L0[k]['branch']['thin_main'])
    soft = {}
    for k in ks:
        d = L0[k]
        m = max(1, d['branch']['main'])
        soft[k] = dict(
            main=d['branch']['main'],
            maxwell_possible_2E_ge_3k1=d['soft'][0],
            maxwell_certain_E_ge_3k1=d['soft'][1],
            wall_node_degree_le_5=d['soft'][2],
            kissing_le_8=d['soft'][3],
            wall_node_degree_le_3_certified=(d['soft'][4]
                                             if len(d['soft']) > 4 else None),
            main_wallcap3_and_non_thin=d.get('main_wallcap3_nonthin'),
            all_soft=d['soft_and'],
            frac_maxwell_possible=d['soft'][0] / m,
            frac_wallcap=d['soft'][2] / m,
            E_hist_main={int(a): b for a, b in sorted(
                (d.get('Ehist') or {}).items(), key=lambda x: int(x[0]))},
            E_max_main=(max(int(a) for a in d['Ehist']) if d.get('Ehist') else None),
            E_budget_3k_plus_2=3 * k + 2,
            maxwell_threshold_3k_plus_1=3 * k + 1)

    rep = dict(
        what='A31 structure-space counting pilot: size of the PRUNED contact-structure '
             'space for the structure-first exclusion campaign at s0 = 3.8771',
        object='SUPPORT graph H on a loaded core of k squares + 4 wall nodes, counted up '
               'to S_k x D4 (exact orbit counts)',
        filters_used=dict(
            hard=['Fact 0 (simple)', 'L1', 'L3 (branch kept)', 'L4', 'L5(a) broad',
                  'L5(b)', 'L5(d)', 'L6 (branch kept)'],
            thin_flagged=['L2 degree-2', 'L3/L6 self-stress and lam0=0 branches'],
            soft_report_only=['Maxwell m >= 3k+1', 'L5(c) per-wall cap 5', 'kissing 8']),
        ablation_orbit_counts=abl,
        ablation_rows=[dict(row=a, meaning=b) for a, b in ROWS],
        marginal_kill_on_metric_consistent_set=marg,
        branch_counts=branches,
        soft_columns=soft,
        level1_fanout={a: {x: y for x, y in b.items() if x != 'rows'}
                       for a, b in L1.items()},
        level1b_rotation_system={a: {x: y for x, y in b.items() if x != 'rows'}
                                 for a, b in L1b.items()},
        level2=dict(fits=L2.get('fits'), projection=L2.get('projection')),
        validation=[
            'graph-rep counts match OEIS A000088 (1,2,4,11,34,156,1044)',
            'k=2 and k=3: FULL independent brute force over every edge subset with an '
            'independent filter implementation - all 8 ablation rows and all 5 branch '
            'counts agree exactly',
            'k=4: independent brute force from the L1 stage on - all rows agree exactly',
            'Burnside orbit formula for R0/R2 agrees with the brute-force orbit count '
            'at k=2,3',
            'Level-1 exact decoration count agrees with an independent brute-force '
            'enumeration + explicit tilt-ladder search on 24 small cases',
            'Level-1b Monte Carlo reproduces the exact Level-1 tilt acceptance rate '
            'within sampling error on every graph tested',
            'SOUNDNESS: the contact graph of Trump\'s known optimum (s = 3.877084, '
            'k = 11 loaded squares, 14 square-square + 11 square-wall edges) passes '
            'EVERY hard filter (code/check_trump.py). Its per-wall degrees are '
            '3/3/3/2, exactly meeting the certified per-wall cap of 3 derived here, '
            'and its minimum total degree is 3, so it is NOT in the L2 thin branch. '
            'Its |E| = 25 is far below the Maxwell threshold 3k+1 = 34, confirming '
            'that flush/multi-row contacts carry the rigidity and that |E| >= 3k+1 '
            'must NOT be applied as a prune.'],
        gaps=GAPS)

    # ------------------------------------------------------------------ findings
    kmax = max(ks)
    ratios = {k: L0[k]['branch']['main'] / L0[k - 1]['branch']['main']
              for k in ks if k - 1 in ks and k >= 4}
    proj = L2.get('projection', {})

    def gk(dic, key):
        if key in dic:
            return dic[key]
        return dic.get(str(key), dic.get(int(key) if str(key).isdigit() else key))

    f = []
    f.append('Level 0 is EXHAUSTIVE and orbit-exact for k = %s (S_k x D4). MAIN hard '
             'survivors: %s.' % (
                 ', '.join(str(k) for k in ks),
                 ', '.join('k=%d: %d' % (k, L0[k]['branch']['main']) for k in ks)))
    f.append('The survivor ratio N(k)/N(k-1) is close to LINEAR in k (%s), i.e. the '
             'space grows like k! times an exponential, not like a pure exponential. '
             'That is the shape that decides the campaign.' % (
                 ', '.join('%d->%d: %.2f' % (k - 1, k, v) for k, v in ratios.items())))
    if 'main_non_thin' in L2.get('series', {}):
        nt = L2['series']['main_non_thin']
        kk2 = sorted(int(x) for x in nt)
        rr = [nt[str(k)] / nt[str(k - 1)] for k in kk2[1:]]
        f.append('KEY STRUCTURAL FACT: the factorial-looking growth is entirely in the '
                 'L2 THIN branch. The NON-THIN survivors (%s) grow with an essentially '
                 'CONSTANT ratio (%s), i.e. a pure exponential ~17^k, and all three fit '
                 'models agree on their k=11 value to within 6%% (~7e9). So if L2 '
                 'degree-2 collinearity is upgraded from a thin branch to a hard prune, '
                 'the structure space becomes exponential rather than factorial and the '
                 'k=11 graph count drops by ~50x to ~7e9.' % (
                     ', '.join(str(nt[str(k)]) for k in kk2),
                     ', '.join('%.1f' % r for r in rr)))
    f.append('Filter strength (cumulative, orbit counts): the metric broad phase L5(a) '
             'is by far the strongest hard filter (k=%d: %d -> %d, x%.0f), then L6 '
             '(x%.1f) and full planarity (x%.1f). L5(d) and the Euler bound are almost '
             'free.' % (kmax, L0[kmax]['cum'][2], L0[kmax]['cum'][3],
                        L0[kmax]['cum'][2] / max(1, L0[kmax]['cum'][3]),
                        L0[kmax]['cum'][4] / max(1, L0[kmax]['cum'][5]),
                        L0[kmax]['cum'][5] / max(1, L0[kmax]['cum'][6])))
    f.append('Thin (L2 degree-2) branches are ~%.0f%% of MAIN at k=%d; the two flagged '
             'branches that must be excluded by their own row systems are the '
             'lambda0=0 branch (%d, %.0f%% of MAIN) and the L3 self-stress branch '
             '(%d).' % (100.0 * L0[kmax]['branch']['thin_main'] /
                        L0[kmax]['branch']['main'], kmax, L0[kmax]['branch']['lam0'],
                        100.0 * L0[kmax]['branch']['lam0'] /
                        L0[kmax]['branch']['main'],
                        L0[kmax]['branch']['selfstress_float']))
    f.append('MAXWELL: not one survivor at any k reaches |E| >= 3k+1 (planarity caps '
             '|E| at 3k+2 and the observed maximum is %s). Every candidate structure '
             'therefore needs FLUSH contacts to be first-order rigid. If the Maxwell '
             'row count is ever proved necessary it becomes a very strong filter; the '
             'ledger currently marks it soft, so it is not applied.' % (
                 {k: soft[k]['E_max_main'] for k in ks}))
    if len(L0[kmax]['soft']) > 4:
        f.append('A CERTIFIED tightening of L5(c) is available for free: two squares on '
                 'the same wall have centres within sqrt2/2 of it and >= 1 apart, so '
                 'their along-wall coordinates differ by >= 0.97832 while the range is '
                 's-1 <= 2.8771 - hence AT MOST 3 squares per wall, not 5. Applied as a '
                 'soft column it keeps %d of %d MAIN survivors at k=%d (x%.2f), and '
                 'combined with dropping the L2 thin branches, %d (x%.0f smaller).' % (
                     L0[kmax]['soft'][4], L0[kmax]['branch']['main'], kmax,
                     L0[kmax]['soft'][4] / L0[kmax]['branch']['main'],
                     L0[kmax].get('main_wallcap3_nonthin', -1),
                     L0[kmax]['branch']['main'] /
                     max(1, L0[kmax].get('main_wallcap3_nonthin', 1))))
    if L1:
        kk = sorted(int(x[1:]) for x in L1)
        f.append('Level 1 (decorations): tilt propagation is exact for the tilt '
                 'subsystem and kills %s of the gauge-fixed menu at k=%s, but what '
                 'survives still grows fast: weighted geometric-mean survivors per '
                 'graph %s.' % (
                     ', '.join('%.1f%%' % (100 * L1['k%d' % k]['kill_weighted'])
                               for k in kk), kk,
                     ', '.join('%.3g' % L1['k%d' % k]['gauge_surv_geomean_weighted']
                               for k in kk)))
    if L1b:
        kb = sorted(int(x[1:]) for x in L1b)
        f.append('Level 1b: the ROTATION-SYSTEM (planar embedding) test that Level 1 '
                 'ignores is a real filter and it strengthens fast with k. It removes '
                 '%s of the tilt-feasible decorations (weighted mean) at k=%s, and for '
                 'the MEDIAN graph it removes %s - i.e. at k=7 a typical graph loses '
                 '91%% of its decorations to embedding consistency alone. The weighted '
                 'mean lags the median because a minority of low-degree graphs keep '
                 'everything. This is the single cheapest unexploited constraint found '
                 'here and it should be built into any structure-first generator; even '
                 'so it does not change the order of magnitude of the k=11 projection.'
                 % (', '.join('%.0f%%' % (100 * (1 - L1b['k%d' % k]['rot_keep_weighted']))
                              for k in kb),
                    kb,
                    ', '.join('%.0f%%' % (100 * (1 - L1b['k%d' % k]['rot_keep_median']))
                              for k in kb)))
    if 'total_structures' in proj:
        ts = proj['total_structures']
        f.append('PROJECTION to the full loaded core k=11 (extrapolation, not a bound): '
                 'Level-0 graphs %s; decoration fan-out ~%.2g; composed total %s. '
                 'Summed over all core sizes k=3..11 (rattler completion NOT counted): '
                 '%s.' % (
                     ' / '.join('%s %.3g' % (n, gk(v, 11))
                                for n, v in proj['main_level0'].items()),
                     gk(proj['fanout'], 11),
                     ' / '.join('%s %.3g' % (n, v['k11']) for n, v in ts.items()),
                     ' / '.join('%s %.3g' % (n, v['sum_all_cores'])
                                for n, v in ts.items())))
        # optimistic composite: non-thin + certified wall cap 3, decorations with the
        # rotation-system test extrapolated
        try:
            import math as _m
            nt = L2['projection']['other_series']['main_wallcap3_nonthin']
            g11 = sum(gk(v, 11) for v in nt.values()) / len(nt)
            kb = sorted(int(x[1:]) for x in L1b)
            xs = [k for k in kb if L1b['k%d' % k]['rot_keep_median'] > 0]
            ys = [_m.log(L1b['k%d' % k]['rot_keep_median']) for k in xs]
            b, a = np.polyfit(xs[-3:], ys[-3:], 1)
            keep11 = _m.exp(a + b * 11)
            f.append('BEST CASE if every cheap improvement lands (L2 promoted to a hard '
                     'prune, the certified per-wall cap of 3 promoted, and the '
                     'rotation-system test built into the decoration generator with its '
                     'median keep-rate extrapolated to k=11, ~%.0e): about %.2g graphs '
                     'x %.2g decorations = ~%.1e structures at k=11. That is 5-6 orders '
                     'of magnitude better than the naive count and still astronomically '
                     'far beyond any compute budget - the verdict does not change.' % (
                         keep11, g11, gk(L2['projection']['fanout'], 11) * keep11,
                         g11 * gk(L2['projection']['fanout'], 11) * keep11))
        except Exception as e:
            f.append('best-case composite not computed: %r' % (e,))
        f.append('GO/NO-GO: an enumerate-then-solve structure-first campaign at k=11 is '
                 'not viable - ~1e11-1e12 contact graphs before decoration, ~1e30 '
                 'decorated structures after. Even the undecorated Level-0 layer at '
                 '1 ms/graph is ~1e4 CPU-days. Viability requires (i) branching on '
                 'structure jointly with the metric solve (prune during generation, '
                 'never enumerate a level), (ii) promoting L2 and the certified '
                 'per-wall cap 3 (about 1.5 orders of magnitude), and (iii) treating '
                 'the contact TYPE (flush / corner-on-edge) as an algebraic unknown '
                 'inside one FJ solve per graph rather than as 1e18 separate branches.')
    rep['findings'] = f
    with open(os.path.join(outdir, 'count_report.json'), 'w') as fh:
        json.dump(rep, fh, indent=1, default=float)
    print('wrote count_report.json')
    return rep


GAPS = [
 dict(id='G1', kind='soundness/bookkeeping', text=(
  'The object enumerated is the SUPPORT graph H (positive multipliers), because L1, L3 '
  'and L6 are statements about H. L7 is a statement about the ACTIVE-CONTACT graph G, '
  'so it is NOT a legitimate hard filter on H and is only reported as a column. In the '
  'lambda0>0 branch L6 already implies it, and empirically R10 = R9 at every k, so '
  'nothing is lost - but a future enumerator that works on G must not double-use it.')),
 dict(id='G2', kind='filter strength', text=(
  'L4 planarity is applied to H together with the wall 4-cycle, exactly as L4\'s '
  'drawing constructs it. If one only accepts planarity of H alone the filter is '
  'about 2x weaker (measured: see marginal_kill_on_metric_consistent_set, '
  'L4b_graph_only vs L4b_with_wall_cycle). Both counts are reported; MAIN uses the '
  'wall-cycle version.')),
 dict(id='G3', kind='approximation (sound)', text=(
  'L5(a) is implemented as a relaxation: certified centre boxes from wall membership '
  '(x in [1/2, sqrt2/2] on a wall, [s-sqrt2/2, s-1/2] on the far wall, s in '
  '[3.80, 3.8771]), the universal centre separation >= 1 for interior-disjoint unit '
  'squares, and the chain bound |c_i-c_j| <= sqrt2 * hop-distance. No triangle '
  'closure, no full distance-geometry feasibility, no tilt information. It can only '
  'ADMIT unrealizable graphs, never reject realizable ones. The 3.80 endpoint uses '
  'the certified lower bound s(11) >= 3.80 (A06/A07/A08); with only Stromquist '
  '(3.7889) the filter weakens slightly.')),
 dict(id='G4', kind='completeness', text=(
  'The core has EXACTLY k loaded squares; the other 11-k are rattlers / unloaded (L3 '
  'case i). The completion multiplicity (ways to park 11-k rattlers) is NOT counted, '
  'so the projected totals are PER CORE and the true structure count is larger.')),
 dict(id='G5', kind='branch bookkeeping', text=(
  'L2 degree-2 thin branches are kept and flagged. They are ~90% of all survivors '
  '(k=7: 753767 of 842398), so if L2 collinearity is ever upgraded to a hard prune '
  'the space shrinks by roughly one order of magnitude.')),
 dict(id='G6', kind='branch bookkeeping', text=(
  'The L3 self-stress branch and the lambda0=0 branch are counted SEPARATELY and are '
  'not part of MAIN. The lambda0=0 branch is large (k=7: 401250, ~48% of MAIN) and '
  'needs its own excludable row system, as drain_lemma requires.')),
 dict(id='G7', kind='soft filter', text=(
  'The Maxwell count m >= 3k+1 in its CERTAIN form (all contacts point contacts, '
  'm = |E|) is satisfied by ZERO survivors at every k: planarity caps |E| at 3k+2 and '
  'no survivor reaches 3k+1. So every candidate needs flush contacts (2 rows each). '
  'If Maxwell is ever proved necessary it becomes a very strong filter, forcing at '
  'least 3k+1-|E| flush edges; it is NOT applied here (the ledger marks it soft).')),
 dict(id='G8', kind='Level 1 approximation', text=(
  'Level 1 checks the TILT subsystem only, and does so exactly (equalities mod 90 by '
  'union-find, a zero class from wall-flush, strict inequalities from corner-on-edge, '
  'feasible iff the class digraph is acyclic and nothing sits below phi=0). Positions '
  'are never checked: whether the touching corner actually lands inside the unit edge, '
  'non-overlap of non-adjacent squares, and containment are all ignored. The Level-1 '
  'fan-out is therefore an UPPER bound.')),
 dict(id='G9', kind='Level 1b partial', text=(
  'The rotation-system (planar embedding) consistency test is applied only to the '
  'square-square subgraph, because the rotation at a wall node (the order of squares '
  'along that wall) is not determined by a decoration. Including the walls, and '
  'requiring the embedding to be consistent with the L4 drawing, would strengthen it '
  'further. It is measured by Monte Carlo, not enumerated.')),
 dict(id='G10', kind='sampling', text=(
  'Level-1 per-graph counts are exact; the per-k aggregate uses <= 160 sampled '
  'graphs, weighted by the MAIN count of their A-rep (reservoir sampling is uniform '
  'within an A-rep, so the estimator is unbiased across A-reps, but sampling error '
  'remains, especially in the max column).')),
 dict(id='G11', kind='extrapolation', text=(
  'Level 2 is extrapolation, not a bound. Three models are fitted to k=3..7 and the '
  'k=7 point is used as a one-step holdout for models fitted on k=3..6. The spread '
  'between models at k=11 is about a factor of 20.')),
 dict(id='G12', kind='budget', text=(
  'Level 0 is exhaustive only for k = 3..7. Measured cost of k=8 with the present '
  'code is ~120 core-hours (5.3e11 mask rows); k >= 9 needs an orderly generator with '
  'metric pruning inside the generation, plus a canonical-labelling routine that does '
  'not enumerate k! permutations.')),
 dict(id='G13', kind='encoding', text=(
  "The brief's raw decoration menu (48 per square-square edge, 8 per square-wall "
  'edge) is an un-gauge-fixed encoding and is redundant non-uniformly. All decoration '
  'counts here are gauge-fixed (20 per SS edge, 2 per SW edge), where each label is '
  'one physically distinct arrangement.')),
 dict(id='G14', kind='not modelled', text=(
  'Not used at all, and each would shrink the space: L5(c)-style strip capacity '
  'counts (soft), the A23/A25/A26 area-wastage ledger, A22-style local rigidity, '
  'the requirement that the FJ system of a structure actually has a solution with '
  'sigma <= s0, and any use of the known certified lower bound beyond the box '
  'endpoints.')),
]


if __name__ == '__main__':
    main()
