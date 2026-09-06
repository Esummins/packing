"""A106 T2 engine — full 11-square local minimisation of the side under a class's pins.

Geometry and the penalty/SLSQP pipeline are A04's `pack11.py` (unit squares, SAT overlap,
L-BFGS-B penalty continuation -> SLSQP polish on frozen separating axes), reduced to the
class's own variety:

    11 squares.  k = 5 of them are the CLASS PINS: axis-aligned (theta = 0), centres on the
    class slot lines c(s) = alpha + beta*s with beta in {0,1} (A56 P1 / A57 slots_at).
    The remaining 6 squares are free.  Variables z = (6 x (x, y, theta), s), 19 of them.

    x_full = c0 + M z    (M constant, 34 x 19) so every gradient/Jacobian of A04's
    full-space functions is pulled back exactly by M^T.

Constraints kept: pin-free and free-free SAT pairs (40 of the 55), containment of the 6
free squares (24 rows).  Pin-pin pairs and pin containment are IDENTICALLY satisfied for
s >= 3 (they are the slot geometry itself: pins touch exactly, and s - (s - 1/2) - 1/2 = 0),
so they are dropped rather than handed to SLSQP as zero-gradient active rows.

`certify_endpoint` re-checks the landing rigorously in interval arithmetic (mpmath iv,
250-bit) on a RATIONAL rounding of the configuration, inflating s by the smallest eps on a
ladder until every pair is strictly separated on some axis and every square is contained:
that is an exact witness that the local minimum is a real packing of the class at side
s* + eps, not a numerical artefact.

BLAS is pinned before numpy is imported.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import math
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import minimize

N = 11
H = 0.5
I_IDX, J_IDX = np.triu_indices(N, 1)
NP_ = len(I_IDX)

S0 = 969271 / 250000.0          # 3.877084


# --------------------------------------------------------------- class pins
def slot_affine(c_at_s0, s0=S0):
    """(alpha, beta) with c(s) = alpha + beta*s, beta in {0,1}; refuse anything else."""
    for a in (0.5, 1.5, 2.5):
        if abs(c_at_s0 - a) < 1e-6:
            return (a, 0.0)
        if abs(c_at_s0 - (s0 - a)) < 1e-6:
            return (-a, 1.0)
    raise ValueError(f"slot coordinate {c_at_s0} is neither L- nor R-anchored")


def pin_affine(slots):
    """slots at s0 -> [((ax,bx),(ay,by))] per pin."""
    return [(slot_affine(x), slot_affine(y)) for (x, y) in slots]


def pins_at(aff, s):
    return np.array([[ax + bx * s, ay + by * s] for ((ax, bx), (ay, by)) in aff])


# --------------------------------------------------------------- reduction map
PIN_HW = 0.01 / math.sqrt(2.0)      # A57's live delta = 1e-2 slack cores: half-width per axis


class Reduction:
    """x_full(34) = c0 + M z.  Squares 0..k-1 are the class pins, k..10 free.

    z = [ free 6 x (x, y, theta) | pin offsets u (k x 2, only when pin_hw > 0) | s ].

    pin_hw = 0            : the pins sit EXACTLY on the class slot lines c(s) = alpha + beta*s.
    pin_hw = PIN_HW       : the pins may move inside A57's live delta = 1e-2 slack core boxes
                            (|u|_inf <= 0.01/sqrt2 per axis, theta still exactly 0) — which is
                            the hypothesis the live A57 certificates actually have to exclude.
    """

    def __init__(self, aff, pin_hw=0.0):
        self.aff = aff
        k = len(aff)
        self.k = k
        self.nfree = N - k
        self.pin_hw = float(pin_hw)
        self.nu = 2 * k if self.pin_hw > 0 else 0
        self.nz = 3 * self.nfree + self.nu + 1
        M = np.zeros((3 * N + 1, self.nz))
        c0 = np.zeros(3 * N + 1)
        for p, ((ax, bx), (ay, by)) in enumerate(aff):
            c0[2 * p] = ax
            c0[2 * p + 1] = ay
            M[2 * p, self.nz - 1] = bx
            M[2 * p + 1, self.nz - 1] = by
            if self.nu:
                # the pin-offset variables are SCALED to [-1, 1] (u = pin_hw * z): without
                # this the |u| <= 7e-3 block against s ~ 4 stalls the penalty continuation.
                M[2 * p, 3 * self.nfree + 2 * p] = self.pin_hw
                M[2 * p + 1, 3 * self.nfree + 2 * p + 1] = self.pin_hw
            # theta_p = 0 always
        for f in range(self.nfree):
            i = k + f
            M[2 * i, 3 * f] = 1.0
            M[2 * i + 1, 3 * f + 1] = 1.0
            M[2 * N + i, 3 * f + 2] = 1.0
        M[3 * N, self.nz - 1] = 1.0
        self.M = M
        self.c0 = c0
        if self.pin_hw > 0:
            # the pins move, so every pair and every containment row is live
            self.pair_keep = np.ones(NP_, bool)
            self.cont_keep = np.ones(4 * N, bool)
        else:
            # pin-pin pairs and pin containment are identically satisfied: drop them
            self.pair_keep = np.array([(I_IDX[p] >= k) or (J_IDX[p] >= k) for p in range(NP_)])
            cm = np.zeros(4 * N, bool)
            for i in range(k, N):
                cm[i] = cm[N + i] = cm[2 * N + i] = cm[3 * N + i] = True
            self.cont_keep = cm
        b = [(None, None)] * self.nz
        for j in range(self.nu):
            b[3 * self.nfree + j] = (-1.0, 1.0)
        b[self.nz - 1] = (2.0, 5.0)
        self.base_bounds = b

    def x(self, z):
        return self.c0 + self.M @ z

    def z(self, c, th, s, u=None):
        z = np.zeros(self.nz)
        for f in range(self.nfree):
            i = self.k + f
            z[3 * f], z[3 * f + 1], z[3 * f + 2] = c[i, 0], c[i, 1], th[i]
        if self.nu:
            pins = pins_at(self.aff, s)
            for p in range(self.k):
                du = (c[p] - pins[p]) if u is None else np.asarray(u[p])
                z[3 * self.nfree + 2 * p] = float(np.clip(du[0] / self.pin_hw, -1.0, 1.0))
                z[3 * self.nfree + 2 * p + 1] = float(np.clip(du[1] / self.pin_hw, -1.0, 1.0))
        z[-1] = s
        return z


# --------------------------------------------------------------- A04 geometry (verbatim maths)
def unpack(x):
    return x[:2 * N].reshape(N, 2), x[2 * N:3 * N], x[3 * N]


def pair_overlaps(x):
    c, th, s = unpack(x)
    a = c[I_IDX]; b = c[J_IDX]; d = a - b
    al = th[I_IDX]; be = th[J_IDX]
    ca, sa = np.cos(al), np.sin(al)
    cb, sb = np.cos(be), np.sin(be)
    phi = al - be
    cph, sph = np.cos(phi), np.sin(phi)
    r = H * (np.abs(cph) + np.abs(sph))
    rp = H * (-np.sign(cph) * sph + np.sign(sph) * cph)
    n = np.empty((NP_, 4, 2)); npr = np.empty((NP_, 4, 2))
    n[:, 0, 0] = ca; n[:, 0, 1] = sa; npr[:, 0, 0] = -sa; npr[:, 0, 1] = ca
    n[:, 1, 0] = -sa; n[:, 1, 1] = ca; npr[:, 1, 0] = -ca; npr[:, 1, 1] = -sa
    n[:, 2, 0] = cb; n[:, 2, 1] = sb; npr[:, 2, 0] = -sb; npr[:, 2, 1] = cb
    n[:, 3, 0] = -sb; n[:, 3, 1] = cb; npr[:, 3, 0] = -cb; npr[:, 3, 1] = -sb
    dn = np.einsum('pj,pkj->pk', d, n)
    ov = H + r[:, None] - np.abs(dn)
    return ov, dict(d=d, n=n, npr=npr, dn=dn, rp=rp)


def sat_min_overlap(x):
    ov, _ = pair_overlaps(x)
    return ov.min(axis=1)


def container_viol(x):
    c, th, s = unpack(x)
    e = H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    return np.concatenate([e - c[:, 0], c[:, 0] + e - s, e - c[:, 1], c[:, 1] + e - s])


def obj_grad_full(x, mu):
    """A04's penalty objective in full space: s + mu*(overlap^2 + container^2)."""
    c, th, s = unpack(x)
    ov, aux = pair_overlaps(x)
    kmin = np.argmin(ov, axis=1)
    ar = np.arange(NP_)
    o = ov[ar, kmin]
    act = o > 0
    f = s
    g = np.zeros(3 * N + 1)
    g[3 * N] = 1.0
    if act.any():
        nn = aux['n'][ar, kmin]; nnp = aux['npr'][ar, kmin]; dn = aux['dn'][ar, kmin]
        sg = np.sign(dn); d = aux['d']; rp = aux['rp']
        ownerA = kmin < 2
        dnp = np.einsum('mj,mj->m', d, nnp)
        g_al = rp - np.where(ownerA, sg * dnp, 0.0)
        g_be = -rp - np.where(~ownerA, sg * dnp, 0.0)
        ga = -sg[:, None] * nn
        w = 2.0 * mu * o
        f += mu * float(np.sum(o[act] ** 2))
        for p in np.nonzero(act)[0]:
            i, j = I_IDX[p], J_IDX[p]
            g[2 * i:2 * i + 2] += w[p] * ga[p]
            g[2 * j:2 * j + 2] -= w[p] * ga[p]
            g[2 * N + i] += w[p] * g_al[p]
            g[2 * N + j] += w[p] * g_be[p]
    cv = container_viol(x)
    cth, sth = np.cos(th), np.sin(th)
    e = H * (np.abs(cth) + np.abs(sth))
    de = H * (-np.sign(cth) * sth + np.sign(sth) * cth)
    cact = cv > 0
    if cact.any():
        f += mu * float(np.sum(cv[cact] ** 2))
        w = 2.0 * mu * cv
        for i in range(N):
            if cv[i] > 0:
                g[2 * i] -= w[i]; g[2 * N + i] += w[i] * de[i]
            if cv[N + i] > 0:
                g[2 * i] += w[N + i]; g[2 * N + i] += w[N + i] * de[i]; g[3 * N] -= w[N + i]
            if cv[2 * N + i] > 0:
                g[2 * i + 1] -= w[2 * N + i]; g[2 * N + i] += w[2 * N + i] * de[i]
            if cv[3 * N + i] > 0:
                g[2 * i + 1] += w[3 * N + i]; g[2 * N + i] += w[3 * N + i] * de[i]; g[3 * N] -= w[3 * N + i]
    return f, g


def _pair_con_full(x, kfix):
    ov, aux = pair_overlaps(x)
    ar = np.arange(NP_)
    val = -ov[ar, kfix]
    J = np.zeros((NP_, 3 * N + 1))
    nn = aux['n'][ar, kfix]; nnp = aux['npr'][ar, kfix]; dn = aux['dn'][ar, kfix]
    sg = np.sign(dn); d = aux['d']; rp = aux['rp']
    ownerA = kfix < 2
    dnp = np.einsum('mj,mj->m', d, nnp)
    g_al = rp - np.where(ownerA, sg * dnp, 0.0)
    g_be = -rp - np.where(~ownerA, sg * dnp, 0.0)
    ga = -sg[:, None] * nn
    for p in range(NP_):
        i, j = I_IDX[p], J_IDX[p]
        J[p, 2 * i:2 * i + 2] = -ga[p]
        J[p, 2 * j:2 * j + 2] = ga[p]
        J[p, 2 * N + i] = -g_al[p]
        J[p, 2 * N + j] = -g_be[p]
    return val, J


def _cont_con_full(x):
    c, th, s = unpack(x)
    cth, sth = np.cos(th), np.sin(th)
    e = H * (np.abs(cth) + np.abs(sth))
    de = H * (-np.sign(cth) * sth + np.sign(sth) * cth)
    val = np.concatenate([c[:, 0] - e, s - c[:, 0] - e, c[:, 1] - e, s - c[:, 1] - e])
    J = np.zeros((4 * N, 3 * N + 1))
    for i in range(N):
        J[i, 2 * i] = 1; J[i, 2 * N + i] = -de[i]
        J[N + i, 2 * i] = -1; J[N + i, 2 * N + i] = -de[i]; J[N + i, 3 * N] = 1
        J[2 * N + i, 2 * i + 1] = 1; J[2 * N + i, 2 * N + i] = -de[i]
        J[3 * N + i, 2 * i + 1] = -1; J[3 * N + i, 2 * N + i] = -de[i]; J[3 * N + i, 3 * N] = 1
    return val, J


# --------------------------------------------------------------- reduced driver
def _wrap(R, z, bounds=None):
    """theta mod 90 deg on every free square, then clip back into the bounds (if any)."""
    z[2:3 * R.nfree:3] = np.mod(z[2:3 * R.nfree:3], np.pi / 2)
    if bounds is not None:
        lo = np.array([b[0] if b[0] is not None else -np.inf for b in bounds])
        hi = np.array([b[1] if b[1] is not None else np.inf for b in bounds])
        z = np.clip(z, lo, hi)
    return z


def penalty_solve(R, z0, mus=(10., 100., 1e3, 1e4, 1e5, 1e6, 1e7, 1e8), maxiter=1200, bounds=None):
    z = z0.copy()

    def fg(z):
        f, g = obj_grad_full(R.x(z), mu)
        return f, R.M.T @ g

    for mu in mus:
        res = minimize(fg, z, jac=True, method='L-BFGS-B', bounds=bounds,
                       options=dict(maxiter=maxiter, maxcor=20, ftol=1e-16, gtol=1e-11))
        z = _wrap(R, res.x, bounds)
    return z


def polish(R, z0, rounds=6, maxiter=400, bounds=None):
    z = z0.copy()
    for _ in range(rounds):
        x = R.x(z)
        ov, _ = pair_overlaps(x)
        kfix = np.argmin(ov, axis=1)
        pk, ck = R.pair_keep, R.cont_keep

        def pf(z, k=kfix):
            return _pair_con_full(R.x(z), k)[0][pk]

        def pj(z, k=kfix):
            return _pair_con_full(R.x(z), k)[1][pk] @ R.M

        def cf(z):
            return _cont_con_full(R.x(z))[0][ck]

        def cj(z):
            return _cont_con_full(R.x(z))[1][ck] @ R.M

        e_s = np.zeros(R.nz); e_s[-1] = 1.0
        res = minimize(lambda z: z[-1], z, jac=lambda z: e_s, bounds=bounds,
                       constraints=[dict(type='ineq', fun=pf, jac=pj),
                                    dict(type='ineq', fun=cf, jac=cj)],
                       method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-14))
        zn = _wrap(R, res.x, bounds)
        xn = R.x(zn)
        if (sat_min_overlap(xn)[R.pair_keep].max() < 1e-7
                and container_viol(xn)[R.cont_keep].max() < 1e-7
                and zn[-1] <= z[-1] + 1e-9):
            z = zn
        else:
            break
        if np.array_equal(np.argmin(pair_overlaps(R.x(z))[0], axis=1), kfix):
            break
    return z


def feasibility(R, z):
    x = R.x(z)
    return (float(sat_min_overlap(x)[R.pair_keep].max()),
            float(container_viol(x)[R.cont_keep].max()))


def minimise(R, z0, bounds=None):
    z = penalty_solve(R, z0, bounds=bounds)
    z = polish(R, z, bounds=bounds)
    ov, cv = feasibility(R, z)
    if max(ov, cv) > 1e-9:                       # one repair round
        z = polish(R, penalty_solve(R, z, mus=(1e6, 1e7, 1e8, 1e9), bounds=bounds),
                   bounds=bounds)
        ov, cv = feasibility(R, z)
    return z, ov, cv


def box_bounds(R, box):
    """R's own bounds (pin slack boxes, s range) plus the node's pose box B on square #k."""
    bnds = list(R.base_bounds)
    bnds[0] = (box["x0"], box["x1"])
    bnds[1] = (box["y0"], box["y1"])
    bnds[2] = (math.radians(box["th0"]), math.radians(box["th1"]))
    return bnds


def clip_to(bnds, z):
    lo = np.array([b[0] if b[0] is not None else -np.inf for b in bnds])
    hi = np.array([b[1] if b[1] is not None else np.inf for b in bnds])
    return np.clip(z, lo, hi)


# --------------------------------------------------------------- margin push at a fixed side
def push_margin(R, z, s_fixed, rounds=3, maxiter=200, bounds=None):
    """At the FIXED side s_fixed > s*, push the free squares (and the pin offsets) to maximise
    the smallest slack m (separation and containment) WITHOUT leaving the node's hypothesis.
    The local minimum has m = 0 at s*, so m grows like c*(s_fixed - s*): that is what makes a
    rounded rational configuration verifiable in interval arithmetic."""
    bnds = list(bounds) if bounds is not None else list(R.base_bounds)
    zz = np.concatenate([clip_to(bnds, z), [0.0]])
    zz[-2] = s_fixed
    lo = np.array([(b[0] if b[0] is not None else -np.inf) for b in bnds] + [-np.inf])
    hi = np.array([(b[1] if b[1] is not None else np.inf) for b in bnds] + [np.inf])
    lo[R.nz - 1] = hi[R.nz - 1] = s_fixed          # freeze s
    pk, ck = R.pair_keep, R.cont_keep
    best = zz.copy()
    for _ in range(rounds):
        x = R.x(best[:R.nz])
        kfix = np.argmin(pair_overlaps(x)[0], axis=1)

        def pf(w, k=kfix):
            return _pair_con_full(R.x(w[:R.nz]), k)[0][pk] - w[-1]

        def pj(w, k=kfix):
            J = np.zeros((int(pk.sum()), R.nz + 1))
            J[:, :R.nz] = _pair_con_full(R.x(w[:R.nz]), k)[1][pk] @ R.M
            J[:, -1] = -1.0
            return J

        def cf(w):
            return _cont_con_full(R.x(w[:R.nz]))[0][ck] - w[-1]

        def cj(w):
            J = np.zeros((int(ck.sum()), R.nz + 1))
            J[:, :R.nz] = _cont_con_full(R.x(w[:R.nz]))[1][ck] @ R.M
            J[:, -1] = -1.0
            return J

        g = np.zeros(R.nz + 1); g[-1] = -1.0
        res = minimize(lambda w: -w[-1], best, jac=lambda w: g,
                       bounds=list(zip(lo, hi)),
                       constraints=[dict(type='ineq', fun=pf, jac=pj),
                                    dict(type='ineq', fun=cf, jac=cj)],
                       method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-14))
        w = res.x
        w[R.nz - 1] = s_fixed
        xw = R.x(w[:R.nz])
        m = min(float(-sat_min_overlap(xw)[pk].max()), float(-container_viol(xw)[ck].max()))
        if m > min(float(-sat_min_overlap(R.x(best[:R.nz]))[pk].max()),
                   float(-container_viol(R.x(best[:R.nz]))[ck].max())):
            best = w
        else:
            break
    xb = R.x(best[:R.nz])
    m = min(float(-sat_min_overlap(xb)[pk].max()), float(-container_viol(xb)[ck].max()))
    return best[:R.nz], m


# --------------------------------------------------------------- exact endpoint certificate
def certify_endpoint(R, z, eps_ladder=(1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4), den=10 ** 12,
                     prec=250, bounds=None):
    """Rigorous interval check that the landing is a real packing of the class at s* + eps.

    The configuration is rounded to rationals with denominator `den`; sin/cos are enclosed by
    mpmath's interval arithmetic at `prec` bits.  Returns (eps, report) for the smallest eps on
    the ladder at which EVERY kept pair is strictly separated on some axis and every free square
    is strictly inside [0, s*+eps]^2 (the pins ride the walls, so they are checked non-strictly
    at their exact slot values).  eps = None if the whole ladder fails.
    """
    from mpmath import iv, mp
    iv.prec = prec
    mp.prec = prec
    s_star = float(z[-1])

    def ivf(q):
        return iv.mpf(q.numerator) / iv.mpf(q.denominator)

    for eps in eps_ladder:
        zp, m = push_margin(R, z, s_star + eps, bounds=bounds)
        if m < 1e-10:
            continue
        x = R.x(zp)
        c, th, s = unpack(x)
        cq = [[Fr(round(v * den), den) for v in row] for row in c]
        tq = [Fr(round(v * den), den) for v in th]
        for p in range(R.k):
            tq[p] = Fr(0)
        sq = Fr(round((s_star + eps) * den), den)
        for p, ((ax, bx), (ay, by)) in enumerate(R.aff):
            slot_x = Fr(round(ax * 2), 2) + Fr(int(bx)) * sq
            slot_y = Fr(round(ay * 2), 2) + Fr(int(by)) * sq
            if R.pin_hw > 0:
                hw = Fr(round(R.pin_hw * den), den)
                ux = max(-hw, min(hw, cq[p][0] - slot_x))
                uy = max(-hw, min(hw, cq[p][1] - slot_y))
                cq[p][0] = slot_x + ux
                cq[p][1] = slot_y + uy
            else:
                cq[p][0] = slot_x
                cq[p][1] = slot_y
        S = ivf(sq)
        ct = [iv.cos(ivf(t)) for t in tq]
        st = [iv.sin(ivf(t)) for t in tq]
        C = [[ivf(cq[i][0]), ivf(cq[i][1])] for i in range(N)]
        ok = True
        # containment: exact-pin runs need only the free squares (the pins ride their slot
        # lines identically); delta-slack runs must check all eleven, and both check STRICTLY.
        for i in range(0 if R.pin_hw > 0 else R.k, N):
            e = (abs(ct[i]) + abs(st[i])) / 2
            for k in range(2):
                if not ((C[i][k] - e).a > 0 and (C[i][k] + e).b < S.a):
                    ok = False; break
            if not ok:
                break
        if not ok:
            continue
        # SAT separation on the kept pairs
        for p in range(NP_):
            if not R.pair_keep[p]:
                continue
            i, j = int(I_IDX[p]), int(J_IDX[p])
            d = [C[i][0] - C[j][0], C[i][1] - C[j][1]]
            sep = False
            for (owner, other) in ((i, j), (j, i)):
                for ax_ in range(2):
                    if ax_ == 0:
                        n = [ct[owner], st[owner]]
                    else:
                        n = [-st[owner], ct[owner]]
                    dn = d[0] * n[0] + d[1] * n[1]
                    r_other = (abs(ct[other] * n[0] + st[other] * n[1])
                               + abs(-st[other] * n[0] + ct[other] * n[1])) / 2
                    gap = abs(dn) - (iv.mpf('0.5') + r_other)
                    if gap.a > 0:
                        sep = True; break
                if sep:
                    break
            if not sep:
                ok = False
                break
        if ok:
            return eps, dict(den=den, prec=prec, margin=m, s_certified=float(sq),
                             s_certified_rat=f"{sq.numerator}/{sq.denominator}")
    return None, dict(den=den, prec=prec)
