"""A234 -- results/hand234.md from results/hand234.jsonl: the census, TORQUE-ID's residuals, the per-class statistics
of every candidate, the separation test (FOUR = the four-crowds vs the free FJ points and the optima), Trump and the
ring line by line.
    python summarise234.py
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'hand234.jsonl')
OUT = os.path.join(ATT, 'results', 'hand234.md')
RING = 'w364_held'


def load():
    return [json.loads(l) for l in open(RES, encoding='utf-8')]


def group_of(r):
    if r['cls'] in ('TRUMP', 'S02', 'S07', 'RECORD'):
        return 'OPT'
    if r['name'].startswith('fj_'):
        return 'FJ'
    if r['four_crowd']:
        return 'FOUR'
    return 'W3'


def scalars(r):
    a, b, c, w = r['cand_a'], r['cand_b'], r['cand_c'], r['walls']
    return {
        'flips': a['flips'], 'mixed_walls': a['mixed_walls'], 'n_tilted_touchers': a['n_tilted_touchers'],
        'load_imbalance': abs(a['plus_load'] - a['minus_load']),
        'demand': b['demand'], 'supply_alongwall': b['supply_alongwall'], 'supply_interior': b['supply_interior'],
        'supply_ext': b['supply_ext'], 'ext_share': abs(b['supply_ext']) / b['demand'] if b['demand'] > 1e-9 else 0.0,
        '|C|': abs(c['C']), 'ratio_C_bound': c['ratio'] or 0.0, '|S_tilted|': abs(c['S_tilted']), '|F_flat|': abs(c['F_flat']),
        '|S_meet|': abs(c['S_meet']), 'S_tilted_span': (r['ranges']['S_tilted'][1] - r['ranges']['S_tilted'][0]) if r['ranges']['S_tilted'] else 0.0,
        'C_span': (r['ranges']['C'][1] - r['ranges']['C'][0]) if r['ranges']['C'] else 0.0,
        'ext_load': r['ext_load'],
        'P_max_wall': max(x['P'] for x in w.values()), 'n_loaded_walls': sum(x['P'] > 1e-7 for x in w.values()),
    }


def fmt(v):
    return '%.4f' % v if isinstance(v, float) else str(v)


def rng(vals):
    return '[%s, %s] med %s' % (fmt(min(vals)), fmt(max(vals)), fmt(float(np.median(vals)))) if vals else '-'


def main():
    rs = load()
    L = []
    with_stress = [r for r in rs if r['has_stress']]
    L.append('# A234 -- the handedness probe: census, TORQUE-ID, the three candidate counts, the separation test\n')
    L.append('Witnesses: %d (with a bounded FJ stress: %d).  Groups: OPT = Trump, S02, S07, the survey records n = 5..55; '
             'FJ = A217\'s genuine free FJ points; FOUR = the four-crowds (HELD / CROWD, external rows loaded); W3 = the other '
             'A217 witnesses (<= 3 crowds, external rows allowed).' % (len(rs), len(with_stress)))
    by = {}
    for r in rs:
        by.setdefault(group_of(r), []).append(r)
    L.append('\n| group | witnesses | with stress | n2 = 0 / 1 / 2 / 3 / 4 | ext load > 0 |\n|---|---|---|---|---|')
    for g in ('OPT', 'FJ', 'W3', 'FOUR'):
        v = by.get(g, [])
        n2 = [sum(r['n2'] == k for r in v) for k in range(5)]
        L.append('| %s | %d | %d | %s | %d |' % (g, len(v), sum(r['has_stress'] for r in v), ' / '.join(map(str, n2)),
                                                sum(r.get('ext_load', 0) > 1e-7 for r in v)))
    no = [r['name'] for r in rs if not r['has_stress']]
    L.append('\nNo stress (LP infeasible at the row tolerance): %s' % (', '.join(no) if no else 'none'))
    # identities
    res = [abs(r['torque_id']['residual']) for r in with_stress]
    cres = [abs(a['residual']) for r in with_stress for a in r['corners'].values()]
    L.append('\n## TORQUE-ID [T], measured\n')
    L.append('Global: |sum over wall rows of lam (q - O) x n_w + external moments| <= %.1e on %d witnesses (identically 0 up to the '
             'LP slack).  Per corner (the arm\'s moment about the corner point): |floor + wall + far + external pair + external row| '
             '<= %.1e on %d doubly-met corners; floor terms >= 0 and u-wall terms <= 0 on %d / %d of them.' % (
                 max(res), len(res), max(cres) if cres else 0, len(cres),
                 sum(a['floor'] >= -1e-9 and a['wall'] <= 1e-9 for r in with_stress for a in r['corners'].values()), len(cres)))
    L.append('Lemma W: every tilted wall-toucher has tau^wall of sign -chi: %d / %d loaded tilted touchers.' % (
        sum(-x['chi'] * x['tau_wall'] >= -1e-9 for r in with_stress for x in r['squares'] if x['tilted'] and x['W'] > 1e-7),
        sum(1 for r in with_stress for x in r['squares'] if x['tilted'] and x['W'] > 1e-7)))
    # candidate statistics and separation
    keys = list(scalars(with_stress[0]).keys())
    tab = {g: [scalars(r) for r in by.get(g, []) if r['has_stress']] for g in by}
    L.append('\n## Candidates: per-group ranges (min, max, median) and the separation test\n')
    L.append('A quantity SEPARATES if its range on FOUR is disjoint from its range on FJ and on OPT.  None does (last column).\n')
    L.append('| quantity | OPT | FJ | W3 | FOUR | Trump | ring | separates? |\n|---|---|---|---|---|---|---|---|')
    tr = scalars([r for r in rs if r['name'] == 'trump'][0])
    ring = scalars([r for r in rs if r['name'] == RING][0])
    for k in keys:
        col = {g: [t[k] for t in tab.get(g, [])] for g in ('OPT', 'FJ', 'W3', 'FOUR')}
        sep = 'no'
        if col['FOUR'] and col['FJ'] and col['OPT']:
            lo, hi = min(col['FOUR']), max(col['FOUR'])
            rest = col['FJ'] + col['OPT']
            if hi < min(rest) or lo > max(rest):
                sep = 'YES'
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (k, rng(col['OPT']), rng(col['FJ']), rng(col['W3']), rng(col['FOUR']),
                                                                  fmt(tr[k]), fmt(ring[k]), sep))
    # flips histogram
    L.append('\n### (a) handedness flips around the perimeter (loaded tilted wall-touchers, cyclic sign changes)\n')
    L.append('| group | flips = 0 | 2 | 4 | >= 6 | walls carrying both handednesses: 0 / 1 / 2 / 3 / 4 |\n|---|---|---|---|---|---|')
    for g in ('OPT', 'FJ', 'W3', 'FOUR'):
        fl = [t['flips'] for t in tab.get(g, [])]
        mw = [t['mixed_walls'] for t in tab.get(g, [])]
        L.append('| %s | %d | %d | %d | %d | %s |' % (g, fl.count(0), fl.count(2), fl.count(4), sum(f >= 6 for f in fl),
                                                     ' / '.join(str(mw.count(k)) for k in range(5))))
    # (b)
    L.append('\n### (b) the anti-aligning demand of the tilted wall-touchers and who supplies it\n')
    L.append('demand = sum of -tau^wall = sum chi W d over loaded tilted touchers; supply = the contact torques on them from squares '
             'sharing their wall (along-wall), from the others (interior), and from the external rows (tilt bound / crowd pull).\n')
    L.append('| group | demand | along-wall share | interior share | external share |\n|---|---|---|---|---|')
    for g in ('OPT', 'FJ', 'W3', 'FOUR'):
        t = tab.get(g, [])
        D = sum(x['demand'] for x in t)
        if D <= 0:
            L.append('| %s | 0 | - | - | - |' % g)
            continue
        L.append('| %s | %.3f | %.3f | %.3f | %.3f |' % (g, D, sum(x['supply_alongwall'] for x in t) / D,
                                                        sum(x['supply_interior'] for x in t) / D, sum(x['supply_ext'] for x in t) / D))
    # Trump and ring in detail
    for name in ('trump', RING, 's07', 's02'):
        r = [x for x in rs if x['name'] == name][0]
        L.append('\n### %s (%s, side %.4f, n2 = %d, external load %.3f)\n' % (name, r['cls'], r['s'], r['n2'], r['ext_load']))
        ti, c = r['torque_id'], r['cand_c']
        L.append('TORQUE-ID: sum tau^wall = %.4f, C (centre moments) = %.4f, residual %.1e; S_tilted = sum chi W d = %.4f '
                 '(polytope range %s), F_flat = %.4f (range %s), C range %s, |C| / bound = %.3f.' % (
                     ti['sum_tau_wall'], ti['C'], ti['residual'], c['S_tilted'], r['ranges']['S_tilted'], c['F_flat'],
                     r['ranges']['F_flat'], r['ranges']['C'], c['ratio'] or 0))
        L.append('\n| wall | pressure | moment M_c | moment M_q | load + / - / F / D | touchers (i, perimeter coord, W, h) |\n|---|---|---|---|---|---|')
        for wn in ('y=0', 'x=s', 'y=s', 'x=0'):
            wd = r['walls'][wn]
            L.append('| %s | %.4f | %.4f | %.4f | %.3f / %.3f / %.3f / %.3f | %s |' % (
                wn, wd['P'], wd['M_c'], wd['M_q'], wd['mix']['+'], wd['mix']['-'], wd['mix']['F'], wd['mix']['D'],
                ', '.join('(%d, %.2f, %.3f, %s)' % (e['i'], e['t'], e['W'], e['h']) for e in wd['touchers'])))
        L.append('\n| square | tilt | h | d | N | W | tau^wall | tau^contact (along-wall / interior) | tau^ext | meeter of |\n|---|---|---|---|---|---|---|---|---|---|')
        for x in r['squares']:
            L.append('| %d | %.2f | %s | %.3f | %d | %.3f | %.4f | %.4f (%.4f / %.4f) | %.4f | %s |' % (
                x['i'], x['tilt_deg'], x['h'], x['d'], x['N'], x['W'], x['tau_wall'], x['tau_contact'], x['tau_alongwall'],
                x['tau_interior'], x['tau_ext'], ' '.join(x['meeter_of'])))
        if r['corners']:
            L.append('\n| corner | meeters | frame tilts | floor moment | wall moment | far | ext pair | ext row | self tau | S_arm |\n|---|---|---|---|---|---|---|---|---|---|')
            for cn, a in r['corners'].items():
                L.append('| %s | %s | %s | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |' % (
                    cn, a['meeters'], a['tilts_frame'], a['floor'], a['wall'], a['far'], a['ext_pair'], a['ext_row'], a['self_tau'], a['S_arm']))
        L.append('\nperimeter sequence (coord, chi, square, wall): %s; flips %d' % (r['cand_a']['seq'], r['cand_a']['flips']))
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(OUT, len(L), 'lines')


if __name__ == '__main__':
    main()
