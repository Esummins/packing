"""A249: the POCKET of the type-T external ring -- for every ring witness found by twotilted249
(modes ring2 / ring with sup margin > 0): (i) the rigorous WASTE / coverable-area bound and the
PIERCE(1) certificate at the centre (A237 geom237: capacity <= 1 when the eroded free-centre
region of every tilt bin lies in one kernel about the centre), (ii) the best PIERCE(2) with two
points on a grid, (iii) the direct search for k = 1, 2, 3 free squares in the pocket (A248
external248.pocket), and (iv) the FAMILY-STUCK requirement -- one free square poking into a wall
pocket between the mutual pair (both slots of that wall met) -- as a separate search.

    python pocket249.py [--restarts 200]   -> results/pocket249.json
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import twotilted249 as W                                              # noqa: E402
import geom248 as G                                                   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
import external248 as X                                               # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A237-pocket-waste', 'code'))
import geom237 as G237                                                # noqa: E402


def poses_of(polys):
    return [tuple(map(float, G.pose_of(V))) for V in polys]


def pierce2(members, s, free, r=0.6, g=6):
    """best pair of piercing points on a grid about the centre (symmetric pairs c +/- d)."""
    c = s / 2.0
    best = None
    for a in range(-g, g + 1):
        for b in range(-g, g + 1):
            d = (r * a / g, r * b / g)
            pts = [(c + d[0], c + d[1]), (c - d[0], c - d[1])]
            v = G237.pierce(members, s, pts, 1.0, free=free)
            if best is None or v < best[0]:
                best = (float(v), pts)
    return best


def wall_poke(polys, s, restarts, seed=7):
    """one free square meeting BOTH slots of the wall x = 0 (BL01 and TL01 = (0,1)x(s-2,s-1)),
    disjoint from the ring: the FAMILY-STUCK requirement on some wall (D4: x = 0 w.l.o.g.)."""
    rng = np.random.default_rng(seed)

    def f(y):
        F = G.verts(y)
        m = min(F[:, 0].min(), F[:, 1].min(), s - F[:, 0].max(), s - F[:, 1].max(),
                G.depth_rect(F, (0, 1, 1, 2)), G.depth_rect(F, (0, 1, s - 2, s - 1)))
        for V in polys:
            m = min(m, G.poly_gap(F, V))
        return -m
    best = None
    from scipy.optimize import minimize
    for _ in range(restarts):
        y0 = [rng.uniform(0.6, 2.2), rng.uniform(1.2, s - 1.2), rng.uniform(0, math.pi / 2)]
        r = minimize(f, y0, method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
        if best is None or r.fun < best.fun:
            best = r
    return float(-best.fun), [float(v) for v in best.x]


def analyse(x, s, sym, restarts):
    polys, names, xs = W.ring_polys(x, s, sym)
    poses = poses_of(polys)
    out = {'side': s, 'margin': W.ring_margin(x, s, sym), 'poses': dict(zip(names, poses))}
    t0 = time.time()
    Wt = G237.waste(list(poses), s, 1.0)
    out['pocket_area'] = float(Wt['area'])
    out['coverable_area'] = float(Wt['coverable_area'])
    out['waste'] = float(Wt['waste'])
    out['pierce1_centre'] = float(G237.pierce(list(poses), s, [(s / 2, s / 2)], 1.0, free=Wt['free']))
    p2 = pierce2(list(poses), s, Wt['free'])
    out['pierce2_best'] = {'residual': p2[0], 'points': p2[1]}
    out['pierce_seconds'] = time.time() - t0
    out['capacity_le_1'] = bool(out['pierce1_centre'] <= 1e-9)
    out['capacity_le_2'] = bool(p2[0] <= 1e-9)
    for k in (1, 2, 3):
        pb = X.pocket(polys, s, restarts, k=k)
        out['pocket_%d' % k] = {'best_min_gap': float(-pb.fun), 'fits': bool(-pb.fun >= 0),
                                'poses': [list(map(float, pb.x[3 * i:3 * i + 3])) for i in range(k)]}
    m, y = wall_poke(polys, s, restarts)
    out['wall_poke'] = {'best_margin': m, 'pose': y, 'fits': bool(m >= 0)}
    print('s %.6f: waste %.3f of %.3f, pierce1 %.2e (cap<=1 %s), pierce2 %.2e; pocket 1/2/3: %.3g / %.3g / %.3g; wall poke %.3g' % (
        s, out['waste'], out['pocket_area'], out['pierce1_centre'], out['capacity_le_1'], p2[0],
        out['pocket_1']['best_min_gap'], out['pocket_2']['best_min_gap'], out['pocket_3']['best_min_gap'], m), flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=200)
    a = ap.parse_args()
    try:
        import chase248
        chase248.belownormal()
    except Exception:
        pass
    out = {}
    for mode in ('ring2', 'ring'):
        fn = os.path.join(ATT, 'results', 'twotilted249_%s.json' % mode)
        if not os.path.exists(fn):
            continue
        res = json.load(open(fn, encoding='utf-8'))
        for key, r in sorted(res.items()):
            if r['result']['sup_margin'] > 0:
                out['%s@%s' % (mode, key)] = analyse(r['result']['x'], float(key), mode == 'ring2', a.restarts)
    json.dump(out, open(os.path.join(ATT, 'results', 'pocket249.json'), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
