#!/usr/bin/env python3
"""Feasibility residual of the float LP fields used for the exploratory maps.

For each field: the smallest mass of an eps-shrunk unit square found by the A19/A20 row oracle
(RowOracle.search).  A field with worst mass < 1 is NOT feasible, so its "eta = total - 11" and
the resulting exclusion map are heuristic; the certified maps use the sealed exact certificates.
"""
import os
import sys
import json
import argparse
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "t1"))
from lp_measure2 import RowOracle                                        # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fields", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n_theta", type=int, default=181)
    ap.add_argument("--cstep", type=float, default=0.01)
    a = ap.parse_args()
    out = {}
    for p in a.fields:
        d = json.load(open(p))
        P = np.array([[x, y] for x, y, w in d["atoms"]])
        W = np.array([w for x, y, w in d["atoms"]])
        ro = RowOracle(float(d["s"]), P, W, n_theta=a.n_theta, cstep=a.cstep, delta=0.001)
        found = ro.search(thresh=1.0, max_refine=60, max_return=200)
        worst = min([f[3] for f in found], default=1.0)
        out[os.path.basename(p)] = {"total": float(W.sum()), "eta_own": float(W.sum()) - 11.0,
                                    "n_violating_rows": len(found),
                                    "worst_shrunk_mass": float(worst),
                                    "row_violation": float(max(0.0, 1.0 - worst))}
        print(os.path.basename(p), out[os.path.basename(p)], flush=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print("written", a.out)


if __name__ == "__main__":
    main()
