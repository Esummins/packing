"""Small exact-ish geometry helpers for A12: unit squares (centre, theta), overlap test (SAT), conflict graphs,
max independent set (CP-SAT), region membership.  Float geometry with tolerances (analysis only, NOT the verifier)."""
import math
import numpy as np

DEG = math.pi / 180.0


def corners(cx, cy, th, half=0.5):
    c, s = math.cos(th), math.sin(th)
    return np.array([(cx + half * (c * a - s * b), cy + half * (s * a + c * b)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def overlap_pair(p, q, tol=1e-9):
    """True iff the two closed unit squares p=(cx,cy,th) and q have intersecting interiors (SAT on 4 axes).
    Positive tol => require overlap depth > tol on every axis (robust overlap); negative tol => touching counts."""
    Cp, Cq = corners(*p), corners(*q)
    for th in (p[2], q[2]):
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            a = Cp @ ax; b = Cq @ ax
            if min(a.max(), b.max()) - max(a.min(), b.min()) <= tol:
                return False
    return True


def overlap_matrix(P, tol=1e-9):
    """P: (n,3) array of placements.  Boolean (n,n) matrix of interior-overlap (vectorised SAT)."""
    P = np.asarray(P, dtype=float)
    n = len(P)
    C = np.stack([corners(*p) for p in P])           # (n,4,2)
    ov = np.ones((n, n), dtype=bool)
    # separating axes taken from each square's frame: for pair (i,j) test axes of i and axes of j
    for who in (0, 1):
        for k in range(2):
            th = P[:, 2]
            ax = np.stack([np.cos(th + k * math.pi / 2), np.sin(th + k * math.pi / 2)], 1)   # (n,2) axis of square i
            # projections of all squares onto axis of square i:  proj[i, j, corner]
            proj = np.einsum("jkc,ic->ijk", C, ax)     # (n,n,4)
            lo = proj.min(2); hi = proj.max(2)          # (n,n): square j on axis of i
            own_lo = np.diagonal(lo); own_hi = np.diagonal(hi)
            if who == 0:
                depth = np.minimum(own_hi[:, None], hi) - np.maximum(own_lo[:, None], lo)   # axis of i, pair (i,j)
            else:
                depth = (np.minimum(own_hi[:, None], hi) - np.maximum(own_lo[:, None], lo)).T   # axis of j
            ov &= depth > tol
    np.fill_diagonal(ov, False)
    return ov


def inside_container(P, s, tol=1e-9):
    P = np.asarray(P, dtype=float)
    w = np.cos(P[:, 2]) + np.sin(P[:, 2])
    return (P[:, 0] >= w / 2 - tol) & (P[:, 0] <= s - w / 2 + tol) & (P[:, 1] >= w / 2 - tol) & (P[:, 1] <= s - w / 2 + tol)


def max_independent_set(adj, weights=None, time_limit=60.0, fixed_in=None):
    """max (weighted) independent set of a boolean adjacency matrix via CP-SAT.  Returns (value, list of indices)."""
    from ortools.sat.python import cp_model
    n = len(adj)
    m = cp_model.CpModel()
    z = [m.NewBoolVar(f"z{i}") for i in range(n)]
    I, J = np.nonzero(np.triu(adj, 1))
    for i, j in zip(I, J):
        m.AddBoolOr([z[i].Not(), z[j].Not()])
    if fixed_in:
        for i in fixed_in:
            m.Add(z[i] == 1)
    if weights is None:
        m.Maximize(sum(z))
    else:
        W = [int(round(w * 10**6)) for w in weights]
        m.Maximize(sum(W[i] * z[i] for i in range(n)))
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = time_limit
    sol.parameters.num_workers = 4
    st = sol.Solve(m)
    sel = [i for i in range(n) if sol.Value(z[i])]
    val = len(sel) if weights is None else sum(weights[i] for i in sel)
    return val, sel, sol.StatusName(st)


# ---------------------------------------------------------------- regions (centre space)
class Region:
    """union of primitives; each primitive: ('disc', cx, cy, r) | ('rect', x0, x1, y0, y1) | ('annulus', cx, cy, r0, r1).
    C4 images can be added with .sym4(s)."""

    def __init__(self, prims, name=""):
        self.prims = list(prims); self.name = name

    def contains(self, x, y):
        for p in self.prims:
            if p[0] == "disc":
                if (x - p[1]) ** 2 + (y - p[2]) ** 2 <= p[3] ** 2:
                    return True
            elif p[0] == "rect":
                if p[1] <= x <= p[2] and p[3] <= y <= p[4]:
                    return True
            elif p[0] == "annulus":
                d2 = (x - p[1]) ** 2 + (y - p[2]) ** 2
                if p[3] ** 2 <= d2 <= p[4] ** 2:
                    return True
        return False

    def contains_many(self, X, Y):
        return np.array([self.contains(x, y) for x, y in zip(X, Y)])

    def sym4(self, s):
        out = []
        for p in self.prims:
            if p[0] == "disc":
                x, y = p[1], p[2]
                for (a, b) in ((x, y), (s - y, x), (s - x, s - y), (y, s - x)):
                    out.append(("disc", a, b, p[3]))
            elif p[0] == "rect":
                x0, x1, y0, y1 = p[1:]
                boxes = [(x0, x1, y0, y1), (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]
                for b in boxes:
                    out.append(("rect",) + b)
            else:
                out.append(p)
        return Region(out, self.name + "+C4")

    def union(self, other, name=None):
        return Region(self.prims + other.prims, name or (self.name + "|" + other.name))

    def bbox(self):
        xs, ys = [], []
        for p in self.prims:
            if p[0] == "disc":
                xs += [p[1] - p[3], p[1] + p[3]]; ys += [p[2] - p[3], p[2] + p[3]]
            elif p[0] == "rect":
                xs += [p[1], p[2]]; ys += [p[3], p[4]]
            else:
                xs += [p[1] - p[4], p[1] + p[4]]; ys += [p[2] - p[4], p[2] + p[4]]
        return min(xs), max(xs), min(ys), max(ys)


def realise_k(region, s, thetas_deg, step=0.1, time_limit=60.0, tol=1e-9):
    """LOWER bound on k(R): max number of pairwise interior-disjoint unit squares inside [0,s]^2 with centres in R,
    orientations from the given finite list, centres on a grid of the given step (plus nothing else).
    Returns (k_lb, placements)."""
    x0, x1, y0, y1 = region.bbox()
    xs = np.arange(math.floor(x0 / step) * step, x1 + step / 2, step)
    ys = np.arange(math.floor(y0 / step) * step, y1 + step / 2, step)
    P = []
    for th in thetas_deg:
        t = th * DEG
        w = math.cos(t) + math.sin(t)
        for x in xs:
            for y in ys:
                if region.contains(x, y) and w / 2 - 1e-12 <= x <= s - w / 2 + 1e-12 and w / 2 - 1e-12 <= y <= s - w / 2 + 1e-12:
                    P.append((x, y, t))
    if not P:
        return 0, []
    P = np.array(P)
    adj = overlap_matrix(P, tol=tol)
    val, sel, st = max_independent_set(adj, time_limit=time_limit)
    return int(val), [tuple(P[i]) for i in sel], st, len(P)


def incircle_ub_points(region, s, step=0.05):
    """crude UPPER bound helper is not available cheaply; this returns a LOWER bound on the max number of points of R
    pairwise >= 1 apart (grid + MIS) -- used only to see how loose the incircle bound is."""
    x0, x1, y0, y1 = region.bbox()
    xs = np.arange(x0, x1 + step / 2, step); ys = np.arange(y0, y1 + step / 2, step)
    pts = np.array([(x, y) for x in xs for y in ys if region.contains(x, y)])
    if len(pts) == 0:
        return 0
    d = np.linalg.norm(pts[:, None] - pts[None], axis=2)
    adj = d < 1 - 1e-9
    np.fill_diagonal(adj, False)
    val, sel, st = max_independent_set(adj, time_limit=30)
    return int(val)
