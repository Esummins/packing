import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `slot_T1e-2_wide` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_slot_T1e-2_wide.json`:
`T = 1/100`, `r_c = 33/10000`, `r_θ = 33/10000`, `r_s = 0`.

`check_tube_slot_T1e_2_wide` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_slot_T1e_2_wide : checkTube Data.a22 Data.tube_slot_T1e_2_wide = true := by
  native_decide

end PackingCert.Rigid
