#!/usr/bin/env python3
"""Assemble results/w_wc_table.json from the float + exact work files."""
import json
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
W = os.path.join(A46, 'work')
R = os.path.join(A46, 'results')

B0 = F(969271, 250000) ** 2 - 11


def main():
    fl = {e['id']: e for e in json.load(
        open(os.path.join(W, 'wc_float_all.json')))['entries']}
    ex = {}
    for f in ('wc_exact_A.json', 'wc_exact_B.json', 'wc_exact_C.json'):
        p = os.path.join(W, f)
        if os.path.exists(p):
            for e in json.load(open(p))['entries']:
                ex[e['id']] = e
    out = []
    for i, e in sorted(fl.items(), key=lambda kv: F(kv[1]['bin'][0])):
        x = ex.get(i)
        rec = dict(id=i, type='WC', bin=e['bin'],
                   bin_deg=[float(F(e['bin'][0])), float(F(e['bin'][1]))],
                   n_configs=e['nsub'], kw=dict(nsub=e['nsub'],
                                                cell0=e['cell0'],
                                                min_cell=e['min_cell']),
                   window=e['window'], realisable=e['realisable'],
                   realisable_detail=e['realisable_detail'],
                   lemma_P_margin=e['stats']['margin'],
                   lemma_K=e['stats']['keeper'],
                   map_stats={k: v for k, v in e['stats'].items()
                              if k not in ('margin', 'keeper')})
        if x is not None:
            rec.update(status='exact',
                       w_WC=x['area_exact'], w_WC_float=x['area_exact_f'],
                       radial_profile=x['radial_exact'],
                       radial_profile_float=x['radial_exact_f'],
                       n_tiles=x['n_tiles'], n_failed_exact=x['n_failed_exact'],
                       exact_seconds=x['exact_seconds'],
                       area_float_pass=e['area_float'],
                       cells=x['cells'])
        elif e['area_float'] == '0':
            rec.update(status='exact (vacuous: 0 certified tiles)',
                       w_WC='0', w_WC_float=0.0,
                       radial_profile=e['radial_float'],
                       radial_profile_float=e['radial_float_f'],
                       n_tiles=0, n_failed_exact=0, cells=[])
        else:
            rec.update(status='float-preliminary',
                       w_WC=e['area_float'], w_WC_float=e['area_float_f'],
                       radial_profile=e['radial_float'],
                       radial_profile_float=e['radial_float_f'],
                       n_tiles=len(e['cells']), cells=e['cells'])
        out.append(rec)

    tab = dict(
        kind='wall-corner dead-region table (A46 task 2)',
        spec='attempts/A46-balanced-wedge/BRIEF.md (W2 task 2)',
        meaning=(
            'w_WC(phi) is a CERTIFIED LOWER BOUND, uniform over the phi-bin, on '
            'the area of a set that is (i) dead for the single tilted square '
            'whose corner touches the wall at p (A23 deadness, plane mode via '
            'Lemma P/P\'), (ii) interior-disjoint from that square, and (iii) '
            'contained in slab(wall, along-wall bbox of the square) x [0, cos+sin] '
            '(Lemma K).  By A23 Lemma 2 the areas of pairwise interior-disjoint '
            'such sets add against the budget s^2 - 11.  NO MOAT and NO rho_min '
            'clip: this is the FULL dead region of the wedge pair inside the '
            'Lemma-K slab, unlike A45\'s ownership charge.'),
        convention=dict(
            frame='A45 WC frame: big container S = 20, square corner at p = (10,0) '
                  'on the bottom wall, tilt phi in the bin, D4-reduced to (0,45]',
            bin_uniformity='nsub tilt sub-boxes, PlacedBox core-box-uniform, '
                           'outward-rounded rational (cos,sin) hulls',
            window='x in [10-13/8, 10+13/8], y in [0, 5/4] (>= the brief 1.6/1.2)',
            resolution='cell0 = 1/8 quadtree down to min_cell = 1/64; undecided '
                       'tiles DROPPED (lower bound)',
            lemma_K='slab test, a45_lib.keeper_wc verbatim; tiles outside the '
                    'slab are dropped, which is what makes the entry '
                    'container-independent and along-wall composable',
            radial_profile='exact area of the certified tiles within SUP-distance '
                           'r of p (tiles clipped exactly), r in 1/8..13/8'),
        S_big='20', budget_B0=str(B0), budget_B0_float=float(B0),
        n_bins=len(out),
        n_exact=sum(1 for r in out if r['status'].startswith('exact')),
        total_tiles=sum(r['n_tiles'] for r in out),
        total_failed_exact=sum(r.get('n_failed_exact', 0) for r in out),
        max_w_WC=max(r['w_WC_float'] for r in out),
        entries=out)
    p = os.path.join(R, 'w_wc_table.json')
    json.dump(tab, open(p, 'w'), indent=1)
    print('| phi bin (deg) | w_WC exact | status | tiles | max reach (sup r) |')
    print('|---|---|---|---|---|')
    for r in out:
        rp = r['radial_profile_float']
        reach = min([k for k in ('1/8', '1/4', '1/2', '3/4', '1', '8/5', '13/8')
                     if abs(rp[k] - r['w_WC_float']) < 1e-15] or ['13/8'])
        print('| (%g,%g] | %s = %.6f | %s | %d | %s |'
              % (r['bin_deg'][0], r['bin_deg'][1], r['w_WC'], r['w_WC_float'],
                 r['status'], r['n_tiles'], reach))
    print('\nmax w_WC = %.6f ; 12 x max = %.6f ; B0 = %.6f'
          % (tab['max_w_WC'], 12 * tab['max_w_WC'], float(B0)))
    print('->', p)


if __name__ == '__main__':
    main()
