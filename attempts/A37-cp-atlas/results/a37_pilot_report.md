# A37 pilot report — per-CP audit + value certificates (pilot agent, 2026-08-27)

Spec: `attempts/A37-cp-atlas/notes/cookbook.md`.  Scope: pilot families 1, 6, 4 of the
`s_min < 3.95` sorted order, **plus family 0 (Trump) run through the same generic pipeline
as a self-test against A22/A36**.

Deliverables
- `attempts/A37-cp-atlas/code/a37_pipeline.py`   (family-generic producer)
- `attempts/A37-cp-atlas/code/a37_check.py`      (standalone re-checker, cookbook step 4)
- `attempts/A37-cp-atlas/results/atlas.json`     (4 entries: 0, 1, 4, 6)
- `attempts/A37-cp-atlas/results/certs/fam{00_3R,01_3S,04_3S,06_3S}.json`
- logs: `results/pipeline_log.txt`, `results/check_log.txt`, `results/gate_*.txt`

Verification status: **258 checks, ALL PASS**; **5/5 corruption gates fail as required**
(`omega-sign`, `h-big`, `drop-aux`, `drop-branch`, `value-inflate`).

---------------------------------------------------------------------------------------------
## 1. Headline table

| fam | s_min | class | mode | rank | contacts (pair/wall-rows/aux → rows) | variants | h certified | V at h | secs |
|----|----|----|----|----|----|----|----|----|----|
| 0 (Trump) | 3.877083590026693 | **RIGID** | 3R | 34/34 [RFP] | 14 / 20 / 2 → 64 (38 [V]-safe) | 1 (none needed) | 3079/819200 = 3.759e-3 | **σ ≥ 3.877083590022813997** (v_lo−1e-40) | 8.7 |
| 1 (5×45° diamond) | 3.885618083168503 | **VALLEY** | 3S | 30/34 | 13 / 18 / 3 → 55 (35) | 8 | 1838233/163840000 = 1.1220e-2 | σ ≥ 3.884568208423 | 10.8 |
| 4 (10 contacts) | 3.885982567615728 | **NOT-CP** | 3S (trivial) | 15/34, 5 rattlers | 5 / 10 / 0 → 21 (17) | 1 | 182187/20480000 = 8.8958e-3 | σ ≥ 3.877086713678 | 3.7 |
| 6 (24 contacts) | 3.886746028609552 | **VALLEY** | 3S | 32/34 | 13 / 21 / 3 → 65 (37) | 32 | 635909/32768000 = 1.9406e-2 | σ ≥ 3.883595849210 | 28.0 |

`h certified` is the **largest radius at which the certified value still beats the incumbent
3.877084** (cookbook amendment, §4.2).  The cookbook's fixed table {5e-4, 1e-3, 2e-3} is also
recorded in every entry.

**None of the three pilot families is rigid.**  Step 3R was therefore exercised only on
family 0, where it reproduces A22/A36 from scratch (§3).

---------------------------------------------------------------------------------------------
## 2. Per-family findings

### Family 0 — Trump (self-test, not in the pilot brief)
- RIGID, rank 34, [RFP] bound 2.60e-13 on the QR-selected minor.
- Newton residual 2.3e-71; **Krawczyk contracts at r_N = 1/2000, ratio 0.0566** — identical to
  A22 phase 3.  Value enclosure `[3.877083590022813553, 3.877083590022814441]`, width 8.9e-16,
  containing A22's `z0[33] = 3.87708359002281417730…`.
- Max-form barrier: β = 0.42596, κ = 19.76, κ_eff = 19.316 (A36: 19.3157), H̄ = 7.903
  (A36: 7.575), ψ/h = 0.9995, x\* = 8.38e-44, **h = 3.759e-3 vs A36's per-variant 3.779e-3 and
  branch-free universal 3.689e-3.**
- **The A37 run needs NO branch variants at all**: the [V] test (§4.1) discharges every
  ω-loaded row unconditionally, and the LP is feasible on [V]-safe rows alone.  A36's 16-variant
  L1 machinery is not needed for the *value* layer at this radius.
- Audit surprises: three CORNER-CORNER pairs (1,3), (1,8), (3,8) — A35/M4 found only (1,3);
  (1,8) and (3,8) are corner-corner in my labelling too and were also absent from A22's 38 rows.
  All three get ω = 0 and cost nothing.

### Family 1 — the 5×45° diamond
- **VALLEY, rank 30/34** (σ_min kept 1.17e-1, σ_max dropped 3.4e-16 — clean 4-dim mechanism).
- Tolerance ladder: 1e-7 and 1e-6 give an **inconsistent and KKT-infeasible** contact set
  (ls_res 5.0e-10 / 7.3e-10, LP infeasible); 1e-5 is KKT-feasible (ls_res 3.8e-15).  Chosen
  tol_c = **1e-5**.  **The A04 point for this family is only ~1e-6 converged** — two wall
  clearances sit at 1.07e-6 and 1.16e-6 and one pair gap at 2.85e-7; excluding them puts e_s
  outside the row space.
- Refinement displacement **3.15e-3** (large: closing those near-contacts moves the point), and
  the contact set is still inconsistent at **1.41e-19** — one dependent row (the corner-corner
  pair) cannot be closed simultaneously with the other 30.  z_center is therefore not exactly
  feasible; this is harmless for the certificate (the Taylor bound uses W0 = Σ|ω||g|) but must
  be reported.  |ẑ − z0|∞ = 3.15e-3 < h = 1.12e-2, so the box still contains the A04 point.
- 3 corner-corner pairs after refinement — (0,3), (0,6), (5,9) — → 8 variants, min kill margin
  0.783.  `LP on [V]-safe rows: False` — **the branch disjunction is load-bearing here**.
- V_soft: 3.885616043719 @ h=5e-4, 3.885609916888 @ 1e-3, 3.885585350077 @ 2e-3;
  h_max = 1.1220e-2 with V = 3.884568.  Binding constraint at large h is the **[V] tangential
  margin** (wt = 0.0463 at 5e-4, decaying ≈ 4.4·h), not H̄.
- Catalogue count mismatch: catalogue says 8 wall contacts, the audit finds 18 wall *rows*
  (a square flush to a wall contributes 2 corner rows; at tol 1e-5 also 3 aux dist rows).

### Family 4 — the 10-contact family (expected VALLEY)
- **NOT-CP, not merely a valley.**  Rank 15/34 with **5 rattler squares (1, 4, 6, 7, 10)**.
- `e_s` is not even in the *row space* of the active gradients: least-squares residual
  **1.21e-2**.  Dropping the 11 θ-equations makes it feasible at **1.39e-15**.  Diagnosis: the
  A04 point is a local minimum **only at fixed angles** — s strictly decreases under rotation.
  Consistent with A04's fsbh angle lattice (tilt pattern [40,40,45,45,45]).  This holds at
  every tolerance in the ladder (1e-7 … 1e-4, ls_res 1.21e-2 … 1.05e-2), so it is not a
  tolerance artefact.
- Refinement is perfectly consistent (GN residual 5.4e-71), so the contact structure itself is
  exact; it simply is not a critical point of σ.
- Only the **trivial coordinate bound** σ(z) ≥ s(ẑ) − h is available (ω = 0 in the single
  variant).  h_max = 8.8958e-3, V = 3.877086713678.  Reported as such; the far field must
  handle this family by other means (or the lead should re-optimise it with free angles, which
  would land it on a genuinely lower s and probably in a different family).

### Family 6 — the 24-contact family (expected "biggest-count rigid")
- **VALLEY, rank 32/34.**  Very clean: σ_min kept 1.634e-1, σ_max dropped 1.90e-16, GN residual
  6.8e-71, next-nearest wall clearance 0.244 and next-nearest pair gap 0.104.  There is no
  tolerance ambiguity whatsoever, and the 2-dimensional mechanism is real.
- **5 corner-corner pairs**: (3,9), (5,7), (5,8) with 2 tied axes each and (7,8) with **4 tied
  axes** → 32 variants, min kill margin 0.782.  All 32 variants have a feasible multiplier LP;
  max ‖ω‖₁ = 4.558, max r_res = 5.8e-12, max W0 = 8.7e-46.
- `LP on [V]-safe rows: False` — again the branch disjunction is load-bearing.
- V_soft: 3.886744019640 @ 5e-4, 3.886737984069 @ 1e-3, 3.886713781042 @ 2e-3;
  **h_max = 1.9406e-2, V = 3.883595849210** — the best discharge in the pilot, 2× the trivial
  radius (9.66e-3).
- Wall time 28.0 s, dominated by the 32 variants (≈0.7 s each).

---------------------------------------------------------------------------------------------
## 3. What the pilot validated

- The whole pipeline is family-generic: the only A22/A35/A36-specific thing that survives is the
  *row language*, transcribed.  `t3lib` is generic and was used as the semantic reference.
- Step 3R works end to end and reproduces A22 (Krawczyk r_N, value enclosure) and A36 (κ_eff,
  ψ/h, h to within 0.5 %) from scratch, on a family the pipeline had never seen a certificate for.
- Step 3S works on valleys, on NOT-CP families, and with branch variants.
- The standalone checker rebuilds rows, safety flags, branch sets and variant products from the
  contact table alone, and rejects all five corruptions.

---------------------------------------------------------------------------------------------
## 4. Cookbook amendments the lead should make before the production run

### 4.1 The [V] test replaces most of the branch machinery — and is the real row-validity rule
The cookbook says flush rows "may be taken per A36 (any corner row of a separating axis)".  That
is only sound *given a branch*.  The generic, branch-free sufficient condition actually used
here is: a sep row `g = n_e(θ_o)·(q_k(p) − c_o) − 1/2` is valid on box(ẑ,h) as soon as, over the
whole box, `sup|t| < 1/2` **and** `inf d > −1/2` (t, d = the corner's coordinates in the owner's
edge frame).  Proof: a corner of p with both frame coordinates strictly inside would lie in the
open square o.  Uses only pairwise interior-disjointness.  This is the a36_check `[V]` test
promoted from a *check* to the *definition* of a safe row, and it is what makes family 0 need
zero variants.

### 4.2 Three concrete corrections to the recipe

1. **`V_soft`'s gradient term.**  The cookbook writes `r_res·sqrt(34)·h`.  Since `‖d‖∞ ≤ h` and
   `|∇Φ·d| ≤ ‖∇Φ‖₁‖d‖∞`, the correct (and 5.8× tighter) term is **`r_res·h`**.  Implemented.
2. **`V = floor((v_lo − 1e-40)·1e30)/1e30` is a float64 bug.**  `v_lo·1e30` has ~1e14 absolute
   float error, so the "rounded-down" V came out *above* v_lo.  The checker caught it.  Use
   exact rationals: `V = Fraction(v_lo) − Fraction(1, 10**40)`.
3. **The h ladder {5e-4, 1e-3, 2e-3} is vacuous.**  Since s is a *coordinate*, every box of
   radius h trivially satisfies σ(z) ≥ s(ẑ) − h.  For s(ẑ) ≈ 3.886 that already beats the
   incumbent 3.877084 out to h ≈ 9e-3, i.e. past the whole cookbook table with ω = 0.  The
   barrier only earns its keep at larger h.  **Replace the fixed table by: bisect h to maximise
   it subject to `V_soft(h) ≥ 3.877084`** (still recording the fixed table).  Under that
   criterion the barrier buys 1.31× (fam 1) and 2.01× (fam 6) over the trivial radius.

### 4.3 Things the cookbook did not anticipate at all

1. **The A04 points are not uniformly converged; a single `tol_c = 1e-7` is wrong.**
   Families 0 and 6 are converged to 1e-12 and 1e-7 cuts perfectly; family 1 needs 1e-5 (its
   contacts sit at 1.07e-6, 1.16e-6, 2.85e-7) and is KKT-*infeasible* at 1e-7 and 1e-6.
   Implemented: a **tolerance ladder** {1e-7, 1e-6, 1e-5, 1e-4}, scored by (a) Gauss-Newton
   consistency and (b) KKT-LP feasibility, smallest passing tol wins, the whole ladder recorded
   in the atlas entry (`tol_ladder`).  Being generous is *sound* — extra valid rows only cost
   value through `W0 = Σ|ω||g|` — so err loose, not tight.

2. **Classify AFTER a Gauss-Newton refinement, never at the raw A04 point (new Step 1.5).**
   At the raw point family 6 shows σ_max_dropped = 1.06e-10, indistinguishable from noise; after
   refinement (GN residual 6.8e-71) it is 1.9e-16 against σ_min_kept 0.163 and the rank-32
   verdict is unambiguous.  Family 4's smallest singular value likewise moves 2.2e-16.  **Every
   rank/spectral-gap claim at an unrefined A04 point is worthless.**  Implementation note: the
   active row set is massively redundant (rank 15…34 out of 21…65 rows), so regularised normal
   equations are numerically singular — Newton on a **QR-pivoted maximal independent subset with
   minimum-norm steps** is what works (residual on the dependent rows is then the honest
   consistency test).

3. **Corner-corner contacts are the norm, not an exception, and they are load-bearing.**
   Every family in the pilot has 2–5 of them (fam 6 has five, one with **4 tied separating
   axes**), and in families 1, 4 and 6 the multiplier LP is **infeasible on [V]-safe rows alone**.
   "Drop the row" is therefore *not* generally an option, and the cookbook needs the generic
   branch disjunction as a first-class step, not a fallback.  Implemented generically:
   for each pair with **no** [V]-safe row, the live axes are those the interval kill test
   (∃ corner k with sup_box g < 0) cannot eliminate on box(ẑ, h_probe = 0.05); SAT completeness
   then makes the union of the live axes exhaustive, and L1.1 makes every corner row of the live
   axis valid inside its branch.  Variants = product of live sets (fam 1: 8, fam 6: 32).
   **Branch only pairs with no [V]-safe row** — branching every pair that merely *contains* an
   unsafe row blew fam 1 up from 4 to 256 variants and the wall time from 3 s to 138 s.

4. **A NOT-CP outcome is real and needs a defined product.** Family 4 is not a critical point of
   σ at all (fixed-angle optimum only).  The cookbook says "flag and skip"; better is to still
   emit the trivial-bound soft certificate (ω = 0 per variant), which costs nothing and still
   discharges a box of radius ~9e-3.  Implemented: infeasible-LP variants fall back to ω = 0
   automatically, so 3S never fails.  **Expect more NOT-CP families in production** — the A04
   tilt patterns are lattice values (5°, 10°, …, 45°), so any family whose true optimum has an
   irrational tilt will look like this.  Recommend the lead decide whether to re-optimise those
   with free angles before atlasing them.

5. **`h_max` is [V]-tangential-margin-limited, not curvature-limited.**  For fam 1 the barrier
   dies when `wt = 1/2 − sup|t|` hits 0 (≈ h 1.1e-2), long before `H̄h²` matters.  A per-pair
   *branch upgrade* of the margin-critical rows (branch validity needs no tangential margin at
   all) would push h further at the cost of more variants — worth doing for the families where
   the atlas wants a big box.

6. **Variable layout.** `best_x` is centres-interleaved `x[2i], x[2i+1]`, thetas blocked
   `x[22+i]`, `s = x[33]` — **not** the A22 order.  (Confirmed by the lead mid-run; the brief's
   `[cx0,cy0,th0,…]` guess is wrong and would silently produce nonsense.)  Put the converter in
   the cookbook.

7. **Catalogue contact counts are contacts, the audit counts rows.**  `n_wall_contacts` = 8 for
   fam 1 vs 18 wall rows found; a square flush against a wall contributes 2 corner rows.  Do not
   treat a mismatch as an audit failure; the pair counts do match exactly in all four families.

### 4.4 Cost model for the production run
0.6–1.0 s per tolerance-ladder rung (4 rungs), ~0.2 s per audit, ~0.7 s per variant.  Wall times
here were 3.7–28.0 s per family.  The variant count is the only thing that can explode: budget
`2^(#corner-corner pairs)` and cap it (e.g. refuse > 256 and report).  28 families at this cost
is well under an hour on one process.

---------------------------------------------------------------------------------------------
## 5. Open issues for the lead

- **Fam 1's 1.41e-19 inconsistency.** One dependent row (a corner-corner pair) cannot be closed
  with the other 30.  Either the true optimum of this family has that contact only in the limit,
  or the A04 point sits on a slightly different stratum.  Harmless for soundness, but it means
  fam 1's `z_center` is *not* an exactly feasible packing and the "certified value" is a bound
  around a least-squares point 3.15e-3 from the A04 point.  Worth a look before the production
  run adopts the same fallback.
- **No 3R in the pilot proper.** If a large fraction of the 31 families is rank-deficient, the
  atlas will be almost entirely soft.  That is fine for a far-field discharge but means the
  cookbook's Step 3R(a)–(c) machinery only pays off on the (apparently rare) rigid families.
- **Dedupe found no merges** among {0, 1, 4, 6} (D4 + relabel canonical signature at 1e-6).
