"""Is the block-form h380 hybrid value 10.3449 a genuine class member on those rows?
Re-solve, then verify feasibility EXACTLY from the returned (g, f): dense Z PSD, diag rows,
pair rows. Also re-solve with tightened Clarabel tolerances and with SCS for cross-check."""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap
from block_sdp import BlockHybridSDP
from validate_a20 import load_rows
import scipy.sparse as sp

st = np.load(os.path.join(HERE, "..", "A19-hybrid-kernel", "results", "h380_state.npz"), allow_pickle=True)
fm = FeatureMap(st["A"], st["w"], 3.80)
hs = BlockHybridSDP(fm, None, r_mask=st["r_mask"].astype(bool))
nd, npr = load_rows("h380", hs)
print(f"rows {nd} diag {npr} pair, k={hs.k}")

def verify(sol, tag):
    g_atom = sol["g_orb"][hs.oid]
    f = sol["f"]; lam = sol["lam"]
    k = hs.k
    # dense Z
    Z = np.zeros((k+1, k+1))
    Z[:k, :k] = np.diag(g_atom[hs.r_idx])
    if len(f):
        Z[:k, :k] += np.asarray((hs.Bas @ f)).reshape(k, k)
    wR = fm.w[hs.r_idx]
    Z[k, :k] = wR; Z[:k, k] = wR
    N_at = np.setdiff1d(np.arange(fm.m), hs.r_idx)
    wN = fm.w[N_at]
    Z[k, k] = 1.0 - float(np.sum(wN**2 / g_atom[N_at]))
    emin = np.linalg.eigvalsh(Z).min()
    # rows
    nd = len(hs.diag_meta)
    Gc = sp.csr_matrix((hs.dG_v, (hs.dG_r, hs.dG_c)), shape=(nd, hs.n_orb))
    m2 = np.array(hs.d_m2)
    lhs = Gc @ sol["g_orb"]
    if hs.dF_r and len(f):
        Fq = sp.csr_matrix((hs.dF_v, (hs.dF_r, hs.dF_c)), shape=(nd, hs.n_forb))
        lhs = lhs + Fq @ f
    dviol = (lhs - m2*lam).max()
    npair = len(hs.pair_meta)
    if npair and len(f):
        Fp = sp.csr_matrix((hs.pF_v, (hs.pF_r, hs.pF_c)), shape=(npair, hs.n_forb))
        mm = np.array(hs.p_mm)
        pviol = (Fp @ f + hs.delta_pair*mm).max()
    else:
        pviol = 0.0
    print(f"[{tag}] lam={lam:.6f} Zmin_eig={emin:.3e} tail={Z[k,k]:.4f} "
          f"diag_viol={dviol:.3e} pair_viol={pviol:.3e} gN_min={g_atom[N_at].min():.3e}")
    return emin, dviol, pviol

r = hs.solve()
verify(r, "clarabel-default")
r2 = hs.solve(solver="SCS")
verify(r2, "scs-2e-6")
