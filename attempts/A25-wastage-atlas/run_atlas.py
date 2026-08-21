#!/usr/bin/env python3
"""
run_atlas.py -- A25: sweep driver for the single-square and pair wastage atlases.

Checkpointed: every finished cell is appended as one JSON line to
work/<tag>.jsonl and the sweep can be restarted (finished ids are skipped).
Multiprocessing with <= 5 workers (a sibling agent shares the machine).

  python run_atlas.py --mode single --s 96/25 --tag s384 --procs 5
  python run_atlas.py --mode pair   --s 96/25 --tag pair384 --procs 5
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as F
from multiprocessing import Pool

from atlas_lib import single_cell, pair_cell, tanhalf, wlo_of, clip_box, merge_rects

# ---------------------------------------------------------------- enumeration


def tilt_bins(theta_max, dtheta):
    out = []
    a = 0
    while a < theta_max - 1e-9:
        b = min(a + dtheta, theta_max)
        out.append((a, b, tanhalf(a, False), tanhalf(b, True)))
        a = b
    return out


def single_cells(s, h, theta_max, dtheta, cxmax=None, mid_only=False):
    """cells of the fundamental domain: centre in the quadrant [0,s/2]^2 (grid of
    step h from 0), tilt in [0, theta_max] in dtheta bins.  See notes.md for the
    D4 convention."""
    S = F(s)
    lim = F(cxmax) if cxmax else S / 2
    nmax = int(math.ceil(float(lim / h)))
    out = []
    for (a, b, t0, t1) in tilt_bins(theta_max, dtheta):
        if mid_only and b <= 15:
            continue
        for i in range(nmax):
            for j in range(nmax):
                xb = (i * h, (i + 1) * h)
                yb = (j * h, (j + 1) * h)
                if clip_box(t0, t1, xb[0], xb[1], yb[0], yb[1], S) is None:
                    continue
                out.append(dict(id=f"{a}_{i}_{j}", theta=[a, b], t=[str(t0), str(t1)],
                                cx=[str(xb[0]), str(xb[1])], cy=[str(yb[0]), str(yb[1])]))
    return out


def pair_cells(s, h, theta_lo, theta_hi, dtheta, dc_lo, dc_hi, anchors,
               max_offsets=0, same_tilt=False):
    """pairs of mid-tilt cells: anchor cell A from a small representative list
    (corner / wall at several depths / interior), B on the same grid with
    box-CENTRE distance in [dc_lo, dc_hi] -- the 'adjacent' regime where A23
    measured superadditivity.  Pairs whose boxes cannot host two interior-disjoint
    unit squares at all (max centre distance < 1) are dropped: two such squares
    have centre distance >= 1 exactly (each supports >= 1/2 towards a separating
    line), so those nodes are already infeasible for a different reason."""
    S = F(s)
    bins = [(a, b, t0, t1) for (a, b, t0, t1) in tilt_bins(theta_hi, dtheta)
            if a >= theta_lo]
    out = []
    nsep = int(math.ceil(float(F(dc_hi) / h))) + 1
    offs = []
    for di in range(-nsep, nsep + 1):
        for dj in range(-nsep, nsep + 1):
            if (di, dj) <= (0, 0):              # unordered pairs, B "after" A
                continue
            dc = float(h) * math.hypot(di, dj)
            if float(dc_lo) <= dc <= float(dc_hi):
                offs.append((math.atan2(dj, di), dc, di, dj))
    offs.sort()
    if max_offsets and len(offs) > max_offsets:   # keep an angularly even subset
        step = len(offs) / float(max_offsets)
        offs = [offs[int(k * step)] for k in range(max_offsets)]
    for (ia, ja) in anchors:
        xa = (ia * h, (ia + 1) * h)
        ya = (ja * h, (ja + 1) * h)
        for (_, dc, di, dj) in offs:
            if True:
                ib, jb = ia + di, ja + dj
                if ib < 0 or jb < 0:
                    continue
                xb = (ib * h, (ib + 1) * h)
                yb = (jb * h, (jb + 1) * h)
                if xb[1] > S or yb[1] > S:
                    continue
                dxM = max(abs(float(xa[1] - xb[0])), abs(float(xb[1] - xa[0])))
                dyM = max(abs(float(ya[1] - yb[0])), abs(float(yb[1] - ya[0])))
                if math.hypot(dxM, dyM) < 1.0:          # cannot host 2 disjoint squares
                    continue
                for (a1, b1, t01, t11) in bins:
                    for (a2, b2, t02, t12) in bins:
                        if a2 < a1 or (a2 - a1 > (0 if same_tilt else dtheta)):
                            continue
                        if clip_box(t01, t11, xa[0], xa[1], ya[0], ya[1], S) is None:
                            continue
                        if clip_box(t02, t12, xb[0], xb[1], yb[0], yb[1], S) is None:
                            continue
                        out.append(dict(
                            id=f"{ia}_{ja}_{di}_{dj}_{a1}_{a2}",
                            A=dict(theta=[a1, b1], t=[str(t01), str(t11)],
                                   cx=[str(xa[0]), str(xa[1])],
                                   cy=[str(ya[0]), str(ya[1])]),
                            B=dict(theta=[a2, b2], t=[str(t02), str(t12)],
                                   cx=[str(xb[0]), str(xb[1])],
                                   cy=[str(yb[0]), str(yb[1])])))
    return out


# ---------------------------------------------------------------- workers
_CFG = {}


def _init(cfg):
    _CFG.update(cfg)


def _params():
    return dict(min_cell=F(_CFG['min_cell']), work_budget=_CFG['work_budget'],
                cell0=F(_CFG['cell0']))


def work_single(cell):
    S = F(_CFG['s'])
    t0 = time.time()
    r = single_cell(S, (F(cell['t'][0]), F(cell['t'][1])),
                    (F(cell['cx'][0]), F(cell['cx'][1])),
                    (F(cell['cy'][0]), F(cell['cy'][1])), _params())
    return _pack(cell, r, t0)


def work_pair(cell):
    S = F(_CFG['s'])
    t0 = time.time()
    A, B = cell['A'], cell['B']
    r = pair_cell(S, (F(A['t'][0]), F(A['t'][1])), (F(A['cx'][0]), F(A['cx'][1])),
                  (F(A['cy'][0]), F(A['cy'][1])),
                  (F(B['t'][0]), F(B['t'][1])), (F(B['cx'][0]), F(B['cx'][1])),
                  (F(B['cy'][0]), F(B['cy'][1])), _params())
    return _pack(cell, r, t0)


def _pack(cell, r, t0):
    out = dict(cell)
    if r is None:
        out.update(dead_lb='0', dead_lb_float=0.0, status='inadmissible',
                   seconds=round(time.time() - t0, 2))
        return out
    if r.get('infeasible'):
        out.update(dead_lb='0', dead_lb_float=0.0, status='infeasible_pair',
                   seconds=round(time.time() - t0, 2))
        return out
    cells = r['cells']
    merged = merge_rects(cells)
    if cells:
        bb = [min(c[0] for c in cells), min(c[1] for c in cells),
              max(c[2] for c in cells), max(c[3] for c in cells)]
    else:
        bb = None
    out.update(dead_lb=str(r['area']), dead_lb_float=float(r['area']),
               status=r.get('screened', 'mapped'),
               bbox=[str(v) for v in bb] if bb else None,
               regions=[[str(v) for v in m] for m in merged],
               cells=[[str(v) for v in c] for c in cells],
               stats=dict(work=r['work'], n_pass=r['n_pass'], n_drop=r['n_drop'],
                          n_occ=r['n_occ'], n_tops=r['n_tops'],
                          truncated=r['truncated']),
               seconds=round(time.time() - t0, 2))
    return out


# ---------------------------------------------------------------- driver
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='single')
    ap.add_argument('--s', default='96/25')
    ap.add_argument('--h', default='3/20')
    ap.add_argument('--dtheta', type=float, default=3)
    ap.add_argument('--theta-max', type=float, default=45)
    ap.add_argument('--theta-lo', type=float, default=15)
    ap.add_argument('--cxmax', default=None)
    ap.add_argument('--mid-only', action='store_true')
    ap.add_argument('--min_cell', default='1/16')
    ap.add_argument('--cell0', default='1/8')
    ap.add_argument('--work_budget', type=int, default=1200)
    ap.add_argument('--max_offsets', type=int, default=0)
    ap.add_argument('--same_tilt', action='store_true')
    ap.add_argument('--dc_lo', default='1')
    ap.add_argument('--dc_hi', default='13/10')
    ap.add_argument('--anchors', default=None, help='e.g. 4,4;10,4;10,10')
    ap.add_argument('--procs', type=int, default=5)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()

    S = F(args.s)
    h = F(args.h)
    cfg = dict(s=args.s, min_cell=args.min_cell, cell0=args.cell0,
               work_budget=args.work_budget)
    if args.mode == 'single':
        cells = single_cells(S, h, args.theta_max, args.dtheta, args.cxmax,
                             args.mid_only)
        fn = work_single
    else:
        anchors = [tuple(int(v) for v in a.split(',')) for a in args.anchors.split(';')]
        cells = pair_cells(S, h, args.theta_lo, args.theta_max, args.dtheta,
                           F(args.dc_lo), F(args.dc_hi), anchors,
                           args.max_offsets, args.same_tilt)
        fn = work_pair
    path = os.path.join('work', args.tag + '.jsonl')
    done = set()
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                try:
                    done.add(json.loads(line)['id'])
                except Exception:
                    pass
    todo = [c for c in cells if c['id'] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"[{args.tag}] {len(cells)} cells, {len(done)} done, {len(todo)} to do",
          flush=True)
    t0 = time.time()
    n = 0
    with open(path, 'a') as out, Pool(args.procs, initializer=_init,
                                      initargs=(cfg,)) as pool:
        for res in pool.imap_unordered(fn, todo, chunksize=1):
            out.write(json.dumps(res) + '\n')
            out.flush()
            n += 1
            if n % 25 == 0:
                el = time.time() - t0
                print(f"[{args.tag}] {n}/{len(todo)}  {el:.0f}s  "
                      f"{el/n:.2f}s/cell (wall)  eta {(len(todo)-n)*el/n/60:.1f}min",
                      flush=True)
    print(f"[{args.tag}] DONE {n} cells in {time.time()-t0:.0f}s", flush=True)
