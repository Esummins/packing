import PackingCertMathlib.Corpus.K61.Data_k3_00
import PackingCertMathlib.CaseBridge

/-!
# `k3_00` replayed in Lean (A78 T5, corpus K61)

Certificate `attempts/A55-k4-sweep/k3_ext/certs/k3_00.json`
(report `attempts/A55-k4-sweep/k3_ext/certs/k3_00.report.json`: PASS, depth 56, 2817596 boxes, 64.947 s in Python).
579 atoms, 3 cores, 0 NO-families, budget 8, n = 11, s = 969271/250000.

* `check_k3_00` -- the checker PASSes (`native_decide` evaluation);
* `k3_00_kill` -- no strict family of 11 closed unit squares in `[0, 969271/250000]²`
  has designated owners containing the 3 cores (`checkCaseI_kill`).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the `k3_00` certificate (native_decide evaluation). -/
theorem check_k3_00 : checkCaseI Data.k3_00 = true := by
  native_decide

theorem k3_00_side : caseSide Data.k3_00 = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The `k3_00` pin-set kill, strict-family form**: no 11 pairwise-disjoint
closed unit squares in `[0, 969271/250000]²` can have designated members
containing the 3 certificate cores. -/
theorem k3_00_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((969271 : ℝ) / 250000) Q)
    (own : Fin 3 → Fin 11)
    (hown : ∀ j : Fin 3, coreSet (Data.k3_00.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k3_00_side] at hQ
  exact checkCaseI_kill check_k3_00 rfl hQ own hown

end S11
end PackingCert
