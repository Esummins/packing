#!/usr/bin/env python3
"""A46 task 2 -- the certified w_WC(phi) table (FULL dead region, no moat).

  python task2_wc.py --bins 20,25 25,30 --mode float --out ../work/wc_float_a.json
  python task2_wc.py --bins 40,45 --mode exact --cells ../work/wc_float_a.json \
                     --out ../work/wc_exact_40_45.json

Float pass: quadtree map of the whole window, tiles kept only if they pass the
Lemma-K slab keeper, uniformly over `nsub` tilt sub-boxes of the bin.
Exact pass: re-certify the IDENTICAL tile list in Fraction arithmetic; failing
tiles are dropped (sound).

Every number written here is a certified LOWER bound on the dead area of the
contact's own wall slab, valid uniformly over the phi-bin -- in `mode float`
under the A23 float-interval guards, in `mode exact` in pure Fractions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction as F

import a45_lib as L
import a46_lib as A

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))

X0 = F(13, 8)                 # window half-width  (>= the brief's 1.6)
Y1 = F(5, 4)                  # window height      (>= the brief's 1.2)
WINDOW = (L.PX - X0, F(0), L.PX + X0, Y1)
RADII = [F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(1), F(8, 5), X0]

BINS = [(F(1, 2), F(1)), (F(1), F(2)), (F(2), F(5)), (F(5), F(10)),
        (F(10), F(15)), (F(15), F(20)), (F(20), F(25)), (F(25), F(30)),
        (F(30), F(35)), (F(35), F(40)), (F(40), F(45))]


def bin_id(lo, hi):
    return 'WC_%s_%s' % (lo, hi)


def run_float(lo, hi, nsub, cell0, min_cell, work_budget, log):
    cfgs = L.build_configs('WC', dict(phi=(lo, hi)), nsub=nsub)
    ok, det = L.realisable('WC', dict(phi=(lo, hi)))
    keeper = A.wc_keeper(cfgs)
    r = A.window_map('WC', cfgs, WINDOW, cell0=cell0, min_cell=min_cell,
                     mode='float', keeper=keeper, work_budget=work_budget)
    prof = A.radial_profile(r['cells'], (L.PX, F(0)), RADII, y_floor=F(0))
    log('  %s float: area=%s (%.6f)  %ds  pass=%d drop=%d occ=%d key=%d'
        % (bin_id(lo, hi), r['area'], float(r['area']), r['stats']['seconds'],
           r['stats']['n_pass'], r['stats']['n_drop'], r['stats']['n_occ'],
           r['stats']['n_key']))
    return dict(id=bin_id(lo, hi), type='WC', bin=[str(lo), str(hi)],
                nsub=nsub, cell0=str(cell0), min_cell=str(min_cell),
                window=[str(v) for v in WINDOW],
                realisable=bool(ok), realisable_detail=det,
                area_float=str(r['area']), area_float_f=float(r['area']),
                radial_float={k: str(v) for k, v in prof.items()},
                radial_float_f={k: float(v) for k, v in prof.items()},
                cells=L.jcells(r['cells']),
                stats={k: v for k, v in r['stats'].items()},
                exact=False)


def run_exact(entry, nsub, depth_max, max_boxes, log):
    lo, hi = F(entry['bin'][0]), F(entry['bin'][1])
    cfgs = L.build_configs('WC', dict(phi=(lo, hi)), nsub=nsub)
    cells = [tuple(F(v) for v in c) for c in entry['cells']]
    r = L.recert_exact('WC', cfgs, cells, depth_max=depth_max,
                       max_boxes=max_boxes)
    kept = [c for c in cells
            if [str(v) for v in c] not in r['failed']]
    prof = A.radial_profile(kept, (L.PX, F(0)), RADII, y_floor=F(0))
    log('  %s EXACT: area=%.6f  (float %.6f)  failed=%d/%d  %ds'
        % (entry['id'], float(r['area']), entry['area_float_f'],
           len(r['failed']), len(cells), r['seconds']))
    e = dict(entry)
    e.update(exact=True, area_exact=str(r['area']),
             area_exact_f=float(r['area']),
             n_tiles=len(cells), n_failed_exact=len(r['failed']),
             failed_tiles=r['failed'], exact_seconds=r['seconds'],
             radial_exact={k: str(v) for k, v in prof.items()},
             radial_exact_f={k: float(v) for k, v in prof.items()},
             cells=L.jcells(kept))
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bins', nargs='*', default=None,
                    help='e.g. 20,25 25,30 ; default = all')
    ap.add_argument('--mode', default='float', choices=['float', 'exact'])
    ap.add_argument('--nsub', type=int, default=4)
    ap.add_argument('--cell0', default='1/8')
    ap.add_argument('--min_cell', default='1/64')
    ap.add_argument('--work_budget', type=int, default=400000)
    ap.add_argument('--depth_max', type=int, default=34)
    ap.add_argument('--max_boxes', type=int, default=200000)
    ap.add_argument('--cells', default=None, help='float json for exact mode')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    sel = BINS
    if a.bins:
        want = set()
        for b in a.bins:
            p, q = b.split(',')
            want.add((F(p), F(q)))
        sel = [b for b in BINS if b in want]

    logf = open(a.out + '.log', 'w')

    def log(m):
        print(m, flush=True)
        logf.write(m + '\n')
        logf.flush()

    out = []
    if a.mode == 'float':
        for (lo, hi) in sel:
            out.append(run_float(lo, hi, a.nsub, F(a.cell0), F(a.min_cell),
                                 a.work_budget, log))
            json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    else:
        src = json.load(open(a.cells))
        ids = {bin_id(lo, hi) for (lo, hi) in sel}
        for e in src['entries']:
            if e['id'] not in ids:
                continue
            out.append(run_exact(e, a.nsub, a.depth_max, a.max_boxes, log))
            json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    log('wrote %s (%d entries)' % (a.out, len(out)))


if __name__ == '__main__':
    main()
