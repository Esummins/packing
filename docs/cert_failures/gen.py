"""Figures for docs/cert_failures.md from attempts/A96-a57-parametric/results/certfail.figures.json.
Each entry: {side, pins: [[cx,cy],...], boxes: [{cx:[lo,hi], cy:[lo,hi], tilt_deg:[lo,hi]}], sample_square: [cx,cy,tilt_deg],
category, source, label?}. Every drawn square is checked for containment; the sample square is checked against the pins."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
S = 120
def sq_c(cx, cy, th):
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
def inside(p, side): return all(-1e-9 <= x <= side+1e-9 and -1e-9 <= y <= side+1e-9 for x, y in p)
def esc(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def poly(pts, ox, oy, col, fill, dash=False, op=0.55, w=1.5):
    d = ' '.join(f'{ox+p[0]*S:.1f},{oy-p[1]*S:.1f}' for p in pts)
    da = ' stroke-dasharray="5,3"' if dash else ''
    return f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{w}"{da}/>'
def text(x, y, s, size=11, col='#222', bold=False):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}"{b}>{esc(s)}</text>'
def figure(entry, name):
    sd = entry['side']; side = float(max(sd)) if isinstance(sd, list) else float(sd); ox, oy = 40, 60 + side*S
    for b in entry.get('conditioned_boxes', []) or []:
        try:
            x0, x1 = map(float, b['cx']); y0, y1 = map(float, b['cy'])
            entry.setdefault('_cond', []).append((x0, x1, y0, y1))
        except Exception: pass
    body = [f'<rect x="{ox}" y="{oy-side*S}" width="{side*S}" height="{side*S}" fill="none" stroke="#000" stroke-width="2.5"/>']
    for cx, cy in [(0,0),(side-1,0),(0,side-1),(side-1,side-1)]:
        body.append(f'<rect x="{ox+cx*S}" y="{oy-(cy+1)*S}" width="{S}" height="{S}" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4,3"/>')
    pins = [sq_c(float(cx), float(cy), 0.0) for cx, cy in entry.get('pins', [])]
    for p in pins: assert inside(p, side), 'pin outside'; body.append(poly(p, ox, oy, '#1565c0', '#90caf9'))
    for (x0, x1, y0, y1) in entry.get('_cond', []):
        body.append(f'<rect x="{ox+x0*S}" y="{oy-y1*S}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" fill="#2e7d32" fill-opacity="0.15" stroke="#2e7d32" stroke-width="1" stroke-dasharray="3,3"/>')
    for b in entry.get('boxes', []):
        # draw the centre box (a rectangle) and the extreme-tilt outlines of the box's square family
        x0, x1 = map(float, b['cx']); y0, y1 = map(float, b['cy']); t0, t1 = map(float, b['tilt_deg'])
        body.append(f'<rect x="{ox+x0*S}" y="{oy-y1*S}" width="{max(x1-x0,0.004)*S}" height="{max(y1-y0,0.004)*S}" fill="#e65100" fill-opacity="0.35" stroke="#e65100" stroke-width="1.5"/>')
        for (cx, cy, td) in [(x0, y0, t0), (x1, y1, t1)]:
            body.append(poly(sq_c(cx, cy, math.radians(td)), ox, oy, '#e65100', 'none', dash=True, w=1))
    if entry.get('sample_square'):
        cx, cy, td = map(float, entry['sample_square']); q = sq_c(cx, cy, math.radians(td))
        assert inside(q, side), 'sample outside'
        worst = min([sep(q, p) for p in pins] + [9])
        body.append(poly(q, ox, oy, '#c62828', '#ef9a9a', op=0.6, w=2))
        body.append(text(ox, oy + 36, f'sample square ({cx:.3f}, {cy:.3f}) tilt {td:.2f} deg; min gap to a pin {worst:+.4f}', 10.5))
    body.insert(0, text(ox, oy - side*S - 10, f"{entry['category']} — {entry.get('source','')}", 13, bold=True))
    body.append(text(ox, oy + 20, entry.get('label', ''), 10.5))
    w = max(int(side*S + 80), 900); h = int(oy + 50)
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
    open(os.path.join(HERE, name), 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', name)
if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'attempts', 'A96-a57-parametric', 'results', 'certfail.figures.json')
    data = json.load(open(src, encoding='utf-8'))
    entries = data if isinstance(data, list) else data.get('figures', data.get('entries', []))
    for i, e in enumerate(entries):
        figure(e, f"fig_{e['category'][:1].upper()}_{i}.svg")
