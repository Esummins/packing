#!/usr/bin/env python3
"""quick structural exploration of A25's atlases (what is enumerated, what is 0)."""
import json
import sys
from fractions import Fraction as F

for path in ('../A25-wastage-atlas/results/atlas_single_3.84.json',
             '../A25-wastage-atlas/results/atlas_single_fine_3.84.json'):
    d = json.load(open(path))
    g = d['grid']
    h = F(g['h'])
    n = int(g['n_centre'])
    dth = float(g['dtheta_deg'])
    nth = int(round(float(g['theta_range'][1]) / dth))
    print('=' * 70)
    print(path)
    print(' h', h, 'n', n, 'dtheta', dth, 'nth', nth, 'counts', d['counts'])
    have = {}
    for c in d['cells']:
        i = int(F(c['cx'][0]) / h)
        j = int(F(c['cy'][0]) / h)
        k = int(round(c['theta_deg'][0] / dth))
        have[(k, i, j)] = F(c['dead_lb'])
    # symmetry pattern: are only i<=j stored?
    ij = set((i, j) for (k, i, j) in have)
    print(' distinct (i,j) with data:', len(ij), 'max i', max(i for i, j in ij),
          'max j', max(j for i, j in ij), ' any i>j?', any(i > j for i, j in ij))
    print(' distinct k:', sorted(set(k for (k, i, j) in have)))
    # band cells: min(cx0,cy0) <= 1.3471
    LIM = F(13471, 10000)
    band = [(k, i, j) for k in range(nth) for i in range(n) for j in range(n)
            if min(i * h, j * h) <= LIM]
    print(' band grid cells (all k,i,j with min(cx0,cy0)<=1.3471):', len(band))
    miss = [b for b in band if b not in have]
    print('   of which MISSING from atlas (=> value 0):', len(miss))
    if miss:
        from collections import Counter
        cnt = Counter((min(i, j), k) for (k, i, j) in miss)
        print('   sample missing (min(i,j)*h, theta0):',
              sorted(set((float(min(i, j) * h), k * dth) for (k, i, j) in miss))[:25])
    present = [have[b] for b in band if b in have]
    if present:
        print('   present:', len(present), ' min', float(min(present)),
              ' median', float(sorted(present)[len(present) // 2]),
              ' max', float(max(present)))
