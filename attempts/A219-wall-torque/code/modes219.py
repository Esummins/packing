"""A219 first-order zero modes with SELECTION: the feasible set near a contact is the union over separating
axes, so a direction y is first-order feasible iff every wall / external row has rate grad g . y >= 0 and
every touching pair has SOME axis whose active corner rows all have rate >= 0.  Modes are completed by an LP
(the unloaded squares move away for free; the loaded rows have rate 0 automatically by stationarity).
"""
import numpy as np
from scipy.optimize import linprog

import rows219 as R

TOL = 1e-9
W_BOX = 10.0          # the second-order correction w is searched in |w|_inf <= W_BOX (the sign of v2 is what matters)
TIGHT = 1e-6          # rows with rate <= TIGHT are treated as tight (conservative for the second-order LP)
LOAD_TOL = 1e-6


def group_rows(rows):
    """walls/ext: list of row indices; pairs: {(i,j): {(owner, edge): [row indices]}}."""
    single, pairs = [], {}
    for k, r in enumerate(rows):
        if r['kind'] == 'edge':
            key = (min(r['i'], r['j']), max(r['i'], r['j']))
            pairs.setdefault(key, {}).setdefault((r['j'], r['edge']), []).append(k)
        else:
            single.append(k)
    return single, pairs


def select(A, groups, y):
    """per pair the axis whose worst active-corner rate under y is largest; returns (selected row
    indices, min rate over the selection)."""
    single, pairs = groups
    rates = A @ y
    sel = list(single)
    worst = float(rates[single].min()) if single else 0.0
    for key, axes in pairs.items():
        best = max(axes.items(), key=lambda kv: rates[kv[1]].min())
        sel += best[1]
        worst = min(worst, float(rates[best[1]].min()))
    return sel, worst


def complete(A, sel, fixed, y0):
    """min sum |y_free|  s.t.  A[sel] y >= 0, y_s = 0, y_k = y0_k for k in fixed.  Returns y or None."""
    n = A.shape[1]
    free = [k for k in range(n) if k not in fixed and k != R.S_IDX]
    if not free:
        return y0 if (A[sel] @ y0).min() >= -TOL else None
    Af = A[np.ix_(sel, free)]
    rhs = -(A[sel] @ y0) + Af @ y0[free]          # A_sel y >= 0 with y = y0 on fixed, y_free = u
    # variables u = up - um >= 0 split; constraint Af (up - um) >= rhs
    m = len(free)
    Aub = np.hstack([-Af, Af])
    r = linprog(np.ones(2 * m), A_ub=Aub, b_ub=-rhs, bounds=(0, R.LP_CAP), method='highs')
    if not r.success:
        return None
    y = y0.copy()
    y[free] = r.x[:m] - r.x[m:]
    y[R.S_IDX] = 0.0
    return y


def make_mode(A, Hs, groups, y0, fixed, rounds=2):
    """From a seed direction y0 (fixed coordinates prescribed): select axes, complete, re-select; then
    the second-order value on the tight selected rows.  Returns dict or None (not a first-order mode)."""
    y = y0.copy()
    y[R.S_IDX] = 0.0
    for _ in range(rounds):
        sel, worst = select(A, groups, y)
        if worst >= -TOL:
            break
        y2 = complete(A, sel, fixed, y)
        if y2 is None:
            return None
        y = y2
    sel, worst = select(A, groups, y)
    if worst < -TOL:
        return None
    nrm = np.linalg.norm(y)
    y = y / nrm
    rates = A[sel] @ y
    E = [sel[a] for a in range(len(sel)) if rates[a] <= TIGHT]
    v2, status, wvec = second_order(A, Hs, E, y)
    return {'y': y, 'w': wvec, 'sel': sel, 'E': E, 'v2': v2, 'status': status,
            'n_open': int((rates > TIGHT).sum()),
            'moving': sorted({int(k // 3) for k in np.nonzero(np.abs(y[:33]) > 1e-9)[0]})}


def second_order(A, Hs, E, y):
    """v2 = min e_s . w  s.t.  grad g_r . w >= - y^T H_r y  (r in E); returns (v2, status, w)."""
    if not E:
        return -float('inf'), 'unbounded', None
    h = np.array([y @ Hs[r] @ y for r in E])
    r = linprog(np.eye(R.NV)[R.S_IDX], A_ub=-A[E], b_ub=h, bounds=(-W_BOX, W_BOX), method='highs')
    if r.status == 3:
        return -float('inf'), 'unbounded', None
    if not r.success:
        return float('nan'), r.message, None
    val = float(r.fun)
    return val, ('bounded' if abs(np.asarray(r.x)).max() < 0.999 * W_BOX else 'at-box'), np.asarray(r.x)


def curve_check(z, rows, y, w, ts=(1e-4, 3e-4, 1e-3)):
    """x(t) = z + t y + t^2 w / 2: the worst violation of the packing rows (walls, every pair's SAT gap, the
    variant's external rows) and the side change, per t.  A verified second-order descent has violations
    O(t^3) and side change ~ v2 t^2 / 2."""
    import geom217 as G
    out = []
    for t in ts:
        x = z + t * y + 0.5 * t * t * w
        gw = G.wall_rows(x)[0].min()
        gp = min(G.pair_gaps(x).values())
        ge = min([R.row_gj(x, r)[0] for r in rows if r['kind'] in ('tiltbound', 'crowd')] + [0.0])
        out.append({'t': t, 'min_wall': float(gw), 'min_pair_gap': float(gp), 'min_ext_row': float(ge),
                    'ds': float(x[R.S_IDX] - z[R.S_IDX])})
    return out


def loaded_squares(rows, lam):
    out = set()
    for k, r in enumerate(rows):
        if lam[k] > LOAD_TOL:
            out.add(r['i'])
            if r['kind'] == 'edge':
                out.add(r['j'])
    return out
