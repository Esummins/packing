#!/usr/bin/env python3
"""A33/T2 step 0: field diversity + Trump canary.

  python diagnose.py --out results/diversity.json
"""
import os
import sys
import json
import math
import argparse
import numpy as np
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper import load_field_atoms, coverage_at, load_cert_exact          # noqa: E402
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "certs"))
from verify_measure import mass_at_frac                                     # noqa: E402

T1 = os.path.join(_REPO, "attempts", "A33-tight-variety", "t1")


# ------------------------------------------------------------------ Trump placements (canary)
def trump_squares(s_target=None):
    d = json.load(open(os.path.join(_REPO, "certs", "trump11_certificate.json")))
    s_cert = F(d["side"])
    out = []
    for q in d["squares"]:
        cx, cy, t = F(q["cx"]), F(q["cy"]), F(q["t"])
        out.append((t, cx, cy))
    lam = F(1)
    if s_target is not None and F(s_target) != s_cert:
        lam = F(s_target) / s_cert
        out = [(t, cx * lam, cy * lam) for (t, cx, cy) in out]
    return out, s_cert, lam


def check_disjoint(sq):
    """separating-axis check that the 11 unit squares are pairwise disjoint (float, with gap)."""
    def corners(t, cx, cy):
        t = float(t); c = (1 - t * t) / (1 + t * t); sn = 2 * t / (1 + t * t)
        out = []
        for (a, b) in ((.5, .5), (.5, -.5), (-.5, -.5), (-.5, .5)):
            out.append((float(cx) + c * a - sn * b, float(cy) + sn * a + c * b))
        return np.array(out)
    P = [corners(*q) for q in sq]
    worst = 1e9
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            best = -1e9
            for poly in (P[i], P[j]):
                for k in range(4):
                    e = poly[(k + 1) % 4] - poly[k]
                    ax = np.array([-e[1], e[0]]) / np.hypot(*e)
                    a = P[i] @ ax
                    b = P[j] @ ax
                    gap = max(a.min() - b.max(), b.min() - a.max())
                    best = max(best, gap)
            worst = min(worst, best)
    return worst   # > 0 => all pairs strictly separated


# --------------------------------------------------------------------------------- diversity
def rand_placements(s, n, rng):
    """uniform on P_s in (t,cx,cy) with dt measure (rejection on the admissible window)."""
    T, X, Y = [], [], []
    while len(T) < n:
        t = rng.random(n)
        w = (1 - t * t) / (1 + t * t) + 2 * t / (1 + t * t)
        lo, hi = w / 2, s - w / 2
        cx = lo + (hi - lo) * rng.random(n)
        cy = lo + (hi - lo) * rng.random(n)
        T.extend(t.tolist()); X.extend(cx.tolist()); Y.extend(cy.tolist())
    return np.array(T[:n]), np.array(X[:n]), np.array(Y[:n])


def grid_weights(A, W, s, h=0.05):
    n = int(math.ceil(s / h))
    g = np.zeros((n, n))
    ix = np.clip((A[:, 0] / h).astype(int), 0, n - 1)
    iy = np.clip((A[:, 1] / h).astype(int), 0, n - 1)
    np.add.at(g, (ix, iy), W)
    return g


def support_jaccard(A1, A2, tol=2e-3):
    from scipy.spatial import cKDTree
    t2 = cKDTree(A2)
    d1, _ = t2.query(A1)
    t1 = cKDTree(A1)
    d2, _ = t1.query(A2)
    m1 = int((d1 <= tol).sum())
    m2 = int((d2 <= tol).sum())
    return (m1 + m2) / (len(A1) + len(A2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/diversity.json")
    ap.add_argument("--nsample", type=int, default=40000)
    a = ap.parse_args()
    rng = np.random.default_rng(20260827)

    fields = {}
    for tag in ["base", "r3", "r4", "r5", "r6", "r7"]:
        p = os.path.join(T1, "results",
                         "field_3.877084.json" if tag == "base" else f"field_3.877084_{tag}.json")
        s, A, W, meta = load_field_atoms(p)
        fields[tag] = dict(path=p, s=s, A=A, W=W, tau=float(W.sum()), meta=meta)
    sealed_path = os.path.join(T1, "certs", "A33_measure_feasible_3.877084.json")
    s, A, W, meta = load_field_atoms(sealed_path)
    fields["sealed"] = dict(path=sealed_path, s=s, A=A, W=W, tau=float(W.sum()), meta=meta)

    s0 = fields["r6"]["s"]
    T, X, Y = rand_placements(s0, a.nsample, rng)
    cov = {}
    for k, f in fields.items():
        cov[k] = coverage_at(f["A"][:, 0], f["A"][:, 1], f["W"], T, X, Y)

    eta_float = 0.2429
    thr_f = 1 + eta_float
    tight = {k: (v <= thr_f) for k, v in cov.items()}

    tags = list(fields)
    pairs = {}
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            a1, a2 = tags[i], tags[j]
            g1 = grid_weights(fields[a1]["A"], fields[a1]["W"], s0)
            g2 = grid_weights(fields[a2]["A"], fields[a2]["W"], s0)
            l1 = float(np.abs(g1 / g1.sum() - g2 / g2.sum()).sum()) / 2
            c1, c2 = cov[a1], cov[a2]
            t1_, t2_ = tight[a1], tight[a2]
            un = float((t1_ | t2_).sum())
            pairs[f"{a1}|{a2}"] = {
                "support_jaccard_2e-3": round(support_jaccard(fields[a1]["A"], fields[a2]["A"]), 4),
                "weight_TV_grid0.05": round(l1, 4),
                "cov_mean_abs_diff": round(float(np.abs(c1 - c2).mean()), 5),
                "cov_corr": round(float(np.corrcoef(c1, c2)[0, 1]), 5),
                "tight_jaccard_eta0.2429": round(float((t1_ & t2_).sum()) / un if un else 1.0, 5),
                "tight_symdiff_frac": round(float((t1_ ^ t2_).sum()) / len(t1_), 5),
            }

    per_field = {k: {"path": os.path.relpath(f["path"], _REPO).replace("\\", "/"),
                     "n_atoms": int(len(f["A"])), "total_mass": round(f["tau"], 9),
                     "cov_mean": round(float(cov[k].mean()), 5),
                     "cov_max_sampled": round(float(cov[k].max()), 5),
                     "cov_min_sampled": round(float(cov[k].min()), 5),
                     "frac_tight_eta0.2429": round(float(tight[k].mean()), 5)}
                 for k, f in fields.items()}

    # ------------------------------------------------------------------ canary
    sq, s_cert, lam = trump_squares(s_target=None)
    gap = check_disjoint(sq)
    canary = {"trump_cert_side": str(s_cert), "lambda_applied_in_cert": str(lam),
              "min_pairwise_separation": gap, "squares": [], "fields": {}}
    for (t, cx, cy) in sq:
        canary["squares"].append({"t": str(t), "cx": str(cx), "cy": str(cy),
                                  "theta_deg": round(math.degrees(2 * math.atan(float(t))), 6)})
    for k, f in fields.items():
        vals = [float(coverage_at(f["A"][:, 0], f["A"][:, 1], f["W"],
                                  np.array([float(t)]), np.array([float(cx)]), np.array([float(cy)]))[0])
                for (t, cx, cy) in sq]
        canary["fields"][k] = {"coverage": [round(v, 8) for v in vals],
                               "sum": round(sum(vals), 8),
                               "min": round(min(vals), 8), "max": round(max(vals), 8),
                               "total_mass": round(f["tau"], 9),
                               "escape": round(f["tau"] - sum(vals), 8)}
    # exact coverage under the sealed certificate
    _d, s_ex, at_ex, w_ex = load_cert_exact(sealed_path)
    ex = []
    for (t, cx, cy) in sq:
        ex.append(mass_at_frac(at_ex, w_ex, t, cx, cy))
    canary["sealed_exact"] = {"coverage": [str(v) for v in ex],
                              "coverage_float": [round(float(v), 10) for v in ex],
                              "sum": str(sum(ex, F(0))), "sum_float": float(sum(ex, F(0))),
                              "total": str(sum(w_ex, F(0))),
                              "escape": float(sum(w_ex, F(0)) - sum(ex, F(0)))}

    out = {"per_field": per_field, "pairs": pairs, "canary": canary,
           "n_sampled_placements": a.nsample, "eta_float_used": eta_float}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(per_field, indent=1))
    print(json.dumps(pairs, indent=1))
    print("canary min separation", gap)
    for k, v in canary["fields"].items():
        print(f"  {k:7s} cov min {v['min']:.6f} max {v['max']:.6f} sum {v['sum']:.6f} escape {v['escape']:.6f}")
    print("sealed exact: min", min(canary["sealed_exact"]["coverage_float"]),
          "max", max(canary["sealed_exact"]["coverage_float"]),
          "sum", canary["sealed_exact"]["sum_float"], "escape", canary["sealed_exact"]["escape"])
    print("written", a.out)


if __name__ == "__main__":
    main()
