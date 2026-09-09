"""A164 -- the U figure, in A148's panel style.

  PANEL U   the container at s0 with the CERTIFIED-UNCOVERABLE set shaded red: every point of a
            shaded cell is a point NO admissible square can contain, so the shading is an INNER
            approximation of U and the printed area is a LOWER bound.  Obstacles (K'(H), exact pin
            cores) filled cyan/blue, the hypothesis boxes' swept cover pale cyan, the region
            partition (four unit corner boxes, four wall strips, the interior) dashed grey with
            the per-region |U| printed, a handful of SAMPLED ADMISSIBLE POSES thin black (drawn ->
            tested -> hits: none of them may touch a red cell).
  PANEL Z   a zoom of the band that carries the wastage, at the same pitch.

Writes only under this attempt.
"""
import math
import os
import xml.dom.minidom

import numpy as np

import geo164 as G


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


DEFS = ('<defs>'
        '<pattern id="uhatch" width="5" height="5" patternTransform="rotate(45)" '
        'patternUnits="userSpaceOnUse">'
        '<line x1="0" y1="0" x2="0" y2="5" stroke="#d32f2f" stroke-width="2.4"/></pattern>'
        '</defs>')


class Pane:
    def __init__(self, ox, oy, sc, s, xlo=0.0, ylo=0.0):
        self.ox, self.oy, self.sc, self.s = ox, oy, sc, s
        self.xlo, self.ylo = xlo, ylo

    def X(self, x):
        return self.ox + (x - self.xlo) * self.sc

    def Y(self, y):
        return self.oy + (self.s - (y - self.ylo)) * self.sc


def wrap(x, y, text, width, size, col="#333"):
    words, line, out = str(text).split(), "", []
    per = max(10, int(width / (size * 0.52)))
    for w in words:
        if len(line) + len(w) + 1 > per:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    el = []
    for ln in out:
        el.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}">'
                  f'{esc(ln)}</text>')
        y += size * 1.32
    return el, y


def _poly(pn, P, fill, stroke, sw=1.0, op=1.0, dash=None):
    pts = " ".join(f"{pn.X(x):.2f},{pn.Y(y):.2f}" for x, y in P)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def _sq(pn, cx, cy, th, half, fill, stroke, sw=0.9, op=0.0):
    c, s = math.cos(th), math.sin(th)
    P = [(cx + half * (dx * c - dy * s), cy + half * (dx * s + dy * c))
         for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return _poly(pn, P, fill, stroke, sw, op)


def _panel(pn, res, Um, xs, ys, obstacles, names, kinds, boxes, poses, title, width_px,
           span, region_text=True):
    s = res["s"]
    p = res["pitch"]
    el = [f'<text x="{pn.ox:.1f}" y="{pn.oy - 8:.1f}" font-size="12.5" font-weight="600" '
          f'fill="#222">{esc(title)}</text>']
    el.append(f'<rect x="{pn.X(pn.xlo):.2f}" y="{pn.Y(pn.ylo + span[1]):.2f}" '
              f'width="{span[0] * pn.sc:.2f}" height="{span[1] * pn.sc:.2f}" fill="#fff" '
              f'stroke="#111" stroke-width="1.6"/>')
    # the certified-uncoverable cells, as horizontal runs
    for (x0, x1, y0, y1) in G.runs_of(Um, xs, ys, p):
        el.append(f'<rect x="{pn.X(x0):.2f}" y="{pn.Y(y1):.2f}" '
                  f'width="{(x1 - x0) * pn.sc:.2f}" height="{(y1 - y0) * pn.sc:.2f}" '
                  f'fill="url(#uhatch)" stroke="none"/>')
    # the hypothesis boxes: the centre box dashed, the mid-tilt square, the certified core filled
    for i, b in enumerate(boxes):
        cx, cy = 0.5 * (float(b.x0) + float(b.x1)), 0.5 * (float(b.y0) + float(b.y1))
        el.append(f'<rect x="{pn.X(float(b.x0)):.2f}" y="{pn.Y(float(b.y1)):.2f}" '
                  f'width="{(float(b.x1) - float(b.x0)) * pn.sc:.2f}" '
                  f'height="{(float(b.y1) - float(b.y0)) * pn.sc:.2f}" fill="none" '
                  f'stroke="#111" stroke-width="1.0" stroke-dasharray="3 2"/>')
        th = math.radians(0.5 * (float(b.th0) + float(b.th1)))
        el.append(_sq(pn, cx, cy, th, 0.5, "#4dd0e1", "#00838f", 1.1, 0.16))
    for P, nm, k in zip(obstacles, names, kinds):
        col = "#0277bd" if k["kind"] == "pin" else "#00838f"
        el.append(_poly(pn, P, "#4dd0e1", col, 1.3, 0.55))
        xc = sum(v[0] for v in P) / len(P)
        yc = sum(v[1] for v in P) / len(P)
        el.append(f'<text x="{pn.X(xc):.1f}" y="{pn.Y(yc):.1f}" font-size="9" '
                  f'fill="#004d40" text-anchor="middle">{esc(nm)}</text>')
    # sampled admissible poses (drawn -> tested -> hits)
    for (cx, cy, th) in poses:
        el.append(_sq(pn, cx, cy, th, 0.5, "none", "#333", 0.6))
    # the region partition
    if region_text:
        for v in (1.0, s - 1.0):
            el.append(f'<line x1="{pn.X(v):.2f}" y1="{pn.Y(0):.2f}" x2="{pn.X(v):.2f}" '
                      f'y2="{pn.Y(s):.2f}" stroke="#bbb" stroke-width="0.7" '
                      f'stroke-dasharray="2 3"/>')
            el.append(f'<line x1="{pn.X(0):.2f}" y1="{pn.Y(v):.2f}" x2="{pn.X(s):.2f}" '
                      f'y2="{pn.Y(v):.2f}" stroke="#bbb" stroke-width="0.7" '
                      f'stroke-dasharray="2 3"/>')
        mid = {"corner_BL": (0.5, 0.5), "corner_BR": (s - 0.5, 0.5), "corner_TR": (s - .5, s - .5),
               "corner_TL": (0.5, s - 0.5), "strip_S": (s / 2, 0.5), "strip_E": (s - 0.5, s / 2),
               "strip_N": (s / 2, s - 0.5), "strip_W": (0.5, s / 2), "interior": (s / 2, s / 2)}
        for nm, (mx, my) in mid.items():
            a = res["by_region"][nm]["area_U"]
            el.append(f'<text x="{pn.X(mx):.1f}" y="{pn.Y(my) + 3:.1f}" font-size="8.5" '
                      f'fill="{"#c62828" if a > 1e-9 else "#999"}" text-anchor="middle">'
                      f'{esc(nm.replace("corner_", "").replace("strip_", ""))} '
                      f'|U| {a:.4f}</text>')
    return el


def page(node, res, Um, xs, ys, obstacles, names, kinds, boxes, out):
    s = res["s"]
    p = res["pitch"]
    rng = np.random.default_rng(164)
    poses = []
    tries = 0
    while len(poses) < 8 and tries < 20000:
        tries += 1
        th = rng.uniform(0.0, math.pi / 2.0)
        w = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
        cx = rng.uniform(w, s - w)
        cy = rng.uniform(w, s - w)
        ok = True
        for P in obstacles:
            import polycore
            if polycore.poly_square_depth(P, np.array([[cx, cy]]), np.array([th]))[0] > 0.0:
                ok = False
                break
        if ok:
            poses.append((cx, cy, th))

    MARG, GAP = 26.0, 34.0
    SC = 250.0
    W_U = s * SC
    # the zoom: a square window of side `zs` hugging the wall that carries the most wastage
    jj, ii = np.nonzero(Um)
    zs = 1.6
    if len(ii):
        cxU, cyU = float(xs[ii].mean()), float(ys[jj].mean())
    else:
        cxU, cyU = s - 0.5, 0.5 * s
    zx0 = min(max(cxU - 0.5 * zs, 0.0), s - zs)
    zy0 = min(max(cyU - 0.5 * zs, 0.0), s - zs)
    SCz = W_U / zs
    W_Z = zs * SCz
    W = MARG + W_U + GAP + W_Z + MARG
    head = []
    y = MARG + 14
    head.append(f'<text x="{MARG}" y="{y}" font-size="16" font-weight="700" fill="#111">'
                f'{esc(node["id"])} — UNCOVERABLE AREA |U| = {res["area_U"]:.5f} '
                f'({100 * res["ratio_B0"]:.2f}% of the wastage budget B0 = '
                f'{G.B0:.6f})</text>')
    y += 20
    e, y = wrap(MARG, y,
                f"U = the set of points of [0, s0]^2 that NO admissible square can contain "
                f"(admissible for a FREE square = inside the container and interior-disjoint from "
                f"every pin's exact core (A135) and from K'(H) of every conditioned square "
                f"(A132); a conditioned square's or a pin's own cover is the union of its poses "
                f"over its box).  Any 11-packing consistent with the node covers exactly 11, so "
                f"|U| <= m^2 - 11; |U| > m^2 - 11 kills the node with no LP.  Charged against "
                f"B0 = s0^2 - 11 = {G.B0:.12f}, the largest budget on the window slab "
                f"[{G.M_WINDOW_LO}, s0].  RASTER pitch {p:.5f} x {res['ntilt']} tilt bins, cover "
                f"square side lam = {res['lam']:.6f}; a cell is shaded only when NO admissible "
                f"pose MEETS the CLOSED cell (Lipschitz margins m1 = {res['free']['m1']:.5f} on "
                f"the clearance, half-width {res['free']['half_width']:.5f} on the cover), so the "
                f"shading is an INNER approximation of U and {res['area_U']:.5f} is a LOWER "
                f"bound.  Cross-check: {res['sample']['free']['drawn']} random poses drawn, "
                f"{res['sample']['free']['admissible']} certified admissible by an independent "
                f"SAT pass, {res['sample']['free']['hits']} of them contain a shaded cell centre "
                f"(a single hit would refute the raster).",
                W - 2 * MARG, 9.6, "#444")
    y += 6
    oy = y + 22
    pu = Pane(MARG, oy, SC, s)
    pz = Pane(MARG + W_U + GAP, oy, SCz, zs, zx0, zy0)
    body = _panel(pu, res, Um, xs, ys, obstacles, names, kinds, boxes, poses,
                  f"U on the container at s0 = {s:.6f}  (red hatch = certified uncoverable)",
                  W_U, (s, s))
    # the zoom window, same raster, same conventions
    body += [f'<text x="{pz.ox:.1f}" y="{pz.oy - 8:.1f}" font-size="12.5" font-weight="600" '
             f'fill="#222">ZOOM x in [{zx0:.3f}, {zx0 + zs:.3f}], y in [{zy0:.3f}, '
             f'{zy0 + zs:.3f}] — the band that carries the wastage</text>']
    body.append(f'<rect x="{pz.X(zx0):.2f}" y="{pz.Y(zy0 + zs):.2f}" width="{zs * SCz:.2f}" '
                f'height="{zs * SCz:.2f}" fill="#fff" stroke="#111" stroke-width="1.4"/>')
    body.append(f'<clipPath id="zc"><rect x="{pz.X(zx0):.2f}" y="{pz.Y(zy0 + zs):.2f}" '
                f'width="{zs * SCz:.2f}" height="{zs * SCz:.2f}"/></clipPath>')
    zbody = []
    sel = (xs >= zx0 - p) & (xs <= zx0 + zs + p)
    Uz, xz = Um[:, sel], xs[sel]
    for (x0, x1, y0, y1) in G.runs_of(Uz, xz, ys, p):
        if y1 < zy0 - p or y0 > zy0 + zs + p:
            continue
        zbody.append(f'<rect x="{pz.X(x0):.2f}" y="{pz.Y(y1):.2f}" '
                     f'width="{(x1 - x0) * SCz:.2f}" height="{(y1 - y0) * SCz:.2f}" '
                     f'fill="url(#uhatch)" stroke="none"/>')
    for P in obstacles:
        zbody.append(_poly(pz, P, "#4dd0e1", "#00838f", 1.3, 0.55))
    for (cx, cy, th) in poses:
        zbody.append(_sq(pz, cx, cy, th, 0.5, "none", "#333", 0.7))
    for v in (1.0, s - 1.0):
        zbody.append(f'<line x1="{pz.X(v):.2f}" y1="{pz.Y(zy0):.2f}" x2="{pz.X(v):.2f}" '
                     f'y2="{pz.Y(zy0 + zs):.2f}" stroke="#bbb" stroke-width="0.9" '
                     f'stroke-dasharray="3 3"/>')
        zbody.append(f'<line x1="{pz.X(zx0):.2f}" y1="{pz.Y(v):.2f}" '
                     f'x2="{pz.X(zx0 + zs):.2f}" y2="{pz.Y(v):.2f}" stroke="#bbb" '
                     f'stroke-width="0.9" stroke-dasharray="3 3"/>')
    body.append('<g clip-path="url(#zc)">' + "".join(zbody) + '</g>')
    body.append(f'<rect x="{pz.X(zx0):.2f}" y="{pz.Y(zy0 + zs):.2f}" width="{zs * SCz:.2f}" '
                f'height="{zs * SCz:.2f}" fill="none" stroke="#111" stroke-width="1.4"/>')
    body.append(f'<rect x="{pu.X(zx0):.2f}" y="{pu.Y(zy0 + zs):.2f}" width="{zs * SC:.2f}" '
                f'height="{zs * SC:.2f}" fill="none" stroke="#d32f2f" stroke-width="1.2" '
                f'stroke-dasharray="4 3"/>')

    y2 = oy + s * SC + 26
    lines = []
    lines.append("REGIONS (disjoint partition; |U| is a set area, so the parts add): "
                 + ", ".join(f"{nm} {res['by_region'][nm]['area_U']:.5f}"
                             for nm in G.REGIONS))
    lines.append("NAMED BANDS (overlapping, for the reading): "
                 + ", ".join(f"{nm} {v['area_U']:.5f} of {v['area_region']:.3f}"
                             for nm, v in res["bands"].items()))
    om = res.get("one_meeter", {})
    lines.append("HOW MANY FREE CENTRES CAN REACH EACH BAND (the PI's 'only one square'; an "
                 "upper bound from the outer admissible-centre mask, min of the disk bound and a "
                 "0.7-cell cover): "
                 + ", ".join(f"{nm} <= {v['n_free_max']} free + {v['n_boxes']} box"
                             for nm, v in om.items()))
    cr = res.get("crowd", {})
    if cr and not cr.get("applicable", True):
        lines.append("CONDITIONAL (K0-FREE'): " + str(cr.get("note", "")))
    elif cr:
        lines.append(f"CONDITIONAL (K0-FREE': every corner box met by >= {cr['n_per_corner']} "
                     f"squares, so {4 * cr['n_per_corner']} squares are corner-committed and only "
                     f"{cr['n_loose']} are loose): the part of the container outside every "
                     f"corner-committed square's reach and outside the hypothesis boxes' cover "
                     f"has area {cr['area_B']:.5f}; the leaf needs it above "
                     f"{cr['n_loose']} + B0 = {cr['n_loose'] + G.B0:.4f} — "
                     + ("KILL" if cr["kill"] else "no kill"))
    lines.append(f"VERDICT: |U| = {res['area_U']:.5f} vs B0 = {G.B0:.6f} — "
                 + ("DEAD by wastage" if res["area_U"] > G.B0 else
                    f"ALIVE ({100 * res['ratio_B0']:.2f}% of the budget; the leaf needs 100%)"))
    for ln in lines:
        e, y2 = wrap(MARG, y2, ln, W - 2 * MARG, 9.4, "#444")
        body += e
        y2 += 4
    e, y2 = wrap(MARG, y2,
                 f"Provenance: A164 geo164.py/fig164.py; record {node.get('record')}; obstacles "
                 f"A132 polycore + A135 exact cores via A148 geo148.obstacles_of; pitch "
                 f"{p:.5f}, {res['ntilt']} tilt bins, {res['free']['n_centre_nodes']} centre "
                 f"nodes evaluated. READ-ONLY on every campaign.",
                 W - 2 * MARG, 8.6, "#777")
    body += e
    H = int(max(y2, oy + s * SC) + 20)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">', DEFS]
           + head + body + ["</svg>"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(doc))
    xml.dom.minidom.parse(out)
    return out
