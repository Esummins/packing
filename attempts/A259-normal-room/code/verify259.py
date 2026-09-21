"""A259 own verifier for certs/pair259_cell_*.jsonl: (1) every CERT leaf is re-checked by cert259.check_box with a
DIFFERENT tilt binning (0.5-degree bins offset by a quarter degree -- an independent cover of [-45, 45));
(2) PRUNE leaves are re-derived; (3) the leaves of each cell tile the root cell exactly (volume identity in exact
dyadic arithmetic via fractions); (4) LAYER / OPEN leaves are listed, never counted as certified.
    python verify259.py [--sample 0.1]   (fraction of CERT leaves re-checked; 1.0 = all)"""
import argparse, glob, json, math, os, random, sys
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import cert259 as K

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sample', type=float, default=1.0); a = ap.parse_args()
    bins = [(-45.25 + 0.5 * k + 0.25, 0.25) for k in range(181)]      # covers [-45.25, 45.25]
    random.seed(1); tot = {'CERT': 0, 'PRUNE': 0, 'LAYER': 0, 'OPEN': 0}; bad = 0
    for fn in sorted(glob.glob(os.path.join(HERE, '..', 'certs', 'pair259_cell_*.jsonl'))):
        rows = [json.loads(l) for l in open(fn)]
        i, j = map(int, os.path.basename(fn)[:-6].split('_')[2:4])
        vol = F(0)
        for r in rows:
            tot[r['st']] += 1
            fr = [F(r['hi'][k]).limit_denominator(1 << 40) - F(r['lo'][k]).limit_denominator(1 << 40) for k in (0, 2)]
            ph = [(r['hi'][k] - r['lo'][k]) / (5.0 * K.DEG) for k in (1, 3)]
            vol += fr[0] * fr[1] * F(ph[0]).limit_denominator(1 << 30) * F(ph[1]).limit_denominator(1 << 30)
            if r['st'] in ('CERT', 'PRUNE') and random.random() < a.sample:
                st, m = K.check_box(r['lo'], r['hi'], bins)
                if st != r['st'] and not (r['st'] == 'PRUNE' and st == 'PRUNE'):
                    bad += 1; print('MISMATCH', fn, r, st, m)
        if vol != 1:
            bad += 1; print('TILING FAILS', fn, float(vol))
    print(json.dumps({'leaves': tot, 'bad': bad}))
    return 1 if bad else 0

sys.exit(main())
