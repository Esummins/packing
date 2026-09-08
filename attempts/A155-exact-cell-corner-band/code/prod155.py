"""A155 T2 -- the four-corner PRODUCT cover at a chosen pad (A150's T2, re-run at pad 0 and 5e-4).

Identical machinery to `attempts/A150-four-corner-product/code/prod150.py` (imported read-only for
the corner frames and the D4 action on 4-tuples); the only change is that the band, the cells and
the polygon cores are those of the chosen K0-WIDEN pad (cells155), so the "exact-cell pair kills"
of A155 T1 enter the product both through the band and through every pair matrix.

Kills, in increasing cost order (each a NECESSARY condition on a K0-BLOCKED packing):
  (Q2)  max centre distance over the two global boxes < 1  ==>  the two squares overlap
  (Q1)  K'(box_1) meets K'(box_2)  (A132 exact polygon cores)
  (Q1s) A131 per-tilt-sub-bin refinement of (Q1), 4 sub-bins a side
applied on the four ADJACENT corner pairs (one matrix A by the rotation symmetry of the frames) and
on the two DIAGONALS (one matrix D).  All kills are pairwise, so the survivor count of the 4-cycle
is a transfer-matrix trace and the D4 orbit count is Burnside over frames150.D4.

    python code/prod155.py --stage pairs --pads w0,w5e-4
    python code/prod155.py --stage stages --pads w0,w5e-4
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
           os.path.join(ATT, "A150-four-corner-product", "code"),
           os.path.join(ATT, "A132-polygon-core", "code"),
           os.path.join(ATT, "A135-polycore-verifier", "code"),
           os.path.join(ATT, "A57-shadow-trees", "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import frames150 as F                                           # noqa: E402  (read-only)
import cells155 as C                                            # noqa: E402
from caselp import Box                                          # noqa: E402

RES = os.path.join(BASE, "results")
MAXV = 16
NSUB = 4
S0 = C.S0


def pad_by_tag(tag):
    for t, w, why in C.PADS:
        if t == tag:
            return w, why
    raise SystemExit("unknown pad tag " + tag)


def global_box(corner, cell):
    b = cell.box
    X0, X1, Y0, Y1 = F.to_global(corner, b.x0, b.x1, b.y0, b.y1)
    return Box(X0, X1, Y0, Y1, b.th0, b.th1)


def global_subbins(corner, cell, a_w, nsub=NSUB):
    out = []
    for (a, b, cl) in C.subbin_clip(*cell.raw, a_w=a_w, nsub=nsub):
        X0, X1, Y0, Y1 = F.to_global(corner, cl[0], cl[1], cl[2], cl[3])
        out.append(Box(X0, X1, Y0, Y1, a, b))
    return out


def max_centre_dist(b1, b2):
    dx = max(abs(b1.x1 - b2.x0), abs(b2.x1 - b1.x0))
    dy = max(abs(b1.y1 - b2.y0), abs(b2.y1 - b1.y0))
    return math.hypot(dx, dy)


def load_band(tag):
    d = json.load(open(os.path.join(RES, "band155_pairs_%s.json" % tag), encoding="utf-8"))
    a_w = d["a_w"]
    byk = {c.key: c for c in C.all_cells(a_w) if not c.empty}
    keys = [tuple(k) for k in d["band_cells"]]
    return keys, [byk[k] for k in keys], a_w


def pair_matrices(cells, a_w, c1, c2, tag, log=print):
    """returns (M_Q2, M_Q2Q1, M_all) and the kill counts."""
    n = len(cells)
    G1 = [global_box(c1, c) for c in cells]
    G2 = [global_box(c2, c) for c in cells]
    t0 = time.time()
    K1 = [polycore.build(b, max_v=MAXV) for b in G1]
    K2 = K1 if c1 == c2 else [polycore.build(b, max_v=MAXV) for b in G2]
    M2 = np.ones((n, n), np.uint8)
    M21 = np.ones((n, n), np.uint8)
    M = np.ones((n, n), np.uint8)
    kills = dict(Q2=0, Q1=0, Q1s=0)
    for i in range(n):
        for j in range(n):
            if max_centre_dist(G1[i], G2[j]) < 1.0:
                M2[i, j] = M21[i, j] = M[i, j] = 0
                kills["Q2"] += 1
            elif polycore.poly_poly_depth(K1[i].P, K2[j].P) > 0.0:
                M21[i, j] = M[i, j] = 0
                kills["Q1"] += 1
    near = [(i, j) for i in range(n) for j in range(n)
            if M[i, j] and max_centre_dist(G1[i], G2[j]) < 2.5]
    if near:
        sub1 = [global_subbins(c1, c, a_w) for c in cells]
        sub2 = sub1 if c1 == c2 else [global_subbins(c2, c, a_w) for c in cells]
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
    kills["total"] = n * n
    kills["n_near_tested"] = len(near)
    log("%s %s-%s: %s in %.0f s" % (tag, c1, c2, json.dumps(kills), time.time() - t0))
    return (M2, M21, M), kills


def count_product(A, D, keys):
    """exact survivor count of the 4-cycle with the two diagonal constraints, plus Burnside."""
    n = len(keys)
    A64 = A.astype(np.int64)
    if bool(D.all()):
        M2 = A64 @ A64
        total = int(np.einsum("ij,ji->", M2, M2))
    else:
        total = 0
        for a0 in range(n):
            m1 = A64[a0] > 0
            m3 = A64[:, a0] > 0
            m2 = D[a0] > 0
            sub = A64[np.ix_(m1, m2)]
            sub3 = A64[np.ix_(m2, m3)]
            Dm = D[np.ix_(m1, m3)]
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
    fix["m_diag"] = sum(1 for a in tfix for c in tfix for b in range(n)
                        if alive((a, b, c, int(tp[b]))))
    fix["m_anti"] = sum(1 for b in tfix for d in tfix for a in range(n)
                        if alive((a, b, int(tp[a]), d)))
    fix["m_horiz"] = sum(1 for a in range(n) for b in range(n)
                         if alive((a, b, int(tp[b]), int(tp[a]))))
    fix["m_vert"] = sum(1 for a in range(n) for b in range(n)
                        if alive((a, int(tp[a]), int(tp[b]), b)))
    orbits = sum(fix.values()) / 8.0
    return dict(total=total, fix=fix, orbits=orbits,
                orbits_exact=(int(orbits) if abs(orbits - round(orbits)) < 1e-9 else orbits))


def pairs_stage(tag, log=print):
    keys, cells, a_w = load_band(tag)
    (A2, A21, A), kA = pair_matrices(cells, a_w, "BL", "BR", tag, log)
    (D2, D21, D), kD = pair_matrices(cells, a_w, "BL", "TR", tag, log)
    for nm, M in (("A2", A2), ("A21", A21), ("A", A), ("D2", D2), ("D21", D21), ("D", D)):
        np.save(os.path.join(RES, "prod155_%s_%s.npy" % (tag, nm)), M)
    idx = {k: i for i, k in enumerate(keys)}
    tp = np.array([idx.get(F.T(k), -1) for k in keys])
    ok = bool((A == A[tp][:, tp].T).all()) if (tp >= 0).all() else None
    out = dict(tag=tag, band=len(keys), adj=kA, diag=kD, A_mirror_consistent=ok)
    json.dump(out, open(os.path.join(RES, "prod155_pairs_%s.json" % tag), "w"), indent=1)
    log(json.dumps(out, indent=1))
    return out


def stages_stage(tag, log=print):
    keys, _cells, _a_w = load_band(tag)
    n = len(keys)
    M = {nm: np.load(os.path.join(RES, "prod155_%s_%s.npy" % (tag, nm)))
         for nm in ("A2", "A21", "A", "D2", "D21", "D")}
    ones = np.ones((n, n), np.uint8)
    tab = []
    for name, Am, Dm in (("0 raw band product", ones, ones),
                         ("1 +Q2 adjacent centre distance", M["A2"], ones),
                         ("2 +Q1 adjacent K'-vs-K'", M["A21"], ones),
                         ("3 +Q1s adjacent per-sub-bin", M["A"], ones),
                         ("4 +Q2/Q1/Q1s on the two diagonals", M["A"], M["D"])):
        r = count_product(Am, Dm, keys)
        r["stage"] = name
        r["adj_alive_frac"] = float(Am.mean())
        r["diag_alive_frac"] = float(Dm.mean())
        tab.append(r)
        log("%-8s %-38s tuples %d   D4-orbits %s" % (tag, name, r["total"], r["orbits_exact"]))
    out = dict(tag=tag, band=n, raw_product=n ** 4, stages=tab)
    json.dump(out, open(os.path.join(RES, "prod155_stages_%s.json" % tag), "w"), indent=1)
    return out


def pick_stage(tag, n=10, seed=1550, log=print):
    """uniformly drawn surviving 4-tuples (for the LP), reported with their D4 canonical form."""
    keys, _cells, _a_w = load_band(tag)
    A = np.load(os.path.join(RES, "prod155_%s_A.npy" % tag))
    D = np.load(os.path.join(RES, "prod155_%s_D.npy" % tag))
    rng = np.random.default_rng(seed)
    nk = len(keys)
    out = []
    seen = set()
    while len(out) < n:
        t = [int(x) for x in rng.integers(0, nk, 4)]
        if not (A[t[0], t[1]] and A[t[1], t[2]] and A[t[2], t[3]] and A[t[3], t[0]]
                and D[t[0], t[2]] and D[t[1], t[3]]):
            continue
        tup = tuple(keys[i] for i in t)
        can = F.canonical(tup)
        if can in seen:
            continue
        seen.add(can)
        out.append([list(k) for k in tup])
    json.dump(dict(tag=tag, n=len(out), seed=seed, tuples=out),
              open(os.path.join(RES, "prod155_pick_%s.json" % tag), "w"), indent=1)
    log(json.dumps(out))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=("pairs", "stages", "pick"))
    ap.add_argument("--pads", default="w0")
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    for t in a.pads.split(","):
        if a.stage == "pairs":
            pairs_stage(t)
        elif a.stage == "stages":
            stages_stage(t)
        else:
            pick_stage(t, n=a.n)


if __name__ == "__main__":
    main()
