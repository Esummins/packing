"""Honest (c2): interval Krawczyk on FJ(S) with lambda over the WHOLE simplex
box [0,1]^(m+1), which is what T3(c) actually demands (no active-set branch,
no knowledge of the multipliers).  Also measures the complementarity-form
degeneracy and the cheap 0-not-in-F(N) range test."""
import json, random, time
from fractions import Fraction
from mpmath import iv
import numpy as np
import t3lib as T, pilot as P

def probe(box, ab, mn, nsel, seed, tag):
    rng = random.Random(seed)
    pairs = sorted(mn['menus'].keys())
    recs = []
    for _ in range(nsel):
        sel_rows = []
        for p in pairs:
            m = mn['menus'][p]
            sel_rows += m[rng.randrange(len(m))]['straddle']
        rows = list(ab['wall_straddle']) + sel_rows
        m = len(rows); n = 35 + m
        full = [iv.mpf([0.0, 1.0])] * m
        l0 = iv.mpf([0.0, 1.0])
        t0 = time.time()
        exc, which = T.fj_range_exclude(box, rows, l0, full, mode='compl')
        t_range = time.time() - t0
        t0 = time.time()
        k = T.krawczyk_fj(box, rows, l0, full, mode='compl')
        t_kraw = time.time() - t0
        recs.append({'m': m, 'n': n, 'range_excluded': exc,
                     't_range': t_range,
                     'kraw_excluded': k['excluded'], 'kraw_isolated': k['isolated'],
                     'kraw_singular': k['singular'], 'kraw_cond': k['cond'],
                     'kraw_ratio': k.get('ratio'), 't_kraw': t_kraw})
    return {'tag': tag, 'n_selections': nsel, 'records': recs,
            'n_range_excluded': sum(r['range_excluded'] for r in recs),
            'n_kraw_excluded': sum(r['kraw_excluded'] for r in recs),
            'n_kraw_isolated': sum(r['kraw_isolated'] for r in recs),
            'mean_t_range': float(np.mean([r['t_range'] for r in recs])),
            'mean_t_kraw': float(np.mean([r['t_kraw'] for r in recs])),
            'mean_n': float(np.mean([r['n'] for r in recs]))}

out = {}
z0, _ = T.load_trump()
cells = []
cells.append(('P1 (Trump, h=5e-4)', P.build_cell(z0, Fraction(1, 2000),
                                                 z0[33] + Fraction(1, 10**6))))
zl, eta = P.loose_config(3.898)
rng = random.Random(5)
zp = [q + Fraction(rng.uniform(-5e-4, 5e-4)).limit_denominator(10**12)
      for q in zl[:33]] + [Fraction(39, 10)]
zp = P.renormalise(zp, pad=1e-9)
for hw in (0.001, 0.01):
    cells.append(('P3 (5x45 @3.9, h=%g)' % hw,
                  P.build_cell(zp, Fraction(hw).limit_denominator(10**9),
                               Fraction(39, 10))))
for tag, box in cells:
    ab = T.test_ab(box); mn = T.build_menu(box, ab)
    r = probe(box, ab, mn, 10, 4, tag)
    r['menu_size'] = mn['menu_size']
    out[tag] = r
    print('%-26s m~%.0f n~%.0f | range-excl %d/10 (%.3fs) | krawczyk excl %d/10 iso %d/10 sing %d/10 (%.2fs)'
          % (tag, np.mean([x['m'] for x in r['records']]), r['mean_n'],
             r['n_range_excluded'], r['mean_t_range'], r['n_kraw_excluded'],
             r['n_kraw_isolated'], sum(x['kraw_singular'] for x in r['records']),
             r['mean_t_kraw']), flush=True)
json.dump(out, open('results/krawczyk_probe.json', 'w'), indent=1, default=str)
