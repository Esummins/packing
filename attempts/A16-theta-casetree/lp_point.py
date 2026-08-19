"""A15 — point-clique LP fractional packing number on a finite placement set.
   nu*_G = max sum x_Q  s.t.  sum_{Q : p in int Q} x_Q <= 1 for all points p,  x >= 0.
Row generation: start with a coarse grid of points, add over-covered points of a fine evaluation grid
(+ pattern search) until max coverage <= 1 + tol.  HiGHS via highspy (LP kept warm by re-solving; small).
"""
import math, time
import numpy as np
import scipy.sparse as sp
import highspy


def coverage_matrix(P, pts, margin=1e-9):
    """Sparse (n_pts, N) 0/1 matrix: point p strictly inside placement Q (|u|,|v| < 1/2 - margin)."""
    P = np.asarray(P, float); pts = np.asarray(pts, float)
    rows = []; cols = []
    c, s_ = np.cos(P[:, 2]), np.sin(P[:, 2])
    chunk = 2000
    for a in range(0, len(pts), chunk):
        pp = pts[a:a + chunk]
        dx = pp[:, None, 0] - P[None, :, 0]
        dy = pp[:, None, 1] - P[None, :, 1]
        u = c[None, :] * dx + s_[None, :] * dy
        v = -s_[None, :] * dx + c[None, :] * dy
        m = (np.abs(u) < 0.5 - margin) & (np.abs(v) < 0.5 - margin)
        r, cc = np.nonzero(m)
        rows.append(r + a); cols.append(cc)
    rows = np.concatenate(rows); cols = np.concatenate(cols)
    return sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(pts), len(P)))


def coverage_at(P, x, pts, margin=1e-9):
    """coverage function sum_{Q ∋ p} x_Q on points (vectorised over support of x)."""
    sup = np.nonzero(x > 1e-12)[0]
    if len(sup) == 0:
        return np.zeros(len(pts))
    A = coverage_matrix(P[sup], pts, margin)
    return A @ x[sup]


class LPModel:
    """persistent HiGHS model  max 1^T x  s.t. A x <= 1, x >= 0;  rows appended incrementally (dual simplex stays warm)."""

    def __init__(self, A, N, time_limit=600.0):
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", False)
        self.h.setOptionValue("time_limit", float(time_limit))
        self.N = N
        inf = highspy.kHighsInf
        lp = highspy.HighsLp()
        lp.num_col_ = N; lp.num_row_ = A.shape[0]
        lp.col_cost_ = -np.ones(N); lp.col_lower_ = np.zeros(N); lp.col_upper_ = np.full(N, inf)
        lp.row_lower_ = np.full(A.shape[0], -inf); lp.row_upper_ = np.ones(A.shape[0])
        Ac = A.tocsc()
        lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        lp.a_matrix_.start_ = Ac.indptr; lp.a_matrix_.index_ = Ac.indices; lp.a_matrix_.value_ = Ac.data
        self.h.passModel(lp)
        self.nrows = A.shape[0]

    def add_rows(self, Anew):
        Ar = Anew.tocsr()
        m = Ar.shape[0]
        inf = highspy.kHighsInf
        self.h.addRows(m, np.full(m, -inf), np.ones(m), Ar.nnz, Ar.indptr, Ar.indices, Ar.data)
        self.nrows += m

    def solve(self):
        self.h.run()
        st = self.h.getModelStatus()
        sol = self.h.getSolution()
        x = np.array(sol.col_value); y = -np.array(sol.row_dual)
        return -self.h.getInfo().objective_function_value, x, y, self.h.modelStatusToString(st)


def solve_lp(A, N):
    """max 1^T x s.t. A x <= 1, x >= 0 (A csr)."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_ = N; lp.num_row_ = A.shape[0]
    lp.col_cost_ = -np.ones(N); lp.col_lower_ = np.zeros(N); lp.col_upper_ = np.full(N, inf)
    lp.row_lower_ = np.full(A.shape[0], -inf); lp.row_upper_ = np.ones(A.shape[0])
    Ac = A.tocsc()
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = Ac.indptr; lp.a_matrix_.index_ = Ac.indices; lp.a_matrix_.value_ = Ac.data
    h.passModel(lp)
    h.run()
    st = h.getModelStatus()
    sol = h.getSolution()
    x = np.array(sol.col_value); y = -np.array(sol.row_dual)
    return -h.getInfo().objective_function_value, x, y, h.modelStatusToString(st)


def arrangement_vertices(P, x, eps=2e-5, xmin=1e-4, max_sup=400, max_pts=300000, seed=0):
    """Intersection points of the edges of the support squares (+ the corners), each perturbed in 8 directions
    by eps: candidate points for the maximum of the coverage function (cells of the arrangement).
    Support restricted to the max_sup heaviest placements with x > xmin; at most max_pts vertices (random subsample)."""
    from graph import corners
    sup = np.nonzero(x > xmin)[0]
    if len(sup) > max_sup:
        sup = sup[np.argsort(-x[sup])[:max_sup]]
    C = corners(P[sup])                       # (k,4,2)
    A = C.reshape(-1, 2); B = np.roll(C, -1, axis=1).reshape(-1, 2)   # segments A->B
    m = len(A)
    d = B - A
    # pairwise intersection of segments i<j
    I, J = np.triu_indices(m, 1)
    # exclude same-square pairs
    same = (I // 4) == (J // 4)
    I, J = I[~same], J[~same]
    pts = []
    for a in range(0, len(I), 200000):
        i = I[a:a + 200000]; j = J[a:a + 200000]
        r = d[i]; q = d[j]; w = A[j] - A[i]
        den = r[:, 0] * q[:, 1] - r[:, 1] * q[:, 0]
        ok = np.abs(den) > 1e-12
        t = (w[:, 0] * q[:, 1] - w[:, 1] * q[:, 0]) / np.where(ok, den, 1)
        u = (w[:, 0] * r[:, 1] - w[:, 1] * r[:, 0]) / np.where(ok, den, 1)
        ok &= (t > -1e-9) & (t < 1 + 1e-9) & (u > -1e-9) & (u < 1 + 1e-9)
        pts.append(A[i[ok]] + t[ok, None] * r[ok])
    V = np.vstack(pts + [A])
    if len(V) > max_pts:
        V = V[np.random.default_rng(seed).choice(len(V), max_pts, replace=False)]
    dirs = np.array([[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]], float) * eps
    return (V[:, None, :] + dirs[None]).reshape(-1, 2)


def nu_point_lp(P, s, grid0=0.05, fine=0.005, tol=1e-6, max_it=60, log=print, init_pts=None, time_limit=None):
    P = np.asarray(P, float); N = len(P)
    g = np.arange(grid0 / 2, s, grid0)
    pts = np.array([(a, b) for a in g for b in g])
    if init_pts is not None and len(init_pts):
        pts = np.vstack([pts, np.asarray(init_pts, float).reshape(-1, 2)])
    A = coverage_matrix(P, pts)
    # drop points covering nothing
    keep = np.asarray(A.sum(1)).ravel() > 0
    pts = pts[keep]; A = A[keep]
    gf = np.arange(fine / 2, s, fine)
    FX, FY = np.meshgrid(gf, gf, indexing='ij')
    fpts = np.stack([FX.ravel(), FY.ravel()], 1)
    t0 = time.time()
    hist = []
    M = LPModel(A, N)
    for it in range(max_it):
        val, x, y, st = M.solve()
        if time_limit is not None and time.time() - t0 > time_limit:
            log(f"  LP: time limit {time_limit}s reached at it {it}")
            cov = coverage_at(P, x, fpts); mc = float(cov.max()); hist.append((it, val, mc, A.shape[0]))
            break
        cov = coverage_at(P, x, fpts)
        av = arrangement_vertices(P, x)
        cova = coverage_at(P, x, av)
        mc = max(cov.max(), cova.max())
        hist.append((it, val, mc, A.shape[0]))
        log(f"  LP it {it}: nu={val:.6f} rows={A.shape[0]} maxcov grid={cov.max():.6f} arr={cova.max():.6f} t={time.time()-t0:.1f}s [{st}]")
        if mc <= 1 + tol:
            break
        bad = np.nonzero(cov > 1 + tol)[0]
        # take up to 1500 worst + local refinement around the worst 200
        order = bad[np.argsort(-cov[bad])]
        new = fpts[order[:1500]]
        ref = []
        for p in fpts[order[:200]]:
            best, bp = cov[order[0]] if False else None, None
            q = p.copy(); cur = coverage_at(P, x, q[None])[0]; step = fine / 2
            for _ in range(6):
                cand = q[None] + np.array([[step, 0], [-step, 0], [0, step], [0, -step], [step, step], [-step, -step], [step, -step], [-step, step]])
                cv = coverage_at(P, x, cand)
                k = int(np.argmax(cv))
                if cv[k] > cur + 1e-12:
                    q = cand[k]; cur = cv[k]
                else:
                    step /= 2
            ref.append(q)
        bada = np.nonzero(cova > 1 + tol)[0]
        bada = bada[np.argsort(-cova[bada])][:3000]
        new = np.vstack([new, np.array(ref).reshape(-1, 2), av[bada]])
        Anew = coverage_matrix(P, new)
        M.add_rows(Anew)
        A = sp.vstack([A, Anew]).tocsr(); pts = np.vstack([pts, new])
    return dict(nu=val, maxcov=float(mc), nu_lb=val / max(mc, 1.0), x=x, n_points=A.shape[0], hist=hist, time=time.time() - t0)


if __name__ == "__main__":
    import sys
    from graph import build_nodes, DEG
    s = float(sys.argv[1]) if len(sys.argv) > 1 else 3.85
    P = build_nodes(s, 0.2, np.arange(0, 90, 10))
    r = nu_point_lp(P, s)
    print(r['nu'], r['maxcov'], r['n_points'], r['time'])
