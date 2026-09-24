"""A276 numeric cross-check of Theorem CORNER (parts 4-6): th, phi in (0, 5 deg].
(a) adversarial: random corner configurations (h_u, h_v, th, phi, D) satisfying the dip window (D > 0, X ∩ int C = ∅,
    X meets int T_u, exact shapely checks) and Nelder-Mead over unit squares Q maximising area(Q ∩ T_u) under the
    hard constraints int Q ∩ int C = ∅ = int Q ∩ int X, Q in the quadrant: must stay 0.
(b) the A1 inequality of part 6.2 on a 501 x 501 grid of (th, phi) in [0, 5 deg]^2:
    (cos phi + sin phi - 1) + 1/2 + sqrt(1/4 - (0.032 tan th + sin phi)^2) - cos th >= 0, and its minimum.
(c) the dead flat Q at phi > 0: T_x - w_phi - 1 < 0 on the corner (first order).
    python check276b.py [n_configs] [n_Q]"""
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
    for _ in range(1000):
        th = math.radians(rng.uniform(0.02, 5.0))
        ph = math.radians(rng.uniform(0.02, 5.0))
        c, s = math.cos(th), math.sin(th)
        hu = rng.uniform(0.3, 0.999)
        hv = rng.uniform(0.6, 0.999)
        Ctop = hv + c + s
        D = rng.uniform(1e-4, 0.2)
        Xlow = Ctop - D
        C = sq((hu + s, hv), th)
        Tu = C - np.array([hu, 0.0])
        X = sq((math.sin(ph), Xlow), ph)
        PC, PT, PX = Polygon(C), Polygon(Tu), Polygon(X)
        if PX.intersection(PC).area > 0 or PX.intersection(PT).area <= 1e-12:
            continue
        return dict(hu=hu, hv=hv, th=th, ph=ph, Ctop=Ctop, D=D, PC=PC, PT=PT, PX=PX)
    raise RuntimeError('no feasible config')


def penalty(cf, z):
    vx, vy, om = z
    Q = sq((vx, vy), om % (math.pi / 2))
    P = Polygon(Q)
    pen = P.intersection(cf['PC']).area + P.intersection(cf['PX']).area
    pen += max(0.0, -Q[:, 0].min()) + max(0.0, -Q[:, 1].min())
    gain = P.intersection(cf['PT']).area
    return gain - 50.0 * pen, gain, pen


def main():
    n_cfg = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    n_Q = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = random.Random(2760)
    worst = -1.0
    for k in range(n_cfg):
        cf = config(rng)
        for j in range(n_Q):
            z0 = np.array([rng.uniform(0.5, 2.2), cf['Ctop'] - rng.uniform(-0.4, 0.4), rng.uniform(0, math.pi / 2)])
            r = minimize(lambda z: -penalty(cf, z)[0], z0, method='Nelder-Mead',
                         options=dict(maxfev=600, xatol=1e-9, fatol=1e-12))
            val, gain, pen = penalty(cf, r.x)
            if pen < 1e-9:
                worst = max(worst, gain)
    print(f"(a) max area(Q ∩ T_u) over feasible Q on {n_cfg} corner configs x {n_Q} starts: {worst:.3e}  (must be 0)")
    g = np.linspace(0.0, math.radians(5.0), 501)
    TH, PH = np.meshgrid(g, g, indexing='ij')
    f = (np.cos(PH) + np.sin(PH) - 1) + 0.5 + np.sqrt(0.25 - (0.032 * np.tan(TH) + np.sin(PH)) ** 2) - np.cos(TH)
    i = np.unravel_index(np.argmin(f), f.shape)
    print(f"(b) A1 inequality min over [0,5]^2 deg: {f.min():.3e} at th={math.degrees(g[i[0]]):.2f}, phi={math.degrees(g[i[1]]):.2f} (must be >= 0); "
          f"at (5,5): {f[-1, -1]:.4f}, (5,0): {f[-1, 0]:.4f}, (0.5,5): {f[50, -1]:.4f}")
    # (c) flat Q dead for phi > 0: T_x - w_phi - 1 = h_u + c - cos phi - sin phi - 1 < 0 for h_u < 1
    hmax = 1.0 + np.cos(PH) + np.sin(PH) - np.cos(TH) - 1.0    # h_u needed for T_x - w_phi >= 1
    print(f"(c) h_u needed for a flat Q at phi > 0: min over the corner (phi > 0) = {hmax[:, 1:].min():.5f} > 1 -> dead")


if __name__ == '__main__':
    main()
