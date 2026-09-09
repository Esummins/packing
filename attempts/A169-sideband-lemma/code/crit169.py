"""A169 Theorem B criterion (exact characterisation of NON-lonely poses) vs the numeric raster.
Q1 = (x1, y1, theta); box (0,c)^2.  Support h(n) = n.centre + (|n.e| + |n.e_perp|)/2.
(NE): exists alpha in [0,90]: h(cos a, sin a) < c (cos a + sin a)
(W) : exists zeta in (0,90): h(-sin z, cos z) < c cos z - sin^2 z
(S) : exists zeta in (0,90): h(cos z, -sin z) < c cos z - sin^2 z
Each satisfied condition is turned into an explicit Q2 and CERTIFIED by SAT (found => certificate)."""
import math, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import *
R2 = math.sqrt(2)

def support(x1, y1, th, n):
    e = (math.cos(th), math.sin(th)); ep = (-e[1], e[0])
    return n[0] * x1 + n[1] * y1 + 0.5 * (abs(n[0] * e[0] + n[1] * e[1]) + abs(n[0] * ep[0] + n[1] * ep[1]))

def certify(Q1, c, pose):
    P = verts(*pose)
    return in_quadrant(P) and meets_open_box(P, c) and sat_gap(P, Q1) >= 0

def criterion(x1, y1, th, c, steps=1800):
    """returns (nonlonely?, best (cond, angle, margin), certified Q2 pose or None)"""
    Q1 = verts(x1, y1, th); best = (None, None, -9); cert = None
    for k in range(steps + 1):
        a = (k / steps) * (math.pi / 2)
        ca, sa = math.cos(a), math.sin(a)
        # (NE)
        m = c * (ca + sa) - support(x1, y1, th, (ca, sa))
        if m > best[2]: best = ('NE', a, m)
        if m > 0 and cert is None:
            eps = min(m / 2, 0.01)
            v = (c - eps * ca, c - eps * sa)
            pose = (v[0] + ca / R2, v[1] + sa / R2, (a - math.pi / 4) % (math.pi / 2))
            if certify(Q1, c, pose): cert = ('NE', a, pose)
        if 0 < k < steps:
            z = a; cz, sz = ca, sa; g = 0.5 * (sz + cz)
            for cond, n in (('W', (-sz, cz)), ('S', (cz, -sz))):
                m = c * cz - sz * sz - support(x1, y1, th, n)
                if m > best[2]: best = (cond, z, m)
                if m > 0 and cert is None:
                    eps = min(m / (2 * cz), 0.01); yv = c - eps
                    pose = (g, yv + g, z) if cond == 'W' else (yv + g, g, math.pi / 2 - z)
                    if certify(Q1, c, pose): cert = (cond, z, pose)
    return cert is not None, best, cert

if __name__ == '__main__':
    lon = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'results', 'lonely.json')))
    rep = {}
    for deg, rec in lon.items():
        th = math.radians(float(deg)); lonely = {(a, b) for a, b, _ in rec['lonely_cells']}
        n = int(1.9 / 0.08); agree = 0; crit_only = 0; num_only = 0; details = []
        for i in range(n):
            for j in range(n):
                cx, cy = round(0.5 + i * 0.08, 4), round(0.5 + j * 0.08, 4)
                Q1 = verts(cx, cy, th)
                if not in_quadrant(Q1) or not meets_open_box(Q1, 1.0): continue
                ok, best, cert = criterion(cx, cy, th, 1.0)
                num = (cx, cy) not in lonely
                if ok == num: agree += 1
                elif ok: crit_only += 1; details.append(('crit_only', cx, cy, cert))
                else: num_only += 1; details.append(('num_only', cx, cy, best))
        rep[deg] = dict(agree=agree, crit_only_certified=crit_only, num_only=num_only, details=details[:20])
        print(deg, rep[deg]['agree'], 'crit-only(certified Q2)', crit_only, 'num-only', num_only, flush=True)
    json.dump(rep, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'crit_vs_raster.json'), 'w'), indent=1)
