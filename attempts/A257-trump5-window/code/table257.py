"""A257 -- the SEAM PILOT's sibling table and its residue page.

Reads results/pilot257.jsonl (the pilot's journal) and writes
  * results/seam_table257.md                                   -- one row per near-Trump sibling;
  * docs/residue_map/campaigns/A257-trump5-window/seam257.svg  -- one PANEL per sibling, in cut order.

What a panel IS (the note is drawn on the panel itself): the plane of ONE aligned cut.  The dashed square is the
TUBE BOX about the assigned Trump image square -- half-width r_c' = r_c - 2(s0 - s-hat) for a centre cut, half-width
r_theta for a tilt cut (then the horizontal axis is the tilt in degrees and the vertical one is nominal).  The solid
rectangle is the HULL of the cut role's pieces at the parent node.  The vertical line is the cut m, drawn at the
tube WALL.  The shaded half is the NEAR-TRUMP SIBLING -- the node the seam has to kill by the ordinary rules; the
unshaded half holds the image and is where the spine descends.  Green = the sibling died (the rule is printed),
red = it did not die inside the wall (that panel IS the seam gap), grey = not run yet."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.abspath(os.path.join(HERE, ".."))
JOURNAL = os.path.join(ATT, "results", "pilot257.jsonl")
TABLE = os.path.join(ATT, "results", "seam_table257.md")
PAGE = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A257-trump5-window", "seam257.svg")
W, H, COLS, PAD = 300, 250, 4, 26
COL = {"DEAD": "#2e7d32", "ALIVE": "#c62828", "UNDECIDED": "#ef6c00", "NOT REACHED": "#9e9e9e", None: "#9e9e9e"}


def rows():
    out = []
    if os.path.exists(JOURNAL):
        for ln in open(JOURNAL, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
    return out


def collect():
    R = rows()
    spine = [r for r in R if r.get("phase") == "spine"]
    sibs = {r.get("only"): r for r in R if r.get("phase") == "sibling"}
    sp = spine[-1] if spine else None
    return sp, sibs


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def image_square(i):
    sys.path[:0] = [os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"),
                    os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")]
    import trump256 as TR
    q = next(x for x in TR.images()["id"] if x["i"] == i)
    return float(q["cx"]), float(q["cy"]), TR.MB.deg_of_t(q["reps"][0][0]), float(TR.radii("slot")["r_c_eff"]), float(TR.radii("slot")["r_theta"])


def panel(s, v, ox, oy):
    """one aligned cut, in the coordinate the cut was made on."""
    cx, cy, th, rc, rt = image_square(s["square"])
    tilt = s["dim"] == "t"
    c = th if tilt else (cx if s["dim"] == "x" else cy)
    r = (rt * 180.0 / 3.141592653589793) if tilt else rc
    box = s.get("box") or []
    if tilt:
        u0, u1 = (box[4], box[5]) if len(box) >= 6 else (c - 3 * r, c + 3 * r)
    else:
        u0, u1 = (box[0], box[1]) if s["dim"] == "x" else (box[2], box[3])
    m = float(s["m_f"])
    lo, hi = min(u0, c - 2 * r, m), max(u1, c + 2 * r, m)
    span = max(hi - lo, 1e-9) * 1.15
    mid = (lo + hi) / 2.0

    def X(u):
        return ox + 14 + (u - (mid - span / 2)) / span * (W - 28)
    col = COL.get((v or {}).get("verdict"))
    p = ['<g><rect x="%d" y="%d" width="%d" height="%d" fill="#fff" stroke="#bbb"/>' % (ox, oy, W, H)]
    y0, y1 = oy + 56, oy + 150
    sx0, sx1 = (X(m), ox + W - 2) if s["side_with_image"] == "lo" else (ox + 2, X(m))
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s" opacity="0.13"/>' % (sx0, y0 - 8, max(0.0, sx1 - sx0), y1 - y0 + 16, col))
    p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="none" stroke="#1565c0" stroke-dasharray="5 3"/>'
             % (X(c - r), y0, X(c + r) - X(c - r), y1 - y0))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" fill="none" stroke="#222" stroke-width="1.4"/>'
             % (X(u0), y0 + 14.0, max(1.0, X(u1) - X(u0)), y1 - y0 - 28))
    p.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2"/>' % (X(m), y0 - 10, X(m), y1 + 10, col))
    p.append('<circle cx="%.1f" cy="%.1f" r="3" fill="#1565c0"/>' % (X(c), (y0 + y1) / 2.0))
    p.append('<text x="%d" y="%d" font-size="11" font-family="sans-serif" font-weight="bold">cut %s: %s on %s at %s</text>'
             % (ox + 8, oy + 16, s["cut_index"], esc(s["role"]), esc(s["dim"]), esc(s["m_f"])))
    p.append('<text x="%d" y="%d" font-size="10" font-family="sans-serif" fill="#444">image square %s, excess %s x radius; sibling %s</text>'
             % (ox + 8, oy + 30, s["square"], s["excess"], esc(s["sibling"])))
    p.append('<text x="%d" y="%d" font-size="10" font-family="sans-serif" fill="#444">dashed = tube box (+-%s); solid = the role hull at the parent; shaded = the SIBLING half</text>'
             % (ox + 8, oy + 44, ("%.4f deg" % r) if tilt else ("%.5f" % r)))
    if v:
        p.append('<text x="%d" y="%d" font-size="11" font-family="sans-serif" fill="%s" font-weight="bold">%s%s in %s s (%s node(s))</text>'
                 % (ox + 8, oy + 172, col, esc(v.get("verdict")), (" by " + ",".join(v.get("rules") or [])) if v.get("rules") else "",
                    v.get("seconds"), v.get("n_nodes")))
        why = ((v.get("alive_leaves") or [{}])[0].get("reason") or "") if v.get("verdict") != "DEAD" else ((v.get("first_kill") or {}).get("leaf") or "")
        for k, chunk in enumerate([why[i:i + 62] for i in range(0, min(len(why), 186), 62)]):
            p.append('<text x="%d" y="%d" font-size="9" font-family="sans-serif" fill="#555">%s</text>' % (ox + 8, oy + 188 + 11 * k, esc(chunk)))
    else:
        p.append('<text x="%d" y="%d" font-size="11" font-family="sans-serif" fill="#9e9e9e">not run yet</text>' % (ox + 8, oy + 172))
    p.append("</g>")
    return "".join(p)


def svg(sp, sibs):
    ss = (sp or {}).get("siblings") or []
    n = max(len(ss), 1)
    rowsn = (n + COLS - 1) // COLS
    width, height = COLS * (W + PAD) + PAD, rowsn * (H + PAD) + 92
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
           '<rect width="%d" height="%d" fill="#fafafa"/>' % (width, height),
           '<text x="%d" y="28" font-size="16" font-family="sans-serif" font-weight="bold">A257 -- the SEAM: the %d near-Trump siblings of the aligned descent to the tube (pad %s, delta_pin %s)</text>'
           % (PAD, len(ss), esc((sp or {}).get("pad")), "1e-2"),
           '<text x="%d" y="48" font-size="11" font-family="sans-serif" fill="#444">Each panel is ONE aligned cut at the tube wall.  The shaded half is the sibling the ordinary rules must kill; the clear half holds the Trump image and is where the spine descends to TUBE-KILL.</text>' % PAD,
           '<text x="%d" y="64" font-size="11" font-family="sans-serif" fill="#444">Green = the sibling died (rule named).  Red = it did not die inside the wall -- that panel IS the seam gap (delta_LP &lt; delta_basin there).  Grey = not run.</text>' % PAD]
    for k, s in enumerate(ss):
        out.append(panel(s, sibs.get(s["sibling"]), PAD + (k % COLS) * (W + PAD), 80 + (k // COLS) * (H + PAD)))
    out.append("</svg>")
    return "\n".join(out)


def table(sp, sibs):
    ss = (sp or {}).get("siblings") or []
    L = ["# A257 -- the seam pilot's SIBLING TABLE (results/pilot257.jsonl)", "",
         "Page `%s`, pad `%s`, delta_pin 1e-2.  Spine: **%s aligned cut(s)**, %s TUBE-KILL, %s gate hit(s), "
         "%s node(s), %s s.  Each sibling below is run on its own with A211's ORDINARY rules (the gate is false "
         "there), the spine replayed first." % ((sp or {}).get("nid"), (sp or {}).get("pad"), (sp or {}).get("aligned_cuts"),
                                                (sp or {}).get("tube_kills"), (sp or {}).get("gate_hits"),
                                                (sp or {}).get("n_nodes"), (sp or {}).get("seconds")), "",
         "| # | sibling | cut | excess x r | verdict | rule | subtree s | nodes | run s |", "|---|---|---|---|---|---|---|---|---|"]
    for s in ss:
        v = sibs.get(s["sibling"]) or {}
        L.append("| %s | `%s` | %s %s %s %s | %s | **%s** | %s | %s | %s | %s |" % (
            s["cut_index"], s["sibling"], s["role"], s["dim"],
            "<=" if s["side_with_image"] == "hi" else ">=", s["m_f"], s["excess"],
            v.get("verdict") or "not run", ",".join(v.get("rules") or []) or "-", v.get("seconds"),
            v.get("n_nodes"), v.get("run_seconds")))
    L += ["", "Rules: `EmptyBox` = the multibox cascade emptied a role; `CC` = Lemma CORNER-COVER; `NOROOM*` = A189 "
              "Lemma 1 / Lemma CN; `REACH`, `S-PAIR`, `RSPLIT-EMPTY`, `SNAP`, `FC+EPS` as in A211 notes/coarse_tree.md.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    sp, sibs = collect()
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    open(TABLE, "w", encoding="utf-8").write(table(sp, sibs))
    open(PAGE, "w", encoding="utf-8").write(svg(sp, sibs))
    print("A257: %s siblings, %d run; %s; %s" % (len((sp or {}).get("siblings") or []), len(sibs),
                                                 os.path.relpath(TABLE, ROOT), os.path.relpath(PAGE, ROOT)))
