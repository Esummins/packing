#!/usr/bin/env python3
"""
update_scoreboard114.py -- fold A114's closures (and, if the A61 campaign has not done it yet,
A61 pass 5's conversions) into the shared A56 scoreboard, in ONE ATOMIC WRITE.

The scoreboard attempts/A56-sparametric/results/scoreboard.json is a shared file: A56, A61 and
A114 all own rows in it.  This updater therefore

  * re-reads the file immediately before writing (never keeps a stale copy across a long run),
  * writes tmp + os.replace (atomic on NTFS: a concurrent reader sees the old or the new file,
    never a truncated one), exactly once per invocation,
  * touches ONLY the rows it can justify from a record file, and never deletes anything.

The A61 fold is update_scoreboard61.py's logic verbatim (P7 ledger rule: certificate
substitution -- the original A53/A54 certificate stays the s0 witness, the re-solved parametric
certificate carries the window claim, both kept with provenance).  It is idempotent, so running
this after the A61 campaign has folded its own rows changes nothing.

Usage: python update_scoreboard114.py [--dry]
"""
import argparse
import glob
import json
import os
import shutil
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A114 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A114, ".."))
A61R = os.path.join(ATT, "A61-window-stragglers", "results")
SB = os.path.join(ATT, "A56-sparametric", "results", "scoreboard.json")
RESULTS = os.path.join(A114, "results")
S_LO, S0 = F(191, 50), F(969271, 250000)
WIDTH = float(S0 - S_LO)


def cov(ranges):
    return round(sum(float(F(b) - F(a)) for a, b in ranges) / WIDTH, 6)


def merge(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def gaps(iv):
    out, cur = [], S_LO
    for lo, hi in iv:
        if lo > cur:
            out.append((cur, lo))
        cur = max(cur, hi)
    if cur < S0:
        out.append((cur, S0))
    return out


def fold_a61(rows, touched, converted):
    """update_scoreboard61.py's fold, unchanged."""
    for p in sorted(glob.glob(os.path.join(A61R, "resolve61_*.json"))):
        try:
            r = json.load(open(p))
        except Exception:
            continue                       # a record being rewritten by the running campaign
        n = r.get("name")
        if n not in rows or not r.get("verdict"):
            continue                       # in-flight record: never fold a partial run in
        row = rows[n]
        A = r.get("stageA") or {}
        B = r.get("stageB") or {}
        row["a61"] = {
            "attempt": "A61", "recipe": r.get("recipe"), "warm_atoms": r.get("warm_atoms"),
            "warm_rows": r.get("warm_rows"), "tau0_enriched": A.get("tau0"),
            "slack0": A.get("slack0"), "gate": r.get("gate"), "eps_geo": r.get("eps_geo"),
            "tau_at_eps_geo": B.get("tau"), "dtau_deps": r.get("dtau_deps"),
            "certify": r.get("certify"), "new_cert": r.get("new_cert"),
            "anchoring_tried": r.get("anchoring_tried"), "c2": r.get("c2"),
            "verdict": r.get("verdict"), "seconds": r.get("total_seconds"), "record": p}
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


def fold_a114(rows, touched, converted):
    for p in sorted(glob.glob(os.path.join(RESULTS, "k*.json"))):
        if p.endswith(".tmp"):
            continue
        try:
            r = json.load(open(p))
        except Exception:
            continue
        n = r.get("class")
        if n not in rows or not r.get("verdict"):
            continue
        row = rows[n]
        row["a114"] = {"attempt": "A114", "mechanism": r.get("mechanism"),
                       "band_attacked": r.get("band"), "cert": r.get("cert"),
                       "cert_sha256": r.get("cert_sha256"),
                       "verifier_sha256": r.get("verifier_sha256"),
                       "rows": r.get("rows"), "residual": r.get("residual"),
                       "gained": r.get("gained"), "still_open": r.get("still_open"),
                       "c2": r.get("c2"), "verdict": r.get("verdict"),
                       "seconds": r.get("wall_s"), "record": p}
        touched.append(n)
        if not r.get("gained"):
            row["a114_outcome"] = r.get("verdict")
            continue
        iv = merge([(F(x), F(y)) for x, y in
                    (row.get("s_ranges") or []) + [list(g) for g in r["gained"]]])
        row["s_ranges"] = [[str(x), str(y)] for x, y in iv]
        row["s_ranges_float"] = [[float(x), float(y)] for x, y in iv]
        row["window_coverage"] = cov(row["s_ranges"])
        g = gaps(iv)
        row["open_band"] = [[str(x), str(y)] for x, y in g]
        if not g:
            converted.append(n)
            row["result"] = "TRANSFERRED"
            row["status"] = (f"FULL [{S_LO}, {S0}] -- A114 closed the residue with the SAME "
                             f"parametric certificate re-verified on the sub-window(s) "
                             f"{r.get('gained')} (A96 resolver / A56 sub-window bisection; "
                             f"full C2 canary)")
        else:
            row["result"] = "partial"
            row["status"] = (f"PARTIAL after A114: certified {row['s_ranges']}, "
                             f"open {row['open_band']}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)

    sb = json.load(open(SB))                      # read immediately before the write
    rows = sb["rows"]
    touched, converted = [], []
    fold_a61(rows, touched, converted)
    fold_a114(rows, touched, converted)

    summ = {}
    for v in rows.values():
        summ[v["result"]] = summ.get(v["result"], 0) + 1
    full = sum(1 for v in rows.values() if v.get("window_coverage") == 1.0)
    sb.setdefault("summary", {})["by_result"] = summ
    sb["summary"]["full_window_rows"] = full
    byk = {}
    for v in rows.values():
        d = byk.setdefault(f"k{v['k']}", {})
        d[v["result"]] = d.get(v["result"], 0) + 1
    sb["summary"]["by_k"] = byk
    sb["a114"] = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "rows_touched": sorted(set(touched)),
                  "rows_converted_to_full_window": sorted(set(converted)),
                  "records": RESULTS,
                  "ledger_rule": "soundness.md P7 (certificate substitution) + A86 T4 "
                                 "WindowRows disjunction for the sub-window unions"}
    print(json.dumps({"touched": sorted(set(touched)), "converted": sorted(set(converted)),
                      "by_result": summ, "full_window_rows": full}, indent=1))
    if a.dry:
        print("(dry run; scoreboard not written)")
        return 0
    bak = SB + ".bak_pre_a114"
    if not os.path.exists(bak):
        shutil.copy2(SB, bak)
    tmp = SB + ".a114.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sb, fh, indent=1)
    os.replace(tmp, SB)                           # ONE atomic write
    print("->", SB, "(backup", bak + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
