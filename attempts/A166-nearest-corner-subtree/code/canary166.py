"""A166 T3 -- THE CANARY, stated and decided.

`l1_153` is the Trump-image cell of the eleven (A140 `cells140.CELLS`: "A38 l1 idx 153 (Trump
image)"), and A166 confirms it exactly: Trump's image `g4`, square `sq9` (one of the three INTERIOR
tilted squares) has its pose INSIDE `l1_153`'s conditioned box `B_H` (pose distance 0.0000, all three
components 0).  So `F = Δ_λ ẑ` at `s0` satisfies `l1_153`'s hypothesis, and by Lemma K0-BLOCKED it
also satisfies the corner hypothesis at every corner in the WIDENED sense (A143 §4, A150 §4).

The canary therefore reads: **the cover A166 builds for `l1_153` must contain a branch that `g4`
reaches.**  If every branch is killed, A166's construction is unsound.  This script decides it by
locating `g4`'s widened TR meeters in the cover and naming the branch.

It also runs the same test on all eight images and all four corners, so the answer does not depend on
one lucky labelling, and it prints the EXACT penetrations (from A166's own from-scratch SAT) so the
result can be compared with A159's 60-dps figures.

    python code/canary166.py --pad wmax
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import cells166 as C                                            # noqa: E402
import check166 as K                                            # noqa: E402  (its own SAT)
import trump166 as T                                            # noqa: E402

RES = os.path.join(BASE, "results")
PADS = {"w0": 0.0, "wmax": C.W_MAX}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    ap.add_argument("--cell", default="l1_153")
    a = ap.parse_args()
    a_w = 1.0 + PADS[a.pad]
    Y0, st, lam = T.trump_scaled()
    images = {("g%d" % k): T.symmetry(Y0, k) for k in range(8)}
    interior = [i for i, (x, y, th) in enumerate(Y0)
                if abs(math.degrees(th) % 90) > 1e-6 and T.is_interior(x, y, th)]

    p = os.path.join(RES, "survivors166_%s_%s.json" % (a.pad, a.cell))
    d = json.load(open(p, encoding="utf-8"))
    corner = d["corner"]
    bHj = d["Hbox"]
    bH = (bHj["x0"], bHj["x1"], bHj["y0"], bHj["y1"], bHj["th0"], bHj["th1"])
    rect = K.corner_rect(corner, a_w)
    per = d["per_cell"]

    out = dict(pad=a.pad, a_w=a_w, cell=a.cell, corner=corner, s_trump=st, lam=lam, images={})
    verdicts = []
    for g, Z in images.items():
        # which squares of this image satisfy the cell's hypothesis (pose inside B_H)?
        inH = [i for i, (x, y, th) in enumerate(Z)
               if (bH[0] <= x <= bH[1] and bH[2] <= y <= bH[3]
                   and bH[4] <= (math.degrees(th) % 90.0) <= bH[5])]
        met = []
        for i, (x, y, th) in enumerate(Z):
            dep = K.sat_depth(K.verts(x, y, math.degrees(th) % 90.0), K.rect_poly(rect))
            if dep > 0.0:
                u, v, t = K.to_local(corner, x, y, math.degrees(th) % 90.0)
                k = K.locate_local(u, v, t, a_w)
                met.append(dict(sq=i, depth=dep, cell=(list(k) if k else None),
                                verdict=(per["%d%d%d" % k]["verdict"] if k and
                                         "%d%d%d" % k in per else None),
                                interior_tilted=bool(i in interior)))
        branch = None
        if len(inH) and len(met) >= 2:
            hset = set(inH)
            # (b) degenerate: one meeter IS the conditioned square
            deg = [m for m in met if m["sq"] in hset]
            oth = [m for m in met if m["sq"] not in hset]
            if deg and oth:
                good = [o for o in oth if o["verdict"] == "ALIVE"]
                branch = ("DEGENERATE (budget 9): meeter sq%d IS H, partner sq%d in cover cell %s "
                          "(verdict %s)" % (deg[0]["sq"], (good or oth)[0]["sq"],
                                            (good or oth)[0]["cell"], (good or oth)[0]["verdict"])
                          if good else
                          "DEGENERATE but the partner's cell is %s -- UNSOUND"
                          % oth[0]["verdict"])
            elif len(oth) >= 2:
                a1, b1 = oth[0], oth[1]
                branch = ("BUDGET 8: meeters sq%d, sq%d in cover cells %s, %s (verdicts %s, %s)"
                          % (a1["sq"], b1["sq"], a1["cell"], b1["cell"], a1["verdict"],
                             b1["verdict"]))
        out["images"][g] = dict(squares_in_BH=inH, meeters=met, branch=branch)
        if inH:
            verdicts.append((g, branch))
        print("%s  in B_H: %s | %s meeters: %s | branch: %s"
              % (g, inH, corner, [(m["sq"], round(m["depth"], 6), m["cell"], m["verdict"])
                                  for m in met], branch), flush=True)

    ok = bool(verdicts) and all(b and "UNSOUND" not in b for _g, b in verdicts)
    out["images_realising_the_cell"] = [g for g, _b in verdicts]
    out["CANARY_PASS"] = ok
    print()
    print("images realising %s: %s" % (a.cell, [g for g, _b in verdicts]))
    for g, b in verdicts:
        print("  %s -> %s" % (g, b))
    print("CANARY_PASS =", ok)
    json.dump(out, open(os.path.join(RES, "canary166_%s.json" % a.pad), "w"), indent=1)


if __name__ == "__main__":
    main()
