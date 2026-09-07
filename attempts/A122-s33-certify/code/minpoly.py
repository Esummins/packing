"""A122 T1 - is s* algebraic of LOW degree?  A PSLQ sweep with an honest acceptance rule.

The rule matters.  PSLQ with a loose tolerance and unbounded coefficients "finds" a relation for
ANY real number: the search space of degree-d integer vectors with |c| <= 10^C carries about d*C
decimal digits of explanatory power, so a hit is meaningless unless d*C is well below the number of
correct digits.  Here s* is computed to ~165 correct digits by the Lagrange Newton of exact.py at
dps = 170, and a relation is accepted only if

    d * log10(maxcoeff) <= 100     and     |sum c_k (s*)^k| < 1e-150,

i.e. 50+ digits of unexplained agreement.  Every rejected hit is recorded too, so the negative
results are auditable.

Outputs results/minpoly.json.
"""
from __future__ import annotations

import json
import os
import time

from mpmath import mp, mpf, pslq

import a122lib as A
import system as SY
import exact as EX

DPS = 170
ACCEPT = 150            # digits of residual required
BUDGET = 100            # d * log10(maxcoeff) ceiling


def hunt(v, label):
    v = mpf(v)
    if abs(v) < mpf(10) ** -100:
        return dict(verdict='zero', note=f'{label} = 0 exactly'), []
    rejected = []
    for logc in (4, 8):
        maxc = 10 ** logc
        for deg in range(1, BUDGET // logc + 1):
            try:
                rel = pslq([v ** k for k in range(deg + 1)], tol=mpf(10) ** -(DPS - 20),
                           maxcoeff=maxc, maxsteps=15000)
            except Exception:
                rel = None
            if not rel:
                continue
            val = sum(mpf(int(c)) * v ** k for k, c in enumerate(rel))
            rec = dict(degree=deg, maxcoeff=maxc, coeffs=[int(c) for c in rel],
                       residual=mp.nstr(val, 5))
            if abs(val) < mpf(10) ** -ACCEPT:
                return dict(verdict='FOUND', **rec), rejected
            rejected.append(rec)
    return dict(verdict='none up to the budget',
                budget=f'degree * log10(maxcoeff) <= {BUDGET}, residual < 1e-{ACCEPT}'), rejected


def main():
    t0 = time.time()
    out = {'dps': DPS, 'accept_digits': ACCEPT, 'budget': BUDGET, 'points': {}}
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        s, cfg = b['sigma'], [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        sysm = SY.System(s, cfg, names)
        x, lam, res = EX.solve_lagrange(sysm, SY.x0_from(s, cfg), dps=DPS, iters=10)
        mp.dps = DPS
        print(f'\n=== {tag}   |F|inf = {mp.nstr(res, 4)}')
        print('  s* =', mp.nstr(x[15], 60))
        rec = dict(s_star=mp.nstr(x[15], 120), lagrange_residual=mp.nstr(res, 5))
        found, rej = hunt(x[15], 's*')
        rec['minpoly_s'] = found
        rec['rejected_s'] = rej
        print('  minpoly(s*):', found)
        if rej:
            print('    rejected (residual too large for the coefficient budget):',
                  [(r['degree'], r['maxcoeff'], mp.nstr(mpf(r['residual']), 2)) for r in rej])
        tl = {}
        for i in ([0,1,2,3,4] if sid == "S38" else [1]):
            th = x[3 * i + 2]
            f, _ = hunt(mp.tan(th), f'tan({names[i]})')
            tl[names[i]] = dict(deg=mp.nstr(th * 180 / mp.pi, 40), tan=mp.nstr(mp.tan(th), 60),
                                minpoly_tan=f)
            print(f'  tan({names[i]}) = {mp.nstr(mp.tan(th), 25)}   {f}')
        rec['tilts'] = tl
        out['points'][tag] = rec

    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'minpoly.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/minpoly.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
