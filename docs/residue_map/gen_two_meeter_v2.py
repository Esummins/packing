"""Two-meeter atlas v2 (PI, 2026-09-09): a PRESSED first meeter leaves no room for a second (v1), so sweep the
first meeter's DISPLACEMENT.  Two families per tilt theta of Q1: (A) slide along the bottom wall keeping wall
contact: centre (h + d, h); (B) pull away from the corner along the diagonal: centre (h + d/sqrt2, h + d/sqrt2),
h = (|cos|+|sin|)/2.  For each family and theta find the smallest d at which a second unit square (any tilt) can
meet the interior of the corner box, be interior-disjoint from Q1 and inside the container; draw the panel at that
threshold (and one panel a step beyond) with the second-meeter centre region.  Unit box; widened box in pale.
Writes docs/residue_map/two_meeter_atlas_v2.svg and prints d*(theta)."""
import math, os
S0 = 969271 / 250000; W0 = 0.025509
THETAS = [0, 15, 30, 45, 60, 75, 90]
PITCH = 0.04
TILTS = [math.radians((k + 0.5) * 90 / 18) for k in range(18)]
DSTEP = 0.02
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
def region(q1, c, coarse=False):
    box = [(0, 0), (c, 0), (c, c), (0, c)]
    pitch = PITCH * (2 if coarse else 1); n = int(2.4 / pitch); cells = []
    for i in range(n):
        for j in range(n):
            cx, cy = (i + 0.5) * pitch, (j + 0.5) * pitch
            for th in TILTS:
                P = sq(cx, cy, th)
                if min(v[0] for v in P) < 0 or min(v[1] for v in P) < 0: continue
                if sat(P, box) >= -1e-9: continue
                if sat(P, q1) < -1e-9: continue
                cells.append((cx, cy)); break
    return cells
def q1_of(theta, fam, d):
    th = math.radians(theta); h = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
    if fam == 'A': return (h + d, h, th)
    return (h + d / math.sqrt(2), h + d / math.sqrt(2), th)
def threshold(theta, fam):
    d = 0.0
    while d <= 1.2:
        q1 = sq(*q1_of(theta, fam, d))
        if region(q1, 1.0, coarse=True): return d
        d += DSTEP
    return None
S = 110; PW = 2.4 * S + 30; PH = 2.4 * S + 60
out = []; row = 0
for fam, famname in (('A', 'slide along the bottom wall (wall contact kept)'), ('B', 'pull away from the corner along the diagonal')):
    for k, theta in enumerate(THETAS):
        dstar = threshold(theta, fam)
        d = dstar if dstar is not None else 1.2
        cx, cy, th = q1_of(theta, fam, d); q1 = sq(cx, cy, th)
        reg = region(q1, 1.0); regw = region(q1, 1.0 + W0)
        ox = 30 + k * PW; oy = 70 + row * PH + 2.4 * S
        X = lambda x: ox + x * S; Y = lambda y: oy - y * S
        out.append(f'<text x="{ox}" y="{oy - 2.4 * S - 26}" font-size="11" font-weight="bold">{famname if k == 0 else ""}</text>')
        out.append(f'<text x="{ox}" y="{oy - 2.4 * S - 10}" font-size="10">theta {theta}°: threshold d* = {("%.2f" % dstar) if dstar is not None else "none ≤ 1.2"} — Q1 at ({cx:.2f}, {cy:.2f})</text>')
        out.append(f'<rect x="{X(0)}" y="{Y(2.4)}" width="{2.4 * S}" height="{2.4 * S}" fill="none" stroke="#000" stroke-width="1.2"/>')
        unit = set(reg)
        for (x, y) in regw:
            if (x, y) in unit: continue
            out.append(f'<rect x="{X(x - PITCH / 2):.1f}" y="{Y(y + PITCH / 2):.1f}" width="{PITCH * S:.1f}" height="{PITCH * S:.1f}" fill="#c8e6c9"/>')
        for (x, y) in reg:
            out.append(f'<rect x="{X(x - PITCH / 2):.1f}" y="{Y(y + PITCH / 2):.1f}" width="{PITCH * S:.1f}" height="{PITCH * S:.1f}" fill="#43a047" fill-opacity="0.75"/>')
        out.append(f'<rect x="{X(0)}" y="{Y(1)}" width="{S}" height="{S}" fill="none" stroke="#1565c0" stroke-width="1.1"/>')
        out.append(f'<line x1="{X(1)}" y1="{Y(0)}" x2="{X(1)}" y2="{Y(2.4)}" stroke="#d81b60" stroke-width="0.9" stroke-dasharray="5,3"/>')
        out.append(f'<line x1="{X(0)}" y1="{Y(1)}" x2="{X(2.4)}" y2="{Y(1)}" stroke="#d81b60" stroke-width="0.9" stroke-dasharray="5,3"/>')
        pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in q1)
        out.append(f'<polygon points="{pts}" fill="#00e5ff" fill-opacity="0.35" stroke="#000" stroke-width="1.8"/>')
        out.append(f'<text x="{ox}" y="{oy + 14}" font-size="9" fill="#333">2nd-meeter centre area at d*: unit {len(reg) * PITCH ** 2:.3f} (in-band {sum(1 for x, y in reg if x <= 1 or y <= 1)}/{len(reg)}), widened {len(regw) * PITCH ** 2:.3f}</text>')
        print(f'{fam} theta {theta:2d}: d* = {dstar}  region cells unit {len(reg)} widened {len(regw)}', flush=True)
    row += 1
Wd = 7 * PW + 40; Hd = 2 * PH + 90
doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.0f}" height="{Hd:.0f}" font-family="Segoe UI, sans-serif" style="background:#fff">',
       '<text x="30" y="24" font-size="14" font-weight="bold">Two-meeter atlas v2: the smallest displacement of the first meeter at which a second meeter of the unit corner box exists (green = second-meeter centres at that threshold; pale = widened box)</text>',
       '<text x="30" y="42" font-size="10" fill="#444">v1 showed a PRESSED first meeter (touching both walls) admits no second meeter of the unit box at any tilt; dashed = sidebands x=1, y=1; blue = the unit corner box; cyan = Q1.</text>'] + out + ['</svg>']
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'two_meeter_atlas_v2.svg')
open(p, 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', p)
import xml.dom.minidom; xml.dom.minidom.parse(p); print('xml ok')
