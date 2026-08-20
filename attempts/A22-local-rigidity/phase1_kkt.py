"""Phase 1: rank analysis of the curated 38 constraints, choice of the
square subsystem S (34 constraints, nonsingular Jacobian), unique KKT
multipliers lambda = A_S^{-T} e_s, strict complementarity check."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a22lib import *
from mpmath import mp
import mpmath
import numpy as np

mp.dps = 90

z0, ex = load_z0()
cons = curated_constraints(ex)
zm = z_point(mp, z0)

# dense Jacobian (38 x 34) in mpf and float
G = [grad_g(mp, zm, c) for c in cons]
Jm = mp.zeros(len(cons), NV)
for r, g in enumerate(G):
    for k, v in g.items():
        Jm[r, k] = v
Jf = np.array([[float(Jm[r, k]) for k in range(NV)] for r in range(len(cons))])

# finite-difference check of gradients
h = mp.mpf('1e-30')
worst = mp.mpf(0)
for r, c in enumerate(cons[:6] + cons[20:24] + cons[36:]):
    pass
def fd_check(c):
    g = grad_g(mp, zm, c)
    w = mp.mpf(0)
    for k in list(g.keys()):
        zp = list(zm); zp[k] = zp[k] + h
        zq = list(zm); zq[k] = zq[k] - h
        fd = (eval_g(mp, zp, c) - eval_g(mp, zq, c)) / (2 * h)
        w = max(w, abs(fd - g[k]))
    return w
print('max FD-gradient error over all cons:',
      max(fd_check(c) for c in cons))

# numpy rank / dependency structure
u, sv, vt = np.linalg.svd(Jf)
print('singular values (smallest 8):', sv[-8:])
rank = int((sv > 1e-9).sum())
print('rank of 38x34 Jacobian:', rank, ' => dependencies:', len(cons) - rank)

# choose S: QR with pivoting on J^T. Prefer keeping edge+dist rows.
from scipy.linalg import qr
# weight rows we prefer to keep by putting them first with mild scaling
pref = []
for idx, c in enumerate(cons):
    pref.append((0 if c['kind'] != 'wall' else 1, idx))
order = [idx for _, idx in sorted(pref)]
Q, R, piv = qr(Jf[order].T, pivoting=True)
chosen = sorted(order[p] for p in piv[:rank])
dropped = sorted(set(range(len(cons))) - set(chosen))
print('dropped rows:', [(d, con_name(cons[d])) for d in dropped])

# nonsingularity of the S-Jacobian, condition number
JS = Jf[chosen]
print('cond(J_S):', np.linalg.cond(JS))

# unique multipliers on S: J_S^T lambda = e_s
JSm = mp.zeros(NV, NV)
for r, idx in enumerate(chosen):
    for k in range(NV):
        JSm[k, r] = Jm[idx, k]     # transpose
es = mp.zeros(NV, 1)
es[33, 0] = 1
lam = mp.lu_solve(JSm, es)
lamv = [lam[r, 0] for r in range(NV)]
print('\nmultipliers (constraint, lambda):')
for r, idx in enumerate(chosen):
    print('  %-22s %s' % (con_name(cons[idx]), mp.nstr(lamv[r], 12)))
neg = [(con_name(cons[idx]), lamv[r]) for r, idx in enumerate(chosen) if lamv[r] <= 0]
print('\nmin lambda:', mp.nstr(min(lamv), 12))
print('negative/zero multipliers:', neg if neg else 'NONE (strict complementarity on S)')
res = mp.norm(JSm * lam - es)
print('KKT residual |J_S^T lam - e_s|:', mp.nstr(res, 5))

# left null space of the full 38-row Jacobian (dependencies / self-stress)
u, sv, vt = np.linalg.svd(Jf.T)
null_dim = Jf.shape[0] - rank
print('\nleft-null dim:', null_dim)
NS = u[:, :] if False else None
import numpy.linalg as la
w, v = la.qr(Jf.T.T @ Jf.T + 0*np.eye(38)), None  # skip
# simpler: nullspace of Jf^T x = 0 over rows: svd of Jf gives row-space; want vectors y with y^T Jf = 0
uu, ss, vv = np.linalg.svd(Jf)
for k in range(rank, len(cons)):
    y = uu[:, k]
    supp = [(con_name(cons[i]), round(float(y[i]), 4)) for i in range(len(cons)) if abs(y[i]) > 1e-6]
    print('dependency %d support:' % k, supp)

json.dump({'chosen': chosen, 'dropped': dropped,
           'names': [con_name(c) for c in cons]},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'subsystem_S.json'), 'w'), indent=1)
