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

**A141 (2026-09-07), the K′ lane leaf on this list and on the wider open pool:** `s3_far_BL389484_TR018470` is DEAD — unconditionally, by a *pair* contradiction (its conditioned squares h0 and h1 share a certified rational point once h0's box is clipped to the container, `shared_point_same_square`), and separately at BL by `LANE_K′ + M ≤ 1`; the other eleven of the twelve survive (five are near-misses at TR with `LANE_K′ ≤ 1, M = 1`, i.e. one free square plus the conditioned one). Over A115's whole open k0 pool the leaf kills **26 further distinct level-1 cells** (A38 l1 idx 156, 157, 162–167, 198–215), 9 level-2 and 3 level-3 records — all DEAD BY POLYCORE LANE **pending Lean** (`LaneCoverSound`, `K0Widen`) and pending k1_00's tree (K0-O1); certificates and an independent checker in `attempts/A141-polycore-lane/{certs,code/check141.py}`, ledger `results/polycore_lane_kills.jsonl`.

**A159 (2026-09-08), the near-miss corners jointly — NOTHING further comes off this list.** A141's 28 two-crowd witnesses are all EXACT (interval arithmetic at 60 dps; **28 of 28** survive, the poses are container-frame and H's pose lies inside its own box B in every one), and a direct joint search raises the count to **30 of the 44 near-miss corners** with a realised two-crowd at the widened box — so by Lemma A159-1 (the piece of any complete split of B that contains a realised H has `lane_ub ≥ 1` and `m_j = 1`, hence total ≥ 2) no lane leaf, joint or not, can ever fire at those 30. On the **14** with no realised two-crowd the joint split was run on 9 distinct box classes (`l1_158` twice, `l1_159`, `l2_p114_011`, `l3_pp114_001_000`, `node_120`, `node_125`, `node_151`, `node_160`) and closed **0**; every open piece carries a *certified* `lane_ub ≥ 1` (`no_lane_bound = 0`), so this is geometry and not cover budget, and the frontier GROWS with depth (`l1_158`: 15 open pieces at depth 9 → 349 at depth 15). The canary is clean (`l1_153` TR: the piece containing its exact witness keeps total = 2 over 15 depths), and the sampled line agrees — 20,000 uniform poses of H per corner, 16,584-20,000 of them in `B_meet`, **0 hits at both widths** on all 14 (the one uniform hit anywhere the optimiser missed, `l1_192_sh3_warm` TR at `w = 0`, is outside this list and re-verified exact). **0 certificates, 0 cells removed, the price table below unchanged.** Ledger `attempts/A159-k0-nearmiss-joint/results/joint_kills159.jsonl`; the 294 A141 certificates re-pass an extended independent checker (`code/check159.py`, with a guard that fails any kill at a corner carrying a proved two-crowd): **294 PASS, 0 fail**.

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


## A170 addendum (2026-09-09) — the 128 `kill-candidate (cert FAIL)` cells re-certified with A135's EXACT cores: **0 recovered**

A166 found an emission bug in shared machinery: `caselp.make_certificate` (and `caselp92`'s copy, which
this attempt's `t5.py:36` imports) ends with `hyp = Hyp.from_json(res["hyp"])`, and `Hyp.__init__`
recomputes `self.cores = [b.core() for b in boxes]` — the STOCK cores — discarding the `cores` field the
json carries. On a lane whose LP ran with A135's certified EXACT cores that manufactures holes, and A166
asked whether the 127 `kill-candidate (cert FAIL)` cells of `cells140.open_pool` (which is derived from
this attempt's `t4_runs.jsonl` / `t5_runs.jsonl`) were such spurious FAILs.

**They are not.** A170 re-emitted the certificate for **every** `kill-candidate` record in the pool —
128 of the 166 open records — from this attempt's **stored** LP measure
(`results/nodes/<nid>.t{4,5}.lp.json`, keys `atoms_all` / `rows_all` / `hyp`; **no LP was re-solved**),
with each core enlarged to `exactcore.exact_a`, at this attempt's own scale rule
(`scale = max(1.005, min(1.4, (budget − 0.005)/τ − 0.002))`, `t4.certify_plain`), and ran the FROZEN
`verify_case.py` (sha `521cb01f…`, byte-identical to this attempt's own copy) at depth 56:

| | n |
|---|---|
| records re-certified | **128** |
| **PASS** | **0** |
| FAIL with genuine holes (6–52 per cert, `exact_mass = 0`) | 119 |
| FAIL on `total ≥ budget` (no core can repair) | 9 |
| core enlargement `a_exact / a_carried` | min 1.0062, median 1.0326, max 1.1179 |

The reason is a property of the population, not an accident: **the T4/T5 LP ran on the STOCK cores too**,
so the certificate it wrote was consistent with its LP — the reversion is present in the code path but
had nothing to revert. Every one of the 128 is a single-box hypothesis at `budget = 10` whose LP did not
converge (`converged: false, dead_unconverged: true`) with `τ ≈ 9.9767–9.9786`, i.e. ≈ 0.022 of slack;
the rounded-up measure lands at `total ≈ 9.977` and a 0.6–11.8 % wider core does not reach the holes.

**Hand-off consequence.** The 71 stage-A kill-candidates still owing the 900 s continuation, and the 32
persistent `cand` cert-FAIL cells skipped by instruction, are **not** collectable by a free re-emission.
They need LP work (longer cap / witness feedback / a new row), exactly as `notes/t6_report.md § What is
left` says. Nothing in this attempt was written to: A170's patched certificates and records live under
`attempts/A170-certfix/{certs,results}` (`results/recert170_k0.s*.jsonl`, `notes/recovered.md`).
