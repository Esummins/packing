"""A186 -- the contact-census page of c0_Y1033: docs/residue_map/c0_Y1033_contacts.svg, in the drawing
rules of docs/residue_map/gen_a57_lp.py (container at side s0, pins light blue, dashed corner cells).
One panel per budget-0 assignment (eight): the eleven boxes (hull of the pieces, tilt range printed),
the CANDIDATE GRAPH (an edge between box centres for every pair the pieces cannot separate; a wall tick
per possible wall contact), and the measured stuck configuration of the node (global186: the least-overlap
configuration of the elastic exact LP at its side s*, every square drawn at its pose, the loaded pairs
of the LP support in red) with s0 overlaid and a banner saying what it IS (an overlap tau > 0 = NOT a
packing; tau = 0 with s* > s0 = a packing of the boxes that needs side s*; tau = 0, s* <= s0, inside the
pieces = a WITNESS).

    python fig186.py [--out docs/residue_map/c0_Y1033_contacts.svg]
"""
from __future__ import annotations
import argparse, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nodes186 as N                                          # noqa: E402
S0 = N.S0
SC = 150                                                      # px per unit
PW, PH = 1010, 720                                            # panel size


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


COL = {"H": "#000", "F1": "#c62828", "F2": "#2e7d32", "F3": "#6a1b9a", "F4": "#ef6c00", "F5": "#00838f"}


def panel(ox, oy, cand, stuck, hull, k):
    X = lambda x: ox + x * SC
    Y = lambda y: oy - y * SC
    out = []
    side = S0
    out.append(text(ox, oy - S0 * SC - 40, "assignment %d: %s   (budget 0: every square boxed)" % (k + 1, cand["short"]), 12, bold=True))
    out.append(text(ox, oy - S0 * SC - 24, "boxes = hull of the multibox pieces (A182 fixed point); candidate graph: %d edges (%d free-free); "
                    "walls %s" % (cand["n_edges"], cand["n_free_edges"], ", ".join("%s:%s" % (r, "".join(w["touch"]) or "-") for r, w in cand["walls"].items())), 9.5, "#444"))
    out.append(text(ox, oy - S0 * SC - 10, "exterior piece faces (loadable box rows, Theorem CC d): %s" %
                    ", ".join("%s %d" % (r, n) for r, n in cand["faces"].items()), 9.5, "#444"))
    # container at s0 and the corner cells
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (X(0), Y(S0), S0 * SC, S0 * SC))
    for (x0, y0) in [(0, 0), (S0 - 1, 0), (0, S0 - 1), (S0 - 1, S0 - 1)]:
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>' % (X(x0), Y(y0 + 1), SC, SC))
    # pins
    centres = {}
    for p in ("P0", "P1", "P2", "P3", "P4"):
        h = hull[p]; cx, cy = 0.5 * (h[0] + h[1]), 0.5 * (h[2] + h[3]); centres[p] = (cx, cy)
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in sq(cx, cy, 0.0))
        out.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>' % pts)
        out.append(text(X(cx), Y(cy) + 4, p, 10, "#1565c0", anchor="middle"))
    # free boxes (hulls)
    for r in ("H", "F1", "F2", "F3", "F4", "F5"):
        h = hull[r]; centres[r] = (0.5 * (h[0] + h[1]), 0.5 * (h[2] + h[3]))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.2"/>' %
                   (X(h[0]), Y(h[3]), (h[1] - h[0]) * SC, (h[3] - h[2]) * SC, COL[r], COL[r]))
        out.append(text(X(h[0]) + 2, Y(h[3]) + 10, "%s [%.0f,%.0f]°" % (r, h[4], h[5]), 8.5, COL[r]))
    # candidate edges
    for (i, j) in cand["edges"]:
        (x1, y1), (x2, y2) = centres[i], centres[j]
        g = cand["pairs"]["%s|%s" % (i, j)]["gap_lo"]
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="%.1f" stroke-opacity="0.55"/>' %
                   (X(x1), Y(y1), X(x2), Y(y2), 0.8 + min(2.5, -g)))
    for r, w in cand["walls"].items():
        cx, cy = centres[r]
        for wall in w["touch"]:
            x2, y2 = {"L": (0, cy), "R": (S0, cy), "B": (cx, 0), "T": (cx, S0)}[wall]
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#999" stroke-width="1" stroke-dasharray="3,3"/>' % (X(cx), Y(cy), X(x2), Y(y2)))
    # the measured stuck configuration
    if stuck:
        s = stuck["side"]; tau = stuck["tau"]
        cfg = stuck["cfg"]
        loaded = set()
        for m, w in stuck["support"]:
            if m[0] == "sel":
                loaded.add(frozenset((m[1], m[2])))
        for r, (cx, cy, thd) in cfg.items():
            col = "#1565c0" if r.startswith("P") else COL[r]
            pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in sq(cx, cy, math.radians(thd)))
            out.append('<polygon points="%s" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2"/>' % (pts, col, col))
        for pr in loaded:
            a, b = sorted(pr)
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d50000" stroke-width="2.5"/>' %
                       (X(cfg[a][0]), Y(cfg[a][1]), X(cfg[b][0]), Y(cfg[b][1])))
        if s > S0 + 1e-9:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#d50000" stroke-width="1.5" stroke-dasharray="6,4"/>' % (X(0), Y(s), s * SC, s * SC))
        what = ("WITNESS: a packing of the boxes at side <= s0" if tau <= 1e-9 and s <= S0 + 1e-9 and stuck["all_inside"] else
                "a packing of the hull boxes that needs side %.6f > s0" % s if tau <= 1e-9 else
                "NOT a packing: least overlap tau = %.4f at side %.6f (elastic LP, %d starts)" % (tau, s, stuck.get("n_starts", 0)))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="18" fill="%s" fill-opacity="0.9"/>' % (X(0), Y(S0) - 0, S0 * SC, "#ffcdd2" if tau > 1e-9 or s > S0 else "#c8e6c9"))
        out.append(text(X(0) + 4, Y(S0) + 13, what, 10, "#b71c1c" if tau > 1e-9 or s > S0 else "#1b5e20", bold=True))
        legend = "stuck configuration drawn at its pose; red = LP support (loaded pairs): %s; inside pieces: %s" % (
            " ".join("%s-%s" % tuple(sorted(pr)) for pr in loaded) or "-",
            "all" if stuck["all_inside"] else "not " + ",".join(r for r, v in stuck["inside"].items() if not v))
        out.append(text(ox, oy + 14, legend, 9, "#444"))
        out.append(text(ox, oy + 27, "s* - s0 = %+.2e, s* - shat = %+.2e; black square = container at s0; red dashed = container at s* when s* > s0" %
                        (s - S0, s - N.A.SHAT), 9, "#444"))
    else:
        out.append(text(ox, oy + 14, "no measured stuck configuration for this assignment (global186 not run)", 9, "#444"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(N.ROOT, "docs", "residue_map", "c0_Y1033_contacts.svg"))
    args = ap.parse_args()
    cands = json.load(open(os.path.join(N.RES, "candidates186_b0.json"), encoding="utf-8"))
    assigns = {a["label"]: a for a in json.load(open(os.path.join(N.RES, "assignments186.json"), encoding="utf-8"))}
    stuck = {}
    gp = os.path.join(N.RES, "global186.jsonl")
    if os.path.exists(gp):
        for l in open(gp, encoding="utf-8"):
            r = json.loads(l)
            if not r["results"]:
                continue
            best = min(r["results"], key=lambda q: (q["tau"] > 1e-9, q["tau"] if q["tau"] > 1e-9 else q["side"]))
            best = dict(best); best["n_starts"] = r["n_starts"]
            cur = stuck.get(r["label"])
            if cur is None or (best["tau"], best["side"]) < (cur["tau"], cur["side"]):
                stuck[r["label"]] = best
    n = len(cands)
    cols = 2
    rows = (n + cols - 1) // cols
    W, H = cols * PW + 40, rows * PH + 120
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica, Arial, sans-serif">' % (W, H),
           '<rect width="100%" height="100%" fill="#fff"/>',
           text(20, 26, "c0_Y1033 (trump5) -- CONTACT CENSUS of the eight budget-0 assignments under BR(0,1)=H+F1 / TR(0,1)=H+F1 (A186, 2026-09-09)", 15, bold=True),
           text(20, 46, "Per panel: the eleven boxes (pins light blue; free roles = hull of the multibox pieces with the tilt range), the candidate contact graph "
                        "(grey edges: pairs the pieces cannot certify apart, thicker = deeper possible overlap; dashed ticks = possible wall contacts), and the "
                        "measured stuck configuration (global186).", 10, "#444"),
           text(20, 60, "Theorem CC (docs/proofs/contact_census.md): the node is dead iff every Fritz-John point of every selection, box faces included, has side > s0; "
                        "solved by the selection tree (tree186, CAPPED [P]) -- no witness, no kill; the least overlap found is the column P2 | F2 | F3.", 10, "#444")]
    for k, c in enumerate(cands):
        ox = 20 + (k % cols) * PW
        oy = 80 + (k // cols) * PH + S0 * SC + 60
        out += panel(ox, oy, c, stuck.get(c["label"]), assigns[c["label"]]["hull"], k)
    out.append("</svg>")
    open(args.out, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", args.out, "panels", n, "stuck configs", len(stuck))


if __name__ == "__main__":
    main()
