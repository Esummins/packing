"""
exact_solve.py -- contact graph extraction + high-precision (mpmath) solution of the tangency
system for a numerically converged packing, plus algebraic identification.

Input : trump11_float.json  (canonicalised float solution, s and X (n,3))
Output: trump11_exact.json  (60-digit coordinates, contact list, polynomial checks)
        prints a report used for notes.md

Contacts detected (tolerance --tol, default 1e-7):
  wall  : corner P of square i on wall  x=0 | y=0 | x=s | y=s
  edge  : corner P of square i on the edge line of square j: n.(P - c_j) = 1/2 with n an
          outward unit normal of j, and P inside the edge segment (|tangential| <= 1/2 + tol)
Every contact is one scalar equation.  Unknowns: (cx,cy,theta) x n and s  (34 for n=11).
Solve: Gauss-Newton with mp.qr_solve (least squares; system is over-determined but consistent).
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

import numpy as np
import mpmath as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'code'))
from squares import all_corners  # noqa: E402

HALF = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
# outward normals of the square in its own frame, edge k joins corner k and k+1
NORMALS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NORMAL_NAMES = ['bottom', 'right', 'top', 'left']


def corner_f(cx, cy, th, k):
    c, s = mp.cos(th), mp.sin(th)
    hx, hy = HALF[k]
    return cx + c * hx - s * hy, cy + s * hx + c * hy


def normal_f(th, e):
    c, s = mp.cos(th), mp.sin(th)
    nx, ny = NORMALS[e]
    return c * nx - s * ny, s * nx + c * ny


def detect_contacts(X, s, tol=1e-7):
    """Return list of contact dicts from a float configuration."""
    n = len(X)
    C = all_corners(X)
    contacts = []
    for i in range(n):
        for k in range(4):
            px, py = C[i, k]
            for wall, val in (('x=0', px), ('y=0', py), ('x=s', s - px), ('y=s', s - py)):
                if abs(val) < tol:
                    contacts.append({'type': 'wall', 'square': i, 'corner': k, 'wall': wall,
                                     'point': [float(px), float(py)]})
            for j in range(n):
                if j == i:
                    continue
                cj = X[j, :2]
                thj = X[j, 2]
                for e in range(4):
                    nx = math.cos(thj) * NORMALS[e][0] - math.sin(thj) * NORMALS[e][1]
                    ny = math.sin(thj) * NORMALS[e][0] + math.cos(thj) * NORMALS[e][1]
                    d = nx * (px - cj[0]) + ny * (py - cj[1]) - 0.5
                    # tangential coordinate along the edge
                    tx, ty = -ny, nx
                    t = tx * (px - cj[0]) + ty * (py - cj[1])
                    if abs(d) < tol and abs(t) <= 0.5 + tol:
                        contacts.append({'type': 'edge', 'square': i, 'corner': k, 'other': j,
                                         'edge': e, 'edge_name': NORMAL_NAMES[e],
                                         'tangential': float(t), 'point': [float(px), float(py)],
                                         'at_edge_end': bool(abs(abs(t) - 0.5) < tol)})
    return contacts


def residuals(z, contacts, n):
    """Residual vector (mp) of all contact equations at unknown vector z (mp matrix / list)."""
    s = z[3 * n]
    res = []
    for c in contacts:
        i, k = c['square'], c['corner']
        px, py = corner_f(z[3 * i], z[3 * i + 1], z[3 * i + 2], k)
        if c['type'] == 'wall':
            w = c['wall']
            res.append({'x=0': px, 'y=0': py, 'x=s': s - px, 'y=s': s - py}[w])
        else:
            j, e = c['other'], c['edge']
            nx, ny = normal_f(z[3 * j + 2], e)
            res.append(nx * (px - z[3 * j]) + ny * (py - z[3 * j + 1]) - mp.mpf(1) / 2)
    return res


def jacobian(z, contacts, n, h=None):
    """Numerical (central difference) Jacobian in mp arithmetic; adequate for Newton since
    we only need it for the direction; the residual is exact."""
    if h is None:
        h = mp.mpf(10) ** (-(mp.mp.dps // 2))
    m = len(contacts)
    nv = 3 * n + 1
    J = mp.matrix(m, nv)
    for v in range(nv):
        zp = list(z); zm = list(z)
        zp[v] += h; zm[v] -= h
        rp = residuals(zp, contacts, n)
        rm = residuals(zm, contacts, n)
        for r in range(m):
            J[r, v] = (rp[r] - rm[r]) / (2 * h)
    return J


def gauss_newton(z0, contacts, n, iters=12, verbose=True):
    z = [mp.mpf(v) for v in z0]
    for it in range(iters):
        r = residuals(z, contacts, n)
        rn = mp.sqrt(sum(x * x for x in r))
        if verbose:
            print(f'  GN iter {it}: |r| = {mp.nstr(rn, 5)}')
        if rn < mp.mpf(10) ** (-(mp.mp.dps - 5)):
            break
        J = jacobian(z, contacts, n)
        rhs = mp.matrix([-x for x in r])
        # least-squares step via normal equations (mp.qr_solve crashes on this Python build)
        dz = mp.lu_solve(J.T * J, J.T * rhs)
        for v in range(len(z)):
            z[v] += dz[v]
    return z


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    tol = 1e-7
    mp.mp.dps = 70
    d = json.load(open(os.path.join(here, 'trump11_float.json')))
    X = np.array(d['X'])
    s = d['s']
    n = len(X)
    contacts = detect_contacts(X, s, tol)
    print(f'{len(contacts)} contact equations detected (tol {tol})')
    for c in contacts:
        if c['type'] == 'wall':
            print(f"  sq{c['square']} corner{c['corner']} on wall {c['wall']}  at ({c['point'][0]:.6f},{c['point'][1]:.6f})")
        else:
            print(f"  sq{c['square']} corner{c['corner']} on sq{c['other']} {c['edge_name']} edge, "
                  f"t={c['tangential']:+.6f}{'  (edge end)' if c['at_edge_end'] else ''}  at ({c['point'][0]:.6f},{c['point'][1]:.6f})")

    z0 = list(X.ravel()) + [s]
    z = gauss_newton(z0, contacts, n)
    # rank of Jacobian at solution
    J = jacobian(z, contacts, n)
    Jn = np.array(J.tolist(), dtype=float)
    sv = np.linalg.svd(Jn, compute_uv=False)
    rank_all = int((sv > 1e-9).sum())
    sv_pos = np.linalg.svd(Jn[:, :3 * n], compute_uv=False)
    rank_pos = int((sv_pos > 1e-9).sum())
    print(f'Jacobian: {len(contacts)} eqs x {3*n+1} unknowns; rank {rank_all}; rank wrt positions only {rank_pos} '
          f'(infinitesimally rigid iff {3*n}); smallest singular values {sv[-3:]}')

    S = z[3 * n]
    th_t = z[3 * 6 + 2]     # squares 6..10 tilted (canonical order); check they're all equal
    ths = [z[3 * i + 2] for i in range(6, n)]
    print('tilted angles (deg):', [mp.nstr(mp.degrees(t), 25) for t in ths])
    print('max angle spread:', mp.nstr(max(ths) - min(ths), 5))
    print('upright angles:', [mp.nstr(z[3 * i + 2], 5) for i in range(6)])
    t = mp.tan(th_t / 2)
    p_t = [5, 10, -2, -14, 12, 6, 2, -2, -1]
    octic = [1, -20, 178, -842, 1923, -496, -6754, 12420, -6865]
    pt_val = mp.polyval(p_t, t)
    pt_val_neg = mp.polyval(p_t, -t)
    oct_val = mp.polyval(octic, S)
    print('s      =', mp.nstr(S, 62))
    print('theta  =', mp.nstr(mp.degrees(th_t), 62), 'deg')
    print('t=tan(theta/2) =', mp.nstr(t, 62))
    print('p(t)   =', mp.nstr(pt_val, 5), '   p(-t) =', mp.nstr(pt_val_neg, 5))
    print('octic(s) =', mp.nstr(oct_val, 5))
    # independent identification by integer relation (PSLQ) with degree 8
    mp.mp.dps = 60
    fp_s = mp.findpoly(S, 8, maxcoeff=10 ** 6, maxsteps=10 ** 5)
    fp_t = mp.findpoly(t, 8, maxcoeff=10 ** 6, maxsteps=10 ** 5)
    fp_c = mp.findpoly(mp.cos(th_t), 8, maxcoeff=10 ** 6, maxsteps=10 ** 5)
    print('findpoly(s, deg 8)      =', fp_s)
    print('findpoly(t, deg 8)      =', fp_t)
    print('findpoly(cos theta, 8)  =', fp_c)
    mp.mp.dps = 70
    # minimal polynomials of all coordinates (degree <= 8)
    coord_polys = []
    for i in range(n):
        row = []
        for v in range(2):
            val = z[3 * i + v]
            mp.mp.dps = 60
            fp = mp.findpoly(val, 8, maxcoeff=10 ** 7, maxsteps=10 ** 5)
            mp.mp.dps = 70
            row.append(fp)
        coord_polys.append(row)
    out = {
        'description': 'Trump (1979) 11-square packing, canonical orientation: uprights 0..5, tilted 6..10',
        'precision_digits': 60,
        'method': 'contacts detected at tol 1e-7 from SLSQP solution; Gauss-Newton (mp.qr_solve) at 70 dps',
        's': mp.nstr(S, 60),
        'theta_deg': mp.nstr(mp.degrees(th_t), 60),
        'theta_rad': mp.nstr(th_t, 60),
        't_tan_half_theta': mp.nstr(t, 60),
        'cos_theta': mp.nstr(mp.cos(th_t), 60),
        'sin_theta': mp.nstr(mp.sin(th_t), 60),
        'squares': [{'cx': mp.nstr(z[3 * i], 60), 'cy': mp.nstr(z[3 * i + 1], 60),
                     'theta': mp.nstr(z[3 * i + 2], 60),
                     'minpoly_cx': coord_polys[i][0], 'minpoly_cy': coord_polys[i][1]} for i in range(n)],
        'contacts': contacts,
        'n_contact_equations': len(contacts),
        'jacobian_rank': rank_all, 'jacobian_rank_positions_only': rank_pos,
        'checks': {
            'p(t) = 5t^8+10t^7-2t^6-14t^5+12t^4+6t^3+2t^2-2t-1 at t=-tan(theta/2)': mp.nstr(pt_val_neg, 5),
            'p(t) at t=+tan(theta/2)': mp.nstr(pt_val, 5),
            'octic(s) = s^8-20s^7+178s^6-842s^5+1923s^4-496s^3-6754s^2+12420s-6865': mp.nstr(oct_val, 5),
            'findpoly_s_deg8': fp_s, 'findpoly_t_deg8': fp_t, 'findpoly_cos_deg8': fp_c,
        },
    }
    with open(os.path.join(here, 'trump11_exact.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('wrote trump11_exact.json')


if __name__ == '__main__':
    main()
