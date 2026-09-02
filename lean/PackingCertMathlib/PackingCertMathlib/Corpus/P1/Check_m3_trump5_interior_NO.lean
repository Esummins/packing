import PackingCertMathlib.Corpus.P1.Data_m3_trump5_interior_NO
import PackingCertMathlib.CaseBridge

/-!
# `m3_trump5_interior_NO` replayed in Lean (A78 T5, corpus P1)

Certificate `attempts/A59-trump-residual/certs/m3_trump5_interior_NO.json`
(report `attempts/A59-trump-residual/certs/m3_trump5_interior_NO.report.json`: PASS, depth 60, 39926 boxes, 2.149 s in Python).
3 atoms, 5 cores, 1 NO-families, budget 6, n = 11, s = 969271/250000.

* `check_m3_trump5_interior_NO` -- the checker PASSes (`native_decide` evaluation);
* `m3_trump5_interior_NO_no_family` -- every strict family of 11 closed unit squares in
  `[0, 969271/250000]²` whose designated owners contain the 5 cores has a
  non-owner that is `CaseExempt` (Lemma B-NO occupancy, `checkCaseI_no_family`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `m3_trump5_interior_NO` certificate (native_decide evaluation). -/
theorem check_m3_trump5_interior_NO : checkCaseI Data.m3_trump5_interior_NO = true := by
  native_decide

theorem m3_trump5_interior_NO_side : caseSide Data.m3_trump5_interior_NO = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `m3_trump5_interior_NO` kill, B-NO form**: every strict family of 11 closed unit
squares in `[0, 969271/250000]²` whose designated members contain the 5
certificate cores has a non-owner member inside the certificate's exempt set. -/
theorem m3_trump5_interior_NO_no_family {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSet (Data.m3_trump5_interior_NO.cores.get j) ⊆ Q (own j)) :
    ∃ i : Fin 11, (∀ j, own j ≠ i) ∧ CaseExempt Data.m3_trump5_interior_NO (Q i) := by
  rw [← m3_trump5_interior_NO_side] at hQ
  exact checkCaseI_no_family check_m3_trump5_interior_NO hQ own hown

end S11
end PackingCert
