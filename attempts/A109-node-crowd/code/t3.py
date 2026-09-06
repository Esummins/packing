"""A109 T3 -- price, schedule effect, and composition with the parametric route.

Inputs (all measured elsewhere and quoted with their source):
  * A57/A96 remaining schedule, LOG.md 2026-09-05 (A96 core96 accounting):
    66.53 CPU-days = 13.31 wall-days at 5 workers; open boxes 1096/389/39/12 at levels 1/2/3/4;
    the tight-core pre-filter's per-level CPU-days (0.29 / 2.71 / 5.80 / 22.59 for 20/32/7/11
    killed nodes) give the DIRECT cost of one node at each level.
  * A57's own measured per-node wall: k5_11 interior level 1, 594 nodes in 95.9 h = 581 s/node
    (block96.md sec 3); A96's parametric comparator 264.6 s/node.
  * A109's own measured crowd re-solve cost (results/t2_runs_s*.jsonl) and certification wall
    (results/t2_certs.jsonl).
"""
import glob, json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a109lib as L

OPEN = {1: 1096, 2: 389, 3: 39, 4: 12}
DIRECT_CPU_D = {1: 0.29 / 20, 2: 2.71 / 32, 3: 5.80 / 7, 4: 22.59 / 11}
SCHED_CPU_D = 66.53
WORKERS = 5
A57_S_PER_NODE_L1 = 581.0


def load_best():
    best = {}
    for p in glob.glob(os.path.join(L.RES, "t2_runs_s*.jsonl")):
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("error"):
                continue
            k = (r["nid"], r["cfg"])
            b = best.get(k)
            if b is None or (r.get("eta") is not None and
                             (b.get("eta") is None or r["eta"] < b["eta"])):
                best[k] = r
    return best


def main():
    plan = {p["nid"]: p for p in json.load(open(os.path.join(L.RES, "t2_plan.json")))}
    best = load_best()
    cfgs = sorted({k[1] for k in best}, key=lambda c: ("sound", "d0.05", "d0.1", "d0.3").index(c)
                  if c in ("sound", "d0.05", "d0.1", "d0.3") else 9)
    out = dict(cfgs={}, price={}, schedule={})

    # --- kill rates per cfg per level (ATTRIBUTABLE: eta0 >= 0 and eta < 0)
    for cfg in cfgs:
        per_lvl = defaultdict(lambda: [0, 0])
        etas, cs, lps, Bs = [], [], [], []
        for (nid, c), r in best.items():
            if c != cfg or r.get("tau") is None:
                continue
            lvl = plan[nid]["level"]
            if r["eta0"] >= -1e-9:
                per_lvl[lvl][1] += 1
                if r["eta"] < -1e-6:
                    per_lvl[lvl][0] += 1
            etas.append(r["eta"])
            if r.get("c_dtau_de") is not None:
                cs.append(r["c_dtau_de"])
            if r.get("lp_s"):
                lps.append(r["lp_s"])
            Bs.append(r["B"])
        n = sum(v[1] for v in per_lvl.values())
        k = sum(v[0] for v in per_lvl.values())
        out["cfgs"][cfg] = dict(
            n=n, dead=k, rate=(k / n if n else None),
            by_level={str(l): dict(dead=v[0], n=v[1]) for l, v in sorted(per_lvl.items())},
            mean_eta=(sum(etas) / len(etas)) if etas else None,
            mean_c=(sum(cs) / len(cs)) if cs else None,
            mean_B=(sum(Bs) / len(Bs)) if Bs else None,
            mean_lp_s=(sum(lps) / len(lps)) if lps else None,
            median_lp_s=(sorted(lps)[len(lps) // 2] if lps else None))

    # --- price
    orig = [plan[n]["lp_time_orig"] for n in plan if plan[n].get("lp_time_orig")]
    all_lp = [r["lp_s"] for r in best.values() if r.get("lp_s")]
    certs = []
    cp = os.path.join(L.RES, "t2_certs.jsonl")
    if os.path.exists(cp):
        certs = [json.loads(l) for l in open(cp) if l.strip()]
    out["price"] = dict(
        crowd_resolve_mean_s=(sum(all_lp) / len(all_lp)) if all_lp else None,
        crowd_resolve_median_s=(sorted(all_lp)[len(all_lp) // 2] if all_lp else None),
        crowd_resolve_max_s=(max(all_lp) if all_lp else None),
        node_original_lp_mean_s=(sum(orig) / len(orig)) if orig else None,
        node_original_lp_median_s=(sorted(orig)[len(orig) // 2] if orig else None),
        a57_measured_s_per_node_L1=A57_S_PER_NODE_L1,
        cert_wall_s=[c.get("cert_s") for c in certs],
        cert_results=[c.get("result") for c in certs])

    # --- schedule
    for cfg in cfgs:
        e = out["cfgs"][cfg]
        rate = e["rate"]
        if rate is None:
            continue
        # (a) a re-solve on ALIVE nodes only: pay one crowd LP per open box, harvest the direct
        #     cost of the killed ones plus (for a killed level-1/2 box) its whole subtree.
        cost_cpu_d = sum(OPEN.values()) * (e["mean_lp_s"] or 0) / 86400.0
        direct = sum(OPEN[l] * DIRECT_CPU_D[l] for l in OPEN) * rate
        # the subtree share: levels 1 and 2 are the roots of everything below them, so killing a
        # fraction `rate` of them removes (to first order) that fraction of the WHOLE remainder.
        whole = SCHED_CPU_D * rate
        out["schedule"][cfg] = dict(
            kill_rate=rate,
            route_a_cost_cpu_d=cost_cpu_d,
            route_a_gain_direct_cpu_d=direct,
            route_a_gain_with_subtrees_cpu_d=whole,
            route_a_net_wall_d_5w=(whole - cost_cpu_d) / WORKERS,
            route_b_extra_cpu_d=sum(OPEN.values()) * (e["mean_lp_s"] or 0) / 86400.0,
            note=("rows in every node LP costs at least the same per node and raises tau, so it "
                  "is never cheaper than (a) at the same kill rate"))
    json.dump(out, open(os.path.join(L.RES, "t3.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
