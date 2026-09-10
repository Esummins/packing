"""A181 -- PARENT-SEEDED top-down re-normalisation of the recorded cascade (the PI's rule, 2026-09-09).

A176's renorm176 intersected a child's inherited roles with the parent's clipped pieces but then
re-merged more than `prop_max` (16) intersected pieces into ONE bounding box per child sub-bin
(`merge_to_subbins`), so the child restarted from (essentially) its weak-clip record and settled at
a LOOSER fixed point than its parent (root/D0/S0 vol1 D 0.1359 -> children B5/B100 vol1 D 0.1592).
Here every inherited role is SEEDED with the parent's fixed-point pieces EXACTLY: child pieces =
recorded child pieces INTERSECTED with the parent's surviving pieces, per role and per tilt sub-bin
(the child's hypothesis is contained in the parent's: sound, never weaker [T]), no re-merge; a role
emptied by the seeding is DEAD by inheritance; then the child's own new role is added and
polyclip175.make_node (= multibox.Node.normalise(nsub=4, refine=2, mode="poly", kmode="pieces",
strict_container=False, corners={every corner role}, c = 1 + w) + roles168's invariant / OVL) runs
to the fixed point.  Side files results/renorm181_<cell>_s<k>of<n>.jsonl, resumable, sharded like
renorm176 (depth-d subtree keys; a node whose parent is held by another shard waits).

A176's S1 records (parent = root, H unclipped at 16 pieces: the cap never bit) are reused only
after `--sample` S1 nodes recomputed by this shard agree with them exactly (vol1 per role).

    python renorm181.py run    --cell l1_104 --shard 0/4 [--depth 2] [--refine 2] [--sample 2]
    python renorm181.py status --cell l1_104
"""
import argparse
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
import renorm175 as RN                                           # noqa: E402  (tree overlay / walls)
import renorm176 as R6                                           # noqa: E402  (todo sharding, A176 side files)
import multibox as MB                                            # noqa: E402
from caselp import Box                                           # noqa: E402

assert "uid" in getattr(MB.Obstacle, "__slots__", ()), "multibox.py predates 13f23204"
TAG = "renorm181"
VERDICT_ALIVE = "ALIVE(geometry; parent-seeded polygon + lonely clip, A181)"


def side_path(cell, k, n):
    return os.path.join(K.RES, "%s_%s_s%dof%d.jsonl" % (TAG, cell, k, n))


def load_side(cell, tag=TAG):
    recs = {}
    import glob
    for fn in sorted(glob.glob(os.path.join(K.RES, "%s_%s_s*of*.jsonl" % (tag, cell)))):
        for ln in open(fn, encoding="utf-8"):
            try:
                d = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            # A183: files are read in NAME order, not time order -- a SKIPPED(cap ...) marker left in
            # another shard file must never override a real record (l1_153 root/D25/S=H: ALIVE at 8/3
            # in s0of1, a stale A181 marker in s0of2)
            q = recs.get(d["node"])
            if q is not None and d["verdict"].startswith("SKIPPED") and not q["verdict"].startswith("SKIPPED"):
                continue
            recs[d["node"]] = d
    return recs


def dedupe(pieces):
    seen, out = set(), []
    for b in pieces:
        k = K.bx(b) if not isinstance(b, (list, tuple)) else tuple(b)
        k = tuple(k)
        if k not in seen:
            seen.add(k)
            out.append(b)
    return out


def seed_roles(roles, par):
    """intersect every inherited role's recorded pieces with the parent's fixed-point pieces (per
    tilt sub-bin, via coex174b.inter); returns (roles, seeded report) or (None, dead reason)."""
    rep = {}
    for r in roles:
        pj = (par.get("roles") or {}).get(r.name)
        if pj is None:
            rep[r.name] = dict(seeded=False, kept=r.kept_frac(), n_pieces=len(r.pieces))
            continue
        kept = [Box(*b) for b in pj["pieces"]]
        v0 = float(sum(R.vol(b) for b in r.pieces))
        new = dedupe(CB.intersect_pieces(r.pieces, kept))
        v1 = float(sum(R.vol(b) for b in new))
        if not new:
            return None, "inheritance: role %s has no pose inside its parent's fixed-point pieces" % r.name
        r.pieces = new
        r.rebuild()
        if r.empty():
            return None, "inheritance: K'(%s) empty on the seeded pieces" % r.name
        rep[r.name] = dict(seeded=True, kept=r.kept_frac(), n_pieces=len(new), vol=v1,
                           frac_of_record=(round(v1 / v0, 6) if v0 > 0 else 0.0))
    return roles, rep


def process(T, path, recs, a, refine=None):
    node = T["nodes"][path]
    rec = dict(node=path, step=node.get("step") or "root", level=node.get("level", 0), parent=node.get("parent"),
               a168_verdict=node["verdict"], a168_kept=node.get("kept"),
               refine=(a.refine if refine is None else refine), lib="post-13f23204", seeding="parent")
    t0 = time.time()
    par = recs.get(node["parent"]) if node.get("parent") else None
    if par is not None and par["verdict"].startswith("SKIPPED"):
        par = None
    if node.get("parent") and par is None:
        pn = T["nodes"].get(node["parent"])
        if pn is not None and pn["verdict"].startswith("DEAD"):
            rec.update(verdict="DEAD(C, ancestor %s (A168 record): %s)" % (node["parent"], pn["verdict"][:70]),
                       leaf="ancestor", wall_s=0.0)
            return rec
        rec.update(verdict="SKIPPED(parent %s not yet re-normalised)" % node["parent"], wall_s=0.0)
        return rec
    if par is not None and par["verdict"].startswith("DEAD"):
        rec.update(verdict="DEAD(C, ancestor %s: %s)" % (node["parent"], par["verdict"][:70]), leaf="ancestor", wall_s=0.0)
        return rec
    roles = CS.roles_of(node)
    rec["vol0"] = R6.vols(roles)
    rec["bbox"] = {r.name: R6.box6(r.bbox()) for r in roles}
    if par is not None:
        roles, srep = seed_roles(roles, par)
        if roles is None:
            rec.update(verdict="DEAD(C, %s)" % srep, leaf="inheritance", wall_s=round(time.time() - t0, 1))
            return rec
        rec["seeded"] = srep
        rec["seeded_kept"] = {k: v["kept"] for k, v in srep.items()}
        rec["seeded_vol"] = R6.vols(roles)
        rec["seeded_n_pieces"] = {k: v["n_pieces"] for k, v in srep.items()}
    rr, rep = PX.make_node(roles, refine=rec["refine"], lonely=bool(a.lonely))
    rec.update(kept=rep.get("kept"), kept_mb=rep.get("kept_mb"), k_area=rep.get("k_area"), k_area_mb=rep.get("k_area_mb"),
               passes=rep.get("passes"), n_pieces=rep.get("n_pieces"),
               lonely=[l for l in rep.get("lonely", []) if l["removed"] > 0 or l["dropped"]],
               corners=rep.get("corners"), stats=rep.get("stats"))
    if rr is None:
        rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), cert=rep.get("cert"),
                   witness=rep.get("witness"), invariant=rep.get("invariant"))
    else:
        rec["roles"] = R.roles_json(rr)
        rec["vol1"] = R6.vols(rr)
        # monotonicity [T]: the fixed point of a seeded role never exceeds the parent's
        if par is not None and par.get("vol1"):
            rec["vol1_le_parent"] = all(rec["vol1"][k] <= par["vol1"][k] * (1 + 1e-9) + 1e-12
                                        for k in rec["vol1"] if k in par["vol1"])
        rec["invariant"] = rep.get("invariant")
        rows = {w: R.best_row(rr, CS.lines_of(w)) for w in RN.walls_of(node)}
        rec["rows"] = rows
        rec["row_kill"] = bool(any(Fr(r["rhs"]) < 0 for r in rows.values()))
        rec["verdict"] = "DEAD(C, chord row A144 LINE-1 on the grown K')" if rec["row_kill"] else VERDICT_ALIVE
        rec["leaf"] = "row" if rec["row_kill"] else None
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def reuse176(p, node, recs, r176, root_ok):
    """an A176 S1 record is the same computation (parent root unclipped, no re-merge): reuse it
    once the shard's recomputed sample agreed; the record is re-labelled and seeded_kept filled."""
    r = r176.get(p)
    if not root_ok or r is None or r["verdict"].startswith("SKIPPED") or node.get("parent") != "root":
        return None
    out = dict(r)
    out.update(reused_from="renorm176", seeding="parent (root H unclipped: identical)", lib="post-13f23204")
    if r.get("roles"):
        out["verdict"] = VERDICT_ALIVE if r["verdict"].startswith("ALIVE") else r["verdict"]
    out["seeded_kept"] = {k: (r.get("a168_kept") or {}).get(k) for k in (r.get("vol0") or {})}
    return out


def same_vol1(r_new, r_old, tol=1e-9):
    if r_new["verdict"].startswith("DEAD") != r_old["verdict"].startswith("DEAD"):
        return False
    a, b = r_new.get("vol1") or {}, r_old.get("vol1") or {}
    return set(a) == set(b) and all(abs(a[k] - b[k]) <= tol * max(1.0, abs(b[k])) for k in a)


def stage_run(a):
    sk, sn = RS.shard_of(a.shard)
    T, n_sh = RN.load_tree_overlay(a.cell, a.overlay)
    recs = load_side(a.cell)
    r176 = R6.load_side(a.cell) if a.reuse176 else {}
    steps = set(a.steps.split(",")) if a.steps else None
    todo = [p for p in R6.todo_nodes(T, sk, sn, steps, a.depth) if p not in recs]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    caps = RS.wallcapped(a.cell)
    out = side_path(a.cell, sk, sn)
    print("%s %s shard %d/%d depth %d: %d nodes to do (%d done, %d shard files, %d A176 records) -> %s" % (
        TAG, a.cell, sk, sn, a.depth, len(todo), len(recs), n_sh, len(r176), out), flush=True)
    t00 = time.time()
    cnt, n_run, n_sample, sample_ok = {}, 0, 0, True
    pending, waited = todo, 0

    def emit(p, rec):
        recs[p] = rec
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        key = rec["verdict"].split("(")[0] + ("/" + str(rec.get("leaf")) if rec.get("leaf") else "")
        cnt[key] = cnt.get(key, 0) + 1
        kp = rec.get("kept") or rec.get("kept_mb") or {}
        print("  %-30s %-5s %-44s seeded %s kept %s %s %.1fs" % (
            p, rec["step"], rec["verdict"][:44], {k: round(v, 3) for k, v in (rec.get("seeded_kept") or {}).items() if v is not None},
            {k: round(v, 3) for k, v in kp.items()}, "REUSED" if rec.get("reused_from") else "", rec["wall_s"]), flush=True)

    while pending:
        nxt, progress = [], False
        for p in pending:
            if K.sentinel():
                print("sentinel; stop", flush=True)
                return 2
            node = T["nodes"][p]
            r_try = None
            if p in caps:
                m = recs.get(p)
                r_prev = m.get("refine") if (m and m["verdict"].startswith("SKIPPED(cap")) else a.refine
                r_try = r_prev - 1
                if r_try < 0:
                    print("  skip %s (wall-capped at every refine level)" % p, flush=True)
                    continue
                marker = dict(node=p, step=node.get("step") or "root", level=node.get("level", 0), parent=node.get("parent"),
                              verdict="SKIPPED(cap attempt refine %d)" % r_try, refine=r_try, wall_s=0.0)
                emit(p, marker)
            # A176 S1 reuse, after this shard's own sample agreed (root must be identical too)
            root_ok = (a.reuse176 and "root" in recs and "root" in r176 and same_vol1(recs["root"], r176["root"])
                       and sample_ok and n_sample >= a.sample)
            ru = reuse176(p, node, recs, r176, root_ok) if node.get("step") == "S1" else None
            if ru is not None:
                emit(p, ru)
                progress = True
                continue
            with RS.NodeWall(a.cell, p):
                rec = process(T, p, recs, a, refine=r_try)
            if rec["verdict"].startswith("SKIPPED"):
                nxt.append(p)
                continue
            if node.get("step") == "S1" and a.reuse176 and p in r176 and n_sample < a.sample:
                n_sample += 1
                ok = same_vol1(rec, r176[p])
                rec["a176_sample_agrees"] = ok
                sample_ok = sample_ok and ok
                print("  A176 sample %d/%d on %s: %s" % (n_sample, a.sample, p, "AGREES" if ok else "DIFFERS -> no reuse"), flush=True)
            emit(p, rec)
            progress = True
            n_run += 1
        if not nxt:
            break
        if not progress:
            waited += 1
            if waited > 720:
                print("  %d nodes still waiting for ancestors; giving up" % len(nxt), flush=True)
                break
            time.sleep(60)
        else:
            waited = 0
        for q, r in load_side(a.cell).items():
            recs.setdefault(q, r)
        print("  retry: %d nodes waiting for ancestors (%d recorded)" % (len(nxt), len(recs)), flush=True)
        pending = nxt
    print("%s shard %d/%d done: %d run, %s, %.0fs" % (TAG, sk, sn, n_run, cnt, time.time() - t00), flush=True)
    return 0


def stage_status(a):
    recs = load_side(a.cell)
    by = {}
    for r in recs.values():
        k = (r["step"], r["verdict"].split("(")[0], r.get("leaf"), "reused" if r.get("reused_from") else "")
        by[k] = by.get(k, 0) + 1
    for k in sorted(by, key=str):
        print("%-6s %-8s %-12s %-6s %d" % (k[0], k[1], k[2], k[3], by[k]))
    print("total", len(recs), "| vol1 > parent:", sum(1 for r in recs.values() if r.get("vol1_le_parent") is False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("run", "status"))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--overlay", type=int, default=1)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--lonely", type=int, default=1)
    ap.add_argument("--steps", default="")
    ap.add_argument("--max_nodes", type=int, default=0)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--reuse176", type=int, default=0)   # A176 records carry the sliver pieces: not reused
    ap.add_argument("--sample", type=int, default=2)
    a = ap.parse_args()
    sys.exit({"run": stage_run, "status": stage_status}[a.stage](a) or 0)


if __name__ == "__main__":
    main()
