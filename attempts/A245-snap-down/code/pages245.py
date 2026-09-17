"""A245 pages (docs/residue_map/campaigns/A245-snap-down/):
  stack_cases.svg  STACK's cases drawn exactly in the wall frame at s = 3.82: the floating (no-contact)
                   witness and five resting pairs, one per contact type, all mutual;
  wall_click.svg   the LOCAL click on a testbed wall pair (frames t = 0, 1/2, 1), a BLOCKED local click
                   with its blockers, the GLOBAL click's end frame;
  reduce.svg       the 3-for-3 REDUCE on a wall (before / after) on a four-crowd and on a 12-stuck candidate.
Every panel is geometry-checked as drawn (containment + pairwise interior-disjointness, exact SAT) and the
check is printed in its note.
    python pages245.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import draw244 as D          # noqa: E402
import geom245 as G          # noqa: E402
import reduce245 as R        # noqa: E402
import stack245 as S         # noqa: E402
import testbeds245 as T      # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A245-snap-down')
RES = os.path.join(HERE, '..', 'results')
CELLCOL = {'c00': '#ffe9c9', 'c01': '#dfeffd', "c'01": '#e6f7e3', "c'00": '#ffe9c9'}


def chk(poses, s):
    ok, gw, gp = G.check_packing(poses, s, tol=1e-9)
    return 'check %s (wall %.1e, pair %.1e)' % ('OK' if ok else 'FAIL', gw, gp)


def page_stack():
    s = 3.82
    cases = [('floating: both flat, gap 0.05 < 4 - s', math.pi / 2, 0.9, 0.0, 2.95),
             ("'++'", math.radians(20), 1.6, math.radians(30), None),
             ("'++'", math.radians(40), 1.2, math.radians(10), None),
             ("'--'", math.radians(60), 1.2, math.radians(70), None),
             ("'-+' (a lean)", math.radians(70), 1.05, math.radians(30), None),
             ('flush: equal tilts 25 deg', math.radians(25), 1.6, math.radians(25), None)]
    pg = D.Page(1180, 900, 'STACK')
    pg.text(14, 22, 'A245 Lemma STACK -- the mutual wall pair at s = 3.82, wall frame (wall = u = 0, corner c at v = 0, '
            "c' at v = s); cells c00, c01 (blue), c'01 (green), c'00", 12, weight='bold')
    for k, (title, th, ell, thp, ellp) in enumerate(cases):
        if ellp is None:
            ellp = S.contact_ell(th, ell, thp, s)
        B, Bp = G.wall_pose(th, ell), G.wall_pose(thp, ellp)
        x, y = 14 + (k % 3) * 390, 40 + (k // 3) * 425
        key = 'p%d' % k
        pg.panel(key, x, y, 250, 330, s, pad=0.1, win=(-0.05, 2.35, -0.05, s + 0.05))
        for nm, r in G.wall_cells(s).items():
            if nm == 'c02':
                continue
            pg.rect(key, r, CELLCOL[nm], '#bbb', 0.7, dash='3,2')
        pg.square(key, B, D.ORANGE, '#8a4a08', 1.4, label='B', op=0.5)
        pg.square(key, Bp, D.BLUE, '#1c4470', 1.4, label="B'", op=0.5)
        a, b = pg._t(key, (0, 0)), pg._t(key, (0, s))
        pg.line(a[0], a[1], b[0], b[1], '#222', 2.0)
        ctype = S.contact_type(th, ell, thp, ellp) if G.pair_gap(B, Bp) <= 1e-6 else 'none'
        if ctype != 'none':
            A, Bv = S.named_verts(th, ell), S.named_verts(thp, ellp)
            pt = A['T'] if ctype.replace('flush:', '').startswith('T') else Bv['V']
            pg.dot(key, (float(pt[0]), float(pt[1])), D.RED, 3.0)
        m = S.mutual(B, Bp, s)
        yT, yVp = ell + math.sin(th), ellp - math.cos(thp)
        pg.text(x, y - 6, '(%s) %s  %s' % ('abcdef'[k], title, ctype if not title.startswith(('flo', 'flu')) else ''), 10.5, weight='bold')
        pg.note(x + 262, y + 14, [
            'theta = %.1f, ell = %.3f' % (math.degrees(th), ell),
            "theta' = %.1f, ell' = %.3f" % (math.degrees(thp), ellp),
            'hand %s' % (G.handedness(th) + G.handedness(thp)),
            'mutual cells %s' % ('all met' if all(m) else str(m)),
            'disjoint gap %.1e' % G.pair_gap(B, Bp),
            "order ell < ell': %s" % (ell < ellp),
            'clearance y_V\' - y_T = %.3f' % (yVp - yT),
            '  (4 - s = %.3f)' % (4 - s),
            'contact: %s' % ctype,
            'table: %s' % S.predicted(th, thp),
            'H = %.3f, chords %.3f' % (ellp + math.sin(thp) - ell + math.cos(th), G.chord(th) + G.chord(thp)),
            chk([B, Bp], s)], size=8.6, lead=11)
    pg.save(os.path.join(OUT, 'stack_cases.svg'))


def draw_cfg(pg, key, poses, s, pair=(), marks=(), labels=True):
    for i, p in enumerate(poses):
        if i in pair:
            fill, stroke = (D.ORANGE, '#8a4a08')
        elif i in marks:
            fill, stroke = (D.RED, '#800')
        else:
            fill, stroke = ('#dddddd', '#777')
        pg.square(key, p, fill, stroke, 1.2, label=str(i) if labels else None, op=0.6)
    pg.frame(key, s)


def page_click(rows, cfgs):
    def pick(pred):
        for r in rows:
            if r['pair_info']['pair'] is not None and pred(r):
                return r
        return None
    feas = pick(lambda r: r['tag'] == 'crowd' and r['pair_info'].get('mutual') and r['pair_info'].get('hwall')
                and r['click']['local']['feasible_at_s0']) or \
        pick(lambda r: r['tag'] == 'crowd' and r['pair_info'].get('hwall') and r['click']['local']['feasible_at_s0']
             and r['pair_info']['contact'])
    blocked = pick(lambda r: r['tag'] == 'crowd' and r['click']['local']['blocked_at'] is not None
                   and r['click']['local']['blockers'])
    pg = D.Page(1180, 760, 'WALL-CLICK')
    pg.text(14, 22, 'A245 WALL-CLICK on testbed wall pairs (orange): LOCAL = the pair alone moves, every other square '
            'frozen; GLOBAL = every centre re-minimised (A223 variant B)', 12, weight='bold')
    panels = []
    if feas:
        fr = feas['click']['local']['frames']
        for k, t in enumerate(sorted(fr, key=float)):
            panels.append(('LOCAL t = %s  (%s, wall %s)' % (t, feas['rid'], feas['wall']), fr[t][0], fr[t][1],
                           feas['pair_info']['pair'], (), feas))
        gf = feas['click']['global']['frames']
        tl = max(gf, key=float)
        panels.append(('GLOBAL t = %s end, s = %.5f' % (tl, gf[tl][1]), gf[tl][0], gf[tl][1], feas['pair_info']['pair'], (), feas))
    if blocked:
        fr = blocked['click']['local']['frames']
        tl = max(fr, key=float)
        marks = tuple(sorted({b[1] for b in blocked['click']['local']['blockers']}))
        panels.append(('LOCAL BLOCKED at t = %s (%s, wall %s): last feasible frame t = %s, blockers red' % (
            blocked['click']['local']['blocked_at'], blocked['rid'], blocked['wall'], tl), fr[tl][0], fr[tl][1],
            blocked['pair_info']['pair'], marks, blocked))
    for k, (title, poses, s, pair, marks, r) in enumerate(panels[:6]):
        x, y = 14 + (k % 3) * 390, 44 + (k // 3) * 350
        key = 'c%d' % k
        pg.panel(key, x, y, 300, 300, s, pad=0.1)
        draw_cfg(pg, key, [tuple(p) for p in poses], s, pair, marks)
        pg.text(x, y - 6, title[:78], 9.5, weight='bold')
        pi = r['pair_info']
        pg.note(x + 306, y + 14, [
            'pair B = %d, B\' = %d' % tuple(pi['pair']), 'hand %s, mutual %s' % (pi['hand'], pi.get('mutual')),
            'contact %s' % pi.get('contact_type', pi['contact']),
            's0 = %.5f' % r['s0'], 'local s(t): %s' % (r['click']['local']['s'][:2] + ['..'] + r['click']['local']['s'][-1:]),
            'global end %s' % r['click']['global']['s_end'],
            'blockers %s' % (r['click']['local']['blockers'] or '-'),
            chk([tuple(p) for p in poses], s)], size=8.3, lead=10.5)
    pg.save(os.path.join(OUT, 'wall_click.svg'))


def page_reduce(rows, cfgs):
    pg = D.Page(1180, 420, 'REDUCE')
    pg.text(14, 22, 'A245 Lemma REDUCE, the 3-for-3 on a wall column: the three meeters of {c00, c01} (orange) exchanged for '
            'the corner domino + one leftover (red), Lemma CELLS / SWAP', 12, weight='bold')
    k = 0
    for tag in ('crowd', 'a244'):
        r = next((r for r in rows if r['tag'] == tag and 'k2' in r['reduce_before'] and r['reduce_before']['k2']['placed']), None)
        if r is None:
            continue
        cfg = cfgs[r['rid']]
        rec = r['reduce_before']['k2']
        new = R.exchanged_packing(cfg['poses'], cfg['s'], r['wall'], rec)
        for j, (title, poses, pair, marks) in enumerate((('before: %s wall %s, M = %s' % (r['rid'][:28], r['wall'], rec['M']),
                                                          cfg['poses'], tuple(rec['M']), ()),
                                                         ('after: domino + leftover, same side %.5f' % cfg['s'], new,
                                                          (len(new) - 3, len(new) - 2), (len(new) - 1,)))):
            x, y = 14 + (2 * k + j) * 292, 44
            key = 'r%d%d' % (k, j)
            pg.panel(key, x, y, 240, 240, cfg['s'], pad=0.1)
            draw_cfg(pg, key, poses, cfg['s'], pair, marks)
            pg.text(x, y - 6, title[:60], 9.0, weight='bold')
            pg.note(x, y + 256, ['n = %d, %s' % (len(poses), chk(poses, cfg['s']))], size=8.3)
        k += 1
    pg.save(os.path.join(OUT, 'reduce.svg'))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [json.loads(l) for l in open(os.path.join(RES, 'click245.jsonl'), encoding='utf-8')]
    cfgs = {c['rid']: c for c in T.all_configs()}
    page_stack()
    page_click(rows, cfgs)
    page_reduce(rows, cfgs)
    print('pages written to', OUT)


if __name__ == '__main__':
    main()
