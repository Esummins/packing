import PackingCertMathlib.Corpus.THMU.Data_u_reinsert_02
import PackingCertMathlib.CaseBridge

/-!
# `u_reinsert_02` replayed in Lean (A78 T5, corpus THMU)

Certificate `attempts/A65-low-k-closure/certs/u_reinsert_02.json`
(report `attempts/A65-low-k-closure/certs/u_reinsert_02.report.json`: PASS, depth 60, 462 boxes, 0.036 s in Python).
0 atoms, 10 cores, 1 NO-families, budget 1, n = 11, s = 3877083591023/1000000000000.

* `check_u_reinsert_02` -- the checker PASSes (`native_decide` evaluation);
* `u_reinsert_02_no_family` -- every strict family of 11 closed unit squares in
  `[0, 3877083591023/1000000000000]²` whose designated owners contain the 10 cores has a
  non-owner that is `CaseExempt` (Lemma B-NO occupancy, `checkCaseI_no_family`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `u_reinsert_02` certificate (native_decide evaluation). -/
theorem check_u_reinsert_02 : checkCaseI Data.u_reinsert_02 = true := by
  native_decide

theorem u_reinsert_02_side : caseSide Data.u_reinsert_02 = 3877083591023 / 1000000000000 := by
  change ((3877083591023 : Int) : ℝ) / ((1000000000000 : Int) : ℝ) = 3877083591023 / 1000000000000
  norm_num

/-- **The `u_reinsert_02` kill, B-NO form**: every strict family of 11 closed unit
squares in `[0, 3877083591023/1000000000000]²` whose designated members contain the 10
certificate cores has a non-owner member inside the certificate's exempt set. -/
theorem u_reinsert_02_no_family {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((3877083591023 : ℝ) / 1000000000000) Q)
    (own : Fin 10 → Fin 11)
    (hown : ∀ j : Fin 10, coreSet (Data.u_reinsert_02.cores.get j) ⊆ Q (own j)) :
    ∃ i : Fin 11, (∀ j, own j ≠ i) ∧ CaseExempt Data.u_reinsert_02 (Q i) := by
  rw [← u_reinsert_02_side] at hQ
  exact checkCaseI_no_family check_u_reinsert_02 hQ own hown

end S11
end PackingCert
