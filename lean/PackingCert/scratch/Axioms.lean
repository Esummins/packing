import PackingCert
open PackingCert
#print axioms PackingCert.trump11_ok
#print axioms PackingCert.trump11_ok_kernel
#print axioms PackingCert.trump11_tight_ok_kernel
#print axioms PackingCert.Example.ex4_ok_decide
-- must FAIL:
example : checkPacking Data.trump11 = false := by decide
