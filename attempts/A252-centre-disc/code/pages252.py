"""A252 pages (docs/residue_map/campaigns/A252-centre-disc/):
  mouth_witness.svg  the far ring: the centre set C, the far disc in a corner MOUTH beyond the
                     circle of radius 1/sqrt3 about O, and the corner frame with the flat limit;
  centre_set.svg     A249's ring at s-hat: C with its smallest enclosing circle, and the POKER in
                     place (the residual centre set is empty);
  notch_disc.svg     the flat-flat corner limit: the corner notch holds a disc of radius 1/2 but
                     no unit square -- why every disc-only criterion is lossy there.
Every panel prints its geometry check in its note.
    python pages252.py
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Point, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')
sys.path.insert(0, HERE)
import disc252 as D                                                   # noqa: E402
import lemmas252 as L                                                 # noqa: E402
import geom249 as T                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402
sys.path.insert(0, os.path.join(D.ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
from draw244 import Page                                              # noqa: E402

OUT = os.path.join(D.ROOT, 'docs', 'residue_map', 'campaigns', 'A252-centre-disc')
BLUE, RED, GREEN, GREY, ORANGE, PURPLE = '#3b6fd6', '#d63b3b', '#3a9d5d', '#999', '#e08a1e', '#7a3fb0'


def poly(pg, key, V, fill, stroke, label=None, op=0.8, dash=None, width=1.3):
    pts = ' '.join('%.2f,%.2f' % pg._t(key, p) for p in V)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pg.parts.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"%s/>'
                    % (pts, fill, op, stroke, width, d))
    if label:
        p = pg._t(key, np.asarray(V).mean(axis=0))
        pg.text(p[0], p[1] + 3, label, 8.5, '#111', anchor='middle')


def shape(pg, key, geom, fill, stroke, op=0.6):
    for gm in D.geoms(geom):
        rings = [list(gm.exterior.coords)] + [list(r.coords) for r in gm.interiors]
        d = ''
        for ring in rings:
            d += 'M ' + ' L '.join('%.2f %.2f' % pg._t(key, p) for p in ring) + ' Z '
        pg.parts.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="0.8" fill-rule="evenodd"/>'
                        % (d, fill, op, stroke))


def circle(pg, key, c, r, col, dash=None, width=1.2):
    p, q = pg._t(key, c), pg._t(key, (c[0] + r, c[1]))
    pg.parts.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                    % (p[0], p[1], abs(q[0] - p[0]), col, width, ' stroke-dasharray="%s"' % dash if dash else ''))


def geo(polys, s):
    pg = min([G.poly_gap(polys[i], polys[j]) for i in range(len(polys)) for j in range(i)] + [9.0])
    wg = min(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()) for V in polys)
    return pg, wg


def ring_panel(pg, key, x, y, xr, s, title, discs, notes, sec=None, extra_polys=()):
    polys, names = D.ring(xr, s)
    allp = list(polys) + list(extra_polys)
    C = D.centre_set(allp, s)
    pg.panel(key, x, y, 330, 330, s)
    pg.frame(key, s, title)
    shape(pg, key, D.pocket(allp, s), '#f4f6ea', '#b8c48a', 0.5)
    for V, nm in zip(polys, names):
        poly(pg, key, V, '#dfe8fb' if nm.startswith('B') else '#fbe3e3', BLUE if nm.startswith('B') else RED, nm, op=0.7)
    for V in extra_polys:
        poly(pg, key, V, '#e6d9f5', PURPLE, 'poker', op=0.8)
    shape(pg, key, C, '#3a9d5d', GREEN, 0.45)
    O = (s / 2, s / 2)
    pg.dot(key, O, '#111', 2.5)
    circle(pg, key, O, D.R3, ORANGE, '4,3')
    for q, col in discs:
        pg.dot(key, q, col, 3.0)
        circle(pg, key, q, 0.5, col)
    if sec:
        circle(pg, key, sec[1], sec[0], PURPLE, '2,2')
    g = geo(allp, s)
    dmin = [min(Polygon(V).distance(Point(q)) for V in allp) for q, _ in discs]
    pg.note(x, y + 342, ['check: least pair gap %.2e, least wall gap %.2e; far disc to nearest square %s' %
                         (g[0], g[1], ', '.join('%.4f' % v for v in dmin))] + notes)
    return C


def best_far_ring():
    fn = os.path.join(RES, 'adv252.json')
    if os.path.exists(fn):
        best = json.load(open(fn, encoding='utf-8'))
        rows = [r for r in best.values() if r['metric'] == 'far_O' and r['margin'] >= 0]
        if rows:
            r = max(rows, key=lambda r: r['value'])
            return r['x'], float(r['side']), r['metrics']
    m = D.metrics(D_XW, D.SW)
    return D_XW, D.SW, m


SEED = [0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891]
D_XW = list(SEED[:4]) + list(SEED[4:8]) + list(SEED[:4]) + list(SEED[4:8])


def page_mouth():
    xr, s, m = best_far_ring()
    fq = tuple(m['far_pt'])
    pg = Page(1040, 430, 'A252 mouth witness')
    ring_panel(pg, 'a', 24, 44, xr, s, '(a) the far ring at s = %.4f: C (green) and the far disc' % s, [(fq, RED)],
               ['far_O = %.4f vs 1/sqrt3 = %.5f (orange circle); ring margin %+.4f; sec_r %.4f, halves %.4f, disp3 %.4f' %
                (m['far_O'], D.R3, m['margin'], m.get('sec_r', 0), m.get('halves_diam', 0), m.get('disp3', 0)),
                'contacts of the far disc: %s' % ', '.join('%s %.3f' % (n, v) for n, v in m['contacts'][:3])],
               sec=(m['sec_r'], tuple(m['sec_c'])) if m.get('sec_c') else None)
    # (b) the corner frame near the flat limit and the mouth point
    tB, dB, tA, dA = math.radians(87), 0.96, math.radians(88.5), 0.985
    B, A = T.wall_square(tB, dB), T.floor_square(tA, dA)
    q = L.mouth_centre(tB, dB, tA, dA)
    pg.panel('b', 400, 44, 330, 330, 2.6, win=(0, 2.6, 0, 2.6))
    pg.frame('b', 2.6, '(b) a corner near the flat limit: the MOUTH disc')
    for r in ((0, 1, 0, 1), (0, 1, 1, 2), (1, 2, 0, 1)):
        pg.rect('b', r, '#fff8e6', '#ccc', 0.6)
    poly(pg, 'b', B, '#dfe8fb', BLUE, 'B', op=0.75)
    poly(pg, 'b', A, '#fbe3e3', RED, 'A', op=0.75)
    pg.dot('b', q, RED, 3.0)
    circle(pg, 'b', q, 0.5, RED)
    pg.dot('b', (1.5, 1.5), ORANGE, 3.0)
    dB_, dA_ = Polygon(B).distance(Point(q)), Polygon(A).distance(Point(q))
    pg.note(400, 386, ['check: B (%.0f deg, %.3f), A (%.1f deg, %.3f), gap(B, A) = %.4f; mouth centre (%.3f, %.3f) at %.4f / %.4f from B / A' %
                       (math.degrees(tB), dB, math.degrees(tA), dA, G.poly_gap(B, A), q[0], q[1], dB_, dA_),
                       'flat limit (orange): (3/2, 3/2), at (s/2 - 3/2) sqrt2 from O = %.4f at s-hat > 1/sqrt3 for s > %.4f' %
                       (D.flat_limit_far(D.SW), D.S_FLAT)])
    pg.note(776, 60, ['(c) Lemma CENTRE-DISC about O is FALSE:', 'the two touchers of ONE corner tend to the flat squares',
                      '[0,1]x[1,2] and [1,2]x[0,1] (delta -> 1, theta -> 90 deg);', 'the corner box stays doubly met by slivers,',
                      'the pair interlocks through a channel of width -> 0,', 'the wall neighbours poke tips into the strips',
                      'the flat squares leave (Lemma GAP).  The disc of', 'radius 1/2 at (3/2, 3/2) of the corner frame is then',
                      'admissible, (s/2 - 3/2) sqrt2 >= 0.58 from O on the window.', '',
                      'What survives (any n): SOME centre within 1/sqrt3,', 'two pieces of diameter < 1, or the POKER-ANCHORED',
                      'residual (docs/proofs/centre_disc.md s.4).'])
    pg.text(24, 26, 'A252 -- CENTRE-DISC about the container centre is false on the window: the corner MOUTH of a near-flat corner', 12, weight='bold')
    pg.save(os.path.join(OUT, 'mouth_witness.svg'))


def page_centre_set():
    s = D.SW
    m = D.metrics(D_XW, s)
    pk = json.load(open(os.path.join(RES, 'poker252_shat.json'), encoding='utf-8')) if os.path.exists(os.path.join(RES, 'poker252_shat.json')) else None
    pg = Page(1040, 430, 'A252 centre set')
    ring_panel(pg, 'a', 24, 44, D_XW, s, '(a) A249\'s ring at s-hat: the centre set C', [(tuple(m['far_pt']), RED)],
               ['far_O %.4f, sec_r %.4f (purple), diam %.4f, halves %.4f, disp3 %.4f: capacity <= 1 here (diam < 1)' %
                (m['far_O'], m['sec_r'], m['diam'], m['halves_diam'], m['disp3'])], sec=(m['sec_r'], tuple(m['sec_c'])))
    if pk:
        F = G.verts(pk['pose'])
        C2 = ring_panel(pg, 'b', 400, 44, D_XW, s, '(b) the POKER in place: residual centre set', [], [], extra_polys=[F])
        pg.note(400, 366, ['poker margin %+.5f on wall %s (its corner in the slot overlap); residual C area %.4f -> EMPTY:' %
                           (pk['poke_margin'], pk['wall'], C2.area), 'no second free square beside the poker: 8 + 1 = 9 < 11 at s-hat'])
    pg.note(776, 60, ['(c) the corrected family-stuck ring structure', '(coordinator / PI, 2026-09-18): the bare ring is',
                      'teleportable -- each eight-cell family {4 corner boxes', '+ one slot per wall} is met by the 8 ring squares',
                      'only -- so the structure is RING + POKER, a free', 'square with a corner in the overlap [0,1]x[s-2,2]',
                      'of one wall\'s two slots and its body in the centre.', 'Capacity question: poker + two more?  With the',
                      'poker pinned the residual centre set decides:', 'diameter < 1 => at most one more => capacity <= 2.',
                      'At s-hat the residual set is empty (panel b).'])
    pg.text(24, 26, 'A252 -- the centre set of the s-hat ring, its enclosing circle, and the poker of the corrected structure', 12, weight='bold')
    pg.save(os.path.join(OUT, 'centre_set.svg'))


def page_notch():
    tB, dB, tA, dA = math.radians(12), 0.95, math.radians(89), 0.9916
    B, A = T.wall_square(tB, dB), T.floor_square(tA, dA)
    q = (0.5, 0.5)
    pg = Page(1040, 430, 'A252 notch disc')
    pg.panel('a', 24, 44, 330, 330, 2.6, win=(0, 2.6, 0, 2.6))
    pg.frame('a', 2.6, '(a) the flat-flat corner: a disc of radius 1/2 in the NOTCH')
    for r in ((0, 1, 0, 1), (0, 1, 1, 2), (1, 2, 0, 1)):
        pg.rect('a', r, '#fff8e6', '#ccc', 0.6)
    poly(pg, 'a', B, '#dfe8fb', BLUE, 'B', op=0.75)
    poly(pg, 'a', A, '#fbe3e3', RED, 'A', op=0.75)
    pg.dot('a', q, GREEN, 3.0)
    circle(pg, 'a', q, 0.5, GREEN)
    dBq, dAq = Polygon(B).distance(Point(q)), Polygon(A).distance(Point(q))
    # the notch region: left of A, below B, in the corner -- and the unit square test
    notch = Polygon([(0, 0), (2.6, 0), (2.6, 2.6), (0, 2.6)]).difference(Polygon(B)).difference(Polygon(A))
    comp = [g for g in D.geoms(notch) if g.contains(Point(q))]
    area = comp[0].area if comp else 0.0
    fits = comp[0].buffer(-0.5).is_empty if comp else True
    bb = comp[0].bounds if comp else (0, 0, 0, 0)
    pg.note(24, 386, ['check: B (%.0f deg, %.2f) meets c00 and reaches (delta + w = %.3f); A (%.0f deg, %.4f); gap(B, A) = %.4f' %
                      (math.degrees(tB), dB, dB + G.w(tB), math.degrees(tA), dA, G.poly_gap(B, A)),
                      'disc at (0.5, 0.5): %.4f from B, %.4f from A, 0.5 from both walls; the notch component has area %.3f,' % (dBq, dAq, area),
                      'bounding box %.3f x %.3f < 1 in width (delta_A < 1): NO unit square fits, though the disc does' % (bb[2] - bb[0], bb[3] - bb[1])])
    pg.note(400, 60, ['(b) why disc-only criteria are lossy', 'INRADIUS replaces a unit square by its inscribed disc;',
                      'in the flat-flat corner limit the corner notch', '(left of A, below B) is a trapezoid of width < 1',
                      'and height ~ 0.9 .. 1.1 that holds the disc but no', 'unit square.  So C acquires a far component',
                      '(|q - O| ~ 2) and far_O, sec_r, the halves and disp3', 'all fail there, while the capacity does not change.',
                      '', 'Consequence: the proof of RING-POKER-RESIDUAL(11)', 'must use square room (Lemma TWO-type bounds on the',
                      'notch and mouth regions), or the box-valid pierce', 'on the protected family -- not a disc radius alone.',
                      '', 'Lemma NOTCH-SEP [T]: a notch disc BEHIND both edge', 'lines L->V, V_A->W needs theta_B > 45 deg,',
                      'delta_B >= phi(theta_B) (min phi = 0.862 at 63.7 deg)', 'and the mirror for A; this panel is the OTHER',
                      'notch case (below B\'s edge V->R, left of A\'s W->T).'])
    pg.text(24, 26, 'A252 -- the corner notch of a flat-flat corner holds a disc of radius 1/2 and no unit square', 12, weight='bold')
    pg.save(os.path.join(OUT, 'notch_disc.svg'))


if __name__ == '__main__':
    D.belownormal()
    os.makedirs(OUT, exist_ok=True)
    page_mouth()
    page_centre_set()
    page_notch()
    print('pages written to', OUT)
