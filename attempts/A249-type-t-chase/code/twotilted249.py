"""A249: TWO-TILTED -- the type-T analogue of TWO-POKERS, as a SAT feasibility search.

WALL problem (mode 'wall'): on the wall x = 0 at side s the two type-T corners c = BL and c' = TL,
each with a wall-touching tilted meeter (B, B') and a floor / ceiling-touching tilted meeter (A, A'),
all four strictly tilted, both corner boxes met by their two squares, the four squares pairwise
interior-disjoint and inside the container, and the wall's two slots c01 = (0,1)x(1,2) and
c'01 = (0,1)x(s-2,s-1) each met by a square of the OTHER corner (sub-cases: BB' mutual wall pair,
BA', AB', AA' -- the tips).  The sup over the 8 parameters of the least margin is > 0 iff the
configuration exists at s.

RING problem (mode 'ring'): all four corners type T with both meeters touching, every meeter
reaching the far slot of its wall (every slot supplied by the adjacent corner: the all-ADJ ring
FAMILY-STUCK allows without a free square at the slots); 16 parameters (or 8 under the central
symmetry C2, mode 'ring2').  The least side at which the sup-margin is > 0 is s_T*(ring).

    python twotilted249.py --mode wall|ring2|ring [--sides 3.82,3.877084,...] [--restarts N]
        -> results/twotilted249_<mode>.json   (one entry per side; resumable; logs/STOP honoured)
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
import geom249 as T                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402

HALF = math.pi / 2
SUBCASES = ('BB', 'BA', 'AB', 'AA')          # who supplies c01 (first letter: c''s square) / c'01


def corner_pair(th_B, d_B, th_A, d_A):
    return T.wall_square(th_B, d_B), T.floor_square(th_A, d_A)


def place(V, corner, s):
    """map a BL-frame vertex array to the corner's position by the reflections of geom248."""
    if corner == 'BL':
        return V
    if corner == 'TL':
        return G.flip_up(V, s)
    if corner == 'BR':
        return np.stack([s - V[:, 0], V[:, 1]], axis=1)
    return np.stack([s - V[:, 0], s - V[:, 1]], axis=1)          # TR: the C2 image of BL


def tilt_margin(th):
    return min(th, HALF - th)


def common_terms(polys, s):
    m = [G.poly_gap(polys[i], polys[j]) for i in range(len(polys)) for j in range(i)]
    # containment is a hard side condition (the squares touch their walls by construction, so the
    # wall distances are not margins): 1 - 10 x violation stays >= 1 when the square is inside
    m += [1.0 - 10.0 * max(0.0, -min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()))
          for V in polys]
    return m


def wall_margin(x, s, sub, terms=False):
    tB, dB, tA, dA, tBp, dBp, tAp, dAp = x
    if not all(0 < t < HALF for t in (tB, tA, tBp, tAp)):
        return [-1.0] * 30 if terms else -1.0
    B, A = corner_pair(tB, dB, tA, dA)
    Bp, Ap = (place(V, 'TL', s) for V in corner_pair(tBp, dBp, tAp, dAp))
    polys = [B, A, Bp, Ap]
    c01, cp01 = (0, 1, 1, 2), (0, 1, s - 2, s - 1)
    m = common_terms(polys, s)
    m += [tilt_margin(t) for t in (tB, tA, tBp, tAp)]
    m += [dB, dA, dBp, dAp]                                           # not wedged
    m += [G.depth_rect(B, (0, 1, 0, 1)), G.depth_rect(A, (0, 1, 0, 1)),
          G.depth_rect(Bp, (0, 1, s - 1, s)), G.depth_rect(Ap, (0, 1, s - 1, s))]
    sup01 = Bp if sub[0] == 'B' else Ap                               # c''s square into c01
    sup_p = B if sub[1] == 'B' else A                                 # c's square into c'01
    m += [G.depth_rect(sup01, c01), G.depth_rect(sup_p, cp01)]
    return [float(v) for v in m] if terms else float(min(m))


def ring_polys(x, s, sym):
    """x = 4 params per corner (BL, BR, TR, TL) or 2 corners (BL, BR) under C2."""
    corners = ('BL', 'BR', 'TR', 'TL')
    xs = list(x) if not sym else list(x[:4]) + list(x[4:8]) + list(x[:4]) + list(x[4:8])
    polys, names = [], []
    for k, c in enumerate(corners):
        tB, dB, tA, dA = xs[4 * k:4 * k + 4]
        B, A = corner_pair(tB, dB, tA, dA)
        polys += [place(B, c, s), place(A, c, s)]
        names += ['B_' + c, 'A_' + c]
    return polys, names, xs


def ring_margin(x, s, sym, terms=False):
    polys, names, xs = ring_polys(x, s, sym)
    ts = [xs[4 * k + j] for k in range(4) for j in (0, 2)]
    if not all(0 < t < HALF for t in ts):
        return [-1.0] * 84 if terms else -1.0
    m = common_terms(polys, s)
    m += [tilt_margin(t) for t in ts]
    m += [xs[4 * k + j] for k in range(4) for j in (1, 3)]           # deltas > 0
    # own box and far slot, in the BL frame of each corner (the reflections preserve cells)
    for k in range(4):
        tB, dB, tA, dA = xs[4 * k:4 * k + 4]
        B, A = corner_pair(tB, dB, tA, dA)
        m += [G.depth_rect(B, (0, 1, 0, 1)), G.depth_rect(A, (0, 1, 0, 1)),
              G.depth_rect(B, (0, 1, s - 2, s - 1)), G.depth_rect(A, (s - 2, s - 1, 0, 1))]
    return [float(v) for v in m] if terms else float(min(m))


def random_start(rng, k, kind):
    """kind 0: uniform; 1: near-flush wall squares with steep pokers (the type-F limit);
    2: mid tilts with deep wall squares (the notch regime)."""
    out = []
    for _ in range(k):
        if kind == 1:
            tB = rng.uniform(0.02, 0.35) if rng.random() < 0.5 else rng.uniform(HALF - 0.35, HALF - 0.02)
            out += [tB, rng.uniform(0.75, 1.0), rng.uniform(0.7, HALF - 0.05), rng.uniform(0.6, 1.0)]
        elif kind == 2:
            out += [rng.uniform(0.3, 1.27), rng.uniform(0.35, 1.0), rng.uniform(0.3, 1.27), rng.uniform(0.35, 1.0)]
        else:
            out += [rng.uniform(0.05, HALF - 0.05), rng.uniform(0.0, 1.0), rng.uniform(0.05, HALF - 0.05), rng.uniform(0.0, 1.0)]
    return out


def polish(f, x, s, iters=300):
    """SLSQP on the slack form: maximise t subject to every margin term >= t (numerical gradients
    of the min-objective are useless; the slack form sees the active terms)."""
    def terms(x):
        return f(x, s, True)
    k = len(terms(x))
    y0 = np.concatenate([x, [f(x, s)]])
    cons = {'type': 'ineq', 'fun': lambda y: np.asarray(terms(y[:-1])) - y[-1]}
    try:
        r = minimize(lambda y: -y[-1], y0, method='SLSQP', constraints=[cons],
                     options={'maxiter': iters, 'ftol': 1e-12})
        xn = r.x[:-1]
        if f(xn, s) > f(x, s):
            return xn
    except Exception:
        pass
    return x


def sup_margin(f, dim, s, restarts, seed, maxiter):
    rng = np.random.default_rng(seed)
    best = None
    for k in range(restarts):
        x0 = random_start(rng, dim // 4, k % 3)
        r = minimize(lambda x: -f(x, s), x0, method='Nelder-Mead',
                     options={'xatol': 1e-10, 'fatol': 1e-12, 'maxiter': maxiter, 'adaptive': dim > 8})
        if best is None or r.fun < best.fun:
            best = r
    x = polish(f, best.x, s)
    return float(f(x, s)), [float(v) for v in x]


def run_side(mode, s, restarts, seed):
    if mode == 'wall':
        out = {}
        for sub in SUBCASES:
            m, x = sup_margin(lambda x, s, t=False: wall_margin(x, s, sub, t), 8, s, restarts, seed, 4000)
            out[sub] = {'sup_margin': m, 'x': x}
            print('  s = %.6f  wall %s  sup margin %+.5f' % (s, sub, m), flush=True)
        return out
    sym = mode == 'ring2'
    m, x = sup_margin(lambda x, s, t=False: ring_margin(x, s, sym, t), 8 if sym else 16, s, restarts, seed, 6000 if sym else 20000)
    print('  s = %.6f  %s  sup margin %+.5f' % (s, mode, m), flush=True)
    return {'sup_margin': m, 'x': x}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='wall')
    ap.add_argument('--sides', default='3.82,3.877084,3.90,3.934,3.96,4.0')
    ap.add_argument('--restarts', type=int, default=60)
    ap.add_argument('--seed', type=int, default=249)
    a = ap.parse_args()
    try:
        sys.path.insert(0, os.path.join(ATT, '..', 'A248-corner-chase', 'code'))
        import chase248
        chase248.belownormal()
    except Exception:
        pass
    fn = os.path.join(ATT, 'results', 'twotilted249_%s.json' % a.mode)
    res = json.load(open(fn, encoding='utf-8')) if os.path.exists(fn) else {}
    for s in [float(v) for v in a.sides.split(',')]:
        if os.path.exists(os.path.join(ATT, 'logs', 'STOP')):
            print('STOP present')
            break
        key = '%.6f' % s
        if key in res and res[key].get('restarts', 0) >= a.restarts:
            continue
        t0 = time.time()
        r = run_side(a.mode, s, a.restarts, a.seed)
        r = {'result': r, 'restarts': a.restarts, 'seconds': time.time() - t0}
        res[key] = r
        json.dump(res, open(fn, 'w', encoding='utf-8'), indent=1)


if __name__ == '__main__':
    main()
