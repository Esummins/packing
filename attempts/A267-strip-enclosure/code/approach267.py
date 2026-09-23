"""A267: where does a free square Q (free of C, X, in the quadrant) come CLOSEST to the strip S on the JAM rings?
Per ring and tilt psi: the free centre region F = quadrant-offset minus (C (+) Q0) minus (X (+) Q0), the target
T = T_u (+) Q0; dist(F, T) > 0 <=> no bad centre at that tilt.  Records the min over psi, the nearest free centre q*,
the pose of Q there, which obstacles Q touches at q* (gap < 1e-6 to C / X / wall / floor), and Q's centre height vs
C's top -- the ENTRY that the geometry wants.   python approach267.py [--step 1.0] -> results/approach267.json"""
import argparse
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import nearest_points

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure267 as M                                                # noqa: E402
from upper267 import mink                                             # noqa: E402
Z, DEG = M.Z, M.DEG


def approach(row, r, step):
    V = M.G.verts(r['p'], r['s'])
    X, C = V[6], V[7]
    hu = row['h_u']
    Tu = C - np.array([hu, 0.0])
    best = None
    for pd in np.arange(0.0, 90.0, step):
        psi = pd * DEG
        q0 = Z.sq_verts(0.0, 0.0, psi)
        h = 0.5 * (abs(math.cos(psi)) + abs(math.sin(psi)))
        F = sbox(h, h, 6.0, 6.0).difference(mink(C, q0)).difference(mink(X, q0))
        T = mink(Tu, q0)
        d = F.distance(T)
        if best is None or d < best['dist']:
            p, _ = nearest_points(F, T)
            Q = Z.sq_verts(p.x, p.y, psi)
            best = dict(dist=float(d), psi_deg=float(pd), q=[float(p.x), float(p.y)],
                        gap_C=Z.poly_gap(Q, C), gap_X=Z.poly_gap(Q, X), wall=float(Q[:, 0].min()),
                        floor=float(Q[:, 1].min()), q_above_Ctop=bool(p.y > row['C_top']),
                        Q_low=float(Q[:, 1].min()), depth_Tu=-Z.poly_gap(Q, Tu))
    best['touches'] = [k for k, v in (('C', best['gap_C']), ('X', best['gap_X']), ('wall', best['wall']),
                                      ('floor', best['floor'])) if abs(v) < 1e-6]
    best['id'] = row['id']
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', type=float, default=1.0)
    a = ap.parse_args()
    res = json.load(open(os.path.join(HERE, '..', 'results', 'measure267.json')))
    rings = {r['id']: r for r in M.rings()}
    rows = [approach(row, rings[row['id']], a.step) for row in res['rows']]
    for b in rows:
        print('%-44s dist %.4f psi %5.1f q (%.3f, %.3f) above_Ctop %s touches %s' %
              (b['id'][:44], b['dist'], b['psi_deg'], b['q'][0], b['q'][1], b['q_above_Ctop'], b['touches']))
    summ = dict(min_dist=min(b['dist'] for b in rows), n_above=sum(b['q_above_Ctop'] for b in rows), n=len(rows))
    print(summ)
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'approach267.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
