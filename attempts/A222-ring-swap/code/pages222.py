"""A222 pages (docs/residue_map/campaigns/A222-ring-swap/):
  sweep_rand_0_0569_t20.svg     -- the PI's sweep on the ring witness, window-shaped perimeter from BL counter-
                                   clockwise: per step the settled cells, the exposed cell and its meeters, the
                                   squares in hand (Lemma STEP bookkeeping, ring_swap.md s.1.4);
  ring_swap_rand_0_0569_t20.svg -- X (the eight meeters), U(X), the corner swap at each corner (BL blocked by
                                   rattler 0), and X' = 4 settled corners + 4 band squares (ring4, admissible);
  window8_fail_<wid>.svg        -- a four-crowd whose window-shaped 8-cell family is over-met everywhere.
    python pages222.py
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import cells222 as C          # noqa: E402
import raise222 as R          # noqa: E402
import draw222 as D           # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
PAGES = os.path.join(ATT, '..', '..', 'docs', 'residue_map', 'campaigns', 'A222-ring-swap')
os.makedirs(PAGES, exist_ok=True)
RID = 'rand_0_0569|t20'
ROLE = {0: 'rattler 0', 1: 'rattler 1', 9: 'holder 9'}


def load_ring():
    w = [x for x in R.load(True) if x['rid'] == RID][0]
    sw = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'swap222.jsonl'), encoding='utf-8')]
    sw = [r for r in sw if r['rid'] == RID][-1]
    return w, sw


def poses_of(z):
    return [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(G.N)]


def page_sweep():
    t0 = time.time()
    w, _ = load_ring()
    z = np.array(w['z'])
    s = float(z[G.S_IDX])
    sq = poses_of(z)
    ring = sorted(sum(w['meeters'].values(), []))
    sw = C.sweep(z, 'BL', False, window=True)
    steps = sw['steps']
    pg = D.Page('A222 -- the sweep on the ring rand_0_0569|t20 (side %.4f), window-shaped perimeter from BL counter-clockwise: '
                'each step exposes one cell, its remaining meeters are picked up, one square is placed as the slot square' % s,
                4, 2, s, note_h=105)
    consumed, settled = set(), []
    t1 = time.time()
    for k, st in enumerate(steps):
        cell = st['cell']
        c, ij = cell.split('(')
        i, j = (int(v) for v in ij[:-1].split(','))
        box = C.cell_box(c, i, j, s)
        pg.frame(k)
        for q in range(G.N):
            if q in consumed:
                continue
            fill = D.ORANGE if q in ring else D.GREY
            if q in st['M']:
                fill = (fill[0], D.RED)
            pg.square(k, sq[q], fill[0], fill[1], label=q, width=2.2 if q in st['M'] else 1.3)
        for b in settled:
            pg.cell(k, b, stroke='#1f4e79', fill='#dbe9f6', dash=None, width=2.0)
        pg.cell(k, box, stroke=D.RED, label=cell)
        remaining = [sq[q] for q in range(G.N) if q not in consumed]
        ok, gap, wall = pg.check_partial(remaining + [((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, 0.0) for b in settled], s)
        consumed |= set(st['M'])
        settled.append(box)
        pg.text(k, ['step %d: expose %s; meeters among the remaining squares M = %s' % (st['k'], cell, st['M']),
                    'action: %s; in hand after the step: %d' % (st['action'], st['h']),
                    'drawn: remaining squares (orange = ring member, grey = other, red edge = meeter of the cell),',
                    'settled cells so far (blue), the exposed cell (red dashed); geometry of the drawn partial packing',
                    'checked: min pair gap %.0e, min wall %.0e; %.2f s per step' % (gap, wall, (time.time() - t1) / (k + 1))])
    tot = sum(len(st['M']) for st in steps)
    pg.text(7, ['', 'after 8 cells: %d squares consumed, %d in hand, %d untouched; the ring alone supplies 8 of the >= 9 the '
                'sweep needs, and the' % (tot, sw['h_final'], G.N - tot),
                'intruders (rattler 0 at BL(1,0), holder 9 at TR(1,0)) the rest.  Full-perimeter (12-cell) sweep at this side: '
                'nothing in hand at step 2 from BR (trivial at S >= 4).', 'renderer %.2f s' % (time.time() - t0)], dy=12)
    return pg.write(os.path.join(PAGES, 'sweep_rand_0_0569_t20.svg'))


def page_ring_swap():
    t0 = time.time()
    w, sw = load_ring()
    z = np.array(w['z'])
    s = float(z[G.S_IDX])
    sq = poses_of(z)
    ring = sorted(sum(w['meeters'].values(), []))
    pg = D.Page('A222 -- RING SWAP on rand_0_0569|t20 (side %.4f): X = the eight meeters, U(X) = container minus the other '
                'squares, the corner swaps, and X\' = four settled corners + four band squares (Lemma SWAP)' % s, 3, 2, s, note_h=110)
    # (0) P with X
    pg.frame(0)
    for q in range(G.N):
        f = D.ORANGE if q in ring else D.GREY
        pg.square(0, sq[q], f[0], f[1], label=q)
    ok, gap, wall = pg.check(sq, s)
    pg.text(0, ['(a) the witness P: X = meeters %s (orange), non-ring squares 0, 1 (rattlers) and 9 (holder, grey).' % ring,
                'exact poses of A217; check: min pair gap %.0e, min wall %.0e.' % (gap, wall)])
    # (1) U(X)
    pg.frame(1)
    for q in range(G.N):
        if q not in ring:
            pg.square(1, sq[q], D.DARK[0], D.DARK[1], label=q)
        else:
            pg.square(1, sq[q], 'none', '#e0b070', label=q, dash='3,3')
    for c in C.CORNERS:
        cx, cy = G.slot_centre(c, s)
        pg.cell(1, (cx - .5, cx + .5, cy - .5, cy + .5), stroke='#1f4e79', fill='#dbe9f6', dash=None, width=2.0)
    pg.check(sq, s)
    pg.text(1, ['(b) U(X) = white: the container minus the interiors of the three non-ring squares (hatched); X dotted.',
                'The four corner slot squares (blue) lie in U(X): each corner box is met by its two meeters only.',
                'window-perimeter cells met by non-ring squares: %s (they enter BL(1,0) and TR(1,0)).' % sw['intruders']])
    # (2..5) corner swaps
    for k, c in enumerate(C.CORNERS):
        r = sw['searches']['corner_' + c]
        pn = 2 + k if k < 3 else None
        if pn is None:
            continue
        pg.frame(pn)
        X = r['X']
        for q in range(G.N):
            if q in X:
                pg.square(pn, sq[q], 'none', '#e0b070', label=q, dash='3,3')
            else:
                pg.square(pn, sq[q], D.GREY[0], D.GREY[1], label=q)
        cx, cy = G.slot_centre(c, s)
        pg.cell(pn, (cx - .5, cx + .5, cy - .5, cy + .5), stroke='#1f4e79', fill='#dbe9f6', dash=None, width=2.0)
        if r['found']:
            newp = poses_of(np.array(r['z_swapped']))
            for p in newp[G.N - r['k']:]:
                pg.square(pn, p, 'none', D.RED, width=2.4, label="X'")
            ok, gap, wall = pg.check(newp, s)
            note = ['(%s) CORNER-SWAP at %s: X = %s -> S_%s + one square in U(X) \\ int S_%s (red outline, admissible pose):' % (
                'cde'[k], c, X, c, c), 'found by %s in %.2f s; exact check of the swapped packing: min gap %.0e, min wall %.0e.' % (
                r['method'], r['secs'], gap, wall)]
        else:
            # undecided: stipple the two removed meeters' remainders
            for q in X:
                pg.square(pn, sq[q], D.STIP[0], D.STIP[1], label=q)
            pg.check(sq, s)
            note = ['(%s) CORNER-SWAP at %s: X = %s, S_%s settled; NO unit square found in U(X) \\ int S_%s' % ('cde'[k], c, X, c, c),
                    '(c-space empty at every tilt on a 1-degree grid, 12 penalty restarts, %.2f s); the remainders (stipple) are' % r['secs'],
                    'cut by rattler 0 (hull intruders %s): the pocket above the 4-6 contact holds it.' % r['hull_intruders']]
        pg.text(pn, note)
    # (5) ring4
    r = sw['searches']['ring4']
    pg.frame(5)
    for q in range(G.N):
        if q in ring:
            pg.square(5, sq[q], 'none', '#e0b070', label=q, dash='3,3')
        else:
            pg.square(5, sq[q], D.GREY[0], D.GREY[1], label=q)
    if r['found']:
        newp = poses_of(np.array(r['z_swapped']))
        for p in newp[G.N - 8:G.N - 4]:
            pg.square(5, p, '#dbe9f6', '#1f4e79', width=2.0, label='S')
        for p in newp[G.N - 4:]:
            pg.square(5, p, 'none', D.RED, width=2.4, label="X'")
        ok, gap, wall = pg.check(newp, s)
        pg.text(5, ['(f) RING SWAP: X = the eight meeters -> four settled corners (blue) + four squares in the wall bands (red,',
                    'admissible poses found by %s in %.2f s); exact check: min gap %.0e, min wall %.0e.' % (r['method'], r['secs'], gap, wall),
                    'The corner swap at BL fails alone (e) but the ring swaps at once: the 4-6 contact is released.  Same side %.4f.' % s,
                    'renderer %.2f s' % (time.time() - t0)])
    else:
        pg.check(sq, s)
        pg.text(5, ['(f) RING SWAP: not found (%s); %d of 4 band squares placed.' % (r['method'], r.get('k_max_greedy', 0))])
    return pg.write(os.path.join(PAGES, 'ring_swap_rand_0_0569_t20.svg'))


def page_window8_fail():
    t0 = time.time()
    rows = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'raise222_kept.jsonl'), encoding='utf-8')]
    cand = [r for r in rows if r['n2'] == 4 and r['window8']['d_min'] >= 1]
    if not cand:
        return None
    r = min(cand, key=lambda x: x['s'])
    w = [x for x in R.load(True) if x['rid'] == r['rid']][0]
    z = np.array(w['z'])
    s = float(z[G.S_IDX])
    sq = poses_of(z)
    cells = C.cells_at(s)
    masks = C.meeter_masks(z, cells)
    byname = {c['name']: k for k, c in enumerate(cells)}
    ring = sorted(sum(w['meeters'].values(), []))
    pg = D.Page('A222 -- a four-crowd whose window-shaped 8-cell perimeter is over-met by every sub-family: %s (%s, side %.4f)' % (
        r['wid'], r['cls'], s), 1, 1, s, note_h=150, width_extra=420)
    pg.frame(0)
    for q in range(G.N):
        f = D.ORANGE if q in ring else D.GREY
        pg.square(0, sq[q], f[0], f[1], label=q)
    for (c, i, j) in C.window_family(s):
        nm = '%s(%d,%d)' % (c, i, j)
        m = masks[byname[nm]]
        pg.cell(0, C.cell_box(c, i, j, s), label='%s: %s' % (nm, [q for q in range(G.N) if (m >> q) & 1]))
    ok, gap, wall = pg.check(sq, s)
    w8 = r['window8']
    pg.text(0, ['the eight window cells (red dashed) with the squares meeting their open interiors; orange = corner meeters.',
                'd(Pi) = |M(Pi)| - |Pi| >= 1 for every sub-family containing a corner: by size %s; full family |M| = %d, d = %d.' % (
                    w8['d_by_size'], w8['M'], w8['d']),
                'The window-shaped sweep leaves >= 1 square in hand from every start; the full %d-cell perimeter at this side '
                'succeeds (S >= 4).' % (4 * int(s) - 4),
                'exact poses; check: min pair gap %.0e, min wall %.0e; renderer %.2f s' % (gap, wall, time.time() - t0)])
    return pg.write(os.path.join(PAGES, 'window8_fail_%s.svg' % r['wid']))


if __name__ == '__main__':
    for f in (page_sweep, page_ring_swap, page_window8_fail):
        print(f())
