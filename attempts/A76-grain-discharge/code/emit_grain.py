#!/usr/bin/env python3
"""emit_grain.py -- emit grain-certificate-v1 files (checked by certs/verify_grain.py).

For a pin set P (Trump-frame square indices) and a box (rc, rt, rs):
  * the row universe: A22's 42 rows (t-version), the flush-upright / corner-corner rows of
    the pairs (0,1), (0,3), (1,3), the pin rows of P;
  * [PA] the possibly-active contact rows on the box (computed the same way the checker does);
  * [K]  the pinned Krawczyk system (pins + an independent completion from A22's S) with Y =
         rational rounding of the float inverse Jacobian;
  * [D1] optional: drain-flex certificates for the listed grains (independent row sets).
Usage: python emit_grain.py OUT.json --pins 0,1,3,5 --rc 1/100 --rt 1/500 [--rs 1/100]
                            [--d1 codim1] [--no-pa] [--k-only-unpinned]
"""
import sys
import json
import argparse
import numpy as np
from fractions import Fraction as F
from grainlib import *
from explore1 import square_system

UPRIGHT_ROWS = ['E1c0-0e1', 'E1c3-0e1', 'E0c1-1e3', 'E0c2-1e3', 'E3c0-0e2', 'E3c1-0e2',
                'E0c2-3e0', 'E0c3-3e0', 'E1c3-3e1', 'E3c1-1e2', 'E1c3-3e0', 'E3c1-1e3']


def parse_edge(name):
    i = int(name[1:name.index('c')]); k = int(name[name.index('c') + 1:name.index('-')])
    j = int(name[name.index('-') + 1:name.index('e')]); e = int(name[name.index('e') + 1:])
    return {'kind': 'edge', 'i': i, 'corner': k, 'j': j, 'edge': e}


def rat_matrix(M, denom=10 ** 40):
    return [['%d/%d' % (F(int(round(float(v) * denom)), denom).numerator,
                        F(int(round(float(v) * denom)), denom).denominator) for v in row] for row in M]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--pins', default='0,1,3,5')
    ap.add_argument('--rc', default='1/100')
    ap.add_argument('--rt', default='1/500')
    ap.add_argument('--rs', default=None)
    ap.add_argument('--d1', default='')
    ap.add_argument('--no-pa', action='store_true')
    ap.add_argument('--desc', default='')
    args = ap.parse_args()
    pins = [int(x) for x in args.pins.split(',')] if args.pins else []
    rc, rt = F(args.rc), F(args.rt)
    rs = F(args.rs) if args.rs else rc
    rad = radii(rc, rt, rs)
    z0 = load_z0()
    z0f = to_float_z(z0)
    rows22, d22 = a22_rows()
    universe = list(rows22) + [parse_edge(n) for n in UPRIGHT_ROWS] + pin_rows(pins)
    name_to_idx = {row_name(c): i for i, c in enumerate(universe)}
    B = box(z0, rad)
    cert = {'format': 'grain-certificate-v1',
            'description': args.desc or ('A76 grain certificate, Trump frame, pins %s, box (rc,rt,rs)=(%s,%s,%s)'
                                         % (pins, rc, rt, rs)),
            'z0': [fstr(x) for x in z0],
            'box': {'rc': fstr(rc), 'rt': fstr(rt), 'rs': fstr(rs), 'radii': [fstr(r) for r in rad]},
            'pins': pins,
            'rows': universe,
            'active_at_z0': list(range(len(universe))),
            'claims': {'centre_residual_max': '1/' + str(10 ** 55)},
            'krawczyk': [], 'd1': []}
    # sanity: residuals
    zc = [IV.point(x) for x in z0]
    mx = max(eval_row(zc, c).mag() for c in universe)
    print('max centre residual over universe: %.3e' % float(mx))
    # PA
    if not args.no_pa:
        pa = []
        for c in all_candidate_rows():
            v = eval_row(B, c)
            if not (v.lo <= 0 <= v.hi):
                continue
            if c['kind'] == 'edge':
                dep, tg = edge_aux(B, c)
                if tg.hi < F(-1, 2) or tg.lo > F(1, 2):
                    continue
            pa.append(row_name(c))
        cert['pa'] = {'rows': pa,
                      'claim': 'every corner-wall / corner-edge contact row that can be active on the box is listed'}
        newr = [n for n in pa if n not in name_to_idx]
        print('PA: %d rows, %d not in the Trump universe: %s' % (len(pa), len(newr), newr))
        cert['pa']['new_rows'] = newr
    # K: pinned basis
    prefer = list(range(len(rows22) + len(UPRIGHT_ROWS), len(universe))) + list(d22['S'])
    sel = square_system(universe, prefer, z0f)
    sub = [universe[k] for k in sel]
    A = grad_matrix_float(z0f, sub)
    Yf = np.linalg.inv(A)
    Y = rationalize_matrix(Yf, 10 ** 40)
    ok, w = krawczyk(z0, rad, sub, Y)
    print('K (pins %s): rows %d, contracts=%s ratio=%.4f' % (pins, len(sel), ok, float(w)))
    cert['krawczyk'].append({'id': 'pinned-basis', 'rows': sel, 'Y': rat_matrix(Yf),
                             'row_names': [row_name(c) for c in sub],
                             'claim_ratio': float(w)})
    # D1 certificates
    if args.d1 == 'codim1':
        n_ok = 0
        for kk in range(len(sub)):
            if sub[kk]['kind'] in ('pinx', 'piny', 'pint'):
                continue
            rowsA = sub[:kk] + sub[kk + 1:]
            M = grad_matrix_float(z0f, rowsA + [{'kind': 'es'}])
            if np.linalg.matrix_rank(M, tol=1e-9) < M.shape[0]:
                continue
            Yp = np.linalg.pinv(M)
            Ypr = [[F(int(round(v * 10 ** 30)), 10 ** 30) for v in row] for row in Yp]
            # exact ratio
            Mrows = rowsA + [{'kind': 'es'}]
            Jb = [grad_row(B, c) for c in Mrows]
            m = len(Mrows)
            worst = F(0)
            for i in range(m):
                rowsum = F(0)
                for j in range(m):
                    acc = IZERO
                    for col, v in Jb[i].items():
                        if Ypr[col][j] != 0:
                            acc = acc + v * Ypr[col][j]
                    rowsum += (acc - (IONE if i == j else IZERO)).mag()
                worst = max(worst, rowsum)
            idx = [sel[t] for t in range(len(sub)) if t != kk]
            entry = {'id': 'codim1-drop-%s' % row_name(sub[kk]), 'rows': idx,
                     'Y': rat_matrix(Yp, 10 ** 30), 'claim_ratio': float(worst)}
            if worst < 1:
                cert['d1'].append(entry)
                n_ok += 1
            print('  D1 drop %-14s ratio %.3f %s' % (row_name(sub[kk]), float(worst), 'OK' if worst < 1 else 'FAIL(not emitted)'))
        print('D1 codim-1 certificates emitted: %d' % n_ok)
    json.dump(cert, open(args.out, 'w'))
    print('wrote', args.out)


if __name__ == '__main__':
    main()
