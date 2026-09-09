"""A175 -- RE-NORMALISE every recorded node of a cascade tree with the POLYGON clip (polyclip175)
and re-derive every verdict.  Top-down: a node's roles are first intersected with the SAME roles'
clipped pieces at its parent (the child's hypothesis is contained in the parent's, so a pose the
parent's clip removed is impossible for the child too [T]); a node under a DEAD parent is DEAD
(C, ancestor) without computation; the rest go through polyclip175.make_node under the 1,500 s
wall.  Results go to SIDE FILES (results/polyclip175_<cell>_s<k>of<n>.jsonl, one line per node,
resumable; a restarted shard reloads every side file of the cell, so ancestors are always known);
`apply` folds them into the tree (run only when nothing else writes the tree).

Shards are by S1 SUBTREE (root/Dk), so each shard sees its own ancestors; `--overlay 1` folds the
step shard files (results/shards/*) into the in-memory tree, so nodes still being produced by the
detached S3 shards are re-normalised before the merge (a record is keyed by path; nothing is
written under results/shards).

    python renorm175.py run   --cell l1_104 --shard 0/4 [--overlay 1] [--refine 2] [--max_nodes N]
    python renorm175.py apply --cell l1_104
    python renorm175.py status --cell l1_104
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
from caselp import Box                                           # noqa: E402


def side_path(cell, k, n):
    return os.path.join(K.RES, "polyclip175_%s_s%dof%d.jsonl" % (cell, k, n))


def load_side(cell):
    recs = {}
    for fn in sorted(glob.glob(os.path.join(K.RES, "polyclip175_%s_s*of*.jsonl" % cell))):
        for ln in open(fn, encoding="utf-8"):
            try:
                d = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            recs[d["node"]] = d
    return recs


def load_tree_overlay(cell, overlay):
    T = CS.load_tree(cell)
    n_sh = 0
    if overlay:
        d = os.path.join(K.RES, "shards")
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not fn.startswith("tree_%s__" % cell):
                continue
            try:
                S = K.jload(os.path.join(d, fn))
            except (json.JSONDecodeError, OSError):
                continue
            for p, node in S["nodes"].items():
                if p not in T["nodes"]:
                    T["nodes"][p] = node
            n_sh += 1
    return T, n_sh


def subtree_key(path):
    parts = path.split("/")
    return parts[1] if len(parts) > 1 else "root"


def todo_nodes(T, sk, sn, steps=None):
    keys = sorted({subtree_key(p) for p in T["nodes"] if p != "root"})
    mine = set(keys[sk::sn]) | {"root"}
    out = []
    for p, n in T["nodes"].items():
        if not n.get("roles") or not n["verdict"].startswith("ALIVE"):
            continue
        if str(n.get("step") or "").endswith("complement"):
            continue
        if steps and (n.get("step") or "root") not in steps:
            continue
        if subtree_key(p) not in mine:
            continue
        out.append(p)
    out.sort(key=lambda q: (T["nodes"][q].get("level", 0), q))
    return out


def walls_of(node):
    st = node.get("step")
    return CS.STEP_BY[st]["walls"] if st in CS.STEP_BY else ()


def process(T, path, recs, a):
    node = T["nodes"][path]
    rec = dict(node=path, step=node.get("step") or "root", level=node.get("level", 0), parent=node.get("parent"),
               a168_verdict=node["verdict"], a168_kept=node.get("kept"), refine=a.refine)
    t0 = time.time()
    par = recs.get(node.get("parent")) if node.get("parent") else None
    if node.get("parent") and par is None:
        rec.update(verdict="SKIPPED(parent %s not yet re-normalised)" % node["parent"], wall_s=0.0)
        return rec
    if par is not None and par["verdict"].startswith("DEAD"):
        rec.update(verdict="DEAD(C, ancestor %s: %s)" % (node["parent"], par["verdict"][:70]), leaf="ancestor",
                   wall_s=round(time.time() - t0, 1))
        return rec
    roles = CS.roles_of(node)
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
                r.pieces = new
                r.rebuild()
                if r.empty():
                    rec.update(verdict="DEAD(C, propagation: K'(%s) empty on the intersected pieces)" % r.name,
                               leaf="propagation", propagated=prop, wall_s=round(time.time() - t0, 1))
                    return rec
    rec["propagated"] = prop
    rr, rep = PX.make_node(roles, refine=a.refine, lonely=bool(a.lonely))
    rec.update(kept=rep.get("kept"), kept_mb=rep.get("kept_mb"), k_area=rep.get("k_area"),
               k_area_mb=rep.get("k_area_mb"), passes=rep.get("passes"), n_pieces=rep.get("n_pieces"),
               lonely=[l for l in rep.get("lonely", []) if l["removed"] > 0 or l["dropped"]],
               corners=rep.get("corners"), stats=rep.get("stats"))
    if rr is None:
        rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), cert=rep.get("cert"),
                   witness=rep.get("witness"), invariant=rep.get("invariant"))
    else:
        rec["roles"] = R.roles_json(rr)
        rec["invariant"] = rep.get("invariant")
        rows = {w: R.best_row(rr, CS.lines_of(w)) for w in walls_of(node)}
        rec["rows"] = rows
        rec["row_kill"] = bool(any(Fr(r["rhs"]) < 0 for r in rows.values()))
        rec["verdict"] = ("DEAD(C, chord row A144 LINE-1 on the grown K')" if rec["row_kill"]
                          else "ALIVE(geometry; polygon clip A175)")
        rec["leaf"] = "row" if rec["row_kill"] else None
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def stage_run(a):
    sk, sn = RS.shard_of(a.shard)
    T, n_sh = load_tree_overlay(a.cell, a.overlay)
    recs = load_side(a.cell)
    steps = set(a.steps.split(",")) if a.steps else None
    todo = [p for p in todo_nodes(T, sk, sn, steps) if p not in recs]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    caps = RS.wallcapped(a.cell)
    out = side_path(a.cell, sk, sn)
    print("renorm175 %s shard %d/%d: %d nodes to do (%d done, %d shard files overlaid) -> %s" % (
        a.cell, sk, sn, len(todo), len(recs), n_sh, out), flush=True)
    t00 = time.time()
    cnt = {}
    n_run = 0
    for p in todo:
        if K.sentinel():
            print("sentinel; stop", flush=True)
            return 2
        if p in caps:
            print("  skip %s (wall-capped)" % p, flush=True)
            continue
        with RS.NodeWall(a.cell, p):
            rec = process(T, p, recs, a)
        if rec["verdict"].startswith("SKIPPED"):
            print("  %s: %s" % (p, rec["verdict"]), flush=True)
            continue
        recs[p] = rec
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        n_run += 1
        key = rec["verdict"].split("(")[0] + ("/" + str(rec.get("leaf")) if rec.get("leaf") else "")
        cnt[key] = cnt.get(key, 0) + 1
        kp = rec.get("kept") or rec.get("kept_mb") or {}
        print("  %-34s %-9s %-46s kept %s  %.1fs" % (
            p, rec["step"], rec["verdict"][:46], {k: round(v, 3) for k, v in kp.items()}, rec["wall_s"]), flush=True)
    print("renorm175 shard %d/%d done: %d run, %s, %.0fs" % (sk, sn, n_run, cnt, time.time() - t00), flush=True)
    return 0


def overlay_side(T, cell):
    """fold the side files into an IN-MEMORY tree (figures while the runs are in flight): verdicts,
    roles (grown K', new kept), rows.  Nothing is written.  Returns the number of nodes overlaid."""
    recs = load_side(cell)
    n = 0
    for p, r in recs.items():
        node = T["nodes"].get(p)
        if node is None or r["verdict"].startswith("SKIPPED"):
            continue
        node["verdict"] = r["verdict"]
        node["polyclip175"] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "passes", "n_pieces", "wall_s")}
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


def stage_apply(a):
    """fold the side files into the tree: verdicts, roles (grown K', new kept), rows; the A168
    record is kept under node['a168']; counts per step before/after."""
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
                n["a168"] = dict(verdict=n["verdict"], kept=n.get("kept"), roles={k: dict(pieces=v["pieces"], kept=v.get("kept"))
                                                                            for k, v in n["roles"].items()})
            n["verdict"] = r["verdict"]
            n["polyclip175"] = {k: r.get(k) for k in ("leaf", "kept", "kept_mb", "k_area", "k_area_mb", "passes",
                                                       "n_pieces", "lonely", "propagated", "wall_s", "refine")}
            if r.get("cert"):
                c = dict(r["cert"])
                if c.get("trace"):
                    c["trace"] = c["trace"][-60:]
                n["polyclip175"]["cert"] = c
            if r.get("roles"):
                n["roles"] = r["roles"]
                n["kept"] = r.get("kept")
                n["invariant"] = r.get("invariant")
                n["clip_passes"] = r.get("passes")
                n["rows"] = r.get("rows")
                n["row_kill"] = r.get("row_kill")
            elif r.get("witness"):
                n["witness"] = r["witness"]
            n_app += 1
        after.setdefault(st, [0, 0])
        after[st][0 if n["verdict"].startswith("ALIVE") else 1] += 1
    for spec in CS.STEPS:
        if any(n.get("step") == spec["step"] for n in T["nodes"].values()):
            CS.canary_locate(T, spec)
    T["polyclip175"] = dict(n_applied=n_app, before=before, after=after, when=time.strftime("%Y-%m-%d %H:%M"),
                            source="A175 polyclip175 (A171 polygon obstacles + A173 lonely clip)")
    CS.save_tree(T)
    K.jdump(T["polyclip175"], os.path.join(K.RES, "polyclip175_summary_%s.json" % a.cell))
    print("apply %s: %d nodes; alive/dead before %s after %s" % (a.cell, n_app, before, after), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("run", "apply", "status"))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--overlay", type=int, default=1)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--lonely", type=int, default=1)
    ap.add_argument("--steps", default="")
    ap.add_argument("--max_nodes", type=int, default=0)
    a = ap.parse_args()
    rc = {"run": stage_run, "apply": stage_apply, "status": stage_status}[a.stage](a)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
