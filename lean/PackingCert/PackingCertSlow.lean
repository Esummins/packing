import PackingCert.MeasureInt
import PackingCert.MeasureIntData
import PackingCert.MeasureIntData382

/-!
# The slow target: the new lower bounds `s(11) ≥ 3.80` and `s(11) ≥ 3.82`

Build with `lake build PackingCertSlow` (NOT part of the default `lake build`; each theorem
evaluates ≈ 6–15 million boxes, several minutes each).

* `s11_ge_3_80 : checkMeasureI Data.cert_3_80 = true` — certs/measure_certificate_3.80.json
  (A07 LP measure, 1069 atoms, total mass 10.801639 < 11, s = 19/5).
* `s11_ge_3_82 : checkMeasureI Data.cert_3_82 = true` — certs/measure_certificate_3.82.json
  (1793 atoms, total mass 10.984680 < 11, s = 191/50).

Meaning (via the bridge lemma stated in PackingCert/MeasureInt.lean, not formalised): every
closed unit square inside `[0,s]²` has μ-mass ≥ 1 while μ has total mass < 11, so no 11
pairwise-disjoint closed unit squares fit in `[0,s]²`, i.e. `s(11) ≥ s`.
-/

namespace PackingCert.MeasureI

open Data

theorem s11_ge_3_80 : checkMeasureI cert_3_80 = true := by native_decide

theorem s11_ge_3_82 : checkMeasureI cert_3_82 = true := by native_decide

end PackingCert.MeasureI
