"""A188 -- docs/residue_map/s01_basin.svg in the drawing rules of docs/residue_map/gen_a57_lp.py.

Three panels (one per class frame k5_11, k5_16, trump5), each: the container at s* = 4 (S01 drawn as a
REAL packing at its own side -- A107's representative in trump5, the 4x4 grid completion of the frame's
pins in the other two, every drawn square checked for containment and pairwise disjointness) with the
s0 container overlaid and a banner (s* > s0); the certified bands (results/s01_basin.jsonl, `any`
variant) as thin dashed outlines: the k-pin line's admissible c-interval widened by the band half-width
0.207, the lock line of the representative in red; the frame's alive S01/S03 pages' conditioned boxes
(results/consumer188.jsonl) coloured by containment (green = inside a band, orange = outside, with the
growth factor), and a note per panel saying what it IS.  READ-ONLY on every other attempt.

    python draw188.py
"""
from __future__ import annotations

import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib188 as L                          # noqa: E402

S = 120                                    # px per unit
SSTAR = 4.0
OUT = os.path.join(L.ROOT, "docs", "residue_map", "s01_basin.svg")


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def sat(p, q):
    axes = []
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
    best = -9
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]
        qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def packing_for(frame, ident):
    """(name, x, y, theta) of a side-4 S01 packing satisfying the frame's pins."""
    pins = list(L.CLASS_PINS[frame])
    out = [(p, float(L.slot_xy(p, 4)[0]), float(L.slot_xy(p, 4)[1]), 0.0) for p in pins]
    if frame == "trump5":
        for f in ident["free"]:
            out.append((f["name"], f["x"], f["y"], math.radians(f["theta_deg"])))
        return out
    # grid completion: the lock row y in [1,2] first (BL(0,1) + three squares), then fill
    cells = [(1, 1), (2, 1), (3, 1), (2, 0), (1, 3), (2, 3), (3, 2), (0, 2), (2, 2), (3, 3), (1, 2)]
    used = {(int(x - 0.5), int(y - 0.5)) for _, x, y, _ in out}
    k = 0
    for (i, j) in cells:
        if len(out) >= 11:
            break
        if (i, j) in used:
            continue
        out.append(("f%d" % k, i + 0.5, j + 0.5, 0.0)); used.add((i, j)); k += 1
    return out


def check(pk, s):
    polys = [sq(x, y, t) for _, x, y, t in pk]
    worst = min([sat(polys[i], polys[j]) for i in range(len(polys)) for j in range(i + 1, len(polys))] or [0])
    inside = all(0 - 1e-9 <= px <= s + 1e-9 and 0 - 1e-9 <= py <= s + 1e-9 for P in polys for px, py in P)
    return worst, inside


def panel(ox, oy, frame, ident, certs, pages):
    o = []
    H = SSTAR * S
    Y = lambda y: oy - y * S                                   # noqa: E731
    X = lambda x: ox + x * S                                   # noqa: E731
    pk = packing_for(frame, ident)
    worst, inside = check(pk, SSTAR)
    o.append(text(ox, oy - H - 46, "%s frame -- S01, the room family, drawn as a packing at its own side s* = 4.000 (%s)" % (
        frame, "A107's representative" if frame == "trump5" else "4x4 grid completion of the pins"), 12, bold=True))
    o.append(text(ox, oy - H - 30, "checked: worst pairwise SAT gap %+.4f, all inside the s* container: %s | s* - s0 = +0.1229 (13x the pinwheel's slack)" % (worst, inside), 9.5, "#444"))
    o.append(text(ox, oy - H - 16, "BANNER: s* > s0 -- this configuration is NOT a packing at s0; the s0 container (black) is overlaid on the s* container (grey)", 9.5, "#b71c1c", bold=True))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#999" stroke-width="1.5"/>' % (ox, oy - H, H, H))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (ox, oy - L.S0 * S, L.S0 * S, L.S0 * S))
    pins = set(L.CLASS_PINS[frame])
    for n, x, y, t in pk:
        P = sq(x, y, t)
        pts = " ".join("%.1f,%.1f" % (X(px), Y(py)) for px, py in P)
        if n in pins:
            o.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>' % pts)
        else:
            o.append('<polygon points="%s" fill="#ffe082" fill-opacity="0.5" stroke="#8d6e63" stroke-width="1.2"/>' % pts)
        o.append(text(X(x), Y(y) + 3, n, 8, "#333", anchor="middle"))
    # the lock line of the representative (trump5 only: y in [1.190, 1.995])
    if frame == "trump5" and ident.get("lock"):
        lk = ident["lock"]
        c = 0.5 * (lk["c_lo"] + lk["c_hi"])
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d32f2f" stroke-width="1.5" stroke-dasharray="6,3"/>' % (X(0), Y(c), X(SSTAR), Y(c)))
        o.append(text(X(SSTAR) + 4, Y(c) + 3, "lock: 4 unit chords, y = %.2f" % c, 8.5, "#d32f2f"))
    # the certified bands (any-tilt variant), one dashed outline per line family
    for e in certs:
        if e["cls"] != frame or e["variant"] != "any":
            continue
        ln = e["line"]
        w = e["w_float"]
        lo, hi = ln["c_lo_float"] - w, ln["c_hi_float"] + w
        col = "#2e7d32" if ln["k"] < 3 else "#6a1b9a"
        if ln["orient"] == "h":
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.05" stroke="%s" stroke-width="0.8" stroke-dasharray="3,3"/>' % (
                X(0), Y(hi), L.S0 * S, (hi - lo) * S, col, col))
            o.append(text(X(0.02), Y(hi) + 9, "y-band k=%d: %d free square(s) within 0.207 of y in [%.2f, %.2f]" % (ln["k"], e["n_free"], ln["c_lo_float"], ln["c_hi_float"]), 7.5, col))
        else:
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.05" stroke="%s" stroke-width="0.8" stroke-dasharray="3,3"/>' % (
                X(lo), Y(L.S0), (hi - lo) * S, L.S0 * S, col, col))
            o.append('<text x="%.1f" y="%.1f" font-size="7.5" fill="%s" transform="rotate(-90 %.1f %.1f)">%s</text>' % (
                X(lo) + 8, Y(0) - 4, col, X(lo) + 8, Y(0) - 4, esc("x-band k=%d: %d free within 0.207 of x in [%.2f, %.2f]" % (ln["k"], e["n_free"], ln["c_lo_float"], ln["c_hi_float"]))))
    # the pages' conditioned boxes
    n_in = n_out = 0
    for r in pages:
        if r["frame"] != frame or r["family"] not in ("S01", "S03") or not r.get("box"):
            continue
        x0, x1, y0, y1, t0, t1 = r["box"]
        col = "#2e7d32" if r["contained"] else "#ef6c00"
        n_in += r["contained"]; n_out += (not r["contained"])
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.2"/>' % (
            X(x0), Y(y1), (x1 - x0) * S, (y1 - y0) * S, col, col))
        lab = r["nid"].replace("k5_11_interior_", "").replace("k5_16_interior_", "").replace("slack0.02_", "s")
        o.append(text(X(x1) + 1, Y(y0) - 1, "%s %s%s" % (lab, r["family"], "" if r["contained"] else " x%.1f" % (r["growth"] or 0)), 6.5, col))
    notes = ["WHAT THIS IS: the S01 basin in the %s frame = every dashed band in which (4 - k) non-pin squares," % frame,
             "at ANY position along the line and ANY tilt, join the k pins of that line: side >= 4 > s0 (Theorem S01-LINE).",
             "Pages: the conditioned boxes of the frame's alive S01/S03 pages -- green = inside a certified band (%d: the YES" % n_in,
             "leaf is dead, the NO children owe 3 - k boxes), orange = outside (%d; the growth factor x is printed)." % n_out,
             "Blue = the frame's pins in their delta-cores; yellow = the other squares of the side-4 packing; purple bands =",
             "the k = 3 lines (A144's node-level guard-line kill: one more square with chord > 0.877 on the line)."]
    for i, ln in enumerate(notes):
        o.append(text(ox, oy + 14 + 12 * i, ln, 9, "#1b5e20", bold=(i == 0)))
    return o


def main():
    ident = json.load(open(os.path.join(L.NOTES, "s01_identity.json"), encoding="utf-8"))
    certs = [json.loads(l) for l in open(os.path.join(L.RES, "s01_basin.jsonl"), encoding="utf-8")]
    pages = [json.loads(l) for l in open(os.path.join(L.RES, "consumer188.jsonl"), encoding="utf-8")]
    W = 3 * (SSTAR * S + 170) + 40
    Hh = SSTAR * S + 200
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hh + 40, W, Hh + 40),
         '<rect width="100%" height="100%" fill="#fff"/>',
         text(20, 22, "A188 -- the S01 basin (the 'room at side 4' family) is a LINE: 4 unit chords on one axis-parallel line lock the side at 4.000 > s0 = 3.877084 -- per class frame, with the alive S01/S03 pages", 14, bold=True),
         text(20, 40, "Source: attempts/A188-s01-basin/results/{s01_basin.jsonl, consumer188.jsonl}, docs/proofs/local_certificate_s01.md; drawing rules of docs/residue_map/gen_a57_lp.py (every drawn square checked for containment and disjointness).", 9.5, "#444")]
    for i, frame in enumerate(("k5_11", "k5_16", "trump5")):
        ox = 40 + i * (SSTAR * S + 170)
        oy = 110 + SSTAR * S
        o += panel(ox, oy, frame, ident, certs, pages)
    o.append("</svg>")
    open(OUT, "w", encoding="utf-8").write("\n".join(o))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
