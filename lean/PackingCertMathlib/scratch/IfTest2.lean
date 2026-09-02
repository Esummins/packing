import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic

open PackingCert.MeasureI

example (ctx : Ctx) (b : IBox) : ∃ r, clipI ctx b = r := by
  simp only [clipI, trig]
  trace_state
  exact ⟨_, rfl⟩
