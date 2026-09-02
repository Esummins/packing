import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic

open PackingCert.MeasureI

set_option maxHeartbeats 1000000 in
example (ctx : Ctx) (b : IBox)
    (hsel : (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * (ctx.P4 + b.T1 * b.T1)
      ≤ (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * (ctx.P4 + b.T0 * b.T0)) :
    ∃ r, clipI ctx b = r := by
  simp only [clipI, trig, if_pos hsel]
  trace_state
  exact ⟨_, rfl⟩
