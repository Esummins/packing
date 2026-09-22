"""A266 own verifier for certs/strip266_<lane>_cell_*.jsonl (A259's rule: at least as strong as the tree at every bin,
bisect on disagreement):  (1) every CERT / PRUNE leaf is re-derived by strip266.check_box under an INDEPENDENT tilt
binning of Q (0.4-degree bins with 0 an edge, not nested in the run's 1-degree bins) -- a CERT leaf the independent
cover rejects is bisected (the tree's rule, depth <= 8) and every piece must come out CERT / PRUNE; a PRUNE leaf must
re-derive PRUNE (its condition is bin-free);  (2) the leaves of each cell tile the root box exactly (dyadic volume
identity in exact rationals);  (3) OPEN leaves are listed, never counted.
    python verify266.py [--lane jam] [--sample 1.0]  -> results/verify266_<lane>.json"""
import argparse
import glob
import json
import os
import random
import sys
from fractions import Fraction as F

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import strip266 as M                                                  # noqa: E402

BINS = [(0.4 * k + 0.2, 0.2) for k in range(-113, 113)]


def recert(lo, hi, depth):
    st, m = M.check_box(lo, hi, BINS)
    if st != 'FAIL':
        return True
    if depth >= 8:
        return False
    k = int(((np.array(hi) - np.array(lo)) * M.WEIGHT).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        if not recert(l2, h2, depth + 1):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lane', default='jam')
    ap.add_argument('--sample', type=float, default=1.0)
    a = ap.parse_args()
    M.Z.belownormal()
    random.seed(1)
    tot = {'CERT': 0, 'PRUNE': 0, 'OPEN': 0, 'cells': 0, 'rechecked': 0, 'refined': 0}
    bad, opens, cells = 0, [], {}
    for fn in sorted(glob.glob(os.path.join(HERE, '..', 'certs', 'strip266_%s_cell_*.jsonl' % a.lane))):
        rows = [json.loads(l) for l in open(fn)]
        i, j, kk = map(int, os.path.basename(fn)[:-6].split('_')[3:6])
        lo0, hi0 = M.root(a.lane, i, j, kk)
        vol, cb = F(0), 0
        tot['cells'] += 1
        for r in rows:
            tot[r['st']] += 1
            v = F(1)
            for k in range(5):
                num = F(r['hi'][k] - r['lo'][k]).limit_denominator(1 << 60)
                den = F(hi0[k] - lo0[k]).limit_denominator(1 << 60)
                v *= (num / den).limit_denominator(1 << 40)
            vol += v
            if r['st'] == 'OPEN':
                opens.append((fn, r))
                continue
            if random.random() < a.sample:
                tot['rechecked'] += 1
                st, m = M.check_box(r['lo'], r['hi'], BINS)
                if st != r['st']:
                    if r['st'] == 'CERT' and st == 'FAIL':
                        tot['refined'] += 1
                        if not recert(r['lo'], r['hi'], 0):
                            bad += 1
                            cb += 1
                            print('BAD (fails at depth 8 under the independent cover)', fn, r, flush=True)
                    else:
                        bad += 1
                        cb += 1
                        print('MISMATCH', fn, r, st, m, flush=True)
        if vol != 1:
            bad += 1
            cb += 1
            print('TILING FAILS', fn, float(vol), flush=True)
        cells['%d,%d,%d' % (i, j, kk)] = {'leaves': len(rows), 'open': sum(r['st'] == 'OPEN' for r in rows), 'bad': cb}
        print(fn, cells['%d,%d,%d' % (i, j, kk)], flush=True)
    rep = {'lane': a.lane, 'leaves': tot, 'bad': bad, 'cells': cells, 'open_leaves': [r for _, r in opens][:50]}
    json.dump(rep, open(os.path.join(HERE, '..', 'results', 'verify266_%s.json' % a.lane), 'w'), indent=1)
    print(json.dumps({'lane': a.lane, 'leaves': tot, 'bad': bad, 'cells': cells}))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
