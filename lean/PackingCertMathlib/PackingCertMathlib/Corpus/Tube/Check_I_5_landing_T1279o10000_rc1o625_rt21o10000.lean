import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `I_5_landing_T1279o10000_rc1o625_rt21o10000` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_I_5_landing_T1279o10000_rc1o625_rt21o10000.json`:
`T = 1279/10000`, `r_c = 1/625`, `r_θ = 21/10000`, `r_s = 0`.

`check_tube_I_5_landing_T1279o10000_rc1o625_rt21o10000` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_I_5_landing_T1279o10000_rc1o625_rt21o10000 : checkTube Data.a22 Data.tube_I_5_landing_T1279o10000_rc1o625_rt21o10000 = true := by
  native_decide

end PackingCert.Rigid
