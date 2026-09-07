# A115 follow-up 3 - the notrun pass completed, and stage B on its new kill-candidates

> **VERDICT.  The plain warm re-solve pass is now COMPLETE over every open k0_00 cell A115 could reach.  Cumulatively it certifies **22 distinct level-1 cells** of the 216-cell root split dead, plus 13 level-2 and 2 level-3 cells and 10 A85/A99 nodes, for **29.83 CPU-h**.  That removes **1023-2372 CPU-h** from A99's 9,341-21,661 CPU-h frontier - a **34x-80x** return - with no new mathematics anywhere.**

This round (15 CPU-h cap, 14.16 CPU-h used): the 34 never-run A38 level-1 cells and all the open level-2/3 cells the previous cap had missed, plain 240 s first, then a 900 s warm continuation plus A85's witness-feedback rounds on the NEW kill-candidates it produced.  The 32 persistent cert-FAIL cells of task `cand` and the converged-alive cells were skipped, as instructed.

## What was run this round

| stage | what | cells | CERTIFIED | cert FAIL | knife-edge | alive |
|---|---|---|---|---|---|---|
| `notrun` | stage A: plain 240 s over the whole 142-cell pool (now COMPLETE) | 142 | **17** | 97 | 6 | 22 |
| `tail2` | stage B: 900 s + witness-feedback on stage A's new kill-candidates | 27 | **5** | 21 | 1 | 0 |

Stage A is complete: all 142 cells of the pool (82 never-run level-1, 49 open level-2, 11 open level-3) have a record.  Stage B reached 26 of the 97 kill-candidates stage A produced; the pool was worked level-1 first, minmass-descending, so what it did not reach is the lowest-value tail.

## The 22 certified LEVEL-1 cells (cumulative, T4 + T5)

| level-1 cell | run in | tau | budget | conv | minmass | LP s | prior A38 | prior A113 |
|---|---|---|---|---|---|---|---|---|
| `l1_004` (`l1_004_plain_warm`) | rest | 8.0000 | 10 | True | 1.000 | 9 | dead(T1) | PASS |
| `l1_005` (`l1_005_plain_warm`) | T4 | 8.0000 | 10 | True | 1.000 | 20 | dead(T1) | KILL(LP,uncertified) |
| `l1_017` (`node_017`) | a121 | 9.0000 | 10 | False | 1.000 | 261 | undecided | UNDECIDED |
| `l1_018` (`node_018`) | a121 | 9.0000 | 10 | True | 1.000 | 58 | undecided | UNDECIDED |
| `l1_030` (`node_030`) | a121 | 9.0000 | 10 | True | 1.000 | 50 | undecided | UNDECIDED |
| `l1_031` (`node_031`) | a121 | 9.0000 | 10 | False | 0.000 | 240 | undecided | UNDECIDED |
| `l1_032` (`node_032`) | a121 | 9.0000 | 10 | False | 0.000 | 240 | undecided | UNDECIDED |
| `l1_049` (`l1_049_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 222 | dead(T1) | KILL(LP,uncertified) |
| `l1_093` (`l1_093_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 46 | dead(T1) | FAIL |
| `l1_098` (`node_098`) | a121 | 9.0000 | 10 | True | 1.000 | 86 | undecided | UNDECIDED |
| `l1_126` (`l1_126_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 109 | dead(T1) | KILL(LP,uncertified) |
| `l1_137` (`l1_137_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 219 | dead(T1) | KILL(LP,uncertified) |
| `l1_143` (`node_143`) | a121 | 9.0000 | 10 | False | 1.000 | 264 | undecided | UNDECIDED |
| `l1_149` (`node_149`) | tail2 | 9.5000 | 10 | False | 0.826 | 974 | notrun | NOTRUN |
| `l1_168` (`node_168`) | tail2 | 9.0000 | 10 | True | 1.000 | 95 | notrun | NOTRUN |
| `l1_169` (`node_169`) | tail2 | 9.0000 | 10 | True | 1.000 | 102 | notrun | NOTRUN |
| `l1_170` (`l1_170_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 156 | notrun | NOTRUN |
| `l1_172` (`node_172`) | notrun | 9.0000 | 10 | True | 1.000 | 184 | notrun | NOTRUN |
| `l1_173` (`node_173`) | tail2 | 9.0000 | 10 | True | 1.000 | 18 | notrun | NOTRUN |
| `l1_174` (`node_174`) | tail2 | 9.0000 | 10 | True | 1.000 | 35 | notrun | NOTRUN |
| `l1_176` (`node_176`) | notrun | 9.0000 | 10 | False | 1.000 | 259 | notrun | NOTRUN |
| `l1_181` (`l1_181_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 160 | notrun | NOTRUN |

New this round: **`l1_149`, `l1_168`, `l1_169`, `l1_173`, `l1_174`** - all five came from **stage B**, i.e. from cells whose plain 240 s certificate had FAILed and which the 900 s continuation closed.  Stage B's hit rate on level-1 was 5 of 26.

## Certified level-2 and level-3 cells (cumulative)

| level | cells | worth each | total |
|---|---|---|---|
| 2 | 13 (`l2_p100_001`, `l2_p61_001`, `l2_p61_010`, `l2_p61_100`, `l2_p61_101`, `l2_p61_111`, `l2_p62_011`, `l2_p74_010`, `l2_p74_011`, `l2_p95_000`, `l2_p95_001`, `l2_p95_010`, `l2_p95_011`) | 5.41-12.54 CPU-h | 70.3-163.0 CPU-h |
| 3 | 2 (`l3_pp114_001_001`, `l3_pp114_001_010`) | 0.68-1.57 CPU-h | 1.35-3.13 CPU-h |

Plus 10 A85 nodes and A99 R2 pattern cells that carry no level-1 cost credit (`l1_004_sh3_warm`, `l1_005_sh1_warm`, `l1_005_sh2adj_warm`, `l1_005_sh2dia_warm`, `l1_005_sh3_warm`, `s1cor_far_b595`, `s1int_l2_l2_p114_010`, `s1int_l2_l2_p210_001`, `s1int_l2_l2_p215_011`, `s4_near_BL357619_BR004483_TR191404`).

## CONVERGED-ALIVE - the hand-off list, now 12 cells

**Nothing was run on these and nothing should be.**  tau = budget exactly, minmass = 1.000, `converged = True`: the case-LP has reached its optimum and it is not below budget, so no amount of further LP time kills them.  They are the candidates for A118's successor's lane-count / two-meeter cover leaf.  The list has grown by 5 since the last report.

| cell | level | seen as | note |
|---|---|---|---|
| `l1_071` | 1 | `l1_071_plain_warm` |  |
| `l1_104` | 1 | `l1_104_plain_warm` |  |
| `l1_124` | 1 | `node_124` | NEW this round |
| `l1_148` | 1 | `node_148` |  |
| `l1_153` | 1 | `node_153` | **a Trump-image cell** (A38 l1 idx 153) - must be alive; the LP agrees |
| `l1_158` | 1 | `node_158` |  |
| `l1_159` | 1 | `l1_159_plain_warm`, `node_159` | confirmed twice, independently (A99 `l1_159_plain_warm` = A38 `node_159`) |
| `l2_p114_001` | 2 (NEW this round) | `l2_p114_001` |  |
| `l2_p65_101` | 2 (NEW this round) | `l2_p65_101` |  |
| `l2_p65_111` | 2 (NEW this round) | `l2_p65_111` |  |
| `l2_p74_001` | 2 (NEW this round) | `l2_p74_001` |  |
| `s3_far_BL389484_TR018470` | A85 | `s3_far_BL389484_TR018470` | A85 node, not a level-1 cell |

## Price and cumulative projection

| item | value |
|---|---|
| T4 | 5.09 CPU-h |
| T5 (all three rounds) | 24.75 CPU-h |
| **cumulative** | **29.83 CPU-h** |
| distinct level-1 cells certified | **22 of 216** (10.2%) |
| level-1 gain | 951-2206 CPU-h |
| level-2 + level-3 gain | 71.6-166.1 CPU-h |
| **CPU-h removed** | **1023-2372** |
| **return** | **34x-80x** |

A115's own corner rows, for contrast, cost 13.4 CPU-h for one pass over the same 216 cells and removed nothing.

## What is left

* 71 of the 97 stage-A kill-candidates have not had the 900 s stage-B treatment (the pool was worked level-1 first, minmass-descending, so the remainder is the low-value tail).
* 32 persistent `cand` cert-FAIL cells were skipped by instruction, as were the converged-alive cells.
* Every record is resumable: `results/t4/<nid>.json`, `results/t5/<task>__<nid>.json`.

## Pointers

* driver `code/t5.py` (tasks `a121`, `cand`, `notrun`, `rest`, `tail2`); records `results/t5/`; summary `results/t6_summary.json`; certificates `certs/t4_<nid>_s<stage>.json`; logs `logs/t5_s0.log`, `logs/t5_s1.log`
* earlier rounds: `notes/t4_report.md`, `notes/t5_report.md`; the control that started it all: `code/control115.py`
