#!/usr/bin/env python3
"""A38 depth-probe aggregation: kill matrix rows per stratum, both accountings, stalls."""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict

KILL_CERT = ("w1kill", "dead(certified)")
KILL_OPT = ("w1kill", "dead(certified)", "dead(LP-uncertified)")
SURV = ("alive(LP)", "undecided")


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [max(0.0, c - h), min(1.0, c + h)]


def med(v):
    v = sorted(v)
    return None if not v else (v[len(v) // 2] if len(v) % 2 else 0.5 * (v[len(v) // 2 - 1] + v[len(v) // 2]))


def summarize(doc, parents_meta=None):
    recs = doc["records"]
    byp = defaultdict(list)
    for r in recs:
        byp[str(r["parent"])].append(r)
    pmeta = {str(p["id"]): p for p in (parents_meta or doc.get("parents") or [])}

    strata = defaultdict(list)
    for r in recs:
        strata[r["stratum"]].append(r)

    rows = []
    for st in sorted(strata):
        R = [r for r in strata[st] if r["status"] != "notrun"]
        n = len(R)
        cnt = Counter(r["status"] for r in R)
        kc = sum(cnt[s] for s in KILL_CERT)
        ko = sum(cnt[s] for s in KILL_OPT)
        fc_ = kc / n if n else 0.0
        fo = ko / n if n else 0.0
        rows.append(dict(
            stratum=st, n_children=len(strata[st]), n_processed=n, counts=dict(cnt),
            f_certified=fc_, f_optimistic=fo,
            b_eff_certified=8 * (1 - fc_), b_eff_optimistic=8 * (1 - fo),
            ci95_f_certified=wilson(kc, n), ci95_f_optimistic=wilson(ko, n),
            median_seconds_lp=med([r.get("seconds_lp", 0.0) for r in R]),
            median_seconds_cert=med([r.get("seconds_cert", 0.0) for r in R
                                     if r.get("seconds_cert")]),
            tau_median=med([r["tau"] for r in R if r.get("tau") is not None]),
            tau_max=max([r["tau"] for r in R if r.get("tau") is not None], default=None),
            c_core_median=med([r["c_core"] for r in R if r.get("c_core") is not None]),
            c_core_max=max([r["c_core"] for r in R if r.get("c_core") is not None], default=None)))

    # ---- overall
    R = [r for r in recs if r["status"] != "notrun"]
    n = len(R); cnt = Counter(r["status"] for r in R)
    kc = sum(cnt[s] for s in KILL_CERT); ko = sum(cnt[s] for s in KILL_OPT)
    overall = dict(n_children=len(recs), n_processed=n, counts=dict(cnt),
                   f_certified=(kc / n if n else 0.0), f_optimistic=(ko / n if n else 0.0),
                   b_eff_certified=8 * (1 - kc / n) if n else None,
                   b_eff_optimistic=8 * (1 - ko / n) if n else None,
                   ci95_f_certified=wilson(kc, n), ci95_f_optimistic=wilson(ko, n),
                   median_seconds_lp=med([r.get("seconds_lp", 0.0) for r in R]))

    # ---- certification pass rate
    attempted = [r for r in recs if r.get("cert")]
    passed = [r for r in attempted if r["cert"]["result"] == "PASS"]
    timeouts = [r for r in attempted if r["cert"].get("timeout")]
    cert = dict(n_attempted=len(attempted), n_pass=len(passed),
                pass_rate=(len(passed) / len(attempted) if attempted else None),
                n_timeout=len(timeouts),
                median_seconds=med([r["cert"]["seconds"] for r in attempted]),
                median_seconds_pass=med([r["cert"]["seconds"] for r in passed]))

    # ---- stalls: parent whose ALL children are alive(LP) with zero W1/W2 contribution
    stalls = []
    for pid, R in sorted(byp.items()):
        Rp = [r for r in R if r["status"] != "notrun"]
        if not Rp:
            continue
        allalive = all(r["status"] == "alive(LP)" for r in Rp)
        n_w1 = sum(1 for r in Rp if r["status"] == "w1kill")
        # W2 contribution at node level: any child whose thr_node < thr_cert (multi-core) or w1kill
        w2c = sum(1 for r in Rp if r.get("thr_node") is not None and r.get("thr_cert") is not None
                  and r["thr_node"] < r["thr_cert"] - 1e-12)
        pm = pmeta.get(pid, {})
        d = dict(parent=pid, stratum=Rp[0]["stratum"], parent_l1_status=pm.get("l1_status"),
                 n=len(Rp), n_complete=len(R),
                 counts=dict(Counter(r["status"] for r in Rp)),
                 n_w1kill=n_w1, n_w2_threshold_active=w2c,
                 all_children_alive=allalive,
                 all_children_survive=all(r["status"] in SURV for r in Rp),
                 stall=bool(allalive and n_w1 == 0 and w2c == 0 and len(Rp) == len(R)),
                 # the honesty-rule variant: undecided-at-limit counts as a survivor, so a parent
                 # all of whose PROCESSED children survive with zero W1/W2 bite is a stall in the
                 # sense that matters for the branching bracket (weaker premise, same conclusion).
                 stall_honest=bool(all(r["status"] in SURV for r in Rp) and n_w1 == 0),
                 tau_median=med([r["tau"] for r in Rp if r.get("tau") is not None]),
                 c_core_max=max([r["c_core"] for r in Rp if r.get("c_core") is not None],
                                default=None))
        stalls.append(d)

    return dict(per_stratum=rows, overall=overall, certification=cert, per_parent=stalls,
                stall_count=sum(1 for d in stalls if d["stall"]),
                stall_parents=[d["parent"] for d in stalls if d["stall"]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probe_json")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    doc = json.load(open(a.probe_json))
    s = summarize(doc)
    print(json.dumps(s, indent=1))
    if a.out:
        doc["aggregate"] = s
        json.dump(doc, open(a.out, "w"), indent=1)
        print("->", a.out)


if __name__ == "__main__":
    main()
