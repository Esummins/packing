"""a36_lib.py -- A36 / levers: BASIS v3, the 8 branch axes, and the (V')
reach machinery.

Builds on A35 (attempts/A35-escape-complex/code: strata_lib, m2_lib, m2b_lib,
m2b_value) via sys.path -- REUSED, not modified.  A35 is read-only for A36.

--------------------------------------------------------------------------
BASIS v3  (44 "geometric" rows + 2 aux + 24 alternative corner rows = 70)
--------------------------------------------------------------------------
  0 .. 35   verbatim A22 krawczyk_cert.json constraints 0..35
  36 F0-1a  flush (0,1), owner 0 right  edge (e=1) vs corner 3 of sq1   [A01a]
  37 F0-1b  flush (0,1), owner 1 left   edge (e=3) vs corner 2 of sq0   [A01b]
  38 F0-3a  flush (0,3), owner 0 top    edge (e=2) vs corner 0 of sq3   [A03a]
  39 F0-3b  flush (0,3), owner 3 bottom edge (e=0) vs corner 3 of sq0   [A03b]
  40 C1-3x  (1,3), owner 1 left   edge (e=3) vs corner 1 of sq3         [B13x ]
  41 C1-3y  (1,3), owner 3 bottom edge (e=0) vs corner 3 of sq1         [B13y ]
  42 C1-3x' (1,3), owner 3 right  edge (e=1) vs corner 3 of sq1         [B13x'] NEW
  43 C1-3y' (1,3), owner 1 top    edge (e=2) vs corner 1 of sq3         [B13y'] NEW
  44, 45    the two auxiliary dist rows a0 = d^2(c0,c1)-1, a1 = d^2(c0,c3)-1
            (= A22 constraints 36, 37 verbatim)
  46 .. 69  for each of the 8 branch axes, the THREE corner rows of that axis
            other than the canonical one above (positions 46 + 3*ax + j,
            j indexing the other corners in increasing corner order).

Rows 36..43 are already one corner row each of their axis; together with
46..69 every branch axis exposes all FOUR of its corner rows, which L1.1 makes
simultaneously valid on the branch.  So the emitter may load any of them.

--------------------------------------------------------------------------
THE 8 BRANCH AXES and the 16 VARIANTS
--------------------------------------------------------------------------
An "axis" is a triple (owner o, owner edge e, other square p).  Its corner
rows are  g_{e,k}(z) = n_e(theta_o).(q_k(p) - c_o) - 1/2,  k = 0..3, in
t3lib sep_row language  sep_row(o, e, p, k)  ==  A22 dict
{'kind':'edge','i':p,'corner':k,'j':o,'edge':e}.

  ax 0  A01a  (o=0, e=1, p=1)      contact (0,1)
  ax 1  A01b  (o=1, e=3, p=0)      contact (0,1)
  ax 2  A03a  (o=0, e=2, p=3)      contact (0,3)
  ax 3  A03b  (o=3, e=0, p=0)      contact (0,3)
  ax 4  B13x  (o=1, e=3, p=3)      contact (1,3)
  ax 5  B13x' (o=3, e=1, p=1)      contact (1,3)
  ax 6  B13y  (o=3, e=0, p=1)      contact (1,3)
  ax 7  B13y' (o=1, e=2, p=3)      contact (1,3)

VARIANT V = (one axis for (0,1), one for (0,3), one for (1,3)) -- 2*2*4 = 16.
L1 (levers.md) says every feasible z in box(z-hat, h) lies in >= 1 variant.

--------------------------------------------------------------------------
THE SOUND INEQUALITY CHAIN OF THE (V') BARRIER  (documented, then coded)
--------------------------------------------------------------------------
Fix a variant V.  Let
    R_V  = {0..35} u {44,45} u (the 12 corner rows of V's three branch axes)
be V's VALID row set: for every feasible z in box(z-hat,h) that belongs to
variant V, g_r(z) >= 0 for all r in R_V.  (Rows 0..35: A22's own SAT-selection
validity, re-certified on box(h) by the tangential/depth margins.  Rows 44,45:
globally valid, incircle argument.  Branch corner rows: L1.1 -- the branch axis
separates the pair, hence all four of its corner rows are >= 0.)

Let P (the PIN set) be a square 34-row subsystem, P subset of R_V, with a
rational preconditioner Y and beta(h) = ||I - Y A_P(box(h))||_inf < 1,
kappa = ||Y||_inf.

Take omega >= 0 supported on R_V with omega_r > 0 for every r in P.  Put
    W(z) = sum_r omega_r g_r(z),    Phi(z) = s - W(z).
Then, with all quantities [IV] over box = box(z-hat, h):

  eps_0 := sum_r |omega_r| |g_r(z-hat)|         (>= |W(z-hat)|)
  eps_w := || A(z-hat)^T omega - e_s ||_1       (= ||grad Phi(z-hat)||_1)
  Hbar  := (1/2) sum_{i,j} sup_box |d^2 W / dz_i dz_j|
  E(x)  := eps_0 + eps_w x + Hbar x^2
  g_max := max_k |g_k(z-hat)|   (6.69e-60)
  c_r   := max_i |Y_ir|,   kappa := ||Y||_inf = max_i sum_r |Y_ir|,
  kappa_eff := max_{r in P} c_r / omega_r.

  (T1)  Phi(z) >= Phi(z-hat) + grad Phi(z-hat).d - Hbar ||d||_inf^2
                >= s-hat - E(h)                             (d = z - z-hat)
        [Taylor with integral remainder; the quadratic form bound is
         |d^T H d| <= sum_ij sup|H_ij| |d_i||d_j| <= 2*Hbar*h^2, so the
         remainder (1/2)|d^T H d| <= Hbar h^2.]

  (T2)  s(z) = Phi(z) + W(z) >= Phi(z) + Gw(z),
        Gw(z) := sum_{r in P} omega_r g_r(z) >= 0,
        because every loaded row has omega_r >= 0 and g_r(z) >= 0, so dropping
        the rows outside P only decreases the sum.

  DICHOTOMY at radius h.
   CASE 1  Gw(z) >= E(h)  ==>  s(z) >= s-hat.                       (T1)+(T2)
   CASE 2  Gw(z) <= E(h).  Every term omega_r g_r(z), r in P, is >= 0, so for
           each row i of Y,
             |sum_r Y_ir g_r(z)| <= sum_r |Y_ir| g_r(z)
                                  = sum_r (|Y_ir|/omega_r) (omega_r g_r(z))
                                  <= max_r(|Y_ir|/omega_r) * Gw(z)
                                  <= kappa_eff * E(h).
           ==>  ||Y F_P(z)||_inf <= kappa_eff E(h),  and
                ||Y F_P(z-hat)||_inf <= kappa g_max.  The mean-value identity
             Y(F_P(z) - F_P(z-hat)) = d - (I - Y A_P(xi)) d
           with beta(h) = sup_box ||I - Y A_P||_inf < 1 then gives
               ||d||_inf <= (kappa_eff E(h) + kappa g_max)/(1 - beta(h)) =: psi(h).

  ** This "max-form" is the A36 sharpening of A35/M2b's chain, which used the
     cruder  g_r <= E/alpha  for each r in P separately and then kappa:
         psi_A35 = kappa (E/alpha + g_max)/(1-beta).
     Because  kappa_eff = max_r c_r/omega_r  <=  kappa/alpha  with typically a
     factor 15-20 to spare (the rows with a large |Y_ir| are exactly the rows
     that carry a large omega_r), the max-form buys an order of magnitude of
     reach for free.  Both forms are evaluated; the certificate reports both. **

  If psi(h) < h the dichotomy ITERATES at radius psi(h) (A35's variant C), and
  the radii fall to the least fixed point x* of
      x = [kappa_eff/(1-beta)] E(x) + kappa g_max/(1-beta).
  (Legitimate because Hbar and beta on the smaller box are bounded by their
  values on box(h).)  If x* <= r_N = 1/2000, A22's local rigidity theorem
  finishes: sigma >= s-hat on box(z-hat,h), with equality only at z-hat.

  BINDING TERM.  eps_0, eps_w, g_max are all ~1e-45 or smaller, so
      psi(h) < h   <==>   approximately   h < (1 - beta(h)) / (kappa_eff Hbar(h)).
  The reach is therefore set by the single product  kappa_eff * Hbar/(1-beta)
  -- the levers of L2: the omega profile (raise omega_r where c_r is large,
  lower it where the row curvature w_r is large), and the pin basis P/Y (which
  sets c, kappa and beta).

Rigour tags: [IV] mpmath.iv dps 60; [RFP] rigorous float64; [LP]/[NUM] float64.
"""
from __future__ import annotations

import itertools
import os
import sys
from fractions import Fraction

import numpy as np
from mpmath import iv, mp
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
A36 = os.path.abspath(os.path.join(HERE, '..'))
RESULTS = os.path.join(A36, 'results')
ATTEMPTS = os.path.abspath(os.path.join(A36, '..'))
A35C = os.path.join(ATTEMPTS, 'A35-escape-complex', 'code')
A22D = os.path.join(ATTEMPTS, 'A22-local-rigidity')
for p in (A35C, A22D, os.path.join(ATTEMPTS, 'A30-t3-pilot')):
    if p not in sys.path:
        sys.path.insert(0, p)

import strata_lib as SL           # noqa: E402  (A35, read-only)
import m2_lib as M                # noqa: E402  (A35, read-only)
import t3lib                      # noqa: E402  (A30, read-only)

iv.dps = 60

NV = SL.NV                        # 34
S_IDX = SL.S_IDX                  # 33
R_N = M.a22_rN()                  # Fraction 1/2000

# --------------------------------------------------------------- v3 row table

# (name, owner o, owner edge e, other square p, canonical corner, base position)
AXES = [
    ('A01a',  0, 1, 1, 3, 36),
    ('A01b',  1, 3, 0, 2, 37),
    ('A03a',  0, 2, 3, 0, 38),
    ('A03b',  3, 0, 0, 3, 39),
    ('B13x',  1, 3, 3, 1, 40),
    ("B13x'", 3, 1, 1, 3, 42),
    ('B13y',  3, 0, 1, 3, 41),
    ("B13y'", 1, 2, 3, 1, 43),
]
AXIS_NAME = [a[0] for a in AXES]
NAXIS = 8
AUX_POS = (44, 45)
NEXT3 = 70
EXTRA0 = 46                       # first alternative-corner position

# contact -> list of admissible axis indices
CONTACT_AXES = [[0, 1], [2, 3], [4, 5, 6, 7]]
CONTACT_NAME = ['(0,1)', '(0,3)', '(1,3)']
VARIANTS = [tuple(v) for v in itertools.product(*CONTACT_AXES)]   # 16

# KILLED (axis) combinations, per L1.2: (pair label, owner, edge, other)
KILLED_AXES = (
    [('(0,1)', 0, e, 1) for e in (0, 2, 3)] +
    [('(0,1)', 1, e, 0) for e in (0, 1, 2)] +
    [('(0,3)', 0, e, 3) for e in (0, 1, 3)] +
    [('(0,3)', 3, e, 0) for e in (1, 2, 3)] +
    [('(1,3)', 1, e, 3) for e in (0, 1)] +
    [('(1,3)', 3, e, 1) for e in (2, 3)]
)


def edge_con(o, e, p, k, name=None):
    """A22-language constraint dict for sep_row(o, e, p, k)."""
    d = {'kind': 'edge', 'i': p, 'corner': k, 'j': o, 'edge': e}
    if name:
        d['name'] = name
    return d


def axis_corner_positions(ax):
    """The four extended positions carrying the four corner rows of axis ax,
    indexed by CORNER (0..3)."""
    _, o, e, p, kc, base = AXES[ax]
    out = {kc: base}
    others = [k for k in range(4) if k != kc]
    for j, k in enumerate(others):
        out[k] = EXTRA0 + 3 * ax + j
    return out


def axis_rows(ax):
    """All four extended positions of axis ax, as a sorted list."""
    return sorted(axis_corner_positions(ax).values())


_CONS3 = None


def v3_constraints():
    """The 70 extended constraint dicts (A22 language)."""
    global _CONS3
    if _CONS3 is not None:
        return [dict(c) for c in _CONS3]
    K = SL.load_cert()
    out = [dict(c) for c in K['constraints'][:36]]
    out += [None] * 34
    for ax, (nm, o, e, p, kc, base) in enumerate(AXES):
        cpos = axis_corner_positions(ax)
        for k, pos in cpos.items():
            out[pos] = edge_con(o, e, p, k,
                                name='%s[k%d]' % (nm, k))
    out[44] = dict(K['constraints'][36])
    out[45] = dict(K['constraints'][37])
    assert all(c is not None for c in out) and len(out) == NEXT3
    _CONS3 = out
    return [dict(c) for c in out]


def v3_rows():
    return [SL.to_t3_row(c) for c in v3_constraints()]


def v3_names():
    return [c.get('name', 'row%d' % i) for i, c in enumerate(v3_constraints())]


# A22's 34-row Krawczyk subsystem in v3 positions
S_EXT = [k if k < 36 else (44 if k == 36 else 45) for k in M.a22_S()]


def variant_rows(V):
    """R_V: the valid row set of variant V = (ax01, ax03, ax13)."""
    rows = set(range(36)) | set(AUX_POS)
    for ax in V:
        rows |= set(axis_rows(ax))
    return sorted(rows)


def variant_tag(V):
    return '-'.join(AXIS_NAME[a] for a in V).replace("'", 'p')


# ------------------------------------------------------------ jacobian / kernel

_JAC = {}


def v3_jacobian(box=None):
    """(mid, rad) float64 of the 70 x 34 interval Jacobian (at z-hat if box
    is None)."""
    key = 'zhat' if box is None else id(box)
    if box is None and key in _JAC:
        return _JAC[key]
    bx = SL.point_box() if box is None else box
    rows = v3_rows()
    mid = np.zeros((NEXT3, NV))
    rad = np.zeros((NEXT3, NV))
    for k, r in enumerate(rows):
        j = SL.eval_geo(bx, r, order=1)
        for loc, gi in enumerate(r['vars']):
            m_, r_ = SL._iv_mid_rad(j.g[loc])
            mid[k, gi] = m_
            rad[k, gi] = r_
    if box is None:
        _JAC[key] = (mid, rad)
    return mid, rad


def v3_jacobian_mp(dps=90):
    """70 x 34 Jacobian at z-hat in mpmath point arithmetic (for the exact
    omega_S re-solve)."""
    old, old_iv = mp.dps, iv.dps
    mp.dps = dps
    iv.dps = dps
    try:
        rows = v3_rows()
        zbox = [t3lib._to_iv(x) for x in SL.z_hat()]
        A = mp.zeros(NEXT3, NV)
        for k, r in enumerate(rows):
            j = SL.eval_geo(zbox, r, order=1)
            for loc, gi in enumerate(r['vars']):
                A[k, gi] = mp.mpf(j.g[loc].a) / 2 + mp.mpf(j.g[loc].b) / 2
    finally:
        mp.dps = old
        iv.dps = old_iv
    return A


_KER = {}


def kernel_param(Sx):
    """Parametrisation of {omega : A^T omega = e_s} with pin/basis rows Sx.

    Returns (Sx, F, N, omp) where omp is the particular solution supported on
    Sx and N[c] (len(F) x NEXT3) spans the kernel of A_ext^T.
    """
    key = tuple(Sx)
    if key in _KER:
        return _KER[key]
    mid, _ = v3_jacobian()
    F = [k for k in range(NEXT3) if k not in set(Sx)]
    AS = mid[list(Sx)].T
    AF = mid[F].T
    Wm = -np.linalg.solve(AS, AF)
    N = np.zeros((len(F), NEXT3))
    for c in range(len(F)):
        N[c, F[c]] = 1.0
        for r, k in enumerate(Sx):
            N[c, k] = Wm[r, c]
    es = np.zeros(NV)
    es[S_IDX] = 1.0
    wS = np.linalg.solve(mid[list(Sx)].T, es)
    omp = np.zeros(NEXT3)
    for r, k in enumerate(Sx):
        omp[k] = wS[r]
    out = (list(Sx), F, N, omp)
    _KER[key] = out
    return out


# ------------------------------------------------------------- Hessian masses

_HMASS = {}


def row_hessian_mass(h):
    """w_r = sum_{i,j} sup_{box(h)} |d2 g_r/dz_i dz_j| for all 70 rows. [IV]"""
    key = str(h)
    if key in _HMASS:
        return _HMASS[key]
    box = M.box_around(SL.z_hat(), h)
    rows = v3_rows()
    w = np.zeros(NEXT3)
    for k, r in enumerate(rows):
        j = SL.eval_geo(box, r, order=2)
        tot = 0.0
        for a in range(len(r['vars'])):
            for b in range(len(r['vars'])):
                tot += M.iv_mag(j.h[a][b])
        w[k] = tot
    _HMASS[key] = w
    return w


# --------------------------------------------------------------- the inner LP

_ACTIVE = None


def active_positions(tol=1e-40):
    """Extended positions whose row is ACTIVE at z-hat (|g| <= tol).

    Only active rows are usable in a barrier: a loaded row with g_r(z-hat) = 1
    would put eps_0 ~ 1 into E(h) and destroy the dichotomy.  Every axis has
    exactly two active corner rows (the tie pair of M1b sec. 7); L1.1 makes
    both valid on the branch simultaneously, with no menu.
    """
    global _ACTIVE
    if _ACTIVE is not None:
        return list(_ACTIVE)
    pb = SL.point_box()
    rows = v3_rows()
    out = [k for k in range(NEXT3)
           if M.iv_mag(SL.eval_geo(pb, rows[k], order=0).v) < tol]
    _ACTIVE = out
    return list(out)


def omega_lp_eff(V, P, h, cvec, w=None, beta=0.0, cap=200.0,
                 only_active=True, branch_floor=0.0):
    """[LP] The L2(a) inner LP in the MAX-FORM.

    Variables (u in R^{|F|}, t).  omega = omp + N^T u, so A^T omega = e_s holds
    identically.  Constraints:
        omega_r >= 0            for r in R_V (validity/sign discipline)
        omega_r = 0             for r outside R_V or inactive at z-hat
        omega_r >= c_r t        for r in P    (=> kappa_eff <= 1/t)
    Objective:
        maximise  t - (h/(1-beta)) * (1/2) sum_{r} w_r omega_r
                = 1/kappa_eff - h*Hbar_bound/(1-beta).
    A strictly positive optimum certifies (with the triangle bound
    Hbar <= (1/2) sum_r w_r omega_r) that psi(h) < h, i.e. that h is reached.
    The TRUE Hbar (with interval cancellation) is smaller, so the [IV]
    certificate is evaluated afterwards and is the thing that is certified;
    this LP is a design heuristic only.
    """
    Sx, F, N, omp = kernel_param(P)
    RV = set(variant_rows(V))
    if only_active:
        RV &= set(active_positions())
    RV |= set(P)
    dead = [k for k in range(NEXT3) if k not in RV]
    fpos = {k: i for i, k in enumerate(F)}
    assert all(k in fpos for k in dead), 'dead row inside the pin basis'
    nf = len(F)
    if w is None:
        w = row_hessian_mass(h)
    Aub, bub = [], []
    for r in sorted(RV):
        row = np.zeros(nf + 1)
        row[:nf] = -N[:, r]
        Aub.append(row)
        bub.append(omp[r])
        row = np.zeros(nf + 1)
        row[:nf] = N[:, r]
        Aub.append(row)
        bub.append(cap - omp[r])
    for r in P:
        row = np.zeros(nf + 1)
        row[:nf] = -N[:, r]
        row[nf] = float(cvec[list(P).index(r)]) if not isinstance(cvec, dict) \
            else float(cvec[r])
        Aub.append(row)
        bub.append(omp[r])
    if branch_floor > 0.0:
        act = set(active_positions())
        for ax in V:
            for r in axis_rows(ax):
                if r not in act:
                    continue
                row = np.zeros(nf + 1)
                row[:nf] = -N[:, r]
                Aub.append(row)
                bub.append(omp[r] - branch_floor)
    hh = float(h) / (1.0 - beta)
    c = np.zeros(nf + 1)
    c[nf] = -1.0
    for r in sorted(RV):
        c[:nf] += 0.5 * hh * w[r] * N[:, r]
    const = sum(0.5 * hh * w[r] * omp[r] for r in sorted(RV))
    bounds = [(None, None)] * nf + [(0.0, cap)]
    for k in dead:
        bounds[fpos[k]] = (-omp[k], -omp[k])
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=bounds,
                  method='highs')
    if not res.success:
        return None, None
    om = omp + N.T @ np.array(res.x[:nf])
    for k in dead:
        om[k] = 0.0
    return om, float(-res.fun - const)


def omega_lp(V, P, h, w=None, kappa_over=None, mode='reach', cap=200.0):
    """[LP] Inner LP over omega for variant V, pin set P, radius h.

    mode 'reach' : maximise  t = alpha - C(h) * (1/2) sum_r w_r omega_r  with
                   C(h) = kappa h/(1-beta), i.e. the SLACK in the (upper-bound
                   form of the) reach condition  kappa Hbar h^2/(alpha(1-beta)) < h.
                   Feasible with t > 0  =>  h is reached with the triangle
                   bound Hbar <= (1/2) sum w_r |omega_r|.
    mode 'maxfloor' : maximise alpha alone (ignores Hbar).
    mode 'minH'     : minimise (1/2) sum w_r omega_r at a fixed alpha floor.

    Returns (omega float (70,), alpha) or (None, None).
    """
    Sx, F, N, omp = kernel_param(P)
    RV = set(variant_rows(V))
    dead = [k for k in range(NEXT3) if k not in RV]
    fpos = {k: i for i, k in enumerate(F)}
    assert all(k in fpos for k in dead), 'dead row inside the pin basis'
    nf = len(F)
    if w is None:
        w = row_hessian_mass(h)
    Aub, bub = [], []
    # nonnegativity on every valid row:  -N u <= omp
    for r in sorted(RV):
        row = np.zeros(nf + 1)
        row[:nf] = -N[:, r]
        Aub.append(row)
        bub.append(omp[r])
    # |omega_r| <= cap  (keeps the LP bounded)
    for r in sorted(RV):
        row = np.zeros(nf + 1)
        row[:nf] = N[:, r]
        Aub.append(row)
        bub.append(cap - omp[r])
    if mode == 'maxfloor':
        c = np.zeros(nf + 1)
        c[-1] = -1.0
        for r in P:
            row = np.zeros(nf + 1)
            row[:nf] = -N[:, r]
            row[nf] = 1.0
            Aub.append(row)
            bub.append(omp[r])
        bounds = [(None, None)] * nf + [(None, cap)]
    elif mode == 'reach':
        # variables [u (nf), t]; alpha_r := omp_r + (N^T u)_r  for r in P
        # constraint:  t <= omega_r - C*(1/2) sum_s w_s omega_s   for r in P
        C = kappa_over * float(h)
        hess = np.zeros(nf)
        base = 0.0
        for s in sorted(RV):
            hess += 0.5 * C * w[s] * N[:, s]
            base += 0.5 * C * w[s] * omp[s]
        for r in P:
            row = np.zeros(nf + 1)
            row[:nf] = -N[:, r] + hess
            row[nf] = 1.0
            Aub.append(row)
            bub.append(omp[r] - base)
        c = np.zeros(nf + 1)
        c[-1] = -1.0
        bounds = [(None, None)] * nf + [(None, cap)]
    else:                                    # minH at a fixed floor
        c = np.zeros(nf + 1)
        for s in sorted(RV):
            c[:nf] += 0.5 * w[s] * N[:, s]
        for r in P:
            row = np.zeros(nf + 1)
            row[:nf] = -N[:, r]
            Aub.append(row)
            bub.append(omp[r] - float(kappa_over))
        bounds = [(None, None)] * nf + [(0.0, 0.0)]
    for k in dead:
        bounds[fpos[k]] = (-omp[k], -omp[k])
    res = linprog(c, A_ub=np.array(Aub), b_ub=np.array(bub), bounds=bounds,
                  method='highs')
    if not res.success:
        return None, None
    om = omp + N.T @ np.array(res.x[:nf])
    om[[k for k in dead]] = 0.0
    return om, float(min(om[r] for r in P))


OMEGA_F_DEN = 10 ** 12
OMEGA_S_DEN = 10 ** 45


def rationalise_omega(P, om_float):
    """Free part rounded at 1e12; pin part re-solved at dps 90 so that
    A_P^T omega_P = e_s - A_F^T omega_F, then rounded at 1e45."""
    Sx, F, _, _ = kernel_param(P)
    wf = [Fraction(round(Fraction(float(om_float[k])) * OMEGA_F_DEN),
                   OMEGA_F_DEN) for k in F]
    old, old_iv = mp.dps, iv.dps
    mp.dps = 90
    iv.dps = 90
    try:
        A = v3_jacobian_mp(dps=90)
        AS = mp.zeros(NV, NV)
        for c, k in enumerate(Sx):
            for j in range(NV):
                AS[j, c] = A[k, j]
        rhs = mp.zeros(NV, 1)
        rhs[S_IDX] = mp.mpf(1)
        for c, k in enumerate(F):
            wk = mp.mpf(wf[c].numerator) / mp.mpf(wf[c].denominator)
            for j in range(NV):
                rhs[j] -= A[k, j] * wk
        ws = mp.lu_solve(AS, rhs)
    finally:
        mp.dps = old
        iv.dps = old_iv
    om = [Fraction(0)] * NEXT3
    for c, k in enumerate(F):
        om[k] = wf[c]
    for c, k in enumerate(Sx):
        om[k] = Fraction(round(Fraction(str(mp.nstr(ws[c], 60)))
                               * OMEGA_S_DEN), OMEGA_S_DEN)
    return om


# ---------------------------------------------------------- pin bases / Y

def make_Y(P, den=10 ** 18):
    """Rational preconditioner Y = rat(inv(A_P)) for pin set P."""
    mid, _ = v3_jacobian()
    Yf = np.linalg.inv(mid[list(P)])
    return [[Fraction(round(Fraction(float(v)) * den), den) for v in row]
            for row in Yf]


def a22_Y_v3():
    """A22's own Y, rows in the order of S_EXT (= A22's S)."""
    return M.a22_Y()


def krawczyk_beta_kappa(P, Y, h):
    """[IV] beta = ||I - Y A_P(box(h))||_inf and kappa = ||Y||_inf."""
    box = M.box_around(SL.z_hat(), h)
    rows = v3_rows()
    grads = []
    for k in P:
        j = SL.eval_geo(box, rows[k], order=1)
        grads.append({gi: j.g[loc] for loc, gi in enumerate(rows[k]['vars'])})
    Yiv = [[t3lib._to_iv(v) for v in row] for row in Y]
    beta = 0.0
    for i in range(NV):
        rs = iv.mpf(0)
        for j2 in range(NV):
            ssum = iv.mpf(0)
            for rr in range(NV):
                v = grads[rr].get(j2)
                if v is not None:
                    ssum = ssum + Yiv[i][rr] * v
            rs = rs + abs((iv.mpf(1) if i == j2 else iv.mpf(0)) - ssum)
        beta = max(beta, M.iv_mag(rs))
    kappa = max(sum(abs(float(Y[i][r])) for r in range(NV)) for i in range(NV))
    return beta, kappa


# ------------------------------------------------------- (V') certificate [IV]

def vprime_constants(om, h):
    """[IV] (eps_0, eps_w, Hbar, Hinf) for W = sum om_r g_r on box(z-hat,h)."""
    rows = v3_rows()
    pbox = SL.point_box()
    e0 = 0.0
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        e0 += abs(float(om[k])) * M.iv_mag(SL.eval_geo(pbox, rows[k],
                                                       order=0).v)
    acc = [iv.mpf(0)] * NV
    for k in range(NEXT3):
        if om[k] == 0:
            continue
        ok = t3lib._to_iv(om[k])
        j = SL.eval_geo(pbox, rows[k], order=1)
        for loc, gi in enumerate(rows[k]['vars']):
            acc[gi] = acc[gi] + ok * j.g[loc]
    ew = sum(M.iv_mag(acc[gi] - (iv.mpf(1) if gi == S_IDX else iv.mpf(0)))
             for gi in range(NV))
    box = M.box_around(SL.z_hat(), h)
    accH = {}
    for k in range(NEXT3):
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
    return e0, ew, float(Hm.sum()) / 2.0, float(np.max(np.sum(Hm, axis=1)))


def vprime_certificate(om, h, P, Y, beta=None, kappa=None, consts=None):
    """Full [IV] evaluation of the (V') dichotomy at radius h (max-form)."""
    e0, ew, Hbar, Hinf = vprime_constants(om, h) if consts is None else consts
    if beta is None:
        beta, kappa = krawczyk_beta_kappa(P, Y, h)
    hf = float(h)
    gmax = M.g_max_at_zhat()
    cvec = [max(abs(float(Y[i][r])) for i in range(NV)) for r in range(NV)]
    omP = [float(om[r]) for r in P]
    alpha = min(omP)
    out = dict(eps_0=e0, eps_w=ew, Hbar=Hbar, Hinf=Hinf, beta=beta,
               kappa=kappa, g_max=gmax, alpha_min=alpha, h=M.fs(h),
               h_float=hf, omega_l1=float(sum(abs(float(x)) for x in om)))
    if beta >= 1.0 or alpha <= 0:
        out.update(ok=False, reason='beta >= 1 or alpha <= 0')
        return out
    keff = max(cvec[i] / omP[i] for i in range(NV))
    E = e0 + ew * hf + Hbar * hf * hf
    psi = (keff * E + kappa * gmax) / (1.0 - beta)
    psi_a35 = kappa * (E / alpha + gmax) / (1.0 - beta)
    C = keff / (1.0 - beta)
    x = hf
    for _ in range(800):
        x = C * (e0 + ew * x + Hbar * x * x) + kappa * gmax / (1.0 - beta)
    out.update(ok=bool(psi < hf and x <= float(R_N)), kappa_eff=keff,
               kappa_over_alpha=kappa / alpha, E=E, psi=psi,
               psi_over_h=psi / hf, psi_A35form=psi_a35, x_star=x,
               r_N=float(R_N))
    return out
