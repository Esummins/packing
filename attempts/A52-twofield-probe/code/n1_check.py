#!/usr/bin/env python3
"""A42 T1 -- exact instance verification of Lemma N1's hypothesis (H1)
(docs/proofs/occupancy_collapse.md section 3).

Checks, in exact rational arithmetic (Fraction over the exact binary float values):
  1. min pairwise centre distance^2 of the 11 A37 Trump e-frame placements  (expect exactly 1);
  2. pairwise disjointness of the 11 footprints R_j = clip(p_j +- r, [1/2, s0-1/2]^2)
     via the min inter-rectangle sup-gap  (expect > 0);
  3. max footprint diameter^2  (expect < 1).
Exit code 0 iff all hold. r defaults to 0.06; any r' <= 0.06 only shrinks footprints, so a
pass at 0.06 covers every sweep radius.
"""
import itertools
import sys
from fractions import Fraction as Fr

import seam38

def main(r=Fr(6, 100)):
    places, _ = seam38.trump_placements('e')
    s0 = Fr(969271, 250000)
    lo, hi = Fr(1, 2), s0 - Fr(1, 2)
    rects = []
    for (x, y, t) in places:
        X, Y = Fr(x), Fr(y)          # exact: float -> rational
        rects.append((max(lo, X - r), min(hi, X + r), max(lo, Y - r), min(hi, Y + r)))

    d2 = min((Fr(places[i][0]) - Fr(places[j][0])) ** 2 +
             (Fr(places[i][1]) - Fr(places[j][1])) ** 2
             for i, j in itertools.combinations(range(11), 2))

    def gap(a, b):
        dx = max(b[0] - a[1], a[0] - b[1], Fr(0))
        dy = max(b[2] - a[3], a[2] - b[3], Fr(0))
        return max(dx, dy)

    g = min(gap(a, b) for a, b in itertools.combinations(rects, 2))
    diag2 = max((b[1] - b[0]) ** 2 + (b[3] - b[2]) ** 2 for b in rects)

    print("min centre dist^2 (exact) =", d2, "=", float(d2))
    print("min footprint sup-gap     =", g, "~", float(g))
    print("max footprint diam^2      =", diag2, "~", float(diag2))
    ok = (d2 >= 1) and (g > 0) and (diag2 < 1)
    print("H1 HOLDS" if ok else "H1 FAILS")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(Fr(sys.argv[1]) if len(sys.argv) > 1 else Fr(6, 100)))
