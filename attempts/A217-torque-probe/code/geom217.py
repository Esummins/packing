"""A217 geometry: vectorised rows for 11 unit squares in [0,s]^2.
Coordinates (A22/A37/A44 order): z[3i]=cx, z[3i+1]=cy, z[3i+2]=theta (radians), z[33]=s.
Rows are written g >= 0.  Wall rows: 4 walls x 11 squares x 4 corners (176).
Pair rows for a selection (owner o, edge e, other p): g_k = n_e(th_o).(q_k(p) - c_o) - 1/2, k = 0..3.
The theta-component of a row gradient IS the torque of the row's force about the square's centre.
"""
import math
import numpy as np

N = 11
NV = 34
S_IDX = 33
HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]


def unpack(z):
    c = np.asarray(z, float)[:33].reshape(N, 3)
    return c[:, 0], c[:, 1], c[:, 2], float(z[S_IDX])


def corners(z):
    """(11,4,2) corner positions."""
    cx, cy, th, s = unpack(z)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    hx, hy = HALF[None, :, 0], HALF[None, :, 1]
    return np.stack([cx[:, None] + co * hx - si * hy, cy[:, None] + si * hx + co * hy], -1)


def normals(z):
    """(11,4,2) outward edge normals n_e(th)."""
    cx, cy, th, s = unpack(z)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    nx, ny = NHAT[None, :, 0], NHAT[None, :, 1]
    return np.stack([co * nx - si * ny, si * nx + co * ny], -1)


def wall_rows(z):
    """Values (176,) and jacobian (176,34) of all corner-wall containment rows.
    Order: for i, for k, for wall in WALLS."""
    cx, cy, th, s = unpack(z)
    q = corners(z)
    r = q - np.stack([cx, cy], -1)[:, None, :]          # q - c
    dq = np.stack([-r[..., 1], r[..., 0]], -1)          # dq/dtheta = J (q - c)
    g = np.zeros((N, 4, 4))
    J = np.zeros((N, 4, 4, NV))
    for i in range(N):
        for k in range(4):
            g[i, k, 0] = q[i, k, 0]
            g[i, k, 1] = q[i, k, 1]
            g[i, k, 2] = s - q[i, k, 0]
            g[i, k, 3] = s - q[i, k, 1]
            J[i, k, 0, 3 * i] = 1.0
            J[i, k, 0, 3 * i + 2] = dq[i, k, 0]
            J[i, k, 1, 3 * i + 1] = 1.0
            J[i, k, 1, 3 * i + 2] = dq[i, k, 1]
            J[i, k, 2, 3 * i] = -1.0
            J[i, k, 2, 3 * i + 2] = -dq[i, k, 0]
            J[i, k, 2, S_IDX] = 1.0
            J[i, k, 3, 3 * i + 1] = -1.0
            J[i, k, 3, 3 * i + 2] = -dq[i, k, 1]
            J[i, k, 3, S_IDX] = 1.0
    return g.reshape(-1), J.reshape(-1, NV)


def sat_table(z):
    """proj[(i,j)] -> (2,4,4): [owner index (0 = i, 1 = j)][edge][corner of other] projections
    n_e(owner).(q_k(other) - c_owner) - 1/2."""
    cx, cy, th, s = unpack(z)
    q = corners(z)
    n = normals(z)
    c = np.stack([cx, cy], -1)
    out = {}
    for (i, j) in PAIRS:
        pi = np.einsum('ed,kd->ek', n[i], q[j] - c[i]) - 0.5      # (4 edges of i, 4 corners of j)
        pj = np.einsum('ed,kd->ek', n[j], q[i] - c[j]) - 0.5
        out[(i, j)] = np.stack([pi, pj])
    return out


def best_selection(z, table=None):
    """For every pair the separating axis (owner, edge) with the largest min-corner gap.
    Returns dict pair -> (o, e, p) and the gap."""
    if table is None:
        table = sat_table(z)
    sel, gaps = {}, {}
    for (i, j) in PAIRS:
        t = table[(i, j)]
        m = t.min(axis=2)                       # (2,4)
        a, e = np.unravel_index(np.argmax(m), m.shape)
        o, p = (i, j) if a == 0 else (j, i)
        sel[(i, j)] = (int(o), int(e), int(p))
        gaps[(i, j)] = float(m[a, e])
    return sel, gaps


def pair_rows(z, sel):
    """Values (4*55,) and jacobian for the selected axis rows, 4 corners each."""
    cx, cy, th, s = unpack(z)
    q = corners(z)
    n = normals(z)
    c = np.stack([cx, cy], -1)
    g = np.zeros((len(PAIRS), 4))
    J = np.zeros((len(PAIRS), 4, NV))
    for a, (i, j) in enumerate(PAIRS):
        o, e, p = sel[(i, j)]
        nn = n[o, e]
        Jn = np.array([-nn[1], nn[0]])
        for k in range(4):
            r = q[p, k] - c[o]
            g[a, k] = nn @ r - 0.5
            rp = q[p, k] - c[p]
            J[a, k, 3 * p] = nn[0]
            J[a, k, 3 * p + 1] = nn[1]
            J[a, k, 3 * p + 2] = nn[0] * (-rp[1]) + nn[1] * rp[0]      # n . J(q-c_p) = (q-c_p) x n
            J[a, k, 3 * o] = -nn[0]
            J[a, k, 3 * o + 1] = -nn[1]
            J[a, k, 3 * o + 2] = Jn @ r                                # = -(r x n)
    return g.reshape(-1), J.reshape(-1, NV)


def pair_gaps(z):
    """55 SAT gaps (max over 8 axes of min over corners); >= 0 iff interior-disjoint."""
    _, gaps = best_selection(z)
    return gaps


def wrap_theta(z, lo=0.0):
    """theta -> theta mod pi/2 into [lo, lo + pi/2) -- same squares."""
    z = np.array(z, float)
    for i in range(N):
        z[3 * i + 2] = lo + (z[3 * i + 2] - lo) % (math.pi / 2)
    return z


# ---------------------------------------------------------------- corners of the container
CORNER_NAMES = ('BL', 'BR', 'TR', 'TL')


def corner_frame(name, s):
    """Map global (x,y) -> corner frame (u,v) = distances from the two walls of the corner.
    Returns (M, t, det): (u,v) = M (x,y) + t.  BL: identity (det +1); BR: u = s - x, v = y (det -1);
    TR: u = s - x, v = s - y (det +1, rotation by pi); TL: u = x, v = s - y (det -1).
    A torque measured in the frame is det * (global torque)."""
    if name == 'BL':
        return np.eye(2), np.zeros(2), 1
    if name == 'BR':
        return np.array([[-1.0, 0], [0, 1.0]]), np.array([s, 0.0]), -1
    if name == 'TR':
        return -np.eye(2), np.array([s, s]), 1
    if name == 'TL':
        return np.array([[1.0, 0], [0, -1.0]]), np.array([0.0, s]), -1
    raise ValueError(name)


def slot_centre(name, s):
    return {'BL': (0.5, 0.5), 'BR': (s - 0.5, 0.5), 'TR': (s - 0.5, s - 0.5), 'TL': (0.5, s - 0.5)}[name]


def axis_dev(th):
    """distance of theta from the nearest multiple of pi/2."""
    m = th % (math.pi / 2)
    return min(m, math.pi / 2 - m)


def settled(z, name, tol=1e-6):
    """index of the slot square at corner `name`, or None."""
    cx, cy, th, s = unpack(z)
    sx, sy = slot_centre(name, s)
    for i in range(N):
        if axis_dev(th[i]) <= tol and abs(cx[i] - sx) <= tol and abs(cy[i] - sy) <= tol:
            return i
    return None


def meets_box(z, i, name, size=1.0):
    """Does the interior of square i meet the open corner box (0,size)^2 of corner `name`?
    SAT between the square and the axis box."""
    cx, cy, th, s = unpack(z)
    M, t, _ = corner_frame(name, s)
    q = corners(z)[i] @ M.T + t                     # square corners in the frame
    n = normals(z)[i] @ M.T
    c = M @ np.array([cx[i], cy[i]]) + t
    box = np.array([(0, 0), (size, 0), (size, size), (0, size)], float)
    tol = 1e-9
    if q[:, 0].max() <= tol or q[:, 0].min() >= size - tol or q[:, 1].max() <= tol or q[:, 1].min() >= size - tol:
        return False
    for e in range(4):
        if (n[e] @ (box - c).T).min() >= 0.5 - tol:
            return False
    return True


def corner_meeters(z, name, size=1.0):
    return [i for i in range(N) if meets_box(z, i, name, size)]
