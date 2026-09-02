"""A69 phase 3 (lean rewrite) -- assemble the (c-idl) certificate.

Pure Python fractions + interpolation; no sympy Expr anywhere near the big
objects.  Uses the CHECKER'S generators verbatim (imports certs/verify_cidl.py).

Memory discipline: every polynomial is a list of Fractions (univariate in t) or
a short list of such lists (S-power -> t-poly).  Coefficient bit-sizes stay in
the hundreds of bits; the whole computation fits in tens of MB.
"""
import os, sys, json
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'certs'))
import verify_cidl as VC

IT, IS = VC.IT, VC.IS
NVAR = VC.NVAR
XNAMES = ['y4', 'x6', 'y6', 'x7', 'y7', 'x8', 'y8', 'x9', 'y9', 'x10', 'y10', 'S']
XIDX = [VC.vidx(n) for n in XNAMES]

OCTIC = [F(c) for c in [-6865, 12420, -6754, -496, 1923, -842, 178, -20, 1]]
M_T = [F(c) for c in [-1, 2, 2, -6, 12, 14, -2, -10, 5]]  # m(t), low-to-high

# ---------------------------------------------------------------- univariate ops

def ustrip(p):
    while p and p[-1] == 0:
        p.pop()
    return p

def uadd(a, b):
    n = max(len(a), len(b))
    return ustrip([ (a[i] if i < len(a) else F(0)) + (b[i] if i < len(b) else F(0)) for i in range(n) ])

def uscale(a, c):
    return [] if c == 0 else [x * c for x in a]

def umul(a, b):
    if not a or not b:
        return []
    r = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[i + j] += x * y
    return ustrip(r)

def uval(a, x):
    r = F(0)
    for c in reversed(a):
        r = r * x + c
    return r

def udivmod(a, b):
    """exact polynomial division with remainder over Q."""
    r = list(a)
    q = [F(0)] * max(0, len(a) - len(b) + 1)
    db, lb = len(b) - 1, b[-1]
    while len(ustrip(r)) - 1 >= db and ustrip(r):
        r = ustrip(r)
        c = r[-1] / lb
        d = len(r) - 1 - db
        q[d] = c
        for i in range(len(b)):
            r[d + i] -= c * b[i]
        r.pop()
    return ustrip(q), ustrip(r)

def interp(points, vals):
    """Lagrange interpolation -> coefficient list (exact, Newton form)."""
    # Newton divided differences
    n = len(points)
    coef = list(vals)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (points[i] - points[i - j])
    # expand Newton form
    poly = [F(0)]
    basis = [F(1)]
    for i in range(n):
        poly = uadd(poly, uscale(basis, coef[i]))
        basis = umul(basis, [-points[i], F(1)])
    return ustrip(poly)

# ---------------------------------------------------------------- linear algebra

def mat_inv_det(Amat):
    """Rational 12x12: returns (inv, det) via Gauss-Jordan."""
    n = len(Amat)
    M = [row[:] + [F(1) if i == j else F(0) for j in range(n)] for i, row in enumerate(Amat)]
    det = F(1)
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        if piv is None:
            return None, F(0)
        if piv != col:
            M[col], M[piv] = M[piv], M[col]
            det = -det
        pv = M[col][col]
        det *= pv
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col]:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    inv = [row[n:] for row in M]
    return inv, det

# ---------------------------------------------------------------- build system

gens = VC.build_generators()
names = [n for n, _ in gens]
print('generators:', names)

def gen_linear(g):
    """Sparse 13-var dict (linear in x-vars) -> (coeff t-polys per x-var, const t-poly)."""
    coeffs = [dict() for _ in range(12)]  # t-power -> F
    const = {}
    for mon, c in g.items():
        tpow = mon[IT]
        xs = [(k, mon[k]) for k in range(NVAR) if k != IT and mon[k]]
        assert sum(e for _, e in xs) <= 1, (mon,)
        if xs:
            k = xs[0][0]
            ci = XIDX.index(k)
            coeffs[ci][tpow] = coeffs[ci].get(tpow, F(0)) + c
        else:
            const[tpow] = const.get(tpow, F(0)) + c
    def tod(dd):
        if not dd:
            return []
        p = [F(0)] * (max(dd) + 1)
        for k, v in dd.items():
            p[k] = v
        return ustrip(p)
    return [tod(d) for d in coeffs], tod(const)

ROWS = []   # (name, [12 t-polys], b_t_poly)  with row = sum coeff_i * x_i - b
for nme, g in gens:
    co, cst = gen_linear(g)
    ROWS.append((nme, co, uscale(cst, F(-1))))  # b = -const

LEAVE = 0  # E1c2-8e3, confirmed nonsingular by the first run
keep = [r for r in range(13) if r != LEAVE]
print('leave-out row:', names[LEAVE])

def A_of(tv):
    return [[uval(ROWS[r][1][c], tv) for c in range(12)] for r in keep]

def b_of(tv):
    return [uval(ROWS[r][2], tv) for r in keep]

iS = XNAMES.index('S')

# degrees bounds
DEG_ADJ = 60     # generous bound for adjugate entries / N_m / c_j / D
NPTS = DEG_ADJ + 1
pts = [F(k + 2, 1) for k in range(NPTS)]  # t = 2, 3, ...

print('evaluating adjugate row, N, c, D at %d points...' % NPTS)
Delta_v, adjS_v, N_v, c_v, D_v = [], [[] for _ in range(12)], [[] for _ in range(12)], [[] for _ in range(12)], []
a13pol = ROWS[LEAVE][1]
b13pol = ROWS[LEAVE][2]
for tv in pts:
    Am = A_of(tv)
    bm = b_of(tv)
    inv, det = mat_inv_det(Am)
    assert det != 0, tv
    Delta_v.append(det)
    # adj = det * inv ; row iS of adj: adj[iS][j] = det * inv[iS][j]
    for j in range(12):
        adjS_v[j].append(det * inv[iS][j])
    # N_m = (adj b)_m = det * (inv b)_m
    xv = [sum(inv[m][j] * bm[j] for j in range(12)) for m in range(12)]
    for m in range(12):
        N_v[m].append(det * xv[m])
    # c_j = sum_m a13_m adj[m][j] = det * (a13 . inv)_j
    a13v = [uval(a13pol[m], tv) for m in range(12)]
    u = [sum(a13v[m] * inv[m][j] for m in range(12)) for j in range(12)]
    for j in range(12):
        c_v[j].append(det * u[j])
    # D = a13 . N - det * b13
    D_v.append(sum(a13v[m] * det * xv[m] for m in range(12)) - det * uval(b13pol, tv))

print('interpolating...')
Delta = interp(pts, Delta_v)
adjS = [interp(pts, adjS_v[j]) for j in range(12)]
N = [interp(pts, N_v[m]) for m in range(12)]
cJ = [interp(pts, c_v[j]) for j in range(12)]
D = interp(pts, D_v)
print('deg Delta = %d, deg D = %d' % (len(Delta) - 1, len(D) - 1))
print('deg adjS =', [len(x) - 1 for x in adjS])

# verify interpolation degrees were not clipped: check at an extra point
textra = F(103, 7)
Am = A_of(textra); bm = b_of(textra)
inv, det = mat_inv_det(Am)
assert uval(Delta, textra) == det, 'Delta interpolation degree clipped'
xv = [sum(inv[m][j] * bm[j] for j in range(12)) for m in range(12)]
assert uval(N[iS], textra) == det * xv[iS], 'N_S interpolation clipped'
a13v = [uval(a13pol[m], textra) for m in range(12)]
assert uval(D, textra) == sum(a13v[m] * det * xv[m] for m in range(12)) - det * uval(b13pol, textra), 'D clipped'
for j in range(12):
    assert uval(adjS[j], textra) == det * inv[iS][j], 'adjS clipped'
    u_j = sum(a13v[m] * inv[m][j] for m in range(12))
    assert uval(cJ[j], textra) == det * u_j, 'cJ clipped'
print('interpolations verified at an extra point')

# m | D and m | G_oct
e, rem = udivmod(D, M_T)
assert not rem, 'm does not divide D'
print('deg e = %d' % (len(e) - 1))
_, rem2 = udivmod(e, M_T)
if not rem2:
    print('WARNING: m^2 | D')

# gcd(Delta, m) must be trivial (Delta(t-hat) != 0)
def ugcd(a, b):
    x, y = list(a), list(b)
    while y:
        x, y = y, udivmod(x, y)[1]
    return x
gcdDm = ugcd(Delta, M_T)
assert len(gcdDm) == 1, 'Delta shares a root with m!'
print('gcd(Delta, m) = 1: OK')
gcdem = ugcd(e, M_T)
assert len(gcdem) == 1, 'e shares a root with m!'
print('gcd(e, m) = 1: OK')

# G_oct = sum a_k N_S^k Delta^(8-k), univariate
NS = N[iS]
print('building G_oct...')
Dpow = [[F(1)]]
for _ in range(8):
    Dpow.append(umul(Dpow[-1], Delta))
Npow = [[F(1)]]
for _ in range(8):
    Npow.append(umul(Npow[-1], NS))
G_oct = []
for k in range(9):
    G_oct = uadd(G_oct, uscale(umul(Npow[k], Dpow[8 - k]), OCTIC[k]))
print('deg G_oct = %d' % (len(G_oct) - 1))
g_cof, rem3 = udivmod(G_oct, M_T)
assert not rem3, 'm does NOT divide G_oct -- no certificate on this slice'
print('m | G_oct: OK (deg g_cof = %d)' % (len(g_cof) - 1))

# Wtel coefficients: w_i(t) = sum_{k=i+1}^{8} a_k N_S^(k-1-i) Delta^(8-k+i), i = 0..7
print('building Wtel...')
W = []
for i in range(8):
    wi = []
    for k in range(i + 1, 9):
        wi = uadd(wi, uscale(umul(Npow[k - 1 - i], Dpow[8 - k + i]), OCTIC[k]))
    W.append(wi)

# cofactors q_j = e * Wtel * adjS_j - g_cof * c_j   (S-poly: list of t-polys),
# q_leave = g_cof * Delta  (S-degree 0)
print('building cofactors...')
Q = {}
for jj, r in enumerate(keep):
    ew = umul(e, adjS[jj])
    qj = [umul(ew, W[i]) for i in range(8)]           # S^i parts
    qj[0] = uadd(qj[0], uscale(umul(g_cof, cJ[jj]), F(-1)))
    Q[names[r]] = qj
Q[names[LEAVE]] = [umul(g_cof, Delta)]

# ---------------------------------------------------------------- identity check
print('verifying identity with the checker machinery...')
def biv_to_sparse(qj):
    r = {}
    for spow, tp in enumerate(qj):
        for tpow, c in enumerate(tp):
            if c:
                ee = [0] * NVAR
                ee[IT] = tpow
                ee[IS] = spow
                r[tuple(ee)] = c
    return r

lhs = {}
for nme, g in gens:
    lhs = VC.padd(lhs, VC.pmul(biv_to_sparse(Q[nme]), g))

rhs_t = umul(e, Dpow[8])
rhs = {}
for spow, c_s in enumerate(OCTIC):
    if c_s:
        for tpow, c in enumerate(rhs_t):
            if c:
                ee = [0] * NVAR
                ee[IT] = tpow
                ee[IS] = spow
                rhs[tuple(ee)] = c * c_s
diff = VC.padd(lhs, {m: -c for m, c in rhs.items()})
assert not diff, 'identity FAILED: %d residual monomials' % len(diff)
print('IDENTITY HOLDS (exact, all 13 generators).')

# ---------------------------------------------------------------- serialize
def upoly_ser(p):
    return [str(x) for x in p] if p else ['0']

cert = {
    'format': 'cidl-membership-v1',
    'description': ('Saturated ideal-membership certificate closing the identity '
                    's-hat_A22 = s-hat_octic (TopLevel.lean axiom shatA22_eq_shat): '
                    'e(t)*Delta(t)^8*octic(S) = sum_j q_j(t,S)*G_j over the 13 reduced '
                    'A22 contact rows on the certified exact-structure slice '
                    '(A22 notes.md headline item 2). Checker: certs/verify_cidl.py '
                    '(rebuilds the G_j itself from the A22 conventions).'),
    'octic': {'variable': 'S', 'coefficients_low_to_high': [str(x) for x in OCTIC]},
    'gate_interval': {'a': '3/10', 'b': '2/5'},
    'e': {'coefficients_low_to_high': upoly_ser(e)},
    'Delta': {'coefficients_low_to_high': upoly_ser(Delta)},
    'cofactors': {n: [{'spow': i, 't': upoly_ser(tp)} for i, tp in enumerate(Q[n]) if tp]
                  for n in names},
    'search_side_notes': {
        'leave_out_row': names[LEAVE],
        'm_t': upoly_ser(M_T),
        'm_t_meaning': 'derived factor of the consistency determinant D(t) vanishing at '
                       't-hat = tan(theta-hat/2); equals A03 p(-t): the tan-half minimal '
                       'polynomial, here DERIVED by elimination, not PSLQ-fitted',
        'deg': {'Delta': len(Delta) - 1, 'D': len(D) - 1, 'e': len(e) - 1,
                'G_oct': len(G_oct) - 1, 'g_cof': len(g_cof) - 1},
        'provenance': 'A69-cidl-identity assemble.py; search untrusted, only the identity matters',
    },
}
out = os.path.join(REPO, 'certs', 'cidl_identity.json')
with open(out, 'w') as f:
    json.dump(cert, f)
print('wrote %s (%.1f KB)' % (out, os.path.getsize(out) / 1024))

# diagnostics for the notes: D, N_y4 saved
diag = {
    'D': upoly_ser(D),
    'N_y4': upoly_ser(N[XNAMES.index('y4')]),
    'N_S': upoly_ser(NS),
    'Delta': upoly_ser(Delta),
    'e': upoly_ser(e),
}
with open(os.path.join(HERE, 'results', 'diagnostics.json'), 'w') as f:
    json.dump(diag, f)
print('saved results/diagnostics.json')
