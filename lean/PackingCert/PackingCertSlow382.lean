import PackingCert.MeasureInt
import PackingCert.MeasureIntData382

/-!
# Slow target: the lower bound `s(11) ≥ 3.82`

Build with `lake build PackingCertSlow382` (≈ 15 min; ~7.6 million boxes).
`s11_ge_3_82 : checkMeasureI Data.cert_3_82 = true` — certs/measure_certificate_3.82.json
(A07 LP measure certificate, 1769 atoms, total mass 5492737/500000 = 10.985474 < 11, s = 191/50),
also PASSED by the independent Python verifier certs/verify_measure.py (A08; 7 639 758 boxes, depth 43).
Meaning via the (unformalised) bridge lemma stated in PackingCert/MeasureInt.lean: s(11) ≥ 3.82.
-/

namespace PackingCert.MeasureI

open Data

theorem s11_ge_3_82 : checkMeasureI cert_3_82 = true := by native_decide

end PackingCert.MeasureI
