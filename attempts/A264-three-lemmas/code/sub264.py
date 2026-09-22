"""A264 Lemma 1 [M]: which OBSTACLES the two BL sectors of a JAM ring really need.

For every JAM ring of A262 (ring262.jsonl + search262.jsonl, t > 0) recompute the BL-floor and BL-left sector
margins of sector262 (exact centre sets, 1-degree tilt grid; -9 = no free square in the sector) with the sector's
obstacle set restricted to subsets of {A, A2, X, C}, and with the container reduced to the two walls of the corner
(the opposite walls dropped, which the corner-frame reduction of A259 s.2.3 allows).  A subset whose margin stays
< 0 on every ring is a candidate for a cheaper certificate; the comparison of three_lemmas.md s.1 says which.
    python sub264.py  -> results/sub264.json
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A262 = os.path.join(ROOT, 'attempts', 'A262-no-jam')
for p in ('attempts/A262-no-jam/code', 'attempts/A259-normal-room/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom262 as G                                                   # noqa: E402
import room259 as R                                                   # noqa: E402

DEG = math.pi / 180
SUBSETS = {'AA2XC': (0, 1, 6, 7), 'AA2C': (0, 1, 7), 'AC': (0, 7), 'C': (7,), 'ACX': (0, 6, 7), 'CX': (6, 7),
           'AA2X': (0, 1, 6), 'X': (6,), 'AXC_A2': (0, 1, 6, 7)}


def sector_margins(Vs, s, step=1.0):
    """BL-floor (n = -v, q_x <= s/2) and BL-left (n = -u, q_y <= s/2) margins against the member arrays Vs."""
    O = np.array([s / 2, s / 2])
    big = s + 1
    halves = dict(L=sbox(-1, -1, s / 2, big), D=sbox(-1, -1, big, s / 2))
    out = {'BL-floor': -9.0, 'BL-left': -9.0}
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * DEG
        C = R.centre_set(Vs, s, psi)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for key, n, h in (('BL-floor', -v, 'L'), ('BL-left', -u, 'D')):
            for Pg in R.polys_of(C.intersection(halves[h])):
                A = np.array(Pg.exterior.coords)[:-1] - O
                out[key] = max(out[key], float((A @ n).max()) - 0.5)
    return out


def ring_facts(V, s):
    """C's wall distances, extents and vertex reach; A's offset / tilt; X's lowest point."""
    Cv, Av, Xv = V[7], V[0], V[6]
    return dict(h_u=float(Cv[:, 0].min()), h_v=float(Cv[:, 1].min()), C_right=float(Cv[:, 0].max()),
                C_top=float(Cv[:, 1].max()), C_far=float(np.hypot(Cv[:, 0], Cv[:, 1]).max()),
                A_x0=float(Av[:, 0].min()), A_depth=float(Av[:, 1].max()), X_low=float(Xv[:, 1].min()),
                X_right=float(Xv[:, 0].max()), half=s / 2)


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
        rec = dict(id=r['id'], s=r['s'], facts=ring_facts(V, r['s']), sectors={})
        for name, idx in SUBSETS.items():
            Vs = [V[i] for i in idx]
            rec['sectors'][name] = sector_margins(Vs, r['s'])
            for k, val in rec['sectors'][name].items():
                worst[name + '|' + k] = max(worst.get(name + '|' + k, -9.0), val)
        per.append(rec)
        print(r['id'][:50], {k: round(v, 3) for k, v in rec['sectors']['AA2XC'].items()},
              {k: round(v, 3) for k, v in rec['sectors']['AC'].items()}, flush=True)
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    json.dump(dict(n=len(per), worst=worst, rows=per), open(os.path.join(HERE, '..', 'results', 'sub264.json'), 'w'),
              indent=1)
    print(len(per), json.dumps(worst, indent=1))


if __name__ == '__main__':
    main()
