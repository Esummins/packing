#!/usr/bin/env python3
"""A45 agent A -- PILOT (float mode).  Three bins, per spec sect.1:
  WC  phi in [21,24]
  CE  d in [21,24], u in the central bin [0, 1/4]
  CC  one mid bin (delta in [130.5, 139.5])   -- expected to fail at every rho
For each: (a) moat ladder, (b) unrestricted dead map out to radius 1/2 (full
extent + area), (c) charged area within B(p, rho/2).
"""
import json
import os
import sys
import time
from fractions import Fraction as F

import a45_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
LOGS = os.path.join(HERE, '..', 'logs')
os.makedirs(RES, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

NSUB = int(os.environ.get('A45_NSUB', '6'))
LOGF = open(os.path.join(LOGS, 'pilot.log'), 'w')


def log(msg):
    print(msg, flush=True)
    LOGF.write(msg + '\n')
    LOGF.flush()


BINS = [
    ('WC', dict(phi=(21, 24)), dict(nsub=NSUB)),
    ('CE', dict(d=(21, 24), u=(F(0), F(1, 4))), dict(nsub=NSUB, nsub_u=4)),
    ('CC', dict(delta=(F(261, 2), F(279, 2))), dict(nsub=1)),
]


def run(kind, bin_, kw):
    t_start = time.time()
    log(f'\n=== {kind} {bin_} nsub={kw} ===')
    ok, det = L.realisable(kind, bin_)
    log(f'  realisable: {ok}  {det}')
    if not ok:
        return dict(kind=kind, bin=str(bin_), realisable=False, detail=str(det))
    configs = L.build_configs(kind, bin_, **kw)
    log(f'  {len(configs)} sub-configs')
    # ---- (a) moat ladder
    mb = 4000 if kind == 'CC' else 60000
    dm = 22 if kind == 'CC' else 30
    rho, runs = L.moat_ladder(kind, configs, mode='float', depth_max=dm,
                              max_boxes=mb, log=log)
    log(f'  MOAT rho = {rho}')
    out = dict(kind=kind, bin={k: [str(v) for v in vv] for k, vv in bin_.items()},
               nsub=kw, realisable=True, realisable_detail=str(det),
               n_configs=len(configs), moat_rho=(str(rho) if rho else None),
               moat_runs=runs)
    # ---- (b) unrestricted dead map, radius 1/2 (diagnostic, single-box bin)
    diag_cfg = L.build_configs(kind, bin_, **{k: 1 for k in kw})
    fd = L.full_dead_map(kind, diag_cfg, R=F(1, 2), cell0=F(1, 16), min_cell=F(1, 64),
                         mode='float', depth_max=24, max_boxes=2500, work_budget=2500)
    log(f'  full dead map R=1/2: area={float(fd["area"]):.6f} '
        f'extent_rel={fd.get("extent_rel")} {fd["stats"]["seconds"]}s '
        f'(pass={fd["stats"]["n_pass"]} drop={fd["stats"]["n_drop"]})')
    out['full_map'] = dict(R='1/2', area=str(fd['area']), area_float=float(fd['area']),
                           extent=fd['extent'], extent_rel=fd.get('extent_rel'),
                           stats={k: v for k, v in fd['stats'].items() if k != 'keeper'},
                           n_cells=len(fd['cells']))
    # ---- (c) charge inside B(p, rho/2)
    if rho is not None:
        R = min(L.RMAX, rho / 2)
        keeper = L.make_keeper(kind, configs)
        cm = L.charge_map(kind, configs, R=L.RMAX, cell0=F(1, 32), min_cell=F(1, 256),
                          mode='float', depth_max=26, max_boxes=4000, keeper=keeper,
                          work_budget=6000)
        a_full, _ = L.clip_cells(cm['cells'], *L.CONTACT_P[kind], L.RMAX,
                                 L.CLIP_Y0[kind])
        a_R, cells_R = L.clip_cells(cm['cells'], *L.CONTACT_P[kind], R, L.CLIP_Y0[kind])
        log(f'  charge map: area(B(p,1/8))={float(a_full):.6f}  '
            f'area(B(p,{R}))={float(a_R):.6f}  {cm["stats"]["seconds"]}s '
            f'(pass={cm["stats"]["n_pass"]} keydrop={cm["stats"]["n_key"]})')
        # box-area reference
        px, py = L.CONTACT_P[kind]
        boxarea = (2 * R) * (2 * R if L.CLIP_Y0[kind] is None else R)
        out['charge'] = dict(
            R=str(R), area=str(a_R), area_float=float(a_R),
            area_at_Rmax=str(a_full), area_at_Rmax_float=float(a_full),
            box_area=str(boxarea), fill_fraction=float(a_R / boxarea) if boxarea else 0.0,
            n_cells=len(cells_R), cells=L.jcells(cells_R),
            stats={k: v for k, v in cm['stats'].items() if k != 'keeper'},
            keeper=cm['stats']['keeper'])
    else:
        out['charge'] = None
    out['seconds'] = round(time.time() - t_start, 1)
    return out


if __name__ == '__main__':
    res = []
    for (kind, bin_, kw) in BINS:
        res.append(run(kind, bin_, kw))
        json.dump(dict(spec='A45 pilot', nsub=NSUB, ladder=[str(r) for r in L.LADDER],
                       results=res), open(os.path.join(RES, 'pilot.json'), 'w'), indent=1)
    n_fail = sum(1 for r in res if r.get('moat_rho') is None)
    log(f'\nPILOT DONE: {n_fail}/{len(res)} bins with NO moat')
    if n_fail == len(res):
        log('DECISION RULE: all three moats fail -> scheme degenerate, STOP.')
        sys.exit(2)
