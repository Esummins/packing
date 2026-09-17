"""A249: results/chase249.jsonl + twotilted249_*.json + pocket249.json -> results/typet249.md,
typet249_summary.json.  Per type-T corner view: the touching class, T1-T3 predictions vs the
measured cells, the second suppliers of c01 / c10 by class, the domino / triple counts
(FAMILY-STUCK), the mutual wall pairs; for the locked FJ corners the holders; the tightest
corpus witness on the window side; the TWO-TILTED ladders and the pocket of the ring.
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')


def tclass(t):
    a, b = t['A_touch'], t['B_touch']
    return ('A:floor' if a['floor'] else 'A:none') + '|' + ('B:wall' if b['wall'] else 'B:none')


def views(rows, locked_only=False):
    for r in rows:
        for v in r['views']:
            if v.get('type') == 'T' and (not locked_only or (r['locked'] and r['locked'].get(v['corner']))):
                yield r, v


def stats(rows, locked_only=False):
    S = {'views': 0, 'touch': collections.Counter(), 'pred': collections.Counter(), 'sup01': collections.Counter(),
         'sup10': collections.Counter(), 'domino': collections.Counter(), 'own_inc': collections.Counter(),
         'reach': collections.Counter(), 'mutual_walls': 0, 'holders': collections.Counter(),
         'corner_holder_free': collections.Counter(), 'sides': []}
    for r, v in views(rows, locked_only):
        t = v['tt']
        S['views'] += 1
        S['sides'].append(r['s'])
        S['touch'][tclass(t)] += 1
        for k in ('A', 'B'):
            if 'pred_' + k in t:
                meas = {c: t['cells_' + k][c] > 1e-9 for c in ('c00', 'c01', 'c10')}
                near = min(abs(t['cells_' + k][c]) for c in meas) < 1e-6
                S['pred'][k + (':ok' if meas == t['pred_' + k] else ':touch-degenerate' if near else ':BAD')] += 1
        for c in t['c01_suppliers'].values():
            S['sup01'][c] += 1
        for c in t['c10_suppliers'].values():
            S['sup10'][c] += 1
        S['domino']['%d,%d,%d' % (v['domino_01'], v['domino_10'], v['triple'])] += 1
        own = sum(t['cells_A'][c] > 1e-9 for c in ('c01', 'c10')) + sum(t['cells_B'][c] > 1e-9 for c in ('c01', 'c10'))
        S['own_inc'][own] += 1
        S['reach']['B far %s, A far %s' % (t['B_reaches_far'], t['A_reaches_far'])] += 1
        S['mutual_walls'] += t['mutual_wall']
        if 'holder_classes' in t:
            hf = False
            for i, cl in t['holder_classes'].items():
                S['holders'][','.join(sorted(cl)) or 'none'] += 1
                hf |= 'free' in cl
            S['corner_holder_free'][hf] += 1
    S['sides'] = (min(S['sides']), max(S['sides'])) if S['sides'] else None
    return {k: (dict(v) if isinstance(v, collections.Counter) else v) for k, v in S.items()}


def tightest(rows):
    """the locked type-T corner views nearest the window: least side, with their parameters."""
    out = []
    for r, v in views(rows, True):
        t = v['tt']
        out.append({'rid': r['rid'], 'corner': v['corner'], 'wall': v['wall'], 's': r['s'], 'class': tclass(t),
                    'theta_A': t['theta_A'], 'delta_A': t['delta_A'], 'theta_B': t['theta_B'], 'delta_B': t['delta_B'],
                    'd_A': t['d_A'], 'd_B': t['d_B'], 'gap_AB': t['gap_AB'], 'B_far': t['B_reaches_far'], 'A_far': t['A_reaches_far'],
                    'domino': (v['domino_01'], v['domino_10'], v['triple'])})
    out.sort(key=lambda d: d['s'])
    return out[:6]


def main():
    rows = [json.loads(l) for l in open(os.path.join(RES, 'chase249.jsonl'), encoding='utf-8')]
    cor = [r for r in rows if not r['kind'].startswith('fj')]
    fj = [r for r in rows if r['kind'].startswith('fj')]
    S = {'corpus': stats(cor), 'fj_locked': stats(fj, True), 'tightest_locked': tightest(rows)}
    for mode in ('wall', 'ring2', 'ring'):
        fn = os.path.join(RES, 'twotilted249_%s.json' % mode)
        if os.path.exists(fn):
            d = json.load(open(fn, encoding='utf-8'))
            S['twotilted_' + mode] = {k: (v['result'] if mode == 'wall' else v['result']['sup_margin']) for k, v in sorted(d.items())}
            if mode == 'wall':
                S['twotilted_wall'] = {k: {sub: r['sup_margin'] for sub, r in v['result'].items()} for k, v in sorted(d.items())}
    fn = os.path.join(RES, 'pocket249.json')
    if os.path.exists(fn):
        d = json.load(open(fn, encoding='utf-8'))
        S['pocket'] = {k: {kk: vv for kk, vv in v.items() if kk != 'poses'} for k, v in d.items()}
    json.dump(S, open(os.path.join(RES, 'typet249_summary.json'), 'w', encoding='utf-8'), indent=1)
    write_md(S)


def write_md(S):
    c, f = S['corpus'], S['fj_locked']
    L = ['# A249 -- the type-T chase: corpus tests, the TWO-TILTED ladders, the ring and its pocket', '',
         'Code `chase249.py` / `twotilted249.py` / `pocket249.py` / `summarise249.py`; every corner is seen from each of its',
         'two walls (a VIEW: B = the meeter on that wall, A = the other); a corner is type T when both meeters are tilted.', '',
         '## 1. The 764 twelve-stuck packings: %d type-T views' % c['views'], '',
         '* touching classes (A floor / B wall): %s' % c['touch'],
         '* T1-T3 closed-form cells vs measured (touching meeters): %s' % c['pred'],
         '* second suppliers of c01: %s' % c['sup01'], '* second suppliers of c10: %s' % c['sup10'],
         '* own slot incidences per corner (k_c): %s; domino_01, domino_10, triple counts: %s' % (c['own_inc'], c['domino']),
         '* far reach (B up the wall / A along the floor): %s; mutual wall pairs: %d' % (c['reach'], c['mutual_walls']),
         '', '## 2. The genuine FJ points: %d LOCKED type-T views (sides %s)' % (f['views'], f['sides']), '',
         '* touching classes: %s' % f['touch'], '* T1-T3 vs measured: %s' % f['pred'],
         '* second suppliers of c01: %s; of c10: %s' % (f['sup01'], f['sup10']),
         '* own incidences: %s; domino / triple: %s' % (f['own_inc'], f['domino']),
         '* holders of the locked meeters (along + other holders, by class: meeter of a corner box / free square): %s' % f['holders'],
         '* locked corner views with at least one FREE (non-meeter) holder: %s' % f['corner_holder_free'],
         '* the tightest locked type-T corners (least side): %s' % json.dumps(S['tightest_locked'][:3]),
         '', '## 3. TWO-TILTED (sup SAT margin; > 0 = the configuration exists)', '']
    if 'twotilted_wall' in S:
        L.append('* the wall problem (B, A at c; B\', A\' at c\'; sub-case = who supplies c01 / c\'01): %s' % S['twotilted_wall'])
    for mode in ('ring2', 'ring'):
        if 'twotilted_' + mode in S:
            L.append('* the all-ADJ type-T ring (%s): %s' % ('C2-symmetric, 8 parameters' if mode == 'ring2' else '16 parameters', S['twotilted_' + mode]))
    if 'pocket' in S:
        L += ['', '## 4. The pocket of the ring (A237 census + direct search)', '']
        for k, v in S['pocket'].items():
            L.append('* %s: waste %.3f of %.3f; PIERCE(1) at the centre %.2e (capacity <= 1: %s); PIERCE(2) best %.2e; direct search 1/2/3 squares: %.3g / %.3g / %.3g; '
                     'a free square meeting both slots of the wall x = 0: margin %.3g' % (
                         k, v['waste'], v['pocket_area'], v['pierce1_centre'], v['capacity_le_1'], v['pierce2_best']['residual'],
                         v['pocket_1']['best_min_gap'], v['pocket_2']['best_min_gap'], v['pocket_3']['best_min_gap'], v['wall_poke']['best_margin']))
    with open(os.path.join(RES, 'typet249.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
