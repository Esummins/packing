"""A253 pages (docs/residue_map/campaigns/A253-min-tilt/):
  min_tilt_ring.svg   the small-tilt ring at s-hat with its poker and pocket, beside the FLUSH
                      LIMIT (tau = 0): the four corner dominoes, the central hole of side s - 2 and
                      the four dead 1 x (s-3) notches;
  ribbon_close.svg    why the ribbon closes: the wall x = 0 and its slot-overlap ribbon
                      [0,1] x [s-2, 2] at tau = 6, 2 and 0 degrees -- the wedge the poker's corner
                      uses shrinks with tau and the limit block [0,1] x [1,3] covers the ribbon;
  capacity_tilt.svg   the measured ladder: the joint ring + poker margin M(tau), the pocket's
                      capacity (FIT / PIERCE) against tau, and the tilt window of the family.
Every panel prints its geometry check in its note.
    python pages253.py
"""
import json
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')
sys.path.insert(0, HERE)
import geom253 as Z                                                   # noqa: E402
import geom237 as G237                                                # noqa: E402
import geom248 as G                                                   # noqa: E402
import limit253 as LIM                                                # noqa: E402
sys.path.insert(0, os.path.join(Z.ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
from draw244 import Page                                             # noqa: E402

OUT = os.path.join(Z.ROOT, 'docs', 'residue_map', 'campaigns', 'A253-min-tilt')
BLUE, RED, GREEN, GREY, ORANGE, PURPLE = '#3b6fd6', '#d63b3b', '#3a9d5d', '#999', '#e08a1e', '#7a3fb0'


def rows(fn):
    p = os.path.join(RES, fn)
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []


def shape(pg, key, geom, fill, stroke, op=0.55):
    for gm in G237.polys_of(geom):
        d = ''
        for ring in [list(gm.exterior.coords)] + [list(r.coords) for r in gm.interiors]:
            d += 'M ' + ' L '.join('%.2f %.2f' % pg._t(key, p) for p in ring) + ' Z '
        pg.parts.append('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="0.8" '
                        'fill-rule="evenodd"/>' % (d, fill, op, stroke))


def geo(polys, s):
    pr = min([G.poly_gap(polys[i], polys[j]) for i in range(len(polys)) for j in range(i)] + [9.0])
    wl = min(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()) for V in polys)
    return pr, wl


def ring_at(s, tau_deg, sg='00110011'):
    """the best common-tilt ring + poker at (s, tau) from the curve rows, else recomputed."""
    R = [r for r in rows('mintilt253_curve.jsonl')
         if r['side'] == '%.6f' % s and abs(r['tau_deg'] - tau_deg) < 1e-6 and r.get('pose')]
    if R:
        r = max(R, key=lambda q: q['M'])
        return Z.x_of(tau_deg * Z.DEG, [int(c) for c in r['sigma']], r['deltas']), r['pose'], \
            r['wall'], r['M']
    import mintilt253 as M
    x = Z.shat_ring()
    d = [x[1], x[3], x[5], x[7], x[9], x[11], x[13], x[15]]
    rr = M.joint_best(tau_deg * Z.DEG, [int(c) for c in sg], s, d0=d, maxiter=900)
    return Z.x_of(tau_deg * Z.DEG, [int(c) for c in sg], rr['deltas']), rr['pose'], rr['wall'], rr['M']


def draw_ring(pg, key, x, y, xr, s, title, pose=None, wall=None, notes=()):
    P = Z.polys(xr, s)
    pg.panel(key, x, y, 320, 320, s)
    pg.frame(key, s, title)
    allp = list(P) + ([G.verts(list(pose))] if pose is not None else [])
    shape(pg, key, G237.pocket([tuple(map(float, G.pose_of(V))) for V in allp], s), '#f4f6ea', '#b8c48a')
    for V, nm in zip(P, Z.NAMES):
        pg.square(key, tuple(map(float, G.pose_of(V))), '#dfe8fb' if nm[0] == 'B' else '#fbe3e3',
                  BLUE if nm[0] == 'B' else RED, label=nm, op=0.72)
    if pose is not None:
        import poker252 as PK
        pg.rect(key, PK.overlap_cell(s, wall), 'none', ORANGE, 1.2, '3,2')
        pg.square(key, tuple(pose), '#e6d9f5', PURPLE, label='poker', op=0.85)
    pr, wl = geo(allp, s)
    pg.note(x, y + 332, ['check: least pair gap %+.2e, least wall gap %+.2e (both >= 0: a packing '
                         'as drawn)' % (pr, wl)] + list(notes))


def page_ring():
    s = Z.SW
    xr, pose, wall, M = ring_at(s, 1.0)
    pg = Page(1060, 470, 'A253 minimum-tilt ring')
    draw_ring(pg, 'a', 24, 44, xr, s, '(a) common tilt 1 deg at s-hat: ring + poker', pose, wall,
              ['joint margin min(ring, poker) = %+.5f; the poker (purple) has its corner in the '
               'slot-overlap ribbon (orange dashed)' % M,
               'tilts (deg): %s' % ', '.join('%.2f' % t for t in
                                             [v / Z.DEG for v in Z.tilts_of(xr)])])
    L = LIM.verify(s)
    R = [[float(v) for v in q] for q in LIM.limit_ring(LIM.Fr(round(s * 10 ** 6), 10 ** 6))]
    poses = [((r[0] + r[1]) / 2, (r[2] + r[3]) / 2, 0.0) for r in R]
    pg.panel('b', 380, 44, 320, 320, s)
    pg.frame('b', s, '(b) the FLUSH LIMIT tau = 0: four corner dominoes')
    shape(pg, 'b', G237.pocket(poses, s), '#f4f6ea', '#b8c48a')
    for r, p in zip(R, poses):
        pg.square('b', p, '#e9eef7', '#5b6b86', op=0.8)
    pg.rect('b', (1.0, s - 1, 1.0, s - 1), 'none', GREEN, 1.6, '5,3')
    import poker252 as PK
    pg.rect('b', PK.overlap_cell(s, 0), 'none', ORANGE, 1.4, '3,2')
    pg.note(380, 376, ['check: least pair gap %+.2e (touching dominoes), contained %s; pocket = '
                       'hole %.4f^2 + four %.4f x 1 notches' % (L['min_gap'], L['contained'],
                                                                L['hole_side'], L['hole_side'] - 1.0),
                       'the ribbon (orange) lies INSIDE the wall block [0,1]x[1,3]: no poker at '
                       'tau = 0; the hole (green) has side s-2 < 2, so it holds ONE square '
                       '(Lemma HOLE-ONE)'])
    pg.note(724, 62, ['[F] there is no POSITIVE minimum tilt: theta_min(s) = 0 on the window.',
                      'For every tau > 0 the pinwheel sign pattern 00110011 carries a ring AND a',
                      'poker; the joint margin degenerates like M ~ c(s) tau (tau -> 0) and the',
                      'limit tau = 0 is the four-corner-domino pinwheel, a boundary point of the',
                      'family (each corner box is met by ONE square there, not two).',
                      '',
                      '[T] At the limit the room is EXACTLY 1: the pocket is the central square',
                      'hole of side s - 2 < 2 (Lemma HOLE-ONE: every unit square in a square of',
                      'side <= 2 contains its centre, with slack (4 - s)/2) plus four isolated',
                      '1 x (s - 3) notches, too narrow for a unit square (Lemma NOTCH-NARROW).',
                      'So 8 + 1 = 9 < 11 AT the extremal tilt, by theorem, with no search.'])
    pg.text(24, 26, 'A253 -- the minimum-tilt ring: theta_min = 0, and the flush limit is the '
                    'four-corner-domino pinwheel (s = %.6f)' % s, 12.5, '#111', weight='600')
    pg.save(os.path.join(OUT, 'min_tilt_ring.svg'))
    return L


def page_ribbon():
    s = Z.SW
    pg = Page(1060, 430, 'A253 ribbon close')
    win = (-0.05, 1.35, 0.6, 3.3)
    wedges = []
    for k, (key, tau, x0) in enumerate((('a', 6.0, 24), ('b', 2.0, 360), ('c', 0.0, 696))):
        pg.panel(key, x0, 48, 300, 300, s, win=win)
        pg.rect(key, (win[0], win[1], win[2], win[3]), '#ffffff', '#ddd', 0.6)
        if tau > 0:
            xr, pose, wall, M = ring_at(s, tau)
            P = Z.polys(xr, s)
            names = list(Z.NAMES)
            for V, nm in zip(P, names):
                if nm in ('B_BL', 'B_TL'):
                    pg.square(key, tuple(map(float, G.pose_of(V))), '#dfe8fb', BLUE, label=nm, op=0.75)
            note = 'tau = %.0f deg, joint margin %+.5f' % (tau, M)
            g = G.poly_gap(Z.polys(xr, s)[0], Z.polys(xr, s)[6])
            wedges.append((tau, xr[1] + math.cos(xr[0]), s - xr[13] - math.cos(xr[12]), g))
        else:
            for r in ((0.0, 1.0, 1.0, 2.0), (0.0, 1.0, 2.0, 3.0)):
                pg.rect(key, r, '#e9eef7', '#5b6b86', 1.3)
            note = 'tau = 0: the wall block [0,1]x[1,3] covers the ribbon'
            gapy = None
        pg.rect(key, (0.0, 1.0, s - 2.0, 2.0), 'none', ORANGE, 1.6, '3,2')
        pg.line(*(list(pg._t(key, (0, win[2]))) + list(pg._t(key, (0, win[3])))), col='#222', width=2.0)
        pg.text(x0, 42, '(%s) wall x = 0, ribbon [0,1] x [%.3f, 2]  --  %s' % (key, s - 2, note), 10.5)
    pg.note(24, 372, ['check: %s; the ribbon rectangle is exactly [0,1] x [s-2, 2] (A252\'s slot '
                      'overlap of the wall x = 0).'
                      % '; '.join('tau %.0f deg: wall vertices at %.4f and %.4f, SAT gap '
                                  'B_BL/B_TL %+.5f' % (t, a, b, g) for t, a, b, g in wedges),
                      'As tau falls the two touchers lean back towards flush and the wedge at the '
                      'wall that the poker\'s corner uses closes; at tau = 0 the block covers the '
                      'ribbon entirely, so the poker dies EXACTLY in the limit.',
                      'This is the PI\'s blocking mechanism -- the blocker is the pair of wall '
                      'touchers of the wall itself, not a corner square -- but the threshold is 0, '
                      'not positive.'])
    pg.text(24, 26, 'A253 -- the ribbon closes only in the limit: the wall block against the '
                    'slot-overlap ribbon', 12.5, '#111', weight='600')
    pg.save(os.path.join(OUT, 'ribbon_close.svg'))


def page_capacity():
    pg = Page(1060, 430, 'A253 capacity vs tilt')
    cur = [r for r in rows('mintilt253_curve.jsonl') if r['M'] is not None]
    rm = [r for r in rows('room253.jsonl') if not r.get('infeasible')]
    x0, y0, w, h = 60, 60, 400, 260
    pg.line(x0, y0 + h, x0 + w, y0 + h, '#222', 1.4)
    pg.line(x0, y0, x0, y0 + h, '#222', 1.4)
    sides = sorted({r['side'] for r in cur})
    cols = {sides[i]: [BLUE, RED, GREEN, ORANGE, PURPLE, '#111'][i % 6] for i in range(len(sides))}
    tmax = max([r['tau_deg'] for r in cur] + [15.0])
    mmax = max([r['M'] for r in cur] + [0.01])
    for sd in sides:
        pts = sorted([(r['tau_deg'], r['M']) for r in cur if r['side'] == sd])
        pg.polyline([(x0 + w * t / tmax, y0 + h - h * m / mmax) for t, m in pts], cols[sd], 1.6)
        for t, m in pts:
            px, py = x0 + w * t / tmax, y0 + h - h * m / mmax
            pg.parts.append('<circle cx="%.2f" cy="%.2f" r="2.0" fill="%s"/>' % (px, py, cols[sd]))
    for i, sd in enumerate(sides):
        pg.text(x0 + w - 90, y0 + 14 + 13 * i, 's = %s' % sd, 9.5, cols[sd])
    pg.text(x0, y0 - 10, 'joint ring + poker margin M(tau), common tilt (sigma = 00110011)', 10.5)
    pg.text(x0 + w / 2 - 20, y0 + h + 22, 'tau (deg), 0 .. %.1f' % tmax, 9.5)
    pg.text(x0 - 48, y0 + 6, '%.4f' % mmax, 9.0)
    pg.text(x0 - 20, y0 + h + 2, '0', 9.0)
    lines = ['capacity of the pocket against the tilt (FIT k = lower bound, PIERCE k = certificate):', '']
    for r in sorted(rm, key=lambda q: (q['side_key'], -q['tau_deg'])):
        lines.append('s = %s  tau %6.3f deg   FIT >= %d   PIERCE <= %d   pocket area %.4f   '
                     'beside the poker: 1 more %s'
                     % (r['side_key'], r['tau_deg'], r['capacity_lo'], r['capacity_hi'],
                        r['pocket_area'], r.get('beside_poker', {}).get('one', {}).get('fits')))
    lines += ['', 'the flush limit tau = 0: capacity EXACTLY 1 by Lemma HOLE-ONE + NOTCH-NARROW.',
              'check: every row above is a ring certified by its own least pair / wall gap >= 0;',
              'the PIERCE column is A237\'s box-valid piercing residual 0 over 1-degree tilt bins.']
    pg.note(500, 70, lines[:26])
    pg.text(24, 26, 'A253 -- the room does not grow with the tilt: capacity 1 from the flush limit '
                    'to the top of the tilt window', 12.5, '#111', weight='600')
    pg.save(os.path.join(OUT, 'capacity_tilt.svg'))


def main():
    os.makedirs(OUT, exist_ok=True)
    Z.belownormal()
    page_ring()
    page_ribbon()
    page_capacity()
    print('wrote pages to', OUT, flush=True)


if __name__ == '__main__':
    main()
