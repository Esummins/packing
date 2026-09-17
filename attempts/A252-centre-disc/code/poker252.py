"""A252 addendum (coordinator / PI, 2026-09-18 00:30): the family-stuck RING structure is the
ring PLUS a POKER -- a free square whose corner lies in the OVERLAP of one wall's two slots
([0,1] x [s-2, 2] on the wall x = 0, or a D4 image) and whose body lies in the centre.  Without
it the sixteen eight-cell families {four corner boxes + one slot per wall} are met by the eight
ring squares only and Lemma CELLS teleports the ring into four corner dominoes; with it both
slots of that wall gain a ninth meeter and every family has |M| >= 9 > 8.  (A249's "+0.0017
poking square" at s-hat is exactly this square.)

So the capacity question is: does the pocket hold the POKER plus two more squares?  capacity <= 2
kills it (8 + 2 = 10 < 11), and the poker's pinned pose is a constraint that can only help:

    poke_margin   the poker's fit: containment, depth of the square in the overlap cell, gaps
                  to the eight ring squares (>= 0: it fits); over the four walls;
    anchored      with the poker in place, the centre set C' of the residual pocket (pocket minus
                  the poker), its diameter (< 1: at most ONE more square, so capacity <= 2), and
                  the far part {q in C : |q - c_p| >= 1} (the only place a further centre can be);
    protected     the adversarial search over ring + poker jointly (19 parameters): the true
                  family-stuck-ring adversary for far_O / sec_r / anchored.

    python poker252.py --mode shat|rows|protected [--sides ...] [--starts N]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import disc252 as D                                                   # noqa: E402
import adv252 as ADV                                                  # noqa: E402
import geom248 as G                                                   # noqa: E402

STOP = os.path.join(ATT, 'logs', 'STOP')
ROWS = os.path.join(ATT, 'results', 'poker252.jsonl')


def overlap_cell(s, wall):
    """the overlap of the two slots of wall 0 (x=0), 1 (y=0), 2 (x=s), 3 (y=s): (x0,x1,y0,y1)."""
    a, b = s - 2.0, 2.0
    return [(0, 1, a, b), (a, b, 0, 1), (s - 1, s, a, b), (a, b, s - 1, s)][wall]


def poke_margin(y, polys, s, wall):
    F = G.verts(y)
    m = min(F[:, 0].min(), F[:, 1].min(), s - F[:, 0].max(), s - F[:, 1].max(),
            G.depth_rect(F, overlap_cell(s, wall)))
    for V in polys:
        m = min(m, G.poly_gap(F, V))
    return float(m)


def find_poker(polys, s, restarts=12, seed=7, walls=(0, 1, 2, 3)):
    """best poker over the walls: (margin, pose, wall)."""
    rng = np.random.default_rng(seed)
    best = (-9.0, None, None)
    for wall in walls:
        x0, x1, y0, y1 = overlap_cell(s, wall)
        for _ in range(restarts):
            cx = rng.uniform(x0, x1) + (0.8 if wall == 0 else -0.8 if wall == 2 else 0)
            cy = rng.uniform(y0, y1) + (0.8 if wall == 1 else -0.8 if wall == 3 else 0)
            r = minimize(lambda z: -poke_margin(z, polys, s, wall), [cx, cy, rng.uniform(0, math.pi / 2)],
                         method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
            if -r.fun > best[0]:
                best = (float(-r.fun), [float(v) for v in r.x], wall)
    return best


def anchored(x, s, pose):
    """metrics of the residual centre set once the poker is in place."""
    polys, _ = D.ring(x, s)
    F = G.verts(pose)
    Cp = D.centre_set(polys + [F], s)
    pts = D.boundary_pts(Cp)
    cp = (pose[0], pose[1])
    C = D.centre_set(polys, s)
    pts0 = D.boundary_pts(C)
    far = pts0[np.hypot(pts0[:, 0] - cp[0], pts0[:, 1] - cp[1]) >= 1.0 - 1e-9] if len(pts0) else pts0
    return {'poker_centre': cp, 'residual_C_area': float(Cp.area), 'residual_diam': D.diam(pts),
            'residual_components': len(D.geoms(Cp)), 'far_part_diam': D.diam(far),
            'far_part_points': int(len(far)), 'poker_far_O': math.hypot(cp[0] - s / 2, cp[1] - s / 2)}


def joint_margin(z, s):
    """ring (16) + poker (3) + wall index fixed outside: min(ring margin, poke margin)."""
    x, y = list(z[:16]), list(z[16:19])
    m = D.margin(x, s)
    if m < -0.3:
        return m
    polys, _ = D.ring(x, s)
    return min(m, poke_margin(y, polys, s, int(round(z[19]))))


def protected_optimise(x0, s, metric, wall, need=0.002, pen=30.0, maxiter=4000, seed=1):
    polys, _ = D.ring(x0, s)
    pm, pose, _ = find_poker(polys, s, restarts=4, seed=seed, walls=(wall,))
    z0 = list(x0) + list(pose) + [wall]

    def J(z):
        m = joint_margin(z, s)
        f = ADV.metric_value(list(z[:16]), s, metric) if m > -0.25 else 0.0
        return -(f - pen * max(0.0, need - m))
    r = minimize(J, z0, method='Nelder-Mead',
                 options={'xatol': 1e-8, 'fatol': 1e-10, 'maxiter': maxiter, 'adaptive': True})
    z = [float(v) for v in r.x]
    z[19] = wall
    return z, joint_margin(z, s), ADV.metric_value(z[:16], s, metric)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='shat')
    ap.add_argument('--sides', default='3.82,3.877084,3.95,3.99')
    ap.add_argument('--metrics', default='far_O,sec_r')
    ap.add_argument('--starts', type=int, default=6)
    ap.add_argument('--maxiter', type=int, default=4000)
    a = ap.parse_args()
    D.belownormal()
    out_fn = os.path.join(ATT, 'results', 'poker252_%s.json' % a.mode)
    if a.mode == 'shat':
        j = json.load(open(os.path.join(D.ROOT, 'attempts', 'A249-type-t-chase', 'results', 'twotilted249_ring2.json')))
        y = j['3.877084']['result']['x']
        x = list(y[:4]) + list(y[4:8]) + list(y[:4]) + list(y[4:8])
        polys, _ = D.ring(x, D.SW)
        pm, pose, wall = find_poker(polys, D.SW, restarts=20)
        anc = anchored(x, D.SW, pose)
        res = {'side': D.SW, 'ring_margin': D.margin(x, D.SW), 'poke_margin': pm, 'pose': pose, 'wall': wall,
               'anchored': anc, 'per_wall': {w: find_poker(polys, D.SW, restarts=8, walls=(w,))[0] for w in range(4)}}
        print(json.dumps(res, indent=1))
        json.dump(res, open(out_fn, 'w', encoding='utf-8'), indent=1)
        return
    if a.mode == 'rows':
        best = json.load(open(ADV.BEST, encoding='utf-8')) if os.path.exists(ADV.BEST) else {}
        res = {}
        for key, r in best.items():
            s = float(r['side'])
            polys, _ = D.ring(r['x'], s)
            pm, pose, wall = find_poker(polys, s, restarts=8)
            res[key] = {'value': r['value'], 'ring_margin': r['margin'], 'poke_margin': pm, 'wall': wall,
                        'anchored': anchored(r['x'], s, pose) if pm > -0.5 else None}
            print('%s value %.4f poke margin %+.4f (wall %s) residual diam %s' % (key, r['value'], pm, wall,
                  None if res[key]['anchored'] is None else round(res[key]['anchored']['residual_diam'], 4)), flush=True)
        json.dump(res, open(out_fn, 'w', encoding='utf-8'), indent=1)
        return
    rows = []
    if os.path.exists(ROWS):
        rows = [json.loads(l) for l in open(ROWS, encoding='utf-8') if l.strip()]
    done = {(r['side'], r['metric'], r['start']) for r in rows}
    for metric in a.metrics.split(','):
        for s in [float(v) for v in a.sides.split(',')]:
            key_s = '%.6f' % s
            for name, x0 in ADV.starts(s, a.starts, 252):
                if os.path.exists(STOP):
                    print('STOP present', flush=True)
                    return
                if (key_s, metric, name) in done:
                    continue
                t0 = time.time()
                z, m, v = protected_optimise(x0, s, metric, wall=0, maxiter=a.maxiter)
                row = {'side': key_s, 'metric': metric, 'start': name, 'margin': m, 'value': v, 'z': z,
                       'anchored': anchored(z[:16], s, z[16:19]) if m > -0.5 else None, 'seconds': time.time() - t0}
                with open(ROWS, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(row) + '\n')
                print('protected s=%s %s %-12s margin %+.5f value %.4f residual diam %s (%.0fs)' % (
                    key_s, metric, name, m, v, None if row['anchored'] is None else round(row['anchored']['residual_diam'], 4),
                    row['seconds']), flush=True)
    print('PROTECTED DONE', flush=True)


if __name__ == '__main__':
    main()
