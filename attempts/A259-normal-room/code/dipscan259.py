"""A259 probe: over the PAIR domain at s_max, the lowest point of any free square with q_x >= s/2 (DIP_floor) and the
least right-wall depth of any free square with q_y <= s/2 (DIP_right); 4 obstacles + container.  [M]"""
import json, math, os, sys, time
import numpy as np
from shapely.geometry import box as sbox
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, pair259 as P, room259 as R
seed = int(sys.argv[1]); budget = float(sys.argv[2]); s = Z.SHAT
rng = np.random.default_rng(seed); t0 = time.time(); rows = []
right = sbox(s / 2, -1, s + 1, s + 1); lower = sbox(-1, -1, s + 1, s / 2)
while time.time() - t0 < budget:
    f0, f1 = rng.uniform(0.2, 45, 2) * Z.DEG
    e0, d1 = rng.uniform(max(0, 2.82 - Z.span(f0)), 1), rng.uniform(max(0, 2.82 - Z.span(f1)), 1)
    if s - e0 - Z.span(f0) < 0 or s - d1 - Z.span(f1) < 0 or P.pair_feas(e0, f0, d1, f1, s) < 0: continue
    Vs = P.pair_verts(e0, f0, d1, f1, s); dipf, dipr = 9, 9
    for pd in range(0, 90, 3):
        psi = pd * Z.DEG; h = (math.cos(psi) + math.sin(psi)) / 2
        C = R.centre_set(Vs, s, psi)
        for G, ax in ((C.intersection(right), 1), (C.intersection(lower), 0)):
            for Pg in R.polys_of(G):
                A = np.array(Pg.exterior.coords)
                if ax == 1: dipf = min(dipf, A[:, 1].min() - h)
                else: dipr = min(dipr, s - A[:, 0].max() - h)
    rows.append((dipf, dipr, e0, f0 / Z.DEG, d1, f1 / Z.DEG))
rows.sort(); print(len(rows)); print('lowest floor dips'); [print([round(v, 3) for v in r]) for r in rows[:6]]
rows.sort(key=lambda r: r[1]); print('least right depths'); [print([round(v, 3) for v in r]) for r in rows[:6]]
