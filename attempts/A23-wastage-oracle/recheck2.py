#!/usr/bin/env python3
"""exact re-certification for pair_sliver configs (pair / corner_tilt / corners4 / tenpack)."""
import argparse
import json

from pair_sliver import config
from wastage import recheck_exact, save

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--depth', type=int, default=40)
    args = ap.parse_args()
    placed, win, s, meta = config(args.name)
    r = json.load(open(f"results/{args.name}.json"))
    out = recheck_exact(placed, s, r['cells'], depth_max=args.depth)
    out['tag'] = args.name
    save(f"results/{args.name}_exact.json", out)
    print(json.dumps(dict(tag=args.name, area=out['area_float'],
                          n=out['n_cells'], failed=len(out['failed'])), indent=1))
