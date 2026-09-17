"""A242 -- the cell leaves.  L1 NO-ROOM(m = 3) over the eight meeters' CORES, and the L2 gate.

A171 / A172 (multibox, K'), A189 (noroom189), A209 (Lemma CN), A213 / A214 (kernels), A221
(pocket221 / noroom221) are READ-ONLY libraries; this module WRAPS them and edits nothing.

L1 -- NO-ROOM(m = 3) OVER THE CELL  [T]
---------------------------------------
Hypothesis of the cell: eight distinct squares of F, one per role, with poses in the role boxes,
and m = 11 - 8 = 3 further squares of F, anonymous, inside [0, S]^2, all interiors pairwise
disjoint.  A172's K'(role) is the intersection of the posed squares over ALL poses in the role's
box, so K'(role) is contained in EVERY pose of that role: the three free squares have interiors
disjoint from every K'(role).  That is the ONLY use made of the meeters -- the over-approximation
of the free region is the container MINUS THE CORES, never minus the roles' reach sets (A171's
direction: a core is a subset of every pose, a reach set is a superset of one; subtracting cores
LOSES exclusions, which is the safe side).  Then:
  * A189 Lemma 1 (pocket counting): bisect the free square's (centre, tilt) space against the cores
    with multibox's exact dead test; every DROPPED piece is certified "every pose in it meets some
    core"; the surviving pieces' centres are covered by rectangles P_1..P_r, and
    m <= sum_j LANE(P_j).
  * A221 Lemma POCKET-DEAD: a pocket all of whose poses meet a core holds no free centre; if every
    pocket is dead the cell has NO free square at all -- DEAD for every m >= 1.
  * A209 Lemma CN (applied by `noroom221.cn_upgrade` to the pockets that SURVIVE): pockets whose
    pairwise l-inf diameter is < 1 hold at most one centre between them, so the group count is an
    upper bound on the number of free squares; group count < 3 is DEAD.
  * A221 Lemma POCKET-INHERIT: a child's roles have boxes inside its parent's, so its cores are
    LARGER and its free poses fewer -- the parent's pockets cover the child's free centres, and the
    child may run the cover on them without a fresh global bisection.
Every verdict is one-sided: DEAD is a certificate, UNDECIDED says nothing.

L2 -- THE GATE  (`notes/crowd242.md` s.3; Lemma BOX-GORDAN)
-----------------------------------------------------------
A box-valid Gordan certificate for "the meeter is not LOCKED" may only be attempted when the cell's
own geometry already forbids an ANONYMOUS free square from touching the meeter: a free square of
unknown tilt contributes a contact normal of unknown direction, and the cone of possibly-active
contact forces is then all of R^2 and no separating h exists.  `l2_gate` decides exactly that from
L1's surviving pockets.  If two unit squares touch they share a point p, and a unit square's body
lies within l-inf distance w(theta)/2 <= sqrt(2)/2 of its centre, so their CENTRES are within
sqrt 2 in l-inf.  Hence a free square whose centre lies in pocket P cannot touch the meeter of role
r whenever  dist_inf(P, B_r) > sqrt 2,  B_r the role's CENTRE box.  The gate passes iff that holds
for every role and every pocket that survived the cover.  Direction: the pockets are a SUPERSET of
the free centres (A189 Lemma 1) and B_r a SUPERSET of the meeter's centres, which is the correct
side for a "cannot touch" conclusion -- the opposite of L1's cores.
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _d in (os.path.join(ROOT, "attempts", "A221-lane-cover", "code"),
           os.path.join(ROOT, "attempts", "A189-noroom", "code"),
           os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import multibox as MB                                              # noqa: E402  READ-ONLY (A171/A172)
import noroom221 as N221                                           # noqa: E402  READ-ONLY (A221)

SQ2 = math.sqrt(2.0)
L1_BUDGET = dict(total_deadline=600.0, pk_deadline=5.0, pk_deadline_inherit=3.0,
                 tsub=8, depth=13, max_pieces=120000)


def install():
    return N221.install_kernels()


def build_node(cell, budget, name="cell"):
    """The cell's eight roles at the multibox fixed point, at the BAND's reference side S.

    A189's `build_node` drops its `s0` argument (it always builds at the default s0), so the Node is
    built HERE with the band's S and normalised with A189's own parameters -- a wrap, not an edit."""
    nd = MB.Node({k: tuple(v) for k, v in cell["roles"].items()}, s=cell["S"], name=name)
    nd.normalise(nsub=budget["nsub"], refine=budget["refine"], mode="poly", kmode="pieces",
                 strict_container=False, verbose=False)
    return nd


def l1(cell, parent_pockets=None, budget=None, name="cell"):
    """L1 on the cell.  Returns the A221 record (verdict DEAD / UNDECIDED / VACUOUS / ERROR)."""
    bud = N221.budget_of({**L1_BUDGET, **(budget or {})})
    t0 = time.time()
    try:
        nd = build_node(cell, bud, name=name)
    except MB.EmptyBox as e:
        return dict(verdict="DEAD", clip="EMPTYBOX", leaf="L0", k=8, m=cell["m"],
                    seconds=round(time.time() - t0, 2),
                    reason="A171 pair leaf: %s -- some role loses every pose, so the cell's "
                           "hypothesis is unsatisfiable" % str(e)[:160])
    except Exception as e:                                          # noqa: BLE001
        return dict(verdict="ERROR", leaf="L1", seconds=round(time.time() - t0, 2),
                    reason=repr(e)[:240])
    try:
        if parent_pockets:
            r = N221.noroom_child(cell["roles"], parent_pockets, budget=bud, name=name,
                                  n=cell["n"], nd=nd)
        else:
            r = N221.noroom(cell["roles"], budget=bud, name=name, n=cell["n"], nd=nd)
    except Exception as e:                                          # noqa: BLE001
        return dict(verdict="ERROR", leaf="L1", seconds=round(time.time() - t0, 2),
                    reason=repr(e)[:240])
    r["leaf"] = "L1"
    r["seconds"] = round(time.time() - t0, 2)
    r.pop("bisect", None)
    r.pop("pocket_recs", None)
    return r


def _grow(box, g):
    return [box[0] - g, box[1] + g, box[2] - g, box[3] + g]


def _linf_gap(a, b):
    """l-inf distance between two axis-aligned rectangles [x0,x1,y0,y1] (0 if they overlap)."""
    dx = max(0.0, max(a[0] - b[1], b[0] - a[1]))
    dy = max(0.0, max(a[2] - b[3], b[2] - a[3]))
    return max(dx, dy)


def l2_gate(cell, alive_pockets):
    """Is a box-valid Gordan test admissible on this cell?  (see the module docstring / Lemma
    BOX-GORDAN in `notes/crowd242.md` s.3).  Returns (ok, worst_gap, per-role gaps)."""
    gaps = {}
    for r, b in cell["roles"].items():
        cbox = [b[0], b[1], b[2], b[3]]
        g = min([_linf_gap(cbox, [p[0], p[1], p[2], p[3]]) for p in alive_pockets] or [float("inf")])
        gaps[r] = g
    worst = min(gaps.values()) if gaps else float("inf")
    return (worst > SQ2), worst, gaps


def leaf_of(cell, parent_pockets=None, budget=None, name="cell"):
    """The cell's verdict: L1 first (the only kill that runs in the cascade), then the L2 gate is
    RECORDED on the survivors so that the alive frontier says where an FJ leaf could ever act."""
    r = l1(cell, parent_pockets=parent_pockets, budget=budget, name=name)
    if r.get("verdict") == "UNDECIDED":
        ok, worst, gaps = l2_gate(cell, r.get("alive") or [])
        r["l2_gate"] = dict(ok=bool(ok), worst_gap=round(worst, 4) if worst != float("inf") else None,
                            per_role={k: (round(v, 4) if v != float("inf") else None)
                                      for k, v in gaps.items()})
    return r
