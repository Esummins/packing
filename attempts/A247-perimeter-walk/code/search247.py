"""A247: the WITNESS SEARCH -- random sampling of the initial box through the vectorised
enclosures (degenerate boxes), then L-BFGS-B / Powell polish of the best points on the scalar
penalty; a float witness passing the strict test (margin 1e-7) is handed back to bb247, which
verifies it in exact rational arithmetic (verify247).  Only FEASIBLE verdicts come from here;
infeasibility is the branch-and-bound's alone.
"""
import numpy as np

import geo247 as G
import verify247 as V


def poses_of(box, k):
    s = (box[:, 0, 0], box[:, 1, 0])
    return s, [G.IV.pose_of(box, 1 + 3 * i) for i in range(k)]


def penalty(x, problem, margin):
    """sum of squared constraint violations (with margin) at the float vector x = (s, poses)."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
    eta_a = problem.get('eta_avoid', eta)
    s = float(x[0])
    ps = [(float(x[1 + 3 * i]), float(x[2 + 3 * i]), float(x[3 + 3 * i])) for i in range(k)]
    pen = 0.0
    for i, sq in enumerate(problem['squares']):
        q = G.C.square_corners(*ps[i])
        pen += max(0.0, margin - q.min()) ** 2 + max(0.0, q.max() - s + margin) ** 2
        for name in sq['req']:
            pen += max(0.0, eta + margin - G.depth_cell_pt(ps[i], name, s)) ** 2
        for name in sq.get('avoid', ()):
            pen += max(0.0, G.depth_cell_pt(ps[i], name, s) - eta_a + margin) ** 2
    for i in range(k):
        for j in range(i + 1, k):
            pen += max(0.0, G.depth_pair_pt(ps[i], ps[j]) + margin) ** 2
    return pen


def penalty_vec(X, problem, margin):
    """vectorised penalty at the rows of X (m, d): squared violations through the enclosures on
    degenerate boxes."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
    eta_a = problem.get('eta_avoid', eta)
    pb = np.stack([X, X], axis=1)
    s, ps = poses_of(pb, k)
    pen = np.zeros(len(X))
    for i, sq in enumerate(problem['squares']):
        (xlo, xhi), (ylo, yhi) = G.extent(ps[i])
        for v in (xlo[0], ylo[0]):
            pen += np.maximum(0.0, margin - v) ** 2
        for v in (xhi[1], yhi[1]):
            pen += np.maximum(0.0, v - s[0] + margin) ** 2
        for name in sq['req']:
            pen += np.maximum(0.0, eta + margin - G.depth_cell(ps[i], G.rect_i(name, s))[0]) ** 2
        for name in sq.get('avoid', ()):
            pen += np.maximum(0.0, G.depth_cell(ps[i], G.rect_i(name, s))[1] - eta_a + margin) ** 2
    for i in range(k):
        for j in range(i + 1, k):
            pen += np.maximum(0.0, G.depth_pair(ps[i], ps[j])[1] + margin) ** 2
    return pen


def search_witness(problem, init, rounds=2, samples=12000, polish=4, margin=2e-6, seed=247):
    """random sampling (vectorised) of the initial box, then L-BFGS-B polish of the best points;
    returns a float witness passing the strict test (margin 1e-7), or None."""
    from scipy.optimize import minimize
    k = len(problem['squares'])
    rng = np.random.default_rng(seed)
    lo, hi = init[0], init[1]
    cand = []
    for _ in range(rounds):
        X = lo + rng.random((samples, len(lo))) * (hi - lo)
        pen = penalty_vec(X, problem, margin)
        idx = np.argsort(pen)[:polish]
        cand += [X[i] for i in idx]
        if pen[idx[0]] == 0.0:
            break
    cand.sort(key=lambda x: penalty(x, problem, margin))
    for x0 in cand[:2 * polish]:
        for method in ('L-BFGS-B', 'Powell'):
            r = minimize(penalty, x0, args=(problem, margin), method=method, bounds=list(zip(lo, hi)),
                         options={'maxiter': 400} if method == 'Powell' else {})
            x = np.clip(r.x, lo, hi)
            s = float(x[0])
            ps = [(float(x[1 + 3 * i]), float(x[2 + 3 * i]), float(x[3 + 3 * i])) for i in range(k)]
            if V.check_float(s, ps, problem, 1e-7, eta=problem.get('eta', 0.0)):
                return s, ps
            if r.fun > 1e-3:
                break
    return None


