"""A260 own verifier for certs/<fam>260_cell_*.jsonl (fam = layer, hybA, hybB, hybAB):
 (1) every CERT / PRUNE leaf is re-derived by cert260.check_box with an INDEPENDENT tilt binning (0.5-degree bins offset
     by a quarter degree, covering [-45.25, 45.25]);  (2) the leaves of each cell tile its root box exactly -- exact
     dyadic volume identity in fractions over the ACTIVE coordinates (a degenerate coordinate has lo = hi in every leaf);
 (3) the PLUG hypothesis is re-checked on every leaf that used it (lo[a'] > 0.354 + RHO);  (4) OPEN leaves are listed,
     never counted.      python verify260.py [--sample 1.0] [--fam layer,hybA]"""
import argparse
import glob
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cert260 as C                                                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=float, default=1.0)
    ap.add_argument('--fam', default='layer,hybA,hybB,hybAB')
    a = ap.parse_args()
    bins = [(-45.25 + 0.5 * k + 0.25, 0.25) for k in range(181)]
    random.seed(1)
    rep, bad = {}, 0
    for fam in a.fam.split(','):
        tot = {'CERT': 0, 'PRUNE': 0, 'OPEN': 0, 'cells': 0, 'plug_leaves': 0}
        for fn in sorted(glob.glob(os.path.join(HERE, '..', 'certs', '%s260_cell_*.jsonl' % fam))):
            rows = [json.loads(l) for l in open(fn)]
            i, j = map(int, os.path.basename(fn)[:-6].split('_')[2:4])
            lo0, hi0 = C.root(fam, i, j, 5.0)
            act = [k for k in range(6) if hi0[k] > lo0[k]]
            vol = F(0)
            tot['cells'] += 1
            for r in rows:
                tot[r['st']] += 1
                v = F(1)
                for k in act:
                    num = F(r['hi'][k] - r['lo'][k]).limit_denominator(1 << 60)
                    den = F(hi0[k] - lo0[k]).limit_denominator(1 << 60)
                    v *= (num / den).limit_denominator(1 << 40)
                vol += v
                if any(r['lo'][k] != r['hi'][k] for k in range(6) if k not in act):
                    bad += 1
                    print('DEGENERATE COORDINATE MOVED', fn, r)
                if r['st'] == 'CERT' and r['lo'][2] > C.PLUG_A:
                    tot['plug_leaves'] += 1
                if r['st'] in ('CERT', 'PRUNE') and random.random() < a.sample:
                    st, m = C.check_box(r['lo'], r['hi'], bins, adj=(fam != 'layer'))
                    if st != r['st']:
                        bad += 1
                        print('MISMATCH', fn, r, st, m)
            if vol != 1:
                bad += 1
                print('TILING FAILS', fn, float(vol))
        rep[fam] = tot
    print(json.dumps({'leaves': rep, 'bad': bad}))
    return 1 if bad else 0


sys.exit(main())
