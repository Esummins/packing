"""A251 pages (docs/residue_map/campaigns/A251-ring-pocket/):
  ring_pocket.svg   the all-ADJ type-T ring at s-hat with its pocket, the two piercing points and
                    the inscribed disc of the one square that fits (PIERCE(1) residual 0);
  notch_bound.svg   Lemma MID-NOTCH: the wall's middle triangle, its inradius against 1/2, and the
                    poking free square whose CORNER enters the notch while its disc stays central;
  failing_box.svg   a box-valid panel: the cores of a box of half-width r (shrunk squares), the
                    over-approximated pocket, and the radius at which PIERCE(2) fails.
Every panel prints its geometry check in the note.
    python pages251.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
RES = os.path.join(ATT, 'results')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import geom251 as C                                                   # noqa: E402
import family251 as F                                                 # noqa: E402
import analytic251 as A                                               # noqa: E402
import cert251 as K                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402
import pages248 as P8                                                 # noqa: E402
from draw244 import Page                                              # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A251-ring-pocket')
BLUE, RED, GREEN, GREY, ORANGE = P8.BLUE, P8.RED, P8.GREEN, P8.GREY, P8.ORANGE
poly, geo_check = P8.poly, P8.geo_check
SW = 3.877084


def shape_path(pg, key, geom, fill, stroke, op=0.55):
    """draw a shapely polygon / multipolygon in panel coordinates."""
    from shapely.geometry import Polygon
    geoms = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
    for gm in geoms:
        if gm.is_empty or gm.area < 1e-9:
            continue
        rings = [list(gm.exterior.coords)] + [list(r.coords) for r in gm.interiors]
        d = ''
        for ring in rings:
            pts = [pg._t(key, p) for p in ring]
            d += 'M ' + ' L '.join('%.2f %.2f' % p for p in pts) + ' Z '
        pg.parts.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" '
                        'stroke-width="0.7" fill-rule="evenodd"/>' % (d, fill, op, stroke))


def circle(pg, key, c, r, col, dash=None):
    p = pg._t(key, c)
    q = pg._t(key, (c[0] + r, c[1]))
    pg.parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" '
                    'stroke-width="1.2"%s/>' % (p[0], p[1], abs(q[0] - p[0]), col,
                                                ' stroke-dasharray="%s"' % dash if dash else ''))


def ring_panel(pg, key, x, y, xr, s, eps, title, pts, extra):
    import twotilted249 as W
    polys, names, _ = W.ring_polys(list(xr), s, False)
    poses, _, _ = F.poses_of(xr, s)
    mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
    pg.panel(key, x, y, 330, 330, s)
    pg.frame(key, s, title)
    shape_path(pg, key, C.pocket_bar(mem, s), '#eef3df', '#8aa04a', 0.75)
    for V, nm in zip(polys, names):
        poly(pg, key, V, '#dfe8fb' if nm.startswith('B') else '#fbe3e3',
             BLUE if nm.startswith('B') else RED, None, op=0.55 if eps > 0 else 0.8)
    if eps > 0:
        for m in mem:
            poly(pg, key, np.array(C.G237.sq_verts(m[0], m[1], m[2], m[3])), '#ffffff', '#666', None, op=0.0, dash='2,2')
    for p in pts:
        pg.dot(key, p, GREEN, 3.0)
        circle(pg, key, p, 0.5, GREEN, '3,3')
    g = geo_check(polys, s, {})
    pg.note(x, y + 342, ['check: least pair gap %.2e, least wall gap %.2e, eight squares' % (g[0], g[1])] + extra)


def page_ring():
    xr = K.seed_ring()
    s = SW
    poses, _, _ = F.poses_of(xr, s)
    mem = [(p[0], p[1], p[2], 0.5) for p in poses]
    free = C.free_bins(mem, s, 1.0)
    r1 = C.pierce(mem, s, [(s / 2, s / 2)], free=free)
    e2, pts2 = C.shrink_tolerance2(poses, s)
    pg = Page(1040, 430, 'A251 ring pocket')
    ring_panel(pg, 'a', 24, 44, xr, s, 0.0, '(a) the all-ADJ ring at s-hat and its pocket', [(s / 2, s / 2)],
               ['pocket area %.3f; PIERCE(1) at the centre: residual %.2e => capacity <= 1' % (C.pocket_bar(mem, s).area, r1),
                'the green circle is the inscribed disc of radius 1/2 of any unit square containing the centre'])
    ring_panel(pg, 'b', 400, 44, xr, s, 0.0, '(b) the two piercing points of the box certificate', pts2,
               ['PIERCE(2) at %s' % ('; '.join('(%.3f, %.3f)' % tuple(p) for p in pts2)),
                'shrink tolerance eps* = %.4f (cores of half-side %.4f still certified)' % (e2, 0.5 - e2)])
    ring_panel(pg, 'c', 776, 44, xr, s, e2, '(c) the cores at the tolerated shrink', pts2,
               ['cores (dashed) = squares of half-side %.4f; the over-approximated pocket is the shaded region' % (0.5 - e2),
                'radius of the parameter box: %.4f in 17 coordinates' % K.radius_for_eps(e2)])
    pg.text(24, 26, 'A251 -- RING-POCKET(11): the pocket of the all-ADJ type-T ring, its piercing points and the box-valid cores', 12, weight='bold')
    pg.save(os.path.join(OUT, 'ring_pocket.svg'))


def page_notch():
    xr, s = K.seed_ring(), SW
    import twotilted249 as W
    polys, names, _ = W.ring_polys(list(xr), s, False)
    tB, dB = xr[0], xr[1]
    tBp, dBp = xr[12], xr[13]
    h = (s - dBp - math.cos(tBp)) - (dB + math.cos(tB))
    r = A.notch_inradius(tB, tBp, dB, dBp, s)
    pg = Page(700, 430, 'A251 notch bound')
    pg.panel('a', 24, 44, 330, 330, s)
    pg.frame('a', s, '(a) the wall x = 0 and its middle notch')
    for V, nm in zip(polys, names):
        poly(pg, 'a', V, '#dfe8fb' if nm.startswith('B') else '#fbe3e3',
             BLUE if nm.startswith('B') else RED, None, op=0.6)
    yB, yp = dB + math.cos(tB), s - dBp - math.cos(tBp)
    if h > 0:
        xs = h / (math.tan(tB) + math.tan(tBp))
        tri = [(0, yB), (0, yp), (xs, yB + xs * math.tan(tB))]
        pg.polyline([pg._t('a', p) for p in tri + [tri[0]]], ORANGE, 1.6)
    pg.note(24, 386, ['B: theta %.2f deg, delta %.3f; B\': theta %.2f deg, delta %.3f' % (math.degrees(tB), dB, math.degrees(tBp), dBp),
                      'base h = %.4f, triangle inradius %.4f < 1/2 (Lemma MID-NOTCH)' % (h, r),
                      'g(theta) + g(theta\') = %.4f > 2 (4 - s) = %.4f: the notch holds no disc of radius 1/2'
                      % (A.g(tB) + A.g(tBp), 2 * (4 - s)),
                      'check: h < 4 - s + sin + sin\' = %.4f (all-ADJ)' % (4 - s + math.sin(tB) + math.sin(tBp))])
    gm, td = A.g_min_exact()
    g2m, t2d = A.g2_min()
    pg.text(390, 70, 'Lemma MID-NOTCH', 11, weight='bold')
    pg.note(390, 88, ['g(t) = (1 + sin t)/cos t - 2 sin t', 'min g = %.5f at t = %.3f deg' % (gm, td),
                      'a disc of radius 1/2 in the middle notch needs', '  g(t) + g(t\') < 2 (4 - s) <= 0.36',
                      'but g + g\' >= %.5f: dead for every s > %.5f' % (2 * gm, 4 - gm),
                      '', 'robust form (separation margin 1/(2 sqrt2)):',
                      '  g2(t) = tan t / 2 + sec t / (2 sqrt2) - sin t',
                      '  min g2 = %.5f at %.3f deg => dead for s > %.5f' % (g2m, t2d, 4 - g2m),
                      '  the window [3.82, 4) clears it by %.4f' % (3.82 - (4 - g2m)),
                      '', 'consequence: no unit square of the pocket has its',
                      'INSCRIBED DISC in a wall notch -- A249\'s poking',
                      'square enters the notch with a CORNER only.'])
    pg.text(24, 26, 'A251 -- Lemma MID-NOTCH: the middle notch of a wall of an all-ADJ ring holds no disc of radius 1/2', 12, weight='bold')
    pg.save(os.path.join(OUT, 'notch_bound.svg'))


def page_failing():
    xr, s = K.seed_ring(), SW
    poses, _, _ = F.poses_of(xr, s)
    pg = Page(1040, 430, 'A251 failing box')
    for i, (key, xx, rad) in enumerate((('a', 24, 0.0312), ('b', 400, 0.05), ('c', 776, 0.10))):
        eps = K.eps_of_radius(rad)
        mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
        free = C.free_bins(mem, s + rad, 2.0)
        p1 = C.pierce(mem, s + rad, [((s + rad) / 2, (s + rad) / 2)], free=free)
        p2, pts = C.best_pierce2(mem, s + rad, free, r=1.0, g=5)
        pg.panel(key, xx, 44, 330, 330, s + rad)
        pg.frame(key, s + rad, '(%s) box half-width %.4f' % (key, rad))
        shape_path(pg, key, C.pocket_bar(mem, s + rad), '#eef3df', '#8aa04a', 0.75)
        for m in mem:
            poly(pg, key, np.array(C.G237.sq_verts(m[0], m[1], m[2], m[3])), '#dfe8fb', BLUE, None, op=0.6)
        for p in pts:
            pg.dot(key, p, GREEN, 3.0)
        pg.note(xx, 386, ['core shrink eps = %.4f, core half-side %.4f' % (eps, 0.5 - eps),
                          'PIERCE(1) %.3e, best PIERCE(2) %.3e -> %s' % (p1, p2, 'CERTIFIED' if min(p1, p2) <= 1e-9 else 'FAILS'),
                          'boxes needed at this radius: %.3g (17 coordinates, D4 quotient)' % K.box_count(rad),
                          'check: over-pocket area %.3f, container side %.4f' % (C.pocket_bar(mem, s + rad).area, s + rad)])
    pg.text(24, 26, 'A251 -- the price: the box radius the PIERCE certificate tolerates, and where it fails', 12, weight='bold')
    pg.save(os.path.join(OUT, 'failing_box.svg'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    page_ring()
    page_notch()
    page_failing()
    print('pages written to', OUT)
