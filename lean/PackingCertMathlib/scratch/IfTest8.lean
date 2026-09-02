import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic

open PackingCert.MeasureI
set_option pp.numericTypes true in
set_option pp.explicit true in
example (ctx : Ctx) (b : IBox) : True := by
  have x := clipI ctx b
  trace_state
  trivial

-- compare elaborations of the selection condition
example (ctx : Ctx) (b : IBox)
    (h : (ctx.P4 - b.T0 * b.T0 + 2 * b.T0 * ctx.TROOT) * (ctx.P4 + b.T1 * b.T1)
      ≤ (ctx.P4 - b.T1 * b.T1 + 2 * b.T1 * ctx.TROOT) * (ctx.P4 + b.T0 * b.T0)) : True := by
  trivial
