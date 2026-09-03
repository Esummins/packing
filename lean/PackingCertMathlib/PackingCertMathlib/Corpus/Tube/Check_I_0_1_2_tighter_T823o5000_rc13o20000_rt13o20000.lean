import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `I_0_1_2_tighter_T823o5000_rc13o20000_rt13o20000` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_I_0_1_2_tighter_T823o5000_rc13o20000_rt13o20000.json`:
`T = 823/5000`, `r_c = 13/20000`, `r_θ = 13/20000`, `r_s = 0`.

`check_tube_I_0_1_2_tighter_T823o5000_rc13o20000_rt13o20000` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_I_0_1_2_tighter_T823o5000_rc13o20000_rt13o20000 : checkTube Data.a22 Data.tube_I_0_1_2_tighter_T823o5000_rc13o20000_rt13o20000 = true := by
  native_decide

end PackingCert.Rigid
