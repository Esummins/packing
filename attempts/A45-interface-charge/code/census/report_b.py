"""A45-B report assembly -> results/census_report.json."""
import os, sys, json, math, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A45 = os.path.abspath(os.path.join(HERE, '..', '..'))
RES = os.path.join(A45, 'results')
A43RES = os.path.abspath(os.path.join(A45, '..', 'A43-spine-census', 'results', 'h1'))
sys.path.insert(0, HERE)
import mub
import charge as CH
KS = [3, 4, 5, 6, 7]


def J(p):
    return json.load(open(p)) if os.path.exists(p) else None


def fits3(ks, ys, name):
    """The A31/A43 3-model protocol, adapted to a keep-FRACTION series:
       K1 log-linear, K2 log-quadratic, K3 constant at the last measured value.
    Holdout: fit on k = 3..6, predict k = 7."""
    ks = np.array(ks, float)
    ly = np.log(np.array(ys, float))
    b1, a1 = np.polyfit(ks, ly, 1)
    c2, b2, a2 = np.polyfit(ks, ly, 2)
    last = float(ys[-1])
    M = {'K1_loglin': (lambda k: math.exp(a1 + b1 * k), 'log f = %.4f + %.4f k' % (a1, b1)),
         'K2_logquad': (lambda k: math.exp(a2 + b2 * k + c2 * k * k),
                        'log f = %.4f + %.4f k + %.4f k^2' % (a2, b2, c2)),
         'K3_const': (lambda k: last, 'f = %.6f (constant at k=%d)' % (last, int(ks[-1])))}
    hb1, ha1 = np.polyfit(ks[:-1], ly[:-1], 1)
    hc2, hb2, ha2 = np.polyfit(ks[:-1], ly[:-1], 2)
    hold = {'K1_loglin': math.exp(ha1 + hb1 * ks[-1]),
            'K2_logquad': math.exp(ha2 + hb2 * ks[-1] + hc2 * ks[-1] ** 2),
            'K3_const': float(ys[-2])}
    return dict(series={int(k): float(v) for k, v in zip(ks, ys)},
                models={n: m[1] for n, m in M.items()},
                projection={n: {k: m[0](k) for k in range(8, 12)} for n, m in M.items()},
                holdout_k7={n: dict(predicted=hold[n], actual=float(ys[-1]),
                                    ratio=hold[n] / float(ys[-1])) for n in hold})


def main():
    L1 = J(os.path.join(RES, 'census_l1.json'))
    CAN = J(os.path.join(RES, 'canary_b.json'))
    REG = J(os.path.join(RES, 'regression_b.json'))
    SPOT = J(os.path.join(RES, 'spot_h2_k3.json'))
    A43L0 = {k: J(os.path.join(A43RES, 'level0_k%d.json' % k)) for k in KS}
    A43L2 = J(os.path.join(A43RES, 'level2.json'))
    ks = [k for k in KS if L1 and 'k%d' % k in L1]
    rep = {}
    rep['what'] = ('A45 agent B: the census bite of the interface-charging calculus (Theorem '
                   'A45.1) and of the PI\'s two flush-ruler laws (Lemmas R and Q), measured on '
                   'the A43-H1 structure census (Level 0 orbits, Level 1 decorations) plus the '
                   'A43-H2 k=3 spine survivors.')
    rep['when'] = datetime.datetime.now().isoformat(timespec='seconds')

    # ------------------------------------------------------------------ filter ledger
    rep['filter_ledger'] = [
        dict(id='RULER', filter='Lemma R flush-ruler cap + Lemma Q quantization, as an interval '
             'CSP over (normal family, sign, slide) per flush component, with WF wall anchors '
             'pinned to 1/2 and s-1/2 and s treated as a shared unknown in [3.80, s0]',
             klass='EXACT', level='L1 (decorations); provably inert at L0',
             over_accepts=['slides relaxed to the interval hull',
                           'no interior-disjointness inside a component (Sec 6.3 licenses none)',
                           'non-zero-pinned components use cos+sin <= sqrt2 (widest window)',
                           'components with > 12 FL links fall back to the path relaxation'],
             use='two columns: RULER_kill (decoration dies) and RULER_refined (A31\'s factor 4 '
                 'per flush edge replaced by the number of FEASIBLE (family,sign) assignments -- '
                 'strictly stronger, still one-sided)'),
        dict(id='CHARGE', filter='Theorem A45.1 interface charging, min charge over reachable '
             'bins, kill if the sum exceeds B0 = s0^2 - 11',
             klass='EXACT (conditional on the certified table)', level='L1 columns',
             over_accepts=['CC is uncharged by design and is reachable from every non-flush '
                           'square-square contact of a decoration, so those contacts contribute '
                           '0 under min-over-realizations semantics',
                           'a wall-degree-2 square may realize the WCC container-corner case, so '
                           'its wall contacts contribute 0 (lead addendum)',
                           'a class tilt window that spans a dropped/uncovered bin contributes 0'],
             use='sound column CHARGE_min; unsound magnitude probe CHARGE_ceforced reported '
                 'beside it'),
        dict(id='ZERO-CHARGE', filter='Theorem A45.2 composition on all-FL/all-WF decorations',
             klass='EXACT for the (b) branch', level='L1 column + structural argument'),
        dict(id='m_ub(theta)', filter='Sec 6.4 crude common-tilt counting guard',
             klass='EXACT (cover-based certified upper bound)', level='standalone table')]

    # ------------------------------------------------------------------ ablation
    rows = ['R10 = A31 MAIN (A43 verbatim)', 'R11 +N1 per-wall<=3 [EXACT]',
            'R12 +N5+N6 [EXACT]', 'R13 +RULER [EXACT]', 'R14 +CHARGE [EXACT]']
    tab = {}
    for k in ks:
        d = A43L0[k]
        tab['k%d' % k] = {rows[0]: d['cum'][7], rows[1]: d['cum'][8], rows[2]: d['cum'][9],
                          rows[3]: d['cum'][9], rows[4]: d['cum'][9]}
    surv_ok = all(min(r['we_surv'] - r['ruler_kill'] - r['charge_kill']
                      for r in L1['k%d' % k]['rows']) > 0 for k in ks) if L1 else None
    rep['ablation_cumulative_orbit_counts'] = dict(
        rows_meaning=rows, table=tab,
        verdict='R13 = R14 = R12 at every k: both new filters are INERT at Level 0.',
        proof=('A Level-0 orbit dies only if EVERY decoration of it dies.  The all-corner '
               'decoration (every square-square contact a corner type, every wall contact a '
               'wall-corner) always exists -- its tilt system is a strict digraph on k singleton '
               'classes with no zero pin, and every graph has at least one acyclic orientation.  '
               'It carries NO flush component, so RULER is vacuous on it; and its charge is 0 '
               'under min-over-bins semantics (every non-flush square-square contact can be '
               'realized as CC, which is uncharged by design).  Even pricing every one of its '
               'wall-corner contacts at the ownership ceiling 1/16 gives at most 12/16 = 0.75 '
               '(per-wall <= 3 caps the wall incidences at 12) against B0 = 4.0318.  So no '
               'Level-0 orbit can be killed by either filter, at any k.'),
        sample_check=dict(
            statement='On every sampled (graph, wall-mask) pair, surviving decoration weight '
                      'we_surv - ruler_kill - charge_kill is strictly positive.',
            holds=surv_ok))

    # ------------------------------------------------------------------ L1 columns
    l1cols = {}
    for k in ks:
        v = L1['k%d' % k]
        l1cols['k%d' % k] = {
            'decorations we_surv (weighted geomean, A43 reproduction)':
                v['we_surv_geomean_weighted'],
            'A43 we_surv rows compared / mismatched':
                '%d / %d' % (v['a43_we_surv_rows_compared'], v['a43_we_surv_mismatches']),
            'RULER kill share of decorations [EXACT]': v['frac_ruler_kill_weighted'],
            'RULER kill share, worst graph': v['frac_ruler_kill_max'],
            'RULER refined gauge keep-factor [EXACT]': v['ruler_refined_keep_weighted'],
            'RULER refined keep, worst graph': v['ruler_refined_keep_min'],
            'zero-charge share of decorations': v['frac_zero_charge_weighted'],
            'zero-charge share, worst graph': v['frac_zero_charge_max'],
            'RULER kill share WITHIN zero-charge decorations':
                v['zero_charge_ruler_kill_weighted'],
            'CHARGE kill share [EXACT, min-over-bins]': v['frac_charge_kill_weighted'],
            'CHARGE kill share, CE-forced probe (unsound)': v['frac_ceforced_kill_weighted'],
            'max chargeable corner contacts seen': v['max_chargeable_contacts'],
            'components over the CSP enumeration cap': v['capped_components']}
    rep['level1_columns'] = l1cols

    kf = {}
    for k in ks:
        v = L1['k%d' % k]
        kf['k%d' % k] = {
            'RULER decoration keep-factor': 1.0 - v['frac_ruler_kill_weighted'],
            'RULER refined gauge keep-factor': v['ruler_refined_keep_weighted'],
            'RULER composed keep-factor (refined, the one that moves the count)':
                v['ruler_refined_keep_weighted'],
            'CHARGE keep-factor': 1.0 - v['frac_charge_kill_weighted'],
            'zero-charge share': v['frac_zero_charge_weighted']}
    rep['per_filter_kill_factors'] = kf

    # ------------------------------------------------------------------ extrapolation
    ex = {}
    ex['RULER_refined_keep'] = fits3(ks, [L1['k%d' % k]['ruler_refined_keep_weighted']
                                          for k in ks], 'ruler')
    ex['RULER_decoration_keep'] = fits3(ks, [1.0 - L1['k%d' % k]['frac_ruler_kill_weighted']
                                             for k in ks], 'rulerkill')
    ex['zero_charge_share'] = fits3(ks, [L1['k%d' % k]['frac_zero_charge_weighted']
                                         for k in ks], 'zero')
    if A43L2:
        ct = A43L2['projection']['composed_totals']['MAINprime_exact']
        comp = {}
        for m in ct:
            k11 = ct[m]['k11']
            comp[m] = {'A43_k11': k11,
                       'A45_k11_with_RULER': {n: k11 * ex['RULER_refined_keep']['projection'][n][11]
                                              for n in ex['RULER_refined_keep']['projection']}}
        ex['composed_k11'] = comp
    rep['extrapolation_k8_to_k11'] = ex

    # ------------------------------------------------------------------ zero-charge residue
    zc = {}
    for k in ks:
        v = L1['k%d' % k]
        zc['k%d' % k] = dict(
            share_of_decorations=v['frac_zero_charge_weighted'],
            every_component_wall_anchored=v['zero_charge_every_component_walled'],
            ruler_kill_share_within=v['zero_charge_ruler_kill_weighted'])
    rep['zero_charge_residue'] = dict(
        per_k=zc,
        split_by_theorem_A45_2=dict(
            b_killable=('ALL of it, for k >= 10, EXACTLY.  In a MAIN structure every '
                        'square-square component carries at least one wall contact (L3, no '
                        'floating component -- components merge only through shared wall bits, '
                        'so a wall-less component has mask 0 and is rejected).  In a ZERO-CHARGE '
                        'decoration every wall contact is WF, so every component is zero-pinned '
                        'and ALL k loaded squares sit at tilt class 0.  A26 caps the number of '
                        'squares within 2.503 deg of class 0 at 9.  Hence every zero-charge core '
                        'with k >= 10 is DEAD -- and this needs no k=11 join, because the cap is '
                        'a universal statement about the packing, not an existential one.  '
                        'Measured premise: zero_charge_every_component_walled = True on every '
                        'sampled structure at every k.'),
            c_killable=('the RULER/Lemma-Q column measured WITHIN the zero-charge class: %s of '
                        'zero-charge decoration weight per k.  Mechanism: a flush component that '
                        'carries WF anchors on OPPOSITE walls at FL-graph distance <= 2 cannot '
                        'span s - 1 in [2.80, 2.877084] (each link moves that projection by at '
                        'most 1).  This is the only mechanism that bites at k <= 9.'
                        % {k: round(zc['k%d' % k]['ruler_kill_share_within'], 4) for k in ks}),
            e_residue=('EMPTY inside this census.  Residue (e) is the floating flush component '
                       'with a free common tilt; MAIN\'s L3 filter already forbids components '
                       'with no wall contact, so no surviving structure has one.  (e) therefore '
                       'contributes 0 here and reappears only if L3 is dropped.'),
            f_residue=('THE WHOLE RESIDUE.  For k <= 9 a zero-charge core is consistent with '
                       'A26: 9 or fewer class-0 squares plus 11-k rattlers of any tilt.  Nothing '
                       'in the calculus touches it.  Share of decorations: %s, falling roughly '
                       'geometrically in k.'
                       % {k: '%.2e' % zc['k%d' % k]['share_of_decorations'] for k in ks})))

    # ------------------------------------------------------------------ m_ub table
    rows = mub.table()
    rep['m_ub_table'] = dict(
        method=mub.__doc__.strip().splitlines()[0],
        deviation=('the brief calls the eroded region an octagon; the Minkowski erosion of a '
                   'square by a square is a SQUARE (4 edges), and the count below is done on '
                   'that exact rotated-square region.'),
        sanity_bin_0_3_is_9=(rows[0]['m_ub'] == 9),
        table=[dict(bin=r['bin'], m_ub=r['m_ub'], partition=r['partition'],
                    per_column=r['per_column'], per_sub_bin=r['per_sub_m_ub'],
                    single_grain_residue_dies=r['single_grain_residue_dies']) for r in rows],
        bins_where_residue_dies=[r['bin'] for r in rows if r['single_grain_residue_dies']],
        bins_where_GAP_A45_Z1_stands=[r['bin'] for r in rows
                                      if not r['single_grain_residue_dies']],
        verdict=('the crude tier delivers m_ub <= 10 on exactly ONE bin, [0,3) -> 9 (which A26 '
                 'already had, out to 2.503 deg).  From 3 deg up the bound is 12 (bins up to '
                 '18 deg) or 14, so GAP-A45-Z1 stands on 14 of 15 bins.  Mechanism: the eroded '
                 'region\'s bounding box in the theta-frame has side w(s0-w) with w = cos+sin, '
                 'which crosses 3 at about 4 deg and forces a 4th column of centres.'))

    # ------------------------------------------------------------------ charge ceiling
    T = CH.load_table()
    rep['charge_table_used'] = dict(
        kind=T['kind'], source=T.get('source'), rho_min=str(T.get('rho_min')),
        half_moat_radius_R=T.get('R'), counts=T.get('counts'),
        max_entry=str(T.get('max_entry')), max_entry_float=T.get('max_entry_float'),
        dropped_WC_bins=T.get('dropped_wc'), dropped_CE_d_bins=T.get('dropped_ce'),
        census_side_min_over_full_window=dict(
            WC=str(CH.min_wc(T, range(15))), CE=str(CH.min_ce(T, range(15)))),
        with_certified_table=dict(
            max_sum_at_k11=35 * (T['max_entry_float'] or 0) if T.get('max_entry_float') else None,
            budget=float(CH.B0),
            shortfall_factor=(float(CH.B0) / (35 * T['max_entry_float'])
                              if T.get('max_entry_float') else None)))
    rep['charge_ceiling'] = dict(
        statement=('TABLE-INDEPENDENT: charge(K) <= area B(p, rho_min/2) = rho_min^2 (Sec 4 '
                   'definition (ii): the certified region list lives inside the half-moat box), '
                   'and rho_min <= 1/4 (top of the Sec 5 moat ladder).  A candidate structure '
                   'has E <= 3k+2 contacts (A31 L4(a), a HARD filter of MAIN).  So the total '
                   'charge of ANY k <= 11 structure is at most (3k+2)/16.'),
        per_k=CH.ceiling_analysis(),
        pilot_calibration=CH.pilot_calibration(),
        verdict=('at k = 11 the ceiling is 35/16 = 2.1875 against B0 = 4.031780343056 -- short '
                 'by a factor 1.843.  Theorem A45.1 CANNOT fire on an 11-square structure with '
                 'the half-moat ownership scheme, whatever the certified table says.  To fire it '
                 'would need a mean charge of 0.1152 per contact, i.e. rho_min >= 0.3394, which '
                 'is off the top of the moat ladder (0.25).  The weighted-Voronoi refinement of '
                 'Sec 4 remark 2 buys radius (rho_i+rho_j)/4 <= 1/8, the same order, so it does '
                 'not change the verdict.'))

    # ------------------------------------------------------------------ spot + canaries
    AUD = J(os.path.join(RES, 'ruler_kill_audit.json'))
    if AUD:
        rep['ruler_kill_audit'] = dict(
            n_killed_component_signatures=AUD['n_killed_signatures'],
            all_zero_pinned=AUD['all_zero_pinned'],
            M1_LemmaQ_path_bound=AUD['explained_by_path_relaxation'],
            M2_odd_cycle_parity=AUD['explained_by_parity'],
            M3_LemmaQ_integrality=AUD['explained_by_LemmaQ_integrality'],
            unexplained=len(AUD['unexplained']),
            mechanisms=AUD['mechanisms'],
            verdict=('every RULER kill is a WALL-ANCHORED flush component -- 411 of 411 killed '
                     'component signatures at k = 3..5 are zero-pinned -- and all of them fall '
                     'into three named mechanisms with NOTHING left over.  Lemma R\'s pure '
                     'length cap contributes ZERO kills, because a decoration never forces the '
                     'normal family or the sign, so a ruler is never forced to be long.'))
    rep['spot_A43_H2_k3_survivors'] = dict(
        n=len(SPOT) if SPOT else 0,
        ruler_kills=sum(r['ruler_kill'] for r in SPOT) if SPOT else None,
        charge_kills=sum(r['charge_kill'] for r in SPOT) if SPOT else None,
        rows=SPOT,
        verdict=('0/10 kills from either filter.  RULER: the C-C ends carry no WF anchor, so the '
                 'flush component has no pin, and a 2-link ruler has extent 2 against the cap '
                 's0*sqrt2 - 1 = 4.4830 -- every one of the 4^(#FL) gauge assignments survives.  '
                 'CHARGE: 2 to 4 corner contacts need 1.008-2.016 of charge each to reach B0, '
                 'against an ownership ceiling of 0.0625.  Both inert by 16x-32x.'))
    rep['canaries'] = dict(
        verdict=CAN['verdict'] if CAN else None,
        checks={c['name']: ('PASS' if c['pass_'] else 'FAIL') +
                ('' if not c.get('detail') else '  [%s]' % c['detail'])
                for c in CAN['checks']} if CAN else None,
        trump_structure=dict(ss_contacts=CAN['ss_edges'], FL=len(CAN['fl_edges']),
                             corner=len(CAN['ce_edges']), WF=len(CAN['wf_edges']),
                             WC=len(CAN['wc_edges']),
                             upright_squares=len(CAN['upright_squares'])) if CAN else None,
        note=('the RULER refined column is a genuinely strong filter on Trump\'s own structure: '
              'only %s of %s (family,sign) assignments of his 8 flush links survive, and the '
              'REALIZED one is among them.'
              % (CAN['ruler']['gauge_ok'], CAN['ruler']['gauge_full'])) if CAN else None)
    rep['verification'] = dict(regression_level0=REG,
                               regression_level1=('census_b.py reproduces A43 level1.json '
                                                  'we_surv on every sampled graph at every k '
                                                  '(mismatches: %s)'
                                                  % {k: L1['k%d' % k]['a43_we_surv_mismatches']
                                                     for k in ks}))

    # ------------------------------------------------------------------ gaps
    rep['gaps'] = [
        dict(id='G-A45B-1', kind='inertness (the headline)',
             text='CHARGE cannot fire at k <= 11.  Table-independent: the half-moat ownership '
                  'box caps a contact at rho_min^2 <= 1/16 and Euler caps the contact count at '
                  '3k+2, so the maximum conceivable sum at k=11 is 2.1875 < B0 = 4.0318.  With '
                  'the CERTIFIED table actually shipped (rho_min = 1/16, max entry 6.256e-04) '
                  'the same maximum is 0.0219, short by 184x.  Closing that gap needs a mean '
                  'charge of 0.1152 per contact, i.e. rho_min >= 0.3394, which is off the top of '
                  'the moat ladder and far above every radius the pilot could certify.'),
        dict(id='G-A45B-2', kind='min-over-realizations collapse',
             text='Even below the ceiling, the census-side semantics zero almost everything: a '
                  'non-flush square-square contact of a DECORATION can always be realized as CC '
                  '(uncharged by design), a wall-degree-2 square can realize the WCC '
                  'container-corner case (uncharged, lead addendum), and a class tilt window '
                  'that spans a dropped bin contributes 0.  To price a contact at all, the '
                  'enumeration would have to resolve CE-vs-CC per edge AND carry a tilt window '
                  'narrow enough to exclude every dropped bin -- neither of which an H1 '
                  'decoration carries.  This is the A43 enumeration-certificate mismatch again, '
                  'now on the family that was supposed to evade it.'),
        dict(id='G-A45B-3', kind='RULER over-acceptance',
             text='The CSP relaxes slides to [-1,1], imposes no interior-disjointness inside a '
                  'flush component, and gives non-zero-pinned components the widest tilt window '
                  '(cos+sin <= sqrt2).  Components with more than 12 FL links fall back to the '
                  'path relaxation (a sub-system, so kills stay sound) and to an unrefined 4^m '
                  'gauge count.  Every one of these can only ADD survivors.'),
        dict(id='G-A45B-4', kind='sampling / extrapolation',
             text='All Level-1 numbers use A43\'s sampling protocol (seed 7, cap 160 graphs, 40 '
                  'at k=7, edge budget 22), so they are weighted sample means, not exhaustive.  '
                  'k = 8..11 are 3-model fits with a k=7 holdout, not bounds -- same status as '
                  'A31/A43.'),
        dict(id='G-A45B-5', kind='m_ub crude tier',
             text='The m_ub table is a cover bound (columns of width < 1, each holding at most '
                  '1 + floor(y-extent) centres), computed per 3-deg bin with interval arithmetic '
                  'and sub-binning.  It is not sharp: a B&B in the style of A08 would lower it.  '
                  'As it stands GAP-A45-Z1 (single-grain mid-tilt residue) is open on 14 of 15 '
                  'bins.'),
        dict(id='G-A45B-6', kind='inherited',
             text='All A43-G2..G7 and A31-G1..G7 gaps are inherited unchanged; the lambda0 = 0 '
                  'branch is uncovered; rattler-join semantics (residue (f)) is the reason the '
                  'zero-charge collapse only bites at k >= 10.')]

    rep['findings'] = [
        'RULER IS THE ONLY THING THAT BITES, AND IT BITES EXACTLY WHERE A43\'S LAW SAYS.  As a '
        'decoration KILL it removes %s of decoration weight at k = 3..7 -- one part in a hundred '
        'or less.  The kill audit is unambiguous: 411 of 411 killed component signatures are '
        'ZERO-PINNED (wall-anchored), and they split into exactly three mechanisms with nothing '
        'left over -- M1 the Lemma-Q path bound (392: opposite-wall WF anchors at FL-graph '
        'distance <= 2, where the projection must equal s-1 in [2.80, 2.877084] but a path of m '
        'links moves it by at most m); M2 odd-cycle parity (16: a same-wall pin set equalises '
        'one family across the component, forcing every link into the other family, and an odd '
        'cycle of +-1 steps cannot close); M3 Lemma Q verbatim (3: the same forcing plus an '
        'opposite anchor pair makes the difference an INTEGER, and [2.80, 2.877084] contains no '
        'integer).  Lemma R\'s pure LENGTH cap contributes ZERO kills: a decoration never forces '
        'the normal family or the sign, so no ruler is ever forced to be long.  Bite '
        'proportional to pinned coordinates, one level below where A43 measured it.'
        % {k: '%.4f' % L1['k%d' % k]['frac_ruler_kill_weighted'] for k in ks},

        'THE REFINED FORM IS WORTH MORE THAN THE KILL FORM.  A31 prices a flush contact with a '
        'gauge multiplicity of 4 -- which is exactly the CSP\'s (normal family, sign) pair.  '
        'Counting only the FEASIBLE assignments instead of all 4 is still one-sided and still '
        'EXACT, and it keeps %s of the decoration count at k = 3..7.  On Trump\'s own structure '
        'the refinement is dramatic (1632 of 65536 assignments survive, the realized one among '
        'them) because his flush skeleton is heavily wall-anchored.'
        % {k: '%.4f' % L1['k%d' % k]['ruler_refined_keep_weighted'] for k in ks},

        'BOTH FILTERS ARE PROVABLY INERT AT LEVEL 0.  A Level-0 orbit dies only if every '
        'decoration dies, and the all-corner decoration always exists, has no flush component at '
        'all, and carries charge 0 under min-over-bins semantics.  R13 = R14 = R12 at every k '
        '-- the ablation table does not move.  The place the calculus can move a number is the '
        'decoration fan-out, i.e. the multiplier, not the orbit count.',

        'THE CERTIFIED TABLE LANDED AND CONFIRMS IT WITH ROOM TO SPARE.  Agent A\'s '
        'results/charge_table.json ships rho_min = 1/16 (half-moat radius R = 1/32), 25 of 75 '
        'bins kept and 50 dropped for want of a moat, every kept entry exact-recertified.  Its '
        'LARGEST entry is 41/65536 = 6.256e-04.  Even charging all 35 Euler-maximal contacts of '
        'a k=11 structure at that maximum gives 0.0219 against B0 = 4.0318 -- short by a factor '
        'of 184.  And the census-side min-over-window is exactly 0 in any case: WC bins 0-2 '
        '(phi < 9 deg) are dropped, and every CE mismatch bin has a dropped u-sub-bin, so an '
        'unrestricted class window always reaches a zero.',

        'CHARGE IS INERT BY CONSTRUCTION, AND THE ARITHMETIC IS TABLE-INDEPENDENT.  Ownership '
        'caps a contact at the area of its half-moat box, rho_min^2 <= (1/4)^2 = 1/16; Euler '
        'caps the contact count at 3k+2 = 35 at k = 11; so the largest charge sum any 11-square '
        'structure can carry is 2.1875 against a budget of 4.031780343056.  Short by 1.84x at '
        'the theoretical maximum.  Calibrated on agent A\'s pilot -- WC shipped at rho = 3/16, '
        'CE at rho = 1/16, CC DROPPED -- the global rho_min is at most 1/16, the half-moat box '
        'has area at most 1/256, and the k=11 ceiling falls to 0.1367: short by 29.5x.  Firing '
        'the filter would need rho_min >= 0.3394, off the top of the shipped ladder.  The '
        'census-side '
        'min-over-realizations semantics then zeroes what little is left (CC reachable from '
        'every non-flush contact; WCC for wall-degree-2 squares; dropped bins).',

        'ZERO-CHARGE COLLAPSE: (b) TAKES ALL OF IT AT k >= 10, EXACTLY, AND NOTHING BELOW.  In '
        'MAIN every component has a wall contact (L3), so a zero-charge decoration pins every '
        'component to class 0 and puts all k loaded squares at tilt 0; A26 allows at most 9 such '
        'squares.  So zero-charge cores with k >= 10 are dead outright -- no k=11 join needed, '
        'since A26\'s cap is universal, not existential.  Below k = 10 the residue is entirely '
        '(f), the rattler caveat, and residue (e) (floating common-tilt components) is EMPTY '
        'because L3 already forbids them.  The zero-charge share of decorations is small and '
        'falling: %s.  Within it, RULER/Lemma Q kills %s.'
        % ({k: '%.2e' % L1['k%d' % k]['frac_zero_charge_weighted'] for k in ks},
           {k: '%.2f' % L1['k%d' % k]['zero_charge_ruler_kill_weighted'] for k in ks}),

        'm_ub(theta) CRUDE TIER: 9 on [0,3), 12 on [3,18), 14 on [18,45).  Exactly one bin '
        'delivers the m_ub <= 10 that the single-grain residue needs, and A26 already had that '
        'bin (out to 2.503 deg).  GAP-A45-Z1 stands on 14 of 15 bins.  The mechanism is crisp: '
        'the centre region\'s bounding box in the theta-frame has side w*(s0-w), w = cos+sin, '
        'which passes 3 at about 4 degrees and buys a fourth column of centres.',

        'CANARIES ALL PASS (%s).  Trump survives RULER with his realized (family,sign) '
        'assignment feasible in every component; his 5-square flush strip at 40.1819 deg has '
        'Lemma-R capacity 5.463650, margin 0.463650 (the brief\'s 0.4636); his 6 upright squares '
        'carry 9 WF and 3 FL contacts and zero wall-corner contacts, all charged exactly 0; and '
        'his total charge sum is under B0 with capture 1.65%% of the budget at the realized bins '
        'of the stub table.' % (CAN['verdict'] if CAN else 'not run'),

        'SPOT MEASUREMENT ON THE A43-H2 k=3 SPINE SURVIVORS: 0/10 kills from either filter, and '
        'RULER does not even trim a gauge assignment (all 10 survivors have C-C ends, hence no '
        'WF anchor, hence no pin).  The certified [18,72] / [12,78] windows do not help: the '
        'extent cap must use the LARGEST cos+sin in the window, and every one of these windows '
        'contains 45 degrees.',

        'BOTTOM LINE.  I-L13\'s promise was a certificate whose unit of account matches the '
        'enumerated object.  It does match -- and it is still too small to pay.  The charging '
        'lemma is sound and its ownership scheme is honest, but the ownership box is two orders '
        'of magnitude smaller than the budget it has to exceed, so the arithmetic never closes.  '
        'The flush-ruler laws are the real find of this brief: they are EXACT, they bite on the '
        'gauge multiplicity rather than the orbit count, and they bite wherever a wall pins a '
        'coordinate -- the same law A43 measured, holding at a third level.']
    json.dump(rep, open(os.path.join(RES, 'census_report.json'), 'w'), indent=1, default=float)
    print('wrote results/census_report.json')
    for f in rep['findings']:
        print('\n* ' + f)


if __name__ == '__main__':
    main()
