"""m2_empty.py -- A35 / M2 Task 2: (E) EMPTY-STRATUM certificates.

theory.md T0.2-(E).  M1 found 143 break sets B that are cone-alive but whose
closed stratum is locally EMPTY (rank(A_M) = 34 at z-hat).  For each of them we
certify, by Krawczyk isolation of a retained 34-row nonsingular square subsystem
F_B over box(z-hat, h),

        Sbar(B)  cap  box(z-hat, h)  =  { z-hat } ,

because any z in Sbar(B) has g_m(z) = 0 for every retained row m, in particular
for the 34 rows of the chosen subsystem, and Krawczyk uniqueness says F_B has
exactly one zero in the box -- which is z-hat (g_k(z-hat) = 0 for all 38 rows).
h is doubled from r_N = 1/2000 until contraction fails; the last success is the
certified reach h_max.  Everything is mpmath.iv [IV] (the preconditioner is a
rationalised float inverse -- a preconditioner needs no certification, only the
contraction test does).

SELECTION CAVEAT.  The 16 'edge' rows are SAT surrogates for a fixed axis/corner
selection; they are valid descriptions of the physical contact only while
|tangential| < 1/2 and depth > -1/2.  That margin is a property of the box, not
of B, and is measured once by bisection (h_valid).  We report h_max (algebraic)
and h_eff = min(h_max, h_valid) (physical).

Outputs results/m2_empty.json, checkpointed every 10 strata.
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from mpmath import iv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m2_lib as M  # noqa: E402
import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60

YDEN = 10 ** 20


def rational_Y(Amid):
    Yf = np.linalg.inv(Amid)
    return [[Fraction(round(Fraction(float(v)) * YDEN), YDEN) for v in row]
            for row in Yf]


def edge_valid(box):
    for c in M.cons():
        if c['kind'] != 'edge':
            continue
        i, j = c['i'], c['j']
        hx = t3lib._hiv(M.HALF[c['corner']][0])
        hy = t3lib._hiv(M.HALF[c['corner']][1])
        ci, si = iv.cos(box[3 * i + 2]), iv.sin(box[3 * i + 2])
        qx = box[3 * i] + (ci * hx - si * hy)
        qy = box[3 * i + 1] + (si * hx + ci * hy)
        nhx, nhy = M.NHAT[c['edge']]
        cj, sj = iv.cos(box[3 * j + 2]), iv.sin(box[3 * j + 2])
        nx = cj * iv.mpf(nhx) - sj * iv.mpf(nhy)
        ny = sj * iv.mpf(nhx) + cj * iv.mpf(nhy)
        wx, wy = qx - box[3 * j], qy - box[3 * j + 1]
        if 0.5 - M.iv_mag(-ny * wx + nx * wy) <= 0:
            return False
        if float((nx * wx + ny * wy).a) <= -0.5:
            return False
    return True


def find_h_valid(zh):
    lo, hi = Fraction(1, 2000), Fraction(1, 100)
    assert edge_valid(M.box_around(zh, lo))
    assert not edge_valid(M.box_around(zh, hi))
    for _ in range(14):
        mid = (lo + hi) / 2
        if edge_valid(M.box_around(zh, mid)):
            lo = mid
        else:
            hi = mid
    return lo


def main():
    t0 = time.time()
    zh = SL.z_hat()
    _, Amid, Arad, _ = SL.jacobian()
    names = M.row_names()
    Bs = M.empty_alive()
    rN = M.a22_rN()

    h_valid = find_h_valid(zh)
    print('edge-selection validity radius (bisection, [IV]): %s = %.5g'
          % (M.fs(h_valid), float(h_valid)))

    out = {
        'meta': {
            'task': 'A35/M2 Task 2 -- (E) empty-stratum Krawczyk isolation '
                    'certificates for the 143 cone-alive-but-empty break sets',
            'n_strata': len(Bs),
            'method': '[IV] mpmath.iv dps 60 Krawczyk on a retained 34-row '
                      'nonsingular subsystem, box(z-hat, h), h doubling from '
                      'r_N = 1/2000 (and halving if r_N itself fails); '
                      'preconditioner = rationalised float64 inverse of the '
                      'midpoint Jacobian (denominator 1e20).',
            'conclusion_form': 'Sbar(B) cap box(z-hat, h_max) = {z-hat}',
            'h_valid_edge_selection': M.fs(h_valid),
            'h_valid_edge_selection_float': float(h_valid),
            'row_names': names,
        },
        'strata': [],
    }

    path = os.path.join(M.RESULTS, 'm2_empty.json')

    def flush():
        with open(path, 'w') as f:
            json.dump(out, f, indent=1)

    for idx, B in enumerate(Bs):
        ts = time.time()
        Mrows = [k for k in range(SL.NGEO) if k not in set(B)]
        basis = M.pick_basis(Mrows, Amid)
        Yq = rational_Y(Amid[basis])
        # scan h
        h = rN
        best = None
        trace = []
        res = M.krawczyk_iv(zh, h, basis, Yq)
        trace.append((M.fs(h), res['ok'], res['beta'], res['radK']))
        if res['ok']:
            best = (h, res)
            while True:
                h2 = h * 2
                if h2 > Fraction(1, 2):
                    break
                r2 = M.krawczyk_iv(zh, h2, basis, Yq)
                trace.append((M.fs(h2), r2['ok'], r2['beta'], r2['radK']))
                if not r2['ok']:
                    break
                h, best = h2, (h2, r2)
        else:
            while h > Fraction(1, 10 ** 7):
                h = h / 2
                r2 = M.krawczyk_iv(zh, h, basis, Yq)
                trace.append((M.fs(h), r2['ok'], r2['beta'], r2['radK']))
                if r2['ok']:
                    best = (h, r2)
                    break
        # refine between h_max and 2*h_max: [RFP] bisection, [IV] confirmation
        if best is not None:
            lo, hi = best[0], best[0] * 2
            for _ in range(6):
                mid = (lo + hi) / 2
                if M.krawczyk_rfp(zh, mid, basis, Y=None)['ok']:
                    lo = mid
                else:
                    hi = mid
            if lo > best[0]:
                rc = M.krawczyk_iv(zh, lo, basis, Yq)
                if rc['ok']:
                    best = (lo, rc)
                    trace.append((M.fs(lo), True, rc['beta'], rc['radK']))
        dt = time.time() - ts
        if best is None:
            ent = {'B': list(B), 'B_names': [names[k] for k in B],
                   'certified': False, 'h_max': None, 'secs': dt,
                   'trace': trace}
        else:
            hm, rr = best
            heff = min(hm, h_valid)
            ent = {'B': list(B), 'B_names': [names[k] for k in B],
                   'certified': True,
                   'h_max': M.fs(hm), 'h_max_float': float(hm),
                   'h_max_over_rN': float(hm / rN),
                   'h_eff': M.fs(heff), 'h_eff_float': float(heff),
                   'beta': rr['beta'], 'radK': rr['radK'],
                   'kappa': rr['kappa'], 'margin': rr['margin'],
                   'basis_rows': basis,
                   'doublings_from_rN': float(np.log2(float(hm / rN))),
                   'secs': dt, 'trace': trace}
        out['strata'].append(ent)
        if idx % 10 == 0 or idx == len(Bs) - 1:
            flush()
            print('  [%3d/%3d] B=%-22s h_max=%-10s beta=%.4f %.2fs'
                  % (idx + 1, len(Bs), str(list(B)),
                     ent.get('h_max'), ent.get('beta', float('nan')), dt))

    hs = [e['h_max_float'] for e in out['strata'] if e['certified']]
    dts = [e['secs'] for e in out['strata']]
    import collections
    hist = collections.Counter(e['h_max'] for e in out['strata']
                               if e['certified'])
    out['summary'] = {
        'n_certified': len(hs), 'n_failed': len(Bs) - len(hs),
        'h_max_min': min(hs), 'h_max_median': float(np.median(hs)),
        'h_max_max': max(hs),
        'h_max_histogram': dict(sorted(hist.items(),
                                       key=lambda kv: -float(Fraction(
                                           *map(int, kv[0].split('/')))))),
        'h_max_over_rN_min': min(hs) / float(rN),
        'h_max_over_rN_max': max(hs) / float(rN),
        'secs_median': float(np.median(dts)), 'secs_max': max(dts),
        'secs_total': sum(dts),
        'note': ('h_eff = min(h_max, h_valid) with h_valid = %.5g is the '
                 'radius over which the edge-row SAT selection is also '
                 'certified; every h_max at or above it is capped there for '
                 'the physical statement.' % float(h_valid)),
    }
    out['meta']['runtime_secs'] = time.time() - t0
    flush()
    print(json.dumps(out['summary'], indent=1))
    print('->', path)


if __name__ == '__main__':
    main()
