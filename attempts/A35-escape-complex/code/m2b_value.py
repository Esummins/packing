"""m2b_value.py -- A35 / M2-delta: the (V') per-stratum VALUE certificate.

Companion to m2b_lib's (W').  Same barrier machinery, but with

        A_ext^T omega = e_s        instead of        A_ext^T omega = 0.

Put Phi(z) = s - sum_r omega_r g_r(z), so grad Phi(z-hat) = e_s - A^T omega
=: -rho with ||rho||_1 = eps_w, and Phi(z-hat) = s-hat - sum_r omega_r
g_r(z-hat) >= s-hat - eps_0.  Sign discipline as in (W'):

    omega_r >= alpha_min > 0   for r in B (broken) and r in AUX,
    omega_r >= 0               for r in DOM,
    omega_r free               for r maintained,
    omega_r = 0                for rows outside the variant.

On Sbar(B) cap box(z-hat, h) the maintained rows vanish and all the other rows
are >= 0, so with Gsum := sum_{b in B} g_b + sum_{a in AUX} g_a,

    s(z) = Phi(z) + sum_B omega_b g_b + sum_AUX omega_a g_a + sum_DOM omega_d g_d
         >= s-hat - eps_0 - eps_w h - Hbar_W h^2 + alpha_min * Gsum .

  CASE 1  Gsum >= T(h) := (eps_0 + eps_w h + Hbar_W h^2)/alpha_min
          =>  s(z) >= s-hat directly.
  CASE 2  Gsum <= T(h)  =>  every row of A22's 34-row Krawczyk system lies in
          [0, T(h) + g_max] (maintained rows are 0, broken and aux rows are
          bounded by Gsum, and A22's system is exactly {0..35}\\{1,10,23,29}
          plus the two aux rows), so quantitative rigidity gives
              ||z - z-hat||_inf <= kappa (T(h) + g_max)/(1 - beta(h)) =: psi(h).

If psi(h) < h the two cases ITERATE: case 2 puts z in box(psi(h)) < box(h) and
the whole argument re-applies there.  Either case 1 fires at some stage (and
s >= s-hat), or the radii shrink to the fixed point and A22's theorem applies.
Either way  sigma >= s-hat on Sbar(B) cap box(h), equality only at z-hat.

Feasibility of the LP is exactly CONE-ALIVENESS on the extended generator set,
strengthened to a strictly positive floor on the broken and auxiliary rows.  So
(V') is the natural test to run on whatever survives (W'): a stratum that
survives the wedge test because it has a genuine first-order flex is still
certified if that flex is paid for by a positive multiplier floor.
"""
from __future__ import annotations

import os
import sys
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import m2b_lib as L  # noqa: E402
import m2_lib as M  # noqa: E402
import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

NV = SL.NV
NEXT = L.NEXT


def _particular(selection):
    """omega with A_ext^T omega = e_s, supported on A22's S rows."""
    Sx, F, N = L.ext_kernel(selection)
    mid, _ = L.ext_jacobian(selection)
    es = np.zeros(NV)
    es[SL.S_IDX] = 1.0
    wS = np.linalg.solve(mid[Sx].T, es)
    omp = np.zeros(NEXT)
    for r, k in enumerate(Sx):
        omp[k] = wS[r]
    return omp, Sx, F, N


def omega_lp_value(B, variant, selection, dom_floor=0.0, mode='maxfloor',
                   floor_target=1e-3, cap=10.0, weights=None):
    """LP for the (V') barrier.  Returns (omega float (50,), alpha_min)."""
    omp, Sx, F, N = _particular(selection)
    vrows = set(SL.v2_variant_rows(variant))
    strict = sorted(set(B) | set(L.AUX_POS))
    # DOMINANCE ROWS CARRY omega = 0 -- they are selection conditions, not
    # inequalities valid on all packings (see m2b_lib).
    dom = []
    dead = [k for k in range(L.NV2) if k not in vrows]
    dead += list(L.DOM_POS)
    fpos = {k: i for i, k in enumerate(F)}
    nf = len(F)
    if mode == 'maxfloor':
        c = np.zeros(nf + 1)
        c[-1] = -1.0
        Aub, bub = [], []
        for r in strict:
            row = np.zeros(nf + 1); row[:nf] = -N[:, r]; row[nf] = 1.0
            Aub.append(row); bub.append(omp[r])
        for r in dom:
            row = np.zeros(nf + 1); row[:nf] = -N[:, r]
            Aub.append(row); bub.append(omp[r] - dom_floor)
        for r in range(NEXT):
            r1 = np.zeros(nf + 1); r1[:nf] = N[:, r]
            Aub.append(r1); bub.append(cap - omp[r])
            r2 = np.zeros(nf + 1); r2[:nf] = -N[:, r]
            Aub.append(r2); bub.append(cap + omp[r])
        bounds = [(None, None)] * nf + [(None, cap)]
        for k in dead:
            bounds[fpos[k]] = (-omp[k], -omp[k])
        res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub),
                      bounds=bounds, method='highs')
        if not res.success:
            return None, None
        om = omp + N.T @ np.array(res.x[:nf])
        return om, float(min(om[r] for r in strict))
    # minL1 at a fixed floor: smaller ||omega|| => smaller Hbar_W => bigger h.
    # With `weights` = per-row Hessian mass this minimises an upper bound on
    # Hbar_W directly (triangle inequality), which is what sets the radius.
    nw = NEXT
    w = np.ones(nw) if weights is None else np.asarray(weights, dtype=float)
    c = np.concatenate([np.zeros(nf), w])
    Aub, bub = [], []
    for r in range(NEXT):
        r1 = np.zeros(nf + nw); r1[:nf] = N[:, r]; r1[nf + r] = -1.0
        Aub.append(r1); bub.append(-omp[r])
        r2 = np.zeros(nf + nw); r2[:nf] = -N[:, r]; r2[nf + r] = -1.0
        Aub.append(r2); bub.append(omp[r])
    for r in strict:
        row = np.zeros(nf + nw); row[:nf] = -N[:, r]
        Aub.append(row); bub.append(omp[r] - floor_target)
    for r in dom:
        row = np.zeros(nf + nw); row[:nf] = -N[:, r]
        Aub.append(row); bub.append(omp[r] - dom_floor)
    bounds = [(None, None)] * nf + [(0, None)] * nw
    for k in dead:
        bounds[fpos[k]] = (-omp[k], -omp[k])
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=bounds,
                  method='highs')
    if not res.success:
        return None, None
    om = omp + N.T @ np.array(res.x[:nf])
    return om, float(min(om[r] for r in strict))


def rationalise_omega_value(selection, om_float):
    """Rationalise: free part at 1e12, S part re-solved at dps 90 so that
    A_S^T omega_S = e_s - A_F^T omega_F."""
    Sx, F, _ = L.ext_kernel(selection)
    wf = [Fraction(round(Fraction(float(om_float[k])) * L.OMEGA_F_DEN),
                   L.OMEGA_F_DEN) for k in F]
    old, old_iv = mp.dps, iv.dps
    mp.dps = 90
    iv.dps = 90
    try:
        A = L.ext_jacobian_mp(selection, dps=90)
        AS = mp.zeros(NV, NV)
        for c, k in enumerate(Sx):
            for j in range(NV):
                AS[j, c] = A[k, j]
        rhs = mp.zeros(NV, 1)
        rhs[SL.S_IDX] = mp.mpf(1)
        for c, k in enumerate(F):
            wk = mp.mpf(wf[c].numerator) / mp.mpf(wf[c].denominator)
            for j in range(NV):
                rhs[j] -= A[k, j] * wk
        ws = mp.lu_solve(AS, rhs)
    finally:
        mp.dps = old
        iv.dps = old_iv
    om = [Fraction(0)] * NEXT
    for c, k in enumerate(F):
        om[k] = wf[c]
    for c, k in enumerate(Sx):
        om[k] = Fraction(round(Fraction(str(mp.nstr(ws[c], 60)))
                               * L.OMEGA_S_DEN), L.OMEGA_S_DEN)
    return om


def vprime_certificate(selection, om, alpha_min, h, Yq=None):
    """[IV] evaluation of the (V') certificate at radius h."""
    zh = SL.z_hat()
    if Yq is None:
        Yq = M.a22_Y()
    rows = L.ext_rows(selection)
    pbox = SL.point_box()
    e0 = 0.0
    for k in range(NEXT):
        if om[k] == 0:
            continue
        e0 += abs(float(om[k])) * M.iv_mag(SL.eval_geo(pbox, rows[k],
                                                       order=0).v)
    acc = [iv.mpf(0)] * NV
    for k in range(NEXT):
        if om[k] == 0:
            continue
        ok = t3lib._to_iv(om[k])
        j = SL.eval_geo(pbox, rows[k], order=1)
        for loc, gi in enumerate(rows[k]['vars']):
            acc[gi] = acc[gi] + ok * j.g[loc]
    ew = sum(M.iv_mag(acc[gi] - (iv.mpf(1) if gi == SL.S_IDX else iv.mpf(0)))
             for gi in range(NV))
    box = M.box_around(zh, h)
    accH = {}
    for k in range(NEXT):
        if om[k] == 0:
            continue
        ok = t3lib._to_iv(om[k])
        j = SL.eval_geo(box, rows[k], order=2)
        vs = rows[k]['vars']
        for a, ga in enumerate(vs):
            for b, gb in enumerate(vs):
                key = (ga, gb)
                t = ok * j.h[a][b]
                accH[key] = t if key not in accH else accH[key] + t
    Hm = np.zeros((NV, NV))
    for (a, b), x in accH.items():
        Hm[a, b] = M.iv_mag(x)
    Hbar = float(Hm.sum()) / 2.0
    Hinf = float(np.max(np.sum(Hm, axis=1)))
    kr = M.krawczyk_iv(zh, h, M.a22_S(), Yq)
    beta, kappa = kr['beta'], kr['kappa']
    hf = float(h)
    gmax = M.g_max_at_zhat()
    a = float(alpha_min)
    if beta >= 1.0 or a <= 0:
        return dict(ok=False, reason='beta >= 1 or alpha_min <= 0', beta=beta,
                    kappa=kappa, eps_0=e0, eps_w=ew, g_max=gmax, Hbar_W=Hbar,
                    Hinf_W=Hinf, h=M.fs(h), h_float=hf)
    T = (e0 + ew * hf + Hbar * hf * hf) / a + gmax
    psi = kappa * T / (1.0 - beta)
    return dict(ok=bool(psi < hf), beta=beta, kappa=kappa, eps_0=e0, eps_w=ew,
                g_max=gmax, Hbar_W=Hbar, Hinf_W=Hinf, alpha_min=a, T_W=T,
                psi=psi, psi_over_h=psi / hf, h=M.fs(h), h_float=hf,
                krawczyk_ok=bool(kr['ok']))


_HMASS = {}


def row_hessian_mass(selection, h):
    """Per-row Hessian mass  w_r = sum_{i,j} sup_box |d2 g_r / dz_i dz_j|.

    Hbar_W = (1/2) sum_ij |sum_r om_r H^r_ij| <= (1/2) sum_r |om_r| w_r, so
    minimising sum_r w_r |om_r| minimises an upper bound on the constant that
    sets the certified radius.
    """
    key = (tuple(sorted(selection.items())), str(h))
    if key in _HMASS:
        return _HMASS[key]
    box = M.box_around(SL.z_hat(), h)
    rows = L.ext_rows(selection)
    w = np.zeros(NEXT)
    for k, r in enumerate(rows):
        j = SL.eval_geo(box, r, order=2)
        tot = 0.0
        for a in range(len(r['vars'])):
            for b in range(len(r['vars'])):
                tot += M.iv_mag(j.h[a][b])
        w[k] = tot
    _HMASS[key] = w
    return w
