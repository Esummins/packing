"""A223 tables: results/grains223.jsonl (the grain census of every four-crowd, Lemma TWO-GRAIN's measured
clauses) and results/click223.md from results/click223.jsonl (the click on the ring and the 193).
    python summarise223.py
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grains223 as GR        # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')


def census():
    out = os.path.join(RES, 'grains223.jsonl')
    rows = []
    with open(out, 'w', encoding='utf-8') as f:
        for w in GR.four_crowds():
            g = GR.grains(w)
            g.pop('hand')
            g.pop('tilts_deg')
            gl = GR.grains(w, 'load')
            g['n_grains_tilted_by_load'] = gl['n_grains_tilted']
            f.write(json.dumps(g) + '\n')
            rows.append(g)
    return rows


def pct(a, b):
    return '%d / %d' % (a, b)


def main():
    gr = census()
    ck = [json.loads(l) for l in open(os.path.join(RES, 'click223.jsonl'), encoding='utf-8')]
    seen, rows = set(), []
    for r in ck:
        if r['wid'] not in seen:
            seen.add(r['wid'])
            rows.append(r)
    L = ['# A223 -- grains and the click on the ring and the %d four-crowd witnesses (`grains223.jsonl`, `click223.jsonl`)' % len(rows), '',
         'Witnesses: A217\'s HELD (8) and CROWD (185) four-crowds (every corner box met by two squares) at their own sides 4.00-4.47.',
         'Grains: connected components of the geometric contact graph among the LOADED squares (bounded FJ stress, A219 rows) within one',
         'handedness class (theta mod 90 in (0,45) = \'+\', (45,90) = \'-\', 45 = diamond, flat).  Click: every tilted square rotates toward',
         'its nearest axis (\'+\' -> 0, \'-\' -> 90) along t in [0,1] (20 steps), the side minimised over the centres at each step by the',
         'alternating separating-axis LP; A = the witness\'s contact axes kept (the lean contacts slide), B = every axis re-selected,',
         'C = A on the loaded squares only, the rattlers re-fitted flat at the end.', '',
         '## 1. Lemma TWO-GRAIN, measured', '']
    n = len(gr)
    both = sum(1 for g in gr if g['hands_present'] == ['+', '-'])
    one = sum(1 for g in gr if len(g['hands_present']) == 1)
    allc = sum(1 for g in gr if g['one_grain_meets_all_corners'])
    walls4 = sum(1 for g in gr if len(g['walls_covered']) == 4)
    lean = sum(1 for g in gr if g['n_lean'] >= 1)
    flatbd = sum(1 for g in gr if g['n_flat_bd'] >= 1)
    ng = collections.Counter(g['n_grains_tilted'] for g in gr)
    ngl = collections.Counter(g['n_grains_tilted_by_load'] for g in gr)
    ch = collections.Counter(tuple(sorted(set(sum((v for v in g['corner_hands'].values()), [])))) for g in gr)
    L += ['| clause | count |', '|---|---|',
          '| both handedness classes present among the loaded tilted squares | %s |' % pct(both, n),
          '| a single handedness class only | %s |' % pct(one, n),
          '| some grain meets ALL FOUR corners | %s |' % pct(allc, n),
          '| the grains\' wall contacts cover all four walls | %s |' % pct(walls4, n),
          '| >= 1 LEAN boundary (loaded contact between opposite-handed tilted squares) | %s |' % pct(lean, n),
          '| >= 1 boundary through a flat square | %s |' % pct(flatbd, n),
          '| number of tilted grains (contact adjacency) | %s |' % dict(sorted(ng.items())),
          '| number of tilted grains (loaded-row adjacency) | %s |' % dict(sorted(ngl.items())),
          '| handedness classes among the corner meeters (all corners pooled) | %s |' % {'/'.join(k): v for k, v in ch.items()}, '']
    L += ['## 2. The click', '']
    A_ok = [r for r in rows if r['A']['blocked_at'] is None]
    A_mono = [r for r in A_ok if r['A']['monotone']]
    A_end4 = [r for r in A_ok if abs(r['A']['s_end'] - 4.0) < 1e-6]
    B_ok = [r for r in rows if r['B']['blocked_at'] is None]
    B_mono = [r for r in B_ok if r['B']['monotone']]
    B_end4 = [r for r in B_ok if abs(r['B']['s_end'] - 4.0) < 1e-6]
    C = [r for r in rows if 'C' in r]
    C_ok = [r for r in C if r['C']['blocked_at'] is None]
    C_refit = [r for r in C_ok if r['C'].get('refit', {}).get('found')]
    up = sorted(((r['A']['max_uptick'], r['wid']) for r in A_ok if not r['A']['monotone']), reverse=True)[:5]
    L += ['| variant | reaches the flush end | end side = 4.000 | side non-increasing at every step | blocked |', '|---|---|---|---|---|',
          '| A click (contact axes kept) | %s | %s | %s | %d |' % (pct(len(A_ok), len(rows)), pct(len(A_end4), len(A_ok)), pct(len(A_mono), len(A_ok)), len(rows) - len(A_ok)),
          '| B free (axes re-selected) | %s | %s | %s | %d |' % (pct(len(B_ok), len(rows)), pct(len(B_end4), len(B_ok)), pct(len(B_mono), len(B_ok)), len(rows) - len(B_ok)),
          '| C loaded core only (%d witnesses with rattlers) | %s | rattlers re-fitted flat at the end: %s | -- | %d |' % (len(C), pct(len(C_ok), len(C)), pct(len(C_refit), len(C_ok)), len(C) - len(C_ok)), '',
          'Largest upticks of variant A (side increase between consecutive steps): %s' % ', '.join('%s %.1e' % (w, u) for u, w in up), '']
    blocked = [r for r in rows if r['A']['blocked_at'] is not None]
    if blocked:
        L += ['Blocked clicks (variant A): ' + '; '.join('%s at t=%s blockers %s' % (r['wid'], r['A']['blocked_at'], r['A']['blockers']) for r in blocked[:12]), '']
    ring = [r for r in rows if r['rid'] == GR.RING]
    if ring:
        r = ring[0]
        L += ['## 3. The ring rand_0_0569|t20', '',
              'A: side along t = %s' % r['A']['s'], '', 'contacts kept at each step: %s of %d' % (r['A']['contacts_kept'], r['A']['n_fixed_contacts']),
              '', 'B: %s' % r['B']['s'], '', 'C (core %s, rattlers %s): %s; refit %s' % ([i for i in range(11) if i not in r['rattlers']], r['rattlers'], r['C']['s'] if 'C' in r else None, r.get('C', {}).get('refit')), '']
    L += ['Resume block:', '    cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1',
          '    python attempts/A223-two-grains/code/click223.py --resume     # rows are appended and committed',
          '    python attempts/A223-two-grains/code/summarise223.py; python attempts/A223-two-grains/code/pages223.py']
    open(os.path.join(RES, 'click223.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:40]))


if __name__ == '__main__':
    main()
