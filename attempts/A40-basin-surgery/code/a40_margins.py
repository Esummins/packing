#!/usr/bin/env python
"""a40_margins.py -- A40 Step A: the measurement pass that the surgery lemma
and the growth loop are designed against.  [IV] dps 60 for all interval facts;
[LP] float64 for the design LPs (certified later by the loop itself).

Measured, on box(z-hat, h) for h in a grid up to 0.03:

 M1. Per-row [V] margins of the 16 A22 edge rows (tangential 1/2 - sup|t|,
     depth 1/2 + inf d), plus per-row h_V (bisected zero of the tangential
     margin).  This is the surgery TARGET LIST: a row must be branched at the
     h where its own margin dies, not before.
 M2. Per-contact-pair axis structure: for each of the 8 candidate separating
     axes of each contact pair, the kill margin  max_k(-sup_box g_{axis,k})
     (axis impossible if > 0).  Beyond a row's h_V the surviving-axis set is
     the branch set of the surgery.
 M3. Gained contacts: all 55 pair gaps at z-hat (best-axis SAT gap) and the
     h at which the pair's box-safety margin (max over axes of inf_box gap)
     dies; pairs that can touch inside box(0.03) are listed.  Wall rows are
     globally valid (a packing stays in [0,s]^2), so only pairs appear here.
 M4. Face growth rates: for each of the 68 faces +-e_i of the box, the
     Charnes-Cooper LP
         h_sat(face) = max { omega_b / (0.5 w.omega) :
                             A(z-hat)^T omega = e_s -+ omega_b e_i,
                             omega >= 0 on universal valid rows }
     with w = interval Hessian masses at h = 0.03.  This is the thin-ring
     saturation radius of the anchor certificate in that face direction
     (see notes/theory.md, Lemma S5): rings can grow while h < h_sat(face).
     Also reported: omega_b at the Hbar-cheap optimum, and the binding face.

Output: results/margins.json
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

import a36_lib as L                       # noqa: E402
import strata_lib as SL                   # noqa: E402
import m2_lib as M                        # noqa: E402
import t3lib                              # noqa: E402

iv.dps = 60
HALF = M.HALF
NHAT = M.NHAT
NSQ = 11


def sup(x):
    return math.nextafter(float(iv.mpf(x).b), math.inf)


def inf(x):
    return -math.nextafter(float((-iv.mpf(x)).b), math.inf)


def corner_frame(box, o, e, p, k):
    """(t, d) of corner k of square p in owner o's edge-e frame.  [IV]"""
    hx = t3lib._to_iv(HALF[k][0])
    hy = t3lib._to_iv(HALF[k][1])
    cp, sp = iv.cos(box[3 * p + 2]), iv.sin(box[3 * p + 2])
    qx = box[3 * p] + (cp * hx - sp * hy)
    qy = box[3 * p + 1] + (sp * hx + cp * hy)
    nhx, nhy = NHAT[e]
    co, so = iv.cos(box[3 * o + 2]), iv.sin(box[3 * o + 2])
    nx = co * iv.mpf(nhx) - so * iv.mpf(nhy)
    ny = so * iv.mpf(nhx) + co * iv.mpf(nhy)
    wx, wy = qx - box[3 * o], qy - box[3 * o + 1]
    t = -ny * wx + nx * wy
    d = nx * wx + ny * wy - iv.mpf(1) / 2
    return t, d


def axis_gap(box, o, e, p):
    """sup and inf over the box of the axis gap  min_k d_k.  [IV]"""
    lo, hi = 1e9, 1e9
    for k in range(4):
        _, d = corner_frame(box, o, e, p, k)
        lo = min(lo, inf(d))
        hi = min(hi, sup(d))
    return lo, hi        # inf_box gap >= lo ... careful: this is min_k bounds


def axis_gap_bounds(box, o, e, p):
    """[lo, hi] enclosure of gap = min_k d_k over the box."""
    los, his = [], []
    for k in range(4):
        _, d = corner_frame(box, o, e, p, k)
        los.append(inf(d))
        his.append(sup(d))
    return min(los), min(his)


PAIR_AXES = [(o, e, p) for o in range(NSQ) for p in range(NSQ) if o != p
             for e in range(4)]


def pair_axes(i, j):
    return ([(i, e, j) for e in range(4)] + [(j, e, i) for e in range(4)])


def edge_rows_a22():
    K = SL.load_cert()
    out = []
    for r, c in enumerate(K['constraints'][:36]):
        if c['kind'] == 'edge':
            out.append((r, c['j'], c['edge'], c['i'], c['corner'],
                        c.get('name', 'row%d' % r)))
    return out


def row_V_margins(box, o, e, p, k):
    t, d = corner_frame(box, o, e, p, k)
    return 0.5 - M.iv_mag(t), 0.5 + inf(d)


def bisect_zero(f, lo, hi, iters=40, tol=1e-7):
    """largest x in [lo,hi] with f(x) > 0 (f decreasing-ish)."""
    if f(hi) > 0:
        return hi, False
    assert f(lo) > 0
    for _ in range(iters):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol * max(lo, 1e-9):
            break
    return lo, True


def boxes_at(h):
    return M.box_around(SL.z_hat(), Fraction(h).limit_denominator(10 ** 9))


def main():
    t0 = time.time()
    os.makedirs(RESULTS, exist_ok=True)
    out = {'meta': {'task': 'A40 margins pass', 'dps': 60,
                    'h_grid': [0.005, 0.01, 0.02, 0.03]}}

    # ---------------- M1: per-row [V] margins + h_V
    rows = edge_rows_a22()
    pb = SL.point_box()
    m1 = []
    for (ridx, o, e, p, k, nm) in rows:
        t, d = corner_frame(pb, o, e, p, k)
        tz = 0.5 * (float(iv.mpf(t).a) + float(iv.mpf(t).b))
        rec = {'row': ridx, 'name': nm, 'owner': o, 'edge': e, 'other': p,
               'corner': k, 't_zhat': tz, 'abs_t_zhat': abs(tz),
               'margins': {}}
        for h in out['meta']['h_grid']:
            bx = boxes_at(h)
            mt, md = row_V_margins(bx, o, e, p, k)
            rec['margins'][str(h)] = {'tangential': mt, 'depth': md}

        def f(h):
            mt, md = row_V_margins(boxes_at(h), o, e, p, k)
            return min(mt, md)
        hv, capped = bisect_zero(f, 1e-4, 0.06)
        rec['h_V'] = hv
        rec['h_V_capped_at_0.06'] = not capped
        m1.append(rec)
    m1.sort(key=lambda r: r['h_V'])
    out['M1_row_validity'] = m1
    print('M1: per-row h_V (sorted):')
    for r in m1:
        print('  row %-2d %-12s |t|=%.4f  h_V=%.5f%s'
              % (r['row'], r['name'], r['abs_t_zhat'], r['h_V'],
                 ' (>=0.06)' if r['h_V_capped_at_0.06'] else ''))

    # ---------------- M2: axis structure of every contact pair
    pairs = sorted({tuple(sorted((o, p))) for (_, o, _, p, _, _) in rows}
                   | {(0, 1), (0, 3), (1, 3)})
    m2 = []
    for (i, j) in pairs:
        rec = {'pair': [i, j], 'axes': []}
        for (o, e, p) in pair_axes(i, j):
            arec = {'owner': o, 'edge': e, 'other': p, 'per_h': {}}
            for h in out['meta']['h_grid']:
                bx = boxes_at(h)
                glo, ghi = axis_gap_bounds(bx, o, e, p)
                # killed if sup gap < 0; kill margin = -ghi
                arec['per_h'][str(h)] = {'gap_sup': ghi, 'gap_inf': glo,
                                         'killed': bool(ghi < 0)}
            arec['gap_zhat'] = axis_gap_bounds(SL.point_box(), o, e, p)[1]
            rec['axes'].append(arec)
        for h in out['meta']['h_grid']:
            rec['n_alive_%s' % h] = sum(
                0 if a['per_h'][str(h)]['killed'] else 1
                for a in rec['axes'])
        m2.append(rec)
        print('M2: pair (%d,%d) alive axes: ' % (i, j)
              + '  '.join('h=%s:%d' % (h, rec['n_alive_%s' % h])
                          for h in out['meta']['h_grid']))
    out['M2_pair_axis_structure'] = m2

    # ---------------- M3: gained contacts
    m3 = []
    for i in range(NSQ):
        for j in range(i + 1, NSQ):
            if (i, j) in pairs:
                continue
            gz = max(axis_gap_bounds(pb, o, e, p)[0]
                     for (o, e, p) in pair_axes(i, j))
            if gz > 0.30:
                continue
            rec = {'pair': [i, j], 'gap_zhat': gz, 'safe_margin': {}}
            for h in out['meta']['h_grid']:
                bx = boxes_at(h)
                rec['safe_margin'][str(h)] = max(
                    axis_gap_bounds(bx, o, e, p)[0]
                    for (o, e, p) in pair_axes(i, j))
            m3.append(rec)
    m3.sort(key=lambda r: r['gap_zhat'])
    out['M3_gained_pairs'] = m3
    print('M3: near pairs (gap at z-hat < 0.30):')
    for r in m3:
        print('  (%d,%d) gap=%.4f  safe@0.01=%.4f safe@0.02=%.4f '
              'safe@0.03=%.4f'
              % (r['pair'][0], r['pair'][1], r['gap_zhat'],
                 r['safe_margin']['0.01'], r['safe_margin']['0.02'],
                 r['safe_margin']['0.03']))

    # ---------------- M4: face growth-rate LPs (Charnes-Cooper)
    mid, _ = L.v3_jacobian()
    w = L.row_hessian_mass(Fraction(3, 100))
    RV = sorted(set(range(36)) | set(L.AUX_POS))
    A = mid[RV]                       # nrows x 34
    wv = w[RV]
    nr = len(RV)
    es = np.zeros(34)
    es[L.S_IDX] = 1.0
    m4 = []
    for i in range(34):
        for sgn in (+1, -1):
            # vars: y (nr), b, tau ; A^T y = tau e_s - sgn*b e_i ;
            # 0.5 w.y = 1 ; maximize b
            neq = 34 + 1
            Aeq = np.zeros((neq, nr + 2))
            beq = np.zeros(neq)
            Aeq[:34, :nr] = A.T
            Aeq[:34, nr] = sgn * es * 0  # placeholder
            ei = np.zeros(34)
            ei[i] = 1.0
            Aeq[:34, nr] = sgn * ei      # + b*sgn*e_i  moved to LHS
            Aeq[:34, nr + 1] = -es
            Aeq[34, :nr] = 0.5 * wv
            beq[34] = 1.0
            c = np.zeros(nr + 2)
            c[nr] = -1.0
            bounds = [(0, None)] * nr + [(0, None), (0, None)]
            res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=bounds,
                          method='highs')
            hsat = float(res.x[nr]) if res.success else 0.0
            m4.append({'coord': i, 'sign': sgn, 'h_sat': hsat,
                       'lp_ok': bool(res.success)})
    m4s = sorted(m4, key=lambda r: r['h_sat'])
    out['M4_face_growth'] = m4
    out['M4_binding_faces'] = m4s[:8]
    print('M4: face thin-ring saturation h_sat (worst 8):')
    for r in m4s[:8]:
        i = r['coord']
        lab = ('s' if i == 33 else
               'sq%d.%s' % (i // 3, 'xyt'[i % 3]))
        print('  %-8s %+d  h_sat=%.5f  ok=%s'
              % (lab, r['sign'], r['h_sat'], r['lp_ok']))
    print('M4: min h_sat = %.5f, max = %.5f'
          % (m4s[0]['h_sat'], m4s[-1]['h_sat']))

    out['meta']['wall_seconds'] = time.time() - t0
    with open(os.path.join(RESULTS, 'margins.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print('%.1f s -> results/margins.json' % out['meta']['wall_seconds'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
