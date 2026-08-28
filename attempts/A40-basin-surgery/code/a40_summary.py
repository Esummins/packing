#!/usr/bin/env python
"""Summarise results/growth.json into the report table."""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, '..', 'results', 'growth.json')))

print('ring  h_in      h_out     modes                                  '
      'certs  branched-pairs  minmarg    wall')
tot = 0
for r in J['rings']:
    modes = Counter(v['mode'] for v in r['faces'].values())
    prs = set()
    for v in r['faces'].values():
        for p in v.get('pairs', []):
            prs.add(tuple(p))
    tot += r['n_certs']
    print('%3d  %.6f  %.6f  %-36s  %5d  %-14s  %.2e  %5.1fs'
          % (r['ring'], r['h_in_float'], r['h_out_float'],
             dict(modes), r['n_certs'],
             ','.join('%d%d' % p for p in sorted(prs)) or '-',
             r['min_anchor_margin'] or 0.0, r['wall_s']))
print('h reached %.6f  rings %d  certs total %d  wall %.1fs'
      % (J['h_reached'], J['n_rings'], tot,
         J['meta'].get('wall_seconds', float('nan'))))
if J.get('saturation'):
    print('SATURATION:', json.dumps(J['saturation'])[:600])
