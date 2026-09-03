import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `scale_T1.3e-1_landing` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_scale_T1.3e-1_landing.json`:
`T = 13/100`, `r_c = 1/625`, `r_θ = 21/10000`, `r_s = 0`.

`check_tube_scale_T1_3e_1_landing` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_scale_T1_3e_1_landing : checkTube Data.a22 Data.tube_scale_T1_3e_1_landing = true := by
  native_decide

end PackingCert.Rigid
