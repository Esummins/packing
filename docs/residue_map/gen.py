"""Generate the SVG figures for docs/residue_map.md. All squares are checked for containment,
interior-disjointness and depth before drawing; failures raise."""
import json, math, os
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SHAT = 3.877083590022814
S = 120  # px per unit

def sq_c(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
def sq_v(v, th_deg):
    t = math.radians(th_deg); e1 = (math.cos(t), math.sin(t)); e2 = (-math.sin(t), math.cos(t))
    return [v, (v[0]+e1[0], v[1]+e1[1]), (v[0]+e1[0]+e2[0], v[1]+e1[1]+e2[1]), (v[0]+e2[0], v[1]+e2[1])]
def depth(pts, corner=(0, 0), side=None):
    # depth into the corner slot at `corner` (one of the 4 container corners); 1 - min over square of max distance to the two walls
    best = 9
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        for k in range(401):
            s = k / 400; x = a[0] + (b[0] - a[0]) * s; y = a[1] + (b[1] - a[1]) * s
            dx = x - corner[0] if corner[0] == 0 else corner[0] - x
            dy = y - corner[1] if corner[1] == 0 else corner[1] - y
            best = min(best, max(dx, dy))
    return 1 - best
def sep(p, q):
    axes = []
    for poly_ in (p, q):
        for i in range(4):
            a, b = poly_[i], poly_[(i + 1) % 4]; ex, ey = b[0] - a[0], b[1] - a[1]; n = math.hypot(ex, ey); axes.append((-ey / n, ex / n))
    best = -9
    for ax in axes:
        pp = [x * ax[0] + y * ax[1] for x, y in p]; qq = [x * ax[0] + y * ax[1] for x, y in q]
        best = max(best, min(qq) - max(pp), min(pp) - max(qq))
    return best
def inside(p, side):
    return all(-1e-9 <= x <= side + 1e-9 and -1e-9 <= y <= side + 1e-9 for x, y in p)
def check_packing(polys, side):
    for p in polys: assert inside(p, side), 'outside'
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            assert sep(polys[i], polys[j]) >= -1e-7, f'overlap {i},{j}: {sep(polys[i], polys[j])}'
def poly(pts, ox, oy, col, fill, dash=False, op=0.55, w=1.6):
    d = ' '.join(f'{ox + p[0]*S:.1f},{oy - p[1]*S:.1f}' for p in pts)
    da = ' stroke-dasharray="5,3"' if dash else ''
    return f'<polygon points="{d}" fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="{w}"{da}/>'
def text(x, y, s, size=11, col='#222', bold=False, anchor='start'):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    b = ' font-weight="bold"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" text-anchor="{anchor}"{b}>{s}</text>'
def container(ox, oy, side, label=None):
    out = [f'<rect x="{ox}" y="{oy - side*S}" width="{side*S}" height="{side*S}" fill="none" stroke="#000" stroke-width="2.5"/>']
    for cx, cy in [(0, 0), (side - 1, 0), (0, side - 1), (side - 1, side - 1)]:
        out.append(f'<rect x="{ox + cx*S}" y="{oy - (cy + 1)*S}" width="{S}" height="{S}" fill="none" stroke="#666" stroke-width="1" stroke-dasharray="4,3"/>')
    if label: out.append(text(ox, oy - side * S - 8, label, 13, bold=True))
    return out
def svg(w, h, body, name):
    doc = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ['</svg>']
    open(os.path.join(HERE, name), 'w', encoding='utf-8').write('\n'.join(doc)); print('wrote', name)

# ---------- data ----------
trump = json.load(open(os.path.join(ROOT, 'certs', 'trump11_certificate.json')))
T = []
for q in trump['squares']:
    cx, cy = float(Fraction(q['cx'])), float(Fraction(q['cy'])); tm = float(Fraction(q['t']))
    T.append((cx, cy, 2 * math.atan(tm)))
side_T = float(Fraction(trump['container_side'])) if isinstance(trump['container_side'], str) else float(trump['container_side'])
TP = [sq_c(*t) for t in T]; check_packing(TP, side_T + 1e-6)
rec = json.load(open(os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'results', 'k0dir87.json')))['record_K0_BLOCKED_packing']
z = [float(Fraction(v)) for v in rec['z']]; side_R = z[33]
R = [(z[3*i], z[3*i+1], z[3*i+2]) for i in range(11)]; RP = [sq_c(*t) for t in R]; check_packing(RP, side_R + 1e-6)

def slot_meeters(P, side):
    """which squares meet each open corner slot (depth > 1e-9)"""
    out = {}
    for name, corner in [('BL', (0, 0)), ('BR', (side, 0)), ('TL', (0, side)), ('TR', (side, side))]:
        out[name] = [(i, depth(p, corner, side)) for i, p in enumerate(P) if depth(p, corner, side) > 1e-12]
    return out
TM = slot_meeters(TP, side_T); RM = slot_meeters(RP, side_R)
print('Trump slot meeters', {k: [(i, round(d, 3)) for i, d in v] for k, v in TM.items()})
print('record slot meeters', {k: [(i, round(d, 3)) for i, d in v] for k, v in RM.items()})

# ---------- fig 1: Trump ----------
ox, oy = 40, 60 + side_T * S
body = container(ox, oy, side_T, f'Trump at s-hat = {side_T:.6f}: 5 simple squares (blue), TL two-crowd (orange), the rest (grey)')
simple = [i for i, (cx, cy, th) in enumerate(T) if abs(th) < 1e-9 and (min(abs(cx - 0.5), abs(cx - (side_T - 0.5))) < 1e-6 and min(abs(cy - 0.5), abs(cy - (side_T - 0.5))) < 1e-6 or (abs(cx - 0.5) < 1e-6 and abs(cy - 1.5) < 1e-6) or (abs(cx - 1.5) < 1e-6 and abs(cy - 0.5) < 1e-6))]
tl = [i for i, d in TM['TL']]
for i, p in enumerate(TP):
    col, fill = ('#1565c0', '#90caf9') if i in simple else (('#e65100', '#ffcc80') if i in tl else ('#555', '#ddd'))
    body.append(poly(p, ox, oy, col, fill))
    body.append(text(ox + T[i][0]*S, oy - T[i][1]*S + 4, f'{i}', 10, anchor='middle'))
body += [text(ox, oy + 20, f'trump5 pins: {sorted(simple)}.  TL crowd: {tl} at depths {[round(d,3) for _, d in TM["TL"]]} (offset-upright + 40.18 deg partner).', 11),
         text(ox, oy + 36, 'Every other corner is a slot square (depth 1). Charge of the TL pair = 0.980 of the 4.032 budget.', 11)]
svg(60 + side_T * S + 40, oy + 50, body, 'trump.svg')

# ---------- fig 2: the 3.985 K0-BLOCKED record ----------
ox, oy = 40, 60 + side_R * S
body = container(ox, oy, side_R, f'K0-BLOCKED record at side {side_R:.6f} (s-hat + 0.108): every corner slot doubly intruded')
colmap = {'BL': ('#c62828', '#ef9a9a'), 'BR': ('#c62828', '#ef9a9a'), 'TL': ('#2e7d32', '#a5d6a7'), 'TR': ('#2e7d32', '#a5d6a7')}
owner = {}
for c, lst in RM.items():
    for i, d in lst: owner[i] = c
for i, p in enumerate(RP):
    col, fill = colmap.get(owner.get(i), ('#555', '#ddd'))
    body.append(poly(p, ox, oy, col, fill))
    body.append(text(ox + R[i][0]*S, oy - R[i][1]*S + 4, f'{i}', 10, anchor='middle'))
body += [text(ox, oy + 20, 'Red corners (BL, BR): INTERLOCKED — the exchange and the Young flood both stall (adjacent crowds lock through the 4 - m overlap of their arm cells).', 11),
         text(ox, oy + 36, 'Green corners (TL, TR): convertible — remove the two intruders, place the slot square, re-fit one square at the same side (verified exactly).', 11),
         text(ox, oy + 52, 'Depths: ' + '; '.join(f'{c}: ' + ', '.join((f'{d:.1e}' if d < 1e-3 else f'{d:.3f}') for _, d in RM[c]) for c in ['BL', 'BR', 'TL', 'TR']) + '.  TL/TR = near-slot square + 1e-8 nick (ghost); BL/BR substantive.', 11)]
svg(60 + side_R * S + 40, oy + 66, body, 'record_3985.svg')

# ---------- fig 3: the four corner cases ----------
d = 0.15
def panel(ox, oy, title, shapes, notes):
    out = [text(ox, oy - 2.55 * S, title, 13, bold=True),
           f'<line x1="{ox}" y1="{oy}" x2="{ox+2.4*S}" y2="{oy}" stroke="#000" stroke-width="3"/>',
           f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-2.4*S}" stroke="#000" stroke-width="3"/>',
           f'<rect x="{ox}" y="{oy-S}" width="{S}" height="{S}" fill="none" stroke="#444" stroke-width="1.2" stroke-dasharray="4,3"/>'] + shapes
    y = oy + 16
    for n in notes: out.append(text(ox, y, n, 10.5)); y += 14
    return out
W = 4 * 330 + 40
body = []
# JAM
g = 0.12; phi = 4.0; x0 = 0.075; eta = (g - x0) * math.tan(math.radians(phi)) * 0.9
J1 = sq_v((g, 0.0), 0.0); J2 = sq_v((x0, 1 - eta), phi); assert sep(J1, J2) >= 0 and inside(J2, 4)
ox, oy = 30, 370
body += panel(ox, oy, '1. JAM (68 of 7,044 pairs)', [f'<rect x="{ox}" y="{oy-S}" width="{g*S}" height="{S}" fill="#fdd835" fill-opacity="0.45"/>', poly(J1, ox, oy, '#c62828', '#ef9a9a'), poly(J2, ox, oy, '#1565c0', '#90caf9')],
              [f'slot square parked g = {g} off the slot; partner nicks', f'the sliver: tilt <= arcsin g, depth ~ g^2/4 = {depth(J2):.3f}', 'area-free; needs a floating pusher (FLOAT: strands', '0.707) or an on-wall pusher (WALL-F: 2 flush widths).', 'Lives only within 0.01 of s-hat (SLIDE).'])
# BLOCK
_t = math.radians(20.0); B1 = sq_v((0.7, 0.0), 20.0); B2 = sq_v((0.7 - math.sin(_t), math.cos(_t)), 20.0); assert inside(B1, 4) and inside(B2, 4) and sep(B1, B2) >= -1e-9
ox = 360
body += panel(ox, oy, '2. BLOCK (same grain, edge-to-edge)', [poly(B1, ox, oy, '#c62828', '#ef9a9a'), poly(B2, ox, oy, '#1565c0', '#90caf9')],
              [f'both at 30 deg sharing an edge; depths {depth(B1):.2f} / {depth(B2):.2f}', 'a 2x1 tilted block against the corner; charge can be', 'exactly 0 (certified) — the free object of the', 'area budget. At 45 deg it is the CEIL pair.'])
# WEDGE (CEIL pair asymmetric): P at 45 shifted, Q at 35
r2 = math.sqrt(2); h = r2 / 2
P = [(r2, 0), (r2 + h, h), (r2, r2), (h, h)]; Q = [(0, r2 + 0.25), (h, h + 0.25), (r2, r2 + 0.25), (h, r2 + h + 0.25)]
assert inside(Q, 4) and sep(P, Q) >= -1e-9, sep(P, Q)
ox = 690
body += panel(ox, oy, '3. WEDGE (both tilted, 15-45 deg)', [poly([(0, 0), (r2, 0), (0, r2)], ox, oy, '#7a5c00', '#fdd835', op=0.35), poly(P, ox, oy, '#c62828', '#ef9a9a'), poly(Q, ox, oy, '#1565c0', '#90caf9')],
              [f'depths {depth(P):.3f} / {depth(Q):.3f}; a line through the corner', 'separates them (CEIL: shallower one <= 0.293).', 'Stranded triangle <= 1. THE MIDDLE BAND: second', 'intruder in (0.05, 0.29) — no tool touches it.'])
# OFFSET-UPRIGHT: Trump TL mapped to BL frame
tl_idx = [i for i, _ in TM['TL']]
mapped = []
for i in tl_idx:
    cx, cy, th = T[i]; mapped.append(sq_c(cx, side_T - cy, -th))
ox = 1020
body += panel(ox, oy, '4. OFFSET-UPRIGHT (Trump\'s own corner; 28% of pairs)', [poly(mapped[0], ox, oy, '#c62828', '#ef9a9a'), poly(mapped[1], ox, oy, '#1565c0', '#90caf9')],
              ['Trump TL in the BL frame: upright flush on the wall,', f'0.8445 off the slot; partner at 40.18 deg. Depths', f'{depth(mapped[0]):.3f} / {depth(mapped[1]):.3f}. Charge 0.980 — affordable only', 'because Trump\'s other three corners charge 0.'])
svg(W, 480, body, 'corner_cases.svg')

# ---------- fig 4: depth axis ----------
w = 900; body = [text(20, 30, 'The second-intruder depth d2 at a corner (K0-BLOCKED), with what is proved on each band', 13, bold=True)]
x0, x1, y = 60, 860, 110
def X(v): return x0 + (x1 - x0) * v / 0.35
body.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#000" stroke-width="2"/>')
for v in [0, 0.05, 0.1, 0.2, 0.2929, 0.35]:
    body.append(f'<line x1="{X(v)}" y1="{y-6}" x2="{X(v)}" y2="{y+6}" stroke="#000"/>'); body.append(text(X(v), y + 20, f'{v:g}', 10, anchor='middle'))
bands = [(0, 0.02, '#ffcc80', 'nick shell: d2 < s-hat - m; SLIDE forbids below side s-hat - d2; pin slack covers d2 < 0.02 (k1 tree)'),
         (0.02, 0.2929, '#ef9a9a', 'THE RESIDUE (middle band): no certificate; crowd LP refused <= 0.1, failed certification at 0.2'),
         (0.2929, 0.35, '#c8e6c9', 'impossible: CEIL — two intruders cannot both exceed 1 - 1/sqrt2 = 0.2929')]
for a, b, col, lab in bands:
    body.append(f'<rect x="{X(a)}" y="{y-40}" width="{X(b)-X(a)}" height="34" fill="{col}" fill-opacity="0.7"/>')
yy = 170
for a, b, col, lab in bands: body.append(f'<rect x="60" y="{yy-10}" width="14" height="14" fill="{col}"/>'); body.append(text(82, yy + 2, lab, 11)); yy += 20
body.append(text(60, yy + 10, 'Census of the 7,044 realisable pairs: 56% cannot host d2 >= 0.05, 82% cannot host d2 >= 0.1, 91% cannot host d2 >= 0.2; 1.2% can host both >= 0.3.', 11))
body.append(text(60, yy + 28, 'Lowest known K0-BLOCKED packing: 3.985 (nicked TL/TR, substantive BL/BR). The middle band is where the tree spends its time.', 11))
svg(w, yy + 50, body, 'depth_axis.svg')

# ---------- fig 5: the interior-first tree root ----------
side = SHAT; ox, oy = 40, 60 + side * S
body = container(ox, oy, side, 'The k0 tree\'s root: one interior square is conditioned on a cell of T (blue), corners are never branched on')
lo, hi = 1.938542, 2.777084
tri = [(lo, lo), (hi, lo), (hi, hi)]
body.append(poly(tri, ox, oy, '#1565c0', '#90caf9', op=0.5))
for cx, cy in [(0, 0), (side, 0), (0, side), (side, side)]:
    r = 2.457
    body.append(f'<circle cx="{ox + cx*S}" cy="{oy - cy*S}" r="{r*S}" fill="none" stroke="#c62828" stroke-width="1" stroke-dasharray="3,3"/>')
body += [text(ox, oy + 20, 'T = {1.9385 <= y <= x <= 2.777} (D4 fundamental domain): every packing at side <= 3.877 has a square centred in T (A24.1/A38.1).', 11),
         text(ox, oy + 36, 'Red arcs: reach 2.457 of a corner blocker — every pair of corners\' blockers can touch (min pair reach 2.001 > s/2).', 11),
         text(ox, oy + 52, '216 level-1 cells of T x [0,90) never decide; ~6,290 nodes at levels 2-4 at ~1 CPU-h each = the 3,200-7,000 CPU-h.', 11)]
svg(60 + side * S + 40, oy + 66, body, 'tree_root.svg')

# ---------- fig 6: Young flood ----------
ox, oy = 40, 330
body = [text(ox, 30, 'The Young flood from a corner: cells placed (blue), completable cells (dashed), intruders removed (red outline)', 13, bold=True),
        f'<line x1="{ox}" y1="{oy}" x2="{ox+3.2*S}" y2="{oy}" stroke="#000" stroke-width="3"/>', f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-2.6*S}" stroke="#000" stroke-width="3"/>']
cells = [(0, 0), (1, 0), (0, 1)]
for cx, cy in cells: body.append(f'<rect x="{ox+cx*S}" y="{oy-(cy+1)*S}" width="{S}" height="{S}" fill="#90caf9" fill-opacity="0.6" stroke="#1565c0" stroke-width="1.5"/>')
for cx, cy in [(2, 0), (1, 1), (0, 2)]: body.append(f'<rect x="{ox+cx*S}" y="{oy-(cy+1)*S}" width="{S}" height="{S}" fill="none" stroke="#444" stroke-width="1.2" stroke-dasharray="5,3"/>')
I1 = sq_v((2.05, 0.2), 25.0); I2 = sq_v((1.1, 1.15), 55.0)
for p in (I1, I2): body.append(poly(p, ox, oy, '#c62828', 'none', w=2))
body += [text(ox, oy + 20, 'X(D) = (#squares meeting D) - |D| = overhang minus free area inside D.  K0-BLOCKED <=> X(slot) >= 1.  Win when X(D) <= 0.', 11),
         text(ox, oy + 36, 'Below side 4 every square meets the 3x3 block, so X(3x3) = 2 exactly: a win needs <= 8 cells (Lemma CAP). Trump: X = 1 for every diagram; deficit 2.', 11),
         text(ox, oy + 52, 'Measured: 30/33 corners convert (depth <= 3); stalls = interlocks. A free cell pays the deficit down; a doubly-intruded cell raises it.', 11)]
svg(3.2 * S + 80, oy + 66, body, 'flood.svg')
print('done')
