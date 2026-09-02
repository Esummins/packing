import PackingCertMathlib.Corpus.K61.Data_k5_06
import PackingCertMathlib.CaseBridge

/-!
# `k5_06` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A53-simple-strata/certs_wip/k5_06.json`
(report `attempts/A53-simple-strata/certs_wip/k5_06.report.json`: PASS, depth 56, 42768 boxes, 1.228 s in Python).
10 atoms, 5 cores, 0 NO-families, budget 6, n = 11, s = 969271/250000.

* `check_k5_06` -- the checker PASSes (`native_decide` evaluation);
* `k5_06_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 5 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k5_06` certificate (native_decide evaluation). -/
theorem check_k5_06 : checkCaseI Data.k5_06 = true := by
  native_decide

theorem k5_06_side : caseSide Data.k5_06 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k5_06` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 5 certificate cores. -/
theorem k5_06_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSet (Data.k5_06.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k5_06_side] at hQ
  exact checkCaseI_kill check_k5_06 rfl hQ own hown

end S11
end PackingCert
