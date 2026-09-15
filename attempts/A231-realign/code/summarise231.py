"""A231 tables from results/realign231.jsonl -> results/realign231.md (per source: swaps, the shrink, the grain
in contact with S, the anchored paths' horns / endpoints / improvements, the per-witness verdicts).
    python summarise231.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'realign231.jsonl')
MD = os.path.join(ATT, 'results', 'realign231.md')
EPS = 1e-6


def load():
    seen, rows = set(), []
    for l in open(RES, encoding='utf-8'):
        r = json.loads(l)
        if r['key'] not in seen:
            seen.add(r['key']); rows.append(r)
    return rows


def frac(a, b):
    return '%d / %d' % (a, b)


def path_stats(rows, name):
    ps = [(r, r['paths'][name]) for r in rows if r.get('paths', {}).get(name, {}).get('s')]
    n = len(ps)
    if not n:
        return None
    c = collections.Counter
    return {'n': n, 'horn': c(p['horn'] for _, p in ps), 'end': c(p['endpoint'] for _, p in ps),
            'blocked': sum(1 for _, p in ps if p['blocked_at'] is not None),
            'free_ok_at_block': sum(1 for _, p in ps if p.get('free_feasible_at_block')),
            'improved': sum(1 for _, p in ps if p['improved']),
            'realign_improves': sum(1 for _, p in ps if p['realign_improves']),
            'monotone': sum(1 for _, p in ps if p['monotone']),
            'L_in_G': sum(1 for _, p in ps if p['L_in_G']), 'L_blocks': sum(1 for _, p in ps if p['L_blocks']),
            'ups': sorted(((p['max_uptick'], r['key']) for r, p in ps), reverse=True)[:4]}


def section(L, rows, src, title):
    cov = sorted({r['wid'] for r in rows if r['src'] == src and r.get('swap') == 'covered by 193'})
    rs = [r for r in rows if r['src'] == src and r.get('swap') != 'covered by 193']
    ok = [r for r in rs if r['status'] == 'ok']
    wids = sorted({r['wid'] for r in rs})
    L += ['## %s' % title, '',
          '| item | count |', '|---|---|',
          '| witnesses (cases = witness x corner) | %d (%d)%s |' % (
              len(wids), len(rs), '; %d further witnesses are among the 193 of section 1 (%s)' % (len(cov), ', '.join(cov)) if cov else ''),
          '| corner swap available (A222 / retraction) | %s |' % frac(len(ok), len(rs)),
          '| the SHRINK (fixed tilts, S pinned, axes free) lowers the side strictly below s0 | %s |' %
          frac(sum(1 for r in ok if r['shrink_improves']), len(ok)),
          '| S touches no tilted square after the shrink (G_comp empty) | %s |' %
          frac(sum(1 for r in ok if not r['grains']['comp']), len(ok)),
          '| S touches tilted squares of ONE handedness / of BOTH | %s / %s |' % (
              frac(sum(1 for r in ok if sum(k in r['grains'] for k in ('g+', 'g-')) == 1), len(ok)),
              frac(sum(1 for r in ok if 'g+' in r['grains'] and 'g-' in r['grains']), len(ok))),
          '| the leftover L is in G_comp | %s |' % frac(sum(1 for r in ok if r['L_in_comp']), len(ok)),
          '| size of G_comp | %s |' % dict(sorted(collections.Counter(len(r['grains']['comp']) for r in ok).items())), '']
    L += ['| anchored path | cases | horn flush-side / kink-side / flat | endpoint flush / kink / start / blocked | '
          'blocked (free axes feasible there) | side < s0 | re-alignment < shrink | non-increasing | L in G / L blocks |',
          '|---|---|---|---|---|---|---|---|---|']
    for name in ('g+A', 'g-A', 'compA', 'compB', 'allA', 'allB'):
        st = path_stats(ok, name)
        if st is None:
            continue
        L.append('| %s | %d | %d / %d / %d | %d / %d / %d / %d | %d (%d) | %s | %s | %s | %d / %d |' % (
            name, st['n'], st['horn']['flush-side'], st['horn']['kink-side'], st['horn']['flat'],
            st['end']['flush'], st['end']['kink'], st['end']['start'], st['end']['blocked'], st['blocked'],
            st['free_ok_at_block'], frac(st['improved'], st['n']), frac(st['realign_improves'], st['n']),
            frac(st['monotone'], st['n']), st['L_in_G'], st['L_blocks']))
    st = path_stats(ok, 'compA')
    if st:
        L += ['', 'Largest upticks of compA: ' + ', '.join('%s %.1e' % (k, u) for u, k in st['ups'])]
    # per-witness verdicts
    per = {}
    for r in rs:
        d = per.setdefault(r['wid'], {'s0': r['s0'], 'swap': 0, 'shrink': 0, 'flush_side_ok': 0, 'any_improve': 0, 'corners': 0})
        d['corners'] += 1
        if r['status'] != 'ok':
            continue
        d['swap'] += 1
        d['shrink'] += r['shrink_improves']
        pa = r['paths'].get('compA', {})
        if pa.get('horn') == 'flush-side' and pa.get('blocked_at') is None and pa.get('improved'):
            d['flush_side_ok'] += 1
        if r['shrink_improves'] or any(p.get('improved') for p in r['paths'].values()):
            d['any_improve'] += 1
    L += ['', '| per witness | count |', '|---|---|',
          '| >= 1 corner swap | %s |' % frac(sum(1 for d in per.values() if d['swap']), len(per)),
          '| >= 1 corner where swap + shrink lowers the side strictly | %s |' % frac(sum(1 for d in per.values() if d['shrink']), len(per)),
          '| >= 1 corner with a FLUSH-SIDE grain in contact with S whose anchored drain (compA) is unblocked and ends below s0 | %s |' %
          frac(sum(1 for d in per.values() if d['flush_side_ok']), len(per)),
          '| >= 1 corner with ANY strict improvement (shrink or a path) | %s |' % frac(sum(1 for d in per.values() if d['any_improve']), len(per)), '']
    return per


def main():
    rows = load()
    L = ['# A231 -- the anchored re-alignment after a corner swap (`realign231.jsonl`, %d rows)' % len(rows), '',
         'Per case (witness x corner with a successful CORNER-SWAP): SHRINK = the fixed-tilt side minimum over the centres with the',
         'settled S pinned to its slot (axes re-selected), s_lp0 <= s0; G_comp = the contact component of S among the tilted squares',
         'at the shrunk configuration, g+/g- = its one-handedness parts touching S, all = every tilted square; the anchored path',
         'rotates G toward alignment in 20 steps with S pinned and the side minimised over the centres at every step (A: the',
         "contacts' axes kept, B: re-selected).  HORN: flush-side if the first step lowers the side, kink-side if it raises it,",
         'flat if unchanged (an unloaded grain).  Endpoint: where the minimum along the path sits.', '']
    p1 = section(L, rows, '193', '1. The ring and the 193 four-crowds (A217 HELD / CROWD; A222 corner swaps)')
    p2 = section(L, rows, 'win40', '2. The 40 window-over-met four-crowds (A222 raise222, window8 d_min >= 1)')
    p3 = section(L, rows, 'a226', '3. The 8 CROWD-ABOVE crowds of A226 (n = 26 .. 55, retraction swap)')
    ring = [r for r in rows if r['rid'] == 'rand_0_0569|t20']
    L += ['## 4. The ring rand_0_0569|t20', '']
    for r in ring:
        if r['status'] != 'ok':
            L.append('* %s: %s' % (r['corner'], r['status'])); continue
        L.append('* %s: s0 %.5f -> shrink %.5f; S touches %s (hands %s); grains %s' % (
            r['corner'], r['s0'], r['s_lp0'], r['S_neighbours'], [r['hand'][i] for i in r['S_neighbours']], r['grains']))
        for k, p in r['paths'].items():
            if p.get('s'):
                L.append('    %s: %s %s s_min %.5f at t %.2f (tilts %s); s = %s' % (
                    k, p['horn'], p['endpoint'], p['s_min'], p['t_min'], p['tilts_at_min_deg'], p['s']))
    a226 = [r for r in rows if r['src'] == 'a226' and r['status'] == 'ok']
    if a226:
        rec = {}
        for l in open(os.path.join(ATT, '..', 'A226-one-flush', 'results', 'crowd226.jsonl'), encoding='utf-8'):
            q = json.loads(l); rec[q['n']] = q['side']
        L += ['', '## 5. A226 crowds: side after swap + shrink against the record', '',
              '| n | crowd side S | record s(n) | corner | s after swap + shrink | below S | G_comp |', '|---|---|---|---|---|---|---|']
        for r in a226:
            L.append('| %d | %.6f | %.6f | %s | %.6f | %s | %s |' % (r['n'], r['s0'], rec.get(r['n'], float('nan')), r['corner'],
                                                                 r['s_lp0'], 'yes' if r['shrink_improves'] else 'no', r['grains']['comp']))
    L += ['', 'Resume block:', '    cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1',
          '    bash attempts/A231-realign/code/run231.sh     # realign231.py --resume, then summarise231.py, pages231.py, commit']
    open(MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('wrote', MD)


if __name__ == '__main__':
    main()
