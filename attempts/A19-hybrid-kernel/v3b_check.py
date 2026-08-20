"""V3b -- is the full-hybrid tiny solution genuine? Re-solve V3, then (1) exact constraint check,
(2) fresh-sample attack (new diag placements + new disjoint R-meeting pairs), (3) structure look,
(4) row-LP tau* reference on the same diag rows."""
import json, math, os, sys, time
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))

from features import FeatureMap, random_placements
from oracle_pair import overlap_depth_many
from hybrid import HybridSDP, Region
from validate import tiny_instance
import cvxpy as cp


def solve_full(fm, hs, extra_diag=None, extra_pairs=None, delta=1e-3):
    m = fm.m; w = fm.w
    inR = np.zeros(m, bool); inR[hs.r_idx] = True
    S = cp.Variable((m, m), symmetric=True)
    lam = cp.Variable()
    cons = [S >> 0]
    iu, ju = np.triu_indices(m, 1)
    mask = ~(inR[iu] & inR[ju])
    sel_i = iu[mask]; sel_j = ju[mask]
    G = sp.csr_matrix((np.ones(len(sel_i)), (np.arange(len(sel_i)), sel_i * m + sel_j)),
                      shape=(len(sel_i), m * m))
    cons.append(G @ cp.reshape(S, (m * m,), order="C") <= -(w[sel_i] * w[sel_j]))
    Pd = np.array(hs.diag_meta)
    if extra_diag is not None and len(extra_diag):
        Pd = np.vstack([Pd, extra_diag])
    pat_d = fm.patterns(Pd)
    mv = pat_d @ w
    ok = mv > 1e-9
    Ad = pat_d.toarray()[ok]; mv = mv[ok]
    # rows as one sparse linear map on vec(S)
    rows = []
    for i in range(Ad.shape[0]):
        a = sp.csr_matrix(Ad[i][None])
        rows.append(sp.kron(a, a))
    Rd = sp.vstack(rows, format="csr")
    cons.append(Rd @ cp.reshape(S, (m * m,), order="C") <= (lam - 1.0) * mv ** 2)
    PX = [p[0] for p in hs.pair_meta]; PY = [p[1] for p in hs.pair_meta]
    if extra_pairs is not None:
        PX += [p[0] for p in extra_pairs]; PY += [p[1] for p in extra_pairs]
    pa = fm.patterns(np.array(PX)); pb = fm.patterns(np.array(PY))
    m1 = pa @ w; m2 = pb @ w
    rows = []
    for i in range(pa.shape[0]):
        rows.append(sp.kron(pa[i], pb[i]))
    Rp = sp.vstack(rows, format="csr")
    cons.append(Rp @ cp.reshape(S, (m * m,), order="C") <= -(1.0 + delta) * m1 * m2)
    prob = cp.Problem(cp.Minimize(lam), cons)
    prob.solve(solver="CLARABEL")
    return float(lam.value), np.array(S.value), prob.status


def kd_of_S(fm, S, P):
    pat = fm.patterns(P)
    mv = pat @ fm.w
    A = pat.toarray()
    q = np.einsum('ip,pq,iq->i', A, S, A)
    return np.where(mv > 0, q / np.maximum(mv, 1e-300) ** 2, np.inf), mv


def main():
    fm, region, rng = tiny_instance()
    s = fm.s
    hs = HybridSDP(fm, region, delta_pair=1e-3)
    P = random_placements(s, 800, rng)
    hs.add_diag(P)
    P2 = random_placements(s, 400, rng)
    Xs, Ys = [], []
    for i in range(len(P2)):
        for j in range(i + 1, len(P2)):
            if overlap_depth_many(P2[i][None], P2[j][None])[0] < 0:
                Xs.append(P2[i]); Ys.append(P2[j])
    hs.add_pairs(np.array(Xs), np.array(Ys))
    inR = np.zeros(fm.m, bool); inR[hs.r_idx] = True

    lam, S, st = solve_full(fm, hs)
    print(f"full hybrid solve: lam = {lam:.6f} [{st}]")
    ev = np.linalg.eigvalsh(S)
    iu, ju = np.triu_indices(fm.m, 1)
    mask = ~(inR[iu] & inR[ju])
    viol_sign = float((S[iu[mask], ju[mask]] + fm.w[iu[mask]] * fm.w[ju[mask]]).max())
    print(f"  min eig S = {ev[0]:.2e}; max sign violation (non-R) = {viol_sign:.2e}")
    # structure: how far below the bound are non-R entries; R-block positivity
    slack = -(S[iu[mask], ju[mask]] + fm.w[iu[mask]] * fm.w[ju[mask]])
    print(f"  non-R off-diag slack below bound: median {np.median(slack):.4f}, "
          f"max {slack.max():.4f}, frac at bound(<1e-6) {np.mean(slack < 1e-6):.3f}")
    SR = S[np.ix_(hs.r_idx, hs.r_idx)]
    wR = fm.w[hs.r_idx]
    DR = SR + np.outer(wR, wR)
    off = DR[np.triu_indices(hs.k, 1)]
    print(f"  R-block D entries: min {off.min():.4f} max {off.max():.4f} "
          f"frac>0 {np.mean(off > 1e-9):.3f}")

    # fresh attack (cutting-plane style, 3 rounds)
    for rd in range(3):
        Pn = random_placements(s, 30000, np.random.default_rng(100 + rd))
        kd, mv = kd_of_S(fm, S, Pn)
        vd = kd - (lam - 1.0)
        # fresh disjoint pairs (R-meeting)
        Pm = random_placements(s, 1500, np.random.default_rng(200 + rd))
        pat = fm.patterns(Pm)
        meets = np.asarray(pat[:, hs.r_idx].sum(axis=1)).ravel() > 0
        idx = np.nonzero(meets)[0]
        XX, YY = [], []
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                i, j = idx[a], idx[b]
                if overlap_depth_many(Pm[i][None], Pm[j][None])[0] < 0:
                    XX.append(i); YY.append(j)
        A = fm.patterns(Pm).toarray()
        mvm = A @ fm.w
        kp = np.array([A[i] @ S @ A[j] / (mvm[i] * mvm[j]) for i, j in zip(XX, YY)])
        print(f"  attack rd{rd}: max fresh diag viol {vd.max():+.4f} "
              f"({(vd>1e-6).sum()} placements); max fresh pair K {kp.max():+.4f} "
              f"({(kp>-1.0).sum()}/{len(kp)} pairs > -1)")
        # add violated and re-solve
        ed = Pn[vd > 1e-6][:400]
        ep = [(Pm[i], Pm[j]) for i, j, v in zip(XX, YY, kp) if v > -1.0 - 1e-3][:800]
        if len(ed) == 0 and len(ep) == 0:
            print("  attack clean")
            break
        hs.add_diag(ed)
        hs.add_pairs(np.array([p[0] for p in ep]).reshape(-1, 3),
                     np.array([p[1] for p in ep]).reshape(-1, 3))
        lam, S, st = solve_full(fm, hs)
        print(f"  re-solve: lam = {lam:.6f} [{st}] ({len(hs.diag_meta)} diag, {len(hs.pair_meta)} pair rows)")

    # row-LP tau* on the diag rows (w free = plain LP floor reference)
    from scipy.optimize import linprog
    pat = fm.patterns(np.array(hs.diag_meta))
    lp = linprog(c=np.ones(fm.m), A_ub=-pat.toarray(), b_ub=-np.ones(pat.shape[0]),
                 bounds=(0, None), method="highs")
    print(f"row-LP tau* = {lp.fun:.4f}; two-measure/boundary lam = 14.462; full hybrid lam = {lam:.6f}")
    json.dump(dict(lam_full_converged=lam, tau_rows=float(lp.fun)),
              open(os.path.join(HERE, "results", "v3b.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
