#!/usr/bin/env python3
"""A39: discharge A38's G1 certification debt.

A38 left 38 of its 44 level-1 dead(T1) nodes as kill(LP) only (6 sampled + root certified,
2 sampled FAILED under certify.py).  This driver runs the A39 loop on every one of them:
round 0 costs ONE verifier run on the CACHED node LP (no re-solve at all); failures get witness
rows fed back and a rows-only re-solve, up to --rounds times.

The exact verifier is the sole arbiter: a PASS is a standalone certificate that never mentions
the LP's convergence state.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
A38 = os.path.abspath(os.path.join(HERE, "..", "..", "A38-root-power", "results"))
OUT = os.path.abspath(os.path.join(HERE, "..", "results", "p2a", "g1"))


def one(args):
    idx, s_rat, rounds, jobs, depth, max_w, tl = args
    import earlycert as ec
    node = os.path.join(A38, "l1_nodes", "node_%03d.json" % idx)
    pre = os.path.join(OUT, "node_%03d" % idx)
    t0 = time.time()
    try:
        r = ec.certify_cached(node, s_rat, out_prefix=pre, rounds=rounds, jobs=jobs, depth=depth,
                              max_w=max_w, time_limit=tl, log=lambda *a: None)
    except Exception as e:
        import traceback
        r = dict(result="ERROR", error=repr(e), tb=traceback.format_exc()[-1500:])
    r["idx"] = idx
    r["wall"] = time.time() - t0
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s_rat", default="969271/250000")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=2, help="verifier workers per node")
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--max_w", type=int, default=48)
    ap.add_argument("--time_limit", type=float, default=180)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(OUT, "g1_debt.json"))
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    l1 = json.load(open(os.path.join(A38, "l1_a38.json")))
    dead = [r["idx"] for r in l1["matrix"] if r["status"] == "dead(T1)"]
    sampled = set(l1["verification"]["full_certification"]["sample"])
    passed = set()
    for rec in l1["verification"]["full_certification"]["records"]:
        if rec.get("result") == "PASS":
            passed.add(int(os.path.basename(rec["node"]).split("_")[1].split(".")[0]))
    debt = [i for i in dead if i not in passed]           # 38 = 44 - 6 certified
    print("dead=%d certified_by_A38=%d debt=%d: %s" % (len(dead), len(passed), len(debt), debt),
          flush=True)
    args = [(i, a.s_rat, a.rounds, a.jobs, a.depth, a.max_w, a.time_limit) for i in debt]
    out = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(one, args):
            out.append(r)
            print("  node %3d %-5s %5.1fs rounds=%d  (%.0fs elapsed)"
                  % (r["idx"], r["result"], r["wall"], len(r.get("rounds", [])), time.time() - t0),
                  flush=True)
            json.dump(dict(when=time.strftime("%FT%T"), debt=debt, records=out,
                           n_pass=sum(1 for x in out if x["result"] == "PASS"),
                           n_fail=sum(1 for x in out if x["result"] == "FAIL"),
                           n_error=sum(1 for x in out if x["result"] == "ERROR"),
                           wall=time.time() - t0), open(a.out, "w"), indent=1)
    n_pass = sum(1 for x in out if x["result"] == "PASS")
    print("G1: %d/%d certified in %.0fs" % (n_pass, len(out), time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
