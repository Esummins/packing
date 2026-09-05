"""A100 projection: measured per-class cost -> protected-tier price -> all-layers total.

Cost model for one protected class on the A96 pipeline.  Every coefficient marked [m] is measured
by this attempt on k4_11 and/or k3_02; [M] is a model input carried over from A84 or A96.

    C(S) = cells * w_node                                   [m]  level-1 (K) emission at s0
         + cells * f1 * w_param                             [m]  parametric verify over W
         + cells * f1 * g * w_resolve                       [m]  resolver on the partials
         + cells * (1-f1) * 2 * w_child                     [m]  ONE round of level-2, delta=1e-2
         + D_cost                                           [m]  (D) leaves: ladder + tube (~0)

  cells    attemptable level-1 cells (exact census)
  w_node   per-node cover wall with the eta-gate on (skip certify + eps_geo when eta = 0)
  f1       first-pass certification rate = fraction of cells with eta < 0 (exact law, 54/54)
  w_param  parametric wall per certified leaf
  g        fraction of certified leaves that come back as a completed partial
  w_child  per-child wall of the level-2 descent

The level-2 term is ONE round and does NOT close (measured kill yield 1/16).  It is reported
separately from the three terms that do close.
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
H = 3600.0

# ---- tier composition (results/tier84_classes.json) --------------------------------------------
TIER = dict(k4=["k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "k4_13"],
            k3=["k3_01", "k3_02", "k3_03", "k3_04", "k3_05"],
            k2=["k2_00", "k2_01", "k2_02"], k1=["k1_00"], k0=["k0_00"])
# measured level-1 attemptable cells; the rest are the group mean / the no-pin bound
CELLS = dict(k4_08=752, k4_11=882, k3_02=780, k3_05=984)
CELLS_MODEL = dict(k4=817, k3=882, k2=1000, k1=1100, k0=1152)
BUDGET = dict(k4=6, k3=7, k2=8, k1=9, k0=10)


def cls_terms(cls, rep):
    R = rep["classes"][cls]
    cells = R["L1_cells"]["attemptable"]
    P = json.load(open(os.path.join(BASE, "progress", "%s_cover_j0_s0.json" % cls)))
    cov = [json.loads(l) for l in open(os.path.join(RES, "a84_%s_cover_j0.jsonl" % cls))]
    byt = {}
    for r in cov:
        byt[r["tag"]] = r
    eg = sum(sum(s["seconds"] for s in r["eps_geo"]) for r in byt.values() if r.get("eps_geo"))
    w_node_asrun = P["elapsed_s"] / P["done"]
    w_node = (P["elapsed_s"] - eg) / P["done"]          # eta-gated forward price
    f1 = R["L3_rates"]["first_pass_rate"]
    L4 = R["L4_parametric"]
    nver = L4["n"] - L4["emit_error"]
    w_param = L4["wall_s"]["mean"] * L4["n"] / nver
    g = (L4["partial_fail"] + L4["timeout"]) / nver
    L5 = R["L5_resolver"]
    w_resolve = L5["wall_s"]["mean"]
    D = json.load(open(os.path.join(BASE, "progress",
                                    "%s_deepen_j0_r1_s0.json" % cls)))
    w_child = D["elapsed_s"] / D["done"]
    lvl2_kill = R["L6_level2"]["kill_rate"]
    t = dict(cls=cls, cells=cells, budget=R["L1_cells"]["child_budget"],
             sample=P["done"], fraction_done=round(P["done"] / cells, 4),
             w_node_asrun_s=round(w_node_asrun, 1), w_node_eta_gated_s=round(w_node, 1),
             eps_geo_waste_s=round(eg, 1), eps_geo_share=round(eg / P["elapsed_s"], 3),
             f1_first_pass=f1, w_param_s=round(w_param, 1), partial_frac=round(g, 3),
             w_resolve_s=w_resolve, resolver_closure=L5["closure_rate"],
             w_child_s=round(w_child, 1), level2_kill_rate=lvl2_kill,
             D_leaves=R["L7_D_leaves"]["D_leaves"],
             ladder_K_queue=R["L7_D_leaves"]["K_kill_queue"])
    t["level1_cpu_h"] = round(cells * w_node / H, 1)
    t["param_cpu_h"] = round(cells * f1 * w_param / H, 1)
    t["resolve_cpu_h"] = round(cells * f1 * g * w_resolve / H, 1)
    t["closing_cpu_h"] = round(t["level1_cpu_h"] + t["param_cpu_h"] + t["resolve_cpu_h"], 1)
    t["level2_round1_cpu_h"] = round(cells * (1 - f1) * 2 * w_child / H, 1)
    t["total_measured_cpu_h"] = round(t["closing_cpu_h"] + t["level2_round1_cpu_h"], 1)
    return t


def scale(base, cells, budget_steps, f1=None):
    """re-price a measured class for another class: cells scale linearly, the per-node and
    per-child walls by the MEASURED per-budget-step multiplier, f1 overridable."""
    mult = 1.149 ** budget_steps          # measured: 388.5 s (budget 7) / 338.0 s (budget 6)
    f = base["f1_first_pass"] if f1 is None else f1
    l1 = cells * base["w_node_eta_gated_s"] * mult / H
    pa = cells * f * base["w_param_s"] * mult / H
    rs = cells * f * base["partial_frac"] * base["w_resolve_s"] / H
    l2 = cells * (1 - f) * 2 * base["w_child_s"] * mult / H
    return dict(cells=cells, f1=round(f, 3), budget_steps=budget_steps,
                closing_cpu_h=round(l1 + pa + rs, 1), level2_round1_cpu_h=round(l2, 1),
                total_cpu_h=round(l1 + pa + rs + l2, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=os.path.join(RES, "a100_report.json"))
    ap.add_argument("--out", default=os.path.join(RES, "a100_projection.json"))
    a = ap.parse_args()
    rep = json.load(open(a.report))
    k4 = cls_terms("k4_11", rep)
    k3 = cls_terms("k3_02", rep)

    # ---- tier -------------------------------------------------------------------------------
    # k4: the measured spread in f1 is the whole uncertainty (k4_11 0.385 vs A84's k4_08 0.81).
    k4_lo = scale(k4, CELLS_MODEL["k4"], 0, f1=0.81)
    k4_hi = scale(k4, CELLS_MODEL["k4"], 0, f1=k4["f1_first_pass"])
    k3_each = scale(k3, CELLS_MODEL["k3"], 0)
    k2_each = scale(k3, CELLS_MODEL["k2"], 1)
    k1_each = scale(k3, CELLS_MODEL["k1"], 2)
    tier = dict(
        k4=dict(n=6, per_class_cpu_h=[k4_lo["total_cpu_h"], k4_hi["total_cpu_h"]],
                group_cpu_h=[round(6 * k4_lo["total_cpu_h"]), round(6 * k4_hi["total_cpu_h"])],
                detail=dict(at_f1_0_81=k4_lo, at_f1_measured=k4_hi)),
        k3=dict(n=5, per_class_cpu_h=k3_each["total_cpu_h"],
                group_cpu_h=round(5 * k3_each["total_cpu_h"]), detail=k3_each),
        k2=dict(n=3, per_class_cpu_h=k2_each["total_cpu_h"],
                group_cpu_h=round(3 * k2_each["total_cpu_h"]), detail=k2_each, note="model"),
        k1=dict(n=1, per_class_cpu_h=k1_each["total_cpu_h"],
                group_cpu_h=round(k1_each["total_cpu_h"]), detail=k1_each, note="model"),
        k0=dict(n=1, note="out of scope here -- priced by A85/A99 as its own block"))
    lo = (tier["k4"]["group_cpu_h"][0] + tier["k3"]["group_cpu_h"] + tier["k2"]["group_cpu_h"]
          + tier["k1"]["group_cpu_h"])
    hi = (tier["k4"]["group_cpu_h"][1] + tier["k3"]["group_cpu_h"] + tier["k2"]["group_cpu_h"]
          + tier["k1"]["group_cpu_h"])
    tier["protected_tier_15_classes_cpu_h"] = [round(lo), round(hi)]
    tier["a84_model_for_comparison_cpu_h"] = [800 + 1000]

    # ---- all layers -------------------------------------------------------------------------
    allL = dict(
        k_ge_6=dict(cpu_h=[0, 0], source="done (A54/A61)"),
        k5_11_k5_16=dict(cpu_h=[1680, 1925], source="A96 LANDED 2026-09-04 (residue_map: 80 "
                         "CPU-days = 1925 CPU-h; honest range 14-16 wall-days at 5 workers)"),
        trump5_A60=dict(cpu_h=[300, 500], source="residue_map (running)"),
        stragglers_A61=dict(cpu_h=[20, 60], source="residue_map (small)"),
        protected_k4=dict(cpu_h=tier["k4"]["group_cpu_h"], source="A100 MEASURED (k4_11)"),
        protected_k3_k2_k1=dict(cpu_h=[round(tier["k3"]["group_cpu_h"]
                                             + tier["k2"]["group_cpu_h"]
                                             + tier["k1"]["group_cpu_h"])] * 2,
                                source="A100 MEASURED (k3_02) + budget scaling"),
        k0_00=dict(cpu_h=[400, 7000], source="A85 model 3200-7000 -> 400-700 if A99's three "
                   "reductions land; A99 still running"))
    tlo = sum(v["cpu_h"][0] for v in allL.values())
    thi = sum(v["cpu_h"][1] for v in allL.values())
    allL["ALL_LAYERS_TOTAL_cpu_h"] = [round(tlo), round(thi)]
    allL["pi_budget_target_cpu_h"] = 400

    # ---- sensitivity: the level-2 per-child wall is the weakest coefficient (16 children) -----
    pooled = ((k4["w_child_s"] * rep["classes"]["k4_11"]["L6_level2"]["children"]
               + k3["w_child_s"] * rep["classes"]["k3_02"]["L6_level2"]["children"])
              / (rep["classes"]["k4_11"]["L6_level2"]["children"]
                 + rep["classes"]["k3_02"]["L6_level2"]["children"]))
    sens = {}
    for name, wc in (("low_k4_11_355s", k4["w_child_s"]), ("pooled_%.0fs" % pooled, pooled),
                     ("high_k3_02_1377s", k3["w_child_s"])):
        b4 = dict(k4); b4["w_child_s"] = wc
        b3 = dict(k3); b3["w_child_s"] = wc
        s4lo = scale(b4, CELLS_MODEL["k4"], 0, f1=0.81)["total_cpu_h"]
        s4hi = scale(b4, CELLS_MODEL["k4"], 0, f1=b4["f1_first_pass"])["total_cpu_h"]
        s3 = scale(b3, CELLS_MODEL["k3"], 0)["total_cpu_h"]
        s2 = scale(b3, CELLS_MODEL["k2"], 1)["total_cpu_h"]
        s1 = scale(b3, CELLS_MODEL["k1"], 2)["total_cpu_h"]
        sens[name] = dict(per_k4=[round(s4lo), round(s4hi)], per_k3=round(s3),
                          per_k2=round(s2), per_k1=round(s1),
                          tier_15_cpu_h=[round(6 * s4lo + 5 * s3 + 3 * s2 + s1),
                                         round(6 * s4hi + 5 * s3 + 3 * s2 + s1)])
    tier["level2_child_wall_sensitivity"] = sens
    pk = [k for k in sens if k.startswith("pooled")][0]
    tier["HEADLINE_pooled_child_wall"] = sens[pk]
    tier["headline_note"] = ("the pooled level-2 child wall (%s) is the central case; the low/high "
                             "rows are the two classes' own measured child walls, and the spread "
                             "is the weakest coefficient in the whole projection (16 children)"
                             % pk)
    # all-layers headline uses the pooled tier, not the k3_02-only one
    allL["protected_k4"]["cpu_h"] = [round(6 * sens[pk]["per_k4"][0]),
                                     round(6 * sens[pk]["per_k4"][1])]
    allL["protected_k3_k2_k1"]["cpu_h"] = [round(5 * sens[pk]["per_k3"] + 3 * sens[pk]["per_k2"]
                                                 + sens[pk]["per_k1"])] * 2
    allL["ALL_LAYERS_TOTAL_cpu_h"] = [
        round(sum(v["cpu_h"][0] for k, v in allL.items() if isinstance(v, dict) and "cpu_h" in v)),
        round(sum(v["cpu_h"][1] for k, v in allL.items() if isinstance(v, dict) and "cpu_h" in v))]

    out = dict(attempt="A100-protected-pilot", per_class=dict(k4_11=k4, k3_02=k3),
               tier=tier, all_layers=allL)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
