import PackingCertMathlib.LocalCertS07Data

/-!
# `LocalDead` for the concrete neighbourhood `S07_trump5_r0.10_rho40` — A126 T1

The A119 certificate `S07_trump5_r0.10_rho40` (`attempts/A119-local-cert-lean/certs/`), independently re-checked
by `check_local.py`, has

  * 2410 tilt-cell bisections, 87 selection branches, 292 impossible-selection leaves,
  * 2302 DEAD leaves (746 of them infeasibility rays), 27363 Farkas rows,
    101629 nonzero rational coefficients.

`check_s07` runs the reflected weak-duality checker of `LocalCert.lean` on ALL 2302 of
them at once (`native_decide`), replacing 2302 `linarith` calls.  `localDead_s07` is
Theorem LOCAL for this `N`, modulo the single named cover obligation `CertCover` — see §3 of
`LocalCert.lean` and `attempts/A126-localdead-lean/notes/obligations.md`.

## The neighbourhood `N`

`L` (3 free bodies, one box each — the tilt interval is stated in the Lean parametrisation
`t = tan(θ/2)` and rounded INWARD, so `N` here is CONTAINED in the certificate's `N`):

  * `f0`: centre in [1.603357419, 1.803357419] × [1.838542000, 2.038542000], tilt θ ∈ [0.725446, 1.483530] rad, i.e. t = tan(θ/2) ∈ [0.379514900417, 0.916331174016] (rounded INWARD)
  * `f2`: centre in [2.308911163, 2.508911163] × [2.544095744, 2.744095744], tilt θ ∈ [0.725446, 1.483530] rad, i.e. t = tan(θ/2) ∈ [0.379514900417, 0.916331174016] (rounded INWARD)
  * `f4`: centre in [2.337443837, 2.537443837] × [1.161520930, 1.361520930], tilt θ ∈ [0.725446, 1.483530] rad, i.e. t = tan(θ/2) ∈ [0.379514900417, 0.916331174016] (rounded INWARD)

`P` (5 class pins, A57 slack cores, tilt exactly 0):

  * `BL(0,0)`: centre (1/2 + 0·s, 1/2 + 0·s) ± 0.007071067812, tilt 0
  * `BL(1,0)`: centre (3/2 + 0·s, 1/2 + 0·s) ± 0.007071067812, tilt 0
  * `BL(0,1)`: centre (1/2 + 0·s, 3/2 + 0·s) ± 0.007071067812, tilt 0
  * `BR(0,0)`: centre (-1/2 + 1·s, 1/2 + 0·s) ± 0.007071067812, tilt 0
  * `TR(0,0)`: centre (-1/2 + 1·s, -1/2 + 1·s) ± 0.007071067812, tilt 0

The certificate's own side window is `[3.82, 3.897084]`; the kill threshold is
`s0 = 969271/250000 = 3.877084 ≥ ŝ`.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Data

/-- The 2302 recorded dead leaves of `S07_trump5_r0.10_rho40` all pass the reflected weak-duality
check.  Evaluated by `native_decide`: the decoding, the accumulation of `e₀ + Σ y_r row_r`, the
coordinatewise minimisation over each leaf's box and the comparison with `s0` are all exact
rational arithmetic. -/
theorem check_s07 : s07Leaves.all (checkLeaf ((969271 : ℚ) / 250000)) = true := by
  native_decide

/-- The boxes of `L`. -/
noncomputable def s07Boxes : List Box := [
  ⟨((7220879872746933 : ℝ) / 4503599627370496), ((8121599798221033 : ℝ) / 4503599627370496), ((4140028533052503 : ℝ) / 2251799813685248), ((4590388495789553 : ℝ) / 2251799813685248), ((379514900417 : ℝ) / 1000000000000), ((7158837297 : ℝ) / 7812500000)⟩,
  ⟨((5199205726410575 : ℝ) / 2251799813685248), ((5649565689147625 : ℝ) / 2251799813685248), ((2864397161544805 : ℝ) / 1125899906842624), ((1544788571456665 : ℝ) / 562949953421312), ((379514900417 : ℝ) / 1000000000000), ((7158837297 : ℝ) / 7812500000)⟩,
  ⟨((5263455596904945 : ℝ) / 2251799813685248), ((5713815559641995 : ℝ) / 2251799813685248), ((653878153377441 : ℝ) / 562949953421312), ((1532936288123407 : ℝ) / 1125899906842624), ((379514900417 : ℝ) / 1000000000000), ((7158837297 : ℝ) / 7812500000)⟩
  ]

/-- The slack cores of `P`. -/
noncomputable def s07Pins : List Pin := [
  ⟨((1 : ℝ) / 2), (0 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((3 : ℝ) / 2), (0 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((1 : ℝ) / 2), (0 : ℝ), ((3 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((-1 : ℝ) / 2), (1 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((-1 : ℝ) / 2), (1 : ℝ), ((-1 : ℝ) / 2), (1 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩
  ]

/-- **`LocalDead` for `S07_trump5_r0.10_rho40`** — Theorem LOCAL for a concrete `N`, from the kernel-checked
certificate plus the cover obligation.  Everything ARITHMETIC in the certificate (every leaf's
Farkas vector, every box minimisation, 27363 rows) is discharged by `check_s07`; the
hypothesis `hcov` is Lemma COVER + Lemma RELAX, i.e. "the recorded leaves cover `N`". -/
theorem localDead_s07
    (hcov : CertCover s07Leaves s07Boxes s07Pins (((969271 : ℚ) / 250000 : ℚ) : ℝ)) :
    LocalDead s07Boxes s07Pins (((969271 : ℚ) / 250000 : ℚ) : ℝ) :=
  localDead_of_cert check_s07 hcov

/-- The same at `ŝ`, the shape `Local.classKilledAt_of_localDead` consumes
(`ŝ ≤ 3877084/1000000 = s0` by `shat_spec`). -/
theorem localDead_s07_shat
    (hcov : CertCover s07Leaves s07Boxes s07Pins (((969271 : ℚ) / 250000 : ℚ) : ℝ)) :
    LocalDead s07Boxes s07Pins shat := by
  have h := localDead_s07 hcov
  intro s z hz hN
  have h1 := h s z hz hN
  have h2 : shat ≤ (((969271 : ℚ) / 250000 : ℚ) : ℝ) := by
    have := shat_spec.2.1.2
    push_cast
    norm_num at this ⊢
    linarith
  linarith

end LocalCert
end S11
end PackingCert
