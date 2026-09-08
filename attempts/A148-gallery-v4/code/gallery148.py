"""A148 -- the v4 review page: three panels, built around ONE question.

  "Can the remaining squares fit in the white space?"

The v3 pages (docs/shadows/{k0v3,a57v3}) drew everything the code knew and the PI found them busy;
worse, they drew IMPOSSIBLE overlaps (the LP relaxation's slack) with the same weight as real
geometry.  v4 fixes the reading order: the geometry panel is the big one and says what is FREE;
the LP panel is demoted and captioned as a relaxation; the packing panel is small and is only
there for the names.

  PANEL G  "GEOMETRY: what is still free"  (largest).  The container at s0.  Pins as light-blue
           squares with their EXACT cores (A135) as a thin inner outline.  Every conditioned
           square H cyan at the box centre and the mid-tilt with its polygon core K'(B) (A132)
           FILLED -- the stock and exact AXIS cores are not drawn at all, their half-sides are in
           the caption.  The FEASIBLE-CENTRE REGION shaded green (geo148: certified inner
           approximation, margin-guarded), the certified-blocked complement left white and the
           undecided band pale.  Pockets narrower than 1 hatched grey with the width printed.
           A144 guard lines thin, with chord sum and rhs at the margin when the sum is within
           0.15 of s0.  Each corner/slot tagged with A141's K' lane verdict.  A131's exact clip
           drawn inside the original centre box.
  PANEL S  "LP support after the exact-core / K' re-solve" (medium).  The dual support of the
           node's LATEST record, fill = dual weight (A107 v2 ramp), K' outlined, columns that
           overlap K' red-dashed and counted as impossible.
  PANEL N  "nearest real packing" (small).  A107's minimised shadow / A128's near-packing, the
           container at s* with s0 overlaid dashed and the realisability banner.

  HEADER   id, class, level, tau/budget/eta, family, A142 subtree cost, the generated WHAT TO
           LOOK FOR line, and the verdict of every geometric leaf already run on the node.
  FOOTER   three fixed lines saying what the three panels ARE, and the drawing conventions.

Read-only on every campaign; writes only docs/shadows/<set>/ and this attempt's results/.

    set PYTHONDONTWRITEBYTECODE=1 && python code/gallery148.py --set k0v4
"""
import argparse
import csv
import json
import math
import os
import sys
import time
import xml.dom.minidom

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A57-shadow-trees", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A131-pin-clip", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A107-shadow-gallery", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           os.path.join(ATT, "A142-a57-review-gallery", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import geo148 as G                                                  # noqa: E402
import data148 as D                                                 # noqa: E402
import polycore                                                     # noqa: E402
import minimise as M                                                # noqa: E402
import shadowlib as L                                               # noqa: E402
from caselp import Box                                              # noqa: E402

S0 = G.S0
SHAT = G.SHAT

SC_G, SC_S, SC_N = 158.0, 100.0, 76.0
MARG, GAP = 30.0, 34.0

CY, PURPLE, PURPLE_D = "#00e5ff", "#7e57c2", "#4527a0"
PINF, PINS_ = "#b3e5fc", "#0277bd"
GREEN, GREENP = "#2e7d32", "#a5d6a7"


# ------------------------------------------------------------------ svg primitives (new)
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, t, size=10, col="#222", bold=False, anchor="start", op=1.0):
    b = ' font-weight="bold"' if bold else ""
    o = f' fill-opacity="{op:.2f}"' if op < 1.0 else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}{o}>{esc(t)}</text>')


def wrap(x, y, t, width_px, size=9.0, col="#222", bold=False, lead=None):
    per = max(10, int(width_px / (size * 0.555)))
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
    return ([txt(x, y + i * lead, ln, size, col, bold) for i, ln in enumerate(lines)],
            y + len(lines) * lead)


class Pane:
    """one panel's coordinate frame: world (x, y) -> page px."""

    def __init__(self, ox, oy, sc):
        self.ox, self.oy, self.sc = ox, oy, sc

    def X(self, x):
        return self.ox + x * self.sc

    def Y(self, y):
        return self.oy - y * self.sc

    def poly(self, P, fill, stroke, op=0.6, w=1.4, dash="", sop=1.0):
        pts = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in P)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        so = f' stroke-opacity="{sop:.2f}"' if sop < 1.0 else ""
        return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.2f}" '
                f'stroke="{stroke}" stroke-width="{w}"{d}{so}/>')

    def rect(self, x0, x1, y0, y1, fill, stroke, op=0.0, w=1.3, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<rect x="{self.X(x0):.1f}" y="{self.Y(y1):.1f}" '
                f'width="{max(0.0, (x1 - x0)) * self.sc:.2f}" '
                f'height="{max(0.0, (y1 - y0)) * self.sc:.2f}" fill="{fill}" '
                f'fill-opacity="{op:.2f}" stroke="{stroke}" stroke-width="{w}"{d}/>')

    def line(self, x0, y0, x1, y1, col, w=1.0, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{self.X(x0):.1f}" y1="{self.Y(y0):.1f}" x2="{self.X(x1):.1f}" '
                f'y2="{self.Y(y1):.1f}" stroke="{col}" stroke-width="{w}"{d}/>')

    def text(self, x, y, t, size=9, col="#222", bold=False, anchor="middle", dy=0.0):
        return txt(self.X(x), self.Y(y) + dy, t, size, col, bold, anchor)

    def container(self, s, label=True, col="#000", w=2.2, dash=""):
        out = [self.rect(0, s, 0, s, "none", col, 0.0, w, dash)]
        if label:
            out.append(txt(self.X(s), self.Y(s) - 5, f"s0 = {s:.6f}", 9, col, True, "end"))
        return out


DEFS = ('<defs>'
        '<pattern id="hatch" width="6" height="6" patternTransform="rotate(45)" '
        'patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#9e9e9e" stroke-width="2.2"/></pattern>'
        '<pattern id="hatchr" width="6" height="6" patternTransform="rotate(-45)" '
        'patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#e57373" stroke-width="2.0"/></pattern>'
        '</defs>')


def wcol(y, dark=False):
    """A107 v2: one sequential pale-yellow -> dark-orange ramp on the dual weight."""
    y = 0.0 if y is None else max(0.0, min(1.0, float(y)))
    h = 46.0 - 22.0 * y
    l = (88.0 - 46.0 * y) - (22.0 if dark else 0.0)
    return f"hsl({h:.0f},92%,{max(l, 12.0):.0f}%)"


# ================================================================== PANEL G
def panel_geometry(pn, node, width_px):
    """the main panel.  Returns (elements, y after the caption, facts)."""
    s = S0
    out = [txt(pn.ox, pn.oy - s * pn.sc - 40, "PANEL G — GEOMETRY: what is still free", 13,
               "#000", True),
           txt(pn.ox, pn.oy - s * pn.sc - 26,
               "the container at s0, the hypothesis squares and their certified cores, and the "
               "set of centres where one more square can still go", 9, "#555")]
    reg = node["region"]
    # --- the region, as horizontal runs (a compact, exact rendering of the grid)
    for (x0, x1, y0, y1) in reg.runs(reg.undecided):
        out.append(pn.rect(x0, x1, y0, y1, GREENP, "none", 0.30, 0.0))
    for (x0, x1, y0, y1) in reg.runs(reg.green):
        out.append(pn.rect(x0, x1, y0, y1, "#66bb6a", "none", 0.42, 0.0))
    out += pn.container(s)
    for (x0, y0) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):    # the four corner cells
        out.append(pn.rect(x0, x0 + 1, y0, y0 + 1, "none", "#bbb", 0.0, 0.9, "4,3"))

    # --- pockets narrower than 1, hatched
    for p in node["pockets"]:
        if p["gap"] >= 1.0:
            continue
        a, b = p["seg"][0], p["seg"][1]
        band = p.get("band")
        if band:
            out.append(pn.poly(band, "url(#hatch)", "#757575", 0.85, 0.8, "3,2"))
        out.append(pn.line(a[0], a[1], b[0], b[1], "#424242", 1.6, "3,2"))
        mx, my = 0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1])
        out.append(pn.text(mx, my, f"{p['to']} {p['gap']:.3f}", 7.2, "#424242", True, "middle",
                           -3))

    # --- the hypothesis squares
    for i, k in enumerate(node["kinds"]):
        P = node["obstacles"][i]
        nm = node["onames"][i]
        if k["kind"] == "pin":
            cx, cy = k["c"]
            out.append(pn.poly(G.sqpoly(cx, cy, 0.0), PINF, "#0288d1", 0.55, 1.2))
            out.append(pn.poly(P, "none", PINS_, 0.0, 1.1))
            out.append(pn.text(cx, cy, nm, 8.5, "#01579b", True, "middle", 3))
        else:
            b = k["box"]
            out.append(pn.rect(b.x0, b.x1, b.y0, b.y1, "none", "#000", 0.0, 1.1, "5,3"))
            cl = node["clip"].get(nm)
            if cl:
                out.append(pn.rect(cl[0], cl[1], cl[2], cl[3], "none", "#e65100", 0.0, 1.5,
                                   "4,2"))
            cx = 0.5 * (b.x0 + b.x1) if not cl else 0.5 * (cl[0] + cl[1])
            cy = 0.5 * (b.y0 + b.y1) if not cl else 0.5 * (cl[2] + cl[3])
            thm = math.radians(0.5 * (b.th0 + b.th1))
            out.append(pn.poly(G.sqpoly(cx, cy, thm), CY, "#006064", 0.30, 2.2))
            out.append(pn.poly(P, PURPLE, PURPLE_D, 0.55, 1.4))
            out.append(pn.text(cx, cy, nm, 11, "#000", True, "middle", 4))
            out.append(pn.text(cx, cy, f"{0.5 * (b.th0 + b.th1):.2f}°", 7.2, "#004d40", False,
                               "middle", 15))
            mid = np.array(P).mean(0)
            out.append(pn.text(mid[0], mid[1], "K'", 8.0, "#311b92", True, "middle", -2))

    # --- guard lines: the tightest few, thin; the binding ones labelled at the margin
    ylab = pn.oy - s * pn.sc + 10
    nbind = 0
    for r in node["guard"][:4]:
        bind = r["rhs"] <= 0.15
        col = "#d50000" if bind else "#8d6e63"
        if r["orient"] == "h":
            out.append(pn.line(0, r["off"], s, r["off"], col, 1.6 if bind else 0.8,
                               "" if bind else "6,4"))
        else:
            out.append(pn.line(r["off"], 0, r["off"], s, col, 1.6 if bind else 0.8,
                               "" if bind else "6,4"))
        if bind:
            nbind += 1
            out.append(txt(pn.ox + 4, ylab, f"guard {r['orient']}={r['off']:.4f} ({r['tag']}): "
                                            f"chord sum {r['chord_sum']:.4f}, rhs {r['rhs']:.4f}",
                            7.4, "#d50000", True))
            ylab += 10
    if not nbind and node["guard"]:
        r = node["guard"][0]
        out.append(txt(pn.ox + 4, ylab, f"tightest guard line {r['orient']}={r['off']:.4f} "
                                        f"({r['tag']}): chord sum {r['chord_sum']:.4f}, rhs "
                                        f"{r['rhs']:.4f} — nothing within 0.15 of s0", 7.4,
                       "#8d6e63"))

    # --- corner / slot lane tags
    for tag in node["lane_tags"]:
        x, y = tag["centre"]
        col = ("#b71c1c" if tag["verdict"].startswith("KILL") else
               ("#e65100" if "NEAR-MISS" in tag["verdict"] or "LANE<=1" in tag["verdict"]
                else "#455a64"))
        out.append(pn.rect(x - 0.5, x + 0.5, y - 0.5, y + 0.5, "none", col, 0.0, 1.2, "5,3"))
        out.append(pn.text(x, y, tag["cell"], 7.6, col, True, "middle", -4))
        out.append(pn.text(x, y, tag["verdict"], 7.0, col, False, "middle", 6))

    y = pn.oy + 15
    e, y = wrap(pn.ox, y, "green = where another square's centre can still be; grey = pockets too "
                          "narrow for any square; tags = how many squares can reach each "
                          "corner/slot", width_px, 9.5, "#1b5e20", True)
    out += e
    y += 3
    reg = node["region"]
    e, y = wrap(pn.ox, y,
                f"FEASIBLE-CENTRE REGION on a {reg.green.shape[0]}x{reg.green.shape[1]} grid of "
                f"pitch {reg.pitch:.5f} (<= 0.02) x {reg.ntilt} tilts; both verdicts carry the "
                f"Lipschitz margin m = {reg.margin:.5f} = pitch*sqrt2/2 + (sqrt2/2)*(dtheta/2), so "
                f"GREEN is a CERTIFIED inner approximation (every point of a green cell admits a "
                f"feasible tilt) and WHITE a CERTIFIED outer one (no point admits any tilt); the "
                f"pale band between is undecided at this resolution. Area: green "
                f"{reg.area_green():.4f}, green+undecided {reg.area_open():.4f}. Sampled "
                f"confirmation, 10^4 each at {node['sample']['green'].get('tilts', 0)} tilts with "
                f"an independent SAT: green hits {node['sample']['green']['hits']}, blocked hits "
                f"{node['sample']['blocked']['hits']}.", width_px, 8.4, "#33691e")
    out += e
    y += 3
    e, y = wrap(pn.ox, y,
                f"DISK BOUND (the shortcut): a unit square contains the disk of radius 1/2 about "
                f"its centre, so the {node['budget']} remaining centres carry disjoint half-unit "
                f"disks inside the container, all with centres in green+undecided. That region "
                f"dilated by 1/2 and clipped to the container has area "
                f"{node['disk']['area_dilated']:.4f}, so at most "
                f"{node['disk']['n_max']} more unit squares fit — "
                + ("**BELOW the budget: the node is dead by geometry alone**"
                   if node["disk"]["n_max"] < node["budget"] else
                   f"the budget is {node['budget']}, so this alone does not kill the node."),
                width_px, 8.4,
                "#b71c1c" if node["disk"]["n_max"] < node["budget"] else "#555",
                bold=bool(node["disk"]["n_max"] < node["budget"]))
    out += e
    y += 3
    cap = []
    for i, k in enumerate(node["kinds"]):
        if k["kind"] == "pin":
            cap.append(f"{node['onames'][i]} exact pin core half-side {k['a_exact']:.9f}"
                       + (" (certified)" if k["certified"] else " (uncertified)"))
        else:
            cap.append(f"{node['onames'][i]}: K' {k['verts']} certified vertices, area "
                       f"{k['area_poly']:.6f}; the axis cores are NOT drawn — stock half-side "
                       f"{k['a_stock']:.6f}"
                       + (f", A135 exact {k['a_exact']:.6f}" if k["a_exact"] else ""))
    e, y = wrap(pn.ox, y, "CORES (captioned, one style on the drawing): " + "; ".join(cap) + ".",
                width_px, 8.4, "#333")
    out += e
    y += 3
    e, y = wrap(pn.ox, y, node["clip_note"], width_px, 8.4, "#e65100")
    out += e
    return out, y


# ================================================================== PANEL S
def panel_support(pn, node, width_px):
    s = S0
    rec = node["record_label"]
    out = [txt(pn.ox, pn.oy - s * pn.sc - 40, "PANEL S — the LP support", 13, "#000", True),
           txt(pn.ox, pn.oy - s * pn.sc - 26, rec[:118], 9, "#555")]
    out += pn.container(s, label=False)
    pk = node["packing"]
    ys = [float(p.get("y", 0.0)) for p in pk]
    ymax = max(ys) if ys else 1.0
    bad, imposs = 0, []
    for k in sorted(range(len(pk)), key=lambda k: float(pk[k].get("y", 0.0))):
        p = pk[k]
        cx, cy, th, w = (float(p["cx"]), float(p["cy"]), float(p["theta"]),
                         float(p.get("y", 0.0)))
        P = G.sqpoly(cx, cy, th)
        if not all(-1e-6 <= x <= s + 1e-6 and -1e-6 <= yy <= s + 1e-6 for x, yy in P):
            bad += 1
            continue
        f = w / ymax if ymax > 0 else 0.0
        out.append(pn.poly(P, wcol(f), wcol(f, True), 0.82, 0.9))
        dep, owner = -9e9, None
        for i, Q in enumerate(node["obstacles"]):
            d = float(polycore.poly_square_depth(Q, [[cx, cy]], [th])[0])
            if d > dep:
                dep, owner = d, node["onames"][i]
        if dep > 0.0:
            imposs.append(dict(col=k, owner=owner, depth=float(dep), y=w,
                               pose=[cx, cy, math.degrees(th) % 90.0]))
            out.append(pn.poly(P, "none", "#d50000", 0.0, 2.0, "6,3"))
            out.append(pn.text(cx, cy, f"x{owner} {dep:.3f}", 6.6, "#d50000", True, "middle", -6))
    for i, k in enumerate(node["kinds"]):
        if k["kind"] == "pin":
            cx, cy = k["c"]
            out.append(pn.poly(G.sqpoly(cx, cy, 0.0), PINF, "#0288d1", 0.45, 1.0))
        else:
            out.append(pn.poly(node["obstacles"][i], PURPLE, PURPLE_D, 0.45, 1.3))
            m = np.array(node["obstacles"][i]).mean(0)
            out.append(pn.text(m[0], m[1], node["onames"][i], 8.5, "#311b92", True, "middle", 3))
    y = pn.oy + 15
    e, y = wrap(pn.ox, y, "what the relaxation puts where; overlaps are the relaxation's slack, "
                          "not a packing", width_px, 9.5, "#5d4037", True)
    out += e
    y += 3
    e, y = wrap(pn.ox, y,
                f"{len(pk)} dual-support placements, fill = dual weight y on one sequential scale "
                f"(pale yellow y->0, dark orange y = {ymax:.2f}); {bad} outside the container, not "
                f"drawn. RED DASHED = {len(imposs)} column(s) whose square overlaps a certified "
                f"core (K'(B) of a conditioned square, or a pin's exact core) — they are "
                f"IMPOSSIBLE under the hypothesis and carry dual weight "
                f"{sum(r['y'] for r in imposs):.4f}. " + node["support_note"],
                width_px, 8.4, "#444")
    out += e
    return out, y, imposs, bad


# ================================================================== PANEL N
def panel_near(pn, node, width_px):
    s2, poses, prov, is_pack = node["s_star"], node["poses"], node["prov"], node["is_packing"]
    out = [txt(pn.ox, pn.oy - S0 * pn.sc - 40, "PANEL N — nearest real packing", 13, "#000", True),
           txt(pn.ox, pn.oy - S0 * pn.sc - 26, prov.split(";")[0][:82], 9, "#555")]
    exc_s = s2 - S0
    if not is_pack:
        out.append(txt(pn.ox, pn.oy - S0 * pn.sc - 12, "raw dual support at s0 — NOT a packing",
                       12, "#d50000", True))
    elif exc_s > 1e-6:
        out.append(txt(pn.ox, pn.oy - S0 * pn.sc - 12,
                       f"s* = {s2:.6f} > s0: NOT realisable at s0", 12, "#d50000", True))
    else:
        out.append(txt(pn.ox, pn.oy - S0 * pn.sc - 12, f"realisable at s0 (s* = {s2:.6f})", 12,
                       "#1b5e20", True))
    out += pn.container(s2, label=False)
    out.append(pn.rect(0, S0, 0, S0, "none", "#d50000" if exc_s > 1e-6 else "#777", 0.0, 1.8,
                       "8,4"))
    out.append(txt(pn.X(S0), pn.Y(S0) - 4, f"s0 {S0:.4f}", 7.5,
                   "#d50000" if exc_s > 1e-6 else "#777", True, "end"))
    polys = [G.sqpoly(*q) for q in poses]
    exc = max([max(-x, x - s2, -y, y - s2) for P in polys for x, y in P] or [0.0])
    mg = min([L.sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2])
              for i in range(len(poses)) for j in range(i + 1, len(poses))] or [0.0])
    names, nf = [], 0
    for (cx, cy, th) in poses:
        nm = L.snap(cx, cy, th, s2, dtol=1e-3, atol=0.05)
        if nm:
            names.append(nm)
        else:
            names.append(f"f{nf}")
            nf += 1
    for i, P in enumerate(polys):
        free = names[i].startswith("f")
        out.append(pn.poly(P, "#ef9a9a" if free else "#90caf9",
                           "#c62828" if free else "#1565c0", 0.6, 1.1))
        out.append(pn.text(poses[i][0], poses[i][1], names[i], 8.0, "#000", True, "middle", 3))
    y = pn.oy + 15
    e, y = wrap(pn.ox, y, "the nearest configuration that is a real packing; the square names "
                          "below come from here", width_px, 9.5, "#1565c0", True)
    out += e
    y += 3
    e, y = wrap(pn.ox, y, f"{len(poses) - nf} slot + {nf} free squares; s* - s0 = {exc_s:+.6f}; "
                          f"min pairwise SAT separation {mg:+.2e}; worst containment excursion "
                          f"{exc:+.2e} against s = {s2:.6f}. {prov}", width_px, 8.4, "#444")
    out += e
    return out, y, names, exc, mg


# ================================================================== the page
FOOTER = [
    "PANEL G is the GEOMETRY of the hypothesis: the container, the hypothesis squares with their "
    "certified cores, and the shaded set of centres where one further unit square can still be "
    "placed at SOME tilt. Nothing in panel G comes from an LP; it is what the case hypothesis "
    "alone forces. This is the panel to read for a shortcut.",
    "PANEL S is the LP RELAXATION's dual support: a fractional measure, one placement per column, "
    "shaded by dual weight. Its squares OVERLAP each other and sometimes the hypothesis — that is "
    "the relaxation's slack, not a packing, and a column drawn red is one the geometry of panel G "
    "already forbids.",
    "PANEL N is a REAL PACKING: the nearest configuration of eleven pairwise interior-disjoint "
    "unit squares to this node's support, minimised over its own side s*. If s* > s0 the "
    "configuration does not fit in the certified container; the square names are the labels used "
    "everywhere else.",
    "CONVENTIONS — BODIES are filled; CERTIFIED CORES are filled purple (K'(B), A132) or outlined "
    "(a pin's exact core, A135); SCHEMATIC regions (centre boxes, the pin-clipped box, lane cells, "
    "guard lines) are THIN DASHED and are never square bodies. One style per object: the stock and "
    "exact AXIS cores are captioned, not drawn. Green/pale-green/white in panel G = certified "
    "free / undecided / certified blocked for a centre.",
]


def build_page(node, outdir):
    W_G = S0 * SC_G
    W_S = S0 * SC_S
    W_N = max(S0, node["s_star"]) * SC_N
    W = MARG + W_G + GAP + W_S + GAP + W_N + MARG
    body = []
    y = 22.0
    e, y = wrap(MARG, y, node["headline"], W - 2 * MARG, 13.5, "#000", True)
    body += e
    y += 4
    e, y = wrap(MARG, y, node["subline"], W - 2 * MARG, 9.5, "#444")
    body += e
    y += 5
    e, y = wrap(MARG, y, "WHAT TO LOOK FOR — " + node["look"], W - 2 * MARG, 10.5, "#1b5e20",
                True)
    body += e
    y += 4
    e, y = wrap(MARG, y, "GEOMETRIC LEAVES ALREADY RUN ON THIS NODE — " + node["leaves"],
                W - 2 * MARG, 9.0, "#4527a0")
    body += e
    if node.get("banner"):
        y += 6
        body.append(txt(MARG, y + 10, node["banner"], 16, "#b71c1c", True))
        y += 20
    ytop = y + 74
    oy = ytop + S0 * SC_G

    pg = Pane(MARG, oy, SC_G)
    ps = Pane(MARG + W_G + GAP, oy, SC_S)
    pnn = Pane(MARG + W_G + GAP + W_S + GAP, oy, SC_N)
    eG, yG = panel_geometry(pg, node, W_G)
    eS, yS, imposs, bad = panel_support(ps, node, W_S)
    eN, yN, names, exc, mg = panel_near(pnn, node, W_N)
    body += eG + eS + eN
    assert exc <= 1e-4, f"{node['id']}: panel N containment violated by {exc:.2e}"

    y = max(yG, yS, yN) + 22
    for ln in FOOTER:
        e, y = wrap(MARG, y, ln, W - 2 * MARG, 8.8, "#555")
        body += e
        y += 4
    e, y = wrap(MARG, y, node["provenance"], W - 2 * MARG, 8.5, "#777")
    body += e
    H = int(y + 22)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">', DEFS]
           + body + ["</svg>"])
    p = os.path.join(outdir, f"{node['id']}.svg")
    open(p, "w", encoding="utf-8").write("\n".join(doc))
    xml.dom.minidom.parse(p)
    return p, int(W), H, imposs, bad, names, exc, mg


# ================================================================== assembly
def assemble(rec):
    """rec comes from data148; returns the fully-computed node dict the drawing needs."""
    boxes = rec["boxes"]
    obst, onames, kinds, bxs = G.obstacles_of(boxes, rec.get("is_pin"))
    node = dict(rec)
    node.update(obstacles=obst, onames=onames, kinds=kinds)
    t0 = time.time()
    reg = G.feasible_region(S0, obst)
    node["region"] = reg
    node["disk"] = G.disk_bound(reg)
    node["sample"] = G.sample_confirm_region(reg, obst, n=10000)
    node["region_s"] = round(time.time() - t0, 1)
    pks = G.pockets(obst, onames, S0)
    for p in pks:
        if p["gap"] < 1.0 and p["kind"] == "core-core":
            i = onames.index(p["to"].split("-")[0])
            j = onames.index(p["to"].split("-")[1])
            p["band"] = G.pocket_band(obst[i], obst[j], p["seg"][0], p["seg"][1])
        elif p["gap"] < 1.0:
            a, b = p["seg"]
            k = onames.index(p["to"].split("->")[0])
            P = obst[k]
            if abs(a[0] - b[0]) < 1e-12:                       # vertical wall gap
                lo = min(v[0] for v in P)
                hi = max(v[0] for v in P)
                p["band"] = [(lo, min(a[1], b[1])), (hi, min(a[1], b[1])),
                             (hi, max(a[1], b[1])), (lo, max(a[1], b[1]))]
            else:
                lo = min(v[1] for v in P)
                hi = max(v[1] for v in P)
                p["band"] = [(min(a[0], b[0]), lo), (max(a[0], b[0]), lo),
                             (max(a[0], b[0]), hi), (min(a[0], b[0]), hi)]
    node["pockets"] = pks
    pcv = None
    for k in kinds:
        if k["kind"] == "H":
            pcv = k["pc"].verts
    top, allg = G.guard_lines(boxes, pcv)
    node["guard"] = top
    node["guard_all"] = allg
    return node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", dest="which", default="k0v4")
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=999)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    outdir = os.path.join(ROOT, "docs", "shadows", a.which)
    os.makedirs(outdir, exist_ok=True)
    recs = D.population(a.which)
    if a.only:
        recs = [r for r in recs if r["id"] in a.only.split(",")]
    recs = recs[a.lo:a.hi]
    rows, summ = [], []
    for i, rec in enumerate(recs):
        t0 = time.time()
        node = assemble(rec)
        D.finish(node)
        p, W, H, imposs, bad, names, exc, mg = build_page(node, outdir)
        rows.append(D.csv_row(node, imposs, names, exc, mg))
        summ.append(D.summary(node, imposs, bad, names, exc, mg, W, H))
        print(f"[{i + 1:3d}/{len(recs)}] {node['id']:32s} {W}x{H}  green "
              f"{node['region'].area_green():.3f} n_max {node['disk']['n_max']}/"
              f"{node['budget']}  pocket {node['pockets'][0]['gap']:.3f}  imposs {len(imposs)}  "
              f"{time.time() - t0:.1f}s", flush=True)
    with open(os.path.join(outdir, f"review_{a.which}.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump(summ, open(os.path.join(BASE, "results", f"gallery148_{a.which}.json"), "w",
                         encoding="utf-8"), indent=1)
    print("wrote", outdir, "and results/gallery148_%s.json" % a.which)


if __name__ == "__main__":
    main()
