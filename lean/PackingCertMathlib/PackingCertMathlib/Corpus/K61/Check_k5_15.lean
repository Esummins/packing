import PackingCertMathlib.Corpus.K61.Data_k5_15
import PackingCertMathlib.CaseBridge

/-!
# `k5_15` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A53-simple-strata/certs_wip/k5_15.json`
(report `attempts/A53-simple-strata/certs_wip/k5_15.report.json`: PASS, depth 56, 1592470 boxes, 34.986 s in Python).
33 atoms, 5 cores, 0 NO-families, budget 6, n = 11, s = 969271/250000.

* `check_k5_15` -- the checker PASSes (`native_decide` evaluation);
* `k5_15_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 5 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k5_15` certificate (native_decide evaluation). -/
theorem check_k5_15 : checkCaseI Data.k5_15 = true := by
  native_decide

theorem k5_15_side : caseSide Data.k5_15 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k5_15` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 5 certificate cores. -/
theorem k5_15_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSet (Data.k5_15.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k5_15_side] at hQ
  exact checkCaseI_kill check_k5_15 rfl hQ own hown

end S11
end PackingCert
