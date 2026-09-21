"""A262 task 3 [M]: the honest SEARCH for a packing with a JAM corner that reaches 11 squares / is family-stuck.

Structured starts (>= 500): every corpus ring of A258's norm258.jsonl (46 rings, sides 3.82 .. 3.99: the window, s-hat
and the stretch (s-hat, 4)) x 4 rotations (which wall loses its END square) x 3 installs of the JAM corner:
    W0, W1 : A261's witness triple (A, C, X) replaces (floor START, wall-3 START, wall-3 END); walls 1, 2 from the ring
    SL     : the ring's own wall-3 END square slid along X's edge until its lowest vertex is just inside the box
Objective: t = min(geom262.margin, -J) (HARD terms only), Nelder-Mead x 2.  For every start with t > 1e-6 (a JAM RING):
    pierce (room259, 1 deg): < 0 <=> every free square of the pocket contains O;   capacity259.best_set (kmax = 3);
    the exact 12-cell all-families test of ring + the free squares found (fam262).
An 11-square witness = capacity 3;  it is written to results/WITNESS262.json and NOTHING else is claimed from it.
    python search262.py [--limit N]    -> results/search262.jsonl   (resumable by start id; logs/STOP)
"""
import argparse
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
import ring262 as RR                                                  # noqa: E402
import fam262 as F                                                    # noqa: E402
import room259 as R                                                   # noqa: E402
import capacity259 as CAP                                             # noqa: E402
Z = G.Z
OUT = os.path.join(ATT, 'results', 'search262.jsonl')
STOP = os.path.join(ATT, 'logs', 'STOP')
CORPUS = os.path.join(G.ROOT, 'attempts', 'A258-normal-ring', 'results', 'norm258.jsonl')


def starts():
    wit = RR.witnesses()
    for ri, line in enumerate(open(CORPUS)):
        r = json.loads(line)
        s, a, f = r['s'], r['a'], [v * Z.DEG for v in r['phi_deg']]
        for rot in range(4):
            d = [a[(k + rot) % 4] for k in range(4)]
            ph = [f[(k + rot) % 4] for k in range(4)]
            for wi, (name, pA, pC, pX) in enumerate(wit):
                p = G.from_local(pA, pC, pX, s, ph[1], ph[2])
                p[1], p[2] = d[1], d[2]
                yield '%d|%d|W%d' % (ri, rot, wi), s, p
            c3, z3 = math.cos(ph[3]), math.sin(ph[3])
            b3 = s - d[3] - Z.span(ph[3])
            lam = max(0.0, (0.996 - b3) / z3)
            Px, Py = z3 + lam * c3, b3 + lam * z3                      # lowest vertex of the slid END square
            cx = Px + 0.5 * (c3 - z3)
            cy = Py + 0.5 * (c3 + z3)
            yield '%d|%d|SL' % (ri, rot), s, np.array(d + ph + [cx, cy, ph[3]], float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--iters', type=int, default=1500)
    a = ap.parse_args()
    Z.belownormal()
    done = {json.loads(l)['id'] for l in open(OUT)} if os.path.exists(OUT) else set()
    n = 0
    for sid, s, p0 in starts():
        if sid in done:
            continue
        if os.path.exists(STOP) or (a.limit and n >= a.limit):
            return
        n += 1
        t0 = time.time()
        f = lambda p: -RR.objective(p, s)
        r = minimize(f, p0, method='Nelder-Mead', options=dict(maxiter=a.iters, xatol=1e-7, fatol=1e-9, adaptive=True))
        r = minimize(f, r.x, method='Nelder-Mead', options=dict(maxiter=a.iters, xatol=1e-8, fatol=1e-10, adaptive=True))
        p, t = r.x, -r.fun
        row = dict(id=sid, s=s, t=float(t), p=[float(v) for v in p], start_margin=G.margin(p0, s))
        if t > 1e-6:
            Vs = G.verts(p, s)
            row.update(margin=G.margin(p, s), J=float(G.jam_J(Vs)))
            pm, pose, nc = R.pierce_O(None, s, 1.0, Vs=Vs)
            W, ncand = CAP.best_set(Vs, s)
            row.update(pierce=float(pm), comps=nc, capacity_lb=len(W), free=[list(map(float, w)) for w in W])
            allV = Vs + [Z.sq_verts(*w) for w in W]
            rep = F.report(allV, s)
            row.update(n_squares=len(allV), family_stuck=rep['family_stuck'], min_excess=rep['min_excess'],
                       argmin=rep['argmin'], packing_margin=rep['packing_margin'],
                       ring_only_min_excess=F.report(Vs, s)['min_excess'])
            if len(allV) >= 11:
                json.dump(row, open(os.path.join(ATT, 'results', 'WITNESS262.json'), 'w'), indent=1)
        row['seconds'] = round(time.time() - t0, 1)
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(sid, 's=%.4f' % s, 't=%.5f' % t, 'pierce=%s cap=%s stuck=%s' % (
            row.get('pierce'), row.get('capacity_lb'), row.get('family_stuck')), row['seconds'], 's', flush=True)


if __name__ == '__main__':
    main()
