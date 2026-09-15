"""A217 crowd rows: every corner box (0,1)^2 met by TWO designated squares with margin delta
(a vertex of each strictly inside the box: u_k <= 1 - delta, v_k <= 1 - delta).  Two meeters with
margin force the corner UNSETTLED (a slot square would overlap the second meeter).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G


def designate(z, k_per=2):
    """per corner the k_per squares whose deepest vertex is deepest in the box, with that vertex."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    out = {}
    for cn in G.CORNER_NAMES:
        M, t, _ = G.corner_frame(cn, s)
        depth = []
        for i in range(G.N):
            uv = q[i] @ M.T + t                            # (4,2)
            d = uv.max(axis=1)                             # max(u,v) per vertex
            k = int(np.argmin(d))
            depth.append((float(d[k]), i, k))
        depth.sort()
        out[cn] = [(i, k) for _, i, k in depth[:k_per]]
    return out


def crowd_rows(z, des, delta):
    """values (16,) and jacobian (16,34) of g = 1 - delta - u_k(q) >= 0 and the same for v."""
    cx, cy, th, s = G.unpack(z)
    q = G.corners(z)
    c = np.stack([cx, cy], -1)
    g, J, labels = [], [], []
    for cn in G.CORNER_NAMES:
        M, t, _ = G.corner_frame(cn, s)
        dt_ds = {'BL': (0, 0), 'BR': (1, 0), 'TR': (1, 1), 'TL': (0, 1)}[cn]
        for (i, k) in des[cn]:
            uv = M @ q[i, k] + t
            dq = np.array([-(q[i, k, 1] - c[i, 1]), q[i, k, 0] - c[i, 0]])      # dq/dtheta
            for a in range(2):
                row = np.zeros(G.NV)
                row[3 * i] = -M[a, 0]
                row[3 * i + 1] = -M[a, 1]
                row[3 * i + 2] = -(M[a] @ dq)
                row[G.S_IDX] = -dt_ds[a]
                g.append(1.0 - delta - uv[a])
                J.append(row)
                labels.append({'kind': 'crowd', 'corner': cn, 'i': i, 'vertex': k, 'coord': 'uv'[a]})
    return np.array(g), np.array(J), labels


def make_extra(delta):
    def extra(z):
        des = designate(z)
        return (lambda x: crowd_rows(x, des, delta)[0], lambda x: crowd_rows(x, des, delta)[1])
    return extra


def active_crowd(z, delta, tol=1e-7):
    des = designate(z)
    g, J, labels = crowd_rows(z, des, delta)
    idx = [k for k in range(len(g)) if abs(g[k]) <= tol]
    return [labels[k] for k in idx], J[idx] if idx else np.zeros((0, G.NV))


# ---------------------------------------------------------------- fixed designation (the crowd search)
def designate_fixed(z):
    """per corner the two squares with centres nearest the corner point, distinct across corners
    (greedy over the 8 (corner, square) pairs by distance)."""
    cx, cy, th, s = G.unpack(z)
    pts = {'BL': (0, 0), 'BR': (s, 0), 'TR': (s, s), 'TL': (0, s)}
    cand = sorted((float(np.hypot(cx[i] - px, cy[i] - py)), cn, i)
                  for cn, (px, py) in pts.items() for i in range(G.N))
    out = {cn: [] for cn in G.CORNER_NAMES}
    used = set()
    for d, cn, i in cand:
        if i in used or len(out[cn]) == 2:
            continue
        out[cn].append(i)
        used.add(i)
    return out


def deepest_vertex(z, cn, i):
    cx, cy, th, s = G.unpack(z)
    M, t, _ = G.corner_frame(cn, s)
    uv = G.corners(z)[i] @ M.T + t
    return int(np.argmin(uv.max(axis=1)))


def des_with_vertices(z, desq):
    return {cn: [(i, deepest_vertex(z, cn, i)) for i in desq[cn]] for cn in G.CORNER_NAMES}


def make_extra_fixed(desq, delta):
    def extra(z):
        des = des_with_vertices(z, desq)
        return (lambda x: crowd_rows(x, des, delta)[0], lambda x: crowd_rows(x, des, delta)[1])
    return extra


def active_crowd_fixed(z, desq, delta, tol=1e-7):
    des = des_with_vertices(z, desq)
    g, J, labels = crowd_rows(z, des, delta)
    idx = [k for k in range(len(g)) if abs(g[k]) <= tol]
    return [labels[k] for k in idx], J[idx] if idx else np.zeros((0, G.NV))


def crowd_feasible_start(z0, desq, delta, iters=300):
    """penalty phase (walls + pairs + crowd rows) at fixed s, widening s on failure."""
    from scipy.optimize import minimize
    import opt217 as O

    def pen(z):
        f, grad = O.penalty(z)
        des = des_with_vertices(z, desq)
        g, J, _ = crowd_rows(z, des, delta)
        v = np.minimum(g, 0.0)
        f += float(v @ v)
        grad = grad + 2 * (v @ J)
        grad[G.S_IDX] = 0.0
        return f, grad

    z = np.array(z0, float)
    for _ in range(8):
        r = minimize(pen, z, jac=True, method='L-BFGS-B', options={'maxiter': iters})
        z = r.x
        if r.fun < 1e-20:
            return z, True
        z[G.S_IDX] += 0.3
    return z, False
