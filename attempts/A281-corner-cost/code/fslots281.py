"""A281 F-SLOTS-ONE: can ONE free unit square meet both own slots c01 = [0,1]x[1,2] and c10 = [1,2]x[0,1] of an F corner
(flat A = [d,1+d]x[0,1] on the floor, poker B on the wall, both meeting the box) while interior-disjoint from A and B
and inside the container?  sup over (d, th_B, d_B, G pose) of the least margin; sup < 0 means NO (then the two slots
of an F corner always take two distinct free squares).    python fslots281.py [--sides 3.82,3.877083590022814]"""
import argparse
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom281 as G  # noqa: E402

DEG = math.pi / 180


def free_square(cx, cy, th):
    co, si = math.cos(th), math.sin(th)
    h = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
    return [(cx + co * a - si * b, cy + si * a + co * b) for a, b in h]


def margin(x, s):
    d, thB, dB, cx, cy, thG = x
    terms = [d, 1 - d, thB - 0.3 * DEG, 89.7 * DEG - thB, dB, 1 - dB, d - math.sin(thB)]
    A = G.float_square('A', 0.0, d, 0, s)
    B = G.float_square('B', thB, dB, 0, s)
    Q = free_square(cx, cy, thG)
    cl = G.cells(s, 0)
    terms.append(-G.gap(B, cl['c00']))
    terms.append(min(min(q[0] for q in Q), min(q[1] for q in Q), s - max(q[0] for q in Q), s - max(q[1] for q in Q)))
    terms += [G.gap(Q, A), G.gap(Q, B), -G.gap(Q, cl['c01']), -G.gap(Q, cl['c10'])]
    return min(terms)


def run(s, restarts, seed=1):
    rng = np.random.default_rng(seed)
    best = (-9, None)
    for r in range(restarts):
        x0 = np.array([rng.uniform(0.05, 0.95), rng.uniform(3, 70) * DEG, rng.uniform(0.3, 0.99),
                       rng.uniform(0.8, 2.2), rng.uniform(0.8, 2.2), rng.uniform(0, 90) * DEG])
        res = minimize(lambda z: -margin(z, s), x0, method='Nelder-Mead',
                       options={'maxiter': 4000, 'xatol': 1e-10, 'fatol': 1e-12})
        res = minimize(lambda z: -margin(z, s), res.x, method='Nelder-Mead',
                       options={'maxiter': 4000, 'xatol': 1e-11, 'fatol': 1e-13})
        if -res.fun > best[0]:
            best = (-res.fun, res.x)
    return best


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sides', default='3.82,%r' % G.SHAT)
    ap.add_argument('--restarts', type=int, default=60)
    a = ap.parse_args()
    out = {}
    for s in [float(v) for v in a.sides.split(',')]:
        m, x = run(s, a.restarts)
        out['%.6f' % s] = {'sup_margin': m, 'x': list(map(float, x)), 'restarts': a.restarts}
        print('F-SLOTS-ONE s=%.6f sup margin %+.5f  (d=%.3f thB=%.1f dB=%.3f G=(%.3f,%.3f,%.1f deg))' % (
            s, m, x[0], x[1] / DEG, x[2], x[3], x[4], x[5] / DEG), flush=True)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'fslots281.json'), 'w'), indent=1)
