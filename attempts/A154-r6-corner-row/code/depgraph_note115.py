"""Append A115's one-line note to the depgraph K0.CW node (owner field untouched).
Usage: python depgraph_note115.py   (edits lean/depgraph.json in place, utf-8, nothing else)."""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
T3 = os.path.join(HERE, "..", "results", "t3.json")

t3 = json.load(open(T3))
cells = t3["n_cells"]
kills = t3["price"]["certified"]
att = t3["price"]["n_cert"]
mean_c = {k: v.get("mean_c") for k, v in t3["cfg"].items()}
meanB = {k: v.get("mean_B") for k, v in t3["cfg"].items()}
lp_s = t3["price"]["mean_lp_s_per_cell_cfg"]

NOTE = ("A115 (2026-09-06, measurement, attempts/A115-k0-corner-rows): Lemma CW's corner rows at "
        "the NODE level of the k0_00 tree, on %d alive K01 cells x delta in {0, 0.05, 0.1} (108 "
        "LPs), certify %d of %d cells they were attempted on and only ONE of those is "
        "ATTRIBUTABLE to the rows (l3_pp65_111_000 at delta = 0, a level-3 cell: the plain node "
        "certificate FAILS at the same LP wall, results/control.jsonl); ZERO of the cells that "
        "were genuinely alive at the LP (eta0 >= 0) died at any delta. "
        "The A109 multiplicity failure mode is IMPOSSIBLE here (the four "
        "widened corner boxes are s0 - 2 a_w = 1.826 > sqrt2 apart, so a unit square carries at "
        "most one incidence and B = 8 - sum r_max(B+) in {7,8} is exact); the rows fail for the "
        "opposite reason -- the guaranteed budget 8 is BELOW what a packing at s0 achieves for "
        "free. EXACT: every D4 image of Trump realises 9 corner incidences at a_w(0) = 1.025520 "
        "(per-corner counts 3/2/2/2, the tangent squares sit at mu_c = 1 exactly, inside the "
        "K0-WIDEN box), so at delta = 0 the achievable crowd mass is >= 9 > 8 = B and the ROOT LP "
        "can never pass; at the node level the LP's own fractional packing realises mean c = %s "
        "(d0) / %s (d0.05) / %s (d0.1) against mean B = %s -- c >= B in 100 of 101 measured runs, "
        "and by the convexity rule (tau(e) convex in e => c(e) non-decreasing) no e can kill. At "
        "delta = 0.05 / 0.1 no Trump image realises the hypothesis (counts 1/1/2/1, total 5), so "
        "the canary is vacuous there and the refusal is purely the LP's. Price: %.0f s per (cell, "
        "delta) corner-row re-solve. T1: all four corner cells of all 84 K01 shadows are met, "
        "never empty -- the 'room' is always a SINGLE deep meeter (TL singly met in 70 of 84, BL "
        "57, TR 50, BR 35; the meeter's depth is >= 0.30 in 296 of 486 incidences), which is "
        "exactly the K0-FREE teleport hypothesis and NOT something the crowd rows can price."
        % (cells, kills, att,
           ("%.2f" % mean_c.get("d0")) if mean_c.get("d0") else "n/a",
           ("%.2f" % mean_c.get("d0.05")) if mean_c.get("d0.05") else "n/a",
           ("%.2f" % mean_c.get("d0.1")) if mean_c.get("d0.1") else "n/a",
           ("%.2f" % (sum(v for v in meanB.values() if v) / max(1, len([v for v in meanB.values() if v])))),
           lp_s))

g = json.load(io.open(P, encoding="utf-8"))
byid = {n["id"]: n for n in g["nodes"]}
if "K0.CW" not in byid:
    print("K0.CW node absent -- nothing done")
    sys.exit(1)
if NOTE[:60] in (byid["K0.CW"].get("note") or ""):
    print("note already present")
    sys.exit(0)
byid["K0.CW"]["note"] = (byid["K0.CW"].get("note", "") + " || " + NOTE)
json.dump(g, io.open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("depgraph K0.CW note appended (A115); owner field unchanged: %r"
      % byid["K0.CW"].get("owner"))
