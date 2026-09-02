import PackingCertMathlib.MeasureChecker
import Mathlib.Tactic
open PackingCert.MeasureI
set_option maxHeartbeats 4000000 in
example (ctx : Ctx) (b : IBox) (P : Option IBox → Prop) (hP : ∀ r, P r) : P (clipI ctx b) := by
  rw [clipI]
  split
  next cn0 sn0 dn0 heq =>
    split
    next cn1 sn1 dn1 heq1 =>
      split
      next wn wd heq2 =>
        trace_state
        split
        · exact hP _
        · exact hP _
