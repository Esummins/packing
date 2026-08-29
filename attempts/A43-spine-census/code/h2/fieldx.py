#!/usr/bin/env python3
"""A43-H2 wrapper around A38/A39 fieldcut: the W1 tight-variety cut (C3).

Field preference per the H2 brief: the A39 RESEALED field at s0 if it is present
and its standalone verification report says PASS with 0 witnesses; else the A33
sealed field.  Everything downstream uses THR = 1 + eta as an exact Fraction.
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F

REPO = r'C:\Users\esumm\code\packing'
sys.path.insert(0, os.path.join(REPO, 'attempts', 'A38-root-power', 'code'))
import fieldcut as FC                                          # noqa: E402

A39_CERT = os.path.join(REPO, 'attempts', 'A39-early-cert', 'results', 'p2b',
                        'certs', 'A39_measure_feasible_3.877084.json')
A39_REPORT = A39_CERT.replace('.json', '.report.json')
A33_CERT = FC.CERT_PATH

S0 = F(969271, 250000)


def choose_field():
    """(Field, meta dict).  Raises if neither field is usable."""
    if os.path.exists(A39_CERT) and os.path.exists(A39_REPORT):
        rep = json.load(open(A39_REPORT))
        if rep.get('result') == 'PASS' and rep.get('stats', {}).get('witnesses', 1) == 0:
            d = json.load(open(A39_CERT))
            s = F(str(d['s']))
            tot = sum(F(str(w)) for w in d['weights'])
            ok = (s == S0 and tot == F(str(rep['total'])))
            if ok:
                old = FC.TOTAL
                FC.TOTAL = tot
                try:
                    f = FC.Field(A39_CERT)
                finally:
                    FC.TOTAL = old
                eta = tot - 11
                return f, dict(field='A39-resealed', path=A39_CERT,
                               total=str(tot), eta=str(eta), eta_float=float(eta),
                               thr=str(1 + eta), thr_float=float(1 + eta),
                               d4_closed=bool(f.d4_closed), d4_defects=f.d4_defects,
                               n_atoms=f.n, verify='standalone PASS (report '
                               'result=PASS, witnesses=0, margin=%s, depth=%s)'
                               % (rep.get('margin'), rep.get('depth')))
    f = FC.Field(A33_CERT)
    eta = FC.ETA_CERT
    return f, dict(field='A33-sealed', path=A33_CERT, total=str(FC.TOTAL),
                   eta=str(eta), eta_float=float(eta), thr=str(FC.THR_CERT),
                   thr_float=float(FC.THR_CERT), d4_closed=bool(f.d4_closed),
                   d4_defects=f.d4_defects, n_atoms=f.n,
                   verify='A33 seal (fallback)')


_F = None
_M = None


def get():
    global _F, _M
    if _F is None:
        _F, _M = choose_field()
    return _F, _M


def mlow(t0, t1, x0, x1, y0, y1):
    f, _ = get()
    return FC.mlow_box(t0, t1, x0, x1, y0, y1, fld=f)


def mlow_exact(t0, t1, x0, x1, y0, y1):
    f, _ = get()
    return FC.mlow_box_exact(t0, t1, x0, x1, y0, y1, fld=f)


def coverage_at(t, cx, cy):
    f, _ = get()
    return FC.coverage_at(t, cx, cy, fld=f)


if __name__ == '__main__':
    f, m = get()
    print(json.dumps(m, indent=1))
    # sanity: a unit square deep inside must carry mu >= 1 (property F1)
    for (t, cx, cy) in ((0.0, 1.9, 1.9), (0.3, 1.2, 2.4), (1.0, 2.5, 1.1)):
        print('mu at t=%.2f c=(%.2f,%.2f) = %.6f' % (t, cx, cy, coverage_at(t, cx, cy)))
