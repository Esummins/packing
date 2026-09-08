"""A150 T2 -- the FOUR-CORNER PRODUCT cover: one band cell per corner, killed by geometry alone.

THE ROOT.  K0-BLOCKED (A143 sec 1 (R1); Lean `teleport_packing`) says every corner box B_c^w(s0)
= the widened unit box at corner c is met by >= 2 squares of F.  Pick ONE meeter at each corner:
the state is a 4-tuple (t_BL, t_BR, t_TR, t_TL) of band cells, read in each corner's own local
frame (frames150).

DISJOINTNESS OF THE FOUR CORNER LINEAGES (new, and the reason budget 7 is right).  The widened
corner boxes are pairwise at distance  s0 - 2 a_w = 1.8262 > sqrt2 = diam(unit square), so NO unit
square meets two corner boxes.  Hence the four conditioned squares are automatically DISTINCT (no
`cores_meet` side condition is needed, unlike A143's Rule I), the node's budget is 11 - 4 = 7, and
in fact K0-BLOCKED forces >= 8 distinct corner meeters, so 4 of the 7 remaining squares are corner
meeters too.

THE KILLS, in increasing cost order.  Every one is a NECESSARY condition on a K0-BLOCKED packing.

  (Q2) ADJACENT-CORNER CENTRE DISTANCE.  Two interior-disjoint unit squares have centre distance
       >= 1 (any separating direction n gives |d.n| >= h_1(n) + h_2(n) >= 1).  If the MAXIMUM
       centre distance over the two global boxes is < 1 the combination is contradictory.  Applied
       to all four adjacent corner pairs and to the two diagonals.
  (Q1) CORE-VS-CORE.  K'(global box at c1) meets K'(global box at c2) (A132 exact polygon cores)
       ==> every square realising the first overlaps every square realising the second ==> (C).
  (Q1s) A131's per-tilt-sub-bin refinement of (Q1): 4 sub-bins each side, container-clipped; the
       pair dies iff EVERY surviving sub-pair is contradictory.
  (QG) GUARD LINES (A144).  rhs(l) = s0 - SUM_j minchord(box_j, l) over the four hypothesis boxes;
       rhs(l) < 0 is an outright contradiction.  The two corner intruders on a wall contribute two
       chords to every axis line near that wall.
  (QD) DISK BOUND with all four cores removed and budget 7 (A148 `geo148.disk_bound`).

BECAUSE EVERY KILL IS PAIRWISE (Q2/Q1/Q1s) OR SEPARABLE (QD), the survivor COUNT of the product
never needs the product to be enumerated: the four corners form a 4-cycle, so the count is a
transfer-matrix trace, and the D4 quotient is Burnside over the eight elements of frames150.D4.

    python code/prod150.py --stage pairs
    python code/prod150.py --stage count
    python code/prod150.py --stage disk
    python code/prod150.py --stage guard
    python code/prod150.py --stage pick
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (os.path.join(ATT, "A143-corner-first-k0", "code"),
           os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A144-guard-lines", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import geo148                                                   # noqa: E402
import guardline as GL                                          # noqa: E402
import cells143 as C                                            # noqa: E402
import frames150 as F                                           # noqa: E402
import band150 as B                                             # noqa: E402

RES = os.path.join(BASE, "results")
MAXV = 16
NSUB = 4
S0 = C.S0
A_W = C.A_W


def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return math.hypot(dx, dy)


def load_band():
    keys = [tuple(k) for k in json.load(open(os.path.join(RES, "band150.json"),
                                             encoding="utf-8"))["band"]]
    byk = {(c.ix, c.iy, c.it): c for c in C.all_cells() if not c.empty}
    return keys, [byk[k] for k in keys], byk


# ------------------------------------------------------------------ (Q2)/(Q1)/(Q1s) matrices
def pair_matrix(cells, c1, c2, tag, log=print):
    """M[i, j] = 0 if cell i at corner c1 is incompatible with cell j at corner c2."""
    n = len(cells)
    G1 = [F.global_box(c1, c) for c in cells]
    G2 = [F.global_box(c2, c) for c in cells]
    t0 = time.time()
    K1 = [polycore.build(b, max_v=MAXV) for b in G1]
    K2 = K1 if c1 == c2 else [polycore.build(b, max_v=MAXV) for b in G2]
    log("%s: %d+%d polygon cores in %.0f s" % (tag, len(K1), len(K2), time.time() - t0))
    M = np.ones((n, n), np.uint8)
    kills = dict(Q2=0, Q1=0, Q1s=0)
    sub1 = sub2 = None
    for i in range(n):
        for j in range(n):
            if max_centre_dist(G1[i], G2[j]) < 1.0:
                M[i, j] = 0
                kills["Q2"] += 1
                continue
            if polycore.poly_poly_depth(K1[i].P, K2[j].P) > 0.0:
                M[i, j] = 0
                kills["Q1"] += 1
                continue
    # (Q1s) only where (Q2)/(Q1) left the pair alive AND the boxes are close enough to matter
    near = [(i, j) for i in range(n) for j in range(n)
            if M[i, j] and max_centre_dist(G1[i], G2[j]) < 2.5]
    if near:
        sub1 = [F.global_subbins(c1, c, NSUB) for c in cells]
        sub2 = sub1 if c1 == c2 else [F.global_subbins(c2, c, NSUB) for c in cells]
        KS1, KS2 = {}, {}
        for (i, j) in near:
            if i not in KS1:
                KS1[i] = [polycore.build(b, max_v=MAXV) for b in sub1[i]]
            if j not in KS2:
                KS2[j] = [polycore.build(b, max_v=MAXV) for b in sub2[j]]
            alive = 0
            for p1 in KS1[i]:
                for p2 in KS2[j]:
                    if polycore.poly_poly_depth(p1.P, p2.P) <= 0.0:
                        alive += 1
            if alive == 0:
                M[i, j] = 0
                kills["Q1s"] += 1
    kills["alive"] = int(M.sum())
    kills["n_near_tested"] = len(near)
    kills["total"] = n * n
    log("%s: %s in %.0f s" % (tag, json.dumps(kills), time.time() - t0))
    return M, kills


def pairs_stage(log=print):
    keys, cells, _ = load_band()
    out = {}
    A, kA = pair_matrix(cells, "BL", "BR", "adj BL-BR", log)
    D, kD = pair_matrix(cells, "BL", "TR", "diag BL-TR", log)
    np.save(os.path.join(RES, "prod150_A.npy"), A)
    np.save(os.path.join(RES, "prod150_D.npy"), D)
    # consistency: the vertical mirror sends (BL a, BR b) to (BR Ta, BL Tb), so A[a,b] = A[Tb,Ta]
    idx = {k: i for i, k in enumerate(keys)}
    tp = np.array([idx.get(F.T(k), -1) for k in keys])
    ok = True
    if (tp >= 0).all():
        ok = bool((A == A[tp][:, tp].T).all())
    out["A"] = kA
    out["D"] = kD
    out["A_mirror_consistent"] = ok
    out["band"] = len(keys)
    json.dump(out, open(os.path.join(RES, "prod150_pairs.json"), "w"), indent=1)
    log(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------------------------------- counting
def count_product(A, D, keys):
    """exact survivor count of the 4-cycle with diagonal constraints, and the D4 Burnside orbit
    count.  A is the (BL,BR) matrix, reused on every edge of the cycle by the rotation; D is the
    (BL,TR) matrix, reused on both diagonals."""
    n = len(keys)
    A64 = A.astype(np.int64)
    diag_trivial = bool(D.all())
    if diag_trivial:
        M2 = A64 @ A64                       # M2[a0,a2] = #a1
        total = int(np.einsum("ij,ji->", M2, M2))
    else:
        # sum_{a0} sum_{a1 in I1, a3 in I3} D[a1,a3] * ( sum_{a2 in I2} A[a1,a2] A[a2,a3] )
        # with I1 = {A[a0,.]}, I3 = {A[.,a0]}, I2 = {D[a0,.]}; D[a1,a3] is independent of a2 so
        # it multiplies the matrix product elementwise.
        total = 0
        for a0 in range(n):
            m1 = A64[a0] > 0
            m3 = A64[:, a0] > 0
            m2 = D[a0] > 0
            sub = A64[np.ix_(m1, m2)]                        # (|I1|, |I2|)
            sub3 = A64[np.ix_(m2, m3)]                       # (|I2|, |I3|)
            Dm = D[np.ix_(m1, m3)]                           # D[a1,a3]
            total += int(((sub @ sub3) * Dm).sum()) if Dm.size else 0
    idx = {k: i for i, k in enumerate(keys)}
    tp = np.array([idx.get(F.T(k), -1) for k in keys])

    def alive(t):
        a0, a1, a2, a3 = t
        if min(a0, a1, a2, a3) < 0:
            return False
        return bool(A[a0, a1] and A[a1, a2] and A[a2, a3] and A[a3, a0]
                    and D[a0, a2] and D[a1, a3])

    tfix = [a for a in range(n) if tp[a] == a]
    fix = {}
    fix["e"] = total
    fix["r"] = sum(1 for a in range(n) if alive((a, a, a, a)))
    fix["r3"] = fix["r"]
    fix["r2"] = sum(1 for a in range(n) for b in range(n) if alive((a, b, a, b)))
    # m_diag fixes t = (a, b, c, Tb) with a, c themselves T-fixed; m_anti fixes (a, b, Ta, d)
    # with b, d T-fixed.  T has no fixed cell, so both are structurally 0.
    fix["m_diag"] = sum(1 for a in tfix for c in tfix for b in range(n)
                        if alive((a, b, c, int(tp[b]))))
    fix["m_anti"] = sum(1 for b in tfix for d in tfix for a in range(n)
                        if alive((a, b, int(tp[a]), d)))
    fix["m_horiz"] = sum(1 for a in range(n) for b in range(n)
                         if alive((a, b, int(tp[b]), int(tp[a]))))
    fix["m_vert"] = sum(1 for a in range(n) for b in range(n)
                        if alive((a, int(tp[a]), int(tp[b]), b)))
    fix["n_T_fixed_cells"] = len(tfix)
    fix.pop("n_T_fixed_cells")
    orbits = sum(fix.values()) / 8.0
    return dict(total=total, diag_trivial=diag_trivial, fix=fix, orbits=orbits,
                orbits_exact=(int(orbits) if abs(orbits - round(orbits)) < 1e-9 else orbits))


def cheap_matrices(cells, c1, c2):
    """the (Q2)-only and (Q2+Q1)-only matrices, for the per-stage survivor table."""
    n = len(cells)
    G1 = [F.global_box(c1, c) for c in cells]
    G2 = [F.global_box(c2, c) for c in cells]
    K1 = [polycore.build(b, max_v=MAXV) for b in G1]
    K2 = [polycore.build(b, max_v=MAXV) for b in G2]
    M2 = np.ones((n, n), np.uint8)
    M21 = np.ones((n, n), np.uint8)
    for i in range(n):
        for j in range(n):
            if max_centre_dist(G1[i], G2[j]) < 1.0:
                M2[i, j] = 0
                M21[i, j] = 0
            elif polycore.poly_poly_depth(K1[i].P, K2[j].P) > 0.0:
                M21[i, j] = 0
    return M2, M21


def stages_stage(log=print):
    """survivor count of the D4-reduced product after each kill, in increasing cost order."""
    keys, cells, _ = load_band()
    n = len(keys)
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    ones = np.ones((n, n), np.uint8)
    A2, A21 = cheap_matrices(cells, "BL", "BR")
    D2, D21 = cheap_matrices(cells, "BL", "TR")
    np.save(os.path.join(RES, "prod150_A2.npy"), A2)
    np.save(os.path.join(RES, "prod150_A21.npy"), A21)
    np.save(os.path.join(RES, "prod150_D2.npy"), D2)
    np.save(os.path.join(RES, "prod150_D21.npy"), D21)
    tab = []
    for name, Am, Dm in (("0 raw band product", ones, ones),
                         ("1 +Q2 adjacent centre distance", A2, ones),
                         ("2 +Q1 adjacent K'-vs-K'", A21, ones),
                         ("3 +Q1s adjacent per-sub-bin", A, ones),
                         ("4 +Q2/Q1/Q1s on the two diagonals", A, D),
                         ):
        r = count_product(Am, Dm, keys)
        r["stage"] = name
        r["adj_alive_frac"] = float(Am.mean())
        r["diag_alive_frac"] = float(Dm.mean())
        tab.append(r)
        log("%-38s tuples %d   D4-orbits %s" % (name, r["total"], r["orbits_exact"]))
    out = dict(band=n, stages=tab)
    json.dump(out, open(os.path.join(RES, "prod150_stages.json"), "w"), indent=1)
    return out


def count_stage(log=print):
    keys, cells, _ = load_band()
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    n = len(keys)
    ones = np.ones((n, n), np.uint8)
    out = dict(band=n, raw_product=n ** 4)
    out["stage0_no_kill"] = count_product(ones, ones, keys)
    out["stage_adj"] = count_product(A, ones, keys)
    out["stage_adj_diag"] = count_product(A, D, keys)
    json.dump(out, open(os.path.join(RES, "prod150_count.json"), "w"), indent=1)
    log(json.dumps(out, indent=1))
    return out


# ---------------------------------------------------------------------- (QD) the disk bound
def disk_stage(pitch=0.02, ntilt=36, budget=7, log=print):
    """The four cores are pairwise > 1.8 apart, so their blocked shadows are disjoint and the
    dilated-open area is EXACTLY additive:  area4 = area0 - SUM_c delta(t_c).  Precompute
    delta per cell (one feasible_region each), then n_max(t) = floor(area4 / (pi/4)) is a
    SEPARABLE function of the 4-tuple.  A sample of tuples is recomputed from scratch to confirm
    the additivity claim."""
    keys, cells, _ = load_band()
    reg0 = geo148.feasible_region(S0, [], pitch_target=pitch, ntilt=ntilt)
    d0 = geo148.disk_bound(reg0)
    area0 = d0["area_dilated"]
    delta = {}
    for k, c in zip(keys, cells):
        pc = polycore.build(F.global_box("BL", c), max_v=MAXV)
        reg = geo148.feasible_region(S0, [pc.P], pitch_target=pitch, ntilt=ntilt)
        delta[k] = area0 - geo148.disk_bound(reg)["area_dilated"]
    dv = np.array([delta[k] for k in keys])
    worst = area0 - 4.0 * dv.max()
    best = area0 - 4.0 * dv.min()
    out = dict(pitch=pitch, ntilt=ntilt, budget=budget, area0=area0,
               n_max_0=d0["n_max"],
               delta_min=float(dv.min()), delta_max=float(dv.max()),
               delta_median=float(np.median(dv)),
               area4_worst_case=worst, area4_best_case=best,
               n_max_4_min=int(math.floor(worst / (math.pi / 4.0))),
               n_max_4_max=int(math.floor(best / (math.pi / 4.0))),
               fires=bool(math.floor(worst / (math.pi / 4.0)) < budget))
    # additivity check on a sample of 4-tuples
    rng = np.random.default_rng(150)
    chk = []
    for _ in range(6):
        t = [keys[i] for i in rng.integers(0, len(keys), 4)]
        obs = [polycore.build(F.global_box(c, [x for x in cells
                                               if (x.ix, x.iy, x.it) == k][0]), max_v=MAXV).P
               for c, k in zip(F.CORNERS, t)]
        reg = geo148.feasible_region(S0, obs, pitch_target=pitch, ntilt=ntilt)
        direct = geo148.disk_bound(reg)
        pred = area0 - sum(delta[k] for k in t)
        chk.append(dict(tuple=[list(k) for k in t], direct_area=direct["area_dilated"],
                        predicted_area=pred, direct_n_max=direct["n_max"],
                        predicted_n_max=int(math.floor(pred / (math.pi / 4.0))),
                        abs_err=abs(direct["area_dilated"] - pred)))
        log("additivity check %s direct=%.5f pred=%.5f err=%.2e"
            % (chk[-1]["tuple"], chk[-1]["direct_area"], pred, chk[-1]["abs_err"]))
    out["additivity_checks"] = chk
    out["additivity_max_abs_err"] = max(c["abs_err"] for c in chk)
    out["delta_by_cell"] = {"%d%d%d" % k: round(delta[k], 6) for k in keys}
    json.dump(out, open(os.path.join(RES, "prod150_disk.json"), "w"), indent=1)
    log(json.dumps({k: v for k, v in out.items()
                    if k not in ("delta_by_cell", "additivity_checks")}, indent=1))
    return out


def disk_direct_stage(nsample=40, pitch=0.02, ntilt=36, budget=7, seed=1502, log=print):
    """The separable surrogate of `disk_stage` is NOT a theorem (dilated areas do not add), so the
    disk bound is measured DIRECTLY on a random sample of surviving 4-tuples: all four polygon
    cores in one feasible_region, one disk_bound.  The SOUND separable statement is only
    area4 <= area0 - max_c delta_c (monotonicity of the blocked set under adding obstacles), which
    is reported alongside."""
    keys, cells, _ = load_band()
    byk = {k: c for k, c in zip(keys, cells)}
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    idx = {k: i for i, k in enumerate(keys)}
    rng = np.random.default_rng(seed)
    rows = []
    t0 = time.time()
    while len(rows) < nsample:
        t = tuple(keys[i] for i in rng.integers(0, len(keys), 4))
        a = [idx[x] for x in t]
        if not (A[a[0], a[1]] and A[a[1], a[2]] and A[a[2], a[3]] and A[a[3], a[0]]
                and D[a[0], a[2]] and D[a[1], a[3]]):
            continue
        obs = [polycore.build(F.global_box(c, byk[k]), max_v=MAXV).P
               for c, k in zip(F.CORNERS, t)]
        reg = geo148.feasible_region(S0, obs, pitch_target=pitch, ntilt=ntilt)
        db = geo148.disk_bound(reg)
        rows.append(dict(tuple=[list(k) for k in t], n_max=db["n_max"],
                         area_dilated=db["area_dilated"], area_open=db["area_open"],
                         area_green=db["area_green"], kills=bool(db["n_max"] < budget)))
        log("%s n_max=%d open=%.4f dil=%.4f" % (rows[-1]["tuple"], db["n_max"],
                                                db["area_open"], db["area_dilated"]))
    nm = [r["n_max"] for r in rows]
    out = dict(nsample=len(rows), budget=budget, pitch=pitch, ntilt=ntilt,
               n_max_min=min(nm), n_max_max=max(nm),
               n_max_median=float(np.median(nm)), n_kills=sum(r["kills"] for r in rows),
               area_open_min=min(r["area_open"] for r in rows),
               secs=round(time.time() - t0, 1), rows=rows)
    json.dump(out, open(os.path.join(RES, "prod150_disk_direct.json"), "w"), indent=1)
    log(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    return out


def sep_bound(reg, L=0.70, noff=4):
    """(QS) SEPARATION BOUND -- strictly sharper than the disk bound on a thin region.

    The centres of the remaining squares lie in the NON-BLOCKED set O (A148's certified outer
    approximation of the feasible-centre region) and are pairwise >= 1 apart.  Partition the plane
    into half-open squares of side L with L*sqrt2 < 1: two centres in the same square would be
    < 1 apart, so

        #remaining  <=  #{ squares of the partition that meet O }.

    Every offset of the partition gives a valid bound, so the MINIMUM over `noff^2` offsets is
    valid too.  Unlike the disk bound this does not throw away the shape of O: a region of small
    area spread over many partition squares is priced correctly, and a region concentrated in a
    few is priced far below area/(pi/4)."""
    assert L * math.sqrt(2.0) < 1.0
    ys, xs = np.nonzero(~reg.blocked)
    if len(xs) == 0:
        return dict(n_max=0, L=L, cells=0)
    px = reg.xs[xs]
    py = reg.ys[ys]
    h = 0.5 * reg.pitch
    best = None
    for a in range(noff):
        for b in range(noff):
            ox, oy = a * L / noff, b * L / noff
            # a grid cell spans [px-h, px+h]: mark every partition square it meets
            i0 = np.floor((px - h - ox) / L).astype(np.int64)
            i1 = np.floor((px + h - ox) / L).astype(np.int64)
            j0 = np.floor((py - h - oy) / L).astype(np.int64)
            j1 = np.floor((py + h - oy) / L).astype(np.int64)
            occ = set()
            for k in range(len(px)):
                for i in range(i0[k], i1[k] + 1):
                    for j in range(j0[k], j1[k] + 1):
                        occ.add((i, j))
            if best is None or len(occ) < best[0]:
                best = (len(occ), ox, oy)
    return dict(n_max=int(best[0]), L=L, offset=[best[1], best[2]],
                cells=int(len(px)), n_offsets=noff * noff)


def sep_stage(nsample=40, pitch=0.02, ntilt=36, budget=7, seed=1502, L=0.70, log=print):
    """the separation bound on the same random survivors the direct disk bound used."""
    keys, cells, _ = load_band()
    byk = {k: c for k, c in zip(keys, cells)}
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    idx = {k: i for i, k in enumerate(keys)}
    rng = np.random.default_rng(seed)
    rows = []
    t0 = time.time()
    while len(rows) < nsample:
        t = tuple(keys[i] for i in rng.integers(0, len(keys), 4))
        a = [idx[x] for x in t]
        if not (A[a[0], a[1]] and A[a[1], a[2]] and A[a[2], a[3]] and A[a[3], a[0]]
                and D[a[0], a[2]] and D[a[1], a[3]]):
            continue
        obs = [polycore.build(F.global_box(c, byk[k]), max_v=MAXV).P
               for c, k in zip(F.CORNERS, t)]
        reg = geo148.feasible_region(S0, obs, pitch_target=pitch, ntilt=ntilt)
        db = geo148.disk_bound(reg)
        sb = sep_bound(reg, L=L)
        rows.append(dict(tuple=[list(k) for k in t], n_max_disk=db["n_max"],
                         n_max_sep=sb["n_max"], area_open=db["area_open"],
                         kills=bool(sb["n_max"] < budget)))
        log("%s disk=%d sep=%d open=%.4f%s" % (rows[-1]["tuple"], db["n_max"], sb["n_max"],
                                               db["area_open"],
                                               "  KILL" if rows[-1]["kills"] else ""))
    ns = [r["n_max_sep"] for r in rows]
    out = dict(nsample=len(rows), budget=budget, L=L, pitch=pitch, ntilt=ntilt,
               sep_min=min(ns), sep_max=max(ns), sep_median=float(np.median(ns)),
               n_kills=sum(r["kills"] for r in rows),
               disk_min=min(r["n_max_disk"] for r in rows),
               secs=round(time.time() - t0, 1), rows=rows)
    json.dump(out, open(os.path.join(RES, "prod150_sep.json"), "w"), indent=1)
    log(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    return out


# ------------------------------------------------------------------------ (QG) guard lines
def guard_stage(nsample=4000, seed=1500, log=print):
    """rhs(l) = s0 - SUM over the four hypothesis boxes of minchord(box, l), minimised over A144's
    line family.  rhs < 0 kills.  Sampled over surviving 4-tuples plus the extreme tuples (the
    four cells furthest from their corners), since rhs is a sum of four per-(corner, cell, line)
    numbers and the line family is common."""
    keys, cells, _ = load_band()
    A = np.load(os.path.join(RES, "prod150_A.npy"))
    D = np.load(os.path.join(RES, "prod150_D.npy"))
    # a common family of axis lines: every 0.01 in y (horizontal) and x (vertical)
    lines = []
    for pos in np.arange(0.005, S0, 0.01):
        lines.append(GL.Line("h", float(pos)))
        lines.append(GL.Line("v", float(pos)))
    n = len(keys)
    # minchord table: mc[corner][cell][line]
    t0 = time.time()
    MC = {}
    for c in F.CORNERS:
        tab = np.zeros((n, len(lines)))
        for i, cell in enumerate(cells):
            gb = F.global_box(c, cell)
            for j, l in enumerate(lines):
                tab[i, j] = float(GL.minchord_box(gb, l)["lo"])
        MC[c] = tab
        log("minchord table %s done %.0f s" % (c, time.time() - t0))
    rng = np.random.default_rng(seed)
    best = dict(rhs=9e9, tuple=None, line=None)
    hist = []
    tried = 0
    while tried < nsample:
        t = [int(x) for x in rng.integers(0, n, 4)]
        if not (A[t[0], t[1]] and A[t[1], t[2]] and A[t[2], t[3]] and A[t[3], t[0]]
                and D[t[0], t[2]] and D[t[1], t[3]]):
            continue
        tried += 1
        tot = sum(MC[c][t[i]] for i, c in enumerate(F.CORNERS))
        j = int(np.argmax(tot))
        rhs = S0 - float(tot[j])
        hist.append(rhs)
        if rhs < best["rhs"]:
            best = dict(rhs=rhs, tuple=[list(keys[i]) for i in t],
                        line=[lines[j].orient, lines[j].foff],
                        chords=[float(MC[c][t[i], j]) for i, c in enumerate(F.CORNERS)])
    h = np.array(hist)
    out = dict(n_lines=len(lines), n_tuples=tried, best=best,
               rhs_min=float(h.min()), rhs_median=float(np.median(h)),
               rhs_max=float(h.max()),
               n_rhs_lt_0=int((h < 0).sum()), n_rhs_lt_015=int((h < 0.15).sum()),
               max_chords_on_a_line=int(max(
                   sum(1 for c in F.CORNERS if MC[c][t, j] > 0)
                   for t in range(0, n, 17) for j in range(0, len(lines), 7))),
               secs=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(RES, "prod150_guard.json"), "w"), indent=1)
    log(json.dumps(out, indent=1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=("pairs", "count", "stages", "disk", "disk_direct", "sep", "guard"))
    ap.add_argument("--pitch", type=float, default=0.02)
    ap.add_argument("--n", type=int, default=4000)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    if a.stage == "pairs":
        pairs_stage()
    elif a.stage == "count":
        count_stage()
    elif a.stage == "stages":
        stages_stage()
    elif a.stage == "disk":
        disk_stage(pitch=a.pitch)
    elif a.stage == "disk_direct":
        disk_direct_stage(nsample=a.n, pitch=a.pitch)
    elif a.stage == "sep":
        sep_stage(nsample=a.n, pitch=a.pitch)
    else:
        guard_stage(nsample=a.n)


if __name__ == "__main__":
    main()
