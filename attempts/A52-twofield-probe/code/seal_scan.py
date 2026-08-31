#!/usr/bin/env python3
"""A39 P2b: find the MINIMAL uniform sealing scale that the exact verifier accepts for a field
certificate, then bake it in (A33 t1/seal_cert.py) and report eta_cert = total - 11.

Bisection over a rational scale ladder; every probe is a full exact verify_measure run, and the
final artifact is re-verified standalone with NO flags (the lab's sealing convention).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A33 = os.path.join(REPO, "attempts", "A33-tight-variety")
VERIFY = os.path.join(REPO, "certs", "verify_measure.py")
SEAL = os.path.join(A33, "t1", "seal_cert.py")


def probe(cert, scale, depth, jobs, report=None, timeout=7200):
    cmd = [sys.executable, VERIFY, cert, "--n", "12", "--depth", str(depth), "--split", "3",
           "--jobs", str(jobs), "--scale-weights", str(scale), "--max-witnesses", "8", "--quiet"]
    if report:
        cmd += ["--report", report]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    return rc, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", required=True)
    ap.add_argument("--depth", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--ladder", default="1.002,1.004,1.006,1.008,1.010,1.012,1.014,1.016,1.020,1.025")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sealed", default=None, help="write the sealed certificate here")
    a = ap.parse_args()
    tot1 = F(json.load(open(a.cert))["total"])
    ladder = [F(x) for x in a.ladder.split(",")]
    print("cert %s total@1 = %s = %.9f (eta %.9f)"
          % (os.path.basename(a.cert), tot1, float(tot1), float(tot1) - 11), flush=True)
    res = []
    lo, hi = 0, len(ladder) - 1
    best = None
    while lo <= hi:                      # bisection on a monotone predicate (PASS is upward closed)
        mid = (lo + hi) // 2
        sc = ladder[mid]
        rc, dt = probe(a.cert, sc, a.depth, a.jobs)
        eta = float(tot1 * sc) - 11
        res.append(dict(scale=str(sc), rc=rc, eta=eta, seconds=dt))
        print("  scale %s -> %s  eta=%.6f  (%.0fs)"
              % (sc, "PASS" if rc == 0 else "FAIL", eta, dt), flush=True)
        json.dump(dict(cert=a.cert, total1=str(tot1), probes=res), open(a.out, "w"), indent=1)
        if rc == 0:
            best = (sc, eta)
            hi = mid - 1
        else:
            lo = mid + 1
    out = dict(cert=a.cert, total1=str(tot1), probes=res,
               min_pass_scale=(str(best[0]) if best else None),
               eta_cert=(best[1] if best else None))
    if best and a.sealed:
        subprocess.run([sys.executable, SEAL, a.cert, str(best[0]), a.sealed], check=True)
        rc, dt = probe(a.sealed, 1, a.depth, a.jobs,
                       report=a.sealed.replace(".json", ".report.json"))
        out["sealed"] = a.sealed
        out["sealed_standalone_rc"] = rc
        out["sealed_verify_s"] = dt
        print("sealed %s standalone -> %s (%.0fs)" % (a.sealed, "PASS" if rc == 0 else "FAIL", dt),
              flush=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "probes"}, indent=1), flush=True)


if __name__ == "__main__":
    main()
