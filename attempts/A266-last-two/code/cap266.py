"""A266 CAPACITY-2 measured on the non-ADJ hybrid family (open_pairs.md s.3, strip_plug.md s.3): can TWO
interior-disjoint free squares of a ring BOTH miss O?  Exact per-tilt centre sets (room259), 1-degree grid:
    M(psi) := C(psi) \\ int(O + Q_psi)          the MISS REGION (centres of free squares of tilt psi not containing O)
    cap2   := max over psi1, psi2, over the four edge normals n of the pair, of
              sup_{M(psi2)} <q, n> + sup_{M(psi1)} <q, -n> - h_psi1(n) - h_psi2(n)       (h = the half-extent along n)
cap2 >= 0  <=>  two interior-disjoint free squares both missing O exist at the sampled tilts (SAT along n); every
witness pair is re-checked exactly (free_margin, contains_O, poly_gap) before it is reported.  Rings: (a) A260's
non-ADJ adversary rows, (b) random non-ADJ hybrid rings (geom260.sample_H, adj=False), (c) STRUCTURED wide-gap
starts (one wall with a + b small so that e >= 1; two such walls, opposite / adjacent) improved by a feasible-only
hill-climb on cap2, (d) the ring around A265's FULL-corner witness.   [M]
    python cap266.py [--n 40] [--iters 40] [--step 1.0] [--s 3.8771]  -> results/cap266.json"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from shapely.geometry import Polygon

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for p in ('attempts/A263-open-pairs/code', 'attempts/A260-locked-wall/code', 'attempts/A259-normal-room/code'):
    sys.path.insert(0, os.path.join(ROOT, p))
import geom260 as H                                                   # noqa: E402
import room259 as R                                                   # noqa: E402
Z = H.Z
DEG = Z.DEG
ANG = np.arange(360)                                                  # support directions, degrees


def miss_region(Vs, s, psi):
    C = R.centre_set(Vs, s, psi)
    if C.is_empty:
        return C
    return C.difference(Polygon(Z.sq_verts(s / 2, s / 2, psi)))


def support_table(M):
    """(S[angle], argmax vertex[angle]) of the polygon(s) M over the 360 unit directions."""
    pts = []
    for P in R.polys_of(M):
        pts.append(np.array(P.exterior.coords)[:-1])
        for r in P.interiors:
            pts.append(np.array(r.coords)[:-1])
    if not pts:
        return None
    pts = np.vstack(pts)
    N = np.stack([np.cos(ANG * DEG), np.sin(ANG * DEG)], axis=1)
    D = pts @ N.T
    i = D.argmax(axis=0)
    return D.max(axis=0), pts[i]


def half_extent(n_deg, psi_deg):
    d = (n_deg - psi_deg) * DEG
    return 0.5 * (abs(math.cos(d)) + abs(math.sin(d)))


def cap2(Vs, s, step=1.0):
    """(cap2 margin, witness) -- witness = (pose1, pose2, axis_deg) at the best pair (None if no miss region at all)."""
    psis = np.arange(-45.0, 45.0, step)
    tabs = {}
    for pd in psis:
        t = support_table(miss_region(Vs, s, pd * DEG))
        if t is not None:
            tabs[pd] = t
    best, wit = -9.0, None
    keys = sorted(tabs)
    for i1, p1 in enumerate(keys):
        S1, A1 = tabs[p1]
        for p2 in keys[i1:]:
            S2, A2 = tabs[p2]
            for base in (p1, p2):
                for n in (base, base + 90, base + 180, base + 270):
                    n = int(round(n)) % 360
                    m = int((n + 180) % 360)
                    g = S2[n] + S1[m] - half_extent(n, p1) - half_extent(n, p2)
                    if g > best:
                        best, wit = float(g), ((float(A1[m][0]), float(A1[m][1]), p1 * DEG),
                                               (float(A2[n][0]), float(A2[n][1]), p2 * DEG), n)
    return best, wit


def exact_pair(wit, Vs, s):
    """exact geometry of a witness pair: both free of the ring, in the container, missing O, and interior-disjoint."""
    if wit is None:
        return None
    (a, b, n) = wit
    Qa, Qb = Z.sq_verts(*a), Z.sq_verts(*b)
    return dict(free1=R.free_margin(a, Vs, s), free2=R.free_margin(b, Vs, s), missO1=-R.contains_O(a, s),
                missO2=-R.contains_O(b, s), gap12=Z.poly_gap(Qa, Qb), axis_deg=n)


def structured(rng, s, walls, iters=4000):
    """a non-ADJ hybrid ring with the WIDEST gap the feasible-only local search reaches on the walls of `walls`
    (objective: the least shift over `walls`; HARD feasibility, hyb_margin >= 0 with adj=False)."""
    x = H.sample_H(rng, s, 1, adj=False)[0]

    def obj(y):
        return min(H.shift(*y[4 * k:4 * k + 4], s) for k in walls)
    best = obj(x)
    for it in range(iters):
        sc = 1.0 if it < iters // 2 else 0.3
        y = np.clip(x + rng.normal(size=16) * np.array([0.03, 1.5 * DEG] * 8) * sc, 0.0, None)
        if H.hyb_margin(y, s, adj=False) >= 0 and obj(y) > best:
            x, best = y, obj(y)
    return x, best


def climb(x, s, iters, rng, step):
    """feasible-only random local search maximising cap2 (HARD feasibility: infeasible proposals are rejected)."""
    Vs = H.hyb_verts(x, s)
    best, wit = cap2(Vs, s, step)
    for it in range(iters):
        y = x + rng.normal(size=16) * np.array([0.02, 0.5 * DEG] * 8) * (0.5 if it > iters // 2 else 1.0)
        y = np.clip(y, 0.0, None)
        if H.hyb_margin(y, s, adj=False) < 0:
            continue
        g, w = cap2(H.hyb_verts(y, s), s, step)
        if g > best:
            x, best, wit = y, g, w
    return x, best, wit


def a265_ring(rng, s):
    """the ring around A265's FULL-corner witness (floor: b = 0.994, fW = 14.3 deg, e = 0.1, s1 at W's tilt; right wall:
    a' = 0.490, f1' = 25.5 deg, e' = 0.6, fW' = 38 deg); walls 2, 3 sampled feasible."""
    fW, f1p, fWp = 14.3 * DEG, 25.5 * DEG, 38.0 * DEG
    b, e, ap, ep = 0.994, 0.1, 0.490, 0.6
    a = s - b - H.w_of(fW) - e - 1.0 / math.cos(fW)
    bp = s - (ap + 1.0 / math.cos(f1p) + ep) - H.w_of(fWp)
    head = [a, fW, b, fW, ap, f1p, bp, fWp]
    best, bx = -9.0, None
    for _ in range(3000):                                              # best-of-3000 tail, then a margin climb on walls 2, 3
        x = list(head)
        for k in (2, 3):
            f1 = rng.uniform(0.3, 40.0) * DEG
            fW2 = min(45.0, max(0.3, f1 / DEG + rng.normal() * 4.0)) * DEG
            x += [rng.uniform(0.3, 1.0), f1, rng.uniform(0.3, 1.0), fW2]
        x = np.array(x)
        m = H.hyb_margin(x, s, adj=False)
        if m > best:
            best, bx = m, x
    for it in range(4000):
        if best >= 0:
            return bx
        y = bx.copy()
        y[8:] = np.clip(y[8:] + rng.normal(size=8) * np.array([0.02, 1.0 * DEG] * 4) * (0.3 if it > 2000 else 1.0), 0.0, None)
        m = H.hyb_margin(y, s, adj=False)
        if m > best:
            best, bx = m, y
    print('a265 ring: best margin reached %.4f' % best, flush=True)
    return bx if best >= 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--iters', type=int, default=40)
    ap.add_argument('--step', type=float, default=1.0)
    ap.add_argument('--s', type=float, default=3.8771)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    Z.belownormal()
    rng = np.random.default_rng(a.seed)
    s = a.s
    rows, t0 = [], time.time()

    def record(name, x, s_here, do_climb=False):
        Vs = H.hyb_verts(x, s_here)
        g, w = cap2(Vs, s_here, a.step)
        rec = dict(name=name, s=s_here, x=[float(t) for t in x], shifts=[float(H.shift(*x[4 * k:4 * k + 4], s_here)) for k in range(4)],
                   cap2=g, pair=exact_pair(w, Vs, s_here), climbed=False)
        if do_climb and a.iters > 0:
            y, g2, w2 = climb(x, s_here, a.iters, rng, a.step)
            rec.update(cap2_climbed=g2, x_climbed=[float(t) for t in y], pair_climbed=exact_pair(w2, H.hyb_verts(y, s_here), s_here),
                       shifts_climbed=[H.shift(*y[4 * k:4 * k + 4], s_here) for k in range(4)], climbed=True)
        rows.append(rec)
        print(name, round(s_here, 4), 'cap2 %+.4f' % g, ('climbed %+.4f' % rec['cap2_climbed']) if do_climb else '',
              'shifts', [round(t, 3) for t in rec['shifts']], round(time.time() - t0), 's', flush=True)

    x = a265_ring(rng, s)
    if x is not None:
        record('a265_witness_ring', x, s, True)
    for r in [json.loads(l) for l in open(os.path.join(ROOT, 'attempts', 'A260-locked-wall', 'results', 'adv260.jsonl'))]:
        if not r['adj']:
            record('adv260:' + r['key'], np.array(r['x']), r['s'])
    for walls, tag in (((0,), 'one_gap'), ((0, 2), 'two_gaps_opposite'), ((0, 1), 'two_gaps_adjacent')):
        for j in range(3):
            x, gap = structured(rng, s, walls)
            print('structured', tag, 'least shift reached %.3f' % gap, flush=True)
            record('%s_%d' % (tag, j), x, s, True)
    for j, x in enumerate(H.sample_H(rng, s, a.n, adj=False)):
        record('random_nonadj_%d' % j, x, s)
    worst = max(rows, key=lambda r: max(r['cap2'], r.get('cap2_climbed', -9)))
    json.dump(dict(step=a.step, s=s, n=len(rows), worst=worst, rows=rows),
              open(os.path.join(HERE, '..', 'results', 'cap266.json'), 'w'), indent=1)
    print('WORST', worst['name'], worst['cap2'], worst.get('cap2_climbed'))


if __name__ == '__main__':
    main()
