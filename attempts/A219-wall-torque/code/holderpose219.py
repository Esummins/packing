"""A219 one-holder poses: put a free square R against a target meeter M so that the contact force on M
points along the wanted direction d (the external load ring219 found necessary), and price every pose by the
minimal external load (forces + torques, all squares) of the free FJ system with R's new contact rows added.
Type 1: R's vertex on M's edge (force on M = minus M's outward edge normal; the edge nearest -d);
type 2: M's rearmost vertex (min d.q) on R's edge whose outward normal is exactly d.
"""
import math

import numpy as np

import geom217 as G
import opt217 as O
import rows219 as R

TOL = 1e-9


def place(z, i, cx, cy, th):
    z2 = np.array(z, float)
    z2[3 * i], z2[3 * i + 1], z2[3 * i + 2] = cx, cy, th
    return z2


def pose_feasible(z2, i, ignore=()):
    """square i inside the container and interior-disjoint from every other square (SAT gap >= -1e-9),
    the squares in `ignore` (other free squares, relocated afterwards) excepted."""
    gw = G.wall_rows(z2)[0].reshape(G.N, 4, 4)[i]
    if gw.min() < -TOL:
        return False
    table = G.sat_table(z2)
    for j in range(G.N):
        if j == i or j in ignore:
            continue
        t = table[(min(i, j), max(i, j))]
        if t.min(axis=2).max() < -TOL:
            return False
    return True


def slots(z, i, ignore=(), grid=14, tilts=(0.0, 15.0, 30.0, 45.0, 60.0, 75.0)):
    """feasible poses (cx, cy, th) of square i in the container, ignoring the squares in `ignore`."""
    s = z[G.S_IDX]
    out = []
    for tdeg in tilts:
        th = math.radians(tdeg)
        hw = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
        for cx in np.linspace(hw, s - hw, grid):
            for cy in np.linspace(hw, s - hw, grid):
                if pose_feasible(place(z, i, cx, cy, th), i, ignore):
                    out.append((float(cx), float(cy), float(th)))
    return out


def relocate(z2, i, slot_list):
    """keep square i where it is if feasible, else the first slot that is; None if none."""
    if pose_feasible(z2, i):
        return z2
    for cx, cy, th in slot_list:
        z3 = place(z2, i, cx, cy, th)
        if pose_feasible(z3, i):
            return z3
    return None


def poses(z, M, Rq, d, tilt_step_deg=15.0, u_steps=(0.2, 0.5, 0.8), ignore=()):
    """list of (z2, desc) for holder Rq against meeter M with wanted force direction d (unit); the
    squares in `ignore` may overlap the pose (they are relocated by the caller)."""
    d = np.asarray(d, float) / np.linalg.norm(d)
    q = G.corners(z)
    n = G.normals(z)
    out = []
    # type 1: R's vertex k on M's edge e, e the edge whose inward normal -n_e best matches d
    e = int(np.argmax([-(n[M, e_] @ d) for e_ in range(4)]))
    if -(n[M, e] @ d) > 0.2:
        a, b = q[M, e], q[M, (e + 1) % 4]
        for u in u_steps:
            P = a + u * (b - a)
            for tdeg in np.arange(0.0, 90.0, tilt_step_deg):
                th = math.radians(tdeg)
                c, s_ = math.cos(th), math.sin(th)
                for k in range(4):
                    hx, hy = G.HALF[k]
                    vk = np.array([c * hx - s_ * hy, s_ * hx + c * hy])
                    cen = P - vk
                    if (cen - P) @ n[M, e] <= 0.0:          # R must sit outside M's edge
                        continue
                    z2 = place(z, Rq, cen[0], cen[1], th)
                    if pose_feasible(z2, Rq, ignore):
                        out.append((z2, {'type': 1, 'edge_of_M': e, 'u': float(u), 'tilt_deg': float(tdeg), 'vertex_of_R': k}))
    # type 2: M's rearmost vertex v (min d.q) on R's edge with outward normal d
    v = q[M, int(np.argmin(q[M] @ d))]
    ang = math.atan2(d[1], d[0])
    th = ang % (math.pi / 2)                                 # edge normal angle theta + f*90deg = ang for some f
    dperp = np.array([-d[1], d[0]])
    for t in np.linspace(-0.4, 0.4, 5):
        cen = v - 0.5 * d + t * dperp
        z2 = place(z, Rq, cen[0], cen[1], th)
        if pose_feasible(z2, Rq, ignore):
            out.append((z2, {'type': 2, 'u': float(t), 'tilt_deg': math.degrees(th)}))
    return out


def evaluate(z2, tol=1e-7):
    """free FJ system at z2 (walls + pair rows): feasible? else the minimal external force+torque load."""
    rows, A = O.active_rows(z2, tol)
    if A.shape[0] == 0:
        return {'feasible': None, 'objective': float('inf'), 'n_rows': 0}
    lam, lam0 = R.feasible(A)
    out = {'feasible': 'lam0=1' if lam0 == 1.0 else ('self-stress' if lam0 == 0.0 else 'INFEASIBLE'), 'n_rows': len(rows)}
    r = R.min_external(A, [3 * i + a for i in range(G.N) for a in range(3)])
    if r is None:
        out['objective'] = float('inf')
        return out
    lamF, mu, obj = r
    out['objective'] = obj
    out['per_square'] = {i: [float(v) for v in mu[3 * i:3 * i + 3]] for i in range(G.N) if np.abs(mu[3 * i:3 * i + 3]).max() > 1e-7}
    return out


def doubly_met_open(z):
    n2 = 0
    for cn in G.CORNER_NAMES:
        if G.settled(z, cn) is None and len(G.corner_meeters(z, cn)) >= 2:
            n2 += 1
    return n2
