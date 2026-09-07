"""A119 -- a thin HiGHS binding for the tree's inner loop.

`scipy.optimize.linprog` spends ~1.5 ms per call on option validation, input cleaning and
sparse-matrix construction for LPs this small (20 columns, 60-200 dense rows); HiGHS itself
takes ~0.4 ms.  This module passes the model straight to a single reused `highspy.Highs`
instance.  It returns the SAME (value, x, y) triple as `a116lib.Rows.solve`, with y the
non-negative multipliers of the `A x <= b` rows -- regression-checked against linprog in
code/xcheck119.py.
"""
from __future__ import annotations
import math
import numpy as np
import highspy

_INF = highspy.kHighsInf
_H = None


def _highs():
    global _H
    if _H is None:
        _H = highspy.Highs()
        _H.setOptionValue("output_flag", False)
        _H.setOptionValue("log_to_console", False)
        _H.setOptionValue("threads", 1)
        _H.setOptionValue("presolve", "off")
    return _H


def solve_phase1(A, b, bounds, nv, big=1e6):
    """Farkas certificate of infeasibility of {A x <= b, bounds}: solve
        min tau  s.t.  A x - tau <= b,  bounds,  tau >= 0.
    tau* > 0 proves the original system infeasible, and the row duals y of the optimum satisfy
    y >= 0 and  min_box (A^T y).x - y.b  =  tau* > 0  (the certificate the checker re-derives).
    Returns (tau, y)."""
    m = len(b)
    A2 = [list(r) + [-1.0] for r in A]
    b2 = list(b)
    bnd = list(bounds) + [(0.0, big)]
    h = _highs()
    lp = highspy.HighsLp()
    lp.num_col_ = nv + 1
    lp.num_row_ = m
    c = np.zeros(nv + 1); c[nv] = 1.0
    lp.col_cost_ = c
    lp.col_lower_ = np.array([q[0] for q in bnd], dtype=float)
    lp.col_upper_ = np.array([q[1] for q in bnd], dtype=float)
    lp.row_lower_ = np.full(m, -_INF)
    lp.row_upper_ = np.asarray(b2, dtype=float)
    Am = np.asarray(A2, dtype=float).reshape(m, nv + 1)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = np.arange(0, m * (nv + 1) + 1, nv + 1)
    lp.a_matrix_.index_ = np.tile(np.arange(nv + 1), m)
    lp.a_matrix_.value_ = Am.ravel()
    h.clearModel()
    h.passModel(lp)
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        return 0.0, None
    sol = h.getSolution()
    y = -np.array(sol.row_dual) if m else np.zeros(0)
    return float(h.getInfo().objective_function_value), np.maximum(y, 0.0)


def solve(A, b, bounds, nv):
    """min s = x[0] s.t. A x <= b, bounds[i] = (lo, hi).  Returns (value, x, y) with
    y >= 0 the row multipliers (value = inf if infeasible, -inf if unbounded/failed)."""
    h = _highs()
    m = len(b)
    lp = highspy.HighsLp()
    lp.num_col_ = nv
    lp.num_row_ = m
    c = np.zeros(nv); c[0] = 1.0
    lp.col_cost_ = c
    lp.col_lower_ = np.array([bd[0] for bd in bounds], dtype=float)
    lp.col_upper_ = np.array([bd[1] for bd in bounds], dtype=float)
    lp.row_lower_ = np.full(m, -_INF)
    lp.row_upper_ = np.asarray(b, dtype=float)
    Am = np.asarray(A, dtype=float).reshape(m, nv)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = np.arange(0, m * nv + 1, nv)
    lp.a_matrix_.index_ = np.tile(np.arange(nv), m)
    lp.a_matrix_.value_ = Am.ravel()
    h.clearModel()
    h.passModel(lp)
    h.run()
    st = h.getModelStatus()
    if st == highspy.HighsModelStatus.kInfeasible:
        return math.inf, None, None
    if st != highspy.HighsModelStatus.kOptimal:
        return -math.inf, None, None
    sol = h.getSolution()
    x = np.array(sol.col_value)
    y = -np.array(sol.row_dual) if m else np.zeros(0)
    return float(h.getInfo().objective_function_value), x, np.maximum(y, 0.0)
