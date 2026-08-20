#!/usr/bin/env python3
"""exact re-certification until a TARGET area is exactly certified (early exit).
For a Lemma-2 kill we only need certified-dead > s^2 - 11; checking all cells is
a luxury.  Cells are shuffled (seeded) and processed until the target is hit."""
import argparse
import json
import random
import time
from fractions import Fraction as F

from pair_sliver import config
from dead_region import Certifier, Region
from wastage import save

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--target', type=str, required=True)   # e.g. 391/100
    ap.add_argument('--depth', type=int, default=40)
    args = ap.parse_args()
    placed, win, s, meta = config(args.name)
    r = json.load(open(f"results/{args.name}.json"))
    cells = list(r['cells'])
    # LARGEST cells first: the target is reached with the fewest exact certifications
    cells.sort(key=lambda c: (F(c[2]) - F(c[0])) * (F(c[3]) - F(c[1])), reverse=True)
    target = F(args.target)
    cert = Certifier(s, placed, mode='exact', depth_max=args.depth)
    area = F(0)
    failed = []
    t0 = time.time()
    for k, (x0, y0, x1, y1) in enumerate(cells):
        x0, y0, x1, y1 = F(x0), F(y0), F(x1), F(y1)
        D = Region([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        res = cert.certify(D, max_boxes=300000)
        if res['passed']:
            area += D.area
        else:
            failed.append([str(x0), str(y0), str(x1), str(y1)])
        if (k + 1) % 100 == 0:
            print(f"  {k+1}/{len(cells)} cells, exact area {float(area):.4f}, "
                  f"{len(failed)} failed, {time.time()-t0:.0f}s", flush=True)
        if area > target:
            print(f"TARGET REACHED: exact-certified dead area {float(area):.6f} "
                  f"( = {area}) > {float(target):.6f} after {k+1} cells, "
                  f"{len(failed)} failed, {time.time()-t0:.0f}s", flush=True)
            break
    out = dict(area=str(area), area_float=float(area), n_checked=k + 1,
               n_cells=len(cells), failed=failed, target=str(target),
               reached=bool(area > target), seconds=time.time() - t0)
    save(f"results/{args.name}_exact_target.json", out)
    print(json.dumps({kk: out[kk] for kk in ('area_float', 'n_checked', 'reached')}))
