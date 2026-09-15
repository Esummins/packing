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
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pocket221 as PK                                             # noqa: E402  (the cover engine; A171/A189 wrapped)

DEFAULTS = PK.DEFAULTS
budget_of = PK.budget_of
install_kernels = PK.install_kernels
cover_rect = PK.cover_rect
pocket_dead = PK.pocket_dead
pocket_pass = PK.pocket_pass
MB = PK.MB
NR = PK.NR


# ------------------------------------------------------------------ LEMMA CN, on the pockets that SURVIVE
def cn_groups(pockets):
    """A209's Lemma CN, verbatim in logic (`tree209.cn_groups`, which is READ-ONLY here): group the pockets so that
    any two centres in one group are < 1 apart in l-inf, hence a group holds at most ONE centre.  -> (n_groups, ok);
    ok is False when some group has diameter >= 1, and the bound then says nothing.

    A221 applies it to the pockets that SURVIVED the cover, never to the whole list: a pocket certified DEAD by
    LEMMA POCKET-DEAD holds no free centre at all, so dropping it from the cover keeps it a cover -- and a shorter
    list can only give FEWER groups.  So this is A209's bound on a strictly better input."""
    groups = []
    for p in pockets:
        for g in groups:
            if all(max(max(q[1], p[1]) - min(q[0], p[0]), max(q[3], p[3]) - min(q[2], p[2])) < 1 for q in g):
                g.append(p)
                break
        else:
            groups.append([p])
    ok = all(max(max(q[1] for q in g) - min(q[0] for q in g),
                 max(q[3] for q in g) - min(q[2] for q in g)) < 1 for g in groups)
    return len(groups), ok


def cn_upgrade(out, m):
    """UNDECIDED -> DEAD by Lemma CN on `out["alive"]` when the group count is below m.  Mutates and returns `out`."""
    pk = out.get("alive") or []
    if out.get("verdict") != "UNDECIDED" or m is None or m < 2 or not pk:
        return out
    n, ok = cn_groups(pk)
    out["cn_bound"] = n if ok else None
    if ok and n < m:
        out.update(verdict="DEAD", clip="NOROOM-CN",
                   reason=("pocket CN bound %d < %d free squares (Lemma CN on the %d pocket(s) that survive the "
                           "cover; the rest hold no free centre at all)" % (n, m, len(pk))))
    return out


# ------------------------------------------------------------------ the leaf
def _node(roles, s0, bud, name, nd=None):
    if nd is not None:
        return nd, None
    try:
        return NR.build_node(roles, s0, bud, name=name)[0], None
    except MB.EmptyBox as e:
        return None, dict(verdict="DEAD", leaf="EmptyBox (A171 pair leaf)", reason=str(e)[:200])


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
        return cn_upgrade(out, m)
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
    # A228: the same guard the pocket re-pocketing got -- A189's `pockets_of` merge is O(components^3) and is
    # reached AFTER `bisect_free`'s deadline, so a residue spread over many grid components burns unbounded wall
    # (the pass-5 k5_16_interior_Y0402 crash sat here for ~500 s past a 150 s cap).  The fallback rectangle is the
    # centre box [1/2, s - 1/2]^2, which contains the centre of EVERY pose of a unit square in the container, so
    # it is a cover: sound, and it can only make the node UNDECIDED.
    pk, how = PK.repocket(pieces, float(nd.s), bud,
                          [0.5, float(nd.s) - 0.5, 0.5, float(nd.s) - 0.5])
    if m >= 2:
        # Lemma CN is FREE (it reads the rectangles, runs nothing).  A209 applies it to the whole pocket list and it
        # often bites there, so try it BEFORE paying for any cover -- that is A189+A209's own fast path, kept.
        early = cn_upgrade(dict(verdict="UNDECIDED", alive=[list(map(float, q)) for q in pk]), m)
        if early.get("verdict") == "DEAD":
            return dict(k=k, m=m, verdict="DEAD", clip="NOROOM-CN", step="bisect+cn", bisect=bcert,
                        pockets=[[round(c, 6) for c in p] for p in pk], pocket_recs=[], alive=[],
                        cn_bound=early.get("cn_bound"), t_build=t_build, t_bisect=t_bis,
                        seconds=round(time.time() - t0, 1), reason=early.get("reason"))
    verdict, recs, alive = pocket_pass(nd, pk, bud, dl, m)
    return cn_upgrade(dict(k=k, m=m, verdict=verdict, clip=("NOROOM-POCKET" if verdict == "DEAD" else None),
                           step="bisect+pockets", bisect=bcert, repocket=how, pockets=[[round(c, 6) for c in p] for p in pk],
                           pocket_recs=recs, alive=alive, t_build=t_build, t_bisect=t_bis,
                           seconds=round(time.time() - t0, 1),
                           reason=("every pocket is DEAD (Lemma POCKET-DEAD): the node has no free unit square"
                                   if verdict == "DEAD"
                                   else "%d of %d pocket(s) survive the cover" % (len(alive), len(pk)))), m)


if __name__ == "__main__":                                          # tiny self-check on A189's STEP 34 regression
    install_kernels()
    r = noroom(NR.STEP34, name="step34")
    print(json.dumps({kk: vv for kk, vv in r.items() if kk not in ("pocket_recs", "bisect")}, indent=1))
    print("STEP34 regression", "PASS" if r["verdict"] == "DEAD" else "FAIL")
