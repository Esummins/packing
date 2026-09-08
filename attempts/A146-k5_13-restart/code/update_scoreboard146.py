#!/usr/bin/env python3
"""
update_scoreboard146.py -- fold A146's k5_13 closure into the shared A56 scoreboard,
in ONE ATOMIC WRITE, by A114's exact procedure.

`attempts/A114-window-closers/code/update_scoreboard114.py` is the reference: it

  * re-reads attempts/A56-sparametric/results/scoreboard.json immediately before writing
    (never a stale copy across a long run),
  * writes tmp + os.replace (atomic on NTFS: a concurrent reader sees the old file or the new
    one, never a truncated one), exactly once per invocation,
  * touches ONLY rows it can justify from a record file, and never deletes anything,
  * folds an A61 conversion through `fold_a61` (P7 ledger rule, certificate substitution: the
    original A53/A54 certificate stays the s0 witness, the re-solved parametric certificate
    carries the window claim, both kept with provenance) and an A114-style slab/sub-window
    closure through `fold_a114` (A86 T4 WindowRows disjunction over a union of closed
    sub-windows).

This script is those two folds restricted to k5_13 and pointed at A146's own record files, so
that A114's `a114` provenance block is left exactly as A114 wrote it.  Idempotent: running it
twice changes nothing but the timestamp.

Usage: python update_scoreboard146.py [--dry]
"""
import argparse
import json
import os
import shutil
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A146 = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(A146, ".."))
A61R = os.path.join(ATT, "A61-window-stragglers", "results")
SB = os.path.join(ATT, "A56-sparametric", "results", "scoreboard.json")
RESULTS = os.path.join(A146, "results")
S_LO, S0 = F(191, 50), F(969271, 250000)
WIDTH = float(S0 - S_LO)
NAME = "k5_13"


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
    """update_scoreboard114.fold_a61 / update_scoreboard61.py, verbatim, for k5_13 only."""
    p = os.path.join(A61R, f"resolve61_{NAME}.json")
    if not os.path.exists(p):
        return
    try:
        r = json.load(open(p))
    except Exception:
        return
    if NAME not in rows or not r.get("verdict"):
        return                                  # in-flight record: never fold a partial run in
    row = rows[NAME]
    A = r.get("stageA") or {}
    B = r.get("stageB") or {}
    row["a61"] = {
        "attempt": "A61 (restarted by A146 under a per-LP process wall)",
        "recipe": r.get("recipe"), "warm_atoms": r.get("warm_atoms"),
        "warm_rows": r.get("warm_rows"), "tau0_enriched": A.get("tau0"),
        "slack0": A.get("slack0"), "gate": r.get("gate"), "eps_geo": r.get("eps_geo"),
        "tau_at_eps_geo": B.get("tau"), "dtau_deps": r.get("dtau_deps"),
        "certify": r.get("certify"), "new_cert": r.get("new_cert"),
        "anchoring_tried": r.get("anchoring_tried"), "c2": r.get("c2"),
        "verdict": r.get("verdict"), "seconds": r.get("total_seconds"), "record": p}
    touched.append(NAME)
    if r.get("verdict", "").startswith("A61 CONVERTS"):
        converted.append(NAME)
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


def fold_a146_slabs(rows, touched, converted):
    """update_scoreboard114.fold_a114's shape, on A146's slab record: a union of closed
    sub-windows, each a PASS of the SAME frozen parametric certificate (A86 T4 WindowRows
    disjunction; every slab PASS is a sound partial transfer, P3)."""
    p = os.path.join(RESULTS, "slab146.json")
    if not os.path.exists(p):
        return
    try:
        r = json.load(open(p))
    except Exception:
        return
    sw = r.get("sweep") or {}
    gained = sw.get("covered") or []
    if NAME not in rows or not gained:
        return
    row = rows[NAME]
    row["a146"] = {"attempt": "A146", "mechanism": "A114 slab sweep (docs/budget.md section E "
                                                   "width law) on the A56 parametric certificate",
                   "cert": r.get("cert"), "slab_width": sw.get("width"),
                   "n_slabs": sw.get("n_slabs"), "depth": sw.get("depth"),
                   "gained": gained, "failed": sw.get("failed"),
                   "seconds": sw.get("seconds"), "c2": r.get("c2"), "record": p}
    touched.append(NAME)
    iv = merge([(F(x), F(y)) for x, y in (row.get("s_ranges") or []) + gained])
    row["s_ranges"] = [[str(x), str(y)] for x, y in iv]
    row["s_ranges_float"] = [[float(x), float(y)] for x, y in iv]
    row["window_coverage"] = cov(row["s_ranges"])
    g = gaps(iv)
    row["open_band"] = [[str(x), str(y)] for x, y in g]
    if not g:
        converted.append(NAME)
        row["result"] = "TRANSFERRED"
        row["certs"]["carries_the_window_claim"] = row["certs"].get("parametric_cert")
        row["status"] = (f"FULL [{S_LO}, {S0}] -- A146 closed the window with the SAME A56 "
                         f"parametric certificate re-verified slab by slab at width "
                         f"{sw.get('width')} (A114 slab-width law; full C2 canary)")
    else:
        row["result"] = "partial"
        row["status"] = (f"PARTIAL after A146: certified {row['s_ranges']}, "
                         f"open {row['open_band']}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)

    sb = json.load(open(SB))                      # read immediately before the write
    rows = sb["rows"]
    touched, converted = [], []
    fold_a61(rows, touched, converted)
    fold_a146_slabs(rows, touched, converted)

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
    sb["a146"] = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
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
    bak = SB + ".bak_pre_a146"
    if not os.path.exists(bak):
        shutil.copy2(SB, bak)
    tmp = SB + ".a146.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(sb, fh, indent=1)
    os.replace(tmp, SB)                           # ONE atomic write
    print("->", SB, "(backup", bak + ")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
