"""A144 -- the Y0147 page with the guard line drawn and the four chords labelled (A142's format).

PANEL 1  the node at s0 in A142's visual language: BODIES filled, CORES solid outlines with no
         fill, SCHEMATIC objects thin dashed with no fill.  Grey P0..P4 = the pins at their box
         centres with A135's exact core; bright cyan H = the conditioned square at the box centre
         and the mid tilt, faint cyan at the two extremal tilts, filled purple = A132's certified
         polygon core K'(B); the LP dual support filled by dual weight.  Over it, the GUARD LINE
         (heavy red dashed, drawn right across the container) and, ON the line, the FOUR CHORDS as
         thick coloured segments, each labelled with its exact length and its owner.

PANEL 2  the chord ledger: the same four chords at their TRUE positions along the line, so the two
         overlaps -- the impossibility -- are visible, and the cumulative bar SUM |l n Q| = 4.0055
         against the container width s0 = 3.877084 with the excess hatched.

Read-only on every campaign; writes only this attempt's figs/ and results/.

    set PYTHONDONTWRITEBYTECODE=1 && python code/draw144.py --node k5_11_interior_Y0147
"""
import argparse
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for _p in (os.path.join(A132, "code"), os.path.join(A135, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import guardline as G                                                   # noqa: E402
import offline144 as OFF                                                # noqa: E402
import polycore                                                         # noqa: E402
import exactcore                                                        # noqa: E402

SC = 112                    # px per unit -- A142's scale
S0 = G.S0
FIGS = os.path.join(BASE, "figs")
HYP_FILL = "#00e5ff"
CH_COL = ["#1b5e20", "#6a1b9a", "#e65100", "#0d47a1", "#880e4f", "#004d40"]


# ------------------------------------------------------------------ primitives (A142's)
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


def _overlaps(chords):
    """pairs of chords that overlap along the line -- the visible impossibility."""
    out = []
    for i in range(len(chords)):
        for j in range(i + 1, len(chords)):
            a, b = chords[i]["iv"], chords[j]["iv"]
            if not a or not b:
                continue
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if hi - lo > 1e-9:
                out.append((lo, hi, f"{chords[i]['owner'].split(' (')[0]} / "
                                    f"{chords[j]['owner'].split(' (')[0]}"))
    return out


# ------------------------------------------------------------------ the page
def build(nid, line_tag="PI: 0.99 below the top"):
    got = OFF.load_node(nid)
    if got is None:
        raise KeyError(nid)
    d, recpath = got
    pins, hbox = G.node_boxes(d)
    s = float(d.get("s") or S0)
    pc = polycore.build(hbox, max_v=40)
    a_ex, a_st, _ok = exactcore.exact_a(hbox)
    fam, rows, _ = OFF.measure(d, want_pi=True, max_lines=40)
    row = next((r for r in rows if r["line"]["tag"] == line_tag), rows[0])
    ln = G.Line(row["line"]["orient"], Fr(row["line"]["off"]), row["line"]["tag"])
    gr = G.guard_row(pins, hbox, ln, pc_verts=pc.verts)

    # ---- the chords that actually appear on this line: pins, H, and the support columns
    chords = []
    hmid = ((hbox.x0 + hbox.x1) / 2, (hbox.y0 + hbox.y1) / 2,
            math.radians((hbox.th0 + hbox.th1) / 2))
    for j, (p, lo) in enumerate(zip(pins, gr["pins_float"])):
        if lo <= 1e-9:
            continue
        cx, cy = (p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2
        iv = G.chord_interval(0.5, cx, cy, 0.0, ln)
        chords.append(dict(owner=f"pin P{j}", kind="pin", lo_exact=str(gr["pins"][j]),
                           length=lo, iv=iv, cx=cx, cy=cy, th=0.0,
                           note="exactly 1: the line runs through the pin core's height range"))
    if gr["h_float"] > 1e-9:
        iv = G.chord_interval(0.5, hmid[0], hmid[1], hmid[2], ln)
        chords.append(dict(owner="H (conditioned)", kind="H", lo_exact=str(gr["h"]),
                           length=gr["h_float"], iv=iv, cx=hmid[0], cy=hmid[1], th=hmid[2],
                           note=f"minchord over the box B; the cheap bound |l n K'(B)| is "
                                f"{gr['kprime_float']:.6f}"))
    for c in row["cols"]:
        th = math.radians(c["theta_deg"])
        iv = G.chord_interval(0.5, c["cx"], c["cy"], th, ln)
        chords.append(dict(owner=f"LP column ({c['cx']:.4f},{c['cy']:.4f}) "
                                 f"{c['theta_deg']:.2f}deg y={c['y']:.3f}", kind="col",
                           length=c["chord"], lo_exact=None, iv=iv,
                           cx=c["cx"], cy=c["cy"], th=th, y=c["y"],
                           note=("through OPPOSITE sides: 1/cos(tilt from the axis)"
                                 if c["chord"] >= 1 - 1e-12 else "through adjacent sides")))
    chords.sort(key=lambda c: (c["iv"][0] if c["iv"] else 9e9))
    tot = sum(c["length"] for c in chords)

    # =============================================================== panel 1
    W1 = int(s * SC) + 120
    W2 = int(s * SC) + 300
    ox = 34
    body = []
    body.append(text(24, 28, f"{nid} — the guard line and its four chords "
                             f"(A144; A142 format)", 15, "#111", True))
    e, ytop = wrap(24, 48, f"record {recpath}; budget {d.get('budget')}, tau "
                           f"{float(d.get('tau') or 0):.9f}; s0 = {s:.6f}. The line is "
                           f"{ln.orient} = {ln.foff:.6f} ({ln.tag}); the family line "
                           f"'grid h 6/8' at 2.907813 gives the identical four chords.",
                   W1 + W2, 9.5, "#444", lead=12.0)
    body += e
    oy = int(ytop) + 34 + int(s * SC)
    body.append(text(ox, oy - s * SC - 14, "PANEL 1 — the node at s0 with the guard line drawn "
                                           "across it", 12, "#111", True))
    body += frame(ox, oy, SC, s)
    # pins with A135's exact cores
    for j, p in enumerate(pins):
        cx, cy = (p.x0 + p.x1) / 2, (p.y0 + p.y1) / 2
        body.append(poly(ox, oy, SC, sq(cx, cy, 0.0), "#9e9e9e", "#424242", 0.28, 1.4))
        body.append(poly(ox, oy, SC, sq(cx, cy, 0.0, float(G.HALF - G.DELTA / G.SQRT2_LO)),
                         "none", "#0d47a1", 0.0, 1.0))
        body.append(text(ox + cx * SC, oy - cy * SC + 4, f"P{j}", 11, "#212121", True, "middle"))
    # the conditioned square: mid tilt solid, the two extremal tilts faint, K' filled
    for th, op, wdt in ((hbox.th0, 0.10, 1.0), (hbox.th1, 0.10, 1.0),
                        ((hbox.th0 + hbox.th1) / 2, 0.30, 1.8)):
        body.append(poly(ox, oy, SC, sq(hmid[0], hmid[1], math.radians(th)),
                         HYP_FILL, "#006064", op, wdt))
    body.append(poly(ox, oy, SC, [(float(a), float(b)) for a, b in pc.verts],
                     "#7e57c2", "#4527a0", 0.45, 1.2))
    body.append(rect(ox, oy, SC, hbox.x0, hbox.x1, hbox.y0, hbox.y1, "none", "#000", 0.0, 1.0,
                     "5,3"))
    body.append(text(ox + hmid[0] * SC, oy - hmid[1] * SC + 4, "H", 12, "#004d40", True,
                     "middle"))
    # the LP dual support
    for p in (d.get("packing") or []):
        y = float(p.get("y", 0.0))
        body.append(poly(ox, oy, SC, sq(float(p["cx"]), float(p["cy"]), float(p["theta"])),
                         wcol(y), wcol(y, True), 0.55, 1.3))
    # the guard line, right across
    if ln.orient == "h":
        yy = oy - ln.foff * SC
        body.append(f'<line x1="{ox - 12:.1f}" y1="{yy:.1f}" x2="{ox + s * SC + 12:.1f}" '
                    f'y2="{yy:.1f}" stroke="#d50000" stroke-width="2.6" '
                    f'stroke-dasharray="9,5"/>')
        body.append(text(ox + s * SC + 16, yy + 4, f"l : y = {ln.foff:.6f}", 10, "#d50000", True))
    else:
        xx = ox + ln.foff * SC
        body.append(f'<line x1="{xx:.1f}" y1="{oy + 12:.1f}" x2="{xx:.1f}" '
                    f'y2="{oy - s * SC - 12:.1f}" stroke="#d50000" stroke-width="2.6" '
                    f'stroke-dasharray="9,5"/>')
    # the chords ON the line, thick and labelled
    for k, c in enumerate(chords):
        if not c["iv"]:
            continue
        col = CH_COL[k % len(CH_COL)]
        a0, a1 = c["iv"]
        if ln.orient == "h":
            yy = oy - ln.foff * SC + (k - (len(chords) - 1) / 2.0) * 5.0
            body.append(f'<line x1="{ox + a0 * SC:.1f}" y1="{yy:.1f}" '
                        f'x2="{ox + a1 * SC:.1f}" y2="{yy:.1f}" stroke="{col}" '
                        f'stroke-width="4.2" stroke-linecap="butt"/>')
            lab = oy - ln.foff * SC + (-16 - 13 * (k // 2) if k % 2 == 0
                                       else 22 + 13 * (k // 2))
            body.append(f'<line x1="{ox + (a0 + a1) / 2 * SC:.1f}" y1="{yy:.1f}" '
                        f'x2="{ox + (a0 + a1) / 2 * SC:.1f}" y2="{lab + (3 if k % 2 else -3):.1f}"'
                        f' stroke="{col}" stroke-width="0.8" stroke-dasharray="2,2"/>')
            body.append(text(ox + (a0 + a1) / 2 * SC, lab, f"{c['length']:.6f}", 10.5, col,
                             True, "middle"))
        else:
            xx = ox + ln.foff * SC + (k - (len(chords) - 1) / 2.0) * 5.0
            body.append(f'<line x1="{xx:.1f}" y1="{oy - a0 * SC:.1f}" x2="{xx:.1f}" '
                        f'y2="{oy - a1 * SC:.1f}" stroke="{col}" stroke-width="4.2"/>')

    # =============================================================== panel 2
    ox2 = ox + W1 + 20
    top2 = oy - s * SC
    body.append(text(ox2, top2 - 14, "PANEL 2 — the chord ledger: the same four chords at their "
                                     "true positions on l", 12, "#111", True))
    lw = s * SC
    yb = top2 + 30
    body.append(f'<line x1="{ox2:.1f}" y1="{yb - 12:.1f}" x2="{ox2 + lw:.1f}" '
                f'y2="{yb - 12:.1f}" stroke="#000" stroke-width="1.6"/>')
    body.append(text(ox2, yb - 18, "0", 9, "#555"))
    body.append(text(ox2 + lw, yb - 18, f"s0 = {s:.6f}", 9, "#555", anchor="end"))
    yy = yb + 8
    for k, c in enumerate(chords):
        col = CH_COL[k % len(CH_COL)]
        a0, a1 = c["iv"] if c["iv"] else (0.0, 0.0)
        body.append(f'<rect x="{ox2 + a0 * SC:.1f}" y="{yy - 9:.1f}" '
                    f'width="{max(1.0, (a1 - a0) * SC):.1f}" height="18" fill="{col}" '
                    f'fill-opacity="0.30" stroke="{col}" stroke-width="1.4"/>')
        body.append(text(ox2 + (a0 + a1) / 2 * SC, yy + 4, f"{c['length']:.6f}", 10, col, True,
                         "middle"))
        e2, yy = wrap(ox2, yy + 24, f"{c['owner']} — {c['note']}", W2 - 20, 8.5, "#444",
                      lead=11.0)
        body += e2
        yy += 12
    for (lo, hi, who) in _overlaps(chords):
        body.append(text(ox2, yy, f"overlap {who}: {hi - lo:.6f} on [{lo:.4f}, {hi:.4f}] — "
                                  f"two squares of one packing would share it", 9.0, "#d50000",
                         True))
        yy += 13
    ycum = yy + 16
    body.append(text(ox2, ycum - 6, "cumulative: the chords are pairwise interior-disjoint in ANY "
                                    "packing, so they must fit in [0, s0]", 9.5, "#111", True))
    acc = 0.0
    for k, c in enumerate(chords):
        col = CH_COL[k % len(CH_COL)]
        body.append(f'<rect x="{ox2 + acc * SC:.1f}" y="{ycum + 6:.1f}" '
                    f'width="{c["length"] * SC:.1f}" height="22" fill="{col}" '
                    f'fill-opacity="0.55" stroke="#fff" stroke-width="1.0"/>')
        acc += c["length"]
    body.append(f'<rect x="{ox2 + s * SC:.1f}" y="{ycum + 2:.1f}" '
                f'width="{(acc - s) * SC:.1f}" height="30" fill="#d50000" fill-opacity="0.35" '
                f'stroke="#d50000" stroke-width="1.6"/>')
    body.append(f'<line x1="{ox2 + s * SC:.1f}" y1="{ycum - 2:.1f}" x2="{ox2 + s * SC:.1f}" '
                f'y2="{ycum + 38:.1f}" stroke="#000" stroke-width="2.0"/>')
    body.append(text(ox2, ycum + 52, f"SUM = {acc:.6f}   >   s0 = {s:.6f}", 11, "#111", True))
    body.append(text(ox2 + lw + 6, ycum + 24, f"EXCESS {acc - s:+.6f}", 10, "#d50000", True))

    # =============================================================== the text block
    y = max(oy + 34, ycum + 76)
    W = ox2 + W2 + 24

    def add(t, size=9.5, col="#222", bold=False):
        nonlocal y
        e2, y = wrap(24, y, t, W - 48, size, col, bold, lead=size + 3.4)
        body.extend(e2)
        y += 5

    add(f"THE ROW.  For any line l inside [0,s0]^2 the chords l n Q of a packing are pairwise "
        f"interior-disjoint sub-intervals of a segment of length s0, so SUM |l n Q| <= s0.  "
        f"Splitting off the hypothesis squares gives the LP row over the {d.get('budget')} free "
        f"placements: SUM_p |l n Q_p| x_p <= s0 - SUM_pins |l n P| - minchord(H, l) = "
        f"{gr['rhs_float']:.6f}.", 10, "#111", True)
    add(f"THE VIOLATION.  On this line the stored dual support charges "
        f"{row['lhs']:.6f} against a right-hand side of {gr['rhs_float']:.6f}: a violation of "
        f"{row['viol']:+.6f}.  The four chords are "
        + " + ".join(f"{c['length']:.6f} ({c['owner'].split(' ')[0]} "
                     f"{c['owner'].split(' ')[1] if len(c['owner'].split(' ')) > 1 else ''})"
                     .strip() + ")" for c in chords)
        + f" = {acc:.6f}, and the container is only {s:.6f} wide.  That is the PI's reading: "
          f"a line crossing four squares through opposing sides forces side >= 4.")
    add(f"THE TERMS.  minchord(H, l) = {gr['h_float']:.6f} exactly, by the two-endpoint argument "
        f"of guardline.minchord_box (V = {gr['h_V']:.6f}, terms {gr['h_terms']}); the cheap "
        f"alternative |l n K'(B)| = {gr['kprime_float']:.6f} is weaker, so the row uses "
        f"{gr['uses']}.  {gr['n_pins_full']} pin chord(s) are exactly 1 (the line runs through "
        f"the pin core's height range at every position of the pin box); the other "
        f"{len(pins) - gr['n_pins_full']} pins do not meet l.  a_stock = {float(a_st):.6f}, "
        f"a_exact = {float(a_ex):.6f} (A135), K'(B) has {len(pc.verts)} certified vertices, "
        f"area {pc.area():.6f}.")
    add("LEGEND — BODIES are filled; CORES are solid outlines with no fill; SCHEMATIC objects "
        "(the centre box) are thin dashed with no fill. Grey P0..P4 = the pins at their box "
        "centres, thin dark blue = A135's exact pin core; bright cyan H = the conditioned square "
        "at the mid tilt, faint cyan = the two extremal tilts, filled purple = A132's certified "
        "polygon core K'(B), black dashed = the centre box; orange-scale = the LP dual support "
        "by weight. HEAVY RED DASHED = the guard line; the thick coloured segments on it are the "
        "chords, each labelled with its length.", 9.0, "#555")

    H = int(y + 24)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ["</svg>"])
    os.makedirs(FIGS, exist_ok=True)
    p = os.path.join(FIGS, f"{nid}_guardline.svg")
    open(p, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(p)
    summ = dict(node=nid, record=recpath, svg=os.path.relpath(p, BASE),
                line=ln.to_json(), rhs=gr["rhs_float"], rhs_exact=str(gr["rhs"]),
                lhs=row["lhs"], violation=row["viol"], sum_chords=acc, s0=s,
                minchord_H=gr["h_float"], minchord_H_exact=str(gr["h"]),
                kprime_chord=gr["kprime_float"], uses=gr["uses"],
                chords=[dict(owner=c["owner"], length=c["length"], interval=c["iv"],
                             note=c["note"]) for c in chords],
                width=int(W), height=H)
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="k5_11_interior_Y0147")
    ap.add_argument("--line-tag", default="PI: 0.99 below the top")
    a = ap.parse_args()
    s = build(a.node, a.line_tag)
    p = os.path.join(BASE, "results", f"draw144_{a.node}.json")
    json.dump(s, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps(s, indent=1))
    print("wrote", s["svg"], "and", os.path.relpath(p, BASE))


if __name__ == "__main__":
    main()
