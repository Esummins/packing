"""A19 -- sizing + Clarabel timing test at 3.84: coarsen atoms, define R by binding-placement
coverage, build the full SDP with a moderate row set, time one solve."""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

from features import FeatureMap, load_atoms_a07_384, random_placements, structured_placements
from oracle_pair import overlap_depth_many, tangent_pairs
from full_sdp import FullHybridSDP, coarsen_atoms
from hybrid import enrich_atoms


def binding_placements_384(s=3.84):
    """mid-tilt binding inventory: A18 r384 binding cells + A12 quarter-pinwheel images
    (stretched 3.85 -> s) + A17 violating-pair endpoints with small gap and mid-tilt angle."""
    out = [(1.396, 1.321, math.radians(27.7)), (1.344, 2.431, math.radians(24.5)),
           (1.273, 1.399, math.radians(45.0)), (1.6034, 1.9897, math.radians(33.02))]
    d = json.load(open(os.path.join(ROOT, "attempts", "A12-region-rank-pilot", "results",
                                    "analysis_s3.85.json")))
    for cx, cy, t, w in d["images"]:
        if 0.2 < t < 1.4:   # mid-tilt only
            f = s / 3.85
            out.append((cx * f, cy * f, t))
    st = np.load(os.path.join(ROOT, "attempts", "A17-kernel-root", "results", "k384_state.npz"),
                 allow_pickle=True)
    X, Y = st["pair_x"], st["pair_y"]
    dep = overlap_depth_many(X, Y)
    sel = dep > -0.12
    for P in (X[sel], Y[sel]):
        for cx, cy, t in P:
            if math.radians(15) < t % (math.pi / 2) < math.radians(75):
                out.append((cx, cy, t))
    return np.array(out)


def main():
    s = 3.84
    A0, w0, _ = load_atoms_a07_384()
    for r_merge in (0.10, 0.13, 0.16):
        A, w = coarsen_atoms(A0, w0, s, r_merge)
    r_merge = 0.13
    A, w = coarsen_atoms(A0, w0, s, r_merge)
    fm = FeatureMap(A, w, s)
    bp = binding_placements_384(s)
    print(f"binding placements: {len(bp)}")
    pat = fm.patterns(bp)
    cover_cnt = np.asarray(pat.sum(axis=0)).ravel()
    in_R = cover_cnt > 0
    # close under D4
    for g in range(8):
        in_R |= in_R[fm.G_atoms[g]]
    for g in range(8):
        in_R |= in_R[fm.G_atoms[g]]
    print(f"R-atoms (covered by binding placements, D4-closed): {in_R.sum()} of {fm.m}")
    # how selective? also try requiring coverage by >= 2 binding placements
    in_R2 = cover_cnt >= 3
    for _ in range(2):
        for g in range(8):
            in_R2 |= in_R2[fm.G_atoms[g]]
    print(f"R-atoms (>=3 binding covers): {in_R2.sum()}")

    fs = FullHybridSDP(fm, None, r_mask=in_R2)
    # rows
    rng = np.random.default_rng(0)
    t0 = time.time()
    nd = fs.add_diag(structured_placements(s))
    nd += fs.add_diag(random_placements(s, 4000, rng))
    print(f"diag rows {nd} ({time.time()-t0:.0f}s)")
    t0 = time.time()
    TX, TY = tangent_pairs(s, 30000, rng)
    ke0 = None
    npr = fs.add_pairs(TX, TY)  # only R-meeting kept
    st = np.load(os.path.join(ROOT, "attempts", "A17-kernel-root", "results", "k384_state.npz"),
                 allow_pickle=True)
    npr += fs.add_pairs(st["pair_x"], st["pair_y"])
    print(f"pair rows {npr} ({time.time()-t0:.0f}s)")
    r = fs.solve(verbose=False)
    print(f"SOLVE: lam = {r['lam']:.6f} [{r['status']}] in {r['time']:.1f}s "
          f"(m={fm.m}, orbits {fs.n_po}, {len(fs.diag_meta)} diag, {len(fs.pair_meta)} pair rows)")
    # automatic-class reference on same rows
    r0 = fs.solve(sign_everywhere=True)
    print(f"automatic-class (sign everywhere) on same diag rows: lam = {r0['lam']:.6f} "
          f"in {r0['time']:.1f}s")
    # two-measure GP reference on same rows/atoms
    from two_measure import TwoMeasureKernel
    tm = TwoMeasureKernel(fm)
    patd = fm.patterns(np.array(fs.diag_meta))
    lam_gp = tm.optimize(patd, log=lambda *a: None)
    print(f"two-measure GP on same rows: lam = {lam_gp:.6f}")


if __name__ == "__main__":
    main()
