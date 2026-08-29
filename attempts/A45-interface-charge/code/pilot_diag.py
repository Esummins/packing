#!/usr/bin/env python3
"""A45 agent A -- re-run the pilot's DIAGNOSTIC (b) at full bin resolution.

The first pilot pass ran the unrestricted dead map with nsub = 1 (one PlacedBox
for the whole bin), which is a much weaker hypothesis than the nsub-refined bin
used for the moat and the charge map -- it therefore UNDERSTATES the dead area
(CE: 0.00366 at nsub=1 vs 0.00964 already inside B(p,1/8) at nsub=24).  This
re-runs (b) with the same sub-box family as (a)/(c) so that the
'full extent vs charged' comparison of remark (2) is apples-to-apples, and
patches results/pilot.json in place (field `full_map_refined`).
"""
import json
import os
from fractions import Fraction as F

import a45_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
P = os.path.join(RES, 'pilot.json')

BINS = {
    'WC': (dict(phi=(F(21), F(24))), dict(nsub=6)),
    'CE': (dict(d=(F(21), F(24)), u=(F(0), F(1, 4))), dict(nsub=6, nsub_u=4)),
    'CC': (dict(delta=(F(261, 2), F(279, 2))), dict(nsub=6)),
}

if __name__ == '__main__':
    doc = json.load(open(P))
    for rec in doc['results']:
        kind = rec['kind']
        bin_, kw = BINS[kind]
        cfg = L.build_configs(kind, bin_, **kw)
        fd = L.full_dead_map(kind, cfg, R=F(1, 2), cell0=F(1, 16), min_cell=F(1, 64),
                             mode='float', depth_max=24, max_boxes=3000,
                             work_budget=3000)
        rec['full_map_refined'] = dict(
            R='1/2', n_configs=len(cfg), area=str(fd['area']),
            area_float=float(fd['area']), extent=fd['extent'],
            extent_rel=fd.get('extent_rel'),
            stats={k: v for k, v in fd['stats'].items() if k != 'keeper'})
        ch = rec.get('charge') or {}
        if ch and fd['area'] > 0:
            rec['full_map_refined']['captured_fraction_at_R'] = (
                float(F(ch['area']) / fd['area']))
            rec['full_map_refined']['captured_fraction_at_Rmax'] = (
                float(F(ch['area_at_Rmax']) / fd['area']))
        print(f'{kind}: full(R=1/2, {len(cfg)} cfg) = {float(fd["area"]):.6f}  '
              f'extent_rel={fd.get("extent_rel")}  '
              f'charged = {ch.get("area_float")}  {fd["stats"]["seconds"]}s',
              flush=True)
        json.dump(doc, open(P, 'w'), indent=1)
