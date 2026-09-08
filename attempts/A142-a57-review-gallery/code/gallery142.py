"""A142 T2 -- the A57/A60 review gallery: one page per surviving alive node, in A140's format.

Format (docs/shadows/k0v3/, attempts/A140-k0-residue-gallery/code/gallery140.py), with the two
objects the A57 figures have never shown -- the EXACT pin cores (A135 `exactcore.exact_a`,
half-side 1/2 - delta/sqrt2 certified vertex-wise) and the CLIPPED centre box (A131 `pinclip`,
per tilt sub-bin) -- and the polygon core K'(B) (A132 `polycore`, certified vertices).

  PANEL 1  the LP dual support of the node's record at s0, fill = dual weight y on one sequential
           scale; the FIVE PINS drawn as pins (zero-tilt-width cores) at their exact cores, each
           pin's K'(P) = that exact square as a thin inner outline; the conditioned square as a
           cyan H at the centre of the CLIPPED box and the mid-tilt, faint outlines at the two
           extremal tilts, its certified polygon core K'(B) drawn inside; every dual-support
           column that overlaps a hypothesis square (the conditioned one OR a pin) at EVERY pose
           of that square's box outlined RED-DASHED with the overlap printed and the owner named.
  PANEL 2  the near-packing the PI labels from: A107's minimised shadow of the family this node
           belongs to (shadow_nodes.json -> shadows.json), slot squares blue and named, free
           squares red with f-index and tilt, contacts ringed.  Where the node has no shadow
           family, the raw integral dual support at s0 plus the conditioned square (labelled).
  PANEL 3  the hypothesis alone: the original centre box, the PIN-CLIPPED box per tilt sub-bin
           and their union, K'(B), the five pins with their exact cores, and the POCKETS -- the
           measured clearance from K'(B) to each pin's exact core and to the four walls, every
           pocket narrower than 1 drawn and printed (nothing fits in it).

Every drawn square is containment-checked; every red-dashed column's overlap is re-verified by an
independent SAT implementation at 7^3 poses of the owning box.  Read-only on every campaign;
writes only docs/shadows/a57v3/ and this attempt's results/.

    set PYTHONDONTWRITEBYTECODE=1 && python code/gallery142.py --camp A57 --lo 0 --hi 20
"""
import argparse
import csv
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A60 = os.path.join(ATT, "A60-trump5-campaign")
A107 = os.path.join(ATT, "A107-shadow-gallery")
A118 = os.path.join(ATT, "A118-lane-count")
A131 = os.path.join(ATT, "A131-pin-clip")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
          os.path.join(A131, "code"), os.path.join(A107, "code"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                           # noqa: E402
import polycore                                              # noqa: E402
import exactcore                                             # noqa: E402
import pinclip                                               # noqa: E402
from caselp import Box, Core                                 # noqa: E402
import shadowlib as L                                        # noqa: E402
import minimise as M                                         # noqa: E402

S0 = 969271.0 / 250000.0
SHAT = 3.877083590022814
OUT = os.path.join(ROOT, "docs", "shadows", "a57v3")
SC = 112                       # px per unit
NPOSE = 7                      # 7^3 pose grid (gen_a57_lp.py's rule)
HYP_FILL = "#00e5ff"
SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json"), encoding="utf-8"))


# ------------------------------------------------------------------ primitives
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


def sq(cx, cy, th, h=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(cx + h * (dx * c - dy * s), cy + h * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def wrap(x, y, t, width_px, size=9.0, col="#222", bold=False, lead=None):
    per = max(8, int(width_px / (size * 0.52)))
    words, lines, cur = str(t).split(), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= per:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lead = lead or (size + 3.0)
    return ([text(x, y + i * lead, ln, size, col, bold) for i, ln in enumerate(lines)],
            y + len(lines) * lead)


def poly(ox, oy, sc, P, fill, stroke, op=0.6, w=1.5, dash=""):
    pts = " ".join(f"{ox + x * sc:.1f},{oy - y * sc:.1f}" for x, y in P)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.2f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def rect(ox, oy, sc, x0, x1, y0, y1, fill, stroke, op=0.0, w=1.4, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{ox + x0 * sc:.1f}" y="{oy - y1 * sc:.1f}" '
            f'width="{max(0.0, (x1 - x0)) * sc:.1f}" height="{max(0.0, (y1 - y0)) * sc:.1f}" '
            f'fill="{fill}" fill-opacity="{op:.2f}" stroke="{stroke}" stroke-width="{w}"{d}/>')


def frame(ox, oy, sc, s):
    out = [f'<rect x="{ox}" y="{oy - s * sc:.1f}" width="{s * sc:.1f}" height="{s * sc:.1f}" '
           f'fill="none" stroke="#000" stroke-width="2.2"/>']
    for (x0, y0) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        out.append(f'<rect x="{ox + x0 * sc:.1f}" y="{oy - (y0 + 1) * sc:.1f}" width="{sc}" '
                   f'height="{sc}" fill="none" stroke="#bbb" stroke-width="1" '
                   f'stroke-dasharray="4,3"/>')
    return out


def wcol(y, dark=False):
    y = 0.0 if y is None else max(0.0, min(1.0, float(y)))
    h = 46.0 - 22.0 * y
    l = (88.0 - 46.0 * y) - (22.0 if dark else 0.0)
    return f"hsl({h:.0f},92%,{max(l, 12.0):.0f}%)"


# ------------------------------------------------------------------ geometry
def sat_poly(P, Q):
    """Independent SAT gap between two convex polygons (>0 disjoint, <0 overlap depth)."""
    best = -9e9
    for A, B in ((P, Q), (Q, P)):
        n = len(A)
        for i in range(n):
            a, b = A[i], A[(i + 1) % n]
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ex, ey)
            if ln < 1e-15:
                continue
            ax, ay = -ey / ln, ex / ln
            pp = [x * ax + y * ay for x, y in A]
            qq = [x * ax + y * ay for x, y in B]
            best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def _seg_dist(p, q, r, s):
    def pt_seg(px, py, ax, ay, bx, by):
        ex, ey = bx - ax, by - ay
        ln = ex * ex + ey * ey
        t = 0.0 if ln <= 0 else max(0.0, min(1.0, ((px - ax) * ex + (py - ay) * ey) / ln))
        return math.hypot(px - (ax + t * ex), py - (ay + t * ey))
    return min(pt_seg(p[0], p[1], r[0], r[1], s[0], s[1]),
               pt_seg(q[0], q[1], r[0], r[1], s[0], s[1]),
               pt_seg(r[0], r[1], p[0], p[1], q[0], q[1]),
               pt_seg(s[0], s[1], p[0], p[1], q[0], q[1]))


def poly_dist(P, Q):
    """EXACT minimum distance between two convex polygons (0 if they meet).  Unlike the SAT gap
    this is an upper bound as well as a lower bound, which is what a POCKET claim needs."""
    if sat_poly(P, Q) < 0.0:
        return 0.0
    d = 9e9
    for i in range(len(P)):
        for j in range(len(Q)):
            d = min(d, _seg_dist(P[i], P[(i + 1) % len(P)], Q[j], Q[(j + 1) % len(Q)]))
    return d


def core_sq(core):
    """the four corners of an axis-aligned-in-its-own-frame core square."""
    return sq(float(core.kx), float(core.ky), float(core.tm), float(core.a))


def meets_core(core, cx, cy, th):
    C = np.array([[cx, cy]], float)
    T = np.array([th], float)
    return bool(polycore.core_depth_fast(core, C, T)[0] > 0.0)


def meets_poly(pc, cx, cy, th):
    return bool(polycore.poly_square_depth(pc.P, [[cx, cy]], [th])[0] > 0.0)


def core_verdict(cx, cy, th, stock, exact, pc, tag):
    """'which core it clears and which it meets', in the PI's words."""
    bits = []
    for nm, hit in (("K(a) stock", meets_core(stock, cx, cy, th) if stock else None),
                    ("K exact", meets_core(exact, cx, cy, th) if exact else None),
                    ("K'", meets_poly(pc, cx, cy, th) if pc is not None else None)):
        if hit is None:
            continue
        bits.append(("meets " if hit else "clears ") + nm)
    return f"{tag}: " + ", ".join(bits)


def box_poses(b, n=NPOSE):
    xs = [b["x0"]] if b["x1"] <= b["x0"] else [b["x0"] + (b["x1"] - b["x0"]) * i / (n - 1.0)
                                               for i in range(n)]
    ys = [b["y0"]] if b["y1"] <= b["y0"] else [b["y0"] + (b["y1"] - b["y0"]) * i / (n - 1.0)
                                               for i in range(n)]
    ts = [b["th0"]] if b["th1"] <= b["th0"] else [b["th0"] + (b["th1"] - b["th0"]) * i / (n - 1.0)
                                                  for i in range(n)]
    for x in xs:
        for y in ys:
            for t in ts:
                yield (x, y, math.radians(t))


def gap_over_box(P, b, n=NPOSE):
    """max over the pose grid of the SAT gap between P and the square at that pose.
    < 0  =>  P overlaps that hypothesis square at EVERY sampled pose."""
    g = -9e9
    for (hx, hy, ht) in box_poses(b, n):
        g = max(g, sat_poly(P, sq(hx, hy, ht)))
    return g


# ------------------------------------------------------------------ node loading
def a57_index():
    idx = {}
    for f in glob.glob(os.path.join(A57, "results", "tree", "*", "*.json")):
        idx.setdefault(os.path.basename(f)[:-5], []).append(f)
    return idx


_A57IDX = None


def load_node(camp, nid):
    global _A57IDX
    if camp == "A60":
        p = os.path.join(A60, "results", "nodes", nid + ".json")
        return json.load(open(p, encoding="utf-8")), os.path.relpath(p, ROOT)
    if _A57IDX is None:
        _A57IDX = a57_index()
    best = None
    for p in sorted(_A57IDX.get(nid, [])):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("hyp", {}).get("boxes"):
            if best is None or len(d.get("packing") or []) > len(best[0].get("packing") or []):
                best = (d, os.path.relpath(p, ROOT))
    if best is None:
        raise KeyError(nid)
    return best


def slots_for(camp, nid):
    if camp == "A60":
        return SLOTS["trump5"]
    return SLOTS["k5_11" if nid.startswith("k5_11") else "k5_16"]


# ------------------------------------------------------------------ A107 shadow / lanes
_SHN = None
_SH = None


def shadow_families(nid):
    global _SHN
    if _SHN is None:
        _SHN = {}
        d = json.load(open(os.path.join(A107, "results", "shadow_nodes.json"), encoding="utf-8"))
        for sid, rows in d.items():
            for r in rows:
                _SHN.setdefault(r["nid"], []).append(sid)
    out, seen = [], set()
    for s in _SHN.get(nid, []):
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def shadow_geom(sid):
    global _SH
    if _SH is None:
        _SH = {r["id"]: r for r in json.load(open(os.path.join(A107, "results", "shadows.json"),
                                                  encoding="utf-8"))}
    return _SH.get(sid)


_LANE = None


def lane_of(nid):
    global _LANE
    if _LANE is None:
        _LANE = {}
        for f in sorted(glob.glob(os.path.join(A118, "results", "lane_s*.jsonl"))):
            for ln in open(f, encoding="utf-8"):
                ln = ln.strip()
                if not ln:
                    continue
                r = json.loads(ln)
                if r.get("nid"):
                    _LANE.setdefault(r["nid"], r)
    return _LANE.get(nid)


# ------------------------------------------------------------------ panel 1
def panel_lp(ox, oy, sc, title, sub, d, boxes, pcs, pincores, hypcores, clip, s):
    pk = d.get("packing", [])
    ys = [float(p.get("y", 0.0)) for p in pk]
    ymax = max(ys) if ys else 1.0
    npin = len(boxes) - 1
    out = [text(ox, oy - S0 * sc - 54, title, 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 40, sub, S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)

    # --- the PINS (zero tilt width) drawn as pins, with BOTH inner cores; any hypothesis box
    # that carries a TILT WINDOW is not a pin but a further conditioned square, drawn cyan.
    for i in range(npin):
        b = boxes[i]
        cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
        if pincores[i]["is_pin"]:
            out.append(poly(ox, oy, sc, sq(cx, cy, 0.0), "#cfd8dc", "#455a64", 0.55, 1.4))
            out.append(poly(ox, oy, sc, pincores[i]["P_stock"], "none", "#01579b", 0.0, 1.0))
            out.append(poly(ox, oy, sc, pincores[i]["P"], "none", "#1a237e", 0.0, 1.2))
            out.append(text(ox + cx * sc, oy - cy * sc + 4, f"P{i}", 9.5, "#263238", True,
                            "middle"))
        else:
            thm = math.radians(0.5 * (b["th0"] + b["th1"]))
            out.append(rect(ox, oy, sc, b["x0"], b["x1"], b["y0"], b["y1"], "none", "#000",
                            0.0, 1.2, "5,3"))
            out.append(poly(ox, oy, sc, sq(cx, cy, thm), HYP_FILL, "#000", 0.30, 2.0))
            out.append(poly(ox, oy, sc, [tuple(v) for v in pcs[i].P], "#7e57c2", "#4527a0",
                            0.35, 1.2))
            out.append(poly(ox, oy, sc, pincores[i]["P_stock"], "none", "#000000", 0.0, 1.4))
            out.append(poly(ox, oy, sc, pincores[i]["P"], "none", "#00695c", 0.0, 1.4))
            out.append(text(ox + cx * sc, oy - cy * sc + 4, f"H{i}", 10, "#000", True, "middle"))
            out.append(text(ox + cx * sc, oy - cy * sc + 15,
                            f"{0.5 * (b['th0'] + b['th1']):.2f}°", 7.0, "#000", False, "middle"))

    # --- the dual support, drawn by weight; impossible columns red-dashed
    bad, imposs = 0, []
    order = sorted(range(len(pk)), key=lambda k: float(pk[k].get("y", 0.0)))
    for k in order:
        p = pk[k]
        cx, cy, th, y = (float(p["cx"]), float(p["cy"]), float(p["theta"]),
                         float(p.get("y", 0.0)))
        P = sq(cx, cy, th)
        if not all(-1e-6 <= x <= s + 1e-6 and -1e-6 <= yy <= s + 1e-6 for x, yy in P):
            bad += 1
            continue
        w = y / ymax if ymax > 0 else 0.0
        out.append(poly(ox, oy, sc, P, wcol(w), wcol(w, True), 0.80, 1.0))
        if w < 0.95:
            out.append(text(ox + cx * sc, oy - cy * sc + 3, f"{y:.2f}", 7.0, "#5d4037",
                            False, "middle"))
        gmin, bi = 9e9, None
        for j, b in enumerate(boxes):
            g = gap_over_box(P, b)
            if g < gmin:
                gmin, bi = g, j
        if gmin < -1e-9:
            owner = ("H" if bi == npin else f"P{bi}")
            if bi == npin:
                cert = meets_poly(pcs[-1], cx, cy, th)
                ckind = "K'(B)"
                cv = core_verdict(cx, cy, th, hypcores["stock"], hypcores["exact"], pcs[-1], "H")
            else:
                cert = bool(sat_poly(P, pincores[bi]["P"]) < 0.0)
                ckind = f"K'(P{bi}) exact"
                cv = core_verdict(cx, cy, th, pincores[bi]["core_stock"],
                                  pincores[bi]["core_exact"], pcs[bi], f"P{bi}")
            imposs.append(dict(col=k, box=bi, owner=owner, overlap=-gmin, y=y, certified=cert,
                               cert_kind=ckind, core_verdict=cv,
                               pose=[cx, cy, math.degrees(th) % 90.0]))
            out.append(poly(ox, oy, sc, P, "none", "#d50000", 0.0, 2.4, dash="7,3"))
            out.append(text(ox + cx * sc, oy - cy * sc - 15,
                            f"impossible under {owner}, overlap {-gmin:.3f}",
                            6.8, "#d50000", True, "middle"))
            out.append(text(ox + cx * sc, oy - cy * sc - 7, cv, 6.4, "#d50000", False, "middle"))

    # --- the conditioned square: original box, clipped box, K'(B), H at mid-tilt
    b = boxes[-1]
    out.append(rect(ox, oy, sc, b["x0"], b["x1"], b["y0"], b["y1"], "none", "#000", 0.0, 1.4,
                    "5,3"))
    if clip.get("stock", {}).get("union_rect_f"):
        (sx0, sx1, sy0, sy1) = clip["stock"]["union_rect_f"]
        out.append(rect(ox, oy, sc, sx0, sx1, sy0, sy1, "none", "#ffb74d", 0.0, 1.0, "2,3"))
    if clip.get("union_rect_f"):
        (ux0, ux1, uy0, uy1) = clip["union_rect_f"]
        out.append(rect(ox, oy, sc, ux0, ux1, uy0, uy1, "none", "#e65100", 0.0, 1.6, "4,2"))
    cx0, cy0 = clip.get("centre") or (0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"]))
    th0, th1 = float(b["th0"]), float(b["th1"])
    thm = 0.5 * (th0 + th1)
    for (td, fop, sw, lab) in ((th0, 0.0, 1.0, ""), (th1, 0.0, 1.0, ""), (thm, 0.35, 2.6, "H")):
        Ph = sq(cx0, cy0, math.radians(td))
        out.append(poly(ox, oy, sc, Ph, HYP_FILL, "#000" if lab else "#006064", fop, sw))
        if lab:
            out.append(text(ox + cx0 * sc, oy - cy0 * sc + 4, "H", 11, "#000", True, "middle"))
            out.append(text(ox + cx0 * sc, oy - cy0 * sc + 16, f"{td:.2f}°", 7.5, "#000",
                            False, "middle"))
        else:
            vx, vy = min(Ph, key=lambda v: v[0] - v[1])
            out.append(text(ox + vx * sc + 2, oy - vy * sc - 3, f"{td:.2f}°", 6.5, "#006064"))
    # --- THE THREE CORES of H, in the PI's three styles
    out.append(poly(ox, oy, sc, [tuple(v) for v in pcs[-1].P], "#7e57c2", "#4527a0", 0.42, 1.4))
    out.append(poly(ox, oy, sc, core_sq(hypcores["stock"]), "none", "#000000", 0.0, 1.9))
    if hypcores["exact"] is not None:
        out.append(poly(ox, oy, sc, core_sq(hypcores["exact"]), "none", "#00695c", 0.0, 1.9))
    kk = pcs[-1].P.mean(0)
    out.append(text(ox + kk[0] * sc, oy - kk[1] * sc - 4, "K'(B)", 8.5, "#311b92", True, "middle"))

    tp = [p for p in pincores if p["is_pin"]]
    npin_true = len(tp)
    e, yy = wrap(ox, oy + 16,
                 f"{npin_true} PINS (grey), each with BOTH inner cores: thin light "
                 f"blue = the STOCK pin core (half-side {tp[0]['a_stock']:.6f}, the one "
                 f"the LP pruned against), thin dark blue = A135's EXACT pin core (half-side "
                 f"{tp[0]['a']:.9f} = 1/2 - delta/sqrt2, certified)"
                 + (f"; {npin - npin_true} further CONDITIONED square(s) H0.. carry a tilt "
                    f"window, so they are drawn cyan with their own three cores, not as pins"
                    if npin_true < npin else "") + ". The conditioned square "
                 f"H (cyan, at the centre of its clipped box and the mid-tilt, faint outlines at "
                 f"the extremal tilts) carries THREE cores: solid black = the STOCK axis core "
                 f"K(a), a_stock = {float(hypcores['stock'].a):.6f}; solid teal = A135's EXACT "
                 f"axis core, a_exact = "
                 f"{float(hypcores['exact'].a) if hypcores['exact'] is not None else float('nan'):.6f}; "
                 f"purple filled = the polygon core K'(B), area {pcs[-1].area():.6f} "
                 f"({pcs[-1].area() / (2.0 * float(hypcores['stock'].a)) ** 2:.3f}x area K(a)). "
                 f"{len(pk)} dual-support placements, fill = dual weight y (pale yellow y->0, "
                 f"dark orange y=1). SCHEMATIC (thin dashed, never filled): black dashed = the "
                 f"original centre box B; pale orange dotted = the pin-clipped centre box at the "
                 f"STOCK pin core (A131 as deployed, kept {clip['stock']['kept_vol']:.4f}); "
                 f"heavy orange dashed = the same clip at the EXACT pin core (kept "
                 f"{clip['kept_vol']:.4f}) — these are regions of CENTRES, not square bodies. "
                 f"Outside container: {bad}",
                 S0 * sc, 8.5, "#444")
    out += e
    e, _ = wrap(ox, yy + 2,
                f"red dashed = {len(imposs)} column(s) overlapping a hypothesis square at EVERY "
                f"of the {NPOSE}^3 = {NPOSE ** 3} sampled poses of that square's box -- "
                f"{sum(1 for r in imposs if r['box'] == npin)} against H's box, "
                f"{sum(1 for r in imposs if r['box'] != npin)} against an EXACT PIN CORE (the "
                f"pins' share is what A132's attribution found the deployed core was missing); "
                f"{sum(1 for r in imposs if r['certified'])} of them carry a core certificate.",
                S0 * sc, 8.5, "#d50000")
    out += e
    return out, imposs, bad, yy + 2 + 11.5 * max(1, len(e))


# ------------------------------------------------------------------ panel 2
def panel_pack(ox, oy, sc, title, sub, s, poses, ring=True):
    out = [text(ox, oy - S0 * sc - 54, title, 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 40, sub, S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)
    polys = [sq(*q) for q in poses]
    exc = max([max(-x, x - s, -y, y - s) for P in polys for x, y in P] or [0.0])
    mg = min([L.sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2])
              for i in range(len(poses)) for j in range(i + 1, len(poses))] or [0.0])
    names, isfree, nf = [], [], 0
    for (cx, cy, th) in poses:
        nm = L.snap(cx, cy, th, s, dtol=1e-3, atol=0.05)
        if nm:
            names.append(nm)
            isfree.append(False)
        else:
            names.append(f"f{nf}")
            nf += 1
            isfree.append(True)
    for i, P in enumerate(polys):
        out.append(poly(ox, oy, sc, P, "#ef9a9a" if isfree[i] else "#90caf9",
                        "#c62828" if isfree[i] else "#1565c0", 0.6))
        cx, cy, th = poses[i]
        out.append(text(ox + cx * sc, oy - cy * sc + 4, names[i], 9.5, "#000", True, "middle"))
        if isfree[i]:
            out.append(text(ox + cx * sc, oy - cy * sc + 15,
                            f"{math.degrees(L.tmod(th)):.2f}°", 8, "#333", False, "middle"))
    if ring:
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                if L.sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2]) < 1e-6:
                    A, B = polys[i], polys[j]
                    best = (9.0, None)
                    for X, Y in ((A, B), (B, A)):
                        for v in X:
                            for k in range(4):
                                p, q = Y[k], Y[(k + 1) % 4]
                                ex, ey = q[0] - p[0], q[1] - p[1]
                                ln = ex * ex + ey * ey
                                t = max(0.0, min(1.0, ((v[0] - p[0]) * ex
                                                       + (v[1] - p[1]) * ey) / ln))
                                f = (p[0] + t * ex, p[1] + t * ey)
                                dd = math.hypot(v[0] - f[0], v[1] - f[1])
                                if dd < best[0]:
                                    best = (dd, f)
                    f = best[1]
                    out.append(f'<circle cx="{ox + f[0] * sc:.1f}" cy="{oy - f[1] * sc:.1f}" '
                               f'r="4.5" fill="none" stroke="#2e7d32" stroke-width="2"/>')
    e, _ = wrap(ox, oy + 16, f"{len(poses) - nf} slot squares + {nf} free squares; min pairwise "
                             f"SAT separation {mg:+.2e}; worst containment excursion {exc:+.2e}; "
                             f"side {s:.6f}", S0 * sc, 8.5, "#444")
    out += e
    return out, names, exc, mg, oy + 16 + 11.5 * max(1, len(e))


# ------------------------------------------------------------------ panel 3
def panel_hyp(ox, oy, sc, boxes, pcs, pincores, hypcores, clip, pockets, lane1, s):
    npin = len(boxes) - 1
    out = [text(ox, oy - S0 * sc - 54, "panel 3: the hypothesis alone — the three cores, the "
                                       "clipped box, and the pockets", 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 40,
                "BODIES (filled): the five pin squares and nothing else. CORES (solid outlines, "
                "no fill): black = stock axis core K(a), teal = A135 exact axis core, purple = "
                "polygon core K'; each pin carries its stock (light blue) and exact (dark blue) "
                "core. SCHEMATIC (thin dashed, no fill): black = the original centre box, orange "
                "= the pin-clipped centre box per tilt sub-bin and their union at the EXACT pin "
                "core, pale orange dotted = the same clip at the STOCK pin core (A131 as "
                "deployed), amber = a corner cell whose A118 lane count is <= 1. Red "
                "dashed segments = a measured pocket between K'(B) and its nearest neighbour "
                "narrower than 1, i.e. no further unit square fits in it.",
                S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)
    for i in range(npin):
        b = boxes[i]
        cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
        if pincores[i]["is_pin"]:
            out.append(poly(ox, oy, sc, sq(cx, cy, 0.0), "#eceff1", "#90a4ae", 0.5, 1.0))
            out.append(poly(ox, oy, sc, pincores[i]["P_stock"], "none", "#01579b", 0.0, 0.9))
            out.append(poly(ox, oy, sc, pincores[i]["P"], "none", "#1a237e", 0.0, 1.2))
            out.append(text(ox + cx * sc, oy - cy * sc + 4, f"P{i}", 9.0, "#263238", True,
                            "middle"))
        else:
            out.append(rect(ox, oy, sc, b["x0"], b["x1"], b["y0"], b["y1"], "none", "#000",
                            0.0, 1.2, "5,3"))
            out.append(poly(ox, oy, sc, [tuple(v) for v in pcs[i].P], "none", "#4527a0", 0.0, 1.4))
            out.append(text(ox + cx * sc, oy - cy * sc + 4, f"H{i}", 9.0, "#000", True, "middle"))
    for c in lane1:
        try:
            (x, y) = M.slot_centres([c], s)[0]
        except Exception:
            continue
        out.append(rect(ox, oy, sc, x - 0.5, x + 0.5, y - 0.5, y + 0.5,
                        "none", "#f57f17", 0.0, 1.6, "6,3"))
        out.append(text(ox + x * sc, oy - y * sc + 4, f"{c} LANE<=1", 7.0, "#e65100", True,
                        "middle"))
    b = boxes[-1]
    out.append(rect(ox, oy, sc, b["x0"], b["x1"], b["y0"], b["y1"], "none", "#000", 0.0, 1.4,
                    "5,3"))
    for (t0d, t1d, r) in clip["bins_f"]:
        if r is None:
            continue
        out.append(rect(ox, oy, sc, r[0], r[1], r[2], r[3], "none", "#e65100", 0.0, 0.8, "2,2"))
    if clip.get("stock", {}).get("union_rect_f"):
        (sx0, sx1, sy0, sy1) = clip["stock"]["union_rect_f"]
        out.append(rect(ox, oy, sc, sx0, sx1, sy0, sy1, "none", "#ffb74d", 0.0, 1.0, "2,3"))
    if clip.get("union_rect_f"):
        (ux0, ux1, uy0, uy1) = clip["union_rect_f"]
        out.append(rect(ox, oy, sc, ux0, ux1, uy0, uy1, "none", "#e65100", 0.0, 1.8, "4,2"))
    out.append(poly(ox, oy, sc, [tuple(v) for v in pcs[-1].P], "none", "#4527a0", 0.0, 1.8))
    out.append(poly(ox, oy, sc, core_sq(hypcores["stock"]), "none", "#000000", 0.0, 1.9))
    if hypcores["exact"] is not None:
        out.append(poly(ox, oy, sc, core_sq(hypcores["exact"]), "none", "#00695c", 0.0, 1.9))
    kk = pcs[-1].P.mean(0)
    out.append(text(ox + kk[0] * sc, oy - kk[1] * sc - 3, "K'(B)", 9.0, "#311b92", True, "middle"))
    out.append(text(ox + kk[0] * sc, oy - kk[1] * sc + 8,
                    f"a_stock {float(hypcores['stock'].a):.6f} / a_exact "
                    + (f"{float(hypcores['exact'].a):.6f}" if hypcores["exact"] is not None
                       else "n/a")
                    + f" / area K' {pcs[-1].area():.6f}", 6.6, "#311b92", False, "middle"))
    for pk_ in pockets[:8]:
        if pk_["gap"] >= 1.0:
            continue
        (ax, ay), (bx, by) = pk_["seg"]
        out.append(f'<line x1="{ox + ax * sc:.1f}" y1="{oy - ay * sc:.1f}" '
                   f'x2="{ox + bx * sc:.1f}" y2="{oy - by * sc:.1f}" stroke="#d50000" '
                   f'stroke-width="2" stroke-dasharray="2,2"/>')
        out.append(text(ox + 0.5 * (ax + bx) * sc, oy - 0.5 * (ay + by) * sc - 3,
                        f"{pk_['to']} {pk_['gap']:.3f}", 7.0, "#d50000", True, "middle"))
    e, yy = wrap(ox, oy + 16,
                 f"pin-clip at the EXACT pin core a = {clip['a_pin_exact']:.9f}: kept volume "
                 f"{clip['kept_vol']:.4f} over {clip['nsub']} tilt sub-bins ({clip['n_empty']} "
                 f"of them EMPTY), union box {clip['kept_union']:.4f}. At the STOCK core a = "
                 f"{clip['a_pin_stock']:.6f} (A131 as deployed) the clip keeps "
                 f"{clip['stock']['kept_vol']:.4f}"
                 + ("  — the box is NOT emptied, so the clip is a shrink, not a kill."
                    if not clip["empty"] else
                    ("  — EMPTY AT THE EXACT CORE: this node is DEAD by pin geometry"
                     + (", and the deployed stock-core clip does NOT see it."
                        if not clip["stock"]["empty"] else "."))),
                 S0 * sc, 8.5, "#444")
    out += e
    nn = [p for p in pockets if p["gap"] < 1.0]
    e, _ = wrap(ox, yy + 2,
                (f"pockets narrower than 1: {len(nn)} of {len(pockets)} measured clearances "
                 f"(K'(B) to each exact pin core and to each wall). Narrowest: "
                 + "; ".join(f"{p['to']} {p['gap']:.4f}" for p in pockets[:4]))
                if pockets else "no pockets measured", S0 * sc, 8.5, "#d50000")
    out += e
    return out, yy + 2 + 11.5 * max(1, len(e))


# ------------------------------------------------------------------ pockets
def pockets_of(pc, pincores, s):
    P = [tuple(v) for v in pc.P]
    out = []
    for i, pcore in enumerate(pincores):
        g = poly_dist(P, pcore["P"])
        a = min(P, key=lambda v: (v[0] - pcore["c"][0]) ** 2 + (v[1] - pcore["c"][1]) ** 2)
        b = min(pcore["P"], key=lambda v: (v[0] - a[0]) ** 2 + (v[1] - a[1]) ** 2)
        out.append(dict(to=f"P{i}", gap=g, seg=[a, b], kind="pin core"))
    xs = [v[0] for v in P]
    yy = [v[1] for v in P]
    for nm, g, seg in (("wall x=0", min(xs), [(min(xs), sum(yy) / len(yy)),
                                              (0.0, sum(yy) / len(yy))]),
                       ("wall x=s", s - max(xs), [(max(xs), sum(yy) / len(yy)),
                                                  (s, sum(yy) / len(yy))]),
                       ("wall y=0", min(yy), [(sum(xs) / len(xs), min(yy)),
                                              (sum(xs) / len(xs), 0.0)]),
                       ("wall y=s", s - max(yy), [(sum(xs) / len(xs), max(yy)),
                                                  (sum(xs) / len(xs), s)])):
        out.append(dict(to=nm, gap=float(g), seg=seg, kind="wall"))
    out.sort(key=lambda r: r["gap"])
    return out


# ------------------------------------------------------------------ right-panel geometry
def right_poses(camp, nid, d, boxes, clip):
    fams = shadow_families(nid)
    for sid in fams:
        sh = shadow_geom(sid)
        if not sh:
            continue
        poses = [tuple(map(float, f)) for f in sh["free"]] + \
                [(x, y, 0.0) for (x, y) in M.slot_centres(sh["slots"], sh["s"])]
        return poses, float(sh["s"]), sid, (
            f"A107 shadow {sid} minimised to s* = {sh['s']:.6f} (s* - s-hat {sh['ds']:+.6f}), "
            f"{sh['nsquares']} squares, {sh['nfree']} free; this node is one of the "
            f"{sh['nnodes']} nodes the family explains. THIS is the panel the PI labels from: "
            f"the square names below are its names.")
    pk = [p for p in d.get("packing", []) if float(p.get("y", 0.0)) > 0.5]
    poses = [(float(p["cx"]), float(p["cy"]), float(p["theta"])) for p in pk]
    b = boxes[-1]
    cx0, cy0 = clip.get("centre") or (0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"]))
    poses.append((cx0, cy0, math.radians(0.5 * (b["th0"] + b["th1"]))))
    for i in range(len(boxes) - 1):
        bb = boxes[i]
        poses.append((0.5 * (bb["x0"] + bb["x1"]), 0.5 * (bb["y0"] + bb["y1"]), 0.0))
    return poses, float(d.get("s") or S0), None, (
        "NO A107 shadow family covers this node: the raw integral dual support at the certified "
        "side s0, plus the five pins and the conditioned square at the centre of its CLIPPED box "
        "and tilt window. It is NOT a packing and NOT minimised — the overlaps are exactly the "
        "'impossible column' effect panel 1 draws in red.")


# ------------------------------------------------------------------ page
LEGEND = (
    "LEGEND — BODIES are filled; CORES are solid outlines with no fill; SCHEMATIC objects "
    "(centre boxes, clipped boxes, lane cells) are THIN DASHED outlines with no fill and are "
    "NOT square bodies. | PANEL 1, the LP dual support of this node's record at s0: fill = dual "
    "weight y on one sequential scale (pale yellow y->0, dark orange y=1); grey P0..P4 = the "
    "PINS, drawn as pins (zero-tilt-width cores), each carrying BOTH inner cores — thin light "
    "blue = the STOCK pin core (half-side 1/2 - delta = 0.49, what the LP pruned against), thin "
    "dark blue = A135's EXACT pin core (half-side 1/2 - delta/sqrt2, certified); bright cyan + H "
    "= the conditioned square at the centre of its CLIPPED box and the MID-TILT, faint cyan = "
    "the two extremal tilts. H carries THREE cores: solid BLACK = the stock axis core K(a) the "
    "LP pruned against, solid TEAL = A135's exact axis core, filled PURPLE = the certified "
    "polygon core K'(B) (A132) — a_stock / a_exact / area K' are captioned in panel 3. Black "
    "dashed = the original centre box; orange dashed = the pin-clipped centre box (A131). RED "
    "DASHED = a dual-support column that overlaps a hypothesis square — H OR a pin — at EVERY "
    "pose of its box; each is labelled with WHICH cores it clears and which it meets. | PANEL 2 "
    "= a real packing: blue = slot square (named cell), red = free square (f-index + tilt), "
    "green ring = contact at gap < 1e-6; these are the names the PI labels from. | PANEL 3 = the "
    "hypothesis alone: the three cores captioned, the clip per tilt sub-bin, the lane <= 1 "
    "corner cells and the measured pockets.")


def build_page(rec, camp):
    nid = rec["id"]
    d, recpath = load_node(camp, nid)
    boxes = d["hyp"]["boxes"]
    npin = len(boxes) - 1
    s = float(d.get("s") or S0)
    pcs = [polycore.build(Box.from_json(b)) for b in boxes]
    # --- the three cores of the conditioned square, and both cores of every pin
    HB = Box.from_json(boxes[-1])
    k_stock = HB.core()
    try:
        a_ex, a_st, ok_ex = exactcore.exact_a(HB)
    except Exception:
        a_ex, a_st, ok_ex = None, k_stock.a, False
    hypcores = dict(stock=k_stock, exact=(Core(k_stock.kx, k_stock.ky, k_stock.tm, a_ex, HB)
                                          if a_ex is not None else None),
                    cert=bool(ok_ex))
    pincores = []
    for i in range(npin):
        Bi = Box.from_json(boxes[i])
        ki = Bi.core()
        try:
            a, a0, ok = exactcore.exact_a(Bi)
        except Exception:
            a, a0, ok = None, ki.a, False
        cx, cy = 0.5 * (boxes[i]["x0"] + boxes[i]["x1"]), 0.5 * (boxes[i]["y0"] + boxes[i]["y1"])
        af = float(a) if a is not None else float(a0)
        pincores.append(dict(a=af, a_stock=float(a0), cert=bool(ok), c=(cx, cy),
                             is_pin=(boxes[i]["th1"] <= boxes[i]["th0"] + 1e-12),
                             P=sq(cx, cy, 0.0, af), P_stock=sq(cx, cy, 0.0, float(a0)),
                             core_exact=(Core(ki.kx, ki.ky, ki.tm, a, Bi)
                                         if a is not None else None),
                             core_stock=ki))
    # pin clip
    sl = slots_for(camp, nid)
    B = Box.from_json(boxes[-1])
    _tp = [p for p in pincores if p["is_pin"]] or pincores
    a_ex_pin = pinclip.Fr(str(min(p["a"] for p in _tp))).limit_denominator(10 ** 14)
    a_st_pin = (pinclip.Fr(str(min(p["a_stock"] for p in _tp))).limit_denominator(10 ** 14)
                if camp == "A60" else pinclip.A_PIN)

    def _clip(ap):
        try:
            return pinclip.clip_node(B, sl, nsub=8, a_pin=ap)
        except Exception as ex:                               # degenerate pins
            return dict(refused=True, reason=str(ex)[:60], bins=[], kept_vol=1.0,
                        kept_union=1.0, union_rect=None, empty=False, n_empty=0)
    cl_stock = _clip(a_st_pin)
    cl = _clip(a_ex_pin)                       # the EXACT-core clip is the one drawn heavy
    clip_stock = dict(kept_vol=float(cl_stock["kept_vol"]),
                      kept_union=float(cl_stock["kept_union"]),
                      n_empty=int(cl_stock["n_empty"]), empty=bool(cl_stock["empty"]),
                      union_rect_f=([float(v) for v in cl_stock["union_rect"]]
                                    if cl_stock.get("union_rect") else None))
    clip = dict(nsub=8, kept_vol=float(cl["kept_vol"]), kept_union=float(cl["kept_union"]),
                n_empty=int(cl["n_empty"]), empty=bool(cl["empty"]),
                refused=bool(cl.get("refused")), reason=cl.get("reason"),
                bins_f=[(float(pinclip.deg_of_t(t0)), float(pinclip.deg_of_t(t1)),
                         ([float(v) for v in r] if r is not None else None))
                        for (t0, t1, r) in cl["bins"]],
                union_rect_f=([float(v) for v in cl["union_rect"]]
                              if cl.get("union_rect") else None),
                a_pin_exact=float(a_ex_pin), a_pin_stock=float(a_st_pin), stock=clip_stock)
    if clip["union_rect_f"]:
        u = clip["union_rect_f"]
        clip["centre"] = (0.5 * (u[0] + u[1]), 0.5 * (u[2] + u[3]))
    else:
        clip["centre"] = (0.5 * (boxes[-1]["x0"] + boxes[-1]["x1"]),
                          0.5 * (boxes[-1]["y0"] + boxes[-1]["y1"]))
    pockets = pockets_of(pcs[-1], [p for p in pincores if p['is_pin']], s)
    lane = lane_of(nid)
    lcells = {c["cell"]: c for c in (lane["cells"] if lane else [])}
    lane1 = sorted(c for c, v in lcells.items()
                   if str(v.get("verdict", "")).startswith(("LANE<=1", "LANE<=0")))

    W1 = S0 * SC + 66
    oy = 140 + S0 * SC
    body, _ = wrap(30, 16, LEGEND, 3 * W1 - 20, 8.5, "#333")
    tau = float(d.get("tau") or 0.0)
    bud = int(d.get("budget") or 5)
    sub = (f"tau {tau:.9f} / budget {bud} (eta {tau - bud:+.2e}), minmass "
           f"{float(d.get('minmass') or 0.0):.3f}, converged {d.get('converged')}; "
           f"record {recpath}")
    p1, imposs, bad, yb1 = panel_lp(30, oy, SC, f"{nid} — panel 1: LP dual support at s0 = "
                                           f"{S0:.6f}", sub, d, boxes, pcs, pincores, hypcores,
                               clip, s)
    body += p1
    poses, s2, sid, prov = right_poses(camp, nid, d, boxes, clip)
    p2, names2, exc, mg, yb2 = panel_pack(30 + W1, oy, SC,
                                     f"{nid} — panel 2: the near-packing"
                                     + (f" ({sid})" if sid else " (raw support)"), prov, s2, poses)
    body += p2
    assert exc <= 1e-4, f"{nid}: panel 2 containment violated by {exc:.2e}"
    p3, yb3 = panel_hyp(30 + 2 * W1, oy, SC, boxes, pcs, pincores, hypcores, clip, pockets,
                        lane1, s)
    body += p3

    y = max(yb1, yb2, yb3) + 26

    def add(t, size=9.5, col="#222", bold=False):
        nonlocal y
        e, y = wrap(30, y, t, 3 * W1 - 20, size, col, bold)
        body.extend(e)
        y += 3.0

    b = boxes[-1]
    add(f"{nid}  —  {camp} {rec['cls']}, level {rec['level']}, recorded {rec['verdict']}; "
        f"budget {bud} = 11 − {npin} pins − 1 conditioned square; subtree cost "
        f"{rec['subtree_s']:.0f} s = {rec['subtree_cpuh']:.2f} CPU-h (rank {rec['rank']} of "
        f"{rec['n_pop']})", 12, "#000", True)
    a_st = float(hypcores["stock"].a)
    a_ex = float(hypcores["exact"].a) if hypcores["exact"] is not None else None
    add(f"box B: x [{b['x0']:.6f}, {b['x1']:.6f}]  y [{b['y0']:.6f}, {b['y1']:.6f}]  tilt "
        f"[{b['th0']:.4f}°, {b['th1']:.4f}°]   |   THE THREE CORES OF H — stock axis core K(a): "
        f"a_stock = {a_st:.9f}, area {(2 * a_st) ** 2:.6f} (this is what the LP pruned against); "
        f"A135 EXACT axis core: a_exact = "
        + (f"{a_ex:.9f}, area {(2 * a_ex) ** 2:.6f} ({(a_ex / a_st - 1) * 100:.2f}% larger "
           f"half-side, certified {hypcores['cert']})" if a_ex is not None else "n/a")
        + f"; polygon core K'(B): {len(pcs[-1].verts)} certified vertices, area "
          f"{pcs[-1].area():.6f} = {pcs[-1].area() / ((2 * a_st) ** 2):.3f}x area K(a).")
    add(f"PIN-CLIP (A131 `pinclip`, exact rationals, 8 tilt sub-bins), run at BOTH pin cores: at "
        f"the STOCK a = {clip['a_pin_stock']:.6f} it keeps {clip['stock']['kept_vol']:.4f} "
        f"({clip['stock']['n_empty']}/8 sub-bins empty); at A135's EXACT a = "
        f"{clip['a_pin_exact']:.9f} it keeps {clip['kept_vol']:.4f}, union box "
        f"{clip['kept_union']:.4f} of the original area, {clip['n_empty']} of 8 sub-bins EMPTY"
        + ("; the clipped box is where H is drawn in panels 1 and 3."
           if clip["union_rect_f"] else "; the clip is REFUSED here (%s), so H is drawn at the "
                                        "original box centre." % clip.get("reason")),
        9.5, "#b71c1c" if clip["empty"] else "#222", bool(clip["empty"]))
    tp = [p for p in pincores if p["is_pin"]]
    add(f"PIN CORES, both drawn: STOCK half-side {tp[0]['a_stock']:.9f} (light blue) vs "
        f"A135 EXACT half-side {tp[0]['a']:.9f} (dark blue) = 1/2 - delta/sqrt2 — an "
        f"enlargement of {100.0 * (tp[0]['a'] / tp[0]['a_stock'] - 1.0):.2f}% per "
        f"side; all {len(tp)} pins certified: {all(p['cert'] for p in tp)}"
        + (f"; {npin - len(tp)} further hypothesis box(es) carry a TILT WINDOW and are "
           f"conditioned squares, not pins." if len(tp) < npin else ".")
        + " A132's attribution found a quarter of the K'-excluded weight lives in exactly "
          "this slop.")
    add(f"IMPOSSIBLE COLUMNS: {len(imposs)} of {len(d.get('packing') or [])} dual-support "
        f"columns overlap a hypothesis square at every one of the {NPOSE}^3 sampled poses — "
        f"{sum(1 for r in imposs if r['box'] == npin)} against H's box "
        f"(weight {sum(r['y'] for r in imposs if r['box'] == npin):.4f}), "
        f"{sum(1 for r in imposs if r['box'] != npin)} against an EXACT PIN CORE "
        f"(weight {sum(r['y'] for r in imposs if r['box'] != npin):.4f}); total weight "
        f"{sum(r['y'] for r in imposs):.4f} of {sum(float(p.get('y', 0.0)) for p in d.get('packing') or []):.4f} "
        f"against slack {tau - (bud - 1):+.4f}. Every one re-verified by an independent SAT at "
        f"{NPOSE}^3 poses of the owning box, and labelled on the drawing with which core it "
        f"CLEARS and which it MEETS. Core split over the red-dashed set: "
        + "; ".join(f"{k} x{v}" for k, v in sorted(
            __import__("collections").Counter(
                r["core_verdict"].split(": ", 1)[1] for r in imposs).items(),
            key=lambda kv: -kv[1])[:6]) + ".", 9.5, "#b71c1c", bool(imposs))
    add("POCKETS (exact convex-polygon distance from K'(B)): "
        + "; ".join(f"{p['to']} {p['gap']:.4f}" for p in pockets[:7])
        + f"   [{sum(1 for p in pockets if p['gap'] < 1.0)} of {len(pockets)} narrower than 1 — "
          f"no further unit square fits in those]")
    if lane:
        add("LANE COUNT (A118 stored verdicts — AXIS-CORE verdicts K(a), not K'; A141's K' lane "
            "run had not landed when this page was drawn): "
            + "; ".join(f"{c['cell']}:{c['verdict']}"
                        + (f"(ncond_pot {c['ncond_pot']})" if c.get("ncond_pot") else "")
                        for c in lane["cells"][:14])
            + f"   [{len(lane['cells'])} cells tested]")
    else:
        add("LANE COUNT: A118 has no stored record for this node.")
    look = []
    if clip["empty"]:
        look.append("THE PIN-CLIP AT THE EXACT PIN CORE EMPTIES THIS BOX AT ALL 8 TILT SUB-BINS "
                    "— the node is dead by pin geometry alone"
                    + ("" if clip["stock"]["empty"] else
                       ", and the deployed stock-core clip does not see it")
                    + "; nothing below needs reading")
    if lane1:
        look.append("corners/slots with LANE <= 1 (a SECOND meeter is what the two-meeter cover "
                    "needs): " + ", ".join(lane1))
    nn = [p for p in pockets if p["gap"] < 1.0]
    if nn:
        look.append(f"{len(nn)} pocket(s) between K'(B) and its neighbour narrower than 1 — "
                    + ", ".join(f"{p['to']} at {p['gap']:.3f}" for p in nn[:5])
                    + " — nothing fits there, so any square the LP puts in that region is a "
                      "column the geometry forbids")
    if imposs:
        look.append(f"{len(imposs)} red-dashed column(s) already impossible under the hypothesis "
                    f"({sum(1 for r in imposs if r['box'] != npin)} of them the PINS')")
    add("WHAT TO LOOK FOR — " + ("; ".join(look) if look else
                                 "no LANE <= 1 corner and no pocket narrower than 1: this node's "
                                 "geometry gives the reading nothing free; read the load path in "
                                 "panel 2 instead."), 10, "#1b5e20", True)
    add(f"geometry check: {len(poses)} squares drawn in panel 2, worst containment excursion "
        f"{exc:+.2e}, min pairwise SAT separation {mg:+.2e}; {bad} support column(s) outside the "
        f"container skipped in panel 1; {len(pcs[-1].verts)} K'(B) vertices certified; "
        f"{len(imposs)} red-dashed column(s) SAT-re-verified.", 9.0, "#555")

    W = 3 * W1 + 60
    H = int(y + 20)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ["</svg>"])
    p = os.path.join(OUT, f"{nid}.svg")
    open(p, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(p)

    nfree = sum(1 for n2 in names2 if n2.startswith("f"))
    row = dict(
        file=f"{nid}.svg", shadow=(sid or "-"),
        classes_or_sources=f"{camp} {rec['cls']}; record {recpath}",
        k=f"k{len(poses)} ({len(poses) - nfree} slot + {nfree} free)",
        s_star=(f"{s2:.6f}" if sid else f"n/a (raw support at s0, overlap {max(0.0, -mg):.3f})"),
        s_star_minus_shat=(f"{s2 - SHAT:+.6f}" if sid else "n/a"),
        nodes_explained=(str(shadow_geom(sid)["nnodes"]) if sid else "1 (this node)"),
        levels=f"L{rec['level']}", n_free_squares=nfree,
        common_tilt=(f"{shadow_geom(sid)['common_tilt']:.3f} deg"
                     if sid and shadow_geom(sid).get("common_tilt") is not None else "no"),
        flexes=(shadow_geom(sid)["analysis"].get("flexes_fixed_s") if sid else "-"),
        coincides_with=";".join(shadow_families(nid)) or "-",
        polycore_status=(f"K'(B) {len(pcs[-1].verts)} verts, area x{pcs[-1].area() / ((2 * a_st) ** 2):.3f} "
                         f"vs K(a); a_stock {a_st:.6f} / a_exact "
                         + (f"{a_ex:.6f}" if a_ex is not None else "n/a")
                         + f"; {rec.get('n_poly_only')} support column(s) K'-only, weight "
                           f"{rec.get('w_poly_only')}"),
        clip_kept=(f"exact-core vol {clip['kept_vol']:.4f} (stock-core "
                   f"{clip['stock']['kept_vol']:.4f}), union {clip['kept_union']:.4f}, "
                   f"{clip['n_empty']}/8 sub-bins empty"
                   + (" — EMPTY: DEAD by pin geometry" if clip["empty"] else "")
                   + (" [REFUSED: %s]" % clip.get("reason") if clip["refused"] else "")),
        lane_1_corners=(",".join(lane1) if lane1 else "none"),
        narrowest_pocket=f"{pockets[0]['to']} {pockets[0]['gap']:.4f}" if pockets else "-",
        subtree_cost_s=f"{rec['subtree_s']:.0f}", subtree_rank=rec["rank"],
        budget=bud, tau=f"{tau:.9f}", minmass=f"{float(d.get('minmass') or 0):.3f}",
        n_support=len(d.get("packing") or []),
        n_impossible=len(imposs),
        n_impossible_pin=sum(1 for r in imposs if r["box"] != npin),
        n_impossible_certified=sum(1 for r in imposs if r["certified"]),
        exact_pin_core=f"{tp[0]['a']:.9f} (stock {tp[0]['a_stock']:.6f}), {len(tp)} pin(s)"
                       + (f" + {npin - len(tp)} extra conditioned box(es)"
                          if len(tp) < npin else ""),
        right_panel=prov.split(";")[0][:120],
        PI_reading="", PI_load_path="", PI_binding_contact="", PI_drain_or_kill="")
    summ = dict(id=nid, camp=camp, cls=rec["cls"], level=rec["level"], rank=rec["rank"],
                subtree_s=rec["subtree_s"], subtree_cpuh=rec["subtree_cpuh"],
                verdict=rec["verdict"], shadow=sid, families=shadow_families(nid),
                tau=tau, budget=bud, s_star=(s2 if sid else None),
                n_support=len(d.get("packing") or []), n_impossible=len(imposs),
                n_impossible_pin=sum(1 for r in imposs if r["box"] != npin),
                n_impossible_certified=sum(1 for r in imposs if r["certified"]),
                w_impossible=round(sum(r["y"] for r in imposs), 6),
                impossible=imposs, clip_empty=bool(clip["empty"]),
                clip_empty_stock=bool(clip["stock"]["empty"]),
                clip=dict((k, v) for k, v in clip.items() if k != "bins_f"),
                clip_bins=clip["bins_f"], pockets=pockets, lane1=lane1,
                lane_cells=[dict(cell=c["cell"], verdict=c["verdict"],
                                 ncond_pot=c.get("ncond_pot")) for c in (lane["cells"] if lane
                                                                         else [])],
                pincore_a=tp[0]["a"], pincore_a_stock=tp[0]["a_stock"],
                pincore_as=[p["a"] for p in pincores],
                pin_is_pin=[bool(p["is_pin"]) for p in pincores],
                pincores_certified=all(p["cert"] for p in tp),
                a_stock=a_st, a_exact=a_ex, a_exact_certified=hypcores["cert"],
                poly_verts=len(pcs[-1].verts), poly_area=pcs[-1].area(),
                panel2_min_sat=mg, panel2_exc=exc, width=int(W), height=H,
                record=recpath, box=b)
    return row, summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camp", default="A57")
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=20)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    pop = json.load(open(os.path.join(BASE, "results", "population142.json"), encoding="utf-8"))
    key = "rank_a57" if a.camp == "A57" else "rank_a60"
    rank = pop[key]
    n_pop = len(rank)
    rows, summ = [], []
    for i in range(a.lo, min(a.hi, len(rank))):
        rec = dict(rank[i])
        rec["rank"] = i + 1
        rec["n_pop"] = n_pop
        r, sm = build_page(rec, a.camp)
        rows.append(r)
        summ.append(sm)
        print(f"[{i + 1:3d}] {rec['id']:34s} -> {sm['width']}x{sm['height']}  "
              f"imposs {sm['n_impossible']} (pins {sm['n_impossible_pin']})  "
              f"clip {sm['clip']['kept_vol']:.3f}  lane1 {sm['lane1']}  "
              f"pocket {sm['pockets'][0]['gap']:.3f}", flush=True)
    p = os.path.join(BASE, "results", f"gallery142_{a.camp}_{a.lo}_{a.hi}.json")
    json.dump(dict(rows=rows, summary=summ), open(p, "w", encoding="utf-8"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
