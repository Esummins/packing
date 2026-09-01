# A55 verification log (k = 4 sweep)

Container s0 = 969271/250000. Budget at k = 4 is 7. Kill arbiter = `verify_case.py` (exact
rational interval B&B). A53/A54 artefacts read-only; A29 untouched.

## V1 — census and naming
`code/k4_classes.py` reproduces A53's D4 census (1,1,3,6,**14**,22,33,35,30,18) and fixes
`k4_00 … k4_13`; `k4_13` verified identical (up to D4) to A53's own `corners4` slot list.
Outputs `results/name_to_slots.json`, `results/k4_lattice.json`.

## V2 — canary (i): trump5 feasibility, rerun under A55
`code/check_trump_feasible.py`: Trump's six free squares all admissible and KEPT by the trump5
row filter; min pairwise SAT gap −9.992007e-16 (exact touch). **FEASIBLE ⇒ τ*(trump5) ≥ 6. PASS.**

## V3 — canary (ii): the four unkillable k = 4 classes (K2)
`k4_03, k4_06, k4_08, k4_11` are exactly the D4 sub-skeletons of trump5 (computed, not assumed).
By K1 each has τ* ≥ 7. All four were run with `--no_cert`; **no certificate was ever attempted
on them.** Measured LP values sit at budget as predicted:

    k4_03  τ = 7.000000000001165   k4_06  τ = 7.019956   k4_08  τ = 6.986580   k4_11  τ = 6.985585

k4_03's τ = 7.000000000001 is the k = 4 reproduction of A14/A16's "four exact corners ⇒ τ = budget"
signature. (Per A54 S0, τ < budget at k4_08/k4_11 is NOT evidence of death — K2 is the arbiter.)

## V4 — the EIGHT exact kills, and their independent re-verification
Produced by `code/sweep4.py` → `ladder.py` (rung 1 merged-warm LP, row pruning OFF, column pruning
only; rung 2 witness-feedback certification at scale cap = budget/τ). Pass = which escalation
round closed it (s1 = 900 s LP / 3 rounds, s2 = 1800 s / 6 rounds, s3 = 3600 s / 8 rounds; each
pass merged-warm-starts from every artefact of the previous ones).

| node | τ | η | pass | certificate total | budget |
|---|---|---|---|---|---|
| k4_00 | 6.662982 | −0.337018 | s3 | 436367/62500 = 6.981872 | 7 |
| k4_01 | 6.651341 | −0.348659 | s2 | 1396391/200000 = 6.981955 | 7 |
| k4_02 | 6.666667 | −0.333333 | s2 | 3490873/500000 = 6.981746 | 7 |
| k4_04 | 6.625000 | −0.375000 | s2 | 1745461/250000 = 6.981844 | 7 |
| k4_07 | 6.000000 | −1.000000 | s1 (round 0, 12 atoms) | 1745751/250000 = 6.983004 | 7 |
| k4_09 | 6.588718 | −0.411282 | s2 | 698211/100000 = 6.982110 | 7 |
| k4_10 | 6.500000 | −0.500000 | s1 | 6982001/1000000 = 6.982001 | 7 |
| k4_12 | 6.334746 | −0.665254 | s2 | 3491203/500000 = 6.982406 | 7 |

**Independent re-verification, every one, at `--depth 60` in a fresh process from the cert file
alone:**

    k4_00  PASS  1494990 boxes, 0 witnesses, max depth used 44,  36.5 s
    k4_01  PASS  1974776 boxes, 0 witnesses, max depth used 47,  71.5 s
    k4_02  PASS  2480066 boxes, 0 witnesses, max depth used 44,  66.3 s
    k4_04  PASS  4582778 boxes, 0 witnesses, max depth used 44, 146.4 s
    k4_07  PASS    80154 boxes, 0 witnesses, max depth used 42,   1.7 s
    k4_09  PASS  4192860 boxes, 0 witnesses, max depth used 44, 158.7 s
    k4_10  PASS  2325594 boxes, 0 witnesses, max depth used 43,  45.5 s
    k4_12  PASS  7439194 boxes, 0 witnesses, max depth used 44, 173.6 s

All eight: `vacuous = 0`, exempt = core only, `nofam = 0`. Max depth used is well inside 60, so no
verdict is depth-limited.

## V4b — THE SWEEP IS EXACTLY SHARP (the headline check)
Certified-empty at k = 4 = {k4_00, k4_01, k4_02, k4_04, k4_07, k4_09, k4_10, k4_12} (8).
Survivors = {k4_03, k4_05, k4_06, k4_08, k4_11, k4_13} (6). Independently, the k = 4 classes
contained in at least one OPEN k = 5 class ({k5_11, trump5, k5_16}) are

    k4_03 ⊂ k5_11, trump5      k4_05 ⊂ k5_11, k5_16      k4_06 ⊂ trump5, k5_16
    k4_08 ⊂ trump5             k4_11 ⊂ trump5, k5_16     k4_13 ⊂ k5_16

**These two sets coincide, with zero exceptions** (checked by D4-containment against the full
census): *a k = 4 Young class is certifiably empty **iff** it is contained in no open k = 5 class.*
By K1 the ⇐ direction is a bound no method can beat, so the guard-LP layer at k = 4 attained the
**theoretical maximum** — nothing was left on the table, and every survivor is a survivor for a
combinatorial reason inherited from k = 5, not an LP weakness.

## V5 — canary (iii): corners4 vs the A14/A16 τ = 7.000 baseline — REPRODUCED IN CONTENT, NOT IN VALUE
A14/A16: "four exact corners fixed still give τ* = 7 = budget (¼-structure)"; A16 re-measured
LP = 7.000 at that node. A55's residual-LP value descends monotonically as atoms are added:

    7.228936  (k4_13, cold start, 900 s)
  → 7.207849  (A53, 300 s)
  → 7.200000  (A55 canary, merged warm from A53, 2563 s, 24891 rows, 3010 orbits)

all ≥ budget, so **certification is refused a priori** (`certify.py` rc = 3 / "impossible
(τ ≥ budget)") — the decisive content of the baseline (corners4 is alive; the ghost survives four
corner pins) is reproduced. The exact value 7.000 was NOT attained. The residual is localized
exactly: the ghost profile of the canary node is

    interior 3.200 (3.026 tilted) + side_L 1.000 + side_B 1.000 + side_R 1.000 + side_T 1.000

— **all four side blocks are already exactly 1.000; the entire 0.200 excess is the interior
block**, which converges to 3 from above (k4_03 attains exactly 3.000). Since restricting the atom
set can only RAISE τ, every value above is an upper bound consistent with the A14/A16 limit 7.000.
Recorded as GAP-A55-3, not as a discrepancy.

## V6 — the ghost decomposition and the alive/dead classifier (measured)
`code/ghost.py`, reference k4_03 (the exact-budget k = 4 ghost). At k = 4 the optimum decomposes as

    τ  =  interior block  +  Σ over lit side zones 1.000  +  Σ over lit corner zones ≈ 1.000

with the interior block ≈ 95–100 % tilted (5–85°). Over the final table of all 14 classes the
interior mass separates the two verdicts with **no overlap**:

    SURVIVORS (6):  2.977  2.986  3.000  3.003  3.072  3.229      (corners4 canary 3.200)
    CERTIFIED (8):  1.000  2.479  2.570  2.651  2.664  2.667  2.750  2.883

min survivor 2.977 vs max killed 2.883 — a margin of 0.094 about a threshold of ≈ 2.93. The
tilted part of the interior block separates them too: survivors 2.817–3.026, killed 1.000–2.750
(margin 0.067). This is an empirical classifier, not a proof, but it is a perfect one on 14/14.

k4_07, the only node killed at round 0, is the one whose interior block **collapses to 1.000** —
the ghost is destroyed, not merely dented, which is why 12 atoms sufficed. Its pin set is the
2 × 2 corner block, the only k = 4 class that fills a whole 2 × 2 quadrant of the slot grid.
(The raw L1 ghost score against *trump5* does NOT discriminate at k = 4 — 0.57–0.85 on both sides —
because the k = 4 ghost lights one more zone than the k = 5 ghost. The interior block is the
statistic; the trump5-referenced score is reported only for continuity with A54 S1.)

## V7 — coverage-number calibration (why ν is not an arbiter)
`code/tightvar.py` on trump5, where ν* = 6 is known from V2: the grid search returns **ν = 5**
(step 0.03, 1.5°), and A54's `alive.py` on the LP rows also returns 5 (A54 recorded 4).
**ν undercounts by 1 on a provably alive node**, so ν = budget − 1 is the alive signature and
ν < budget is never evidence of death. GAP-A54-2 restated quantitatively.

## V8 — cap reconstruction, validated against A54's closing state
`code/cap.py` rebuilds the emptiness map from the PASS ledger alone (A53 `certs_wip/*.PASS`,
A54 `certs/*.PASS`, A55 `certs/*.PASS`) by D4-containment. Run before any A55 kill it returned
exactly A54's recorded state — 52 certified pin-sets (19 at k = 5, 33 at k = 6); k ≥ 6 all empty;
k = 5 open = {k5_11, trump5, k5_16} — **0 discrepancies**, which is the regression test for the
whole containment layer.

## V8b — structural audit of all 8 accepted certificates
Independent of the verifier: each `certs/k4_*.json` carries **exactly 4 degenerate cores whose
(kx, ky) equal that class's own slot set** (checked against `results/name_to_slots.json`),
**zero NO-families** (so the claim is unconditional on the pin hypothesis alone, with no auxiliary
case split), `budget = 7 = 11 − #cores`, `s = 969271/250000`, and `total < budget` in exact
rationals. 8/8 sound. Certificate totals span 6.981746–6.983004; accepted scales 1.048–1.164 —
**every one above A53's hard 1.03 cap, so under the old cap none of the eight would have
certified** (A54 S2's lever, load-bearing here).

## V9 — process discipline
≤ 3 heavy processes for the sweep (3 shards), then ≤ 3 for the escalation chains. The corners4
canary ran as a brief 4th LP-only process with 14.6 GB free and every job under 1 GB — far outside
A54 W7's OOM regime (32k rows × 6k columns with four resident certification jobs). Checkpointed
throughout (`results/<name>_<tag>.json` short-circuits a completed node; `ladder.py` rotates each
node json to `.prev<ts>` so it becomes a warm source for the next pass). A29 untouched.
