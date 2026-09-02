# A64 — Lean wave 2: findings (Fable lead, 2026-09-02)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.

## T1 — A.PARAM discharged (prose + Lean)

* [T] `docs/proofs/parametrization.md` + `lean/PackingCertMathlib/PackingCertMathlib/
  Parametrize.lean`. The `parametrize` axiom of TopLevel is now a THEOREM (axioms
  `propext, Classical.choice, Quot.sound`). Content: `sqSet_rot` (the square's OWN 90°
  symmetry — no container needed) brings the edge vector into the closed first quadrant
  in ≤ 3 rotations; then `t = e₂/(1+e₁)` gives `cosT t = e₁`, `sinT t = e₂` by four
  polynomial identities modulo `e₁²+e₂² = 1`. No transcendental function appears anywhere.
* [F] The lemma needs only the `unit` field of `IsPacking` — parametrisation is a
  single-square statement; the packing form is `choose`.
* [E] The configuration layer (`cosT…PSq.set`) and set-level defs (`container`,
  `IsPacking`, `Fits`) moved verbatim from `TopLevel.lean` to `Parametrize.lean`
  (same namespace, no statement changed) so the measure bridge can consume them.
* [T] Bonus lemmas the bridge needed, proved alongside: `mem_set_iff_uv`
  (`p ∈ Q ⟺ |u| ≤ ½ ∧ |v| ≤ ½`), `set_subset_container_iff` (`Q ⊆ [0,s]² ⟺
  w/2 ≤ c ≤ s − w/2`), `wT_ge_one`, and `wT_ge_min` — quasiconcavity of `w = cos + sin`
  via the identity `w(b) − w(a) = 2(a−b)(a+b+ab−1)/((1+a²)(1+b²))`.

## T2 — A.F2 discharged: the measure bridge is a Lean theorem; s(11) ≥ 3.82 end to end

* [T] `MeasureBridge.lean` (~950 lines): full soundness of `checkMeasureI` (byte-identical
  copy `MeasureChecker.lean`, A28's Checker.lean pattern). Pieces: 4-corner interval
  product bound (`mul_bounds`/`imul4_cast_bounds`); `⌊·⌋`-division cast bound
  (`cast_ediv_le`); exact grid values `cosT(T/2^K) = (4^K−T²)/(4^K+T²)` and monotonicity
  (antitone cos on [0,∞), monotone sin on [0,1] — pure algebra); `trig_enclosure`;
  `projI_sound` (insideAll ⇒ atom ∈ Q, outsideAll ⇒ atom ∉ Q); `clipI_sound` (outward
  rounding + `wT_ge_min`; the clip can never drop an admissible point); `splitI_sound`
  (integer midpoints via omega); `sift_sound` (mass bookkeeping incl. the early-stop
  drop, which is why atom weights ≥ 0 is load-bearing); `go_sound` (fuel induction);
  `checkMeasureI_coverage`; and the counting/scaling argument `coverage_no_packing`.
* [T] The scaling step is done in CONFIGURATION space with no measure theory and almost
  no topology: scale centres by λ = S/s > 1, keep unit size; a point of the shrunk
  square pulled back by 1/λ has strict u/v coordinates, hence lies in the INTERIOR of
  the original square (one `mem_interior` + `isOpen_lt` argument) — so interior-disjoint
  packings give fully disjoint shrunk closed squares. Counting is a finite `Finset` ×
  `List` double sum swap; an atom lands in ≤ 1 square by disjointness.
* [T] `Measure382.lean`: `check_3_82` (`native_decide`, 5 837 883-box evaluation) +
  `s_eleven_ge_382 : ∀ s, Fits 11 s → 191/50 ≤ s`. TopLevel's `lb_382` axiom = this
  theorem now. Axioms: `propext, Classical.choice, Quot.sound` + the `native_decide` axiom
  (this toolchain emits a per-theorem `..._native.native_decide.ax_1_1` instead of the
  older `Lean.ofReduceBool`; same trust content) — exactly the brief's target.
* [F] **The A28 estimate "3–5 days" was right in spirit, wrong in bottleneck.** The
  mathematics (interval soundness, quasiconcavity, the counting argument) is routine;
  what actually costs is CROSS-TOOLCHAIN ELABORATION: the checker is compiled without
  Mathlib, so its `OfNat` numeral instances and `Decidable` instances differ
  SYNTACTICALLY from Mathlib-elaborated terms. `rw`/`simp` with Mathlib-written
  `if_pos h` silently fails against checker-compiled `ite`s (no match at reducible
  transparency) even when the proposition is literally the same. The working recipe,
  used uniformly: evaluate checker functions by `obtain ⟨res, hres⟩ : ∃ r, f args = r`,
  keep a pristine copy, `rw [f] at hres`, then `split at hres` (+ `dsimp only at hres`)
  — `split at` introduces case hypotheses in the GOAL'S OWN elaboration — and connect
  to Mathlib-side facts only through full-unification tactics (`exact`,
  `exact_mod_cast`), never through rewriting. Worth recording for the A22 Krawczyk
  replay (F6), which will hit the same wall.
* [E] CI note: `TopLevel` now imports `Measure382`, so the `mathlib` CI job includes the
  ~30 min `native_decide` evaluation (desktop: 26.5 min in the sibling project; the job
  timeout is 120 min and the module is cached across runs — only rebuilt when the
  measure files change). `.github/` was out of A64's write scope; if Actions minutes
  become a problem the PI can gate `Measure382` behind a separate lake target the same
  way `PackingCertSlow382` is gated.

## T3 — A.UBshat: identity assessed; sign route refuted; (c-idl) spec; Lean split executed

* [F] The brief's suggested "sign argument entirely in rationals" CANNOT close
  ŝ_A22 = ŝ_octic: equality of algebraic numbers needs a separation gap, a gap needs a
  height bound on ŝ_A22's minimal polynomial, and a-priori (arithmetic-Bézout) height
  bounds through the 34-variable system are doubly exponential — no reachable interval
  precision (2.1e-47 or otherwise) beats them. Closed off, not merely unexecuted.
  Written up as `docs/proofs/attainment_ub.md` §6.
* [C→spec] NEW closure spec **(c-idl)**, strictly cheaper than (c-alg): a saturated
  ideal-membership certificate `h·octic(s) = Σ q_k F_k + Σ r_i (c_i²+s_i²−1)` with
  `h(ẑ) ≠ 0`. Verification = rational polynomial identity + one interval sign gate
  (verify_sturm-class TCB, NO number-field arithmetic, no coordinate recovery); the
  cofactor search (Gröbner/Macaulay, untrusted) is a bounded future campaign.
* [T] Lean split executed in `TopLevel.lean` (the fallback clause WITHOUT regressing
  A63's `shat_spec`): `trump_packs_at_shat` is now a theorem from
  `shatA22` + `trump_packs_at_shatA22` (certified, Python-interval TCB) +
  `shatA22_eq_shat` (THE open identity, one axiom). Roster stays at 13 axioms but the
  algebraically-open content of A.UBshat is now exactly one named axiom; discharging
  (c-idl) later touches nothing else. The published restatement `s(11) = ŝ_A22`
  remains available by flipping which constant is primitive.
* [F] Side-finding while splitting: the `basin` axiom's certification is INTRINSIC
  (A22/A36 enclose σ against ŝ_A22-side quantities); as stated over the octic `shat` it
  also consumes the identification. Recorded in prose (attainment_ub.md §6); no
  statement change — the identity axiom is the single carrier either way.

## T4 — scoreboard

* `lean/depgraph.json`: new gold tier `lean-proved`; A.PARAM, A.F2, A.LB382 → lean-proved
  (A.S3 recoloured too); A.UBshat note carries the split + (c-idl); svg re-rendered
  (merged over A65's THMU/H10 updates, no conflicts). `lean/render_depgraph.py` COLORS
  updated. `lean/README.md` matrix + statement section updated;
  `scratch/Axioms.lean` extended (parametrize, checkMeasureI_no_packing,
  s_eleven_ge_382).
* Open-node count on the depgraph: 13 → 12 (A.PARAM out).
