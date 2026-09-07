"""A122 - the exact contact SYSTEM of an A122 landing, in mpmath at arbitrary precision.

The six slot squares are not variables: BL(i,j) sits at (i + 1/2, j + 1/2), BR(0,j) at
(s - 1/2, j + 1/2), TR(0,0) at (s - 1/2, s - 1/2), all upright.  (This is not an assumption - it is
read off the landing, where every slot square is exactly on its cell to 1e-16, and it is checked
again at the end.)  The unknowns are the five free poses (cx, cy, th) and s: SIXTEEN.

Each active incidence contributes one equation "vertex V of square A lies on the line through edge
E of square B", i.e. n_E . (V - P_E) = 0, with n_E the outward unit normal of that edge.  Wall
incidences are V.x = 0 / V.x = s / V.y = 0 / V.y = s.

The incidence LIST (which vertex of which square on which edge of which other) is read once from
A107's `analyse` at the double-precision landing; from then on the algebra is exact and the
refinement is Newton in mpmath.
"""
from __future__ import annotations

import math

import numpy as np
from mpmath import mp, mpf, matrix, cos, sin, sqrt, findroot

import a122lib as A
from a122lib import AN, L

CORNER = ((-1, -1), (1, -1), (1, 1), (-1, 1))     # L.corners order (checked below)


def _check_corner_order():
    c = L.corners(0.0, 0.0, 0.0)
    for k, (dx, dy) in enumerate(CORNER):
        assert abs(c[k][0] - dx / 2) < 1e-12 and abs(c[k][1] - dy / 2) < 1e-12, (k, c)


_check_corner_order()


def slot_expr(name):
    """(a, b, c, d) with centre = (a + b*s, c + d*s) for a slot square."""
    return A.MZ.slot_affine(name)


def incidence_list(s, cfg, names, tol=2e-5):
    """[(i, vi, j, ei)] pair incidences + [(i, vi, wall)] wall incidences at the landing."""
    z = A.to107(s, cfg)
    sq = AN.build_squares((), 11)
    pairs, walls = [], []
    for i in range(11):
        for j in range(i + 1, 11):
            if AN.pair_gap(sq[i], sq[j], z) >= 1e-9:
                continue
            seen = set()
            for owner, vi, ei, t, d in AN.incidences(sq[i], sq[j], z, tol=tol):
                key = (owner, vi)
                if key in seen:
                    continue
                seen.add(key)
                if owner == 'a':
                    pairs.append((i, vi, j, ei))
                else:
                    pairs.append((j, vi, i, ei))
    for i in range(11):
        c, th = sq[i].pose(z)
        P = L.corners(c[0], c[1], th)
        for wall in ('left', 'right', 'bottom', 'top'):
            for vi, v in enumerate(P):
                g = {'left': v[0], 'right': s - v[0], 'bottom': v[1], 'top': s - v[1]}[wall]
                if g < 1e-9:
                    walls.append((i, vi, wall))
    return pairs, walls


class System:
    """The 16-unknown exact system of one landing.  x = [cx,cy,th]*5 + [s]."""

    QUARTER = ((1, 0), (0, 1), (-1, 0), (0, -1))

    def __init__(self, s, cfg, names, free_only=True):
        self.names = list(names)
        self.pairs, self.walls = incidence_list(s, cfg, names)
        # keep only rows that involve at least one FREE square (slot-slot rows are identities)
        self.pairs = [(i, vi, j, ei) for (i, vi, j, ei) in self.pairs if i < 5 or j < 5]
        self.walls = [(i, vi, w) for (i, vi, w) in self.walls if i < 5]
        self.slot_aff = [slot_expr(n) for n in self.names[5:]]
        # a slot square is upright, but the LANDING may store it at a multiple of 90 deg, which
        # permutes its corner labels; the incidence list is written in those labels, so keep them
        self.slot_q = [int(round(cfg[i][2] / (math.pi / 2))) % 4 for i in range(5, 11)]

    # -------------------------------------------------------------- pose accessors
    def corners(self, x, i):
        if i < 5:
            cx, cy, th = x[3 * i], x[3 * i + 1], x[3 * i + 2]
            co, si = cos(th), sin(th)
        else:
            a, b, c, d = self.slot_aff[i - 5]
            s = x[15]
            cx, cy = a + b * s, c + d * s
            co, si = self.QUARTER[self.slot_q[i - 5]]
        out = []
        for dx, dy in CORNER:
            out.append((cx + (co * dx - si * dy) / 2, cy + (si * dx + co * dy) / 2))
        return out

    # -------------------------------------------------------------- residuals
    def residuals(self, x):
        r = []
        C = [self.corners(x, i) for i in range(11)]
        for (i, vi, j, ei) in self.pairs:
            V = C[i][vi]
            P, Q = C[j][ei], C[j][(ei + 1) % 4]
            ex, ey = Q[0] - P[0], Q[1] - P[1]
            # unit normal is (ey, -ex)/|e|; |e| = 1 for a unit square, so no division needed
            r.append((V[0] - P[0]) * ey - (V[1] - P[1]) * ex)
        s = x[15]
        for (i, vi, w) in self.walls:
            V = C[i][vi]
            r.append({'left': V[0], 'right': s - V[0], 'bottom': V[1], 'top': s - V[1]}[w])
        return r

    def nrows(self):
        return len(self.pairs) + len(self.walls)

    def labels(self):
        out = []
        for (i, vi, j, ei) in self.pairs:
            out.append(f'{self.names[i]}.v{vi} on {self.names[j]}.e{ei}')
        for (i, vi, w) in self.walls:
            out.append(f'{self.names[i]}.v{vi} on {w} wall')
        return out


def x0_from(s, cfg):
    x = []
    for c in cfg[:5]:
        x += [mpf(repr(c[0])), mpf(repr(c[1])), mpf(repr(c[2]))]
    x.append(mpf(repr(s)))
    return x


def jac_numeric(sysm, x, h=None):
    h = h or mpf(10) ** (-(mp.dps // 2))
    n = len(x)
    r0 = sysm.residuals(x)
    m = len(r0)
    J = matrix(m, n)
    for k in range(n):
        xp = list(x)
        xp[k] = xp[k] + h
        rp = sysm.residuals(xp)
        for q in range(m):
            J[q, k] = (rp[q] - r0[q]) / h
    return J, r0


def gauss_newton(sysm, x, iters=60, extra=None, verbose=False):
    """Levenberg-free Gauss-Newton with a pseudo-inverse step (handles rank deficiency by taking
    the minimum-norm correction).  `extra` is an optional list of callables adding equations."""
    x = list(x)
    for it in range(iters):
        J, r = jac_numeric(sysm, x)
        if extra:
            m0 = J.rows
            rows = []
            for fn in extra:
                rows.append(fn)
            Jn = matrix(m0 + len(rows), 16)
            for a in range(m0):
                for b in range(16):
                    Jn[a, b] = J[a, b]
            h = mpf(10) ** (-(mp.dps // 2))
            for q, fn in enumerate(rows):
                r.append(fn(x))
                for b in range(16):
                    xp = list(x); xp[b] = xp[b] + h
                    Jn[m0 + q, b] = (fn(xp) - r[m0 + q]) / h
            J = Jn
        Jf = np.array([[float(J[a, b]) for b in range(16)] for a in range(J.rows)])
        rf = np.array([float(v) for v in r])
        dx, *_ = np.linalg.lstsq(Jf, -rf, rcond=1e-12)
        nrm = float(np.abs(rf).max())
        if verbose:
            print(f'   it {it}: |r|inf = {nrm:.3e}')
        for b in range(16):
            x[b] = x[b] + mpf(repr(float(dx[b])))
        if nrm < mpf(10) ** (-(mp.dps - 5)):
            break
    return x
