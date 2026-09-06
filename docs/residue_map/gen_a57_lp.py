"""Draw the LP output directly (PI, 2026-09-06): for each alive A57 node, the LP's dual-support placements ('packing':
placements with positive dual weight y) as squares, opacity by weight, overlaps allowed — the phase-space point the LP
search stalled at. Read-only on A57. Every drawn square is checked for containment (admissibility)."""
import json, math, os, glob, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
A57 = os.path.join(R, 'attempts', 'A57-shadow-trees')
S0 = 969271 / 250000
def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5*(dx*c - dy*s_), cy + 0.5*(dx*s_ + dy*c)) for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def esc(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'
S = 140
def find_node(nid):
    for p in glob.glob(os.path.join(A57, 'results', 'tree', '*', nid + '.json')) + glob.glob(os.path.join(A57, 'results', 'nodes', nid + '.json')):
        return json.load(open(p, encoding='utf-8')), p
    return None, None
def row_of(nid):
    for f in glob.glob(os.path.join(A57, 'results', 'tree_k5_11_interior_G1*.jsonl')):
        for l in open(f, encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if r.get('id') == nid: return r
    return {}
def panel(ox, oy, nid, node, row):
    from fractions import Fraction
    cores = (node.get('hyp') or {}).get('cores', [])
    pins = []
    for c in cores:
        try: pins.append((float(Fraction(str(c['kx']))), float(Fraction(str(c['ky'])))))
        except Exception: pass
    pk = node.get('packing', [])
    # gaps: pairwise SAT among placements, and to each core centre (axis-aligned pins; the conditioned core drawn from its box)
    def sat(p, q):
        axes = []
        for poly_ in (p, q):
            for i in range(4):
                a, b = poly_[i], poly_[(i+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; n = math.hypot(ex, ey); axes.append((-ey/n, ex/n))
        best = -9
        for ax in axes:
            pp = [x*ax[0]+y*ax[1] for x, y in p]; qq = [x*ax[0]+y*ax[1] for x, y in q]
            best = max(best, min(qq)-max(pp), min(pp)-max(qq))
        return best
    polys = [sq(float(p['cx']), float(p['cy']), float(p['theta'])) for p in pk]
    gaps = [(sat(polys[i], polys[j]), i, j) for i in range(len(polys)) for j in range(i+1, len(polys))]
    worst_pair = min(gaps) if gaps else (0, -1, -1)
    pin_polys = [sq(cx, cy, 0.0) for cx, cy in pins[:5]]
    worst_pin = min([(sat(P, Q), i) for i, P in enumerate(polys) for Q in pin_polys] or [(0, -1)])
    print(f'  {nid}: placements {len(pk)}, weights {[round(float(p.get("y",0)),3) for p in pk]}, worst pairwise SAT gap {worst_pair[0]:+.4f} (placements {worst_pair[1]},{worst_pair[2]}), worst gap to a pin {worst_pin[0]:+.4f}')
    for i, p in enumerate(pk): print(f'     {i}: ({float(p["cx"]):.4f}, {float(p["cy"]):.4f}, {math.degrees(float(p["theta"]))%90:.2f} deg) y={float(p.get("y",0)):.3f}')
    ys = [float(p.get('y', 0)) for p in pk]; ymax = max(ys) if ys else 1.0
    box = row.get('box', {})
    out = [text(ox, oy - S0*S - 26, f'{nid.replace("k5_11_interior_", "")}: LP dual support, {len(pk)} placements, tau {float(node.get("tau", 0)):.4f} / budget {node.get("budget")}', 12, bold=True),
           text(ox, oy - S0*S - 10, f'sum of dual weights {sum(ys):.3f}; max weight {ymax:.3f}; opacity = weight; black box = the conditioned square (tilt {box.get("th0", 0):.1f}–{box.get("th1", 0):.1f}°)', 9.5, '#444')]
    out.append(f'<rect x="{ox}" y="{oy-S0*S:.1f}" width="{S0*S:.1f}" height="{S0*S:.1f}" fill="none" stroke="#000" stroke-width="2"/>')
    for (x0, y0) in [(0, 0), (S0-1, 0), (0, S0-1), (S0-1, S0-1)]:
        out.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>')
    for (cx, cy) in pins:
        P = sq(cx, cy, 0.0); pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
        out.append(f'<polygon points="{pts}" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>')
    bad = 0
    # colour by tilt bin so distinct squares of the shadow separate visually
    for p in sorted(pk, key=lambda p: float(p.get('y', 0))):
        cx, cy, th, y = float(p['cx']), float(p['cy']), float(p['theta']), float(p.get('y', 0))
        P = sq(cx, cy, th)
        if not all(-1e-6 <= x <= S0+1e-6 and -1e-6 <= yy <= S0+1e-6 for x, yy in P): bad += 1; continue
        hue = int((math.degrees(th) % 90) / 90 * 300)
        pts = ' '.join(f'{ox+x*S:.1f},{oy-yy*S:.1f}' for x, yy in P)
        op = 0.15 + 0.6 * (y / ymax if ymax > 0 else 0)
        out.append(f'<polygon points="{pts}" fill="hsl({hue},70%,45%)" fill-opacity="{op:.2f}" stroke="hsl({hue},70%,30%)" stroke-width="0.8"/>')
    if box:
        out.append(f'<rect x="{ox+box["x0"]*S:.1f}" y="{oy-box["y1"]*S:.1f}" width="{(box["x1"]-box["x0"])*S:.1f}" height="{(box["y1"]-box["y0"])*S:.1f}" fill="none" stroke="#000" stroke-width="2"/>')
    # weight table: top placements
    top = sorted(pk, key=lambda p: -float(p.get('y', 0)))[:8]
    out.append(text(ox, oy + 16, 'top weights: ' + '; '.join(f'({float(p["cx"]):.2f},{float(p["cy"]):.2f},{math.degrees(float(p["theta"]))%90:.0f}°) {float(p.get("y",0)):.2f}' for p in top), 8.5, '#333'))
    out.append(text(ox, oy + 28, f'placements outside the container skipped: {bad}; colour hue = tilt mod 90° (0° red … 90° magenta)', 8.5, '#666'))
    return out
ids = sys.argv[1:] or ['k5_11_interior_Y0036_D07_D00', 'k5_11_interior_Y0036_D07_D04', 'k5_11_interior_Y0036_D07_D05', 'k5_11_interior_Y0186_D00_D00']
PW = int(S0*S + 50); oy = 60 + S0*S
body = []
for k, nid in enumerate(ids):
    node, path = find_node(nid)
    if node is None: print('no node json for', nid); continue
    body += panel(30 + k*PW, oy, nid, node, row_of(nid))
    print(nid, path, 'packing', len(node.get('packing', [])), 'keys', sorted(node.keys())[:20])
W = len(ids)*PW + 40; H = int(oy + 44)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a57_lp_support.svg')
open(out, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', out, W, H)
import xml.dom.minidom; xml.dom.minidom.parse(out); print('xml ok')
