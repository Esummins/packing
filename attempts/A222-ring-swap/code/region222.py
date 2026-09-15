"""A222 region-constrained placement: pack k unit squares inside U(X) = container minus the interiors of the
FIXED squares (the untouched squares of the witness plus the settled slot squares), interior-disjoint from
them and from each other.  One square: exact configuration space per tilt (shapely: container shrunk by the
square's axis half-width minus the Minkowski sums obstacle (+) square), the pole of inaccessibility as the
placement.  k squares: greedy beam over tilts (largest clearance first), then a penalty polish with a margin,
then the lab's exact check (geom217 SAT gaps and wall rows >= -1e-9 on the composed 11-square configuration).
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from shapely.geometry import Polygon, MultiPolygon, box as sbox
from shapely.ops import unary_union
from shapely.algorithms.polylabel import polylabel

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import geom217 as G          # noqa: E402

TOL = 1e-9
MARGIN = 2e-7


def sq_verts(cx, cy, th):
    c, d = math.cos(th), math.sin(th)
    return [(cx + c * x - d * y, cy + d * x + c * y) for x, y in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]


def w_of(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def cspace(fixed, s, th):
    """feasible centres (closed region, as a shapely polygon) of a unit square of tilt th that lies in the
    container and is interior-disjoint from every fixed square (list of (cx, cy, th))."""
    h = w_of(th) / 2
    if s - 2 * h < 0:
        return Polygon()
    region = sbox(h, h, s - h, s - h)
    q0 = sq_verts(0.0, 0.0, th)
    sums = []
    for (fx, fy, ft) in fixed:
        fv = sq_verts(fx, fy, ft)
        pts = [(a[0] + b[0], a[1] + b[1]) for a in fv for b in q0]
        sums.append(Polygon(pts).convex_hull)
    if sums:
        region = region.difference(unary_union(sums))
    return region


def best_point(region):
    """the point of the region farthest from its boundary (pole of inaccessibility) and that distance."""
    if region.is_empty or region.area < 1e-12:
        return None, 0.0
    polys = list(region.geoms) if isinstance(region, MultiPolygon) else [region]
    best, bd = None, -1.0
    for p in polys:
        if p.area < 1e-12:
            continue
        pt = polylabel(p, tolerance=1e-4)
        d = p.exterior.distance(pt)
        for ring in p.interiors:
            d = min(d, ring.distance(pt))
        if d > bd:
            best, bd = (pt.x, pt.y), d
    return best, bd


def candidates(fixed, s, thetas, top=3):
    """per tilt the pole of the feasible region; the `top` placements by clearance."""
    out = []
    for th in thetas:
        pt, d = best_point(cspace(fixed, s, th))
        if pt is not None and d > 1e-7:
            out.append((d, pt[0], pt[1], th))
    out.sort(reverse=True)
    return out[:top]


def greedy(fixed, s, k, thetas, beam=2):
    """depth-first beam search placing k squares one at a time; returns a list of k poses or None."""
    if k == 0:
        return []
    for (_, cx, cy, th) in candidates(fixed, s, thetas, top=beam):
        rest = greedy(fixed + [(cx, cy, th)], s, k - 1, thetas, beam)
        if rest is not None:
            return [(cx, cy, th)] + rest
    return None


# ---------------------------------------------------------------- polish + exact check
def compose(fixed, placed, s):
    """34-vector with the fixed squares first, then the placed ones (11 in total)."""
    allq = list(fixed) + list(placed)
    assert len(allq) == G.N, len(allq)
    z = np.zeros(G.NV)
    for i, (cx, cy, th) in enumerate(allq):
        z[3 * i:3 * i + 3] = (cx, cy, th)
    z[G.S_IDX] = s
    return z


def polish(fixed, placed, s, margin=MARGIN, iters=300):
    """minimise the squared violations (with a margin) of the placed squares' rows against the walls, the fixed
    squares and each other; the fixed squares do not move."""
    nf = len(fixed)
    z0 = compose(fixed, placed, s)
    free = np.zeros(G.NV, bool)
    for i in range(nf, G.N):
        free[3 * i:3 * i + 3] = True

    def pen(x):
        z = z0.copy()
        z[free] = x
        gw, Jw = G.wall_rows(z)
        sel, _ = G.best_selection(z)
        gp, Jp = G.pair_rows(z, sel)
        vw = np.minimum(gw - margin, 0.0)
        vp = np.minimum(gp - margin, 0.0)
        f = float(vw @ vw + vp @ vp)
        grad = 2 * (vw @ Jw + vp @ Jp)
        return f, grad[free]

    r = minimize(pen, z0[free], jac=True, method='L-BFGS-B', options={'maxiter': iters})
    z = z0.copy()
    z[free] = r.x
    return z, float(r.fun)


def exact_check(z):
    """the lab's check on the composed configuration: min SAT gap and min wall row (both >= -TOL)."""
    gap = min(G.pair_gaps(z).values())
    wall = float(G.wall_rows(z)[0].min())
    return gap >= -TOL and wall >= -TOL, gap, wall


def place(fixed, s, k, thetas=None, beam=2, restarts=20, rng=None, seeds=()):
    """pack k unit squares into U = container minus the fixed squares; returns dict(found, poses, gap, wall,
    method) after the exact check, or found = False with the largest number of squares placed.
    seeds: initial pose lists (k poses each) polished first (e.g. the removed squares at their old poses)."""
    if thetas is None:
        thetas = [math.radians(t) for t in range(0, 90, 5)]
    if k == 0:
        return {'found': True, 'poses': [], 'method': 'nothing to place', 'k': 0}
    rng = rng or np.random.default_rng(0)
    for si, seed in enumerate(seeds):
        if len(seed) != k:
            continue
        z, f = polish(fixed, [tuple(p) for p in seed], s, iters=400)
        ok, gap, wall = exact_check(z)
        if ok:
            return {'found': True, 'poses': [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(len(fixed), G.N)],
                    'gap': gap, 'wall': wall, 'method': 'seed %d+polish' % si, 'k': k}
    # greedy over tilt grids of increasing resolution
    for th_list in (thetas, [math.radians(t) for t in np.arange(0, 90, 1.0)]):
        got = greedy(fixed, s, k, th_list, beam)
        if got is not None:
            z, f = polish(fixed, got, s)
            ok, gap, wall = exact_check(z)
            if ok:
                return {'found': True, 'poses': [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(len(fixed), G.N)],
                        'gap': gap, 'wall': wall, 'method': 'greedy(%d tilts)+polish' % len(th_list), 'k': k}
        if len(th_list) > len(thetas) and k > 3:
            break
    # random restarts of the penalty polish
    best_f = None
    for t in range(restarts):
        placed = [(rng.uniform(0.5, s - 0.5), rng.uniform(0.5, s - 0.5), rng.uniform(0, math.pi / 2)) for _ in range(k)]
        z, f = polish(fixed, placed, s, iters=400)
        ok, gap, wall = exact_check(z)
        if ok:
            return {'found': True, 'poses': [tuple(float(v) for v in z[3 * i:3 * i + 3]) for i in range(len(fixed), G.N)],
                    'gap': gap, 'wall': wall, 'method': 'penalty restart %d' % t, 'k': k}
        best_f = f if best_f is None else min(best_f, f)
    # how many DO fit (greedy, for the report)
    kmax = 0
    for kk in range(k - 1, 0, -1):
        if greedy(fixed, s, kk, thetas, beam) is not None:
            kmax = kk
            break
    return {'found': False, 'k': k, 'k_max_greedy': kmax, 'best_penalty': best_f, 'method': 'greedy+%d restarts' % restarts}


def slot_pose(corner, s):
    cx, cy = G.slot_centre(corner, s)
    return (cx, cy, 0.0)
