"""A276 numeric cross-check of Theorem FLAT-X (parts 2-3), phi = 0, th <= 30 deg.
For random (h_u, h_v, th, D) in the dip window (1.1) and random unit squares Q (lowest vertex V, tilt om) that are
interior-disjoint from C and X and inside the quadrant, we check
  (a) area(Q ∩ T_u) == 0  (no strip point: S = T_u \\ C and Q misses int C),
  (b) Lemma A: if x_min >= 1 then min over the cap {y <= C_top} of x - r_Tu(y) >= 1 - c,
  (c) the near-miss: the flat Q with corner (1, C_top) is at distance (1 - c) c from T_u (1.4).
Adversarial: Nelder-Mead on a penalty maximising area(Q ∩ T_u) - penalties.  Prints worst cases.  Light (~1 min).
    python check276.py [n_configs] [n_Q]"""
import math
import random
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon

sys.dont_write_bytecode = True


def sq(v, om):
    c, s = math.cos(om), math.sin(om)
    e1, e2 = np.array([c, s]), np.array([-s, c])
    V = np.array(v)
    return np.array([V, V + e1, V + e1 + e2, V + e2])


def config(rng):
    th = math.radians(rng.uniform(0.05, 30.0))
    c, s = math.cos(th), math.sin(th)
    hu = rng.uniform(1 - c + 1e-3, 0.999)          # h_u + c > 1
    hv = rng.uniform(0.5, 0.999)
    Lh, Ctop = hv + c, hv + c + s
    Dmax = (hu + c - 1) * math.tan(th)
    D = Dmax * rng.uniform(1e-3, 0.999)
    Xlow = Ctop - D
    C = sq((hu + s, hv), th)
    Tu = C - np.array([hu, 0.0])
    X = np.array([[0, Xlow], [1, Xlow], [1, Xlow + 1], [0, Xlow + 1]], float)
    return dict(hu=hu, hv=hv, th=th, c=c, s=s, Lh=Lh, Ctop=Ctop, D=D, Xlow=Xlow, C=C, Tu=Tu, X=X,
                PC=Polygon(C), PT=Polygon(Tu), PX=Polygon(X))


def r_Tu(cf, y):
    return cf['c'] + (cf['Ctop'] - y) * math.tan(cf['th'])


def penalty(cf, z):
    vx, vy, om = z
    om = om % (math.pi / 2)
    Q = sq((vx, vy), om)
    P = Polygon(Q)
    pen = 0.0
    pen += P.intersection(cf['PC']).area
    pen += P.intersection(cf['PX']).area
    pen += max(0.0, -Q[:, 0].min()) + max(0.0, -Q[:, 1].min())
    gain = P.intersection(cf['PT']).area
    return gain - 50.0 * pen, gain, pen, Q, om


def main():
    n_cfg = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    n_Q = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    rng = random.Random(276)
    worst_gain, worst_A, worst_near = -1.0, 9.0, 9.0
    for k in range(n_cfg):
        cf = config(rng)
        c = cf['c']
        # (c) the near-miss distance
        d = Polygon(sq((1.0, cf['Ctop']), 0.0)).distance(cf['PT'])
        worst_near = min(worst_near, d - (1 - c) * c)
        for j in range(n_Q):
            z0 = np.array([rng.uniform(0.8, 2.2), cf['Ctop'] - rng.uniform(-0.3, 0.3), rng.uniform(0, math.pi / 2)])
            r = minimize(lambda z: -penalty(cf, z)[0], z0, method='Nelder-Mead',
                         options=dict(maxfev=600, xatol=1e-9, fatol=1e-12))
            val, gain, pen, Q, om = penalty(cf, r.x)
            if pen < 1e-9:
                worst_gain = max(worst_gain, gain)               # (a): must stay 0
                if Q[:, 0].min() >= 1 - 1e-12 and Q[:, 1].min() < cf['Ctop'] < Q[:, 1].mean():   # (b) Lemma A, q_y > C_top
                    P = Polygon(Q)
                    cap = P.intersection(Polygon([(-1, -1), (9, -1), (9, cf['Ctop']), (-1, cf['Ctop'])]))
                    if not cap.is_empty:
                        m = min(x - r_Tu(cf, y) for x, y in np.array(cap.exterior.coords))
                        worst_A = min(worst_A, m - (1 - c))
    print(f"(a) max area(Q ∩ T_u) over feasible Q: {worst_gain:.3e}  (must be 0)")
    print(f"(b) Lemma A: min over feasible Q with x_min >= 1 of [min_cap (x - r_Tu) - (1 - c)]: {worst_A:.3e}  (must be >= 0)")
    print(f"(c) near-miss: min of dist((1,C_top)-square, T_u) - (1 - c) c: {worst_near:.3e}  (must be ~0)")


if __name__ == '__main__':
    main()
