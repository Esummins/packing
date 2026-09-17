"""A249 pages (docs/residue_map/campaigns/A249-type-t-chase/):
  type_t_corner.svg    a type-T corner's forced structure: T-CELLS / T-TIP (the chords at height 1),
                       the own-tip supply of c01, the mutual wall pair at s-hat (the wall witness);
  type_t_ring.svg      the all-ADJ type-T ring at s-hat (every cell doubly met by the eight meeters)
                       and its pocket: the one square that fits, PIERCE(1) = 0;
  tightest_witness.svg the tightest locked type-T corner of the genuine FJ points (least side).
Every configuration panel prints its geometry check (containment, disjointness, cells) in its note.
    python pages249.py
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
import geom249 as T                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402
import twotilted249 as W                                              # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
import pages248 as P8                                                 # noqa: E402
import external248 as X                                               # noqa: E402
from draw244 import Page                                              # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A249-type-t-chase')
BLUE, RED, GREEN, GREY, ORANGE = P8.BLUE, P8.RED, P8.GREEN, P8.GREY, P8.ORANGE
poly, geo_check, frame_cells = P8.poly, P8.geo_check, P8.frame_cells


def corner_panel(pg, key, x, y, A, B, s, title, extra_lines, win=(0, 2.4, 0, 2.6)):
    pg.panel(key, x, y, 300, 330, s, win=win)
    frame_cells(pg, key, s, ('c00', 'c01', 'c10'))
    pg.frame(key, s, title)
    poly(pg, key, A, '#dfe8fb', BLUE, 'A')
    poly(pg, key, B, '#fbe3e3', RED, 'B')
    tA, dA, _ = T.frame_params(A, 'A')
    tB, dB, _ = T.frame_params(B, 'B')
    a1 = T.u_A_at_1(tA, dA)
    lam = (G.w(tA) - 1) / (math.sin(tA) * math.cos(tA))
    b2 = T.u_B_at_1(tB, dB) if dB < 1 else None
    pg.polyline([pg._t(key, (0, 1)), pg._t(key, (2.4, 1))], GREY, 0.8, dash='3,3')
    pg.polyline([pg._t(key, (a1, 1)), pg._t(key, (a1 + lam, 1))], BLUE, 3.0)
    if b2 is not None and b2 < 2.4:
        pg.polyline([pg._t(key, (max(0, min(b2, 2.4) - 0.0001), 1)), pg._t(key, (min(b2, 2.4), 1))], RED, 3.0)
        pg.dot(key, (min(b2, 2.4), 1), RED)
    g = geo_check([A, B], s, T.CELLS_C)
    cells = 'c00:%d c01:%d c10:%d' % (g[2]['c00'], g[2]['c01'], g[2]['c10'])
    pg.note(x, y + 340, ['theta_A %.1f, delta_A %.3f | theta_B %.1f, delta_B %.3f' % (math.degrees(tA), dA, math.degrees(tB), dB),
                         'A\'s chord at height 1: [%.3f, %.3f]; B\'s cap ends at u_B(1) = %s' % (a1, a1 + lam, '%.3f' % b2 if b2 is not None else '-'),
                         'check: pair gap %.2e, wall gap %.2e, cells %s' % (g[0], g[1], cells)] + extra_lines)


def page_corner():
    s = 3.877084
    pg = Page(1000, 460, 'A249 type-T corner')
    S = json.load(open(os.path.join(RES, 'typet249_summary.json'), encoding='utf-8'))
    t = S['tightest_locked'][0]
    A = T.floor_square(math.radians(t['theta_A']), t['delta_A'])
    B = T.wall_square(math.radians(t['theta_B']), t['delta_B'])
    corner_panel(pg, 'a', 20, 40, A, B, t['s'], '(a) the tightest LOCKED type-T corner: %s %s, s = %.4f' % (t['rid'][3:23], t['corner'], t['s']),
                 ['depths d_A %.3f, d_B %.3f; A\'s tip meets c01: %s (T-TIP: right of B\'s cap)' % (t['d_A'], t['d_B'], T.A_meets_c01(math.radians(t['theta_A']), t['delta_A']))])
    # (b) the own-tip supply: A on all three cells, B on c00, c01 (u_A(1) >= u_B(1) < 1)
    tB, dB = math.radians(30), 0.55
    tA, dA = math.radians(28), 0.35
    A2, B2 = T.floor_square(tA, dA), T.wall_square(tB, dB)
    corner_panel(pg, 'b', 350, 40, A2, B2, s, '(b) own-tip supply of c01: A meets c00, c01, c10; B misses c10',
                 ['A\'s chord at height 1 starts right of B\'s cap (u_A(1) >= u_B(1)): the only way', 'a floor-touching A reaches c01 beside a wall-touching B (Lemma T-TIP)'])
    # (c) the mutual wall pair at s-hat from the wall witness (sub-case BB)
    fn = os.path.join(RES, 'twotilted249_wall.json')
    if os.path.exists(fn):
        d = json.load(open(fn, encoding='utf-8'))
        key = '%.6f' % s
        if key in d and d[key]['result']['BB']['sup_margin'] > 0:
            xw = d[key]['result']['BB']['x']
            B3, A3 = W.corner_pair(*xw[:4])
            Bp, Ap = (W.place(V, 'TL', s) for V in W.corner_pair(*xw[4:8]))
            pg.panel('c', 680, 40, 300, 330, s, win=(0, 2.4, 0, s))
            frame_cells(pg, 'c', s)
            pg.frame('c', s, '(c) TWO-TILTED fails: the mutual type-T wall pair at s-hat')
            for V, col, fill, lab in ((A3, BLUE, '#dfe8fb', 'A'), (B3, RED, '#fbe3e3', 'B'), (Ap, BLUE, '#dfe8fb', "A'"), (Bp, RED, '#fbe3e3', "B'")):
                poly(pg, 'c', V, fill, col, lab)
            g = geo_check([A3, B3, Bp, Ap], s, G.cells(s))
            pg.note(680, 380, ['sup SAT margin %.4f > 0: B meets c\'01 and B\' meets c01, all four tilted' % d[key]['result']['BB']['sup_margin'],
                               'check: pair gap %.2e, wall gap %.2e; c00:%d c01:%d c\'01:%d c\'00:%d' % (g[0], g[1], g[2]['c00'], g[2]['c01'], g[2]["c'01"], g[2]["c'00"]),
                               'no analogue of s* > s-hat: the wall carries two type-T corners on the window'])
    pg.text(20, 22, 'A249 -- the type-T corner: T-CELLS / T-TIP (the chords at height 1), the own-tip supply, the mutual wall pair on the window', 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'type_t_corner.svg'))


def page_ring():
    fn = os.path.join(RES, 'twotilted249_ring2.json')
    if not os.path.exists(fn):
        return
    d = json.load(open(fn, encoding='utf-8'))
    keys = [k for k, v in sorted(d.items()) if v['result']['sup_margin'] > 0]
    if not keys:
        return
    key = '3.877084' if '3.877084' in keys else keys[0]
    s, x = float(key), d[key]['result']['x']
    polys, names, _ = W.ring_polys(x, s, True)
    pk = {}
    pf = os.path.join(RES, 'pocket249.json')
    if os.path.exists(pf):
        pk = json.load(open(pf, encoding='utf-8')).get('ring2@' + key, {})
    pg = Page(1000, 580, 'A249 type-T ring')
    C = X.cell_rects(s)
    pg.panel('a', 20, 40, 460, 460, s)
    for k, r in C.items():
        pg.rect('a', r, P8.CELLCOL[k[2:]], '#bbb', 0.7)
    pg.frame('a', s, '(a) the all-ADJ type-T ring at s = %.6f: sup margin %.4f > 0' % (s, d[key]['result']['sup_margin']))
    for n, V in zip(names, polys):
        poly(pg, 'a', V, '#dfe8fb' if n.startswith('A') else '#fbe3e3', BLUE if n.startswith('A') else RED, n)
    pgap, wgap, cnt = geo_check(polys, s, C)
    for k, r in C.items():
        p = pg._t('a', ((r[0] + r[1]) / 2, (r[2] + r[3]) / 2))
        pg.text(p[0], p[1] - 14, '%s:%d' % (k, cnt[k]), 7.5, '#333', anchor='middle')
    pg.note(20, 515, ['x per corner (theta_B, delta_B, theta_A, delta_A): BL %s, BR %s (TR, TL by the half-turn)' % (
        ['%.3f' % v for v in x[:4]], ['%.3f' % v for v in x[4:8]]),
        'check: pair gap %.2e, wall gap %.2e, every cell doubly met by the eight meeters: %s' % (pgap, wgap, all(v >= 2 for v in cnt.values())),
        'every meeter reaches the far slot of its wall: the type-T ring exists on the window (TWO-POKERS\' type-F ring does not)'])
    pg.panel('b', 510, 40, 460, 460, s)
    pg.frame('b', s, '(b) its pocket: one square fits, two do not; PIERCE(1) at the centre = %s' % ('%.1e' % pk['pierce1_centre'] if pk else '-'))
    for n, V in zip(names, polys):
        poly(pg, 'b', V, '#eeeeee', GREY, n, op=0.6)
    if pk:
        for kk, col in (('pocket_1', GREEN), ('pocket_2', ORANGE)):
            for i, p in enumerate(pk[kk]['poses']):
                poly(pg, 'b', G.verts(p), 'none', col, '%s%d' % ('F' if kk == 'pocket_1' else 'G', i), dash='4,3' if kk == 'pocket_2' else None)
        if pk['wall_poke']['fits']:
            poly(pg, 'b', G.verts(pk['wall_poke']['pose']), '#e6f7e3', GREEN, 'P', op=0.5, dash='2,2')
        pg.note(510, 515, ['waste %.3f of pocket area %.3f (A237 census); PIERCE(1) residual %.1e: capacity <= 1 [T-computed]' % (pk['waste'], pk['pocket_area'], pk['pierce1_centre']),
                           'direct search: 1 square least gap %.3f (F0, fits); 2 squares %.3f (G0, G1 overlap); 3: %.3f' % (
                               pk['pocket_1']['best_min_gap'], pk['pocket_2']['best_min_gap'], pk['pocket_3']['best_min_gap']),
                           'P: a free square meeting both slots of the wall x = 0 (FAMILY-STUCK\'s ring family), margin %.3g -- it is the one square' % pk['wall_poke']['best_margin'],
                           '8 + 1 = 9 < 11: this ring is not the skeleton of an eleven-square packing (POCKET-CAP)'])
    pg.text(20, 22, 'A249 -- the all-ADJ type-T ring on the window and its pocket (8 + 1 = 9 < 11)', 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'type_t_ring.svg'))


def page_tightest():
    S = json.load(open(os.path.join(RES, 'typet249_summary.json'), encoding='utf-8'))
    t = S['tightest_locked'][0]
    sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A234-handedness', 'code'))
    import stress234 as St
    z = None
    for wd in St.genuine_fj():
        if wd['name'] == t['rid']:
            z = np.asarray(wd['z'], float)
            break
    if z is None:
        return
    s = float(z[-1])
    polys = [G.verts(z[3 * i:3 * i + 3]) for i in range(11)]
    rows = [json.loads(l) for l in open(os.path.join(RES, 'chase249.jsonl'), encoding='utf-8')]
    v = next(v for r in rows if r['rid'] == t['rid'] for v in r['views'] if v['corner'] == t['corner'] and v['wall'] == t['wall'])
    tt = v['tt']
    pg = Page(1000, 560, 'A249 tightest witness')
    pg.panel('a', 20, 40, 460, 460, s)
    C = X.cell_rects(s)
    for k, r in C.items():
        pg.rect('a', r, P8.CELLCOL[k[2:]], '#bbb', 0.7)
    pg.frame('a', s, '(a) %s, s = %.6f: locked type-T corner %s' % (t['rid'][:30], s, t['corner']))
    for i, V in enumerate(polys):
        col = RED if i == tt['B'] else BLUE if i == tt['A'] else GREY
        poly(pg, 'a', V, '#fbe3e3' if i == tt['B'] else '#dfe8fb' if i == tt['A'] else '#eeeeee', col, str(i), op=0.7)
    pgap, wgap, cnt = geo_check(polys, s, C)
    pg.note(20, 515, ['A = %d (floor side), B = %d (wall side) seen from %s: theta_A %.1f delta_A %.3f, theta_B %.1f delta_B %.3f, depths %.3f / %.3f' % (
        tt['A'], tt['B'], t['wall'], tt['theta_A'], tt['delta_A'], tt['theta_B'], tt['delta_B'], tt['d_A'], tt['d_B']),
        'c01 suppliers %s; c10 suppliers %s; domino/triple %s' % (tt['c01_suppliers'], tt['c10_suppliers'], t['domino']),
        'holders of the locked meeters (class): %s' % tt.get('holder_classes'),
        'check: pair gap %.2e, wall gap %.2e; cells doubly met: %d of 12' % (pgap, wgap, sum(v >= 2 for v in cnt.values()))])
    pg.panel('b', 510, 40, 460, 460, s, win=(0, 2.6, 0, 2.6) if t['corner'] == 'BL' else None)
    pg.frame('b', s, '(b) the corner in its wall frame %s (u = distance to the wall)' % t['wall'])
    Pf = [G.to_wall(V, t['wall'], s) for V in polys]
    if t['corner'] != G.WALL_CORNERS[t['wall']][0]:
        Pf = [G.flip_up(V, s) for V in Pf]
    frame_cells(pg, 'b', s, ('c00', 'c01', 'c10'))
    for i, V in enumerate(Pf):
        if V[:, 0].min() < 2.6 and V[:, 1].min() < 2.6:
            col = RED if i == tt['B'] else BLUE if i == tt['A'] else GREY
            poly(pg, 'b', V, '#fbe3e3' if i == tt['B'] else '#dfe8fb' if i == tt['A'] else '#eeeeee', col, str(i), op=0.7)
    pg.text(20, 22, 'A249 -- the tightest locked type-T corner of the genuine FJ points (least side %.4f > s-hat): every T-inequality holds there' % s, 12, '#111', weight='bold')
    pg.save(os.path.join(OUT, 'tightest_witness.svg'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    page_corner()
    page_ring()
    page_tightest()
    print('pages written to', OUT)
