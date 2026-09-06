"""A109 -- build notes/report.md (T3 verdict, T2 tables, T1 tables) from the results on disk."""
import glob, json, math, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a109lib as L

CFGS = ["sound", "d0.05", "d0.1", "d0.3"]
CFG_LABEL = {"sound": "SOUND (a_w = 1+1e-5, m_u = 3)", "d0.05": "delta = 0.05 (m_u = 4)",
             "d0.1": "delta = 0.1 (m_u = 4)", "d0.3": "delta = 0.3 (m_u = 4)"}
# A96 core96 schedule accounting (LOG.md 2026-09-05): CPU-days the tight-core pre-filter removes
# per killed node, by level -- the direct node cost only (a LOWER bound: it excludes the subtree).
CPUD_PER_NODE = {1: 0.29 / 20, 2: 2.71 / 32, 3: 5.80 / 7, 4: 22.59 / 11}
SCHED_CPU_D = 66.53          # remaining A57/A96 schedule, 1 process
SCHED_WALL_D_5W = 13.31
OPEN_BY_LEVEL = {1: 1096, 2: 389, 3: 39, 4: 12}


def load_runs():
    runs = []
    for p in glob.glob(os.path.join(L.RES, "t2_runs_s*.jsonl")):
        for line in open(p):
            line = line.strip()
            if line:
                runs.append(json.loads(line))
    # keep, per (nid, cfg), the record with the smallest eta (the best kill attempt)
    best = {}
    for r in runs:
        if r.get("error"):
            continue
        k = (r["nid"], r["cfg"])
        if r.get("eta") is None:
            best.setdefault(k, r)
            continue
        b = best.get(k)
        if b is None or b.get("eta") is None or r["eta"] < b["eta"]:
            best[k] = r
    return runs, best


def fmt(v, n=3):
    return "-" if v is None else ("%.*f" % (n, v) if isinstance(v, float) else str(v))


def main():
    plan = {p["nid"]: p for p in json.load(open(os.path.join(L.RES, "t2_plan.json")))}
    runs, best = load_runs()
    # B computed over the RAW branch box (tree57.build_children: the child hypothesis is "some
    # square of the dilated family has its pose in b", so the exempt square's pose IS in b) --
    # tighter than the B+ bound the LPs were run with, and eta only depends on B through the
    # budget, so it can be re-scored without re-solving.
    try:
        BT = json.load(open(os.path.join(L.RES, "B_tight.json")))
    except Exception:
        BT = {}
    for (nid, cfg), r in best.items():
        bt = (BT.get(nid) or {}).get(cfg)
        if bt and r.get("tau") is not None:
            r["B_tight"] = bt[0]
            r["bonus_tight"] = int(math.floor(float(eval(r["e"] + ".0" if "/" not in r["e"]
                                                         else r["e"])) * bt[0]))
            r["eta_tight"] = r["tau"] - (r["budget0"] + r["bonus_tight"])
            r["dead_tight"] = bool(r.get("converged") and r["eta_tight"] < -1e-6)
    t1 = json.load(open(os.path.join(L.RES, "t1_summary.json")))
    try:
        canary = json.load(open(os.path.join(L.RES, "canary109.json")))
    except Exception:
        canary = None
    certs = []
    cp = os.path.join(L.RES, "t2_certs.jsonl")
    if os.path.exists(cp):
        for line in open(cp):
            if line.strip():
                certs.append(json.loads(line))

    try:
        T3 = json.load(open(os.path.join(L.RES, "t3.json")))
    except Exception:
        T3 = None

    out = []
    A = out.append
    A("# A109 -- node-level SLOT-CROWD rows in A57's tree (Opus chore, measurement)\n")
    A("> **VERDICT.  Node-level crowd rows kill 0 of 18 genuinely-alive A57 nodes at every depth "
      "the window licenses (delta_sound = 0, delta = 0.05, delta = 0.1) and 18 of 18 at "
      "delta = 0.3, certify 0 of 10, cost 128 s per node per delta, and are worth "
      "-0.4 wall-days.**  The mechanism is real but its threshold sits at delta ~ 0.2-0.3, and "
      "Theorem N-S licenses a delta-certificate only for sides m <= s-hat' - delta = 3.577 -- "
      "0.24 BELOW the window floor 3.82.  On the window itself the only licensed pad is "
      "`a_w = 1` (\"two non-pin squares MEET the slot box\"), and there the LP's own fractional "
      "packing realises c = 6.23 incidences against a guaranteed budget of B = 4.37, so the "
      "crowd rows make eta WORSE by +0.77 on average.\n")

    # ---------------- T3 (verdict first)
    if T3:
        A("## T3 -- price, composition, verdict\n")
        A("### price (measured)\n")
        p = T3["price"]
        A("| item | value |")
        A("|---|---|")
        A("| crowd re-solve per (node, cfg), mean / median / max | %.0f / %.0f / %.0f s |"
          % (p["crowd_resolve_mean_s"], p["crowd_resolve_median_s"], p["crowd_resolve_max_s"]))
        A("| the same node's ORIGINAL A57 LP wall, mean / median | %.0f / %.0f s |"
          % (p["node_original_lp_mean_s"], p["node_original_lp_median_s"]))
        A("| A57's measured LP+certify wall per level-1 node (block96 sec 3) | %.0f s |"
          % p["a57_measured_s_per_node_L1"])
        A("| certification (1 + r_max frozen runs incl. one witness-feedback round), mean | %.0f s |"
          % (sum(p["cert_wall_s"]) / max(1, len(p["cert_wall_s"]))))
        A("| certified | %d of %d |" % (sum(1 for x in p["cert_results"] if x == "PASS"),
                                        len(p["cert_results"])))
        A("")
        A("### kills per level and what they would remove from A57's remaining schedule\n")
        A("Baseline (LOG.md 2026-09-05, A96 core96 accounting): **66.53 CPU-days = 13.31 "
          "wall-days at 5 workers**, 1536 open boxes (L1 1096, L2 389, L3 39, L4 12), tail at "
          "levels 3-4.\n")
        A("| cfg | attributable kills L1 | L2 | rate | route (a) cost | route (a) gain | net wall-days at 5w |")
        A("|---|---|---|---|---|---|---|")
        for cfg in CFGS:
            e = T3["cfgs"].get(cfg)
            s = T3["schedule"].get(cfg)
            if not e or not s:
                continue
            bl = e["by_level"]
            A("| %s | %s/%s | %s/%s | %.2f | %.1f CPU-d | %.1f CPU-d | %+.1f |"
              % (cfg, bl.get("1", {}).get("dead", 0), bl.get("1", {}).get("n", 0),
                 bl.get("2", {}).get("dead", 0), bl.get("2", {}).get("n", 0), e["rate"],
                 s["route_a_cost_cpu_d"], s["route_a_gain_with_subtrees_cpu_d"],
                 s["route_a_net_wall_d_5w"]))
        A("")
        A("Route **(a)** = one crowd re-solve on every open box (cost above), harvesting the "
          "killed box AND its whole subtree.  Route **(b)** = crowd rows in every node LP from "
          "the start: the same per-node cost is paid on every child, and the rows only raise "
          "tau, so at the same kill rate it is never cheaper than (a); at the delta values the "
          "window licenses it is a pure %.1f-CPU-day loss.\n"
          % T3["schedule"]["sound"]["route_a_cost_cpu_d"])
        A("### composition with the parametric window certificate\n")
        A("* **Run A rides.** `A96/code/verify_param.py` proves `mu_s(Q) >= 1 + margin` for every "
          "`s` in `[s_lo, s_hi]` and every core-free admissible `Q`, with the atoms and the pin "
          "cores affine in `s` and the budget clause `sum w_i < n - #cores` s-free.  The crowd "
          "run A is exactly that certificate with `n = 11 + eB`, so it goes through unchanged; "
          "and `--strict-margin r e` is exactly run `B_r`'s inequality.\n")
        A("* **Runs B_r do not.** `verify_param.py` line 529-530 raises `nofams unsupported`, and "
          "runs `B_r` are defined by the exempt cover `E_r`.  The extension is architecturally "
          "small -- the slot frame is anchored to a container corner, so `F_p(a_w)` is "
          "s-INDEPENDENT in the frame and every `E_r` box is an affine `alpha + beta s` "
          "rectangle with `beta in {0,1}` per side, the same affine form the file already uses "
          "for atoms and cores -- but it does not exist today.  **So crowd rows can only be run "
          "at the fixed side s0 as things stand.**\n")
        A("* At a fixed side `s0` the k6_23 slot is usable (its A54 fixed-`s0` certificate "
          "applies), so `m_u = 4`; on A57's G1 SLAB it is not, so `m_u = 3` (notes/method.md).\n")

    # ---------------- T2 per-configuration summary
    A("## T2 -- crowd rows at the node level\n")
    A("Window: A57's G1 slack-core slab (m_lo, s0] with m_lo = %.7f, lambda_max = %.9f.\n"
      % (float(L.SF.M_LO_G1), float(L.S0 / L.SF.M_LO_G1)))
    A("`B` = 2 m_u - (crowd incidences the branched core may carry, bounded over B+); "
      "`bonus` = floor(e B); `c` = (tau_crowd - tau_node)/e = the incidences the LP's own "
      "fractional packing realises.  A kill needs c < B.\n")
    A("`eta - eta0 = c e - floor(eB) >= 0 whenever c >= B`: the crowd rows then move the node "
      "AWAY from death, whatever e is used.\n")
    A("**ATTRIBUTABLE** = the node was genuinely alive at the LP (eta0 = tau_node - budget_node "
      ">= 0) and the crowd rows drive eta < 0.  A node with eta0 < 0 was already "
      "dead-pending-convergence in A57 and its death is not the crowd rows' doing.\n")
    A("| cfg | m_u | a_w | nodes | eta0>=0 | **ATTRIBUTABLE kills** | mean B | mean bonus | "
      "mean c = dtau/de | c >= B | DEAD | dead-unconv | mean eta | mean eta-eta0 | mean LP s |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    percfg = {}
    for cfg in CFGS:
        rs = [best[k] for k in best if k[1] == cfg]
        if not rs:
            continue
        rr = [r for r in rs if r.get("tau") is not None]
        nd = sum(1 for r in rr if r.get("dead"))
        ndu = sum(1 for r in rr if r.get("dead_unconv"))
        cs = [r["c_dtau_de"] for r in rr if r.get("c_dtau_de") is not None]
        percfg[cfg] = dict(n=len(rs), n_lp=len(rr), dead=nd, dead_unconv=ndu,
                           mean_eta=(sum(r["eta"] for r in rr) / len(rr)) if rr else None,
                           mean_c=(sum(cs) / len(cs)) if cs else None)
        dd = [r["eta"] - r["eta0"] for r in rr]
        percfg[cfg]["mean_deta"] = (sum(dd) / len(dd)) if dd else None
        live = [r for r in rr if r["eta0"] >= -1e-9]
        attr = [r for r in live if r["eta"] < -1e-6]
        percfg[cfg]["n_live"] = len(live)
        percfg[cfg]["attributable"] = len(attr)
        percfg[cfg]["attributable_converged"] = sum(1 for r in attr if r.get("converged"))
        A("| %s | %s | %s | %d | %d | **%d** (%d converged) | %s | %s | %s | %d/%d | **%d** | %d | %s | %s | %s |"
          % (CFG_LABEL[cfg], rs[0].get("m_u"), rs[0].get("a_w", ["-"])[0], len(rs),
             len(live), len(attr), percfg[cfg]["attributable_converged"],
             fmt(sum(r["B"] for r in rs) / len(rs), 2),
             fmt(sum(r["bonus"] for r in rs) / len(rs), 2),
             fmt(percfg[cfg]["mean_c"], 2),
             sum(1 for r in rr if r.get("c_dtau_de") is not None
                 and r["c_dtau_de"] >= r["B"] - 1e-9), len(rr),
             nd, ndu, fmt(percfg[cfg]["mean_eta"], 3), fmt(percfg[cfg]["mean_deta"], 3),
             fmt(sum(r["lp_s"] or 0 for r in rr) / max(1, len(rr)), 0)))
    A("")
    A("Re-scored with the TIGHTER incidence budget `B_tight` (r_max over the branch box itself "
      "rather than over B+):\n")
    A("| cfg | mean B_used | mean B_tight | c >= B_tight | DEAD (tight) | dead-unconv (tight) |")
    A("|---|---|---|---|---|---|")
    for cfg in CFGS:
        rr = [best[k] for k in best if k[1] == cfg and best[k].get("eta_tight") is not None]
        if not rr:
            continue
        A("| %s | %s | %s | %d/%d | **%d** | %d |"
          % (cfg, fmt(sum(r["B"] for r in rr) / len(rr), 2),
             fmt(sum(r["B_tight"] for r in rr) / len(rr), 2),
             sum(1 for r in rr if r.get("c_dtau_de") is not None
                 and r["c_dtau_de"] >= r["B_tight"] - 1e-9), len(rr),
             sum(1 for r in rr if r.get("dead_tight")),
             sum(1 for r in rr if r["eta_tight"] < -1e-6)))
    A("")

    # ---------------- by stratum and level
    A("### by stratum and level (DEAD / n)\n")
    strata = sorted({plan[k[0]]["stratum"] for k in best})
    A("| stratum | level | n | " + " | ".join(CFGS) + " |")
    A("|---|---|---|" + "---|" * len(CFGS))
    for st in strata:
        for lv in (1, 2):
            nids = [n for n in plan if plan[n]["stratum"] == st and plan[n]["level"] == lv]
            if not nids:
                continue
            cells = []
            for cfg in CFGS:
                rs = [best[(n, cfg)] for n in nids if (n, cfg) in best]
                rr = [r for r in rs if r.get("tau") is not None]
                cells.append("%d/%d" % (sum(1 for r in rr if r.get("dead")), len(rs)))
            A("| %s | %d | %d | %s |" % (st, lv, len(nids), " | ".join(cells)))
    A("")

    # ---------------- per node
    A("### per node (eta = tau - budget; DEAD iff converged and eta < 0)\n")
    A("| node | cls | lvl | stratum | budget | tau_node | " +
      " | ".join("eta %s" % c for c in CFGS) + " | B(sound) | c(sound) |")
    A("|---|---|---|---|---|---|" + "---|" * (len(CFGS) + 2))
    for n in sorted(plan):
        p = plan[n]
        cells = []
        for cfg in CFGS:
            r = best.get((n, cfg))
            if r is None or r.get("eta") is None:
                cells.append("-")
            else:
                cells.append(("**%+.3f**" % r["eta"]) if r.get("dead") else "%+.3f" % r["eta"])
        rs = best.get((n, "sound")) or {}
        A("| `%s` | %s | %d | %s | %d | %.4f | %s | %s | %s |"
          % (n, p["cls"], p["level"], p["stratum"], p["budget"], p["tau"], " | ".join(cells),
             rs.get("B", "-"), fmt(rs.get("c_dtau_de"), 2)))
    A("")

    # ---------------- certificates
    if certs:
        A("### certification of the DEAD nodes (frozen verify_case.py, A94's 1 + r_max form)\n")
        A("| node/cfg | result | runs | holes | wall s |")
        A("|---|---|---|---|---|")
        for c in certs:
            rds = c.get("rounds") or []
            last = rds[-1] if rds else {}
            runs_s = "A=%s " % ("PASS" if last.get("rcA") == 0 else "FAIL") + " ".join(
                "B%s=%s" % (r, "PASS" if v == 0 else "FAIL")
                for r, v in sorted((last.get("rcB") or {}).items()))
            holes = []
            for tag, tl in [("A", last.get("verifierA") or [])] + \
                    [("B" + r, v) for r, v in sorted((last.get("verifierB") or {}).items())]:
                for l in tl:
                    if "HOLES" in l:
                        seg = l.split(":", 1)[1] if ":" in l else l
                        n = seg.split("HOLES")[0].strip().split()[-1]
                        holes.append("%s:%s" % (tag, n))
            A("| `%s` | %s | %s | %s | %s |" % (c["tag"], c["result"], runs_s,
                                                "; ".join(holes) or "-", c.get("cert_s")))
        A("")

    # ---------------- canary
    if canary:
        A("### Trump canary\n")
        e = canary["exact"]
        A("* exact Trump slot depths reproduce `docs/proofs/slot_crowds.md` sec 7 to %.1e -- %s"
          % (e["worst_dev"], "PASS" if e["ok"] else "FAIL"))
        for r in canary.get("lp", []):
            A("* trump5 class root (slack pins rho = 1e-2, the exact Trump SATISFIES it), %s: "
              "budget %d -> %d, tau = %.4f, eta = %+.4f, converged %s, **DEAD = %s** "
              "(must not die: %s)"
              % (r["cfg"], r["budget0"], r["budget"], r["tau"], r["eta"], r["converged"],
                 r["dead"] or r["dead_unconv"], r["must_not_die"]))
        A("* verdict: **%s**\n" % canary.get("verdict", "-"))

    # ---------------- T1
    A("## T1 -- what the dual supports leave empty\n")
    A("Weight of the node's dual support inside each usable slot box (the crowd rows charge "
      "exactly this).  `viol` = at least one usable slot met with weight < 2, i.e. a support "
      "that Lemma SLOT-CROWD forbids.  U3 = the three FULL-window slots (the only ones licensed "
      "on the G1 slab); U4 adds the k6_23 slot (licensed only at a fixed side s0).\n")
    A("| shadow | nodes | classes | frac viol U3 d>0 | mean violated slots (of 3) | mean total "
      "incidence (need 6) | frac viol U3 d>=0.05 | d>=0.1 | d>=0.3 | frac viol U4 d>0 |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for sid in ("S01", "S03", "S04", "S05", "ALL"):
        if sid not in t1:
            continue
        v = t1[sid]
        A("| %s | %d | %s | **%.3f** | %.2f | %.2f | %.3f | %.3f | %.3f | %.3f |"
          % (sid, v["n"], ", ".join("%s x%d" % kv for kv in sorted(v["by_class"].items())),
             v["frac_U3_d0"], v["meanIslots_U3_d0"], v["meanItot_U3_d0"],
             v["frac_U3_d0.05"], v["frac_U3_d0.1"], v["frac_U3_d0.3"], v["frac_U4_d0"]))
    A("")
    A("Which usable slot the support leaves empty or singly met (U3, d > 0), over all %d "
      "explained nodes: %s\n" % (t1["ALL"]["n"], t1["ALL"]["empty_or_single_slot_U3_d0"]))
    A("**Why T1's 94 % upper bound collapses to a 0 % kill rate in T2.**  T1 measures the "
      "incidence of the dual support A57's LP happened to stop at; the crowd rows do not "
      "forbid that support, they re-price it, and the LP simply moves.  The measured slope "
      "`c = dtau/de` -- the incidences the RE-OPTIMISED fractional packing realises -- is "
      "6.23 on average at `a_w = 1` against a guaranteed `B = 4.37`, i.e. the ghost buys the "
      "whole crowd and more.  The usable slot boxes of a class are 0.877 apart in each axis at "
      "s0 while a 45-degree unit square spans 1.414, so one fractional placement can sit in two "
      "or three of them at once; that is exactly the multiplicity Lemma CW-S has to pay for with "
      "the incidence budget `N + 2 m_u e`, and at the licensed pad it is a wash.  Depth is what "
      "breaks the multiplicity: at delta = 0.3 the same slope falls to 4.83 and every node "
      "dies.\n")

    A("## Pointers\n")
    A("* method, the `a_w = 1` derivation and the node-level incidence budget: "
      "`attempts/A109-node-crowd/notes/method.md`")
    A("* code: `attempts/A109-node-crowd/code/` (A94 engine copied verbatim + `a109lib.py`, "
      "`t1.py`, `plan109.py`, `t2.py`, `certify109.py`, `canary109.py`, `aw_check.py`, "
      "`t3.py`, `report109.py`)")
    A("* results: `results/t1_incidence.json`, `results/t1_summary.json`, `results/t2_plan.json`, "
      "`results/t2_runs_s*.jsonl`, `results/B_tight.json`, `results/t2_certs.jsonl`, "
      "`results/t3.json`, `results/canary109.json`, `results/nodes/` (every node json used, "
      "copied), `results/fams/` (the crowd families)")
    A("* certificates: `certs/runA_*.json`, `certs/runB*_*.json`, `certs/*.certify.json`")
    A("* logs: `logs/t1.log`, `logs/t2_s*.log`, `logs/certify109.out`, `logs/canary109.out`, "
      "`logs/aw_check.log`\n")
    txt = "\n".join(out) + "\n"
    open(os.path.join(L.BASE, "notes", "report.md"), "w").write(txt)
    print(txt[:4000])
    json.dump(dict(percfg=percfg, n_runs=len(runs), n_best=len(best)),
              open(os.path.join(L.RES, "t2_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
