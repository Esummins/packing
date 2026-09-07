"""A115 follow-up 2: append the LOG entry, extend the registry row, note the depgraph K0.TREE node."""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "..", "results", "t5_summary.json")))

ENTRY = """
## 2026-09-07 - A115 follow-up 2 (PI) - the continuation, and A121's pointer

**Continuation of the plain warm re-solve pass**, 10 CPU-h cap, 82 cells: (1) the 36 T4
kill-candidates with a 900 s warm continuation plus A85's witness-feedback rounds; (2) the 240 s
plain pass over A38's 82 never-run level-1 cells and its 60 still-open level-2/3 cells; (3) the 9
open A99/A85 cells the T4 cap did not reach; and, added mid-run on the PI's instruction, (4) the 14
A38 k0 nodes A121's `i` table flagged as having incomplete supports and never queued by A115.

**Result. Across T4 + T5 the plain warm re-solve now certifies 17 DISTINCT level-1 cells of the
k0_00 root split dead (16 of them newly), plus 6 level-2 cells, 1 level-3 cell and 4 A85 nodes, for
15.36 CPU-h. That removes 735-1,705 CPU-h (level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) =
768-1,782 CPU-h from A99's 9,341-21,661 CPU-h frontier - a 48x-111x return.** For contrast A115's
own corner rows cost 13.4 CPU-h for the same pass and removed nothing.

* **A121's `i` table was the best pointer in the whole pass: 14 of 14 of its cells certified**, 7 of
  them level-1 (`node_017/018/030/031/032/098/143` - all A38 `undecided`, none of which any A115
  queue would have reached), 6 level-2 and 1 level-3. Every one had tau = 9, budget 10, and closed
  in 37-264 s.
* Sub-task (1): the 900 s continuation plus A85's own witness-feedback rounds turns **4 of the 36**
  first-pass cert-FAIL cells into certificates (`s1int_l2_l2_p210_001`, `s1int_l2_l2_p215_011`,
  `s1int_l2_l2_p114_010`, `s1cor_far_b595`). The other 32 still FAIL - row-generation-incomplete at
  a level a 900 s continuation does not fix. A121's two cert-FAIL cells were run first; both still
  FAIL.
* Sub-task (2): 48 of A38's 82 never-run level-1 cells were reached; 2 certified (`node_172`,
  `node_176` - cells that had no verdict at all), 27 kill-candidate, 16 alive, 3 knife-edge.
* Sub-task (3): all 9 not-reached cells ran; 4 certified. A121's 3 not-reached cells are among them.
* By what A113 previously said about the 17: 7 `UNDECIDED` (all A121's) and 4 `NOTRUN` are NEW
  kills; 4 `KILL(LP,uncertified)` and 1 `FAIL` are upgraded to a frozen-verifier certificate; 1
  (`l1_004`) was already `PASS` and is a re-confirmation with no new cost credit.

**Handed to A118 - the CONVERGED-ALIVE cells (nothing was run on them, and nothing should be).**
Six level-1 cells and one A85 node come back with tau = budget exactly, minmass = 1.000,
`converged = True`: the case-LP has reached its optimum and it is not below budget, so no amount of
further LP time kills them. They are the candidates for A118's lane-count / two-meeter cover leaf:
`l1_071`, `l1_104`, `l1_148`, `l1_153`, `l1_158`, `l1_159`, and `s3_far_BL389484_TR018470` (A85).
`l1_159` is confirmed twice independently (A99's `l1_159_plain_warm` and A38's `node_159`), and
`l1_153` is a Trump-image cell, which must be alive - the LP agrees.

**Discipline.** READ-ONLY on A38/A85/A99/A113/A121 (every node json copied to
`results/nodes/<nid>.src.json` before being touched); <= 2 BLAS-pinned processes; commit/physical
gate before every LP and every verifier run; one resumable record per cell
(`results/t5/<task>__<nid>.json`); hard per-task and per-process CPU-second caps, checked before
each cell, so the final cell of each shard overruns (36,963 s = 10.27 CPU-h against the 10 CPU-h
cap); frozen `verify_case.py` byte-identical; nothing deleted anywhere - when the queue had to be
re-ordered for A121's cells the two running shards were stopped and relaunched, and every completed
record was kept. Report: `attempts/A115-k0-corner-rows/notes/t5_report.md`.
"""

REG_OLD = ("minmass 1.000: l1_071, l1_104, l1_159, s3_far_BL389484_TR018470), which no further LP "
           "time can kill.** |")
REG_NEW = ("minmass 1.000: l1_071, l1_104, l1_159, s3_far_BL389484_TR018470), which no further LP "
           "time can kill.** **CONTINUATION (notes/t5_report.md, 10 CPU-h, 82 more cells): T4+T5 "
           "together certify 17 DISTINCT level-1 cells of the k0_00 root split (16 newly) + 6 "
           "level-2 + 1 level-3 + 4 A85 nodes for 15.36 CPU-h = 768-1,782 CPU-h removed, a "
           "48x-111x return. A121's `i` table was the best pointer in the pass: 14 of 14 of its "
           "cells certified, 7 of them level-1 A38 `undecided` cells no A115 queue would have "
           "reached. A85's witness-feedback rounds convert 4 of the 36 first-pass cert-FAIL cells. "
           "SIX level-1 cells (l1_071, l1_104, l1_148, l1_153, l1_158, l1_159) + s3_far are "
           "CONVERGED ALIVE and handed to A118 as the two-meeter cover candidates.** |")

NOTE = ("A115 follow-up 2 (2026-09-07, attempts/A115-k0-corner-rows/notes/t5_report.md): the plain "
        "warm re-solve pass continued to 15.36 CPU-h total and now certifies 17 DISTINCT level-1 "
        "cells of the k0_00 root split dead (16 newly), plus 6 level-2, 1 level-3 and 4 A85 nodes "
        "= 768-1,782 CPU-h off A99's 9,341-21,661 CPU-h frontier, a 48x-111x return, with NO new "
        "mathematics (A38/A85/A99's own case-LP warm-continued from their own atoms_all + rows_all, "
        "then their own node certificate under the frozen verify_case.py; A85's witness-feedback "
        "rounds convert 4 of the 36 first-pass cert-FAIL cells). A121's `i` table (incomplete "
        "supports) was the single best pointer: 14 of 14 of its cells certified, 7 of them level-1 "
        "A38 `undecided` cells that no A115 queue would have reached. HANDED TO A118: six level-1 "
        "cells (l1_071, l1_104, l1_148, l1_153, l1_158, l1_159) and the A85 node "
        "s3_far_BL389484_TR018470 are CONVERGED ALIVE (tau = budget exactly, minmass 1.000) - no "
        "further LP time kills them, they need the two-meeter cover; l1_159 is confirmed twice "
        "independently and l1_153 is a Trump-image cell, which must be alive.")


def main():
    p = os.path.join(ROOT, "LOG.md")
    t = io.open(p, encoding="utf-8").read()
    if ENTRY[:60] not in t:
        io.open(p, "w", encoding="utf-8").write(t.rstrip("\n") + "\n" + ENTRY)
        print("LOG entry appended")
    q = os.path.join(ROOT, "attempts", "REGISTRY.md")
    s = io.open(q, encoding="utf-8").read()
    if REG_NEW[:80] in s:
        print("registry already updated")
    else:
        assert REG_OLD in s, "registry anchor not found"
        io.open(q, "w", encoding="utf-8").write(s.replace(REG_OLD, REG_NEW))
        print("registry row extended")
    d = os.path.join(ROOT, "lean", "depgraph.json")
    g = json.load(io.open(d, encoding="utf-8"))
    byid = {x["id"]: x for x in g["nodes"]}
    tgt = "K0.TREE"
    if NOTE[:60] in (byid[tgt].get("note") or ""):
        print("depgraph note already present")
    else:
        byid[tgt]["note"] = (byid[tgt].get("note", "") + " || " + NOTE)
        json.dump(g, io.open(d, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("depgraph %s note appended; owner unchanged: %r" % (tgt, byid[tgt].get("owner")))


if __name__ == "__main__":
    main()
