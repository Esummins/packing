import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic
open PackingCert.MeasureI
-- does the goal-condition from split_ifs match a Mathlib-elaborated statement via exact?
set_option maxHeartbeats 2000000 in
example (ctx : Ctx) (b : IBox)
    (hsel : (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * (ctx.P4 + b.T1 * b.T1)
      ≤ (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * (ctx.P4 + b.T0 * b.T0)) :
    clipI ctx b = clipI ctx b := by
  conv_lhs => simp only [clipI, trig]
  split_ifs with h1 h2
  · exact rfl
  · exact absurd hsel h1  -- if this works, h1's Prop defeq-unifies with hsel's
  · exact absurd hsel h1
