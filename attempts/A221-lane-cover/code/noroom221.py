"""A221 -- the POCKET COVER that decides the k = n-1 no-room nodes, and pocket INHERITANCE.

Everything here is n-general: `n` is the number of unit squares, `k` the number of boxed roles of the node,
m = n - k the number of free squares left.  A171 (multibox), A189 (noroom189), A141/A161 (the lane) are READ-ONLY
libraries -- this module wraps them and never edits them.

--------------------------------------------------------------------------------------------------------------
LEMMA POCKET-DEAD [T] (the object A189's Lemma 1 was approximating).
Let P_1..P_r be axis-aligned rectangles whose union contains the CENTRE of every free pose (A189's `pockets_of`
gives such a cover from the bisection residue: every dropped piece is certified "every pose in it meets some
core").  Say a pocket P is DEAD when every pose (c, th) with c in P and th in [0, 180) meets some core K'(role).
    If every P_j is DEAD then the node has NO free square at all, hence it is DEAD for EVERY m >= 1.
Proof: a free square's centre lies in some P_j (the cover), and its pose is then excluded by P_j's certificate. []
The pocket certificate is the SAME exact machine A189's bisection uses -- `multibox._clip_rect_obstacle`, the exact
convex dead-set clip, with `multibox.container_clip(strict=False)` on top (a pose of tilt sub-bin [t0,t1] has
w(th) >= w_min, so its centre lies in [w_min/2, s - w_min/2]^2: sound) -- but ROOTED AT THE POCKET instead of at the
whole container.  That is the whole difference in cost: A189 spends its budget bisecting the container
([1/2, s-1/2]^2, area ~8.4 at s = 3.877) and then hands the leftovers to a lane cover whose root is the pocket's
MEETING window (the pocket grown by 1/sqrt(2) on every side, area ~3.5 for a pocket of area 0.2) -- 17x the pocket.
Rooted at the pocket, the same clip reaches ~4 more halvings per coordinate for the same piece count.

LEMMA POCKET-INHERIT [T].  Let a child node arise from its parent by (a) Rule NS (a role's box is replaced by a
meet/miss subset), (b) ROLE-SPLIT (a role's box replaced by one half), or (c) POCKET instantiation (a NEW role is
added, the others unchanged).  In each case every role of the parent has, in the child, a box CONTAINED in the
parent's.  A172's K' is an intersection over the surviving poses, so shrinking a role's box can only ENLARGE its
K'; hence K'_parent(role) is contained in K'_child(role) for every parent role, and a pose excluded by the parent's
cores is excluded by the child's.  So
    { free poses of the child }  is contained in  { free poses of the parent },
and THE PARENT'S POCKETS COVER THE CHILD'S FREE CENTRES.
Consequence (`noroom_child`): a child may skip the container-wide bisection entirely and run the pocket cover of
LEMMA POCKET-DEAD on its PARENT'S pockets with its OWN (larger) cores.  Only if some inherited pocket survives does
it pay for a fresh global bisection.  This is sound for every m; for m = 1 it is complete in the sense that the
child is DEAD iff no pocket survives.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _d in (os.path.join(ROOT, "attempts", "A189-noroom", "code"),
           os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code"),
           os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"),
           os.path.join(ROOT, "attempts", "A161-chord-lane", "code"),
           os.path.join(ROOT, "attempts", "A213-int-polycore", "code")):
    if os.path.isdir(_d) and _d not in sys.path:
        sys.path.insert(0, _d)

import noroom189 as NR                                             # READ-ONLY (A189)
import multibox as MB                                             # READ-ONLY (A171/A172)

DEFAULTS = dict(NR.DEFAULT_BUDGET)
DEFAULTS.update(
    pk_tsub=8,             # tilt sub-bins of the pocket root
    pk_depth=34,           # halvings of the pocket cover (the pocket is ~1/16 of the container's area)
    pk_max_pieces=200000,   # stack cap (depth-first: this is the frontier, not the whole level)
    pk_max_open=20000,      # undischarged pieces at pk_depth before the pocket is given up
    pk_deadline=5.0,       # per pocket.  MEASURED (results/bench221.md s."the cap"): on 42 pocket covers every DEAD
                           # pocket died in <= 0.1 s and every surviving one burned the whole 45 s cap -- the cover
                           # either collapses at once or not at all, so a 5 s cap is a 50x margin and turns an
                           # UNDECIDED node from ~45 s into ~5 s.
    pk_deadline_inherit=3.0,   # per pocket in the INHERITED pass: it is a cheap filter, and a parent pocket that
                                # survives it is paid for again by the full leaf -- so keep the filter short
    pk_container=True,     # the sound w_min container clip on every piece (A171 container_clip, strict=False)
    grow=0.0,              # extra margin added to an inherited pocket before the cover (0: the cover is exact)
)


def install_kernels():
    """A213's integer K' build + A214's C vertex kernel, exactly as coarse211.install_a213 does (idempotent)."""
    try:
        import mbpatch213 as M213
        return bool(M213.install())
    except Exception:                                              # noqa: BLE001 -- never let the patch stop a node
        return False


def budget_of(b=None):
    d = dict(DEFAULTS)
    d.update(b or {})
    return d


# ------------------------------------------------------------------ LEMMA POCKET-DEAD
def cover_rect(nd, rect, bud, deadline=None):
    """Bisect { (c, th) : c in `rect` } against the node's cores.  -> (open pieces, certificate).

    `rect` is a float 4-tuple (x0, x1, y0, y1); it is intersected with [1/2, s-1/2]^2 (every unit square's centre
    is there) and rationalised OUTWARD, so the cover is of a superset of the pocket."""
    S = nd.s
    half = Fr(1, 2)
    x0 = max(half, Fr(math.floor(rect[0] * 4096 - 1), 4096))
    x1 = min(S - half, Fr(math.ceil(rect[1] * 4096 + 1), 4096))
    y0 = max(half, Fr(math.floor(rect[2] * 4096 - 1), 4096))
    y1 = min(S - half, Fr(math.ceil(rect[3] * 4096 + 1), 4096))
    t0 = time.time()
    if x1 <= x0 or y1 <= y0:
        return [], dict(depth=0, stop="empty", n_open=0, n_dropped=0, seconds=0.0,
                        root=[float(x0), float(x1), float(y0), float(y1)], dropped_container=0)
    obst = [nd.boxes[k].obstacle("poly") for k in nd.names]
    root = [(0, MB.Bin(a, b), (x0, x1, y0, y1)) for (a, b) in MB.sub_bins(Fr(0), Fr(1), bud["pk_tsub"])]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for _d, bn, r in root)
    stats = nd.stats
    # DEPTH-FIRST, unlike A189's level-by-level `bisect_free`: the memory is the stack (depth x 2), not the whole
    # frontier, so a pocket whose residue is thin reaches depth 30+ where a breadth-first pass dies on its piece cap.
    stack = list(reversed(root))
    open_ = []
    depth = 0
    nseen = n_dropped = n_cont = 0
    why = "exhausted"
    while stack:
        d, bn, r = stack.pop()
        nseen += 1
        depth = max(depth, d)
        if (nseen & 255) == 0 and deadline is not None and time.time() > deadline:
            why = "deadline"
            open_.append((bn, r))
            open_.extend([(b2, r2) for _d2, b2, r2 in stack])
            break
        cur = r
        if bud["pk_container"]:
            cur, _sl = MB.container_clip(cur, bn, S, strict=False)
            if cur is None:
                n_cont += 1
                continue
        for ob in obst:
            cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
            if cur is None:
                break
        if cur is None:
            n_dropped += 1
            continue
        if d >= bud["pk_depth"]:
            open_.append((bn, cur))
            if len(open_) > bud["pk_max_open"]:
                why = "open cap"
                open_.extend([(b2, r2) for _d2, b2, r2 in stack])
                break
            continue
        for (b2, r2) in MB.split_piece(bn, cur):
            stack.append((d + 1, b2, r2))
        if len(stack) > bud["pk_max_pieces"]:
            why = "piece cap"
            open_.extend([(b2, r2) for _d2, b2, r2 in stack])
            break
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in open_)
    cert = dict(depth=depth, stop=why, n_open=len(open_), n_dropped=n_dropped, dropped_container=n_cont,
                n_seen=nseen, root=[float(x0), float(x1), float(y0), float(y1)],
                open_volume=float(vol), root_volume=float(vol0),
                dropped_fraction=float(1 - vol / vol0) if vol0 else None,
                seconds=round(time.time() - t0, 1))
    return open_, cert


def pocket_dead(nd, pocket, bud, deadline=None):
    """LEMMA POCKET-DEAD on one pocket -> dict(dead, cert, residue_pockets)."""
    g = bud["grow"]
    rect = (pocket[0] - g, pocket[1] + g, pocket[2] - g, pocket[3] + g)
    dl = time.time() + bud["pk_deadline"]
    if deadline is not None:
        dl = min(dl, deadline)
    pieces, cert = cover_rect(nd, rect, bud, deadline=dl)
    out = dict(pocket=[round(float(v), 6) for v in pocket], dead=not pieces, cert=cert,
               seconds=cert["seconds"], residue=[],
               open_volume=cert.get("open_volume"), root_volume=cert.get("root_volume"),
               dropped_fraction=cert.get("dropped_fraction"))
    if pieces:
        # re-pocket the SURVIVORS with NO extra margin: `pockets_of`'s grid-cell hulls already contain every open
        # piece, so the margin is pure slack -- and re-applying it at every level would GROW the pocket each time.
        rb = dict(bud)
        rb["margin"] = 0.0
        rb["grid"] = min(bud["grid"], 0.015625)
        out["residue"] = [[round(c, 6) for c in p] for p in NR.pockets_of(pieces, float(nd.s), rb)]
    return out


# ------------------------------------------------------------------ the leaf
def _node(roles, s0, bud, name, nd=None):
    if nd is not None:
        return nd, None
    try:
        return NR.build_node(roles, s0, bud, name=name)[0], None
    except MB.EmptyBox as e:
        return None, dict(verdict="DEAD", leaf="EmptyBox (A171 pair leaf)", reason=str(e)[:200])


def pocket_pass(nd, pockets, bud, deadline, m):
    """the cover on a pocket LIST -> (verdict, per-pocket records, surviving pockets)."""
    recs, alive = [], []
    for p in pockets:
        if deadline is not None and time.time() > deadline:
            recs.append(dict(pocket=[round(float(v), 6) for v in p], dead=False, cert=dict(stop="deadline"),
                             seconds=0.0, residue=[[round(float(v), 6) for v in p]]))
            alive.append(list(p))
            continue
        r = pocket_dead(nd, p, bud, deadline=deadline)
        recs.append(r)
        if not r["dead"]:
            alive.extend(r["residue"] or [list(p)])
    return ("DEAD" if not alive else "UNDECIDED"), recs, alive


def noroom_child(roles, parent_pockets, budget=None, s0=None, name="child", n=11, nd=None, deadline=None):
    """LEMMA POCKET-INHERIT + LEMMA POCKET-DEAD: decide the child on its PARENT'S pockets, no global bisection.

    Falls back to the full A221 leaf (`noroom`, which bisects the container) only when an inherited pocket
    survives the cover."""
    t0 = time.time()
    bud = budget_of(budget)
    k = len(roles)
    m = n - k
    dl = (t0 + bud["total_deadline"]) if deadline is None else deadline
    if m <= 0:
        return dict(k=k, m=m, verdict="VACUOUS", step="none", seconds=0.0)
    nd, bad = _node(roles, s0, bud, name, nd=nd)
    if bad is not None:
        return dict(k=k, m=m, step="build", seconds=round(time.time() - t0, 1), **bad)
    t_build = time.time() - t0
    fb = dict(bud)
    fb["pk_deadline"] = min(bud["pk_deadline"], bud["pk_deadline_inherit"])
    # LARGEST pocket first: a DEAD verdict needs every pocket anyway, but an UNDECIDED one is reached soonest by
    # testing the pocket most likely to survive first.
    pks = sorted([list(map(float, q)) for q in (parent_pockets or [])],
                 key=lambda q: -((q[1] - q[0]) * (q[3] - q[2])))
    verdict, recs, alive = pocket_pass(nd, pks, fb, dl, m)
    out = dict(k=k, m=m, verdict=verdict, step="inherited-pockets", n_inherited=len(parent_pockets or []),
               pockets=[r["pocket"] for r in recs], pocket_recs=recs, alive=alive,
               inherit_cap=fb["pk_deadline"],
               t_build=round(t_build, 1), seconds=round(time.time() - t0, 1),
               reason=("every inherited pocket is DEAD (Lemma POCKET-DEAD + Lemma POCKET-INHERIT): the node has no "
                       "free unit square" if verdict == "DEAD" else
                       "%d of %d inherited pocket(s) survive the cover" % (len(alive), len(parent_pockets or []))))
    if verdict == "DEAD" or not pks:
        out["clip"] = "NOROOM-POCKET" if verdict == "DEAD" else None
        return out
    full = noroom(roles, s0=s0, budget=bud, name=name, n=n, nd=nd, deadline=dl)
    full["step"] = "inherited-pockets -> full"
    full["inherited"] = dict(n=len(parent_pockets), alive=alive, seconds=out["seconds"],
                             pocket_recs=recs)
    full["seconds"] = round(time.time() - t0, 1)
    return full


def noroom(roles, s0=None, budget=None, name="node", n=11, nd=None, deadline=None):
    """The A221 no-room leaf: A189's global bisection, then LEMMA POCKET-DEAD on its pockets (instead of A189's
    lane cover of their MEETING windows).  DEAD as soon as every pocket is dead -- for every m >= 1."""
    t0 = time.time()
    bud = budget_of(budget)
    k = len(roles)
    m = n - k
    if m <= 0:
        return dict(k=k, m=m, verdict="VACUOUS", step="none", seconds=0.0)
    dl = (t0 + bud["total_deadline"]) if deadline is None else deadline
    nd, bad = _node(roles, s0, bud, name, nd=nd)
    if bad is not None:
        return dict(k=k, m=m, step="build", seconds=round(time.time() - t0, 1), **bad)
    t_build = round(time.time() - t0, 1)
    t1 = time.time()
    pieces, bcert = NR.bisect_free(nd, bud, deadline=dl)
    t_bis = round(time.time() - t1, 1)
    if not pieces:
        return dict(k=k, m=m, verdict="DEAD", clip="NOROOM", step="bisect", bisect=bcert, pockets=[],
                    t_build=t_build, t_bisect=t_bis, seconds=round(time.time() - t0, 1),
                    reason="bisection alone: every pose of a free unit square meets some core")
    pk = NR.pockets_of(pieces, float(nd.s), bud)
    verdict, recs, alive = pocket_pass(nd, pk, bud, dl, m)
    return dict(k=k, m=m, verdict=verdict, clip=("NOROOM-POCKET" if verdict == "DEAD" else None),
                step="bisect+pockets", bisect=bcert, pockets=[[round(c, 6) for c in p] for p in pk],
                pocket_recs=recs, alive=alive, t_build=t_build, t_bisect=t_bis,
                seconds=round(time.time() - t0, 1),
                reason=("every pocket is DEAD (Lemma POCKET-DEAD): the node has no free unit square"
                        if verdict == "DEAD" else "%d of %d pocket(s) survive the cover" % (len(alive), len(pk))))


if __name__ == "__main__":                                          # tiny self-check on A189's STEP 34 regression
    install_kernels()
    r = noroom(NR.STEP34, name="step34")
    print(json.dumps({kk: vv for kk, vv in r.items() if kk not in ("pocket_recs", "bisect")}, indent=1))
    print("STEP34 regression", "PASS" if r["verdict"] == "DEAD" else "FAIL")
