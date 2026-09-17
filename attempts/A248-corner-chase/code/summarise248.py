"""A248: results/chase248.jsonl (+ external248_*.json) -> results/chase248.md + chase248_summary.json.

The chase steps a corner (seen from a wall) is scored against, in order:
  S0 LOCKED      both meeters retreat-free (A244: no corpus packing; A240's flag for the FJ points)
  S1 TYPE-F      a flat meeter on the floor of this wall frame (the PI's picture)
  S2 POKE        the poker touches the shared wall; its sense (CCW / CW); sin t <= x_v <= delta;
                 TILT-MIN's depth bound; top vertex >= 2 (TOP-2); no flat wall square above (FLAT-ABOVE)
  S3 SUPPLY      c01's second supplier beyond B: a wall square (STACK) | off-wall square; c'-meeter | free
  S4 NO-ROTATE   for a wall pair (B, B'): the click's Psi-gain and whether the window [0,1]x[1,3]
                 is blocked, by whom (A | c'-meeter | another wall square | interior)
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results')


def first_failure(v, locked):
    """where this corner view leaves the PI's chain."""
    if not locked:
        return 'S0 not locked'
    if 'poke' not in v:
        return 'S1 type T (no flat floor meeter)' if v['type'] == 'T' else 'S1 flat meeter on the wall, not the floor'
    p = v['poke']
    if not p['B_touches_wall']:
        return 'S2 poker off the wall'
    if p['sense'] == 'CW':
        return 'S2 poker CW (POKE sense fails)'
    if not p['c01_suppliers']:
        return 'S3 c01 singly met beyond touches'
    kinds = set(p['c01_suppliers'].values())
    if not any(k.startswith('wall') for k in kinds):
        return 'S3 second supplier off the wall (%s)' % ','.join(sorted(kinds))
    if any(q['gain'] < 0 and not q['blocked'] for q in p['pairs']):
        return 'S4 click unblocked (a Psi-lowering exchange exists)'
    return 'consistent through S4'


def main():
    rows = [json.loads(l) for l in open(os.path.join(RES, 'chase248.jsonl'), encoding='utf-8')]
    cor = [r for r in rows if not r['kind'].startswith('fj')]
    fj = [r for r in rows if r['kind'].startswith('fj')]
    S = {'corpus_packings': len(cor), 'fj_points': len(fj)}
    # ---- corpus: the geometric steps
    ct, sense, sup, pairs, bad = (collections.Counter() for _ in range(5))
    fail = collections.Counter()
    for r in cor:
        for v in r['views']:
            ct[v['type']] += 1
            fail[first_failure(v, True)] += 1            # as if locked: the geometric failure
            if 'poke' not in v:
                continue
            p = v['poke']
            sense[(p['sense'], 'on wall' if p['B_touches_wall'] else 'off wall')] += 1
            bad['sin > delta'] += not p['sin_le_delta']
            bad['top < 2'] += not p['top_ge_2']
            bad['flat wall square above'] += bool(p['flat_above'])
            bad['depth > TILT-MIN bound (1e-5)'] += p['d_v'] > p['tiltmin_bound'] + 1e-5
            bad['A meets c01 (depth > 1e-6)'] += p.get('A_c01_depth', 0.0) > 1e-6
            for k in p['c01_suppliers'].values():
                sup[k] += 1
            for q in p['pairs']:
                pairs[('gain<0' if q['gain'] < 0 else 'gain>=0',
                       'blocked by ' + '+'.join(sorted(q['blockers'])) if q['blocked'] else 'UNBLOCKED')] += 1
    S['corpus'] = {'views_by_type': dict(ct), 'poker_sense': {'%s %s' % k: v for k, v in sense.items()},
                   'violations': dict(bad), 'c01_second_suppliers': dict(sup),
                   'wall_pairs': {'%s | %s' % k: v for k, v in pairs.items()},
                   'first_failure_geometric': dict(fail),
                   'first_failure_actual': {'S0 not locked (A244: free FJ infeasible on every one)': 8 * len(cor)}}
    # ---- the FJ points' doubly-met corners
    lk = collections.Counter()
    lfail = collections.Counter()
    lsense = collections.Counter()
    lpairs = collections.Counter()
    for r in fj:
        for v in r['views']:
            if v['n_meeters'] < 2:
                continue
            locked = bool(r['locked'].get(v['corner']))
            lk[('locked' if locked else 'unlocked', v['type'])] += 1
            if locked:
                lfail[first_failure(v, True)] += 1
                if 'poke' in v:
                    lsense[v['poke']['sense']] += 1
                    for q in v['poke']['pairs']:
                        lpairs['blocked by ' + '+'.join(sorted(q['blockers'])) if q['blocked'] else 'UNBLOCKED'] += 1
    S['fj'] = {'doubly_met_views': {'%s %s' % k: v for k, v in lk.items()}, 'locked_first_failure': dict(lfail),
               'locked_poker_sense': dict(lsense), 'locked_wall_pairs': dict(lpairs)}
    # ---- the external ring
    ext = {}
    for fn in sorted(glob.glob(os.path.join(RES, 'external248_*.json'))):
        d = json.load(open(fn, encoding='utf-8'))
        ext['%.4f' % d['side']] = {k: d[k] for k in d if k not in ('poses',)}
    S['external'] = ext
    tp = os.path.join(RES, 'twopokers248.json')
    if os.path.exists(tp):
        S['two_pokers'] = json.load(open(tp, encoding='utf-8'))
    S['notches'] = {}
    for fn in sorted(glob.glob(os.path.join(RES, 'notches248_*.json'))):
        d = json.load(open(fn, encoding='utf-8'))
        S['notches']['%.4f' % d['side']] = d['sup_margin']
    json.dump(S, open(os.path.join(RES, 'chase248_summary.json'), 'w', encoding='utf-8'), indent=1)
    write_md(S)


def write_md(S):
    L = ['# A248 -- the corner chase on the 764 twelve-stuck packings and the genuine FJ corners',
         '', 'Code `chase248.py` / `external248.py` / `summarise248.py`; steps S0-S4 in the header of '
         '`summarise248.py`; every corner is seen from each of its two walls (a VIEW).', '',
         '## 1. The 764 corpus packings (%d x 8 views)' % S['corpus_packings'], '']
    c = S['corpus']
    L.append('* views by corner type (from this wall): %s' % c['views_by_type'])
    L.append('* poker sense where the PI\'s picture applies (flat floor meeter + partner): %s' % c['poker_sense'])
    L.append('* violations of the proved facts (sin t <= delta, TOP-2, FLAT-ABOVE, TILT-MIN, TYPE-F-OWN): %s' % c['violations'])
    L.append('* c01\'s second supplier beyond the poker: %s' % c['c01_second_suppliers'])
    L.append('* wall pairs (B, B\') and the click: %s' % c['wall_pairs'])
    L.append('* where the chase fails, ACTUAL: %s' % c['first_failure_actual'])
    L.append('* where it would fail if the corner were locked (the geometric step): %s' % c['first_failure_geometric'])
    L += ['', '## 2. The genuine free FJ points (%d packings)' % S['fj_points'], '']
    f = S['fj']
    L.append('* doubly-met corner views, LOCKED (A240 flag) vs not, by type: %s' % f['doubly_met_views'])
    L.append('* locked corners: the step of the chase they satisfy / fail: %s' % f['locked_first_failure'])
    L.append('* locked corners with the PI\'s picture: poker sense %s; wall pairs %s' % (f['locked_poker_sense'], f['locked_wall_pairs']))
    L += ['', '## 3. TWO-POKERS, SEPARATE-NOTCHES, the external ring and the pocket', '']
    if 'two_pokers' in S:
        t = S['two_pokers']
        L.append('* TWO-POKERS: on the line theta + theta_f = 90 the bound is h(theta) = tan(45 - theta/2) + tan(theta/2) + sec theta, '
                 'min %.10f at theta = %.6f deg -> s* = %.10f; grid min over the triangle %.8f at %s; certified lower bound '
                 '%.8f over the whole triangle: %s (%d boxes)' % (t['line']['min_h'], t['line']['theta_deg'], t['line']['s_star'],
                                                                 t['grid_min']['F'], t['grid_min']['at_deg'], t['certified']['target'],
                                                                 t['certified']['ok'], t['certified']['boxes']))
        L.append('* SAT sup-margin of the pair (pokers wall-touching or floating, offsets <= 1) by side: %s' % {
            k: round(v['sup_margin'], 5) for k, v in t['sat_ladder'].items()})
    if S.get('notches'):
        L.append('* SEPARATE-NOTCHES [M]: sup least margin of one free square serving BL01 and TL10 in the pinwheel: %s' % S['notches'])
    for s, d in S['external'].items():
        L.append('* side %s: ring %s (pair gap %.3g, wall gap %.3g, least second depth %.3g); x = %s' % (
            s, 'OK' if d['ring_ok'] else 'NOT found', d['min_pair_gap'], d['min_wall_gap'], d['min_second_depth'],
            ['%.4f' % v for v in d['x']]))
        for k in (1, 2, 3):
            if 'pocket_%d' % k in d:
                p = d['pocket_%d' % k]
                L.append('  * %d free square(s) in the pocket: best least gap %.4g -> %s' % (
                    k, p['best_min_gap'], 'FITS' if p['fits'] else 'does not fit (search)'))
    with open(os.path.join(RES, 'chase248.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
