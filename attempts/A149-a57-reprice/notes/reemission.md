# A149 Task B — the day's exact-core re-emission, and the one number that reorders the chore

**Headline: the FAIL population is where this lever pays, by a factor of 3.9.**

| population | nodes | CPU-h | certified kills | rate | CPU-h per kill |
|---|---|---|---|---|---|
| recorded **ALIVE** | 125 | 13.86 | 20 | **16.0 %** | 0.693 |
| recorded **FAIL** | 112 | 15.42 | **70** | **62.5 %** | **0.220** |
| **total** | **240** | **29.66** | **93** | **38.8 %** | 0.319 |

And the same lever on the protected tier, for the first time:

| population | nodes | CPU-h | certified kills | rate | CPU-h per kill |
|---|---|---|---|---|---|
| **A60 alive trump5**, scope `exH` | 218 (214 decided) | 17.07 | **87** | **40.7 %** | **0.196** |

Across both lanes: 0 ERROR, 7 WALL-CAP (never a verdict — 0 on A57, 4 on A60, 3 in the A60 lane's
earlier passes), and **not one node in either lane reached FAIL-with-holes**, so `verify_case_v3`
was never needed and both v3 ledgers are empty by construction. Every kill is
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
| masked G1 nodes | 18 + `Y0275` | **14** | **73.7 %** |

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
  python processes that fired as holds rather than oversubscribe alongside A156 and A136,
  per-node process wall 1,500 s, free-physical and commit gates on every launch.

## A60 (trump5) — the protected tier's first exact-core measurement

218 alive trump5 nodes, **87 certified kills (40.7 % of 214 decided) in 17.07 CPU-h**, 0.196 CPU-h
per kill, 4 WALL-CAP (never a verdict), 11 LOST-KILL-ON-RESOLVE, **0 FAIL-with-holes** so no v3.
All 87 are level 1; by shadow family S01 60, S07 5, S03 5, and thirteen others 1–2 each.

The change is one number: **only the conditioned square's core**. A60's pins are already exact
boxes and must keep the corpus core `16383999967232/32768001953125` — at `a = 1/2` the cores of two
slots exactly 1.0 apart would touch and the `budget = n − #cores` bridge would lose pairwise
disjointness (measured gap 6.2e-8, re-checked before every node). So the whole gain is H's, and it
is **×1.048 per side on average and ×1.109 at most**, against A57's pin gain of ×1.006. That is why
the same lever is worth 40.7 % here and 16.0 % on A57's alive nodes.

The coordinator's named start `c0_Y0215` is **not** among the kills: τ moves only
5.5000000000000435 → 5.499999999825466. The near-simple BL(1,1) square at tilt 82–90° sits half a
unit above budget; the core is not what holds it.

## A166's stock-core reversion: audited, and this attempt was never on the broken path

`code/certaudit149.py` recomputes A135's exact core from the box each certificate itself carries
and compares it with the carried `a`, over all 233 certificates written here.

* **A57: 137 of 137 clean** — the exact core is written on every box. Both node paths emit through
  A135's `emit135.make_cert`, which reads the LIVE `Hyp`; `caselp.make_certificate` is never
  called, and A135 wrote `make_cert` for exactly this reason.
* **A60: the five pins are the corpus core by design** (see above), which the auditor labels
  "STOCK"; H is exact in all 96. The shortfall is **3.1e-8 of the half-side, six orders of
  magnitude below A166's measured 1.4–15 %**, and it is the conservative direction — it can cost a
  kill, never soundness.

`code/recheck149.py` then re-verified **all 55 stored non-PASS certificates with no re-solve** (the
measure is on disk: `emit135.certify` dumps the certificate before taking the verdict, so nothing
needed re-solving). **0 recovered.** 40 LOST-KILL-ON-RESOLVE re-FAIL deterministically — real
holes — and 15 TOO-TIGHT have a written total ≥ budget, which the verifier's claim forbids, so they
cannot PASS without a better τ. For A170's audit: every non-`NO-KILL` outcome has its atoms and
weights on disk under `certs/`; `NO-KILL` never built a certificate because τ ≥ budget.

## Operational finding: the wall kills the node but not its verifier grandchild

At the close of the run one A149 process was still alive: `verify_case.py` on
`certs/a60/c0_Y1099__exH.json`, **orphaned** (its parent gone), started 00:54:32 and holding a core
for **2,914 CPU-seconds** by the time it was reaped. `c0_Y1099` is one of the four WALL-CAP rows:
`run149.py` (like `run137.py`, from which it descends) enforces the 1,500 s per-node wall by
`p.kill()` on the **node** process, but the node's own `emit135.run_case` child — the frozen
verifier — is a *grandchild* and survives, then runs to completion with nobody left to read its
result. This is the hazard `pausegate.orphans()` was written for ("a `certify.py` ran 11.3 h after
its parent shard was restarted, burning a core unattributed"), reproduced from a different
direction: not a restart, but the wall itself.

**Deployable fix, and it belongs in `run137.py` as much as here:** kill the process *tree*, not the
process — on Windows `subprocess.Popen(..., creationflags=CREATE_NEW_PROCESS_GROUP)` plus
`taskkill /T /F /PID`, or a job object. Until then, a WALL-CAP node leaves a verifier behind that
the box-count gate cannot see as work, which is precisely how a 16-process ceiling gets quietly
over-subscribed. The verdict itself is unaffected — WALL-CAP is never a verdict and `c0_Y1099`
keeps its prior state.
