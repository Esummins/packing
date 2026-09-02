#!/usr/bin/env python3
"""explore1.py -- sanity + Krawczyk radius scans in t-coordinates (design/measurement only).

1. centre residuals of A22's 42 rows at z0_t (expect ~1e-60);
2. Krawczyk on A22's S (34 rows) at r = 5e-4 (regression vs A22) and a radius scan;
3. pinned Krawczyk: pin rows for a Trump sub-skeleton P replace the redundant S rows;
   radius scan per P.
Usage: python explore1.py [uniform|theta]   (theta: tilt radius = r/2, i.e. the theta-box)
"""
import sys
import time
import json
from fractions import Fraction
import numpy as np
from grainlib import *


def square_system(rows_all, prefer, z0f):
    """greedy independent 34-row subset: rows in `prefer` order (indices into rows_all)."""
    A = grad_matrix_float(z0f, rows_all)
    chosen = []
    M = np.zeros((0, NV))
    for k in prefer:
        M2 = np.vstack([M, A[k]])
        if np.linalg.matrix_rank(M2, tol=1e-9) > M.shape[0]:
            M = M2
            chosen.append(k)
        if len(chosen) == NV:
            break
    return chosen


def kraw_scan(z0, rows_all, sel, rs, mode, label):
    z0f = to_float_z(z0)
    sub = [rows_all[k] for k in sel]
    A = grad_matrix_float(z0f, sub)
    Y = rationalize_matrix(np.linalg.inv(A), 10 ** 40)
    print('%s: |S|=%d cond=%.3g' % (label, len(sel), np.linalg.cond(A)))
    out = []
    for r in rs:
        rr = radii(r, r / 2, r) if mode == 'theta' else Fraction(r)
        t0 = time.time()
        ok, worst = krawczyk(z0, rr, sub, Y)
        print('   r=%-9s contracts=%-5s max|K|/r=%.4f  (%.1fs)' % (r, ok, float(worst), time.time() - t0))
        out.append((str(r), ok, float(worst)))
        if not ok:
            break
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'uniform'
    z0 = load_z0()
    rows, d = a22_rows()
    zc = [IV.point(x) for x in z0]
    mx = max(eval_row(zc, c).mag() for c in rows)
    print('max centre residual over 42 rows: %.3e' % float(mx))
    S = d['S']
    z0f = to_float_z(z0)
    res = {}
    rs = [Fraction(5, 10000), Fraction(2, 1000), Fraction(4, 1000), Fraction(6, 1000),
          Fraction(8, 1000), Fraction(10, 1000), Fraction(12, 1000), Fraction(15, 1000),
          Fraction(20, 1000)]
    res['S'] = kraw_scan(z0, rows, S, rs, mode, 'A22 S (t-coords)')
    # F~ system S2 (angle equalities)
    res['S2'] = kraw_scan(z0, rows, d['S2'], rs, mode, 'A22 S2 (with teq rows)')
    # pinned systems
    pinsets = {'k4_08': [0, 1, 3, 5], 'k4_11': [0, 3, 2, 5], 'k4_03': [0, 1, 3, 2],
               'k4_x': [0, 1, 2, 5], 'trump5': [0, 1, 2, 3, 5], 'k3_02': [0, 1, 3],
               'k3_03': [0, 3, 2], 'k3_04': [0, 3, 5], 'k2_00': [0, 3], 'k1_00': [0]}
    for name, P in pinsets.items():
        prow = pin_rows(P)
        rows_all = rows + prow
        prefer = list(range(len(rows), len(rows_all))) + list(d['S2'])
        sel = square_system(rows_all, prefer, z0f)
        res['pin_' + name + '_S2'] = kraw_scan(z0, rows_all, sel, rs, mode, 'pins %s + S2 rows' % name)
        prefer = list(range(len(rows), len(rows_all))) + list(S)
        sel = square_system(rows_all, prefer, z0f)
        res['pin_' + name + '_S'] = kraw_scan(z0, rows_all, sel, rs, mode, 'pins %s + S rows' % name)
    json.dump(res, open(os.path.join(HERE, '..', 'results', 'explore1_%s.json' % mode), 'w'), indent=1)


if __name__ == '__main__':
    main()
