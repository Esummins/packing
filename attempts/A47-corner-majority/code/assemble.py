#!/usr/bin/env python3
"""A47 leg (b) -- assemble results/primitives_corner.json and
results/primitives_side.json from the work/ checkpoints.

CORNER.  Ships the theta-indexed table (9 position cells x 6 tilt bins,
theta in [0,45]) and the DERIVED delta-indexed table, delta = dist(theta, 90 Z):
the hypothesis "delta in [a,b]" is the UNION of the two theta components
[a,b] and [90-b, 90-a], so its dead set is the INTERSECTION of the two
components' dead sets, and by the container's diagonal symmetry
sigma:(x,y)->(y,x) (which maps (cellA,cellB,theta) to (cellB,cellA,90-theta))
the second component's dead set is the reflection of entry (iy,ix,ib)'s.
The intersection is computed EXACTLY, rectangle by rectangle: every piece is a
subset of a certified dead set of each component, hence dead for the union
hypothesis.

SIDE.  Ships the refined table (3 cx x 7 cy x 3 bins), the min over cy cells
per (cx, bin) -- the number a "the square is somewhere in the side zone" premise
licenses -- and the brief's two COARSE cy cells derived exactly as the
intersection of their refined sub-cells' dead sets.
"""
from __future__ import annotations

import glob
import json
import os
from fractions import Fraction as F

import a47_lib as L
import run_side as RS


def rects(rec):
    return [tuple(F(v) for v in c) for c in rec.get('cells_raw', [])]


def inter_area(A, B):
    """(exact area, tiles) of the intersection of two axis-aligned tile lists."""
    a = F(0)
    out = []
    for (x0, y0, x1, y1) in A:
        for (u0, v0, u1, v1) in B:
            p0, p1 = max(x0, u0), min(x1, u1)
            q0, q1 = max(y0, v0), min(y1, v1)
            if p1 > p0 and q1 > q0:
                a += (p1 - p0) * (q1 - q0)
                out.append((p0, q0, p1, q1))
    return a, out


def reflect(A):
    return [(y0, x0, y1, x1) for (x0, y0, x1, y1) in A]


def load(dirname):
    out = {}
    for p in sorted(glob.glob(os.path.join(L.WORK, dirname, '*.json'))):
        r = json.load(open(p))
        out[(r['ix'], r['iy'], r['ib'])] = r
    return out


def corner():
    E = load('corner')
    theta = []
    for (ix, iy, ib), r in sorted(E.items()):
        theta.append(dict(
            id=r['id'], ix=ix, iy=iy, ib=ib, status=r['status'],
            x_cell=r['x_cell'], y_cell=r['y_cell'], tilt_bin_deg=r['tilt_bin_deg'],
            area_exact=r['area_exact'], area=r['area_float'],
            n_tiles=r['n_tiles'], n_failed=r.get('n_failed', 0),
            feasibility=dict(status=r['feasibility']['feasible'],
                             nsub=r['feasibility']['nsub'],
                             n_kept=r['feasibility']['n_kept'],
                             n_dropped=r['feasibility']['n_dropped'],
                             kept=r['feasibility']['kept'],
                             dropped=r['feasibility']['dropped']),
            radial=r.get('radial', {}), radial_f=r.get('radial_f', {}),
            cells=r.get('cells', []), stats=r.get('stats')))
    delta = []
    for (ix, iy, ib), r in sorted(E.items()):
        s = E.get((iy, ix, ib))
        A, B = rects(r), reflect(rects(s)) if s else []
        if r['status'] == 'INFEASIBLE' or (s and s['status'] == 'INFEASIBLE'):
            a, tiles = F(0), []
            st = 'INFEASIBLE'
        else:
            a, tiles = inter_area(A, B)
            st = 'OK'
        delta.append(dict(id='D_' + r['id'][2:], ix=ix, iy=iy, ib=ib, status=st,
                          x_cell=r['x_cell'], y_cell=r['y_cell'],
                          delta_bin_deg=r['tilt_bin_deg'],
                          area_exact=str(a), area=float(a), n_tiles=len(tiles),
                          radial={k: str(v) for k, v in
                                  L.radial_corner(tiles).items()},
                          radial_f={k: float(v) for k, v in
                                    L.radial_corner(tiles).items()},
                          components=[r['id'], (s or r)['id'] + ' (sigma-image)']))
    ok = [e for e in theta if e['status'] == 'OK']
    out = dict(
        what='A47 leg (b) TABLE (i): CORNER primitive table',
        frame=dict(container='[0, s0]^2', s0=str(L.S0), B0=str(L.B0),
                   corner='origin', window='[0, 13/8]^2',
                   cell0=str(L.CELL0), min_cell=str(L.MIN_CELL),
                   position_box='[49/100, 11/10]^2 (A21 corner zone, enlarged '
                                'to cover the s0/3.88 scale-back)',
                   x_cells=[[str(a), str(b)] for (a, b) in L.XCELLS],
                   tilt_bins_deg=[[str(a), str(b)] for (a, b) in L.CORNER_BINS],
                   semantics='PlacedBox bin-uniform: every certificate holds for '
                             'EVERY placement of (cell x bin); tiles must be '
                             'interior-disjoint from every placement; undecided '
                             'tiles at min_cell are dropped => LOWER bound',
                   exactness='float map for search, identical tile list '
                             're-certified in pure Fractions; only exact shipped'),
        n_entries=len(theta),
        n_infeasible=sum(1 for e in theta if e['status'] == 'INFEASIBLE'),
        min_area=min((e['area'] for e in ok), default=None),
        max_area=max((e['area'] for e in ok), default=None),
        near_flush=next((e for e in theta if e['id'] == 'C_x0_x0_b0_1'), None),
        total_failed_tiles=sum(e['n_failed'] for e in theta),
        table_theta=theta, table_delta=delta)
    L.save(os.path.join(L.RES, 'primitives_corner.json'), out)
    return out


def side():
    E = load('side')
    ent = []
    for (ix, iy, ib), r in sorted(E.items()):
        ent.append(dict(
            id=r['id'], ix=ix, iy=iy, ib=ib, status=r['status'],
            x_cell=r['x_cell'], y_cell=r['y_cell'],
            tilt_bin_deg=r['tilt_bin_deg'], window=r.get('window'),
            area_exact=r['area_exact'], area=r['area_float'],
            n_tiles=r['n_tiles'], n_failed=r.get('n_failed', 0),
            feasibility=dict(status=r['feasibility']['feasible'],
                             nsub=r['feasibility']['nsub'],
                             n_kept=r['feasibility']['n_kept'],
                             n_dropped=r['feasibility']['n_dropped'],
                             kept=r['feasibility']['kept'],
                             dropped=r['feasibility']['dropped']),
            radial=r.get('radial', {}), radial_f=r.get('radial_f', {}),
            cells=r.get('cells', []), stats=r.get('stats')))
    zone_min = []
    for ix in range(3):
        for ib in range(3):
            vs = [e for e in ent if e['ix'] == ix and e['ib'] == ib]
            if not vs:
                continue
            m = min(vs, key=lambda e: F(e['area_exact']))
            zone_min.append(dict(ix=ix, ib=ib, x_cell=m['x_cell'],
                                 tilt_bin_deg=m['tilt_bin_deg'],
                                 min_area_exact=m['area_exact'],
                                 min_area=m['area'], argmin=m['id'],
                                 n_cells=len(vs)))
    coarse = []
    for ix in range(3):
        for ib in range(3):
            for cname, idxs in RS.COARSE.items():
                sets = [rects(E[(ix, j, ib)]) for j in idxs if (ix, j, ib) in E]
                if len(sets) != len(idxs):
                    continue
                cur = sets[0]
                a = sum((x1 - x0) * (y1 - y0) for (x0, y0, x1, y1) in cur)
                for nxt in sets[1:]:
                    a, cur = inter_area(cur, nxt)
                coarse.append(dict(
                    ix=ix, ib=ib, coarse=cname,
                    x_cell=[str(L.XCELLS[ix][0]), str(L.XCELLS[ix][1])],
                    y_cell=([str(F(109, 100)), str(F(9, 5))] if cname == 'Y0'
                            else [str(F(9, 5)), str(F(139, 50))]),
                    tilt_bin_deg=[str(L.SIDE_BINS[ib][0]),
                                  str(L.SIDE_BINS[ib][1])],
                    area_exact=str(a), area=float(a), n_tiles=len(cur),
                    derivation='exact intersection of the refined sub-cell dead '
                               'sets (coarse hypothesis = union of sub-cell '
                               'hypotheses)'))
    ok = [e for e in ent if e['status'] == 'OK']
    out = dict(
        what='A47 leg (b) TABLE (ii): SIDE (left-wall) primitive table',
        frame=dict(container='[0, s0]^2', s0=str(L.S0), wall='x = 0',
                   window='[0, 13/8] x [cy_cell +- 13/8] cap container',
                   cell0=str(L.CELL0), min_cell=str(L.MIN_CELL),
                   position_box='[49/100, 11/10] x [109/100, 139/50] '
                                '(A21 side zone, enlarged for the s0/3.88 '
                                'scale-back)',
                   x_cells=[[str(a), str(b)] for (a, b) in L.XCELLS],
                   y_cells_refined=[[str(a), str(b)] for (a, b) in RS.YCELLS],
                   y_cells_coarse_brief=[['109/100', '9/5'], ['9/5', '139/50']],
                   tilt_bins_deg=[[str(a), str(b)] for (a, b) in L.SIDE_BINS],
                   work_budget=RS.WORK_BUDGET),
        n_entries=len(ent),
        min_area=min((e['area'] for e in ok), default=None),
        max_area=max((e['area'] for e in ok), default=None),
        total_failed_tiles=sum(e['n_failed'] for e in ent),
        table_refined=ent, zone_min_per_cx_bin=zone_min,
        table_coarse_brief_cells=coarse)
    L.save(os.path.join(L.RES, 'primitives_side.json'), out)
    return out


if __name__ == '__main__':
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('both', 'corner'):
        c = corner()
        print('corner: %d entries, %d infeasible, min=%s max=%s, failed tiles=%d'
              % (c['n_entries'], c['n_infeasible'], c['min_area'], c['max_area'],
                 c['total_failed_tiles']))
        nf = c['near_flush']
        if nf:
            print('  NEAR-FLUSH C_x0_x0_b0_1 = %s (%s tiles)'
                  % (nf['area'], nf['n_tiles']))
    if which in ('both', 'side'):
        s = side()
        print('side: %d entries, min=%s max=%s, failed tiles=%d'
              % (s['n_entries'], s['min_area'], s['max_area'],
                 s['total_failed_tiles']))
