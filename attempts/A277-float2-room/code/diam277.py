"""A277 [M]: the BL-sector admissible-centre region R of the dropped FLOAT2 witness and its DIAMETER (diam R < 1 =>
no two disjoint sector squares: CAP-2).  Obstacles from results/float277_witness.json (C, D, X, Y; C -> T_u(C), D ->
T_v(D)); exact per-tilt centre sets (room259.centre_set, imported), 1-degree grid on psi in [-45, 45) so that -v points at the floor and -u at the wall (A259 s.2.2), side shat; sectors BL-floor
{(q-O).(-v) >= 1/2, q_x <= s/2} and BL-left {(q-O).(-u) >= 1/2, q_y <= s/2}.  For several obstacle subsets: area of R,
diameter of its convex hull, worst miss margin, and the two farthest centres.  Runs ~ 1 min.
    python diam277.py -> results/diam277.json"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A259-normal-room', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import room259 as R                                                    # noqa: E402
import local261 as L                                                   # noqa: E402

S = 3.877083590022814
WIT = json.load(open(os.path.join(HERE, '..', 'results', 'float277_witness.json')))
V = {k: L.verts(v[0], v[1], math.radians(v[2])) for k, v in WIT['poses'].items()}
V['Y'] = np.array(WIT['Y_vertices'])
V['TuC'] = V['C'] - [float(V['C'][:, 0].min()), 0.0]
V['TvD'] = V['D'] - [0.0, float(V['D'][:, 1].min())]
SUBSETS = {'C D X Y': ('C', 'D', 'X', 'Y'), 'TuC TvD': ('TuC', 'TvD'), 'TuC TvD X': ('TuC', 'TvD', 'X'),
           'TuC TvD Y': ('TuC', 'TvD', 'Y'), 'TuC TvD X Y': ('TuC', 'TvD', 'X', 'Y'), 'C D': ('C', 'D')}


def region(Vs, s=S, step=1.0):
    O = np.array([s / 2, s / 2])
    parts, worst = [], -9.0
    for pd in np.arange(-45.0, 45.0, step):
        psi = math.radians(pd)
        C = R.centre_set(Vs, s, psi)
        if C.is_empty:
            continue
        u = np.array([math.cos(psi), math.sin(psi)])
        v = np.array([-math.sin(psi), math.cos(psi)])
        big = 3 * s
        for n, half in ((-v, sbox(-big, -big, s / 2, big)), (-u, sbox(-big, -big, big, s / 2))):
            # half-plane (q - O).n >= 1/2 as a big polygon
            p0 = O + 0.5 * n
            t = np.array([-n[1], n[0]])
            hp = Polygon([p0 + big * t, p0 + big * t + big * n, p0 - big * t + big * n, p0 - big * t])
            g = C.intersection(half).intersection(hp)
            for Pg in R.polys_of(g):
                parts.append(Pg)
                A = np.array(Pg.exterior.coords)[:-1] - O
                worst = max(worst, float((A @ n).max()) - 0.5)
    if not parts:
        return dict(area=0.0, diam=0.0, worst_miss=worst, farthest=None)
    U = unary_union(parts)
    H = U.convex_hull
    pts = np.array(H.exterior.coords)[:-1] if H.geom_type == 'Polygon' else np.array(H.coords)
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
    i, j = np.unravel_index(int(d.argmax()), d.shape)
    return dict(area=float(U.area), diam=float(d.max()), worst_miss=worst, farthest=[pts[i].tolist(), pts[j].tolist()])


out = {}
for name, keys in SUBSETS.items():
    out[name] = region([V[k] for k in keys])
    print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out[name].items()}, flush=True)
json.dump(out, open(os.path.join(HERE, '..', 'results', 'diam277.json'), 'w'), indent=1)
