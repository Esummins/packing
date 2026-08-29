#!/usr/bin/env python3
"""A46 task 4 -- CE + CC pilot (float; magnitude only) + the Lemma-K cost probe.

CE frame = A45's (a's lowest corner at p = (10,10) with tilt d; b upright, top
edge on y = 10, centre (10-u, 9.5)).  Unlike A45's charge map we use the FULL
window B_inf(p, 5/4) (>= the brief's 1.2) and keep BOTH wedges.
CC frame = A45's (a = [10,11]^2, b's cone [delta, delta+90], delta in [90,180];
relative mismatch = delta - 90 reduced mod 90, so delta = 180 is the ALIGNED
diagonal corner-corner that the whole genuine atlas realises).

`--probe wc` additionally maps a WC bin with NO Lemma-K keeper, to price what
the slab containment costs (needed for the honest 'max conceivable' ceiling).
"""
from __future__ import annotations

import argparse
import json
import os
from fractions import Fraction as F

import a45_lib as L
import a46_lib as A

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
RW = F(5, 4)                       # window half-width (>= the brief's 1.2)

CE_BINS = [(F(2), F(5)), (F(18), F(21)), (F(39), F(42))]
U_BIN = (F(-1, 4), F(1, 4))        # the middle slide bin
CC_BINS = [(F(177), F(180)), (F(110), F(120))]
CC_BINS2 = [(F(170), F(177)), (F(160), F(170)), (F(135), F(145))]


def ce_run(d0, d1, nsub, nsub_u, cell0, min_cell, wb, log):
    b = dict(d=(d0, d1), u=U_BIN)
    cfgs = L.build_configs('CE', b, nsub=nsub, nsub_u=nsub_u)
    ok, det = L.realisable('CE', b)
    keep = A.hull_keeper(cfgs, 'CE')
    win = (L.PX - RW, L.PY - RW, L.PX + RW, L.PY + RW)
    r = A.window_map('CE', cfgs, win, cell0=cell0, min_cell=min_cell,
                     mode='float', keeper=keep, work_budget=wb)
    prof = A.radial_profile(r['cells'], (L.PX, L.PY),
                            [F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(1), RW])
    log('  CE d=(%s,%s] u=%s : area=%s (%.6f)  %ss  cfgs=%d pass=%d drop=%d'
        % (d0, d1, U_BIN, r['area'], float(r['area']), r['stats']['seconds'],
           len(cfgs), r['stats']['n_pass'], r['stats']['n_drop']))
    return dict(id='CE_%s_%s' % (d0, d1), type='CE',
                bin=dict(d=[str(d0), str(d1)], u=[str(v) for v in U_BIN]),
                n_configs=len(cfgs), nsub=nsub, nsub_u=nsub_u,
                cell0=str(cell0), min_cell=str(min_cell),
                window=[str(v) for v in win],
                realisable=bool(ok), realisable_detail=det,
                area_float=str(r['area']), area_float_f=float(r['area']),
                radial_float={k: str(v) for k, v in prof.items()},
                radial_float_f={k: float(v) for k, v in prof.items()},
                lemma_K=r['stats']['keeper'], lemma_P_margin=r['stats']['margin'],
                stats={k: v for k, v in r['stats'].items()
                       if k not in ('keeper', 'margin')},
                cells=L.jcells(r['cells']), exact=False)


def cc_run(d0, d1, nsub, cell0, min_cell, wb, log):
    b = dict(delta=(d0, d1))
    cfgs = L.build_configs('CC', b, nsub=nsub)
    ok, det = L.realisable('CC', b)
    keep = A.hull_keeper(cfgs, 'CC')
    win = (L.PX - RW, L.PY - RW, L.PX + RW, L.PY + RW)
    r = A.window_map('CC', cfgs, win, cell0=cell0, min_cell=min_cell,
                     mode='float', keeper=keep, work_budget=wb)
    prof = A.radial_profile(r['cells'], (L.PX, L.PY),
                            [F(1, 8), F(1, 4), F(1, 2), F(3, 4), F(1), RW])
    mis = [float((x - 90) % 90) for x in (d0, d1)]
    log('  CC delta=(%s,%s] (mismatch %s): area=%s (%.6f)  %ss  pass=%d'
        % (d0, d1, mis, r['area'], float(r['area']), r['stats']['seconds'],
           r['stats']['n_pass']))
    return dict(id='CC_%s_%s' % (d0, d1), type='CC',
                bin=dict(delta=[str(d0), str(d1)]), mismatch_deg=mis,
                n_configs=len(cfgs), nsub=nsub, cell0=str(cell0),
                min_cell=str(min_cell), window=[str(v) for v in win],
                realisable=bool(ok), realisable_detail=det,
                area_float=str(r['area']), area_float_f=float(r['area']),
                radial_float={k: str(v) for k, v in prof.items()},
                radial_float_f={k: float(v) for k, v in prof.items()},
                lemma_K=r['stats']['keeper'], lemma_P_margin=r['stats']['margin'],
                stats={k: v for k, v in r['stats'].items()
                       if k not in ('keeper', 'margin')},
                cells=L.jcells(r['cells']), exact=False)


def wc_probe(lo, hi, nsub, cell0, min_cell, wb, log):
    """WC bin mapped with NO Lemma-K keeper: the intrinsic plane-dead area."""
    cfgs = L.build_configs('WC', dict(phi=(lo, hi)), nsub=nsub)
    win = (L.PX - F(13, 8), F(0), L.PX + F(13, 8), F(5, 4))
    r = A.window_map('WC', cfgs, win, cell0=cell0, min_cell=min_cell,
                     mode='float', keeper=L._always, work_budget=wb)
    log('  WC-noK phi=(%s,%s]: area=%s (%.6f)  %ss  pass=%d'
        % (lo, hi, r['area'], float(r['area']), r['stats']['seconds'],
           r['stats']['n_pass']))
    return dict(id='WCnoK_%s_%s' % (lo, hi), type='WC-no-lemmaK',
                bin=[str(lo), str(hi)], nsub=nsub,
                area_float=str(r['area']), area_float_f=float(r['area']),
                note='diagnostic only: NOT container-independent, NOT usable in '
                     'a composed budget; prices what the Lemma-K slab costs',
                stats={k: v for k, v in r['stats'].items()
                       if k not in ('keeper', 'margin')}, exact=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--what', default='ce', choices=['ce', 'cc', 'cc2', 'probe'])
    ap.add_argument('--nsub', type=int, default=4)
    ap.add_argument('--nsub_u', type=int, default=4)
    ap.add_argument('--cell0', default='1/8')
    ap.add_argument('--min_cell', default='1/64')
    ap.add_argument('--work_budget', type=int, default=400000)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    lf = open(a.out + '.log', 'w')

    def log(m):
        print(m, flush=True)
        lf.write(m + '\n')
        lf.flush()
    out = []
    c0, mc = F(a.cell0), F(a.min_cell)
    if a.what == 'ce':
        for (d0, d1) in CE_BINS:
            out.append(ce_run(d0, d1, a.nsub, a.nsub_u, c0, mc,
                              a.work_budget, log))
            json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    elif a.what in ('cc', 'cc2'):
        for (d0, d1) in (CC_BINS if a.what == 'cc' else CC_BINS2):
            out.append(cc_run(d0, d1, a.nsub, c0, mc, a.work_budget, log))
            json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    else:
        for (lo, hi) in [(F(40), F(45)), (F(20), F(25)), (F(2), F(5))]:
            out.append(wc_probe(lo, hi, a.nsub, c0, mc, a.work_budget, log))
            json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    json.dump(dict(entries=out), open(a.out, 'w'), indent=1)
    log('wrote %s' % a.out)


if __name__ == '__main__':
    main()
