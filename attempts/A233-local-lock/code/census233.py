"""A233 -- the LOCAL lock census: the finite list of contact structures that decide whether the two meeters of one
corner are LOCKED (Lemma ROT / ROT-W read their own rows only -- LOCALITY), counted abstractly, against the
signatures actually realised on the witnesses (results/arm233.jsonl) and against A219's four-corner count.
    python census233.py     -> results/census233.md
Model (one arm, exactly two meeters A, B; local_lock.md s.3):
  * cells: A2 puts the two centres in distinct cells of the 2x2 grid at 1 (SW/NW/SE/NE); B1: no meeter touches
    both walls; a NW meeter can touch only the u-wall, SE only the v-wall (floor), NE neither, SW either one.
  * wall rows per meeter: none / one vertex on the wall / a flush edge (2 rows).
  * partner rows (shared): none / vertex-on-edge (1 row) / edge-to-edge (2 rows).
  * depth type per meeter (Lemma K): X, Y, D-vertex, D-edge, axis tie -- 5.
  * holders per meeter: h <= H squares in contact, each contributing 1 or 2 rows (vertex-on-edge / edge-edge);
    a holder may serve both meeters (its rows are counted at each); holder-holder contacts do NOT enter a
    meeter's certificate (that is LOCALITY) -- they enter the holders' own balance, which leaves the arm.
The count is of LABELLED row lists per meeter (what a Gordan certificate consumes), an upper bound on the
structures; the per-structure decision is a semi-algebraic feasibility question in the arm's poses.
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'arm233.jsonl')
OUT = os.path.join(ATT, 'results', 'census233.md')

WALL_OPTIONS = {'SW': 5, 'NW': 3, 'SE': 3, 'NE': 1}      # none | u vertex | u flush | v vertex | v flush (as allowed)
CELLS = ['SW', 'NW', 'SE', 'NE']
DEPTH_TYPES = 5
PARTNER = 3


def holder_lists(H):
    """multisets of h <= H holders with 1 or 2 rows each: sum_{h<=H} (h+1)."""
    return sum(h + 1 for h in range(H + 1))


def per_meeter(cell, H):
    return WALL_OPTIONS[cell] * DEPTH_TYPES * holder_lists(H)


def count(H):
    tot = 0
    for a in range(4):
        for b in range(a + 1, 4):
            tot += PARTNER * per_meeter(CELLS[a], H) * per_meeter(CELLS[b], H)
    return tot


def main():
    rs = [json.loads(l) for l in open(RES, encoding='utf-8')]
    hmax = max(len(m['holders']) for r in rs for m in r['members'])
    rmax = max(m['n_rows'] for r in rs for m in r['members'])
    L = ['# A233 -- the local lock census (one arm)', '',
         'Abstract count of labelled per-meeter row lists (cells x wall rows x depth type x partner rows x holder rows):', '']
    L.append('| H (holders per meeter) | row lists (2 meeters, one arm) | four independent arms (product / 8, s > 6.243) |')
    L.append('|---|---|---|')
    for H in (2, 3, 4, 5, 6):
        c = count(H)
        L.append('| %d | %s | %s |' % (H, format(c, ','), format(c ** 4 // 8, '.3g')))
    L.append('')
    L.append('Measured on the witnesses: holders per meeter max %d, rows per meeter (wall + pair rows) max %d; '
             '%d distinct realised signatures (cells | wall bits | partner | holders | cross-crowd holders) on %d corners.'
             % (hmax, rmax, len({r['signature'] for r in rs}), len(rs)))
    L.append('')
    L.append('Against A219 (`wall_torque.md` s.6): 2.6e11 four-corner structures with cross-corner holders, 2.3e6 CPU-days. '
             'The arm list at H = %d is %s per corner; the four arms are INDEPENDENT lists only for s > 2 + 3 sqrt2 = 6.243 '
             '(row partners), and even then the holders\' balance couples them through the chains (Corollary CHAIN, NOCRIT-SEL): '
             'the local list decides LOCKED, not the residue.' % (hmax, format(count(hmax), ',')))
    L.append('')
    # what the realised arm signatures say about wall bits and cells
    walls = collections.Counter()
    for r in rs:
        for m in r['members']:
            walls[(m['cell'], len(m['walls']))] += 1
    L.append('Realised (cell, wall-touching) per meeter: ' + ', '.join('%s:%d %d' % (k[0], k[1], v) for k, v in sorted(walls.items())) + '.')
    both_wall = sum(all(len(m['walls']) >= 1 for m in r['members']) for r in rs)
    L.append('Corners with every meeter wall-touching: %d / %d; with a meeter touching no wall: %d.' % (both_wall, len(rs), len(rs) - both_wall))
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
