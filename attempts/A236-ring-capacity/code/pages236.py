"""A236 pages (docs/residue_map/campaigns/A236-ring-capacity/), every configuration panel geometry-checked (pairwise
SAT gaps + wall margins >= -1e-6, printed in the panel's note):
  ring_band.svg     (a) the ring rand_0_0569|t20 with the unit band, the centre (1, s-1)^2, its squares coloured by
                    class (band grey / core blue / straddler orange), the loaded component U outlined; (b) Trump, the
                    same overlay: NOT a ring, the grain crosses the centre; (c) A226's 8-square crowd ring at S = 3.99
                    with the ONE square its pocket holds.
  n11_capacity.svg  (a) Lemma TILT-BAND's point for a 10-degree square in the corner; (b) the count at n = 11: the 8
                    band slots a four-crowd can have (each corner claimed by one wall) + the 1 core slot; (c) the record
                    n = 26 with the overlay: records are cross-braced (X straddlers through the centre), not rings.
    python pages236.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import draw222 as D            # noqa: E402
import band236 as BD           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A236-ring-capacity')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'capacity236.jsonl')
FILL = {'band': D.GREY, 'core': D.BLUE, 'straddle': D.ORANGE}


def rows():
    return [json.loads(l) for l in open(RES, encoding='utf-8')]


def draw_overlay(pg, k, poses, s, classes, U=(), labels=True):
    pg.frame(k, s)
    for i, p in enumerate(poses):
        f, st = FILL[classes[i]]
        pg.square(k, p, f, st, label=i if labels else None, width=1.2)
    for i in U:
        pg.square(k, poses[i], 'none', D.RED, width=2.4)
    pg.cell(k, (1, s - 1, 1, s - 1), stroke='#555', dash='6,4', width=1.4, label='(1, s-1)^2')
    ok, gap, wall = pg.check_partial(poses, s)
    return 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)


def wrap(lines, width=118):
    """wrap the note lines so that they fit the panel (10.5 px font, panel_w = 700)."""
    out = []
    for t in lines:
        while len(t) > width:
            cut = t.rfind(' ', 0, width)
            cut = width if cut < 40 else cut
            out.append(t[:cut])
            t = '   ' + t[cut:].lstrip()
        out.append(t)
    return out


def dot(pg, k, x, y, col='#d62728', r=4.0):
    px, py = pg.P(k, x, y)
    pg.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (px, py, r, col))


def page_ring(rs):
    ring = [r for r in rs if r['src'] == '193' and r['rid'] == 'rand_0_0569|t20'][0]
    trump = [r for r in rs if r['label'] == 'square-11'][0]
    r8 = [r for r in rs if r['label'] == 'ring8_S3.99_eps0.02'][0]
    side = max(ring['s'], trump['s'], r8['s'])
    pg = D.Page('A236 -- the unit band and the centre: the ring (a), Trump (b), the 8-square crowd ring of A226 at S = 3.99 (c); '
                'grey = band square (flush, touching a wall), blue = core, orange = straddler', 3, 1, side, panel_w=700, note_h=215)
    for k, r in enumerate((ring, trump)):
        poses = [tuple(p) for p in r['poses']]
        note = draw_overlay(pg, k, poses, r['s'], r['classes'], r.get('U', []))
        lines = [note, '(%s) %s, side %.4f, m = 4: B = %d, K = %d, X = %d (n = %d); doubly-met corners %d; tilted %d' % (
            'ab'[k], r['label'], r['s'], r['B'], r['K'], r['X'], r['n'], r['doubly_met'], r['n_tilted'])]
        if k == 0:
            lines += ['loaded component U (red) = %s: p = %d, the rest %s = %s; N_record(s-2 = %.2f) = %d >= n - p = %d: consistent (s > 4)' % (
                r['U'], r['p'], r['rest'], [r['rest_classes'][str(i)] for i in r['rest']], r['sigma'], r['N_record'], r['n_minus_p']),
                'meeters %s: intrusion iota(20 deg) = %.3f each; depth into the centre %.2f .. %.2f; every tilted square intrudes (TILT-BAND)' % (
                    sorted(i for c in r['corners'].values() for i in c), 0.2817, r['meeter_depth_min'], r['meeter_depth_max']),
                'U lies within depth %.2f of the band: a ring in a band of width 1.3; its pocket holds the 2 rattlers 0, 1 at side 4.11.' % r['U_max_depth']]
        else:
            lines += ['NOT a ring: one doubly-met corner (TR) and X = 5 straddlers = the five 40.18-degree strip squares crossing the centre;',
                      'B = 6 = the six flush squares, all wall touchers (BAND-FLUSH), K = 0: the record beats the grid by cross-bracing,',
                      'not by a ring.  Count bound at m = 4: B <= 8 is not attained (6); the 4-crowd BAND-COUNT does not apply (not a 4-crowd).']
        pg.text(k, wrap(lines))
    # (c) the 8-ring with its one square
    S = r8['s']
    ring8 = [tuple(p) for p in r8['poses']]
    thetas = [math.radians(t) for t in range(0, 90, 5)]
    import region222 as RG
    got = RG.greedy(ring8, S, 1, thetas, beam=3)
    extra = [tuple(float(v) for v in q) for q in got] if got else []
    poses = ring8 + extra
    classes = r8['classes'] + [BD.centre_class(q, S) for q in extra]
    note = draw_overlay(pg, 2, poses, S, classes, list(range(8)))
    pg.text(2, wrap([note, '(c) A226 ring11: 8 crowd-ring members (red) at S = %.2f, eps = %.2f: B = 4 (the lifted flush corner squares), X = 4 (the' % (S, r8['eps']),
                'eps/2-tilted neighbours, depth %.3f into the centre: no floor), K = 0; the pocket holds ONE square (%s; A226 greedy+restarts: 1),' % (
                    r8['depths'][1], 'drawn' if extra else 'none placed'),
                'not 2 (greedy) and not 3: 8 + 1 = 9 < 11.  Largest flush square in the pocket: side %.3f < 2, N_proved = 1.' % r8['pocket_inscribed_side'],
                'The count says B + K + X <= 8 + 1 + X with X >= 4: 13 >= 11 -- no closure; the pocket (a region) is what closes this family.']))
    return pg.write(os.path.join(PAGES, 'ring_band.svg'))


def page_n11(rs):
    s = 3.99
    rec26 = [r for r in rs if r['label'] == 'square-26b'][0]
    side = max(s, rec26['s'])
    pg = D.Page('A236 -- n = 11: Lemma TILT-BAND (a), the count 8 + 1 + 4 = 13 >= 11 (b); records are cross-braced, not rings: n = 26 (c)',
                3, 1, side, panel_w=700, note_h=215)
    # (a) TILT-BAND
    th = math.radians(10)
    c, d = math.cos(th), math.sin(th)
    p = (d + (c - d) / 2, (c + d) / 2, th)         # lowest vertex on the floor, leftmost on the wall: a = b = 0
    v = BD.verts(p)
    pg.frame(0, s)
    pg.square(0, p, D.ORANGE[0], D.ORANGE[1], label='Q', width=1.4)
    pg.cell(0, (1, s - 1, 1, s - 1), stroke='#555', dash='6,4', width=1.4, label='(1, s-1)^2')
    pg.cell(0, (0, 1, 0, 1), stroke=D.RED, dash='2,2', width=1.0)
    vR, vT = v[np.argmax(v[:, 0])], v[np.argmax(v[:, 1])]
    lower, upper = (1 - d) / c, (c + d - 1) / d
    ell = 0.5 * (max(lower, 0) + min(upper, 1))
    P = (vR[0] - ell * d, vR[1] + ell * c)
    pg.poly(0, [tuple(vR), tuple(vT)], 'none', D.RED, width=2.6)
    dot(pg, 0, *P)
    ok, gap, wall = pg.check_partial([p], s)
    pg.text(0, wrap(['geometry check: %s (min wall %.1e)' % (ok, wall),
                '(a) TILT-BAND: a unit square of tilt 10 deg touching both walls of BL (a = b = 0), side %.2f.  Its max-x vertex v_R = (%.3f, %.3f)' % (s, vR[0], vR[1]),
                'and max-y vertex v_T = (%.3f, %.3f) span an edge (red) whose points at parameters l in (%.3f, %.3f) have x > 1 AND y > 1:' % (vT[0], vT[1], max(lower, 0), min(upper, 1)),
                'the dot (%.3f, %.3f) is in the open centre -- lower < upper because (1 - cos)(1 - sin) > 0.  iota(10 deg) = cos + sin - 1 = %.3f,' % (P[0], P[1], BD.iota(th)),
                'depth into the centre %.3f: positive for every tilt, with NO floor (both -> 0 as the tilt -> 0; A89: no loaded tilt floor exists).' % BD.depth_into_centre(p, s)]))
    # (b) the count at n = 11
    a1, a2, a3 = 0.30, 1.30, 2.30
    band = [(a1 + .5, .5, 0.0), (a2 + .5, .5, 0.0), (a3 + .5, .5, 0.0),           # floor: claims BL and BR
            (s - .5, 1.5, 0.0), (s - .5, s - .5, 0.0),                             # right wall: [1,2] and the top one claims TR
            (.8, s - .5, 0.0), (1.8, s - .5, 0.0),                                 # ceiling: the left one claims TL
            (.5, 1.9, 0.0)]                                                        # left wall: one, in [1, s-1)
    core = [(s / 2, s / 2, 0.0)]
    poses = band + core
    classes = ['band'] * 8 + ['core']
    note = draw_overlay(pg, 1, poses, s, classes, labels=False)
    for cx, cy in ((0.5, 0.5), (s - .5, .5), (s - .5, s - .5), (.5, s - .5)):
        pg.cell(1, (cx - .5, cx + .5, cy - .5, cy + .5), stroke=D.RED, dash='2,2', width=1.0)
    pg.text(1, wrap([note, '(b) the count at n = 11, s = %.2f < 4: a four-crowd has no corner slot square, so a wall with 3 flush touchers CLAIMS both its corner' % s,
                'boxes and a wall with 2 claims one; two walls cannot claim the same corner (OVERLAP): B <= 4*3 - 4 = 8 (drawn: 3 + 2 + 2 + 1).',
                'The centre (1, s-1)^2 has side < 2 and holds K <= 1 square (Lemma TWO).  ONE-TILTED gives X >= 4 tilted meeters (not drawn: they',
                'must intrude past the claimed slots).  8 + 1 + 4 = 13 >= 11 = n: the count leaves slack 2 = m^2 - 3 - n and closes nothing;',
                'the four tilted meeters have to fit beside the 8 flush slots AND the pocket has to hold the rest -- a region question (A226: 9 < 11).']))
    # (c) record n = 26
    poses = [tuple(p) for p in rec26['poses']]
    note = draw_overlay(pg, 2, poses, rec26['s'], rec26['classes'], labels=False)
    pg.text(2, wrap([note, '(c) record n = 26 (Friedman 1997), side %.4f < 6: B = %d, K = %d, X = %d, tilted %d, four flush corners, no doubly-met corner.' % (
        rec26['s'], rec26['B'], rec26['K'], rec26['X'], rec26['n_tilted']),
        'The X straddlers are the tilted grain crossing the band line: the record is CROSS-BRACED.  Count bound B <= 4(m-2) = 16 would',
        'apply only to a four-crowd; here B = %d because the four corner slots are flush.  N_record(s - 2 = %.2f) = %d >= K = %d.' % (
            rec26['B'], rec26['sigma'], rec26['N_record'], rec26['K']),
        'Every record n = 5..55 satisfies TILT-BAND, BAND-FLUSH, WALL-EXCESS and K <= N(s-2) (capacity236.md); none is a ring.']))
    return pg.write(os.path.join(PAGES, 'n11_capacity.svg'))


if __name__ == '__main__':
    rs = rows()
    print(page_ring(rs))
    print(page_n11(rs))
