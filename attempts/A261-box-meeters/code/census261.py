"""A261 task 1/2 [M]: CENSUS of the box meeters of every doubly-met corner of the corpus (A244's twelve-stuck rows,
A217's witnesses, the ring witnesses), split below / above side 4.

Per corner box c00 (A255's cell system, imported -- never edited): its meeters, which of the corner's two walls each
touches, the class
    PAIR        exactly two meeters, one touching each wall of the box
    SAME-WALL   exactly two meeters, both touchers, both on the SAME wall of the box only
    FLOAT1      exactly two meeters, exactly one touches no wall of the box
    FLOAT2      exactly two meeters, neither touches a wall of the box
    THIRD       three or more meeters (sub-class by the touch pattern)
and for every FLOATING meeter C the two DROP CELLS T_u, T_v (C translated straight to each wall of the box): who
meets them (P1 of normal_ring.md says: a toucher, or >= 2 squares) -- 'free' means C alone meets the drop cell, so
(E2) lands C on the wall and the packing is not a Phi1-maximiser.

    python census261.py   ->  results/census261.jsonl, results/census261_summary.json
"""
import collections
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
for p in ('attempts/A249-type-t-chase/code', 'attempts/A248-corner-chase/code', 'attempts/A255-common-sense/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import numpy as np                                                   # noqa: E402
import geo255 as G                                                   # noqa: E402
import sense255 as S5                                                # noqa: E402

OUT = os.path.join(ATT, 'results', 'census261.jsonl')
SUM = os.path.join(ATT, 'results', 'census261_summary.json')


def sat_gap(A, B):
    best = -1e9
    for P in (A, B):
        e = np.roll(P, -1, 0) - P
        n = np.stack([e[:, 1], -e[:, 0]], 1)
        n = n / np.linalg.norm(n, axis=1, keepdims=True)
        pa, pb = A @ n.T, B @ n.T
        best = max(best, float(np.maximum(pa.min(0) - pb.max(0), pb.min(0) - pa.max(0)).max()))
    return best


def drop(V, wall, s):
    """the polygon V translated straight onto the wall."""
    V = V.copy()
    if wall == 'x0':
        V[:, 0] -= V[:, 0].min()
    elif wall == 'x1':
        V[:, 0] += s - V[:, 0].max()
    elif wall == 'y0':
        V[:, 1] -= V[:, 1].min()
    else:
        V[:, 1] += s - V[:, 1].max()
    return V


def corner(c, s, poses, polys, tch, table):
    root = table[(c, '00', 0)]
    wv, wh = G.WALL_V[c], G.WALL_H[c]
    pat = []
    for i in root:
        t = tch[i]
        pat.append('B' if (wv in t and wh in t) else 'V' if wv in t else 'H' if wh in t else 'O')
    rec = dict(corner=c, meeters=list(root), touch=pat, tilts=[round(G.phi_deg(poses[i][2]), 3) for i in root])
    k = len(root)
    if k < 2:
        rec['cls'] = 'NOT-DOUBLE'
    elif k == 2:
        p = ''.join(sorted(pat))
        rec['cls'] = ('PAIR' if p == 'HV' else 'SAME-WALL' if p in ('HH', 'VV') else 'FLOAT2' if p == 'OO'
                      else 'FLOAT1' if 'O' in p else 'OTHER:' + p)
    else:
        rec['cls'] = 'THIRD:' + ''.join(sorted(pat))
    drops = []
    for i, t in zip(root, pat):
        if t != 'O':
            continue
        for wall in (wv, wh):
            T = drop(polys[i], wall, s)
            who = [j for j in range(len(polys)) if j != i and -sat_gap(T, polys[j]) > 1e-9]
            drops.append(dict(sq=i, wall=wall, dist=float(np.abs(T - polys[i]).max()), blockers=who,
                              blocker_touch=[sorted(tch[j]) for j in who],
                              blocker_meets_box=[j in root for j in who], free=len(who) == 0))
    rec['drops'] = drops
    return rec


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cnt = collections.Counter()
    free_drop = collections.Counter()
    ex = {}
    with open(OUT, 'w', encoding='utf-8') as f:
        for name, rid, s, poses in S5.corpora():
            polys = [G.corners_of(*p) for p in poses]
            tch = [G.touches(p[0], p[1], p[2], s) for p in poses]
            table = G.meeter_table(poses, s, [(c, '00', 0) for c in G.CORNERS])
            band = 'lt4' if s < 4 - 1e-9 else 'ge4'
            for c in G.CORNERS:
                r = corner(c, s, poses, polys, tch, table)
                r.update(corpus=name, rid=rid, s=s, n=len(poses))
                cnt[(name, band, r['cls'])] += 1
                for d in r['drops']:
                    free_drop[(name, band, 'free' if d['free'] else 'blocked:' + (
                        'toucher' if any(d['blocker_touch']) else 'floaters'))] += 1
                if r['cls'] not in ('PAIR', 'NOT-DOUBLE'):
                    key = (band, r['cls'])
                    if key not in ex or s < ex[key]['s']:
                        ex[key] = dict(rid=rid, corpus=name, s=s, corner=c)
                    f.write(json.dumps(r) + '\n')
    summ = dict(counts={'%s|%s|%s' % k: v for k, v in sorted(cnt.items())},
                drops={'%s|%s|%s' % k: v for k, v in sorted(free_drop.items())},
                least_side_example={'%s|%s' % k: v for k, v in sorted(ex.items())})
    json.dump(summ, open(SUM, 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
