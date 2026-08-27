#!/usr/bin/env python3
"""Soundness spot-check of an exclusion map.

  (a) EXCLUDED boxes: sample admissible placements inside each of N random excluded boxes and
      verify by EXACT rational arithmetic that mu(Q) > thr there  (an exclusion cover is wrong
      the moment one placement in it has coverage <= thr).
  (b) INSIDE cells of the raster: the cell centre must have exact coverage <= thr.
  (c) the 11 Trump placements must NOT lie in any excluded box (canary).
"""
import os
import sys
import json
import math
import argparse
import numpy as np
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper import load_cert_exact, field_to_exact                       # noqa: E402
from diagnose import trump_squares                                        # noqa: E402
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "certs"))
from verify_measure import mass_at_frac                                   # noqa: E402


def admissible(s, t, cx, cy):
    c = (1 - t * t) / (1 + t * t)
    sn = 2 * t / (1 + t * t)
    h = (c + sn) / 2
    return h <= cx <= s - h and h <= cy <= s - h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("map")
    ap.add_argument("--nboxes", type=int, default=300)
    ap.add_argument("--ncells", type=int, default=300)
    a = ap.parse_args()
    M = json.load(open(a.map))
    src = M["extra"]["source_path"]
    if not os.path.isabs(src):
        src = os.path.join(os.path.dirname(os.path.abspath(a.map)), "..", src) \
            if not os.path.exists(src) else src
    if "cert" in os.path.basename(src) or "A33_measure" in os.path.basename(src):
        _d, s, atoms, weights = load_cert_exact(src)
    else:
        _d, s, atoms, weights = field_to_exact(src)
    thr = 1 + F(M["extra"]["eta"])
    sc = M["int_scale"]
    T_ROOT, D = sc["T_ROOT"], sc["D"]
    rng = np.random.default_rng(7)

    E = M["excluded_boxes"]
    nE = len(E["T0"])
    bad_excl, tested_excl, worst = 0, 0, None
    if nE:
        pick = rng.choice(nE, size=min(a.nboxes, nE), replace=False)
        for b in pick:
            T0, T1 = E["T0"][b], E["T1"][b]
            X0, X1 = E["X0"][b], E["X1"][b]
            Y0, Y1 = E["Y0"][b], E["Y1"][b]
            for _ in range(3):
                T = int(rng.integers(T0, T1 + 1))
                X = int(rng.integers(X0, X1 + 1))
                Y = int(rng.integers(Y0, Y1 + 1))
                t, cx, cy = F(T, T_ROOT), F(X, D), F(Y, D)
                if not admissible(float(s), float(t), float(cx), float(cy)):
                    continue
                m = mass_at_frac(atoms, weights, t, cx, cy)
                tested_excl += 1
                if worst is None or m < worst:
                    worst = m
                if m <= thr:
                    bad_excl += 1
                    print("UNSOUND EXCLUSION", float(t), float(cx), float(cy), float(m), float(thr))

    # ---- (b) INSIDE cells
    npz = os.path.splitext(a.map)[0] + "_raster.npz"
    bad_in, tested_in, worst_in = 0, 0, None
    if os.path.exists(npz):
        g = np.load(npz, allow_pickle=True)["grid"]
        G = M["grid"]
        idx = np.array(np.nonzero(g == 1))
        if idx.shape[1]:
            sel = rng.choice(idx.shape[1], size=min(a.ncells, idx.shape[1]), replace=False)
            for q in sel:
                i, j, k = idx[:, q]
                t = F(int(2 * i + 1), int(2 * G["NT"]))
                cx = F(round((G["c_lo"] + (j + 0.5) * G["cell_c"]) * 10 ** 9), 10 ** 9)
                cy = F(round((G["c_lo"] + (k + 0.5) * G["cell_c"]) * 10 ** 9), 10 ** 9)
                if not admissible(float(s), float(t), float(cx), float(cy)):
                    continue
                m = mass_at_frac(atoms, weights, t, cx, cy)
                tested_in += 1
                if worst_in is None or m > worst_in:
                    worst_in = m
                if m > thr:
                    bad_in += 1
                    print("BAD INSIDE CELL", float(t), float(cx), float(cy), float(m), float(thr))

    # ---- (c) canary: the 11 Trump placements, exact coverage + raster cell status
    sq, s_cert, lam = trump_squares()
    hits, canary = [], []
    G = M["grid"]
    for n, (t, cx, cy) in enumerate(sq):
        m = mass_at_frac(atoms, weights, t, cx, cy)
        i = int(min(max(math.floor(float(t) * G["NT"]), 0), G["NT"] - 1))
        j = int(min(max(math.floor((float(cx) - G["c_lo"]) / G["cell_c"]), 0), G["NC"] - 1))
        k = int(min(max(math.floor((float(cy) - G["c_lo"]) / G["cell_c"]), 0), G["NC"] - 1))
        st = int(g[i, j, k]) if os.path.exists(npz) else -1
        canary.append({"sq": n, "theta_deg": round(math.degrees(2 * math.atan(float(t))), 4),
                       "cx": round(float(cx), 6), "cy": round(float(cy), 6),
                       "coverage": float(m), "coverage_exact": str(m),
                       "in_T_eta": bool(m <= thr), "cell_status": st})
        if st == 0:
            hits.append(n)
        if m > thr:
            hits.append(("coverage_over_threshold", n))
    out = {"map": a.map, "thr": str(thr), "n_excluded_boxes": nE,
           "excl_placements_tested": tested_excl, "excl_violations": bad_excl,
           "excl_min_exact_coverage": float(worst) if worst is not None else None,
           "inside_cells_tested": tested_in, "inside_violations": bad_in,
           "inside_max_exact_coverage": float(worst_in) if worst_in is not None else None,
           "canary_trump_in_excluded": hits, "canary": canary,
           "verdict": "OK" if (bad_excl == 0 and bad_in == 0 and not hits) else "PROBLEM"}
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    r = main()
    sys.exit(0 if r["verdict"] == "OK" else 1)
