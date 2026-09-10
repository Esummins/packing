"""A200 -- the residue page of a SURVIVOR of the quick chain, in the drawing rules of docs/residue_map/gen_a57_lp.py
(A198's fig198 helpers, READ-ONLY import): hypothesis squares only at ADMISSIBLE sampled poses (dashed at the box
centre if none is found), the forced-slot cells coloured by viability, H's CLIPPED box (the record box dashed), the
instantiated meeters, the per-slot union statistics (CN diameter / l-inf / chord row) and caps, the propagation
table and the times.  One panel per pad (window pad; pad 0 if it was run), each with a note saying what it IS."""
import math
import os
import time

import numpy as np

import fastprop as FP                      # noqa  READ-ONLY (A198)
import fig198 as F8                        # noqa  READ-ONLY (A198)

S0 = float(FP.S_RAT)
text, sq, sat, poly_rect = F8.text, F8.sq, F8.sat, F8.rect_poly
SLOTCOL = F8.SLOTCOL


def panel(page, out, body, ox, oy, S, rng, title):
    pins = [(0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3])) for k, b in page.pins.items()]
    pin_polys = [sq(cx, cy, 0.0) for cx, cy in pins]

    def X(x):
        return ox + x * S

    def Y(y):
        return oy - y * S

    def poly(P, fill, op, stroke, w=1.0, dash=""):
        pts = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in P)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (pts, fill, op, stroke, w, d)

    body.append(text(ox, oy - S0 * S - 8, title, 11, bold=True))
    body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (X(0), Y(S0), S0 * S, S0 * S))
    rd = page.rounds[-1] if page.rounds else {}
    single = rd.get("single") or {}
    cell_max = {}
    for p, v in single.items():
        for ci, f in v.items():
            cell_max[int(ci)] = max(cell_max.get(int(ci), 0.0), f)
    for ci, c in enumerate(page.cells):
        r = [float(v) for v in c["rect"]]
        f = cell_max.get(ci, 0.0)
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%.2f" stroke="#bbb" stroke-width="0.6"/>' % (
            X(r[0]), Y(r[3]), (r[1] - r[0]) * S, (r[3] - r[2]) * S, "#c8e6c9" if f > 0 else "#fff", min(0.9, 0.15 + f) if f > 0 else 0.0))
    # the per-slot union bounding boxes (where an anonymous meeter's centre can be) and the widened boxes
    urec = rd.get("union") or {}
    for k, it in enumerate(page.items):
        wb = [float(v) for v in it["wb"]]
        col = SLOTCOL[k % len(SLOTCOL)]
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10" stroke="%s" stroke-width="1.5" stroke-dasharray="6,3"/>' % (
            X(wb[0]), Y(wb[3]), (wb[1] - wb[0]) * S, (wb[3] - wb[2]) * S, col, col))
        u = urec.get(it["cell"]) or {}
        cap = u.get("cap")
        lab = "%s cap %s" % (it["cell"], "-" if cap in (None, 99) else cap)
        body.append(text(X(0.5 * (wb[0] + wb[1])), Y(0.5 * (wb[2] + wb[3])) + 4, lab, 8.5, col, True, "middle"))
        bb = u.get("bbox")
        if bb:
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="1.0" stroke-dasharray="2,2"/>' % (
                X(bb[0]), Y(bb[3]), max(1, (bb[1] - bb[0]) * S), max(1, (bb[3] - bb[2]) * S), col))
    for (cx, cy) in pins:
        body.append(poly(sq(cx, cy, 0.0), "#90caf9", 0.6, "#1565c0", 1.5))
    for role, b in page.roles.items():
        if role.startswith("P"):
            continue
        col = "#000" if role.startswith("H") else "#6a1b9a"
        body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="2"/>' % (
            X(b[0]), Y(b[3]), max(0.5, (b[1] - b[0]) * S), max(0.5, (b[3] - b[2]) * S), col))
        pcs = page.nd.boxes[role].pieces if page.nd is not None and role in page.nd.boxes else []
        z = F8.admissible_pose(pcs, pin_polys, rng) if pcs else None
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
    wit = getattr(page, "witness", None) or []
    real = F8.realise(page, wit, pin_polys, rng) if wit else None
    if real:
        Ps = [sq(*z) for _, _, z in real]
        worst = min([sat(Ps[i], Ps[j]) for i in range(len(Ps)) for j in range(i + 1, len(Ps))] + [9])
        for (who, Sset, z), P in zip(real, Ps):
            body.append(poly(P, "#ff8f00", 0.30, "#e65100", 1.8))
            body.append(text(X(z[0]), Y(z[1]) - 8, "%s -> %s" % (who, "+".join(sorted(Sset))), 7.5, "#bf360c", True, "middle"))
        note = "REALISED count witness (sampled): %d squares pairwise interior-disjoint (min SAT gap %+.4f), clear of the pins, each meeting its claimed open slot boxes" % (len(real), worst)
    elif wit:
        for who, (ci, Sset, _ch, h) in wit:
            hh = [float(v) for v in h]
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ff8f00" fill-opacity="0.25" stroke="#e65100" stroke-width="1.2" stroke-dasharray="4,2"/>' % (
                X(hh[0]), Y(hh[3]), max(1, (hh[1] - hh[0]) * S), max(1, (hh[3] - hh[2]) * S)))
            body.append(text(X(0.5 * (hh[0] + hh[1])), Y(0.5 * (hh[2] + hh[3])) - 4, "%s@%d -> %s" % (who, ci, "+".join(sorted(Sset))), 7, "#bf360c", True, "middle"))
        note = "count witness as HULLS of the placements' pieces (no realised configuration found in 400 tries -- the count is a bound, not a packing)"
    else:
        note = "no count witness recorded"
    body.append(text(ox, oy + 14, note, 8.5, "#bf360c", True))
    body.append(text(ox, oy + 26, "WHAT THIS IS: the page's node {pins (blue), H (black: record box dashed, CLIPPED box solid), instantiated meeters (purple)} at the %s; "
                     "green cells = where an anonymous free meeter of some slot can still have its centre (Lemma A1 grid, side %.3f); "
                     "dotted boxes = the per-slot union of survivors (CN / A1-U / chord row read off it); 'cap' = the anonymous-meeter bound." % (
                         {"window": "WINDOW pad (lambda_max = s0/3.82: valid on [3.82, s0])", "g1": "G1 pad (lambda = s0/3.861637: the page's own window (3.861637, s0])", "zero": "PAD 0 (lambda = 1: a statement at s0 only)"}.get(out.get("pad"), out.get("pad")), float(page.side)), 7.5, "#444"))
    # the propagation table
    ty = oy + 40
    body.append(text(ox, ty, "propagation (%s pad): %s in %.0f s; %d exact tests" % (out.get("pad"), out["verdict"], out["seconds"], out.get("n_tests", 0)), 9, "#222", True))
    ty += 12
    for r_ in page.rounds:
        body.append(text(ox, ty, "round %d: caps %s; H reaches %s; H forced %s; roles forced %s; instantiate %s; count %s / chords %s%s" % (
            r_["round"], r_.get("caps"), r_.get("H_reach"), r_.get("forced_H"), r_.get("forced_role"), r_.get("instantiate"),
            (r_.get("count_nochord") or {}).get("feasible"), (r_.get("count_chord") or {}).get("feasible"),
            ("; DEAD: " + r_["dead"]) if r_.get("dead") else ""), 7.5, "#222"))
        ty += 10
        for p, u in (r_.get("union") or {}).items():
            body.append(text(ox + 12, ty, "%-8s n %s  diam %s  linf %s  chord row %s on %s  -> cap %s (%s)" % (
                p, u.get("n_pieces"), u.get("diam"), u.get("linf"), u.get("chord_row"), u.get("chord_line"), "-" if u.get("cap") in (None, 99) else u.get("cap"), u.get("why")), 7, "#333"))
            ty += 9
    for st in out.get("steps", []):
        if st["step"] in ("seal", "noroom", "pair-test"):
            body.append(text(ox, ty, "%s: %s" % (st["step"], {k: v for k, v in st.items() if k not in ("step", "t")}), 7.5, "#222"))
            ty += 10
    body.append(text(ox, ty, "steps: " + "; ".join("%s%s %.1fs" % (st["step"], ("[%s]" % st.get("label")) if st.get("label") else "", st["seconds"]) for st in out.get("steps", [])), 7, "#666"))
    ty += 10
    if out.get("pair_test"):
        pr = out["pair_test"]
        body.append(text(ox, ty, "DEEP: pair tests (geo178b, nsub 8 / refine 4): %s; total %.0f s" % (
            "; ".join("%s (fixed %s) %s %.0fs" % (r["slot"], "+".join(r.get("fixed_roles") or []) or "-", "ALIVE" if r["alive"] else "DEAD", r["seconds"]) for r in pr.get("runs", [])) or "none run", pr.get("seconds", 0)), 8, "#222", True))
        ty += 10
    return ty


def draw(page, outs, path, seed=200):
    """`page` = the LAST QPage run (its rounds/roles are drawn); `outs` = the result dicts of the chain (window pad first)."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    S = 140
    W = int(S0 * S) + 60
    body = []
    body.append(text(30, 24, "%s (%s): A200 quick chain -- %s" % (page.name, page.cls, "; ".join("%s pad: %s%s" % (o.get("pad"), o["verdict"], (" (" + (o.get("leaf") or "")[:90] + ")") if o.get("leaf") else "") for o in outs)), 13, bold=True))
    body.append(text(30, 40, "drawing rules: hypothesis squares only at admissible sampled poses; pins blue; H black; instantiated meeters purple; forced slots' boxes dashed in colour; "
                     "cells shaded by the largest per-slot surviving volume fraction.  Every number is an exact-test result (A171 multibox / A161 / Lemma CN / A1 / open chords).", 8, "#444"))
    oy = 70 + S0 * S
    ty = panel(page, outs[-1], body, 30, oy, S, rng, "PANEL: the node after the quick chain at the %s pad" % outs[-1].get("pad"))
    Hh = int(ty + 30)
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (max(W, 1250), Hh)] + body + ["</svg>"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(path)
    return dict(path=path, seconds=round(time.time() - t0, 1))
