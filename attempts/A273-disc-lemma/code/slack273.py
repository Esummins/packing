"""A273 [M] the DROP slack at a fixed configuration, with an EXACT support-function gap (no area surrogate):
  gap(drop, K) = max_n [ min_{k in K} n.k - max(n.q + 1/2, n.p) ]   (drop = conv(D(q,1/2) u {p}), K convex polygon)
  t_drop(q, p) = min(gap(drop, Xi), gap(drop, Gam), 1/sqrt2 - |p - q|, depth(p, P), q_y - L_h, q_x - 1/2)
maximised over (q, p) by a q-grid x p-grid screen then Nelder-Mead.  Also a SOUNDNESS SAMPLER for drop273's kills:
random (q, p) with q in a K5-killed cell must have t_drop < 0.
    python slack273.py one hu hv thdeg xlow phideg   |   python slack273.py fam   -> results/slack273_<mode>.json"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom273 as G                                                   # noqa: E402
import sets273 as SE                                                  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
ANG = np.linspace(0, 2 * math.pi, 1440, endpoint=False)
NV = np.c_[np.cos(ANG), np.sin(ANG)]


def gap(q, p, K):
    Kp = np.array(K)
    mk = (NV @ Kp.T).min(axis=1)
    md = np.maximum(NV @ np.asarray(q) + 0.5, NV @ np.asarray(p))
    g = mk - md
    i = int(np.argmax(g))
    a = ANG[i]
    best = g[i]
    for da in np.linspace(-0.005, 0.005, 41):                         # local refinement of the best direction
        n = np.array([math.cos(a + da), math.sin(a + da)])
        best = max(best, float((Kp @ n).min() - max(n @ q + 0.5, n @ p)))
    return float(best)


def point_sets(m):
    b = [(v, v) for v in m]
    Xi, Gam = SE.nominal('xi', m), SE.nominal('gam', m)
    Tu = SE.T_outer(b)
    from shapely.geometry import Polygon
    hu, hv, th = m[0], m[1], m[2]
    c, s = math.cos(th), math.sin(th)
    C = Polygon([(hu + s, hv), (hu + s + c, hv + s), (hu + c, hv + s + c), (hu, hv + c)])
    P = Polygon(Tu).difference(C).difference(Polygon(Xi)).difference(Polygon(Gam))
    return Xi, Gam, P, hv + c


def t_drop(S, z):
    from shapely.geometry import Point
    Xi, Gam, P, Lh = S
    q, p = np.asarray(z[:2]), np.asarray(z[2:])
    zp = Point(p)
    dP = P.boundary.distance(zp) if P.contains(zp) else -P.distance(zp)
    return min(gap(q, p, Xi), gap(q, p, Gam), G.R2 - float(np.hypot(*(p - q))), dP, q[1] - Lh, q[0] - 0.5)


def best(m, seed=0):
    S = point_sets(m)
    P = S[2]
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = P.bounds
    ps = [np.array(P.representative_point().coords[0])]
    for pt in (P.geoms if hasattr(P, 'geoms') else [P]):
        ps += [np.array(v) for v in pt.exterior.coords]
    ps += [np.array([x0 + rng.random() * (x1 - x0), y0 + rng.random() * (y1 - y0)]) for _ in range(40)]
    cands = []
    for p in ps:
        for ang in np.linspace(0, 2 * math.pi, 16, endpoint=False):
            q = p + 0.69 * np.array([math.cos(ang), math.sin(ang)])
            z = np.r_[q, p]
            cands.append((t_drop(S, z), z))
    cands.sort(key=lambda t: -t[0])
    top = cands[0]
    for t0, z in cands[:8]:
        r = minimize(lambda v: -t_drop(S, v), z, method='Nelder-Mead', options=dict(maxfev=1500, xatol=1e-10, fatol=1e-13))
        if -r.fun > top[0]:
            top = (-r.fun, r.x)
    return float(top[0]), [float(v) for v in top[1]]


if __name__ == '__main__':
    if sys.argv[1] == 'one':
        m = [float(sys.argv[2]), float(sys.argv[3]), math.radians(float(sys.argv[4])), float(sys.argv[5]),
             math.radians(float(sys.argv[6]))]
        print(best(m))
