"""A268 -- one SVG panel per terminal representative: the role HULL BOXES of the node exactly as its certificate
records them (centre rectangles; tilt range in the label), the container [0, s], and a note saying what the node IS.
Coordinates are read from the certificates, never retyped; the geometry check asserts every box lies in [0, s]^2.

    python fig268.py   ->  docs/residue_map/campaigns/A268-terminal-leaves/terminal268.svg"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A268-terminal-leaves", "terminal268.svg")
S = 3.877083590022814
K5 = ("attempts/A211-coarse-tree/certs/coarsetree211_k5_16_interior_Y0384__g1_R.2.1.5.p2.p2.2.2.2.json", "g1_page", "R.2.1.5.p2.p2.2.2.2")
T5 = ("attempts/A256-trump5-passes/certs/coarsetree211_c0_Y0886__zero_R.3.3.2.p1.p1.2.2.2.2.2.2.json", "zero_page", "R.3.3.2.p1.p1.2.2.2.2.2.2.2")
SEAM = "attempts/A257-trump5-window/certs/pilot257_synth257_d001_h002_t2_g1_sib_R_1_2_1.json"
COL = {"H": "#b03a2e", "F1": "#1f618d", "F2": "#117a65", "F3": "#7d3c98", "F4": "#b9770e", "F5": "#5d6d7e"}


def node_boxes(path, run, label):
    d = json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    n = [x for x in d["runs"][run]["nodes"] if x.get("label") == label][-1]
    return {k: v for k, v in n["roles"].items()}, n.get("role_slots") or {}, n.get("forced_H") or []


def seam_boxes():
    d = json.load(open(os.path.join(ROOT, SEAM), encoding="utf-8"))
    out = {}
    for t in d["out"]["tests"]:
        if t.get("test") == "ROLE-CLIP" and t.get("box_after"):
            out[t["role"]] = t["box_after"]
    return out


def panel(x0, title, boxes, notes, zoom=None):
    W = 300.0
    lo, hi = (0.0, S) if zoom is None else zoom
    sc = W / (hi - lo)
    g = ['<g transform="translate(%d,40)">' % x0, '<text x="0" y="-14" font-size="13" font-weight="bold">%s</text>' % title,
         '<rect x="0" y="0" width="%.1f" height="%.1f" fill="none" stroke="#333"/>' % (W, W)]
    for r, b in sorted(boxes.items()):
        if r.startswith("P"):
            continue
        bx0, bx1, by0, by1, t0, t1 = b
        assert 0.0 <= bx0 <= bx1 <= S + 1e-9 and 0.0 <= by0 <= by1 <= S + 1e-9, (r, b)     # the geometry check
        X, Y = (bx0 - lo) * sc, W - (by1 - lo) * sc
        w, h = max((bx1 - bx0) * sc, 1.5), max((by1 - by0) * sc, 1.5)
        c = COL.get(r[:2] if r.startswith("F") else "H", "#444")
        g.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" fill-opacity="0.18" stroke="%s"/>' % (X, Y, w, h, c, c))
        g.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s">%s %.0f-%.0f&#176;</text>' % (X + 2, Y + 11, c, r, t0, t1))
    for i, s in enumerate(notes):
        g.append('<text x="0" y="%d" font-size="10.5">%s</text>' % (W + 18 + 14 * i, s))
    g.append("</g>")
    return "\n".join(g)


def main():
    kb, ks, kf = node_boxes(*K5)
    tb, ts, tf = node_boxes(*T5)
    sb = seam_boxes()
    k_notes = ["k5_16_interior_Y0384 g1, start R.2.1.5.p2.p2.2.2.2 (role centre boxes).",
               "Named: F1@TL(1,0), F2@TR(0,1), F3@BL(1,0); H forced at TL(1,0);",
               "F4 = F5: the two pocket squares (unnamed, miss TL(1,0)).",
               "IS: a JOINT-COUNT-infeasible node -- no pairwise-compatible",
               "choice of rows gives every slot two meeters. 27 passes",
               "never saw it: the 200k-node cap. count268: DEAD in 3.7 s."]
    t_notes = ["trump5 c0_Y0886 pad 0, start R.3.3.2.p1.p1.2.2.2.2.2.2,",
               "child .2 (the ALIVE leaf). Named: F1@BR(0,1), F2@BL(1,1),",
               "F3@BL(0,2); F4 = F5 unnamed, tilt 0-90.",
               "IS: 99.4% of 2,217 s in capped counts; the pad-0",
               "residue of trump5 is now EMPTY (A256 pass 12).", ""]
    s_notes = ["A257 far sibling R.1.2.1 (synth257 g1), true scale.",
               "Every box <= 0.004 wide, <= 0.4 deg of tilt: a near-Trump",
               "configuration, all six slots FC-forced (avail = 2).",
               "IS: a fixed point of every rule; ROLE-SPLIT's WIDE gate",
               "blocked it. Forced ROLE-SPLIT (F1 x, F2 t): DEAD in 286 s.", ""]
    body = [panel(20, "k5 terminal node", kb, k_notes), panel(360, "trump5 terminal node", tb, t_notes)]
    # the seam panel: the whole square (the boxes are dots at this scale), each box drawn at its true place
    body.append(panel(700, "A257 far sibling (true scale)", sb, s_notes))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1030" height="480" font-family="sans-serif">\n'
           '<rect width="100%%" height="100%%" fill="white"/>\n%s\n'
           '<text x="20" y="470" font-size="10" fill="#666">A268 terminal leaves: role hull boxes (centres) read from the '
           'certificates (seam: the fixed-point leaf R.1.2.1.1, its last ROLE-CLIP boxes); container s = %.6f.</text>\n</svg>\n') % ("\n".join(body), S)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(svg)
    print(OUT)


if __name__ == "__main__":
    main()
