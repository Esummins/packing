"""A159 T4 -- the fold-in.

Writes `results/joint_kills159.jsonl` (A115/A99's node-record shape, as A141's
`polycore_lane_kills.jsonl` uses it) and appends the `polycore_status` column to
`docs/shadows/k0v4/review_k0v4.csv`.  The three prose appends (A115 `notes/t6_report.md`,
`docs/budget.md`, `docs/residue_ledger.md`) are made by hand so their wording is exact.

    python fold159.py
"""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A141 = os.path.join(ROOT, "attempts", "A141-polycore-lane")
CSV = os.path.join(ROOT, "docs", "shadows", "k0v4", "review_k0v4.csv")


def load(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out


def main():
    xw = {(r["cell"], r["corner"]): r for r in load(os.path.join(BASE, "results",
                                                                 "xwitness159.jsonl"))}
    tc = {(r["cell"], r["corner"]): r for r in load(os.path.join(BASE, "results",
                                                                 "twocrowd159.jsonl"))}
    uw = {(r["cell"], r["corner"]): r for r in load(os.path.join(BASE, "results",
                                                                 "unwiden159.jsonl"))}
    sl = {(r["cell"], r["corner"]): r for r in load(os.path.join(BASE, "results",
                                                                  "sampleline159.jsonl"))}
    sp = load(os.path.join(BASE, "results", "split159.jsonl"))
    spd = {(r["cell"], r["corner"]): r for r in sp}
    # the deeper pass supersedes the shallow record for the cells it re-ran
    for r in load(os.path.join(BASE, "results", "split159_deep.jsonl")):
        r = dict(r, deeper_pass=True)
        spd[(r["cell"], r["corner"])] = r
    # the canary is a witness-chain record, not a split record; it is folded in as its own field
    can = {(r["cell"], r["corner"]): r for r in
           load(os.path.join(BASE, "results", "canary159.jsonl")) if "chain" in r}

    rows = {}
    for f in sorted(glob.glob(os.path.join(A141, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            rows.setdefault(r["cell"], r)

    out = []
    keys = sorted(set(list(spd) + list(xw) + list(tc)))
    for k in keys:
        cid, corner = k
        w = xw.get(k)
        t = tc.get(k)
        s = spd.get(k)
        q = sl.get(k)
        # a uniform-draw hit is a realised two-crowd too (each was re-verified exactly); the
        # cross-check between the optimiser and the uniform draws caught one the optimiser missed
        hit_w = bool(q and q["widened"]["hits"] > 0)
        hit_u = bool(q and q["unwidened"]["hits"] > 0)
        rec = dict(
            cell=cid, corner=corner, camp="k0", leaf="polycore_split_lane",
            attempt="A159", record=rows[cid].get("record"), level=rows[cid].get("level"),
            n_boxes=rows[cid]["n_boxes"], boxes=rows[cid]["boxes"],
            lane_ub_A141=rows[cid]["corners"][corner]["lane_ub"],
            M_A141=rows[cid]["corners"][corner]["M"],
            a141_twocrowd_claimed=bool(w),
            a141_twocrowd_exact=(bool(w["SURVIVES"]) if w else None),
            both_meet_unwidened_cell=(bool(w and w["H_vs_unwidened"][1] < 0
                                           and w["free_vs_unwidened"][1] < 0) if w else None),
            joint_split_run=bool(s),
            joint_split_closed=(bool(s["closed"]) if s else None),
            n_pieces=(s.get("n_pieces") if s else None),
            n_meet_pieces=(s.get("n_meet_pieces") if s else None),
            n_miss_pieces=(s.get("n_miss_pieces") if s else None),
            cert=(s.get("cert") if s else None),
            sha256=(s.get("sha256") if s else None),
            same_as=(s.get("same_as") if s else None),
            open_reasons=(s.get("open_reasons") if s else None),
            deeper_pass=(bool(s.get("deeper_pass")) if s else None),
            canary_chain_depths=(len(can[k]["chain"]) if k in can else None),
            canary_fired=(bool(can[k]["fired"]) if k in can else None),
            twocrowd_J_widened=(t["widened"]["best_J"] if t else None),
            twocrowd_J_unwidened=(t["unwidened"]["best_J"] if t else None),
            unwidened_lane_ub=(uw[k]["lane_ub"] if k in uw else None),
            unwidened_M=(uw[k]["M"] if k in uw else None),
            unwidened_kill_s0_only=(bool(uw[k]["kill"]) if k in uw else None),
            twocrowd_exact_widened=bool((w and w["SURVIVES"]) or hit_w
                                        or (t and (t["widened"].get("exact") or {})
                                            .get("SURVIVES"))),
            twocrowd_realised_unwidened=bool(hit_u
                                             or (t and (t["unwidened"].get("exact") or {})
                                                 .get("SURVIVES"))),
            sample_line=(dict(widened=q["widened"], unwidened=q["unwidened"],
                              consistent_with_optimiser=q["consistent_with_optimiser"])
                         if q else None),
            verdict=("KILL" if (s and s["closed"]) else
                     ("REFUTED-BY-EXACT-TWO-CROWD"
                      if ((w and w["SURVIVES"]) or hit_w
                          or (t and (t["widened"].get("exact") or {}).get("SURVIVES")))
                      else "OPEN")),
        )
        out.append(rec)
    p = os.path.join(BASE, "results", "joint_kills159.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    print("wrote %s (%d rows, %d KILL, %d REFUTED, %d OPEN)"
          % (os.path.relpath(p, ROOT), len(out),
             sum(1 for r in out if r["verdict"] == "KILL"),
             sum(1 for r in out if r["verdict"] == "REFUTED-BY-EXACT-TWO-CROWD"),
             sum(1 for r in out if r["verdict"] == "OPEN")))

    # ---- review_k0v4.csv: append the polycore_status column (one new column, nothing else)
    with open(CSV, newline="", encoding="utf-8-sig") as fh:
        rd = list(csv.reader(fh))
    hdr = rd[0]
    if "polycore_status" in hdr:
        print("review_k0v4.csv already has polycore_status; not appending again")
        return
    by = {}
    for r in out:
        by.setdefault(r["cell"], []).append(r)
    hdr.append("polycore_status")
    for row in rd[1:]:
        node = row[1]
        recs = by.get(node, [])
        if not recs:
            row.append("A159: no near-miss corner on this cell")
            continue
        bits = []
        for r in sorted(recs, key=lambda z: z["corner"]):
            if r["verdict"] == "KILL":
                bits.append("%s KILL by joint split (A159, %s)" % (r["corner"], r["cert"]))
            elif r["verdict"] == "REFUTED-BY-EXACT-TWO-CROWD":
                bits.append("%s NEAR-MISS with an EXACT realised two-crowd at the WIDENED box "
                            "(A159 T1/T1c, verified at 60 dps) -- no lane leaf can fire; at the "
                            "unwidened cell TR(0,0) the joint optimum is J = %s (%s)"
                            % (r["corner"], ("%.3e" % r["twocrowd_J_unwidened"])
                               if r["twocrowd_J_unwidened"] is not None else "n/a",
                               "two-crowd REALISED there too"
                               if r["twocrowd_realised_unwidened"]
                               else "mutually exclusive there, as the PI reads"))
            else:
                bits.append("%s NEAR-MISS, joint split did NOT close (A159: %s pieces, %s open, "
                            "every open piece with a certified lane_ub >= 1)"
                            % (r["corner"], r["n_pieces"], (r.get("open_reasons") or {})
                               .get("lane_ge_1", "?")))
        row.append("; ".join(bits))
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rd)
    print("appended polycore_status to %s" % os.path.relpath(CSV, ROOT))


if __name__ == "__main__":
    sys.exit(main())
