import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `slot_T4.2e-2_landing_rt2.3e-3` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_slot_T4.2e-2_landing_rt2.3e-3.json`:
`T = 21/500`, `r_c = 1/625`, `r_θ = 23/10000`, `r_s = 0`.

`check_tube_slot_T4_2e_2_landing_rt2_3e_3` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_slot_T4_2e_2_landing_rt2_3e_3 : checkTube Data.a22 Data.tube_slot_T4_2e_2_landing_rt2_3e_3 = true := by
  native_decide

end PackingCert.Rigid
