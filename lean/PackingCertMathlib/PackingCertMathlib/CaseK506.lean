import PackingCertMathlib.CaseData506
import PackingCertMathlib.CaseBridge

/-!
# One case-LP certificate replayed end to end (A70, V.CASE pilot)

`attempts/A56-sparametric/certs/c2/k5_06.lo.json` — the k5_06 pin-set kill at
`s = 191/50`: 10 atoms, total mass `5150007/1000000 < budget 6`, five point-like
cores (`a ≈ 1/2 − 3·10⁻⁸`, `tm = 2⁻²⁵`) at the five pin slots, no NO-families;
depth 44 (the Python report's settings; report:
`attempts/A56-sparametric/certs/c2/k5_06.lo.report.json`, 8 402 boxes, PASS).

* `check_k5_06_lo` — the checker PASSes (`native_decide` evaluation);
* `k5_06_lo_kill` — **no strict family of 11 closed unit squares in
  `[0, 191/50]²` has designated owners containing the five cores** (composition
  of the PASS with `checkCaseI_kill`);
* `k5_06_lo_kill_packing` — the interior-disjoint (λ-dilated) form, composed
  with A68's `lemma_B`: no 11-packing at side `m = (191/50)/λ` realises the
  dilated core-containment hypothesis (H).
-/

namespace PackingCert
namespace S11

open Set CaseI

/-- The checker PASSes the k5_06.lo certificate (native_decide evaluation). -/
theorem check_k5_06_lo : checkCaseI Data.k5_06_lo = true := by
  native_decide

theorem k5_06_lo_side : caseSide Data.k5_06_lo = 191 / 50 := by
  change ((191 : Int) : ℝ) / ((50 : Int) : ℝ) = 191 / 50
  norm_num

/-- **The k5_06 pin-set kill, strict-family form**: no 11 pairwise-disjoint closed
unit squares in `[0, 191/50]²` can have designated members containing the five
certificate cores. -/
theorem k5_06_lo_kill {Q : Fin 11 → Set RP}
    (hQ : IsStrictFamily 11 ((191 : ℝ) / 50) Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSet (Data.k5_06_lo.cores.get j) ⊆ Q (own j)) :
    False := by
  rw [← k5_06_lo_side] at hQ
  exact checkCaseI_kill check_k5_06_lo rfl hQ own hown

/-- **The k5_06 pin-set kill, packing form** (composed with Lemma B's λ-dilation,
A68 `Dilation.lean`): no interior-disjoint 11-packing at side `m = (191/50)/λ`
realises the dilated core-containment hypothesis (H). -/
theorem k5_06_lo_kill_packing {m lam : ℝ} (hlam : 1 < lam)
    (hs : (191 : ℝ) / 50 = lam * m)
    {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 m fun i => (z i).set)
    (own : Fin 5 → Fin 11)
    (hH : ∀ j : Fin 5, coreSet (Data.k5_06_lo.cores.get j)
        ⊆ interior ((scaleC lam (z (own j))).set)) : False :=
  lemma_B hlam hs ht hP (fun j => coreSet (Data.k5_06_lo.cores.get j)) own
    (fun _Q hQ hI => k5_06_lo_kill hQ own
      (fun j => (hI j).trans interior_subset)) hH

end S11
end PackingCert
