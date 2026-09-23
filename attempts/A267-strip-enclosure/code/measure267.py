"""A267 measurements on the JAM rings (A262 ring262.jsonl, t > 0): the ENCLOSURE of the strip S = T_u \\ C.
Squares (geom262.verts, imported, never edited): 0 = A (floor START), 6 = X (wall START above C), 7 = C (floater).
Per ring: h_u, h_v, theta_C, u = h_u + sin theta, g = ell_C(1) (the LL edge's x at height 1; g < 1 <=> C meets
the open box when h_v < 1 <= h_v + cos theta), C's area in the box, gaps C-A / C-X, A's area in the band
[0, h_u] x [h_v - 0.6, h_v], X's pose (leftmost vertex y_X, lowest point, tilt), X's centre height vs h_v + cos,
X's intrusion into T_u, and the UPPER-case quantities of strip_enclosure.md (X's centre chord, tau_X).
    python measure267.py  -> results/measure267.json (+ a table on stdout)"""
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
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A262-no-jam', 'code'))
import geom262 as G                                                   # noqa: E402
Z = G.Z
DEG = G.DEG
RING = os.path.join(ROOT, 'attempts', 'A262-no-jam', 'results', 'ring262.jsonl')


def tilt45(V):
    """tilt in [0, 45 deg) of the square with vertices V (edge angle mod 90, folded)."""
    e = V[1] - V[0]
    th = math.atan2(e[1], e[0]) % (math.pi / 2)
    return th if th <= math.pi / 4 else th - math.pi / 2                # signed: |tilt| <= 45 deg


def frame(V):
    """(h_u, h_v, theta, c, s, u): C's wall / floor distances and tilt in [0, 45] with lowest vertex (h_u + s, h_v)."""
    hu, hv = float(V[:, 0].min()), float(V[:, 1].min())
    th = abs(tilt45(V))
    c, s = math.cos(th), math.sin(th)
    low = V[np.argmin(V[:, 1])]
    return dict(h_u=hu, h_v=hv, theta_deg=th / DEG, c=c, sn=s, u=hu + s, low_x=float(low[0]),
                mirror=bool(abs(low[0] - (hu + s)) > 1e-9))          # mirror: lowest vertex at h_u + c instead


def rings():
    out = []
    for line in open(RING):
        r = json.loads(line)
        if r.get('t', -1) > 0:
            out.append(r)
    return out


def measure(r):
    s = r['s']
    V = G.verts(r['p'], s)
    A, X, C = V[0], V[6], V[7]
    f = frame(C)
    hu, hv, c, sn = f['h_u'], f['h_v'], f['c'], f['sn']
    Tu = C - np.array([hu, 0.0])
    Pc, Px, Pa, Pt = Polygon(C), Polygon(X), Polygon(A), Polygon(Tu)
    S = Pt.difference(Pc)
    g = f['u'] - (1.0 - hv) * sn / c                                  # ell_C(1) along the lower-left edge
    band = sbox(0.0, hv - 0.6, hu, hv)
    xl = X[np.argmin(X[:, 0])]
    xlow = float(X[:, 1].min())
    phi = abs(tilt45(X))
    xc = X.mean(axis=0)
    # X's leftmost vertex must be ON the wall (the ring's X touches x = 0)
    out = dict(id=r['id'], s=s, t=r['t'], **f, g=g, box_ok=bool(g < 1.0 and hv < 1.0 and hv + c > 1.0),
               C_box_area=float(Pc.intersection(sbox(0, 0, 1, 1)).area),
               gap_CA=float(Z.poly_gap(C, A)), gap_CX=float(Z.poly_gap(C, X)),
               A_band_area=float(Pa.intersection(band).area), A_xmin=float(A[:, 0].min()),
               X_left_x=float(xl[0]), y_X=float(xl[1]), X_low=xlow, phi_X_deg=phi / DEG,
               X_centre_y=float(xc[1]), X_centre_x=float(xc[0]), L_height=hv + c,
               X_meets_Tu_area=float(Px.intersection(Pt).area), X_in_S_area=float(Px.intersection(S).area),
               S_area=float(S.area), X_above_L=bool(xc[1] > hv + c),
               tau_X=(1.0 / math.cos(phi) - hu) * sn / c, X_top=float(X[:, 1].max()), C_top=hv + c + sn)
    return out


def main():
    rows = [measure(r) for r in rings()]
    keys = ['h_u', 'h_v', 'theta_deg', 'u', 'g', 'C_box_area', 'gap_CA', 'gap_CX', 'A_band_area', 'A_xmin', 'y_X',
            'X_low', 'phi_X_deg', 'X_centre_y', 'L_height', 'X_meets_Tu_area', 'X_in_S_area', 'tau_X', 'X_top', 'C_top']
    summ = {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in keys}
    summ['n'] = len(rows)
    summ['all_box_ok'] = all(r['box_ok'] for r in rows)
    summ['all_X_above_L'] = all(r['X_above_L'] for r in rows)
    summ['any_mirror'] = any(r['mirror'] for r in rows)
    summ['all_X_left_on_wall'] = all(abs(r['X_left_x']) < 1e-9 for r in rows)
    summ['all_X_low_ge_hv'] = all(r['X_low'] >= r['h_v'] for r in rows)
    for k in keys:
        print('%-16s %10.5f %10.5f' % (k, summ[k][0], summ[k][1]))
    for k in ('n', 'all_box_ok', 'all_X_above_L', 'any_mirror', 'all_X_left_on_wall', 'all_X_low_ge_hv'):
        print(k, summ[k])
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'measure267.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
