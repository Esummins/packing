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
            ok &= d[0] <= GUARD
    for i in range(k):
        for j in range(i + 1, k):
            dp = G.depth_pair(ps[i], ps[j])
            ok &= dp[0] <= GUARD
    for i, j in problem.get('order', ()):        # symmetry breaking cx_i <= cx_j (identical squares)
        ok &= ps[i][0][0] <= ps[j][0][1] + GUARD
    return ok


def point_feasible(box, problem, margin=1e-7):
    """vectorised strict test of the box MIDPOINTS (degenerate boxes through the same enclosures):
    True where the midpoint satisfies every constraint with the margin."""
    k = len(problem['squares'])
    eta = problem.get('eta', 0.0)
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
            ok &= G.depth_cell(ps[i], G.rect_i(name, s))[1] <= -margin
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
        ok = alive(cur, problem)
        stats['processed'] += len(cur)
        stats['discarded'] += int((~ok).sum())
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
                 eta=problem.get('eta', 0.0), s=list(problem['s']))
    return stats


def problem_of(specs, s_range, eta=0.0):
    """specs: list of ('M', corner, cells) or ('F', cells).  A meeter of c requires c00 + cells; a
    free square requires its cells and avoids all four boxes."""
    sq = []
    for sp in specs:
        if sp[0] == 'M':
            sq.append({'kind': 'M', 'corner': sp[1], 'req': list(sp[2]), 'avoid': []})
        elif sp[0] == 'P':                                    # plain: required cells only
            sq.append({'kind': 'P', 'req': list(sp[1]), 'avoid': []})
        else:
            sq.append({'kind': 'F', 'req': list(sp[1]), 'avoid': list(G.BOXES)})
    order = []
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if sq[i]['req'] == sq[j]['req'] and sq[i]['avoid'] == sq[j]['avoid']:
                order.append((i, j))
    return {'squares': sq, 's': tuple(s_range), 'eta': eta, 'order': order, 'specs': specs}
