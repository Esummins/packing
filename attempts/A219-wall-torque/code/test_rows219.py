"""self-test: gradients vs opt217's jacobians, Hessians vs central differences, stress reproduced."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rows219 as R
import opt217 as O
W = [json.loads(l) for l in open(os.path.join(R.HERE, '..', '..', 'A217-torque-probe/results/witnesses217.jsonl'))]
t0 = time.time()
for wid in ('w364_held', None):
    w = next(x for x in W if (x['wid'] == wid if wid else x['cls'] == 'CROWD' and x['n2'] == 4))
    rows, z = R.witness_rows(w)
    vals, A, Hs = R.system(z, rows)
    rows0, A0 = O.active_rows(z, 1e-7)
    assert np.abs(A[:len(rows0)] - A0).max() < 1e-12, 'gradient mismatch'
    print('  line rows (corner beyond the owner edge segment):', sum(1 for r in rows if r.get('on_segment') is False))
    assert np.abs(vals).max() < 1e-6, ('active rows not at zero', np.abs(vals).max())
    worst = R.check_hessians(z, rows)
    lam, lam0 = R.feasible(A)
    res = np.abs(A.T @ lam - O.E_S).max() if lam is not None else None
    print(w['wid'], w['cls'], 'rows', len(rows), {k: sum(r['kind'] == k for r in rows) for k in ('wall', 'edge', 'tiltbound', 'crowd')},
          'hess err %.1e' % worst, 'lam0', lam0, 'res', res)
    assert worst < 1e-6 and lam is not None
print('ok %.1f s' % (time.time() - t0))
