#!/usr/bin/env python3
"""Render lean/depgraph.json as a layered SVG (lean/depgraph.svg).

LIVE monitoring copy (promoted from A62/A63 per PI request 2026-09-02): the advisor
updates depgraph.json labels/notes as milestones land and re-runs this script.
Stdlib only. Layout: fixed layers by node id; any node NOT named in LAYERS is
appended to a trailing "new / unplaced" row so additions never vanish silently.

Edge routing (PI requests 2026-09-02, "circuit" revision):
 - BUS TRUNKS: all edges from one source to targets in one row share a single
   trunk wire — one drop per source, one lateral run on a lane unique to the
   trunk within each row-gap, then arrowed drops into each target ("one wire per
   voltage", as the PI put it).
 - PORTS: connection points are spread along a node's top/bottom edge (sorted by
   the far end's x), so verticals leaving/entering one node never stack.
 - Corridor crossings are deduplicated per row (min 8 px apart), so long trunks
   crossing the same corridor don't overlap.
 - Node status: colour = label; a DASHED node outline means "blocked_only" —
   the node's own work is done, it waits only on open dependencies.
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
LAYERS = [[nid for nid in layer if nid in nodes] for layer in LAYERS]

W, ROW_H, NH = 1720, 150, 54
H = ROW_H * len(LAYERS) + 130
pos, width, rowof = {}, {}, {}
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

# ---------- geometry helpers ----------
GAP_PAD = 10

def row_y(r):
    return 70 + r * ROW_H

def gap_bounds(g):
    return (row_y(g) + NH / 2 + GAP_PAD, row_y(g + 1) - NH / 2 - GAP_PAD)

def corridors(r):
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

used_crossings = []  # x already used by ANY row crossing (global: adjacent-row
                     # crossings at one x share vertical space in their common gap)

def corridor_x(r, want):
    """Nearest usable crossing x in row r to `want`, >=8px from ALL prior crossings."""
    cands = []
    for lo, hi in corridors(r):
        base = min(max(want, lo + 6), hi - 6)
        for off in range(0, 400, 8):
            for x in (base + off, base - off):
                if lo + 6 <= x <= hi - 6:
                    cands.append((abs(x - want), x))
                    if all(abs(x - u) >= 8 for u in used_crossings):
                        used_crossings.append(x)
                        return x
    # every slot taken: pick the candidate farthest from existing crossings
    if cands:
        x = max(cands, key=lambda c: min((abs(c[1] - u) for u in used_crossings), default=1e9))[1]
    else:
        x = want
    used_crossings.append(x)
    return x

# ---------- group edges into trunks ----------
edges = [e for e in G["edges"] if e["from"] in pos and e["to"] in pos]
trunks = {}   # (from, target_row, kind) -> list of targets
arcs = []     # same-row edges, kept individual
for e in edges:
    r1, r2 = rowof[e["from"]], rowof[e["to"]]
    if r1 == r2:
        arcs.append(e)
    else:
        trunks.setdefault((e["from"], r2, e["kind"]), []).append(e["to"])
trunk_list = sorted(trunks.items(), key=lambda kv: (rowof[kv[0][0]], pos[kv[0][0]][0]))

# lane allocation: one lane per trunk per gap it crosses
gap_members = {}
for ti, ((src, r2, kind), tgts) in enumerate(trunk_list):
    r1 = rowof[src]
    for g in range(min(r1, r2), max(r1, r2)):
        gap_members.setdefault(g, []).append(ti)
lane_y = {}
for g, tis in gap_members.items():
    tis.sort(key=lambda ti: min([pos[trunk_list[ti][0][0]][0]] +
                                [pos[t][0] for t in trunk_list[ti][1]]))
    top, bot = gap_bounds(g)
    for k, ti in enumerate(tis):
        lane_y[(ti, g)] = top + (k + 1) * (bot - top) / (len(tis) + 1)

# ---------- ports: spread stubs along node top/bottom edges ----------
stubs = {}  # (nid, 'top'|'bot') -> list of (sort_x, key)

def reg_stub(nid, side, sort_x, key):
    stubs.setdefault((nid, side), []).append((sort_x, key))

for ti, ((src, r2, kind), tgts) in enumerate(trunk_list):
    down = r2 > rowof[src]
    med = sorted(pos[t][0] for t in tgts)[len(tgts) // 2]
    reg_stub(src, "bot" if down else "top", med, ("T", ti))
    for t in tgts:
        reg_stub(t, "top" if down else "bot", pos[src][0], ("D", ti, t))
for ai, e in enumerate(arcs):
    r = rowof[e["from"]]
    side = "top" if r == len(LAYERS) - 1 else "bot"
    reg_stub(e["from"], side, pos[e["to"]][0], ("A", ai, "f"))
    reg_stub(e["to"], side, pos[e["from"]][0], ("A", ai, "t"))

port_x = {}
for (nid, side), lst in stubs.items():
    lst.sort()
    x, nw = pos[nid][0], width[nid]
    n = len(lst)
    for k, (_, key) in enumerate(lst):
        port_x[(nid, side) + (key,)] = x - nw / 2 + (k + 1) * nw / (n + 1)

# same-row arc depths (nested by span)
arc_depth = {}
by_row = {}
for ai, e in enumerate(arcs):
    by_row.setdefault(rowof[e["from"]], []).append(ai)
for r, ais in by_row.items():
    ais.sort(key=lambda ai: abs(pos[arcs[ai]["from"]][0] - pos[arcs[ai]["to"]][0]))
    for k, ai in enumerate(ais):
        arc_depth[ai] = 16 + 12 * k

# ---------- render ----------
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
lx = 12
for lab, col in COLORS.items():
    c = counts.get(lab, 0)
    txt = f"{lab} ({c})"
    out.append(f'<rect x="{lx}" y="32" width="12" height="12" fill="{col}" rx="2"/>')
    out.append(f'<text x="{lx+16}" y="42">{txt}</text>')
    lx += 30 + 7 * len(txt)
out.append(f'<rect x="{lx+10}" y="32" width="12" height="12" fill="none" stroke="#c62828" stroke-width="1.6" stroke-dasharray="4,3" rx="2"/>')
out.append(f'<text x="{lx+26}" y="42">dashed outline = own work done, waiting only on dependencies &#183; '
           f'one wire per source&#8594;row, arrows at each dependency &#183; hover for details</text>')

for r, t in enumerate(LAYER_TITLES):
    out.append(f'<text x="8" y="{row_y(r) - NH/2 - 8}" font-size="10" fill="#888" font-style="italic">{html.escape(t)}</text>')

def fmt(p):
    return f'{p[0]:.0f} {p[1]:.0f}'

# trunks
for ti, ((src, r2, kind), tgts) in enumerate(trunk_list):
    r1 = rowof[src]
    down = r2 > r1
    step = 1 if down else -1
    dash = ' stroke-dasharray="5,4"' if kind == "motivation" else ""
    col = "#bbb" if kind == "motivation" else "#666"
    marker = "arrm" if kind == "motivation" else "arr"
    sx = port_x[(src, "bot" if down else "top", ("T", ti))]
    sy = pos[src][1] + (NH / 2 if down else -NH / 2)
    pts = [(sx, sy)]
    cx, r = sx, r1
    # travel to the gap adjacent to the target row
    while True:
        g = r if down else r - 1
        ly = lane_y[(ti, g)]
        nxt = r + step
        if nxt == r2:
            pts.append((cx, ly))
            final_ly = ly
            break
        nx = corridor_x(nxt, sorted(pos[t][0] for t in tgts)[len(tgts) // 2])
        pts.append((cx, ly))
        pts.append((nx, ly))
        cx, r = nx, nxt
    # bus span on the final lane
    drop_xs = [port_x[(t, "top" if down else "bot", ("D", ti, t))] for t in tgts]
    lo, hi = min(drop_xs + [cx]), max(drop_xs + [cx])
    tip = f'{html.escape(src)} &#8594; {", ".join(html.escape(t) for t in sorted(tgts))} ({kind})'
    trunk_path = 'M ' + ' L '.join(fmt(p) for p in pts)
    trunk_path += f' M {lo:.0f} {final_ly:.0f} L {hi:.0f} {final_ly:.0f}'
    out.append(f'<g><title>{tip}</title>')
    out.append(f'<path d="{trunk_path}" fill="none" stroke="{col}" stroke-width="1.2"{dash} '
               f'opacity="0.7" stroke-linejoin="round"/>')
    for t, dx in zip(tgts, drop_xs):
        ty = pos[t][1] - (NH / 2 if down else -NH / 2)
        out.append(f'<path d="M {dx:.0f} {final_ly:.0f} L {dx:.0f} {ty:.0f}" fill="none" '
                   f'stroke="{col}" stroke-width="1.2"{dash} opacity="0.7" marker-end="url(#{marker})"/>')
    out.append('</g>')

# same-row arcs
for ai, e in enumerate(arcs):
    r = rowof[e["from"]]
    dash = ' stroke-dasharray="5,4"' if e["kind"] == "motivation" else ""
    col = "#bbb" if e["kind"] == "motivation" else "#666"
    marker = "arrm" if e["kind"] == "motivation" else "arr"
    last = r == len(LAYERS) - 1
    side = "top" if last else "bot"
    x1 = port_x[(e["from"], side, ("A", ai, "f"))]
    x2 = port_x[(e["to"], side, ("A", ai, "t"))]
    ya = pos[e["from"]][1] + (-NH / 2 if last else NH / 2)
    yc = ya + (-1 if last else 1) * (arc_depth[ai] + GAP_PAD)
    tip = f'{html.escape(e["from"])} &#8594; {html.escape(e["to"])} ({e["kind"]})'
    out.append(f'<g><title>{tip}</title>'
               f'<path d="M {x1:.0f} {ya:.0f} C {x1:.0f} {yc:.0f} {x2:.0f} {yc:.0f} {x2:.0f} {ya:.0f}" '
               f'fill="none" stroke="{col}" stroke-width="1.2"{dash} opacity="0.7" marker-end="url(#{marker})"/></g>')

# nodes
for nid, (x, y) in pos.items():
    n = nodes[nid]
    NW = width[nid]
    col = COLORS[n["label"]]
    blocked = n.get("blocked_only", False)
    node_dash = ' stroke-dasharray="7,4"' if blocked else ""
    title = html.escape(n["title"])
    note = html.escape(n.get("note", ""))
    status = n["label"] + (" — own work done; waiting on dependencies" if blocked else "")
    out.append(f'<g><title>{html.escape(nid)} — {title}&#10;[{status}]&#10;{note}</title>')
    out.append(f'<rect x="{x-NW/2:.0f}" y="{y-NH/2:.0f}" width="{NW:.0f}" height="{NH}" rx="7" fill="white"/>')
    out.append(f'<rect x="{x-NW/2:.0f}" y="{y-NH/2:.0f}" width="{NW:.0f}" height="{NH}" rx="7" '
               f'fill="{col}" fill-opacity="0.13" stroke="{col}" stroke-width="1.6"{node_dash}/>')
    out.append(f'<text x="{x:.0f}" y="{y-NH/2+15:.0f}" text-anchor="middle" font-weight="bold" fill="{col}">{html.escape(nid)}</text>')
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
print("wrote", os.path.join(HERE, "depgraph.svg"),
      f"({len(trunk_list)} trunks for {len(edges)-len(arcs)} cross-row edges, {len(arcs)} arcs)")
