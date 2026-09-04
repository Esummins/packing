import PackingCertMathlib.RigidTubeKernel
namespace PackingCert.Rigid
variable (c : A22Cert) (tc : TubeCert)
theorem t_hv : (tubeStats c tc).hv = Array.ofFn (n := NV) fun i => hvMag tc (omegaHessT c tc) i.val := rfl
theorem t_e0 : (tubeStats c tc).e0 = eps0 c tc.a36 (radBox c.z0 c.r0) := rfl
theorem t_qvv2 : (tubeStats c tc).qvv = qvvT tc (omegaHessT c tc) := by
  delta tubeStats
  rfl
theorem t_qvv3 : (tubeStats c tc).qvv = qvvT tc (omegaHessT c tc) := by
  simp only [tubeStats]
theorem t_qvv : (tubeStats c tc).qvv = qvvT tc (omegaHessT c tc) := rfl
end PackingCert.Rigid
