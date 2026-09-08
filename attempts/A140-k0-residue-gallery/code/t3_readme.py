"""A140 T3 -- the one-table summary for the PI (docs/shadows/k0v3/README.md) and the Part III
pointer appended to docs/shadows.md.

docs/shadows.md is APPEND-ONLY here: an existing "# Part III" section written by this script is
replaced, nothing before it is touched.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import cells140 as C140                                       # noqa: E402

OUT = os.path.join(ROOT, "docs", "shadows", "k0v3")
SHAT = C140.SHAT
S0 = C140.S0

NOSHADOW = {"l1_124", "l1_153", "l1_158"}       # no A107 gallery entry under ANY alias


def _exs(r):
    """The exact-core arm's verdict for one cell, for the README table."""
    e = r.get("exact") or {}
    if not e or e.get("tau") is None:
        return "not run"
    c = e.get("cert") or {}
    if c.get("result") == "PASS":
        return ("**CERTIFIED DEAD** — tau %.4f of %d, converged, FROZEN verify_case PASS "
                "(`certs/%s`)" % (e["tau"], e["budget"], c["cert"]))
    if c.get("result"):
        return "converged kill, certificate %s (`certs/%s`)" % (c["result"], c.get("cert"))
    if e.get("kills"):
        return ("kill candidate — tau %.4f of %d, unconverged after 240+900 s"
                % (e["tau"], e["budget"]))
    return "alive — tau %.4f = budget%s" % (e["tau"], ", converged" if e.get("converged") else
                                            ", unconverged at cap")


def pi_reading(g):
    """What the PI's reading would decide, for each cell."""
    iv = g.get("invitro") or {}
    cov = g["cover"]
    bits = []
    if iv.get("kills_converged"):
        bits.append("**the polygon core already kills it in vitro, converged** — the reading "
                    "needed is "
                    "whether the K' row filter is worth a verifier change (A135 route: the exact "
                    "axis core is inside the frozen schema and removes "
                    f"{g['support']['w_exact_only']:.2f} of the {g['support']['w_poly_only']:.2f} "
                    "excluded weight)")
    elif iv.get("kills"):
        bits.append("**the polygon core drops tau below budget but the LP has not converged at "
                    "the 240 s cap** — a warm continuation, not a reading, is the next step "
                    f"(the excluded weight is {g['support']['w_poly_only']:.2f}, of which "
                    f"{g['support']['w_exact_only']:.2f} is inside the frozen schema)")
    elif iv.get("tau") is not None:
        bits.append("K' alone does not kill it (the LP replaces the excluded columns), so the "
                    "reading has to name a structural obstruction, not a column count")
    if cov["kind"].startswith("two-meeter"):
        bits.append(f"the cover is decided by geometry already: {cov['cell']} admits at most one "
                    "non-conditioned meeter, so the PI only has to confirm the 'conditioned "
                    "square meets it' arm is a real sub-box")
    else:
        bits.append(f"the PI's call is which slot to re-branch on — the support leans on "
                    f"{cov['cell']}, but the load path in panel 2 may name a different one")
    return "; ".join(bits) + "."


def main():
    g = json.load(open(os.path.join(BASE, "results", "gallery140.json"), encoding="utf-8"))
    ex = {}
    exp = os.path.join(BASE, "results", "exactcore140.jsonl")
    if os.path.exists(exp):
        for ln in open(exp, encoding="utf-8"):
            if ln.strip():
                r = json.loads(ln)
                ex[r["cell"]] = r
    for r in g:
        r["exact"] = ex.get(r["cell"], {})
    t1 = json.load(open(os.path.join(BASE, "results", "t1_polycore.json"), encoding="utf-8"))
    A = []
    a = A.append
    a("# The k0 residue gallery, v3 — the twelve converged-alive k0_00 cells\n")
    a("A140 (2026-09-07).  One page per cell, in the two-panel form the PI reviewed for A107's "
      "K-gallery (`docs/shadows.md` Part II), redrawn with the drawing rules of 2026-09-07 and "
      "carrying two objects the gallery has never shown: the **polygon core K'(B)** (A132) and "
      "the cell's **candidate cover**.\n")
    a("The twelve cells are A115 T6's hand-off list (`attempts/A115-k0-corner-rows/notes/"
      "t6_report.md`): tau = budget exactly, minmass 1.000, `converged = True` — the case-LP has "
      "reached its optimum and it is not below budget, so **no amount of further LP time kills "
      "them**.  Every page is drawn from A115's own converged record "
      "(`attempts/A115-k0-corner-rows/results/nodes/<nid>.t{4,5}.lp.json`), not from the A38/A99 "
      "record the cell was first seen in.\n")
    a("**k0_00 has no pins.**  Every hypothesis core of a k0 node IS a conditioned square, so the "
      "T5 pin-vs-box kill has no analogue; the only geometric kills available are column "
      "exclusion by K', K' leaving the container, and (where a cell carries more than one "
      "conditioned square) K' meeting K'.\n")
    a("## The table\n")
    a("| cell | level | s\\* of the right panel | shadow family | polycore status (T1) | "
      "in-vitro LP under K' | candidate cover | what the PI's reading would decide |")
    a("|---|---|---|---|---|---|---|---|")
    for r in g:
        iv = r.get("invitro") or {}
        sup = r["support"]
        src2 = ("A107 shadow" if r["prov"].startswith("A107")
                else ("A128 near-packing" if r["prov"].startswith("A128") else "raw support"))
        fam = (f"{r['shadow']} (panel 2: {src2})" if r["shadow"]
               else f"**none** (panel 2: {src2})")
        sst = (f"{r['s_star']:.6f} ({r['s_star'] - SHAT:+.6f} vs s-hat)"
               if r.get("panel2_is_packing", True)
               else f"n/a — panel 2 is the raw support at s0, overlap {-r['panel2_min_sat']:.3f}")
        ivs = ("**tau %.4f, CONVERGED — LP-dead under polygon core, certificate pending**"
               % iv["tau"] if iv.get("kills_converged")
               else ("tau %.4f < %d but unconverged at the cap — **kill candidate**"
                     % (iv["tau"], r["budget"]) if iv.get("kills")
                     else ("tau %.4f = budget (no kill)" % iv["tau"]
                           if iv.get("tau") is not None else "not run")))
        a(f"| **{r['cell']}**{' *(Trump image)*' if r['cell'] == 'l1_153' else ''} | "
          f"{r['level']} | {sst} | {fam} | "
          f"K' meets {sup['n_poly']} of {sup['n']} support columns (K(a) meets 0), weight "
          f"{sup['w_poly_only']:.3f} of {sup['w']:.1f} vs slack {r['slack']:+.1e}; exact-core "
          f"part {sup['w_exact_only']:.3f} | {ivs} | {_exs(r)} | {r['cover']['kind']} on "
          f"{r['cover']['cell']} | {pi_reading(r)} |")
    a("")
    a("## The three cells that had no drawing before\n")
    a("A107's gallery was built before A115's last pass, from the A38/A99 records.  Three of the "
      "twelve appear in it under **no alias at all** — A38 has no node json for them (they were "
      "in A115's `notrun` pool) and A99 never produced a `plain_warm` record for them:\n")
    for c in sorted(NOSHADOW):
        r = [x for x in g if x["cell"] == c][0]
        a(f"* **`{c}`**{' — the Trump-image cell (A38 l1 idx 153); it must stay alive' if c == 'l1_153' else ''}"
          f" — right panel: {r['prov'].split(';')[0]}.")
    a("")
    a("One correction to the brief: `l1_148` DOES have an A107 entry — its unconverged A99 alias "
      "`l1_148_plain_warm` sits in **K01** — while `l1_153` has none.  The cells A128 built "
      "near-packings for (`l1_124`, `l1_148`, `l1_158`) and the cells with no gallery entry "
      "(`l1_124`, `l1_153`, `l1_158`) are different sets.\n")
    a("## Files\n")
    a("| file | what |")
    a("|---|---|")
    for r in g:
        a(f"| [`{r['cell']}.svg`]({r['cell']}.svg) | {r['cell']}: LP dual support with K' and "
          f"{r['n_impossible']} impossible column(s); panel 2 at "
          + (f"s\\* = {r['s_star']:.6f}" if r.get("panel2_is_packing", True)
             else "s0 (raw support, not a packing)")
          + f"; the {r['cover']['kind']} cover on {r['cover']['cell']} |")
    a("| [`review_k0v3.csv`](review_k0v3.csv) | review.csv's columns plus `polycore_status`, "
      "`candidate_cover`, the k0v3 measurements, and empty `PI_*` columns |")
    a("")
    a("## How to read a page\n")
    a("* **LEFT** — the LP dual support of the converged record.  Fill = the dual weight y on one "
      "sequential scale (pale yellow y→0, dark orange y=1).  Bright cyan + heavy black outline + "
      "**H** = a conditioned square, drawn at the **centre of its box** and the **centre of its "
      "tilt window**; the faint cyan outlines are the same square at the two **extremal tilts**.  "
      "Purple = the certified **polygon core K'(B)**.  Red dashed = a support column that "
      "overlaps a hypothesis square at **every** pose of its box — impossible under the node's "
      "own hypothesis, kept by the LP only because the LP prunes against the axis core K(a).\n")
    a("* **RIGHT** — a real packing with the square names the PI labels from: blue = slot square "
      "(named corner cell), red = free square (f-index + tilt), green ring = a contact at "
      "gap < 1e-6.  Source is stated in the subtitle: A107's minimised shadow, A128's polished "
      "near-packing, or the raw integral dual support at s0.\n")
    a("* **Three cores are drawn inside each H**, and they are three different objects: SOLID "
      "BLACK = the **stock axis core K(a)** the LP actually pruned against (the record's own "
      "`a`); SOLID TEAL = **A135's exact axis core**, the largest half-side at the same "
      "(kx, ky, tm) that passes the exact rational vertex test — still a square at the box's own "
      "tilt, so the frozen certificate schema is unchanged and a kill from it is certifiable "
      "today; PURPLE FILL = the **polygon core K'(B)**, the full intersection of the square over "
      "the box, which needs a verifier change.  The panel caption prints `a_stock`, `a_exact` and "
      "the area of K'.  Each red-dashed column's label gives its depth against all three and says "
      "which core would drop it.\n")
    a("* **THIRD** — the candidate cover.  Amber = the cell to branch on.  Thin green dashed "
      "outlines are **slot-census BINS, not squares of a packing**: every dual-support column is "
      "assigned to exactly one bin (the nearest slot centre), so the printed `w=` weights "
      "**partition** the support's total dual weight and never double count.  `(H)` marks a bin a "
      "conditioned square could itself reach; the conditioned square is never a dual-support "
      "column, because the node LP counts only the budget = 11 − #cores other squares.  The "
      "separate `met` census under the panels is the geometric statement (a column can overlap "
      "several cells) — that one is A113's singly/doubly-met count and is *not* a partition.\n")
    a("* Under the panels: the box(es), tau / eta / minmass, the T1 polygon-core measurement, the "
      "slot census (A113), the lane count (A118), the cover in words with what it needs to be a "
      "certified leaf, and the geometry check.\n")
    # ---------------------------------------------------------------- exact-core arm
    cert = [r for r in g if ((r.get("exact") or {}).get("cert") or {}).get("result") == "PASS"]
    cfail = [r for r in g if ((r.get("exact") or {}).get("cert") or {}).get("result")
             not in (None, "PASS")]
    cand = [r for r in g if (r.get("exact") or {}).get("kills")
            and not ((r.get("exact") or {}).get("cert") or {}).get("result")]
    alv = [r for r in g if (r.get("exact") or {}).get("tau") is not None
           and not (r.get("exact") or {}).get("kills")]
    cpu = sum((r.get("exact") or {}).get("wall_s", 0.0) for r in g)
    a("## The exact-core arm — the only kill here that is certifiable TODAY\n")
    a("A135's `exactcore.exact_a` returns the largest rational half-side `a` at the box's own "
      "`(kx, ky, tm)` whose four corners pass A132's exact rational vertex test.  It is still a "
      "**square at the box's own tilt**, so it fits the FROZEN certificate schema "
      "`{kx, ky, tm, a}` verbatim — `verify_case.py` reads `a` straight out of the file and never "
      "re-derives it from the box.  Unlike the polygon core, a kill from this arm needs **no "
      "verifier change**.  One re-solve per cell with the exact cores as the row filter (240 s, "
      "then a 900 s warm continuation where tau was below budget but unconverged); every "
      f"converged kill certified through the frozen `verify_case.py`.  {cpu / 3600.0:.2f} CPU-h, "
      "2 BelowNormal processes.\n")
    a("| cell | a_stock → a_exact (area gain) | tau / budget | converged | verdict | certificate |")
    a("|---|---|---|---|---|---|")
    for r in sorted(g, key=lambda r: (not (r.get("exact") or {}).get("kills"), r["cell"])):
        e = r.get("exact") or {}
        if e.get("tau") is None:
            a(f"| `{r['cell']}` | - | - | - | not run | - |")
            continue
        c = e.get("cert") or {}
        ar = ", ".join(f"{a0:.6f} → {ax:.6f} ({rt:.3f}x)" for a0, ax, rt
                       in zip(e["a_stock"], e["a_exact"], e["area_ratio"]))
        vd = ("**CERTIFIED DEAD**" if c.get("result") == "PASS" else
              ("converged kill, cert " + c["result"] if c.get("result") else
               ("kill candidate (unconverged)" if e.get("kills") else "alive")))
        cc = (f"`certs/{c['cert']}` — {c['result']}, total {c['total']:.6f} < {c['budget']}, "
              f"verifier {c.get('verify_s')} s" if c.get("result") else "-")
        a(f"| `{r['cell']}` | {ar} | {e['tau']:.6f} / {e['budget']} | {e['converged']} | {vd} | "
          f"{cc} |")
    a("")
    a(f"**SURVIVOR COUNT.  {len(cert)} certified dead, {len(cfail)} cert-FAIL, {len(cand)} kill "
      f"candidates (below budget, unconverged after 240 + 900 s), {len(alv)} alive.  The "
      f"converged-alive k0_00 residue drops from {len(g)} to {len(g) - len(cert)} cells**"
      + (" — `" + "`, `".join(r["cell"] for r in cert) + "` "
         + ("is" if len(cert) == 1 else "are") + " now dead under the FROZEN verifier, with the "
         "exact axis cores written into the certificate and nothing else changed."
         if cert else ".") + "\n")
    if cand:
        a("The " + str(len(cand)) + " kill candidates (" +
          ", ".join(f"`{r['cell']}`" for r in cand) + ") are below budget but the LP had not "
          "converged at 240 + 900 s; a longer warm continuation is what would settle them, and "
          "each would then certify the same way.\n")
    a("## The two levers, and how they split the twelve\n")
    kills = [r["cell"] for r in g if (r.get("invitro") or {}).get("kills")]
    conv = [r["cell"] for r in g if (r.get("invitro") or {}).get("kills_converged")]
    tm = [r["cell"] for r in g if r["cover"]["kind"].startswith("two-meeter")]
    a(f"* **Polygon core.**  In vitro, K' drops tau below budget on {len(kills)} of {len(g)}: "
      + ", ".join(f"`{c}`" for c in kills) + f".  Of those, {len(conv)} also CONVERGED below "
      f"budget (" + ", ".join(f"`{c}`" for c in conv) + ") and is LP-dead under the polygon core; "
      "the rest are `dead_unconverged` kill candidates at the 240 s cap.\n")
    a(f"* **Lane count.**  {len(tm)} of {len(g)} carry a corner cell with LANE <= 1: "
      + ", ".join(f"`{c}` ({[x for x in g if x['cell'] == c][0]['cover']['cell']})"
                  for c in tm) + ".  Three of these verdicts (`l1_124`, `l1_153`, `l1_158`) are "
      "NEW — A118 never saw those cells.\n")
    both = [c for c in tm if c in kills]
    neither = [r["cell"] for r in g
               if r["cell"] not in kills and not r["cover"]["kind"].startswith("two-meeter")]
    a("* The two levers **partition the residue almost exactly**: "
      + (", ".join(f"`{c}`" for c in both) + " is in both"
         if both else "no cell is in both") + ", and "
      + ((", ".join(f"`{c}`" for c in neither) + " " + ("is" if len(neither) == 1 else "are")
          + " in neither — that is where a genuinely new reading is needed") if neither else
         "every one of the twelve is in at least one bucket, so none is without a concrete route")
      + ".\n")
    a(f"* **Exact core (certifiable today).**  {len(cert)} of {len(g)} certified dead through the "
      f"FROZEN verifier, {len(cand)} more below budget but unconverged: "
      + ", ".join(f"`{r['cell']}`" for r in cert + cand) + ".  This is the only lever of the "
      "three whose kills need no change to `verify_case.py`.\n")
    a("## Provenance and soundness\n")
    a("* Every K' is A132's **certified** polygon (exact rational vertex test, "
      "`polycore.vertex_ok`); the half-side of the exact axis core is A135's `exactcore.exact_a`, "
      "certified the same way.\n")
    a("* An in-vitro kill is **not** a certificate: the frozen verifier knows only K(a).  The "
      "A135 exact axis core IS a square at the box's own tilt and therefore fits the frozen "
      "schema, so the `exact-core part` column is the weight a kill could claim **today**; the "
      "rest needs the v3 verifier.\n")
    a("* Every drawn square is containment-checked, and every red-dashed column's overlap is "
      "re-verified by an independent SAT implementation at 7³ = 343 poses of its box.\n")
    a("* Read-only on every campaign; the only files written are under "
      "`attempts/A140-k0-residue-gallery/` and `docs/shadows/k0v3/`, plus this Part III pointer "
      "in `docs/shadows.md`.\n")
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write("\n".join(A))

    # ---------------------------------------------------------------- Part III in docs/shadows.md
    B = []
    b = B.append
    b("")
    b("# Part III - the k0 residue gallery v3 (A140)\n")
    b("Part II above is the A107 K-gallery of the k0_00 class, built from the A38/A85/A99 records "
      "BEFORE A115's last pass.  A115 T6 has since reduced the k0_00 residue to **exactly twelve "
      "converged-alive cells** (tau = budget, minmass 1.000, converged - no LP time kills them):")
    b("`l1_071`, `l1_104`, `l1_124`, `l1_148`, `l1_153` (a Trump image, must stay alive), "
      "`l1_158`, `l1_159`, `l2_p114_001`, `l2_p65_101`, `l2_p65_111`, `l2_p74_001`, "
      "`s3_far_BL389484_TR018470`.\n")
    b("**[docs/shadows/k0v3/](shadows/k0v3/README.md)** is one page per cell in the reviewed "
      "two-panel form, redrawn with the 2026-09-07 drawing rules and carrying the polygon core "
      "K'(B) and the cell's candidate cover.  A fresh review sheet is "
      "`docs/shadows/k0v3/review_k0v3.csv`.\n")
    b("| cell | level | s* of the right panel | Part II family | in-vitro LP under K' | "
      "candidate cover |")
    b("|---|---|---|---|---|---|")
    for r in g:
        iv = r.get("invitro") or {}
        fam = r["shadow"] or "none"
        sst2 = (f"{r['s_star']:.6f}" if r.get("panel2_is_packing", True)
                else "s0 (raw support)")
        ivs = ("**dead (converged), cert pending** (tau %.4f)" % iv["tau"]
               if iv.get("kills_converged")
               else ("kill candidate (tau %.4f, unconverged)" % iv["tau"] if iv.get("kills")
                     else ("no kill (tau %.4f)" % iv["tau"] if iv.get("tau") is not None else "-")))
        b(f"| [`{r['cell']}`](shadows/k0v3/{r['cell']}.svg) | {r['level']} | "
          f"{sst2} | {fam} | {ivs} | {r['cover']['kind']} on {r['cover']['cell']} |")
    b("")
    nk = sum(1 for r in g if (r.get("invitro") or {}).get("kills"))
    nkc = sum(1 for r in g if (r.get("invitro") or {}).get("kills_converged"))
    b(f"The polygon core K'(B) meets dual-support columns the axis core K(a) misses on **all "
      f"twelve** cells (A132's measurement, run on k0 for the first time); one in-vitro re-solve "
      f"per cell (240 s cap) with the column pool pruned by K' drops tau below budget on **{nk} "
      f"of {len(g)}**.  On **{nkc}** of those the LP also CONVERGED there, which is LP-dead under "
      f"the polygon core with the certificate pending (the frozen verifier knows only K(a)); the "
      f"other {nk - nkc} are A57's `dead_unconverged` -- kill candidates a warm continuation "
      f"would settle.  The measurement, per cell and per box, is "
      f"`attempts/A140-k0-residue-gallery/results/t1_polycore.json`; the same scan over all 166 "
      f"OPEN k0 cells A115 lists finds K'-excluded dual weight on every one (median 2.02).\n")
    b(f"**The one result here that is certifiable TODAY.**  A135's EXACT axis core "
      f"(`exactcore.exact_a`) is still a square at the box's own tilt, so the frozen certificate "
      f"schema `{{kx, ky, tm, a}}` is unchanged and `verify_case.py` reads `a` verbatim.  One "
      f"re-solve per cell with the exact cores as the row filter (240 s, then 900 s warm where "
      f"tau was below budget but unconverged), {cpu / 3600.0:.2f} CPU-h: **{len(cert)} certified "
      f"dead, {len(cfail)} cert-FAIL, {len(cand)} kill candidates, {len(alv)} alive** -- the "
      f"converged-alive k0_00 residue drops from {len(g)} to {len(g) - len(cert)} cells."
      + (" `" + "`, `".join(r["cell"] for r in cert) + "` passed the FROZEN verifier "
         + "(" + "; ".join("total %.6f < %d, %s s"
                           % (((r["exact"]["cert"])["total"]), (r["exact"]["cert"])["budget"],
                              (r["exact"]["cert"]).get("verify_s")) for r in cert)
         + "); certificates in `attempts/A140-k0-residue-gallery/certs/`."
         if cert else "") +
      (" Kill candidates: `" + "`, `".join(r["cell"] for r in cand)
       + "` -- below budget, LP not converged at 240 + 900 s." if cand else "") + "\n")
    n2 = sum(1 for r in g if r["cover"]["kind"].startswith("two-meeter"))
    b(f"Second result, independent of the LP: A118's lane count was never run on `l1_124`, "
      f"`l1_153` or `l1_158` (A38 has no node json for them, so they were not in A118's corpus).  "
      f"Re-running A118's own `lane.run_cell` unchanged gives **TR(0,0) LANE <= 1** on all three; "
      f"with `l1_159`'s TR(0,0) and `s3_far`'s BL(0,0), **{n2} of {len(g)}** cells now carry a "
      f"two-meeter cover whose geometric half is already certified.  None is a kill on its own "
      f"(the conditioned square can itself reach the cell, so the meeter count is <= 2 and "
      f"K0-FREE does not fire directly) -- each is a two-child cover: the conditioned square "
      f"meets the cell (shrink its box, re-solve) or it does not (the cell is met by <= 1 square "
      f"and K0-FREE teleports into k1).  Per-cell verdicts: "
      f"`attempts/A140-k0-residue-gallery/results/lane140.json`.\n")
    p = os.path.join(ROOT, "docs", "shadows.md")
    cur = open(p, encoding="utf-8").read()
    cut = cur.find("\n# Part III - the k0 residue gallery v3")
    if cut >= 0:
        cur = cur[:cut]
    open(p, "w", encoding="utf-8").write(cur.rstrip("\n") + "\n" + "\n".join(B))
    print("wrote", os.path.join(OUT, "README.md"), "and Part III in docs/shadows.md")


if __name__ == "__main__":
    main()
