"""A248: the corner chase -- n-general geometry of a corner crowd seen from one of its walls.

WALL FRAME (A245): the shared wall is u = 0, the lower corner c at the origin, the upper corner c'
at (0, s); all four frames are ROTATIONS of the container (tilt sense preserved).  Cells in the
frame: c00 = (0,1)^2, c01 = (0,1)x(1,2) up the wall, c10 = (1,2)x(0,1) along c's floor,
c'00 = (0,1)x(s-1,s), c'01 = (0,1)x(s-2,s-1), c'10 = (1,2)x(s-1,s).
A square is handled by its four vertices (4x2 array); the frame tilt of a square is the angle of
its edge leaving its lowest vertex (in [0, 90) degrees).
POKER beside a flat floor meeter A = [delta, 1+delta] x [0,1]: a tilted square B touching u = 0
with wall vertex L = (0, ell), lowest vertex V = L + (sin t, -cos t), R = V + (cos t, sin t),
T = L + (cos t, sin t) (A245's wall_pose).  Depth of B at c: d = 1 - mu, mu = min over B of
max(u, v) (A233's depthC); for the poker mu <= 1 - d_V with d_V = 1 - y_V.
"""
import math
from fractions import Fraction

import numpy as np

HALF = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))
WALLS = ('x=0', 'y=s', 'x=s', 'y=0')                      # ring order of the walls
WALL_CORNERS = {'x=0': ('BL', 'TL'), 'y=s': ('TL', 'TR'), 'x=s': ('TR', 'BR'), 'y=0': ('BR', 'BL')}
TOL = 1e-9


# ---------------------------------------------------------------- squares
def verts(pose):
    cx, cy, th = pose
    co, si = math.cos(th), math.sin(th)
    return np.array([(cx + co * a - si * b, cy + si * a + co * b) for a, b in HALF])


def edge_normals(V):
    e = np.roll(V, -1, axis=0) - V
    n = np.stack([e[:, 1], -e[:, 0]], axis=1)
    return n / np.linalg.norm(n, axis=1)[:, None]


def axis_gap(P, Q, n):
    a, b = P @ n, Q @ n
    return max(b.min() - a.max(), a.min() - b.max())


def poly_gap(P, Q):
    """SAT gap of two convex polygons (vertex arrays); >= 0 iff interior-disjoint; -gap = depth."""
    return max(axis_gap(P, Q, n) for n in np.vstack([edge_normals(P), edge_normals(Q)]))


def rect_verts(r):
    x0, x1, y0, y1 = r
    return np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], float)


def depth_rect(V, r):
    """overlap depth of the square V against the open axis cell r: > 0 iff they meet."""
    return -poly_gap(V, rect_verts(r))


def pose_of(V):
    c = V.mean(axis=0)
    e = V[1] - V[0]
    return (float(c[0]), float(c[1]), math.atan2(e[1], e[0]) % (math.pi / 2))


# ---------------------------------------------------------------- frames
def to_wall(V, wall, s):
    x, y = V[:, 0], V[:, 1]
    if wall == 'x=0':
        u, v = x, y
    elif wall == 'y=s':
        u, v = s - y, x
    elif wall == 'x=s':
        u, v = s - x, s - y
    else:
        u, v = y, s - x
    return np.stack([u, v], axis=1)


def from_wall(V, wall, s):
    u, v = V[:, 0], V[:, 1]
    if wall == 'x=0':
        x, y = u, v
    elif wall == 'y=s':
        x, y = v, s - u
    elif wall == 'x=s':
        x, y = s - u, s - v
    else:
        x, y = s - v, u
    return np.stack([x, y], axis=1)


def flip_up(V, s):
    """the upper corner c' seen as a lower corner: (u, v) -> (u, s - v) (a reflection)."""
    return np.stack([V[:, 0], s - V[:, 1]], axis=1)


def cells(s):
    return {'c00': (0, 1, 0, 1), 'c01': (0, 1, 1, 2), 'c10': (1, 2, 0, 1),
            "c'00": (0, 1, s - 1, s), "c'01": (0, 1, s - 2, s - 1), "c'10": (1, 2, s - 1, s)}


# ---------------------------------------------------------------- the corner depth
def mu_corner(V):
    """min over the (convex) square of max(u, v): the vertices and the diagonal crossings."""
    best = float(np.max(V, axis=1).min())
    for k in range(4):
        p, q = V[k], V[(k + 1) % 4]
        fp, fq = p[0] - p[1], q[0] - q[1]
        if fp * fq < 0:
            t = fp / (fp - fq)
            best = min(best, float(p[0] + t * (q[0] - p[0])))
    return best


def depth_corner(V):
    return max(0.0, 1.0 - mu_corner(V))


# ---------------------------------------------------------------- the poker beside a flat meeter
def flat_floor(delta):
    return np.array([(delta, 0.0), (delta + 1, 0.0), (delta + 1, 1.0), (delta, 1.0)])


def poker(theta, d, x_v=None):
    """the tilted square with lowest vertex V = (x_v, 1 - d) (x_v = sin theta: touching the wall)
    and frame tilt theta (radians, 0 < theta < pi/2)."""
    si, co = math.sin(theta), math.cos(theta)
    xv = si if x_v is None else x_v
    V = np.array([xv, 1.0 - d])
    return np.array([V, V + (co, si), V + (co - si, si + co), V + (-si, co)])


def frame_tilt(V):
    """angle (radians in [0, pi/2)) of the edge leaving the lowest vertex, and that vertex."""
    k = int(np.argmin(V[:, 1] + 1e-12 * V[:, 0]))
    e1, e2 = V[(k + 1) % 4] - V[k], V[k - 1] - V[k]
    e = e1 if e1[0] >= e2[0] else e2
    return math.atan2(e[1], e[0]) % (math.pi / 2), V[k]


def poke_facts(B, A_delta):
    """POKE's true content for a square B beside the flat floor meeter at offset delta:
    the sense (CCW: lowest vertex nearer the wall than the highest; CW otherwise), the frame
    tilt, sin theta <= x_v <= delta, TILT-MIN's depth bound and the top-vertex height."""
    th, V = frame_tilt(B)
    top = B[int(np.argmax(B[:, 1]))]
    d_v = 1.0 - float(V[1])
    tan = math.tan(th) if th < math.pi / 2 - 1e-12 else float('inf')
    return {'theta_deg': math.degrees(th), 'x_v': float(V[0]), 'y_v': float(V[1]),
            'sense': 'CCW' if V[0] < top[0] else 'CW', 'top': float(top[1]), 'x_top': float(top[0]),
            'd_v': d_v, 'tiltmin_bound': (A_delta - float(V[0])) * tan,
            'sin_le_delta': math.sin(th) <= A_delta + TOL,
            'top_ge_2': float(top[1]) >= 2.0 - 1e-9}


def w(theta):
    return abs(math.cos(theta)) + abs(math.sin(theta))


# ---------------------------------------------------------------- the POKE witness (exact)
def poke_witness_exact():
    """B with cos = 3/5, sin = 4/5 (theta = 53.13 deg > 45: the CW sense), lowest vertex
    (4/5, 9/10), beside A = [19/20, 39/20] x [0, 1]: exact rational checks."""
    F = Fraction
    co, si, d = F(3, 5), F(4, 5), F(1, 10)
    delta = F(19, 20)
    V = (si, 1 - d)
    R = (V[0] + co, V[1] + si)
    T = (V[0] + co - si, V[1] + si + co)
    L = (V[0] - si, V[1] + co)
    facts = {'L': L, 'V': V, 'R': R, 'T': T, 'delta': delta}
    # B's part below height 1 lies under the edge V->R: abscissa at height 1 is x_V + (1-y_V) cot
    x_at_1 = V[0] + (1 - V[1]) * co / si
    facts['edge_VR_at_height_1'] = x_at_1
    facts['disjoint_from_A'] = x_at_1 <= delta          # and B's other points are above height 1
    facts['touches_wall'] = L[0] == 0
    facts['V_in_box'] = 0 < V[0] < 1 and 0 < V[1] < 1
    facts['lowest_nearer_wall_than_highest'] = V[0] < T[0]   # POKE's directional claim
    facts['top_ge_2'] = T[1] >= 2
    return facts


# ---------------------------------------------------------------- FLAT-ABOVE, the click
def flat_above_violation(top_B, x_top, y0):
    """a flat wall square [0,1] x [y0, y0+1] above the poker needs top_B <= y0 (x_top < 1);
    returns the slack y0 - top_B (< 0: overlap)."""
    return y0 - top_B if x_top < 1 - TOL else float('nan')


def click_gain(d, d_up, s):
    """Psi(new) - Psi(old) of the flush stack [0,1]x[1,3] replacing the wall pair (B, B'):
    B leaves c00, the flush B' meets c'00 to depth (4 - s)^+ (below 4)."""
    return max(0.0, 4.0 - s) - d - d_up


def window_blockers(polys, skip, s, y0=1.0):
    """indices of squares (not in skip) whose interior meets the window [0,1] x [y0, y0+2]."""
    W = rect_verts((0.0, 1.0, y0, y0 + 2.0))
    return [i for i, P in enumerate(polys) if i not in skip and poly_gap(P, W) < -TOL]


def touches(V, line, s, tol=1e-7):
    """does the square touch the wall u = 0 ('u'), the floor v = 0 ('v') or the ceiling v = s?"""
    if line == 'u':
        return float(V[:, 0].min()) < tol
    if line == 'v':
        return float(V[:, 1].min()) < tol
    return float(s - V[:, 1].max()) < tol


def is_flat(V, tol=1e-7):
    th, _ = frame_tilt(V)
    return min(th, math.pi / 2 - th) < tol
