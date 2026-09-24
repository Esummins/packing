"""A277 page: docs/residue_map/campaigns/A277-float2-room/float2_room.svg -- three true-scale panels of the BL corner at
side shat.  (a) the FLOAT2 witness with the floor toucher Y (C, D blue; X, Y orange; the four drops dashed; the strips
S_u(C), S_v(D) grey stipple).  (b) the dropped pair T_u(C), T_v(D) with the exact BL-sector admissible-centre region R
(grey stipple: two misses, undecided), its diameter (red) and one exact miss square (violet).  (c) A261's JAM corner
(A, C, X) with S_u(C) stippled: where an indirect holder would have to enter.  Every panel is geometry-checked here
(assertions) and the checks are written into results/page277_checks.json.  Undecided regions are grey stipple, never green.
    python page277.py   (< 1 min)"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for p in ('attempts/A259-normal-room/code', 'attempts/A261-box-meeters/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import room259 as R                                                    # noqa: E402
import geom259 as Z                                                    # noqa: E402
import local261 as L                                                   # noqa: E402

S = Z.SHAT
O = np.array([S / 2, S / 2])
OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A277-float2-room')
PX, PAD, W = 115.0, 30.0, 4.0
P = lambda A: Polygon([tuple(p) for p in A])
CHECKS = {}


def f(ox):
    return lambda p: (ox + PAD + p[0] * PX, PAD + (W - p[1]) * PX)


def poly(pts, tf, **kw):
    return '<polygon points="%s" %s/>' % (' '.join('%.2f,%.2f' % tf(p) for p in pts), ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items()))


def shp(g, tf, **kw):
    out = []
    for Pg in R.polys_of(g):
        out.append(poly(np.array(Pg.exterior.coords)[:-1], tf, **kw))
    return '\n'.join(out)


def frame(tf, title):
    s = [poly([(0, 0), (S, 0), (S, S), (0, S)], tf, fill='none', stroke='#333', stroke_width=1.5),
         poly([(0, 0), (1, 0), (1, 1), (0, 1)], tf, fill='none', stroke='#999', stroke_dasharray='3,3'),
         '<circle cx="%.1f" cy="%.1f" r="3" fill="#c00"/>' % tf(O),
         '<text x="%.1f" y="%.1f" font-size="13" font-family="sans-serif">%s</text>' % (tf((0, W))[0], tf((0, W))[1] - 8, title)]
    return '\n'.join(s)


def region_and_miss(Vs):
    parts, best = [], None
    for pd in np.arange(-45.0, 45.0, 1.0):
        psi = math.radians(pd)
        C = R.centre_set(Vs, S, psi)
        if C.is_empty:
            continue
        u, v = np.array([math.cos(psi), math.sin(psi)]), np.array([-math.sin(psi), math.cos(psi)])
        big = 3 * S
        for n, half in ((-v, sbox(-big, -big, S / 2, big)), (-u, sbox(-big, -big, big, S / 2))):
            p0, t = O + 0.5 * n, np.array([-n[1], n[0]])
            hp = Polygon([p0 + big * t, p0 + big * t + big * n, p0 - big * t + big * n, p0 - big * t])
            for Pg in R.polys_of(C.intersection(half).intersection(hp)):
                parts.append(Pg)
                A = np.array(Pg.exterior.coords)[:-1]
                m = float(((A - O) @ n).max()) - 0.5
                if best is None or m > best[0]:
                    best = (m, A[int(((A - O) @ n).argmax())], psi)
    U = unary_union(parts)
    H = U.convex_hull
    pts = np.array(H.exterior.coords)[:-1]
    d = np.linalg.norm(pts[:, None] - pts[None], axis=2)
    i, j = np.unravel_index(int(d.argmax()), d.shape)
    return U, float(d.max()), (pts[i], pts[j]), best


def main():
    wit = json.load(open(os.path.join(HERE, '..', 'results', 'float277_witness.json')))
    V = {k: L.verts(v[0], v[1], math.radians(v[2])) for k, v in wit['poses'].items()}
    V['Y'] = np.array(wit['Y_vertices'])
    TuC = V['C'] - [V['C'][:, 0].min(), 0]; TvC = V['C'] - [0, V['C'][:, 1].min()]
    TuD = V['D'] - [V['D'][:, 0].min(), 0]; TvD = V['D'] - [0, V['D'][:, 1].min()]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d">' % (3 * (W * PX + 2 * PAD), W * PX + 2 * PAD + 70),
           '<defs><pattern id="st" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.1" fill="#777"/></pattern></defs>',
           '<rect width="100%" height="100%" fill="white"/>']
    # (a)
    tf = f(0)
    svg.append(frame(tf, '(a) FLOAT2 witness + Y: all four drops blocked; P1 lands D (J_D > 0): not normal'))
    for T, F in ((TuC, 'C'), (TvC, 'C'), (TuD, 'D'), (TvD, 'D')):
        svg.append(shp(P(T).difference(P(V[F])), tf, fill='url(#st)', stroke='none'))
        svg.append(poly(T, tf, fill='none', stroke='#36c', stroke_dasharray='4,3', stroke_width=1))
    for k, col in (('C', '#36c'), ('D', '#36c'), ('X', '#e80'), ('Y', '#e80')):
        svg.append(poly(V[k], tf, fill=col, fill_opacity=0.25, stroke=col, stroke_width=1.5))
        c = V[k].mean(0)
        svg.append('<text x="%.1f" y="%.1f" font-size="14" font-family="sans-serif">%s</text>' % (tf(c)[0] - 5, tf(c)[1] + 5, k))
    ga = {a + b: float(P(V[a]).distance(P(V[b]))) for a in 'CDXY' for b in 'CDXY' if a < b}
    blk = {'Cu': P(TuC).intersection(P(V['X'])).area, 'Cv': P(TvC).intersection(P(V['D'])).area,
           'Du': P(TuD).intersection(P(V['C'])).area, 'Dv': P(TvD).intersection(P(V['Y'])).area}
    CHECKS['a'] = dict(min_gap=min(ga.values()), drop_blocker_areas=blk, X_misses_box=float(V['X'][:, 1].min()) >= 1,
                       Y_misses_box=float(V['Y'][:, 0].min()) >= 1, J_D=wit['P1_any_pose_J']['J_D'])
    assert CHECKS['a']['min_gap'] >= 0 and all(v > 1e-9 for v in blk.values()) and CHECKS['a']['X_misses_box'] and CHECKS['a']['Y_misses_box']
    # (b)
    ox = W * PX + 2 * PAD
    tf = f(ox)
    U, diam, (p1, p2), best = region_and_miss([TuC, TvD])
    svg.append(frame(tf, '(b) dropped pair T_u(C), T_v(D): BL-sector centres R (stipple), diam %.3f < 1: CAP-2' % diam))
    for T, col in ((TuC, '#36c'), (TvD, '#36c')):
        svg.append(poly(T, tf, fill=col, fill_opacity=0.25, stroke=col, stroke_width=1.5))
    svg.append(shp(U, tf, fill='url(#st)', stroke='#555', stroke_width=0.8))
    svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#c00" stroke_width="2"/>' % (tf(p1) + tf(p2)))
    q, psi = best[1], best[2]
    Q = Z.sq_verts(q[0], q[1], psi)
    fm = R.free_margin((q[0], q[1], psi), [TuC, TvD], S)
    co = R.contains_O((q[0], q[1], psi), S)
    svg.append(poly(Q, tf, fill='none', stroke='#909', stroke_width=1.5))
    CHECKS['b'] = dict(diam=diam, farthest=[p1.tolist(), p2.tolist()], miss_centre=q.tolist(), miss_tilt_deg=math.degrees(psi),
                       miss_free_margin=fm, miss_contains_O=co, worst_miss=best[0])
    assert diam < 1 and fm >= -1e-9 and co < 0
    # (c)
    ox = 2 * (W * PX + 2 * PAD)
    tf = f(ox)
    jam = json.load(open(os.path.join(ROOT, 'attempts', 'A261-box-meeters', 'results', 'jam261_polished.json')))['poses']
    J = {k: L.verts(*jam[k]) for k in ('A', 'C', 'X')}
    Tu = J['C'] - [J['C'][:, 0].min(), 0]
    g = float(J['X'][:, 1].min()) - float(J['C'][:, 1].max())
    svg.append(frame(tf, '(c) JAM corner (A261): S_u(C) stippled; X_low - C_top = %.3f < 0 (X holds C); indirect holder: none drawn' % g))
    svg.append(shp(P(Tu).difference(P(J['C'])), tf, fill='url(#st)', stroke='none'))
    svg.append(poly(Tu, tf, fill='none', stroke='#36c', stroke_dasharray='4,3'))
    for k, col in (('A', '#e80'), ('C', '#36c'), ('X', '#e80')):
        svg.append(poly(J[k], tf, fill=col, fill_opacity=0.25, stroke=col, stroke_width=1.5))
        c = J[k].mean(0)
        svg.append('<text x="%.1f" y="%.1f" font-size="14" font-family="sans-serif">%s</text>' % (tf(c)[0] - 5, tf(c)[1] + 5, k))
    CHECKS['c'] = dict(gap_X_low_minus_C_top=g, X_meets_Tu_area=P(J['X']).intersection(P(Tu)).area,
                       min_gap=min(P(J[a]).distance(P(J[b])) for a in 'ACX' for b in 'ACX' if a < b))
    assert CHECKS['c']['X_meets_Tu_area'] > 0 and CHECKS['c']['min_gap'] >= 0
    y0 = W * PX + 2 * PAD + 18
    for i, t in enumerate(['Grey stipple = drop strips (a, c) / admissible centres of BL-sector misses (b): undecided regions, never green.  Side shat = 3.877084; O red.',
                           'Checks per panel in attempts/A277-float2-room/results/page277_checks.json (gaps >= 0, blocker areas > 0, X/Y miss the open box, the miss square in (b) is exactly free and misses O).']):
        svg.append('<text x="%d" y="%d" font-size="12" font-family="sans-serif">%s</text>' % (PAD, y0 + 16 * i, t))
    svg.append('</svg>')
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'float2_room.svg'), 'w').write('\n'.join(svg))
    json.dump(CHECKS, open(os.path.join(HERE, '..', 'results', 'page277_checks.json'), 'w'), indent=1, default=float)
    print(json.dumps(CHECKS, indent=1, default=float))


if __name__ == '__main__':
    main()
