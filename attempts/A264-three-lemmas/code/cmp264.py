"""A264 Lemma 1, candidate (i) tested [M]: replace the floater C by its WALL DROP cell T_u = C - h_u e_x (a fictitious
wall toucher with C's tilt and C's far flank moved to the wall by h_u) and by its FLOOR DROP T_v = C - h_v e_y, and
recompute the BL sector margins on every JAM ring; also the strip test: does any free square of the true pocket
meet T_u \ C (the strip between the wall and C's left flank)?  Soundness of the comparison needs T_u \ C to be
unreachable for free squares of the sector -- the strip test measures exactly that.
    python cmp264.py -> results/cmp264.json
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A262 = os.path.join(ROOT, 'attempts', 'A262-no-jam')
for p in ('attempts/A262-no-jam/code', 'attempts/A259-normal-room/code', 'attempts/A264-three-lemmas/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom262 as G                                                   # noqa: E402
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
from sub264 import sector_margins, DEG                                # noqa: E402


def strip_hit(Vs_true, Tu, Cv, s, step=1.0):
    """max over free squares Q of the true pocket (BL sectors only) of the area of Q meeting T_u \\ C; 0 = none."""
    O = np.array([s / 2, s / 2])
    strip = Polygon(Tu).difference(Polygon(Cv))
    big = s + 1
    halves = dict(L=sbox(-1, -1, s / 2, big), D=sbox(-1, -1, big, s / 2))
    worst = 0.0
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * DEG
        C = R.centre_set(Vs_true, s, psi)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for n, h in ((-v, 'L'), (-u, 'D')):
            for Pg in R.polys_of(C.intersection(halves[h])):
                A = np.array(Pg.exterior.coords)[:-1]
                for q in A:
                    if float((q - O) @ n) - 0.5 < -0.4:        # only squares within 0.4 of the sector's test
                        continue
                    Q = Polygon(Z.sq_verts(q[0], q[1], psi))
                    worst = max(worst, Q.intersection(strip).area)
    return worst


def main():
    rows = []
    for f in ('ring262.jsonl', 'search262.jsonl'):
        path = os.path.join(A262, 'results', f)
        if os.path.exists(path):
            rows += [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r.get('t', -1) > 1e-6 and 'p' in r]
    per, worst = [], {}
    for r in rows:
        V = G.verts(np.array(r['p']), r['s'])
        Cv = V[7]
        hu, hv = float(Cv[:, 0].min()), float(Cv[:, 1].min())
        Tu = Cv - np.array([hu, 0.0])
        Tv = Cv - np.array([0.0, hv])
        rec = dict(id=r['id'], s=r['s'], h_u=hu, h_v=hv,
                   true=sector_margins([V[0], V[1], V[6], V[7]], r['s']),
                   Tu=sector_margins([V[0], V[1], V[6], Tu], r['s']),
                   Tv=sector_margins([V[0], V[1], V[6], Tv], r['s']),
                   strip=strip_hit([V[0], V[1], V[6], V[7]], Tu, Cv, r['s']))
        for k in ('true', 'Tu', 'Tv'):
            for kk, val in rec[k].items():
                worst[k + '|' + kk] = max(worst.get(k + '|' + kk, -9.0), val)
        worst['strip'] = max(worst.get('strip', 0.0), rec['strip'])
        per.append(rec)
        print(r['id'][:40], round(r['s'], 3), 'true', {k: round(v, 3) for k, v in rec['true'].items()},
              'Tu', {k: round(v, 3) for k, v in rec['Tu'].items()}, 'strip', round(rec['strip'], 5), flush=True)
    json.dump(dict(n=len(per), worst=worst, rows=per), open(os.path.join(HERE, '..', 'results', 'cmp264.json'), 'w'),
              indent=1)
    print(len(per), json.dumps(worst, indent=1))


if __name__ == '__main__':
    main()
