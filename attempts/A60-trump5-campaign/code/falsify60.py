"""
A60 falsifier probe (G-A59-10): price a stratified sample of the depth-j residue-ladder kill
queue BEFORE committing the campaign.  One record per solve in results/a60_falsify_j<J>.jsonl,
a rolling summary in progress/falsify_j<J>_s<i>.json.
"""
import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import tree60 as T
from tree60 import Sink, kill, basin_box, RES, PROG, logline
from caselp import Box
from pilot59 import init_warm


def sample_queue(scan, n, seed=0):
    """stratified over levels: take the queue items spread across all levels that have any."""
    q = [(L["level"], i, it) for L in scan["levels"] for i, it in enumerate(L.get("queue", []))]
    if not q or n >= len(q):
        return q
    step = len(q) / float(n)
    return [q[int(i * step)] for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", default="sq7")
    ap.add_argument("--scan", default=None)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--cert_time", type=float, default=240.0)
    ap.add_argument("--wall", type=float, default=1e9)
    a = ap.parse_args()
    cond_names = [c for c in a.cond.split(",") if c]
    j = len(cond_names)
    si, sn = map(int, a.shard.split("/"))
    scan = json.load(open(os.path.join(RES, a.scan or ("a60_ladder_j%d_scan.json" % j))))
    budget = scan["budget"]
    cond = ([Box.from_json(d) for d in scan["cond_boxes"]] if scan.get("cond_boxes")
            else [basin_box(n) for n in cond_names])
    sink = Sink("a60_falsify_j%d.jsonl" % j, "falsify_j%d_s%d.log" % (j, si))
    init_warm()
    sel = sample_queue(scan, a.n)
    mine = [x for i, x in enumerate(sel) if i % sn == si]
    prog = os.path.join(PROG, "falsify_j%d_s%d.json" % (j, si))
    st = dict(phase="falsify", j=j, cond=cond_names, budget=budget, shard=a.shard,
              total=len(mine), done=0, passed=0, failed=0, alive=0, lp_s=0.0, cert_s=0.0,
              started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t0 = time.time()

    def flush():
        st["elapsed_s"] = round(time.time() - t0, 1)
        st["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        json.dump(st, open(prog, "w"), indent=1)

    flush()
    logline("A60 falsifier j=%d budget=%d sample=%d shard=%s" % (j, budget, len(mine), a.shard))
    for (level, i, it) in mine:
        tag = "f%d_L%02d_%04d" % (j, level, i)
        if sink.has(tag):
            st["done"] += 1
            flush()
            continue
        if time.time() - t0 > a.wall:
            logline("wall reached; stopping cleanly")
            break
        b = Box.from_json(it["box"])
        rec = kill(sink, tag, b, cond, [], budget,
                   dict(kind="YES-ladder-sample", depth_j=j, level=level, pinguard="ok",
                        a=float(b.core().a), hugs=it["hugs"], k=it["k"], cond=list(cond_names)),
                   lp_time=a.lp_time, cert_time=a.cert_time)
        v = (rec or {}).get("verdict", "")
        st["done"] += 1
        st["passed"] += 1 if v == "PASS" else 0
        st["failed"] += 1 if v.startswith("FAIL") else 0
        st["alive"] += 1 if v.startswith("refused") else 0
        st["lp_s"] = round(st["lp_s"] + (rec or {}).get("lp_s", 0.0), 1)
        st["cert_s"] = round(st["cert_s"] + (rec or {}).get("cert_s", 0.0), 1)
        flush()
    st["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    flush()
    print(json.dumps(st, indent=1))


if __name__ == "__main__":
    main()
