"""A219 fixed-row system at a witness: values, gradients and ANALYTIC Hessians of every active row
(walls, pair rows, tilt-bound rows, crowd rows), the FJ multiplier polytope and the LPs used by
ring219 (minimal external load) and second219 (second-order descent along a first-order zero mode).
Coordinates as geom217: z[3i], z[3i+1], z[3i+2] = cx, cy, theta; z[33] = s.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import geom217 as G          # noqa: E402
import opt217 as O           # noqa: E402
import crowd217 as C         # noqa: E402

NV = G.NV
S_IDX = G.S_IDX
LP_CAP = 1e4
J2 = np.array([[0.0, -1.0], [1.0, 0.0]])       # rotation by +90 deg


def jrot(v):
    return np.array([-v[1], v[0]])


# ---------------------------------------------------------------- rows
def witness_rows(w, tol=1e-7):
    """Active rows of witness dict w (witnesses217.jsonl): walls + edges (opt217.active_rows), then
    the active tilt-bound rows (HELD) and the active crowd rows (CROWD).  Returns (rows, z)."""
    z = np.array(w['z'], float)
    rows, _ = O.active_rows(z, tol)
    for r in rows:                       # NLP(S) keeps A217's line rows (corner on the extended edge line:
        if r['kind'] == 'edge':          # part of the separating-axis condition); flagged for the reports
            r['on_segment'] = bool(on_segment(z, r, tol))
    if w.get('tmin_deg') is not None and w['cls'] in ('HELD', 'BOXK0'):
        tmin = math.radians(w['tmin_deg'])
        for i in O.corner_squares(z):
            th = z[3 * i + 2]
            for sign, b in ((1.0, tmin), (-1.0, math.pi / 2 - tmin)):
                if abs(th - b) <= tol:
                    rows.append({'kind': 'tiltbound', 'i': i, 'bound': b, 'sign': sign})
    if w.get('crowd_delta') is not None and w['cls'] == 'CROWD':
        des = w['designated']
        desq = {cn: [int(i) for i in des[cn]] for cn in G.CORNER_NAMES}
        labels, _ = C.active_crowd_fixed(z, desq, w['crowd_delta'], tol)
        for lab in labels:
            lab['delta'] = w['crowd_delta']
        rows += labels
    return rows, z


def on_segment(z, r, tol=1e-7):
    """an edge row is a geometric contact only if the other's corner lies within the owner's edge SEGMENT
    (|tangential coordinate| <= 1/2); A217's active set also carries 'line rows' (corner on the extended
    line, outside the segment), which are dropped here."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    n = G.normals(z)[r['j'], r['edge']]
    tvec = jrot(n)
    tcoord = tvec @ (q[r['i'], r['corner']] - np.array([cx[r['j']], cy[r['j']]]))
    return abs(tcoord) <= 0.5 + tol


def row_gj(z, r):
    """value, gradient (34,) of one row."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    c = np.stack([cx, cy], -1)
    g = np.zeros(NV)
    if r['kind'] == 'wall':
        i, k = r['i'], r['corner']
        d = jrot(q[i, k] - c[i])
        a = 0 if r['wall'] in ('x=0', 'x=s') else 1
        far = r['wall'] in ('x=s', 'y=s')
        sg = -1.0 if far else 1.0
        val = (s - q[i, k, a]) if far else q[i, k, a]
        g[3 * i + a] = sg
        g[3 * i + 2] = sg * d[a]
        if far:
            g[S_IDX] = 1.0
        return val, g
    if r['kind'] == 'edge':
        p, k, o, e = r['i'], r['corner'], r['j'], r['edge']
        n = G.normals(z)[o, e]
        rr = q[p, k] - c[o]
        dp = jrot(q[p, k] - c[p])
        val = n @ rr - 0.5
        g[3 * p:3 * p + 2] = n
        g[3 * p + 2] = n @ dp
        g[3 * o:3 * o + 2] = -n
        g[3 * o + 2] = jrot(n) @ rr
        return val, g
    if r['kind'] == 'tiltbound':
        g[3 * r['i'] + 2] = r['sign']
        return r['sign'] * (th[r['i']] - r['bound']), g
    if r['kind'] == 'crowd':
        i, k = r['i'], r['vertex']
        M, t, _ = G.corner_frame(r['corner'], s)
        dt_ds = {'BL': (0, 0), 'BR': (1, 0), 'TR': (1, 1), 'TL': (0, 1)}[r['corner']]
        a = 0 if r['coord'] == 'u' else 1
        uv = M @ q[i, k] + t
        d = jrot(q[i, k] - c[i])
        g[3 * i:3 * i + 2] = -M[a]
        g[3 * i + 2] = -(M[a] @ d)
        g[S_IDX] = -dt_ds[a]
        return 1.0 - r['delta'] - uv[a], g
    raise ValueError(r['kind'])


def row_hessian(z, r):
    """analytic Hessian (34,34) of one row.  Vertex q = c + R(th) h: q_c = I, q_th = J(q-c),
    q_thth = -(q-c); edge normal n(th): n_th = J n, n_thth = -n."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    c = np.stack([cx, cy], -1)
    H = np.zeros((NV, NV))
    if r['kind'] == 'wall':
        i, k = r['i'], r['corner']
        a = 0 if r['wall'] in ('x=0', 'x=s') else 1
        sg = -1.0 if r['wall'] in ('x=s', 'y=s') else 1.0
        H[3 * i + 2, 3 * i + 2] = -sg * (q[i, k, a] - c[i, a])
    elif r['kind'] == 'edge':
        p, k, o, e = r['i'], r['corner'], r['j'], r['edge']
        n = G.normals(z)[o, e]
        nprime = jrot(n)
        rr = q[p, k] - c[o]
        vp = q[p, k] - c[p]
        dp = jrot(vp)
        # theta_o with c_p and c_o
        for a in range(2):
            H[3 * p + a, 3 * o + 2] = H[3 * o + 2, 3 * p + a] = nprime[a]
            H[3 * o + a, 3 * o + 2] = H[3 * o + 2, 3 * o + a] = -nprime[a]
        H[3 * o + 2, 3 * o + 2] = -(n @ rr)
        H[3 * p + 2, 3 * o + 2] = H[3 * o + 2, 3 * p + 2] = nprime @ dp
        H[3 * p + 2, 3 * p + 2] = -(n @ vp)
    elif r['kind'] == 'crowd':
        i, k = r['i'], r['vertex']
        M, t, _ = G.corner_frame(r['corner'], s)
        a = 0 if r['coord'] == 'u' else 1
        H[3 * i + 2, 3 * i + 2] = M[a] @ (q[i, k] - c[i])
    return H


def system(z, rows):
    vals, A, Hs = [], [], []
    for r in rows:
        v, g = row_gj(z, r)
        vals.append(v)
        A.append(g)
        Hs.append(row_hessian(z, r))
    return np.array(vals), (np.array(A) if A else np.zeros((0, NV))), Hs


def check_hessians(z, rows, h=1e-6):
    """max |analytic - central-difference| over the rows (self-test)."""
    worst = 0.0
    for r in rows:
        Ha = row_hessian(z, r)
        Hn = np.zeros((NV, NV))
        for k in range(NV):
            zp, zm = z.copy(), z.copy()
            zp[k] += h
            zm[k] -= h
            Hn[:, k] = (row_gj(zp, r)[1] - row_gj(zm, r)[1]) / (2 * h)
        worst = max(worst, float(np.abs(Ha - Hn).max()))
    return worst


# ---------------------------------------------------------------- LPs
def feasible(A):
    """lam >= 0 with A^T lam = e_s (lam0 = 1); else self-stress A^T lam = 0, sum = 1; else None."""
    m = A.shape[0]
    if m == 0:
        return None, None
    r = linprog(np.ones(m), A_eq=A.T, b_eq=O.E_S, bounds=(0, LP_CAP), method='highs')
    if r.success:
        return np.asarray(r.x), 1.0
    Aeq = np.vstack([A.T, np.ones((1, m))])
    beq = np.concatenate([np.zeros(NV), [1.0]])
    r = linprog(np.zeros(m), A_eq=Aeq, b_eq=beq, bounds=(0, LP_CAP), method='highs')
    if r.success:
        return np.asarray(r.x), 0.0
    return None, None


def min_external(A, coords):
    """min sum |mu| over external unit loads on the listed coordinates, with A^T lam + E mu = e_s,
    lam >= 0.  Returns (lam, mu (len coords), objective) or None."""
    m = A.shape[0]
    k = len(coords)
    E = np.zeros((k, NV))
    for a, cidx in enumerate(coords):
        E[a, cidx] = 1.0
    Aeq = np.hstack([A.T, E.T, -E.T])
    cost = np.concatenate([np.zeros(m), np.ones(2 * k)])
    r = linprog(cost, A_eq=Aeq, b_eq=O.E_S, bounds=(0, LP_CAP), method='highs')
    if not r.success:
        return None
    x = np.asarray(r.x)
    return x[:m], x[m:m + k] - x[m + k:], float(r.fun)


def second_order_value(A, Hs, y, tol=1e-9):
    """v2(y) = min_w  e_s.w  s.t.  grad g_r . w >= - y^T H_r y  for rows with grad g_r . y = 0.
    = max over the multiplier polytope of y^T Hess(L) y (dual).  Returns (value, status, E-rows)."""
    Ay = A @ y
    E = [r for r in range(A.shape[0]) if abs(Ay[r]) <= tol]
    if not E:
        return -float('inf'), 'unbounded', E
    h = np.array([y @ Hs[r] @ y for r in E])
    AE = A[E]
    r = linprog(O.E_S, A_ub=-AE, b_ub=h, bounds=(-LP_CAP, LP_CAP), method='highs')
    if r.status == 3:
        return -float('inf'), 'unbounded', E
    if not r.success:
        return float('nan'), r.message, E
    val = float(r.fun)
    status = 'bounded' if val > -0.5 * LP_CAP else 'unbounded'
    return val, status, E
