"""A122 T2 - contact graph, Fritz-John multipliers, first-order rigidity and the load-bearing
subgraph of every A122 landing, with ALL ELEVEN squares free.

Everything is computed with A107's `analyse` machinery: the exact analytic incidence Jacobian
(derivative of the vertex-to-supporting-line distance, rotation lever included) plus Fritz-John
multipliers from nnls - never a finite difference of a SAT gap.  The only A122 change is that all
eleven squares are free (the gallery held the six slot squares affine in s), so the squares are
handed to `analyse` as slots = (), nfree = 11 and relabelled back into the slot/f naming language.

Load-bearing test: remove one square (any of the eleven) and re-minimise the remaining ten, all
free.  Reported alongside the Fritz-John force, because the two notions differ: a square can carry
no contact force and still raise s*, because deleting it lets the other ten re-arrange.

Outputs results/rigidity.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

import a122lib as A
from a122lib import AN, MZ

POINTS = ('S33min', 'S35min', 'S38min')


def labeller(names):
    lbl = {f'f{i}': names[i] for i in range(11)}
    return lambda x: lbl.get(x, x)


def analyse_allfree(s, cfg, names):
    rl = labeller(names)
    r = AN.analyse((), 11, A.to107(s, cfg))
    for c in r['contacts']:
        c['a'], c['b'] = rl(c['a']), rl(c['b'])
    for w in r['walls']:
        w['a'] = rl(w['a'])
    r['labels'] = [[rl(l[0]), rl(l[1])] + list(l[2:]) for l in r['labels']]
    r['binding'] = [[rl(b[0]), rl(b[1])] + list(b[2:]) for b in r['binding']]
    r['resultant'] = {f'{rl(k.split("|")[0])}|{rl(k.split("|")[1])}': v
                      for k, v in r['resultant'].items()}
    r['degenerate'] = [[rl(a), rl(b)] for a, b in r['degenerate']]
    return r


def minimise_subset(s, cfg, drop, ntries=10, seed=0):
    keep = [c for i, c in enumerate(cfg) if i != drop]
    n = len(keep)
    cons = MZ.make_cons((), n)
    rng = np.random.RandomState(1000 + seed + drop)
    best = None
    starts = [A.to107(s, keep)]
    for k in range(ntries):
        z = A.to107(s, keep)
        amp = [0.02, 0.06, 0.15, 0.3][k % 4]
        z[1:] += rng.uniform(-amp, amp, 3 * n)
        starts.append(z)
    for z0 in starts:
        try:
            z, sv, feas = MZ.solve(cons, z0, n)
        except Exception:
            continue
        if feas < -1e-7 or not np.isfinite(sv):
            continue
        ss, cc = A.from107(z)
        sg = A.sigma(*A.normalise(ss, cc))
        if best is None or sg < best:
            best = float(sg)
    return best


def report(tag, s, cfg, names, out):
    r = analyse_allfree(s, cfg, names)
    out[tag] = dict(s=s, names=list(names), analysis=r)
    print(f"\n=== {tag}:  s = {s:.12f}   {len(r['contacts'])} pair contacts, "
          f"{len(r['walls'])} wall contacts")
    for c in r['contacts']:
        f = r['resultant'].get(f"{c['a']}|{c['b']}", 0.0)
        print(f"   {c['a']:9s} - {c['b']:9s} {c['kind']:17s} gap {c['gap']:+.2e}  "
              f"rows {c['nrows']}  force {f:.4f}")
    for w in r['walls']:
        f = r['resultant'].get(f"{w['a']}|{w['b']}", 0.0)
        print(f"   {w['a']:9s} - {w['b']:17s} force {f:.4f}")
    print(f"   rows {r['nrows']}  vars {r['nvars']}  rank {r['rank']}  "
          f"rank at fixed s {r['rank_fixed_s']}/{r['nvars']-1}  FLEXES {r['flexes_fixed_s']}  "
          f"KKT residual {r['kkt_residual']:.2e}")
    for f in r['flat']:
        print(f"     flat {f['dir']}: {f['verdict']}  d(1e-3) {f['delta_1e_3']:+.2e} "
              f"d(1e-2) {f['delta_1e_2']:+.2e}")
    return r


def main():
    t0 = time.time()
    out = {}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    src = {'S33min': 'S33', 'S35min': 'S35', 'S38min': 'S38'}
    for tag, sid in src.items():
        b = d['entries'][sid]['best']
        s = b['sigma']
        cfg = [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        report(tag, s, cfg, names, out)

        print(f'\n--- load-bearing at {tag} (remove one square, re-minimise the other ten, free)')
        lb = []
        for i, nm in enumerate(names):
            sv = minimise_subset(s, cfg, i)
            role = 'rattler/strut' if (sv is not None and s - sv < 1e-7) else 'load-bearing'
            lb.append(dict(removed=nm, s_without=sv, drop=(s - sv) if sv is not None else None,
                           role=role))
            print(f"   remove {nm:9s} -> s* = {'n/a' if sv is None else round(sv, 9)}   "
                  f"drop {'n/a' if sv is None else round(s - sv, 9)}   {role}")
        out[tag]['load_bearing'] = lb

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'rigidity.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/rigidity.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
