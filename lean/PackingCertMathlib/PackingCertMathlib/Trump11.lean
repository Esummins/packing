import PackingCertMathlib.Bridge
import PackingCertMathlib.Data

/-!
# `s(11) ≤ 969271/250000 = 3.877084`, as a statement about ℝ²

This combines
* the *computational* fact `checkPackingCCW Data.trump11 = true` (`native_decide`, the same
  certificate as `PackingCert.trump11_ok` in `lean/PackingCert`), and
* the *semantic* bridge `checkPackingCCW_sound` (`Bridge.lean`),

into a statement that mentions only real geometry.
-/

namespace PackingCert

open Data

/-- The certificate is accepted by the counter-clockwise checker (`native_decide`). -/
theorem trump11_ccw_ok : checkPackingCCW Data.trump11 = true := by native_decide

set_option maxRecDepth 10000 in
/-- The same fact by **kernel** evaluation: no `native_decide`, hence no compiler trust. -/
theorem trump11_ccw_ok_kernel : checkPackingCCW Data.trump11 = true := by decide

/-- Hence it is also accepted by the checker verified in `lean/PackingCert`. -/
theorem trump11_ok_of_ccw : checkPacking Data.trump11 = true :=
  checkPackingCCW_imp trump11_ccw_ok_kernel

theorem trump11_squares_length : Data.trump11.squares.length = 11 := by rfl

/-- **Eleven pairwise disjoint closed unit squares fit in the closed square of side
`969271/250000 = 3.877084`.**  Hence `s(11) ≤ 3.877084`. -/
theorem eleven_unit_squares_in_3877084 :
    ∃ Q : List (Set RP),
      Q.length = 11 ∧
      (∀ q ∈ Q, IsUnitSquare q) ∧
      (∀ q ∈ Q, q ⊆ Set.Icc (0 : ℝ) (969271 / 250000) ×ˢ Set.Icc (0 : ℝ) (969271 / 250000)) ∧
      Q.Pairwise Disjoint := by
  obtain ⟨Q, hlen, hunit, hsub, hdisj⟩ := checkPackingCCW_sound Data.trump11 trump11_ccw_ok_kernel
  refine ⟨Q, by rw [hlen]; rfl, hunit, ?_, hdisj⟩
  intro q hq
  have := hsub q hq
  norm_num [Data.trump11] at this ⊢
  exact this

end PackingCert
