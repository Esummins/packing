"""A120 T3 -- aggregation, the closures ledger, and the schedule arithmetic.

Reads only this attempt's own records plus A107's `extract.json` (for the structural dedup) and
A96's target list.  Writes

  * `results/t3_report.json`                              -- the whole picture
  * `attempts/A96-a57-parametric/results/a120_closures.jsonl`  -- NEW file, the ledger of closures
    (one row per node processed: its verdict, its four children, the cone it removes, the tags)

THE SCHEDULE ARITHMETIC (A96, LOG.md 2026-09-06).  A57's tree is an 8-way split and A96 measured
the expansion factors f2 = 0.906, f3 = 0.762, f4 = 0 (expected ALIVE children per parent), so an
ALIVE node killed outright removes a descendant cone of

    C3 = 8,  C2 = 8 + f3 C3 = 14.10,  C1 = 8 + f2 C2 = 20.77

nodes (A96's ~8 / ~14.1 / ~20.8).  A96's per-child cost is 240.3 s at level 2 and 291.8 s at level
3 -- "cost does NOT escalate with depth" -- so the cone is priced at both ends of that range.  The
standing schedule after trimming is 10-11 wall-days at 5 workers, i.e. 50-55 CPU-days.
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a120lib as A                                     # noqa: E402

F2, F3, F4 = 0.906, 0.762, 0.0
CONE = {3: 8.0, 2: 8.0 + F3 * 8.0, 1: 8.0 + F2 * (8.0 + F3 * 8.0)}
COST_LO, COST_HI = 240.3, 291.8                          # A96 per-child seconds (L2, L3)
SCHEDULE_WALL_DAYS = (10.0, 11.0)
WORKERS = 5


def groups_index():
    """A107's structural dedup: node id -> group key (same source, same class pins, same
    skeleton)."""
    d = A.jload(os.path.join(A.A107R, "extract.json"))
    nodes = d["nodes"]
    out = {}
    for gk, idxs in d["groups"].items():
        for i in idxs:
            out[nodes[i]["nid"]] = gk
    return out


def collect():
    recs = []
    for p in sorted(glob.glob(os.path.join(A.NODES, "rec__*.json"))):
        try:
            recs.append(A.jload(p))
        except Exception:
            pass
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process_wall_s", type=float, default=0.0,
                    help="measured wall of every A120 process (the true CPU-h against the cap; "
                         "the per-node LP/cert seconds do not include node setup, the soundness "
                         "sampling, warm-start loading, or work lost when a run was restarted)")
    ap.add_argument("--extra_cpu_s", type=float, default=0.0,
                    help="CPU seconds spent outside the node records (T2 controls etc.)")
    a = ap.parse_args()

    recs = collect()
    tg = A.targets()
    by = {r["id"]: r for r in recs}
    gi = groups_index()
    _, entry = A.n_entry()

    closed, open_, partial, skipped, notrun = [], [], [], [], []
    for nid in tg:
        r = by.get(nid)
        if r is None:
            notrun.append(nid)
        elif r["status"] == "CLOSED":
            closed.append(r)
        elif r["status"] == "OPEN":
            open_.append(r)
        elif r["status"] == "SKIP-UNSOUND":
            skipped.append(r)
        else:
            partial.append(r)

    lp = sum(r.get("lp_wall_s", 0.0) for r in recs)
    cert = sum(r.get("cert_wall_s", 0.0) for r in recs)
    flat = sum(r.get("flat900_s", 0.0) for r in recs)
    cpu_s = lp + cert + a.extra_cpu_s

    # ---- cones removed
    cone_nodes = sum(CONE[r["level"]] for r in closed)
    cone_by_level = {}
    for r in closed:
        cone_by_level.setdefault(r["level"], [0, 0.0])
        cone_by_level[r["level"]][0] += 1
        cone_by_level[r["level"]][1] += CONE[r["level"]]
    cone_cpu_lo = cone_nodes * COST_LO / 3600.0
    cone_cpu_hi = cone_nodes * COST_HI / 3600.0

    # ---- what the open nodes re-price to, by A107's dedup
    op = []
    for r in open_:
        k = len(r.get("open_children", []))
        op.append(dict(id=r["id"], level=r["level"], group=gi.get(r["id"]),
                       open_children=r.get("open_children"),
                       dead_children=[c for c, st in zip(sorted(r["children"]),
                                                         r.get("child_status") or [])
                                      if st == "DEAD-CERT"],
                       n_open=k,
                       reason=[dict(child=c, status=r["children"][c]["status"],
                                    eta=(r["children"][c].get("lp") or {}).get("eta"),
                                    converged=(r["children"][c].get("lp") or {}).get("converged"),
                                    cert=(r["children"][c].get("cert") or {}).get("result"),
                                    cert_s=(r["children"][c].get("cert") or {}).get("seconds"))
                               for c in (r.get("open_children") or [])]))
    dedup_groups = sorted({x["group"] for x in op if x["group"]})
    reprice = dict(
        open_nodes=len(open_),
        open_no_children=sum(x["n_open"] for x in op),
        distinct_A107_groups=len(dedup_groups),
        groups=dedup_groups,
        by_group={g: sorted(x["id"] for x in op if x["group"] == g) for g in dedup_groups},
        note=("an OPEN node re-prices to its surviving NO children only -- the YES leaf is gone "
              "for good (local certificate) and every certified NO child is gone for good; the "
              "ordinary A57 alternative is an 8-way split, so the residue is n_open/8 of one "
              "level of the old tree, and A107's structural dedup collapses the %d open nodes "
              "onto %d distinct structures" % (len(open_), len(dedup_groups))))

    # ---- the CHILD-LEVEL picture, which is what the NO side actually achieves and is
    # independent of how much certifier time was spent
    kids = [(r, k, c) for r in recs for k, c in sorted(r["children"].items())]
    def eta_of(c):
        return (c.get("lp") or {}).get("eta")
    lp_dead = [x for x in kids if (eta_of(x[2]) is not None and eta_of(x[2]) <= -1e-3)]
    certified = [x for x in kids if x[2]["status"] == "DEAD-CERT"]
    survivors = [x for x in kids if x[2]["status"] == "ALIVE"
                 and (eta_of(x[2]) is None or eta_of(x[2]) > -1e-3)]
    shortfall = [x for x in kids if x[2]["status"] == "ALIVE"
                 and eta_of(x[2]) is not None and eta_of(x[2]) <= -1e-3]
    children = dict(
        total=len(kids),
        lp_clearly_below_budget=len(lp_dead),
        certified_dead=len(certified),
        genuine_survivors_eta_at_budget=len(survivors),
        certifier_shortfall=len(shortfall),
        shortfall_detail=[dict(node=r["id"], child=k, eta=eta_of(c),
                               first=(c.get("cert") or {}).get("result"),
                               first_s=(c.get("cert") or {}).get("seconds"),
                               retry=(c.get("cert_retry") or {}).get("result"),
                               retry_s=(c.get("cert_retry") or {}).get("seconds"))
                          for (r, k, c) in shortfall],
        survivor_detail=[dict(node=r["id"], child=k, box=c["box"], eta=eta_of(c),
                              converged=(c.get("lp") or {}).get("converged"),
                              tau=(c.get("lp") or {}).get("tau"))
                         for (r, k, c) in survivors],
        note=("a NO child with eta ~ 0 is a GENUINE survivor -- the node LP says it is not below "
              "budget and no certifier time can change that; a child with eta <= -1e-3 whose "
              "certificate FAILed or was CAPped is a certifier shortfall, not a survivor"))

    # ---- soundness roll-up
    snd = dict(nodes=len(recs), all_ok=all(r["soundness"]["ok"] for r in recs),
               failed=[r["id"] for r in recs if not r["soundness"]["ok"]],
               checks=sorted({k for r in recs for k in r["soundness"]["checks"]}),
               same_boxes_same_frame=all(
                   all(c["box_identical_to_yes"]["ok"] for c in r["children"].values())
                   for r in recs),
               roundtrip_samples=dict(
                   drawn=sum(r["soundness"]["checks"]["A4_map_invertible"]["sample"]["drawn"]
                             for r in recs),
                   tested=sum(r["soundness"]["checks"]["A4_map_invertible"]["sample"]["tested"]
                              for r in recs),
                   inside=sum(r["soundness"]["checks"]["A4_map_invertible"]["sample"]
                              ["inside_class_boxes"] for r in recs)))
    trump = [dict(id=r["id"], child=k, realizes=c.get("trump_realizes"))
             for r in recs for k, c in r["children"].items()
             if c.get("trump_realizes") is True]

    out = dict(
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        N=entry["id"], s0=A.S0, yes_claim=A.YES_CLAIM, no_side_window=A.NO_TAG,
        targets=len(tg), processed=len(recs),
        closed=[dict(id=r["id"], level=r["level"], cls=r["cls"], cone=CONE[r["level"]],
                     lp_s=r["lp_wall_s"], cert_s=r["cert_wall_s"],
                     claim=r.get("claim")) for r in closed],
        open=op, partial=[r["id"] for r in partial], skipped_unsound=[r["id"] for r in skipped],
        not_run=notrun,
        counts=dict(closed=len(closed), open=len(open_), partial=len(partial),
                    skipped=len(skipped), not_run=len(notrun),
                    closed_by_level={lv: sum(1 for r in closed if r["level"] == lv)
                                     for lv in sorted({r["level"] for r in closed})} if closed else {},
                    open_by_level={lv: sum(1 for r in open_ if r["level"] == lv)
                                   for lv in sorted({r["level"] for r in open_})} if open_ else {}),
        cpu=dict(lp_wall_s=round(lp, 1), cert_wall_s=round(cert, 1),
                 controls_and_other_s=round(a.extra_cpu_s, 1),
                 total_s=round(cpu_s, 1), total_cpu_h=round(cpu_s / 3600.0, 2),
                 process_wall_s=round(a.process_wall_s, 1),
                 process_wall_cpu_h=round(a.process_wall_s / 3600.0, 2),
                 flat900_counterfactual_s=round(flat, 1),
                 protocol_saving_factor=(round(flat / lp, 2) if lp else None),
                 cap_cpu_h=15.0),
        cones=dict(model=dict(f2=F2, f3=F3, f4=F4, C1=round(CONE[1], 2), C2=round(CONE[2], 2),
                              C3=CONE[3],
                              per_child_seconds=[COST_LO, COST_HI],
                              source="A96 level-3 probe, LOG.md 2026-09-06"),
                   closed_by_level={str(k): dict(nodes=v[0], cone_nodes=round(v[1], 1))
                                    for k, v in sorted(cone_by_level.items())},
                   cone_nodes_removed=round(cone_nodes, 1),
                   cpu_h_removed=[round(cone_cpu_lo, 2), round(cone_cpu_hi, 2)],
                   cpu_days_removed=[round(cone_cpu_lo / 24.0, 3), round(cone_cpu_hi / 24.0, 3)],
                   wall_days_at_5_workers=[round(cone_cpu_lo / 24.0 / WORKERS, 4),
                                           round(cone_cpu_hi / 24.0 / WORKERS, 4)],
                   schedule_wall_days=list(SCHEDULE_WALL_DAYS),
                   note=("the cone is the A57 subtree the closure removes; it is priced at A96's "
                         "own per-child cost and is a DIRECT saving on the 10-11 wall-day "
                         "schedule, not a re-derivation of it")),
        children=children, reprice=reprice, soundness=snd, trump_violations=trump)

    A.jdump(os.path.join(A.RES, "t3_report.json"), out)

    # ---- the closures ledger (a NEW file under A96, nothing else there is touched)
    led = os.path.join(A.A96R, "a120_closures.jsonl")
    rows = []
    for nid in tg:
        r = by.get(nid)
        if r is None:
            rows.append(dict(id=nid, cls=A.node_cls(nid), level=A.node_level(nid),
                             status="NOT-RUN", reason="A120 CPU cap"))
            continue
        rows.append(dict(
            id=r["id"], cls=r["cls"], level=r["level"], s=r["s"], budget=r["budget"],
            status=r["status"], struct_op=r["struct_op"], N=r["N"],
            yes=dict(status=r["yes"]["status"], claim=r["yes"]["claim"]),
            no_children={k: dict(box=c["box"], status=c["status"],
                                 eta=(c.get("lp") or {}).get("eta"),
                                 cert=(c.get("cert") or {}).get("result"),
                                 tag=c.get("cert_tag"))
                         for k, c in sorted(r["children"].items())},
            cone_removed=(CONE[r["level"]] if r["status"] == "CLOSED" else 0.0),
            soundness_ok=r["soundness"]["ok"],
            same_boxes_same_frame=all(c["box_identical_to_yes"]["ok"]
                                      for c in r["children"].values()),
            no_side_window=A.NO_TAG,
            claim=r.get("claim"),
            source="attempts/A120-no-side-runner (T1 runner, A112 protocol, frozen verify_case.py)"))
    tmp = led + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    os.replace(tmp, led)

    print(json.dumps(dict(counts=out["counts"], cpu=out["cpu"], cones=out["cones"],
                          children={k: v for k, v in children.items()
                                    if not k.endswith("_detail")},
                          reprice={k: v for k, v in reprice.items() if k != "by_group"},
                          soundness={k: v for k, v in snd.items() if k != "checks"},
                          trump_violations=trump), indent=1))


if __name__ == "__main__":
    main()
