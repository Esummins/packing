"""A277: exact geometry check of the FLOAT2 witness (attempts/A262-no-jam/results/float262.json; poses = centre + tilt,
local261.verts imported).  For each floater (C, D): its wall drop T_u and floor drop T_v, which of the other squares
meets each drop's interior (area > 1e-12), whether each drop meets the open box, and BLOCKER-SIDE data.  Then the
pair (T_u(C), T_v(D)) and the alternative (C, T_v(D)) / (T_u(C), D): pairwise interior-disjoint?  Runs < 1 s.
    python witness277.py  -> results/witness277.json (+ stdout)"""
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
V = {k: L.verts(*W[k]) for k in W}
BOX = sbox(0, 0, 1, 1)


def P(A):
    return Polygon([tuple(p) for p in A])


def area(A, B):
    return float(P(A).intersection(P(B)).area)


def drops(name):
    A = V[name]
    hu, hv = float(A[:, 0].min()), float(A[:, 1].min())
    return hu, hv, A - np.array([hu, 0.0]), A - np.array([0.0, hv])


out = {}
for k in V:
    A = V[k]
    out[k] = dict(pose_deg=[W[k][0], W[k][1], math.degrees(W[k][2])], xmin=float(A[:, 0].min()), ymin=float(A[:, 1].min()),
                  xmax=float(A[:, 0].max()), ymax=float(A[:, 1].max()), box_depth_area=float(P(A).intersection(BOX).area))
for f in ('C', 'D'):
    hu, hv, Tu, Tv = drops(f)
    out[f].update(h_u=hu, h_v=hv, Tu_meets_box=float(P(Tu).intersection(BOX).area), Tv_meets_box=float(P(Tv).intersection(BOX).area),
                  Tu_blockers={k: area(Tu, V[k]) for k in V if k != f and area(Tu, V[k]) > 1e-12},
                  Tv_blockers={k: area(Tv, V[k]) for k in V if k != f and area(Tv, V[k]) > 1e-12})
    out[f]['gaps'] = {k: float(P(A := V[f]).distance(P(V[k]))) for k in V if k != f}
_, _, TuC, _ = drops('C')
_, _, _, TvD = drops('D')
out['pairs'] = dict(TuC_TvD=area(TuC, TvD), TuC_D=area(TuC, V['D']), C_TvD=area(V['C'], TvD), TuC_X=area(TuC, V['X']),
                    TvD_A=area(TvD, V['A']), TuC_A=area(TuC, V['A']), TvD_X=area(TvD, V['X']),
                    TuC_offset_b=float(TuC[:, 1].min()), TvD_offset_a=float(TvD[:, 0].min()))
os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
json.dump(out, open(os.path.join(HERE, '..', 'results', 'witness277.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
