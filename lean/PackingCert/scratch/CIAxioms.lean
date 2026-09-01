-- CI axiom audit (.github/workflows/lean.yml). Same theorems as scratch/Axioms.lean, minus its
-- deliberate must-fail `example`, which would make a plain `lake env lean` run exit non-zero.
import PackingCert.Kernel
import PackingCert.Main
import PackingCert.MeasureIntMain
import PackingCert.MeasureMain
#print axioms PackingCert.trump11_ok_kernel
#print axioms PackingCert.trump11_tight_ok_kernel
#print axioms PackingCert.trump11_ok
#print axioms PackingCert.MeasureI.a05_10pt_int_ok
#print axioms PackingCert.MeasureI.goebel26_int_ok
#print axioms PackingCert.Measure.s11_ge_37416
