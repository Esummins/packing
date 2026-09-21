"""A259 probe [M]: GAP dips over the PAIR domain at s (corner BR; obstacles = floor row + right row + container).
  G1: min height of the lowest vertex P_L of a free square with P_L.x >= T2.x = s - e0 - sin(phi0)   (floor row's END gap)
  G2: min right-wall depth of the rightmost vertex P_R with P_R.y <= I1.y = delta1 + cos(phi1)        (right row's START gap)
Needed by the proof: both >= (s-2)/2 (+ slack).  usage: gapscan259.py seed budget [s]"""
import json, math, os, sys, time
import numpy as np
from shapely.geometry import box as sbox
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import geom259 as Z, pair259 as P, room259 as R

def gap_dips(e0, f0, d1, f1, s, step=3.0, Vs=None, half=0.5):
    Vs = P.pair_verts(e0, f0, d1, f1, s) if Vs is None else Vs
    T2x, I1y = s - e0 - math.sin(f0), d1 + math.cos(f1)
    g1, g2, p1, p2 = 9.0, 9.0, None, None
    for pd in np.arange(0.0, 90.0 - 1e-9, step):
        psi = pd * Z.DEG; C_, S_ = math.cos(psi), math.sin(psi); h = (C_ + S_) / 2
        C = R.centre_set(Vs, s, psi, half)
        if C.is_empty: continue
        A = C.intersection(sbox(T2x + (C_ - S_) / 2, -1, s + 1, s + 1))
        for Pg in R.polys_of(A):
            X = np.array(Pg.exterior.coords); i = int(X[:, 1].argmin())
            if X[i, 1] - h < g1: g1, p1 = float(X[i, 1] - h), (float(X[i, 0]), float(X[i, 1]), psi)
        B = C.intersection(sbox(-1, -1, s + 1, I1y - (S_ - C_) / 2))
        for Pg in R.polys_of(B):
            X = np.array(Pg.exterior.coords); i = int(X[:, 0].argmax())
            if s - X[i, 0] - h < g2: g2, p2 = float(s - X[i, 0] - h), (float(X[i, 0]), float(X[i, 1]), psi)
    return g1, p1, g2, p2

if __name__ == '__main__':
    seed, budget = int(sys.argv[1]), float(sys.argv[2]); s = float(sys.argv[3]) if len(sys.argv) > 3 else Z.SHAT
    rng = np.random.default_rng(seed); t0 = time.time(); rows = []
    while time.time() - t0 < budget:
        f0, f1 = rng.uniform(0.2, 45, 2) * Z.DEG
        e0, d1 = rng.uniform(max(0, 2.82 - Z.span(f0)), 1), rng.uniform(max(0, 2.82 - Z.span(f1)), 1)
        if s - e0 - Z.span(f0) < 0 or s - d1 - Z.span(f1) < 0 or P.pair_feas(e0, f0, d1, f1, s) < 0: continue
        g1, p1, g2, p2 = gap_dips(e0, f0, d1, f1, s)
        rows.append({'e0': e0, 'phi0': f0 / Z.DEG, 'd1': d1, 'phi1': f1 / Z.DEG, 'g1': g1, 'p1': p1, 'g2': g2, 'p2': p2, 's': s})
    with open(os.path.join(HERE, '..', 'results', 'gapscan259.jsonl'), 'a') as fh:
        for r in rows: fh.write(json.dumps(r) + '\n')
    print(len(rows), 'need', (s - 2) / 2)
    for key in ('g1', 'g2'):
        rows.sort(key=lambda r: r[key]); print('min', key)
        for r in rows[:5]: print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k[0] != 'p' or k.startswith('phi')}, [round(t, 3) for t in r['p' + key[1]]])
