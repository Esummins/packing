"""
Numerical (non-rigorous, grid-based) check of the point sets in Stromquist 2003, Theorem 2.

* P1  : 10 points of Fig. 13 (3-4-3 lattice).  Claim: every unit square inside S=[0,s]^2 whose
        centre is NOT in the four edge rectangles contains a point of P1.
* P2  : 12 points of Fig. 14.  Claim: every unit square inside S contains a point of P2.
* MU  : measure mu = (2/3) delta_{P1} + (1/3) delta_{P2}  (mass 32/3 < 11).
        Claim: mu(Q) >= 1 for every unit square Q inside S.
* Also: every unit square inside S that avoids P1 contains A1, A2, A3 (up to symmetry).

We test closed unit squares (side exactly 1) with centre (x,y) and tilt theta, on a grid.
Stromquist's "boxes" are open squares of side > 1, so a closed unit square that fits inside S and
avoids the points is exactly the kind of counterexample his lemmas exclude (up to boundary cases).
Usage:  python check_stromquist.py [grid_xy] [grid_theta]
"""
import sys
import numpy as np

s = 2 + 2 * np.sqrt(4 / 5)          # 3.788854...
r5 = 1 / np.sqrt(5)

# ---- P1: Fig. 13 -------------------------------------------------------------------------
row_y = [1.0, s / 2, s - 1]
P1 = []
for x in (1.0, s / 2, s - 1):
    P1.append((x, 1.0)); P1.append((x, s - 1))
for x in (1.5 - s / 4, 0.5 + s / 4, s - (0.5 + s / 4), s - (1.5 - s / 4)):
    P1.append((x, s / 2))
P1 = np.array(P1)

# ---- P2: Fig. 14 -------------------------------------------------------------------------
A1 = (1.0, 0.9); A2 = (s / 2, 0.9); A3 = (1 + r5, 1.12)
B = (s - 1, 1.0); C = (s - 0.9, s / 2); D = (s - 1, s - 1); E = (s / 2, s - 0.9); F = (1.0, s - 1)
G = (0.8, 1.85); H = (1.5, 2.1); I = (2.1, 2.1); J = (2.1, 1.5)
P2 = np.array([A1, A2, A3, B, C, D, E, F, G, H, I, J])
A123 = np.array([A1, A2, A3])


def contains(pts, cx, cy, th, half=0.5):
    """boolean array: which points lie in the closed square centre (cx,cy), tilt th, half-side half."""
    c, sn = np.cos(th), np.sin(th)
    dx = pts[:, 0] - cx; dy = pts[:, 1] - cy
    u = c * dx + sn * dy; v = -sn * dx + c * dy
    return (np.abs(u) <= half) & (np.abs(v) <= half)


def in_edge_rect(cx, cy):
    """centre in one of the four top/bottom edge rectangles [1,s/2]x[0,1], [s/2,s-1]x[0,1], mirrors"""
    return (1 <= cx <= s - 1) and (cy <= 1 or cy >= s - 1)


def main(nxy=400, nth=181):
    thetas = np.linspace(0, np.pi / 2, nth, endpoint=False)
    bad_P1, bad_P2, bad_mu, bad_A = [], [], [], []
    for th in thetas:
        h = (np.cos(th) + np.sin(th)) / 2           # half of bounding-box side
        lo, hi = h, s - h                            # centre range for the square to fit in S
        xs = np.linspace(lo, hi, nxy)
        for cx in xs:
            for cy in xs:
                m1 = contains(P1, cx, cy, th)
                m2 = contains(P2, cx, cy, th)
                mu = (2 / 3) * m1.sum() + (1 / 3) * m2.sum()
                if not m1.any() and not in_edge_rect(cx, cy):
                    bad_P1.append((cx, cy, np.degrees(th)))
                if not m2.any():
                    bad_P2.append((cx, cy, np.degrees(th)))
                if mu < 1 - 1e-12:
                    bad_mu.append((cx, cy, np.degrees(th), mu))
                if not m1.any():
                    # symmetry: map centre into bottom-left / bottom-right edge rectangle -> reflect
                    x, y = cx, cy
                    if y > s / 2: y = s - y
                    if x > s / 2: x = s - x
                    # now centre in [1, s/2] x [0,1] (should be), check A1,A2,A3 all inside the reflected square
                    # reflect the tilt accordingly
                    th2 = th
                    if cx > s / 2: th2 = -th2
                    if cy > s / 2: th2 = -th2
                    if not contains(A123, x, y, th2).all():
                        bad_A.append((cx, cy, np.degrees(th)))
    print(f"s = {s:.6f}, grid {nxy}^2 x {nth} tilts")
    print("P1 fails (outside edge rects):", len(bad_P1), bad_P1[:5])
    print("P2 fails:", len(bad_P2), bad_P2[:5])
    print("mu<1 fails:", len(bad_mu), bad_mu[:5])
    print("P1-avoiding square not containing all of A1,A2,A3:", len(bad_A), bad_A[:5])


if __name__ == "__main__":
    nxy = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    nth = int(sys.argv[2]) if len(sys.argv) > 2 else 181
    main(nxy, nth)
