"""m2b_lib.py -- A35 / M2-delta: the (W') menu-complete wedge on basis v2.

theory.md (W').  The v2 escape-cone test of M1b is incomplete in two ways:

 (i)  AUXILIARY VALID ROWS.  Any polynomial inequality valid on ALL packings and
      ACTIVE at z-hat joins the possibly-active set of every cone / wedge / FJ
      test.  Two such rows exist and were dropped when v1 -> v2 replaced the
      centre-distance surrogates by flush rows:

          a0 : d^2(c0,c1) - 1 >= 0        a1 : d^2(c0,c3) - 1 >= 0

      They are valid for EVERY pair of interior-disjoint unit squares (the
      incircles have radius 1/2, so |c_i - c_j| >= 1) and M1b certified both are
      ACTIVE at z-hat (centre distance^2 = exactly 1).  They are never
      stratification coordinates -- they are permanent inequality rows, never
      "broken" -- so an escape direction v must satisfy grad a . v >= 0.

 (ii) TIED DOMINANCE ROWS.  The six repaired v2 rows put their contact corner at
      an edge ENDPOINT: the alternative corner of the same owner edge has
      dominance margin 0 to 1e-61 (M1b sec. 7 -- theory.md G5 biting at the jam
      itself).  A22's original rows are immune (tangential margins >= 0.015).
      Per D3' menu completeness, a feasible escape must be describable by SOME
      consistent selection S, and that selection's dominance rows

          dom_S : n_e(theta_o) . (q_other(p) - q_selected(p)) >= 0

      are then active-at-z-hat inequality rows of the test.  So the stratum is
      (W')-dead iff for EVERY selection S in its tie menu

          C_S(B) = { v : A_maint v = 0, A_B v >= 0, A_aux v >= 0,
                         A_dom(S) v >= 0 }  =  {0}.

ROW BOOK-KEEPING (the "extended row set", 50 rows, positions fixed):

    0 .. 41   the 42 v2 rows with the selection's corner choices applied
              (0..35 verbatim A22; 36..41 the repaired flush / (1,3) rows)
    42, 43    the two auxiliary dist rows a0, a1  (= v1 rows 36, 37 verbatim)
    44 .. 49  the six tied dominance rows of the selection

A22's 34-row Krawczyk subsystem S maps into this list as
    {0..35} \\ {1,10,23,29}  (32 rows)  +  {42,43}  (the two dist rows),
so A22's preconditioner Y, r_N and uniqueness theorem apply verbatim -- this is
also why the certificate can still finish through A22 even though M1b found
rank(rows 0..35) = 32.

THE (W') CERTIFICATE (generalised (W), see m2_routes.py for the v1 version).
Find rational omega over the extended row set with

    A_ext^T omega = 0 up to eps_w,
    omega_r >= alpha_min > 0   for r in B (broken) and r in AUX,
    omega_r >= 0               for r in DOM,
    omega_r free               for r maintained,

and set W(z) = sum_r omega_r g_r(z).  On Sbar(B) cap box(h) the maintained rows
vanish and every other term is >= 0, so

    W(z) >= alpha_min * ( sum_{b in B} g_b(z) + sum_{a in AUX} g_a(z) ) >= 0,
    W(z) <= eps_0 + eps_w h + Hbar_W(h) h^2         (Taylor, interval Hessian)

hence every row of A22's S obeys 0 <= g <= T_W(h), and the same rigidity /
iteration step as in m2_routes.py pins ||z - z-hat||_inf <= x* <= r_N, after
which A22's theorem gives sigma >= s-hat with equality only at z-hat.

Note the omega >= alpha_min on AUX (not just >= 0): the two dist rows ARE two of
A22's 34 Krawczyk rows, so they must be bounded ABOVE as well, which only a
strictly positive omega delivers.

Rigour tags as in M1/M2: [IV] mpmath.iv dps 60; [RFP] rigorous float64;
[LP]/[NUM] float64, not rigorous by itself.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import m2_lib as M  # noqa: E402   (v1 machinery: krawczyk_iv, hess bounds, ...)
import strata_lib as SL  # noqa: E402
import t3lib  # noqa: E402

iv.dps = 60

RESULTS = M.RESULTS
NV = SL.NV
NV2 = SL.NGEO_V2          # 42
AUX_POS = (42, 43)
DOM_POS = tuple(range(44, 50))
NEXT = 50                 # extended row count
REPAIRED = tuple(range(36, 42))   # the six tied rows

# A22's 34-row Krawczyk subsystem, expressed in EXTENDED positions
_A22_S_V1 = M.a22_S()                       # v1 indices, includes 36,37
S_EXT = [k if k < 36 else (42 if k == 36 else 43) for k in _A22_S_V1]


# ------------------------------------------------------------- row builders

def aux_constraints():
    """The two auxiliary valid+active dist rows (v1 rows 36, 37 verbatim)."""
    return [dict(c) for c in SL.load_cert()['constraints'][36:38]]


def selection_iter(variant):
    """All corner selections in the tie menu of `variant`.

    A selection is a dict {v2 row index -> corner}.  Only the six repaired rows
    are tied; the (1,3) branch dropped by the variant is not selected over.
    """
    rows = [k for k in REPAIRED if k in set(SL.v2_variant_rows(variant))]
    base = {k: SL.V2_NEW_ROWS[k - 36]['corner'] for k in rows}
    alt = {k: SL.V2_FLUSH_TIE_ALTERNATIVES[SL.V2_NEW_ROWS[k - 36]['name']]
           ['corner'] for k in rows}
    for bits in itertools.product((0, 1), repeat=len(rows)):
        sel = {}
        for k, b in zip(rows, bits):
            sel[k] = base[k] if b == 0 else alt[k]
        yield sel


def ext_constraints(selection):
    """The 50 extended constraint dicts for a given corner selection."""
    cons = SL.geo_constraints_v2()
    out = [dict(c) for c in cons]
    for k, corner in selection.items():
        out[k] = dict(out[k])
        out[k]['corner'] = corner
    out += aux_constraints()
    for k in REPAIRED:
        c = SL.V2_NEW_ROWS[k - 36]
        sel = selection.get(k, c['corner'])
        other = (SL.V2_FLUSH_TIE_ALTERNATIVES[c['name']]['corner']
                 if sel == c['corner'] else c['corner'])
        out.append({'kind': 'dom', 'o': c['j'], 'e': c['edge'], 'p': c['i'],
                    'k': sel, 'm': other,
                    'name': 'DOM[%s|%d>%d]' % (c['name'], sel, other)})
    return out


def ext_rows(selection):
    """The 50 extended rows in t3lib language."""
    out = []
    for c in ext_constraints(selection):
        if c['kind'] == 'dom':
            out.append(t3lib.dom_row(c['o'], c['e'], c['p'], c['k'], c['m']))
        else:
            out.append(SL.to_t3_row(c))
    return out


def ext_row_names(selection):
    out = []
    for i, c in enumerate(ext_constraints(selection)):
        if 'name' in c:
            out.append(c['name'])
        elif i in AUX_POS:
            out.append('AUXdist')
        else:
            out.append('row%d' % i)
    return out


_EXTJAC = {}


def ext_jacobian(selection, box=None):
    """(mid, rad) float64 arrays of the 50 x 34 extended interval Jacobian."""
    key = tuple(sorted(selection.items()))
    if box is None and key in _EXTJAC:
        return _EXTJAC[key]
    if box is None:
        box = SL.point_box()
    rows = ext_rows(selection)
    mid = np.zeros((NEXT, NV))
    rad = np.zeros((NEXT, NV))
    for k, r in enumerate(rows):
        j = SL.eval_geo(box, r, order=1)
        for loc, gi in enumerate(r['vars']):
            m_, r_ = SL._iv_mid_rad(j.g[loc])
            mid[k, gi] = m_
            rad[k, gi] = r_
    out = (mid, rad)
    if box is None:
        _EXTJAC[key] = out
    return out


def ext_values_iv(selection, box):
    rows = ext_rows(selection)
    return [SL.eval_geo(box, r, order=0).v for r in rows]


# ------------------------------------------------------- escape cone C_S(B)

def cone_is_trivial(E, G, tol=1e-8):
    """Is  {v : E v = 0, G v >= 0}  =  {0} ?

    Returns (trivial: bool, dof: int, detail: dict).  Exact-ish and CHEAP:
    reduce to the kernel of E (dimension d) and test the cone {u : (G N) u >= 0}
    in R^d.  d = 0 -> trivial (an EMPTY stratum).  d = 1 -> a sign test.
    d = 2 -> an angular-gap test.  d >= 3 -> an LP.  Only d >= 3 costs.
    """
    _, sv, Vt = np.linalg.svd(E) if E.shape[0] else (
        None, np.zeros(0), np.eye(NV))
    r = int((sv > 1e-9).sum())
    d = NV - r
    if d <= 0:
        return True, 0, {'reason': 'dof 0 (empty stratum)'}
    N = Vt[r:]                     # d x 34, orthonormal
    C = G @ N.T                    # m x d
    m = C.shape[0]
    if m == 0:
        return False, d, {'reason': 'no inequality rows'}
    nz = np.linalg.norm(C, axis=1) > tol
    C = C[nz]
    if C.shape[0] == 0:
        return False, d, {'reason': 'all inequality rates vanish on the kernel'}
    if d == 1:
        c = C[:, 0]
        trivial = bool(c.max() > tol and c.min() < -tol)
        return trivial, d, {'reason': 'sign test', 'max': float(c.max()),
                            'min': float(c.min())}
    if d == 2:
        ang = np.sort(np.arctan2(C[:, 1], C[:, 0]))
        gaps = np.diff(np.concatenate([ang, [ang[0] + 2 * np.pi]]))
        # cone {u : C u >= 0} = {0}  iff the normals positively span R^2
        # iff the largest angular gap between consecutive normals is < pi
        trivial = bool(gaps.max() < np.pi - 1e-9)
        return trivial, d, {'reason': 'angular gap', 'max_gap': float(gaps.max())}
    # d >= 3 : LP.  max sum(Cu) s.t. Cu >= 0, |u|_inf <= 1
    res = linprog(-C.sum(axis=0), A_ub=-C, b_ub=np.zeros(C.shape[0]),
                  bounds=[(-1, 1)] * d, method='highs')
    if not res.success:
        return False, d, {'reason': 'LP failed'}
    opt = float(-res.fun)
    if opt > 1e-7:
        return False, d, {'reason': 'LP', 'opt': opt}
    svC = np.linalg.svd(C, compute_uv=False)
    kerC = int((svC < 1e-9).sum()) + max(0, d - len(svC))
    return bool(kerC == 0), d, {'reason': 'LP', 'opt': opt, 'kerC': kerC}


def wprime_test(B, variant, selections=None, mid_cache=None,
                use_aux=True, use_dom=True, first_alive_stops=True):
    """(W') verdict for break set B in `variant`.

    Returns dict(dead, n_selections_tested, alive_selection, dofs, detail).
    Dead  <=>  C_S(B) = {0} for EVERY selection S in the menu.
    """
    Bs = set(B)
    vrows = [k for k in SL.v2_variant_rows(variant)]
    Mrows = [k for k in vrows if k not in Bs]
    Brows = [k for k in vrows if k in Bs]
    ineq_extra = []
    if use_aux:
        ineq_extra += list(AUX_POS)
    sels = list(selection_iter(variant)) if selections is None else selections
    alive = None
    dofs = []
    details = []
    for si, sel in enumerate(sels):
        mid = (mid_cache.get(tuple(sorted(sel.items())))
               if mid_cache is not None else None)
        if mid is None:
            mid, _ = ext_jacobian(sel)
            if mid_cache is not None:
                mid_cache[tuple(sorted(sel.items()))] = mid
        dom = [p for p in DOM_POS
               if (p - 44 + 36) in set(vrows)] if use_dom else []
        E = mid[Mrows]
        G = mid[Brows + ineq_extra + dom] if (Brows or ineq_extra or dom) \
            else np.zeros((0, NV))
        triv, d, det = cone_is_trivial(E, G)
        dofs.append(d)
        details.append(det)
        if not triv:
            alive = (si, sel, det)
            if first_alive_stops:
                break
    return dict(dead=(alive is None), n_selections=len(sels),
                n_tested=len(dofs), alive_selection=(
                    None if alive is None else
                    {'index': alive[0],
                     'selection': {str(k): v for k, v in alive[1].items()},
                     'detail': alive[2]}),
                dof_min=(min(dofs) if dofs else None),
                dof_max=(max(dofs) if dofs else None))


# --------------------------------------------- (W') Motzkin dual certificate

_KER_EXT = {}


def ext_kernel(selection):
    """Parametrisation of ker(A_ext^T): free rows = extended \\ S_EXT (16 rows).

    omega_S = -(A_S^T)^{-1} A_F^T omega_F.  Returns (S_EXT, FREE, N) with
    N a (16 x 50) float basis, N[c] the self-stress with omega_F = e_c.
    """
    key = tuple(sorted(selection.items()))
    if key in _KER_EXT:
        return _KER_EXT[key]
    mid, _ = ext_jacobian(selection)
    F = [k for k in range(NEXT) if k not in set(S_EXT)]
    AS = mid[S_EXT].T
    AF = mid[F].T
    Wm = -np.linalg.solve(AS, AF)          # 34 x 16
    N = np.zeros((len(F), NEXT))
    for c in range(len(F)):
        N[c, F[c]] = 1.0
        for r, k in enumerate(S_EXT):
            N[c, k] = Wm[r, c]
    out = (list(S_EXT), F, N)
    _KER_EXT[key] = out
    return out


def omega_lp(B, variant, selection, dom_floor=1e-3, mode='minL1'):
    """LP for the (W') barrier omega, over the extended row set.

    Sign discipline (this is the whole soundness of the certificate):
      * omega_r >= alpha (strictly positive) for r in B and r in AUX  -- these
        are the rows whose gaps must be bounded ABOVE on the stratum;
      * omega_r >= dom_floor > 0 for the DOM rows of this variant -- they are
        >= 0 on the stratum, so a nonnegative coefficient only helps, and a
        strictly positive floor makes the sign survive rationalisation;
      * omega_r free for maintained v2 rows (they are = 0 on the stratum);
      * omega_r = 0 for every row NOT in this variant (the dropped (1,3) branch
        and its dominance row) -- otherwise a row that is not part of the
        stratum's description would enter W with an uncontrolled sign.

    mode 'minL1'  : min sum|omega| s.t. omega_r >= 1 on the strict set.
                    Minimises the Hessian bound Hbar_W (which scales with
                    ||omega||) at fixed alpha_min = 1, i.e. maximises the
                    certified radius.  Preferred.
    mode 'maxfloor': max t s.t. omega_r >= t, ||omega||_inf <= 1.  Fallback.

    Returns (omega_F float, alpha_min) or (None, None).
    """
    _, F, N = ext_kernel(selection)
    vrows = set(SL.v2_variant_rows(variant))
    strict = sorted(set(B) | set(AUX_POS))
    # DOMINANCE ROWS CARRY omega = 0.  They are SELECTION conditions, not
    # inequalities valid on all packings, so a positive coefficient in the
    # barrier would be unsound.  They remain in the WEDGE TEST (where the menu
    # argument justifies them) but never in a certificate.
    dom = []
    dead = [k for k in range(NV2) if k not in vrows]
    dead += list(DOM_POS)
    nf = len(F)
    fpos = {k: i for i, k in enumerate(F)}
    # every 'dead' row is a FREE parameter of the kernel parametrisation, so
    # pinning it to 0 is a variable bound, not an extra equation.
    assert all(k in fpos for k in dead), 'dead row is not a free parameter'
    if mode == 'maxfloor':
        c = np.zeros(nf + 1); c[-1] = -1.0
        Aub, bub = [], []
        for r in strict:
            row = np.zeros(nf + 1); row[:nf] = -N[:, r]; row[nf] = 1.0
            Aub.append(row); bub.append(0.0)
        for r in dom:
            row = np.zeros(nf + 1); row[:nf] = -N[:, r]
            Aub.append(row); bub.append(-dom_floor)
        for r in range(NEXT):
            r1 = np.zeros(nf + 1); r1[:nf] = N[:, r]
            Aub.append(r1); bub.append(1.0)
            r2 = np.zeros(nf + 1); r2[:nf] = -N[:, r]
            Aub.append(r2); bub.append(1.0)
        bounds = [(None, None)] * nf + [(None, 10.0)]
        for k in dead:
            bounds[fpos[k]] = (0.0, 0.0)
        res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub),
                      bounds=bounds, method='highs')
        if not res.success:
            return None, None
        return np.array(res.x[:nf]), float(-res.fun)
    # ---- minL1: variables [u (nf), w (NEXT)] with |omega_r| <= w_r
    nw = NEXT
    c = np.concatenate([np.zeros(nf), np.ones(nw)])
    Aub, bub = [], []
    for r in range(NEXT):
        r1 = np.zeros(nf + nw); r1[:nf] = N[:, r]; r1[nf + r] = -1.0
        Aub.append(r1); bub.append(0.0)
        r2 = np.zeros(nf + nw); r2[:nf] = -N[:, r]; r2[nf + r] = -1.0
        Aub.append(r2); bub.append(0.0)
    for r in strict:
        row = np.zeros(nf + nw); row[:nf] = -N[:, r]
        Aub.append(row); bub.append(-1.0)
    for r in dom:
        row = np.zeros(nf + nw); row[:nf] = -N[:, r]
        Aub.append(row); bub.append(-dom_floor)
    bounds = [(None, None)] * nf + [(0, None)] * nw
    for k in dead:
        bounds[fpos[k]] = (0.0, 0.0)
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=bounds,
                  method='highs')
    if not res.success:
        return None, None
    u = np.array(res.x[:nf])
    om = N.T @ u
    return u, float(min(om[r] for r in strict))


OMEGA_F_DEN = 10 ** 12
OMEGA_S_DEN = 10 ** 45


def rationalise_omega(selection, omegaF):
    """omega_F -> exact rational omega (50 Fractions), omega_S re-solved at
    mpmath dps 90 (M1/M2 recipe)."""
    Sx, F, _ = ext_kernel(selection)
    wf = [Fraction(round(Fraction(float(v)) * OMEGA_F_DEN), OMEGA_F_DEN)
          for v in omegaF]
    old = mp.dps
    mp.dps = 90
    try:
        A = ext_jacobian_mp(selection, dps=90)      # 50 x 34
        AS = mp.zeros(NV, NV)
        for c, k in enumerate(Sx):
            for j in range(NV):
                AS[j, c] = A[k, j]
        rhs = mp.zeros(NV, 1)
        for c, k in enumerate(F):
            wk = mp.mpf(wf[c].numerator) / mp.mpf(wf[c].denominator)
            for j in range(NV):
                rhs[j] -= A[k, j] * wk
        ws = mp.lu_solve(AS, rhs)
    finally:
        mp.dps = old
    om = [Fraction(0)] * NEXT
    for c, k in enumerate(F):
        om[k] = wf[c]
    for c, k in enumerate(Sx):
        om[k] = Fraction(round(Fraction(str(mp.nstr(ws[c], 60))) * OMEGA_S_DEN),
                         OMEGA_S_DEN)
    return om


def ext_jacobian_mp(selection, dps=90):
    """50 x 34 extended Jacobian at z-hat, mpmath point arithmetic."""
    old = mp.dps
    old_iv = iv.dps
    mp.dps = dps
    iv.dps = dps
    try:
        rows = ext_rows(selection)
        zbox = [t3lib._to_iv(x) for x in SL.z_hat()]
        A = mp.zeros(NEXT, NV)
        for k, r in enumerate(rows):
            j = SL.eval_geo(zbox, r, order=1)
            for loc, gi in enumerate(r['vars']):
                A[k, gi] = mp.mpf(j.g[loc].a) / 2 + mp.mpf(j.g[loc].b) / 2
    finally:
        mp.dps = old
        iv.dps = old_iv
    return A


def omega_constants(selection, om, h):
    """[IV] (eps_0, eps_w, Hbar_W, Hinf_W) for W = sum_r om_r g_r on box(h)."""
    zh = SL.z_hat()
    rows = ext_rows(selection)
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
    ew = sum(M.iv_mag(acc[gi]) for gi in range(NV))
    box = M.box_around(zh, h)
    Hm = np.zeros((NV, NV))
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
    for (a, b), x in accH.items():
        Hm[a, b] = M.iv_mag(x)
    return e0, ew, float(Hm.sum()) / 2.0, float(np.max(np.sum(Hm, axis=1)))


def wprime_certificate(selection, om, alpha_min, h, Yq=None):
    """Evaluate the (W') pinning certificate at radius h.  All [IV]."""
    zh = SL.z_hat()
    if Yq is None:
        Yq = M.a22_Y()
    e0, ew, Hbar, Hinf = omega_constants(selection, om, h)
    kr = M.krawczyk_iv(zh, h, M.a22_S(), Yq)   # v1 S rows == S_EXT rows
    beta, kappa = kr['beta'], kr['kappa']
    hf = float(h)
    gmax = M.g_max_at_zhat()
    if beta >= 1.0:
        return dict(ok=False, reason='beta >= 1', beta=beta, kappa=kappa,
                    eps_0=e0, eps_w=ew, g_max=gmax, Hbar_W=Hbar, Hinf_W=Hinf,
                    h=M.fs(h), h_float=hf)
    a = float(alpha_min)
    C = kappa / ((1.0 - beta) * a)
    T = (e0 + ew * hf + Hbar * hf * hf) / a + gmax
    psi = kappa * T / (1.0 - beta)
    ok = psi < hf
    xstar = float('inf')
    if ok:
        x = hf
        for _ in range(400):
            x = C * (e0 + ew * x + Hbar * x * x) + kappa * gmax / (1.0 - beta)
        xstar = x
    return dict(ok=bool(ok), beta=beta, kappa=kappa, eps_0=e0, eps_w=ew,
                g_max=gmax, Hbar_W=Hbar, Hinf_W=Hinf,
                alpha_min=float(alpha_min), C_contraction=C, T_W=T, psi=psi,
                psi_over_h=psi / hf, x_star=xstar, h=M.fs(h), h_float=hf,
                krawczyk_ok=bool(kr['ok']))


# ------------------------------------------------------------- cone-aliveness

def cone_alive(B, variant, selection, mid=None, use_aux=True, use_dom=True):
    """Is e_s in cone{ grad g_r : r maintained } + cone{aux, dom} ?

    The aux and dominance rows are ordinary  g >= 0  rows in FJ stationarity,
    so they carry lambda >= 0 and ADD generators -- aliveness can only GROW
    when they are included.  [LP]
    """
    if mid is None:
        mid, _ = ext_jacobian(selection)
    vrows = set(SL.v2_variant_rows(variant))
    gens = [k for k in sorted(vrows) if k not in set(B)]
    if use_aux:
        gens += list(AUX_POS)
    if use_dom:
        gens += [p for p in DOM_POS if (p - 44 + 36) in vrows]
    A = mid[gens]
    n = len(gens)
    beq = np.zeros(NV); beq[SL.S_IDX] = 1.0
    res = linprog(np.zeros(n), A_eq=A.T, b_eq=beq,
                  bounds=[(0, None)] * n, method='highs')
    return bool(res.success), gens
