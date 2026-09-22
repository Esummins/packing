"""A265 own verifier for certs/P2265_cell_*.jsonl (A259's rule: at least as strong as the tree at every bin, bisect on
disagreement):  (1) every CERT / PRUNE leaf is re-derived by cert265.check_box under an INDEPENDENT tilt binning
(0.4-degree bins, 0 an edge, not nested in the run's 1-degree bins); a leaf the independent cover does not re-certify
is bisected (the tree's rule, depth <= 8) and every piece must come out CERT / PRUNE -- only a piece still failing at
depth 8 is BAD;  (2) the leaves of each cell tile the root box exactly (dyadic volume identity);  (3) on every leaf the
recorded side equals the ADJ-consistent side recomputed here and is >= SMIN, and the plug used (from lo[a']) satisfies
Lemma PLUG's hypothesis a' > sqrt(2)/4 + rho;  (4) OPEN leaves are listed, never counted.
    python verify265.py [--sample 1.0]  -> results/verify265.json"""
import argparse
import glob
import json
import math
import os
import random
import sys
from fractions import Fraction as F

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cert265 as M                                                   # noqa: E402

BINS = [(0.4 * k + 0.2, 0.2) for k in range(-113, 113)]


def recert(lo, hi, depth):
    st, m, s = M.check_box(lo, hi, BINS)
    if st != 'FAIL':
        return True
    if depth >= 8:
        return False
    k = int(((np.array(hi) - np.array(lo)) * M.C.WEIGHT['P2']).argmax())
    mid = 0.5 * (lo[k] + hi[k])
    for a, b in ((lo[k], mid), (mid, hi[k])):
        l2, h2 = list(lo), list(hi)
        l2[k], h2[k] = a, b
        if not recert(l2, h2, depth + 1):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=float, default=1.0)
    a = ap.parse_args()
    random.seed(1)
    tot = {'CERT': 0, 'PRUNE': 0, 'OPEN': 0, 'cells': 0, 'rechecked': 0, 'refined': 0, 'plug_leaves': 0}
    bad, opens, cells = 0, [], {}
    for fn in sorted(glob.glob(os.path.join(HERE, '..', 'certs', 'P2265_cell_*.jsonl'))):
        rows = [json.loads(l) for l in open(fn)]
        i, j = map(int, os.path.basename(fn)[:-6].split('_')[2:4])
        lo0, hi0 = M.C.root('P2', i, j, 5.0)
        vol, cb = F(0), 0
        tot['cells'] += 1
        for r in rows:
            tot[r['st']] += 1
            v = F(1)
            for k in range(4):
                num = F(r['hi'][k] - r['lo'][k]).limit_denominator(1 << 60)
                den = F(hi0[k] - lo0[k]).limit_denominator(1 << 60)
                v *= (num / den).limit_denominator(1 << 40)
            vol += v
            if r['st'] == 'OPEN':
                opens.append((fn, r))
                continue
            s_here = min(M.SMAX, r['hi'][0] + math.cos(r['hi'][1]) + math.sin(r['hi'][1]) + 2.0,
                         r['hi'][2] + math.cos(r['hi'][3]) + math.sin(r['hi'][3]) + 2.0)
            if r['st'] == 'CERT' and (abs(s_here - r['s']) > 1e-5 or s_here < M.SMIN):
                bad += 1
                cb += 1
                print('SIDE MISMATCH', fn, r, s_here, flush=True)
            a_min, rho = M.plug_of(r['lo'])
            if rho > 0:
                tot['plug_leaves'] += 1
                if not r['lo'][2] > math.sqrt(2) / 4 + rho:
                    bad += 1
                    cb += 1
                    print('PLUG HYPOTHESIS FAILS', fn, r, flush=True)
            if random.random() < a.sample:
                tot['rechecked'] += 1
                st, m, s = M.check_box(r['lo'], r['hi'], BINS)
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
        cells['%d,%d' % (i, j)] = {'leaves': len(rows), 'open': sum(r['st'] == 'OPEN' for r in rows), 'bad': cb}
    rep = {'leaves': tot, 'bad': bad, 'cells': cells, 'open_leaves': [r for _, r in opens][:50]}
    json.dump(rep, open(os.path.join(HERE, '..', 'results', 'verify265.json'), 'w'), indent=1)
    print(json.dumps({'leaves': tot, 'bad': bad, 'cells': cells}))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
