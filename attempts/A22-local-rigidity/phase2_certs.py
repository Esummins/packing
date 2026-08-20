"""Phase 2: high-precision lambda on the chosen S; 68 closed-form
positive-spanning certificates  sigma*e_i = sum mu_k grad g_k - nu*e_s,
mu = c + nu*lambda >= 0,  nu = (1+eps)*max(0, max_k(-c_k/lambda_k)).
Certificates rounded to rationals; stored for the interval verifier."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from fractions import Fraction
from mpmath import mp

mp.dps = 90
z0, ex = load_z0()
cons = curated_constraints(ex)
zm = z_point(mp, z0)

DROP = [i for i, c in enumerate(cons) if con_name(c) in
        ('W0c0[y=0]', 'W2c2[x=s]', 'W5c3[y=s]', 'E8c3-7e0')]
S = [i for i in range(len(cons)) if i not in DROP]
assert len(S) == NV
print('dropped:', [con_name(cons[d]) for d in DROP])

# A = 34x34 matrix, rows = grad g_k (k in S)
G = [grad_g(mp, zm, cons[k]) for k in S]
A = mp.zeros(NV, NV)
for r, g in enumerate(G):
    for k, v in g.items():
        A[r, k] = v
AT = A.T

es = mp.zeros(NV, 1); es[33, 0] = 1
lam = mp.lu_solve(AT, es)
lamv = [lam[r, 0] for r in range(NV)]
mn = min(lamv)
print('min lambda:', mp.nstr(mn, 15), 'at', con_name(cons[S[lamv.index(mn)]]))
print('max lambda:', mp.nstr(max(lamv), 15))
print('KKT residual:', mp.nstr(mp.norm(AT * lam - es), 5))
assert mn > 0

# certificates
nu_all = []
mu_all = []
maxmu = mp.mpf(0)
for i in range(NV):
    for sg in (1, -1):
        b = mp.zeros(NV, 1); b[i, 0] = sg
        cvec = mp.lu_solve(AT, b)
        cv = [cvec[r, 0] for r in range(NV)]
        nu = max([mp.mpf(0)] + [-cv[r] / lamv[r] for r in range(NV)]) * (mp.mpf(1) + mp.mpf('1e-10'))
        mu = [cv[r] + nu * lamv[r] for r in range(NV)]
        m2 = min(mu)
        assert m2 >= 0, (i, sg, m2)
        nu_all.append(nu)
        mu_all.append(((i, sg), nu, mu))
        maxmu = max(maxmu, max(mu))
print('max nu:', mp.nstr(max(nu_all), 8))
print('max mu:', mp.nstr(maxmu, 8))
l1 = max(sum(mu, mp.mpf(0)) + nu for (_, nu, mu) in mu_all)
print('max ||(mu,nu)||_1:', mp.nstr(l1, 8))

# rational rounding (denominator 10^40) and exact-rational storage
Q = 10 ** 40
def rat(x):
    return Fraction(int(mp.floor(x * Q + mp.mpf('0.5'))), Q)

out = {
    'dropped': DROP,
    'S': S,
    'names': [con_name(c) for c in cons],
    'lambda': [frac_str(rat(v)) for v in lamv],
    'certificates': [
        {'i': i, 'sigma': sg, 'nu': frac_str(rat(nu)),
         'mu': [frac_str(rat(m)) for m in mu]}
        for (i, sg), nu, mu in mu_all],
}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'farkas_certs.json')
json.dump(out, open(path, 'w'))
print('wrote', path)

# quick residual estimate of the rounded certificates at the centre (float check)
import numpy as np
Af = np.array([[float(A[r, k]) for k in range(NV)] for r in range(NV)])
worst = 0.0
for cert in out['certificates']:
    mu = np.array([float(str_frac(x)) for x in cert['mu']])
    nu = float(str_frac(cert['nu']))
    b = np.zeros(NV); b[cert['i']] = cert['sigma']
    resid = mu @ Af - nu * np.eye(NV)[33] - b
    worst = max(worst, np.abs(resid).sum())
print('worst centre residual l1 of rounded certs (float):', worst)
