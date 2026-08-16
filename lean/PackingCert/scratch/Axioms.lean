import PackingCert
open PackingCert
#print axioms PackingCert.trump11_ok
#print axioms PackingCert.trump11_ok_kernel
#print axioms PackingCert.trump11_tight_ok_kernel
#print axioms PackingCert.Example.ex4_ok_decide
#print axioms PackingCert.Measure.s5_gt_26
#print axioms PackingCert.Measure.s11_ge_37416
-- must FAIL:
example : checkPacking Data.trump11 = false := by decide
