#!/usr/bin/env python3
"""A45 agent A -- build results/charge_table.json from work/<tag>.jsonl.

Steps (spec sect.3 and 4):
 3. rho_min = global min moat over KEPT bins; bins failing the ladder at 1/16 are
    DROPPED (charge 0, recorded).  Every charge is then re-evaluated on
    B(p, rho_min/2) by CLIPPING the tile list certified on B(p, 1/8) -- a subset
    of a dead set is dead, so this is sound.
 4. EXACT: Fraction re-certification of every nonzero kept entry, identical tile
    list.  Any failure drops the entry (recorded).

Also emits the FRONTIER: the same table built at each ladder radius rho*, i.e.
keeping only bins with moat >= rho* and charging on B(p, rho*/2).  (The primary
table is rho* = rho_min, per spec; the frontier is diagnostic.)
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
RES = os.path.join(HERE, '..', 'results')
os.makedirs(RES, exist_ok=True)

S0 = F(969271, 250000)
B0 = S0 * S0 - 11                      # 251986271441/62500000000 = 4.031780343056


_CFG = dict(depth_max=34, max_boxes=50000)


def rebuild_bin(rec):
    b = {}
    for k, vv in rec['bins'].items():
        b[k] = tuple(F(v) for v in vv)
    return b


def _exact_job(rec):
    t0 = time.time()
    kind = rec['kind']
    configs = L.build_configs(kind, rebuild_bin(rec), **rec['kw'])
    cells = [tuple(F(v) for v in c) for c in rec['_cells_R']]
    r = L.recert_exact(kind, configs, cells, depth_max=_CFG.get('depth_max', 34),
                       max_boxes=_CFG.get('max_boxes', 50000))
    return dict(id=rec['id'], exact_area=str(r['area']), n_cells=len(cells),
                n_failed=len(r['failed']), failed=r['failed'],
                seconds=round(time.time() - t0, 1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='sweep')
    ap.add_argument('--procs', type=int, default=2)
    ap.add_argument('--out', default=os.path.join(RES, 'charge_table.json'))
    a = ap.parse_args()
    assert a.procs <= 2

    rows = []
    for line in open(os.path.join(WORK, a.tag + '.jsonl')):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    rows.sort(key=lambda r: r['id'])

    vacuous = [r for r in rows if not r['realisable']]
    live = [r for r in rows if r['realisable']]
    kept = [r for r in live if r.get('moat_rho')]
    dropped = [r for r in live if not r.get('moat_rho')]
    assert kept, 'no bin carries a moat'
    rho_min = min(F(r['moat_rho']) for r in kept)
    print(f'{len(rows)} bins: {len(vacuous)} vacuous, {len(dropped)} dropped, '
          f'{len(kept)} kept; rho_min = {rho_min}')

    # ---- frontier (diagnostic) + primary clip
    frontier = {}
    for rho in L.LADDER:
        sel = [r for r in kept if F(r['moat_rho']) >= rho]
        tot = F(0)
        per = {}
        for r in sel:
            px, py = L.CONTACT_P[r['kind']]
            cells = [tuple(F(v) for v in c) for c in r['cells']]
            ar, _ = L.clip_cells(cells, px, py, rho / 2, L.CLIP_Y0[r['kind']])
            per[r['id']] = float(ar)
            tot += ar
        frontier[str(rho)] = dict(R=str(rho / 2), n_bins=len(sel),
                                  max_charge=str(max(per.values())) if per else '0',
                                  mean_charge=float(tot / len(sel)) if sel else 0.0,
                                  per_bin_float=per)

    R = rho_min / 2
    entries = []
    for r in live:
        px, py = L.CONTACT_P[r['kind']]
        e = dict(id=r['id'], type=r['kind'], bins=r['bin'], n_configs=r.get('n_configs'),
                 kw=r['kw'], moat_rho=r.get('moat_rho'),
                 dropped=bool(not r.get('moat_rho')),
                 moat_ladder=[dict(rho=x['rho'], passed=x['passed'],
                                   boxes=x['boxes'], seconds=x['seconds'])
                              for x in r.get('moat_runs', [])],
                 lemma_P_margin=(r.get('moat_runs') or [{}])[-1].get('margin'),
                 lemma_K=r.get('keeper'))
        if e['dropped']:
            e.update(charge='0', charge_float=0.0, R=str(R), regions=[], exact=True,
                     exact_charge='0', exact_failed_cells=0,
                     note='moat fails at 1/16 -> dropped, charge 0 (sound)')
        else:
            cells = [tuple(F(v) for v in c) for c in r['cells']]
            ar, cR = L.clip_cells(cells, px, py, R, L.CLIP_Y0[r['kind']])
            e.update(charge=str(ar), charge_float=float(ar), R=str(R),
                     area_at_Rmax=r.get('area_Rmax'),
                     regions=[[str(c[0] - px), str(c[1] - py), str(c[2] - px),
                               str(c[3] - py)] for c in cR],
                     regions_frame=[[str(v) for v in c] for c in cR],
                     n_regions=len(cR), exact=False)
            e['_cells_R'] = [[str(v) for v in c] for c in cR]
            e['kind'] = r['kind']
        entries.append(e)

    # ---- exact recertification of every nonzero kept entry
    todo = [e for e in entries if not e['dropped'] and F(e['charge']) > 0]
    print(f'exactify {len(todo)} nonzero entries, '
          f'{sum(len(e["_cells_R"]) for e in todo)} tiles', flush=True)
    t0 = time.time()
    ex = {}
    cache = os.path.join(WORK, 'exact_' + a.tag + '.jsonl')
    if os.path.exists(cache):
        for line in open(cache):
            line = line.strip()
            if line:
                res = json.loads(line)
                ex[res['id']] = res
        print(f'  cache: {len(ex)} entries already exact-certified', flush=True)
    todo = [e for e in todo if e['id'] not in ex]
    if todo:
        with open(cache, 'a') as cf, Pool(a.procs) as pool:
            for k, res in enumerate(pool.imap_unordered(_exact_job, todo, chunksize=1)):
                ex[res['id']] = res
                cf.write(json.dumps(res) + '\n')
                cf.flush()
                print(f'  [{k+1}/{len(todo)}] {res["id"]} exact={float(F(res["exact_area"])):.6f} '
                      f'failed={res["n_failed"]} {res["seconds"]}s', flush=True)
    n_exact_fail = 0
    print(f'exact pass: {len(ex)} results, {round(time.time() - t0, 1)}s', flush=True)
    for e in entries:
        e.pop('_cells_R', None)
        e.pop('kind', None)
        if e['id'] in ex:
            res = ex[e['id']]
            e['exact_charge'] = res['exact_area']
            e['exact_failed_cells'] = res['n_failed']
            e['exact'] = (res['n_failed'] == 0)
            if res['n_failed']:
                n_exact_fail += 1
                e['exact_failed'] = res['failed']
                e['dropped'] = True
                e['note'] = 'exact re-certification failed -> entry DROPPED (charge 0)'
                e['charge'], e['charge_float'], e['regions'] = '0', 0.0, []
        elif not e['dropped']:
            e['exact'] = True
            e['exact_charge'] = '0'
            e['exact_failed_cells'] = 0

    out = dict(
        kind='interface', spec='A45 charging calculus (notes/charging_lemma.md)',
        generated=time.strftime('%Y-%m-%d %H:%M'),
        meaning=('per entry: a moat certificate of radius `moat_rho` (no legal unit '
                 'square meets B(p,moat_rho), uniformly over the bin) and a list of '
                 'closed rational rectangles inside B(p,R), R = rho_min/2, each '
                 'certified PLANE-DEAD for the pair uniformly over the bin and each '
                 'inside conv(a cup b) (Lemma K).  `charge` = sum of their areas.  '
                 'Theorem A45.1: over any set of corner-type contacts of one packing, '
                 'the charges of the bins they realise sum to <= s^2 - 11.'),
        convention=dict(
            frames=dict(
                WC='square a, lowest corner at p=(10,0) on the bottom wall of [0,20]^2; '
                   'phi = tilt in (0,45] after the mirror reduction phi ~ 90-phi',
                CE='a lowest corner at p=(10,10), tilt d; b upright, top edge on y=10, '
                   'centre (10-u, 9.5); d in (0,45] and u in [-1/2,1/2] after the '
                   'mirror reduction (d,u) ~ (90-d,-u)',
                CC='NOT TABULATED: at a corner-corner contact the two bodies occupy '
                   '180 deg around p, so one free wedge is >= 90 deg and a legal unit '
                   'square has a corner AT p; the moat fails at every radius.  All CC '
                   'contacts are charged 0 (conservative).'),
            regions=('`regions` are RELATIVE to the contact point p (x-px, y-py); '
                     '`regions_frame` are the same rectangles in the certifier frame'),
            rationals='all numbers are exact rationals as strings'),
        S_big='20', ladder=[str(x) for x in L.LADDER],
        rho_min=str(rho_min), rho_min_float=float(rho_min), R=str(R),
        budget_B0=str(B0), budget_B0_float=float(B0),
        counts=dict(bins=len(rows), vacuous=len(vacuous), dropped_no_moat=len(dropped),
                    kept=len(kept), nonzero=len([e for e in entries
                                                 if not e['dropped'] and F(e['charge']) > 0]),
                    exact_recertified=len(ex), exact_failures=n_exact_fail,
                    exact_seconds=round(time.time() - t0, 1)),
        vacuous_bins=[dict(id=r['id'], type=r['kind'], bins=r['bin'],
                           reason=r.get('note')) for r in vacuous],
        frontier=frontier,
        entries=entries)
    json.dump(out, open(a.out, 'w'), indent=1)
    tot = sum(F(e['charge']) for e in entries)
    print(f'\nwrote {a.out}\n  rho_min={rho_min}  R={R}  '
          f'nonzero entries={out["counts"]["nonzero"]}  '
          f'max charge={max([float(F(e["charge"])) for e in entries]):.6f}  '
          f'sum over all entries={float(tot):.6f}  exact failures={n_exact_fail}')
