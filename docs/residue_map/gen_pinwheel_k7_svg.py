import json, math, os
d = json.load(open('pinwheel_result.json')); s = d['s']; F = d['free']; fx = d['fixed']
SHAT = 3.877083590022814
names = ['BL(0,0)', 'BL(1,0)', 'BL(0,1)', 'TL(0,0)', 'TR(0,0)', 'BR(0,0)', 'BR(0,1)']
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
allsq = [(f[0], f[1], f[2]) for f in F] + [(p[0], p[1], 0.0) for p in fx]
polys = [sq(*q) for q in allsq]
assert all(-1e-6 <= x <= s+1e-6 and -1e-6 <= y <= s+1e-6 for p in polys for x, y in p)
m = min(sep(polys[i], polys[j]) for i in range(11) for j in range(i+1, 11)); assert m >= -1e-6, m
S = 160; ox, oy = 40, 60 + s*S
def esc(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def text(x, y, t, size=11, col='#222', bold=False, anchor='start'):
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{esc(t)}</text>'
body = [text(ox, oy - s*S - 28, f'PI candidate: 7 slot squares (BL L-shape 3, BR stacked 2, TL 1, TR 1) + 4-square pinwheel; minimum side s* = {s:.6f} = s-hat + {s-SHAT:.6f}', 12.5, bold=True),
        text(ox, oy - s*S - 10, f'SLSQP over the 4 free squares and s, 301 starts, 242 feasible; the 4 free squares share one tilt, 48.435 deg; min pairwise SAT separation {m:+.1e}', 10, '#444')]
body.append(f'<rect x="{ox}" y="{oy-s*S:.1f}" width="{s*S:.1f}" height="{s*S:.1f}" fill="none" stroke="#000" stroke-width="2.2"/>')
for (x0, y0) in [(0, 0), (s-1, 0), (0, s-1), (s-1, s-1)]:
    body.append(f'<rect x="{ox+x0*S:.1f}" y="{oy-(y0+1)*S:.1f}" width="{S}" height="{S}" fill="none" stroke="#bbb" stroke-width="1" stroke-dasharray="4,3"/>')
for i, P in enumerate(polys):
    col, fill = ('#c62828', '#ef9a9a') if i < 4 else ('#1565c0', '#90caf9')
    pts = ' '.join(f'{ox+x*S:.1f},{oy-y*S:.1f}' for x, y in P)
    body.append(f'<polygon points="{pts}" fill="{fill}" fill-opacity="0.6" stroke="{col}" stroke-width="1.5"/>')
    cx, cy, th = allsq[i]
    body.append(text(ox+cx*S, oy-cy*S+4, f'f{i}' if i < 4 else names[i-4], 10, '#000', True, 'middle'))
    if i < 4: body.append(text(ox+cx*S, oy-cy*S+15, f'{math.degrees(th)%90:.2f}°', 8, '#333', False, 'middle'))
contacts = []
for i in range(11):
    for j in range(i+1, 11):
        if i >= 4 and j >= 4: continue
        if sep(polys[i], polys[j]) < 1e-6:
            contacts.append(f'{("f%d" % i) if i < 4 else names[i-4]}–{("f%d" % j) if j < 4 else names[j-4]}')
            # mark the contact point
            best = (9, None)
            for A, B in ((polys[i], polys[j]), (polys[j], polys[i])):
                for v in A:
                    for k in range(4):
                        a, b = B[k], B[(k+1)%4]; ex, ey = b[0]-a[0], b[1]-a[1]; L = ex*ex+ey*ey
                        t = max(0, min(1, ((v[0]-a[0])*ex + (v[1]-a[1])*ey)/L)); f = (a[0]+t*ex, a[1]+t*ey)
                        dd = math.hypot(v[0]-f[0], v[1]-f[1])
                        if dd < best[0]: best = (dd, f)
            f = best[1]; body.append(f'<circle cx="{ox+f[0]*S:.1f}" cy="{oy-f[1]*S:.1f}" r="4.5" fill="none" stroke="#2e7d32" stroke-width="2"/>')
walls = []
for i in range(4):
    cx, cy, th = allsq[i]; w = (abs(math.cos(th)) + abs(math.sin(th)))/2
    for nm, g in (('left', cx-w), ('right', s-w-cx), ('bottom', cy-w), ('top', s-w-cy)):
        if g < 1e-6: walls.append(f'f{i}–{nm} wall')
y = oy + 20
body.append(text(ox, y, 'contact graph (green circles): ' + ', '.join(contacts + walls), 10)); y += 14
body.append(text(ox, y, 'free squares: ' + '; '.join(f'f{i} ({cx:.4f}, {cy:.4f}, {math.degrees(th)%90:.3f}°)' for i, (cx, cy, th) in enumerate(F)), 9.5, '#444')); y += 14
body.append(text(ox, y, 'This is a k7 packing (seven exact slot squares). Its side is above s0 = 3.877084 by 0.0097, which is why every k5_11 box that contains it is alive at the LP and dies only when the boxes and cores resolve 0.01.', 9.5, '#444'))
W = int(s*S + 80 + 700); H = int(y + 14)
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
out = r'C:\Users\esumm\code\packing\docs\residue_map\pinwheel_k7_shadow.svg'
open(out, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', out)
import xml.dom.minidom; xml.dom.minidom.parse(out); print('xml ok'); print(contacts + walls)
