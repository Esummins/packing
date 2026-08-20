"""A18 -- post-hoc cross-check of the r384 kernel against A17's hard-cell inventory:
evaluate K_u*(x,x) on (a) A17's 8k stored diagonal row placements (k384_state.npz),
(b) A17's final-attack argmax (the continuum min-coverage cell), (c) a full-strength
low_coverage_placements scan (A17 covscan, dth 0.25 / cstep 0.005 / 250 polishes),
each polished under the two-measure kernel.  Reports the honest sup over everything,
for both u = u* and u = 1 (calibration).
"""
import os, sys, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap, load_atoms_a07_384
from oracle_diag import low_coverage_placements, polish_diag
from two_measure import TwoMeasureKernel

A, w, s = load_atoms_a07_384()
fm = FeatureMap(A, w, s)
tau = float(w.sum())
ke = TwoMeasureKernel(fm)
ke.theta_orb = np.load(os.path.join(HERE, "results", "r384_theta.npy"))

st = np.load(os.path.join(HERE, "..", "A17-kernel-root", "results", "k384_state.npz"),
             allow_pickle=True)
dp = st["diag_pts"]
print(f"A17 diag rows: {len(dp)}")
x17 = np.array([1.6034, 1.9897, math.radians(33.02)])   # A17 final-attack argmax
lowP, lowcov = low_coverage_placements(fm, s, dth_deg=0.25, cstep=0.005, n_polish=250)
print(f"covscan full strength: exact min coverage {lowcov.min():.6f}")

for name, th in (("u=1", np.zeros_like(ke.theta_orb)), ("u*", ke.theta_orb.copy())):
    ke.theta_orb = th
    pools = np.vstack([dp, x17[None], lowP])
    kv = ke.kdiag(pools)
    order = np.argsort(-kv)[:60]
    best = (kv[order[0]], pools[order[0]])
    for t in order[:40]:
        v, xb = polish_diag(ke, s, pools[t])
        if v > best[0]:
            best = (v, xb)
    lam = 1.0 + best[0]
    xb = best[1]
    print(f"{name}: sup K over A17 inventory (polished) = {best[0]:.6f} -> lambda = {lam:.6f} "
          f"at ({xb[0]:.4f},{xb[1]:.4f},{math.degrees(xb[2]):.2f}deg)")
    if name == "u=1":
        print(f"   (identity check: min m over inventory = {tau/lam:.6f}; "
              f"A17 continuum m_min = 0.968742 -> lambda(u=1) >= {tau/0.968742:.6f})")
json.dump(dict(note="see stdout log crosscheck_384.log"), open(os.devnull, "w"))
