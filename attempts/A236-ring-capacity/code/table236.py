"""A236 the n-table (docs/proofs/ring_capacity.md s.3): for n = 5..60 the capacity count of a four-crowd below
m = ceil(sqrt n) -- band squares B <= 4(m - 2) (Lemma BAND-COUNT), core squares K <= N(s - 2) (Lemma CORE-CAP, the
proven staircase and the record staircase), straddlers X >= 4 (ONE-TILTED) -- against n, and the flat-core ring
bound p >= n - (m - 3)^2 against the band's 4(m - 1) toucher slots.  The count closes for NO n: B_max + K_max + 4 =
m^2 - 3 >= n (Theorem NO-CLOSURE).  Records: the survey's 21 below m; s(n) = m otherwise (n <= 64: Ellsworth's page as
read by A226 has no record below m for the other n <= 55; 56..60 assumed = 8, no record below 8 is known to the lab).
    python table236.py   -> results/table236.md, results/table236.jsonl
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import band236 as BD                                                   # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT_MD = os.path.join(ATT, 'results', 'table236.md')
OUT_JL = os.path.join(ATT, 'results', 'table236.jsonl')
CROWD_ABOVE = {26, 28, 29, 37, 40, 50, 51, 55}      # one_flush.md s.3: four-crowds exist at every side in (s(n), m)


def row(n, rec):
    m = math.ceil(math.sqrt(n))
    s = rec[n]
    below = s < m - 1e-9
    proven = n in BD.PROVEN and abs(BD.PROVEN[n] - s) < 1e-9
    sigma = s - 2.0
    Np, Nr = BD.N_proved(sigma), BD.N_record(sigma, rec)
    Bmax = 4 * (m - 2)
    Kmax_general = max(0, (m - 2) ** 2 - 3) if m >= 4 else 0     # Nagamochi: N(sigma) <= (m-2)^2 - 3 for sigma < m-2
    X_forced_p = max(4, n - Bmax - Np)
    X_forced_r = max(4, n - Bmax - Nr)
    slack = Bmax + Kmax_general + 4 - n                            # = m^2 - 3 - n >= 0 whenever below
    p_flat_core = n - max(0, (m - 3) ** 2)                         # a ring with a FLAT core: n - p <= (m-3)^2
    return {'n': n, 'm': m, 's': s, 'below_m': below, 'proven': proven, 'floor_s': math.floor(s + 1e-9),
            'sigma': sigma, 'N_proved': Np, 'N_record': Nr, 'K_max_general': Kmax_general, 'B_max': Bmax,
            'X_forced_proved': X_forced_p, 'X_forced_record': X_forced_r, 'count_slack': slack,
            'closes': slack < 0, 'p_flat_core_min': p_flat_core, 'toucher_slots': 4 * (m - 1),
            'ring_slack_flat_core': 4 * (m - 1) - p_flat_core,
            'crowd_above': n in CROWD_ABOVE, 'regime': s > 2 + math.sqrt(2) + 1e-9}


def main():
    rec = BD.records()
    rows = [row(n, rec) for n in range(5, 61)]
    with open(OUT_JL, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    L = ['# A236 -- the capacity count for n = 5..60 (four-crowds below m = ceil(sqrt n))', '',
         'Columns: s = record side (survey226; = m where no record below m is known; **proven** where s(n) is a theorem);',
         'sigma = s - 2 (the centre\'s side); N_p / N_r = the centre\'s packing number from the proven / record staircase;',
         'B_max = 4(m - 2) band squares (Lemma BAND-COUNT); K_max = (m - 2)^2 - 3 (Nagamochi, sigma < m - 2);',
         'X_forced = max(4, n - B_max - N) straddlers forced by the count; slack = B_max + K_max + 4 - n = m^2 - 3 - n;',
         'p_min(flat core) = n - (m - 3)^2 ring members if every non-ring square is flat and in the core (Lemma FLUSH),',
         'against the 4(m - 1) toucher slots of the band (WALL-EXCESS); CROWD-ABOVE = four-crowds exist at every side',
         'in (s(n), m) (A226), so no all-four-crowd inequality can close there.  Rows with s(n) = m are out of scope',
         '(no packing below m; shown for completeness).  s > 2 + sqrt2 is the regime of TILT-BAND / distinct meeters.', '',
         '| n | m | s(n) | below m | sigma | N_p | N_r | B_max | K_max | X_forced (p / r) | slack m^2-3-n | closes? | p_min flat core | toucher slots | CROWD-ABOVE |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if not r['below_m']:
            L.append('| %d | %d | %g (= m) | no | -- | -- | -- | -- | -- | -- | -- | out of scope | -- | -- | -- |' % (r['n'], r['m'], r['s']))
            continue
        L.append('| %d | %d | %.4f%s | yes | %.3f | %d | %d | %d | %d | %d / %d | %d | %s | %d | %d | %s |' % (
            r['n'], r['m'], r['s'], ' (proven)' if r['proven'] else '', r['sigma'], r['N_proved'], r['N_record'],
            r['B_max'], r['K_max_general'], r['X_forced_proved'], r['X_forced_record'], r['count_slack'],
            'NO' if not r['closes'] else 'yes', r['p_flat_core_min'], r['toucher_slots'], 'yes' if r['crowd_above'] else ''))
    below = [r for r in rows if r['below_m']]
    L += ['', '**Reading.**  %d of the %d values n = 5..60 pack below m; the count slack m^2 - 3 - n is >= %d on every one'
          ' of them (min at n = %s) and the count closes for none.  X_forced exceeds the trivial 4 (ONE-TILTED) only at'
          ' n = %s (proven staircase) / %s (record staircase): elsewhere the band and the core alone have room for n.'
          '  The flat-core ring variant (every non-ring square flat and inside the core, every ring member a wall toucher)'
          ' needs p >= n - (m-3)^2 members against 4(m-1) toucher slots: it closes only at n = %s (n > m^2 - 2m + 5), under'
          ' hypotheses no stability argument supplies (rattlers tilt; ring members hover).' % (
              len(below), len(rows), min(r['count_slack'] for r in below),
              ', '.join(str(r['n']) for r in below if r['count_slack'] == min(x['count_slack'] for x in below)),
              ', '.join(str(r['n']) for r in below if r['X_forced_proved'] > 4) or 'none',
              ', '.join(str(r['n']) for r in below if r['X_forced_record'] > 4) or 'none',
              ', '.join(str(r['n']) for r in below if r['ring_slack_flat_core'] < 0) or 'none')]
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[-2:]))


if __name__ == '__main__':
    main()
