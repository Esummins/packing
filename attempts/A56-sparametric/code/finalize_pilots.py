#!/usr/bin/env python3
"""
finalize_pilots.py -- fold the two stage-1 pilot runs (k5_15, k6_23) that were priced OUTSIDE
sweep.py into results/scoreboard.json, so the scoreboard is complete.  k5_15's canary C2 is run
here (three specialisations + the unmodified A53 verify_case.py); k6_23's row is recorded from
its pilot report (its 4D run FAILed, so there is nothing to cross-check).
"""
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                              # noqa: E402

S0, S_LO = SW.S0, SW.S_LO


class A:                                                        # minimal args object for sweep helpers
    depth0 = "44"
    heavy = 3
    timeout = 900


def stats_of(rep):
    st = json.load(open(rep))
    return st, {k: st.get("stats", {}).get(k) for k in
                ("boxes", "covered", "exempt", "vacuous", "split", "s_splits", "s_cells",
                 "max_depth", "max_s_depth")}


def main():
    sb_path = os.path.join(SW.RESULTS, "scoreboard.json")
    sb = json.load(open(sb_path))
    inv = {c["name"]: c for c in SW.load_inventory()["certs"]}
    log = os.path.join(SW.LOGS, "finalize_pilots.log")

    # ---- k5_15: 4D PASS at depth 56 (687.1 s, gap anchoring); run canary C2
    c = inv["k5_15"]
    par = os.path.join(SW.CERTS, "k5_15.gapB.param.json")
    st, ss = stats_of(os.path.join(SW.CERTS, "k5_15.d56.report.json"))
    c2 = SW.c2_crosscheck("k5_15", par, S_LO, A, log, tag=".pilot")
    sb["rows"]["k5_15"] = {
        "name": "k5_15", "k": c["k"], "margin": c["margin"], "atoms": c["atoms"],
        "corners": c["corners"], "single_corner": False, "anchoring": "gap",
        "depth": 56, "param_result": "PASS", "param_time_s": st["time_s"],
        "param_report": os.path.join(SW.CERTS, "k5_15.d56.report.json"),
        "param_stats": ss, "s_range": [str(S_LO), str(S0)], "c2": c2,
        "result": "TRANSFERRED" if all(x.get("result") == "PASS" for x in c2) else "C2-DISCREPANCY",
        "note": "stage-1 representative, run outside sweep.py at --depth 56",
    }

    # ---- k6_23: 4D FAIL at depth 56 (2727.6 s); undischarged boxes only in a sliver at s0
    c = inv["k6_23"]
    st, ss = stats_of(os.path.join(SW.CERTS, "k6_23.pilot.report.json"))
    sb["rows"]["k6_23"] = {
        "name": "k6_23", "k": c["k"], "margin": c["margin"], "atoms": c["atoms"],
        "corners": c["corners"], "single_corner": False, "anchoring": "gap",
        "depth": 56, "param_result": "FAIL", "param_time_s": st["time_s"],
        "param_report": os.path.join(SW.CERTS, "k6_23.pilot.report.json"),
        "param_stats": ss, "witness_s_range": st.get("witness_s_range"),
        "worst": SW.worst_witness(os.path.join(SW.CERTS, "k6_23.pilot.report.json")),
        "result": "OPEN",
        "note": ("stage-1 hard representative. 9 undischarged boxes at depth 56, 0 holes, ALL "
                 "inside the sliver s in [3.877000381, 3.877084] adjoining s0; the rest of the "
                 "window is discharged. A partial-transfer certificate on [191/50, 969250/250000] "
                 "is one further ~45 min run away (not spent)."),
    }
    sb["summary"] = SW.summarize(sb["rows"])
    SW.checkpoint(sb_path, sb)
    print(json.dumps(sb["summary"], indent=1))
    print("k5_15 C2:", c2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
