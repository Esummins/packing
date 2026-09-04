import PackingCertMathlib.RigidTubeData
import PackingCertMathlib.RigidData22

/-!
# The contraction-tube replays (A86 T1) — ISOLATED `native_decide` module

Kept in its own module (the `Measure382Check` / `RigidityCheck` pattern) so
that the evaluation axiom enters exactly here and every other module of the
default target is cache-hit-only.  The three LOAD-BEARING tubes only; the
remaining certificates are replayed one module each in the separate
`PackingCertCorpus` library (`PackingCertMathlib.Corpus.Tube`).

* `checkTube_slot_landing` — `certs/tube_slot_T4.5e-2_landing.json` (`T = 9/200`);
* `checkTube_k4_08_landing` — `certs/tube_k4_08_landing_T28o625_rc1o625_rt21o10000.json` (`T = 28/625`);
* `checkTube_scale_landing` — `certs/tube_I_none_landing_T1279o10000_rc1o625_rt21o10000.json` (`T = 1279/10000`);
-/

namespace PackingCert.Rigid

open PackingCert.Rigid.Data

theorem checkTube_slot_landing : checkTube a22 tube_slot_T4_5e_2_landing = true := by native_decide

theorem checkTube_k4_08_landing : checkTube a22 tube_k4_08_landing_T28o625_rc1o625_rt21o10000 = true := by native_decide

theorem checkTube_scale_landing : checkTube a22 tube_I_none_landing_T1279o10000_rc1o625_rt21o10000 = true := by native_decide

end PackingCert.Rigid
