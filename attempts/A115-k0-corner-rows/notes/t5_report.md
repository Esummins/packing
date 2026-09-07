# A115 follow-up 2 - the continuation: cert-FAIL cells, A38's never-run cells, the not-reached tail, and A121's `i` table

> **VERDICT.  Across T4 + T5 the plain warm re-solve - no corner rows, no new mathematics - now certifies 17 DISTINCT level-1 cells of the k0_00 root split dead, plus 6 level-2 and 1 level-3 cell and 4 A85 nodes, for 15.36 CPU-h in total.  That removes **735-1,705 CPU-h** (level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) = **768-1,782 CPU-h** from A99's 9,341-21,661 CPU-h frontier: a **48x-111x** return.**  A121's `i` table was the single best pointer in the whole pass: **14 of 14 of its cells certified**, 7 of them level-1.

## What was run (10 CPU-h cap, 82 cells)

| task | what | cells | CERTIFIED | kill-cand. (cert FAIL) | knife-edge | alive |
|---|---|---|---|---|---|---|
| `a121` | A121 `i` table: 14 A38 cells never in the T4 queue | 14 | **14** | 0 | 0 | 0 |
| `cand` | the 36 T4 kill-candidates: 900 s + A85 witness-feedback rounds | 11 | **4** | 7 | 0 | 0 |
| `notrun` | A38's 82 never-run level-1 + 60 open level-2/3, 240 s plain | 48 | **2** | 27 | 3 | 16 |
| `rest` | the 9 open A99/A85 cells the T4 cap did not reach | 9 | **4** | 5 | 0 | 0 |
| | **total** | **82** | **24** | 39 | 3 | 16 |

A121's 3 not-reached cells (`l1_005_sh2dia_warm`, `l1_203_sh3_warm`, `l1_214_sh3_warm`) are all in task `rest`, which ran to completion; its 2 cert-FAIL cells (`l1_214_sh2adj_warm`, `l1_049_sh2adj_warm`) were pulled to the front of task `cand` and both ran (both still FAIL after 900 s + 2 feedback rounds).

## The 17 certified LEVEL-1 cells (the ones that carry cost), T4 + T5

| level-1 cell | run in | tau | budget | conv | minmass | LP s | prior A38 status | prior A113 verdict |
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
| `l1_170` (`l1_170_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 156 | notrun | NOTRUN |
| `l1_172` (`node_172`) | notrun | 9.0000 | 10 | True | 1.000 | 184 | notrun | NOTRUN |
| `l1_176` (`node_176`) | notrun | 9.0000 | 10 | False | 1.000 | 259 | notrun | NOTRUN |
| `l1_181` (`l1_181_plain_warm`) | T4 | 9.0000 | 10 | True | 1.000 | 160 | notrun | NOTRUN |

**7 of these 17 came from A121's `i` table** (`node_017/018/030/031/032/098/143` - all A38 `undecided` cells that no A115 queue would have reached), **2 from A38's never-run list** (`node_172`, `node_176`), 1 from the not-reached tail (`l1_004`), and 7 from T4.

By what A113 previously said about the cell:

| prior A113 verdict | cells | what the certificate does |
|---|---|---|
| `UNDECIDED` | 7 (`l1_017/018/030/031/032/098/143`) | **new kill** - all seven are A121's |
| `NOTRUN` | 4 (`l1_170/172/176/181`) | **new kill** - the cell had no verdict at all |
| `KILL(LP,uncertified)` | 4 (`l1_005/049/126/137`) | upgrades an LP kill to a frozen-verifier certificate |
| `FAIL` | 1 (`l1_093`) | turns a failed certification into a passing one |
| `PASS` | 1 (`l1_004`) | re-confirmation only - **no new cost credit** |

So **16 of the 17 are newly certified** (691-1,605 CPU-h) and one is a re-confirmation; the 735-1,705 CPU-h headline counts all 17, since A99's 18,624-weighted-node model prices the subtree under every one of the 216 level-1 cells and does not discount uncertified LP kills.

## The other certified cells

| cell | level | worth | run in |
|---|---|---|---|
| `l2_p61_001` | 2 | 5.41-12.54 CPU-h | a121 |
| `l2_p61_010` | 2 | 5.41-12.54 CPU-h | a121 |
| `l2_p61_111` | 2 | 5.41-12.54 CPU-h | a121 |
| `l2_p74_010` | 2 | 5.41-12.54 CPU-h | a121 |
| `l2_p74_011` | 2 | 5.41-12.54 CPU-h | a121 |
| `l2_p95_000` | 2 | 5.41-12.54 CPU-h | a121 |
| `l3_pp114_001_001` | 3 | 0.68-1.57 CPU-h | a121 |
| `s1cor_far_b595` | A85 node | - | cand |
| `s1int_l2_l2_p114_010` | A85 node | - | cand |
| `s1int_l2_l2_p210_001` | A85 node | - | cand |
| `s1int_l2_l2_p215_011` | A85 node | - | cand |
| `s4_near_BL357619_BR004483_TR191404` | A85 node | - | T4 |
| `l1_004_sh3_warm` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |
| `l1_005_sh1_warm` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |
| `l1_005_sh2adj_warm` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |
| `l1_005_sh2dia_warm` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |
| `l1_005_sh3_warm` | A99 R2 pattern cell | no cost credit (x15 multiplier, not the route) | rest/T4 |

The four A85 `s1*` nodes are the direct answer to sub-task (1): **the 900 s continuation plus A85's own witness-feedback rounds turns 4 of the 36 first-pass cert-FAIL cells into certificates** - `s1int_l2_l2_p210_001`, `s1int_l2_l2_p215_011`, `s1int_l2_l2_p114_010`, `s1cor_far_b595`.  The other 32 still FAIL: they are row-generation-incomplete at a level a 900 s continuation does not fix.

## CONVERGED-ALIVE - hand-off to A118 (the two-meeter cover candidates)

**Nothing further was run on these, and nothing should be.**  tau = budget exactly, minmass = 1.000, `converged = True`: the case-LP has reached its optimum and it is not below budget, so no amount of further LP time kills them.  They are the candidates for A118's lane-count / two-meeter cover leaf.

| level-1 cell | seen as | tau | budget | eta | note |
|---|---|---|---|---|---|
| `l1_071` | `l1_071_plain_warm` (A99) | 10.0000 | 10 | 0.000000 |  |
| `l1_104` | `l1_104_plain_warm` (A99) | 10.0000 | 10 | 0.000000 |  |
| `l1_148` | `node_148` (A38) | 10.0000 | 10 | 0.000000 |  |
| `l1_153` | `node_153` (A38) | 10.0000 | 10 | 0.000000 | **a Trump-image cell** (A38 l1 idx 153) - must be alive; the LP agrees |
| `l1_158` | `node_158` (A38) | 10.0000 | 10 | 0.000000 |  |
| `l1_159` | `l1_159_plain_warm` (A99) = `node_159` (A38) | 10.0000 | 10 | 0.000000 | confirmed twice, independently |
| - | `s3_far_BL389484_TR018470` (A85) | 7.0000 | 7 | 0.000000 | A85 node, not a level-1 cell |

## Price and projection

| item | value |
|---|---|
| T4 | 5.09 CPU-h, 55 cells |
| T5 | 10.27 CPU-h, 82 cells (cap 10 CPU-h; the cap is checked before each cell, so the last cell of each shard overruns it) |
| **total** | **15.36 CPU-h** |
| distinct level-1 cells certified | **17** of 216 |
| per level-1 cell | 43.2-100.3 CPU-h |
| **CPU-h removed** | **735-1,705** (level-1) + 32-75 (level-2) + 0.7-1.6 (level-3) = **768-1,782** |
| return | **48x-111x** |

For contrast, A115's own corner rows cost 13.4 CPU-h for one pass over the same 216 cells and removed nothing (net -13 CPU-h).

## What is left

* 32 of the 36 T4 kill-candidates still FAIL after 900 s + 2 witness-feedback rounds.
* Of A38's 82 never-run level-1 cells, 48 were reached (2 certified, 27 kill-candidate, 16 alive, 3 knife-edge); 34 were not reached at the cap, and neither were most of the 60 open level-2/3 cells.
* Every record is resumable: `results/t4/<nid>.json`, `results/t5/<task>__<nid>.json`.

## Pointers

* driver `code/t5.py` (tasks `a121`, `cand`, `notrun`, `rest`); records `results/t5/`; run log `results/t5_runs.jsonl`; pools `results/t5_plan.json`; summary `results/t5_summary.json`; certificates `certs/t4_<nid>_s<stage>.json`; logs `logs/t5_s0.log`, `logs/t5_s1.log`
* the first pass: `notes/t4_report.md`; the control that started it: `code/control115.py`
