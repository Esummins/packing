#!/usr/bin/env python3
"""admissible-but-zero band cells of the A25 atlases (the gap that matters)."""
import json
import math
from fractions import Fraction as F
from collections import Counter

S = F(96, 25)
LIM = F(13471, 10000)          # centre within this of a wall  (0.64 + sqrt2/2)


def wlo(th0_deg):
    """rational LOWER bound on min_{th in bin} (cos th + sin th); bins are inside
    [0,45] where cos+sin increases, so the min is at th0."""
    v = math.cos(math.radians(th0_deg)) + math.sin(math.radians(th0_deg))
    return F(int(v * 10 ** 9), 10 ** 9)          # <= true value


def admissible(x0, x1, y0, y1, th0):
    w = wlo(th0)
    lo, hi = w / 2, S - w / 2
    return max(x0, lo) <= min(x1, hi) and max(y0, lo) <= min(y1, hi)


for path in ('../A25-wastage-atlas/results/atlas_single_3.84.json',
             '../A25-wastage-atlas/results/atlas_single_fine_3.84.json'):
    d = json.load(open(path))
    g = d['grid']
    h = F(g['h'])
    n = int(g['n_centre'])
    dth = float(g['dtheta_deg'])
    ks = sorted(set(int(round(c['theta_deg'][0] / dth)) for c in d['cells']))
    have = {}
    for c in d['cells']:
        i = int(F(c['cx'][0]) / h)
        j = int(F(c['cy'][0]) / h)
        k = int(round(c['theta_deg'][0] / dth))
        have[(k, i, j)] = F(c['dead_lb'])
    print('=' * 74)
    print(path, ' h=', h, ' dtheta=', dth, ' theta bins k in', ks)
    tot = adm = zero = 0
    zeros = []
    vals = []
    for k in ks:
        for i in range(n):
            for j in range(n):
                x0, x1, y0, y1 = i * h, (i + 1) * h, j * h, (j + 1) * h
                if min(x0, y0) > LIM:
                    continue                       # not a band cell
                tot += 1
                if not admissible(x0, x1, y0, y1, k * dth):
                    continue
                adm += 1
                v = have.get((k, i, j))
                if v is None or v == 0:
                    zero += 1
                    zeros.append((k, i, j, float(min(x0, y0)), k * dth))
                else:
                    vals.append((v, k, i, j))
    print(f'  band grid cells {tot}, ADMISSIBLE {adm}, of which value-0/missing {zero}')
    vals.sort()
    if vals:
        print(f'  positive: {len(vals)}  min={float(vals[0][0]):.4f} at '
              f'(k={vals[0][1]},i={vals[0][2]},j={vals[0][3]})  '
              f'median={float(vals[len(vals)//2][0]):.4f}  max={float(vals[-1][0]):.4f}')
        print('  10 smallest positive:',
              [(round(float(v), 4), f'th{k*dth:.0f}', f'x{float(i*h):.2f}',
                f'y{float(j*h):.2f}') for v, k, i, j in vals[:10]])
    c = Counter((z[3], z[4]) for z in zeros)
    print('  zero cells by (min(cx0,cy0), theta0):')
    for key in sorted(c):
        print(f'     d={key[0]:.3f} th={key[1]:.0f}: {c[key]}')
