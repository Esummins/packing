"""Three-panel figure: the 3.9907 record, after rotating square 3, after the simultaneous snaps (k = 7). Geometry-checked."""
import json, math
R = r'C:\Users\esumm\code\packing'
d = json.load(open(R + '/attempts/A87-drain-flow/results/pi_drain_3p9907.json')); s = d['side']
def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5*(dx*c - dy*s_), cy + 0.5*(dx*s_ + dy*c)) for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def sep(p, q):
    axes = []
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; n = math.hypot(ex, ey); axes.append((-ey/n, ex/n))
    best = -9
    for ax in axes:
        pp = [x*ax[0]+y*ax[1] for x, y in p]; qq = [x*ax[0]+y*ax[1] for x, y in q]
        best = max(best, min(qq)-max(pp), min(pp)-max(qq))
    return best
def check(poses):
    polys = [sq(*q) for q in poses]
    assert all(-5e-9 <= x <= s+5e-9 and -5e-9 <= y <= s+5e-9 for p in polys for x, y in p), 'containment'
    m = min(sep(polys[i], polys[j]) for i in range(11) for j in range(i+1, 11)); assert m >= -5e-9, m
    return m
S = 120; PW = int(s*S + 40)
def esc(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'
def panel(ox, oy, poses, title, sub, highlight, young_cells=(), contacts=()):
    out = [text(ox, oy - s*S - 26, title, 12.5, bold=True), text(ox, oy - s*S - 10, sub, 10, '#444')]
    out.append(f'<rect x="{ox}" y="{oy-s*S:.1f}" width="{s*S:.1f}" height="{s*S:.1f}" fill="none" stroke="#000" stroke-width="2.2"/>')
    for (x0, y0) in [(0, 0), (s-1, 0), (0, s-1), (s-1, s-1)]:
        out.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>')
    for (x0, y0) in young_cells:
        out.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="#2e7d32" fill-opacity="0.12" stroke="none"/>')
    for i, q in enumerate(poses):
        P = sq(*q); col, fill = highlight.get(i, ('#555', '#e0e0e0'))
        pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
        out.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.6" stroke="{col}" stroke-width="1.5"/>')
        t = math.degrees(q[2]) % 90; t = min(t, 90-t)
        out.append(text(ox+q[0]*S, oy-q[1]*S+4, str(i), 11, '#000', True, 'middle'))
        out.append(text(ox+q[0]*S, oy-q[1]*S+15, f'{t:.1f}°', 8, '#333', False, 'middle'))
    for (x, y, lab) in contacts:
        out.append(f'<circle cx="{ox+x*S:.1f}" cy="{oy-y*S:.1f}" r="5" fill="none" stroke="#c62828" stroke-width="2"/>')
        out.append(text(ox+x*S+8, oy-y*S-6, lab, 9, '#c62828', True))
    return out
before, after, final = [tuple(p) for p in d['before']], [tuple(p) for p in d['after_rotation']], [tuple(p) for p in d['final']]
m0, m1, m2 = check(before), check(after), check(final)
oy = 70 + s*S
body = []
red = ('#c62828', '#ef9a9a'); blue = ('#1565c0', '#90caf9'); green = ('#2e7d32', '#a5d6a7'); orange = ('#e65100', '#ffcc80')
# panel 1: record; square 3 highlighted, its three contacts circled
c3 = [(3.9233, 1.0000, 'sq 2: CCW'), (3.9907, 1.9987, 'wall: CCW'), (2.9910, 2.0216, 'sq 8 (edge slope 0.47): CCW')]
body += panel(30, oy, before, f'1. the record, side {s:.6f}', 'square 3 tilted 1.31° CW of axis, vertex 1.02e-3 into BR; all three contacts torque it CCW (+0.46, +0.49, +0.23)', {3: red, 2: blue}, contacts=c3)
# panel 2: after rotation
body += panel(30 + PW + 30, oy, after, '2. rotate 3 CCW by 1.31° about its centre', f'collision-free along the whole path (checked at 2000 steps); BR now met by square 2 alone', {3: orange, 2: blue})
# panel 3: final
moves = {int(k): v for k, v in d['moves'].items()}
yc = []
lat = {'BL': lambda i, j: (i, j), 'BR': lambda i, j: (s-i-1, j), 'TR': lambda i, j: (s-i-1, s-j-1), 'TL': lambda i, j: (i, s-j-1)}
for L, cells in d['young'].items():
    for (i, j) in cells: yc.append(lat[L](i, j))
hl = {i: green for i in moves}
body += panel(30 + 2*(PW + 30), oy, final, '3. simultaneous snaps: 1, 2, 3, 5, 6, 7, 9 -> lattice cells', 'valid packing at the same side; BR staircase [3,1] + TR row [3]: k = 7 simple squares (shaded), 4 tilted remain', hl, young_cells=yc)
y = oy + 24
body.append(text(30, y, 'moves (destination form, Lemma SNAP / K0-FREE teleport): ' + '; '.join(f'{i} -> {v[0]}({v[1]},{v[2]}) by {math.hypot(v[3]-after[i][0], v[4]-after[i][1]):.4f}' for i, v in sorted(moves.items())), 10)); y += 15
body.append(text(30, y, f'checks in this script: containment of all 11 squares in all three panels; min pairwise SAT separation {m0:+.1e} / {m1:+.1e} / {m2:+.1e} (certification tolerance 5e-9)', 10, '#444')); y += 15
body.append(text(30, y, 'PI reading (2026-09-06): the three contacts of square 3 (square 2, right wall, square 8) leave it free to rotate CCW; once it lifts out of BR, 2 snaps in and the bottom and top rows follow. Verified exactly.', 10, '#444'))
W = 3*PW + 90; H = int(y + 12)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
out = R + r'\docs\residue_map\strict_3p9907_drain.svg'
open(out, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', out, W, H)
import xml.dom.minidom; xml.dom.minidom.parse(out); print('xml ok')
