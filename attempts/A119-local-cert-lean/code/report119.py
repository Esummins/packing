"""A119 -- build notes/t1_table.md and notes/t3_table.md from the results (idempotent)."""
from __future__ import annotations
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
CERTS = os.path.join(BASE, "certs")
NOTES = os.path.join(BASE, "notes")


def t1():
    man = json.load(open(os.path.join(CERTS, "manifest.json"), encoding="utf-8"))
    chk = {}
    p = os.path.join(RES, "check_local.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        for r in (d.get("previous") or [])[::-1] + d["runs"]:   # newest wins
            chk[r["id"]] = r
    out = ["# A119 T1 — the exact certificates and the independent checker", "",
           "Generator `code/exact119.py` (float LP + rational rounding of the multipliers to a",
           "denominator of 2^40, each vector re-verified by weak duality before it is written);",
           "checker `code/check_local.py` (no numpy, no scipy, no tree code — dyadic interval",
           "arithmetic on Python ints at scale 2^-96, `code/exactiv.py`).  `s0 = 969271/250000`.",
           "",
           "| certificate | cells (bisections) | selection branches | infeasible cells | dead leaves | multipliers | file | sha256 | gen wall | checker wall | checker's min bound | verdict |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for cid in sorted(man):
        m = man[cid]
        nc = m["node_counts"]
        c = chk.get(cid, {})
        cc = c.get("counts", {})
        out.append("| `%s` | %d | %d | %d | %d | %d | %.1f MB | `%s` | %s s | %s s | %s | %s |" % (
            cid, nc.get("bisect", 0), nc.get("branch", 0),
            cc.get("infeas", 0) + cc.get("imp", 0) + cc.get("imp_sel", 0),
            nc.get("dead", 0), nc.get("mult", 0), m["bytes"] / 1e6, m["sha256"][:16],
            m["seconds_tree"], c.get("seconds", "-"),
            ("%.9f" % c["certified_min"]) if c.get("certified_min") else "-",
            "**VALID**" if c.get("ok") else ("INVALID " + (c.get("errors") or [""])[0][:80] if c else "not checked")))
    out += ["", "## What one certificate contains", "",
            "* `meta`: the bodies (each free body's centre box and tilt interval, each pin's",
            "  `(alpha, beta, h)` slack core, the LP variable indices), the side window, the tilt",
            "  cut, `s0` as the exact fraction `969271/250000`, and the kill margin `1e-8`.",
            "* `root`: the proof tree.  `bisect` nodes split one body's tilt interval at a recorded",
            "  point (the two children cover it); `branch` nodes list the selections their children",
            "  assume for one near pair (the checker verifies every OTHER selection has",
            "  `sup [g] < 0` on the cell, so Lemma SAT leaves no third case); `qsplit` nodes would",
            "  split a q-range (NONE occurs — see `notes/method.md` finding F1); `imp` / `imp_sel`",
            "  leaves are cells where some pair has no possible selection at all; `dead` leaves",
            "  carry the selections the multipliers use, which of them are FORCED rather than",
            "  supplied by a branch, and the rational Farkas vector — a value `> s0` for a bounded",
            "  leaf, a Farkas RAY (`infeas: true`) for an infeasible cell.",
            "* `certs/manifest.json`: sha256, size, node counts and the generator's own certified",
            "  minimum per file.",
            "",
            "## What the checker does (and does not) trust", "",
            "It trusts the certificate for NOTHING except the shape of the search: it rebuilds every",
            "row of Lemma RELAX itself, from the cell and the boxes, in exact dyadic interval",
            "arithmetic (rigorous `pi`, `cos`, `sin`, and the EXACT range of `|cos| + |sin|`), it",
            "verifies every excluded selection's enclosure itself, and it evaluates the Farkas bound",
            "itself.  A multiplier vector is data; a wrong one simply fails.  The checker shares no",
            "code with the generator and imports neither numpy nor scipy nor any tree module.", ""]
    open(os.path.join(NOTES, "t1_table.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote notes/t1_table.md (%d certificates)" % len(man))


def t3():
    rows = []
    for p in sorted(glob.glob(os.path.join(RES, "t3_*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            t = d["tree"]
            st = t["stats"]
            rows.append((d["tag"], d["cls"], d["r"], d["rho"], d["cut"], d["label"],
                         d.get("slot_radius"), len(d["loadbearing"]),
                         "DEAD" if t["dead"] else ("CAP" if t["capped"] else "ALIVE"),
                         st["nodes"], st["lp_calls"], t["n_near"], t["n_closed"],
                         t["certified_min"], (d.get("local_min") or {}).get("side"),
                         (d.get("sampling") or {}).get("hits"), d["trump"]["inside"],
                         d["seconds_tree"], d.get("n_witnesses", 0),
                         (d.get("witnesses") or [{}])[0].get("witness_side")))
    rows.sort()
    out = ["# A119 T3 — the blocking squares as boxes, and the ρ ≥ 20° cap", "",
           "| shadow/frame | r | ρ | cut | L | boxes | verdict | nodes | LP calls | near pairs | closed | certified min | measured min | sample hits | Trump in N | wall | witness |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for q in rows:
        out.append("| %s/%s | %.2f | %.0f° | %s | %s%s | %d | **%s** | %d | %d | %d | %d | %s | %s | %s | %s | %.0f s | %s |" % (
            q[0], q[1], q[2], q[3], q[4] if q[4] is not None else "—", q[5],
            "" if q[6] is None else " (slot %.2f)" % q[6], q[7], q[8], q[9], q[10], q[11], q[12],
            ("%.6f" % q[13]) if q[13] else "—", ("%.6f" % q[14]) if q[14] else "—",
            "—" if q[15] is None else q[15], q[16], q[17],
            ("%.6f" % q[19]) if q[19] else ("%d found" % q[18] if q[18] else "—")))
    out += ["", "(`wall` is the TREE's wall clock; a DEAD verdict then costs a further 10⁴-sample",
            "check + 30-start SLSQP + the Trump canary.  `L` names the run's label; `boxes` is the",
            "number of FREE bodies, i.e. the number of tilt dimensions the tree must bisect.)", "",
            "## (a) The blocking squares as boxes do NOT extend the radius", "",
            "S02 gets `f0` and `TR(0,0)`, S07 gets `f1`, `f3` and `BL(0,2)` — the squares A116",
            "identified as the ones that would forbid the r = 0.3 rearrangement.  They are the right",
            "objects (see (c)) and they cost two extra tilt dimensions: 16–23 near pairs instead of",
            "10–13, and 6 tilt intervals to bisect instead of 3–4.  **Exactly one blocking-box N",
            "closes: S02 (0.1, 5°), DEAD in 121 s of tree (58 447 nodes, 29 384 closed leaves),",
            "certified 3.877101, measured 3.886746, 0 hits in 10⁴ samples, Trump outside** — and it is",
            "a strictly LARGER N than A116's own six-box run, which had to confine the slot square",
            "`BR(0,1)` to a 0.05 box.  Every other blocking-box cell (r ≥ 0.2, or ρ ≥ 10°, either",
            "shadow) hits the 900–1200 s cap with 320 000–460 000 nodes.  For S07 no blocking-box N",
            "closes at all.  **So A116's (0.2, 10°) and (0.1, 40°) with the ORIGINAL L remain the",
            "largest certified neighbourhoods, and the blocking-box route trades radius for tilt",
            "dimensions at a loss.**", "",
            "## (b) The ρ ≥ 20° frontier at r = 0.2 is ALIVE, not capped", "",
            "A116 tabulates CAP at S02 (0.2, 20°) / (0.2, 40°) and S07 (0.2, 20°) / (0.2, 40°) and",
            "reads them as \"no witness and no dip were found there, so those cells are open, not",
            "dead\" (§5).  That reading is wrong, and for S07 **A116's own results file already",
            "contains the refutation**: `t2_S07.jsonl` records 4 128 witnesses at (0.2, 20°) and",
            "1 733 at (0.2, 40°), the first of each with `witness_valid: true` (worst pair gap",
            "−4.4·10⁻¹⁶, worst wall gap 0) at sides 3.873374 and 3.869626 — checked packings of L ∪ P",
            "below s0 — while the run's verdict field says `capped`.  (Re-running A116's own tree",
            "TODAY with A116's own parameters returns ALIVE with the same witness in 25 s and 4 899",
            "nodes: `code/f1probe.py`, `results/f1_probe.json`.  The stored rows were evidently",
            "produced before `Tree._loop`'s \"return on the first checked witness\" existed, so the",
            "ALIVE verdict never reached the table.)  The same mislabelling affects A116's",
            "(0.3, 20°) and (0.3, 40°) rows in both shadows.", "",
            "| N (original L) | A116 as tabulated | what is in A116's data | A119, independently | witness side |",
            "|---|---|---|---|---|",
            "| S07 (0.2, 20°), cut 41.565° | CAP, 107 796 nodes | 4 128 witnesses, first VALID | **ALIVE at node 917, 2 s** | 3.873374 (f0, f2, f4 all at 65°: the ladder shears) |",
            "| S07 (0.2, 40°), cut 41.565° | CAP, 119 048 nodes | 1 733 witnesses, first VALID | **ALIVE, 4 769 nodes, 9 s** | 3.869626 (the same at 68.7°) |",
            "| S02 (0.2, 40°) | CAP, 259 684 nodes | **0 witnesses** | **ALIVE, 392 144 nodes, 559 s** | 3.876703 — NEW (f3 turns to 88.3°, f1 to 12.2°, f2 to 8.4°) |",
            "| S02 (0.2, 20°) | CAP, 138 451 nodes | 0 witnesses | CAP, **633 660 nodes** (4.6× the nodes in the same wall) | still genuinely open |",
            "",
            "So **the S07 tilt radius at r = 0.2 is below 20°, and the S02 tilt radius at r = 0.2 is",
            "below 40°** — not for want of budget but because the |L| + |P| squares really do",
            "rearrange there.  The one cell that is merely capped is S02 (0.2, 20°).",
            "", "## (c) The blocking squares DO kill those rearrangements", "",
            "Re-running the three ALIVE cells with the blocking squares added as boxes finds NO",
            "witness in 900 s and 320 000–450 000 nodes (verdict CAP, not ALIVE), and on S02",
            "(0.2, 40°) the certified minimum over the CLOSED part of the tree rises from 3.877567 to",
            "**3.881900** — well clear of s0.  The blocking squares are therefore the right objects;",
            "what stops the proof is the tilt-cell count of a six-body tree, not the geometry.",
            "", "## (d) The consumer count is unchanged", "",
            "`code/consumer119.py` (a bipartite MATCHING instead of A116's 11 P |L| brute force —",
            "same answer, and it terminates for |L| = 6) reproduces A116's table exactly:",
            "**72 of 184 k5_11 + 23 of 68 k5_16 = 95 of the 252 S02-explained alive nodes** at",
            "A116's (0.2, 10°) / (0.1, 10°), 2 of 18 for S07 at (0.1, 40°).  A119's new certified N,",
            "S02 (0.1, 5°) with the blocking boxes, catches **1 of 184** — the supports do not hold",
            "`f0` and `TR(0,0)` at the shadow's poses, exactly as A116 found for its own six-box run.",
            "The blocking squares are a device for the certificate, not for the node cut.", ""]
    open(os.path.join(NOTES, "t3_table.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("wrote notes/t3_table.md (%d runs)" % len(rows))


if __name__ == "__main__":
    which = sys.argv[1:] or ["t1", "t3"]
    for w in which:
        {"t1": t1, "t3": t3}[w]()
