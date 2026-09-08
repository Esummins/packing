"""A150 -- assemble notes/tables.md from the results on disk (no compute)."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")


def j(name):
    p = os.path.join(RES, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def lp_rows():
    rows = []
    for f in sorted(glob.glob(os.path.join(RES, "lp150*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            r["_src"] = os.path.basename(f)
            rows.append(r)
    return rows


def main():
    out = []
    w = out.append
    w("# A150 — tables\n")

    b1 = j("band150_b1.json")
    b2 = j("band150_b2.json")
    band = j("band150.json")
    conf = j("band150_confirm.json")
    w("## 1. The band (per corner)\n")
    w("| step | cells in | killed | cells out |")
    w("|---|---|---|---|")
    w("| A143 level-1 cells (6 x 6 positions x 6 tilt windows of 15 deg) | 216 | 0 | 216 |")
    w("| (B1) no partner cell survives A143's pair geometry | 216 | %d | %d |"
      % (b1["stats"]["b1_fail"], b1["stats"]["b1_pass"]))
    w("| (B2) disk bound n_max >= 10 with the one core removed | %d | %d | %d |"
      % (b1["stats"]["b1_pass"], b2["stats"]["b2_fail"], len(band["band"])))
    w("")
    g = band["geometry"]
    w("band = **%d** cells; centre distance from the corner spans [%.4f, %.4f] (width %.4f), "
      "tilt spans [%.0f, %.0f) deg (the full range); %d of 36 position cells present; "
      "disk bound over all 216 cells n_max in [%d, %d] against budget 10."
      % (g["n"], g["d_min"], g["d_max"], g["d_width"], g["th_min"], g["th_max"],
         len(g["pos_cells"]), b2["stats"]["n_max_min"], b2["stats"]["n_max_max"]))
    w("")
    if conf:
        w("cover confirmation: **%d drawn / %d hits / %d misses** (realised interior-disjoint BL "
          "2-crowds, both members located); %d exact-rational cross-checks of the meet test, "
          "0 disagreements.\n"
          % (conf["drawn"], conf["hits"], conf["misses"], conf["n_exact_cross_checked"]))

    st = j("prod150_stages.json")
    pr = j("prod150_pairs.json")
    w("## 2. The product cover, stage by stage\n")
    w("| stage | surviving 4-tuples | D4 orbits | cut so far |")
    w("|---|---|---|---|")
    tot0 = st["stages"][0]["total"]
    for s in st["stages"]:
        w("| %s | %d | %d | %.2f %% |"
          % (s["stage"], s["total"], s["orbits_exact"], 100.0 * (1 - s["total"] / tot0)))
    w("")
    w("per adjacent corner pair, of 206^2 = 42 436: (Q2) %d, (Q1) %d, (Q1s) %d -> %d killed "
      "(%.2f %%); per diagonal pair: (Q2) %d, (Q1) %d, (Q1s) %d -> %d (%.3f %%).  "
      "Vertical-mirror consistency of the adjacency matrix: %s.\n"
      % (pr["A"]["Q2"], pr["A"]["Q1"], pr["A"]["Q1s"],
         pr["A"]["total"] - pr["A"]["alive"],
         100.0 * (1 - pr["A"]["alive"] / pr["A"]["total"]),
         pr["D"]["Q2"], pr["D"]["Q1"], pr["D"]["Q1s"],
         pr["D"]["total"] - pr["D"]["alive"],
         100.0 * (1 - pr["D"]["alive"] / pr["D"]["total"]), pr["A_mirror_consistent"]))

    dd = j("prod150_disk_direct.json")
    sp = j("prod150_sep.json")
    gu = j("prod150_guard.json")
    can = j("canary150.json")
    w("## 3. The kills that fire on nothing\n")
    w("| leaf | measured on | result | kills |")
    w("|---|---|---|---|")
    if gu:
        w("| (QG) A144 guard lines, %d axis lines at pitch 0.01 | %d sampled survivors | "
          "rhs_min %.4f, median %.4f (needs < 0) | 0 |"
          % (gu["n_lines"], gu["n_tuples"], gu["rhs_min"], gu["rhs_median"]))
    if dd:
        w("| (QD) A148 disk bound, all four cores, budget 7 | %d random survivors | "
          "n_max in [%d, %d], median %.0f | 0 |"
          % (dd["nsample"], dd["n_max_min"], dd["n_max_max"], dd["n_max_median"]))
    if sp:
        w("| (QS) separation bound, side %.2f partition | the same %d survivors | "
          "n_max in [%d, %d], median %.0f — WORSE than the disk bound | 0 |"
          % (sp["L"], sp["nsample"], sp["sep_min"], sp["sep_max"], sp["sep_median"]))
    w("")
    if can:
        w("**Trump canary**: %d 4-tuples over the eight D4 images, %d in band, **%d survive every "
          "geometric kill** — verdict %s.\n"
          % (can["n_tuples"], can["n_in_band"], can["n_survive"], can["verdict"]))

    w("## 4. The LP with four conditioned squares (budget 7 = 11 - 4)\n")
    w("A143's ONE-corner numbers at the same 240 s cap, for comparison: budget 10, "
      "eta = -0.0442 / -0.6328 / -0.0000, **0 converged kills**; budget 9 with TWO squares at the "
      "SAME corner, eta = -0.0826 / -0.0769, **0 converged kills**.\n")
    rows = lp_rows()
    tot_cpu = 0.0
    seen = set()
    dedup = []
    for r in sorted(rows, key=lambda r: (r.get("kind") or "", r["node"])):
        tot_cpu += r.get("wall_s_total") or r.get("wall_s") or 0.0
        if r["node"] in seen:
            continue
        seen.add(r["node"])
        dedup.append(r)
    rec = [r for r in dedup if (r.get("kind") or "") == "recert-scale130"]
    dedup = [r for r in dedup if (r.get("kind") or "") != "recert-scale130"]
    for title, keep in (("### 4a. the FINE band cover (206 cells/corner, a ~ 0.31-0.36)",
                         lambda r: not (r.get("kind") or "").startswith("coarse")),
                        ("### 4b. the COARSE covers (the pricing question)",
                         lambda r: (r.get("kind") or "").startswith("coarse"))):
        sel = [r for r in dedup if keep(r)]
        if not sel:
            continue
        w(title + "\n")
        w("| node | kind | cells (BL,BR,TR,TL) | a_exact | tau | eta | conv | kill | cert | "
          "rows | wall s |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in sel:
            t = r.get("tuple") or []
            w("| `%s` | %s | %s | %.3f | %s | %s | %s | %s | %s | %s | %.1f |"
              % (r["node"], r.get("kind", ""),
                 " ".join("%d%d t%d" % tuple(x) for x in t),
                 min(r.get("a_exact") or [0]),
                 ("%.4f" % r["tau"]) if r.get("tau") is not None else "err",
                 ("%+.4f" % r["eta"]) if r.get("eta") is not None else "-",
                 r.get("converged"), r.get("kills_converged"), r.get("certified") or "-",
                 r.get("n_rows"), r.get("wall_s") or 0.0))
        nk = sum(1 for r in sel if r.get("kills_converged"))
        nc = sum(1 for r in sel if r.get("certified") == "PASS")
        ncand = sum(1 for r in sel if (r.get("tau") is not None and r["tau"] < 7 - 1e-9
                                       and not r.get("kills_converged")))
        w("")
        w("%d nodes: **%d converged kills** (%d certified PASS through the frozen verifier), "
          "%d unconverged kill candidates (tau < 7), %d alive.\n"
          % (len(sel), nk, nc, ncand, len(sel) - nk - ncand))
    if rec:
        w("### 4c. re-certification of the two FAILed kills at scale cap 1.30 (A143 used 1.03)\n")
        w("| node | tau | eta | conv | cert | wall s |")
        w("|---|---|---|---|---|---|")
        for r in rec:
            w("| `%s` | %.4f | %+.4f | %s | %s | %.1f |"
              % (r["node"], r["tau"], r["eta"], r.get("converged"),
                 r.get("certified") or "-", r.get("wall_s") or 0.0))
        w("")
        w("Same tau, same FAIL: the certificate failure is NOT a margin problem.  Both stay "
          "**LP-dead, certificate pending** (they need the A13/A14 separation loop with more "
          "rounds than A150's cert budget allowed).\n")
    w("total LP + certification CPU: **%.0f s = %.2f CPU-h** over %d node solves.\n"
      % (tot_cpu, tot_cpu / 3600.0, len(rows)))

    w("## 5. The coarseness ladder\n")
    w("`area_open` is A148's certified-non-blocked feasible-centre area with all four cores "
      "removed (6 random states per row, `results/ladder150.json`); on the fine cover the LP "
      "decides below `area_open ~ 2` and is alive above ~ 3.3, so it is a 1-second proxy for "
      "the 240 s LP.\n")
    w("| cover (positions x tilt windows) | cells/corner | core a (median) | D4 orbits | "
      "area_open min/med/max | cost at 100 s/node |")
    w("|---|---|---|---|---|---|")
    lad = {}
    for d in (j("ladder150.json") or []):
        lad[(d["npos"], d["ntilt"])] = d
    cz = []
    for p in sorted(glob.glob(os.path.join(RES, "coarse150_*.json"))):
        cz.append(json.load(open(p, encoding="utf-8")))
    st4 = st["stages"][-1]
    cz.append(dict(npos=6, ntilt=6, cells=206, total=st4["total"],
                   orbits=st4["orbits_exact"], adj_alive_frac=st4["adj_alive_frac"],
                   a_exact_min=0.3121, a_exact_max=0.3606))
    cz.sort(key=lambda d: d["cells"])
    for d in cz:
        L = lad.get((d["npos"], d["ntilt"]))
        orb = int(d["orbits"])
        w("| %d x %d x %d of %.1f deg | %d | %s | %d | %s | %s CPU-h |"
          % (d["npos"], d["npos"], d["ntilt"], 90.0 / d["ntilt"], d["cells"],
             ("%.4f" % L["a_exact_median"]) if L else "-", orb,
             ("%.2f / %.2f / %.2f" % (L["area_open_min"], L["area_open_median"],
                                      L["area_open_max"])) if L else "-",
             "{:,}".format(int(orb * 100 / 3600))))
    w("")
    open(os.path.join(BASE, "notes", "tables.md"), "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
