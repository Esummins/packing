"""A197 -- one gallery panel per page killed by the FORCED-CELL PAIR TEST (slotpair197.jsonl).

Drawing rules follow `gen_a57_lp.py`: the container square at S px per unit, the four corner cells
dashed, the class PINS as light-blue axis squares drawn from the record's zero-tilt-width cores, the
conditioned square H as a black box with one example square at the mid tilt drawn at the feasible
centre nearest the box centre, and every number printed on the page.  What is NEW here is the CELL:
the widened open slot box B_p+ (orange), its meeter window (dashed), and the Lemma A1 grid cells of
the two meeters HATCHED EMPTY -- every cell pair the library proved is `EmptyBox`.

    python docs/residue_map/gen_slotpair197.py            # every DEAD page of slotpair197.jsonl
    python docs/residue_map/gen_slotpair197.py <nid> ...  # named pages
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", ".."))
JL = os.path.join(R, "attempts", "A197-slot-pair-pass", "results", "slotpair197.jsonl")
S0 = 969271 / 250000
S = 150                     # px per unit
PAD_L, PAD_T, PAD_B = 40, 96, 150


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>'
            % (x, y, size, col, anchor, b, esc(t)))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def sat(p, q):
    axes = []
    for poly in (p, q):
        for i in range(4):
            a, b = poly[i], poly[(i + 1) % 4]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
    best = -9.0
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]
        qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def load_record(rel):
    return json.load(open(os.path.join(R, rel), encoding="utf-8"))


def rows(path=JL):
    last = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            last[d["nid"]] = d
    return last


def panel(ox, oy, d):
    """ox = left edge px, oy = BOTTOM edge px of the container."""
    rec = load_record(d["record"])
    cores = (rec.get("hyp") or {}).get("cores", [])
    pins, hbox = [], None
    for c in cores:
        b = c.get("box") or {}
        if "th0" in b and abs(float(b["th1"]) - float(b["th0"])) > 1e-9:
            hbox = b
            continue
        try:
            pins.append((float(Fr(str(c["kx"]))), float(Fr(str(c["ky"])))))
        except Exception:                                        # noqa: BLE001
            pass
    if hbox is None:
        hh = (d.get("H_hull_base") or {}).get("H")
        if hh:
            hbox = dict(x0=hh[0], x1=hh[1], y0=hh[2], y1=hh[3], th0=hh[4], th1=hh[5])
    kill = d.get("kill_cell")
    tab = None
    for t in (d.get("subcases") or []):
        if isinstance(t, dict) and t.get("cell") == kill:
            tab = t
    item = None
    for f in (d.get("forced") or []):
        if f.get("cell") == kill:
            item = f

    def X(u):
        return ox + u * S

    def Y(v):
        return oy - v * S

    out = []
    out.append(text(ox, oy - S0 * S - 72,
                    "%s  (%s)  --  DEAD at %s" % (d["nid"], d.get("cls"), kill or "the base node"),
                    13, "#b71c1c", True))
    out.append(text(ox, oy - S0 * S - 56,
                    "Theorem FC: two DISTINCT non-pin squares must meet the widened open slot box "
                    "B+ (orange).  The library proves there is no such pair.", 9.5, "#333"))
    if tab:
        hm = [x for x in tab["subcases"] if x.get("case") == "H-meets"]
        tf = [x for x in tab["subcases"] if x.get("case") == "two-free"]
        hm, tf = (hm[0] if hm else {}), (tf[0] if tf else {})
        out.append(text(ox, oy - S0 * S - 42,
                        "(H-meets) H + one free square: %s ordered Lemma A1 cell pairs, %s alive.   "
                        "(two-free) two free squares: %s cell pairs, %s alive.   %s s"
                        % (hm.get("n_pairs", hm.get("dead", "-")), hm.get("n_alive", 0),
                           tf.get("n_pairs", tf.get("dead", "-")), tf.get("n_alive", 0),
                           tab.get("seconds")), 9.5, "#333"))
    out.append(text(ox, oy - S0 * S - 28,
                    "nsub %s / refine %s on the pair nodes (A178 ran 4 / 2); Lemma A1 grid side %s "
                    "< 1/sqrt2; caps %s cells / %s pairs"
                    % (d.get("nsub"), d.get("refine"), d.get("side"), d.get("max_cells"),
                       d.get("max_pairs")), 9.5, "#666"))
    # container + corner cells
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
               'stroke-width="2"/>' % (ox, oy - S0 * S, S0 * S, S0 * S))
    for (x0, y0) in ((0, 0), (S0 - 1, 0), (0, S0 - 1), (S0 - 1, S0 - 1)):
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#ccc" '
                   'stroke-width="1" stroke-dasharray="4,3"/>' % (X(x0), Y(y0 + 1), S, S))
    # the widened slot box and its meeter window
    if item:
        wx0, wx1, wy0, wy1 = item["wbox"]
        mx0, mx1, my0, my1 = item["window"]
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ff9800" '
                   'fill-opacity="0.30" stroke="#e65100" stroke-width="2"/>'
                   % (X(wx0), Y(wy1), (wx1 - wx0) * S, (wy1 - wy0) * S))
        out.append(text(X(0.5 * (wx0 + wx1)), Y(0.5 * (wy0 + wy1)) + 4, "B+", 11, "#e65100", True,
                        "middle"))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#e65100"'
                   ' stroke-width="1" stroke-dasharray="6,4"/>'
                   % (X(mx0), Y(my1), (mx1 - mx0) * S, (my1 - my0) * S))
        out.append(text(X(mx0) + 3, Y(my1) - 4, "meeter window of %s" % kill, 8, "#e65100"))
    # the pins
    for (cx, cy) in pins:
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in sq(cx, cy, 0.0))
        out.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" '
                   'stroke-width="1.5"/>' % pts)
    # the two meeters' admissible regions, HATCHED EMPTY
    if tab and tab.get("hull_B"):
        hb = tab["hull_B"]
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#hatch)" '
                   'stroke="#6a1b9a" stroke-width="1.6"/>'
                   % (X(hb[0]), Y(hb[3]), (hb[1] - hb[0]) * S, (hb[3] - hb[2]) * S))
        out.append(text(X(hb[0]) + 3, Y(hb[2]) - 4,
                        "hull of a free meeter's centre after the one-free clip "
                        "(%.3f x %.3f) -- every Lemma A1 cell pair inside is EmptyBox"
                        % (hb[1] - hb[0], hb[3] - hb[2]), 8, "#6a1b9a"))
        # the grid lines actually used by the two-free split
        w, h = hb[1] - hb[0], hb[3] - hb[2]
        nx = max(1, int(math.ceil(w / float(d.get("side") or 0.70) - 1e-12)))
        ny = max(1, int(math.ceil(h / float(d.get("side") or 0.70) - 1e-12)))
        for a in range(1, nx):
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a1b9a" '
                       'stroke-width="0.8" stroke-dasharray="3,3"/>'
                       % (X(hb[0] + w * a / nx), Y(hb[2]), X(hb[0] + w * a / nx), Y(hb[3])))
        for b in range(1, ny):
            out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a1b9a" '
                       'stroke-width="0.8" stroke-dasharray="3,3"/>'
                       % (X(hb[0]), Y(hb[2] + h * b / ny), X(hb[1]), Y(hb[2] + h * b / ny)))
    # the conditioned square
    if hbox:
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
                   'stroke-width="2"/>' % (X(hbox["x0"]), Y(hbox["y1"]),
                                           (hbox["x1"] - hbox["x0"]) * S,
                                           (hbox["y1"] - hbox["y0"]) * S))
        pin_rects = [(b["x1"] - 0.5, b["x0"] + 0.5, b["y1"] - 0.5, b["y0"] + 0.5)
                     for b in ((c.get("box") or {}) for c in cores)
                     if "x0" in b and abs(float(b.get("th1", 0)) - float(b.get("th0", 0))) < 1e-9]

        def rect_poly(r):
            return [(r[0], r[2]), (r[1], r[2]), (r[1], r[3]), (r[0], r[3])]

        def feasible(cx, cy, th):
            P = sq(cx, cy, th)
            if not all(0 <= x <= S0 and 0 <= y <= S0 for x, y in P):
                return False
            return all(sat(P, rect_poly(r)) >= -1e-12 for r in pin_rects)

        thm = 0.5 * (float(hbox.get("th0", 0)) + float(hbox.get("th1", 0)))
        th = math.radians(thm)
        best = None
        for i in range(49):
            for j in range(49):
                cx = hbox["x0"] + (hbox["x1"] - hbox["x0"]) * i / 48
                cy = hbox["y0"] + (hbox["y1"] - hbox["y0"]) * j / 48
                if feasible(cx, cy, th):
                    dd = math.hypot(cx - 0.5 * (hbox["x0"] + hbox["x1"]),
                                    cy - 0.5 * (hbox["y0"] + hbox["y1"]))
                    if best is None or dd < best[0]:
                        best = (dd, cx, cy)
        hx, hy = (best[1], best[2]) if best else (0.5 * (hbox["x0"] + hbox["x1"]),
                                                  0.5 * (hbox["y0"] + hbox["y1"]))
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in sq(hx, hy, th))
        out.append('<polygon points="%s" fill="#00e5ff" fill-opacity="0.35" stroke="#000" '
                   'stroke-width="2.5"/>' % pts)
        out.append(text(X(hx), Y(hy) + 4, "H", 12, "#000", True, "middle"))
        out.append(text(X(hx), Y(hy) + 17, "%.1f deg" % thm, 8, "#000", False, "middle"))
    # what it IS
    note = d.get("leaf") or ""
    lines = ["WHAT THIS IS: the page's own hypothesis (5 slack pins + the conditioned square H, "
             "budget %s) forces two distinct" % d.get("budget"),
             "non-pin squares to meet B+ at %s (Theorem FC; the extension class %s is FULL on "
             "[191/50, s0])." % (kill, (item or {}).get("extension")),
             "H sits IN FRONT of the cell: with H as one meeter no free square can be the second, "
             "and two free squares cannot both",
             "reach B+ either -- every Lemma A1 cell pair is EmptyBox under the A171 multibox clip. "
             "So the page is DEAD.",
             "[C: library geometry -- the frozen verifier is not involved.]  leaf: " + note]
    for i, ln in enumerate(lines):
        out.append(text(ox, oy + 20 + 14 * i, ln, 9, "#333"))
    return out


def alive_panel(ox, oy, d, wit_file=None):
    """the SURVIVING pair configuration of an ALIVE page: a real pair of admissible poses when the
    sampler (or a hand witness) found one, else the open residue."""
    rec = load_record(d["record"])
    cores = (rec.get("hyp") or {}).get("cores", [])
    pins = []
    hbox = None
    for c in cores:
        b = c.get("box") or {}
        if "th0" in b and abs(float(b["th1"]) - float(b["th0"])) > 1e-9:
            hbox = b
            continue
        try:
            pins.append((float(Fr(str(c["kx"]))), float(Fr(str(c["ky"]))))) 
        except Exception:                                        # noqa: BLE001
            pass
    wit, cell, item = None, None, None
    if wit_file and os.path.exists(wit_file):
        w = json.load(open(wit_file, encoding="utf-8"))
        wit, cell = w["poses_xytheta_deg"], w["cell"]
        item = dict(cell=cell, wbox=w["widened_box"], extension=w.get("extension"))
        note = w.get("note", "")
        gap = w.get("min_pairwise_sat_gap")
    else:
        note, gap = "", None
        for t in (d.get("subcases") or []):
            if t.get("witness"):
                wit = t["witness"]["poses"]
                cell = t["cell"]
                break
        if cell:
            for f in (d.get("forced") or []):
                if f.get("cell") == cell:
                    item = f

    def X(u):
        return ox + u * S

    def Y(v):
        return oy - v * S

    out = [text(ox, oy - S0 * S - 72, "%s  (%s)  --  ALIVE: %s IS doubly met"
                % (d["nid"], d.get("cls"), cell or "no cell decided"), 13, "#1b5e20", True),
           text(ox, oy - S0 * S - 56,
                "A real pair of admissible poses, drawn.  Every square is a closed unit square, all "
                "pairs interior-disjoint%s." % ("" if gap is None else
                                                " (min separating-axis gap %+.6f)" % gap), 9.5, "#333")]
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
               'stroke-width="2"/>' % (ox, oy - S0 * S, S0 * S, S0 * S))
    for (x0, y0) in ((0, 0), (S0 - 1, 0), (0, S0 - 1), (S0 - 1, S0 - 1)):
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" fill="none" stroke="#ccc" '
                   'stroke-width="1" stroke-dasharray="4,3"/>' % (X(x0), Y(y0 + 1), S, S))
    if item:
        wx0, wx1, wy0, wy1 = item["wbox"]
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ff9800" '
                   'fill-opacity="0.30" stroke="#e65100" stroke-width="2"/>'
                   % (X(wx0), Y(wy1), (wx1 - wx0) * S, (wy1 - wy0) * S))
        out.append(text(X(0.5 * (wx0 + wx1)), Y(0.5 * (wy0 + wy1)) + 4, "B+", 11, "#e65100", True,
                        "middle"))
    for (cx, cy) in pins:
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in sq(cx, cy, 0.0))
        out.append('<polygon points="%s" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" '
                   'stroke-width="1.5"/>' % pts)
    if hbox:
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" '
                   'stroke-width="1.5" stroke-dasharray="4,3"/>'
                   % (X(hbox["x0"]), Y(hbox["y1"]), (hbox["x1"] - hbox["x0"]) * S,
                      (hbox["y1"] - hbox["y0"]) * S))
    for k, v in sorted((wit or {}).items()):
        if k.startswith("P"):
            continue
        col = "#00e5ff" if k.startswith("H") else "#a5d6a7"
        edge = "#000" if k.startswith("H") else "#2e7d32"
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y))
                       for x, y in sq(v[0], v[1], math.radians(v[2])))
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.45" stroke="%s" '
                   'stroke-width="2.5"/>' % (pts, col, edge))
        out.append(text(X(v[0]), Y(v[1]) + 4, k, 11, edge, True, "middle"))
        out.append(text(X(v[0]), Y(v[1]) + 16, "(%.3f, %.3f, %.2f deg)" % (v[0], v[1], v[2]), 7.5,
                        edge, False, "middle"))
    lines = ["WHAT THIS IS: the two meeters Theorem FC demands at %s, EXHIBITED." % (cell or "-"),
             "So the cell is not the contradiction it was read as -- the page survives the pair test."]
    for chunk in [note[i:i + 118] for i in range(0, len(note), 118)][:5]:
        lines.append(chunk)
    for i, ln in enumerate(lines):
        out.append(text(ox, oy + 20 + 14 * i, ln, 9, "#333"))
    return out


def main():
    last = rows()
    dead = [k for k, v in sorted(last.items()) if v.get("verdict") == "DEAD"]
    alive_w = [k for k, v in sorted(last.items())
               if v.get("verdict") == "ALIVE"
               and any((t or {}).get("witness") for t in (v.get("subcases") or []))]
    WITF = os.path.join(R, "attempts", "A197-slot-pair-pass", "results",
                        "witness_Y0054_BL10.json")
    hand = ["k5_16_interior_Y0054"] if os.path.exists(WITF) else []
    ids = sys.argv[1:] or (dead + [i for i in hand if i in last]
                           + [i for i in alive_w if i not in hand][:max(0, 3 - len(dead))])
    ids = [i for i in ids if i in last]
    if not ids:
        print("no rows to draw in", JL)
    ncol = min(3, max(1, len(ids)))
    nrow = max(1, (len(ids) + ncol - 1) // ncol)
    PW = int(S0 * S + 60)
    PH = int(S0 * S + PAD_T + PAD_B)
    body = []
    for k, nid in enumerate(ids):
        r, c = divmod(k, ncol)
        d = last[nid]
        ox, oy = PAD_L + c * PW, PAD_T + r * PH + S0 * S
        if d.get("verdict") == "DEAD":
            body += panel(ox, oy, d)
        else:
            wf = os.path.join(R, "attempts", "A197-slot-pair-pass", "results",
                              "witness_Y0054_BL10.json")
            body += alive_panel(ox, oy, d, wf if nid == "k5_16_interior_Y0054" else None)
        print("panel", nid, d.get("verdict"), d.get("kill_cell"), d.get("leaf"))
    W = ncol * PW + 2 * PAD_L
    H = nrow * PH + 40
    head = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, H),
            '<defs><pattern id="hatch" width="7" height="7" patternTransform="rotate(45)" '
            'patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#f3e5f5"/>'
            '<line x1="0" y1="0" x2="0" y2="7" stroke="#8e24aa" stroke-width="1.6"/>'
            '</pattern></defs>',
            text(PAD_L, 30, "A197 -- forced-cell PAIR test: %d page(s) retired, %d drawn"
                 % (len(dead), len(ids)), 17, "#111", True),
            text(PAD_L, 50, "docs/proofs/forced_corners.md Theorem FC + Corollaries FC-slot / "
                            "FC-count; sideband.md Lemma A1; A171 multibox at nsub 8 / refine 4.  "
                            "Hatched = an admissible region the clip empties.", 10, "#555")]
    doc = head + body + ["</svg>"]
    out = os.path.join(HERE, "slotpair197.svg")
    open(out, "w", encoding="utf-8").write("\n".join(doc))
    print("wrote", out, W, H)
    import xml.dom.minidom
    xml.dom.minidom.parse(out)
    print("xml ok")


if __name__ == "__main__":
    main()
