"""A248: SEPARATE-NOTCHES -- in the pinwheel (every wall carries exactly one type-F poker) can ONE
free square supply two adjacent pokers' slots?  Setting on the wall x = 0 at side s: BL's poker B
(tilt t, depth d, touching x = 0, beside BL's flat floor meeter at offset <= 1), TL's flat meeter
A_TL = [0,1] x [y0, y0+1] on x = 0 with 2 <= y0 < s - 1 (FLAT-ABOVE: y0 >= 2), TL's poker B_TL
touching the ceiling beside A_TL (tilt t', depth d'), and a free square F that meets BL01 and TL10
with positive depth and is interior-disjoint from B, A_TL, B_TL.  The sup of the least margin over
all parameters is computed by many restarts of Nelder-Mead; a negative sup is the [M] evidence.
    python notches248.py [--side 3.877084] [--restarts 400]  -> results/notches248_<side>.json
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402


def scene(x, s):
    t, d, y0, tf, df, cx, cy, ph = x
    B = G.poker(t, d)
    A = np.array([(0, y0), (1, y0), (1, y0 + 1), (0, y0 + 1)], float)
    P = G.poker(tf, df)                                    # TL frame: (u, v) = (s - y, x)
    Btl = np.stack([P[:, 1], s - P[:, 0]], axis=1)
    F = G.verts((cx, cy, ph))
    return B, A, Btl, F


def margin(x, s):
    t, d, y0, tf, df, cx, cy, ph = x
    if not (0 < t < math.pi / 2 and 0 < tf < math.pi / 2):
        return -1.0
    B, A, Btl, F = scene(x, s)
    m = min(d, df, (1 - math.sin(t)) * math.tan(t) - d, y0 - 2, s - 1 - y0,
            G.depth_rect(F, (0, 1, 1, 2)), G.depth_rect(F, (1, 2, s - 1, s)),
            G.poly_gap(F, B), G.poly_gap(F, A), G.poly_gap(F, Btl), G.poly_gap(B, A), G.poly_gap(Btl, A),
            F[:, 0].min(), F[:, 1].min(), s - F[:, 0].max(), s - F[:, 1].max(), s - Btl[:, 1].max())
    # B_TL's TILT-MIN against A_TL in TL's frame: offset delta = s - 1 - y0
    m = min(m, (s - 1 - y0 - math.sin(tf)) * math.tan(tf) - df)
    return float(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--side', type=float, default=3.877084)
    ap.add_argument('--restarts', type=int, default=400)
    a = ap.parse_args()
    s = a.side
    rng = np.random.default_rng(248)
    best = None
    for k in range(a.restarts):
        x0 = [rng.uniform(0.02, 1.5), rng.uniform(0, 0.25), rng.uniform(2, s - 1), rng.uniform(0.02, 1.5),
              rng.uniform(0, 0.25), rng.uniform(0.5, 2.0), rng.uniform(1.5, s - 0.5), rng.uniform(0, math.pi / 2)]
        r = minimize(lambda x: -margin(x, s), x0, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': 6000})
        if best is None or r.fun < best.fun:
            best = r
    out = {'side': s, 'sup_margin': float(-best.fun), 'x': [float(v) for v in best.x], 'restarts': a.restarts}
    print('side %.6f: sup least margin of a free square serving BL01 and TL10 = %+.5f' % (s, -best.fun))
    json.dump(out, open(os.path.join(ATT, 'results', 'notches248_%.4f.json' % s), 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
