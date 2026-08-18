#!/usr/bin/env python3
"""summarize.py -- table from results.jsonl: per n the best run, plus per-run listing. Prints markdown."""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'records.json')))
rows = [json.loads(l) for l in open(os.path.join(HERE, 'results.jsonl')) if l.strip()]
byn = defaultdict(list)
for r in rows:
    byn[r['n']].append(r)


def ang(a):
    return '{' + ','.join(f'{x:.4g}' if x != int(x) else str(int(x)) for x in a) + '}'


print('| n | record | best MILP s | gap | Θ (best run) | mode | solver status | t_limit | structure |')
print('|---|---|---|---|---|---|---|---|---|')
matches, beats = [], []
for n in sorted(byn):
    rs = byn[n]
    rec = R[str(n)]['record']
    good = [r for r in rs if r.get('s') is not None]
    if good:
        b = min(good, key=lambda r: r['s'])
        gap = b['s'] - rec
        mode = f"fix {b['fix_s']:.4f}" if b.get('fix_s') is not None else 'free'
        flag = ' **MATCH**' if abs(gap) <= 1e-6 else (' **BEAT**' if gap < -1e-9 else '')
        print(f"| {n} | {rec:.10f} | {b['s']:.10f}{flag} | {gap:+.2e} | {ang(b['angles'])} | {mode} | {b.get('status')} | "
              f"{b['time_limit']} | {b.get('structure')} |")
        if abs(gap) <= 1e-6:
            matches.append((n, b))
        if gap < -1e-9:
            beats.append((n, b))
    else:
        b = rs[0]
        mode = f"fix {b['fix_s']:.4f}" if b.get('fix_s') is not None else 'free'
        print(f"| {n} | {rec:.10f} | none | — | {ang(b['angles'])} | {mode} | {b.get('status')} | {b['time_limit']} | — |")
print()
print('All runs:')
print('| n | Θ | mode | s | gap | status | bound | wall s | structure | cert |')
print('|---|---|---|---|---|---|---|---|---|---|')
for r in sorted(rows, key=lambda r: (r['n'], r['id'])):
    mode = f"fix {r['fix_s']:.4f}" if r.get('fix_s') is not None else 'free'
    s = f"{r['s']:.10f}" if r.get('s') is not None else 'none'
    gap = f"{r['gap']:+.2e}" if r.get('gap') is not None else '—'
    cert = 'PASS' if r.get('cert_rc') == 0 else ('FAIL' if r.get('cert_rc') is not None else '')
    print(f"| {r['n']} | {ang(r['angles'])} | {mode} | {s} | {gap} | {r.get('status')} | {r.get('bound')} | "
          f"{r['wall']:.0f} | {r.get('structure')} | {cert} |")
print()
print('MATCHES:', [(n, b['s']) for n, b in matches])
print('BEATS:', [(n, b['s']) for n, b in beats])
