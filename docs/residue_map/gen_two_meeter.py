"""Two-meeter atlas at a corner (PI, 2026-09-09): the first meeter Q1 sits on the corner diagonal, pressed into
the corner as far as its tilt allows (touching both walls); as its tilt sweeps 0..90 deg its corners press it out
to the 45-degree maximum.  For each Q1 pose, draw the region of CENTRES of a second unit square Q2 (any tilt) that
(a) meets the interior of the corner box, (b) is interior-disjoint from Q1, (c) lies inside the container.
Both the unit corner box and the K0-WIDEN widened box (side 1 + w, w = 0.025509) are shown.  Green = some tilt
works; the sideband lines x = 1 and y = 1 are drawn (the PI's SIDEBAND lemma, A169: one of the two meeters has
its centre within 1 of a wall).  Read-only; writes docs/residue_map/two_meeter_atlas.svg."""
import math, os, sys
S0 = 969271 / 250000
W0 = 0.025509
PANELS = [0, 10, 20, 30, 45, 60, 75, 90]        # tilt of Q1 in degrees
PITCH = 0.03
TILTS = [math.radians((k + 0.5) * 90 / 24) for k in range(24)]
def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)]]
def sat(p, q):
    axes = []
    for poly in (p, q):
        for i in range(4):
            a, b = poly[i], poly[(i + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey)
            axes.append((-ey / n, ex / n))
    best = -9
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]; qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best
def pressed(theta_deg):
    th = math.radians(theta_deg); h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
    return (h, h, th)
def region(q1poly, c):
    box = [(0, 0), (c, 0), (c, c), (0, c)]
    cells = []
    n = int(2.4 / PITCH)
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * PITCH, (j + 0.5) * PITCH
            ok = False
            for th in TILTS:
                P = sq(cx, cy, th)
                if min(v[0] for v in P) < 0 or min(v[1] for v in P) < 0: continue
                if sat(P, box) >= -1e-9: continue          # must meet int box
                if sat(P, q1poly) < -1e-9: continue         # must be disjoint from Q1
                ok = True; break
            if ok: cells.append((cx, cy))
    return cells
def esc(t): return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
S = 130; PW = 2.4 * S + 40; PH = 2.4 * S + 70
out = []
for k, theta in enumerate(PANELS):
    cx, cy, th = pressed(theta); q1 = sq(cx, cy, th)
    ox = 30 + (k % 4) * PW; oy = 60 + (k // 4) * PH + 2.4 * S
    def X(x): return ox + x * S
    def Y(y): return oy - y * S
    regs = {}
    for c in (1.0, 1.0 + W0):
        regs[c] = region(q1, c)
    out.append(f'<text x="{ox}" y="{oy - 2.4 * S - 30}" font-size="13" font-weight="bold">Q1 pressed on the diagonal, tilt {theta}° — centre ({cx:.3f}, {cy:.3f})</text>')
    out.append(f'<text x="{ox}" y="{oy - 2.4 * S - 14}" font-size="10" fill="#444">green = centres of a second meeter at SOME tilt (unit box); pale green = extra centres allowed by the widened box (K0-WIDEN, +{W0:.4f}); dashed = sidebands x=1, y=1</text>')
    out.append(f'<rect x="{X(0)}" y="{Y(2.4)}" width="{2.4 * S}" height="{2.4 * S}" fill="none" stroke="#000" stroke-width="1.5"/>')
    unit = set(regs[1.0])
    for (x, y) in regs[1.0 + W0]:
        if (x, y) in unit: continue
        out.append(f'<rect x="{X(x - PITCH / 2):.1f}" y="{Y(y + PITCH / 2):.1f}" width="{PITCH * S:.1f}" height="{PITCH * S:.1f}" fill="#c8e6c9" stroke="none"/>')
    for (x, y) in regs[1.0]:
        out.append(f'<rect x="{X(x - PITCH / 2):.1f}" y="{Y(y + PITCH / 2):.1f}" width="{PITCH * S:.1f}" height="{PITCH * S:.1f}" fill="#43a047" fill-opacity="0.75" stroke="none"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(1)}" width="{S}" height="{S}" fill="none" stroke="#1565c0" stroke-width="1.2"/>')
    out.append(f'<rect x="{X(0)}" y="{Y(1 + W0)}" width="{(1 + W0) * S}" height="{(1 + W0) * S}" fill="none" stroke="#1565c0" stroke-width="0.8" stroke-dasharray="3,2"/>')
    out.append(f'<line x1="{X(1)}" y1="{Y(0)}" x2="{X(1)}" y2="{Y(2.4)}" stroke="#d81b60" stroke-width="1" stroke-dasharray="5,3"/>')
    out.append(f'<line x1="{X(0)}" y1="{Y(1)}" x2="{X(2.4)}" y2="{Y(1)}" stroke="#d81b60" stroke-width="1" stroke-dasharray="5,3"/>')
    pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in q1)
    out.append(f'<polygon points="{pts}" fill="#00e5ff" fill-opacity="0.35" stroke="#000" stroke-width="2"/>')
    out.append(f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="3" fill="#000"/>')
    n_unit = len(regs[1.0]); n_wid = len(regs[1.0 + W0])
    band = sum(1 for (x, y) in regs[1.0] if x <= 1 or y <= 1)
    out.append(f'<text x="{ox}" y="{oy + 14}" font-size="10" fill="#333">second-meeter centre area: unit box {n_unit * PITCH ** 2:.3f}, widened {n_wid * PITCH ** 2:.3f}; of the unit-box centres {band} of {n_unit} lie in a sideband (x≤1 or y≤1)</text>')
    print(f'theta {theta:2d}: Q1 centre ({cx:.3f},{cy:.3f}); second-meeter centres unit {n_unit} widened {n_wid}; in-band {band}/{n_unit}', flush=True)
Wd = 4 * PW + 40; Hd = 2 * PH + 80
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.0f}" height="{Hd:.0f}" font-family="Segoe UI, sans-serif" style="background:#fff">',
       '<text x="30" y="24" font-size="15" font-weight="bold">Two-meeter atlas at a corner: the first meeter pressed into the corner on the diagonal, sweeping 0–90°; where the second meeter\'s centre can be</text>'] + out + ['</svg>']
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'two_meeter_atlas.svg')
open(p, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', p)
import xml.dom.minidom; xml.dom.minidom.parse(p); print('xml ok')
