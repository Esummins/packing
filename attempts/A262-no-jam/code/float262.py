"""A262 task 1 [M]: the FLOAT2 corner -- can TWO floaters C, D meet the box with NO wall toucher meeting it, both
JAMMED (no wall-touching cell of any tilt receives C or D)?   Local model (A261's local261 / jam261 imported):
squares C:F D:F A:H X:V; C, D meet the open box; A, X may or may not; objective
    t = min( pair gaps, depths of C and D, float distances of C and D, -J_C, -J_D ),
    J_C = sup over wall cells T of min( gap(T,A), gap(T,X), gap(T,D), depth(T,C) )   (J_D likewise, with C, D swapped)
Structured starts (HARD feasibility): A261's JAM witness with D placed on a grid inside the box's free region + the
mirror (C, D swapped roles), 60 starts; sup t > 0 <=> a JAMMED FLOAT2 corner.   python float262.py -> results/float262.json
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import jam261 as J                                                    # noqa: E402
L, G8 = J.L, J.G8
SQ, DIM = L.layout('C:F D:F A:H X:V')
A261 = os.path.join(G.ROOT, 'attempts', 'A261-box-meeters', 'results')


def terms(x):
    ps = L.poses(x, SQ)
    P = [L.verts(*p) for p in ps]
    t = [G8.sat_gap(P[i], P[j]) for i in range(4) for j in range(i)]
    t += [G8.depth(P[0], L.BOX), G8.depth(P[1], L.BOX)]
    t += [float(P[0][:, 0].min()), float(P[0][:, 1].min()), float(P[1][:, 0].min()), float(P[1][:, 1].min())]
    if min(t) > -0.05:
        gA, gX, gC, gD = J.gaps(P[2]), J.gaps(P[3]), J.gaps(P[0]), J.gaps(P[1])
        jC = np.minimum(np.minimum(np.minimum(gA, gX), gD), -gC).max()
        jD = np.minimum(np.minimum(np.minimum(gA, gX), gC), -gD).max()
        t += [-float(jC), -float(jD)]
    return t, ps


def x_of(pC, pD, pA, pX):
    wv = lambda th: abs(math.cos(th)) + abs(math.sin(th))
    f = lambda p: [math.sqrt(max(p[0] - wv(p[2]) / 2, 1e-4)), math.sqrt(max(p[1] - wv(p[2]) / 2, 1e-4)), p[2]]
    return f(pC) + f(pD) + [math.sqrt(max(pA[0] - wv(pA[2]) / 2, 1e-4)), pA[2], math.sqrt(max(pX[1] - wv(pX[2]) / 2, 1e-4)), pX[2]]


def main():
    G.Z.belownormal()
    best, bx, n = -9.0, None, 0
    for f in ('jam261_polished.json', 'jam261_a080.json'):
        w = json.load(open(os.path.join(A261, f)))['poses']
        for dx in (0.65, 0.8, 0.95):
            for dy in (0.65, 0.8, 0.95):
                for thd in (0.0, 14.0, 30.0):
                    for swap in (0, 1):
                        pD = [dx, dy, math.radians(thd)]
                        pC = w['C']
                        pA, pX = w['A'], w['X']
                        if swap:
                            pA = [pA[0] + 0.3, pA[1], pA[2]]
                            pX = [pX[0], pX[1] + 0.3, pX[2]]
                        x0 = x_of(pC, pD, pA, pX)
                        fun = lambda x: -min(terms(x)[0])
                        opt = dict(maxiter=1500, xatol=1e-7, fatol=1e-9, adaptive=True)
                        r = minimize(fun, x0, method='Nelder-Mead', options=opt)
                        r = minimize(fun, r.x, method='Nelder-Mead', options=opt)
                        n += 1
                        if -r.fun > best:
                            best, bx = -r.fun, r.x
                        print(n, '%.4f' % -r.fun, 'best %.4f' % best, flush=True)
    t, ps = terms(bx)
    out = dict(sup_t=float(best), starts=n, poses={s[0]: list(map(float, p)) for s, p in zip(SQ, ps)},
               terms=[float(v) for v in t], verdict='JAMMED FLOAT2 EXISTS' if best > 1e-6 else 'none found')
    json.dump(out, open(os.path.join(ATT, 'results', 'float262.json'), 'w'), indent=1)
    print(out['verdict'], best)


if __name__ == '__main__':
    main()
