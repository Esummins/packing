"""A150 -- one page per surviving 4-tuple, in A148's PANEL-G style.

The page answers the same question A148's pages do -- "can the remaining squares fit in the white
space?" -- for a node whose hypothesis is FOUR conditioned squares, one at each corner.

  container at s0; the four level-1 centre boxes (clipped, per corner, in global coordinates) as
  thin purple rectangles; each conditioned square drawn cyan at its box centre and mid-tilt with
  its A132 polygon core K' FILLED; the widened corner boxes [0, a_w]^2 as dotted squares; the
  FEASIBLE-CENTRE REGION (A148 geo148, margin-certified) green where a further square's centre can
  certainly sit and pale where undecided; the disk bound n_max for budget 7 and the tightest A144
  guard line printed in the caption.

    python code/draw150.py --n 20
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import polycore                                                     # noqa: E402
import geo148 as G                                                  # noqa: E402
import gallery148 as GA                                             # noqa: E402
import guardline as GL                                              # noqa: E402
import cells143 as C                                                # noqa: E402
import frames150 as F                                               # noqa: E402

RES = os.path.join(BASE, "results")
FIGS = os.path.join(BASE, "figs")
S0 = C.S0
A_W = C.A_W
SC = 150.0
MARG = 34.0


def page(tup, cells, outdir, extra=None, pitch=0.02, ntilt=36):
    """tup = ((ix,iy,it) x 4) in corner order BL, BR, TR, TL."""
    boxes = [F.global_box(c, cells[k]) for c, k in zip(F.CORNERS, tup)]
    cores = [polycore.build(b, max_v=16) for b in boxes]
    reg = G.feasible_region(S0, [pc.P for pc in cores], pitch_target=pitch, ntilt=ntilt)
    db = G.disk_bound(reg)
    W = 2 * MARG + S0 * SC
    H = MARG + S0 * SC + 132.0
    pn = GA.Pane(MARG, MARG + S0 * SC, SC)
    body = [GA.DEFS]
    # feasible-centre region
    for (x0, x1, y0, y1) in reg.runs(reg.green):
        body.append(pn.rect(x0, x1, y0, y1, "#a5d6a7", "none", 0.55, 0))
    for (x0, x1, y0, y1) in reg.runs(reg.undecided):
        body.append(pn.rect(x0, x1, y0, y1, "#c8e6c9", "none", 0.28, 0))
    body += pn.container(S0)
    # widened corner boxes
    for c in F.CORNERS:
        x0, x1, y0, y1 = F.to_global(c, 0.0, A_W, 0.0, A_W)
        body.append(pn.rect(x0, x1, y0, y1, "none", "#455a64", 0.0, 1.0, "3,3"))
    # the four conditioned squares + cores
    for i, (c, b, pc) in enumerate(zip(F.CORNERS, boxes, cores)):
        body.append(pn.rect(b.x0, b.x1, b.y0, b.y1, "none", "#7e57c2", 0.0, 1.1, "2,2"))
        cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
        th = math.radians(0.5 * (b.th0 + b.th1))
        body.append(pn.poly(G.sqpoly(cx, cy, th), "#00e5ff", "#0097a7", 0.20, 1.4))
        body.append(pn.poly([tuple(p) for p in pc.P], "#00e5ff", "#006064", 0.60, 1.0))
        body.append(pn.text(cx, cy, "%s %d%d t%d" % (c, tup[i][0], tup[i][1], tup[i][2]),
                            8, "#004d40", True, dy=3))
    # tightest guard line
    best = None
    for pos in np.arange(0.01, S0, 0.02):
        for ax in ("h", "v"):
            l = GL.Line(ax, float(pos))
            tot = sum(float(GL.minchord_box(b, l)["lo"]) for b in boxes)
            if best is None or S0 - tot < best[0]:
                best = (S0 - tot, ax, float(pos), tot)
    if best is not None:
        rhs, ax, pos, tot = best
        if ax == "h":
            body.append(pn.line(0, pos, S0, pos, "#d84315", 1.0, "5,3"))
        else:
            body.append(pn.line(pos, 0, pos, S0, "#d84315", 1.0, "5,3"))
    tag = "_".join("%d%d%d" % k for k in tup)
    y = MARG + S0 * SC + 18
    head = "A150 four-corner product node  %s   budget 7 = 11 - 4" % tag
    body.append(GA.txt(MARG, y, head, 12, "#111", True))
    y += 15
    ln2 = ("cells (local frames): " + "  ".join("%s=(%d,%d,t%d)" % (c, k[0], k[1], k[2])
                                                for c, k in zip(F.CORNERS, tup)))
    body.append(GA.txt(MARG, y, ln2, 9.5, "#333"))
    y += 13
    ln3 = ("disk bound: n_max = %d for budget 7 (open area %.4f, dilated %.4f);  "
           "tightest guard line: %s = %.3f, chord sum %.4f, rhs %.4f"
           % (db["n_max"], db["area_open"], db["area_dilated"],
              ("y" if best[1] == "h" else "x"), best[2], best[3], best[0]))
    body.append(GA.txt(MARG, y, ln3, 9.5, "#333"))
    y += 13
    ln4 = ("K' areas: " + " ".join("%.4f" % pc.area() for pc in cores)
           + ";  region pitch %.4f, %d tilts, margin %.4f" % (reg.pitch, reg.ntilt, reg.margin))
    body.append(GA.txt(MARG, y, ln4, 9.5, "#333"))
    y += 13
    if extra:
        body.append(GA.txt(MARG, y, extra, 9.5, "#b71c1c", True))
        y += 13
    foot = ("green = a further unit square's centre can certainly sit there; pale green = "
            "undecided band; white = certified no square.  Cyan squares are the four conditioned "
            "corner intruders at their box centre and mid-tilt; the filled cyan polygon is K'(B), "
            "the exact core every pose of the box contains.  Dashed grey = the widened corner "
            "boxes [0,a_w]^2, a_w = 1.0255.  Dashed orange = the tightest A144 guard line.")
    lines, y = GA.wrap(MARG, y, foot, W - 2 * MARG, 8.5, "#555")
    body += lines
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{int(H)}" '
            f'viewBox="0 0 {int(W)} {int(H)}"><rect width="100%" height="100%" fill="#fff"/>']
           + body + ["</svg>"])
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, "node_%s.svg" % tag)
    open(p, "w", encoding="utf-8").write("\n".join(doc))
    return p, db, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--list", default=os.path.join(RES, "nodes150.json"))
    a = ap.parse_args()
    byk = {(c.ix, c.iy, c.it): c for c in C.all_cells() if not c.empty}
    nodes = json.load(open(a.list, encoding="utf-8"))[:a.n]
    idx = []
    for n in nodes:
        tup = tuple(tuple(k) for k in n["tuple"])
        p, db, best = page(tup, byk, FIGS, extra=n.get("note"))
        idx.append(dict(node=n["node"], tuple=[list(k) for k in tup], svg=os.path.basename(p),
                        n_max=db["n_max"], area_open=db["area_open"],
                        guard_rhs=best[0], guard_axis=("y" if best[1] == "h" else "x"),
                        guard_pos=best[2]))
        print("drew", p, "n_max", db["n_max"], "rhs %.4f" % best[0], flush=True)
    json.dump(idx, open(os.path.join(RES, "draw150_index.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
