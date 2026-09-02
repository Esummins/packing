import PackingCertMathlib.RigidData22
import PackingCertMathlib.RigidData36

/-!
# The certificate replays (A79) — ISOLATED `native_decide` module

Kept in its own module (the `Measure382Check` pattern) so that the evaluation axiom
enters exactly here and every other module is cache-hit-only.

* `checkA22_a22` — the A22 Krawczyk certificate (`krawczyk_cert.json`): [G][K][K0][K~][V][E][B][F];
* `checkA36_universal` — the branch-free A36 basin certificate `G3_UNIVERSAL`;
* `checkA36_all17` — all 17 A36 certificates (the 16 variants + UNIVERSAL).
-/

namespace PackingCert.Rigid

open PackingCert.Rigid.Data

theorem checkA22_a22 : checkA22 a22 = true := by native_decide

theorem checkA36_universal : checkA36 a22 a36_UNIVERSAL = true := by native_decide

theorem checkA36_all17 : checkA36All a22 a36All = true := by native_decide

end PackingCert.Rigid
