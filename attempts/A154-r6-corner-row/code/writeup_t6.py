"""A115 follow-up 3: LOG entry, registry row extension, depgraph K0.TREE note."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "..", "results", "t6_summary.json")))

ENTRY = """
## 2026-09-07 - A115 follow-up 3 (PI) - the plain warm re-solve pass, completed

**The pass is now complete over every open k0_00 cell A115 could reach.** This round (15 CPU-h cap,
14.16 used): the 34 never-run A38 level-1 cells and every open level-2/3 cell the previous cap had
missed, plain 240 s first (level-1 first, minmass-descending), then a 900 s warm continuation plus
A85's witness-feedback rounds on the NEW kill-candidates that pass produced. The 32 persistent
cert-FAIL cells and the converged-alive cells were skipped, as instructed.

**Cumulative result: 22 DISTINCT level-1 cells of the 216-cell k0_00 root split certified dead, plus
13 level-2 and 2 level-3 cells and 10 A85/A99 nodes, for 29.83 CPU-h - 1,023-2,372 CPU-h off A99's
9,341-21,661 CPU-h frontier, a 34x-80x return, with no new mathematics anywhere.** A115's own corner
rows, for contrast, cost 13.4 CPU-h for one pass over the same 216 cells and removed nothing.

* Stage A (plain 240 s) is COMPLETE over the whole 142-cell pool: 17 certified, 97 kill-candidate,
  22 alive, 6 knife-edge.
* Stage B (900 s + feedback) reached 26 of those 97 and certified 5 - and all five are level-1
  (`l1_149`, `l1_168`, `l1_169`, `l1_173`, `l1_174`), i.e. cells whose plain 240 s certificate had
  FAILed and which only the continuation closed. Stage B is the highest-yield thing left.
* The certified level-1 set is now {4, 5, 17, 18, 30, 31, 32, 49, 93, 98, 126, 137, 143, 149, 168,
  169, 170, 172, 173, 174, 176, 181} - 22 of 216 (10.2%).

**Hand-off list for A118's successor has grown to 12 (nothing was run on them).** CONVERGED-ALIVE =
tau = budget exactly, minmass = 1.000, converged: the case-LP has reached its optimum and it is not
below budget, so no further LP time kills them. Seven level-1 cells - `l1_071`, `l1_104`, `l1_124`
(new), `l1_148`, `l1_153`, `l1_158`, `l1_159` - four level-2 cells - `l2_p114_001`, `l2_p65_101`,
`l2_p65_111`, `l2_p74_001` (all new) - and the A85 node `s3_far_BL389484_TR018470`. `l1_153` is a
Trump-image cell, which must be alive, and the LP agrees; `l1_159` is confirmed twice independently.

**What is left.** 71 of the 97 stage-A kill-candidates have not had the stage-B treatment (the pool
was worked level-1 first, minmass-descending, so the remainder is the low-value tail); the 32
persistent `cand` cert-FAIL cells remain untouched by instruction.

**Discipline.** READ-ONLY on A38/A85/A99/A113/A121; <= 2 BLAS-pinned processes; commit/physical gate
before every LP and verifier run; resumable per-cell records; hard per-task and per-process
CPU-second caps checked before each cell; frozen `verify_case.py` byte-identical; nothing deleted.
Report: `attempts/A115-k0-corner-rows/notes/t6_report.md`.
"""

REG_OLD = ("SIX level-1 cells (l1_071, l1_104, l1_148, l1_153, l1_158, l1_159) + s3_far are "
           "CONVERGED ALIVE and handed to A118 as the two-meeter cover candidates.** |")
REG_NEW = ("SIX level-1 cells (l1_071, l1_104, l1_148, l1_153, l1_158, l1_159) + s3_far are "
           "CONVERGED ALIVE and handed to A118 as the two-meeter cover candidates.** "
           "**COMPLETED (notes/t6_report.md, +15 CPU-h cap, 14.16 used): the plain pass is now "
           "complete over every open k0_00 cell A115 could reach - stage A (240 s) over the whole "
           "142-cell never-run/open pool, then stage B (900 s + A85 witness-feedback) on its new "
           "kill-candidates. CUMULATIVE: 22 DISTINCT level-1 cells of 216 certified dead + 13 "
           "level-2 + 2 level-3 + 10 A85/A99 nodes for 29.83 CPU-h = 1,023-2,372 CPU-h removed, a "
           "34x-80x return. All five of stage B's kills are level-1 cells whose plain certificate "
           "had FAILed, so stage B is the highest-yield thing left (71 of 97 candidates unreached). "
           "The converged-alive hand-off list is now TWELVE: l1_071, l1_104, l1_124, l1_148, "
           "l1_153, l1_158, l1_159, l2_p114_001, l2_p65_101, l2_p65_111, l2_p74_001, s3_far.** |")

NOTE = ("A115 follow-up 3 (2026-09-07, attempts/A115-k0-corner-rows/notes/t6_report.md): the plain "
        "warm re-solve pass is COMPLETE over every open k0_00 cell A115 could reach. CUMULATIVE: 22 "
        "DISTINCT level-1 cells of the 216-cell root split certified dead (10.2 percent), plus 13 "
        "level-2, 2 level-3 and 10 A85/A99 nodes, for 29.83 CPU-h = 1,023-2,372 CPU-h off A99's "
        "9,341-21,661 CPU-h frontier, a 34x-80x return, with NO new mathematics (each campaign's "
        "own case-LP warm-continued from its own atoms_all + rows_all, then its own node "
        "certificate under the frozen verify_case.py). Stage A (240 s plain) over the whole "
        "142-cell never-run/open pool: 17 certified, 97 kill-candidate, 22 alive, 6 knife-edge. "
        "Stage B (900 s + A85 witness-feedback) on stage A's kill-candidates: 5 certified out of 26 "
        "reached, ALL FIVE level-1 (l1_149, l1_168, l1_169, l1_173, l1_174) -- cells whose plain "
        "certificate had FAILed -- so stage B is the highest-yield remaining move, with 71 of 97 "
        "candidates unreached. HAND-OFF (nothing run on them): TWELVE cells are CONVERGED ALIVE "
        "(tau = budget exactly, minmass 1.000) and need the two-meeter cover, not more LP: level-1 "
        "l1_071, l1_104, l1_124, l1_148, l1_153, l1_158, l1_159; level-2 l2_p114_001, l2_p65_101, "
        "l2_p65_111, l2_p74_001; and the A85 node s3_far_BL389484_TR018470. l1_153 is a "
        "Trump-image cell, which must be alive, and the LP agrees.")


def main():
    p = os.path.join(ROOT, "LOG.md")
    t = io.open(p, encoding="utf-8").read()
    if "A115 follow-up 3 (PI)" in t:
        print("LOG entry already present")
    else:
        io.open(p, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + ENTRY)
        print("LOG entry appended")
    q = os.path.join(ROOT, "attempts", "REGISTRY.md")
    s = io.open(q, encoding="utf-8").read()
    if "COMPLETED (notes/t6_report.md" in s:
        print("registry already updated")
    else:
        assert REG_OLD in s, "registry anchor not found"
        io.open(q, "w", encoding="utf-8").write(s.replace(REG_OLD, REG_NEW))
        print("registry row extended")
    d = os.path.join(ROOT, "lean", "depgraph.json")
    g = json.load(io.open(d, encoding="utf-8"))
    byid = {x["id"]: x for x in g["nodes"]}
    if NOTE[:60] in (byid["K0.TREE"].get("note") or ""):
        print("depgraph note already present")
    else:
        byid["K0.TREE"]["note"] = (byid["K0.TREE"].get("note", "") + " || " + NOTE)
        json.dump(g, io.open(d, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("depgraph K0.TREE note appended; owner unchanged: %r" % byid["K0.TREE"].get("owner"))


if __name__ == "__main__":
    main()
