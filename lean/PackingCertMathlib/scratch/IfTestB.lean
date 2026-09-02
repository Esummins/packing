import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic
open PackingCert.MeasureI
set_option maxHeartbeats 4000000 in
set_option pp.explicit true in
set_option pp.maxSteps 100 in
example (ctx : Ctx) (b : IBox) : (clipI ctx b) = clipI ctx b := by
  conv_lhs => rw [clipI]
  trace_state
  rfl
