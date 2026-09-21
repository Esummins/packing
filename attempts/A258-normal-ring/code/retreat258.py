"""A258 addendum [M]: the RETREAT of the seated poker, and the room for a BLOCKER beside it.

For normal rings (tight C4 slice and LP-centre points of D) with the SEATED poker F on wall 0:
  lift      F + tau * (inward wall normal), tau = 1 - cos(phi) + 1e-3 (F's lowest vertex leaves the band d < 1):
            the least gap of the lifted F to the eight ring squares (>= 0: the RING does not hold F down), and the
            Hall minimum of ring + lifted F (0: the structure UNSTICKS -- the coordinator's point);
  sliver    the areas F shares with the slots L = [1,2] x [0,1] and R = [s-2, s-1] x [0,1] (exact polygon clipping);
  blocker   sup over a TENTH unit square G (HARD containment: centre parametrised inside the container) of
            min(gap(G, ring squares), gap(G, F)): < 0 means no unit square fits in the pocket beside the seated poker,
            so nothing can hold F down -- the 9-square structure cannot be completed to a retreat-blocked one.
Output results/retreat258.jsonl.
"""
import json
import math
import os

import numpy as np
from scipy.optimize import minimize

import dom258 as Dm
import geo258 as G
import poker258 as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'results', 'retreat258.jsonl'))


def clip_area(Q, R):
    """area of (convex polygon Q) n (axis rectangle R given as 4 vertices) by Sutherland-Hodgman."""
    x0, x1 = R[:, 0].min(), R[:, 0].max()
    y0, y1 = R[:, 1].min(), R[:, 1].max()
    poly = [tuple(p) for p in Q]
    for axis, bound, keep_less in ((0, x0, False), (0, x1, True), (1, y0, False), (1, y1, True)):
        out = []
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            pin = (p[axis] <= bound) if keep_less else (p[axis] >= bound)
            qin = (q[axis] <= bound) if keep_less else (q[axis] >= bound)
            if pin:
                out.append(p)
            if pin != qin:
                t = (bound - p[axis]) / (q[axis] - p[axis])
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
        poly = out
        if not poly:
            return 0.0
    a = 0.0
    for i in range(len(poly)):
        a += poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
    return abs(a) / 2


def blocker(nine, s, rng, starts=12):
    best = -9.0
    f = lambda z: -min(G.sat_gap(P.square(z[0], z[1], z[2], s), Q) for Q in nine)
    for _ in range(starts):
        z0 = P.inv(rng.uniform(0.9, s - 0.9), rng.uniform(0.9, s - 0.9), rng.uniform(0, math.pi / 2), s)
        r = minimize(f, z0, method='Nelder-Mead', options=dict(xatol=1e-7, fatol=1e-9, maxiter=500))
        best = max(best, float(-r.fun))
    return best


def main():
    rng = np.random.default_rng(2581)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        for s in (3.82, G.SHAT, 3.99):
            for deg in (8, 14.545, 22):
                phi = [deg * G.DEG] * 4
                for kind in ('tight', 'centre'):
                    if kind == 'tight':
                        a = [G.tight_ring(s, phi[0])[0]] * 4
                    else:
                        a = Dm.sup_margin(s, phi, slots=True)[1]
                    if a is None or G.in_D(s, a, phi) < -1e-9 or min(G.tooth_terms(s, a[0], phi[0])) <= 0:
                        continue
                    ring = G.ring(s, a, phi)
                    F = G.seated(s, 0, a[0], phi[0])
                    tau = 1 - math.cos(phi[0]) + 1e-3
                    lifted = F + np.array([0.0, tau])
                    cl = G.cells(s)
                    row = dict(s=s, phi_deg=deg, kind=kind, a=a[0], hall_seated=G.hall_min(ring + [F], s)[0],
                               sliver_area_L=clip_area(F, cl[('L', 0)]), sliver_area_R=clip_area(F, cl[('R', 0)]),
                               sliver_depth=1 - math.cos(phi[0]), lift=tau,
                               lift_gap_to_ring=min(G.sat_gap(lifted, Q) for Q in ring),
                               hall_lifted=G.hall_min(ring + [lifted], s)[0],
                               blocker_sup_gap=blocker(ring + [F], s, rng))
                    f.write(json.dumps(row) + '\n')
                    f.flush()
                    print('%.4f %6.3f %-6s hall %d -> lifted %d (gap to ring %+.4f)  sliver L %.1e R %.1e  blocker %+.4f'
                          % (s, deg, kind, row['hall_seated'], row['hall_lifted'], row['lift_gap_to_ring'],
                             row['sliver_area_L'], row['sliver_area_R'], row['blocker_sup_gap']), flush=True)


if __name__ == '__main__':
    main()
