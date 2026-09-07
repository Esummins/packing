#!/usr/bin/env python3
"""
ladder.py -- A129 T3.  The net-refinement PROFILE of a whole-problem measure certificate.

For each of a set of sample positions t in [0,1] (t = tan(theta/2)), find the smallest level L such
that the net cell of level L containing that position passes on its own, and time it.  From the
profile L(t) the adaptive net's size and wall are estimated by

    net cells  ~  sum over the sample of 2^L(t) / (number of samples)          (a Riemann sum of
                  the density 2^{L(t)} of an adaptive net that is level L(t) locally)
    wall       ~  (net cells) x (median per-cell wall at the level that passed)

This is exact per sample point -- every reported PASS is a real, exact decision for that net cell --
and only the aggregation over [0,1] is an estimate.

    python ladder.py cert.json out.json [--samples 24] [--lmin 6] [--lmax 20]
"""
import sys
import os
import json
import time
import argparse
import ctypes
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netverify as NV        # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("out")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--lmin", type=int, default=6)
    ap.add_argument("--lmax", type=int, default=20)
    ap.add_argument("--budget", type=float, default=2400.0)
    a = ap.parse_args()
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass

    cert = NV.load_certificate(a.cert)
    v = NV.NetVerifier(cert)
    print(f"{a.cert}: s = {cert['s']} n = {cert['n']} atoms = {len(cert['atoms'])} "
          f"total = {float(cert['total']):.9f} budget = {cert['budget']} "
          f"cores = {len(cert['cores'])} nofams = {len(cert['nofams'])}", flush=True)
    N = a.samples
    prof = []
    t_all = time.time()
    for i in range(N):
        # sample position: the midpoint of the i-th of N equal pieces of [0,1]
        pos = F(2 * i + 1, 2 * N)
        rec = {"i": i, "pos": str(pos), "pos_float": float(pos), "steps": []}
        for L in range(a.lmin, a.lmax + 1):
            K = 1 << L
            j = int(pos * K)
            t0, t1 = F(j, K), F(j + 1, K)
            t0_ = time.time()
            try:
                ok, info = v.net_cell(t0, t1, max_witnesses=1)
            except ValueError:
                ok, info = False, {"B": F(0), "n_light": None}
            dt = time.time() - t0_
            rec["steps"].append({"L": L, "pass": bool(ok), "wall_s": dt,
                                 "B": str(info["B"]), "B_float": float(info["B"]),
                                 "shrink": float(1 - info["B"]),
                                 "light": info.get("n_light"),
                                 "live_min": (float(info["live_min"])
                                              if info.get("live_min") is not None else None),
                                 "grid_min": (float(info["grid_min"]) if "grid_min" in info else None)})
            if ok:
                rec["L_pass"] = L
                rec["wall_pass_s"] = dt
                break
        print(f"  t ~ {float(pos):.4f} (theta ~ "
              f"{2*__import__('math').degrees(__import__('math').atan(float(pos))):7.3f} deg)  "
              f"L_pass = {rec.get('L_pass')}  {rec.get('wall_pass_s', 0):.2f}s  "
              f"[{time.time()-t_all:.0f}s]", flush=True)
        prof.append(rec)
        if time.time() - t_all > a.budget:
            print("  [budget reached]")
            break

    got = [r for r in prof if r.get("L_pass") is not None]
    est = None
    if got:
        cells = sum(1 << r["L_pass"] for r in got) / len(got)
        percell = sorted(r["wall_pass_s"] for r in got)[len(got) // 2]
        est = {"sampled": len(prof), "resolved": len(got),
               "L_min": min(r["L_pass"] for r in got), "L_max": max(r["L_pass"] for r in got),
               "est_net_cells": cells, "median_per_cell_s": percell,
               "est_wall_s": cells * percell, "est_wall_h": cells * percell / 3600.0}
        print(f"\n  L_pass in [{est['L_min']}, {est['L_max']}]; estimated adaptive net "
              f"{cells:,.0f} orientations; median {percell:.2f}s per orientation; "
              f"estimated wall {est['est_wall_h']:.2f} h")
    json.dump({"cert": os.path.abspath(a.cert), "s": str(cert["s"]), "n": cert["n"],
               "atoms": len(cert["atoms"]), "cores": len(cert["cores"]),
               "profile": prof, "estimate": est,
               "wall_s": time.time() - t_all}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
