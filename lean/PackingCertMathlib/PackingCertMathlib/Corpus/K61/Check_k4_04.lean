import PackingCertMathlib.Corpus.K61.Data_k4_04
import PackingCertMathlib.CaseBridge

/-!
# `k4_04` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A55-k4-sweep/certs/k4_04.json`
(report `attempts/A55-k4-sweep/certs/k4_04.report.json`: PASS, depth 60, 4582778 boxes, 146.403 s in Python).
205 atoms, 4 cores, 0 NO-families, budget 7, n = 11, s = 969271/250000.

* `check_k4_04` -- the checker PASSes (`native_decide` evaluation);
* `k4_04_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 4 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k4_04` certificate (native_decide evaluation). -/
theorem check_k4_04 : checkCaseI Data.k4_04 = true := by
  native_decide

theorem k4_04_side : caseSide Data.k4_04 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k4_04` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 4 certificate cores. -/
theorem k4_04_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 4 → Fin 11)
    (hown : ∀ j : Fin 4, coreSet (Data.k4_04.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k4_04_side] at hQ
  exact checkCaseI_kill check_k4_04 rfl hQ own hown

end S11
end PackingCert
