"""A89 / T2: merge the four task summaries into results/t2_summary.json."""
from __future__ import annotations

import json
import os

import a89lib as L

R = L.RESULTS


def jl(p):
    return [json.loads(x) for x in open(os.path.join(R, p)) if x.strip()]


def js(p):
    return json.load(open(os.path.join(R, p)))


def minpos(rows, thr):
    c = [r for r in rows if r['tilt_deg'] > thr]
    if not c:
        return None
    m = min(c, key=lambda x: x['tilt_deg'])
    return {'tilt_deg': m['tilt_deg'], 'tag': m['tag'], 'square': m['square'],
            'corner': m['corner']}


def main():
    a = js('t2_summary_a87.json')
    b = js('t2_summary_atlas.json')
    c = js('t2_summary_trump.json')
    d = js('t2_a85_zone.json')
    ra, rb = jl('t2_blockers_a87.jsonl'), jl('t2_blockers_atlas.jsonl')

    out = {
        'attempt': 'A89-tilt-floor / T2 empirical check (Opus compute chore)',
        'definitions': {
            'meets_corner_box': 'int(Q) cap int(B_c) != empty by SAT on 4 axes, '
                                'penetration depth > 1e-9',
            'tilt': 'dist(theta_deg, 90 Z) in [0,45]',
            'positive_tilt_threshold': L.TILT_POS,
            'contact_tol': L.CONTACT_TOL,
            'LP_TOL_forced_loadable': L.LP_TOL,
            'FJ_polytope': 'lam >= 0, lam_0 + sum lam = 1, lam_0 grad s = sum lam_k grad g_k',
            'theta0_candidates': list(L.THETA0_CANDIDATES)},
        'headline': {
            'A87_167_points': {
                'n_blockers': a['n_blockers'],
                'min_positive_tilt_loaded_forced_deg':
                    a['min_positive_tilt']['loaded_forced']['tilt_deg'],
                'min_positive_tilt_loaded_forced_at':
                    '%s sq%d %s' % (a['min_positive_tilt']['loaded_forced']['tag'],
                                    a['min_positive_tilt']['loaded_forced']['square'],
                                    a['min_positive_tilt']['loaded_forced']['corner']),
                'min_positive_tilt_loaded_loadable_deg':
                    a['min_positive_tilt']['loaded_loadable']['tilt_deg'],
                'min_positive_tilt_loaded_loadable_at':
                    '%s sq%d %s' % (a['min_positive_tilt']['loaded_loadable']['tag'],
                                    a['min_positive_tilt']['loaded_loadable']['square'],
                                    a['min_positive_tilt']['loaded_loadable']['corner']),
                'min_positive_tilt_loadable_above_1e-6_deg':
                    minpos([r for r in ra if r['loaded_loadable']], 1e-6),
                'min_positive_tilt_all_blockers_deg':
                    a['min_positive_tilt']['all_blockers']['tilt_deg'],
                'n_loaded_loadable_in_zone_by_theta0':
                    {k: v['loaded_loadable_in_zone']
                     for k, v in a['theta0_table'].items()},
                'n_loaded_forced_in_zone_by_theta0':
                    {k: v['loaded_forced_in_zone']
                     for k, v in a['theta0_table'].items()},
                'n_unloaded_or_rattler_in_zone_by_theta0':
                    {k: v['unloaded_or_rattler_in_zone']
                     for k, v in a['theta0_table'].items()},
                'n_near_flush_ghosts': a['near_flush_ghosts']['n']},
            'atlas_12_families': {
                'n_blockers': b['n_blockers'],
                'min_positive_tilt_loaded_forced_deg':
                    b['min_positive_tilt']['loaded_forced']['tilt_deg'],
                'min_positive_tilt_loaded_loadable_deg':
                    b['min_positive_tilt']['loaded_loadable']['tilt_deg'],
                'min_positive_tilt_all_blockers_deg':
                    b['min_positive_tilt']['all_blockers']['tilt_deg'],
                'n_loaded_loadable_in_zone_by_theta0':
                    {k: v['loaded_loadable_in_zone']
                     for k, v in b['theta0_table'].items()},
                'n_slot_squares': b['n_slot_squares'],
                'n_near_flush_ghosts': b['near_flush_ghosts']['n']},
            'trump_canary': {
                'verdict': c['canary_verdict_no_blocker_tilt_in_1e-7_to_theta0'],
                'n_blockers': c['n_blockers'],
                'n_slot_squares': c['n_slot_squares'],
                'slot_tilts_deg': [s['tilt_deg_300dps'][:12] for s in c['slot_squares']],
                'exact_zero_branch_contains_the_slots':
                    c['exact_zero_branch_contains_the_slots'],
                'TL_crowd_tilts_deg': [t['tilt_deg'] for t in c['TL_crowd']]},
            'a85': {
                'D1_frac_failed_blocker_nodes_touched':
                    {k: v['frac_failed_blocker_nodes_touched']
                     for k, v in d['D1_lp_rows']['theta0_table'].items()},
                'D2_frac_sound_boxes_zone_intersecting':
                    {k: v['a_boxes']['frac_zone_intersecting']
                     for k, v in d['D2_BL_census']['per_theta0'].items()},
                'D2_tilt_volume_frac_deleted_deg':
                    {k: v['b_tilt_volume_deleted']['xytheta_volume_frac_deg']
                     for k, v in d['D2_BL_census']['per_theta0'].items()},
                'D2_tilt_volume_frac_deleted_t':
                    {k: v['b_tilt_volume_deleted']['xytheta_volume_frac_t']
                     for k, v in d['D2_BL_census']['per_theta0'].items()},
                'D2_frac_pairs_one_member':
                    {k: v['c_pairs']['frac_at_least_one']
                     for k, v in d['D2_BL_census']['per_theta0'].items()},
                'D2_frac_pairs_both_members':
                    {k: v['c_pairs']['frac_both']
                     for k, v in d['D2_BL_census']['per_theta0'].items()},
                'D2_e_pairs_killed_after_refine_level0':
                    {k: v['n_pairs_core_contradictory_after_refine_level0']
                     for k, v in d['D2_BL_census']['e_refined_level0_prune'].items()}}},
        'files': {
            'A': ['results/t2_blockers_a87.jsonl', 'results/t2_summary_a87.json'],
            'B': ['results/t2_blockers_atlas.jsonl', 'results/t2_summary_atlas.json'],
            'C': ['results/t2_blockers_trump.jsonl', 'results/t2_summary_trump.json'],
            'D': ['results/t2_a85_zone.json'],
            'code': ['code/a89lib.py', 'code/t2_a87.py', 'code/t2_atlas.py',
                     'code/t2_trump.py', 'code/t2_a85.py', 'code/t2_combine.py'],
            'log': ['logs/t2.log'], 'notes': ['notes/t2_report.md']},
        'task_A': a, 'task_B': b, 'task_C': {k: v for k, v in c.items()
                                             if k != 'point_record'},
        'task_D': d,
    }
    json.dump(out, open(os.path.join(R, 't2_summary.json'), 'w'), indent=1,
              default=str)
    print(json.dumps(out['headline'], indent=1, default=str))


if __name__ == '__main__':
    main()
