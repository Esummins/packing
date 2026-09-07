"""A112 T2 -- run the region tree with the three orderings over a region set.

  python run112.py --set s02 --ordering stranded --shard 0/2 --wall 900 --lp_cap 900

Resumable: every region-tree node has its own record file under results/rt/<region>/<ordering>/,
and a node whose record exists is never recomputed.  One line per region goes to
results/t2_<set>_<ordering>.jsonl.

<= 2 processes, BLAS pinned, memory gate before every LP and certificate, READ-ONLY on every
campaign (root node jsons are copied first by plan112).
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L
import regiontree as RT
from caselp import Hyp


def old_tree_projection(root_res, level, per_child_s=290.0, fanout=8, descent=(0.91, 0.76, 0.0)):
    """A96's model, as the brief states it: 290 s per child, fan-out 8, measured descent
    0.91 / 0.76 / 0 at levels 1->2 / 2->3 / 3->4.  A stalled node at level L is split into 8
    children; a fraction `descent` of them are themselves alive and split again; the tree
    terminates at level 4 (descent 0 of 30 measured).  Returns (nodes, LPs, wall seconds)."""
    d = list(descent) + [0.0] * 8
    nodes, lps, wall, alive = 0, 0, 0.0, 1.0
    lvl = level
    while alive > 1e-9 and lvl <= 4:
        kids = alive * fanout
        nodes += kids
        lps += kids
        wall += kids * per_child_s
        alive = kids * d[min(lvl - 1, len(d) - 1)]
        lvl += 1
    return dict(nodes=round(nodes, 2), lps=round(lps, 2), wall_s=round(wall, 1),
                model="A96: %gs/child, fan-out %d, descent %s" % (per_child_s, fanout, descent))


def run_region(pl, ordering, A, log):
    region = pl["region"]
    res0 = L.jload(pl["path"])
    s = res0["s"]
    lp_boxes, lp_rank = None, None
    if pl["kind"] == "a57":
        try:
            lp_boxes = L.loadpath_boxes(pl["shadow"], pl["cls"], A.lp_r, A.lp_rho, pl["op"], s)
            lp_rank, _ = L.loadpath_rank(pl["shadow"], pl["cls"])
        except Exception as ex:
            log("  loadpath boxes unavailable: %s" % repr(ex)[:120])
    r = RT.Runner(region, ordering, s, res0["budget"], log, lp_cap=A.lp_cap, stage1=A.stage1,
                  depth_cap=A.depth_cap, node_cap=A.node_cap, wall=A.wall, kind=pl["kind"],
                  area=A.area, sample_n=A.sample_n)
    r.cert_time = A.cert_time
    t0 = time.time()
    leaves, internal = r.run(res0, lp_boxes=lp_boxes, lp_rank=lp_rank)
    # Under the PI's protocol every kill is a CERTIFIED pass (or a logic / chain kill); the
    # certifier already ran inline at every node the LP put below budget, so nothing is certified
    # here.  A leaf that is not dead is OPEN.
    DEADS = ("DEAD-LOGIC", "DEAD-CLASS", "DEAD-CHAIN-LP", "DEAD-CERT")
    open_leaves = [x for x in leaves if x.get("status") not in DEADS]
    certs = [x["cert"] for x in (leaves + internal) if x.get("cert")]
    cert_wall = sum(c.get("seconds", 0.0) for c in certs)
    cont = RT.containment(region, ordering, leaves, internal, res0, pl["path"])
    out = dict(region=region, ordering=ordering, kind=pl["kind"], level=pl.get("level"),
               cls=pl.get("cls"), shadow=pl.get("shadow"), op=pl.get("op"),
               budget=res0["budget"], s=s, tau0=res0["tau"],
               conv0=bool(res0.get("converged")),
               nodes=r.stats["nodes"], leaves=len(leaves), internal=len(internal),
               lps=r.stats["lps"], lp_wall=round(r.stats["lp_wall"], 1),
               flat900_wall=round(r.stats["flat900_wall"], 1),
               certs_pass=r.stats["certs_pass"], certs_fail=r.stats["certs_fail"],
               logic_kills=r.stats["logic_kills"], class_clause=r.stats["class_clause"],
               chain_kills=r.stats["chain_kills"],
               fires=r.stats["fires"], sampled_pairs=r.stats["sampled_pairs"],
               counterexamples=r.stats["counterexamples"],
               cert_wall=round(cert_wall, 1), certs=certs,
               wall=round(time.time() - t0, 1),
               open_leaves=[x["key"] for x in open_leaves],
               leaf_status={x["key"]: x.get("status") for x in leaves},
               killed=bool(cont["transfers"]),
               containment=cont,
               old_tree=old_tree_projection(res0, pl.get("level") or 1,
                                            per_child_s=A.per_child_s))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="rset", default="s02", choices=["s02", "k0"])
    ap.add_argument("--ordering", default="stranded",
                    choices=["stranded", "loadpath", "hybrid", "wastage"])
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--wall", type=float, default=900.0, help="wall seconds per region tree")
    ap.add_argument("--lp_cap", type=float, default=900.0)
    ap.add_argument("--stage1", type=float, default=RT.LP_STAGE1)
    ap.add_argument("--depth_cap", type=int, default=6)
    ap.add_argument("--node_cap", type=int, default=40)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--per_child_s", type=float, default=290.0)
    ap.add_argument("--lp_r", type=float, default=0.1)
    ap.add_argument("--lp_rho", type=float, default=10.0)
    ap.add_argument("--sample_n", type=int, default=400)
    ap.add_argument("--area", action="store_true", help="also score the unusable-area variant")
    ap.add_argument("--certify", action="store_true", default=True)
    ap.add_argument("--no_certify", dest="certify", action="store_false")
    ap.add_argument("--minutes", type=float, default=600.0)
    ap.add_argument("--only", default="")
    A = ap.parse_args()

    plan = L.jload(os.path.join(L.RES, "plan.json"))[A.rset]
    si, sn = map(int, A.shard.split("/"))
    plan = [p for i, p in enumerate(plan) if i % sn == si]
    if A.only:
        keep = set(v for v in A.only.split(",") if v)
        plan = [p for p in plan if p["region"] in keep]
    log = L.mklog("run_%s_%s_s%d.log" % (A.rset, A.ordering, si))
    sink = os.path.join(L.RES, "t2%s_%s_%s.jsonl" % (L.SUF, A.rset, A.ordering))
    done = set()
    if os.path.exists(sink):
        for line in open(sink, encoding="utf-8"):
            try:
                done.add(json.loads(line)["region"])
            except Exception:
                pass
    T_END = time.time() + 60 * A.minutes
    log("A112 %s / %s : %d regions (shard %s), wall %gs each, LP cap %gs"
        % (A.rset, A.ordering, len(plan), A.shard, A.wall, A.lp_cap))
    for pl in plan:
        if pl["region"] in done:
            log("  %s already recorded, skipping" % pl["region"])
            continue
        if time.time() > T_END:
            log("wall budget exhausted"); break
        log("== %s (L%s %s tau0=%.6f conv=%s)" % (pl["region"], pl.get("level"), pl.get("cls"),
                                                  pl["tau"], pl["converged"]))
        try:
            out = run_region(pl, A.ordering, A, log)
        except BaseException as ex:
            import traceback
            log("  ERROR %s: %s" % (pl["region"], traceback.format_exc()[-800:]))
            out = dict(region=pl["region"], ordering=A.ordering, error=repr(ex)[:300])
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps(out) + "\n")
        log("  -> nodes=%s lps=%s lp_wall=%ss (flat-900 %ss) cert=%ss %sP/%sF logic=%s "
            "chain=%s killed=%s open=%s"
            % (out.get("nodes"), out.get("lps"), out.get("lp_wall"), out.get("flat900_wall"),
               out.get("cert_wall"), out.get("certs_pass"), out.get("certs_fail"),
               out.get("logic_kills"), out.get("chain_kills"), out.get("killed"),
               len(out.get("open_leaves") or [])))
    log("A112 %s/%s shard %s done" % (A.rset, A.ordering, A.shard))


if __name__ == "__main__":
    main()
