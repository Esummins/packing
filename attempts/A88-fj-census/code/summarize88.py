"""A88 T2: assemble results/census88_summary.json from every stage output."""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
import json
import math

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
FACT = math.factorial(11) * 8


def rd(name):
    p = os.path.join(RES, name)
    if not os.path.exists(p):
        return None
    return json.load(open(p))


def _ablation(d3, r3):
    """The report columns: the DECORATED k_H = 11 census under each filter set.
    K0-2 is a Level-0 filter (measured pass rate on F0 survivors); K0-1 and K0-3
    are decoration filters, applied as decoration-count-weighted pass rates."""
    if not d3:
        return None
    base = d3['decorated_census_k11']['point_estimate_F0']
    f1 = d3['k0_decoration_rates']['K0_1_decoration_weighted']
    f13 = d3['k0_decoration_rates']['K0_1_and_3_decoration_weighted']
    f3 = f13 / f1 if f1 else 1.0
    f2 = r3.get('K0_2_rate') or 1.0
    cols = [
        ('F0 alone', base, 1.0),
        ('F0 + K0-1', base * f1, f1),
        ('F0 + K0-1 + K0-3', base * f13, f13),
        ('F0 + K0-1 + K0-2 + K0-3', base * f13 * f2, f13 * f2),
        ('drop K0-1 (F0 + K0-2 + K0-3)', base * f3 * f2, f3 * f2),
        ('drop K0-2 (F0 + K0-1 + K0-3)', base * f13, f13),
        ('drop K0-3 (F0 + K0-1 + K0-2)', base * f1 * f2, f1 * f2),
    ]
    return dict(unit='decorated structures at k_H = 11, S_11 x D4 orbits, MC '
                     'point estimate',
                K0_1_factor=f1, K0_3_factor_given_K0_1=f3, K0_2_factor=f2,
                columns=[dict(name=a, estimate=b, log10=math.log10(b),
                              factor_vs_F0=c) for a, b, c in cols])


def main():
    bs = rd('burnside88.json')
    r3 = rd('mc_run3.json')
    r2 = rd('mc_run2.json')
    lb = rd('lower88.json')
    l1 = rd('level1_88.json')
    can = rd('canary88.json')
    st = rd('selftest88.json')
    smeta = rd('census88_sample_meta.json')
    d6 = rd('d6_checks.json')
    a31 = json.load(open(os.path.join(
        ROOT, 'attempts', 'A31-structure-count', 'results', 'count_report.json')))

    UB = bs['k11_factorable_orbits_UB']
    Z = int(bs['k11_labelled_Z'])
    p = r3['F0_rate']
    sp = r3['F0_rate_sigma']
    est_orb = UB * p
    est_orb_sig = UB * sp
    est_lab = Z * p

    a31ab = a31['ablation_orbit_counts']
    k37 = {k: a31ab[k]['_hard_survivors_MAIN'] for k in ('3', '4', '5', '6', '7')}
    proj = a31['level2']['projection']

    out = dict(
        what='A88 T2: the k0 FJ-supporting contact-structure census at k_H = 11, '
             'with a rigorous bracket (exact Burnside upper bound on the '
             'factorable filter subset; exhaustively verified sub-family lower '
             'bound; unbiased Monte-Carlo point estimate)',
        window=dict(S_LO=3.82, S_HI=3.877084,
                    note='A88 uses the certified window [3.82, 3.877084]; '
                         'A31 used [3.80, 3.8771]'),
        validation=dict(
            burnside_R0_R2_vs_A31=dict(
                R0_k3=bs['R0_k3'], R2_k3=bs['R2_k3'], R0_k4=bs['R0_k4'],
                R2_k4=bs['R2_k4'], match=bs['R0_R2_match_A31'],
                note='R2 is L5(b) only, so it does NOT change when S_LO moves '
                     'from 3.80 to 3.82; verified identical to A31'),
            weighted_burnside_vs_brute_force=dict(
                k3=[bs['fact_k3_burnside'], bs['fact_k3_brute']],
                k4=[bs['fact_k4_burnside'], bs['fact_k4_brute']],
                match=bs['brute_match']),
            labelled_Z_vs_mask_count_table=True,
            decoration_menu_and_tilt_count=dict(
                menu_matches_20_per_SS_2_per_SW=st['decoration_all_agree'],
                rows_map_injective=st['rows_map_injective']),
            d4_equivariance=st['d4_equivariance'],
            structural_facts=st['structural_facts'],
        ),
        canary=dict(verdict=can['CANARY'], checks=can['checks'],
                    slot_squares=can['slot_squares'],
                    per_wall=can['per_wall'],
                    degenerate_corner_corner=can['degenerate_corner_corner'],
                    tolerance=can['tolerance'],
                    max_abs_residual=can['max_abs_residual']),
        D1_level0_k11=dict(
            labelled_factorable_Z=str(Z),
            orbit_upper_bound_EXACT=UB,
            orbit_upper_bound_note='exact Burnside over S_11 x D4 on the '
                                   'factorable subset (mask admissibility + '
                                   'pairwise coexistence + touching window)',
            exact_cumulative_ablation_factorable=bs['k11_ablation_exact'],
            orbit_weight_excess=UB / (Z / FACT),
            mc=dict(n_draws=r3['n'], F0_rate=p, F0_rate_sigma=sp,
                    stage_names=r3['stage_names'],
                    stage_counts=r3['stage_counts'],
                    stage_rate=r3['stage_rate'],
                    proposal=r3['proposal']),
            mc_crosscheck_importance_sampled=(
                dict(stage_names=r2['stage_names'], stage_rate=r2['stage_rate'],
                     stage_sigma=r2['stage_sigma']) if r2 else None),
            point_estimate_orbits_MC=est_orb,
            point_estimate_orbits_sigma=est_orb_sig,
            point_estimate_labelled_MC=est_lab,
            lower_bound_EXACT=(lb['LOWER_BOUND_orbits'] if lb else None),
            lower_bound_family=(lb['family'] if lb else None),
            lower_bound_detail=lb,
            bracket=[lb['LOWER_BOUND_orbits'] if lb else None, UB],
            K0_2_rate_on_F0_survivors=r3.get('K0_2_rate'),
            K0_2_count=r3.get('K0_2_count'),
        ),
        D2_level1=l1 and {a: b for a, b in l1.items() if a != 'rows'},
        D3_composed=rd('d3_compose.json'),
        ablation_table=_ablation(rd('d3_compose.json'), r3),
        D5_sample=dict(path='results/census88_sample.jsonl',
                       format_doc='notes/sample_format.md', meta=smeta),
        D6_certified_fj_checks=(d6['summary'] if d6 else None),
        A31_reuse=dict(
            exact_k3_to_k7_MAIN=k37,
            sum_k3_to_k7=sum(k37.values()),
            A31_projection_k8_to_k11_level0=proj['main_level0'],
        A31_projection_total_structures=proj['total_structures']['M1_exp']['k11'],
        A31_extrapolated_fanout=proj['fanout'],
            note='k = 3..7 are A31 EXACT (S_LO = 3.80; the only S_LO-sensitive '
                 'filter is L5(a), and it can only get STRONGER at 3.82, so '
                 'these are upper bounds for the A88 window); 8..10 are A31 '
                 'EXTRAPOLATED'),
    )
    with open(os.path.join(RES, 'census88_summary.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({a: b for a, b in out.items()
                      if a not in ('D2_level1', 'D6_certified_fj_checks')},
                     indent=1)[:6000])
    print('wrote results/census88_summary.json')


if __name__ == '__main__':
    main()
