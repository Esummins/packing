"""Search the drop-set D (4 rows) so that the unique multiplier on S = rest
is nonnegative / strictly positive; also global LP feasibility on all 38."""
import sys, os, itertools, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from mpmath import mp
import numpy as np
from scipy.optimize import linprog

mp.dps = 60
z0, ex = load_z0()
cons = curated_constraints(ex)
zm = z_point(mp, z0)
G = [grad_g(mp, zm, c) for c in cons]
Jf = np.zeros((len(cons), NV))
for r, g in enumerate(G):
    for k, v in g.items():
        Jf[r, k] = float(v)
es = np.zeros(NV); es[33] = 1.0

# global LP: max t st J^T y = e_s, y >= t
# vars: y (38), t
n = len(cons)
A_eq = np.hstack([Jf.T, np.zeros((NV, 1))])
c_obj = np.zeros(n + 1); c_obj[-1] = -1.0
A_ub = np.hstack([-np.eye(n), np.ones((n, 1))])   # t - y_k <= 0
b_ub = np.zeros(n)
bounds = [(None, None)] * n + [(None, None)]
r = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=es, bounds=bounds, method='highs')
print('global max-min LP status:', r.status, 'max min-multiplier t* =', -r.fun if r.success else None)
if r.success:
    y = r.x[:n]
    print('min y:', y.min(), 'argmin:', con_name(cons[int(y.argmin())]))

# blocks for drop candidates
sq0w = [i for i, c in enumerate(cons) if c['kind'] == 'wall' and c['i'] == 0]
sq2w = [i for i, c in enumerate(cons) if c['kind'] == 'wall' and c['i'] == 2]
sq5w = [i for i, c in enumerate(cons) if c['kind'] == 'wall' and c['i'] == 5]
pin = [i for i, c in enumerate(cons) if c['kind'] == 'edge' and c['i'] >= 7 and c['j'] >= 7]
print('pinwheel rows:', [con_name(cons[i]) for i in pin])

best = None
results = []
for D in itertools.product(sq0w, sq2w, sq5w, pin):
    keep = [i for i in range(n) if i not in D]
    JS = Jf[keep]
    if np.linalg.matrix_rank(JS, tol=1e-9) < NV:
        continue
    lam = np.linalg.solve(JS.T @ JS.T.T if False else JS.T, es) if False else None
    try:
        lam = np.linalg.solve(JS.T, es)
    except np.linalg.LinAlgError:
        continue
    mn = lam.min()
    results.append((mn, D))
    if best is None or mn > best[0]:
        best = (mn, D, lam, keep)
results.sort(reverse=True, key=lambda x: x[0])
print('\ntop 8 drop sets by min-lambda:')
for mn, D in results[:8]:
    print('  min lam %.6f  drop %s' % (mn, [con_name(cons[d]) for d in D]))
print('\nworst:', results[-1][0])
if best and best[0] > 0:
    mn, D, lam, keep = best
    print('\nBEST drop set:', [con_name(cons[d]) for d in D], 'min lambda:', mn)
    json.dump({'dropped': sorted(D)}, open(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'results', 'best_drop.json'), 'w'))
