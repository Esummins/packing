import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `slot_T6.2e-2_tiny` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_slot_T6.2e-2_tiny.json`:
`T = 31/500`, `r_c = 1/5000`, `r_θ = 1/5000`, `r_s = 0`.

`check_tube_slot_T6_2e_2_tiny` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_slot_T6_2e_2_tiny : checkTube Data.a22 Data.tube_slot_T6_2e_2_tiny = true := by
  native_decide

end PackingCert.Rigid
