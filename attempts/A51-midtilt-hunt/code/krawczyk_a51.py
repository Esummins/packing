#!/usr/bin/env python
"""krawczyk_a51.py -- the LAST stage of the A51 candidate pipeline.

`audit_a49.py` decides SURVIVOR / REJECTED in float.  A survivor would then
have to be promoted to an EXACT statement, and that is A37's 3R path: audit
the contact set, Gauss-Newton refine, classify, pick a well-conditioned
34-row pin set, Newton-refine in high precision, build the approximate
inverse Y, and run interval KRAWCZYK -- which, when it contracts, PROVES
existence and uniqueness of a genuine critical point in box(zh, r_N) and
returns a rigorous enclosure of its s value.

This module re-uses `a37_pipeline` verbatim (nothing in A37 is edited); it
only wires its pieces into a single entry point that takes an A51 candidate.

  python krawczyk_a51.py --selftest        # run it on atlas family 0
                                           # (the Trump packing: must
                                           # contract at r = 1/2000)
  python krawczyk_a51.py --cand ID         # run it on one audited candidate
                                           # from results/candidates/<ID>.json
  python krawczyk_a51.py                   # every SURVIVOR in
                                           # results/candidates/summary.json

Output: results/candidates/<ID>.krawczyk.json.
[EXACT] the Krawczyk step itself is interval arithmetic over rationals; the
pin-set choice and the refinement are float/mpmath heuristics, which is sound
because only the interval step is trusted.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import numpy as np
from scipy.linalg import qr

HERE = os.path.dirname(os.path.abspath(__file__))
A51 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A51, '..'))
for p in (os.path.join(ATT, 'A49-flushfree-hunt', 'code'), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import a51_run                              # noqa: E402,F401 (re-aims dirs)
import a49_common as C                      # noqa: E402

P, D = C.P, C.D
NV, S_IDX = P.NV, P.S_IDX
CAND = os.path.join(C.RESULTS, 'candidates')
os.makedirs(CAND, exist_ok=True)

RADII = [Fraction(1, 2000), Fraction(1, 10 ** 4), Fraction(1, 10 ** 5),
         Fraction(1, 10 ** 6)]


def certify_z(z0, tol0=1e-7, tol1=1e-9, label='?'):
    """A37's 3R chain on one point z0 (list of 34 floats/Fractions)."""
    out = {'label': label, 'tol0': tol0, 'tol1': tol1}
    aud0 = P.audit(z0, tol=tol0)
    rows0, _ = P.build_rows(aud0)
    zc, gnres, disp = P.gn_refine(z0, rows0)
    aud = P.audit(zc, tol=tol1)
    rows, meta = P.build_rows(aud)
    safe = [m['safe'] for m in meta]
    cls = P.classify(zc, rows, meta)
    mid, _ = P.jac_at(zc, rows)
    out.update(gn_residual=gnres, displacement=disp, n_rows=len(rows),
               n_safe=int(sum(safe)), struct_class=cls['class'],
               rank=cls['rank'],
               n_pairs=len(aud['pairs']), n_walls=len(aud['walls']),
               flush_free=bool(C.flush_report(
                   D.z_to_a04([float(v) for v in zc]),
                   tol_f=C.TOL_F_DEG)['flush_free']))

    cand = [k for k in range(len(rows)) if safe[k]]
    if len(cand) < NV or np.linalg.matrix_rank(mid[cand], tol=1e-9) < NV:
        cand = list(range(len(rows)))
        out['pin_note'] = ('[V]-safe rows do not span; pin set drawn from ALL '
                           'active rows (branch disjunction load-bearing)')
    if len(cand) < NV or np.linalg.matrix_rank(mid[cand], tol=1e-9) < NV:
        out['verdict'] = 'NO-PIN-BASIS'
        out['rank_available'] = int(np.linalg.matrix_rank(mid[cand], tol=1e-9))
        return out
    piv = qr(mid[cand].T, pivoting=True, mode='economic')[2]
    Pin = sorted(cand[int(q)] for q in piv[:NV])
    ok_rfp, bnd = P.certify_nonsingular(mid[Pin], np.zeros((NV, NV)))
    out['rfp_ok'] = bool(ok_rfp)
    out['rfp_bound'] = float(bnd)

    zh, res = P.newton_refine(zc, rows, Pin)
    out['newton_residual'] = float(res)
    out['newton_displacement'] = max(abs(float(zh[i] - zc[i]))
                                     for i in range(NV))
    midh, _ = P.jac_at(zh, rows)
    Y = P.make_Y(midh, Pin)

    ladder = []
    rN = None
    for r in RADII:
        okk, K, ratio = P.krawczyk(zh, rows, Pin, Y, r)
        ladder.append({'r': P.fs(r), 'contracted': bool(okk),
                       'ratio': float(ratio)})
        if okk and rN is None:
            rN = r
    out['krawczyk_ladder'] = ladder
    out['r_N'] = P.fs(rN) if rN is not None else None
    out['contracted'] = rN is not None
    if rN is not None:
        _, K2, _ = P.krawczyk(zh, rows, Pin, Y, Fraction(1, 10 ** 30))
        v_lo = P.inf(P.cnum(zh[S_IDX]) + K2[S_IDX])
        v_hi = P.sup(P.cnum(zh[S_IDX]) + K2[S_IDX])
        out['s_enclosure'] = [float(v_lo), float(v_hi)]
        out['s_enclosure_width'] = float(v_hi - v_lo)
        out['verdict'] = 'KRAWCZYK-CERTIFIED'
    else:
        out['verdict'] = 'KRAWCZYK-FAILED'
    return out


def selftest():
    """Canary: atlas family 0 (the Trump packing, the sole RIGID critical
    point).  A37 records r_N = 1/2000 at ratio 0.0566 and
    s in [3.8770835900228136, 3.8770835900228144]."""
    z0, fam, ci = P.load_family(0)
    r = certify_z(z0, label='SELFTEST-family-0')
    r['expected'] = {'r_N': '1/2000', 'ratio_approx': 0.0566,
                     's_approx': 3.8770835900228}
    r['selftest_pass'] = bool(r.get('contracted')
                              and r.get('s_enclosure')
                              and abs(r['s_enclosure'][0]
                                      - 3.8770835900228136) < 1e-12)
    with open(os.path.join(CAND, 'selftest_family0.krawczyk.json'), 'w') as f:
        json.dump(r, f, indent=1)
    print(json.dumps({k: v for k, v in r.items()
                      if k not in ('krawczyk_ladder',)}, indent=1))
    print('ladder:', json.dumps(r.get('krawczyk_ladder')))
    print('SELFTEST %s' % ('PASS' if r.get('selftest_pass') else 'FAIL'))
    return 0 if r.get('selftest_pass') else 1


def main():
    argv = sys.argv[1:]
    if '--selftest' in argv:
        return selftest()
    ids = []
    if '--cand' in argv:
        ids = [argv[argv.index('--cand') + 1]]
    else:
        p = os.path.join(CAND, 'summary.json')
        if os.path.exists(p):
            with open(p) as f:
                ids = json.load(f)['survivors']
    if not ids:
        print('no survivors to certify (0 candidates survived the audit); '
              'nothing for the Krawczyk stage to do')
        return 0
    for cid in ids:
        with open(os.path.join(CAND, cid + '.json')) as f:
            rec = json.load(f)
        z = rec.get('z_refined')
        r = certify_z(z, label=cid)
        with open(os.path.join(CAND, cid + '.krawczyk.json'), 'w') as f:
            json.dump(r, f, indent=1)
        print(cid, r['verdict'], r.get('r_N'), r.get('s_enclosure'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
