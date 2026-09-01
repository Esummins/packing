#!/usr/bin/env python3
"""
close_a56.py -- A56 T2 close-out.  Folds pass-3 results into results/scoreboard.json (every row
carrying its exact status and s-range) and rewrites results/stage1_pricing.json with the
CORRECTED cost law and both repair recipes priced.  No compute.
"""
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                              # noqa: E402

S0, S_LO = SW.S0, SW.S_LO
FULL = [str(S_LO), str(S0)]


def main():
    sb_path = os.path.join(SW.RESULTS, "scoreboard.json")
    sb = json.load(open(sb_path))
    rows = sb["rows"]
    spent = float(sb.get("cumulative_verifier_time_s", 0))

    # ---- certificates repaired by re-solving with a robustness margin (every resolve_*.json)
    import glob
    inv = {c["name"]: c for c in SW.load_inventory()["certs"]}
    seen_resolve = json.load(open(os.path.join(SW.RESULTS, "resolve_accounted.json"))) \
        if os.path.exists(os.path.join(SW.RESULTS, "resolve_accounted.json")) else {}
    for p in sorted(glob.glob(os.path.join(SW.RESULTS, "resolve_*.json"))):
        n = os.path.basename(p)[len("resolve_"):-len(".json")]
        if n not in rows:
            continue
        d = json.load(open(p))
        key = str(round(float(d.get("total_seconds") or d.get("lp_seconds") or 0), 1))
        cost = float(d.get("lp_seconds") or 0) + float(d.get("certify_seconds") or 0) \
            + float(d.get("param_seconds") or 0)
        if seen_resolve.get(n) != key:                  # count each resolve run's cost once
            spent += cost
            seen_resolve[n] = key
        r = rows[n]
        r["resolve"] = {k: d.get(k) for k in
                        ("verdict", "eps_geo", "tau", "budget", "converged", "lp_seconds",
                         "certify_seconds", "param_seconds", "total_seconds", "new_cert",
                         "n_4d_witnesses", "param_stats")}
        if d.get("verdict") == "RECIPE CONVERTS":
            r["result"] = "TRANSFERRED-resolved"
            r["s_ranges"] = [FULL]
            r["s_ranges_float"] = [[float(S_LO), float(S0)]]
            r["window_coverage"] = 1.0
            r["open_band"] = []
            r["c2"] = d.get("c2")
            # ledger rule (A56 advisor ruling): the composed claim is PER-STRATUM and any
            # exactly-verified certificate family is fungible, so substitution is acceptable --
            # provided BOTH certificates stay referenced with their provenance.
            r["certs"] = {
                "original_s0_cert": inv[n]["path"],
                "original_status": "verified at s = s0 only (A53/A54); still the s0 witness",
                "parametric_base_cert": os.path.join(SW.CERTS, "resolved", f"{n}.json"),
                "parametric_cert": os.path.join(SW.CERTS, "resolved", f"{n}.param.json"),
                "parametric_status": (f"re-solved at s0 with eps_geo={d.get('eps_geo')}, then "
                                      "verified over the whole window by verify_param + C2"),
                "carries_the_window_claim": os.path.join(SW.CERTS, "resolved",
                                                         f"{n}.param.json"),
            }
            r["base_cert"] = os.path.join(SW.CERTS, "resolved", f"{n}.json")
            r["note"] = ("TRANSFERRED via a RE-SOLVED base certificate (A56 resolve_margin, "
                         f"eps_geo={d.get('eps_geo')}). Certificate substitution, permitted by "
                         "the A56 ledger rule: the composed claim is per-stratum and any "
                         "exactly-verified certificate family is fungible. Both certificates are "
                         "referenced in .certs; the original A53/A54 certificate remains the "
                         "s0-only witness and is unmodified.")
        else:
            r["resolve_failed_because"] = d.get("verdict")
            r["note"] = ((r.get("note", "") + " ") if r.get("note") else "") + \
                (f"resolve_margin at eps_geo={d.get('eps_geo')}: {d.get('verdict')}"
                 + (f" (tau {d.get('tau')} vs budget {d.get('budget')})"
                    if d.get("tau") is not None else "")).strip()

    # ---- normalise every row's s-range bookkeeping
    for n, r in rows.items():
        if r["result"] != "TRANSFERRED-resolved":
            r.setdefault("certs", {
                "original_s0_cert": inv[n]["path"],
                "parametric_cert": os.path.join(SW.CERTS, f"{n}.param.json"),
                "carries_the_window_claim": (os.path.join(SW.CERTS, f"{n}.param.json")
                                             if r["result"] in ("TRANSFERRED", "partial")
                                             else None),
                "note": ("the parametric certificate is the SAME measure as the A53/A54 one, "
                         "re-expressed with s-affine atom and core positions (C1 identity)"),
            })
        if r["result"] == "TRANSFERRED":
            r.setdefault("s_ranges", [FULL])
            r.setdefault("window_coverage", 1.0)
            r.setdefault("open_band", [])
            r["status"] = f"FULL [{S_LO}, {S0}]"
        elif r["result"] == "TRANSFERRED-resolved":
            r["status"] = f"FULL [{S_LO}, {S0}] (re-solved base certificate)"
        elif r["result"] == "M1":
            r["s_ranges"] = [FULL]
            r["window_coverage"] = 1.0
            r["open_band"] = []
            r["status"] = (f"FULL [{S_LO}, {S0}] by soundness.md M1 (single-corner transfer "
                           "theorem; no computation)")
        elif r["result"] == "partial":
            if n == "k6_23":
                r["s_ranges"] = [[str(S_LO), "3877/1000"]]
                r["s_ranges_float"] = [[float(S_LO), 3.877]]
                r["window_coverage"] = round((3.877 - float(S_LO)) / float(S0 - S_LO), 6)
                r["open_band"] = [["3877/1000", str(S0)]]
                r["status"] = ("PARTIAL: parametric PASS on [191/50, 3877/1000]; the A54 fixed-s "
                               "certificate holds AT s0 = 969271/250000 itself; open = the OPEN "
                               "interval (3877/1000, 969271/250000), width 84/1000000 = 8.4e-5")
            else:
                r["status"] = ("PARTIAL: " + ", ".join(f"[{a}, {b}]" for a, b in r["s_ranges"])
                               + "; open " + ", ".join(f"[{a}, {b}]" for a, b in r["open_band"]))
        else:
            rep = r.get("param_report")
            wr = None
            if rep and os.path.exists(rep):
                wr = json.load(open(rep)).get("witness_s_range")
            r["s_ranges"] = []
            r["window_coverage"] = 0.0
            r["open_band"] = [FULL]
            r["status"] = ("OPEN over the whole window; recorded FAIL-witness s-range "
                           + (f"[{wr[0]:.7f}, {wr[1]:.7f}]" if wr else "unavailable")
                           + " (TRUNCATED at the per-box witness cap unless the witness count is "
                             "not a multiple of 8 -- see stage1_pricing.json)")

    json.dump(seen_resolve, open(os.path.join(SW.RESULTS, "resolve_accounted.json"), "w"),
              indent=1)
    sb["cumulative_verifier_time_s"] = round(spent, 1)
    sb["summary"] = SW.summarize(rows)
    sb["legend"] = {
        "TRANSFERRED": "4D PASS over the whole window on the ORIGINAL A53/A54 certificate + C2",
        "TRANSFERRED-resolved": "same, on a re-solved base certificate (A56 resolve_margin)",
        "M1": "single-corner: transferred by the soundness.md M1 theorem, no computation",
        "partial": "4D PASS on the listed sub-window(s), each with its own C2",
        "OPEN": "no parametric PASS; every witness is depth-limited, never a hole",
        "TIMEOUT": "the 4D run was capped before it could decide",
    }
    SW.checkpoint(sb_path, sb)

    # ---- corrected cost law
    p = json.load(open(os.path.join(SW.RESULTS, "stage1_pricing.json")))
    p["corrected_cost_law"] = {
        "headline": ("t_4D ~= 261 us x (number of s-splits), Spearman 0.978 on the 21 PASSes. "
                     "The s-subdivision count is the cost; neither the LP margin (rho -0.35) nor "
                     "the atom count (rho +0.45) predicts it."),
        "artifact_1_witness_capped_FAIL_times": (
            "A FAIL time is NOT a cost measurement. verify_param stops a root box after "
            "--max-witnesses-per-box (8) witnesses, so a FAIL reports whatever the DFS reached "
            "first and exits. k6_32 'FAILs in 0.7 s' at depth 48 and then runs >900 s at depth 56 "
            "and >600 s at depth 60 without finishing. Only PASS times are true costs."),
        "artifact_2_witness_s_ranges_do_not_localise": (
            "For the same reason the recorded witness_s_range is a sample, not the failing set. "
            "A witness s-range localises the failure ONLY when the search completed, i.e. when "
            "the witness count is NOT a multiple of the per-box cap 8. Across the whole campaign "
            "exactly one run satisfied this: k6_23's full-window run (9 witnesses), and it is "
            "exactly the one whose sub-window bisection PASSed. Every other OPEN row reports 16 "
            "or 24 witnesses (truncated), and 6 of 7 attempted sub-window bisections FAILed."),
        "depth_scaling_0_of_5": (
            "Lifting the depth converted 0 of 5 attempts: k6_32, k5_19 (depth 56 AND 60), k5_20 "
            "(60), all timing out at 600-900 s. The +8-depth ~2.5x factor holds only for a run "
            "that CONVERGES (k5_15: 277 s FAIL@48 -> 687 s PASS@56). Depth 48 is the affordable "
            "regime and produced all 21 original TRANSFERRED rows; depth 56 pays only for a "
            "certificate whose tangency sits just past the depth-48 horizon."),
    }
    p["repairs_priced"] = {
        "sub_window_bisection": {
            "what": "verify_param on the complementary sub-window of the recorded witness band",
            "verdict": "WORKS ONLY WHEN THE WITNESS SET IS COMPLETE (see artifact 2)",
            "results": "2 successes / 8 windows attempted: k6_23 [191/50, 3877/1000] (2888 s, "
                       "99.85% of the window) and k6_07 [191/50, 956767/250000] (173 s, 12.4%). "
                       "k6_28, k5_14, k5_20, k6_32, k5_04, k6_19 all FAILed on their "
                       "complementary windows (0.5-144 s each).",
            "price": "one depth-48 run per window, 0.5-2900 s; cheap to attempt, low hit rate",
        },
        "resolve_with_margin": {
            "what": ("re-solve the guard LP with a ROW-SHRINK robustness margin eps_geo, so every "
                     "covering atom must sit at least eps_geo INSIDE Q, then re-certify at the "
                     "largest weight scale the budget allows and re-run the 4D verifier"),
            "verdict": "CONVERTS. 3 of 4 sampled certificates went from OPEN to full-window PASS.",
            "the_lever_is_eps_geo_not_the_weight_scale": (
                "k6_08 was first re-solved with witness-feedback rows and scale 1.03 -> 1.06 and "
                "STILL failed the 4D run (26 s). The same certificate with eps_geo = 0.003 "
                "converted in 12 s total. Scaling weights cannot help when coverage at the weak "
                "placement rests on ONE atom that must lie inside Q: the mass is already >= 1, it "
                "is the atom's POSITION that has no slack. eps_geo buys exactly that slack, and "
                "it is the same quantity the 4D verifier needs against the atom's s-interval."),
            "witness_feedback_was_inert": (
                "In all four sampled runs the witness glob matched 0 files (the sweep writes "
                "<name>.param.wit.json, the glob looked for *.witnesses.json), so n_4d_witnesses "
                "= 0 and the three conversions are due to eps_geo ALONE. The glob is fixed in "
                "resolve_margin.py, but the priced result stands without witness feedback."),
            "prices": {
                "k6_08": "CONVERTS in 12.0 s (LP 7.6 + certify 0.9 + 4D 1.5); new cert 4 atoms, "
                         "margin 0.760",
                "k6_28": "CONVERTS in 96.7 s (LP 49.5 + certify 2.8 + 4D 39.4); new cert 9 atoms, "
                         "margin 0.230",
                "k6_32": "CONVERTS in 677.3 s (LP 651.9 + certify 2.8 + 4D 17.9); new cert 452 "
                         "atoms, margin 0.230. The LP dominates; the 4D run is 18 s.",
                "k5_02": "INFEASIBLE at eps_geo = 0.003: tau rose to exactly 6.000000 = budget. "
                         "A certificate with total margin 0.00055 cannot pay for 0.003 of "
                         "positional slack. Retry with eps_geo ~ 0.0003.",
            },
            "robustness_budget_rule": (
                "eps_geo is affordable iff the re-solved tau stays below the budget. The observed "
                "cost of eps_geo = 0.003 was tau 4.000 -> 4.500 for k6_28/k6_32 (0.5 of budget) "
                "and 0 for k6_08. So certificates with budget - tau >= ~0.5 can afford it; the "
                "thin ones need eps_geo scaled down in proportion."),
            "caveat": ("a converted row kills the STRATUM over the window, but via a NEW base "
                       "certificate; the original A53/A54 certificate stays s0-only."),
            "recipe_steps": "see the module docstring of code/resolve_margin.py (steps 1-5)",
        },
    }
    p["cumulative_verifier_time_s"] = sb["cumulative_verifier_time_s"]
    json.dump(p, open(os.path.join(SW.RESULTS, "stage1_pricing.json"), "w"), indent=1)

    print(json.dumps(sb["summary"], indent=1))
    print("cumulative_verifier_time_s", sb["cumulative_verifier_time_s"],
          "=", round(sb["cumulative_verifier_time_s"] / 3600, 2), "h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
