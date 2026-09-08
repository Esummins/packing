"""A107 shared library: geometry (SAT gaps, incidence Jacobians), D4 symmetry, slot naming, shadow
extraction / de-duplication. READ-ONLY on every campaign's files."""
import math, json, os, glob
import numpy as np

S0 = 969271.0 / 250000.0           # 3.877084, the certified side
SHAT = 3.877083590022814           # s-hat

# ---------------------------------------------------------------- geometry
def corners(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]

def sat_gap(c1, t1, c2, t2):
    """Separation gap between two unit squares (>0 disjoint, <0 overlap). Max over the 4 axis
    directions of (centre distance along axis) - 0.5 - 0.5*(support of the other square)."""
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) + abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot))
            best = max(best, d - 0.5 - 0.5 * g)
    return best

def gaps_pairs(C, T, I, Jx):
    """Vectorised SAT gaps for the pairs (I[k], Jx[k]) of unit squares with centres C and angles T.
    Identical to sat_gap() but evaluated for every pair at once."""
    C = np.asarray(C, float); T = np.asarray(T, float)
    d = C[Jx] - C[I]
    cI, sI = np.cos(T[I]), np.sin(T[I])
    cJ, sJ = np.cos(T[Jx]), np.sin(T[Jx])
    best = np.full(len(I), -1e9)
    for (ax, ay, ocx, ocy, osx, osy) in (
            (cI, sI, cJ, sJ, -sJ, cJ), (-sI, cI, cJ, sJ, -sJ, cJ),
            (cJ, sJ, cI, sI, -sI, cI), (-sJ, cJ, cI, sI, -sI, cI)):
        proj = np.abs(d[:, 0] * ax + d[:, 1] * ay)
        sup = np.abs(ax * ocx + ay * ocy) + np.abs(ax * osx + ay * osy)
        best = np.maximum(best, proj - 0.5 - 0.5 * sup)
    return best

def half_width(th):
    return (abs(math.cos(th)) + abs(math.sin(th))) / 2.0

def wall_gaps(cx, cy, th, s):
    w = half_width(th)
    return {'left': cx - w, 'right': s - w - cx, 'bottom': cy - w, 'top': s - w - cy}

def contained(cx, cy, th, s, tol=1e-9):
    return min(wall_gaps(cx, cy, th, s).values()) >= -tol

# ---------------------------------------------------------------- D4
def d4_ops(s):
    """The 8 elements of D4 on [0,s]^2 acting on (cx, cy, theta)."""
    return [
        ('e',    lambda x, y, t: (x, y, t)),
        ('r90',  lambda x, y, t: (s - y, x, t)),
        ('r180', lambda x, y, t: (s - x, s - y, t)),
        ('r270', lambda x, y, t: (y, s - x, t)),
        ('mx',   lambda x, y, t: (s - x, y, -t)),
        ('my',   lambda x, y, t: (x, s - y, -t)),
        ('diag', lambda x, y, t: (y, x, -t)),
        ('anti', lambda x, y, t: (s - y, s - x, -t)),
    ]

def tmod(t):
    """theta reduced to [0, 90) degrees-equivalent in radians."""
    q = math.pi / 2
    return t - q * math.floor(t / q)

def tilt_close(a, b, deg=3.0):
    d = abs(tmod(a) - tmod(b)) % (math.pi / 2)
    d = min(d, math.pi / 2 - d)
    return math.degrees(d) <= deg

def stabiliser(pins, s, tol=1e-6):
    """Elements of D4 that fix the pin set (as a set of axis-aligned unit squares)."""
    P = sorted((round(x, 6), round(y, 6)) for x, y in pins)
    keep = []
    for nm, f in d4_ops(s):
        Q = sorted((round(f(x, y, 0.0)[0], 6), round(f(x, y, 0.0)[1], 6)) for x, y in pins)
        if all(abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol for a, b in zip(P, Q)):
            keep.append((nm, f))
    return keep

# ---------------------------------------------------------------- slot naming
def slot_cells(s, imax=4):
    """Named axis-aligned unit cells stacked into the four corners."""
    out = {}
    for i in range(imax):
        for j in range(imax):
            out[f'BL({i},{j})'] = (0.5 + i, 0.5 + j)
            out[f'BR({i},{j})'] = (s - 0.5 - i, 0.5 + j)
            out[f'TL({i},{j})'] = (0.5 + i, s - 0.5 - j)
            out[f'TR({i},{j})'] = (s - 0.5 - i, s - 0.5 - j)
    return out

def snap(cx, cy, th, s, dtol=0.05, atol=3.0):
    """Return the slot name if (cx,cy,th) is within dtol of a slot cell and atol degrees of axis."""
    a = math.degrees(tmod(th))
    if min(a, 90.0 - a) > atol:
        return None
    best, bd = None, 1e9
    for nm, (x, y) in slot_cells(s).items():
        d = math.hypot(cx - x, cy - y)
        if d < bd:
            best, bd = nm, d
    return best if bd <= dtol else None

# ---------------------------------------------------------------- A57 loading
A57 = os.path.join('attempts', 'A57-shadow-trees')

def node_files(root='.'):
    return sorted(glob.glob(os.path.join(root, A57, 'results', 'tree', '*', '*.json')))

def load_node(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def node_shadow(d, ythr=0.5):
    """(pins, conditioned, support) from a node json. pins = the 5 class squares, conditioned = the
    branch square (centre of its box), support = LP dual-support placements with y > ythr."""
    cores = (d.get('hyp') or {}).get('cores', [])
    pins, cond = [], None
    for k, c in enumerate(cores):
        fl = c.get('float', {})
        x, y = float(fl.get('kx')), float(fl.get('ky'))
        t = math.radians(float(fl.get('theta_deg', 0.0)))
        if k < 5:
            pins.append((x, y))
        else:
            b = c.get('box') or {}
            cx = 0.5 * (b.get('x0', x) + b.get('x1', x))
            cy = 0.5 * (b.get('y0', y) + b.get('y1', y))
            th = math.radians(0.5 * (b.get('th0', 0.0) + b.get('th1', 0.0)))
            cond = (cx, cy, th)
    sup = [(float(q['cx']), float(q['cy']), float(q['theta']))
           for q in d.get('packing', []) if float(q.get('y', 0.0)) > ythr]
    return pins, cond, sup

def is_integral(d, lo=1e-6, hi=1e-6):
    ys = [float(q.get('y', 0.0)) for q in d.get('packing', [])]
    return all(y < lo or y > 1 - hi for y in ys)

# ---------------------------------------------------------------- shadow matching
def canon(sqs, ops, s):
    """All symmetry images of a square list, each sorted; used for tolerant matching."""
    out = []
    for nm, f in ops:
        im = [tuple(f(x, y, t)) for x, y, t in sqs]
        im = [(x, y, tmod(t)) for x, y, t in im]
        im.sort(key=lambda q: (round(q[0], 3), round(q[1], 3), round(q[2], 3)))
        out.append((nm, im))
    return out

def match(a, b, dtol=0.05, atol=3.0):
    """Greedy bijection between two square lists within tolerance."""
    if len(a) != len(b):
        return False
    used = [False] * len(b)
    for p in a:
        hit = -1
        for j, q in enumerate(b):
            if used[j]:
                continue
            if math.hypot(p[0] - q[0], p[1] - q[1]) <= dtol and tilt_close(p[2], q[2], atol):
                hit = j
                break
        if hit < 0:
            return False
        used[hit] = True
    return True

# ---------------------------------------------------------------- incidence Jacobian
def _edges(cx, cy, th):
    P = corners(cx, cy, th)
    return [(P[i], P[(i + 1) % 4]) for i in range(4)]

def contact_type(c1, t1, c2, t2, tol=1e-5):
    """Classify a touching pair: 'vertex-on-edge', 'flush' (edge-edge, positive overlap length),
    'vertex-vertex'.  Returns (kind, detail)."""
    A, B = corners(*c1, t1), corners(*c2, t2)
    # count near-incidences of A's vertices with B's edges and vice versa
    inc = []
    for (V, W, tag) in ((A, B, 'a'), (B, A, 'b')):
        for vi, v in enumerate(V):
            for ei in range(4):
                p, q = W[ei], W[(ei + 1) % 4]
                ex, ey = q[0] - p[0], q[1] - p[1]
                L = math.hypot(ex, ey)
                nx, ny = -ey / L, ex / L
                d = abs((v[0] - p[0]) * nx + (v[1] - p[1]) * ny)
                t = ((v[0] - p[0]) * ex + (v[1] - p[1]) * ey) / (L * L)
                if d <= tol and -tol <= t <= 1 + tol:
                    inc.append((tag, vi, ei, t, d))
    corner_hits = [i for i in inc if i[3] < 1e-4 or i[3] > 1 - 1e-4]
    if len(inc) >= 4:
        return 'flush', inc
    if len(inc) >= 2 and len(corner_hits) >= 2:
        return 'vertex-vertex', inc
    if len(inc) >= 1:
        return 'vertex-on-edge', inc
    return 'none', inc


def incidence_rows(sqs, free_idx, s, s_is_var, contacts, walls):
    """Rows of the incidence Jacobian.  Variables: [s?] + (dx,dy,dth) for each free square.
    Each contact contributes one row: the derivative of the signed distance from the incident
    VERTEX to the supporting LINE of the other square's edge (exact, analytic).  Flush contacts
    contribute two rows (both vertices of the shared edge)."""
    nv = (1 if s_is_var else 0) + 3 * len(free_idx)
    col = {k: (1 if s_is_var else 0) + 3 * m for m, k in enumerate(free_idx)}
    rows = []
    labels = []

    def vertex_jac(k, vi):
        """d(vertex)/d(vars) for vertex vi of square k; returns (2 x nv) array plus the vertex."""
        J = np.zeros((2, nv))
        cx, cy, th = sqs[k]
        dx, dy = ((-1, -1), (1, -1), (1, 1), (-1, 1))[vi]
        c, si = math.cos(th), math.sin(th)
        v = (cx + 0.5 * (dx * c - dy * si), cy + 0.5 * (dx * si + dy * c))
        if k in col:
            j = col[k]
            J[0, j] = 1.0
            J[1, j + 1] = 1.0
            J[0, j + 2] = 0.5 * (-dx * si - dy * c)
            J[1, j + 2] = 0.5 * (dx * c - dy * si)
        elif s_is_var:
            # slot square: centre is an affine function of s (built by the caller as dcds)
            pass
        return J, v

    return rows, labels, col, nv
