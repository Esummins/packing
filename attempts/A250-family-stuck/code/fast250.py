"""A250 penalty and gradient for FAMILY rows, on top of A244's wall / pair / depth machinery.

A ROW is a family Pi of pairwise disjoint border cells with a demand `need` = |Pi| + 1: the row is
satisfied when at least `need` distinct squares each meet SOME cell of Pi to depth >= delta.  Write
D(i) = max over the cells of Pi of the overlap depth of square i; the row's residual is the
`need`-th largest of D minus delta, and

    F(z) = walls + pairs (A244, unchanged) + sum over rows of min(residual, 0)^2 + tilt floor.

|Pi| = 1 reproduces A244's twelve-cell penalty exactly (need = 2, the second-deepest square), so
`--maxfam 1` is A244's optimiser and the control.  Nothing is designated anywhere: which squares
serve which family is re-decided at every evaluation.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts/A244-twelve-stuck/code'))
sys.path.insert(0, HERE)

import cells244 as C                                             # noqa: E402
import fast244 as F4                                             # noqa: E402
import fam250 as FM                                              # noqa: E402

N = F4.N
NV = F4.NV
S_IDX = F4.S_IDX
CELLS = list(C.CELLS)
TILT_MIN = 0.0


class Rows(object):
    """the row set for one side regime; `.R` (nrows, 12) membership, `.need` (nrows,)."""

    def __init__(self, rows):
        self.rows = list(rows)
        self.R = np.zeros((len(self.rows), len(CELLS)), bool)
        self.need = np.zeros(len(self.rows), int)
        for r, (f, nd) in enumerate(self.rows):
            self.R[r, list(f)] = True
            self.need[r] = nd

    def __len__(self):
        return len(self.rows)

    def names(self, r):
        return [CELLS[i] for i in self.rows[r][0]]


_CACHE = {}


def rows_for_side(s, kmax=3):
    """the rows active at side s (which cells are disjoint depends on s; in [3, 4+] the only
    threshold is s = 4, where the four facing slot pairs separate)."""
    key = (bool(s >= 4.0), int(kmax))
    if key not in _CACHE:
        _CACHE[key] = Rows(FM.rows(4.2 if key[0] else 3.9, kmax=kmax))
    return _CACHE[key]


def row_depths(d, rows):
    """(nrows, N): D(row, i) = max over the row's cells of the depth of square i."""
    return np.where(rows.R[:, :, None], d[None, :, :], -np.inf).max(axis=1)


def family_part(z, rows, delta, grad):
    d = F4.depths(z, CELLS)                      # (12, N)
    D = row_depths(d, rows)
    order = np.argsort(-D, axis=1)
    pick = np.take_along_axis(order, (rows.need - 1)[:, None], 1)[:, 0]
    val = D[np.arange(len(rows)), pick]
    f = 0.0
    for r in np.nonzero(val - delta < 0)[0]:
        short = float(val[r] - delta)
        f += short * short
        i = int(pick[r])
        cells = np.nonzero(rows.R[r])[0]
        ci = int(cells[int(np.argmax(d[cells, i]))])
        F4._depth_grad(z, CELLS[ci], i, grad, 2.0 * short)
    return f


def tilt_part(z, grad):
    F4.TILT_MIN = TILT_MIN
    return F4.tilt_part(z, grad)


def penalty(z, rows, delta, free_s=False, wgt=0.0):
    z = np.asarray(z, float)
    grad = np.zeros(NV)
    cx, cy, th, co, si, q, n = F4.geom(z)
    f = F4.wall_part(z, q, cx, cy, th, grad)
    f += F4.pair_part(z, q, n, cx, cy, grad)
    f += family_part(z, rows, delta, grad)
    f += tilt_part(z, grad)
    if free_s:
        f += wgt * float(z[S_IDX])
        grad[S_IDX] += wgt
    else:
        grad[S_IDX] = 0.0
    return f, grad


def worst(z, rows, delta):
    """(min wall gap, min pair gap, min over rows of the need-th largest depth)."""
    cx, cy, th, co, si, q, n = F4.geom(z)
    s = float(z[S_IDX])
    gw = float(np.min(np.stack([q[..., 0], q[..., 1], s - q[..., 0], s - q[..., 1]], -1)))
    _, g1, _ = F4.pair_table(q, n, cx, cy)
    gp = min(max(g1[i, j], g1[j, i]) for (i, j) in F4.PAIRS)
    if not len(rows):
        return gw, float(gp), float('inf')
    d = F4.depths(z, CELLS)
    D = row_depths(d, rows)
    val = -np.sort(-D, axis=1)
    v = np.take_along_axis(val, (rows.need - 1)[:, None], 1)[:, 0]
    return gw, float(gp), float(v.min())


def row_residuals(z, rows):
    """the need-th largest depth of every row, for reporting."""
    d = F4.depths(z, CELLS)
    D = row_depths(d, rows)
    val = -np.sort(-D, axis=1)
    return np.take_along_axis(val, (rows.need - 1)[:, None], 1)[:, 0]


def check_grad(seed=0, delta=0.01, kmax=3, h=1e-7):
    """finite-difference test of the family gradient."""
    rng = np.random.default_rng(seed)
    z = np.zeros(NV)
    z[0:33:3] = rng.uniform(0.7, 3.3, N)
    z[1:33:3] = rng.uniform(0.7, 3.3, N)
    z[2:33:3] = rng.uniform(0, math.pi / 2, N)
    z[S_IDX] = 3.95
    rows = rows_for_side(z[S_IDX], kmax)
    f0, g = penalty(z, rows, delta, free_s=True, wgt=0.1)
    err = 0.0
    for k in list(range(0, 12)) + [S_IDX]:
        w = z.copy()
        w[k] += h
        f1, _ = penalty(w, rows, delta, free_s=True, wgt=0.1)
        w[k] -= 2 * h
        f2, _ = penalty(w, rows, delta, free_s=True, wgt=0.1)
        err = max(err, abs((f1 - f2) / (2 * h) - g[k]))
    return f0, err, len(rows)


if __name__ == '__main__':
    for km in (1, 2, 3):
        f0, err, nr = check_grad(kmax=km)
        print('kmax %d rows %4d  f %.6f  max grad err %.3e' % (km, nr, f0, err))
