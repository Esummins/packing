"""A246: every propagation inequality of the note on (i) the 282 corpus 12-stuck four-crowds
(A217's feasible crowds), (ii) A244's 34 certified 12-stuck candidates, (iii) A244's near-4
probe attempts that carry a pose (residual < 1e-3), (iv) fresh fixed-side attempts at s-hat and
3.95 through A244's probe (read-only import), to see which inequality a sub-4 attempt breaks.

    python check246.py [--fresh N]      -> results/construct246.jsonl + results/construct246.md
"""
import argparse
import collections
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import geom246 as G                                   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import cells244 as C                                  # noqa: E402

A217 = os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'results', 'search217_crowd0.jsonl')
A244 = os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'results')


def corpus_282():
    out = []
    for line in open(A217):
        r = json.loads(line)
        if 'z' not in r or r.get('min_pair_gap', -9) < -1e-9 or r.get('min_wall_gap', -9) < -1e-9:
            continue
        if C.stuck_report(r['z'])['twelve_stuck']:
            out.append((r['rid'], r['z'], 'packing'))
    return out


def certified_34():
    out = []
    for line in open(os.path.join(A244, 'twelve244.jsonl')):
        r = json.loads(line)
        if r.get('cert') and r.get('s_cert') and r.get('mode') == 'twelve':
            out.append((r['rid'], r['z'], 'certified'))
    return out


def near4():
    out = []
    for fn in ('probe244_below4.jsonl', 'probe244_ctrl4.jsonl'):
        p = os.path.join(A244, fn)
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            if 'z' in r and r.get('mode') == 'twelve':
                out.append((r['rid'], r['z'], 'attempt r=%.2e' % r['residual']))
    return out


def fresh(n, sides=(3.877084, 3.95), delta=1e-5, seed=246):
    import probe244 as P
    import feas244 as A
    from search244 import a217_seeds
    seeds = a217_seeds()
    rng = np.random.default_rng(seed)
    out = []
    for s in sides:
        best = None
        for k in range(n):
            rid, z0 = seeds[k % len(seeds)]
            r, wv, det = P.attempt(z0, A.CELLSETS['twelve'], delta, s, rng)
            if best is None or r < best[0]:
                best = (r, wv, det, rid)
        out.append(('fresh|s%.6f|%s' % (s, best[3]), [float(v) for v in best[1]],
                    'attempt r=%.2e (wall %.1e pair %.1e depth %.1e)' % (best[0], best[2][0], best[2][1], best[2][2])))
    return out


def summarise(rows, kind):
    R = [r for r in rows if r['kind'] == kind]
    if not R:
        return ['(none)']
    viol = collections.Counter()
    for r in R:
        rep = r['report']
        for key in ('A_two_corners', 'B_max_five', 'R_adj_reach', 'TWO_centre'):
            viol[key] += len(rep[key])
        viol['D_not_self_sufficient'] += sum(len(v) for v in rep['D_not_self_sufficient'].values())
        viol['F_type_f'] += sum(len(v) for v in rep['F_type_f'].values())
        if rep['twelve_stuck']:
            viol['count'] += (0 if rep['pattern']['demand_le_supply'] else 1) + (0 if rep['pattern']['free_inc_le_4f'] else 1)
    types = collections.Counter(r['report']['pattern']['types'] for r in R)
    fs = collections.Counter(r['report']['pattern']['free_squares'] for r in R)
    mc = collections.Counter(r['report']['max_cells'] for r in R)
    letters = collections.Counter()
    for r in R:
        for name, l in r['report']['pattern']['letters'].items():
            letters[l] += 1
    dem = collections.Counter(sum(r['report']['pattern']['outside_demand'].values()) for r in R)
    adj = collections.Counter(r['report']['pattern']['adj_inc'] for r in R)
    L = ['%d packings, sides %.6f .. %.6f; 12-stuck with depth > 1e-9: %d, > 1e-5: %d (the count inequalities are read on the latter)'
         % (len(R), min(r['s'] for r in R), max(r['s'] for r in R), sum(r['report']['twelve_stuck_1e-9'] for r in R),
            sum(r['report']['twelve_stuck'] for r in R)),
         'violations per lemma: ' + ', '.join('%s %d' % kv for kv in sorted(viol.items())),
         'corner types (BL BR TR TL): ' + ', '.join('%s %d' % kv for kv in types.most_common()),
         'free squares f = 11 - sum |M_c|: ' + ', '.join('%s: %d' % kv for kv in sorted(fs.items())),
         'max cells met by one square: ' + ', '.join('%s: %d' % kv for kv in sorted(mc.items())),
         'slot supply letters (over 8 slots each): ' + ', '.join('%s %d' % kv for kv in letters.most_common()),
         'total outside demand sum_c (4 - k_c): ' + ', '.join('%s: %d' % kv for kv in sorted(dem.items())),
         'ADJ incidences: ' + ', '.join('%s: %d' % kv for kv in sorted(adj.items()))]
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fresh', type=int, default=8)
    a = ap.parse_args()
    try:
        from search244 import belownormal
        belownormal()
    except Exception:
        pass
    t0 = time.time()
    items = corpus_282() + certified_34() + near4()
    if a.fresh > 0:
        items += fresh(a.fresh)
    rows = []
    for rid, z, kind in items:
        rep = G.check_all(z)
        rows.append({'rid': rid, 's': rep['s'], 'kind': kind.split()[0], 'note': kind, 'report': rep})
    os.makedirs(os.path.join(ATT, 'results'), exist_ok=True)
    with open(os.path.join(ATT, 'results', 'construct246.jsonl'), 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    L = ['# A246 -- the propagation inequalities on the corpus', '',
         'Generated by `code/check246.py` (%.0f s).  Every lemma of `docs/proofs/construct_towards.md` '
         'is a statement about PACKINGS, so the 12-stuck packings (all at s >= 4) must satisfy every one '
         'of them -- a violation would refute the lemma.  The attempts (not packings) show what a sub-4 '
         'candidate looks like against the same rules.' % (time.time() - t0), '']
    for kind, title in (('packing', '## 1. The 282 corpus 12-stuck four-crowds (A217 feasible crowds)'),
                        ('certified', '## 2. The 34 certified 12-stuck candidates (A244)'),
                        ('attempt', '## 3. A244 near-4 attempts with a pose (residual < 1e-3) and the fresh sub-4 attempts')):
        L += [title, ''] + ['- ' + t for t in summarise(rows, kind)] + ['']
    att = [r for r in rows if r['kind'] == 'attempt']
    if att:
        L += ['### 3a. The fresh attempts, one by one', '',
              '| rid | side | residual note | violations | types | f | demand | adj | free inc | max cells |', '|---|---|---|---|---|---|---|---|---|---|']
        for r in att:
            if not r['rid'].startswith('fresh'):
                continue
            p = r['report']['pattern']
            L.append('| %s | %.6f | %s | %d | %s | %d | %d | %d | %d | %d |' % (
                r['rid'], r['s'], r['note'], r['report']['violations'], p['types'], p['free_squares'],
                sum(p['outside_demand'].values()), p['adj_inc'], p['free_inc'], r['report']['max_cells']))
        L.append('')
    with open(os.path.join(ATT, 'results', 'construct246.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
