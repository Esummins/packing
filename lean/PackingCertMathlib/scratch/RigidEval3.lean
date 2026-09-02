import PackingCertMathlib.RigidData22
import PackingCertMathlib.RigidData36

open PackingCert.Rigid PackingCert.Rigid.Data

-- A36 replay diagnostics (interpreted)
#eval checkA22 a22
#eval rows70OK a22
#eval a36All.map fun a => (a.name, pinsOK a22 a, omegaOK a, activityOK a22 a (radBox a22.z0 a22.r0))
#eval (a36Stats a22 a36_UNIVERSAL)
#eval checkA36 a22 a36_UNIVERSAL
#eval a36All.map fun a => (a.name, checkA36 a22 a)
