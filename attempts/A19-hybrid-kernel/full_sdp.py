"""A19 -- FULL hybrid SDP in D4 pair-orbit coordinates (the production formulation; see notes SS1b).

S symmetric D4-invariant is parametrised by one value s_o per D4 orbit of (unordered) atom pairs
(diagonal orbits included). Then:
  PSD:   S = sum_o s_o A_o  >= 0            (one m x m cone; the map vec(S) = Bmap @ s is 1-sparse)
  sign:  s_o <= -w_p w_q  for every pair orbit NOT inside R x R   (simple variable bounds!)
  diag row (placement x):  sum_o c_o(x) s_o <= (lam - 1) m(x)^2,   c_o(x) = #orbit pairs in pattern
  pair row (disjoint x,y): sum_o d_o(x,y) s_o <= -(1+delta_p) m(x) m(y)
K(x,y) = a(x)^T S a(y) / (m(x) m(y)) for ALL x, y (diagonal included).
Automatic-(ii): for disjoint pairs not both meeting R, every cross pair (p,q) has s_o at most the
bound => K <= -1 with no row needed. R-meeting disjoint pairs get rows from the localised oracle.

Atom sets are COARSENED to m ~ 300-420 (greedy weighted merge in the fundamental domain) so the
PSD cone stays tractable for Clarabel.
"""
import math, os, sys, time
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))


# ---------------------------------------------------------------- atom coarsening
def fundamental_rep(x, y, s):
    """map (x,y) to the D4 fundamental domain x <= s/2, y <= s/2, x <= y (lexicographic min works too)."""
    from features import d4_images_pt
    best = None
    for q in d4_images_pt(x, y, s):
        t = (round(q[0], 12), round(q[1], 12))
        if best is None or t < best:
            best = t
    return best


def coarsen_atoms(A, w, s, r_merge, log=print):
    """greedy CLUSTER-SELECTION merge (atoms are never moved -- D4 closure exact, total mass
    preserved): on fundamental-domain orbit reps, the heaviest unused rep absorbs the orbit mass
    of all unused reps within r_merge. Returns (A2, w2) with per-atom weights."""
    from hybrid import d4_orbit_pts
    reps = {}
    for (x, y), wt in zip(A, w):
        f = fundamental_rep(x, y, s)
        if f not in reps:
            reps[f] = [0.0, len(d4_orbit_pts(f[0], f[1], s))]
        reps[f][0] += wt          # orbit mass accumulates: wt per atom, |orb| atoms per orbit rep
    pts = np.array(sorted(reps.keys()))
    orbmass = np.array([reps[tuple(p)][0] for p in pts])   # = per-atom w * |orb| (all images seen)
    orbsize = np.array([reps[tuple(p)][1] for p in pts])
    order = np.argsort(-orbmass)
    used = np.zeros(len(pts), bool)
    from scipy.spatial import cKDTree
    tree = cKDTree(pts)
    A2, w2 = [], []
    for i in order:
        if used[i]:
            continue
        nb = [j for j in tree.query_ball_point(pts[i], r_merge) if not used[j]]
        for j in nb:
            used[j] = True
        mass = orbmass[nb].sum()
        w_at = mass / orbsize[i]
        for q in d4_orbit_pts(pts[i][0], pts[i][1], s):
            A2.append(q); w2.append(w_at)
    A2 = np.array(A2); w2 = np.array(w2)
    log(f"  [coarsen] {len(A)} atoms -> {len(A2)} (r_merge {r_merge}); "
        f"mass {w.sum():.4f} -> {w2.sum():.4f}")
    return A2, w2


# ---------------------------------------------------------------- pair orbits over ALL atoms
def all_pair_orbits(fm):
    """orbit id for every unordered atom pair incl. diagonal: returns (poid (m,m) int32, n_orb,
    rep pair per orbit)."""
    m = fm.m
    G = fm.G_atoms
    poid = np.full((m, m), -1, dtype=np.int32)
    reps = []
    for i in range(m):
        for j in range(i, m):
            if poid[i, j] >= 0:
                continue
            o = len(reps)
            for g in range(8):
                a, b = int(G[g, i]), int(G[g, j])
                poid[a, b] = o
                poid[b, a] = o
            reps.append((i, j))
    return poid, len(reps), reps


class FullHybridSDP:
    def __init__(self, fm, region, delta_pair=1e-3, log=print, r_mask=None):
        """region: Region or None; r_mask: explicit bool atom mask (overrides region).
        The mask must be D4-closed (a union of atom orbits) -- checked."""
        self.fm = fm
        self.region = region
        self.delta_pair = float(delta_pair)
        self.log = log
        t0 = time.time()
        self.poid, self.n_po, self.po_reps = all_pair_orbits(fm)
        if r_mask is not None:
            in_R = np.asarray(r_mask, bool)
        else:
            in_R = region.contains(fm.A) if region is not None else np.zeros(fm.m, bool)
        for g in range(8):
            assert (in_R[fm.G_atoms[g]] == in_R).all(), "R atom set not D4-closed"
        self.in_R = in_R
        self.r_idx = np.nonzero(in_R)[0]
        # bounds per pair orbit: ub_o = -w_p w_q if (p != q and not both in R) else +inf
        ub = np.full(self.n_po, np.inf)
        for o, (i, j) in enumerate(self.po_reps):
            if i != j and not (in_R[i] and in_R[j]):
                ub[o] = -fm.w[i] * fm.w[j]
        self.ub = ub
        self.free_orbs = np.nonzero(~np.isfinite(ub))[0]
        # vec map: rows = m*m entries, cols = orbits
        m = fm.m
        ii, jj = np.meshgrid(np.arange(m), np.arange(m), indexing="ij")
        self.Bmap = sp.csr_matrix((np.ones(m * m), (np.arange(m * m),
                                                    self.poid.ravel())), shape=(m * m, self.n_po))
        log(f"  [full-sdp] m={m}, pair orbits {self.n_po} "
            f"({len(self.free_orbs)} free = R-block+diag), k=|R-atoms|={len(self.r_idx)} "
            f"({time.time()-t0:.1f}s)")
        # rows
        self.keys = set()
        self.diag_meta = []
        self.dr, self.dc, self.dv = [], [], []
        self.d_m2 = []
        self.pair_meta = []
        self.pr, self.pc, self.pv = [], [], []
        self.p_mm = []
        self._sol = None

    # ---------------- rows
    def add_diag(self, pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        if len(pts) == 0:
            return 0
        pat = self.fm.patterns(pts)
        cov = pat @ self.fm.w
        n_new = 0
        for i in range(len(pts)):
            nz = pat.indices[pat.indptr[i]:pat.indptr[i + 1]]
            if len(nz) == 0 or cov[i] <= 1e-9:
                continue
            key = ('d', self.fm.canon_key(nz))
            if key in self.keys:
                continue
            self.keys.add(key)
            r = len(self.diag_meta)
            self.diag_meta.append(pts[i].copy())
            cnt = {}
            for ai in range(len(nz)):
                o = self.poid[nz[ai], nz[ai]]
                cnt[o] = cnt.get(o, 0.0) + 1.0
                for aj in range(ai + 1, len(nz)):
                    o = self.poid[nz[ai], nz[aj]]
                    cnt[o] = cnt.get(o, 0.0) + 2.0
            for o, c in cnt.items():
                self.dr.append(r); self.dc.append(o); self.dv.append(c)
            self.d_m2.append(float(cov[i]) ** 2)
            n_new += 1
        return n_new

    def add_pairs(self, X, Y, only_R_meeting=True):
        X = np.atleast_2d(np.asarray(X, float)); Y = np.atleast_2d(np.asarray(Y, float))
        if len(X) == 0:
            return 0
        pat1 = self.fm.patterns(X); pat2 = self.fm.patterns(Y)
        cov1 = pat1 @ self.fm.w; cov2 = pat2 @ self.fm.w
        n_new = 0
        for i in range(len(X)):
            nz1 = pat1.indices[pat1.indptr[i]:pat1.indptr[i + 1]]
            nz2 = pat2.indices[pat2.indptr[i]:pat2.indptr[i + 1]]
            if len(nz1) == 0 or len(nz2) == 0 or cov1[i] <= 1e-9 or cov2[i] <= 1e-9:
                continue
            if only_R_meeting and not (self.in_R[nz1].any() and self.in_R[nz2].any()):
                continue
            key = ('p', self.fm.canon_key_pair(nz1, nz2))
            if key in self.keys:
                continue
            self.keys.add(key)
            r = len(self.pair_meta)
            self.pair_meta.append((X[i].copy(), Y[i].copy()))
            cnt = {}
            for p in nz1:
                row = self.poid[p]
                for q in nz2:
                    o = row[q]
                    cnt[o] = cnt.get(o, 0.0) + 1.0
            for o, c in cnt.items():
                self.pr.append(r); self.pc.append(o); self.pv.append(c)
            self.p_mm.append(float(cov1[i]) * float(cov2[i]))
            n_new += 1
        return n_new

    # ---------------- solve
    def solve(self, solver="CLARABEL", verbose=False, warm=None, sign_everywhere=False, **kw):
        import cvxpy as cp
        m = self.fm.m
        sv = cp.Variable(self.n_po)
        lam = cp.Variable()
        fin = np.isfinite(self.ub)
        if sign_everywhere:
            # automatic-class reference: bound EVERY off-diagonal orbit (R included)
            ub2 = self.ub.copy()
            for o, (i, j) in enumerate(self.po_reps):
                if i != j:
                    ub2[o] = -self.fm.w[i] * self.fm.w[j]
            fin2 = np.isfinite(ub2)
            cons = [sv[np.nonzero(fin2)[0]] <= ub2[fin2]]
        else:
            cons = [sv[np.nonzero(fin)[0]] <= self.ub[fin]]
        Smat = cp.reshape(self.Bmap @ sv, (m, m), order="C")
        cons.append(Smat >> 0)
        nd = len(self.diag_meta)
        if nd:
            Rd = sp.csr_matrix((self.dv, (self.dr, self.dc)), shape=(nd, self.n_po))
            m2 = np.array(self.d_m2)
            cons.append(Rd @ sv <= (lam - 1.0) * m2)
        npr = len(self.pair_meta)
        if npr and not sign_everywhere:
            Rp = sp.csr_matrix((self.pv, (self.pr, self.pc)), shape=(npr, self.n_po))
            mm = np.array(self.p_mm)
            cons.append(Rp @ sv <= -(1.0 + self.delta_pair) * mm)
        prob = cp.Problem(cp.Minimize(lam), cons)
        t0 = time.time()
        prob.solve(solver=solver, verbose=verbose, **kw)
        if prob.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(f"solver status {prob.status}")
        s_val = np.array(sv.value)
        self._sol = s_val
        return dict(lam=float(lam.value), s=s_val, status=prob.status, time=time.time() - t0)

    def dense_S(self, s_val=None):
        s_val = self._sol if s_val is None else s_val
        m = self.fm.m
        return np.asarray((self.Bmap @ s_val)).reshape(m, m)

    def dense_M(self, s_val=None):
        S = self.dense_S(s_val)
        w = self.fm.w
        m = self.fm.m
        M = np.zeros((m + 1, m + 1))
        M[0, 0] = 1.0
        M[0, 1:] = -w
        M[1:, 0] = -w
        M[1:, 1:] = S + np.outer(w, w)
        return M

    def kernel(self, s_val=None):
        return FullKernel(self, self.dense_S(s_val))


class FullKernel:
    """K(x,y) = a(x)^T S a(y)/(m(x)m(y)); kdiag + u_single shims for A17 oracles."""
    def __init__(self, fs, S):
        self.fs = fs
        self.fm = fs.fm
        self.S = np.asarray(S)

    def kdiag(self, P):
        pat = self.fm.patterns(np.asarray(P, float).reshape(-1, 3))
        mv = pat @ self.fm.w
        Q = pat @ self.S          # dense (n, m)
        q = np.asarray(pat.multiply(Q).sum(axis=1)).ravel()
        return np.where(mv > 0, q / np.maximum(mv, 1e-300) ** 2, np.inf)

    def u_single(self, x):
        v = float(self.kdiag(np.asarray(x, float)[None])[0])
        return np.array([math.sqrt(max(v, 0.0))])

    def kpair(self, X, Y):
        pat1 = self.fm.patterns(np.asarray(X, float).reshape(-1, 3))
        pat2 = self.fm.patterns(np.asarray(Y, float).reshape(-1, 3))
        m1 = pat1 @ self.fm.w; m2 = pat2 @ self.fm.w
        Q = pat1 @ self.S
        cross = np.asarray(pat2.multiply(Q).sum(axis=1)).ravel()
        return cross / np.maximum(m1 * m2, 1e-300)

    def meets_R(self, P):
        pat = self.fm.patterns(np.asarray(P, float).reshape(-1, 3))
        if len(self.fs.r_idx) == 0:
            return np.zeros(pat.shape[0], bool)
        return np.asarray(pat[:, self.fs.r_idx].sum(axis=1)).ravel() > 0
