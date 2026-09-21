"""A262 task 2/3 [M]: does a RING close around a JAM corner, and what is the room of its pocket?

Starts: A261's local witnesses (jam261_polished.json, jam261_a080.json) embedded by geom262.from_local at side s,
walls 1, 2 seeded on a grid of (delta, phi).  Objective (HARD terms only, no penalties):
    t = min( geom262.margin , -J )     maximised by Nelder-Mead from every structured start;  t > 0 <=> a JAM RING.
For every JAM ring found: the exact per-tilt centre sets of the pocket (room259, imported): pierce margin (< 0: every
free square contains O), number of components, and capacity259-style TWO disjoint free squares test.
    python ring262.py --s 3.877083590022814 [--grid 3]   -> results/ring262.jsonl   (resumable by start id; logs/STOP)
"""
import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
os.environ.setdefault('JAM_COARSE', '1')
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom262 as G                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = G.Z
OUT = os.path.join(ATT, 'results', 'ring262.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
A261 = os.path.join(G.ROOT, 'attempts', 'A261-box-meeters', 'results')


def witnesses():
    out = []
    for f in ('jam261_polished.json', 'jam261_a080.json'):
        w = json.load(open(os.path.join(A261, f)))['poses']
        out.append((f.split('.')[0], w['A'], w['C'], w['X']))
    return out


def objective(p, s):
    m = G.margin(p, s)
    if m < -0.05:
        return m
    return min(m, -G.jam_J(G.verts(p, s)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', type=float, default=G.SHAT)
    ap.add_argument('--grid', type=int, default=3)
    ap.add_argument('--iters', type=int, default=1500)
    a = ap.parse_args()
    Z.belownormal()
    s = a.s
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['id'] for l in open(OUT)}
    dl = np.linspace(0.55, 0.95, a.grid)
    fl = np.radians(np.linspace(6, 26, a.grid))
    for name, pA, pC, pX in witnesses():
        for d1, f1, d2, f2 in itertools.product(dl, fl, dl, fl):
            sid = '%s|%.6f|%.2f,%.1f,%.2f,%.1f' % (name, s, d1, math.degrees(f1), d2, math.degrees(f2))
            if sid in done:
                continue
            if os.path.exists(STOP):
                return
            t0 = time.time()
            p0 = G.from_local(pA, pC, pX, s, f1, f2)
            p0[1], p0[2] = d1, d2
            f = lambda p: -objective(p, s)
            r = minimize(f, p0, method='Nelder-Mead', options=dict(maxiter=a.iters, xatol=1e-7, fatol=1e-9, adaptive=True))
            r = minimize(f, r.x, method='Nelder-Mead', options=dict(maxiter=a.iters, xatol=1e-8, fatol=1e-10, adaptive=True))
            p, t = r.x, -r.fun
            row = dict(id=sid, s=s, t=float(t), p=[float(v) for v in p], start_margin=G.margin(p0, s),
                       seconds=round(time.time() - t0, 1))
            if t > 1e-6:
                Vs = G.verts(p, s)
                row['margin'] = G.margin(p, s)
                row['J'] = float(G.jam_J(Vs))
                pm, pose, nc = R.pierce_O(None, s, 1.0, Vs=Vs)
                row.update(pierce=float(pm), pierce_pose=pose, comps=nc)
                if pose is not None:
                    row['pierce_pose_free_margin'] = float(R.free_margin(pose, Vs, s))
            with open(OUT, 'a') as fh:
                fh.write(json.dumps(row) + '\n')
            print(sid, 't=%.5f' % t, 'pierce=%s' % row.get('pierce'), row['seconds'], 's', flush=True)


if __name__ == '__main__':
    main()
