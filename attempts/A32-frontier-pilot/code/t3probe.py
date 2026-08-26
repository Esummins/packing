"""A32 cascade stages 4-6: the metric/first-order tests, on STRUCTURE-DERIVED cells.

A node's structure induces a coordinate cell
    C(node) = prod_i (centre box from wall mask) x (tilt interval) x (s interval)
which SHRINKS under extension, so any sound per-cell exclusion applied to C(node)
is a monotone kill for the node.  We measure cost and firing rate of

  stage 4a  interval SAT / D2 on C(node)           (t3lib.test_ab)
  stage 4b  bonus test (a'): an empty pair menu certifies C n D0 = 0
  stage 4   FARKAS / Gordan first-order test on the union of rows that can be
            active on C(node)                      (t3lib.farkas_lp + interval
            verification) -- exactly first-order complete per drain_lemma v3 (c1)
  stage 5   case-LP style feasibility LP on the interval-linearised rows (STUB,
            cost measurement only)
  stage 6   FJ Krawczyk on one selection                (t3lib.krawczyk_fj)

t3lib is hard-wired to 11 squares with s at index 33; it is imported READ-ONLY and
the two globals (NSQ, NV) plus the s-index-dependent helpers are re-bound locally.
"""
import os
import sys
import json
import math
import time
import random
from fractions import Fraction

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_A30 = os.path.normpath(os.path.join(_HERE, '..', '..', 'A30-t3-pilot'))
if _A30 not in sys.path:
    sys.path.insert(0, _A30)

import t3lib as T                                            # noqa: E402
from mpmath import iv                                        # noqa: E402
import core as C                                             # noqa: E402
import lib0 as L                                             # noqa: E402

S_LO, S_HI = L.S_LO, L.S_HI


def set_k(k):
    T.NSQ = k
    T.NV = 3 * k + 1


def wall_row(k, i, corner, wall):
    vs = (3 * i, 3 * i + 1, 3 * i + 2) + ((3 * k,) if wall in ('x=s', 'y=s') else ())
    return {'kind': 'wall', 'i': i, 'corner': corner, 'wall': wall, 'vars': vs}


def build_box(k, wm, tilt=None, s_range=(S_LO, S_HI)):
    """Structure-derived cell.  tilt[i] = (lo, hi) in radians (default [0, pi/2])."""
    box = []
    for i in range(k):
        (xl, xh), (yl, yh) = C.BOX[wm[i]]
        box.append(iv.mpf([xl, xh]))
        box.append(iv.mpf([yl, yh]))
        tl, th = tilt[i] if tilt else (0.0, math.pi / 2)
        box.append(iv.mpf([tl, th]))
    box.append(iv.mpf([s_range[0], s_range[1]]))
    return box


def rows_on_cell(k, box, max_pairs=None):
    """Every row that can be active anywhere on the cell (wall rows that straddle,
    plus the union over each straddling pair's selection menu)."""
    union = {}
    infeasible = None
    for i in range(k):
        for c in range(4):
            for w in T.WALLS:
                r = wall_row(k, i, c, w)
                v = T.row_value(box, r)
                if v.b < 0:
                    return None, 'containment', 0
                if v.a <= 0:
                    union[T.row_key(r)] = r
    npairs = 0
    empty_menu = False
    for i in range(k):
        for j in range(i + 1, k):
            g = T.pair_sep_iv(box, i, j)
            if g.b < 0:
                return None, 'pair_overlap', 0
            if g.a > 0:
                continue
            npairs += 1
            menu = T.pair_menu(box, i, j)
            if not menu:
                empty_menu = True
            for sel in menu:
                for r in sel['straddle']:
                    union[T.row_key(r)] = r
    if empty_menu:
        return None, 'empty_menu', npairs
    return list(union.values()), None, npairs


def farkas_generic(k, box, rows, ybound=1.0):
    """Farkas LP with the s variable at index 3k (t3lib's is hard-wired to 33)."""
    from scipy.optimize import linprog
    NV = 3 * k + 1
    sidx = 3 * k
    G = []
    for r in rows:
        _, g = T.row_grad(box, r)
        lo = np.zeros(NV)
        hi = np.zeros(NV)
        for gi, val in g.items():
            lo[gi] = float(val.a)
            hi[gi] = float(val.b)
        G.append((lo, hi))
    n = 2 * NV + 1
    A = np.zeros((len(G) + 1, n))
    b = np.zeros(len(G) + 1)
    for t, (lo, hi) in enumerate(G):
        A[t, :NV] = -lo
        A[t, NV:2 * NV] = hi
        A[t, -1] = 1.0
    A[-1, sidx] = 1.0
    A[-1, NV + sidx] = -1.0
    A[-1, -1] = 1.0
    c = np.zeros(n)
    c[-1] = -1.0
    bounds = [(0, ybound)] * (2 * NV) + [(0, 1.0)]
    r = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    if not r.success:
        return False, None, 0.0
    eps = -r.fun
    return eps > 1e-12, r.x[:NV] - r.x[NV:2 * NV], float(eps)


def verify(k, box, rows, y):
    yiv = [T._to_iv(Fraction(float(v)).limit_denominator(10 ** 12)) for v in y]
    if not (yiv[3 * k].b < 0):
        return False
    for r in rows:
        _, g = T.row_grad(box, r)
        acc = iv.mpf(0)
        for gi, val in g.items():
            acc = acc + val * yiv[gi]
        if not (acc.a > 0):
            return False
    return True


def lp_feasibility_stub(k, box, rows):
    """Stage-5 STUB: LP feasibility of the interval-linearised row system on the
    cell (the shape A27's case-LP has).  Cost measurement only -- a NEGATIVE
    result here is NOT used as a kill (the linearisation is not certified)."""
    from scipy.optimize import linprog
    NV = 3 * k + 1
    mid = np.array([float((b.a + b.b) / 2) for b in box])
    rad = np.array([float((b.b - b.a) / 2) for b in box])
    A = []
    bb = []
    for r in rows:
        v, g = T.row_grad(box, r)
        lo = np.zeros(NV)
        hi = np.zeros(NV)
        for gi, val in g.items():
            lo[gi] = float(val.a)
            hi[gi] = float(val.b)
        # sound relaxation: g(z) >= v.a + sum_i min over gradient interval
        A.append(-np.where(lo > 0, lo, hi))
        bb.append(float(v.b))
    A = np.array(A)
    bb = np.array(bb)
    c = np.zeros(NV)
    c[3 * k] = 1.0
    bounds = [(-rad[i] , rad[i]) for i in range(NV)]
    r = linprog(c, A_ub=A, b_ub=bb, bounds=bounds, method='highs')
    return bool(r.success)


def fj_range_exclude_g(k, box, rows, lam0=(0.0, 1.0), lamb=(0.0, 1.0)):
    """Generic (any k) version of t3lib.fj_range_exclude: interval evaluation of
    the Fritz John residual with lam0, lam ranging over the normalisation box.  If
    any component's interval misses 0, FJ(S) has no solution in the cell.  SOUND;
    this is the cheap dimension-agnostic part of stage 6 (the full Krawczyk step
    needs a square system, i.e. a DECORATION-determined active set -- see the
    report's stage-6 note)."""
    NV = 3 * k + 1
    sidx = 3 * k
    l0 = iv.mpf([lam0[0], lam0[1]])
    lk = iv.mpf([lamb[0], lamb[1]])
    F = [iv.mpf(0)] * NV
    F[sidx] = l0
    vals = []
    for r in rows:
        v, g = T.row_grad(box, r)
        vals.append(v)
        for gi, val in g.items():
            F[gi] = F[gi] - lk * val
    for i, f in enumerate(F):
        if f.a > 0 or f.b < 0:
            return True, ('stationarity', i)
    for i, v in enumerate(vals):            # complementarity lam_k g_k = 0
        p = lk * v
        if p.a > 0 or p.b < 0:
            return True, ('compl', i)
    return False, None


def active_rows_from_contacts(k, box, ss, sw):
    """Rows that the CONTACT structure declares active: for each square-square
    contact the pair's straddling selection rows, for each wall contact the
    straddling containment rows of that wall."""
    out = []
    for (i, j) in ss:
        menu = T.pair_menu(box, i, j)
        if menu:
            sel = menu[0]
            out += sel['rows']
    for (i, b) in sw:
        w = T.WALLS[b] if b < 4 else 'x=0'
        for c in range(4):
            out.append(wall_row(k, i, c, w))
    return out


def probe_node(k, wm, tilt=None, do_lp=False, do_fj=False):
    set_k(k)
    out = {'k': k, 'wm': list(wm)}
    box = build_box(k, wm, tilt)
    t0 = time.perf_counter()
    rows, reason, npairs = rows_on_cell(k, box)
    out['t_rows'] = time.perf_counter() - t0
    out['straddling_pairs'] = npairs
    if rows is None:
        out['stage4a_kill'] = reason
        out['nrows'] = 0
        return out
    out['stage4a_kill'] = None
    out['nrows'] = len(rows)
    t0 = time.perf_counter()
    ok, y, eps = farkas_generic(k, box, rows)
    out['t_farkas'] = time.perf_counter() - t0
    out['farkas_lp_ok'] = bool(ok)
    out['farkas_eps'] = eps
    if ok:
        t0 = time.perf_counter()
        out['farkas_verified'] = bool(verify(k, box, rows, y))
        out['t_verify'] = time.perf_counter() - t0
    else:
        out['farkas_verified'] = False
    if do_lp:
        t0 = time.perf_counter()
        try:
            out['stage5_lp_feasible'] = lp_feasibility_stub(k, box, rows)
        except Exception as e:                                # pragma: no cover
            out['stage5_lp_feasible'] = 'error: %s' % e
        out['t_stage5_lp'] = time.perf_counter() - t0
    if do_fj is not False:
        ss, sw = do_fj if isinstance(do_fj, tuple) else ([], [])
        t0 = time.perf_counter()
        arows = active_rows_from_contacts(k, box, ss, sw)
        ok, why = fj_range_exclude_g(k, box, arows)
        out['stage6_active_rows'] = len(arows)
        out['stage6_fj_excluded'] = bool(ok)
        out['stage6_why'] = why
        out['t_stage6_fj'] = time.perf_counter() - t0
    return out
