"""A152 T4 -- the targeted pass over A141's OWN 244 slot-lane kill cells.

The population sweep answers "does the refinement buy anything new?".  This answers the other
half: "what does the refinement COST?" -- i.e. how many of A141's 244 exact-cell / exact-pin kills
survive when the same cell is run in the node's real (slack) pin regime at an ADMISSIBLE translate.

    python t4_a141cells.py [--wall 900]
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import lane152 as L152                                   # noqa: E402
import numpy as np                                       # noqa: E402
import t2_sweep as T2                                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=900.0)
    ap.add_argument("--sample", type=int, default=8000)
    ap.add_argument("--maxopen", type=int, default=500)
    a = ap.parse_args()
    src = os.path.join(ROOT, "attempts", "A141-polycore-lane", "results", "t4_slots.jsonl")
    want = []
    for ln in open(src, encoding="utf-8"):
        r = json.loads(ln)
        if r["verdict"] == "KILL":
            want.append((r["nid"], r["slot"]))
    recs = collections.defaultdict(list)
    for r in L152.alive_records():
        recs[r["nid"]].append(r)
    rng = np.random.default_rng(15299)
    cover_budget = [a.wall]
    out, t0 = [], time.time()
    miss = 0
    for (nid, slot) in want:
        if nid not in recs:
            miss += 1
            continue
        for rec in recs[nid]:
            if slot not in L152.CP.CLASSES[rec["cls"]]["usable"]:
                continue
            if time.time() - t0 > a.wall:
                break
            row, best, ij = T2.do_cell(rec, slot, L152.H_G1, rng, a.sample, a.maxopen,
                                       cover_budget)
            for v in row["rows"]:
                v.pop("_res", None)
                v.pop("_conds", None)
            out.append(row)
    tal = collections.Counter()
    for r in out:
        tr = [v for v in r["rows"] if v["kind"] == "trans"]
        sh = [v for v in r["rows"] if v["kind"] == "shrunk"]
        tal["a141_cells_rerun"] += 1
        tal["still_KILL_at_some_admissible_translate"] += any(v["verdict"] == "KILL" for v in tr)
        tal["KILL_at_the_shrunk_cell"] += any(v["verdict"] == "KILL" for v in sh)
        tal["baseline_exact_screen_lane_lb0"] += (r["baseline_exact"]["lane_lb"] == 0)
        best = min((v["verdict"] for v in tr), key=lambda x: 0 if x == "KILL" else 1) if tr \
            else "none"
        tal["best_" + (best if best == "KILL" else
                       [v["verdict"] for v in tr][0] if tr else "none")] += 1
    p = os.path.join(BASE, "results", "t4_a141cells.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    s = dict(tally=dict(tal), a141_kill_cells=len(want), not_in_alive_corpus=miss,
             seconds=round(time.time() - t0, 1))
    json.dump(s, open(os.path.join(BASE, "results", "t4_a141cells.json"), "w",
                      encoding="utf-8"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
