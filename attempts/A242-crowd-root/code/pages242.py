"""A242 -- the campaign pages: the CROWD ROOT, the first kills, the survivors.

Self-contained SVG (no plotting library); every panel states what it draws, the cell's label and
the leaf that decided it.  `docs/residue_map/campaigns/A242-crowd-root/`.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
OUT = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A242-crowd-root")
sys.path.insert(0, HERE)
import root242 as R                                                # noqa: E402

PAD, W = 46, 300
CSS = ("<style>text{font-family:Helvetica,Arial,sans-serif}"
       ".t{font-size:12px;fill:#111}.s{font-size:10px;fill:#555}.h{font-size:15px;fill:#000}</style>")


def _sc(S):
    return (W - 2 * PAD) / S


def panel(x0, y0, S, title, sub, roles=None, pockets=None, cores=None, meeters=None, w=None):
    k = _sc(S)
    def X(u): return x0 + PAD + u * k
    def Y(v): return y0 + W - PAD - v * k
    p = ['<g>', '<text class="h" x="%d" y="%d">%s</text>' % (x0 + PAD - 8, y0 + 20, title)]
    for i, ln in enumerate((sub or "").split("|")):
        p.append('<text class="s" x="%d" y="%d">%s</text>' % (x0 + PAD - 8, y0 + 34 + 11 * i, ln))
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000" stroke-width="1.4"/>'
             % (X(0), Y(S), S * k, S * k))
    if w is not None:                                              # the four widened corner boxes
        for cx, cy in ((0, 0), (S, 0), (S, S), (0, S)):
            u0, u1 = (0, 1 + w) if cx == 0 else (S - 1 - w, S)
            v0, v1 = (0, 1 + w) if cy == 0 else (S - 1 - w, S)
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fde8e8" stroke="#c33" '
                     'stroke-dasharray="3 2" stroke-width="0.8"/>'
                     % (X(u0), Y(v1), (u1 - u0) * k, (v1 - v0) * k))
    for pk in (pockets or []):
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dcecff" stroke="#36c" '
                 'stroke-width="0.8"/>' % (X(pk[0]), Y(pk[3]), (pk[1] - pk[0]) * k, (pk[3] - pk[2]) * k))
    for nm, b in sorted((roles or {}).items()):
        col = {"A": "#1a7", "B": "#a51"}[nm[-1]]
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.1"/>' % (X(b[0]), Y(b[3]), (b[1] - b[0]) * k, (b[3] - b[2]) * k, col))
        p.append('<text class="s" x="%.1f" y="%.1f" fill="%s">%s %.0f-%.0f</text>'
                 % (X(b[0]) + 1, Y(b[3]) - 2, col, nm, b[4], b[5]))
    for poly, col in (cores or []):
        p.append('<polygon points="%s" fill="%s" fill-opacity="0.45" stroke="%s" stroke-width="0.7"/>'
                 % (" ".join("%.1f,%.1f" % (X(a), Y(b)) for a, b in poly), col, col))
    for (cx, cy, th, col) in (meeters or []):
        t = math.radians(th)
        pts = []
        for dx, dy in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)):
            pts.append((cx + dx * math.cos(t) - dy * math.sin(t), cy + dx * math.sin(t) + dy * math.cos(t)))
        p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1.2"/>'
                 % (" ".join("%.1f,%.1f" % (X(a), Y(b)) for a, b in pts), col))
    p.append('</g>')
    return "\n".join(p)


def page(path, title, note, panels, cols=3):
    rows = (len(panels) + cols - 1) // cols
    h = rows * W + 62
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
           % (cols * W, h, cols * W, h), CSS,
           '<rect width="100%" height="100%" fill="#fff"/>',
           '<text class="h" x="14" y="24">%s</text>' % title,
           '<text class="s" x="14" y="40">%s</text>' % note]
    for i, fn in enumerate(panels):
        out.append(fn((i % cols) * W, 52 + (i // cols) * W))
    out.append('</svg>')
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", path, flush=True)


def rows_of(band):
    f = os.path.join(BASE, "results", "crowd242_%s.jsonl" % band)
    if not os.path.exists(f):
        return []
    return [json.loads(x) for x in open(f, encoding="utf-8") if x.strip()]


def main():
    os.makedirs(OUT, exist_ok=True)
    # (a) the root, one panel per band
    pans = []
    for tag, lo, hi in R.BANDS:
        c = R.root_cell(tag)
        pans.append(lambda x, y, c=c, lo=lo, hi=hi: panel(
            x, y, c["S"], "H_B(%s)" % c["band"],
            "sides [%.4f, %.4f], reference S = %.4f|K0-WIDEN w = %.5f (lam_max = %.5f)|"
            "8 role boxes (A green, B brown) = [1/2, 1+w+sqrt2/2]^2 x [0,90) per corner|"
            "3 anonymous free squares; CC-1(ii) slack %.3f" % (lo, hi, c["S"], c["w"], c["lam_max"],
                                                              c["disjoint_slack"]),
            roles=c["roles"], w=c["w"]))
    page(os.path.join(OUT, "crowd_root.svg"), "A242 -- the CROWD ROOT H_B, one cell per side band",
         "k0_route.md s.4.2 (Lemma K0-BLOCKED) + K0-WIDEN s.4.1 + local_lock.md s.2.1 LOCALITY (i); "
         "red dashed = the widened corner box B_c^w, coloured rectangles = the meeters' CENTRE boxes", pans, cols=2)

    # (b) the first kills and (c) the survivors
    for band in ("W", "B3"):
        rows = rows_of(band)
        if not rows:
            continue
        dead = [r for r in rows if r.get("verdict") == "DEAD"][:3]
        alive = sorted([r for r in rows if r.get("verdict") == "UNDECIDED"],
                       key=lambda r: -r["depth"])[:3]
        S = [b for b in R.BANDS if b[0] == band][0][2]
        pans = []
        for r in dead + alive:
            g = (r.get("l2_gate") or {})
            pans.append(lambda x, y, r=r, S=S, g=g: panel(
                x, y, S, "%s  d%d" % (r["verdict"], r["depth"]),
                "%s|leaf %s / %s|%s|pockets %d alive %d  cn %s|L2 gate %s (needs > 1.414)"
                % (r["label"][-44:], r.get("leaf"), r.get("clip") or r.get("step"),
                   (r.get("reason") or "")[:66], r.get("n_pockets") or 0, r.get("n_alive") or 0,
                   r.get("cn_bound"), g.get("worst_gap")),
                roles=r["roles"], pockets=r.get("alive") or []))
        page(os.path.join(OUT, "cells_%s.svg" % band),
             "A242 -- band %s: the first kills (top) and the deepest survivors (bottom)" % band,
             "blue = the pocket that survives the cover (A221 POCKET-DEAD); a DEAD cell has none",
             pans, cols=3)


if __name__ == "__main__":
    main()
