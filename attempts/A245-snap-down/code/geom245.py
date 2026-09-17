"""A245 -- n-general square geometry for the SNAP-DOWN tests: poses (cx, cy, theta), exact SAT gaps
between squares and against axis cells, the twelve border cells, the WALL FRAME of each of the four
walls (the wall becomes u = 0, its first corner c the origin, the adjacent corner c' at v = s), and the
wall-pair parametrisation (theta, ell): a square touching u = 0 with its leftmost vertex at (0, ell),
vertices L = (0, ell), V = L + (sin, -cos), R = V + (cos, sin), T = L + (cos, sin), tilt theta in
[0, 90 deg]; at theta = 0 it is [0,1] x [ell-1, ell], at 90 deg [0,1] x [ell, ell+1].
"""
import math

import numpy as np

HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
CORNERS = ('BL', 'BR', 'TR', 'TL')
WALLS = {'x=0': ('BL', 'TL'), 'y=0': ('BR', 'BL'), 'x=s': ('TR', 'BR'), 'y=s': ('TL', 'TR')}
TOL = 1e-9


def verts(p):
    cx, cy, th = p
    co, si = math.cos(th), math.sin(th)
    return np.array([(cx + co * a - si * b, cy + si * a + co * b) for a, b in HALF])


def normals(th):
    co, si = math.cos(th), math.sin(th)
    return np.array([(co, si), (-si, co)])


def _axis_gap(P, Q, n):
    a, b = P @ n, Q @ n
    return max(b.min() - a.max(), a.min() - b.max())


def pair_gap(p, q):
    """max over the four edge-normal axes of the separation; >= 0 iff interior-disjoint."""
    P, Q = verts(p), verts(q)
    return max(_axis_gap(P, Q, n) for n in np.vstack([normals(p[2]), normals(q[2])]))


def rect_verts(r):
    x0, x1, y0, y1 = r
    return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], float)


def rect_gap(p, r):
    """SAT gap between the square and the axis rectangle; < 0 iff their interiors meet (the square
    MEETS the open cell); -gap is the overlap depth of cells244."""
    P, Q = verts(p), rect_verts(r)
    axes = np.vstack([np.eye(2), normals(p[2])])
    return max(_axis_gap(P, Q, n) for n in axes)


def meets(p, r, tol=0.0):
    return rect_gap(p, r) < -tol


def wall_gap(p, s):
    V = verts(p)
    return float(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()))


def check_packing(poses, s, tol=TOL):
    """(ok, min wall gap, min pair gap) -- containment and pairwise interior-disjointness."""
    gw = min(wall_gap(p, s) for p in poses) if poses else 0.0
    gp = min((pair_gap(poses[i], poses[j]) for i in range(len(poses)) for j in range(i + 1, len(poses))),
             default=0.0)
    return bool(gw >= -tol and gp >= -tol), float(gw), float(gp)


# ---------------------------------------------------------------- the twelve border cells
def cell_rect(name, s):
    """cells244's naming: c00 the corner box, c01 up c's wall, c10 along c's floor."""
    c, k = name[:2], name[2:]
    u0, u1, v0, v1 = {'00': (0, 1, 0, 1), '01': (0, 1, 1, 2), '10': (1, 2, 0, 1)}[k]
    if c == 'BL':
        return (u0, u1, v0, v1)
    if c == 'BR':
        return (s - u1, s - u0, v0, v1)
    if c == 'TR':
        return (s - u1, s - u0, s - v1, s - v0)
    return (u0, u1, s - v1, s - v0)


CELLS = tuple('%s%s' % (c, k) for c in CORNERS for k in ('00', '01', '10'))


def meeters(poses, s, tol=0.0):
    return {n: [i for i, p in enumerate(poses) if meets(p, cell_rect(n, s), tol)] for n in CELLS}


def box_meeters(poses, s, corner, tol=0.0):
    return meeters_of(poses, cell_rect(corner + '00', s), tol)


def meeters_of(poses, r, tol=0.0):
    return [i for i, p in enumerate(poses) if meets(p, r, tol)]


# ---------------------------------------------------------------- wall frames
def _frame_maps(wall, s):
    """(M, t): frame point = M @ global + t; the wall is u = 0, its first corner the origin."""
    if wall == 'x=0':                       # BL -> TL along v
        return np.eye(2), np.zeros(2)
    if wall == 'y=0':                       # BR at the origin, BL at v = s: u = y, v = s - x
        return np.array([[0.0, 1.0], [-1.0, 0.0]]), np.array([0.0, s])
    if wall == 'x=s':                       # TR at the origin, BR at v = s: u = s - x, v = s - y
        return -np.eye(2), np.array([s, s])
    if wall == 'y=s':                       # TL at the origin, TR at v = s: u = s - y, v = x
        return np.array([[0.0, -1.0], [1.0, 0.0]]), np.array([s, 0.0])
    raise ValueError(wall)


def pose_from_verts(V):
    c = V.mean(axis=0)
    e = V[1] - V[0]
    th = math.atan2(e[1], e[0]) % (math.pi / 2)
    return (float(c[0]), float(c[1]), float(th))


def to_frame(pose, wall, s):
    M, t = _frame_maps(wall, s)
    return pose_from_verts(verts(pose) @ M.T + t)


def from_frame(pose, wall, s):
    M, t = _frame_maps(wall, s)
    return pose_from_verts((verts(pose) - t) @ np.linalg.inv(M).T)


def wall_cells(s):
    """the wall's cells in its frame: c00, c01, c'01, c'00 and the third column cell c02."""
    return {'c00': (0, 1, 0, 1), 'c01': (0, 1, 1, 2), "c'01": (0, 1, s - 2, s - 1),
            "c'00": (0, 1, s - 1, s), 'c02': (0, 1, 2, 3)}


def wall_names(wall):
    """(c, c') and the global cell names of the wall's four cells in frame order."""
    c, cp = WALLS[wall]
    k = '01' if wall in ('x=0', 'x=s') else '10'
    return c, cp, (c + '00', c + k, cp + k, cp + '00')


# ---------------------------------------------------------------- the wall-pair parametrisation
def wall_pose(th, ell):
    """the square touching u = 0 with leftmost vertex (0, ell) and tilt th in [0, pi/2]."""
    co, si = math.cos(th), math.sin(th)
    return ((si + co) / 2, ell + (si - co) / 2, th)


def wall_params(pose, tol=1e-6):
    """(theta, ell) of a pose touching u = 0 (its leftmost vertex is on the wall); a flat square is
    [0,1] x [ell-1, ell] at theta = 0 and [0,1] x [ell, ell+1] at theta = 90 deg."""
    V = verts(pose)
    th = pose[2] % (math.pi / 2)
    if th <= tol:
        return 0.0, float(V[:, 1].max())
    if th >= math.pi / 2 - tol:
        return math.pi / 2, float(V[:, 1].min())
    k = int(np.argmin(V[:, 0]))
    return th, float(V[k, 1])


def handedness(th, tol=1e-6):
    phi = th % (math.pi / 2)
    if min(phi, math.pi / 2 - phi) <= tol:
        return 'F'
    if abs(phi - math.pi / 4) <= 1e-7:
        return 'D'
    return '+' if phi < math.pi / 4 else '-'


def extent(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def chord(th):
    """WALL-EXCESS's chord of a wall toucher: 1 / max(cos, sin) >= 1."""
    return 1.0 / max(abs(math.cos(th)), abs(math.sin(th)))
