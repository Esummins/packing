import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# `k3_05_tiny_T112o625_rc1o5000_rt1o5000` replayed in Lean (A86 T1, corpus Tube)

Certificate `certs/tube_k3_05_tiny_T112o625_rc1o5000_rt1o5000.json`:
`T = 112/625`, `r_c = 1/5000`, `r_θ = 1/5000`, `r_s = 0`.

`check_tube_k3_05_tiny_T112o625_rc1o5000_rt1o5000` — `checkTube` accepts it against A22's Krawczyk
certificate (`native_decide` evaluation).
-/

namespace PackingCert.Rigid

theorem check_tube_k3_05_tiny_T112o625_rc1o5000_rt1o5000 : checkTube Data.a22 Data.tube_k3_05_tiny_T112o625_rc1o5000_rt1o5000 = true := by
  native_decide

end PackingCert.Rigid
