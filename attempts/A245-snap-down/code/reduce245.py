"""A245 Lemma REDUCE on a wall: the column families Pi_k = {c00, c01, .., c0(k-1)} (k = 1, 2, 3) in the wall
frame, their meeter sets M(Pi_k) (Lemma CELLS: |M| <= k exchanges the packing into one containing the k
flush column squares at the same side), and the (k+1)-for-(k+1) exchange when |M(Pi_k)| = k + 1: the k+1
meeters are picked up, the k column squares put down, and ONE leftover square is searched in the container
minus the other squares minus the column (A222 `region222.cspace`, exact re-check here)."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'code'))
import geom245 as G                      # noqa: E402
import region222 as RG                   # noqa: E402

THETAS = [math.radians(d) for d in range(0, 90, 3)]


def column_cells(k):
    return [(0.0, 1.0, float(j), float(j + 1)) for j in range(k)]


def column_squares(k):
    return [(0.5, j + 0.5, 0.0) for j in range(k)]


def place_one(fixed, s, thetas=THETAS):
    """one unit square inside the container minus the fixed squares, or None (exact SAT re-check)."""
    best = None
    for th in thetas:
        region = RG.cspace(fixed, s, th)
        pt, d = RG.best_point(region)
        if pt is None:
            continue
        pose = (float(pt[0]), float(pt[1]), th)
        ok, gw, gp = G.check_packing(list(fixed) + [pose], s, tol=1e-9)
        if ok and (best is None or d > best[1]):
            best = (pose, d)
    return best[0] if best else None


def reduce_wall(poses, s, wall, kmax=3):
    """per k: |M(Pi_k)|, the direct CELLS exchange, or the (k+1)-for-(k+1) with a placed leftover."""
    fr = [G.to_frame(p, wall, s) for p in poses]
    out = {}
    M = set()
    for k in range(1, kmax + 1):
        if k > s:
            break
        M |= set(G.meeters_of(fr, column_cells(k)[-1]))
        rec = {'k': k, 'M': sorted(int(i) for i in M), 'size': len(M), 'direct': len(M) <= k, 'placed': None}
        if len(M) == k + 1:
            others = [fr[i] for i in range(len(fr)) if i not in M]
            fixed = others + column_squares(k)
            pose = place_one(fixed, s)
            if pose is not None:
                rec['placed'] = [float(v) for v in G.from_frame(pose, wall, s)]
        rec['ok'] = bool(rec['direct'] or rec['placed'] is not None)
        out['k%d' % k] = rec
    out['any_ok'] = bool(any(v['ok'] for kk, v in out.items() if kk.startswith('k')))
    out['best_k'] = max((v['k'] for kk, v in out.items() if kk.startswith('k') and v['ok']), default=0)
    return out


def exchanged_packing(poses, s, wall, rec):
    """the packing after the successful exchange of level k (for drawing / re-checking), global poses."""
    k = rec['k']
    fr = [G.to_frame(p, wall, s) for p in poses]
    M = rec['M']
    keep = [fr[i] for i in range(len(fr)) if i not in M]
    new = keep + column_squares(k)
    if rec['placed'] is not None:
        new.append(G.to_frame(tuple(rec['placed']), wall, s))
    return [G.from_frame(p, wall, s) for p in new]


if __name__ == '__main__':
    import json
    import testbeds245 as T
    for c in T.all_configs(('ring',))[:3]:
        for w in G.WALLS:
            r = reduce_wall(c['poses'], c['s'], w)
            print(c['rid'], w, json.dumps({k: (v['size'], v['ok']) for k, v in r.items() if k.startswith('k')}))
