"""A160 -- the figure, in A148's panel style (panel title + a one-line "what this IS" caption,
geometry largest, nothing drawn that is not certified data).

  PANEL A  "THE SLIDE: the one place f0 is free"  -- the polished eleven-square pinwheel at its own
           s*, with f0 drawn at seven poses along its slide, the slide segment itself as the orange
           spine, and the contact set printed at each end.  Everything in this panel is a REAL
           packing (worst pair SAT gap -5.6e-16).
  PANEL B  "THE BOX at s0: what the certificate covers" -- the container at s0, the five A57 slack
           cores, A151-B's three tilted boxes and BR(0,1)'s, f0's slide-cover box, and the
           COMMON-TILT CHAIN drawn as the track of the three centres over the certified links with
           the extreme tilts' squares outlined.  Boxes are hypotheses, not packings: dashed.

    python draw160.py [--out results/A160_slide_and_box.svg]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                      # noqa: E402
import a116lib as A                     # noqa: E402
import grow160 as G                     # noqa: E402
from slide160 import config             # noqa: E402

RES = L.RES
SLOT = "#0288d1"
SLOTF = "#e1f5fe"
CY = "#b2ebf2"
CYD = "#006064"
ORA = "#e65100"
PUR = "#5e35b1"


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Pane:
    def __init__(self, ox, oy, sc, side):
        self.ox, self.oy, self.sc, self.side = ox, oy, sc, side

    def X(self, x):
        return self.ox + x * self.sc

    def Y(self, y):
        return self.oy - y * self.sc

    def poly(self, pts, fill, stroke, op=1.0, w=1.0, dash=""):
        d = " ".join("%.2f,%.2f" % (self.X(x), self.Y(y)) for x, y in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                'stroke-width="%.2f"%s/>' % (d, fill, op, stroke, w, da))

    def rect(self, x0, x1, y0, y1, fill, stroke, op=1.0, w=1.0, dash=""):
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, stroke, op, w, dash)

    def line(self, x0, y0, x1, y1, col, w=1.0, dash="", cap=""):
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        return ('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"%s%s/>'
                % (self.X(x0), self.Y(y0), self.X(x1), self.Y(y1), col, w, da, cap))

    def path(self, pts, col, w=1.0, dash=""):
        d = "M " + " L ".join("%.2f %.2f" % (self.X(x), self.Y(y)) for x, y in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%.2f"%s/>' % (d, col, w, da)

    def text(self, x, y, t, size=9, col="#222", bold=False, anchor="middle", dy=0.0):
        return txt(self.X(x), self.Y(y) + dy, t, size, col, bold, anchor)


def txt(px, py, t, size=9, col="#222", bold=False, anchor="middle"):
    return ('<text x="%.2f" y="%.2f" font-family="Helvetica,Arial,sans-serif" font-size="%.1f" '
            'fill="%s" text-anchor="%s"%s>%s</text>'
            % (px, py, size, col, anchor, ' font-weight="bold"' if bold else "", esc(t)))


def sq(c, th):
    return A.corners(c, th)


# ------------------------------------------------------------------ panel A
def panel_slide(pn, out):
    side, poses, slots, free = config("S02", "polished")
    pol = json.load(open(os.path.join(RES, "polish160.json"), encoding="utf-8"))
    sl = json.load(open(os.path.join(RES, "slide_exact.json"), encoding="utf-8"))
    out.append(txt(pn.ox, pn.oy - side * pn.sc - 42,
                   "PANEL A — THE SLIDE: the one place f0 is free", 13, "#000", True))
    out.append(txt(pn.ox, pn.oy - side * pn.sc - 27,
                   "the eleven-square pinwheel at its own s* = %.9f (worst pair SAT gap %.1e): "
                   "every pose drawn here is a real packing" % (pol["eleven"]["s"],
                                                                pol["eleven"]["worst_gap"]),
                   8.6, "#555"))
    out.append(pn.rect(0, side, 0, side, "none", "#000", 0.0, 2.2))
    out.append(txt(pn.X(side), pn.Y(side) - 6, "s* = %.6f" % side, 9, "#000", True, "end"))
    for n in slots:
        x, y, t = poses[n]
        out.append(pn.poly(sq((x, y), t), SLOTF, SLOT, 0.85, 1.2))
        out.append(pn.text(x, y, n, 7.6, "#01579b", True, "middle", 3))
    for n in ("f1", "f2", "f3"):
        x, y, t = poses[n]
        out.append(pn.poly(sq((x, y), t), CY, CYD, 0.45, 2.0))
        out.append(pn.text(x, y, n, 11, "#000", True, "middle", 4))
    # the slide
    lo, hi = sl["end_lo"], sl["end_hi"]
    th = math.radians(sl["tilt_deg"])
    for u in (0.0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6, 1.0):
        c = (lo[0] + u * (hi[0] - lo[0]), lo[1] + u * (hi[1] - lo[1]))
        end = u in (0.0, 1.0)
        out.append(pn.poly(sq(c, th), ORA if end else "#ffcc80",
                           ORA if end else "#ef6c00", 0.30 if end else 0.16,
                           2.2 if end else 1.0, "" if end else "3,2"))
    out.append(pn.line(lo[0], lo[1], hi[0], hi[1], ORA, 3.2))
    for c, col in ((lo, ORA), (hi, ORA)):
        out.append('<circle cx="%.2f" cy="%.2f" r="3.4" fill="%s"/>' % (pn.X(c[0]), pn.Y(c[1]), col))
    mid = (0.5 * (lo[0] + hi[0]), 0.5 * (lo[1] + hi[1]))
    out.append(pn.text(mid[0] - 0.34, mid[1] + 0.30,
                       "f0 slide  %.6f" % sl["length"], 9.4, ORA, True, "middle"))
    out.append(pn.text(mid[0] - 0.34, mid[1] + 0.30, "along e2 = (%.4f, %.4f), tilt FIXED"
                       % tuple(sl["axis"]), 7.6, "#bf360c", False, "middle", 11))
    out.append(pn.text(lo[0] + 0.42, lo[1] - 0.30, "end A: " + " ".join(sl["contacts_lo"]),
                       7.4, "#bf360c", True, "middle"))
    out.append(pn.text(hi[0] - 0.30, hi[1] + 0.42, "end B: " + " ".join(sl["contacts_hi"]),
                       7.4, "#bf360c", True, "middle"))
    out.append(pn.text(mid[0] + 0.05, mid[1] - 0.62, "interior: " + " ".join(sl["contacts_mid"]),
                       7.4, "#6d4c41", False, "middle"))


# ------------------------------------------------------------------ panel B
def panel_box(pn, out):
    s = A.S0
    sl = json.load(open(os.path.join(RES, "slide_exact.json"), encoding="utf-8"))
    out.append(txt(pn.ox, pn.oy - s * pn.sc - 42,
                   "PANEL B — THE BOX at s0: what the certificate covers", 13, "#000", True))
    out.append(txt(pn.ox, pn.oy - s * pn.sc - 27,
                   "dashed = a HYPOTHESIS box, not a packing.  Grey track = the common-tilt chain's "
                   "spine (the centres of f1, f2, f3 as the shared tilt moves).", 8.6, "#555"))
    out.append(pn.rect(0, s, 0, s, "none", "#000", 0.0, 2.2))
    out.append(txt(pn.X(s), pn.Y(s) - 6, "s0 = %.6f" % s, 9, "#000", True, "end"))

    spec = G.with_f0(L.a151_spec_B())
    bodies, nv, s_sh, P = L.bodies_for(spec)
    for b in bodies:
        if b.kind == "pin":
            cx, cy = b.ax[0] + b.ax[1] * s, b.ay[0] + b.ay[1] * s
            out.append(pn.poly(sq((cx, cy), 0.0), SLOTF, SLOT, 0.8, 1.2))
            out.append(pn.rect(cx - b.hh, cx + b.hh, cy - b.hh, cy + b.hh, "none", "#01579b",
                               0.0, 1.0))
            out.append(pn.text(cx, cy, b.name, 7.6, "#01579b", True, "middle", 3))

    # the chain: spine track + extreme tilts
    tracks, tilts = {}, []
    for p in sorted(glob.glob(os.path.join(RES, "chain_*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            if not rec.get("dead"):
                continue
            tilts.append(rec["tilt_deg"])
            for bx in rec["boxes"]:
                if bx["kind"] == "free" and bx["name"] in ("f1", "f2", "f3"):
                    tracks.setdefault(bx["name"], []).append(
                        (bx["anchor"][0], bx["anchor"][1], bx["anchor"][2]))
    for n, pts in tracks.items():
        pts.sort(key=lambda q: q[2])
        out.append(pn.path([(q[0], q[1]) for q in pts], "#9e9e9e", 2.4))
        for q in (pts[0], pts[-1]):
            out.append(pn.poly(sq((q[0], q[1]), math.radians(q[2])), "none", "#616161", 0.0, 1.0,
                               "3,2"))

    for b in bodies:
        if b.kind != "free":
            continue
        col = PUR if b.name == "f0" else "#000"
        out.append(pn.rect(b.x0, b.x1, b.y0, b.y1, "none", col, 0.0,
                           1.8 if b.name == "f0" else 1.2, "5,3"))
        cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
        tm = 0.5 * (b.t0 + b.t1)
        out.append(pn.poly(sq((cx, cy), tm), "#ede7f6" if b.name == "f0" else CY,
                           PUR if b.name == "f0" else CYD, 0.35, 2.0))
        out.append(pn.text(cx, cy, b.name, 11, "#000", True, "middle", 4))
        out.append(pn.text(cx, cy, "%.2f° ± %.2f" % (math.degrees(tm),
                                                               math.degrees(b.t1 - tm)),
                           7.0, "#004d40", False, "middle", 15))
    # f0's slide, dilated into the s0 frame, inside its box
    lam = s / json.load(open(os.path.join(RES, "polish160.json"),
                             encoding="utf-8"))["eleven"]["s"]
    lo = [v * lam for v in sl["end_lo"]]
    hi = [v * lam for v in sl["end_hi"]]
    out.append(pn.line(lo[0], lo[1], hi[0], hi[1], ORA, 3.0))
    out.append(pn.text(0.5 * (lo[0] + hi[0]) - 0.05, 0.5 * (lo[1] + hi[1]) - 0.34,
                       "f0's slide (dilated)", 7.4, ORA, True, "middle"))
    if tilts:
        out.append(txt(pn.ox, pn.oy + 22,
                       "chain: %d certified links, shared tilt %.3f° – %.3f°"
                       % (len(tilts), min(tilts), max(tilts)), 9, "#333", True, "start"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "A160_slide_and_box.svg"))
    a = ap.parse_args()
    sc = 132.0
    W, H = 2 * 3.95 * sc + 190, 3.95 * sc + 175
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
           'viewBox="0 0 %.0f %.0f">' % (W, H, W, H),
           '<rect width="100%%" height="100%%" fill="#ffffff"/>',
           txt(20, 26, "A160 — S02's f0 slide and the grown neighbourhood", 15, "#000",
               True, "start"),
           txt(20, 43, "attempts/A160-s02-f0-slide — the pinwheel shadow S02 (k7 + pinwheel-4, "
                       "s* = 3.886746), its rattler f0, and the boxes the local certificate covers",
               9, "#666", False, "start")]
    pa = Pane(70, 60 + 3.95 * sc, sc, 3.95)
    pb = Pane(70 + 3.95 * sc + 100, 60 + 3.95 * sc, sc, 3.95)
    panel_slide(pa, out)
    panel_box(pb, out)
    out.append(txt(20, H - 12,
                   "Panel A: exact geometry (shapely half-plane boolean ops, eps → 0 limit).  "
                   "Panel B: A151-B's boxes + f0's slide cover + this attempt's certified chain "
                   "links.  Dashed = hypothesis box; solid squares = poses.", 8, "#777", False,
                   "start"))
    out.append('</svg>')
    open(a.out, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
