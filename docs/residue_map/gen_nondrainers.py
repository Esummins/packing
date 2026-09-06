"""The two strictly K0-BLOCKED packings that do NOT drain (A102): floor-1e-4 (4.0000044) and polish12 (4.0000001).
Poses from A87's exact files (same loader as A102's rigid102.py); contacts/jam data from A102's results. Geometry-checked."""
import json, math, os
from fractions import Fraction
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
A87R = os.path.join(R, 'attempts', 'A87-drain-flow', 'results')
def load():
    out = {}
    d = json.load(open(os.path.join(A87R, 'k0dir2_87.records.json')))
    v = d['floors']['1e-04']
    out['floor_1e-04_d1em04_s0202'] = (float(Fraction(v['container_side_exact'])),
        [(float(Fraction(p['cx_exact'])), float(Fraction(p['cy_exact'])), float(Fraction(p['theta_exact']))) for p in v['poses']])
    for i, line in enumerate(open(os.path.join(A87R, 'k0dir87.polish.jsonl'))):
        r = json.loads(line)
        if i == 12:
            z = [Fraction(a) for a in r['z_polished']]
            out['polish12_%s' % r['tag']] = (float(z[33]), [(float(z[3*j]), float(z[3*j+1]), float(z[3*j+2])) for j in range(11)])
    return out
packs = load()
rows = {json.loads(l)['packing']: json.loads(l) for l in open(os.path.join(R, 'attempts', 'A102-rigidity-drain', 'results', 'rigid102.jsonl'), encoding='utf-8') if l.strip()}
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
def cell_depth(p, x0, y0):
    xs = [x for x, y in p]; ys = [y for x, y in p]
    dx = min(max(xs), x0+1) - max(min(xs), x0); dy = min(max(ys), y0+1) - max(min(ys), y0)
    return min(dx, dy) if dx > 1e-12 and dy > 1e-12 else 0.0
S = 130
def esc(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'
red = ('#c62828', '#ef9a9a'); blue = ('#1565c0', '#90caf9'); grey = ('#555', '#e0e0e0')
def panel(ox, oy, name, s, P, row):
    polys = [sq(*q) for q in P]
    assert all(-5e-9 <= x <= s+5e-9 and -5e-9 <= y <= s+5e-9 for p in polys for x, y in p), 'containment'
    m = min(sep(polys[i], polys[j]) for i in range(11) for j in range(i+1, 11)); assert m >= -5e-9, m
    corners = {'BL': (0, 0), 'BR': (s-1, 0), 'TR': (s-1, s-1), 'TL': (0, s-1)}
    meet = {cn: sorted([(cell_depth(p, *c), i) for i, p in enumerate(polys) if cell_depth(p, *c) > 1e-9], reverse=True) for cn, c in corners.items()}
    first = {ds[0][1] for ds in meet.values() if ds}; second = {d[1] for ds in meet.values() for d in ds[1:]}
    out = [text(ox, oy - s*S - 28, f'{name}: side {s:.7f}, strictly K0-BLOCKED, does not drain', 12.5, bold=True)]
    out.append(f'<rect x="{ox}" y="{oy-s*S:.1f}" width="{s*S:.1f}" height="{s*S:.1f}" fill="none" stroke="#000" stroke-width="2.2"/>')
    for cn, (x0, y0) in corners.items():
        out.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>')
    for i, p in enumerate(polys):
        col, fill = red if i in second else blue if i in first else grey
        pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in p)
        out.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.6" stroke="{col}" stroke-width="1.5"/>')
        t = math.degrees(P[i][2]) % 90; t = min(t, 90-t)
        out.append(text(ox+P[i][0]*S, oy-P[i][1]*S+4, str(i), 11, '#000', True, 'middle'))
        out.append(text(ox+P[i][0]*S, oy-P[i][1]*S+15, f'{t:.2f}°', 8, '#333', False, 'middle'))
    # A102 T1: contacts of every second meeter and the jam
    jam_lines = []
    entries = []
    def flat(x):
        if isinstance(x, dict) and 'square' in x: entries.append(x)
        elif isinstance(x, (list, tuple)): [flat(y) for y in x]
        elif isinstance(x, dict): [flat(y) for y in x.values()]
    flat(row['t1'])
    for e in entries:
        if e['square'] not in second: continue
        for c in e['contacts']:
            x, y = c['point']
            out.append(f'<circle cx="{ox+x*S:.1f}" cy="{oy-y*S:.1f}" r="4" fill="none" stroke="#c62828" stroke-width="1.5"/>')
        best = None
        for mo in e['motions']:
            if mo.get('first_order_free') and not mo.get('collision_free'):
                bl = mo.get('blocked_by') or {}
                cand = (mo['kind'], mo.get('reached_deg', mo.get('reached')), bl.get('blocker'), bl.get('gap'))
                if best is None or (cand[1] or 0) > (best[1] or 0): best = cand
        cs = ', '.join(sorted({c['with'] for c in e['contacts']}))
        jam = f'free at first order ({best[0]}), jams at {best[1]:.2e}{" deg" if "rot" in best[0] else ""} on {best[2]} (gap {best[3]:.1e})' if best else 'rigid at first order'
        jam_lines.append(f'{e["corner"]} second meeter sq {e["square"]}: depth {e["depth"]:.2e}; contacts {cs}; {jam}')
    y = oy + 20
    for ln in jam_lines:
        out.append(text(ox, y, ln, 9.5, '#333')); y += 13
    out.append(text(ox, y, f'checks: containment, min pairwise SAT separation {m:+.1e}; corner meeter counts ' + ' '.join(f'{cn}:{len(ds)}' for cn, ds in meet.items()), 9, '#666')); y += 13
    return out, y
W = 2*(int(4.0*S) + 60) + 40
body = []; ymax = 0
for k, name in enumerate(['floor_1e-04_d1em04_s0202', 'polish12_s0380']):
    s, P = packs[name]
    out, y = panel(30 + k*(int(4.0*S) + 60), 60 + 4.0*S, name, s, P, rows[name]); body += out; ymax = max(ymax, y)
body.append(text(30, ymax + 16, 'red = second meeter of a corner cell, blue = first meeter, grey = the rest; small red circles = the contacts A102 found on the second meeters (gap < 1e-7). Intrusions here are 1e-2 to 1e-7 deep and invisible at this scale; the numbers carry them.', 9.5, '#444'))
body.append(text(30, ymax + 30, 'A102 (2026-09-06): both packings have first-order-free second meeters that jam within 1e-4 degrees on a square whose gap is just above the contact bar; retraction fractions 0.022 and 0.22 (drainers: 1.000). Sides 4.0000044 and 4.0000001.', 9.5, '#444'))
H = int(ymax + 44)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
outp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nondrainers.svg')
open(outp, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', outp, W, H)
import xml.dom.minidom; xml.dom.minidom.parse(outp); print('xml ok')
for name in packs:
    s, P = packs[name]; print(name, s); [print('  ', i, round(q[0], 5), round(q[1], 5), round(math.degrees(q[2]) % 90, 4)) for i, q in enumerate(P)]
