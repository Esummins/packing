"""A165 -- the cascade figure, in A148's panel style: one panel per CASE of the tree.

Each panel draws the container at s0, the conditioned square H with its A132 polygon core K'(H),
the case's corner cover boxes (centre rectangle + the pose envelope of the box), the widened corner
boxes of Lemma K0-WIDEN, the wall guard line the row is read on with its chord vector, and the
verdict banner.  Nothing in a panel comes from an LP except the banner's tau/eta line.

    python code/fig165.py --cell l1_104 --depth 8
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import cascade165 as CS                                          # noqa: E402
import polycore as PC                                            # noqa: E402
from caselp import Box                                           # noqa: E402

PW, PH = 470, 470                       # panel size in px
PAD = 46
COLS = 3


def sc(v, s=None):
    s = s or K.S0
    return PAD + (PW - 2 * PAD) * v / s


def poly(pts, **kw):
    at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    d = " ".join("%.2f,%.2f" % (sc(x), PH - PAD - (sc(y) - PAD)) for x, y in pts)
    return '<polygon points="%s" %s/>' % (d, at)


def rect(x0, x1, y0, y1, **kw):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)


def line(x0, y0, x1, y1, **kw):
    at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" %s/>' % (
        sc(x0), PH - PAD - (sc(y0) - PAD), sc(x1), PH - PAD - (sc(y1) - PAD), at)


def text(x, y, s, size=9, fill="#222", anchor="start", weight="normal"):
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s" '
            'font-weight="%s" font-family="DejaVu Sans,Arial,sans-serif">%s</text>'
            % (x, y, size, fill, anchor, weight,
               s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")))


def box_envelope(b, n=13):
    """the union of the four vertices of Q(c, th) over the box corners and tilt endpoints --
    drawn as a convex hull for orientation only (not a certified object)."""
    pts = []
    for cx in (b.x0, b.x1):
        for cy in (b.y0, b.y1):
            for t in (b.th0, 0.5 * (b.th0 + b.th1), b.th1):
                pts += K.sq_verts(cx, cy, math.radians(t))
    # convex hull (Andrew monotone chain)
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))

    def half(P):
        H = []
        for p in P:
            while len(H) >= 2 and ((H[-1][0] - H[-2][0]) * (p[1] - H[-2][1])
                                   - (H[-1][1] - H[-2][1]) * (p[0] - H[-2][0])) <= 0:
                H.pop()
            H.append(p)
        return H
    return half(pts)[:-1] + half(pts[::-1])[:-1]


def panel(ox, oy, title, sub, H, cases, line_row, verdict, note=""):
    """one panel; `cases` = [(corner, [Box, ...])]"""
    g = ['<g transform="translate(%d,%d)">' % (ox, oy)]
    g.append('<rect x="0" y="0" width="%d" height="%d" fill="#fff" stroke="#bbb"/>' % (PW, PH))
    g.append(text(12, 18, title, 12, "#000", weight="bold"))
    g.append(text(12, 32, sub, 8, "#555"))
    g.append(rect(0, K.S0, 0, K.S0, fill="none", stroke="#000", stroke_width="1.2"))
    # the four widened corner boxes
    for c in K.CORNERS:
        X0, X1, Y0, Y1 = K.corner_cell(c)
        g.append(rect(X0, X1, Y0, Y1, fill="#f4f7ff", stroke="#8fa8dd", stroke_width="0.7",
                      stroke_dasharray="3,2"))
    # H and K'(H)
    pc = PC.build(H, n_grid=129)
    g.append(rect(H.x0, H.x1, H.y0, H.y1, fill="none", stroke="#111", stroke_width="0.8"))
    g.append(poly([(float(v[0]), float(v[1])) for v in pc.verts], fill="#ffd9a0",
                  fill_opacity="0.85", stroke="#c07b12", stroke_width="0.7"))
    g.append(text(sc(0.5 * (H.x0 + H.x1)) - 4, PH - PAD - (sc(0.5 * (H.y0 + H.y1)) - PAD),
                  "H", 10, "#7a4a00", weight="bold"))
    COL = {"TR": ("#d94a3d", "TR"), "TL": ("#2f7d32", "TL"), "BL": ("#2b5fbe", "BL"),
           "BR": ("#8a4ec4", "BR")}
    for corner, bxs in cases:
        col, lab = COL[corner]
        for k, b in enumerate(bxs):
            g.append(poly(box_envelope(b), fill=col, fill_opacity="0.14", stroke=col,
                          stroke_width="0.6"))
            g.append(rect(b.x0, b.x1, b.y0, b.y1, fill=col, fill_opacity="0.5", stroke=col,
                          stroke_width="0.8"))
            g.append(text(sc(0.5 * (b.x0 + b.x1)),
                          PH - PAD - (sc(0.5 * (b.y0 + b.y1)) - PAD),
                          "%s%s" % (lab, "ab"[k] if k < 2 else str(k)), 8, "#fff",
                          anchor="middle", weight="bold"))
    if line_row:
        from fractions import Fraction as Fr
        off = float(Fr(str(line_row["off"])))
        if line_row["orient"] == "h":
            g.append(line(0, off, K.S0, off, stroke="#e0007a", stroke_width="0.9",
                          stroke_dasharray="5,3"))
        else:
            g.append(line(off, 0, off, K.S0, stroke="#e0007a", stroke_width="0.9",
                          stroke_dasharray="5,3"))
        g.append(text(12, PH - 30, "guard line %s = %.6f   chords %s   rhs = %s"
                      % ("y" if line_row["orient"] == "h" else "x", off,
                         "+".join("%.3f" % v for v in line_row["minchords_f"]),
                         ("%.4f" % line_row["rhs_f"])), 8, "#a4005a"))
    g.append(text(12, PH - 16, verdict, 10, "#000", weight="bold"))
    if note:
        g.append(text(12, PH - 4, note, 7.5, "#555"))
    g.append("</g>")
    return "\n".join(g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cov = json.load(open(CS.cover_path(a.cell, a.depth), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    OB = {c: [Box(*b) for b in cov["covers"][c]["open"]] for c in K.CORNERS}
    rp = None
    p = os.path.join(CS.RES, "rowprod_%s.json" % CS.tag(a.cell, a.depth))
    if os.path.exists(p):
        rp = json.load(open(p, encoding="utf-8"))
    lp = {}
    p = os.path.join(CS.RES, "lp3_%s_TR.jsonl" % CS.tag(a.cell, a.depth))
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            lp[tuple(d["pair"])] = d
    geom = {}
    p = CS.geom_path(a.cell, a.depth, "TR")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            geom[tuple(d["pair"])] = d

    panels = []
    # --- panel 1: the root
    panels.append(("C0 root: %s, one box H, budget 10" % a.cell,
                   "tau = %.6f = budget exactly (A115 record).  K0-BLOCKED: every widened corner "
                   "box carries 2 meeters; M(c) = 0 at all four corners (A161 exact SAT), so H is "
                   "none of them: 11 = 8 corner meeters + H + 2" % cov["tau"],
                   [], None, "ALIVE (LP at the budget, zero slack)", ""))
    # --- panel 2: the four covers
    panels.append(("C1 the four widened-corner meeter covers",
                   "open cover boxes: " + ", ".join("%s %d" % (c, cov["covers"][c]["n_open"])
                                                    for c in K.CORNERS),
                   [(c, OB[c][:0]) for c in K.CORNERS], None,
                   "branching set of the case tree", ""))
    # --- panel 3-5: three TR pair cases with their top row
    pr = json.load(open(CS.pairs_path(a.cell, a.depth, "TR"), encoding="utf-8"))
    pairs = [tuple(q) for q in pr["pairs"]]
    show = []
    if geom:
        sortable = sorted(geom.items(), key=lambda kv: kv[1]["row_min_rhs"])
        show = [k for k, _ in sortable[:2]]
    for q in (show + pairs)[:3]:
        gg = geom.get(tuple(q))
        row = gg["rows"]["top"] if gg else None
        lprec = lp.get(tuple(q))
        vd = ("LP tau=%.4f eta=%+.4f conv=%s %s" % (
            lprec["tau"], lprec["eta"], lprec["converged"],
            "KILL" if lprec.get("kills_converged") else "alive")) if lprec else "LP not run"
        panels.append(("C2 TR pair (%d,%d): boxes {H, D, S}, budget 8" % tuple(q),
                       "top-wall row: two TR meeters each carry a certified chord >= 1, so beta = "
                       "floor(rhs) bounds the FREE squares that fully cross the top strip",
                       [("TR", [OB["TR"][q[0]], OB["TR"][q[1]]])], row, vd,
                       "|U| = %.4f vs B0 = %.4f (no area kill)" % (gg.get("area_U", -1), CS.B0)
                       if gg else ""))
    # --- panel 6: a row-killed 5-box case
    if rp and rp.get("certs"):
        ct = rp["certs"][0]
        bxs = [Box(*b) for b in ct["boxes"]]
        panels.append(("C3 %s row: (%s,%s) case pair KILLED" % (ct["wall"], *ct["corners"]),
                       "minchord sum on the line exceeds s0 = 3.877084: A144 LINE-1 violated -- a "
                       "(C) leaf with no LP",
                       [(ct["corners"][0], bxs[1:1 + len(ct["case1"])]),
                        (ct["corners"][1], bxs[1 + len(ct["case1"]):])],
                       ct["row"], "DEAD (C): chord row violated",
                       "exact rhs = %s < 0" % ct["row"]["rhs"]))

    n = len(panels)
    rows = (n + COLS - 1) // COLS
    W, Hh = COLS * (PW + 14) + 14, rows * (PH + 14) + 92
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d">' % (W, Hh, W, Hh),
           '<rect width="%d" height="%d" fill="#fafafa"/>' % (W, Hh),
           text(20, 26, "A165 -- the CASCADE case tree on %s (k0_00, level 1)" % a.cell, 16,
                "#000", weight="bold"),
           text(20, 44, "s0 = 969271/250000 = 3.877084;  widened corner pad w = %.8f "
                        "(Lemma K0-WIDEN);  (R6) gap s0 - 2(1+w) - sqrt2 = %+.6f"
                        % (cov["w"], cov["r6_gap"]), 9, "#444"),
           text(20, 58, "orange = A132 polygon core K'(H);  dashed blue = the widened corner "
                        "boxes;  filled = a case's cover box (centre rectangle) with its pose "
                        "envelope;  magenta dashed = the guard line the chord row is read on", 8,
                "#555")]
    for i, (t, s, cases, row, vd, note) in enumerate(panels):
        ox = 14 + (i % COLS) * (PW + 14)
        oy = 76 + (i // COLS) * (PH + 14)
        out.append(panel(ox, oy, t, s, H, cases, row, vd, note))
    out.append(text(20, Hh - 8, "generated by attempts/A165-cascade-l1_104/code/fig165.py from "
                                "results/{cover,pairs,geom,rowprod,lp3}_*.json", 7.5, "#888"))
    out.append("</svg>")
    p = a.out or os.path.join(K.BASE, "figs", "cascade_%s.svg" % a.cell)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", p, "(%d panels)" % n, flush=True)


if __name__ == "__main__":
    main()
