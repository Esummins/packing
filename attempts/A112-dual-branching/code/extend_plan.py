"""A112 -- extend the S02 region list with nodes that SURVIVE the T5'' octagon trim.

Six of the first twelve S02 regions turn out to be killed outright by A96's T5'' trim at the ROOT
(their conditioned bin is empty once every tilt sub-interval inside a pin's octagon is removed).
Those are pre-existing kills of an already-measured A96 lever, not region-tree kills, and they say
nothing about the branching ORDER because all four orderings terminate at node 1.  So the region
list is extended with nodes whose bin survives the trim, keeping the original twelve (the runs are
resumable: run112 skips a region already recorded in its sink).

Usage: python extend_plan.py <target survivors>
"""
from __future__ import annotations

import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a112lib as L
import plan112 as P


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    plan = L.jload(os.path.join(L.RES, "plan.json"))
    have = plan["s02"]
    keep_ids = {o["nid"] for o in have}
    survivors = [o for o in have if not o["trim"]["emptied"]]
    _, pool = P.plan_s02(n=0)
    extra = []
    strata = {}
    for o in pool:
        if o["nid"] in keep_ids or o["trim"]["emptied"]:
            continue
        strata.setdefault((o["cls"], o["level"]), []).append(o)
    order = sorted(strata)
    i = 0
    while len(survivors) + len(extra) < target and any(strata[k] for k in order):
        k = order[i % len(order)]
        i += 1
        if strata[k]:
            extra.append(strata[k].pop(0))
    plan["s02"] = have + extra
    plan["s02_root_trim_dead"] = [o["nid"] for o in have if o["trim"]["emptied"]]
    plan["s02_survivors_target"] = target
    L.jdump(os.path.join(L.RES, "plan.json"), plan)
    print(json.dumps(dict(kept=len(have), root_trim_dead=len(plan["s02_root_trim_dead"]),
                          survivors_before=len(survivors), added=len(extra),
                          total=len(plan["s02"]),
                          added_ids=[dict(nid=o["nid"], L=o["level"], cls=o["cls"],
                                          sup=o["support"], op=o["op"]) for o in extra]), indent=1))


if __name__ == "__main__":
    main()
