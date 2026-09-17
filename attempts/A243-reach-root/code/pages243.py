"""A243 -- the campaign page: the type-F (theta, delta) plane with the closed-form curves (TILT-MIN's domain, the REACH
contact curves R = s - 2, the LEVER curve delta = sin theta + cos^3 theta), a survivor crowd drawn with its off-wall
holder, and the fibre of one summary cell with the role cores.  Self-contained SVG, no plotting library.
`docs/residue_map/campaigns/A243-reach-root/reach_domain.svg`.
"""
import json
import math
import os
import sys

from shapely import wkt

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
OUT = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A243-reach-root")
sys.path.insert(0, HERE)
import leaves243 as L                                                   # noqa: E402

CSS = ("<style>text{font-family:Helvetica,Arial,sans-serif}.t{font-size:11px;fill:#111}"
       ".s{font-size:9px;fill:#555}.h{font-size:12.5px;fill:#000}</style>")
PW, PH, PAD = 325, 300, 40                                              # panel width / plot height / margin


def _esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _txt(x, y, lines, cls="s", dy=11):
    return "\n".join('<text class="%s" x="%d" y="%d">%s</text>' % (cls, x, y + i * dy, _esc(ln))
                     for i, ln in enumerate(lines))


def _sq(pts, X, Y, col, fill="none", width=1.2, dash=""):
    d = ' stroke-dasharray="%s"' % dash if dash else ""
    return '<polygon points="%s" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="%.1f"%s/>' % (
        " ".join("%.1f,%.1f" % (X(u), Y(v)) for u, v in pts), fill, col, width, d)


def contact_curve(s):
    """delta(theta) with R(theta, delta) = s - 2 inside TILT-MIN's domain (A239 s.1: the contact curve)."""
    pts = []
    for k in range(1, 900):
        th = k / 10.0
        t = th * L.DEG
        den = 1 - math.tan(t)
        if abs(den) < 1e-9:
            continue
        d = (s - 2 - math.cos(t) - math.sin(t) - math.sin(t) * math.tan(t)) / den
        if math.sin(t) <= d < 1:
            pts.append((th, d))
    return pts


def panel_plane(x0, y0, s_list):
    def X(th): return x0 + PAD + th / 90.0 * (PW - 2 * PAD)
    def Y(d): return y0 + 50 + PH - PAD - d * (PH - 2 * PAD)
    p = [_txt(x0 + 4, y0 + 14, ["(A) the type-F summary plane (theta, delta)"], "h"),
         _txt(x0 + 4, y0 + 27, ["shaded: TILT-MIN's domain sin theta <= delta < 1 (A237) -- where a",
                                "flat-meeter crowd lives; curves: REACH R = s - 2 (contact), LEVER"]),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000"/>' % (X(0), Y(1), PW - 2 * PAD, PH - 2 * PAD)]
    dom = [(th, math.sin(th * L.DEG)) for th in range(0, 91)] + [(90, 1.0), (0, 1.0)]
    p.append('<polygon points="%s" fill="#e8f0fb" stroke="#36c" stroke-width="0.8"/>' % " ".join("%.1f,%.1f" % (X(a), Y(b)) for a, b in dom))
    for s, col in zip(s_list, ("#c33", "#e63", "#d93", "#9a0")):
        pts = contact_curve(s)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (
            " ".join("%.1f,%.1f" % (X(a), Y(b)) for a, b in pts), col))
        a, b = pts[len(pts) // 2]
        p.append('<text class="s" x="%.1f" y="%.1f" fill="%s">s = %.3f</text>' % (X(a) + 3, Y(b) - 2, col, s))
    lev = [(th, L.lever_delta(th)) for th in range(0, 91) if L.lever_delta(th) < 1]
    p.append('<polyline points="%s" fill="none" stroke="#080" stroke-width="1.8" stroke-dasharray="4 2"/>' % " ".join(
        "%.1f,%.1f" % (X(a), Y(b)) for a, b in lev))
    p.append('<text class="s" x="%.1f" y="%.1f" fill="#080">LEVER (theta &gt;= 57.07)</text>' % (X(52), Y(0.96)))
    for th in (0, 30, 60, 90):
        p.append('<text class="s" x="%.1f" y="%.1f">%d</text>' % (X(th) - 5, Y(0) + 12, th))
    for d in (0, 0.5, 1):
        p.append('<text class="s" x="%.1f" y="%.1f">%.1f</text>' % (X(0) - 22, Y(d) + 3, d))
    p.append(_txt(int(X(22)), int(Y(0)) + 24, ["theta (deg): the partner's tilt; delta: the flat meeter's offset"]))
    p.append(_txt(x0 + 4, y0 + 50 + PH + 8, ["Below a REACH curve two mode-(a) crowds do not span the wall in contact",
                                             "(the gap < 1: a third member juts); on the LEVER curve the partner balances",
                                             "under wall + corner + top-vertex contacts, and R > 2 there: side > 4.017.",
                                             "Neither is a cell kill (notes/reach243.md s.3): the first needs the holder",
                                             "on the wall, the second a fixed contact structure."]))
    return "\n".join(p)


def panel_survivor(x0, y0):
    k = (PW - 2 * PAD) / 2.6
    def X(u): return x0 + PAD + u * k
    def Y(v): return y0 + 50 + PH - PAD - v * k
    d = math.sin(20 * L.DEG) + 0.02
    A, B = L.pair_F(20.0, d)
    _, C, f, _, ylow = L.holder_witness(delta=d, phi_deg=95.0)
    assert L.disjoint(B, C) and L.disjoint(A, C, tol=1e-9)
    p = [_txt(x0 + 4, y0 + 14, ["(B) a survivor crowd and its off-wall holder"], "h"),
         _txt(x0 + 4, y0 + 27, ["the window crowd (theta = 20, delta = %.3f; below every REACH curve at" % d,
                                "s-hat) with C holding A toward the corner, force (%.2f, %.2f), floating" % (f[0], f[1])]),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000"/>' % (X(0), Y(2.6), 2.6 * k, 2.6 * k),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fde8e8" stroke="#c33" stroke-dasharray="3 2"/>' % (X(0), Y(1), k, k)]
    p.append(_sq(L.verts(A), X, Y, "#1a7", "#1a7"))
    p.append(_sq(L.verts(B), X, Y, "#a51", "#a51"))
    p.append(_sq(L.verts(C), X, Y, "#36c", "#36c", dash="4 2"))
    px, py = 1 + d, 1.0
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c00" stroke-width="2"/>' % (X(px), Y(py), X(px + 0.4 * f[0]), Y(py + 0.4 * f[1])))
    for nm, P in (("A", A), ("B", B), ("C", C)):
        p.append('<text class="t" x="%.1f" y="%.1f">%s</text>' % (X(P[0]) - 4, Y(P[1]) + 4, nm))
    S = L.summary(A, B)
    p.append(_txt(x0 + 4, y0 + 50 + PH + 8, ["Summary (r_u, r_v, d_1, d_2) = (%.3f, %.3f, %.3f, %.3f)." % S,
                                             "C's lowest vertex is at v = %.2f: Lemma HOLD's along-wall holder is not a" % ylow,
                                             "wall member, and CHAIN's path from C to a far wall need not run along the",
                                             "floor -- so 'reaches + bridges must span the wall' has no proof (R1)."]))
    return "\n".join(p)


def panel_fibre(x0, y0, rec):
    k = (PW - 2 * PAD) / 2.6
    def X(u): return x0 + PAD + u * k
    def Y(v): return y0 + 50 + PH - PAD - v * k
    p = [_txt(x0 + 4, y0 + 14, ["(C) one summary cell's FIBRE (h = %.2f) and its cores" % rec["h"]], "h"),
         _txt(x0 + 4, y0 + 27, ["%d sampled crowds with the same summary to within h; the two role" % rec["n"],
                                "cores (dark) = intersections of bodies: areas %.2f / %.2f" % (rec["core_deep_area"], rec["core_shallow_area"])]),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000"/>' % (X(0), Y(2.6), 2.6 * k, 2.6 * k),
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fde8e8" stroke="#c33" stroke-dasharray="3 2"/>' % (X(0), Y(1), k, k)]
    for A, B in rec["sample"]:
        p.append(_sq(L.verts(tuple(A)), X, Y, "#1a7", width=0.7))
        p.append(_sq(L.verts(tuple(B)), X, Y, "#a51", width=0.7))
    for key, col in (("core_deep_wkt", "#063"), ("core_shallow_wkt", "#630")):
        if rec.get(key):
            g = wkt.loads(rec[key])
            if not g.is_empty:
                p.append(_sq(list(g.exterior.coords), X, Y, col, col, width=1.0))
    p.append(_txt(x0 + 4, y0 + 50 + PH + 8, ["The core is what the no-room leaf may subtract (A172's K', A242 s.2).  This",
                                             "cell is the window crowd's: its fibre is THIN and the cores stay large.  A",
                                             "GENERIC cell's fibre is fat: every occupied bin at h = 0.2 has an EMPTY",
                                             "core (results/reach243.md s.5) -- R3 reads nothing until the cell is a pose box."]))
    return "\n".join(p)


def main():
    os.makedirs(OUT, exist_ok=True)
    recs = [json.loads(l) for l in open(os.path.join(BASE, "results", "reach243.jsonl"), encoding="utf-8")]
    fib = [r for r in recs if r["item"] == "fibre" and r["h"] == 0.05][0]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1010" height="470" viewBox="0 0 1010 470">', CSS,
           '<rect width="1010" height="470" fill="#fff"/>',
           _txt(10, 16, ["A243 -- the reach-summary root: the closed-form leaves are curves in the type-F plane, not cell kills; "
                         "a summary cell's fibre keeps its cores only when it is a pose box"], "h"),
           panel_plane(10, 24, (3.82, L.SHAT, 3.95, 4.0)), panel_survivor(345, 24), panel_fibre(680, 24, fib),
           _txt(10, 462, ["Sources: A239 rings_below_4.md s.1, s.3 (REACH, LEVER); A237 pocket_waste.md s.1 (TILT-MIN); A218 k0_count.md s.3 "
                          "(HOLD); A233 local_lock.md s.3 (RADIAL, CHAIN); A242 crowd242.md s.2 (cores); results/reach243.jsonl."]),
           '</svg>']
    with open(os.path.join(OUT, "reach_domain.svg"), "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("wrote", os.path.join(OUT, "reach_domain.svg"))


if __name__ == "__main__":
    main()
