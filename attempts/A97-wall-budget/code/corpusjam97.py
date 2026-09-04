"""corpusjam97.py -- A97 T3: the JAM pusher clause (P-ON) measured on the exact K0-BLOCKED corpus.

Corpus: the four polished exact-K0-BLOCKED endpoints of k0dir87 (A87, k0dir87.polish.jsonl rows
with exact_K0_BLOCKED and z_polished; layout [cx,cy,theta]*11 + [s], theta in radians), all at
sigma ~ 4.000, plus exact Trump (0 JAM corners, control).

Per corner (D4 corner frame): intruders of the open slot; a JAM corner = an axis-aligned member S
at offset g = max(a,b) <= 0.1 with a partner N of tilt <= arcsin g (cases85's definition).  For
each JAM: S's retreat type (x-side if a > b, y-side if b > a, corner if a = b), the squares in
contact with S's far edge in the retreat direction (the S-pushers), and for each pusher its
lowest point above the PUSHER WALL (the wall perpendicular to the retreat direction) and its
footprint phi on that wall's line (wall_budget.md Lemma WALL-F).  P-ON holds for the jam iff
some pusher has phi >= 1.  Also reports every wall's footprint sum vs sigma (WALL-F at sigma 4).

One process, no BLAS.  Writes attempts/A97-wall-budget/results/corpusjam97.json.
"""
from __future__ import annotations
import os, json, math
from fractions import Fraction
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_v] = '1'

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'attempts', 'A87-drain-flow', 'results', 'k0dir87.polish.jsonl')
TRUMP = os.path.join(ROOT, 'attempts', 'A03-upper-reconstruct', 'trump11_exact.json')
OUT = os.path.join(HERE, '..', 'results')
H0 = 1 / math.sqrt(2)
TOL = 1e-4   # contact tolerance (the flows' rows are active to ~1e-6; 1e-4 also catches the EPS_KEEP-floored kisses)
AX_TOL_DEG = 0.15  # corpus flows drive the axis member to 0.005-0.12 deg (d1max87 caveat), not exactly 0


def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + u * c - v * s, cy + u * s + v * c)
            for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def tilt(th):
    t = math.degrees(th) % 90.0
    return min(t, 90.0 - t)


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy)


def poly_seg_dist(poly, a, b):
    """distance between a convex polygon and a segment (0 if they meet): min over vertex-edge
    pairs both ways (exact for non-crossing; crossing is excluded by disjoint interiors)."""
    d = min(seg_dist(v, a, b) for v in poly)
    n = len(poly)
    for k in range(n):
        d = min(d, seg_dist(a, poly[k], poly[(k + 1) % n]), seg_dist(b, poly[k], poly[(k + 1) % n]))
    return d


def chord(poly, h):
    xs = []
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        if (y1 - h) * (y2 - h) < 0:
            xs.append(x1 + (h - y1) / (y2 - y1) * (x2 - x1))
        elif abs(y1 - h) < 1e-12:
            xs.append(x1)
    ymin = min(p[1] for p in poly); ymax = max(p[1] for p in poly)
    if len(xs) < 2 or not (ymin < h - 1e-12 and ymax > h + 1e-12):
        return 0.0
    return max(xs) - min(xs)


def depth(poly):
    """corner intrusion depth 1 - min over the square of max(x,y) (BL frame), 0 if none."""
    # min of max(x,y) over a convex polygon: attained on the boundary; sample edges finely + vertices
    best = min(max(x, y) for x, y in poly)
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        # the minimiser of max along an edge is where x = y if inside the edge
        if (x1 - y1) * (x2 - y2) < 0:
            t = (x1 - y1) / ((x1 - y1) - (x2 - y2))
            x = x1 + t * (x2 - x1); y = y1 + t * (y2 - y1)
            best = min(best, max(x, y))
    return max(0.0, 1 - best)


FRAMES = {  # corner -> map container coords to the corner's frame (corner at origin)
    'BL': lambda x, y, s: (x, y), 'BR': lambda x, y, s: (s - x, y),
    'TR': lambda x, y, s: (s - x, s - y), 'TL': lambda x, y, s: (x, s - y)}
WALLS = {'bottom': lambda x, y, s: (x, y), 'left': lambda x, y, s: (y, x),
         'right': lambda x, y, s: (y, s - x), 'top': lambda x, y, s: (x, s - y)}


def analyse(tag, sq, s):
    polys = [verts(*q) for q in sq]
    rec = dict(tag=tag, sigma=s, walls={}, corners={})
    for wname, fr in WALLS.items():
        tot = 0.0; ntouch = 0
        for P in polys:
            Q = [fr(x, y, s) for x, y in P]
            tot += chord(Q, H0)
            ntouch += min(p[1] for p in Q) < TOL
        rec['walls'][wname] = dict(sum_phi=tot, n_touch=ntouch, ok=bool(tot <= s + 1e-9 and ntouch <= 3))
    njam = 0; npon = 0
    for cname, fr in FRAMES.items():
        cp = [[fr(x, y, s) for x, y in P] for P in polys]
        intr = [i for i, Q in enumerate(cp) if depth(Q) > 1e-9]
        info = dict(intruders=intr, jam=False)
        # axis-aligned member with g <= 0.1 ?
        for i in intr:
            if tilt(sq[i][2]) > AX_TOL_DEG:
                continue
            xs = [p[0] for p in cp[i]]; ys = [p[1] for p in cp[i]]
            a, b = min(xs), min(ys)
            g = max(a, b)
            if g > 0.1:
                continue
            partners = [j for j in intr if j != i and tilt(sq[j][2]) <= math.degrees(math.asin(max(g, 1e-12))) + AX_TOL_DEG]
            if not partners:
                continue
            info['jam'] = True; njam += 1
            typ = 'x-side' if a > b + 1e-9 else ('y-side' if b > a + 1e-9 else 'corner')
            info.update(S=i, N=partners, a=a, b=b, g=g, type=typ,
                        partner_tilts=[tilt(sq[j][2]) for j in partners])
            # far edge of S in the retreat direction(s)
            pushers = []
            dirs = ['x'] if typ == 'x-side' else (['y'] if typ == 'y-side' else ['x', 'y'])
            for dr in dirs:
                if dr == 'x':
                    seg = ((a + 1, b), (a + 1, b + 1)); pwall = 'perp-to-x (the y=0 wall of the corner frame)'
                else:
                    seg = ((a, b + 1), (a + 1, b + 1)); pwall = 'perp-to-y (the x=0 wall of the corner frame)'
                for j in range(len(cp)):
                    if j == i:
                        continue
                    if poly_seg_dist(cp[j], *seg) < TOL:
                        Q = cp[j]
                        if dr == 'x':
                            ymin = min(p[1] for p in Q); ph = chord(Q, H0)
                        else:
                            ymin = min(p[0] for p in Q); ph = chord([(y, x) for x, y in Q], H0)
                        pushers.append(dict(sq=j, dir=dr, pusher_wall=pwall, y_min_above_pusher_wall=ymin,
                                            tilt=tilt(sq[j][2]), phi=ph, intruder=bool(depth(Q) > 1e-9),
                                            touches_pusher_wall=bool(ymin < TOL)))
            info['pushers'] = pushers
            info['P_ON'] = any(p['phi'] >= 1 - 1e-9 for p in pushers)
            npon += info['P_ON']
            # nick side: does the partner have a vertex in the left strip (x < a, 0 < y < 1)?
            nick_left = any((p[0] < a and 0 < p[1] < 1) for j in partners for p in cp[j])
            info['nick_left'] = bool(nick_left)
            info['pocket'] = pocket_eval(cp, i, a, b, nick_left, s)
            break
        rec['corners'][cname] = info
    rec['n_jam'] = njam; rec['n_jam_P_ON'] = npon
    return rec


# ---------------------------------------------------------------- Lemma FLOAT evaluation (PI follow-up)
def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for k in range(n):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def pocket_eval(cp, i_S, a, b, nick_left, s, grid=(400, 280)):
    """In the corner frame with the nick on the LEFT (diagonal-reflect if it is on the bottom):
    P = (a+1, a+2) x (0, h0); L = sum over Q != S of |chord_{h0}(Q) meet (a+1, a+2)|; stranded area
    of P by grid count; the squares meeting P."""
    if not nick_left:
        cp = [[(y, x) for x, y in Q] for Q in cp]
        a, b = b, a
    x_lo, x_hi = a + 1, a + 2
    L = 0.0; meets = []
    for j, Q in enumerate(cp):
        if j == i_S:
            continue
        xs = []
        n = len(Q)
        for k in range(n):
            (x1, y1), (x2, y2) = Q[k], Q[(k + 1) % n]
            if (y1 - H0) * (y2 - H0) < 0:
                xs.append(x1 + (H0 - y1) / (y2 - y1) * (x2 - x1))
        if len(xs) >= 2:
            cl, cr = min(xs), max(xs)
            L += max(0.0, min(cr, x_hi) - max(cl, x_lo))
    nx, ny = grid
    covered = 0; tot = 0
    for ix in range(nx):
        x = x_lo + (ix + 0.5) / nx
        for iy in range(ny):
            y = (iy + 0.5) * H0 / ny
            tot += 1
            for j, Q in enumerate(cp):
                if j != i_S and point_in_poly((x, y), Q):
                    covered += 1
                    if j not in meets:
                        meets.append(j)
                    break
    stranded = H0 * (1 - covered / tot)
    return dict(L=L, stranded_area_grid=stranded, bound_h0_1_minus_L=H0 * (1 - L), squares_meeting_P=meets,
                grid=grid, nick_reflected=(not nick_left))


def main():
    out = []
    with open(SRC, encoding='utf-8') as fh:
        for line in fh:
            r = json.loads(line)
            if not (r.get('exact_K0_BLOCKED') and r.get('z_polished')):
                continue
            z = [float(Fraction(v)) for v in r['z_polished']]
            sq = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11)]
            out.append(analyse(r['tag'] + '@' + '%.6f' % r['sigma_polished'], sq, z[33]))
    d = json.load(open(TRUMP, encoding='utf-8'))
    sq = [(float(q['cx']), float(q['cy']), float(q['theta'])) for q in d['squares']]
    out.append(analyse('Trump', sq, float(d['s'])))
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, 'corpusjam97.json'), 'w'), indent=1)
    for rec in out:
        print('==', rec['tag'], 'walls:', {w: (round(v['sum_phi'], 4), v['n_touch'], v['ok']) for w, v in rec['walls'].items()})
        for c, info in rec['corners'].items():
            if info['jam']:
                print('  JAM', c, 'S', info['S'], 'N', info['N'], 'g=%.4f' % info['g'], info['type'],
                      'partner tilts', [round(t, 4) for t in info['partner_tilts']], 'P_ON', info['P_ON'])
                for p in info['pushers']:
                    print('     pusher sq', p['sq'], p['dir'], 'y_min=%.4f' % p['y_min_above_pusher_wall'],
                          'tilt=%.3f' % p['tilt'], 'phi=%.4f' % p['phi'], 'touches', p['touches_pusher_wall'],
                          'intruder', p['intruder'])
            else:
                print('  ', c, 'intruders', info['intruders'], '(no jam)')


if __name__ == '__main__':
    main()
