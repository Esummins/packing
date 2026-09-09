"""A173 -- DRAW the lonely clip.  Style reference: docs/residue_map/gen_a57_lp.py (PI's rules:
every mark is a real object, and every panel carries a note saying what it IS).

  * `--node <cell> <path>`  a BEFORE / AFTER page for one S1 node:
        - the container and both roles' K' (H solid; K'(D) DASHED before, SOLID after, both drawn
          on both panels so the growth is visible);
        - D's surviving centre pieces as thin rects;
        - the centres the lonely clip REMOVED, hatched red;
        - the hypothesis square at the centre of D's box at mid tilt, with the two extremal-tilt
          outlines of the same centre;
        - a row of per-tilt-sub-bin insets of D's centre window (every BEFORE piece red-hatched,
          every AFTER piece painted blue on top: blue survives, the hatch still showing was
          removed), which is the only exact per-bin view;
        - a note on each panel saying what it is.
    -> docs/residue_map/lonely_clip_S1.svg
  * `--gallery`             a one-page gallery of the ten largest-effect nodes -> figs/.

READ-ONLY on A168 (the trees are read, nothing is written there).
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figs"))
sys.path.insert(0, os.path.join(ATT, "A171-multibox-invariant", "code"))

import multibox as MB                                          # noqa: E402
from caselp import Box                                         # noqa: E402

S0 = float(MB.S_RAT)
PAL = {"H": "#1f77b4", "D": "#d62728", "S": "#2ca02c", "B1": "#9467bd"}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="DejaVu Sans,Arial,sans-serif" '
            f'font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>')


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


HATCH = ('<pattern id="hat" width="6" height="6" patternTransform="rotate(45)" '
         'patternUnits="userSpaceOnUse">'
         '<line x1="0" y1="0" x2="0" y2="6" stroke="#d62728" stroke-width="1.6"/></pattern>')


# ==================================================================== the two runs
def build(boxes, corners, nsub=4, refine=1, max_iter=6, lonely_refine=1):
    nd = MB.Node(dict(boxes), name="A173")
    nd.normalise(nsub=nsub, refine=refine, max_iter=max_iter, corners=corners,
                 lonely_refine=lonely_refine)
    nd.assert_invariant(raise_on_fail=False, sample=1200)
    return nd


def node_boxes(cell, path):
    T = json.load(open(os.path.join(ATT, "A168-cascade-fable", "results",
                                    "tree_%s.json" % cell), encoding="utf-8"))
    nd = T["nodes"][path]
    return {k: Box(*r["box"]) for k, r in nd["roles"].items()}, nd.get("verdict")


# ==================================================================== the page
def page(cell, path, out, nsub=4, refine=1, max_iter=6, lonely_refine=1):
    boxes, verdict = node_boxes(cell, path)
    base = build(boxes, None, nsub, refine, max_iter, lonely_refine)
    lone = build(boxes, {"D": ("TR", MB.C_WIDEN)}, nsub, refine, max_iter, lonely_refine)

    PAD, SC = 40.0, 150.0
    PW = S0 * SC
    W = PAD * 2 + PW * 2 + 40 + 300
    INS_H = 150.0
    H = PAD * 2 + PW + 44 + INS_H + 40

    def X(x, ox):
        return ox + x * SC

    def Y(y):
        return PAD + 26 + (S0 - y) * SC

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{int(H)}" '
         f'viewBox="0 0 {int(W)} {int(H)}">',
         f'<rect width="{int(W)}" height="{int(H)}" fill="#ffffff"/>', f'<defs>{HATCH}</defs>',
         text(PAD, PAD - 12,
              f"A173 the LONELY CLIP on {cell} {path} (A168 S1: H + D, D the first TR meeter, "
              f"c = 1 + w = {float(MB.C_WIDEN):.7f}) -- {verdict}", 13, bold=True)]

    def panel(ox, nd, other, title, note, dash_own):
        out = [f'<rect x="{X(0, ox):.2f}" y="{Y(S0):.2f}" width="{PW:.2f}" height="{PW:.2f}" '
               f'fill="none" stroke="#000" stroke-width="2"/>',
               text(ox, PAD + 14, title, 12, bold=True)]
        # the removed centres, hatched (BEFORE minus AFTER, projected over all tilt sub-bins)
        if other is not None:
            for (_bn, r) in other["D"].pieces:
                x0, x1, y0, y1 = (float(v) for v in r)
                out.append(f'<rect x="{X(x0, ox):.2f}" y="{Y(y1):.2f}" '
                           f'width="{(x1 - x0) * SC:.2f}" height="{(y1 - y0) * SC:.2f}" '
                           f'fill="url(#hat)" fill-opacity="0.85" stroke="none"/>')
        for k, mb in nd.boxes.items():
            col = PAL.get(k, "#666")
            for (_bn, r) in mb.pieces:
                x0, x1, y0, y1 = (float(v) for v in r)
                out.append(f'<rect x="{X(x0, ox):.2f}" y="{Y(y1):.2f}" '
                           f'width="{(x1 - x0) * SC:.2f}" height="{(y1 - y0) * SC:.2f}" '
                           f'fill="#ffffff" fill-opacity="0.95" stroke="{col}" '
                           f'stroke-width="0.5"/>')
        # K' of every box: own solid/dashed per the caller, the other run's K'(D) as the twin
        for k, mb in nd.boxes.items():
            col = PAL.get(k, "#666")
            pts = " ".join(f"{X(float(a), ox):.2f},{Y(float(b)):.2f}" for (a, b) in mb.pc.verts)
            da = ' stroke-dasharray="5,3"' if (k == "D" and dash_own) else ""
            out.append(f'<polygon points="{pts}" fill="{col}" fill-opacity="0.35" '
                       f'stroke="{col}" stroke-width="1.6"{da}/>')
        if other is not None:
            pts = " ".join(f"{X(float(a), ox):.2f},{Y(float(b)):.2f}"
                           for (a, b) in other["D"].pc.verts)
            out.append(f'<polygon points="{pts}" fill="none" stroke="#d62728" '
                       f'stroke-width="1.2" stroke-dasharray="5,3" stroke-opacity="0.9"/>')
        # the hypothesis squares: centre of D's box at mid tilt (solid) and at the two extremes
        mb = nd.boxes["D"]
        b0 = mb.box0
        cx, cy = 0.5 * (b0.x0 + b0.x1), 0.5 * (b0.y0 + b0.y1)
        for (th, wdt, dsh) in ((0.5 * (b0.th0 + b0.th1), 1.7, ""),
                               (b0.th0, 0.8, ' stroke-dasharray="3,2"'),
                               (b0.th1, 0.8, ' stroke-dasharray="3,2"')):
            pts = " ".join(f"{X(x, ox):.2f},{Y(y):.2f}" for (x, y) in sq(cx, cy, math.radians(th)))
            out.append(f'<polygon points="{pts}" fill="none" stroke="#111" '
                       f'stroke-width="{wdt}"{dsh}/>')
        for i, ln in enumerate(note):
            out.append(text(ox, Y(0) + 16 + 13 * i, ln, 9, "#444"))
        return out

    o += panel(PAD, base, None,
               "BEFORE -- A171/A172 normalise (container + mutual clip only)",
               ["every thin rect IS a surviving centre piece of that box; K'(D) DASHED, K'(H) solid",
                "black squares ARE poses: D's box centre at mid tilt (thick) and at both tilt ends",
                f"kept D {base.boxes['D'].kept_fraction():.4f}  H {base.boxes['H'].kept_fraction():.4f}"
                f"   K'(D) area {base.boxes['D'].pc.area():.6f}"],
               dash_own=True)
    ox2 = PAD + PW + 40
    o += panel(ox2, lone, base.boxes,
               "AFTER -- the same node with the LONELY CLIP on D (TR, c = 1 + w)",
               ["red hatch = centres that the BEFORE run kept and Theorem B has now removed",
                "(projection over every tilt sub-bin; the exact per-bin picture is the strip below)",
                f"kept D {lone.boxes['D'].kept_fraction():.4f}  H {lone.boxes['H'].kept_fraction():.4f}"
                f"   K'(D) area {lone.boxes['D'].pc.area():.6f} (solid; dashed = BEFORE)"],
               dash_own=False)

    # ------------------------------------------------ per-tilt-sub-bin insets (exact per bin)
    b0 = base.boxes["D"].box0
    refs = MB.sub_bins(MB.t_lo(b0.th0), MB.t_hi(b0.th1), nsub)
    iy = PAD + 26 + PW + 58
    iw = min(190.0, (W - 2 * PAD - 300) / nsub - 14)
    x0b, x1b = float(MB.PIN.outer_rect(b0)[0]), float(MB.PIN.outer_rect(b0)[1])
    y0b, y1b = float(MB.PIN.outer_rect(b0)[2]), float(MB.PIN.outer_rect(b0)[3])
    spanx, spany = max(x1b - x0b, 1e-9), max(y1b - y0b, 1e-9)
    o.append(text(PAD, iy - 12, "D's centre window per TILT SUB-BIN of its box -- every BEFORE piece "
                                "of that bin is drawn red-hatched and every surviving AFTER piece is "
                                "painted blue over it, so BLUE IS WHAT SURVIVES and the red hatch "
                                "left showing IS what Theorem B removed.  Exact per bin: no "
                                "projection.", 10, bold=True))
    for i, (t0, t1) in enumerate(refs):
        ox = PAD + i * (iw + 14)
        sx, sy = iw / spanx, INS_H / spany

        def IX(x, ox=ox):
            return ox + (x - x0b) * sx

        def IY(y):
            return iy + (y1b - y) * sy
        o.append(f'<rect x="{ox:.1f}" y="{iy:.1f}" width="{iw:.1f}" height="{INS_H:.1f}" '
                 f'fill="#fafafa" stroke="#bbb" stroke-width="0.8"/>')
        for (bn, r) in base.boxes["D"].pieces:
            if not (bn.t0 >= t0 and bn.t1 <= t1):
                continue
            a, b, cc, dd = (float(v) for v in r)
            o.append(f'<rect x="{IX(a):.2f}" y="{IY(dd):.2f}" width="{(b - a) * sx:.2f}" '
                     f'height="{(dd - cc) * sy:.2f}" fill="url(#hat)" fill-opacity="0.7" '
                     f'stroke="#999" stroke-width="0.5"/>')
        for (bn, r) in lone.boxes["D"].pieces:
            if not (bn.t0 >= t0 and bn.t1 <= t1):
                continue
            a, b, cc, dd = (float(v) for v in r)
            o.append(f'<rect x="{IX(a):.2f}" y="{IY(dd):.2f}" width="{(b - a) * sx:.2f}" '
                     f'height="{(dd - cc) * sy:.2f}" fill="#cfe3f5" fill-opacity="0.95" '
                     f'stroke="#1f77b4" stroke-width="0.5"/>')
        o.append(text(ox, iy + INS_H + 12,
                      f"tilt {MB.deg_of_t(t0):.2f}-{MB.deg_of_t(t1):.2f} deg", 9, "#333"))
    # ------------------------------------------------ the numbers
    tx = PAD + 2 * PW + 60
    ty = PAD + 20
    rows = [("", "BEFORE", "AFTER")]
    for k in base.names:
        rows.append((f"kept {k}", f"{base.boxes[k].kept_fraction():.6f}",
                     f"{lone.boxes[k].kept_fraction():.6f}"))
    for k in base.names:
        rows.append((f"K'({k}) area", f"{base.boxes[k].pc.area():.6f}",
                     f"{lone.boxes[k].pc.area():.6f}"))
    for k in base.names:
        rows.append((f"axis a({k})", f"{float(base.boxes[k].core.a):.6f}",
                     f"{float(lone.boxes[k].core.a):.6f}"))
    rows.append(("passes", str(base.stats["passes"]), str(lone.stats["passes"])))
    rows.append(("pieces D", str(len(base.boxes["D"].pieces)), str(len(lone.boxes["D"].pieces))))
    rows.append(("invariant", "HOLDS" if base.report["ok"] else "FAILS",
                 "HOLDS" if lone.report["ok"] else "FAILS"))
    rows.append(("lonely area removed", "-",
                 f"{float(getattr(lone.boxes['D'], 'lonely_removed', 0.0)):.8f}"))
    for (a, b, c) in rows:
        o.append(text(tx, ty, a, 10, "#111", bold=(a == "")))
        o.append(text(tx + 120, ty, b, 10, "#666", anchor="end"))
        o.append(text(tx + 200, ty, c, 10, "#111", anchor="end"))
        ty += 15
    ty += 10
    for ln in ("WHAT THIS IS: A169 Theorem B (sideband.md sec 3,",
               "row R3 sec 6) says a corner meeter pose with no",
               "possible SECOND meeter of the widened corner box",
               "cannot occur in a K0-BLOCKED packing.  A168 used",
               "it only to kill a role all of whose poses are",
               "lonely.  Here it CLIPS: every centre slab and tilt",
               "sub-bin certified lonely is removed, K'(D) is",
               "rebuilt from the survivors (larger), and the",
               "cascade carries that into H.", "",
               "SOUNDNESS: the box test is a SUFFICIENT condition",
               "for lonely, so only certified-lonely slabs go; the",
               "clause grid keeps A168's [S] grade, clause (P) is",
               "exact (A131 rational clip vs the pressed square)."):
        o.append(text(tx, ty, ln, 9, "#444"))
        ty += 12
    o.append("</svg>")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(o))
    print("wrote", out, flush=True)
    return dict(cell=cell, path=path,
                kept_before={k: base.boxes[k].kept_fraction() for k in base.names},
                kept_after={k: lone.boxes[k].kept_fraction() for k in base.names})


# ==================================================================== the gallery
def gallery(rows, out, ncol=5):
    """one page, ten panels: D's centre window per node, BEFORE grey / AFTER blue / removed hatch,
    projected over the tilt sub-bins (each panel says so)."""
    CW, CH = 250.0, 210.0
    W = 30 + ncol * (CW + 16)
    H = 74 + ((len(rows) + ncol - 1) // ncol) * (CH + 44)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{int(H)}" '
         f'viewBox="0 0 {int(W)} {int(H)}">',
         f'<rect width="{int(W)}" height="{int(H)}" fill="#fff"/>', f'<defs>{HATCH}</defs>',
         text(20, 26, "A173 -- the ten A168 nodes whose D loses the most to the LONELY CLIP",
              14, bold=True),
         text(20, 44, "each panel: D's centre window.  Every BEFORE piece is drawn red-hatched and "
                      "every surviving AFTER piece is painted blue over it, so BLUE IS WHAT SURVIVES "
                      "and the red hatch left showing IS what Theorem B removed.  Projection over the "
                      "tilt sub-bins (the exact per-bin view is lonely_clip_S1.svg).", 10, "#444")]
    for i, r in enumerate(rows):
        cx = 20 + (i % ncol) * (CW + 16)
        cy = 74 + (i // ncol) * (CH + 44)
        boxes, _v = node_boxes(r["cell"], r["path"])
        base = build(boxes, None)
        try:
            lone = build(boxes, {"D": ("TR", MB.C_WIDEN)})
        except MB.EmptyBox:
            lone = None                       # D lost EVERY pose: the node is DEAD by row R3
        b0 = base.boxes["D"].box0
        rr = MB.PIN.outer_rect(b0)
        x0b, x1b, y0b, y1b = (float(v) for v in rr)
        sx, sy = CW / max(x1b - x0b, 1e-9), CH / max(y1b - y0b, 1e-9)
        o.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{CW:.1f}" height="{CH:.1f}" '
                 f'fill="#fafafa" stroke="#bbb" stroke-width="0.8"/>')
        for (nd, fill, stk, op) in ((base, "url(#hat)", "#999", 0.7),
                                    (lone, "#cfe3f5", "#1f77b4", 0.95)):
            if nd is None:
                continue
            for (_bn, q) in nd.boxes["D"].pieces:
                a, b, c, d = (float(v) for v in q)
                o.append(f'<rect x="{cx + (a - x0b) * sx:.2f}" y="{cy + (y1b - d) * sy:.2f}" '
                         f'width="{(b - a) * sx:.2f}" height="{(d - c) * sy:.2f}" fill="{fill}" '
                         f'fill-opacity="{op}" stroke="{stk}" stroke-width="0.4"/>')
        o.append(text(cx, cy + CH + 14, f"{r['cell']} {r['step']} {r['path']}", 9, "#111", bold=True))
        if lone is None:
            o.append(text(cx + CW / 2, cy + CH / 2, "D EMPTY -- node DEAD by row R3", 12,
                          "#d62728", bold=True, anchor="middle"))
        o.append(text(cx, cy + CH + 26,
                      (f"D kept {r['kept_before']:.4f} -> KILL (EmptyBox)" if lone is None else
                       f"D kept {r['kept_before']:.4f} -> {r['kept_after']:.4f}  "
                       f"(x{r['kept_before'] / max(r['kept_after'], 1e-12):.1f} smaller)"),
                      9, "#444"))
        o.append(text(cx, cy + CH + 38,
                      f"K'(D) {r['k_before']:.4f} -> {r['k_after']:.4f}   H kept "
                      f"{r['h_before']:.4f} -> {r['h_after']:.4f}", 9, "#444"))
    o.append("</svg>")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(o))
    print("wrote", out, flush=True)


def top_rows(n=10, step="S1"):
    seen = {}
    for fn in sorted(os.listdir(RES)):
        if not fn.startswith("measure173") or not fn.endswith(".jsonl"):
            continue
        for line in open(os.path.join(RES, fn), encoding="utf-8"):
            if line.strip():
                q = json.loads(line)
                seen[(q["cell"], q["step"], q["path"])] = q      # DEDUPE: shards may overlap
    rows = []
    for r in seen.values():
        b, l = r.get("base", {}), r.get("lonely", {})
        if b.get("kill") or "kept" not in b:
            continue
        if step and r["step"] != step:
            continue
        if l.get("kill"):
            ka, ha, kk, hh = 0.0, 0.0, 0.0, 0.0
        else:
            ka, ha = l["kept"]["D"], l["kept"]["H"]
            kk, hh = l["k_area"]["D"], l["k_area"]["H"]
        rows.append(dict(cell=r["cell"], step=r["step"], path=r["path"],
                         kept_before=b["kept"]["D"], kept_after=ka,
                         k_before=b["k_area"]["D"], k_after=kk,
                         h_before=b["kept"]["H"], h_after=ha,
                         loss=b["kept"]["D"] - ka))
    rows.sort(key=lambda r: -r["loss"])
    return rows[:n]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", nargs=2, default=None, metavar=("CELL", "PATH"))
    ap.add_argument("--auto", action="store_true", help="pick the worst S1 node from the results")
    ap.add_argument("--gallery", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "residue_map", "lonely_clip_S1.svg"))
    a = ap.parse_args()
    os.makedirs(FIGS, exist_ok=True)
    if a.auto:
        t = [r for r in top_rows(60, "S1") if r["kept_after"] > 0.0]   # the page needs an AFTER
        if not t:
            sys.exit("no surviving S1 results yet")
        a.node = [t[0]["cell"], t[0]["path"]]
        print("worst S1 node:", a.node, "D kept", t[0]["kept_before"], "->", t[0]["kept_after"])
    if a.node:
        page(a.node[0], a.node[1], a.out)
    if a.gallery:
        gallery(top_rows(10, "S1"), os.path.join(FIGS, "lonely_clip_gallery.svg"))
