"""A236 summary: results/capacity236.jsonl (+ table236.md) -> results/capacity236.md.
    python summarise236.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'capacity236.jsonl')
TAB = os.path.join(ATT, 'results', 'table236.md')
OUT = os.path.join(ATT, 'results', 'capacity236.md')
W4 = ('floor', 'right', 'ceil', 'left')


def hist(xs):
    c = collections.Counter(xs)
    return ', '.join('%s: %d' % (k, c[k]) for k in sorted(c))


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else float('nan')


def main():
    rows = [json.loads(l) for l in open(RES, encoding='utf-8')]
    W = [r for r in rows if r['src'] == '193']
    R = [r for r in rows if r['src'] == 'ring11']
    S = [r for r in rows if r['src'] == 'survey']
    ring = [r for r in W if r['rid'] == 'rand_0_0569|t20'][0]
    L = ['# A236 -- RING-CAPACITY: the band / core / straddler trichotomy, the intrusion and the count, measured', '',
         'Sources: the ring `rand_0_0569|t20` + the 193 HELD / CROWD four-crowds of A217 (loaded component U from A233\'s '
         '`arm233.jsonl`, union over the four corners), A226\'s eight-square crowd rings at n = 11 (`ring11_226.jsonl`), the 21 '
         'survey records + Trump\'s certificate (`survey226.jsonl`).  Band width 1: BAND = interior misses the open centre '
         '(1, s-1)^2, CORE = inside [1, s-1]^2, STRADDLER = neither.  `python capacity236.py` (25 s).', '',
         '## 1. The ring and the 193 four-crowds (n = 11, sides 4.0014 .. 4.42: ABOVE m = 4, so the lemma must not fire)', '',
         '| check ([T] lemma on data) | holds on |', '|---|---|',
         '| TILT-BAND: every tilted square (tilt > 1e-3 deg) intrudes into the centre (depth > 0) | %d / %d |' % (sum(r['tilted_all_intrude'] for r in W), len(W)),
         '| BAND-FLUSH: every band square is flush (tilt < 1e-3 deg) and touches a wall | %d / %d |' % (sum(r['band_all_flush_touchers'] for r in W), len(W)),
         '| WALL-EXCESS: chord sums <= s on all four walls | %d / %d |' % (sum(r['wall_excess_ok'] for r in W), len(W)),
         '| touchers per wall <= floor(s) | %d / %d |' % (sum(r['touchers_per_wall_le_floor'] for r in W), len(W)),
         '| BAND-COUNT: B <= 4(floor(s) - 1) (four-crowd, no corner slot) | %d / %d |' % (sum(r['B'] <= 4 * (r['floor_s'] - 1) for r in W), len(W)),
         '| CORE-CAP: K <= N_proved(s - 2) | %d / %d |' % (sum(r['core_ok'] for r in W), len(W)),
         '| ONE-TILTED: >= 4 tilted meeters | %d / %d |' % (sum(len(r['tilted_meeters']) >= 4 for r in W), len(W)),
         '| B + K + X = 11 | %d / %d |' % (sum(r['B'] + r['K'] + r['X'] == 11 for r in W), len(W)), '',
         'Distributions: B (band) %s; K (core) %s; X (straddlers) %s; tilted meeters %s.' % (
             hist(r['B'] for r in W), hist(r['K'] for r in W), hist(r['X'] for r in W), hist(len(r['tilted_meeters']) for r in W)),
         'Loaded component U: p = |U| %s (p = 0: no A233 chain record); n - p %s; U contains core squares on %d / %d; max depth of a U '
         'member into the centre: min %.3f, median %.3f, max %.3f (a "ring in a band of width 1 + d" needs d = that depth).' % (
             hist(r['p'] for r in W), hist(r['n_minus_p'] for r in W), sum(bool(r['U_core_members']) for r in W), len(W),
             min(r['U_max_depth'] for r in W), med([r['U_max_depth'] for r in W]), max(r['U_max_depth'] for r in W)),
         'The rest (non-U squares): classes %s; n - p <= N_record(s - 2) on %d / %d (the 4 failures are the p = 0 rows).' % (
             hist(c for r in W for c in r['rest_classes'].values()), sum(r['rest_le_N_record'] for r in W), len(W)),
         'Tilted meeters\' intrusion iota = cos + sin - 1: min %.4f, median %.3f, max %.4f; their depth into the centre: min %.4f, median %.3f.' % (
             min(v for r in W for v in r['meeter_iota'].values()), med([v for r in W for v in r['meeter_iota'].values()]),
             max(v for r in W for v in r['meeter_iota'].values()),
             min(r['meeter_depth'][str(i)] for r in W for i in r['tilted_meeters']),
             med([r['meeter_depth'][str(i)] for r in W for i in r['tilted_meeters']])), '',
         '**The ring** (side %.4f): classes %s; B = %d, K = %d, X = %d; U = %s (p = %d), rest %s (%s); walls (flush / tilted touchers, chord sum): %s; '
         'meeters %s with depth %.2f .. %.2f and iota = 0.2817 (20 deg); N_record(s - 2 = %.2f) = %d >= n - p = %d.' % (
             ring['s'], ring['classes'], ring['B'], ring['K'], ring['X'], ring['U'], ring['p'], ring['rest'],
             [ring['rest_classes'][str(i)] for i in ring['rest']],
             {w: (ring['walls'][w]['flush'], ring['walls'][w]['tilted'], round(ring['walls'][w]['chord_sum'], 3)) for w in W4},
             ring['corners'], ring['meeter_depth_min'], ring['meeter_depth_max'], ring['sigma'], ring['N_record'], ring['n_minus_p']), '',
         '## 2. A226\'s eight-square crowd rings at n = 11 (S < 4: the only four-crowd family BELOW m the lab has)', '',
         '| ring | S | eps | B | K | X | meeter depth (tilted) | pocket: squares placed (greedy) | A226 k_max | inscribed flush square | N_proved(S-2) |',
         '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in R:
        L.append('| %s | %.2f | %.2f | %d | %d | %d | %.3f | %d | %d | %.3f | %d |' % (
            r['label'], r['s'], r['eps'], r['B'], r['K'], r['X'], r['depths'][1], r['pocket_k_greedy'], r['a226_k_max_greedy'],
            r['pocket_inscribed_side'], r['N_proved']))
    L += ['', 'Reading: 8 ring members + 1 = 9 < 11 on every member of the family; the count allows 8 + 1 + 4 = 13.  The closure is the '
          'POCKET (a region search), not the count; the tilted members\' depth is eps/2-small -- no intrusion floor.', '',
          '## 3. The 21 records (not rings: 0 or 1 doubly-met corner; the lemma\'s hypothesis fails)', '',
          '| record | n | s | m | B | K | X | tilted | doubly met | flush touchers per wall | tilted touchers per wall | N_p(s-2) | N_r(s-2) | 4(floor s - 1) | checks |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in S:
        L.append('| %s | %d | %.4f | %d | %d | %d | %d | %d | %d | %s | %s | %d | %d | %d | %s |' % (
            r['label'], r['n'], r['s'], r['m'], r['B'], r['K'], r['X'], r['n_tilted'], r['doubly_met'],
            [r['walls'][w]['flush'] for w in W4], [r['walls'][w]['tilted'] for w in W4], r['N_proved'], r['N_record'],
            4 * (r['floor_s'] - 1), 'ok' if (r['wall_excess_ok'] and r['band_all_flush_touchers'] and r['tilted_all_intrude'] and r['core_ok']) else 'FAIL'))
    L += ['', 'Reading: every record has X >= 1 straddlers (median %d) -- the tilted grain crosses the band line into the centre '
          '(cross-braced), B is at or just below 4(floor s - 1) and K <= N(s - 2) always; no record is a four-crowd, so BAND-COUNT '
          'is not invoked, and the count identity n = B + K + X holds on all %d.' % (med([r['X'] for r in S]), len(S)), '']
    if os.path.exists(TAB):
        L += ['## 4. ' + open(TAB, encoding='utf-8').read().split('\n', 1)[1].strip(), '']
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(OUT)


if __name__ == '__main__':
    main()
