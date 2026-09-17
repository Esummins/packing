"""A250 self-tests: the neighbourhoods against geometry, the penalty against A244, the family
report against a brute-force scan, and the exact verifier on a known twelve-stuck packing."""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C          # noqa: E402
import fast244 as F4          # noqa: E402
import fam250 as FM           # noqa: E402
import fast250 as F5          # noqa: E402
import count250 as K          # noqa: E402
import verify250 as V5        # noqa: E402

OK = []


def chk(name, cond, extra=''):
    OK.append(bool(cond))
    print('%-46s %s %s' % (name, 'ok' if cond else 'FAIL', extra), flush=True)


def main():
    s = 3.877084
    # 1. the five-cell neighbourhood is exactly what A247's witness meets
    z = np.zeros(34)
    z[0], z[1], z[2], z[33] = 1.393, 1.393, 0.0, s
    for i in range(1, 11):
        z[3 * i] = z[3 * i + 1] = 50 + 3 * i
    met = {c for c, v in C.meeter_sets(z).items() if 0 in v}
    chk('N_BL = the witness cell-set', met == set(K.NBR['BL']), sorted(met))
    # 2. every slot lies in exactly two neighbourhoods, every box in one
    cnt = {c: sum(c in K.NBR[d] for d in K.NBR) for c in FM.CELLS}
    chk('each slot in 2 neighbourhoods, box in 1',
        all(cnt[c] == (1 if c.endswith('00') else 2) for c in FM.CELLS))
    # 3. conflicts: the four facing slot pairs below 4, none at or above 4
    chk('4 conflicting cell pairs below 4', len(FM.conflicts(3.99)) == 4)
    chk('0 conflicting cell pairs at 4', len(FM.conflicts(4.0)) == 0)
    chk('max family 8 below 4 / 12 at 4',
        FM.max_family_size(3.99) == 8 and FM.max_family_size(4.0) == 12)
    # 4. the kmax = 1 penalty IS A244's twelve-cell penalty
    rng = np.random.default_rng(1)
    w = np.zeros(34)
    w[0:33:3] = rng.uniform(0.7, 3.3, 11)
    w[1:33:3] = rng.uniform(0.7, 3.3, 11)
    w[2:33:3] = rng.uniform(0, 1.57, 11)
    w[33] = 3.95
    f4, g4 = F4.penalty(w, list(C.CELLS), 0.01, True, 0.1)
    f5, g5 = F5.penalty(w, F5.rows_for_side(3.95, 1), 0.01, True, 0.1)
    chk('kmax=1 penalty == A244', f4 == f5 and float(np.abs(g4 - g5).max()) == 0.0)
    f0, err, nr = F5.check_grad(kmax=3)
    chk('family gradient vs finite differences', err < 1e-6, '%.2e' % err)
    # 5. family_report against a brute-force scan on a random meeter table
    ms = {c: sorted(rng.choice(11, size=int(rng.integers(0, 4)), replace=False).tolist())
          for c in FM.CELLS}
    rep = FM.family_report(ms, 3.95, kmax=12)
    conf = FM.conflicts(3.95)
    worst = None
    for k in range(1, 13):
        for comb in itertools.combinations(range(12), k):
            if any((i, j) in conf for i, j in itertools.combinations(comb, 2)):
                continue
            u = set()
            for i in comb:
                u |= set(ms[FM.CELLS[i]])
            worst = len(u) - k if worst is None else min(worst, len(u) - k)
    chk('family_report == brute force', rep['min_excess'] == worst, rep['min_excess'])
    # 6. the exact verifier on A244's first certified twelve-stuck packing
    r = json.loads(open(os.path.join(
        ROOT, 'attempts/A244-twelve-stuck/results/twelve244.jsonl')).readline())
    c = V5.certify_z(r['z'])
    chk('corpus packing certified NOT family-stuck',
        c['contained'] and c['disjoint'] and c['NOT_FAMILY_STUCK'] and not c['FAMILY_STUCK'],
        'witness %s' % (c['witness_families'][0]['cells'] if c['witness_families'] else None))
    # 7. the count's headline numbers
    chk('count: 13 needed at s >= 4', K.solve('at4', 12, 4, verbose=False)['n_min'] == 13)
    chk('count: 9 needed below 4', K.solve('below4', 12, 5, verbose=False)['n_min'] == 9)
    print('%d/%d ok' % (sum(OK), len(OK)))
    return 0 if all(OK) else 1


if __name__ == '__main__':
    sys.exit(main())
