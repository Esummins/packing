#!/usr/bin/env python3
"""
sliver61.py -- A61's bounded tries on the two A56 PARTIAL rows (G-A56-2, G-A56-3).

k6_23 (G-A56-2).  A56's full-window depth-56 run FAILed with NINE undischarged boxes, 0
holes, all inside [3.877000381, 3.877084].  Nine is NOT a multiple of the per-box witness
cap 8, so by soundness.md P6(iv) that search COMPLETED and the witness s-range is a genuine
localisation, not a truncation sample.  The residue is therefore the open sliver
(3877/1000, s0), width 8.4e-5 = 1/680 of the window.  A61 re-runs the SAME parametric
certificate on that slab alone at higher depth: the s-axis has 680x less to bisect, so the
depth budget that was spent on s-splitting over the full window is available for (t, x, y),
which is exactly the P6(iii) situation where +8 depth pays (a tangency just past the
48-horizon).  Ladder: depth 56 -> 60 -> 64, each capped.

k6_07 (G-A56-3).  Certified on [191/50, 956767/250000]; the open band is 0.050 wide and the
A56 sub1 probe FAILed on [478393/125000, s0], so unlike k6_23 the failure is NOT localised
(sub1's own witnesses lie outside the full-window witness range).  A61 spends a bounded
budget bisecting the band and banking whatever sub-slabs PASS -- every PASSing slab is a
sound partial transfer under P3 and raises the row's window coverage; the residue is
reported honestly.

Nothing outside attempts/A61-window-stragglers/ is written.  A29 untouched.

Usage: python sliver61.py --which k6_23 [--depths 56,60,64] [--timeout 3600]
       python sliver61.py --which k6_07 [--slabs 4] [--depths 48,56]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A61 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A61, ".."))
A56 = os.path.join(ATT, "A56-sparametric")
sys.path.insert(0, os.path.join(A56, "code"))
import sweep as SW                                                    # noqa: E402

CERTS = os.path.join(A61, "certs", "slivers")
RESULTS = os.path.join(A61, "results")
LOGS = os.path.join(A61, "logs")
for _d in (CERTS, RESULTS, LOGS):
    os.makedirs(_d, exist_ok=True)

S0 = SW.S0
S_LO = SW.S_LO
PARAM = {n: os.path.join(A56, "certs", f"{n}.param.json") for n in ("k6_23", "k6_07")}
# A56 scoreboard: certified up to here, open above it (k6_23's open end is s0 itself)
OPEN_BAND = {"k6_23": (F(3877, 1000), S0), "k6_07": (F(956767, 250000), S0)}


def run(name, slo, shi, depth, tag, log, timeout, jobs, sscale="8"):
    rep = os.path.join(CERTS, f"{name}.{tag}.report.json")
    wit = os.path.join(CERTS, f"{name}.{tag}.wit.json")
    rc, dt = SW.sh([sys.executable, SW.VERIFY_PARAM, PARAM[name], "--slo", str(slo),
                    "--shi", str(shi), "--depth", str(depth), "--sscale", sscale,
                    "--jobs", str(jobs), "--split", "3", "--report", rep,
                    "--max-witnesses", "40", "--witness-file", wit, "--quiet"],
                   log, timeout=timeout)
    r = {"slo": str(slo), "shi": str(shi), "slo_f": float(slo), "shi_f": float(shi),
         "depth": depth, "seconds": round(dt, 1),
         "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)}
    if os.path.exists(rep):
        try:
            d = json.load(open(rep))
            r["stats"] = {q: d.get("stats", {}).get(q) for q in
                          ("boxes", "covered", "exempt", "vacuous", "s_splits", "s_cells",
                           "max_depth", "max_s_depth")}
            r["witness_s_range"] = d.get("witness_s_range")
            nw = len(d.get("witnesses", []) or [])
            r["n_witnesses"] = nw
            r["search_completed"] = bool(nw and nw % 8)      # P6(iv)
        except Exception:
            pass
    r["report"] = rep
    return rc, r


def c2(name, slo, shi, log, jobs):
    """C2 on the slab endpoints + midpoint with the UNMODIFIED A53 verify_case.py."""
    out = []
    for lbl, s in (("lo", slo), ("mid", (slo + shi) / 2), ("hi", shi)):
        spec = os.path.join(CERTS, f"{name}.c2.{lbl}.json")
        rep = os.path.join(CERTS, f"{name}.c2.{lbl}.report.json")
        rc, _ = SW.sh([sys.executable, SW.SPECIALIZE, PARAM[name], "--s", str(s), "-o", spec],
                      log)
        if rc != 0:
            out.append({"s": str(s), "result": "SPECIALIZE_ERROR"})
            break
        rc, dt = SW.sh([sys.executable, SW.VERIFY_CASE, spec, "--depth", "44", "--jobs",
                        str(jobs), "--report", rep, "--max-witnesses", "20", "--quiet"],
                       log, timeout=2400)
        out.append({"s": str(s), "s_float": float(s), "time_s": round(dt, 1),
                    "result": {0: "PASS", 1: "FAIL", 2: "MALFORMED", 124: "TIMEOUT"}.get(rc, rc)})
        if rc != 0:
            break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--which", required=True, choices=("k6_23", "k6_07"))
    ap.add_argument("--depths", default=None)
    ap.add_argument("--slabs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args(argv)
    name = a.which
    lo, hi = OPEN_BAND[name]
    log = os.path.join(LOGS, f"sliver61_{name}.log")
    rec = {"name": name, "open_band": [str(lo), str(hi)],
           "open_band_float": [float(lo), float(hi)], "width": float(hi - lo),
           "param_cert": PARAM[name], "attempts": [], "gained": [],
           "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    out = os.path.join(RESULTS, f"sliver61_{name}.json")

    def save():
        json.dump(rec, open(out, "w"), indent=1)

    save()
    if name == "k6_23":
        depths = [int(x) for x in (a.depths or "56,60,64").split(",")]
        for d in depths:
            # sscale 1: the slab is 8.4e-5 wide, so DON'T preferentially split s -- spend the
            # depth on (t, x, y), which is where the undischarged tangency lives.
            rc, r = run(name, lo, hi, d, f"slab_d{d}", log, a.timeout, a.jobs, sscale="1")
            rec["attempts"].append(r)
            save()
            print(f"  k6_23 slab depth {d}: {r['result']} ({r['seconds']}s)", flush=True)
            if rc == 0:
                rec["gained"].append([str(lo), str(hi)])
                rec["c2"] = c2(name, lo, hi, log, a.jobs)
                rec["verdict"] = ("SLIVER CLOSED: full window"
                                  if all(x.get("result") == "PASS" for x in rec["c2"])
                                  else "C2-DISCREPANCY")
                save()
                return 0
        rec["verdict"] = "sliver still open (depth ladder exhausted)"
        save()
        return 1

    # k6_07: bisect the band, bank every PASSing slab
    n = a.slabs
    depths = [int(x) for x in (a.depths or "48,56").split(",")]
    edges = [lo + (hi - lo) * F(i, n) for i in range(n + 1)]
    for i in range(n):
        s0_, s1_ = edges[i], edges[i + 1]
        got = False
        for d in depths:
            rc, r = run(name, s0_, s1_, d, f"slab{i}_d{d}", log, a.timeout, a.jobs)
            r["slab"] = i
            rec["attempts"].append(r)
            save()
            print(f"  k6_07 slab {i} [{float(s0_):.6f},{float(s1_):.6f}] depth {d}: "
                  f"{r['result']} ({r['seconds']}s)", flush=True)
            if rc == 0:
                rec["gained"].append([str(s0_), str(s1_)])
                got = True
                break
        if not got:
            rec.setdefault("still_open", []).append([str(s0_), str(s1_)])
        save()
    W = float(S0 - S_LO)
    gained = sum(float(F(b) - F(a_)) for a_, b in rec["gained"])
    rec["band_coverage_gained"] = round(gained / W, 6)
    rec["verdict"] = ("BAND CLOSED" if not rec.get("still_open")
                      else f"band partially closed (+{rec['band_coverage_gained']:.4f} of the window)")
    if rec["gained"]:
        rec["c2_first_gained"] = c2(name, F(rec["gained"][0][0]), F(rec["gained"][0][1]),
                                    log, a.jobs)
    save()
    return 0 if not rec.get("still_open") else 1


if __name__ == "__main__":
    sys.exit(main())
