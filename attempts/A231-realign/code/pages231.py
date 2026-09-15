"""A231 pages (docs/residue_map/campaigns/A231-realign/), every configuration panel geometry-checked (n-general
SAT + walls, the result printed in the panel's note):
  ring_realign_rand_0_0569_t20.svg  -- the ring: the four-crowd, after the corner swap, after the SHRINK (S pinned),
                                       the anchored path's minimum and its flush end, the side along the path;
  realign_worst_<wid>.svg           -- the compA path with the largest uptick (or a blocked one): start / min / end;
  crowd_above_realign_n26.svg       -- A226's n = 26 crowd: the crowd, the retraction swap at BL, the shrink.
    python pages231.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
import geomn231 as GN         # noqa: E402
import inputs231 as IN        # noqa: E402
import draw222 as D           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
PAGES = os.path.join(ATT, '..', '..', 'docs', 'residue_map', 'campaigns', 'A231-realign')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'realign231.jsonl')
FILL = {'-': D.BLUE, '+': D.ORANGE, 'F': D.GREY, 'D': D.DARK}


def rows():
    seen, out = set(), []
    for l in open(RES, encoding='utf-8'):
        r = json.loads(l)
        if r['key'] not in seen:
            seen.add(r['key']); out.append(r)
    return out


def draw(pg, k, poses, s, marks=(), G=(), S=None, corner=None):
    pg.frame(k, s)
    for i, p in enumerate(poses):
        h = GN.handedness(p[2])
        f, st = FILL[h]
        pg.square(k, p, f, st, label=i, width=2.4 if i in G else 1.2, dash='4,3' if (i in marks) else None)
    if S is not None:
        pg.square(k, poses[S], 'none', D.RED, width=2.6)
    if corner:
        ax, bx, ay, by = GN.slot_pin(corner)
        cx, cy = ax + bx * s, ay + by * s
        pg.cell(k, (cx - .5, cx + .5, cy - .5, cy + .5), stroke='#999999', dash='3,3', width=1.0)
    ok, gap, wall = pg.check_partial(poses, s)
    return 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)


def side_plot(pg, k, curves, s_lo, s_hi, title):
    ox, oy = pg.origin(k)
    W = H = D.S * pg.side
    pg.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#333"/>' % (ox, oy, W, H))
    for j in range(5):
        v = s_lo + (s_hi - s_lo) * j / 4
        y = oy + H - H * j / 4
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ddd"/>' % (ox, y, ox + W, y))
        pg.o.append('<text x="%.1f" y="%.1f" font-size="10" fill="#555">%.4f</text>' % (ox + 4, y - 3, v))
    for j, (name, (ts, ss, col)) in enumerate(curves.items()):
        pts = ' '.join('%.1f,%.1f' % (ox + W * t, oy + H - H * (v - s_lo) / (s_hi - s_lo)) for t, v in zip(ts, ss))
        pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (pts, col))
        pg.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="%s">%s</text>' % (ox + 6, oy + 28 + 13 * j, col, D.esc(name)))
    pg.o.append('<text x="%.1f" y="%.1f" font-size="11" fill="#222">%s</text>' % (ox + 4, oy + 14, D.esc(title)))


def case_of(r):
    src = {'193': IN.cases_193, 'win40': IN.cases_win40, 'a226': IN.cases_a226}[r['src']]
    for k in src() if r['src'] != 'win40' else IN.cases_win40({c['rid'] for c in IN.cases_193()}):
        if IN.key_of(k) == r['key']:
            return k
    raise KeyError(r['key'])


def page_path(r, fname, title):
    k = case_of(r)
    p = r['paths'].get('compA') or {}
    fr = p.get('frames', {})
    keys = [x for x in ('0.0', str(p.get('t_min')), '1.0') if x in fr]
    keys = list(dict.fromkeys(keys))
    n = 2 + len(keys) + 1
    pg = D.Page(title, n, 1, r['s0'], note_h=135)
    pg.text(0, [draw(pg, 0, k['poses0'], r['s0'], corner=r['corner']),
                '(a) the four-crowd at side %.5f; corner %s: meeters %s' % (r['s0'], r['corner'], GN.corner_meeters(k['poses0'], r['s0'], r['corner']))])
    pg.text(1, [draw(pg, 1, k['poses'], r['s0'], S=r['S'], corner=r['corner']),
                '(b) after the CORNER-SWAP (%s): S = %d settled (red), leftover L = %d; a packing at the same side (Lemma SWAP)' % (r['swap'][:40], r['S'], r['L'])])
    for j, key in enumerate(keys):
        z = fr[key]
        s = p['s'][p['t'].index(float(key))]
        G = p['members']
        note = draw(pg, 2 + j, z, s, G=G, S=r['S'], corner=r['corner'])
        tag = {'0.0': 'the SHRINK (fixed tilts, S pinned, side minimised over the centres)', '1.0': 'the anchored move at t = 1 (G flush)'}.get(key, 'the path minimum at t = %s' % key)
        pg.text(2 + j, [note, '(%s) %s: side %.6f; G = %s (thick) tilts %s deg' % (
            'cde'[j], tag, s, G, sorted({round(GN.phi_deg(z[i][2]), 2) for i in G}))])
    curves = {}
    for name, col in (('compA', D.RED), ('compB', D.BLUE[1]), ('allA', D.ORANGE[1])):
        q = r['paths'].get(name, {})
        if q.get('s'):
            curves[name + ' (%s, %s)' % (q['horn'], q['endpoint'])] = (q['t'], q['s'], col)
    if curves:
        lo = min(min(c[1]) for c in curves.values()) - 0.003
        side_plot(pg, n - 1, curves, lo, r['s0'] + 0.003, 'side along the anchored move, t = 0 .. 1; s0 = %.5f (top)' % r['s0'])
    pg.text(n - 1, ['(%s) the side along the paths; horn = sign of the first step, endpoint = where the minimum sits' % 'cdefg'[len(keys)]])
    return pg.write(os.path.join(PAGES, fname))


def page_a226(rs):
    r = [x for x in rs if x['src'] == 'a226' and x['status'] == 'ok' and x['corner'] == 'BL' and x['n'] == 26][0]
    k = case_of(r)
    p0, s = k['poses0'], r['s0']
    p1 = k['poses']
    th = np.array([q[2] for q in p1])
    p2, s2, _, _ = GN.fixed_tilt_min(p1, th, {}, {r['S']: 'BL'})
    pg = D.Page('A231 -- CROWD-ABOVE at n = 26 (A226, side %.6f < 6): the retraction swap at BL and the shrink' % s, 3, 1, s, note_h=110)
    pg.text(0, [draw(pg, 0, p0, s), '(a) the crowd: every corner box met by a lifted corner square and a tilted neighbour (tilt eps/2)'])
    pg.text(1, [draw(pg, 1, p1, s, S=r['S'], corner='BL'), '(b) after the retraction at BL: the slot square (red) + the flush neighbour, same side'])
    pg.text(2, [draw(pg, 2, p2, s2, S=r['S'], corner='BL'), '(c) the SHRINK at fixed tilts with S pinned: side %.6f (record s(26) = 5.621320; the other three crowds still tilted eps/2)' % s2])
    return pg.write(os.path.join(PAGES, 'crowd_above_realign_n26.svg'))


def main():
    rs = rows()
    ring = [r for r in rs if r['rid'] == 'rand_0_0569|t20' and r['status'] == 'ok']
    best = min(ring, key=lambda r: (r['paths'].get('compA', {}).get('s_min') or r['s_lp0']))
    print(page_path(best, 'ring_realign_rand_0_0569_t20.svg',
                    'A231 -- the ring rand_0_0569|t20: corner swap at %s, shrink with S pinned, the anchored re-alignment of the grain touching S' % best['corner']))
    ok = [r for r in rs if r['src'] == '193' and r['status'] == 'ok' and r['paths'].get('compA', {}).get('s')]
    worst = max(ok, key=lambda r: (r['paths']['compA']['blocked_at'] is not None, r['paths']['compA']['max_uptick']))
    print(page_path(worst, 'realign_worst_%s.svg' % worst['wid'],
                    'A231 -- the worst anchored path (compA): %s, corner %s (uptick %.3f, %s)' % (
                        worst['wid'], worst['corner'], worst['paths']['compA']['max_uptick'], worst['paths']['compA']['endpoint'])))
    print(page_a226(rs))


if __name__ == '__main__':
    main()
