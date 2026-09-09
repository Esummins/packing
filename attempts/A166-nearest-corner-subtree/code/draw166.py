"""A166 -- one page per cell, in A148's panel style, with the THREE boxes drawn.

Panel G (large): the container at s0; the corner box (exact unit box solid, the K0-WIDEN pad dashed);
the corner-meeting zone Z(w) of the cover; the 6 x 6 position cells of the cover coloured by their
worst-to-best verdict (white = DEAD by some stage, yellow = DEGENERATE only, green = ALIVE); H's
conditioned box in black with its A132 polygon core K'(H) in orange and its A135 exact axis core
K(H) hatched; the representative node's TWO corner boxes in blue with their own K' cores; and the
matching Trump image's eleven squares as thin grey outlines.

Panel V (right): the full 6 x 6 x 6 verdict matrix, one 6 x 6 block per tilt window, and the legend
with the stage counts, the pair-stage counts, and the cell's verdict.

Nothing on the page comes from an LP; the LP numbers are printed in the caption only.

    python code/draw166.py --pad wmax
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import cells166 as C                                            # noqa: E402
import polycore as PC                                           # noqa: E402  READ-ONLY (A132)
from caselp import Box                                          # noqa: E402  READ-ONLY (A57)

RES = os.path.join(BASE, "results")
FIGS = os.path.join(BASE, "figs")
S0 = C.S0
PADS = {"w0": 0.0, "wmax": C.W_MAX}
COL = {"ALIVE": "#bfe6bf", "DEGENERATE": "#ffe08a", "DEAD": "#ffffff"}


def klass(v):
    if v == "ALIVE":
        return "ALIVE"
    if v.startswith("DEGENERATE"):
        return "DEGENERATE"
    return "DEAD"


def sq_path(cx, cy, th, sc, oy):
    t = math.radians(th)
    co, si = math.cos(t), math.sin(t)
    e = (0.5 * co, 0.5 * si)
    f = (-0.5 * si, 0.5 * co)
    P = [(cx + a * e[0] + b * f[0], cy + a * e[1] + b * f[1])
         for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    return "M " + " L ".join("%.3f,%.3f" % (sc * x, oy - sc * y) for x, y in P) + " Z"


def poly_path(P, sc, oy):
    return "M " + " L ".join("%.3f,%.3f" % (sc * x, oy - sc * y) for x, y in P) + " Z"


def rect(x0, x1, y0, y1, sc, oy, **kw):
    at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return ('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" %s/>'
            % (sc * x0, oy - sc * y1, sc * (x1 - x0), sc * (y1 - y0), at))


def page(cellname, pad, d, lp, trump):
    a_w = 1.0 + PADS[pad]
    sc = 150.0
    W = int(sc * S0) + 400
    Hh = int(sc * S0) + 130
    oy = sc * S0 + 20
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d" font-family="DejaVu Sans, Arial" font-size="11">' % (W, Hh, W, Hh),
           '<rect width="%d" height="%d" fill="white"/>' % (W, Hh)]
    corner = d["corner"]
    # --- container
    out.append(rect(0, S0, 0, S0, sc, oy, fill="none", stroke="#000", stroke_width="2"))
    # --- corner boxes
    ex = C.corner_rect(corner, 1.0)
    wd = C.corner_rect(corner, a_w)
    out.append(rect(wd[0], wd[1], wd[2], wd[3], sc, oy, fill="#f2f2ff", stroke="#8888cc",
                    stroke_width="1", stroke_dasharray="4,3"))
    out.append(rect(ex[0], ex[1], ex[2], ex[3], sc, oy, fill="none", stroke="#4444aa",
                    stroke_width="1.6"))
    # --- the zone Z(w) in global coordinates
    zlo, zhi = 0.5, a_w + math.sqrt(0.5)
    ZX0, ZX1, ZY0, ZY1 = C.to_global_rect(corner, zlo, zhi, zlo, zhi)
    out.append(rect(ZX0, ZX1, ZY0, ZY1, sc, oy, fill="none", stroke="#aa6600",
                    stroke_width="1", stroke_dasharray="7,4"))
    # --- Trump image, faint
    for (x, y, t) in trump:
        out.append('<path d="%s" fill="none" stroke="#cccccc" stroke-width="0.8"/>'
                   % sq_path(x, y, t, sc, oy))
    # --- the 6 x 6 position cells, coloured by the BEST verdict over the 6 tilt windows
    rank = {"ALIVE": 2, "DEGENERATE": 1, "DEAD": 0}
    for ix in range(6):
        for iy in range(6):
            best = "DEAD"
            for it in range(6):
                k = "%d%d%d" % (ix, iy, it)
                if k in d["per_cell"]:
                    v = klass(d["per_cell"][k]["verdict"])
                    if rank[v] > rank[best]:
                        best = v
            u0 = zlo + (zhi - zlo) * ix / 6.0
            u1 = zlo + (zhi - zlo) * (ix + 1) / 6.0
            v0 = zlo + (zhi - zlo) * iy / 6.0
            v1 = zlo + (zhi - zlo) * (iy + 1) / 6.0
            X0, X1, Y0, Y1 = C.to_global_rect(corner, u0, u1, v0, v1)
            out.append(rect(X0, X1, Y0, Y1, sc, oy, fill=COL[best], fill_opacity="0.55",
                            stroke="#999", stroke_width="0.5"))
    # --- H
    bH = Box(**d["Hbox"])
    KH = G.kprime(bH)
    cH = G.exact_core(bH)
    # the coordinator's drawing convention: K' is the box's CORE and is drawn SOLID; the pose union
    # (the centre box) is a THIN OUTLINE only, so nothing on the page can be read as feasible space.
    out.append(rect(bH.x0, bH.x1, bH.y0, bH.y1, sc, oy, fill="none", stroke="#666",
                    stroke_width="0.6", stroke_dasharray="4,3"))
    out.append('<path d="%s" fill="#ff9933" fill-opacity="0.95" stroke="#994400" '
               'stroke-width="1.2"/>' % poly_path(KH.P, sc, oy))
    out.append('<path d="%s" fill="none" stroke="#663300" stroke-width="0.7" '
               'stroke-dasharray="2,2"/>'
               % poly_path([(float(v[0]), float(v[1])) for v in cH.vertices()], sc, oy))
    # --- the representative node's two corner boxes
    rep = None
    kind = "budget8"
    if d["survivors"]:
        rep = d["survivors"][0]["boxes"][1:]
    else:
        al = sorted(k for k, r in d["per_cell"].items() if r["verdict"] == "ALIVE")
        if al:
            rep = [d["per_cell"][al[0]]["cbox"]]
            kind = "degenerate (H is the other meeter)"
    for bj in (rep or []):
        b = Box(**bj)
        out.append(rect(b.x0, b.x1, b.y0, b.y1, sc, oy, fill="none", stroke="#6688bb",
                        stroke_width="0.6"))
        try:
            P = G.kprime(b).P
            out.append('<path d="%s" fill="#3377ee" fill-opacity="0.95" stroke="#113388" '
                       'stroke-width="1"/>' % poly_path(P, sc, oy))
        except Exception:                                       # noqa: BLE001
            pass
    # --- panel V: the 6 x 6 x 6 verdict matrix
    x0 = sc * S0 + 30
    out.append('<text x="%.0f" y="%.0f" font-size="13" font-weight="bold">%s  --  %s corner, pad %s'
               '</text>' % (x0, 24, cellname, corner, pad))
    yy = 44
    cellpx = 13
    for it in range(6):
        out.append('<text x="%.0f" y="%.0f" font-size="10">tilt %d: [%d, %d) deg</text>'
                   % (x0, yy, it, 15 * it, 15 * (it + 1)))
        yy += 6
        for iy in range(5, -1, -1):
            for ix in range(6):
                k = "%d%d%d" % (ix, iy, it)
                v = klass(d["per_cell"][k]["verdict"]) if k in d["per_cell"] else "DEAD"
                out.append('<rect x="%.0f" y="%.0f" width="%d" height="%d" fill="%s" '
                           'stroke="#888" stroke-width="0.4"/>'
                           % (x0 + ix * cellpx, yy, cellpx, cellpx, COL[v]))
            yy += cellpx
        yy += 10
    st, ps = d["cell_stats"], d["pair_stats"]
    lines = [
        "cover 216 cells (6x6 positions x 6 tilt windows of 15 deg), no transpose quotient",
        "cells: DEAD_R %d  DEAD_H2 %d  DEAD_H1 %d  DEAD_CLIP %d  DEGENERATE %d  ALIVE %d"
        % (st["dead_R"], st["dead_H2"], st["dead_H1"], st["dead_clip"], st["degenerate"],
           st["survive"]),
        "pairs: %d raw, %d alive in A143's chain, %d both-cells-alive," % (ps["raw"],
                                                                          ps["raw_alive_a143"],
                                                                          ps["both_alive"]),
        "       then P2 %d  P1 %d  P1s %d  MUT %d  DIST %d  ->  %d SURVIVORS"
        % (ps["P2"], ps["P1"], ps["P1s"], ps["MUT"], ps["DIST"], ps["alive"]),
        "H box %s, tilt [%.1f, %.1f) deg;  d(H centre, %s) = %.5f"
        % ("[%.4f,%.4f]x[%.4f,%.4f]" % (bH.x0, bH.x1, bH.y0, bH.y1), bH.th0, bH.th1, corner,
           d["dist_to_corner"]),
        "K'(H) area %.6f, exact core a = %.6f, inscribed axis core a = %.6f"
        % (d["kprime_H_area"], d["a_exact_H"], d["a_axis_H"]),
        "node drawn: %s" % kind,
    ] + lp
    for i, t in enumerate(lines):
        out.append('<text x="%.0f" y="%.0f" font-size="10.5">%s</text>'
                   % (20, oy + 22 + 14 * i,
                      t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")))
    out.append('<text x="%.0f" y="%.0f" font-size="10">legend: green = ALIVE cover cell (can hold a '
               'corner meeter distinct from H); yellow = DEGENERATE (any square there IS H); '
               'white = DEAD.  SOLID orange = K\'(H) (the box\'s guaranteed core), dotted = the exact '
               'axis core K(H); SOLID blue = K\' of each corner box.  The thin dashed outlines are the '
               'POSE UNIONS (centre boxes) and are NOT feasible space.  Dashed blue rectangle = the '
               'K0-WIDEN pad, solid blue = the exact unit corner box.  Grey outlines = the matching '
               'Trump image.  Every corner box drawn here is already clipped against K\'(H) and '
               'against the other corner box\'s core, per tilt sub-bin.</text>'
               % (20, oy + 22 + 14 * len(lines) + 6))
    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax", choices=sorted(PADS))
    a = ap.parse_args()
    os.makedirs(FIGS, exist_ok=True)
    T = json.load(open(os.path.join(RES, "trump166.json"), encoding="utf-8"))
    tcells = {r["cell"]: r for r in T["cells"]}
    lps = {}
    for s in (0, 1):
        p = os.path.join(RES, "lp166_%s_s%d.jsonl" % (a.pad, s))
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                r = json.loads(ln)
                lps.setdefault(r.get("cell"), []).append(r)
    idx = []
    for (meta, _bH, _rec) in C.load_eleven():
        name = meta["cell"]
        p = os.path.join(RES, "survivors166_%s_%s.json" % (a.pad, name))
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        rows = lps.get(name, [])
        img = tcells[name]["trump_interior"]["image"]
        tp = [(x, y, t) for (x, y, t) in T["images"][img]["poses"]]
        lp = ["Trump match: %s sq%d (pose distance %.4f);  image's non-simple corner %s;  "
              "nearest corner %s is %s in Trump"
              % (img, tcells[name]["trump_interior"]["sq"], tcells[name]["trump_interior"]["d"],
                 ",".join(tcells[name]["image_nonsimple"]), d["corner"],
                 "NON-SIMPLE" if tcells[name]["nearest_is_nonsimple"] else "SIMPLE")]
        if rows:
            taus = [r.get("tau") for r in rows if r.get("tau") is not None]
            lp.append("LP: %d node(s), budget %s, tau %s, converged kills %d, certified %s"
                      % (len(rows), sorted({r["budget"] for r in rows}),
                         "/".join("%.4f" % t for t in taus[:8]),
                         sum(1 for r in rows if r.get("kills_converged")),
                         "/".join(str(r.get("certified")) for r in rows
                                  if r.get("certified")) or "-"))
        else:
            lp.append("LP: not run (no surviving pair cell)" if not d["survivors"]
                      else "LP: pending")
        svg = page(name, a.pad, d, lp, tp)
        fp = os.path.join(FIGS, "a166_%s_%s.svg" % (a.pad, name))
        open(fp, "w", encoding="utf-8").write(svg)
        idx.append(dict(cell=name, file=os.path.basename(fp), corner=d["corner"],
                        survivors=d["n_survivors"]))
        print("wrote", fp, flush=True)
    json.dump(idx, open(os.path.join(FIGS, "index166_%s.json" % a.pad), "w"), indent=1)


if __name__ == "__main__":
    main()
