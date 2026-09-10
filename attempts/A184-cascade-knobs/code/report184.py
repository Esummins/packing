"""A184 -- results/knobs184.json: every number of the three experiments from the side files, plus
the per-cell projection (S1..S4 populations x per-node time) for the eleven k0 cells.

    python report184.py
"""
import json
import os
from collections import Counter

import common184 as C
from common184 import CS
import run184 as RU

OUT = os.path.join(C.RES, "knobs184.json")


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def mean_kept(rs):
    names = sorted({k for r in rs for k in (r.get("kept") or {})})
    return {n: round(mean([r["kept"][n] for r in rs if r.get("kept") and n in r["kept"]]), 4) for n in names}


def step_stats(rs):
    alive = [r for r in rs if r["verdict"].startswith("ALIVE")]
    leaves = Counter((r.get("leaf") or "alive") for r in rs)
    died_83 = sum(1 for r in rs if r.get("died_at") == "8/3")
    return dict(n=len(rs), alive=len(alive), dead_by=dict(leaves), died_at_83=died_83,
                mean_kept=mean_kept(alive), mean_vol1={k: round(v, 5) for k, v in (mean_vols(alive) or {}).items()},
                wall_total=round(sum(r.get("t_total") or 0 for r in rs), 1),
                wall_mean=round(mean([r.get("t_total") for r in rs if r.get("t_total") is not None]) or 0, 1),
                wall_mean_alive=round(mean([r.get("t_total") for r in alive]) or 0, 1),
                clip42_mean=round(mean([r.get("t_clip42") for r in rs if r.get("t_clip42") is not None]) or 0, 1),
                clip83_mean=round(mean([r.get("t_clip83") for r in rs if r.get("t_clip83") is not None]) or 0, 1),
                rest_mean=round(mean([(r.get("t_rest42") or 0) + (r.get("t_rest83") or 0) for r in rs if r.get("t_clip42") is not None]) or 0, 1))


def mean_vols(rs):
    names = sorted({k for r in rs for k in (r.get("vol1") or {})})
    return {n: mean([r["vol1"][n] for r in rs if r.get("vol1") and n in r["vol1"]]) for n in names}


def by(recs, exp, step):
    return [r for r in recs.values() if r.get("exp") == exp and r.get("step") == step]


def compare(recs, e1, e2, step):
    """verdict agreement node by node (same hypothesis, different setting / order)."""
    a = {k.split("|", 1)[1]: r for k, r in recs.items() if r.get("exp") == e1 and r.get("step") == step}
    b = {k.split("|", 1)[1]: r for k, r in recs.items() if r.get("exp") == e2 and r.get("step") == step}
    both = sorted(set(a) & set(b))
    cnt = Counter((a[k]["verdict"].split("(")[0], b[k]["verdict"].split("(")[0]) for k in both)
    diff = [dict(node=k, first=a[k]["verdict"][:60], second=b[k]["verdict"][:60]) for k in both
            if a[k]["verdict"].startswith("ALIVE") != b[k]["verdict"].startswith("ALIVE")]
    ratio = {}
    for k in both:
        if a[k].get("vol1") and b[k].get("vol1"):
            for n in a[k]["vol1"]:
                if n in b[k]["vol1"] and a[k]["vol1"][n] > 0:
                    ratio.setdefault(n, []).append(b[k]["vol1"][n] / a[k]["vol1"][n])
    return dict(n_both=len(both), verdict_pairs={"%s/%s" % p: c for p, c in cnt.items()}, differing=diff,
                vol1_ratio_second_over_first={n: round(mean(v), 4) for n, v in ratio.items()})


def e3_stats(waste, recs):
    out = {}
    for step in ("S1", "S2", "HDB", "S3"):
        ws = [w for k, w in waste.items() if (recs.get(k) or {}).get("step") == step or (step == "S1" and k.startswith("S1|"))]
        if not ws:
            continue
        out[step] = dict(n=len(ws), area_U_mean=round(mean([w["area_U"] for w in ws]), 4), area_U_max=round(max(w["area_U"] for w in ws), 4),
                         area_U_b_mean=round(mean([w["area_U_b"] for w in ws]), 4), ratio_B0_max=round(max(w["ratio_B0"] for w in ws), 4),
                         kills=sum(1 for w in ws if w["kill"]),
                         corner={c: dict(n=sum(1 for w in ws if c in w["corner"]),
                                         area_mean=round(mean([w["corner"][c]["area"] for w in ws if c in w["corner"]]) or 0, 5),
                                         naive_mean=round(mean([w["corner"][c]["naive_area"] for w in ws if c in w["corner"]]) or 0, 4),
                                         naive_max=round(max([w["corner"][c]["naive_area"] for w in ws if c in w["corner"]] or [0]), 4))
                                 for c in ("TR", "BR")},
                         east_strip_share=round(mean([w["by_region"]["strip_E"]["area_U"] / w["area_U_b"] for w in ws if w["area_U_b"] > 0]) or 0, 3),
                         sample_hits=sum(w["sample"]["free"]["hits"] for w in ws),
                         seconds_mean=round(mean([w["seconds"] for w in ws]), 1))
    return out


def projection(recs, T):
    """populations per step on l1_104 (the record) x the measured per-node wall, both settings, x 11 cells."""
    nodes = T["nodes"]
    pop = {}
    for st in ("S1", "S2", "S3"):
        ns = [n for n in nodes.values() if n.get("step") == st]
        pop[st] = dict(boxes=len(ns), a168_alive=sum(1 for n in ns if n["verdict"].startswith("ALIVE")))
    pop["S1"]["a183_alive"], pop["S2"]["a183_alive"] = 28, 64
    fan_s2 = pop["S2"]["a168_alive"] / max(1, pop["S1"]["a168_alive"])
    s3_alive = {}
    for e in ("c", "f"):
        s = step_stats(by(recs, e, "S3"))
        s3_alive[e] = (s["alive"] / s["n"]) if s["n"] else None
    out = dict(populations=pop, fan_S2_alive_per_alive_S1=round(fan_s2, 2),
               rule="S4 population = alive S3 x (S2 fan-out per alive S1 parent) [estimate]; per-node wall = the sample's mean; x 11 cells")
    for e, label in (("c", "coarse_only"), ("f", "a183_4/2_then_8/3")):
        t = {st: step_stats(by(recs, e, st))["wall_mean"] for st in ("S2", "S3")}
        t["S1"] = mean([r.get("t_total") for k, r in recs.items() if k.startswith("S1|%s|" % ("42" if e == "c" else "83"))]) or 0
        n1, n2 = pop["S1"]["a168_alive"] + 0, pop["S2"]["a168_alive"]
        n3 = pop["S3"]["a168_alive"]
        alive3 = int(round(n3 * (s3_alive[e] or 0)))
        n4 = int(round(alive3 * fan_s2))
        t4 = t["S3"] * 1.3
        cell_h = (n1 * t["S1"] + n2 * t["S2"] + n3 * t["S3"] + n4 * t4) / 3600
        out[label] = dict(t_node=dict(S1=round(t["S1"], 1), S2=round(t["S2"], 1), S3=round(t["S3"], 1), S4_est=round(t4, 1)),
                          n_nodes=dict(S1=n1, S2=n2, S3=n3, S4_est=n4), s3_alive_frac=s3_alive[e],
                          cpu_h_per_cell=round(cell_h, 1), cpu_h_11_cells=round(11 * cell_h, 1))
    return out


def main():
    recs = RU.load_all(2)
    waste = C.load_jsonl(os.path.join(C.RES, "waste184.jsonl"))
    lp = C.load_jsonl(os.path.join(C.RES, "lp184.jsonl"))
    S = C.jload(RU.SAMPLE)
    T = CS.load_tree(C.CELL)
    K_ = dict(sample=dict(chains={c: dict(S=[s["node"] for s in e["S"]], B=[b["idx"] for b in e["B"]],
                                          cover_HD={k: v for k, v in (e.get("cover_HD") or {}).items() if k not in ("open_boxes", "lonely_idx")},
                                          cover_HDS_tree=e.get("cover_HDS_tree")) for c, e in S["chains"].items()},
                          s1={k: dict(verdict=r["verdict"][:30], kept=r.get("kept"), t_total=r.get("t_total"), t_clip42=r.get("t_clip42"),
                                      t_clip83=r.get("t_clip83")) for k, r in recs.items() if k.startswith("S1|")}))
    K_["E1"] = {e: {st: step_stats(by(recs, e, st)) for st in ("S2", "S3")} for e in ("c", "f")}
    K_["E1"]["compare"] = {st: compare(recs, "c", "f", st) for st in ("S2", "S3")}
    K_["E2"] = {"c": {st: step_stats(by(recs, "c", st)) for st in ("S2", "S3")},
                "b": {st: step_stats(by(recs, "b", st)) for st in ("HDB", "S3")}}
    K_["E2"]["compare_S3"] = compare(recs, "c", "b", "S3")
    for e, inter in (("c", "S2"), ("b", "HDB")):
        w_i = [waste[k]["area_U"] for k, r in recs.items() if r.get("exp") == e and r.get("step") == inter and k in waste]
        w_f = [waste[k]["area_U"] for k, r in recs.items() if r.get("exp") == e and r.get("step") == "S3" and k in waste]
        K_["E2"][e]["stranded_U"] = dict(after_step2_mean=round(mean(w_i) or 0, 4), after_step3_mean=round(mean(w_f) or 0, 4),
                                          n=[len(w_i), len(w_f)])
        K_["E2"][e]["wall_total_both_steps"] = round(K_["E2"][e][inter]["wall_total"] + K_["E2"][e]["S3"]["wall_total"], 1)
    K_["E3"] = dict(summary=e3_stats(waste, recs), B0=C.B0,
                    lp={k: dict(budget=v["budget"], area_U=v["area_U"], forms={f: {kk: vv for kk, vv in d.items() if kk in (
                        "tau", "eta", "converged", "kills", "kills_converged", "certified", "verdict", "wall_s", "n_nofams", "n_rows")}
                        for f, d in v["forms"].items()}) for k, v in lp.items()})
    if lp:
        forms = sorted({f for v in lp.values() for f in v["forms"]})
        K_["E3"]["lp_summary"] = {f: dict(n=sum(1 for v in lp.values() if f in v["forms"]),
                                          tau_mean=round(mean([v["forms"][f].get("tau") for v in lp.values() if f in v["forms"]]) or 0, 5),
                                          kills=sum(1 for v in lp.values() if f in v["forms"] and v["forms"][f].get("kills")),
                                          converged=sum(1 for v in lp.values() if f in v["forms"] and v["forms"][f].get("converged")),
                                          wall_mean=round(mean([v["forms"][f].get("wall_s") for v in lp.values() if f in v["forms"]]) or 0, 1))
                                  for f in forms}
    K_["projection"] = projection(recs, T)
    K_["wallcapped"] = sorted(C.wallcapped())
    C.jdump(K_, OUT)
    print(json.dumps({k: K_[k] for k in ("E1", "E2", "projection")}, indent=1, default=str)[:6000])
    print("E3", json.dumps(K_["E3"].get("summary"), default=str)[:1500], K_["E3"].get("lp_summary"))


if __name__ == "__main__":
    main()
