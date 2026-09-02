# A79 — rigidity replay in Lean, rungs (b)/(c): findings (Fable lead, 2026-09-02)

Labels: [T] proved, [F] finding, [C] open, [E] engineering.

Verdicts: RUNG (b) E.A22 LEAN-PROVED (Krawczyk uniqueness + feasibility + A22 §5
optimality, `checkA22` replayed by `native_decide`); RUNG (c) E.A36 LEAN-PROVED for the
UNIVERSAL certificate (`G3_UNIVERSAL`, radius 3689/10⁶), which is what the composition
consumes; all 17 A36 certificates replayed by `native_decide`.  TopLevel: `zhat`,
`shatA22`, `trump_packs_at_shatA22`, `basin` are now DEFINITIONS/THEOREMS; with A78's
census/CIDL discharges the named-axiom roster is down to `a22_exact_structure` (A78's
A22 interface), `stratum_kill`, `trump_residual`.

## The Lean chain (all in `lean/PackingCertMathlib/PackingCertMathlib/`)

| file | content |
|---|---|
| `RigidKernel.lean` | core Lean: dyadic-rounded `IV`, Taylor brackets `cosPt/sinPt/cosIV/sinIV`, the deep-embedded row language `Expr` with symbolic `D`, `evalIV`, order-2 `jet`; A22 rows; `checkA22`; A36 v3 table + `checkA36` |
| `RigidData22.lean`, `RigidData36.lean` | GENERATED (`lean/gen_rigidity_lean.py`) from `krawczyk_cert.json` and the 17 `G3_*.json` |
| `RigidIV.lean` | rounding widens; `mem_add/sub/neg/mul/mag`; `cos_bracket`/`sin_bracket` (Mathlib `Real.hasSum_cos/sin` + `Antitone.alternating_series_le_tendsto`); `cosIV_sound`, `sinIV_sound` |
| `RigidExpr.lean` | `eval`, `evalIV_sound`, `jet_sound` (value/gradient/Hessian in one induction), `gradDense_sound`, `hessDense_sound`, `hasDerivAt_eval` (symbolic `D` = the derivative along any segment), `mvt_box` |
| `RigidKrawczyk.lean` | `krawczyk_sound`: `krawczykOK = true` ⟹ exactly one zero in the box (Banach on the true box, contraction from the checked row sums `β_i < 1`, `Y` invertible by Neumann + `Matrix.mulVec_injective_iff_isUnit`) |
| `RigidGeom.lean` | θ-frame squares `sqZ` (= `PSq` with `t = tan(θ/2)`), rows as body coordinates, validity lemmas `wall_valid`/`dist_valid`/`edge_valid`, separation `disjoint_of_rows`/`disjoint_upright`, exact-structure lemmas `sin_zero_of_mates`, `theta_eq_of_pair`, `row_transfer`, `wall_transfer` |
| `RigidA22.lean` | `zhatV` (the unique zero), `zhatV_unique_N`, `zhatV_feas` (feasibility from the searched witnesses), `zhatV_tilt_nonneg` |
| `RigidOptimal.lean` | `a22_optimal` / `a22_optimal'`: A22 §5 (Farkas + MVT on the box) |
| `RigidA36.lean`, `RigidBasin.lean`, `RigidBasinMain.lean` | `taylor2` (two MVTs), `quad_pin`, the enclosure lemmas for `ε₀, ε_w, H̄, β, κ, κ_eff, g_max`, max-form pinning, `a36_basin` |
| `RigidityCheck.lean` | ISOLATED `native_decide`: `checkA22_a22`, `checkA36_universal`, `checkA36_all17` (module build 140 s incl. compilation) |
| `Rigidity.lean` | `zhatCfg`, `shatR`, `zhatCfg_packing`, `basin_tframe` (t-frame, slab gate `(3/2000)(1+√2) ≤ 3689/10⁶`) |

## Findings

* [F] **Frame decision: θ, not t.**  A70's finding carries to the Lean tier: staying in
  the θ frame keeps every certificate constant verbatim; the price is certified cos/sin
  brackets, which Mathlib provides essentially for free (`Real.hasSum_cos` + the antitone
  alternating-series bounds — no Taylor-remainder API, no quartic `Real.cos_bound`).
  A76's t-native Krawczyk enclosure was not needed.

* [F] **One deep embedding, one induction.**  Encoding the rows as a small expression
  language (`var/const/add/sub/mul/neg/cosv/sinv`) with SYMBOLIC differentiation `D` makes
  the interval jets' soundness a single structural induction (value, gradient, Hessian
  together), and `hasDerivAt_eval` (`D` is the derivative along every straight segment)
  is the only analytic bridge; the MVT and second-order Taylor are then 1-D Mathlib
  lemmas.  No Fréchet derivatives, no `iteratedDeriv`.

* [F] **The A22 re-checker's [F] is not self-contained; the feasibility of ẑ needs the
  exact-structure argument, and it is derivable from `S` alone.**  `recheck.py`
  (and A70's exact replay) skips the three dropped wall rows and the flush pairs
  ("exact by inspection", A22 §3–4, via the second system S2).  The Lean port had to make
  this generic: (i) mate wall rows in `S` force `sin θ_i = 0` (`sin_zero_of_mates`), (ii) a
  corner-on-edge / edge-on-corner PAIR in `S` with parallel body normals forces equal tilts
  (`theta_eq_of_pair` — the two lines meet in one point unless parallel, and the
  tangential margin of [V] excludes the coinciding-corner case), closed transitively
  (`angRel`), (iii) rows transfer across a corner when the angles agree (`row_transfer`),
  and (iv) the flush-upright block needs an affine "known centre coordinate" inference over
  the dist rows (`knownFix`; pairs (0,1), (0,3), (1,3) were the only interval failures).
  S2 (the angle-equality system) is replayed for fidelity but is NOT load-bearing.

* [F] **Quantities the Python evaluates at z0 must be evaluated over box(z0, r0).**
  `ε₀, ε_w, g_max` and the activity checks are point evaluations at the rational centre in
  both re-checkers; the theorem is about ẑ, so the Lean checker evaluates them over
  `box(z0, r0) ∋ ẑ`.  Effect: `ε₀ ≈ 1.4e-49` (Python 1.05e-59), `g_max ≈ 4.3e-50`,
  `x* ≈ 6.3e-48` (Python 5e-58) — harmless (`x* + r0 ≤ r_N` with 46 orders of margin);
  the certificates' float `claims` for these three are not reproduced and the 1e-59
  activity threshold of [N] is unattainable with a 1e-50 box (checked at 1e-40).

* [F] **The basin composition only needs the UNIVERSAL certificate.**  The `basin` axiom
  quantifies over `InBasin` at `rBasin = 3/2000` in `(cx, cy, t)`; the sharp slab gate is
  `rBasin·(1 + √2) = 3.6213e-3 < 3689/10⁶ = h_UNIVERSAL` (`slab_gate_universal`,
  `√2 < 1.459`), and the tilt gate `2·rBasin = 3e-3 < h`.  So the branch-free barrier at
  7.378 r_N suffices and the 16 variant certificates (h = 3779/10⁶, needing the L1
  axis disjunction = SAT completeness) are NOT load-bearing at this `rBasin`; they are
  replayed (`checkA36_all17`) but their soundness theorem is not formalised (named
  residue).  The E.COORD gates (`37/10000`) are untouched.

* [F] **The 800-step fixed-point iteration is replaced by a two-point convexity
  argument.**  `ψ` is a convex quadratic; the checker verifies `ψ(h) < h` and, for the
  iterate `x*` it computed, `ψ(x*) ≤ x*` explicitly; `quad_pin` then gives
  `x ≤ ψ(x) ∧ x ≤ h ⟹ x ≤ x*` from the identity
  `(h−x*)q(x) = (h−x)q(x*) + (x−x*)q(h) + A(x−h)(h−x*)(x−x*)`.  No iteration is trusted.

* [F] **Krawczyk needs the row sums, not just the containment.**  The Python infers
  `‖I − Y[J]‖_∞ < 1` from `K(X) ⊂ int X`; the Lean checker checks `β_i < 1` explicitly
  (implied by the Python check), so Banach's constant is a checker output.  The contraction
  is proved on the ROUNDED box (uniqueness there) while the mapping property `G(X) ⊂ int X`
  is proved on the TRUE box `‖z − z0‖_∞ ≤ r` (existence there): the rounded box is not
  exactly `z0 + [−r, r]`, and the checker's `dbox = mkR(−r, r)` is what the true box lands in.

* [E] Faithfulness deviations, all decision-neutral or stricter: explicit `β_i < 1`;
  `ψ(x*) ≤ x*`; `x* + r0 ≤ r_N`; basin boxes at `h + r0`; loaded-row validity margins checked
  on the box (universal certificates only); `S` verified angeq-free; pins verified distinct
  and in range; a far-wall `S` row verified to exist (the slab gate's witness).  The
  interval statistics agree with A70's exact replay to displayed precision (K/r 0.05896 /
  4.919e-10 / 0.04713, tan 0.01900, β 0.6339, ν_max 57.01; A36 UNIVERSAL β 0.4353,
  H̄ 7.908, κ 20.292, κ_eff 19.316, tan 0.00617, kill 0.989).

* [E] Engineering notes: a 34-row record literal with 60-digit rationals exceeds the
  elaborator's recursion depth — emit one `def` per large component; core-Lean
  `Array.zipWith` argument order is toolchain-dependent — `Array.ofFn` + `getD` with
  `Array.getElem_ofFn` is the robust idiom; `Nat`-indexed `Expr` variables with
  `getV : Vec → ℕ → ℝ` (zero out of range) keep the checker free of `Fin` proofs while the
  analysis sums over `Fin 34`; `List.range` inside the checker must not be called `range`
  (shadows `Finset.range` in the bridge files); interpreted `#eval` of the A22 chain takes
  43 s, of the 17 A36 certificates 2 min — fine for development.

## Residues (named)

* [C] Variant certificates: soundness (L1 axis disjunction) not formalised; not needed.
* [C] `a22_exact_structure` (A78's A22 interface axiom: the generators vanish at ẑ,
  t̂ ∈ [3/10, 2/5], ŝ_A22 in the isolating interval) is now an axiom ABOUT the defined
  `zhat`/`shatA22`; its content is within reach of this chain (`zhatV_zero`,
  `zhatV_inBoxR`, `upright_zero`, `angRel_sound`, `zhatVec_tilt`) but was not packaged.
