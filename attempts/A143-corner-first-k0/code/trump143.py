"""A143 -- where TRUMP enters the corner-first cover (the PI's prediction).

trump5's frame has three SIMPLE corners (BL[2,1], BR[1], TR[1] axis-aligned at their slots) and one
corner met only by tilted squares.  Under the D4 reduction that corner becomes BL, so the PI's
prediction is that the doubly-met corner-first tree carries essentially ONE deep lineage: the pair
cell(s) holding Trump's two meeters at its non-simple corner.

This module takes Trump's exact placements (A65 `crowdfam.trump_scaled`, the A22/known_results-6
data, centres dilated by lambda = s0/shat so the family lives at s0), forms all eight D4 images, and
for each image and each corner reports the meeters of the widened corner box [0, a_w]^2, whether
each is axis-aligned (a SIMPLE corner square) and which level-1 cell / pair cell the meeters fall in.

    python code/trump143.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A99 = os.path.join(ROOT, "attempts", "A99-k0-tree-v2", "code")
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
for _p in (A99, _A57, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import class84 as K84                                           # noqa: E402
import cells143 as C                                            # noqa: E402

S0 = C.S0
AW = C.A_W
CORNERS = ("BL", "BR", "TR", "TL")


def to_corner(cx, cy, th, corner, s=S0):
    """pose in the corner's own frame (corner at the origin, container in x, y >= 0)."""
    if corner == "BL":
        return cx, cy, th
    if corner == "BR":
        return s - cx, cy, -th
    if corner == "TL":
        return cx, s - cy, -th
    return s - cx, s - cy, th


def main():
    Y0, s_trump, lam = K84.trump_scaled()
    out = dict(s_trump=s_trump, lam=lam, s0=S0, a_w=AW, images={})
    for k in range(8):
        Z = K84.symmetry(Y0, k)
        img = {}
        for corner in CORNERS:
            meet = []
            for i, (x, y, th) in enumerate(Z):
                u, v, t = to_corner(x, y, th, corner)
                tn = math.degrees(t) % 90.0
                if not C.meets_bl(u, v, tn, a_w=AW):
                    continue
                simple = min(tn, 90.0 - tn) < 1e-6
                cellk = C.locate(u, v, tn)
                meet.append(dict(sq=i, u=round(u, 6), v=round(v, 6), th=round(tn, 6),
                                 simple=bool(simple), cell=(list(cellk) if cellk else None)))
            img[corner] = dict(n=len(meet), n_simple=sum(1 for m in meet if m["simple"]),
                               meeters=meet)
        out["images"]["g%d" % k] = img
        line = "  ".join(f"{c}:{img[c]['n']}({img[c]['n_simple']}s)" for c in CORNERS)
        print(f"g{k}  {line}", flush=True)
    p = os.path.join(BASE, "results", "trump143.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p, flush=True)

    # the non-simple corner: which image has BL met only by tilted squares?
    hits = []
    for k in range(8):
        bl = out["images"]["g%d" % k]["BL"]
        if bl["n"] >= 2 and bl["n_simple"] == 0:
            cells = sorted(tuple(m["cell"]) for m in bl["meeters"] if m["cell"])
            hits.append(dict(image="g%d" % k, cells=[list(c) for c in cells],
                             meeters=bl["meeters"]))
    print(json.dumps(hits, indent=1))
    json.dump(hits, open(os.path.join(BASE, "results", "trump143_blpairs.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
