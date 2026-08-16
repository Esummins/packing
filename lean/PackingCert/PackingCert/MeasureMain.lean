import PackingCert.MeasureExample

/-!
# The measure-certificate theorem for the prototype example

`checkMeasure (g26 18) = true`: Göbel's perturbed 4-point measure certificate,
i.e. no 5 pairwise-disjoint closed unit squares fit in `[0, 2.6]²`, modulo the
(unformalised) bridge lemma for `checkMeasure`.
-/

namespace PackingCert.Measure

open Example

theorem s5_gt_26 : checkMeasure (g26 18) = true := by native_decide

end PackingCert.Measure
