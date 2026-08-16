"""
A04-upper-search: self-contained geometry + optimisation for packing N unit squares
(rotations allowed) into the smallest square [0,s]^2.

Variables: x = (cx_1, cy_1, ..., cx_N, cy_N, th_1..th_N, s)   (3N+1 numbers)

Overlap measure between two unit squares: separating-axis penetration depth
    depth(A,B) = max(0, min over the 4 edge normals n of  (rA(n)+rB(n) - |(a-b).n|))
where r(n) = half-width of the projection.  Penalty = depth^2.
Container penalty: squared violation of  e_i <= cx_i <= s-e_i  (e_i = (|cos|+|sin|)/2), same for y.

Pipeline for one start:  penalty continuation (L-BFGS-B, mu = 10 ... 1e6)  ->  SLSQP polish on the
active contact structure (fixed separating axis per pair)  ->  strict SAT feasibility check.
"""
import numpy as np
from scipy.optimize import minimize
import json, time, os, sys

N = 11
H = 0.5
I_IDX, J_IDX = np.triu_indices(N, 1)
NP = len(I_IDX)


def unpack(x):
    c = x[:2 * N].reshape(N, 2)
    th = x[2 * N:3 * N]
    s = x[3 * N]
    return c, th, s


def pack(c, th, s):
    return np.concatenate([c.ravel(), th, [s]])


def pair_overlaps(x):
    """Return ov (NP,4) overlap along each of the 4 axes, plus arrays needed for gradient."""
    c, th, s = unpack(x)
    a = c[I_IDX]; b = c[J_IDX]; d = a - b
    al = th[I_IDX]; be = th[J_IDX]
    ca, sa = np.cos(al), np.sin(al)
    cb, sb = np.cos(be), np.sin(be)
    phi = al - be
    cph, sph = np.cos(phi), np.sin(phi)
    r = H * (np.abs(cph) + np.abs(sph))              # same for all 4 axes
    rp = H * (-np.sign(cph) * sph + np.sign(sph) * cph)  # d r / d phi
    # axes: k=0: A's u1, k=1: A's u2, k=2: B's u1, k=3: B's u2
    n = np.empty((NP, 4, 2)); npr = np.empty((NP, 4, 2))
    n[:, 0, 0] = ca; n[:, 0, 1] = sa; npr[:, 0, 0] = -sa; npr[:, 0, 1] = ca
    n[:, 1, 0] = -sa; n[:, 1, 1] = ca; npr[:, 1, 0] = -ca; npr[:, 1, 1] = -sa
    n[:, 2, 0] = cb; n[:, 2, 1] = sb; npr[:, 2, 0] = -sb; npr[:, 2, 1] = cb
    n[:, 3, 0] = -sb; n[:, 3, 1] = cb; npr[:, 3, 0] = -cb; npr[:, 3, 1] = -sb
    dn = np.einsum('pj,pkj->pk', d, n)               # (NP,4)
    ov = H + r[:, None] - np.abs(dn)
    return ov, dict(d=d, n=n, npr=npr, dn=dn, rp=rp)


def sat_min_overlap(x):
    """min over axes overlap for each pair (<=0 means separated)."""
    ov, _ = pair_overlaps(x)
    return ov.min(axis=1)


def container_viol(x):
    c, th, s = unpack(x)
    e = H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    v = np.stack([e - c[:, 0], c[:, 0] + e - s, e - c[:, 1], c[:, 1] + e - s], axis=1)  # (N,4)
    return v


def obj_grad(x, mu):
    c, th, s = unpack(x)
    g = np.zeros_like(x)
    F = s
    g[3 * N] = 1.0
    # container
    cth, sth = np.cos(th), np.sin(th)
    e = H * (np.abs(cth) + np.abs(sth))
    de = H * (-np.sign(cth) * sth + np.sign(sth) * cth)
    v = np.stack([e - c[:, 0], c[:, 0] + e - s, e - c[:, 1], c[:, 1] + e - s], axis=1)
    vp = np.maximum(v, 0.0)
    F += mu * np.sum(vp ** 2)
    w = 2 * mu * vp  # (N,4)
    gc = np.zeros((N, 2))
    gc[:, 0] = -w[:, 0] + w[:, 1]
    gc[:, 1] = -w[:, 2] + w[:, 3]
    gth = de * (w[:, 0] + w[:, 1] + w[:, 2] + w[:, 3])
    gs = -np.sum(w[:, 1] + w[:, 3])
    # pairs
    ov, aux = pair_overlaps(x)
    k = np.argmin(ov, axis=1)
    ovm = ov[np.arange(NP), k]
    pos = ovm > 0
    F += mu * np.sum(np.maximum(ovm, 0) ** 2)
    if np.any(pos):
        idx = np.nonzero(pos)[0]
        kk = k[idx]
        wgt = 2 * mu * ovm[idx]
        nn = aux['n'][idx, kk]              # (m,2)
        nnp = aux['npr'][idx, kk]
        dn = aux['dn'][idx, kk]
        sg = np.sign(dn)
        d = aux['d'][idx]
        rp = aux['rp'][idx]
        ii = I_IDX[idx]; jj = J_IDX[idx]
        # d ov/ d a = -sg n ; d ov / d b = + sg n
        ga = -(sg * wgt)[:, None] * nn
        np.add.at(gc, ii, ga)
        np.add.at(gc, jj, -ga)
        # angles: owner of the axis: A if kk<2 else B
        ownerA = kk < 2
        dphi_dal = 1.0; dphi_dbe = -1.0
        # d ov/d al = rp*dphi_dal - [ownerA]*sg*(d.npr)
        # d ov/d be = rp*dphi_dbe - [ownerB]*sg*(d.npr)
        dnp = np.einsum('mj,mj->m', d, nnp)
        g_al = rp * dphi_dal - np.where(ownerA, sg * dnp, 0.0)
        g_be = rp * dphi_dbe - np.where(~ownerA, sg * dnp, 0.0)
        np.add.at(gth, ii, wgt * g_al)
        np.add.at(gth, jj, wgt * g_be)
    g[:2 * N] += gc.ravel()
    g[2 * N:3 * N] += gth
    g[3 * N] += gs
    return F, g


def penalty_solve(x0, mus=(10., 100., 1e3, 1e4, 1e5, 1e6), maxiter=400):
    x = x0.copy()
    for mu in mus:
        res = minimize(obj_grad, x, args=(mu,), jac=True, method='L-BFGS-B',
                       options=dict(maxiter=maxiter, maxcor=20, ftol=1e-15, gtol=1e-9))
        x = res.x
        # keep angles bounded
        x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], np.pi / 2)
    return x


# ---------------- SLSQP polish on active constraints (fixed axes) -----------------
def _pair_con_fixed(x, kfix):
    ov, aux = pair_overlaps(x)
    ar = np.arange(NP)
    val = -ov[ar, kfix]                      # >= 0 required
    # jacobian
    J = np.zeros((NP, 3 * N + 1))
    nn = aux['n'][ar, kfix]; nnp = aux['npr'][ar, kfix]; dn = aux['dn'][ar, kfix]
    sg = np.sign(dn); d = aux['d']; rp = aux['rp']
    ownerA = kfix < 2
    dnp = np.einsum('mj,mj->m', d, nnp)
    g_al = rp - np.where(ownerA, sg * dnp, 0.0)
    g_be = -rp - np.where(~ownerA, sg * dnp, 0.0)
    ga = -(sg)[:, None] * nn
    for p in range(NP):
        i, j = I_IDX[p], J_IDX[p]
        J[p, 2 * i:2 * i + 2] = -ga[p]
        J[p, 2 * j:2 * j + 2] = ga[p]
        J[p, 2 * N + i] = -g_al[p]
        J[p, 2 * N + j] = -g_be[p]
    return val, J


def _cont_con(x):
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


def polish(x0, rounds=3, maxiter=200):
    x = x0.copy()
    for r in range(rounds):
        ov, _ = pair_overlaps(x)
        kfix = np.argmin(ov, axis=1)
        cons = [dict(type='ineq', fun=lambda x, k=kfix: _pair_con_fixed(x, k)[0],
                     jac=lambda x, k=kfix: _pair_con_fixed(x, k)[1]),
                dict(type='ineq', fun=lambda x: _cont_con(x)[0], jac=lambda x: _cont_con(x)[1])]
        res = minimize(lambda x: x[3 * N], x, jac=lambda x: np.eye(3 * N + 1)[3 * N],
                       constraints=cons, method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-14))
        xn = res.x
        xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], np.pi / 2)
        ovn = sat_min_overlap(xn); cv = container_viol(xn)
        if ovn.max() < 1e-7 and cv.max() < 1e-7 and xn[3 * N] <= x[3 * N] + 1e-9:
            x = xn
        else:
            break
        if np.array_equal(np.argmin(pair_overlaps(x)[0], axis=1), kfix):
            break
    return x


def feasibility(x):
    """max overlap over pairs and max container violation (both should be <= 0)."""
    return float(sat_min_overlap(x).max()), float(container_viol(x).max())


def make_feasible_s(x):
    """Return the smallest s such that this configuration (centres/angles fixed, shifted so
    it fits) is strictly feasible; ignores overlaps (report separately)."""
    c, th, s = unpack(x)
    e = H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    lo = (c - e[:, None]).min(axis=0); hi = (c + e[:, None]).max(axis=0)
    return float(max(hi - lo)), lo


# ---------------- canonicalisation for the catalogue -----------------
def canonical(x):
    """Sort angles mod 90 deg; return signature (s, angle multiset)."""
    c, th, s = unpack(x)
    ang = np.mod(np.degrees(th), 90.0)
    ang = np.where(ang > 89.95, 0.0, ang)
    ang = np.where(ang < 0.05, 0.0, ang)
    return float(s), sorted(np.round(ang, 1).tolist())


# ---------------- random / structured starts -----------------
def start_random(rng, s0=None):
    if s0 is None:
        s0 = rng.uniform(3.9, 4.4)
    c = rng.uniform(0.6, s0 - 0.6, size=(N, 2))
    th = rng.uniform(0, np.pi / 2, size=N)
    return pack(c, th, s0)


def start_biased(rng, k=None, tilt=None, s0=None):
    """k upright + (N-k) tilted; tilt: centre of tilt distribution in degrees or None (uniform)."""
    if s0 is None:
        s0 = rng.uniform(3.9, 4.3)
    if k is None:
        k = int(rng.integers(3, 9))
    c = rng.uniform(0.6, s0 - 0.6, size=(N, 2))
    th = np.zeros(N)
    if tilt is None:
        th[k:] = rng.uniform(0.15, np.pi / 2 - 0.15, size=N - k)
    elif tilt == 'two':
        t1, t2 = rng.uniform(10, 80, size=2)
        m = (N - k) // 2
        th[k:k + m] = np.radians(t1) + rng.normal(0, 0.03, m)
        th[k + m:] = np.radians(t2) + rng.normal(0, 0.03, N - k - m)
    else:
        th[k:] = np.radians(tilt) + rng.normal(0, 0.06, size=N - k)
    # snap uprights to grid-ish positions near walls with some probability
    if rng.random() < 0.6:
        for i in range(k):
            gx = rng.integers(0, 4) + 0.5; gy = rng.integers(0, 4) + 0.5
            c[i] = [gx + rng.normal(0, 0.05), gy + rng.normal(0, 0.05)]
    rng.shuffle(c)  # positions random, but keep angle assignment
    return pack(c, th, s0)


def start_diagonal_band(rng):
    """Trump-like: two L-trominoes of uprights in opposite corners, 5 tilted squares in the diagonal band."""
    s0 = 3.95 + rng.uniform(0, 0.15)
    th0 = np.radians(rng.uniform(30, 50))
    c = np.zeros((N, 2)); th = np.zeros(N)
    # top-left L and bottom-right L
    c[0] = [0.5, s0 - 0.5]; c[1] = [1.5, s0 - 0.5]; c[2] = [0.5, s0 - 1.5]
    c[3] = [s0 - 0.5, 0.5]; c[4] = [s0 - 0.5, 1.5]; c[5] = [s0 - 1.5, 0.5]
    # band along the diagonal
    t = np.linspace(0.75, s0 - 0.75, 5)
    off = rng.uniform(-0.15, 0.15, size=5)
    for m in range(5):
        c[6 + m] = [t[m] + off[m] * (-1) ** m, t[m] - off[m] * (-1) ** m]
        th[6 + m] = th0 + rng.normal(0, 0.05)
    c += rng.normal(0, 0.08, size=c.shape)
    if rng.random() < 0.5:  # mirror
        c[:, 0] = s0 - c[:, 0]
        th = np.pi / 2 - th
    return pack(c, th, s0)


def run_one(x0, do_polish=True):
    x = penalty_solve(x0)
    if do_polish:
        x = polish(x)
    ovmax, cvmax = feasibility(x)
    return x, ovmax, cvmax


def result_record(x, ovmax, cvmax, method, extra=None):
    c, th, s = unpack(x)
    sc, angs = canonical(x)
    rec = dict(s=float(s), ovmax=ovmax, cvmax=cvmax, method=method,
               angles=angs, x=x.tolist(), t=time.time())
    if extra:
        rec.update(extra)
    return rec


if __name__ == '__main__':
    # quick self-test: gradient check
    rng = np.random.default_rng(0)
    x = start_random(rng)
    F, g = obj_grad(x, 100.)
    gn = np.zeros_like(x); h = 1e-6
    for i in range(len(x)):
        xp = x.copy(); xp[i] += h; xm = x.copy(); xm[i] -= h
        gn[i] = (obj_grad(xp, 100.)[0] - obj_grad(xm, 100.)[0]) / (2 * h)
    print('grad err', np.abs(g - gn).max(), np.abs(g).max())
    t0 = time.time()
    x1, ov, cv = run_one(x)
    print('one start: s=%.6f ov=%.2e cv=%.2e time=%.2fs' % (x1[3 * N], ov, cv, time.time() - t0))
    print(canonical(x1))
