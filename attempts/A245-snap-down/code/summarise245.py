"""A245 summary: results/stack245_summary.json + results/click245.jsonl -> results/snapdown245.md
(+ results/summary245.json for the pages)."""
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom245 as G          # noqa: E402
import testbeds245 as T      # noqa: E402

RES = os.path.join(HERE, '..', 'results')
TAGS = ('a244', 'ring', 'crowd')
TAGNAME = {'a244': "A244's 12-stuck candidates (S >= 4.00001)", 'ring': "A239 / A226 rings (8-9 squares, not 12-stuck)",
           'crowd': "the 193 four-crowds (S >= 4.0014)"}


def load_rows():
    p = os.path.join(RES, 'click245.jsonl')
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def classify_blockers(r):
    """the squares that block the local click: A, A', another wall-cell meeter, or a free square."""
    pi = r['pair_info']
    cm = r['click']['local']
    if not cm.get('blockers'):
        return set()
    kinds = set()
    wallm = set(pi['m_c01']) | set(pi['m_cp01'])
    for i, j, g in cm['blockers']:
        if j in pi['pair']:
            kinds.add('pair')
        elif j in pi['A']:
            kinds.add('A')
        elif j in pi['Ap']:
            kinds.add("A'")
        elif j in wallm:
            kinds.add('slot-meeter')
        else:
            kinds.add('free')
    return kinds


def supply_census(cfgs):
    """A244's supply field: how each wall slot is supplied (OWN / ADJ / FREE), and the walls with a
    MUTUAL supply (both slots supplied by the adjacent corner's meeter)."""
    kinds = collections.Counter()
    mutual_walls = 0
    for c in cfgs:
        sup = c.get('supply') or {}
        for k, v in sup.items():
            kinds.update(v)
        for wall, (a, b) in G.WALLS.items():
            ka = a + ('01' if wall in ('x=0', 'x=s') else '10')
            kb = b + ('01' if wall in ('x=0', 'x=s') else '10')
            if 'ADJ' in sup.get(ka, []) and 'ADJ' in sup.get(kb, []):
                mutual_walls += 1
    return dict(kinds), mutual_walls, 4 * len(cfgs)


def touch_census(cfgs, tol=1e-4):
    """corner meeters touching a wall (either wall of their corner), per family."""
    tot = touching = 0
    for c in cfgs:
        ms = G.meeters(c['poses'], c['s'])
        for corner in G.CORNERS:
            for i in ms[corner + '00']:
                tot += 1
                if G.wall_gap(c['poses'][i], c['s']) <= tol:
                    touching += 1
    return touching, tot


def family_stats(rows):
    pairs = [r for r in rows if r['pair_info']['pair'] is not None]
    hw = [r for r in pairs if r['pair_info'].get('hwall')]
    mut = [r for r in pairs if r['pair_info'].get('mutual')]
    loc = [r['click']['local'] for r in pairs]
    glo = [r['click']['global'] for r in pairs]
    st = {'walls': len(rows), 'pairs': len(pairs), 'hwall': len(hw), 'mutual': len(mut),
          'mutual_hwall': sum(1 for r in mut if r['pair_info'].get('hwall')),
          'why': dict(collections.Counter(r['pair_info'].get('why') for r in rows if r['pair_info']['pair'] is None)),
          'contact': sum(r['pair_info']['contact'] for r in pairs),
          'hands': dict(collections.Counter(r['pair_info']['hand'] for r in pairs)),
          'contact_types': dict(collections.Counter(r['pair_info'].get('contact_type', 'n/a') for r in hw)),
          'order_ok': sum(1 for r in hw if r['pair_info'].get('order_ok')),
          'local_feasible': sum(c['feasible_at_s0'] for c in loc),
          'local_blocked': sum(c['blocked_at'] is not None for c in loc),
          'local_raises': sum(1 for c in loc if c['blocked_at'] is None and not c['feasible_at_s0']),
          'local_blockers': dict(collections.Counter(k for r in pairs for k in classify_blockers(r))),
          'global_blocked': sum(c['blocked_at'] is not None for c in glo),
          'global_end_le_s0': sum(1 for r, c in zip(pairs, glo) if c['s_end'] is not None and c['s_end'] <= r['s0'] + 1e-7),
          'global_monotone': sum(c['monotone'] for c in glo),
          'global_max_uptick': max((c['max_uptick'] for c in glo), default=0.0),
          'global_rise': max((c['s_max'] - r['s0'] for r, c in zip(pairs, glo) if c['s_max'] is not None), default=0.0),
          'extent_H_before_gt2': sum(1 for r in pairs if r['extent_before']['H'] > 2 + 1e-9),
          'chord_before_min': min((r['extent_before']['chord_sum'] for r in pairs), default=0.0),
          'chord_before_max': max((r['extent_before']['chord_sum'] for r in pairs), default=0.0),
          'reduce_before_any': sum(r['reduce_before']['any_ok'] for r in rows),
          'reduce_before_k1': sum(r['reduce_before']['k1']['direct'] for r in rows),
          'reduce_before_k2_direct': sum(r['reduce_before']['k2']['direct'] for r in rows if 'k2' in r['reduce_before']),
          'reduce_before_k2_placed': sum(1 for r in rows if 'k2' in r['reduce_before'] and r['reduce_before']['k2']['placed']),
          'reduce_after_local': sum(1 for c in loc if c.get('reduce_end', {}).get('any_ok')),
          'reduce_after_local_n': sum(1 for c in loc if 'reduce_end' in c),
          'reduce_after_global': sum(1 for c in glo if c.get('reduce_end', {}).get('any_ok')),
          'reduce_after_global_n': sum(1 for c in glo if 'reduce_end' in c),
          'mutual_local_feasible': sum(r['click']['local']['feasible_at_s0'] for r in mut),
          'mutual_global_end_le_s0': sum(1 for r in mut if r['click']['global']['s_end'] is not None
                                         and r['click']['global']['s_end'] <= r['s0'] + 1e-7)}
    return st


def main():
    rows = load_rows()
    stack = json.load(open(os.path.join(RES, 'stack245_summary.json'))) if os.path.exists(
        os.path.join(RES, 'stack245_summary.json')) else {}
    fam = {t: family_stats([r for r in rows if r['tag'] == t]) for t in TAGS}
    rids = {r['rid'] for r in rows}
    cfgs = {t: [c for c in T.all_configs((t,)) if c['rid'] in rids] for t in TAGS}
    sup = supply_census(cfgs['a244'])
    touch = {t: touch_census(cfgs[t]) for t in TAGS}
    L = ['# A245 results -- STACK sampled, WALL-CLICK and REDUCE on every testbed wall', '',
         '## 1. Lemma STACK on the mutual wall-pair family (`stack245.py`, exact SAT, 4 000 mutual pairs per side)', '',
         '| side | pairs | order B < B\' | clearance < 4 - s | floating (gap > 0) | max gap | contact keeps cells | table match | H_contact min | H - chords min |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for s, d in stack.items():
        L.append('| %s | %d | %d | %d | %d | %.4f | %d | %d | %.3f | %.3f |' % (
            s, d['n'], d['order_ok'], d['clear_lt_4ms'], d['gap_pairs'], d['max_clearance'], d['contact_cells_ok'],
            d['contact_matches_table'], d['H_contact_min'], d['H_minus_chords_min']))
    L += ['', 'Handedness pairs and contact types at contact (side 3.82): `%s`' % json.dumps(stack.get('3.82', {}).get('types', {})), '']
    L += ['## 2. Wall pairs in the testbeds (`click245.py`)', '',
          '| family | walls | pairs found | H-WALL | mutual | mutual & H-WALL | B|B\' in contact | order ok (H-WALL) |', '|---|---|---|---|---|---|---|---|']
    for t in TAGS:
        f = fam[t]
        L.append('| %s | %d | %d | %d | %d | %d | %d | %d |' % (TAGNAME[t], f['walls'], f['pairs'], f['hwall'], f['mutual'],
                                                            f['mutual_hwall'], f['contact'], f['order_ok']))
    for t in TAGS:
        L.append('- %s: no pair because %s; handedness of the pairs %s; contact types (H-WALL pairs) %s.' % (
            t, json.dumps(fam[t]['why']), json.dumps(fam[t]['hands']), json.dumps(fam[t]['contact_types'])))
    L += ['', "- A244's slot supply over the %d candidates (%d slots): %s; walls whose BOTH slots are supplied by the "
          'adjacent corner (the mutual case): %d of %d.' % (len(cfgs['a244']), 8 * len(cfgs['a244']), json.dumps(sup[0]), sup[1], sup[2])]
    L += ['- corner meeters touching a wall of the container (tol 1e-4): ' +
          ', '.join('%s %d / %d' % (t, touch[t][0], touch[t][1]) for t in TAGS), '']
    L += ['## 3. WALL-CLICK: the pair rotated jointly to flush', '',
          '| family | pairs | LOCAL feasible at s0 | LOCAL blocked | LOCAL side rises | blockers | GLOBAL blocked | GLOBAL end <= s0 | GLOBAL monotone | max rise above s0 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for t in TAGS:
        f = fam[t]
        L.append('| %s | %d | %d | %d | %d | %s | %d | %d | %d | %.4f |' % (
            t, f['pairs'], f['local_feasible'], f['local_blocked'], f['local_raises'], json.dumps(f['local_blockers']),
            f['global_blocked'], f['global_end_le_s0'], f['global_monotone'], f['global_rise']))
    L += ['', '- on the MUTUAL walls: local click feasible at s0 on ' + ', '.join(
        '%s %d / %d' % (t, fam[t]['mutual_local_feasible'], fam[t]['mutual']) for t in TAGS) +
        '; global click ends at <= s0 on ' + ', '.join('%s %d / %d' % (t, fam[t]['mutual_global_end_le_s0'], fam[t]['mutual']) for t in TAGS) + '.',
        '- the pair\'s along-wall extent H exceeds 2 before the click on ' + ', '.join(
        '%s %d / %d' % (t, fam[t]['extent_H_before_gt2'], fam[t]['pairs']) for t in TAGS) +
        ' (chord sums %.3f .. %.3f, exactly 2 after any click).' % (
            min(fam[t]['chord_before_min'] for t in TAGS if fam[t]['pairs']), max(fam[t]['chord_before_max'] for t in TAGS)), '']
    L += ['## 4. REDUCE on the wall column (Lemma CELLS k = 1, 2, 3 and the (k+1)-for-(k+1) exchange)', '',
          '| family | walls | before: any k | k1 direct | k2 direct | k2 3-for-3 placed | after LOCAL click | after GLOBAL click |',
          '|---|---|---|---|---|---|---|---|']
    for t in TAGS:
        f = fam[t]
        L.append('| %s | %d | %d | %d | %d | %d | %d / %d | %d / %d |' % (
            t, f['walls'], f['reduce_before_any'], f['reduce_before_k1'], f['reduce_before_k2_direct'], f['reduce_before_k2_placed'],
            f['reduce_after_local'], f['reduce_after_local_n'], f['reduce_after_global'], f['reduce_after_global_n']))
    L += ['', 'Every testbed sits at S >= 3.877 (rings) or S >= 4.0000 (12-stuck, four-crowds): REDUCE succeeding there is room at '
          'or above 4, not a kill; the tables test the choreography, not STUCK-4.', '']
    open(os.path.join(RES, 'snapdown245.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    json.dump({'fam': fam, 'supply': sup, 'touch': touch, 'stack': stack},
              open(os.path.join(RES, 'summary245.json'), 'w'), indent=1)
    print('\n'.join(L))


if __name__ == '__main__':
    main()
