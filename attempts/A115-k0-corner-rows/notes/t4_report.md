# A115 follow-up — the PLAIN warm re-solve pass over A99/A85's open k0_00 cells

> **VERDICT.  A plain 240 s warm re-solve — no corner rows, no new mathematics — certifies 10 of the 55 open k0_00 cells it reached, including **7 of A99's plain level-1 cells**, for 5.09 CPU-h.  Against A99's own projection (9,341–21,661 CPU-h over the 216 level-1 cells, 43.2–100.3 CPU-h each) that removes **303–702 CPU-h** — a 59×–138× return, versus the corner rows' net −13 CPU-h.**  It also turns 4 cells into *converged* ALIVE verdicts (τ = budget exactly, minmass = 1.000): those are un-killable by this LP at this node, not merely undecided.

The pass is what A115's attribution control (`code/control115.py`) implied: for the cells where the corner-row certificate passed, the *plain* certificate passed too. The campaign's stored node results are simply row-generation-incomplete; 240 s of warm continuation from their own `atoms_all` + `rows_all` finishes the job on the cells that were close.

## Verdicts

| verdict | A99 | A85 | total |
|---|---|---|---|
| CERTIFIED DEAD | 9 | 1 | 10 |
| kill-candidate | 27 | 9 | 36 |
| knife-edge | 3 | 1 | 4 |
| alive | 5 | 0 | 5 |
| **processed** | 44 | 11 | **55 of 64 open cells** |

`kill-candidate` = η ≤ −10⁻³ but the first-pass certificate FAILED (the LP is still row-generation-incomplete); `knife-edge` = |η| < 10⁻⁶ after the 900 s stage-2 re-solve; `alive` = τ > budget.

## The 10 CERTIFIED DEAD cells (frozen `verify_case.py`, depth 56)

| cell | src | τ₀ → τ | budget | converged | minmass₀ → minmass | scale | total | LP s | verify s | prior A38 | prior A113 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `l1_005_plain_warm` | A99 | 8.0000 → 8.0000 | 10 | True | 1.000 → 1.000 | 1.2474 | 9.9790 | 20 | 2 | dead | KILL(LP,uncertified) |
| `l1_005_sh2adj_warm` | A99 | 8.0000 → 8.0000 | 10 | False | 0.000 → 0.000 | 1.2474 | 9.9790 | 284 | 14 | - | - |
| `l1_005_sh3_warm` | A99 | 8.0000 → 8.0000 | 10 | False | 0.500 → 0.000 | 1.2474 | 9.9790 | 283 | 26 | - | - |
| `l1_049_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.000 → 1.000 | 1.1086 | 9.9770 | 222 | 21 | dead | KILL(LP,uncertified) |
| `l1_093_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.500 → 1.000 | 1.1086 | 9.9770 | 46 | 64 | dead | FAIL |
| `l1_126_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.440 → 1.000 | 1.1086 | 9.9770 | 109 | 1 | dead | KILL(LP,uncertified) |
| `l1_137_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.624 → 1.000 | 1.1086 | 9.9770 | 219 | 2 | dead | KILL(LP,uncertified) |
| `l1_170_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.615 → 1.000 | 1.1086 | 9.9770 | 156 | 2 | NOTRUN | NOTRUN |
| `l1_181_plain_warm` | A99 | 9.0000 → 9.0000 | 10 | True | 0.400 → 1.000 | 1.1086 | 9.9770 | 160 | 14 | NOTRUN | NOTRUN |
| `s4_near_BL357619_BR004483_TR191404` | A85 | 4.3333 → 4.3333 | 5 | False | 0.833 → 0.896 | 1.1507 | 4.9863 | 268 | 10 | - | - |

**What is new versus what is upgraded.**  `l1_170` and `l1_181` had NO prior verdict at all (A38 `notrun`, A113 `NOTRUN`) — two previously unprocessed level-1 cells, now certified dead. `l1_005`, `l1_049`, `l1_093`, `l1_126`, `l1_137` were LP-killed by A38 but **uncertified** (A113: `KILL(LP,uncertified)`, and `l1_093` was an outright certification `FAIL`); this pass upgrades each to a frozen-verifier certificate, which is what the tree needs to actually remove them.  The two `l1_005_sh*` cells belong to A99's R2 pattern-branched tree (an exact ×15 cost multiplier, not the route), so they carry no cost credit.

## The 4 CONVERGED-ALIVE cells (the hard negative)

| cell | src | τ | budget | η | minmass |
|---|---|---|---|---|---|
| `l1_071_plain_warm` | A99 | 10.0000 | 10 | +0.000000 | 1.000 |
| `l1_104_plain_warm` | A99 | 10.0000 | 10 | -0.000000 | 1.000 |
| `l1_159_plain_warm` | A99 | 10.0000 | 10 | -0.000000 | 1.000 |
| `s3_far_BL389484_TR018470` | A85 | 7.0000 | 7 | +0.000000 | 1.000 |

τ = budget exactly with minmass = 1.000 and `converged = True`: the case-LP has reached its optimum and it is not below the budget, so **no amount of further LP time kills these cells**. They match A113's "un-killable at the measured LP state" list and upgrade it from *measured* to *converged*.

## Price and projection

| item | value |
|---|---|
| cells reached | 55 of 64 open (A99 53 + A85 11); the 9 not reached are listed in `results/t4_summary.json` |
| CPU spent | 18318 s = **5.09 CPU-h** (cap 5 CPU-h; the cap is checked before each cell, so the last cell of each shard overruns it) |
| mean per cell | 314 s LP + 22 s verifier |
| certified plain level-1 cells | **7** |
| A99 frontier | 9,341–21,661 CPU-h over 216 level-1 cells = 43.2–100.3 CPU-h each |
| **CPU-h removed** | **303–702** |
| return on the 5.09 CPU-h spent | **59×–138×** |

Compare A115's main result: corner rows cost 13.4 CPU-h for one pass over the same 216 cells and removed nothing (net −13 CPU-h). The cheap thing works and the clever thing does not.

**Next, if wanted (not run here).** 9 of the 64 open cells were not reached, and the 36 `kill-candidate` cells all have η ≤ −10⁻³ with a failing first-pass certificate — the obvious continuation is a second stage at 900 s with A85's witness-feedback rounds on exactly those, and the same pass over the level-1 cells A38 left `notrun`.

## Pointers

* driver `code/t4.py`; per-cell resumable records `results/t4/<nid>.json`; run log `results/t4_runs.jsonl`; cell order and the un-reached list `results/t4_plan.json`, `results/t4_summary.json`; certificates `certs/t4_<nid>_s<stage>.json`; logs `logs/t4_s0.log`, `logs/t4_s1.log`
* the control that motivated it: `code/control115.py`, `results/control.jsonl`
