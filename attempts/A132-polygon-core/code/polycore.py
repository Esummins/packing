"""A132 -- the POLYGON CORE K'(B) of a parameter box, and its exact vertex certification.

For a parameter box  B = [x0,x1] x [y0,y1] x [th0,th1]  the hypothesis is "some square Q0 of the
packing has (centre, tilt) in B".  A13/A57 replace that by the axis-ish RATIONAL SQUARE

    K(a) = Box.core(B)          (centre = box midpoint, tilt = theta_m, half-side a),

which is contained in Q(c, theta) for every (c, theta) in B (T5, Lean `core_meet_same_square`
supplies the consequence).  K(a) is the largest *square of that pose* inside the intersection; the
intersection itself,

    K'(B) = INTERSECTION over (c, theta) in B of Q(c, theta),

is a convex polygon and is strictly bigger -- for a narrow tilt bin it is nearly the whole tilted
square, while K(a) loses ~0.21 along each diagonal.  Everything T5 does with K(a) it does with K',
because the only property used is  K subset Q(c,theta) for every pose in B  (and K subset the
INTERIOR, which is why the polygon is shrunk by a hair before it is certified).

CERTIFICATION.  K' is convex, so it is enough to certify the VERTICES: if every vertex v of a
candidate polygon P satisfies  v in Q(c, theta) for all (c, theta) in B,  then conv(P) subset K'(B)
by convexity -- regardless of how P was found.  The vertex test is exact in rationals.  With
d = v - c and the rational parametrisation t = tan(theta/2),

    cos(th) u + sin(th) w  =  ((1 - t^2) u + 2 t w) / (1 + t^2),

so  |R(-th) d|_inf <= 1/2  for all t in [t0,t1] and all c in the centre rectangle is exactly

    for each of the 4 corners c of the centre rectangle, and for (u,w) = (dx,dy) and (dy,-dx):
        P1(t) = (1/2 + u) t^2 - 2 w t + (1/2 - u)  >= 0   on [t0,t1]
        P2(t) = (1/2 - u) t^2 + 2 w t + (1/2 + u)  >= 0   on [t0,t1]

(c enters affinely, so its max over the rectangle is at a corner; requiring all four corners is
equivalent to requiring the max).  Nonnegativity of a rational quadratic on a rational interval is
decided exactly: endpoints, plus the vertex  4AC - B^2 >= 0  when A > 0 and -B/(2A) is inside.

t0 = caselp.t_lo(th0), t1 = caselp.t_hi(th1) are the corpus's own OUTWARD-rounded rational tilt
bounds, so the certified statement is about a tilt range that CONTAINS [th0,th1]: conservative.

CONSTRUCTION (numerical, then certified).  K' is the intersection of the four half-planes

    e_i(th) . p <= 1/2 + min_{c in Bc} e_i(th) . c ,   -e_i(th) . p <= 1/2 - max_{c in Bc} e_i(th) . c

over theta in [th0,th1] and i = 1,2.  Clip a big square by those half-planes on a fine theta grid,
each offset inward by `shrink`; delete vertices whose cut-off triangle is negligible (deleting a
vertex of a CONVEX polygon always shrinks it, so this stays a subset); round to a rational grid;
take the exact rational convex hull; certify every vertex.  The certification is the authority --
the grid and the shrink only have to be good enough for it to pass.

Nothing in this module is wired into any driver.  A57/A96 code is imported read-only.
"""
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A57 = os.path.abspath(os.path.join(HERE, "..", "..", "A57-shadow-trees"))
if os.path.join(A57, "code") not in sys.path:
    sys.path.insert(0, os.path.join(A57, "code"))

from caselp import Box, Core, t_lo, t_hi           # noqa: E402  (read-only import)

HALF = Fr(1, 2)
VDEN = 10 ** 9          # rational grid the polygon vertices are rounded to


# --------------------------------------------------------------------- half-planes of one pose set
def _corners(box):
    return ((box.x0, box.y0), (box.x1, box.y0), (box.x1, box.y1), (box.x0, box.y1))


def halfplanes(box, thetas):
    """[(nx, ny, b)] with the meaning  nx*px + ny*py <= b,  whose intersection over the given
    thetas (radians) contains K'(B) and equals it in the limit of a fine grid."""
    cor = _corners(box)
    out = []
    for th in thetas:
        c, s = math.cos(th), math.sin(th)
        for (ex, ey) in ((c, s), (-s, c)):
            pr = [ex * cx + ey * cy for (cx, cy) in cor]
            out.append((ex, ey, 0.5 + min(pr)))
            out.append((-ex, -ey, 0.5 - max(pr)))
    return out


def _clip(poly, nx, ny, b):
    """Sutherland-Hodgman clip of a convex polygon by the half-plane n.p <= b."""
    if not poly:
        return poly
    out = []
    m = len(poly)
    for i in range(m):
        px, py = poly[i]
        qx, qy = poly[(i + 1) % m]
        dp = nx * px + ny * py - b
        dq = nx * qx + ny * qy - b
        if dp <= 0.0:
            out.append((px, py))
        if (dp > 0.0) != (dq > 0.0):
            t = dp / (dp - dq)
            out.append((px + t * (qx - px), py + t * (qy - py)))
    return out


def _tri_area(a, b, c):
    return 0.5 * abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def _simplify(poly, max_v=40, area_tol=2e-8):
    """Delete vertices of a CONVEX polygon (always a shrink: the cut-off triangle is removed)
    while the cut is negligible or the polygon is still too big."""
    P = list(poly)
    while len(P) > 3:
        m = len(P)
        areas = [_tri_area(P[(i - 1) % m], P[i], P[(i + 1) % m]) for i in range(m)]
        j = int(np.argmin(areas))
        if len(P) > max_v or areas[j] < area_tol:
            P.pop(j)
        else:
            break
    return P


def _hull_frac(pts):
    """exact rational monotone-chain convex hull (counter-clockwise)."""
    P = sorted(set(pts))
    if len(P) <= 2:
        return P

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo = []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# --------------------------------------------------------------------- exact vertex certification
def _quad_nonneg(A, B, C, t0, t1):
    """A t^2 + B t + C >= 0 for every t in [t0, t1]?  Exact in Fractions."""
    if A * t0 * t0 + B * t0 + C < 0:
        return False
    if A * t1 * t1 + B * t1 + C < 0:
        return False
    if A > 0:
        # interior minimum at t* = -B/(2A)
        if t0 * (2 * A) <= -B <= t1 * (2 * A):
            return 4 * A * C - B * B >= 0
    return True


def vertex_ok(vx, vy, box, t0=None, t1=None):
    """EXACT: does the rational point (vx, vy) lie in Q(c, theta) for every (c, theta) in `box`?"""
    if t0 is None:
        t0, t1 = t_lo(box.th0), t_hi(box.th1)
    for (cx, cy) in _corners(box):
        dx = vx - Fr(cx)
        dy = vy - Fr(cy)
        for (u, w) in ((dx, dy), (dy, -dx)):
            if not _quad_nonneg(HALF + u, -2 * w, HALF - u, t0, t1):
                return False
            if not _quad_nonneg(HALF - u, 2 * w, HALF + u, t0, t1):
                return False
    return True


# --------------------------------------------------------------------- the polygon core
class PolyCore:
    """a certified convex polygon contained in every Q(c, theta), (c, theta) in `box`."""

    __slots__ = ("box", "verts", "P", "n_grid", "shrink", "certified",
                 "fk", "fc", "fs", "au", "av", "fa", "fkc")

    def __init__(self, box, verts_frac, n_grid, shrink, certified):
        self.box = box
        self.verts = verts_frac                       # [(Fraction, Fraction)] ccw
        self.P = np.array([[float(a), float(b)] for a, b in verts_frac])
        self.n_grid = n_grid
        self.shrink = shrink
        self.certified = certified
        # --- the OUTER rectangle (bounding box in the box-core's own frame) and the INNER square
        # K(a): a placement that misses the rectangle misses K', one that meets K(a) by a margin
        # meets K'.  Both are 4-axis tests, and they bracket all but a thin band of placements.
        k = box.core()
        self.fc, self.fs = (k.fc, k.fs) if k is not None else (1.0, 0.0)
        self.fa = float(k.a) if k is not None else 0.0
        self.fkc = k.fk if k is not None else np.zeros(2)
        pu = self.P[:, 0] * self.fc + self.P[:, 1] * self.fs
        pv = -self.P[:, 0] * self.fs + self.P[:, 1] * self.fc
        mu, mv = 0.5 * (pu.min() + pu.max()), 0.5 * (pv.min() + pv.max())
        self.au, self.av = 0.5 * (pu.max() - pu.min()), 0.5 * (pv.max() - pv.min())
        self.fk = np.array([mu * self.fc - mv * self.fs, mu * self.fs + mv * self.fc])

    def area(self):
        P = self.P
        x, y = P[:, 0], P[:, 1]
        return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))

    def to_json(self):
        return dict(box=self.box.to_json(), certified=self.certified, n_grid=self.n_grid,
                    shrink=self.shrink, area=self.area(),
                    verts=[[str(a), str(b)] for a, b in self.verts])


def build(box, n_grid=129, shrink=1e-6, max_v=40, retries=(1e-6, 1e-5, 1e-4, 1e-3)):
    """K'(B), certified.  Raises if no shrink in `retries` yields a fully certified polygon."""
    t0, t1 = t_lo(box.th0), t_hi(box.th1)
    cx = 0.5 * (box.x0 + box.x1)
    cy = 0.5 * (box.y0 + box.y1)
    ths = np.linspace(math.radians(box.th0), math.radians(box.th1), n_grid) \
        if box.th1 > box.th0 else np.array([math.radians(box.th0)])
    HP = halfplanes(box, ths)
    last = None
    for sh in ((shrink,) + tuple(s for s in retries if s > shrink)):
        poly = [(cx - 1.2, cy - 1.2), (cx + 1.2, cy - 1.2), (cx + 1.2, cy + 1.2), (cx - 1.2, cy + 1.2)]
        for (nx, ny, b) in HP:
            poly = _clip(poly, nx, ny, b - sh)
            if not poly:
                break
        if not poly:
            continue
        poly = _simplify(poly, max_v=max_v)
        vf = [(Fr(round(x * VDEN), VDEN), Fr(round(y * VDEN), VDEN)) for (x, y) in poly]
        vf = _hull_frac(vf)
        if len(vf) < 3:
            continue
        bad = [i for i, (a, b) in enumerate(vf) if not vertex_ok(a, b, box, t0, t1)]
        last = (vf, sh, bad)
        if not bad:
            return PolyCore(box, vf, len(ths), sh, True)
    raise RuntimeError(f"polycore: no certified polygon for {box!r}; "
                       f"last had {len(last[2]) if last else '?'} bad vertices")


# --------------------------------------------------------------------- SAT: polygon vs unit square
def poly_square_depth(P, C, TH):
    """SAT overlap depth between the convex polygon P (nv,2, ccw) and the unit squares Q(c, theta)
    for centres C (m,2) and tilts TH (m,) in RADIANS.  depth > 0  <=>  the interiors meet.
    Vectorised over the placements; the same convention as caselp.Core.depth_many."""
    P = np.asarray(P, float)
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    m = len(C)
    if m == 0:
        return np.zeros(0)
    ct, st = np.cos(TH), np.sin(TH)
    depth = np.full(m, np.inf)
    # (a) the polygon's edge normals
    E = np.roll(P, -1, axis=0) - P
    N = np.stack([E[:, 1], -E[:, 0]], 1)                       # outward for ccw
    L = np.hypot(N[:, 0], N[:, 1])
    keep = L > 1e-14
    N = N[keep] / L[keep][:, None]
    for k in range(len(N)):
        nx, ny = N[k]
        pp = P[:, 0] * nx + P[:, 1] * ny
        plo, phi = pp.min(), pp.max()
        h = 0.5 * (np.abs(nx * ct + ny * st) + np.abs(-nx * st + ny * ct))
        qc = C[:, 0] * nx + C[:, 1] * ny
        depth = np.minimum(depth, np.minimum(phi, qc + h) - np.maximum(plo, qc - h))
    # (b) the square's own two axes
    for (ax, ay) in ((ct, st), (-st, ct)):
        pp = np.outer(P[:, 0], ax) + np.outer(P[:, 1], ay)     # (nv, m)
        plo, phi = pp.min(0), pp.max(0)
        qc = C[:, 0] * ax + C[:, 1] * ay
        depth = np.minimum(depth, np.minimum(phi, qc + 0.5) - np.maximum(plo, qc - 0.5))
    return depth


def _rect_depth(fk, fc, fs, au, av, C, ct, st):
    """SAT depth between the rotated rectangle (centre fk, frame (fc,fs), half-widths au, av) and
    the unit squares Q(C, theta).  Core.depth_many is the special case au = av = a."""
    A = np.abs(ct * fc + st * fs)
    Bv = np.abs(-st * fc + ct * fs)
    g = A + Bv
    d = C - fk[None, :]
    pe1 = np.abs(d[:, 0] * fc + d[:, 1] * fs)
    pe2 = np.abs(-d[:, 0] * fs + d[:, 1] * fc)
    pf1 = np.abs(d[:, 0] * ct + d[:, 1] * st)
    pf2 = np.abs(-d[:, 0] * st + d[:, 1] * ct)
    de = np.minimum(au + 0.5 * g - pe1, av + 0.5 * g - pe2)
    df = np.minimum(0.5 + au * A + av * Bv - pf1, 0.5 + au * Bv + av * A - pf2)
    return np.minimum(de, df)


def poly_square_meets(pc, C, TH, eps, margin=1e-3):
    """Boolean 'Q(c, theta) meets K' with SAT depth > eps', fast.

    Three steps, the first two 4-axis and the third the full polygon SAT on what is left:
      (1) depth against the OUTER rectangle <= eps  ->  certainly a miss (the rectangle contains
          the polygon);
      (2) depth against the INNER square K(a) > eps + margin  ->  certainly a hit (K(a) is inside
          K' up to the builder's 1e-6 shrink, hence the margin);
      (3) everything else: the exact float SAT of `poly_square_depth`.
    Same answer as `poly_square_depth(...) > eps` up to the 1e-6 shrink, at a fraction of the cost.
    """
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    if len(C) == 0:
        return np.zeros(0, bool)
    ct, st = np.cos(TH), np.sin(TH)
    outer = _rect_depth(pc.fk, pc.fc, pc.fs, pc.au, pc.av, C, ct, st) > eps
    hit = np.zeros(len(C), bool)
    if not outer.any():
        return hit
    inner = np.zeros(len(C), bool)
    idx = np.flatnonzero(outer)
    inner[idx] = _rect_depth(pc.fkc, pc.fc, pc.fs, pc.fa, pc.fa, C[idx], ct[idx], st[idx]) \
        > eps + margin
    hit |= inner
    band = np.flatnonzero(outer & ~inner)
    if len(band):
        hit[band] = poly_square_depth(pc.P, C[band], TH[band]) > eps
    return hit


def poly_poly_depth(P, R):
    """SAT overlap depth between two convex polygons (both ccw).  > 0  <=>  interiors meet."""
    P = np.asarray(P, float)
    R = np.asarray(R, float)
    d = np.inf
    for A, B in ((P, R), (R, P)):
        E = np.roll(A, -1, axis=0) - A
        N = np.stack([E[:, 1], -E[:, 0]], 1)
        L = np.hypot(N[:, 0], N[:, 1])
        for k in range(len(N)):
            if L[k] <= 1e-14:
                continue
            nx, ny = N[k] / L[k]
            a = A[:, 0] * nx + A[:, 1] * ny
            b = B[:, 0] * nx + B[:, 1] * ny
            d = min(d, min(a.max(), b.max()) - max(a.min(), b.min()))
    return d


def overlap_witness(pc1, pc2, ngrid=41):
    """A single RATIONAL point certified (exactly, by `vertex_ok`) to lie in Q(c,theta) for every
    pose of BOTH boxes -- i.e. an exact witness that the T5-polygon kill fires.  Returns
    [str(x), str(y)] or None.  Searched on a grid over the overlap of the two float polygons; the
    exact test on the two ORIGINAL boxes is what makes it a certificate, so a failed search is a
    'not proved', never a false kill."""
    P, R = pc1.P, pc2.P
    lo = np.maximum(P.min(0), R.min(0))
    hi = np.minimum(P.max(0), R.max(0))
    if np.any(hi <= lo):
        return None
    xs = np.linspace(lo[0], hi[0], ngrid)
    ys = np.linspace(lo[1], hi[1], ngrid)

    def inside(poly, x, y):
        E = np.roll(poly, -1, axis=0) - poly
        return bool(np.all((E[:, 0] * (y - poly[:, 1]) - E[:, 1] * (x - poly[:, 0])) >= 0.0))

    cand = []
    for x in xs:
        for y in ys:
            if inside(P, x, y) and inside(R, x, y):
                cand.append((x, y))
    if not cand:
        return None
    cx, cy = np.mean([c[0] for c in cand]), np.mean([c[1] for c in cand])
    cand.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    for (x, y) in cand[:12]:
        vx, vy = Fr(round(x * VDEN), VDEN), Fr(round(y * VDEN), VDEN)
        if vertex_ok(vx, vy, pc1.box) and vertex_ok(vx, vy, pc2.box):
            return [str(vx), str(vy)]
    return None


# --------------------------------------------------------------------- the axis core, for contrast
def core_of(box):
    """K(a) exactly as the LP and the certificates use it (caselp.Box.core)."""
    return box.core()


def core_depth(core, C, TH):
    """caselp.Core.depth_many, but with a per-placement theta array."""
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    out = np.empty(len(C))
    for i, th in enumerate(TH):
        out[i] = core.depth_many(C[i:i + 1], float(th))[0]
    return out


def core_depth_fast(core, C, TH):
    """vectorised form of Core.depth_many over (centre, theta) pairs."""
    C = np.asarray(C, float).reshape(-1, 2)
    TH = np.asarray(TH, float).reshape(-1)
    c, s = np.cos(TH), np.sin(TH)
    g = np.abs(c * core.fc + s * core.fs) + np.abs(-s * core.fc + c * core.fs)
    d = C - core.fk[None, :]
    pe1 = np.abs(d[:, 0] * core.fc + d[:, 1] * core.fs)
    pe2 = np.abs(-d[:, 0] * core.fs + d[:, 1] * core.fc)
    pf1 = np.abs(d[:, 0] * c + d[:, 1] * s)
    pf2 = np.abs(-d[:, 0] * s + d[:, 1] * c)
    de = np.minimum(core.fa + 0.5 * g - pe1, core.fa + 0.5 * g - pe2)
    df = np.minimum(0.5 + core.fa * g - pf1, 0.5 + core.fa * g - pf2)
    return np.minimum(de, df)


def core_verts(core):
    return np.array([[float(v[0]), float(v[1])] for v in core.vertices()])


# --------------------------------------------------------------------- self-test
if __name__ == "__main__":
    import json
    import time
    b = Box(1.3795140000000001, 1.4144532500000002, 2.357813, 2.39275225,
            73.73979529168804, 75.89780905162085)
    t0 = time.time()
    pc = build(b)
    k = core_of(b)
    print(f"K' vertices {len(pc.verts)}  area {pc.area():.6f}  certified {pc.certified} "
          f"shrink {pc.shrink}  ({time.time() - t0:.2f} s)")
    print(f"K(a) a = {float(k.a):.6f}  area {(2 * float(k.a)) ** 2:.6f}  "
          f"ratio {pc.area() / (2 * float(k.a)) ** 2:.4f}")
    rng = np.random.default_rng(0)
    n = 10000
    cs = np.stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)], 1)
    th = np.radians(rng.uniform(b.th0, b.th1, n))
    worst = 0.0
    for (vx, vy) in pc.verts:
        d = np.stack([float(vx) - cs[:, 0], float(vy) - cs[:, 1]], 1)
        u = np.abs(d[:, 0] * np.cos(th) + d[:, 1] * np.sin(th))
        w = np.abs(-d[:, 0] * np.sin(th) + d[:, 1] * np.cos(th))
        worst = max(worst, float(np.maximum(u, w).max()))
    print(f"sampled: {n} poses x {len(pc.verts)} vertices, max |R(-th)(v-c)|_inf = {worst:.9f} "
          f"(must be <= 0.5); hits = {0 if worst <= 0.5 else 1} violations")
    print(json.dumps(pc.to_json())[:200])
