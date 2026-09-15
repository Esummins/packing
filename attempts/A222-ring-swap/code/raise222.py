"""A222 RAISE test on every A217 witness (all search files, deduplicated as collect217 does; the 486 kept
witnesses carry their wid): for each packing, the deficiency d(Pi) = |M(Pi)| - |Pi| over every family of
pairwise disjoint census cells containing a corner, the corner + adjacent-cell pairs, and the sweep.
    python raise222.py [--kept]     -> results/raise222.jsonl, results/raise222.md
Classes: SETTLED (a slot square present: RAISE trivial, reported apart), K0FREE / BOXK0 (genuine k0 FJ
points), HELD, CROWD.  Verdict per witness: K0FREE-corner (a corner met by <= 1: RAISE(0->1) by teleport),
RAISE2 (a family of >= 2 cells with d <= 0), RAISE1 (a family with d <= 0, corner only), NONE (d >= 1).
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
import collect217 as K        # noqa: E402
import geom217 as G           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'raise222.jsonl')
MD = os.path.join(ATT, 'results', 'raise222.md')
WIT = os.path.join(ATT, '..', 'A217-torque-probe', 'results', 'witnesses217.jsonl')


def load(kept_only):
    kept = {}
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        kept[w['rid']] = w
    if kept_only:
        return list(kept.values())
    ws = K.load_witnesses()
    for w in ws:
        w['wid'] = kept[w['rid']]['wid'] if w['rid'] in kept else None
        w['n2'] = sum(1 for c, m in w['meeters'].items() if w['settled'][c] is None and len(m) >= 2)
    return ws


def analyse(w):
    z = np.array(w['z'], float)
    s = float(z[G.S_IDX])
    cells = C.cells_at(s)
    masks = C.meeter_masks(z, cells)
    corner_M = {c['name']: bin(masks[k]).count('1') for k, c in enumerate(cells) if c['is_corner']}
    best, per_size, nfam = C.min_deficiency(cells, masks)
    pairs = C.pair_families(cells, masks)
    sw, allsw = C.best_sweep(z)
    # the window-shaped 8-cell family (the count of S < 4) as a sweep at every side
    win = C.window_family(s)
    byname = {c['name']: k for k, c in enumerate(cells)}
    wmask, wnames = 0, []
    for (c, i, j) in win:
        nm = '%s(%d,%d)' % (c, i, j)
        if nm in byname:
            wmask |= masks[byname[nm]]
            wnames.append(nm)
    d_window = bin(wmask).count('1') - len(wnames)
    wbest, wper, _ = C.window_deficiency(cells, masks)
    wsw, wall = C.best_sweep(z, window=True)
    settled = any(v is not None for v in w['settled'].values())
    if settled:
        verdict = 'SETTLED'
    elif min(corner_M.values()) <= 1:
        verdict = 'K0FREE-corner'
    elif best['d'] <= 0 and len(best['family']) >= 2:
        verdict = 'RAISE2'
    elif best['d'] <= 0:
        verdict = 'RAISE1'
    else:
        verdict = 'NONE'
    two_indep = sum(1 for p in pairs if p['independent'])
    return {'wid': w.get('wid'), 'rid': w['rid'], 'cls': w['cls'], 's': s, 'n2': w['n2'], 'verdict': verdict,
            'corner_meeters': corner_M, 'd_min': best['d'], 'best_family': best['family'],
            'best_M': [q for q in range(G.N) if (best.get('M', 0) >> q) & 1],
            'd_by_size': {str(k): v['d'] for k, v in sorted(per_size.items())},
            'n_families': nfam, 'pairs': pairs, 'n_independent_pairs': two_indep,
            'sweep': {'start': sw['start'], 'clockwise': sw['clockwise'], 'success_at': sw['success_at'],
                      'h_final': sw['h_final'], 'steps': sw['steps']},
            'sweeps_succeeding': sum(1 for r in allsw if r['success_at'] is not None),
            'window8': {'cells': wnames, 'M': bin(wmask).count('1'), 'd': d_window, 'd_min': wbest['d'],
                        'best_family': wbest['family'], 'd_by_size': {str(k): v['d'] for k, v in sorted(wper.items())},
                        'sweep_success_at': wsw['success_at'], 'sweep_h_final': wsw['h_final'],
                        'sweeps_succeeding': sum(1 for r in wall if r['success_at'] is not None),
                        'sweep_steps': wsw['steps'], 'sweep_start': wsw['start'], 'sweep_cw': wsw['clockwise']},
            'min_size_raise': min([k for k, v in per_size.items() if v['d'] <= 0] or [0])}


def main():
    kept = '--kept' in sys.argv
    global OUT, MD
    if kept:
        OUT, MD = OUT.replace('raise222.jsonl', 'raise222_kept.jsonl'), MD.replace('raise222.md', 'raise222_kept.md')
    ws = load(kept)
    t0 = time.time()
    rows = []
    with open(OUT, 'w', encoding='utf-8') as f:
        for w in ws:
            r = analyse(w)
            rows.append(r)
            f.write(json.dumps(r) + '\n')
    dt = time.time() - t0
    # summary
    lines = ['# A222 RAISE test on A217\'s witnesses (%d packings, %.0f s; `raise222.jsonl`)' % (len(rows), dt), '',
             'd(Pi) = |M(Pi)| - |Pi| minimised over every family Pi of pairwise disjoint census cells (offsets <= 2, all '
             'four frames) containing a corner; d <= 0 is Lemma CELLS: the packing exchanges into one with all of Pi '
             'settled.  "K0FREE-corner": a corner box met by <= 1 square (K0-FREE teleports).  "window8": the 8-cell '
             'window-shaped perimeter (one middle per wall) at the witness\'s own side.', '',
             '| class | n | sides | SETTLED | K0FREE-corner | RAISE2 | RAISE1 | NONE | smallest under-met family: '
             'size 1 / 2 / 3 / >= 4 | window8 sub-family d_min <= 0 / = 1 / >= 2 | window8 sweep succeeds | '
             '>= 1 independent pair |', '|' + '---|' * 12]
    for cls in ('SETTLED', 'K0FREE', 'BOXK0', 'HELD', 'CROWD'):
        R = [r for r in rows if r['cls'] == cls]
        if not R:
            continue
        v = {k: sum(1 for r in R if r['verdict'] == k) for k in ('SETTLED', 'K0FREE-corner', 'RAISE2', 'RAISE1', 'NONE')}
        ms = [r['min_size_raise'] for r in R]
        dw = [r['window8']['d_min'] for r in R]
        lines.append('| %s | %d | %.4f - %.4f | %d | %d | %d | %d | %d | %d / %d / %d / %d | %d / %d / %d | %d | %d |' % (
            cls, len(R), min(r['s'] for r in R), max(r['s'] for r in R), v['SETTLED'], v['K0FREE-corner'], v['RAISE2'],
            v['RAISE1'], v['NONE'], sum(1 for d in ms if d == 1), sum(1 for d in ms if d == 2),
            sum(1 for d in ms if d == 3), sum(1 for d in ms if d >= 4), sum(1 for d in dw if d <= 0),
            sum(1 for d in dw if d == 1), sum(1 for d in dw if d >= 2),
            sum(1 for r in R if r['window8']['sweep_success_at'] is not None),
            sum(1 for r in R if r['n_independent_pairs'] > 0)))
    four = [r for r in rows if r['n2'] == 4 and r['cls'] in ('HELD', 'CROWD')]
    lines += ['', '## Four-crowds (n2 = 4, HELD + CROWD): %d' % len(four),
              'verdicts: ' + ', '.join('%s %d' % (k, sum(1 for r in four if r['verdict'] == k))
                                       for k in ('K0FREE-corner', 'RAISE2', 'RAISE1', 'NONE')),
              'd_min distribution: ' + ', '.join('%d: %d' % (d, sum(1 for r in four if r['d_min'] == d))
                                                 for d in sorted(set(r['d_min'] for r in four))),
              'window8 full-family d: ' + ', '.join('%d: %d' % (d, sum(1 for r in four if r['window8']['d'] == d))
                                                    for d in sorted(set(r['window8']['d'] for r in four))),
              'window8 sub-family d_min: ' + ', '.join('%d: %d' % (d, sum(1 for r in four if r['window8']['d_min'] == d))
                                                       for d in sorted(set(r['window8']['d_min'] for r in four))),
              'window8 sweeps succeeding (of 8 starts) per witness: ' + ', '.join(
                  '%d: %d' % (k, sum(1 for r in four if r['window8']['sweeps_succeeding'] == k)) for k in range(9)),
              'sweeps succeeding (of 8 starts) per witness: ' + ', '.join(
                  '%d: %d' % (k, sum(1 for r in four if r['sweeps_succeeding'] == k)) for k in range(9))]
    ring = [r for r in rows if r['rid'] == 'rand_0_0569|t20']
    if ring:
        r = ring[0]
        lines += ['', '## The ring rand_0_0569|t20 (side %.4f)' % r['s'], 'corner meeters: %s' % r['corner_meeters'],
                  'd_min = %d at %s (M = %s); by size: %s' % (r['d_min'], r['best_family'], r['best_M'], r['d_by_size']),
                  'window8: %s, |M| = %d, d = %d' % (r['window8']['cells'], r['window8']['M'], r['window8']['d']),
                  'sweep from %s%s: %s' % (r['sweep']['start'], ' (cw)' if r['sweep']['clockwise'] else '',
                                           'nothing in hand at step %s' % r['sweep']['success_at'] if r['sweep']['success_at']
                                           else 'h_final = %d' % r['sweep']['h_final'])]
        for st in r['sweep']['steps']:
            lines.append('  step %d %s: M = %s, %s, in hand %d' % (st['k'], st['cell'], st['M'], st['action'], st['h']))
        w8 = r['window8']
        lines.append('window8 sub-family d_min = %d at %s; by size %s; window sweep from %s%s: %s' % (
            w8['d_min'], w8['best_family'], w8['d_by_size'], w8['sweep_start'], ' (cw)' if w8['sweep_cw'] else '',
            'nothing in hand at step %s' % w8['sweep_success_at'] if w8['sweep_success_at']
            else 'h_final = %d' % w8['sweep_h_final']))
        for st in w8['sweep_steps']:
            lines.append('  step %d %s: M = %s, %s, in hand %d' % (st['k'], st['cell'], st['M'], st['action'], st['h']))
    open(MD, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
