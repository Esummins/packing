"""A265 Lemma STRIP, tested exactly on A264's 323 JAM rings with obstacle SUBSETS (three_lemmas.md s.4.3):
for each ring and each subset S of {A, A2, X, C}, the STRIP-SECTOR margin
    max over psi, over centres q with Q free of S, Q meeting T_u \\ C with positive area, in the BL-floor sector
    (q_x <= s/2) resp. BL-left sector (q_y <= s/2), of (q - O).(-v) - 1/2 resp. (q - O).(-u) - 1/2.
< 0 (or -9 = no such square) on every ring  <=>  STRIP holds against S alone.  Exact centre sets (room259), 1 deg
grid.  Q free of C meets T_u \\ C with positive area  <=>  q in int(T_u (+) Q0); without C the strip is triangulated.
Also records the strip's shape: h_u, h_v, C's tilt, X's lowest point and X's intrusion into T_u (the jam depth).
    python strip265.py [--step 1] -> results/strip265.json"""
import argparse
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import triangulate, unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A262 = os.path.join(ROOT, 'attempts', 'A262-no-jam')
for p in ('attempts/A262-no-jam/code', 'attempts/A259-normal-room/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom262 as G                                                   # noqa: E402
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402

DEG = math.pi / 180
SUBSETS = {'AA2XC': (0, 1, 6, 7), 'AXC': (0, 6, 7), 'AC': (0, 7), 'AX': (0, 6), 'A': (0,), 'CX': (6, 7), 'C': (7,),
           'X': (6,), 'none': ()}


def mink(P, q0):
    return Polygon([(a[0] + b[0], a[1] + b[1]) for a in P for b in q0]).convex_hull


def strip_region(Tu, Cv, psi, with_C):
    """centres q whose square (tilt psi) meets T_u \\ C with positive area (given Q free of C when with_C)."""
    q0 = Z.sq_verts(0.0, 0.0, psi)
    if with_C:
        return mink(Tu, q0)
    S = Polygon(Tu).difference(Polygon(Cv))
    return unary_union([mink(np.array(t.exterior.coords)[:-1], q0) for t in triangulate(S) if t.within(S.buffer(1e-9))])


def strip_margins(V, Tu, idx, s, step):
    Vs = [V[i] for i in idx]
    with_C = 7 in idx
    O = np.array([s / 2, s / 2])
    big = s + 1
    halves = dict(L=sbox(-1, -1, s / 2, big), D=sbox(-1, -1, big, s / 2))
    out = {'BL-floor': -9.0, 'BL-left': -9.0}
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * DEG
        C = R.centre_set(Vs, s, psi)
        if C.is_empty:
            continue
        C = C.intersection(strip_region(Tu, V[7], psi, with_C).buffer(-1e-7))
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for key, n, h in (('BL-floor', -v, 'L'), ('BL-left', -u, 'D')):
            for Pg in R.polys_of(C.intersection(halves[h])):
                A = np.array(Pg.exterior.coords)[:-1] - O
                out[key] = max(out[key], float((A @ n).max()) - 0.5)
    return out


def facts(V, Tu, s):
    Cv, Av, Xv = V[7], V[0], V[6]
    jam = Polygon(Tu).intersection(Polygon(Xv))
    e = Cv[1] - Cv[0]
    return dict(h_u=float(Cv[:, 0].min()), h_v=float(Cv[:, 1].min()), th_C=float(math.degrees(math.atan2(e[1], e[0]))),
                C_top=float(Cv[:, 1].max()), X_low=float(Xv[:, 1].min()), X_jam_area=float(jam.area),
                X_jam_depth=float(Tu[:, 1].max() - Xv[:, 1].min()), A_x0=float(Av[:, 0].min()),
                A_top=float(Av[:, 1].max()), strip_area=float(Polygon(Tu).difference(Polygon(Cv)).area), half=s / 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', type=float, default=1.0)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    Z.belownormal()
    rows = []
    for f in ('ring262.jsonl', 'search262.jsonl'):
        path = os.path.join(A262, 'results', f)
        if os.path.exists(path):
            rows += [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r.get('t', -1) > 1e-6 and 'p' in r]
    if a.limit:
        rows = rows[:a.limit]
    per, worst = [], {}
    for r in rows:
        V = G.verts(np.array(r['p']), r['s'])
        Tu = V[7] - np.array([float(V[7][:, 0].min()), 0.0])
        rec = dict(id=r['id'], s=r['s'], facts=facts(V, Tu, r['s']), strip={})
        for name, idx in SUBSETS.items():
            rec['strip'][name] = strip_margins(V, Tu, idx, r['s'], a.step)
            for k, val in rec['strip'][name].items():
                worst[name + '|' + k] = max(worst.get(name + '|' + k, -9.0), val)
        per.append(rec)
        print(r['id'][:40], round(r['s'], 3), {k: (round(v['BL-floor'], 3), round(v['BL-left'], 3))
                                                for k, v in rec['strip'].items()}, flush=True)
    json.dump(dict(n=len(per), step=a.step, worst=worst, rows=per),
              open(os.path.join(HERE, '..', 'results', 'strip265.json'), 'w'), indent=1)
    print(len(per), json.dumps(worst, indent=1))


if __name__ == '__main__':
    main()
