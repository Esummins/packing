#!/usr/bin/env python3
"""exact-mode re-certification of a float-mapped cell list (headline entries)."""
import argparse
import json
from fractions import Fraction as F

from table_wall import wall_config, corner_config, S
from wastage import recheck_exact, save

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('tag')                    # e.g. wall_th25_d0
    ap.add_argument('--depth', type=int, default=40)
    args = ap.parse_args()
    r = json.load(open(f"results/{args.tag}.json"))
    meta = r['meta']
    if meta['kind'] == 'wall':
        placed, win, _ = wall_config(meta['theta'], int(round(meta['d'] * 100)))
    else:
        placed, win, _ = corner_config(meta['theta'])
    out = recheck_exact(placed, S, r['cells'], depth_max=args.depth)
    out['tag'] = args.tag
    save(f"results/{args.tag}_exact.json", out)
    print(json.dumps({k: out[k] for k in ('area_float', 'n_cells')}, indent=1),
          "failed:", len(out['failed']))
