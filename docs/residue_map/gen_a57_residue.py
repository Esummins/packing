"""A57 k5_11 residue, drawn: (A) every level-1 node box coloured by status; (B) the alive lineages by level;
(C) the hole witnesses of the fertile lineages clustered into 'squares' (one colour per cluster = the shadow's squares).
Read-only on A57 files. Geometry-checked: every drawn witness square is inside the container."""
import json, math, os, glob, collections
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
A57 = os.path.join(R, 'attempts', 'A57-shadow-trees')
S0 = 3.877084
PINS = [(0.5, 0.5), (0.5, 1.5), (0.5, S0 - 0.5), (1.5, 0.5), (S0 - 0.5, 0.5)]   # k5_11 = BL[2,1] + TL[1] + BR[1]
def rows(pattern):
    out = []
    for f in sorted(glob.glob(os.path.join(A57, 'results', pattern))):
        out += [json.loads(l) for l in open(f, encoding='utf-8') if l.strip()]
    return out
L1 = [r for r in rows('tree_k5_11_interior_G1_s[0-9].jsonl') if isinstance(r.get('box'), dict)]
L2 = rows('tree_k5_11_interior_G1_D2.jsonl'); L2A = rows('tree_k5_11_interior_G1_D2_s0.jsonl')
L3 = rows('tree_k5_11_interior_G1_D2_D2.jsonl'); L3A = rows('tree_k5_11_interior_G1_D2_D2_s0.jsonl')
L4 = rows('tree_k5_11_interior_G1_D2_D2_D2.jsonl')
def status(r):
    c = (r.get('cert') or '')
    if c.startswith('PASS'): return 'PASS'
    if c.startswith('KILL'): return 'LOGIC'
    if c.startswith('ALIVE'): return 'ALIVE'
    if c.startswith('FAIL'): return 'FAIL'
    return 'OTHER'
COL = {'PASS': ('#9e9e9e', '#eeeeee'), 'LOGIC': ('#bdbdbd', '#f7f7f7'), 'FAIL': ('#e65100', '#ffcc80'), 'ALIVE': ('#c62828', '#ef9a9a'), 'OTHER': ('#777', '#ddd')}
def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5*(dx*c - dy*s_), cy + 0.5*(dx*s_ + dy*c)) for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
def esc(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'
S = 150
def frame(ox, oy, title, sub):
    out = [text(ox, oy - S0*S - 26, title, 12.5, bold=True), text(ox, oy - S0*S - 10, sub, 9.5, '#444')]
    out.append(f'<rect x="{ox}" y="{oy-S0*S:.1f}" width="{S0*S:.1f}" height="{S0*S:.1f}" fill="none" stroke="#000" stroke-width="2"/>')
    for (x0, y0) in [(0, 0), (S0-1, 0), (0, S0-1), (S0-1, S0-1)]:
        out.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>')
    for (cx, cy) in PINS:
        P = sq(cx, cy, 0.0); pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
        out.append(f'<polygon points="{pts}" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>')
    return out
def box_rect(ox, oy, b, col, fill, op=0.5, w=1.0):
    return f'<rect x="{ox+b["x0"]*S:.1f}" y="{oy-b["y1"]*S:.1f}" width="{max(b["x1"]-b["x0"],0.003)*S:.1f}" height="{max(b["y1"]-b["y0"],0.003)*S:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{w}"/>'
PW = int(S0*S + 60); oy = 60 + S0*S
body = []
# ---- panel A: level 1
st1 = collections.Counter(status(r) for r in L1)
ox = 30
body += frame(ox, oy, f'A. k5_11 level 1: {len(L1)} node boxes (conditioned square centre range), by status',
              f'PASS {st1["PASS"]}, logic {st1["LOGIC"]}, FAIL {st1["FAIL"]}, ALIVE-at-LP {st1["ALIVE"]} — tilt ranges not shown (8° bins)')
for key in ('LOGIC', 'PASS', 'FAIL', 'ALIVE'):
    for r in L1:
        if status(r) == key:
            c, f = COL[key]; body.append(box_rect(ox, oy, r['box'], c, f, 0.45 if key in ('PASS', 'LOGIC') else 0.6))
# ---- panel B: alive lineages
ox = 30 + PW
alive2 = {r['id'] for r in L2A}; alive3 = {r['id'] for r in L3A}
roots = sorted({r['parent'] for r in L2A})
palette = ['#c62828', '#6a1b9a', '#00838f', '#2e7d32', '#ef6c00', '#4527a0', '#ad1457', '#558b2f', '#0277bd', '#5d4037', '#9e9d24', '#d84315']
rc = {rt: palette[i % len(palette)] for i, rt in enumerate(roots)}
st2 = collections.Counter(status(r) for r in L2); st3 = collections.Counter(status(r) for r in L3); st4 = collections.Counter(status(r) for r in L4)
body += frame(ox, oy, f'B. the alive lineages: level-2 alive {len(alive2)} (of {len(L2)}), level-3 alive {len(alive3)} (of {len(L3)}), level-4 children {len(L4)}',
              f'colour = level-1 root ({len(roots)} roots carry all alive level-2 nodes); thin = level 2, thick = level 3 alive, hatched = level 4 ({st4["PASS"]} PASS/{st4["LOGIC"]} logic/{st4["FAIL"]} FAIL)')
for r in L1:
    if r['id'] in roots: body.append(box_rect(ox, oy, r['box'], rc[r['id']], 'none', 0, 0.8))
for r in L2A:
    body.append(box_rect(ox, oy, r['box'], rc[r['parent']], rc[r['parent']], 0.25, 1.0))
for r in L3A:
    rt = r['parent'].rsplit('_D', 1)[0]
    body.append(box_rect(ox, oy, r['box'], rc.get(rt, '#000'), rc.get(rt, '#000'), 0.55, 2.2))
for r in L4:
    rt = r['parent'].rsplit('_D', 1)[0].rsplit('_D', 1)[0]
    c, f = COL[status(r)]
    body.append(box_rect(ox, oy, r['box'], c, f, 0.7, 1.0))
# root labels
for r in L1:
    if r['id'] in roots:
        b = r['box']; body.append(text(ox + (b['x0']+b['x1'])/2*S, oy - b['y1']*S - 3, r['id'].split('_')[-1], 8.5, rc[r['id']], True, 'middle'))
# ---- panel C: hole witnesses of the fertile lineages, clustered
ox = 30 + 2*PW
wit = []
for f in glob.glob(os.path.join(A57, 'certs', 'tree', 'k5_11_interior_G1_D2*', '*.witnesses.json')):
    nid = os.path.basename(f).split('.')[0]
    if not (nid.startswith('k5_11_interior_Y0036') or nid.startswith('k5_11_interior_Y0186') or nid.startswith('k5_11_interior_Y0083')): continue
    w = json.load(open(f, encoding='utf-8'))
    for e in w.get('witnesses', []):
        p = e['placement']; wit.append((p['cx_float'], p['cy_float'], math.radians(p['theta_deg']), nid, e.get('kind')))
# de-duplicate placements and cluster by centre distance
uniq = {}
for cx, cy, th, nid, kind in wit:
    key = (round(cx, 3), round(cy, 3), round(math.degrees(th), 1))
    uniq.setdefault(key, (cx, cy, th, set()))[3].add(nid)
pts = list(uniq.values())
clusters = []
for cx, cy, th, nids in sorted(pts, key=lambda p: (-len(p[3]), p[0], p[1])):
    for cl in clusters:
        if math.hypot(cl['cx']-cx, cl['cy']-cy) < 0.35: cl['m'].append((cx, cy, th, nids)); break
    else: clusters.append({'cx': cx, 'cy': cy, 'm': [(cx, cy, th, nids)]})
for cl in clusters:
    xs = [m[0] for m in cl['m']]; ys = [m[1] for m in cl['m']]; ts = [math.degrees(m[2]) % 90 for m in cl['m']]
    cl['ext'] = (max(xs)-min(xs), max(ys)-min(ys), max(ts)-min(ts), len(cl['m']))
clusters.sort(key=lambda c: -len(c['m']))
body += frame(ox, oy, f'C. hole witnesses of the Y0036 / Y0186 / Y0083 lineages: {len(pts)} distinct placements in {len(clusters)} clusters',
              'each translucent square is one witness placement (an unlocalised square the certificate could not exclude); colour = cluster (centres within 0.35)')
bad = 0
for i, cl in enumerate(clusters):
    col = palette[i % len(palette)]
    for cx, cy, th, nids in cl['m']:
        P = sq(cx, cy, th)
        if not all(-1e-6 <= x <= S0+1e-6 and -1e-6 <= y <= S0+1e-6 for x, y in P): bad += 1; continue
        pts_ = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
        body.append(f'<polygon points="{pts_}" fill="{col}" fill-opacity="0.08" stroke="{col}" stroke-width="0.6" stroke-opacity="0.5"/>')
for i, cl in enumerate(clusters[:12]):
    col = palette[i % len(palette)]; ex = cl['ext']
    body.append(text(ox + cl['cx']*S, oy - cl['cy']*S + 4, f'{i}', 11, col, True, 'middle'))
# conditioned box of the lineages' roots on panel C
for r in L1:
    if r['id'] in ('k5_11_interior_Y0036', 'k5_11_interior_Y0186', 'k5_11_interior_Y0083'):
        body.append(box_rect(ox, oy, r['box'], '#000', 'none', 0, 1.5))
        b = r['box']; body.append(text(ox + (b['x0']+b['x1'])/2*S, oy - b['y0']*S + 11, r['id'].split('_')[-1] + ' (conditioned)', 8.5, '#000', True, 'middle'))
y = oy + 22
body.append(text(30, y, 'Panel C clusters (index: members, spread in x / y / tilt°): ' + '; '.join(f'{i}: {c["ext"][3]}, {c["ext"][0]:.2f}/{c["ext"][1]:.2f}/{c["ext"][2]:.0f}°' for i, c in enumerate(clusters[:12])), 9.5)); y += 14
body.append(text(30, y, f'Level-2 alive boxes: median width x {sorted(r["box"]["x1"]-r["box"]["x0"] for r in L2A)[len(L2A)//2]:.3f}, tilt {sorted(r["box"]["th1"]-r["box"]["th0"] for r in L2A)[len(L2A)//2]:.2f}°; level-3 alive: width {sorted(r["box"]["x1"]-r["box"]["x0"] for r in L3A)[len(L3A)//2]:.3f}, tilt {sorted(r["box"]["th1"]-r["box"]["th0"] for r in L3A)[len(L3A)//2]:.2f}°. Witness squares outside the container skipped: {bad}.', 9.5)); y += 14
body.append(text(30, y, 'Pins (blue) = k5_11 class squares BL(0,0),(1,0),(0,1) + TL(0,0) + BR(0,0) at s0 = 3.877084. Dashed = corner cells. Tree nodes condition ONE square (its centre box drawn); every other non-pin square is free and appears only through witnesses.', 9.5, '#444'))
W = 3*PW + 40; H = int(y + 16)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a57_residue.svg')
open(out, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', out, W, H)
import xml.dom.minidom; xml.dom.minidom.parse(out); print('xml ok')
print('L1', st1, 'L2', st2, 'L3', st3, 'L4', st4, 'roots', roots)
for i, c in enumerate(clusters[:12]): print(i, c['ext'], round(c['cx'], 3), round(c['cy'], 3))
