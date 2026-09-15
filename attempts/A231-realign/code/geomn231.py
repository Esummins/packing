"""A231 n-general geometry for the anchored re-alignment: poses = list of (cx, cy, theta) unit squares in [0, s]^2.
Separating-axis tables per pair, the selection (owner, edge) per pair, the fixed-tilt side LP of Lemma GRAIN-LP
(rows affine in the centres at fixed tilts; pinned squares held by equality rows), contacts, handedness, corner
meeters (open unit corner box), and the exact check (min SAT gap, min wall row).  No n = 11 assumption anywhere.
"""
import math

import numpy as np
from scipy.optimize import linprog

HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])
CORNERS = ('BL', 'BR', 'TR', 'TL')
S_MAX = 40.0


def arrays(poses):
    p = np.asarray(poses, float).reshape(-1, 3)
    return p[:, 0], p[:, 1], p[:, 2]


def corners(poses):
    cx, cy, th = arrays(poses)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    hx, hy = HALF[None, :, 0], HALF[None, :, 1]
    return np.stack([cx[:, None] + co * hx - si * hy, cy[:, None] + si * hx + co * hy], -1)


def normals(poses):
    cx, cy, th = arrays(poses)
    co, si = np.cos(th)[:, None], np.sin(th)[:, None]
    nx, ny = NHAT[None, :, 0], NHAT[None, :, 1]
    return np.stack([co * nx - si * ny, si * nx + co * ny], -1)


def pairs_of(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def sat_tables(poses):
    """(P, 2, 4, 4) projections n_e(owner).(q_k(other) - c_owner) - 1/2 for every pair (owner 0 = i, 1 = j)."""
    q, nrm = corners(poses), normals(poses)
    cx, cy, _ = arrays(poses)
    c = np.stack([cx, cy], -1)
    n = len(cx)
    I, J = np.array([(i, j) for i in range(n) for j in range(i + 1, n)]).T if n > 1 else (np.array([], int),) * 2
    pi = np.einsum('ped,pkd->pek', nrm[I], q[J] - c[I][:, None, :]) - 0.5
    pj = np.einsum('ped,pkd->pek', nrm[J], q[I] - c[J][:, None, :]) - 0.5
    return np.stack([pi, pj], 1), list(zip(I.tolist(), J.tolist()))


def select(poses, fixed=None):
    """best separating axis per pair: sel[(i, j)] = (owner, edge), gaps[(i, j)] = its min-corner gap; pairs in `fixed`
    keep the given (owner, edge) (their gap is then the gap ON that axis)."""
    fixed = fixed or {}
    tab, prs = sat_tables(poses)
    sel, gaps = {}, {}
    for p, (i, j) in enumerate(prs):
        t = tab[p]
        if (i, j) in fixed:
            o, e = fixed[(i, j)]
            sel[(i, j)] = (o, e)
            gaps[(i, j)] = float(t[0 if o == i else 1, e].min())
            continue
        mm = t.min(axis=2)
        oi, e = np.unravel_index(np.argmax(mm), mm.shape)
        sel[(i, j)] = (i if oi == 0 else j, int(e))
        gaps[(i, j)] = float(mm[oi, e])
    return sel, gaps


def pair_gaps(poses):
    return select(poses)[1]


def wall_min(poses, s):
    q = corners(poses)
    return float(min(q[..., 0].min(), q[..., 1].min(), s - q[..., 0].max(), s - q[..., 1].max()))


def check(poses, s, tol=1e-6):
    """exact check of a configuration: (ok, min pair gap, min wall row)."""
    gap = min(pair_gaps(poses).values()) if len(poses) > 1 else 1.0
    wall = wall_min(poses, s)
    return (gap >= -tol and wall >= -tol), gap, wall


def wfun(nv, th):
    return abs(nv[0] * math.cos(th) + nv[1] * math.sin(th)) + abs(-nv[0] * math.sin(th) + nv[1] * math.cos(th))


def slot_pin(corner):
    """the slot-square centre at a corner as (ax, bx, ay, by): c = a + b*s per coordinate."""
    return {'BL': (0.5, 0, 0.5, 0), 'BR': (-0.5, 1, 0.5, 0), 'TR': (-0.5, 1, -0.5, 1), 'TL': (0.5, 0, -0.5, 1)}[corner]


def lp(th, sel, pins):
    """min s over the centres at tilts th (array), selection sel {(i, j): (owner, edge)}, pins {i: corner name}
    (equality rows: the pinned square sits at the corner slot).  Returns (centres (n, 2), s) or None."""
    n = len(th)
    nv = 2 * n + 1
    A, b = [], []
    for i in range(n):
        w = (abs(math.cos(th[i])) + abs(math.sin(th[i]))) / 2
        for k in range(2):
            r = np.zeros(nv); r[2 * i + k] = -1.0; A.append(r); b.append(-w)
            r = np.zeros(nv); r[2 * i + k] = 1.0; r[-1] = -1.0; A.append(r); b.append(-w)
    for (i, j), (o, e) in sel.items():
        p = j if o == i else i
        nn = NHAT[e]
        co, si = math.cos(th[o]), math.sin(th[o])
        nn = np.array([co * nn[0] - si * nn[1], si * nn[0] + co * nn[1]])
        rhs = (1 + wfun(nn, th[p])) / 2
        r = np.zeros(nv)
        r[2 * p:2 * p + 2] = -nn
        r[2 * o:2 * o + 2] = nn
        A.append(r); b.append(-rhs)
    Aeq, beq = [], []
    for i, cn in pins.items():
        ax, bx, ay, by = slot_pin(cn)
        r = np.zeros(nv); r[2 * i] = 1.0; r[-1] = -bx; Aeq.append(r); beq.append(ax)
        r = np.zeros(nv); r[2 * i + 1] = 1.0; r[-1] = -by; Aeq.append(r); beq.append(ay)
    cost = np.zeros(nv); cost[-1] = 1.0
    res = linprog(cost, A_ub=np.array(A), b_ub=np.array(b), A_eq=np.array(Aeq) if Aeq else None,
                  b_eq=np.array(beq) if beq else None, bounds=[(0, S_MAX)] * (nv - 1) + [(1, S_MAX)], method='highs')
    if not res.success:
        return None
    return res.x[:-1].reshape(n, 2), float(res.x[-1])


def poses_at(c, th):
    return [(float(c[i, 0]), float(c[i, 1]), float(th[i])) for i in range(len(th))]


def fixed_tilt_min(poses, th, fixed, pins, iters=8):
    """alternating LP at tilts th from the centres of `poses`: returns (poses', s, sel, k) or (None, None, sel, k)."""
    cur = poses_at(np.array([[p[0], p[1]] for p in poses]), th)
    sel, _ = select(cur, fixed)
    best = None
    for k in range(iters):
        r = lp(th, sel, pins)
        if r is None:
            return (None, None, sel, k) if best is None else best + (k,)
        c, s = r
        cur = poses_at(c, th)
        if best is None or s < best[1] - 1e-10:
            best = (cur, s, sel)
        sel2, _ = select(cur, fixed)
        if sel2 == sel:
            break
        sel = sel2
    return best + (k + 1,)


def contacts(poses, tol=1e-6):
    """pairs in contact (SAT gap <= tol) with their separating axis."""
    sel, gaps = select(poses)
    return {pr: sel[pr] for pr, g in gaps.items() if g <= tol}


def handedness(theta, tol=1e-6):
    phi = theta % (math.pi / 2)
    if min(phi, math.pi / 2 - phi) <= tol:
        return 'F'
    if abs(phi - math.pi / 4) <= 1e-7:
        return 'D'
    return '+' if phi < math.pi / 4 else '-'


def phi_deg(theta):
    return math.degrees(theta % (math.pi / 2))


def frame_pts(pts, corner, s):
    x, y = pts[..., 0], pts[..., 1]
    u = x if corner in ('BL', 'TL') else s - x
    v = y if corner in ('BL', 'BR') else s - y
    return np.stack([u, v], -1)


def meets_corner(poses, i, corner, s, size=1.0, tol=1e-9):
    """does the interior of square i meet the open box (0, size)^2 at the corner?  SAT of square vs box."""
    q = frame_pts(corners(poses)[i], corner, s)
    if q[:, 0].max() <= tol or q[:, 0].min() >= size - tol or q[:, 1].max() <= tol or q[:, 1].min() >= size - tol:
        return False
    th = poses[i][2]
    sgn = 1.0 if corner in ('BL', 'TR') else -1.0                      # reflections flip the tilt sense
    c = q.mean(0)
    box = np.array([(0, 0), (size, 0), (size, size), (0, size)], float)
    for e in range(4):
        co, si = math.cos(sgn * th), math.sin(sgn * th)
        nn = np.array([co * NHAT[e][0] - si * NHAT[e][1], si * NHAT[e][0] + co * NHAT[e][1]])
        if (nn @ (box - c).T).min() >= 0.5 - tol:
            return False
    return True


def corner_meeters(poses, s, corner):
    return [i for i in range(len(poses)) if meets_corner(poses, i, corner, s)]


def settled_at(poses, corner, s, tol=1e-6):
    ax, bx, ay, by = slot_pin(corner)
    for i, (cx, cy, th) in enumerate(poses):
        phi = th % (math.pi / 2)
        if min(phi, math.pi / 2 - phi) <= tol and abs(cx - (ax + bx * s)) <= tol and abs(cy - (ay + by * s)) <= tol:
            return i
    return None


def wall_touchers(poses, s, tol=1e-6):
    """per square the walls it touches ('x=0', 'y=0', 'x=s', 'y=s')."""
    q = corners(poses)
    out = []
    for i in range(len(poses)):
        w = []
        if q[i, :, 0].min() <= tol: w.append('x=0')
        if q[i, :, 1].min() <= tol: w.append('y=0')
        if q[i, :, 0].max() >= s - tol: w.append('x=s')
        if q[i, :, 1].max() >= s - tol: w.append('y=s')
        out.append(w)
    return out
