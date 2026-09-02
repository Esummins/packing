# A68 — Lean wave 3: findings (Fable lead, 2026-09-01)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.

Verdicts: T1 LEAN-PROVED (axiom discharged, roster 13 -> 12). T2 LEAN-PROVED (geometry +
pricing; residues named). T3 PARTIAL (K1(i) lean-proved; M->E conditional on the census
interface — obligation F11/H2). T4 LEAN-PROVED (transfer constants + gates; `basin` stays an
axiom by design). Full library builds, `scratch/Axioms.lean` audit clean; every new theorem
depends on `propext, Classical.choice, Quot.sound` only.

## T1 — A.D1 `attained` DISCHARGED (`Attain.lean`, -> theorem in `TopLevel.lean`)

* [T] `attained : ∃ m, IsLeast {s | Fits 11 s} m` is a THEOREM. Route: compactness in the
  33+1 COORDINATES (not in the space of sets): the feasible region `Dom` (tilts in [0,1],
  the `set_subset_container_iff` containment inequalities, pairwise non-overlap, side in
  [0,11]) is closed and bounded; the side projection is continuous;
  `IsCompact.exists_isMinOn`; `parametrize` (A64) maps set-level packings into `Dom`;
  explicit 11-in-a-row packing at side 11 for nonemptiness; `s >= 0` from a corner point.
* [T] The load-bearing new lemma is `mem_interior_iff_uv`: the interior of a parametrised
  square is EXACTLY the open u/v box. `⊇` was A64's `strict_uv_mem_interior`; `⊆` is a push
  of length eps/2 along ±edir/±perp. This makes interior-disjointness a closed condition
  (overlap = ∃ witness point with four strict inequalities = open).
* [F] The old TopLevel docstring priced D1 as "Hausdorff-limit argument on the configuration
  representation". No limit argument of any kind is needed; the (A64) coordinate
  characterisations were already sufficient. Cost was ~300 lines.
* [F] Prose D1 asserts "D0 closed" as evident; true, but the only non-obvious ingredient is
  (i) above — recorded in `drain_lemma.md` (D1 annotated, no gap).

## T2 — A.SBRIDGE Lemma B / B' / B-NO (`Dilation.lean`)

* [T] B.0(a) `scaleC_disjoint`, B.0(b) (= A64 `scaleC_subset`), B.0(c) `slot_tracking`,
  `dilation_bridge` (CfgPacking at m ⟹ `IsStrictFamily` at lam*m, centres lam*c and tilts
  unchanged definitionally), `lemma_B` (certificate claim abstracted), and — the full prose
  proof content — `priced_dichotomy` / `hcert_of_priced`: (P1) Sigma w < b = n − r plus (P2)
  "admissible ∧ core-free ∧ non-exempt ⟹ mu >= 1" refute any strict family whose owners
  contain the cores, via mu-additivity over the >= b disjoint non-owners (A64's `massIn` /
  `indicator_sum_le` machinery reused, sub-family padded by ∅). The `Exempt` parameter makes
  Lemma B-NO the SAME theorem (its conclusion: some non-owner is exempt). Corollary B''s
  (H') ⟹ (H) step is `bprime_containment`; the B.2'' pullback widening is `pullback_mem_Icc`.
* [F] The SAT/separating-axis citation in prose B.0(a) is UNNECESSARY: A64's pull-back trick
  (a common point of the dilates pulls back by 1/lam to a common interior point) gives strict
  disjointness with no separation theorem. Prose annotated.
* [F] Hypothesis (H)'s "open interior" clause is not needed for Lemma B's conclusion —
  closed containment suffices for both "meets no core" and the pricing; it matters only for
  certificate-side exemption semantics. Prose annotated (B.5).
* [F] B.0(c) needs no hypothesis on beta: lam(a+b m) − (a+b lam m) = (lam−1)a identically.
* [C->named] Residues: producing (P2) for a concrete PASS file = V.CASE (the case-LP verifier
  soundness, the analogue of A64's MeasureChecker replay — the next big Lean item on this
  branch); B.2' owner-frame criterion (tilted cores) prose-only; corpus margin rho stays [M].

## T3 — B.K1 / B.EXACT (`Skeleton.lean`) — PARTIAL, obligation named

* [T] Slot model (`Slot` = corner × Young cell, `slotCentre` affine a + b*s), `ContainsPins`
  (injective slot assignment), K1(i) as `containsPins_mono`/`kill_mono`,
  `occupiesSlot_of_axis` (t ∈ {0,1} squares occupy their slot, via the new
  `set_of_t_zero`/`set_of_t_one` axis characterisations in `Dilation.lean`).
* [F] In the indexed slot model K1(i) is content-free: the prose's geometric step
  "sub-diagram cells keep their offsets ⟹ slots_S(s) ⊆ slots_S'(s)" IS the pin-set
  inclusion. ALL of K1's residual mathematical content sits in the census's identification
  of slot indices with plane positions — i.e. exactly in F11/H2, nowhere else.
* [T/C] M->E formalised as `monotone_to_exact` with the census interface as hypothesis
  `hface : Exact z -> ContainsPins T s z` (after D4 normalisation). NAMED OBLIGATION: `hface`
  per class = the Young census as a Lean definition (F11/H2) + E.2's D4 bookkeeping (the
  equivariance A67 R8 machine-checked computationally). E.1(ii) (aliveness descends)
  deliberately not formalised: a tau*-statement about which certificates can exist —
  completeness, not soundness; it belongs to no trusted-composition node.

## T4 — E.COORD theta<->t transfer (`ThetaT.lean` + gates in `TopLevel.lean`)

* [T] `cosT_eq_cos`/`sinT_eq_sin`: the rational parametrisation IS cos/sin of
  theta(t) = 2*arctan t — the first formal tie between t-world and theta-world. X.1 both
  directions: arctan 1-Lipschitz (MVT, universal) and tan 2-Lipschitz on [0, pi/4]
  (cos^2 >= 1/2). Circle bound (dcos)^2 + (dsin)^2 <= dtheta^2 via 2 − 2cos x <= x^2
  (`Real.one_sub_sq_div_two_le_cos`). X.2 `corner_perturb` with the sharp constant
  r_c + sqrt2*r_t (Cauchy–Schwarz on the body coordinates, (a−1/2)^2 + (b−1/2)^2 <= 1/2).
  Gates: `rBasin_gate_tilt`, `rBasin_gate_slab` are TopLevel theorems; composed form
  `corner_perturb_rBasin` (< 37/10000 inside the box).
* [F] Sharpness is load-bearing, now machine-checked: the naive per-component estimate
  r_c + 2r_t gives 3*rBasin = 4.5e-3 > 3.7e-3 and fails gate (b). And the slab gate is
  EXACTLY sqrt2 < 22/15: (3/2000)*(1 + 22/15) = 37/10000 with equality — rBasin = 3/2000
  sits precisely at the rational threshold the prose slack ledger described.
* [C unchanged, by design] The `basin` axiom itself: A36's interval computations remain
  Python-certified (mpmath.iv, checklist F6); the wall-touching step of X.3(b) consumes the
  opaque `zhat`. T4's deliverable was the transfer's justification layer, now gold.

## Engineering notes (this toolchain, delta over A64's recipe)

* [E] Mathlib at v4.34.0-rc1 (this repo's pin) has renamed: `le_or_lt` -> `le_or_gt`,
  `abs_add` -> `abs_add_le`, `Set.mem_setOf_eq` -> `Set.mem_ofPred_eq` (deprecation),
  `push_neg` -> `push Not` (deprecation), and min-attainment is `IsCompact.exists_isMinOn`
  (no `exists_forall_le`).
* [E] `@[fun_prop]` on `continuous_cosT/sinT/wT` makes all the configuration-space
  continuity goals one-liners after `simp only [rdot, edir, perpV, toPSq]`.
* [E] The linter set flags unused simp args and `show`-for-defeq; both avoided by explicit
  `have` restatements (defeq `exact` through `scaleC`/`rBasin` unfolds fine).
* [E] New modules are in the default lake target (root import list), so the existing CI
  (`lean.yml`: full build + `scratch/Axioms.lean` audit incl. the new prints) covers them;
  the isolated 2380 s `Measure382Check` module was neither edited nor rebuilt (cache hit).
