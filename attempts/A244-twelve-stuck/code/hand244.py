"""A244 structure measurements behind the threshold (brief s.3): how many of the twelve border
cells ONE square can meet, whether a corner can be SELF-SUFFICIENT (two disjoint squares each
meeting all three of its cells), and the reach bound that kills the cross-corner supply.

    python hand244.py            -> results/hand244.json  (+ a printed summary)

Everything here is plain scalar geometry: for a unit square (cx, cy, th) and an axis-aligned
rect the overlap depth is the min over {ex, ey, n0, n1} of the projection overlap, with the
square's support width |a.n0| + |a.n1| and the rect's |a_x| wx + |a_y| wy.
"""
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
TRIPLE = ((0.0, 1.0, 0.0, 1.0), (0.0, 1.0, 1.0, 2.0), (1.0, 2.0, 0.0, 1.0))


def depth(cx, cy, th, r):
    """overlap depth of the unit square (cx, cy, th) with the rect r = (x0, x1, y0, y1)."""
    x0, x1, y0, y1 = r
    co, si = math.cos(th), math.sin(th)
    W = abs(co) + abs(si)
    bx, by = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    wx, wy = x1 - x0, y1 - y0
    best = min(min(cx + W / 2, x1) - max(cx - W / 2, x0),
               min(cy + W / 2, y1) - max(cy - W / 2, y0))
    for (ax, ay) in ((co, si), (-si, co)):
        ca = cx * ax + cy * ay
        v = abs(ax) * wx + abs(ay) * wy
        ba = bx * ax + by * ay
        best = min(best, min(ca + 0.5, ba + v / 2) - max(ca - 0.5, ba - v / 2))
    return best


def pair_gap(a, b):
    """separating-axis gap of two unit squares (>= 0 iff interior-disjoint)."""
    best = -1e9
    for (o, p) in ((a, b), (b, a)):
        co, si = math.cos(o[2]), math.sin(o[2])
        for (ax, ay) in ((co, si), (-si, co)):
            cp, sp = math.cos(p[2]), math.sin(p[2])
            hp = (abs(ax * cp + ay * sp) + abs(-ax * sp + ay * cp)) / 2.0
            d = (p[0] - o[0]) * ax + (p[1] - o[1]) * ay
            best = max(best, abs(d) - hp - 0.5)
    return best


def max_cells_one_square(s, ng=181, nt=181):
    """the largest number of the twelve cells one unit square can meet at side s, over a grid in
    (cx, cy, theta); vectorised over the grid."""
    rects = [C.cell_rect(n, s) for n in C.CELLS]
    xs = np.linspace(0.45, s - 0.45, ng)
    ths = np.linspace(0, math.pi / 2, nt)
    CX, CY = np.meshgrid(xs, xs, indexing='ij')
    CX, CY = CX.reshape(-1), CY.reshape(-1)
    best, wit, triples = 0, None, set()
    for th in ths:
        co, si = math.cos(th), math.sin(th)
        W = abs(co) + abs(si)
        hit = np.zeros((len(C.CELLS), CX.size), bool)
        for ci, (x0, x1, y0, y1) in enumerate(rects):
            bx, by, wx, wy = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
            d = np.minimum(np.minimum(CX + W / 2, x1) - np.maximum(CX - W / 2, x0),
                           np.minimum(CY + W / 2, y1) - np.maximum(CY - W / 2, y0))
            for (ax, ay) in ((co, si), (-si, co)):
                ca = CX * ax + CY * ay
                v = abs(ax) * wx + abs(ay) * wy
                ba = bx * ax + by * ay
                d = np.minimum(d, np.minimum(ca + 0.5, ba + v / 2) - np.maximum(ca - 0.5, ba - v / 2))
            hit[ci] = d > 1e-12
        cnt = hit.sum(axis=0)
        m = int(cnt.max())
        for j in np.nonzero(cnt >= 3)[0]:
            triples.add(tuple(C.CELLS[ci] for ci in np.nonzero(hit[:, j])[0]))
        if m > best:
            j = int(cnt.argmax())
            best, wit = m, (float(CX[j]), float(CY[j]), float(th),
                            [C.CELLS[ci] for ci in np.nonzero(hit[:, j])[0]])
    return best, wit, sorted(triples)


def _pen2(v, delta):
    f = 0.0
    P = ((v[0], v[1], v[2]), (v[3], v[4], v[5]))
    for (cx, cy, th) in P:
        co, si = math.cos(th), math.sin(th)
        W = (abs(co) + abs(si)) / 2.0
        f += min(cx - W, 0.0) ** 2 + min(cy - W, 0.0) ** 2
        for r in TRIPLE:
            f += min(depth(cx, cy, th, r) - delta, 0.0) ** 2
    f += min(pair_gap(P[0], P[1]), 0.0) ** 2
    return f


def _pen1(v, delta):
    cx, cy, th = v
    co, si = math.cos(th), math.sin(th)
    W = (abs(co) + abs(si)) / 2.0
    f = min(cx - W, 0.0) ** 2 + min(cy - W, 0.0) ** 2
    for r in TRIPLE:
        f += min(depth(cx, cy, th, r) - delta, 0.0) ** 2
    return f


def multistart(fn, n, tries, delta, seed):
    rng = np.random.default_rng(seed)
    best = (float('inf'), None)
    for _ in range(tries):
        v0 = np.concatenate([[rng.uniform(0.2, 2.2), rng.uniform(0.2, 2.2),
                              rng.uniform(0, math.pi / 2)] for _ in range(n // 3)])
        r = minimize(fn, v0, args=(delta,), method='L-BFGS-B',
                     options={'maxiter': 600, 'ftol': 1e-20, 'gtol': 1e-16})
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
        out['max_cells']['%.6f' % s] = {'max': b, 'witness': list(w[:3]), 'cells': list(w[3]),
                                        'n_subsets_ge3': len(triples),
                                        'subsets_ge3': [list(t) for t in triples[:40]]}
        print('  s=%.6f  max cells met = %d  (%d distinct >=3-subsets)  witness %s'
              % (s, b, len(triples), w[3]), flush=True)
    print('--- (b) can a CORNER be self-sufficient?', flush=True)
    for delta, tries in ((1e-3, 1500), (1e-6, 1500)):
        f1, v1 = multistart(_pen1, 3, 300, delta, 1)
        f2, v2 = multistart(_pen2, 6, tries, delta, 0)
        out['corner_%g' % delta] = {'one_square': {'penalty': f1, 'pose': v1},
                                    'two_squares': {'penalty': f2, 'poses': v2, 'tries': tries}}
        print('  delta %g: ONE square meeting all three cells of a corner: penalty %.3e '
              '(0 = found); TWO disjoint squares each meeting all three: %.3e over %d restarts'
              % (delta, f1, f2, tries), flush=True)
    print('--- (c) the reach bounds', flush=True)
    out['reach'] = {'adjacent_supply_max_side': 3 + SQ2,
                    'note': 'a square with points in a corner box (u < 1) and in the FAR slot of '
                            'the same wall (u > s - 2) needs extent > s - 3 along that wall, and '
                            'a unit square has extent <= sqrt2: the cross-corner (ADJ) supply is '
                            'impossible for s >= 3 + sqrt2 = %.6f' % (3 + SQ2)}
    print('  cross-corner (ADJ) supply along a wall is impossible for s >= 3 + sqrt2 = %.6f'
          % (3 + SQ2), flush=True)
    with open(os.path.join(ATT, 'results', 'hand244.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
    print('written results/hand244.json', flush=True)


if __name__ == '__main__':
    main()
