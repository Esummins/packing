#!/usr/bin/env python3
"""curve_from_sweep.py -- assemble results/curve.json from results/sweep.jsonl (A83).

Groups the exact-checker evaluations: for each (mode, r_c, r_theta) with several T the
largest passing T and the smallest failing T (with its binding check); for each (mode, T)
with several isotropic r the largest passing r; for each (mode, T, r_c) with several
r_theta the largest passing r_theta.  Prints a markdown table.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
rows = [json.loads(l) for l in open(os.path.join(RES, 'sweep.jsonl')) if l.strip()]
# de-duplicate identical evaluations (the sweep was launched twice)
seen, uniq = set(), []
for r in rows:
    key = (r['mode'], r['T'], r['r_c'], r['r_theta'], r['r_s'])
    if key in seen:
        continue
    seen.add(key)
    uniq.append(r)
rows = uniq


def binding(r):
    return [f.split('] ')[-1] for f in r['fails']]


def stat(r):
    return {k: r[k] for k in ('beta', 'psi_over_Xmax', 'x_star', 'n_iter', 'min_tangential',
                              'min_tangential_row', 'Hbar', 'q_vv', 'Hv_l1_tilts')}


out = {'source': 'results/sweep.jsonl (exact checker certs/verify_tube.py, r_s = 0)',
       'n_evaluations': len(rows), 'T_max_at_r': [], 'r_max_at_T': [], 'r_theta_max_at_T_rc': []}
G = defaultdict(list)
for r in rows:
    G[('T', r['mode'], r['r_c'], r['r_theta'])].append(r)
    if r['r_c'] == r['r_theta']:
        G[('r', r['mode'], r['T'])].append(r)
    G[('rt', r['mode'], r['T'], r['r_c'])].append(r)
for key, lst in sorted(G.items(), key=lambda kv: str(kv[0])):
    kind = key[0]
    var = {'T': 'T_float', 'r': 'r_c_float', 'rt': 'r_theta_float'}[kind]
    vals = sorted(set(r[var] for r in lst))
    if len(vals) < 3:
        continue
    passing = [r for r in lst if r['PASS']]
    failing = [r for r in lst if not r['PASS']]
    best = max(passing, key=lambda r: r[var]) if passing else None
    worst = min(failing, key=lambda r: r[var]) if failing else None
    rec = dict(mode=key[1], n=len(lst),
               best_pass=(best[var] if best else None),
               best_pass_frac=(best[{'T': 'T', 'r': 'r_c', 'rt': 'r_theta'}[kind]] if best else None),
               first_fail=(worst[var] if worst else None),
               binding=(binding(worst) if worst else None),
               pass_stats=(stat(best) if best else None))
    if kind == 'T':
        rec.update(r_c=lst[0]['r_c_float'], r_theta=lst[0]['r_theta_float'])
        out['T_max_at_r'].append(rec)
    elif kind == 'r':
        rec.update(T=lst[0]['T_float'])
        out['r_max_at_T'].append(rec)
    else:
        rec.update(T=lst[0]['T_float'], r_c=lst[0]['r_c_float'])
        out['r_theta_max_at_T_rc'].append(rec)
with open(os.path.join(RES, 'curve.json'), 'w') as f:
    json.dump(out, f, indent=1)

print('| mode | r_c | r_theta | T_max (PASS) | first FAIL | binding | beta | psi/X | tan margin (row) |')
print('|---|---|---|---|---|---|---|---|---|')
for r in sorted(out['T_max_at_r'], key=lambda r: (r['mode'], r['r_c'], r['r_theta'])):
    s = r['pass_stats'] or {}
    print('| %s | %.2e | %.2e | %.5f | %.5f | %s | %.3f | %.3f | %.5f (%s) |' % (
        r['mode'], r['r_c'], r['r_theta'], r['best_pass'] or 0, r['first_fail'] or 0,
        (r['binding'] or ['-'])[0][:38], s.get('beta', 0), s.get('psi_over_Xmax', 0),
        s.get('min_tangential', 0), s.get('min_tangential_row', '')))
print()
print('| mode | T | r_max (isotropic, PASS) | first FAIL | binding | beta | psi/X | tan margin |')
print('|---|---|---|---|---|---|---|---|')
for r in sorted(out['r_max_at_T'], key=lambda r: (r['mode'], r['T'])):
    s = r['pass_stats'] or {}
    print('| %s | %.5f | %s | %.2e | %s | %.3f | %.3f | %.5f |' % (
        r['mode'], r['T'], ('%.4e' % r['best_pass']) if r['best_pass'] else 'none',
        r['first_fail'] or 0, (r['binding'] or ['-'])[0][:38], s.get('beta', 0),
        s.get('psi_over_Xmax', 0), s.get('min_tangential', 0)))
print()
print('| mode | T | r_c | r_theta_max (PASS) | first FAIL | binding |')
print('|---|---|---|---|---|---|')
for r in sorted(out['r_theta_max_at_T_rc'], key=lambda r: (r['mode'], r['T'], r['r_c'])):
    print('| %s | %.4f | %.2e | %s | %.2e | %s |' % (
        r['mode'], r['T'], r['r_c'], ('%.4e' % r['best_pass']) if r['best_pass'] else 'none',
        r['first_fail'] or 0, (r['binding'] or ['-'])[0][:38]))
