"""A277: can a floor toucher Y (missing the box) block D's floor drop in the float262 witness geometry?  Y's left vertex
is placed just under D's right vertex R_D = (R_x, R_y), tilt alpha with cos alpha = R_y - e2, left vertex x = R_x - e1;
exact shapely check of every term (gaps to C, D, X; Y misses int D; Y meets int T_v(D); Y in the container; Y misses
the open box; Y touches the floor by construction).  Grid over (e1, e2); prints the best min-margin.  Runs < 5 s.
    python ypoke277.py -> results/ypoke277.json"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import local261 as L                                                   # noqa: E402

W = json.load(open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'float262.json')))['poses']
V = {k: L.verts(*W[k]) for k in ('C', 'D', 'X')}
S = 3.877083590022814
P = lambda A: Polygon([tuple(p) for p in A])
D = V['D']
iR = int(np.argmax(D[:, 0]))
Rx, Ry = float(D[iR, 0]), float(D[iR, 1])
hv = float(D[:, 1].min())
TvD = D - np.array([0.0, hv])


def Y_of(e1, e2):
    ca = Ry - e2
    al = math.acos(ca)
    sa = math.sin(al)
    y0 = Rx - e1 + sa
    return np.array([[y0, 0.0], [y0 + ca, sa], [y0 + ca - sa, sa + ca], [y0 - sa, ca]]), math.degrees(al)


def terms(Y):
    PY = P(Y)
    t = dict(gap_C=PY.distance(P(V['C'])), gap_X=PY.distance(P(V['X'])), gap_D=PY.distance(P(D)),
             overlap_D=PY.intersection(P(D)).area, depth_TvD=PY.intersection(P(TvD)).area,
             contain=S - float(Y[:, 0].max()), miss_box=float(Y[:, 0].min()) - 1.0)
    return t


best, brow = -1.0, None
rows = []
for e1 in np.linspace(0.0002, 0.004, 20):
    for e2 in np.linspace(0.0002, 0.006, 30):
        Y, al = Y_of(e1, e2)
        t = terms(Y)
        ok = t['overlap_D'] <= 1e-15 and t['depth_TvD'] > 0
        m = min(t['gap_C'], t['gap_X'], t['gap_D'], t['contain'], t['miss_box'], math.sqrt(t['depth_TvD'])) if ok else -1.0
        if m > best:
            best, brow = m, dict(e1=e1, e2=e2, alpha_deg=al, terms=t, Y=Y.tolist())
out = dict(R_D=[Rx, Ry], h_v_D=hv, best_min_margin=best, best=brow,
           note='depth_TvD is an AREA; the min uses its square root as a length scale')
os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, '..', 'results', 'ypoke277.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
