import PackingCert.MeasureInt
import PackingCert.MeasureIntData381

/-!
# Slow target: the lower bound `s(11) ≥ 3.81`

Build with `lake build PackingCertSlow381` (≈ 10 min; ~5.1 million boxes).
`s11_ge_3_81 : checkMeasureI Data.cert_3_81 = true` — certs/measure_certificate_3.81.json
(A07 LP measure certificate, total mass 27463/2500 = 10.9852 < 11, s = 381/100), also PASSED by
the independent Python verifier certs/verify_measure.py (A08; 5 116 216 boxes, max depth 42).
Meaning via the (unformalised) bridge lemma stated in PackingCert/MeasureInt.lean: s(11) ≥ 3.81.
-/

namespace PackingCert.MeasureI

open Data

theorem s11_ge_3_81 : checkMeasureI cert_3_81 = true := by native_decide

end PackingCert.MeasureI
