"""A155 -- the band at pad 0 vs pad 0.0255, in A148's panel-G idiom.

One page, two blocks of six panels (one panel per 15 deg tilt window):

  * each panel draws the BL corner zone [1/2, a_w + sqrt2/2]^2 of CENTRES, the corner box
    [0, a_w]^2 (dashed), and the 36 position cells of that tilt window;
  * a cell is GREY when (B1) kills it (no partner cell admits an interior-disjoint second meeter
    that also meets the corner box) -- the (T) teleport leaves;
  * a surviving cell is shaded by its POSE-LEVEL occupancy p (the fraction of sampled realised
    first meeters in the cell that have a witnessed partner): dark green p = 1, pale green
    p -> 0, RED HATCH p = 0 -- alive under the level-1 test but with no witnessed 2-crowd at all,
    i.e. the cells a finer cover would be expected to kill;
  * the bottom strip shows four DRAWN 2-crowds at pad 0 (two interior-disjoint unit squares both
    meeting the exact unit corner box) with their A132 cores, so the reader can see what the
    surviving band is made of.

    python code/draw155.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                        # noqa: F401,E402
import numpy as np                                                  # noqa: E402
import polycore                                                     # noqa: E402
import gallery148 as GA                                             # noqa: E402
import cells155 as C                                                # noqa: E402
import geom155 as G                                                 # noqa: E402
import band155 as B                                                 # noqa: E402

RES = os.path.join(BASE, "results")
FIGS = os.path.join(BASE, "figs")
S0 = C.S0
SC = 108.0                       # px per unit in the zone panels
MARG = 40.0
GAPX = 22.0


def pcol(p):
    if p is None:
        return "#eceff1"
    y = max(0.0, min(1.0, p))
    return "hsl(%d,%d%%,%d%%)" % (122, 40 + int(30 * y), 92 - int(40 * y))


def zone_panel(body, ox, oy, tag, it, band, occ, a_w, npos=6):
    zlo, zhi = C.zone(a_w)
    pn = GA.Pane(ox, oy, SC)
    body.append(pn.rect(0.0, a_w, 0.0, a_w, "#ffe0b2", "#455a64", 0.35, 1.2, "3,3"))
    w = (zhi - zlo) / npos
    for ix in range(npos):
        for iy in range(npos):
            k = (ix, iy, it)
            x0, x1 = zlo + ix * w, zlo + (ix + 1) * w
            y0, y1 = zlo + iy * w, zlo + (iy + 1) * w
            if k not in band:
                body.append(pn.rect(x0, x1, y0, y1, "#b0bec5", "#78909c", 0.75, 0.5))
                continue
            p = occ.get(k)
            body.append(pn.rect(x0, x1, y0, y1, pcol(p), "#78909c", 0.95, 0.5))
            if p == 0.0:
                body.append(pn.rect(x0, x1, y0, y1, "url(#hatchr)", "#c62828", 1.0, 0.7))
    body.append(pn.rect(zlo, zhi, zlo, zhi, "none", "#37474f", 0.0, 1.2))
    body.append(GA.txt(ox + 2, oy - zhi * SC - 6, "tilt %d-%d deg" % (it * 15, it * 15 + 15),
                       9, "#37474f", True))


def crowd_panel(body, ox, oy, cx, cy, th, a_w, sc=118.0):
    pn = GA.Pane(ox, oy, sc)
    body.append(pn.rect(0.0, a_w, 0.0, a_w, "#ffe0b2", "#455a64", 0.45, 1.2, "3,3"))
    cols = (("#00e5ff", "#006064"), ("#ce93d8", "#4a148c"))
    for j in (0, 1):
        V = G._verts(np.array(cx[j]), np.array(cy[j]), np.array(th[j]))
        body.append(pn.poly([(float(a), float(b)) for a, b in V], cols[j][0], cols[j][1],
                            0.30, 1.3))
    body.append(pn.rect(0.0, 2.6, 0.0, 2.6, "none", "#90a4ae", 0.0, 0.7))
    body.append(GA.txt(ox + 2, oy + 12, "th = %.1f, %.1f deg" % (th[0], th[1]), 8, "#37474f"))


def main():
    os.makedirs(FIGS, exist_ok=True)
    blocks = []
    for tag in ("w0", "wmax"):
        d = json.load(open(os.path.join(RES, "band155_pairs_%s.json" % tag), encoding="utf-8"))
        band = {tuple(k) for k in d["band_cells"]}
        occ = {}
        p = os.path.join(RES, "band155_occ_%s.json" % tag)
        if os.path.exists(p):
            o = json.load(open(p, encoding="utf-8"))
            occ = {tuple(r["cell"]): r["p"] for r in o["rows"]}
        blocks.append((tag, d, band, occ))
    zhi0 = C.zone(1.0 + blocks[1][1]["pad"])[1]
    pw = zhi0 * SC + GAPX
    W = 2 * MARG + 6 * pw
    Hblock = zhi0 * SC + 46.0
    body = [GA.DEFS]
    y = MARG + 22.0
    for (tag, d, band, occ) in blocks:
        a_w = d["a_w"]
        ttl = ("pad w = %.7f (%s) -- band %d of 216 cells, %d alive pair cells of 11 772"
               % (d["pad"], d["why"], d["band"], d["pair_stats"]["alive"]))
        body.append(GA.txt(MARG, y - 26, ttl, 11.5, "#111", True))
        for it in range(6):
            zone_panel(body, MARG + it * pw, y + C.zone(a_w)[1] * SC, tag, it, band, occ, a_w)
        y += Hblock + 34.0
    # ---- drawn 2-crowds at pad 0
    rng = np.random.default_rng(15501)
    CX, CY, TH = B.draw_crowds(rng, 1.0, 4000)
    body.append(GA.txt(MARG, y - 6, "drawn 2-crowds at pad 0 (both squares meet the EXACT unit "
                       "corner box, interiors disjoint)", 11.5, "#111", True))
    csc = 88.0
    sel = rng.choice(len(CX), size=4, replace=False)
    for i, s in enumerate(sel):
        crowd_panel(body, MARG + i * (2.6 * csc + 26.0), y + 2.6 * csc + 12.0,
                    CX[s], CY[s], TH[s], 1.0, sc=csc)
    y += 2.6 * csc + 48.0
    foot = ("Grey = the cell is killed by (B1): no cell of the cover admits an interior-disjoint "
            "second meeter of the corner box avoiding K'(first meeter), so the corner is met by "
            "at most one square and Lemma K0-FREE teleports the packing into a k >= 1 class. "
            "Green = the cell survives (B1); the shade is the pose-level occupancy p (fraction of "
            "sampled realised first meeters in the cell that have a witnessed partner), dark = 1, "
            "pale = 0. RED HATCH = p = 0 over the whole sample: alive under the level-1 pair test "
            "but with no witnessed 2-crowd -- the cells a finer cover is expected to kill. "
            "Dashed orange square = the corner box [0, a_w]^2; the outer frame is the corner zone "
            "[1/2, a_w + sqrt2/2]^2 of admissible centres.")
    lines, y = GA.wrap(MARG, y, foot, W - 2 * MARG, 9.0, "#555")
    body += lines
    H = y + 30.0
    doc = (['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
            % (int(W), int(H), int(W), int(H)),
            '<rect width="100%" height="100%" fill="#fff"/>'] + body + ["</svg>"])
    out = os.path.join(FIGS, "band155_pad0_vs_padmax.svg")
    open(out, "w", encoding="utf-8").write("\n".join(doc))
    print("wrote", out)


if __name__ == "__main__":
    main()
