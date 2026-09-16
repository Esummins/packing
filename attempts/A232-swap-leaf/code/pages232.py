"""A232 pages: one SVG per k0_00 cell, four panels (one per corner, each drawn in the frame that
takes that corner to BL).  Every panel shows the container at m_lo = 3.82 (solid) with s0 dashed,
the reach set of every role OUTSIDE X in GREY (the obstacle the leftovers must miss), its centre
box as a thin dashed rectangle, the corner slot square S in blue, the leftover cells the search
placed in orange, and a NOTE saying what the panel is, how many cells the leaf needs, how many
exist, and the exact geometry check of everything drawn.

Drawing rules (docs/residue_map/README.md §3): hypothesis objects at their box with extremal
outlines only at admissible poses, schematic objects thin dashed, UNDECIDED grey (never green),
a note on every panel, the verifier's name on every verdict.

    python pages232.py [--jsonl results/swapleaf232.jsonl]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)
import cell232 as C                                              # noqa: E402
import search232 as S                                            # noqa: E402
import verify_swap232 as V                                       # noqa: E402

PAGES = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A232-swap-leaf")
PX = 98.0
PAD = 30
NOTE = 182


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Page:
    def __init__(self, title, side, cols=2, rows=2):
        self.side, self.cols = side, cols
        self.pw = int(PX * side) + 2 * PAD
        self.ph = int(PX * side) + 2 * PAD + NOTE
        self.W, self.H = cols * self.pw, rows * self.ph + 54
        self.o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                  'font-family="Helvetica,Arial,sans-serif">' % (self.W, self.H),
                  '<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse">'
                  '<circle cx="3" cy="3" r="1.1" fill="#8a8a8a"/></pattern></defs>',
                  '<rect width="%d" height="%d" fill="white"/>' % (self.W, self.H),
                  '<text x="12" y="22" font-size="15" font-weight="bold" fill="#222">%s</text>'
                  % esc(title)]
        self.checks = []

    def org(self, k):
        r, c = divmod(k, self.cols)
        return c * self.pw + PAD, 54 + r * self.ph + PAD

    def P(self, k, x, y):
        ox, oy = self.org(k)
        return ox + PX * x, oy + PX * (self.side - y)

    def rect(self, k, x0, y0, x1, y1, fill, stroke, w=1.4, dash=None):
        a = self.P(k, x0, y1)
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" '
                      'stroke-width="%.1f"%s/>' % (a[0], a[1], PX * (x1 - x0), PX * (y1 - y0),
                                                   fill, stroke, w, ' stroke-dasharray="5,3"' if dash else ''))

    def poly(self, k, verts, fill, stroke, w=1.3, label=None, dash=None):
        pts = " ".join("%.1f,%.1f" % self.P(k, *v) for v in verts)
        self.o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
                      % (pts, fill, stroke, w, ' stroke-dasharray="4,3"' if dash else ''))
        if label is not None:
            cx = sum(v[0] for v in verts) / len(verts)
            cy = sum(v[1] for v in verts) / len(verts)
            x, y = self.P(k, cx, cy)
            self.o.append('<text x="%.1f" y="%.1f" font-size="11" text-anchor="middle" '
                          'fill="#333">%s</text>' % (x, y + 4, esc(label)))

    def note(self, k, lines, size=10.4):
        ox, oy = self.org(k)
        y = oy + PX * self.side + 15
        wrapped = []
        for t in lines:
            while len(t) > 74:
                cut = t.rfind(" ", 0, 74)
                cut = cut if cut > 40 else 74
                wrapped.append(t[:cut])
                t = "   " + t[cut:].lstrip()
            wrapped.append(t)
        for t in wrapped:
            self.o.append('<text x="%d" y="%.1f" font-size="%.1f" fill="#222">%s</text>'
                          % (ox, y, size, esc(t)))
            y += 12.6

    def write(self, path):
        assert all(self.checks), self.checks
        self.o.append("</svg>")
        open(path, "w", encoding="utf-8").write("\n".join(self.o))
        return path


def geometry_check(cells, boxes, m_lo):
    """EXACT, by the verifier's own routines: the drawn cells are unit squares inside
    [0, m_lo]^2, pairwise interior-disjoint, and miss every drawn reach box."""
    polys = [V.poly_of(c) for c in cells]
    ok = all(V.is_unit_square(p) for p in polys)
    ok &= all(0 <= v[0] <= m_lo and 0 <= v[1] <= m_lo for p in polys for v in p)
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            ok &= V.polys_interior_disjoint(polys[i], polys[j])[0]
    nm = 0
    for b in boxes:
        for c in cells:
            if c["kind"] == "axis":
                r, _ = V.box_misses_axis_cell(b, (Fr(c["x"]), Fr(c["x"]) + 1,
                                                  Fr(c["y"]), Fr(c["y"]) + 1))
            else:
                r, _ = V.box_misses_poly(b, c["verts"])
            ok &= r
            nm += 1
    return ok, nm


def draw_cell_page(rec, cell):
    m_lo, s0 = float(C.M_LO), float(C.S0)
    pg = Page("A232 SWAP-LEAF -- %s (k0_00, %s): the leaf at each corner, in the frame that "
              "takes that corner to BL" % (rec["node"], rec["record"].split("/")[-1]), s0)
    for k, cr in enumerate(rec["corners"]):
        corner = cr["corner"]
        pg.rect(k, 0, 0, s0, s0, "none", "#999", 1.0, dash=True)         # s0, schematic
        pg.rect(k, 0, 0, m_lo, m_lo, "none", "#333", 1.8)                # the container used
        outside = [r for r in cell["roles"] if r["name"] in cr["outside"]]
        boxes = []
        for r in outside:
            for b in C.normalised_pieces(r, corner):
                boxes.append(b)
                g = C.reach_poly(b)
                pg.poly(k, list(g.exterior.coords)[:-1], "url(#stip)", "#777", 1.1,
                        label="reach %s" % r["name"])
                pg.rect(k, float(b[0]), float(b[2]), float(b[1]), float(b[3]),
                        "none", "#b06a00", 1.1, dash=True)
        cells = rec.get("cells_drawn", {}).get(str(corner)) or []
        for i, c in enumerate(cells):
            V4 = [(float(a), float(b)) for a, b in V.poly_of(c)]
            pg.poly(k, V4, "#dbe9f6" if i == 0 else "#fde9c9",
                    "#1f4e79" if i == 0 else "#b06a00", 1.5,
                    label="S" if i == 0 else "P%d" % i)
        ok, nm = geometry_check(cells, boxes, C.M_LO)
        pg.checks.append(ok)
        pg.note(k, [
            "PANEL %s -- corner %s, drawn in the frame taking it to BL.  Solid frame = [0, 3.82]^2"
            % ("ABCD"[k], cr["corner_name"]),
            "(every container of the window); dashed = s0 = 3.877084 (schematic).  GREY STIPPLE =",
            "the REACH SET of a role outside X (every pose of its pulled-back, flipped box) -- the",
            "leftovers must miss it; thin orange dashed = that role's centre box.  Blue = the slot",
            "square S; orange = the leftover cells the search placed.",
            "LEAF: |X| = %d cells needed; %d DRAWN here (the page re-runs the search under an "
            "8 s wall; the campaign row's best at this corner was %d)  ->  %s" % (
                cr["need"], len(cells), cr["found"],
                "DEAD by SWAP-LEAF (verify_swap232 %s)" % cr.get("verified")
                if cr.get("verified") == "PASS" else "UNDECIDED (no certificate)"),
            "X = %s   (every UNBOXED role is forced into X: its reach is the whole container)"
            % ", ".join(cr["X"]),
            "outside X (boxed, drawn grey) = %s" % (", ".join(cr["outside"]) or "none"),
            "reach area inside the container %s ; free area %.3f" % (cr["blocked_area"], cr["free_area"]),
            "geometry check (exact, verify_swap232): %d cells unit + inside + pairwise disjoint, "
            "%d miss certificates -- %s" % (len(cells), nm, "OK" if ok else "FAILED"),
        ])
    return pg.write(os.path.join(PAGES, "swapleaf232_%s.svg" % rec["node"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default=os.path.join(BASE, "results", "swapleaf232.jsonl"))
    a = ap.parse_args()
    os.makedirs(PAGES, exist_ok=True)
    recs = {}
    for ln in open(a.jsonl, encoding="utf-8"):
        r = json.loads(ln)
        recs[r["node"]] = r
    made = []
    for node, rec_rel in C.k0v4_cells():
        rec = recs.get(node)
        if rec is None:
            continue
        cell = C.load_cell(node, rec_rel)
        if "cells_drawn" not in rec:                              # re-run the search for the page
            rec["cells_drawn"] = {}
            for cr in rec["corners"]:
                if cr.get("cells"):
                    rec["cells_drawn"][str(cr["corner"])] = cr["cells"]
                    continue
                X, outside, obst = C.role_sets(cell, cr["corner"])
                boxes = [b for r in cell["roles"] if r["name"] in outside
                         for b in C.normalised_pieces(r, cr["corner"])]
                cs, _k = S.search(obst, boxes, C.M_LO, len(X), restarts=1,
                                  wall=time.time() + 8.0, clock=time.time)
                rec["cells_drawn"][str(cr["corner"])] = cs
        made.append(draw_cell_page(rec, cell))
    for p in made:
        print("page", os.path.relpath(p, ROOT).replace("\\", "/"))
    print("%d pages" % len(made))


if __name__ == "__main__":
    main()
