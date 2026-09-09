# A149 Task B — the day's exact-core re-emission, and the one number that reorders the chore

**Headline: the FAIL population is where this lever pays, by a factor of 3.9.**

| population | nodes | CPU-h | certified kills | rate | CPU-h per kill |
|---|---|---|---|---|---|
| recorded **ALIVE** | 125 | 13.86 | 20 | **16.0 %** | 0.693 |
| recorded **FAIL** | 112 | 15.42 | **70** | **62.5 %** | **0.220** |
| **total** | **237** | **29.28** | **90** | **38.0 %** | 0.325 |

0 WALL-CAP, 0 ERROR, and **not one node reached FAIL-with-holes**, so `verify_case_v3` was never
needed and `results/superseded_by_exactcore_v3_A149.jsonl` is empty by construction. Every kill is
the FROZEN `verify_case.py` (521cb01f) on a `case-measure-certificate-v1` whose only change from
the corpus's own is the core half-side.

**Why the split, and what it means for the chore.** A FAIL is a node whose LP was already below
budget but whose certificate had holes; a slightly larger core closes the holes without the LP
having to move at all. An ALIVE node needs τ itself to fall. So the exact core is really a
**certificate-repair** tool that happens to be also an LP lever — and the queue should be run
**FAIL-first**. A137's night ran ALIVE-only (its `targets137.py` defaults `--include_fail 0`), and
today's order was ALIVE-then-FAIL as instructed; on the measured rates the reverse order would have
banked the same 70 kills in 15.4 CPU-h instead of 29.3.

**A145's `frac_exact` predictor, at both ends, on n = 237** (PAUSED v3 §C.1 left the bottom
untested at n = 2):

| band | ALIVE | FAIL | all |
|---|---|---|---|
| ≥ 0.60 | 2/2 | 17/23 = 73.9 % | 19/25 = **76.0 %** |
| 0.45–0.60 | 1/2 | 20/27 = 74.1 % | 21/29 = **72.4 %** |
| 0.30–0.45 | 11/39 = 28.2 % | 21/42 = 50.0 % | 32/81 = **39.5 %** |
| < 0.30 | 6/82 = **7.3 %** | 12/20 = 60.0 % | 18/102 = **17.6 %** |

Two readings. (i) **On the ALIVE population the predictor is sharp and monotone** — 7.3 % below
0.30 against 28.2 % in 0.30–0.45 — so A145's rule was directionally right and A137's "untested, not
refuted" resolves *for* it: the `< 0.30` band is 4× weaker, not worthless (18 kills), and should be
run last. (ii) **On the FAIL population `frac_exact` barely discriminates at all** (74/74/50/60 %),
because what closes a FAIL is not how much dual weight is impossible but whether the certificate's
holes are inside the core's growth. Ranking a FAIL queue by `frac_exact` buys almost nothing;
running it at all buys 62.5 %.

A137's published band rates (37.9 / 20.0 / 23.8 %) are ALIVE-only and are consistent with column 1
here at the sample sizes involved.

## The two priority nodes the coordinator named

**`k5_11_interior_Y0130` — ALIVE under both cores, and the polygon core does not help.**

| arm | core on the conditioned box | τ | converged | verdict |
|---|---|---|---|---|
| recorded | `Box.core()` | 5.500000000004487 (η +0.500) | no | ALIVE |
| exact square core, FROZEN verifier | 0.395282921 | **4.99999999999996** (η −4e-14) | no (420 s cap) | NO-KILL |
| **K′-pruned polygon core** (A135 `emitpoly135`, v3-capable) | 16-vertex polygon, area **0.681528** vs the square's 0.624994 (**+9.0 %**) | **5.000000 exactly** | **yes**, 64 s | NO-KILL |

The exact square core takes η from +0.500 to −4e-14 and stalls exactly at the budget; the polygon
core, which is 9 % larger in area, **converges at exactly 5.000000**. No certificate was emitted
(total ≥ budget), so no v3 run was needed and none was made. A145's reading of the support — 7 of
10 columns K′-only impossible, carrying weight 3.5 — is a correct description of the support that
the recorded solve happened to pick; the LP simply finds another measure at exactly the budget. The
node is genuinely alive at both cores and needs a different leaf, not a bigger core.

**`k5_11_interior_Y0275` — CERTIFIED KILL, frozen verifier, first re-solve.**
τ 4.999999999999965 → **3.999999999999985** (η −3.5e-14 → **−1.000**), converged in 770 s,
certificate total 4.12 < 5, `verify_case.py` **PASS** in 33.7 s (673,994 boxes, 15,772 exempt,
0 holes). The K′ arm was not run: a kill under the frozen verifier is strictly better than a v3
kill, so there was nothing left to buy.

## Third duplication finding — and it is the one that cost kills

`Y0275` **was not in any queue**, and neither were 18 others. `targets137.py` — and anything that
walks `tree_*.jsonl` into a dict keyed by id — builds a **last-wins** map. An id names a node in
*both* window trees: the **G1** tree (slack pins, δ = 1e-2, pin core 0.492928902) and the **L1**
tree (eps-fat pins, core 1/2 − 2.98e-8). They are different nodes with different hypotheses —
PAUSED v3 §C.3 makes exactly this point for the fold-in — and when the L1 row is PASS while the G1
row is ALIVE or FAIL, the map records the id as dead and the **open G1 node disappears from every
queue**.

**19 such nodes.** `code/targets_masked.py` enumerates them
(`results/masked_by_tag_collision.json`); they were run as their own lane and the yield is the
highest of anything today:

| | n | certified kills | rate |
|---|---|---|---|
| masked G1 nodes | 18 + `Y0275` | **10** so far | ~56 % |

Fix, and it is the same shape as the other two: key the corpus by **(tag, id)**, not `id`. A
one-line change in every consumer, and PAUSED v3 §C.3 already has the reason written down.

## Files

* ledger `results/superseded_by_exactcore_A149.jsonl` (A137's format + `box_source`, `frac_exact`,
  `frac_exact_band`, `verifier`); v3 ledger `..._v3_A149.jsonl`, **empty**;
* summary `results/day149_summary.json`; raw rows `results/exact_reemit_*.jsonl`;
* certificates `certs/*__exall.json`, polygon arm `certs/poly/`, A60 `certs/a60/`;
* the K′ arm's driver `code/poly149.py`, output `results/poly149.jsonl`;
* box discipline: 4 workers at Normal priority, `ProcessorAffinity 0xFFFF` on every process
  (P-core threads only; `code/affinity149.ps1` sweeps every 5 min), a machine-wide gate of 16 lab
  python processes that fired **119 times** as holds rather than oversubscribe alongside A156,
  per-node process wall 1,500 s, free-physical and commit gates on every launch.
