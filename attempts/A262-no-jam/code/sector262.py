"""A262 [M]: the eight SECTOR margins of MISS => corner PAIR (normal_room.md s.2.2) on every JAM ring found.

A free square Q (tilt psi in [-45, 45), u = (cos, sin), v = u-perp) with O not in int Q has (q - O).n >= 1/2 for a normal
n in {-v (floor), u (right), v (ceiling), -u (left)}; split by the half of the container q lies in: eight sectors, two per
corner.  Sector margin = max over free Q of (q - O).n - 1/2 (exact centre sets, 1-degree tilt grid; -9 = no free Q).
JAM corner = BL: sectors 'BL-floor' (n = -v, q_x <= s/2) and 'BL-left' (n = -u, q_y <= s/2) see A, A2, X, C;
'TL-left', 'TL-ceil' see the ceiling row, X and C;  the BR / TR sectors see only complete rows (A259's PAIR).
    python sector262.py   -> results/sector262.json
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import box as sbox

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = G.Z


def sectors(Vs, s, step=1.0):
    O = np.array([s / 2, s / 2])
    big = s + 1
    half = dict(L=sbox(-1, -1, s / 2, big), Rr=sbox(s / 2, -1, big, big), D=sbox(-1, -1, big, s / 2), U=sbox(-1, s / 2, big, big))
    out = {k: -9.0 for k in ('BL-floor', 'BR-floor', 'BR-right', 'TR-right', 'TR-ceil', 'TL-ceil', 'TL-left', 'BL-left')}
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * Z.DEG
        C = R.centre_set(Vs, s, psi)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        for key, n, h in (('BL-floor', -v, 'L'), ('BR-floor', -v, 'Rr'), ('BR-right', u, 'D'), ('TR-right', u, 'U'),
                          ('TR-ceil', v, 'Rr'), ('TL-ceil', v, 'L'), ('TL-left', -u, 'U'), ('BL-left', -u, 'D')):
            for Pg in R.polys_of(C.intersection(half[h])):
                A = np.array(Pg.exterior.coords)[:-1] - O
                out[key] = max(out[key], float((A @ n).max()) - 0.5)
    return out


def main():
    rows = []
    for f in ('ring262.jsonl', 'search262.jsonl'):
        path = os.path.join(ATT, 'results', f)
        if os.path.exists(path):
            rows += [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r['t'] > 1e-6]
    worst, per = {}, []
    for r in rows:
        sec = sectors(G.verts(np.array(r['p']), r['s']), r['s'])
        per.append(dict(id=r['id'], s=r['s'], sectors=sec))
        for k, v in sec.items():
            worst[k] = max(worst.get(k, -9.0), v)
    json.dump(dict(n=len(per), worst=worst, rows=per), open(os.path.join(ATT, 'results', 'sector262.json'), 'w'), indent=1)
    print(len(per), json.dumps(worst, indent=1))


if __name__ == '__main__':
    main()
