"""A185 figure: docs/residue_map/boxed_windows_S1.svg -- l1_104 root/D0/S1 BEFORE (A183: v1 cores only,
tau = budget = 8, the windows unconstrained) and AFTER (A185: per-square windows, v4).  Drawn as
docs/residue_map/gen_kprime_pieces.py: container [0,s0]^2, thin dashed rects = the window pieces (centre
rectangles), filled squares = the attached cores, circles = the measure's support (area ~ weight), bold square
= the adversary's worst pose per window (the min-mass pose over a sample of the window under the final
measure), tau and budget printed.   python fig185.py [--node lp185_l1_104_root_D0_S1]"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)
import numpy as np                                               # noqa: E402
import winlp185 as W                                             # noqa: E402
import run185 as RN                                              # noqa: E402

S0 = W.K.S0
COL = {"H": "#1565c0", "D": "#2e7d32", "S": "#c62828"}


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]]


def core_poly(c):
    return [(float(v[0]), float(v[1])) for v in c.vertices()]


def mass_at(atoms, cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    m = 0.0
    for (x, y, w) in atoms:
        dx, dy = x - cx, y - cy
        u, v = c * dx + s * dy, -s * dx + c * dy
        if abs(u) <= 0.5 + 1e-9 and abs(v) <= 0.5 + 1e-9:
            m += w
    return m


def worst_pose(atoms, wrole, n=9):
    best = None
    for b in wrole.pieces:
        for fx in np.linspace(b.x0, b.x1, 5):
            for fy in np.linspace(b.y0, b.y1, 5):
                for th in np.linspace(b.th0, b.th1, 3):
                    m = mass_at(atoms, fx, fy, math.radians(th))
                    if best is None or m < best[0]:
                        best = (m, fx, fy, th)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="lp185_l1_104_root_D0_S1")
    a = ap.parse_args()
    rec = None
    for ln in open(RN.OUT, encoding="utf-8"):
        d = json.loads(ln)
        if d["node"] == a.node:
            rec = d
    if rec is None:
        raise SystemExit("no record for %s" % a.node)
    tag, wroles, before, cell = RN.a183_nodes()[0]
    H = W.WindowsHyp(wroles)
    atoms = rec.get("atoms") or []
    worst = {w.name: worst_pose(atoms, w) for w in wroles}
    SC = 440 / S0
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="760" font-family="Segoe UI, sans-serif" style="background:#fff">',
           '<text x="30" y="24" font-size="14" font-weight="bold">A185 boxed windows on l1_104 root/D0/S1 (A183 roles H, D, S): BEFORE = v1 cores only (budget 11 - 3 = 8, tau 8, the boxed squares unconstrained); AFTER = per-square pose windows (Theorem W, budget 11, verify_case_v4)</text>']
    panels = [("BEFORE (A183 lp183: cores exempt the free rows; windows carry no obligation)", False,
               "tau = %.4f   budget = %d   ALIVE(LP)" % (before["tau"], before["budget"])),
              ("AFTER (A185: every pose of each window must carry >= 1; own core never exempts)", True,
               "tau = %s   budget_v4 = %d   %s" % (("%.4f" % rec["tau"]) if rec.get("tau") is not None else "n/a",
                                                    rec["budget_v4"], rec.get("verdict")))]
    for pi, (lab, after, line) in enumerate(panels):
        OX, OY = 30 + pi * 560, 60
        X = lambda x: OX + x * SC                                 # noqa: E731
        Y = lambda y: OY + (S0 - y) * SC                          # noqa: E731
        pts = lambda P: " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in P)   # noqa: E731
        out.append('<text x="%d" y="%d" font-size="12" font-weight="bold">%s</text>' % (OX, OY - 22, lab))
        out.append('<text x="%d" y="%d" font-size="12">%s</text>' % (OX, OY - 6, line))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#000" stroke-width="1.2"/>'
                   % (X(0), Y(S0), S0 * SC, S0 * SC))
        if after:
            wmax = max([w for (_, _, w) in atoms] or [1.0])
            for (x, y, w) in atoms:
                out.append('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="#444" fill-opacity="0.55"/>'
                           % (X(x), Y(y), 1.5 + 6.0 * math.sqrt(w / wmax)))
        for i, w in enumerate(wroles):
            c = COL.get(w.name, "#555")
            for b in w.pieces:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="0.5" '
                           'stroke-opacity="0.8" stroke-dasharray="2,1.5"/>' % (X(b.x0), Y(b.y1), (b.x1 - b.x0) * SC, (b.y1 - b.y0) * SC, c))
            if w.core is not None:
                out.append('<polygon points="%s" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="1.2"/>'
                           % (pts(core_poly(w.core)), c, c))
            ub = w.bbox
            for th in (ub.th0, ub.th1):
                out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="0.5" stroke-opacity="0.3"/>'
                           % (pts(sq(0.5 * (ub.x0 + ub.x1), 0.5 * (ub.y0 + ub.y1), math.radians(th))), c))
            if after and worst[w.name] is not None:
                m, fx, fy, th = worst[w.name]
                out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (pts(sq(fx, fy, math.radians(th))), c))
                out.append('<text x="%.1f" y="%.1f" font-size="10" fill="%s">worst %s: mass %.3f at (%.3f, %.3f, %.1f deg)</text>'
                           % (X(0.05), Y(0.05) + 14 * (i + 1) - 10, c, w.name, m, fx, fy, th))
            out.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="bold" fill="%s">%s</text>'
                       % (X(0.5 * (ub.x0 + ub.x1)) - 6, Y(0.5 * (ub.y0 + ub.y1)) + 4, c, w.name))
    ly = 545
    out.append('<text x="30" y="%d" font-size="12" font-weight="bold">roles: pieces, core (kind, half-side), window obligation</text>' % ly)
    for w in wroles:
        ly += 16
        out.append('<text x="30" y="%d" font-size="11" fill="%s">%s: %d pieces, core %s a = %s; AFTER worst pose mass %s</text>'
                   % (ly, COL.get(w.name, "#555"), w.name, len(w.pieces), w.core_kind,
                      ("%.4f" % float(w.core.a)) if w.core else "none", ("%.4f" % worst[w.name][0]) if worst[w.name] else "n/a"))
    for t in ["thin dashed rects = the window pieces (centre rectangles, one per tilt sub-bin; the pose set of the role); filled tilted square = the attached core (A183 grow_core inside K'); faint squares = extremal-tilt outlines at the box centre",
              "AFTER: circles = the measure's support (area ~ weight); bold square = the adversary's worst pose per window under the final measure (min over a 5x5x3 sample of the pieces)",
              "budget: BEFORE 11 - #cores = 8 (free squares only); AFTER n - #cores + #attached = 11 (Theorem W, docs/proofs/boxed_windows.md); a v4 kill is [C] under v4 ONLY -- the frozen v1 chain is untouched",
              "LP rows %s, support %s, converged %s; record attempts/A185-boxed-windows-clause/results/win185.jsonl; container [0,s0]^2, s0 = %.6f" % (rec.get("n_rows"), rec.get("support"), rec.get("converged"), S0)]:
        ly += 16
        out.append('<text x="30" y="%d" font-size="10" fill="#333">%s</text>' % (ly, t))
    out.append("</svg>")
    p = os.path.join(ROOT, "docs", "residue_map", "boxed_windows_S1.svg")
    open(p, "w", encoding="utf-8").write("\n".join(out))
    import xml.dom.minidom
    xml.dom.minidom.parse(p)
    print("wrote", p, "xml ok")


if __name__ == "__main__":
    main()
