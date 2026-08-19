"""A15 — Schrijver / Lovasz-Schrijver theta-prime  theta'(G) = max{ 1'B1 : B psd, B >= 0, tr B = 1, B_ij = 0 (ij in E) }
with the container's D4 symmetry block-diagonalised and fed directly to SCS.

B may be taken D4-invariant (average an optimal B over the group: all constraints and the objective are invariant).
Invariant B = sum_rho sum_{r=1..d_rho} T_rho^(r) X_rho T_rho^(r)T, X_rho psd (m_rho x m_rho), with T built orbit-wise from
the isotypic projectors P_{rs} = (d_rho/8) sum_g rho(g)_{rs} pi(g) (Serre 2.7).  Irreps of D4: A1, A2, B1, B2 (1-dim), E (2-dim).
Group elements g = 2k + e  <->  f^e r^k with r = rotation by 90 deg about the container centre, f = reflection x -> s-x
(same enumeration as graph.d4_images).
"""
import math, time
import numpy as np
import scipy.sparse as sp

IRREPS = ["A1", "A2", "B1", "B2", "E"]
DIMS = {"A1": 1, "A2": 1, "B1": 1, "B2": 1, "E": 2}


def rep_matrices():
    """rho[name][g] = matrix (d x d) of group element g = 2k + e  (f^e r^k)."""
    R = np.array([[0., -1.], [1., 0.]]); F = np.array([[-1., 0.], [0., 1.]])
    out = {n: [] for n in IRREPS}
    for k in range(4):
        for e in range(2):
            M = np.linalg.matrix_power(F, e) @ np.linalg.matrix_power(R, k)
            out["E"].append(M)
            out["A1"].append(np.array([[1.]]))
            out["A2"].append(np.array([[(-1.) ** e]]))
            out["B1"].append(np.array([[(-1.) ** k]]))
            out["B2"].append(np.array([[(-1.) ** (k + e)]]))
    return out


def symmetry_basis(G, orbs):
    """For each orbit O and irrep rho: V[rho][r] (n_O x m_rho(O)) orthonormal, r = 0..d-1.
    Returns dict with per-node sparse rows: t[rho][r] = (N, 2) values, col[rho] = (N, 2) global column index (-1 = none),
    and block sizes m[rho]."""
    rho = rep_matrices()
    N = G.shape[1]
    t = {n: [np.zeros((N, 2)) for _ in range(DIMS[n])] for n in IRREPS}
    col = {n: -np.ones((N, 2), dtype=int) for n in IRREPS}
    m = {n: 0 for n in IRREPS}
    for O in orbs:
        nO = len(O)
        loc = {int(i): a for a, i in enumerate(O)}
        Pi = np.zeros((8, nO, nO))
        for g in range(8):
            for a, i in enumerate(O):
                Pi[g, loc[int(G[g, i])], a] = 1.0
        for n in IRREPS:
            d = DIMS[n]
            P = {}
            for r in range(d):
                for s_ in range(d):
                    P[(r, s_)] = (d / 8.0) * sum(rho[n][g][r, s_] * Pi[g] for g in range(8))
            P11 = P[(0, 0)]
            w, U = np.linalg.eigh((P11 + P11.T) / 2)
            V1 = U[:, w > 0.5]
            mO = V1.shape[1]
            if mO == 0:
                continue
            assert mO <= 2, (n, mO, nO)
            Vs = [V1] + [P[(r, 0)] @ V1 for r in range(1, d)]
            for r in range(d):
                Vr = Vs[r]
                assert np.allclose(Vr.T @ Vr, np.eye(mO), atol=1e-8), (n, r, Vr.T @ Vr)
                t[n][r][O, :mO] = Vr
            col[n][O, :mO] = m[n] + np.arange(mO)[None, :]
            m[n] += mO
    return dict(t=t, col=col, m=m)


def dense_T(SB, n, r):
    N = SB["col"][n].shape[0]
    Tm = np.zeros((N, SB["m"][n]))
    for a in range(2):
        ok = SB["col"][n][:, a] >= 0
        Tm[np.nonzero(ok)[0], SB["col"][n][ok, a]] = SB["t"][n][r][ok, a]
    return Tm


def reconstruct_B(SB, X):
    """Dense B = sum_rho sum_r T X T^T from blocks X[rho]."""
    N = SB["col"]["A1"].shape[0]
    B = np.zeros((N, N))
    for n in IRREPS:
        if SB["m"][n] == 0:
            continue
        for r in range(DIMS[n]):
            Tm = dense_T(SB, n, r)
            B += Tm @ X[n] @ Tm.T
    return B


def pair_orbits(G, ov, chunk=400):
    """Representatives of the orbits of unordered node pairs (i<j) under D4: (I, J, is_edge, orbit sizes)."""
    N = G.shape[1]
    keys_all = []
    for i0 in range(0, N, chunk):
        i1 = min(N, i0 + chunk)
        I, J = np.meshgrid(np.arange(i0, i1), np.arange(N), indexing='ij')
        mask = J > I
        I = I[mask]; J = J[mask]
        best = None
        for g in range(8):
            gi = G[g, I]; gj = G[g, J]
            k = np.minimum(gi, gj).astype(np.int64) * N + np.maximum(gi, gj)
            best = k if best is None else np.minimum(best, k)
        keys_all.append(best)
    keys = np.concatenate(keys_all)
    uk, counts = np.unique(keys, return_counts=True)
    I = uk // N; J = uk % N
    return I.astype(int), J.astype(int), ov[I, J], counts


def svec_index(m):
    """SCS lower-triangular column-major svec ordering: index of (a,b)."""
    idx = np.zeros((m, m), dtype=np.int64)
    k = 0
    for b in range(m):
        for a in range(b, m):
            idx[a, b] = k; idx[b, a] = k; k += 1
    return idx


def build_scs(G, orbs, ov, SB, log=print, trace_scale=1.0):
    """Returns (data, cone, meta) for scs.SCS."""
    N = G.shape[1]
    I, J, isE, cnt = pair_orbits(G, ov)
    log(f"  pair orbits: {len(I)} (edge orbits {isE.sum()}, non-edge {(~isE).sum()})")
    off = {}; nvar = 0; sidx = {}
    for n in IRREPS:
        m = SB["m"][n]
        off[n] = nvar; nvar += m * (m + 1) // 2; sidx[n] = svec_index(m) if m > 0 else None
    npair = len(I)
    rows_l, cols_l, vals_l = [], [], []
    for n in IRREPS:
        m = SB["m"][n]
        if m == 0:
            continue
        col = SB["col"][n]
        for a in range(2):
            for b in range(2):
                ca = col[I, a]; cb = col[J, b]
                ok = (ca >= 0) & (cb >= 0)
                if not ok.any():
                    continue
                v = np.zeros(npair)
                for r in range(DIMS[n]):
                    v += SB["t"][n][r][I, a] * SB["t"][n][r][J, b]
                ca_, cb_ = ca[ok], cb[ok]
                scale = np.where(ca_ == cb_, 1.0, 1.0 / math.sqrt(2.0))
                rows_l.append(np.nonzero(ok)[0]); cols_l.append(off[n] + sidx[n][ca_, cb_]); vals_l.append(v[ok] * scale)
    rows = np.concatenate(rows_l); cols = np.concatenate(cols_l); vals = np.concatenate(vals_l)
    Cpair = sp.csr_matrix((vals, (rows, cols)), shape=(npair, nvar))
    Cpair.sum_duplicates()
    tr_cols = []; tr_vals = []
    for n in IRREPS:
        m = SB["m"][n]
        if m == 0:
            continue
        d = DIMS[n]
        diag = np.array([sidx[n][a, a] for a in range(m)])
        tr_cols.append(off[n] + diag); tr_vals.append(np.full(m, float(d)))
    tc = np.concatenate(tr_cols); tv = np.concatenate(tr_vals)
    tr_row = sp.csr_matrix((tv, (np.zeros(len(tc), dtype=int), tc)), shape=(1, nvar))
    c = np.zeros(nvar)
    for n in IRREPS:
        m = SB["m"][n]
        if m == 0:
            continue
        for r in range(DIMS[n]):
            u = dense_T(SB, n, r).T @ np.ones(N)
            if np.abs(u).max() < 1e-12:
                continue
            M = np.outer(u, u)
            for a in range(m):
                for b in range(a, m):
                    c[off[n] + sidx[n][a, b]] -= (M[a, a] if a == b else 2 * M[a, b] / math.sqrt(2.0))
    Ez = Cpair[isE]; Enz = Cpair[~isE]
    A_zero = sp.vstack([tr_row, Ez])
    b_zero = np.zeros(A_zero.shape[0]); b_zero[0] = float(trace_scale)
    A_pos = -Enz
    b_pos = np.zeros(A_pos.shape[0])
    A_psd = -sp.identity(nvar, format='csr')
    b_psd = np.zeros(nvar)
    A = sp.vstack([A_zero, A_pos, A_psd]).tocsc()
    b = np.concatenate([b_zero, b_pos, b_psd])
    c = c / float(trace_scale)
    cone = dict(z=A_zero.shape[0], l=A_pos.shape[0], s=[SB["m"][n] for n in IRREPS if SB["m"][n] > 0])
    meta = dict(off=off, sidx=sidx, nvar=nvar, I=I, J=J, isE=isE, cnt=cnt, npair=npair)
    log(f"  SCS data: {A.shape[0]} rows x {nvar} vars, nnz {A.nnz}, psd blocks {cone['s']}")
    return dict(A=A, b=b, c=c), cone, meta


def unpack(x, SB, meta):
    X = {}
    for n in IRREPS:
        m = SB["m"][n]
        if m == 0:
            continue
        Xm = np.zeros((m, m)); sidx = meta["sidx"][n]; off = meta["off"][n]
        iu = np.triu_indices(m)
        vals = x[off + sidx[iu[1], iu[0]]]
        Xm[iu[0], iu[1]] = vals
        Xm = Xm + Xm.T
        Xm[np.diag_indices(m)] /= 2
        offd = iu[0] != iu[1]
        # off-diagonals were svec-scaled by sqrt2
        Xm2 = Xm.copy()
        mask = ~np.eye(m, dtype=bool)
        Xm2[mask] /= math.sqrt(2.0)
        X[n] = Xm2
    return X


def theta_prime(G, orbs, ov, eps=1e-5, max_iters=20000, log=print, time_limit=None, verbose=False, trace_scale=None, scs_kw=None):
    import scs
    t0 = time.time()
    N = G.shape[1]
    if trace_scale is None:
        trace_scale = float(N)
    SB = symmetry_basis(G, orbs)
    log(f"  symmetry basis: blocks {SB['m']} (sum d*m = {sum(DIMS[n]*SB['m'][n] for n in IRREPS)} = N {G.shape[1]}) t={time.time()-t0:.1f}s")
    data, cone, meta = build_scs(G, orbs, ov, SB, log, trace_scale=trace_scale)
    log(f"  build t={time.time()-t0:.1f}s; solving SCS eps={eps} (trace scale {trace_scale})")
    kw = dict(eps_abs=eps, eps_rel=eps, max_iters=max_iters, verbose=verbose, normalize=True, acceleration_lookback=10)
    if scs_kw:
        kw.update(scs_kw)
    if time_limit:
        kw["time_limit_secs"] = time_limit
    solver = scs.SCS(data, cone, **kw)
    sol = solver.solve()
    info = sol["info"]
    X = unpack(sol["x"] / trace_scale, SB, meta)
    val = -info["pobj"]; dval = -info["dobj"]
    meta["trace_scale"] = trace_scale
    log(f"  SCS: status {info['status']} iters {info['iter']} pobj {val:.6f} dobj {dval:.6f} res_pri {info['res_pri']:.2e} res_dual {info['res_dual']:.2e} gap {info['gap']:.2e} t={time.time()-t0:.1f}s")
    return dict(theta=val, theta_dual=dval, status=info["status"], iters=info["iter"], res_pri=info["res_pri"],
                res_dual=info["res_dual"], gap=info["gap"], time=time.time() - t0, X=X, SB=SB, meta=meta, y=sol["y"],
                solve_time=info.get("solve_time", 0.0))


def pair_orbit_of_all(G, I, J):
    """orbit index (into the representative arrays I,J) of every pair i<j of the graph."""
    N = G.shape[1]
    keys_rep = np.minimum(I, J).astype(np.int64) * N + np.maximum(I, J)
    II, JJ = np.triu_indices(N, 1)
    best = None
    for g in range(8):
        gi = G[g, II]; gj = G[g, JJ]
        k = np.minimum(gi, gj).astype(np.int64) * N + np.maximum(gi, gj)
        best = k if best is None else np.minimum(best, k)
    o = np.searchsorted(keys_rep, best)
    assert np.all(keys_rep[o] == best)
    return II, JJ, o


def dual_certificate(r, G, ov):
    """From the SCS dual multipliers build Z = lam*I - J - Y (full N x N; Y_ij = +y_E/(2|O|) on edges, -y_P/(2|O|)
    on non-edges, orbit-wise), make it PSD by adding delta*I (delta = -min eig if negative), and return the rigorous
    (modulo floating point) bound  theta' <= 1 + (lam' - 1)/(1 - eps)  where lam' = lam + delta and
    eps = max over non-edges of (Z_ij + 1)_+  (valid when eps < 1)."""
    meta = r["meta"]; y = r["y"]; N = G.shape[1]
    ts = meta.get("trace_scale", 1.0)
    isE = meta["isE"]; I = meta["I"]; J = meta["J"]; cnt = meta["cnt"]
    nz = int(isE.sum()) + 1; npos = int((~isE).sum())
    lam = y[0] * ts; yE = y[1:nz] * ts; yP = y[nz:nz + npos] * ts
    ymul = np.zeros(len(I)); ymul[isE] = yE; ymul[~isE] = -yP
    II, JJ, o = pair_orbit_of_all(G, I, J)
    Z = lam * np.eye(N) - np.ones((N, N))
    v = ymul[o] * (0.5 / cnt[o])
    Z[II, JJ] += v; Z[JJ, II] += v
    w = np.linalg.eigvalsh(Z)
    delta = max(0.0, -w.min())
    nonadj = ~ov & ~np.eye(N, dtype=bool)
    eps = max(0.0, float((Z[nonadj] + 1).max()))
    lam2 = lam + delta
    maxdiag = float(np.diag(Z).max() + delta)
    lam2 = max(lam2, maxdiag + 1)
    bound = 1 + (lam2 - 1) / (1 - eps) if eps < 1 else float("inf")
    return dict(lam=float(lam), min_eig=float(w.min()), eps_nonedge=eps, max_diag=maxdiag, bound=float(bound))


def theta_prime_cvxpy_full(ov, solver="CLARABEL"):
    """Plain full-matrix formulation (validation only, small N)."""
    import cvxpy as cp
    N = len(ov)
    B = cp.Variable((N, N), PSD=True)
    cons = [cp.trace(B) == 1, B >= 0]
    I, J = np.nonzero(np.triu(ov, 1))
    cons.append(B[I, J] == 0)
    prob = cp.Problem(cp.Maximize(cp.sum(B)), cons)
    prob.solve(solver=solver)
    return prob.value, B.value


def feasible_value(Bfull, ov):
    """Clean B (clip negatives, zero edges, symmetrise) and report 1'B1/trB and the min eigenvalue; if min eig >= -tiny
    this is (numerically) a feasible point, hence a lower bound on theta'."""
    Bc = np.maximum(Bfull, 0); Bc[ov] = 0; Bc = (Bc + Bc.T) / 2
    w = np.linalg.eigvalsh(Bc)
    return Bc.sum() / np.trace(Bc), w.min()


if __name__ == "__main__":
    from graph import build_nodes, d4_action, orbits, overlap_matrix
    s = 3.85
    P = build_nodes(s, 0.5, [0, 30, 60])
    G = d4_action(P, s); oid, orbs = orbits(G); ov = overlap_matrix(P)
    print("N", len(P), "orbits", len(orbs), "edges", ov.sum() // 2)
    SB = symmetry_basis(G, orbs)
    rng = np.random.default_rng(0)
    A0 = rng.standard_normal((len(P), len(P))); A0 = A0 + A0.T
    Ainv = sum(A0[np.ix_(G[g], G[g])] for g in range(8)) / 8
    for g in range(8):
        assert np.allclose(Ainv[np.ix_(G[g], G[g])], Ainv), "averaging wrong"
    blocks = {}
    for n in IRREPS:
        if SB["m"][n] == 0:
            continue
        for r in range(DIMS[n]):
            T1 = dense_T(SB, n, r)
            blk = T1.T @ Ainv @ T1
            if r == 0:
                blocks[n] = blk
            else:
                print(n, "row", r, "block equal to row 0:", np.allclose(blk, blocks[n], atol=1e-8))
    Brec = reconstruct_B(SB, blocks)
    print("reconstruction error", np.abs(Brec - Ainv).max())
    T_all = np.hstack([dense_T(SB, n, r) for n in IRREPS for r in range(DIMS[n]) if SB["m"][n] > 0])
    print("T orthogonal:", np.allclose(T_all.T @ T_all, np.eye(len(P)), atol=1e-8))
    r = theta_prime(G, orbs, ov, eps=1e-7)
    v, Bfull = theta_prime_cvxpy_full(ov)
    print("theta' reduced:", r["theta"], " full cvxpy:", v)
    B = reconstruct_B(SB, r["X"])
    print("B min", B.min(), "edge max", np.abs(B[ov]).max(), "tr", np.trace(B), "sum", B.sum(), "min eig", np.linalg.eigvalsh(B).min())
    from alpha import max_independent_set
    print("alpha", max_independent_set(ov)[0])
