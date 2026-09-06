"""A111 -- recompute the T1 selection census REPORT fields.

The first version of `t1_yes.loaded_pairs` keyed a pair in the shadow's name order while
`selection_census` keys it in the box-then-pin order, so a (box, pin) pair whose two names fall on
opposite sides of that split was missed by the join and reported with n_possible = 0.  That is a
REPORTING bug only -- the LP rows, the branch-and-bound and the direct minimiser never use the
join, and none of their numbers change -- but `loaded_forced` / `selection_forced` /
`loaded_detail` do.  This recomputes exactly those three fields, in place, from the same interval
census (no LP, seconds).
"""
from __future__ import annotations

import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T


def fix(path):
    if not os.path.exists(path):
        return 0
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    for r in rows:
        pin_names = tuple(r["pins"])
        ext = tuple(n for n in r.get("anchors") or ())
        _, _, _, _, _, lp, B = T.make_boxes(r["tag"], r["r"], r["rho"], extra=ext)
        pins = T.pins_spec(pin_names, r["pin_slack"])
        cen = T.selection_census(B, lp, pins, T.S_WIN_LO, T.S0)
        loaded = T.loaded_pairs(r["tag"], pin_names, lp)
        det = []
        for k, (o, kk, sg, g) in loaded.items():
            poss = cen.get(k, [])
            det.append(dict(pair="%s|%s" % k, n_possible=len(poss), shadow_sel=[o, kk, sg],
                            shadow_possible=bool((o, kk, sg) in poss),
                            forced=bool(len(poss) == 1 and poss[0] == (o, kk, sg))))
        r["loaded_detail"] = det
        r["loaded_pairs"] = len(loaded)
        r["loaded_forced"] = sum(1 for d in det if d["forced"])
        r["selection_forced"] = bool(r["loaded_forced"] == len(loaded))
        r["n_pairs"] = len(cen)
        r["n_forced"] = sum(1 for v in cen.values() if len(v) == 1)
        r["n_infeasible_pairs"] = sum(1 for v in cen.values() if len(v) == 0)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return len(rows)


def main():
    for nm in ("t1_radius.jsonl", "t1_treelevel.jsonl", "t1_threshold.jsonl"):
        n = fix(os.path.join(L.RES, nm))
        print("%-22s %d rows re-scored" % (nm, n), flush=True)


if __name__ == "__main__":
    main()
