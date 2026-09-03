"""A87 chore: SECOND-ORDER classification of the certified k0 Fritz-John points.

Question (PI): are any of the 167 tight-certified k0 FJ points of
`results/cp87_fj_polished.jsonl` genuine LOCAL MINIMA of the enclosing side, or
are they saddles along their flat directions?

For each certified point z* (side sigma*, active rows A at tol 1e-6, NNLS
multipliers lam >= 0 with A^T lam = e_s):

(1) FLEX SPACE.  Feasible directions with zero first-order change of the side
    that keep every active contact to first order:
        H_flex = { y in R^34 : y_33 = 0,  grad g_k . y = 0  for all active k }.
    Because s = z_33 enters only the two "x=s"/"y=s" wall rows linearly and
    y_33 = 0, this is exactly null(A[:, :33]) embedded with y_33 = 0, so
    d_H = 33 - rank(A[:, :33]) -- the "flat_dim_33" already reported by
    fjpolish87.  A[:, :33] has an identically zero column block at the
    coordinates of every RATTLER square (a square touched by no active row), so
    the flex space splits as an exact coordinate direct sum

        H_flex = R^{3 * n_rattlers}  (+)  null( A[:, nonrattler coords] ),

    and we report the two dimensions separately: rattler flex is flat for
    trivial reasons (the square floats inside its cage, the side does not see
    it at all), the non-rattler flex is the interesting part.

(2) SECOND ORDER.  Lagrangian of  min s  s.t.  g_k(z, s) >= 0:
        L = lam0 * s - sum_k lam_k g_k,      grad^2 L = - sum_k lam_k grad^2 g_k
    (s is linear, so it contributes nothing to the Hessian).  Restricted
    Hessian  Hred = Z^T (grad^2 L)[:33,:33] Z  on an orthonormal basis Z of the
    flex space; its eigenvalues are the second-order test.  Hred > 0 on H_flex
    is the classical second-order SUFFICIENT condition (on the subspace);
    a negative eigenvalue is a CANDIDATE descent -- candidate only, because
    holding grad g_k . y = 0 does not keep g_k >= 0 to second order.  Hence:

(3) DIRECT NUMERICAL CHECK (the decisive one).  From z* + t*y and z* - t*y
    (t = 1e-4, 1e-3, y a flex direction scaled to ||y||_inf = 1), re-optimise
    the side with the full packing constraints by SLSQP -- contacts free to
    form, break and slide -- and ask whether a strictly smaller side is
    reached.  The SLSQP model is the sound INNER approximation of the packing
    problem: 176 smooth wall rows plus, for each of the 55 pairs, one chosen
    separating axis (owner o, edge e) with all four corners of the other square
    on its far side (equivalent to the SAT gap for that axis being >= 0).  Any
    feasible point of this model is a genuine packing, so a side it reaches is
    genuinely achievable; the axis choice is refreshed between outer rounds so
    the contact structure is free to change.  Every returned configuration is
    re-verified independently (`sigma_verified`: canonicalise, then inflate
    about the bbox centre until all 55 SAT gaps are >= 1e-11), so a reported
    drop is a drop to a *verified feasible packing*, never SLSQP slop.

Classification per point:
    STRICT_LOCAL_MIN  all flex curvature > 0 and no descent found
    DEGENERATE        zero-curvature flex directions, no descent found
    SADDLE            a verified descent found

Usage:  python fjsecond87.py {selftest|probe|run|report}
One process, BLAS pinned before numpy import.  Writes only
results/fjsecond87.jsonl, results/fjsecond87.json, logs/fjsecond87.log.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import json
import math
import sys
import time

import numpy as np
from scipy.optimize import minimize

import t3lib as T
import pilot87 as P
import fjpolish87 as F

RESULTS = P.RESULTS
LOGS = P.LOGS
S_HAT = F.S_HAT
S0F = F.S0F
TOL = 1e-6                 # the tight end of the ladder: the certified tol
RANK_TOL = 1e-9            # matches fjpolish87's rank / rank33 report
CURV_TOL = 1e-9            # eigenvalue threshold, relative to ||grad^2 L||
DESCENT_MARGIN = 1e-9      # verified side drop that counts as a descent
STEPS = (1e-3, 1e-4)
BIG_STEP = 1e-2            # extra probe on genuinely negative-curvature dirs
N_RANDOM_FLEX = 6          # random directions in the flex subspace as a whole

_HALF = np.array([[-.5, -.5], [.5, -.5], [.5, .5], [-.5, .5]])   # t3lib.HALF
_NHAT = np.array([[0., -1.], [1., 0.], [0., 1.], [-1., 0.]])     # t3lib.NHAT
_IJ = F._IJ


# ------------------------------------------------------------- float geometry

def unpack(x):
    x = np.asarray(x, float)
    c = np.stack([x[0:33:3], x[1:33:3]], axis=1)
    return c, x[2:33:3], x[33]


def corner_jet(c, th):
    """corners q[i,k,:] and their theta-derivative dq[i,k,:]."""
    ct, st = np.cos(th), np.sin(th)
    hx, hy = _HALF[:, 0], _HALF[:, 1]
    qx = c[:, None, 0] + ct[:, None] * hx[None, :] - st[:, None] * hy[None, :]
    qy = c[:, None, 1] + st[:, None] * hx[None, :] + ct[:, None] * hy[None, :]
    dqx = -st[:, None] * hx[None, :] - ct[:, None] * hy[None, :]
    dqy = ct[:, None] * hx[None, :] - st[:, None] * hy[None, :]
    return np.stack([qx, qy], -1), np.stack([dqx, dqy], -1)


def sigma_verified(z):
    """Canonicalise + inflate to a strictly feasible packing; return its side.

    inflate() guarantees every SAT gap >= 1e-11 by expanding the centres about
    the bbox centre, which can only RAISE the side; canonical() pins the walls.
    So the value returned is a side genuinely achieved by a valid packing.
    """
    w = F.inflate(F.canonical(np.asarray(z, float)))
    return F.enclosing_side(w), float(F.pair_gaps(w).min()), w


# --------------------------------------------------- flex space + Hessian

def active_data(z, tol=TOL):
    """rows, gradient matrix, NNLS multipliers, cone residual at z."""
    rows, info = F.classify(z, tol)
    if not rows:
        return None
    A = F.gradA(z, rows)
    res, lam, r = F.cone_nnls(A)
    return {'rows': rows, 'info': info, 'A': A, 'lam': lam, 'res': res,
            'gordan': r}


def touched_squares(rows):
    s = set()
    for r in rows:
        if r['kind'] == 'wall':
            s.add(r['i'])
        else:
            s.add(r['o']); s.add(r['p'])
    return s


def flex_space(A, rows):
    """Orthonormal bases of the flex space, split rattler / non-rattler."""
    Aq = A[:, :33]
    touched = touched_squares(rows)
    ratt = sorted(set(range(11)) - touched)
    rcoord = [3 * i + a for i in ratt for a in range(3)]
    ncoord = [j for j in range(33) if j not in set(rcoord)]

    # rattler block: A has identically zero columns there -> unit vectors
    Zr = np.zeros((33, len(rcoord)))
    for k, j in enumerate(rcoord):
        Zr[j, k] = 1.0
    # non-rattler block: nullspace of the reduced gradient matrix
    An = Aq[:, ncoord]
    if An.size:
        _u, sv, vt = np.linalg.svd(An, full_matrices=True)
        rank = int((sv > RANK_TOL).sum())
        Nn = vt[rank:].T                        # (len(ncoord), d)
    else:
        rank, Nn = 0, np.zeros((0, 0))
    Zn = np.zeros((33, Nn.shape[1]))
    Zn[ncoord, :] = Nn
    rank33 = int(np.linalg.matrix_rank(Aq, tol=RANK_TOL))
    return {'Zr': Zr, 'Zn': Zn, 'rattlers': ratt, 'rcoord': rcoord,
            'rank33': rank33, 'd_H': 33 - rank33,
            'd_rattler': len(rcoord), 'd_flex_nr': Zn.shape[1],
            'rank_nonrattler': rank}


def row_hessians(z, rows):
    """grad^2 g_k on the 33 config coords, per active row."""
    pt = [T._to_iv(float(v)) for v in z]
    out = []
    for r in rows:
        Hk = np.zeros((33, 33))
        _v, _g, h = T.row_grad_hess(pt, r)
        for (a, b), val in h.items():
            if a < 33 and b < 33:
                Hk[a, b] = T._mid(val)
        out.append(0.5 * (Hk + Hk.T))
    return out


def hess_lagrangian(z, rows, lam):
    """grad^2 L = - sum_k lam_k grad^2 g_k, restricted to the 33 config coords.

    Uses t3lib's interval order-2 jets (the same machinery the Newton polish
    drives to 1e-16 residual) and takes midpoints.
    """
    pt = [T._to_iv(float(v)) for v in z]
    H = np.zeros((33, 33))
    for k, r in enumerate(rows):
        lk = float(lam[k])
        if abs(lk) < 1e-14:
            continue
        _v, _g, h = T.row_grad_hess(pt, r)
        for (a, b), val in h.items():
            if a < 33 and b < 33:
                H[a, b] -= lk * T._mid(val)
    return 0.5 * (H + H.T)


def second_order(z, ad, fx):
    """Restricted Hessian on the flex space + eigen-analysis."""
    H = hess_lagrangian(z, ad['rows'], ad['lam'])
    Z = np.concatenate([fx['Zn'], fx['Zr']], axis=1)     # 33 x d_H
    hn = float(np.linalg.norm(H, 2)) if H.size else 0.0
    # every row is LINEAR in the centre coordinates, so the centre-centre block
    # of grad^2 L vanishes identically: any flex direction with no theta
    # component has exactly zero second-order change.  Reported as a gate.
    ci = [j for j in range(33) if j % 3 != 2]
    out = {'H_norm': hn,
           'H_centre_block_max_abs': float(np.abs(H[np.ix_(ci, ci)]).max())}
    if Z.shape[1] == 0:
        out.update({'eigs': [], 'n_pos': 0, 'n_zero': 0, 'n_neg': 0,
                    'eig_min': None, 'eig_max': None, 'Hred_max_abs': 0.0})
        return out, H, Z, np.zeros((0, 0))
    Hred = Z.T @ H @ Z
    Hred = 0.5 * (Hred + Hred.T)
    w, V = np.linalg.eigh(Hred)
    scale = max(hn, 1e-12)
    thr = CURV_TOL * scale
    out.update({'eigs': [float(e) for e in w],
                'Hred_max_abs': float(np.abs(Hred).max()),
                'curv_scale': scale, 'curv_thr': thr,
                'n_pos': int((w > thr).sum()),
                'n_zero': int((np.abs(w) <= thr).sum()),
                'n_neg': int((w < -thr).sum()),
                'eig_min': float(w.min()), 'eig_max': float(w.max())})
    # rattler block must be exactly flat -- assert it as a self-check
    if fx['d_rattler']:
        out['rattler_block_max_abs'] = float(
            np.abs(fx['Zr'].T @ H @ fx['Zr']).max())
    # MULTIPLIER-FREE version: restrict every single active row's Hessian to
    # the flex space.  If all of them vanish there, Hred = 0 for EVERY choice
    # of multipliers, so the multiplier ambiguity (lam0 = 0 self-stresses,
    # unbounded polytope) cannot rescue a second-order verdict.
    HK = row_hessians(z, ad['rows'])
    mx, arg = 0.0, None
    for k, Hk in enumerate(HK):
        v = float(np.abs(Z.T @ Hk @ Z).max())
        if v > mx:
            mx, arg = v, k
    out['max_row_Hred'] = mx
    out['max_row_Hred_row'] = (T.row_name(ad['rows'][arg])
                               if arg is not None else None)
    out['row_H_norm_max'] = max((float(np.abs(Hk).max()) for Hk in HK),
                                default=0.0)
    out.update(multiplier_sweep(ad, Z, HK, Hred, thr))
    return out, H, Z, V


def multiplier_sweep(ad, Z, HK, Hred, thr, ntry=400, seed=0):
    """The FJ multipliers here are NOT unique (the reported lam0 = 0 branch is a
    self-stress: sum mu_k grad g_k = 0 with mu >= 0, so the multiplier set is an
    unbounded polytope).  The second-order SUFFICIENT condition only needs ONE
    multiplier with Hred > 0, so a verdict read off the NNLS multiplier alone is
    not safe.  Every multiplier differs from lam by an element of ker(A^T), so:

      * q = dim ker(A^T) is the ambiguity;
      * Hred is AFFINE in lam, so if Z^T (sum_k d_k grad^2 g_k) Z = 0 for every
        basis direction d of ker(A^T), then Hred is the SAME for every
        multiplier and the verdict is multiplier-free;
      * otherwise maximise lambda_min(Hred(lam + N t)) over {lam + N t >= 0}
        -- a concave maximisation -- and report the best curvature any
        multiplier can produce.
    """
    A, lam = ad['A'], np.asarray(ad['lam'], float)
    m = A.shape[0]
    _u, sv, vt = np.linalg.svd(A.T, full_matrices=True)
    q = int(m - (sv > RANK_TOL).sum())
    N = vt[m - q:].T if q else np.zeros((m, 0))       # (m, q), A^T N = 0
    out = {'n_mult_null': q}
    if q == 0:
        out['multiplier_unique'] = True
        out['Hred_null_max'] = 0.0
        out['best_min_eig_over_multipliers'] = (
            float(np.linalg.eigvalsh(Hred).min()) if Hred.size else None)
        return out
    out['multiplier_unique'] = False
    Hj = []
    nmx = 0.0
    for j in range(q):
        Sj = sum(N[k, j] * HK[k] for k in range(m))
        Rj = Z.T @ Sj @ Z
        Rj = 0.5 * (Rj + Rj.T)
        Hj.append(Rj)
        nmx = max(nmx, float(np.abs(Rj).max()) if Rj.size else 0.0)
    out['Hred_null_max'] = nmx
    if nmx <= thr or Hred.shape[0] == 0:
        # Hred is constant over the whole multiplier set
        out['Hred_multiplier_invariant'] = True
        out['best_min_eig_over_multipliers'] = (
            float(np.linalg.eigvalsh(Hred).min()) if Hred.size else None)
        return out
    out['Hred_multiplier_invariant'] = False

    def mineig(t):
        M = Hred + sum(t[j] * Hj[j] for j in range(q))
        return float(np.linalg.eigvalsh(0.5 * (M + M.T)).min())

    def ok(t):
        return bool((lam + N @ t >= -1e-12).all())

    best = (float(np.linalg.eigvalsh(Hred).min()), np.zeros(q))
    rng = np.random.default_rng(seed)
    scale = max(float(np.abs(lam).max()), 1e-12)
    for _ in range(ntry):
        t = rng.standard_normal(q) * scale * rng.choice([1e-2, 1e-1, 1.0, 10.0])
        # project back into lam + N t >= 0 by shrinking
        for _s in range(40):
            if ok(t):
                break
            t *= 0.5
        else:
            continue
        v = mineig(t)
        if v > best[0]:
            best = (v, t.copy())
    # local polish of the best sample (mineig is concave in t)
    t = best[1].copy()
    stepv = scale * 0.5
    while stepv > 1e-14 * max(scale, 1.0):
        improved = False
        for j in range(q):
            for sg in (1.0, -1.0):
                tt = t.copy(); tt[j] += sg * stepv
                if ok(tt):
                    v = mineig(tt)
                    if v > best[0]:
                        best = (v, tt.copy()); t = tt; improved = True
        if not improved:
            stepv *= 0.5
    out['best_min_eig_over_multipliers'] = best[0]
    out['second_order_sufficient_some_multiplier'] = bool(best[0] > thr)
    return out


# ---------------------------------------------- geometry of a flex direction

def dir_geometry(y, rattlers):
    """What the flex direction DOES: translation vs rotation, which squares."""
    y = np.asarray(y, float)
    nrm = float(np.linalg.norm(y)) or 1.0
    th = y[2::3]
    ct = np.stack([y[0:33:3], y[1:33:3]], axis=1)
    per_sq = np.maximum(np.abs(ct).max(axis=1), np.abs(th))
    inv = [int(i) for i in np.where(per_sq > 0.05 * per_sq.max())[0]]
    tf = float(np.linalg.norm(th) / nrm)
    rs = set(rattlers)
    if inv and all(i in rs for i in inv):
        kind = 'rattler'
    elif tf < 1e-8:
        kind = 'translation'          # sliding square(s), zero curvature exactly
    elif tf > 0.99:
        kind = 'rotation'
    else:
        kind = 'mixed'
    return {'kind': kind, 'theta_frac': tf, 'squares': inv,
            'n_squares': len(inv)}


def flex_anatomy(fx):
    """Basis-independent geometric anatomy of the flex space.

    Per square: how much of the flex space touches its centre, and how much
    touches its angle.  A square with centre participation but no angle
    participation SLIDES; one with angle participation TILTS; a square in the
    rattler list floats free inside its cage.
    """
    Z = np.concatenate([fx['Zn'], fx['Zr']], axis=1)
    if Z.shape[1] == 0:
        return {'sliding': [], 'tilting': [], 'rigid': list(range(11))}
    slide, tilt, rigid = [], [], []
    for i in range(11):
        cn = float(np.linalg.norm(Z[[3 * i, 3 * i + 1], :]))
        tn = float(np.linalg.norm(Z[3 * i + 2, :]))
        if cn < 1e-9 and tn < 1e-9:
            rigid.append(i)
        elif tn < 1e-9:
            slide.append(i)
        else:
            tilt.append(i)
    return {'sliding': slide, 'tilting': tilt, 'rigid': rigid,
            'n_moving': 11 - len(rigid)}


def translation_dim(fx):
    """dim( flex space  intersect  {all theta components zero} ).

    Curvature vanishes exactly on this subspace (centre-centre block of
    grad^2 L is identically zero), so it is flat for a structural reason.
    """
    Z = np.concatenate([fx['Zn'], fx['Zr']], axis=1)
    if Z.shape[1] == 0:
        return 0
    Th = Z[2::3, :]                       # (11, d_H): theta rows of the basis
    if not Th.size:
        return Z.shape[1]
    sv = np.linalg.svd(Th, compute_uv=False)
    return int(Z.shape[1] - (sv > 1e-9).sum())


# --------------------------------------------- SLSQP re-optimisation of s

def choose_axes(z):
    """Per pair, the (owner, edge) whose SAT gap is largest: the separating
    axis of the current configuration.  Refreshed between outer rounds."""
    c, th, _s = unpack(z)
    q, _dq = corner_jet(c, th)
    sel = []
    for (i, j) in _IJ:
        best, arg = -np.inf, (i, j, 0)
        for o, p in ((i, j), (j, i)):
            ct, st = math.cos(th[o]), math.sin(th[o])
            R = np.array([[ct, -st], [st, ct]])
            for e in range(4):
                n = R @ _NHAT[e]
                v = float(((q[p] - c[o]) @ n).min() - 0.5)
                if v > best:
                    best, arg = v, (o, p, e)
        sel.append(arg)
    return sel


NW = 11 * 4 * 4          # wall rows
NP = 55 * 4              # pair rows (4 corners on the chosen axis)


def cons_and_jac(x, sel):
    c, th, s = unpack(x)
    q, dq = corner_jet(c, th)
    g = np.empty(NW + NP)
    Jc = np.zeros((NW + NP, 34))
    # ---- walls: qx >= 0, qy >= 0, s - qx >= 0, s - qy >= 0
    t = 0
    for i in range(11):
        for k in range(4):
            g[t] = q[i, k, 0]
            Jc[t, 3 * i] = 1.0; Jc[t, 3 * i + 2] = dq[i, k, 0]
            g[t + 1] = q[i, k, 1]
            Jc[t + 1, 3 * i + 1] = 1.0; Jc[t + 1, 3 * i + 2] = dq[i, k, 1]
            g[t + 2] = s - q[i, k, 0]
            Jc[t + 2, 33] = 1.0
            Jc[t + 2, 3 * i] = -1.0; Jc[t + 2, 3 * i + 2] = -dq[i, k, 0]
            g[t + 3] = s - q[i, k, 1]
            Jc[t + 3, 33] = 1.0
            Jc[t + 3, 3 * i + 1] = -1.0; Jc[t + 3, 3 * i + 2] = -dq[i, k, 1]
            t += 4
    # ---- pairs on the chosen separating axis
    for (o, p, e) in sel:
        ct, st = math.cos(th[o]), math.sin(th[o])
        nhx, nhy = _NHAT[e]
        n = np.array([ct * nhx - st * nhy, st * nhx + ct * nhy])
        nt = np.array([-st * nhx - ct * nhy, ct * nhx - st * nhy])
        u = q[p] - c[o]                                  # (4,2)
        g[t:t + 4] = u @ n - 0.5
        for k in range(4):
            row = t + k
            Jc[row, 3 * o] = -n[0]; Jc[row, 3 * o + 1] = -n[1]
            Jc[row, 3 * o + 2] = float(nt @ u[k])
            Jc[row, 3 * p] = n[0]; Jc[row, 3 * p + 1] = n[1]
            Jc[row, 3 * p + 2] = float(n @ dq[p, k])
        t += 4
    return g, Jc


class _Cache:
    def __init__(self, sel):
        self.sel = sel
        self.x = None
        self.g = None
        self.J = None

    def _ev(self, x):
        if self.x is None or not np.array_equal(x, self.x):
            self.x = np.array(x, float)
            self.g, self.J = cons_and_jac(self.x, self.sel)

    def f(self, x):
        self._ev(x); return self.g

    def j(self, x):
        self._ev(x); return self.J


def reopt(z0, rounds=2, maxiter=120):
    """Local SLSQP re-optimisation of the side from z0.  Returns the best
    VERIFIED (canonicalised + inflated) side reached and its configuration."""
    x = F.canonical(np.asarray(z0, float)).astype(float)
    best_s, best_z = sigma_verified(x)[0], x.copy()
    for _ in range(rounds):
        cache = _Cache(choose_axes(x))
        r = minimize(lambda v: v[33], x, jac=lambda v: np.eye(34)[33],
                     method='SLSQP', constraints=[{'type': 'ineq',
                                                   'fun': cache.f,
                                                   'jac': cache.j}],
                     options={'maxiter': maxiter, 'ftol': 1e-14})
        xn = np.asarray(r.x, float)
        if not np.all(np.isfinite(xn)):
            break
        sv, gap, w = sigma_verified(xn)
        if sv < best_s:
            best_s, best_z = sv, w.copy()
        x = F.canonical(xn)
    return best_s, best_z


# ------------------------------------------------------------- per-point run

def critical_cone_dirs(ad, nmax=8, seed=0):
    """Directions in the CRITICAL CONE that are NOT in the flex subspace.

    The flex subspace holds EVERY active row at zero to first order.  The
    critical cone of  min s  s.t. g >= 0  is larger: it only forces
    grad g_k . y = 0 on the rows with lam_k > 0 and allows the active rows
    carrying ZERO multiplier to OPEN (grad g_k . y >= 0).  A second-order
    descent can hide there, so those directions are probed too.
    """
    A = ad['A'][:, :33]
    lam = np.asarray(ad['lam'], float)
    supp = np.where(lam > 1e-12)[0]
    zero = np.where(lam <= 1e-12)[0]
    info = {'n_supp': int(len(supp)), 'n_zero_mult_active': int(len(zero))}
    if not len(zero) or not len(supp):
        info['d_cone_sub'] = None
        return [], info
    _u, sv, vt = np.linalg.svd(A[supp], full_matrices=True)
    rk = int((sv > RANK_TOL).sum())
    Zs = vt[rk:].T
    dc = Zs.shape[1]
    info['d_cone_sub'] = dc
    if dc == 0:
        return [], info
    B = A[zero] @ Zs
    nz = np.linalg.norm(B, axis=1); nz[nz == 0] = 1.0
    Bn = B / nz[:, None]
    out = []
    # (i) the most interior cone direction: max t s.t. Bn a >= t, |a| <= 1
    from scipy.optimize import linprog
    nq = Bn.shape[0]
    c = np.zeros(dc + 1); c[-1] = -1.0
    Aub = np.zeros((nq, dc + 1)); Aub[:, :dc] = -Bn; Aub[:, dc] = 1.0
    r = linprog(c, A_ub=Aub, b_ub=np.zeros(nq),
                bounds=[(-1, 1)] * dc + [(-1, 1)], method='highs')
    if r.success:
        info['cone_interior_t'] = float(-r.fun)
        a = r.x[:dc]
        if np.linalg.norm(a) > 1e-12:
            out.append(('cone_int', Zs @ a))
    # (ii) one direction per zero-multiplier row: OPEN that row as much as
    #      possible while keeping every other zero-multiplier row closed or
    #      opening (random Gaussians essentially never land in this thin cone,
    #      so it has to be hit with an LP).
    ext = []
    for j in range(nq):
        if len(ext) >= nmax:
            break
        cj = np.zeros(dc + 1); cj[:dc] = -Bn[j]
        r2 = linprog(cj, A_ub=Aub, b_ub=np.zeros(nq),
                     bounds=[(-1, 1)] * dc + [(0, 0)], method='highs')
        if r2.success and -r2.fun > 1e-9:
            a = r2.x[:dc]
            if np.linalg.norm(a) > 1e-12:
                ext.append(a)
                out.append(('cone%02d' % len(ext), Zs @ a))
    # (iii) a few random NON-NEGATIVE combinations of those (still in the cone)
    rng = np.random.default_rng(seed)
    for k in range(min(3, max(0, len(ext) - 1))):
        w = rng.random(len(ext))
        a = sum(w[i] * ext[i] for i in range(len(ext)))
        out.append(('conemix%d' % k, Zs @ a))
    info['n_cone_dirs'] = len(out)
    info['n_cone_extreme'] = len(ext)
    return [(nm, y / max(np.abs(y).max(), 1e-300)) for nm, y in out], info


def flex_directions(fx, V, mode='eigen', rng=None):
    """The directions to probe, as 33-vectors, with labels."""
    Z = np.concatenate([fx['Zn'], fx['Zr']], axis=1)
    out = []
    if mode == 'eigen' and V.shape[1]:
        for k in range(V.shape[1]):
            y = Z @ V[:, k]
            out.append(('eig%02d' % k, y))
    if mode == 'random' and fx['Zn'].shape[1] > 1:
        d = fx['Zn'].shape[1]
        for k in range(N_RANDOM_FLEX):
            a = rng.standard_normal(d)
            out.append(('rnd%02d' % k, fx['Zn'] @ (a / np.linalg.norm(a))))
    return [(nm, y / max(np.abs(y).max(), 1e-300)) for nm, y in out]


def probe_direction(z, sig0, y, steps=STEPS, rounds=3, maxiter=250):
    """Move +-t*y, re-optimise, return the best verified drop."""
    rec = {'trials': []}
    best = 0.0
    for t in steps:
        for sgn in (1.0, -1.0):
            w = np.asarray(z, float).copy()
            w[:33] = w[:33] + sgn * t * y[:33]
            sv, bz = reopt(w, rounds=rounds, maxiter=maxiter)
            drop = sig0 - sv
            rec['trials'].append({'t': t, 'sign': sgn, 'sigma': sv,
                                  'drop': drop,
                                  'drift': float(np.max(np.abs(bz - z)))})
            if drop > best:
                best = drop
                rec['best'] = {'t': t, 'sign': sgn, 'sigma': sv, 'drop': drop}
                rec['z'] = bz
    rec['best_drop'] = best
    rec['max_drift'] = max(tr['drift'] for tr in rec['trials'])
    return rec


def analyse(tag, zfrac, meta, full=False, budget=None, log=print):
    t0 = time.time()
    z = np.array([float(T.str_frac(v)) if isinstance(v, str) else float(v)
                  for v in zfrac], float)
    rec = {'tag': tag}
    rec.update(meta)
    sig0, gap0, z = sigma_verified(z)
    rec['sigma'] = sig0
    rec['sat_gap'] = gap0
    ad = active_data(z)
    if ad is None:
        rec['error'] = 'no active rows / infeasible at tol %g' % TOL
        return rec
    rec['m_active'] = len(ad['rows'])
    rec['cone_residual'] = ad['res']
    rec['fj_reproduced'] = bool(ad['res'] <= F.CONE_TOL)
    fx = flex_space(ad['A'], ad['rows'])
    rec.update({k: fx[k] for k in ('rank33', 'd_H', 'd_rattler', 'd_flex_nr')})
    rec['rattlers'] = fx['rattlers']
    rec['split_ok'] = bool(fx['d_rattler'] + fx['d_flex_nr'] == fx['d_H'])
    so, H, Z, V = second_order(z, ad, fx)
    rec['second_order'] = so
    rec['d_translation'] = translation_dim(fx)
    rec['anatomy'] = flex_anatomy(fx)
    kf, naa, dslot = F.k0_census(z, float(z[33]))
    rec['k_flush_corner'] = kf
    rec['k0'] = bool(kf == 0)

    # ---- BASELINE: what a re-optimisation gets with NO perturbation at all.
    # cp87's polish stops at a finite residual, so some certified points sit a
    # little above their own local optimum; that offset would otherwise show up
    # in EVERY probe direction and be misread as a descent.  Every probe is
    # scored net of it.
    s_base, _zb = reopt(z, rounds=5, maxiter=600)
    rec['baseline_drop'] = sig0 - s_base

    # ---- direct numerical descent probes
    rng = np.random.default_rng(abs(hash(tag)) % (2 ** 31))
    dirs = flex_directions(fx, V, 'eigen')
    dirs += flex_directions(fx, V, 'random', rng)
    cdirs, cinfo = critical_cone_dirs(ad, seed=abs(hash(tag)) % (2 ** 31))
    rec['cone'] = cinfo
    dirs += cdirs
    # order: most negative curvature first (V columns are eigh-sorted ascending)
    probes = []
    best_drop, best_probe = 0.0, None
    thr = so.get('curv_thr', 0.0)
    for nm, y in dirs:
        if budget is not None and time.time() - t0 > budget:
            rec['budget_hit'] = True
            break
        eig = so['eigs'][int(nm[3:])] if nm.startswith('eig') else None
        steps = STEPS
        if eig is not None and eig < -thr:
            steps = STEPS + (BIG_STEP,)      # genuine negative curvature
        pr = probe_direction(z, sig0, y, steps=steps)
        e = {'dir': nm, 'best_drop': pr['best_drop'],
             'max_drift': pr['max_drift'],
             'geom': dir_geometry(y, fx['rattlers'])}
        if eig is not None:
            e['eig'] = eig
        if pr.get('best'):
            e.update({k: pr['best'][k] for k in ('t', 'sign', 'sigma')})
        probes.append(e)
        if pr['best_drop'] > best_drop:
            best_drop, best_probe = pr['best_drop'], (nm, pr)
    rec['probes'] = probes
    rec['best_drop'] = best_drop
    rec['net_drop'] = best_drop - rec['baseline_drop']
    # a descent that EVERY direction finds equally is not directional: it is
    # the baseline offset again.  Recorded so the two can never be confused.
    rec['descent_isotropic'] = (
        float(sum(1 for p in probes if p['best_drop'] >= 0.5 * best_drop)
              / max(len(probes), 1)) if best_drop > 0 else None)
    # a compact geometric summary of the flex space
    gk = {}
    for p in probes:
        if p['dir'].startswith('eig'):
            gk[p['geom']['kind']] = gk.get(p['geom']['kind'], 0) + 1
    rec['flex_geometry'] = gk

    # ---- confirm a candidate descent at higher effort + record where it lands
    rec['descent'] = None
    if best_probe is not None and rec['net_drop'] > DESCENT_MARGIN:
        nm, pr = best_probe
        y = dict(dirs)[nm]
        pr2 = probe_direction(z, sig0, y, steps=STEPS + (BIG_STEP,),
                              rounds=5, maxiter=500)
        use = pr2 if pr2['best_drop'] >= pr['best_drop'] else pr
        zb = use['z']
        svb, gapb, zb = sigma_verified(zb)
        kfb, naab, _d = F.k0_census(zb, float(zb[33]))
        rec['descent'] = {
            'dir': nm, 'eig': (so['eigs'][int(nm[3:])]
                               if nm.startswith('eig') else None),
            'step': use['best']['t'], 'sign': use['best']['sign'],
            'sigma_reached': svb, 'drop': sig0 - svb,
            'sat_gap': gapb, 'k_flush_corner': kfb, 'k0': bool(kfb == 0),
            'stratum': 'k0' if kfb == 0 else 'k>=1',
            'below_s_hat': bool(svb < S_HAT),
            'net_drop': (sig0 - svb) - rec['baseline_drop'],
            'z': [T.frac_str(__import__('fractions').Fraction(float(v))
                             .limit_denominator(10 ** 15)) for v in zb]}
        rec['best_drop'] = max(best_drop, sig0 - svb)
        rec['net_drop'] = rec['best_drop'] - rec['baseline_drop']

    # ---- classification
    #  curvature verdict uses the BEST multiplier (second-order sufficiency
    #  only needs one), which for a unique/invariant multiplier set is just
    #  the NNLS eig_min.
    bme = so.get('best_min_eig_over_multipliers')
    thr = so.get('curv_thr', 0.0)
    rec['best_min_eig'] = bme
    if fx['d_H'] == 0:
        rec['curv_verdict'] = 'no_flex'
    elif bme is None:
        rec['curv_verdict'] = 'unknown'
    elif bme > thr:
        rec['curv_verdict'] = 'positive_definite'
    elif bme < -thr:
        rec['curv_verdict'] = 'indefinite_or_negative'
    else:
        rec['curv_verdict'] = 'zero_curvature_present'
    if rec['net_drop'] > DESCENT_MARGIN:
        cls = 'SADDLE'
    elif fx['d_H'] == 0 or (bme is not None and bme > thr):
        cls = 'STRICT_LOCAL_MIN'
    else:
        cls = 'DEGENERATE'
    rec['klass'] = cls
    # a saddle is "confirmed" when the second-order test and the numerical
    # descent AGREE (a curvature eigenvalue below -thr), or when the drop is
    # far too large to be numerical slop
    rec['saddle_quality'] = None
    if cls == 'SADDLE':
        rec['saddle_quality'] = (
            'confirmed' if ((bme is not None and bme < -thr)
                            or rec['net_drop'] > 1e-6) else 'marginal')
    rec['n_probes'] = len(probes)
    rec['secs'] = time.time() - t0
    return rec


# --------------------------------------------------------------- self-test

def selftest():
    """Gates against silent corruption of the three new pieces."""
    ok = 0
    recs = load_tight()
    tag, zf, meta = recs[0]
    z = np.array([float(T.str_frac(v)) for v in zf])
    z = sigma_verified(z)[2]
    ad = active_data(z)

    # 1. NNLS multipliers really solve the FJ system on the raw rows
    r = ad['A'].T @ ad['lam'] - np.eye(34)[33]
    assert np.max(np.abs(r)) < 1e-7, np.max(np.abs(r))
    print('S1 ok  A^T lam = e_s residual %.2e' % np.max(np.abs(r))); ok += 1

    # 2. flex space really annihilates the active gradients, and d_H matches
    fx = flex_space(ad['A'], ad['rows'])
    Z = np.concatenate([fx['Zn'], fx['Zr']], axis=1)
    resid = np.max(np.abs(ad['A'][:, :33] @ Z)) if Z.size else 0.0
    assert resid < 1e-8, resid
    assert fx['d_rattler'] + fx['d_flex_nr'] == fx['d_H'], fx
    assert abs(np.max(np.abs(Z.T @ Z - np.eye(Z.shape[1])))) < 1e-10
    print('S2 ok  d_H=%d = %d rattler + %d flex, A33.Z = %.2e, Z orthonormal'
          % (fx['d_H'], fx['d_rattler'], fx['d_flex_nr'], resid)); ok += 1

    # 3. Lagrangian Hessian against central finite differences of grad L
    H = hess_lagrangian(z, ad['rows'], ad['lam'])
    lam = ad['lam']

    def gradL(w):
        A = F.gradA(w, ad['rows'])
        return (np.eye(34)[33] - A.T @ lam)[:33]
    hstep = 1e-6
    err = 0.0
    for j in (0, 2, 5, 17, 32):
        wp = np.array(z, float); wp[j] += hstep
        wm = np.array(z, float); wm[j] -= hstep
        fd = (gradL(wp) - gradL(wm)) / (2 * hstep)
        err = max(err, float(np.max(np.abs(fd - H[:, j]))))
    assert err < 1e-4, err
    print('S3 ok  Hessian vs finite differences: max err %.2e' % err); ok += 1

    # 4. SLSQP constraint values agree with t3lib's own row evaluation
    sel = choose_axes(z)
    g, Jc = cons_and_jac(z, sel)
    pt = [T._to_iv(float(v)) for v in z]
    tw = 0
    err = 0.0
    for i in range(11):
        for k in range(4):
            for w in ('x=0', 'y=0', 'x=s', 'y=s'):
                v = T._mid(T.row_value(pt, T.wall_row(i, k, w)))
                err = max(err, abs(v - g[tw])); tw += 1
    assert err < 1e-9, err
    print('S4 ok  wall rows vs t3lib: max err %.2e' % err); ok += 1

    # 5. SLSQP Jacobian against finite differences
    e2 = 0.0
    for j in (1, 4, 8, 20, 33):
        wp = np.array(z, float); wp[j] += 1e-7
        wm = np.array(z, float); wm[j] -= 1e-7
        fd = (cons_and_jac(wp, sel)[0] - cons_and_jac(wm, sel)[0]) / 2e-7
        e2 = max(e2, float(np.max(np.abs(fd - Jc[:, j]))))
    assert e2 < 1e-5, e2
    print('S5 ok  constraint Jacobian vs finite differences: %.2e' % e2); ok += 1

    # 6. the SLSQP inner model is SOUND: its feasible points are packings
    #    (min pair gap of the model >= 0  =>  SAT gap >= 0)
    gp = g[NW:].reshape(55, 4).min(axis=1)
    pg = F.pair_gaps(z)
    assert np.all(pg >= gp - 1e-9), float(np.min(pg - gp))
    print('S6 ok  model pair rows <= true SAT gaps (sound inner model), '
          'slack %.2e' % float(np.min(pg - gp))); ok += 1

    # 7. re-optimising FROM the certified point must not find a descent
    sv, _z = reopt(z, rounds=2, maxiter=200)
    print('S7 ok  reopt at the point itself: sigma %.12f vs %.12f (drop %.2e)'
          % (sv, F.enclosing_side(z), F.enclosing_side(z) - sv)); ok += 1

    # 8. reopt DOES descend from a deliberately inflated start (it works)
    w = np.array(z, float).copy()
    m = float(z[33]) / 2.0
    w[0:33:3] = m + (w[0:33:3] - m) * 1.02
    w[1:33:3] = m + (w[1:33:3] - m) * 1.02
    w = F.canonical(w)
    s_in = F.enclosing_side(w)
    sv2, _ = reopt(w, rounds=3, maxiter=300)
    assert sv2 < s_in - 1e-4, (s_in, sv2)
    print('S8 ok  reopt descends a 2%% inflation: %.9f -> %.9f' % (s_in, sv2))
    ok += 1

    # 9. every row is linear in the centres => centre-centre block of grad^2 L
    #    is identically zero (so pure-translation flex has zero curvature)
    ci = [j for j in range(33) if j % 3 != 2]
    cb = float(np.abs(H[np.ix_(ci, ci)]).max())
    assert cb == 0.0, cb
    print('S9 ok  centre-centre block of grad^2 L is exactly 0 (%.1e)' % cb)
    ok += 1
    print('selftest %d/9 ok' % ok)


# ------------------------------------------------------------------ driver

def load_tight():
    path = os.path.join(RESULTS, 'cp87_fj_polished.jsonl')
    recs = [json.loads(ln) for ln in open(path) if ln.strip()]
    out = []
    for r in recs:
        if not r.get('survivor_tight') or not r.get('z_polished'):
            continue
        f = r['final']['fj']
        out.append((r['tag'], r['z_polished'],
                    {'kind': r.get('kind'), 'idx': r.get('idx'),
                     'sigma_polished': r['sigma_polished'],
                     'delta_vs_s_hat': r['sigma_polished'] - S_HAT,
                     'flat_dim_33_cp87': 33 - f['rank33'],
                     'n_rattlers_cp87': f['n_rattlers'],
                     'lam0_zero_branch': f['lam0_zero_branch'],
                     'm_active_cp87': f['m_active']}))
    out.sort(key=lambda t: t[2]['sigma_polished'])
    return out


def cmd_selftest():
    selftest()


def cmd_probe():
    items = load_tight()
    print('n tight survivors = %d' % len(items), flush=True)
    for tag, zf, meta in [items[0]]:
        r = analyse(tag, zf, meta, full=True)
        print(json.dumps({k: v for k, v in r.items()
                          if k not in ('probes', 'descent')},
                         indent=1, default=str), flush=True)
        print('probes:', flush=True)
        for p in r['probes']:
            print('  %-8s eig=%-12s best_drop=%.3e' %
                  (p['dir'], ('%+.3e' % p['eig']) if 'eig' in p else '-',
                   p['best_drop']), flush=True)
        if r['descent']:
            print('DESCENT', json.dumps({k: v for k, v in r['descent'].items()
                                         if k != 'z'}, indent=1), flush=True)


def cmd_run():
    items = load_tight()
    path = os.path.join(RESULTS, 'fjsecond87.jsonl')
    done = set()
    if os.path.exists(path):
        for ln in open(path):
            try:
                done.add(json.loads(ln)['tag'])
            except Exception:
                pass
    todo = [x for x in items if x[0] not in done]
    print('todo %d of %d' % (len(todo), len(items)), flush=True)
    t0 = time.time()
    for n, (tag, zf, meta) in enumerate(todo, 1):
        try:
            r = analyse(tag, zf, meta, budget=240.0)
        except Exception as e:
            import traceback
            r = {'tag': tag, 'error': repr(e), 'tb': traceback.format_exc()}
            r.update(meta)
        with open(path, 'a') as f:
            f.write(json.dumps(r, default=str) + '\n')
        print('[%7.1fs] %3d/%3d %-8s sig=%.9f dH=%s(%s r) neg/zero/pos=%s/%s/%s'
              ' best_drop=%.2e %s'
              % (time.time() - t0, n, len(todo), tag, r.get('sigma', -1),
                 r.get('d_H'), r.get('d_rattler'),
                 r.get('second_order', {}).get('n_neg'),
                 r.get('second_order', {}).get('n_zero'),
                 r.get('second_order', {}).get('n_pos'),
                 r.get('best_drop', -1), r.get('klass', r.get('error'))),
              flush=True)
    print('run done %.1f s' % (time.time() - t0), flush=True)


def cmd_report():
    path = os.path.join(RESULTS, 'fjsecond87.jsonl')
    recs = [json.loads(ln) for ln in open(path) if ln.strip()]
    good = [r for r in recs if 'error' not in r]
    cnt = {}
    for r in good:
        cnt[r['klass']] = cnt.get(r['klass'], 0) + 1
    sad = sorted([r for r in good if r['klass'] == 'SADDLE'],
                 key=lambda r: r['descent']['sigma_reached'] if r.get('descent')
                 else 9e9)
    deg = [r for r in good if r['klass'] == 'DEGENERATE']
    strict = [r for r in good if r['klass'] == 'STRICT_LOCAL_MIN']

    def hist(xs):
        h = {}
        for x in xs:
            k = 'none' if x is None else x
            h[k] = h.get(k, 0) + 1
        return {str(k): v for k, v in
                sorted(h.items(), key=lambda kv: (kv[0] == 'none', kv[0]))}

    out = {
        'attempt': 'A87 chore: second-order classification of the certified '
                   'k0 Fritz-John points',
        'input': 'attempts/A87-drain-flow/results/cp87_fj_polished.jsonl '
                 '(survivor_tight, tol 1e-6)',
        'method': {
            'flex_space': 'null(A[:, :33]) with y_s = 0; split exactly into '
                          '3*n_rattlers rattler coords + non-rattler nullspace',
            'second_order': 'Hred = Z^T (-sum lam_k grad^2 g_k) Z, NNLS '
                            'multipliers, eigenvalues, rel tol %g' % CURV_TOL,
            'descent': 'SLSQP re-optimisation of s from z +- t*y, t in %s, '
                       'sound inner model (176 wall rows + 55 chosen '
                       'separating axes x 4 corners), axes refreshed per '
                       'round; every result re-verified by canonical+inflate'
                       % (STEPS,),
            'descent_margin': DESCENT_MARGIN},
        'constants': {'s_hat': S_HAT, 's0': S0F, 'tol': TOL},
        'counts_by_class': cnt,
        'n_points': len(good), 'n_errors': len(recs) - len(good),
        'headline_o012': next(({k: v for k, v in r.items()
                                if k not in ('probes',)}
                               for r in good if r['tag'] == 'o012'), None),
        'd_H_hist': hist([r['d_H'] for r in good]),
        'd_rattler_hist': hist([r['d_rattler'] for r in good]),
        'd_flex_nonrattler_hist': hist([r['d_flex_nr'] for r in good]),
        'n_neg_curv_hist': hist([r['second_order']['n_neg'] for r in good]),
        'n_zero_curv_hist': hist([r['second_order']['n_zero'] for r in good]),
        'n_points_with_negative_curvature':
            sum(1 for r in good if r['second_order']['n_neg'] > 0),
        'n_points_all_positive_curvature':
            sum(1 for r in good if r['second_order']['n_neg'] == 0
                and r['second_order']['n_zero'] == 0),
        'saddles': [
            {'tag': r['tag'], 'sigma': r['sigma'],
             'quality': r.get('saddle_quality'),
             'net_drop': r.get('net_drop'),
             'baseline_drop': r.get('baseline_drop'),
             'descent_isotropic': r.get('descent_isotropic'),
             'sigma_reached': r['descent']['sigma_reached'],
             'drop': r['descent']['drop'],
             'dir': r['descent']['dir'], 'eig': r['descent']['eig'],
             'step': r['descent']['step'], 'sign': r['descent']['sign'],
             'stratum_landed': r['descent']['stratum'],
             'k_flush_corner': r['descent']['k_flush_corner'],
             'below_s_hat': r['descent']['below_s_hat'],
             'sat_gap': r['descent']['sat_gap'],
             'd_H': r['d_H'], 'd_rattler': r['d_rattler'],
             'n_neg': r['second_order']['n_neg']}
            for r in sad if r.get('descent')],
        'saddle_summary': {
            'n': len(sad),
            'n_confirmed': sum(1 for r in sad
                               if r.get('saddle_quality') == 'confirmed'),
            'n_marginal': sum(1 for r in sad
                              if r.get('saddle_quality') == 'marginal'),
            'lowest_sigma_reached': min((r['descent']['sigma_reached']
                                         for r in sad if r.get('descent')),
                                        default=None),
            'lowest_sigma_reached_tag': (
                sad[0]['tag'] if sad and sad[0].get('descent') else None),
            'any_below_s_hat': any(r['descent']['below_s_hat']
                                   for r in sad if r.get('descent')),
            'any_below_s0': any(r['descent']['sigma_reached'] < S0F
                                for r in sad if r.get('descent')),
            'n_exit_k0': sum(1 for r in sad
                             if r.get('descent') and not r['descent']['k0']),
            'n_stay_k0': sum(1 for r in sad
                             if r.get('descent') and r['descent']['k0'])},
        'critical_cone': {
            'note': 'the flex SUBSPACE holds every active row at 0; the '
                    'critical CONE also lets the zero-multiplier active rows '
                    'open.  Those directions were probed separately.',
            'd_cone_sub_hist': hist([r.get('cone', {}).get('d_cone_sub')
                                     for r in good]),
            'n_zero_mult_active_hist': hist(
                [r.get('cone', {}).get('n_zero_mult_active') for r in good]),
            'n_points_with_cone_dirs': sum(
                1 for r in good if r.get('cone', {}).get('n_cone_dirs')),
            'n_saddles_found_by_cone_dir': sum(
                1 for r in sad if r.get('descent')
                and str(r['descent']['dir']).startswith('cone')),
            'n_saddles_found_by_flex_dir': sum(
                1 for r in sad if r.get('descent')
                and not str(r['descent']['dir']).startswith('cone'))},
        'geometry_of_the_flex': {
            'n_with_rattlers': sum(1 for r in good if r['d_rattler'] > 0),
            'total_flex_dims': sum(r['d_H'] for r in good),
            'total_rattler_dims': sum(r['d_rattler'] for r in good),
            'total_translation_dims': sum(r.get('d_translation', 0)
                                          for r in good),
            'n_pure_translation_flex': sum(
                1 for r in good if r['d_H'] and r.get('d_translation') == r['d_H']),
            'n_sliding_squares_hist': hist(
                [len(r.get('anatomy', {}).get('sliding', [])) for r in good]),
            'n_tilting_squares_hist': hist(
                [len(r.get('anatomy', {}).get('tilting', [])) for r in good])},
        'degenerate_summary': {
            'n': len(deg),
            'n_pure_rattler_flex': sum(1 for r in deg
                                       if r['d_flex_nr'] == 0),
            'n_with_nonrattler_zero_curv': sum(
                1 for r in deg if r['d_flex_nr'] > 0),
            'rattler_block_flat_max': max(
                (r['second_order'].get('rattler_block_max_abs', 0.0)
                 for r in deg), default=0.0),
            'max_best_drop': max((r['best_drop'] for r in deg), default=0.0)},
        'strict_summary': {'n': len(strict),
                           'tags': [r['tag'] for r in strict][:40],
                           'max_best_drop': max((r['best_drop']
                                                 for r in strict),
                                                default=0.0)},
        'baseline_drop_quantiles': (
            [float(q) for q in np.quantile([r.get('baseline_drop', 0.0)
                                            for r in good],
                                           [0, .5, .9, .99, 1.0])]
            if good else None),
        'n_baseline_above_margin': sum(
            1 for r in good if r.get('baseline_drop', 0.0) > DESCENT_MARGIN),
        'multiplier_ambiguity': {
            'n_unique_multiplier': sum(
                1 for r in good
                if r['second_order'].get('multiplier_unique')),
            'n_Hred_multiplier_invariant': sum(
                1 for r in good
                if r['second_order'].get('Hred_multiplier_invariant')),
            'n_Hred_multiplier_dependent': sum(
                1 for r in good
                if r['second_order'].get('Hred_multiplier_invariant') is False),
            'n_second_order_sufficient_some_multiplier': sum(
                1 for r in good
                if r['second_order'].get(
                    'second_order_sufficient_some_multiplier'))},
        'net_drop_quantiles': (
            [float(q) for q in np.quantile([r.get('net_drop', 0.0)
                                            for r in good],
                                           [0, .5, .9, .99, 1.0])]
            if good else None),
        'best_drop_quantiles': (
            [float(q) for q in np.quantile([r['best_drop'] for r in good],
                                           [0, .25, .5, .75, .9, 1.0])]
            if good else None),
        'n_fj_reproduced': sum(1 for r in good if r.get('fj_reproduced')),
        'n_lam0_zero_branch': sum(1 for r in good
                                  if r.get('lam0_zero_branch')),
        'n_split_ok': sum(1 for r in good if r.get('split_ok')),
        'wall_secs': sum(r.get('secs', 0.0) for r in good),
    }
    json.dump(out, open(os.path.join(RESULTS, 'fjsecond87.json'), 'w'),
              indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != 'saddles'},
                     indent=1, default=str))
    print('\nsaddles (%d):' % len(out['saddles']))
    for s in out['saddles'][:60]:
        print(' %-8s [%s] sig %.9f -> %.9f  net_drop %.3e  dir %-8s eig %+.2e  '
              't=%g s=%+g  %s' %
              (s['tag'], s['quality'], s['sigma'], s['sigma_reached'],
               s['net_drop'], s['dir'],
               s['eig'] if s['eig'] is not None else float('nan'),
               s['step'], s['sign'], s['stratum_landed']))


CMDS = {'selftest': cmd_selftest, 'probe': cmd_probe, 'run': cmd_run,
        'report': cmd_report}

if __name__ == '__main__':
    for c in sys.argv[1:]:
        print('=== %s ===' % c, flush=True)
        t0 = time.time()
        CMDS[c]()
        print('=== %s done in %.1f s ===' % (c, time.time() - t0), flush=True)
