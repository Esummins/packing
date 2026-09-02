#!/usr/bin/env python3
"""Render lean/depgraph.json as a layered SVG (lean/depgraph.svg).

LIVE monitoring copy (promoted from A62/A63 per PI request 2026-09-02): the advisor
updates depgraph.json labels/notes as milestones land and re-runs this script.
Stdlib only. Layout: fixed layers by node id; any node NOT named in LAYERS is
appended to a trailing "new / unplaced" row so additions never vanish silently.
Node colour = label; dashed edge = motivation.

Edge routing (PI request 2026-09-02): orthogonal with per-gap lanes.
 - Same-row edges arc into the gap below the row (or above, for the last row).
 - Cross-row edges run vertically from the node, laterally along a lane y that is
   UNIQUE to that edge within each row-gap it crosses, and vertically into the
   target; multi-row edges cross intermediate rows through corridors between the
   node boxes, never through them.
 - Arrowheads point at the dependency (from USES to); hover an edge for its ends.
"""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "depgraph.json"), encoding="utf-8"))

COLORS = {
    "lean-proved": "#b8860b",           # gold — a Lean THEOREM (statement + proof in lean/)
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

W, ROW_H, NH = 1720, 150, 54
H = ROW_H * len(LAYERS) + 130
pos = {}
width = {}
rowof = {}
for r, layer in enumerate(LAYERS):
    n = max(1, len(layer))
    gap = W / (n + 1)
    nw = min(196, gap * 0.94)
    for k, nid in enumerate(layer):
        pos[nid] = ((k + 1) * gap, 70 + r * ROW_H)
        width[nid] = nw
        rowof[nid] = r

counts = {}
for n in G["nodes"]:
    counts[n["label"]] = counts.get(n["label"], 0) + 1

# ---------- edge routing ----------
GAP_TOP_PAD, GAP_BOT_PAD = 10, 10

def row_y(r):
    return 70 + r * ROW_H

def gap_bounds(g):
    """Free vertical band between row g and row g+1."""
    top = row_y(g) + NH / 2 + GAP_TOP_PAD
    bot = row_y(g + 1) - NH / 2 - GAP_BOT_PAD
    return top, bot

def corridors(r):
    """Free x-intervals between node boxes of row r (margins included)."""
    iv = sorted((pos[nid][0] - width[nid] / 2 - 8, pos[nid][0] + width[nid] / 2 + 8)
                for nid in LAYERS[r])
    out, cur = [], 8
    for lo, hi in iv:
        if lo - cur >= 14:
            out.append((cur, lo))
        cur = max(cur, hi)
    if W - 8 - cur >= 14:
        out.append((cur, W - 8))
    return out

def corridor_x(r, want):
    """Nearest usable crossing x in row r's corridors to `want`."""
    best, bd = want, float("inf")
    for lo, hi in corridors(r):
        x = min(max(want, lo + 6), hi - 6)
        d = abs(x - want)
        if d < bd:
            best, bd = x, d
    return best

edges = [e for e in G["edges"] if e["from"] in pos and e["to"] in pos]

# lane allocation: every cross-row edge gets its own lane index in each gap it crosses
gap_edges = {}
for i, e in enumerate(edges):
    r1, r2 = rowof[e["from"]], rowof[e["to"]]
    if r1 == r2:
        continue
    for g in range(min(r1, r2), max(r1, r2)):
        gap_edges.setdefault(g, []).append(i)
lane_y = {}  # (edge_index, gap) -> y
for g, eis in gap_edges.items():
    eis.sort(key=lambda i: min(pos[edges[i]["from"]][0], pos[edges[i]["to"]][0]))
    top, bot = gap_bounds(g)
    n = len(eis)
    for k, i in enumerate(eis):
        lane_y[(i, g)] = top + (k + 1) * (bot - top) / (n + 1)

# same-row arcs: rank per row by span so nested arcs don't coincide
row_arcs = {}
for i, e in enumerate(edges):
    r1, r2 = rowof[e["from"]], rowof[e["to"]]
    if r1 == r2:
        row_arcs.setdefault(r1, []).append(i)
arc_depth = {}
for r, eis in row_arcs.items():
    eis.sort(key=lambda i: abs(pos[edges[i]["from"]][0] - pos[edges[i]["to"]][0]))
    for k, i in enumerate(eis):
        arc_depth[i] = 16 + 12 * k

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'font-family="Segoe UI, sans-serif" font-size="11">')
out.append('<defs>'
           '<marker id="arr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#666"/></marker>'
           '<marker id="arrm" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#bbb"/></marker>'
           '</defs>')
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
out.append(f'<text x="{lx+10}" y="42">arrow points at the dependency &#183; solid = uses &#183; dashed = motivation &#183; hover an edge for its ends</text>')

# layer titles
for r, t in enumerate(LAYER_TITLES):
    y = row_y(r) - NH / 2 - 8
    out.append(f'<text x="8" y="{y}" font-size="10" fill="#888" font-style="italic">{html.escape(t)}</text>')

# ---------- edges (under nodes) ----------
def fmt(p):
    return f'{p[0]:.0f} {p[1]:.0f}'

for i, e in enumerate(edges):
    a, b = e["from"], e["to"]
    (x1, y1), (x2, y2) = pos[a], pos[b]
    r1, r2 = rowof[a], rowof[b]
    dash = ' stroke-dasharray="5,4"' if e["kind"] == "motivation" else ""
    col = "#bbb" if e["kind"] == "motivation" else "#666"
    marker = "arrm" if e["kind"] == "motivation" else "arr"
    tip = f'{html.escape(a)} &#8594; {html.escape(b)} ({e["kind"]})'
    if r1 == r2:
        # arc through the gap below (above, for the bottom row)
        d = arc_depth[i]
        if r1 == len(LAYERS) - 1:
            ya = y1 - NH / 2
            yc = ya - d - GAP_TOP_PAD
        else:
            ya = y1 + NH / 2
            yc = ya + d + GAP_TOP_PAD
        path = f'M {x1:.0f} {ya:.0f} C {x1:.0f} {yc:.0f} {x2:.0f} {yc:.0f} {x2:.0f} {ya:.0f}'
    else:
        down = r2 > r1
        step = 1 if down else -1
        pts = [(x1, y1 + (NH / 2 if down else -NH / 2))]
        cx = x1
        r = r1
        while r != r2:
            g = r if down else r - 1
            ly = lane_y[(i, g)]
            nxt = r + step
            nx = x2 if nxt == r2 else corridor_x(nxt, x2)
            pts.append((cx, ly))
            pts.append((nx, ly))
            cx = nx
            r = nxt
        pts.append((x2, y2 - (NH / 2 if down else -NH / 2)))
        path = 'M ' + ' L '.join(fmt(p) for p in pts)
    out.append(f'<g><title>{tip}</title>'
               f'<path d="{path}" fill="none" stroke="{col}" stroke-width="1.2"{dash} '
               f'opacity="0.7" stroke-linejoin="round" marker-end="url(#{marker})"/></g>')

# ---------- nodes ----------
for nid, (x, y) in pos.items():
    n = nodes[nid]
    NW = width[nid]
    col = COLORS[n["label"]]
    title = html.escape(n["title"])
    note = html.escape(n.get("note", ""))
    out.append(f'<g><title>{html.escape(nid)} — {title}&#10;[{n["label"]}]&#10;{note}</title>')
    out.append(f'<rect x="{x-NW/2:.0f}" y="{y-NH/2:.0f}" width="{NW:.0f}" height="{NH}" rx="7" '
               f'fill="white"/>')
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
