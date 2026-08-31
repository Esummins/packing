#!/usr/bin/env python3
"""Pick the depth-3 parents: one surviving depth-2 child from each of an alive(LP) l1 parent,
an undecided l1 parent and a notrun l1 parent (prefer alive(LP) children, else highest-tau
survivor)."""
import json, sys, os

SURV = ("alive(LP)", "undecided")
GROUPS = [("alive", "alive"), ("undecided", "undec_mid_lowtau,undec_mid_hitau,undec_edge"),
          ("notrun", "notrun_corner")]


def main(inp, out, nmax=3):
    doc = json.load(open(inp))
    recs = doc["records"]
    picked, seen_group = [], set()
    for gname, strata in GROUPS:
        S = set(strata.split(","))
        C = [r for r in recs if r["stratum"] in S and r["status"] in SURV]
        if not C:
            print("group %s: no surviving child" % gname); continue
        C.sort(key=lambda r: (0 if r["status"] == "alive(LP)" else 1,
                              -(r.get("tau") if r.get("tau") is not None else -1)))
        r = C[0]
        picked.append(dict(id=r["cid"].replace("l2_", ""), stratum="l3_" + gname, budget=10,
                           box=r["box"], l2_parent=r["parent"], l2_status=r["status"],
                           l2_tau=r.get("tau"), l2_c_core=r.get("c_core"),
                           l1_stratum=r["stratum"], n_candidates=len(C)))
        print("group %-10s -> %s  status=%s tau=%s  (of %d survivors)"
              % (gname, r["cid"], r["status"], r.get("tau"), len(C)))
    picked = picked[:nmax]
    json.dump(picked, open(out, "w"), indent=1)
    print("wrote %d parents -> %s" % (len(picked), out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3)
