"""A143 drawings, in A140's format (three cores per H, legend, schematic objects as thin dashed
outlines).

  figs/cover143_single.svg   the level-1 single-intruder cover: 6 tilt panels x a 6x6 position
                             grid, cells coloured by geometry verdict, Trump-occupied cells hatched.
  figs/cover143_pairs.svg    the level-1 PAIR cover: one 36x36 verdict matrix per (tilt, tilt)
                             block, coloured by which prune fired; Trump pair cells ringed.
  figs/pair_survivors.svg    one page per drawn pair cell: the container, the widened BL box, both
                             hypothesis squares H1, H2 at their box centres with the THREE cores
                             (stock K(a) solid black, A135 exact axis core dashed black, A132
                             polygon core K' purple fill), and the extremal-tilt outlines as thin
                             dashed schematics.

    python code/draw143.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
_A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
for _p in (_A57, _A132, _A135, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import polycore                                                 # noqa: E402
import exactcore                                                # noqa: E402
import cells143 as C                                            # noqa: E402
import pairs143 as P                                            # noqa: E402

FIGS = os.path.join(BASE, "figs")
os.makedirs(FIGS, exist_ok=True)

COL = {"ALIVE-CORE": "#c8e6c9", "P2-CENTRE-DIST": "#ffcdd2", "P1-CORES-MEET": "#ef9a9a",
       "P1s-SUBBIN": "#b71c1c", "ALIVE-GEOM": "#c8e6c9", "CLIP-EMPTY": "#9e9e9e"}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, s, size=9, col="#111", bold=False):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial" font-size="{size}" '
            f'fill="{col}"{" font-weight=\"bold\"" if bold else ""}>{esc(s)}</text>')


def rect(x, y, w, h, fill="none", stroke="#333", sw=0.6, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" '
            f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def poly(pts, fill="none", stroke="#333", sw=0.7, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (f'<polygon points="{p}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def svg(body, w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#fff"/>'
            + "".join(body) + "</svg>")


# ------------------------------------------------------------------ 1. single-intruder cover
def draw_single():
    geo = {}
    for ln in open(os.path.join(BASE, "results", "geom143.dedup.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        geo[r["cell"]] = r
    tr = json.load(open(os.path.join(BASE, "results", "trump143_cells.json"), encoding="utf-8"))
    trump = {tuple(s) for s in tr["single"]}
    cell = 26
    pad, top = 40, 96
    body = [txt(16, 26, "A143 — corner-first level-1 cover of k0_00: the BL intruder's cell "
                        "(6 position x 6 position x 6 tilt = 216)", 14, "#111", True),
            txt(16, 44, "position grid over the corner-meeting zone [1/2, a_w + √2/2]^2 = "
                        f"[{C.ZLO:.4f}, {C.ZHI:.4f}]^2, a_w = 1 + w = {C.A_W:.6f} "
                        "(Lemma K0-WIDEN); one panel per 15° tilt window.", 10),
            txt(16, 60, "GREEN = survives every geometric leaf (container clip, K' vs walls, "
                        "K' lane test on all four corners).  RED would be a geometry kill — "
                        "there are none.", 10),
            txt(16, 76, "HATCHED = a Trump image's BL meeter lies in this cell (the canary: it "
                        "can never be certified dead).  x >= y is the D4_BL fundamental domain; "
                        "cells below the diagonal are its transpose images.", 10)]
    body.append('<defs><pattern id="h" width="5" height="5" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" '
                'stroke="#1a237e" stroke-width="1.4"/></pattern></defs>')
    for it in range(C.NTILT):
        ox = pad + it * (C.NPOS * cell + 34)
        oy = top + 24
        body.append(txt(ox, oy - 8, f"tilt [{it*15}°, {(it+1)*15}°)", 10, "#111", True))
        for ix in range(C.NPOS):
            for iy in range(C.NPOS):
                nm = "c1_%d%d_t%d" % (ix, iy, it)
                v = geo.get(nm, {}).get("verdict", "?")
                x = ox + ix * cell
                y = oy + (C.NPOS - 1 - iy) * cell
                body.append(rect(x, y, cell, cell, COL.get(v, "#eee"), "#607d8b", 0.5))
                if (ix, iy, it) in trump:
                    body.append(rect(x, y, cell, cell, "url(#h)", "#1a237e", 1.2))
                if ix < iy:
                    body.append(rect(x + 2, y + 2, cell - 4, cell - 4, "none", "#90a4ae", 0.4,
                                     dash="2,2"))
        body.append(f'<line x1="{ox:.1f}" y1="{oy + C.NPOS*cell:.1f}" '
                    f'x2="{ox + C.NPOS*cell:.1f}" y2="{oy:.1f}" stroke="#37474f" '
                    'stroke-width="1" stroke-dasharray="4,3"/>')
        body.append(txt(ox, oy + C.NPOS * cell + 14, "x →", 8, "#555"))
    w = pad + C.NTILT * (C.NPOS * cell + 34) + 20
    h = top + 24 + C.NPOS * cell + 60
    body.append(txt(16, h - 30, "Legend: cell colour = geometry verdict; dashed inner square = "
                                "non-canonical (x < y) cell; diagonal line = the D4_BL mirror "
                                "x = y (transpose, θ → 90° − θ).", 9))
    body.append(txt(16, h - 16, "Result: 0 of 216 cells die by geometry alone in the "
                                "single-intruder root.", 9, "#b71c1c", True))
    open(os.path.join(FIGS, "cover143_single.svg"), "w", encoding="utf-8").write(svg(body, w, h))
    print("wrote figs/cover143_single.svg")


# ------------------------------------------------------------------ 2. pair cover
def draw_pairs():
    rows = [json.loads(l) for l in
            open(os.path.join(BASE, "results", "pairs143_geom.jsonl"), encoding="utf-8")]
    V = {(tuple(r["pair"][0]), tuple(r["pair"][1])): r["verdict"] for r in rows}
    tr = json.load(open(os.path.join(BASE, "results", "trump143_cells.json"), encoding="utf-8"))
    tp = {(tuple(p["pair"][0]), tuple(p["pair"][1])) for p in tr["pairs"]}
    px = 5
    blk = 36 * px
    pad, top = 46, 118
    body = [txt(16, 26, "A143 — corner-first level-1 PAIR cover of k0_00 (the doubly-met BL "
                        "corner): 11,772 D4_BL-canonical pair cells", 14, "#111", True),
            txt(16, 44, "Rows/columns of each block are the 36 position cells (ix + 6·iy) of "
                        "the two conditioned squares; blocks are the (tilt of Q1, tilt of Q2) "
                        "windows.  Only the canonical half of each block is populated.", 10),
            txt(16, 60, "RED = P2 (max centre distance over the two boxes < 1 ⇒ the squares "
                        "overlap);  MID RED = P1 (K'(A) meets K'(B) ⇒ every realisation "
                        "overlaps);  DARK RED = P1s (A131 per-tilt-sub-bin refinement of P1);  "
                        "GREEN = survives.", 10),
            txt(16, 76, "BLUE RING = a Trump image realises this pair cell (canary).  "
                        "Geometry alone empties 9,638 of 11,772 = 81.9 %.", 10, "#1a237e", True)]
    for t1 in range(C.NTILT):
        for t2 in range(C.NTILT):
            ox = pad + t2 * (blk + 12)
            oy = top + t1 * (blk + 26)
            body.append(txt(ox, oy - 5, f"θ1 {t1*15}–{(t1+1)*15}°  ×  "
                                        f"θ2 {t2*15}–{(t2+1)*15}°", 7.5))
            body.append(rect(ox, oy, blk, blk, "#fafafa", "#b0bec5", 0.5))
            for p1 in range(36):
                for p2 in range(36):
                    k1 = (p1 % 6, p1 // 6, t1)
                    k2 = (p2 % 6, p2 // 6, t2)
                    key = P.pair_canonical(k1, k2)
                    v = V.get(key)
                    if v is None:
                        continue
                    body.append(f'<rect x="{ox + p2*px:.1f}" y="{oy + p1*px:.1f}" '
                                f'width="{px}" height="{px}" fill="{COL.get(v, "#eee")}" '
                                'stroke="none"/>')
                    if key in tp:
                        body.append(f'<rect x="{ox + p2*px - 0.5:.1f}" '
                                    f'y="{oy + p1*px - 0.5:.1f}" width="{px+1}" '
                                    f'height="{px+1}" fill="none" stroke="#1a237e" '
                                    'stroke-width="1.3"/>')
    w = pad + C.NTILT * (blk + 12) + 20
    h = top + C.NTILT * (blk + 26) + 46
    body.append(txt(16, h - 26, "Trump's genuinely (unwidened) doubly-met BL corner is the pair "
                                "cell {(0,4,0), (5,0,3)} (≡ {(0,4,5),(5,0,3)} under the "
                                "θ ≡ θ+90° glue): an axis-aligned non-slot "
                                "meeter with a 49.82° one.", 9))
    body.append(txt(16, h - 12, "Lemma K0-WIDEN's pad w = 0.02551 adds seven more Trump-occupied "
                                "pair cells (flush neighbours that meet the widened but not the "
                                "unwidened box): the canary is 9 pair cells, not 1.", 9))
    open(os.path.join(FIGS, "cover143_pairs.svg"), "w", encoding="utf-8").write(svg(body, w, h))
    print("wrote figs/cover143_pairs.svg")


# ------------------------------------------------------------------ 3. pair pages, A140 format
def sq_pts(cx, cy, th, ox, oy, sc, half=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(ox + (cx + su * half * c - sv * half * s) * sc,
             oy - (cy + su * half * s + sv * half * c) * sc)
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def draw_pair_page(keys, title, fname, note=""):
    byk = {P.cell_key(c): c for c in C.all_cells() if not c.empty}
    sc = 92.0
    W, Hh = 1500, 300 + 470 * len(keys)
    body = [txt(16, 26, title, 14, "#111", True),
            txt(16, 44, "Each panel: the container [0, s0]^2 (thin dashed), the widened BL box "
                        f"[0, {C.A_W:.5f}]^2 (dashed orange), and the two conditioned squares H1, "
                        "H2 drawn at their clipped boxes' centres.", 10),
            txt(16, 60, "THREE cores inside each H, exactly as A140 draws them: SOLID BLACK = the "
                        "stock axis core K(a) = caselp.Box.core() that the LP prunes against; "
                        "DASHED BLACK = A135's certified EXACT axis core (same pose, larger a — "
                        "inside the FROZEN certificate schema);", 10),
            txt(16, 76, "PURPLE FILL = A132's certified polygon core K'(B) = the intersection of "
                        "Q(c,θ) over the whole box (NOT in the frozen schema — a kill that "
                        "needs it is 'LP-dead, certificate pending').", 10),
            txt(16, 92, "Thin dashed grey outlines are schematic: the square at the box's two "
                        "extremal tilts, drawn to show how much pose freedom the cell still "
                        "carries.  " + note, 10)]
    y0 = 150
    for n, key in enumerate(keys):
        (a, b) = key
        oy = y0 + n * 470
        ox = 60
        body.append(txt(ox, oy - 12, f"pair cell {a} x {b}", 11, "#111", True))
        body.append(rect(ox, oy - 4 - C.S0 * sc + C.S0 * sc, 0, 0))
        base = oy + C.S0 * sc
        body.append(rect(ox, oy, C.S0 * sc, C.S0 * sc, "none", "#90a4ae", 0.8, dash="5,4"))
        body.append(rect(ox, base - C.A_W * sc, C.A_W * sc, C.A_W * sc, "#fff3e0", "#ef6c00",
                         1.0, dash="4,3", op=0.5))
        body.append(txt(ox + 3, base - C.A_W * sc - 4, "widened BL box", 8, "#ef6c00"))
        for j, k in enumerate((a, b)):
            bx = byk[k].box
            cx, cy = 0.5 * (bx.x0 + bx.x1), 0.5 * (bx.y0 + bx.y1)
            thm = math.radians(0.5 * (bx.th0 + bx.th1))
            col = ("#0d47a1", "#00695c")[j]
            body.append(poly(sq_pts(cx, cy, thm, ox, base, sc), "#e3f2fd" if j == 0 else "#e0f2f1",
                             col, 1.6, op=0.35))
            for th in (bx.th0, bx.th1):
                body.append(poly(sq_pts(cx, cy, math.radians(th), ox, base, sc), "none",
                                 "#9e9e9e", 0.6, dash="2,3"))
            body.append(rect(ox + bx.x0 * sc, base - bx.y1 * sc, (bx.x1 - bx.x0) * sc,
                             (bx.y1 - bx.y0) * sc, "none", col, 0.9, dash="3,2"))
            k0 = bx.core()
            ka, _a0, ok = exactcore.exact_a(bx)
            pc = polycore.build(bx, max_v=16)
            body.append(poly([(ox + float(vx) * sc, base - float(vy) * sc)
                              for (vx, vy) in pc.verts], "#7e57c2", "#311b92", 1.0, op=0.34))
            tm = 2.0 * math.atan(float(k0.tm))
            body.append(poly(sq_pts(float(k0.kx), float(k0.ky), tm, ox, base, sc,
                                    half=float(k0.a)), "none", "#000", 1.5))
            if ok:
                body.append(poly(sq_pts(float(k0.kx), float(k0.ky), tm, ox, base, sc,
                                        half=float(ka)), "none", "#000", 1.2, dash="4,3"))
            lx = ox + C.S0 * sc + 24
            ly = oy + 18 + j * 96
            body.append(txt(lx, ly, f"H{j+1}  cell {k}", 10, col, True))
            body.append(txt(lx, ly + 15,
                            f"box x [{bx.x0:.4f}, {bx.x1:.4f}]  y [{bx.y0:.4f}, {bx.y1:.4f}]  "
                            f"θ [{bx.th0:.2f}°, {bx.th1:.2f}°]", 9))
            body.append(txt(lx, ly + 29, f"stock core a = {float(k0.a):.6f}   "
                                         f"A135 exact a = {float(ka):.6f}  "
                                         f"({(float(ka)/float(k0.a))**2:.3f}× area)", 9))
            body.append(txt(lx, ly + 43, f"K' : {len(pc.verts)} vertices, area {pc.area():.6f} "
                                         f"({pc.area()/(2*float(k0.a))**2:.3f}× the stock "
                                         "core's area), certified", 9, "#311b92"))
        body.append(txt(ox + C.S0 * sc + 24, oy + 220,
                        f"K'(H1) vs K'(H2) SAT depth = "
                        f"{polycore.poly_poly_depth(polycore.build(byk[a].box, max_v=16).P, polycore.build(byk[b].box, max_v=16).P):+.5f}"
                        "  (> 0 would be the P1 kill)", 9))
    open(os.path.join(FIGS, fname), "w", encoding="utf-8").write(svg(body, W, Hh))
    print("wrote figs/" + fname)


def main():
    draw_single()
    draw_pairs()
    rows = [json.loads(l) for l in
            open(os.path.join(BASE, "results", "pairs143_geom.jsonl"), encoding="utf-8")]
    alive = [r for r in rows if r["verdict"] == "ALIVE-CORE"]
    keys = [((0, 4, 0), (5, 0, 3))]
    import numpy as np
    rng = np.random.default_rng(9143)
    for i in sorted(rng.choice(len(alive), size=3, replace=False)):
        keys.append((tuple(alive[i]["pair"][0]), tuple(alive[i]["pair"][1])))
    draw_pair_page(keys, "A143 — surviving level-1 PAIR cells of the doubly-met corner-first root",
                   "pair_survivors.svg",
                   "The first panel is the TRUMP pair cell (the canary): Trump's own BL 2-crowd "
                   "at its single non-simple corner, after the D4 reduction.")


if __name__ == "__main__":
    main()
