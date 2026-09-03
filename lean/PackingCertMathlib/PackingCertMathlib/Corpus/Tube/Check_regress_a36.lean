import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `regress_a36` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_regress_a36.json`:
`T = 0`, `r_c = 3689/1000000`, `r_θ = 3689/1000000`, `r_s = 3689/1000000`.

`check_tube_regress_a36` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_regress_a36 : checkTube Data.a22 Data.tube_regress_a36 = true := by
  native_decide

end PackingCert.Rigid
