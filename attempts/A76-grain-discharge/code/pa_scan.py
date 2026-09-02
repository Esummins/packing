#!/usr/bin/env python3
"""pa_scan.py -- the possibly-active row set PA(R) BY CONSTRUCTION (measurement run; the
certified version is emitted separately).  For each radius R, evaluate every corner-wall row
(176) and every corner-edge row (1760) over box(z0, R) in exact interval arithmetic and list
the rows whose enclosure contains 0.  Rows certified strictly positive or strictly negative
cannot be active anywhere in the box.  Also records the min positive lower bound (the
next-contact margin).
Usage: python pa_scan.py [uniform|theta]
"""
import sys
import json
import time
from fractions import Fraction
from grainlib import *


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'uniform'
    z0 = load_z0()
    cand = all_candidate_rows()
    rows22, d = a22_rows()
    names22 = set(row_name(c) for c in rows22)
    out = {}
    for R in ['1/1000', '2/1000', '3/1000', '4/1000', '5/1000', '6/1000', '8/1000', '10/1000',
              '12/1000', '15/1000', '20/1000', '25/1000', '30/1000']:
        r = Fraction(R)
        rr = radii(r, r / 2, r) if mode == 'theta' else r
        B = box(z0, rr)
        t0 = time.time()
        pa = []
        margin = None
        for c in cand:
            v = eval_row(B, c)
            if v.lo <= 0 <= v.hi:
                pa.append(row_name(c))
            elif v.lo > 0:
                if margin is None or v.lo < margin[0]:
                    margin = (v.lo, row_name(c))
        new = [n for n in pa if n not in names22]
        print('R=%-8s |PA|=%3d  new(not A22)=%d  next-contact margin=%.4g (%s)  %.1fs'
              % (R, len(pa), len(new), float(margin[0]), margin[1], time.time() - t0))
        if new:
            print('    new:', new)
        out[R] = {'PA': pa, 'new': new, 'margin': [fstr(margin[0]), margin[1]]}
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'pa_scan_%s.json' % mode), 'w'), indent=1)


if __name__ == '__main__':
    main()
