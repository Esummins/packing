"""A239 pages 2 and 3 (docs/residue_map/campaigns/A239-rings-below-4/): rings_reach.svg = (A) the reach curve with
the s = 3.88 / 3.95 / 3.99 thresholds, (A') the contact curve delta(theta) and its corner waste, (B) A226's ring at
S = 3.90, (C) at S = 3.99 -- each ring exact, pocket shaded, uncoverable set hatched, the one square that fits in
grey stipple, PUSH normals, Lemma W arcs, the deficit in red; rings_gear.svg = (D) the wall-to-wall contact ring
at S = 3.95 (k = 0, theta*), (D') the jutting ring (k = 1) with its empty pocket, (E) the corner swap + shrink of the
S = 3.90 ring, (E') its flush end.  Every configuration panel geometry-checked; notes give what it is and the
time per step.   python pages239.py
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import draw239 as DR                                                       # noqa: E402
import geom239 as GM                                                       # noqa: E402
import geom237 as G237                                                     # noqa: E402
import page239a                                                            # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ATT = os.path.abspath(os.path.join(HERE, '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A239-rings-below-4')
RINGS = os.path.join(ATT, 'results', 'rings239.jsonl')
REACH = os.path.join(ATT, 'results', 'reach239.jsonl')
CLICK = os.path.join(ATT, 'results', 'click239.jsonl')


def load(path):
    return [json.loads(l) for l in open(path, encoding='utf-8')]


def ring_panel(pg, k, r, tag, what):
    """one ring: pocket, uncoverable set, members, the interior square, PUSH, forces, Lemma W, deficit."""
    t0 = time.time()
    S, P = r['S'], [tuple(p) for p in r['poses']]
    W = G237.waste(P, S, 1.0)
    DR.pocket(pg, k, P, S)
    DR.shade(pg, k, W['uncov'])
    pg.frame(k, S)
    meet = sorted({i for ms in r['meeters'].values() for i in ms})
    for i, p in enumerate(P):
        fill, stroke = (DR.ORANGE if i in meet else DR.BLUE)
        pg.square(k, p, fill, stroke, label='%d:%.1f' % (i, math.degrees(p[2] % (math.pi / 2))), width=1.6)
    for q in r.get('interior', []):
        pg.square(k, tuple(q), 'url(#stip)', '#777', label='fits', width=1.2, dash='4,3')
    ld = r.get('loaded_deficit') or r.get('deficit')
    if ld:
        DR.forces(pg, k, ld['arrows'], 0.4)
        DR.lemma_w(pg, k, ld['squares'], P)
        DR.deficit(pg, k, ld['per_square'], P)
    DR.push(pg, k, r['push'], P, S)
    if r['pierce1_centre'] <= 1e-9:
        DR.dot(pg, k, S / 2, S / 2)
    ok, gap, wall = pg.check_partial(P + [tuple(q) for q in r.get('interior', [])], S)
    tm = r['times']
    ext = []
    if ld:
        for i, d in ld['per_square'].items():
            ext.append('%s: %s%s' % (i, d.get('direction', 'torque only'), (' + %s torque %+.3f' % (d.get('torque', ''), d['tau'])) if abs(d['tau']) > 1e-6 else ''))
    lines = ['(%s) WHAT IT IS: %s' % (tag, what),
             'ring: %d squares, pattern %s (meeters per corner BL BR TR TL), %d contact rows; free FJ LP (walls + contacts, no floor, no crowd '
             'rows): %s; minimal external load closing the balance: %.3f%s; torque-only: %s.' % (
                 r['n'], r['pattern'], r['n_rows'], r['free_lp'], (r['deficit'] or {}).get('objective', float('nan')),
                 ('; with every PUSH loaded >= 0.1: %.3f' % r['loaded_deficit']['objective']) if r.get('loaded_deficit') else '',
                 'infeasible (the forces cannot close around the ring)' if r['torque_only'] is None else '%.3f' % r['torque_only']['objective']),
             'RED = the deficit rows drawn at the squares that need them (external force at the centre, torque as an arc): ' + ('; '.join(ext) if ext else 'none') + '.',
             'pocket: area %.3f, coverable <= %.3f, waste >= %.3f (hatched); greedy capacity %d (the stipple square); PIERCE(1) at the centre '
             'residual %.1e%s; members an interior square can touch: %s.' % (
                 r['pocket_area'], r['coverable'], r['waste'], r['capacity_greedy'], r['pierce1_centre'],
                 ' => capacity 1' if r['pierce1_centre'] <= 1e-9 else '', [i for i, v in r['touchable'].items() if v['can']]),
             'checks: packing %s (min pair gap %.1e, min wall %.1e; contacts at 0); times: check %.2f s, LP %.2f s, capacity %.1f s, waste %.1f s, '
             'pierce %.1f s, touchable %.1f s; draw %.2f s.' % (ok, gap, wall, tm['check'], tm['lp'], tm['capacity'], tm['waste'], tm['pierce'], tm['touchable'], time.time() - t0)]
    return lines


def page_reach(rings, reach):
    thr, curves = reach[0]['thresholds'], reach[0]['contact_curves']
    tab = reach[1:]
    B = [r for r in rings if r['label'] == 'ring226_S3.90_eps0.02'][0]
    C = [r for r in rings if r['label'] == 'ring226_S3.99_eps0.02'][0]
    pg = DR.page("A239 -- rings strictly below 4: (A) the along-wall REACH of a flat + tilted crowd vs its tilt, (A') the contact curve "
                 "and the corner it wastes, (B) A226's 8-square crowd ring at S = 3.90, (C) at S = 3.99 -- pocket shaded, one square fits", 2, 2, 3.99, note_h=230)
    t0 = time.time()
    pl = DR.Plot(pg, 0, (0.0, 90.0), (0.9, 2.5))
    ths = [t['theta'] for t in tab]
    pl.line(ths, [t['reach_least'] for t in tab], '#1f4e79', 2.0, lab='R(th, sin th + 0.02)')
    pl.line(ths, [t['reach_deep'] for t in tab], '#7b2cbf', 1.6, '6,3', 'R(th, 0.98)')
    pl.line(ths, [t['w'] for t in tab], '#b06a00', 1.2, '3,3', 'cos + sin')
    pl.line(ths, [t['chord'] for t in tab], '#2a9d8f', 1.2, '1,3', '1/max(cos, sin)')
    for S, col in ((3.88, '#d62728'), (3.95, '#e07b00'), (3.99, '#888'), (4.11, '#444')):
        pl.hline(S - 2, col, 's = %.2f: s - 2 = %.2f' % (S, S - 2))
    for S in ('3.88', '3.95', '3.99'):
        pl.vline(thr[S]['least'], '#1f4e79', 'th* %.1f' % thr[S]['least'])
    pl.axes('tilt theta of the crowd\'s tilted meeter (deg)', 'reach R beyond the two corner boxes', [0, 15, 30, 45, 60, 75, 90], [1.0, 1.5, 2.0, 2.5])
    pg.text(0, DR.wrap([
        '(A) WHAT IT IS: the REACH inequality of rings_below_4.md s.1.  A wall of side s between two corner crowds of the flat + tilted type '
        '(flat meeter at offset delta from its wall, TILT-MIN partner of tilt theta) is spanned in contact with k = 0 wall squares iff '
        '2 + R >= s, R(theta, delta) = cos + sin + delta - (delta - sin theta) tan theta; the gap for a third member is s - 2 - R < 1.',
        'Blue: the least-waste crowd (delta = sin theta + 0.02) -- it bridges s only for theta >= theta* = %.1f / %.1f / %.1f deg at s = 3.88 / 3.95 / 3.99 '
        '(the PI\'s "fairly high tilt"); purple: the deep-offset crowd (delta = 0.98) bridges every s < 3.98 at any tilt but wastes the corner '
        '(A\'); orange / green: the extent cos + sin and A231\'s chord 1/max(cos, sin) of one tilted square for comparison.  %.2f s.'
        % (thr['3.88']['least'], thr['3.95']['least'], thr['3.99']['least'], time.time() - t0)]))
    t0 = time.time()
    pl = DR.Plot(pg, 1, (0.0, 45.0), (0.0, 1.0))
    for S, col in (('3.88', '#d62728'), ('3.95', '#e07b00'), ('3.99', '#888')):
        cur = curves[S]
        pl.line([c['theta'] for c in cur], [c['delta'] for c in cur], col, 1.8, lab='delta, s=' + S)
        pl.line([c['theta'] for c in cur], [c['waste'] for c in cur], col, 1.2, '5,3', 'waste, s=' + S)
    pl.axes('tilt theta (deg)', 'offset delta needed for contact (solid) / uncoverable corner area (dashed)', [0, 15, 30, 45], [0, 0.25, 0.5, 0.75, 1.0])
    pg.text(1, DR.wrap([
        "(A') WHAT IT IS: the k = 0 CONTACT curve: at side s the flat meeter's offset delta that makes R(theta, delta) = s - 2 (solid), for the "
        'tilts where TILT-MIN allows it (sin theta + 0.02 <= delta < 1); dashed: the uncoverable area of that crowd in its corner (A237\'s '
        'sandwich census in a side-6 box) -- the dichotomy: a low tilt needs delta near 1 (the corner strip is wasted), the least waste sits '
        'at the high-tilt end theta*.',
        'Read with (A): below 4 a two-per-wall ring in wall-to-wall contact exists at every s in (3, 4) along this curve; what it cannot '
        'do is balance (page 3, D).  %.2f s.' % (time.time() - t0)]))
    for k, r, tag in ((2, B, 'B'), (3, C, 'C')):
        pg.text(k, DR.wrap(ring_panel(pg, k, r, tag,
                "A226's crowd ring at S = %.2f, eps = 0.02 (one_flush.md s.3.4): at each corner the flush corner square lifted eps up its wall "
                "(flat, orange) and its neighbour tilted eps/2 = 0.57 deg hovering eps/4 above the wall with a vertex poked under it; a RATTLER "
                "crowd: the only contacts are the four flat squares' walls, no square touches another." % r['S'])))
    return pg.write(os.path.join(PAGES, 'rings_reach.svg'))


def page_gear(rings, click):
    D = [r for r in rings if r['label'].startswith('contact_S3.950')][0]
    J = [r for r in rings if r['label'] == 'jut_S3.95_th10_phi45'][0]
    pg = DR.page("A239 -- the gear lemma on rings below 4: (D) the wall-to-wall contact ring at S = 3.95 (k = 0, theta* = %.1f deg), "
                 "(D') the jutting third member (k = 1) and the pocket it kills, (E) corner swap + shrink of the S = 3.90 ring, (E') its flush end"
                 % D['theta'], 2, 2, 3.95, note_h=250)
    th = D['theta']
    gain = 1.0 / math.tan(math.radians(th))
    pg.text(0, DR.wrap(ring_panel(pg, 0, D, 'D',
            'the window ring (A237 family, eta = 0: real contacts) at S = 3.95 at the tilt theta* = %.2f deg where the reach closes: at every '
            'corner a flat meeter (offset delta = %.3f) and a tilted partner resting on its corner and on the wall; every wall spanned in '
            'CONTACT by one flat and one tilted meeter (k = 0).' % (th, D['delta'])) + [
            'GEAR LEMMA: the load enters a crowd along the flat meeter\'s wall and leaves along the other wall through the corner-on-edge '
            'contact at angle theta: F_out = cot(theta) F_in (rings_below_4.md s.3), so the loop gain is cot^4(theta*) = %.2f != 1 and NO '
            'force balance closes around the ring (torque-only infeasible); torque balance of a tilted meeter under its three contacts '
            'needs the partner\'s corner at cos^2 theta along its edge, i.e. delta = sin th + cos^3 th = %.3f > 1: impossible in the box.' % (gain ** 4, math.sin(math.radians(th)) + math.cos(math.radians(th)) ** 3),
            'What would move: with the PUSHes loaded and nothing from outside, every tilted meeter turns TOWARD alignment (Lemma W\'s sense, '
            'the red arcs are the anti-aligning torques it lacks) and every flat meeter slides along its wall AWAY from its corner (the red '
            'arrows are the corner-ward holders it lacks): the crowd settles -- the DRAIN.  An interior square could supply one holder only '
            'by touching a member; the pocket holds ONE square (grey), which can touch the tilted meeters (%s) but cannot hold four corners: '
            '8 + 1 = 9 < 11.' % [i for i, v in D['touchable'].items() if v['can']]]))
    jv = GM.BD.verts(tuple(J['poses'][8]))
    jt = [i for i, g in enumerate(J.get('jut_gaps', [])) if abs(g) <= 1e-7]
    pg.text(1, DR.wrap(ring_panel(pg, 1, J, "D'",
            'the JUTTING variant: the window ring at theta = %g deg (walls NOT in contact: floor gap %.3f < 1, the reach falls short of '
            's - 2), plus a third member M (blue, 45 deg) resting as low as it goes on the two tilted meeters beside the floor gap -- the '
            'k = 1 holder that closes the floor chain (contacts %s).' % (J['theta'], J['gap'], jt)) + [
            'The jut reaches y = %.2f > S/2: the pocket left is EMPTY -- the eroded free-centre region is empty in every 1-deg tilt bin '
            '(rigorous, A237\'s kernel sandwich), so no unit square fits and no second jut (the ceiling\'s 3 2 3 2 pattern) has room: this '
            'ring closes at 9 < 11.  With the PUSHes loaded the deficit is again anti-aligning torques on the tilted meeters and corner-ward '
            'holders on the flat ones (red); M supplies one holder pair and nothing can supply the rest.' % jv[:, 1].max()]))
    # (E) the swap + shrink, (E') the flush end
    sw = click['swaps']['BL']
    P0 = [tuple(p) for p in sw['shrink_poses']]
    s0 = sw['shrink_side']
    pg.frame(2, 3.90)
    pg.frame(2, s0)
    for i, p in enumerate(P0):
        pg.square(2, p, DR.ORANGE[0] if i < 7 else DR.BLUE[0], DR.ORANGE[1] if i < 7 else DR.BLUE[1], label=i, width=1.5)
    ok, gap, wall = pg.check_partial(P0, s0)
    seq = sw['move_sides']
    pg.text(2, DR.wrap([
        '(E) WHAT IT IS: the CLICK / SWAP on the S = 3.90 ring (A231\'s improvement): the ring + its one interior square is a 9-square '
        'packing; CORNER-SWAP at BL (ring_swap.md s.2.1): the two meeters out, the slot square in (blue, pinned), the leftover re-placed by '
        'the region search (Lemma SWAP: same side %.2f); then the SHRINK -- the fixed-tilt side LP of Lemma GRAIN-LP with the slot pinned, '
        'axes re-selected: side %.4f (inner frame; %d LP rounds, %.2f s).' % (3.90, s0, sw['lp_iters'], sw['secs']['shrink']),
        'The anchored move (the three remaining tilted squares rotate to alignment in 20 steps, LP at each): %s -> %.4f = the 3 x 3 grid '
        '(E\'); the plain click of the unswapped 9-ring reaches %.4f as well and the 8-ring %.4f: below 4 the crowd ring is a rattler '
        'structure whose side is set by nothing.  checks: packing %s (gap %.1e, wall %.1e); swap %.2f s, move %.2f s.'
        % (' '.join('%.3f' % v for v in seq[::5]), seq[-1], click['click9']['sides'][-1], click['click8']['sides'][-1], ok, gap, wall,
           sw['secs']['swap'], sw['secs']['move'])]))
    Pe = [tuple(p) for p in sw['move_end']]
    se = seq[-1]
    pg.frame(3, se)
    for i, p in enumerate(Pe):
        pg.square(3, p, DR.ORANGE[0] if i < 7 else DR.BLUE[0], DR.ORANGE[1] if i < 7 else DR.BLUE[1], label=i, width=1.5)
    ok, gap, wall = pg.check_partial(Pe, se)
    pg.text(3, DR.wrap([
        "(E') WHAT IT IS: the end of the anchored move: every square flat, the slot square still pinned at BL, side %.4f -- the trivial "
        '3 x 3 packing of the 9 squares (Lemma FLUSH: a flush packing of 9 needs side >= 3, attained).  For 11 squares the same ring has no '
        'room for the missing three (capacity 1), which is why no 11-square four-crowd below 4 exists to click (A217: the lowest is 4.0014).'
        % se,
        'checks: packing %s (min pair gap %.1e, min wall %.1e).' % (ok, gap, wall)]))
    return pg.write(os.path.join(PAGES, 'rings_gear.svg'))


if __name__ == '__main__':
    os.makedirs(PAGES, exist_ok=True)
    rings, reach, click = load(RINGS), load(REACH), load(CLICK)[0]
    print(page239a.page())
    print(page_reach(rings, reach))
    print(page_gear(rings, click))
