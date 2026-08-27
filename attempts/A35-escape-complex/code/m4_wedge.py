"""m4_wedge.py -- A35 / M4: quantitative WEDGE certificate data for M1's 81.

For each surviving break set B, the escape cone is
    C(B) = { v in ker A_M : A_B v >= 0 }.
M4 measures the WEDGE STRENGTH

    w(B) = min over unit v in ker A_M of  max_{b in B} ( -grad g_b . v ),

i.e. every unit motion along the stratum closes SOME broken gap at rate at
least w(B).  w(B) > 0  <=>  C(B) = {0}  <=>  Sbar(B) meets a neighbourhood of
z-hat in {z-hat} only (first order).  w(B) is exactly the constant M2 needs to
turn the wedge into a rigorous certificate: for a curve z(t) on the stratum,
g_b(z(t)) <= -w(B) t + (curvature) t^2 / 2 < 0 for t < 2 w(B) / Hbar.

dof 1: exact (two unit vectors).  dof 2: fine sweep of the unit circle in the
kernel plane (N_SWEEP samples) plus local refinement.  [NUM].
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m4_geom as G          # noqa: E402
import m4_cascade as M       # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
N_SWEEP = 20000


def wedge_strength(B):
    Mrows = M.build_M(set(B), [])
    K, d, sg = M.kernel(M.ZHAT, Mrows)
    A = G.rows_jac(M.ZHAT, [M.CONS[b] for b in sorted(B)])
    if d == 0:
        return None, 0, sg
    Mk = A @ K.T                        # (|B| x d) rates in kernel coords
    if d == 1:
        vals = [float((-Mk[:, 0]).max()), float((Mk[:, 0]).max())]
        return min(vals), d, sg
    # d >= 2: sweep the unit sphere of R^d (d is 2 here; general: random+sweep)
    if d == 2:
        t = np.linspace(0, 2 * np.pi, N_SWEEP, endpoint=False)
        Cc = np.stack([np.cos(t), np.sin(t)])          # (2, N)
    else:
        rng = np.random.default_rng(11)
        Cc = rng.standard_normal((d, N_SWEEP))
        Cc /= np.linalg.norm(Cc, axis=0)
    R = -(Mk @ Cc)                                     # (|B|, N)
    # kernel coords are orthonormal so |v| = |c|
    return float(R.max(axis=0).min()), d, sg


def main():
    m1 = json.load(open(os.path.join(RES, 'm1_strata.json')))
    sv = m1['synthesis']['global_exhaustive']['survivors']
    out = []
    for B in sv:
        w, d, sg = wedge_strength(B)
        out.append({'B': list(B), 'dof': d, 'wedge_strength': w,
                    'sv_min_kept': sg[0], 'sv_max_dropped': sg[1]})
    ws = [r['wedge_strength'] for r in out]
    res = {'note': '[NUM] wedge strength of M1 s 81 survivors at z-hat; '
                   'w > 0 means the stratum is locally {z-hat} at first order',
           'n': len(out), 'n_wedged': int(sum(1 for w in ws if w > 0)),
           'min_wedge_strength': float(min(ws)),
           'max_wedge_strength': float(max(ws)),
           'median_wedge_strength': float(np.median(ws)),
           'strata': out}
    with open(os.path.join(RES, 'm4_wedge.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print('81 survivors: wedged %d/%d, wedge strength min %.6f median %.6f '
          'max %.6f' % (res['n_wedged'], res['n'], res['min_wedge_strength'],
                        res['median_wedge_strength'],
                        res['max_wedge_strength']))
    from collections import Counter
    print('by dof:', Counter(r['dof'] for r in out))
    print('worst 5:', sorted(out, key=lambda r: r['wedge_strength'])[:5])


if __name__ == '__main__':
    main()
