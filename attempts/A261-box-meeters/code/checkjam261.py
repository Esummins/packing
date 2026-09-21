"""A261: exact-geometry CHECK of the JAMMED FLOATER witness (results/jam261_polished.json), independent of the search
objective: containment, pairwise SAT gaps, box meetings, C floats; then the inner supremum
    J = sup over wall-touching cells T (x = 0 or y = 0, any tilt, any position) of min(gap(T,A), gap(T,X), depth(T,C))
and E = the same with gap(T, C) (an EMPTY wall cell), by a FINE grid (1 deg, 0.01) + Nelder-Mead from the 150 best
grid cells of each.  J < 0 and E < 0  <=>  no wall cell can receive C (E2) or is empty.  [M]: the inner sup is
numerical (2 parameters, piecewise smooth), not a certificate.      python checkjam261.py"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jam261 as J                                                     # noqa: E402  (fine grid: JAM_COARSE unset)
L, G8 = J.L, J.G8
RES = os.path.join(HERE, '..', 'results')
w = json.load(open(os.path.join(RES, 'jam261_polished.json')))
P = {k: L.verts(*w['poses'][k]) for k in ('C', 'A', 'X')}
out = dict(contain=min(float(p.min()) for p in P.values()),
           gaps={a + b: G8.sat_gap(P[a], P[b]) for a, b in (('C', 'A'), ('C', 'X'), ('A', 'X'))},
           meet={k: G8.depth(P[k], L.BOX) for k in P}, float_C=[float(P['C'][:, 0].min()), float(P['C'][:, 1].min())],
           touch_A=float(P['A'][:, 1].min()), touch_X=float(P['X'][:, 0].min()),
           tilts_deg={k: math.degrees(w['poses'][k][2]) for k in P})
gC, gA, gX = J.gaps(P['C']), J.gaps(P['A']), J.gaps(P['X'])
N = len(J.CELLS) // 2


def cell(wall, p, th):
    wv = abs(math.cos(th)) + abs(math.sin(th))
    return L.verts(0.5 * wv, 0.5 * wv + p, th) if wall == 0 else L.verts(0.5 * wv + p, 0.5 * wv, th)


def sup(score, fun):
    best = -9.0
    for i in np.argsort(-score)[:150]:
        wall, k = (0, i) if i < N else (1, i - N)
        th, p = J.CTH[i], J.POS[k % len(J.POS)]
        r = minimize(lambda z: -fun(cell(wall, abs(z[0]), z[1])), [p, th], method='Nelder-Mead',
                     options=dict(xatol=1e-10, fatol=1e-13, maxiter=1000))
        best = max(best, -r.fun)
    return float(max(best, score.max()))


# only cells inside the region the three squares control: below X's top on the wall, left of A's right end on the floor
top, right = J.CELLS[:, :, 1].max(1), J.CELLS[:, :, 0].max(1)
mask = np.concatenate([top[:N] < P['X'][:, 1].max(), right[N:] < P['A'][:, 0].max()])
sJ = np.where(mask, np.minimum(np.minimum(gA, gX), -gC), -9.0)
sE = np.where(mask, np.minimum(np.minimum(gA, gX), gC), -9.0)
out['J_receiving_cell'] = sup(sJ, lambda T: min(G8.sat_gap(T, P['A']), G8.sat_gap(T, P['X']), G8.depth(T, P['C'])))
out['E_empty_cell'] = sup(sE, lambda T: min(G8.sat_gap(T, P['A']), G8.sat_gap(T, P['X']), G8.sat_gap(T, P['C'])))
out['ok'] = bool(out['contain'] >= 0 and min(out['gaps'].values()) > 0 and out['meet']['C'] > 0 and out['meet']['A'] > 0
                 and out['meet']['X'] <= 0 and min(out['float_C']) > 0 and out['J_receiving_cell'] < 0
                 and out['E_empty_cell'] < 0 and abs(out['touch_A']) < 1e-12 and abs(out['touch_X']) < 1e-12)
json.dump(out, open(os.path.join(RES, 'checkjam261.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
