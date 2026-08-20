"""A19 -- hybrid kernel class: D = diag(g) + F, F supported on R-atom pairs (see notes.md SS1).

Convex SDP (cvxpy/Clarabel): min lambda s.t.
  diag rows:  sum_{p in x} g_p + a_R(x)^T F a_R(x) <= lambda * m(x)^2
  pair rows:  a_R(x)^T F a_R(y) <= -delta_p * m(x) m(y)     (disjoint, both meeting R)
  PSD:        Z_R = [[diag(g_R)+F, w_R],[w_R^T, 1 - sum_N w_p^2/g_p]] >= 0,  g_N > 0.
D4: g per atom orbit, F = sum_o f_o A_o over R-pair orbits.
"""
import math, os, sys, time
import numpy as np
import scipy.sparse as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A17-kernel-root"))
sys.path.insert(0, os.path.join(HERE, "..", "A18-restricted-kernel"))


# ---------------------------------------------------------------- enriched atom sets
def d4_orbit_pts(x, y, s, tol=1e-9):
    from features import d4_images_pt
    imgs = []
    for q in d4_images_pt(x, y, s):
        if not any(abs(q[0] - r[0]) < tol and abs(q[1] - r[1]) < tol for r in imgs):
            imgs.append(q)
    return imgs


def enrich_atoms(A, w, s, reps, w_new=0.0, min_dist=1e-6):
    """append the D4 orbits of new atom representatives (weight w_new, default 0)."""
    from scipy.spatial import cKDTree
    A = np.asarray(A, float); w = np.asarray(w, float)
    newA = []
    tree = cKDTree(A)
    for x, y in reps:
        for q in d4_orbit_pts(x, y, s):
            if tree.query(q)[0] < min_dist:
                continue
            if newA and min((q[0]-a[0])**2 + (q[1]-a[1])**2 for a in newA) < min_dist**2:
                continue
            newA.append(q)
    if not newA:
        return A, w, 0
    A2 = np.vstack([A, np.array(newA)])
    w2 = np.concatenate([w, np.full(len(newA), w_new)])
    return A2, w2, len(newA)


# ---------------------------------------------------------------- region R
class Region:
    """union of axis boxes [x0,x1]x[y0,y1], D4-symmetrised at construction."""
    def __init__(self, boxes, s):
        from features import d4_images_pt
        self.s = float(s)
        full = []
        for (x0, x1, y0, y1) in boxes:
            corners = [(x0, y0), (x1, y1)]
            for g in range(8):
                pts = [d4_images_pt(x, y, s)[g] for x, y in corners]
                xs = sorted(p[0] for p in pts); ys = sorted(p[1] for p in pts)
                b = (xs[0], xs[1], ys[0], ys[1])
                if not any(all(abs(b[i]-c[i]) < 1e-9 for i in range(4)) for c in full):
                    full.append(b)
        self.boxes = full

    def contains(self, pts):
        pts = np.atleast_2d(np.asarray(pts, float))
        out = np.zeros(len(pts), bool)
        for (x0, x1, y0, y1) in self.boxes:
            out |= (pts[:, 0] >= x0) & (pts[:, 0] <= x1) & (pts[:, 1] >= y0) & (pts[:, 1] <= y1)
        return out

    def bounding_radius(self):
        """max distance of any box point from the container centre."""
        c = self.s / 2.0
        r = 0.0
        for (x0, x1, y0, y1) in self.boxes:
            for x in (x0, x1):
                for y in (y0, y1):
                    r = max(r, math.hypot(x - c, y - c))
        return r


# ---------------------------------------------------------------- orbit structures
def atom_orbits(fm):
    m = fm.m
    oid = np.full(m, -1, dtype=int)
    orbs = []
    for i in range(m):
        if oid[i] >= 0:
            continue
        img = np.unique(fm.G_atoms[:, i])
        for j in img:
            oid[j] = len(orbs)
        orbs.append(img)
    return oid, orbs


def rpair_orbits(fm, r_idx):
    """D4 orbits of unordered R-atom pairs (i<j, global indices in r_idx).
    Returns pair_oid (k,k) int array (-1 off-support/diag), n_orb, and per-orbit pair lists."""
    k = len(r_idx)
    pos = {int(a): i for i, a in enumerate(r_idx)}
    pair_oid = np.full((k, k), -1, dtype=np.int32)
    orb_pairs = []
    for i in range(k):
        for j in range(i + 1, k):
            if pair_oid[i, j] >= 0:
                continue
            o = len(orb_pairs)
            members = set()
            for g in range(8):
                gi = pos[int(fm.G_atoms[g, r_idx[i]])]
                gj = pos[int(fm.G_atoms[g, r_idx[j]])]
                members.add((min(gi, gj), max(gi, gj)))
            for (a, b) in members:
                pair_oid[a, b] = o
                pair_oid[b, a] = o
            orb_pairs.append(sorted(members))
    return pair_oid, len(orb_pairs), orb_pairs


# ---------------------------------------------------------------- the SDP
class HybridSDP:
    def __init__(self, fm, region, delta_pair=1e-3, psd_eps=0.0, r_mask=None):
        self.fm = fm
        self.region = region
        self.delta_pair = float(delta_pair)
        self.psd_eps = float(psd_eps)
        self.oid, self.orbs = atom_orbits(fm)
        self.n_orb = len(self.orbs)
        self.w_orb = np.array([fm.w[o[0]] for o in self.orbs])
        self.size_orb = np.array([len(o) for o in self.orbs])
        if r_mask is not None:
            in_R = np.asarray(r_mask, bool)
        else:
            in_R = region.contains(fm.A) if region is not None else np.zeros(fm.m, bool)
        # R must be a union of orbits: an orbit is in R iff ALL members are (D4-closed R => equal)
        orb_in = np.zeros(self.n_orb, bool)
        for o, mem in enumerate(self.orbs):
            flags = in_R[mem]
            if flags.any() and not flags.all():
                raise ValueError(f"orbit {o} straddles R (region not D4-closed?)")
            orb_in[o] = flags.all() and len(mem) > 0
        self.orb_in_R = orb_in
        self.r_idx = np.nonzero(orb_in[self.oid])[0].astype(int)     # global indices of R-atoms
        self.k = len(self.r_idx)
        self.rpos = -np.ones(fm.m, dtype=int)
        self.rpos[self.r_idx] = np.arange(self.k)
        if self.k:
            self.pair_oid, self.n_forb, self.orb_pairs = rpair_orbits(fm, self.r_idx)
            # basis matrix: vec(F) (k*k) = Bas @ f  (each orbit contributes 1 at both (i,j),(j,i))
            rows, cols = [], []
            for o, mem in enumerate(self.orb_pairs):
                for (i, j) in mem:
                    rows += [i * self.k + j, j * self.k + i]
                    cols += [o, o]
            self.Bas = sp.csc_matrix((np.ones(len(rows)), (rows, cols)),
                                     shape=(self.k * self.k, self.n_forb))
        else:
            self.pair_oid, self.n_forb, self.orb_pairs, self.Bas = None, 0, [], None
        # rows
        self.keys = set()
        self.diag_meta = []        # placements
        self.dG_r, self.dG_c, self.dG_v = [], [], []   # sparse triplets rows x n_orb (atom counts)
        self.dF_r, self.dF_c, self.dF_v = [], [], []   # rows x n_forb
        self.d_m2 = []
        self.pair_meta = []        # (x, y)
        self.pF_r, self.pF_c, self.pF_v = [], [], []
        self.p_mm = []

    # ---------------- rows
    def _pattern_orb_counts(self, nz):
        cnt = {}
        for p in nz:
            o = self.oid[p]
            cnt[o] = cnt.get(o, 0) + 1
        return cnt

    def _quad_forb_counts(self, nzR):
        """coeffs of f_o in a_R^T F a_R = sum over unordered pairs in pattern: 2*f_o each."""
        cnt = {}
        rp = self.rpos[nzR]
        for ii in range(len(rp)):
            for jj in range(ii + 1, len(rp)):
                o = self.pair_oid[rp[ii], rp[jj]]
                if o >= 0:
                    cnt[o] = cnt.get(o, 0) + 2.0
        return cnt

    def _cross_forb_counts(self, nzR1, nzR2):
        """coeffs of f_o in a_R(x)^T F a_R(y) (patterns disjoint)."""
        cnt = {}
        r1 = self.rpos[nzR1]; r2 = self.rpos[nzR2]
        for i in r1:
            for j in r2:
                o = self.pair_oid[i, j]
                if o >= 0:
                    cnt[o] = cnt.get(o, 0) + 1.0
        return cnt

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
            for o, c in self._pattern_orb_counts(nz).items():
                self.dG_r.append(r); self.dG_c.append(o); self.dG_v.append(float(c))
            nzR = nz[self.rpos[nz] >= 0]
            if len(nzR) >= 2:
                for o, c in self._quad_forb_counts(nzR).items():
                    self.dF_r.append(r); self.dF_c.append(o); self.dF_v.append(c)
            self.d_m2.append(float(cov[i]) ** 2)
            n_new += 1
        return n_new

    def add_pairs(self, X, Y):
        X = np.atleast_2d(np.asarray(X, float)); Y = np.atleast_2d(np.asarray(Y, float))
        if len(X) == 0:
            return 0
        pat1 = self.fm.patterns(X); pat2 = self.fm.patterns(Y)
        cov1 = pat1 @ self.fm.w; cov2 = pat2 @ self.fm.w
        n_new = 0
        for i in range(len(X)):
            nz1 = pat1.indices[pat1.indptr[i]:pat1.indptr[i + 1]]
            nz2 = pat2.indices[pat2.indptr[i]:pat2.indptr[i + 1]]
            nzR1 = nz1[self.rpos[nz1] >= 0]; nzR2 = nz2[self.rpos[nz2] >= 0]
            if len(nzR1) == 0 or len(nzR2) == 0:
                continue                      # automatic
            if cov1[i] <= 1e-9 or cov2[i] <= 1e-9:
                continue
            cnt = self._cross_forb_counts(nzR1, nzR2)
            if not cnt:
                continue
            key = ('p', self.fm.canon_key_pair(nz1, nz2))
            if key in self.keys:
                continue
            self.keys.add(key)
            r = len(self.pair_meta)
            self.pair_meta.append((X[i].copy(), Y[i].copy()))
            for o, c in cnt.items():
                self.pF_r.append(r); self.pF_c.append(o); self.pF_v.append(c)
            self.p_mm.append(float(cov1[i]) * float(cov2[i]))
            n_new += 1
        return n_new

    # ---------------- solve
    def solve(self, solver="auto", verbose=False, lam_ub=None, allow_F=True, **kw):
        import cvxpy as cp
        nd = len(self.diag_meta); npair = len(self.pair_meta)
        g = cp.Variable(self.n_orb)
        lam = cp.Variable()
        use_F = allow_F and self.n_forb > 0
        f = cp.Variable(self.n_forb) if use_F else None
        cons = [g >= 1e-9]
        # PSD via Schur: t_o >= w_o^2/g_o per NON-R orbit; Z_R psd
        N_orbs = np.nonzero(~self.orb_in_R)[0]
        R_orbs = np.nonzero(self.orb_in_R)[0]
        wN = self.w_orb[N_orbs]; szN = self.size_orb[N_orbs].astype(float)
        pos = wN > 0
        if pos.any():
            t = cp.Variable(int(pos.sum()))
            cons.append(t >= cp.multiply(wN[pos] ** 2, cp.inv_pos(g[N_orbs[pos]])))
            tail = 1.0 - szN[pos] @ t
        else:
            tail = cp.Constant(1.0)
        # zero-weight non-R orbits: g >= 0 suffices (already), no coupling
        if self.k:
            gR_atom = g[self.oid[self.r_idx]]
            if use_F:
                Fmat = cp.reshape(self.Bas @ f, (self.k, self.k), order="C")
            else:
                Fmat = np.zeros((self.k, self.k))
            wR = self.fm.w[self.r_idx]
            Z = cp.bmat([[cp.diag(gR_atom) + Fmat, wR.reshape(-1, 1)],
                         [wR.reshape(1, -1), cp.reshape(tail, (1, 1), order="C")]])
            cons.append(Z >> self.psd_eps * np.eye(self.k + 1))
        else:
            cons.append(tail >= self.psd_eps)
        # rows
        if nd:
            Gc = sp.csr_matrix((self.dG_v, (self.dG_r, self.dG_c)), shape=(nd, self.n_orb))
            m2 = np.array(self.d_m2)
            lhs = Gc @ g
            if use_F and self.dF_r:
                Fq = sp.csr_matrix((self.dF_v, (self.dF_r, self.dF_c)), shape=(nd, self.n_forb))
                lhs = lhs + Fq @ f
            cons.append(lhs <= m2 * lam)
        if npair and use_F:
            Fp = sp.csr_matrix((self.pF_v, (self.pF_r, self.pF_c)),
                               shape=(npair, self.n_forb))
            mm = np.array(self.p_mm)
            cons.append(Fp @ f <= -self.delta_pair * mm)
        if lam_ub is not None:
            cons.append(lam <= lam_ub)
        prob = cp.Problem(cp.Minimize(lam), cons)
        t0 = time.time()
        if solver == "auto":
            # Clarabel's direct factorisation explodes in memory for large PSD cones
            # (observed: 9 GB alloc failure at cone 309); SCS is the safe big-cone choice.
            if self.k > 150:
                prob.solve(solver="SCS", verbose=verbose, eps=2e-6, max_iters=60000, **kw)
            else:
                prob.solve(solver="CLARABEL", verbose=verbose, **kw)
        elif solver == "SCS":
            prob.solve(solver="SCS", verbose=verbose, eps=3e-5, max_iters=30000, **kw)
        else:
            prob.solve(solver=solver, verbose=verbose, **kw)
        if prob.status not in ("optimal", "optimal_inaccurate"):
            raise RuntimeError(f"solver status {prob.status}")
        g_orb = np.array(g.value)
        f_val = np.array(f.value) if use_F else np.zeros(self.n_forb)
        return dict(lam=float(lam.value), g_orb=g_orb, f=f_val, status=prob.status,
                    time=time.time() - t0)

    # ---------------- kernel evaluation of a solution
    def kernel(self, g_orb, f):
        return HybridKernel(self, g_orb, f)

    def dense_M(self, g_orb, f):
        """the full (nf x nf) M for validation against A17 machinery."""
        m = self.fm.m
        w = self.fm.w
        D = np.diag(g_orb[self.oid])
        if self.k and f is not None and len(f):
            Fd = np.asarray((self.Bas @ f)).reshape(self.k, self.k)
            D[np.ix_(self.r_idx, self.r_idx)] += Fd
        M = np.zeros((m + 1, m + 1))
        M[0, 0] = 1.0
        M[0, 1:] = -w
        M[1:, 0] = -w
        M[1:, 1:] = D
        return M


class HybridKernel:
    """oracle-facing evaluator: kdiag / u_single (A17 diag_oracle shim) + kpair for disjoint pairs."""
    def __init__(self, hs, g_orb, f):
        self.hs = hs
        self.fm = hs.fm
        self.g_atom = np.asarray(g_orb, float)[hs.oid]
        self.k = hs.k
        if hs.k and f is not None and len(f):
            self.Fd = np.asarray((hs.Bas @ np.asarray(f, float))).reshape(hs.k, hs.k)
        else:
            self.Fd = np.zeros((hs.k, hs.k))
        self.r_idx = hs.r_idx

    def _parts(self, P):
        pat = self.fm.patterns(np.asarray(P, float).reshape(-1, 3))
        mv = pat @ self.fm.w
        gsum = pat @ self.g_atom
        patR = pat[:, self.r_idx].tocsr() if self.k else None
        return pat, mv, gsum, patR

    def kdiag(self, P):
        pat, mv, gsum, patR = self._parts(P)
        quad = np.zeros(len(mv))
        if self.k and patR.nnz:
            Q = patR @ self.Fd
            quad = np.asarray(patR.multiply(Q).sum(axis=1)).ravel()
        bad = mv <= 0
        val = np.where(bad, np.inf, (gsum + quad) / np.maximum(mv, 1e-300) ** 2 - 1.0)
        return val

    def u_single(self, x):
        v = float(self.kdiag(np.asarray(x, float)[None])[0])
        return np.array([math.sqrt(max(v, 0.0))])

    def kpair(self, X, Y):
        """K(x,y) for DISJOINT pairs (patterns must share no atom; not checked)."""
        _, m1, _, pR1 = self._parts(X)
        _, m2, _, pR2 = self._parts(Y)
        if self.k == 0:
            return -np.ones(len(m1))
        if pR1.nnz and pR2.nnz:
            A = pR1 @ self.Fd                       # dense (n, k)
            cross = np.asarray(pR2.multiply(A).sum(axis=1)).ravel()
        else:
            cross = np.zeros(len(m1))
        return cross / np.maximum(m1 * m2, 1e-300) - 1.0

    def meets_R(self, P):
        if self.k == 0:
            return np.zeros(len(np.atleast_2d(P)), bool)
        pat = self.fm.patterns(np.asarray(P, float).reshape(-1, 3))
        return np.asarray(pat[:, self.r_idx].sum(axis=1)).ravel() > 0
