#!/usr/bin/env python
"""a36_l1.py -- A36 Task 2: the L1 interval checks on box(z-hat, h).  [IV]

What is certified, per levers.md L1.4:

 (i) KILLED AXES.  For each of the 16 (owner, edge, other) combinations that
     L1.2 declares impossible, exhibit a CORNER k with
         sup_{box(h)}  g_{e,k}(z) = n_e(theta_o).(q_k(p) - c_o) - 1/2  <  0.
     Since the TRUE axis gap is  gap_e(z) = min_k g_{e,k}(z) <= g_{e,k}(z),
     one such corner certifies gap_e < 0 on the whole box, i.e. that axis
     cannot separate the pair anywhere in box(h).  The reported margin is
         kill_margin = max_k ( -sup_box g_{e,k} )  > 0.
     (This single test subsumes both L1.4(i) projection overlaps and L1.4(ii)
     centre orders: a strictly negative one-corner support already forbids the
     axis.  The centre-order quantities are reported alongside as diagnostics.)

 (ii) A22 ROWS 0..35 SAT-selection validity on box(h): tangential margin
      1/2 - sup|tangential| > 0 and depth margin 1/2 + inf(depth) > 0.

 (iii) the two aux rows are ACTIVE at z-hat (|g| <= 1e-40), and the two NEW v3
       rows B13x', B13y' evaluate to 0 at z-hat within 1e-59.

Since 8 of the 24 (axis) combinations survive, and separating-axis
completeness for convex polygons says at least one of the 8 per pair must
separate a feasible (interior-disjoint) pair, L1's disjunction follows:
   (A01a or A01b) and (A03a or A03b) and (B13x or B13x' or B13y or B13y').

Output: results/a36_l1.json
"""
import json
import math
import os
import sys
from fractions import Fraction

from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import a36_lib as L                       # noqa: E402
import strata_lib as SL                   # noqa: E402
import m2_lib as M                        # noqa: E402
import t3lib                              # noqa: E402

iv.dps = 60
HALF = M.HALF
NHAT = M.NHAT


def sup(x):
    return math.nextafter(float(iv.mpf(x).b), math.inf)


def inf(x):
    return -math.nextafter(float((-iv.mpf(x)).b), math.inf)


def sep_value_iv(box, o, e, p, k):
    """n_e(theta_o).(q_k(p) - c_o) - 1/2 over the box."""
    hx, hy = iv.mpf(HALF[k][0].numerator) / 2 * 0, None  # placeholder
    hx = t3lib._to_iv(HALF[k][0])
    hy = t3lib._to_iv(HALF[k][1])
    cp, sp = iv.cos(box[3 * p + 2]), iv.sin(box[3 * p + 2])
    qx = box[3 * p] + (cp * hx - sp * hy)
    qy = box[3 * p + 1] + (sp * hx + cp * hy)
    nhx, nhy = NHAT[e]
    co, so = iv.cos(box[3 * o + 2]), iv.sin(box[3 * o + 2])
    nx = co * iv.mpf(nhx) - so * iv.mpf(nhy)
    ny = so * iv.mpf(nhx) + co * iv.mpf(nhy)
    return nx * (qx - box[3 * o]) + ny * (qy - box[3 * o + 1]) - iv.mpf(1) / 2


def killed_axis_check(box):
    out = []
    ok = True
    worst = 1e9
    for lab, o, e, p in L.KILLED_AXES:
        best_k, best_m = None, -1e9
        for k in range(4):
            m = -sup(sep_value_iv(box, o, e, p, k))
            if m > best_m:
                best_m, best_k = m, k
        out.append({'pair': lab, 'owner': o, 'edge': e, 'other': p,
                    'witness_corner': best_k, 'kill_margin': best_m})
        ok = ok and best_m > 0.0
        worst = min(worst, best_m)
    return ok, worst, out


def centre_orders(box):
    """Diagnostic centre-order bounds used in L1.2's prose."""
    def cx(i):
        return box[3 * i]

    def cy(i):
        return box[3 * i + 1]
    return {
        'c1x-c0x_inf': inf(cx(1) - cx(0)),
        'c3y-c0y_inf': inf(cy(3) - cy(0)),
        'c1x-c3x_inf': inf(cx(1) - cx(3)),
        'c3y-c1y_inf': inf(cy(3) - cy(1)),
        'y-overlap(0,1)_inf': inf(iv.mpf(1) - abs(cy(1) - cy(0))),
        'x-overlap(0,3)_inf': inf(iv.mpf(1) - abs(cx(3) - cx(0))),
    }


def a22_row_margins(box):
    """Tangential / depth margins of A22 rows 0..35 over the box."""
    cons = SL.load_cert()['constraints'][:36]
    wt, wd = 1e9, 1e9
    for c in cons:
        if c['kind'] != 'edge':
            continue
        i, j = c['i'], c['j']
        hx = t3lib._to_iv(HALF[c['corner']][0])
        hy = t3lib._to_iv(HALF[c['corner']][1])
        ci, si = iv.cos(box[3 * i + 2]), iv.sin(box[3 * i + 2])
        qx = box[3 * i] + (ci * hx - si * hy)
        qy = box[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = NHAT[c['edge']]
        cj, sj = iv.cos(box[3 * j + 2]), iv.sin(box[3 * j + 2])
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        wx, wy = qx - box[3 * j], qy - box[3 * j + 1]
        wt = min(wt, 0.5 - M.iv_mag(-ny * wx + nx * wy))
        wd = min(wd, 0.5 + inf(nx * wx + ny * wy))
    return wt, wd


def branch_corner_margins(box):
    """For every branch axis, the tangential margin of its 4 corner rows -- a
    REPORTED number only (the barrier does not use dominance; L1.1)."""
    out = {}
    for ax, (nm, o, e, p, kc, base) in enumerate(L.AXES):
        worst = 1e9
        for k in range(4):
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
            worst = min(worst, 0.5 - M.iv_mag(-ny * wx + nx * wy))
        out[nm] = worst
    return out


def run_at(h):
    box = M.box_around(SL.z_hat(), h)
    kok, kworst, kdet = killed_axis_check(box)
    wt, wd = a22_row_margins(box)
    ent = {
        'h': M.fs(h), 'h_float': float(h),
        'killed_axes_ok': bool(kok),
        'kill_margin_min': kworst,
        'killed_axes': kdet,
        'a22_tangential_margin': wt,
        'a22_depth_margin': wd,
        'a22_rows_ok': bool(wt > 0 and wd > 0),
        'centre_orders': centre_orders(box),
        'branch_corner_tangential_margin_REPORTED': branch_corner_margins(box),
    }
    ent['all_L1_ok'] = bool(ent['killed_axes_ok'] and ent['a22_rows_ok'])
    return ent


def zhat_facts():
    pb = SL.point_box()
    rows = L.v3_rows()
    vals = {L.v3_names()[k]: M.iv_mag(SL.eval_geo(pb, rows[k], order=0).v)
            for k in (42, 43, 44, 45)}
    active = [k for k in range(L.NEXT3)
              if M.iv_mag(SL.eval_geo(pb, rows[k], order=0).v) < 1e-40]
    return {'new_row_values_at_zhat': vals,
            'new_rows_zero_within_1e-59': all(v < 1e-59 for k, v in
                                              vals.items()),
            'aux_active_within_1e-40': all(vals[n] < 1e-40
                                           for n in ('D0-1', 'D0-3')),
            'active_positions': active, 'n_active': len(active)}


def main():
    grid = [Fraction(8, 10000), Fraction(5, 10000), Fraction(1, 1000),
            Fraction(16, 10000), Fraction(25, 10000),
            Fraction(3779, 1000000), Fraction(3689, 1000000)]
    grid = sorted(set(grid))
    out = {'meta': {'task': 'A36 L1 interval checks', 'dps': 60,
                    'r_N': M.fs(L.R_N)},
           'zhat': zhat_facts(), 'grid': []}
    for h in grid:
        e = run_at(h)
        print('h = %-12s killed_ok=%s (min margin %.6f)  a22 tan=%.6f dep=%.6f'
              '  ALL=%s' % (e['h_float'], e['killed_axes_ok'],
                            e['kill_margin_min'], e['a22_tangential_margin'],
                            e['a22_depth_margin'], e['all_L1_ok']))
        out['grid'].append(e)
    # bisect the max h at which all L1 checks pass
    lo, hi = Fraction(1, 10000), Fraction(1, 2)
    assert run_at(lo)['all_L1_ok']
    for _ in range(40):
        mid = (lo + hi) / 2
        if run_at(mid)['all_L1_ok']:
            lo = mid
        else:
            hi = mid
        if float(hi - lo) < 1e-9:
            break
    out['h_L1_max'] = float(lo)
    out['h_L1_max_frac'] = M.fs(lo)
    e = run_at(lo)
    out['h_L1_max_detail'] = {k: e[k] for k in
                              ('kill_margin_min', 'a22_tangential_margin',
                               'a22_depth_margin')}
    # which check binds just above
    e2 = run_at(lo * Fraction(1001, 1000))
    out['binding_at_h_L1_max'] = ('a22 rows 0..35 tangential/depth'
                                  if not e2['a22_rows_ok'] else 'killed axes')
    print('h_L1_max = %.6g  (binding: %s)' % (out['h_L1_max'],
                                              out['binding_at_h_L1_max']))
    os.makedirs(L.RESULTS, exist_ok=True)
    with open(os.path.join(L.RESULTS, 'a36_l1.json'), 'w') as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
