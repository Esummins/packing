"""A274 page: docs/residue_map/campaigns/A274-flat-corner/r1_274.svg -- one panel per ring inequality that FAILS on the
near-flat corner (r1_274_adv.json): the exact-checked minimiser drawn at true scale (left: the corner; right: a
true-scale zoom of the channel at C's top vertex), with C (blue), T_u (dashed), S = T_u minus C (grey stipple:
undecided, never green), X (orange), A (violet), the open box (dotted), the line a = a* across C's upper-left edge
(red dash-dot) and the room segment rho(C_top) (red).  Geometry check: every drawn polygon is ringdom271.squares of
the reported configuration (asserted), and the note repeats its exact H1-H3 verdict."""
import html
import json
import math
import os

import numpy as np
from shapely.geometry import Polygon

import r1_274 as M

R = M.R
OUT = os.path.join(R.ROOT, 'docs', 'residue_map', 'campaigns', 'A274-flat-corner')
NOTE = {'U3': 'wedge mouth a2 - a* vs half the wedge width w_max/2',
        'U4': 'room right of X at C_top: rho(C_top) = l_C(C_top) - r_X(C_top) must be < 1',
        'U5': "X's right vertex a_R - sin(beta+) must reach a* (T_u's top edge end)",
        'U6': 'h_u + cos(theta) - cos(phi) must be < 1', 'U8': 'X_top - C_top - 1/sqrt2'}


def poly(P, f, **kw):
    pts = ' '.join('%.2f,%.2f' % f(p) for p in P)
    return '<polygon points="%s" %s/>' % (pts, ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items()))


def line(a, b, f, **kw):
    (x1, y1), (x2, y2) = f(a), f(b)
    return '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" %s/>' % (
        x1, y1, x2, y2, ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items()))


def scene(q, f):
    C, X, A, Tu = R.squares(q)
    S = Polygon(Tu).difference(Polygon(C))
    out = []
    for G in getattr(S, 'geoms', [S]):
        if G.geom_type == 'Polygon' and G.area > 0:
            out.append(poly(np.array(G.exterior.coords), f, fill='url(#stip)', stroke='#888', stroke_width=0.5))
    out.append(poly(M.R.BOX, f, fill='none', stroke='#555', stroke_dasharray='2,3'))
    out.append(poly(Tu, f, fill='none', stroke='#1f5fa8', stroke_dasharray='5,3'))
    out.append(poly(C, f, fill='#1f5fa8', fill_opacity=0.25, stroke='#1f5fa8'))
    out.append(poly(X, f, fill='#e07b00', fill_opacity=0.25, stroke='#e07b00'))
    out.append(poly(A, f, fill='#7a3fb0', fill_opacity=0.2, stroke='#7a3fb0'))
    hu, hv, th = q[0], q[1], q[2]
    c, s = math.cos(th), math.sin(th)
    L, e, n = np.array([hu, hv + c]), np.array([c, s]), np.array([-s, c])
    P0 = L + (1 - hu * c) * e                                           # a = a*
    out.append(line(P0 - 0.3 * n, P0 + 0.6 * n, f, stroke='#c00', stroke_dasharray='6,2,1,2'))
    ctop = hv + c + s
    lC = hu + c                                                         # C's top vertex = l_C(C_top)
    cut = Polygon(X).intersection(Polygon([(-1, ctop - 1e-9), (5, ctop - 1e-9), (5, ctop + 1e-9), (-1, ctop + 1e-9)]))
    if not cut.is_empty:                                                # room segment at C_top: r_X -> l_C
        out.append(line((cut.bounds[2], ctop), (lC, ctop), f, stroke='#c00', stroke_width=2))
    return out, C, X, A, Tu, ctop, lC


def panel(key, row, ox, oy):
    q = np.array([row['config'][k] for k in ('h_u', 'h_v')] + [row['config']['theta_deg'] * M.DEG, row['config']['X_low'],
                  row['config']['phi_deg'] * M.DEG, row['config']['a_x'], row['config']['alpha_deg'] * M.DEG,
                  row['config']['side']])
    C, X, A, Tu = R.squares(q)
    tests, qf, _ = M.exact_check(q)
    assert np.allclose(R.squares(qf)[0], C, atol=1e-9) and all(tests.values()) == row['exact_H1H3']
    sc1, y1 = 80.0, float(X[:, 1].max()) + 0.1
    f1 = lambda p: (ox + 10 + sc1 * (p[0] + 0.1), oy + 30 + sc1 * (y1 - p[1]))      # noqa: E731
    g, C, X, A, Tu, ctop, lC = scene(q, f1)
    xm = min(float(X[1][0]), lC)                                        # zoom at the channel mouth: X's right vertex
    Tx = np.array([xm + 0.12, q[1] + math.cos(q[2]) + (xm - q[0]) * math.tan(q[2])])
    sc2 = 900.0
    f2 = lambda p: (ox + 420 + sc2 * (p[0] - Tx[0] + 0.32), oy + 150 + sc2 * (Tx[1] - p[1]))  # noqa: E731
    g2 = scene(q, f2)[0]
    cfg = row['config']
    txt = ['<text x="%d" y="%d" font-size="13" font-weight="bold">(%s) %s FAILS: margin %+.5f</text>' % (
        ox + 10, oy + 18, key.lower(), key, row['min_margin'])]
    notes = [NOTE[key],
             'h_u %.4f  h_v %.4f  theta %.3f deg  phi %.3f deg  D = C_top - X_low %.5f' % (
                 cfg['h_u'], cfg['h_v'], cfg['theta_deg'], cfg['phi_deg'], cfg['D']),
             'X_low %.5f  A (%.4f, 0) tilt %.2f deg  side %.4f  beta %.3f deg' % (
                 cfg['X_low'], cfg['a_x'], cfg['alpha_deg'], cfg['side'], row['conditions']['beta_deg']),
             'exact H1-H3 (Fractions, SAT): %s; U3 %+.4f U4 %+.4f U5 %+.4f U6 %+.4f U8 %+.4f' % (
                 'ALL TRUE' if row['exact_H1H3'] else 'FAILED', *[row['conditions'][k] for k in M.KEYS]),
             'right: true-scale zoom x %.0f at the channel mouth by the right vertex of X (window 0.45 x 0.25)' % sc2]
    for i, t in enumerate(notes):
        txt.append('<text x="%d" y="%d" font-size="11">%s</text>' % (ox + 10, oy + 330 + 14 * i, html.escape(t)))
    clip = '<clipPath id="z%s"><rect x="%d" y="%d" width="405" height="225"/></clipPath>' % (key, ox + 420, oy + 40)
    return [clip] + g + ['<g clip-path="url(#z%s)">' % key] + g2 + [
        '</g><rect x="%d" y="%d" width="405" height="225" fill="none" stroke="#333"/>' % (ox + 420, oy + 40)] + txt


def main():
    adv = json.load(open(os.path.join(M.RES, 'r1_274.json')))['adv']['results']      # {adv, curve} merged
    bad = [k for k in M.KEYS if adv[k]['min_margin'] <= 0]
    os.makedirs(OUT, exist_ok=True)
    W_, H_ = 860, 420 * max(1, len(bad)) + 20
    body = []
    for i, k in enumerate(bad):
        body += panel(k, adv[k], 0, 10 + 420 * i)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (W_, H_),
           '<defs><pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.7"'
           ' fill="#888"/></pattern></defs><rect width="100%" height="100%" fill="white"/>'] + body + ['</svg>']
    open(os.path.join(OUT, 'r1_274.svg'), 'w').write('\n'.join(svg))
    print('page: %d panels (%s)' % (len(bad), ', '.join(bad)))
