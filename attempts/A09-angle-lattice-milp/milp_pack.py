#!/usr/bin/env python3
"""
milp_pack.py -- "angle-lattice MILP" for packing n unit squares in the smallest square.

Idea (PI): at FIXED orientations the packing problem is a disjunctive LINEAR program.
For a finite angle lattice Theta = {theta_1..theta_K} in [0, 90 deg) we minimise s subject to

  * z_{i,k} in {0,1}, sum_k z_{i,k} = 1            (square i has angle theta_k)
  * containment: w_k = (cos + sin)/2 half-width;   x_i >= sum_k w_k z_ik,  x_i <= s - sum_k w_k z_ik (same for y)
  * disjointness of i<j: exists a signed axis a in A (A = all edge normals of all lattice angles, both
    signs; deduplicated) with  a.(c_j - c_i) >= h_i(a) + h_j(a),  h_i(a) = sum_k H(a,k) z_ik,
    H(a,k) = (|a.e1(k)| + |a.e2(k)|)/2 (support half-width of a unit square of angle theta_k along a).
    Modelled with binaries y_{ij,a}, sum_a y_{ij,a} >= 1, big-M:  a.(c_j-c_i) - h_i - h_j >= -M_a (1 - y_ija).
    Every such constraint is SOUND (disjoint projections => disjoint squares) and the family is COMPLETE
    (SAT: two disjoint convex polygons are separated by an edge normal of one of them, and those are in A).
    Optional strengthening (default on): y_{ij,a} <= z_{i,k(a)} + z_{j,k(a)} (the axis must be an edge normal
    of i or of j), which is valid by the same SAT completeness statement.
  * symmetry breaking (default on): angle index non-decreasing in i, and x_i <= x_{i+1} within an angle class
    (any packing can be relabelled this way); optionally centre of mass in the lower-left quadrant (container
    rotations by 90 deg keep every angle class).

Solver: HiGHS via highspy (default) -- or OR-tools CP-SAT with scaled integers (--solver cpsat) if installed.

Usage examples
  python milp_pack.py --n 11 --angles 0 --time 600
  python milp_pack.py --n 11 --angles 0,45 --time 3600 --out results/n11_0_45.json --png plots/n11_0_45.png
  python milp_pack.py --n 11 --angles 0,40.18193729032971646523 --time 7200
  python milp_pack.py --n 11 --angles 0,5,10,15,20,25,30,35,40,45 --time 3600

Output JSON: {n, angles_deg, s, status, gap, time, squares: [{cx, cy, theta_deg, angle_index}], ...}
Author: A09-angle-lattice-milp.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'code'))


# --------------------------------------------------------------------------------------------
# geometry of the lattice
# --------------------------------------------------------------------------------------------
def build_axes(angles_deg, tol=1e-9):
    """Return (axes, owner): axes = list of unit vectors (both signs), owner[a] = index k of the lattice
    angle whose edge normal it is.  Directions are deduplicated modulo the tolerance."""
    axes, owner = [], []
    for k, th in enumerate(angles_deg):
        t = math.radians(th)
        for d in (t, t + math.pi / 2):
            for sgn in (1.0, -1.0):
                v = (sgn * math.cos(d), sgn * math.sin(d))
                dup = False
                for u in axes:
                    if abs(u[0] - v[0]) < tol and abs(u[1] - v[1]) < tol:
                        dup = True
                        break
                if not dup:
                    axes.append(v)
                    owner.append(k)
    return axes, owner


def support_halfwidth(axis, theta_deg):
    """H(a,k) = (|a.e1| + |a.e2|)/2, e1 = (cos,sin), e2 = (-sin,cos)."""
    t = math.radians(theta_deg)
    e1 = (math.cos(t), math.sin(t))
    e2 = (-math.sin(t), math.cos(t))
    return (abs(axis[0] * e1[0] + axis[1] * e1[1]) + abs(axis[0] * e2[0] + axis[1] * e2[1])) / 2


def half_width(theta_deg):
    t = math.radians(theta_deg)
    return (abs(math.cos(t)) + abs(math.sin(t))) / 2


# --------------------------------------------------------------------------------------------
# HiGHS model
# --------------------------------------------------------------------------------------------
class Model:
    def __init__(self, n, angles_deg, s_max=4.0, symbreak=True, com=True, link=True, s_min=None,
                 fixed_counts=None, sum_y_eq=False):
        self.n = n
        self.angles = list(angles_deg)
        K = len(self.angles)
        self.K = K
        self.s_max = s_max
        self.axes, self.owner = build_axes(self.angles)
        A = len(self.axes)
        self.A = A
        self.W = [half_width(t) for t in self.angles]
        self.H = [[support_halfwidth(a, t) for t in self.angles] for a in self.axes]   # H[a][k]
        self.pairs = list(itertools.combinations(range(n), 2))
        # variable indexing
        self.idx_s = 0
        self.idx_x = lambda i: 1 + i
        self.idx_y = lambda i: 1 + n + i
        self.idx_z = lambda i, k: 1 + 2 * n + i * K + k
        base = 1 + 2 * n + n * K
        self.pair_pos = {p: q for q, p in enumerate(self.pairs)}
        self.idx_w = lambda i, j, a: base + self.pair_pos[(i, j)] * A + a
        self.ncol = base + len(self.pairs) * A
        self.symbreak, self.com, self.link = symbreak, com, link
        self.s_min = s_min if s_min is not None else math.sqrt(n)
        self.fixed_counts = fixed_counts
        self.sum_y_eq = sum_y_eq
        self._build_rows()

    def _build_rows(self):
        n, K, A = self.n, self.K, self.A
        rows = []      # (lo, hi, {col: coef})
        inf = float('inf')
        # containment
        for i in range(n):
            for coord in (self.idx_x, self.idx_y):
                d = {coord(i): 1.0}
                for k in range(K):
                    d[self.idx_z(i, k)] = -self.W[k]
                rows.append((0.0, inf, dict(d)))                    # x - sum w z >= 0
                d2 = {coord(i): 1.0, self.idx_s: -1.0}
                for k in range(K):
                    d2[self.idx_z(i, k)] = self.W[k]
                rows.append((-inf, 0.0, d2))                        # x - s + sum w z <= 0
        # angle choice
        for i in range(n):
            rows.append((1.0, 1.0, {self.idx_z(i, k): 1.0 for k in range(K)}))
        # fixed counts (optional): number of squares with angle k
        if self.fixed_counts is not None:
            for k, cnt in enumerate(self.fixed_counts):
                rows.append((float(cnt), float(cnt), {self.idx_z(i, k): 1.0 for i in range(n)}))
        # disjointness
        self.M = []
        for a, ax in enumerate(self.axes):
            Ma = (self.s_max - 1.0) * (abs(ax[0]) + abs(ax[1])) + 2 * max(self.H[a]) + 1e-6
            self.M.append(Ma)
        for (i, j) in self.pairs:
            rows.append((1.0, 1.0 if self.sum_y_eq else inf, {self.idx_w(i, j, a): 1.0 for a in range(A)}))
            for a, ax in enumerate(self.axes):
                d = {self.idx_x(j): ax[0], self.idx_y(j): ax[1], self.idx_x(i): -ax[0], self.idx_y(i): -ax[1]}
                for k in range(K):
                    d[self.idx_z(i, k)] = -self.H[a][k]
                    d[self.idx_z(j, k)] = d.get(self.idx_z(j, k), 0.0) - self.H[a][k]
                d[self.idx_w(i, j, a)] = -self.M[a]
                rows.append((-self.M[a], inf, d))                   # a.(cj-ci) - hi - hj + M(1-y) >= 0
                if self.link:
                    k = self.owner[a]
                    rows.append((-inf, 0.0, {self.idx_w(i, j, a): 1.0, self.idx_z(i, k): -1.0, self.idx_z(j, k): -1.0}))
        # symmetry breaking: angle index non-decreasing; x non-decreasing inside a class
        if self.symbreak:
            for i in range(n - 1):
                d = {}
                for k in range(K):
                    d[self.idx_z(i, k)] = -float(k)
                    d[self.idx_z(i + 1, k)] = float(k)
                if K > 1:
                    rows.append((0.0, inf, dict(d)))                # idx_{i+1} - idx_i >= 0
                # x_i <= x_{i+1} + Mx (idx_{i+1} - idx_i)
                Mx = self.s_max
                d2 = {self.idx_x(i): -1.0, self.idx_x(i + 1): 1.0}
                for k in range(K):
                    d2[self.idx_z(i, k)] = d2.get(self.idx_z(i, k), 0.0) - Mx * k
                    d2[self.idx_z(i + 1, k)] = d2.get(self.idx_z(i + 1, k), 0.0) + Mx * k
                rows.append((0.0, inf, d2))
        if self.com:
            rows.append((-inf, 0.0, {**{self.idx_x(i): 1.0 for i in range(n)}, self.idx_s: -n / 2.0}))
            rows.append((-inf, 0.0, {**{self.idx_y(i): 1.0 for i in range(n)}, self.idx_s: -n / 2.0}))
        self.rows = rows

    # ---- HiGHS ----
    def to_highs(self, threads=1, time_limit=600.0, mip_gap=1e-7, log=True, log_file=None):
        import highspy
        h = highspy.Highs()
        h.setOptionValue('output_flag', bool(log))
        if log_file:
            h.setOptionValue('log_file', log_file)
        h.setOptionValue('threads', int(threads))
        h.setOptionValue('time_limit', float(time_limit))
        h.setOptionValue('mip_rel_gap', float(mip_gap))
        h.setOptionValue('mip_abs_gap', 1e-7)
        h.setOptionValue('mip_feasibility_tolerance', 1e-7)
        h.setOptionValue('primal_feasibility_tolerance', 1e-8)
        n, K, A = self.n, self.K, self.A
        lp = highspy.HighsLp()
        lp.num_col_ = self.ncol
        lp.num_row_ = len(self.rows)
        cost = np.zeros(self.ncol)
        cost[self.idx_s] = 1.0
        lo = np.zeros(self.ncol)
        hi = np.ones(self.ncol)
        lo[self.idx_s] = self.s_min
        hi[self.idx_s] = self.s_max
        for i in range(n):
            lo[self.idx_x(i)] = 0.5
            hi[self.idx_x(i)] = self.s_max - 0.5
            lo[self.idx_y(i)] = 0.5
            hi[self.idx_y(i)] = self.s_max - 0.5
        lp.col_cost_ = cost
        lp.col_lower_ = lo
        lp.col_upper_ = hi
        rl = np.array([r[0] for r in self.rows])
        ru = np.array([r[1] for r in self.rows])
        lp.row_lower_ = rl
        lp.row_upper_ = ru
        starts, index, value = [0], [], []
        for (_, _, d) in self.rows:
            for c, v in d.items():
                index.append(c)
                value.append(v)
            starts.append(len(index))
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.start_ = np.array(starts, dtype=np.int32)
        lp.a_matrix_.index_ = np.array(index, dtype=np.int32)
        lp.a_matrix_.value_ = np.array(value)
        integ = [highspy.HighsVarType.kContinuous] * self.ncol
        for c in range(1 + 2 * n, self.ncol):
            integ[c] = highspy.HighsVarType.kInteger
        lp.integrality_ = integ
        h.passModel(lp)
        return h

    def warm_start(self, h, X, s):
        """Feed a known packing (X rows (cx,cy,theta_rad)) as MIP start (angles snapped to lattice)."""
        import highspy
        vals = np.zeros(self.ncol)
        vals[self.idx_s] = s
        Xs = self._canonical_order(X)
        for i, (cx, cy, th) in enumerate(Xs):
            vals[self.idx_x(i)] = cx
            vals[self.idx_y(i)] = cy
            k = self._nearest_angle(th)
            vals[self.idx_z(i, k)] = 1.0
        for (i, j) in self.pairs:
            best, ba = -1e9, 0
            for a, ax in enumerate(self.axes):
                ki = self._nearest_angle(Xs[i][2])
                kj = self._nearest_angle(Xs[j][2])
                v = ax[0] * (Xs[j][0] - Xs[i][0]) + ax[1] * (Xs[j][1] - Xs[i][1]) - self.H[a][ki] - self.H[a][kj]
                if self.link and self.owner[a] not in (ki, kj):
                    continue
                if v > best:
                    best, ba = v, a
            vals[self.idx_w(i, j, ba)] = 1.0
        sol = highspy.HighsSolution()
        sol.col_value = list(vals)
        h.setSolution(sol)

    def _nearest_angle(self, th):
        d = math.degrees(th) % 90.0
        return int(np.argmin([min(abs(d - a), abs(d - a - 90), abs(d - a + 90)) for a in self.angles]))

    def _canonical_order(self, X):
        X = np.asarray(X, float)
        keys = [(self._nearest_angle(th), cx) for (cx, cy, th) in X]
        order = sorted(range(len(X)), key=lambda i: keys[i])
        return X[order]

    def extract(self, h):
        sol = h.getSolution()
        v = np.array(sol.col_value)
        s = v[self.idx_s]
        sq = []
        for i in range(self.n):
            k = int(np.argmax([v[self.idx_z(i, kk)] for kk in range(self.K)]))
            sq.append({'cx': float(v[self.idx_x(i)]), 'cy': float(v[self.idx_y(i)]),
                       'theta_deg': self.angles[k], 'angle_index': k})
        return float(s), sq


# --------------------------------------------------------------------------------------------
# CP-SAT alternative (scaled integers)
# --------------------------------------------------------------------------------------------
def solve_cpsat(m: Model, time_limit, threads, scale=100000, log=True, seed=0):
    from ortools.sat.python import cp_model
    S = scale
    n, K, A = m.n, m.K, m.A
    md = cp_model.CpModel()
    smax = int(round(m.s_max * S))
    s = md.NewIntVar(int(math.ceil(m.s_min * S)), smax, 's')
    x = [md.NewIntVar(0, smax, f'x{i}') for i in range(n)]
    y = [md.NewIntVar(0, smax, f'y{i}') for i in range(n)]
    z = [[md.NewBoolVar(f'z{i}_{k}') for k in range(K)] for i in range(n)]
    for i in range(n):
        md.AddExactlyOne(z[i])
        for k in range(K):
            w = int(math.ceil(m.W[k] * S))
            md.Add(x[i] >= w).OnlyEnforceIf(z[i][k])
            md.Add(x[i] <= s - w).OnlyEnforceIf(z[i][k])
            md.Add(y[i] >= w).OnlyEnforceIf(z[i][k])
            md.Add(y[i] <= s - w).OnlyEnforceIf(z[i][k])
    # axes: scale a to integers too: a.(cj-ci) >= h_i + h_j  ->  Sa_x dx + Sa_y dy >= S^2 (H_i+H_j)  (over-approx by ceil)
    for (i, j) in m.pairs:
        ys = []
        for a, ax in enumerate(m.axes):
            ya = md.NewBoolVar(f'y{i}_{j}_{a}')
            ys.append(ya)
            axx, ayy = int(round(ax[0] * S)), int(round(ax[1] * S))
            for ki in range(K):
                for kj in range(K):
                    if m.link and m.owner[a] not in (ki, kj):
                        continue
                    rhs = int(math.ceil((m.H[a][ki] + m.H[a][kj]) * S * S))
                    md.Add(axx * (x[j] - x[i]) + ayy * (y[j] - y[i]) >= rhs).OnlyEnforceIf([ya, z[i][ki], z[j][kj]])
            if m.link:
                k = m.owner[a]
                md.AddBoolOr([z[i][k], z[j][k]]).OnlyEnforceIf(ya)
        md.AddBoolOr(ys)
    if m.symbreak:
        for i in range(n - 1):
            idx_i = sum(k * z[i][k] for k in range(K))
            idx_j = sum(k * z[i + 1][k] for k in range(K))
            md.Add(idx_i <= idx_j)
            same = md.NewBoolVar(f'same{i}')
            md.Add(idx_i == idx_j).OnlyEnforceIf(same)
            md.Add(idx_i < idx_j).OnlyEnforceIf(same.Not())
            md.Add(x[i] <= x[i + 1]).OnlyEnforceIf(same)
    if m.com:
        md.Add(2 * sum(x) <= n * s)
        md.Add(2 * sum(y) <= n * s)
    md.Minimize(s)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_workers = int(threads)
    solver.parameters.log_search_progress = bool(log)
    solver.parameters.random_seed = int(seed)
    t0 = time.time()
    st = solver.Solve(md)
    dt = time.time() - t0
    status = solver.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        sv = solver.Value(s) / S
        sq = []
        for i in range(n):
            k = [kk for kk in range(K) if solver.Value(z[i][kk])][0]
            sq.append({'cx': solver.Value(x[i]) / S, 'cy': solver.Value(y[i]) / S,
                       'theta_deg': m.angles[k], 'angle_index': k})
        lb = solver.BestObjectiveBound() / S
        return {'s': sv, 'status': status, 'bound': lb, 'time': dt, 'squares': sq}
    return {'s': None, 'status': status, 'bound': solver.BestObjectiveBound() / S, 'time': dt, 'squares': []}


# --------------------------------------------------------------------------------------------
# post-processing
# --------------------------------------------------------------------------------------------
def polish_lp(m: Model, res, slack=0.0):
    """With the angle assignment and the separating axis of every pair FIXED (taken from the solver's
    solution: the axis with the largest margin), the problem is an LP in (s, centres); solve it with
    HiGHS LP to get s of that combinatorial structure to ~1e-9.  Also returns the LP status."""
    from scipy.optimize import linprog
    n = m.n
    sq = res['squares']
    ks = [q['angle_index'] for q in sq]
    nv = 1 + 2 * n
    A_ub, b_ub = [], []
    # containment: w <= x <= s - w
    bounds = [(m.s_min, m.s_max)] + [(None, None)] * (2 * n)
    for i in range(n):
        w = m.W[ks[i]]
        bounds[1 + i] = (w + slack, None)
        bounds[1 + n + i] = (w + slack, None)
        for coord in (1 + i, 1 + n + i):
            row = np.zeros(nv)
            row[coord] = 1.0
            row[0] = -1.0
            A_ub.append(row)
            b_ub.append(-w - slack)
    for (i, j) in m.pairs:
        best, ba = -1e9, None
        for a, ax in enumerate(m.axes):
            v = ax[0] * (sq[j]['cx'] - sq[i]['cx']) + ax[1] * (sq[j]['cy'] - sq[i]['cy']) - m.H[a][ks[i]] - m.H[a][ks[j]]
            if v > best:
                best, ba = v, a
        ax = m.axes[ba]
        row = np.zeros(nv)
        row[1 + j] -= ax[0]
        row[1 + n + j] -= ax[1]
        row[1 + i] += ax[0]
        row[1 + n + i] += ax[1]
        A_ub.append(row)
        b_ub.append(-(m.H[ba][ks[i]] + m.H[ba][ks[j]]) - slack)
    c = np.zeros(nv)
    c[0] = 1.0
    r = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method='highs')
    if r.status != 0:
        return None
    s = float(r.x[0])
    out = []
    for i in range(n):
        out.append({'cx': float(r.x[1 + i]), 'cy': float(r.x[1 + n + i]), 'theta_deg': m.angles[ks[i]], 'angle_index': ks[i]})
    return s, out


def check_and_polish(res, m: Model):
    """Float check with code/squares.py, then LP polish (structure fixed)."""
    from squares import pair_separations, containment_margin
    X = np.array([[q['cx'], q['cy'], math.radians(q['theta_deg'])] for q in res['squares']])
    s = res['s']
    res['float_min_sep'] = float(pair_separations(X).min())
    res['float_min_margin'] = float(containment_margin(X, s).min())
    res['s_solver'] = s
    p = polish_lp(m, res)
    if p is not None:
        s2, sq2 = p
        X2 = np.array([[q['cx'], q['cy'], math.radians(q['theta_deg'])] for q in sq2])
        res['s_polished'] = s2
        res['polished_min_sep'] = float(pair_separations(X2).min())
        res['polished_min_margin'] = float(containment_margin(X2, s2).min())
        res['s'] = s2
        res['squares'] = sq2
    return res


def describe_structure(res):
    from collections import Counter
    c = Counter(round(q['theta_deg'], 6) for q in res['squares'])
    return ' + '.join(f'{v}x{k:g}deg' for k, v in sorted(c.items()))


def plot(res, path, title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from squares import plot_packing
    X = np.array([[q['cx'], q['cy'], math.radians(q['theta_deg'])] for q in res['squares']])
    ax = plot_packing(X, res['s'], title=title or f"n={len(X)}  s={res['s']:.9f}  {describe_structure(res)}")
    ax.figure.savefig(path, dpi=130, bbox_inches='tight')
    plt.close(ax.figure)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=11)
    ap.add_argument('--angles', type=str, default='0,45', help='comma separated degrees in [0,90)')
    ap.add_argument('--time', type=float, default=600.0)
    ap.add_argument('--threads', type=int, default=1)
    ap.add_argument('--smax', type=float, default=4.0)
    ap.add_argument('--smin', type=float, default=None)
    ap.add_argument('--fix-s', type=float, default=None, help='feasibility mode: s fixed to this value')
    ap.add_argument('--gap', type=float, default=1e-7)
    ap.add_argument('--no-symbreak', action='store_true')
    ap.add_argument('--no-com', action='store_true')
    ap.add_argument('--no-link', action='store_true')
    ap.add_argument('--sum-y-eq', action='store_true', help='use sum_a y = 1 instead of >= 1')
    ap.add_argument('--counts', type=str, default=None, help='fix the number of squares per angle, e.g. 6,5')
    ap.add_argument('--warm', type=str, default=None, help='JSON packing (this format or certs trump) as MIP start')
    ap.add_argument('--solver', choices=['highs', 'cpsat'], default='highs')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', type=str, default=None)
    ap.add_argument('--png', type=str, default=None)
    ap.add_argument('--log', type=str, default=None)
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()

    angles = [float(a) for a in args.angles.split(',')]
    counts = [int(c) for c in args.counts.split(',')] if args.counts else None
    if args.fix_s is not None:
        args.smax = args.fix_s
        args.smin = args.fix_s
    m = Model(args.n, angles, s_max=args.smax, symbreak=not args.no_symbreak, com=not args.no_com,
              link=not args.no_link, s_min=args.smin, fixed_counts=counts, sum_y_eq=args.sum_y_eq)
    print(f'n={args.n} angles={angles} axes={m.A} cols={m.ncol} rows={len(m.rows)} solver={args.solver}', flush=True)
    t0 = time.time()
    if args.solver == 'cpsat':
        res = solve_cpsat(m, args.time, args.threads, log=not args.quiet, seed=args.seed)
        res['proven_optimal'] = res['status'] == 'OPTIMAL'
        res['gap'] = (res['s'] - res['bound']) / res['s'] if res['s'] else None
    else:
        h = m.to_highs(threads=args.threads, time_limit=args.time, mip_gap=args.gap, log=not args.quiet,
                       log_file=args.log)
        if args.warm:
            with open(args.warm) as f:
                W = json.load(f)
            if 'squares' in W and 'theta_deg' in W['squares'][0]:
                X = [[q['cx'], q['cy'], math.radians(q['theta_deg'])] for q in W['squares']]
                sw = W['s']
            else:
                from fractions import Fraction as F
                X = []
                for q in W['squares']:
                    t = float(F(q['t']))
                    X.append([float(F(q['cx'])), float(F(q['cy'])), 2 * math.atan(t)])
                sw = float(F(W['side']))
            m.warm_start(h, X, sw)
        h.run()
        info = h.getInfo()
        status = h.modelStatusToString(h.getModelStatus())
        dt = time.time() - t0
        res = {'status': status, 'time': dt, 'squares': [], 's': None}
        if info.primal_solution_status > 0:
            s, sq = m.extract(h)
            res.update({'s': s, 'squares': sq})
        res['bound'] = float(info.mip_dual_bound)
        res['gap'] = float(info.mip_gap)
        res['nodes'] = int(info.mip_node_count)
        res['proven_optimal'] = status == 'Optimal'
    res.update({'n': args.n, 'angles_deg': angles, 'solver': args.solver, 'threads': args.threads,
                'time_limit': args.time, 'options': {'symbreak': not args.no_symbreak, 'com': not args.no_com,
                                                     'link': not args.no_link, 'counts': counts}})
    if res['s'] is not None:
        check_and_polish(res, m)
        res['structure'] = describe_structure(res)
        print(f"RESULT n={args.n} angles={angles} s={res['s']:.10f} (solver {res['s_solver']:.7f}) bound={res['bound']:.10f} "
              f"status={res['status']} time={res['time']:.1f}s structure={res['structure']} "
              f"min_sep={res.get('polished_min_sep', res['float_min_sep']):.2e} "
              f"min_margin={res.get('polished_min_margin', res['float_min_margin']):.2e}", flush=True)
        if args.png:
            plot(res, args.png)
    else:
        print(f"RESULT n={args.n} angles={angles} NO SOLUTION status={res['status']} bound={res['bound']} time={res['time']:.1f}s")
    if args.out:
        with open(args.out, 'w') as f:
            json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
