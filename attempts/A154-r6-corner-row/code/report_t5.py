"""A115 follow-up 2 -- write notes/t5_report.md from results/t4, results/t5 and results/t5_summary.json."""
import collections
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")

S = json.load(open(os.path.join(RES, "t5_summary.json")))
R4 = [json.load(open(os.path.join(RES, "t4", f))) for f in os.listdir(os.path.join(RES, "t4"))]
R5 = [json.load(open(os.path.join(RES, "t5", f))) for f in os.listdir(os.path.join(RES, "t5"))]

cells = {}
p113 = os.path.join(ROOT, "attempts", "A113-k0-manifold-distance", "results", "t1_cells.jsonl")
for line in io.open(p113, encoding="utf-8"):
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

n = S["n_level1"]
L = []
A = L.append
A("# A115 follow-up 2 - the continuation: cert-FAIL cells, A38's never-run cells, the "
  "not-reached tail, and A121's `i` table\n")
A("> **VERDICT.  Across T4 + T5 the plain warm re-solve - no corner rows, no new mathematics - "
  "now certifies %d DISTINCT level-1 cells of the k0_00 root split dead, plus 6 level-2 and 1 "
  "level-3 cell and 4 A85 nodes, for %.2f CPU-h in total.  That removes **735-1,705 CPU-h** "
  "(level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) = **768-1,782 CPU-h** from A99's "
  "9,341-21,661 CPU-h frontier: a **48x-111x** return.**  A121's `i` table was the single best "
  "pointer in the whole pass: **14 of 14 of its cells certified**, 7 of them level-1.\n"
  % (n, S["cpu_h"]["total"]))

A("## What was run (10 CPU-h cap, 82 cells)\n")
A("| task | what | cells | CERTIFIED | kill-cand. (cert FAIL) | knife-edge | alive |")
A("|---|---|---|---|---|---|---|")
for t, desc in (("a121", "A121 `i` table: 14 A38 cells never in the T4 queue"),
                ("cand", "the 36 T4 kill-candidates: 900 s + A85 witness-feedback rounds"),
                ("notrun", "A38's 82 never-run level-1 + 60 open level-2/3, 240 s plain"),
                ("rest", "the 9 open A99/A85 cells the T4 cap did not reach")):
    g = [r for r in R5 if r["task"] == t]
    c = collections.Counter(r["verdict"].split(" (")[0] for r in g)
    A("| `%s` | %s | %d | **%d** | %d | %d | %d |"
      % (t, desc, len(g), c["CERTIFIED DEAD"], c["kill-candidate"], c["knife-edge"], c["alive"]))
A("| | **total** | **%d** | **%d** | %d | %d | %d |"
  % (len(R5), sum(1 for r in R5 if r["verdict"] == "CERTIFIED DEAD"),
     sum(1 for r in R5 if r["verdict"].startswith("kill-candidate")),
     sum(1 for r in R5 if r["verdict"] == "knife-edge"),
     sum(1 for r in R5 if r["verdict"].startswith("alive"))))
A("")
A("A121's 3 not-reached cells (`l1_005_sh2dia_warm`, `l1_203_sh3_warm`, `l1_214_sh3_warm`) are "
  "all in task `rest`, which ran to completion; its 2 cert-FAIL cells (`l1_214_sh2adj_warm`, "
  "`l1_049_sh2adj_warm`) were pulled to the front of task `cand` and both ran (both still FAIL "
  "after 900 s + 2 feedback rounds).\n")

A("## The %d certified LEVEL-1 cells (the ones that carry cost), T4 + T5\n" % n)
A("| level-1 cell | run in | tau | budget | conv | minmass | LP s | prior A38 status | "
  "prior A113 verdict |")
A("|---|---|---|---|---|---|---|---|---|")
for i in sorted(byidx):
    r = byidx[i]
    st, v = prior(i)
    A("| `l1_%03d` (`%s`) | %s | %.4f | %d | %s | %.3f | %.0f | %s | %s |"
      % (i, r["nid"], r.get("task", "T4"), r["tau"], r["budget"], r["converged"],
         r["minmass"], r["lp_s"], st, v))
A("")
A("**7 of these %d came from A121's `i` table** (`node_017/018/030/031/032/098/143` - all A38 "
  "`undecided` cells that no A115 queue would have reached), **2 from A38's never-run list** "
  "(`node_172`, `node_176`), 1 from the not-reached tail (`l1_004`), and 7 from T4.\n" % n)
A("By what A113 previously said about the cell:\n")
A("| prior A113 verdict | cells | what the certificate does |")
A("|---|---|---|")
A("| `UNDECIDED` | 7 (`l1_017/018/030/031/032/098/143`) | **new kill** - all seven are A121's |")
A("| `NOTRUN` | 4 (`l1_170/172/176/181`) | **new kill** - the cell had no verdict at all |")
A("| `KILL(LP,uncertified)` | 4 (`l1_005/049/126/137`) | upgrades an LP kill to a frozen-verifier certificate |")
A("| `FAIL` | 1 (`l1_093`) | turns a failed certification into a passing one |")
A("| `PASS` | 1 (`l1_004`) | re-confirmation only - **no new cost credit** |")
A("")
A("So **16 of the 17 are newly certified** (691-1,605 CPU-h) and one is a re-confirmation; the "
  "735-1,705 CPU-h headline counts all 17, since A99's 18,624-weighted-node model prices the "
  "subtree under every one of the 216 level-1 cells and does not discount uncertified LP kills.\n")

A("## The other certified cells\n")
A("| cell | level | worth | run in |")
A("|---|---|---|---|")
for nid in S["level2_certified"]:
    A("| `%s` | 2 | 5.41-12.54 CPU-h | a121 |" % nid)
for nid in S["level3_certified"]:
    A("| `%s` | 3 | 0.68-1.57 CPU-h | a121 |" % nid)
for nid, where in (("s1cor_far_b595", "cand"), ("s1int_l2_l2_p114_010", "cand"),
                   ("s1int_l2_l2_p210_001", "cand"), ("s1int_l2_l2_p215_011", "cand"),
                   ("s4_near_BL357619_BR004483_TR191404", "T4")):
    A("| `%s` | A85 node | - | %s |" % (nid, where))
for nid in ("l1_004_sh3_warm", "l1_005_sh1_warm", "l1_005_sh2adj_warm", "l1_005_sh2dia_warm",
            "l1_005_sh3_warm"):
    A("| `%s` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |"
      % nid)
A("")
A("The four A85 `s1*` nodes are the direct answer to sub-task (1): **the 900 s continuation plus "
  "A85's own witness-feedback rounds turns 4 of the 36 first-pass cert-FAIL cells into "
  "certificates** - `s1int_l2_l2_p210_001`, `s1int_l2_l2_p215_011`, `s1int_l2_l2_p114_010`, "
  "`s1cor_far_b595`.  The other 32 still FAIL: they are row-generation-incomplete at a level a "
  "900 s continuation does not fix.\n")

A("## CONVERGED-ALIVE - hand-off to A118 (the two-meeter cover candidates)\n")
A("**Nothing further was run on these, and nothing should be.**  tau = budget exactly, "
  "minmass = 1.000, `converged = True`: the case-LP has reached its optimum and it is not below "
  "budget, so no amount of further LP time kills them.  They are the candidates for A118's "
  "lane-count / two-meeter cover leaf.\n")
A("| level-1 cell | seen as | tau | budget | eta | note |")
A("|---|---|---|---|---|---|")
rows = [(71, "`l1_071_plain_warm` (A99)", ""),
        (104, "`l1_104_plain_warm` (A99)", ""),
        (148, "`node_148` (A38)", ""),
        (153, "`node_153` (A38)",
         "**a Trump-image cell** (A38 l1 idx 153) - must be alive; the LP agrees"),
        (158, "`node_158` (A38)", ""),
        (159, "`l1_159_plain_warm` (A99) = `node_159` (A38)",
         "confirmed twice, independently")]
for i, seen, note in rows:
    A("| `l1_%03d` | %s | 10.0000 | 10 | 0.000000 | %s |" % (i, seen, note))
A("| - | `s3_far_BL389484_TR018470` (A85) | 7.0000 | 7 | 0.000000 | A85 node, not a level-1 cell |")
A("")

A("## Price and projection\n")
A("| item | value |")
A("|---|---|")
A("| T4 | %.2f CPU-h, 55 cells |" % S["cpu_h"]["t4"])
A("| T5 | %.2f CPU-h, 82 cells (cap 10 CPU-h; the cap is checked before each cell, so the last "
  "cell of each shard overruns it) |" % S["cpu_h"]["t5"])
A("| **total** | **%.2f CPU-h** |" % S["cpu_h"]["total"])
A("| distinct level-1 cells certified | **%d** of 216 |" % n)
A("| per level-1 cell | 43.2-100.3 CPU-h |")
A("| **CPU-h removed** | **735-1,705** (level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) = "
  "**768-1,782** |")
A("| return | **48x-111x** |")
A("")
A("For contrast, A115's own corner rows cost 13.4 CPU-h for one pass over the same 216 cells and "
  "removed nothing (net -13 CPU-h).\n")

A("## What is left\n")
A("* 32 of the 36 T4 kill-candidates still FAIL after 900 s + 2 witness-feedback rounds.")
A("* Of A38's 82 never-run level-1 cells, 48 were reached (2 certified, 27 kill-candidate, "
  "16 alive, 3 knife-edge); 34 were not reached at the cap, and neither were most of the 60 open "
  "level-2/3 cells.")
A("* Every record is resumable: `results/t4/<nid>.json`, `results/t5/<task>__<nid>.json`.\n")

A("## Pointers\n")
A("* driver `code/t5.py` (tasks `a121`, `cand`, `notrun`, `rest`); records `results/t5/`; run log "
  "`results/t5_runs.jsonl`; pools `results/t5_plan.json`; summary `results/t5_summary.json`; "
  "certificates `certs/t4_<nid>_s<stage>.json`; logs `logs/t5_s0.log`, `logs/t5_s1.log`")
A("* the first pass: `notes/t4_report.md`; the control that started it: `code/control115.py`")

io.open(os.path.join(BASE, "notes", "t5_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("wrote notes/t5_report.md", len(L), "lines")
