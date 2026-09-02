import PackingCertMathlib.Corpus.K61.Data_k6_07
import PackingCertMathlib.CaseBridge

/-!
# `k6_07` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A53-simple-strata/certs_wip/k6_07.json`
(report `attempts/A53-simple-strata/certs_wip/k6_07.report.json`: PASS, depth 56, 454286 boxes, 11.895 s in Python).
11 atoms, 6 cores, 0 NO-families, budget 5, n = 11, s = 969271/250000.

* `check_k6_07` -- the checker PASSes (`native_decide` evaluation);
* `k6_07_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 6 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k6_07` certificate (native_decide evaluation). -/
theorem check_k6_07 : checkCaseI Data.k6_07 = true := by
  native_decide

theorem k6_07_side : caseSide Data.k6_07 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k6_07` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 6 certificate cores. -/
theorem k6_07_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 6 → Fin 11)
    (hown : ∀ j : Fin 6, coreSet (Data.k6_07.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k6_07_side] at hQ
  exact checkCaseI_kill check_k6_07 rfl hQ own hown

end S11
end PackingCert
