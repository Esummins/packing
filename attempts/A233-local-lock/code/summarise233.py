"""A233 summary: results/arm233.jsonl -> results/arm233.md (LOCALITY, the arm census, RADIAL, CHAIN, clusters)."""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
RES = os.path.join(ATT, 'results', 'arm233.jsonl')
OUT = os.path.join(ATT, 'results', 'arm233.md')


def main():
    rs = [json.loads(l) for l in open(RES, encoding='utf-8')]
    L = ['# A233 -- the corner arm on the witnesses (`arm233.py`, %d doubly-met corners of %d witnesses + Trump)' % (
        len(rs), len({r['wid'] for r in rs})), '']
    by = collections.Counter(r['cls'] for r in rs)
    L.append('Corners per class: ' + ', '.join('%s %d' % kv for kv in sorted(by.items())) + '.')
    L.append('')
    L.append('## LOCALITY (every row partner of a meeter: |dc| <= sqrt2 componentwise, centre in [1/2, 1 + 3/sqrt2)^2, body in [0, 1 + 2 sqrt2)^2)')
    L.append('')
    for key in ('partner_within_sqrt2', 'inside_arm_centres', 'inside_arm_points'):
        L.append('* %s: %d / %d' % (key, sum(r['locality'][key] for r in rs), len(rs)))
    L.append('')
    L.append('## The arm census (signature = cells | wall bits | partner contact | holders per meeter | holders that are meeters of another crowd)')
    L.append('')
    sig = collections.defaultdict(list)
    for r in rs:
        sig[r['signature']].append(r)
    L.append('%d distinct signatures.  Top 20:' % len(sig))
    L.append('')
    L.append('| count | cells | walls | partner | holders | cross-crowd holders | classes | example |')
    L.append('|---|---|---|---|---|---|---|---|')
    for k, v in sorted(sig.items(), key=lambda kv: -len(kv[1]))[:20]:
        cells, walls, partner, holders, cross = k.split('|')
        cls = collections.Counter(r['cls'] for r in v)
        L.append('| %d | %s | %s | %s | %s | %s | %s | %s:%s |' % (
            len(v), cells, walls, partner, holders, cross, ' '.join('%s %d' % kv for kv in sorted(cls.items())),
            v[0]['wid'], v[0]['corner']))
    cells = collections.Counter(r['signature'].split('|')[0] for r in rs)
    L.append('')
    L.append('Cell pairs: ' + ', '.join('%s %d' % kv for kv in cells.most_common()) + '.')
    hmax = max(len(m['holders']) for r in rs for m in r['members'])
    rmax = max(m['n_rows'] for r in rs for m in r['members'])
    L.append('Holders per meeter: max %d; rows per meeter (walls + pair rows): max %d.' % (hmax, rmax))
    L.append('Corners with >= 3 meeters: %d.' % sum(r['n_meeters'] >= 3 for r in rs))
    L.append('')
    L.append('## Lemma RADIAL on the bounded FJ stress (U = the meeters; internal = meeter-meeter + corner-wall rows)')
    L.append('')
    rad = [r for r in rs if r['radial']]
    L.append('* corners with a lam0 = 1 stress: %d (no stress / self-stress only: %d)' % (len(rad), len(rs) - len(rad)))
    L.append('* identity Sum_ext + Sum_int = 0: max |residual| %.1e' % max(abs(r['radial']['identity_residual']) for r in rad))
    L.append('* internal term >= 0 on all: %d / %d; strictly > 0 (a loaded internal row): %d' % (
        sum(r['radial']['internal'] >= -1e-7 for r in rad), len(rad), sum(r['radial']['internal'] > 1e-7 for r in rad)))
    src = collections.Counter()
    for r in rad:
        d = r['radial']
        if d['internal'] <= 1e-7:
            continue
        src[('squares' if d['ext_squares'] < -1e-7 else '') + ('+farwall' if d['ext_farwall'] < -1e-7 else '') +
            ('+rows' if d['ext_rows'] < -1e-7 else '')] += 1
    L.append('* who supplies the inward push when the arm is loaded: ' + ', '.join('%s %d' % kv for kv in src.most_common()))
    L.append('')
    L.append('## Corollary CHAIN (the loaded component of the meeters reaches a far wall)')
    L.append('')
    ch = collections.Counter()
    for r in rad:
        c = r['chain']
        if not c['loaded_meeters']:
            ch['meeters unloaded (rattler crowd)'] += 1
        elif c['reaches_farwall']:
            ch['loaded -> reaches a far wall' + (' (+ external rows)' if c['external_rows'] else '')] += 1
        else:
            ch['loaded -> NO far wall (external rows %s)' % c['external_rows']] += 1
    for k, v in ch.most_common():
        L.append('* %s: %d' % (k, v))
    L.append('* loaded component leaves the arm: %d / %d loaded corners' % (
        sum(r['chain']['leaves_arm'] for r in rad if r['chain']['loaded_meeters']), sum(bool(r['chain']['loaded_meeters']) for r in rad)))
    L.append('')
    L.append('## NOCRIT-SEL retreat clusters (geometric closure under pressing; per meeter and cardinal direction)')
    L.append('')
    cl = collections.Counter()
    for r in rs:
        for c in r['clusters']:
            cl[(r['cls'], 'wall-anchored' if c['wall_anchored'] else 'not wall-anchored',
                'contains another crowd\'s meeter' if c['other_corner_meeters'] else 'no other crowd',
                'leaves the arm' if c['leaves_arm'] else 'inside the arm')] += 1
    L.append('| class | wall | other crowd | arm | count |')
    L.append('|---|---|---|---|---|')
    for k, v in sorted(cl.items()):
        L.append('| %s | %s | %s | %s | %d |' % (k + (v,)))
    single = sum(1 for r in rs for c in r['clusters'] if c['size'] == 1)
    L.append('')
    L.append('Clusters of size 1 (the meeter retreats alone -- not a Psi-minimiser): %d of %d.' % (
        single, sum(len(r['clusters']) for r in rs)))
    t = [r for r in rs if r['wid'] == 'trump']
    if t:
        t = t[0]
        L.append('')
        L.append('## Trump (canary), TL: ' + json.dumps({'members': t['members'], 'radial': t['radial'], 'chain': t['chain']}))
    open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:12]))


if __name__ == '__main__':
    main()
