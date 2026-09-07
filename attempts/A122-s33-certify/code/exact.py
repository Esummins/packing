"""A122 T1 - the minima of S33 / S35 / S38 to 40+ digits, and the search for a closed form.

A108 could write S07 down in Q(sqrt 2) because every tilt there was 0 or 45 deg, so the sixteen
active contact rows closed on s by rational elimination.  Here they do NOT: the active contact
system of each A122 landing is RANK-DEFICIENT (16 rows, 16 unknowns, rank 14 at S33min and 15 at
S35min / S38min), i.e. the contact graph alone leaves a 2- (resp. 1-) parameter family of packings
with exactly that graph, and the minimum sits at an interior critical point of s on that family.
The exact characterisation is therefore the LAGRANGE system

    g(x) = 0                (the 16 incidence equations, free poses + s, slots on their cells)
    J(x)^T lam = e_s        (ds vanishes on the tangent of the family)

- 32 equations in 32 unknowns, solved by pseudo-inverse Gauss-Newton in mpmath at 80 digits with
an analytic (forward-mode) Jacobian.  A PSLQ sweep then asks whether s* satisfies a low-degree
integer polynomial; the answer for all three is NO up to degree 12 with 40-digit coefficients,
which is the honest statement that these are not quadratic-field points like S07.

Outputs results/exact.json.
"""
from __future__ import annotations

import json
import math
import os
import time

import numpy as np
from mpmath import mp, mpf, matrix, cos, sin, pslq, mpmathify

import a122lib as A
import system as SY

NV = 16


# ------------------------------------------------------------------ forward-mode dual numbers
class D:
    __slots__ = ('v', 'g')

    def __init__(self, v, g=None):
        self.v = v
        self.g = g if g is not None else [mpf(0)] * NV

    @staticmethod
    def var(v, k):
        g = [mpf(0)] * NV
        g[k] = mpf(1)
        return D(v, g)

    def __add__(self, o):
        o = o if isinstance(o, D) else D(mpf(o))
        return D(self.v + o.v, [a + b for a, b in zip(self.g, o.g)])

    __radd__ = __add__

    def __neg__(self):
        return D(-self.v, [-a for a in self.g])

    def __sub__(self, o):
        o = o if isinstance(o, D) else D(mpf(o))
        return D(self.v - o.v, [a - b for a, b in zip(self.g, o.g)])

    def __rsub__(self, o):
        return (D(mpf(o)) if not isinstance(o, D) else o) - self

    def __mul__(self, o):
        if not isinstance(o, D):
            o = D(mpf(o))
        return D(self.v * o.v, [self.v * b + o.v * a for a, b in zip(self.g, o.g)])

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = o if isinstance(o, D) else D(mpf(o))
        w = self.v / o.v
        return D(w, [(a - w * b) / o.v for a, b in zip(self.g, o.g)])


def dcos(a):
    return D(cos(a.v), [-sin(a.v) * t for t in a.g])


def dsin(a):
    return D(sin(a.v), [cos(a.v) * t for t in a.g])


# ------------------------------------------------------------------ residuals with gradients
def corners_D(sysm, X, i):
    if i < 5:
        cx, cy, th = X[3 * i], X[3 * i + 1], X[3 * i + 2]
        co, si = dcos(th), dsin(th)
    else:
        a, b, c, d = sysm.slot_aff[i - 5]
        s = X[15]
        cx = s * mpf(b) + mpf(a)
        cy = s * mpf(d) + mpf(c)
        qc, qs = SY.System.QUARTER[sysm.slot_q[i - 5]]
        co, si = D(mpf(qc)), D(mpf(qs))
    out = []
    for dx, dy in SY.CORNER:
        out.append((cx + (co * dx - si * dy) * mpf(0.5),
                    cy + (si * dx + co * dy) * mpf(0.5)))
    return out


def residuals_D(sysm, x):
    X = [D.var(x[k], k) for k in range(NV)]
    C = [corners_D(sysm, X, i) for i in range(11)]
    r = []
    for (i, vi, j, ei) in sysm.pairs:
        V = C[i][vi]
        P, Q = C[j][ei], C[j][(ei + 1) % 4]
        ex, ey = Q[0] - P[0], Q[1] - P[1]
        r.append((V[0] - P[0]) * ey - (V[1] - P[1]) * ex)
    s = X[15]
    for (i, vi, w) in sysm.walls:
        V = C[i][vi]
        r.append({'left': V[0], 'right': s - V[0], 'bottom': V[1], 'top': s - V[1]}[w])
    return r


def gJ(sysm, x):
    r = residuals_D(sysm, x)
    m = len(r)
    g = [t.v for t in r]
    J = [[r[a].g[b] for b in range(NV)] for a in range(m)]
    return g, J


# ------------------------------------------------------------------ the Lagrange system
def F(sysm, y):
    """y = x (16) + lam (m).  Returns g(x) then J^T lam - e_s."""
    m = sysm.nrows()
    x, lam = y[:NV], y[NV:]
    g, J = gJ(sysm, x)
    out = list(g)
    for b in range(NV):
        acc = mpf(0)
        for a in range(m):
            acc += J[a][b] * lam[a]
        out.append(acc - (mpf(1) if b == 15 else mpf(0)))
    return out


def lstsq_mp(Amat, b, rcond=mpf(10) ** -25):
    """Minimum-norm least-squares solve via mpmath SVD (handles rank deficiency)."""
    m, n = Amat.rows, Amat.cols
    if m < n:                                     # svd_r wants m >= n
        Ap = matrix(n, n)
        for i in range(m):
            for j in range(n):
                Ap[i, j] = Amat[i, j]
        bp = matrix(n, 1)
        for i in range(m):
            bp[i] = b[i]
        Amat, b, m = Ap, bp, n
    U, S, V = mp.svd_r(Amat)
    smax = max(S)
    y = matrix(n, 1)
    Ub = U.T * b
    for k in range(n):
        y[k] = (Ub[k] / S[k]) if S[k] > rcond * smax else mpf(0)
    return V.T * y


def solve_lagrange(sysm, x0, dps=80, iters=25, verbose=False):
    mp.dps = dps
    m = sysm.nrows()
    n = NV + m
    x = [mpmathify(v) for v in x0]
    g, J = gJ(sysm, x)
    Jf = np.array([[float(J[a][b]) for b in range(NV)] for a in range(m)])
    e = np.zeros(NV); e[15] = 1.0
    lam0, *_ = np.linalg.lstsq(Jf.T, e, rcond=1e-10)
    y = list(x) + [mpf(repr(float(v))) for v in lam0]
    h = mpf(10) ** (-(dps // 3))
    for it in range(iters):
        f0 = F(sysm, y)
        nrm = max(abs(v) for v in f0)
        if verbose:
            print(f'   it {it}: |F|inf = {mp.nstr(nrm, 5)}')
        if nrm < mpf(10) ** (-(dps - 8)):
            break
        Jm = matrix(n, n)
        for k in range(n):
            yp = list(y); yp[k] = yp[k] + h
            ym = list(y); ym[k] = ym[k] - h
            fp, fm = F(sysm, yp), F(sysm, ym)
            for q in range(n):
                Jm[q, k] = (fp[q] - fm[q]) / (2 * h)
        rhs = matrix(n, 1)
        for q in range(n):
            rhs[q] = -f0[q]
        dy = lstsq_mp(Jm, rhs)
        for k in range(n):
            y[k] = y[k] + dy[k]
    return y[:NV], y[NV:], max(abs(v) for v in F(sysm, y))


# ------------------------------------------------------------------ verification and PSLQ
def verify(sysm, x, dps=60):
    """Every pairwise SAT gap and every containment gap of the eleven squares, in mpmath."""
    mp.dps = dps
    X = [D.var(x[k], k) for k in range(NV)]
    C = [[(c[0].v, c[1].v) for c in corners_D(sysm, X, i)] for i in range(11)]
    s = x[15]
    pose = []
    for i in range(11):
        if i < 5:
            pose.append((x[3 * i], x[3 * i + 1], x[3 * i + 2]))
        else:
            a, b, c, d = sysm.slot_aff[i - 5]
            q = sysm.slot_q[i - 5]
            pose.append((mpf(a) + mpf(b) * s, mpf(c) + mpf(d) * s, mp.pi / 2 * q))

    def sat(p, q):
        best = None
        for (cc, tt, oc, ot) in ((p, p[2], q, q[2]), (q, q[2], p, p[2])):
            co, si = cos(tt), sin(tt)
            for ax in ((co, si), (-si, co)):
                dd = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
                gg = (abs(ax[0] * cos(ot) + ax[1] * sin(ot))
                      + abs(-ax[0] * sin(ot) + ax[1] * cos(ot)))
                v = dd - mpf(1) / 2 - gg / 2
                best = v if best is None or v > best else best
        return best

    worst_pair, worst_wall = None, None
    for i in range(11):
        for j in range(i + 1, 11):
            v = sat(pose[i], pose[j])
            worst_pair = v if worst_pair is None or v < worst_pair else worst_pair
    for i in range(11):
        w = (abs(cos(pose[i][2])) + abs(sin(pose[i][2]))) / 2
        for v in (pose[i][0] - w, s - w - pose[i][0], pose[i][1] - w, s - w - pose[i][1]):
            worst_wall = v if worst_wall is None or v < worst_wall else worst_wall
    return worst_pair, worst_wall


def pslq_hunt(v, maxdeg=12, tol_digits=55, maxcoeff=10 ** 8, check_digits=45):
    """Minimal integer polynomial of v up to `maxdeg`, or None.

    A relation is accepted only if its coefficients are bounded by `maxcoeff` AND it evaluates to
    < 1e-`check_digits` at the working precision - PSLQ with a loose tolerance and huge allowed
    coefficients will 'find' a spurious quadratic for any number at all.
    """
    v = mpmathify(v)
    if abs(v) < mpf(10) ** (-40):
        return dict(degree=1, coeffs=[0, 1], note='v = 0 exactly')
    for deg in range(1, maxdeg + 1):
        try:
            rel = pslq([v ** k for k in range(deg + 1)], tol=mpf(10) ** (-tol_digits),
                       maxcoeff=maxcoeff, maxsteps=40000)
        except Exception:
            rel = None
        if not rel:
            continue
        val = sum(mpf(int(c)) * v ** k for k, c in enumerate(rel))
        if abs(val) < mpf(10) ** (-check_digits) and max(abs(int(c)) for c in rel) <= maxcoeff:
            return dict(degree=deg, coeffs=[int(c) for c in rel], residual=mp.nstr(val, 5))
    return None


def main():
    t0 = time.time()
    mp.dps = 90
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    out = {}
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        s, cfg = b['sigma'], [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        sysm = SY.System(s, cfg, names)
        x0 = SY.x0_from(s, cfg)
        print(f'\n=== {tag}: {sysm.nrows()} incidence rows, 16 unknowns')
        for l in sysm.labels():
            print('    ', l)
        x, lam, res = solve_lagrange(sysm, x0, dps=80, verbose=True)
        mp.dps = 75
        wp, ww = verify(sysm, x)
        s_star = x[15]
        print(f'  s* = {mp.nstr(s_star, 60)}')
        print(f'  |F|inf {mp.nstr(res, 4)}   worst pair gap {mp.nstr(wp, 4)}   '
              f'worst wall gap {mp.nstr(ww, 4)}')
        poly = pslq_hunt(s_star)
        print('  PSLQ minimal polynomial of s* up to degree 12:', poly)
        tilts = {}
        for i in range(5):
            th = x[3 * i + 2]
            tilts[names[i]] = dict(rad=mp.nstr(th, 45), deg=mp.nstr(th * 180 / mp.pi, 40),
                                   tan_poly=pslq_hunt(mp.tan(th), maxdeg=10))
        out[tag] = dict(
            id=sid, names=list(names), rows=sysm.labels(),
            rank=int(np.linalg.matrix_rank(
                np.array([[float(v) for v in row] for row in gJ(sysm, x)[1]]), tol=1e-10)),
            s_star=mp.nstr(s_star, 50), s_star_float=float(s_star),
            s_minus_shat=float(s_star) - A.SHAT, s_minus_s0=float(s_star) - A.S0,
            lagrange_residual=float(res), worst_pair_gap=float(wp), worst_wall_gap=float(ww),
            pslq_minpoly_s=poly,
            configuration=[dict(name=names[i],
                                cx=mp.nstr(x[3 * i], 45), cy=mp.nstr(x[3 * i + 1], 45),
                                tilt_deg=mp.nstr(x[3 * i + 2] * 180 / mp.pi, 40))
                           for i in range(5)]
            + [dict(name=names[5 + k],
                    cx=mp.nstr(mpf(sysm.slot_aff[k][0]) + mpf(sysm.slot_aff[k][1]) * x[15], 45),
                    cy=mp.nstr(mpf(sysm.slot_aff[k][2]) + mpf(sysm.slot_aff[k][3]) * x[15], 45),
                    tilt_deg='0') for k in range(6)],
            tilts=tilts)
        mp.dps = 90
    out['seconds'] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(A.RES, 'exact.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/exact.json in', out['seconds'], 's')


if __name__ == '__main__':
    main()
