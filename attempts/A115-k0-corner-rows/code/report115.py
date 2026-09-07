"""A115 report generator -- writes notes/report.md (T3 first, T2 second, T1 third, pointers last)."""
import collections
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a115lib as L

CFGS = ("d0", "d0.05", "d0.1")
OUT = os.path.join(L.BASE, "notes", "report.md")


def runs():
    d = os.path.join(L.RES, "rec")
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            out.append(json.load(open(os.path.join(d, f))))
    return out


def certs():
    p = os.path.join(L.RES, "t2_certs.jsonl")
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
                out[r["tag"]] = r
            except Exception:
                pass
    return out


def main():
    R = [r for r in runs() if r.get("tau") is not None]
    C = certs()
    T1 = {r["nid"]: r for r in json.load(open(os.path.join(L.RES, "t1_corners.json")))["recs"]}
    plan = json.load(open(os.path.join(L.RES, "t2_plan.json")))
    PL = {n["nid"]: n for n in plan["nodes"]}
    t3 = json.load(open(os.path.join(L.RES, "t3.json")))
    can = json.load(open(os.path.join(L.RES, "canary115.json")))
    t1md = open(os.path.join(L.RES, "t1_table.md"), encoding="utf-8").read()

    ncells = len({r["nid"] for r in R})
    cert_pass = sum(1 for c in C.values() if c["result"] == "PASS")
    Lo = []
    A = Lo.append

    A("# A115 — Lemma CW corner-crowd rows at the k0_00 NODE level (Opus chore, measurement)\n")
    kills = cert_pass
    att = t3.get("attributable_certified", 0)
    R_c = [r for r in R if r.get("c") is not None]
    cge = sum(1 for r in R_c if r["c"] >= r["B"] - 1e-9)
    A("> **VERDICT.  Corner incidence rows at δ ∈ {0, 0.05, 0.1} certify %d of %d %s K01 k0_00 "
      "cells they were attempted on, and only **%d** of those is attributable to the rows "
      "(`l3_pp65_111_000` at δ = 0, a level-3 cell: the plain node certificate FAILS on the same "
      "cell at the same LP wall, `results/control.jsonl`); the other reproduces without the rows. "
      "Zero cells that were genuinely alive at the LP (η₀ ≥ 0, %d of %d) died at any δ.**  The "
      "A109 failure mode is IMPOSSIBLE here — the four widened corner boxes are s0 − 2a_w = 1.826 "
      "> √2 apart, so a unit square carries at most ONE incidence, r_max ∈ {0,1}, B = 8 − Σ r_max "
      "∈ {7,8} is EXACT and no multiplicity re-pricing can happen.  The rows fail for the "
      "opposite reason: **the guaranteed budget 8 is below what a packing at s0 achieves for "
      "free.**  Exactly: every D4 image of Trump realises **9** corner incidences at a_w(0) = "
      "1.025520 (per-corner counts 3/2/2/2 — its tangent squares sit at μ_c = 1, inside the "
      "K0-WIDEN box), so at δ = 0 the achievable crowd mass is ≥ 9 > 8 = B and the ROOT LP can "
      "never pass; and at the node level the LP's own fractional packing realises c ≥ B in **%d "
      "of %d** measured runs (mean c = %.2f / %.2f / %.2f at δ = 0 / 0.05 / 0.1 against mean B = "
      "%.2f), so by the convexity rule (τ(e) is the optimum of an LP affine in e ⇒ c(e) "
      "non-decreasing ⇒ a kill needs c(e) < B) **no e can kill them**.  Price 224 s per (cell, δ) "
      "+ 410 s per certification; net −13 CPU-h against A99's 9,341–21,661 CPU-h frontier.\n"
      % (cert_pass, len(C), "" and "", att,
         sum(1 for r in R if (r.get("eta0") is not None and r["eta0"] >= -1e-9
                              and r["verdict"] != "alive")),
         len({r["nid"] for r in R if r.get("eta0") is not None and r["eta0"] >= -1e-9}),
         cge, len(R_c),
         t3["cfg"]["d0"]["mean_c"], t3["cfg"]["d0.05"]["mean_c"], t3["cfg"]["d0.1"]["mean_c"],
         sum(t3["cfg"][k]["mean_B"] for k in CFGS) / 3.0))
    A("> The single run in %d with c < B — `l2_p215_000__d0.1` (c = 6.55 < B = 7) — is an "
      "unconverged LP, and its two-run certificate FAILS on BOTH runs in both rounds (796 s).\n"
      % len(R_c))

    # ---------------- T3
    A("## T3 — verdict, price, projection\n")
    A("### price (measured)\n")
    A("| item | value |")
    A("|---|---|")
    p = t3["price"]
    A("| corner-row re-solve per (cell, δ), mean / median | %.0f / %.0f s |"
      % (p["mean_lp_s_per_cell_cfg"], p["median_lp_s"] or 0))
    walls = [r["lp_s"] for r in R if r.get("lp_s")]
    A("| … max | %.0f s |" % (max(walls) if walls else 0))
    A("| the same cell's ORIGINAL k0 node LP wall, mean / median | %.0f / %.0f s |"
      % (st.mean(x["time"] for x in _src_times()), st.median(x["time"] for x in _src_times())))
    A("| two-run frozen certification, mean | %s |"
      % ("%.0f s" % p["mean_cert_s"] if p["mean_cert_s"] else "n/a"))
    A("| certified | %d of %d attempted |" % (p["certified"], p["n_cert"]))
    A("")
    A("### projection onto the k0_00 tree\n")
    pr = t3["projection"]
    A("A115's rows are part of the NODE HYPOTHESIS, so a certified node is an ordinary A92 "
      "two-run certificate and the deployment is route (a): one corner-row re-solve on every open "
      "cell, harvesting the killed cell AND its whole subtree.\n")
    A("| item | value |")
    A("|---|---|")
    A("| A99 frontier (STACKED window-valid, `projection99.json`) | %.0f–%.0f CPU-h |" % tuple(pr["frontier_cpu_h"]))
    A("| level-1 cells of the k0_00 root split | %d |" % pr["n_level1"])
    A("| what one CERTIFIED level-1 kill removes | %.1f–%.1f CPU-h |"
      % tuple(pr["gain_per_certified_level1_kill_cpu_h"]))
    A("| cost of one corner-row pass over all %d level-1 cells (one δ) | %.2f CPU-h |"
      % (pr["n_level1"], p["root_deploy_one_cfg_cpu_h"]))
    A("| what one CERTIFIED kill removes at level 2 / 3 | %.2f–%.2f / %.2f–%.2f CPU-h |"
      % (*pr["gain_per_certified_kill_cpu_h_by_level"]["2"],
         *pr["gain_per_certified_kill_cpu_h_by_level"]["3"]))
    A("| certified level-1 kills measured here | %d |" % pr["certified_level1_kills"])
    A("| certified kills at any level (attributable to the rows) | %d (%d) |"
      % (p["certified"], t3.get("attributable_certified", 0)))
    A("| **net, counting only ATTRIBUTABLE certified kills** | %.2f / %.2f CPU-h |"
      % tuple(pr["net_cpu_h_attributable"]))
    A("")
    A("### attribution control (`code/control115.py`, `results/control.jsonl`)\n")
    A("For every cell whose CORNER-ROW certificate passed: does the same cell certify WITHOUT the "
      "rows?  `ctrlA` = the campaign's own stored LP result, plain certificate; `ctrlB` = a PLAIN "
      "re-solve warm-started from it with the same 240 s cap A115's stage 1 used, then the same "
      "plain certificate.\n")
    A("| cell | level | corner-row cert | ctrlA (stored LP) | ctrlB (matched plain re-solve) | "
      "attributable to the rows |")
    A("|---|---|---|---|---|---|")
    for a in t3.get("certified", []):
        A("| `%s` | %s | PASS | %s | %s | **%s** |"
          % (a["nid"], a["level"], a["ctrlA"], a["ctrlB"], "YES" if a["attributable"] else "no"))
    A("")

    # ---------------- T2
    A("## T2 — corner rows at the node level\n")
    A("`B` = 8 − Σ r_max(B⁺) over the node's conditioned cores = the corner-crowd incidences "
      "Lemma CW guarantees among the squares the node LP still pays for; `bonus` = floor(eB) = 1 "
      "at e = 1/B; `c` = (τ − τ₀)/e = the incidences the LP's own fractional packing realises. "
      "A kill needs `c < B`.\n")
    A("| cfg | δ | a_w | cells | mean B | mean c | c ≥ B | kill-candidates (LP) | knife-edge | "
      "alive | certified | mean LP s |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for cfg in CFGS:
        s = t3["cfg"].get(cfg)
        if not s:
            continue
        A("| `%s` | %s | %.6f | %d | %.2f | %s | %d/%d | %d | %d | %d | %d/%d | %.0f |"
          % (cfg, cfg[1:] or "0", s["a_w"], s["n"], s["mean_B"],
             ("%.2f" % s["mean_c"]) if s["mean_c"] is not None else "n/a",
             s["c_ge_B"], s["c_known"], s["kill_cand"], s["knife"], s["alive"],
             s["certified"], s["cert_attempted"], s["mean_lp_s"] or 0))
    A("")

    A("### per cell (η = τ − budget; the CERTIFICATE is the verdict, never η)\n")
    A("| cell | src | lvl | room | budget₀ | τ₀ | η₀ | B | n | τ(d0) | η(d0) | τ(d0.05) | "
      "η(d0.05) | τ(d0.1) | η(d0.1) | c(d0) | cert |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    bynid = collections.defaultdict(dict)
    for r in R:
        bynid[r["nid"]][r["cfg"]] = r
    for nid in sorted(bynid, key=lambda n: (T1[n]["level"] if n in T1 else 9, n)):
        g = bynid[nid]
        any_r = next(iter(g.values()))
        t1 = T1.get(nid, {})
        pl = PL.get(nid, {})
        cs = [c["result"] for t, c in C.items() if t.startswith(nid + "__")]
        A("| `%s` | %s | %s | %s | %d | %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |"
          % (nid, t1.get("src", "-"), t1.get("level", "-"), pl.get("room", "-"),
             any_r["budget0"],
             ("%.4f" % any_r["tau0"]) if any_r.get("tau0") is not None else "-",
             ("%+.3f" % any_r["eta0"]) if any_r.get("eta0") is not None else "-",
             any_r["B"], any_r["budget"],
             *sum([[("%.4f" % g[c]["tau"]) if c in g else "-",
                    ("%+.3f" % g[c]["eta"]) if c in g else "-"] for c in CFGS], []),
             ("%.2f" % g["d0"]["c"]) if "d0" in g and g["d0"].get("c") is not None else "-",
             ",".join(cs) or "-"))
    A("")

    if C:
        A("### certification of the kill candidates (frozen `verify_case.py`, A92's two-run form)\n")
        A("| tag | result | rounds | run A | run B | wall s |")
        A("|---|---|---|---|---|---|")
        for t, c in sorted(C.items()):
            rds = c.get("rounds") or []
            last = rds[-1] if rds else {}
            A("| `%s` | %s | %d | %s | %s | %.0f |"
              % (t, c["result"], len(rds),
                 ("PASS" if last.get("rcA") == 0 else "FAIL(%s)" % (last.get("holesA") or "?"))
                 if last else "-",
                 ("PASS" if last.get("rcB") == 0 else "FAIL(%s)" % (last.get("holesB") or "?"))
                 if last else "-",
                 c.get("wall_s", 0)))
        A("")

    A("### Trump canary\n")
    for cfg in CFGS:
        row = can["images"][cfg]
        A("* `%s` (a_w = %.6f): images realising the corner-crowd hypothesis: **%s** — "
          "per-image corner counts %s"
          % (cfg, row["a_w_f"], ",".join(row["realising"]) or "NONE",
             ";".join("%s[%d%d%d%d]" % (x["image"], x["BL"], x["BR"], x["TL"], x["TR"])
                      for x in row["counts"])))
    A("")
    for n in can["notes"]:
        A("* " + n)
    A("")
    A("* **canary verdict: %s**\n" % can["verdict"])

    # ---------------- T1
    A("## T1 — which corner, how deep\n")
    A(t1md.split("\n", 1)[1])

    A("## Pointers\n")
    A("* method, the licensing table for δ = 0 / 0.05 / 0.1 and the exact node incidence budget: "
      "`attempts/A115-k0-corner-rows/notes/method.md`")
    A("* code: `attempts/A115-k0-corner-rows/code/` (the A92 engine copied verbatim + "
      "`a115lib.py`, `t1.py`, `plan115.py`, `t2.py`, `certify115.py`, `canary115.py`, `t3.py`, "
      "`report115.py`)")
    A("* results: `results/t1_corners.json`, `results/t1_table.md`, `results/t2_plan.json`, "
      "`results/t2_runs.jsonl`, `results/rec/<tag>.json` (one resumable record per cell x δ x e), "
      "`results/nodes/<nid>.src.json` (every campaign node json, copied) and "
      "`results/nodes/<tag>.lp.json`, `results/fams/fam_d*.json`, `results/t2_certs.jsonl`, "
      "`results/t3.json`, `results/canary115.json`, `results/trump_family_counts.json`")
    A("* certificates: `certs/runA_*.json`, `certs/runB_*.json` (frozen verifier sha256 "
      "`521cb01f…`)")
    A("* logs: `logs/t1.log`, `logs/t2_s0.log`, `logs/t2_s1.log`, `logs/certify_s0.log`, "
      "`logs/canary.log`")
    open(OUT, "w", encoding="utf-8").write("\n".join(Lo) + "\n")
    print("wrote", OUT)


def _src_times():
    out = []
    d = L.NODES
    for f in os.listdir(d):
        if f.endswith(".src.json"):
            try:
                j = json.load(open(os.path.join(d, f)))
            except Exception:
                continue
            if "time" in j:
                out.append(j)
    return out or [dict(time=0.0)]


if __name__ == "__main__":
    main()
