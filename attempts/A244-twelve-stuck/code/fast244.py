"""A244 vectorised penalty and gradient for "11 unit squares in [0,s]^2 with every one of a set of
border cells met by at least TWO squares with depth >= delta".

    F(z) = sum over wall rows of min(g,0)^2
         + sum over the 55 pairs of min(gap,0)^2
         + sum over the constrained cells of min(d2 - delta, 0)^2

where gap is the exact separating-axis gap (>= 0 iff interior-disjoint) and d2 is the SECOND
largest overlap depth of the cell over the 11 squares.  Nothing is designated: which squares meet
which cell is decided afresh at every evaluation by the depths themselves, so the assignment is
free to change during the descent -- the fixed-designation form (crowd244 + opt244) traps SLSQP at
the touching configurations where a designated meeter only clips a cell corner.

For any unit axis a, a unit square at (c, th) projects to [c.a - h/2, c.a + h/2] with support
width h = |a.n0| + |a.n1| (n0 = (cos, sin), n1 = (-sin, cos)), and an axis-aligned box of widths
(wx, wy) centred at b projects to [b.a - v/2, b.a + v/2] with v = |a_x| wx + |a_y| wy.  The
overlap along a is min(A+, B+) - max(A-, B-); the depth is the min over a in {ex, ey, n0, n1}.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells244 as C

N = 11
NV = 34
S_IDX = 33
HALF = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
NHAT = np.array([(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)])
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]

# The TILT FLOOR (radians, 0 = off): every square's tilt is pushed at least this far from a
# multiple of pi/2.  A217 applied its floor to the corner squares only; here the whole packing is
# floored, which is the stronger variant -- a floored packing has no axis-aligned square at all.
TILT_MIN = 0.0


def tilt_part(z, grad):
    if TILT_MIN <= 0.0:
        return 0.0
    f = 0.0
    q = math.pi / 2
    for i in range(N):
        m = z[3 * i + 2] % q
        dev, sgn = (m, 1.0) if m <= q / 2 else (q - m, -1.0)
        v = min(dev - TILT_MIN, 0.0)
        if v < 0.0:
            f += v * v
            grad[3 * i + 2] += 2.0 * v * sgn
    return f


def geom(z):
    c = np.asarray(z, float)[:33].reshape(N, 3)
    cx, cy, th = c[:, 0], c[:, 1], c[:, 2]
    co, si = np.cos(th), np.sin(th)
    q = np.stack([cx[:, None] + co[:, None] * HALF[None, :, 0] - si[:, None] * HALF[None, :, 1],
                  cy[:, None] + si[:, None] * HALF[None, :, 0] + co[:, None] * HALF[None, :, 1]], -1)
    n = np.stack([co[:, None] * NHAT[None, :, 0] - si[:, None] * NHAT[None, :, 1],
                  si[:, None] * NHAT[None, :, 0] + co[:, None] * NHAT[None, :, 1]], -1)
    return cx, cy, th, co, si, q, n


def wall_part(z, q, cx, cy, th, grad):
    s = float(z[S_IDX])
    g = np.stack([q[..., 0], q[..., 1], s - q[..., 0], s - q[..., 1]], -1)     # (N,4,4)
    v = np.minimum(g, 0.0)
    f = float((v * v).sum())
    if v.any():
        r = q - np.stack([cx, cy], -1)[:, None, :]
        dq = np.stack([-r[..., 1], r[..., 0]], -1)                            # dq/dth
        for i, k, w in zip(*np.nonzero(v)):
            two = 2.0 * v[i, k, w]
            if w == 0:
                grad[3 * i] += two
                grad[3 * i + 2] += two * dq[i, k, 0]
            elif w == 1:
                grad[3 * i + 1] += two
                grad[3 * i + 2] += two * dq[i, k, 1]
            elif w == 2:
                grad[3 * i] -= two
                grad[3 * i + 2] -= two * dq[i, k, 0]
                grad[S_IDX] += two
            else:
                grad[3 * i + 1] -= two
                grad[3 * i + 2] -= two * dq[i, k, 1]
                grad[S_IDX] += two
    return f


def pair_table(q, n, cx, cy):
    c = np.stack([cx, cy], -1)
    t = np.einsum('oed,pkd->opek', n, q) - np.einsum('oed,od->oe', n, c)[:, None, :, None] - 0.5
    m = t.min(axis=3)                                   # (o,p,e)
    e = m.argmax(axis=2)
    g1 = np.take_along_axis(m, e[:, :, None], 2)[:, :, 0]
    return t, g1, e


def pair_part(z, q, n, cx, cy, grad):
    t, g1, e = pair_table(q, n, cx, cy)
    f = 0.0
    c = np.stack([cx, cy], -1)
    for (i, j) in PAIRS:
        if g1[i, j] >= g1[j, i]:
            o, p, gap = i, j, g1[i, j]
        else:
            o, p, gap = j, i, g1[j, i]
        if gap >= 0:
            continue
        f += gap * gap
        ee = int(e[o, p])
        k = int(t[o, p, ee].argmin())
        nn = n[o, ee]
        r = q[p, k] - c[o]
        rp = q[p, k] - c[p]
        two = 2.0 * gap
        grad[3 * p] += two * nn[0]
        grad[3 * p + 1] += two * nn[1]
        grad[3 * p + 2] += two * (nn[0] * (-rp[1]) + nn[1] * rp[0])
        grad[3 * o] -= two * nn[0]
        grad[3 * o + 1] -= two * nn[1]
        grad[3 * o + 2] += two * (-nn[1] * r[0] + nn[0] * r[1])
    return f


def _axes(co, si):
    """the four axes of square i and their d/dth, as (4,2) arrays."""
    a = np.array([(1.0, 0.0), (0.0, 1.0), (co, si), (-si, co)])
    da = np.array([(0.0, 0.0), (0.0, 0.0), (-si, co), (-co, -si)])
    return a, da


def axis_stack(co, si):
    """(N,4,2) the four axes of every square, and (N,4) their support widths for a unit square:
    ex and ey see the width |cos| + |sin|, the square's own normals see 1."""
    z2 = np.zeros_like(co)
    o2 = np.ones_like(co)
    a = np.stack([np.stack([o2, z2], -1), np.stack([z2, o2], -1),
                  np.stack([co, si], -1), np.stack([-si, co], -1)], 1)
    W = np.abs(co) + np.abs(si)
    h = np.stack([W, W, o2, o2], -1)
    return a, h


def depths(z, cells):
    """(len(cells), N) overlap depths, vectorised."""
    cx, cy, th, co, si, q, n = geom(z)
    s = float(z[S_IDX])
    a, h = axis_stack(co, si)
    ca = np.einsum('ikd,id->ik', a, np.stack([cx, cy], -1))
    out = np.zeros((len(cells), N))
    for ci, name in enumerate(cells):
        x0, x1, y0, y1 = C.cell_rect(name, s)
        b = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        v = np.abs(a[:, :, 0]) * (x1 - x0) + np.abs(a[:, :, 1]) * (y1 - y0)
        ba = a @ b
        out[ci] = (np.minimum(ca + h / 2, ba + v / 2) - np.maximum(ca - h / 2, ba - v / 2)).min(axis=1)
    return out


def _depth_grad(z, name, i, grad, coef):
    """add coef * d(depth of square i in cell `name`)/d(params) to grad."""
    cx, cy, th = z[3 * i], z[3 * i + 1], z[3 * i + 2]
    co, si = math.cos(th), math.sin(th)
    s = float(z[S_IDX])
    x0, x1, y0, y1 = C.cell_rect(name, s)
    dx0, dx1, dy0, dy1 = C.cell_rect_ds(name)
    b = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    db = np.array([(dx0 + dx1) / 2.0, (dy0 + dy1) / 2.0])
    n0, n1 = np.array([co, si]), np.array([-si, co])
    a, da = _axes(co, si)
    cvec = np.array([cx, cy])
    best, arg = None, None
    for k in range(4):
        ak, dak = a[k], da[k]
        h = abs(ak @ n0) + abs(ak @ n1)
        vv = abs(ak[0]) * (x1 - x0) + abs(ak[1]) * (y1 - y0)
        A, B = cvec @ ak, b @ ak
        ov = min(A + h / 2, B + vv / 2) - max(A - h / 2, B - vv / 2)
        if best is None or ov < best:
            best, arg = ov, k
    k = arg
    ak, dak = a[k], da[k]
    p0, p1 = ak @ n0, ak @ n1
    dp0 = dak @ n0 + ak @ n1                    # d(a.n0)/dth  (dn0/dth = n1)
    dp1 = dak @ n1 - ak @ n0                    # d(a.n1)/dth  (dn1/dth = -n0)
    h = abs(p0) + abs(p1)
    dh = np.sign(p0) * dp0 + np.sign(p1) * dp1
    vv = abs(ak[0]) * (x1 - x0) + abs(ak[1]) * (y1 - y0)
    dv = np.sign(ak[0]) * dak[0] * (x1 - x0) + np.sign(ak[1]) * dak[1] * (y1 - y0)
    A, B = cvec @ ak, b @ ak
    dA_th, dB_th = cvec @ dak, b @ dak
    dB_s = db @ ak
    g = np.zeros(4)                              # d/d(cx, cy, th, s)

    def add(sgn, which, up):
        if which == 'A':
            g[0] += sgn * ak[0]
            g[1] += sgn * ak[1]
            g[2] += sgn * (dA_th + up * dh / 2)
        else:
            g[2] += sgn * (dB_th + up * dv / 2)
            g[3] += sgn * dB_s
    add(1.0, 'A' if A + h / 2 <= B + vv / 2 else 'B', +1.0)
    add(-1.0, 'A' if A - h / 2 >= B - vv / 2 else 'B', -1.0)
    grad[3 * i] += coef * g[0]
    grad[3 * i + 1] += coef * g[1]
    grad[3 * i + 2] += coef * g[2]
    grad[S_IDX] += coef * g[3]


def cell_part(z, cells, delta, grad):
    d = depths(z, cells)
    f = 0.0
    for ci, name in enumerate(cells):
        order = np.argsort(-d[ci])
        i2 = int(order[1])
        short = d[ci, i2] - delta
        if short >= 0:
            continue
        f += short * short
        _depth_grad(z, name, i2, grad, 2.0 * short)
    return f


def penalty(z, cells, delta, free_s=False, wgt=0.0):
    z = np.asarray(z, float)
    grad = np.zeros(NV)
    cx, cy, th, co, si, q, n = geom(z)
    f = wall_part(z, q, cx, cy, th, grad)
    f += pair_part(z, q, n, cx, cy, grad)
    f += cell_part(z, cells, delta, grad)
    f += tilt_part(z, grad)
    if free_s:
        f += wgt * float(z[S_IDX])
        grad[S_IDX] += wgt
    else:
        grad[S_IDX] = 0.0
    return f, grad


def worst(z, cells, delta):
    """(min wall gap, min pair gap, min over cells of the second depth)."""
    cx, cy, th, co, si, q, n = geom(z)
    s = float(z[S_IDX])
    gw = float(np.min(np.stack([q[..., 0], q[..., 1], s - q[..., 0], s - q[..., 1]], -1)))
    _, g1, _ = pair_table(q, n, cx, cy)
    gp = min(max(g1[i, j], g1[j, i]) for (i, j) in PAIRS)
    d = depths(z, cells)
    d2 = min(float(np.sort(d[ci])[-2]) for ci in range(len(cells)))
    return gw, float(gp), d2
