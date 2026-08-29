#!/usr/bin/env python3
"""print the md tables for results/primitives_report.md"""
import json
import os
from fractions import Fraction as F

import a47_lib as L
import run_side as RS

C = json.load(open(os.path.join(L.RES, 'primitives_corner.json')))
CT = {(e['ix'], e['iy'], e['ib']): e for e in C['table_theta']}
DT = {(e['ix'], e['iy'], e['ib']): e for e in C['table_delta']}
XN = ['[.49,.7]', '[.7,.9]', '[.9,1.1]']
BN = ['[0,1]', '(1,5]', '(5,15]', '(15,30]', '(30,40]', '(40,45]']


def cell(e):
    if e is None:
        return ' - '
    if e['status'] == 'INFEASIBLE':
        return '**INF**'
    return '%.4f' % e['area']


print('### corner, theta-indexed (rows = cx-cell x cy-cell, cols = tilt bin)\n')
print('| cx / cy | ' + ' | '.join(BN) + ' |')
print('|---' * 7 + '|')
for ix in range(3):
    for iy in range(3):
        print('| %s x %s | ' % (XN[ix], XN[iy])
              + ' | '.join(cell(CT.get((ix, iy, ib))) for ib in range(6)) + ' |')
print()
print('### corner, delta-indexed (delta = dist(theta,90Z); derived exactly)\n')
print('| cx / cy | ' + ' | '.join(BN) + ' |')
print('|---' * 7 + '|')
for ix in range(3):
    for iy in range(3):
        print('| %s x %s | ' % (XN[ix], XN[iy])
              + ' | '.join(cell(DT.get((ix, iy, ib))) for ib in range(6)) + ' |')
print()
print('### corner radial profile (theta-table, sup-distance r from the corner)\n')
print('| entry | area | r=1/2 | 3/4 | 1 | 5/4 | 13/8 |')
print('|---|---|---|---|---|---|---|')
for key in [(0, 0, 4), (1, 1, 3), (1, 1, 5), (2, 2, 3), (2, 2, 5), (1, 2, 4)]:
    e = CT.get(key)
    if not e or e['status'] != 'OK' or not e['radial_f']:
        continue
    r = e['radial_f']
    print('| %s | %.4f | %s |' % (e['id'], e['area'],
                                  ' | '.join('%.4f' % r[k] for k in
                                             ('1/2', '3/4', '1', '5/4', '13/8'))))
p = os.path.join(L.RES, 'primitives_side.json')
if os.path.exists(p):
    S = json.load(open(p))
    ST = {(e['ix'], e['iy'], e['ib']): e for e in S['table_refined']}
    YN = ['%.2f-%.2f' % (float(a), float(b)) for (a, b) in RS.YCELLS]
    SB = ['[0,1]', '(1,15]', '(15,45]']
    print('\n### side, refined (rows = cy cell; blocks = tilt bin; cols = cx cell)\n')
    print('| cy cell | ' + ' | '.join('%s %s' % (SB[ib], XN[ix])
                                      for ib in range(3) for ix in range(3)) + ' |')
    print('|---' * 10 + '|')
    for iy in range(len(RS.YCELLS)):
        print('| %s | ' % YN[iy] + ' | '.join(
            cell(ST.get((ix, iy, ib))) for ib in range(3) for ix in range(3)) + ' |')
    print('\n### side, zone minima and the brief\'s coarse cells\n')
    print('| cx cell | tilt bin | min over cy cells | argmin | coarse Y0 | coarse Y1 |')
    print('|---|---|---|---|---|---|')
    co = {(c['ix'], c['ib'], c['coarse']): c for c in
          S['table_coarse_brief_cells']}
    for z in S['zone_min_per_cx_bin']:
        y0 = co.get((z['ix'], z['ib'], 'Y0'))
        y1 = co.get((z['ix'], z['ib'], 'Y1'))
        print('| %s | %s | %.4f | %s | %s | %s |'
              % (XN[z['ix']], SB[z['ib']], z['min_area'], z['argmin'],
                 ('%.4f' % y0['area']) if y0 else '-',
                 ('%.4f' % y1['area']) if y1 else '-'))
    print('\n### side radial profile (area with x <= r), strongest entries\n')
    print('| entry | area | r=1/2 | 3/4 | 1 | 5/4 | 13/8 |')
    print('|---|---|---|---|---|---|---|')
    best = sorted([e for e in S['table_refined'] if e['status'] == 'OK'],
                  key=lambda e: -e['area'])[:5]
    for e in best:
        r = e['radial_f']
        print('| %s | %.4f | %s |' % (e['id'], e['area'],
                                      ' | '.join('%.4f' % r[k] for k in
                                                 ('1/2', '3/4', '1', '5/4', '13/8'))))
