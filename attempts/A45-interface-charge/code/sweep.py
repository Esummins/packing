#!/usr/bin/env python3
"""A45 agent A -- SWEEP (float mode) over the WC and CE bins.

  WC: phi-bins of (0,45] in 3 deg steps (15 bins), nsub = 6 sub-bins each.
  CE: d-bins of (0,45] in 3 deg steps x 4 slide bins of [-1/2,1/2],
      nsub = 6 x nsub_u = 4 sub-boxes each.
  CC: NOT swept -- structurally moat-free (see notes: one free wedge is always
      >= 90 deg, so a legal square's corner reaches the contact point).

Per bin: moat ladder (largest rho in {1/4,3/16,1/8,3/32,1/16} that certifies),
then the charge map on B(p, 1/8) = B(p, max(ladder)/2).  Charges for any smaller
half-moat radius are obtained by CLIPPING that certified tile list (subsets of
dead sets are dead), which is done in build_table.py.

Checkpoints to work/<tag>.jsonl.  <= 2 processes (hard cap).
"""
import argparse
import json
import os
import time
from fractions import Fraction as F
from multiprocessing import Pool

import a45_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, '..', 'work')
LOGS = os.path.join(HERE, '..', 'logs')
os.makedirs(WORK, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

def u_bins(nu):
    return [(F(-1, 2) + F(j, nu), F(-1, 2) + F(j + 1, nu)) for j in range(nu)]


def jobs(step=3, nsub=6, nsub_u=4, nu=4, types='WC,CE'):
    out = []
    n = int(45 / step)
    types = types.split(',')
    for i in range(n):
        d0, d1 = F(i * step), F((i + 1) * step)
        if 'WC' in types:
            out.append(dict(id=f'WC_{i}', kind='WC', bin=dict(phi=(d0, d1)),
                            kw=dict(nsub=nsub)))
    if 'CE' not in types:
        return out
    for i in range(n):
        d0, d1 = F(i * step), F((i + 1) * step)
        for j, (u0, u1) in enumerate(u_bins(nu)):
            out.append(dict(id=f'CE_{i}_{j}', kind='CE',
                            bin=dict(d=(d0, d1), u=(u0, u1)),
                            kw=dict(nsub=nsub, nsub_u=nsub_u)))
    return out


def work(job):
    t0 = time.time()
    kind, bin_, kw = job['kind'], job['bin'], job['kw']
    rec = dict(id=job['id'], kind=kind,
               bin={k: [str(v) for v in vv] for k, vv in bin_.items()}, kw=kw)
    ok, det = L.realisable(kind, bin_)
    rec['realisable'] = bool(ok)
    rec['realisable_detail'] = {k: str(v) for k, v in det.items()} if isinstance(det, dict) else str(det)
    if not ok:
        rec['note'] = 'vacuous bin -- excluded from the table entirely'
        rec['seconds'] = round(time.time() - t0, 1)
        return rec
    configs = L.build_configs(kind, bin_, **kw)
    rec['n_configs'] = len(configs)
    rho, runs = L.moat_ladder(kind, configs, mode='float', depth_max=32,
                              max_boxes=120000)
    rec['moat_runs'] = runs
    rec['moat_rho'] = str(rho) if rho is not None else None
    if rho is None:
        rec['dropped'] = True
        rec['note'] = 'moat fails at 1/16 -> DROPPED, charge 0'
        rec['area_Rmax'] = '0'
        rec['cells'] = []
        rec['seconds'] = round(time.time() - t0, 1)
        return rec
    rec['dropped'] = False
    keeper = L.make_keeper(kind, configs)
    cm = L.charge_map(kind, configs, R=L.RMAX, cell0=F(1, 32), min_cell=F(1, 256),
                      mode='float', depth_max=26, max_boxes=6000, keeper=keeper,
                      work_budget=8000)
    rec['area_Rmax'] = str(cm['area'])
    rec['area_Rmax_float'] = float(cm['area'])
    rec['cells'] = L.jcells(cm['cells'])
    rec['keeper'] = cm['stats']['keeper']
    rec['map_stats'] = {k: v for k, v in cm['stats'].items() if k != 'keeper'}
    rec['seconds'] = round(time.time() - t0, 1)
    return rec


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='sweep')
    ap.add_argument('--procs', type=int, default=2)
    ap.add_argument('--step', type=int, default=3)
    ap.add_argument('--nsub', type=int, default=6)
    ap.add_argument('--nsub_u', type=int, default=4)
    ap.add_argument('--nu', type=int, default=4)
    ap.add_argument('--types', default='WC,CE')
    ap.add_argument('--only', default=None)
    a = ap.parse_args()
    assert a.procs <= 2, 'hard cap: <= 2 concurrent processes'
    J = jobs(a.step, a.nsub, a.nsub_u, a.nu, a.types)
    if a.only:
        J = [j for j in J if j['id'].startswith(a.only)]
    path = os.path.join(WORK, a.tag + '.jsonl')
    done = set()
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                done.add(json.loads(line)['id'])
    J = [j for j in J if j['id'] not in done]
    print(f'{len(J)} jobs ({len(done)} already done) -> {path}', flush=True)
    t0 = time.time()
    with open(path, 'a') as f, Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(work, J, chunksize=1)):
            f.write(json.dumps(r) + '\n')
            f.flush()
            print(f'  [{k+1}/{len(J)}] {r["id"]} moat={r.get("moat_rho")} '
                  f'area(1/8)={r.get("area_Rmax_float", 0.0):.6f} {r["seconds"]}s',
                  flush=True)
    print(f'DONE {time.time()-t0:.0f}s', flush=True)
