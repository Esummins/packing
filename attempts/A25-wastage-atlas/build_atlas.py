#!/usr/bin/env python3
"""
build_atlas.py -- turn a checkpoint JSONL sweep into the published atlas JSON.

  python build_atlas.py --tag s384 --s 96/25 --out results/atlas_single_3.84.json
  python build_atlas.py --tag pair384 --s 96/25 --kind pair \
                        --out results/atlas_pair_3.84.json

SCHEMA (see notes.md sect.3)
{
 "s": "96/25", "s_float": 3.84, "budget": "s^2-11 as a rational",
 "kind": "single" | "pair",
 "convention": "...D4 fundamental domain...",
 "grid": {"h": "3/20", "dtheta_deg": 3, "theta_range": [0,45], "n_centre": 13,
          "cell0": "1/8", "min_cell": "1/16"},
 "counts": {...}, "meaning": "...",
 "cells": [ {"cx": ["lo","hi"], "cy": ["lo","hi"], "t": ["lo","hi"],
             "theta_deg": [lo,hi], "dead_lb": "rational", "dead_lb_float": f,
             "exact": bool, "bbox": [...], "regions": [[x0,y0,x1,y1], ...],
             "stats": {...}} ]     # (pair cells carry "A" and "B" sub-boxes)
}
Cells NOT listed have no information: a query must treat them as dead_lb = 0.
"""
import argparse
import json
import os
from fractions import Fraction as F

CONV = ("centre in the quadrant [0,s/2]^2 (grid of step h anchored at 0, the last "
        "column/row may stick out past s/2), tilt theta in [0,45] deg; the D4 "
        "action is r:(x,y)->(s-y,x) with theta fixed (theta is mod 90) and "
        "m:(x,y)->(y,x) with theta->90-theta.  Quadrant x theta<=45 is a "
        "fundamental domain (4 x 2 = |D4| = 8).  cx/cy are the ADMISSIBLE CLIP of "
        "the grid cell: [max(lo, wLo/2), min(hi, s-wLo/2)] with wLo = min over the "
        "t-box of cos+sin -- every admissible placement of the grid cell is in it.")

MEANING = ("dead_lb is a certified lower bound on the total area of the listed "
           "regions, each of which is (i) interior-disjoint from every placement "
           "allowed by the cell, (ii) pairwise interior-disjoint, and (iii) DEAD "
           "for that placement -- no unit square inside [0,s]^2 avoiding it can "
           "meet the region -- UNIFORMLY over the whole cell box (A23 PlacedBox "
           "semantics).  Budget lemma: sum over squares of dead_lb <= s^2 - n for "
           "any n-packing meeting the hypothesis, provided the region lists of "
           "different squares are pairwise interior-disjoint.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', required=True)
    ap.add_argument('--s', required=True)
    ap.add_argument('--h', default='3/20')
    ap.add_argument('--dtheta', type=float, default=3)
    ap.add_argument('--theta-max', type=float, default=45)
    ap.add_argument('--n-centre', type=int, default=13)
    ap.add_argument('--cell0', default='1/8')
    ap.add_argument('--min_cell', default='1/16')
    ap.add_argument('--kind', default='single')
    ap.add_argument('--exact', default=None, help='JSON of exact re-certifications')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    S = F(a.s)
    rows = []
    with open(os.path.join('work', a.tag + '.jsonl')) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    exact = {}
    if a.exact and os.path.exists(a.exact):
        with open(a.exact) as f:
            for r in json.load(f)['results']:
                exact[r['id']] = r

    n_all = len(rows)
    n_inadm = sum(1 for r in rows if r.get('status') == 'inadmissible')
    n_infeas = sum(1 for r in rows if r.get('status') == 'infeasible_pair')
    n_screen = sum(1 for r in rows if r.get('status', '').startswith('no wall'))
    n_pos = 0
    cells = []
    for r in rows:
        v = F(r.get('dead_lb', '0'))
        if v <= 0:
            continue
        n_pos += 1
        c = dict(id=r['id'], dead_lb=str(v), dead_lb_float=float(v),
                 exact=False, bbox=r.get('bbox'), regions=r.get('regions', []),
                 stats=r.get('stats'), seconds=r.get('seconds'))
        if a.kind == 'single':
            c.update(cx=r['cx'], cy=r['cy'], t=r['t'], theta_deg=r['theta'])
        else:
            c.update(A=r['A'], B=r['B'])
        e = exact.get(r['id'])
        if e and e.get('exact_area') is not None:
            c['exact'] = True
            c['dead_lb_exact'] = e['exact_area']
            c['dead_lb_float_exact'] = float(F(e['exact_area']))
            c['exact_failed_cells'] = e.get('n_failed', 0)
        cells.append(c)
    cells.sort(key=lambda c: -c['dead_lb_float'])

    out = dict(
        s=a.s, s_float=float(S), budget=str(S * S - 11),
        budget_float=float(S * S - 11), kind=a.kind, convention=CONV,
        meaning=MEANING,
        grid=dict(h=a.h, dtheta_deg=a.dtheta, theta_range=[0, a.theta_max],
                  n_centre=a.n_centre, cell0=a.cell0, min_cell=a.min_cell),
        counts=dict(enumerated=n_all, inadmissible=n_inadm,
                    infeasible_pair=n_infeas, screened_no_wall=n_screen,
                    positive=n_pos, zero=n_all - n_pos,
                    exact_recertified=sum(1 for c in cells if c['exact'])),
        cells=cells)
    with open(a.out, 'w') as f:
        json.dump(out, f, indent=1)
    tot = sum(r.get('seconds', 0) for r in rows)
    print(f"{a.out}: {n_all} enumerated, {n_pos} with dead_lb>0, "
          f"max={cells[0]['dead_lb_float'] if cells else 0:.4f}, "
          f"cpu={tot:.0f}s ({tot/max(1,n_all):.2f}s/cell)")


if __name__ == '__main__':
    main()
