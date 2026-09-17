"""A248 pages (docs/residue_map/campaigns/A248-corner-chase/):
  bl_structure.svg   BL's structure step by step: the poker beside the flat meeter (CCW), the exact
                     CW witness refuting POKE's sense, TOP-2 / FLAT-ABOVE, the click and its window;
  chase_ring.svg     the consistent external chase: the 8-square ring at 3.85 with every cell's
                     meeter count, and the pocket's best three-square attempt;
  twelve_stuck_fail.svg  a corpus twelve-stuck packing at its failing step (an unblocked click).
Every configuration panel prints its geometry check (containment, disjointness, cells) in its note.
    python pages248.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402
import external248 as X                                               # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
from draw244 import Page                                              # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A248-corner-chase')
BLUE, RED, GREEN, GREY, ORANGE = '#3b6fd6', '#d63b3b', '#3a9d5d', '#999', '#e08a1e'
CELLCOL = {'00': '#fff3cc', '01': '#e3f0ff', '10': '#e6f7e3'}


def poly(pg, key, V, fill, stroke, label=None, op=0.8, dash=None):
    pts = ' '.join('%.2f,%.2f' % pg._t(key, p) for p in V)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pg.parts.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="1.3"%s/>'
                    % (pts, fill, op, stroke, d))
    if label:
        c = V.mean(axis=0)
        p = pg._t(key, c)
        pg.text(p[0], p[1] + 3, label, 8.5, '#111', anchor='middle')


def geo_check(polys, s, cells):
    """(min pair gap, min wall gap, {cell: meeter count}) as drawn."""
    pg = min([G.poly_gap(polys[i], polys[j]) for i in range(len(polys)) for j in range(i)] + [9.0])
    wg = min(min(V[:, 0].min(), V[:, 1].min(), s - V[:, 0].max(), s - V[:, 1].max()) for V in polys)
    cnt = {k: sum(G.depth_rect(V, r) > 1e-9 for V in polys) for k, r in cells.items()}
    return float(pg), float(wg), cnt


def frame_cells(pg, key, s, names=('c00', 'c01', 'c10', "c'00", "c'01", "c'10")):
    for k, r in G.cells(s).items():
        if k in names:
            pg.rect(key, r, CELLCOL[k[-2:]], '#bbb', 0.7)


def page_bl(s=3.85):
    pg = Page(1180, 640, 'A248 BL structure')
    # (a) A flat + poker CCW resting on A's tip (TILT-MIN tight)
    th, delta = math.radians(25), 0.9
    d = (delta - math.sin(th)) * math.tan(th)
    A, B = G.flat_floor(delta), G.poker(th, d)
    win = (0, 2.4, 0, 3.0)
    pg.panel('a', 20, 40, 270, 340, s, win=win)
    frame_cells(pg, 'a', s, ('c00', 'c01', 'c10'))
    pg.frame('a', s, '(a) the poker B beside the flat A: sense CCW, notch at L')
    poly(pg, 'a', A, '#dfe8fb', BLUE, 'A'); poly(pg, 'a', B, '#fbe3e3', RED, 'B')
    pf = G.poke_facts(B, delta)
    L = B[3]; T = B[2]
    pg.dot('a', L, RED); pg.dot('a', T, RED); pg.dot('a', B[0], RED)
    pg.polyline([pg._t('a', (0, L[1])), pg._t('a', (0, 2.9))], ORANGE, 2.5)
    pg.polyline([pg._t('a', L), pg._t('a', T)], ORANGE, 2.5)
    g = geo_check([A, B], s, {k: v for k, v in G.cells(s).items() if not k.startswith("c'")})
    pg.note(20, 395, ['theta = 25 deg, delta = 0.9, d = (delta - sin) tan = %.3f (TILT-MIN tight)' % d,
                      'lowest V = (%.3f, %.3f), top T = (%.3f, %.3f) >= 2  [TOP-2]' % (B[0][0], B[0][1], T[0], T[1]),
                      'check: pair gap %.2e, wall gap %.2e, cells c00:%d c01:%d c10:%d' % (g[0], g[1], g[2]['c00'], g[2]['c01'], g[2]['c10']),
                      'the notch (orange) between the wall and L->T is where a second', 'meeter of c01 may enter; A never meets c01 (TYPE-F-OWN)'])
    # (b) the CW witness
    B2, A2 = G.poker(math.atan2(4, 3), 0.1), G.flat_floor(0.95)
    pg.panel('b', 310, 40, 270, 340, s, win=win)
    frame_cells(pg, 'b', s, ('c00', 'c01', 'c10'))
    pg.frame('b', s, '(b) POKE\'s sense is NOT forced: the exact CW witness')
    poly(pg, 'b', A2, '#dfe8fb', BLUE, 'A'); poly(pg, 'b', B2, '#fbe3e3', RED, 'B')
    for p in (B2[0], B2[2], B2[3]):
        pg.dot('b', p, RED)
    f = G.poke_witness_exact()
    g = geo_check([A2, B2], s, {k: v for k, v in G.cells(s).items() if not k.startswith("c'")})
    pg.note(310, 395, ['cos = 3/5, sin = 4/5 (53.13 deg), V = (4/5, 9/10), L = (0, 3/2), T = (3/5, 23/10)',
                       'A = [19/20, 39/20] x [0,1]; edge V->R at height 1: x = 7/8 <= 19/20 (exact)',
                       'lowest vertex x = 0.8 > highest x = 0.6: the CW sense; B meets c00, c01',
                       'check: pair gap %.2e, wall gap %.2e, cells c00:%d c01:%d c10:%d' % (g[0], g[1], g[2]['c00'], g[2]['c01'], g[2]['c10']),
                       'exact witness fields: %s' % ', '.join(k for k in ('disjoint_from_A', 'touches_wall', 'V_in_box') if f[k])])
    # (c) FLAT-ABOVE: the diagonal V->T crosses any flat wall square with y0 < 2
    pg.panel('c', 600, 40, 270, 340, s, win=win)
    frame_cells(pg, 'c', s, ('c00', 'c01', 'c10'))
    pg.frame('c', s, '(c) FLAT-ABOVE: no flat wall square meets c01 above B')
    W = np.array([(0, 1.6), (1, 1.6), (1, 2.6), (0, 2.6)], float)
    poly(pg, 'c', A, '#dfe8fb', BLUE, 'A'); poly(pg, 'c', B, '#fbe3e3', RED, 'B')
    poly(pg, 'c', W, '#eeeeee', GREY, 'flat [0,1]x[1.6,2.6]', op=0.5, dash='4,3')
    pg.polyline([pg._t('c', B[0]), pg._t('c', B[2])], GREEN, 2.2)
    gap = G.poly_gap(W, B)
    pg.note(600, 395, ['the open diagonal V->T (green) is interior to B and crosses the band',
                       '(0,1) x (y0, y0+1) for every 0 < y0 < 2: overlap depth here %.3f' % -gap,
                       'so c01\'s second meeter is a TILTED wall square, or an off-wall square',
                       '(through the notch or beside B over A) -- never a flat wall square;',
                       'this kills the flat-ADJ / alternating patterns of A246 s.3.4 (b), (c)'])
    # (d) the click: the pair (B, B') and the flush stack [0,1]x[1,3]
    thf, df = math.radians(70), 0.06
    Bp = G.flip_up(G.poker(thf, df), s)
    while G.poly_gap(B, Bp) < 0.01 and df < 0.95:          # a deep c'-meeter: type-T c', no flat binds it
        df += 0.01
        Bp = G.flip_up(G.poker(thf, df), s)
    pg.panel('d', 890, 40, 270, 340, s, win=(0, 2.4, 0, s))
    frame_cells(pg, 'd', s)
    pg.frame('d', s, '(d) NO-ROTATE: the click of (B, B\') to [0,1]x[1,3]')
    poly(pg, 'd', A, '#dfe8fb', BLUE, 'A'); poly(pg, 'd', B, '#fbe3e3', RED, 'B'); poly(pg, 'd', Bp, '#fbe3e3', RED, "B'")
    S1 = np.array([(0, 1), (1, 1), (1, 2), (0, 2)], float); S2 = S1 + (0, 1)
    poly(pg, 'd', S1, 'none', GREEN, None, dash='5,3'); poly(pg, 'd', S2, 'none', GREEN, None, dash='5,3')
    dB, dBp = G.depth_corner(B), G.depth_corner(G.flip_up(Bp, s))
    g = geo_check([A, B, Bp], s, G.cells(s))
    pg.note(890, 395, ['s = %.2f: d_BL(B) = %.3f, d_TL(B\') = %.3f, sum %.3f vs 4 - s = %.3f' % (s, dB, dBp, dB + dBp, 4 - s),
                       'Psi(flush) - Psi = (4 - s) - d - d\' = %.3f < 0: a retreat unless the' % G.click_gain(dB, dBp, s),
                       'window (green) minus B, B\' is met by a THIRD square [T]',
                       'check: pair gap %.2e, wall gap %.2e, c00:%d c01:%d c\'00:%d c\'01:%d' % (g[0], g[1], g[2]['c00'], g[2]['c01'], g[2]["c'00"], g[2]["c'01"]),
                       'A never blocks (A in {v <= 1}); the next corner\'s flat ceiling meeter always does'])
    pg.text(20, 22, 'A248 -- BL\'s structure: POKE (true form + the CW witness), TOP-2, FLAT-ABOVE, NO-ROTATE\'s click (wall frame u = 0 is the shared wall)', 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'bl_structure.svg'))


def page_two_pokers():
    """the TWO-POKERS pair at its threshold s* (corner-to-corner contact) and the same tilts at s-hat."""
    tp = json.load(open(os.path.join(ATT, 'results', 'twopokers248.json'), encoding='utf-8'))
    th = math.radians(tp['line']['theta_deg'])
    thf = math.pi / 2 - th
    d, df = (1 - math.sin(th)) * math.tan(th), (1 - math.sin(thf)) * math.tan(thf)
    pg = Page(1000, 600, 'A248 two pokers')
    for key, s, x, lab in (('a', tp['line']['s_star'], 20, '(a) s = s* = %.6f: the tight pair (T = T\')'),
                           ('b', 3.877084, 510, '(b) the same tilts at s-hat = %.6f: overlap')):
        B = G.poker(th, d)
        Bp = G.flip_up(G.poker(thf, df), s)
        A = G.flat_floor(1.0)
        Ap = np.array([(1, s - 1), (2, s - 1), (2, s), (1, s)], float)
        pg.panel(key, x, 40, 460, 460, s, win=(0, 2.4, 0, s))
        frame_cells(pg, key, s)
        pg.frame(key, s, lab % s)
        poly(pg, key, A, '#dfe8fb', BLUE, 'A'); poly(pg, key, Ap, '#dfe8fb', BLUE, "A'")
        poly(pg, key, B, '#fbe3e3', RED, 'B'); poly(pg, key, Bp, '#fbe3e3', RED, "B'")
        pg.dot(key, B[2], RED); pg.dot(key, Bp[2], RED)
        gap = G.poly_gap(B, Bp)
        pg.note(x, 515, ['theta = %.3f, theta_f = %.3f deg (theta + theta_f = 90), d = (1 - sin) tan = %.4f, d\' = %.4f' % (
            math.degrees(th), math.degrees(thf), d, df),
            'B top T = (%.3f, %.3f) >= 2; B\' bottom T\' = (%.3f, %.3f) <= s - 2 = %.3f' % (B[2][0], B[2][1], Bp[2][0], Bp[2][1], s - 2),
            'SAT gap B vs B\' = %+.2e (%s); offsets delta = delta\' = 1 (the sup)' % (gap, 'touching' if abs(gap) < 1e-6 else 'OVERLAP' if gap < 0 else 'disjoint')])
    pg.text(20, 22, 'A248 -- TWO-POKERS: two type-F pokers on one wall need s >= s* = 2 + min_theta [tan(45-theta/2) + tan(theta/2) + sec theta] = %.7f > s-hat' % tp['line']['s_star'], 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'two_pokers.svg'))


def page_ring():
    fn = os.path.join(ATT, 'results', 'external248_3.9700.json')
    if not os.path.exists(fn):
        return
    d = json.load(open(fn, encoding='utf-8'))
    s = d['side']
    polys = X.ring(d['x'], s)
    pg = Page(1000, 560, 'A248 external chase')
    pg.panel('a', 20, 40, 460, 460, s)
    C = X.cell_rects(s)
    for k, r in C.items():
        pg.rect('a', r, CELLCOL[k[2:]], '#bbb', 0.7)
    pg.frame('a', s, '(a) the 6-parameter ring search at s = %.2f (> s*): best margin %.1e, NOT a strict ring' % (s, min(d['min_pair_gap'], d['min_second_depth'])))
    for name, V in zip(X.NAMES, polys):
        poly(pg, 'a', V, '#dfe8fb' if name.startswith('A') else '#fbe3e3', BLUE if name.startswith('A') else RED, name)
    pgap, wgap, cnt = geo_check(polys, s, C)
    for k, r in C.items():
        p = pg._t('a', ((r[0] + r[1]) / 2, (r[2] + r[3]) / 2))
        pg.text(p[0], p[1] - 14, '%s:%d' % (k, cnt[k]), 7.5, '#333', anchor='middle')
    pg.note(20, 515, ['x = (dBL, dBR, theta, d, theta_f, d_f) = %s' % ', '.join('%.4f' % v for v in d['x']),
                      'check: pair gap %.2e, wall gap %.2e, every cell doubly met: %s (least second depth %.3g)' % (
                          pgap, wgap, all(v >= 2 for v in cnt.values()), d['min_second_depth'])])
    pg.panel('b', 510, 40, 460, 460, s)
    pg.frame('b', s, '(b) the same poses: the 12 cell counts as drawn (every cell needs 2)')
    for name, V in zip(X.NAMES, polys):
        poly(pg, 'b', V, '#eeeeee', GREY, name, op=0.6)
    if 'pocket_3' in d:
        for k, p in enumerate(d['pocket_3']['poses']):
            poly(pg, 'b', G.verts(p), '#e6f7e3', GREEN, 'F%d' % k, op=0.7)
        pg.note(510, 515, ['least gap of the three free squares: %.4f (%s) over %d restarts' % (
            d['pocket_3']['best_min_gap'], 'FITS' if d['pocket_3']['fits'] else 'negative: they overlap', 300),
            'one square: %.4f, two: %.4f -- the room statement POCKET(11) is the residue' % (
                d['pocket_1']['best_min_gap'], d['pocket_2']['best_min_gap'])])
    lo = os.path.join(ATT, 'results', 'external248_3.8500.json')
    if os.path.exists(lo):
        e = json.load(open(lo, encoding='utf-8'))
        pg.text(20, 548, 'at s = 3.85 (< s* = 3.9342) the same 6-parameter search reaches least margin %.1e only: the ring does not exist below s* (TWO-POKERS)' % min(e['min_pair_gap'], e['min_second_depth']), 9.2, '#333')
    pg.text(20, 22, 'A248 -- the external pattern (flats on two opposite walls, mutual pokers on the other two): excluded below s* = 3.9342 (TWO-POKERS); above s* the ring search reaches margin 0 only [M]', 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'chase_ring.svg'))


def page_fail():
    rows = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'chase248.jsonl'), encoding='utf-8')]
    sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A246-construct-towards', 'code'))
    import check246 as K
    zs = {rid: z for rid, z, _ in K.corpus_282() + K.certified_34()}
    pick = None
    for r in rows:
        if r['kind'].startswith('fj'):
            continue
        for v in r['views']:
            for q in v.get('poke', {}).get('pairs', []):
                if not q['blocked'] and (pick is None or r['s'] < pick[0]['s']):
                    pick = (r, v, q)
    if pick is None:
        return
    r, v, q = pick
    z = np.asarray(zs[r['rid']], float)
    s = float(z[-1])
    polys = [G.verts(z[3 * i:3 * i + 3]) for i in range(11)]
    wall = v['wall']
    P = [G.to_wall(V, wall, s) for V in polys]
    if v['corner'] != G.WALL_CORNERS[wall][0]:
        P = [G.flip_up(V, s) for V in P]
    pg = Page(1000, 560, 'A248 failing step')
    pg.panel('a', 20, 40, 460, 460, s)
    for k, rc in G.cells(s).items():
        pg.rect('a', rc, CELLCOL[k[-2:]], '#bbb', 0.7)
    pg.frame('a', s, '(a) %s, s = %.6f, wall %s in its frame' % (r['rid'][:38], s, wall))
    B, Bp, A = v['poke']['B'], q['B_up'], v['poke']['A']
    for i, V in enumerate(P):
        col = RED if i in (B, Bp) else BLUE if i == A else GREY
        poly(pg, 'a', V, '#fbe3e3' if i in (B, Bp) else '#dfe8fb' if i == A else '#eeeeee', col, str(i), op=0.7)
    S1 = np.array([(0, 1), (1, 1), (1, 2), (0, 2)], float)
    poly(pg, 'a', S1, 'none', GREEN, None, dash='5,3'); poly(pg, 'a', S1 + (0, 1), 'none', GREEN, None, dash='5,3')
    pgap, wgap, cnt = geo_check(P, s, G.cells(s))
    blk = G.window_blockers(P, {B, Bp}, s)
    pg.note(20, 515, ['pair (B=%d, B\'=%d) beside A=%d: d = %.4f, d\' = %.4f, Psi-gain of the flush stack = %.4f < 0' % (
        B, Bp, A, v['poke']['d_B'], q['d_up'], q['gain']),
        'window [0,1]x[1,3] blockers: %s -> the click is a Psi-lowering exchange: not Psi-minimal, fails NO-ROTATE' % (blk or 'none'),
        'check (frame): pair gap %.2e, wall gap %.2e; c00:%d c01:%d c\'00:%d c\'01:%d' % (pgap, wgap, cnt['c00'], cnt['c01'], cnt["c'00"], cnt["c'01"])])
    pg.text(20, 22, 'A248 -- a twelve-stuck corpus packing at its failing step (all 764 fail at S0: none is locked; this is the geometric step)', 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'twelve_stuck_fail.svg'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    page_bl()
    page_two_pokers()
    page_ring()
    page_fail()
    print('pages written to', OUT)
