"""A15 — discretised placement graph for the ϑ′ vs LP pilot.

Nodes: unit-square placements (cx, cy, θ), θ ∈ [0, 90°), Q(c,θ) ⊂ [0,s]².
Edges: interiors overlap (exact SAT test, vectorised; touching is NOT an edge, matching A07's
ε-shrunk point coverage / A12's geom.overlap_matrix with tol = 1e-9).
Symmetry: the container's D4 acts on placements; the node set is built D4-invariant and the
orbits / permutation action are returned (needed by the symmetry-reduced SDP).
"""
import math
import numpy as np

DEG = math.pi / 180.0


def admissible(cx, cy, th, s, tol=1e-9):
    w = math.cos(th) + math.sin(th)
    return (w / 2 - tol <= cx <= s - w / 2 + tol) and (w / 2 - tol <= cy <= s - w / 2 + tol)


def d4_images(p, s):
    """The 8 D4 images of a placement p = (cx, cy, θ) (θ in radians, reduced mod π/2)."""
    cx, cy, th = p
    o = s / 2.0
    out = []
    x, y, t = cx - o, cy - o, th
    for k in range(4):                    # rotations by 90° about the container centre: θ unchanged mod 90°
        for refl in (False, True):        # reflection x -> -x: θ -> -θ
            xx, yy, tt = (-x, y, (-t) % (math.pi / 2)) if refl else (x, y, t % (math.pi / 2))
            out.append((xx + o, yy + o, tt))
        x, y = -y, x
    return out


def _canon(p):
    cx, cy, th = p
    th = th % (math.pi / 2)
    if th > math.pi / 2 - 1e-7 or th < 1e-7:
        th = 0.0
    return (cx, cy, th)


def build_nodes(s, h, thetas_deg, extra=(), centre_offset=0.0, merge_tol=2e-5, extra_group=None):
    """Grid nodes: centres cx = s/2 + (k + centre_offset) h (symmetric about s/2), theta in thetas_deg (symmetrised under
    theta -> -theta mod 90), plus the D4-orbits of `extra` placements (list of (cx, cy, theta_rad)).  Near-duplicates (within
    merge_tol in (cx, cy, theta)) are merged (first kept) so that the D4 action is well defined.  Returns P (N,3)."""
    from scipy.spatial import cKDTree
    P = []
    kmax = int(math.ceil(s / h)) + 1
    thetas = sorted(set([(t * DEG) % (math.pi / 2) for t in thetas_deg] + [(-t * DEG) % (math.pi / 2) for t in thetas_deg]))
    for th in thetas:
        for i in range(-kmax, kmax + 1):
            for j in range(-kmax, kmax + 1):
                cx = s / 2 + (i + centre_offset) * h
                cy = s / 2 + (j + centre_offset) * h
                for q in d4_images((cx, cy, th), s):
                    if admissible(*q, s):
                        P.append(_canon(q))
    gl = list(range(8)) if extra_group is None else list(extra_group)
    for p in extra:
        imgs = d4_images(tuple(p), s)
        for g in gl:
            q = imgs[g]
            if admissible(*q, s):
                P.append(_canon(q))
    P = np.array(P, dtype=float)
    tree = cKDTree(P)
    pairs = tree.query_pairs(merge_tol, output_type='ndarray')
    drop = np.zeros(len(P), dtype=bool)
    if len(pairs):
        pairs = pairs[np.argsort(pairs[:, 0], kind='stable')]
        for a, b in pairs:
            if not drop[a]:
                drop[b] = True
    return P[~drop]


def d4_action(P, s, gl=None):
    """Permutation action of D4 (or of the subgroup with element indices gl) on the node set: returns G (|gl|, N) int
    array, G[a, i] = index of gl[a]·i.  Group element order: k rotations x reflection as in d4_images.  Raises if the
    set is not invariant."""
    from scipy.spatial import cKDTree
    N = len(P)
    gl = list(range(8)) if gl is None else list(gl)
    tree = cKDTree(np.array([_canon(p) for p in P]))
    G = np.zeros((len(gl), N), dtype=int)
    for a, g in enumerate(gl):
        Q = np.array([_canon(d4_images(tuple(p), s)[g]) for p in P])
        d, idx = tree.query(Q)
        if d.max() > 5e-5:
            i = int(np.argmax(d))
            raise ValueError(f"node set not D4-invariant: image {Q[i]} of node {i} {P[i]} missing (d={d[i]})")
        G[a] = idx
    # dedupe check
    return G


def orbits(G):
    """Node orbits from the action array. Returns (orbit_id (N,), list of orbit index arrays)."""
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


def corners(P):
    P = np.asarray(P, dtype=float)
    c, s_ = np.cos(P[:, 2]), np.sin(P[:, 2])
    H = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])
    C = np.empty((len(P), 4, 2))
    C[:, :, 0] = P[:, None, 0] + H[None, :, 0] * c[:, None] - H[None, :, 1] * s_[:, None]
    C[:, :, 1] = P[:, None, 1] + H[None, :, 0] * s_[:, None] + H[None, :, 1] * c[:, None]
    return C


def overlap_matrix(P, tol=1e-9, chunk=800):
    """Boolean (N,N) interior-overlap matrix via SAT on the 4 edge normals (2 per square). Vectorised, chunked."""
    P = np.asarray(P, dtype=float)
    N = len(P)
    C = corners(P)                                   # (N,4,2)
    th = P[:, 2]
    AX = np.stack([np.stack([np.cos(th), np.sin(th)], 1), np.stack([-np.sin(th), np.cos(th)], 1)], 1)  # (N,2,2)
    # projections of every square j onto the two axes of square i: computed per chunk of i
    ov = np.ones((N, N), dtype=bool)
    # own projections on own axes are cx·ax ± 1/2 (unit square): centre projection ± 0.5
    for a in range(2):
        for i0 in range(0, N, chunk):
            i1 = min(N, i0 + chunk)
            ax = AX[i0:i1, a]                        # (m,2)
            proj = np.einsum('jkd,id->ijk', C, ax)   # (m,N,4)
            lo = proj.min(2)
            hi = proj.max(2)
            own = P[i0:i1, :2] @ ax.T                # (m,m) -> need diagonal: own centre projection
            ownc = np.einsum('id,id->i', P[i0:i1, :2], ax)  # (m,)
            depth = np.minimum(ownc[:, None] + 0.5, hi) - np.maximum(ownc[:, None] - 0.5, lo)
            ov[i0:i1, :] &= depth > tol
    ov &= ov.T                                       # axes of j for pair (i,j)
    np.fill_diagonal(ov, False)
    return ov


def edge_list(ov):
    I, J = np.nonzero(np.triu(ov, 1))
    return np.stack([I, J], 1)


if __name__ == "__main__":
    import sys, time
    s = float(sys.argv[1]) if len(sys.argv) > 1 else 3.85
    h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
    dth = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
    t0 = time.time()
    P = build_nodes(s, h, np.arange(0, 90, dth))
    G = d4_action(P, s)
    oid, orbs = orbits(G)
    ov = overlap_matrix(P)
    print(f"s={s} h={h} dθ={dth}: N={len(P)} orbits={len(orbs)} edges={ov.sum()//2} density={ov.mean():.3f} t={time.time()-t0:.1f}s")
    # sanity vs A12 geom
    sys.path.insert(0, 'C:/Users/esumm/code/packing/attempts/A12-region-rank-pilot')
    import geom
    ov2 = geom.overlap_matrix(P[:300])
    print("agree with A12 geom on first 300:", np.array_equal(ov2, ov[:300, :300]))
