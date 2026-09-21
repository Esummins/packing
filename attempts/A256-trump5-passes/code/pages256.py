"""A256 -- the campaign pages: docs/residue_map/campaigns/A256-trump5-passes/{seam_axis,node_atlas}.svg.

seam_axis.svg  -- the SIDE axis [3.82, s0] with, drawn to scale from the exact numbers: the certified tube reach
(slot ray, r = A60's landings), the (K)-slack reach T_K(delta_pin) for the four pin slacks that occur in the lab,
the G1 slab the pass loop works in, and the region only an unmeasured delta_LP could close (grey stipple).
node_atlas.svg -- the 149 trump5 nodes, one tile each: A212's pad-0 verdict and the (a)/(b) ray triage.  Undecided
is ALWAYS grey stipple; nothing undecided is ever green.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A256-trump5-passes")
TRIAGE = os.path.join(HERE, "..", "results", "triage256.json")
S0, SHAT, LO = 3.877084, 3.877083590022814, 3.82
GBOT = 3.861637
STIPPLE = ('<pattern id="st" width="6" height="6" patternUnits="userSpaceOnUse">'
           '<rect width="6" height="6" fill="#f4f4f4"/><circle cx="1.5" cy="1.5" r="1.1" fill="#9aa0a6"/>'
           '<circle cx="4.5" cy="4.5" r="1.1" fill="#9aa0a6"/></pattern>')


def T_K(d):
    return ((2.0 / 3.0) * d * SHAT - (S0 - SHAT)) / (1 + (2.0 / 3.0) * d)


def seam_axis():
    W, H, x0, x1 = 980, 430, 90, 930
    def X(s):
        return x0 + (s - LO) * (x1 - x0) / (S0 - LO)
    L = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="Georgia,serif" font-size="13">' % (W, H),
         '<defs>%s</defs><rect width="%d" height="%d" fill="#ffffff"/>' % (STIPPLE, W, H),
         '<text x="%d" y="30" font-size="17">trump5: which side of [3.82, s0] each certificate family reaches</text>' % x0,
         '<text x="%d" y="50" fill="#555">A256, 2026-09-21 -- drawn to scale from docs/proofs/contraction_tube.md s.3-s.4 and the records\' own pin slack</text>' % x0]
    y = 92
    L.append('<rect x="%d" y="%d" width="%d" height="26" fill="url(#st)" stroke="#bbb"/>' % (x0, y, x1 - x0))
    L.append('<text x="%d" y="%d" font-size="12" fill="#333">the window: every side m in [3.82, s0] must be excluded (s0 - s-hat = 4.1e-7)</text>' % (x0 + 8, y + 18))
    L.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#111"/>' % (x0, y + 40, x1, y + 40))
    for s, t in ((LO, "3.82"), (3.84, "3.84"), (3.86, "3.86"), (GBOT, "3.861637 = G1 bottom"), (SHAT, "s-hat = 3.8770836")):
        L.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#111"/>' % (X(s), y + 34, X(s), y + 46))
        L.append('<text x="%.1f" y="%d" font-size="11" text-anchor="middle" fill="#333">%s</text>' % (X(s), y + 62, t))
    rows = [("tube, slot ray, A60 landing radii (r_c 1.6e-3, r_th 2.1e-3): T = 0.045", SHAT - 0.045, "#2e7d32", "certs/tube_slot_T4.5e-2_landing.json  [T]"),
            ("tube, slot ray, r = 6.5e-4: T = 0.0571 = the whole window", LO, "#2e7d32", "certs/tube_slot_T5.71e-2_window.json  [T] (no tree lands this tightly)"),
            ("(K) slack reach T_K(delta_pin = 2e-2) = 0.0510", SHAT - T_K(2e-2), "#1565c0", "3 records: slack0.02_c0_Y0272 / _Y0411 / _Y0419"),
            ("(K) slack reach T_K(delta_pin = 1e-2) = 0.0257", SHAT - T_K(1e-2), "#1565c0", "A57's G1 operating point -- what the k5 pages carry"),
            ("(K) slack reach T_K(delta_pin = 3.08e-8) &lt; 0: NOTHING", SHAT, "#b71c1c", "146 of A60's 149 trump5 records  [C] open link O1")]
    y = 200
    for lab, left, col, note in rows:
        w = max(2.0, X(SHAT) - X(max(left, LO)))
        L.append('<rect x="%.1f" y="%d" width="%.1f" height="17" fill="%s" opacity="0.75"/>' % (X(SHAT) - w, y, w, col))
        L.append('<text x="%d" y="%d" font-size="12">%s</text>' % (x0, y - 3, lab))
        L.append('<text x="%d" y="%d" font-size="10.5" fill="#666">%s</text>' % (x0 + 470, y - 3, note))
        y += 40
    yb = y + 4
    L.append('<rect x="%.1f" y="%d" width="%.1f" height="17" fill="url(#st)" stroke="#999"/>' % (X(LO), yb, X(GBOT) - X(LO)))
    L.append('<text x="%d" y="%d" font-size="12">below the G1 slab: plain slack-core certificates, and the seam\'s second number</text>' % (x0, yb - 3))
    L.append('<text x="%d" y="%d" font-size="10.5" fill="#666">delta_LP(trump5) NEVER SCANNED -- open link O3; grey = undecided</text>' % (x0 + 470, yb - 3))
    L.append('<rect x="%.1f" y="%d" width="%.1f" height="17" fill="none" stroke="#1565c0" stroke-dasharray="4 3"/>' % (X(GBOT), yb, X(S0) - X(GBOT)))
    L.append('<text x="%.1f" y="%d" font-size="10.5" fill="#1565c0" text-anchor="end">G1 slab: T\' = 0.01545, where A256\'s window pilot would run</text>' % (X(S0) - 4, yb + 31))
    L.append('<text x="%d" y="%d" font-size="11.5" fill="#333">Read: the tube is NOT the binding link.  The binding link is the pin slack of A60\'s records (red): at delta_pin = 3.08e-8</text>' % (x0, H - 34))
    L.append('<text x="%d" y="%d" font-size="11.5" fill="#333">a certificate at s0 reaches no side below s0 at all, so no pad-g1 run on them is a window statement.  Re-emit at delta_pin &gt;= 1e-2.</text>' % (x0, H - 16))
    L.append('</svg>')
    return "\n".join(L)


def node_atlas():
    d = json.load(open(TRIAGE, encoding="utf-8"))
    rows = d["rows"]
    cols, cell = 20, 40
    W = 90 + cols * cell + 40
    H = 150 + ((len(rows) + cols - 1) // cols) * cell + 90
    L = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="Georgia,serif" font-size="13">' % (W, H),
         '<defs>%s</defs><rect width="%d" height="%d" fill="#ffffff"/>' % (STIPPLE, W, H),
         '<text x="60" y="34" font-size="17">the 149 trump5 nodes: A212\'s pad-0 verdict and A256\'s ray triage</text>',
         '<text x="60" y="54" fill="#555" font-size="12">tile = one node (13 gallery pages + 136 of A60\'s alive frontier).  Solid = DEAD at s0 (pass 1).  Grey stipple = ALIVE,',
         '</text><text x="60" y="72" fill="#555" font-size="12">undecided -- never green.  A thick border would mark class (b) (a contracted Trump image might fit): THERE ARE NONE.</text>']
    x0, y0 = 60, 110
    for i, r in enumerate(rows):
        cx, cy = x0 + (i % cols) * cell, y0 + (i // cols) * cell
        dead = r["a212"] == "DEAD"
        fill = "#2e7d32" if dead else "url(#st)"
        stroke = "#8b0000" if r["klass"] == "b" else "#999"
        sw = 3 if r["klass"] == "b" else 1
        L.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="%d" opacity="%s"><title>%s: %s, class (%s), delta_pin %g</title></rect>'
                 % (cx, cy, cell - 6, cell - 6, fill, stroke, sw, "0.8" if dead else "1", r["nid"], r["a212"], r["klass"], r["dpin"]))
        if r["dpin"] > 1e-3:
            L.append('<circle cx="%d" cy="%d" r="4" fill="#1565c0"><title>delta_pin = 2e-2: window-capable at g1</title></circle>' % (cx + cell - 12, cy + 8))
    yb = y0 + ((len(rows) + cols - 1) // cols) * cell + 24
    c = d["counts"]
    L += ['<rect x="60" y="%d" width="22" height="22" fill="#2e7d32" opacity="0.8"/><text x="90" y="%d" font-size="12">DEAD at s0, pass 1: %d</text>' % (yb, yb + 16, c["a_dead"] + c["b_dead"]),
          '<rect x="280" y="%d" width="22" height="22" fill="url(#st)" stroke="#999"/><text x="310" y="%d" font-size="12">ALIVE / undecided: %d -- A256\'s pass loop</text>' % (yb, yb + 16, c["a_alive"] + c["b_alive"]),
          '<circle cx="640" cy="%d" r="6" fill="#1565c0"/><text x="655" y="%d" font-size="12">delta_pin = 2e-2 (3 records): window-capable</text>' % (yb + 11, yb + 16),
          '<text x="60" y="%d" font-size="12" fill="#333">Triage over the whole ray (scale and slot, every depth t in the pad\'s slab, boxes padded outward): class (a) %d, class (b) %d.</text>' % (yb + 44, c["a"], c["b"]),
          '<text x="60" y="%d" font-size="12" fill="#333">The five corner pins force g = id, and no image square lies in any node\'s H box -- A60/A83 discharged the Trump residue before A212 ran.</text>' % (yb + 62),
          '</svg>']
    return "\n".join(L)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("seam_axis", seam_axis), ("node_atlas", node_atlas)):
        p = os.path.join(OUT, name + ".svg")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(fn())
        print("   -> %s (%d bytes)" % (os.path.relpath(p, ROOT).replace("\\", "/"), os.path.getsize(p)))
