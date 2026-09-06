"""A109 -- pick the T2 node set (stratified) and copy every chosen node json into A109's own
results/nodes/ (nothing under A57/A60/A61/A94/A96/A107 is ever written)."""
import json, os, random, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a109lib as L

ROOT = L.ROOT
WANT = {"S01": 15, "S03": 8, "S04": 8, "S05": 5}
N_CONTROL = 10
SEED = 109109


def main():
    rnd = random.Random(SEED)
    sn = json.load(open(os.path.join(ROOT, "attempts/A107-shadow-gallery/results/shadow_nodes.json")))
    unexp = json.load(open(os.path.join(ROOT, "attempts/A107-shadow-gallery/results/unexplained.json")))
    t1 = {r["nid"]: r for r in json.load(open(os.path.join(L.RES, "t1_incidence.json")))}
    plan, taken = [], set()

    def add(rec, stratum, shadow=None):
        nid = rec["nid"]
        if nid in taken:
            return False
        cls = L.cls_of(nid)
        if cls is None:
            return False
        p = L.copy_node(nid, rec.get("src"))
        if p is None:
            return False
        d = json.load(open(p))
        taken.add(nid)
        r = t1.get(nid, {})
        plan.append(dict(nid=nid, src=rec.get("src"), shard=rec.get("shard"), cls=cls,
                         level=rec.get("level"), stratum=stratum, shadow=shadow,
                         via=rec.get("via"), path=os.path.relpath(p, ROOT).replace("\\", "/"),
                         budget=d["budget"], tau=d["tau"], converged=bool(d.get("converged")),
                         n_box=len(d["hyp"]["boxes"]), lp_time_orig=d.get("time"),
                         I_U3_d0=r.get("I_U3_d0"), viol_U3_d0=r.get("viol_U3_d0")))
        return True

    # --- shadow-explained strata (A57 only; levels 1-2; balanced over class and support kind)
    for sid, want in WANT.items():
        cands = [r for r in sn[sid]
                 if r["src"] == "A57" and r.get("level") in (1, 2) and L.cls_of(r["nid"])]
        rnd.shuffle(cands)
        # prefer a spread: alternate class and via
        buckets = {}
        for r in cands:
            buckets.setdefault((L.cls_of(r["nid"]), r.get("via"), r.get("level")), []).append(r)
        keys = sorted(buckets)
        n = 0
        while n < want and any(buckets[k] for k in keys):
            for k in keys:
                if n >= want:
                    break
                if buckets[k] and add(buckets[k].pop(), "shadow:" + sid, sid):
                    n += 1

    # --- controls: unexplained / fractional-support nodes
    cands = [r for r in unexp if r["src"] == "A57" and r.get("level") in (1, 2)
             and L.cls_of(r["nid"])]
    rnd.shuffle(cands)
    n = 0
    for r in cands:
        if n >= N_CONTROL:
            break
        if add(r, "control:unexplained"):
            n += 1

    json.dump(plan, open(os.path.join(L.RES, "t2_plan.json"), "w"), indent=1)
    print("plan: %d nodes" % len(plan))
    print(Counter(p["stratum"] for p in plan))
    print(Counter((p["cls"], p["level"]) for p in plan))
    print(Counter(p["n_box"] for p in plan), "boxes per node")


if __name__ == "__main__":
    main()
