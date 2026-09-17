"""A244 crowd rows for the twelve border cells, in WITNESS-POINT form.

A217's corner crowd rows push a designated VERTEX of the meeter into the corner box.  That is a
sufficient condition for meeting, but it misses the cross configuration (a 45-degree square
centred on a cell meets it with no vertex of either inside the other), which is exactly the
configuration a wall slot invites.  So A244 designates, for each (cell, meeter) pair, a WITNESS
POINT p and asks p to lie in the cell and in the square, both with margin delta:

    p in cell:    x0 + delta <= p_x <= x1 - delta,   y0 + delta <= p_y <= y1 - delta
    p in square:  n_e(th_i) . (p - c_i) <= 1/2 - delta,  e = 0..3

Eight rows per pair, all smooth, no selection: delta > 0 implies the interiors meet with a margin,
so a feasible point is a 12-stuck packing up to the rounding handled in verify244.

Variables: w = [z (34: A217's layout), p_0 (2), ..., p_{M-1} (2)], M = 2 * (#constrained cells).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G
import cells244 as C

ROT90 = np.array([[0.0, -1.0], [1.0, 0.0]])


def nw(npair):
    return G.NV + 2 * npair


def designate(z, cells, k=2, n=11):
    """the k squares of deepest overlap with each cell, as a list of (cell, square) pairs."""
    d = C.depth_table(z, n)
    idx = {name: j for j, name in enumerate(C.CELLS)}
    out = []
    for name in cells:
        order = np.argsort(-d[idx[name]])
        for i in order[:k]:
            out.append((name, int(i)))
    return out


def witness_init(z, des):
    """initial witness points: the centroid of the square-cell intersection when it is non-empty,
    else the cell centre pulled onto the square."""
    s = float(z[G.S_IDX])
    P = []
    for name, i in des:
        x0, x1, y0, y1 = C.cell_rect(name, s)
        q = C.square_corners(z[3 * i], z[3 * i + 1], z[3 * i + 2])
        poly = _clip(q, (x0, x1, y0, y1))
        if len(poly) >= 3:
            P.append(np.mean(poly, axis=0))
        else:
            rc = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
            sc = np.array([z[3 * i], z[3 * i + 1]])
            P.append(0.5 * (rc + sc))
    return np.concatenate([np.asarray(z, float), np.array(P).reshape(-1)])


def _clip(poly, rect):
    x0, x1, y0, y1 = rect
    out = [tuple(p) for p in poly]
    for a, lim, keep_lower in ((0, x0, False), (0, x1, True), (1, y0, False), (1, y1, True)):
        inp, out = out, []
        if not inp:
            break
        for k in range(len(inp)):
            cur, prv = inp[k], inp[k - 1]
            ic = (cur[a] <= lim) if keep_lower else (cur[a] >= lim)
            ip = (prv[a] <= lim) if keep_lower else (prv[a] >= lim)
            if ic != ip:
                t = (lim - prv[a]) / (cur[a] - prv[a])
                out.append((prv[0] + t * (cur[0] - prv[0]), prv[1] + t * (cur[1] - prv[1])))
            if ic:
                out.append(cur)
    return np.array(out) if out else np.zeros((0, 2))


def crowd_rows(w, des, delta):
    """values (8M,) and jacobian (8M, NW) of the witness-point rows."""
    z = w[:G.NV]
    s = float(z[G.S_IDX])
    M = len(des)
    NW = nw(M)
    g = np.zeros((M, 8))
    J = np.zeros((M, 8, NW))
    for a, (name, i) in enumerate(des):
        p = w[G.NV + 2 * a: G.NV + 2 * a + 2]
        x0, x1, y0, y1 = C.cell_rect(name, s)
        d0, d1, e0, e1 = C.cell_rect_ds(name)
        ip = G.NV + 2 * a
        for r, (val, dp, dsv) in enumerate((
                (p[0] - x0 - delta, (1.0, 0.0), -d0),
                (x1 - delta - p[0], (-1.0, 0.0), d1),
                (p[1] - y0 - delta, (0.0, 1.0), -e0),
                (y1 - delta - p[1], (0.0, -1.0), e1))):
            g[a, r] = val
            J[a, r, ip] = dp[0]
            J[a, r, ip + 1] = dp[1]
            J[a, r, G.S_IDX] = dsv
        th = z[3 * i + 2]
        co, si = np.cos(th), np.sin(th)
        R = np.array([[co, -si], [si, co]])
        c = np.array([z[3 * i], z[3 * i + 1]])
        for e in range(4):
            n = R @ G.NHAT[e]
            dn = ROT90 @ n
            g[a, 4 + e] = 0.5 - delta - n @ (p - c)
            J[a, 4 + e, ip] = -n[0]
            J[a, 4 + e, ip + 1] = -n[1]
            J[a, 4 + e, 3 * i] = n[0]
            J[a, 4 + e, 3 * i + 1] = n[1]
            J[a, 4 + e, 3 * i + 2] = -dn @ (p - c)
    return g.reshape(-1), J.reshape(-1, NW)


def make_extra(des, delta):
    def fun(w):
        return crowd_rows(w, des, delta)[0]

    def jac(w):
        return crowd_rows(w, des, delta)[1]
    return fun, jac


def active_crowd(w, des, delta, tol=1e-7):
    g, J = crowd_rows(w, des, delta)
    idx = [k for k in range(len(g)) if abs(g[k]) <= tol]
    labels = [{'kind': 'crowd', 'cell': des[k // 8][0], 'i': des[k // 8][1], 'row': k % 8} for k in idx]
    return labels, (J[idx][:, :G.NV] if idx else np.zeros((0, G.NV)))
