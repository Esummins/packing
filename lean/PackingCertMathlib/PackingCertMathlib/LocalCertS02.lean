import PackingCertMathlib.LocalCertS02Data

/-!
# `LocalDead` for the concrete neighbourhood `S02_k5_11_r0.20_rho10` — A126 T1

The A119 certificate `S02_k5_11_r0.20_rho10` (`attempts/A119-local-cert-lean/certs/`), independently re-checked
by `check_local.py`, has

  * 32426 tilt-cell bisections, 63 selection branches, 0 impossible-selection leaves,
  * 32570 DEAD leaves (5782 of them infeasibility rays), 504404 Farkas rows,
    1977332 nonzero rational coefficients.

`check_s02` runs the reflected weak-duality checker of `LocalCert.lean` on ALL 32570 of
them at once (`native_decide`), replacing 32570 `linarith` calls.  `localDead_s02` is
Theorem LOCAL for this `N`, modulo the single named cover obligation `CertCover` — see §4 of
`LocalCert.lean` and `attempts/A126-localdead-lean/notes/obligations.md`.

## The neighbourhood `N`

`L` (4 free bodies, one box each — the tilt interval is stated in the Lean parametrisation
`t = tan(θ/2)` and rounded INWARD, so `N` here is CONTAINED in the certificate's `N`):

  * `f1`: centre in [1.062500739, 1.462500739] × [2.226657559, 2.626657559], tilt θ ∈ [0.670819, 1.019885] rad, i.e. t = tan(θ/2) ∈ [0.348580331259, 0.559283157592] (rounded INWARD)
  * `f2`: centre in [1.724319429, 2.124319429] × [2.973002602, 3.373002602], tilt θ ∈ [0.670819, 1.019885] rad, i.e. t = tan(θ/2) ∈ [0.348580331259, 0.559283157592] (rounded INWARD)
  * `f3`: centre in [2.414583232, 2.814583232] × [2.247940520, 2.647940520], tilt θ ∈ [0.670819, 1.019885] rad, i.e. t = tan(θ/2) ∈ [0.348580331259, 0.559283157592] (rounded INWARD)
  * `BR(0,1)`: centre in [3.177084000, 3.577084000] × [1.300000000, 1.700000000], tilt θ ∈ [-0.174533, 0.174533] rad, i.e. t = tan(θ/2) ∈ [-0.087488663524, 0.087488663524] (rounded INWARD)  **this cell leaves θ ∈ [0°, 90°]: the box carries only its inside part**

`P` (5 class pins, A57 slack cores, tilt exactly 0):

  * `BL(0,0)`: centre (1/2 + 0·s, 1/2 + 0·s) ± 0.007071067812, tilt 0
  * `BL(0,1)`: centre (1/2 + 0·s, 3/2 + 0·s) ± 0.007071067812, tilt 0
  * `TL(0,0)`: centre (1/2 + 0·s, -1/2 + 1·s) ± 0.007071067812, tilt 0
  * `BL(1,0)`: centre (3/2 + 0·s, 1/2 + 0·s) ± 0.007071067812, tilt 0
  * `BR(0,0)`: centre (-1/2 + 1·s, 1/2 + 0·s) ± 0.007071067812, tilt 0

Every box above is CONTAINED in the certificate's own cell -- the centre bounds are the
certificate's exact dyadic numbers, the tilt bounds are rounded INWARD, and a tilt cell that
leaves the fundamental domain `theta in [0, 90 deg]` keeps only its inside part (`Box` carries
one interval in `t = tan(theta/2)`, while such a cell is the union of two).  A smaller `N` makes
`LocalHyp` harder to satisfy and `LocalDead` a weaker statement, so this direction is the sound
one; the marked boxes are where it is strict.

The certificate's own side window is `[3.82, 3.897084]`; the kill threshold is
`s0 = 969271/250000 = 3.877084 ≥ ŝ`.
-/

namespace PackingCert
namespace S11
namespace LocalCert

open Data

/-- The 32570 recorded dead leaves of `S02_k5_11_r0.20_rho10` all pass the reflected weak-duality
check.  Evaluated by `native_decide`: the decoding, the accumulation of `e₀ + Σ y_r row_r`, the
coordinatewise minimisation over each leaf's box and the comparison with `s0` are all exact
rational arithmetic. -/
theorem check_s02 : s02Leaves.all (checkLeaf ((969271 : ℚ) / 250000)) = true := by
  native_decide

/-- The boxes of `L`. -/
noncomputable def s02Boxes : List Box := [
  ⟨((299067370632385 : ℝ) / 281474976710656), ((3293258890533179 : ℝ) / 2251799813685248), ((313374192230635 : ℝ) / 140737488355328), ((1478676750291065 : ℝ) / 562949953421312), ((348580331259 : ℝ) / 1000000000000), ((69910394699 : ℝ) / 125000000000)⟩,
  ⟨((7765644337381863 : ℝ) / 4503599627370496), ((4783542094165031 : ℝ) / 2251799813685248), ((836825838154095 : ℝ) / 281474976710656), ((1898831657676715 : ℝ) / 562949953421312), ((348580331259 : ℝ) / 1000000000000), ((69910394699 : ℝ) / 125000000000)⟩,
  ⟨((5437158070922815 : ℝ) / 2251799813685248), ((6337877996396915 : ℝ) / 2251799813685248), ((5061912043333949 : ℝ) / 2251799813685248), ((5962631968808049 : ℝ) / 2251799813685248), ((348580331259 : ℝ) / 1000000000000), ((69910394699 : ℝ) / 125000000000)⟩,
  ⟨((3577078579631191 : ℝ) / 1125899906842624), ((4027438542368241 : ℝ) / 1125899906842624), ((5854679515581645 : ℝ) / 4503599627370496), ((7656119366529843 : ℝ) / 4503599627370496), ((-21872165881 : ℝ) / 250000000000), ((21872165881 : ℝ) / 250000000000)⟩
  ]

/-- The slack cores of `P`. -/
noncomputable def s02Pins : List Pin := [
  ⟨((1 : ℝ) / 2), (0 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((1 : ℝ) / 2), (0 : ℝ), ((3 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((1 : ℝ) / 2), (0 : ℝ), ((-1 : ℝ) / 2), (1 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((3 : ℝ) / 2), (0 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩,
  ⟨((-1 : ℝ) / 2), (1 : ℝ), ((1 : ℝ) / 2), (0 : ℝ), ((2038096535208247 : ℝ) / 288230376151711744)⟩
  ]

/-- **`LocalDead` for `S02_k5_11_r0.20_rho10`** — Theorem LOCAL for a concrete `N`, from the kernel-checked
certificate plus the cover obligation.  Everything ARITHMETIC in the certificate (every leaf's
Farkas vector, every box minimisation, 504404 rows) is discharged by `check_s02`; the
hypothesis `hcov` is Lemma COVER + Lemma RELAX, i.e. "the recorded leaves cover `N` on the
certificate's own window `[191/50, 974271/250000] = [3.82, 3.897084]`".  That window reaches
ABOVE `s0`, so `hcov` is NOT a consequence of the conclusion — see `LocalCert.CertCover`. -/
theorem localDead_s02
    (hcov : CertCover s02Leaves s02Boxes s02Pins
      ((191 : ℝ) / 50) ((974271 : ℝ) / 250000)) :
    LocalDead s02Boxes s02Pins (((969271 : ℚ) / 250000 : ℚ) : ℝ) :=
  localDead_of_cert (by norm_num) (by push_cast; norm_num) check_s02 hcov

/-- The same at `ŝ`, the shape `Local.classKilledAt_of_localDead` consumes
(`ŝ ≤ 3877084/1000000 = s0` by `shat_spec`). -/
theorem localDead_s02_shat
    (hcov : CertCover s02Leaves s02Boxes s02Pins
      ((191 : ℝ) / 50) ((974271 : ℝ) / 250000)) :
    LocalDead s02Boxes s02Pins shat := by
  have h := localDead_s02 hcov
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
