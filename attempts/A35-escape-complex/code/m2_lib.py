"""m2_lib.py -- A35 / M2 (per-stratum certificate reach): shared machinery.

Builds on strata_lib (M1) which builds on A22's krawczyk_cert.json and A30's
t3lib interval jets.  Nothing here forks strata_lib; it only adds

  * lambda*      : the 38 exact rationals from M1 (results/m1_strata.json)
  * FLOAT row evaluation / Jacobian (fast Newton + LP work along routes)
  * Krawczyk machinery over a box with a rational centre, in two flavours
      - [RFP]  numpy float64 with an explicit Rump rounding bound  (fast)
      - [IV]   mpmath.iv, recheck.py style                          (rigorous)
  * interval bounds for the inflation lemma: r_res(r), Hbar(r), beta(r), kappa
  * LP for the local multiplier cone floor on a retained row set

RIGOUR TAGS as in M1: [IV] mpmath.iv; [RFP] rigorous float64 (Rump bound,
rigorous modulo IEEE-754); [NUM] plain float64, NOT rigorous.
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction

import numpy as np
from mpmath import iv, mp

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

RESULTS = os.path.abspath(os.path.join(HERE, '..', 'results'))

NV = SL.NV            # 34
NGEO = SL.NGEO        # 38
S_IDX = SL.S_IDX      # 33
NSQ = SL.NSQ          # 11

HALF = [(Fraction(-1, 2), Fraction(-1, 2)), (Fraction(1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)), (Fraction(-1, 2), Fraction(1, 2))]
NHAT = [(0, -1), (1, 0), (0, 1), (-1, 0)]

EPS64 = float(np.finfo(float).eps) / 2.0      # unit roundoff


# ------------------------------------------------------------------ M1 data

_M1 = None


def m1():
    global _M1
    if _M1 is None:
        with open(os.path.join(RESULTS, 'm1_strata.json')) as f:
            _M1 = json.load(f)
    return _M1


def lam_star():
    """lambda* as 38 exact Fractions (M1 task1.lambda_star)."""
    return [SL.str_frac(s) for s in m1()['task1']['lambda_star']['lambda_rational']]


def lam_floor():
    """min_k lambda*_k, exact Fraction."""
    return SL.str_frac(m1()['task1']['lambda_star']['min_lambda_exact'])


def survivors():
    return [tuple(b) for b in m1()['synthesis']['global_exhaustive']['survivors']]


def empty_alive():
    return [tuple(b) for b in
            m1()['synthesis']['global_exhaustive']['empty_and_cone_alive']]


def row_names():
    return m1()['meta']['row_names']


def a22_Y():
    """A22's 34x34 preconditioner as exact Fractions (rows indexed by S order)."""
    c = SL.load_cert()
    return [[SL.str_frac(v) for v in row] for row in c['Y']]


def a22_S():
    return list(SL.load_cert()['S'])


def a22_rN():
    return SL.str_frac(SL.load_cert()['r_N'])


# ------------------------------------------------------- FLOAT row language
# Same formulas as A22/recheck.py eval_g / grad_g, in float64.  [NUM]

_CONS = None


def cons():
    global _CONS
    if _CONS is None:
        _CONS = SL.geo_constraints()
    return _CONS


def _rotf(th, vx, vy):
    c, s = math.cos(th), math.sin(th)
    return vx * c - vy * s, vx * s + vy * c


def _drotf(th, vx, vy):
    c, s = math.cos(th), math.sin(th)
    return -vx * s - vy * c, vx * c - vy * s


def _cornerf(z, i, corner):
    hx, hy = float(HALF[corner][0]), float(HALF[corner][1])
    rx, ry = _rotf(z[3 * i + 2], hx, hy)
    return z[3 * i] + rx, z[3 * i + 1] + ry


def eval_g_f(z, c):
    if c['kind'] == 'wall':
        qx, qy = _cornerf(z, c['i'], c['corner'])
        return {'x=0': qx, 'y=0': qy,
                'x=s': z[33] - qx, 'y=s': z[33] - qy}[c['wall']]
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        qx, qy = _cornerf(z, i, c['corner'])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = _rotf(z[3 * j + 2], float(nhx), float(nhy))
        return nx * (qx - z[3 * j]) + ny * (qy - z[3 * j + 1]) - 0.5
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        return dx * dx + dy * dy - 1.0
    raise ValueError(c['kind'])


def grad_g_f(z, c):
    g = {}
    if c['kind'] == 'wall':
        i = c['i']
        hx, hy = float(HALF[c['corner']][0]), float(HALF[c['corner']][1])
        dx, dy = _drotf(z[3 * i + 2], hx, hy)
        w = c['wall']
        if w == 'x=0':
            g[3 * i] = 1.0; g[3 * i + 2] = dx
        elif w == 'y=0':
            g[3 * i + 1] = 1.0; g[3 * i + 2] = dy
        elif w == 'x=s':
            g[3 * i] = -1.0; g[3 * i + 2] = -dx; g[33] = 1.0
        else:
            g[3 * i + 1] = -1.0; g[3 * i + 2] = -dy; g[33] = 1.0
        return g
    if c['kind'] == 'edge':
        i, j = c['i'], c['j']
        hx, hy = float(HALF[c['corner']][0]), float(HALF[c['corner']][1])
        nhx, nhy = NHAT[c['edge']]
        nx, ny = _rotf(z[3 * j + 2], float(nhx), float(nhy))
        qx, qy = _cornerf(z, i, c['corner'])
        wx, wy = qx - z[3 * j], qy - z[3 * j + 1]
        dhx, dhy = _drotf(z[3 * i + 2], hx, hy)
        dnx, dny = _drotf(z[3 * j + 2], float(nhx), float(nhy))
        g[3 * i] = nx; g[3 * i + 1] = ny
        g[3 * j] = -nx; g[3 * j + 1] = -ny
        g[3 * i + 2] = nx * dhx + ny * dhy
        g[3 * j + 2] = dnx * wx + dny * wy
        return g
    if c['kind'] == 'dist':
        i, j = c['i'], c['j']
        dx = z[3 * i] - z[3 * j]
        dy = z[3 * i + 1] - z[3 * j + 1]
        g[3 * i] = 2 * dx; g[3 * i + 1] = 2 * dy
        g[3 * j] = -2 * dx; g[3 * j + 1] = -2 * dy
        return g
    raise ValueError(c['kind'])


def vals_f(z, rows=None):
    C = cons()
    idx = range(NGEO) if rows is None else rows
    return np.array([eval_g_f(z, C[k]) for k in idx])


def jac_f(z, rows=None):
    C = cons()
    idx = list(range(NGEO)) if rows is None else list(rows)
    A = np.zeros((len(idx), NV))
    for r, k in enumerate(idx):
        for gi, v in grad_g_f(z, C[k]).items():
            A[r, gi] = v
    return A


def zhat_f():
    return np.array([float(x) for x in SL.z_hat()])


# ------------------------------------------------ interval Jacobian helpers

def box_around(zc, r):
    """box(zc, r) as 34 iv.mpf.  zc: list of Fraction OR float; r: Fraction/float."""
    return t3lib.box_from(list(zc), r)


def iv_mag(x):
    return max(abs(float(x.a)), abs(float(x.b)))


def iv_sup(x):
    return float(x.b)


def iv_inf(x):
    return float(x.a)


def jac_iv_rows(box, rows):
    """(interval values, interval gradient dicts) for the given row indices."""
    R = SL.geo_rows()
    vals, grads = [], []
    for k in rows:
        j = SL.eval_geo(box, R[k], order=1)
        vals.append(j.v)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(R[k]['vars'])})
    return vals, grads


def jac_mid_rad(box, rows):
    """float64 (mid, rad) arrays of the interval Jacobian, plus value ivs."""
    vals, grads = jac_iv_rows(box, rows)
    n = len(rows)
    mid = np.zeros((n, NV))
    rad = np.zeros((n, NV))
    for r in range(n):
        for gi, x in grads[r].items():
            m, rr = SL._iv_mid_rad(x)
            mid[r, gi] = m
            rad[r, gi] = rr
    return mid, rad, vals


# ------------------------------------------------------- Krawczyk  [RFP]
# For a SQUARE system F = (g_k)_{k in S} on box(zc, h) with zc rational:
#   K(box) = zc - Y F(zc) + (I - Y A(box)) (box - zc)
# Contraction (K strictly inside box) => F has exactly one zero in box.
# We bound everything with float64 + Rump rounding terms.

def rump_gamma(k):
    return k * EPS64 / (1.0 - k * EPS64)


def krawczyk_rfp(zc_frac, h, S, Y=None, Fc=None):
    """[RFP] Krawczyk test for rows S (len 34) on box(zc_frac, h).

    zc_frac : list of 34 Fractions (exact centre)
    h       : Fraction or float radius
    Fc      : optional dict {k: (lo, hi)} float enclosure of g_k(zc); if None
              an [IV] evaluation at the (degenerate) centre box is used.
    Returns dict(ok, beta, radK, kappa, margin).
       beta  = upper bound of ||I - Y A(box)||_inf
       radK  = upper bound of ||K - zc||_inf
       ok    = radK < h  (strict) and beta < 1
    """
    S = list(S)
    assert len(S) == NV
    hf = float(h)
    box = box_around(zc_frac, h)
    mid, rad, _ = jac_mid_rad(box, S)
    if Y is None:
        try:
            Y = np.linalg.inv(mid)
        except np.linalg.LinAlgError:
            return dict(ok=False, beta=float('inf'), radK=float('inf'),
                        kappa=float('inf'), margin=-1.0)
        if not np.all(np.isfinite(Y)):
            return dict(ok=False, beta=float('inf'), radK=float('inf'),
                        kappa=float('inf'), margin=-1.0)
    aY = np.abs(Y)
    E = np.eye(NV) - Y @ mid
    g = rump_gamma(NV + 2)
    errE = g * (aY @ np.abs(mid)) + aY @ rad
    Brow = np.sum(np.abs(E) + errE, axis=1)
    beta = float(np.max(Brow))
    kappa = float(np.max(np.sum(aY, axis=1)))
    # F(zc): interval at the degenerate centre box
    if Fc is None:
        pbox = [t3lib._to_iv(x) for x in zc_frac]
        R = SL.geo_rows()
        fmag = np.array([iv_mag(SL.eval_geo(pbox, R[k], order=0).v) for k in S])
    else:
        fmag = np.array([max(abs(Fc[k][0]), abs(Fc[k][1])) for k in S])
    t1 = aY @ fmag
    t1 = t1 * (1.0 + rump_gamma(NV + 2)) + 1e-300
    radK = float(np.max(t1 + Brow * hf))
    return dict(ok=bool(radK < hf and beta < 1.0), beta=beta, radK=radK,
                kappa=kappa, margin=float(hf - radK))


def krawczyk_iv(zc_frac, h, S, Yq):
    """[IV] Krawczyk test, recheck.py style, mpmath.iv only.

    Yq : 34x34 rational preconditioner (list of lists of Fraction).
    Returns dict(ok, beta, radK, kappa).
    """
    S = list(S)
    box = box_around(zc_frac, h)
    pbox = [t3lib._to_iv(x) for x in zc_frac]
    R = SL.geo_rows()
    Fc = [SL.eval_geo(pbox, R[k], order=0).v for k in S]
    _, grads = jac_iv_rows(box, S)
    Yiv = [[t3lib._to_iv(v) for v in row] for row in Yq]
    hiv = t3lib._to_iv(h)
    dbox = iv.mpf([(-hiv).a, hiv.b])
    ok = True
    radK = 0.0
    beta = 0.0
    kappa = 0.0
    for i in range(NV):
        acc = iv.mpf(0)
        for rr in range(NV):
            acc = acc + Yiv[i][rr] * Fc[rr]
        Ki = -acc
        rowsum = iv.mpf(0)
        for j in range(NV):
            m = iv.mpf(1) if i == j else iv.mpf(0)
            ssum = iv.mpf(0)
            for rr in range(NV):
                v = grads[rr].get(j)
                if v is not None:
                    ssum = ssum + Yiv[i][rr] * v
            e = m - ssum
            rowsum = rowsum + abs(e)
            Ki = Ki + e * dbox
        beta = max(beta, iv_sup(rowsum))
        kappa = max(kappa, sum(abs(float(Yq[i][rr])) for rr in range(NV)))
        radK = max(radK, iv_mag(Ki))
        if not (Ki.a > (-hiv).a and Ki.b < hiv.b):
            ok = False
    return dict(ok=bool(ok and beta < 1.0), beta=beta, radK=radK, kappa=kappa,
                margin=float(h) - radK)


def pick_basis(rows, Amid):
    """34 independent rows out of `rows` by column-pivoted QR."""
    from scipy.linalg import qr
    rows = list(rows)
    sub = Amid[rows]
    _, _, piv = qr(sub.T, pivoting=True, mode='economic')
    return sorted(rows[p] for p in piv[:NV])


# --------------------------------------------------- inflation-lemma bounds

def res_l1_box(box, lam):
    """[IV] upper bound of  sup_{z in box} || A(z)^T lam - e_s ||_1 .

    lam: 38 Fractions.  Returns (float bound, per-coordinate mags).
    """
    R = SL.geo_rows()
    acc = [iv.mpf(0)] * NV
    for k in range(NGEO):
        lk = t3lib._to_iv(lam[k])
        j = SL.eval_geo(box, R[k], order=1)
        for loc, gi in enumerate(R[k]['vars']):
            acc[gi] = acc[gi] + lk * j.g[loc]
    mags = []
    tot = 0.0
    for gi in range(NV):
        t = acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0))
        m = iv_mag(t)
        mags.append(m)
        tot += m
    return tot, mags


def hess_bounds_box(box, lam):
    """[IV] Hessian bounds for Phi = s - sum_k lam_k g_k on `box`.

    Returns (Hsum, Hinf) where
       Hsum = sum_{i,j} sup_box |d2 Phi / dz_i dz_j|
       Hinf = max_i sum_j sup_box |d2 Phi / dz_i dz_j|   (interval matrix
              inf-norm of the entrywise magnitude matrix)
    NORM INEQUALITY USED (stated precisely):
       for d = z - zhat with ||d||_inf <= r,
         |d^T H d| = |sum_{i,j} H_ij d_i d_j| <= sum_{i,j} |H_ij| |d_i| |d_j|
                   <= (sum_{i,j} sup|H_ij|) * ||d||_inf^2 = Hsum * r^2 .
       Hsum <= NV * Hinf always, so the Hinf form  |d^T H d| <= NV*Hinf*r^2
       is also valid but weaker; we use Hsum (the rows are sparse: each g_k
       touches <= 7 of the 34 variables, so Hsum << NV*Hinf).
    """
    R = SL.geo_rows()
    Hm = np.zeros((NV, NV))
    acc = {}
    for k in range(NGEO):
        lk = t3lib._to_iv(lam[k])
        j = SL.eval_geo(box, R[k], order=2)
        vs = R[k]['vars']
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                cur = acc.get(key)
                term = lk * j.h[a][b]
                acc[key] = term if cur is None else cur + term
    for (a, b), x in acc.items():
        Hm[a, b] = iv_mag(x)          # Phi's Hessian is -(sum lam H_g); |.| same
    Hsum = float(Hm.sum())
    Hinf = float(np.max(np.sum(Hm, axis=1)))
    return Hsum, Hinf


def g_max_at_zhat():
    """[IV] max_k |g_k(z-hat)| over the 38 geometric rows (~6.7e-60).

    Needed because the rigidity step bounds ||F_S(z) - F_S(z-hat)||_inf, and
    F_S(z-hat) is only zero to this accuracy (z-hat is A22's rational centre).
    """
    pbox = [t3lib._to_iv(x) for x in SL.z_hat()]
    R = SL.geo_rows()
    return max(iv_mag(SL.eval_geo(pbox, r, order=0).v) for r in R)


# ------------------------------------------------------------ cone floor LP

def cone_floor(A_rows, tol=0.0):
    """Chebyshev LP:  max t  s.t.  A_rows^T lam = e_s,  lam >= t, t free.

    A_rows: (m, 34) float array of retained-row gradients.
    Returns (t_opt or None if infeasible, lam vector or None).
    A positive t means e_s is in the INTERIOR of the retained cone with floor t.
    """
    from scipy.optimize import linprog
    m = A_rows.shape[0]
    # variables: [lam (m), t]
    c = np.zeros(m + 1)
    c[-1] = -1.0
    Aeq = np.zeros((NV, m + 1))
    Aeq[:, :m] = A_rows.T
    beq = np.zeros(NV)
    beq[S_IDX] = 1.0
    # lam_i - t >= 0  ->  -lam_i + t <= 0
    Aub = np.zeros((m, m + 1))
    Aub[:, :m] = -np.eye(m)
    Aub[:, -1] = 1.0
    bub = np.zeros(m)
    bounds = [(0, None)] * m + [(None, 10.0)]
    try:
        res = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=beq,
                      bounds=bounds, method='highs')
    except Exception:
        return None, None
    if not res.success:
        return None, None
    return float(-res.fun), np.array(res.x[:m])


# ---------------------------------------------------------- misc

def fs(x):
    return '%d/%d' % (x.numerator, x.denominator)


def rat(x, den):
    return Fraction(round(Fraction(float(x)) * den), den)


def frac_vec(zf, den=10 ** 30):
    return [rat(v, den) for v in zf]
