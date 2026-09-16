"""A237 summary -> results/pocket237.md from tiltmin237.jsonl, pocket237.jsonl, family237.jsonl, table237.jsonl."""
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')


def rows(name):
    p = os.path.join(RES, name)
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def main():
    T, P, F, TB = rows('tiltmin237.jsonl'), rows('pocket237.jsonl'), rows('family237.jsonl'), rows('table237.jsonl')
    L = ['# A237 -- POCKET WASTE: TILT-MIN, the JAGGED census and POCKET-CAP, measured', '',
         'Sources: the ring `rand_0_0569|t20` + the 193 HELD / CROWD four-crowds of A217 (loaded component U from A233), '
         "A226's nine crowd rings at n = 11, the 21 records + Trump; the window family ring(S, theta) of `family237.py`.  "
         'Waste = the rigorous coverable-set sandwich over 1-degree tilt bins (`geom237.py`); PIERCE(k) = a k-point piercing '
         'certificate of capacity <= k.  `bash attempts/A237-pocket-waste/code/run237.sh` reruns everything.', '',
         '## 1. Lemma TILT-MIN on the doubly-met corners (`tiltmin237.jsonl`)', '']
    n = len(T)
    pairs = [p for r in T for p in r['pairs'] if 'partner' in p]
    held = [r for r in T if r['src'] == 'HELD']
    L += ['| check | holds on |', '|---|---|',
          '| ONE-TILTED: a tilted meeter at every doubly-met corner | %d / %d corners |' % (sum(r['one_tilted'] for r in T), n),
          '| TILT-MIN (b): flat wall meeter at offset delta, tilted partner theta: sin theta <= delta | %d / %d flat-tilted pairs |' % (sum(p['sin_le_delta'] for p in pairs), len(pairs)),
          "| TILT-MIN (b'): the partner's lowest point >= 1 - (delta - sin theta) tan theta | %d / %d |" % (sum(p['low_ok'] for p in pairs), len(pairs)),
          '| DEPTH-BUDGET: d_A + d_B <= 1 for every pair of meeters | %d / %d corners (max %.4f, median %.4f) |' % (
              sum(r['depth_budget_ok'] for r in T), n, max(r['depth_sum_max_pair'] for r in T), st.median(r['depth_sum_max_pair'] for r in T)),
          '| hovering flat meeters (touching no wall) | %d |' % sum(1 for r in T for p in r['pairs'] if p.get('hover')),
          '| HELD corners whose least tilt sits AT the imposed floor tmin_deg = 10 | %d / %d |' % (sum(r['at_floor'] for r in held), len(held))]
    sl = sorted(p['theta_max_deg'] - p['theta_deg'] for p in pairs)
    if sl:
        L += ['', 'Slack of the tilt bound arcsin(delta) - theta on the flat-tilted pairs: min %.2f deg, median %.2f deg; '
              'the flat meeters sit at offsets delta = %.3f .. %.3f.' % (sl[0], sl[len(sl) // 2], min(p['delta'] for p in pairs), max(p['delta'] for p in pairs))]
    tr = [r for r in T if r['label'] == 'trump']
    for r in tr:
        L += ['Trump %s: tilts %s, depths %s, pairs %s.' % (r['corner'], {k: round(v, 3) for k, v in r['tilts'].items()},
              {k: round(v, 4) for k, v in r['depths'].items()}, [(p['flat'], p.get('partner'), round(p.get('delta', 0), 4), round(p.get('theta_deg', 0), 2), round(p.get('theta_max_deg', 0), 2)) for p in r['pairs']])]
    L += ['', '## 2. The pockets (`pocket237.jsonl`)', '']
    W = [r for r in P if r['src'] == '193']
    Wk = [r for r in W if r['k'] > 0]
    L += ['**The ring + 193 four-crowds** (%d with a loaded component; %d with n - p > 0 rattlers in the pocket):' % (len(W), len(Wk)),
          '- soundness (coverable area >= n - p, the rattlers ARE in the coverable set): %d / %d; the area bound fires on %d (as it must not: they are packings).' % (sum(r['sound'] for r in W), len(W), sum(r['area_bound_fires'] for r in W)),
          '- waste: min %.2f, median %.2f, max %.2f (pocket area median %.2f); coverable - (n - p) slack: min %.3f, median %.3f.' % (
              min(r['waste'] for r in W), st.median(r['waste'] for r in W), max(r['waste'] for r in W), st.median(r['area'] for r in W),
              min(r['coverable'] - r['k'] for r in Wk), st.median(r['coverable'] - r['k'] for r in Wk)),
          '- PIERCE(n - p) with the rattlers\' own centres: certifies %d / %d (the rattlers can usually slide).' % (sum(r.get('pierce_k_ok', False) for r in Wk), len(Wk)),
          '- features: convex vertices median %d (acute, i.e. < 90: %d rows have one), reflex median %d, tilted boundary edges median %d.' % (
              st.median(r['features']['n_convex'] for r in W), sum(r['features']['n_acute'] > 0 for r in W),
              st.median(r['features']['n_reflex'] for r in W), st.median(r['features']['n_tilted_edges'] for r in W))]
    rg = [r for r in W if r.get('rid') == 'rand_0_0569|t20']
    if rg:
        r = rg[0]
        L += ['', '**The ring** (side %.4f, p = %d, rattlers %d): pocket area %.3f, coverable %.3f, waste %.3f (%d uncoverable components, '
              'the largest %.3f at (%.2f, %.2f)); PIERCE(2) with the rattler centres: residual %.3f (not certified).' % (
                  r['s'], r['p'], r['k'], r['area'], r['coverable'], r['waste'], r['n_components'], r['components'][0]['area'],
                  r['components'][0]['cx'], r['components'][0]['cy'], r['pierce_k'])]
    L += ['', "**A226's crowd rings** (n = 11, S < 4):", '',
          '| ring | area | coverable | waste | PIERCE(1) residual (best point) | capacity <= 1 certified | A226 greedy |', '|---|---|---|---|---|---|---|']
    for r in [x for x in P if x['src'] == 'ring11']:
        L.append('| %s | %.3f | %.3f | %.3f | %.1e at (%.3f, %.3f) | %s | %d |' % (
            r['label'], r['area'], r['coverable'], r['waste'], r['pierce1'], r['pierce1_pt'][0], r['pierce1_pt'][1], 'YES' if r['pierce1_ok'] else 'no', r['a226_kmax']))
    R = [r for r in P if r['src'] == 'record']
    L += ['', '**The records** (U = the wall touchers; %d): sound %d / %d, the area bound fires on %d (it must not); waste min %.2f median %.2f max %.2f; '
          'PIERCE(n - p) with the interior squares\' centres: %d / %d.' % (len(R), sum(r['sound'] for r in R), len(R), sum(r['area_bound_fires'] for r in R),
                                                                        min(r['waste'] for r in R), st.median(r['waste'] for r in R), max(r['waste'] for r in R), sum(r.get('pierce_k_ok', False) for r in R), len(R)),
          '', '| record | n | s | p | n - p | area | coverable | waste |', '|---|---|---|---|---|---|---|---|']
    for r in R:
        L.append('| %s | %d | %.4f | %d | %d | %.2f | %.2f | %.2f |' % (r['label'], r['n'], r['s'], r['p'], r['k'], r['area'], r['coverable'], r['waste']))
    L += ['', '## 3. The n = 11 window family ring(S, theta) (`family237.jsonl`)', '',
          '| S | theta | delta | packing | four-crowd | area | coverable | waste | PIERCE(1) centre | PIERCE(2) | greedy cap | closes |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in F:
        cl = 'PIERCE(1)' if r['pierce1'] <= 1e-9 else ('PIERCE(2)' if r['pierce2_ok'] else ('area' if r['closes_area'] else 'no'))
        L.append('| %.3f | %d | %.3f | %s | %s | %.3f | %.3f | %.3f | %.1e | %.4f | %s | %s |' % (
            r['S'], r['theta'], r['delta'], r['packing_ok'], r['four_crowd'], r['area'], r['coverable'], r['waste'], r['pierce1'], r['pierce2'], r['greedy_capacity'], cl))
    L += ['', '## 4. The n-general table (`table237.jsonl`): the area bound 4 w_c(theta) > s(n)^2 - n', '']
    if TB:
        wc = TB[0]['corner_waste']
        L += ['One-corner sealed waste w_c(theta) (flat meeter at the least offset sin theta + 0.02, partner at tilt theta, in a side-6 box): ' +
              ', '.join('%s deg: %.3f' % (t, wc[t]) for t in ('5', '10', '15', '20', '30', '45')), '',
              '| n | m | s(n) | s^2 - n | 4 w_c(10) | 4 w_c(20) | 4 w_c(45) | least tilt floor theta* that closes |', '|---|---|---|---|---|---|---|---|']
        for r in TB[1:]:
            L.append('| %d | %d | %.4f | %.3f | %.3f | %.3f | %.3f | %s |' % (r['n'], r['m'], r['s'], r['area_slack'], r['w4_at_10'], r['w4_at_20'], r['w4_at_45'], r['theta_star'] if r['theta_star'] else 'none'))
    open(os.path.join(RES, 'pocket237.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('wrote pocket237.md')


if __name__ == '__main__':
    main()
