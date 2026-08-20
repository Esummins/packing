"""A18 -- medium-scale validation of the collapse theorem (96 atoms, 220 pattern rows, generic
orbit-constant weights, NON-symmetrised row sample):

  restricted-class SDP (cvxpy/Clarabel, D off-diag <= 0 via cp.upper_tri, M psd, border -w)
    == two-measure GP inf_u max_rows W*vt/m^2   (full per-atom theta = log u, softmax L-BFGS)

Observed: SDP lambda = 17.057096, GP = 17.057133 (beta -> 3e5), diff 4e-5.  Also checked:
u_eps = (S* + eps I)^{-1} 1 from the SDP's own solution gives the two-measure value ->
17.057097 as eps -> 0 (the optimal S* is singular; u blows up but its PROFILE converges) —
the collapse is exact and the dominance-vector route recovers it constructively.

Pitfalls this run documents (both hit during development):
 (1) cvxpy fancy-indexing Mv[1:,1:][iu] for the sign constraints silently under-constrains —
     use cp.upper_tri;
 (2) the orbit-constant parametrisation of u is only WLOG when the row set is D4-closed (or
     canon-deduped orbit representatives, as in run_opt.py) — on an arbitrary row sample the
     optimal u is not D4-invariant (here: orbit-restricted GP gives 18.04, full 17.057).
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
from features import FeatureMap, d4_images_pt, random_placements
from scipy.optimize import minimize


def build():
    rng = np.random.default_rng(9)
    s = 3.8
    reps = rng.uniform(0.55, s / 2, (12, 2))
    A = []
    for x, y in reps:
        for q in d4_images_pt(x, y, s):
            if not any(abs(q[0] - r[0]) < 1e-9 and abs(q[1] - r[1]) < 1e-9 for r in A):
                A.append(q)
    A = np.array(A)
    w = []
    for x, y in reps:
        seen = []
        for q in d4_images_pt(x, y, s):
            if not any(abs(q[0] - r[0]) < 1e-9 and abs(q[1] - r[1]) < 1e-9 for r in seen):
                seen.append(q)
        val = 0.1 + 0.4 * rng.random()
        w += [val] * len(seen)
    w = np.array(w)
    fm = FeatureMap(A, w, s)
    P = random_placements(s, 3000, rng)
    pat = fm.patterns(P)
    pat = pat[np.nonzero((pat @ w) > 1e-9)[0]]
    keys = set()
    rows = []
    for i in range(pat.shape[0]):
        nz = tuple(pat.indices[pat.indptr[i]:pat.indptr[i + 1]])
        if nz and nz not in keys:
            keys.add(nz)
            rows.append(i)
    return fm, w, pat[rows[:220]].toarray()


def main():
    fm, w, Arow = build()
    m = fm.m
    mv = Arow @ w
    import cvxpy as cp
    Mv = cp.Variable((m + 1, m + 1), symmetric=True)
    t = cp.Variable()
    cons = [Mv >> 0, Mv[0, 0] == 1, Mv[0, 1:] == -w, cp.upper_tri(Mv[1:, 1:]) <= 0]
    for i in range(Arow.shape[0]):
        phi = np.concatenate([[1.0], Arow[i] / mv[i]])
        cons.append(cp.quad_form(phi, Mv) <= t)
    cp.Problem(cp.Minimize(t), cons).solve(solver="CLARABEL")
    lam_sdp = 1 + t.value
    Sstar = Mv.value[1:, 1:] - np.outer(w, w)
    u_eps = np.linalg.solve(Sstar + 1e-6 * np.eye(m), np.ones(m))
    lam_ueps = float(((w @ u_eps) * (Arow @ (w / u_eps)) / mv ** 2).max())

    logm2 = 2 * np.log(mv)
    th = np.zeros(m)
    for beta in (30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000):
        def f(th):
            eth = np.exp(th)
            W = w @ eth
            vt = Arow @ (w * np.exp(-th))
            g = np.log(W) + np.log(vt) - logm2
            gm = g.max()
            z = np.exp(beta * (g - gm))
            Z = z.sum()
            sm = z / Z
            dvt = -(Arow * (w * np.exp(-th))[None, :]) / vt[:, None]
            return gm + np.log(Z) / beta, (w * eth / W) * sm.sum() + dvt.T @ sm
        th = minimize(f, th, jac=True, method="L-BFGS-B",
                      options=dict(maxiter=20000, maxcor=30, ftol=1e-19, gtol=1e-15)).x
    W = w @ np.exp(th)
    lam_gp = float((W * (Arow @ (w * np.exp(-th))) / mv ** 2).max())
    print(f"SDP {lam_sdp:.6f}  GP {lam_gp:.6f}  u_eps {lam_ueps:.6f}  "
          f"(diffs {lam_gp-lam_sdp:+.1e}, {lam_ueps-lam_sdp:+.1e})")
    json.dump(dict(m=int(m), n_rows=int(Arow.shape[0]), lam_sdp=float(lam_sdp),
                   lam_gp=lam_gp, lam_u_eps=lam_ueps),
              open(os.path.join(HERE, "results", "medium_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
