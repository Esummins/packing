"""A183 -- RESUME of A181's parent-seeded top-down re-normalisation after the 15:46 crash, with the
coordinator's refinement lever: every node that SURVIVES the nsub 4 / refine 2 pass is re-clipped
at nsub 8 / refine 3, SEEDED FROM ITS OWN 4/2 FIXED POINT (each piece's tilt sub-bin is bisected
once more -- nsub 8 relative to the record's 4 -- then three levels of tautologous bisection and
the polygon + lonely clip to the fixed point: a subset of the 4/2 fixed point, hence sound [T]).
Children are seeded from the parent's FINAL (8/3) pieces.  Measured by the coordinator on
l1_104 root/D0/S1/B5: 4/2 keeps H 0.745, 8/3 keeps 0.639 at 3.6x the time, 16/3 no better.

Records go to A181's side files (results/renorm181_<cell>_s<k>of<n>.jsonl, last record per node
wins) with `setting` = "nsub 8 / refine 3 (after 4/2)" and both kept fractions (`kept_42`,
`kept`).  Resumable: a node is done when its last record is DEAD, SKIPPED(cap ...) at every
level, or ALIVE at the 8/3 setting; an A181 record ALIVE at 4/2 is UPGRADED (its recorded
fixed-point roles re-seeded by the parent's current pieces, then the 8/3 pass only).  A node
wall-capped during the 8/3 pass is retried at 4/2 only, then at 4/1 (renorm181's rule).

    python renorm183.py run --cell l1_104 --shard 0/2 --depth 2
    python renorm183.py run --cell l1_153 --shard 0/2 --depth 5
"""
import argparse
import json
import sys
import time
import os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import cascade168 as CS                                          # noqa: E402
import resume168 as RS                                           # noqa: E402
import polyclip175 as PX                                         # noqa: E402
import renorm175 as RN                                           # noqa: E402
import renorm176 as R6                                           # noqa: E402
import renorm181 as R8                                           # noqa: E402
import multibox as MB                                            # noqa: E402
from caselp import Box, t_lo, t_hi                               # noqa: E402

SET42 = "nsub 4 / refine 2"
SET83 = "nsub 8 / refine 3 (after 4/2)"
_role_to_mbox_orig = PX.role_to_mbox


def role_to_mbox_split(role, tsplit=2):
    """A171 MBox on the role's pieces with every tilt sub-bin bisected `tsplit` ways (tautologous:
    the sub-bins cover the piece's tilt range exactly [T])."""
    mb = _role_to_mbox_orig(role)
    out = []
    for (bn, r) in mb.pieces:
        for (a, b) in MB.sub_bins(bn.t0, bn.t1, tsplit):
            out.append((MB.Bin(a, b), r))
    mb.pieces = out
    return mb


def make_node_83(roles, lonely=True):
    """polyclip175.make_node at nsub 8 / refine 3 (module-level splitter swapped for the call)."""
    PX.role_to_mbox = role_to_mbox_split
    try:
        return PX.make_node(roles, refine=3, lonely=lonely)
    finally:
        PX.role_to_mbox = _role_to_mbox_orig


def rows_of(node, rr):
    rows = {w: R.best_row(rr, CS.lines_of(w)) for w in RN.walls_of(node)}
    kill = bool(any(Fr(r["rhs"]) < 0 for r in rows.values()))
    return rows, kill


def finish(rec, node, rr, rep, par, t0):
    """the record's tail after the LAST pass (DEAD from rep, or ALIVE with rows) -- renorm181's."""
    if rr is None:
        rec.update(verdict="DEAD(C, %s)" % rep["dead"], leaf=rep.get("leaf"), cert=rep.get("cert"),
                   witness=rep.get("witness"), invariant=rep.get("invariant"))
    else:
        rec["roles"] = R.roles_json(rr)
        rec["vol1"] = R6.vols(rr)
        if par is not None and par.get("vol1"):
            rec["vol1_le_parent"] = all(rec["vol1"][k] <= par["vol1"][k] * (1 + 1e-9) + 1e-12
                                        for k in rec["vol1"] if k in par["vol1"])
        rec["invariant"] = rep.get("invariant")
        rec["rows"], rec["row_kill"] = rows_of(node, rr)
        rec["verdict"] = "DEAD(C, chord row A144 LINE-1 on the grown K')" if rec["row_kill"] else R8.VERDICT_ALIVE
        rec["leaf"] = "row" if rec["row_kill"] else None
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def process(T, path, recs, a, refine=None, upgrade=None):
    """4/2 (renorm181.process) then, on a survivor, the 8/3 pass from the 4/2 fixed point.
    `upgrade` = an A181 record ALIVE at 4/2: its roles are re-seeded by the parent and only the
    8/3 pass runs.  refine=2 with a.pass83 off (or refine < 2) = the 4/2-only cap retry."""
    node = T["nodes"][path]
    t0 = time.time()
    par = recs.get(node["parent"]) if node.get("parent") else None
    if par is not None and par["verdict"].startswith("SKIPPED"):
        par = None
    if upgrade is not None:
        rec = dict(upgrade)
        rec.pop("rows", None)
        rec.update(kept_42=upgrade.get("kept"), vol1_42=upgrade.get("vol1"), setting=SET83, upgraded_from="A181 4/2 record")
        roles = [R.Role.from_json(v) for v in upgrade["roles"].values()] if isinstance(upgrade["roles"], dict) else None
        if roles is None:
            rec.update(verdict="SKIPPED(record roles unreadable)", wall_s=0.0)
            return rec
        if par is not None and par["verdict"].startswith("DEAD"):
            rec.update(verdict="DEAD(C, ancestor %s: %s)" % (node["parent"], par["verdict"][:70]), leaf="ancestor", wall_s=0.0)
            return rec
        if par is not None:
            roles, srep = R8.seed_roles(roles, par)
            if roles is None:
                rec.update(verdict="DEAD(C, %s)" % srep, leaf="inheritance", wall_s=round(time.time() - t0, 1))
                return rec
            rec["reseeded_kept"] = {k: v["kept"] for k, v in srep.items()}
        rr, rep = make_node_83(roles, lonely=bool(a.lonely))
        rec.update(kept=rep.get("kept"), kept_mb=rep.get("kept_mb"), k_area=rep.get("k_area"), passes=rep.get("passes"),
                   n_pieces=rep.get("n_pieces"), lonely=[l for l in rep.get("lonely", []) if l["removed"] > 0 or l["dropped"]])
        return finish(rec, node, rr, rep, par, t0)
    rec = R8.process(T, path, recs, a, refine=refine)
    rec["setting"] = SET42 if rec.get("refine") == 2 else "nsub 4 / refine %s" % rec.get("refine")
    if not rec["verdict"].startswith("ALIVE") or not a.pass83 or (refine is not None and refine < 2):
        return rec
    roles = [R.Role.from_json(v) for v in rec["roles"].values()]
    rec.update(kept_42=rec.get("kept"), vol1_42=rec.get("vol1"), passes_42=rec.get("passes"), setting=SET83)
    rr, rep = make_node_83(roles, lonely=bool(a.lonely))
    rec.update(kept=rep.get("kept"), kept_mb=rep.get("kept_mb"), k_area=rep.get("k_area"), passes=rep.get("passes"),
               n_pieces=rep.get("n_pieces"), lonely=[l for l in rep.get("lonely", []) if l["removed"] > 0 or l["dropped"]])
    return finish(rec, node, rr, rep, par, t0)


def done(r):
    if r is None:
        return False
    if r["verdict"].startswith("DEAD"):
        return True
    return r["verdict"].startswith("ALIVE") and r.get("setting") == SET83


def stage_run(a):
    sk, sn = RS.shard_of(a.shard)
    T, n_sh = RN.load_tree_overlay(a.cell, a.overlay)
    recs = R8.load_side(a.cell)
    steps = set(a.steps.split(",")) if a.steps else None
    todo = [p for p in R6.todo_nodes(T, sk, sn, steps, a.depth) if not done(recs.get(p))]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    caps = RS.wallcapped(a.cell)
    out = R8.side_path(a.cell, sk, sn)
    print("renorm183 %s shard %d/%d depth %d: %d nodes to do (%d recorded, %d shard files) setting %s -> %s" % (
        a.cell, sk, sn, a.depth, len(todo), len(recs), n_sh, SET83 if a.pass83 else SET42, out), flush=True)
    t00 = time.time()
    cnt, n_run = {}, 0
    pending, waited = todo, 0

    def emit(p, rec):
        recs[p] = rec
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        key = rec["verdict"].split("(")[0] + ("/" + str(rec.get("leaf")) if rec.get("leaf") else "")
        cnt[key] = cnt.get(key, 0) + 1
        kp = rec.get("kept") or rec.get("kept_mb") or {}
        print("  %-28s %-4s %-40s seeded %s kept42 %s kept %s [%s] %.1fs" % (
            p, rec["step"], rec["verdict"][:40], {k: round(v, 3) for k, v in (rec.get("seeded_kept") or {}).items() if v is not None},
            {k: round(v, 3) for k, v in (rec.get("kept_42") or {}).items()}, {k: round(v, 3) for k, v in kp.items()},
            rec.get("setting"), rec["wall_s"]), flush=True)

    while pending:
        nxt, progress = [], False
        for p in pending:
            if K.sentinel():
                print("sentinel; stop", flush=True)
                return 2
            node = T["nodes"][p]
            r_try, pass83 = None, a.pass83
            if p in caps:                                        # wall-capped: 4/2 only, then 4/1, then 4/0
                m = recs.get(p)
                r_prev = m.get("refine") if (m and m["verdict"].startswith("SKIPPED(cap")) else 3
                r_try = min(r_prev - 1, 2)
                pass83 = False
                if r_try < 0:
                    print("  skip %s (wall-capped at every refine level)" % p, flush=True)
                    continue
                emit(p, dict(node=p, step=node.get("step") or "root", level=node.get("level", 0), parent=node.get("parent"),
                             verdict="SKIPPED(cap attempt refine %d)" % r_try, refine=r_try, wall_s=0.0))
            prev = recs.get(p)
            up = prev if (prev is not None and prev["verdict"].startswith("ALIVE") and prev.get("roles")
                          and prev.get("setting") != SET83 and r_try is None) else None
            a.pass83 = pass83
            with RS.NodeWall(a.cell, p):
                rec = process(T, p, recs, a, refine=r_try, upgrade=up)
            a.pass83 = True
            if rec["verdict"].startswith("SKIPPED"):
                nxt.append(p)
                continue
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
        for q, r in R8.load_side(a.cell).items():
            recs.setdefault(q, r)
        print("  retry: %d nodes waiting for ancestors (%d recorded)" % (len(nxt), len(recs)), flush=True)
        pending = nxt
    print("renorm183 shard %d/%d done: %d run, %s, %.0fs" % (sk, sn, n_run, cnt, time.time() - t00), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("run",))
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--overlay", type=int, default=1)
    ap.add_argument("--refine", type=int, default=2)
    ap.add_argument("--lonely", type=int, default=1)
    ap.add_argument("--steps", default="")
    ap.add_argument("--max_nodes", type=int, default=0)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--pass83", type=int, default=1)
    a = ap.parse_args()
    a.reuse176, a.sample = 0, 0
    sys.exit(stage_run(a) or 0)


if __name__ == "__main__":
    main()
