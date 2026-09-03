import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `slot_T5.71e-2_window` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_slot_T5.71e-2_window.json`:
`T = 571/10000`, `r_c = 13/20000`, `r_θ = 13/20000`, `r_s = 0`.

`check_tube_slot_T5_71e_2_window` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_slot_T5_71e_2_window : checkTube Data.a22 Data.tube_slot_T5_71e_2_window = true := by
  native_decide

end PackingCert.Rigid
