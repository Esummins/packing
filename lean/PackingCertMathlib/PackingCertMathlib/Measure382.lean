import PackingCertMathlib.MeasureBridge
import PackingCertMathlib.Measure382Check

/-!
# `s(11) ≥ 3.82`, end to end (A64, depgraph nodes A.LB382 + A.F2)

The composition of the `native_decide` evaluation `check_3_82`
(`Measure382Check.lean`) with the measure bridge `checkMeasureI_no_packing`
(`MeasureBridge.lean`): checker PASS ⇒ every unit square in `[0, 191/50]²` has mass
≥ 1 ⇒ no 11-packing at any side `< 191/50`.  This is the END-TO-END theorem
`s_eleven_ge_382 : ∀ s, Fits 11 s → 191/50 ≤ s` — the `lb_382` axiom of
`TopLevel.lean`, discharged.  `#print axioms` shows exactly
`propext, Classical.choice, Quot.sound` plus the `native_decide` axiom
(`check_3_82._native.native_decide.ax_1_1`).
-/

namespace PackingCert
namespace S11

open MeasureI

/-- **Theorem 1, fully in Lean: `s(11) ≥ 3.82`** — every side admitting an 11-packing
is `≥ 191/50`. -/
theorem s_eleven_ge_382 : ∀ s : ℝ, Fits 11 s → (191 / 50 : ℝ) ≤ s := by
  intro s hs
  have h := checkMeasureI_no_packing check_3_82 s hs
  have h1 : Data.cert_3_82.sNum = 191 := rfl
  have h2 : Data.cert_3_82.sDen = 50 := rfl
  rw [h1, h2] at h
  norm_num at h
  exact h

end S11
end PackingCert
