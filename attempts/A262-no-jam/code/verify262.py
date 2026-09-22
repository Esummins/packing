"""A262 own verifier for certs/<fam>262_cell_*.jsonl (fam = pair3, jam):
 (1) every CERT / PRUNE leaf is re-derived by cert262's kernel with an INDEPENDENT tilt binning (0.5-degree bins offset
     by a quarter degree, covering [-45.25, 45.25]);  (2) the leaves of each cell tile its root box exactly (dyadic
     volume identity in fractions);  (3) OPEN leaves are listed, never counted;  (4) the index rows match the files.
    python verify262.py [--fam pair3,jam] [--sample 1.0]   -> results/verify262.json;  exit 1 if anything is bad."""
import argparse
import glob
import json
import os
import random
import sys
from fractions import Fraction as F

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cert262 as K2                                                  # noqa: E402
import tree262 as T                                                   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=float, default=1.0)
    ap.add_argument('--fam', default='pair3,jam')
    a = ap.parse_args()
    bins = [(-45.25 + 0.5 * k + 0.25, 0.25) for k in range(181)]
    random.seed(262)
    rep, bad = {}, 0
    for fam in a.fam.split(','):
        tot = {'CERT': 0, 'PRUNE': 0, 'OPEN': 0, 'cells': 0, 'mismatch': 0, 'tiling_bad': 0}
        idx = os.path.join(ATT, 'certs', '%s262_index.jsonl' % fam)
        index = {json.loads(l)['cell']: json.loads(l) for l in open(idx)} if os.path.exists(idx) else {}
        for fn in sorted(glob.glob(os.path.join(ATT, 'certs', '%s262_cell_*.jsonl' % fam))):
            rows = [json.loads(l) for l in open(fn)]
            parts = list(map(int, os.path.basename(fn)[:-6].split('_')[2:]))
            i, j = parts[:2]
            lo0, hi0 = T.root(fam, i, j, 5.0)
            if len(parts) == 3:                                        # a --sub job: its box is the q-th subcell
                sub = index.get(','.join(map(str, parts)), {}).get('sub', 0)
                lo0, hi0 = T.subcells(fam, (lo0, hi0), sub)[parts[2]]
            n = len(lo0)
            tot['cells'] += 1
            if index.get(','.join(map(str, parts)), {}).get('leaves') != len(rows):
                bad += 1
                print('INDEX MISMATCH', fn)
            vol = F(0)
            for r in rows:
                tot[r['st']] += 1
                v = F(1)
                for k in range(n):
                    v *= (F(r['hi'][k] - r['lo'][k]) / F(hi0[k] - lo0[k])).limit_denominator(1 << 40)
                vol += v
                if r['st'] in ('CERT', 'PRUNE') and random.random() < a.sample:
                    st, m = T.CHECK[fam](r['lo'], r['hi'], bins)
                    if st != r['st'] and not (r['st'] == 'CERT' and st == 'PRUNE'):
                        bad += 1
                        tot['mismatch'] += 1
                        print('MISMATCH', fn, r['st'], '->', st, m)
            if vol != 1:
                bad += 1
                tot['tiling_bad'] += 1
                print('TILING FAILS', fn, float(vol))
        rep[fam] = tot
    out = {'leaves': rep, 'bad': bad}
    json.dump(out, open(os.path.join(ATT, 'results', 'verify262.json'), 'w'), indent=1)
    print(json.dumps(out))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
