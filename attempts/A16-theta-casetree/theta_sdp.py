"""A16 — Schrijver / Lovasz-Schrijver theta-prime  theta'(G) = max{ 1'B1 : B psd, B >= 0, tr B = 1, B_ij = 0 (ij in E) }
block-diagonalised for an arbitrary symmetry subgroup H <= D4 of the node set (generalisation of A15's theta_sdp.py,
which was D4-only).  H = D4 (5 irreps, one 2-dim), or an elementary-abelian 2-subgroup (incl. the trivial group: then
there is one full N x N block and the formulation is the plain one).

Invariant B = sum_rho sum_{r<=d_rho} T_rho^(r) X_rho T_rho^(r)T, X_rho psd (m_rho x m_rho), T built orbit-wise from the
isotypic projectors P_{rs} = (d_rho/|H|) sum_g rho(g)_{rs} pi(g).  Constraints: one per pair-orbit under H.
"""
import math, time
import numpy as np
import scipy.sparse as sp


# ------------------------------------------------------------------ groups
def d4_rep_matrices():
    """rho[name][g] = matrix (d x d) of D4 element g = 2k + e  (f^e r^k), same enumeration as graph.d4_images."""
    R = np.array([[0., -1.], [1., 0.]]); F = np.array([[-1., 0.], [0., 1.]])
    out = {n: [] for n in ["A1", "A2", "B1", "B2", "E"]}
    for k in range(4):
        for e in range(2):
            M = np.linalg.matrix_power(F, e) @ np.linalg.matrix_power(R, k)
            out["E"].append(M)
            out["A1"].append(np.array([[1.]]))
            out["A2"].append(np.array([[(-1.) ** e]]))
            out["B1"].append(np.array([[(-1.) ** k]]))
            out["B2"].append(np.array([[(-1.) ** (k + e)]]))
    return out


def stabiliser(Gfull, keep):
    """indices g of D4 elements (rows of Gfull (8,N)) that map the kept node set onto itself."""
    keep = np.asarray(keep, bool)
    return [g for g in range(Gfull.shape[0]) if np.array_equal(keep[Gfull[g]], keep)]


def mult_table(Gsub):
    """Gsub (m, N) permutation arrays; returns table T[a,b] = index c with Gsub[c] = Gsub[a] o Gsub[b]."""
    m = Gsub.shape[0]
    T = -np.ones((m, m), dtype=int)
    for a in range(m):
        for b in range(m):
            comp = Gsub[a][Gsub[b]]
            for c in range(m):
                if np.array_equal(Gsub[c], comp):
                    T[a, b] = c
                    break
            assert T[a, b] >= 0, "not closed under composition"
    return T


def subgroup_rep(Gfull, gl, keep_idx):
    """Restrict the action of the subgroup H (element indices gl of D4) to the kept nodes and return
    (Gsub (|H|, n), rho dict, name).  If H = D4 -> the D4 irreps.  If every element has order <= 2 -> real characters.
    Otherwise (C4) fall back to the subgroup {e, r^2} (valid, weaker)."""
    N = Gfull.shape[1]
    idx = -np.ones(N, dtype=int); idx[keep_idx] = np.arange(len(keep_idx))
    Gsub = idx[Gfull[gl][:, keep_idx]]
    assert (Gsub >= 0).all()
    if len(gl) == 8:
        return Gsub, d4_rep_matrices(), "D4"
    T = mult_table(Gsub)
    m = len(gl)
    e = [a for a in range(m) if T[a, a] == a and all(T[a, b] == b for b in range(m))][0]
    if any(T[a, a] != e for a in range(m)):
        # contains an element of order 4: use {e, r^2} if present, else trivial
        sq = [T[a, a] for a in range(m)]
        r2 = [c for c in set(sq) if c != e]
        sel = [e] + r2[:1]
        return subgroup_rep(Gfull, [gl[a] for a in sel], keep_idx)
    # elementary abelian: enumerate characters
    import itertools
    chars = []
    for signs in itertools.product([1.0, -1.0], repeat=m):
        if signs[e] != 1.0:
            continue
        ok = all(signs[T[a, b]] == signs[a] * signs[b] for a in range(m) for b in range(m))
        if ok:
            chars.append(signs)
    assert len(chars) == m, (len(chars), m)
    rho = {f"X{k}": [np.array([[c[g]]]) for g in range(m)] for k, c in enumerate(chars)}
    return Gsub, rho, f"Z2^{int(round(math.log2(m)))}" if m > 1 else "C1"


def orbits(G):
    N = G.shape[1]
    oid = -np.ones(N, dtype=int)
    orbs = []
    for i in range(N):
        if oid[i] >= 0:
            continue
        mem = np.unique(G[:, i])
        oid[mem] = len(orbs)
        orbs.append(mem)
    return oid, orbs


# ------------------------------------------------------------------ symmetry basis
def symmetry_basis(G, orbs, rho):
    """For each orbit O and irrep rho: orthonormal V[rho][r] (n_O x m_rho(O)), r = 0..d-1.
    Returns dict with per-node sparse rows t[rho][r] (N, dmax) values, col[rho] (N, dmax) global column index (-1 = none),
    block sizes m[rho], names, dims."""
    names = list(rho.keys())
    dims = {n: rho[n][0].shape[0] for n in names}
    dmax = max(dims.values())
    H = G.shape[0]
    N = G.shape[1]
    t = {n: [np.zeros((N, dmax)) for _ in range(dims[n])] for n in names}
    col = {n: -np.ones((N, dmax), dtype=int) for n in names}
    m = {n: 0 for n in names}
    for O in orbs:
        nO = len(O)
        loc = {int(i): a for a, i in enumerate(O)}
        Pi = np.zeros((H, nO, nO))
        for g in range(H):
            for a, i in enumerate(O):
                Pi[g, loc[int(G[g, i])], a] = 1.0
        for n in names:
            d = dims[n]
            P = {}
            for r in range(d):
                for s_ in range(d):
                    P[(r, s_)] = (d / float(H)) * sum(rho[n][g][r, s_] * Pi[g] for g in range(H))
            P11 = P[(0, 0)]
            w, U = np.linalg.eigh((P11 + P11.T) / 2)
            V1 = U[:, w > 0.5]
            mO = V1.shape[1]
            if mO == 0:
                continue
            assert mO <= d, (n, mO, nO)
            Vs = [V1] + [P[(r, 0)] @ V1 for r in range(1, d)]
            for r in range(d):
                Vr = Vs[r]
                assert np.allclose(Vr.T @ Vr, np.eye(mO), atol=1e-8), (n, r, Vr.T @ Vr)
                t[n][r][O, :mO] = Vr
            col[n][O, :mO] = m[n] + np.arange(mO)[None, :]
            m[n] += mO
    return dict(t=t, col=col, m=m, names=names, dims=dims, dmax=dmax)


def dense_T(SB, n, r):
    N = SB["col"][n].shape[0]
    Tm = np.zeros((N, SB["m"][n]))
    for a in range(SB["dmax"]):
        ok = SB["col"][n][:, a] >= 0
        Tm[np.nonzero(ok)[0], SB["col"][n][ok, a]] = SB["t"][n][r][ok, a]
    return Tm


def reconstruct_B(SB, X):
    N = SB["col"][SB["names"][0]].shape[0]
    B = np.zeros((N, N))
    for n in SB["names"]:
        if SB["m"][n] == 0:
            continue
        for r in range(SB["dims"][n]):
            Tm = dense_T(SB, n, r)
            B += Tm @ X[n] @ Tm.T
    return B


def pair_orbits(G, ov, chunk=400):
    """Representatives of the orbits of unordered node pairs (i<j) under the group: (I, J, is_edge, orbit sizes)."""
    H, N = G.shape
    keys_all = []
    for i0 in range(0, N, chunk):
        i1 = min(N, i0 + chunk)
        I, J = np.meshgrid(np.arange(i0, i1), np.arange(N), indexing='ij')
        mask = J > I
        I = I[mask]; J = J[mask]
        best = None
        for g in range(H):
            gi = G[g, I]; gj = G[g, J]
            k = np.minimum(gi, gj).astype(np.int64) * N + np.maximum(gi, gj)
            best = k if best is None else np.minimum(best, k)
        keys_all.append(best)
    keys = np.concatenate(keys_all)
    uk, counts = np.unique(keys, return_counts=True)
    I = uk // N; J = uk % N
    return I.astype(int), J.astype(int), ov[I, J], counts


def svec_index(m):
    """SCS lower-triangular column-major svec ordering: index of (a,b) (vectorised)."""
    a, b = np.meshgrid(np.arange(m), np.arange(m), indexing='ij')
    lo = np.minimum(a, b); hi = np.maximum(a, b)       # column = lo, row = hi
    # number of entries in columns < lo: sum_{c<lo} (m - c) = lo*m - lo(lo-1)/2
    return (lo * m - lo * (lo - 1) // 2 + (hi - lo)).astype(np.int64)


def build_scs(G, orbs, ov, SB, log=print, trace_scale=1.0):
    names = SB["names"]; dims = SB["dims"]; dmax = SB["dmax"]
    N = G.shape[1]
    I, J, isE, cnt = pair_orbits(G, ov)
    log(f"  pair orbits: {len(I)} (edge orbits {isE.sum()}, non-edge {(~isE).sum()})")
    off = {}; nvar = 0; sidx = {}
    for n in names:
        m = SB["m"][n]
        off[n] = nvar; nvar += m * (m + 1) // 2; sidx[n] = svec_index(m) if m > 0 else None
    npair = len(I)
    rows_l, cols_l, vals_l = [], [], []
    for n in names:
        m = SB["m"][n]
        if m == 0:
            continue
        col = SB["col"][n]
        for a in range(dmax):
            for b in range(dmax):
                ca = col[I, a]; cb = col[J, b]
                ok = (ca >= 0) & (cb >= 0)
                if not ok.any():
                    continue
                v = np.zeros(npair)
                for r in range(dims[n]):
                    v += SB["t"][n][r][I, a] * SB["t"][n][r][J, b]
                ca_, cb_ = ca[ok], cb[ok]
                scale = np.where(ca_ == cb_, 1.0, 1.0 / math.sqrt(2.0))
                rows_l.append(np.nonzero(ok)[0]); cols_l.append(off[n] + sidx[n][ca_, cb_]); vals_l.append(v[ok] * scale)
    rows = np.concatenate(rows_l); cols = np.concatenate(cols_l); vals = np.concatenate(vals_l)
    Cpair = sp.csr_matrix((vals, (rows, cols)), shape=(npair, nvar))
    Cpair.sum_duplicates()
    tr_cols = []; tr_vals = []
    for n in names:
        m = SB["m"][n]
        if m == 0:
            continue
        d = dims[n]
        diag = np.array([sidx[n][a, a] for a in range(m)])
        tr_cols.append(off[n] + diag); tr_vals.append(np.full(m, float(d)))
    tc = np.concatenate(tr_cols); tv = np.concatenate(tr_vals)
    tr_row = sp.csr_matrix((tv, (np.zeros(len(tc), dtype=int), tc)), shape=(1, nvar))
    c = np.zeros(nvar)
    for n in names:
        m = SB["m"][n]
        if m == 0:
            continue
        for r in range(dims[n]):
            u = dense_T(SB, n, r).T @ np.ones(N)
            if np.abs(u).max() < 1e-12:
                continue
            M = np.outer(u, u)
            iu = np.triu_indices(m)
            vals_c = np.where(iu[0] == iu[1], M[iu], 2 * M[iu] / math.sqrt(2.0))
            np.add.at(c, off[n] + sidx[n][iu[0], iu[1]], -vals_c)
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
    cone = dict(z=A_zero.shape[0], l=A_pos.shape[0], s=[SB["m"][n] for n in names if SB["m"][n] > 0])
    meta = dict(off=off, sidx=sidx, nvar=nvar, I=I, J=J, isE=isE, cnt=cnt, npair=npair)
    log(f"  SCS data: {A.shape[0]} rows x {nvar} vars, nnz {A.nnz}, psd blocks {cone['s']}")
    return dict(A=A, b=b, c=c), cone, meta


def unpack(x, SB, meta):
    X = {}
    for n in SB["names"]:
        m = SB["m"][n]
        if m == 0:
            continue
        Xm = np.zeros((m, m)); sidx = meta["sidx"][n]; off = meta["off"][n]
        iu = np.triu_indices(m)
        vals = x[off + sidx[iu[1], iu[0]]]
        Xm[iu[0], iu[1]] = vals
        Xm = Xm + Xm.T
        Xm[np.diag_indices(m)] /= 2
        Xm2 = Xm.copy()
        mask = ~np.eye(m, dtype=bool)
        Xm2[mask] /= math.sqrt(2.0)
        X[n] = Xm2
    return X


def theta_prime(G, orbs, ov, rho, eps=1e-5, max_iters=20000, log=print, time_limit=None, verbose=False,
                trace_scale=None, scs_kw=None, warm=None):
    import scs
    t0 = time.time()
    N = G.shape[1]
    if trace_scale is None:
        trace_scale = float(N)
    SB = symmetry_basis(G, orbs, rho)
    log(f"  symmetry basis: blocks {SB['m']} (sum d*m = {sum(SB['dims'][n]*SB['m'][n] for n in SB['names'])} = N {N}) t={time.time()-t0:.1f}s")
    data, cone, meta = build_scs(G, orbs, ov, SB, log, trace_scale=trace_scale)
    log(f"  build t={time.time()-t0:.1f}s; solving SCS eps={eps} (trace scale {trace_scale})")
    kw = dict(eps_abs=eps, eps_rel=eps, max_iters=max_iters, verbose=verbose, normalize=True, acceleration_lookback=10)
    if scs_kw:
        kw.update(scs_kw)
    if time_limit:
        kw["time_limit_secs"] = time_limit
    solver = scs.SCS(data, cone, **kw)
    if warm is not None:
        sol = solver.solve(warm_start=True, x=warm["x"], y=warm["y"], s=warm["s"])
    else:
        sol = solver.solve()
    info = sol["info"]
    X = unpack(sol["x"] / trace_scale, SB, meta)
    val = -info["pobj"]; dval = -info["dobj"]
    meta["trace_scale"] = trace_scale
    log(f"  SCS: status {info['status']} iters {info['iter']} pobj {val:.6f} dobj {dval:.6f} res_pri {info['res_pri']:.2e} res_dual {info['res_dual']:.2e} gap {info['gap']:.2e} t={time.time()-t0:.1f}s")
    return dict(theta=val, theta_dual=dval, status=info["status"], iters=info["iter"], res_pri=info["res_pri"],
                res_dual=info["res_dual"], gap=info["gap"], time=time.time() - t0, X=X, SB=SB, meta=meta,
                y=sol["y"], x=sol["x"], s=sol["s"], solve_time=info.get("solve_time", 0.0))


def pair_orbit_of_all(G, I, J):
    H, N = G.shape
    keys_rep = np.minimum(I, J).astype(np.int64) * N + np.maximum(I, J)
    II, JJ = np.triu_indices(N, 1)
    best = None
    for g in range(H):
        gi = G[g, II]; gj = G[g, JJ]
        k = np.minimum(gi, gj).astype(np.int64) * N + np.maximum(gi, gj)
        best = k if best is None else np.minimum(best, k)
    o = np.searchsorted(keys_rep, best)
    assert np.all(keys_rep[o] == best)
    return II, JJ, o


def dual_certificate(r, G, ov, return_Z=False):
    """Z = lam*I - J - Y from the SCS dual multipliers (orbit-wise), made PSD by + delta*I, bound
    theta' <= 1 + (lam' - 1)/(1 - eps), eps = max over non-edges of (Z_ij + 1)_+ ."""
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
    out = dict(lam=float(lam), min_eig=float(w.min()), eps_nonedge=eps, max_diag=maxdiag, bound=float(bound))
    if return_Z:
        out["Z"] = Z
    return out


def feasible_value(Bfull, ov):
    Bc = np.maximum(Bfull, 0); Bc[ov] = 0; Bc = (Bc + Bc.T) / 2
    w = np.linalg.eigvalsh(Bc)
    return Bc.sum() / np.trace(Bc), w.min()


def theta_prime_cvxpy_full(ov, solver="CLARABEL"):
    import cvxpy as cp
    N = len(ov)
    B = cp.Variable((N, N), PSD=True)
    cons = [cp.trace(B) == 1, B >= 0]
    I, J = np.nonzero(np.triu(ov, 1))
    cons.append(B[I, J] == 0)
    prob = cp.Problem(cp.Maximize(cp.sum(B)), cons)
    prob.solve(solver=solver)
    return prob.value, B.value


if __name__ == "__main__":
    # validation: D4 reduction vs Z2 reduction vs trivial vs cvxpy full on a small graph, with a non-symmetric filter
    from graph import build_nodes, d4_action, overlap_matrix
    s = 3.85
    P = build_nodes(s, 0.5, [0, 30, 60])
    Gfull = d4_action(P, s); ovfull = overlap_matrix(P)
    N = len(P)
    # filter: drop nodes overlapping the corner square [0,1]^2 -> stabiliser = diagonal reflection
    keep = ~((np.abs(P[:, 0] - 0.5) < 0.999) & (np.abs(P[:, 1] - 0.5) < 0.999) & (P[:, 2] == 0))
    keep_idx = np.nonzero(keep)[0]
    for gl, label in [(stabiliser(Gfull, keep), "stab"), ([0], "trivial"), (list(range(8)), "D4 (root)")]:
        kidx = keep_idx if label != "D4 (root)" else np.arange(N)
        Gs, rho, name = subgroup_rep(Gfull, gl, kidx)
        oid, orbs = orbits(Gs); ov = ovfull[np.ix_(kidx, kidx)]
        r = theta_prime(Gs, orbs, ov, rho, eps=1e-8, max_iters=200000)
        B = reconstruct_B(r["SB"], r["X"])
        fv, me = feasible_value(B, ov)
        cert = dual_certificate(r, Gs, ov)
        v, _ = theta_prime_cvxpy_full(ov)
        print(f"{label}: group {name} |H|={len(gl)} n={len(kidx)} theta' reduced {r['theta']:.6f} feasible {fv:.6f} cert {cert['bound']:.6f} cvxpy {v:.6f}")
