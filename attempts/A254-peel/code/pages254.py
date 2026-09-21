"""A254 pages: the tight flush pinwheel (four 1 x (m-2) wall blocks), its hole [1, s-1]^2 and the inner record packing.
    peel_n17.svg  n = 17 at side 2 + s(5)  (proved value)         peel_n84.svg  n = 84: EQUALITY with the record
    peel_n65.svg  n = 65 at 2 + rec(37), and at the record side 8.5355 where the hole is UNDECIDED (grey stipple)
Every panel is geometry-checked (containment, pairwise SAT gap >= -1e-9) and the check is printed in its note.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A226-one-flush', 'code'))
sys.path.insert(0, HERE)
from svg226 import load_svg, square_corners      # noqa: E402
import cells254 as C                             # noqa: E402

PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A254-peel')
DATA = os.path.join(ROOT, 'attempts', 'A226-one-flush', 'data', 'ellsworth')


def pinwheel(m, s):
    """the 4(m-2) flush ring squares: left wall block [0,1] x [1, m-1] and its C4 images."""
    return [C.rot([(0, j), (1, j), (1, j + 1), (0, j + 1)], s, k) for k in range(4) for j in range(1, m - 1)]


def notches(m, s):
    return [C.rot([(0, m - 1), (1, m - 1), (1, s), (0, s)], s, k) for k in range(4)]


def inner(n):
    if n == 5:                                   # Goebel: four corner squares + one at 45 degrees, side 2 + 1/sqrt2
        t = 2 + 1 / math.sqrt(2)
        sq = [(.5, .5, 0), (t - .5, .5, 0), (.5, t - .5, 0), (t - .5, t - .5, 0), (t / 2, t / 2, math.pi / 4)]
        return [square_corners(*q) for q in sq], t
    sq, t, _ = load_svg(os.path.join(DATA, 'square-%d.svg' % n))
    return [square_corners(*q) for q in sq], t


def check(quads, s):
    out = min(min(P.min(), s - P.max()) for P in quads)
    gap = min(C.sat_gap(quads[i], quads[j]) for i in range(len(quads)) for j in range(i + 1, len(quads)))
    return out, gap


def poly(P, sc, s, style):
    pts = ' '.join('%.3f,%.3f' % (x * sc, (s - y) * sc) for x, y in P)
    return '<polygon points="%s" %s/>' % (pts, style)


def panel(x0, y0, px, m, s, inn, undecided, title, note):
    sc = px / s
    ring = pinwheel(m, s)
    g = ['<g transform="translate(%d,%d)">' % (x0, y0),
         '<text x="0" y="-10" font-size="15" font-weight="bold">%s</text>' % title,
         '<rect x="0" y="0" width="%.2f" height="%.2f" fill="#fff" stroke="#222" stroke-width="2"/>' % (px, px)]
    for P in notches(m, s):
        g.append(poly(P, sc, s, 'fill="url(#hatch)" stroke="#999" stroke-width="0.6"'))
    for P in ring:
        g.append(poly(P, sc, s, 'fill="#c9d6ea" stroke="#33507a" stroke-width="1"'))
    hole = np.array([(1, 1), (s - 1, 1), (s - 1, s - 1), (1, s - 1)])
    quads = list(ring)
    if undecided:
        g.append(poly(hole, sc, s, 'fill="url(#stipple)" stroke="#555" stroke-width="1.2" stroke-dasharray="5,3"'))
    else:
        g.append(poly(hole, sc, s, 'fill="none" stroke="#a33" stroke-width="1.4" stroke-dasharray="6,3"'))
        for P in inn:
            Q = P + 1.0
            quads.append(Q)
            g.append(poly(Q, sc, s, 'fill="#f6dfb8" stroke="#8a5a12" stroke-width="0.9"'))
    out, gap = check(quads, s)
    assert out > -1e-9 and gap > -1e-9, (title, out, gap)
    lines = note + ['GEOMETRY CHECK: %d squares, containment %.1e, least pairwise SAT gap %.1e (>= -1e-9): %s.'
                    % (len(quads), out, gap, 'a packing' if not undecided else 'the ring alone is a packing')]
    for i, t in enumerate(lines):
        g.append('<text x="0" y="%.1f" font-size="12">%s</text>' % (px + 20 + 16 * i, t))
    g.append('</g>')
    return '\n'.join(g), len(quads), gap


DEFS = ('<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<rect width="6" height="6" fill="#f2f2f2"/><line x1="0" y1="0" x2="0" y2="6" stroke="#aaa" stroke-width="1"/>'
        '</pattern><pattern id="stipple" width="7" height="7" patternUnits="userSpaceOnUse">'
        '<rect width="7" height="7" fill="#ececec"/><circle cx="2" cy="2" r="1" fill="#777"/>'
        '<circle cx="5.5" cy="5.5" r="1" fill="#777"/></pattern></defs>')
LEGEND = ['blue = the 4(m-2) flush ring squares (tight pinwheel: four 1 x (m-2) wall blocks, wall gaps 0); '
          'hatched = the four corner notches, width s-(m-1) &lt; 1: hold NO unit square [T, NOTCH-NARROW];',
          'red dashes = the hole [1, s-1]^2 of side s-2; orange = the inner packing; '
          'grey stipple = UNDECIDED (never green): whether n\' squares fit is an open value of s(n\').']


def page(name, W, H, panels, head):
    body = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'font-family="DejaVu Sans, Arial, sans-serif">' % (W, H, W, H), DEFS,
            '<rect width="%d" height="%d" fill="#fbfbf8"/>' % (W, H),
            '<text x="20" y="26" font-size="17" font-weight="bold">%s</text>' % head]
    for i, t in enumerate(LEGEND):
        body.append('<text x="20" y="%d" font-size="12">%s</text>' % (46 + 16 * i, t))
    info = []
    for p in panels:
        g, k, gap = panel(*p)
        body.append(g)
        info.append((p[7], k, gap))
    body.append('</svg>')
    os.makedirs(PAGES, exist_ok=True)
    open(os.path.join(PAGES, name), 'w', encoding='utf-8').write('\n'.join(body) + '\n')
    for t in info:
        print(name, *t)


def main():
    i5, t5 = inner(5)
    s17 = 2 + t5
    page('peel_n17.svg', 760, 800, [(40, 110, 560, 5, s17, i5, False,
         'n = 17, m = 5: tight pinwheel (12) + Goebel s(5) (5) at side 2 + s(5) = %.6f' % s17,
         ['IS: a genuine packing of 17 unit squares at side 4.707107 -- the least side of ANY tight-pinwheel',
          'structure, because s(5) = 2 + 1/sqrt2 is PROVED (Goebel).  The record s(17) = 4.675530 (Bidwell) is',
          'SMALLER: [T] no packing at the record side is a tight pinwheel + core.  NOT: a record; NOT family-stuck',
          '(flush ring: each corner box is met by ONE square; Lemma CELLS teleports a corner square in).'])],
         'A254 PEEL -- n = 17: s &gt;= 2 + s(n - 4(m-2)) at the tight flush pinwheel [T]')
    i37, t37 = inner(37)
    s65, r65 = 2 + t37, 5 + 2.5 * math.sqrt(2)
    page('peel_n65.svg', 1380, 830, [
        (40, 110, 600, 9, s65, i37, False,
         'n = 65, m = 9: pinwheel (28) + Cantrell s(37) record at side %.6f' % s65,
         ['IS: a genuine packing of 65 squares at side 2 + rec(37) = 8.598620.  NOT a record: s(65) &lt;= 8.535534',
          '(Goebel 1979, 5 + 5/sqrt2).  The brief\'s "equality at n = 65" is WRONG; 2 + rec(37) exceeds the record',
          'by 0.0631.  The inner packing is a RECORD, not a proved optimum.']),
        (720, 110, 600, 9, r65, None, True,
         'n = 65 at the RECORD side %.6f: the hole has side %.6f' % (r65, r65 - 2),
         ['IS: the tight pinwheel ring alone at the record side; the hole [1, s-1]^2 has side 6.535534.',
          'UNDECIDED (grey stipple): do 37 unit squares fit in side 6.535534?  Record s(37) = 6.598620 says no,',
          'but the PROVED bound is only s(37) &gt;= 6.099020 (Nagamochi Thm 2(ii)).  PEEL excludes the tight pinwheel',
          'at the record side only IF rec(37) is optimal: verdict RECORDS-ONLY.'])],
        'A254 PEEL -- n = 65: no equality; excluded at the record side only given rec(37)')
    i52, t52 = inner(52)
    s84 = 2 + t52
    page('peel_n84.svg', 760, 800, [(40, 110, 600, 10, s84, i52, False,
         'n = 84, m = 10: pinwheel (32) + Goebel s(52) at side 2 + rec(52) = %.6f = rec(84)' % s84,
         ['IS: a genuine packing of 84 squares at side 9.707107 = 9 + 1/sqrt2, EQUAL to the record s(84)',
          '(Stenlund 1980).  The only EQUALITY row of the table (n &lt;= 100): the tight pinwheel + core exists AT the',
          'record side, so PEEL can never exclude it there.  It is flush-ringed, hence NOT family-stuck (CELLS).'])],
         'A254 PEEL -- n = 84: the equality case 2 + rec(52) = rec(84)')


if __name__ == '__main__':
    main()
