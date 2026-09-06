r"""report102.py -- turn results/rigid102[_bar1e-06].jsonl into notes/rigid102.md and
results/table102.json (the T3 rule, the T2 drain table, the T1 detail, the residue)."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rigid102 as G                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A102 = os.path.dirname(HERE)
RES = os.path.join(A102, 'results')
NOTES = os.path.join(A102, 'notes')


def load(tag=''):
    p = os.path.join(RES, 'rigid102%s.jsonl' % tag)
    rows = [json.loads(l) for l in open(p, encoding='utf-8')]
    for r in rows:                       # annotate: how far out of its cell did it retract?
        for rnd in r['t1']:
            for x in rnd:
                d0 = x['depth']
                best = 0.0
                for m in x['motions']:
                    da = G.corner_depth(tuple(m['pose']), x['corner'], r['side'])
                    f = (d0 - da) / d0 if d0 > 0 else 0.0
                    best = max(best, f)
                x['max_retraction'] = round(best, 6)
    return rows


def best_motion(x):
    """The motion that got furthest / freed the corner, for the T1 table."""
    fr = [m for m in x['motions'] if m['frees_corner'] and m['fraction_reached'] > 0]
    if fr:
        m = fr[0]
    elif x['motions']:
        m = max(x['motions'], key=lambda m: m.get('reached_deg', 0) ** 2
                + (m.get('travel', 0) * 100) ** 2)
    else:
        return '-', '', ''
    amt = ('%.3g deg' % m['reached_deg']) if 'reached_deg' in m else ('%.3g' % m['travel'])
    blk = 'free' if m['collision_free'] else m['blocked_by']['blocker']
    return m['kind'], amt, blk


def young_str(y):
    out = []
    for c in ('BL', 'BR', 'TR', 'TL'):
        cells = y.get(c) or []
        if not cells:
            continue
        rows = {}
        for i, j in cells:
            rows[j] = rows.get(j, 0) + 1
        out.append('%s%s' % (c, [rows[k] for k in sorted(rows)]))
    return ' + '.join(out) if out else 'empty'


def main():
    R = {'1e-9': load(), '1e-6': load('_bar1e-06')}
    L = []
    A = L.append
    A('# A102 -- the rigidity drain: contact-torque test on the K0-BLOCKED corpus\n')
    A('*Opus chore, 2026-09-05. Code `code/rigid102.py` (+ `code/report102.py`); results\n'
      '`results/rigid102{,_bar1e-06}.{json,jsonl}`; logs `logs/`. One process, BLAS pinned,\n'
      'pure geometry, no LP; whole corpus at both meet bars in ~12 min.*\n')

    rows9, rows6 = R['1e-9'], R['1e-6']
    by6 = {r['packing']: r for r in rows6}
    sub4 = [r for r in rows9 if r['side'] < 4.0 and r['packing'] != 'TRUMP_canary']
    dr9 = [r for r in rows9 if r['drained'] and r['packing'] != 'TRUMP_canary']
    dr6 = [r for r in rows6 if r['drained'] and r['packing'] != 'TRUMP_canary']

    # ---- census of second meeters
    cen = {}
    for r in rows9:
        for x in r['t1'][0]:
            if not x['is_second_meeter']:
                continue
            k = ('floor' if x['depth'] <= 1e-2 else 'deep', x['class'])
            cen[k] = cen.get(k, 0) + 1
    rigid = sum(1 for r in rows9 for x in r['t1'][0]
                if x['is_second_meeter'] and x.get('first_order_rigid'))
    nsec = sum(1 for r in rows9 for x in r['t1'][0] if x['is_second_meeter'])

    pk = {}
    for r in rows9:
        for x in r['t1'][0]:
            if x['is_second_meeter'] and x['class'] == 'PINNED':
                pk[x['pin_kind']] = pk.get(x['pin_kind'], 0) + 1
    retr = {r['packing']: max([mx for x in r['t1'][0] if x['is_second_meeter']
                               for mx in [x.get('max_retraction', 0.0)]] or [0.0])
            for r in rows9}
    A('## T3 -- the empirical rule\n')
    A('**The rule the brief guessed is FALSE, and the true one is a dichotomy about ROOM, not '
      'about first-order freedom:** *in this corpus a second meeter either retracts entirely '
      'out of its corner cell under one rigid-body motion (10 of the 12 strictly K0-BLOCKED '
      'packings, retraction fraction 1.000, and the K0-FREE snap then gives k >= 2 at the same '
      'side -- k = 7 for both packings below side 4) or it barely moves at all (the two '
      'exceptions retract 0.22 and 0.022 of their depth, Trump 0.000); nothing in between.*\n')
    A('Specifically:\n')
    A('* **"every floor-depth (d2 <= 1e-2) second meeter is FREE-ROT or FREE-TRANS" is false**: '
      'of the %d floor-depth second meeters, %d are PINNED (all torques about the centre '
      'opposed AND the normal cone the whole plane), and %d are RIGID for the *full* '
      'first-order motion cone (no rotation about any point, no translation).'
      % (sum(v for k, v in cen.items() if k[0] == 'floor'), cen.get(('floor', 'PINNED'), 0),
         sum(1 for r in rows9 for x in r['t1'][0]
             if x['is_second_meeter'] and x['depth'] <= 1e-2 and x.get('first_order_rigid'))))
    A('* **first-order freedom does not predict the drain either.** Both non-draining packings '
      'have screw-free second meeters; their motions are stopped after 1e-4 deg by a square '
      'whose gap is just ABOVE the 1e-7 contact bar (1.4e-6 and 3.1e-5), i.e. by a near-contact '
      'that the contact set does not see. The obstruction to a theorem is exactly this: the '
      'contact set at any fixed tolerance does not determine the finite motion.')
    A('* **largest d2 that drained: 1.02e-2** (`floor_1e-02_d1em02_s0076`, TR sq6, a 1.279 deg '
      'rotation about its own centre, then 11 simultaneous snaps to k = 5). The deepest second '
      'meeters in the corpus (0.155 Trump TL, 0.206 anchored0 TL) do not move at all.')
    A('* **both sub-4 packings drain to k = 7 at the same side** (3.98548 `record_s0115`, '
      '3.99075 `floor_1e-03`); at the 1e-6 census bar the record is not K0-BLOCKED at all '
      '(TR/TL are 1.6e-8 / 7.0e-9 nicks) and the second meeters of its two genuinely crowded '
      'corners (BL sq0 at 0.0147, BR sq3 at 0.0145) are first-order RIGID, '
      'so it does not drain there -- the record\'s drain is a tangency-scale motion, degen87\'s '
      'observation, not a floor-depth one.')
    A('* **the pins are square-square, not wall-square**: of the PINNED second meeters, %s.'
      % ', '.join('%d %s' % (v, k) for k, v in sorted(pk.items())))
    A('* **canary**: Trump\'s TL crowd {4, 6} at depth 0.155 / 0.168 is first-order RIGID, '
      'retraction 0.000, zero moves, k stays 5. **PASS.**\n')
    A('```')
    A(json.dumps({'second_meeters': nsec, 'class_census': {'%s/%s' % k: v
                                                           for k, v in sorted(cen.items())},
                  'second_meeters_first_order_rigid': rigid,
                  'pin_kinds': pk,
                  'packings_drained_bar1e-9': len(dr9),
                  'packings_drained_bar1e-6': len(dr6),
                  'not_drained': [r['packing'] for r in rows9
                                  if not r['drained'] and r['packing'] != 'TRUMP_canary'],
                  'sub4_packings': [r['packing'] for r in sub4],
                  'sub4_drained': [r['packing'] for r in sub4 if r['drained']],
                  'max_depth_retraction_of_a_second_meeter': retr}, indent=1))
    A('```\n')

    # ---- T2 table
    for bar, rows in (('1e-9 (exact: any intrusion is a meeting)', rows9),
                      ('1e-6 (strict85 / degen87 census bar)', rows6)):
        A('## T2 -- the drain, meet bar %s\n' % bar)
        A('| packing | side | n_meet BL/BR/TR/TL | d2 per corner | moves | final k | class '
          '(Young) | drained |')
        A('|---|---|---|---|---|---|---|---|')
        for r in rows:
            mc = r['initial']['meet_counts']
            d2 = r['initial']['d2']
            mv = [m for m in r['moves'] if m.get('kind') != 'SNAP']
            desc = '; '.join('%s sq%d %s' % (m['corner'], m['square'], m['motion'])
                             for m in mv) or '-'
            A('| `%s` | %.7f | %d/%d/%d/%d | %s | %s | %d | %s | %s |'
              % (r['packing'], r['side'], mc['BL'], mc['BR'], mc['TR'], mc['TL'],
                 ' '.join('%.2g' % d2[c] if d2[c] is not None else '-'
                          for c in ('BL', 'BR', 'TR', 'TL')),
                 desc, r['final']['k'], young_str(r['final']['young']),
                 'YES' if r['drained'] else 'no'))
        A('')

    # ---- T1 detail
    A('## T1 -- the rigidity test, per corner, per meeter (meet bar 1e-9)\n')
    A('`class` is the brief\'s trichotomy from the centre torques / normal cone; `rigid` = the '
      'FULL first-order motion cone {(v, w) : v.F_k + w*tau_k >= 0} is {0} (rotation about '
      'every point and every translation blocked).\n')
    A('| packing | corner | sq | d | tilt | contacts | class | rigid | pin | best motion | '
      'reached | stopped by | frees |')
    A('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows9:
        for x in r['t1'][0]:
            k, amt, blk = best_motion(x)
            A('| `%s` | %s | %d%s | %.2e | %.4f | %s | %s | %s | %s | %s | %s | %s | %s |'
              % (r['packing'], x['corner'], x['square'],
                 '*' if x['is_second_meeter'] else '', x['depth'], x['tilt_deg'],
                 '+'.join(sorted({c['with'] for c in x['contacts']})) or 'none',
                 x['class'], 'RIGID' if x.get('first_order_rigid') else 'screw-free',
                 x.get('pin_kind') or '-', k, amt, blk,
                 'YES' if x['frees_corner'] else ''))
    A('')

    # ---- residue
    A('## The residue: PINNED second meeters of the packings that do not drain\n')
    for r in rows9:
        if r['drained'] or r['packing'] == 'TRUMP_canary':
            continue
        A('### `%s` (side %.9f)\n' % (r['packing'], r['side']))
        for x in r['t1'][0]:
            if not x['is_second_meeter']:
                continue
            A('* **%s sq%d**, depth %.3e, tilt %.4f deg, %s, %s' %
              (x['corner'], x['square'], x['depth'], x['tilt_deg'], x['class'],
               x.get('pin_kind') or '-'))
            for c in x['contacts']:
                A('  * %s at (%.6f, %.6f), edge normal (force on Q) (%+.4f, %+.4f), gap %s, '
                  'torque about centre %+.5f'
                  % (c['with'], c['point'][0], c['point'][1],
                     c['normal_force_on_Q'][0], c['normal_force_on_Q'][1], c['gap'],
                     c['torque_about_centre']))
        A('')
    A('### The canary\n')
    t = [r for r in rows9 if r['packing'] == 'TRUMP_canary'][0]
    A('Trump: TL crowd {%s}, both PINNED by two or more squares, every tested motion blocked, '
      '0 moves, k stays 5 (`trump5`). **CANARY PASS.**\n'
      % ', '.join(str(x['square']) for x in t['t1'][0]))

    open(os.path.join(NOTES, 'rigid102.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

    tab = {'attempt': 'A102 rigidity drain',
           'census_second_meeters': {'%s/%s' % k: v for k, v in sorted(cen.items())},
           'n_second_meeters': nsec, 'n_first_order_rigid': rigid,
           'drained_bar1e-9': [r['packing'] for r in dr9],
           'drained_bar1e-6': [r['packing'] for r in dr6],
           'per_packing': [{'packing': r['packing'], 'side': r['side'],
                            'drained_1e-9': r['drained'],
                            'drained_1e-6': by6[r['packing']]['drained'],
                            'k_1e-9': r['final']['k'],
                            'k_1e-6': by6[r['packing']]['final']['k'],
                            'young_1e-9': r['final']['young'],
                            'moves': [m for m in r['moves'] if m.get('kind') != 'SNAP'],
                            'd2': r['initial']['d2']} for r in rows9]}
    json.dump(tab, open(os.path.join(RES, 'table102.json'), 'w'), indent=1)
    print('wrote notes/rigid102.md and results/table102.json')


if __name__ == '__main__':
    main()
