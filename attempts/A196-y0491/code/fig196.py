"""A196 step 5 -- the step page docs/residue_map/y0491_cascade.svg (gen_a57_lp.py's drawing rules): one panel per
step, hypothesis squares only at admissible poses (the centre of a SURVIVING piece at its mid tilt, checked inside
the container and clear of every other role's K'), the TR(0,1) meeters as filled families (their surviving pieces'
union, K' solid, extreme poses as thin outlines), the chord lines with the chords printed, U hatched, times
printed, a note per panel saying what it IS.        python fig196.py <nid> [--out docs/residue_map/y0491_cascade.svg]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
S0 = 969271 / 250000
S = 140
COL = {"H": "#00e5ff", "F1": "#ffb300", "F2": "#7cb342", "F3": "#ab47bc", "F4": "#ef5350", "F5": "#26a69a"}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=10, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return '<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


def sat(p, q):
    axes = []
    for poly in (p, q):
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ex, ey = b[0] - a[0], b[1] - a[1]
            n = math.hypot(ex, ey) or 1.0
            axes.append((-ey / n, ex / n))
    best = -9
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]
        qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best


class Panel:
    def __init__(self, ox, oy):
        self.ox, self.oy, self.out = ox, oy, []

    def X(self, x):
        return self.ox + x * S

    def Y(self, y):
        return self.oy - y * S

    def poly(self, P, fill, fo, stroke, sw=1.0, dash=""):
        pts = " ".join("%.1f,%.1f" % (self.X(x), self.Y(y)) for x, y in P)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.out.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>' % (pts, fill, fo, stroke, sw, d))

    def rect(self, x0, x1, y0, y1, fill, fo, stroke, sw=1.0, dash=""):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, fo, stroke, sw, dash)

    def container(self, title, sub):
        self.out.append(text(self.ox, self.oy - S0 * S - 24, title, 12, bold=True))
        self.out.append(text(self.ox, self.oy - S0 * S - 9, sub, 8.5, "#444"))
        self.out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="2"/>' % (self.ox, self.oy - S0 * S, S0 * S, S0 * S))
        for (x0, y0) in [(0, 0), (S0 - 1, 0), (0, S0 - 1), (S0 - 1, S0 - 1)]:
            self.rect(x0, x0 + 1, y0, y0 + 1, "none", 0, "#bbb", 1, "4,3")

    def note(self, lines, y0=14, size=8.5, col="#333"):
        for i, l in enumerate(lines):
            self.out.append(text(self.ox, self.oy + y0 + 11 * i, l, size, col))


def admissible_pose(node, role):
    """the centre of the largest surviving piece at its mid tilt, inside the container and clear of the other K'."""
    P = sorted(node["pieces"][role], key=lambda p: -(p[1] - p[0]) * (p[3] - p[2]))
    others = [node["kprime"][k] for k in node["kprime"] if k != role and node["kprime"][k]]
    for p in P[:40]:
        cx, cy, th = 0.5 * (p[0] + p[1]), 0.5 * (p[2] + p[3]), math.radians(0.5 * (p[4] + p[5]))
        Q = sq(cx, cy, th)
        if not all(-1e-9 <= x <= S0 + 1e-9 and -1e-9 <= y <= S0 + 1e-9 for x, y in Q):
            continue
        if all(sat(Q, [(float(a), float(b)) for a, b in K]) >= -1e-9 for K in others):
            return cx, cy, th, True
    p = P[0]
    return 0.5 * (p[0] + p[1]), 0.5 * (p[2] + p[3]), math.radians(0.5 * (p[4] + p[5])), False


def draw_roles(pn, node, wbox=None, families=("F1", "F2")):
    for k, h in node["hull"].items():
        if k.startswith("P"):
            pn.poly(sq(0.5 * (h[0] + h[1]), 0.5 * (h[2] + h[3]), 0.0), "#90caf9", 0.6, "#1565c0", 1.5)
    for k in list(families) + ["H"]:
        if k not in node["pieces"]:
            continue
        col = COL.get(k, "#888")
        for p in node["pieces"][k]:                              # the family: every surviving piece's centre rect
            pn.rect(p[0], p[1], p[2], p[3], col, 0.10, col, 0.3)
        K = node["kprime"].get(k)
        if K:
            pn.poly([(float(a), float(b)) for a, b in K], col, 0.55, "#000", 1.0)
        ps = node["pieces"][k]
        ext = [min(ps, key=lambda p: p[4]), max(ps, key=lambda p: p[5])]
        for p in ext:                                            # extreme poses as thin outlines
            pn.poly(sq(0.5 * (p[0] + p[1]), 0.5 * (p[2] + p[3]), math.radians(p[4] if p is ext[0] else p[5])), "none", 0, col, 0.7, "3,2")
        cx, cy, th, ok = admissible_pose(node, k)
        pn.poly(sq(cx, cy, th), col, 0.30, "#000", 2.0)
        pn.out.append(text(pn.X(cx), pn.Y(cy) + 4, k, 11, "#000", True, "middle"))
        pn.out.append(text(pn.X(cx), pn.Y(cy) + 15, "%.1f deg%s" % (math.degrees(th) % 90, "" if ok else " (piece centre; not clear)"), 7.5, "#000", False, "middle"))
    if wbox:
        pn.rect(wbox[0], min(wbox[1], S0), wbox[2], min(wbox[3], S0), "none", 0, "#d50000", 1.5, "6,3")
        pn.out.append(text(pn.X(wbox[0]) + 3, pn.Y(wbox[3] if wbox[3] < S0 else S0) + 11, "B+ TR(0,1)", 8, "#d50000", True))


def panel_node(ox, oy, nodes, case):
    pn = Panel(ox, oy)
    node = case["node"]
    pr = case["propagation"]
    pn.container("1. THE NODE at TR(0,1) -- case %s" % case["label"],
                 "pins (blue) + H + the meeters of B+ as filled families (pieces pale, K' solid, extreme tilts dashed); squares at surviving-piece poses")
    draw_roles(pn, node, nodes["wbox"])
    st = {s["step"]: s for s in nodes["steps"]}
    pt = st.get("pair-test", {})
    subs = {s["case"]: s for s in pt.get("subcases", [])}
    tf = subs.get("two-free", {})
    kept = {k: v for k, v in (node.get("kept") or {}).items() if not k.startswith("P")}
    lines = ["WHAT IT IS: the page's hypothesis (pins in their delta-cores, H in its box) plus Theorem FC at TR(0,1): two distinct NON-pin squares meet B+.",
             "reach: H %s B+ (A161 exact miss test on the base fixed point)." % ("provably MISSES" if st.get("reach", {}).get("H_misses") else "MAY MEET"),
             "pair test (geo178b, %d/%d): H-meets %s; two-free %s -> %s" % (nodes["nsub"], nodes["refine"],
                 "alive" if (subs.get("H-meets") and not subs["H-meets"].get("dead") and not subs["H-meets"].get("vacuous")) else "dead/vacuous",
                 ("%d/%d Lemma A1 cell pairs alive" % (tf.get("n_alive_pairs", -1), tf.get("n_pairs", 0))) if "n_alive_pairs" in tf else str(tf.get("skipped") or tf.get("dead")),
                 pt.get("result", "")),
             "unit propagation (A180 propagate, no branching): %s; %d multibox nodes, %.0f s; assignment %s" % (
                 pr.get("kind"), pr.get("n_nodes", 0), pr.get("seconds", 0), json.dumps(pr.get("assign"))),
             "meet clip rounds: %s; sharp fixed point %d/%d: kept %s, invariant %s (%.0f s); k = %d roles, %d free" % (
                 [r.get("drops") for r in case.get("meet_clip", {}).get("rounds", [])], nodes["sharp"][0], nodes["sharp"][1],
                 {k: round(v, 3) for k, v in kept.items()}, case.get("sharp", {}).get("invariant"), case.get("sharp", {}).get("seconds", 0), case.get("k", 0), case.get("free", 0)),
             "no-room (A189 Lemma 1): %s -- %s (%.0f s)" % ((case.get("noroom") or {}).get("verdict"), (case.get("noroom") or {}).get("reason"), (case.get("noroom") or {}).get("seconds", 0))]
    if pr.get("branch"):
        b = pr["branch"]
        lines.append("stopped at the first branch: %s needs %d, candidates %s, %d options (the node is a superset of every branch)" % (b["cell"], b["need"], "+".join(b["cand"]), b["n_opts"]))
    pn.note(lines)
    return pn.out


def panel_rows(ox, oy, nodes, case, rws):
    pn = Panel(ox, oy)
    node = case["node"]
    pn.container("2. THE CHORD ROWS (Lemma LINE-1, open chords)", "pin midlines (red) and the tightest band line per side (orange); per line the roles' minimum chords, rhs = s0 - sum, beta = floor(rhs)")
    draw_roles(pn, node, nodes["wbox"])
    sm = rws["summary"]
    shown = list(sm["named"]) + [v for v in sm["tightest_per_band"].values()]
    seen = set()
    for r in shown:
        key = (r["orient"], r["off"])
        if key in seen:
            continue
        seen.add(key)
        col = "#d50000" if "midline" in r["tag"] else "#ef6c00"
        off = r["off_float"]
        if r["orient"] == "h":
            pn.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>' % (pn.X(0), pn.Y(off), pn.X(S0), pn.Y(off), col))
            ax, ay = pn.X(S0) + 4, pn.Y(off) + 3
        else:
            pn.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2"/>' % (pn.X(off), pn.Y(0), pn.X(off), pn.Y(S0), col))
            ax, ay = pn.X(off) + 2, pn.Y(S0) - 4
        ch = " ".join("%s %.2f" % (k, v) for k, v in r["minchord"].items() if v > 1e-9)
        pn.out.append(text(ax, ay, "%s=%.3f: %s | rhs %.3f beta %d" % (r["orient"], off, ch, r["rhs_float"], r["beta"]), 6.5, col))
    lines = ["WHAT IT IS: for every axis-parallel line the OPEN chords of the 11 squares sum to <= s0; each boxed role contributes its minimum",
             "over its surviving pieces (>= the hull's), a pin 1 where the line crosses its band; rhs < 0 kills, beta = free squares with a unit chord.",
             "%d lines swept: %d negative, %d with beta <= 1; tightest %s=%.4f (%s) rhs %.4f" % (rws["n_lines"], sm["n_negative"], sm["n_beta_le1"],
                 sm["tightest"]["orient"], sm["tightest"]["off_float"], sm["tightest"]["tag"], sm["tightest"]["rhs_float"])]
    for r in sm["named"]:
        lines.append("  %s (%s=%.4f): pins %d, %s -> rhs %.4f, beta %d" % (r["tag"], r["orient"], r["off_float"], r["pins_full"],
                     ", ".join("%s %.3f" % (k, v) for k, v in r["minchord"].items() if not k.startswith("P")), r["rhs_float"], r["beta"]))
    pn.note(lines)
    return pn.out


def panel_waste(ox, oy, nodes, case, w, mask_path):
    pn = Panel(ox, oy)
    node = case["node"]
    pn.container("3. THE WASTAGE U (A164/A184 certified uncoverable region)", "U hatched (no role pose and no admissible free square meets the cell); the NO-family zone Z = {c : dist(c,U) <= 1/2} outlined")
    draw_roles(pn, node, nodes["wbox"])
    pn.out.append('<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="#b71c1c" stroke-width="1.2"/></pattern></defs>')
    if mask_path and os.path.exists(mask_path):
        sys.path.insert(0, os.path.join(ROOT, "attempts", "A164-wastage-area", "code"))
        import geo164 as G
        z = np.load(mask_path)
        U, Z, xs, ys = z["U"], z["Z"], z["xs"], z["ys"]
        p = float(xs[1] - xs[0])
        for (x0, x1, y0, y1) in G.runs_of(U, xs, ys, p):
            pn.out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#hatch)" stroke="none"/>' % (pn.X(x0), pn.Y(y1), (x1 - x0) * S, (y1 - y0) * S))
        for (x0, x1, y0, y1) in (w.get("zone_rects") or [])[:400]:
            pn.rect(x0, x1, y0, y1, "#b71c1c", 0.06, "#b71c1c", 0.4)
    bands = w.get("bands") or {}
    lines = ["WHAT IT IS: obstacles = every role's K' (inside every surviving pose), covers = the roles' pose unions; a cell is U only if no admissible",
             "free pose meets it (Lipschitz margins). 11 <= s0^2 - |U|, so |U| > s0^2 - 11 = %.4f kills; else Z is a NO-family for the LP." % w["B0"],
             "|U| = %.4f = %.1f%% of the budget %.4f -> %s;  Z: %d rects, area %.3f;  pitch %.3f, %d tilts, %.0f s" % (
                 w["area_U"], 100 * w["ratio_B0"], w["B0"], "KILL" if w["kill"] else "no kill", w["zone_n_rects"], w["zone_area"], w["pitch"], w["ntilt"], w["seconds"]),
             "where U sits: " + "; ".join("%s %.3f" % (k.split(" (")[0], v) for k, v in bands.items()),
             "by region: " + "; ".join("%s %.3f" % (k, v["area_U"]) for k, v in (w.get("by_region") or {}).items() if v["area_U"] > 1e-6),
             "sample check: %s" % json.dumps((w.get("sample") or {}).get("free", w.get("sample")))[:150]]
    pn.note(lines)
    return pn.out


def panel_lp(ox, oy, nodes, case, r, leg, lpres):
    pn = Panel(ox, oy)
    node = case["node"]
    title = "4%s. %s" % (leg, "EXACT-CORE LP (budget 11 - #cores, zone as nofams, guard rows)" if leg == "a" else "WINDOWS + GUARD-LINE LP (Theorem W + G, zone as nofams)")
    pn.container(title, "the LP's dual support: placements filled by dual weight (hue = tilt); the roles as in panel 1; active guard lines drawn")
    draw_roles(pn, node, nodes["wbox"])
    pk = (lpres or {}).get("packing") or []
    ys = [float(p.get("y", 0)) for p in pk]
    ymax = max(ys) if ys else 1.0
    for p in sorted(pk, key=lambda p: float(p.get("y", 0))):
        cx, cy, th, y = float(p["cx"]), float(p["cy"]), float(p["theta"]), float(p.get("y", 0))
        hue = int((math.degrees(th) % 90) / 90 * 300)
        pn.poly(sq(cx, cy, th), "hsl(%d,70%%,45%%)" % hue, 0.15 + 0.6 * (y / ymax if ymax > 0 else 0), "hsl(%d,70%%,30%%)" % hue, 0.8)
    for zr in (r.get("z") or []):
        if float(zr.get("z") or 0) > 1e-6:
            L = zr["line"]; off = float(L["off_float"] if "off_float" in L else L["off"])
            if L["orient"] == "h":
                pn.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a1b9a" stroke-width="2"/>' % (pn.X(0), pn.Y(off), pn.X(S0), pn.Y(off)))
            else:
                pn.out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6a1b9a" stroke-width="2"/>' % (pn.X(off), pn.Y(0), pn.X(off), pn.Y(S0)))
    sup = r.get("support") or {}
    lines = ["WHAT IT IS: " + ("min mu(container) over measures with mu(Q) >= 1 on every admissible non-exempt placement Q (exempt: meets a core, or centre in the zone)" if leg == "a"
                              else "the same LP with every role WINDOWED on its pieces (mu >= 1 on its poses too) and its grown core attached; budget b4"),
             "tau = %s vs budget %s (%s); %d rows; %d of %d guard lines active; LP %.0f s, wall %.0f s" % (
                 ("%.4f" % r["tau"]) if r.get("tau") is not None else "-", r.get("budget"), "converged" if r.get("converged") else "UNCONVERGED at cap",
                 r.get("n_rows") or 0, r.get("n_active") or 0, len(r.get("z") or []), r.get("lp_s") or 0, r.get("wall_s") or 0),
             "verdict: %s%s" % (r.get("verdict"), ("; certificate %s (%s)" % (r.get("certified"), r.get("verifier"))) if r.get("certified") else ""),
             "support: %s" % sup.get("kind", "-"),
             ("cores %s; uncored (windowed only / free) %s; nofams %d" % (r.get("cored"), r.get("uncored"), r.get("n_nofams", 0))) if leg == "a"
             else ("cores attached: %s; nofams %d" % ({k: v for k, v in (r.get("core_kind") or {}).items() if not k.startswith("P")}, r.get("n_nofams", 0)))]
    pn.note(lines)
    return pn.out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "residue_map", "y0491_cascade.svg"))
    a = ap.parse_args()
    nid = a.nid
    nodes = json.load(open(os.path.join(RES, "node_%s.json" % nid), encoding="utf-8"))
    page = json.load(open(os.path.join(RES, "page_%s.json" % nid), encoding="utf-8")) if os.path.exists(os.path.join(RES, "page_%s.json" % nid)) else {}
    PW = int(S0 * S + 60)                                        # panels in a 2-column grid (k -> column k % 2, row k // 2)
    PH = int(S0 * S + 150)
    oy0 = 70 + S0 * S

    def pos(k):
        return 30 + (k % 2) * PW, oy0 + (k // 2) * PH
    body, k = [], 0
    for case in nodes.get("cases", []):
        if "node" not in case:
            continue
        ck = case["label"].replace(":", "_").replace("+", "-")
        body += panel_node(*pos(k), nodes, case); k += 1
        rp = os.path.join(RES, "rows_%s__%s.json" % (nid, ck))
        if os.path.exists(rp):
            body += panel_rows(*pos(k), nodes, case, json.load(open(rp, encoding="utf-8"))); k += 1
        wp = os.path.join(RES, "waste_%s__%s.json" % (nid, ck))
        if os.path.exists(wp):
            body += panel_waste(*pos(k), nodes, case, json.load(open(wp, encoding="utf-8")), os.path.join(RES, "masks", "%s__%s.npz" % (nid, ck))); k += 1
        for leg in ("a", "b"):
            lp = os.path.join(RES, "lp_%s__%s_%s.json" % (nid, ck, leg))
            if os.path.exists(lp):
                lr = os.path.join(RES, "lpres_%s__%s_%s.json" % (nid, ck, leg))
                body += panel_lp(*pos(k), nodes, case, json.load(open(lp, encoding="utf-8")), leg,
                                 json.load(open(lr, encoding="utf-8")) if os.path.exists(lr) else None); k += 1
    W_ = min(2, max(1, k)) * PW + 40
    H_ = int(oy0 + ((k + 1) // 2 - 1) * PH + 110)
    head = [text(30, 22, "A196 -- %s: the PI's reading (TR(0,1) double meet + the top/bottom chord rows vs the wastage budget) run to a verdict: %s %s" % (
        nid, page.get("verdict", nodes.get("verdict")), page.get("leaf") or nodes.get("leaf") or ""), 13, bold=True),
        text(30, 38, "drawing rules: docs/residue_map/gen_a57_lp.py -- hypothesis squares only at admissible poses; every number on the page is from attempts/A196-y0491/results; times printed per step", 9, "#555")]
    doc = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W_, H_)] + head + body + ["</svg>"]
    open(a.out, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(a.out)
    print("wrote", a.out, W_, H_, "panels", k)


if __name__ == "__main__":
    main()
