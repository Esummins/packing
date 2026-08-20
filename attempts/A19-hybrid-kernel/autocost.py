"""A19 -- coarsening cost curve: automatic-class (two-measure) lambda at 3.84 vs atom count,
via A18's convex GP + oracle attack loop (cheap, no SDP)."""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))

from features import FeatureMap, load_atoms_a07_384, random_placements, structured_placements
from oracle_diag import boundary_sweep
from full_sdp import coarsen_atoms
from two_measure import TwoMeasureKernel, attack
import scipy.sparse as sp


def gp_with_attack(fm, s, iters=5, n_rand=25000, log=print):
    rng = np.random.default_rng(3)
    ke = TwoMeasureKernel(fm)
    pts = [structured_placements(s), random_placements(s, 5000, rng),
           boundary_sweep(s, n_theta=91, step_c=0.04)]
    keys = set()
    rows = []
    pat_blocks = []

    def add(P):
        P = np.atleast_2d(P)
        pat = fm.patterns(P)
        keep = []
        for i in range(len(P)):
            nz = pat.indices[pat.indptr[i]:pat.indptr[i + 1]]
            if len(nz) == 0:
                continue
            k = fm.canon_key(nz)
            if k in keys:
                continue
            keys.add(k)
            keep.append(i)
        if keep:
            pat_blocks.append(pat[keep])
        return len(keep)

    for P in pts:
        add(P)
    lam = None
    for it in range(iters):
        pat = sp.vstack(pat_blocks, format="csr")
        lam_rows = ke.optimize(pat, log=lambda *a: None)
        rd = attack(ke, fm, s, rng, structP=None, n_rand=n_rand, n_polish=40,
                    bnd_theta=121, bnd_step=0.03, with_ratio=True, dth_deg=0.5, cstep=0.01,
                    log=lambda *a: None)
        vb, xb = rd["best"]
        lam_att = 1.0 + vb
        nadd = add(np.array([x for v, x in rd["cands"][:250]]))
        log(f"    it {it}: lam_rows {lam_rows:.4f} attack {lam_att:.4f} (+{nadd} rows)")
        lam = lam_att
        if lam_att - lam_rows <= 1e-7 and nadd == 0:
            break
    return lam


def main():
    s = 3.84
    A0, w0, _ = load_atoms_a07_384()
    out = {}
    for r_merge in (0.02, 0.035, 0.05, 0.08):
        A, w = coarsen_atoms(A0, w0, s, r_merge)
        fm = FeatureMap(A, w, s)
        t0 = time.time()
        lam = gp_with_attack(fm, s)
        out[r_merge] = dict(m=len(A), lam=lam, t=time.time() - t0)
        print(f"r_merge {r_merge}: m = {len(A)}, lambda_auto = {lam:.4f} ({time.time()-t0:.0f}s)"
              f"   [full-set reference 11.179]")
    json.dump(out, open(os.path.join(HERE, "results", "autocost.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
