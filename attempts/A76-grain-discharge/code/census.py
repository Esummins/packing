#!/usr/bin/env python3
"""census.py -- the grain lattice of a protected class near Trump (group-state form) and the
float D1 (drain-flex) ratio of every grain of co-dimension <= DMAX at a target box.

Groups (Trump-frame, pins fixed): each Trump contact is a group with a finite list of STATES,
each state = the list of active rows (independent representatives; implied rows dropped):
  flush pair (i,j): FLUSH = [corner row a, tie t_i - t_j]; PA = [a]; PB = [b]; OPEN = []
  point contact:    ON = [row]; OFF = []
  corner square walls (4 rows, rank 3): any subset, represented by an independent subset
  single wall rows: ON/OFF
A grain = one state per group.  Its independent row set A' = pins + union of state rows
(rank checked in floats; states are chosen so that the union is independent except for the
wall-circuit and tie-cycle identities, which are removed by taking the ring's 4th tie out).
The D1 ratio = ||(M(box) - M(z0)) Y||_inf, M = [J_{A'}; e_s], Y = pinv(M(z0)) -- < 1 certifies
e_s not in rowspace(J_{A'}(z)) for all z in the box (drain-flex lemma).  Full-rank grains
(rank 34) are Krawczyk grains instead.
"""
import sys
import json
import itertools
import time
from fractions import Fraction as F
import numpy as np
from grainlib import *

DMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 6
RC = F(sys.argv[2]) if len(sys.argv) > 2 else F(1, 100)
RT = F(sys.argv[3]) if len(sys.argv) > 3 else F(1, 500)
PINS = [int(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 else [0, 1, 3, 5]

z0 = load_z0()
rows22, d22 = a22_rows()
z0f = to_float_z(z0)
NAME = {row_name(c): c for c in rows22}


def R(name):
    return NAME[name]


TIE = lambda i, j: {'kind': 'teq', 'i': i, 'j': j}
# flush pairs: (a, b) corner rows (A22 names), tie
FLUSH = [((6, 9), 'E6c1-9e2', 'E9c3-6e0'), ((7, 8), 'E7c1-8e2', 'E8c3-7e0'),
         ((7, 9), 'E7c2-9e3', 'E9c0-7e1'), ((8, 10), 'E8c2-10e3', 'E10c0-8e1'),
         ((9, 10), 'E9c1-10e2', 'E10c3-9e0')]
POINT = ['E1c2-8e3', 'E2c3-8e0', 'E3c2-7e3', 'E4c1-7e2', 'E4c2-6e3', 'E5c0-9e1']
WALLS = {0: ['W0c0[x=0]', 'W0c0[y=0]', 'W0c1[y=0]', 'W0c3[x=0]'],
         1: ['W1c0[y=0]', 'W1c1[y=0]'], 2: ['W2c0[y=0]', 'W2c1[y=0]', 'W2c1[x=s]', 'W2c2[x=s]'],
         3: ['W3c0[x=0]', 'W3c3[x=0]'], 4: ['W4c0[x=0]', 'W4c3[x=0]'],
         5: ['W5c1[x=s]', 'W5c2[x=s]', 'W5c2[y=s]', 'W5c3[y=s]'],
         6: ['W6c2[y=s]'], 10: ['W10c1[x=s]']}
UPRIGHT_PAIRS = {(0, 1): ['E1c0-0e1', 'E1c3-0e1'], (0, 3): ['E3c0-0e2', 'E3c1-0e2'],
                 (1, 3): ['E1c3-3e1', 'E3c1-1e2']}    # only used when a member is unpinned


def upright_row(name):
    # build the flush-upright corner rows (not in A22's list)
    m = name
    i = int(m[1:m.index('c')]); k = int(m[m.index('c') + 1:m.index('-')])
    j = int(m[m.index('-') + 1:m.index('e')]); e = int(m[m.index('e') + 1:])
    return {'kind': 'edge', 'i': i, 'corner': k, 'j': j, 'edge': e}


def build_groups(pins):
    groups = []
    for (i, j), a, b in FLUSH:
        groups.append(('flush%d-%d' % (i, j), [('FLUSH', [R(a), TIE(i, j)]), ('PA', [R(a)]),
                                               ('PB', [R(b)]), ('OPEN', [])]))
    for nm in POINT:
        groups.append((nm, [('ON', [R(nm)]), ('OFF', [])]))
    for sq, wl in WALLS.items():
        if sq in pins:
            continue
        states = []
        for r in range(len(wl) + 1):
            for sub in itertools.combinations(wl, r):
                states.append(('+'.join(sub) if sub else 'OFF', [R(n) for n in sub]))
        groups.append(('walls%d' % sq, states))
    for (i, j), rl in UPRIGHT_PAIRS.items():
        if i in pins and j in pins:
            continue
        states = []
        for r in range(len(rl) + 1):
            for sub in itertools.combinations(rl, r):
                states.append(('+'.join(sub) if sub else 'OFF', [upright_row(n) for n in sub]))
        groups.append(('upr%d-%d' % (i, j), states))
    return groups


def main():
    pins = PINS
    groups = build_groups(pins)
    prow = pin_rows(pins)
    rr = radii(RC, RT, RC)
    B = box(z0, rr)
    # caches: gradient at z0 (float) and half-widths over the box, per row name
    cache = {}

    def rowdata(c):
        nm = row_name(c)
        if nm not in cache:
            g0 = grad_row(z0f, c)
            gb = grad_row(B, c)
            v0 = np.zeros(NV); hw = np.zeros(NV)
            for k, v in g0.items():
                v0[k] = v
            for k, v in gb.items():
                hw[k] = max(float(v.hi) - v0[k], v0[k] - float(v.lo), 0.0)
            cache[nm] = (v0, hw)
        return cache[nm]

    es0 = np.zeros(NV); es0[S_IDX] = 1.0
    pin_rows_l = [rowdata(c) for c in prow]
    total = 1
    for _, st in groups:
        total *= len(st)
    print('pins %s  groups %d  total grains %d  box (rc,rt)=(%s,%s)  DMAX=%d'
          % (pins, len(groups), total, RC, RT, DMAX))
    # enumerate by co-dimension: precompute each state's row count; the full-rank count
    full_rank = 34
    results = []
    counts = {}
    t0 = time.time()
    ncomputed = 0
    # DFS over groups with pruning on the maximum possible rank
    maxrows = [max(len(rs) for _, rs in st) for _, st in groups]
    suffix_max = [0] * (len(groups) + 1)
    for gi in range(len(groups) - 1, -1, -1):
        suffix_max[gi] = suffix_max[gi + 1] + maxrows[gi]
    npin = len(prow)

    def rec(gi, chosen, nrows):
        nonlocal ncomputed
        if nrows + suffix_max[gi] < full_rank - DMAX:
            return
        if gi == len(groups):
            # assemble
            rowsA = list(prow)
            names = []
            for (gname, st), sidx in zip(groups, chosen):
                sname, rs = st[sidx]
                rowsA += rs
                names.append(sname)
            V = np.array([rowdata(c)[0] for c in rowsA])
            rank = np.linalg.matrix_rank(V, tol=1e-9) if len(rowsA) else 0
            codim = full_rank - rank
            counts[codim] = counts.get(codim, 0) + 1
            if codim > DMAX:
                return
            if codim == 0:
                results.append({'states': names, 'codim': 0, 'type': 'K'})
                return
            # independent subset (greedy) + D1 ratio
            keep = []
            M = np.zeros((0, NV))
            for c in rowsA:
                v = rowdata(c)[0]
                M2 = np.vstack([M, v])
                if np.linalg.matrix_rank(M2, tol=1e-9) > M.shape[0]:
                    M = M2; keep.append(c)
            HW = np.array([rowdata(c)[1] for c in keep] + [np.zeros(NV)])
            M0 = np.vstack([M, es0])
            Y = np.linalg.pinv(M0)
            ratio = float(np.max(np.sum(HW @ np.abs(Y), axis=1)))
            ncomputed += 1
            results.append({'states': names, 'codim': int(codim), 'type': 'D1', 'ratio': float(ratio)})
            return
        for sidx, (sname, rs) in enumerate(groups[gi][1]):
            rec(gi + 1, chosen + [sidx], nrows + len(rs))

    rec(0, [], npin)
    print('enumerated; counts by co-dim:', dict(sorted(counts.items())), ' computed D1: %d  (%.1fs)'
          % (ncomputed, time.time() - t0))
    hard = [r for r in results if r['type'] == 'D1' and r['ratio'] >= 1.0]
    print('K grains: %d;  D1 grains <= DMAX: %d;  HARD (ratio>=1): %d'
          % (sum(1 for r in results if r['type'] == 'K'), ncomputed, len(hard)))
    bycd = {}
    for r in results:
        if r['type'] == 'D1':
            bycd.setdefault(r['codim'], []).append(r['ratio'])
    for cd in sorted(bycd):
        v = sorted(bycd[cd])
        print('  codim %d: n=%5d  ratio min/median/max = %.2f / %.2f / %.2f   hard=%d'
              % (cd, len(v), v[0], v[len(v) // 2], v[-1], sum(1 for x in v if x >= 1)))
    hard.sort(key=lambda r: -r['ratio'])
    gn = [g for g, _ in groups]
    print('worst 25 hard grains:')
    for r in hard[:25]:
        deg = [('%s=%s' % (g, s)) for g, s in zip(gn, r['states'])
               if s not in ('FLUSH', 'ON') and not s.startswith('W')]
        deg = [('%s=%s' % (g, s)) for g, s in zip(gn, r['states'])
               if (g.startswith('flush') and s != 'FLUSH') or (g.startswith('E') and s != 'ON')
               or (g.startswith('walls') and s != '+'.join(WALLS[int(g[5:])]))
               or (g.startswith('upr') and '+' not in s)]
        print('  ratio %.2f codim %d: %s' % (r['ratio'], r['codim'], ', '.join(deg)))
    tag = 'census_%s_rc%s_rt%s_d%d' % ('-'.join(map(str, pins)), str(RC).replace('/', 'o'),
                                       str(RT).replace('/', 'o'), DMAX)
    json.dump({'pins': pins, 'rc': str(RC), 'rt': str(RT), 'DMAX': DMAX, 'groups': gn,
               'counts': {str(k): v for k, v in counts.items()},
               'results': results}, open(os.path.join(HERE, '..', 'results', tag + '.json'), 'w'))


if __name__ == '__main__':
    main()
