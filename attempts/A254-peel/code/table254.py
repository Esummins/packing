"""A254 PEEL table: for every n <= 100 with record s(n) < m = ceil(sqrt n): m, k = m^2 - n, n' = n - 4(m-2),
the best PROVED lower bound on s(n'), the record s(n'), the record s(n), and PEEL's verdicts.

  tight  = 2 + LB(n')              [T] the tight pinwheel (all wall gaps 0): no such structure below this side
  slack  = (LB(n') + m + 1) / 2    [T] the whole flush stratum (wall gaps up to s - m + 1, pokes <= gap/2 a side)

Records: docs/papers/ellsworth_squares_in_squares.txt (local copy of Ellsworth's page, 2026) cross-checked against
A226's survey (the 21 packings <= 55 the lab holds as poses).  Proved: Goebel 5; Kearney-Shiu / Friedman 6-8;
Stromquist 10 and s(11) >= 2 + 4/sqrt5; Bentz 13, 46, 22, 33; Nagamochi 2005 Thm 2: s(j^2-1) = s(j^2-2) = j and
s(N) >= sqrt(N - 2 floor(sqrt N) + 1) + 1; monotonicity of s.  The lab's own certified s(11) >= 3.82 is kept in a
separate column (T-computed, not literature).
    python table254.py        -> results/peel254_table.jsonl, results/peel254_table.md
"""
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
TXT = os.path.join(ROOT, 'docs', 'papers', 'ellsworth_squares_in_squares.txt')
SURVEY = os.path.join(ROOT, 'attempts', 'A226-one-flush-theory', 'results', 'survey226.jsonl')
SQ2 = math.sqrt(2)
NMAX = 100


def records():
    """{n: record side} for n <= 140 from the local copy of Ellsworth's page; unlisted n default to ceil sqrt n."""
    rec, cur = {}, None
    for line in open(TXT, encoding='utf-8'):
        m = re.match(r'^ (\d+)(?:, (\d+))* \[A square-', line)
        if m:
            cur = [int(t) for t in re.findall(r'\d+', line.split('[A')[0])]
            continue
        if cur is None:
            continue
        v = re.search(r'\\Nn\{([0-9.]+)\}', line) or re.search(r'\$s = (\d+)\$', line)
        if v:
            for n in cur:
                rec.setdefault(n, float(v.group(1)))
            cur = None
    for n in range(1, 141):
        c = float(math.ceil(math.sqrt(n)))
        rec[n] = min(rec.get(n, c), c)
    return rec


def survey():
    out = {}
    if os.path.exists(SURVEY):
        for l in open(SURVEY, encoding='utf-8'):
            r = json.loads(l)
            out[r['n']] = min(out.get(r['n'], 99.0), r['side'])
    return out


PROVEN = {1: (1.0, 'trivial'), 2: (2.0, 'Goebel'), 5: (2 + 1 / SQ2, 'Goebel 1979'), 6: (3.0, 'Kearney-Shiu 2002'),
          10: (3 + 1 / SQ2, 'Stromquist 2003'), 11: (2 + 4 / math.sqrt(5), 'Stromquist 2003 (bound)'),
          13: (4.0, 'Bentz 2010'), 22: (5.0, 'Bentz 2018'), 33: (6.0, 'Bentz 2018'), 46: (7.0, 'Bentz 2010')}
for _j in range(2, 13):
    PROVEN.setdefault(_j * _j - 2, (float(_j), 'Nagamochi 2005 Thm 2(i)'))
LAB = {11: (3.82, 'lab certificate (T-computed)')}


def proved_lower(n, lab=False):
    """(bound, source): max over j <= n of proved values (s monotone) and Nagamochi's Thm 2(ii) at j."""
    best, src = 0.0, ''
    table = dict(PROVEN)
    if lab:
        table.update(LAB)
    for j in range(1, n + 1):
        cands = []
        if j in table:
            cands.append(table[j])
        if j >= 4:
            r = math.isqrt(j)
            if r * r != j:
                cands.append((min(r + 1.0, math.sqrt(j - 2 * r + 1) + 1), 'Nagamochi 2005 Thm 2(ii)'))
            else:
                cands.append((float(r), 'trivial area'))
        for v, s_ in cands:
            if v > best + 1e-12:
                best, src = v, s_ + ('' if j == n else ' at %d' % j)
    return best, src


def verdict(rec_n, m, lb, rec_np):
    tight = 2 + lb
    if tight >= m - 1e-12:
        return 'THEOREM-WINDOW'          # no tight pinwheel anywhere below m, by proved bounds
    if tight > rec_n + 1e-9:
        return 'THEOREM-AT-RECORD'       # none at the record side, by proved bounds; open on (2+lb, m)
    if 2 + rec_np > rec_n + 1e-9:
        return 'RECORDS-ONLY'            # excluded at the record side only if the record s(n') is optimal
    if abs(2 + rec_np - rec_n) <= 1e-9:
        return 'EQUALITY'
    return 'NOT-EXCLUDED'


def main():
    rec, sv = records(), survey()
    rows = []
    for n in range(5, NMAX + 1):
        m = math.ceil(math.sqrt(n) - 1e-12)
        if rec[n] >= m - 1e-12:
            continue
        k, ring = m * m - n, 4 * (m - 2)
        np_ = n - ring
        lb, src = proved_lower(np_)
        lbl, _ = proved_lower(np_, lab=True)
        rows.append(dict(n=n, m=m, k=k, ring=ring, n_inner=np_, lb_inner=lb, lb_src=src, lb_inner_lab=lbl,
                         rec_inner=rec[np_], rec_n=rec[n], survey_n=sv.get(n), lb_n=proved_lower(n)[0],
                         tight=2 + lb, tight_lab=2 + lbl, slack=(lb + m + 1) / 2, tight_rec=2 + rec[np_],
                         verdict=verdict(rec[n], m, lb, rec[np_]), verdict_lab=verdict(rec[n], m, lbl, rec[np_])))
    os.makedirs(os.path.join(ATT, 'results'), exist_ok=True)
    with open(os.path.join(ATT, 'results', 'peel254_table.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    L = ['# A254 PEEL table (n <= %d below ceil sqrt n: %d values)' % (NMAX, len(rows)), '',
         'tight = 2 + LB(n\') [T]; slack = (LB(n\') + m + 1)/2 [T]; rec = record.  Verdict on the TIGHT pinwheel.', '',
         '| n | m | k | n\' | LB(n\') proved | source | rec s(n\') | rec s(n) | tight | slack | 2+rec(n\') | verdict | with lab 3.82 |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        L.append('| %d | %d | %d | %d | %.6f | %s | %.6f | %.6f | %.6f | %.6f | %.6f | %s | %s |' % (
            r['n'], r['m'], r['k'], r['n_inner'], r['lb_inner'], r['lb_src'], r['rec_inner'], r['rec_n'], r['tight'],
            r['slack'], r['tight_rec'], r['verdict'], r['verdict_lab']))
    cnt = {}
    for r in rows:
        cnt[r['verdict']] = cnt.get(r['verdict'], 0) + 1
    L += ['', 'Counts: ' + ', '.join('%s %d' % kv for kv in sorted(cnt.items())), '',
          'Survey cross-check (|Ellsworth - A226| > 1e-5): ' + (', '.join(
              'n=%d %.6f vs %.6f' % (r['n'], r['rec_n'], r['survey_n']) for r in rows
              if r['survey_n'] and abs(r['survey_n'] - r['rec_n']) > 1e-5) or 'none')]
    open(os.path.join(ATT, 'results', 'peel254_table.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
