# A87 follow-up — FJ-polished k0 critical-point search

Closes the `[C]` item at the end of `docs/proofs/drain_flow_k0.md` §5.4
("re-run A85's CP search with an FJ-polish … ~1 desktop-hour").
Driver `code/fjpolish87.py`; log `logs/fjpolish.log`; results
`results/cp87_fj_polished.json` (summary), `results/cp87_fj_polished.jsonl`
(per-seed), `results/cp87_below_shat_verify.json` (exact re-verification).
One process, BLAS pinned to 1 thread, **1928 s** (32 min) for 269 seeds
(7.2 s/seed mean). No LP solver anywhere. A57/A60/A61/A85 untouched;
no certificate emitted.

## 0. Headline

**NO.** No genuine k0 Fritz-John point at or below ŝ = 3.877083590022814 —
**zero** of the 179 survivors, and zero of the 167 that survive at the tight
end of the tolerance ladder. A04's 702-optimum search is not contradicted.

* Lowest **certified-FJ (tol 1e-6) k0 point**: σ = **3.897230787** (`o012`),
  Δ = +2.015·10⁻² above ŝ. This is the *same single point* A87/J3 already
  found FJ-feasible among the 14 lowest landings — the polish adds nothing
  below it.
* Lowest **feasible k0 packing the drains ever reach** (independent of FJ
  status, since σ decreases monotonically along the flow): σ ≤
  **3.877140815**, i.e. **ŝ + 5.72·10⁻⁵**, from Trump rotated by φ = 10⁻⁴.
  Re-verified in exact rationals at 80 dps: all 55 pairwise SAT gaps ≥
  9.86·10⁻¹¹ > 0 (worst pair 0–3), side ≤ 3.877140815 — a valid packing,
  strictly **above** ŝ. `results/cp87_below_shat_verify.json`.
* Sanity check the run passes: the rotational ghosts φ ≤ 10⁻⁵ all drain back
  to σ = **3.877083590** = ŝ exactly (to 2.9·10⁻¹¹) and are then correctly
  rejected as **not k0** (k_flush_corner = 3). The machinery finds ŝ when ŝ is
  reachable, and refuses to count it.

## 1. Method

Per seed: canonicalise (bbox at PAD = 10⁻⁹, s = enclosing side), then

1. **Classify** the active set with t3lib rows at tolerance `tol` —
   containment rows plus, for each pair whose SAT gap ≤ tol, the straddling
   rows of the first consistent selection (`jobs87.active_rows_at_point`).
2. **FJ test = NNLS**, not an LP: `min_{λ≥0} ‖Aₙᵀλ − e_s‖` on the
   unit-row-normalised gradient matrix. Residual ≤ 10⁻⁷ ⟺ e_s ∈ cone{∇g_k}
   ⟺ FJ multipliers exist with λ₀ = 1 (λ ≠ 0 is automatic since e_s ≠ 0).
   The λ₀ = 0 branch is a second NNLS on `[Aₙᵀ; 1ᵀ]λ = [0; 1]`.
3. **Descent.** NNLS's own KKT conditions make the residual vector
   r = Aₙᵀλ\* − e_s a certified Gordan direction: `Aₙ r ≥ 0` (every active
   constraint non-decreasing) and `e_s·r = −‖r‖² < 0` (the side strictly
   decreases). So the FJ test *hands back* the descent direction for free
   whenever it fails. Backtracking line search on the true (non-penalised)
   constraints; a step may lose O(t²) of gap to curvature, so it is accepted
   with a violation ≤ 5 % of the side it gained and repaired by a centre
   inflation about the bbox centre (cost ≈ 4× the violation).
   The working tolerance is **ε-active**, `wtol = clamp(20·step, 1e-6, 1e-3)`,
   ratcheting downward only — a constraint nearer than the step travels can
   block, so it must be in the descent set.
4. **Newton polish** of the active-set FJ system (`t3lib.fj_eval` mode
   `active`, unknowns z(34), λ₀, λ(m); damped, `lstsq` for the rank-deficient
   degenerate sets), accepted only if the packing stays feasible and the side
   does not rise.
5. **Verdict** at the polished point over the whole ladder 1e-6 … 1e-3:
   FJ feasibility, λ₀ = 0 branch, rank / flat dimension / rattlers, plus the
   k0 rule (no square both axis-aligned within 1e-6 and within 1e-6 L∞ of a
   corner slot) and a packing-feasibility check.

Budget: 14 s of flow per seed, ≤ 800 iterations.

**Survivor = polished point that is a feasible packing, is k0, and has feasible
FJ multipliers.** "Tight" = the cone test passes at tol = **10⁻⁶** (exact
contacts). The loose count also admits passes at 10⁻⁴/10⁻³, which is *not* a
first-order certificate — see §4.

## 2. Seed-level census (the A87 §5.4 finding, extended to all 262)

A87/J3 tested 15 points and found 14 without FJ multipliers. Across the whole
A85 census:

| at the A85 landing itself | count of 262 |
|---|---|
| FJ-feasible at tol 10⁻⁶ (exact contacts) | 139 |
| FJ-feasible at some ladder tol | 147 |
| **FJ-INFEASIBLE at every ladder tol** | **115 (44 %)** |

So 44 % of A85's "k0 optima" are first-order artefacts of the penalty/SLSQP
stopping rule, not critical points — J3's result on the 14 lowest was not a
low-σ peculiarity.

## 3. Survivors and side distribution

269 seeds = 262 A85 optima + 7 rotated-Trump (φ ∈ {5·10⁻⁸, 10⁻⁷, 10⁻⁶, 10⁻⁵,
10⁻⁴, 10⁻³, 10⁻²}).

| | survivors | of 262 |
|---|---|---|
| tight (FJ at 10⁻⁶) | **167** | 167 |
| any ladder tol | 179 | 178 |

Non-survivors: 73 "no FJ multipliers at any tol" (flow still descending at the
budget) + 17 "drain left the k0 stratum" (a square settles onto a corner slot).
Flow status: `fj` 171, `time_cap` 75, `stuck` 23. 149 seeds did not move at all
(already FJ); median drop 0, max drop 5.92·10⁻².

**Side distribution of the 167 tight survivors** (and, for reference, how many
seeds started in each band):

| σ band | tight survivors | seeds in band |
|---|---|---|
| [3.87, 3.88) | **0** | 5 |
| [3.88, 3.90) | **1** (o012, σ = 3.897230787) | 15 |
| [3.90, 3.95) | 0 | 4 |
| [3.95, 4.00) | 3 | 16 |
| [4.00, 4.10) | 139 | 204 |
| [4.10, 4.30) | 16 | 16 |
| [4.30, ∞) | 8 | 9 |

The five lowest tight-survivor sides: 3.897230787, 3.982843051, 3.982843051,
3.996920774, 4.000000000. **Nothing below 3.897.** The survivor rate is
strongly σ-dependent: 1/5 in [3.87, 3.88), 7/15 in [3.88, 3.90), but 16/16 in
[4.10, 4.30) — the low-σ landings are exactly the ones that are not critical
points, which is the A87 §5.4 claim made quantitative.

Tight survivors: m_active median 23 (range 11–48), rattlers median 3, flat
dimension on the 33 configuration coordinates median 16; 6 of them also admit
the λ₀ = 0 branch.

## 4. The 14 low landings of A87/J3, re-run

| id | σ seed | σ polished | drop | tight FJ | k0 kept | flow |
|---|---|---|---|---|---|---|
| o000 | 3.8872133 | 3.8867695 | 4.4e-04 | no | yes | time_cap |
| o001 | 3.8872587 | 3.8871654 | 9.3e-05 | no | yes | time_cap |
| o002 | 3.8872878 | 3.8867723 | 5.2e-04 | no | yes | time_cap |
| o003 | 3.8874037 | 3.8868091 | 6.0e-04 | no | yes | time_cap |
| o004 | 3.8874647 | 3.8867771 | 6.9e-04 | no | yes | time_cap |
| o005 | 3.8875528 | 3.8869196 | 6.3e-04 | no | yes | time_cap |
| o006 | 3.8878121 | 3.8867638 | 1.0e-03 | no | yes | time_cap |
| o007 | 3.8878253 | 3.8868561 | 9.7e-04 | no | **no** | time_cap |
| o008 | 3.8878912 | 3.8867460 | 1.0e-03 | no | **no** | time_cap |
| o009 | 3.8880201 | 3.8868691 | 1.2e-03 | no | yes | time_cap |
| o010 | 3.8882801 | 3.8869487 | 1.3e-03 | no | yes | time_cap |
| o011 | 3.8886982 | 3.8869738 | 1.7e-03 | no | yes | time_cap |
| **o012** | 3.8972308 | **3.8972308** | 0 | **YES** | yes | `fj` |
| o013 | 3.8988968 | 3.8986318 | 2.7e-04 | no | yes | time_cap |

o012 is confirmed as the sole genuine FJ point in this set, unmoved by the
polish — J3 reproduced exactly. The other 13 all drain (10⁻⁴–10⁻³ in σ) and
**none** of them converges inside the 14 s budget; two leave the k0 stratum on
the way. So the drains of the low landings do exist and are long, but every
one of them is still ≥ 3.8867 when the budget runs out — 9.7·10⁻³ above ŝ.

## 5. Rotated-Trump controls

| φ | σ seed | σ polished | k_flush | k0 | verdict |
|---|---|---|---|---|---|
| 5·10⁻⁸ | 3.877083784 | **3.877083590** | 3 | no | drains to ŝ, not k0 |
| 10⁻⁷ | 3.877083978 | **3.877083590** | 3 | no | drains to ŝ, not k0 |
| 10⁻⁶ | 3.877087467 | **3.877083590** | 3 | no | drains to ŝ, not k0 |
| 10⁻⁵ | 3.877122361 | **3.877083590** | 3 | no | drains to ŝ, not k0 |
| 10⁻⁴ | 3.877471279 | 3.877140815 | 0 | yes | still descending at cap |
| 10⁻³ | 3.880958734 | 3.880108391 | 0 | yes | still descending at cap |
| 10⁻² | 3.915659927 | 3.893984443 | 0 | yes | still descending at cap |

The φ ≤ 10⁻⁵ ghosts un-rotate back onto Trump to 2.9·10⁻¹¹ — the strongest
correctness check available, and it also shows the flow is not what is
limiting §5.2's "r7 stays alive at h = 10⁻⁸": the geometry really is Trump.
The φ ≥ 10⁻⁴ ghosts are k0 by the 10⁻⁶ axis-alignment rule and drain toward,
but never below, ŝ + 5.7·10⁻⁵.

## 6. Caveats — what this does and does not establish

1. **The 12 "loose" survivors are not certificates.** They pass the cone test
   only at tol 10⁻⁴/10⁻³, where 34–42 rows are called active and the rank on
   the configuration coordinates reaches 31–34 (flat dimension 0–3) — a point
   mid-drain looks jammed if everything within 10⁻⁴ is called a contact. All
   12 have flow status `time_cap`/`stuck` with tight residuals 10⁻¹–10⁻³.
   Read them as "drain not finished", not "FJ point". Every one of them is
   nonetheless ≥ 3.8771, so they do not affect the headline.
2. **The drains are not run to convergence.** 98 of 269 flows were still
   descending when the 14 s budget expired. The headline is therefore of the
   form *no drain reached ŝ*, not *no k0 FJ point below ŝ exists*. What is
   certified is that σ falls monotonically along each flow and every visited
   configuration is a feasible packing, so a k0 FJ point below ŝ at the end of
   any of these drains would have required the flow to pass through σ ≤ ŝ —
   and none did, the closest approach being ŝ + 5.7·10⁻⁵.
3. **Selection ambiguity survives.** Classification still takes the *first*
   consistent selection per contact pair (J3's caveat); a corner–corner tie
   admits several, and FJ feasibility for a different tie is not excluded.
4. The k0 test is A85/cp85's operational one (1e-6 in both angle and centre),
   so a square that drifts 2·10⁻⁶ off a corner slot counts as k0. Two drains
   (o007, o008) cross the other way and are dropped.

## 7. Bearing on DF-K0 / H1

Unchanged: DF-K0 quantifies over the true minimiser and is untouched. What
this run does is replace A87 §5.4's "[F] the under-contacted k0 optima are not
FJ points" with a positive statement about where their drains go: the genuine
k0 FJ points recovered from A85's census sit at σ ≥ 3.8972, and no drain from
any of the 262 landings or the 7 rotational ghosts descends below ŝ. The
empirical comfort behind H1 is restored in a weaker but honest form —
**the k0 critical set that A85's search can see starts 2.0·10⁻² above ŝ**,
with the caveat that 98 drains were truncated.
