"""A198 -- the step page of a fastprop run, in the drawing rules of docs/residue_map/gen_a57_lp.py: hypothesis squares
only at ADMISSIBLE poses (a sampled pose of the surviving pieces, clear of every pin square and inside the
container; dashed at the box centre if none is found), the slot cells coloured by viability, H's pulled-down box,
the joint-count table and the times printed.  A REALISED configuration (every square of the witness cover sampled
interior-disjoint from every other and from the pins, each meeting its claimed slots) is drawn when the sampler
finds one; otherwise the witness placements are drawn as their hulls."""
import math
import os
import time

import numpy as np

import fastprop as FP

S0 = float(FP.S_RAT)


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=10, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def sat(p, q):
    """separating-axis gap of two convex quads (>= 0: interiors disjoint)."""
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


def rect_poly(r):
    return [(r[0], r[2]), (r[1], r[2]), (r[1], r[3]), (r[0], r[3])]


def meets_open_box(P, wb):
    """the square's interior meets the open box iff their SAT gap is < 0 (both convex)."""
    return sat(P, rect_poly([float(v) for v in wb])) < -1e-9


def in_container(P):
    return all(-1e-9 <= x <= S0 + 1e-9 and -1e-9 <= y <= S0 + 1e-9 for x, y in P)


def sample_pose(pcs, rng):
    wts = np.array([float(FP.MB.rect_area(r) * (b.t1 - b.t0)) for (b, r) in pcs])
    if wts.sum() <= 0:
        return None
    k = rng.choice(len(pcs), p=wts / wts.sum())
    bn, r = pcs[k]
    cx = rng.uniform(float(r[0]), float(r[1]))
    cy = rng.uniform(float(r[2]), float(r[3]))
    t = rng.uniform(float(bn.t0), float(bn.t1))
    return cx, cy, 2.0 * math.atan(t)


def admissible_pose(pcs, pin_polys, rng, tries=400, wbs=()):
    """a sampled pose of the pieces clear of every pin square and inside the container (and meeting the open boxes
    `wbs` when given); None if not found."""
    for _ in range(tries):
        z = sample_pose(pcs, rng)
        if z is None:
            return None
        P = sq(*z)
        if not in_container(P):
            continue
        if any(sat(P, Q) < 0 for Q in pin_polys):
            continue
        if any(not meets_open_box(P, wb) for wb in wbs):
            continue
        return z
    return None


def realise(page, witness, pin_polys, rng, tries=400):
    """try to sample one pose per witness placement, pairwise interior-disjoint, each meeting its claimed slots."""
    plans = []
    for who, (ci, S, _ch, _h) in witness:
        if who == "free":
            pcs = page.reach(ci, S)[1] if S else page.reach(ci, frozenset())[1]
        else:
            pcs = page.role_pieces_in_cell(who, S, ci)
        wbs = [page.item[p]["wb"] for p in S]
        plans.append((who, S, pcs, wbs))
    for _ in range(tries):
        poses = []
        ok = True
        for who, S, pcs, wbs in plans:
            z = admissible_pose(pcs, pin_polys + [sq(*q) for q in poses], rng, tries=40, wbs=wbs)
            if z is None:
                ok = False
                break
            poses.append(z)
        if ok:
            return [(pl[0], pl[1], z) for pl, z in zip(plans, poses)]
    return None


COL = {"H": "#000", "F": "#6a1b9a"}
SLOTCOL = ["#e65100", "#2e7d32", "#1565c0", "#ad1457", "#00838f", "#5d4037", "#827717", "#4527a0"]


def draw(page, out, path, seed=198):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    S = 150
    PW = int(S0 * S) + 40
    pins = [(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3])) for k, b in page.pins.items()]
    pin_polys = [sq(cx, cy, 0.0) for cx, cy in pins]
    body = []
    ox, oy = 30, 70 + S0 * S

    def X(x):
        return ox + x * S

    def Y(y):
        return oy - y * S

    def poly(P, fill, op, stroke, w=1.0, dash=""):
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in P)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (pts, fill, op, stroke, w, d)

    verdict = out["verdict"]
    body.append(text(ox, 24, "%s (%s): FASTPROP %s in %.0f s -- %s" % (page.name, page.cls, verdict, out["seconds"], out.get("leaf") or "the joint count is feasible"), 13, bold=True))
    body.append(text(ox, 40, "pins blue; H black box + example square at an ADMISSIBLE sampled pose (dashed at the box centre if none found); forced slots' widened boxes orange; "
                     "grid cells of side %.3f < 1/sqrt2 (Lemma A1: one centre per cell); cell shading = per-slot alive volume; instantiated meeters purple" % float(page.side), 8.5, "#444"))
    body.append(text(ox, 52, "steps: " + "; ".join("%s %.1fs" % (st["step"] + ("[%s]" % st.get("label") if st.get("label") else ""), st["seconds"]) for st in out["steps"]), 8.5, "#444"))
    # container
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (X(0), Y(S0), S0 * S, S0 * S))
    # grid cells with the max alive fraction over slots (last round)
    rd = page.rounds[-1] if page.rounds else {}
    single = rd.get("single") or {}
    cell_max = {}
    for p, v in single.items():
        for ci, f in v.items():
            ci = int(ci)
            cell_max[ci] = max(cell_max.get(ci, 0.0), f)
    for ci, c in enumerate(page.cells):
        r = [float(v) for v in c["rect"]]
        f = cell_max.get(ci, 0.0)
        fill = "#c8e6c9" if f > 0 else "#fff"
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%.2f" stroke="#bbb" stroke-width="0.6"/>' % (
            X(r[0]), Y(r[3]), (r[1] - r[0]) * S, (r[3] - r[2]) * S, fill, min(0.9, 0.15 + f) if f > 0 else 0.0))
        body.append(text(X(r[0]) + 2, Y(r[3]) + 9, "%d" % ci, 7, "#999"))
    # slots
    for k, it in enumerate(page.items):
        wb = [float(v) for v in it["wb"]]
        col = SLOTCOL[k % len(SLOTCOL)]
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.5" stroke-dasharray="6,3"/>' % (
            X(wb[0]), Y(wb[3]), (wb[1] - wb[0]) * S, (wb[3] - wb[2]) * S, col, col))
        body.append(text(X(0.5 * (wb[0] + wb[1])), Y(0.5 * (wb[2] + wb[3])) + 4, it["cell"], 9, col, True, "middle"))
    # pins
    for (cx, cy) in pins:
        body.append(poly(sq(cx, cy, 0.0), "#90caf9", 0.6, "#1565c0", 1.5))
    # H and the instantiated roles: box + admissible example
    for role, b in page.roles.items():
        if role.startswith("P"):
            continue
        col = COL["H"] if role.startswith("H") else COL["F"]
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="2"/>' % (
            X(b[0]), Y(b[3]), max(0.5, (b[1] - b[0]) * S), max(0.5, (b[3] - b[2]) * S), col))
        pcs = page.nd.boxes[role].pieces if page.nd is not None and role in page.nd.boxes else []
        z = admissible_pose(pcs, pin_polys, rng) if pcs else None
        if z is None:
            z = (0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), math.radians(0.5 * (b[4] + b[5])))
            body.append(poly(sq(*z), "#00e5ff", 0.15, col, 2.0, "5,4"))
            body.append(text(X(z[0]), Y(z[1]) + 4, role + " (no admissible pose found)", 8, col, True, "middle"))
        else:
            body.append(poly(sq(*z), "#00e5ff", 0.35, col, 2.5))
            body.append(text(X(z[0]), Y(z[1]) + 4, role, 11, col, True, "middle"))
            body.append(text(X(z[0]), Y(z[1]) + 15, "%.1f deg" % math.degrees(z[2]), 8, col, False, "middle"))
    for hn in page.hnames:
        b0 = page.base[hn]
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="0.8" stroke-dasharray="3,2"/>' % (
            X(b0[0]), Y(b0[3]), (b0[1] - b0[0]) * S, (b0[3] - b0[2]) * S))
    # the witness cover: realised if possible
    wit = getattr(page, "witness", None) or []
    real = realise(page, wit, pin_polys, rng) if wit else None
    if real:
        Ps = [sq(*z) for _, _, z in real]
        worst = min([sat(Ps[i], Ps[j]) for i in range(len(Ps)) for j in range(i + 1, len(Ps))] + [9])
        for (who, Sset, z), P in zip(real, Ps):
            body.append(poly(P, "#ff8f00", 0.30, "#e65100", 1.8))
            body.append(text(X(z[0]), Y(z[1]) - 8, "%s -> %s" % (who, "+".join(sorted(Sset))), 7.5, "#bf360c", True, "middle"))
        body.append(text(ox, oy + 16, "REALISED witness cover (sampled): %d squares pairwise interior-disjoint (min SAT gap %+.4f), clear of the pins, each meeting its claimed open slot boxes" % (len(real), worst), 9, "#bf360c", True))
    elif wit:
        for who, (ci, Sset, _ch, h) in wit:
            hh = [float(v) for v in h]
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ff8f00" fill-opacity="0.25" stroke="#e65100" stroke-width="1.2" stroke-dasharray="4,2"/>' % (
                X(hh[0]), Y(hh[3]), max(1, (hh[1] - hh[0]) * S), max(1, (hh[3] - hh[2]) * S)))
            body.append(text(X(0.5 * (hh[0] + hh[1])), Y(0.5 * (hh[2] + hh[3])) - 4, "%s@%d -> %s" % (who, ci, "+".join(sorted(Sset))), 7, "#bf360c", True, "middle"))
        body.append(text(ox, oy + 16, "witness cover (hulls of the placements' surviving pieces; the sampler found NO realised configuration in 400 tries)", 9, "#bf360c", True))
    # per-slot small panels
    px0 = ox + S0 * S + 40
    ss = 62
    for k, it in enumerate(page.items):
        cx0 = px0 + (k % 3) * (S0 * ss + 18)
        cy0 = 90 + (k // 3) * (S0 * ss + 40) + S0 * ss
        col = SLOTCOL[k % len(SLOTCOL)]
        body.append(text(cx0, cy0 - S0 * ss - 6, "%s: %d alive cells; H %s" % (it["cell"], len(single.get(it["cell"], {})),
                                                                                "reaches" if it["cell"] in (rd.get("H_reach") or []) else "MISSES"), 8.5, col, True))
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="1"/>' % (cx0, cy0 - S0 * ss, S0 * ss, S0 * ss))
        for ci, c in enumerate(page.cells):
            r = [float(v) for v in c["rect"]]
            f = single.get(it["cell"], {}).get(str(ci), single.get(it["cell"], {}).get(ci, 0.0))
            if f > 0:
                body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%.2f" stroke="none"/>' % (
                    cx0 + r[0] * ss, cy0 - r[3] * ss, (r[1] - r[0]) * ss, (r[3] - r[2]) * ss, col, min(0.95, 0.2 + f)))
        wb = [float(v) for v in it["wb"]]
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="4,2"/>' % (
            cx0 + wb[0] * ss, cy0 - wb[3] * ss, (wb[1] - wb[0]) * ss, (wb[3] - wb[2]) * ss, col))
        for (cx, cy) in pins:
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#90caf9" fill-opacity="0.5" stroke="#1565c0" stroke-width="0.8"/>' % (
                cx0 + (cx - 0.5) * ss, cy0 - (cy + 0.5) * ss, ss, ss))
        for hn in page.hnames:
            b = page.roles[hn]
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="1.2"/>' % (
                cx0 + b[0] * ss, cy0 - b[3] * ss, max(0.5, (b[1] - b[0]) * ss), max(0.5, (b[3] - b[2]) * ss)))
    # the joint-count table
    ty = 90 + 2 * (S0 * ss + 40) + 10
    body.append(text(px0, ty, "JOINT COUNT (round %d): %d forced slots x 2 distinct non-pin meeters = %d incidences; H + %d free squares; A1 cells; chord rows on %d lines" % (
        rd.get("round", 0), len(page.slots), 2 * len(page.slots), page.n_free, len(page.lines)), 9, "#222", True))
    ty += 13
    body.append(text(px0, ty, "%s options (cell -> slots met jointly): " % page.H + "; ".join("%d -> %s" % (ci, "+".join(Sl) if Sl else "none") for ci, Sl in (rd.get("fixed") or {}).get(page.H, [])[:12]), 8, "#222"))
    ty += 12
    bycell = {}
    for ci, Sl, h in rd.get("free_opts", []):
        bycell.setdefault(ci, []).append(Sl)
    for ci in sorted(bycell):
        maxs = [Sl for Sl in bycell[ci] if not any(set(Sl) < set(T) for T in bycell[ci])]
        body.append(text(px0, ty, "cell %2d: %s" % (ci, " | ".join("+".join(Sl) for Sl in maxs)), 7.5, "#333"))
        ty += 10
    ty += 4
    for r_ in page.rounds:
        body.append(text(px0, ty, "round %d: count %s / with chords %s; H forced at %s; instantiate %s%s" % (
            r_["round"], (r_.get("count_nochord") or {}).get("feasible"), (r_.get("count_chord") or {}).get("feasible"),
            r_.get("forced_H"), r_.get("instantiate"), ("; DEAD: " + r_["dead"]) if r_.get("dead") else ""), 8, "#222"))
        ty += 11
    if out.get("pair_test"):
        pr = out["pair_test"]
        body.append(text(px0, ty, "pair test (geo178b, nsub 8 / refine 4) on %s: %s in %.0f s" % (pr["slot"], "ALIVE" if pr["alive"] else "DEAD", pr["seconds"]), 8, "#222"))
        ty += 11
    body.append(text(px0, ty, "exact tests recorded: %d; figure %.1f s" % (out.get("n_tests", 0), time.time() - t0), 8, "#666"))
    W = int(px0 + 3 * (S0 * ss + 18) + 20)
    Hh = int(max(oy + 40, ty + 20))
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, Hh)] + body + ["</svg>"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(path)
    return dict(realised=bool(real), path=path)
