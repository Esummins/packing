#!/usr/bin/env python3
"""validate.py -- A25 sanity checks against A23's published numbers, and
resolution / box-size sensitivity of the atlas pipeline."""
import sys
import time
from fractions import Fraction as F

from atlas_lib import single_cell, tanhalf

S385 = F(77, 20)
S384 = F(96, 25)


def show(tag, r, t0):
    if r is None:
        print(f"{tag:34s} INADMISSIBLE")
        return
    print(f"{tag:34s} area={float(r['area']):.4f} work={r['work']} pass={r['n_pass']} "
          f"occ={r['n_occ']} tops={r['n_tops']} trunc={r['truncated']} "
          f"{time.time()-t0:.1f}s")


def run(tag, s, tb, xb, yb, **params):
    t0 = time.time()
    show(tag, single_cell(s, tb, xb, yb, params), t0)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if which in ('all', 'a23'):
        # A23 sect.4b "corner_box": core [0.72,0.74]^2 x [39,41]deg at s=3.85,
        # A23 exhaustive quadtree (min_cell 1/64, whole 2.1x2.1 window) -> 0.5285
        tb = (F(354119, 1000000), F(373885, 1000000))
        xb = (F(18, 25), F(37, 50))
        run('A23 corner_box (mc 1/16)', S385, tb, xb, xb)
        run('A23 corner_box (mc 1/32)', S385, tb, xb, xb, min_cell=F(1, 32),
            work_budget=6000)
        run('A23 corner_box (mc 1/64)', S385, tb, xb, xb, min_cell=F(1, 64),
            work_budget=30000)

    if which in ('all', 'res'):
        # resolution / core-box-size sensitivity at s = 3.84
        tb = (tanhalf(30, False), tanhalf(33, True))
        for mc, wb in ((F(1, 16), 1200), (F(1, 32), 5000)):
            run(f'wall y[.90,1.05] h=.15 mc1/{mc.denominator}', S384, tb,
                (F(3, 2), F(33, 20)), (F(9, 10), F(21, 20)), min_cell=mc, work_budget=wb)
        run('wall y[.90,.975] h=.075 mc1/16', S384, tb,
            (F(3, 2), F(63, 40)), (F(9, 10), F(39, 40)))
        run('wall y[.90,.975] h=.075 mc1/32', S384, tb,
            (F(3, 2), F(63, 40)), (F(9, 10), F(39, 40)), min_cell=F(1, 32),
            work_budget=5000)
        tb1 = (tanhalf(30, False), tanhalf(31, True))
        run('wall h=.075 dth=1deg mc1/32', S384, tb1,
            (F(3, 2), F(63, 40)), (F(9, 10), F(39, 40)), min_cell=F(1, 32),
            work_budget=5000)
        run('corner h=.15 dth=3 mc1/32', S384, tb, (F(3, 5), F(3, 4)),
            (F(3, 5), F(3, 4)), min_cell=F(1, 32), work_budget=5000)
        run('corner h=.075 dth=3 mc1/32', S384, tb, (F(3, 5), F(27, 40)),
            (F(3, 5), F(27, 40)), min_cell=F(1, 32), work_budget=5000)
