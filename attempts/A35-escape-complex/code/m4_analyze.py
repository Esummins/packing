"""m4_analyze.py -- A35 / M4 post-processing: re-jam classification + summary.

For every re-jam found by the cascade, rebuild the FULL active set at the point
(all corner-wall clearances = 0, all pair SAT gaps = 0) and test whether
e_s lies in the cone of the active gradients (LP).  A YES means the point is a
candidate LOCAL MINIMUM of sigma on its stratum (a genuine new jam); a NO means
it is a rank-34 point that is not a minimiser.  [NUM] throughout.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m4_geom as G          # noqa: E402
import m4_cascade as M       # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
ACT = 1e-7


def active_rows(z):
    """Every geometrically active constraint at z (independent of the 38 rows)."""
    rows = []
    Q = G.corners(z)
    s = z[G.S_IDX]
    for i in range(11):
        for k in range(4):
            for w, val in (('x=0', Q[i, k, 0]), ('y=0', Q[i, k, 1]),
                           ('x=s', s - Q[i, k, 0]), ('y=s', s - Q[i, k, 1])):
                if abs(float(val)) < ACT:
                    rows.append({'kind': 'wall', 'i': i, 'corner': k,
                                 'wall': w, 'name': 'W%dc%d[%s]' % (i, k, w)})
    gap, wit = G.sat_all(z)
    pairs = []
    for (i, j) in G.ALL_PAIRS:
        if abs(float(gap[i, j])) < ACT:
            pairs.append((i, j))
            # MENU COMPLETENESS (theory.md G5): at a flush / tie contact the
            # normal cone is spanned by EVERY (owner, edge, corner) row that
            # realises the gap, not just one witness.  Include them all.
            for (o, p_) in ((i, j), (j, i)):
                for e in range(4):
                    for k in range(4):
                        rr = {'kind': 'edge', 'i': p_, 'j': o,
                              'corner': k, 'edge': e,
                              'name': 'P%d-%d(%d,%d,%d)' % (i, j, o, e, k)}
                        if abs(float(G.row_val(z, rr))) < ACT:
                            rows.append(rr)
    return rows, pairs


def cone_test(z, rows):
    A = G.rows_jac(z, rows)
    es = np.zeros(G.NV); es[G.S_IDX] = 1.0
    n = A.shape[0]
    lp = linprog(np.zeros(n), A_eq=A.T, b_eq=es,
                 bounds=[(0, None)] * n, method='highs')
    if not lp.success:
        return False, None
    c = np.zeros(n + 1); c[-1] = -1.0
    r2 = linprog(c, A_ub=np.hstack([-np.eye(n), np.ones((n, 1))]),
                 b_ub=np.zeros(n),
                 A_eq=np.hstack([A.T, np.zeros((G.NV, 1))]), b_eq=es,
                 bounds=[(0, None)] * n + [(None, 10)], method='highs')
    return True, (float(r2.x[-1]) if r2.success else None)


def full_rows(z, B, gained):
    """Maintained A22 rows + gained rows + any OTHER geometrically active
    constraint not already represented (e.g. the (1,3) corner touch)."""
    rows = [M.CONS[k] for k in range(M.NGEO) if k not in set(B)]
    for g in gained:
        rows.append({'kind': 'edge', 'i': g[0], 'j': g[1], 'corner': g[2],
                     'edge': g[3], 'name': 'GAINED'})
    have_pairs = set()
    for c in rows:
        if c['kind'] in ('edge', 'dist', 'sat'):
            have_pairs.add(tuple(sorted((c['i'], c['j']))))
    have_wall = set((c['i'], c['corner'], c['wall'])
                    for c in rows if c['kind'] == 'wall')
    extra, _ = active_rows(z)
    for c in extra:
        if c['kind'] == 'wall':
            if (c['i'], c['corner'], c['wall']) not in have_wall:
                rows.append(c)
        else:
            if tuple(sorted((c['i'], c['j']))) not in have_pairs:
                rows.append(c)
    return rows


def main():
    fam = json.load(open(os.path.join(
        HERE, '..', '..', 'A04-upper-search',
        'families_catalogue.json')))['families']
    out = []
    seen = {}
    for f in ('m4_cascade_eventsurvey.json',
              'm4_cascade_repaired_eventsurvey.json'):
        d = json.load(open(os.path.join(RES, f)))
        for r in d['rejams']:
            z = np.array(r['z'])
            _, pairs = active_rows(z)
            rows = full_rows(z, r['B'], r['gained'])
            ok, floor = cone_test(z, rows)
            rank = int((np.linalg.svd(G.rows_jac(z, rows),
                                      compute_uv=False) > 1e-8).sum())
            near = min(fam, key=lambda q: abs(q['s_min'] - r['sigma']))
            key = round(r['sigma'], 8)
            rec = {'basis': 'repaired' if 'repaired' in f else 'a22',
                   'sigma': r['sigma'],
                   'sigma_minus_shat': r['sigma'] - M.S_HAT,
                   'travel_inf': r['travel'],
                   'broken_rows': r['B'], 'gained': r['gained'],
                   'n_active_rows': len(rows), 'n_active_pairs': len(pairs),
                   'active_pairs': [list(p) for p in pairs],
                   'rank_active': rank,
                   'es_in_active_cone': ok, 'lambda_floor': floor,
                   'nearest_A04_family_s_min': near['s_min'],
                   'A04_delta': abs(near['s_min'] - r['sigma']),
                   'A04_match': bool(abs(near['s_min'] - r['sigma']) < 1e-7),
                   'A04_structure': {'n_upright': near['n_upright'],
                                     'n_pair_contacts': near['n_pair_contacts'],
                                     'n_wall_contacts': near['n_wall_contacts']},
                   'z': r['z']}
            if key not in seen:
                seen[key] = rec
                out.append(rec)
    out.sort(key=lambda r: r['sigma'])
    with open(os.path.join(RES, 'm4_rejams.json'), 'w') as f:
        json.dump({'s_hat': M.S_HAT, 'n_distinct': len(out),
                   'note': '[NUM]; active set rebuilt geometrically at ACT=1e-7',
                   'rejams': out}, f, indent=1)
    for r in out:
        print('sigma %.9f (+%.6f) travel %.4f  active rows %d pairs %d rank %d '
              'es_in_cone %s  A04 %s (d=%.2e)'
              % (r['sigma'], r['sigma_minus_shat'], r['travel_inf'],
                 r['n_active_rows'], r['n_active_pairs'], r['rank_active'],
                 r['es_in_active_cone'], r['A04_match'], r['A04_delta']))


if __name__ == '__main__':
    main()
