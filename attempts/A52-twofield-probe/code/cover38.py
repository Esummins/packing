#!/usr/bin/env python3
"""
A38 level-1 cover at s0 = 969271/250000 (design.md "Base machinery").

A24's scheme, re-instantiated at s0 with EXACT rationals:

  root zone     Z = [1/2 + CW, s0 - 1/2 - CW]^2,  CW = 3/5      (D4-invariant: Z and [0,s0]^2
                share the centre m = s0/2)
  fundamental   T = { (x, y) : m <= y <= x <= m + h },  h = (b - a)/2 = 419271/500000
  triangle      (T is one of the 8 D4 sectors of Z; the 8 images tile Z)
  level 1       8 x 8 grid on [m, m+h]^2 keeping the cells (i, j) with j <= i (36 position cells,
                diagonal cells kept WHOLE) x 6 theta windows of 15 deg = 216 nodes, budget 10.
                Cell half-widths: h/16 = 419271/8000000 = 0.052408875 in x and y, 7.5 deg in theta.

The machine check (exact rationals, no floats in the verdict):
  C1  the theta cuts 90k/6 partition [0, 90];
  C2  the position cuts m + h*i/8 are strictly increasing from m to m + h = b;
  C3  every (i, j) with j <= i is present for every theta window, and none is vacuous
      (=> the 36 cells cover T: for (x,y) in T the index of y is <= the index of x);
  C4  the 8 D4 images of T cover Z: the 8 sectors of Z about m tile it (their exact areas sum to
      area(Z) = 4h^2 and their interiors are pairwise disjoint by construction), and for each
      sector an explicit element of D4 maps its three vertices into T (D4 acts affinely, T is
      convex, hence the whole sector maps into T).
  C5  theta bookkeeping: rotations fix theta mod 90, reflections map theta -> 90 - theta; since
      every position cell carries ALL SIX theta windows (a partition of [0,90]), the D4 transport
      is theta-closed.

  python cover38.py            # writes ../results/cover_l1.json
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from caselp import Box                      # noqa: E402
import fieldcut as fc                       # noqa: E402

S0 = fc.S0                                  # 969271/250000
CW = F(3, 5)
NX = 8
NTH = 6
BUDGET = 10
OUT = os.path.join(HERE, "..", "results", "cover_l1.json")


def geometry(s=S0, cw=CW):
    a = F(1, 2) + cw
    b = s - F(1, 2) - cw
    m = (a + b) / 2                     # == s/2
    h = (b - a) / 2
    return a, b, m, h


def cells(s=S0, cw=CW, nx=NX, nth=NTH):
    """The 216 level-1 cells, with EXACT rational bounds (and their float mirrors)."""
    a, b, m, h = geometry(s, cw)
    gc = [m + h * F(i, nx) for i in range(nx + 1)]
    cuts = [F(90 * k, nth) for k in range(nth + 1)]
    out = []
    for i in range(nx):
        for j in range(i + 1):
            for k in range(nth):
                out.append(dict(i=i, j=j, k=k,
                                x0=gc[i], x1=gc[i + 1], y0=gc[j], y1=gc[j + 1],
                                th0=cuts[k], th1=cuts[k + 1]))
    for n, c in enumerate(out):
        c['idx'] = n
    return out, dict(a=a, b=b, m=m, h=h, gc=gc, cuts=cuts)


def to_box(c):
    return Box(float(c['x0']), float(c['x1']), float(c['y0']), float(c['y1']),
               float(c['th0']), float(c['th1']))


# ---------------------------------------------------------------------------- D4 on (u, v) = p - m
D4 = [("e",       lambda u, v: (u, v)),
      ("r90",     lambda u, v: (-v, u)),
      ("r180",    lambda u, v: (-u, -v)),
      ("r270",    lambda u, v: (v, -u)),
      ("mx",      lambda u, v: (-u, v)),
      ("my",      lambda u, v: (u, -v)),
      ("d",       lambda u, v: (v, u)),
      ("ad",      lambda u, v: (-v, -u))]


def _tri_area(P):
    (x0, y0), (x1, y1), (x2, y2) = P
    return abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / 2


def check_cover(s=S0, cw=CW, nx=NX, nth=NTH):
    a, b, m, h = geometry(s, cw)
    cs, geo = cells(s, cw, nx, nth)
    gc, cuts = geo['gc'], geo['cuts']

    # C1 theta partition
    c1 = (cuts[0] == 0 and cuts[-1] == 90 and all(cuts[k] < cuts[k + 1] for k in range(nth)))
    # C2 position cuts
    c2 = (gc[0] == m and gc[-1] == b and all(gc[i] < gc[i + 1] for i in range(nx)))
    # C3 all cells present + none vacuous
    have = {(c['i'], c['j'], c['k']) for c in cs}
    want = {(i, j, k) for i in range(nx) for j in range(i + 1) for k in range(nth)}
    c3 = (have == want) and len(cs) == nx * (nx + 1) // 2 * nth
    vac = [c['idx'] for c in cs if to_box(c).vacuous(float(s)) or to_box(c).core() is None]
    c3 = c3 and not vac

    # C4 the 8 D4 sectors of Z tile it, and each maps into T
    P = [(h, F(0)), (h, h), (F(0), h), (-h, h), (-h, F(0)), (-h, -h), (F(0), -h), (h, -h)]
    sectors = [[(F(0), F(0)), P[i], P[(i + 1) % 8]] for i in range(8)]
    area_sum = sum(_tri_area(S) for S in sectors)
    c4_area = (area_sum == 4 * h * h)                       # == area(Z)

    def in_T(u, v):                                          # T in (u,v) coords: 0 <= v <= u <= h
        return (0 <= v) and (v <= u) and (u <= h)

    sector_g, c4_map = [], True
    for S in sectors:
        found = None
        for name, g in D4:
            if all(in_T(*g(u, v)) for (u, v) in S):
                found = name
                break
        sector_g.append(found)
        c4_map = c4_map and (found is not None)
    c4 = bool(c4_area and c4_map)

    # C5 every position cell carries all nth theta windows
    bycell = {}
    for c in cs:
        bycell.setdefault((c['i'], c['j']), set()).add(c['k'])
    c5 = all(v == set(range(nth)) for v in bycell.values()) and len(bycell) == nx * (nx + 1) // 2

    return dict(
        theta_partition=c1, grid_partition=c2, all_cells_present=c3,
        d4_images_cover_Z=c4, d4_sector_areas_exact=str(area_sum), d4_sector_maps=sector_g,
        theta_closed_under_D4=c5, vacuous_cells=vac,
        n_cells=len(cs), Z=[str(a), str(b)], m=str(m), h=str(h),
        cell_half_width=str(h / (2 * nx)), cell_half_theta_deg=str(F(90, 2 * nth)),
        ok=bool(c1 and c2 and c3 and c4 and c5))


def build(s=S0, cw=CW, nx=NX, nth=NTH, out=OUT):
    cs, geo = cells(s, cw, nx, nth)
    chk = check_cover(s, cw, nx, nth)
    obj = dict(
        format="A38-level1-cover-v1",
        s=str(s), s_float=float(s), CW=str(cw), nx=nx, nth=nth, budget=BUDGET,
        zone_Z=dict(lo=str(geo['a']), hi=str(geo['b']),
                    claim="Z = [1/2+CW, s0-1/2-CW]^2, D4-invariant about m = s0/2"),
        triangle_T=dict(m=str(geo['m']), h=str(geo['h']),
                        claim="T = {(x,y): m <= y <= x <= m+h}; the 8 D4 images of T cover Z"),
        cover_check=chk,
        cuts=dict(x=[str(g) for g in geo['gc']], theta_deg=[str(c) for c in geo['cuts']]),
        nodes=[dict(idx=c['idx'], i=c['i'], j=c['j'], k=c['k'],
                    exact=dict(x0=str(c['x0']), x1=str(c['x1']), y0=str(c['y0']), y1=str(c['y1']),
                               th0=str(c['th0']), th1=str(c['th1'])),
                    box=to_box(c).to_json()) for c in cs])
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        json.dump(obj, open(out, 'w'), indent=1)
    return obj


def load_boxes(path=OUT):
    d = json.load(open(path))
    return [Box.from_json(n['box']) for n in d['nodes']], d


def centre_cell_idx(path=None):
    """Index of the triangle cell nearest the container centre (i = j = 0 corner of T)."""
    cs, geo = cells()
    m = geo['m']
    best, bi = None, None
    for c in cs:
        if c['k'] != 0:
            continue
        d = abs((c['x0'] + c['x1']) / 2 - m) + abs((c['y0'] + c['y1']) / 2 - m)
        if best is None or d < best:
            best, bi = d, (c['i'], c['j'])
    return bi


if __name__ == '__main__':
    o = build()
    print(json.dumps(o['cover_check'], indent=1))
    print("nodes: %d -> %s" % (len(o['nodes']), os.path.abspath(OUT)))
    assert o['cover_check']['ok'], o['cover_check']
