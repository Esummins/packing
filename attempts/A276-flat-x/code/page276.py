"""A276 page: docs/residue_map/campaigns/A276-flat-x/flat_x.svg -- three true-scale zooms of the corner at X FLAT
(theta = 5, 2, 0.5 deg; h_u = 0.9, h_v = 0.9, D = D_max / 2): C (blue), T_u (dashed), S = T_u \\ C (grey stipple:
undecided-by-convention, never green), X (orange), the resting flat Q with corner (1, C_top) (violet outline), the
sliver Sigma (hatched), the clearance segment from (1, C_top) to T_u's upper-right edge (red).  Geometry check per
panel (asserted, and written into the note): X ∩ int C = ∅, X meets int T_u, Q ∩ int C = ∅ = Q ∩ int X,
area(Q ∩ T_u) = 0, dist((1, C_top), T_u) = (1 - c) c to 1e-12."""
import html
import math
import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check276 as K                                                  # noqa: E402

OUT = os.path.join(HERE, '..', '..', '..', 'docs', 'residue_map', 'campaigns', 'A276-flat-x')


def poly(P, f, **kw):
    pts = ' '.join('%.2f,%.2f' % f(p) for p in P)
    return '<polygon points="%s" %s/>' % (pts, ' '.join('%s="%s"' % (k.replace('_', '-'), v) for k, v in kw.items()))


def panel(th_deg, ox, W=300, H=300):
    th = math.radians(th_deg)
    c, s = math.cos(th), math.sin(th)
    hu, hv = 0.9, 0.9
    Lh, Ctop = hv + c, hv + c + s
    Dmax = (hu + c - 1) * math.tan(th)
    D = Dmax / 2
    Xlow = Ctop - D
    C = K.sq((hu + s, hv), th)
    Tu = C - np.array([hu, 0.0])
    X = np.array([[0, Xlow], [1, Xlow], [1, Xlow + 1], [0, Xlow + 1]], float)
    Q = K.sq((1.0, Ctop), 0.0)
    PC, PT, PX, PQ = Polygon(C), Polygon(Tu), Polygon(X), Polygon(Q)
    EPS = 1e-12                      # float vertex rounding (hv + s + c vs hv + c + s); exact contacts are areas ~1e-17
    assert PX.intersection(PC).area < EPS and PX.intersection(PT).area > 1e-6
    assert PQ.intersection(PC).area < EPS and PQ.intersection(PX).area < EPS and PQ.intersection(PT).area < EPS
    dist = Point(1.0, Ctop).distance(PT)
    assert abs(dist - (1 - c) * c) < 1e-12
    # zoom window: half-width z around (1, C_top), true scale (equal x/y)
    z = max(3.0 * (1 - c), 1.5 * Dmax, 1.5 * hu * s)
    sc = (W - 20) / (2 * z)
    f = lambda p: (ox + 10 + (p[0] - (1 - z)) * sc, 30 + (Ctop + z - p[1]) * sc)
    out = ['<clipPath id="clip%d"><rect x="%d" y="30" width="%d" height="%d"/></clipPath>' % (ox, ox + 10, W - 20, H - 40)]
    out.append('<g clip-path="url(#clip%d)">' % ox)
    S = PT.difference(PC)
    for G in getattr(S, 'geoms', [S]):
        if G.geom_type == 'Polygon' and G.area > 0:
            out.append(poly(np.array(G.exterior.coords), f, fill='url(#stip)', stroke='#888', stroke_width=0.6))
    y1, y2 = Lh + (1 - hu) * math.tan(th), Lh + math.tan(th / 2)
    r_Tu = lambda y: c + (Ctop - y) * math.tan(th)
    Sig = Polygon([(1, y1), (1, y2), (r_Tu(y1), y1)]).intersection(S)
    if Sig.area > 0:
        out.append(poly(np.array(Sig.exterior.coords), f, fill='url(#hatch)', stroke='#444', stroke_width=0.6))
    out.append(poly(Tu, f, fill='none', stroke='#1f5fa8', stroke_dasharray='5,3'))
    out.append(poly(C, f, fill='#1f5fa8', fill_opacity=0.2, stroke='#1f5fa8'))
    out.append(poly(X, f, fill='#e8772e', fill_opacity=0.25, stroke='#e8772e'))
    out.append(poly(Q, f, fill='none', stroke='#7a3fb0', stroke_width=1.2))
    foot = np.array([c, Ctop]) + (1 - c) * s * np.array([s, -c])
    (x1, y1s), (x2, y2s) = f((1.0, Ctop)), f(foot)
    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#c81e1e" stroke-width="1.5"/>' % (x1, y1s, x2, y2s))
    out.append('</g>')
    out.append('<text x="%d" y="20" font-size="11" font-family="sans-serif">theta = %g deg, phi = 0, h_u = %g, D = D_max/2 = %.5f; zoom half-width %.4f, true scale</text>' % (ox + 10, th_deg, hu, D, z))
    note = ('geometry-checked: X∩intC=∅, X meets intT_u, Q∩intC=Q∩intX=∅, area(Q∩T_u)=0; dist((1,C_top),T_u) = %.3e = (1-c)c; '
            'probe split (1-c)c/2 = %.3e; Sigma width <= %.2e' % (dist, dist / 2, math.tan(th) ** 2 * (hu - c / (1 + c))))
    out.append('<text x="%d" y="%d" font-size="8.5" font-family="sans-serif">%s</text>' % (ox + 10, H, html.escape(note)))
    return '\n'.join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    W, H = 300, 300
    body = [panel(th, i * W, W, H) for i, th in enumerate((5.0, 2.0, 0.5))]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif">' % (3 * W, H + 40),
           '<defs><pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.7" fill="#999"/></pattern>',
           '<pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0,4 L4,0" stroke="#555" stroke-width="0.6"/></pattern></defs>',
           '<rect width="100%" height="100%" fill="white"/>'] + body + [
           '<text x="10" y="%d" font-size="9">A276 flat_x.svg: the resting flat Q (violet) with corner (1, C_top) at X FLAT; S grey stipple (undecided by convention), Sigma hatched (S right of x = 1, width O(theta^2)), red = clearance (1-c)c to T_u (dashed). Every panel geometry-checked (assertions in page276.py).</text>' % (H + 32),
           '</svg>']
    with open(os.path.join(OUT, 'flat_x.svg'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(svg))
    print('wrote', os.path.join(OUT, 'flat_x.svg'))


if __name__ == '__main__':
    main()
