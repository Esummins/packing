"""A174 -- APPLY the piece-level coexistence cuts (coex174 side files) to a cascade tree.

For every recorded node: DEAD verdicts are written through; an ALIVE node has its first-meeter role
replaced by the union of the surviving sub-pieces (each re-normalised inside its own sub-node, so a
subset of the sub-piece; the union covers every pose not proved impossible [T]) and is
RE-NORMALISED (roles168.make_node: container + mutual clip to a fixed point, invariant, OVL) --
a node that dies there is DEAD by the clip / PAIR / OVL leaf.  Chord rows are recomputed.

PROPAGATION to descendants (S1 -> S2 -> S3): a descendant's hypothesis is contained in its
ancestor's, so the ancestor's argument ("no configuration has D in a dropped sub-piece") holds for
it too: every piece of the descendant's first-meeter role is intersected with the union of the
ancestor's surviving sub-pieces (rect x tilt intersection); an emptied role is a DEAD node; a
changed role is rebuilt (K' from the new pieces, invariant re-asserted, OVL) and, for nodes at
level <= --full_level, fully re-normalised; deeper nodes are flagged `renorm_pending` (their
pieces are sound supersets either way; the full fixed point is re-run before any LP by lp stage).

Run only when no other process writes the tree (after the step shards are merged).

    python coex174b.py apply --cell l1_153 --step S1 [--full_level 2]
"""
import argparse
import glob
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import cascade168 as CS                                          # noqa: E402
from caselp import Box                                           # noqa: E402


def load_cuts(cell, step):
    recs = {}
    for fn in sorted(glob.glob(os.path.join(K.RES, "piececut_%s_%s_s*of*.jsonl" % (cell, step)))):
        for ln in open(fn, encoding="utf-8"):
            try:
                d = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            recs[d["node"]] = d
    return recs


def inter(q, k):
    x0, x1 = max(q.x0, k.x0), min(q.x1, k.x1)
    y0, y1 = max(q.y0, k.y0), min(q.y1, k.y1)
    t0, t1 = max(q.th0, k.th0), min(q.th1, k.th1)
    if x1 <= x0 or y1 <= y0 or t1 < t0 or (t1 == t0 and q.th1 > q.th0):
        return None
    return Box(x0, x1, y0, y1, t0, t1)


def intersect_pieces(pieces, kept):
    out = []
    for q in pieces:
        for k in kept:
            r = inter(q, k)
            if r is not None:
                out.append(r)
    return out


def set_roles(node, roles, rep, walls, why):
    node["roles"] = R.roles_json(roles)
    node["kept"] = rep.get("kept")
    node["invariant"] = rep.get("invariant")
    node["clip_passes"] = rep.get("passes")
    node["rows"] = {w: R.best_row(roles, CS.lines_of(w)) for w in walls}
    node["row_kill"] = bool(any(Fr(r["rhs"]) < 0 for r in node["rows"].values()))
    if node["row_kill"]:
        node["verdict"] = "DEAD(C, chord row A144 LINE-1, after %s)" % why
    else:
        node["verdict"] = "ALIVE(geometry; %s)" % why


def renorm(T, path, first, new_pieces, why, full, a):
    """replace role `first`'s pieces and rebuild / re-normalise; returns the verdict."""
    node = T["nodes"][path]
    walls = CS.STEP_BY[node["step"]]["walls"] if node.get("step") in CS.STEP_BY else ("top", "right")
    roles = CS.roles_of(node)
    rr = []
    for r in roles:
        if r.name == first:
            rr.append(R.Role(first, new_pieces, src=r.src))
        else:
            rr.append(R.Role(r.name, r.pieces, src=r.src))
    fr = [r for r in rr if r.name == first][0]
    if fr.empty():
        node["verdict"] = "DEAD(C, %s: role %s has no piece left)" % (why, first)
        return node["verdict"]
    if full:
        rr2, rep = R.make_node(rr, nsub=a.nsub)
        if rr2 is None:
            node["verdict"] = "DEAD(C, %s -> %s)" % (why, rep["dead"])
            node["witness"] = rep.get("witness")
            return node["verdict"]
        set_roles(node, rr2, rep, walls, why)
        node["renorm_pending"] = False
    else:
        inv = R.invariant(rr)
        if not inv["ok"]:
            node["verdict"] = "DEAD(C, %s -> %s)" % (why, inv["dead"])
            node["witness"] = inv.get("witness")
            return node["verdict"]
        d = R.pair_leaves(rr)
        if d is not None:
            node["verdict"] = "DEAD(C, %s -> %s)" % (why, d)
            return node["verdict"]
        set_roles(node, rr, dict(kept={r.name: r.kept_frac() for r in rr}, invariant=inv,
                                 passes=node.get("clip_passes")), walls, why + " (pieces intersected, fixed point pending)")
        node["renorm_pending"] = True
    return node["verdict"]


def descendants(T, path):
    out = []
    stack = list(T["nodes"][path].get("children", []))
    while stack:
        q = stack.pop()
        out.append(q)
        stack += T["nodes"][q].get("children", [])
    return out


def stage_apply(a):
    T = CS.load_tree(a.cell)
    step = a.step.upper()
    recs = load_cuts(a.cell, step)
    first = CS.FIRSTN[step]
    t00 = time.time()
    n_dead = n_shrunk = n_desc_dead = n_desc_changed = n_desc_seen = 0
    for path, rec in sorted(recs.items()):
        node = T["nodes"].get(path)
        if node is None or not node["verdict"].startswith("ALIVE"):
            continue
        summ = {k: rec.get(k) for k in ("n_pieces", "n_sub", "n_dead", "n_undecided", "bisect", "cover", "wall_s")}
        summ["subs"] = [dict(box=s["box"], cell=s["cell"], dead=s.get("dead"),
                             witness=(s.get("witness") or {}).get("src"),
                             witness_cell=(s.get("witness") or {}).get("cell")) for s in rec.get("subs", [])]
        node["piececut"] = summ
        if rec["verdict"].startswith("DEAD"):
            node["verdict"] = rec["verdict"]
            n_dead += 1
            for q in descendants(T, path):
                if T["nodes"][q]["verdict"].startswith("ALIVE"):
                    T["nodes"][q]["verdict"] = "DEAD(C, ancestor %s: piece coexistence)" % path
                    n_desc_dead += 1
            print("  %s DEAD (%d descendants dead)" % (path, len(descendants(T, path))), flush=True)
            continue
        if rec["verdict"].startswith("UNDECIDED"):
            continue
        kept = [Box(*b) for b in rec["kept_subs"]]
        old = [Box(*b) for b in node["roles"][first]["pieces"]]
        vol_old = sum(float(R.vol(b)) for b in old)
        vol_new = sum(float(R.vol(b)) for b in kept)
        v = renorm(T, path, first, kept, "piece coexistence %d/%d sub-pieces" % (rec["n_sub"] - rec["n_dead"], rec["n_sub"]),
                   True, a)
        n_shrunk += int(vol_new < vol_old - 1e-12)
        node["piececut"]["vol_frac"] = (vol_new / vol_old) if vol_old > 0 else None
        print("  %s: %s  vol %.3f -> %.3f" % (path, v[:70], vol_old, vol_new), flush=True)
        if v.startswith("DEAD"):
            for q in descendants(T, path):
                if T["nodes"][q]["verdict"].startswith("ALIVE"):
                    T["nodes"][q]["verdict"] = "DEAD(C, ancestor %s: %s)" % (path, v[:60])
                    n_desc_dead += 1
            continue
        # propagate the surviving sub-pieces to the descendants' copy of the role
        for q in descendants(T, path):
            d = T["nodes"][q]
            if not d.get("roles") or not d["verdict"].startswith("ALIVE") or first not in d["roles"]:
                continue
            n_desc_seen += 1
            pcs = [Box(*b) for b in d["roles"][first]["pieces"]]
            new = intersect_pieces(pcs, kept)
            if sum(float(R.vol(b)) for b in new) >= sum(float(R.vol(b)) for b in pcs) - 1e-12:
                continue
            n_desc_changed += 1
            vq = renorm(T, q, first, new, "ancestor %s piece coexistence" % path, d.get("level", 9) <= a.full_level, a)
            if vq.startswith("DEAD"):
                n_desc_dead += 1
                for q2 in descendants(T, q):
                    if T["nodes"][q2]["verdict"].startswith("ALIVE"):
                        T["nodes"][q2]["verdict"] = "DEAD(C, ancestor %s: %s)" % (q, vq[:60])
                        n_desc_dead += 1
    T.setdefault("piececut", {})[step] = dict(n_recorded=len(recs), n_dead=n_dead, n_shrunk=n_shrunk,
                                              n_desc_seen=n_desc_seen, n_desc_changed=n_desc_changed,
                                              n_desc_dead=n_desc_dead, when=time.strftime("%Y-%m-%d %H:%M"),
                                              wall_s=round(time.time() - t00, 1))
    CS.save_tree(T)
    print("apply %s %s: %s" % (a.cell, step, T["piececut"][step]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("apply",))
    ap.add_argument("--cell", default="l1_153")
    ap.add_argument("--step", default="S1")
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--full_level", type=int, default=2)
    a = ap.parse_args()
    stage_apply(a)


if __name__ == "__main__":
    main()
