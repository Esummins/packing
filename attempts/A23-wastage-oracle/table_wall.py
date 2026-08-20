#!/usr/bin/env python3
"""
table_wall.py -- task 2: certified dead area stranded by ONE mid-tilt square near a wall.

Config: container [0,s]^2, s = 3.85 (77/20).  One unit square at tilt theta
(t = tan(theta/2) rational), lowest corner at (X0, d), bottom wall y = 0.
Mapped window: the strip under and beside the square, y in [0, 0.6].

Usage: python table_wall.py [--theta 25] [--d 0] [--corner] [--min_cell 128] [--out path]
       --theta all --d all  runs the whole table sequentially.
"""
import argparse
import json
import sys
from fractions import Fraction as F

from dead_region import Certifier, Placed, cos_sin, tilted_square_on_wall
from wastage import dead_map, save

S = F(77, 20)
X0 = F(8, 5)     # 1.6, far from both side walls

T_OF = {20: F(176327, 1000000), 25: F(221695, 1000000),
        30: F(267949, 1000000), 35: F(315322, 1000000),
        45: F(414214, 1000000)}
D_OF = {0: F(0), 5: F(1, 20), 10: F(1, 10), 20: F(1, 5)}


def wall_config(theta_key, d_key):
    t = T_OF[theta_key]
    d = D_OF[d_key]
    P = tilted_square_on_wall(t, d, X0)
    c, s = cos_sin(t)
    win = (X0 - s - F(7, 10), X0 + c + F(7, 10), F(0), F(3, 5))
    return [P], win, dict(kind='wall', theta=theta_key, d=float(d), s=str(S))


def corner_config(theta_key):
    """square at tilt theta touching BOTH walls at the container corner (0,0)."""
    t = T_OF[theta_key]
    c, s = cos_sin(t)
    P = Placed((c + s) / 2, (c + s) / 2, t)
    win = (F(0), c + s + F(7, 10), F(0), c + s + F(7, 10))
    return [P], win, dict(kind='corner', theta=theta_key, s=str(S))


def run_one(placed, win, meta, min_cell_den, tag, cell0=F(4, 25)):
    print(f"== {tag}  {meta}")
    res = dead_map(placed, S, win, cell0=cell0, min_cell=F(1, min_cell_den),
                   mode='float', depth_max=24, max_boxes_per_cell=1500)
    res['meta'] = meta
    save(f"results/{tag}.json", res)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--theta', default='25')
    ap.add_argument('--d', default='0')
    ap.add_argument('--corner', action='store_true')
    ap.add_argument('--min_cell', type=int, default=64)
    args = ap.parse_args()
    thetas = [20, 25, 30, 35] if args.theta == 'all' else [int(args.theta)]
    ds = [0, 5, 10, 20] if args.d == 'all' else [int(args.d)]
    table = {}
    for th in thetas:
        if args.corner:
            placed, win, meta = corner_config(th)
            r = run_one(placed, win, meta, args.min_cell, f"corner_th{th}")
            table[f"corner,{th}"] = r['area_float']
        else:
            for d in ds:
                placed, win, meta = wall_config(th, d)
                r = run_one(placed, win, meta, args.min_cell, f"wall_th{th}_d{d}")
                table[f"wall,{th},{d}"] = r['area_float']
    print(json.dumps(table, indent=1))
