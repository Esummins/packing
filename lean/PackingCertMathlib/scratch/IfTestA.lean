import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic
open PackingCert.MeasureI
set_option maxHeartbeats 4000000 in
example (ctx : Ctx) (b : IBox) : clipI ctx b = clipI ctx b := by
  conv_lhs => simp only [clipI, trig]
  split_ifs with h1 h2
  · simp only [if_pos h1]
    trace_state
    sorry
  · sorry
  · sorry
