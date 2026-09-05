"""A100 report: every measured term of the protected-class pipeline, then the tier projection
and the all-layers total.

Terms measured per class (all from this attempt's own ledgers):
  L1  level-1 cell count            -- results/a84_<cls>_census_j0.json  (exact, no LP)
  L2  per-node LP + certify wall    -- results/a84_<cls>_cover_j0.jsonl
  L3  first-pass certification rate -- same
  L4  parametric emission + verify  -- results/param100.jsonl
  L5  resolver closure              -- results/resolve100.jsonl
  L6  level-2 descent + child cost  -- results/a84_<cls>_deepen_r1.jsonl (delta_pin = 1e-2)
  L7  (D) leaves                    -- results/a84_<cls>_ladder_j0_scan.json + A83/A86 tube certs

Projection: per-class CPU-h x 16, adjusted per A84's tier table (docs/proofs/protected_trees.md
Sec 7), then the all-layers total with A96's A57 numbers (projection96.json) and A99's k0 numbers.
"""
import argparse, json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")
H = 3600.0


def _rows(p):
    out = []
    if os.path.exists(p):
        for ln in open(p):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def _stat(v):
    if not v:
        return None
    return dict(n=len(v), mean=round(sum(v) / len(v), 1), median=round(st.median(v), 1),
                lo=round(min(v), 1), hi=round(max(v), 1))


def cls_report(cls):
    R = dict(cls=cls)
    cen_p = os.path.join(RES, "a84_%s_census_j0.json" % cls)
    if os.path.exists(cen_p):
        cen = json.load(open(cen_p))
        R["L1_cells"] = dict(cover=cen["counts"]["cover"], attemptable=cen["counts"]["attemptable"],
                             contradictory=cen["counts"]["contradictory"],
                             unkillable=cen["counts"]["unkillable"],
                             by_rule=cen["contradictory_by_rule"],
                             child_budget=cen["child_budget"],
                             canary_violations=len(cen["canary_violations"]),
                             canary_PD_violations=len(cen["canary_PD_violations"]),
                             image_squares_in_zone=sum(1 for v in cen["images_in_zone"].values() if v))

    cov = _rows(os.path.join(RES, "a84_%s_cover_j0.jsonl" % cls))
    if cov:
        # pilot59.run_child appends its own row and tree84.kill appends the final one (with the
        # eps_geo outcome folded in), so a node can appear twice.  Keep the LAST row per tag.
        byt = {}
        for r in cov:
            byt[r["tag"]] = r
        cov = [byt[t] for t in sorted(byt)]
        done = [r for r in cov if "verdict" in r]
        pas = [r for r in done if r["verdict"] == "PASS"]
        fail = [r for r in done if str(r["verdict"]).startswith("FAIL")]
        alive = [r for r in done if str(r["verdict"]).startswith("refused (tau")]
        can = [r for r in done if "CANARY" in str(r["verdict"])]
        lp = [r["lp_s"] for r in done if isinstance(r.get("lp_s"), (int, float))]
        ce = [r["cert_s"] for r in done if isinstance(r.get("cert_s"), (int, float))]
        tot = [r.get("lp_s", 0.0) + r.get("cert_s", 0.0) for r in done
               if isinstance(r.get("lp_s"), (int, float))]
        first = [r for r in pas if not r.get("eps_geo_used")]
        R["L2_per_node_s"] = dict(lp=_stat(lp), certify=_stat(ce), lp_plus_certify=_stat(tot),
                                  cpu_h_spent=round(sum(tot) / H, 3))
        R["L3_rates"] = dict(attempted=len(done), passed=len(pas), first_pass=len(first),
                             cert_fail=len(fail), lp_alive=len(alive), canary_refused=len(can),
                             first_pass_rate=round(len(first) / len(done), 4) if done else None,
                             pass_rate=round(len(pas) / len(done), 4) if done else None,
                             resister_rate=round((len(fail) + len(alive)) / len(done), 4)
                             if done else None,
                             tau=_stat([r["tau"] for r in done if isinstance(r.get("tau"), float)]),
                             eta=_stat([r["eta"] for r in done if isinstance(r.get("eta"), float)]))

    par = [r for r in _rows(os.path.join(RES, "param100.jsonl")) if r["cls"] == cls]
    if par:
        pw = [r["param_wall_s"] for r in par if isinstance(r.get("param_wall_s"), (int, float))]
        ok = [r for r in par if r["verdict"] == "PASS"]
        pf = [r for r in par if r["verdict"] == "FAIL"]
        em = [r for r in par if r["verdict"] == "EMIT-ERROR"]
        to = [r for r in par if r["verdict"] == "TIMEOUT"]
        fr = [(r.get("coverage") or {}).get("certified_frac") for r in par]
        fr = [f for f in fr if f is not None]
        R["L4_parametric"] = dict(n=len(par), full_window_pass=len(ok), partial_fail=len(pf),
                                  emit_error=len(em), timeout=len(to),
                                  full_window_rate=round(len(ok) / len(par), 4),
                                  wall_s=_stat(pw), cpu_h=round(sum(pw) / H, 3),
                                  mean_coverage_frac=round(sum(fr) / len(fr), 6) if fr else None,
                                  emit_errors=[r["id"] for r in em][:8])

    rsv = [r for r in _rows(os.path.join(RES, "resolve100.jsonl")) if r["cls"] == cls]
    if rsv:
        w = [r["resolve_wall_s"] for r in rsv]
        R["L5_resolver"] = dict(n=len(rsv), closed=sum(1 for r in rsv if r["closed"]),
                                closure_rate=round(sum(1 for r in rsv if r["closed"]) / len(rsv), 4),
                                wall_s=_stat(w), cpu_h=round(sum(w) / H, 3),
                                rows=sum(len(r["rows"]) for r in rsv),
                                residual=sum(len(r["residual"]) for r in rsv))

    dp = _rows(os.path.join(RES, "a84_%s_deepen_j0_r1.jsonl" % cls))
    if dp:
        byt = {}
        for r in dp:
            byt[r["tag"]] = r
        dp = [byt[t] for t in sorted(byt)]
        done = [r for r in dp if "verdict" in r]
        pas = [r for r in done if r["verdict"] == "PASS"]
        logic = [r for r in done if str(r["verdict"]).startswith("free")
                 or "contradictory" in str(r["verdict"]) or "shared" in str(r["verdict"])]
        tot = [r.get("lp_s", 0.0) + r.get("cert_s", 0.0) for r in done
               if isinstance(r.get("lp_s"), (int, float))]
        pr = len({r["tag"].rsplit("_D", 1)[0] for r in done})
        R["L6_level2"] = dict(children=len(done), parents=pr,
                              children_per_resister=(round(len(done) / pr, 2) if pr else None),
                              passed=len(pas), logic_killed=len(logic),
                              kill_rate=round(len(pas) / len(done), 4) if done else None,
                              per_child_s=_stat(tot), cpu_h=round(sum(tot) / H, 3),
                              delta_pin=1e-2)

    lad_p = os.path.join(RES, "a84_%s_ladder_j0_scan.json" % cls)
    if os.path.exists(lad_p):
        L = json.load(open(lad_p))
        lv = L["levels"]
        land = next((l["level"] for l in lv if l.get("all_inside")), None)
        R["L7_D_leaves"] = dict(
            levels=len(lv) - 1, landing_level=land,
            D_leaves=len(L.get("final_residue", [])),
            chain_boxes=lv[-1].get("chain_boxes") if lv else None,
            K_kill_queue=sum(l.get("kill_queue", 0) for l in lv),
            all_inside=lv[-1].get("all_inside") if lv else None,
            all_in_tube=lv[-1].get("all_in_tube") if lv else None,
            max_containment_t=lv[-1].get("max_containment_t") if lv else None,
            max_containment_c=lv[-1].get("max_containment_c") if lv else None,
            max_containment_theta=lv[-1].get("max_containment_theta") if lv else None,
            rbasin=lv[-1].get("rbasin") if lv else None,
            r_c_tube=lv[-1].get("r_c_tube") if lv else None,
            r_theta_tube=lv[-1].get("r_theta_tube") if lv else None,
            contraction_ratio=[l.get("contraction_ratio") for l in lv],
            residue_per_level=[l.get("boxes") for l in lv],
            images_in_zone=len(L.get("images_in_zone", [])),
            canary_bugs=len(L.get("canary_bugs", [])))
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_11,k3_02")
    ap.add_argument("--out", default=os.path.join(RES, "a100_report.json"))
    a = ap.parse_args()
    out = dict(attempt="A100-protected-pilot",
               classes={c: cls_report(c) for c in a.cls.split(",") if c})
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
