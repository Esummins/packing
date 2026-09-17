"""A246: vectorised interval arithmetic for boxes of square poses, and interval ENCLOSURES of the
separating-axis overlap depth (square vs axis-aligned rectangle, square vs square).

An interval is a pair of equal-shape numpy arrays (lo, hi).  A pose box is (cx, cy, th) with each
coordinate an interval; th within [0, pi/2] (a unit square is invariant under 90-degree turns).
Every function returns an enclosure: for EVERY pose in the box the true value lies in [lo, hi].
Rounding is not directed; every verdict that uses these enclosures keeps a guard of GUARD = 1e-9,
four orders above the accumulated double-precision error of these few operations (see test246).
"""
import numpy as np

GUARD = 1e-9
HALF_PI = np.pi / 2


def I(lo, hi=None):
    lo = np.asarray(lo, float)
    return (lo, lo.copy() if hi is None else np.asarray(hi, float))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[1], a[1] - b[0])


def neg(a):
    return (-a[1], -a[0])


def mul(a, b):
    p = np.stack([a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]])
    return (p.min(axis=0), p.max(axis=0))


def scale(a, k):
    return (a[0] * k, a[1] * k) if k >= 0 else (a[1] * k, a[0] * k)


def imin(a, b):
    return (np.minimum(a[0], b[0]), np.minimum(a[1], b[1]))


def imax(a, b):
    return (np.maximum(a[0], b[0]), np.maximum(a[1], b[1]))


def cos_i(t):
    """cos on th within [0, pi/2] (decreasing)."""
    return (np.cos(np.minimum(t[1], HALF_PI)), np.cos(np.maximum(t[0], 0.0)))


def sin_i(t):
    return (np.sin(np.maximum(t[0], 0.0)), np.sin(np.minimum(t[1], HALF_PI)))


def absval(a):
    lo = np.where(a[0] > 0, a[0], np.where(a[1] < 0, -a[1], 0.0))
    hi = np.maximum(np.abs(a[0]), np.abs(a[1]))
    return (lo, hi)


def hull(*vals):
    """the enclosure of the min and of the max of several intervals: (min_lo, min_hi), (max_lo, max_hi)."""
    los = np.stack([v[0] for v in vals])
    his = np.stack([v[1] for v in vals])
    return (los.min(axis=0), his.min(axis=0)), (los.max(axis=0), his.max(axis=0))


# ---------------------------------------------------------------- projections
def axes(th):
    """the two edge normals n0 = (cos, sin), n1 = (-sin, cos) of a square with tilt th (intervals)."""
    c, s = cos_i(th), sin_i(th)
    return (c, s), (neg(s), c)


def proj_square(pose, n):
    """[min, max] of a unit square's projection onto the (interval) direction n = (nx, ny), which is
    a unit vector for every parameter: centre.n -+ (|nx.e0| + |nx.e1|)/2 with e0, e1 the edge
    directions; for a unit direction the half-width is (|n.e0| + |n.e1|)/2."""
    cx, cy, th = pose
    c, s = cos_i(th), sin_i(th)
    e0 = (c, s)
    e1 = (neg(s), c)
    dot = add(mul(n[0], e0[0]), mul(n[1], e0[1]))
    dot1 = add(mul(n[0], e1[0]), mul(n[1], e1[1]))
    hw = scale(add(absval(dot), absval(dot1)), 0.5)
    cn = add(mul(cx, n[0]), mul(cy, n[1]))
    return sub(cn, hw), add(cn, hw)


def proj_rect(rect, n):
    """[min, max] of the projection of the fixed axis-aligned rectangle (x0, x1, y0, y1) onto n."""
    x0, x1, y0, y1 = rect
    pts = [add(scale(n[0], x), scale(n[1], y)) for x in (x0, x1) for y in (y0, y1)]
    mn, mx = hull(*pts)
    return mn, mx


def overlap(pa, pb):
    """min(maxA, maxB) - max(minA, minB) as an interval."""
    return sub(imin(pa[1], pb[1]), imax(pa[0], pb[0]))


def depth_rect(pose, rect):
    """enclosure of the SAT overlap depth of the square with the rectangle: min over the four
    axes e_x, e_y, n0, n1 of the projection overlap.  > 0 iff the interiors meet."""
    cx, cy, th = pose
    w = add(cos_i(th), sin_i(th))
    hw = scale(w, 0.5)
    ox = overlap((sub(cx, hw), add(cx, hw)), (I(rect[0]), I(rect[1])))
    oy = overlap((sub(cy, hw), add(cy, hw)), (I(rect[2]), I(rect[3])))
    vals = [ox, oy]
    for n in axes(th):
        vals.append(overlap(proj_square(pose, n), proj_rect(rect, n)))
    return hull(*vals)[0]


def depth_pair(pa, pb):
    """enclosure of the SAT overlap depth of two unit squares (min over their four edge normals)."""
    vals = []
    for pose in (pa, pb):
        for n in axes(pose[2]):
            vals.append(overlap(proj_square(pa, n), proj_square(pb, n)))
    return hull(*vals)[0]


def extent(pose):
    """[min x, max x], [min y, max y] of the square (intervals)."""
    cx, cy, th = pose
    hw = scale(add(cos_i(th), sin_i(th)), 0.5)
    return (sub(cx, hw), add(cx, hw)), (sub(cy, hw), add(cy, hw))


# ---------------------------------------------------------------- point evaluation (for tests)
def depth_rect_pt(cx, cy, th, rect):
    return float(depth_rect((I(cx), I(cy), I(th)), rect)[0])


def depth_pair_pt(a, b):
    pa = (I(a[0]), I(a[1]), I(a[2]))
    pb = (I(b[0]), I(b[1]), I(b[2]))
    return float(depth_pair(pa, pb)[0])


def box_split(box, k):
    """bisect the box (an (m, 2, d) array: lo/hi per dim) along dim k -> (2m, 2, d)."""
    lo, hi = box[:, 0, :], box[:, 1, :]
    mid = 0.5 * (lo[:, k] + hi[:, k])
    b1 = box.copy()
    b1[:, 1, k] = mid
    b2 = box.copy()
    b2[:, 0, k] = mid
    return np.concatenate([b1, b2])


def pose_of(box, off):
    """the pose intervals (cx, cy, th) of dims off, off+1, off+2 of a box array."""
    return ((box[:, 0, off], box[:, 1, off]), (box[:, 0, off + 1], box[:, 1, off + 1]),
            (box[:, 0, off + 2], box[:, 1, off + 2]))
