"""A211 (fig209 adapted) -- the page (A206's fig206 layout on A209's certificate): the stage-0 line per pad, then per RUN the root panel and
one panel per closed branch, the tree as a text table beside them, the pad-0 verdict printed beside the window verdict;
drawing rules as A204/A205/A206 (fig204.panel).        python fig209.py <nid> | gallery"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.join(HERE, "..", "certs")
OUTD = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A211-coarsetree")
sys.path.insert(0, HERE)
import fig204 as F4                                            # noqa: E402
import fig205 as F5                                            # noqa: E402
import fig206 as F6                                            # noqa: E402

S0, text, defs, panel, wrap = F4.S0, F4.text, F4.defs, F4.panel, F5.wrap
MAXP = 12


def node_note(n):
    kind = str(n.get("kind") or "")
    if kind == "pocket":
        col = "#c62828" if n.get("verdict") == "DEAD" else ("#2e7d32" if n.get("verdict") == "ALIVE" else "#333")
        L = [("PANEL = Lemma POCKET branch %s (depth %d): the 10th square's centre in pocket %s (diameter %s) instantiated as %s; pins + H + roles after this node's cascade (%s rounds, %s s; t = %s s)" % (
            n.get("label"), n.get("depth", 0), n.get("pocket"), n.get("diam"), n.get("pocket_role"), n.get("n_rounds"), n.get("seconds"), n.get("t")), 6.5, "#000", True)]
    elif kind == "inherited":
        return [("%s: DEAD inherited from A206 -- %s" % (n.get("label"), str(n.get("leaf"))[:300]), 6.5, "#c62828", True)]
    else:
        L = F6.node_note(n)
        col = "#c62828" if n.get("verdict") == "DEAD" else "#2e7d32"
    if kind == "exact":
        L = [("PANEL = the EXACT cascade (leaf rule e: nsub 4 / refine 2, lonely clip, basins, %s rounds) at the fully named leaf %s after the coarse rules; %s s; t = %s s" % (n.get("n_rounds"), n.get("label"), n.get("seconds"), n.get("t")), 6.5, col, True)]
    if n.get("coarse"):
        L.append(("COARSE node: pieces re-binned to <= 96 units per role %s, refine 1, <= 2 mutual passes, no lonely clip, reach depth 2 (a SUPERSET of the exact node: sound); n_pieces %s" % (n.get("rebin") and [(r["role"], r["n_before"], r["n_after"]) for r in n["rebin"]], n.get("n_pieces")), 6.5, "#555", False))
    if n.get("clip") == "CC":
        L.append(("DEAD by rule CC (Lemma CORNER-COVER) at slot %s, corner square %s: %s" % (n.get("cc_slot"), n.get("cc_role"), str(n.get("leaf") or "")[:300]), 6.5, "#c62828", True))
    if n.get("noroom"):
        r = n["noroom"]
        L.append(("NO-ROOM leaf (A189 Lemma 1 on the role boxes, k=%s, m=%s): %s%s; %s pockets; %s s" % (r.get("k"), r.get("m"), r.get("verdict"), (" by " + r["clip"]) if r.get("clip") else "", r.get("n_pockets"), r.get("seconds")), 6.5, col, True))
    if kind == "pocket" and n.get("verdict") == "DEAD":
        L.append(("DEAD by %s at round %s: %s" % (n.get("clip"), n.get("killed_round"), str(n.get("leaf") or "")[:300]), 6.5, col, True))
    return L


def stage_lines(doc):
    L = []
    for pad, s in (doc.get("stage0") or {}).items():
        col = "#c62828" if s.get("verdict") == "DEAD" else "#2e7d32"
        L.append(("STAGE 0 (%s pad): %s -- %s [%s; kills %s; CSP units alive %s/%s; %s s]%s" % (
            pad, s.get("verdict"), s.get("source"), s.get("file"), s.get("kills"), s.get("n_units_alive"), s.get("n_units"), s.get("seconds"), ("; " + str(s.get("leaf"))[:160]) if s.get("leaf") else ""), 8, col, True))
    v = doc.get("verdicts") or {}
    L.append(("VERDICTS: window pad (g1, lam = 1.004) = %s | pad 0 (lam = 1, s0-only, WINDOW-PENDING) = %s   (a page is KILLED only by a DEAD g1 verdict; every kill [C: closed-form / library clip trace + the leaf lemma (CORNER-COVER / A189 Lemma 1 / Lemma CN / Lemma BASIN)], no verifier clause)" % (
        v.get("g1", "not run"), v.get("zero", "not run")), 9, "#000", True))
    return L


def run_head(doc, key, d):
    col = "#c62828" if d.get("verdict") == "DEAD" else ("#2e7d32" if d.get("verdict") == "ALIVE" else "#555")
    L = [("RUN %s: the COARSE tree from %s -- coarse internal nodes (one round, re-binned pieces, refine 1, no lonely clip), the leaf rules at every fully named leaf: rule CC -> no-room + pockets -> basin clip (basins %s) -> Rule NS -> the exact cascade; verdict %s in %s s; %s nodes, depth %s, %s CC kills, %s exact leaf cascades, %s NS splits, %s pocket splits, %s inherited kills" % (
        key, d.get("source"), [(b.get("cell"), b.get("r_c")) for b in (d.get("basins") or [])] or "none certified", d.get("verdict"), d.get("seconds"), d.get("n_nodes"), d.get("max_depth"), d.get("cc_kills"), d.get("exact_rounds"), d.get("ns_splits"), d.get("pocket_splits"), len(d.get("inherited") or {})), 9, col, True)]
    if d.get("leaf"):
        L.append((str(d["leaf"])[:600], 7, col, False))
    return L


def page_svg(doc):
    S = 80
    PW = int(S0 * S) + 20
    NH = 110
    ncol = 4
    body = [text(20, 22, "%s -- A211 coarsetree211: the COARSE tree (cheap coarse internal nodes; at every fully named leaf: rule CC -> no-room + pockets -> basin clip -> Rule NS -> the exact cascade last; pad 0 first); NO LP" % doc["nid"], 12, "#000", True),
            text(20, 36, "per run: the ROOT panel, then one panel per closed branch (first %d); blue = pins; black = H (thin = pieces, filled = certified K'); coloured = instantiated meeters; grey stipple = alive cells of the anonymous option table (never green); yellow = the count's witness" % MAXP, 8, "#444"),
            text(20, 48, "read-only from certs/coarsetree211_%s.json (record %s); rendered %s" % (doc["nid"], doc.get("record"), time.strftime("%Y-%m-%d %H:%M:%S")), 8, "#444")]
    y = wrap(body, 20, 62, stage_lines(doc), 300) + 4
    for key, d in (doc.get("runs") or {}).items():
        pad = d.get("pad")
        nodes = [n for n in (d.get("nodes") or []) if n.get("snapshot")]
        show = nodes[:1] + [n for n in nodes[1:] if n.get("verdict") in ("DEAD", "ALIVE")][:MAXP - 1]
        nrow = max(1, (len(show) + ncol - 1) // ncol)
        y = wrap(body, 20, y + 10, run_head(doc, key, d), 300) + 4
        ys = F5.side(dict(doc, pads={pad: d}), pad, body, 20 + ncol * PW + 10, y + 12)
        for k, n in enumerate(show):
            ox, oy = 20 + (k % ncol) * PW, y + (k // ncol) * (S0 * S + NH + 12)
            panel(doc, dict(n["snapshot"], pad=pad), body, ox, oy, S, small=False)
            wrap(body, ox, oy + S0 * S + 10, node_note(n), 80)
        y = max(y + nrow * (S0 * S + NH + 12) + 30, ys + 20)
    W = 20 + ncol * PW + 10 + 1000
    return "\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (W, y + 20), defs()] + body + ["</svg>"])


def render(doc):
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, "coarsetree211_%s.svg" % doc["nid"])
    open(p, "w", encoding="utf-8").write(page_svg(doc))
    return p


def gallery():
    S = 52
    PW = int(S0 * S) + 16
    PH = PW + 44
    ncol = 6
    docs = []
    for f in sorted(glob.glob(os.path.join(CERTS, "coarsetree211_*.json"))):
        try:
            docs.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            continue
    body = [text(16, 20, "A211 coarsetree211 -- the coarse tree over the alive k5 pages and the k5 frontier, one thumbnail per node (red = DEAD at the window pad, green = ALIVE; the pad-0 verdict beside it); rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 12, "#000", True)]
    for k, doc in enumerate(docs):
        runs = doc.get("runs") or {}
        v = doc.get("verdicts") or {}
        first = next(iter(runs.values()), {}) if runs else {}
        nodes = [n for n in (first.get("nodes") or []) if n.get("snapshot")]
        ox, oy = 16 + (k % ncol) * PW, 40 + (k // ncol) * PH
        if nodes:
            panel(doc, dict(nodes[0]["snapshot"], pad=first.get("pad")), body, ox, oy, S, small=True)
        dead = v.get("g1") == "DEAD"
        body.append(text(ox, oy + S0 * S + 11, doc["nid"].replace("_interior", ""), 8, "#000", True))
        body.append(text(ox, oy + S0 * S + 21, ("g1 %s | pad0 %s" % (v.get("g1", "-"), v.get("zero", "-")))[:60], 6.5, "#c62828" if dead else "#2e7d32"))
        body.append(text(ox, oy + S0 * S + 31, ("stage %s; %s nodes" % (doc.get("stage_reached"), sum(int(r.get("n_nodes") or 0) for r in runs.values())))[:60], 6.5, "#555"))
    nrow = max(1, (len(docs) + ncol - 1) // ncol)
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, "coarsetree211_gallery.svg")
    open(p, "w", encoding="utf-8").write("\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (ncol * PW + 32, 40 + nrow * PH), defs()] + body + ["</svg>"]))
    return p


if __name__ == "__main__":
    if sys.argv[1] == "gallery":
        print(gallery())
    else:
        print(render(json.load(open(os.path.join(CERTS, "coarsetree211_%s.json" % sys.argv[1]), encoding="utf-8"))))
