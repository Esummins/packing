"""A19 -- define R from data (notes SS3): cluster A17's recorded pair rows (the violating /
near-active disjoint pairs at 3.84 -- all interior mid-tilt) + the A12 quarter-structure support.
Prints geometry stats and proposes R boxes; saves results/R_def.json."""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

from oracle_pair import overlap_depth_many


def main():
    s = 3.84
    st = np.load(os.path.join(ROOT, "attempts", "A17-kernel-root", "results", "k384_state.npz"),
                 allow_pickle=True)
    X, Y = st["pair_x"], st["pair_y"]
    dep = overlap_depth_many(X, Y)
    print(f"A17 recorded pair rows: {len(X)}; SAT depth: min {dep.min():.3f} med {np.median(dep):.3f} "
          f"max {dep.max():.3f}")
    # midpoints of the two centres, folded into the fundamental domain
    mid = 0.5 * (X[:, :2] + Y[:, :2])
    c = s / 2
    fx = np.minimum(np.abs(mid[:, 0] - c), np.abs(mid[:, 1] - c))
    fy = np.maximum(np.abs(mid[:, 0] - c), np.abs(mid[:, 1] - c))
    r = np.hypot(mid[:, 0] - c, mid[:, 1] - c)
    print(f"midpoint distance from centre: q10 {np.percentile(r,10):.3f} med {np.median(r):.3f} "
          f"q90 {np.percentile(r,90):.3f} max {r.max():.3f}")
    th = np.concatenate([X[:, 2], Y[:, 2]])
    print(f"angles (deg): q10 {np.degrees(np.percentile(th,10)):.1f} med "
          f"{np.degrees(np.median(th)):.1f} q90 {np.degrees(np.percentile(th,90)):.1f}")
    # where are the centres themselves?
    cen = np.vstack([X[:, :2], Y[:, :2]])
    rc = np.hypot(cen[:, 0] - c, cen[:, 1] - c)
    print(f"centre distance from centre: med {np.median(rc):.3f} q90 {np.percentile(rc,90):.3f} "
          f"max {rc.max():.3f}")
    # 2-D histogram of midpoints in folded coords (|x-c|, |y-c|) sorted
    H, xe, ye = np.histogram2d(fx, fy, bins=[8, 8], range=[[0, 1.92], [0, 1.92]])
    print("midpoint histogram (folded |dx|<=|dy|), rows=|dx| 0..1.92, cols=|dy|:")
    for i in range(8):
        print("   " + " ".join(f"{int(H[i,j]):5d}" for j in range(8)))
    # A12 structure at 3.85 (mid-tilt images), where do the tilted squares sit
    d = json.load(open(os.path.join(ROOT, "attempts", "A12-region-rank-pilot", "results",
                                    "analysis_s3.85.json")))
    tilted = [(cx, cy, t) for cx, cy, t, w in d["images"] if 0.2 < t < 1.4]
    print("A12 tilted images (3.85):", [(round(a,3), round(b,3), round(math.degrees(t),1))
                                        for a, b, t in tilted])
    # A18 binding cells at 3.84
    print("A18 r384 binding cells: (1.396,1.321,27.7deg), (1.344,2.431,24.5deg), (1.273,1.399,45deg)")


if __name__ == "__main__":
    main()
