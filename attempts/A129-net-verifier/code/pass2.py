#!/usr/bin/env python3
"""
pass2.py -- A129 T2, second pass.  A BLOWUP in bench.py means "the adaptive net had not terminated
inside the wall budget", not "the method fails".  This turns each BLOWUP into a NUMBER: sample a few
positions in t, find the smallest net level at which the cell there passes on its own (an exact
decision), and estimate from that profile how large a net the leaf needs and what it would cost.

    python pass2.py blowups.json out.jsonl [--samples 8] [--lmin 4] [--lmax 16] [--shard i n]
"""
import sys
import os
import json
import time
import math
import argparse
import ctypes
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netverify as NV       # noqa: E402


def profile(cert_path, samples, lmin, lmax, budget):
    cert = NV.load_certificate(cert_path)
    v = NV.NetVerifier(cert)
    out = []
    t0 = time.time()
    for i in range(samples):
        pos = F(2 * i + 1, 2 * samples)
        rec = {"pos": str(pos), "pos_float": float(pos), "L_pass": None, "wall_pass_s": None,
               "wall_total_s": 0.0}
        for L in range(lmin, lmax + 1):
            K = 1 << L
            j = int(pos * K)
            ta = time.time()
            try:
                ok, info = v.net_cell(F(j, K), F(j + 1, K), max_witnesses=1)
            except ValueError:
                ok, info = False, {"B": F(0)}
            dt = time.time() - ta
            rec["wall_total_s"] += dt
            if ok:
                rec["L_pass"] = L
                rec["wall_pass_s"] = dt
                rec["shrink"] = float(1 - info["B"])
                break
        out.append(rec)
        if time.time() - t0 > budget:
            break
    return out, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("blowups")
    ap.add_argument("out")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--lmin", type=int, default=4)
    ap.add_argument("--lmax", type=int, default=16)
    ap.add_argument("--budget", type=float, default=420.0)
    ap.add_argument("--shard", nargs=2, type=int, default=None)
    a = ap.parse_args()
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
    rows = json.load(open(a.blowups))
    if a.shard:
        i, k = a.shard
        rows = [r for j, r in enumerate(rows) if j % k == i]
    with open(a.out, "w") as fh:
        for r in rows:
            prof, wall = profile(r["cert_path"], a.samples, a.lmin, a.lmax, a.budget)
            got = [p for p in prof if p["L_pass"] is not None]
            est = None
            if got:
                cells = sum(1 << p["L_pass"] for p in got) / len(got)
                per = sorted(p["wall_pass_s"] for p in got)[len(got) // 2]
                est = {"resolved": len(got), "sampled": len(prof),
                       "L_min": min(p["L_pass"] for p in got),
                       "L_max": max(p["L_pass"] for p in got),
                       "est_net_cells": cells, "median_per_cell_s": per,
                       "est_wall_s": cells * per,
                       "est_ratio_vs_frozen": (cells * per / r["frozen_wall_s"]
                                               if r.get("frozen_wall_s") else None)}
            rec = {"id": r["id"], "n_atoms": r["n_atoms"], "n_cores": r["n_cores"],
                   "level": r["level"], "stratum": r.get("stratum"),
                   "frozen_wall_s": r.get("frozen_wall_s"), "frozen_boxes": r.get("frozen_boxes"),
                   "profile": prof, "estimate": est, "pass2_wall_s": wall}
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"{r['id']:30s} atoms={r['n_atoms']:4d} "
                  f"resolved={len(got)}/{len(prof)} "
                  f"L=[{est['L_min'] if est else '-'},{est['L_max'] if est else '-'}] "
                  f"est_cells={est['est_net_cells'] if est else '-'} "
                  f"est_wall={est['est_wall_s'] if est else '-'} "
                  f"frozen={r.get('frozen_wall_s', 0):.1f}s  ({wall:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
