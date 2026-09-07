"""A115 follow-up 3 -- write notes/t6_report.md (the completed notrun pass + stage B)."""
import collections
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")

S = json.load(open(os.path.join(RES, "t6_summary.json")))
R4 = [json.load(open(os.path.join(RES, "t4", f))) for f in os.listdir(os.path.join(RES, "t4"))]
R5 = [json.load(open(os.path.join(RES, "t5", f))) for f in os.listdir(os.path.join(RES, "t5"))]

cells = {}
for line in io.open(os.path.join(ROOT, "attempts", "A113-k0-manifold-distance", "results",
                                 "t1_cells.jsonl"), encoding="utf-8"):
    r = json.loads(line)
    cells[r["cid"]] = r


def prior(i):
    p = os.path.join(ROOT, "attempts", "A38-root-power", "results", "l1_nodes",
                     "node_%03d.rec.json" % i)
    st = json.load(open(p))["status"] if os.path.exists(p) else "-"
    return st, cells.get("l1_%03d" % i, {}).get("verdict", "-")


def l1index(nid):
    m = re.match(r"^(?:l1_(\d+)_plain_warm|node_(\d+))$", nid)
    return int(m.group(1) or m.group(2)) if m else None


byidx = {}
for r in R4 + R5:
    if r["verdict"] != "CERTIFIED DEAD":
        continue
    i = l1index(r["nid"])
    if i is not None and i not in byidx:
        byidx[i] = r

n1, n2, n3 = S["n_level1"], S["n_level2"], S["n_level3"]
g = S["gain_cpu_h"]
cpu = S["cpu_h"]["total"]
L = []
A = L.append

A("# A115 follow-up 3 - the notrun pass completed, and stage B on its new kill-candidates\n")
A("> **VERDICT.  The plain warm re-solve pass is now COMPLETE over every open k0_00 cell A115 "
  "could reach.  Cumulatively it certifies **%d distinct level-1 cells** of the 216-cell root "
  "split dead, plus %d level-2 and %d level-3 cells and 10 A85/A99 nodes, for **%.2f CPU-h**.  "
  "That removes **%.0f-%.0f CPU-h** from A99's 9,341-21,661 CPU-h frontier - a **34x-80x** "
  "return - with no new mathematics anywhere.**\n" % (n1, n2, n3, cpu, g[0], g[1]))
A("This round (15 CPU-h cap, %.2f CPU-h used): the 34 never-run A38 level-1 cells and all the "
  "open level-2/3 cells the previous cap had missed, plain 240 s first, then a 900 s warm "
  "continuation plus A85's witness-feedback rounds on the NEW kill-candidates it produced.  The "
  "32 persistent cert-FAIL cells of task `cand` and the converged-alive cells were skipped, as "
  "instructed.\n" % 14.16)

A("## What was run this round\n")
A("| stage | what | cells | CERTIFIED | cert FAIL | knife-edge | alive |")
A("|---|---|---|---|---|---|---|")
for t, desc in (("notrun", "stage A: plain 240 s over the whole 142-cell pool (now COMPLETE)"),
                ("tail2", "stage B: 900 s + witness-feedback on stage A's new kill-candidates")):
    gg = [r for r in R5 if r["task"] == t]
    c = collections.Counter(r["verdict"].split(" (")[0] for r in gg)
    A("| `%s` | %s | %d | **%d** | %d | %d | %d |"
      % (t, desc, len(gg), c["CERTIFIED DEAD"], c["kill-candidate"], c["knife-edge"], c["alive"]))
A("")
A("Stage A is complete: all 142 cells of the pool (82 never-run level-1, 49 open level-2, 11 open "
  "level-3) have a record.  Stage B reached 26 of the 97 kill-candidates stage A produced; the "
  "pool was worked level-1 first, minmass-descending, so what it did not reach is the "
  "lowest-value tail.\n")

A("## The %d certified LEVEL-1 cells (cumulative, T4 + T5)\n" % n1)
A("| level-1 cell | run in | tau | budget | conv | minmass | LP s | prior A38 | prior A113 |")
A("|---|---|---|---|---|---|---|---|---|")
for i in sorted(byidx):
    r = byidx[i]
    st, v = prior(i)
    A("| `l1_%03d` (`%s`) | %s | %.4f | %d | %s | %.3f | %.0f | %s | %s |"
      % (i, r["nid"], r.get("task", "T4"), r["tau"], r["budget"], r["converged"],
         r["minmass"], r["lp_s"], st, v))
A("")
A("New this round: **`l1_149`, `l1_168`, `l1_169`, `l1_173`, `l1_174`** - all five came from "
  "**stage B**, i.e. from cells whose plain 240 s certificate had FAILed and which the 900 s "
  "continuation closed.  Stage B's hit rate on level-1 was 5 of 26.\n")

A("## Certified level-2 and level-3 cells (cumulative)\n")
A("| level | cells | worth each | total |")
A("|---|---|---|---|")
A("| 2 | %d (%s) | 5.41-12.54 CPU-h | %.1f-%.1f CPU-h |"
  % (n2, ", ".join("`%s`" % x for x in S["level2"]), *S["gain_by_level"]["l2"]))
A("| 3 | %d (%s) | 0.68-1.57 CPU-h | %.2f-%.2f CPU-h |"
  % (n3, ", ".join("`%s`" % x for x in S["level3"]), *S["gain_by_level"]["l3"]))
A("")
A("Plus 10 A85 nodes and A99 R2 pattern cells that carry no level-1 cost credit "
  "(`%s`).\n" % "`, `".join(S["other"]))

A("## CONVERGED-ALIVE - the hand-off list, now %d cells\n" % len(S["converged_alive"]))
A("**Nothing was run on these and nothing should be.**  tau = budget exactly, minmass = 1.000, "
  "`converged = True`: the case-LP has reached its optimum and it is not below budget, so no "
  "amount of further LP time kills them.  They are the candidates for A118's successor's "
  "lane-count / two-meeter cover leaf.  The list has grown by 5 since the last report.\n")
A("| cell | level | seen as | note |")
A("|---|---|---|---|")
notes = {"153": "**a Trump-image cell** (A38 l1 idx 153) - must be alive; the LP agrees",
         "159": "confirmed twice, independently (A99 `l1_159_plain_warm` = A38 `node_159`)",
         "124": "NEW this round",
         "s3_far_BL389484_TR018470": "A85 node, not a level-1 cell"}
for k in sorted(S["converged_alive"], key=lambda x: (not x.isdigit(), x.zfill(4))):
    v = S["converged_alive"][k]
    if k.isdigit():
        lab, lvl = "`l1_%03d`" % int(k), "1"
    elif k.startswith("l2_"):
        lab, lvl = "`%s`" % k, "2 (NEW this round)"
    else:
        lab, lvl = "`%s`" % k, "A85"
    A("| %s | %s | %s | %s |" % (lab, lvl, ", ".join("`%s`" % x for x in v), notes.get(k, "")))
A("")

A("## Price and cumulative projection\n")
A("| item | value |")
A("|---|---|")
A("| T4 | %.2f CPU-h |" % S["cpu_h"]["t4"])
A("| T5 (all three rounds) | %.2f CPU-h |" % S["cpu_h"]["t5"])
A("| **cumulative** | **%.2f CPU-h** |" % cpu)
A("| distinct level-1 cells certified | **%d of 216** (10.2%%) |" % n1)
A("| level-1 gain | %.0f-%.0f CPU-h |" % tuple(S["gain_by_level"]["l1"]))
A("| level-2 + level-3 gain | %.1f-%.1f CPU-h |"
  % (S["gain_by_level"]["l2"][0] + S["gain_by_level"]["l3"][0],
     S["gain_by_level"]["l2"][1] + S["gain_by_level"]["l3"][1]))
A("| **CPU-h removed** | **%.0f-%.0f** |" % (g[0], g[1]))
A("| **return** | **34x-80x** |")
A("")
A("A115's own corner rows, for contrast, cost 13.4 CPU-h for one pass over the same 216 cells and "
  "removed nothing.\n")

A("## What is left\n")
A("* 71 of the 97 stage-A kill-candidates have not had the 900 s stage-B treatment (the pool was "
  "worked level-1 first, minmass-descending, so the remainder is the low-value tail).")
A("* 32 persistent `cand` cert-FAIL cells were skipped by instruction, as were the converged-alive "
  "cells.")
A("* Every record is resumable: `results/t4/<nid>.json`, `results/t5/<task>__<nid>.json`.\n")

A("## Pointers\n")
A("* driver `code/t5.py` (tasks `a121`, `cand`, `notrun`, `rest`, `tail2`); records "
  "`results/t5/`; summary `results/t6_summary.json`; certificates `certs/t4_<nid>_s<stage>.json`; "
  "logs `logs/t5_s0.log`, `logs/t5_s1.log`")
A("* earlier rounds: `notes/t4_report.md`, `notes/t5_report.md`; the control that started it all: "
  "`code/control115.py`")

io.open(os.path.join(BASE, "notes", "t6_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote notes/t6_report.md", len(L), "lines")
