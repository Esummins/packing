"""
A84 R9: the pilot scoreboard -> results/pilot_summary.json.

Reads only this attempt's results/.  Emits, per class, the laws the theory lead asked for:
P1 verdict; census counts; cover kill rate with LP-second statistics and the eta law; resisters
and deepen yield; residue boxes per level, contraction ratio, landing level under BOTH criteria
(t <= 3/2000) and (c <= 1.6e-3, theta <= 2.1e-3 rad); r_kill; the canary ledger (every image
square, its chain through the ladder, and the assertion that no node it realises was certified);
every commit-wait and defer event; total LP CPU-seconds.

    python code\\summary84.py --cls k4_08,k3_05
"""
import argparse, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")


def jl(p):
    q = os.path.join(RES, p)
    if not os.path.exists(q):
        return {}
    last = {}
    for line in open(q):
        try:
            r = json.loads(line)
        except Exception:
            continue
        last[r.get("tag")] = r
    return last


def jf(p, default=None):
    q = os.path.join(RES, p)
    return json.load(open(q)) if os.path.exists(q) else default


def bucket(v):
    return ("PASS" if v == "PASS" else
            "KILL-BY-LOGIC" if v.startswith("KILL-BY-LOGIC") else
            "ALIVE-CERTIFIED" if v.startswith("ALIVE") else
            "CANARY" if "CANARY" in v else
            "carried" if v.startswith("carried") else
            "DEFERRED" if v.startswith("DEFERRED") else
            "LP-alive" if v.startswith("refused (tau") else
            "cert-FAIL" if v.startswith("FAIL") else "other")


def stats(x):
    x = sorted(v for v in x if v is not None)
    if not x:
        return None
    return dict(n=len(x), min=round(x[0], 2), median=round(statistics.median(x), 2),
                mean=round(statistics.fmean(x), 2), max=round(x[-1], 2),
                total=round(sum(x), 1))


def phase_summary(recs):
    import collections
    c = collections.Counter()
    lps, certs, etas, taus = [], [], [], []
    for r in recs.values():
        c[bucket(r.get("verdict", "?"))] += 1
        if r.get("lp_s"):
            lps.append(r["lp_s"])
        if r.get("cert_s"):
            certs.append(r["cert_s"])
        if r.get("eta") is not None:
            etas.append(r["eta"])
        if r.get("tau") is not None:
            taus.append(r["tau"])
    den = c["PASS"] + c["LP-alive"] + c["cert-FAIL"]
    hist = {}
    for e in etas:
        k = ("eta<=-1" if e <= -1 + 1e-9 else "-1<eta<=-0.5" if e <= -0.5 else
             "-0.5<eta<0" if e < 0 else "eta>=0")
        hist[k] = hist.get(k, 0) + 1
    return dict(records=len(recs), verdicts=dict(c),
                kill_rate=(round(c["PASS"] / float(den), 4) if den else None),
                kill_rate_denominator=den, lp_s=stats(lps), cert_s=stats(certs),
                eta_histogram=hist,
                eta_le_minus1_fraction=(round(sum(1 for e in etas if e <= -1 + 1e-9)
                                              / float(len(etas)), 4) if etas else None),
                tau=stats(taus))


def ladder_laws(scan):
    if not scan:
        return None
    L = scan["levels"]
    boxes = [x["boxes"] for x in L]
    ratios = [x["contraction_ratio"] for x in L if x.get("contraction_ratio")]
    land_t = next((x["level"] for x in L
                   if x["boxes"] and x["inside_A36_basin"] == x["boxes"]), None)
    land_tube = next((x["level"] for x in L
                      if x["boxes"] and x["inside_tube_profile"] == x["boxes"]), None)
    return dict(levels=len(L), terminated=(L[-1].get("all_inside") is True),
                residue_boxes=dict(min=min(boxes), mean=round(statistics.fmean(boxes), 1),
                                   max=max(boxes), final=boxes[-1]),
                contraction_ratio=dict(min=round(min(ratios), 2),
                                       median=round(statistics.median(ratios), 2),
                                       mean=round(statistics.fmean(ratios), 2),
                                       max=round(max(ratios), 2),
                                       last=round(ratios[-1], 2)),
                landing_level_rbasin=land_t, landing_level_tube_profile=land_tube,
                final=dict(max_box_radius=L[-1]["max_box_radius"],
                           max_containment_t=L[-1]["max_containment_t"],
                           max_containment_c=L[-1]["max_containment_c"],
                           max_containment_theta=L[-1]["max_containment_theta"],
                           rbasin=L[-1]["rbasin"], r_c_tube=L[-1]["r_c_tube"],
                           r_theta_tube=L[-1]["r_theta_tube"]),
                kill_queue_total=sum(x.get("kill_queue", 0) for x in L),
                per_level=[{k: x[k] for k in ("level", "boxes", "max_box_radius",
                                              "max_gap_to_image", "max_containment_t",
                                              "max_containment_c", "max_containment_theta",
                                              "inside_A36_basin", "inside_tube_profile",
                                              "contraction_ratio") if k in x}
                           | {"kill_queue": x.get("kill_queue")} for x in L])


def r_kill(ladder_recs, scan):
    """the smallest sup-gap to an image square at which a kill still certifies."""
    ok = [r for r in ladder_recs.values() if r.get("verdict") == "PASS" and r.get("sup_gap")]
    bad = [r for r in ladder_recs.values()
           if r.get("verdict", "").startswith(("refused (tau", "FAIL")) and r.get("sup_gap")]
    return dict(passes=len(ok), non_passes=len(bad),
                r_kill=(round(min(r["sup_gap"] for r in ok), 6) if ok else None),
                largest_non_pass_gap=(round(max(r["sup_gap"] for r in bad), 6) if bad else None),
                by_level={str(r.get("level")): dict(verdict=r.get("verdict"),
                                                    sup_gap=r.get("sup_gap"),
                                                    lp_s=r.get("lp_s"), cert_s=r.get("cert_s"))
                          for r in sorted(ladder_recs.values(),
                                          key=lambda z: (z.get("level") or 0))})


def canary_ledger(cls, cen, scan, all_recs):
    led = dict(images_in_zone=(cen or {}).get("images_in_zone"),
               level0_boxes=(cen or {}).get("image_boxes"),
               census_canary_violations=(cen or {}).get("canary_violations"),
               census_PD_canary_violations=(cen or {}).get("canary_PD_violations"),
               ladder_canary_bugs=(scan or {}).get("canary_bugs"),
               ladder_PD_canary_violations=(scan or {}).get("canary_PD_violations"))
    chain = {}
    for lv in (scan or {}).get("canary_chain", []):
        for n, hits in lv["placements"].items():
            chain.setdefault(n, []).append(dict(level=lv["level"], boxes=len(hits),
                                                kinds=sorted({h["kind"] for h in hits}),
                                                min_contain_t=(min(h["contain_t"] for h in hits)
                                                               if hits else None)))
    led["chain"] = chain
    led["chain_unbroken"] = all(all(s["boxes"] >= 1 for s in v) for v in chain.values()) \
        if chain else None
    cert = [r for r in all_recs.values()
            if r.get("verdict") == "PASS" and (r.get("canary_images") or [])]
    led["certified_image_nodes"] = cert
    led["canary_refusals"] = sum(1 for r in all_recs.values()
                                 if "CANARY" in str(r.get("verdict", "")))
    led["ASSERT_no_image_node_certified"] = (len(cert) == 0)
    return led


def per_class(cls):
    cen = jf("a84_%s_census_j0.json" % cls)
    cen_pre = jf("a84_%s_census_j0_pre_PD.json" % cls)
    scan = jf("a84_%s_ladder_j0_scan.json" % cls)
    scan_pre = jf("a84_%s_ladder_j0_scan_pre_PD.json" % cls)
    klass = jf("class_%s.json" % cls)
    p1 = jf("a84_%s_p1.json" % cls)
    cover = jl("a84_%s_cover_j0.jsonl" % cls)
    ladder = jl("a84_%s_ladder_j0.jsonl" % cls)
    deep = jl("a84_%s_deepen_j0_r1.jsonl" % cls)
    allr = {}
    for d in (cover, ladder, deep, jl("a84_%s_p1.jsonl" % cls)):
        allr.update(d)
    waits = []
    wp = os.path.join(RES, "a84_%s_waits.jsonl" % cls)
    if os.path.exists(wp):
        waits = [json.loads(l) for l in open(wp) if l.strip()]
    defers = []
    for f in os.listdir(RES):
        if f.startswith("a84_%s_deferred" % cls):
            defers += [json.loads(l) for l in open(os.path.join(RES, f)) if l.strip()]
    cov = phase_summary(cover)
    dee = phase_summary(deep)
    out = dict(
        cls=cls,
        class_constants=dict(k_s=(klass or {}).get("k_s"), N=(klass or {}).get("N"),
                             delta_pin=(klass or {}).get("delta_pin"),
                             pin_core_a=(klass or {}).get("pin_core_a"),
                             rho=(klass or {}).get("rho"), rho_f=(klass or {}).get("rho_f"),
                             A=(klass or {}).get("A"),
                             images=[i["key"] for i in (klass or {}).get("images", [])],
                             witness_summary=(klass or {}).get("witness_summary"),
                             lemma_PD=(klass or {}).get("lemma_PD")),
        P1=dict(verdict=(p1 or {}).get("verdict"), tau=(p1 or {}).get("tau"),
                eta=(p1 or {}).get("eta"), gate_k=(p1 or {}).get("gate_k"),
                per_image=(p1 or {}).get("per_image"), budget=(p1 or {}).get("budget"),
                rect=(p1 or {}).get("rect"), lp_s=(p1 or {}).get("lp_s"),
                cert_s=(p1 or {}).get("cert_s"), lemma=(p1 or {}).get("lemma")),
        census=dict(counts=(cen or {}).get("counts"),
                    contradictory_by_rule=(cen or {}).get("contradictory_by_rule"),
                    counts_pre_PD=(cen_pre or {}).get("counts"),
                    corner_TR=( (jf("a84_%s_census_corner_TR_j0.json" % cls) or {}).get("counts")
                                if cls.startswith("k3") else None)),
        cover=cov, deepen=dee,
        resisters=dict(cover=[t for t, r in cover.items()
                              if bucket(r.get("verdict", "")) in ("LP-alive", "cert-FAIL")],
                       deepen_yield=dict(free=dee["verdicts"].get("KILL-BY-LOGIC", 0),
                                         residue=(dee["verdicts"].get("ALIVE-CERTIFIED", 0)
                                                  + dee["verdicts"].get("carried", 0)),
                                         passed=dee["verdicts"].get("PASS", 0),
                                         still_resisting=(dee["verdicts"].get("LP-alive", 0)
                                                          + dee["verdicts"].get("cert-FAIL", 0)))),
        ladder=ladder_laws(scan), ladder_pre_PD=ladder_laws(scan_pre),
        ladder_kills=phase_summary(ladder), r_kill=r_kill(ladder, scan),
        canary=canary_ledger(cls, cen, scan, allr),
        waits=waits, defers=defers,
        total_lp_cpu_s=round(sum((r.get("lp_s") or 0) + (r.get("cert_s") or 0)
                                 for r in allr.values()), 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_08,k3_05")
    ap.add_argument("--out", default="pilot_summary.json")
    a = ap.parse_args()
    classes = [c for c in a.cls.split(",") if c]
    res = dict(attempt="A84-protected-trees", pilot="R1-R9 (pilot_design.md)",
               generated=__import__("time").strftime("%Y-%m-%d %H:%M:%S"),
               engine_corrections=[
                   "parent tolerance = delta_pin + 1e-9 (slack pins)",
                   "mod-90 identification in contain_t / sup_containment / sup_gap",
                   "Lemma PD (pin drift) logic kill -- without it the residue floor equals "
                   "delta_pin (see ladder_pre_PD)"],
               classes={c: per_class(c) for c in classes})
    res["total_lp_cpu_s"] = round(sum(res["classes"][c]["total_lp_cpu_s"] for c in classes), 1)
    json.dump(res, open(os.path.join(RES, a.out), "w"), indent=1)
    print(json.dumps({c: dict(P1=res["classes"][c]["P1"]["verdict"],
                              census=res["classes"][c]["census"]["counts"],
                              cover_kill_rate=res["classes"][c]["cover"]["kill_rate"],
                              landing=(res["classes"][c]["ladder"] or {}).get(
                                  "landing_level_rbasin"),
                              canary_ok=res["classes"][c]["canary"][
                                  "ASSERT_no_image_node_certified"])
                      for c in classes}, indent=1))
    print("wrote %s" % os.path.join(RES, a.out))


if __name__ == "__main__":
    main()
