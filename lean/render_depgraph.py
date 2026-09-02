#!/usr/bin/env python3
"""Render lean/depgraph.json as a layered SVG (lean/depgraph.svg).

LIVE monitoring copy (promoted from A62/A63 per PI request 2026-09-02): the advisor
updates depgraph.json labels/notes as milestones land and re-runs this script.
Stdlib only. Layout: fixed layers by node id; any node NOT named in LAYERS is
appended to a trailing "new / unplaced" row so additions never vanish silently.
Node colour = label; dashed edge = motivation.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "depgraph.json"), encoding="utf-8"))

COLORS = {
    "proved-prose": "#2e7d32",          # green
    "certificate+verifier": "#1565c0",  # blue
    "cited": "#6a1b9a",                 # purple
    "conjecture": "#e65100",            # orange
    "open": "#c62828",                  # red
}

# layers top->bottom
LAYERS = [
    ["TOP"],
    ["A.D1", "A.PARAM", "A.LB382", "A.S3", "A.UBshat", "A.UNIQ", "A.SBRIDGE", "A.THMU"],
    ["B.SEL", "B.CENSUS", "B.K1", "B.EXACT", "C.WIN"],
    ["C.K61", "C.A57", "C.K4TIER", "C.CC2", "C.T5T11", "C.M1", "C.A61"],
    ["D.TREE", "D.N1", "D.TRAP", "D.P1", "D.LADDER", "D.ALIVE", "D.SLAB", "D.D4", "D.S6", "D.TAUK"],
    ["A.F2", "V.MEAS", "V.CASE", "V.PARAM", "E.A36", "E.A22", "E.COORD", "E.IV"],
    ["X.IL19", "X.S3BDBFS", "X.ATLAS", "X.CSTAR", "X.GA531"],
]
LAYER_TITLES = [
    "top-level theorem (TopLevel.lean)",
    "frame: attainment / parametrisation / bounds / uniqueness / bridges",
    "stratification layer",
    "per-stratum kills + window transfer",
    "trump5 residual (A59/A60)",
    "verifier soundness + rigidity trust chain",
    "off-tree (motivation only; H11 sweep)",
]

nodes = {n["id"]: n for n in G["nodes"]}
placed = {nid for layer in LAYERS for nid in layer}
unplaced = [nid for nid in nodes if nid not in placed]
if unplaced:
    LAYERS.append(unplaced)
    LAYER_TITLES.append("new / unplaced (assign a layer in render_depgraph.py)")
# drop ids named in LAYERS but absent from the json (renamed/retired nodes)
LAYERS = [[nid for nid in layer if nid in nodes] for layer in LAYERS]

W, ROW_H, NH = 1720, 118, 54
H = ROW_H * len(LAYERS) + 130
pos = {}
width = {}
for r, layer in enumerate(LAYERS):
    n = max(1, len(layer))
    gap = W / (n + 1)
    nw = min(196, gap * 0.94)
    for k, nid in enumerate(layer):
        pos[nid] = ((k + 1) * gap, 70 + r * ROW_H)
        width[nid] = nw

counts = {}
for n in G["nodes"]:
    counts[n["label"]] = counts.get(n["label"], 0) + 1

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'font-family="Segoe UI, sans-serif" font-size="11">')
out.append(f'<rect width="{W}" height="{H}" fill="white"/>')
out.append(f'<text x="12" y="22" font-size="15" font-weight="bold">s(11) optimality — lemma dependency graph '
           f'(live; base commit {G["meta"]["commit"][:8]}, updated {G["meta"]["date"]})</text>')
# legend with live counts
lx = 12
for lab, col in COLORS.items():
    c = counts.get(lab, 0)
    txt = f"{lab} ({c})"
    out.append(f'<rect x="{lx}" y="32" width="12" height="12" fill="{col}" rx="2"/>')
    out.append(f'<text x="{lx+16}" y="42">{txt}</text>')
    lx += 30 + 7 * len(txt)
out.append(f'<text x="{lx+10}" y="42">solid edge = uses (load-bearing) &#183; dashed = motivation only</text>')

# layer titles
for r, t in enumerate(LAYER_TITLES):
    y = 70 + r * ROW_H - NH / 2 - 6
    out.append(f'<text x="8" y="{y}" font-size="10" fill="#888" font-style="italic">{html.escape(t)}</text>')

# edges under nodes
for e in G["edges"]:
    if e["from"] not in pos or e["to"] not in pos:
        continue
    (x1, y1), (x2, y2) = pos[e["from"]], pos[e["to"]]
    dash = ' stroke-dasharray="5,4"' if e["kind"] == "motivation" else ""
    col = "#bbb" if e["kind"] == "motivation" else "#666"
    midy = (y1 + y2) / 2
    out.append(f'<path d="M {x1:.0f} {y1:.0f} C {x1:.0f} {midy:.0f} {x2:.0f} {midy:.0f} {x2:.0f} {y2:.0f}" '
               f'fill="none" stroke="{col}" stroke-width="1.1"{dash} opacity="0.75"/>')

# nodes
for nid, (x, y) in pos.items():
    n = nodes[nid]
    NW = width[nid]
    col = COLORS[n["label"]]
    title = html.escape(n["title"])
    note = html.escape(n.get("note", ""))
    out.append(f'<g><title>{html.escape(nid)} — {title}&#10;[{n["label"]}]&#10;{note}</title>')
    out.append(f'<rect x="{x-NW/2:.0f}" y="{y-NH/2:.0f}" width="{NW:.0f}" height="{NH}" rx="7" '
               f'fill="{col}" fill-opacity="0.13" stroke="{col}" stroke-width="1.6"/>')
    out.append(f'<text x="{x:.0f}" y="{y-NH/2+15:.0f}" text-anchor="middle" font-weight="bold" fill="{col}">{html.escape(nid)}</text>')
    # wrap the title into <=2 lines scaled to the node width
    maxc = max(16, int(NW / 5.9))
    words, lines, cur = n["title"].split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > maxc and cur:
            lines.append(cur); cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    for j, ln in enumerate(lines[:2]):
        if j == 1 and len(lines) > 2:
            ln = ln[:30] + "…"
        out.append(f'<text x="{x:.0f}" y="{y-NH/2+29+j*12:.0f}" text-anchor="middle" fill="#222">{html.escape(ln)}</text>')
    out.append('</g>')

out.append('</svg>')
open(os.path.join(HERE, "depgraph.svg"), "w", encoding="utf-8").write("\n".join(out))
print("wrote", os.path.join(HERE, "depgraph.svg"))
