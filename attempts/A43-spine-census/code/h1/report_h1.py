"""A43-H1 report assembly -> results/h1/h1_report.json (the json findings array IS the report)."""
import json, os, math, datetime

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'h1')
KS = [3, 4, 5, 6, 7]


def J(n):
    p = os.path.join(RES, n)
    return json.load(open(p)) if os.path.exists(p) else None


def fmt(x):
    return '%.3e' % x if isinstance(x, float) and abs(x) >= 1e4 else x


def main():
    L0 = {k: J('level0_k%d.json' % k) for k in KS}
    L0 = {k: v for k, v in L0.items() if v}
    ks = sorted(L0)
    L1 = J('level1.json')
    L2 = J('level2.json')
    FI = J('field_info.json')
    REG = J('regression.json')
    TR = J('trump_canary.json')
    HC = J('handcheck_n1.json')
    WF = J('l1_wallflush_n5.json')
    A31 = {k: json.load(open(os.path.join(RES, '..', '..', '..', 'A31-structure-count',
                                          'results', 'level0_k%d.json' % k))) for k in ks}

    rep = {}
    rep['what'] = ('A43 H1: the A31 structure census re-run with the 2026 theorem library as '
                   'additional filters, per-filter ablation, exact vs conditional vs approximate '
                   'labelled. Level 0 exhaustive and orbit-exact (S_k x D4) for k = 3..7.')
    rep['when'] = datetime.datetime.now().isoformat(timespec='seconds')
    rep['field'] = dict(
        chosen=FI['field'], cert=FI['cert'], n_atoms=FI['n_atoms'],
        d4_defects=FI['d4_defects'], total_mass_exact=FI['total'],
        eta_cert_exact=FI['eta_cert'], eta_cert_float=FI['eta_float'],
        W1_threshold_exact='1 + eta = ' + FI['thr1_exact'], W1_threshold_float=FI['thr1_float'],
        W2_threshold_exact='2 + eta = ' + FI['thr2_exact'], W2_threshold_float=FI['thr2_float'],
        note=('A39 resealed field selected: the artifact AND its standalone verification report '
              '(result PASS, margin 0, s = 969271/250000) are both present, per the H1 brief. '
              'The A33 fallback (eta = 1661717/3906250 = 0.425399552) was NOT used. Field is '
              'exactly D4-closed (0 defects).'),
        grid=FI['grid'])

    rep['filter_ledger'] = [
        dict(id='N1', filter='per-wall <= 3', klass='EXACT', level='L0',
             use='NEW HARD ablation row R11 (A31 soft bit 16 promoted); old soft column kept'),
        dict(id='N2', filter='A38.1 interior occupancy: all-wall core is dead',
             klass='EXACT-EXISTENTIAL', level='L0 column + k=11 join',
             use='column only for k < 11 (the A38.1 witness may be a rattler); hard at k=11'),
        dict(id='N3', filter='A21 THM3 orientation; necessary condition = no zero-pinned class',
             klass='EXACT-EXISTENTIAL', level='L1 column + k=11 join'),
        dict(id='N4', filter='Maxwell flush-mandatory (2E >= 3k+1 at L0, #flush >= 3k+1-E at L1)',
             klass='CONDITIONAL', level='L0+L1 columns',
             use='provenance check: structure_lemmas.md marks m >= 3k+1 SOFT, NOT a theorem; '
                 'reported both ways, never in the composed exact count'),
        dict(id='N5', filter='W1 tight-variety: certified m_low over a placement window > 1+eta',
             klass='EXACT', level='L0+L1'),
        dict(id='N6', filter='W2 pair tight-sum: m_low(i) + m_low(j) > 2+eta kills the pair',
             klass='EXACT', level='L0+L1'),
        dict(id='N7', filter='wastage motifs: (a) any square-square 4-cycle; (d) 4-cycle with '
                             'all four links corner-on-edge in a common (18,45) deg band',
             klass='APPROX', level='L0+L1 columns', use='NEVER composed; see finding on Trump'),
        dict(id='N8', filter='band count (A26.1/A28.*): at most one square with wall clearance '
                             '>= 0.938542', klass='EXACT but inert here', level='-',
             use='0-cost column: a mask-0 centre box cannot certify clearance either way, so the '
                 'filter has no L0 handle. Recorded so it is not re-spent on.')]

    # ------------------------------------------------------------------ ablation table
    rows = ['R0 no filter', 'R2 +L5b', 'R3 +L1', 'R4 +L5d', 'R5 +L4a', 'R6 +L5a', 'R7 +L3',
            'R8 +L6', 'R9 +L4b', 'R10 +L7', 'R11 +N1 (NEW HARD, EXACT)',
            'R12 +N5 +N6 (NEW HARD, EXACT)']
    tab = {}
    for k in ks:
        d = L0[k]
        vals = [d['R0_no_filter'], d['R2_L5b']] + list(d['cum'])
        tab['k%d' % k] = dict(zip(rows, vals))
        tab['k%d' % k]['A31_R10_reference'] = A31[k]['cum'][7]
    rep['ablation_cumulative_orbit_counts'] = dict(
        rows_meaning=rows, table=tab,
        note='R0..R10 are A31 verbatim and reproduce exactly (see verification.regression). '
             'R11/R12 are new. R12 = R11 at every k: N5 and N6 kill nothing at Level-0 window '
             'scale.')

    cols = {}
    for k in ks:
        d, n = L0[k], L0[k]['new']
        cols['k%d' % k] = {
            'MAIN (A31 hard branch)': d['branch']['main'],
            'MAIN thin (L2)': d['branch']['thin_main'],
            'N1 MAIN&N1  [EXACT]': n['main_N1'],
            'N5 kills on MAIN  [EXACT]': n['main_N5dead'],
            'N6 kills on MAIN, contact edges  [EXACT]': n['main_N6dead_edge'],
            'N6 kills on MAIN, all pairs  [EXACT]': n['main_N6dead_pair'],
            "MAIN' = MAIN&N1&N5&N6  [EXACT composed]": n['mainprime'],
            "MAIN' non-thin  [EXACT composed]": n['mainprime_nonthin'],
            'N2 all-wall, of MAIN  [EXACT-EXISTENTIAL]': n['main_allwall'],
            'N2 all-wall, of MAIN&N1  [EXACT-EXISTENTIAL]': n['main_N1_allwall'],
            'N4 2E>=3k+1, of MAIN  [CONDITIONAL]': n['main_N4'],
            "N4 2E>=3k+1, of MAIN'  [CONDITIONAL]": n['mainprime_N4'],
            'N7a has 4-cycle, of MAIN  [APPROX]': n['main_4cyc'],
            "N7a has 4-cycle, of MAIN'  [APPROX]": n['mainprime_4cyc'],
            'A-reps containing a 4-cycle': '%d/%d' % (d['n_areps_with_4cycle'], d['n_areps'])}
    rep['level0_columns'] = cols

    kf = {}
    for k in ks:
        d, n = L0[k], L0[k]['new']
        m = d['branch']['main']
        kf['k%d' % k] = {
            'N1 keep-factor on MAIN': n['main_N1'] / m,
            'N5 keep-factor': 1.0 - n['main_N5dead'] / m,
            'N6 keep-factor': 1.0 - n['main_N6dead_edge'] / m,
            "composed EXACT keep-factor MAIN'/MAIN": n['mainprime'] / m,
            'N2 all-wall share of MAIN&N1 (existential)': n['main_N1_allwall'] / n['main_N1'],
            'N4 share of MAIN (conditional)': n['main_N4'] / m,
            'N7a share of MAIN (approx)': n['main_4cyc'] / m,
            'L2-thin share of MAIN': d['branch']['thin_main'] / m}
    rep['per_filter_kill_factors'] = kf

    # ------------------------------------------------------------------ level 1
    if L1:
        rep['level1'] = {
            'protocol': 'A31 level1.py sampling protocol: reservoir of <=40 MAIN survivors per '
                        'A-rep, numpy default_rng(7), cap 160 (k<=6) / 40 (k=7); gauge-fixed '
                        'menu 20 per square-square edge, 2 per square-wall edge.',
            'per_k': {kk: {a: b for a, b in v.items() if a != 'rows'} for kk, v in L1.items()},
            'N3_column': 'we_surv_nozero / we_surv = share of tilt-feasible decorations with NO '
                         'zero-pinned class  [EXACT-EXISTENTIAL]',
            'N4_column': 'we_surv_N4 / we_surv = share with #flush >= 3k+1-E  [CONDITIONAL]',
            'N7d_column': 'we_surv_N7d / we_surv = share containing a 4-cycle whose four links '
                          'are all corner-on-edge  [APPROX]',
            'walledge_crosscheck': 'we_surv (wall-edge-resolved re-enumeration: each square-wall '
                                   'edge independently flush/corner, with the phi=0 vs phi!=0 '
                                   'consistency constraint) equals A31 gauge_surv at EVERY '
                                   'sampled graph, ratio 1.0 -- an independent confirmation of '
                                   "A31's wall-class enumeration."}
    if WF:
        rep['level1_N5_wallflush'] = WF

    if L2:
        rep['extrapolation'] = dict(
            series=L2['series'], fits=L2['fits'], holdout_k7=L2['holdout'],
            projection_level0=({n: v for n, v in L2['projection'].items()
                                if n not in ('composed_totals',)}),
            composed_totals=L2['projection']['composed_totals'])
        rep['k11_join'] = L2['k11_join']

    rep['comparison_to_A31'] = {
        'A31_headline_k11_composed': {'M1_exp': 4.15e29, 'M2_logquad': 3.26e30,
                                      'M3_ratio_lin': 2.22e30},
        'A31_best_case_if_every_cheap_improvement_lands': 2.5e25}
    if L2:
        ct = L2['projection']['composed_totals']
        rep['comparison_to_A31']['A43_k11_composed_EXACT'] = {
            m: ct['MAINprime_exact'][m]['k11'] for m in ct['MAINprime_exact']}
        rep['comparison_to_A31']['A43_k11_composed_EXACT_nonthin'] = {
            m: ct['MAINprime_nonthin'][m]['k11'] for m in ct['MAINprime_nonthin']}
        rep['comparison_to_A31']['A43_k11_composed_CONDITIONAL_N4'] = {
            m: ct['MAINprime_N4_conditional'][m]['k11'] for m in ct['MAINprime_N4_conditional']}

    rep['verification'] = dict(
        a_regression=REG,
        a_regression_level1=('gauge_surv_geomean_weighted reproduces A31 level2 measured_surv '
                             'exactly at k = 3,4,5,6,7'),
        b_trump_canary={c['name']: ('PASS' if c['pass_'] else 'FAIL') +
                        ('' if not c.get('detail') else '  [%s]' % c['detail'])
                        for c in TR['checks']} if TR else None,
        b_trump_verdict=TR['verdict'] if TR else None,
        b_trump_extra=dict(wall_degrees_LBRT=TR['wall_degrees_LBRT'],
                           n_interior_squares=TR['n_interior_squares'],
                           max_coverage=max(TR['trump_coverage_float']),
                           threshold=TR['field']['thr1_float'],
                           has_4cycle=TR['trump_has_4cycle']) if TR else None,
        c_handcheck_k4_N1=HC)

    rep['gaps'] = [
        dict(id='G-A43-1', kind='measurement (the headline gap)',
             text='N5 (W1) and N6 (W2) are EXACT and were applied at the Level-0 window scale, '
                  'and they kill NOTHING: the certified m_low over a wall-mask centre box '
                  '(x full tilt t in [0,1]) is 0.000000 for all 9 admissible masks, against the '
                  'threshold 1 + eta = 1.40295728. The windows are the whole container up to a '
                  'wall strip; no atomic-measure lower bound survives that much translation '
                  'freedom. The filters are sound and simply have no purchase on a purely '
                  'combinatorial structure -- they need position information the census does '
                  'not carry.'),
        dict(id='G-A43-2', kind='existential/vacuous',
             text='N2 and N3 are EXACT but EXISTENTIAL over the 11 squares. On a loaded core of '
                  'k < 11 the A38.1 / THM3 witness may be one of the 11-k rattlers, so neither '
                  'is a legitimate prune below k = 11. They are reported as columns and folded '
                  'in only in the k = 11 projection.'),
        dict(id='G-A43-3', kind='provenance correction',
             text='The A43 brief lists flush-mandatory (Maxwell m >= 3k+1) as certified. The '
                  'provenance check says it is NOT: docs/proofs/structure_lemmas.md marks it '
                  'SOFT ("NOT a theorem - degenerate structures can jam with fewer independent '
                  'rows") and A32-H1 resolved it as unusable. It is therefore reported only as '
                  'a labelled CONDITIONAL column, never composed into the exact count.'),
        dict(id='G-A43-4', kind='approximation (over-kill), CONFIRMED BY CANARY',
             text="N7's graph-level proxies over-kill. Trump's own contact graph CONTAINS a "
                  '4-cycle, so the N7a proxy would remove the known optimum. This is exactly the '
                  'realizability caveat A25 recorded, now demonstrated on a realized packing. '
                  'N7a/N7d are report-only columns and must never be composed. Note also that '
                  "N7d's extra condition -- \"tilt classes admit a common assignment in (18,45) "
                  'deg" -- is VACUOUS at this resolution: any acyclic orientation of a 4-cycle is '
                  'realisable by 4 distinct tilt values inside any open interval, so N7d reduces '
                  'to "some 4-cycle has all four links corner-on-edge".'),
        dict(id='G-A43-5', kind='soundness of the N5/N6 window semantics',
             text='Centre boxes use lib0._box semantics with the EXACT s0 = 969271/250000 upper '
                  'endpoint and the certified lower endpoint s >= 3.80, so they are valid for '
                  'every container side in [3.80, s0]; float endpoints are widened outward by '
                  '1e-9 before certification (a larger window can only lower m_low, so the kill '
                  'test stays one-sided). m_low is the max of two independent valid lower '
                  'bounds: an exact-rational single-box evaluation (A38 mlow_box_exact) and the '
                  'min over all dense-grid cells meeting the box.'),
        dict(id='G-A43-6', kind='inherited from A31',
             text='All of A31 gaps G1-G7 still apply unchanged: L7 is a statement about the '
                  'active-contact graph G not the support graph H (column only); the core has '
                  'exactly k loaded squares and rattler completion multiplicity is NOT counted; '
                  'L2 degree-2 thin branches are kept and flagged; the L3 self-stress and '
                  'lambda0 = 0 branches are counted separately and are not in MAIN.'),
        dict(id='G-A43-7', kind='extrapolation, not a bound',
             text='Everything at k = 8..11 is a fit of k = 3..7 counts under three models with a '
                  'k = 7 holdout, exactly as in A31. It is an extrapolation, not a bound, and '
                  'the decoration fan-out multiplier is a fitted mean over a 160-graph sample.'),
        dict(id='G-A43-8', kind='resolution',
             text='The L1 wall-flush N5 scan partitions the free along-wall coordinate into 2000 '
                  'slabs (and, for the right/top walls, the pinned coordinate into 40). A finer '
                  'partition can only RAISE the certified m_low, so the reported exempt fraction '
                  'is a lower bound on what this filter can restrict; the no-kill verdict '
                  '(m_low min < 1+eta) is likewise resolution-limited and could in principle '
                  'change under refinement.')]

    ct = L2['projection']['composed_totals'] if L2 else {}
    kf7 = kf['k7']
    n1keep = {k: round(kf['k%d' % k]['N1 keep-factor on MAIN'], 4) for k in ks}
    aw = L2['k11_join']['N2_allwall_frac_of_MAIN_N1'] if L2 else {}
    n4l1 = L2['fits']['fanout']['N4_frac'] if L2 else {}
    n7l0 = {k: round(kf['k%d' % k]['N7a share of MAIN (approx)'], 4) for k in ks}

    rep['findings'] = [
        'FIELD: the A39 resealed guard field was used (artifact + standalone PASS report both '
        'present). eta_cert = 2518483/6250000 = 0.40295728 EXACTLY, so the W1 threshold is '
        '1 + eta = 8768483/6250000 = 1.40295728 and the W2 threshold is 2 + eta = '
        '15018483/6250000 = 2.40295728. The A33 fallback (eta = 0.425399552) was not needed. '
        'The field is exactly D4-closed (0 defects over 1468 atoms).',

        'REGRESSION PASS. With the new filters off, every number in A31 level0_k{3..7}.json '
        '(cum, marg, soft, branch, Ehist, Burnside rows) reproduces EXACTLY, and the Level-1 '
        'weighted geometric-mean decoration counts reproduce A31 exactly at every k '
        '(271, 1.733e4, 2.179e6, 3.298e8, 4.095e10). The refitted k=11 composed totals '
        'reproduce A31 headline to the digit: 4.153e29 / 3.255e30 / 2.223e30.',

        'N1 (per-wall <= 3) is the ONLY member of the 2026 library that bites at Level 0, and it '
        'is now a HARD row (R11). Keep-factor on MAIN: %s. It weakens as k grows only slowly and '
        'is worth x1.35 at k=7.' % n1keep,

        'N5 (W1 tight-variety) and N6 (W2 pair tight-sum) are EXACT and kill NOTHING at Level 0: '
        'the certified m_low over the centre box of EVERY one of the 9 admissible wall masks '
        '(full tilt t in [0,1]) is exactly 0.000000, against the threshold 1.40295728. R12 = R11 '
        'at every k. This is a measurement, not a failure: the same field pointwise exempts '
        '7.13%% of admissible (t,cx,cy) grid cells at that threshold, so the kill power exists '
        'but a wall-mask window is ~10^6 times too coarse to see it. The guard field needs '
        'POSITION information that a combinatorial structure does not carry.',

        "COMPOSED EXACT count MAIN' = MAIN & N1 & N5 & N6 (= MAIN & N1, since N5/N6 are inert): "
        '%s at k = 3..7. Non-thin: %s.'
        % ({k: L0[k]['new']['mainprime'] for k in ks},
           {k: L0[k]['new']['mainprime_nonthin'] for k in ks}),

        'HEADLINE: the whole 2026 theorem library buys a factor of about 2 on the k=11 structure '
        'count. Composed EXACT k=11 projection %s versus A31 4.15e29 / 3.26e30 / 2.22e30. '
        "MAIN' non-thin gives %s. A31's GO/NO-GO verdict is unchanged: an enumerate-then-solve "
        'structure-first campaign at k=11 remains non-viable.'
        % ({m: '%.3e' % ct['MAINprime_exact'][m]['k11'] for m in ct['MAINprime_exact']},
           {m: '%.3e' % ct['MAINprime_nonthin'][m]['k11'] for m in ct['MAINprime_nonthin']}),

        'N2 (A38.1 all-wall kill) at the k=11 JOIN: the all-wall share of MAIN&N1 decays '
        'exponentially in k (%s), fit log frac = 2.2270 - 0.7795 k, extrapolating to 1.75e-03 at '
        'k=11. So the one place where N2 is a legitimate hard kill it removes about 0.2%% of the '
        'k=11 graph count. There is also an exact combinatorial squeeze: under N1 the four walls '
        'carry at most 12 square-wall incidences, so an all-wall k=11 core has at most ONE '
        'corner square.' % {k: round(v, 4) for k, v in aw.items()},

        'N3 (A21 THM3) at the k=11 JOIN: two thirds of tilt-feasible decorations already carry a '
        'zero-pinned tilt class (a wall-flush edge forces phi = 0, which satisfies THM3 for '
        'free). The no-zero-class share is FLAT in k (%s) and extrapolates to 0.314 at k=11, so '
        'THM3 can bite on at most ~31%% of decorated k=11 structures -- and only on the subset of '
        'those in which the tilt system FORCES all 11 tilts into (18,27)u(63,72) deg, which this '
        'census does not test. THM3 is not a bulk filter.'
        % {k: round(v, 4) for k, v in L2['k11_join']['N3_frac_no_zero_class'].items()},

        'N4 (Maxwell flush-mandatory) is CONDITIONAL, not certified -- the provenance check '
        'contradicts the A43 brief (structure_lemmas.md marks m >= 3k+1 SOFT and A32-H1 ruled it '
        'unusable). Two measurements: (i) at Level 0 the column 2E >= 3k+1 is IMPLIED by '
        'non-thinness -- min total degree 3 gives 2E >= 3k and at least one wall edge gives '
        '2E >= 3k+1 -- which is why MAIN\'&N4&non-thin equals MAIN\'&non-thin at every k; '
        '(ii) at Level 1 the flush-mandatory share of decorations collapses with k (%s), '
        'extrapolating to 6.3e-04 at k=11. If Maxwell were ever proved, the composed k=11 total '
        'would fall to %s, and with non-thinness to %s -- i.e. to A31\'s own best case of ~2.5e25. '
        'Maxwell is the single biggest available lever and it is the one that is unproven.'
        % ({k: round(v, 4) for k, v in n4l1.items()},
           {m: '%.3e' % ct['MAINprime_N4_conditional'][m]['k11']
            for m in ct['MAINprime_N4_conditional']},
           {m: '%.3e' % ct['MAINprime_N4_nonthin_conditional'][m]['k11']
            for m in ct['MAINprime_N4_nonthin_conditional']}),

        "N7 (wastage motifs) OVER-KILLS THE KNOWN OPTIMUM: Trump's contact graph contains a "
        '4-cycle, so the N7a proxy would delete the realized packing. The proxy share of MAIN '
        'grows fast with k (%s) and at Level 1 the all-corner-on-edge 4-cycle share reaches 0.44 '
        'weighted / 0.96 median at k=7, so it LOOKS like the strongest filter available and is '
        'in fact unsound as stated. A23/A25 kill specific certified CELLS, not graph motifs; the '
        'realizability caveat A25 recorded is now demonstrated on a realized packing.' % n7l0,

        'N5 DOES bite at Level 1, partially. On the wall-flush pinned window (tilt exactly 0, '
        'centre exactly 1/2 from the wall, along-wall coordinate free) the certified m_low runs '
        'from 1.013644 to 1.437085 against the threshold 1.402957, and 36 of 2000 slabs -- 1.8%% '
        'of the along-wall range -- are certified EXEMPT, identically on all four walls. So W1 '
        'does not forbid wall-flush contacts, but it does forbid 1.8%% of their positions. This '
        'is the only place in the census where the guard field actually cuts, and it cuts only '
        'because the decoration pins two of the three placement coordinates.',

        'TRUMP CANARY PASS (20/20 checks). Wall degrees 3/3/3/2 exactly meet the new N1 cap; 3 '
        'squares are interior so N2 correctly does not fire; max exact coverage 1.137624852 vs '
        'threshold 1.402957280 (slack 0.265); worst exact pair sum 2.207686884 vs 2.402957280; '
        'total coverage 11.375094588 vs total field mass 11.402957280 (slack 0.0279); no Trump '
        'placement lies in an exempt eroded grid cell (A38 canary cross-check).',

        'INDEPENDENT CROSS-CHECK of A31 Level 1: a wall-edge-resolved re-enumeration (each '
        'square-wall edge chosen flush or corner independently, with the phi = 0 versus phi != 0 '
        'consistency constraint) reproduces A31\'s wall-CLASS enumeration exactly -- ratio 1.000 '
        'on every sampled graph at every k. A31\'s decoration count was suspected of '
        'under-counting the 2^Esw wall menu; it does not.',

        'BOTTOM LINE for the PI bulk-kill thesis: no certified theorem proven since A31 bulk-kills '
        'structures. Each one fails for a different structural reason -- N2/N3 are EXISTENTIAL '
        'and therefore vacuous on a k<11 core; N5/N6 are POSITIONAL and a contact structure '
        'carries no position; N4 is UNPROVEN; N7 is UNSOUND as a motif filter (it kills Trump). '
        'Only N1, which was already computed as a soft column in A31, survives as a hard prune, '
        'and it is worth x1.35 at k=7. The composed exact k=11 count moves from 4.15e29 to '
        '2.30e29.']

    json.dump(rep, open(os.path.join(RES, 'h1_report.json'), 'w'), indent=1, default=float)
    print('wrote h1_report.json')
    return rep


if __name__ == '__main__':
    main()
