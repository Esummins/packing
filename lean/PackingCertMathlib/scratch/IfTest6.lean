import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic

open PackingCert.MeasureI

set_option maxHeartbeats 1000000 in
example (ctx : Ctx) (b : IBox) : ∃ r, clipI ctx b = r := by
  simp only [clipI, trig]
  split
  case isTrue h => trace_state; exact ⟨_, rfl⟩
  case isFalse h => exact ⟨_, rfl⟩
