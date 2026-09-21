"""A258 pages, part 2: excluded.svg (uses the Panel / write helpers of pages258)."""
import json
import os

import dom258 as Dm
import geo258 as G
from pages258 import BLUE, HERE, RED, SC, Panel, checked, write


def page_excluded():
    s = G.SHAT
    pans = []
    W = 4 * SC + 120
    jobs = [('(a) mixed senses + + + - (14.5 deg)', (1, 1, 1, -1), (2, 2, 2, 2), [14.545] * 4,
             '[M] scan258: sup-margin < 0 on the whole tilt grid; -> 0 only as all tilts -> 0.'),
            ('(b) a row of THREE (tilts 8 deg)', (1, 1, 1, 1), (3, 2, 2, 2), [8.0] * 4,
             '[T] common tilt: 2 sec + cos + sin + tan(45 - phi/2) >= 4 > s.  [M] any tilts: scan258.'),
            ('(c) alternating + - + - (10 deg)', (1, -1, 1, -1), (2, 2, 2, 2), [10.0] * 4,
             '[T] near flat: a mixed corner needs a >= 1 - phi/2 AND b >= 1 - phi^2/2.')]
    for k, (title, sg, l, degs, why) in enumerate(jobs):
        phi = [d * G.DEG for d in degs]
        t, a = Dm.sup_margin(s, phi, sg, l, False)
        P = Panel(20 + k * W, 60, s, title + ': NOT a ring')
        P.cells()
        if a is not None:
            sq = G.ring(s, a, phi, sg, l)
            bad = [(i, j) for i in range(len(sq)) for j in range(i) if G.sat_gap(sq[i], sq[j]) < -1e-9]
            badset = {i for p in bad for i in p}
            cl = G.cells(s)
            unmet = [kk for kk in range(4) if sum(G.depth(Q, cl[('C', kk)]) > 1e-9 for Q in sq) < 2]
            for i, Q in enumerate(sq):
                P.sq(Q, RED if i in badset else BLUE)
            for kk in unmet:
                P.poly(cl[('C', kk)], fill=RED, fill_opacity='0.25', stroke=RED, stroke_width='1')
            P.note(['IS: the LP optimum of the offsets for these tilts: least margin %.4f < 0 (dom258.sup_margin); the LP spreads the deficit equally over the corners.' % t,
                    'red squares overlap (%d pair(s)); red boxes are met by fewer than two (%d).' % (len(bad), len(unmet)),
                    why])
        pans.append(P)
    # (d) the COUNTEREXAMPLE on the stretch window: the mixed pattern + + + - exists above s_mix = 3.9298
    rows = [json.loads(ln) for ln in open(os.path.join(HERE, '..', 'results', 'side258.jsonl'), encoding='utf-8')]
    r = [x for x in rows if x['senses'] == [1, 1, 1, -1] and x['lengths'] == [2, 2, 2, 2]][0]
    s2, sg, phi = 3.95, tuple(r['senses']), [d * G.DEG for d in r['tilts_deg']]
    t, a = Dm.sup_margin(s2, phi, sg, (2, 2, 2, 2), False)
    sq = G.ring(s2, a, phi, sg)
    P = Panel(20 + 3 * W, 60, s2, '(d) COUNTEREXAMPLE at s = 3.95: + + + - IS a ring of pairs')
    P.cells()
    for i, Q in enumerate(sq):
        P.sq(Q, RED if sg[i // 2] < 0 else BLUE)
    mt = G.meet_table(sq, s2, 1e-9)
    thin = [k for k, v in mt.items() if len(v) < 2]
    for k in thin:
        P.poly(G.cells(s2)[k], fill='url(#stip)', stroke='none')
    P.note(['IS: a packing of eight squares, four common-tilt ROWS OF TWO, senses + + + - (red = sense -), tilts '
            '(%s) deg, least margin %.4f; ' % (', '.join('%.2f' % d for d in r['tilts_deg']), t) + checked(sq, s2),
            'every corner box is doubly met; stippled: border cells met by only ONE ring square (%d) -- they need a '
            'free square each, so this is NOT an all-ADJ ring (A255 found none: consistent).' % len(thin),
            '[M] least side of this pattern over all tilts: %.4f (side258) -- above s-hat = 3.8771 by 0.053, below 4: '
            'COMMON-SENSE at ring level fails on the stretch window (s-hat, 4), not on [3.82, s-hat].' % r['s_min']])
    pans.append(P)
    write('excluded.svg', pans, int(4 * W + 20), int(60 + s * SC + 150),
          'A258 -- (a)-(c): structures excluded at s-hat, drawn as FAILED constructions;  (d): the mixed-sense ring that EXISTS above 3.93')
