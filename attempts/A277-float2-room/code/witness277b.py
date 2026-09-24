"""A277: the FLOAT2 corner with ALL FOUR DROPS BLOCKED -- C, D, X of float262.json + Y from ypoke277 (a floor toucher,
tilt 77.2 deg, left vertex under D's right vertex).  Exact terms (shapely / local261 SAT): pairwise gaps, box depths,
float distances, every drop's blockers (interior overlap areas), containment at s = shat, X / Y miss the open box,
box roles (Y serves BR iff x_max > s - 1; X serves TL iff y_max > s - 1), and A261's any-pose P1 test J (JAM_COARSE grid:
J_F = sup over wall cells T of min(gap(T, others), depth(T, F)); J < 0 <=> no wall cell meeting F is free of the rest).
    python witness277b.py -> results/float277_witness.json"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'code'))
import local261 as L                                                   # noqa: E402
import jam261 as J                                                     # noqa: E402

S = 3.877083590022814
W = json.load(open(os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'float262.json')))['poses']
Y = np.array(json.load(open(os.path.join(HERE, '..', 'results', 'ypoke277.json')))['best']['Y'])
V = {k: L.verts(*W[k]) for k in ('C', 'D', 'X')}
V['Y'] = Y
P = lambda A: Polygon([tuple(p) for p in A])
BOX = sbox(0, 0, 1, 1)
names = ['C', 'D', 'X', 'Y']
out = dict(side=S, poses={k: [W[k][0], W[k][1], math.degrees(W[k][2])] for k in W if k != 'A'}, Y_vertices=Y.tolist())
out['gaps'] = {a + '-' + b: float(P(V[a]).distance(P(V[b]))) for i, a in enumerate(names) for b in names[:i]}
out['box_area'] = {k: float(P(V[k]).intersection(BOX).area) for k in names}
out['contain'] = {k: [float(V[k][:, 0].min()), float(V[k][:, 1].min()), S - float(V[k][:, 0].max()), S - float(V[k][:, 1].max())] for k in names}
out['roles'] = dict(X_serves_TL=float(V['X'][:, 1].max()) > S - 1, Y_serves_BR=float(V['Y'][:, 0].max()) > S - 1,
                    X_ymax=float(V['X'][:, 1].max()), Y_xmax=float(V['Y'][:, 0].max()))
drops = {}
for f in ('C', 'D'):
    A = V[f]
    hu, hv = float(A[:, 0].min()), float(A[:, 1].min())
    for lab, T in (('u', A - [hu, 0.0]), ('v', A - [0.0, hv])):
        drops[f + lab] = {k: float(P(T).intersection(P(V[k])).area) for k in names if k != f and P(T).intersection(P(V[k])).area > 1e-15}
out['drop_blockers_area'] = drops
out['h'] = {f: [float(V[f][:, 0].min()), float(V[f][:, 1].min())] for f in ('C', 'D')}
jC = np.minimum.reduce([J.gaps(V['D']), J.gaps(V['X']), J.gaps(V['Y']), -J.gaps(V['C'])]).max()
jD = np.minimum.reduce([J.gaps(V['C']), J.gaps(V['X']), J.gaps(V['Y']), -J.gaps(V['D'])]).max()
out['P1_any_pose_J'] = dict(J_C=float(jC), J_D=float(jD), grid_cells=int(len(J.CELLS)), note='J < 0 <=> jammed in A261 sense')
out['all_four_drops_blocked'] = all(len(v) > 0 for v in drops.values())
out['min_gap'] = min(out['gaps'].values())
json.dump(out, open(os.path.join(HERE, '..', 'results', 'float277_witness.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
