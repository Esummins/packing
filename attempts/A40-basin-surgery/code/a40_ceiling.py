#!/usr/bin/env python
"""a40_ceiling.py -- A40 Step B: the CEILING scan.  For each of the 68 shell
faces, the largest thin-ring radius h at which an anchor certificate (Lemma S5)
can exist, when the multiplier cone is enriched with EVERYTHING the surgery
lemma can ever make valid:

  arsenal = A22 rows 0..35 alive at h ([V])                     unconditional
          + aux dist rows 44,45                                  unconditional
          + all 4 corner rows of every ALIVE axis of every       branch-cond.
            contact pair (the surgery branches)
          + all 4 corner rows of every alive/safe axis of the    gained rows
            near pairs (6,7),(8,9),(3,4),(7,10)

Rows conditional on a branch are marked; the scan is an UPPER BOUND on the
honest per-branch loop (a branch cannot use two axes of one pair at once, and
the scan lets omega mix them).  A face whose ceiling is below the target dies
honestly; the loop can only do worse.

Margin LP at ring [h, rho*h], face (i, sgn):
  max  m = omega_b*h - sum_r omega_r*max(gval_r,0)*1 + sum_r omega_r*min(gval_r,0)*(-1)
           ... i.e.  omega_b*h - sum_r omega_r*gval_r  - 0.5*(w.omega)*(rho*h)^2
  s.t. A^T omega + sgn*omega_b*e_i = e_s,  omega >= 0, omega_b >= 0.
(gval_r = g_r(z-hat) signed: a negative-at-zhat branch row is an extra anchor.)
Note eps_w = 0 at the design point; the loop pays the rationalisation residual.

Output: results/ceiling.json
"""
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A40 = os.path.abspath(os.path.join(HERE, '..'))
RESULTS = os.path.join(A40, 'results')
sys.path.insert(0, os.path.join(A40, '..', 'A36-levers', 'code'))
sys.path.insert(0, HERE)

import a36_lib as L                       # noqa: E402
import strata_lib as SL                   # noqa: E402
import m2_lib as M                        # noqa: E402
from a40_margins import (corner_frame, axis_gap_bounds, pair_axes,
                         edge_rows_a22, boxes_at, sup, inf)   # noqa: E402

iv.dps = 60
RHO = 1.02
CONTACT_PAIRS = [(0, 1), (0, 3), (1, 3), (1, 8), (2, 8), (3, 7), (4, 6),
                 (4, 7), (5, 9), (6, 9), (7, 8), (7, 9), (8, 10), (9, 10)]
NEAR_PAIRS = [(6, 7), (8, 9), (3, 4), (7, 10)]


def build_arsenal():
    """Row table: (tag, condict, kind, pair, axis) for every candidate row."""
    rows = []
    K = SL.load_cert()
    for r, c in enumerate(K['constraints'][:36]):
        rows.append(('a22_%d' % r, dict(c), 'a22', None, None))
    rows.append(('aux44', dict(K['constraints'][36]), 'aux', None, None))
    rows.append(('aux45', dict(K['constraints'][37]), 'aux', None, None))
    for (i, j) in CONTACT_PAIRS + NEAR_PAIRS:
        kind = 'branch' if (i, j) in CONTACT_PAIRS else 'gained'
        for (o, e, p) in pair_axes(i, j):
            for k in range(4):
                rows.append(('%s_%d-%d_o%de%dk%d' % (kind, i, j, o, e, k),
                             L.edge_con(o, e, p, k), kind, (i, j), (o, e, p)))
    return rows


def main():
    t0 = time.time()
    os.makedirs(RESULTS, exist_ok=True)
    arsenal = build_arsenal()
    n = len(arsenal)
    print('%d candidate rows' % n)
    pb = SL.point_box()

    # values + gradients at z-hat, Hessian masses at h=0.03  [IV]
    gval = np.zeros(n)
    A = np.zeros((n, 34))
    w = np.zeros(n)
    bx = M.box_around(SL.z_hat(), Fraction(3, 100))
    t3rows = [SL.to_t3_row(c) for (_, c, _, _, _) in arsenal]
    for k, r in enumerate(t3rows):
        j0 = SL.eval_geo(pb, r, order=1)
        gval[k] = 0.5 * (float(iv.mpf(j0.v).a) + float(iv.mpf(j0.v).b))
        for loc, gi in enumerate(r['vars']):
            A[k, gi] = 0.5 * (float(iv.mpf(j0.g[loc]).a) +
                              float(iv.mpf(j0.g[loc]).b))
        j2 = SL.eval_geo(bx, r, order=2)
        tot = 0.0
        for a in range(len(r['vars'])):
            for b in range(len(r['vars'])):
                tot += M.iv_mag(j2.h[a][b])
        w[k] = tot
    print('row data built (%.1f s)' % (time.time() - t0))

    # per-h alive sets ------------------------------------------------------
    a22_edge = {r: (o, e, p, kk) for (r, o, e, p, kk, _) in edge_rows_a22()}

    _alive_cache = {}

    def alive_mask(h):
        key = round(h, 8)
        if key in _alive_cache:
            return _alive_cache[key]
        bxh = boxes_at(h)
        # a22 edge rows: [V]; walls/aux: always
        ok = np.ones(n, dtype=bool)
        axis_ok = {}
        for k, (tag, c, kind, pr, ax) in enumerate(arsenal):
            if kind == 'a22' and c['kind'] == 'edge':
                t, d = corner_frame(bxh, c['j'], c['edge'], c['i'],
                                    c['corner'])
                ok[k] = (0.5 - M.iv_mag(t) > 0) and (0.5 + inf(d) > 0)
            elif kind in ('branch', 'gained'):
                if ax not in axis_ok:
                    glo, ghi = axis_gap_bounds(bxh, *ax)
                    axis_ok[ax] = ghi > 0        # alive (not killed)
                ok[k] = axis_ok[ax]
        _alive_cache[key] = ok
        return ok

    es = np.zeros(34)
    es[L.S_IDX] = 1.0

    def face_margin(i, sgn, h, mask):
        idx = np.where(mask)[0]
        m = len(idx)
        # vars: omega (m), omega_b   (caps keep the scan LP bounded; the
        # honest loop re-derives caps from the certificate arithmetic)
        Aeq = np.zeros((34, m + 1))
        Aeq[:, :m] = A[idx].T
        ei = np.zeros(34)
        ei[i] = 1.0
        Aeq[:, m] = sgn * ei
        c = np.zeros(m + 1)
        c[:m] = gval[idx] + 0.5 * w[idx] * (RHO * h) ** 2
        c[m] = -h
        res = linprog(c, A_eq=Aeq, b_eq=es,
                      bounds=[(0, 200.0)] * m + [(0, 50.0)],
                      method='highs')
        if not res.success:
            return None, None
        return -res.fun, res.x

    def face_empty(i, sgn, h):
        """(E) emptiness: some globally-valid row has sup < 0 on the face
        sub-box {d_i in sgn*[h, RHO*h]} (rings with ratio RHO).  [IV]"""
        z = SL.z_hat()
        hq = Fraction(h).limit_denominator(10 ** 9)
        ho = hq * Fraction(RHO).limit_denominator(100)
        import t3lib
        bxf = []
        for q in range(34):
            lo = z[q] - ho
            hi = z[q] + ho
            if q == i:
                if sgn > 0:
                    lo = z[q] + hq
                else:
                    hi = z[q] - hq
            bxf.append(iv.mpf([t3lib._to_iv(lo).a, t3lib._to_iv(hi).b]))
        K = SL.load_cert()
        for r, cst in enumerate(K['constraints'][:36]):
            if cst['kind'] != 'wall':
                continue
            rr = SL.to_t3_row(cst)
            v = SL.eval_geo(bxf, rr, order=0).v
            if sup(v) < 0:
                return ('wall_row_%d' % r), -sup(v)
        return None, None

    out = {'meta': {'task': 'A40 ceiling scan', 'rho': RHO,
                    'n_rows': n},
           'faces': []}
    worst = (1e9, None)
    for i in range(34):
        for sgn in (+1, -1):
            if i == L.S_IDX and sgn == +1:
                out['faces'].append({'coord': i, 'sign': sgn,
                                     'h_ceiling': None,
                                     'note': 'trivial face: s >= s-hat + h0'})
                continue
            # (E) emptiness first: wall-backed faces have no feasible points
            erow, emarg = face_empty(i, sgn, 5e-4)
            if erow is not None:
                # find how far emptiness extends
                elo, ehi = 5e-4, 0.2
                for _ in range(18):
                    emid = (elo + ehi) / 2
                    if face_empty(i, sgn, emid)[0] is not None:
                        elo = emid
                    else:
                        ehi = emid
                lab = ('s' if i == 33 else 'sq%d.%s' % (i // 3, 'xyt'[i % 3]))
                out['faces'].append({'coord': i, 'sign': sgn, 'face': lab,
                                     'h_ceiling': elo, 'mode': 'EMPTY',
                                     'empty_row': erow})
                if elo < worst[0]:
                    worst = (elo, (lab, sgn))
                print('  %-8s %+d  h_ceiling = %.5f  (EMPTY via %s)'
                      % (lab, sgn, elo, erow))
                continue
            lo, hi = 5e-4, 0.2
            mlo, _ = face_margin(i, sgn, lo, alive_mask(lo))
            if mlo is None or mlo <= 0:
                hc = 0.0
                sup_rows = []
            else:
                for _ in range(22):
                    mid = (lo + hi) / 2
                    mm, _ = face_margin(i, sgn, mid, alive_mask(mid))
                    if mm is not None and mm > 0:
                        lo = mid
                    else:
                        hi = mid
                    if hi - lo < 1e-4 * lo:
                        break
                hc = lo
                _, x = face_margin(i, sgn, lo, alive_mask(lo))
                idx = np.where(alive_mask(lo))[0]
                sup_rows = [
                    {'tag': arsenal[idx[q]][0], 'omega': float(x[q]),
                     'kind': arsenal[idx[q]][2]}
                    for q in np.argsort(-x[:len(idx)])[:8]
                    if x[q] > 1e-6]
            lab = ('s' if i == 33 else 'sq%d.%s' % (i // 3, 'xyt'[i % 3]))
            out['faces'].append({'coord': i, 'sign': sgn, 'face': lab,
                                 'h_ceiling': hc, 'top_rows': sup_rows})
            if hc < worst[0]:
                worst = (hc, (lab, sgn))
            print('  %-8s %+d  h_ceiling = %.5f' % (lab, sgn, hc))
    out['h_ceiling_min'] = worst[0]
    out['binding_face'] = {'face': worst[1][0], 'sign': worst[1][1]}
    out['meta']['wall_seconds'] = time.time() - t0
    with open(os.path.join(RESULTS, 'ceiling.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('CEILING: min over faces = %.5f at %s%+d   (%.1f s)'
          % (worst[0], worst[1][0], worst[1][1], out['meta']['wall_seconds']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
