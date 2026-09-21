"""A258 pages (geometry-checked; a note per panel saying what it IS; undecided = grey stipple, never green).
  exchange.svg      the exchange W -> T on a corpus ring (A253, s-hat, 14.545 deg): before / poker kept / normal
  normal_ring.svg   the normal ring with its parameters, the tight C4 ring, and the C4 slice of D at s-hat
  excluded.svg      the structures the normal form excludes, each with its reason and its tag
Every PACKING panel is checked before it is drawn (containment and all pairwise SAT gaps >= -1e-9); a panel that
is NOT a packing says so in its title and shows the overlapping pair in red.
"""
import html
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
import dom258 as Dm          # noqa: E402
import geo258 as G           # noqa: E402
import norm258 as N          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A258-normal-ring')
SC = 78.0
BLUE, RED, ORANGE, GREY, PURPLE = '#2b6cb0', '#c53030', '#dd6b20', '#718096', '#6b46c1'
STIPPLE = ('<defs><pattern id="stip" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" '
           'r="0.9" fill="#a0aec0"/></pattern></defs>')


class Panel:
    def __init__(self, x0, y0, s, title):
        self.x0, self.y0, self.s, self.o = x0, y0, s, []
        self.o.append('<text x="%.1f" y="%.1f" font-size="12" font-weight="bold">%s</text>' % (x0, y0 - 8, html.escape(title)))
        self.poly([(0, 0), (s, 0), (s, s), (0, s)], fill='none', stroke='#1a202c', stroke_width='2.2')

    def pt(self, p):
        return self.x0 + p[0] * SC, self.y0 + (self.s - p[1]) * SC

    def poly(self, V, **kw):
        pts = ' '.join('%.2f,%.2f' % self.pt(p) for p in V)
        self.o.append('<polygon points="%s" %s/>' % (pts, ' '.join('%s="%s"' % (k.replace('_', '-'), v)
                                                                   for k, v in kw.items())))

    def sq(self, Q, col=BLUE, name=None, op='0.20'):
        self.poly(Q, fill=col, fill_opacity=op, stroke=col, stroke_width='1.5')
        if name:
            self.text(np.asarray(Q).mean(0), name, 11, col)

    def cell(self, Q, col=ORANGE, dash='3,3'):
        self.poly(Q, fill='none', stroke=col, stroke_width='1.5', stroke_dasharray=dash)

    def text(self, p, s, size=10, fill='#1a202c'):
        x, y = self.pt(p)
        self.o.append('<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="middle">%s</text>'
                      % (x, y + 4, size, fill, s))

    def cells(self):
        for k, R in G.cells(self.s).items():
            self.poly(R, fill='none', stroke='#a0aec0', stroke_width='0.7', stroke_dasharray='5,4')

    def note(self, lines):
        import textwrap
        lines = [seg for ln in lines for seg in textwrap.wrap(ln, 74)]
        for k, ln in enumerate(lines):
            self.o.append('<text x="%.1f" y="%.1f" font-size="10.5" fill="#2d3748">%s</text>'
                          % (self.x0, self.y0 + self.s * SC + 30 + 13 * k, html.escape(ln)))


def checked(sq, s):
    cm, pg = G.check_packing(sq, s)
    assert cm >= -1e-9 and pg >= -1e-9, (cm, pg)
    return 'geometry check: containment %.1e, least pair gap %.1e' % (cm, pg)


def write(name, panels, w, h, head):
    os.makedirs(PAGES, exist_ok=True)
    body = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Segoe UI, Arial">' % (w, h),
            STIPPLE, '<rect width="100%" height="100%" fill="white"/>',
            '<text x="20" y="24" font-size="15" font-weight="bold">%s</text>' % head]
    for P in panels:
        body += P.o
    body.append('</svg>')
    open(os.path.join(PAGES, name), 'w', encoding='utf-8').write('\n'.join(body))
    print('wrote', name)


def page_exchange():
    name, s, sq = [r for r in N.load() if r[0].startswith('A253 tau=14.545 s=3.877')][0]
    W = 4 * SC + 120
    pans = []
    P = Panel(20, 60, s, '(a) BEFORE: A253 ring + poker, s = %.6f' % s)
    P.cells()
    for i, Q in enumerate(sq):
        P.sq(Q, PURPLE if i == 8 else BLUE, 'F' if i == 8 else None)
    _, info = N.normalise(sq, s, True)
    for w, rec in enumerate(info):
        i1, _ = N.wall_pair(sq[:8], s, w)
        T = sq[i1] + (1 / math.cos(rec['phi_deg'] * G.DEG)) * np.array(N.EW[w], float)
        P.cell(T, RED if rec['status'].startswith('LOCKED') else ORANGE)
    P.note(['IS: a corpus ring (8 wall touchers, blue) with its ribbon poker F (purple); ' + checked(sq, s),
            'dotted: the four NORMAL CELLS T = s1 + sec(phi) e.  Orange: met by the next toucher W only',
            '(exchange available).  Red: met by W AND the poker -- the wall is LOCKED: |M(T)| = 2.'])
    pans.append(P)
    curK, infoK = N.normalise(sq, s, True)
    P = Panel(20 + W, 60, s, '(b) poker KEPT: three walls exchanged, one locked')
    P.cells()
    for i, Q in enumerate(curK):
        P.sq(Q, PURPLE if i == 8 else BLUE, 'F' if i == 8 else None)
    P.note(['IS: the packing after W -> T on every unlocked wall; ' + checked(curK, s),
            'walls: ' + ', '.join('%d %s' % (i['wall'], i['status'].split(' ')[0]) for i in infoK),
            'Row-normal as it stands: the locked wall stays an OPEN PAIR (normal_ring.md s.3.4, the hybrid family).'])
    pans.append(P)
    curR, infoR = N.normalise(sq, s, False)
    a = [i['a'] for i in infoR]
    phi = [i['phi_deg'] * G.DEG for i in infoR]
    best = None
    for w in range(4):
        a2 = list(a)
        for sh in (0.0, max(0.0, infoR[w]['W_minus_T_along_wall'])):
            a2[w] = a[w] + sh
            if G.in_D(s, a2, phi, False) > 0 and min(G.tooth_terms(s, a2[w], phi[w])) > 0:
                nine = G.ring(s, a2, phi) + [G.seated(s, w, a2[w], phi[w])]
                if min(G.check_packing(nine, s)) >= -1e-9 and G.hall_min(nine, s)[0] >= 1 and best is None:
                    best = (nine, w, list(a2))
    nine, w, a2 = best
    P = Panel(20 + 2 * W, 60, s, '(c) poker lifted, four walls exchanged: NORMAL RING + seated poker')
    P.cells()
    for i, Q in enumerate(nine):
        P.sq(Q, PURPLE if i == 8 else BLUE, 'F' if i == 8 else None)
    P.poly(G.ribbon(s, w), fill='url(#stip)', stroke='none')
    P.note(['IS: a point of D (margin %.4f) with the SEATED poker in the tooth of wall %d; ' % (G.in_D(s, a2, phi), w)
            + checked(nine, s), 'Hall minimum = %d: family-stuck as a 9-square structure.  Stipple: that wall\'s'
            % G.hall_min(nine, s)[0], 'ribbon [s-2, 2] x [0, 1].  a = (%s), phi = %.3f deg.'
            % (', '.join('%.3f' % v for v in a2), phi[0] / G.DEG)])
    pans.append(P)
    write('exchange.svg', pans, int(3 * W + 20), int(60 + s * SC + 150),
          'A258 -- the exchange W -> T on a corpus ring (Lemma NORMAL-CELL), before / after')


def page_ring():
    s, ph = G.SHAT, 14.545 * G.DEG
    a0, b0 = G.tight_ring(s, ph)
    sq = G.ring(s, [a0] * 4, [ph] * 4)
    nine = sq + [G.seated(s, 0, a0, ph)]
    P = Panel(20, 60, s, '(a) the TIGHT C4 normal ring at s-hat, phi = 14.545 deg')
    P.cells()
    P.poly(G.ribbon(s, 0), fill='url(#stip)', stroke='none')
    for i, Q in enumerate(nine):
        P.sq(Q, PURPLE if i == 8 else BLUE, ('Q1', 'Q2')[i] if i < 2 else ('F' if i == 8 else None))
    c, g = math.cos(ph), math.sin(ph)
    P.poly([(a0 + g, 0), (a0 + 1 / c + g, 0), (a0 + c + g, g)], fill=GREY, fill_opacity='0.5', stroke='none')
    P.text((a0 / 2, -0.12), 'a=%.3f' % a0)
    P.text((s - b0 / 2, -0.12), 'b=%.3f' % b0)
    P.note(['IS: a = (K cos - 1)/(cos - sin), b = K - a: all four corners in contact (a sin + b cos = 1); '
            + checked(nine, s), 'grey: the SEALED triangle under the row (legs 1, tan phi).  F: the seated poker, vertex'
            ' at the tooth apex', '(a + sec, cos); Hall minimum of the nine = %d.  Stipple: the floor\'s ribbon.'
            % G.hall_min(nine, s)[0]])
    W = 4 * SC + 120
    P2 = Panel(20 + W, 60, s, '(b) C4 slice of D at s-hat: phi (across, 0..45 deg) vs a (up, 0..1)')
    n = 180
    for i in range(n):
        for j in range(n):
            deg, a = 45.0 * (i + 0.5) / n, (j + 0.5) / n
            v = G.in_D(s, [a] * 4, [deg * G.DEG] * 4)
            if v > 0:
                tooth = min(G.tooth_terms(s, a, deg * G.DEG)) > 0
                x, y = s * i / n, s * j / n
                P2.poly([(x, y), (x + s / n, y), (x + s / n, y + s / n), (x, y + s / n)],
                        fill=PURPLE if tooth else BLUE, fill_opacity='0.55', stroke='none')
    for deg in (0, 15, 30, 45):
        P2.text((s * deg / 45.0, -0.12), '%d' % deg)
    for a in (0.5, 1.0):
        P2.text((-0.12, s * a), '%.1f' % a)
    ts = [(s * d / 45.0, s * G.tight_ring(s, d * G.DEG)[0]) for d in np.linspace(0.5, 29, 60)]
    P2.o.append('<polyline points="%s" fill="none" stroke="#1a202c" stroke-width="1.4"/>'
                % ' '.join('%.1f,%.1f' % P2.pt(p) for p in ts))
    P2.note(['IS: the set {(phi, a): (a, a, a, a; phi, phi, phi, phi) in D} at s-hat, exact closed forms (family258.md).',
             'blue: in D; purple: in D AND the tooth reaches the ribbon (a seated poker exists); black: D_tight.',
             'White is NOT "excluded": it is outside the family; the classification claim is NORMAL-RING [C].'])
    write('normal_ring.svg', [P, P2], int(2 * W + 20), int(60 + s * SC + 150),
          'A258 -- the NORMAL RING: a pinwheel of four common-tilt pairs, parameters (a_w, phi_w), and its domain D')


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


if __name__ == '__main__':
    page_exchange()
    page_ring()
    page_excluded()
