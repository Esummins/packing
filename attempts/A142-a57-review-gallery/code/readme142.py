"""A142 T3 -- docs/shadows/a57v3/README.md (the ranked table) and review_a57v3.csv.

Reads every results/gallery142_*.json shard plus results/population142.json and writes, into
docs/shadows/a57v3/:

  README.md          the population arithmetic, the subtree-cost formula, and the ranked table
                     (node, class, level, subtree cost, family, lane-1 corners, narrowest pocket,
                     what to look for), A57 then A60;
  review_a57v3.csv   docs/shadows/review.csv's own columns plus polycore_status, clip_kept,
                     lane_1_corners, narrowest_pocket and the empty PI columns.

    set PYTHONDONTWRITEBYTECODE=1 && python code/readme142.py
"""
import csv
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
OUT = os.path.join(ROOT, "docs", "shadows", "a57v3")


def look_for(sm):
    bits = []
    if sm.get("clip_empty"):
        bits.append("**DEAD**: the pin-clip at the EXACT pin core empties the box at all 8 tilt "
                    "sub-bins" + ("" if sm.get("clip_empty_stock")
                                  else " (the deployed stock-core clip does not see it)"))
    if sm["lane1"]:
        bits.append("LANE<=1 at " + ", ".join(sm["lane1"]) + " (a second meeter is the cover)")
    nn = [p for p in sm["pockets"] if p["gap"] < 1.0]
    if nn:
        bits.append(f"{len(nn)} pocket(s) < 1: "
                    + ", ".join(f"{p['to']} {p['gap']:.3f}" for p in nn[:3]))
    if sm["n_impossible"]:
        bits.append(f"{sm['n_impossible']} impossible column(s)"
                    + (f", {sm['n_impossible_pin']} of them the PINS'"
                       if sm["n_impossible_pin"] else ""))
    if sm["clip"]["kept_vol"] < 0.999:
        bits.append(f"pin-clip keeps only {sm['clip']['kept_vol']:.3f} of the box")
    return "; ".join(bits) or "nothing free: read the load path in panel 2"


def main():
    pop = json.load(open(os.path.join(BASE, "results", "population142.json"), encoding="utf-8"))
    rows, summ = [], []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "gallery142_*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        rows += d["rows"]
        summ += d["summary"]
    order = {r["file"]: i for i, r in enumerate(rows)}
    summ.sort(key=lambda s: (s["camp"], s["rank"]))
    rows.sort(key=lambda r: order[r["file"]])
    byid = {s["id"]: s for s in summ}

    # ---- csv
    cols = list(rows[0].keys())
    with open(os.path.join(OUT, "review_a57v3.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (byid[r["file"][:-4]]["camp"],
                                             byid[r["file"][:-4]]["rank"])):
            w.writerow(r)

    # ---- readme
    ar = pop["arithmetic"]
    st = pop["start"]
    sv = pop["surviving"]
    cm = pop["cost_model"]
    L = []
    L.append("# The A57 / A60 review gallery, v3 (A142)")
    L.append("")
    L.append("One page per surviving alive node, in the format the PI reviewed on 2026-09-07 "
             "(A140's `docs/shadows/k0v3/`), with the three objects the A57 figures had never "
             "shown: the **exact pin cores** (A135, half-side 1/2 - delta/sqrt2, certified), the "
             "**polygon core** K'(B) (A132, certified vertices) and the **pin-clipped centre "
             "box** (A131, exact rationals per tilt sub-bin). Every conditioned H carries all "
             "THREE of its cores in distinct styles - solid black = the stock axis core K(a) the "
             "LP pruned against, solid teal = A135's exact axis core, filled purple = K' - and "
             "every pin carries both its stock and its exact core. Schematic objects (centre "
             "boxes, clipped boxes, lane cells) are thin dashed outlines with no fill: they are "
             "regions of centres, not square bodies.")
    L.append("")
    L.append("## 1. The population: which alive nodes survive today's kills")
    L.append("")
    L.append(f"Start from A131's corpus (`attempts/A131-pin-clip/results/corpus131.jsonl`): of "
             f"A96's {st['corpus_total']} boxes, {st['corpus_open']} are open and "
             f"**{st['work_owing']} are work-owing = {st['alive']} ALIVE + {st['fail']} FAIL**. "
             f"Then remove today's kills, and every descendant of a killed node (monotonicity: a "
             f"child's centre box is a sub-box and its tilt bin a sub-interval, so a geometric "
             f"exclusion is inherited - A124 `notes/trim_empty_alive.md` section 4).")
    L.append("")
    L.append("| step | list | hits the work-owing set | NEW removals | running total removed |")
    L.append("|---|---|---|---|---|")
    names = {"pinclip_A131": "A131 pin-clip kills (`backlog_kills.jsonl`)",
             "polycore_A135": "A135 polygon (T5-poly) kills (`polycore_kills.jsonl`)",
             "lp_certified_A135": "A135 LP kills certified through the verifier",
             "trimempty_A124": "A124 trim-empty ALIVE nodes (zero-LP sweep)",
             "descendants_of_killed (monotonicity)":
                 "descendants of anything killed (monotonicity)"}
    for a in ar:
        L.append(f"| {names.get(a['step'], a['step'])} | {a['n_in_list']} | "
                 f"{a['n_hits_work_owing']} | {a['n_new']} | {a['running_removed']} |")
    # ---- A142's own kills: the clip re-run at A135's certified exact pin core (section 2b)
    xk = json.load(open(os.path.join(BASE, "results", "exactclip_kills.json"), encoding="utf-8"))
    k57 = [json.loads(x) for x in
           open(os.path.join(BASE, "results", "exactclip_kills_a57.jsonl"), encoding="utf-8")
           if x.strip()]
    nk = len(k57)
    tot = ar[-1]["running_removed"] + nk
    L.append(f"| **A142 pin-clip at the EXACT pin core** (certificates below) | {nk} | {nk} | "
             f"{nk} | {tot} |")
    L.append(f"| **surviving** | | | | **{st['work_owing']} - {tot} = {sv['n'] - nk}** |")
    L.append("")
    lev = dict(sv["by_level"])
    cls_ = dict(sv["by_class"])
    for r in k57:
        lev[str(r["level"])] = lev.get(str(r["level"]), lev.get(r["level"], 0)) - 1
        lev.pop(r["level"], None) if str(r["level"]) in lev else None
        cls_[r["cls"]] = cls_.get(r["cls"], 0) - 1
    nal = sv["alive"] - sum(1 for r in k57 if "ALIVE" in str(r["prior_verdict"]))
    nfa = sv["fail"] - sum(1 for r in k57 if "ALIVE" not in str(r["prior_verdict"]))
    L.append(f"**{sv['n'] - nk} nodes survive: {nal} ALIVE + {nfa} FAIL**, by level "
             + ", ".join(f"L{k} {v}" for k, v in sorted(lev.items()))
             + ", by class " + ", ".join(f"{k} {v}" for k, v in sorted(cls_.items()))
             + ". The first four kill lists overlap heavily - the 54 A124 trim-empty nodes are "
               "ALL already inside the 132 pin-clip kills, and 54 of the 64 polygon kills are "
               "too, which is why 253 list entries remove only 142 nodes. The last row is this "
               f"attempt's own: {nk} further nodes die to the SAME clip re-run at A135's "
               f"certified exact pin core (section 2b), taking the population from "
               f"{sv['n']} to {sv['n'] - nk}. None of the {nk} has a still-open descendant in "
               "the population, and none of them is among the 40 pages drawn below, so no page "
               "here is stale.")
    L.append("")
    L.append(f"A60's alive population is the **{pop['a60']['n']} nodes with an LP support** in "
             f"A107's `shadow_nodes.json`; they are all at depth j = 0 (level 1) and none has "
             f"emitted a child.")
    L.append("")
    L.append("## 2. The subtree-cost ranking")
    L.append("")
    L.append("From `docs/budget.md` section B: KILL-BY-LOGIC ~0 s, PASS ~850 s (LP 240-400 + "
             "exact verify 100 at s0 + 4-D window verify 545 at level 2), FAIL ~900 s, "
             "ALIVE-at-LP 300 s of LP **and then eight children**. With p_K(L), p_L(L), p_A(L) "
             "the measured per-level verdict shares of A57's own 2,418-box corpus,")
    L.append("")
    L.append("```")
    L.append("C(L) = p_K(L)*0 + p_L(L)*850 + p_A(L)*(300 + 8*C(L+1)),    C(5) = 0")
    L.append("")
    L.append("subtree(n) = residual(n) + SUM over still-open emitted descendants d of residual(d)")
    L.append("residual(ALIVE at L with no still-open emitted child) = 8*C(L+1) * kept8(n)")
    L.append("residual(ALIVE at L that already has such children)   = 0")
    L.append("residual(FAIL)                                        = 900 s")
    L.append("```")
    L.append("")
    L.append("`kept8(n)` is A131's measured pin-clip kept VOLUME at 8 tilt sub-bins - the "
             "per-node alive fraction that multiplies the crude 8^(levels remaining); a node "
             "clipped to 12% of its box carries 12% of the modelled subtree. C(5) = 0 because "
             "the tree terminates at level 4 (budget.md section A: level-4 descent 0 of 30).")
    L.append("")
    L.append("| level | corpus rows | logic | leaf (PASS+FAIL) | alive | C(L) |")
    L.append("|---|---|---|---|---|---|")
    for k in sorted(cm["per_level_mix"], key=lambda x: int(x)):
        m = cm["per_level_mix"][k]
        L.append(f"| {k} | {m['n']} | {100 * m['pK']:.1f}% | {100 * m['pL']:.1f}% | "
                 f"{100 * m['pA']:.1f}% | {cm['C'][k]:.0f} s |")
    L.append("")
    L.append("The model cannot see inside an un-descended box, so every level-1 ALIVE node with "
             "kept8 = 1 and no emitted child gets the SAME subtree cost (2.88 CPU-h). Ties are "
             "broken by the polygon core's measured bite on that node's own dual support "
             "(A132 `measure132.jsonl`, `w_poly_only`): among equally expensive nodes, the ones "
             "where K' already excludes the most dual weight are the ones a geometric reading is "
             "most likely to close. That is the order below.")
    L.append("")

    cs = None
    p = os.path.join(BASE, "results", "clipsweep142.json")
    if os.path.exists(p):
        cs = json.load(open(p, encoding="utf-8"))
        L.append("## 2b. A free kill found while drawing: the pin-clip at the EXACT pin core")
        L.append("")
        L.append("A131 deployed the clip with the STOCK pin core half-side "
                 "`A_PIN = 1/2 - delta = 0.49`. A135 certified the pin's guaranteed core to be "
                 "the larger square of half-side `1/2 - delta/sqrt2 = 0.492928902`, and that the "
                 "frozen verifiers take the half-side VERBATIM. Enlarging `a_pin` in the clip is "
                 "sound for the same reason it is sound in the verifier: the conditioned square "
                 "is interior-disjoint from the pin square, and the pin square CONTAINS K'(P) at "
                 "every pose of the pin box. So the clip re-run at `a_pin = a_exact` is a "
                 "strictly stronger geometric test at the same cost - and it is the composition "
                 "of the day's two levers that nobody had run.")
        L.append("")
        a = cs["a57"]
        b = cs["a60"]
        L.append(f"* **A57**: over all {a['n']} surviving nodes the deployed stock-core clip "
                 f"empties **{a['empty_stock']}** (the correct control - the 132 stock-clip "
                 f"kills were already removed from this population), and the exact-core clip "
                 f"empties **{a['empty_exact']}**. Those "
                 f"**{a['n_new']} are NEW T5''' logic kills**, free, geometry only: "
                 + ", ".join(f"`{x}`" for x in a["new_empty_under_exact"]) + ".")
        L.append(f"* **A60 has never been clipped at all.** Its pins are EXACT placements "
                 f"(box `x0 = x1`), so the guaranteed pin core is the whole unit square, "
                 f"`a_pin = 1/2`. Of the {b['n']} A60 nodes with an LP support, "
                 f"**{b['empty_exact']} clip to EMPTY** - dead by pin geometry, no LP, no "
                 f"certificate change. {b['touched_exact']} more are narrowed (mean kept volume "
                 f"{b['mean_kept_exact']}).")
        L.append(f"* Across A57 the exact core also narrows **{a['tighter_than_stock']} of "
                 f"{a['measured']}** boxes strictly further than the stock core does (mean kept "
                 f"volume {a['mean_kept_stock']} -> {a['mean_kept_exact']}).")
        L.append("")
        L.append(f"**Replayable certificates for all {xk['a57']['nodes'] + xk['a60']['nodes']} "
                 f"of them** are emitted in A131's own `pin-clip-kill-certificate-v1` format "
                 f"under `attempts/A142-a57-review-gallery/certs/{{a57,a60}}/`, with ledgers "
                 f"`results/exactclip_kills_{{a57,a60}}.jsonl`. Each records `a_pin = "
                 f"33873816211/68719476736 = 0.49292890196375083` (A60: 1/2 to the same grid) as "
                 f"the half-side actually used, carries A135's `exactcore` certification for "
                 f"every pin box (the corner-by-corner rational vertex test that licenses the "
                 f"larger core - all certified), and carries the full per-sub-bin replay trace. "
                 f"**A131's INDEPENDENT checker `checkclip131.py` reads them unchanged and passes "
                 f"all {xk['a57']['nodes'] + xk['a60']['nodes']} "
                 f"({xk['a57']['nodes']} A57 + {xk['a60']['nodes']} A60, 0 FAIL)**; the sampled "
                 f"confirmation inside the certificates is "
                 f"{xk['a57']['sample_totals']['drawn'] + xk['a60']['sample_totals']['drawn']:,} "
                 f"drawn poses with "
                 f"{xk['a57']['sample_totals']['hits'] + xk['a60']['sample_totals']['hits']} "
                 f"pin-free hits. Witnesses: "
                 f"{xk['a57']['by_witness_kind'].get('single', 0) + xk['a60']['by_witness_kind'].get('single', 0)}"
                 f" single-pin, "
                 f"{xk['a57']['by_witness_kind'].get('joint-2', 0) + xk['a60']['by_witness_kind'].get('joint-2', 0)}"
                 f" two-pin joint. Of the A60 kills, {xk['a60']['t5pp_alone_suffices']} are "
                 f"emptied by the ALREADY-DEPLOYED T5'' trim alone - they are open only because "
                 f"the trim was never applied to A60. A57/A96/A60 state is untouched; one line "
                 f"is appended to A57's `PAUSED.md` resume block and to A60's "
                 f"`notes/ledger.md` so the owners fold them in.")
        L.append("")
        L.append("Independent control (`results/clipsweep142.json`, sampling, not the same "
                 "code path): 4,000 uniform poses drawn in the box of each EMPTY node give "
                 "**zero** pin-free poses, while non-empty controls give 75-2,126. Every page "
                 "below draws BOTH clips - pale orange dotted = stock, heavy orange dashed = "
                 "exact - so the difference is visible on the node.")
        L.append("")

    for camp, key, title in (("A57", "rank_a57", "3. A57 - the top 40 by subtree cost"),
                             ("A60", "rank_a60", "4. A60 - the top 20 by subtree cost")):
        drawn = [s for s in summ if s["camp"] == camp]
        if not drawn:
            continue
        L.append(f"## {title}")
        L.append("")
        L.append("| # | node | class | L | subtree cost | family | tau/budget | K'-only support "
                 "(cols / weight) | impossible cols (pins) | clip kept (exact core) | LANE<=1 "
                 "corners | narrowest pocket | what to look for |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        rk = {r["id"]: r for r in pop[key]}
        for s in drawn:
            r = rk.get(s["id"], {})
            L.append(
                f"| {s['rank']} | [`{s['id']}`]({s['id']}.svg) | {s['cls']} | {s['level']} | "
                f"{s['subtree_cpuh']:.2f} CPU-h | {s['shadow'] or '-'} | "
                f"{s['tau']:.6f}/{s['budget']} | {r.get('n_poly_only', '-')} / "
                f"{r.get('w_poly_only', '-')} | {s['n_impossible']} ({s['n_impossible_pin']}) | "
                + ("**EMPTY - dead**" if s.get("clip_empty")
                   else f"{s['clip']['kept_vol']:.3f}")
                + f" | {', '.join(s['lane1']) or '-'} | {s['pockets'][0]['to']} "
                f"{s['pockets'][0]['gap']:.3f} | {look_for(s)} |")
        L.append("")

    L.append("## 5. How to read a page")
    L.append("")
    L.append("* **Panel 1** is the LP's own dual support at s0. A red-dashed column is a "
             "placement the LP is charging weight to that **cannot exist** under this node's "
             "hypothesis - it overlaps the conditioned square H, or one of the five pins, at "
             "every one of 7^3 sampled poses of that square's box. Each is labelled with which "
             "core it clears and which it meets, so `clears K(a) stock, clears K exact, meets K'` "
             "is a column only the polygon core reaches, and `clears K(a) stock, meets K exact` "
             "is one the exact pin core alone reaches - the slop A132's attribution found.")
    n4 = sum(1 for s in summ if s.get("reading_auto") == "st4")
    nnr = sum(1 for s in summ if s["shadow"] and s["s_star"] - 3.877084 > 1e-6)
    L.append(f"* **Panel 2** is the near-packing, and its names are the names to label from. "
             f"**It is drawn at the shadow's OWN side s\\*, not at s0**, because a minimised "
             f"shadow closes only at its own s\\*; s0's container is overlaid as a heavy dashed "
             f"square from the same origin, and the band between the two is the room the "
             f"configuration needs and does not have at s0. A large-type banner says which case "
             f"it is. **{nnr} of the {len([s for s in summ if s['shadow']])} pages with a shadow "
             f"family have s\\* > s0 and are NOT realisable at s0** - the four squares that span "
             f"the container in, e.g., `c0_Y0171` (S01, s\\* = 4.000000, s\\* - s0 = +0.122916) "
             f"span it at s\\*, and that unit of room is exactly the S01 \"room at side 4\" "
             f"structure. {n4} pages have s\\* >= 4 and are marked `st4` in the review sheet's "
             f"new `reading_auto` column. The 5 pages with no shadow family draw the raw dual "
             f"support at s0 and are banner-marked NOT a packing.")
    L.append("* **Panel 3** is the hypothesis alone: the three cores of H captioned with "
             "`a_stock / a_exact / area K'`, the pin-clipped centre box per tilt sub-bin, the "
             "A118 LANE<=1 corner cells, and the measured pockets.")
    L.append("* **The line under each page** names the corners whose lane count is 1 (a second "
             "meeter is what a two-meeter cover needs) and the pockets between K'(B) and the "
             "nearest pin narrower than 1 - nothing fits there, so any square the LP puts in "
             "that region is a column the geometry forbids.")
    L.append("")
    L.append("Lane counts are **A118's stored AXIS-CORE verdicts** (K(a), not K'). A141's K' "
             "lane run had not landed when these pages were drawn, so a corner marked UNDECIDED "
             "here may still become LANE<=1 under K' - that is exactly the s3_far effect the PI "
             "read on A140's page.")
    L.append("")
    v = os.path.join(BASE, "results", "verify142.json")
    if os.path.exists(v):
        t = json.load(open(v, encoding="utf-8"))["totals"]
        L.append(f"**Geometry check** (`code/verify142.py`, a second implementation using "
                 f"edge-crossing and strict point-in-polygon, no separating axis anywhere): "
                 f"{t['A_cols']} red-dashed columns re-verified over {t['A_poses']} poses, "
                 f"{t['A_fail']} failures; {t['B_cols']} non-flagged columns each shown disjoint "
                 f"at some pose of every box, {t['B_fail']} failures; {t['C_pins']} exact pin "
                 f"cores contained in their pin square at every pose, {t['C_fail']} failures; "
                 f"{t['D_verts']} K'(B) vertices contained at every pose, {t['D_fail']} "
                 f"failures; {t['E_rects']} clipped rects inside the original box, "
                 f"{t['E_fail']} failures.")
        L.append("")
    L.append(f"Files: {len([s for s in summ if s['camp'] == 'A57'])} A57 pages + "
             f"{len([s for s in summ if s['camp'] == 'A60'])} A60 pages, "
             f"`review_a57v3.csv` (the review sheet, PI columns empty), and the machine-readable "
             f"record in `attempts/A142-a57-review-gallery/results/`.")
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote", os.path.join(OUT, "README.md"), "and review_a57v3.csv",
          f"({len(rows)} pages)")


if __name__ == "__main__":
    main()
