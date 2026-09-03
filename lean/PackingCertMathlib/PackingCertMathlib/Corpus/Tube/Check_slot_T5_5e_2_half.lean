import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `slot_T5.5e-2_half` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_slot_T5.5e-2_half.json`:
`T = 11/200`, `r_c = 1/1250`, `r_θ = 21/20000`, `r_s = 0`.

`check_tube_slot_T5_5e_2_half` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_slot_T5_5e_2_half : checkTube Data.a22 Data.tube_slot_T5_5e_2_half = true := by
  native_decide

end PackingCert.Rigid
