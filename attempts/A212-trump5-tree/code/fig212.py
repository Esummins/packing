"""A212 -- the page (fig211's layout on A212's certificate) with the GATE decision and the TUBE leaf on every panel note, pad 0
only; pages docs/residue_map/campaigns/A212-trump5tree/trump5tree212_<nid>.svg + trump5tree212_gallery.svg.
   python fig212.py <nid> | gallery"""
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CERTS = os.path.join(HERE, "..", "certs")
OUTD = os.path.join(ROOT, "docs", "residue_map", "campaigns", "A212-trump5tree")
sys.path.insert(0, HERE)
import fig204 as F4                                            # noqa: E402
import fig211 as F11                                           # noqa: E402

S0, text, defs, panel = F4.S0, F4.text, F4.defs, F4.panel
_NOTE211, _STAGE211 = F11.node_note, F11.stage_lines


def node_note(n):
    L = list(_NOTE211(n))
    tg = n.get("trump_gate") or {}
    if tg.get("contains"):
        L.append(("GATE: this node CONTAINS the Trump image %s (assignment %s; pins %s): no kill rule applied here -- branched only (notes/trump5_tree.md s.1)" % (
            tg.get("g"), tg.get("assignment"), tg.get("pins")), 6.5, "#6a1b9a", True))
    elif tg:
        L.append(("GATE: no D4 image of z-hat satisfies this node (%s; %s s): the kill rules apply" % (
            (tg.get("checks") or [{}])[0].get("fail") if tg.get("checks") else "-", tg.get("seconds")), 6.5, "#555", False))
    if n.get("gate_conflict"):
        L.append(("GATE-CONFLICT: %s claimed DEAD on a gated node -- refused, ALIVE: %s" % (n["gate_conflict"].get("rule"), str(n.get("reason"))[:200]), 6.5, "#e65100", True))
    if n.get("verdict") == "TRUMP-TUBE":
        tb = n.get("tube") or {}
        L.append(("TRUMP-TUBE leaf (Lemma TUBE-LEAF, s.2; NOT a kill): all 11 squares named, every piece inside the tube box r_c' %s / r_theta %s about image %s (%s); %s aligned cuts; worst role %s" % (
            tb.get("r_c_eff_float"), (tb.get("radii") or {}).get("r_theta"), tb.get("g"), (tb.get("radii") or {}).get("cert"), n.get("tube_depth"), tb.get("worst")), 6.5, "#1b5e20", True))
    elif n.get("tube"):
        tb = n["tube"]
        L.append(("tube check: NOT fitted -- worst %s; per role %s" % (tb.get("worst"), {k: (round(v.get("dx", 0), 4), round(v.get("dy", 0), 4), round(v.get("dt_deg", 0), 3)) for k, v in (tb.get("roles") or {}).items() if not k.startswith("P")}), 6.5, "#6a1b9a", False))
    if (n.get("rsplit") or {}).get("aligned"):
        r = n["rsplit"]
        L.append(("ALIGNED split (s.3): %s cut on %s at the tube wall %s (excess %s x radius; the image on the %s side) -- both halves below" % (r.get("role"), r.get("dim"), r.get("m"), r.get("excess"), r.get("side")), 6.5, "#1565c0", True))
    return L


def stage_lines(doc):
    L = []
    for pad, s in (doc.get("stage0") or {}).items():
        col = "#c62828" if s.get("verdict") == "DEAD" else "#2e7d32"
        L.append(("STAGE 0 (pad 0): %s -- %s [%s; kills %s; CSP units alive %s/%s; %s s]%s" % (
            s.get("verdict"), s.get("source"), s.get("file"), s.get("kills"), s.get("n_units_alive"), s.get("n_units"), s.get("seconds"), ("; " + str(s.get("leaf"))[:160]) if s.get("leaf") else ""), 8, col, True))
    v = (doc.get("verdicts") or {}).get("zero", "not run")
    g = ((doc.get("runs") or {}).get("zero_page") or {}).get("gate_root") or {}
    col = "#c62828" if v == "DEAD" else ("#1b5e20" if v == "TRUMP-TUBE" else "#2e7d32")
    L.append(("VERDICT (pad 0, lam = 1, s0-only): %s   [DEAD = every branch killed at s0; TRUMP-TUBE = every branch DEAD or a tube leaf: the residue is the Trump basin (uniqueness by Theorem T1); ALIVE = undecided]; root gate: %s" % (
        v, ("contains %s" % g.get("g")) if g.get("contains") else "no image"), 9, col, True))
    return L


def render(doc):
    F11.node_note, F11.stage_lines = node_note, stage_lines
    os.makedirs(OUTD, exist_ok=True)
    svg = F11.page_svg(doc)
    svg = svg.replace("A211 coarsetree211: the COARSE tree", "A212 trump5tree212: the TRUMP5 tree (A211's coarse tree + the Trump-containment GATE + the TUBE leaf + the aligned split; pad 0 only)", 1)
    svg = svg.replace("certs/coarsetree211_%s.json" % doc["nid"], "certs/trump5tree212_%s.json" % doc["nid"])
    p = os.path.join(OUTD, "trump5tree212_%s.svg" % doc["nid"])
    open(p, "w", encoding="utf-8").write(svg)
    return p


def gallery():
    S = 52
    PW = int(S0 * S) + 16
    PH = PW + 44
    ncol = 6
    docs = []
    for f in sorted(glob.glob(os.path.join(CERTS, "trump5tree212_*.json"))):
        try:
            docs.append(json.load(open(f, encoding="utf-8")))
        except Exception:
            continue
    body = [text(16, 20, "A212 trump5tree212 -- the trump5 tree over the 13 alive trump5 gallery pages and A60's frontier (pad 0; red = DEAD, dark green = TRUMP-TUBE, green = ALIVE); rendered %s" % time.strftime("%Y-%m-%d %H:%M:%S"), 12, "#000", True)]
    for k, doc in enumerate(docs):
        runs = doc.get("runs") or {}
        v = (doc.get("verdicts") or {}).get("zero", "-")
        first = next(iter(runs.values()), {}) if runs else {}
        nodes = [n for n in (first.get("nodes") or []) if n.get("snapshot")]
        ox, oy = 16 + (k % ncol) * PW, 40 + (k // ncol) * PH
        if nodes:
            panel(doc, dict(nodes[0]["snapshot"], pad=first.get("pad")), body, ox, oy, S, small=True)
        col = "#c62828" if v == "DEAD" else ("#1b5e20" if v == "TRUMP-TUBE" else "#2e7d32")
        body.append(text(ox, oy + S0 * S + 11, doc["nid"], 8, "#000", True))
        body.append(text(ox, oy + S0 * S + 21, ("pad0 %s; gate %s" % (v, "yes" if (first.get("gate_root") or {}).get("contains") else "no"))[:60], 6.5, col))
        body.append(text(ox, oy + S0 * S + 31, ("%s nodes; %s gated; %s tube" % (first.get("n_nodes"), first.get("gate_hits"), first.get("tube_leaves")))[:60], 6.5, "#555"))
    nrow = max(1, (len(docs) + ncol - 1) // ncol)
    os.makedirs(OUTD, exist_ok=True)
    p = os.path.join(OUTD, "trump5tree212_gallery.svg")
    open(p, "w", encoding="utf-8").write("\n".join(['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, sans-serif" style="background:#fff">' % (ncol * PW + 32, 40 + nrow * PH), defs()] + body + ["</svg>"]))
    return p


if __name__ == "__main__":
    if sys.argv[1] == "gallery":
        print(gallery())
    else:
        print(render(json.load(open(os.path.join(CERTS, "trump5tree212_%s.json" % sys.argv[1]), encoding="utf-8"))))
