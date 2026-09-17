"""A248: the CONSISTENT EXTERNAL CHASE -- an 8-square ring below side 4 in which every one of the
twelve border cells is doubly met by the eight corner meeters alone, POKE's true form and
NO-ROTATE's click accounting hold at every wall with EXTERNAL blockers only, and then the room
test for the three free squares (the POCKET obligation).

Pattern (the only external pattern FLAT-ABOVE leaves, corner_chase.md s.3): flat meeters on the
floor (A_BL at offset dBL from x = 0, A_BR at offset dBR from x = s) and on the ceiling (their
180-degree images), pokers touching the two side walls in MUTUAL tilted pairs (B_BL, B_TL) on
x = 0 and their images on x = s; central symmetry (rotation by 180 degrees about the centre).

    python external248.py [--side 3.85] [--restarts 400] [--pocket 300]
        -> results/external248_<side>.json
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402

NAMES = ('A_BL', 'A_BR', 'B_BL', 'B_TL', 'A_TR', 'A_TL', 'B_TR', 'B_BR')


def ring(x, s):
    """x = (dBL, dBR, theta, d, theta_f, d_f) -> the eight squares (vertex arrays, global)."""
    dBL, dBR, th, d, thf, df = x
    A_BL = G.flat_floor(dBL)
    A_BR = G.flat_floor(dBR)                    # in BR's floor frame: rotate later
    B_BL = G.poker(th, d)                       # x = 0 wall frame = global
    B_TL = G.flip_up(G.poker(thf, df), s)       # TL's frame is x = 0's frame flipped
    A_BR = np.stack([s - A_BR[:, 0], A_BR[:, 1]], axis=1)
    rot = lambda V: np.stack([s - V[:, 0], s - V[:, 1]], axis=1)      # noqa: E731
    return [A_BL, A_BR, B_BL, B_TL, rot(A_BL), rot(A_BR), rot(B_BL), rot(B_TL)]


def cell_rects(s):
    C = {}
    for c in ('BL', 'BR', 'TR', 'TL'):
        for k, (u0, u1, v0, v1) in (('00', (0, 1, 0, 1)), ('01', (0, 1, 1, 2)), ('10', (1, 2, 0, 1))):
            X = (u0, u1) if c in ('BL', 'TL') else (s - u1, s - u0)
            Y = (v0, v1) if c in ('BL', 'BR') else (s - v1, s - v0)
            C[c + k] = (X[0], X[1], Y[0], Y[1])
    return C


def margins(polys, s):
    """(min pair gap, min wall gap, min over cells of the second-largest depth)."""
    pg = min(G.poly_gap(polys[i], polys[j]) for i in range(len(polys)) for j in range(i))
    wg = min(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()) for V in polys)
    sec = []
    for r in cell_rects(s).values():
        ds = sorted((G.depth_rect(V, r) for V in polys), reverse=True)
        sec.append(ds[1])
    return float(pg), float(wg), float(min(sec))


def objective(x, s):
    pg, wg, sec = margins(ring(x, s), s)
    return -min(pg, wg, sec)


def search(s, restarts, seed=248):
    rng = np.random.default_rng(seed)
    best = None
    for k in range(restarts):
        x0 = [rng.uniform(s - 3, 1), rng.uniform(s - 3, 1), rng.uniform(0.02, 1.5), rng.uniform(0.0, 0.3),
              rng.uniform(0.02, 1.5), rng.uniform(0.0, 0.3)]
        res = minimize(objective, x0, args=(s,), method='Nelder-Mead',
                       options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 4000})
        if best is None or res.fun < best.fun:
            best = res
        if best.fun < -1e-3:
            break
    return best


def pocket(polys, s, restarts, k=3, seed=1):
    """try to add k unit squares to the ring: maximise the least gap of the k new squares."""
    rng = np.random.default_rng(seed)

    def f(y):
        new = [G.verts(y[3 * i:3 * i + 3]) for i in range(k)]
        allp = polys + new
        m = float('inf')
        for i, V in enumerate(new):
            m = min(m, V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max())
            for j, W in enumerate(allp):
                if j != len(polys) + i:
                    m = min(m, G.poly_gap(V, W))
        return -m
    best = None
    for _ in range(restarts):
        y0 = np.concatenate([[rng.uniform(0.6, s - 0.6), rng.uniform(0.6, s - 0.6), rng.uniform(0, math.pi / 2)]
                             for _ in range(k)])
        res = minimize(f, y0, method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-11, 'maxiter': 6000})
        if best is None or res.fun < best.fun:
            best = res
        if best.fun < 0:
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--side', type=float, default=3.85)
    ap.add_argument('--restarts', type=int, default=400)
    ap.add_argument('--pocket', type=int, default=300)
    a = ap.parse_args()
    s = a.side
    t0 = time.time()
    best = search(s, a.restarts)
    polys = ring(best.x, s)
    pg, wg, sec = margins(polys, s)
    out = {'side': s, 'x': [float(v) for v in best.x], 'min_pair_gap': pg, 'min_wall_gap': wg,
           'min_second_depth': sec, 'ring_ok': min(pg, wg, sec) > 0,
           'poses': {n: list(map(float, G.pose_of(V))) for n, V in zip(NAMES, polys)},
           'search_seconds': time.time() - t0}
    print('side %.4f: ring margin %.4g (pair %.4g wall %.4g second-depth %.4g) in %.0f s' % (
        s, min(pg, wg, sec), pg, wg, sec, out['search_seconds']))
    if out['ring_ok']:
        t1 = time.time()
        for k in (1, 2, 3):
            pb = pocket(polys, s, a.pocket, k=k)
            out['pocket_%d' % k] = {'best_min_gap': float(-pb.fun), 'fits': bool(-pb.fun >= 0),
                                    'poses': [list(map(float, pb.x[3 * i:3 * i + 3])) for i in range(k)]}
            print('  pocket k=%d: best least gap %.4g -> %s' % (k, -pb.fun, 'FITS' if -pb.fun >= 0 else 'no'))
        out['pocket_seconds'] = time.time() - t1
    with open(os.path.join(ATT, 'results', 'external248_%.4f.json' % s), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
