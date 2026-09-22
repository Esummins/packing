"""A266 probe of STRIP_2's domain: in-domain samples (X avoids C, meets T_u, in the quadrant), the box test at shrinking
radii on each, and for a FAILING small box the EXACT centre-set search for a real bad square (Q free of C, X, in the
quadrant, meeting int T_u) at the box middle -- every reported witness passes the exact SAT + containment check.
    python probe266.py [--n 60] [--lane jam|mir] [--seed 1] [--nobox]  -> results/probe266_<lane>[_nobox].json
(--nobox drops "C meets the open box": the reading of strip_plug.md s.1.1; its FAILS are [F] witnesses for that reading)"""
import argparse
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import strip266 as M                                                  # noqa: E402
Z = M.Z
DEG = M.DEG


def verts_of(x):
    """exact vertex arrays of C, X, T_u at parameter x."""
    hu, hv, th, yx, ph = x
    cC, cX, cT = M.centres(np.array(x))
    return M.sq(*cC, th, 0.5), M.sq(*cX, ph, 0.5), M.sq(*cT, th, 0.5)


def in_domain(x, box=True):
    C, X, T = verts_of(x)
    if X[:, 1].min() < -1e-12 or (box and Z.poly_gap(C, M.UNIT) >= -1e-9):   # X over the floor; C meets the open unit box
        return False
    if X[:, 1].min() < x[1] - 1e-12:                                   # X above C (its lowest point not below C's)
        return False
    return Z.poly_gap(X, C) >= -1e-12 and Z.poly_gap(X, T) < -1e-9


def sample(rng, lane, n, box=True):
    p0, p1 = M.LANES[lane]
    out = []
    while len(out) < n:
        x = [rng.uniform(0.001, 0.999), rng.uniform(0.0, 0.999), rng.uniform(0, 45) * DEG, rng.uniform(*M.YX),
             rng.uniform(p0, p1) * DEG]
        if in_domain(x, box):
            out.append(x)
    return out


def exact_bad(x, step=1.0):
    """max over tilts of the area of {q : Q free of C, X, in the quadrant, q in int(T_u (+) Q)} and a witness pose."""
    C, X, T = verts_of(x)
    best, pose = 0.0, None
    for pd in np.arange(-45.0, 45.0, step):
        psi = pd * DEG
        q0 = Z.sq_verts(0.0, 0.0, psi)
        h = 0.5 * (abs(math.cos(psi)) + abs(math.sin(psi)))
        free = sbox(h, h, 9.0, 9.0)
        for V in (C, X):
            free = free.difference(Polygon(M.mink(V, q0)))
        S = free.intersection(Polygon(M.mink(T, q0)).buffer(-1e-9))
        if S.area > best:
            best = S.area
            P = max(getattr(S, 'geoms', [S]), key=lambda g: g.area)
            c = P.representative_point()
            pose = (float(c.x), float(c.y), float(psi))
    return best, pose


def witness_check(pose, x):
    """exact geometry: Q at pose is in the quadrant, interior-disjoint from C and X, and meets int T_u (depth > 0)."""
    C, X, T = verts_of(x)
    Q = Z.sq_verts(*pose)
    return dict(quadrant=float(min(Q[:, 0].min(), Q[:, 1].min())), gap_C=Z.poly_gap(Q, C), gap_X=Z.poly_gap(Q, X),
                depth_Tu=-Z.poly_gap(Q, T))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=60)
    ap.add_argument('--lane', default='jam')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--nobox', action='store_true')                   # the WRONG domain (h_u, h_v < 1 only): [F] witnesses
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    xs = sample(rng, a.lane, a.n, not a.nobox)
    rows, fails = [], 0
    for x in xs:
        rec = dict(x=[float(t) for t in x], radii={})
        for r in (0.02, 0.01, 0.005, 0.0025):
            lo = [x[0] - r, x[1] - r, x[2] - r, x[3] - r, x[4] - r]
            hi = [x[0] + r, x[1] + r, x[2] + r, x[3] + r, x[4] + r]
            st, m = M.check_box(lo, hi)
            rec['radii'][str(r)] = [st, None if m is None else float(m)]
        if rec['radii']['0.0025'][0] == 'FAIL':
            fails += 1
            area, pose = exact_bad(x)
            rec['exact_bad_area'] = area
            if pose is not None:
                rec['witness'] = dict(pose=pose, check=witness_check(pose, x))
        rows.append(rec)
        print(json.dumps(rec), flush=True)
    json.dump(dict(lane=a.lane, n=len(rows), fails_at_0025=fails, nobox=a.nobox, rows=rows),
              open(os.path.join(HERE, '..', 'results', 'probe266_%s%s.json' % (a.lane, '_nobox' if a.nobox else '')), 'w'), indent=1)
    print('fails at r=0.0025:', fails, 'of', len(rows))


if __name__ == '__main__':
    main()
