"""A152 T6 -- settle the screen-level NEW candidates.

`t3_fold.py` lists the cells where SOME admissible translate is a kill candidate
(`lane_lb = 0, M_lb <= 1`) while the exact-cell / exact-pin BASELINE is not -- the only cells at
which the refinement could ever produce a kill A141 does not already have.  There are few of them,
so they are run here with a generous cover budget (the sweep's covers are capped, and after the
sweep's cover budget runs out they are not run at all).

Also re-runs the sweep's UNSOUNDNESS CANARY cells (shrunk-cell KILL, no translate kill) with the
same generous budget, so the canary is not an artefact of a truncated cover.

    python t6_candidates.py [--wall 900]
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lane152 as L152                                   # noqa: E402
import numpy as np                                       # noqa: E402
import t2_sweep as T2                                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=900.0)
    ap.add_argument("--sample", type=int, default=10000)
    ap.add_argument("--maxopen", type=int, default=1500)
    a = ap.parse_args()
    tab = json.load(open(os.path.join(BASE, "results", "t3_tables.json"), encoding="utf-8"))
    jobs = [(e["key"], e["slot"], "new_candidate") for e in tab["screen_new_examples"]]
    jobs += [(e["key"], e["slot"], "unsound_canary")
             for e in tab["unsound_canary_shrunk_fires_no_translate_does"]["examples"]]
    jobs += [(e["key"], e["slot"], "lost_candidate") for e in tab["screen_lost_examples"]]
    recs = {T2.reckey(r): r for r in L152.alive_records()}
    rng = np.random.default_rng(15266)
    budget = [1e9]
    out, t0 = [], time.time()
    for (key, slot, why) in jobs:
        if key not in recs or time.time() - t0 > a.wall:
            continue
        rec = recs[key]
        row, best, ij = T2.do_cell(rec, slot, L152.H_G1, rng, a.sample, a.maxopen, budget)
        row["why"] = why
        if best is not None:
            cp, sha = T2.emit(rec, slot, best, ij, L152.H_G1, os.path.join(BASE, "certs"))
            best["cert"], best["sha256"] = cp, sha
        for v in row["rows"]:
            v.pop("_res", None)
            v.pop("_conds", None)
        out.append(row)
        tr = [v["verdict"] for v in row["rows"] if v["kind"] == "trans"]
        sh = [v["verdict"] for v in row["rows"] if v["kind"] == "shrunk"]
        print("%-14s %-46s %-9s base_lane_lb=%s trans=%s shrunk=%s"
              % (why, key, slot, row["baseline_exact"]["lane_lb"], tr, sh), flush=True)
    tal = collections.Counter()
    for r in out:
        tr = [v["verdict"] for v in r["rows"] if v["kind"] == "trans"]
        sh = [v["verdict"] for v in r["rows"] if v["kind"] == "shrunk"]
        tal[r["why"] + "_n"] += 1
        tal[r["why"] + "_translate_KILL"] += ("KILL" in tr)
        tal[r["why"] + "_shrunk_KILL"] += ("KILL" in sh)
    with open(os.path.join(BASE, "results", "t6_candidates.jsonl"), "w",
              encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    s = dict(jobs=len(jobs), run=len(out), tally=dict(tal),
             seconds=round(time.time() - t0, 1))
    json.dump(s, open(os.path.join(BASE, "results", "t6_candidates.json"), "w",
                      encoding="utf-8"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
