r"""
A66 PAIR-LP pilot (docs/proofs/pair_kill.md Lemma P / sect. 6; docs/specs/pair_certificate_v1.md).

Dual/packing side of the restricted pair LP.  Variables z_{ij} >= 0 live on unordered pairs of
CORE-FREE, interior-disjoint unit-square placements drawn from a finite catalog S; the packing
constraint is the (P2') row load at every ordered point pattern (c,d):

    sum_{i<j} z_ij * ( [c in Q_i][d in Q_j] + [c in Q_j][d in Q_i] )  <=  1     for all c,d,

and the objective is sum_{i<j} z_ij * (1 + beta * m2_ij).  Weak duality against (P2'): any
certificate satisfying (P2') has W2 >= sum_ij z_ij (1 + beta m2_ij) for any feasible z (sum the
rows with weights z and use that each atom is collected by at most one pair -- pair_kill.md
step 6 / "death witness" of sect. 4).  So the LP value is a LOWER bound on every certificate's
W2, and value > C(N,2) + beta*m REFUTES the pair route for the class.

Float pilot (HiGHS), exactly as A65's boostlp.py prices the single-square boosted LP: this run
measures the route, it does not certify it.

    python code\pairlp.py --cls k4_08 --betas 0,0.25,0.5,1.0
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")           # BEFORE numpy

import argparse, ctypes, json, math, sys, time
from fractions import Fraction as Fr
import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(BASE, ".."))
BOXSPEC = os.path.join(REPO, "A65-low-k-closure", "results", "h10_boxspec.json")
CROWDFAM = os.path.join(REPO, "A65-low-k-closure", "results", "crowdfam.json")

S0 = float(Fr("969271/250000"))

EPS_CORE = 1e-7        # margin in the core-free separating-axis test
EPS_MEET = 1e-9        # strict margin for "open interiors meet" (box incidence)
EPS_DISJ = 1e-9        # required SAT gap for a disjoint pair
EPS_IN = 1e-9          # strict-interior margin for point membership
EPS_LOAD = 1e-9        # violation tolerance in the cutting-plane loop

T_COARSE = [0.0, 0.1, 0.2, 0.29, 0.36576931, 0.41421356, 0.46437613, 0.55, 0.7, 0.85]
T_EXTRA = [0.03, 0.06, 0.15, 0.25, 0.33]


def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n")
        fh.flush()


# ------------------------------------------------------------------ memory guard
class MEMSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def commit_headroom_gb():
    st = MEMSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPageFile / 2.0 ** 30, st.ullAvailPhys / 2.0 ** 30


def require_headroom(gb, fh=None, wait=0.0):
    """Hard gate: never start a solve with ullAvailPageFile <= gb.  The other campaigns on this
    box (A57/A60/A61 + the lean wave) swing the commit charge by several GB on a ~30 s scale,
    so a transient dip is waited out rather than treated as a verdict; a sustained dip aborts."""
    t0 = time.time()
    while True:
        avail, phys = commit_headroom_gb()
        if avail > gb:
            log("headroom OK: ullAvailPageFile=%.2f GB, ullAvailPhys=%.2f GB (need > %.1f GB)"
                % (avail, phys, gb), fh)
            return avail
        if time.time() - t0 >= wait:
            log("ABORT: commit headroom %.2f GB <= %.1f GB (waited %.0f s)"
                % (avail, gb, time.time() - t0), fh)
            sys.exit(3)
        log("headroom low: %.2f GB <= %.1f GB, waiting..." % (avail, gb), fh)
        time.sleep(10.0)


# ------------------------------------------------------------------ geometry
def theta_of(t):
    return 2.0 * math.atan(t)


def width(th):
    return abs(math.cos(th)) + abs(math.sin(th))


def core_free_mask(C, th, pins):
    """(n,) bool: unit square at centres C (n,2), tilt th, is separated from EVERY axis unit pin.
    Separated on direction u iff |dc.u| >= (1+w)/2 (margin EPS_CORE), u in {e1,e2,a1,a2}."""
    if len(pins) == 0:
        return np.ones(len(C), dtype=bool)
    c, s = math.cos(th), math.sin(th)
    thr = (1.0 + width(th)) / 2.0 - EPS_CORE
    dx = C[:, None, 0] - pins[None, :, 0]
    dy = C[:, None, 1] - pins[None, :, 1]
    sep = ((np.abs(dx) >= thr) | (np.abs(dy) >= thr)
           | (np.abs(dx * c + dy * s) >= thr) | (np.abs(-dx * s + dy * c) >= thr))
    return sep.all(axis=1)


def core_margin(C, th, pins):
    """(n,) float: max over pins of (best-axis |proj| - thr).  >=0 means separated."""
    if len(pins) == 0:
        return np.full(len(C), np.inf)
    c, s = math.cos(th), math.sin(th)
    thr = (1.0 + width(th)) / 2.0
    dx = C[:, None, 0] - pins[None, :, 0]
    dy = C[:, None, 1] - pins[None, :, 1]
    best = np.maximum.reduce([np.abs(dx), np.abs(dy),
                              np.abs(dx * c + dy * s), np.abs(-dx * s + dy * c)]) - thr
    return best.min(axis=1)


def box_mask_bits(C, th, boxes):
    """(n,) int64 bitmask of class boxes (axis unit squares at slot centres) whose OPEN interior
    meets the open interior of the unit square at C, tilt th."""
    n = len(C)
    if len(boxes) == 0:
        return np.zeros(n, dtype=np.int64)
    c, s = math.cos(th), math.sin(th)
    thr = (1.0 + width(th)) / 2.0 - EPS_MEET
    dx = C[:, None, 0] - boxes[None, :, 0]
    dy = C[:, None, 1] - boxes[None, :, 1]
    hit = ((np.abs(dx) < thr) & (np.abs(dy) < thr)
           & (np.abs(dx * c + dy * s) < thr) & (np.abs(-dx * s + dy * c) < thr))
    bits = (np.int64(1) << np.arange(len(boxes), dtype=np.int64))[None, :]
    return (hit.astype(np.int64) * bits).sum(axis=1)


def half_width(u, th):
    """half-width of the unit square with tilt th on unit direction u=(ux,uy)."""
    c, s = math.cos(th), math.sin(th)
    return 0.5 * (abs(u[0] * c + u[1] * s) + abs(-u[0] * s + u[1] * c))


def inside_mask_points(P, cx, cy, th):
    """(np,) bool: point strictly inside the unit square (cx,cy,th) by margin EPS_IN."""
    c, s = math.cos(th), math.sin(th)
    dx = P[:, 0] - cx
    dy = P[:, 1] - cy
    u = dx * c + dy * s
    v = -dx * s + dy * c
    h = 0.5 - EPS_IN
    return (np.abs(u) < h) & (np.abs(v) < h)


# ------------------------------------------------------------------ catalog
def greedy_diverse(X, keep, seed_idx=None):
    """farthest-point sampling of `keep` rows of X (n,d), max-min Euclidean."""
    n = len(X)
    if n <= keep:
        return np.arange(n)
    sel = [0 if seed_idx is None else int(seed_idx)]
    d = np.linalg.norm(X - X[sel[0]], axis=1)
    for _ in range(keep - 1):
        j = int(np.argmax(d))
        sel.append(j)
        d = np.minimum(d, np.linalg.norm(X - X[j], axis=1))
    return np.array(sel)


def grid_vals(lo, hi, step):
    if hi < lo:
        return np.zeros(0)
    v = np.arange(0.0, S0 + 1e-12, step)
    v = v[(v >= lo - 1e-12) & (v <= hi + 1e-12)]
    return np.unique(np.concatenate([[lo, hi], v]))


def build_catalog(pins, boxes, cap_total, cap_m2, cap_m1, fh, extra=None):
    """returns dict with arrays t, th, cx, cy, mask, m, and per-source counts."""
    stats = {}

    # ---- coarse
    co_t, co_c = [], []
    for t in T_COARSE:
        th = theta_of(t)
        w = width(th)
        lo, hi = w / 2.0, S0 - w / 2.0
        v = grid_vals(lo, hi, 0.2)
        XX, YY = np.meshgrid(v, v, indexing="ij")
        C = np.column_stack([XX.ravel(), YY.ravel()])
        keep = core_free_mask(C, th, pins)
        C = C[keep]
        co_t.append(np.full(len(C), t))
        co_c.append(C)
    co_t = np.concatenate(co_t)
    co_c = np.vstack(co_c)
    stats["coarse_corefree"] = int(len(co_t))
    log("catalog: coarse core-free = %d" % len(co_t), fh)

    # ---- enrichment
    en_t, en_c = [], []
    bc = boxes
    for t in sorted(set(T_COARSE + T_EXTRA)):
        th = theta_of(t)
        w = width(th)
        lo, hi = w / 2.0, S0 - w / 2.0
        v = grid_vals(lo, hi, 0.07)
        XX, YY = np.meshgrid(v, v, indexing="ij")
        C = np.column_stack([XX.ravel(), YY.ravel()])
        if len(bc):
            d = np.min(np.hypot(C[:, None, 0] - bc[None, :, 0], C[:, None, 1] - bc[None, :, 1]), axis=1)
            C = C[d <= 1.7]
        keep = core_free_mask(C, th, pins)
        C = C[keep]
        en_t.append(np.full(len(C), t))
        en_c.append(C)
    en_t = np.concatenate(en_t)
    en_c = np.vstack(en_c)
    stats["enrich_corefree"] = int(len(en_t))
    log("catalog: enrichment core-free = %d" % len(en_t), fh)

    en_mask = np.zeros(len(en_t), dtype=np.int64)
    for t in np.unique(en_t):
        sel = np.nonzero(en_t == t)[0]
        en_mask[sel] = box_mask_bits(en_c[sel], theta_of(float(t)), boxes)
    en_m = np.array([bin(int(x)).count("1") for x in en_mask])

    pick = []
    for lo_m, hi_m, cap in ((2, 99, cap_m2), (1, 1, cap_m1)):
        sel = np.nonzero((en_m >= lo_m) & (en_m <= hi_m))[0]
        if len(sel) == 0:
            continue
        X = np.column_stack([en_c[sel, 0], en_c[sel, 1], 2.0 * en_t[sel]])
        g = greedy_diverse(X, min(cap, len(sel)))
        pick.append(sel[g])
        stats["enrich_m%s_avail" % lo_m] = int(len(sel))
        stats["enrich_m%s_kept" % lo_m] = int(len(g))
    pick = np.concatenate(pick) if pick else np.zeros(0, dtype=int)

    T = list(en_t[pick])
    C = list(map(tuple, en_c[pick]))

    # ---- explicit extra placements (control family), before the coarse fill
    n_extra = 0
    if extra:
        for (t, cx, cy) in extra:
            T.append(t); C.append((cx, cy)); n_extra += 1
    stats["extra_added"] = n_extra

    # ---- coarse fill
    room = cap_total - len(T)
    if room > 0 and len(co_t):
        X = np.column_stack([co_c[:, 0], co_c[:, 1], 2.0 * co_t])
        g = greedy_diverse(X, min(room, len(co_t)))
        T += list(co_t[g])
        C += list(map(tuple, co_c[g]))
    stats["coarse_kept"] = int(len(T) - len(pick) - n_extra)

    t = np.array(T, dtype=float)
    C = np.array(C, dtype=float)
    # dedupe
    key = np.round(np.column_stack([C, t]) / 1e-9).astype(np.int64)
    _, uniq = np.unique(key, axis=0, return_index=True)
    uniq = np.sort(uniq)
    t, C = t[uniq], C[uniq]

    th = np.array([theta_of(x) for x in t])
    mask = np.zeros(len(t), dtype=np.int64)
    for tv in np.unique(t):
        sel = np.nonzero(t == tv)[0]
        mask[sel] = box_mask_bits(C[sel], theta_of(float(tv)), boxes)
    m = np.array([bin(int(x)).count("1") for x in mask])
    cm = np.zeros(len(t))
    for tv in np.unique(t):
        sel = np.nonzero(t == tv)[0]
        cm[sel] = core_margin(C[sel], theta_of(float(tv)), pins)
    stats["near_tangent_to_core"] = int(np.sum(cm < 1e-5))
    stats["min_core_margin"] = float(cm.min()) if len(cm) else None
    stats["n_placements"] = int(len(t))
    stats["m_histogram"] = {int(k): int(v) for k, v in zip(*np.unique(m, return_counts=True))}
    return dict(t=t, th=th, C=C, mask=mask, m=m, stats=stats)


# ------------------------------------------------------------------ disjoint pairs
def disjoint_pairs(cat):
    """all i<j with a separating axis of gap >= EPS_DISJ among the 4 square normals."""
    n = len(cat["t"])
    C, th = cat["C"], cat["th"]
    cs, sn = np.cos(th), np.sin(th)
    dx = C[:, None, 0] - C[None, :, 0]
    dy = C[:, None, 1] - C[None, :, 1]
    ok = np.zeros((n, n), dtype=bool)
    # half-widths on the 4 normal families, done per "owner" of the normal
    for owner in (0, 1):
        for ax in (0, 1):
            # normal u = a1 or a2 of square `owner`; loop over the owner index vectorised
            if owner == 0:
                ux = cs if ax == 0 else -sn
                uy = sn if ax == 0 else cs
                UX = ux[:, None] * np.ones((1, n))
                UY = uy[:, None] * np.ones((1, n))
            else:
                ux = cs if ax == 0 else -sn
                uy = sn if ax == 0 else cs
                UX = np.ones((n, 1)) * ux[None, :]
                UY = np.ones((n, 1)) * uy[None, :]
            proj = np.abs(dx * UX + dy * UY)
            hw_i = 0.5 * (np.abs(UX * cs[:, None] + UY * sn[:, None])
                          + np.abs(-UX * sn[:, None] + UY * cs[:, None]))
            hw_j = 0.5 * (np.abs(UX * cs[None, :] + UY * sn[None, :])
                          + np.abs(-UX * sn[None, :] + UY * cs[None, :]))
            ok |= (proj >= hw_i + hw_j + EPS_DISJ)
    iu = np.triu_indices(n, 1)
    sel = ok[iu]
    I = iu[0][sel]
    J = iu[1][sel]
    return I, J


# ------------------------------------------------------------------ point sets
def build_points(cat, boxes, step_global, step_local, radius):
    pts = [cat["C"]]
    if len(boxes):
        pts.append(boxes)
        for sx in (-0.5, 0.5):
            for sy in (-0.5, 0.5):
                pts.append(boxes + np.array([sx, sy]))
    v = np.arange(0.0, S0 + 1e-12, step_global)
    XX, YY = np.meshgrid(v, v, indexing="ij")
    pts.append(np.column_stack([XX.ravel(), YY.ravel()]))
    if len(boxes):
        v2 = np.arange(0.0, S0 + 1e-12, step_local)
        XX, YY = np.meshgrid(v2, v2, indexing="ij")
        G = np.column_stack([XX.ravel(), YY.ravel()])
        d = np.min(np.hypot(G[:, None, 0] - boxes[None, :, 0], G[:, None, 1] - boxes[None, :, 1]), axis=1)
        pts.append(G[d <= radius])
    P = np.vstack(pts)
    P = P[(P[:, 0] >= -1e-12) & (P[:, 0] <= S0 + 1e-12) & (P[:, 1] >= -1e-12) & (P[:, 1] <= S0 + 1e-12)]
    key = np.round(P / 1e-9).astype(np.int64)
    _, u = np.unique(key, axis=0, return_index=True)
    return P[np.sort(u)]


def membership(P, cat, cols=None):
    """(np, ns) bool membership matrix (strict interior)."""
    idx = np.arange(len(cat["t"])) if cols is None else np.asarray(cols)
    A = np.zeros((len(P), len(idx)), dtype=bool)
    for a, i in enumerate(idx):
        A[:, a] = inside_mask_points(P, cat["C"][i, 0], cat["C"][i, 1], cat["th"][i])
    return A


def dedupe_by_pattern(P, A, keep_empty=False, protect=0):
    """drop points with an all-false membership column, then dedupe identical columns.
    The first `protect` rows are always kept (they anchor the seed-row indexing)."""
    if not keep_empty and protect == 0:
        nz = A.any(axis=1)
        P, A = P[nz], A[nz]
    if len(P) == 0:
        return P, A
    pk = np.packbits(A, axis=1)
    _, u = np.unique(pk, axis=0, return_index=True)
    keep = np.zeros(len(P), dtype=bool)
    keep[np.sort(u)] = True
    keep[:protect] = True
    if not keep_empty:
        keep &= (A.any(axis=1) | (np.arange(len(P)) < protect))
    return P[keep], A[keep]


# ------------------------------------------------------------------ load / cuts
def chunk_load_topk(Af, Z, k, exclude=None, chunk=384, only_upper=True):
    """max entries of L = Af Z Af^T over c<d, returning (list of (val,c,d), Lmax)."""
    npts = Af.shape[0]
    best = []
    lmax = 0.0
    for r0 in range(0, npts, chunk):
        r1 = min(npts, r0 + chunk)
        B = Af[r0:r1] @ Z
        L = B @ Af.T
        if only_upper:
            rows = np.arange(r0, r1)[:, None]
            cols = np.arange(npts)[None, :]
            L = np.where(cols > rows, L, -1.0)
        lmax = max(lmax, float(L.max()) if L.size else 0.0)
        if k > 0:
            flat = L.ravel()
            v = 1.0 + EPS_LOAD
            hits = np.nonzero(flat > v)[0]
            if len(hits):
                vals = flat[hits]
                if len(hits) > k:
                    sub = np.argpartition(-vals, k)[:k]
                    hits, vals = hits[sub], vals[sub]
                cc = r0 + hits // npts
                dd = hits % npts
                for a in range(len(hits)):
                    key = (int(cc[a]), int(dd[a]))
                    if exclude is not None and key in exclude:
                        continue
                    best.append((float(vals[a]), key[0], key[1]))
    best.sort(key=lambda x: -x[0])
    return best[:k], lmax


def chunk_lmax(Af, Z, chunk=384):
    _, lm = chunk_load_topk(Af, Z, 0, chunk=chunk, only_upper=True)
    return lm


def arrangement_probes(cat, sup_sq, z, I, J, args, rng):
    """cell representatives of the arrangement of the support squares: their vertices and
    pairwise edge-intersection points, nudged into the four surrounding cells.  The load
    L(c,d) is constant on arrangement cells, so its maximum is attained arbitrarily close to
    such a point -- the plain 0.12/0.3 grids miss the thin cells entirely."""
    if len(sup_sq) == 0:
        return np.zeros((0, 2))
    idx = sup_sq
    if len(idx) > args.probe_squares:                      # keep the heaviest squares
        wsq = np.zeros(len(cat["t"]))
        np.add.at(wsq, I, z)
        np.add.at(wsq, J, z)
        idx = idx[np.argsort(-wsq[idx])[:args.probe_squares]]
    V = square_vertices(cat, idx)
    X, _ = seg_intersections(cat, idx, cap=args.seg_cap)
    base = np.vstack([V, X]) if len(X) else V
    nb = max(1, args.probe_cap // 4)
    if len(base) > nb:
        base = base[rng.choice(len(base), nb, replace=False)]
    out = []
    for ex in (-args.probe_eps, args.probe_eps):
        for ey in (-args.probe_eps, args.probe_eps):
            out.append(base + np.array([ex, ey]))
    Pp = np.vstack(out)
    return Pp[(Pp[:, 0] >= -1e-9) & (Pp[:, 0] <= S0 + 1e-9)
              & (Pp[:, 1] >= -1e-9) & (Pp[:, 1] <= S0 + 1e-9)]


# ------------------------------------------------------------------ LP
def solve_beta(cat, I, J, m2, P, A, beta, args, fh):
    ns = len(cat["t"])
    npair = len(I)
    t0 = time.time()

    PID = -np.ones((ns, ns), dtype=np.int64)
    PID[I, J] = np.arange(npair)
    PID[J, I] = np.arange(npair)

    obj = 1.0 + beta * m2.astype(float)

    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("time_limit", float(args.lp_time))
    h.changeObjectiveSense(highspy.ObjSense.kMaximize)
    h.addCols(npair, obj, np.zeros(npair), np.full(npair, float(args.zub)),
              0, np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))

    added = set()          # rows are identified by their SUPPORT (point sets come and go)

    def row_support_from_masks(mc, md):
        Ic = np.nonzero(mc)[0]
        Id = np.nonzero(md)[0]
        if len(Ic) == 0 or len(Id) == 0:
            return None
        sub = PID[np.ix_(Ic, Id)]
        v = sub[sub >= 0]
        if v.size == 0:
            return None
        return np.unique(v)

    def add_rows(Amat, pairs):
        starts, idxs = [], []
        nnew, run = 0, 0
        for (c, d) in pairs:
            sup = row_support_from_masks(Amat[c], Amat[d])
            if sup is None:
                continue
            key = sup.tobytes()
            if key in added:
                continue
            added.add(key)
            starts.append(run)          # cumulative NONZERO offset (not list length)
            run += len(sup)
            idxs.append(sup)
            nnew += 1
        if nnew == 0:
            return 0, 0
        ind = np.concatenate(idxs).astype(np.int32)
        st = np.array(starts, dtype=np.int32)
        nrow0 = h.getNumRow()
        h.addRows(nnew, np.full(nnew, -highspy.kHighsInf), np.ones(nnew),
                  len(ind), st, ind, np.ones(len(ind)))
        if h.getNumRow() != nrow0 + nnew:
            raise RuntimeError("addRows rejected %d rows (have %d, wanted %d)"
                               % (nnew, h.getNumRow(), nrow0 + nnew))
        return nnew, len(ind)

    # ---- seed rows: box centres/corners pairs + random pattern pairs
    rng = np.random.default_rng(args.seed)
    nb = args.n_boxpts
    seed_pairs = [(c, d) for c in range(nb) for d in range(c + 1, nb)]
    rp = rng.integers(0, len(P), size=(args.n_seed_random, 2))
    seed_pairs += [(int(a), int(b)) for a, b in rp if a != b]
    nr, nnz = add_rows(A, seed_pairs)
    total_nnz = nnz
    log("beta=%.4g: seed rows=%d nnz=%d cols=%d" % (beta, nr, nnz, npair), fh)

    rounds = 0
    status_note = "converged"
    lm_last = None
    for rd in range(args.max_rounds):
        rounds = rd + 1
        h.run()
        st = h.getModelStatus()
        if st != highspy.HighsModelStatus.kOptimal:
            status_note = "non-optimal LP status %s at round %d" % (st, rounds)
            log("beta=%.4g: %s" % (beta, status_note), fh)
            break
        z = np.array(h.getSolution().col_value)
        val = float(h.getInfo().objective_function_value)
        Z = np.zeros((ns, ns))
        Z[I, J] = z
        Z[J, I] = z
        sup_pairs = np.nonzero(z > 1e-9)[0]
        sup_sq = (np.unique(np.concatenate([I[sup_pairs], J[sup_pairs]]))
                  if len(sup_pairs) else np.zeros(0, dtype=int))
        # working point set = coarse grid + arrangement probes of the CURRENT support squares
        probes = arrangement_probes(cat, sup_sq, z, I, J, args, rng)
        W = np.vstack([P, probes]) if len(probes) else P
        Asub = membership(W, cat, sup_sq)
        keep = Asub.any(axis=1)
        W, Asub = W[keep], Asub[keep]
        W, Asub = dedupe_by_pattern(W, Asub)
        Zs = Z[np.ix_(sup_sq, sup_sq)] if len(sup_sq) else np.zeros((0, 0))
        cuts, lm = chunk_load_topk(Asub.astype(float), Zs, args.max_cuts, chunk=args.chunk)
        lm_last = lm
        log("beta=%.4g round %d: value=%.6f Lmax=%.6f violated=%d pts=%d(probe %d) "
            "supsq=%d rows=%d nnz=%d (%.0fs)"
            % (beta, rounds, val, lm, len(cuts), len(W), len(probes), len(sup_sq),
               h.getNumRow(), total_nnz, time.time() - t0), fh)
        if not cuts:
            break
        idx = np.unique(np.array([[c, d] for (_, c, d) in cuts]).ravel())
        remap = {int(v): a for a, v in enumerate(idx)}
        Afull = membership(W[idx], cat)
        nr, nnz = add_rows(Afull, [(remap[c], remap[d]) for (_, c, d) in cuts])
        total_nnz += nnz
        if nr == 0:
            status_note = "no new distinct rows at round %d" % rounds
            break
        if total_nnz > args.max_nnz:
            status_note = "nnz cap %d hit at round %d" % (args.max_nnz, rounds)
            log("beta=%.4g: %s" % (beta, status_note), fh)
            h.run()
            break
        if time.time() - t0 > args.cls_budget:
            status_note = "time budget hit at round %d" % rounds
            log("beta=%.4g: %s" % (beta, status_note), fh)
            h.run()
            break
    else:
        status_note = "round cap %d reached" % args.max_rounds

    st = h.getModelStatus()
    z = np.array(h.getSolution().col_value)
    val = float(h.getInfo().objective_function_value)
    Z = np.zeros((ns, ns))
    Z[I, J] = z
    Z[J, I] = z

    n_at_ub = int(np.sum(z > args.zub - 1e-6))
    sup = np.nonzero(z > 1e-9)[0]
    mass = float(z.sum())
    mbar2 = float((z * m2).sum() / mass) if mass > 0 else 0.0

    order = np.argsort(-z)[:10]
    top10 = []
    for k in order:
        if z[k] <= 1e-9:
            break
        i, j = int(I[k]), int(J[k])
        top10.append(dict(z=float(z[k]), m2=int(m2[k]),
                          a=dict(t=float(cat["t"][i]), cx=float(cat["C"][i, 0]), cy=float(cat["C"][i, 1])),
                          b=dict(t=float(cat["t"][j]), cx=float(cat["C"][j, 0]), cy=float(cat["C"][j, 1]))))

    return dict(value=val, z=z, Z=Z, support=sup, mbar2=mbar2, top10=top10,
                rounds=rounds, n_rows=int(h.getNumRow()), nnz=total_nnz, n_at_ub=n_at_ub,
                status=str(st), note=status_note, last_cut_Lmax=lm_last,
                seconds=time.time() - t0)


# ------------------------------------------------------------------ fine validity
def square_vertices(cat, idx):
    V = []
    for i in idx:
        cx, cy, th = cat["C"][i, 0], cat["C"][i, 1], cat["th"][i]
        c, s = math.cos(th), math.sin(th)
        for su in (-0.5, 0.5):
            for sv in (-0.5, 0.5):
                V.append((cx + su * c - sv * s, cy + su * s + sv * c))
    return np.array(V) if V else np.zeros((0, 2))


def seg_intersections(cat, idx, cap=400000):
    """pairwise edge-intersection points of the given squares (vectorised, capped)."""
    A, B = [], []
    for i in idx:
        cx, cy, th = cat["C"][i, 0], cat["C"][i, 1], cat["th"][i]
        c, s = math.cos(th), math.sin(th)
        v = [(cx + su * c - sv * s, cy + su * s + sv * c)
             for (su, sv) in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]
        for k in range(4):
            A.append(v[k]); B.append(v[(k + 1) % 4])
    A = np.array(A); B = np.array(B)
    n = len(A)
    if n == 0 or n * n // 2 > cap:
        return np.zeros((0, 2)), (n * n // 2 > cap)
    iu = np.triu_indices(n, 1)
    p, r = A[iu[0]], B[iu[0]] - A[iu[0]]
    q, sv = A[iu[1]], B[iu[1]] - A[iu[1]]
    den = r[:, 0] * sv[:, 1] - r[:, 1] * sv[:, 0]
    good = np.abs(den) > 1e-12
    qp = q - p
    tt = np.where(good, (qp[:, 0] * sv[:, 1] - qp[:, 1] * sv[:, 0]) / np.where(good, den, 1.0), -1.0)
    uu = np.where(good, (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / np.where(good, den, 1.0), -1.0)
    ok = good & (tt >= 0) & (tt <= 1) & (uu >= 0) & (uu <= 1)
    X = p[ok] + tt[ok, None] * r[ok]
    return X, False


def fine_validity(cat, Z, sup_sq, boxes, args, fh):
    if len(sup_sq) == 0:
        return 1.0, 0, {}
    # arrangement cell representatives FIRST (they carry the true load maxima), grids after
    V = square_vertices(cat, sup_sq)
    X, skipped = seg_intersections(cat, sup_sq, cap=args.seg_cap)
    probe = np.vstack([V, X]) if len(X) else V
    pts = []
    for ex in (-args.probe_eps, args.probe_eps):
        for ey in (-args.probe_eps, args.probe_eps):
            pts.append(probe + np.array([ex, ey]))
    n_probe = sum(len(p) for p in pts)
    v = np.arange(0.0, S0 + 1e-12, args.fine_global)
    XX, YY = np.meshgrid(v, v, indexing="ij")
    pts.append(np.column_stack([XX.ravel(), YY.ravel()]))
    if len(boxes):
        v2 = np.arange(0.0, S0 + 1e-12, args.fine_local)
        XX, YY = np.meshgrid(v2, v2, indexing="ij")
        G = np.column_stack([XX.ravel(), YY.ravel()])
        d = np.min(np.hypot(G[:, None, 0] - boxes[None, :, 0], G[:, None, 1] - boxes[None, :, 1]), axis=1)
        pts.append(G[d <= args.fine_radius])
    P = np.vstack(pts)
    ok = ((P[:, 0] >= -1e-9) & (P[:, 0] <= S0 + 1e-9)
          & (P[:, 1] >= -1e-9) & (P[:, 1] <= S0 + 1e-9))
    P = P[ok]
    n_raw = len(P)
    A = membership(P, cat, sup_sq)
    P, A = dedupe_by_pattern(P, A)
    n_uniq = len(P)
    n_drop = 0
    if n_uniq > args.fine_cap:            # probes are first, so they survive the truncation
        rng = np.random.default_rng(args.seed + 7)
        head = min(n_probe, args.fine_cap)
        tail = rng.choice(np.arange(head, n_uniq), args.fine_cap - head, replace=False)
        sel = np.sort(np.concatenate([np.arange(head), tail]))
        n_drop = n_uniq - len(sel)
        P, A = P[sel], A[sel]
    info = dict(fine_points_raw=int(n_raw), fine_points_unique=int(n_uniq),
                fine_points_used=int(len(P)), fine_points_dropped=int(n_drop),
                n_support_squares=int(len(sup_sq)),
                edge_intersections=int(len(X)), edge_intersections_skipped=bool(skipped))
    log("fine validity: raw=%d unique=%d used=%d (support squares=%d, edge-int=%d)"
        % (n_raw, n_uniq, len(P), len(sup_sq), len(X)), fh)
    if len(P) == 0:
        return 1.0, 0, info
    Zs = Z[np.ix_(sup_sq, sup_sq)]
    lm = chunk_lmax(A.astype(float), Zs, chunk=args.chunk)
    return lm, len(P), info


# ------------------------------------------------------------------ control
def control_family(cls, cat_pins, boxes, fh):
    d = json.load(open(CROWDFAM))
    e = d["classes"].get(cls, {})
    fam = e.get("family") or []
    if not fam:
        return None
    P = []
    for f in fam:
        t = float(Fr(f["t"]))
        P.append((t, float(Fr(f["cx"])), float(Fr(f["cy"]))))
    n = len(P)
    ths = [theta_of(t) for (t, _, _) in P]
    C = np.array([[cx, cy] for (_, cx, cy) in P])
    # core-free
    cf = []
    for i in range(n):
        cf.append(bool(core_free_mask(C[i:i + 1], ths[i], cat_pins)[0]))
    # pairwise disjoint + m2
    masks = [int(box_mask_bits(C[i:i + 1], ths[i], boxes)[0]) for i in range(n)]
    gaps, m2s = [], []
    for i in range(n):
        for j in range(i + 1, n):
            dc = C[j] - C[i]
            g = -1e9
            for (th, ) in ((ths[i],), (ths[j],)):
                c, s = math.cos(th), math.sin(th)
                for u in ((c, s), (-s, c)):
                    g = max(g, abs(dc[0] * u[0] + dc[1] * u[1])
                            - half_width(u, ths[i]) - half_width(u, ths[j]))
            gaps.append(g)
            m2s.append(bin(masks[i] & masks[j]).count("1"))
    out = dict(n=n, all_core_free=bool(all(cf)), n_pairs=len(gaps),
               min_sat_gap=float(min(gaps)), all_disjoint=bool(min(gaps) >= 0.0),
               sum_m2=int(sum(m2s)), per_pair_m2=m2s,
               box_meet_counts=[int(sum(1 for k in range(n) if (masks[k] >> b) & 1))
                                for b in range(len(boxes))],
               placements=P)
    log("control %s: core-free=%s disjoint=%s min_gap=%.3e sum_m2=%d box_meets=%s"
        % (cls, out["all_core_free"], out["all_disjoint"], out["min_sat_gap"],
           out["sum_m2"], out["box_meet_counts"]), fh)
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--betas", default="0,0.25,0.5,1.0")
    ap.add_argument("--cap_total", type=int, default=450)
    ap.add_argument("--cap_m2", type=int, default=220)
    ap.add_argument("--cap_m1", type=int, default=130)
    ap.add_argument("--max_rounds", type=int, default=25)
    ap.add_argument("--max_cuts", type=int, default=3000)
    ap.add_argument("--probe_squares", type=int, default=200)
    ap.add_argument("--probe_cap", type=int, default=4000)
    ap.add_argument("--seg_cap", type=int, default=900000)
    ap.add_argument("--probe_eps", type=float, default=1e-5)
    ap.add_argument("--max_nnz", type=int, default=9000000)
    ap.add_argument("--n_seed_random", type=int, default=2000)
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cls_budget", type=float, default=600.0)
    ap.add_argument("--zub", type=float, default=30.0)
    ap.add_argument("--chunk", type=int, default=384)
    ap.add_argument("--fine_global", type=float, default=0.05)
    ap.add_argument("--fine_local", type=float, default=0.02)
    ap.add_argument("--fine_radius", type=float, default=1.2)
    ap.add_argument("--fine_cap", type=int, default=9000)
    ap.add_argument("--seed", type=int, default=20260901)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=300.0)
    ap.add_argument("--no_control_cols", action="store_true")
    args = ap.parse_args()

    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    fh = open(os.path.join(BASE, "logs", "pairlp_%s.log" % args.cls), "w")
    T00 = time.time()

    log("A66 pair-LP pilot: class=%s betas=%s" % (args.cls, args.betas), fh)
    require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
    N, k, m = int(e["N"]), int(e["k"]), len(boxes)
    thresh_base = N * (N - 1) // 2
    log("class %s: k=%d N=%d m=%d  threshold = %d + beta*%d" % (args.cls, k, N, m, thresh_base, m), fh)

    ctrl = control_family(args.cls, pins, boxes, fh)
    extra = None
    if ctrl and not args.no_control_cols:
        extra = ctrl["placements"]

    cat = build_catalog(pins, boxes, args.cap_total, args.cap_m2, args.cap_m1, fh, extra=extra)
    log("catalog: |S|=%d  stats=%s" % (len(cat["t"]), json.dumps(cat["stats"])), fh)

    I, J = disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
    log("disjoint pairs: %d of %d (m2>0: %d, m2 max %d)"
        % (len(I), len(cat["t"]) * (len(cat["t"]) - 1) // 2, int((m2 > 0).sum()),
           int(m2.max()) if len(m2) else 0), fh)

    # point set for the cut loop
    nb = 0
    boxpts = []
    if len(boxes):
        boxpts = [boxes] + [boxes + np.array([sx, sy]) for sx in (-0.5, 0.5) for sy in (-0.5, 0.5)]
        boxpts = np.vstack(boxpts)
        nb = len(boxpts)
    P = build_points(cat, boxes, 0.3, 0.12, 1.5)
    # put the box centres/corners first so the seed rows are exactly those pairs
    if nb:
        keyP = {(round(x, 12), round(y, 12)): i for i, (x, y) in enumerate(P)}
        head = [keyP[(round(x, 12), round(y, 12))] for x, y in boxpts if (round(x, 12), round(y, 12)) in keyP]
        rest = [i for i in range(len(P)) if i not in set(head)]
        P = P[np.array(head + rest)]
        nb = len(head)
    args.n_boxpts = nb
    A = membership(P, cat)
    P, A = dedupe_by_pattern(P, A, keep_empty=False, protect=nb)
    args.n_boxpts = nb
    log("cut-loop points: %d (membership depth mean %.1f, max %d)"
        % (len(P), A.sum(1).mean(), A.sum(1).max()), fh)

    betas = [float(x) for x in args.betas.split(",")]
    out = dict(cls=args.cls, k=k, N=N, m=m, s0=S0,
               threshold_formula="%d + beta*%d" % (thresh_base, m),
               catalog=cat["stats"], n_placements=int(len(cat["t"])),
               n_pairs_disjoint=int(len(I)), n_cut_points=int(len(P)),
               control=None, betas={}, deviations=[],
               settings={kk: vv for kk, vv in vars(args).items()})
    out["deviations"] = [
        "core-free test uses the FULL unit pin (delta = 0), i.e. the strongest core; margin "
        "EPS_CORE = %g applied as |proj| >= (1+w)/2 - EPS_CORE (spec's literal reading)" % EPS_CORE,
        "cutting-plane point set is augmented each round with arrangement-cell representatives "
        "(vertices + pairwise edge intersections of the CURRENT support squares, nudged by "
        "%g in the four diagonal directions); a plain 0.12/0.3 grid leaves Lmax >> 1 because the "
        "load is constant on arrangement cells that the grid never samples" % args.probe_eps,
        "rows are deduplicated by their support set (not by point index), so the working point "
        "set may change between rounds without losing rows",
        "z has an upper bound %g purely to keep intermediate LPs bounded; n_z_at_ub is reported"
        % args.zub,
    ]
    if ctrl:
        out["control"] = {kk: vv for kk, vv in ctrl.items() if kk != "placements"}
        out["control"]["value_formula"] = "%d + beta*%d" % (thresh_base, ctrl["sum_m2"])
        out["control"]["control_columns_added_to_catalog"] = not args.no_control_cols
        if not args.no_control_cols:
            out["deviations"].append(
                "the %d exactly-verified crowdfam placements were ADDED to the catalog as columns "
                "(spec does not ask for it, but the sanity claim 'LP value >= control value' is "
                "only meaningful if the control family's pairs are available to the LP)"
                % ctrl["n"])

    for beta in betas:
        require_headroom(args.headroom, fh, args.headroom_wait)
        r = solve_beta(cat, I, J, m2, P, A, beta, args, fh)
        sup_sq = np.unique(np.concatenate([I[r["support"]], J[r["support"]]])) if len(r["support"]) else np.zeros(0, dtype=int)
        lmax, nfine, finfo = fine_validity(cat, r["Z"], sup_sq, boxes, args, fh)
        lmax = max(lmax, 1.0)
        scaled = r["value"] / lmax
        thr = thresh_base + beta * m
        ctrl_val = (thresh_base + beta * ctrl["sum_m2"]) if ctrl else None
        rec = dict(beta=beta, value=r["value"], Lmax_fine=lmax, scaled_value=scaled,
                   threshold=thr, margin=scaled - thr, mbar2=r["mbar2"],
                   control_value=ctrl_val,
                   value_ge_control=(None if ctrl_val is None else bool(r["value"] >= ctrl_val - 1e-6)),
                   n_support_pairs=int(len(r["support"])), n_support_squares=int(len(sup_sq)),
                   rounds=r["rounds"], n_rows=r["n_rows"], nnz=r["nnz"],
                   n_z_at_ub=r["n_at_ub"], lp_status=r["status"], note=r["note"],
                   seconds=r["seconds"], fine=finfo, top10=r["top10"])
        out["betas"][repr(beta)] = rec
        log("RESULT beta=%.4g: value=%.6f Lmax=%.6f scaled=%.6f thr=%.4f margin=%+.6f "
            "mbar2=%.4f ctrl=%s (%.1fs)"
            % (beta, r["value"], lmax, scaled, thr, scaled - thr, r["mbar2"],
               ctrl_val, r["seconds"]), fh)

    out["total_seconds"] = time.time() - T00
    fp = os.path.join(BASE, "results", "pairlp_%s.json" % args.cls)
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs total)" % (fp, out["total_seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
