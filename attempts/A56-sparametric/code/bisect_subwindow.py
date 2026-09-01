#!/usr/bin/env python3
"""
bisect_subwindow.py -- A56 pass 3, item 1: SUB-WINDOW BISECTION.

For an OPEN certificate whose 4D FAIL witnesses are confined to a band of s hugging one end of
the window (or a narrow band in the middle), run verify_param on the COMPLEMENTARY sub-window(s)
-- the side away from the witnesses.  A PASS there is a sound PARTIAL transfer: the kill holds
for every s in that sub-window (soundness.md [S] applies verbatim to any closed s-cell contained
in W), and only the excluded band stays open.

The sub-window endpoints are derived from the certificate's own recorded witness s-range, pushed
outward by --guard units of 1/250000 so the excluded band strictly contains every witness box:

    witnesses in [wlo, whi]        sub-windows kept
    wlo == s_lo   (low end)        [ceil(whi*250000)+g , s0]
    whi == s0     (high end)       [s_lo , floor(wlo*250000)-g]
    otherwise     (middle band)    [s_lo , floor(wlo*250000)-g]  AND  [ceil(whi*250000)+g , s0]

Every PASS is followed by canary C2: the UNMODIFIED A53 verify_case.py on the specialisations at
the sub-window's two endpoints and its midpoint.  The scoreboard row becomes
    result = "partial",  s_ranges = [[a,b], ...],  open_band = [lo, hi]
with every bound an exact rational.

Usage:  python bisect_subwindow.py [--only k6_28,k6_32] [--depth 48] [--timeout 900] [--guard 2]
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                             # noqa: E402

S0, S_LO, DEN = SW.S0, SW.S_LO, 250000


class A:
    depth0 = "44"
    heavy = 3
    timeout = 1800


def grid_up(x, g):
    """smallest k/250000 >= x, pushed g units further up, clamped to s0"""
    n = -((-(x * DEN)) // 1) + g
    return min(S0, F(int(n), DEN))


def grid_dn(x, g):
    n = (x * DEN) // 1 - g
    return max(S_LO, F(int(n), DEN))


def windows_for(wlo, whi, guard):
    """complementary sub-windows of the witness band [wlo, whi] inside [s_lo, s0]"""
    out = []
    if wlo > S_LO:
        b = grid_dn(wlo, guard)
        if b > S_LO:
            out.append((S_LO, b))
    if whi < S0:
        a = grid_up(whi, guard)
        if a < S0:
            out.append((a, S0))
    return out


def c2_on(name, par, a, b, log, tag):
    d = os.path.join(SW.CERTS, "c2")
    os.makedirs(d, exist_ok=True)
    out = []
    for lbl, s in (("lo", a), ("mid", (a + b) / 2), ("hi", b)):
        spec = os.path.join(d, f"{name}{tag}.{lbl}.json")
        rep = os.path.join(d, f"{name}{tag}.{lbl}.report.json")
        rc, _ = SW.sh([sys.executable, SW.SPECIALIZE, par, "--s", str(s), "-o", spec], log)
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = SW.sh([sys.executable, SW.VERIFY_CASE, spec, "--depth", A.depth0,
                        "--jobs", str(A.heavy), "--report", rep, "--max-witnesses", "20",
                        "--witness-file", os.path.join(d, f"{name}{tag}.{lbl}.wit.json"),
                        "--quiet"], log, timeout=A.timeout)
        out.append({"s": str(s), "s_float": float(s),
                    "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc),
                    "time_s": round(dt, 1)})
        if rc != 0:
            break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default=None)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--sscale", default="8")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--guard", type=int, default=2, help="units of 1/250000 of outward guard")
    ap.add_argument("--max-band", type=float, default=0.02,
                    help="only attempt certs whose witness band is narrower than this")
    a = ap.parse_args(argv)

    sb_path = os.path.join(SW.RESULTS, "scoreboard.json")
    sb = json.load(open(sb_path))
    inv = {c["name"]: c for c in SW.load_inventory()["certs"]}
    todo = []
    for n, r in sb["rows"].items():
        if r["result"] not in ("OPEN", "TIMEOUT"):
            continue
        rep = r.get("param_report")
        if not rep or not os.path.exists(rep):
            continue
        wr = json.load(open(rep)).get("witness_s_range")
        if not wr:
            continue
        band = wr[1] - wr[0]
        if band > a.max_band:
            continue
        todo.append((band, n, wr))
    todo.sort()
    if a.only:
        keep = set(a.only.split(","))
        todo = [t for t in todo if t[1] in keep]
    print(f"sub-window bisection: {len(todo)} certificates, depth {a.depth}, guard {a.guard}/250000")

    spent = float(sb.get("cumulative_verifier_time_s", 0))
    for band, n, wr in todo:
        log = os.path.join(SW.LOGS, f"bisect_{n}.log")
        wins = windows_for(F(str(wr[0])).limit_denominator(10 ** 9),
                           F(str(wr[1])).limit_denominator(10 ** 9), a.guard)
        if not wins:
            print(f"  {n}: witness band covers the whole window, skipped")
            continue
        par = os.path.join(SW.CERTS, f"{n}.param.json")
        if not os.path.exists(par):
            rc, _ = SW.build_param(n, inv[n]["path"], par, "gap", log)
            if rc != 0:
                continue
        results, ok_wins, t_tot = [], [], 0.0
        for i, (lo, hi) in enumerate(wins):
            rep = os.path.join(SW.CERTS, f"{n}.sub{i}.report.json")
            rc, dt = SW.sh([sys.executable, SW.VERIFY_PARAM, par, "--slo", str(lo), "--shi", str(hi),
                            "--depth", str(a.depth), "--sscale", a.sscale, "--jobs", "3",
                            "--split", "3", "--report", rep, "--max-witnesses", "20",
                            "--witness-file", os.path.join(SW.CERTS, f"{n}.sub{i}.wit.json"),
                            "--quiet"], log, timeout=a.timeout)
            t_tot += dt
            res = {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)
            entry = {"window": [str(lo), str(hi)], "window_float": [float(lo), float(hi)],
                     "result": res, "time_s": round(dt, 1), "report": rep}
            if rc == 0:
                entry["c2"] = c2_on(n, par, lo, hi, log, f".sub{i}")
                if all(x.get("result") == "PASS" for x in entry["c2"]):
                    ok_wins.append((lo, hi))
                else:
                    entry["result"] = "C2-DISCREPANCY"
            results.append(entry)
            print(f"  {n:7s} [{float(lo):.6f}, {float(hi):.6f}] -> {entry['result']:8s} "
                  f"{round(dt,1)}s", flush=True)
        row = sb["rows"][n]
        row["subwindow_attempts"] = results
        row["param_time_s"] = round((row.get("param_time_s") or 0) + t_tot, 1)
        if ok_wins:
            row["result"] = "partial"
            row["s_ranges"] = [[str(x), str(y)] for x, y in ok_wins]
            row["s_ranges_float"] = [[float(x), float(y)] for x, y in ok_wins]
            covered = sum(float(y - x) for x, y in ok_wins)
            row["window_coverage"] = round(covered / float(S0 - S_LO), 6)
            gaps = []
            cur = S_LO
            for x, y in sorted(ok_wins):
                if x > cur:
                    gaps.append([str(cur), str(x)])
                cur = max(cur, y)
            if cur < S0:
                gaps.append([str(cur), str(S0)])
            row["open_band"] = gaps
            row["note"] = ("PARTIAL TRANSFER by sub-window bisection: certified on the listed "
                           "s-ranges (each with its own C2); open only on the listed band(s), "
                           "which strictly contain every recorded FAIL witness.")
        spent += t_tot
        sb["cumulative_verifier_time_s"] = round(spent, 1)
        sb["summary"] = SW.summarize(sb["rows"])
        SW.checkpoint(sb_path, sb)
    print(json.dumps(sb["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
