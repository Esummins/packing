"""strata_lib.py -- A35 escape-complex: shared machinery for M1/M2/M3/M4.

Everything is built on the A22 certificate (results/krawczyk_cert.json):

  * z-hat : 34 EXACT rationals (Fractions), layout z[3i]=cx_i, z[3i+1]=cy_i,
            z[3i+2]=theta_i (i = 0..10), z[33] = s.
  * the 38 GEOMETRIC rows = constraints[0..37] (20 wall + 16 edge + 2 dist),
            all written g_k >= 0 and all g_k(z-hat) = 0 (to ~1e-55).
            The 4 'angeq' rows 38..41 are A22 surrogates and are NOT used.

Row evaluation reuses A30's t3lib (interval jets, mpmath.iv) via sys.path:
  * wall rows  -> t3lib.wall_row(i, corner, wall)
  * edge rows  -> t3lib.sep_row(o=j, e=edge, p=i, kstar=corner)
        (A22's 'edge' row is  n_e(theta_j) . (q_corner(i) - c_j) - 1/2 >= 0,
         which is exactly t3lib's separation row with OWNER j.)
  * dist rows  -> not in t3lib's language; a 4-variable jet is built here with
        t3lib.Jet (|c_i - c_j|^2 - 1 >= 0).

RIGOUR CONVENTIONS (used verbatim in the report):
  [IV]   mpmath.iv at dps 60 over the DEGENERATE point box at z-hat (z-hat is
         rational, so the only interval width comes from cos/sin enclosures;
         widths are ~1e-58).  Rigorous.
  [RFP]  rigorous float64: Rump-style preconditioned nonsingularity test
         ||I - Y*A||_inf < 1 with an explicit rounding-error bound and the
         [IV] entry radii folded in.  Rigorous (modulo IEEE-754 semantics).
  [NUM]  float64 SVD with an explicit spectral gap reported.  NOT rigorous:
         a rank DEFICIENCY claim is never interval-certifiable at a rational
         approximation of an algebraic point.  Rank-34 (dof 0 / "empty")
         claims ARE certified, by [RFP]; rank-drop claims are [NUM].
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from fractions import Fraction

import numpy as np
from mpmath import iv, mp

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPTS = os.path.abspath(os.path.join(HERE, '..', '..'))
A30 = os.path.join(ATTEMPTS, 'A30-t3-pilot')
A22 = os.path.join(ATTEMPTS, 'A22-local-rigidity')
if A30 not in sys.path:
    sys.path.insert(0, A30)

if A22 not in sys.path:
    sys.path.insert(0, A22)

import t3lib  # noqa: E402  (row language + interval jets)
import a22lib  # noqa: E402  (point-arithmetic gradients, same conventions)

IV_DPS = 60
iv.dps = IV_DPS
mp.dps = 60

NV = 34
NSQ = 11
NGEO = 38          # geometric rows = cert constraints 0..37
S_IDX = 33         # index of the container side s
WALLS = ('x=0', 'y=0', 'x=s', 'y=s')


# --------------------------------------------------------------- cert loading

_CERT = None


def load_cert():
    """The A22 krawczyk certificate (dict)."""
    global _CERT
    if _CERT is None:
        with open(os.path.join(A22, 'results', 'krawczyk_cert.json')) as f:
            _CERT = json.load(f)
    return _CERT


def str_frac(s):
    n, d = s.split('/')
    return Fraction(int(n), int(d))


def z_hat():
    """z-hat as 34 exact Fractions."""
    return [str_frac(s) for s in load_cert()['z0']]


def geo_constraints():
    """The 38 geometric constraint dicts, verbatim from the certificate."""
    return load_cert()['constraints'][:NGEO]


# ------------------------------------------------------------------ row language

def dist_row(i, j):
    return {'kind': 'dist', 'i': i, 'j': j,
            'vars': (3 * i, 3 * i + 1, 3 * j, 3 * j + 1)}


def to_t3_row(c):
    """A22 constraint dict -> t3lib-style row dict (adds 'dist')."""
    if c['kind'] == 'wall':
        return t3lib.wall_row(c['i'], c['corner'], c['wall'])
    if c['kind'] == 'edge':
        # corner c['corner'] of square c['i'] against edge c['edge'] of c['j']
        return t3lib.sep_row(c['j'], c['edge'], c['i'], c['corner'])
    if c['kind'] == 'dist':
        return dist_row(c['i'], c['j'])
    raise ValueError(c['kind'])


def geo_rows():
    """The 38 geometric rows in t3lib language, in certificate order."""
    return [to_t3_row(c) for c in geo_constraints()]


def row_names():
    return [c['name'] for c in geo_constraints()]


# ------------------------------------------------------------- BASIS v2
# M4 (results/m4_report.md sec. 4-5) exposed two defects in the A22 row basis:
#  (a) rows 36, 37 (D0-1, D0-3) are CENTRE-DISTANCE surrogates.  |c_i-c_j|^2-1
#      is a valid inequality (incircle argument) but holding it at 0 does not
#      pin the flush contacts of pairs (0,1) and (0,3): the squares can rotate
#      into each other while the row still reads 0.  Verified here: centre
#      dist^2 = 1 EXACTLY for both pairs, and both are genuine FLUSH contacts.
#  (b) pair (1,3) touches CORNER-TO-CORNER at (1,1) -- verified exactly:
#      sq1 corner 3 = sq3 corner 1 = (1,1), centre dist^2 = 2 EXACTLY (so no
#      dist row could ever be active there), SAT gap 0 within +-4.7e-61.
#      It is a 14th contact pair and is absent from the 38 v1 rows.
#
# BASIS v2 = rows 0..35 verbatim + 4 proper flush sep rows (2 per flush pair,
# one per owner, following A22's own convention for the tilted flush pairs such
# as (6,9) = rows 24/32) + the 2 orthogonal separation branches of the (1,3)
# corner-corner contact.  42 rows.
#
# SEMANTIC WARNING (drain_lemma D3', theory.md G5), carried into every v2
# result: the two (1,3) branches are MENU ALTERNATIVES, not conjunctive
# constraints.  The true SAT gap of a corner-corner pair is the MAX over the
# branches, so "contact maintained" = the SELECTED branch = 0 and "broken" =
# max over branches > 0.  For the CONE / FJ analysis treating both branches as
# separate rows with independent lambda >= 0 is exactly right (the Clarke
# subdifferential of a max is the convex hull of the branch gradients, and
# cone(conv{a,b}) = cone{a,b}).  For the RANK / dof analysis it is NOT: holding
# both at 0 over-constrains the stratum.  m1b_enum.py therefore runs the
# stratum enumeration in three variants -- 'conj' (both branches maintained),
# 'selx' (only the x-branch is a row) and 'sely' (only the y-branch) -- and
# reports all three.
#
# The four flush selections are also TIED at z-hat (both candidate corners of
# each edge have dominance margin 0 to within 1e-61), and the two tied corners
# give DIFFERENT gradients in theta.  The chosen selection is recorded per row
# and the alternative is available as V2_FLUSH_TIE_ALTERNATIVES.

V2_NEW_ROWS = [
    {'kind': 'edge', 'i': 1, 'corner': 3, 'j': 0, 'edge': 1, 'name': 'F0-1a',
     'role': 'flush (0,1), owner 0 right edge vs corner 3 of sq1',
     'replaces': 'v1 row 36 (D0-1)'},
    {'kind': 'edge', 'i': 0, 'corner': 2, 'j': 1, 'edge': 3, 'name': 'F0-1b',
     'role': 'flush (0,1), owner 1 left edge vs corner 2 of sq0',
     'replaces': 'v1 row 36 (D0-1)'},
    {'kind': 'edge', 'i': 3, 'corner': 0, 'j': 0, 'edge': 2, 'name': 'F0-3a',
     'role': 'flush (0,3), owner 0 top edge vs corner 0 of sq3',
     'replaces': 'v1 row 37 (D0-3)'},
    {'kind': 'edge', 'i': 0, 'corner': 3, 'j': 3, 'edge': 0, 'name': 'F0-3b',
     'role': 'flush (0,3), owner 3 bottom edge vs corner 3 of sq0',
     'replaces': 'v1 row 37 (D0-3)'},
    {'kind': 'edge', 'i': 3, 'corner': 1, 'j': 1, 'edge': 3, 'name': 'C1-3x',
     'role': 'corner-corner (1,3), X-BRANCH (owner 1 left edge)',
     'replaces': 'NEW -- absent from v1'},
    {'kind': 'edge', 'i': 1, 'corner': 3, 'j': 3, 'edge': 0, 'name': 'C1-3y',
     'role': 'corner-corner (1,3), Y-BRANCH (owner 3 bottom edge)',
     'replaces': 'NEW -- absent from v1'},
]

# the tied alternative corner for each flush/corner row (same owner+edge)
V2_FLUSH_TIE_ALTERNATIVES = {
    'F0-1a': {'corner': 0}, 'F0-1b': {'corner': 1},
    'F0-3a': {'corner': 1}, 'F0-3b': {'corner': 2},
    'C1-3x': {'corner': 2}, 'C1-3y': {'corner': 2},
}

NGEO_V2 = 42
V2_BRANCH_X = 40          # index of C1-3x in the v2 row list
V2_BRANCH_Y = 41          # index of C1-3y
V2_DROPPED_V1_ROWS = (36, 37)


def geo_constraints_v2():
    """The 42 v2 geometric constraint dicts (A22 language)."""
    return load_cert()['constraints'][:36] + [dict(r) for r in V2_NEW_ROWS]


def geo_rows_v2():
    return [to_t3_row(c) for c in geo_constraints_v2()]


def row_names_v2():
    return [c['name'] for c in geo_constraints_v2()]


def v2_variant_rows(variant='conj'):
    """Row INDEX list for a (1,3) branch-selection variant.

    'conj' -> all 42 rows; 'selx' -> drop the y-branch; 'sely' -> drop x.
    """
    if variant == 'conj':
        return list(range(NGEO_V2))
    if variant == 'selx':
        return [k for k in range(NGEO_V2) if k != V2_BRANCH_Y]
    if variant == 'sely':
        return [k for k in range(NGEO_V2) if k != V2_BRANCH_X]
    raise ValueError(variant)


_JAC_V2 = None


def jacobian_v2(box=None):
    """(A_iv, mid, rad, values_iv) for the 42-row v2 basis at z-hat."""
    global _JAC_V2
    if box is None and _JAC_V2 is not None:
        return _JAC_V2
    rows = geo_rows_v2()
    A_iv, vals = jacobian_iv(box, rows)
    n = len(rows)
    mid = np.zeros((n, NV))
    rad = np.zeros((n, NV))
    for k in range(n):
        for j in range(NV):
            m, r = _iv_mid_rad(A_iv[k][j])
            mid[k, j] = m
            rad[k, j] = r
    out = (A_iv, mid, rad, vals)
    if box is None:
        _JAC_V2 = out
    return out


_JAC_MP_V2 = {}


def jacobian_mp_v2(dps=90, z=None):
    if z is None and dps in _JAC_MP_V2:
        return _JAC_MP_V2[dps]
    old = mp.dps
    mp.dps = dps
    try:
        zz = z_hat() if z is None else z
        zm = [a22lib.cnum(mp, x) for x in zz]
        cons = geo_constraints_v2()
        A = mp.zeros(len(cons), NV)
        for k, c in enumerate(cons):
            for gi, v in a22lib.grad_g(mp, zm, c).items():
                A[k, gi] = v
    finally:
        mp.dps = old
    if z is None:
        _JAC_MP_V2[dps] = A
    return A


def contact_edges_v2():
    """The 25 distinct v2 contact EDGES (24 of v1 with (0,1),(0,3) re-rowed,
    plus the (1,3) corner-corner edge)."""
    cons = geo_constraints_v2()
    seen, order = {}, []
    for k, c in enumerate(cons):
        if c['kind'] == 'wall':
            key = ('W', c['i'], c['wall'])
        else:
            key = ('P',) + tuple(sorted((c['i'], c['j'])))
        if key not in seen:
            seen[key] = {'id': len(order), 'rows': []}
            order.append(key)
        seen[key]['rows'].append(k)
    out = []
    for key in order:
        d = seen[key]
        if key[0] == 'W':
            out.append({'id': d['id'], 'type': 'wall', 'a': key[1],
                        'b': key[2], 'wall': key[2], 'rows': d['rows']})
        else:
            out.append({'id': d['id'], 'type': 'pair', 'a': key[1],
                        'b': key[2], 'rows': d['rows']})
    return out


def eval_geo(box, r, order=1):
    """Interval jet of a geometric row (t3lib conventions + 'dist')."""
    if r['kind'] != 'dist':
        return t3lib.eval_row(box, r, order=order)
    vs = r['vars']
    d = len(vs)
    V = [t3lib.Jet.var(box[gi], k, d, order) for k, gi in enumerate(vs)]
    dx = V[0] - V[2]
    dy = V[1] - V[3]
    return (dx * dx + dy * dy) - iv.mpf(1)


def row_grad_geo(box, r):
    j = eval_geo(box, r, order=1)
    return j.v, {gi: j.g[k] for k, gi in enumerate(r['vars'])}


def point_box(z=None):
    """Degenerate interval box at z-hat (exact rationals -> tight ivs)."""
    if z is None:
        z = z_hat()
    return [t3lib._to_iv(x) for x in z]


def frac_box(z, r):
    """box(z, r) with rational centre and rational radius (scalar or list)."""
    return t3lib.box_from(z, r)


# ------------------------------------------------------------------ Jacobian

_JAC = None


def jacobian_iv(box=None, rows=None):
    """38 x 34 interval Jacobian; also returns interval row VALUES."""
    if box is None:
        box = point_box()
    if rows is None:
        rows = geo_rows()
    A = [[iv.mpf(0)] * NV for _ in rows]
    vals = []
    for k, r in enumerate(rows):
        j = eval_geo(box, r, order=1)
        vals.append(j.v)
        for loc, gi in enumerate(r['vars']):
            A[k][gi] = j.g[loc]
    return A, vals


def _iv_mid_rad(x):
    a, b = mp.mpf(x.a), mp.mpf(x.b)
    m = float((a + b) / 2)
    rad = float(max(abs(b - mp.mpf(m)), abs(mp.mpf(m) - a)))
    rad = rad * (1 + 1e-12) + 5e-324
    return m, rad


def jacobian(box=None):
    """Cached (A_iv, A_mid float64, A_rad float64, values_iv) at z-hat."""
    global _JAC
    if box is None and _JAC is not None:
        return _JAC
    A_iv, vals = jacobian_iv(box)
    mid = np.zeros((NGEO, NV))
    rad = np.zeros((NGEO, NV))
    for k in range(NGEO):
        for j in range(NV):
            m, r = _iv_mid_rad(A_iv[k][j])
            mid[k, j] = m
            rad[k, j] = r
    out = (A_iv, mid, rad, vals)
    if box is None:
        _JAC = out
    return out


_JAC_MP = {}


def jacobian_mp(dps=90, z=None):
    """38 x 34 Jacobian as an mpmath.mp matrix at the requested precision.

    Uses a22lib.grad_g (point arithmetic, IDENTICAL row conventions to the
    interval jets); consistency with the [IV] Jacobian is asserted by
    check_jacobian_consistency().
    """
    if z is None and dps in _JAC_MP:
        return _JAC_MP[dps]
    old = mp.dps
    mp.dps = dps
    try:
        zz = z_hat() if z is None else z
        zm = [a22lib.cnum(mp, x) for x in zz]
        A = mp.zeros(NGEO, NV)
        for k, c in enumerate(geo_constraints()):
            for gi, v in a22lib.grad_g(mp, zm, c).items():
                A[k, gi] = v
    finally:
        mp.dps = old
    if z is None:
        _JAC_MP[dps] = A
    return A


def check_jacobian_consistency():
    """Every a22lib point gradient must lie inside the t3lib interval jet."""
    A_iv, _, _, _ = jacobian()
    Amp = jacobian_mp(dps=60)
    bad = []
    for k in range(NGEO):
        for j in range(NV):
            v = Amp[k, j]
            b = A_iv[k][j]
            if not (mp.mpf(b.a) <= v <= mp.mpf(b.b)):
                bad.append((k, j, float(v), float(b.a), float(b.b)))
    return bad


# ------------------------------------------- rigorous nonsingularity  [RFP]

def certify_nonsingular(Amid, Arad=None):
    """Rigorous float64 nonsingularity test for the interval matrix
    [Amid - Arad, Amid + Arad] (square).

    Uses Y = fl(inv(Amid)) as preconditioner and the standard backward bound
        |fl(Y*A) - Y*A| <= gamma_{n+2} * (|Y| * |A|),  gamma_k = k*eps/(1-k*eps)
    so that   ||I - Y*A_true||_inf <= max_i sum_j (|E_ij| + err_ij).
    If that is < 1 then Y*A_true is nonsingular, hence A_true is.
    Returns (certified: bool, bound: float).
    """
    n = Amid.shape[0]
    assert Amid.shape[1] == n
    if Arad is None:
        Arad = np.zeros_like(Amid)
    try:
        Y = np.linalg.inv(Amid)
    except np.linalg.LinAlgError:
        return False, float('inf')
    if not np.all(np.isfinite(Y)):
        return False, float('inf')
    E = np.eye(n) - Y @ Amid
    eps = float(np.finfo(float).eps) / 2.0     # unit roundoff
    k = n + 2
    gamma = k * eps / (1.0 - k * eps)
    aY = np.abs(Y)
    err = gamma * (aY @ np.abs(Amid)) + aY @ Arad
    bound = float(np.max(np.sum(np.abs(E) + err, axis=1)))
    return bool(bound < 1.0), bound


_BASIS_CACHE = {}


def certified_rank34(M, Amid=None, Arad=None):
    """Try to CERTIFY rank(A_M) = 34 by exhibiting a nonsingular 34-row minor.

    Returns (True, basis tuple, bound) or (False, None, bound).
    """
    if Amid is None:
        _, Amid, Arad, _ = jacobian()
    M = list(M)
    if len(M) < NV:
        return False, None, float('inf')
    sub = Amid[M]
    # pick 34 independent rows by column-pivoted QR of sub^T
    from scipy.linalg import qr
    _, _, piv = qr(sub.T, pivoting=True, mode='economic')
    basis = tuple(sorted(M[p] for p in piv[:NV]))
    if basis in _BASIS_CACHE:
        ok, bound = _BASIS_CACHE[basis]
        return (ok, basis if ok else None, bound)
    ok, bound = certify_nonsingular(Amid[list(basis)], Arad[list(basis)])
    _BASIS_CACHE[basis] = (ok, bound)
    return (ok, basis if ok else None, bound)


def basis_cache():
    return dict(_BASIS_CACHE)


# ---------------------------------------------------------- rank / dof  [NUM]

RANK_TOL = 1e-9


def rank_gap(M, Amid=None, tol=RANK_TOL):
    """(numerical rank, singular values) of A_M via float64 SVD."""
    if Amid is None:
        _, Amid, _, _ = jacobian()
    sub = Amid[list(M)]
    sv = np.linalg.svd(sub, compute_uv=False)
    r = int((sv > tol).sum())
    return r, sv


def stratum(B, Amid=None, want_kernel=False, tol=RANK_TOL):
    """Analyse the closed stratum with broken set B.

    Returns dict: B, M, rank, dof, sv_gap (last kept / first dropped),
    kernel (list of dof unit vectors, float) if want_kernel.
    """
    if Amid is None:
        _, Amid, _, _ = jacobian()
    B = tuple(sorted(B))
    M = [k for k in range(NGEO) if k not in set(B)]
    sub = Amid[M]
    U, sv, Vt = np.linalg.svd(sub)
    r = int((sv > tol).sum())
    dof = NV - r
    small = sv[r] if r < len(sv) else 0.0
    big = sv[r - 1] if r > 0 else float('inf')
    out = {'B': list(B), 'rank': r, 'dof': int(dof),
           'sv_min_kept': float(big), 'sv_max_dropped': float(small)}
    if want_kernel and dof > 0:
        out['kernel'] = Vt[r:].tolist()
    elif want_kernel:
        out['kernel'] = []
    return out


def kernel_basis(B, Amid=None, tol=RANK_TOL):
    """Orthonormal basis (rows) of ker(A_M), M = complement of B."""
    if Amid is None:
        _, Amid, _, _ = jacobian()
    M = [k for k in range(NGEO) if k not in set(B)]
    _, sv, Vt = np.linalg.svd(Amid[M])
    r = int((sv > tol).sum())
    return Vt[r:]


# ------------------------------------------------------------ contact graph

def contact_edges():
    """The 24 distinct contact EDGES with their row lists.

    Returns list of dicts: {'id', 'type': 'wall'|'pair', 'a', 'b', 'rows',
                            'wall' (for wall edges)}
    'a','b' are node labels: int = square index, str = wall node.
    """
    cons = geo_constraints()
    seen = {}
    order = []
    for k, c in enumerate(cons):
        if c['kind'] == 'wall':
            key = ('W', c['i'], c['wall'])
        elif c['kind'] == 'edge':
            key = ('P',) + tuple(sorted((c['i'], c['j'])))
        else:
            key = ('P',) + tuple(sorted((c['i'], c['j'])))
        if key not in seen:
            seen[key] = {'id': len(order), 'rows': []}
            order.append(key)
        seen[key]['rows'].append(k)
    out = []
    for key in order:
        d = seen[key]
        if key[0] == 'W':
            out.append({'id': d['id'], 'type': 'wall', 'a': key[1],
                        'b': key[2], 'wall': key[2], 'rows': d['rows']})
        else:
            out.append({'id': d['id'], 'type': 'pair', 'a': key[1],
                        'b': key[2], 'rows': d['rows']})
    return out


def rows_per_edge():
    return {e['id']: tuple(e['rows']) for e in contact_edges()}


def edge_of_row():
    m = {}
    for e in contact_edges():
        for k in e['rows']:
            m[k] = e['id']
    return m


# ------------------------------------------------------------------- SAT gaps

def sat_gap_pair(box, i, j):
    """Interval enclosure of the SAT separation of squares i and j."""
    return t3lib.pair_sep_iv(box, i, j)


def wall_gap(box, i, corner, wall):
    """Interval value of the corner-wall clearance row."""
    return t3lib.row_value(box, t3lib.wall_row(i, corner, wall))


def contact_wall_set():
    """{(square, corner, wall)} that are already contacts among the 38 rows."""
    out = set()
    for c in geo_constraints():
        if c['kind'] == 'wall':
            out.add((c['i'], c['corner'], c['wall']))
    return out


def contact_pairs():
    out = set()
    for c in geo_constraints():
        if c['kind'] in ('edge', 'dist'):
            out.add(tuple(sorted((c['i'], c['j']))))
    return out


# --------------------------------------------------------------- misc helpers

def es_vector():
    e = np.zeros(NV)
    e[S_IDX] = 1.0
    return e


def iv_dot(g, y):
    """interval dot of a sparse gradient dict with a list of 34 iv numbers."""
    acc = iv.mpf(0)
    for gi, val in g.items():
        acc = acc + val * y[gi]
    return acc


def to_iv_vec(fracs):
    return [t3lib._to_iv(x) for x in fracs]


def frac_str(x):
    return '%d/%d' % (x.numerator, x.denominator)


def rationalize(x, den):
    """Nearest rational with the given denominator."""
    return Fraction(round(Fraction(x) * den), den)
