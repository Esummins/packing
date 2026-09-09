"""A168 -- ROLES with per-tilt-sub-bin PIECES, the NORMALISE fixed point and the NODE INVARIANT.

Coordinator's rule (2026-09-09): at EVERY node, in this order, (i) container clip of each box per
tilt sub-bin, (ii) mutual clip of each box against every other box's K' per tilt sub-bin, iterated
to a fixed point, (iii) K' and the exact axis core recomputed on the clipped boxes, (iv) an
ASSERTION that every K' lies inside the container and every pair of K' is interior-disjoint --
before any row, cover, figure or LP.  A171 `multibox.py` is being built for the same purpose; this
module is the attempt-local implementation with the same statement.

A ROLE is a named square of the node whose pose is known to lie in the UNION of its PIECES, each
piece a caselp.Box with its own tilt sub-range (the pieces partition the role's tilt range; the
union is never re-formed).  Its certified objects:

  * K'(piece)   A132's polygon core of the piece (vertices certified by `vertex_ok`, exact);
  * K'(role)    the exact rational INTERSECTION of the pieces' K' -- a convex polygon inside EVERY
                pose of EVERY piece, i.e. inside the role's square wherever it is; every vertex is
                re-certified by `vertex_ok` against every piece;
  * axis(role)  the largest axis-aligned square about K'(role)'s centroid inside K'(role), its four
                corners certified by `vertex_ok` against every piece (this is the 'pin' A131's clip
                consumes, A158's rule).

The CONTAINER clip of a piece uses w_min over the sub-bin (A131's rule: a centre that is outside
[w/2, s0 - w/2] for EVERY tilt of the sub-bin carries no admissible pose).  Poses of a piece at a
tilt where the square would leave the container are inadmissible and are simply not squares of the
family; the per-piece residual `slack = (w_max - w_min)/2` is reported, and every drawn or sampled
pose union is restricted to admissible poses.  The MUTUAL clip of a piece against another role's
axis core discards the centres whose square meets that core at EVERY tilt of the piece's sub-bin
(A131 `dead_q`, exact): such a centre carries no square of the family distinct from that role.

The NODE INVARIANT (iv) is decided exactly: K'(role) inside [0, s0]^2 (every vertex), and every
pair of K'(role)s interior-disjoint (SAT over both polygons' edge normals in Fractions).  A failing
pair is not an error: a point of the intersection lies in every pose of both roles, so the two
witnesses are the SAME square (`shared_point_same_square`) -- the node is DEAD (C) with that point
as the certificate.  Nothing downstream is computed on a node whose invariant did not pass.
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import numpy as np                                               # noqa: E402
import pinclip as PCLIP                                          # noqa: E402  A131 (read-only)
import polycore as PC                                            # noqa: E402  A132 (read-only)
import polylane as PL                                            # noqa: E402  A141 (read-only)
import lanelib as L                                              # noqa: E402  A118 (read-only)
from caselp import Box, t_lo, t_hi                               # noqa: E402  A57  (read-only)

S_RAT = K.S_RAT
HALF = Fr(1, 2)
MAXV = 24
_PC_CACHE = {}
_PC_CACHE_MAX = 40000


# ===================================================================== exact polygon helpers
def _clip_halfplane(P, nx, ny, b):
    """keep {p : nx*px + ny*py <= b} of a convex polygon P (rational), Sutherland-Hodgman."""
    out = []
    m = len(P)
    for i in range(m):
        p, q = P[i], P[(i + 1) % m]
        dp = nx * p[0] + ny * p[1] - b
        dq = nx * q[0] + ny * q[1] - b
        if dp <= 0:
            out.append(p)
        if (dp < 0 < dq) or (dq < 0 < dp):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def poly_intersect(P, Q):
    """exact intersection of two convex polygons (ccw rational vertex lists)."""
    R = list(P)
    m = len(Q)
    for i in range(m):
        a, b = Q[i], Q[(i + 1) % m]
        ex, ey = b[0] - a[0], b[1] - a[1]
        nx, ny = ey, -ex                                        # outward normal for ccw
        R = _clip_halfplane(R, nx, ny, nx * a[0] + ny * a[1])
        if not R:
            return []
    # drop duplicate consecutive vertices
    out = []
    for p in R:
        if not out or p != out[-1]:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def poly_area(P):
    if len(P) < 3:
        return Fr(0)
    s = Fr(0)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        s += a[0] * b[1] - b[0] * a[1]
    return s / 2


def poly_centroid(P):
    A = poly_area(P)
    if A == 0:
        xs = [p[0] for p in P]
        ys = [p[1] for p in P]
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    cx = cy = Fr(0)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        w = a[0] * b[1] - b[0] * a[1]
        cx += (a[0] + b[0]) * w
        cy += (a[1] + b[1]) * w
    return (cx / (6 * A), cy / (6 * A))


def polys_interior_disjoint(P, Q):
    """EXACT SAT over both polygons' edge normals: (disjoint, best_gap)."""
    best = None
    for A in (P, Q):
        m = len(A)
        for i in range(m):
            a, b = A[i], A[(i + 1) % m]
            nx, ny = b[1] - a[1], a[0] - b[0]
            if nx == 0 and ny == 0:
                continue
            pa = [nx * p[0] + ny * p[1] for p in P]
            pb = [nx * p[0] + ny * p[1] for p in Q]
            g = max(min(pb) - max(pa), min(pa) - max(pb))      # > 0 separated on this axis (unnormalised)
            best = g if best is None else max(best, g)
            if g >= 0:
                return True, g
    return False, best


def poly_in_container(P):
    return all(0 <= p[0] <= S_RAT and 0 <= p[1] <= S_RAT for p in P)


# ===================================================================== the role
class Role:
    __slots__ = ("name", "pieces", "pcs", "core", "axis", "kept", "area0", "src")

    def __init__(self, name, pieces, kept=1.0, src=None):
        self.name = name
        self.pieces = list(pieces)
        self.kept = kept
        self.src = src
        self.pcs = self.core = self.axis = None
        self.area0 = None
        self.rebuild()

    @staticmethod
    def from_box(name, box, nsub=4, src=None):
        """split the tilt range into nsub sub-bins and container-clip each piece (w_min rule)."""
        pieces = []
        th0, th1 = box.th0, box.th1
        edges = [th0 + (th1 - th0) * k / nsub for k in range(nsub + 1)] if th1 > th0 else [th0, th1]
        for k in range(len(edges) - 1):
            pb = Box(box.x0, box.x1, box.y0, box.y1, edges[k], edges[k + 1])
            cb = container_clip(pb)
            if cb is not None:
                pieces.append(cb)
        r = Role.__new__(Role)
        r.name, r.pieces, r.kept, r.src = name, pieces, 1.0, (src if src is not None else K.bx(box))
        r.pcs = r.core = r.axis = None
        r.area0 = vol(box)
        r.rebuild()
        return r

    def empty(self):
        return not self.pieces or self.core is None or len(self.core) < 3

    def bbox(self):
        P = self.pieces
        return Box(min(b.x0 for b in P), max(b.x1 for b in P), min(b.y0 for b in P),
                   max(b.y1 for b in P), min(b.th0 for b in P), max(b.th1 for b in P))

    def rebuild(self):
        if not self.pieces:
            self.pcs, self.core, self.axis = [], None, (Fr(0), Fr(0), Fr(0))
            return
        # A181: PC.build is pure and deterministic; the same piece is rebuilt many times per node (the
        # seeded roles, then the fixed point, then every sibling seeded from the same parent), so the
        # per-piece K' is cached per process, keyed by the exact float box and max_v (bounded size).
        mv = 40 if self.name == "H" else MAXV
        self.pcs = []
        for b in self.pieces:
            key = (tuple(K.bx(b)), mv)
            pc = _PC_CACHE.get(key)
            if pc is None:
                pc = PC.build(b, max_v=mv)
                if len(_PC_CACHE) >= _PC_CACHE_MAX:
                    _PC_CACHE.clear()
                _PC_CACHE[key] = pc
            self.pcs.append(pc)
        core = list(self.pcs[0].verts)
        for pc in self.pcs[1:]:
            core = poly_intersect(core, list(pc.verts))
            if not core:
                break
        if len(core) < 3:
            self.core, self.axis = None, (Fr(0), Fr(0), Fr(0))
            return
        # certify every vertex of the intersection against EVERY piece (exact)
        for (vx, vy) in core:
            for b in self.pieces:
                if not PC.vertex_ok(vx, vy, b):
                    raise RuntimeError("core vertex fails vertex_ok on a piece of %s" % self.name)
        self.core = core
        self.axis = axis_core_in_poly(core, self.pieces)

    def kept_frac(self):
        return float(sum(vol(b) for b in self.pieces) / self.area0) if self.area0 else 1.0

    def json(self):
        kx, ky, a = self.axis
        return dict(name=self.name, pieces=[K.bx(b) for b in self.pieces],
                    slack=[float(piece_slack(b)) for b in self.pieces],
                    box=K.bx(self.bbox()) if self.pieces else None, src=self.src,
                    kept=self.kept_frac(),
                    core=[[str(v[0]), str(v[1])] for v in (self.core or [])],
                    core_area=float(poly_area(self.core)) if self.core else 0.0,
                    axis_core=dict(kx=str(kx), ky=str(ky), a=str(a), a_float=float(a)),
                    kprime=dict(verts=[[str(v[0]), str(v[1])] for v in (self.core or [])],
                                n_verts=len(self.core or []),
                                area=float(poly_area(self.core)) if self.core else 0.0))

    @staticmethod
    def from_json(d):
        r = Role(d["name"], [Box(*p) for p in d["pieces"]], src=d.get("src"))
        return r


def vol(b):
    return Fr(b.x1 - b.x0) * Fr(b.y1 - b.y0) * Fr(b.th1 - b.th0) if b.th1 > b.th0 else Fr(0)


def piece_slack(b):
    """(w_max - w_min)/2 over the piece's tilt range: the container-clip residual."""
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    lo, hi = K.CL().cs_min_exact(t0, t1), K.CL().cs_max_exact(t0, t1)
    return (hi - lo) / 2


def container_clip(b):
    """A131's container rule per piece: centres in [w_min/2, s0 - w_min/2]^2 (exact)."""
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    o = PCLIP.Oct(t0, t1, Fr(1, 4))
    rect, _ = PCLIP.clip_rect(PCLIP.outer_rect(b), [], o, S_RAT)
    if rect is None:
        return None
    x0, x1 = max(b.x0, float(rect[0])), min(b.x1, float(rect[1]))
    y0, y1 = max(b.y0, float(rect[2])), min(b.y1, float(rect[3]))
    if x1 <= x0 or y1 <= y0:
        return None
    return Box(x0, x1, y0, y1, b.th0, b.th1)


def _inside(P, x, y):
    m = len(P)
    for i in range(m):
        a, b = P[i], P[(i + 1) % m]
        if (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]) < 0:
            return False
    return True


def axis_core_in_poly(core, pieces, iters=44):
    """the largest axis square about the core's centroid inside the core; corners certified
    (vertex_ok) against every piece.  Exact rational output."""
    cx, cy = poly_centroid(core)
    if not _inside(core, cx, cy):
        return (cx, cy, Fr(0))
    lo, hi = Fr(0), HALF
    for _ in range(iters):
        mid = (lo + hi) / 2
        if all(_inside(core, cx + sx * mid, cy + sy * mid) for sx in (-1, 1) for sy in (-1, 1)):
            lo = mid
        else:
            hi = mid
    a = Fr(int(lo * 10 ** 12), 10 ** 12)
    for _ in range(6):
        if a <= 0:
            return (cx, cy, Fr(0))
        if all(PC.vertex_ok(cx + sx * a, cy + sy * a, b) for b in pieces
               for sx in (-1, 1) for sy in (-1, 1)):
            return (cx, cy, a)
        a -= Fr(1, 10 ** 9)
    return (cx, cy, Fr(0))


# ===================================================================== the clip and the fixed point
def clip_piece(b, cores, trace=None):
    """clip ONE piece (its own tilt range = the sub-bin) against the axis cores [(kx, ky, a)]
    with A131's exact predicates.  Returns the clipped piece or None."""
    t0, t1 = t_lo(b.th0), t_hi(b.th1)
    rect = PCLIP.outer_rect(b)
    stats = {"exact_calls": 0, "backoffs": 0}
    for (kx, ky, a) in cores:
        if a <= 0 or rect is None:
            continue
        o = PCLIP.Oct(t0, t1, a)
        rect, _ = PCLIP.clip_rect(rect, [(kx, ky)], o, S_RAT, stats=stats, trace=trace)
    if rect is None:
        return None
    x0, x1 = max(b.x0, float(rect[0])), min(b.x1, float(rect[1]))
    y0, y1 = max(b.y0, float(rect[2])), min(b.y1, float(rect[3]))
    if x1 <= x0 or y1 <= y0:
        return None
    return Box(x0, x1, y0, y1, b.th0, b.th1)


def normalise(roles, passes=8, fixed=()):
    """(i) container clip is in Role.from_box; (ii) mutual clip of every piece of every role against
    every OTHER role's axis core, K' and axis cores recomputed after each pass, until nothing moves;
    (iii) done inside rebuild.  Returns (roles or None, report)."""
    rep = dict(passes=0, dead=None, kept={}, moved=[])
    for p in range(passes):
        moved = False
        for i, r in enumerate(roles):
            if r.name in fixed:
                continue
            cores = [o.axis for j, o in enumerate(roles) if j != i and o.axis[2] > 0]
            new = []
            changed = False
            for b in r.pieces:
                nb = clip_piece(b, cores)
                if nb is None:
                    changed = True
                    continue
                if K.bx(nb) != K.bx(b):
                    changed = True
                new.append(nb)
            if changed:
                moved = True
                r.pieces = new
                r.rebuild()
                if r.empty():
                    rep["dead"] = "role %s EMPTY after the mutual clip (pass %d)" % (r.name, p)
                    rep["passes"] = p + 1
                    rep["kept"] = {q.name: q.kept_frac() for q in roles}
                    return None, rep
        rep["passes"] = p + 1
        if not moved:
            break
    rep["kept"] = {q.name: q.kept_frac() for q in roles}
    return roles, rep


def invariant(roles):
    """(iv) every K'(role) inside the container; every pair interior-disjoint (exact).  A failing
    pair yields the PAIR certificate (a rational point in both cores)."""
    out = dict(ok=True, container=[], pairs=[], dead=None, witness=None)
    for r in roles:
        inc = bool(r.core) and poly_in_container(r.core)
        out["container"].append(dict(role=r.name, inside=inc))
        if not inc:
            out["ok"] = False
            out["dead"] = "K'(%s) not inside the container (or empty)" % r.name
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            a, b = roles[i], roles[j]
            if not a.core or not b.core:
                continue
            dj, g = polys_interior_disjoint(a.core, b.core)
            out["pairs"].append(dict(i=a.name, j=b.name, disjoint=bool(dj), gap=str(g)))
            if not dj:
                out["ok"] = False
                I = poly_intersect(a.core, b.core)
                if I:
                    w = poly_centroid(I)
                    wq = (Fr(round(w[0] * 10 ** 9), 10 ** 9), Fr(round(w[1] * 10 ** 9), 10 ** 9))
                    cert = all(PC.vertex_ok(wq[0], wq[1], pb) for pb in a.pieces + b.pieces)
                    out["witness"] = dict(pair=[a.name, b.name], w=[str(wq[0]), str(wq[1])],
                                          certified=bool(cert))
                out["dead"] = "K'(%s) meets K'(%s): shared point => same square (PAIR)" % (a.name, b.name)
    return out


def ovl_roles(a, b):
    """every piece pair always overlaps (A118) -> the two roles cannot be distinct squares."""
    return all(L.pair_always_overlap(pa, pb) for pa in a.pieces for pb in b.pieces)


def pair_leaves(roles):
    """OVL on every role pair (the invariant already did PAIR).  Returns (dead_reason or None)."""
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            if ovl_roles(roles[i], roles[j]):
                return "OVL: every pose of %s overlaps every pose of %s (A118 1.2(ii))" % (
                    roles[i].name, roles[j].name)
    return None


def make_node(roles, nsub=4, passes=8):
    """the whole (i)-(iv) at a node.  Returns (roles or None, report) with report.dead set on a
    DEAD node and report.invariant the assertion record.

    A176: the DEFAULT is now the library's POLYGON-obstacle clip with the LONELY clip at every
    corner role (polyclip175.make_node on A171's fixed multibox >= 13f23204: container clip,
    lonely clip, refine-2 bisection against every other role's K' polygon, mutual clip to a fixed
    point, then this module's own K'/axis rebuild, invariant and OVL as the cross-check).  The
    axis-core clip below is kept only behind A168_LEGACY_CLIP=1 (the A168 record's own rule)."""
    if os.environ.get("A168_LEGACY_CLIP", "0") != "1":
        import polyclip175 as PX                                  # lazy: polyclip175 imports this module
        return PX.make_node(roles, refine=int(os.environ.get("A176_REFINE", "2")))
    return make_node_legacy(roles, nsub=nsub, passes=passes)


def make_node_legacy(roles, nsub=4, passes=8):
    """A168's axis-core clip (the record's rule before A175/A176)."""
    roles, rep = normalise(roles, passes=passes)
    if roles is None:
        rep["invariant"] = None
        return None, rep
    inv = invariant(roles)
    rep["invariant"] = inv
    if not inv["ok"]:
        rep["dead"] = inv["dead"]
        rep["witness"] = inv.get("witness")
        return None, rep
    d = pair_leaves(roles)
    if d is not None:
        rep["dead"] = d
        return None, rep
    return roles, rep


def roles_json(roles):
    return {r.name: r.json() for r in roles}


def roles_from_json(d):
    return [Role.from_json(v) for v in d.values()]


def minchord_role(role, line):
    return min(K.minchord(b, line) for b in role.pieces)


def chord_row(roles, line):
    mcs = [minchord_role(r, line) for r in roles]
    rhs = S_RAT - sum(mcs, Fr(0))
    return dict(off=str(line.off), off_f=float(line.off), orient=line.orient,
                minchords=[str(m) for m in mcs], minchords_f=[float(m) for m in mcs],
                rhs=str(rhs), rhs_f=float(rhs), beta=(int(math.floor(rhs)) if rhs >= 0 else -1))


def best_row(roles, lines):
    best = None
    for ln in lines:
        r = chord_row(roles, ln)
        if best is None or Fr(r["rhs"]) < Fr(best["rhs"]):
            best = r
    return best


# ===================================================================== the role-aware cover (A141's shape)
def _witness(b, roles):
    """a rational point in every pose of `b` AND in every pose of every piece of some role: then a
    square with pose in b IS that role's square (shared_point_same_square).  Candidates: the role's
    core vertices pulled inward and its centroid; certified exactly."""
    best = None
    for r in roles:
        if not r.core:
            continue
        c = poly_centroid(r.core)
        cands = [c] + [((v[0] * 17 + c[0] * 3) / 20, (v[1] * 17 + c[1] * 3) / 20) for v in r.core]
        W = np.array([[float(p[0]), float(p[1])] for p in cands])
        mb = PL.point_margin_many(W, b)
        k = int(np.argmax(mb))
        if mb[k] > PL.MARGIN and (best is None or mb[k] > best[0]):
            best = (float(mb[k]), r, cands[k])
    if best is None:
        # the concave refinement against the role's bbox (a superset of the pieces): sound
        for r in roles:
            w, f, _mb, _mj = PL.best_shared_point(b, r.bbox())
            if w is not None and f > PL.MARGIN:
                wq = PL.rationalise(w)
                if PC.vertex_ok(wq[0], wq[1], b) and all(PC.vertex_ok(wq[0], wq[1], pb) for pb in r.pieces):
                    return r.name, [str(wq[0]), str(wq[1])]
        return None
    _f, r, w = best
    wq = (Fr(round(float(w[0]) * 10 ** 9), 10 ** 9), Fr(round(float(w[1]) * 10 ** 9), 10 ** 9))
    if PC.vertex_ok(wq[0], wq[1], b) and all(PC.vertex_ok(wq[0], wq[1], pb) for pb in r.pieces):
        return r.name, [str(wq[0]), str(wq[1])]
    return None


def cover(root, cell, roles, line=None, band_mode=None, depth=8, max_open=6000, lane_pairs=True,
          max_depth=30):
    """a COMPLETE prefix-code cover of `root`: every box discharged by container / band|not_band /
    misses_cell (exact) / witness (role-aware), or kept open at `depth`.  With `lane_pairs` the open
    set is pair-tested (A118): lane = 0 (empty), 1 (every pair always overlaps) or None."""
    leaves, open_ = [], []
    stack = [("", root)]
    CL = K.CL()
    while stack:
        p, b = stack.pop()
        if PL.box_outside_container(b, K.S0):
            leaves.append(dict(path=p, box=K.bx(b), why="container"))
            continue
        if line is not None and band_mode == "band":
            ok, det = CL.not_band_ok(b, line)
            if ok:
                leaves.append(dict(path=p, box=K.bx(b), why="not_band", **det))
                continue
        if line is not None and band_mode == "out":
            ok, det = CL.band_ok(b, line)
            if ok:
                leaves.append(dict(path=p, box=K.bx(b), why="band", **det))
                continue
        if cell is not None:
            ok, det = CL.box_misses_cell_exact(b, cell)
            if ok:
                leaves.append(dict(path=p, box=K.bx(b), why="misses_cell", **(det or {})))
                continue
        w = _witness(b, roles)
        if w is not None:
            leaves.append(dict(path=p, box=K.bx(b), why="witness", j=w[0], w=w[1]))
            continue
        if len(p) >= depth:
            open_.append((p, b))
            if len(open_) > max_open:
                return dict(complete=False, reason="open budget exhausted", leaves=leaves,
                            open=[dict(path=q, box=K.bx(bb)) for q, bb in open_], lane=None,
                            root=K.bx(root))
            continue
        b0, b1 = PL.split_box(b)
        stack.append((p + "0", b0))
        stack.append((p + "1", b1))
    lane = None
    if lane_pairs:
        if not open_:
            lane = 0
        elif len(open_) <= 4000:
            bxs = [bb for _, bb in open_]
            BAD = ~L.pairs_always_overlap_matrix(bxs)
            if BAD.any():
                ii, jj = np.nonzero(np.triu(BAD))
                if len(ii) <= 60000:
                    for (u, v) in zip(ii.tolist(), jj.tolist()):
                        if L.pair_always_overlap(bxs[u], bxs[v]):
                            BAD[u, v] = BAD[v, u] = False
            lane = 1 if not BAD.any() else None
    return dict(complete=True, reason=None, leaves=leaves,
                open=[dict(path=q, box=K.bx(bb)) for q, bb in open_], lane=lane, root=K.bx(root))


def admissible_hull(role, n=400, seed=0):
    """the hull of the squares at ADMISSIBLE sampled poses of the role's pieces (drawing aid; it
    cannot leave the container because inadmissible poses are dropped)."""
    rng = np.random.default_rng(seed)
    pts = []
    for b in role.pieces:
        for cx in (b.x0, b.x1):
            for cy in (b.y0, b.y1):
                for t in np.linspace(b.th0, b.th1, 5):
                    th = math.radians(t)
                    h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
                    if h <= cx <= K.S0 - h and h <= cy <= K.S0 - h:
                        pts += K.sq_verts(cx, cy, th)
        C, T = K.sample_poses_in(b, n, rng)
        h = 0.5 * (np.abs(np.cos(T)) + np.abs(np.sin(T)))
        ok = (C[:, 0] >= h) & (C[:, 0] <= K.S0 - h) & (C[:, 1] >= h) & (C[:, 1] <= K.S0 - h)
        for (cx, cy), th in zip(C[ok], T[ok]):
            pts += K.sq_verts(cx, cy, th)
    return pts
