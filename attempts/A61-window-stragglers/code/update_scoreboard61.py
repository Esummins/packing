#!/usr/bin/env python3
"""
update_scoreboard61.py -- fold the A61 outcomes into the A56 scoreboard under the P7 ledger
rule (certificate substitution): a stratum's window claim may be carried by ANY exactly
verified certificate family; the original A53/A54 certificate remains the s0 witness, and
both are kept with provenance.  Nothing is deleted; every touched row grows an `a61` block
recording the recipe, the measured (tau0, slack0, tau_eps), the new base certificate and the
4D/C2 evidence.  A backup of the previous scoreboard is written before any change.

Usage: python update_scoreboard61.py [--dry]
"""
import argparse
import glob
import json
import os
import shutil
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A61 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A61, ".."))
SB = os.path.join(ATT, "A56-sparametric", "results", "scoreboard.json")
RESULTS = os.path.join(A61, "results")
S_LO, S0 = F(191, 50), F(969271, 250000)
WIDTH = float(S0 - S_LO)


def cov(ranges):
    return round(sum(float(F(b) - F(a)) for a, b in ranges) / WIDTH, 6)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    sb = json.load(open(SB))
    rows = sb["rows"]
    touched, converted = [], []

    # ---- the 12 s0-only strata
    for p in sorted(glob.glob(os.path.join(RESULTS, "resolve61_*.json"))):
        r = json.load(open(p))
        n = r["name"]
        if n not in rows or not r.get("verdict"):
            continue          # in-flight record (no verdict yet): never fold a partial run in
        row = rows[n]
        A = r.get("stageA") or {}
        B = r.get("stageB") or {}
        blk = {
            "attempt": "A61",
            "recipe": r.get("recipe"),
            "warm_atoms": r.get("warm_atoms"),
            "warm_rows": r.get("warm_rows"),
            "tau0_enriched": A.get("tau0"),
            "slack0": A.get("slack0"),
            "gate": r.get("gate"),
            "eps_geo": r.get("eps_geo"),
            "tau_at_eps_geo": B.get("tau"),
            "dtau_deps": r.get("dtau_deps"),
            "certify": r.get("certify"),
            "new_cert": r.get("new_cert"),
            "anchoring_tried": r.get("anchoring_tried"),
            "c2": r.get("c2"),
            "verdict": r.get("verdict"),
            "seconds": r.get("total_seconds"),
            "record": p,
        }
        row["a61"] = blk
        touched.append(n)
        if r.get("verdict", "").startswith("A61 CONVERTS"):
            converted.append(n)
            row["result"] = "TRANSFERRED-resolved"
            row["s_ranges"] = [[str(S_LO), str(S0)]]
            row["window_coverage"] = 1.0
            row["open_band"] = []
            row["anchoring"] = r.get("anchoring")
            row["status"] = (f"FULL [{S_LO}, {S0}] via an A61 re-solved base certificate "
                             f"(enriched column pool -> tau0 {A.get('tau0'):.6f}, "
                             f"eps_geo {r.get('eps_geo')}, anchoring {r.get('anchoring')}); "
                             f"P7 ledger rule: the A53/A54 certificate remains the s0 witness")
            row["certs"]["a61_base_cert"] = (r.get("new_cert") or {}).get("path")
            row["certs"]["a61_parametric_cert"] = r.get("param_cert")
            row["certs"]["carries_the_window_claim"] = r.get("param_cert")
            row["certs"]["provenance"] = (
                "P7 ledger rule (certificate substitution): the stratum claim is "
                "certificate-fungible. s0 endpoint witness = original_s0_cert (A53/A54); "
                "window claim = a61_parametric_cert (A61 resolve61). Both verified, both kept.")
        else:
            row["a61_outcome"] = r.get("verdict")

    # ---- the two partial slivers
    for p in sorted(glob.glob(os.path.join(RESULTS, "sliver61_*.json"))):
        r = json.load(open(p))
        n = r["name"]
        if n not in rows:
            continue
        row = rows[n]
        row["a61_sliver"] = {"attempt": "A61", "attempts": r.get("attempts"),
                             "gained": r.get("gained"), "still_open": r.get("still_open"),
                             "c2": r.get("c2") or r.get("c2_first_gained"),
                             "verdict": r.get("verdict"), "record": p}
        touched.append(n)
        if r.get("gained"):
            merged = [[str(F(x)), str(F(y))] for x, y in
                      (row.get("s_ranges") or []) + r["gained"]]
            # merge touching/overlapping ranges
            iv = sorted(((F(x), F(y)) for x, y in merged))
            out = []
            for lo, hi in iv:
                if out and lo <= out[-1][1]:
                    out[-1] = (out[-1][0], max(out[-1][1], hi))
                else:
                    out.append((lo, hi))
            row["s_ranges"] = [[str(x), str(y)] for x, y in out]
            row["window_coverage"] = cov(row["s_ranges"])
            row["open_band"] = [] if (len(out) == 1 and out[0] == (S_LO, S0)) else \
                [[str(x), str(y)] for x, y in _gaps(out)]
            if not row["open_band"]:
                row["result"] = "TRANSFERRED"
                row["status"] = f"FULL [{S_LO}, {S0}] (A61 closed the residual slab)"
            else:
                row["status"] = (f"PARTIAL after A61: certified {row['s_ranges']}, "
                                 f"open {row['open_band']}")

    summ = {}
    for v in rows.values():
        summ[v["result"]] = summ.get(v["result"], 0) + 1
    full = sum(1 for v in rows.values() if v.get("window_coverage") == 1.0)
    sb["summary"]["by_result"] = summ
    sb["summary"]["full_window_rows"] = full
    byk = {}
    for v in rows.values():
        d = byk.setdefault(f"k{v['k']}", {})
        d[v["result"]] = d.get(v["result"], 0) + 1
    sb["summary"]["by_k"] = byk
    sb["a61"] = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                 "gap": "G-A56-1 (+ G-A56-2/3 slivers)",
                 "rows_touched": sorted(set(touched)),
                 "rows_converted_to_full_window": sorted(converted),
                 "ledger_rule": "soundness.md P7 (certificate substitution)",
                 "notes": os.path.join(A61, "notes", "lemmas.md")}
    print(json.dumps({"touched": sorted(set(touched)), "converted": sorted(converted),
                      "by_result": summ, "full_window_rows": full}, indent=1))
    if a.dry:
        print("(dry run; scoreboard not written)")
        return 0
    bak = SB + f".bak_pre_a61"
    if not os.path.exists(bak):
        shutil.copy2(SB, bak)
    json.dump(sb, open(SB, "w"), indent=1)
    print("->", SB, "(backup", bak + ")")
    return 0


def _gaps(iv):
    out = []
    cur = S_LO
    for lo, hi in iv:
        if lo > cur:
            out.append((cur, lo))
        cur = max(cur, hi)
    if cur < S0:
        out.append((cur, S0))
    return out


if __name__ == "__main__":
    raise SystemExit(main())
