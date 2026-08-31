#!/usr/bin/env python
"""summary_a51.py -- roll the A51 result files up into results/a51_summary.json.

Adds, on top of A49's rollup, the MID-TILT FLUSH-ACQUISITION MAP and its
head-to-head against A49's wall-termination law.

A51 role letters are TILT REGIMES, not A49 decks (see seeds.json/role_legend):
    B -> UPRIGHT (<12 deg),  M -> MID (12-30),  T -> HIGH (>=30).
CATMAP translates a49_common.role_pair_category's labels accordingly, so the
numbers are never printed under A49's deck names.

Reads only; writes one summary file.  [NUM] float64.
"""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A51 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A51, '..'))
for p in (os.path.join(ATT, 'A49-flushfree-hunt', 'code'), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

R = os.path.join(A51, 'results')

CATMAP = {'chain B-B': 'pair UPRIGHT-UPRIGHT', 'press M-B': 'pair MID-UPRIGHT',
          'top T-T': 'pair HIGH-HIGH', 'M-M': 'pair MID-MID',
          'B-T': 'pair UPRIGHT-HIGH', 'M-T': 'pair MID-HIGH',
          'B-wall': 'WALL UPRIGHT', 'M-wall': 'WALL MID',
          'T-wall': 'WALL HIGH', 'other': 'other'}

# A49's published map (results/a49_report.md sect. 4), for the head-to-head.
A49_MAP = {'n_events': 97,
           'by_category': {'B-wall': 33, 'top T-T': 31, 'chain B-B': 18,
                           'T-wall': 15, 'press M-B': 0},
           'wall_share': (33 + 15) / 97.0,
           'solo_events': 20, 'solo_wall_events': 19,
           'median_s_at_acquisition': 4.0000000000375,
           'simultaneity': {'1': 20, '10': 67, '13': 10},
           's_final_min': 4.000000000000012}


def load(name):
    p = os.path.join(R, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def cat_of(e):
    return CATMAP.get(e.get('category'), e.get('category'))


def is_wall(e):
    return e.get('type') == 'wall'


def acquisition_map(recs):
    ev = [dict(r['acquisition'], _seed=r['seed'], _fam=r.get('profile'))
          for r in recs if r.get('acquisition')]
    if not ev:
        return {'n_events': 0}
    solo = [e for e in ev if e.get('n_simultaneous', 0) == 1]
    s_ev = sorted(e['s_at_event'] for e in ev)
    byfam = {}
    for e in ev:
        byfam.setdefault(e['_fam'], collections.Counter())[cat_of(e)] += 1
    m = {'n_events': len(ev),
         'by_category': dict(collections.Counter(cat_of(e) for e in ev)),
         'modal_category': collections.Counter(
             cat_of(e) for e in ev).most_common(1)[0][0],
         'n_wall_events': sum(1 for e in ev if is_wall(e)),
         'n_pair_events': sum(1 for e in ev if not is_wall(e)),
         'wall_share': sum(1 for e in ev if is_wall(e)) / float(len(ev)),
         'by_wall': dict(collections.Counter(
             '|'.join(e['key'].split(':')[2:]) for e in ev if is_wall(e))),
         'n_solo_events': len(solo),
         'solo_by_category': dict(collections.Counter(cat_of(e)
                                                      for e in solo)),
         'solo_wall_share': (sum(1 for e in solo if is_wall(e)) / float(
             len(solo)) if solo else None),
         'simultaneity_hist': dict(sorted(collections.Counter(
             e.get('n_simultaneous') for e in ev).items())),
         'median_n_simultaneous': sorted(
             e.get('n_simultaneous', 0) for e in ev)[len(ev) // 2],
         'median_s_at_acquisition': s_ev[len(s_ev) // 2],
         'min_s_at_acquisition': s_ev[0], 'max_s_at_acquisition': s_ev[-1],
         'continued_down_after_event': sum(1 for e in ev
                                           if e.get('continued_down')),
         'by_seed_family': {k: dict(v) for k, v in byfam.items()},
         'n_categories_at_event_hist': dict(sorted(collections.Counter(
             len(e.get('all_categories') or []) for e in ev).items()))}
    return m


def main():
    out = {'incumbent_s0': 3.877084}
    sd = load('seeds.json')
    if sd:
        out['seeds'] = {'n': sd['n_seeds'], 'n_accepted': sd['n_accepted'],
                        'role_legend': sd.get('role_legend'),
                        'families': dict(collections.Counter(
                            s['family'] for s in sd['seeds'])),
                        'table': [{k: s[k] for k in
                                   ('id', 'family', 'mode', 'lam_minus_1',
                                    's_repaired', 'min_class_gap_deg',
                                    'n_mid_tilt_ge12deg',
                                    'mean_tilt_class_deg', 'accepted')}
                                  for s in sd['seeds']]}
    h = load('hunt.json')
    if h:
        recs, a = h['records'], h['aggregate']
        byfam = {}
        for r in recs:
            d = byfam.setdefault(r['profile'],
                                 {'n': 0, 'a': 0, 'b': 0, 'c': 0,
                                  's_min': float('inf'),
                                  'families': collections.Counter()})
            d['n'] += 1
            d['a'] += bool(r.get('outcome_a'))
            d['b'] += bool(r['outcome_b'])
            d['c'] += bool(r['outcome_c'])
            d['s_min'] = min(d['s_min'], r['s_final'])
            d['families'][r['family']] += 1
        for d in byfam.values():
            d['families'] = dict(d['families'])
        amap = acquisition_map(recs)
        out['census'] = {
            'n_runs': a['n_runs'],
            'n_a_candidate': a['n_a_flushfree_candidate'],
            'n_a_flushfree_landings': a['n_a_flushfree_landing'],
            'n_b_flush_acquired': a['n_b_flush_acquired'],
            'n_c_drain_to_known': a['n_c_drain_to_known'],
            's_final_min': a['s_final_min'],
            'n_landing_below_4': sum(1 for r in recs
                                     if r['s_final'] < 4.0 - 1e-9),
            'n_landing_at_s0': sum(1 for r in recs
                                   if r['s_final'] < 3.8771),
            's_final_hist': dict(sorted(collections.Counter(
                round(r['s_final'], 4) for r in recs).items(),
                key=lambda kv: kv[0])[:25]),
            'families': a['family_census'],
            'by_seed_family': byfam,
            'acquisition_map': amap,
            'flushfree_landing_classes': dict(collections.Counter(
                r.get('landing_class', '-') for r in recs
                if r['landing_flush_free'])),
            'flushfree_landing_s_range': [
                min((r['s_final'] for r in recs if r['landing_flush_free']),
                    default=None),
                max((r['s_final'] for r in recs if r['landing_flush_free']),
                    default=None)],
            'seed_flush_free': sum(1 for r in recs if r.get('seed_flush_free')),
            'micro_events': sum(1 for r in recs if r.get('acquisition')),
            'fd_events': sum(1 for r in recs if r.get('acquisition_fd'))}
        out['A49_vs_A51'] = {
            'a49': A49_MAP,
            'a51': {'n_events': amap.get('n_events'),
                    'by_category': amap.get('by_category'),
                    'wall_share': amap.get('wall_share'),
                    'solo_events': amap.get('n_solo_events'),
                    'solo_wall_share': amap.get('solo_wall_share'),
                    'median_s_at_acquisition':
                        amap.get('median_s_at_acquisition'),
                    'simultaneity': amap.get('simultaneity_hist'),
                    's_final_min': a['s_final_min']}}
    for fn, key in (('stratum.json', 'stratum_global'),
                    ('stratum_local.json', 'stratum_local')):
        d = load(fn)
        if not d:
            continue
        a, recs = d['aggregate'], d['records']
        out[key] = {k: a.get(k) for k in
                    ('n_runs', 'n_pressed_on_flush_boundary',
                     'n_blocked_by_flush_boundary', 'n_no_progress',
                     'n_interior', 'n_interior_candidate',
                     'n_interior_not_cp', 's_final_min', 's_final_median',
                     'verdicts', 'active_row_types')}
        out[key]['n_active_hist'] = dict(sorted(collections.Counter(
            r['n_active_stratum'] for r in recs).items()))
        out[key]['s_final_range'] = [min(r['s_final'] for r in recs),
                                     max(r['s_final'] for r in recs)]
        out[key]['by_seed_family'] = {
            f: {'n': sum(1 for r in recs if r['profile'] == f),
                's_min': min(r['s_final'] for r in recs if r['profile'] == f),
                'verdicts': dict(collections.Counter(
                    r['verdict'] for r in recs if r['profile'] == f))}
            for f in sorted({r['profile'] for r in recs})}
        esc = [r['escaped'] for r in recs if r.get('escaped')]
        if esc:
            keys = collections.Counter(k.split(':')[0] for e in esc
                                       for k in e['keys'])
            out[key]['escape_row_types'] = dict(keys)
            out[key]['escape_n_keys_hist'] = dict(sorted(
                collections.Counter(len(e['keys']) for e in esc).items()))
    c = load('control.json')
    if c:
        recs = c['records']
        byfam = {}
        for r in recs:
            d = byfam.setdefault(r['seed'], {'n': 0, 'rematched_own': 0,
                                             'flush_present': 0,
                                             'true': r.get('true_family'),
                                             's_ref': r.get('s_ref'),
                                             'matched': collections.Counter(),
                                             's_min': float('inf'),
                                             'n_viol_total': 0})
            d['n'] += 1
            d['matched'][r['family']] += 1
            d['s_min'] = min(d['s_min'], r['s_final'])
            d['n_viol_total'] += len(r['landing_violations'])
            if not r['landing_flush_free']:
                d['flush_present'] += 1
            if str(r['family']).split(':')[-1] == str(r.get('true_family')):
                d['rematched_own'] += 1
        for d in byfam.values():
            d['matched'] = dict(d['matched'])
        out['control'] = {
            'n_runs': len(recs), 'per_seed': byfam,
            'n_flush_present': sum(1 for r in recs
                                   if not r['landing_flush_free']),
            'median_violations_per_landing': sorted(
                len(r['landing_violations']) for r in recs)[len(recs) // 2],
            'n_wall_violations': sum(1 for r in recs
                                     for v in r['landing_violations']
                                     if v['type'] == 'wall'),
            'n_pair_violations': sum(1 for r in recs
                                     for v in r['landing_violations']
                                     if v['type'] == 'pair'),
            'n_rematched_own': sum(
                1 for r in recs
                if str(r['family']).split(':')[-1] == str(r.get('true_family')))}
    s = load(os.path.join('candidates', 'summary.json'))
    if s:
        out['audits'] = {'n_candidates': s['n_candidates'],
                         'n_survivors': s['n_survivors'],
                         'survivors': s['survivors'],
                         'by_verdict': s['by_verdict'],
                         'by_class': s.get('by_class'), 's_min': s.get('s_min')}
    mins = [v for v in (out.get('census', {}).get('s_final_min'),
                        out.get('stratum_global', {}).get('s_final_min'),
                        out.get('stratum_local', {}).get('s_final_min'))
            if v is not None]
    out['min_s_seen_anywhere'] = min(mins) if mins else None
    with open(os.path.join(R, 'a51_summary.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'seeds'},
                     indent=1)[:14000])
    return 0


if __name__ == '__main__':
    sys.exit(main())
