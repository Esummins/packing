import PackingCert
open PackingCert.MeasureI
set_option maxRecDepth 100000
set_option maxHeartbeats 0
-- kernel decide on the tiny integer certificate (depth 18)
theorem goebel26_int_kernel : checkMeasureI Data.goebel26_int = true := by decide
#print axioms goebel26_int_kernel
#print axioms PackingCert.MeasureI.a05_10pt_int_ok
#print axioms PackingCert.Measure.s11_ge_37416
