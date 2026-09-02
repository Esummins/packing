import PackingCertMathlib.Corpus.K61.Data_k6_23
import PackingCertMathlib.CaseBridge

/-!
# `k6_23` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A54-stragglers/certs/k6_23.json`
(report `attempts/A54-stragglers/certs/k6_23.report.json`: PASS, depth 56, 2449492 boxes, 43.936 s in Python).
501 atoms, 6 cores, 0 NO-families, budget 5, n = 11, s = 969271/250000.

* `check_k6_23` -- the checker PASSes (`native_decide` evaluation);
* `k6_23_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 6 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k6_23` certificate (native_decide evaluation). -/
theorem check_k6_23 : checkCaseI Data.k6_23 = true := by
  native_decide

theorem k6_23_side : caseSide Data.k6_23 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k6_23` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 6 certificate cores. -/
theorem k6_23_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 6 → Fin 11)
    (hown : ∀ j : Fin 6, coreSet (Data.k6_23.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k6_23_side] at hQ
  exact checkCaseI_kill check_k6_23 rfl hQ own hown

end S11
end PackingCert
