"""A247: certified interval branch-and-bound for k unit squares (k <= 3) with designated cells.

A PROBLEM is: the side s in [s_lo, s_hi]; squares i = 0..k-1, each with REQUIRED cells (SAT
depth >= eta; eta = 0 is the closed form "meets or touches") and AVOIDED cells (depth <= 0);
every square inside [0, s]^2; every pair interior-disjoint (pair depth <= 0).  Verdicts:
  INFEASIBLE  every box of the search tree was discarded by an interval enclosure showing that
              EVERY pose in it violates a constraint (guard GUARD = 1e-9 on each test);
  FEASIBLE    a witness pose was found (a box midpoint) and verified in EXACT rational arithmetic
              (verify247: rationalised tilt on the unit circle, all depths as Fractions);
  UNDECIDED   boxes below the relative width floor hmin survived (listed), or the budget ran out.
The queue is processed depth-first in batches (numpy-vectorised), checkpointed to a .npz for
resume, and stops on logs/STOP.
"""
import json
import os
import time

import numpy as np

import geo247 as G
import verify247 as V

IV = G.IV
GUARD = G.GUARD
HALF_PI = np.pi / 2
HW = 0.70711                                     # half of sqrt2, the largest half-extent


def initial_box(problem):
    """(2, d) lo/hi rows: s, then (cx, cy, th) per square, centres narrowed by the required cells."""
    s_lo, s_hi = problem['s']
    rows = [(s_lo, s_hi)]
    for sq in problem['squares']:
        xs0, xs1, ys0, ys1 = [], [], [], []
        for name in sq['req']:
            r0, r1 = G.rect_at(name, s_lo), G.rect_at(name, s_hi)
            xs0.append(min(r0[0], r1[0]))
            xs1.append(max(r0[1], r1[1]))
            ys0.append(min(r0[2], r1[2]))
            ys1.append(max(r0[3], r1[3]))
        cx = (max(0.5, max(xs0) - HW) if xs0 else 0.5, min(s_hi - 0.5, min(xs1) + HW) if xs1 else s_hi - 0.5)
        cy = (max(0.5, max(ys0) - HW) if ys0 else 0.5, min(s_hi - 0.5, min(ys1) + HW) if ys1 else s_hi - 0.5)
        rows += [cx, cy, tuple(sq.get('theta', (0.0, HALF_PI)))]
    return np.array(rows, float).T.copy()          # (2, d)


def poses_of(box, k):
    s = (box[:, 0, 0], box[:, 1, 0])
    ps = [IV.pose_of(box, 1 + 3 * i) for i in range(k)]
    return s, ps


def alive(box, problem):
    """boolean mask: False where an enclosure proves EVERY pose of the box infeasible."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
    eta_a = problem.get('eta_avoid', eta)
    s, ps = poses_of(box, k)
    ok = np.ones(len(box), bool)
    for i, sq in enumerate(problem['squares']):
        (xlo, xhi), (ylo, yhi) = G.extent(ps[i])
        ok &= (xlo[1] >= -GUARD) & (ylo[1] >= -GUARD)
        ok &= (xhi[0] <= s[1] + GUARD) & (yhi[0] <= s[1] + GUARD)
        for name in sq['req']:
            d = G.depth_cell(ps[i], G.rect_i(name, s))
            ok &= d[1] >= eta - GUARD
        for name in sq.get('avoid', ()):
            d = G.depth_cell(ps[i], G.rect_i(name, s))
            ok &= d[0] <= eta_a + GUARD
    for i in range(k):
        for j in range(i + 1, k):
            dp = G.depth_pair(ps[i], ps[j])
            ok &= dp[0] <= GUARD
    for i, j in problem.get('order', ()):        # symmetry breaking cx_i <= cx_j (identical squares)
        ok &= ps[i][0][0] <= ps[j][0][1] + GUARD
    return ok


def contract(box, problem):
    """hull consistency on the centres from the required cells' e_x / e_y overlaps and from
    containment (every bound is implied by the constraints, so no pose is lost)."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
    s, ps = poses_of(box, k)
    out = box.copy()
    for i, sq in enumerate(problem['squares']):
        th = ps[i][2]
        w = G.E.w_range(th[0], th[1])
        hwl, hwh = 0.5 * w[0], 0.5 * w[1]
        lo_x, hi_x = hwl + np.zeros(len(box)), s[1] - hwl
        lo_y, hi_y = lo_x.copy(), hi_x.copy()
        for name in sq['req']:
            x0, x1, y0, y1 = G.rect_i(name, s)
            lo_x = np.maximum(lo_x, x0[0] + eta - hwh)
            hi_x = np.minimum(hi_x, x1[1] - eta + hwh)
            lo_y = np.maximum(lo_y, y0[0] + eta - hwh)
            hi_y = np.minimum(hi_y, y1[1] - eta + hwh)
        o = 1 + 3 * i
        out[:, 0, o] = np.maximum(out[:, 0, o], lo_x)
        out[:, 1, o] = np.minimum(out[:, 1, o], hi_x)
        out[:, 0, o + 1] = np.maximum(out[:, 0, o + 1], lo_y)
        out[:, 1, o + 1] = np.minimum(out[:, 1, o + 1], hi_y)
    ok = np.all(out[:, 1, :] >= out[:, 0, :] - GUARD, axis=1)
    out[:, 1, :] = np.maximum(out[:, 1, :], out[:, 0, :])
    return out, ok


def point_feasible(box, problem, margin=1e-7):
    """vectorised strict test of the box MIDPOINTS (degenerate boxes through the same enclosures):
    True where the midpoint satisfies every constraint with the margin."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
    eta_a = problem.get('eta_avoid', eta)
    mid = 0.5 * (box[:, 0, :] + box[:, 1, :])
    pb = np.stack([mid, mid], axis=1)
    s, ps = poses_of(pb, k)
    ok = np.ones(len(pb), bool)
    for i, sq in enumerate(problem['squares']):
        (xlo, xhi), (ylo, yhi) = G.extent(ps[i])
        ok &= (xlo[0] >= margin) & (ylo[0] >= margin) & (xhi[1] <= s[0] - margin) & (yhi[1] <= s[0] - margin)
        for name in sq['req']:
            ok &= G.depth_cell(ps[i], G.rect_i(name, s))[0] >= eta + margin
        for name in sq.get('avoid', ()):
            ok &= G.depth_cell(ps[i], G.rect_i(name, s))[1] <= eta_a - margin
    for i in range(k):
        for j in range(i + 1, k):
            ok &= G.depth_pair(ps[i], ps[j])[1] <= -margin
    return ok, mid


def midpoint_witness(box, problem, margin=1e-7):
    """the first box whose midpoint passes the strict float test; None if none."""
    ok, mid = point_feasible(box, problem, margin)
    idx = np.flatnonzero(ok)
    if not len(idx):
        return None
    m = mid[idx[0]]
    k = len(problem['squares'])
    return float(m[0]), [(float(m[1 + 3 * i]), float(m[2 + 3 * i]), float(m[3 + 3 * i])) for i in range(k)]


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


def widest(box, init):
    wd = (box[:, 1, :] - box[:, 0, :]) / np.maximum(init[1] - init[0], 1e-12)
    wd[:, 0] *= 0.25                              # the side is narrow and cheap: split it late
    return np.argmax(wd, axis=1), wd.max(axis=1)


def solve(problem, hmin=1e-5, budget_boxes=3_000_000, budget_s=None, batch=20000, ck=None, stop=None,
          log=None, want_witness=True):
    """run the branch-and-bound; returns the verdict dict (status, counts, witness / undecided boxes)."""
    init = initial_box(problem)
    k = len(problem['squares'])
    stats = {'processed': 0, 'discarded': 0, 'undecided': 0, 'seconds': 0.0, 'witness': None,
             'undecided_boxes': [], 'min_pair_depth_lo': None}
    if want_witness and not (ck and os.path.exists(ck)):
        t0 = time.time()
        w = search_witness(problem, init)
        if w is not None:
            ex = V.check_exact(w[0], w[1], problem)
            if ex['ok']:
                stats.update(witness={'s': w[0], 'poses': w[1], 'exact': ex, 'how': 'search'},
                             status='FEASIBLE', queue_left=0, hmin=hmin, guard=GUARD,
                             eta=problem.get('eta', 0.0), s=list(problem['s']), seconds=time.time() - t0)
                return stats
    if ck and os.path.exists(ck):
        d = np.load(ck)
        queue, stats = d['queue'], json.loads(str(d['stats']))
    else:
        queue = init[None, :, :].copy()
    t0 = time.time()
    last = t0
    status = 'RUNNING'
    while len(queue):
        if stop and os.path.exists(stop):
            status = 'STOPPED'
            break
        if stats['processed'] > budget_boxes or (budget_s and time.time() - t0 + stats['seconds'] > budget_s):
            status = 'BUDGET'
            break
        cur, queue = queue[-batch:], queue[:-batch]
        cur, okc = contract(cur, problem)
        cur = cur[okc]
        ok = alive(cur, problem) if len(cur) else np.zeros(0, bool)
        stats['processed'] += len(okc)
        stats['discarded'] += int((~okc).sum()) + int((~ok).sum())
        cur = cur[ok]
        if not len(cur):
            continue
        if want_witness:
            w = midpoint_witness(cur, problem)
            if w is not None:
                ex = V.check_exact(w[0], w[1], problem)
                if ex['ok']:
                    stats['witness'] = {'s': w[0], 'poses': w[1], 'exact': ex}
                    status = 'FEASIBLE'
                    break
        kd, wd = widest(cur, init)
        small = wd < hmin
        if small.any():
            stats['undecided'] += int(small.sum())
            for b in cur[small][:10]:
                if len(stats['undecided_boxes']) < 50:
                    stats['undecided_boxes'].append(b.tolist())
        big = cur[~small]
        if len(big):
            parts = [IV.box_split(big[kd[~small] == d], int(d)) for d in np.unique(kd[~small])]
            queue = np.concatenate([queue] + parts) if len(queue) else np.concatenate(parts)
        if ck and time.time() - last > 120:
            stats['seconds'] += time.time() - t0
            t0 = time.time()
            np.savez(ck, queue=queue, stats=json.dumps(stats))
            last = time.time()
            if log:
                log('  processed %d queue %d undecided %d' % (stats['processed'], len(queue), stats['undecided']))
    stats['seconds'] += time.time() - t0
    if status == 'RUNNING':
        status = 'INFEASIBLE' if stats['undecided'] == 0 else 'UNDECIDED'
        if ck and os.path.exists(ck):
            os.remove(ck)
    elif status != 'FEASIBLE' and ck:
        np.savez(ck, queue=queue, stats=json.dumps(stats))
    stats.update(status=status, queue_left=int(len(queue)), hmin=hmin, guard=GUARD,
                 eta=problem.get('eta', 0.0), eta_avoid=problem.get('eta_avoid'), s=list(problem['s']))
    return stats


def problem_of(specs, s_range, eta=0.0, exact=False, eta_avoid=None):
    """specs: list of ('M', corner, cells) / ('F', cells) / ('P', cells).  Monotone (exact=False):
    a meeter requires its cells (c00 among them), a free square requires its cells and avoids
    the four boxes (depth <= eta), a plain square requires its cells.  EXACT: every square
    requires exactly its cells and avoids (depth <= eta) every other cell of the neighbourhoods
    N_c that contain its set (a free square avoids the boxes too)."""
    sq = []
    for sp in specs:
        cells = list(sp[2] if sp[0] == 'M' else sp[1])
        if exact:
            reach = set()
            for c in G.CORNERS:
                if set(cells) <= set(G.NBR[c]):
                    reach |= set(G.NBR[c])
            avoid = set(reach) - set(cells)
            if sp[0] == 'F':
                avoid |= set(G.BOXES)
            sq.append({'kind': sp[0], 'corner': sp[1] if sp[0] == 'M' else None, 'req': cells,
                       'avoid': sorted(avoid, key=G.RING.index)})
        elif sp[0] == 'M':
            sq.append({'kind': 'M', 'corner': sp[1], 'req': cells, 'avoid': []})
        elif sp[0] == 'P':
            sq.append({'kind': 'P', 'req': cells, 'avoid': []})
        else:
            sq.append({'kind': 'F', 'req': cells, 'avoid': list(G.BOXES)})
    order = []
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if sq[i]['req'] == sq[j]['req'] and sq[i]['avoid'] == sq[j]['avoid']:
                order.append((i, j))
    return {'squares': sq, 's': tuple(s_range), 'eta': eta, 'eta_avoid': eta if eta_avoid is None else eta_avoid,
            'order': order, 'specs': specs, 'exact': exact}
