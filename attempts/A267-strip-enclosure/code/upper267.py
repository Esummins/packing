"""A267: the UPPER-case quantities on the 43 JAM rings (strip_enclosure.md s.2): X's bottom vertex vs L, the C-X
wedge (X's lower-right edge vs C's upper-left edge), whether X covers T_u's top vertex T', the free room right of X
below C's top, and the exact free-centre region of a third square Q (free of C, X, wall, floor) intersected with the
left shadow of C (+) Q -- the bad-centre area, which must be 0 -- with the tightest constraint per ring.
    python upper267.py  -> results/upper267.json"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, Point, box as sbox

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure267 as M                                                # noqa: E402
Z, DEG = M.Z, M.DEG


def mink(P, Q):
    pts = np.array([p + q for p in P for q in Q])
    return Polygon(pts).convex_hull


def bad_area(C, X, hu, step=1.0):
    """max over tilts of the area of {q : Q(q, psi) free of C, X, in the quadrant, q + h_u e_x in int(C (+) Q)}."""
    best, at = 0.0, None
    for pd in np.arange(0.0, 90.0, step):
        psi = pd * DEG
        q0 = Z.sq_verts(0.0, 0.0, psi)
        h = 0.5 * (abs(math.cos(psi)) + abs(math.sin(psi)))
        free = sbox(h, h, 6.0, 6.0).difference(mink(C, q0)).difference(mink(X, q0))
        Tu = C - np.array([hu, 0.0])
        bad = free.intersection(mink(Tu, q0).buffer(-1e-9))
        if bad.area > best:
            best, at = bad.area, pd
    return best, at


def upper(row, r):
    V = M.G.verts(r['p'], r['s'])
    X, C = V[6], V[7]
    hu, hv, c, sn = row['h_u'], row['h_v'], row['c'], row['sn']
    Lh, Ctop = hv + c, hv + c + sn
    Tp = np.array([c, Ctop])                                          # T_u's top vertex T'
    L = np.array([hu, Lh])
    xlow = row['X_low']
    sX = float(X[np.argmin(X[:, 1])][0])                              # x of X's bottom vertex
    phi = row['phi_X_deg'] * DEG
    th = row['theta_deg'] * DEG
    # room right of X, left of C's UL edge, at C's top and at max(X_low, L_h)
    def rX(y):
        return sX + (y - xlow) / math.tan(phi) if y <= xlow + math.sin(phi) else \
            sX + math.cos(phi) - (y - xlow - math.sin(phi)) * math.tan(phi)
    def lC(y):
        return hu + (y - Lh) / math.tan(th) if y >= Lh else hu + sn - (y - hv) * math.tan(th)
    y0 = max(xlow, Lh)
    room_top = lC(Ctop) - rX(Ctop)
    room_lo = lC(y0) - rX(y0)
    ba, at = bad_area(C, X, hu)
    return dict(id=row['id'], X_low_minus_Lh=xlow - Lh, sX=sX, phi_minus_theta=row['phi_X_deg'] - row['theta_deg'],
                Tp_in_X=bool(Polygon(X).contains(Point(Tp))), L_gap_to_X=float(Polygon(X).distance(Point(L))),
                room_at_Ctop=room_top, room_at_y0=room_lo, y0=y0, bad_area=ba, bad_tilt=at,
                X_left_x_at_Ctop=(row['y_X'] - Ctop) * math.tan(phi), c=c)


def main():
    res = json.load(open(os.path.join(HERE, '..', 'results', 'measure267.json')))
    rings = {r['id']: r for r in M.rings()}
    rows = [upper(row, rings[row['id']]) for row in res['rows']]
    keys = ['X_low_minus_Lh', 'sX', 'phi_minus_theta', 'L_gap_to_X', 'room_at_Ctop', 'room_at_y0', 'bad_area',
            'X_left_x_at_Ctop', 'c']
    summ = {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in keys}
    summ['all_Tp_in_X'] = all(r['Tp_in_X'] for r in rows)
    summ['n_Tp_in_X'] = sum(r['Tp_in_X'] for r in rows)
    for k in keys:
        print('%-18s %10.5f %10.5f' % (k, summ[k][0], summ[k][1]))
    print('Tp_in_X', summ['n_Tp_in_X'], 'of', len(rows))
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'upper267.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
