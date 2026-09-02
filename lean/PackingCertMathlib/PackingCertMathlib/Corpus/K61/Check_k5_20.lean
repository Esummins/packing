import PackingCertMathlib.Corpus.K61.Data_k5_20
import PackingCertMathlib.CaseBridge

/-!
# `k5_20` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A53-simple-strata/certs_wip/k5_20.json`
(report `attempts/A53-simple-strata/certs_wip/k5_20.report.json`: PASS, depth 56, 192678 boxes, 5.006 s in Python).
10 atoms, 5 cores, 0 NO-families, budget 6, n = 11, s = 969271/250000.

* `check_k5_20` -- the checker PASSes (`native_decide` evaluation);
* `k5_20_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 5 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k5_20` certificate (native_decide evaluation). -/
theorem check_k5_20 : checkCaseI Data.k5_20 = true := by
  native_decide

theorem k5_20_side : caseSide Data.k5_20 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k5_20` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 5 certificate cores. -/
theorem k5_20_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSet (Data.k5_20.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k5_20_side] at hQ
  exact checkCaseI_kill check_k5_20 rfl hQ own hown

end S11
end PackingCert
