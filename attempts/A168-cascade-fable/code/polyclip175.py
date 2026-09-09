"""A175 -- the POLYGON clip for the cascade's roles (the coordinator's defect, 2026-09-09).

`roles168.normalise` clipped every piece only against the other roles' AXIS CORES (`Role.axis`, the
largest axis square inside K'(role)); the polygon K'(role) itself -- the certified object, much
larger than its inscribed axis square -- was never an obstacle, so the clip barely propagated
upstream (on the recorded node l1_104 root/D0/S1/B0 A168 kept H 1.00 / D 1.00 / S 1.00 / B 0.60;
with polygon obstacles H loses every pose: DEAD by the pair leaf).

This module drives A171/A172/A173's primitives (`attempts/A171-multibox-invariant/code/multibox.py`,
READ-ONLY -- A173 is editing it; imported, never copied) on roles168's PIECES:

  * every piece (a caselp.Box, its own tilt sub-bin) becomes an A171 piece (Bin(t_lo, t_hi) x the
    exact rational rect of its float coordinates -- a superset [T]);
  * the SOUND container clip (w_min; `strict_container=False`), then A173's LONELY CLIP on every
    corner role (A169 Theorem B / R3 as a per-piece clip: centre slabs and tilt halves certified
    lonely at the K0-WIDEN box c = 1 + w are removed) BEFORE anything reads K';
  * `refine` levels of tautologous bisection (`split_piece`) interleaved with the clip against the
    POLYGON obstacles (`MBox.obstacle("poly")` = A172's per-piece K', every vertex certified by
    `polycore.vertex_ok` against every piece), then the lonely + mutual clip to a fixed point,
    K' rebuilt from the survivors after every pass;
  * `EmptyBox` = the pair-leaf kill, with the emptied box's replayable slab trace as the certificate.

Back in roles168's world every surviving piece is rounded OUTWARD to floats (`piece_box`) and
intersected with the piece it came from (sound both ways), the role is rebuilt (roles168's own
per-piece K', exact intersection, vertex_ok-certified, axis core: the CROSS-CHECK of A171's K'),
and the invariant (K' inside the container, pairwise interior-disjoint, exact) and OVL are
asserted exactly as before.  Kept fractions are now relative to the role's SOURCE box (roles168's
`Role.from_json` lost `area0`, which is why every reloaded role printed kept 1.00).
"""
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import resume168 as RS                                           # noqa: E402
sys.path.insert(0, os.path.join(K.ATT, "A171-multibox-invariant", "code"))
import multibox as MB                                            # noqa: E402  A171+A172+A173 (read-only)
from caselp import Box, t_lo, t_hi                               # noqa: E402

assert hasattr(MB, "lonely_clip"), "A173's lonely_clip is not in multibox.py"
assert MB.C_WIDEN == RS.C_RAT, "K0-WIDEN constant mismatch between multibox and resume168"

CORNER_OF = {"D": "TR", "S": "TR", "B": "BR", "Bp": "BR", "T1": "TL", "T2": "TL", "L1": "BL", "L2": "BL"}


def role_to_mbox(role):
    """an A171 MBox carrying the role's CURRENT pieces (not re-split from a box)."""
    src = Box(*role.src) if role.src is not None else role.bbox()
    mb = MB.MBox(role.name, src)
    mb.pieces = [(MB.Bin(t_lo(b.th0), t_hi(b.th1)), (Fr(b.x0), Fr(b.x1), Fr(b.y0), Fr(b.y1)))
                 for b in role.pieces]
    mb.kmode = "pieces"
    mb.trace = []
    mb.sliver_area = Fr(0)
    mb.lonely_removed = 0.0
    return mb


def inter(q, k):
    x0, x1 = max(q.x0, k.x0), min(q.x1, k.x1)
    y0, y1 = max(q.y0, k.y0), min(q.y1, k.y1)
    t0, t1 = max(q.th0, k.th0), min(q.th1, k.th1)
    if x1 <= x0 or y1 <= y0 or t1 < t0 or (t1 == t0 and q.th1 > q.th0):
        return None
    return Box(x0, x1, y0, y1, t0, t1)


def mbox_to_pieces(mb, old_pieces):
    """surviving A171 pieces -> caselp.Boxes (outward float rounding, then intersected with the
    piece of the role they came from -- the unique old piece whose rational t-range contains the
    survivor's sub-bin; every split is nested -- so the result is a subset of both, hence sound;
    if the origin is ambiguous every old piece is tried)."""
    out = []
    rng = [(t_lo(q.th0), t_hi(q.th1), q) for q in old_pieces]
    for (bn, r) in mb.pieces:
        pb, _t0, _t1 = MB.piece_box(bn, r)
        cands = [q for (a, b, q) in rng if a <= bn.t0 and bn.t1 <= b]
        if len(cands) != 1:
            cands = old_pieces
        for q in cands:
            x = inter(pb, q)
            if x is not None:
                out.append(x)
    return out


def poly_normalise(roles, refine=2, max_iter=10, max_pieces=96, lonely=True, lonely_refine=0,
                   corners=None, verbose=False):
    """A171's `Node.normalise` (mode="poly", kmode="pieces", strict_container=False, corners=...)
    on roles168 pieces.  Returns (mboxes, report) or raises MB.EmptyBox."""
    s = K.S_RAT
    mbs = {r.name: role_to_mbox(r) for r in roles}
    try:
        return _poly_normalise(mbs, s, refine, max_iter, max_pieces, lonely, lonely_refine, corners, verbose)
    except MB.EmptyBox as e:
        e.mbs = mbs                                              # the traces are the certificate
        raise


def _poly_normalise(mbs, s, refine, max_iter, max_pieces, lonely, lonely_refine, corners, verbose):
    names = list(mbs)
    stats = dict(exact_calls=0, backoffs=0, passes=0)
    cspec = dict(corners or {})
    if lonely and corners is None:
        cspec = {nm: (CORNER_OF[nm], RS.C_RAT) for nm in names if nm in CORNER_OF}
    rep = dict(corners={k: v[0] for k, v in cspec.items()}, lonely=[], refine=refine, passes=0)

    def lonely_pass(tag):
        moved = False
        for nm, (corner, cc) in cspec.items():
            mb = mbs[nm]
            lr = MB.lonely_clip(mb, corner, c=cc, s=s, nsub=4, refine=lonely_refine,
                                max_pieces=max_pieces * 2, pass_=tag)
            rep["lonely"].append(dict(box=nm, stage=tag, removed=lr["removed"],
                                      dropped=lr["dropped_pieces"], n_after=lr["n_after"]))
            if lr["removed"] > 0 or lr["dropped_pieces"]:
                moved = True
        return moved

    def clip_all(cur, bn, k, obst, tr):
        for j in names:
            if j == k:
                continue
            if cur is None:
                break
            cur = MB._clip_rect_obstacle(cur, obst[j], bn, stats, trace=tr, tag=j)
        return cur

    # 1. container clip (sound, w_min)
    for mb in mbs.values():
        keep = []
        for (bn, r) in mb.pieces:
            tr = []
            nr, _sl = MB.container_clip(r, bn, s, strict=False, trace=tr)
            if tr:
                mb.trace.append(dict(pass_=0, t=[str(bn.t0), str(bn.t1)], steps=tr))
            if nr is not None:
                keep.append((bn, nr))
        if not keep:
            raise MB.EmptyBox(mb.name, dict(reason="container"))
        mb.pieces = keep
    # 1b. the lonely clip before anything reads K'
    if cspec:
        lonely_pass("container")
    # 2. refinement levels: bisect, clip against the POLYGON obstacles, drop the dead halves
    for lvl in range(max(0, refine)):
        if cspec:
            lonely_pass("refine%d" % (lvl + 1))
        for mb in mbs.values():
            mb.rebuild()
        obst = {k: mbs[k].obstacle("poly") for k in names}
        for k in names:
            mb = mbs[k]
            if len(mb.pieces) * 2 > max_pieces:
                continue
            new = []
            for (bn, r) in mb.pieces:
                for (bn2, r2) in MB.split_piece(bn, r):
                    tr = []
                    cur, _sl = MB.container_clip(r2, bn2, s, strict=False, trace=tr)
                    cur = clip_all(cur, bn2, k, obst, tr)
                    if tr:
                        mb.trace.append(dict(refine=lvl + 1, t=[str(bn2.t0), str(bn2.t1)], steps=tr))
                    if cur is not None:
                        new.append((bn2, cur))
            if not new:
                raise MB.EmptyBox(mb.name, dict(reason="refine", level=lvl + 1))
            mb.pieces = new
        if verbose:
            print("  refine %d: " % (lvl + 1) + " ".join("%s=%.4f(%dp)" % (k, mbs[k].kept_fraction(), len(mbs[k].pieces)) for k in names), flush=True)
    # 3. lonely + mutual clip to a fixed point, K' rebuilt after every pass
    for it in range(max_iter):
        moved = lonely_pass("pass%d" % (it + 1)) if cspec else False
        for mb in mbs.values():
            mb.rebuild()
        obst = {k: mbs[k].obstacle("poly") for k in names}
        for k in names:
            mb = mbs[k]
            keep = []
            for (bn, r) in mb.pieces:
                tr = []
                cur = clip_all(r, bn, k, obst, tr)
                if tr:
                    mb.trace.append(dict(pass_=it + 1, t=[str(bn.t0), str(bn.t1)], steps=tr))
                    moved = True
                if cur is not None:
                    keep.append((bn, cur))
            if not keep:
                raise MB.EmptyBox(mb.name, dict(reason="mutual", pass_=it + 1))
            mb.pieces = keep
        rep["passes"] = it + 1
        if verbose:
            print("  pass %d: kept " % (it + 1) + " ".join("%s=%.4f" % (k, mbs[k].kept_fraction()) for k in names), flush=True)
        if not moved:
            break
    for mb in mbs.values():
        mb.rebuild()
        mb.kept = mb.kept_fraction()
    rep["kept_mb"] = {k: mbs[k].kept for k in names}
    rep["k_area_mb"] = {k: (mbs[k].pc.area() if mbs[k].pc is not None else None) for k in names}
    rep["n_pieces_mb"] = {k: len(mbs[k].pieces) for k in names}
    rep["stats"] = dict(stats)
    return mbs, rep


def trace_of(mb, cap=400):
    return mb.trace[-cap:]


def make_node(roles, refine=2, max_iter=10, lonely=True, verbose=False):
    """the whole (i)-(iv) with the polygon obstacles.  Returns (roles or None, report); on a DEAD
    node report.dead names the leaf and report.cert carries the certificate (the emptied box's
    slab trace, or the PAIR witness / OVL pair)."""
    t0 = time.time()
    old = {r.name: list(r.pieces) for r in roles}
    try:
        mbs, rep = poly_normalise(roles, refine=refine, max_iter=max_iter, lonely=lonely, verbose=verbose)
    except MB.EmptyBox as e:
        rep = dict(dead="EmptyBox(%s): every pose of %s meets another role's K' at every tilt of its "
                        "sub-bin (or is lonely / outside the container) -- the pair leaf; %s" % (
                            e.name, e.name, e.detail), leaf="EmptyBox", box=e.name, detail=e.detail,
                   kept={}, invariant=None, passes=None, wall_s=round(time.time() - t0, 1))
        mbs = getattr(e, "mbs", {})
        rep["cert"] = dict(kind="EmptyBox", box=e.name, detail=e.detail,
                           trace=(trace_of(mbs[e.name]) if e.name in mbs else None),
                           pieces_at_death={k: [dict(t=[str(b.t0), str(b.t1)], rect=[str(v) for v in r])
                                                for (b, r) in mb.pieces] for k, mb in mbs.items()})
        rep["kept_mb"] = {k: mb.kept_fraction() for k, mb in mbs.items()}
        return None, rep
    new_roles = []
    for r in roles:
        pcs = mbox_to_pieces(mbs[r.name], old[r.name])
        if not pcs:
            rep.update(dead="role %s has no piece after the outward rounding" % r.name, leaf="EmptyBox",
                       cert=dict(kind="EmptyBox", box=r.name, detail="rounding"), kept={}, invariant=None)
            rep["wall_s"] = round(time.time() - t0, 1)
            return None, rep
        nr = R.Role(r.name, pcs, src=r.src)
        if nr.empty():
            rep.update(dead="K'(%s) empty on the clipped pieces" % r.name, leaf="EmptyBox",
                       cert=dict(kind="EmptyBox", box=r.name, detail="K' empty"), kept={}, invariant=None)
            rep["wall_s"] = round(time.time() - t0, 1)
            return None, rep
        new_roles.append(nr)
    rep["kept"] = {q.name: q.kept_frac() for q in new_roles}
    rep["k_area"] = {q.name: float(R.poly_area(q.core)) for q in new_roles}
    rep["n_pieces"] = {q.name: len(q.pieces) for q in new_roles}
    inv = R.invariant(new_roles)
    rep["invariant"] = inv
    if not inv["ok"]:
        rep["dead"] = inv["dead"]
        rep["leaf"] = "PAIR"
        rep["witness"] = inv.get("witness")
        rep["cert"] = dict(kind="PAIR", witness=inv.get("witness"), dead=inv["dead"])
        rep["wall_s"] = round(time.time() - t0, 1)
        return None, rep
    d = R.pair_leaves(new_roles)
    if d is not None:
        rep["dead"] = d
        rep["leaf"] = "OVL"
        rep["cert"] = dict(kind="OVL", dead=d)
        rep["wall_s"] = round(time.time() - t0, 1)
        return None, rep
    rep["dead"] = None
    rep["wall_s"] = round(time.time() - t0, 1)
    return new_roles, rep


def _patch_roles168():
    """roles168.Role.from_json lost area0 (kept 1.00 on every reloaded role): kept relative to src."""
    orig_init = R.Role.__init__

    def init(self, name, pieces, kept=1.0, src=None):
        orig_init(self, name, pieces, kept=kept, src=src)
        if src is not None and self.area0 is None:
            self.area0 = R.vol(Box(*src))
    R.Role.__init__ = init


_patch_roles168()
