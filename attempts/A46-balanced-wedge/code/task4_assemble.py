#!/usr/bin/env python3
"""Assemble results/w_ce_cc_pilot.json; optionally exact-recertify chosen bins.

  python task4_assemble.py                 # float only
  python task4_assemble.py --exact CE_39_42 CC_110_120
"""
from __future__ import annotations

import argparse
import json
import os
from fractions import Fraction as F

import a45_lib as L
import a46_lib as A

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
W = os.path.join(A46, 'work')
RES = os.path.join(A46, 'results')
RW = F(5, 4)


def rebuild_cfgs(e):
    if e['type'] == 'CE':
        b = dict(d=(F(e['bin']['d'][0]), F(e['bin']['d'][1])),
                 u=(F(e['bin']['u'][0]), F(e['bin']['u'][1])))
        return L.build_configs('CE', b, nsub=e['nsub'], nsub_u=e['nsub_u'])
    b = dict(delta=(F(e['bin']['delta'][0]), F(e['bin']['delta'][1])))
    return L.build_configs('CC', b, nsub=e['nsub'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exact', nargs='*', default=[])
    a = ap.parse_args()
    ents = []
    for f in ('ce_pilot.json', 'cc_pilot.json', 'cc_pilot2.json'):
        p = os.path.join(W, f)
        if os.path.exists(p):
            ents += json.load(open(p))['entries']
    for e in ents:
        if e['type'] == 'CC':
            d0, d1 = F(e['bin']['delta'][0]), F(e['bin']['delta'][1])
            # free wedges at the shared corner: (delta - 90) and (270 - delta)
            e['free_wedge_min_deg'] = [float(min(x - 90, 270 - x))
                                       for x in (d0, d1)]
            e['free_wedge_max_deg'] = [float(max(x - 90, 270 - x))
                                       for x in (d0, d1)]
            e['note_param'] = ('the dead area is governed by the SHARP free '
                               'wedge min(delta-90, 270-delta), not by the '
                               'relative angle mod 90')
        if e['id'] in a.exact:
            cfgs = rebuild_cfgs(e)
            cells = [tuple(F(v) for v in c) for c in e['cells']]
            r = L.recert_exact(e['type'], cfgs, cells, depth_max=34,
                               max_boxes=200000)
            kept = [c for c in cells if [str(v) for v in c] not in r['failed']]
            p = (L.PX, F(0)) if e['type'] == 'WC' else (L.PX, L.PY)
            prof = A.radial_profile(kept, p, [F(1, 8), F(1, 4), F(1, 2),
                                              F(3, 4), F(1), RW])
            e.update(exact=True, area_exact=str(r['area']),
                     area_exact_f=float(r['area']),
                     n_tiles=len(cells), n_failed_exact=len(r['failed']),
                     exact_seconds=r['seconds'],
                     radial_exact={k: str(v) for k, v in prof.items()},
                     radial_exact_f={k: float(v) for k, v in prof.items()})
            print('%s EXACT %.6f (float %.6f) failed=%d/%d %ss'
                  % (e['id'], float(r['area']), e['area_float_f'],
                     len(r['failed']), len(cells), r['seconds']))
    ents.sort(key=lambda e: (e['type'], e['id']))
    out = dict(
        what='A46 task 4: CE + CC dead-region pilot (magnitude)',
        status='FLOAT unless an entry carries exact:true',
        frames=('A45 CE frame (a corner at p=(10,10), b upright with top edge '
                'on y=10, slide u); A45 CC frame (a = [10,11]^2, b cone '
                '[delta, delta+90]).  Window = B_inf(p, 5/4), i.e. the FULL '
                'window of the brief (1.2), not A45\'s 1/2; Lemma-K keeper '
                '= conv(guaranteed subset of a cup b), a45_lib.keeper_hull '
                'VERBATIM.'),
        max_CE=max((e['area_float_f'] for e in ents if e['type'] == 'CE'),
                   default=0.0),
        max_CC=max((e['area_float_f'] for e in ents if e['type'] == 'CC'),
                   default=0.0),
        entries=ents)
    json.dump(out, open(os.path.join(RES, 'w_ce_cc_pilot.json'), 'w'), indent=1)
    for e in ents:
        extra = ('wedge %s' % e.get('free_wedge_min_deg', '')
                 if e['type'] == 'CC' else '')
        print('%-14s %-3s area=%.6f %-8s %s'
              % (e['id'], e['type'],
                 e.get('area_exact_f', e['area_float_f']),
                 'EXACT' if e.get('exact') else 'float', extra))
    print('-> results/w_ce_cc_pilot.json')


if __name__ == '__main__':
    main()
