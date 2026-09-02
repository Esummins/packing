"""A69 phase 2 -- exact elimination over Q(t) and the octic membership.

Takes the 13 reduced rows (phase 1), leaves one out, solves the 12x12 system by
adjugate/Cramer over Q[t], forms the leftover consistency condition D(t), factors
it, and tests:
  * which factor m(t) vanishes at t-hat = tan(theta-hat/2) ~ 0.365769307604677
  * whether m(t) divides G_oct(t) = sum_k a_k N_S(t)^k Delta(t)^(8-k)
    (octic = sum a_k s^k)  -- the heart of the (c-idl) certificate
  * where y4 = N_y4(t-hat)/Delta(t-hat) actually lives (A03 deg-7 minpoly test)
"""
import os, pickle, json
import sympy as sp
from sympy import Poly, QQ

HERE = os.path.dirname(os.path.abspath(__file__))
t, S, y4 = sp.symbols('t S y4')

with open(os.path.join(HERE, 'results', 'reduced_system.pkl'), 'rb') as f:
    data = pickle.load(f)
M = sp.sympify(data['M'])
b = sp.sympify(data['b'])
names = [g[0][0] for g in data['groups']]
xvars = data['xvars']
print('rows:', names)
print('xvars:', xvars)

OCTIC = [-6865, 12420, -6754, -496, 1923, -842, 178, -20, 1]  # a_0..a_8
P_T = [-1, -2, 2, 6, 12, -14, -2, 10, 5]   # p(t) from A03 (vanishes at -t-hat)
THAT = sp.Rational('0.365769307604677293388545018143311315239104830794924193607064')

t0 = sp.Rational(37, 101)

# choose leave-out row: try each, keep those with generically nonsingular A
sing = []
for leave in range(13):
    keep = [r for r in range(13) if r != leave]
    A0 = M[keep, :].subs(t, t0)
    if A0.det() != 0:
        sing.append(leave)
print('leave-out choices with nonsingular A:', [names[i] for i in sing])

leave = sing[0]
keep = [r for r in range(13) if r != leave]
print('using leave-out row:', names[leave])
A = M[keep, :]
bb = b[keep, :]

# convert to DomainMatrix over QQ[t] for fast exact det/adjugate
ring = QQ[t]
def to_ring(e):
    return Poly(sp.expand(e), t, domain=QQ)

from sympy.polys.matrices import DomainMatrix
Adm = DomainMatrix([[ring.from_sympy(sp.expand(A[i, j])) for j in range(12)] for i in range(12)], (12, 12), ring)
bdm = DomainMatrix([[ring.from_sympy(sp.expand(bb[i, 0]))] for i in range(12)], (12, 1), ring)

Delta_r = Adm.det()
Delta = ring.to_sympy(Delta_r)
Dp = Poly(Delta, t)
print('deg Delta =', Dp.degree())

# adjugate via cofactors: adj[i][j] = (-1)^(i+j) * minor(j,i)
# we need N_m = (adj * b)_m for all m, i.e. Cramer: N_m = det(A with col m -> b)
N = []
Alist = [[sp.expand(A[i, j]) for j in range(12)] for i in range(12)]
for m in range(12):
    cols = [[ (bb[i,0] if j == m else A[i,j]) for j in range(12)] for i in range(12)]
    dm = DomainMatrix([[ring.from_sympy(sp.expand(cols[i][j])) for j in range(12)] for i in range(12)], (12,12), ring)
    N.append(ring.to_sympy(dm.det()))
    print('N_%s deg %d' % (xvars[m], Poly(N[m], t).degree()))

# consistency of the kept system: A * N == Delta * b  (Cramer identity check at t0)
Nv = sp.Matrix([[Ni.subs(t, t0)] for Ni in N])
assert (A.subs(t, t0) * Nv - Delta.subs(t, t0) * bb.subs(t, t0)).norm() == 0
print('Cramer solution verified at t0')

# leftover condition D(t) = a_leave . N - Delta * b_leave
arow = M[leave, :]
Dcond = sp.expand(sum(sp.expand(arow[0, m]) * N[m] for m in range(12)) - Delta * b[leave, 0])
Dc = Poly(Dcond, t)
print('deg D =', Dc.degree())
fac = sp.factor_list(Dcond)
print('D factors:')
mfac = None
for f, mult in fac[1]:
    val = sp.sign(f.subs(t, THAT))
    v = f.subs(t, THAT)
    near = abs(sp.N(v, 30))
    print('   mult %d deg %d  |f(t~)| ~ %s   %s' % (mult, Poly(f, t).degree(), sp.N(near, 3), sp.sstr(f)[:120]))
    if near < 1e-40:
        mfac = (f, mult)
print('t-hat factor:', sp.sstr(mfac[0]) if mfac else None)

# compare with A03 p(t): p(-t) up to sign?
pt = sum(c * t**k for k, c in enumerate(P_T))
pmt = sp.expand(pt.subs(t, -t))
print('p(-t) == +-m ?', sp.simplify(mfac[0] - pmt) == 0 or sp.simplify(mfac[0] + pmt) == 0 if mfac else 'n/a')

# octic membership: G_oct = sum a_k N_S^k Delta^(8-k)
iS = xvars.index('S')
NS = N[iS]
G_oct = sp.expand(sum(OCTIC[k] * NS**k * Delta**(8 - k) for k in range(9)))
print('deg G_oct =', Poly(G_oct, t).degree())
q, r = sp.div(G_oct, mfac[0], t)
print('m | G_oct ?', r == 0)

# y4 location
iy = xvars.index('y4')
y4v = sp.N(N[iy].subs(t, THAT) / Delta.subs(t, THAT), 80)
print('y4 from elimination =', y4v)
A03Y4 = sp.Rational('2.53255831434961478706261630031474610351563106381658734570862')
print('A03 cy4            =', sp.N(A03Y4, 60))
print('diff =', sp.N(y4v - A03Y4, 10))
m7 = [-141578, 255957, 28184, 857962, 244037, -2766727, 1599635, -1430160]
p7 = sum(c * y4**k for k, c in enumerate(m7))
print('A03 deg-7 minpoly at A03 y4 (60-digit):', sp.N(p7.subs(y4, A03Y4), 10))

with open(os.path.join(HERE, 'results', 'elimination.pkl'), 'wb') as f:
    pickle.dump({'leave': leave, 'keep': keep, 'names': names,
                 'Delta': sp.srepr(Delta), 'N': [sp.srepr(x) for x in N],
                 'Dcond': sp.srepr(Dcond), 'mfac': sp.srepr(mfac[0]) if mfac else None,
                 'mmult': mfac[1] if mfac else None,
                 'G_oct': sp.srepr(G_oct)}, f)
print('saved results/elimination.pkl')
