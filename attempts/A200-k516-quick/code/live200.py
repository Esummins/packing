"""A200 -- the page AFTER THE FAST STEPS, drawn from the certificates (q200_<nid>[_pad0|_deep].json) while the run goes on.
quick200.py emits a certificate right after each pad's propagation (normalise / options / union / count), BEFORE the
slow leaves (SEAL, pair test), so a certificate is exactly "what the fast steps got the page to"; when a slow leaf
has run, its step is listed too.  One file per page (docs/residue_map/quick200_fast_<nid>.svg, one panel per pad)
plus a contact sheet (quick200_fast_gallery.svg).  Drawing rules: pins blue (stock boxes); H black = the clipped
box (record box dashed) with its hypothesis square at the box centre and mid-tilt (thin; NO extremal outlines,
admissibility is not re-checked here); instantiated meeters purple; slot units dashed in the slot colour; cells
GREY STIPPLE where some slot's meeter still has surviving centres (undecided), white where none does; the count
search's witness placement as thin dashed rects; every time is the run's own.  Read-only: nothing is recomputed.

    python live200.py            # one render
    python live200.py loop       # every 180 s until killed
"""
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.join(HERE, "..", "certs")
OUTD = os.path.join(ROOT, "docs", "residue_map")
S0 = 969271 / 250000
SLOTCOL = ["#e65100", "#2e7d32", "#1565c0", "#ad1457", "#00838f", "#5d4037", "#827717", "#4527a0"]
WBOX = {}      # slot unit boxes per page (from geo178.forced_items; cached)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=10, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def _sep(P, Q):
    """separating-axis test for two convex polygons (True = disjoint interiors)."""
    for poly_ in (P, Q):
        for i in range(len(poly_)):
            x0, y0 = poly_[i]; x1, y1 = poly_[(i + 1) % len(poly_)]
            nx, ny = y0 - y1, x1 - x0
            p0 = [nx * x + ny * y for x, y in P]; q0 = [nx * x + ny * y for x, y in Q]
            if max(p0) <= min(q0) + 1e-12 or max(q0) <= min(p0) + 1e-12:
                return True
    return False


def admissible(b, pins, tries=300, seed=0):
    """first pose in the box b (centre / mid-tilt first, then a fixed random sample) whose unit square lies inside the
    container and meets no pin's stock square; None if none is found.  Container + pins only (no other roles)."""
    import random
    rng = random.Random(seed)
    pinp = [sq(cx, cy, 0.0) for cx, cy in pins]
    cands = [(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), math.radians(0.5 * (b[4] + b[5])))]
    cands += [(b[0] + rng.random() * (b[1] - b[0]), b[2] + rng.random() * (b[3] - b[2]), math.radians(b[4] + rng.random() * (b[5] - b[4]))) for _ in range(tries)]
    for k, (cx, cy, th) in enumerate(cands):
        P = sq(cx, cy, th)
        if min(x for x, y in P) < -1e-9 or max(x for x, y in P) > S0 + 1e-9 or min(y for x, y in P) < -1e-9 or max(y for x, y in P) > S0 + 1e-9:
            continue
        if all(_sep(P, Q) for Q in pinp):
            return (cx, cy, th), ("box centre / mid-tilt" if k == 0 else "sampled admissible pose (container + pins only)")
    return None, None


def slot_boxes(nid):
    if nid in WBOX:
        return WBOX[nid]
    try:
        sys.path.insert(0, os.path.join(ROOT, "attempts", "A198-fastprop", "code"))
        sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
        import fastprop as FP                      # READ-ONLY
        rec, cls, row = FP.load_page(nid)
        WBOX[nid] = {it["cell"]: [float(v) for v in it["wbox"]] for it in FP.G.forced_items(cls, rec)}
        WBOX[nid]["_H"] = [float(v) for v in rec["H"][0]]
        WBOX[nid]["_pins"] = [(float(p["kx"]), float(p["ky"])) for p in rec["pins"]]
    except Exception as e:                         # the page still renders without the slot units
        WBOX[nid] = {}
        print("slot boxes unavailable for %s: %s" % (nid, e), flush=True)
    return WBOX[nid]


def cells_of(cert):
    cells = {}
    for t in cert.get("tests") or []:
        if "cell" in t and "rect" in t and t["cell"] not in cells:
            cells[int(t["cell"])] = [float(v) for v in t["rect"]]
    return cells


def panel(cert, body, ox, oy, S, small=False):
    """ox, oy = the top-left of the container in SVG pixels.  Returns the panel's bottom y."""
    nid = cert["nid"]
    X = lambda x: ox + x * S
    Y = lambda y: oy + (S0 - y) * S

    def rect(r, fill, op, stroke, w=1.0, dash="", extra=""):
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s%s/>' % (
            X(r[0]), Y(r[3]), max(0.6, (r[1] - r[0]) * S), max(0.6, (r[3] - r[2]) * S), fill, op, stroke, w,
            (' stroke-dasharray="%s"' % dash) if dash else "", extra)

    def poly(P, fill, op, stroke, w=1.0, dash=""):
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in P)
        return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (
            pts, fill, op, stroke, w, (' stroke-dasharray="%s"' % dash) if dash else "")

    rounds = cert.get("rounds") or []
    rd = rounds[-1] if rounds else {}
    single = rd.get("single") or {}
    cells = cells_of(cert)
    alive = {}
    for p, v in single.items():
        for ci, f in v.items():
            alive[int(ci)] = max(alive.get(int(ci), 0.0), float(f))
    body.append(rect((0, S0, 0, S0), "#fff", 1.0, "#000", 1.6))
    # cells: grey stipple where some slot still has surviving meeter centres, white otherwise
    for ci, r in sorted(cells.items()):
        f = alive.get(ci, 0.0)
        if f > 0:
            body.append(rect(r, "url(#stipple)", 1.0, "#bbb", 0.4))
            if not small:
                body.append(text(X(0.5 * (r[0] + r[1])), Y(0.5 * (r[2] + r[3])) + 3, "%d" % ci, 6.5, "#888", False, "middle"))
        else:
            body.append(rect(r, "#fff", 1.0, "#ddd", 0.4))
    slots = list(single.keys()) or list((cert.get("caps") or {}).keys())
    wb = slot_boxes(nid)
    urec = rd.get("union") or {}
    for k, p in enumerate(slots):
        col = SLOTCOL[k % len(SLOTCOL)]
        if p in wb:
            body.append(rect(wb[p], col, 0.06, col, 1.3, "6,3"))
            if not small:
                body.append(text(X(0.5 * (wb[p][0] + wb[p][1])), Y(wb[p][3]) + 9, p, 7.5, col, True, "middle"))
        u = urec.get(p) or {}
        bb = u.get("bbox")
        if bb:
            body.append(rect(bb, "none", 0, col, 0.9, "2,2"))
    # pins (stock boxes, blue), H (record dashed, clipped solid) and the instantiated meeters (purple)
    roles = cert.get("roles") or {}
    for name, b in roles.items():
        if name.startswith("P"):
            cx, cy = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3])
            body.append(poly(sq(cx, cy, 0.0), "#90caf9", 0.6, "#1565c0", 1.2))
    for name, b in roles.items():
        if name.startswith("P"):
            continue
        col = "#000" if name.startswith("H") else "#6a1b9a"
        if name.startswith("H") and wb.get("_H"):
            body.append(rect(wb["_H"], "none", 0, "#000", 0.8, "4,3"))         # the record's H box (before the clips)
        body.append(rect(b, "none", 0, col, 1.8 if not small else 1.0))
        z, how = admissible(b, wb.get("_pins") or [(0.5 * (v[0] + v[1]), 0.5 * (v[2] + v[3])) for n_, v in roles.items() if n_.startswith("P")])
        if z is None:
            cx, cy, th = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), math.radians(0.5 * (b[4] + b[5]))
            body.append(poly(sq(cx, cy, th), "none", 0, col, 0.8, "5,4"))
            how = "NO admissible pose found in the box (dashed: schematic)"
        else:
            cx, cy, th = z
            body.append(poly(sq(cx, cy, th), "#00e5ff", 0.18, col, 1.0 if not small else 0.6))
        if not small:
            body.append(text(X(cx), Y(cy) + 4, name, 10, col, True, "middle"))
            body.append(text(X(cx), Y(cy) + 14, "%.1f deg of %.1f-%.1f; %s" % (math.degrees(th), b[4], b[5], how), 6.5, col, False, "middle"))
    # the count search's witness placement (schematic: cells, not poses)
    for w in cert.get("witness") or []:
        try:
            name, ci, served, r = w[0], w[1], w[2], [float(v) for v in w[3]]
        except Exception:
            continue
        body.append(rect(r, "#ffe082", 0.35, "#8d6e00", 0.7, "3,2"))
        if not small:
            body.append(text(X(0.5 * (r[0] + r[1])), Y(0.5 * (r[2] + r[3])) + 3, "%s:%s" % (name, ",".join(s.split("(")[0] + s[s.find("("):] for s in served)) if served else name, 5.5, "#6d4c00", False, "middle"))
    return oy + S0 * S


def side_text(cert, body, x, y, w):
    steps = cert.get("steps") or []
    rounds = cert.get("rounds") or []
    rd = rounds[-1] if rounds else {}
    v = cert.get("verdict")
    col = "#c62828" if v == "DEAD" else "#2e7d32"
    lines = [("%s at pad %s: %s%s" % (cert["nid"], cert.get("pad"), v, ("  [killed at step: %s]" % cert["step_killed"]) if cert.get("step_killed") else ""), 11, col, True)]
    if cert.get("leaf"):
        s = str(cert["leaf"])
        while s:
            lines.append((s[:95], 8, col, False)); s = s[95:]
    fast = [st for st in steps if st["step"] not in ("seal", "pair", "noroom")]
    lines.append(("FAST STEPS %.0f s: %s   (whole run so far %.0f s, %d exact tests, %d round(s))" % (
        sum(float(st.get("seconds", 0)) for st in fast),
        " > ".join("%s %.0fs" % (st["step"] + (("[" + st.get("label", "") + "]") if st.get("label") else ""), st.get("seconds", 0)) for st in fast),
        float(cert.get("seconds") or 0), len(cert.get("tests") or []), len(rounds)), 8, "#333", False))
    slow = [st for st in steps if st["step"] in ("seal", "pair", "noroom")]
    if slow:
        lines.append(("slow leaves run so far: " + "; ".join("%s %s %s %.0fs" % (st["step"], st.get("corner", ""), st.get("verdict", ""), st.get("seconds", 0)) for st in slow), 8, "#333", False))
    else:
        lines.append(("slow leaves (SEAL / pair test): not yet run on this pad -- the picture is the fast steps only", 8, "#333", False))
    lines.append(("forced H at: %s;  instantiated meeters: %s;  role cells: %s" % (
        cert.get("forced_H") or "-", {k: v for k, v in (cert.get("role_slots") or {}).items()} or "-", cert.get("role_cells") or "-"), 8, "#333", False))
    caps = cert.get("caps") or {}
    single = rd.get("single") or {}
    urec = rd.get("union") or {}
    lines.append(("slot      alive cells   cap   union diam / l-inf / chord row   why", 8, "#000", True))
    for k, p in enumerate(single.keys() or caps.keys()):
        u = urec.get(p) or {}
        cap = caps.get(p)
        lines.append(("%-9s %3d           %-4s  %s / %s / %s   %s" % (
            p, len(single.get(p) or {}), "-" if cap in (None, 99) else cap,
            u.get("diam", "-"), u.get("linf", "-"), u.get("chord_row", "-"), str(u.get("why", ""))[:40]), 7.5, SLOTCOL[k % len(SLOTCOL)], False))
    cn, cc = rd.get("count_nochord") or {}, rd.get("count_chord") or {}
    if cn or cc:
        lines.append(("assignment count: no chords %s (%s nodes); with chords %s (%s nodes); free options %s; H fixed options %s" % (
            cn.get("feasible"), cn.get("nodes"), cc.get("feasible"), cc.get("nodes"), rd.get("n_free_opts"), (rd.get("fixed") or {}).get("H") and len(rd["fixed"]["H"])), 8, "#333", False))
    if cert.get("witness"):
        lines.append(("witness of the count (yellow cells): a cell per free square with the slots it would serve -- a counting witness, not a packing", 7.5, "#6d4c00", False))
    lines.append(("window pending: %s;  path: %s;  chain done: %s;  lam %s" % (cert.get("window_pending"), cert.get("path"), cert.get("chain_done"), cert.get("lam")), 7.5, "#555", False))
    yy = y
    for t, sz, c, b in lines:
        t = str(t)
        width = 120 if sz <= 8 else 90
        while True:
            body.append(text(x, yy, t[:width], sz, c, b))
            yy += sz + 4
            t = t[width:]
            if not t:
                break
    return yy


def load_certs():
    out = {}
    for f in sorted(glob.glob(os.path.join(CERTS, "q200_*.json"))):
        base = os.path.basename(f)[5:-5]
        nid = base.replace("_pad0", "").replace("_deep", "")
        try:
            c = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        c["_file"] = os.path.basename(f)
        c["_mtime"] = os.path.getmtime(f)
        out.setdefault(nid, []).append(c)
    return out


def defs():
    return ('<defs><pattern id="stipple" width="4" height="4" patternUnits="userSpaceOnUse">'
            '<rect width="4" height="4" fill="#f2f2f2"/><circle cx="1" cy="1" r="0.7" fill="#999"/><circle cx="3" cy="3" r="0.7" fill="#999"/></pattern></defs>')


def page_svg(nid, certs):
    S = 118
    PW = int(S0 * S) + 20
    TW = 560
    n = len(certs)
    W = n * (PW + TW) + 40
    body = []
    body.append(text(20, 22, "%s -- A200 quick chain: the page AFTER THE FAST STEPS (propagation: normalise / options / union / count), one panel per pad" % nid, 13, "#000", True))
    body.append(text(20, 38, "grey stipple = cells where some forced slot's meeter still has surviving centres (undecided); white = none; dashed colour = slot unit + its meeter-centre union box; "
                     "blue = pins; black = H's clipped box with the hypothesis square at the box centre / mid-tilt (thin, no extremal outlines); purple = instantiated meeters; yellow = the count's witness cells.", 8, "#444"))
    body.append(text(20, 50, "drawn from the run's certificates (read-only, nothing recomputed); rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 8, "#444"))
    y0 = 70
    ybot = y0
    for k, c in enumerate(certs):
        ox = 20 + k * (PW + TW)
        body.append(text(ox, y0 - 6, "PANEL %d: %s  (pad %s; %s)" % (k + 1, c["_file"], c.get("pad"), time.strftime("%H:%M:%S", time.localtime(c["_mtime"]))), 9, "#000", True))
        yb = panel(c, body, ox, y0, S)
        yt = side_text(c, body, ox + PW + 10, y0 + 12, TW)
        ybot = max(ybot, yb, yt)
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, ybot + 20), defs()] + body + ["</svg>"]
    return "\n".join(doc)


def gallery_svg(pages):
    S = 52
    PW = int(S0 * S) + 16
    PH = PW + 34
    ncol = 6
    keys = sorted(pages.keys())
    nrow = max(1, (len(keys) + ncol - 1) // ncol)
    body = [text(16, 20, "A200 quick chain over the k5_16 pages -- after the fast steps (one thumbnail per page: its latest certificate); rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 12, "#000", True),
            text(16, 34, "verdict colours: red DEAD, green ALIVE (fast steps only, slow leaves may still run); open quick200_fast_<page>.svg for the full panel and numbers", 8, "#444")]
    for k, nid in enumerate(keys):
        certs = sorted(pages[nid], key=lambda c: c["_mtime"])
        c = certs[-1]
        dead = [d for d in certs if d.get("verdict") == "DEAD"]
        if dead:
            c = dead[-1]
        ox, oy = 16 + (k % ncol) * PW, 50 + (k // ncol) * PH
        panel(c, body, ox, oy, S, small=True)
        v = c.get("verdict")
        col = "#c62828" if v == "DEAD" else "#2e7d32"
        body.append(text(ox, oy + S0 * S + 11, nid.replace("k5_16_interior_", ""), 8, "#000", True))
        body.append(text(ox, oy + S0 * S + 21, "%s pad %s %s %.0fs" % (v, c.get("pad"), c.get("step_killed") or ("fast only" if not any(st["step"] in ("seal", "pair") for st in c.get("steps") or []) else "leaves run"), float(c.get("seconds") or 0)), 7, col))
    W = ncol * PW + 32
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, 50 + nrow * PH), defs()] + body + ["</svg>"]
    return "\n".join(doc)


def render():
    pages = load_certs()
    os.makedirs(OUTD, exist_ok=True)
    n = 0
    for nid, certs in pages.items():
        certs.sort(key=lambda c: (0 if c["_file"].endswith("_pad0.json") else (2 if c["_file"].endswith("_deep.json") else 1)))
        certs.sort(key=lambda c: {"g1": 0, "window": 0, "zero": 1}.get(c.get("pad"), 2))
        p = os.path.join(OUTD, "quick200_fast_%s.svg" % nid)
        s = page_svg(nid, certs)
        old = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        import re
        strip = lambda t: re.sub(r"rendered [0-9: -]+", "", t)
        if strip(old) != strip(s):
            open(p, "w", encoding="utf-8").write(s)
            n += 1
    open(os.path.join(OUTD, "quick200_fast_gallery.svg"), "w", encoding="utf-8").write(gallery_svg(pages))
    import xml.dom.minidom
    xml.dom.minidom.parse(os.path.join(OUTD, "quick200_fast_gallery.svg"))
    return len(pages), n


if __name__ == "__main__":
    loop = len(sys.argv) > 1 and sys.argv[1] == "loop"
    while True:
        try:
            print(time.strftime("%H:%M:%S"), "pages, rewritten:", render(), flush=True)
        except Exception as e:
            print("render error", repr(e), flush=True)
        if not loop:
            break
        time.sleep(180)
