#!/usr/bin/env python3
"""A39: stage-A probe (one exact-certification attempt on the CACHED A38 LP) over EVERY processed
level-1 node, not just the ones A27's rule called dead.  Measures how many level-1 decisions the
convergence rule threw away."""
import json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
A38R = os.path.abspath(os.path.join(HERE, "..", "..", "A38-root-power", "results"))
OUT = os.path.abspath(os.path.join(HERE, "..", "results", "p2a", "l1all"))

def one(idx):
    import earlycert as ec
    t0 = time.time()
    try:
        r = ec.certify_cached(os.path.join(A38R, "l1_nodes", "node_%03d.json" % idx),
                              "969271/250000", out_prefix=os.path.join(OUT, "node_%03d" % idx),
                              rounds=0, jobs=1, depth=56, max_w=32, log=lambda *a: None)
        return dict(idx=idx, result=r["result"], rounds=r["rounds"], wall=time.time() - t0)
    except Exception as e:
        return dict(idx=idx, result="ERROR", error=repr(e), wall=time.time() - t0)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    l1 = json.load(open(os.path.join(A38R, "l1_a38.json")))
    m = {r["idx"]: r for r in l1["matrix"]}
    idxs = [r["idx"] for r in l1["matrix"] if r["status"] in ("undecided", "alive(LP)")]
    print("probing %d non-dead processed level-1 nodes" % len(idxs), flush=True)
    out, t0 = [], time.time()
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    with ProcessPoolExecutor(max_workers=W) as ex:
        for r in ex.map(one, idxs):
            r["a38_status"] = m[r["idx"]]["status"]; r["a38_tau"] = m[r["idx"]]["tau"]
            out.append(r)
            print("  node %3d %-5s %5.1fs (a38 %s tau=%.3f)" % (r["idx"], r["result"], r["wall"],
                  r["a38_status"], r["a38_tau"]), flush=True)
            json.dump(dict(records=out, n=len(idxs),
                           n_pass=sum(1 for x in out if x["result"] == "PASS"),
                           wall=time.time() - t0),
                      open(os.path.join(OUT, "l1all_probe.json"), "w"), indent=1)
    print("done: %d/%d newly certified in %.0fs"
          % (sum(1 for x in out if x["result"] == "PASS"), len(out), time.time() - t0), flush=True)
