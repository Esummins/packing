"""A142 -- append Part IV to docs/shadows.md (append only; refuses if Part IV is already there).

    set PYTHONDONTWRITEBYTECODE=1 && python code/part4_142.py
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
DOC = os.path.join(ROOT, "docs", "shadows.md")


def main():
    txt = open(DOC, encoding="utf-8").read()
    if "# Part IV" in txt:
        print("Part IV already present; nothing appended.")
        return
    pop = json.load(open(os.path.join(BASE, "results", "population142.json"), encoding="utf-8"))
    cs = json.load(open(os.path.join(BASE, "results", "clipsweep142.json"), encoding="utf-8"))
    vf = json.load(open(os.path.join(BASE, "results", "verify142.json"), encoding="utf-8"))
    summ = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "gallery142_*.json"))):
        summ += json.load(open(f, encoding="utf-8"))["summary"]
    a57 = sorted([s for s in summ if s["camp"] == "A57"], key=lambda s: s["rank"])
    a60 = sorted([s for s in summ if s["camp"] == "A60"], key=lambda s: s["rank"])
    st, sv, ar, cm = pop["start"], pop["surviving"], pop["arithmetic"], pop["cost_model"]
    t = vf["totals"]

    L = ["", "", "# Part IV - the A57 / A60 review gallery v3 (A142)", ""]
    L.append("Parts I-III are the k0_00 and pinned-class shadow galleries. Part IV is the "
             "**A57 / A60 review gallery**: one page per surviving alive node, drawn in the "
             "format the PI reviewed on 2026-09-07 (Part III / `docs/shadows/k0v3/`), carrying "
             "the objects the A57 figures had never shown - the **exact pin cores** (A135), the "
             "**polygon core K'(B)** (A132) and the **pin-clipped centre box** (A131) - and, per "
             "the PI's drawing rules of that evening, all THREE cores of every conditioned "
             "square in distinct styles (stock K(a) solid black, A135's exact axis core solid "
             "teal, K' filled purple, captioned `a_stock / a_exact / area K'`), both cores of "
             "every pin, each red-dashed column labelled with which core it clears and which it "
             "meets, and every schematic object (centre box, clipped box, lane cell) as a thin "
             "dashed outline with no fill.")
    L.append("")
    L.append("**Pages:** `docs/shadows/a57v3/<node>.svg` - "
             f"{len(a57)} A57 + {len(a60)} A60. **Index and ranked table:** "
             "`docs/shadows/a57v3/README.md`. **Review sheet:** "
             "`docs/shadows/a57v3/review_a57v3.csv` (review.csv's columns + `polycore_status`, "
             "`clip_kept`, `lane_1_corners`, `narrowest_pocket`, PI columns empty). "
             "**Machine-readable:** `attempts/A142-a57-review-gallery/results/`.")
    L.append("")
    L.append("## IV.1 The population: which alive nodes survive today's kills")
    L.append("")
    L.append(f"Of A131's **{st['work_owing']} work-owing nodes ({st['alive']} ALIVE + "
             f"{st['fail']} FAIL)**:")
    L.append("")
    L.append("| removed by | list | hits | NEW | running |")
    L.append("|---|---|---|---|---|")
    for a in ar:
        L.append(f"| {a['step']} | {a['n_in_list']} | {a['n_hits_work_owing']} | {a['n_new']} | "
                 f"{a['running_removed']} |")
    L.append("")
    L.append(f"**{sv['n']} survive ({sv['alive']} alive + {sv['fail']} fail; L1 "
             f"{sv['by_level'].get('1', sv['by_level'].get(1, 0))}, L2 "
             f"{sv['by_level'].get('2', sv['by_level'].get(2, 0))}, L3 "
             f"{sv['by_level'].get('3', sv['by_level'].get(3, 0))})**. The four kill lists "
             f"overlap almost completely - all 54 A124 trim-empty nodes and 54 of the 64 "
             f"polygon kills are already inside the 132 pin-clip kills - so 253 list entries "
             f"remove {ar[-1]['running_removed']} nodes. A60 adds "
             f"{pop['a60']['n']} nodes with an LP support (A107 `shadow_nodes.json`), all at "
             f"depth j = 0.")
    L.append("")
    L.append("## IV.2 The subtree-cost ranking")
    L.append("")
    L.append("From `docs/budget.md` section B, with the per-level verdict shares measured on "
             "A57's own 2,418-box corpus:")
    L.append("")
    L.append("```")
    L.append("C(L) = p_K(L)*0 + p_L(L)*850 + p_A(L)*(300 + 8*C(L+1)),   C(5) = 0")
    L.append("subtree(n) = residual(n) + SUM over still-open emitted descendants d of residual(d)")
    L.append("residual(ALIVE frontier at L) = 8*C(L+1)*kept8(n)   [kept8 = A131's pin-clip kept "
             "volume]")
    L.append("residual(FAIL) = 900 s")
    L.append("```")
    L.append("")
    L.append("| L | C(L) | | L | C(L) |")
    L.append("|---|---|---|---|---|")
    Cs = cm["C"]
    L.append(f"| 1 | {Cs['1']:.0f} s | | 3 | {Cs['3']:.0f} s |")
    L.append(f"| 2 | {Cs['2']:.0f} s | | 4 | {Cs['4']:.0f} s |")
    L.append("")
    L.append(f"Top of the A57 list: `{a57[0]['id']}` {a57[0]['subtree_cpuh']:.2f} CPU-h "
             f"({a57[0]['clip']['kept_vol']:.3f} clip, "
             f"{[r for r in pop['rank_a57'] if r['id'] == a57[0]['id']][0]['n_open_desc']} still-"
             f"open emitted descendants), then `{a57[1]['id']}` and `{a57[2]['id']}` at "
             f"{a57[1]['subtree_cpuh']:.2f}. The model cannot see inside an un-descended box, so "
             f"every level-1 ALIVE node with `kept8 = 1` and no emitted child ties at 2.88 "
             f"CPU-h; ties break on the polygon core's measured bite on that node's own dual "
             f"support (A132 `w_poly_only`).")
    L.append("")
    L.append("## IV.3 What the drawing found: the pin-clip at the EXACT pin core")
    L.append("")
    a, b = cs["a57"], cs["a60"]
    L.append(f"A131 deployed the clip with the stock pin core `a = 1/2 - delta = 0.49`; A135 "
             f"certified the pin's guaranteed core to be `1/2 - delta/sqrt2 = 0.492928902` and "
             f"that the frozen verifiers take the half-side verbatim. Enlarging `a_pin` in the "
             f"clip is sound for the same reason it is sound in the verifier (the pin square "
             f"contains K'(P) at every pose of the pin box), and it costs nothing. Run over the "
             f"whole surviving population:")
    L.append("")
    L.append(f"* **A57: {a['empty_stock']} boxes empty at the stock core** (the correct control - "
             f"the 132 stock-clip kills are already out of this population) **and "
             f"{a['empty_exact']} at the exact core. Those {a['n_new']} are NEW T5''' logic "
             f"kills**, geometry only, no LP and no certificate change: "
             + ", ".join(f"`{x}`" for x in a["new_empty_under_exact"]) + ".")
    L.append(f"* **A60 had never been clipped at all.** Its pins are exact placements, so the "
             f"guaranteed pin core is the whole unit square (`a_pin = 1/2`): of "
             f"{b['n']} A60 nodes with an LP support, **{b['empty_exact']} clip to EMPTY** and "
             f"{b['touched_exact']} more are narrowed.")
    L.append(f"* The exact core also narrows **{a['tighter_than_stock']} of {a['measured']}** "
             f"A57 boxes strictly further than the stock core (mean kept volume "
             f"{a['mean_kept_stock']} -> {a['mean_kept_exact']}).")
    L.append("")
    L.append("Independent control (sampling, a different code path): 4,000 uniform poses drawn "
             "in each EMPTY node's box give **zero** pin-free poses; non-empty controls give "
             "75-2,126. Every page draws both clips (pale orange dotted = stock, heavy orange "
             "dashed = exact) so the difference is visible on the node.")
    L.append("")
    L.append("## IV.4 What the pages carry, and the geometry check")
    L.append("")
    L.append(f"Over the {t['pages']} pages: {sum(s['n_impossible'] for s in summ)} red-dashed "
             f"columns (of which {sum(s['n_impossible_pin'] for s in summ)} are impossible "
             f"against an EXACT PIN CORE rather than against the conditioned square - the pins' "
             f"share A132's attribution predicted), "
             f"{sum(s['n_impossible_certified'] for s in summ)} of them carrying a core "
             f"certificate; {sum(1 for s in summ if s['lane1'])} pages with at least one "
             f"A118 LANE<=1 corner; "
             f"{sum(1 for s in summ if s['pockets'][0]['gap'] < 1.0)} pages whose narrowest "
             f"measured pocket between K'(B) and its nearest neighbour is under 1.")
    L.append("")
    L.append(f"`code/verify142.py` re-checks all of it with a SECOND implementation (edge "
             f"crossing + strict point-in-polygon; no separating axis anywhere in the file): "
             f"{t['A_cols']} red-dashed columns over {t['A_poses']} poses ({t['A_fail']} "
             f"failures); {t['B_cols']} non-flagged control columns, each shown disjoint at some "
             f"pose of every box ({t['B_fail']}); {t['C_pins']} exact pin cores contained in "
             f"their pin square over {t['C_poses']} poses ({t['C_fail']}); {t['D_verts']} K'(B) "
             f"vertices contained over {t['D_poses']} poses ({t['D_fail']}); {t['E_rects']} "
             f"clipped rects inside the original box ({t['E_fail']}). **Total failures: "
             f"{vf['n_failures']}.**")
    L.append("")
    L.append("Two caveats of record. (1) Lane counts on these pages are **A118's stored "
             "AXIS-CORE verdicts** (K(a), not K'): A141's K' lane run had not landed when the "
             "pages were drawn, so a corner marked UNDECIDED here may still become LANE<=1 under "
             "K' - exactly the s3_far effect the PI read on the Part III page. (2) A pocket is "
             "an exact convex-polygon DISTANCE, hence a measurement the reading can use, not a "
             "proof that nothing fits: the proof is the lane leaf.")
    L.append("")
    with open(DOC, "a", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("appended Part IV to", DOC)


if __name__ == "__main__":
    main()
