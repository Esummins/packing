"""A250 pages: (1) a certified twelve-stuck packing with its teleportable corner domino and the k2
packing Lemma CELLS exchanges it into; (2) the cells' disjointness at the two regimes and the
family-stuck count table.  Every panel carries its own geometry check (containment + pairwise
interior-disjointness of exactly the poses drawn)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C          # noqa: E402
import draw244 as D           # noqa: E402
import fam250 as FM           # noqa: E402

OUT = os.path.join(ROOT, 'docs/residue_map/campaigns/A250-family-stuck')
GREEN, ORANGE, BLUE, RED = D.GREEN, D.ORANGE, D.BLUE, D.RED


def pick(dom=('BL00', 'BL01')):
    """the lowest-sided certified twelve-stuck packing whose domino `dom` has exactly 2 meeters."""
    rs = [json.loads(l) for l in open(os.path.join(
        ROOT, 'attempts/A244-twelve-stuck/results/twelve244.jsonl')) if l.strip()]
    rs = [r for r in rs if 'z' in r]
    rs.sort(key=lambda r: r['z'][33])
    for r in rs:
        ms = C.meeter_sets(r['z'])
        u = sorted(set(ms[dom[0]]) | set(ms[dom[1]]))
        if len(u) == 2:
            return r, u, ms
    raise RuntimeError('none')


def cells_panel(p, key, s, label, hi=(), conflict=False):
    p.frame(key, s, label)
    for c in FM.CELLS:
        r = C.cell_rect(c, s)
        p.rect(key, r, D.CELLFILL[c[2:]] if c not in hi else '#ffd0d0',
               '#c02020' if c in hi else '#bbb', 1.4 if c in hi else 0.7)
    if conflict:
        for (i, j) in sorted(FM.conflicts(s)):
            a, b = C.cell_rect(FM.CELLS[i], s), C.cell_rect(FM.CELLS[j], s)
            ov = (max(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]))
            p.rect(key, ov, '#f0a0a0', '#c02020', 1.0)


def page_exchange():
    r, u, ms = pick()
    z, s = r['z'], r['z'][33]
    keep = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11) if i not in u]
    gone = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in u]
    ra, rb = C.cell_rect('BL00', s), C.cell_rect('BL01', s)
    pins = [((ra[0] + ra[1]) / 2, (ra[2] + ra[3]) / 2, 0.0),
            ((rb[0] + rb[1]) / 2, (rb[2] + rb[3]) / 2, 0.0)]
    okA, gwA, gpA = D.check(keep + gone, s)
    okB, gwB, gpB = D.check(keep + pins, s)
    p = D.Page(1000, 560, 'A250 domino exchange')
    p.text(20, 26, 'A250 -- every certified twelve-stuck packing has a TELEPORTABLE corner domino',
           15, '#111', weight='bold')
    p.text(20, 46, 'Lemma CELLS (ring_swap.md s.1.3, Lean cells_swap): a family Pi of pairwise '
                   'disjoint unit cells with |M(Pi)| <= |Pi| exchanges into the |Pi| cell squares '
                   'at the SAME side.', 10.5)
    p.panel('A', 40, 70, 400, 400, s)
    p.panel('B', 530, 70, 400, 400, s)
    cells_panel(p, 'A', s, 'twelve-stuck packing, s = %.6f (A244 certified)' % s,
                hi=('BL00', 'BL01'))
    for q in keep:
        p.square('A', q, BLUE, '#1b4a77')
    for k, q in enumerate(gone):
        p.square('A', q, ORANGE, '#8a4a10', 2.0, label='M%d' % (k + 1))
    cells_panel(p, 'B', s, 'after the exchange: a k2 packing at the same side', hi=('BL00', 'BL01'))
    for q in keep:
        p.square('B', q, BLUE, '#1b4a77')
    for k, q in enumerate(pins):
        p.square('B', q, GREEN, '#1d5c33', 2.0, label=('BL00', 'BL01')[k])
    p.note(40, 492, [
        'Pi = {BL00, BL01} (the corner box and the wall slot up its wall) is met by exactly TWO '
        'squares in total, M1 = #%d and M2 = #%d: |M(Pi)| = 2 = |Pi|.' % (u[0], u[1]),
        'So the packing is NOT pair-stuck, and Lemma CELLS puts the two cells down as squares -- '
        'the corner pin (c,0,0) AND the slot pin (c,0,1): RAISE(0 -> 2).',
        'Panel A check: min wall gap %.2e, min pair gap %.2e (11 poses).   Panel B check: min wall '
        'gap %.2e, min pair gap %.2e (9 kept + 2 cell squares).' % (gwA, gpA, gwB, gpB),
        'Corpus: 0 of A244\'s 488 certified twelve-stuck packings and 0 of A217\'s 486 witnesses '
        'are pair-stuck or family-stuck (count250, exact in verify250).'])
    p.save(os.path.join(OUT, 'domino_exchange.svg'))
    return {'page': 'domino_exchange.svg', 's': s, 'meeters': u, 'panelA': [okA, gwA, gpA],
            'panelB': [okB, gwB, gpB]}


def page_count(count_json):
    lad = count_json['ladder']

    def look(reg, kmax, layer=None):
        for r in lad:
            if r['regime'] == reg and r['kmax'] == kmax and r.get('layer') == layer \
                    and not r.get('corner_only'):
                return r['n_min']
        return None
    s1, s2 = 3.877084, 4.2
    p = D.Page(1000, 660, 'A250 the family-stuck count')
    p.text(20, 26, 'A250 -- FAMILY-STUCK needs 13 squares at s >= 4 and 9 below 4 (exact, ILP over '
                   'the PROJECTION catalogue)', 15, '#111', weight='bold')
    p.text(20, 46, 'FAMILY-STUCK: every family Pi of pairwise disjoint border cells has |M(Pi)| > '
                   '|Pi| (else Lemma CELLS exchanges).  Which cells are disjoint depends on s.',
           10.5)
    p.panel('A', 40, 70, 330, 330, s1)
    p.panel('B', 400, 70, 330, 330, s2)
    cells_panel(p, 'A', s1, 's = 3.877084 = s-hat: 4 facing pairs OVERLAP', conflict=True)
    cells_panel(p, 'B', s2, 's = 4.2: all twelve cells are disjoint', conflict=True)
    p.note(40, 420, [
        'Below 4 the two facing slots of each wall overlap (red): the largest family is 8 cells '
        '(4 boxes + one slot per wall) and family-stuck needs >= 9 squares.',
        'At s >= 4 all twelve are disjoint: family-stuck needs >= 13 -- more than eleven.  So no '
        'packing of eleven unit squares at ANY side >= 4 is family-stuck,',
        'while A244 certifies 488 TWELVE-stuck ones from 4.000010 to 4.5 and A247\'s UPPER-END '
        'only reaches down to 4 + sqrt2.  The family window is [3.82, 4) alone.'], 10.0, 13)
    y = 490
    p.text(40, y, 'the count n_min (minimum squares an incidence structure needs), exact:', 11,
           '#111', weight='bold')
    rows = [('|Pi| <= 1  (A244 TWELVE-STUCK)', look('below4', 1), look('at4', 1)),
            ('|Pi| <= 2  (pairs / dominoes)', look('below4', 2), look('at4', 2)),
            ('|Pi| <= 3  (the brief\'s rows)', look('below4', 3), look('at4', 3)),
            ('|Pi| <= 4', look('below4', 4), look('at4', 4)),
            ('every family (FAMILY-STUCK)', look('below4', 12), look('at4', 12))]
    p.text(430, y + 16, 's in [3, 4)', 10, '#111', anchor='middle', mono=True)
    p.text(540, y + 16, 's >= 4', 10, '#111', anchor='middle', mono=True)
    for k, (nm, a, b) in enumerate(rows):
        yy = y + 32 + 15 * k
        p.text(40, yy, nm, 10, '#333', mono=True)
        p.text(430, yy, str(a), 10, '#111' if (a or 0) <= 11 else RED, anchor='middle', mono=True)
        p.text(540, yy, str(b), 10, '#111' if (b or 0) <= 11 else RED, anchor='middle', mono=True)
    p.text(600, y + 32 + 15 * 4, '13 > 11: dead at every side >= 4', 10, RED, mono=True)
    p.note(40, y + 32 + 15 * 5 + 8, [
        'Dependencies: Lemma CELLS [T], PROJECTION / MAX-FIVE [T, A247] (a square meets cells of '
        'ONE five-cell corner neighbourhood), NOT-SELF-SUFFICIENT [T, A246], TWO-FAR [T, A247].',
        'Adding SLOT-MET and A247\'s 62 certified pair kills (436 D4 images) leaves both numbers '
        'unchanged.  9 <= 11: the count does NOT close the window.'], 9.6, 12)
    p.save(os.path.join(OUT, 'count.svg'))
    return {'page': 'count.svg', 'table': rows}


def main():
    os.makedirs(OUT, exist_ok=True)
    cj = json.load(open(os.path.join(ATT, 'results', 'count250.json')))
    out = [page_exchange(), page_count(cj)]
    json.dump(out, open(os.path.join(ATT, 'results', 'pages250.json'), 'w'), indent=1)
    for o in out:
        print(o, flush=True)


if __name__ == '__main__':
    main()
