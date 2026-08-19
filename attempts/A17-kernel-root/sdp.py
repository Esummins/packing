"""A17 — kernel SDP:  find M = sum_n sum_r T_nr X_n T_nr^T (D4-invariant), X_n psd, minimising lambda s.t.
    diag rows:  phi_i^T M phi_i  <= lambda - 1 - delta_d
    pair rows:  phi_i^T M psi_i  <= -1 - delta_p .

Patterns are dense (~130 atoms per placement), so a sparse-A conic form explodes (~2e5 nnz per row).
Instead: Burer-Monteiro factorisation per block (X_n = Y_n^T Y_n, full or near-full rank so the
parametrisation is de-facto exact) + L-BFGS on the preconditioned hinge^2 feasibility loss
    F(Y; lambda) = sum_i (relu(g_i)/n_i)^2 ,   g = K - (rhs) ,  n_i = |phi1_i| |phi2_i| ,
with an outer loop that walks lambda downward while F can be driven to ~0 (max violation <= tol).
Validated against cvxpy/Clarabel on small instances (validate_small: same lambda to ~1e-3).
"""
import math, time
import numpy as np


class KernelSDP:
    def __init__(self, sym, delta_pair=1e-3, delta_diag=0.0):
        self.sym = sym
        self.SB = sym["SB"]
        self.names = [n for n in self.SB["names"] if self.SB["m"][n] > 0]
        self.delta_pair = float(delta_pair)
        self.delta_diag = float(delta_diag)
        self.P1 = {n: [[] for _ in range(self.SB["dims"][n])] for n in self.names}
        self.P2 = {n: [[] for _ in range(self.SB["dims"][n])] for n in self.names}
        self.is_diag = []
        self.norms = []
        self.nrows = 0
        self._dense = None

    # ------------------------------------------------ rows
    def _project_rows(self, Phi1, Phi2):
        for n in self.names:
            for r in range(self.SB["dims"][n]):
                T = self.sym["Ts"][n][r]
                self.P1[n][r].append(np.asarray((Phi1 @ T).toarray() if hasattr(Phi1 @ T, "toarray") else Phi1 @ T))
                self.P2[n][r].append(np.asarray((Phi2 @ T).toarray() if hasattr(Phi2 @ T, "toarray") else Phi2 @ T))
        n1 = np.sqrt(np.asarray(Phi1.multiply(Phi1).sum(axis=1)).ravel())
        n2 = np.sqrt(np.asarray(Phi2.multiply(Phi2).sum(axis=1)).ravel())
        self.norms += list(n1 * n2)
        self._dense = None

    def add_diag_rows(self, Phi):
        self._project_rows(Phi, Phi)
        self.is_diag += [True] * Phi.shape[0]
        self.nrows += Phi.shape[0]

    def add_pair_rows(self, Phi1, Phi2):
        self._project_rows(Phi1, Phi2)
        self.is_diag += [False] * Phi1.shape[0]
        self.nrows += Phi1.shape[0]

    def drop_rows(self, keep_mask):
        """keep only rows with keep_mask True (row order = insertion order)."""
        keep = np.asarray(keep_mask, bool)
        D = self._stack()
        newP1 = {n: [[D["P1"][n][r][keep]] for r in range(self.SB["dims"][n])] for n in self.names}
        newP2 = {n: [[D["P2"][n][r][keep]] for r in range(self.SB["dims"][n])] for n in self.names}
        self.P1, self.P2 = newP1, newP2
        self.is_diag = list(np.array(self.is_diag)[keep])
        self.norms = list(np.array(self.norms)[keep])
        self.nrows = int(keep.sum())
        self._dense = None

    def _stack(self):
        if self._dense is None:
            self._dense = dict(
                P1={n: [np.vstack(self.P1[n][r]) for r in range(self.SB["dims"][n])] for n in self.names},
                P2={n: [np.vstack(self.P2[n][r]) for r in range(self.SB["dims"][n])] for n in self.names},
                isd=np.array(self.is_diag, bool), nrm=np.array(self.norms))
        return self._dense

    # ------------------------------------------------ factor handling
    def init_Y(self, rank=None, M0=None, rng=None, scale=1e-3):
        """Y blocks (r_n x m_n).  If M0 given (dense invariant M), factor its block projections."""
        rng = np.random.default_rng(0) if rng is None else rng
        Y = {}
        for n in self.names:
            m = self.SB["m"][n]
            r = m if rank is None else min(m, rank)
            if M0 is not None:
                d = self.SB["dims"][n]
                acc = 0
                for rr in range(d):
                    T = self.sym["Ts"][n][rr].toarray()
                    acc = acc + T.T @ M0 @ T
                Xn = acc / d
                w, U = np.linalg.eigh((Xn + Xn.T) / 2)
                w = np.maximum(w, 0.0)
                idx = np.argsort(-w)[:r]
                Y[n] = (np.sqrt(w[idx])[:, None] * U[:, idx].T)
                if Y[n].shape[0] < r:
                    Y[n] = np.vstack([Y[n], np.zeros((r - Y[n].shape[0], m))])
            else:
                Y[n] = scale * rng.standard_normal((r, m))
        return Y

    def X_of(self, Y):
        return {n: Y[n].T @ Y[n] for n in self.names}

    def get_M(self, Y):
        from features import reconstruct_M
        return reconstruct_M(self.sym, self.X_of(Y))

    def row_values(self, Y):
        D = self._stack()
        K = np.zeros(self.nrows)
        for n in self.names:
            Yn = Y[n]
            for r in range(self.SB["dims"][n]):
                U1 = D["P1"][n][r] @ Yn.T
                U2 = D["P2"][n][r] @ Yn.T
                K += np.einsum('ij,ij->i', U1, U2)
        return K

    def rhs(self, lam):
        D = self._stack()
        return np.where(D["isd"], lam - 1.0 - self.delta_diag, -1.0 - self.delta_pair)

    # ------------------------------------------------ feasibility solve at fixed lambda
    def solve_feas(self, Y, lam, maxiter=400, tol_viol=1e-7, log=None):
        from scipy.optimize import minimize
        D = self._stack()
        b = self.rhs(lam)
        wgt = 1.0 / np.maximum(D["nrm"], 1e-9) ** 2
        shapes = [(n, Y[n].shape) for n in self.names]
        sizes = [int(np.prod(sh)) for _, sh in shapes]

        def pack(Yd):
            return np.concatenate([Yd[n].ravel() for n, _ in shapes])

        def unpack(v):
            out = {}
            o = 0
            for (n, sh), sz in zip(shapes, sizes):
                out[n] = v[o:o + sz].reshape(sh)
                o += sz
            return out

        def fun(v):
            Yd = unpack(v)
            U1 = {}; U2 = {}
            K = np.zeros(self.nrows)
            for n in self.names:
                Yn = Yd[n]
                U1[n] = []; U2[n] = []
                for r in range(self.SB["dims"][n]):
                    u1 = D["P1"][n][r] @ Yn.T
                    u2 = D["P2"][n][r] @ Yn.T
                    U1[n].append(u1); U2[n].append(u2)
                    K += np.einsum('ij,ij->i', u1, u2)
            g = K - b
            act = g > 0
            c = np.where(act, wgt * g, 0.0)
            F = float((c * np.where(act, g, 0.0)).sum())
            grads = []
            for n, _ in shapes:
                Gn = 0
                for r in range(self.SB["dims"][n]):
                    Gn = Gn + (c[:, None] * U2[n][r]).T @ D["P1"][n][r] + (c[:, None] * U1[n][r]).T @ D["P2"][n][r]
                grads.append(2.0 * Gn)
            grad = np.concatenate([G.ravel() for G in grads])
            return F, grad

        res = minimize(fun, pack(Y), jac=True, method="L-BFGS-B",
                       options=dict(maxiter=maxiter, maxcor=8, ftol=1e-18, gtol=1e-14))
        Yn = unpack(res.x)
        K = self.row_values(Yn)
        g = K - b
        isd = D["isd"]
        gd = float(g[isd].max()) if isd.any() else 0.0
        gp = float(g[~isd].max()) if (~isd).any() else 0.0
        return Yn, float(max(0.0, g.max())), float(res.fun), int(res.nit), gd, gp

    # ------------------------------------------------ lambda descent
    def minimize_lambda(self, Y=None, lam0=None, step0=0.25, min_step=0.01, tol_viol=1e-6,
                        maxiter=400, time_limit=None, log=print, rank=None, M0=None, lam_floor=None):
        t0 = time.time()
        if Y is None:
            Y = self.init_Y(rank=rank, M0=M0)
        K = self.row_values(Y)
        b0 = self.rhs(0.0)
        D = self._stack()
        isd = D["isd"]
        if lam0 is None:
            lam0 = float(K[isd].max() + 1.0 + self.delta_diag + 0.05) if isd.any() else 2.0
        if lam_floor is not None:
            lam0 = max(lam0, lam_floor)
        lam = lam0
        # acceptance rule: pair-row residual must stay within half the delta_pair margin (the
        # certificate vs -1 still holds); diag-row residual is folded into the effective lambda.
        gp_ok = 0.5 * self.delta_pair

        def attempt(Ystart, lam_try):
            Yn, viol, F, nit, gd, gp = self.solve_feas(Ystart, lam_try, maxiter=maxiter, log=log)
            lam_eff = lam_try + max(0.0, gd) if gp <= gp_ok else None
            return Yn, lam_eff, gd, gp, nit

        Y, lam_eff, gd, gp, nit = attempt(Y, lam)
        log(f"    [sdp] start lam {lam:.4f}: gd {gd:+.2e} gp {gp:+.2e} ({nit} it, {time.time()-t0:.0f}s)")
        tries = 0
        while lam_eff is None and tries < 6:
            lam += max(0.2, 2 * gp)
            Y, lam_eff, gd, gp, nit = attempt(Y, lam)
            log(f"    [sdp] raise lam {lam:.4f}: gd {gd:+.2e} gp {gp:+.2e} ({nit} it)")
            tries += 1
        if lam_eff is None:
            log("    [sdp] WARNING: could not restore pair-row feasibility; returning last iterate")
            return dict(Y=Y, lam=float(lam + max(0.0, gd) + max(0.0, gp)), time=time.time() - t0)
        best = {n: Y[n].copy() for n in self.names}
        best_lam = lam_eff
        step = step0
        while step >= min_step:
            if time_limit and time.time() - t0 > time_limit:
                log("    [sdp] time limit")
                break
            if lam_floor is not None and best_lam <= lam_floor + 1e-9:
                break
            lam_try = best_lam - step
            if lam_floor is not None:
                lam_try = max(lam_try, lam_floor)
            Y, lam_eff, gd, gp, nit = attempt({n: best[n].copy() for n in self.names}, lam_try)
            if lam_eff is not None and lam_eff < best_lam - 1e-6:
                best = {n: Y[n].copy() for n in self.names}
                best_lam = lam_eff
                log(f"    [sdp] lam {lam_try:.4f} -> eff {lam_eff:.4f} accepted (gd {gd:+.1e} gp {gp:+.1e}, {nit} it, {time.time()-t0:.0f}s)")
            else:
                log(f"    [sdp] lam {lam_try:.4f} rejected (gd {gd:+.1e} gp {gp:+.1e}, {nit} it, {time.time()-t0:.0f}s)")
                step /= 2
        return dict(Y=best, lam=float(best_lam), time=time.time() - t0)


# ------------------------------------------------------------------ validation vs cvxpy
def validate_small(seed=0, log=print):
    from features import FeatureMap, build_symmetry, random_placements, d4_images_pt
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "A16-theta-casetree"))
    from graph import d4_images
    from oracle_pair import overlap_depth
    rng = np.random.default_rng(seed)
    s = 3.8
    reps = np.array([[1.0, 1.0], [1.0, 1.9], [0.7, 1.0], [1.4, 1.4], [1.0, 1.53]])
    A = []
    for x, y in reps:
        for q in d4_images_pt(x, y, s):
            if not any(abs(q[0] - r[0]) < 1e-9 and abs(q[1] - r[1]) < 1e-9 for r in A):
                A.append(q)
    A = np.array(A)
    w = np.full(len(A), 0.3)
    fm = FeatureMap(A, w, s)
    sym = build_symmetry(fm)
    log(f"validate_small: {len(A)} atoms, blocks {sym['SB']['m']}")
    P = random_placements(s, 12, rng)
    Pall = np.array([q for p in P for q in d4_images(tuple(p), s)])
    Phi_d = fm.phi(Pall)
    P2 = random_placements(s, 60, rng)
    pairs = []
    for i in range(len(P2)):
        for j in range(i + 1, len(P2)):
            if overlap_depth(P2[i], P2[j]) < 0:
                pairs.append((i, j))
    pairs = pairs[:15]
    p1 = []; p2 = []
    for i, j in pairs:
        for g in range(8):
            p1.append(d4_images(tuple(P2[i]), s)[g]); p2.append(d4_images(tuple(P2[j]), s)[g])
    Phi1 = fm.phi(np.array(p1)); Phi2 = fm.phi(np.array(p2))
    prob = KernelSDP(sym, delta_pair=1e-3)
    prob.add_diag_rows(Phi_d)
    prob.add_pair_rows(Phi1, Phi2)
    r = prob.minimize_lambda(step0=0.5, min_step=0.002, maxiter=600, log=log)
    import cvxpy as cp
    nf = fm.nf
    M = cp.Variable((nf, nf), PSD=True)
    lam = cp.Variable()
    cons = []
    Pd = Phi_d.toarray()
    for i in range(Pd.shape[0]):
        cons.append(cp.quad_form(Pd[i], M) <= lam - 1)
    B1 = Phi1.toarray(); B2 = Phi2.toarray()
    for i in range(B1.shape[0]):
        cons.append(B1[i] @ M @ B2[i] <= -1 - 1e-3)
    pr = cp.Problem(cp.Minimize(lam), cons)
    pr.solve(solver="CLARABEL")
    log(f"validate_small: BM lam = {r['lam']:.6f}  cvxpy lam = {pr.value:.6f}  (diff {r['lam']-pr.value:+.2e})")
    return r, pr.value


if __name__ == "__main__":
    validate_small()
