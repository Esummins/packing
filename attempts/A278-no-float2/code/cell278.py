r"""A278: the free cell of the Y-poke FLOAT2 witness, exactly.  Loads A277's witness (C, D, X poses in degrees; Y by
vertices; results/float277_witness.json), computes the LOW FOOTPRINTS I(Z) = x-projection of int Z meet {0 < y < 1},
the flat floor cells F_x = [x, x+1] x [0, 1] met by D only among {C, D, X, Y}, picks the middle one T, and then
CERTIFIES (disc test, exact up to floating point) that NO unit square Z inside [0, s]^2 with int Z disjoint from
int C, int D, int X, int Y meets T \ int D: every such Z contains the closed disc of radius 1/2 about its centre c
(so dist(c, obstacle) >= 1/2, c in [1/2, s - 1/2]^2) and lies inside the disc of radius 1/sqrt2 about c; hence it
suffices that dist(T \ int D, K_outer) > 1/sqrt2 where K_outer = [1/2, s-1/2]^2 minus the obstacles inflated by the
INSCRIBED 64-gon of the radius-1/2 disc (a subset of the true inflation, so K_outer contains every admissible centre).
Also a numerical adversary ([M] only) for the same question.  Runs < 20 s.
    python cell278.py  -> results/cell278.json (+ stdout)"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import local261 as L                                                   # noqa: E402

W = json.load(open(os.path.join(ROOT, 'attempts', 'A277-float2-room', 'results', 'float277_witness.json')))
S = W['side']
V = {k: L.verts(W['poses'][k][0], W['poses'][k][1], math.radians(W['poses'][k][2])) for k in ('C', 'D', 'X')}
V['Y'] = np.array(W['Y_vertices'])
P = {k: Polygon([tuple(p) for p in V[k]]) for k in V}
BAND = sbox(0, 0, S, 1)
R2 = 1 / math.sqrt(2)


def footprint(poly):
    q = poly.intersection(BAND)
    return (None if q.is_empty or q.area < 1e-12 else (float(q.bounds[0]), float(q.bounds[2])))


out = dict(side=S, gaps={f'{a}-{b}': float(P[a].distance(P[b])) for a in P for b in P if a < b},
           footprints={k: footprint(P[k]) for k in P})
IC, ID_, IY = out['footprints']['C'], out['footprints']['D'], out['footprints']['Y']
assert out['footprints']['X'] is None
# flat cells F_x met by D only among the four: (x, x+1) misses I(C) and I(Y), meets I(D)
lo = max(IC[1], ID_[0] - 1, 0.0)
hi = min(IY[0] - 1, ID_[1])
out['flat_cells_x_range'] = [lo, hi]
assert hi > lo
xs = 0.5 * (lo + hi)
T = sbox(xs, 0, xs + 1, 1)
out['cell'] = dict(x=xs, meeters={k: float(T.intersection(P[k]).area) for k in P})
assert all(out['cell']['meeters'][k] < 1e-12 for k in ('C', 'X', 'Y')) and out['cell']['meeters']['D'] > 0.1
# disc-test certificate of unreachability of T \ int D
NG = 64
gon = Polygon([(0.5 * math.cos(2 * math.pi * i / NG), 0.5 * math.sin(2 * math.pi * i / NG)) for i in range(NG)])
inflated = [Polygon([tuple(p) for p in V[k]]).union(unary_union([Polygon([(p[0] + g[0], p[1] + g[1]) for g in gon.exterior.coords[:-1]])
                                                                     for p in V[k]])).convex_hull for k in V]
K_outer = sbox(0.5, 0.5, S - 0.5, S - 0.5).difference(unary_union(inflated))
target = T.difference(P['D'])
dist = float(target.distance(K_outer))
out['disc_test'] = dict(dist_target_to_Kouter=dist, threshold=R2, margin=dist - R2, K_outer_area=float(K_outer.area),
                        target_area=float(target.area), certified=bool(dist > R2 + 1e-9))
# [M] numerical adversary: a unit square Z meeting T \ int D, disjoint from the four, inside the container


def score(x):
    Z = Polygon([tuple(p) for p in L.verts(x[0], x[1], x[2])])
    g = min(Z.distance(P[k]) if Z.intersection(P[k]).area < 1e-12 else -Z.intersection(P[k]).area ** 0.5 for k in P)
    cont = min(Z.bounds[0], Z.bounds[1], S - Z.bounds[2], S - Z.bounds[3])
    pen = Z.intersection(target).area ** 0.5 if Z.intersection(target).area > 0 else -Z.distance(target)
    return min(g, cont, pen)


rng = np.random.default_rng(278)
best = -9.0
for i in range(300):
    x0 = np.array([rng.uniform(0.5, 3.0), rng.uniform(0.5, 3.0), rng.uniform(0, math.pi / 2)])
    r = minimize(lambda x: -score(x), x0, method='Nelder-Mead', options=dict(xatol=1e-7, fatol=1e-9, maxiter=800))
    best = max(best, -r.fun)
out['adversary_sup_M'] = best
os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, '..', 'results', 'cell278.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
