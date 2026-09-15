"""A222 results/swap222.md from swap222.jsonl (+ the RAISE tables of raise222*.md by reference).
    python summarise222.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROWS = os.path.join(ATT, 'results', 'swap222.jsonl')
MD = os.path.join(ATT, 'results', 'swap222.md')
CORNERS = ('BL', 'BR', 'TR', 'TL')
WALLS = ('BLBR', 'BRTR', 'TRTL', 'TLBL')


def main():
    rows = {}
    for l in open(ROWS, encoding='utf-8'):
        r = json.loads(l)
        rows[r['wid']] = r                      # the last row per witness
    rows = list(rows.values())
    n = len(rows)
    lines = ['# A222 exchange searches on the four-crowd witnesses (%d of 193 HELD + CROWD four-crowds; `swap222.jsonl`)' % n, '',
             'Per witness (side = the witness\'s own, 4.00-4.47): CORNER-SWAP per corner (X = the two meeters, S_c settled, one '
             'square placed in U(X) \\ int S_c); WALL-SWAP per wall (both corners settled, two squares placed); RING4 (X = the '
             'eight meeters, all four corners settled, four squares placed); RING1 (one corner settled, seven placed; implied by '
             'a successful corner swap); RING4X (X = the meeters + the non-meeters that meet a window-perimeter cell, all four '
             'settled).  Placement: exact c-space per tilt for one square, seeded greedy + penalty restarts otherwise; every '
             'placement exact-checked on the composed 11-square configuration (SAT gaps and wall rows >= -1e-9).  A "not found" '
             'is a heuristic verdict for k >= 2 squares; for one square it is exact up to the 1-degree tilt grid.', '']
    def cnt(pred):
        return sum(1 for r in rows if pred(r))
    corners_ok = [len(r['summary']['corners_swappable']) for r in rows]
    lines += ['| search | witnesses where it succeeds | notes |', '|---|---|---|',
              '| CORNER-SWAP at >= 1 corner | %d / %d | corners swappable per witness: 4: %d, 3: %d, 2: %d, 1: %d, 0: %d |' % (
                  cnt(lambda r: corners_ok[rows.index(r)] >= 1), n, *[corners_ok.count(k) for k in (4, 3, 2, 1, 0)]),
              '| CORNER-SWAP at all four corners | %d / %d | |' % (corners_ok.count(4), n),
              '| WALL-SWAP at >= 1 wall | %d / %d | walls per witness: 4: %d, 3: %d, 2: %d, 1: %d, 0: %d |' % (
                  cnt(lambda r: len(r['summary']['walls_swappable']) >= 1), n,
                  *[sum(1 for r in rows if len(r['summary']['walls_swappable']) == k) for k in (4, 3, 2, 1, 0)]),
              '| RING4 (all four settled) | %d / %d | fails: %d (band squares placed 3: %d, 2: %d, <= 1: %d) |' % (
                  cnt(lambda r: r['summary']['ring4']), n, cnt(lambda r: not r['summary']['ring4']),
                  *[sum(1 for r in rows if not r['summary']['ring4'] and r['searches']['ring4'].get('k_max_greedy', 0) == k) for k in (3, 2)],
                  sum(1 for r in rows if not r['summary']['ring4'] and r['searches']['ring4'].get('k_max_greedy', 0) <= 1)),
              '| RING1 (>= 1 corner settled, ring re-packed) | %d / %d | all four corners: %d |' % (
                  cnt(lambda r: len(r['summary']['ring1']) >= 1), n, cnt(lambda r: len(r['summary']['ring1']) == 4)),
              '| RING4X (intruders moved too) | %d / %d | intruders per witness: 0: %d, 1: %d, 2: %d, >= 3: %d |' % (
                  cnt(lambda r: r['summary']['ring4x']), n, *[sum(1 for r in rows if len(r['intruders']) == k) for k in (0, 1, 2)],
                  sum(1 for r in rows if len(r['intruders']) >= 3)),
              '| RING4 or RING4X | %d / %d | |' % (cnt(lambda r: r['summary']['ring4'] or r['summary']['ring4x']), n),
              '| any exchange with >= 1 settled corner | %d / %d | (corner, ring1, ring4, ring4x) |' % (
                  cnt(lambda r: r['summary']['ring1'] or r['summary']['ring4'] or r['summary']['ring4x'] or r['summary']['corners_swappable']), n)]
    # what blocks a corner swap
    blk = {}
    for r in rows:
        for c in CORNERS:
            sr = r['searches']['corner_' + c]
            if not sr['found']:
                blk[len(sr['hull_intruders'])] = blk.get(len(sr['hull_intruders']), 0) + 1
    lines += ['', 'Blocked corner swaps: %d of %d corners; non-X squares cutting the hull of the two meeters: %s (0 = the '
              'remainders themselves are too thin: the two meeters cover the box and their outer parts hold no unit square '
              'without the free space).' % (sum(blk.values()), 4 * n, dict(sorted(blk.items())))]
    ring = [r for r in rows if r['rid'] == 'rand_0_0569|t20']
    if ring:
        r = ring[0]
        lines += ['', '## The ring rand_0_0569|t20 (side %.4f, %.0f s)' % (r['s'], r['secs'])]
        for k, v in r['searches'].items():
            lines.append('* %s: X = %s, settled %s, place %d: %s (%s, %.2f s; non-X squares in the hull of X: %s)' % (
                k, v['X'], v['settled'], v['k'], 'FOUND' if v['found'] else 'not found (%d placed)' % v.get('k_max_greedy', 0),
                v['method'], v['secs'], v['hull_intruders']))
    lines += ['', 'Sides: %.4f - %.4f; wall time %.0f s total.' % (min(r['s'] for r in rows), max(r['s'] for r in rows), sum(r['secs'] for r in rows)),
              'RAISE (Lemma CELLS on census cells): `raise222_kept.md` (486 kept witnesses) and `raise222.md` (every search row).']
    open(MD, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:24]))


if __name__ == '__main__':
    main()
