"""A237 pages (docs/residue_map/campaigns/A237-pocket-waste/), each configuration panel geometry-checked (pairwise
SAT gaps + wall margins >= -1e-6, printed in the panel note):
  ring_pocket.svg   (a) the ring rand_0_0569|t20: the loaded component U (red outline), its pocket, the uncoverable
                    set shaded (hatch), the two rattlers; (b) A226's crowd ring at S = 3.90, eps = 0.02 with the
                    uncoverable stubs and the piercing point that certifies capacity 1; (c) Trump with U = its wall
                    touchers (not a ring: the lemma must not fire).
  n11_window.svg    the window family at S = s-hat: (a) theta = 20 deg (four-crowd, PIERCE(1) certifies capacity 1);
                    (b) theta = 2 deg (near-flush crowd: the same); (c) one corner crowd at 20 deg in a big box with
                    its sealed region (the n-general w_c(theta) of the table).
    python pages237.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import draw222 as D            # noqa: E402
import geom237 as G            # noqa: E402
import family237 as FM         # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A237-pocket-waste')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'pocket237.jsonl')


def rows():
    return [json.loads(l) for l in open(RES, encoding='utf-8')]


def wrap(lines, width=118):
    out = []
    for t in lines:
        while len(t) > width:
            cut = t.rfind(' ', 0, width)
            cut = width if cut < 40 else cut
            out.append(t[:cut])
            t = '   ' + t[cut:].lstrip()
        out.append(t)
    return out


def shade(pg, k, geom, fill='url(#hatch)', stroke='#555'):
    for poly in G.polys_of(geom):
        pg.poly(k, list(poly.exterior.coords)[:-1], fill, stroke, width=0.8)


def dot(pg, k, x, y, col='#d62728', r=4.0):
    px, py = pg.P(k, x, y)
    pg.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (px, py, r, col))


def panel(pg, k, members, s, rest=(), pts=(), labels=True, step=1.0):
    W = G.waste(members, s, step)
    pg.frame(k, s)
    shade(pg, k, W['uncov'])
    for i, m in enumerate(members):
        pg.square(k, m, D.GREY[0], D.RED, label=i if labels else None, width=2.0)
    for j, p in enumerate(rest):
        pg.square(k, p, D.BLUE[0], D.BLUE[1], label='r%d' % j if labels else None, width=1.2)
    for p in pts:
        dot(pg, k, p[0], p[1])
    ok, gap, wall = pg.check_partial(list(members) + list(rest), s)
    note = 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)
    return W, note


def page_ring(rs):
    ring = [r for r in rs if r.get('rid') == 'rand_0_0569|t20'][0]
    r8 = [r for r in rs if r['label'] == 'ring8_S3.90_eps0.02'][0]
    tr = [r for r in rs if r['label'] == 'square-11'][0]
    side = max(ring['s'], r8['s'], tr['s'])
    pg = D.Page('A237 -- pockets and their uncoverable sets (hatched): (a) the ring rand_0_0569|t20 (U red, rattlers blue); '
                "(b) A226's crowd ring at S = 3.90 with its piercing point (red dot); (c) Trump with U = wall touchers",
                3, 1, side, panel_w=700, note_h=200)
    W, note = panel(pg, 0, [tuple(m) for m in ring['members']], ring['s'], [tuple(p) for p in ring['rest']])
    pg.text(0, wrap([note, '(a) side %.4f, p = %d, rattlers %d; pocket area %.3f, coverable <= %.3f, waste >= %.3f; the hatched set is '
                     'uncoverable by ANY unit square inside the pocket (sandwich over 1-deg bins); the rattlers lie in the white part.' % (
                         ring['s'], ring['p'], ring['k'], W['area'], W['coverable_area'], W['waste']),
                     'PIERCE(2) with the rattler centres fails by %.3f: two squares fit and can slide; the ring is at 4.11 > 4 where nothing must fire.' % ring['pierce_k']]))
    W, note = panel(pg, 1, [tuple(m) for m in r8['members']], r8['s'], pts=[tuple(r8['pierce1_pt'])])
    pg.text(1, wrap([note, '(b) S = 3.90, eps = 0.02: area %.3f, coverable <= %.3f, waste >= %.3f (the four stubs of width 0.87 < 1 and the corner '
                     'slivers); PIERCE(1): every unit square inside the pocket contains the red point (%.3f, %.3f) in its interior '
                     '(residual %.1e over 90 bins) => capacity 1 => 8 + 1 = 9 < 11: this ring family is dead at S = 3.90 by certificate.' % (
                         W['area'], W['coverable_area'], W['waste'], r8['pierce1_pt'][0], r8['pierce1_pt'][1], r8['pierce1'])]))
    W, note = panel(pg, 2, [tuple(m) for m in tr['members']], tr['s'], [tuple(p) for p in tr['rest']])
    pg.text(2, wrap([note, '(c) Trump, U = the %d wall touchers, %d interior squares: pocket area %.3f, coverable <= %.3f >= 3 (sound: the '
                     'three interior squares sit in the white part); waste >= %.3f is the sealed corners of its 45-deg and 40-deg grain.' % (
                         tr['p'], tr['k'], W['area'], W['coverable_area'], W['waste'])]))
    return pg.write(os.path.join(PAGES, 'ring_pocket.svg'))


def page_window():
    S = 3.877
    pg = D.Page('A237 -- the n = 11 window pocket: the family ring(S, theta) at S = s-hat = 3.877; (a) theta = 20, (b) theta = 2; '
                '(c) one corner crowd at 20 deg in a side-6 box: the sealed region w_c(theta)', 3, 1, 6.0, panel_w=700, note_h=200)
    for k, th in enumerate((20, 2)):
        R, delta = FM.ring(S, th)
        W, note = panel(pg, k, R, S, pts=[(S / 2, S / 2)])
        p1 = G.pierce(R, S, [(S / 2, S / 2)], 1.0, free=W['free'])
        crowd = all(len(__import__('band236').meeters(R, S, c)) >= 2 for c in ('BL', 'BR', 'TR', 'TL'))
        pg.text(k, wrap([note, '(%s) theta = %d deg, flat meeters at offset delta = sin theta + 0.02 = %.3f (the least that admits the partner: '
                         'TILT-MIN), four-crowd: %s; pocket area %.3f, coverable <= %.3f, waste >= %.3f.' % ('ab'[k], th, delta, crowd, W['area'], W['coverable_area'], W['waste']),
                         'PIERCE(1) at the centre: residual %.1e => capacity 1 => 8 + 1 = 9 < 11 on this family; at theta = 2 the crowd is '
                         'O(eps) and the waste is O(eps): the closure is the CENTRE (side %.3f < 2, Lemma TWO), not the jaggedness.' % (p1, S - 2 - delta)]))
    A, B, delta = FM.crowd_pair(20)
    W, note = panel(pg, 2, [A, B], 6.0)
    comps = [c for c in G.components(W['uncov']) if c['cx'] < 3 and c['cy'] < 3]
    pg.text(2, wrap([note, '(c) one crowd at 20 deg: the sealed strip under the tilted meeter against the wall and the wedge above the '
                     'flat one, total uncoverable area w_c(20) = %.3f (the table\'s per-corner term); 4 w_c(20) = %.3f < s-hat^2 - 11 = 4.03: '
                     'the area bound needs theta >= 32 deg at n = 11 and no tilt floor exists (A89).' % (sum(c['area'] for c in comps), 4 * sum(c['area'] for c in comps))]))
    return pg.write(os.path.join(PAGES, 'n11_window.svg'))


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(HERE, '..', '..', 'A236-ring-capacity', 'code'))
    rs = rows()
    print(page_ring(rs))
    print(page_window())
