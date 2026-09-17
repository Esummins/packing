"""A247 pages (docs/residue_map/campaigns/A247-perimeter-walk/):
  catalogue.svg   (A) the twelve cells as a ring with N_BL; (B)-(E) exact witnesses of realisable
                  cell-sets (drawn poses re-checked: cells met at the level, containment);
  walks.svg       ring diagrams of walks (combinatorial: no geometry drawn);
  tight_case.svg  the certified kills and a surviving walk's tight sub-configuration (witnesses
                  re-checked as drawn).
Every configuration panel prints its geometry check in the panel note.
    python pages247.py
"""
import json
import math
import os
import sys

import geo247 as G

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
from draw244 import Page                 # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A247-perimeter-walk')
BLUE, RED, GREEN, GREY, ORANGE = '#3b6fd6', '#d63b3b', '#3a9d5d', '#999', '#e08a1e'
CELLCOL = {'00': '#fff3cc', '01': '#e3f0ff', '10': '#e6f7e3'}


def rows(name):
    p = os.path.join(ATT, 'results', name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def check_pose(pose, s, eta):
    met = [n for n in G.RING if G.depth_cell_pt(pose, n, s) > eta]
    q = G.C.square_corners(*pose)
    return met, float(min(q.min(), s - q.max()))


def cells_panel(pg, key, x, y, w, h, s, win=None, names=G.RING):
    pg.panel(key, x, y, w, h, s, win=win)
    for n in names:
        pg.rect(key, G.rect_at(n, s), CELLCOL[n[2:]], '#bbb', 0.7)
    pg.frame(key, s)


def page_catalogue():
    s = G.SHAT
    pg = Page(1000, 720, 'A247 catalogue')
    cells_panel(pg, 'A', 20, 30, 300, 300, s)
    for n in G.NBR['BL']:
        pg.rect('A', G.rect_at(n, s), 'none', RED, 1.4, dash='4,2')
    for n in G.RING:
        r = G.rect_at(n, s)
        pg.text(*pg._t('A', ((r[0] + r[1]) / 2 - 0.3, (r[2] + r[3]) / 2 - 0.08)), n, 8)
    pg.text(30, 24, '(A) the twelve cells at s-hat; N_BL dashed (the five cells one square can meet)', 11, weight='bold')
    pg.note(20, 346, ['PROJECTION [T]: cells with along-wall intervals (0,1) and (s-1,s) are > s-2 > sqrt2 apart,',
                      'so a square meets cells of one N_c only; every subset of N_c is realisable (witness below).'])
    cat = rows('catalogue247_exact_0.05.jsonl') or rows('catalogue247.jsonl')
    want = [('M', ['BL00', 'BL10', 'BR10', 'TL01', 'BL01']), ('F', ['BL10', 'BL01']),
            ('M', ['BL00', 'BR10', 'TL01']), ('F', ['BL10', 'BR10', 'TL01'])]
    keys = 'BCDE'
    slots = [(340, 30), (660, 30), (340, 380), (660, 380)]
    k = 0
    for kind, cells in want:
        hit = [r for r in cat if r.get('kind') == kind and sorted(r['cells']) == sorted(cells)]
        if not hit or not hit[0].get('witness'):
            continue
        r = hit[0]
        w = r['witness']
        sw, pose = w['s'], tuple(w['pose'])
        key = keys[k]
        x0, y0 = slots[k]
        k += 1
        cells_panel(pg, key, x0, y0, 300, 300, sw, win=(0, 3.0, 0, 3.0))
        pg.square(key, pose, BLUE if kind == 'M' else ORANGE, '#123', label=kind)
        eta = r.get('eta', 0.0) if r.get('exact') else 0.0
        met, gap = check_pose(pose, sw, eta)
        pg.text(x0 + 10, y0 - 6, '(%s) %s set %s' % (key, 'meeter' if kind == 'M' else 'free (box-avoiding)', ' '.join(cells)), 11, weight='bold')
        lines = ['witness s = %.4f, pose (%.3f, %.3f, %.1f deg), exact rational check: %s' % (
            sw, pose[0], pose[1], math.degrees(pose[2]), w['exact']['ok']),
            'check as drawn: cells met at level %g = %s' % (eta, ' '.join(met)),
            'containment gap %.3f; %s; tilt bins %s' % (gap, 'exact form' if r.get('exact') else 'monotone form', r.get('tilt_bins_deg', ''))]
        if r.get('exact') and sorted(met) != sorted(cells):
            lines.append('NB: the avoid gap (depth <= %g on the other cells) admits this pose, whose threshold-%g set is larger;' % (r.get('eta_avoid', eta), eta))
            lines.append('the set %s itself is a zero-margin case (a meeter reaching a far slot meets its own slot as deeply, s.4.3).' % ' '.join(cells))
        pg.note(x0, y0 + 316, lines)
    pg.save(os.path.join(OUT, 'catalogue.svg'))


def ring_diagram(pg, x, y, size, rec, title):
    """a walk as a ring: 12 cells on a circle, each square an arc through its cells."""
    cx, cy, R = x + size / 2, y + size / 2, size / 2 - 40
    ang = {n: -math.pi / 2 + 2 * math.pi * G.RING.index(n) / 12 for n in G.RING}
    for n in G.RING:
        px, py = cx + R * math.cos(ang[n]), cy + R * math.sin(ang[n])
        pg.parts.append('<rect x="%.1f" y="%.1f" width="34" height="16" fill="%s" stroke="#999" stroke-width="0.7"/>'
                        % (px - 17, py - 8, CELLCOL[n[2:]]))
        pg.text(px, py + 4, n, 7.5, anchor='middle')
    squares = []
    for c, d1, d2 in rec['corners']:
        for d in (d1, d2):
            squares.append((['%s00' % c] + list(d), BLUE))
    for f in rec['free']:
        if f:
            squares.append((list(f), ORANGE))
    for j, (cells, col) in enumerate(squares):
        r = R - 22 - 7 * (j % 6)
        idx = sorted(G.RING.index(n) for n in cells)
        # the shortest arc covering the cells (they lie within 5 consecutive ring positions)
        best = None
        for start in idx:
            span = max((i - start) % 12 for i in idx)
            if best is None or span < best[1]:
                best = (start, span)
        a0 = -math.pi / 2 + 2 * math.pi * best[0] / 12
        pts = []
        for t in range(21):
            a = a0 + 2 * math.pi * best[1] / 12 * t / 20
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        if best[1] == 0:
            pg.dot(None, (0, 0), col, 0) if False else None
            pg.parts.append('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (pts[0][0], pts[0][1], col))
        else:
            pg.polyline(pts, col, 2.0)
            for n in cells:
                a = ang[n]
                pg.parts.append('<circle cx="%.1f" cy="%.1f" r="2.4" fill="%s"/>' % (cx + r * math.cos(a), cy + r * math.sin(a), col))
    pg.text(x + 6, y + 12, title, 10, weight='bold')
    pg.text(x + 6, y + size - 6, 'slots: ' + ' '.join('%s:%s' % (z[:2] + z[2:], rec['letters'][z]) for z in G.SLOT_RING), 7.2)


def page_walks():
    files = [f for f in sorted(os.listdir(os.path.join(ATT, 'results'))) if f.startswith('walks247_') and f.endswith('.jsonl')]
    if not files:
        return
    R = rows(files[-1])
    summ = R[0] if R and R[0].get('kind') == 'summary' else {}
    walks = [r for r in R if r.get('kind') != 'summary']
    pick = walks[:8]
    pg = Page(1000, 560 if len(pick) <= 4 else 1040, 'A247 walks')
    pg.text(20, 22, 'A247 walks (%s): %s walks up to D4 at level eta = %s; blue arcs = corner meeters, orange = free squares; '
            'combinatorial diagrams, no geometry drawn' % (files[-1], summ.get('walks_d4', '?'), summ.get('eta', '?')), 11, weight='bold')
    for i, rec in enumerate(pick):
        x, y = 20 + 245 * (i % 4), 40 + 490 * (i // 4)
        ring_diagram(pg, x, y, 235, rec, 'walk %d: free used %d, free incidences %d' % (i + 1, rec['n_free_used'], rec['free_incidences']))
        y2 = y + 250
        pg.note(x + 6, y2, ['corners: ' + '; '.join('%s{%s|%s}' % (c, '+'.join(d1) or '-', '+'.join(d2) or '-') for c, d1, d2 in rec['corners'])][:1], 6.4)
        pg.note(x + 6, y2 + 10, ['free: ' + ' / '.join('+'.join(f) or '-' for f in rec['free'])], 6.4)
        pg.note(x + 6, y2 + 22, ['verdict: %s' % rec.get('verdict', 'pairs feasible; triples pending')], 7.2)
    pg.save(os.path.join(OUT, 'walks.svg'))


def page_tight():
    pg = Page(1000, 400, 'A247 tight case')
    prs = [r for r in rows('pairs247_window_exact_0.05.jsonl')]
    kills = [r for r in prs if r['status'] == 'INFEASIBLE']
    feas = [r for r in prs if r['status'] == 'FEASIBLE' and r.get('witness')]
    pg.text(20, 22, 'A247 pair table (exact form, level 0.05, window): %d pairs, %d INFEASIBLE (certified), %d FEASIBLE (exact witnesses), %d undecided' % (
        len(prs), len(kills), len(feas), len(prs) - len(kills) - len(feas)), 11, weight='bold')
    shown = 0
    for r in feas:
        if shown >= 3:
            break
        sp = r['specs']
        if not any(s[0] == 'M' for s in sp):
            continue
        w = r['witness']
        sw = w['s']
        key = 'T%d' % shown
        x0 = 20 + 330 * shown
        cells_panel(pg, key, x0, 40, 300, 280, sw, win=(0, 3.0, 0, 3.0))
        notes = []
        for j, (sp_j, pose) in enumerate(zip(sp, w['poses'])):
            pose = tuple(pose)
            pg.square(key, pose, BLUE if sp_j[0] == 'M' else ORANGE, '#123', label=sp_j[0])
            met, gap = check_pose(pose, sw, r['eta'])
            notes.append('%s wants %s: meets %s at level %g' % (sp_j[0], '+'.join(sp_j[2] if sp_j[0] == 'M' else sp_j[1]), '+'.join(met), r['eta']))
        pd = G.depth_pair_pt(tuple(w['poses'][0]), tuple(w['poses'][1]))
        notes.append('pair depth %.4f (<= 0: disjoint), exact check %s, s = %.4f' % (pd, w['exact']['ok'], sw))
        pg.text(x0 + 10, 34, '(%d) a feasible pair, its exact witness' % (shown + 1), 10, weight='bold')
        pg.note(x0, 336, notes, 7.6, 10)
        shown += 1
    pg.save(os.path.join(OUT, 'tight_case.svg'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    page_catalogue()
    page_walks()
    page_tight()
    print('pages written to', OUT)
