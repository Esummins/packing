"""A176 -- RE-NORMALISE every recorded ALIVE node of both trees (+ the S3 shard files) on the FIXED
library (multibox.py at/after 13f23204: Obstacle.uid, content-keyed MBox.obstacle, lonely clip) and
re-derive every verdict.  Same top-down discipline as renorm175 (a child's roles are first intersected
with the SAME roles' clipped pieces at its parent [T]; a node under a DEAD parent is DEAD(ancestor);
the rest go through polyclip175.make_node = Node.normalise(nsub=4, refine=2, mode="poly",
kmode="pieces", strict_container=False, corners={every corner role}) driven on the recorded PIECES,
then roles168's invariant (strict=False) and OVL), but with FRESH side files
results/renorm176_<cell>_s<k>of<n>.jsonl -- A175's polyclip175_* files are NOT read (pre-fix, not the
record).  Every record carries the ABSOLUTE pose volume per role before/after (vol0 / vol1) so the
coordinator's clipcheck.jsonl (kept relative to the role's bounding box) can be compared node by node.

    python renorm176.py run    --cell l1_104 --shard 0/2 [--overlay 1] [--refine 2] [--max_nodes N]
    python renorm176.py status --cell l1_104
    python renorm176.py apply  --cell l1_104          (only when nothing else writes the tree)
    python renorm176.py xcheck --cell l1_104          (against <scratchpad>/clipcheck.jsonl)
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
import resume168 as RS                                           # noqa: E402
import coex174b as CB                                            # noqa: E402
import polyclip175 as PX                                         # noqa: E402
import renorm175 as RN                                           # noqa: E402  (tree overlay / todo helpers only)
import multibox as MB                                            # noqa: E402  (already on sys.path via polyclip175)
from caselp import Box                                           # noqa: E402

assert "uid" in getattr(MB.Obstacle, "__slots__", ()), "multibox.py on disk predates the A173 fix (no Obstacle.uid)"
TAG = "renorm176"
CLIPCHECK = os.path.join(os.environ.get("A176_SCRATCH", r"C:\Users\esumm\AppData\Local\Temp\claude"
                         r"\C--Users-esumm-code-packing\8b20e315-017a-445b-9327-302e5359887a\scratchpad"), "clipcheck.jsonl")


def side_path(cell, k, n):
    return os.path.join(K.RES, "%s_%s_s%dof%d.jsonl" % (TAG, cell, k, n))


def load_side(cell):
    recs = {}
    for fn in sorted(glob.glob(os.path.join(K.RES, "%s_%s_s*of*.jsonl" % (TAG, cell)))):
        for ln in open(fn, encoding="utf-8"):
            try:
                d = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            recs[d["node"]] = d
    return recs


def vol_t(b):
    """pose volume of a Box in A171's measure: area x (t_hi(th1) - t_lo(th0)), t = the library's
    tilt parameter (what MBox.kept_fraction weighs sub-bins by)."""
    from caselp import t_lo, t_hi
    x0, x1, y0, y1, th0, th1 = b[:6]
    return float((x1 - x0) * (y1 - y0)) * float(t_hi(th1) - t_lo(th0))


def box6(b):
    return [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]


def merge_to_subbins(new, child, cap):
    """the parent-intersected pieces of a role, if more than `cap`, are replaced per CHILD piece by
    the bounding box of those inside its tilt range (a superset of their union, a subset of the
    child piece: sound both ways [T]); keeps the piece count -- and the per-piece K' cost of every
    later rebuild -- bounded, at the price of the parent's finer partition."""
    if len(new) <= cap:
        return new
    groups = {}
    for q in new:
        host = [k for k, c in enumerate(child) if c.th0 - 1e-12 <= q.th0 and q.th1 <= c.th1 + 1e-12]
        groups.setdefault(host[0] if host else ("solo", id(q)), []).append(q)
    out = []
    for g in groups.values():
        out.append(Box(min(b.x0 for b in g), max(b.x1 for b in g), min(b.y0 for b in g), max(b.y1 for b in g),
                       min(b.th0 for b in g), max(b.th1 for b in g)))
    return out


def vols(roles):
    return {r.name: float(sum(R.vol(b) for b in r.pieces)) for r in roles}


def process(T, path, recs, a, refine=None):
    node = T["nodes"][path]
    rec = dict(node=path, step=node.get("step") or "root", level=node.get("level", 0), parent=node.get("parent"),
               a168_verdict=node["verdict"], a168_kept=node.get("kept"), refine=(a.refine if refine is None else refine), lib="post-13f23204")
    t0 = time.time()
    par = recs.get(node.get("parent")) if node.get("parent") else None
    if par is not None and par["verdict"].startswith("SKIPPED"):
        par = None
    if node.get("parent") and par is None:
        pn = T["nodes"].get(node["parent"])
        if pn is not None and pn["verdict"].startswith("DEAD"):
            # the A168 record itself: a DEAD parent (killed after the child was recorded) kills the child
            rec.update(verdict="DEAD(C, ancestor %s (A168 record): %s)" % (node["parent"], pn["verdict"][:70]),
                       leaf="ancestor", wall_s=round(time.time() - t0, 1))
            return rec
        rec.update(verdict="SKIPPED(parent %s not yet re-normalised)" % node["parent"], wall_s=0.0)
        return rec
    if par is not None and par["verdict"].startswith("DEAD"):
        rec.update(verdict="DEAD(C, ancestor %s: %s)" % (node["parent"], par["verdict"][:70]), leaf="ancestor",
                   wall_s=round(time.time() - t0, 1))
        return rec
    roles = CS.roles_of(node)
    rec["vol0"] = vols(roles)
    rec["bbox"] = {r.name: box6(r.bbox()) for r in roles}
    prop = {}
    if par is not None and par.get("roles"):
        for r in roles:
            if r.name in par["roles"]:
                kept = [Box(*b) for b in par["roles"][r.name]["pieces"]]
                new = CB.intersect_pieces(r.pieces, kept)
                v0 = sum(float(R.vol(b)) for b in r.pieces)
                v1 = sum(float(R.vol(b)) for b in new)
                if v1 < v0 - 1e-15:
                    prop[r.name] = round(v1 / v0, 4) if v0 > 0 else 0.0
                if not new:
                    rec.update(verdict="DEAD(C, propagation: role %s has no pose inside its parent's clipped "
                                       "region -- the child's hypothesis is contained in the parent's)" % r.name,
                               leaf="propagation", propagated=prop, wall_s=round(time.time() - t0, 1))
                    return rec
                r.pieces = merge_to_subbins(new, r.pieces, a.prop_max)
                r.rebuild()
                if r.empty():
                    rec.update(verdict="DEAD(C, propagation: K'(%s) empty on the intersected pieces)" % r.name,
                               leaf="propagation", propagated=prop, wall_s=round(time.time() - t0, 1))
                    return rec
    rec["propagated"] = prop
    rr, rep = PX.make_node(roles, refine=rec["refine"], lonely=bool(a.lonely))
    rec.update(kept=rep.get("kept"), kept_mb=rep.get("kept_mb"), k_area=rep.get("k_area"),
               k_area_mb=rep.get("k_area_mb"), passes=rep.get("passes"), n_pieces=rep.get("n_pieces"),
               lonely=[l for l in rep.get("lonely", []) if l["removed"] > 0 or l["dropped"]],
               corners=rep.get("corners"), stats=rep.get("stats"))
    if rr is None:
        rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), cert=rep.get("cert"),
                   witness=rep.get("witness"), invariant=rep.get("invariant"))
    else:
        rec["roles"] = R.roles_json(rr)
        rec["vol1"] = vols(rr)
        rec["invariant"] = rep.get("invariant")
        rows = {w: R.best_row(rr, CS.lines_of(w)) for w in RN.walls_of(node)}
        rec["rows"] = rows
        rec["row_kill"] = bool(any(Fr(r["rhs"]) < 0 for r in rows.values()))
        rec["verdict"] = ("DEAD(C, chord row A144 LINE-1 on the grown K')" if rec["row_kill"]
                          else "ALIVE(geometry; polygon + lonely clip, fixed library A176)")
        rec["leaf"] = "row" if rec["row_kill"] else None
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def todo_nodes(T, sk, sn, steps, depth):
    """ALIVE nodes with roles, sharded by the subtree key of the first `depth` path parts (nodes
    above that depth by their own key), keys assigned greedily by size to the least-loaded shard
    (deterministic); the retry loop in stage_run waits for ancestors computed by another shard."""
    def key(p):
        parts = p.split("/")
        return "/".join(parts[1:1 + depth]) if len(parts) > 1 else "root"
    cand = []
    for p, n in T["nodes"].items():
        if not n.get("roles") or not n["verdict"].startswith("ALIVE"):
            continue
        if str(n.get("step") or "").endswith("complement"):
            continue
        if steps and (n.get("step") or "root") not in steps:
            continue
        cand.append(p)
    size = {}
    for p in cand:
        size[key(p)] = size.get(key(p), 0) + 1
    load = [0] * sn
    owner = {}
    for k in sorted(size, key=lambda q: (-size[q], q)):
        j = min(range(sn), key=lambda i: (load[i], i))
        owner[k] = j
        load[j] += size[k]
    mine = [p for p in cand if key(p) == "root" or owner[key(p)] == sk]
    mine.sort(key=lambda q: (T["nodes"][q].get("level", 0), q))
    return mine


def stage_run(a):
    sk, sn = RS.shard_of(a.shard)
    T, n_sh = RN.load_tree_overlay(a.cell, a.overlay)
    recs = load_side(a.cell)
    steps = set(a.steps.split(",")) if a.steps else None
    todo = [p for p in todo_nodes(T, sk, sn, steps, a.depth) if p not in recs]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    caps = RS.wallcapped(a.cell)
    out = side_path(a.cell, sk, sn)
    print("%s %s shard %d/%d depth %d: %d nodes to do (%d done, %d shard files overlaid) -> %s" % (
        TAG, a.cell, sk, sn, a.depth, len(todo), len(recs), n_sh, out), flush=True)
    t00 = time.time()
    cnt = {}
    n_run = 0
    pending, waited = todo, 0
    while pending:
        nxt, progress = [], False
        for p in pending:
            if K.sentinel():
                print("sentinel; stop", flush=True)
                return 2
            r_try = None
            if p in caps:
                m = recs.get(p)
                r_prev = m.get("refine") if (m and m["verdict"].startswith("SKIPPED(cap")) else a.refine
                r_try = r_prev - 1
                if r_try < 0:
                    print("  skip %s (wall-capped at every refine level)" % p, flush=True)
                    continue
                marker = dict(node=p, step=T["nodes"][p].get("step") or "root", level=T["nodes"][p].get("level", 0),
                              parent=T["nodes"][p].get("parent"), verdict="SKIPPED(cap attempt refine %d)" % r_try,
                              refine=r_try, wall_s=0.0)
                recs[p] = marker
                with open(out, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(marker) + "\n")
                print("  %s wall-capped: retrying at refine %d" % (p, r_try), flush=True)
            with RS.NodeWall(a.cell, p):
                rec = process(T, p, recs, a, refine=r_try)
            if rec["verdict"].startswith("SKIPPED"):
                nxt.append(p)
                continue
            recs[p] = rec
            progress = True
            with open(out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, default=str) + "\n")
            n_run += 1
            key = rec["verdict"].split("(")[0] + ("/" + str(rec.get("leaf")) if rec.get("leaf") else "")
            cnt[key] = cnt.get(key, 0) + 1
            kp = rec.get("kept") or rec.get("kept_mb") or {}
            print("  %-34s %-9s %-46s kept %s  %.1fs" % (
                p, rec["step"], rec["verdict"][:46], {k: round(v, 3) for k, v in kp.items()}, rec["wall_s"]), flush=True)
        if not nxt:
            break
        if not progress:
            waited += 1
            if waited > 720:
                print("  %d nodes still waiting for ancestors from other shards; giving up" % len(nxt), flush=True)
                break
            time.sleep(60)
        else:
            waited = 0
        for q, r in load_side(a.cell).items():       # ancestors computed by the other shards
            recs.setdefault(q, r)
        print("  retry: %d nodes waiting for ancestors (%d recorded)" % (len(nxt), len(recs)), flush=True)
        pending = nxt
    print("%s shard %d/%d done: %d run, %s, %.0fs" % (TAG, sk, sn, n_run, cnt, time.time() - t00), flush=True)
    return 0


def overlay_side(T, cell):
    """fold the A176 side files into an IN-MEMORY tree (figures while the runs are in flight)."""
    recs = load_side(cell)
    n = 0
    for p, r in recs.items():
        node = T["nodes"].get(p)
        if node is None or r["verdict"].startswith("SKIPPED"):
            continue
        node["verdict"] = r["verdict"]
        node[TAG] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "passes", "n_pieces", "wall_s")}
        if r.get("roles"):
            node["roles"], node["kept"], node["invariant"] = r["roles"], r.get("kept"), r.get("invariant")
            node["clip_passes"], node["rows"], node["row_kill"] = r.get("passes"), r.get("rows"), r.get("row_kill")
        n += 1
    return n


def stage_status(a):
    recs = load_side(a.cell)
    by = {}
    for r in recs.values():
        k = (r["step"], r["verdict"].split("(")[0], r.get("leaf"))
        by[k] = by.get(k, 0) + 1
    for k in sorted(by, key=str):
        print("%-6s %-8s %-12s %d" % (k[0], k[1], k[2], by[k]))
    print("total", len(recs))


def stage_xcheck(a):
    """node-by-node against the coordinator's clipcheck.jsonl (fixed library, NO lonely clip, roles
    re-split from their bounding boxes).  Weaker here = they killed it and we did not, or both alive
    and our absolute pose volume exceeds theirs (kept x vol(bbox)) on some role by > 1e-9."""
    recs = load_side(a.cell)
    cc = {}
    for ln in open(CLIPCHECK, encoding="utf-8"):
        try:
            d = json.loads(ln)
        except Exception:                                        # noqa: BLE001
            continue
        if d["key"].startswith(a.cell + ":"):
            cc[d["key"].split(":", 1)[1]] = d
    n_cmp = n_weak = n_str = 0
    weak = []
    for p, d in cc.items():
        r = recs.get(p)
        if r is None or r["verdict"].startswith("SKIPPED"):
            continue
        n_cmp += 1
        ours_dead = r["verdict"].startswith("DEAD")
        if d["result"] == "DEAD" and not ours_dead:
            n_weak += 1
            weak.append(dict(node=p, why="clipcheck DEAD, ours ALIVE", theirs=d.get("empty"), ours=r["verdict"][:80]))
            continue
        if d["result"] == "DEAD" or ours_dead or not r.get("vol1"):
            n_str += int(ours_dead and d["result"] != "DEAD")
            continue
        for nm, kp in (d.get("kept") or {}).items():
            bb = r["bbox"].get(nm)
            src = (r.get("roles") or {}).get(nm, {}).get("src")
            if bb is None or src is None or nm not in (r.get("kept_mb") or {}):
                continue
            theirs = kp * vol_t(bb)                       # both in A171's t-measure (kept_fraction)
            ours = r["kept_mb"][nm] * vol_t(src)
            if ours > theirs * (1 + a.tol) + 1e-12:
                n_weak += 1
                weak.append(dict(node=p, role=nm, ours=ours, theirs=theirs, ratio=round(ours / theirs, 4) if theirs > 0 else None,
                                 why="role %s t-volume ours %.6g > theirs %.6g" % (nm, ours, theirs)))
                break
    rep = dict(cell=a.cell, compared=n_cmp, weaker=n_weak, dead_here_alive_there=n_str, weak=weak,
               n_clipcheck=len(cc), n_ours=len(recs))
    K.jdump(rep, os.path.join(K.RES, "%s_xcheck_%s.json" % (TAG, a.cell)))
    print(json.dumps({k: v for k, v in rep.items() if k != "weak"}))
    for w in weak[:20]:
        print("  WEAK", w)
    return 0


def stage_apply(a):
    """fold the side files into the tree: verdicts, roles (grown K', new kept), rows; the A168
    record is kept under node['a168']; counts per step before/after; then DEAD(ancestor) closure."""
    T = CS.load_tree(a.cell)
    recs = load_side(a.cell)
    before, after = {}, {}
    n_app = 0
    for p, n in T["nodes"].items():
        st = n.get("step") or "root"
        if str(st).endswith("complement") or not n.get("roles"):
            continue
        before.setdefault(st, [0, 0])
        before[st][0 if n["verdict"].startswith("ALIVE") else 1] += 1
        r = recs.get(p)
        if r is not None and n["verdict"].startswith("ALIVE") and not r["verdict"].startswith("SKIPPED"):
            if "a168" not in n:
                n["a168"] = dict(verdict=n["verdict"], kept=n.get("kept"),
                                 roles={k: dict(pieces=v["pieces"], kept=v.get("kept")) for k, v in n["roles"].items()})
            n["verdict"] = r["verdict"]
            n[TAG] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "k_area_mb", "passes", "n_pieces",
                                             "lonely", "propagated", "wall_s", "refine", "vol0", "vol1", "lib")}
            if r.get("cert"):
                c = dict(r["cert"])
                if c.get("trace"):
                    c["trace"] = c["trace"][-60:]
                n[TAG]["cert"] = c
            if r.get("roles"):
                n["roles"], n["kept"], n["invariant"] = r["roles"], r.get("kept"), r.get("invariant")
                n["clip_passes"], n["rows"], n["row_kill"] = r.get("passes"), r.get("rows"), r.get("row_kill")
            elif r.get("witness"):
                n["witness"] = r["witness"]
            n_app += 1
        after.setdefault(st, [0, 0])
        after[st][0 if n["verdict"].startswith("ALIVE") else 1] += 1
    n_anc = 0
    for q in sorted(T["nodes"], key=len):
        n = T["nodes"][q]
        par = n.get("parent")
        if par and T["nodes"].get(par, {}).get("verdict", "").startswith("DEAD") and n["verdict"].startswith("ALIVE"):
            n["verdict"] = "DEAD(C, ancestor %s: %s)" % (par, T["nodes"][par]["verdict"][:60])
            st = n.get("step") or "root"
            after.setdefault(st, [0, 0])
            after[st][0] -= 1
            after[st][1] += 1
            n_anc += 1
    for spec in CS.STEPS:
        if any(n.get("step") == spec["step"] for n in T["nodes"].values()):
            CS.canary_locate(T, spec)
    T[TAG] = dict(n_applied=n_app, n_dead_by_ancestor=n_anc, before=before, after=after, when=time.strftime("%Y-%m-%d %H:%M"),
                  source="A176 renorm176 (fixed multibox >= 13f23204: polygon obstacles + lonely clip)")
    CS.save_tree(T)
    K.jdump(T[TAG], os.path.join(K.RES, "%s_summary_%s.json" % (TAG, a.cell)))
    print("apply %s: %d nodes; alive/dead before %s after %s (+%d dead by ancestor)" % (a.cell, n_app, before, after, n_anc), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("run", "apply", "status", "xcheck"))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--overlay", type=int, default=1)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--lonely", type=int, default=1)
    ap.add_argument("--steps", default="")
    ap.add_argument("--max_nodes", type=int, default=0)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--prop_max", type=int, default=16)
    ap.add_argument("--tol", type=float, default=0.0)
    a = ap.parse_args()
    rc = {"run": stage_run, "apply": stage_apply, "status": stage_status, "xcheck": stage_xcheck}[a.stage](a)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
