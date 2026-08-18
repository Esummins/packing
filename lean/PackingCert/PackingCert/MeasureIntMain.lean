import PackingCert.MeasureInt
import PackingCert.MeasureIntDataA05
import PackingCert.MeasureIntDataGoebel

/-!
# Integer measure-checker theorems (fast ones; the big certificates live in `PackingCertSlow`)

* `a05_10pt_int_ok` : A05's 10-point unavoidable set at s = 1870797/500000 = 3.741594
  (571k boxes, ≈ 10 s) — the same certificate as `Measure.s11_ge_37416`, checked by the
  all-integer checker: `s(11) ≥ 3.741594`.
* `goebel26_int_ok` : perturbed Göbel set at s = 2.6 (`s(5) > 2.6`), by `native_decide`
  and by kernel `decide` (proof of concept that the integer checker is kernel-reducible).
-/

namespace PackingCert.MeasureI

open Data

theorem a05_10pt_int_ok : checkMeasureI a05_10pt_int = true := by native_decide

theorem goebel26_int_ok : checkMeasureI goebel26_int = true := by native_decide

end PackingCert.MeasureI
