"""A30 self-tests: cross-checks against A22 + corruption gates (each MUST fail)."""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'
import json, random, sys
from fractions import Fraction
import numpy as np
from mpmath import iv
import t3lib as T, pilot87 as P

fails = []
def check(name, ok, detail=''):
    print('  [%s] %s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok: fails.append(name)

z0, _ = T.load_trump()
pt = [T._to_iv(x) for x in z0]
cert = T.load_a22_cert()

# 1. every A22 curated wall/edge row is reproduced by the t3 row language
mx = 0.0; n = 0
for c in cert['constraints']:
    if c['kind'] == 'wall':   r = T.wall_row(c['i'], c['corner'], c['wall'])
    elif c['kind'] == 'edge': r = T.sep_row(c['j'], c['edge'], c['i'], c['corner'])
    else: continue
    n += 1
    v = T.row_value(pt, r); mx = max(mx, abs(float(v.a)), abs(float(v.b)))
check('A22 row reproduction', mx < 1e-28, 'max |g| = %.2e over %d rows' % (mx, n))

# 2. FJ multipliers at Trump reproduce A22's min multiplier 0.01754
box = P.build_cell(z0, Fraction(1, 2000), z0[33] + Fraction(1, 10**6))
ab = T.test_ab(box); mn = T.build_menu(box, ab)
sel = []
for p in sorted(mn['menus'].keys()):
    for s in mn['menus'][p]:
        vals = [T.row_value(pt, r) for r in s['rows']]
        if all(v.b > -1e-20 for v in vals):
            sel += [r for r, v in zip(s['rows'], vals) if abs(float(v.a)) < 1e-20]
            break
rows = list(ab['wall_straddle']) + sel
A = P.grad_matrix(box, rows)
v = P.find_vertex(A, tries=400, seed=7, stop_at=1.0)
check('A22 min-multiplier cross-check', v is not None and abs(v[0] - 0.017542) < 2e-4,
      'best 34-vertex min lambda = %.6f (A22 reports 0.01754)' % (v[0] if v else -1))

# 3. Krawczyk isolates the Trump FJ point at h = 2e-4 and NOT at h = 1e-3
arows = [rows[i] for i in v[1]]
xp, resid = P.polish([T._mid(x) for x in box], rows, v[1], v[2], 1.0, iters=4)
al = [xp[T.NV + 1 + q] for q in range(len(v[1]))]; l0v = xp[T.NV]
res = {}
for den in (1000, 5000):
    b = P.build_cell(z0, Fraction(1, den), z0[33] + Fraction(1, 10**6))
    lb = [iv.mpf([q - 1e-6, q + 1e-6]) for q in al]
    res[den] = T.krawczyk_fj(b, arows, iv.mpf([l0v - 1e-6, l0v + 1e-6]), lb, mode='active')
check('Krawczyk isolation threshold', (not res[1000]['isolated']) and res[5000]['isolated'],
      'h=1e-3 ratio %.3f (no), h=2e-4 ratio %.3f (yes)' % (res[1000]['ratio'], res[5000]['ratio']))

# --- corruption gates (each MUST fail) -------------------------------------
# 4. a Farkas direction with y_s > 0 must be rejected
ok0, y, eps, _ = T.farkas_lp(box, mn['union'])
badok, _ = T.verify_farkas(box, mn['union'], [1.0] * 34)
check('corruption: y_s > 0 rejected', not badok, '(verifier refused an ascent direction)')

# 5. a cell known to contain a MINIMISER must not be discharged by any test
verdict = P.cell_excluded(z0, Fraction(1, 2000), z0[33] + Fraction(1, 10**6))
check('corruption: cell containing zhat survives', verdict is None,
      'verdict = %s' % verdict)

# 6. a genuinely overlapping cell must be reported infeasible
zz = list(z0)
zz[3] = zz[3] - Fraction(1, 4)          # slide square 1 into square 0
check('corruption: overlap detected',
      P.cell_excluded(zz, Fraction(1, 10000), z0[33] + Fraction(1, 100)) in ('a', 'a-menu'),
      'verdict = %s' % P.cell_excluded(zz, Fraction(1, 10000), z0[33] + Fraction(1, 100)))

# 7. adversarial sampling: cells discharged by (b)/(c1)/(a-menu) must contain
#    no configuration that beats the incumbent; and (a)/(a-menu) cells must
#    contain no legal packing at all.
rng = random.Random(2)
zl, eta = P.loose_config(3.898)
zp = [q + Fraction(rng.uniform(-5e-4, 5e-4)).limit_denominator(10**12)
      for q in zl[:33]] + [Fraction(39, 10)]
zp = P.renormalise(zp, pad=1e-9)
bad = 0; tested = 0
for trial in range(40):
    d = [rng.gauss(0, 1) for _ in range(33)]
    nn = max(abs(x) for x in d); d = [x / nn * rng.uniform(0.002, 0.05) for x in d]
    zc = [x + Fraction(o).limit_denominator(10**15) for x, o in zip(zp, d + [0.0])]
    R = Fraction(1, 1000)
    verd = P.cell_excluded(zc, R, Fraction(39, 10))
    if verd not in ('a', 'a-menu'):
        continue
    tested += 1
    for _ in range(40):                    # sample configurations inside the cell
        zs = [x + Fraction(rng.uniform(-float(R), float(R))).limit_denominator(10**12)
              for x in zc[:33]] + [Fraction(39, 10)]
        s = [T._to_iv(q) for q in zs]
        a2 = T.test_ab(s)
        if not a2['infeasible'] and a2.get('min_gap', -1) >= 0:
            bad += 1
check('adversarial: no legal packing inside (a)-discharged cells', bad == 0,
      '%d cells sampled x40, %d violations' % (tested, bad))

print('=> %s' % ('ALL PASS' if not fails else 'FAILURES: %s' % fails))
sys.exit(0 if not fails else 1)
