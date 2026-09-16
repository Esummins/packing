"""A240 -- tables from results/cross240.jsonl -> results/cross240.md (Lemma OPPOSE's test on every witness corner,
the wall grains, the bracing chains, the crossing and what sits there).
    python summarise240.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'cross240.jsonl')
OUT = os.path.join(ATT, 'results', 'cross240.md')
RING = 'w364_held'


def grp(r):
    return r['cls'] if r['cls'] in ('HELD', 'CROWD', 'TRUMP', 'RECORD') else 'FJ'


def table(counter, cols, title):
    keys = sorted({k[0] for k in counter})
    lines = ['', title, '', '| group | ' + ' | '.join(cols) + ' | total |', '|---|' + '---|' * (len(cols) + 1)]
    for g in keys:
        row = [counter.get((g, c), 0) for c in cols]
        lines.append('| %s | %s | %d |' % (g, ' | '.join(str(v) for v in row), sum(row)))
    return lines


def main():
    rs = [json.loads(l) for l in open(RES, encoding='utf-8')]
    st = [r for r in rs if r['has_stress']]
    L = ['# A240 -- Theorem CROSS on the witnesses (%d witnesses with a bounded FJ stress; %d doubly-met corners)' % (
        len(st), sum(len(r['corners']) for r in st)), '',
         'Corner frame (u, v); handedness in the FRAME: + = frame tilt < 45 deg, - = > 45 deg, F flat, D diamond; a pair is '
         '"same" / "opposite" by frame handedness, "flat" if a member is F or D.  LOCKED = both meeters carry a loaded wall or '
         'pair row and NO external row (tilt bound / crowd pull) is loaded on either; EXT = an external row is loaded on a meeter; '
         'UNLOADED = a meeter carries nothing.  Partner type = the loaded contact(s) between the two meeters (flush / VE / VV).']
    # T1 lock status x pair
    C = collections.Counter()
    for r in st:
        for c in r['corners']:
            status = 'locked' if c['locked'] else ('ext' if c['ext_on_meeters'] else 'unloaded')
            C[(grp(r), status + '/' + c['pair_frame'])] += 1
    cols = [s + '/' + p for s in ('locked', 'ext', 'unloaded') for p in ('same', 'opposite', 'flat')]
    L += table(C, cols, '## T1. Lemma OPPOSE\'s test: every doubly-met corner by lock status and frame-handedness pair')
    # T2 locked corners by partner type
    C = collections.Counter()
    for r in st:
        for c in r['corners']:
            if c['locked']:
                C[(grp(r), '%s/%s' % (c['pair_frame'], c['partner_type']))] += 1
    cols = sorted({k[1] for k in C})
    L += table(C, cols, '## T2. LOCKED corners by pair and partner contact type')
    # T3 sign patterns at locked corners with a loaded partner contact
    C = collections.Counter()
    for r in st:
        for c in r['corners']:
            if c['locked'] and c['partner_loaded']:
                pat = ''.join(sorted(('A' if m['partner_anti'] else 'a') if m['chi'] else 'f' for m in c['members']))
                C[(grp(r), pat)] += 1
    cols = sorted({k[1] for k in C})
    L += table(C, cols, '## T3. At LOCKED corners with a loaded partner contact: the partner torque on each meeter is '
                        'anti-aligning (A, sign chi) or aligning (a, sign -chi); f = flat / diamond meeter')
    # Lemma W
    nw = sum(1 for r in st for c in r['corners'] for m in c['members'] if m['wall_sign_ok'])
    nt = sum(1 for r in st for c in r['corners'] for m in c['members'] if m['wall_sign_ok'] is not None)
    nf = sum(1 for r in st for c in r['corners'] for m in c['members'] if m['chi'] == 0 and m['W'] > 1e-7)
    L += ['', 'Lemma W on the meeters: wall torque of sign -chi (or 0) on %d / %d tilted meeters; %d flat / diamond wall-loaded meeters '
          'carry a free self-torque (two vertex rows).' % (nw, nt, nf)]
    # ring
    ring = [r for r in rs if r['name'] == RING][0]
    L += ['', '## T4. The ring `rand_0_0569|t20` (w364_held, side %.4f): every corner is a same-handed pair held by a tilt-bound torque' % ring['s'], '',
          '| corner | pair (frame / global) | meeter | h frame / global | tilt (frame) | W | tau wall | tau partner | tau along-wall | tau other | tau ext (tilt bound) |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for c in ring['corners']:
        for m in c['members']:
            L.append('| %s | %s / %s | %d | %s / %s | %.1f | %.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f |' % (
                c['corner'], c['pair_frame'], c['pair_global'], m['i'], m['h'], m['h_global'], m['tilt_frame_deg'], m['W'],
                m['tau_wall'], m['tau_partner'], m['tau_along'], m['tau_other'], m['tau_ext']))
    L += ['', 'Wall grains of the ring (meeters touching each wall, global handedness): ' + '; '.join(
        '%s: %s %s' % (wn, g['meeters'], g['h']) for wn, g in ring['grains'].items()),
          'Chains: LR %s, TB %s, shared %s (%s).' % (ring['chains']['LR'], ring['chains']['TB'], ring['chains']['shared'],
                                                     ring['chains']['shared_desc'])]
    # T5 wall grains
    four = [r for r in st if r['n2'] == 4]
    C = collections.Counter()
    for r in four:
        for wn, g in r['grains'].items():
            hs = ''.join(sorted(h for h, l in zip(g['h'], g['loaded']) if l))
            key = 'mixed +-' if '+' in hs and '-' in hs else ('one-handed' if hs and set(hs) <= {'+', '-'} else ('flat only' if hs else 'none loaded'))
            if hs and 'F' in hs and set(hs) - {'F'}:
                key = 'tilted + flat'
            C[('FOUR (%d)' % len(four), key)] += 1
    cols = ['one-handed', 'mixed +-', 'tilted + flat', 'flat only', 'none loaded']
    L += table(C, cols, '## T5. Wall grains on the 193 four-crowds: the loaded handednesses of the meeters touching each wall (772 walls)')
    mixed = sum(1 for r in four if any('+' in ''.join(h for h, l in zip(g['h'], g['loaded']) if l) and '-' in ''.join(h for h, l in zip(g['h'], g['loaded']) if l) for g in r['grains'].values()))
    L += ['', 'Four-crowds with at least one mixed wall: %d / %d; with the PI\'s alternation (left = right handed, top = bottom handed, '
          'left != top, every wall one-handed): %d.' % (mixed, len(four), sum(1 for r in four if alternates(r)))]
    # T6 chains
    C = collections.Counter()
    for r in four:
        ch = r['chains']
        key = ('LR+TB' if ch['LR'] and ch['TB'] else ('LR only' if ch['LR'] else ('TB only' if ch['TB'] else 'neither')))
        C[('FOUR', key)] += 1
    L += table(C, ['LR+TB', 'LR only', 'TB only', 'neither'], '## T6. Loaded bracing chains on the four-crowds: a left-right chain '
               '(loaded contact path from a loaded left-wall row to a loaded right-wall row) and a floor-ceiling chain')
    C = collections.Counter()
    nshared = collections.Counter()
    for r in four:
        ch = r['chains']
        if ch['shared_desc']:
            nshared[len(ch['shared'])] += 1
            for d in ch['shared_desc']:
                cls = ('tilted' if d['h'] in '+-' else 'flush/diamond') + ' ' + ('meeter' if d['meeter_of'] else 'non-meeter')
                C[('FOUR', cls + (', ext-loaded' if d['ext_load'] > 1e-7 else ', no ext'))] += 1
    cols = sorted({k[1] for k in C})
    L += table(C, cols, '## T7. What sits at the crossing (the squares shared by the shortest LR and TB chains; 126 four-crowds)')
    L += ['', 'Shared-square counts per four-crowd: %s.  Interior chains (both chains avoiding every corner meeter): %d / %d.  '
          'Four-crowds whose crossing squares are ALL tilted and externally unloaded: %d.' % (
              dict(sorted(nshared.items())), sum(1 for r in four if r['chains']['LR_interior'] and r['chains']['TB_interior']), len(four),
              sum(1 for r in four if r['chains']['shared_desc'] and all(d['ext_load'] <= 1e-7 and d['h'] in '+-' for d in r['chains']['shared_desc'])))]
    # T8 ends
    C = collections.Counter()
    for r in st:
        for cn, e in r['ends'].items():
            c = [c for c in r['corners'] if c['corner'] == cn][0]
            if not (c['both_loaded'] or c['partner_loaded']):
                continue
            g = 'FOUR' if r['n2'] == 4 else grp(r)
            key = ('both far walls' if len(e['far_walls']) == 2 else ('one far wall' if e['far_walls'] else 'no far wall')) + \
                  (', opposite corner' if e['reaches_opposite_corner'] else (', adjacent corner' if e['other_corners'] else ', no other corner'))
            C[(g, key)] += 1
    cols = sorted({k[1] for k in C})
    L += table(C, cols, '## T8. Where the loaded component of a loaded crowd ENDS (Corollary CHAIN): far walls reached and other corners\' meeters contained')
    both = [r for r in st if r['chains']['LR'] and r['chains']['TB']]
    touch = [r for r in both if not r['chains']['shared']]
    L += ['', 'CROSS-PLANAR on all %d witnesses with both loaded chains: a shared square on %d, only an UNLOADED contact between '
          'the chains on %d (four-crowds among them: %d; e.g. %s), neither on 0.' % (
              len(both), len(both) - len(touch), len(touch), sum(1 for r in touch if r['n2'] == 4),
              ', '.join('%s %s' % (r['name'], r['chains']['touch_only']) for r in touch[:4]))]
    tr = [r for r in rs if r['name'] == 'trump'][0]
    L += ['', 'Trump: TL %s pair (sq4 flat, sq6 at %.2f deg frame), locked; chains LR %s, TB %s, shared %s = the FLUSH square 3 on the left wall (%s).' % (
        tr['corners'][0]['pair_frame'], tr['corners'][0]['members'][1]['tilt_frame_deg'], tr['chains']['LR'], tr['chains']['TB'],
        tr['chains']['shared'], tr['chains']['shared_desc'][0]['edges'])]
    # examples for the pages
    ex = {'same_VE_FJ': [(r['name'], c['corner']) for r in st if grp(r) == 'FJ' for c in r['corners'] if c['locked'] and c['pair_frame'] == 'same' and c['partner_type'] == 'VE'],
          'opposite_HELD': [(r['name'], c['corner']) for r in st if grp(r) == 'HELD' for c in r['corners'] if c['locked'] and c['pair_frame'] == 'opposite'],
          'tilted_crossing_no_ext': [r['name'] for r in four if r['chains']['shared_desc'] and all(d['ext_load'] <= 1e-7 and d['h'] in '+-' for d in r['chains']['shared_desc'])]}
    L += ['', '## Examples (for the pages)', '', '```', json.dumps({k: v[:8] for k, v in ex.items()}), '```']
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(OUT)


def alternates(r):
    g = r['grains']
    hs = {}
    for wn, d in g.items():
        s = {h for h, l in zip(d['h'], d['loaded']) if l and h in '+-'}
        if len(s) != 1:
            return False
        hs[wn] = next(iter(s))
    return hs['x=0'] == hs['x=s'] and hs['y=0'] == hs['y=s'] and hs['x=0'] != hs['y=0']


if __name__ == '__main__':
    main()
