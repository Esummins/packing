"""Generic feasibility check of a saved A20 state: is (g_orb, f, lam) a genuine class member
on the state's own rows? Reports dense-Z min eig, max diag/pair row residuals.
usage: python check_feas.py <tag> <s> <lam>"""
import os, sys
import numpy as np
import scipy.sparse as sp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "A19-hybrid-kernel"))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap
from block_sdp import BlockHybridSDP

def verify(hs, fm, g_orb, f, lam, tag=""):
    g_atom = g_orb[hs.oid]
    k = hs.k
    Z = np.zeros((k + 1, k + 1))
    Z[:k, :k] = np.diag(g_atom[hs.r_idx])
    if f is not None and len(f):
        Z[:k, :k] += np.asarray((hs.Bas @ f)).reshape(k, k)
    wR = fm.w[hs.r_idx]
    Z[k, :k] = wR; Z[:k, k] = wR
    N_at = np.setdiff1d(np.arange(fm.m), hs.r_idx)
    wN = fm.w[N_at]
    Z[k, k] = 1.0 - float(np.sum(wN ** 2 / g_atom[N_at]))
    emin = float(np.linalg.eigvalsh(Z).min())
    nd = len(hs.diag_meta)
    Gc = sp.csr_matrix((hs.dG_v, (hs.dG_r, hs.dG_c)), shape=(nd, hs.n_orb))
    m2 = np.array(hs.d_m2)
    lhs = Gc @ g_orb
    if hs.dF_r and f is not None and len(f):
        Fq = sp.csr_matrix((hs.dF_v, (hs.dF_r, hs.dF_c)), shape=(nd, hs.n_forb))
        lhs = lhs + Fq @ f
    dviol = float((lhs - m2 * lam).max())
    npair = len(hs.pair_meta)
    pviol = 0.0
    if npair and f is not None and len(f):
        Fp = sp.csr_matrix((hs.pF_v, (hs.pF_r, hs.pF_c)), shape=(npair, hs.n_forb))
        mm = np.array(hs.p_mm)
        pviol = float((Fp @ f + hs.delta_pair * mm).max())
    print(f"[{tag}] lam={lam:.6f} Zmin={emin:.3e} tail={Z[k,k]:.4f} "
          f"diag_viol={dviol:.3e} pair_viol={pviol:.3e} gNmin={g_atom[N_at].min():.3e}")
    return emin, dviol, pviol

if __name__ == "__main__":
    tag, s, lam = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    st = np.load(os.path.join(HERE, "results", tag + "_state.npz"), allow_pickle=True)
    fm = FeatureMap(st["A"], st["w"], s)
    hs = BlockHybridSDP(fm, None, r_mask=st["r_mask"].astype(bool))
    hs.add_diag(st["diag_pts"])
    if len(st["pair_x"]):
        hs.add_pairs(st["pair_x"], st["pair_y"])
    print(f"rows {len(hs.diag_meta)}d/{len(hs.pair_meta)}p k={hs.k}")
    verify(hs, fm, np.asarray(st["g_orb"], float), np.asarray(st["f"], float), lam, tag)
