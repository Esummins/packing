#!/usr/bin/env python3
"""Pair-variety spot check (A33 lemma remark (b)):  how much of  T_eta x T_eta  restricted to
DISJOINT square pairs already violates the two-square subfamily bound

        mu(Q(x)) + mu(Q(y))  <=  2 + eta          (Lemma A33.1 (i) with |I| = 2)

which the per-square bound mu(Q) <= 1 + eta alone does NOT imply (it only gives 2 + 2 eta).
Placements are drawn from the surviving raster of a map and kept only if their EXACT coverage
is <= 1 + eta (so both members really lie in T_eta).
"""
import os
import sys
import json
import math
import argparse
import numpy as np
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper import load_cert_exact, field_to_exact, coverage_at          # noqa: E402
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "certs"))
from verify_measure import mass_at_frac                                   # noqa: E402


def corners(t, cx, cy):
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    return np.array([[cx + c * a - sn * b, cy + sn * a + c * b]
                     for (a, b) in ((.5, .5), (.5, -.5), (-.5, -.5), (-.5, .5))])


def disjoint(P, Q):
    best = -1e9
    for poly in (P, Q):
        for k in range(4):
            e = poly[(k + 1) % 4] - poly[k]
            ax = np.array([-e[1], e[0]]) / math.hypot(*e)
            a, b = P @ ax, Q @ ax
            best = max(best, max(a.min() - b.max(), b.min() - a.max()))
    return best > 0, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--npairs", type=int, default=200)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    M = json.load(open(a.map))
    g = np.load(os.path.splitext(a.map)[0] + "_raster.npz", allow_pickle=True)["grid"]
    src = M["extra"]["source_path"]
    if "A33_measure" in os.path.basename(src) or os.path.basename(src).startswith("cert"):
        _d, s, atoms, weights = load_cert_exact(src)
    else:
        _d, s, atoms, weights = field_to_exact(src)
    eta = F(M["extra"]["eta"])
    thr = 1 + eta
    sf = float(s)
    G = M["grid"]
    NT, NC, hc, clo = G["NT"], G["NC"], G["cell_c"], G["c_lo"]
    PX = np.array([float(p[0]) for p in atoms])
    PY = np.array([float(p[1]) for p in atoms])
    W = np.array([float(w) for w in weights])
    rng = np.random.default_rng(a.seed)

    surv = np.array(np.nonzero((g == 1) | (g == 2)))
    n = surv.shape[1]
    print(f"surviving cells: {n}")

    def draw(m):
        sel = rng.integers(0, n, size=m)
        i, j, k = surv[0, sel], surv[1, sel], surv[2, sel]
        t = (i + rng.random(m)) / NT
        cx = clo + (j + rng.random(m)) * hc
        cy = clo + (k + rng.random(m)) * hc
        c = (1 - t * t) / (1 + t * t)
        sn = 2 * t / (1 + t * t)
        h = (c + sn) / 2
        ok = (cx >= h) & (cx <= sf - h) & (cy >= h) & (cy <= sf - h)
        cv = coverage_at(PX, PY, W, t, cx, cy)
        ok &= cv <= float(thr)
        return t[ok], cx[ok], cy[ok], cv[ok]

    T, X, Y, CV = [], [], [], []
    tries = 0
    while len(T) < 4 * a.npairs and tries < 400:
        t, x, y, cv = draw(4000)
        T.extend(t.tolist()); X.extend(x.tolist()); Y.extend(y.tolist()); CV.extend(cv.tolist())
        tries += 1
    T, X, Y, CV = map(np.array, (T, X, Y, CV))
    print(f"drew {len(T)} placements in T_eta")

    rows = []
    n_disj = n_fail = 0
    tried = 0
    idx = rng.permutation(len(T))
    p = 0
    while n_disj < a.npairs and p + 1 < len(idx):
        i, j = idx[p], idx[p + 1]
        p += 2
        tried += 1
        P = corners(T[i], X[i], Y[i])
        Qc = corners(T[j], X[j], Y[j])
        ok, gap = disjoint(P, Qc)
        if not ok:
            continue
        n_disj += 1
        ti = F(round(T[i] * 10 ** 9), 10 ** 9); xi = F(round(X[i] * 10 ** 9), 10 ** 9)
        yi = F(round(Y[i] * 10 ** 9), 10 ** 9)
        tj = F(round(T[j] * 10 ** 9), 10 ** 9); xj = F(round(X[j] * 10 ** 9), 10 ** 9)
        yj = F(round(Y[j] * 10 ** 9), 10 ** 9)
        mi = mass_at_frac(atoms, weights, ti, xi, yi)
        mj = mass_at_frac(atoms, weights, tj, xj, yj)
        ssum = mi + mj
        fail = ssum > 2 + eta
        n_fail += bool(fail)
        rows.append({"cov_x": float(mi), "cov_y": float(mj), "sum": float(ssum),
                     "excess_over_2_plus_eta": float(ssum - (2 + eta)),
                     "separation": float(gap), "violates_pair_bound": bool(fail)})
    sums = np.array([r["sum"] for r in rows])
    out = {"map": a.map, "eta": str(eta), "thr_single": float(thr), "thr_pair": float(2 + eta),
           "n_pairs_tested": n_disj, "n_random_pairs_drawn": tried,
           "disjoint_acceptance_rate": n_disj / max(1, tried),
           "n_violating_pair_bound": n_fail,
           "frac_of_TxT_disjoint_killed_by_pair_bound": n_fail / max(1, n_disj),
           "sum_mean": float(sums.mean()) if len(sums) else None,
           "sum_max": float(sums.max()) if len(sums) else None,
           "sum_min": float(sums.min()) if len(sums) else None,
           "trivial_upper_bound_2_plus_2eta": float(2 + 2 * eta),
           "pairs": rows[:200]}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "pairs"}, indent=1))


if __name__ == "__main__":
    main()
