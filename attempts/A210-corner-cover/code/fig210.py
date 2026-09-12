"""A210 -- the page: A202's stage-0 panel + A203's CSP panel per pad, PLUS rule CC's CORNER-COVER band drawn as a
thin dashed region over the container with the note "Lemma CORNER-COVER band" and the pose-class bookkeeping.
    python fig210.py <nid>   ->  docs/residue_map/campaigns/A210-cornercover/cornercover210_<nid>.svg"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
OUTD = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A210-cornercover")
sys.path.insert(0, HERE)
import fig203 as F                                             # noqa: E402  (A202's panel0 / side0, copied)
import fig203b as FB                                           # noqa: E402  (A203's CSP panel, copied)

text, defs, S0 = F.text, F.defs, F.S0
F.RULECOL["Q"] = "#00838f"
F.RULETXT["Q"] = "rule CC: outside the CORNER-COVER band of the square at the corner (Lemma CORNER-COVER)"


def cc_overlay(cert, body, ox, oy, S):
    """the band as a thin dashed region (teal) over the stage-0 panel."""
    X = lambda x: ox + x * S
    Y = lambda y: oy + (S0 - y) * S
    recs = cert.get("cc") or []
    if not recs:
        return
    last = recs[-1]
    for r in last.get("slots") or []:
        for w in r.get("band") or []:
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#00838f" fill-opacity="0.07" '
                        'stroke="#00838f" stroke-width="0.7" stroke-dasharray="3,2"/>'
                        % (X(w[0]), Y(w[3]), max(0.6, (w[1] - w[0]) * S), max(0.6, (w[3] - w[2]) * S)))
        if r.get("band"):
            w = r["band"][0]
            body.append(text(X(w[0]) + 2, Y(w[3]) - 3, "Lemma CORNER-COVER band (%s at %s)" % (r.get("near_corner"), r.get("slot")), 6.5, "#00838f", True))


def cc_panel(cert, body, ox, oy):
    recs = cert.get("cc") or []
    yy = oy + 12
    L = [("rule CC -- Lemma CORNER-COVER (attempts/A210-corner-cover/notes/corner_cover.md), pad lambda = %.6f" % float(cert.get("lam") or 1), 8.5, "#00838f", True),
         ("a square within delta of both walls of an unpinned corner covers the corner slot's unit cell except the two wall wedges;", 7, "#333", False),
         ("every OTHER meeter of that slot has an interior point in the wedges, so its centre is within lambda/sqrt2 of the band drawn dashed above.", 7, "#333", False)]
    if not recs:
        L.append(("no round recorded", 7.5, "#900", False))
    for r in recs:
        L.append(("round %d: %d anonymous piece(s) killed (letter Q), %d H piece(s) killed, %.1f ms" % (
            r.get("round", 0), r.get("killed", 0), r.get("h_killed", 0), r.get("ms", 0)), 7.5, "#000", True))
        if not (r.get("slots") or []):
            L.append(("  no corner slot has a square at its corner: the rule says nothing here", 7, "#555", False))
        for s in r.get("slots") or []:
            L.append(("  %s [%s]: %d pose class(es), all at the corner = %s, %d class(es) excluded (no second meeter), "
                      "pieces %d -> %d, alive cells %s" % (s["slot"], s["near_corner"], s["n_classes"], s.get("all_near"),
                                                          s.get("dead_classes", 0), s["pieces_before"], s["pieces_after"],
                                                          s.get("cells_after")), 7, "#00838f", False))
    for t, sz, c, b in L:
        t = str(t)
        while True:
            body.append(text(ox, yy, t[:150], sz, c, b))
            yy += sz + 3
            t = t[150:]
            if not t:
                break
    return yy


def load(nid):
    out = []
    for f in sorted(glob.glob(os.path.join(CERTS, "cornercover210_%s_*_s0.json" % nid))):
        try:
            c = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        c["_file"] = os.path.basename(f)
        out.append(c)
    out.sort(key=lambda c: {"zero": 0, "g1": 1}.get(c.get("pad"), 2))
    return out


def page_svg(nid, certs):
    S = 118
    PW = int(S0 * S) + 20
    TW, CW = 600, 700
    body = [text(20, 22, "%s -- A210 cornercover210: STAGE 0 (A202's closed-form layer) + A203's piece CSP + RULE CC "
                 "(Lemma CORNER-COVER), pad 0 first then the G1 window pad" % nid, 13, "#000", True),
            text(20, 38, "grey stipple = sub-rects where some forced slot's meeter may still sit; white + letter = dead "
                 "(P pins, W walls, C CN vs H, M tilt-SAT vs H, L chord row, R reach / A161 miss, H / F = H-consistency, "
                 "Q = rule CC); teal dashed = the CORNER-COVER band (where a second meeter of the corner slot must have "
                 "a point); blue = pins; black = H; yellow = the count's witness.", 8, "#444"),
            text(20, 50, "read-only from certs/cornercover210_*.json; rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 8, "#444")]
    y0 = 70
    ybot = y0
    for k, c in enumerate(certs):
        ox = 20 + k * (PW + TW + CW)
        body.append(text(ox, y0 - 6, "PANEL stage 0 + CSP + CC / pad %s: %s" % (c.get("pad"), c["_file"]), 9, "#000", True))
        yb = F.panel0(c, body, ox, y0, S)
        cc_overlay(c, body, ox, y0, S)
        yt = F.side0(c, body, ox + PW + 10, y0 + 12)
        yc = FB.csp_panel(c, body, ox + PW + TW + 20, y0 + 12)
        yq = cc_panel(c, body, ox + PW + TW + 20, yc + 10)
        ybot = max(ybot, yb, yt, yq)
    W = len(certs) * (PW + TW + CW) + 40
    return "\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">'
                      % (W, ybot + 20), defs()] + body + ["</svg>"])


def render(nid):
    certs = load(nid)
    if not certs:
        return None
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, "cornercover210_%s.svg" % nid)
    open(p, "w", encoding="utf-8").write(page_svg(nid, certs))
    return p


if __name__ == "__main__":
    print(render(sys.argv[1]))
