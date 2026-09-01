#!/usr/bin/env python3
"""
finalize_partial.py -- record the k6_23 PARTIAL transfer.

The full-window 4D run FAILed with 9 undischarged boxes, all inside the sliver
s in [3.877000381, s0].  Re-running on the sub-window [191/50, 3877/1000] PASSes, so the kill is
certified for every s in [3.82, 3.877]; at s = s0 itself the A54 fixed-s certificate holds, and
only the half-open sliver (3.877, 3.877084) is open.  Canary C2 is run here on the sub-window's
own endpoints and midpoint with the unmodified A53 verify_case.py.
"""
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                              # noqa: E402

A_HI = F(3877, 1000)
S_LO = SW.S_LO


class A:
    depth0 = "44"
    heavy = 3
    timeout = 1800


def main():
    log = os.path.join(SW.LOGS, "finalize_partial.log")
    d = os.path.join(SW.CERTS, "c2")
    os.makedirs(d, exist_ok=True)
    par = os.path.join(SW.CERTS, "k6_23.param.json")
    c2 = []
    for lbl, s in (("lo", S_LO), ("mid", (S_LO + A_HI) / 2), ("hi", A_HI)):
        spec = os.path.join(d, f"k6_23.partial.{lbl}.json")
        rep = os.path.join(d, f"k6_23.partial.{lbl}.report.json")
        rc, _ = SW.sh([sys.executable, SW.SPECIALIZE, par, "--s", str(s), "-o", spec], log)
        if rc != 0:
            c2.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = SW.sh([sys.executable, SW.VERIFY_CASE, spec, "--depth", A.depth0,
                        "--jobs", str(A.heavy), "--report", rep, "--max-witnesses", "20",
                        "--witness-file", os.path.join(d, f"k6_23.partial.{lbl}.wit.json"),
                        "--quiet"], log, timeout=A.timeout)
        c2.append({"s": str(s), "s_float": float(s),
                   "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc),
                   "time_s": round(dt, 1)})
        print(c2[-1], flush=True)
        if rc != 0:
            break

    sb_path = os.path.join(SW.RESULTS, "scoreboard.json")
    sb = json.load(open(sb_path))
    full = json.load(open(os.path.join(SW.CERTS, "k6_23.pilot.report.json")))
    part = json.load(open(os.path.join(SW.CERTS, "k6_23.partial.report.json")))
    r = sb["rows"]["k6_23"]
    r.update({
        "result": "partial" if all(x.get("result") == "PASS" for x in c2) else "C2-DISCREPANCY",
        "param_result": "PASS on the sub-window",
        "s_range": [str(S_LO), str(A_HI)],
        "open_sliver": [str(A_HI), str(SW.S0)],
        "depth": 56,
        "param_time_s": round(full["time_s"] + part["time_s"], 1),
        "param_report": os.path.join(SW.CERTS, "k6_23.partial.report.json"),
        "param_stats": {k: part.get("stats", {}).get(k) for k in
                        ("boxes", "covered", "exempt", "vacuous", "split", "s_splits",
                         "s_cells", "max_depth", "max_s_depth")},
        "c2": c2,
        "probes": [{"a": str(SW.S0), "result": "FAIL", "time_s": full["time_s"],
                    "note": "full window; 9 undischarged boxes, 0 holes, all in "
                            "[3.877000381, 3.877084]"},
                   {"a": str(A_HI), "result": "PASS", "time_s": part["time_s"]}],
        "note": ("PARTIAL TRANSFER: certified for every s in [3.82, 3.877]; at s = s0 the A54 "
                 "fixed-s certificate holds; open only on the half-open sliver "
                 "(3.877, 3.877084), width 8.4e-5."),
    })
    sb["cumulative_verifier_time_s"] = round(
        float(sb.get("cumulative_verifier_time_s", 0)) + part["time_s"], 1)
    sb["summary"] = SW.summarize(sb["rows"])
    SW.checkpoint(sb_path, sb)
    print(json.dumps(sb["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
