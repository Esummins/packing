"""A234 pages (docs/residue_map/campaigns/A234-handedness/), every panel geometry-checked (pairwise SAT gaps and wall
rows >= -1e-6, printed in the panel's note):
  wall_pressure_chi.svg    -- the ring, Trump, S07, S02: squares coloured by handedness chi ('+' orange, '-' blue, flat
                              grey, 45-deg hatched), the wall forces of the FJ stress drawn as arrows at their contact
                              points (length = force), each wall labelled with its pressure P and moment M_c, the note
                              carrying TORQUE-ID (sum tau^wall = -C) and the handedness sum S = sum chi W d.
  perimeter_handedness.svg -- the perimeter handedness map: the loaded wall-touchers as bars outside the wall (height
                              = W, colour = chi) for the four packings above and four four-crowd witnesses; the flip
                              count and the per-wall handedness mix in the note.
    python pages234.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stress234 as S          # noqa: E402  (puts A217's geom217 on the path for draw222)
import hand234 as H            # noqa: E402
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
import draw222 as D            # noqa: E402

PAGES = os.path.join(S.ROOT, 'docs', 'residue_map', 'campaigns', 'A234-handedness')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(S.ATT, 'results', 'hand234.jsonl')
RING = 'w364_held'
FILL = {'-': D.BLUE, '+': D.ORANGE, 'F': D.GREY, 'D': D.DARK}
CHI_COL = {1: '#b06a00', -1: '#1f4e79', 0: '#888888'}
NW = {'x=0': (1, 0), 'y=0': (0, 1), 'x=s': (-1, 0), 'y=s': (0, -1)}
ARROW = 0.9                    # units of length per unit force


def a217_witness(wid):
    for l in open(S.WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['wid'] == wid:
            return S.from_w217(w)
    raise KeyError(wid)


def poses_of(z):
    n = (len(z) - 1) // 3
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(n)], float(z[-1])


def base_panel(pg, k, w, rec):
    poses, s = poses_of(w['z'])
    pg.frame(k, s)
    meet = {i for v in rec['meeters'].values() for i in v}
    for i, p in enumerate(poses):
        f, st = FILL[H.handed(p[2])[1]]
        pg.square(k, p, f, st, label=i, width=1.2)
    for i in meet:
        pg.square(k, poses[i], 'none', D.RED, width=2.6)
    ok, gap, wall = pg.check(poses, s) if len(poses) == 11 else pg.check_partial(poses, s)
    return poses, s, 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)


def arrow(pg, k, a, b, col='#222', width=1.6):
    x0, y0 = pg.P(k, *a)
    x1, y1 = pg.P(k, *b)
    pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>' % (x0, y0, x1, y1, col, width))
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    hx, hy = x1 - 7 * ux, y1 - 7 * uy
    pg.o.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>' % (x1, y1, hx - 3.5 * uy, hy + 3.5 * ux, hx + 3.5 * uy, hy - 3.5 * ux, col))


def label(pg, k, x, y, txt, col='#222', size=10, anchor='middle'):
    px, py = pg.P(k, x, y)
    pg.o.append('<text x="%.1f" y="%.1f" font-size="%d" text-anchor="%s" fill="%s">%s</text>' % (px, py, size, anchor, col, D.esc(txt)))


def page_pressure(recs):
    ws = [(RING, a217_witness(RING)), ('trump', S.trump()), ('s07', S.s07()), ('s02', S.s02())]
    side = max(w['z'][-1] for _, w in ws)
    pg = D.Page('A234 -- wall pressure and handedness at an FJ stress: the ring (four-crowd, held by tilt bounds), Trump, S07, S02.  '
                'Fill = chi (+ orange, - blue, flat grey, 45 hatched); red = corner meeters; arrows = wall forces at their contact points; '
                'TORQUE-ID: sum tau^wall + C = 0', 4, 1, side, note_h=150)
    for k, (name, w) in enumerate(ws):
        rec = recs[name]
        poses, s, note = base_panel(pg, k, w, rec)
        q = S.verts(w['z'])
        for r_, lam in zip(w['rows'], w['lam']):
            if r_['kind'] == 'wall' and lam > 1e-7:
                p = q[r_['i'], r_['corner']]
                n = np.array(NW[r_['wall']], float)
                arrow(pg, k, p, p + ARROW * lam * n, col=CHI_COL[H.handed(poses[r_['i']][2])[0]])
        for wn, (x, y, anc) in {'y=0': (s / 2, -0.22, 'middle'), 'y=s': (s / 2, s + 0.12, 'middle'),
                                'x=0': (-0.05, s / 2, 'end'), 'x=s': (s + 0.05, s / 2, 'start')}.items():
            wd = rec['walls'][wn]
            label(pg, k, x, y, 'P %.2f M %.3f' % (wd['P'], wd['M_c']), size=9, anchor=anc)
        ti, c = rec['torque_id'], rec['cand_c']
        pg.text(k, [note,
                    '(%s) %s, side %.4f, doubly-met corners %d, external load %.3f' % ('abcd'[k], name, s, rec['n2'], rec['ext_load']),
                    'sum tau^wall = %.4f = -C (C = %.4f, residual %.0e); S = sum chi W d over tilted = %.4f, flat squares\' tau = %.4f' % (
                        ti['sum_tau_wall'], ti['C'], ti['residual'], c['S_tilted'], c['F_flat']),
                    'polytope ranges: S %s, C %s' % ([round(v, 3) for v in rec['ranges']['S_tilted']], [round(v, 3) for v in rec['ranges']['C']]),
                    'per wall load + / -: ' + ', '.join('%s %.2f/%.2f' % (wn, rec['walls'][wn]['mix']['+'], rec['walls'][wn]['mix']['-']) for wn in ('y=0', 'x=s', 'y=s', 'x=0')),
                    'flips around the perimeter: %d (tilted loaded touchers %d)' % (rec['cand_a']['flips'], rec['cand_a']['n_tilted_touchers'])])
    return pg.write(os.path.join(PAGES, 'wall_pressure_chi.svg'))


def bars(pg, k, rec, s):
    """the loaded wall-touchers as bars outside each wall: height 25 px per unit force, colour chi."""
    for wn, wd in rec['walls'].items():
        for e in wd['touchers']:
            t, h = e['t'], 25 * e['W']
            if wn == 'y=0':
                x0, y0 = pg.P(k, t, 0)
                box = (x0 - 3, y0, 6, h)
            elif wn == 'x=s':
                x0, y0 = pg.P(k, s, t - s)
                box = (x0, y0 - 3, h, 6)
            elif wn == 'y=s':
                x0, y0 = pg.P(k, 3 * s - t, s)
                box = (x0 - 3, y0 - h, 6, h)
            else:
                x0, y0 = pg.P(k, 0, 4 * s - t)
                box = (x0 - h, y0 - 3, h, 6)
            pg.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.85"/>' % (box + (CHI_COL[e['chi']],)))


def page_perimeter(recs, four):
    ws = [(RING, a217_witness(RING)), ('trump', S.trump()), ('s07', S.s07()), ('s02', S.s02())] + [(n, a217_witness(n)) for n in four]
    side = max(w['z'][-1] for _, w in ws)
    pg = D.Page('A234 -- the perimeter handedness map: every loaded wall-toucher as a bar outside its wall (length = wall force W, '
                'colour = chi: + orange, - blue, flat/45 grey).  Top: the ring, Trump, S07, S02; bottom: four four-crowd witnesses '
                '(bars of both colours on one wall = a mixed wall)', 4, 2, side, note_h=120)
    for k, (name, w) in enumerate(ws):
        rec = recs[name]
        poses, s, note = base_panel(pg, k, w, rec)
        bars(pg, k, rec, s)
        a = rec['cand_a']
        pg.text(k, [note,
                    '(%s) %s (%s), side %.4f, doubly-met corners %d, external load %.3f' % ('abcdefgh'[k], name, rec['cls'], s, rec['n2'], rec['ext_load']),
                    'perimeter sequence of chi (floor, right, ceiling, left): %s; flips %d; walls carrying both signs %d' % (
                        ''.join('+' if e[1] > 0 else '-' for e in a['seq']) or '(none)', a['flips'], a['mixed_walls']),
                    'load on + %.3f, on - %.3f; S = %.4f, C = %.4f, flat tau = %.4f' % (a['plus_load'], a['minus_load'], rec['S_tilted'],
                                                                                      rec['torque_id']['C'], rec['F_flat'])])
    return pg.write(os.path.join(PAGES, 'perimeter_handedness.svg'))


def main():
    S.set_priority()
    recs = {}
    for l in open(RES, encoding='utf-8'):
        r = json.loads(l)
        if r['has_stress']:
            recs[r['name']] = r
    four = [r for r in recs.values() if r['four_crowd']]
    pick = []
    for want in ((lambda r: r['cand_a']['flips'] == 0 and r['cand_a']['n_tilted_touchers'] >= 4),
                 (lambda r: r['cand_a']['mixed_walls'] >= 3),
                 (lambda r: r['cls'] == 'HELD'),
                 (lambda r: r['cand_a']['flips'] >= 4)):
        for r in sorted(four, key=lambda r: -r['cand_a']['n_tilted_touchers']):
            if want(r) and r['name'] not in pick and r['name'] != RING:
                pick.append(r['name'])
                break
    while len(pick) < 4:
        pick.append([r['name'] for r in four if r['name'] not in pick and r['name'] != RING][0])
    print(page_pressure(recs))
    print(page_perimeter(recs, pick))


if __name__ == '__main__':
    main()
