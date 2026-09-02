import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic

open PackingCert.MeasureI
#check @if_pos
#check @ite_eq_left

set_option maxHeartbeats 1000000 in
example (ctx : Ctx) (b : IBox)
    (hsel : (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * (ctx.P4 + b.T1 * b.T1)
      ≤ (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * (ctx.P4 + b.T0 * b.T0)) :
    ∃ r, clipI ctx b = r := by
  rw [clipI]
  trace_state
  exact ⟨_, rfl⟩
