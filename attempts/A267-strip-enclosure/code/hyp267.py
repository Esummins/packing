"""A267: the hypotheses of STRIP_2-IN-RING (strip_enclosure.md s.3) checked with margins on the 43 JAM rings.
C's frame: a along C's upper-left edge from L (unit e = (c, s)), b the outward normal (n = (-s, c)); C = [0,1] x [-1,0],
T_u = C + (-h_u c, h_u s), T_u's top edge a = a* := 1 - h_u c.  X's lower-right edge from B_X = (a_B, b_B) to
R_X = (a_R, b_R) is the roof of the C-X wedge b_X(a) over [a_1, a_2] = [max(a_B, 0), min(a_R, 1)].
    (D1) h_v < 1 < h_v + cos theta and g = ell_C(1) < 1  (C meets the open box; L above height 1)
    (D2) X: leftmost vertex on the wall, tilt phi in [0, 45], lowest point >= h_v, X meets int T_u, X avoids int C
    (U1) a_1 < a*   (U2) b_X >= 0 on [a_1, a_2] (the roof is above C's edge: the wedge exists)
    (U3) a_2 - a* > w_max s' c' for every tilt, i.e. a_2 - a* > w_max / 2, w_max = max(b_X(a_1), b_X(a_2))
    (U4) the room right of X below C's top is < 1: rho(C_top) < 1, rho(y_0) < 1, and ell_C(X_low) < 1 if X_low > L_h
    (U5) a_R - sin(beta)^+ >= a*  (T_u's top edge is left of X's right vertex's perpendicular)
    (U6) h_u + cos theta - cos phi_X < 1   (U8) X_top > C_top + 1/sqrt 2   (U9) T_u lies below X's far edge: sigma < 1
    python hyp267.py -> results/hyp267.json"""
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure267 as M                                                # noqa: E402


def frame_X(row, X):
    hu, hv, c, s = row['h_u'], row['h_v'], row['c'], row['sn']
    L = np.array([hu, hv + c])
    e, n = np.array([c, s]), np.array([-s, c])
    ab = lambda P: (float(e @ (P - L)), float(n @ (P - L)))         # noqa: E731
    B, R = X[np.argmin(X[:, 1])], X[np.argmax(X[:, 0])]
    (aB, bB), (aR, bR) = ab(B), ab(R)
    tb = (bR - bB) / (aR - aB)
    bX = lambda a: bB + (a - aB) * tb                                 # noqa: E731
    a1, a2, astar = max(aB, 0.0), min(aR, 1.0), 1.0 - hu * c
    wmax = max(bX(a1), bX(a2))
    beta = math.atan(tb)
    Tu = np.array([[-hu * c, hu * s], [1 - hu * c, hu * s], [1 - hu * c, hu * s - 1], [-hu * c, hu * s - 1]])
    sig = max(-(p[0] - aB) * math.sin(beta) + (p[1] - bB) * math.cos(beta) for p in Tu)
    return dict(a_B=aB, b_B=bB, a_R=aR, b_R=bR, beta_deg=math.degrees(beta), a1=a1, a2=a2, a_star=astar,
                w_neck=bX(a1), w_mouth=bX(a2), w_max=wmax, U1=astar - a1, U2=min(bX(a1), bX(a2)),
                U3=a2 - astar - wmax / 2, U5=aR - max(0.0, math.sin(beta)) - astar,
                U6=1.0 - (hu + c - math.cos(math.radians(row['phi_X_deg']))),
                U8=row['X_top'] - row['C_top'] - 0.5 ** 0.5, U9=1.0 - sig)


def rooms(row, X):
    hu, hv, c, s = row['h_u'], row['h_v'], row['c'], row['sn']
    Lh, Ctop, xlow = hv + c, hv + c + s, row['X_low']
    phi, th = math.radians(row['phi_X_deg']), math.atan2(s, c)
    sX = float(X[np.argmin(X[:, 1])][0])
    rX = lambda y: (sX + (y - xlow) / math.tan(phi) if y <= xlow + math.sin(phi) else                # noqa: E731
                    sX + math.cos(phi) - (y - xlow - math.sin(phi)) * math.tan(phi))
    lC = lambda y: hu + (y - Lh) / math.tan(th) if y >= Lh else hu + s - (y - hv) * math.tan(th)   # noqa: E731
    y0 = max(xlow, Lh)
    return dict(rho_top=lC(Ctop) - rX(Ctop), rho_y0=lC(y0) - rX(y0), lC_xlow=lC(xlow) if xlow > Lh else hu,
                U4=1.0 - max(lC(Ctop) - rX(Ctop), lC(y0) - rX(y0), lC(xlow) if xlow > Lh else hu))


def main():
    res = json.load(open(os.path.join(HERE, '..', 'results', 'measure267.json')))
    rings = {r['id']: r for r in M.rings()}
    rows = []
    for row in res['rows']:
        X = M.G.verts(rings[row['id']]['p'], rings[row['id']]['s'])[6]
        d = dict(id=row['id'], D1=min(1.0 - row['h_v'], row['h_v'] + row['c'] - 1.0, 1.0 - row['g']),
                 D2=min(row['X_low'] - row['h_v'], 45.0 - row['phi_X_deg'], row['X_meets_Tu_area'], row['gap_CX']))
        d.update(frame_X(row, X))
        d.update(rooms(row, X))
        rows.append(d)
    keys = ['D1', 'D2', 'U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U8', 'U9', 'a_B', 'b_B', 'a_R', 'b_R', 'beta_deg', 'a_star', 'w_neck',
            'w_mouth', 'rho_top', 'rho_y0', 'lC_xlow']
    summ = {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in keys}
    summ['n'] = len(rows)
    summ['all_hold'] = all(min(r['D1'], r['D2'], r['U1'], r['U2'], r['U3'], r['U4'], r['U5'], r['U6'], r['U8'], r['U9']) > 0 for r in rows)
    for k in keys:
        print('%-10s %10.5f %10.5f' % (k, summ[k][0], summ[k][1]))
    print('n', summ['n'], 'all hypotheses hold with positive margin:', summ['all_hold'])
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'hyp267.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
