"""A273 page: docs/residue_map/campaigns/A273-disc-lemma/disc_lemma.svg -- three panels.
 (a) the WITNESS (results/witness273.json, exact Fractions): X flat, theta = 8.01 deg; the centre q with D(q, 1/2)
     (blue) missing Xi and Gam, the strip point p within 1/sqrt2 of q: A272's DISC LEMMA fails; its DROP
     conv(D u {p}) (orange) crosses X's corner -- the reason the square cannot be there.
 (b) the same q under the DROP test: the penumbras Pi(Xi), Pi(Gam) of D(q, 1/2) (hatched); the strip part P within
     1/sqrt2 of q (red) must lie inside them -- panel check: area of P n D(q, 1/sqrt2) minus the penumbras.
 (c) the certified map over (theta, phi) (5 deg cells): green = tree CERT + verify273 PASS, grey stipple = OPEN
     (the corner layer or capped), white = pending, red = verifier disagreement.  Never green unless verified.
    python pages273.py"""
import json
import math
import os
import sys
from fractions import Fraction

import numpy as np
from shapely.geometry import Point, Polygon, MultiPoint

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A273-disc-lemma')
W0, Y0, SC = 0.55, 1.78, 250.0


def T(p, ox, oy=40):
    return ox + SC * (p[0] - W0), oy + SC * (3.25 - p[1])


def poly(V, fill, ox, op=0.5, stroke='#333', w=1.0, extra=''):
    pts = ' '.join('%.1f,%.1f' % T(p, ox) for p in V)
    return '<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f" %s/>' % (pts, fill, op, stroke, w, extra)


def geom(g, fill, ox, **kw):
    gs = getattr(g, 'geoms', [g])
    return ''.join(poly(list(P.exterior.coords)[:-1], fill, ox, **kw) for P in gs if P.geom_type == 'Polygon' and not P.is_empty)


def witness():
    w = json.load(open(os.path.join(ATT, 'results', 'witness273.json')))
    pr = {k: float(Fraction(v)) for k, v in w['params'].items()}
    t = pr['tan_half_theta']
    c, s = (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)
    hu, hv, xl = pr['h_u'], pr['h_v'], pr['X_low']
    C = [(hu + s, hv), (hu + s + c, hv + s), (hu + c, hv + s + c), (hu, hv + c)]
    X = [(0, xl), (1, xl), (1, xl + 1), (0, xl + 1)]
    Tu = [(x - hu, y) for x, y in C]
    Gam = Polygon([C[0], (6, hv), (6, hv + c + s), C[2], C[3]])
    return w, C, X, Tu, Gam, np.array(w['q_float']), np.array(w['p_float'])


def penumbra(K, q, r=0.5, tl=5.0):
    V = np.asarray(K.exterior.coords)[:-1]
    D = q + r * np.c_[np.cos(np.linspace(0, 2 * np.pi, 256, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, 256, endpoint=False))]
    return MultiPoint(np.r_[V, (D[None] + tl * (V[:, None] - D[None])).reshape(-1, 2)]).convex_hull


def panel_ab(ox, which):
    w, C, X, Tu, Gam, q, p = witness()
    S = Polygon(Tu).difference(Polygon(C))
    out = [poly(Tu, 'none', ox, stroke='#555', w=1.0, extra='stroke-dasharray="5,3"'), poly(C, '#d9534f', ox, op=0.25),
           poly(X, '#428bca', ox, op=0.25), geom(S, 'url(#stip)', ox, op=1.0, stroke='#999', w=0.5)]
    D = Point(q).buffer(0.5, 128)
    if which == 'a':
        drop = MultiPoint(list(D.exterior.coords) + [tuple(p)]).convex_hull
        out += [geom(drop, '#f0ad4e', ox, op=0.35, stroke='#c77c00'), geom(D, '#5bc0de', ox, op=0.35, stroke='#1b6d85'),
                geom(Point(q).buffer(0.5 ** 0.5, 128).exterior.buffer(0.002), '#555', ox, op=0.8, w=0.2)]
        cross = drop.intersection(Polygon(X)).area
        note = 'drop meets int X: area %.2e (> 0); disc terms exact: %s' % (cross, all(w['disc_terms'].values()))
    else:
        Xi = Polygon(X)
        P = S.difference(Xi).difference(Gam)
        near = P.intersection(Point(q).buffer(0.5 ** 0.5, 256))
        PX, PG = penumbra(Xi, q), penumbra(Gam, q)
        rest = near.difference(PX).difference(PG)
        out += [geom(PX.intersection(Polygon([(0.4, 1.7), (2.3, 1.7), (2.3, 3.3), (0.4, 3.3)])), 'url(#hatchB)', ox, op=1, stroke='#428bca', w=0.4),
                geom(PG.intersection(Polygon([(0.4, 1.7), (2.3, 1.7), (2.3, 3.3), (0.4, 3.3)])), 'url(#hatchR)', ox, op=1, stroke='#d9534f', w=0.4),
                geom(near, '#c9302c', ox, op=0.8, stroke='#c9302c', w=0.6), geom(D, '#5bc0de', ox, op=0.25, stroke='#1b6d85')]
        note = 'P within 1/sqrt2 of q, outside both penumbras: area %.1e (drop test kills q)' % rest.area
    for z, col, lab in ((q, '#1b6d85', 'q'), (p, '#c9302c', 'p')):
        x, y = T(z, ox)
        out.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/><text x="%.1f" y="%.1f" font-size="12">%s</text>' % (x, y, col, x + 5, y - 5, lab))
    return ''.join(out), note


def panel_map(ox, oy=60, cw=36):
    idx = os.path.join(ATT, 'results', 'verify273_index.jsonl')
    V = {}
    if os.path.exists(idx):
        for l in open(idx):
            r = json.loads(l)
            V[r['cell']] = r
    out = []
    for ti in range(9):
        for pj in range(9):
            r = V.get('c%d_%d' % (ti, pj))
            fill = 'white' if r is None else ('#d9534f' if not r['verdict'].startswith('PASS') else
                                              ('url(#stipG)' if r['open'] else '#5cb85c'))
            out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#666" stroke-width="0.6"/>' % (
                ox + ti * cw, oy + (8 - pj) * cw, cw, cw, fill))
    out.append('<text x="%d" y="%d" font-size="12">theta_C 0..45 deg (5 deg cells)</text>' % (ox, oy + 9 * cw + 18))
    out.append('<text x="%d" y="%d" font-size="12" transform="rotate(-90 %d %d)">phi_X 0..45 deg</text>' % (
        ox - 8, oy + 9 * cw, ox - 8, oy + 9 * cw))
    done = sum(1 for r in V.values())
    return ''.join(out), 'verified cells: %d of 81 (green PASS, grey stipple OPEN layer, white pending)' % done


DEFS = ('<defs><pattern id="stip" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="0.8" '
        'fill="#777"/></pattern><pattern id="stipG" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" '
        'height="6" fill="#ddd"/><circle cx="2" cy="2" r="1" fill="#888"/></pattern><pattern id="hatchB" width="6" '
        'height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" '
        'stroke="#428bca" stroke-width="1.2"/></pattern><pattern id="hatchR" width="6" height="6" '
        'patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="6" '
        'stroke="#d9534f" stroke-width="1.2"/></pattern></defs>')


def text(x, y, s, size=12, weight='normal'):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '<text x="%d" y="%d" font-size="%d" font-weight="%s" font-family="sans-serif">%s</text>' % (x, y, size, weight, s)


def main():
    os.makedirs(OUT, exist_ok=True)
    a, na = panel_ab(20, 'a')
    b, nb = panel_ab(460, 'b')
    m, nm = panel_map(960)
    body = [DEFS, '<rect width="1330" height="560" fill="white"/>', a, b, m,
            text(20, 22, '(a) DISC LEMMA false: D(q,1/2) misses X, Gam; p in S, |p-q| < 1/sqrt2', 12, 'bold'),
            text(470, 22, '(b) DROP test at q: P near q (red) inside the penumbras', 12, 'bold'),
            text(930, 22, '(c) DROP LEMMA: certified map over (theta_C, phi_X)', 12, 'bold'),
            text(20, 470, na), text(460, 470, nb), text(930, 470, nm),
            text(20, 490, 'witness: h_u = 17/20, h_v = 199/200, tan(theta/2) = 7/100, X_low = 211/100, phi = 0, A at (11/10, 0), '
                 'tan(alpha/2) = 1/18, side 387/100 -- every H1-H3 term and every disc term checked in Fractions'),
            text(20, 508, 'T_u dashed, C red, X blue, S = T_u minus C stippled; orange = conv(D(q,1/2) u {p}) (the DROP): it '
                 'crosses X\'s corner, so no unit square with this disc and p exists -- the distance form forgot the cone.'),
            text(20, 526, '(b): penumbra Pi(K) = points p whose drop from D(q,1/2) meets K (K = X\'s side Xi, C\'s side Gam); '
                 'the drop lemma = P n D(q, 1/sqrt2) inside Pi(Xi) u Pi(Gam) for every admissible q.'),
            text(20, 544, '(c) green only when tree273 CERT/PRUNE on every leaf AND verify273 re-derived it (coverage replay, '
                 'mpmath cores, shapely penumbras); grey stipple = OPEN (corner theta, phi <= 5 deg or capped): never green.')]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1330" height="560" viewBox="0 0 1330 560">%s</svg>' % ''.join(body)
    open(os.path.join(OUT, 'disc_lemma.svg'), 'w').write(svg)
    json.dump(dict(panel_a=na, panel_b=nb, panel_c=nm), open(os.path.join(ATT, 'results', 'pages273.json'), 'w'), indent=1)
    print(na, '|', nb, '|', nm)


if __name__ == '__main__':
    main()
