"""A244 Fritz-John reading of a candidate, on A217's machinery.

A 12-stuck packing produced by the crowd search is held there by the CROWD rows, which are
artificial: they are not contacts.  The question the brief asks is whether any candidate is
LOCKED -- whether the FREE FJ system (walls + contacts only, no crowd rows) already certifies
the side as a local minimum, and whether every meeter of the twelve cells carries load.

    fj_free_res   0 (to 1e-8) iff the free active-row system A^T lam = e_s, lam >= 0 is solvable
    loaded        the squares carrying positive multipliers in the NNLS solution
    meeters_loadable  per meeter, the LP maximum of its total multiplier over the whole
                  multiplier polytope (0 means: unloaded in EVERY FJ certificate)
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code')))
sys.path.insert(0, HERE)

import opt217 as O            # noqa: E402
import stress217 as T         # noqa: E402
import cells244 as C          # noqa: E402


def analyse(z, tol=1e-7, lp=True):
    z = np.asarray(z, float)[:34]
    res, lam, rows = O.fj_residual(z, tol=tol)
    loaded = set()
    for r, l in zip(rows, lam):
        if l > 1e-9:
            loaded.add(int(r['i']))
            if 'j' in r:
                loaded.add(int(r['j']))
    ms = C.meeter_sets(z)
    meeters = sorted({i for v in ms.values() for i in v})
    out = {'fj_free_res': float(res), 'fj_free_rows': len(rows),
           'fj_wall_rows': sum(r['kind'] == 'wall' for r in rows),
           'fj_edge_rows': sum(r['kind'] == 'edge' for r in rows),
           'fj_loaded': sorted(loaded), 'n_meeters': len(meeters),
           'meeters_all_loaded': bool(set(meeters) <= loaded),
           'locked': bool(res < 1e-8 and set(meeters) <= loaded)}
    if lp and res < 1e-8 and rows:
        A = np.array([_row_jac(z, r) for r in rows])
        cap = {}
        for i in meeters:
            w = np.array([1.0 if (r['i'] == i or r.get('j') == i) else 0.0 for r in rows])
            try:
                cap[i] = round(T.lp_range(A, w)[1], 6)
            except Exception:                                     # noqa
                cap[i] = None
        out['meeter_lp_max_load'] = cap
        out['unloadable_meeters'] = sorted(i for i, v in cap.items()
                                           if v is not None and v <= 1e-9)
    return out


def _row_jac(z, r):
    """the gradient row of an active row, as opt217.active_rows built it."""
    import geom217 as G
    if r['kind'] == 'wall':
        gw, Jw = G.wall_rows(z)
        Jw = Jw.reshape(G.N, 4, 4, G.NV)
        return Jw[r['i'], r['corner'], G.WALLS.index(r['wall'])]
    gp, Jp = O._pair_rows_one(z, r['j'], r['edge'], r['i'])
    return Jp[r['corner']]
