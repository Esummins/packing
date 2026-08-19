"""A17 calibration (run FIRST): s = 3.80, M = M_LP from certs/measure_certificate_3.80.json.
Expected: pair oracle max = -1 exactly (LP-form kernel identity), diag oracle max = tau/m_min - 1
with m_min ~ 1.0300 (advisor's independent float spot check of the certificate margin)."""
import json, os, time
import numpy as np
from features import FeatureMap, load_atoms_cert, structured_placements
from oracle_pair import KernelEval, pair_oracle
from oracle_diag import diag_oracle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

t0 = time.time()
A, w, s = load_atoms_cert(os.path.join(ROOT, "certs", "measure_certificate_3.80.json"))
tau = w.sum()
print(f"3.80 certificate: {len(A)} atoms, tau = {tau:.6f}, s = {s}")
fm = FeatureMap(A, w, s)
M = fm.M_lp()
wv, U = np.linalg.eigh(M)
print(f"M_LP: min eig {wv.min():.2e} (PSD), max {wv.max():.3f}")
L = np.sqrt(np.maximum(wv, 0.0))[:, None] * U.T
ke = KernelEval(fm, L)
rng = np.random.default_rng(7)
sp = structured_placements(s)
rd = diag_oracle(ke, s, structP=sp, rng=rng, n_rand=60000, n_polish=60, log=print)
vd, xd = rd["best"]
print(f"DIAG: max K(x,x) = {vd:.6f}  => min coverage found = {tau/(vd+1):.6f} (advisor spot check: 1.0300)")
print(f"      => lambda_LP = 1 + maxK = {1+vd:.6f} (tau = {tau:.6f})")
rp = pair_oracle(ke, s, nodesP=sp, rng=rng, n_tangent=20000, n_polish=40, log=print)
vp, xp, yp = rp["best"]
print(f"PAIR: max K(x,y) over disjoint pairs = {vp:.9f} (must be -1 to float accuracy)")
res = dict(s=s, tau=float(tau), n_atoms=len(A), diag_max=float(vd), diag_x=list(map(float, xd)),
           min_cov=float(tau / (vd + 1)), pair_max=float(vp), pair_x=list(map(float, xp)),
           pair_y=list(map(float, yp)), lambda_lp=float(1 + vd), time=time.time() - t0)
json.dump(res, open(os.path.join(HERE, "results", "calibration_380.json"), "w"), indent=1)
print(f"saved results/calibration_380.json ({time.time()-t0:.0f}s)")
