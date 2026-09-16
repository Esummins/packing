"""A240 pages (docs/residue_map/campaigns/A240-cross/); every configuration panel geometry-checked (pairwise SAT gaps
and wall rows >= -1e-6, the result printed in the panel's note).
  cross_ring_x.svg    -- (a) the PI's X on the ring: sectors C/W/C/W vs the ring's actual grains (left half '-', right
                         half '+'), every corner pair same-handed and held by a tilt bound; (b) the ring's loaded
                         left-right and floor-ceiling chains and their shared square 6 (tilted, a meeter, no external
                         load); (c) a CROWD four-crowd whose crossing squares are tilted interior squares with no
                         external load; (d) Trump: the chains cross at the FLUSH square 3.
  oppose_corners.svg  -- Lemma OPPOSE's test, four corner arms in their frames: a locked same-handed flush pair (HELD),
                         a locked same-handed VE pair at a free FJ point, a locked opposite-handed pair (HELD), Trump TL.
  wall_grains.svg     -- the wall grains of three four-crowds (mixed wall / one-handed / the alternation never occurs).
    python pages240.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A234-handedness', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import draw222 as D            # noqa: E402
import geom217 as G            # noqa: E402
import stress234 as S          # noqa: E402
import cross240 as X           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A240-cross')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'cross240.jsonl')
RING = 'w364_held'
FILL = {'-': D.BLUE, '+': D.ORANGE, 'F': D.GREY, 'D': D.DARK}
CHAIN_COL = {'LR': '#d62728', 'TB': '#2ca02c'}


def poses_of(z):
    n = (len(z) - 1) // 3
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(n)], float(z[-1])


def frame_poses(poses, cn, s):
    M, t, det = G.corner_frame(cn, s)
    return [tuple(M @ np.array(p[:2]) + t) + (det * p[2],) for p in poses]


def load_witnesses(names):
    out = {}
    pool = [S.trump()] + S.a217_witnesses()
    if any(n.startswith('fj_') for n in names):
        pool += S.genuine_fj()
    for w in pool:
        if w['name'] in names:
            out[w['name']] = w
    return out


def draw_config(pg, k, poses, s, thick=(), hatch=(), labels=True):
    pg.frame(k, s)
    for i, p in enumerate(poses):
        f, st = FILL[X.handed(p[2] % (math.pi / 2))[1]]
        pg.square(k, p, f, st, label=i if labels else None, width=2.6 if i in thick else 1.2)
    for i in hatch:
        pg.square(k, poses[i], 'url(#hatch)', '#000', width=2.2)
    ok, gap, wall = pg.check_partial(poses, s)
    return 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)


def draw_chain(pg, k, poses, path, col):
    if not path:
        return
    pts = ' '.join('%.1f,%.1f' % pg.P(k, poses[i][0], poses[i][1]) for i in path)
    pg.o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4" stroke-opacity="0.75"/>' % (pts, col))


def draw_x(pg, k, s):
    for (a, b) in (((0, 0), (s, s)), ((0, s), (s, 0))):
        (x0, y0), (x1, y1) = pg.P(k, *a), pg.P(k, *b)
        pg.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555" stroke-width="1.5" stroke-dasharray="6,4"/>' % (x0, y0, x1, y1))
    for lab, (x, y) in (('C', (0.35, s / 2)), ('C', (s - 0.35, s / 2)), ('W', (s / 2, 0.35)), ('W', (s / 2, s - 0.35))):
        px, py = pg.P(k, x, y)
        pg.o.append('<text x="%.1f" y="%.1f" font-size="22" font-weight="bold" text-anchor="middle" fill="#555" fill-opacity="0.8">%s</text>' % (px, py + 8, lab))


def page_cross(recs, ws):
    ring, tr = recs[RING], recs['trump']
    crowd_name = [r['name'] for r in recs.values() if r.get('n2') == 4 and r['chains']['shared_desc'] and
                  all(d['ext_load'] <= 1e-7 and d['h'] in '+-' and not d['meeter_of'] for d in r['chains']['shared_desc'])]
    crowd_name = crowd_name[0] if crowd_name else 'w037_crowd'
    cr = recs[crowd_name]
    side = max(ring['s'], tr['s'], cr['s'])
    pg = D.Page('A240 -- the PI\'s X made exact: sectors vs the ring\'s grains (a); the ring\'s bracing chains cross at the tilted meeter 6 (b); '
                'a four-crowd whose chains cross at tilted interior squares with no external load (c); Trump crosses at a flush square (d)', 4, 1, side, panel_w=760, note_h=175)
    poses, s = poses_of(ws[RING]['z'])
    note = draw_config(pg, 0, poses, s)
    draw_x(pg, 0, s)
    pg.text(0, [note, '(a) the ring rand_0_0569|t20, side %.4f; fill = GLOBAL handedness (orange +, blue -, grey flat); dashed X + C/W = the PI\'s sectors.' % s,
                'Actual grains: LEFT half 2,3,4,5 all "-" (70 deg), RIGHT half 6,7,8,10 all "+" (20 deg) -- split by a vertical line, not by the X;',
                'floor meeters 4 "-" | 6 "+" and ceiling meeters 3 "-" | 10 "+" are MIXED walls; every corner pair (4|5, 6|7, 8|10, 2|3) is a',
                'flush SAME-handed pair; the tilt bound is loaded on 4 (-0.300), 7 (-0.018), 8 (+0.196), 2 (+0.073) -- the squares with no wall load.',
                'Lemma OPPOSE (opposite handedness at a jammed corner) fails at %d LOCKED same-handed corners of the witnesses (T1), '
                'against %d opposite-handed ones.' % tuple(sum(1 for r in recs.values() for c in r.get('corners', []) if c['locked'] and c['pair_frame'] == p)
                                                       for p in ('same', 'opposite'))])
    ch = ring['chains']
    note = draw_config(pg, 1, poses, s, thick=set(ch['LR']) | set(ch['TB']), hatch=ch['shared'])
    draw_chain(pg, 1, poses, ch['LR'], CHAIN_COL['LR'])
    draw_chain(pg, 1, poses, ch['TB'], CHAIN_COL['TB'])
    d = ch['shared_desc'][0]
    pg.text(1, [note, '(b) the ring\'s loaded chains: left-right %s (red), floor-ceiling %s (green); shared square (hatched): %s.' % (ch['LR'], ch['TB'], ch['shared']),
                'Square %d: tilted "%s", meeter of %s, wall load on %s, chain contacts %s, external load %.3f: it carries both chains and' % (
                    d['i'], d['h'], d['meeter_of'], d['walls_loaded'], d['edges'], d['ext_load']),
                'is torque-balanced by its contacts alone.  Planarity (Theorem CROSS-PLANAR) forces the chains to meet; nothing forbids the meeting square.',
                'No chain avoids the corner meeters at n = 11 (0 / 193 four-crowds have an interior LR and TB chain: 8 of 11 squares are meeters).'])
    poses, s = poses_of(ws[crowd_name]['z'])
    ch = cr['chains']
    note = draw_config(pg, 2, poses, s, thick=set(ch['LR']) | set(ch['TB']), hatch=ch['shared'])
    draw_chain(pg, 2, poses, ch['LR'], CHAIN_COL['LR'])
    draw_chain(pg, 2, poses, ch['TB'], CHAIN_COL['TB'])
    pg.text(2, [note, '(c) %s (CROWD four-crowd, side %.4f, external load %.2f on the crowd rows): chains LR %s, TB %s;' % (
        crowd_name, s, cr['ext_load'], ch['LR'], ch['TB']),
                'shared squares %s: %s' % (ch['shared'], '; '.join('%d %s %s ext %.2f' % (d['i'], d['h'], 'meeter' if d['meeter_of'] else 'interior', d['ext_load']) for d in ch['shared_desc'])),
                'tilted, NOT meeters, no external row: the "shared square carrying both torque senses" of step (v) exists and balances.',
                '%d of the 126 four-crowds with both chains have EVERY crossing square tilted and externally unloaded (T7).' % sum(
                    1 for r in recs.values() if r.get('n2') == 4 and r['chains']['shared_desc'] and all(x['ext_load'] <= 1e-7 and x['h'] in '+-' for x in r['chains']['shared_desc']))])
    poses, s = poses_of(ws['trump']['z'])
    ch = tr['chains']
    note = draw_config(pg, 3, poses, s, thick=set(ch['LR']) | set(ch['TB']), hatch=ch['shared'])
    draw_chain(pg, 3, poses, ch['LR'], CHAIN_COL['LR'])
    draw_chain(pg, 3, poses, ch['TB'], CHAIN_COL['TB'])
    pg.text(3, [note, '(d) Trump, side %.6f: LR %s, TB %s cross at square %s -- FLUSH, on the left wall, contacts %s.' % (
        s, ch['LR'], ch['TB'], ch['shared'], ch['shared_desc'][0]['edges']),
                'The flush-crossing case (b) of the brief is realised at the optimum itself (three flush corners, TL a locked 2-crowd):',
                'a flush square at the crossing is torque-neutral (two vertex rows per contact) and is Trump\'s reservoir (A234).'])
    return pg.write(os.path.join(PAGES, 'cross_ring_x.svg'))


def page_oppose(recs, ws, picks):
    side = max(recs[n]['s'] for n, _ in picks)
    pg = D.Page('A240 -- Lemma OPPOSE tested: four LOCKED corner arms in their frames (both meeters loaded, no external row on either); '
                'the frame handedness of the pair and the torque budget of each meeter', 4, 1, side, panel_w=760, note_h=175)
    for k, (name, cn) in enumerate(picks):
        r, w = recs[name], ws[name]
        c = [c for c in r['corners'] if c['corner'] == cn][0]
        poses, s = poses_of(w['z'])
        fp = frame_poses(poses, cn, s)
        meet = c['meeters']
        holders = sorted({h for m in c['members'] for h in m['along_holders'] + m['other_holders']})
        note = draw_config(pg, k, fp, s, thick=set(holders), hatch=[])
        for i in meet:
            pg.square(k, fp[i], 'none', D.RED, width=2.8)
        pg.cell(k, (0, 1, 0, 1), stroke=D.RED, dash='2,2', width=1.0)
        lines = [note, '(%s) %s corner %s in its frame, side %.4f: meeters %s (red), pair %s-handed (frame), partner contact %s, LOCKED %s' % (
            'abcd'[k], name, cn, s, meet, c['pair_frame'], c['partner_type'], c['locked'])]
        for m in c['members']:
            lines.append('sq %d %s %.1f deg: W %.3f | tau wall %+.3f partner %+.3f along-wall %+.3f (%s) other %+.3f (%s) ext %+.3f | sum %+.0e' % (
                m['i'], m['h'], m['tilt_frame_deg'], m['W'], m['tau_wall'], m['tau_partner'], m['tau_along'], m['along_holders'],
                m['tau_other'], m['other_holders'], m['tau_ext'], m['tau_sum']))
        lines.append({'same': 'same-handed and balanced by walls + contacts: OPPOSE fails here.',
                      'opposite': 'opposite-handed: the case OPPOSE predicts; 11 of 293 locked tilted pairs.',
                      'flat': 'a flat meeter (free self-torque on its wall edge): outside OPPOSE\'s hypothesis.'}[c['pair_frame']])
        pg.text(k, lines)
    return pg.write(os.path.join(PAGES, 'oppose_corners.svg'))


def page_grains(recs, ws, names):
    side = max(recs[n]['s'] for n in names)
    pg = D.Page('A240 -- wall grains of three four-crowds: the loaded handedness of each wall\'s meeters (fill = global handedness); '
                'the PI\'s alternation (left = right, top = bottom, left != top, every wall one-handed) occurs on 0 of 193', 3, 1, side, panel_w=760, note_h=150)
    for k, name in enumerate(names):
        r, w = recs[name], ws[name]
        poses, s = poses_of(w['z'])
        note = draw_config(pg, k, poses, s, thick={i for g in r['grains'].values() for i, l in zip(g['meeters'], g['loaded']) if l})
        gl = '; '.join('%s: %s' % (wn, ''.join(h for h, l in zip(g['h'], g['loaded']) if l) or '(none loaded)') for wn, g in r['grains'].items())
        pg.text(k, [note, '(%s) %s, side %.4f, external load %.2f; loaded meeters thick.' % ('abc'[k], name, s, r['ext_load']),
                    'wall grains (loaded meeters touching the wall, handedness): ' + gl,
                    {0: 'a MIXED floor and ceiling (the ring): the two floor meeters hold each other across a lean, opposite handedness (CORNER-LOAD).',
                     1: 'one-handed everywhere: a single grain meets all four corners (A223 s.1.5); no alternation.',
                     2: 'a four-crowd with a mixed wall and a flat wall meeter: handedness is not a wall label.'}[k]])
    return pg.write(os.path.join(PAGES, 'wall_grains.svg'))


def main():
    recs = {}
    for l in open(RES, encoding='utf-8'):
        r = json.loads(l)
        recs[r['name']] = r
    same_flush = [(r['name'], c['corner']) for r in recs.values() if r['cls'] == 'HELD' for c in r['corners']
                  if c['locked'] and c['pair_frame'] == 'same' and c['partner_type'] == 'flush' and c['wall_loaded_meeters'] == 2][0]
    same_ve_fj = [(r['name'], c['corner']) for r in recs.values() if r['name'].startswith('fj_') for c in r['corners']
                  if c['locked'] and c['pair_frame'] == 'same' and c['partner_type'] == 'VE' and c['wall_loaded_meeters'] == 2
                  and min(min(m['tilt_frame_deg'], 90 - m['tilt_frame_deg']) for m in c['members']) > 1.0][0]
    opp = [(r['name'], c['corner']) for r in recs.values() if r['cls'] == 'HELD' for c in r['corners'] if c['locked'] and c['pair_frame'] == 'opposite'][0]
    picks = [same_flush, same_ve_fj, opp, ('trump', 'TL')]
    one_handed = [r['name'] for r in recs.values() if r.get('n2') == 4 and r['name'] == 'w062_crowd'] or \
                 [r['name'] for r in recs.values() if r.get('n2') == 4 and all(len({h for h, l in zip(g['h'], g['loaded']) if l}) <= 1 for g in r['grains'].values())]
    mixed_flat = [r['name'] for r in recs.values() if r.get('n2') == 4 and r['name'] != RING and
                  any('+' in g['h'] and '-' in g['h'] for g in r['grains'].values()) and any('F' in g['h'] for g in r['grains'].values())]
    names = [RING, one_handed[0], mixed_flat[0]]
    need = {RING, 'trump'} | {n for n, _ in picks} | set(names)
    crowd_pick = [r['name'] for r in recs.values() if r.get('n2') == 4 and r['chains']['shared_desc'] and
                  all(d['ext_load'] <= 1e-7 and d['h'] in '+-' and not d['meeter_of'] for d in r['chains']['shared_desc'])]
    need |= set(crowd_pick[:1])
    ws = load_witnesses(need)
    print(page_cross(recs, ws))
    print(page_oppose(recs, ws, picks))
    print(page_grains(recs, ws, names))


if __name__ == '__main__':
    main()
