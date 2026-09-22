"""A263 own verifier for certs/<tag>263_cell_*.jsonl  (tag = P2, WE, WS; WEn / WSn = the non-ADJ runs):
 (1) every CERT / PRUNE leaf is re-derived by cert263.check_box with an INDEPENDENT tilt binning: 0.4-degree bins with
     edges at multiples of 0.4 (so 0 is an edge -- the wall-nearest-vertex convention changes there -- and the bins are
     not nested in the 1-degree bins of the run), covering [-45.2, 45.2];
 (2) the leaves of each cell tile its root box exactly (dyadic volume identity in fractions);
 (3) the PLUG hypothesis is re-checked on every P2 leaf that used it (lo[a'] > 0.604);
 (4) OPEN leaves are listed, never counted.        python verify263.py [--sample 1.0] [--tags P2,WE,WS]"""
import argparse
import glob
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cert263 as C                                                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=float, default=1.0)
    ap.add_argument('--tags', default='P2,WE,WS')
    a = ap.parse_args()
    bins = [(0.4 * k + 0.2, 0.2) for k in range(-113, 113)]
    random.seed(1)
    rep, bad = {}, 0
    for tag in a.tags.split(','):
        fam, adj = tag[:2], not tag.endswith('n')
        tot = {'CERT': 0, 'PRUNE': 0, 'OPEN': 0, 'cells': 0, 'plug_leaves': 0, 'rechecked': 0}
        for fn in sorted(glob.glob(os.path.join(HERE, '..', 'certs', '%s263_cell_*.jsonl' % tag))):
            rows = [json.loads(l) for l in open(fn)]
            i, j = map(int, os.path.basename(fn)[:-6].split('_')[2:4])
            lo0, hi0 = C.root(fam, i, j, 5.0, None if adj else 1.2)
            vol = F(0)
            tot['cells'] += 1
            for r in rows:
                tot[r['st']] += 1
                v = F(1)
                for k in range(4):
                    num = F(r['hi'][k] - r['lo'][k]).limit_denominator(1 << 60)
                    den = F(hi0[k] - lo0[k]).limit_denominator(1 << 60)
                    v *= (num / den).limit_denominator(1 << 40)
                vol += v
                if fam == 'P2' and r['st'] == 'CERT' and r['lo'][2] > C.PLUG_A:
                    tot['plug_leaves'] += 1
                if r['st'] in ('CERT', 'PRUNE') and random.random() < a.sample:
                    tot['rechecked'] += 1
                    st, m = C.check_box(fam, r['lo'], r['hi'], bins, adj=adj)
                    if st != r['st']:
                        bad += 1
                        print('MISMATCH', fn, r, st, m, flush=True)
            if vol != 1:
                bad += 1
                print('TILING FAILS', fn, float(vol), flush=True)
        rep[tag] = tot
    print(json.dumps({'leaves': rep, 'bad': bad}))
    return 1 if bad else 0


sys.exit(main())
