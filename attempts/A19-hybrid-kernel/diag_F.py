"""A19 -- post-run diagnostic: on the FINAL row set of a run, what does F actually buy?
Solves the hybrid SDP with and without F on identical rows, reports both and the F structure."""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))

from features import FeatureMap
from hybrid import HybridSDP


def main(tag, s):
    st = np.load(os.path.join(HERE, "results", tag + "_state.npz"), allow_pickle=True)
    fm = FeatureMap(st["A"], st["w"], s)
    hs = HybridSDP(fm, None, r_mask=st["r_mask"].astype(bool))
    nd = hs.add_diag(st["diag_pts"])
    npr = 0
    if len(st["pair_x"]):
        PX, PY = st["pair_x"], st["pair_y"]
        if len(PX) > 2200:
            import sys as _s
            _s.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
            from oracle_pair import overlap_depth_many
            dep = overlap_depth_many(PX, PY)
            keep = np.argsort(-dep)[:2200]     # barely-disjoint (binding) pair rows first
            PX, PY = PX[keep], PY[keep]
        npr = hs.add_pairs(PX, PY)
    print(f"[{tag}] rows: {nd} diag, {npr} pair; k={hs.k}, n_forb={hs.n_forb}")
    r1 = hs.solve()
    print(f"[{tag}] hybrid (F on):  lam = {r1['lam']:.6f} ({r1['time']:.0f}s)")
    r0 = hs.solve(allow_F=False)
    print(f"[{tag}] F = 0:          lam = {r0['lam']:.6f} ({r0['time']:.0f}s)")
    print(f"[{tag}] F buys {r0['lam'] - r1['lam']:+.6f} on identical rows "
          f"(note: F=0 violates the pair-row margins by construction, so compare with care)")
    f = r1["f"]
    if len(f):
        Fd = np.asarray((hs.Bas @ f)).reshape(hs.k, hs.k)
        off = Fd[np.triu_indices(hs.k, 1)]
        print(f"[{tag}] F off-diag: min {off.min():+.4f} max {off.max():+.4f} "
              f"frac>1e-6 {np.mean(off > 1e-6):.3f} frac<-1e-6 {np.mean(off < -1e-6):.3f} "
              f"|F|_max {np.abs(off).max():.4f}")
    json.dump(dict(lam_hybrid=r1["lam"], lam_F0=r0["lam"]),
              open(os.path.join(HERE, "results", f"diagF_{tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]))
