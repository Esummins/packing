import PackingCertMathlib.RigidData22
import PackingCertMathlib.RigidData36

open PackingCert.Rigid PackingCert.Rigid.Data

-- quick diagnostics (interpreted)
#eval shapeOK a22
#eval centreResidual a22
#eval krawczykStats a22 a22.S a22.Y a22.rN
#eval krawczykStats a22 a22.S a22.Y a22.r0
#eval krawczykStats a22 a22.S2 a22.Y2 a22.rN
#eval validityMargin a22 a22.S (radBox a22.z0 a22.rN)
#eval lambdaResidual a22
#eval farkasBeta a22
#eval feasibleOK a22
#eval wallMargin a22 (radBox a22.z0 a22.r0)
#eval checkA22 a22
