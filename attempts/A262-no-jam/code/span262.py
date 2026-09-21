"""A262 task 1 [M]: can the JAM corner's wall square X be a MIDDLE toucher -- a second toucher S on the same wall
ABOVE X, under the ceiling y = cap?  (Then the wall carries two touchers + the floater: count 8 + j.)

Local model of A261 (local261 / jam261 imported): C floats and meets the box, A touches the floor and meets the box,
X and S touch the wall x = 0, S above X.  t = min( pair gaps, box depths of C and A, float distances of C,
cap - top(S), -J ),  J = sup over wall-touching cells of min(gap(T,A), gap(T,X), gap(T,S), depth(T,C)).
Structured starts: A261's two witnesses, S seated on X at 12 tilts x 3 heights.  sup t < 0 at cap = s-hat  <=>  [M] at
s <= s-hat the JAM's X is the START of its wall.  Positive control: cap = 4.6 must return the JAM margin.
    python span262.py    -> results/span262.json
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
SQ, DIM = L.layout('C:F A:H X:V S:V')
A261 = os.path.join(G.ROOT, 'attempts', 'A261-box-meeters', 'results')


def terms(x, cap):
    ps = L.poses(x, SQ)
    P = [L.verts(*p) for p in ps]
    t = [G8.sat_gap(P[i], P[j]) for i in range(4) for j in range(i)]
    t += [G8.depth(P[0], L.BOX), G8.depth(P[1], L.BOX), float(P[0][:, 0].min()), float(P[0][:, 1].min())]
    t += [cap - float(P[3][:, 1].max()), float(P[3][:, 1].min() - P[2][:, 1].min())]
    if min(t) > -0.05:
        j = np.minimum(np.minimum(np.minimum(J.gaps(P[1]), J.gaps(P[2])), J.gaps(P[3])), -J.gaps(P[0]))
        t.append(-float(j.max()))
    return t, ps


def x_of(pC, pA, pX, yS, thS):
    wv = lambda th: abs(math.cos(th)) + abs(math.sin(th))
    return [math.sqrt(pC[0] - wv(pC[2]) / 2), math.sqrt(pC[1] - wv(pC[2]) / 2), pC[2],
            math.sqrt(pA[0] - wv(pA[2]) / 2), pA[2], math.sqrt(pX[1] - wv(pX[2]) / 2), pX[2], math.sqrt(yS), thS]


def main():
    G.Z.belownormal()
    out = []
    for cap in (G.SHAT, 3.95, 4.0, 4.6):
        best, bx, n = -9.0, None, 0
        for f in ('jam261_polished.json', 'jam261_a080.json'):
            w = json.load(open(os.path.join(A261, f)))['poses']
            topX = w['X'][1] + 0.5 * (math.cos(w['X'][2]) + math.sin(w['X'][2]))
            for thd in np.linspace(0.0, 44.0, 12):
                for dy in (-0.3, -0.15, 0.0):
                    x0 = x_of(w['C'], w['A'], w['X'], topX + dy, math.radians(thd))
                    fun = lambda x: -min(terms(x, cap)[0])
                    opt = dict(maxiter=1500, xatol=1e-7, fatol=1e-9, adaptive=True)
                    r = minimize(fun, x0, method='Nelder-Mead', options=opt)
                    r = minimize(fun, r.x, method='Nelder-Mead', options=opt)
                    n += 1
                    if -r.fun > best:
                        best, bx = -r.fun, r.x
        t, ps = terms(bx, cap)
        out.append(dict(cap=cap, sup_t=float(best), starts=n, poses={s[0]: list(map(float, p)) for s, p in zip(SQ, ps)},
                        terms=[float(v) for v in t], top_S=float(L.verts(*ps[3])[:, 1].max()),
                        verdict='JAM + second toucher EXISTS' if best > 1e-6 else 'none found'))
        print(cap, out[-1]['verdict'], '%.5f' % best, flush=True)
        json.dump(out, open(os.path.join(ATT, 'results', 'span262.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
