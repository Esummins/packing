"""cp85.py -- A85 JOB 1: targeted k = 0 critical-point search.

Geometry + penalty/SLSQP local optimiser transcribed from
  attempts/A04-upper-search/pack11.py   (unpack/pack/pair_overlaps/obj_grad/penalty_solve/
                                         _pair_con_fixed/_cont_con/feasibility)
  attempts/A04-upper-search/driver.py   (local_opt, try_slsqp, perturb)
  attempts/A04-upper-search/fsbh.py     (kick)
with the A04 layout kept verbatim:  x = (cx_0, cy_0, ..., cx_10, cy_10, th_0..th_10, s), 34 floats.
Nothing under attempts/A04-* is imported or modified.

Added here: a k0 repulsion penalty (pushes squares off the four flush corner slots), the k0
operational test, contact-graph summary, Trump-image distance, and the driver.
"""
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atlas85 as A85
from atlas85 import S0, S_HAT, align_linf, load_atlas, in_atlas, trump_placements

N = 11
H = 0.5
I_IDX, J_IDX = np.triu_indices(N, 1)
NP = len(I_IDX)
HALFPI = np.pi / 2.0

REPO = A85.REPO
ATTEMPTS = A85.ATTEMPTS


# =========================================================== A04 pack11.py (verbatim transcription)
def unpack(x):
    return x[:2 * N].reshape(N, 2), x[2 * N:3 * N], x[3 * N]


def pack(c, th, s):
    return np.concatenate([c.ravel(), th, [s]])


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
    n = np.empty((NP, 4, 2)); npr = np.empty((NP, 4, 2))
    n[:, 0, 0] = ca; n[:, 0, 1] = sa; npr[:, 0, 0] = -sa; npr[:, 0, 1] = ca
    n[:, 1, 0] = -sa; n[:, 1, 1] = ca; npr[:, 1, 0] = -ca; npr[:, 1, 1] = -sa
    n[:, 2, 0] = cb; n[:, 2, 1] = sb; npr[:, 2, 0] = -sb; npr[:, 2, 1] = cb
    n[:, 3, 0] = -sb; n[:, 3, 1] = cb; npr[:, 3, 0] = -cb; npr[:, 3, 1] = -sb
    dn = np.einsum('pj,pkj->pk', d, n)
    ov = H + r[:, None] - np.abs(dn)
    return ov, dict(d=d, n=n, npr=npr, dn=dn, rp=rp)


def sat_min_overlap(x):
    return pair_overlaps(x)[0].min(axis=1)


def container_viol(x):
    c, th, s = unpack(x)
    e = H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    return np.stack([e - c[:, 0], c[:, 0] + e - s, e - c[:, 1], c[:, 1] + e - s], axis=1)


def obj_grad(x, mu):
    c, th, s = unpack(x)
    g = np.zeros_like(x)
    F = s
    g[3 * N] = 1.0
    cth, sth = np.cos(th), np.sin(th)
    e = H * (np.abs(cth) + np.abs(sth))
    de = H * (-np.sign(cth) * sth + np.sign(sth) * cth)
    v = np.stack([e - c[:, 0], c[:, 0] + e - s, e - c[:, 1], c[:, 1] + e - s], axis=1)
    vp = np.maximum(v, 0.0)
    F += mu * np.sum(vp ** 2)
    w = 2 * mu * vp
    gc = np.zeros((N, 2))
    gc[:, 0] = -w[:, 0] + w[:, 1]
    gc[:, 1] = -w[:, 2] + w[:, 3]
    gth = de * (w[:, 0] + w[:, 1] + w[:, 2] + w[:, 3])
    gs = -np.sum(w[:, 1] + w[:, 3])
    ov, aux = pair_overlaps(x)
    k = np.argmin(ov, axis=1)
    ovm = ov[np.arange(NP), k]
    pos = ovm > 0
    F += mu * np.sum(np.maximum(ovm, 0) ** 2)
    if np.any(pos):
        idx = np.nonzero(pos)[0]
        kk = k[idx]
        wgt = 2 * mu * ovm[idx]
        nn = aux['n'][idx, kk]
        nnp = aux['npr'][idx, kk]
        dn = aux['dn'][idx, kk]
        sg = np.sign(dn)
        d = aux['d'][idx]
        rp = aux['rp'][idx]
        ii = I_IDX[idx]; jj = J_IDX[idx]
        ga = -(sg * wgt)[:, None] * nn
        np.add.at(gc, ii, ga)
        np.add.at(gc, jj, -ga)
        ownerA = kk < 2
        dnp = np.einsum('mj,mj->m', d, nnp)
        g_al = rp - np.where(ownerA, sg * dnp, 0.0)
        g_be = -rp - np.where(~ownerA, sg * dnp, 0.0)
        np.add.at(gth, ii, wgt * g_al)
        np.add.at(gth, jj, wgt * g_be)
    g[:2 * N] += gc.ravel()
    g[2 * N:3 * N] += gth
    g[3 * N] += gs
    return F, g


# ------------------------------------------------------------------ k0 repulsion (NEW in A85)
# Smooth bump that is large exactly where a square is a "flush corner square":
#     B_ic = exp(-|c_i - p_c|^2 / (2 sc^2)) * exp(-sin(2 th_i)^2 / (2 sa^2))
# sin(2 th)^2 vanishes iff th is a multiple of pi/2, i.e. iff the square is axis aligned.
# p_c ranges over the four corner slots (1/2,1/2),(s-1/2,1/2),(1/2,s-1/2),(s-1/2,s-1/2);
# their s-dependence is differentiated too.
K0_SC = 0.30
K0_SA = 0.35


def k0_pen(x, lam):
    c, th, s = unpack(x)
    g = np.zeros_like(x)
    if lam == 0.0:
        return 0.0, g
    f = np.sin(2 * th) ** 2
    ang = np.exp(-f / (2 * K0_SA ** 2))
    dang = -(np.sin(4 * th) / K0_SA ** 2) * ang          # d/dth
    F = 0.0
    gc = np.zeros((N, 2)); gth = np.zeros(N); gs = 0.0
    for sx in (0, 1):
        for sy in (0, 1):
            px = 0.5 if sx == 0 else s - 0.5
            py = 0.5 if sy == 0 else s - 0.5
            dx = c[:, 0] - px
            dy = c[:, 1] - py
            u = dx * dx + dy * dy
            rad = np.exp(-u / (2 * K0_SC ** 2))
            B = rad * ang
            F += lam * np.sum(B)
            w = -lam * B / K0_SC ** 2
            gc[:, 0] += w * dx
            gc[:, 1] += w * dy
            gth += lam * rad * dang
            # d px/ds = sx, d py/ds = sy
            gs += -np.sum(w * (dx * sx + dy * sy))
    g[:2 * N] = gc.ravel()
    g[2 * N:3 * N] = gth
    g[3 * N] = gs
    return F, g


def obj_grad_k0(x, mu, lam):
    F, g = obj_grad(x, mu)
    Fp, gp = k0_pen(x, lam)
    return F + Fp, g + gp


def penalty_solve(x0, mus=(10., 100., 1e3, 1e4, 1e5, 1e6), maxiter=400, lam=0.0):
    x = x0.copy()
    for mu in mus:
        res = minimize(obj_grad_k0, x, args=(mu, lam), jac=True, method='L-BFGS-B',
                       options=dict(maxiter=maxiter, maxcor=20, ftol=1e-15, gtol=1e-9))
        x = res.x
        x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], HALFPI)
    return x


def _pair_con_fixed(x, kfix):
    ov, aux = pair_overlaps(x)
    ar = np.arange(NP)
    val = -ov[ar, kfix]
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


def feasibility(x):
    return float(sat_min_overlap(x).max()), float(container_viol(x).max())


# =========================================================== A04 driver.py (verbatim transcription)
def try_slsqp(x, thresh=2e-3, maxiter=300):
    ov, _ = pair_overlaps(x)
    kfix = np.argmin(ov, axis=1); ovm = ov.min(axis=1)
    act = np.nonzero(ovm > -thresh)[0]
    if len(act) == 0:
        return None
    fpair = lambda x, k=kfix, act=act: _pair_con_fixed(x, k)[0][act]
    jpair = lambda x, k=kfix, act=act: _pair_con_fixed(x, k)[1][act]
    cons = [dict(type='ineq', fun=fpair, jac=jpair),
            dict(type='ineq', fun=lambda x: _cont_con(x)[0], jac=lambda x: _cont_con(x)[1])]
    try:
        res = minimize(lambda x: x[3 * N], x, jac=lambda x: np.eye(3 * N + 1)[3 * N],
                       constraints=cons, method='SLSQP', options=dict(maxiter=maxiter, ftol=1e-15))
    except Exception:
        return None
    xn = res.x.copy()
    xn[2 * N:3 * N] = np.mod(xn[2 * N:3 * N], HALFPI)
    ovn, cvn = feasibility(xn)
    if ovn < 1e-8 and cvn < 1e-8 and xn[3 * N] <= x[3 * N] + 1e-10:
        return xn
    return None


def local_opt(x0, deep=True, lam=0.0):
    """Free-side local optimiser: minimise s subject to no overlap (A04 driver.local_opt).
    lam > 0 adds the k0 repulsion during the penalty phase only."""
    x = penalty_solve(x0, lam=lam)
    x = penalty_solve(x, mus=(1e7, 1e8), maxiter=1000, lam=lam)
    if deep and lam == 0.0:
        xs = try_slsqp(x)
        if xs is not None:
            x = xs
    ovmax, cvmax = feasibility(x)
    c, th, s = unpack(x)
    eps = max(ovmax, 0.0) * 1.05 + 1e-12
    cc = (c - s / 2) * (1 + eps) + s / 2
    e = H * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    lo = (cc - e[:, None]).min(axis=0); hi = (cc + e[:, None]).max(axis=0)
    cc = cc - lo
    s_strict = float(max(hi - lo)) + 1e-12
    xs = pack(cc, th, s_strict)
    ov2, cv2 = feasibility(xs)
    return xs, s_strict, float(s), ov2, cv2


def perturb(x, rng, scale=1.0):
    """A04 driver.perturb, structural moves only (scaled down for 'small' restarts)."""
    c, th, s = unpack(x)
    c = c.copy(); th = th.copy()
    r = rng.random()
    if r < 0.30:
        m = 1 if rng.random() < 0.6 else 2
        for i in rng.choice(N, m, replace=False):
            c[i] = rng.uniform(0.6, s - 0.6, size=2)
            th[i] = rng.uniform(0, HALFPI) if rng.random() < 0.7 else 0.0
    elif r < 0.50:
        i = rng.integers(N)
        th[i] = np.mod(th[i] + rng.normal(0, 0.5 * scale), HALFPI)
    elif r < 0.65:
        i, j = rng.choice(N, 2, replace=False)
        c[[i, j]] = c[[j, i]]
    elif r < 0.75:
        i = rng.integers(N)
        th[i] = np.mod(HALFPI - th[i], HALFPI)
    elif r < 0.85:
        tilted = (np.mod(np.degrees(th), 90) > 3) & (np.mod(np.degrees(th), 90) < 87)
        th[tilted] = np.mod(th[tilted] + rng.normal(0, 0.15 * scale), HALFPI)
    elif r < 0.93:
        c += rng.normal(0, 0.12 * scale, size=c.shape)
        th += rng.normal(0, 0.12 * scale, size=N)
    else:
        i = rng.integers(N)
        if np.mod(np.degrees(th[i]), 90) < 3 or np.mod(np.degrees(th[i]), 90) > 87:
            th[i] = np.radians(rng.uniform(15, 75))
        else:
            th[i] = 0.0
    return pack(c, th, s + 0.05)


def small_perturb(x, rng, sig_c=0.06, sig_t=0.06):
    """Small STRUCTURAL jiggle used for the per-seed restarts (keeps the basin's identity
    at risk but not its scale); mixes in one A04 structural move half the time."""
    c, th, s = unpack(x)
    c = c + rng.normal(0, sig_c, size=c.shape)
    th = th + rng.normal(0, sig_t, size=N)
    y = pack(c, th, s + 0.02)
    if rng.random() < 0.5:
        y = perturb(y, rng, scale=0.5)
    return y


# =========================================================== k0 test / diagnostics
def to_placements(x):
    c, th, s = unpack(x)
    return np.concatenate([c, np.mod(th, HALFPI)[:, None]], axis=1), float(s)


def axis_aligned_mask(th, tol=1e-6):
    """|theta - k*pi/2| <= tol (radians)."""
    d = np.abs(np.mod(th + np.pi / 4.0, HALFPI) - np.pi / 4.0)
    return d <= tol


def corner_slots(s):
    return np.array([[0.5, 0.5], [s - 0.5, 0.5], [0.5, s - 0.5], [s - 0.5, s - 0.5]])


def k_count(x, tol_th=1e-6, tol_c=1e-6):
    """Operational census: number of FLUSH CORNER squares (axis-aligned AND centre at a
    corner slot).  k = 0 iff this is 0.  Also returns the stricter count = number of
    axis-aligned squares at all."""
    c, th, s = unpack(x)
    aa = axis_aligned_mask(th, tol_th)
    slots = corner_slots(s)
    dmin = np.abs(c[:, None, :] - slots[None, :, :]).max(axis=2).min(axis=1)
    flush = aa & (dmin <= tol_c)
    return int(flush.sum()), int(aa.sum()), flush, aa, dmin


def contact_summary(x, tol=1e-6):
    ovm = sat_min_overlap(x)
    pairs = [[int(I_IDX[p]), int(J_IDX[p])] for p in range(NP) if ovm[p] > -tol]
    cv = container_viol(x)
    wl = ['x=0', 'x=s', 'y=0', 'y=s']
    walls = [[int(i), wl[j]] for i in range(N) for j in range(4) if cv[i, j] > -tol]
    return dict(n_pair_contacts=len(pairs), n_wall_contacts=len(walls),
                pairs=pairs, walls=walls)


_TRUMP = None


def trump_ref():
    global _TRUMP
    if _TRUMP is None:
        X, s = trump_placements()
        _TRUMP = (X[:, :2].copy(), X[:, 2].copy(), s)
    return _TRUMP


def dist_to_trump(x):
    P, T, s = trump_ref()
    pl, ss = to_placements(x)
    d_full, g, _ = align_linf(pl[:, :2], pl[:, 2], ss, P, T, s, include_s=True)
    d_nos, _, _ = align_linf(pl[:, :2], pl[:, 2], ss, P, T, s, include_s=False)
    return float(d_full), float(d_nos), A85.D4_NAMES[g] if g is not None else None


# =========================================================== seeds
def seed_vcrowder(theta_deg, same_sign, rng, jitter=0.0):
    """Two tilted squares tucked into each corner (both meeting the open corner box
    [0,1]^2 in the corner frame) + 3 squares in the middle.  D4-symmetric by construction:
    the corner-(0,0) pair is copied to the other three corners by the rotations of D4."""
    th = np.radians(theta_deg)
    e = H * (abs(np.cos(th)) + abs(np.sin(th)))
    s0 = 3.95
    # corner-(0,0) frame: square A flush in the corner, square B alongside it on the x wall
    thB = th if same_sign else -th
    eB = H * (abs(np.cos(thB)) + abs(np.sin(thB)))
    A = (e, e, th)
    B = (e + 0.90, eB - 0.02, thB)          # its inner corner still pokes into [0,1]^2
    base = [A, B]
    C = np.zeros((N, 2)); T = np.zeros(N)
    k = 0
    for rot in range(4):                     # rotate the corner pair by 90 deg four times
        for (px, py, pt) in base:
            for _ in range(1):
                q = np.array([px, py])
                a = rot * HALFPI
                ca, sa = np.cos(a), np.sin(a)
                # rotate the corner frame about the container centre
                v = q - np.array([s0 / 2, s0 / 2])
                v = np.array([ca * v[0] - sa * v[1], sa * v[0] + ca * v[1]])
                C[k] = v + s0 / 2
                T[k] = pt + a
                k += 1
    mid = np.array([[s0 / 2, s0 / 2 - 1.0], [s0 / 2, s0 / 2], [s0 / 2, s0 / 2 + 1.0]])
    for m in range(3):
        C[k] = mid[m]
        T[k] = np.radians(45.0) if m % 2 == 0 else -np.radians(45.0)
        k += 1
    assert k == N
    if jitter > 0:
        C = C + rng.normal(0, jitter, size=C.shape)
        T = T + rng.normal(0, jitter, size=N)
    return pack(C, np.mod(T, HALFPI), s0 + 0.15)


def seed_trump_rotated(alpha_deg):
    """Rigidly rotate Trump's packing about the container centre, refit the minimal
    axis-aligned enclosing square."""
    P, T, s = trump_ref()
    a = np.radians(alpha_deg)
    ca, sa = np.cos(a), np.sin(a)
    v = P - s / 2.0
    C = np.stack([ca * v[:, 0] - sa * v[:, 1], sa * v[:, 0] + ca * v[:, 1]], axis=1) + s / 2.0
    Th = T + a
    e = H * (np.abs(np.cos(Th)) + np.abs(np.sin(Th)))
    lo = (C - e[:, None]).min(axis=0); hi = (C + e[:, None]).max(axis=0)
    C = C - lo
    snew = float(max(hi - lo))
    return pack(C, np.mod(Th, HALFPI), snew)


def seed_from_pack11_x(bx):
    x = np.array(bx, dtype=float)
    x[2 * N:3 * N] = np.mod(x[2 * N:3 * N], HALFPI)
    return x


def seed_from_z34(z):
    """A22-order 34-vector (atlas z_center) -> pack11 layout."""
    z = np.asarray(z, dtype=float)
    C = np.array([[z[3 * i], z[3 * i + 1]] for i in range(N)])
    T = np.array([z[3 * i + 2] for i in range(N)])
    return pack(C, np.mod(T, HALFPI), float(z[33]))


def collect_seeds(rng):
    seeds = []
    # (a) V-crowder
    for td in (25.0, 30.0, 35.0, 40.0):
        for ss in (False, True):
            seeds.append(("vcrowder_%s_%02d" % ("same" if ss else "mixed", int(td)),
                          seed_vcrowder(td, ss, rng)))
            seeds.append(("vcrowderJ_%s_%02d" % ("same" if ss else "mixed", int(td)),
                          seed_vcrowder(td, ss, rng, jitter=0.05)))
    # (b) Trump rigidly rotated
    for a in (-10.0, -5.0, -2.0, 2.0, 5.0, 10.0):
        seeds.append(("trumprot_%+g" % a, seed_trump_rotated(a)))
    # (c) A04 catalogue families
    cat = json.load(open(os.path.join(ATTEMPTS, "A04-upper-search", "families_catalogue.json")))
    for i, f in enumerate(cat["families"]):
        seeds.append(("cat%03d" % i, seed_from_pack11_x(f["best_x"])))
    # (c') non-catalogue atlas attractors
    for e in load_atlas():
        if "NEW" in str(e.family_id):
            seeds.append(("atlas_%s" % e.family_id, seed_from_z34(e.z_center)))
    return seeds


# =========================================================== driver
def evaluate(x, atlas, tol_th=1e-6, tol_c=1e-6):
    nflush, naa, flush, aa, dmin = k_count(x, tol_th, tol_c)
    nflush4, naa4, _, _, _ = k_count(x, 1e-4, 1e-4)
    c, th, s = unpack(x)
    ov, cv = feasibility(x)
    pl, ss = to_placements(x)
    d_tr, d_tr_nos, d_tr_g = dist_to_trump(x)
    hits = in_atlas(pl, ss, atlas)
    pos = [h for h in hits if h["margin"] >= 0]
    return dict(
        s=float(s), ovmax=ov, cvmax=cv,
        k_flush_corner=nflush, n_axis_aligned=naa,
        k_flush_corner_tol1e4=nflush4, n_axis_aligned_tol1e4=naa4,
        tilts_deg=[round(float(v), 6) for v in np.degrees(np.mod(th, HALFPI))],
        centres=[[round(float(a), 9), round(float(b), 9)] for a, b in c],
        min_corner_slot_dist=[round(float(v), 9) for v in dmin],
        contacts=contact_summary(x),
        dist_to_trump_linf=d_tr, dist_to_trump_linf_no_s=d_tr_nos, dist_to_trump_d4=d_tr_g,
        atlas_hits=[dict(family_id=h["family_id"], margin=h["margin"],
                         dist_linf=h["dist_linf"], h=h["h"], cls=h["cls"]) for h in pos],
        atlas_nearest=dict(family_id=hits[0]["family_id"], margin=hits[0]["margin"],
                           dist_linf=hits[0]["dist_linf"], h=hits[0]["h"]),
        x=[float(v) for v in x],
    )


def d4_same(x, y, tol=1e-5):
    px, sx = to_placements(x)
    py, sy = to_placements(y)
    d, _, _ = align_linf(px[:, :2], px[:, 2], sx, py[:, :2], py[:, 2], sy)
    return d <= tol, d


def main():
    t0 = time.time()
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 2400.0
    rng = np.random.default_rng(85)
    atlas = load_atlas()
    seeds = collect_seeds(rng)
    print("seeds:", len(seeds), flush=True)

    raw = []          # every optimum with k = 0
    all_opt = []      # (name, s, k) for the census line
    n_runs = 0

    def run(x0, tag, lam=0.0):
        nonlocal n_runs
        try:
            xs, s_strict, s_raw, ov, cv = local_opt(x0, deep=True, lam=0.0)
        except Exception as exc:
            print("  fail", tag, exc, flush=True)
            return None
        n_runs += 1
        nf, na, _, _, _ = k_count(xs)
        all_opt.append((tag, float(s_strict), nf, na))
        if nf == 0 and ov < 1e-8 and cv < 1e-8:
            r = evaluate(xs, atlas)
            r["seed_tag"] = tag
            raw.append(r)
            return r
        return None

    for name, x0 in seeds:
        if time.time() - t0 > budget:
            print("BUDGET STOP (phase 1)", flush=True)
            break
        run(x0, name + "/base")
        x = x0
        for k in range(2):                       # small structural restarts
            run(small_perturb(x, rng), name + "/pert%d" % k)
        # k0-forced variant: relax WITH the repulsion, then re-relax WITHOUT it
        try:
            xf = penalty_solve(x0, lam=0.6)
            xf = penalty_solve(xf, mus=(1e5, 1e6), maxiter=600, lam=0.6)
            run(xf, name + "/k0forced")
        except Exception as exc:
            print("  k0forced fail", name, exc, flush=True)
    print("phase1 done: %d local_opt runs, %d k0 optima, %.1fs"
          % (n_runs, len(raw), time.time() - t0), flush=True)

    # dedupe: side at 1e-6 then D4 alignment
    raw.sort(key=lambda r: r["s"])
    uniq = []
    for r in raw:
        hit = None
        for u in uniq:
            if abs(u["s"] - r["s"]) < 1e-6:
                same, d = d4_same(np.array(u["x"]), np.array(r["x"]))
                if same:
                    hit = u
                    break
        if hit is None:
            r["n_hits"] = 1
            r["seed_tags"] = [r.pop("seed_tag")]
            uniq.append(r)
        else:
            hit["n_hits"] += 1
            if len(hit["seed_tags"]) < 12:
                hit["seed_tags"].append(r["seed_tag"])

    # headline classification
    ROT_TOL = 5e-3
    for u in uniq:
        is_rot = u["dist_to_trump_linf_no_s"] < 0.35 and u["s"] > S_HAT - 1e-9
        u["classification"] = (
            "trump_rotation" if (u["s"] > S_HAT + 1e-9 and u["dist_to_trump_linf_no_s"] < 0.35)
            else ("atlas_family" if u["atlas_hits"]
                  else ("NEW_below_3.9" if u["s"] < 3.9 else "unmatched_above_3.9")))

    non_rot = [u for u in uniq if u["classification"] != "trump_rotation"]
    head = dict(
        n_local_opt_runs=n_runs,
        n_k0_optima_raw=len(raw),
        n_k0_optima_distinct=len(uniq),
        best_k0_side=(uniq[0]["s"] if uniq else None),
        best_k0_classification=(uniq[0]["classification"] if uniq else None),
        best_k0_atlas_hits=([h["family_id"] for h in uniq[0]["atlas_hits"]] if uniq else None),
        best_k0_dist_to_trump=(uniq[0]["dist_to_trump_linf_no_s"] if uniq else None),
        best_non_trump_rotation_k0_side=(non_rot[0]["s"] if non_rot else None),
        best_non_trump_rotation_k0_classification=(non_rot[0]["classification"] if non_rot else None),
        best_non_trump_rotation_k0_atlas=([h["family_id"] for h in non_rot[0]["atlas_hits"]]
                                          if non_rot else None),
        any_k0_below_s_hat=bool(uniq and uniq[0]["s"] < S_HAT),
        any_k0_below_s0=bool(uniq and uniq[0]["s"] < S0),
        s_hat=S_HAT, s0=S0,
        wall_secs=time.time() - t0,
    )

    census = dict(
        n_optima_total=len(all_opt),
        n_optima_k0=sum(1 for a in all_opt if a[2] == 0),
        n_optima_no_axis_aligned_at_all=sum(1 for a in all_opt if a[3] == 0),
        min_side_over_all_optima=min(a[1] for a in all_opt) if all_opt else None,
        min_side_k0=min([a[1] for a in all_opt if a[2] == 0], default=None),
        min_side_zero_axis_aligned=min([a[1] for a in all_opt if a[3] == 0], default=None),
    )

    out = dict(
        attempt="A85-k0-route", job="JOB 1 targeted k0 critical-point search",
        constants=dict(s_hat=S_HAT, s0=S0, s0_rational="969271/250000"),
        k0_test=dict(rule="no square is BOTH axis-aligned (|theta - k*pi/2| <= 1e-6 rad) AND "
                          "centred within 1e-6 (L_inf) of a corner slot "
                          "(1/2,1/2),(s-1/2,1/2),(1/2,s-1/2),(s-1/2,s-1/2)",
                     stricter_count="n_axis_aligned = number of axis-aligned squares at all"),
        optimiser="A04 driver.local_opt (penalty continuation mu=10..1e8, SLSQP polish on the "
                  "active contact structure, inflate to strict feasibility) transcribed into "
                  "code/cp85.py; k0-forced variant adds a Gaussian corner-slot repulsion during "
                  "the penalty phase only, then re-relaxes with lam = 0",
        headline=head, census=census, optima=uniq)
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                        "cp85_k0_search.json")
    dest = os.path.abspath(dest)
    json.dump(out, open(dest, "w"), indent=1)
    print(json.dumps(head, indent=1))
    print(json.dumps(census, indent=1))
    print("written", dest)


if __name__ == "__main__":
    main()
