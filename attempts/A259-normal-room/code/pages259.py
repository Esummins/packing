"""A259 pages -> docs/residue_map/campaigns/A259-normal-room/{normal_pocket,corner_gap,worst_case}.svg
Every drawn ring passes ring_margin >= 0 (in-D panels: with the corner-box terms) and every drawn free square passes
the exact free_margin >= 0 (hard containment + SAT) BEFORE it is drawn; a failed check aborts the page.
Colours: ring squares blue-grey; pocket white; exact admissible-centre set (union over a 1-degree tilt grid) amber;
region R outlines dashed; free squares red outline; the piercing point O black; UNDECIDED = grey stipple, never green."""
import json
import math
import os
import sys

import numpy as np
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom259 as Z                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
import pair259 as P                                                   # noqa: E402
import gapscan259 as GS                                               # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'docs', 'residue_map', 'campaigns', 'A259-normal-room'))
SC = 120.0


class Panel:
    def __init__(self, s, x0, y0, view=None):
        self.s, self.x0, self.y0, self.el = s, x0, y0, []
        self.view = view or (0, 0, s, s)
        self.k = SC * s / (self.view[2] - self.view[0])

    def pt(self, p):
        return (self.x0 + (p[0] - self.view[0]) * self.k, self.y0 + (self.view[3] - p[1]) * self.k)

    def poly(self, V, fill='none', stroke='#333', sw=1.0, dash=None, op=1.0):
        pts = ' '.join('%.2f,%.2f' % self.pt(p) for p in V)
        d = '' if not dash else ' stroke-dasharray="%s"' % dash
        self.el.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.2f"%s/>' % (pts, fill, op, stroke, sw, d))

    def geom(self, g, fill, op=0.6):
        for Pg in R.polys_of(g):
            self.poly(list(Pg.exterior.coords)[:-1], fill=fill, stroke='none', op=op)

    def dot(self, p, r=3.0, fill='#000'):
        x, y = self.pt(p)
        self.el.append('<circle cx="%.2f" cy="%.2f" r="%.1f" fill="%s"/>' % (x, y, r, fill))

    def text(self, p, t, size=11, fill='#222'):
        x, y = self.pt(p)
        self.el.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" font-family="sans-serif">%s</text>' % (x, y, size, fill, t))

    def frame(self):
        v = self.view
        self.el.insert(0, '<clipPath id="c%d"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f"/></clipPath>' % (
            id(self) % 100000, self.x0, self.y0, (v[2] - v[0]) * self.k, (v[3] - v[1]) * self.k))
        self.poly([(v[0], v[1]), (v[2], v[1]), (v[2], v[3]), (v[0], v[3])], stroke='#000', sw=1.5)

    def svg(self):
        return '<g>%s</g>' % ''.join(self.el)


def write(name, panels, notes, W, H):
    os.makedirs(OUT, exist_ok=True)
    body = ''.join(p.svg() for p in panels)
    txt = ''.join('<text x="%d" y="%d" font-size="12" font-family="sans-serif" fill="#111">%s</text>' % (x, y, t) for x, y, t in notes)
    pat = ('<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#e8e8e8"/>'
           '<circle cx="2" cy="2" r="1" fill="#888"/></pattern></defs>')
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="100%%" height="100%%" fill="#fff"/>%s%s%s</svg>'
        % (W, H, W, H, pat, body, txt))


def ring_panel(x, s, x0, y0, boxes=True, view=None, frees=(), centres=True, rot_psi=None):
    assert Z.ring_margin(x, s, boxes) >= -1e-12, 'ring fails its domain check'
    Vs = Z.ring_verts(x, s)
    pn = Panel(s, x0, y0, view)
    if centres:
        U = unary_union([R.centre_set(Vs, s, t * Z.DEG) for t in range(0, 90, 1)])
        pn.geom(U, '#f0a830', 0.55)
    for V in Vs:
        pn.poly(V, fill='#9fb4c8', stroke='#34495e', op=0.9)
    for pose in frees:
        assert R.free_margin(pose, Vs, s) >= -1e-9, 'free square fails the exact check %r' % (pose,)
        pn.poly(Z.sq_verts(*pose), stroke='#c0392b', sw=1.6)
    if rot_psi is not None:
        pn.poly(Z.sq_verts(s / 2, s / 2, rot_psi, (s - 2) / 2), stroke='#1a7', sw=1.2, dash='5,3')
    pn.dot((s / 2, s / 2))
    pn.frame()
    return pn, Vs


def main():
    s = Z.SHAT
    phi = 14.545 * Z.DEG
    lo, hi = Z.delta_range_c4(phi, s)
    x = Z.c4(0.5 * (lo + hi), phi)
    w, pose, _ = R.pierce_O(x, s, 1.0)
    p1, Vs = ring_panel(x, s, 20, 40, frees=[pose[:3]], rot_psi=pose[2])
    c = math.cos(phi)
    p1.poly([(c, c), (s - c, c), (s - c, s - c), (c, s - c)], stroke='#2255cc', sw=1.2, dash='2,3')
    n1 = [(20, 20, 'PANEL 1 IS: the C4 normal ring (four common-tilt pairs, 14.545 deg, delta = %.4f) at s-hat, in D.' % x[0]),
          (20, 40 + SC * s + 18, 'Amber = the EXACT set of admissible centres of a free unit square (union over a 1-degree tilt grid).  Black dot = O.'),
          (20, 40 + SC * s + 34, 'Red = the free square FARTHEST from containing O (exact check passed): it still contains O, margin %+.4f.' % w),
          (20, 40 + SC * s + 50, 'Blue dots = R_cos = [cos phi, s - cos phi]^2 (TOOTH: no vertex dips below cos phi).  Green dashes = the ROTATED HOLE:'),
          (20, 40 + SC * s + 66, 'side s - 2 at the free square\'s own tilt; [M] every free square of that tilt lies inside it (margin >= (4-s)/2).')]
    write('normal_pocket.svg', [p1], n1, int(40 + SC * s), int(40 + SC * s + 80))

    # corner gap: a pair near the double limit, zoomed on BR
    e0, f0, d1, f1 = 0.97, 12 * Z.DEG, 0.96, 18 * Z.DEG
    assert P.pair_feas(e0, f0, d1, f1, s) >= -1e-12
    PV = P.pair_verts(e0, f0, d1, f1, s)
    g1, q1, g2, q2 = GS.gap_dips(e0, f0, d1, f1, s, 1.0, PV)
    view = (s - 2.4, 0.0, s, 2.4)
    p2 = Panel(s, 20, 40, view)
    U = unary_union([R.centre_set(PV, s, t * Z.DEG) for t in range(0, 90, 1)]).intersection(
        __import__('shapely.geometry', fromlist=['box']).box(*view))
    p2.geom(U, '#f0a830', 0.55)
    for V in PV:
        p2.poly(V, fill='#9fb4c8', stroke='#34495e', op=0.9)
    for q in (q1, q2):
        if q is None:
            continue
        assert R.free_margin(q, PV, s) >= -1e-9
        p2.poly(Z.sq_verts(*q), stroke='#c0392b', sw=1.6)
    p2.poly([(s - 1, 0), (s, 0), (s, 1), (s - 1, 1)], stroke='#555', sw=1.0, dash='4,3')
    lay = 1.0 / 64
    p2.poly([(s - 1, 0), (s - 1 + 8 * lay, 0), (s - 1 + 8 * lay, 8 * lay), (s - 1, 8 * lay)], fill='url(#stip)', stroke='#777')
    p2.frame()
    n2 = [(20, 20, 'PANEL IS: the BR corner of a PAIR (floor row end gap e0 = %.2f, %.0f deg; right row offset delta1 = %.2f, %.0f deg), only these 4 squares.' % (e0, f0 / Z.DEG, d1, f1 / Z.DEG)),
          (20, 40 + SC * s + 18, 'Dashed box = the corner box (both rows meet it: e0 &lt; 1, delta1 &lt; 1).  Amber = exact admissible centres: NONE in the corner gap.'),
          (20, 40 + SC * s + 34, 'Red = the free squares with the lowest vertex right of the row end (height %s) and the right-most vertex below the first tip (depth %s): both &gt;= 1 [M]; 9 = none exists.' % (round(g1, 3), round(g2, 3))),
          (20, 40 + SC * s + 50, 'Grey stipple (symbolic, 8x enlarged) = the OPEN layer e0, delta1 &gt; 63/64: at e0 = delta1 = 1 a unit square fits the gap, so no box certificate; obligation CORNER-NOTCH.')]
    write('corner_gap.svg', [p2], n2, int(60 + SC * s + 260), int(40 + SC * s + 64))

    # worst case in D (adversary, s-hat) and the off-D witness of capacity 2
    adv = [json.loads(l) for l in open(os.path.join(HERE, '..', 'results', 'adv259.jsonl'))]
    inD = max((r for r in adv if r['boxes'] == 1 and abs(r['s'] - s) < 1e-9), key=lambda r: r['pierceO'])
    pa, _ = ring_panel(np.array(inD['x']), s, 20, 40, frees=[tuple(inD['pose'])], rot_psi=inD['pose'][2])
    cap = json.load(open(os.path.join(HERE, '..', 'results', 'capacity259.json')))
    off = max(cap, key=lambda r: (r['capacity_lb'], r['pierceO']))
    pb, _ = ring_panel(np.array(off['x']), off['s'], 60 + SC * s, 40, boxes=False, frees=[tuple(p) for p in off['witness']])
    n3 = [(20, 20, 'LEFT IS: the worst ring found IN D at s-hat (adversary, 6 restarts): margin %+.4f; the sup over D is -(4-s)/2 = %.4f (flush limit).' % (inD['pierceO'], -(4 - s) / 2)),
          (int(60 + SC * s), 20, 'RIGHT IS: a ring OUTSIDE D (s = %.2f; a row end misses its corner box: b &gt;= 1): %d disjoint free squares, one missing O.' % (off['s'], off['capacity_lb'])),
          (20, 40 + int(SC * 4) + 18, 'So the corner-box conditions (D2) of family258 are what the room bound uses; without them NORMAL-ROOM(1) is [F].  All red squares passed the exact check.')]
    write('worst_case.svg', [pa, pb], n3, int(100 + SC * (s + 4)), int(40 + SC * 4 + 40))
    print('pages ok', OUT)


main()
