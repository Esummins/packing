"""Load-path page for the nine-square ring witness rand_0_0569|t20 (A218 s.5): squares exact, FJ forces
as arrows (blue wall, black square-square, width ~ multiplier), the tilt-floor torques as orange arcs.
Geometry-checked: every arrow foot lies on both touching boundaries, no pair overlaps.  Run from anywhere."""
import json, math, time, os
ROOT = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(ROOT, '..', '..', '..'))
WID = 'w364_held'
t0 = time.time()


def load(path, key):
    for l in open(path, encoding='utf-8', errors='replace'):
        if key in l[:80]:
            return json.loads(l)


T = load(os.path.join(REPO, 'attempts/A217-torque-probe/results/torque217.jsonl'), '"%s"' % WID)
Wt = load(os.path.join(REPO, 'attempts/A217-torque-probe/results/witnesses217.jsonl'), '"%s"' % WID)
z = Wt['z']; s = z[-1]; n = (len(z) - 1) // 3
sq = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(n)]


def verts(i):
    cx, cy, th = sq[i]; c, d = math.cos(th), math.sin(th)
    return [(cx + c * x - d * y, cy + d * x + c * y) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def dist_to_boundary(i, p):
    cx, cy, th = sq[i]; c, d = math.cos(th), math.sin(th)
    u = c * (p[0] - cx) + d * (p[1] - cy); v = -d * (p[0] - cx) + c * (p[1] - cy)
    return max(abs(u), abs(v)) - 0.5


def sep(i, j):  # separating-axis gap (>= -1e-9 means no overlap)
    best = -1e9
    for k in (i, j):
        th = sq[k][2]
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            pi = [ax[0] * x + ax[1] * y for x, y in verts(i)]; pj = [ax[0] * x + ax[1] * y for x, y in verts(j)]
            best = max(best, min(pi) - max(pj), min(pj) - max(pi))
    return best


# ---- contact points: A217's row point is on square i only; the true contact is a vertex of one square lying on
# the other's boundary -- take the one nearest the row point, and check it against BOTH boundaries.
def contact(i, j, p):
    cands = [v for v in verts(i) if abs(dist_to_boundary(j, v)) < 1e-6] + [v for v in verts(j) if abs(dist_to_boundary(i, v)) < 1e-6]
    return min(cands, key=lambda v: math.hypot(v[0] - p[0], v[1] - p[1]))


worst = 0.0
for a in T['arrows']:
    if a['kind'] == 'edge':
        a['p'] = contact(a['i'], a['j'], a['p'])
        worst = max(worst, abs(dist_to_boundary(a['j'], a['p'])))
    worst = max(worst, abs(dist_to_boundary(a['i'], a['p'])))
gap = min(sep(i, j) for i in range(n) for j in range(i + 1, n))
wall = min(min(min(x, y, s - x, s - y) for x, y in verts(i)) for i in range(n))
print('geometry: worst arrow-foot error %.1e, min pair gap %.1e, min wall gap %.1e' % (worst, gap, wall))
assert worst < 1e-6 and gap > -1e-6 and wall > -1e-6

# ---- page
S = 150.0; M = 60; H = int(S * s) + 2 * M; W = H + 340


def P(x, y):
    return (M + S * x, M + S * (s - y))


meeters = sorted(sum(Wt['meeters'].values(), [])); holders = [9]
tb = {q['i']: q['tau_bound'] for q in T['squares'] if abs(q['tau_bound']) > 1e-6}
o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica,Arial,sans-serif">' % (W, H + 250)]
o.append('<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="context-stroke"/></marker>'
         '<pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="#999"/></pattern></defs>')
o.append('<rect width="%d" height="%d" fill="white"/>' % (W, H + 250))
x0, y0 = P(0, s)
o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#333" stroke-width="2"/>' % (x0, y0, S * s, S * s))
for i in range(n):
    pts = ' '.join('%.1f,%.1f' % P(*v) for v in verts(i))
    if i in meeters:
        fill, stroke = '#fde9c9', '#b06a00'
    elif i in holders:
        fill, stroke = '#dbe9f6', '#1f4e79'
    else:
        fill, stroke = 'url(#stip)', '#777'
    o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.5"/>' % (pts, fill, stroke))
    cx, cy = P(sq[i][0], sq[i][1])
    o.append('<text x="%.1f" y="%.1f" font-size="15" text-anchor="middle" fill="#222">%d</text>' % (cx, cy + 5, i))
lam_max = max(a['lam'] for a in T['arrows'])


def arrow(p, f, col, lam):
    L = 0.55 * lam / lam_max + 0.12; fn = math.hypot(*f)
    if fn < 1e-9:
        return
    ux, uy = f[0] / fn, f[1] / fn; a0 = P(*p); a1 = P(p[0] + L * ux, p[1] + L * uy)
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" marker-end="url(#ah)"/>'
             % (a0[0], a0[1], a1[0], a1[1], col, 1.2 + 3.5 * lam / lam_max))
    o.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (a0[0], a0[1], col))


for a in T['arrows']:
    if a['lam'] < 1e-6:
        continue
    if a['kind'] == 'wall':
        arrow(a['p'], a['f'], '#1f77b4', a['lam'])
    elif a['kind'] == 'edge':
        arrow(a['p'], a['f'], '#000', a['lam']); arrow(a['p'], [-a['f'][0], -a['f'][1]], '#555', a['lam'])
tmax = max(abs(v) for v in tb.values())
for i, tau in tb.items():  # orange arc = torque from the 20-degree tilt floor; + = counter-clockwise in the packing
    cx, cy = P(sq[i][0], sq[i][1]); r = 22 + 30 * abs(tau) / tmax
    # polyline through the bottom half of a circle, traversed in the torque's sense (+ = counter-clockwise);
    # screen y points down, so a packing point (x, y) is drawn at (cx + x, cy - y)
    angs = [math.radians(200 + 140 * k / 40.0) for k in range(41)] if tau > 0 else [math.radians(340 - 140 * k / 40.0) for k in range(41)]
    pts = ' '.join('%.1f,%.1f' % (cx + r * math.cos(t), cy - r * math.sin(t)) for t in angs)
    o.append('<polyline points="%s" fill="none" stroke="#ff7f0e" stroke-width="3" marker-end="url(#ah)"/>' % pts)
    o.append('<text x="%.1f" y="%.1f" font-size="11" fill="#ff7f0e" text-anchor="middle">floor %+.3f</text>' % (cx, cy + r + 13, tau))
tx = M + S * s + 25; ty = M + 10


def line(t, dy=17, size=12, col='#222', bold=False):
    global ty
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    o.append('<text x="%d" y="%d" font-size="%d" fill="%s"%s>%s</text>' % (tx, ty, size, col, ' font-weight="bold"' if bold else '', t)); ty += dy


line('WHAT THIS IS', size=13, bold=True)
NOTES = ['HELD local optimum rand_0_0569|t20, side %.4f,' % s, '11 unit squares; NOT a Fritz-John point of',
         'the free problem: the search floor |tilt| >= 20 deg', 'is active on 8 squares (four carry its torque).', '',
         'orange squares = the 8 corner meeters', '(BL 4,5  BR 6,7  TR 8,10  TL 2,3), all at 20 deg',
         'from alignment; blue = holder 9 (flat);', 'grey stipple = 0, 1: no loaded contact (rattlers).', '',
         'ARROWS = FJ contact forces at the contact', 'point, length and width ~ multiplier:',
         'blue = wall normal; black = force on the first', 'square of the pair, dark grey = its reaction.', '',
         'ORANGE ARCS = torque the tilt floor supplies', '(units: force x side; + = counter-clockwise).',
         'No square and no wall supplies it: without the', 'floor, 2 and 4 turn counter-clockwise and 7, 8',
         'clockwise: each toward alignment (Lemma W).', '',
         'LOAD PATH (a closed compression ring):', 'wall x=0 -> 5 -> 4 -> 6 -> 7 <- wall x=s;',
         '7 -> 8 -> 10 <- wall y=s;  10 <- 9 -> 3 <- wall y=s;', '3 <- 2 <- 5.  Floor meeters 4, 6 hold each other',
         'ALONG the floor; wall meeters 5|2 and 7|8 hold', 'each other UP the walls; 9 holds both ceiling',
         'meeters.  Nine squares, force-balanced; torque-', 'balanced only with the floor.  A218 s.5.']
for t in NOTES:
    line(t)
line('', dy=10)
line('renderer %.2f s from A217 stress rows; geometry checked: arrow feet on both' % (time.time() - t0), size=10, col='#666')
line('boundaries (%.0e), no overlaps, no wall crossing' % worst, size=10, col='#666')
ty = H + 20; tx = M
line('Per-square torque balance (force x side; + = counter-clockwise): tau_wall + tau_contact + tau_floor = 0', dy=18, size=11, bold=True)
for q in T['squares']:
    if q['i'] in meeters + holders:
        line('%2d: tilt %5.1f  W=%.3f  tau_wall=%+.4f  tau_contact=%+.4f  tau_floor=%+.4f' % (q['i'], q['tilt_deg'], q['W'], q['tau_wall'], q['tau_contact'], q['tau_bound']), dy=16, size=11)
o.append('</svg>')
out = os.path.join(REPO, 'docs/residue_map/campaigns/A218-k0-count/ring_loadpath_rand_0_0569_t20.svg')
open(out, 'w', encoding='utf-8').write('\n'.join(o)); print('wrote', out, 'in %.2f s' % (time.time() - t0))
