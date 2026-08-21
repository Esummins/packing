#!/usr/bin/env python3
"""calibrate.py -- cost/value probe on representative atlas cells."""
import sys
import time
from fractions import Fraction as F

from atlas_lib import single_cell, pair_cell, tanhalf

S = F(96, 25)
H = F(3, 20)


def tb(a, b):
    return (tanhalf(a, False), tanhalf(b, True))


CASES = [
    ('corner_30-33', (tb(30, 33), (F(3, 5), F(3, 5) + H), (F(3, 5), F(3, 5) + H))),
    ('corner_42-45', (tb(42, 45), (F(3, 5), F(3, 5) + H), (F(3, 5), F(3, 5) + H))),
    ('corner_00-03', (tb(0, 3), (F(3, 5), F(3, 5) + H), (F(3, 5), F(3, 5) + H))),
    ('wall_30-33_y0.60', (tb(30, 33), (F(3, 2), F(3, 2) + H), (F(3, 5), F(3, 5) + H))),
    ('wall_30-33_y0.90', (tb(30, 33), (F(3, 2), F(3, 2) + H), (F(9, 10), F(9, 10) + H))),
    ('wall_30-33_y1.20', (tb(30, 33), (F(3, 2), F(3, 2) + H), (F(6, 5), F(6, 5) + H))),
    ('interior_30-33', (tb(30, 33), (F(3, 2), F(3, 2) + H), (F(3, 2), F(3, 2) + H))),
]

if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for name, (t, xb, yb) in CASES:
        if only and only not in name:
            continue
        t0 = time.time()
        r = single_cell(S, t, xb, yb)
        if r is None:
            print(f"{name:22s} INADMISSIBLE")
            continue
        print(f"{name:22s} area={float(r['area']):.4f} work={r['work']} "
              f"pass={r['n_pass']} drop={r['n_drop']} occ={r['n_occ']} "
              f"tops={r['n_tops']} trunc={r['truncated']} {time.time()-t0:.1f}s "
              f"{r.get('screened','')}")
