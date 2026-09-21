"""A254: summarise results/search254.jsonl -> results/search254.md  ([M] only: a failure to find is not a proof)."""
import json
import os

ATT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
rows = [json.loads(l) for l in open(os.path.join(ATT, 'results', 'search254.jsonl'), encoding='utf-8')]
key = sorted({(r['n'], r['side']) for r in rows})
L = ['# A254 search254 -- FAMILY-STUCK search, general n [M]', '',
     '| n | m | side | starts | feasible packings | family-stuck (Hall min >= 1) | best Hall min among feasible | least penalty |',
     '|---|---|---|---|---|---|---|---|']
for n, s in key:
    R = [r for r in rows if r['n'] == n and r['side'] == s]
    F = [r for r in R if r['feasible']]
    L.append('| %d | %d | %.4f | %d | %d | %d | %s | %.2e |' % (
        n, R[0]['m'], s, len(R), len(F), sum(r['family_stuck'] for r in R),
        max((r['hall_min'] for r in F), default='-'), min(r['penalty'] for r in R)))
open(os.path.join(ATT, 'results', 'search254.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
