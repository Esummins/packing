import PackingCertMathlib.RigidData22
import PackingCertMathlib.RigidData36

open PackingCert.Rigid PackingCert.Rigid.Data

def bx0 := radBox a22.z0 a22.r0
def R := angRel a22
def K := knownFix a22 bx0

#eval (rng 11).map fun i => (kx K i, ky K i)
#eval (rng 11).map fun i => (rng 11).filter fun j => i < j && !(pairOK a22 R K bx0 i j)
#eval feasibleOK a22
#eval checkA22 a22
