#!/usr/bin/env python3
"""validate_pair.py -- A25 pair pipeline vs A23's `pair_box` number (1.3837)."""
import time
from fractions import Fraction as F

from atlas_lib import pair_cell, tanhalf

S386 = F(193, 50)
S384 = F(96, 25)


def show(tag, r, t0):
    if r is None:
        print(f"{tag:36s} INADMISSIBLE")
    elif r.get('infeasible'):
        print(f"{tag:36s} INFEASIBLE PAIR")
    else:
        print(f"{tag:36s} area={float(r['area']):.4f} work={r['work']} "
              f"pass={r['n_pass']} occ={r['n_occ']} tops={r['n_tops']} "
              f"trunc={r['truncated']} {time.time()-t0:.1f}s")


if __name__ == '__main__':
    # --- A23 pair_box: centres +-0.01 around the two adjacent 33deg pinwheel
    # squares of the s=3.86 interior support, theta in [32.1, 33.9] deg.
    t0b, t1b = F(287000, 1000000), F(305500, 1000000)
    d = F(1, 100)
    ax, ay = F(2459700, 1000000), F(2540486, 1000000)
    bx, by = F(1319514, 1000000), F(2459700, 1000000)
    for mc, wb in ((F(1, 16), 2500), (F(1, 32), 9000)):
        t0 = time.time()
        r = pair_cell(S386, (t0b, t1b), (ax - d, ax + d), (ay - d, ay + d),
                      (t0b, t1b), (bx - d, bx + d), (by - d, by + d),
                      dict(min_cell=mc, work_budget=wb))
        show(f'A23 pair_box mc1/{mc.denominator}', r, t0)

    # --- atlas-grid pairs at s = 3.84, h = 3/20, mid tilt
    h = F(3, 20)
    tb = (tanhalf(30, False), tanhalf(33, True))
    for (ia, ja, di, dj) in ((9, 8, -8, 0), (9, 8, -7, 1), (4, 4, 7, 0), (4, 4, 0, 7)):
        xa, ya = (ia * h, (ia + 1) * h), (ja * h, (ja + 1) * h)
        xb, yb = ((ia + di) * h, (ia + di + 1) * h), ((ja + dj) * h, (ja + dj + 1) * h)
        t0 = time.time()
        r = pair_cell(S384, tb, xa, ya, tb, xb, yb, dict(work_budget=2200))
        show(f'pair a=({ia},{ja}) d=({di},{dj})', r, t0)
