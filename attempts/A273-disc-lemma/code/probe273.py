"""A273 probe: is A272's DISC LEMMA (distance form) true on H1-H3, and is the DROP form (the full cone
conv(D(q,1/2) u {p}) misses int Xi and int Gam) true?  Configurations along the flat-X family near X_low -> C_top.
    t_disc (A272 s.5): min(dist(q,Xi)-1/2, dist(q,Gam)-1/2, q_y-L_h, q_x-1/2, 1/sqrt2 - dist(q,P))
    t_drop: max over (q, p) of min(t_disc terms at q, 1/sqrt2-|p-q|, depth of p in P, -pen(drop, Xi), -pen(drop, Gam))
      pen(D, K) = sqrt(area(D n K)) if they overlap else -dist(D, K)  (a search surrogate, NOT a certificate)
    t_sq  (left272.best_Q, A272): the unit-square statement itself.
    python probe273.py [scan|one hu hv thdeg xlow phideg] -> results/probe273_<mode>.json"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Point, MultiPoint

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A272-strip-jam', 'code'))
import disc272b as DB                                                 # noqa: E402
import left272 as LF                                                  # noqa: E402

R = DB.R
RES = os.path.join(HERE, '..', 'results')
R2 = 0.5 ** 0.5


def config(hu, hv, th, xl, phi):
    """a full H1-H3 point: (a_x, alpha, side) chosen to maximise the smallest H1-H3 margin (grid + Nelder-Mead)."""
    def m(z):
        return float(R.constraints(np.array([hu, hv, th, xl, phi, z[0], z[1], z[2]])).min())
    best = max(((m((a, al, sd)), (a, al, sd)) for a in np.linspace(0.3, 1.6, 27)
                for al in np.radians(np.linspace(0.1, 44.9, 23)) for sd in (3.83, 3.85, 3.87)))
    r = minimize(lambda z: -m(z), np.array(best[1]), method='Nelder-Mead', options=dict(maxfev=800, xatol=1e-10))
    z = r.x if -r.fun > best[0] else np.array(best[1])
    return np.array([hu, hv, th, xl, phi, z[0], z[1], z[2]])


def sets(q):
    Xi, Gam, P, Lh, Ctop, xlow = DB.sets(q, 'all')
    P = P.difference(Gam)                                             # P := S \ int(Xi u Gam)  (A272 s.2 P3)
    return Xi, Gam, P, Lh


def pen(D, K):
    if D.intersects(K):
        return math.sqrt(max(D.intersection(K).area, 0.0))
    return -D.distance(K)


def t_drop_at(S, z):
    Xi, Gam, P, Lh = S
    q, p = z[:2], z[2:]
    zq, zp = Point(q), Point(p)
    dP = P.boundary.distance(zp) if P.contains(zp) else -P.distance(zp)
    D = MultiPoint([tuple(v) for v in (q + 0.5 * np.c_[np.cos(np.linspace(0, 2 * math.pi, 48, endpoint=False)),
                                                        np.sin(np.linspace(0, 2 * math.pi, 48, endpoint=False))])]
                   + [tuple(p)]).convex_hull
    return float(min(zq.distance(Xi) - 0.5, zq.distance(Gam) - 0.5, q[1] - Lh, q[0] - 0.5,
                     R2 - float(np.hypot(*(p - q))), dP, -pen(D, Xi), -pen(D, Gam)))


def best_drop(q, starts=None):
    S = sets(q)
    pt, _ = DB.best_q(q, 'all')
    P = S[2]
    cands = []
    qs = [np.array(pt)] + ([np.array(s) for s in starts] if starts else [])
    for qq in qs:
        for p in P.exterior.coords if P.geom_type == 'Polygon' else []:
            p = np.array(p)
            if np.hypot(*(p - qq)) < 0.8:
                cands.append(np.r_[qq, 0.98 * p + 0.02 * np.array(P.centroid.coords[0])])
    if not cands:
        return None, -9.0
    vals = sorted(((t_drop_at(S, z), i) for i, z in enumerate(cands)), reverse=True)[:6]
    best = (cands[vals[0][1]], vals[0][0])
    for _, i in vals:
        r = minimize(lambda z: -t_drop_at(S, z), cands[i], method='Nelder-Mead',
                     options=dict(maxfev=1500, xatol=1e-10, fatol=1e-12))
        if -r.fun > best[1]:
            best = (r.x, float(-r.fun))
    return [float(v) for v in best[0]], best[1]


def one(hu, hv, thd, xl, phd, square=True):
    q = config(hu, hv, math.radians(thd), xl, math.radians(phd))
    cons = R.constraints(q)
    pt, td = DB.best_q(q, 'all')
    zd, tdr = best_drop(q)
    row = dict(q=[float(v) for v in q], H1H3_min=float(cons.min()), H1H3_argmin=int(np.argmin(cons)),
               t_disc=td, centre=list(pt), t_drop=tdr, drop_qp=zd)
    if square:
        Qp, tq = LF.best_Q(q)
        row.update(t_sq=tq, Q=list(Qp))
    return row


def scan():
    rows = []
    for thd, hu in [(8, 0.85), (5.9, 0.88), (4, 0.9), (2, 0.9), (1, 0.95)]:
        th = math.radians(thd)
        c, s, hv = math.cos(th), math.sin(th), 0.995
        lo, hi = hv + c + (1 - hu) * math.tan(th), hv + c + s
        for f in (0.5, 0.8, 0.9, 0.97):
            r = one(hu, hv, thd, lo + f * (hi - lo), 0.01)
            rows.append(r)
            print('th %4.1f hu %.2f xl %.4f H1H3 %+.1e  disc %+.5f  drop %+.5f  sq %+.5f' % (
                thd, hu, r['q'][3], r['H1H3_min'], r['t_disc'], r['t_drop'], r['t_sq']), flush=True)
    json.dump(dict(rows=rows), open(os.path.join(RES, 'probe273_scan.json'), 'w'), indent=1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'one':
        print(json.dumps(one(*map(float, sys.argv[2:7])), indent=1))
    else:
        scan()
