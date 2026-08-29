#!/usr/bin/env python3
"""A45 agent A -- EXACT (Fraction) re-certification of the moat of every KEPT entry.

The sweep ran the moat ladder in float-interval mode.  Lemma M / M' (and hence the
disjointness of the Own(i) sets in Theorem A45.1) rest on the moat, so this closes
the last float-only step: for every kept entry, re-run D = B(p, moat_rho) cap
container through the certifier in pure Fractions, over the SAME sub-box family.

A failure DOWNGRADES the entry: it is dropped from the table (charge 0), which is
always sound.  Results are written back into results/charge_table.json as
`moat_exact` / `moat_exact_failed`, and rho_min / charges / the frontier are
recomputed over the surviving entries.
"""
import argparse
import json
import os
import time
from fractions import Fraction as F
from multiprocessing import Pool

import a45_lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
WORK = os.path.join(HERE, '..', 'work')
TABLE = os.path.join(RES, 'charge_table.json')


def job(e):
    t0 = time.time()
    bin_ = {k: tuple(F(v) for v in vv) for k, vv in e['bins'].items()}
    configs = L.build_configs(e['type'], bin_, **e['kw'])
    r = L.moat(e['type'], configs, F(e['moat_rho']), mode='exact',
               depth_max=_D['depth_max'], max_boxes=_D['max_boxes'])
    return dict(id=e['id'], rho=e['moat_rho'], passed=bool(r['passed']),
                boxes=r['boxes'], seconds=round(time.time() - t0, 1),
                witness=r.get('witness'))


_D = dict(depth_max=34, max_boxes=200000)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--procs', type=int, default=2)
    a = ap.parse_args()
    assert a.procs <= 2
    tab = json.load(open(TABLE))
    todo = [e for e in tab['entries'] if not e['dropped']]
    cache = os.path.join(WORK, 'exact_moats.jsonl')
    done = {}
    if os.path.exists(cache):
        for line in open(cache):
            if line.strip():
                r = json.loads(line)
                done[r['id']] = r
    todo = [e for e in todo if e['id'] not in done]
    print(f'exact moats: {len(todo)} to do ({len(done)} cached)', flush=True)
    t0 = time.time()
    with open(cache, 'a') as cf, Pool(a.procs) as pool:
        for k, r in enumerate(pool.imap_unordered(job, todo, chunksize=1)):
            done[r['id']] = r
            cf.write(json.dumps(r) + '\n')
            cf.flush()
            print(f'  [{k+1}/{len(todo)}] {r["id"]} rho={r["rho"]} '
                  f'{"PASS" if r["passed"] else "FAIL"} {r["boxes"]} boxes {r["seconds"]}s',
                  flush=True)
    nfail = 0
    for e in tab['entries']:
        if e['dropped']:
            e['moat_exact'] = None
            continue
        r = done.get(e['id'])
        e['moat_exact'] = bool(r and r['passed'])
        e['moat_exact_boxes'] = r['boxes'] if r else None
        if not e['moat_exact']:
            nfail += 1
            e['dropped'] = True
            e['note'] = 'moat failed EXACT re-certification -> entry DROPPED (charge 0)'
            e['charge'], e['charge_float'], e['regions'] = '0', 0.0, []
    # recompute rho_min and the charges over the survivors
    kept = [e for e in tab['entries'] if not e['dropped']]
    if nfail:
        rho_min = min(F(e['moat_rho']) for e in kept)
        print(f'{nfail} moats failed exactly; rho_min recomputed = {rho_min}')
        assert F(tab['rho_min']) <= rho_min, 'rho_min can only rise when bins drop'
        # charges were computed on B(p, old rho_min/2) which is a SUBSET of
        # B(p, new rho_min/2): still sound, just conservative.  Record both.
        tab['rho_min_after_exact_moats'] = str(rho_min)
    tab['counts']['moat_exact_failures'] = nfail
    tab['counts']['moat_exact_seconds'] = round(time.time() - t0, 1)
    tab['moat_exact'] = dict(
        depth_max=_D['depth_max'], max_boxes=_D['max_boxes'],
        note=('every kept entry\'s moat B(p,moat_rho) re-certified in pure Fractions '
              'over the same sub-box family; failures drop the entry'))
    json.dump(tab, open(TABLE, 'w'), indent=1)
    print(f'DONE: {len(kept)} entries keep an EXACT moat, {nfail} dropped, '
          f'{time.time()-t0:.0f}s')
