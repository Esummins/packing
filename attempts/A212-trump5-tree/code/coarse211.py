"""A211 -- the COARSE node (notes/coarse_tree.md, soundness points S1-S4): A207's TreePage207 (A206 Rule NS + A205's
clips + A204's cascade + the basin clip) with a `coarse` switch.  In coarse mode (every INTERNAL node):
  * every non-pin role with more than CAP pieces is RE-BINNED onto NX x NY sub-rects x NB tilt bins of its own hull
    (exact rationals); a unit is kept iff it meets some piece, so the union of the units is a SUPERSET of the union of
    the pieces (S1: sound, weaker);
  * the polygon fixed point runs with refine REFINE, at most MAX_ITER mutual-clip passes, NO lonely clip, K' rebuilt
    in KMODE ("pieces" = A172's per-piece intersection, "union" = A171's union-hull polygon: both certified, the
    union one weaker) -- a PREFIX of A204's clip chain (S2: any prefix of a chain of sound clips is sound);
  * the option table's reach bisects DEPTH levels per cell (JDEPTH for joint slot sets) instead of A198's 5 / 2, and a
    role's reach is clipped in place (depth 0) -- a shallower bisection keeps a superset (S3);
  * the basin clip is off (it returns with the exact leaf cascade; skipping a clip keeps more: S2).
In exact mode (the leaf's cascade, rule (e)) everything is A209's: nsub 4 / refine 2, lonely clip, the basins, depth
5 / 2, the sharp round.  Every coarse DEAD is a genuine DEAD (every test is a sound necessary condition); a coarse
ALIVE only says "branch further"."""
import time
from fractions import Fraction as Fr

import poly204 as P
import tree207 as N7

FP, MB = P.FP, P.MB
NX, NY, NB = 4, 4, 6                     # the coarse grid: 16 sub-rects x 6 tilt bins
CAP = 96                                 # a role carrying more pieces than this is re-binned (<= NX*NY*NB units)
REFINE, MAX_ITER, NSUB = 1, 2, 2         # the coarse fixed point: refine 1, <= 2 mutual passes, nsub 2 for box-only roles
DEPTH, JDEPTH = 2, 1                     # the coarse reach depths (A198: 5 / 2)
KMODE = "pieces"                         # "pieces" (A172) or "union" (A171's box-only K')
EXACT = dict(depth=5, joint_depth=2, refine_mb=2, nsub_mb=4)
_BINS = {}


def mkbin(a, b):
    k = (a, b)
    if k not in _BINS:
        _BINS[k] = MB.Bin(a, b)
    return _BINS[k]


def _ov(a0, a1, b0, b1):
    """the intervals meet (open overlap; a degenerate interval counts when it lies inside the other)."""
    return max(a0, b0) < min(a1, b1) or (a0 == a1 and b0 <= a0 <= b1) or (b0 == b1 and a0 <= b0 <= a1)


def rebin(pcs, nx=NX, ny=NY, nb=NB):
    """the pieces re-gridded onto nx x ny x nb units of their hull; a unit is kept iff it meets some piece (S1)."""
    x0, x1, y0, y1, t0, t1 = FP.pieces_hull(pcs)
    xs = [x0 + (x1 - x0) * Fr(i, nx) for i in range(nx + 1)]
    ys = [y0 + (y1 - y0) * Fr(j, ny) for j in range(ny + 1)]
    ts = MB.sub_bins(t0, t1, nb)
    out = []
    for i in range(nx):
        for j in range(ny):
            u = (xs[i], xs[i + 1], ys[j], ys[j + 1])
            hit = [(b, r) for b, r in pcs if _ov(r[0], r[1], u[0], u[1]) and _ov(r[2], r[3], u[2], u[3])]
            if not hit:
                continue
            for (a, c) in ts:
                if any(_ov(b.t0, b.t1, a, c) for b, _ in hit):
                    out.append((mkbin(a, c), u))
    return out


def coarse_fixpoint(nd, corners, s, refine=REFINE, max_iter=MAX_ITER, max_pieces=96, near=True):
    """A204's fixpoint (poly204.fixpoint) with the lonely clip OFF, refine / max_iter capped and K' in KMODE (S2)."""
    names = nd.names
    st = nd.stats
    rep = dict(lonely=[], passes=0, refine=refine, coarse=True, kmode=KMODE)

    def clip_all(cur, bn, k, obst):
        for j in names:
            if j == k or cur is None:
                continue
            ob = obst[j]
            if ob is None or (near and not FP.obstacle_near(ob, cur)):
                continue
            cur = MB._clip_rect_obstacle(cur, ob, bn, st)
        return cur

    for mb in nd.boxes.values():
        keep = []
        for (bn, r) in mb.pieces:
            nr, _sl = MB.container_clip(r, bn, s, strict=False)
            if nr is not None:
                keep.append((bn, nr))
        if not keep:
            raise MB.EmptyBox(mb.name, dict(reason="container"))
        mb.pieces = keep
        mb.kmode = KMODE
    for lvl in range(max(0, refine)):
        for mb in nd.boxes.values():
            mb.rebuild()
        obst = {k: nd.boxes[k].obstacle("poly") for k in names}
        for k in names:
            mb = nd.boxes[k]
            if len(mb.pieces) * 2 > max_pieces:
                continue
            new = []
            for (bn, r) in mb.pieces:
                for (bn2, r2) in MB.split_piece(bn, r):
                    cur, _sl = MB.container_clip(r2, bn2, s, strict=False)
                    cur = clip_all(cur, bn2, k, obst)
                    if cur is not None:
                        new.append((bn2, cur))
            if not new:
                raise MB.EmptyBox(mb.name, dict(reason="refine", level=lvl + 1))
            mb.pieces = new
    vprev = sum(P.vol(mb.pieces) for mb in nd.boxes.values())
    for it in range(max_iter):
        moved = False
        for mb in nd.boxes.values():
            mb.rebuild()
        obst = {k: nd.boxes[k].obstacle("poly") for k in names}
        for k in names:
            mb = nd.boxes[k]
            keep = []
            for (bn, r) in mb.pieces:
                cur = clip_all(r, bn, k, obst)
                if cur != r:
                    moved = True
                if cur is not None:
                    keep.append((bn, cur))
            if not keep:
                raise MB.EmptyBox(mb.name, dict(reason="mutual", pass_=it + 1))
            mb.pieces = keep
        rep["passes"] = it + 1
        vnow = sum(P.vol(mb.pieces) for mb in nd.boxes.values())
        if not moved or vnow > vprev * (1 - Fr(1, 1000)):
            rep["stopped"] = "moved < 0.1%" if moved else "fixed"
            break
        vprev = vnow
    for mb in nd.boxes.values():
        mb.rebuild()
        mb.kept = mb.kept_fraction()
    nd.normalised = True
    return rep


class CoarsePage(N7.TreePage207):
    def __init__(self, *a, **kw):
        N7.TreePage207.__init__(self, *a, **kw)
        self.all_basins = list(self.basins)
        self.rebin_rep = []
        self.coarse = None
        self.set_coarse(True)

    def set_coarse(self, on):
        self.coarse = bool(on)
        if on:
            self.depth, self.joint_depth, self.refine_mb, self.nsub_mb = DEPTH, JDEPTH, REFINE, NSUB
            self.basins = []
        else:
            self.depth, self.joint_depth, self.refine_mb, self.nsub_mb = EXACT["depth"], EXACT["joint_depth"], EXACT["refine_mb"], EXACT["nsub_mb"]
            self.basins = list(self.all_basins)

    def normalise(self, label):
        if not self.coarse:
            return N7.TreePage207.normalise(self, label)
        t0 = time.time()
        for k, pcs in list(self.pieces.items()):
            if k.startswith("P") or not pcs or len(pcs) <= CAP:
                continue
            new = rebin(pcs)
            self.pieces[k] = new
            self.rebin_rep.append(dict(label=label, role=k, n_before=len(pcs), n_after=len(new)))
            self.T.test("REBIN", role=k, label=label, n_before=len(pcs), n_after=len(new), grid=[NX, NY, NB])
        self.T.step("rebin", time.time() - t0, label=label)
        old = P.fixpoint
        P.fixpoint = coarse_fixpoint
        try:
            return N7.TreePage207.normalise(self, label)
        finally:
            P.fixpoint = old

    def role_reach(self, role, S):
        if not self.coarse:
            return N7.TreePage207.role_reach(self, role, S)
        key = (role, S)
        if key in self.reach_cache:
            return self.reach_cache[key]
        pcs = self.nd.boxes[role].pieces
        t0 = time.time()
        res = FP.bisect_region(None, self.obstacles_except(role), [self.item[p]["wb"] for p in S], self.s, self.nd.stats, depth=0, seed_pieces=pcs, max_pieces=4096)
        self.T.test("ROLE-REACH", role=role, slots=sorted(S), depth=0, coarse=True, frac=round(res[0], 6), n_pieces=len(res[1]), n_exact=res[2], seconds=round(time.time() - t0, 3))
        self.reach_cache[key] = res
        return res


def save_state(pg):
    st = N7.save_state(pg)
    st["coarse"], st["rebin_rep"], st["noroom_k"] = pg.coarse, list(pg.rebin_rep), getattr(pg, "noroom_k", None)
    return st


def restore_state(pg, st):
    N7.restore_state(pg, st)
    pg.set_coarse(st["coarse"])
    pg.rebin_rep = list(st["rebin_rep"])
    pg.noroom_k = st.get("noroom_k")


def install():
    """route the tree's save / restore through the coarse flag (after tree207.install)."""
    import tree206 as N6
    N7.install()
    N6.save_state = save_state
    N6.restore_state = restore_state
