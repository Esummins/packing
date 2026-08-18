import PackingCert.MeasureInt
import PackingCert.MeasureIntData

/-!
# The slow target: the new lower bound `s(11) ≥ 3.80`

Build with `lake build PackingCertSlow` (NOT part of the default `lake build`; the theorem
evaluates ≈ 5.8 million boxes — about 9 min as a compiled executable, see
`lake exe measure_bench int_3_80 48`).

* `s11_ge_3_80 : checkMeasureI Data.cert_3_80 = true` — certs/measure_certificate_3.80.json
  (A07 LP measure, 1069 atoms, total mass 10.801639 < 11, s = 19/5), also PASSED by the
  independent Python verifier certs/verify_measure.py (A08).

Meaning (via the bridge lemma stated in PackingCert/MeasureInt.lean, not formalised): every
closed unit square inside `[0,19/5]²` has μ-mass ≥ 1 while μ has total mass < 11, so no 11
pairwise-disjoint closed unit squares fit in `[0,19/5]²`, i.e. `s(11) ≥ 3.80`.

(certs/measure_certificate_3.82.json — data in `PackingCert/MeasureIntData382.lean` — is
REJECTED by both checkers: `lake exe measure_bench int_3_82 48` → `ok=false` after 103 534
boxes; A08 finds 17 genuine holes with mass ≈ 0.988. No theorem for it.)
-/

namespace PackingCert.MeasureI

open Data

theorem s11_ge_3_80 : checkMeasureI cert_3_80 = true := by native_decide

end PackingCert.MeasureI
