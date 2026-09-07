# A126 — the next step, priced

`CertCover` is the single hypothesis between the kernel-checked leaves and `LocalDead` for a
concrete `N` (`notes/obligations.md` §2).  Two routes reach it.  They are not equally expensive
and the cheaper one is not a Lean route.

## Route A — a certified rational-interval kernel for `cos`, `sin`, `π` in Lean

What has to exist, in the shape A119's `code/exactiv.py` already has it:

| piece | `exactiv.py` | what Lean needs |
|---|---|---|
| `π` to ~30 digits with a proof | `PI` (dyadic, scale `2⁻⁹⁶`) | Mathlib has `Real.pi_gt_3141592` / `pi_lt_3141593` — 7 digits.  More needs the Machin-type series with an explicit remainder |
| `cos_q` / `sin_q` at a rational point | Taylor with an explicit dyadic remainder | Mathlib's `Real.cos_bound` / `Real.sin_bound` give `\|x\|⁴·(5/96)` for `\|x\| ≤ 1` — enough for ~3 digits at `x ≈ 1`, not for the 10⁻⁹ the certificates use.  Higher-order alternating-series bounds with explicit remainders are the work |
| `cos_iv` / `sin_iv` over a rational interval | endpoints plus the multiples of `π` (cos) and `π/2` (sin) inside the cell | monotonicity between the critical points; `Real.strictMonoOn_sin` and `Real.cos_le_cos_of_nonneg_of_le_pi` are already used in `Local.lean` |
| `w_iv`, `w = \|cos\| + \|sin\|` | endpoints plus the multiples of `π/4` (extrema `1`, `√2`) | the same, plus `√2` |
| `kink_in` | the multiple of `π/2` strictly inside a cell, decided by the `π` enclosure | a decision procedure with a proof that it cannot be fooled at the granularity in use |

Then (C2) and (C3) of `obligations.md` follow from lemmas already proved in `Local.lean`
(`axis_decomp`, `mccormick_hi/lo`, `abs_chord`, `chord_of_concave`, `abs_sin_le_sin`,
`cos_ge_of_abs_le`).  **A119's finding F4 is the warning**: the kernel has to reproduce the
generator's SHARPNESS, not merely be sound — a looser but perfectly valid enclosure made the
first version of `check_local.py` reject a `branch` node of S07 (0.1, 40°) whose root cell is
80° wide.

This is the honest, self-contained Lean route, and it is a project, not a task.

## Route B — re-emit the certificate in `t = tan(θ/2)`

Lean's own tilt parameter.  `Parametrize.cosT t = (1 − t²)/(1 + t²)` and
`sinT t = 2t/(1 + t²)` are RATIONAL functions, and `cosT_sq_add_sinT_sq` is proved for EVERY
real `t` — no domain condition, no `π`, no series.  On a rational cell `t ∈ [a, b] ⊆ [0, 1]`:

* `cosT` is decreasing and `sinT` increasing, so their exact ranges are the endpoint values —
  **exact rational interval arithmetic, no enclosure error at all**;
* `w(Δ) = |cos Δ| + |sin Δ|` becomes a rational function of the two tilt parameters through the
  addition formulas already written into `Local.wrel`;
* every constant in the relaxed rows (`a_k(θ*)`, `1 − cos h_w`, `sin h_w`, the chord of `w`) is
  a rational number of the cell endpoints.

The whole trig kernel leaves the trusted base.  The cost is on the GENERATOR side and it is
real: the relaxation is currently affine in the tilt ANGLE about the cell midpoint
(`axis_decomp` + McCormick + the `|q|` chord), and in `t` the axis components are rational, not
affine, so the relaxation has to be redone — a rational-function relaxation over the cell (for
instance: multiply through by `(1 + t²)` and relax the resulting bilinear terms, which is again
McCormick, on a cell where `t` is bounded) — and every LP re-solved.  A119's own numbers price
the re-solve: 32 570 leaves at `S02 (0.2, 10°)` took 91 s of tree time with `fastlp`.

**Recommendation: Route B.**  It removes a whole class of trusted arithmetic rather than
formalising it, it reuses A119's tree and checker structure unchanged, and the Lean side is then
exactly what already exists here — `checkLeaf` for the leaves plus a decidable cover check, with
`sat_selection_thm` supplying the only geometry.  Route A is worth doing only if the relaxation
in `t` turns out to be materially weaker than the relaxation in `θ`, which should be measured
first, on one cell, before anything is rebuilt.

## Two smaller items, both cheap

* **`Local.Box` should carry a LIST of `t`-intervals** (finding E3), as `CaseChecker.CNoFam.tivs`
  and `ParamNoFam.PNoFam.tivs` already do.  Without it a tilt cell that straddles `θ = 0` or
  `θ = 90°` can only be represented by its inside part, and `S02 (0.2, 10°)`'s `BR(0,1)` is such
  a cell.  A120 already emits both intervals on its side; it is only `Box` that cannot say it.
* **Emit A120's NO zone with INWARD rounding** (finding F-COVER) and re-certify the four
  children.  The amounts are `≤ 1.07·10⁻⁷` in tilt and `≤ 4.71·10⁻¹⁰` in the upper centre
  bounds — far below the resolution at which those certificates pass, so this should be a
  formality, and it is what makes the YES/NO split an actual tautology.
