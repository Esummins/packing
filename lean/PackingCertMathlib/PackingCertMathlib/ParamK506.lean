import PackingCertMathlib.ParamData506
import PackingCertMathlib.ParamBridge

/-!
# One parametric (window) certificate replayed end to end (A75, V.PARAM pilot)

`attempts/A56-sparametric/certs/k5_06.param.json` — the k5_06 pin-set kill over the
WHOLE window `[191/50, 969271/250000]`: 10 affine atoms (gap anchoring), total mass
`5150007/1000000 < budget 6`, five point-like cores at the five pin slots (three
BL-anchored, two BR-anchored: `bkx = 1`), no NO-families; depth 56, `--split 3`,
`tscale 2`, `sscale 8` (the Python report's settings:
`attempts/A56-sparametric/certs/k5_06.param.report.json`, 293 854 boxes, 421 s-cells,
PASS in 6.4 s).  The Lean replay uses the `--no-float-prepass` oracle `pickAll`.

* `check_k5_06_param` — the checker PASSes (`native_decide` evaluation);
* `k5_06_param_kill` — **for EVERY real side `s ∈ [191/50, 969271/250000]`, no strict
  family of 11 closed unit squares in `[0,s]²` has designated owners containing the
  five cores `Kⱼ(s)`** (composition with `checkParamI_kill`);
* `k5_06_param_kill_packing` — the interior-disjoint (λ-dilated) form via Lemma B.
-/

namespace PackingCert
namespace S11

open Set ParamI

/-- The checker PASSes the k5_06 parametric certificate (native_decide evaluation). -/
theorem check_k5_06_param : checkParamI Data.k5_06_param 2 8 3 pickAll = true := by
  native_decide

theorem k5_06_param_lo : paramLo Data.k5_06_param = 191 / 50 := by
  change ((955000 : Int) : ℝ) / ((250000 : Int) : ℝ) = 191 / 50
  norm_num

theorem k5_06_param_hi : paramHi Data.k5_06_param = 969271 / 250000 := by
  change ((969271 : Int) : ℝ) / ((250000 : Int) : ℝ) = 969271 / 250000
  norm_num

/-- **The k5_06 window kill, strict-family form**: at every side of the window. -/
theorem k5_06_param_kill {s : ℝ} (hlo : (191 : ℝ) / 50 ≤ s) (hhi : s ≤ 969271 / 250000)
    {Q : Fin 11 → Set RP} (hQ : IsStrictFamily 11 s Q)
    (own : Fin 5 → Fin 11)
    (hown : ∀ j : Fin 5, coreSetP (Data.k5_06_param.cores.get j) s ⊆ Q (own j)) :
    False := by
  rw [← k5_06_param_lo] at hlo
  rw [← k5_06_param_hi] at hhi
  exact checkParamI_kill check_k5_06_param hlo hhi hQ own hown

/-- **The k5_06 window kill, packing form** (Lemma B's λ-dilation at any side
`λ·m` of the window). -/
theorem k5_06_param_kill_packing {m lam : ℝ} (hlam : 1 < lam)
    (hlo : (191 : ℝ) / 50 ≤ lam * m) (hhi : lam * m ≤ 969271 / 250000)
    {z : Fin 11 → PSq} (ht : ∀ i, (z i).t ∈ Icc (0 : ℝ) 1)
    (hP : IsPacking 11 m fun i => (z i).set)
    (own : Fin 5 → Fin 11)
    (hH : ∀ j : Fin 5, coreSetP (Data.k5_06_param.cores.get j) (lam * m)
        ⊆ interior ((scaleC lam (z (own j))).set)) : False :=
  lemma_B hlam rfl ht hP (fun j => coreSetP (Data.k5_06_param.cores.get j) (lam * m)) own
    (fun _Q hQ hI => k5_06_param_kill hlo hhi hQ own
      (fun j => (hI j).trans interior_subset)) hH

end S11
end PackingCert
