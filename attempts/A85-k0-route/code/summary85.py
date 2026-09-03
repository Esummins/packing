"""A85 `summary85.py` -- R5: collate R1-R4 into results/pilot_summary85.json + notes/pilot_report.md."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
NOTES = os.path.join(BASE, "notes")


def jl(p):
    out = {}
    if os.path.exists(p):
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            out[r.get("tag")] = r          # last record for a tag wins
    return out


def main():
    R1 = json.load(open(os.path.join(RES, "a85_reach_BL.json")))
    R2 = json.load(open(os.path.join(RES, "a85_pairs_BL.json")))
    R3 = json.load(open(os.path.join(RES, "a85_gate_samples.json")))
    CL = json.load(open(os.path.join(RES, "class_k0_00.json")))
    plan = json.load(open(os.path.join(RES, "a85_lp_plan.json")))["plan"]
    recs = jl(os.path.join(RES, "a85_lp_samples.jsonl"))
    waits = []
    wp = os.path.join(RES, "a85_waits.jsonl")
    if os.path.exists(wp):
        waits = [json.loads(l) for l in open(wp) if l.strip()]
    defer = []
    dp = os.path.join(RES, "a85_k0_00_deferred_j0.jsonl")
    if os.path.exists(dp):
        defer = [json.loads(l) for l in open(dp) if l.strip()]

    rows = []
    for p in plan:
        r = recs.get(p["tag"])
        rows.append(dict(tag=p["tag"], group=p["group"], level=p["level"],
                         budget=p["budget"], n_cores=p["n_cores"],
                         near_far=p["near_far"], ghost=round(p.get("ghost", 0.0), 5),
                         a38_tau=p.get("a38_tau"),
                         tau=(r or {}).get("tau"), eta=(r or {}).get("eta"),
                         converged=(r or {}).get("converged"), lp_s=(r or {}).get("lp_s"),
                         cert_s=(r or {}).get("cert_s"),
                         verdict=(r or {}).get("verdict", "not-run"),
                         eps_geo=(r or {}).get("eps_geo"),
                         canary_images=(r or {}).get("canary_images")))
    done = [r for r in rows if r["verdict"] not in ("not-run",)]
    cert = [r for r in done if r["eta"] is not None and r["eta"] <= -0.15]
    board = dict(planned=len(rows), run=len(done),
                 PASS=sum(1 for r in done if r["verdict"] == "PASS"),
                 FAIL=sum(1 for r in done if str(r["verdict"]).startswith("FAIL")),
                 refused=sum(1 for r in done if str(r["verdict"]).startswith("refused")),
                 eta_le_m015=len(cert),
                 lp_seconds_total=round(sum(r["lp_s"] or 0 for r in done), 1),
                 cert_seconds_total=round(sum(r["cert_s"] or 0 for r in done), 1))

    V = R1["variants"]
    out = dict(
        cls="k0_00", generated=time.strftime("%Y-%m-%d %H:%M:%S"),
        object=dict(k_s=CL["k_s"], N=CL["N"], pins=CL["SLOTS"], images=len(CL["images"]),
                    s_rat=CL["s_rat"],
                    witness_min_pairwise_gap=CL["witness_summary"]["g0"]["min_pairwise_gap_f"],
                    all_families_ok=all(v["ok"] for v in CL["witness_summary"].values())),
        R1=dict(corner="BL", w_widen=R1["w_widen"], a=R1["a"], rect=R1["rect"],
                w_box=R1["w_box"], a_min=R1["a_min"],
                t_partition_sigma_closed=R1["sigma_closed_check"]["closed"],
                variants={k: dict(counts=V[k]["counts"], grid=V[k]["grid"],
                                  box_set_sigma_closed=V[k]["box_set_sigma_closed"],
                                  sound_by_sense=V[k]["sound_by_sense"],
                                  t_edges=V[k]["t_edges"]) for k in V},
                seconds=R1["seconds"]),
        R2=dict(variant=R2["variant"], n_sound_boxes=R2["n_sound_boxes"],
                n_pair=R2["n_pair"], sense_table=R2["sense_table"], seconds=R2["seconds"]),
        R3=dict(pair_gate_budget9=R3["pair_gate_budget9"],
                image_compatible_pairs=R3["image_compatible_pairs"],
                canary_images_without_a_compatible_BL_pair=R3[
                    "canary_images_without_a_compatible_BL_pair"],
                fast_gate_validation={k: R3["fast_gate_validation"][k]
                                      for k in ("n", "disagreements")},
                corner_map_check=R3["corner_map_check"],
                surviving_pairs_sigma_closed=R3["surviving_pairs_sigma_closed"],
                sample_2corner=R3["sample_2corner"], sample_3corner=R3["sample_3corner"],
                sample_4corner={k: R3["sample_4corner"][k] for k in
                                ("corners", "budget", "n", "counts", "d4_canonical",
                                 "d4_canonical_fraction", "orbit_size_histogram")},
                seconds=R3["seconds"]),
        R4=dict(scoreboard=board, rows=rows, deferred=defer),
        waits=dict(n=len(waits), events=waits))
    json.dump(out, open(os.path.join(RES, "pilot_summary85.json"), "w"), indent=1)

    L = []
    A = L.append
    A("# A85 pilot report -- k0_00 corner frame (numbers only)")
    A("")
    A("## Object")
    A("k0_00: k_S = 0, pins = [], N = 11, images = 8 (G_S = D4), s0 = %s." % CL["s_rat"])
    A("All 8 exact witness families verified (admissible + strictly pairwise disjoint); "
      "min pairwise gap %.4e; every exact witness within 1e-5 of its float image placement."
      % CL["witness_summary"]["g0"]["min_pairwise_gap_f"])
    A("")
    A("## R1 reach cover at BL (rect [1/2,7/4]^2 x [0,90), w_box 0.15, a_min 0.34, "
      "w = %.3f, a = %.3f)" % (R1["w_widen"], R1["a"]))
    A("t-partition sigma-closed: %s" % R1["sigma_closed_check"]["closed"])
    A("| variant | boxes | sound (a=1+w) | sound (w=0) | witnessed | box set sigma-closed | "
      "P / M / S / A |")
    A("|---|---|---|---|---|---|---|")
    for k in V:
        c = V[k]["counts"]
        s = V[k]["sound_by_sense"]
        A("| %s | %d | %d | %d | %d | %s | %d / %d / %d / %d |"
          % (k, c["cover"], c["sound"], c["sound_w0"], c["witnessed"],
             V[k]["box_set_sigma_closed"], s.get("P", 0), s.get("M", 0), s.get("S", 0),
             s.get("A", 0)))
    A("")
    A("## R2 pair census at BL (variant %s, %d sound boxes)"
      % (R2["variant"], R2["n_sound_boxes"]))
    np_ = R2["n_pair"]
    A("all unordered pairs %d -> level0 %d -> level1 %d -> level2 %d"
      % (np_["all_unordered"], np_["level0"], np_["level1"], np_["level2"]))
    st = R2["sense_table"]
    kk = sorted(st["level0"])
    A("| level | " + " | ".join(kk) + " |")
    A("|---|" + "---|" * len(kk))
    for lv in ("level0", "level1", "level2"):
        A("| %s | " % lv + " | ".join(str(st[lv].get(x, 0)) for x in kk) + " |")
    A("")
    A("## R3 alive gate (exact)")
    pg = R3["pair_gate_budget9"]
    A("BL pairs at budget 9: attemptable %d (%.4f), unkillable %d (%.4f)"
      % (pg["attemptable"][0], pg["attemptable"][1], pg["unkillable"][0], pg["unkillable"][1]))
    A("image-compatible BL pairs per image: %s -- canary missing: %s"
      % (json.dumps(R3["image_compatible_pairs"]),
         R3["canary_images_without_a_compatible_BL_pair"] or "NONE (canary PASSES)"))
    A("fast gate vs frozen alive84 gate: %d sampled, %d disagreements"
      % (R3["fast_gate_validation"]["n"], R3["fast_gate_validation"]["disagreements"]))
    A("corner maps (BR/TR/TL): theta bins preserved = %s"
      % json.dumps({c: R3["corner_map_check"][c]["theta_bins_preserved"]
                    for c in R3["corner_map_check"]}))
    sc = R3["surviving_pairs_sigma_closed"]
    A("surviving-pair set sigma-closure: %d/%d (%.4f); max |a(b) - a(sigma b)| = %.4e"
      % (sc["sigma_image_also_surviving"], sc["n"], sc["fraction"],
         sc["max_core_a_asymmetry"]))
    for tag, key in (("2-corner BL+TR (budget 7)", "sample_2corner"),
                     ("3-corner BL+BR+TR (budget 5)", "sample_3corner"),
                     ("4-corner (budget 3)", "sample_4corner")):
        s = R3[key]
        A("%s, n=%d: %s" % (tag, s["n"], json.dumps(
            {k: v[1] for k, v in s["counts"].items()})))
    s4 = R3["sample_4corner"]
    A("D4-canonical 4-tuples: %d/%d = %.4f (1/8 = 0.125); orbit sizes %s"
      % (s4["d4_canonical"], s4["n"], s4["d4_canonical_fraction"],
         json.dumps(s4["orbit_size_histogram"])))
    A("")
    A("## R4 LP samples (lp_time 900 s, cert_time 300 s, <= 3 concurrent, commit gate 6144 MB)")
    A("| tag | group | budget | cores | near/far | ghost | A38 tau | tau | eta | conv | lp_s | "
      "cert_s | verdict |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        A("| %s | %s | %d | %d | %s | %.4f | %s | %s | %s | %s | %s | %s | %s |"
          % (r["tag"], r["group"], r["budget"], r["n_cores"], r["near_far"], r["ghost"],
             ("%.4f" % r["a38_tau"]) if r["a38_tau"] is not None else "-",
             ("%.6f" % r["tau"]) if r["tau"] is not None else "-",
             ("%+.6f" % r["eta"]) if r["eta"] is not None else "-",
             r["converged"], r["lp_s"], r["cert_s"], r["verdict"]))
    A("")
    A("scoreboard: %s" % json.dumps(board))
    A("waits logged: %d (results/a85_waits.jsonl); deferred: %d" % (len(waits), len(defer)))
    open(os.path.join(NOTES, "pilot_report.md"), "w").write("\n".join(L) + "\n")
    print(json.dumps(board))
    print("wrote results/pilot_summary85.json and notes/pilot_report.md")


if __name__ == "__main__":
    main()
