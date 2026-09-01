# A54 — the four straggler strata: semantics, arbiters, rung-by-rung record

Everything here is at s0 = 969271/250000 = 3.877084 and uses A53's definitions (Young-form simple
squares, corner slot grid, residual guard LP). A53 code is copied unmodified into `code/`
(`certify.py` alone carries one additive A54 flag, `--scale_cap`, documented in S2 below);
A53's own results are read, never written. A29 untouched.

## S0 — what a kill means, and what τ does and does not say

Node = the k pinned slot squares of a stratum (degenerate core boxes), budget = 11 − k.
τ = the value of the guard LP restricted to the rows AND the atoms generated so far. Dropping
rows lowers the optimum, restricting the atom set raises it, so

    τ_LP bounds τ* in NEITHER direction        (τ* = the true residual guard value)

— a point worth stating flatly, because it is easy to mis-read a run: **τ < budget is not a
kill, and τ ≥ budget is not a survival.** The sole arbiter of a kill is an exact rational
measure certificate accepted by `verify_case.py` (interval B&B over (t, cx, cy), exact
witnesses); the arbiter of the opposite verdict would be a dual witness whose coverage is
verified ≤ 1 everywhere, which this lab does not have (GAP-A54-2). Observed live: k5_16's
restricted LP sat at exactly 6.000000 with minmass 1.0 for one iteration and then fell to
5.9725 as column generation continued — no conclusion may be drawn from either number.

## S1 — the straggler set and its Trump geometry

Trump's skeleton (A53 L4, k=5): BL staircase {(½,½),(3/2,½),(½,3/2)} + BR corner + TR corner.

| node | slots | relation to Trump's tuple |
|---|---|---|
| k6_23 | trump5 ∪ {(½, s0−½)} | Trump + TL corner (the unique open k=6 class) |
| k5_11 | trump5 with TR ↦ TL | Trump's staircase + BR, other corner moved |
| k5_13 | BL {(½,½),(½,3/2)} + TL {(½,s0−½),(3/2,s0−½)} + TR | two 2-cell diagrams + a corner |
| k5_16 | corners4 ∪ {(½,3/2)} | all four corners + one |

k5_11 ⊂ k6_23 and k5_16 ⊂ k6_23 (as slot sets), so a kill of either k=5 node implies the
k=6 kill, never the converse; k6_23 carries the largest relative headroom and is the node whose
death would close the k ≥ 6 tier of A53's cap (L5).

**Fractional structure of all four (measured, A53 node LPs, zone weights of the LP packing):**
interior zone [1.1, 2.777]² carries 2.74–2.99 of the weight, of which 2.56–2.93 is tilted
(5–85°), plus 1.00 in each of two or three side zones and ≈0 in the corners. Trump's own
residual (trump5, provably alive) has exactly this profile: interior 2.97 (2.83 tilted),
side_R 1.00, side_T 1.00. **The stragglers' LP optima are Trump's ghost with a different
corner decoration** — that is the precise sense of "Trump-satellite".

## S2 — rung 2 has less room than A53 thought, and it is not the blocker

A53 attempted certification only when τ·1.03 < budget and always at scale ≤ 1.03. The available
scale is budget/τ: 1.021 (k6_23), 1.016 (k5_11), **1.068 (k5_13)**, 1.0018 (k5_16). A54's
`certify.py --scale_cap` lifts the cap. Measured (A54 probe, k5_13 at scale 1.06, exact
verifier): still FAIL, worst hole exact mass 484281/500000 = 0.9686 — i.e. at unit scale that
placement carries only 0.913. **Scale headroom is not the blocker; LP convergence is.**
A hole of mass m needs scale ≥ 1/m, so certification needs τ*·(1/m) < budget, i.e. the LP must
be converged to within a factor budget/τ of true coverage.

## S3 — rung 4 (wastage / dead area) is a priori dead at these nodes

The A23/A25 ledger needs certified pairwise-disjoint dead area > s0² − 11 = 4.0318…
Every pin of every straggler is an axis-parallel unit square flush in a container corner or
against a wall, and this is exactly the configuration whose certified dead area is **exactly
zero** (A26: 16 of 1070 admissible band cells strand 0, all of them axis-parallel-on-wall;
A47: the near-flush corner cell certifies exactly 0, Trump-confirmed). The free squares are
not pinned at all, so they contribute nothing. Hence the ledger's value at every straggler
node is 0 vs a budget of 4.0318 — the T2 route cannot fire without first sub-stratifying at
least three mid-tilt squares into ≤ 0.075-wide cores (A25's MIN k = 3 result, 3 × 1.4023 =
4.2070 > 4.0318 at s0), a depth at which T1 has already decided the node (A24 (v): T2 fired at
zero tree nodes). Recorded as an assessment, not a campaign: no compute spent.

## S4 — canary discipline

trump5 is never certified. Two standing checks:
(i) A53 V6 rerun (`check_trump_feasible.py`): Trump's six free squares are admissible, pairwise
disjoint (min SAT gap −1.0e-15 = exact touch) and KEPT by the row filter of the trump5 node ⇒
τ*(trump5) ≥ 6 = budget. PASS (rerun 2026-08-31, A54).
(ii) `substrat.trump_realizes` — before any child node of a sub-stratification is certified, the
node's hypotheses are tested against Trump's 11 exact placements: a YES box is realized iff one
of his squares has (centre, θ) **inside the box** (not merely overlapping its core — the weaker
predicate is the bug this check was written to avoid), and a NO-family must contain none of them.
Self-test: trump5 → realized (never certify), corners4/k6_23/k5_11/k5_13/k5_16 → not realized
(certification legitimate).

## S5 — results and their arbiters (A54 verification log)

- **W1 (k6_23 KILLED).** `certs/k6_23.json`: 6 cores (the pin set), 501 atoms, total
  997089/200000 = 4.985445 < budget 5, scale 1.0160 (ceiling 5/τ = 1.0187). Produced by
  `ladder.py --name k6_23 --tag r2` (rung-1 merged-warm LP, τ = 4.907742, 38536 rows, 2787
  orbits, 2014 s) + 2 witness-feedback rounds (728 s). Verified by `verify_case.py` inside the
  loop and RE-VERIFIED independently at `--depth 60 --jobs 6`: PASS, 2449492 boxes, max depth
  used 47, 31.1 s, 0 witnesses. Consequence: **all 33 k = 6 Young classes now carry exact
  certificates**, so A53's L5 cap is unconditional and every stratum with k ≥ 6 is certifiably
  empty (A53's V9 containment check now rests on 33/33).
- **W2 (k5_13 KILLED).** `certs/k5_13.json`: 5 cores, 106 atoms, total 5962551/1000000 =
  5.962551 < budget 6, **scale 1.0600** (ceiling 6/τ = 1.0667 — unreachable under A53's 1.03
  cap). Produced by `ladder.py --name k5_13 --tag r1b` (τ = 5.625000, memory-safe settings)
  + 2 rounds. Re-verified independently at depth 60: PASS, 2589162 boxes, max depth 43, 48.2 s.
- **W3 (k5_11 open).** rung-1 τ = 5.899605 → 5.905058 (two passes, 24133 rows), coarse minmass
  0.9787. Certification at scale 1.0141 (total 747933/125000 = 5.983464) FAILS on exact holes,
  the worst at θ = 53.2872°, centre (1.699716, 1.901125), exact mass 490739/500000 = 0.981478 —
  a deep-interior mid-tilt placement, i.e. the ghost's own home. Closing it needs the measure
  1.9 % better there while total stays < 6 (ceiling scale 1.0170).
- **W4 (k5_16 open, the thinnest).** rung-1 τ = 5.972514 (20202 rows, 7004 orbits, 2596 s);
  auto-scale 1.0050 already gives total 6.002710 ≥ budget, so certification is REFUSED before
  the verifier runs (`certify.py` rc = 3). A second, column-heavy pass moved τ to 5.9860.
  η ≈ −0.014…−0.028: the pins (four corners + one) leave Trump's ghost essentially intact.
- **W5 (rung-3 probe, measured).** k6_23 / zone side_T = [1.1,2.777]×[0.5,1.1]:
  NO child τ = 4.000000 vs budget 5 (η = −1.000, LP-dead); YES child Y05 (0.84 × 0.30 × 30°,
  rational core half-side a = 0.0385) τ = 4.500000 vs budget 4 (**η = +0.500, ALIVE**).
  Exact cover audit of one shallow level (kept ∪ vacuous = the whole zone × [0,90], volume
  ratio 1.0000, 0 boxes without a rational core): available a is 0.202–0.227 (corner zones),
  0.038–0.043 (side), 0.022–0.025 (interior) — all below A24 (iii)'s measured kill threshold
  (a ≥ 0.35 kills, ≈ 0.31 marginal, ≤ 0.28 alive). One level at a ≥ 0.31 needs centre boxes
  ≤ 0.1 and θ windows ≤ 15°: ≈ 612 children per side zone, ≈ 6000 for the interior.
- **W6 (canary).** `check_trump_feasible.py` rerun: PASS (τ*(trump5) ≥ 6). trump5 never
  certified, never branched. `substrat.trump_realizes` self-test as in S4.
- **W7 (operational).** HiGHS raised `MemoryError: bad allocation` at 32k rows × 6k columns with
  four such jobs on a 31.7 GB machine. Fix used afterwards: prune COLUMNS only
  (`--prune_cols 3 --max_cols_add 350 --col_stop_cov 1.03`); pruning columns can only raise τ,
  so it is sound for a kill, while pruning rows (A53's `--loop_cols` re-solve, strikes 6)
  destroys the accumulated coverage that both kills depended on.
