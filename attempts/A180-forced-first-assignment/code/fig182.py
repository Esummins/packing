"""A182 -- the forced-first step page of one node from the JOURNAL (results/journal/<nid>.jsonl: every
tree node's pieces are stored there, so the page survives a crash and a resume) and the search tree
(results/trees/<nid>.json), in the drawing rules of docs/residue_map/gen_a57_lp.py / fig178 / fig180:
hypothesis square at box centre & mid-tilt with extremal-tilt outlines at the surviving pieces' tilt
extremes; three cores per H; pins as pins (stock square + exact core); forced cells thin dashed with
legends; every instantiated F_i a FILLED region of admissible centres (the surviving pieces); roles
without surviving pieces grey stipple; the premise tests and their results printed on each step's
panel; branch children as sub-panels, dead ones faint with the leaf named.

    python fig182.py c0_Y1033 [--out docs/residue_map/c0_Y1033_forced.svg] [--max-panels 48]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, HERE)
import fig180 as F0                                              # noqa: E402  (A180: draw, premise_lines)
import fig178 as F                                               # noqa: E402  READ-ONLY (A178)
import classes178 as CL                                          # noqa: E402  READ-ONLY (A178)
import geo178 as G                                               # noqa: E402  READ-ONLY (A178)

S0 = F.S0
TREE_KINDS = ("base", "forced", "branch")


def load(nid):
    tree = json.load(open(os.path.join(RES, "trees", "%s.json" % nid), encoding="utf-8"))
    nodes, steps = {}, []
    for l in open(os.path.join(RES, "journal", "%s.jsonl" % nid), encoding="utf-8"):
        if not l.strip():
            continue
        try:
            d = json.loads(l)
        except ValueError:
            continue
        if d.get("kind") in ("subtree", "lane"):
            continue
        steps.append(d)
        if d.get("kind") in TREE_KINDS:
            nodes[d["label"]] = dict(label=d["label"], roles=d.get("roles_in") or {}, boxes=d.get("capture") or {},
                                     dead=d.get("dead"), kept=d.get("kept"), passes=d.get("passes"),
                                     invariant=d.get("invariant"), seconds=d.get("seconds"), chord=d.get("chord"),
                                     sharp=d.get("sharp"))
    return tree, nodes, steps


def stipple(P, node):
    """roles that carry no surviving pieces (undecided / not yet instantiated): grey stipple on the box."""
    for k, b in node["roles"].items():
        if k.startswith("P") or k in node.get("boxes", {}):
            continue
        P.out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#stip)" stroke="none"/>' % (
            P.X(b[0]), P.Y(b[3]), (b[1] - b[0]) * P.sc, (b[3] - b[2]) * P.sc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-panels", type=int, default=48)
    a = ap.parse_args()
    tree, bylabel, steps = load(a.nid)
    row = tree["row"]
    rec = G.load_record(row["record"])
    forced = []
    for f in row["forced"]:
        c = f["cell"]
        corner, (i, j) = c[:2], (int(v) for v in c[3:-1].split(","))
        forced.append(dict(cell=c, wbox=CL.widened_box(corner, i, j), window=CL.meeter_window(corner, i, j)))
    pinset = {"P%d" % k: p["a"] for k, p in enumerate(rec["pins"])}
    panels = []

    def walk(t, depth):
        if t is None:
            return
        panels.append((t, depth))
        for k in t.get("children", []):
            walk(k, depth + 1)
    walk(tree["tree"], 0)
    seen, order = set(), []
    for t, depth in panels:
        parts = t["label"].split("/")
        for n in range(1, len(parts) + 1):
            sub = "/".join(parts[:n])
            if sub not in seen and sub in bylabel:
                seen.add(sub)
                order.append((sub, t if n == len(parts) else None, depth))
    order = order[:a.max_panels]
    SC, PW, PH, COLS = 100.0, 420, 620, 3
    W = COLS * PW + 40
    rows = (len(order) + COLS - 1) // COLS
    Hh = 130 + rows * PH
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><defs>%s</defs>' % (W, Hh, W, Hh, F0.STIP),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hh)]
    hdr = F.Panel(20, 0)
    hdr.text(20, 24, "%s -- A182 forced-first assignment (A180 resumed): %s%s" % (
        a.nid, row["verdict"], (" (" + str(row["leaf"]) + ")") if row.get("leaf") else ""), 16, bold=True)
    hdr.text(20, 44, "class %s; forced cells %s (Theorem FC); each needs two distinct meeters from {H, F1..F5} (notes/assignment.md); "
             "%d multibox nodes (%d fresh, %d replayed from the journal), %.0f s compute." % (
                 row["cls"], ", ".join(f["cell"] for f in row["forced"]), row["n_nodes"], row.get("n_fresh", 0),
                 row.get("n_replayed", 0), row.get("compute_s", 0)), 9.5)
    hdr.text(20, 58, "Drawing: pins light blue (exact core dashed); H solid at hull centre & mid-tilt, extremal surviving tilts dashed, stock core dotted, "
             "exact core dashed, K' filled; F_i = FILLED admissible-centre region (surviving pieces) with a mid-pose outline; grey stipple = no pieces;", 8.5, "#444")
    hdr.text(20, 72, "red dashed = widened forced boxes.  One panel per step (base / FORCED / BRANCH child); the premise tests and results printed under it; "
             "dead panels faint with the leaf named.  Node kept fractions are the 8/3 pass where it ran.", 8.5, "#444")
    out += hdr.out
    for n, (lab, t, depth) in enumerate(order):
        r, c = divmod(n, COLS)
        ox, oy = 20 + c * PW, 100 + r * PH
        node = bylabel[lab]
        dead = bool(node.get("dead")) or (t is not None and t.get("verdict") == "DEAD")
        P = F.Panel(ox + 5, oy + 5, SC)
        F0.draw(P, node, forced, pinset, faint=dead)
        stipple(P, node)
        y = oy + 5 + S0 * SC + 14
        last = lab.split("/")[-1]
        P.text(P.ox, y, ("STEP %d: %s" % (n, "base node" if lab == "root" else last))[:100], 9, "#222", bold=True)
        y += 11
        if node.get("dead"):
            P.text(P.ox, y, ("DEAD: %s" % node["dead"])[:105], 8.5, "#b71c1c", bold=True)
            y += 11
        elif t is not None and "children" not in t:
            P.text(P.ox, y, ("verdict %s%s" % (t.get("verdict"), (": " + str(t.get("leaf"))) if t.get("leaf") else ""))[:105], 8.5,
                   "#b71c1c" if t.get("verdict") == "DEAD" else "#1b5e20", bold=True)
            y += 11
        elif t is not None:
            P.text(P.ox, y, "verdict %s (branch on %s, %d children)" % (t.get("verdict"), t.get("branch"), t.get("n_children", 0)), 8.5,
                   "#b71c1c" if t.get("verdict") == "DEAD" else "#1b5e20", bold=True)
            y += 11
        kp = node.get("kept") or {}
        P.text(P.ox, y, ("kept: " + " ".join("%s=%.3f" % (k, v) for k, v in kp.items()))[:110], 8, "#222")
        y += 11
        sh = node.get("sharp") or {}
        P.text(P.ox, y, "invariant(strict=False) %s  passes %s  %.1f s%s" % (
            "HOLDS" if node.get("invariant") else "FAILS", node.get("passes"), node.get("seconds") or 0,
            ("  (4/2 H %.3f -> 8/3 %.3f)" % (sh["kept42"].get("H", 0), sh["kept83"].get("H", 0))) if sh.get("kept42") and "H" in sh["kept42"] else ""), 8, "#222")
        y += 11
        ch = node.get("chord") or {}
        if ch:
            P.text(P.ox, y, "chord rows: %d lines, min rhs %.3f at %s%s" % (ch.get("n_lines", 0), ch.get("min_rhs", 0), ch.get("line"),
                                                                            "  KILL" if ch.get("dead") else ""), 8, "#222")
            y += 11
        cells = sorted({s["cell"] for s in steps if s.get("label", "").startswith(lab + "/?") and s.get("cell")})
        for cell in cells:
            lines = F0.premise_lines(steps, lab, cell)
            P.text(P.ox, y, "premise at %s: %d tests" % (cell, len(lines)), 8, "#333", bold=True)
            y += 10
            for ln in lines[:6]:
                P.text(P.ox, y, ln[:105], 7.5, "#333")
                y += 9
            if len(lines) > 6:
                P.text(P.ox, y, "  ... %d more (results/journal/%s.jsonl)" % (len(lines) - 6, a.nid), 7.5, "#333")
                y += 9
        out += P.out
    out.append("</svg>")
    path = a.out or os.path.join(ROOT, "docs", "residue_map", "%s_forced.svg" % a.nid)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(path, len(order), "panels")


if __name__ == "__main__":
    main()
