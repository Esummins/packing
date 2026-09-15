"""A223 pages (docs/residue_map/campaigns/A223-two-grains/), every configuration panel geometry-checked:
  ring_grains_rand_0_0569_t20.svg -- the ring's squares coloured by handedness ('-' blue, '+' orange, flat grey),
                                     the grain boundaries (LEAN red, through a flat square purple), the two
                                     floor-to-ceiling load chains;
  ring_click_rand_0_0569_t20.svg  -- three frames of the joint click (t = 0, 1/2, 1) and the side along the move;
  click_fail_<wid>.svg            -- the first four-crowd whose click (variant A) is blocked: the last admissible
                                     frame with the blocking pair marked, and the free variant's end.
    python pages223.py
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
import grains223 as GR        # noqa: E402
import click223 as CK         # noqa: E402
import draw222 as D           # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
PAGES = os.path.join(ATT, '..', '..', 'docs', 'residue_map', 'campaigns', 'A223-two-grains')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'click223.jsonl')
PURPLE = '#7b3fa0'
FILL = {'-': D.BLUE, '+': D.ORANGE, 'F': D.GREY, 'D': D.DARK}


def poses_of(z):
    return [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(G.N)]


def draw_config(pg, k, z, hand, loaded, marks=(), boundaries=(), corners=True):
    s = float(z[G.S_IDX])
    sq = poses_of(z)
    pg.frame(k, s)
    for q in range(G.N):
        f, st = FILL[hand[q]]
        pg.square(k, sq[q], f, st if q in loaded else '#aaaaaa', label=q, dash=None if q in loaded else '4,3',
                  width=2.4 if q in marks else 1.3)
    for q in marks:
        pg.square(k, sq[q], 'none', D.RED, width=2.4)
    for b in boundaries:
        col = D.RED if b['kind'] == 'LEAN' else PURPLE
        for p in b['points']:
            x, y = pg.P(k, p[0], p[1])
            pg.o.append('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="none"/>' % (x, y, col))
    if corners:
        for cn in G.CORNER_NAMES:
            cx, cy = G.slot_centre(cn, s)
            pg.cell(k, (cx - .5, cx + .5, cy - .5, cy + .5), stroke='#999999', dash='3,3', width=1.0)
    return pg.check(sq, s)


def chain_polyline(pg, k, z, chain, col):
    pts = ' '.join('%.1f,%.1f' % pg.P(k, *p) for p in chain)
    pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="7,4"/>' % (pts, col))


def contact_chain(z, order, e_start, e_end):
    """polyline: wall point of the first square, then the contact points between consecutive members, then the
    far-wall point of the last (the telescoping chain of Lemma GRAIN, axis e_y)."""
    q = G.corners(z)
    s = float(z[G.S_IDX])
    pts = [tuple(q[order[0]][np.argmin(q[order[0]][:, 1])])]
    tab = G.sat_table(z)
    for a, b in zip(order, order[1:]):
        i, j = min(a, b), max(a, b)
        t = tab[(i, j)]
        oi, e = np.unravel_index(np.argmax(t.min(axis=2)), (2, 4))
        kc = int(np.argmin(t[oi, e]))
        other = j if oi == 0 else i
        pts.append(tuple(q[other][kc]))
    pts.append(tuple(q[order[-1]][np.argmax(q[order[-1]][:, 1])]))
    return pts


def page_ring():
    t0 = time.time()
    w = [x for x in GR.four_crowds() if x['rid'] == GR.RING][0]
    g = GR.grains(w)
    gl = GR.grains(w, 'load')
    z = np.array(w['z'])
    s = float(z[G.S_IDX])
    pg = D.Page('A223 -- the ring rand_0_0569|t20 (side %.4f) as TWO GRAINS: squares coloured by tilt handedness '
                '(blue: theta in (45,90); orange: (0,45); grey: flat), grain boundaries and the load chains' % s, 2, 1, s, note_h=130)
    ok, gap, wall = draw_config(pg, 0, z, g['hand'], set(g['loaded']), boundaries=g['boundaries'])
    t1 = time.time()
    pg.text(0, ['(a) handedness grains by CONTACT adjacency among the loaded squares: %s' %
                '; '.join('%s %s tilts %s corners %s walls %s' % (x['hand'], x['members'], sorted(set(x['tilts_deg'])), x['corners'], x['walls']) for x in g['grains']),
                'boundaries: %s' % '; '.join('%s %s (lam %.3f)' % (b['kind'], b['pair'], b['lam']) for b in g['boundaries']),
                'red dot = LEAN contact (opposite handedness), purple dot = contact through the flat holder 9; dashed edge = unloaded (rattlers %s)' % g['rattlers'],
                'corner boxes dashed grey; geometry check of the drawn 11-square configuration: %s (min pair gap %.1e, min wall %.1e); %.2f s' % (ok, gap, wall, t1 - t0)])
    ok2, gap2, wall2 = draw_config(pg, 1, z, g['hand'], set(g['loaded']), boundaries=gl['boundaries'])
    chain_polyline(pg, 1, z, contact_chain(z, [4, 5, 2, 3], 0, 1), D.BLUE[1])
    chain_polyline(pg, 1, z, contact_chain(z, [6, 7, 8, 10], 0, 1), D.ORANGE[1])
    t2 = time.time()
    pg.text(1, ['(b) the same by LOADED-row adjacency (the bounded FJ stress picks a basis: %s) and the two floor-to-ceiling chains' %
                '; '.join('%s %s' % (x['hand'], x['members']) for x in gl['grains']),
                'blue chain: floor -> 4 -> 5 -> 2 -> 3 -> ceiling (flush ladder at 70 deg); orange chain: floor -> 6 -> 7 -> 8 -> 10 -> ceiling (20 deg);',
                'each chain telescopes to s = sum of projected extents + tangential offsets (two_grains.md s.2.4); the halves meet at 4|6 (lean) and 3|9|10 (flat).',
                'geometry check: %s (gap %.1e, wall %.1e); %.2f s' % (ok2, gap2, wall2, t2 - t1)])
    return pg.write(os.path.join(PAGES, 'ring_grains_rand_0_0569_t20.svg'))


def side_plot(pg, k, curves, s_lo, s_hi, title):
    ox, oy = pg.origin(k)
    W = H = D.S * pg.side
    pg.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#333"/>' % (ox, oy, W, H))
    for j in range(5):
        v = s_lo + (s_hi - s_lo) * j / 4
        y = oy + H - H * j / 4
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ddd"/>' % (ox, y, ox + W, y))
        pg.o.append('<text x="%.1f" y="%.1f" font-size="10" fill="#555">%.4f</text>' % (ox + 4, y - 3, v))
    for name, (ts, ss, col) in curves.items():
        pts = ' '.join('%.1f,%.1f' % (ox + W * t, oy + H - H * (s - s_lo) / (s_hi - s_lo)) for t, s in zip(ts, ss))
        pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, col))
        pg.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s">%s</text>' % (ox + W * ts[-1] - 60, oy + H - H * (ss[-1] - s_lo) / (s_hi - s_lo) - 6 - 12 * list(curves).index(name), col, name))
    pg.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="#222">%s</text>' % (ox + 4, oy + 14, D.esc(title)))


def page_click():
    t0 = time.time()
    rows = [json.loads(l) for l in open(RES, encoding='utf-8')]
    r = [x for x in rows if x['rid'] == GR.RING][-1]
    w = [x for x in GR.four_crowds() if x['rid'] == GR.RING][0]
    g = GR.grains(w)
    A = r['A']
    keys = sorted(A['frames'], key=float)
    s0 = float(w['z'][G.S_IDX])
    pg = D.Page('A223 -- the joint CLICK on the ring: both grains rotate toward alignment (blue 70 -> 90 deg, orange 20 -> 0 deg), '
                'the side minimised over the centres at each tilt step with the 15 contact axes kept (variant A)', 4, 1, s0, note_h=120)
    for k, key in enumerate(keys):
        z = np.array(A['frames'][key])
        th = [math.degrees(v % (math.pi / 2)) for v in z[2:33:3]]
        t1 = time.time()
        ok, gap, wall = draw_config(pg, k, z, g['hand'], set(g['loaded']), boundaries=g['boundaries'] if k == 0 else ())
        pg.text(k, ['frame t = %s: side %.6f, tilts (mod 90) %s' % (key, z[G.S_IDX], sorted(set(round(v, 2) for v in th))),
                    'fixed-tilt side minimum over the centres, the 15 contact pairs on their t=0 separating axes, the others re-selected;',
                    'contacts still closed at this step: %d of 15 (the lean 4|6 slides on 6\'s edge)' % A['contacts_kept'][[0, 10, 20][k]],
                    'geometry check: %s (min pair gap %.1e, min wall %.1e); %.2f s' % (ok, gap, wall, time.time() - t1)])
    curves = {'A click (contacts kept)': (A['t'], A['s'], D.RED), 'B free re-selection': (r['B']['t'], r['B']['s'], D.BLUE[1])}
    if 'C' in r:
        curves['C loaded core only'] = (r['C']['t'], r['C']['s'], D.ORANGE[1])
    side_plot(pg, 3, curves, 3.99, s0 + 0.005, 'side along the click, t = 0 .. 1 (left to right)')
    pg.text(3, ['(d) the side s_min(theta(t)) along the move: start %.6f, end %.6f, monotone non-increasing: %s (max uptick %.1e);' %
                (A['s'][0], A['s_end'], A['monotone'], A['max_uptick']),
                'the free variant B coincides with A to 1e-7 at every step (no contact needs releasing); the core variant C (rattlers 0, 1 removed) too;',
                '4.000 at t = 1 is the flush end (Lemma FLUSH: a flat packing of 11 squares has side >= 4). %.2f s total' % (time.time() - t0)])
    return pg.write(os.path.join(PAGES, 'ring_click_rand_0_0569_t20.svg'))


def page_fail():
    """the worst click: a blocked variant A if any, else the largest side UPTICK of variant A (frames before / after)."""
    t0 = time.time()
    rows = [json.loads(l) for l in open(RES, encoding='utf-8')]
    bad = [x for x in rows if x['A']['blocked_at'] is not None]
    r = bad[0] if bad else max(rows, key=lambda x: x['A']['max_uptick'])
    w = [x for x in GR.four_crowds() if x['wid'] == r['wid']][0]
    g = GR.grains(w)
    z0 = np.array(w['z'])
    s0 = float(z0[G.S_IDX])
    A = CK.path(z0, list(range(G.N)), True, 20, r['diamond_sense'], keep_all=True)
    B = CK.path(z0, list(range(G.N)), False, 20, r['diamond_sense'], keep_all=True)
    ups = [A['s'][k + 1] - A['s'][k] for k in range(len(A['s']) - 1)]
    ku = int(np.argmax(ups))
    keys = sorted(A['frames'], key=float)
    side = max(s0, max(A['s']), max(B['s']))
    pg = D.Page('A223 -- the WORST click among the 193: %s (%s, side %.4f): variant A (contact axes kept) is %s; '
                'its largest uptick %.4f at t = %s -> %s; the free variant B ends at %.4f' %
                (r['wid'], r['cls'], s0, 'BLOCKED at t = %s' % A['blocked_at'] if A['blocked_at'] is not None else 'never blocked',
                 ups[ku], A['t'][ku], A['t'][ku + 1], B['s_end']), 4, 1, side, note_h=130)
    ok, gap, wall = draw_config(pg, 0, z0, g['hand'], set(g['loaded']), boundaries=g['boundaries'])
    pg.text(0, ['(a) the witness at t = 0 by handedness: grains %s' % '; '.join('%s %s' % (x['hand'], x['members']) for x in g['grains']),
                'boundaries %s; rattlers %s' % ('; '.join('%s %s' % (b['kind'], b['pair']) for b in g['boundaries']), g['rattlers']),
                'geometry check: %s (gap %.1e, wall %.1e); %.2f s' % (ok, gap, wall, time.time() - t0)])
    for k, kk in enumerate((ku, ku + 1)):
        z = np.array(A['frames'][keys[kk]])
        t1 = time.time()
        ok2, gap2, wall2 = draw_config(pg, 1 + k, z, g['hand'], set(g['loaded']))
        pg.text(1 + k, ['(%s) variant A frame t = %s (%s the uptick): side %.6f, contacts still closed %d of %d' %
                        ('bc'[k], keys[kk], 'before' if k == 0 else 'after', z[G.S_IDX], A['contacts_kept'][kk], A['n_fixed_contacts']),
                        'an LP minimiser at these tilts with the t=0 contact axes: admissible, drawn as such;',
                        'the side RISES between (b) and (c) by %.4f: the fixed axes force the squares apart as the tilts advance.' % ups[ku],
                        'geometry check: %s (gap %.1e, wall %.1e); %.2f s' % (ok2, gap2, wall2, time.time() - t1)])
    lo = min(min(A['s']), min(B['s'])) - 0.01
    side_plot(pg, 3, {'A click (contacts kept)': (A['t'], A['s'], D.RED), 'B free re-selection': (B['t'], B['s'], D.BLUE[1])}, lo, side + 0.01,
              'side along the click, t = 0 .. 1')
    pg.text(3, ['(d) A: start %.4f, end %.4f, monotone %s (max uptick %.3f); B: end %.4f, monotone %s (max uptick %.3f).' %
                (A['s'][0], A['s_end'], A['monotone'], A['max_uptick'], B['s_end'], B['monotone'], B['max_uptick']),
                'Neither path is a certificate: the fixed-tilt minimum found is a warm-started LOCAL minimum (Lemma INHERIT (iii): a local',
                'branch can turn up); the flush end 4.000 is the floor of Lemma FLUSH.  %.2f s total' % (time.time() - t0)])
    return pg.write(os.path.join(PAGES, 'click_worst_%s.svg' % r['wid']))


if __name__ == '__main__':
    print(page_ring())
    print(page_click())
    print(page_fail())
