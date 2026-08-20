"""A19 -- quantify the (ii)-verification burden of the hybrid class (notes H6):
fraction of random disjoint admissible pairs at s that are R-meeting (need verification),
vs the automatic rest. Uses the saved run state (r_mask + atoms)."""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))

from features import FeatureMap, random_placements
from oracle_pair import overlap_depth_many


def main(tag, s):
    st = np.load(os.path.join(HERE, "results", tag + "_state.npz"), allow_pickle=True)
    fm = FeatureMap(st["A"], st["w"], s)
    r_idx = np.nonzero(st["r_mask"])[0]
    rng = np.random.default_rng(0)
    N = 60000
    X = random_placements(s, N, rng, boundary_frac=0.0)
    Y = random_placements(s, N, rng, boundary_frac=0.0)
    dep = overlap_depth_many(X, Y)
    dis = dep < 0
    pat1 = fm.patterns(X); pat2 = fm.patterns(Y)
    m1 = np.asarray(pat1[:, r_idx].sum(axis=1)).ravel() > 0
    m2 = np.asarray(pat2[:, r_idx].sum(axis=1)).ravel() > 0
    need = dis & m1 & m2
    print(f"[{tag}] s={s}: {dis.sum()} of {N} random pairs disjoint; "
          f"R-meeting disjoint (need (ii) verification): {need.sum()} "
          f"= {100.0*need.sum()/max(dis.sum(),1):.2f}% of disjoint pairs")
    # centre-distance profile of the needing pairs
    c = s / 2
    r1 = np.hypot(X[:, 0] - c, X[:, 1] - c)
    r2 = np.hypot(Y[:, 0] - c, Y[:, 1] - c)
    rr = np.maximum(r1, r2)[need]
    if len(rr):
        print(f"   max centre-dist of needing pairs: {rr.max():.3f} "
              f"(bound: R-radius + 1/sqrt2)")
    return dict(frac_of_disjoint=float(need.sum()/max(dis.sum(),1)),
                n_disjoint=int(dis.sum()), n_need=int(need.sum()),
                max_centre_dist=float(rr.max()) if len(rr) else 0.0)


if __name__ == "__main__":
    out = {}
    for tag, s in (("h384", 3.84), ("h380", 3.80)):
        if os.path.exists(os.path.join(HERE, "results", tag + "_state.npz")):
            out[tag] = main(tag, s)
    json.dump(out, open(os.path.join(HERE, "results", "burden.json"), "w"), indent=1)
