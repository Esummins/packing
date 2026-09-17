"""A244 structure measurements behind the threshold (brief s.3): how many of the twelve border
cells ONE square can meet, whether a corner can be SELF-SUFFICIENT (two disjoint squares each
meeting all three of its cells), and the reach bound that kills the cross-corner supply.

    python hand244.py            -> results/hand244.json  (+ a printed summary)
"""
import itertools
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cells244 as C          # noqa: E402

SQ2 = math.sqrt(2.0)


def max_cells_one_square(s, ng=141, nt=46):
    """the largest number of the twelve cells a single unit square can meet at side s, by a grid
    over (cx, cy, theta) covering the border strip; also which triples occur."""
    rects = [(n, C.cell_rect(n, s)) for n in C.CELLS]
    best, witness = 0, None
    seen = set()
    xs = np.linspace(0.5, s - 0.5, ng)
    ths = np.linspace(0, math.pi / 2, nt)
    for th in ths:
        for cx in xs:
            for cy in xs:
                hit = tuple(n for n, r in rects if C.overlap_depth(cx, cy, th, r) > 1e-12)
                if len(hit) >= 3:
                    seen.add(hit)
                if len(hit) > best:
                    best, witness = len(hit), (float(cx), float(cy), float(th), hit)
    return best, witness, sorted(seen)


def _pen3(v, rects, delta):
    """two unit squares in the quadrant, both meeting every rect of `rects` to depth >= delta,
    interior-disjoint, inside the quadrant."""
    f = 0.0
    P = [(v[0], v[1], v[2]), (v[3], v[4], v[5])]
    for (cx, cy, th) in P:
        q = C.square_corners(cx, cy, th)
        for a in (q[:, 0].min(), q[:, 1].min()):
            f += min(a, 0.0) ** 2
        for r in rects:
            d = C.overlap_depth(cx, cy, th, r)
            f += min(d - delta, 0.0) ** 2
    g = _gap(P[0], P[1])
    f += min(g, 0.0) ** 2
    return f


def _gap(a, b):
    qa, qb = C.square_corners(*a), C.square_corners(*b)
    best = -1e9
    for (o, p, qo, qp) in ((a, b, qa, qb), (b, a, qb, qa)):
        for n in list(C.square_normals(o[2])) + [-C.square_normals(o[2])[0], -C.square_normals(o[2])[1]]:
            best = max(best, float((qp @ n).min() - (qo @ n).max()))
    return best


def self_sufficient_corner(delta=1e-3, tries=4000, seed=0):
    """can TWO disjoint unit squares in the closed quadrant each meet all three cells of the
    corner (0,1)^2, (0,1)x(1,2), (1,2)x(0,1)?  Random multistart on the penalty."""
    rects = [(0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 2.0), (1.0, 2.0, 0.0, 1.0)]
    rng = np.random.default_rng(seed)
    best = (float('inf'), None)
    for _ in range(tries):
        v0 = np.array([rng.uniform(0.2, 2.0), rng.uniform(0.2, 2.0), rng.uniform(0, math.pi / 2),
                       rng.uniform(0.2, 2.0), rng.uniform(0.2, 2.0), rng.uniform(0, math.pi / 2)])
        r = minimize(_pen3, v0, args=(rects, delta), method='Nelder-Mead',
                     options={'maxiter': 2000, 'xatol': 1e-10, 'fatol': 1e-18})
        if r.fun < best[0]:
            best = (float(r.fun), [float(x) for x in r.x])
        if best[0] <= 0.0:
            break
    return best


def one_square_three_cells(delta=1e-3, tries=400, seed=1):
    """the control: ONE square meeting all three cells of a corner is easy."""
    rects = [(0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 2.0), (1.0, 2.0, 0.0, 1.0)]
    rng = np.random.default_rng(seed)
    best = (float('inf'), None)
    for _ in range(tries):
        v0 = np.array([rng.uniform(0.3, 1.8), rng.uniform(0.3, 1.8), rng.uniform(0, math.pi / 2)])
        r = minimize(lambda v: sum(min(C.overlap_depth(v[0], v[1], v[2], rr) - delta, 0.0) ** 2
                                   for rr in rects)
                     + min(C.square_corners(v[0], v[1], v[2])[:, 0].min(), 0.0) ** 2
                     + min(C.square_corners(v[0], v[1], v[2])[:, 1].min(), 0.0) ** 2,
                     v0, method='Nelder-Mead', options={'maxiter': 1500, 'fatol': 1e-18})
        if r.fun < best[0]:
            best = (float(r.fun), [float(x) for x in r.x])
        if best[0] <= 0.0:
            break
    return best


def main():
    out = {}
    print('--- (a) how many of the twelve cells can ONE unit square meet?', flush=True)
    out['max_cells'] = {}
    for s in (3.82, 3.877084, 4.0, 4.2, 4.41421356, 4.6):
        b, w, triples = max_cells_one_square(s)
        out['max_cells']['%.6f' % s] = {'max': b, 'witness': w[:3], 'cells': list(w[3]),
                                        'n_triples': len(triples)}
        print('  s=%.6f  max cells met = %d  (%d distinct >=3-subsets)  witness %s'
              % (s, b, len(triples), w[3]), flush=True)

    print('--- (b) can a CORNER be self-sufficient (two disjoint squares, each meeting all three '
          'of its cells)?', flush=True)
    f1, v1 = one_square_three_cells()
    out['one_square_three_cells'] = {'penalty': f1, 'pose': v1}
    print('  control, ONE square meeting all three: penalty %.3e (0 = found) pose %s'
          % (f1, None if v1 is None else [round(x, 4) for x in v1]), flush=True)
    f2, v2 = self_sufficient_corner()
    out['self_sufficient_corner'] = {'penalty': f2, 'poses': v2, 'tries': 4000}
    print('  TWO disjoint squares, each meeting all three: best penalty %.3e over 4000 restarts'
          % f2, flush=True)

    print('--- (c) the reach bounds', flush=True)
    out['reach'] = {'adjacent_supply_max_side': 3 + SQ2,
                    'note': 'a square with points in c00 (x<1) and in the far slot of the same '
                            'wall (x>s-2) needs x-extent > s-3, and a unit square has extent '
                            '<= sqrt2: cross-corner supply needs s < 3 + sqrt2 = %.6f' % (3 + SQ2)}
    print('  cross-corner (ADJ) supply along a wall is impossible for s >= 3 + sqrt2 = %.6f'
          % (3 + SQ2), flush=True)
    with open(os.path.join(ATT, 'results', 'hand244.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print('written results/hand244.json', flush=True)


if __name__ == '__main__':
    main()
