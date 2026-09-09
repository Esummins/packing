"""A166 T1 -- LEMMA A166-1, the NEAREST-CORNER SQUEEZE, and the dichotomy it forces.

This is the geometric content of the nearest-corner sub-tree, and it is a THEOREM about the whole
conditioned box, not a box-cover statement.

--------------------------------------------------------------------------------------------------
LEMMA A166-1 (the squeeze).  Fix a corner `c`, a pad `w >= 0`, `a_w = 1 + w`, and work in `c`'s own
local frame (corner at the origin, container in `u, v >= 0`; A150's rotation convention).  Let

    Z(w)  :=  [1/2, a_w + sqrt2/2]^2

be the corner-meeting zone: every unit square inside `[0, s0]^2` whose interior meets
`int [0, a_w]^2` has its centre in `Z(w)`  (A143 (R3): admissibility gives `c_i >= h(theta) >= 1/2`
and meeting gives `c_i < a_w + h(theta) <= a_w + sqrt2/2`).

Let `R_H` be the centre RECTANGLE of the node's conditioned box `B_H` (in the same local frame), and
put

    S*(R_H)  :=  { p in Z(w) : max over the four corners v of R_H of |p - v| >= 1 } .

Suppose `Q_1 != Q_2` are two squares of the packing that meet `int [0, a_w]^2`, and that NEITHER is
the conditioned square `H`.  Then

    (i)   z_{Q_1}, z_{Q_2} in Z(w);
    (ii)  |z_{Q_i} - z_H| >= 1 for i = 1, 2, and |z_{Q_1} - z_{Q_2}| >= 1
          (two unit squares with disjoint interiors have centre distance >= 1: any separating
          direction `n` gives |d.n| >= h_1(n) + h_2(n) >= 1/2 + 1/2);
    (iii) z_{Q_i} in S*(R_H)  --  because `z_H in R_H`, so `|z_{Q_i} - z_H| >= 1` forces
          `max_v |z_{Q_i} - v| >= 1`;

hence `S*(R_H)` contains two points at distance `>= 1` and

    **diam S*(R_H) < 1  ==>  no such pair exists  ==>  H itself meets int [0, a_w]^2.**

Together with Lemma K0-BLOCKED (every corner box of `F` is met by two DISTINCT squares) this is a
DICHOTOMY on the node:

    (A) `H` meets `int B_c^w`  -- the DEGENERATE branch: one of the two corner meeters IS `H`, the
        node becomes `H in B_H ∩ (poses meeting the corner box)` plus ONE further corner square,
        budget 11 - 2 = 9;
    (B) otherwise the node is CONTRADICTORY -- a (C) leaf, no LP, no certificate.

and (B) is decided by A161's exact `box_misses_cell_exact(B_H, corner box)`.

--------------------------------------------------------------------------------------------------
HOW `diam S*` IS BOUNDED, SOUNDLY AND EXACTLY.  `p -> |p - v|` is convex, so `max_v |p - v|` is
convex and its supremum over a grid square is attained at one of the square's four corners.  Cover
`Z(w)` by an `n x n` grid of closed squares with EXACT rational corners; mark a square if the max
over its four corners of `max_v |p - v|^2` is `>= 1` (exact rational comparison).  Then

    S*(R_H)  subset  union of the marked squares  subset  conv(corners of the marked squares),

so `diam S*(R_H) <= diam conv(...)`, and the hull diameter is a max of exact rational squared
distances between hull vertices.  Refining the grid only tightens the bound; the printed value is an
UPPER bound of the truth, so `bound < 1` is a proof.

    python code/squeeze166.py --n 240
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                          # noqa: E402
import cells166 as C                                        # noqa: E402

RES = os.path.join(BASE, "results")
SQ2H = math.sqrt(0.5)


def _hull(pts):
    """monotone-chain convex hull on exact rational points."""
    P = sorted(set(pts))
    if len(P) <= 2:
        return P

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo = []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def squeeze_bound(RH, a_w, n=240):
    """(bound on diam S*, n_marked, hull size).  RH = (u0, u1, v0, v1) exact-able floats."""
    u0, u1, v0, v1 = (Fr(str(x)) for x in RH)
    verts = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    zlo = Fr(1, 2)
    zhi = Fr(str(a_w)) + Fr(SQ2H).limit_denominator(10 ** 12)
    h = (zhi - zlo) / n
    ONE = Fr(1)

    def far(p):
        return max((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 for q in verts) >= ONE

    marked = []
    grid = [zlo + h * i for i in range(n + 1)]
    farflag = [[far((grid[i], grid[j])) for j in range(n + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(n):
            if (farflag[i][j] or farflag[i + 1][j] or farflag[i][j + 1] or farflag[i + 1][j + 1]):
                marked.append((i, j))
    if not marked:
        return 0.0, 0, 0, None
    pts = set()
    for (i, j) in marked:
        pts.add((grid[i], grid[j]))
        pts.add((grid[i + 1], grid[j]))
        pts.add((grid[i], grid[j + 1]))
        pts.add((grid[i + 1], grid[j + 1]))
    H = _hull(sorted(pts))
    best = Fr(0)
    arg = None
    for i in range(len(H)):
        for j in range(i + 1, len(H)):
            d2 = (H[i][0] - H[j][0]) ** 2 + (H[i][1] - H[j][1]) ** 2
            if d2 > best:
                best, arg = d2, (H[i], H[j])
    return math.sqrt(float(best)), len(marked), len(H), (best, arg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=240)
    a = ap.parse_args()
    out = []
    for tag, w in (("wmax", C.W_MAX), ("w0", 0.0)):
        a_w = 1.0 + w
        print("=== pad %s  a_w = %.9f  zone [0.5, %.7f]" % (tag, a_w, a_w + SQ2H), flush=True)
        for (meta, b, _rec) in C.load_eleven():
            corner, dists = C.nearest_corner(b)
            rect = C.corner_rect(corner, a_w)
            can, det = G.cell_can_meet(b, rect)
            # H's centre rectangle in the corner's local frame
            uu = [C.to_local_pose(corner, x, y, 0.0)[:2]
                  for x in (b.x0, b.x1) for y in (b.y0, b.y1)]
            u0 = min(p[0] for p in uu)
            u1 = max(p[0] for p in uu)
            v0 = min(p[1] for p in uu)
            v1 = max(p[1] for p in uu)
            t0 = time.time()
            bnd, nm, nh, dbg = squeeze_bound((u0, u1, v0, v1), a_w, a.n)
            zc = C.to_local_pose(corner, *C.box_centre(b), 0.0)
            rec = dict(cell=meta["cell"], level=meta["level"], family=meta["family"], pad=tag,
                       a_w=a_w, corner=corner, dist_to_corner=round(dists[corner], 6),
                       RH_local=[float(u0), float(u1), float(v0), float(v1)],
                       zH_local=[round(zc[0], 6), round(zc[1], 6)],
                       H_can_meet_corner=bool(can),
                       H_misses_axis=(None if can else det.get("axis")),
                       H_misses_margin=(None if can else det.get("margin")),
                       diam_S_star_upper=round(bnd, 9), n_marked=nm, n_hull=nh,
                       squeeze_kills=bool(bnd < 1.0),
                       verdict=("DEAD_SQUEEZE" if (bnd < 1.0 and not can)
                                else "DEGENERATE_ONLY" if bnd < 1.0
                                else "PAIR_COVER_NEEDED"),
                       grid_n=a.n, secs=round(time.time() - t0, 1))
            out.append(rec)
            print("%-12s %s  H_can_meet=%-5s  diam S* <= %.6f %s -> %s"
                  % (meta["cell"], corner, can, bnd,
                     "(< 1: SQUEEZE FIRES)" if bnd < 1.0 else "", rec["verdict"]), flush=True)
    p = os.path.join(RES, "squeeze166.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
