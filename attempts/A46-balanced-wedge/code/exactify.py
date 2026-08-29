#!/usr/bin/env python3
"""
exactify.py -- re-certify the strongest atlas entries in PURE FRACTION arithmetic.

The sweep runs the certifier in float-interval mode (outward-rounded guards, A23
sect.2).  This script takes the top-N entries of a sweep and re-runs the SAME
tile list through the exact (Fractions end-to-end) certifier; the exact area is
the sum of the tiles that pass.  Entries with 0 failures carry `exact: true` and
`dead_lb_exact` into the published atlas.

  python exactify.py --tag s384 --s 96/25 --top 50 --procs 5 \
                     --out results/exact_s384.json
"""
import argparse
import json
import os
import time
from fractions import Fraction as F
from multiprocessing import Pool

from dead_region import PlacedBox
from atlas_lib import clip_box
from wastage import recheck_exact

_CFG = {}


def _init(cfg):
    _CFG.update(cfg)


def _boxes(row, S):
    subs = [row] if 'cx' in row else [row['A'], row['B']]
    out = []
    for sub in subs:
        t0, t1 = F(sub['t'][0]), F(sub['t'][1])
        cl = clip_box(t0, t1, F(sub['cx'][0]), F(sub['cx'][1]),
                      F(sub['cy'][0]), F(sub['cy'][1]), S)
        out.append(PlacedBox(t0, t1, *cl))
    return out


def work(row):
    S = F(_CFG['s'])
    t0 = time.time()
    placed = _boxes(row, S)
    cells = [(F(c[0]), F(c[1]), F(c[2]), F(c[3])) for c in row['cells']]
    r = recheck_exact(placed, S, cells, depth_max=_CFG['depth_max'],
                      max_boxes_per_cell=_CFG['max_boxes'], verbose=False)
    return dict(id=row['id'], float_area=row['dead_lb'], exact_area=r['area'],
                exact_float=r['area_float'], n_cells=r['n_cells'],
                n_failed=len(r['failed']), seconds=round(time.time() - t0, 1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--s', required=True)
    ap.add_argument('--top', type=int, default=50)
    ap.add_argument('--procs', type=int, default=5)
    ap.add_argument('--depth_max', type=int, default=34)
    ap.add_argument('--max_boxes', type=int, default=200000)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    rows = []
    with open(os.path.join('work', a.tag + '.jsonl')) as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get('cells'):
                    rows.append(r)
    rows.sort(key=lambda r: -r['dead_lb_float'])
    rows = rows[:a.top]
    print(f"exactify {len(rows)} entries, "
          f"{sum(len(r['cells']) for r in rows)} tiles", flush=True)
    cfg = dict(s=a.s, depth_max=a.depth_max, max_boxes=a.max_boxes)
    res = []
    t0 = time.time()
    with Pool(a.procs, initializer=_init, initargs=(cfg,)) as pool:
        for k, r in enumerate(pool.imap_unordered(work, rows, chunksize=1)):
            res.append(r)
            print(f"  [{k+1}/{len(rows)}] {r['id']} float={float(F(r['float_area'])):.4f}"
                  f" exact={r['exact_float']:.4f} failed={r['n_failed']}"
                  f" {r['seconds']}s", flush=True)
            with open(a.out, 'w') as f:
                json.dump(dict(s=a.s, tag=a.tag, results=res,
                               seconds=round(time.time() - t0, 1)), f, indent=1)
    nf = sum(r['n_failed'] for r in res)
    print(f"DONE {len(res)} entries, {nf} failed tiles total, "
          f"{time.time()-t0:.0f}s", flush=True)
