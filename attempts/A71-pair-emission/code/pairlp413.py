r"""
A71 variant of the A66 PAIR-LP pilot -- corners4 (k4_13) solve-time wall breaker.

Differences from code/pairlp.py (which is left untouched):

  (1) SOLVER.  The cut-loop solves use HiGHS interior point with crossover OFF (--lp_solver ipm,
      --loop_crossover off): no vertex is needed to separate, and an interior (analytic-centre-ish)
      z generates far better cuts than a degenerate simplex vertex.  The FINAL solve of every
      outer pass switches to --final_solver / --final_crossover so the reported optimum and the
      row duals are a clean basic solution.  --ab_rounds runs a fresh-model A/B/C timing of
      {simplex, ipm, pdlp} at the given rounds (time-boxed by --ab_budget).

  (2) MAXIMAL-PATTERN ROW REDUCTION (the actual wall-breaker).  The (P2') load
          L(c,d) = sum_{i<j} z_ij ([c in Qi][d in Qj] + [c in Qj][d in Qi])
      is monotone non-decreasing in the membership sets M(c) = {i : c in int Q_i}, because every
      z_ij >= 0.  Hence  M(c) subset M(c')  implies  L(c,d) <= L(c',d)  for every d, so the row
      of (c,d) is implied by the row of (c',d) and the maximum of L over any point family is
      attained at inclusion-MAXIMAL patterns.  Reducing every working point set to its
      inclusion-maximal membership patterns therefore leaves both the LP feasible region and
      Lmax unchanged while deleting the great majority of the rows.  A66's model reached
      15474 rows / 7.6M nnz at round 11 and each dual-simplex re-solve cost ~5 min; that is the
      wall.  See maximal_by_pattern().

  (3) The fine validity check uses the same reduction, so it no longer has to random-subsample
      down to --fine_cap and can no longer miss a deep cell (A66's fine Lmax = 1075 next to a
      cut-loop Lmax of 1.36 was exactly that blindness).

Original header follows.

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


S0Q = Fr(969271, 250000)
ENFORCE_CONTAINMENT = True     # set False ONLY by the audit, to reproduce the pre-fix catalogs


def w_exact(tq):
    """exact w(t) = |cos th| + |sin th| for th = 2*atan(t): cos = (1-t^2)/(1+t^2),
    sin = 2t/(1+t^2), both rational, and |t| <= 1 so 1 - t^2 >= 0."""
    a = abs(tq)
    return (1 - tq * tq + 2 * a) / (1 + tq * tq)


def contain_margin_exact(t, cx, cy):
    """exact min over the four walls of (centre - w/2) resp. (s0 - centre - w/2).
    >= 0  <=>  the closed unit square at (cx,cy) with tilt t lies inside [0,s0]^2.
    (P2') quantifies over pairs of closed unit squares IN [0,s0]^2, so a placement with a
    negative margin is not an admissible test object and must never become a column."""
    tq, xq, yq = Fr(t), Fr(cx), Fr(cy)
    h = w_exact(tq) / 2
    return min(xq - h, yq - h, S0Q - xq - h, S0Q - yq - h)


def contained_mask_exact(t, C):
    """(n,) bool + (n,) float margins, computed in exact rational arithmetic."""
    marg = np.array([float(contain_margin_exact(t[a], C[a, 0], C[a, 1])) for a in range(len(t))])
    ok = np.array([contain_margin_exact(t[a], C[a, 0], C[a, 1]) >= 0 for a in range(len(t))])
    return ok, marg


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
def greedy_diverse(X, keep, C=None, tbin=None, min_sep=0.0):
    """farthest-point sampling of `keep` rows of X (n,d), max-min Euclidean.
    If min_sep > 0, a candidate whose CENTRE (C) is within min_sep of an already-kept square of
    the SAME tilt bin is barred: that is what keeps the membership depth (and hence the row
    density of the pair LP) down."""
    n = len(X)
    if n <= keep and min_sep <= 0.0:
        return np.arange(n)
    sel = [0]
    d = np.linalg.norm(X - X[0], axis=1)
    barred = np.zeros(n, dtype=bool)
    while len(sel) < keep:
        if min_sep > 0.0:
            j0 = sel[-1]
            close = (np.hypot(C[:, 0] - C[j0, 0], C[:, 1] - C[j0, 1]) < min_sep) & (tbin == tbin[j0])
            barred |= close
            barred[j0] = True
        dd = np.where(barred, -1.0, d)
        j = int(np.argmax(dd))
        if dd[j] <= 0.0:
            break
        sel.append(j)
        d = np.minimum(d, np.linalg.norm(X - X[j], axis=1))
    return np.array(sel)


def grid_vals(lo, hi, step):
    if hi < lo:
        return np.zeros(0)
    v = np.arange(0.0, S0 + 1e-12, step)
    v = v[(v >= lo - 1e-12) & (v <= hi + 1e-12)]
    return np.unique(np.concatenate([[lo, hi], v]))


def build_catalog(pins, boxes, args, fh, extra=None):
    cap_total, cap_m2, cap_m1 = args.cap_total, args.cap_m2, args.cap_m1
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
        g = greedy_diverse(X, min(cap, len(sel)), C=en_c[sel],
                           tbin=np.round(en_t[sel] / 0.05).astype(int), min_sep=args.min_sep)
        pick.append(sel[g])
        stats["enrich_m%s_avail" % lo_m] = int(len(sel))
        stats["enrich_m%s_kept" % lo_m] = int(len(g))
    pick = np.concatenate(pick) if pick else np.zeros(0, dtype=int)

    T = list(en_t[pick])
    C = list(map(tuple, en_c[pick]))

    # ---- explicit extra placements (control family / zone perturbations), before the coarse fill
    # These bypass the grid clip, so they need BOTH filters applied explicitly.
    n_extra = n_extra_rej_core = n_extra_rej_cont = 0
    if extra:
        for (t, cx, cy) in extra:
            if not core_free_mask(np.array([[cx, cy]]), theta_of(t), pins)[0]:
                n_extra_rej_core += 1
                continue
            if ENFORCE_CONTAINMENT and contain_margin_exact(t, cx, cy) < 0:
                n_extra_rej_cont += 1
                continue
            T.append(t); C.append((cx, cy)); n_extra += 1
    stats["extra_added"] = n_extra
    stats["extra_rejected_not_core_free"] = n_extra_rej_core
    stats["extra_rejected_not_contained"] = n_extra_rej_cont

    # ---- coarse fill
    room = min(args.cap_coarse, cap_total - len(T))
    if room > 0 and len(co_t):
        X = np.column_stack([co_c[:, 0], co_c[:, 1], 2.0 * co_t])
        g = greedy_diverse(X, min(room, len(co_t)), C=co_c,
                           tbin=np.round(co_t / 0.05).astype(int), min_sep=args.min_sep)
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
    # ---- FINAL exact containment sweep over the assembled catalog (defence in depth)
    okc, margc = contained_mask_exact(t, C)
    stats["containment_violators"] = int((~okc).sum())
    stats["min_containment_margin"] = float(margc.min()) if len(margc) else None
    if ENFORCE_CONTAINMENT and not okc.all():
        t, C, th, mask = t[okc], C[okc], th[okc], mask[okc]
        margc = margc[okc]
    stats["min_containment_margin_kept"] = float(margc.min()) if len(margc) else None
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


def catalog_from_list(placements, pins, boxes):
    """build a catalog dict from an explicit [[t,cx,cy],...] list (e.g. a D1-enriched catalog)."""
    t = np.array([p[0] for p in placements], dtype=float)
    C = np.array([[p[1], p[2]] for p in placements], dtype=float)
    th = np.array([theta_of(x) for x in t])
    mask = np.zeros(len(t), dtype=np.int64)
    cm = np.zeros(len(t))
    for a in range(len(t)):
        mask[a] = box_mask_bits(C[a:a + 1], th[a], boxes)[0]
        cm[a] = core_margin(C[a:a + 1], th[a], pins)[0]
    m = np.array([bin(int(x)).count("1") for x in mask])
    keep = cm >= -EPS_CORE                      # re-verify core-freeness of an imported catalog
    okc, margc = contained_mask_exact(t, C)     # and containment, exactly
    n_bad_cont = int((~okc).sum())
    if ENFORCE_CONTAINMENT:
        keep = keep & okc
    stats = dict(n_placements=int(keep.sum()), imported=int(len(t)),
                 dropped_not_core_free=int((~(cm >= -EPS_CORE)).sum()),
                 dropped_not_contained=n_bad_cont,
                 min_containment_margin=float(margc.min()) if len(margc) else None,
                 min_containment_margin_kept=float(margc[keep].min()) if keep.any() else None,
                 min_core_margin=float(cm[keep].min()) if keep.any() else None,
                 m_histogram={int(k): int(v) for k, v in zip(*np.unique(m[keep], return_counts=True))})
    return dict(t=t[keep], th=th[keep], C=C[keep], mask=mask[keep], m=m[keep], stats=stats)


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


def maximal_by_pattern(P, A, protect=0, block=96):
    """Reduce a point set to inclusion-MAXIMAL membership patterns.

    SOUNDNESS (this is the A71 wall-breaker, so state it plainly).  For z >= 0 the (P2') load
        L(c,d) = sum_{i<j} z_ij ([c in Qi][d in Qj] + [c in Qj][d in Qi])
    depends on (c,d) only through the membership sets M(c), M(d), and is monotone
    non-decreasing in each: adding an index to M(c) can only add non-negative terms.  Therefore

        M(c) subset M(c')   ==>   L(c,d) <= L(c',d)  for every d,

    so (i) the constraint row of (c,d) is implied by the row of (c',d) together with z >= 0 --
    dropping it does not enlarge the LP feasible set -- and (ii) max_{c != d} L(c,d) over a
    point family equals the max over its inclusion-maximal patterns.  Points with M(c) = {} have
    load 0 and are dropped.  The first `protect` rows are kept unconditionally.

    Returns (P', A') with A' the distinct inclusion-maximal patterns (one representative point
    each), protected rows first-come.
    """
    n = A.shape[0]
    if n == 0:
        return P, A
    prot = np.zeros(n, dtype=bool)
    prot[:protect] = True
    live = A.any(axis=1) | prot
    P, A, prot = P[live], A[live], prot[live]
    n = A.shape[0]
    if n == 0:
        return P, A
    B = np.packbits(A, axis=1)                       # (n, w) uint8 bitsets
    # distinct patterns, first occurrence wins (protected rows are at the front)
    _, first = np.unique(B, axis=0, return_index=True)
    uniq = np.sort(first)
    uniq = np.unique(np.concatenate([np.nonzero(prot)[0], uniq]))
    Bu, pc = B[uniq], A[uniq].sum(axis=1).astype(np.int64)
    nu = len(uniq)
    srt = np.argsort(-pc, kind="stable")
    Bs, pcs = Bu[srt], pc[srt]
    keep_s = np.ones(nu, dtype=bool)
    lo = 0
    for v in np.unique(pcs)[::-1]:                   # descending popcount groups
        idxs = np.nonzero(pcs == v)[0]
        if lo > 0:
            R = Bs[:lo][keep_s[:lo]]                 # strictly larger, still maximal
            if len(R):
                for a in range(0, len(idxs), block):
                    blk = idxs[a:a + block]
                    dom = ((Bs[blk][:, None, :] & ~R[None, :, :]) == 0).all(axis=2).any(axis=1)
                    keep_s[blk] &= ~dom
        lo += len(idxs)
    keep_u = np.zeros(nu, dtype=bool)
    keep_u[srt[keep_s]] = True
    keep_u |= prot[uniq]                             # never drop a protected anchor
    sel = np.sort(uniq[keep_u])
    return P[sel], A[sel]


# ------------------------------------------------------------------ load / cuts
def chunk_load_topk(Af, Z, k, exclude=None, chunk=384, only_upper=True, tol=EPS_LOAD):
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
            v = 1.0 + tol
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
class RowStore:
    """The (P2') rows found so far, keyed by their SUPPORT set of pair-columns.  Shared across
    betas: a row is valid for every beta (the constraint does not depend on it), so each new beta
    starts warm from every cut the previous betas paid for."""

    def __init__(self):
        self.keys = {}           # support bytes -> index
        self.rows = []
        self.pts = []            # the (c, d) point pair that generated each row (for the primal)
        self.pidx = []           # the same pair as INDICES into the global point family
        self.nnz = 0
        self.purges = []         # how often each row has been purged from the model

    def add(self, sup, pt=None, pidx=None):
        """returns (index, is_new)."""
        key = sup.tobytes()
        if key in self.keys:
            return self.keys[key], False
        i = len(self.rows)
        self.keys[key] = i
        self.rows.append(sup)
        self.pts.append(pt)
        self.pidx.append(pidx)
        self.purges.append(0)
        self.nnz += len(sup)
        return i, True


def diverse_cuts(cuts, keep, per_point):
    """thin a violated-pair list so no single point anchors more than `per_point` of the cuts.
    Top-load violators cluster in one deep pocket; spreading them buys far more separation per
    row (and rows are what the solve time is made of)."""
    if per_point <= 0:
        return cuts[:keep]
    use, out = {}, []
    for (v, c, d) in cuts:
        if use.get(c, 0) >= per_point or use.get(d, 0) >= per_point:
            continue
        use[c] = use.get(c, 0) + 1
        use[d] = use.get(d, 0) + 1
        out.append((v, c, d))
        if len(out) >= keep:
            break
    return out


def set_solver(h, solver, crossover, tlim):
    """A71: solver selection.  `run_crossover` is ignored by the simplex path, harmless there."""
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.setOptionValue("time_limit", float(tlim))
    h.setOptionValue("solver", solver)
    h.setOptionValue("run_crossover", "on" if crossover else "off")


def solve_beta(cat, I, J, m2, P, A, beta, args, fh, store, boxes):
    ns = len(cat["t"])
    npair = len(I)
    t0 = time.time()
    solver_times = []

    PID = -np.ones((ns, ns), dtype=np.int64)
    PID[I, J] = np.arange(npair)
    PID[J, I] = np.arange(npair)

    obj = 1.0 + beta * m2.astype(float)

    h = highspy.Highs()
    set_solver(h, args.lp_solver, args.loop_crossover == "on", args.lp_time)
    h.changeObjectiveSense(highspy.ObjSense.kMaximize)
    h.addCols(npair, obj, np.zeros(npair), np.full(npair, float(args.zub)),
              0, np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))

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

    # ---- model bookkeeping: `active` maps HiGHS row order -> store row index, so rows can be
    # purged when they go slack and re-added later if they ever bind again.
    active, born, in_model = [], [], set()
    state = dict(nnz=0)

    def push(idxs, rnd=0):
        """append store rows (by index) to HiGHS (CSR)."""
        # de-duplicate WITHIN the batch as well as against the model: two different point pairs
        # in the same round can share a row support, and pushing that support twice would put a
        # duplicate row in HiGHS and split its dual across the copies.
        seen, uniq = set(), []
        for i in idxs:
            if i in in_model or i in seen:
                continue
            seen.add(i)
            uniq.append(i)
        idxs = uniq
        if not idxs:
            return 0, 0
        sups = [store.rows[i] for i in idxs]
        starts, run = [], 0
        for sup in sups:
            starts.append(run)
            run += len(sup)
        ind = np.concatenate(sups).astype(np.int32)
        st = np.array(starts, dtype=np.int32)
        nrow0 = h.getNumRow()
        h.addRows(len(sups), np.full(len(sups), -highspy.kHighsInf), np.ones(len(sups)),
                  len(ind), st, ind, np.ones(len(ind)))
        if h.getNumRow() != nrow0 + len(sups):
            raise RuntimeError("addRows rejected %d rows (have %d, wanted %d)"
                               % (len(sups), h.getNumRow(), nrow0 + len(sups)))
        for i in idxs:
            active.append(i)
            born.append(rnd)
            in_model.add(i)
        state["nnz"] += len(ind)
        return len(sups), len(ind)

    def add_rows(Amat, pairs, pts=None, rnd=0):
        want = []
        for (c, d) in pairs:
            sup = row_support_from_masks(Amat[c], Amat[d])
            if sup is None:
                continue
            pp = None if pts is None else (tuple(pts[c]), tuple(pts[d]))
            i, _ = store.add(sup, pp, (int(c), int(d)))
            want.append(i)
        return push(want, rnd)

    def purge(z, rnd):
        """drop rows whose load is far below 1 and that have had at least --purge_age rounds to
        prove themselves.  Dropping a slack row can only ENLARGE the feasible set, so the LP
        value stays a valid upper bound on the restricted optimum; if the row ever binds again
        the separator re-finds it (RowStore keeps its support, so nothing is recomputed)."""
        if not active:
            return 0
        loads = np.array([z[store.rows[i]].sum() for i in active])
        old = np.array(born) <= rnd - args.purge_age
        reuse = np.array([store.purges[i] for i in active]) < args.purge_max
        kill = np.nonzero((loads < 1.0 - args.purge_slack) & old & reuse)[0]
        if len(kill) < args.purge_min:
            return 0
        h.deleteRows(len(kill), kill.astype(np.int32))
        killset = set(int(a) for a in kill)
        for a in killset:
            i = active[a]
            in_model.discard(i)
            store.purges[i] += 1
            state["nnz"] -= len(store.rows[i])
        keep = [a for a in range(len(active)) if a not in killset]
        na = [active[a] for a in keep]
        nb = [born[a] for a in keep]
        active[:] = na
        born[:] = nb
        return len(kill)

    # ---- warm start from every row any earlier beta paid for
    Af = A.astype(float)
    depth = A.sum(axis=1)
    if store.rows:
        nr, nnz = push(range(len(store.rows)), 0)
        log("beta=%.4g: warm start rows=%d nnz=%d cols=%d" % (beta, nr, nnz, npair), fh)
    else:
        rng0 = np.random.default_rng(args.seed)
        deep = np.argsort(-depth)[:args.seed_deep]
        seed_pairs = [(int(deep[a]), int(deep[b]))
                      for a in range(len(deep)) for b in range(a + 1, len(deep))]
        rp = rng0.integers(0, len(P), size=(args.n_seed_random, 2))
        seed_pairs += [(int(a), int(b)) for a, b in rp if a != b]
        nr, nnz = add_rows(A, seed_pairs, pts=P, rnd=0)
        log("beta=%.4g: seed rows=%d nnz=%d cols=%d (pts=%d, depth mean %.1f max %d)"
            % (beta, nr, nnz, npair, len(P), depth.mean(), depth.max()), fh)

    last_good = None
    best = (None, None, None, None)          # (value, z, Lmax, round) of the best FEASIBLE iterate
    rounds = 0
    status_note = "converged"
    lm_cut = None
    lm_fine = None
    fine_info = dict(point_family="A71 global inclusion-maximal membership patterns",
                     n_points=int(len(P)), depth_mean=float(depth.mean()),
                     depth_max=int(depth.max()) if len(depth) else 0)
    converged = False
    stop = False
    ab_at = set(int(x) for x in args.ab_rounds.split(",") if x.strip())

    def clean_solve(tag, solver=None, xover=None, tlim=None):
        """final solve of an outer pass: basic solution + row duals.  Skipped when it would just
        repeat the loop configuration (the loop's own last solve is already that solution)."""
        solver = solver or args.final_solver
        xover = xover or args.final_crossover
        tlim = tlim or args.final_lp_time
        if solver == args.lp_solver and xover == args.loop_crossover:
            log("beta=%.4g %s: FINAL config == loop config, reusing last solve" % (beta, tag), fh)
            return h.getModelStatus()
        set_solver(h, solver, xover == "on", tlim)
        ts = time.time()
        h.run()
        dt = time.time() - ts
        solver_times.append(dict(kind="final:" + tag, solver=solver, crossover=xover,
                                 rows=int(h.getNumRow()), seconds=dt,
                                 status=str(h.getModelStatus()),
                                 value=float(h.getInfo().objective_function_value)))
        log("beta=%.4g %s: FINAL %s/xover=%s -> %s value=%.6f (%.0fs)"
            % (beta, tag, solver, xover, h.getModelStatus(),
               h.getInfo().objective_function_value, dt), fh)
        set_solver(h, args.lp_solver, args.loop_crossover == "on", args.lp_time)
        return h.getModelStatus()

    for outer in range(args.outer_passes):
        # ---------- inner: cut on the GLOBAL maximal-pattern point family (= the fine family)
        while rounds < args.max_rounds:
            rounds += 1
            ts = time.time()
            h.run()
            dts = time.time() - ts
            st = h.getModelStatus()
            solver_times.append(dict(kind="loop", solver=args.lp_solver,
                                     crossover=args.loop_crossover, round=rounds,
                                     rows=int(h.getNumRow()), nnz=int(state["nnz"]), seconds=dts,
                                     status=str(st)))
            inf0 = h.getInfo()
            # HiGHS IPM WITHOUT crossover cannot certify a basis, so it reports kUnknown even
            # when it has a perfectly good interior solution.  For SEPARATION that solution is
            # all we need (and it separates better than a degenerate vertex): accept it as long
            # as the primal is flagged feasible.  Everything reported comes from clean_solve().
            ok_loop = (st == highspy.HighsModelStatus.kOptimal
                       or (st == highspy.HighsModelStatus.kUnknown
                           and inf0.primal_solution_status == highspy.kSolutionStatusFeasible))
            if not ok_loop:
                status_note = "non-optimal LP status %s at round %d" % (st, rounds)
                log("beta=%.4g: %s (primal_status=%s)" % (beta, status_note,
                                                          inf0.primal_solution_status), fh)
                stop = True
                break
            z = np.array(h.getSolution().col_value)
            z = np.clip(z, 0.0, float(args.zub))
            val = float(inf0.objective_function_value)
            solver_times[-1]["primal_inf"] = float(inf0.max_primal_infeasibility)
            solver_times[-1]["ipm_iters"] = int(inf0.ipm_iteration_count)
            if st == highspy.HighsModelStatus.kOptimal:
                last_good = (val, z.copy())
            Z = np.zeros((ns, ns))
            Z[I, J] = z
            Z[J, I] = z
            raw, lm_cut = chunk_load_topk(Af, Z, args.max_cuts * args.cut_pool, chunk=args.chunk,
                                          tol=args.cut_tol)
            cuts = diverse_cuts(raw, args.max_cuts, args.cuts_per_point)
            # Purging bounces Lmax back up (a dropped row is a dropped cut), so it is switched
            # off once the iterate is close to feasible -- that is the endgame, and there the
            # model is small enough anyway.
            npg = (purge(z, rounds)
                   if (args.purge_every and rounds % args.purge_every == 0
                       and lm_cut > args.purge_stop_lmax) else 0)
            nsup = int((z > 1e-9).sum())
            log("beta=%.4g p%d r%d: value=%.6f Lmax=%.6f viol=%d/%d supz=%d rows=%d nnz=%d "
                "purged=%d (lp %.1fs, tot %.0fs)"
                % (beta, outer, rounds, val, lm_cut, len(cuts), len(raw), nsup, h.getNumRow(),
                   state["nnz"], npg, dts, time.time() - t0), fh)
            if rounds in ab_at:
                bench_solvers(store, npair, obj, args, fh, tag="r%d" % rounds)
            # A CERTIFICATE OF CONVERGENCE.  lm_cut is the load maximum of THIS z over the whole
            # point family, so lm_cut <= 1 + tol makes z feasible for the FULL (all point pairs)
            # restricted LP, while `val` is the optimum of a row-subset relaxation of it and is
            # therefore an upper bound.  The two meeting closes the bracket.  Note the interior
            # (crossover-off) iterate is what achieves this: a crossover VERTEX of the same
            # optimal face routinely violates rows that are not in the model, which is why the
            # feasible iterate -- not the vertex -- is what gets reported and dumped.
            if lm_cut <= args.fine_tol and (best[0] is None or val >= best[0] - 1e-9):
                if best[0] is None or val > best[0] or lm_cut < best[2]:
                    best = (val, z.copy(), lm_cut, rounds)
            if not cuts:
                break
            nr, nnz = add_rows(A, [(c, d) for (_, c, d) in cuts], pts=P, rnd=rounds)
            if nr == 0 and npg == 0:
                status_note = "no new distinct rows at round %d" % rounds
                stop = True
                break
            if state["nnz"] > args.max_nnz or h.getNumRow() > args.max_rows:
                status_note = ("nnz/row cap hit at round %d (nnz=%d rows=%d)"
                               % (rounds, state["nnz"], h.getNumRow()))
                log("beta=%.4g: %s" % (beta, status_note), fh)
                stop = True
                break
            if time.time() - t0 > args.cls_budget:
                status_note = "time budget hit at round %d" % rounds
                log("beta=%.4g: %s" % (beta, status_note), fh)
                stop = True
                break
        else:
            status_note = "round cap %d reached" % args.max_rounds
            stop = True

        # the inner loop already certified feasibility of its own iterate over the whole family
        if best[0] is not None and lm_cut is not None and lm_cut <= args.fine_tol:
            converged = True
            lm_fine = lm_cut
            log("beta=%.4g p%d: CONVERGED on the interior iterate (value=%.9f, Lmax=%.9f <= %g) "
                "-- relaxation optimum == feasible objective" % (beta, outer, best[0], best[2],
                                                                 args.fine_tol), fh)
            if not (status_note.startswith("round cap") or status_note.startswith("nnz")
                    or status_note.startswith("time budget")):
                status_note = "converged"
            break

        # ---------- outer: clean (basic) solve, then re-check on the same exact family
        clean_solve("p%d" % outer)
        z = np.array(h.getSolution().col_value)
        Z = np.zeros((ns, ns))
        Z[I, J] = z
        Z[J, I] = z
        fcuts, lm_fine = chunk_load_topk(Af, Z, args.max_cuts, chunk=args.chunk,
                                         tol=args.fine_tol - 1.0)
        log("beta=%.4g p%d: fine Lmax=%.6f (violators %d)" % (beta, outer, lm_fine, len(fcuts)), fh)
        if lm_fine <= args.fine_tol:
            converged = True
            if not (status_note.startswith("round cap") or status_note.startswith("nnz")
                    or status_note.startswith("time budget")):
                status_note = "converged"
            break
        if stop or outer == args.outer_passes - 1 or not fcuts:
            break
        nr, _ = add_rows(A, [(c, d) for (_, c, d) in fcuts], pts=P, rnd=rounds)
        log("beta=%.4g p%d: fed %d clean-solution violator rows back" % (beta, outer, nr), fh)
        if nr == 0:
            break

    # ---- headline solve: one last, generously time-boxed run on the final row set
    z_loop = np.array(h.getSolution().col_value)
    val_loop = float(h.getInfo().objective_function_value)
    st_loop = h.getModelStatus()
    headline = None
    if args.headline_solver != "none":
        sth = clean_solve("headline", args.headline_solver, args.headline_crossover,
                          args.headline_time)
        if sth == highspy.HighsModelStatus.kOptimal:
            headline = dict(solver=args.headline_solver, crossover=args.headline_crossover,
                            value=float(h.getInfo().objective_function_value), status=str(sth))
        else:
            log("beta=%.4g: headline solve did NOT reach kOptimal (%s); keeping the loop's "
                "interior optimum" % (beta, sth), fh)
            headline = dict(solver=args.headline_solver, crossover=args.headline_crossover,
                            value=None, status=str(sth))

    total_nnz = state["nnz"]
    st = h.getModelStatus()
    z = np.array(h.getSolution().col_value)
    val = float(h.getInfo().objective_function_value)
    if st != highspy.HighsModelStatus.kOptimal:
        # IPM-without-crossover reports kUnknown; that solution is still the one we want.
        if (st == highspy.HighsModelStatus.kUnknown
                and h.getInfo().primal_solution_status == highspy.kSolutionStatusFeasible):
            pass
        elif len(z_loop) and st_loop in (highspy.HighsModelStatus.kOptimal,
                                         highspy.HighsModelStatus.kUnknown):
            val, z, st = val_loop, z_loop, st_loop
            status_note += " | reported the loop's last solve (headline solve was %s)" % st
        elif last_good is not None:
            val, z = last_good[0], last_good[1]  # never report a time-limited garbage solve
            status_note += " | reported last OPTIMAL solve (final solve was %s)" % st
    z = np.clip(z, 0.0, float(args.zub))
    # Prefer the best FEASIBLE iterate (Lmax <= fine_tol on the whole family): that is the one a
    # certificate can be built from.  A crossover vertex of the same optimal face is fine as a
    # value but is typically NOT feasible off-model, so it must not be what gets dumped.
    if best[0] is not None:
        z_here = np.clip(z, 0.0, float(args.zub))
        Zh = np.zeros((ns, ns)); Zh[I, J] = z_here; Zh[J, I] = z_here
        lm_here = chunk_lmax(Af, Zh, chunk=args.chunk)
        if lm_here > args.fine_tol or best[0] > val + 1e-9:
            log("beta=%.4g: reporting the FEASIBLE iterate from round %d (value=%.9f, "
                "Lmax=%.9f) instead of the final solve (value=%.9f, Lmax=%.9f)"
                % (beta, best[3], best[0], best[2], val, lm_here), fh)
            val, z = best[0], best[1]
            lm_fine = best[2]
            status_note += " | reported the feasible interior iterate of round %d" % best[3]
        else:
            lm_fine = lm_here
    Z = np.zeros((ns, ns))
    Z[I, J] = z
    Z[J, I] = z
    fine_info["Lmax_final"] = float(lm_fine) if lm_fine is not None else None

    n_at_ub = int(np.sum(z > args.zub - 1e-6))
    sup = np.nonzero(z > 1e-9)[0]
    mass = float(z.sum())
    mbar2 = float((z * m2).sum() / mass) if mass > 0 else 0.0

    order = np.argsort(-z)[:args.top_k]
    top10 = []
    for k in order:
        if z[k] <= 1e-9:
            break
        i, j = int(I[k]), int(J[k])
        top10.append(dict(pair=int(k), z=float(z[k]), m2=int(m2[k]),
                          a=dict(t=float(cat["t"][i]), cx=float(cat["C"][i, 0]), cy=float(cat["C"][i, 1])),
                          b=dict(t=float(cat["t"][j]), cx=float(cat["C"][j, 0]), cy=float(cat["C"][j, 1]))))

    # tight-constraint census on the final solution: duals are indexed by the ACTIVE row order,
    # so scatter them back onto store row indices (purged rows carry dual 0).
    rd = np.array(h.getSolution().row_dual)
    row_dual = np.zeros(len(store.rows))
    dual_gap = None
    if len(rd) >= len(active) and active:
        np.add.at(row_dual, np.array(active, dtype=int), rd[:len(active)])
        # strong duality self-check: with no active column bound (n_z_at_ub == 0) the sum of the
        # row duals must equal the LP optimum.  A mismatch means the dual is being mis-mapped.
        dual_gap = float(row_dual.sum() - float(h.getInfo().objective_function_value))
        log("beta=%.4g: dual check sum(y)=%.9f vs objective=%.9f (gap %.3e)"
            % (beta, row_dual.sum(), h.getInfo().objective_function_value, dual_gap), fh)
    loads = np.array([z[store.rows[i]].sum() for i in active]) if active else np.zeros(0)
    n_tight = int(np.sum(loads > 1.0 - 1e-6))
    return dict(value=val, z=z, Z=Z, support=sup, mbar2=mbar2, top10=top10,
                row_dual=row_dual, n_tight_rows=n_tight, solver_times=solver_times,
                headline=headline, n_active_rows=len(active), dual_gap=dual_gap,
                rounds=rounds, n_rows=int(h.getNumRow()), nnz=total_nnz, n_at_ub=n_at_ub,
                status=str(st), note=status_note, Lmax_cut=lm_cut, Lmax_fine=lm_fine,
                converged=converged, fine=fine_info, seconds=time.time() - t0)


# ------------------------------------------------------------------ solver A/B
def bench_solvers(store, npair, obj, args, fh, tag=""):
    """Time-boxed A/B/C on a FRESH model built from the rows found so far.  Reports value and
    wall time for simplex, ipm (no crossover) and pdlp so the loop solver can be chosen on
    evidence rather than on faith."""
    combos = [("simplex", "on"), ("ipm", "off"), ("ipm", "on"), ("pdlp", "off")]
    rows = list(store.rows)
    starts, run = [], 0
    for sup in rows:
        starts.append(run)
        run += len(sup)
    ind = np.concatenate(rows).astype(np.int32) if rows else np.zeros(0, dtype=np.int32)
    stt = np.array(starts, dtype=np.int32)
    out = []
    spent = 0.0
    for (slv, xo) in combos:
        if spent > args.ab_budget:
            log("AB %s: budget spent, skipping %s/%s" % (tag, slv, xo), fh)
            continue
        hb = highspy.Highs()
        set_solver(hb, slv, xo == "on", min(args.ab_each, args.ab_budget - spent))
        hb.changeObjectiveSense(highspy.ObjSense.kMaximize)
        hb.addCols(npair, obj, np.zeros(npair), np.full(npair, float(args.zub)),
                   0, np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))
        hb.addRows(len(rows), np.full(len(rows), -highspy.kHighsInf), np.ones(len(rows)),
                   len(ind), stt, ind, np.ones(len(ind)))
        ts = time.time()
        try:
            hb.run()
            stat = str(hb.getModelStatus())
            val = float(hb.getInfo().objective_function_value)
        except Exception as ex:                      # pdlp may not be built in every wheel
            stat, val = "EXC:%s" % ex, float("nan")
        dt = time.time() - ts
        spent += dt
        rec = dict(tag=tag, solver=slv, crossover=xo, rows=len(rows), nnz=int(store.nnz),
                   seconds=dt, status=stat, value=val)
        out.append(rec)
        log("AB %s: %-8s xover=%-3s rows=%d nnz=%d -> %-34s value=%.6f (%.1fs)"
            % (tag, slv, xo, len(rows), store.nnz, stat, val, dt), fh)
        del hb
    return out


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


def fine_eval(cat, Z, sup_sq, boxes, args, fh, want_cuts=0):
    """independent validity check of the final z on a much finer point set; returns
    (Lmax, info, points, violator list) so the violators can be fed back as rows."""
    if len(sup_sq) == 0:
        return 1.0, {}, np.zeros((0, 2)), []
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
        return 1.0, info, P, []
    Zs = Z[np.ix_(sup_sq, sup_sq)]
    cuts, lm = chunk_load_topk(A.astype(float), Zs, want_cuts, chunk=args.chunk,
                               tol=args.fine_tol - 1.0)
    return lm, info, P, cuts


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


# ------------------------------------------------------------------ D2 emission prep
def _q(x, den=10 ** 6, up=False):
    f = Fr(x).limit_denominator(10 ** 12) * den
    n = math.ceil(f) if up else round(f)
    return "%d/%d" % (int(n), den)


def dump_primal(args, cat, I, J, m2, store, r, beta, thresh_base, mboxes, fh):
    """The row duals of the packing LP ARE the restricted covering primal: each row is the point
    pattern (c,d) of an atom, its dual is the atom weight.  Emitted in pair-certificate-v1 atom
    shape (exact rational strings).  Positions round to 1e-6; WEIGHTS ROUND UP so the restricted
    covering inequalities A^T y >= obj stay satisfied."""
    y = r["row_dual"]
    atoms, W2 = [], Fr(0)
    for k in np.nonzero(y > 1e-12)[0]:
        pp = store.pts[k]
        if pp is None:
            continue
        (cx, cy), (dx, dy) = pp
        w = _q(float(y[k]), up=True)
        W2 += Fr(w)
        atoms.append(dict(px=_q(cx), py=_q(cy), qx=_q(dx), qy=_q(dy), w=w))
    # residual check of the restricted rows with the ROUNDED-UP weights
    obj = 1.0 + beta * m2.astype(float)
    cov = np.zeros(len(I))
    for k in np.nonzero(y > 1e-12)[0]:
        if store.pts[k] is None:
            continue
        np.add.at(cov, store.rows[k], float(Fr(_q(float(y[k]), up=True))))
    deficit = float(np.max(obj - cov)) if len(cov) else 0.0
    out = dict(format="pair-certificate-v1", s=str(Fr("969271/250000")), n=11,
               k=int(len(json.load(open(BOXSPEC))["classes"][args.cls]["pins"])),
               m=int(mboxes), beta=_q(beta), atoms=atoms, total=str(W2),
               provenance=dict(source="A71 pairlp413.py restricted covering primal (row duals)",
                               cls=args.cls, beta=beta, lp_value=r["value"],
                               threshold="%d + beta*%d" % (thresh_base, mboxes),
                               n_atoms=len(atoms), W2_float=float(W2),
                               restricted_row_max_deficit=deficit,
                               note=("cores/boxes NOT filled in: this is the atom measure only. "
                                     "Positions rounded to 1e-6 (membership may shift); weights "
                                     "rounded UP to 1e-6. max_deficit<=0 means every restricted "
                                     "row still holds with the rounded weights.")))
    fp = os.path.join(BASE, "results", "pair_primal_%s_b%s.json"
                      % (args.cls, ("%g" % beta).replace(".", "")))
    json.dump(out, open(fp, "w"), indent=1)
    log("dumped %d atoms (W2=%.6f, restricted-row max deficit %.3e) -> %s"
        % (len(atoms), float(W2), deficit, fp), fh)

    rp = os.path.join(BASE, "results", "pair_rows_%s.json" % args.cls)
    json.dump(dict(cls=args.cls, s0=S0, n_placements=int(len(cat["t"])),
                   placements=[[float(cat["t"][a]), float(cat["C"][a, 0]), float(cat["C"][a, 1])]
                               for a in range(len(cat["t"]))],
                   n_pairs=int(len(I)),
                   pairs=[[int(a), int(b), int(c)] for a, b, c in zip(I, J, m2)],
                   note="disjoint core-free catalog pairs (i, j, m2) = the restricted (P2') rows"),
              open(rp, "w"))
    log("dumped %d restricted rows -> %s" % (len(I), rp), fh)


# ------------------------------------------------------------------ column generation
def dual_matrix(row_dual, store, npts):
    """(npts, npts) symmetric matrix of the row weights, indexed by the generating point pair.
    Negative entries (simplex noise at the 1e-11 level) are clamped to 0 so that y >= 0."""
    y = np.zeros((npts, npts))
    for i in np.nonzero(np.abs(row_dual) > 1e-13)[0]:
        pi = store.pidx[i]
        if pi is None:
            continue
        w = max(float(row_dual[i]), 0.0)
        y[pi[0], pi[1]] += w
        y[pi[1], pi[0]] += w
    return y


def price_catalog(y, P, ecat, beta, chunk=256):
    """reduced cost  c_ij - (A^T y)_ij  of every DISJOINT pair of the pricing catalog.
    Returns (I, J, deficits, per-square best deficit)."""
    n = len(ecat["t"])
    I, J = disjoint_pairs(ecat)
    m2 = np.array([bin(int(ecat["mask"][a] & ecat["mask"][b])).count("1") for a, b in zip(I, J)])
    obj = 1.0 + beta * m2.astype(float)
    A = membership(P, ecat).T.astype(np.float64)          # (n, npts)
    B = A @ y
    defs = np.empty(len(I))
    for r0 in range(0, n, chunk):
        r1 = min(n, r0 + chunk)
        M = B[r0:r1] @ A.T
        s = (I >= r0) & (I < r1)
        defs[s] = obj[s] - M[I[s] - r0, J[s]]
    score = np.full(n, -np.inf)
    np.maximum.at(score, I, defs)
    np.maximum.at(score, J, defs)
    return I, J, defs, score


def pick_new_squares(ecat, score, have, keep, min_sep):
    """top-scoring pricing-catalog placements not already in the catalog, thinned so that no two
    accepted squares of the same tilt bin sit within min_sep of each other."""
    order = np.argsort(-score)
    tb = np.round(ecat["t"] / 0.05).astype(int)
    out, acc = [], []
    for a in order:
        if score[a] <= 0:
            break
        key = (round(float(ecat["t"][a]), 9), round(float(ecat["C"][a, 0]), 9),
               round(float(ecat["C"][a, 1]), 9))
        if key in have:
            continue
        if min_sep > 0 and any(tb[a] == b and
                               math.hypot(ecat["C"][a, 0] - cx, ecat["C"][a, 1] - cy) < min_sep
                               for (b, cx, cy) in acc):
            continue
        acc.append((tb[a], float(ecat["C"][a, 0]), float(ecat["C"][a, 1])))
        out.append([float(ecat["t"][a]), float(ecat["C"][a, 0]), float(ecat["C"][a, 1])])
        have.add(key)
        if len(out) >= keep:
            break
    return out


def build_point_family(cat, boxes, args, fh, rng):
    """the A71 global family: arrangement-cell representatives of the WHOLE catalog, reduced to
    inclusion-maximal membership patterns.  With a large catalog the raw intersection set is
    subsampled to --base_cap first (vertices are always kept); that is a weakening of the
    heuristic completeness, and it is recorded in the output."""
    t_pts = time.time()
    allsq = np.arange(len(cat["t"]))
    V = square_vertices(cat, allsq)
    X, skipped = seg_intersections(cat, allsq, cap=args.seg_cap)
    nX = len(X)
    if len(X) > max(0, args.base_cap - len(V)):
        X = X[rng.choice(len(X), max(0, args.base_cap - len(V)), replace=False)]
    base = np.vstack([V, X]) if len(X) else V
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    if args.nudge8:
        dirs += [(-1, 0), (1, 0), (0, -1), (0, 1)]
    pieces = [base + np.array([ex * args.probe_eps, ey * args.probe_eps]) for (ex, ey) in dirs]
    pieces.append(build_points(cat, boxes, args.fine_global, args.fine_local, args.fine_radius))
    Praw = np.vstack(pieces)
    Praw = Praw[(Praw[:, 0] >= -1e-9) & (Praw[:, 0] <= S0 + 1e-9)
                & (Praw[:, 1] >= -1e-9) & (Praw[:, 1] <= S0 + 1e-9)]
    n_raw = len(Praw)
    A = membership(Praw, cat)
    P1, A1 = dedupe_by_pattern(Praw, A)
    if args.no_maximal:
        P, A = P1, A1
        red = "dedupe-only (A66 behaviour)"
    else:
        P, A = maximal_by_pattern(Praw, A)
        red = "inclusion-maximal"
    log("A71 point family: raw=%d distinct-pattern=%d %s=%d (edge-int=%d of %d kept, "
        "skipped=%s) depth mean %.1f max %d (%.1fs)"
        % (n_raw, len(P1), red, len(P), len(X), nX, skipped,
           A.sum(1).mean(), A.sum(1).max(), time.time() - t_pts), fh)
    info = dict(n_raw=int(n_raw), n_distinct_pattern=int(len(P1)), n_used=int(len(P)),
                reduction=red, edge_intersections_total=int(nX),
                edge_intersections_kept=int(len(X)),
                edge_intersections_skipped=bool(skipped), nudge_dirs=len(dirs),
                probe_eps=args.probe_eps, base_cap=args.base_cap,
                depth_mean=float(A.sum(1).mean()), depth_max=int(A.sum(1).max()))
    return P, A, info


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--betas", default="0,0.25,0.5,1.0")
    ap.add_argument("--cap_total", type=int, default=300)
    ap.add_argument("--cap_m2", type=int, default=200)
    ap.add_argument("--cap_m1", type=int, default=60)
    ap.add_argument("--cap_coarse", type=int, default=40)
    ap.add_argument("--min_sep", type=float, default=0.35)
    ap.add_argument("--max_rounds", type=int, default=40)
    ap.add_argument("--max_cuts", type=int, default=1500)
    ap.add_argument("--max_rows", type=int, default=25000)
    ap.add_argument("--outer_passes", type=int, default=3)
    ap.add_argument("--cut_tol", type=float, default=1e-6)
    ap.add_argument("--fine_tol", type=float, default=1.05)
    ap.add_argument("--probe_squares", type=int, default=200)
    ap.add_argument("--probe_cap", type=int, default=4000)
    ap.add_argument("--seg_cap", type=int, default=900000)
    ap.add_argument("--probe_eps", type=float, default=1e-5)
    ap.add_argument("--max_nnz", type=int, default=25000000)
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
    ap.add_argument("--catalog", default=None,
                    help="JSON with .placements = [[t,cx,cy],...]; replaces the built catalog")
    ap.add_argument("--tag", default="")
    ap.add_argument("--dump_primal", default=None,
                    help="beta whose restricted covering PRIMAL (atoms) to dump, e.g. 0.0")
    # ---- A71 additions
    ap.add_argument("--lp_solver", default="ipm", choices=["simplex", "ipm", "pdlp", "choose"])
    ap.add_argument("--loop_crossover", default="off", choices=["on", "off"])
    ap.add_argument("--final_solver", default="ipm", choices=["simplex", "ipm", "pdlp", "choose"])
    ap.add_argument("--final_crossover", default="on", choices=["on", "off"])
    ap.add_argument("--final_lp_time", type=float, default=1800.0)
    ap.add_argument("--ab_rounds", default="", help="rounds at which to run the solver A/B, e.g. 1,4")
    ap.add_argument("--ab_budget", type=float, default=300.0)
    ap.add_argument("--ab_each", type=float, default=150.0)
    ap.add_argument("--seed_deep", type=int, default=60)
    ap.add_argument("--top_k", type=int, default=20)
    ap.add_argument("--nudge8", action="store_true", default=True,
                    help="nudge arrangement points in all 8 directions (4 axis + 4 diagonal)")
    ap.add_argument("--no_maximal", action="store_true",
                    help="disable the inclusion-maximal reduction (A66 behaviour, for the A/B)")
    ap.add_argument("--dump_support", default=None,
                    help="beta whose final support (pairs + z + catalog) to dump for exact certification")
    ap.add_argument("--price_catalog", default=None,
                    help="JSON catalog to PRICE against (column generation); .placements")
    ap.add_argument("--grow_rounds", type=int, default=0)
    ap.add_argument("--grow_add", type=int, default=120, help="new placements per grow round")
    ap.add_argument("--grow_tol", type=float, default=1e-6)
    ap.add_argument("--grow_min_sep", type=float, default=0.10)
    ap.add_argument("--base_cap", type=int, default=40000,
                    help="cap on arrangement base points before nudging (vertices always kept)")
    ap.add_argument("--total_budget", type=float, default=1e9)
    ap.add_argument("--dump_dual", default=None,
                    help="beta whose FINAL row duals to dump (for the enriched-catalog dual check)")
    ap.add_argument("--purge_every", type=int, default=4, help="0 disables row purging")
    ap.add_argument("--purge_slack", type=float, default=0.02)
    ap.add_argument("--purge_age", type=int, default=3)
    ap.add_argument("--purge_min", type=int, default=200)
    ap.add_argument("--purge_max", type=int, default=4, help="max times a row may be purged")
    ap.add_argument("--purge_stop_lmax", type=float, default=1.05,
                    help="stop purging once the iterate's Lmax drops below this")
    ap.add_argument("--cut_pool", type=int, default=6, help="candidate multiplier before thinning")
    ap.add_argument("--cuts_per_point", type=int, default=3, help="0 disables cut thinning")
    ap.add_argument("--headline_solver", default="none",
                    choices=["none", "simplex", "ipm", "pdlp", "choose"])
    ap.add_argument("--headline_crossover", default="on", choices=["on", "off"])
    ap.add_argument("--headline_time", type=float, default=3600.0)
    args = ap.parse_args()

    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    fh = open(os.path.join(BASE, "logs", "pairlp_%s%s.log" % (args.cls, args.tag)), "w")
    T00 = time.time()

    log("A71 pair-LP (k4_13 wall-breaker): class=%s betas=%s" % (args.cls, args.betas), fh)
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

    if args.catalog:
        pls = json.load(open(args.catalog))["placements"]
        if extra:
            pls = pls + [[t, cx, cy] for (t, cx, cy) in extra]
        cat = catalog_from_list(pls, pins, boxes)
        log("catalog IMPORTED from %s: %s" % (args.catalog, json.dumps(cat["stats"])), fh)
    else:
        cat = build_catalog(pins, boxes, args, fh, extra=extra)
    log("catalog: |S|=%d  stats=%s" % (len(cat["t"]), json.dumps(cat["stats"])), fh)

    args.n_boxpts = 0
    rng_pts = np.random.default_rng(args.seed + 3)
    base_pls = list(pls) if args.catalog else [[float(cat["t"][a]), float(cat["C"][a, 0]),
                                                float(cat["C"][a, 1])] for a in range(len(cat["t"]))]
    ecat = None
    if args.price_catalog:
        epls = json.load(open(args.price_catalog))["placements"]
        ecat = catalog_from_list(epls, pins, boxes)
        log("PRICING catalog %s: %d placements (%d imported)"
            % (args.price_catalog, len(ecat["t"]), len(epls)), fh)

    I, J = disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1") for a, b in zip(I, J)])
    log("disjoint pairs: %d of %d (m2>0: %d, m2 max %d)"
        % (len(I), len(cat["t"]) * (len(cat["t"]) - 1) // 2, int((m2 > 0).sum()),
           int(m2.max()) if len(m2) else 0), fh)
    P, A, pointinfo = build_point_family(cat, boxes, args, fh, rng_pts)

    betas = [float(x) for x in args.betas.split(",")]
    out = dict(cls=args.cls, k=k, N=N, m=m, s0=S0,
               threshold_formula="%d + beta*%d" % (thresh_base, m),
               catalog=cat["stats"], n_placements=int(len(cat["t"])),
               n_pairs_disjoint=int(len(I)), n_cut_points=int(len(P)),
               point_family=pointinfo, colgen=[],
               control=None, betas={}, deviations=[],
               settings={kk: vv for kk, vv in vars(args).items()})
    out["deviations"] = [
        "A71: the working point family is the FULL catalog arrangement's cell representatives "
        "reduced to inclusion-MAXIMAL membership patterns.  Sound because the (P2') load is "
        "monotone in the membership sets for z >= 0, so a dominated point's row is implied and "
        "the load maximum over the family is attained on maximal patterns; the cut loop and the "
        "validity check are therefore the same exact test on this family (no random subsampling, "
        "unlike A66's --fine_cap truncation).",
        "A71: cut-loop LPs are solved by HiGHS interior point with crossover OFF; every outer "
        "pass ends with a clean %s solve (crossover=%s) whose basic solution and row duals are "
        "what gets reported." % (args.final_solver, args.final_crossover),
        "A71: cell-representative point sets are HEURISTICALLY COMPLETE.  Each evaluated load is "
        "exact for its point, but maximality of the load over all of [0,s0]^2 rests on the "
        "representative construction (vertices + pairwise edge intersections nudged by "
        "%g), not on a proof." % args.probe_eps,
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

    have = {(round(float(cat["t"][a]), 9), round(float(cat["C"][a, 0]), 9),
             round(float(cat["C"][a, 1]), 9)) for a in range(len(cat["t"]))}
    cur_pls = base_pls
    out["grow_history"] = []
    adequate = None
    for grow in range(args.grow_rounds + 1):
        if grow > 0:
            cat = catalog_from_list(cur_pls, pins, boxes)
            log("GROW %d: catalog |S|=%d  %s" % (grow, len(cat["t"]), json.dumps(cat["stats"])), fh)
            I, J = disjoint_pairs(cat)
            m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1")
                           for a, b in zip(I, J)])
            log("GROW %d: disjoint pairs %d" % (grow, len(I)), fh)
            require_headroom(args.headroom, fh, args.headroom_wait)
            P, A, pointinfo = build_point_family(cat, boxes, args, fh, rng_pts)
            out["point_family"] = pointinfo
            out["catalog"] = cat["stats"]
            out["n_placements"] = int(len(cat["t"]))
            out["n_pairs_disjoint"] = int(len(I))
            out["n_cut_points"] = int(len(P))

        store = RowStore()
        for beta in betas:
            require_headroom(args.headroom, fh, args.headroom_wait)
            r = solve_beta(cat, I, J, m2, P, A, beta, args, fh, store, boxes)
            sup_sq = (np.unique(np.concatenate([I[r["support"]], J[r["support"]]]))
                      if len(r["support"]) else np.zeros(0, dtype=int))
            lmax = max(r["Lmax_fine"] if r["Lmax_fine"] is not None else 1.0, 1.0)
            scaled = r["value"] / lmax
            thr = thresh_base + beta * m
            ctrl_val = (thresh_base + beta * ctrl["sum_m2"]) if ctrl else None
            lo = max(x for x in (scaled, ctrl_val or 0.0) if x is not None)
            rec = dict(beta=beta, value=r["value"], Lmax_fine=lmax, scaled_value=scaled,
                       threshold=thr, margin=scaled - thr, mbar2=r["mbar2"],
                       converged=bool(r["converged"]),
                       tau2_bracket=[lo, r["value"]],
                       bracket_note=("scaled_value is a VALID lower bound on tau2; value is the "
                                     "restricted-LP optimum on the rows found so far and is an upper "
                                     "bound on what this catalog can give"),
                       control_value=ctrl_val,
                       value_ge_control=(None if ctrl_val is None else bool(r["value"] >= ctrl_val - 1e-6)),
                       n_support_pairs=int(len(r["support"])), n_support_squares=int(len(sup_sq)),
                       rounds=r["rounds"], n_rows=r["n_rows"], nnz=r["nnz"],
                       Lmax_cut=r["Lmax_cut"],
                       n_z_at_ub=r["n_at_ub"], lp_status=r["status"], note=r["note"],
                       n_tight_rows=r["n_tight_rows"], solver_times=r["solver_times"],
                       headline_solve=r["headline"], n_active_rows=r["n_active_rows"],
                       seconds=r["seconds"], fine=r["fine"], top10=r["top10"])
            out["betas"][repr(beta)] = rec
            if args.dump_dual is not None and abs(beta - float(args.dump_dual)) < 1e-12:
                y = r["row_dual"]
                nz = [i for i in np.nonzero(np.abs(y) > 1e-13)[0] if store.pidx[i] is not None]
                fpD = os.path.join(BASE, "results", "pair_dual_%s%s.json" % (args.cls, args.tag))
                json.dump(dict(cls=args.cls, beta=beta, lp_value=r["value"],
                               headline=r["headline"],
                               sum_duals=float(np.abs(y).sum()),
                               sum_duals_signed=float(y.sum()),
                               dual_gap_vs_objective=r.get("dual_gap"),
                               n_nonzero=len(nz), n_active_rows=r["n_active_rows"],
                               n_points=int(len(P)),
                               points=[[float(P[a, 0]), float(P[a, 1])] for a in range(len(P))],
                               rows=[[int(store.pidx[i][0]), int(store.pidx[i][1]), float(y[i])]
                                     for i in nz],
                               note=("row duals of the FINAL solve, indexed by the (c,d) point pair "
                                     "that generated the row; points are the global maximal-pattern "
                                     "family.  y >= 0 and A^T y >= c certify an UPPER bound sum(y) "
                                     "on tau_2 for ANY catalog whose columns satisfy A^T y >= c.")),
                          open(fpD, "w"))
                log("dumped %d nonzero row duals (sum %.9f) -> %s"
                    % (len(nz), float(y.sum()), fpD), fh)
            if args.dump_support is not None and abs(beta - float(args.dump_support)) < 1e-12:
                sp = np.nonzero(r["z"] > 1e-12)[0]
                fpS = os.path.join(BASE, "results", "pair_support_%s%s.json" % (args.cls, args.tag))
                json.dump(dict(cls=args.cls, beta=beta, s0=str(Fr(969271, 250000)),
                               lp_value=r["value"], Lmax_fine=lmax, converged=bool(r["converged"]),
                               n_placements=int(len(cat["t"])),
                               placements=[[float(cat["t"][a]), float(cat["C"][a, 0]),
                                            float(cat["C"][a, 1])] for a in range(len(cat["t"]))],
                               pins=[[str(Fr(a)), str(Fr(b))] for a, b in e["pins"]],
                               boxes=[[str(Fr(b["slot"][0])), str(Fr(b["slot"][1]))] for b in e["boxes"]],
                               n_support=int(len(sp)),
                               support=[[int(I[k]), int(J[k]), float(r["z"][k]), int(m2[k])]
                                        for k in sp],
                               note="final z support: (i, j, z_ij, m2_ij) into .placements"),
                          open(fpS, "w"))
                log("dumped %d support pairs -> %s" % (len(sp), fpS), fh)
            log("RESULT beta=%.4g: value=%.6f Lmax_fine=%.6f scaled=%.6f thr=%.4f margin=%+.6f "
                "mbar2=%.4f ctrl=%s converged=%s (%.1fs)"
                % (beta, r["value"], lmax, scaled, thr, scaled - thr, r["mbar2"],
                   ctrl_val, r["converged"], r["seconds"]), fh)
            out["rowstore_rows"] = len(store.rows)
            out["rowstore_nnz"] = store.nnz
            json.dump(out, open(os.path.join(BASE, "results", "pairlp_%s%s.json" % (args.cls, args.tag)), "w"), indent=1)
            if args.dump_primal is not None and abs(beta - float(args.dump_primal)) < 1e-12:
                dump_primal(args, cat, I, J, m2, store, r, beta, thresh_base, m, fh)

        # ---------------- COLUMN GENERATION against the enriched pricing catalog.
        # Reduced cost of a pair column (i,j) is c_ij - (A^T y)_ij with y the row duals; a
        # positive value means the current catalog is NOT pair-adequate and the true tau_2 on
        # the pricing catalog is strictly larger than what was just computed.
        out["grow_history"].append(dict(grow=grow, n_placements=int(len(cat["t"])),
                                        n_pairs=int(len(I)), n_points=int(len(P)),
                                        value=r["value"], converged=bool(r["converged"]),
                                        Lmax_fine=r["Lmax_fine"], rounds=r["rounds"],
                                        seconds=r["seconds"]))
        json.dump(out, open(os.path.join(BASE, "results", "pairlp_%s%s.json"
                                         % (args.cls, args.tag)), "w"), indent=1)
        if ecat is None or grow == args.grow_rounds:
            break
        t_pr = time.time()
        y = dual_matrix(r["row_dual"], store, len(P))
        Ie, Je, defs, score = price_catalog(y, P, ecat, betas[0], chunk=args.chunk)
        maxdef = float(defs.max()) if len(defs) else -1.0
        npos = int((defs > args.grow_tol).sum())
        log("GROW %d PRICING: max reduced cost %.6f over %d pricing pairs (%d > %g, %.1f%%) "
            "(%.1fs)" % (grow, maxdef, len(Ie), npos, args.grow_tol,
                         100.0 * npos / max(1, len(Ie)), time.time() - t_pr), fh)
        out["colgen"].append(dict(grow=grow, n_placements=int(len(cat["t"])),
                                  value=r["value"], converged=bool(r["converged"]),
                                  max_reduced_cost=maxdef, n_positive=npos,
                                  n_priced_pairs=int(len(Ie)),
                                  frac_positive=float(npos) / max(1, len(Ie))))
        if maxdef <= args.grow_tol:
            adequate = True
            log("GROW %d: catalog is PAIR-ADEQUATE against the pricing catalog (max reduced "
                "cost %.3e <= %g): the value above IS the pricing-catalog value, and sum(y) "
                "= %.9f is a valid upper bound for it." % (grow, maxdef, args.grow_tol,
                                                           float(r["row_dual"].sum())), fh)
            break
        adequate = False
        new = pick_new_squares(ecat, score, have, args.grow_add, args.grow_min_sep)
        if not new:
            log("GROW %d: no admissible new placements left" % grow, fh)
            break
        cur_pls = cur_pls + new
        log("GROW %d: adding %d placements -> |S| = %d" % (grow, len(new), len(cur_pls)), fh)
        json.dump(dict(cls=args.cls, s0=S0, n=len(cur_pls), placements=cur_pls,
                       note="A71 column-generated catalog (A66 support seed + priced additions)"),
                  open(os.path.join(BASE, "results", "catalog_%s_colgen%s.json"
                                    % (args.cls, args.tag)), "w"))
        if time.time() - T00 > args.total_budget:
            log("GROW: total budget hit", fh)
            break
    out["catalog_pair_adequate"] = adequate


    out["total_seconds"] = time.time() - T00
    fp = os.path.join(BASE, "results", "pairlp_%s%s.json" % (args.cls, args.tag))
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs total)" % (fp, out["total_seconds"]), fh)
    fh.close()


if __name__ == "__main__":
    main()
