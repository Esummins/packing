"""A180 -- the forced-first step page of one node, from results/capture180_<nid>.json, in the drawing
rules of docs/residue_map/gen_a57_lp.py / fig178.py: hypothesis square at box centre & mid-tilt with
extremal-tilt outlines; three cores per H (stock axis core dotted, exact axis core dashed, K' filled);
pins as pins (stock square + exact core); forced cells thin dashed with legends; every instantiated
F_i a FILLED region of admissible centres (the surviving centre pieces); undecided roles grey
stipple; the premise test and its result printed on each step's panel; one panel per step, branch
children as sub-panels, dead ones faint with the leaf named.

    python fig180.py c0_Y1033 [--out docs/residue_map/c0_Y1033_forced.svg]
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"))
import fig178 as F                                               # noqa: E402  READ-ONLY (A178)
import classes178 as CL                                          # noqa: E402  READ-ONLY (A178)
from caselp import Box                                           # noqa: E402  READ-ONLY (A57)

S0 = F.S0
PAL = F.PAL
STIP = '<pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.7" fill="#888"/></pattern>'


def draw(P, node, forced, pinset, faint=False):
    s = P.s
    op = 0.35 if faint else 1.0
    P.out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000" stroke-width="1.6"/>' % (P.X(0), P.Y(s), s * P.sc, s * P.sc))
    for it in forced:
        P.rect(it["wbox"], "#c62828", 0.6, "4,2", op=op)
        P.text(P.X(0.5 * (it["wbox"][0] + it["wbox"][1])), P.Y(0.5 * (it["wbox"][2] + it["wbox"][3])), it["cell"], 7, "#c62828", anchor="middle")
    roles, boxes = node["roles"], node.get("boxes", {})
    ci = 0
    for k, b in roles.items():
        if k.startswith("P"):
            cx, cy = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3])
            P.poly(F.sq(cx, cy, 0.0), fill="#90caf9", stroke="#1565c0", w=1.0, op=0.5 * op)
            a = pinset.get(k, 0.5)
            P.rect((cx - a, cx + a, cy - a, cy + a), "#1565c0", 0.6, "2,2")
            P.text(P.X(cx), P.Y(cy) + 3, k, 8, "#0d47a1", anchor="middle")
            continue
        col = PAL[ci % len(PAL)]
        ci += 1
        info = boxes.get(k)
        cx, cy, tm = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), 0.5 * (b[4] + b[5])
        if k.startswith("H"):
            P.poly(F.sq(cx, cy, tm), stroke=col, w=1.2, op=op)
            P.poly(F.sq(cx, cy, b[4]), stroke=col, w=0.6, dash="3,2", op=op)
            P.poly(F.sq(cx, cy, b[5]), stroke=col, w=0.6, dash="3,2", op=op)
            P.rect(b, col, 0.8, op=op)
            kc = Box(*b).core()
            if kc is not None and kc.a > 0:
                a = float(kc.a)
                P.rect((float(kc.kx) - a, float(kc.kx) + a, float(kc.ky) - a, float(kc.ky) + a), col, 0.5, "1,2", op=op)
        else:
            P.rect(b, col, 0.5, "2,2", op=op)
        if info is None:
            dead = node.get("dead") == k
            P.text(P.X(cx), P.Y(cy), ("%s EMPTY" % k) if dead else k, 8, "#b71c1c" if dead else col, bold=True, anchor="middle")
            continue
        if k.startswith("F"):
            for pc in info["pieces"][:160]:
                P.rect(pc, col, 0.25, fill=col, op=0.28 * op)
            hb = info["hull"]
            P.poly(F.sq(0.5 * (hb[0] + hb[1]), 0.5 * (hb[2] + hb[3]), 0.5 * (hb[4] + hb[5])), stroke=col, w=0.8, dash="3,2", op=op)
        else:
            for pc in info["pieces"][:96]:
                P.rect(pc, col, 0.3, op=op)
        if len(info["verts"]) >= 3:
            P.poly(info["verts"], fill=col, stroke=col, w=1.0, op=0.45 * op)
            if info.get("axis_a"):
                vx = sum(v[0] for v in info["verts"]) / len(info["verts"])
                vy = sum(v[1] for v in info["verts"]) / len(info["verts"])
                a = info["axis_a"]
                P.rect((vx - a, vx + a, vy - a, vy + a), col, 0.6, "2,2", op=op)
        hb = info["hull"]
        P.text(P.X(0.5 * (hb[0] + hb[1])), P.Y(0.5 * (hb[2] + hb[3])) + 3, k, 8, col, bold=True, anchor="middle")


def premise_lines(steps, parent, cell):
    """what was tested at (parent, cell) and what it said."""
    pre = parent + "/?" + cell + ":"
    out, tested = [], [s for s in steps if s.get("label", "").startswith(pre)]
    for s in tested:
        mem = "+".join(s.get("members") or []) + (("@%s+%s" % tuple(s["split"])) if s.get("split") else "")
        v = "DEAD (%s)" % s["dead"] if s.get("dead") else ("alive" + ((" -- " + s["note"]) if s.get("note") else ""))
        out.append("  test %s: %s%s" % (mem, v, ("  %.0fs" % s["seconds"]) if s.get("seconds") else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-panels", type=int, default=48)
    a = ap.parse_args()
    cap = json.load(open(os.path.join(RES, "capture180_%s.json" % a.nid), encoding="utf-8"))
    forced = []
    for f in cap["forced"]:
        c = f["cell"]
        corner, (i, j) = c[:2], (int(v) for v in c[3:-1].split(","))
        forced.append(dict(cell=c, wbox=CL.widened_box(corner, i, j), window=CL.meeter_window(corner, i, j)))
    pinset = {"P%d" % k: p["a"] for k, p in enumerate(cap["pins"])}
    bylabel = {n["label"]: n for n in cap["nodes"]}
    steps = cap["steps"]
    # the panels: every tree node (base, forced, branch children) in DFS order, with its verdict
    panels = []

    def walk(t, depth):
        if t is None:
            return
        panels.append((t, depth))
        for k in t.get("children", []):
            walk(k, depth + 1)
    walk(cap["tree"], 0)
    # forced steps hidden inside a tree node's label chain: expand the chain of labels
    seen, order = set(), []
    for t, depth in panels:
        lab = t["label"]
        parts = lab.split("/")
        for n in range(1, len(parts) + 1):
            sub = "/".join(parts[:n])
            if sub not in seen and sub in bylabel:
                seen.add(sub)
                order.append((sub, t if n == len(parts) else None, depth))
    order = order[:a.max_panels]
    SC, PW, PH, COLS = 100.0, 420, 600, 3
    W = COLS * PW + 40
    rows = (len(order) + COLS - 1) // COLS
    Hh = 130 + rows * PH
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><defs>%s</defs>' % (W, Hh, W, Hh, STIP),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hh)]
    hdr = F.Panel(20, 0)
    hdr.text(20, 24, "%s -- A180 forced-first assignment: %s%s" % (a.nid, cap["verdict"], (" (" + cap["leaf"] + ")") if cap.get("leaf") else ""), 16, bold=True)
    hdr.text(20, 44, "class %s; forced cells %s (Theorem FC); each cell needs two distinct meeters from {H, F1..F5} (notes/assignment.md)." % (
        cap["cls"], ", ".join(f["cell"] for f in cap["forced"])), 9.5)
    hdr.text(20, 58, "Drawing: pins light blue (exact core dashed); H solid at box centre & mid-tilt, extremal tilts dashed, stock core dotted, exact core dashed, "
             "K' filled; F_i = FILLED admissible-centre region (surviving pieces) with a mid-pose outline; red dashed = widened forced boxes.", 8.5, "#444")
    hdr.text(20, 72, "Each panel = one step (base / FORCED / BRANCH child); the premise tests of that step and their results are printed under it; "
             "dead panels are faint with the leaf named.  %d multibox nodes computed, %d panels." % (len(cap["nodes"]), len(order)), 8.5, "#444")
    out += hdr.out
    for n, (lab, t, depth) in enumerate(order):
        r, c = divmod(n, COLS)
        ox, oy = 20 + c * PW, 100 + r * PH
        node = bylabel[lab]
        dead = bool(node.get("dead")) or (t is not None and t.get("verdict") == "DEAD")
        P = F.Panel(ox + 5, oy + 5, SC)
        draw(P, node, forced, pinset, faint=dead)
        y = oy + 5 + S0 * SC + 14
        last = lab.split("/")[-1]
        head = "STEP %d: %s" % (n, "base node" if lab == "root" else last)
        P.text(P.ox, y, head[:100], 9, "#222", bold=True)
        y += 11
        if node.get("dead"):
            P.text(P.ox, y, "DEAD: EmptyBox(%s) -- pair leaf" % node["dead"], 8.5, "#b71c1c", bold=True)
            y += 11
        elif t is not None and "children" not in t:
            P.text(P.ox, y, "verdict %s%s" % (t.get("verdict"), (": " + str(t.get("leaf"))) if t.get("leaf") else ""), 8.5,
                   "#b71c1c" if t.get("verdict") == "DEAD" else "#1b5e20", bold=True)
            y += 11
        kp = node.get("kept") or {}
        P.text(P.ox, y, ("kept: " + " ".join("%s=%.3f" % (k, v) for k, v in kp.items() if not k.startswith("P")))[:110], 8, "#222")
        y += 11
        P.text(P.ox, y, "invariant(strict=False) %s  passes %s  %.1f s" % ("HOLDS" if node.get("invariant") else "FAILS", node.get("passes"), node.get("seconds") or 0), 8, "#222")
        y += 11
        # premise: the tests made at THIS node for the cell decided next (its child steps)
        cells = sorted({s["cell"] for s in steps if s.get("label", "").startswith(lab + "/?") and s.get("cell")})
        for cell in cells:
            lines = premise_lines(steps, lab, cell)
            P.text(P.ox, y, "premise at %s:" % cell, 8, "#333", bold=True)
            y += 10
            for ln in lines[:7]:
                P.text(P.ox, y, ln[:105], 7.5, "#333")
                y += 9
            if len(lines) > 7:
                P.text(P.ox, y, "  ... %d more tests (results/trees/%s.json)" % (len(lines) - 7, a.nid), 7.5, "#333")
                y += 9
        out += P.out
    out.append("</svg>")
    path = a.out or os.path.join(ROOT, "docs", "residue_map", "%s_forced.svg" % a.nid)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(path, len(order), "panels")


if __name__ == "__main__":
    main()
