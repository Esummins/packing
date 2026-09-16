"""A237 pocket census (docs/proofs/pocket_waste.md s.2-s.4): for every pocket the lab has -- the ring
rand_0_0569|t20 and the 193 HELD / CROWD four-crowds (loaded component U from A233's arm233.jsonl, the pocket =
container minus U, the other n - p squares pack in it), A226's nine eight-square crowd rings at n = 11 (S < 4),
and the 21 records (U = the wall touchers; not rings: the census must not fire) -- the pocket polygon, its boundary
features, the rigorous WASTE bound (geom237: coverable-set sandwich over 1-degree tilt bins), the soundness check
coverable area >= n - p, the uncoverable components attributed to features, and the PIERCE(n - p) test with the
resident squares' centres as the piercing points.
    python pocket237.py [--quick]   -> results/pocket237.jsonl (one row per pocket)
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import psutil
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    psutil.Process().cpu_affinity(list(range(16)))
except Exception:
    pass
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A236-ring-capacity', 'code'))
import geom237 as G                                                    # noqa: E402
import band236 as BD                                                   # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ATTS = os.path.abspath(os.path.join(ATT, '..'))
WIT = os.path.join(ATTS, 'A217-torque-probe', 'results', 'witnesses217.jsonl')
ARM = os.path.join(ATTS, 'A233-local-lock', 'results', 'arm233.jsonl')
RING11 = os.path.join(ATTS, 'A226-one-flush', 'results', 'ring11_226.jsonl')
OUT = os.path.join(ATT, 'results', 'pocket237.jsonl')
RING = 'rand_0_0569|t20'
STEP = 1.0


def loaded_components():
    U = {}
    for l in open(ARM, encoding='utf-8'):
        r = json.loads(l)
        U.setdefault(r['wid'], set()).update((r.get('chain') or {}).get('component') or [])
    return U


def feature_summary(verts, edges):
    conv = [v['angle'] for v in verts if v['convex']]
    return {'n_vertices': len(verts), 'n_convex': len(conv), 'n_reflex': len(verts) - len(conv),
            'n_acute': sum(a < 90.0 - 1e-6 for a in conv), 'n_right': sum(abs(a - 90.0) <= 1e-6 for a in conv),
            'n_obtuse': sum(a > 90.0 + 1e-6 for a in conv), 'min_convex_angle': min(conv) if conv else None,
            'n_edges': len(edges), 'n_tilted_edges': sum(not e['flush'] for e in edges),
            'tilted_edge_len': sum(e['len'] for e in edges if not e['flush']),
            'edge_tilts': sorted({round(e['tilt'], 2) for e in edges if not e['flush']})}


def census(label, src, members, s, n, rest_poses, extra=None):
    t0 = time.time()
    W = G.waste(members, s, STEP)
    verts, edges = G.features(W['pocket'])
    comps = G.attribute(G.components(W['uncov']), verts)
    k = len(rest_poses)
    row = {'label': label, 'src': src, 's': s, 'n': n, 'p': len(members), 'k': k,
           'area': W['area'], 'coverable': W['coverable_area'], 'waste': W['waste'],
           'sound': bool(W['coverable_area'] >= k - 1e-6), 'area_bound_cap': int(math.floor(W['coverable_area'] + 1e-9)),
           'area_bound_fires': bool(W['coverable_area'] < k), 'features': feature_summary(verts, edges),
           'components': [{'area': c['area'], 'cx': c['cx'], 'cy': c['cy'],
                           'vertex': {kk: c['vertex'][kk] for kk in ('x', 'y', 'angle', 'convex')} if c['vertex'] else None,
                           'vertex_dist': c['vertex_dist']} for c in comps[:12]],
           'n_components': len(comps), 'members': [list(m) for m in members], 'rest': [list(p) for p in rest_poses]}
    if k > 0:
        pts = [(p[0], p[1]) for p in rest_poses]
        row['pierce_k'] = G.pierce(members, s, pts, STEP, free=W['free'])
        row['pierce_k_ok'] = bool(row['pierce_k'] <= 1e-9)
    if extra:
        row.update(extra)
    row['secs'] = time.time() - t0
    return row


def best_pierce1(members, S, free, r=0.3, g=7):
    """the best single piercing point on a (2g+1)^2 grid of half-width r about the centre."""
    c = S / 2.0
    best = None
    for a in range(-g, g + 1):
        for b in range(-g, g + 1):
            pt = (c + r * a / g, c + r * b / g)
            v = G.pierce(members, S, [pt], STEP, free=free)
            if best is None or v < best[0]:
                best = (v, pt)
    return best


def four_crowds():
    out = []
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            out.append(w)
    out.sort(key=lambda w: (w['rid'] != RING, w['wid']))
    return out


def main():
    quick = '--quick' in sys.argv
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    U = loaded_components()
    rows = []
    for w in four_crowds():
        u = sorted(U.get(w['wid'], set()))
        if not u:
            continue
        poses, s = [(w['z'][3 * i], w['z'][3 * i + 1], w['z'][3 * i + 2]) for i in range(11)], w['z'][-1]
        members = [poses[i] for i in u]
        rest = [poses[i] for i in range(11) if i not in u]
        rows.append(census(w['wid'], '193', members, s, 11, rest, {'rid': w['rid'], 'cls': w['cls'], 'U': u}))
        print(rows[-1]['label'], 'p=%d k=%d area %.3f cov %.3f waste %.3f pierce %s %.1fs' % (
            len(u), len(rest), rows[-1]['area'], rows[-1]['coverable'], rows[-1]['waste'],
            rows[-1].get('pierce_k_ok'), rows[-1]['secs']), flush=True)
        if quick and len(rows) >= 3:
            break
    for l in open(RING11, encoding='utf-8'):
        r = json.loads(l)
        ring = [tuple(p) for p in r['ring']]
        S = r['S']
        row = census('ring8_S%.2f_eps%.2f' % (S, r['eps']), 'ring11', ring, S, 11, [], {'eps': r['eps'], 'a226_kmax': r['k_max_greedy']})
        c = S / 2.0
        free = G.coverable(ring, S, STEP)[1]
        row['pierce_centre'] = G.pierce(ring, S, [(c, c)], STEP, free=free)
        row['pierce1'], row['pierce1_pt'] = best_pierce1(ring, S, free)
        row['pierce1_ok'] = bool(row['pierce1'] <= 1e-9)
        best = None
        for t in (0.3, 0.4, 0.5, 0.6):
            for pts in ([(c - t, c - t), (c + t, c + t)], [(c - t, c + t), (c + t, c - t)]):
                v = G.pierce(ring, S, pts, STEP, free=free)
                if best is None or v < best[0]:
                    best = (v, pts)
        row['pierce2'], row['pierce2_pts'] = best[0], best[1]
        row['pierce2_ok'] = bool(best[0] <= 1e-9)
        rows.append(row)
        print(row['label'], 'area %.3f cov %.3f waste %.3f centre %.4f pierce1 %.2e at %s pierce2 %.4f' % (
            row['area'], row['coverable'], row['waste'], row['pierce_centre'], row['pierce1'], row['pierce1_pt'],
            row['pierce2']), flush=True)
    for l in open(BD.SURVEY, encoding='utf-8'):
        r = json.loads(l)
        poses, s = [tuple(p) for p in r['squares']], r['side']
        C = BD.classify(poses, s)
        touch = [i for i, q in enumerate(C['squares']) if q['walls']]
        members = [poses[i] for i in touch]
        rest = [poses[i] for i in range(len(poses)) if i not in touch]
        rows.append(census(r['label'], 'record', members, s, r['n'], rest, {'touchers': touch}))
        print(rows[-1]['label'], 'p=%d k=%d area %.3f cov %.3f waste %.3f sound %s pierce %s %.1fs' % (
            len(touch), len(rest), rows[-1]['area'], rows[-1]['coverable'], rows[-1]['waste'], rows[-1]['sound'],
            rows[-1].get('pierce_k_ok'), rows[-1]['secs']), flush=True)
        if quick:
            break
    with open(OUT, 'w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    print('wrote', OUT, len(rows), 'rows')


if __name__ == '__main__':
    main()
