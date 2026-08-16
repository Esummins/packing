import PackingCert.MeasureExample
import PackingCert.MeasureData

/-!
# Measure-certificate theorems

* `s5_gt_26`      : the perturbed Göbel 4-point measure at `s = 2.6`, i.e. no 5 pairwise-disjoint
                    closed unit squares fit in `[0, 2.6]²`.
* `s11_ge_37416`  : A05's 10-point unavoidable set (integral measure, total 10 < 11) at
                    `s = 1870797/500000 = 3.741594`, i.e. no 11 pairwise-disjoint closed unit
                    squares fit in `[0, 3.741594]²`; hence `s(11) ≥ 3.741594`.
                    (Weaker than Stromquist's 3.7889, but a fully machine-checked bound.)

Both modulo the (unformalised) bridge lemma for `checkMeasure` — see
attempts/A06-lean-setup/notes.md §7.  Only `native_decide` works here (kernel `decide`
gets stuck on `Rat` normalisation).
-/

namespace PackingCert.Measure

open Example Data

theorem s5_gt_26 : checkMeasure (g26 18) = true := by native_decide

theorem s11_ge_37416 : checkMeasure a05_10pt = true := by native_decide

theorem a05_10pt_side : a05_10pt.side = (1870797 : Rat) / 500000 ∧ a05_10pt.n = 11 := by
  native_decide

end PackingCert.Measure
