"""A174 -- the COEXISTENCE cut at PIECE granularity (the PI's rule, 2026-09-09).

A first meeter's box at a corner is a valid hypothesis only where SOME second meeter of that corner
exists (K0-BLOCKED: two distinct meeters of the widened box); A168 applied that cut to the whole
first-meeter box (S1: D needs an S at TR; S3: B needs a B' at BR).  Here the cut is applied to every
PIECE of the first meeter, BISECTED `--bisect` times (the longer centre side split in half; the tilt
sub-bin kept): a sub-piece with no admissible partner is DROPPED, and the role is replaced by the
union of its surviving (re-normalised) sub-pieces.

Soundness of dropping a sub-piece sp of the first meeter X (roles = the node's other roles):
  * the sub-node {roles, X in sp} is normalised (roles168.make_node: container + mutual clip to a
    fixed point, invariant, OVL) -- a DEAD sub-node means no configuration has X in sp;
  * the partner window (the corner's meeter window) is covered ONCE PER PARENT with the parent's
    roles as obstacles (a complete prefix-code cover, A141's discharges: container / misses-cell
    exact / witness = same square as a role); fewer obstacles => MORE open boxes, so the parent's
    open set is a superset cover of every child's and every sub-piece's partner poses [T];
  * every open box is tested by R3 (lonely => no square of a K0-BLOCKED family, A169 Theorem B),
    by R1 against sp (Lemma A2 cells / Lemma A1 l_inf), then NORMALISED with {roles, X in sp}: an
    empty candidate has no pose interior-disjoint from every role and inside the container;
    a role emptied by the candidate's core means no pose pair exists either;
  * the FIRST survivor is a certificate of coexistence (early exit); none => sp is dropped [T].
  * M(TR) = 1 (the canary): H itself may be the second TR meeter -- the mixed sub-node
    {H restricted to B_meet, X in sp, ...} normalising is a coexistence certificate too.
The cells of the 2x2 grid at c = 1 + w (A169 Lemma A2) of the parent's open boxes are RECORDED
(the PI's reading: at BR the partner of B comes from the (left, floor) cell -- the cells above B and
above-left are H's); the (left, floor) boxes are tried FIRST, so the early exit is cheap when the
reading is right, and nothing is assumed.

Results go to a SIDE FILE (results/piececut_<cell>_<STEP>_s<k>of<n>.jsonl, one line per node,
resumable) -- the main tree is written only by `apply` (coex174b.py), after the step shards merge.

    python coex174.py cut --cell l1_104 --step S1 [--bisect 1] [--shard k/n] [--only path,path]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import cascade168 as CS                                          # noqa: E402
import resume168 as RS                                           # noqa: E402
import polylane as PL                                            # noqa: E402
from caselp import Box                                           # noqa: E402

C_F = RS.C_F


def bisect_rect(b, d):
    """2^d sub-boxes of b (centre rect split along its longer side, tilt range kept)."""
    out = [b]
    for _ in range(d):
        nxt = []
        for q in out:
            if q.x1 - q.x0 >= q.y1 - q.y0:
                m = 0.5 * (q.x0 + q.x1)
                nxt += [Box(q.x0, m, q.y0, q.y1, q.th0, q.th1), Box(m, q.x1, q.y0, q.y1, q.th0, q.th1)]
            else:
                m = 0.5 * (q.y0 + q.y1)
                nxt += [Box(q.x0, q.x1, q.y0, m, q.th0, q.th1), Box(q.x0, q.x1, m, q.y1, q.th0, q.th1)]
        out = nxt
    return out


def cell_of(box, corner):
    """the 2x2 cell at c = 1 + w of a box's centre rect in corner-local coordinates:
    ('lo'|'hi'|'straddle') x 2; 'lo' = within c of the wall."""
    lb = RS.to_local(box, corner)
    eps = 1e-9
    xs = "lo" if lb.x1 < C_F - eps else ("hi" if lb.x0 >= C_F + eps else "straddle")
    ys = "lo" if lb.y1 < C_F - eps else ("hi" if lb.y0 >= C_F + eps else "straddle")
    return xs, ys


def side_path(cell, step, k, n):
    return os.path.join(K.RES, "piececut_%s_%s_s%dof%d.jsonl" % (cell, step, k, n))


def parent_candidates(T, parent_path, corner, a):
    """the partner cover of the corner's meeter window with the PARENT's roles as obstacles,
    R3-filtered, cells recorded, (left, floor) first.  Cached per parent."""
    node = T["nodes"][parent_path]
    roles = CS.roles_of(node)
    cell = K.corner_cell(corner)
    root = Box(*PL.centre_window(cell, K.S0), 0.0, 90.0)
    cov = R.cover(root, cell, roles, depth=a.depth, max_open=a.max_open, lane_pairs=False)
    if not cov["complete"]:
        return None, dict(complete=False, reason=cov["reason"])
    cands, cells, n_lon = [], {}, 0
    for ob in cov["open"]:
        b = Box(*ob["box"])
        if RS.lonely_box(b, corner)[0]:
            n_lon += 1
            continue
        cx = cell_of(b, corner)
        key = "%s/%s" % cx
        cells[key] = cells.get(key, 0) + 1
        cands.append((cx, ob))
    # (left, floor) at BR = far from the right wall (x_loc hi) and near the floor (y_loc lo)
    pref = {("hi", "lo"): 0, ("lo", "hi"): 1, ("hi", "hi"): 2, ("lo", "lo"): 3}
    cands.sort(key=lambda t: pref.get(t[0], 4))
    return [ob for _, ob in cands], dict(complete=True, n_open=len(cov["open"]), n_lonely=n_lon, cells=cells,
                                         n_leaves=len(cov["leaves"]))


def try_partner(rr, cands, second, corner, first_name, a, budget_try):
    """the first candidate that normalises with rr = a certificate; (witness or None, stats)."""
    first = [r for r in rr if r.name == first_name][0]
    st = dict(n_cells=0, n_tested=0, n_dead=0)
    for k, ob in enumerate(cands):
        if budget_try and st["n_tested"] >= budget_try:
            st["undecided"] = True
            return dict(undecided=True), st
        b = Box(*ob["box"])
        if RS.cells_dead(first.pieces, [b], corner)[0]:
            st["n_cells"] += 1
            continue
        new = R.Role.from_box(second, b, nsub=a.nsub, src=ob["box"])
        st["n_tested"] += 1
        if new.empty():
            st["n_dead"] += 1
            continue
        rr2 = [R.Role(r.name, r.pieces, src=r.src) for r in rr] + [new]
        rr2, rep = R.make_node(rr2, nsub=a.nsub)
        if rr2 is None:
            st["n_dead"] += 1
            continue
        return dict(src=ob["box"], cell="%s/%s" % cell_of(b, corner), pieces=[K.bx(p) for p in rr2[-1].pieces],
                    kept=rep["kept"], idx=k), st
    return None, st


def cut_node(T, path, step, cands, a):
    corner, second = CS.SECOND[step]
    first_name = CS.FIRSTN[step]
    node = T["nodes"][path]
    roles = CS.roles_of(node)
    fr = [r for r in roles if r.name == first_name][0]
    others = [r for r in roles if r.name != first_name]
    rec = dict(node=path, step=step, corner=corner, first=first_name, second=second, bisect=a.bisect,
               n_pieces=len(fr.pieces), subs=[], kept_subs=[], n_sub=0, n_dead=0, n_undecided=0)
    t0 = time.time()
    for pi, piece in enumerate(fr.pieces):
        for sp in bisect_rect(piece, a.bisect):
            rec["n_sub"] += 1
            srec = dict(piece=pi, box=K.bx(sp), cell="%s/%s" % cell_of(sp, corner))
            rsub = R.Role(first_name, [sp], src=fr.src)
            rr = [R.Role(o.name, o.pieces, src=o.src) for o in others] + [rsub]
            rr, rep = R.make_node(rr, nsub=a.nsub)
            if rr is None:
                srec.update(dead="sub-node: " + str(rep["dead"])[:100])
                rec["n_dead"] += 1
                rec["subs"].append(srec)
                continue
            if RS.lonely_role(rr[-1], corner)[0]:
                srec.update(dead="R3 lonely sub-piece (Theorem B)")
                rec["n_dead"] += 1
                rec["subs"].append(srec)
                continue
            w, st = try_partner(rr, cands, second, corner, first_name, a, a.max_try)
            srec.update(st)
            if w is None and step == "S1" and T["M"]["TR"]["M"] == 1 and T.get("H_meet_TR", {}).get("box"):
                Hm = R.Role.from_box("H", Box(*T["H_meet_TR"]["box"]), nsub=a.nsub, src=T["H_meet_TR"]["box"])
                rr3 = [Hm] + [R.Role(r.name, r.pieces, src=r.src) for r in rr if r.name != "H"]
                rr3, rep3 = R.make_node(rr3, nsub=a.nsub)
                if rr3 is not None:
                    w = dict(mixed="H itself is the second TR meeter", kept=rep3["kept"])
            if w is None:
                srec.update(dead="no admissible %s partner (%d candidates: %d R1, %d tested, %d dead)" % (
                    second, len(cands), st["n_cells"], st["n_tested"], st["n_dead"]))
                rec["n_dead"] += 1
            else:
                if w.get("undecided"):
                    rec["n_undecided"] += 1
                srec["witness"] = w
                # the surviving sub-piece as re-normalised inside its sub-node
                srec["kept_pieces"] = [K.bx(p) for p in rr[-1].pieces]
                rec["kept_subs"] += srec["kept_pieces"]
            rec["subs"].append(srec)
    rec["wall_s"] = round(time.time() - t0, 1)
    rec["verdict"] = ("DEAD(C, piece coexistence: no sub-piece of %s admits a second %s meeter)" % (first_name, corner)
                      if not rec["kept_subs"] else "ALIVE(piece coexistence: %d/%d sub-pieces kept)" % (
                          rec["n_sub"] - rec["n_dead"], rec["n_sub"]))
    return rec


def stage_cut(a):
    T = CS.load_tree(a.cell)
    step = a.step.upper()
    sk, sn = RS.shard_of(a.shard)
    out = side_path(a.cell, step, sk, sn)
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                    # noqa: BLE001
                pass
    todo = sorted(p for p, n in T["nodes"].items() if n.get("step") == step and n.get("roles")
                  and n["verdict"].startswith("ALIVE"))
    if a.only:
        todo = [p for p in todo if p in a.only.split(",")]
    todo = todo[sk::sn]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    caps = RS.wallcapped(a.cell)
    cache = {}
    t00 = time.time()
    n_run = n_dead = 0
    print("piece cut %s %s shard %d/%d: %d nodes (%d done) -> %s" % (a.cell, step, sk, sn, len(todo), len(done), out), flush=True)
    for p in todo:
        if p in done or p in caps:
            continue
        if K.sentinel():
            print("sentinel; stop", flush=True)
            break
        corner = CS.SECOND[step][0]
        parent = T["nodes"][p]["parent"]
        with RS.NodeWall(a.cell, p):
            if parent not in cache:
                cache[parent] = parent_candidates(T, parent, corner, a)
                print("  parent %s: partner cover %s" % (parent, cache[parent][1]), flush=True)
            cands, crec = cache[parent]
            if cands is None:
                rec = dict(node=p, step=step, verdict="UNDECIDED(partner cover incomplete)", cover=crec)
            else:
                rec = cut_node(T, p, step, cands, a)
                rec["cover"] = crec
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        n_run += 1
        n_dead += int(rec["verdict"].startswith("DEAD"))
        print("  %s: %s  %d sub, %d dead, %d undecided; %.0fs" % (
            p, rec["verdict"][:60], rec.get("n_sub", 0), rec.get("n_dead", 0), rec.get("n_undecided", 0),
            rec.get("wall_s", 0)), flush=True)
    print("piece cut done: %d nodes run, %d DEAD, %.0fs" % (n_run, n_dead, time.time() - t00), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("cut",))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--step", default="S1")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--bisect", type=int, default=1)
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--max_open", type=int, default=6000)
    ap.add_argument("--max_try", type=int, default=0)
    ap.add_argument("--max_nodes", type=int, default=0)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    stage_cut(a)


if __name__ == "__main__":
    main()
