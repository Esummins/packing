"""A108 T1 (contact graph, rigidity, load-bearing) for S07, with all eleven squares free.

Everything is computed with A107's `analyse` machinery: the exact analytic incidence Jacobian
(derivative of the vertex-to-supporting-line distance, rotation lever term included) plus
Fritz-John multipliers from nnls - never a finite difference of a SAT gap.  The only A108 change
is that ALL ELEVEN squares are free (A107 held the six uprights affine in s), so the squares are
handed to `analyse` as slots = (), nfree = 11 and relabelled back into the naming language.

Two configurations are analysed:
  `exact`   - the closed-form landing of exact.py (s = 2 + 4 sqrt2 / 3, every tilted square at
              exactly 45 deg, the two rattlers parked on their slot cells).  This is the one to
              quote: its contacts are exactly zero, not 1e-16.
  `polished` - the raw numerical all-free landing of polish.py, where the rattlers have drifted
              off their slots.  Kept to show that the flex count is a property of the structure
              and not of where the rattlers happen to sit.

Load-bearing test: remove one square (any of the eleven) and re-minimise the remaining ten, all
free.  Reported alongside the Fritz-John force, because the two notions differ here: a square can
carry no contact force at the landing and still raise s*, because deleting it lets the other ten
re-arrange into a different structure.

Outputs results/rigidity.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np

import a108lib as A
from a108lib import AN, MZ
import exact as EX

LBL = {f'f{i}': A.NAMES[i] for i in range(11)}          # analyse's f0..f10 -> A108 names


def relabel(x):
    return LBL.get(x, x)


def analyse_allfree(s, cfg):
    r = AN.analyse((), 11, A.to107(s, cfg))
    for c in r['contacts']:
        c['a'], c['b'] = relabel(c['a']), relabel(c['b'])
    for w in r['walls']:
        w['a'] = relabel(w['a'])
    r['labels'] = [[relabel(l[0]), relabel(l[1])] + list(l[2:]) for l in r['labels']]
    r['binding'] = [[relabel(b[0]), relabel(b[1])] + list(b[2:]) for b in r['binding']]
    r['resultant'] = {f'{relabel(k.split("|")[0])}|{relabel(k.split("|")[1])}': v
                      for k, v in r['resultant'].items()}
    r['degenerate'] = [[relabel(a), relabel(b)] for a, b in r['degenerate']]
    return r


def minimise_subset(s, cfg, drop, ntries=10, seed=0):
    """Remove square `drop` and re-minimise the remaining ten, all free (A107's engine, which
    takes an arbitrary square count; shadow11 is hard-wired to eleven)."""
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


def report(tag, s, cfg, out):
    r = analyse_allfree(s, cfg)
    out[tag] = r
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
    s_e, cfg_e = EX.exact_float()
    out['s_exact_float'] = s_e
    out['names'] = list(A.NAMES)
    report('exact', s_e, cfg_e, out)

    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    report('polished', d['penalty_polish']['s'], [tuple(c) for c in d['penalty_polish']['cfg']], out)

    print('\n=== load-bearing (remove one square, re-minimise the other ten, all free)')
    lb = []
    for i, nm in enumerate(A.NAMES):
        sv = minimise_subset(s_e, cfg_e, i)
        role = 'rattler' if (sv is not None and s_e - sv < 1e-7) else 'load-bearing'
        lb.append(dict(removed=nm, s_without=sv, drop=(s_e - sv) if sv is not None else None,
                       role=role))
        print(f"   remove {nm:9s} -> s* = {'n/a' if sv is None else round(sv, 9)}   "
              f"drop {'n/a' if sv is None else round(s_e - sv, 9)}   {role}")
    out['load_bearing'] = lb
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'rigidity.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/rigidity.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
