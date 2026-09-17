"""A247: TIGHT interval enclosures of the SAT projections.  The only trigonometric dependency
in the square-vs-rectangle and square-vs-square projections is through one-dimensional
functions of a single tilt (a cos th + b sin th, and w(phi) = |cos phi| + |sin phi|); their
exact ranges over an interval are computed in closed form (endpoints + interior extremum), so
the enclosure of every projection is the natural extension with NO dependency loss inside a
square.  Every function returns (lo, hi) arrays containing the true value for every parameter
in the box; rounding is not directed (guard 1e-9 in the verdicts; soundness tested in
verify247 against random point evaluations and against A246's coarser enclosures).
"""
import numpy as np

PI2 = np.pi / 2
PI4 = np.pi / 4
SQ2 = np.sqrt(2.0)


def max_lin_trig(a, b, t0, t1):
    """max over th in [t0, t1] of a cos th + b sin th (arrays; t0 <= t1)."""
    v0 = a * np.cos(t0) + b * np.sin(t0)
    v1 = a * np.cos(t1) + b * np.sin(t1)
    m = np.maximum(v0, v1)
    ts = np.arctan2(b, a)
    inside = (ts >= t0) & (ts <= t1)
    return np.where(inside, np.maximum(m, np.hypot(a, b)), m)


def lin_trig_range(a, b, t):
    """range of a cos th + b sin th for a in [a0,a1], b in [b0,b1], th in t = (t0, t1) within
    [0, pi/2] (cos, sin >= 0 there, so the function is monotone in a and in b)."""
    lo = -max_lin_trig(-a[0], -b[0], t[0], t[1])
    hi = max_lin_trig(a[1], b[1], t[0], t[1])
    return lo, hi


def w_range(p0, p1):
    """range of w(phi) = |cos phi| + |sin phi| (period pi/2, values in [1, sqrt2]) over [p0, p1]."""
    width = p1 - p0
    lo0 = np.mod(p0, PI2)
    hi0 = lo0 + width
    e0 = np.abs(np.cos(lo0)) + np.abs(np.sin(lo0))
    e1 = np.abs(np.cos(hi0)) + np.abs(np.sin(hi0))
    has_max = np.floor((hi0 - PI4) / PI2) >= np.ceil((lo0 - PI4) / PI2)
    has_min = np.floor(hi0 / PI2) >= np.ceil(lo0 / PI2)
    hi = np.where(has_max | (width >= PI2), SQ2, np.maximum(e0, e1))
    lo = np.where(has_min | (width >= PI2), 1.0, np.minimum(e0, e1))
    return lo, hi


def extent(pose):
    """[min x, max x], [min y, max y] of the square: centre -+ w(th)/2."""
    cx, cy, th = pose
    w = w_range(th[0], th[1])
    hw = (0.5 * w[0], 0.5 * w[1])
    return ((cx[0] - hw[1], cx[1] - hw[0]), (cx[0] + hw[0], cx[1] + hw[1])), \
           ((cy[0] - hw[1], cy[1] - hw[0]), (cy[0] + hw[0], cy[1] + hw[1]))


def proj_square_on(pose, psi, own):
    """projection [min, max] of the square onto the unit direction (cos psi, sin psi), psi an
    interval within [0, pi]: centre.n -+ half-width, the half-width being 1/2 on the square's
    own normals (own = True, psi = th or th + pi/2) and w(th - psi)/2 otherwise."""
    cx, cy, th = pose
    # centre.n = cx cos psi + cy sin psi; on [pi/2, pi] use cos psi = -sin(psi - pi/2) etc.
    lo, hi = _centre_dot(cx, cy, psi)
    if own:
        return (lo - 0.5, hi - 0.5), (lo + 0.5, hi + 0.5)
    w = w_range(th[0] - psi[1], th[1] - psi[0])
    return (lo - 0.5 * w[1], hi - 0.5 * w[0]), (lo + 0.5 * w[0], hi + 0.5 * w[1])


def _centre_dot(cx, cy, psi):
    """range of cx cos psi + cy sin psi over the box, psi within [0, pi] (split at pi/2)."""
    if np.all(psi[1] <= PI2 + 1e-15):
        return lin_trig_range(cx, cy, (np.minimum(psi[0], PI2), np.minimum(psi[1], PI2)))
    if np.all(psi[0] >= PI2 - 1e-15):
        t = (np.maximum(psi[0] - PI2, 0.0), np.maximum(psi[1] - PI2, 0.0))
        # cos psi = -sin t, sin psi = cos t: value = cy cos t - cx sin t
        return lin_trig_range(cy, (-cx[1], -cx[0]), t)
    # mixed: split elementwise
    a = lin_trig_range(cx, cy, (np.minimum(psi[0], PI2), np.minimum(psi[1], PI2)))
    t = (np.maximum(psi[0] - PI2, 0.0), np.maximum(psi[1] - PI2, 0.0))
    b = lin_trig_range(cy, (-cx[1], -cx[0]), t)
    left = psi[0] <= PI2
    right = psi[1] >= PI2
    lo = np.where(left & right, np.minimum(a[0], b[0]), np.where(left, a[0], b[0]))
    hi = np.where(left & right, np.maximum(a[1], b[1]), np.where(left, a[1], b[1]))
    return lo, hi


def proj_rect_on(R, psi):
    """projection (min_iv, max_iv) of the interval rectangle R = (x0, x1, y0, y1) (each (lo, hi))
    onto (cos psi, sin psi), psi within [0, pi]: the hull of the four corner projections."""
    x0, x1, y0, y1 = R
    pts = [_centre_dot(X, Y, psi) for X in (x0, x1) for Y in (y0, y1)]
    los = np.stack([p[0] for p in pts])
    his = np.stack([p[1] for p in pts])
    return (los.min(axis=0), his.min(axis=0)), (los.max(axis=0), his.max(axis=0))


def overlap(pa, pb):
    """min(maxA, maxB) - max(minA, minB) as an interval, pa = (min_iv, max_iv)."""
    top = (np.minimum(pa[1][0], pb[1][0]), np.minimum(pa[1][1], pb[1][1]))
    bot = (np.maximum(pa[0][0], pb[0][0]), np.maximum(pa[0][1], pb[0][1]))
    return top[0] - bot[1], top[1] - bot[0]


def depth_cell(pose, R):
    """enclosure of the SAT depth of the square with the interval rectangle: min over e_x, e_y,
    n0(th), n1(th)."""
    cx, cy, th = pose
    (xl, xh), (yl, yh) = extent(pose)
    vals = [overlap((xl, xh), (R[0], R[1])), overlap((yl, yh), (R[2], R[3]))]
    for psi in (th, (th[0] + PI2, th[1] + PI2)):
        vals.append(overlap(proj_square_on(pose, psi, True), proj_rect_on(R, psi)))
    lo = np.minimum.reduce([v[0] for v in vals])
    hi = np.minimum.reduce([v[1] for v in vals])
    return lo, hi


def depth_pair(pa, pb):
    """enclosure of the SAT depth of two squares: min over the four edge normals."""
    vals = []
    for own, other in ((pa, pb), (pb, pa)):
        th = own[2]
        for psi in (th, (th[0] + PI2, th[1] + PI2)):
            vals.append(overlap(proj_square_on(own, psi, True), proj_square_on(other, psi, False)))
    lo = np.minimum.reduce([v[0] for v in vals])
    hi = np.minimum.reduce([v[1] for v in vals])
    return lo, hi
