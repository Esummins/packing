"""A244 fixed-side probe: at a ladder of sides BELOW the descent's limit, how close does the
twelve-cell (or four-cell) condition get?  For each side the probe runs many restarts of the
fixed-s penalty and records the best residual -- the smallest achievable

    max( -min wall gap, -min pair gap, delta - min over cells of the second depth )

which is 0 exactly when a delta-margin stuck packing exists at that side.  Evidence, not proof:
a positive best residual says only that the search did not find one.

    python probe244.py --tag T --mode twelve --sides 3.99,3.95,3.9,3.877084,3.82 --n 400
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A217-torque-probe/code'))
sys.path.insert(0, HERE)

import fast244 as F           # noqa: E402
import feas244 as A           # noqa: E402
import cells244 as C          # noqa: E402
import verify244 as V         # noqa: E402
from search244 import a217_seeds, belownormal        # noqa: E402


def residual(z, cells, delta):
    gw, gp, d2 = F.worst(z, cells, delta)
    return max(-gw, -gp, delta - d2, 0.0), (gw, gp, d2)


def attempt(z0, cells, delta, s, rng, inner=4):
    z = np.array(z0, float)
    lam = s / float(z[F.S_IDX])
    z[0:33:3] *= lam
    z[1:33:3] *= lam
    z[F.S_IDX] = s
    best = None
    for k in range(inner):
        start = z if k == 0 else A.jitter(z, rng, 0.05 * k, 4.0 * k)
        start[F.S_IDX] = s
        w, f = A.polish(start, cells, delta)
        r, det = residual(w, cells, delta)
        if best is None or r < best[0]:
            best = (r, w, det)
        if r == 0.0:
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--mode', default='twelve', choices=('twelve', 'four', 'slots'))
    ap.add_argument('--sides', default='3.999,3.99,3.95,3.9,3.877084,3.82')
    ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--delta', type=float, default=1e-4)
    ap.add_argument('--wall', type=float, default=1e9)
    a = ap.parse_args()
    belownormal()
    cells = A.CELLSETS[a.mode]
    sides = [float(x) for x in a.sides.split(',')]
    out = os.path.join(ATT, 'results', 'probe244_%s.jsonl' % a.tag)
    stop = os.path.join(ATT, 'logs', 'STOP')
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                done.add(json.loads(line)['rid'])
            except Exception:                                     # noqa
                pass
    fh = open(out, 'a')
    rng = np.random.default_rng(a.seed)
    pool = a217_seeds()
    t0 = time.time()
    for s in sides:
        bestr = float('inf')
        for k in range(a.n):
            if os.path.exists(stop) or time.time() - t0 > a.wall:
                print('stop', flush=True)
                fh.close()
                return
            rid = 'probe|%s|s%g|d%g|%d' % (a.mode, s, a.delta, a.seed * 100000 + k)
            if rid in done:
                continue
            fam = ('a217', 'random', 'border', 'grid')[k % 4]
            if fam == 'a217':
                z0 = pool[(a.seed + k) % len(pool)][1].copy()
            else:
                z0 = A.STARTS[fam](rng, s)
            ts = time.time()
            r, w, det = attempt(z0, cells, a.delta, s, rng)
            strict = bool(det[0] >= -1e-12 and det[1] >= -1e-12 and det[2] > 0.0)
            rec = {'rid': rid, 'side': s, 'mode': a.mode, 'delta': a.delta, 'family': fam,
                   'residual': r, 'min_wall_gap': det[0], 'min_pair_gap': det[1],
                   'worst_second_depth': det[2], 'strict_ok': strict,
                   'secs': round(time.time() - ts, 2)}
            if r < 1e-3:
                rec['z'] = [float(v) for v in w]
            if strict:
                st = C.stuck_report(w)
                rec['meeters'] = st['meeters']
                cert = V.certify_z(w, need=('twelve' if a.mode == 'twelve' else 'four',))
                rec['cert'] = {kk: vv for kk, vv in cert.items() if kk != 'cells'}
            fh.write(json.dumps(rec) + '\n')
            fh.flush()
            bestr = min(bestr, r)
            if k % 25 == 0 or strict:
                print('s %.6f  %4d/%d  best residual %.6f  %.0fs' % (
                    s, k, a.n, bestr, time.time() - t0), flush=True)
        print('SIDE %.6f done: best residual %.6f' % (s, bestr), flush=True)
    print('all done %.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
