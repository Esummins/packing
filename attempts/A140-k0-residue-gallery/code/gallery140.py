"""A140 T2 -- the k0 residue gallery, v3: one two-panel page per converged-alive k0_00 cell.

Format: the reviewed A107 two-panel form (docs/shadows/K*.svg, docs/shadows.md Part II) with the
drawing rules of 2026-09-07 (docs/residue_map/gen_a57_lp.py `0fbbc165`), plus the two objects the
gallery has never shown -- the polygon core K'(B) (A132) and the cell's candidate cover.

  LEFT   the LP dual support of the CONVERGED record, fill = dual weight y on one sequential scale
         (A107 v2); every conditioned square as a cyan H at the box centre and the MID-TILT with
         faint outlines at the two extremal tilts; the certified polygon core K'(B) drawn as a
         polygon inside each H; every dual-support column that overlaps a hypothesis square at
         EVERY pose of its box outlined red-dashed with the overlap printed; the container and the
         four corner cells.  k0 has NO pins, so the "feasible centre" rule of gen_a57_lp.py runs
         against the container and the OTHER conditioned boxes' K' instead of against pins.
  RIGHT  the near-packing: A107's minimised shadow where the cell has one, A128's polished
         near-packing where it does not, and the raw integral dual support at s0 where neither
         exists.  Slot squares blue and named, free squares red with f-index and tilt, contacts
         ringed -- the panel the PI labels from.
  THIRD  the candidate cover: the slot the support keeps occupying (A113's re-branching rule) or
         the two-meeter cover on a corner cell with LANE <= 1 (A118 T4).

Every drawn square is containment-checked; every red-dashed column's overlap is re-verified by an
independent SAT implementation at 7^3 poses of the box.  READ-ONLY on every campaign; writes only
docs/shadows/k0v3/.

    python code/gallery140.py
"""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
for p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
          os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
          os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code"),
          os.path.join(ROOT, "attempts", "A107-shadow-gallery", "code"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import polycore                                              # noqa: E402
import exactcore                                             # noqa: E402
from caselp import Box, EPS_CORE                             # noqa: E402
import shadowlib as L                                        # noqa: E402
import minimise as M                                         # noqa: E402
import cells140 as C140                                      # noqa: E402

S0 = C140.S0
SHAT = C140.SHAT
OUT = os.path.join(ROOT, "docs", "shadows", "k0v3")
SC = 118                       # px per unit, A107's gallery scale
NPOSE = 7                      # 7^3 pose grid of the box (gen_a57_lp.py's rule)

HYP_FILL, HYP_STROKE = "#00e5ff", "#000000"


# ------------------------------------------------------------------ primitives
def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s), cy + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def wrap(x, y, t, width_px, size=9.0, col="#222", bold=False, lead=None):
    """Word-wrapped text block; returns (elements, y after the block)."""
    per = max(8, int(width_px / (size * 0.52)))
    words, lines, cur = str(t).split(), [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= per:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    lead = lead or (size + 3.0)
    out = []
    for i, ln in enumerate(lines):
        out.append(text(x, y + i * lead, ln, size, col, bold))
    return out, y + len(lines) * lead


def poly(ox, oy, sc, P, fill, stroke, op=0.6, w=1.5, dash=""):
    pts = " ".join(f"{ox + x * sc:.1f},{oy - y * sc:.1f}" for x, y in P)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.2f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>')


def frame(ox, oy, sc, s):
    out = [f'<rect x="{ox}" y="{oy - s * sc:.1f}" width="{s * sc:.1f}" height="{s * sc:.1f}" '
           f'fill="none" stroke="#000" stroke-width="2.2"/>']
    for (x0, y0) in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        out.append(f'<rect x="{ox + x0 * sc:.1f}" y="{oy - (y0 + 1) * sc:.1f}" width="{sc}" '
                   f'height="{sc}" fill="none" stroke="#bbb" stroke-width="1" '
                   f'stroke-dasharray="4,3"/>')
    return out


def wcol(y, dark=False):
    """A107 v2: sequential pale-yellow -> dark-orange ramp on the dual weight y."""
    y = 0.0 if y is None else max(0.0, min(1.0, float(y)))
    h = 46.0 - 22.0 * y
    l = (88.0 - 46.0 * y) - (22.0 if dark else 0.0)
    return f"hsl({h:.0f},92%,{max(l, 12.0):.0f}%)"


def sat_poly(P, Q):
    """Independent SAT gap between two convex polygons (>0 disjoint, <0 overlap depth)."""
    best = -9e9
    for A, B in ((P, Q), (Q, P)):
        n = len(A)
        for i in range(n):
            a, b = A[i], A[(i + 1) % n]
            ex, ey = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(ex, ey)
            if ln < 1e-15:
                continue
            ax, ay = -ey / ln, ex / ln
            pp = [x * ax + y * ay for x, y in A]
            qq = [x * ax + y * ay for x, y in B]
            best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


def box_poses(b, n=NPOSE):
    for i in range(n):
        for j in range(n):
            for k in range(n):
                yield (b["x0"] + (b["x1"] - b["x0"]) * i / (n - 1.0),
                       b["y0"] + (b["y1"] - b["y0"]) * j / (n - 1.0),
                       math.radians(b["th0"] + (b["th1"] - b["th0"]) * k / (n - 1.0)))


def gap_over_box(P, b, n=NPOSE):
    """max over the n^3 pose grid of the SAT gap between P and the hypothesis square.
    < 0  =>  P overlaps the hypothesis square at EVERY sampled pose (gen_a57_lp.py's rule)."""
    g = -9e9
    for (hx, hy, ht) in box_poses(b, n):
        g = max(g, sat_poly(P, sq(hx, hy, ht)))
    return g


# ------------------------------------------------------------------ slot census
def slot_cell_poly(name, s):
    (x, y) = M.slot_centres([name], s)[0]
    return [(x - 0.5, y - 0.5), (x + 0.5, y - 0.5), (x + 0.5, y + 0.5), (x - 0.5, y + 0.5)], (x, y)


CENSUS_RULE = ("BIN RULE: every dual-support column is assigned to EXACTLY ONE bin — the named "
               "slot cell whose CENTRE is nearest the column's centre (ties broken by name "
               "order), over BL/BR/TL/TR (i,j), i,j < 3. So the bin weights PARTITION the "
               "support's total dual weight; they do not double count. The separate 'met' counts "
               "below are the geometric statement (a column can overlap several cells) and are "
               "A113's singly/doubly-met census, not a partition. The conditioned square is NOT a "
               "dual-support column — the node LP counts only the budget = 11 - #cores OTHER "
               "squares — so no bin contains it; a bin a conditioned box can itself reach is "
               "marked (H).")


def slot_census(pk, boxes, s, imax=3, thr=1e-9):
    """Two different objects, kept apart because they answer different questions.

    * `n_met` / `w_met`  -- columns with positive-area overlap with the closed slot cell.  A
      column can meet several cells, so these DO NOT partition the support; 'singly'/'doubly met'
      is A113's census and this is what it means.
    * `n_bin` / `w_bin`  -- each column assigned to exactly ONE bin, the nearest slot CENTRE.
      These PARTITION the support: sum of w_bin over bins = sum of y over columns.
    * `n_snap` / `w_snap` -- columns that actually snap onto the cell (axis-aligned, on centre).
      This is the object A113's re-branching rule talks about.

    The conditioned squares are not dual-support columns at all (the node LP counts the budget =
    11 - #cores OTHER squares), so nothing here can be one; `cond_can_meet` records which
    conditioned boxes could themselves reach the cell, and those bins are marked (H)."""
    names = [f"{c}({i},{j})" for c in ("BL", "BR", "TL", "TR")
             for i in range(imax) for j in range(imax)]
    ctrs = {nm: slot_cell_poly(nm, s)[1] for nm in names}
    # --- the partition: nearest slot centre, one bin per column
    assign = {}
    for k, p in enumerate(pk):
        best = min(names, key=lambda nm: (math.hypot(p["cx"] - ctrs[nm][0],
                                                     p["cy"] - ctrs[nm][1]), nm))
        assign.setdefault(best, []).append(k)
    out = []
    for nm in names:
        cell, ctr = slot_cell_poly(nm, s)
        met, snapped = [], []
        for k, p in enumerate(pk):
            P = sq(p["cx"], p["cy"], p["theta"])
            if sat_poly(P, cell) < -thr:
                met.append((k, float(p.get("y", 0.0))))
            if L.snap(p["cx"], p["cy"], p["theta"], s) == nm:
                snapped.append(k)
        binned = assign.get(nm, [])
        if not met and not binned:
            continue
        cond = []
        for bi, b in enumerate(boxes):
            if any(sat_poly(sq(hx, hy, ht), cell) < -thr for (hx, hy, ht) in box_poses(b, 5)):
                cond.append(bi)
        out.append(dict(slot=nm, centre=[ctr[0], ctr[1]],
                        n_met=len(met), w_met=round(sum(w for _, w in met), 6),
                        n_bin=len(binned),
                        w_bin=round(sum(float(pk[k].get("y", 0.0)) for k in binned), 6),
                        n_snap=len(snapped),
                        w_snap=round(sum(float(pk[k].get("y", 0.0)) for k in snapped), 6),
                        cols=[k for k, _ in met][:12], bin_cols=binned[:12],
                        cond_can_meet=cond,
                        kind=("singly" if len(met) == 1 else "doubly")))
    out.sort(key=lambda r: (-r["n_snap"], -r["w_snap"], -r["w_bin"], r["slot"]))
    return out


# ------------------------------------------------------------------ panels
def panel_lp(ox, oy, sc, title, sub, d, boxes, pcs, sts, exs, s):
    """LEFT: the LP dual support with the 2026-09-07 drawing rules."""
    pk = d.get("packing", [])
    ys = [float(p.get("y", 0.0)) for p in pk]
    ymax = max(ys) if ys else 1.0
    out = [text(ox, oy - S0 * sc - 52, title, 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 38, sub, S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)

    # --- the "feasible centre" rule, k0 form: no pins, so feasibility is the container and the
    # OTHER conditioned boxes' polygon cores.
    def feasible(cx, cy, th, skip):
        P = sq(cx, cy, th)
        if not all(-1e-12 <= x <= s + 1e-12 and -1e-12 <= y <= s + 1e-12 for x, y in P):
            return False
        for j, pc in enumerate(pcs):
            if j == skip:
                continue
            if polycore.poly_square_depth(pc.P, [[cx, cy]], [th])[0] > 0.0:
                return False
        return True

    def nearest_feasible(b, th, skip, N=40):
        cx0, cy0 = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
        best = None
        for i in range(N + 1):
            for j in range(N + 1):
                cx = b["x0"] + (b["x1"] - b["x0"]) * i / N
                cy = b["y0"] + (b["y1"] - b["y0"]) * j / N
                if feasible(cx, cy, th, skip):
                    dd = math.hypot(cx - cx0, cy - cy0)
                    if best is None or dd < best[0]:
                        best = (dd, cx, cy)
        return best

    # --- the support, drawn by weight; impossible columns red-dashed
    bad = 0
    imposs = []
    for k, p in enumerate(sorted(range(len(pk)), key=lambda k: float(pk[k].get("y", 0.0)))):
        pass
    order = sorted(range(len(pk)), key=lambda k: float(pk[k].get("y", 0.0)))
    for k in order:
        p = pk[k]
        cx, cy, th, y = (float(p["cx"]), float(p["cy"]), float(p["theta"]),
                         float(p.get("y", 0.0)))
        P = sq(cx, cy, th)
        if not all(-1e-6 <= x <= s + 1e-6 and -1e-6 <= yy <= s + 1e-6 for x, yy in P):
            bad += 1
            continue
        w = y / ymax if ymax > 0 else 0.0
        out.append(poly(ox, oy, sc, P, wcol(w), wcol(w, True), 0.85, 1.0))
        if w < 0.95:
            out.append(text(ox + cx * sc, oy - cy * sc + 3, f"{y:.2f}", 7.5, "#5d4037",
                            False, "middle"))
        gmin, bi = 9e9, None
        for j, b in enumerate(boxes):
            g = gap_over_box(P, b)
            if g < gmin:
                gmin, bi = g, j
        # depth against each of the three cores of the box that fires (positive = meets)
        d_st = max(float(polycore.core_depth_fast(c, [[cx, cy]], [th])[0]) for c in sts)
        d_ex = max(float(polycore.core_depth_fast(c, [[cx, cy]], [th])[0]) for c in exs)
        d_pl = max(float(polycore.poly_square_depth(pc.P, [[cx, cy]], [th])[0]) for pc in pcs)
        kp = bool(d_pl > EPS_CORE)
        if gmin < -1e-9:
            # the LP drops a row only when it penetrates a core by more than EPS_CORE = 2e-3,
            # so "clears" here means "passes the LP's own filter at that core".
            imposs.append(dict(col=k, box=bi, overlap=-gmin, y=y, kprime=kp,
                               d_stock=d_st, d_exact=d_ex, d_poly=d_pl, eps=EPS_CORE,
                               clears_stock=bool(d_st <= EPS_CORE),
                               clears_exact=bool(d_ex <= EPS_CORE),
                               pose=[cx, cy, math.degrees(th) % 90.0]))
            lab = f"K(a) d={d_st:+.3f} clears (LP kept it)"
            lab += (f"; K_exact d={d_ex:+.3f} " +
                    ("DROPS it" if d_ex > EPS_CORE else "clears"))
            lab += (f"; K' d={d_pl:+.3f} " + ("DROPS it" if d_pl > EPS_CORE else "clears"))
            out.append(poly(ox, oy, sc, P, "none", "#d50000", 0.0, 2.5, dash="7,3"))
            out.append(text(ox + cx * sc, oy - cy * sc - 15,
                            f"impossible under H: overlap {-gmin:.3f}", 7.0, "#d50000", True,
                            "middle"))
            out.append(text(ox + cx * sc, oy - cy * sc - 7, lab, 6.5, "#d50000", False,
                            "middle"))
    # --- the conditioned squares: box, K', extremal-tilt outlines, the cyan H
    for j, (b, pc) in enumerate(zip(boxes, pcs)):
        out.append(f'<rect x="{ox + b["x0"] * sc:.1f}" y="{oy - b["y1"] * sc:.1f}" '
                   f'width="{(b["x1"] - b["x0"]) * sc:.1f}" '
                   f'height="{(b["y1"] - b["y0"]) * sc:.1f}" fill="none" stroke="#000" '
                   f'stroke-width="1.6"/>')
        th0, th1 = float(b["th0"]), float(b["th1"])
        thm = 0.5 * (th0 + th1)
        for (td, fop, sw, lab) in ((th0, 0.0, 1.0, ""), (th1, 0.0, 1.0, ""),
                                   (thm, 0.35, 2.6, "H")):
            th = math.radians(td)
            nf = nearest_feasible(b, th, j)
            if nf is None:
                hx, hy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
                dash, note = "5,4", " (no feasible centre in box)"
            else:
                _, hx, hy = nf
                dash, note = "", ""
            Ph = sq(hx, hy, th)
            out.append(poly(ox, oy, sc, Ph, HYP_FILL, "#000" if lab else "#006064",
                            fop, sw, dash))
            if lab:
                out.append(text(ox + hx * sc, oy - hy * sc + 4, f"H{j if len(boxes) > 1 else ''}",
                                11, "#000", True, "middle"))
                out.append(text(ox + hx * sc, oy - hy * sc + 16, f"{td:.1f}°{note}", 7.5,
                                "#000", False, "middle"))
            else:
                vx, vy = min(Ph, key=lambda v: v[0] - v[1])
                out.append(text(ox + vx * sc + 2, oy - vy * sc - 3, f"{td:.1f}°", 6.5,
                                "#006064"))
        # PI (2026-09-07): THREE cores inside each H, distinct styles.
        #   K'      the polygon core (A132)               -- purple, translucent fill
        #   K_ex    A135's EXACT axis core                -- solid teal outline, no fill
        #   K(a)    the STOCK axis core the LP pruned against (the record's a) -- solid black
        out.append(poly(ox, oy, sc, [tuple(v) for v in pc.P], "#7e57c2", "#4527a0", 0.42, 1.4))
        out.append(poly(ox, oy, sc, [tuple(v) for v in polycore.core_verts(exs[j])],
                        "none", "#00695c", 0.0, 1.8))
        out.append(poly(ox, oy, sc, [tuple(v) for v in polycore.core_verts(sts[j])],
                        "none", "#000000", 0.0, 1.8))
        kk = pc.P.mean(0)
        out.append(text(ox + kk[0] * sc, oy - kk[1] * sc - 4, "K'", 8.5, "#311b92", True,
                        "middle"))
    e, yy = wrap(ox, oy + 16,
                 f"{len(boxes)} conditioned square(s) H (cyan) + {len(pk)} dual-support "
                 f"placements, fill = dual weight y (pale yellow y→0, dark orange y=1); "
                 f"outside container: {bad}",
                 S0 * sc, 8.5, "#444")
    out += e
    core_leg = "; ".join(
        f"box {j}: a_stock {float(sts[j].a):.6f} (area {(2 * float(sts[j].a)) ** 2:.6f}), "
        f"a_exact {float(exs[j].a):.6f} (area {(2 * float(exs[j].a)) ** 2:.6f}, "
        f"{(float(exs[j].a) / float(sts[j].a)) ** 2:.3f}x), area K' {pcs[j].area():.6f} "
        f"({pcs[j].area() / (2 * float(sts[j].a)) ** 2:.3f}x)"
        for j in range(len(boxes)))
    e, yy = wrap(ox, yy + 2,
                 "THREE cores are drawn inside each H: SOLID BLACK = the STOCK axis core K(a) the "
                 "LP actually pruned against (the record's own a); SOLID TEAL = A135's EXACT axis "
                 "core (certifiable today — a square at the box's own tilt, so the frozen "
                 "certificate schema is unchanged); PURPLE FILL = the polygon core K'(B), the "
                 "full intersection of the square over the box. " + core_leg,
                 S0 * sc, 8.0, "#333")
    out += e
    ncl = sum(1 for r in imposs if r["clears_exact"])
    e, _y = wrap(ox, yy + 2,
                f"red dashed = {len(imposs)} column(s) overlapping a hypothesis square at "
                f"EVERY of the {NPOSE}³ = {NPOSE ** 3} sampled poses of its box. All of them "
                f"clear K(a) at the LP's own drop margin EPS_CORE = {EPS_CORE:g} — that is why "
                f"the LP kept them. {len(imposs) - ncl} are DROPPED by the exact axis core (so an "
                f"exact-core row filter deletes them with no verifier change); {ncl} clear the "
                f"exact core too and are caught only by K'. Each label gives the three depths.",
                S0 * sc, 8.5, "#d50000")
    out += e
    return out, imposs, bad, _y


def panel_pack(ox, oy, sc, title, sub, s, poses, ring=True):
    """RIGHT: a real packing.  Slot squares blue and named, free squares red with tilt."""
    out = [text(ox, oy - S0 * sc - 52, title, 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 38, sub, S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)
    polys = [sq(*q) for q in poses]
    exc = max([max(-x, x - s, -y, y - s) for P in polys for x, y in P] or [0.0])
    mg = min([L.sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2])
              for i in range(len(poses)) for j in range(i + 1, len(poses))] or [0.0])
    names, isfree = [], []
    nf = 0
    for (cx, cy, th) in poses:
        nm = L.snap(cx, cy, th, s, dtol=1e-3, atol=0.05)
        if nm:
            names.append(nm)
            isfree.append(False)
        else:
            names.append(f"f{nf}")
            nf += 1
            isfree.append(True)
    for i, P in enumerate(polys):
        fill = "#ef9a9a" if isfree[i] else "#90caf9"
        stroke = "#c62828" if isfree[i] else "#1565c0"
        out.append(poly(ox, oy, sc, P, fill, stroke, 0.6))
        cx, cy, th = poses[i]
        out.append(text(ox + cx * sc, oy - cy * sc + 4, names[i], 9.5, "#000", True, "middle"))
        if isfree[i]:
            out.append(text(ox + cx * sc, oy - cy * sc + 15,
                            f"{math.degrees(L.tmod(th)):.2f}°", 8, "#333", False, "middle"))
    if ring:
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                if L.sat_gap(poses[i][:2], poses[i][2], poses[j][:2], poses[j][2]) < 1e-6:
                    A, B = polys[i], polys[j]
                    best = (9.0, None)
                    for X, Y in ((A, B), (B, A)):
                        for v in X:
                            for k in range(4):
                                p, q = Y[k], Y[(k + 1) % 4]
                                ex, ey = q[0] - p[0], q[1] - p[1]
                                ln = ex * ex + ey * ey
                                t = max(0.0, min(1.0, ((v[0] - p[0]) * ex
                                                       + (v[1] - p[1]) * ey) / ln))
                                f = (p[0] + t * ex, p[1] + t * ey)
                                dd = math.hypot(v[0] - f[0], v[1] - f[1])
                                if dd < best[0]:
                                    best = (dd, f)
                    f = best[1]
                    out.append(f'<circle cx="{ox + f[0] * sc:.1f}" cy="{oy - f[1] * sc:.1f}" '
                               f'r="4.5" fill="none" stroke="#2e7d32" stroke-width="2"/>')
    e, _y = wrap(ox, oy + 16, f"{len(poses) - nf} slot squares + {nf} free squares; min "
                              f"pairwise SAT separation {mg:+.2e}; worst containment excursion "
                              f"{exc:+.2e}; side {s:.6f}", S0 * sc, 8.5, "#444")
    out += e
    return out, names, exc, mg, _y


def panel_cover(ox, oy, sc, cov, boxes, pcs, s, census, pk, budget):
    """THIRD: the candidate cover, drawn."""
    out = [text(ox, oy - S0 * sc - 52, "panel 3: the candidate cover", 12, bold=True)]
    e, _ = wrap(ox, oy - S0 * sc - 38, cov["headline"], S0 * sc, 8.5, "#444", lead=11.0)
    out += e
    out += frame(ox, oy, sc, s)
    for j, (b, pc) in enumerate(zip(boxes, pcs)):
        out.append(f'<rect x="{ox + b["x0"] * sc:.1f}" y="{oy - b["y1"] * sc:.1f}" '
                   f'width="{(b["x1"] - b["x0"]) * sc:.1f}" '
                   f'height="{(b["y1"] - b["y0"]) * sc:.1f}" fill="none" stroke="#000" '
                   f'stroke-width="1.6"/>')
        out.append(poly(ox, oy, sc, [tuple(v) for v in pc.P], "#7e57c2", "#4527a0", 0.4, 1.3))
    cellname = cov["cell"]
    cell, ctr = slot_cell_poly(cellname, s)
    out.append(poly(ox, oy, sc, cell, "#ffd54f", "#f57f17", 0.55, 2.6))
    out.append(text(ox + ctr[0] * sc, oy - ctr[1] * sc + 4, cellname, 10, "#000", True, "middle"))
    # PI (2026-09-07): the census bins are NOT squares of a packing.  Thin dashed outline, NO
    # fill, and a label that says "slot bin".  Each column is in exactly one bin (nearest centre),
    # so the printed weights partition the support's total dual weight.
    allbins = [r for r in census if r["n_bin"] > 0]
    shown = sorted(allbins, key=lambda r: -r["w_bin"])[:12]
    for r in shown:
        c2, ct2 = slot_cell_poly(r["slot"], s)
        if r["slot"] == cellname:
            continue
        out.append(poly(ox, oy, sc, c2, "none", "#2e7d32", 0.0, 1.0, dash="3,3"))
        out.append(text(ox + ct2[0] * sc, oy - ct2[1] * sc - 2,
                        f"slot bin {r['slot']}", 6.5, "#1b5e20", False, "middle"))
        out.append(text(ox + ct2[0] * sc, oy - ct2[1] * sc + 7,
                        f"w={r['w_bin']:.2f} n={r['n_bin']}"
                        + (" (H)" if r["cond_can_meet"] else ""), 6.5, "#1b5e20", False,
                        "middle"))
    tot_bin = sum(r["w_bin"] for r in census)
    tot_y = sum(float(p.get("y", 0.0)) for p in pk)
    y = oy + 16
    e, y = wrap(ox, y, "LEGEND (this panel): green dashed = slot-census BINS (support columns "
                       "grouped by nearest slot centre; NOT squares of a packing); amber = the "
                       "cover corner; purple polygon = the conditioned square's K'; black "
                       "rectangle = its parameter box.", S0 * sc, 8.0, "#1b5e20")
    out += e
    y += 2.0
    e, y = wrap(ox, y, f"bin weights partition the support: sum over ALL {len(allbins)} bins "
                       f"{tot_bin:.4f} = sum of dual weights {tot_y:.4f} (budget {budget}); every "
                       f"column is in exactly one bin. {len(shown)} heaviest bins drawn; the full "
                       f"list is under the panels. (H) = a conditioned square can itself reach "
                       f"that cell. The conditioned square is not a dual-support column.",
                S0 * sc, 8.0, "#555")
    out += e
    y += 3.0
    for ln in cov["lines"]:
        e, y = wrap(ox, y, ln, S0 * sc, 8.5, "#333")
        out += e
        y += 2.0
    return out, y


# ------------------------------------------------------------------ candidate cover
def choose_cover(cell, lane, census, boxes):
    """A118 T4's two-meeter cover where a corner cell has LANE <= 1; else A113's re-branching
    split on the slot the support keeps occupying."""
    le1 = [(c, v) for c, v in lane["fresh"].items() if v["verdict"].startswith("LANE<=")]
    if le1:
        c, v = le1[0]
        return dict(
            kind="two-meeter (A118 T4)", cell=c, lane=v.get("lane_ub"),
            ncond_pot=v.get("ncond_pot"),
            headline=f"TWO-MEETER on {c}: LANE <= {v.get('lane_ub')} non-conditioned squares "
                     f"reach it; {v.get('ncond_pot')} conditioned square(s) can",
            words=(f"A118's lane count certifies that at most {v.get('lane_ub')} square OTHER than "
                   f"the conditioned one can meet {c}, while {v.get('ncond_pot')} conditioned "
                   f"square(s) could. Cover: (a) the conditioned square meets {c} -- restrict its "
                   f"box to the sub-box of poses that meet {c} and re-solve; (b) it does not -- "
                   f"then {c} is met by at most one square in total and K0-FREE teleports the "
                   f"configuration into class k1, which is dead on the window."),
            needs=("(a) the LANE <= 1 cover certified by interval arithmetic over the box cover "
                   "(A118 has it: cover ok + confirm clean); (b) the 'meets C' / 'misses C' split "
                   "emitted as two children with LP certificates; (c) K0-FREE for the k0 root "
                   "(docs/proofs/k0_route.md, already proved)."),
            lines=[f"(a) conditioned square meets {c}  ->  shrink its box, re-solve",
                   f"(b) it does not  ->  {c} met by <= 1 square  ->  K0-FREE  ->  k1 (dead)",
                   f"needs: A118 cover certificate on {c}; the two-child split; K0-FREE (proved)"])
    top = census[0] if census else None
    nm = top["slot"] if top else "BL(0,0)"
    return dict(
        kind="re-branch on the occupied slot (A113)", cell=nm, lane=None,
        ncond_pot=None,
        headline=f"RE-BRANCH on {nm}: the support keeps occupying it "
                 f"({top['n_snap']} column(s) SNAP onto it, weight {top['w_snap']:.2f}; "
                 f"{top['n_met']} column(s) meet it at all, weight {top['w_met']:.2f})"
                 if top else "RE-BRANCH",
        words=(f"A113's re-branching rule: the dual support keeps occupying {nm} "
               f"({top['n_snap']} column(s) snapped onto the cell, weight {top['w_snap']:.2f}; "
               f"{top['n_met']} column(s) meet it, weight {top['w_met']:.2f}), "
               f"so branch on it. Cover: (a) some square has its centre in the box of {nm} -- add "
               f"that box as a second conditioned square and re-solve at budget-1; (b) no square "
               f"occupies {nm} -- add the NO-family for {nm}, which deletes exactly the columns "
               f"the LP is leaning on."),
        needs=("(a) the two children emitted and LP-certified at s0; (b) the NO-family arm needs "
               "the occupancy transfer of Lemma B-NO to stay sound on the window; (c) the "
               "conditioned-pair gate (cores pairwise disjoint) checked for the first child."),
        lines=[f"(a) a square occupies {nm}  ->  second conditioned box, budget-1",
               f"(b) none does  ->  NO-family on {nm}, deletes the leaned-on columns",
               "needs: two children LP-certified; Lemma B-NO on the (b) arm"])


# ------------------------------------------------------------------ right-panel geometry
def right_poses(cell, d, boxes):
    """(poses, side, provenance) for the right panel."""
    np_ = C140.a128_nearpack(cell)
    if np_ is not None:
        return ([tuple(map(float, q)) for q in np_["poses"]], float(np_["side"]),
                f"A128 near-packing of the converged support (all 11 squares polished free), "
                f"worst gap {np_['worst_gap']:+.1e}")
    alias = None
    for (nm, lvl, src, fn, lk, al) in C140.CELLS:
        if nm == cell:
            alias = al
    sid, _ = C140.a107_shadow(alias) if alias else (None, None)
    if sid:
        sh = C140.a107_shadow_geom(sid)
        poses = [tuple(map(float, f)) for f in sh["free"]] + \
                [(x, y, 0.0) for (x, y) in M.slot_centres(sh["slots"], sh["s"])]
        return poses, float(sh["s"]), (f"A107 shadow {sid} minimised to s* = {sh['s']:.6f} "
                                       f"(s* - s-hat {sh['ds']:+.6f}); the cell enters {sid} "
                                       f"through its A99/A38 alias {alias}")
    pk = [p for p in d.get("packing", []) if float(p.get("y", 0.0)) > 0.5]
    poses = [(float(p["cx"]), float(p["cy"]), float(p["theta"])) for p in pk]
    for b in boxes:
        poses.append((0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"]),
                      math.radians(0.5 * (b["th0"] + b["th1"]))))
    return poses, float(d.get("s") or S0), (
        "RAW integral dual support at the certified side s0, plus the conditioned square at the "
        "centre of its box and tilt window. This cell has neither a gallery shadow nor a polished "
        "near-packing. It is NOT a packing and NOT minimised: the conditioned square OVERLAPS the "
        "support (see the min pairwise SAT separation below) -- that overlap is exactly the "
        "'impossible column' effect the left panel draws in red.")


# ------------------------------------------------------------------ main
LEGEND = ("LEGEND  |  LEFT = the LP dual support of the CONVERGED record (A115 T6): fill = dual "
          "weight y on one sequential scale (pale yellow y→0, dark orange y=1), bright cyan "
          "+ heavy outline + H = a conditioned square drawn at the box centre and the MID-TILT, "
          "faint cyan outlines = the two extremal tilts of the window, purple = the certified "
          "polygon core K'(B) (A132), red dashed = a column that overlaps a hypothesis square at "
          "EVERY pose of its box.  |  RIGHT = a real packing: blue = slot square (named cell), "
          "red = free square (f-index + tilt), green ring = contact at gap < 1e-6.  |  THIRD = "
          "the candidate cover: amber = the cell to branch on, faint green = the other occupied "
          "slots.  k0_00 has NO pins: every hypothesis core is a conditioned square.")


def main():
    os.makedirs(OUT, exist_ok=True)
    t1 = json.load(open(os.path.join(BASE, "results", "t1_polycore.json"), encoding="utf-8"))
    t1map = {r["cell"]: r for r in t1["twelve"]}
    lanes = json.load(open(os.path.join(BASE, "results", "lane140.json"), encoding="utf-8"))
    invitro = {}
    for sh in (0, 1):
        p = os.path.join(BASE, "results", f"invitro140_s{sh}.jsonl")
        if os.path.exists(p):
            for ln in open(p, encoding="utf-8"):
                if ln.strip():
                    r = json.loads(ln)
                    invitro[r["cell"]] = r
    rows, summary = [], []
    for (name, lvl, src, fn, lanekey, alias) in C140.CELLS:
        meta, d = C140.load_cell(name)
        boxes = d["hyp"]["boxes"]
        bxs = [Box.from_json(b) for b in boxes]
        pcs = [polycore.build(b) for b in bxs]
        sts = [b.core() for b in bxs]
        exs = [exactcore.exact_core(b) for b in bxs]
        s = float(d.get("s") or S0)
        pk = d.get("packing", [])
        census = slot_census(pk, boxes, s)
        lane = lanes[name]
        cov = choose_cover(name, lane, census, boxes)
        r1 = t1map[name]
        iv = invitro.get(name, {})

        W1 = S0 * SC + 70
        oy = 132 + S0 * SC
        body, _ = wrap(30, 16, LEGEND, 3 * W1 - 20, 8.5, "#333")
        tau, bud = float(d["tau"]), int(d["budget"])
        sub = (f"tau {tau:.9f} / budget {bud}  (eta {tau - bud:+.2e}), minmass "
               f"{float(d['minmass']):.3f}, converged {d['converged']}; record "
               f"{os.path.basename(meta['record'])}")
        p1, imposs, bad, yb1 = panel_lp(30, oy, SC, f"{name} — panel 1: LP dual support at s0 "
                                               f"= {S0:.6f}", sub, d, boxes, pcs, sts, exs, s)
        body += p1
        poses, s2, prov = right_poses(name, d, boxes)
        p2, names2, exc, mg, yb2 = panel_pack(30 + W1, oy, SC, f"{name} — panel 2: the "
                                                          f"near-packing", prov, s2, poses)
        body += p2
        assert exc <= 1e-4, f"{name}: containment violated by {exc:.2e}"
        p3, yb3 = panel_cover(30 + 2 * W1, oy, SC, cov, boxes, pcs, s, census, pk, bud)
        body += p3

        # ---- the text block
        y = max(yb1, yb2, yb3) + 22.0
        def add(t, size=9.5, col="#222", bold=False):
            nonlocal y
            e, y = wrap(30, y, t, 3 * W1 - 20, size, col, bold)
            body.extend(e)
            y += 3.0

        add(f"{name}  —  level {lvl}  ({src});  budget {bud} = 11 − "
            f"{len(boxes)} conditioned square(s)", 12, "#000", True)
        for j, b in enumerate(boxes):
            bi = r1["boxes"][j]
            add(f"box {j}: x [{b['x0']:.6f}, {b['x1']:.6f}]  y [{b['y0']:.6f}, {b['y1']:.6f}]  "
                f"tilt [{b['th0']:.3f}°, {b['th1']:.3f}°]   |   K' {bi['poly_verts']} "
                f"vertices, area {bi['area_poly']:.6f} = {bi['ratio_poly_stock']:.3f}x the axis "
                f"core K(a) (a = {bi['a_stock']:.6f}); A135 exact axis core a = "
                f"{bi['a_exact']:.6f} ({bi['ratio_exact_stock']:.3f}x area)")
        sup = r1["support"]
        add(f"polygon core on the support: {sup['n_poly']} of {sup['n']} columns meet K' "
            f"(0 meet K(a) — the LP's own filter), carrying dual weight "
            f"{sup['w_poly_only']:.4f} of {sup['w']:.4f} against slack {r1['slack']:+.2e}; "
            f"the A135 exact axis core alone removes {sup['n_exact_only']} column(s) / weight "
            f"{sup['w_exact_only']:.4f} — that part is inside the FROZEN certificate schema.")
        add(f"full pool: {r1['pool']['n_poly']} of {r1['pool']['n']} generated columns meet K' "
            f"({100.0 * r1['pool']['n_poly'] / max(1, r1['pool']['n']):.1f}%); "
            f"K' vs container: worst excursion "
            f"{max(c['excursion_poly'] for c in r1['container']):+.2e} (0 = inside, no T5-type "
            f"kill); K' vs K' between conditioned boxes: "
            + ("; ".join(f"{p['i']}-{p['j']} depth {p['depth_poly']:+.4f}"
                         for p in r1["pairs"]) or "n/a (one conditioned square)"))
        if iv.get("tau") is not None:
            add(f"IN-VITRO LP with the column pool pruned by K' (one re-solve, {iv['cap']:.0f} s "
                f"cap, warm-started from this record): tau {iv['tau']:.6f} of budget {bud} "
                f"(eta {iv['eta']:+.4f}), converged {iv['converged']}, {iv['wall_s']} s — "
                + ("LP-DEAD UNDER POLYGON CORE, CERTIFICATE PENDING: the LP CONVERGED below "
                   "budget. The frozen verifier knows only the axis core K(a); the A135 exact "
                   "axis core is inside the frozen schema and removes part of the same weight."
                   if iv.get("kills_converged") else
                   ("tau is below budget but the LP has NOT converged at the cap — a KILL "
                    "CANDIDATE under the polygon core (A57's `dead_unconverged`), not a kill; "
                    "a warm continuation is what would settle it."
                    if iv.get("kills") else
                    "tau still at budget: the LP replaces the excluded columns, so K' alone does "
                    "not kill this cell.")),
                9.5, "#b71c1c" if iv.get("kills") else "#555", bool(iv.get("kills")))
        met = [r for r in census if r["n_met"] >= 1]
        add("slot census (A113), MET (a column can meet several cells, so these do NOT "
            "partition the support): " + "; ".join(
                f"{r['slot']} {r['kind']} by {r['n_met']} column(s) w {r['w_met']:.2f}"
                + ("*" if r["cond_can_meet"] else "") for r in met[:12])
            + f"   [{len(met)} named cells met; * = a conditioned square can reach it too]")
        binned = [r for r in census if r["n_bin"] > 0]
        add("slot census, BINNED (each column in exactly one bin — the nearest slot centre; these "
            "DO partition): " + "; ".join(
                f"{r['slot']} n={r['n_bin']} w={r['w_bin']:.2f}"
                + ("(H)" if r["cond_can_meet"] else "") for r in binned)
            + f"   [bin total {sum(r['w_bin'] for r in census):.4f} = support total "
              f"{sum(float(q.get('y', 0.0)) for q in pk):.4f}]")
        add(CENSUS_RULE, 9.0, "#555")
        lf = lane["fresh"]
        add("lane count (A118): " + "; ".join(
            f"{c} {v['verdict']}" + (f" (n_cond_pot {v['ncond_pot']})"
                                     if v.get("ncond_pot") else "") for c, v in lf.items())
            + ("   [A118's stored record agrees]" if lane["a118_stored"] and all(
                lane["a118_stored"].get(c, {}).get("verdict") == v["verdict"]
                for c, v in lf.items()) else
               ("   [A118 had no record for this cell — computed here with A118's own "
                "lane.run_cell]" if not lane["a118_stored"] else
                "   [differs from A118's stored record; sampling, see results/lane140.json]")))
        add(f"CANDIDATE COVER — {cov['kind']}: {cov['words']}", 9.5, "#1b5e20", True)
        add(f"    what it needs to be a certified leaf: {cov['needs']}", 9.0, "#1b5e20")
        add(f"geometry check: {len(poses)} squares drawn in panel 2, worst containment excursion "
            f"{exc:+.2e}, min pairwise SAT separation {mg:+.2e}; {bad} support column(s) outside "
            f"the container skipped in panel 1; {len(imposs)} red-dashed column(s), every one "
            f"re-verified by an independent SAT at {NPOSE}³ poses.", 9.0, "#555")

        W = 3 * W1 + 60
        H = int(y + 20)
        doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(W)}" height="{H}" '
                f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ["</svg>"])
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w", encoding="utf-8").write("\n".join(doc))
        import xml.dom.minidom
        xml.dom.minidom.parse(p)

        sid, _ = C140.a107_shadow(alias) if alias else (None, None)
        shg = C140.a107_shadow_geom(sid) if sid else None
        pstat = (f"K' removes {sup['n_poly']} support column(s) / weight "
                 f"{sup['w_poly_only']:.3f} > slack {r1['slack']:.1e}; "
                 f"exact-core part {sup['w_exact_only']:.3f}")
        nfree = sum(1 for n2 in names2 if n2.startswith("f"))
        iv = invitro.get(name, {})
        rows.append(dict(
            # ---- review.csv's own columns
            file=f"{name}.svg", shadow=name,
            classes_or_sources=f"k0_00; {src}; record {os.path.basename(meta['record'])}",
            k=f"k{len(poses)} ({len(poses) - nfree} slot + {nfree} free)",
            s_star=(f"{s2:.6f}" if mg > -1e-5 else f"n/a (s0, raw support, overlap {-mg:.3f})"),
            s_star_minus_shat=(f"{s2 - SHAT:+.6f}" if mg > -1e-5 else "n/a"),
            nodes_explained="1 (this cell)", levels=f"L{lvl}",
            n_free_squares=nfree,
            common_tilt=(f"{shg['common_tilt']:.3f} deg"
                         if shg and shg.get("common_tilt") is not None else "no"),
            flexes=(shg["analysis"].get("flexes_fixed_s") if shg else "-"),
            coincides_with=(sid or "-"),
            # ---- the new k0v3 columns
            polycore_status=pstat, candidate_cover=f"{cov['kind']} on {cov['cell']}",
            right_panel=prov.split(";")[0], budget=bud, tau=f"{tau:.9f}",
            minmass=f"{float(d['minmass']):.3f}", n_conditioned=len(boxes),
            n_support=len(pk), n_impossible=len(imposs),
            n_impossible_kprime=sum(1 for r in imposs if r["kprime"]),
            slot_census_met="; ".join(f"{r['slot']}x{r['n_met']}(w{r['w_met']:.2f})"
                                      for r in met[:8]),
            slot_census_binned="; ".join(f"{r['slot']}n{r['n_bin']}(w{r['w_bin']:.2f})"
                                        for r in census if r["n_bin"] > 0),
            lane_count="; ".join(f"{c}:{v['verdict']}" for c, v in lf.items()),
            invitro_poly_lp=(f"tau {iv['tau']:.6f} / {bud} "
                             + ("LP-DEAD (converged)" if iv.get("kills_converged")
                                else ("kill candidate (unconverged at cap)" if iv.get("kills")
                                      else "no kill"))
                             + f", {iv.get('wall_s')} s"
                             if iv.get("tau") is not None else "not run"),
            # ---- empty PI columns
            PI_reading="", PI_load_path="", PI_binding_contact="", PI_drain_or_kill=""))
        summary.append(dict(cell=name, level=lvl, s_star=s2, shadow=sid, prov=prov,
                            panel2_min_sat=mg, panel2_is_packing=bool(mg > -1e-5),
                            polycore=pstat, cover=cov, lane=lf, census=census, census_met=met[:12],
                            n_impossible=len(imposs),
                            n_impossible_kprime=sum(1 for r in imposs if r["kprime"]),
                            width=int(W), height=H, tau=tau, budget=bud,
                            record=meta["record"], boxes=boxes,
                            support=sup, pool=r1["pool"], slack=r1["slack"],
                            container=r1["container"], pairs=r1["pairs"],
                            invitro=iv, n_free=nfree, n_slot=len(poses) - nfree,
                            impossible=imposs))
        print(f"{name:26s} -> {p}  ({int(W)}x{H})  impossible {len(imposs)} "
              f"(K' {sum(1 for r in imposs if r['kprime'])})  cover {cov['kind']}", flush=True)

    cols = list(rows[0].keys())
    with open(os.path.join(OUT, "review_k0v3.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump(summary, open(os.path.join(BASE, "results", "gallery140.json"), "w",
                            encoding="utf-8"), indent=1)
    print("wrote", os.path.join(OUT, "review_k0v3.csv"), "and results/gallery140.json")


if __name__ == "__main__":
    main()
