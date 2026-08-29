# A44 census re-run — the Maxwell column, re-thresholded and branch-decomposed

Computation agent, 2026-08-29. Code `code/census/`, log `logs/census.log`, machine-readable
`results/census.json` (projections) and `results/census_l1.json` (per-graph exact integers).

**What changed vs A43.** A43's N4 column applied one threshold, `m >= 3k+1`, as a single
CONDITIONAL kill. A44 theory (`notes/theory.md`) shows that threshold is unsound
unconditionally (the atlas inhabits `m = 3k` with genuine critical points) and splits the family
into an EXACT two-branch decomposition plus two labeled conditional thresholds. This re-run
measures all of them on the same sample, the same seed, the same models.

Row count convention (Fact 0): `E = Ess + Esw` edges, `F = nf + nwf` flush edges (2 rows each),
`m = E + F`, `N = 3k+1`, `chi := m - N = sig - d` (L8, proved).

| column | meaning | soundness |
|---|---|---|
| MAIN' baseline | A43 R11 = MAIN & N1 & N5 & N6 | EXACT |
| RIGID-POSSIBLE | `m >= 3k+1` (chi >= 0) | EXACT split (L9 contraposition) |
| FLEX-ONLY | `m < 3k+1` (chi <= -1) | EXACT split — **carried, not killed** |
| C-rep column | kill `m < 3k+1` | CONDITIONAL on C-rep (unproved, A44-G1) |
| C* column | kill `m < 3k` | CONDITIONAL on C* (unproved, atlas-consistent) |
| chi = -1 slice | `m = 3k` exactly | EXACT slice of FLEX-ONLY (where the atlas valleys live) |

---

## 1. Regression against A43 — PASS, exactly

Run under A43's own protocol: A43 `results/h1/level0_k*.json` MAIN samples, `default_rng(7)`,
cap 160 (k<=6) / 40 (k=7), budget 22, weight `main/nsample`. No file under
`A43-spine-census`, `A31-structure-count` or `A29-finish-384` was written. Total wall time
about 2 s for k = 3..7; the budget/cap mechanism was never hit (0 graphs skipped).

- **510 / 510 sampled (graph, wall-mask) rows reproduce A43's `level1.json` integers exactly**
  on all four recorded columns: `we_surv` (= our `tot`), `we_surv_N4` (= our `m_ge_3k1`),
  `we_surv_nozero`, `we_surv_nozero_N4`. Zero mismatches.
- Weighted `frac_m_ge_3k1` equals A43's `N4_frac_weighted` at every k (max abs diff 6.9e-18,
  float summation order only); `frac_nozero` equals A43's `N3_frac_nozero_weighted` likewise.
- Re-fitted fan-out multiplier reproduces A43's `level2.json` `projection.fanout` to 1e-12 at
  every k = 3..11.
- Composed baseline k = 11 reproduces A43's `MAINprime_exact` **to the last bit**:
  2.3036e29 / 1.5066e30 / 1.0869e30.
- C-rep column built A43's way (its L0 `mainprime_N4` graph series x the L1 fraction)
  reproduces A43's `MAINprime_N4_conditional` k = 11 to 2e-16: **1.634e26 / 8.933e26 /
  6.909e26** — inside the reported 1.6e26–8.9e26 band, as required.
- Non-thin conditional reproduces A43's `MAINprime_N4_nonthin_conditional` exactly:
  1.7162e25 / 2.1813e25 / 2.0897e25.

`results/census.json -> regression.PASS = true`.

## 2. Per-k exact fractions (weighted over the A43 sample, k = 3..7 EXACT)

Shares of all tilt-feasible decorations, orbit-weighted:

| k | RIGID-POSSIBLE `m>=3k+1` | C* `m>=3k` | chi = -1 (`m=3k`) | FLEX-ONLY `m<3k+1` | chi=-1 share of FLEX |
|---|---|---|---|---|---|
| 3 | 0.135421 | 0.223340 | 0.087918 | 0.864579 | 0.1062 |
| 4 | 0.053280 | 0.134800 | 0.081520 | 0.946720 | 0.0920 |
| 5 | 0.031449 | 0.078133 | 0.046685 | 0.968551 | 0.0509 |
| 6 | 0.025039 | 0.059854 | 0.034815 | 0.974961 | 0.0378 |
| 7 | 0.007219 | 0.021026 | 0.013807 | 0.992781 | 0.0141 |
| **11 (proj.)** | **6.281e-4** | **2.827e-3** | **2.199e-3** | **0.99937** | **2.20e-3** |

Fits (A43's own rule, log-linear in k): `log frac(m>=3k+1) = -0.0927 - 0.6618 k` (this is A43's
N4 fit verbatim); `log frac(m>=3k) = 0.2228 - 0.5538 k`. FLEX-ONLY and the chi = -1 slice are
DERIVED from those two so the projected shares stay coherent (an independent log-fit of the
FLEX share runs through 1.0 before k = 11 — it is a saturating share, not an exponential).

**Full chi profile** (orbit-weighted share of decorations, k = 7): chi = -8:0.002, -7:0.005,
-6:0.017, -5:0.148, **-4:0.308**, -3:0.270, -2:0.145, -1:0.066, 0:0.026, +1:0.009, +2:0.003.
The mode is at chi = -4, i.e. the typical enumerated structure is four rows short of Maxwell,
not one. Lowering the threshold from 3k+1 to 3k moves it into the tail's second bin only.

## 3. k = 11 projected columns and kill factors

Composed as A43 does: `graphs(k) x fanout(k) x frac(k)`, three models
(M1 exp / M2 log-quadratic / M3 linear-ratio). Kill factor = baseline / column.

| column | k=11 (M1 / M2 / M3) | kill factor |
|---|---|---|
| MAIN' baseline (EXACT) | 2.30e29 / 1.51e30 / 1.09e30 | 1 |
| MAIN' non-thin (EXACT) | 2.73e28 / 3.47e28 / 3.33e28 | 8.4 / 43 / 33 |
| **C-rep `m>=3k+1`** (CONDITIONAL) | **1.45e26 / 9.46e26 / 6.83e26** | **1592** (all models) |
| C-rep, A43 replication (L0 N4 series) | 1.63e26 / 8.93e26 / 6.91e26 | 1410 / 1687 / 1573 |
| **C* `m>=3k`** (CONDITIONAL) | **6.51e26 / 4.26e27 / 3.07e27** | **354** (all models) |
| chi = -1 slice (`m=3k`) | 5.07e26 / 3.31e27 / 2.39e27 | 455 |
| **FLEX-ONLY `m<3k+1`** (EXACT) | **2.30e29 / 1.51e30 / 1.09e30** | **1.0006** |
| C-rep & non-thin | 1.72e25 / 2.18e25 / 2.09e25 | 1.34e4 / 6.91e4 / 5.20e4 |
| C* & non-thin | 7.72e25 / 9.82e25 / 9.41e25 | 2.98e3 / 1.53e4 / 1.16e4 |
| FLEX-ONLY & non-thin | 2.73e28 / 3.47e28 / 3.33e28 | 8.4 / 43 / 33 |

The C-rep and C* kill factors are model-independent because they are pure multiplicative
Level-1 fractions on a common graph series; only the non-thin and A43-replication rows carry
model spread (they change the Level-0 graph series too).

## 4. Headline

**(a) About 4.5x of the old conditional kill is lost by dropping to C*, and the rest survives.**
The C-rep threshold `m >= 3k+1` buys x1592 at k = 11; the C* threshold `m >= 3k` buys x354.
Ratio exactly 4.50 = frac(m>=3k)/frac(m>=3k+1) at k = 11. On the ledger's own "x1e4" figure —
which is the N4-plus-non-thinness number, 1.3e4–6.9e4 — the C* analogue is 3.0e3–1.5e4. In log
terms C* retains 80% of the C-rep kill (ln 354 / ln 1592 = 0.796). So the weaker, atlas-
consistent conjecture is still a three-orders-of-magnitude instrument: the composed conditional
count moves from 1.6e26–8.9e26 up to only 6.5e26–4.3e27. **Neither threshold is anywhere near
enough to make enumerate-then-solve viable at k = 11** — A31/A43's NO-GO stands under both.

**(b) The branch the old filter silently killed is essentially the entire census.**
FLEX-ONLY (`m < 3k+1`) is **99.94% of the projected k = 11 count, 2.30e29–1.51e30 structures**,
and 99.28% already at k = 7 (exact, measured). A43's N4 column was not trimming a tail — it was
discarding the census and keeping a 0.06% residue. Since the atlas certifies critical points at
chi = -1, that discard is unsound as stated, and the sound object is the decomposition:
RIGID-POSSIBLE 6.3e-4 of the count, FLEX-ONLY the remainder, both carried.

**(c) The chi = -1 slice — the only inhabited flex layer known — is thin inside FLEX-ONLY.**
`m = 3k` is 2.2e-3 of the flex branch at k = 11 (1.4% at k = 7, exact). Everything C* would kill
lies at chi <= -2, which is 99.8% of the flex branch, i.e. 99.7% of the whole census. C*'s bite
is almost entirely against structures with two or more excess flexes over stresses — the region
the atlas has never populated but the FJ+counting route provably cannot exclude
(`theory.md`, "no unconditional bound below 3k+1").

**(d) New cross-column fact: the RIGID-POSSIBLE branch is almost entirely zero-pinned.**
Only 1.2% of the `m >= 3k+1` mass at k = 7 has no zero-pinned tilt class (2.1% for `m >= 3k`),
against a 33.6% no-zero share overall. High row counts are bought with wall-flush edges, and
wall-flush forces phi = 0, which satisfies A21 THM3 for free. So the Maxwell-conditional
columns and the N3/THM3 column are near-disjoint in bite: they cannot be composed for a product
of gains. (Diagnostic only — never composed.)

## 5. Honest notes

1. **Sampling protocol inherited from A43**, not re-derived: 160 (k<=6) / 40 (k=7) sampled
   (graph, wall-mask) pairs per k from A43's exhaustive Level-0 MAIN orbit list, seed 7. The
   k = 3..7 fractions are exact weighted means over that sample, not over the full population.
   Any sampling bias in A43's Level-1 numbers is inherited verbatim here — that is deliberate,
   it is what makes the regression meaningful.
2. **The k = 8..11 numbers are extrapolations, not bounds** (A43 G-A43-7 / G2). Three fitted
   models on five points with no holdout beyond A43's own. The fraction columns add a second
   fitted extrapolation (log-linear share) on top of the graph-count fit and the fan-out fit —
   three stacked fits. Treat the model spread as a lower bound on the true uncertainty.
3. **The C-rep and C* columns are CONDITIONAL on unproved conjectures** and are labeled as such
   everywhere in `census.json`. C-rep additionally requires the max-contact-representative
   census reduction (A44-G1). Neither may enter a certified count.
4. **The FLEX-ONLY / RIGID-POSSIBLE split itself is EXACT** — it is L9 by contraposition at the
   graph level (a structure with `m < 3k+1` has rank <= m < N at every realization and so can
   never be first-order rigid). It kills nothing; it labels.
5. The C-rep row is reported twice: once in A43's exact composition (its Level-0 `mainprime_N4`
   graph series, for the regression) and once on the common `mainprime` series (for a
   like-for-like kill factor against C*). The two differ by 0.997 at the graph level — a
   negligible, purely bookkeeping, difference.
6. Compute: one process, ~2 s total for k = 3..7. The budget (22) and cap mechanisms were
   available but never triggered a skip; every sampled graph was enumerated in full.
