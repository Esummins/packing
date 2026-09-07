#!/usr/bin/env python3
"""
bench.py -- A129 T2.  Replay a stratified sample of A57 PASS certificates through the net verifier
and record, per leaf: reproduced or not, the net refinement needed, the shrink consumed, the wall
against the frozen verifier's recorded wall, and the failure mode when it fails.

READ-ONLY on every campaign directory: it opens A57's certificates and reports and writes nothing
outside attempts/A129-net-verifier/.

    python bench.py sample.json out.jsonl [--budget 180] [--lmax 26] [--check] [--shard i n]
"""
import sys
import os
import json
import time
import argparse
import ctypes
from fractions import Fraction as F

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import netverify as NV                                    # noqa: E402


def below_normal():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass


def one(rec, budget, lmax, l0=3):
    out = dict(rec)
    try:
        cert = NV.load_certificate(rec["cert_path"])
    except Exception as e:
        out["net"] = {"status": "MALFORMED", "error": str(e)}
        return out
    v = NV.NetVerifier(cert, use_numpy=True)
    v.timed_out = False
    t0 = time.time()
    try:
        ok = v.run_adaptive(l0, lmax, max_witnesses=3, time_budget=budget)
    except Exception as e:
        out["net"] = {"status": "ERROR", "error": repr(e), "wall_s": time.time() - t0}
        return out
    wall = v.elapsed
    Bmin = min((cc[2]["B"] for cc in v.cells), default=F(1))
    s = cert["s"]
    if ok:
        mode = "PASS"
    elif getattr(v, "timed_out", False):
        mode = "BLOWUP"          # the net did not terminate inside the budget
    else:
        mode = "MARGIN"          # the shrunk problem is feasible at the deepest net tried
    out["net"] = {
        "status": mode,
        "net_leaves": v.K,
        "deepest_level": getattr(v, "deepest", None),
        "B_min": str(Bmin),
        "B_min_float": float(Bmin),
        "shrink": float(1 - Bmin),
        "margin_consumed_side": float(s * (1 / Bmin - 1)) if Bmin > 0 else None,
        "wall_s": wall,
        "grid_cells": v.n_cells,
        "bisections": v.n_bisect,
        "exempt": v.n_exempt,
        "inadmissible": v.n_outside,
        "live_min_mass": (float(v.min_mass) if v.min_mass is not None else None),
        "witnesses": v.witnesses[:3],
    }
    if rec.get("frozen_wall_s"):
        out["net"]["wall_ratio_vs_frozen"] = wall / rec["frozen_wall_s"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sample")
    ap.add_argument("out")
    ap.add_argument("--budget", type=float, default=180.0)
    ap.add_argument("--lmax", type=int, default=26)
    ap.add_argument("--l0", type=int, default=3)
    ap.add_argument("--shard", nargs=2, type=int, default=None)
    a = ap.parse_args()
    below_normal()
    rows = json.load(open(a.sample))
    if a.shard:
        i, k = a.shard
        rows = [r for j, r in enumerate(rows) if j % k == i]
    with open(a.out, "w") as fh:
        for j, r in enumerate(rows):
            res = one(r, a.budget, a.lmax, a.l0)
            fh.write(json.dumps(res) + "\n")
            fh.flush()
            n = res["net"]
            print(f"[{j+1}/{len(rows)}] {r['id']:32s} atoms={r['n_atoms']:4d} "
                  f"{n.get('status'):9s} leaves={n.get('net_leaves')} "
                  f"L={n.get('deepest_level')} shrink={n.get('shrink')} "
                  f"wall={n.get('wall_s', 0):.1f}s frozen={r.get('frozen_wall_s', 0):.1f}s",
                  flush=True)


if __name__ == "__main__":
    main()
