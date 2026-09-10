"""A190 -- docs/residue_map/guardline_kills.svg in the drawing rules of docs/residue_map/gen_a57_lp.py: per page
(killed pages first, then the rest of the run) two panels, the LP dual support BEFORE (the stored record) and
AFTER (the guard-line LP), with the pins (light blue), the conditioned box H (black), the guard line(s) that carry
the row (red, the active ones thick) drawn right across, and every support square's chord on the active line
printed as a thick segment with its length; the rhs*, the support's chord sum and tau / budget in the header.
Read-only on every record.    python fig190.py [--max-pages 40]
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
sys.path.insert(0, HERE)
import lines190 as LN                                            # noqa: E402  (A144 guardline chord helpers)
import guardline as G                                            # noqa: E402
from fractions import Fraction as Fr                             # noqa: E402

S0 = float(LN.S_RAT)
S = 120                                                          # px per unit
PW, PH = int(S0 * S) + 40, int(S0 * S) + 70


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'


def panel(ox, oy, title, sub, pins, box, support, lines, active):
    """ox, oy = the panel's top-left; the container drawn with y up."""
    X = lambda x: ox + 20 + x * S                                # noqa: E731
    Y = lambda y: oy + 40 + (S0 - y) * S                         # noqa: E731
    out = [text(ox + 20, oy + 14, title, 11.5, bold=True), text(ox + 20, oy + 30, sub, 9, "#444")]
    out.append(f'<rect x="{X(0):.1f}" y="{Y(S0):.1f}" width="{S0 * S:.1f}" height="{S0 * S:.1f}" fill="none" stroke="#000" stroke-width="1.5"/>')
    for (cx, cy) in pins:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in sq(cx, cy, 0.0))
        out.append(f'<polygon points="{pts}" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.2"/>')
    if box:
        out.append(f'<rect x="{X(box["x0"]):.1f}" y="{Y(box["y1"]):.1f}" width="{(box["x1"] - box["x0"]) * S:.1f}" '
                   f'height="{(box["y1"] - box["y0"]) * S:.1f}" fill="none" stroke="#000" stroke-width="1.6"/>')
        out.append(text(X(box["x1"]) + 3, Y(box["y1"]) + 9, "H %.0f-%.0f deg" % (box["th0"], box["th1"]), 8.5))
    ymax = max([w for (_, _, _, w) in support] or [1.0])
    for (cx, cy, th, w) in support:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in sq(cx, cy, th))
        out.append(f'<polygon points="{pts}" fill="#ef6c00" fill-opacity="{0.15 + 0.5 * w / ymax:.2f}" stroke="#bf360c" stroke-width="0.8"/>')
    for L, z in lines:
        thick = z > 1e-6
        col, sw = ("#c62828", 2.2) if thick else ("#e57373", 0.8)
        if L.orient == "h":
            out.append(f'<line x1="{X(0):.1f}" y1="{Y(L.foff):.1f}" x2="{X(S0):.1f}" y2="{Y(L.foff):.1f}" stroke="{col}" stroke-width="{sw}" stroke-dasharray="{"" if thick else "5,4"}"/>')
        else:
            out.append(f'<line x1="{X(L.foff):.1f}" y1="{Y(0):.1f}" x2="{X(L.foff):.1f}" y2="{Y(S0):.1f}" stroke="{col}" stroke-width="{sw}" stroke-dasharray="{"" if thick else "5,4"}"/>')
    if active is not None:
        L = active
        tot = 0.0
        for (cx, cy, th, w) in support:
            iv = G.chord_interval(0.5, cx, cy, th, L)
            if not iv:
                continue
            c = iv[1] - iv[0]
            tot += c * w
            if L.orient == "h":
                out.append(f'<line x1="{X(iv[0]):.1f}" y1="{Y(L.foff):.1f}" x2="{X(iv[1]):.1f}" y2="{Y(L.foff):.1f}" stroke="#1b5e20" stroke-width="5" stroke-opacity="{0.35 + 0.6 * w / ymax:.2f}"/>')
                out.append(text(X(0.5 * (iv[0] + iv[1])), Y(L.foff) - 6, "%.3f x%.2f" % (c, w), 8, "#1b5e20", anchor="middle"))
            else:
                out.append(f'<line x1="{X(L.foff):.1f}" y1="{Y(iv[0]):.1f}" x2="{X(L.foff):.1f}" y2="{Y(iv[1]):.1f}" stroke="#1b5e20" stroke-width="5" stroke-opacity="{0.35 + 0.6 * w / ymax:.2f}"/>')
                out.append(text(X(L.foff) + 6, Y(0.5 * (iv[0] + iv[1])), "%.3f x%.2f" % (c, w), 8, "#1b5e20"))
        out.append(text(ox + 20, oy + 40 + S0 * S + 14, "weighted chord sum of the support on the active line = %.3f" % tot, 9, "#1b5e20"))
    return out


def page_panels(row, k, x0, y0):
    rec = json.load(open(os.path.join(ROOT, row["record"].replace("\\", os.sep)), encoding="utf-8"))
    pins, hbox = G.node_boxes(rec)
    pin_c = [(0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)) for b in pins]
    box = hbox.to_json()
    before = [(float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0))) for p in (rec.get("packing") or [])]
    lp = os.path.join(RES, "lpres_%s.json" % row["id"])
    after, zs, lines = [], [], []
    if os.path.exists(lp):
        d = json.load(open(lp, encoding="utf-8"))
        after = [(float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0))) for p in (d.get("packing") or [])]
        lines = [G.Line(e["orient"], Fr(e["off"]), e.get("tag", "")) for e in d.get("lines") or []]
        zs = d.get("z") or [0.0] * len(lines)
    pairs = list(zip(lines, zs))
    act = max(pairs, key=lambda p: p[1])[0] if pairs and max(zs) > 1e-6 else (pairs[0][0] if pairs else None)
    rhs = None
    for e in row.get("z") or []:
        if act is not None and e["line"]["orient"] == act.orient and abs(e["line"]["off_float"] - act.foff) < 1e-9:
            rhs = e["rhs"]
    hdr = "%s  [%s, %s]  %s" % (row["id"], row.get("family"), row.get("cls"), row.get("verdict", ""))
    sub_b = "BEFORE: stored record, tau %.4f / budget %s, %d support placements" % (float(row.get("tau_stored") or 0), row.get("budget"), len(before))
    sub_a = "AFTER: guard-line LP, tau %s / budget %s, %d placements; active line %s = %s, rhs* = %s, z = %s" % (
        ("%.4f" % row["tau"]) if row.get("tau") is not None else "-", row.get("budget"), len(after),
        act.orient if act else "-", ("%.4f" % act.foff) if act else "-", ("%.4f" % rhs) if rhs is not None else "-",
        ("%.4f" % max(zs)) if zs else "-")
    out = [text(x0, y0 - 6, "%d. %s" % (k, hdr), 12, bold=True)]
    out += panel(x0, y0, "before", sub_b, pin_c, box, before, pairs, act)
    out += panel(x0 + PW + 20, y0, "after", sub_a, pin_c, box, after, pairs, act)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "residue_map", "guardline_kills.svg"))
    a = ap.parse_args()
    rows = {}
    for ln in open(os.path.join(RES, "run190.jsonl"), encoding="utf-8"):
        if ln.strip():
            r = json.loads(ln)
            if r.get("record"):
                rows[r["id"]] = r
    rows = list(rows.values())
    rows.sort(key=lambda r: (not str(r.get("verdict", "")).startswith("DEAD"), not r.get("kills"), r.get("family") != "S01", r["id"]))
    rows = rows[:a.max_pages]
    n_dead = sum(1 for r in rows if str(r.get("verdict", "")).startswith("DEAD"))
    W = 2 * PW + 60
    H = 90 + len(rows) * (PH + 40)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
           '<rect width="100%" height="100%" fill="#fff"/>',
           text(20, 24, "A190 -- guard-line kills: the LP dual support before / after the chord-sum column (Theorem G, docs/proofs/guardline_clause.md)", 14, bold=True),
           text(20, 42, "%d pages drawn, %d DEAD under verify_case_v5 [C under v5 ONLY]; pins light blue, H black, guard lines red (active thick), "
                        "support squares orange (opacity = dual weight), chords on the active line green with length x weight; s0 = %.6f" % (len(rows), n_dead, S0), 9.5, "#444"),
           text(20, 56, "A kill: the support's weighted chord sum on the active line exceeded rhs* = s0 - (pin chords) - minchord(H) before; after, the column prices the line and tau drops below the budget.", 9.5, "#444")]
    y = 90
    for k, r in enumerate(rows, 1):
        try:
            out += page_panels(r, k, 20, y)
        except Exception as e:                                   # noqa: BLE001
            out.append(text(20, y + 20, "%s: not drawn (%s)" % (r["id"], repr(e)[:80]), 10, "#c00"))
        y += PH + 40
    out.append("</svg>")
    open(a.out, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", a.out, "pages", len(rows), "dead", n_dead)


if __name__ == "__main__":
    main()
