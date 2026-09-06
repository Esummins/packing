"""A109 -- the certification-engine probe.

If the crowd rows kill no ALIVE node there is nothing to certify, and the brief's question
"does a node-level box escape A94's B_2..B_4 hole failure mode?" would go unanswered.  This
builds a second plan of A57 nodes that are ALREADY DEAD (dead == True, so tau < budget with
margin): adding crowd rows can only raise both tau and the budget, and the resulting certificate
is exactly the 1 + r_max chain of A94 sec 4 at NODE scale.  Certifying those answers the engine
question with no soundness pretence -- these nodes were dead before A109 touched them.
"""
import json, os, random, sys, glob
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a109lib as L

N = 12
SEED = 10910


def main():
    rnd = random.Random(SEED)
    cands = []
    for p in glob.glob(os.path.join(L.ROOT, "attempts/A57-shadow-trees/results/tree/*/*.json")):
        nid = os.path.splitext(os.path.basename(p))[0]
        cls = L.cls_of(nid)
        if cls is None:
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if not d.get("dead"):
            continue
        if len(d["hyp"]["boxes"]) != 6:          # level 1-2 shape: 5 pins + 1 branched core
            continue
        # a comfortable margin so the crowd rows cannot flip it back alive
        if d["tau"] > d["budget"] - 0.5:
            continue
        lvl = 1 + nid.count("_D")
        cands.append(dict(nid=nid, src="A57", shard=os.path.basename(os.path.dirname(p)),
                          cls=cls, level=lvl, tau=d["tau"], budget=d["budget"],
                          eta=d["tau"] - d["budget"]))
    rnd.shuffle(cands)
    by = {}
    for c in cands:
        by.setdefault((c["cls"], c["level"]), []).append(c)
    plan, keys = [], sorted(by)
    while len(plan) < N and any(by[k] for k in keys):
        for k in keys:
            if len(plan) >= N:
                break
            if by[k]:
                c = by[k].pop()
                p = L.copy_node(c["nid"], "A57")
                if p is None:
                    continue
                c["path"] = os.path.relpath(p, L.ROOT).replace("\\", "/")
                c["stratum"] = "already-dead"
                c["shadow"] = None
                plan.append(c)
    json.dump(plan, open(os.path.join(L.RES, "t2_plan_dead.json"), "w"), indent=1)
    print("dead-node probe plan: %d of %d candidates" % (len(plan), len(cands)))
    print(Counter((p["cls"], p["level"]) for p in plan))
    print([ (p["nid"], round(p["eta"], 2)) for p in plan ])


if __name__ == "__main__":
    main()
