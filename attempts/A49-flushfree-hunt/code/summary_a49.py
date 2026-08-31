#!/usr/bin/env python
"""summary_a49.py -- roll the A49 result files up into results/a49_summary.json
and print the report numbers.  Reads only; writes one summary file."""
from __future__ import annotations

import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a49_common as C              # noqa: E402

R = C.RESULTS


def load(name):
    p = os.path.join(R, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def main():
    out = {}
    h = load('hunt.json')
    if h:
        recs = h['records']
        a = h['aggregate']
        amap = a['flush_acquisition_map']
        bymode = {}
        for md in sorted({r['mode'] for r in recs}):
            sub = [r for r in recs if r['mode'] == md]
            ev = [r['acquisition'] for r in sub if r['acquisition']]
            cat = collections.Counter(e['category'] for e in ev)
            bymode[md] = {
                'n': len(sub),
                'a': sum(1 for r in sub if r.get('outcome_a')),
                'a_flushfree_landings': sum(1 for r in sub
                                            if r['landing_flush_free']),
                'b': sum(1 for r in sub if r['outcome_b']),
                'c': sum(1 for r in sub if r['outcome_c']),
                's_min': min(r['s_final'] for r in sub),
                'modal_category': cat.most_common(1)[0] if cat else None,
                'median_s_at_acq': (sorted(e['s_at_event'] for e in ev)
                                    [len(ev) // 2] if ev else None),
                'n_simultaneous_median': (
                    sorted(e['n_simultaneous'] for e in ev)[len(ev) // 2]
                    if ev else None)}
        out['census'] = {
            'n_runs': a['n_runs'], 'n_a': a['n_a_flushfree_candidate'],
            'n_a_flushfree_landings': a['n_a_flushfree_landing'],
            'n_b': a['n_b_flush_acquired'], 'n_c': a['n_c_drain_to_known'],
            's_final_min': a['s_final_min'],
            'families': a['family_census'],
            'by_mode': bymode,
            'acquisition_map': amap,
            'flushfree_landing_classes': dict(collections.Counter(
                r.get('landing_class', '-') for r in recs
                if r['landing_flush_free'])),
            'flushfree_landing_s_range': (
                [min((r['s_final'] for r in recs if r['landing_flush_free']),
                     default=None),
                 max((r['s_final'] for r in recs if r['landing_flush_free']),
                     default=None)])}
    for fn, key in (('stratum.json', 'stratum_global'),
                    ('stratum_local.json', 'stratum_local')):
        d = load(fn)
        if not d:
            continue
        a = d['aggregate']
        recs = d['records']
        out[key] = {k: a.get(k) for k in
                    ('n_runs', 'n_pressed_on_flush_boundary',
                     'n_blocked_by_flush_boundary', 'n_no_progress',
                     'n_interior', 'n_interior_candidate',
                     'n_interior_not_cp', 's_final_min', 's_final_median',
                     'verdicts', 'by_mode', 'active_row_types')}
        out[key]['n_active_hist'] = dict(sorted(collections.Counter(
            r['n_active_stratum'] for r in recs).items()))
        out[key]['s_final_range'] = [min(r['s_final'] for r in recs),
                                     max(r['s_final'] for r in recs)]
    c = load('control.json')
    if c:
        recs = c['records']
        rows = []
        for r in recs:
            rows.append({'seed': r['seed'], 'replica': r['replica'],
                         'true_family': r.get('true_family'),
                         's_ref': r.get('s_ref'), 's_final': r['s_final'],
                         'family_matched': r['family'],
                         'landing_flush_free': r['landing_flush_free'],
                         'n_landing_violations':
                             len(r['landing_violations'])})
        byfam = {}
        for r in recs:
            d = byfam.setdefault(r['seed'], {'n': 0, 'rematched_own': 0,
                                             'flush_present': 0,
                                             'true': r.get('true_family'),
                                             'matched': collections.Counter(),
                                             's_min': float('inf')})
            d['n'] += 1
            d['matched'][r['family']] += 1
            d['s_min'] = min(d['s_min'], r['s_final'])
            if not r['landing_flush_free']:
                d['flush_present'] += 1
            fam = str(r['family']).split(':')[-1]
            if fam == str(r.get('true_family')):
                d['rematched_own'] += 1
        for d in byfam.values():
            d['matched'] = dict(d['matched'])
        out['control'] = {'n_runs': len(recs), 'per_seed': byfam,
                          'n_flush_present': sum(1 for r in recs
                                                 if not r['landing_flush_free']),
                          'n_rematched_own': sum(
                              1 for r in recs
                              if str(r['family']).split(':')[-1]
                              == str(r.get('true_family')))}
    s = load(os.path.join('candidates', 'summary.json'))
    if s:
        out['audits'] = {'n_candidates': s['n_candidates'],
                         'n_survivors': s['n_survivors'],
                         'survivors': s['survivors'],
                         'by_verdict': s['by_verdict'],
                         'by_class': s.get('by_class'),
                         's_min': s.get('s_min')}
    mins = [v for v in (out.get('census', {}).get('s_final_min'),
                        out.get('stratum_global', {}).get('s_final_min'),
                        out.get('stratum_local', {}).get('s_final_min'))
            if v is not None]
    out['min_s_seen_anywhere'] = min(mins) if mins else None
    out['incumbent_s0'] = 3.877084
    with open(os.path.join(R, 'a49_summary.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1)[:12000])
    return 0


if __name__ == '__main__':
    sys.exit(main())
