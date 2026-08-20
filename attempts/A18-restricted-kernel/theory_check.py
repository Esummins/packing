"""A18 -- machine validation of the restricted-class collapse theorem.

Claims checked here (see notes.md for proofs):
 T1. With phi(x) = (1, a(x)/m(x)) and M = [[1,-w^T],[-w,D]], M psd <=> S := D - w w^T psd,
     and K(x,x) = a(x)^T S a(x) / m(x)^2   (identity; checked against A17's kdiag).
 T2. For strictly disjoint closed squares, K(x,y) = -1 + a(x)^T C a(y)/(m m') with C = the
     off-diagonal part of D; if D_pq <= 0 off-diag then K <= -1 (equality when D diagonal).
 T3. (monotonicity) If S is u-dominance certified (u>0, Su>=0) and S_pq <= -w_p w_q, then for
     every 0/1 pattern a:  a^T S a >= a^T S_u a  where S_u is the "two-measure" boundary matrix
     (S_u)_pq = -w_p w_q (p != q), (S_u)_pp = w_p (W - w_p u_p)/u_p,  W = sum_q w_q u_q.
 T4. (identity) a^T S_u a = W * (sum_{p in a} w_p/u_p) - m(a)^2, so
     K_u(x,x) = W*vt(x)/m(x)^2 - 1  with vt(x) = sum_{p in x} (w_p/u_p) a_p.
 T5. (class = two-measure family) the restricted-class SDP optimum on any finite row set equals
     inf_u of max_x [1 + K_u(x,x)] (checked: cvxpy SDP value == softmax-LBFGS u-optimum), and
     >= the row-LP value tau*_rows = min sum(nu) s.t. nu(a_i) >= 1; equality when w = nu_LP.
"""
import math, os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap, d4_images_pt, random_placements, kdiag
from oracle_pair import overlap_depth_many

rng = np.random.default_rng(3)
s = 3.8
reps = np.array([[1.0, 1.0], [1.0, 1.9], [0.7, 1.0], [1.4, 1.4], [1.0, 1.53]])
A = []
for x, y in reps:
    for q in d4_images_pt(x, y, s):
        if not any(abs(q[0]-r[0]) < 1e-9 and abs(q[1]-r[1]) < 1e-9 for r in A):
            A.append(q)
A = np.array(A)
m = len(A)
w = np.full(m, 0.3)
fm = FeatureMap(A, w, s)
print(f"tiny instance: {m} atoms at s={s}")

def build_Su(w, u):
    W = float(w @ u)
    Su = -np.outer(w, w)
    np.fill_diagonal(Su, w * (W - w * u) / u)
    return Su, W

def M_of_S(S, w):
    nf = len(w) + 1
    M = np.zeros((nf, nf))
    M[0, 0] = 1.0
    M[0, 1:] = -w
    M[1:, 0] = -w
    M[1:, 1:] = S + np.outer(w, w)
    return M

# ---- placements with nonzero coverage
P = random_placements(s, 4000, rng)
pat = fm.patterns(P)
cov = pat @ w
keep = cov > 1e-9
P, cov = P[keep], cov[keep]
pat = pat[np.nonzero(keep)[0]]
print(f"{len(P)} placements with m(x)>0 (min cov {cov.min():.3f})")

# ---- T1/T4: identity K(x,x) via A17 kdiag vs formulas, psd of M
u = np.exp(rng.uniform(-1.0, 1.0, m))
Su, W = build_Su(w, u)
M = M_of_S(Su, w)
ev = np.linalg.eigvalsh(M)
Phi = fm.phi(pat=pat)
kd = kdiag(Phi, M)
vt = pat @ (w / u)
form = W * vt / cov**2 - 1.0
patd = pat.toarray()
quad = np.einsum('ij,jk,ik->i', patd, Su, patd)
err1 = np.abs(kd - form).max()
err2 = np.abs(kd - (quad / cov**2)).max()
print(f"T1/T4: eigmin(M) = {ev.min():+.2e} (>=0); |kdiag - two-measure formula| = {err1:.2e}; "
      f"|kdiag - a'Sa/m^2| = {err2:.2e}")
assert ev.min() > -1e-9 and err1 < 1e-9 and err2 < 1e-9

# ---- T2: disjoint pairs, D diagonal -> K = -1 exactly; generic Z-margin S -> K <= -1
idx = rng.choice(len(P), (4000, 2))
dep = overlap_depth_many(P[idx[:, 0]], P[idx[:, 1]])
dis = idx[dep < -1e-9]
Phi1 = fm.phi(P[dis[:, 0]]); Phi2 = fm.phi(P[dis[:, 1]])
Kp = np.einsum('ij,ij->i', np.asarray(Phi1 @ M), Phi2.toarray())
print(f"T2a: {len(dis)} strictly disjoint pairs, D diagonal: max |K+1| = {np.abs(Kp + 1).max():.2e}")
assert np.abs(Kp + 1).max() < 1e-9

# generic feasible S: S2 = S_u + G, G = graph-Laplacian-like with G u = 0 (so S2 u >= 0), E >= 0
E = rng.uniform(0, 0.2, (m, m)); E = np.triu(E, 1); E = E + E.T
G = -E.copy()
np.fill_diagonal(G, (E @ u) / u)
S2 = Su + G
assert np.linalg.eigvalsh(np.diag(u) @ G @ np.diag(u)).min() > -1e-9
M2 = M_of_S(S2, w)
Kp2 = np.einsum('ij,ij->i', np.asarray(Phi1 @ M2), Phi2.toarray())
print(f"T2b: generic Z-margin S: eigmin(M2) = {np.linalg.eigvalsh(M2).min():+.2e}; "
      f"max K over disjoint pairs = {Kp2.max():.6f} (<= -1)")
assert Kp2.max() <= -1 + 1e-9

# ---- T3: pointwise monotonicity a'S2a >= a'S_u a on every pattern
q2 = np.einsum('ij,jk,ik->i', patd, S2, patd)
diff = q2 - quad
print(f"T3: min over {len(P)} patterns of a'(S_u+G)a - a'S_u a = {diff.min():+.3e} (>= 0)")
assert diff.min() > -1e-9

# ---- T5: cvxpy restricted SDP == softmax u-optimum >= row-LP; equality at w = nu_LP
import cvxpy as cp
from scipy.optimize import minimize, linprog

# dedup patterns for rows
keys = {}
rows = []
for i in range(min(len(P), 1200)):
    nz = tuple(pat.indices[pat.indptr[i]:pat.indptr[i+1]])
    if nz and nz not in keys:
        keys[nz] = 1
        rows.append(i)
rows = np.array(rows)
Arow = patd[rows]          # (R, m) 0/1
print(f"T5: {len(rows)} deduped pattern rows")

def solve_sdp(wv):
    mv = Arow @ wv
    ok = mv > 1e-9
    Ar, mr = Arow[ok], mv[ok]
    nf = m + 1
    Mv = cp.Variable((nf, nf), symmetric=True)
    t = cp.Variable()
    cons = [Mv >> 0, Mv[0, 0] == 1, Mv[0, 1:] == -wv]
    for i in range(m):
        for j in range(i + 1, m):
            cons.append(Mv[i + 1, j + 1] <= 0)
    for i in range(len(Ar)):
        phi = np.concatenate([[1.0], Ar[i] / mr[i]])
        cons.append(cp.quad_form(phi, Mv) <= t)
    pr = cp.Problem(cp.Minimize(t), cons)
    pr.solve(solver="CLARABEL")
    return 1.0 + pr.value          # lambda = 1 + max K

def solve_u(wv, beta_sched=(50, 500, 5000, 50000)):
    mv = Arow @ wv
    ok = mv > 1e-9
    Ar, mr = Arow[ok], mv[ok]
    logm2 = 2 * np.log(mr)
    th0 = np.zeros(m)
    for beta in beta_sched:
        def f(th):
            eth = np.exp(th)
            Wv = wv @ eth
            vt = Ar @ (wv * np.exp(-th))
            g = np.log(Wv) + np.log(vt) - logm2
            gm = g.max()
            z = np.exp(beta * (g - gm))
            Z = z.sum()
            F = gm + np.log(Z) / beta
            sm = z / Z
            eW = wv * eth / Wv
            dvt = -(Ar * (wv * np.exp(-th))[None, :]) / vt[:, None]
            grad = eW * sm.sum() + dvt.T @ sm
            return F, grad
        res = minimize(f, th0, jac=True, method="L-BFGS-B",
                       options=dict(maxiter=2000, ftol=1e-16, gtol=1e-12))
        th0 = res.x
    Wv = wv @ np.exp(th0)
    val = Wv * (Arow @ (wv * np.exp(-th0))) / (Arow @ wv)**2
    return float(val.max()), th0    # = lambda

# row-LP: tau*_rows
lp = linprog(c=np.ones(m), A_ub=-Arow, b_ub=-np.ones(len(Arow)), bounds=(0, None), method="highs")
tau_rows = lp.fun
nu_lp = lp.x
lam_sdp_w = solve_sdp(w)
lam_u_w, _ = solve_u(w)
w2 = np.maximum(nu_lp, 1e-7)
lam_sdp_lp = solve_sdp(w2)
lam_u_lp, _ = solve_u(w2)
print(f"T5: row-LP tau* = {tau_rows:.6f}")
print(f"    fixed w=const:  SDP lambda = {lam_sdp_w:.6f}   u-family inf = {lam_u_w:.6f}  "
      f"(match: {abs(lam_sdp_w-lam_u_w):.1e}; >= tau*: {lam_sdp_w - tau_rows:+.4f})")
print(f"    w = nu_LP:      SDP lambda = {lam_sdp_lp:.6f}   u-family inf = {lam_u_lp:.6f}  "
      f"(== tau*: {abs(lam_sdp_lp-tau_rows):.1e})")
res = dict(m_atoms=int(m), n_rows=int(len(rows)), tau_rows=float(tau_rows),
           lam_sdp_fixed_w=float(lam_sdp_w), lam_u_fixed_w=float(lam_u_w),
           lam_sdp_lp_w=float(lam_sdp_lp), lam_u_lp_w=float(lam_u_lp),
           t1_err=float(err1), t2b_max_pairK=float(Kp2.max()), t3_min_gap=float(diff.min()))
json.dump(res, open(os.path.join(HERE, "results", "theory_check.json"), "w"), indent=1)
print("saved results/theory_check.json")
