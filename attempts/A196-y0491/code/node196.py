"""A196 step 1 -- BUILD THE NODE of a k5_16 page around the PI's cell TR(0,1).

    pins (A135 exact cores) + H + the two meeters of TR(0,1) as roles, the slot's meeter window in the
    container frame (classes178.meeter_window), H one of them iff A161's exact miss test allows it.

The cases, all sound over-approximations of the page's packings (forced_corners.md Theorem FC, FC-count;
geo178b): two distinct NON-pin squares meet the widened box B+ of TR(0,1); the non-pin squares are H and
the free squares, so either (H-meets) H meets B+ and ONE free square F1 (centre in the window) does, or
(two-free) H misses B+ and TWO free squares F1, F2 do, centres at l-inf distance >= 1/sqrt2 (Lemma A1),
so in distinct cells of side < 1/sqrt2 of the one-free hull.  A case that dies at normalise (EmptyBox) is
DEAD by A171's pair leaf; the page is DEAD iff every case is.

Then UNIT PROPAGATION (A180/A182's Search.propagate, no branching): every other forced cell of the class
with ONE admissible option gets it applied; the propagation stops at the first cell with >= 2 options (the
node then is a superset of every branch, so every leaf verdict on it is sound for the whole subtree).

Then the MEET clip [T]: a role assigned to a cell has interior meeting the open widened box, so a piece all
of whose poses provably miss the box (A161's exact separating-axis test on the piece's outward box) holds
no pose of the role and is dropped; the role's box is replaced by the hull of the survivors and the node
re-normalised, to a fixed point.  Then the sharp fixed point (nsub 8 / refine 3), the invariant, the record.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A180-forced-first-assignment", "code"), os.path.join(ATT, "A178-gallery-geometry", "code"),
           os.path.join(ATT, "A171-multibox-invariant", "code"), os.path.join(ATT, "A161-chord-lane", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prio196                                                   # noqa: E402,F401
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)
import geo178b as GB                                             # noqa: E402  READ-ONLY (A178)
import assign180 as A                                            # noqa: E402  READ-ONLY (A180)
import multibox as MB                                            # noqa: E402  READ-ONLY (A171)
import chordlane as CL                                           # noqa: E402  READ-ONLY (A161)

CELL = "TR(0,1)"


def _hull(nd, k):
    return G.hull_of(nd, k)


def _pieces(nd, k):
    return [[float(v) for v in r] + [MB.deg_of_t(bn.t0), MB.deg_of_t(bn.t1)] for (bn, r) in nd.boxes[k].pieces]


def _kprime(nd, k):
    b = nd.boxes[k]
    return [[float(x), float(y)] for (x, y) in b.pc.verts] if b.pc is not None else None


def snapshot(nd, info, roles):
    return dict(hull={k: _hull(nd, k) for k in nd.boxes}, pieces={k: _pieces(nd, k) for k in nd.boxes},
                kprime={k: _kprime(nd, k) for k in nd.boxes}, kept=info.get("kept"), k_area=info.get("k_area"),
                invariant=info.get("invariant"), failures=info.get("failures"), passes=info.get("passes"),
                n_pieces=info.get("n_pieces"), seconds=info.get("seconds"), roles_in={k: list(v) for k, v in roles.items()})


# ----------------------------------------------------------------------------- the cases at TR(0,1)
def cases_at_cell(rec, cls, item, hull, pinroles, nsub, refine, log):
    """(cases, report): each case = dict(label, roles, assign_members).  Uses geo178b's pair test [S]."""
    r = GB.slot_pair_test(pinroles, ["H"], hull, item, nsub=nsub, refine=refine, log=log, label="root")
    sub = {s["case"]: s for s in r["subcases"]}
    cases = []
    W = item["window"]
    win = (W[0], W[1], W[2], W[3], 0.0, 90.0)
    hm = sub.get("H-meets") or {}
    if hm and not hm.get("dead") and not hm.get("vacuous"):
        roles = dict(pinroles)
        roles["H"] = tuple(A.restrict(hull["H"], W))
        roles["F1"] = win
        cases.append(dict(label="H-meets", roles=roles, members=["H", "F1"], why="H may meet B+ (A161 exact test) and the H-meets node is alive"))
    tf = sub.get("two-free") or {}
    if tf.get("skipped") or tf.get("note"):
        # hull too wide: the pair test could not split; ONE case with two free meeters in the whole window (sound)
        roles = dict(pinroles)
        roles["H"] = tuple(hull["H"])
        roles["F1"], roles["F2"] = win, win
        cases.append(dict(label="two-free(untested)", roles=roles, members=["F1", "F2"], why=tf.get("skipped") or tf.get("note")))
    elif tf.get("n_alive_pairs", 0) > 0:
        hb = tf["hull_B"]
        cells = GB._cells(tuple(hb[:4]))
        # re-run the alive pairs to recover which (geo178b only counts them): every pair is a case
        one = sub["one-free"]
        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                roles = dict(pinroles)
                roles["H"] = tuple(hull["H"])
                ci, cj = cells[i], cells[j]
                roles["F1"] = (ci[0], ci[1], ci[2], ci[3], 0.0, 90.0)
                roles["F2"] = (cj[0], cj[1], cj[2], cj[3], 0.0, 90.0)
                nd2, info2 = G.run_node(roles, nsub=nsub, refine=refine, label="root/two-free:%d+%d" % (i, j))
                if not info2["dead"]:
                    cases.append(dict(label="two-free:%d+%d" % (i, j), roles=roles, members=["F1", "F2"],
                                      why="Lemma A1 cell pair alive at %d/%d" % (nsub, refine)))
        _ = one
    rep = dict(pair_test=r, n_cases=len(cases), cases=[c["label"] for c in cases])
    return cases, rep


# ----------------------------------------------------------------------------- the meet clip
def meet_clip(roles, must_meet, nsub, refine, log, max_rounds=4, label="meet"):
    """[T] a role that meets an open box has no pose in a piece that provably misses it.  Returns (nd, info, rep)."""
    rep = []
    for rnd in range(max_rounds):
        nd, info = G.run_node(roles, nsub=nsub, refine=refine, label="%s#%d" % (label, rnd))
        if info["dead"]:
            rep.append(dict(round=rnd, dead=info["dead"], seconds=info["seconds"]))
            return None, info, rep
        changed, drops = False, {}
        for r, cells in must_meet.items():
            mb = nd.boxes[r]
            keep, n_drop = [], 0
            for (bn, rect) in mb.pieces:
                pb = MB.piece_box(bn, rect)
                if any(CL.box_misses_cell_exact(pb, tuple(c))[0] for c in cells):
                    n_drop += 1
                else:
                    keep.append((bn, rect))
            drops[r] = dict(dropped=n_drop, kept=len(keep))
            if not keep:
                info2 = dict(dead="meet clip: every piece of %s misses its cell" % r, seconds=info["seconds"])
                rep.append(dict(round=rnd, drops=drops, dead=info2["dead"]))
                return None, info2, rep
            if n_drop:
                mb.pieces = keep
                changed = True
        rep.append(dict(round=rnd, drops=drops, seconds=info["seconds"], changed=changed))
        log("    meet clip round %d: %s" % (rnd, {k: v["dropped"] for k, v in drops.items()}))
        if not changed:
            return nd, info, rep
        roles = dict(roles)
        for r in must_meet:
            roles[r] = tuple(_hull(nd, r))
    nd, info = G.run_node(roles, nsub=nsub, refine=refine, label="%s#final" % label)
    return (None if info["dead"] else nd), info, rep


# ----------------------------------------------------------------------------- one case through propagation
def propagate_case(rec, cls, case, nsub, refine, log, max_nodes=120, deadline_s=700.0):
    S = A.Search(rec, cls, nsub=nsub, refine=refine, log=log, max_nodes=max_nodes, deadline=deadline_s, leaf=None)
    items = S.items
    st = dict(roles=dict(case["roles"]), corners={}, assign={c: [] for c in items}, fcells={}, nF=0,
              label="root/" + case["label"], hist=[])
    for m in case["members"]:
        st["assign"][CELL].append(m)
        if m.startswith("F"):
            st["fcells"].setdefault(m, []).append(CELL)
            st["nF"] += 1
    t0 = time.time()
    if not S.normalise(st, "forced"):
        return dict(verdict="DEAD", leaf="case node dead at normalise (A171 pair leaf)", steps=S.steps, seconds=round(time.time() - t0, 1))
    try:
        kind, o = S.propagate(st)
        budget_hit = None
    except A.Budget as e:
        kind, o, budget_hit = "budget", None, str(e)
    out = dict(kind=kind, steps=S.steps, n_nodes=S.n_nodes, seconds=round(time.time() - t0, 1), budget_hit=budget_hit,
               assign=st["assign"], fcells=st["fcells"], nF=st["nF"], label=st["label"], roles=st["roles"], hist=st["hist"])
    if kind == "dead":
        out.update(verdict="DEAD", leaf="no admissible meeter assignment at %s (Theorem ASSIGN)" % o["cell"],
                   detail={k: v for k, v in o.items() if k != "opts"})
    else:
        out["verdict"] = "OPEN"
        if kind == "branch":
            out["branch"] = dict(cell=o["cell"], need=o["need"], cand=o["cand"], n_opts=len(o["opts"]), why=o["why"])
    out["items"] = {c: dict(wbox=it["wbox"], window=it["window"]) for c, it in items.items()}
    return out
