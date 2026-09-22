"""A266 price of the STRIP_2 tree: run the tree on a sub-cell (1/150 of a root cell) and report boxes/s and the leaf
depth profile.   python time266.py [--frac 6,5,5] [--lane jam] -> stdout"""
import argparse
import collections
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
import strip266 as M                                                  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frac', default='6,5,5')
    ap.add_argument('--lane', default='jam')
    ap.add_argument('--cell', default='1,1,0')
    ap.add_argument('--maxdepth', type=int, default=30)
    a = ap.parse_args()
    M.Z.belownormal()
    i, j, k = map(int, a.cell.split(','))
    f = list(map(int, a.frac.split(',')))
    lo, hi = M.root(a.lane, i, j, k)
    hi2 = list(hi)
    hi2[2] = lo[2] + (hi[2] - lo[2]) / f[0]
    hi2[3] = lo[3] + (hi[3] - lo[3]) / f[1]
    hi2[4] = lo[4] + (hi[4] - lo[4]) / f[2]
    out, stats = [], {}
    t0 = time.time()
    ok = M.tree(lo, hi2, 0, a.maxdepth, out, stats)
    dt = time.time() - t0
    n = sum(stats.values())
    print('ok', ok, stats, 'leaves', len(out), 'sec', round(dt, 1), 'sec/box', round(dt / max(n, 1), 4),
          'est root cell sec', round(dt * f[0] * f[1] * f[2]), flush=True)
    print('leaf h_u widths (log2):', sorted(collections.Counter(int(round(np.log2(1 / max(r['hi'][0] - r['lo'][0], 1e-12))))
                                                           for r in out).items()))
    op = [r for r in out if r['st'] == 'OPEN']
    print('open', len(op), op[:3])


if __name__ == '__main__':
    main()
