import PackingCertMathlib.MeasureChecker
import PackingCertMathlib.MeasureData382

/-!
# The `native_decide` evaluation of the 3.82 measure certificate (A64)

Isolated in its own module so that the ≈ 30 min evaluation (5 837 883-box
branch-and-bound at depth 48 over `certs/measure_certificate_3.82.json`) is cached
independently of the composition theorem in `Measure382.lean`.  The same evaluation
also runs in the no-Mathlib project as `PackingCert.MeasureI.s11_ge_3_82`
(target `PackingCertSlow382`) on a byte-identical checker — see `lean/README.md`.
-/

namespace PackingCert
namespace S11

open MeasureI

/-- The checker accepts the 3.82 certificate (`native_decide` evaluation). -/
theorem check_3_82 : checkMeasureI Data.cert_3_82 = true := by native_decide

end S11
end PackingCert
