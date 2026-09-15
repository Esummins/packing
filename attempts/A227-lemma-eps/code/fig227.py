"""A227 -- the pages: (A) the PI's Y0865 case -- F1's forced cell BL(1,0) with its four wedge polygons (exact, over
F1's hull box), the corner zones of the pin/wall-backed sides, and H's square entering the right-upper wedge;
(B) the pinwheel of a pure rotation; (C) an offset.  Every panel carries a geometry check computed here.

    python fig227.py     -> docs/residue_map/campaigns/A227-lemma-eps/eps227_Y0865.svg, eps227_pinwheel.svg
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import epsscan227 as ES                                        # noqa: E402  (sets the paths, loads eps227)
import eps227 as E                                             # noqa: E402

OUT = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A227-lemma-eps")
COL = dict(L="#1565c0", R="#c62828", B="#2e7d32", T="#ef6c00")


def sq_corners(cx, cy, deg):
    th = math.radians(deg)
    e, f = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
    return [(cx + a * e[0] + b * f[0], cy + a * e[1] + b * f[1]) for a, b in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


class Panel:
    def __init__(self, ox, oy, S, x0, y0, x1, y1):
        self.ox, self.oy, self.S, self.x0, self.y0, self.x1, self.y1 = ox, oy, S, x0, y0, x1, y1
        self.g = []

    def P(self, x, y):
        return (self.ox + (float(x) - self.x0) * self.S, self.oy + (self.y1 - float(y)) * self.S)

    def poly(self, pts, fill, stroke, sw=1, op=1.0, dash=None):
        s = " ".join("%.2f,%.2f" % self.P(x, y) for x, y in pts)
        self.g.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" fill-opacity="%s"%s/>' % (
            s, fill, stroke, sw, op, ' stroke-dasharray="%s"' % dash if dash else ""))

    def rect(self, r, **kw):
        x0, x1, y0, y1 = (float(v) for v in r)
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)

    def text(self, x, y, s, size=11, fill="#222", anchor="start"):
        px, py = self.P(x, y)
        self.g.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s">%s</text>' % (px, py, size, fill, anchor, s))

    def note(self, lines, y, size=11):
        for i, ln in enumerate(lines):
            self.g.append('<text x="%.1f" y="%.1f" font-size="%d" fill="#333">%s</text>' % (self.ox, y + 14 * i, size, ln))


def draw_cell(pn, box, C, back, label):
    """the wedge polygons of (box, C) coloured by side, the targets outlined, F's core rectangle."""
    tg, info = E.targets(box, C, back)
    polys = E.wedge_polys(box, C)
    E.assign(polys, C)
    pn.rect(C, fill="#fafafa", stroke="#000", sw=1.2)
    for P in polys:
        pn.poly(P["poly"], fill=COL.get(P["side"], "#999"), stroke="none", op=0.45)
    w = {k: Fr(v) for k, v in info["depths"].items()}
    Kr = (C[0] + w["L"], C[1] - w["R"], C[2] + w["B"], C[3] - w["T"])
    pn.rect(Kr, fill="none", stroke="#555", sw=0.8, dash="3,2")
    for nm, T in tg:
        pn.rect(T, fill="none", stroke="#000" if nm.startswith("zone") else "#7b1fa2", sw=1.4 if nm.startswith("zone") else 0.9,
                dash=None if nm.startswith("zone") else "2,2")
    return tg, info, polys


def page_Y0865():
    doc = json.load(open(os.path.join(ES.SC.CERTS, "coarsetree211_k5_16_interior_Y0865.json"), encoding="utf-8"))
    node = [n for n in doc["runs"]["g1_page"]["nodes"] if n["label"] == "R.2.3.1.p1.1.2.2.1.1.1x"][0]
    pg = ES.Page(doc, node, "g1")
    C = E.S.slot_cell(pg, "BL(1,0)")
    back = E.backing(pg, C)
    box = E.hull_box(pg, "F1")
    W, H = 1250, 640
    pn = Panel(40, 70, 420, 0.75, -0.15, 2.45, 1.5)
    # container wall, pin core, F1's box
    pn.poly([(0.75, -0.15), (2.45, -0.15), (2.45, 0), (0.75, 0)], fill="#ddd", stroke="none")
    K = E.pin_core(pg.roles["P0"])
    pn.rect(K, fill="#e0e0e0", stroke="#777", sw=0.8)
    pn.text(0.78, 0.5, "pin BL(0,0) core", 10, "#555")
    tg, info, polys = draw_cell(pn, box, C, back, "BL(1,0)")
    b = pg.roles["F1"]
    pn.rect(b[:4], fill="#fff59d", stroke="#f9a825", sw=1)
    pn.text(float(b[0]) - 0.02, float(b[3]) + 0.03, "F1 centre box", 9, "#f9a825")
    # H at its recorded pose (snap_rule.md s.3): (2.17, 1.475, 58 deg)
    hc = sq_corners(2.17, 1.475, 58.0)
    pn.poly(hc, fill="#90caf9", stroke="#0d47a1", sw=1.2, op=0.5)
    pn.text(2.05, 1.42, "H (2.17, 1.475, 58 deg)", 10, "#0d47a1")
    # geometry check: the edge of H crossing x = 2
    cross = []
    for i in range(4):
        (ax, ay), (bx, by) = hc[i], hc[(i + 1) % 4]
        if (ax - 2.0) * (bx - 2.0) < 0:
            cross.append(ay + (by - ay) * (2.0 - ax) / (bx - ax))
    yc = min(cross)
    px, py = pn.P(2.0, yc)
    pn.g.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#d50000"/>' % (px, py))
    pn.text(2.03, yc - 0.06, "H's edge crosses x = 2 at y = %.3f" % yc, 10, "#d50000")
    pn.text(1.05, 1.42, "right-upper wedge", 10, COL["R"])
    inR = [nm for nm, T in tg if T[0] <= Fr(2) <= T[1] and T[2] <= Fr(str(round(yc, 6))) <= T[3]]
    notes = ["(A) Y0865 node R.2.3.1.p1.1.2.2.1.1.1x, F1 near-simple at BL(1,0): the cell C = B_p+ = [%s] and the four wedge families of F1's hull box"
             % ", ".join("%.4f" % float(v) for v in C),
             "    (blue = left family, red = right, green = bottom, orange = top; dashed grey = K'_rect, F1's certified core; dashed purple = free-side targets; black = corner zones of the backed sides).",
             "    backing: %s; depths w_L %s w_R %s w_B %s w_T %s; GATE %s.  Targets: %s." % (
                 ", ".join("%s=%s" % (s, back[s][0]) for s in E.SIDES), info["depths"]["L"], info["depths"]["R"], info["depths"]["B"], info["depths"]["T"], info["gate"],
                 "; ".join("%s [%s]" % (nm, ", ".join("%.4f" % float(v) for v in T)) for nm, T in tg)),
             "    GEOMETRY CHECK: H's lowest crossing of x = 2 is y = %.4f (snap_rule.md: 0.992); it lies in target(s) %s -- so H is NOT struck, every other free role is: no kill, the wedge is handed to Rule NS."
             % (yc, inR)]
    pn.note(notes, 560, 10)
    body = "\n".join(pn.g)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif">\n<rect width="%d" height="%d" fill="white"/>\n'
           '<text x="12" y="22" font-size="14" font-weight="bold" fill="#222">A227 -- Lemma EPS on the PI\'s Y0865 case: F1\'s cell BL(1,0) with its four wedges; H\'s edge enters the right-upper wedge (docs/proofs/lemma_eps.md)</text>\n%s\n</svg>\n'
           % (W, H, W, H, body))
    return svg, notes[-1]


def page_pinwheel():
    W, H = 1250, 560
    out, notes = [], []
    for k, (dx, deg, title) in enumerate(((0.0, 8.0, "(B) pure rotation theta = 8 deg: the PINWHEEL"), (-0.06, 4.0, "(C) offset dx = -0.06, theta = 4 deg: the right foot lengthens, the left wedge closes"))):
        pn = Panel(40 + k * 620, 60, 380, -0.1, -0.1, 1.1, 1.1)
        t = Fr(str(round(math.tan(math.radians(deg) / 2), 12)))
        box = (Fr(1, 2) + Fr(str(dx)), Fr(1, 2) + Fr(str(dx)), Fr(1, 2), Fr(1, 2), t, t)
        C = (Fr(0), Fr(1), Fr(0), Fr(1))
        back = {s: ("free",) for s in E.SIDES}
        tg, info, polys = draw_cell(pn, box, C, back, "")
        pn.poly(sq_corners(0.5 + dx, 0.5, deg), fill="none", stroke="#000", sw=1.2)
        ystar = 0.5 + float(t) / 2 + dx * (1 - float(t) ** 2) / (2 * float(t))
        wR = float(t) * (1 - float(t)) / (1 - float(t) ** 2) - dx
        # numeric check of the foot: the point (1, y* +- eps) is outside / inside F
        def inF(x, y):
            c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
            u, v = (x - 0.5 - dx) * c + (y - 0.5) * s, -(x - 0.5 - dx) * s + (y - 0.5) * c
            return abs(u) <= 0.5 + 1e-12 and abs(v) <= 0.5 + 1e-12
        chk = (not inF(1.0, min(1.0, ystar) + 1e-4)) and (ystar < 0 or inF(1.0, ystar - 1e-4))
        for y, lab in ((ystar, "y* = %.4f" % ystar),):
            if 0 <= y <= 1:
                px, py = pn.P(1.0, y)
                out.append('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#d50000"/>' % (px, py))
                pn.text(1.02, y, lab, 10, "#d50000")
        pn.text(0.0, 1.06, title, 11, "#222")
        pn.note(["    t = tan(theta/2) = %.5f; right-side foot y* = 1/2 + dy + t/2 + dx(1-t^2)/(2t) = %.4f; corner depth w_R = t(1-t-2dy)/(1-t^2) - dx = %.4f;" % (float(t), ystar, wR),
                 "    wedge depths from the polygons: L %s R %s B %s T %s.  GEOMETRY CHECK (numeric): (1, y*+1e-4) outside F and (1, y*-1e-4) inside F: %s." % (
                     info["depths"]["L"], info["depths"]["R"], info["depths"]["B"], info["depths"]["T"], chk)], 500, 10)
        out += pn.g
        notes.append(chk)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif">\n<rect width="%d" height="%d" fill="white"/>\n'
           '<text x="12" y="22" font-size="14" font-weight="bold" fill="#222">A227 -- Lemma EPS-2: the four wedges of a near-simple square in the unit cell -- pinwheel (pure rotation) and offset; feet at y* (red)</text>\n%s\n</svg>\n'
           % (W, H, W, H, "\n".join(out)))
    return svg, notes


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    svg, note = page_Y0865()
    open(os.path.join(OUT, "eps227_Y0865.svg"), "w", encoding="utf-8", newline="\n").write(svg)
    print(note)
    svg, chk = page_pinwheel()
    open(os.path.join(OUT, "eps227_pinwheel.svg"), "w", encoding="utf-8", newline="\n").write(svg)
    print("pinwheel checks", chk)
