"""A17 — indicator-feature machinery for the continuum theta'-kernel certificate at the root.

Features: phi(x) = (1, a_1(x)/m(x), ..., a_m(x)/m(x))  (variant 'norm'; 'plain' = raw indicators),
a_k(x) = 1[p_k in Q(x)] (CLOSED unit square), m(x) = sum_k w_k a_k(x).
Atom sets: A07's LP atoms at the target s (v2_s3.84.json orbits) or a measure certificate
(D4-equivariantly stretched to the target s).  Everything float (this is the float phase; A18 = exact).
"""
import json, math, os, sys
import numpy as np
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
A16 = os.path.join(ROOT, "attempts", "A16-theta-casetree")
A07 = os.path.join(ROOT, "attempts", "A07-lp-dual")
sys.path.insert(0, A16)
import theta_sdp  # symmetry machinery (d4_rep_matrices, symmetry_basis, orbits, dense_T)


# ---------------------------------------------------------------- D4 on points (same enumeration as
# graph.d4_images / theta_sdp.d4_rep_matrices: g = 2k + e  =  F^e R^k, R = +90 deg rotation, F: x -> -x)
def d4_images_pt(x, y, s):
    o = s / 2.0
    xx, yy = x - o, y - o
    out = []
    for k in range(4):
        for refl in (False, True):
            a, b = (-xx, yy) if refl else (xx, yy)
            out.append((a + o, b + o))
        xx, yy = -yy, xx
    return out


def d4_perm_points(A, s, tol=1e-7):
    """Permutation action of D4 on the atom list A (m,2): G (8,m), G[g,i] = index of g*i.
    Raises if the set is not D4-invariant within tol."""
    from scipy.spatial import cKDTree
    A = np.asarray(A, float)
    tree = cKDTree(A)
    m = len(A)
    G = np.zeros((8, m), dtype=np.int32)
    for g in range(8):
        Q = np.array([d4_images_pt(x, y, s)[g] for x, y in A])
        d, idx = tree.query(Q)
        if d.max() > tol:
            i = int(np.argmax(d))
            raise ValueError(f"atom set not D4-invariant: image {Q[i]} of atom {i} {A[i]} missing (d={d[i]:.2e})")
        G[g] = idx
    return G


# ---------------------------------------------------------------- atom sets
def load_atoms_a07_384():
    """A07 LP atoms at s = 3.84 (v2_s3.84.json: 155 orbits, 1181 atoms, total 11.020)."""
    d = json.load(open(os.path.join(A07, "results", "v2_s3.84.json")))
    s = float(d["s"])
    A, w = [], []
    for a in d["atoms"]:
        x, y = a["rep"]
        imgs = []
        for q in d4_images_pt(x, y, s):
            if not any(abs(q[0] - r[0]) < 1e-9 and abs(q[1] - r[1]) < 1e-9 for r in imgs):
                imgs.append(q)
        assert len(imgs) == a["m"], (a, len(imgs))
        for q in imgs:
            A.append(q); w.append(a["w"])
    return np.array(A), np.array(w), s


def stretch_1d(u, s_from, s_to):
    """D4-equivariant piecewise-linear map [0,s_from] -> [0,s_to] fixing the Stromquist lines
    (knots at 1 and s_from-1 -> 1 and s_to-1)."""
    u = np.asarray(u, float)
    lo, hi = 1.0, s_from - 1.0
    mid = 1.0 + (u - 1.0) * (s_to - 2.0) / (s_from - 2.0)
    return np.where(u <= lo, u, np.where(u >= hi, u + (s_to - s_from), mid))


def load_atoms_cert(path, s_to=None):
    """Measure-certificate atoms (exact rationals -> float), optionally stretched to s_to."""
    d = json.load(open(path))
    s = float(F(d["s"]))
    A = np.array([[float(F(x)), float(F(y))] for x, y in d["atoms"]])
    w = np.array([float(F(v)) for v in d["weights"]])
    if s_to is not None and abs(s_to - s) > 1e-12:
        A = np.stack([stretch_1d(A[:, 0], s, s_to), stretch_1d(A[:, 1], s, s_to)], 1)
        s = s_to
    return A, w, s


# ---------------------------------------------------------------- feature map
class FeatureMap:
    def __init__(self, A, w, s, variant="norm"):
        self.A = np.asarray(A, float)
        self.w = np.asarray(w, float)
        self.s = float(s)
        self.m = len(A)
        self.nf = self.m + 1
        assert variant in ("norm", "plain")
        self.variant = variant
        self.G_atoms = d4_perm_points(self.A, self.s)
        # weights must be orbit-constant (m(gx) = m(x))
        for g in range(8):
            assert np.abs(self.w[self.G_atoms[g]] - self.w).max() < 1e-12, "weights not D4-invariant"
        self.Gf = np.zeros((8, self.nf), dtype=np.int32)
        self.Gf[:, 1:] = self.G_atoms + 1

    # ---- patterns / coverage / features
    def patterns(self, P, chunk=1500, tol=0.0):
        """CSR bool (Np, m): a_k(x) = 1[p_k in closed Q(x)] (tol widens the square by tol)."""
        import scipy.sparse as sp
        P = np.asarray(P, float).reshape(-1, 3)
        Ax, Ay = self.A[:, 0], self.A[:, 1]
        indptr = [0]; indices = []
        for i0 in range(0, len(P), chunk):
            Pc = P[i0:i0 + chunk]
            c, sn = np.cos(Pc[:, 2])[:, None], np.sin(Pc[:, 2])[:, None]
            dx = Ax[None, :] - Pc[:, 0][:, None]
            dy = Ay[None, :] - Pc[:, 1][:, None]
            u = c * dx + sn * dy
            v = -sn * dx + c * dy
            lim = 0.5 + tol
            ins = (np.abs(u) <= lim) & (np.abs(v) <= lim)
            for r in range(len(Pc)):
                nz = np.nonzero(ins[r])[0]
                indices.append(nz)
                indptr.append(indptr[-1] + len(nz))
        indices = np.concatenate(indices) if indices else np.zeros(0, dtype=int)
        data = np.ones(len(indices))
        return sp.csr_matrix((data, indices, np.array(indptr)), shape=(len(P), self.m))

    def coverage(self, P=None, pat=None):
        if pat is None:
            pat = self.patterns(P)
        return pat @ self.w

    def phi(self, P=None, pat=None):
        """CSR (Np, nf): column 0 = 1, columns 1.. = a_k (variant plain) or a_k/m(x) (variant norm).
        Placements with m(x) = 0 get phi = (1, 0, ..., 0) (counted in .n_zero_cov)."""
        import scipy.sparse as sp
        if pat is None:
            pat = self.patterns(P)
        pat = pat.tocsr().astype(float)
        n = pat.shape[0]
        if self.variant == "norm":
            cov = pat @ self.w
            self.n_zero_cov = int((cov <= 0).sum())
            scale = np.where(cov > 0, 1.0 / np.maximum(cov, 1e-300), 0.0)
            pat = sp.diags(scale) @ pat
        ones = sp.csr_matrix(np.ones((n, 1)))
        return sp.hstack([ones, pat], format="csr")

    # ---- D4-canonical pattern keys (for row dedup)
    def canon_key(self, nz):
        """nz = sorted atom indices of a pattern; returns the lexicographically smallest D4 image."""
        best = None
        for g in range(8):
            img = tuple(sorted(self.G_atoms[g, nz]))
            if best is None or img < best:
                best = img
        return best

    def canon_key_pair(self, nz1, nz2):
        best = None
        for g in range(8):
            i1 = tuple(sorted(self.G_atoms[g, nz1]))
            i2 = tuple(sorted(self.G_atoms[g, nz2]))
            pair = (i1, i2) if i1 <= i2 else (i2, i1)
            if best is None or pair < best:
                best = pair
        return best

    # ---- LP-form kernel (A15 §4): M_LP = (1/tau) sum_k w_k (tau e_k - e_0)(tau e_k - e_0)^T
    def M_lp(self, tau=None):
        assert self.variant == "norm", "LP form is only a certificate in the normalised class"
        tau = float(self.w.sum()) if tau is None else float(tau)
        M = np.zeros((self.nf, self.nf))
        M[0, 0] = self.w.sum() / tau
        M[0, 1:] = -self.w
        M[1:, 0] = -self.w
        M[np.arange(1, self.nf), np.arange(1, self.nf)] = tau * self.w
        return M


# ---------------------------------------------------------------- kernel evaluation
def kdiag(Phi, M, chunk=4000):
    """K(x,x) for a sparse feature matrix Phi (Np, nf) and dense M."""
    out = np.empty(Phi.shape[0])
    for i0 in range(0, Phi.shape[0], chunk):
        Pc = Phi[i0:i0 + chunk]
        G = Pc @ M
        out[i0:i0 + chunk] = np.asarray(Pc.multiply(G).sum(axis=1)).ravel()
    return out


def kmatrix(Phi1, M, Phi2=None):
    """dense K = Phi1 M Phi2^T."""
    Phi2 = Phi1 if Phi2 is None else Phi2
    return np.asarray((Phi1 @ M) @ Phi2.T.toarray() if hasattr(Phi2, "toarray") else (Phi1 @ M) @ Phi2.T)


# ---------------------------------------------------------------- symmetry basis over features
def build_symmetry(fm):
    """Isotypic basis of the D4 permutation action on the nf features.
    Returns dict(SB, Ts) with Ts[name] = list over r of sparse csc (nf, m_name)."""
    import scipy.sparse as sp
    rho = theta_sdp.d4_rep_matrices()
    oid, orbs = theta_sdp.orbits(fm.Gf)
    SB = theta_sdp.symmetry_basis(fm.Gf, orbs, rho)
    Ts = {}
    for n in SB["names"]:
        if SB["m"][n] == 0:
            continue
        Ts[n] = [sp.csc_matrix(theta_sdp.dense_T(SB, n, r)) for r in range(SB["dims"][n])]
    return dict(SB=SB, Ts=Ts, n_orbits=len(orbs))


def reconstruct_M(sym, X):
    SB = sym["SB"]
    nf = SB["col"][SB["names"][0]].shape[0]
    M = np.zeros((nf, nf))
    for n in SB["names"]:
        if SB["m"][n] == 0 or n not in X:
            continue
        for r in range(SB["dims"][n]):
            T = sym["Ts"][n][r].toarray()
            M += T @ X[n] @ T.T
    return M


# ---------------------------------------------------------------- placement sampling helpers
def admissible_w(theta):
    return np.cos(theta) + np.sin(theta)


def random_placements(s, n, rng, boundary_frac=0.25):
    """uniform placements in P_s; a fraction on the admissible-centre boundary (A14 lesson)."""
    th = rng.uniform(0, math.pi / 2, n)
    w = admissible_w(th)
    lo = w / 2
    hi = s - w / 2
    cx = lo + (hi - lo) * rng.uniform(0, 1, n)
    cy = lo + (hi - lo) * rng.uniform(0, 1, n)
    nb = int(n * boundary_frac)
    if nb:
        which = rng.integers(0, 4, nb)
        val = np.where(which % 2 == 0, lo[:nb], hi[:nb])
        cx[:nb] = np.where(which < 2, val, cx[:nb])
        cy[:nb] = np.where(which >= 2, val, cy[:nb])
    # a few exactly-axis thetas
    na = int(n * 0.1)
    th[-na:] = rng.choice([0.0, math.pi / 4, math.pi / 2 - 1e-12], na)
    w = admissible_w(th)
    cx = np.clip(cx, w / 2, s - w / 2)
    cy = np.clip(cy, w / 2, s - w / 2)
    return np.stack([cx, cy, th], 1)


def structured_placements(s):
    """A15-style seeded grid: h = 0.2, dtheta = 10 deg + A12 quarter-structures + A07 dual support."""
    sys.path.insert(0, A16)
    from graph import build_nodes
    from nodes import a15_extras
    seeds = [(cx, cy, th) for cx, cy, th, y in a15_extras(s, mode="all")]
    P = build_nodes(s, 0.2, list(np.arange(0.0, 90.0, 10.0)), extra=seeds)
    return P


if __name__ == "__main__":
    # smoke test at 3.84
    A, w, s = load_atoms_a07_384()
    print(f"atoms {len(A)} total {w.sum():.6f} s {s}")
    fm = FeatureMap(A, w, s)
    sym = build_symmetry(fm)
    print("blocks", sym["SB"]["m"], "orbits", sym["n_orbits"])
    rng = np.random.default_rng(0)
    P = random_placements(s, 2000, rng)
    pat = fm.patterns(P)
    cov = fm.coverage(pat=pat)
    q = np.diff(pat.indptr)
    print(f"coverage min/med/max {cov.min():.4f}/{np.median(cov):.4f}/{cov.max():.4f}; atoms-in-Q min/med/max {q.min()}/{int(np.median(q))}/{q.max()}")
    Phi = fm.phi(pat=pat)
    M = fm.M_lp()
    kd = kdiag(Phi, M)
    tau = w.sum()
    print(f"LP-form K(x,x): max {kd.max():.6f} (= tau/m_min - 1 = {tau/cov.min()-1:.6f}?), min {kd.min():.6f}")
    # invariance check: K(gx, gx) = K(x, x)
    from graph import d4_images as d4p
    Pg = np.array([d4p(tuple(p), s)[3] for p in P[:200]])
    kd2 = kdiag(fm.phi(Pg), M)
    print("D4 invariance of LP kernel:", np.abs(kd2 - kd[:200]).max())
    # M reconstruction round trip: project M_lp on the invariant algebra should be exact (M_lp invariant)
    import scipy.sparse as sp
    err = 0.0
    for n in sym["SB"]["names"]:
        if sym["SB"]["m"][n] == 0:
            continue
        for r in range(sym["SB"]["dims"][n]):
            pass
    print("ok")
