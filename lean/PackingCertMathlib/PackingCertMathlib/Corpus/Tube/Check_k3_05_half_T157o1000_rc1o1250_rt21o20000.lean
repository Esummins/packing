import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `k3_05_half_T157o1000_rc1o1250_rt21o20000` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_k3_05_half_T157o1000_rc1o1250_rt21o20000.json`:
`T = 157/1000`, `r_c = 1/1250`, `r_θ = 21/20000`, `r_s = 0`.

`check_tube_k3_05_half_T157o1000_rc1o1250_rt21o20000` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_k3_05_half_T157o1000_rc1o1250_rt21o20000 : checkTube Data.a22 Data.tube_k3_05_half_T157o1000_rc1o1250_rt21o20000 = true := by
  native_decide

end PackingCert.Rigid
