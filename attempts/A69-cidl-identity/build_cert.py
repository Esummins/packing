"""A69 phase 3 -- assemble the (c-idl) certificate against the CHECKER'S generators.

Imports certs/verify_cidl.py (the trusted checker) and uses ITS 13 generators
G_j verbatim, so the cofactors are computed against exactly what the checker
rebuilds.  Search-side only; nothing here is trusted.

Construction (all exact over Q):
  * the 13 generators are linear in x = (y4, x6..y10, S) over Q[t]:
        G_j = (A x - b)_j       (12 kept rows)   and   G_13 (left-out row)
  * adjugate identity:  sum_j adj[m][j] G_j = Delta x_m - N_m
  * leftover condition: D := sum_m a13_m N_m - Delta b13
                        D  = Delta G_13 - sum_j c_j G_j,  c_j = sum_m a13_m adj[m][j]
  * m(t) = the factor of D vanishing at t-hat (deg 8); e = D/m; G_oct = m*g
        G_oct := sum_k a_k N_S^k Delta^(8-k)   (octic = sum_k a_k s^k)
  * telescope:  Delta^8 octic(S) - G_oct = (Delta S - N_S) * Wtel,
        Wtel = sum_{k=1}^{8} a_k ( sum_{i=0}^{k-1} (Delta S)^i N_S^{k-1-i} ) Delta^{8-k}
  * certificate:
        e * Delta^8 * octic(S) = sum_j [ e*Wtel*adj[S][j] - g*c_j ] G_j + [ g*Delta ] G_13
"""
import os, sys, json, pickle
from fractions import Fraction as F
import sympy as sp
from sympy import Poly, QQ, Rational

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'certs'))
import verify_cidl as VC

t, S = sp.symbols('t S')
xnames = ['y4', 'x6', 'y6', 'x7', 'y7', 'x8', 'y8', 'x9', 'y9', 'x10', 'y10', 'S']
xsyms = [sp.Symbol(n) for n in xnames]
allsyms = [sp.Symbol(v) for v in VC.VARS]  # t first

OCTIC = [Rational(int(c)) for c in [-6865, 12420, -6754, -496, 1923, -842, 178, -20, 1]]
THAT = sp.Rational('0.365769307604677293388545018143311315239104830794924193607064')

def sparse_to_sympy(p):
    e = sp.Integer(0)
    for mon, c in p.items():
        term = sp.Rational(c.numerator, c.denominator)
        for v, k in zip(allsyms, mon):
            if k:
                term *= v**k
        e += term
    return sp.expand(e)

gens = VC.build_generators()
names = [n for n, _ in gens]
rows = [sparse_to_sympy(g) for _, g in gens]
print('generators:', names)

# linear structure over Q[t]
M = sp.zeros(13, 12)
b = sp.zeros(13, 1)
for r, p in enumerate(rows):
    rem = p
    for cidx, v in enumerate(xsyms):
        co = sp.expand(sp.diff(p, v))
        assert sp.diff(co, v) == 0, (names[r], v)
        for u in xsyms:
            assert sp.diff(co, u) == 0, (names[r], v, u)
        M[r, cidx] = co
        rem = sp.expand(rem - co * v)
    b[r, 0] = sp.expand(-rem)
    for u in xsyms:
        assert sp.diff(b[r, 0], u) == 0, names[r]

# choose leave-out: first row giving nonsingular kept system
t0 = sp.Rational(37, 101)
leave = None
for cand in range(13):
    keep = [r for r in range(13) if r != cand]
    if M[keep, :].subs(t, t0).det() != 0:
        leave = cand
        break
assert leave is not None
keep = [r for r in range(13) if r != leave]
print('leave-out row:', names[leave])

ring = QQ.old_poly_ring(t) if False else QQ[t]
from sympy.polys.matrices import DomainMatrix

def dm(mat):
    return DomainMatrix([[ring.from_sympy(sp.expand(mat[i, j])) for j in range(mat.shape[1])]
                         for i in range(mat.shape[0])], mat.shape, ring)

A = M[keep, :]
bb = b[keep, :]
Adm = dm(A)
print('computing adjugate/determinant over QQ[t]...')
adj_dm, Delta_r = Adm.adj_det()
Delta = ring.to_sympy(Delta_r)
adj = [[ring.to_sympy(adj_dm[i, j].element if hasattr(adj_dm[i, j], 'element') else adj_dm[i, j])
        for j in range(12)] for i in range(12)]
print('deg Delta =', sp.degree(Delta, t))

# sanity: adj * A == Delta * I at t0
At0 = A.subs(t, t0)
adjt0 = sp.Matrix(12, 12, lambda i, j: adj[i][j].subs(t, t0))
assert adjt0 * At0 == Delta.subs(t, t0) * sp.eye(12)
print('adjugate verified at t0')

N = [sp.expand(sum(adj[m][j] * bb[j, 0] for j in range(12))) for m in range(12)]
iS = xnames.index('S')

# leftover condition
a13 = [sp.expand(M[leave, j]) for j in range(12)]
b13 = b[leave, 0]
D = sp.expand(sum(a13[m] * N[m] for m in range(12)) - Delta * b13)
print('deg D =', sp.degree(D, t))
fac = sp.factor_list(D)
mfac = None
others = sp.Integer(1) * fac[0]
for f, mult in fac[1]:
    v = abs(sp.N(f.subs(t, THAT), 30))
    if v < 1e-40:
        assert mfac is None, 'two factors vanish at t-hat?!'
        mfac = f
        if mult > 1:
            others *= f**(mult - 1)
    else:
        others *= f**mult
assert mfac is not None, 'no factor of D vanishes at t-hat'
e = sp.expand(others)
assert sp.expand(e * mfac - D) == 0
print('m(t) =', mfac)
print('deg e =', sp.degree(e, t))

# octic membership
NS = N[iS]
G_oct = sp.expand(sum(OCTIC[k] * NS**k * Delta**(8 - k) for k in range(9)))
g_cof, r = sp.div(G_oct, mfac, t)
assert r == 0, 'm does not divide G_oct -- no certificate on this slice'
print('m | G_oct: OK  (deg g_cof = %d)' % sp.degree(g_cof, t))

# telescope Wtel
DS = Delta * S
Wtel = sp.expand(sum(OCTIC[k] * sum(DS**i * NS**(k - 1 - i) for i in range(k)) * Delta**(8 - k)
                     for k in range(1, 9)))

# c_j
c = [sp.expand(sum(a13[m] * adj[m][j] for m in range(12))) for j in range(12)]

# cofactors
q = {}
for jj, j in enumerate(keep):
    q[names[j]] = sp.expand(e * Wtel * adj[iS][jj] - g_cof * c[jj])
q[names[leave]] = sp.expand(g_cof * Delta)

# full verification of the identity (search-side; the checker redoes this)
print('verifying identity symbolically...')
lhs = sp.expand(sum(q[names[r]] * rows[r] for r in range(13)))
rhs = sp.expand(e * Delta**8 * sum(OCTIC[k] * sp.Symbol('S')**k for k in range(9)))
assert sp.expand(lhs - rhs) == 0, 'identity FAILED'
print('identity holds.')

# serialize
def upoly_coeffs(p, var):
    pp = Poly(p, var)
    cs = [sp.Rational(0)] * (pp.degree() + 1)
    for (k,), cco in zip(pp.monoms(), pp.coeffs()):
        cs[k] = cco
    return [str(x) for x in cs]

def biv_serialize(p):
    pp = Poly(p, S, t)
    by_s = {}
    for (ks, kt), cco in zip(pp.monoms(), pp.coeffs()):
        by_s.setdefault(ks, {})[kt] = cco
    out = []
    for ks in sorted(by_s):
        maxt = max(by_s[ks])
        tt = [str(by_s[ks].get(k, sp.Rational(0))) for k in range(maxt + 1)]
        out.append({'spow': ks, 't': tt})
    return out

cert = {
    'format': 'cidl-membership-v1',
    'description': ('Saturated ideal-membership certificate closing the identity '
                    's-hat_A22 = s-hat_octic (TopLevel.lean axiom shatA22_eq_shat): '
                    'e(t)*Delta(t)^8*octic(S) = sum_j q_j(t,S)*G_j over the 13 reduced '
                    'A22 contact rows on the certified exact-structure slice. '
                    'Checker: certs/verify_cidl.py (builds the G_j itself).'),
    'octic': {'variable': 'S', 'coefficients_low_to_high': [str(x) for x in OCTIC]},
    'gate_interval': {'a': '3/10', 'b': '2/5'},
    'e': {'coefficients_low_to_high': upoly_coeffs(e, t)},
    'Delta': {'coefficients_low_to_high': upoly_coeffs(Delta, t)},
    'cofactors': {n: biv_serialize(q[n]) for n in names},
    'search_side_notes': {
        'leave_out_row': names[leave],
        'm_t_factor_of_D_vanishing_at_t_hat': upoly_coeffs(mfac, t),
        'D_condition_deg': int(sp.degree(D, t)),
        'Delta_deg': int(sp.degree(Delta, t)),
        'provenance': 'A69-cidl-identity build_cert.py; search untrusted, only the identity matters',
    },
}
out = os.path.join(REPO, 'certs', 'cidl_identity.json')
with open(out, 'w') as f:
    json.dump(cert, f)
print('wrote', out, '(%.1f KB)' % (os.path.getsize(out) / 1024))

with open(os.path.join(HERE, 'results', 'cert_build.pkl'), 'wb') as f:
    pickle.dump({'Delta': sp.srepr(Delta), 'e': sp.srepr(e), 'm': sp.srepr(mfac),
                 'D': sp.srepr(D), 'g_cof': sp.srepr(g_cof), 'N_S': sp.srepr(NS),
                 'leave': leave}, f)
print('saved results/cert_build.pkl')
