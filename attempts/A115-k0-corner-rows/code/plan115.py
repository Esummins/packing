"""A115 -- pick the T2 node set: >= 30 K01 cells stratified over the four corners (which corner
the shadow leaves singly met) and levels 1-3, plus the three Trump-image canary cells.

`room` corner of a cell = the corner with the FEWEST meeters of the closed cell [0,1]^2 in its
shadow (ties broken by the smallest second-meeter mu, then by name): the corner whose "room" the
K01 support is exploiting.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a115lib as L

TARGET_L1 = 20
TARGET_L2 = 8
TARGET_L3 = 4
OUT = os.path.join(L.RES, "t2_plan.json")
CANARY = ["node_021", "node_152", "node_153"]     # A38 l1 idx 21/152/153 (Trump images)


def room_corner(rec):
    best = None
    for c in L.CORNERS:
        p = rec["corners"][c]
        mus = [m for m in p["mu_sorted"] if m <= 1.0 + 1e-12]
        key = (p["n_closed"], mus[1] if len(mus) > 1 else 9.0, c)
        if best is None or key < best[0]:
            best = (key, c)
    return best[1]


def main():
    log = L.logger("plan.log")
    recs = json.load(open(os.path.join(L.RES, "t1_corners.json")))["recs"]
    for r in recs:
        r["room"] = room_corner(r)
    bylvl = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in recs:
        bylvl[r["level"]][r["room"]].append(r)

    plan = []
    for lvl, want in ((1, TARGET_L1), (2, TARGET_L2), (3, TARGET_L3)):
        pool = bylvl[lvl]
        # round-robin over the corners; within a corner take FIRST the cells that are genuinely
        # alive at the LP (tau0 >= budget: the rows' kill would be attributable to them), then the
        # cells whose fractional crowd weight is smallest (the ones with any chance of c < B)
        for c in pool:
            pool[c].sort(key=lambda r: (0 if r["at_budget"] else 1, r["frac_wt_all_wide"], r["nid"]))
        picked, i = [], 0
        order = [c for c in L.CORNERS if pool.get(c)]
        while len(picked) < want and any(pool[c] for c in order):
            c = order[i % len(order)]
            if pool[c]:
                picked.append(pool[c].pop(0))
            i += 1
        plan.extend(picked)

    seen = {r["nid"] for r in plan}
    canary = []
    idx = L.extract_index()
    for nid in CANARY:
        ent = dict(nid=nid, kind="canary")
        if nid in idx:
            ent["path"] = idx[nid]["path"]
            ent["has_lp"] = True
        else:
            ent["path"] = "attempts/A38-root-power/results/l1_nodes/%s.rec.json" % nid
            ent["has_lp"] = False
        ent["in_plan"] = nid in seen
        canary.append(ent)

    out = dict(n=len(plan), target=dict(l1=TARGET_L1, l2=TARGET_L2, l3=TARGET_L3),
               canary=canary,
               nodes=[dict(nid=r["nid"], src=r["src"], level=r["level"], room=r["room"],
                           budget=r["budget"], tau0=r["tau"], converged0=r["converged"],
                           at_budget=r["at_budget"], eta0=round(r["tau"] - r["budget"], 6),
                           frac_wt_wide=r["frac_wt_all_wide"], frac_total=r["frac_total"],
                           n_closed={c: r["corners"][c]["n_closed"] for c in L.CORNERS},
                           path=idx[r["nid"]]["path"])
                      for r in plan])
    json.dump(out, open(OUT, "w"), indent=1)
    cnt = collections.Counter((r["level"], r["room"]) for r in plan)
    log("A115 plan: %d nodes" % len(plan))
    log("  by (level, room corner): %s" % dict(sorted(cnt.items())))
    log("  by source: %s" % dict(collections.Counter(r["src"] for r in plan)))
    log("  canary: %s" % [(c["nid"], c["has_lp"], c["in_plan"]) for c in canary])
    log("wrote %s" % OUT)


if __name__ == "__main__":
    main()
