#!/usr/bin/env python
# -*- coding: ascii -*-
"""emit413_v2.py -- A73 T3: assemble the corners4 (k4_13) beta=0 v2 candidate
certificate from the A71 emission seed, and run the per-run Trump canary
(A71 semantics, results written into A73).

Usage: python emit413_v2.py [--out ../certs/pair_k4_13_s0_b0_seed.json]
"""
import argparse
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A71 = os.path.join(REPO, "attempts", "A71-pair-emission")
A73 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(A71, "code"))

S0 = Fr(969271, 250000)
DELTA = Fr(1, 1000)
CORE_A = Fr(1, 2) - DELTA          # slack core half-side


def frs(x):
    return str(Fr(x))


def canary(log_path):
    """Trump canary under A73 parameters; writes results/canary_trump.json in A73."""
    import emitk408 as ek
    import emitlib as el
    # redirect the A71 writer's BASE to A73 so we never touch A71 state
    el.BASE = A73
    ek.el.BASE = A73
    fh = open(log_path, "a")
    ok = ek.canary_trump(fh, delta=DELTA, eps_box=Fr(1, 833))
    fh.close()
    return ok


def build(out_path, seed_path=None):
    seed = json.load(open(seed_path or
                          os.path.join(A71, "results", "pair_primal_k4_13_b0.json")))
    spec = json.load(open(os.path.join(REPO, "attempts", "A65-low-k-closure",
                                       "results", "h10_boxspec.json")))
    pins = spec["classes"]["k4_13"]["pins"]
    assert len(pins) == 4
    cores = [{"kx": frs(p[0]), "ky": frs(p[1]), "a": frs(CORE_A)} for p in pins]
    atoms = []
    tot = Fr(0)
    for a in seed["atoms"]:
        w = Fr(a["w"])
        if w <= 0:
            continue
        tot += w
        atoms.append({"px": a["px"], "py": a["py"],
                      "qx": a["qx"], "qy": a["qy"], "w": a["w"]})
    cert = {
        "format": "pair-certificate-v2",
        "s": frs(S0),
        "n": 11, "k": 4, "m": 0,
        "beta": "0",
        "cores": cores,
        "boxes": [],
        "atoms": atoms,
        "total": frs(tot),
        "provenance": {
            "attempt": "A73-pair-v2 T3 pilot",
            "cls": "k4_13 (corners4)",
            "seed": seed_path or
                    "attempts/A71-pair-emission/results/pair_primal_k4_13_b0.json",
            "seed_eta": str(seed.get("provenance", {}).get("eta")),
            "delta": frs(DELTA),
            "note": "beta=0 emptiness candidate (Corollary P0 consumption); "
                    "slack cores half-side 1/2 - delta at the 4 corner pins; "
                    "m declared 0 (boxes unused at beta=0).",
            "W2_str": frs(tot),
        },
    }
    with open(out_path, "w") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
    print("wrote %s  atoms=%d W2=%s (threshold 21)" % (out_path, len(atoms), tot))
    return cert


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(A73, "certs",
                                                  "pair_k4_13_s0_b0_seed.json"))
    ap.add_argument("--seed", default=None,
                    help="primal JSON to assemble (default: the A71 sharp seed)")
    ap.add_argument("--skip-canary", action="store_true")
    args = ap.parse_args()
    if not args.skip_canary:
        ok = canary(os.path.join(A73, "logs", "canary.log"))
        print("canary:", "SAFE" if ok else "FAILED")
        if not ok:
            sys.exit(3)
    build(args.out, args.seed)
