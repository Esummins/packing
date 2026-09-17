"""A251: BOX-VALID cores and the PIERCE certificate over a parameter BOX of the ring family.

Sound direction (A242/A243, A171 multibox).  For a parameter box X the ACTUAL pocket of any ring
x in X satisfies

    pocket(x) = [0, s(x)]^2 \\ U_i int Q_i(x)   SUBSET   [0, s_max]^2 \\ U_i core_i(X) =: POCKET_bar(X)

whenever core_i(X) is contained in Q_i(x) for EVERY x in X.  So a capacity bound proved for
POCKET_bar(X) holds for every ring of the box: the pocket is OVER-approximated, the cores
UNDER-approximated -- the only sound direction.

CORE formula [T].  Let the member's reference pose be (cbar, thetabar) and over the box let
|theta(x) - thetabar| <= Dtheta and |c(x) - cbar|_2 <= rho.  Then the square of pose
(cbar, thetabar) and half-side

    a := (0.5 - rho) / w(Dtheta),      w(t) = cos t + sin t,

lies in Q_i(x) for every x in X.  Proof: p = cbar + Rbar q with |q|_inf <= a; then
R(theta(x))^T (p - c(x)) = R(thetabar - theta(x)) q + R(theta(x))^T (cbar - c(x)), whose
infinity norm is at most w(Dtheta) a + rho <= 0.5.  (A237's kernel bound |R(d) q|_inf <=
w(|d|) |q|_inf.)  a <= 0 means the core is EMPTY -- the product law.

PIERCE over the box (A237 Lemma JAGGED (J4), Lean `capacity_le_of_pierce`): points p_1..p_k with
(POCKET_bar (-) K_bin) contained in U_i (p_i + K_bin) for every tilt bin certify capacity
(POCKET_bar) <= k, hence capacity(pocket(x)) <= k for every x in the box.
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A237-pocket-waste', 'code'))
import geom237 as G237                                                # noqa: E402

# vertex / centre Lipschitz constants of the corner-frame squares of geom249 (see family251)
LIP_C_THETA = 1.0 + math.sqrt(2.0) / 2.0          # |d centre / d theta|  <= 1.7072
LIP_V_THETA = LIP_C_THETA + math.sqrt(2.0) / 2.0  # |d vertex / d theta|  <= 2.4143


def w_of(a):
    return math.cos(a) + math.sin(a)


def core_half(rho, dtheta):
    """the sound core half-side (0 or less = empty core: the product law)."""
    return (0.5 - rho) / w_of(dtheta)


def core_members(poses, rhos, dthetas):
    """[(cx, cy, theta, half)] for the reference poses and the box's per-member deviations."""
    out = []
    for (cx, cy, th), rho, dth in zip(poses, rhos, dthetas):
        out.append((float(cx), float(cy), float(th), core_half(rho, dth)))
    return out


def member_poly(m):
    return Polygon(G237.sq_verts(m[0], m[1], m[2], half=m[3]))


def pocket_bar(members, s):
    """[0, s]^2 minus the cores (empty cores drop out)."""
    P = sbox(0.0, 0.0, s, s)
    live = [member_poly(m) for m in members if m[3] > 1e-12]
    return P.difference(unary_union(live)) if live else P


def erode(members, s, mid, half_k):
    """{c : c + K in POCKET_bar} for the kernel square K of tilt `mid`, half-side `half_k`:
    the container shrunk by K's axis half-width minus every core (+) K (A237 geom237.erode_by_square,
    generalised to per-member half-sides)."""
    h = half_k * w_of(mid)
    if s - 2 * h <= 0:
        return Polygon()
    region = sbox(h, h, s - h, s - h)
    k0 = G237.sq_verts(0.0, 0.0, mid, half_k)
    sums = [G237.minkowski_convex(G237.sq_verts(m[0], m[1], m[2], m[3]), k0)
            for m in members if m[3] > 1e-12]
    if sums:
        region = region.difference(unary_union(sums))
    return region


def free_bins(members, s, step_deg=1.0):
    """the per-bin over-approximated free-centre regions (t1, t2, Cbar)."""
    out = []
    for t1, t2 in G237.bins(step_deg):
        K, H, m, f = G237.kernel_hull(t1, t2)
        out.append((t1, t2, erode(members, s, m, 0.5 / f)))
    return out


def pierce(members, s, points, step_deg=1.0, free=None):
    """max over tilt bins of area(Cbar \\ U_i (p_i + K_bin)); <= tol certifies capacity <= len(points)."""
    worst = 0.0
    if free is None:
        free = free_bins(members, s, step_deg)
    for t1, t2, Cbar in free:
        if Cbar.is_empty:
            continue
        K, H, m, f = G237.kernel_hull(t1, t2)
        cover = unary_union([Polygon([(p[0] + k[0], p[1] + k[1]) for k in K]) for p in points])
        worst = max(worst, Cbar.difference(cover).area)
    return float(worst)


def pierce_witness(members, s, points, step_deg=1.0, free=None):
    """(residual, worst bin mid deg, a representative uncovered centre) -- for pages and diagnosis."""
    worst, wb, wc = 0.0, None, None
    if free is None:
        free = free_bins(members, s, step_deg)
    for t1, t2, Cbar in free:
        if Cbar.is_empty:
            continue
        K, H, m, f = G237.kernel_hull(t1, t2)
        cover = unary_union([Polygon([(p[0] + k[0], p[1] + k[1]) for k in K]) for p in points])
        D = Cbar.difference(cover)
        if D.area > worst:
            worst = D.area
            wb = math.degrees(m)
            c = D.representative_point()
            wc = (c.x, c.y)
    return float(worst), wb, wc


def best_pierce2(members, s, free, r=0.7, g=6):
    """the best CENTRAL pair p = centre +/- d on a grid (A249 pocket249.pierce2)."""
    c = s / 2.0
    best = None
    for a in range(-g, g + 1):
        for b in range(0, g + 1):
            if a == 0 and b == 0:
                continue
            d = (r * a / g, r * b / g)
            pts = [(c + d[0], c + d[1]), (c - d[0], c - d[1])]
            v = pierce(members, s, pts, free=free)
            if best is None or v < best[0]:
                best = (v, pts)
    return best


def shrink_tolerance(poses, s, points, lo=0.0, hi=0.5, iters=12, tol=1e-9):
    """the largest uniform core shrink eps for which PIERCE(points) still certifies:
    cores = the squares of `poses` with half-side 0.5 - eps.  Bisection (the residual is
    monotone in eps: a smaller core enlarges POCKET_bar).  Returns (eps, residual_at_eps)."""
    def ok(eps):
        mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
        return pierce(mem, s, points) <= tol
    if not ok(lo):
        return 0.0, None
    a, b = lo, hi
    if ok(hi):
        return hi, 0.0
    for _ in range(iters):
        m = 0.5 * (a + b)
        if ok(m):
            a = m
        else:
            b = m
    mem = [(p[0], p[1], p[2], 0.5 - a) for p in poses]
    return a, pierce(mem, s, points)


def shrink_tolerance2(poses, s, iters=10, tol=1e-9, step_deg=2.0, g=5, r=1.0):
    """as shrink_tolerance but for PIERCE(2) with the two points RE-OPTIMISED at each shrink."""
    def ok(eps):
        mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
        free = free_bins(mem, s, step_deg)
        if pierce(mem, s, [(s / 2, s / 2)], free=free) <= tol:
            return True, [(s / 2, s / 2)]
        v, pts = best_pierce2(mem, s, free, r=r, g=g)
        return v <= tol, pts
    good, pts = ok(0.0)
    if not good:
        return 0.0, None
    a, b, best = 0.0, 0.5, pts
    for _ in range(iters):
        m = 0.5 * (a + b)
        good, p = ok(m)
        if good:
            a, best = m, p
        else:
            b = m
    return a, best


def lemma_two_side(sigma):
    """Lemma TWO (ring_capacity.md s.2.5): a unit square inside a square of side sigma < 2 contains
    its centre, so N(sigma) = 1.  Returns the certified capacity of a sigma-square region."""
    return 1 if sigma < 2.0 - 1e-12 else None


if __name__ == '__main__':
    # smoke: eight unit squares in a ring around a container, cores at three shrinks
    s = 3.877084
    poses = [(0.5, 0.5, 0.0), (s - 0.5, 0.5, 0.0), (s - 0.5, s - 0.5, 0.0), (0.5, s - 0.5, 0.0),
             (0.5, 1.6, 0.3), (1.6, 0.5, 0.3), (s - 0.5, 1.6, 0.3), (1.6, s - 0.5, 0.3)]
    for eps in (0.0, 0.05, 0.15):
        mem = [(p[0], p[1], p[2], 0.5 - eps) for p in poses]
        print('eps %.2f  pocket %.3f  pierce1 %.4f' % (eps, pocket_bar(mem, s).area,
                                                       pierce(mem, s, [(s / 2, s / 2)])))
