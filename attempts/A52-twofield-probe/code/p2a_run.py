#!/usr/bin/env python3
"""
A39 P2a driver -- certification-in-the-loop calibration on A38's samples.

Stage A (probe): ONE exact-certification attempt on each node's CACHED A38 LP result.  Marginal
cost = one verifier run.  This is the cheapest possible instance of the A39 rule: it asks whether
the LP A38 already paid for was ALREADY a certificate, which A38 never asked because A27's
classification rule refused to look at an unconverged LP.

Stage B (loop): every node still undecided is re-solved warm-started from A38's cached checkpoint
with the certification hook firing after EVERY row-generation round; verifier witnesses become LP
rows.  time_limit caps the node.

Stage C (cold): a small stratum run FROM SCRATCH under the A39 rule, to measure the honest
from-scratch cost/node (no A38 warm start), which is what the extrapolation frame needs.

Populations: --pop l2  (A38's depth-2 stratified sample, the 0/49-decided baseline)
             --pop l1u (level-1 undecided nodes)
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
A38R = os.path.abspath(os.path.join(HERE, "..", "..", "A38-root-power", "results"))
OUT = os.path.abspath(os.path.join(HERE, "..", "results", "p2a"))
S0 = "969271/250000"


# ------------------------------------------------------------------------------- populations
def pop_l2():
    d = json.load(open(os.path.join(A38R, "l2_a38.json")))
    out = []
    for r in d["records"]:
        if r.get("status") == "notrun":
            continue
        cid = r["cid"]
        nj = os.path.join(A38R, "l2_nodes", cid + ".json")
        stj = os.path.join(A38R, "l2_nodes", cid + "_state.json")
        if not os.path.exists(nj):
            continue
        out.append(dict(cid=cid, box=r["box"], budget=r["budget"], node=nj,
                        state=(stj if os.path.exists(stj) else None),
                        a38_status=r["status"], a38_tau=r["tau"], a38_seconds=r["seconds"],
                        stratum=r.get("stratum"), depth=2))
    return out


def pop_l1u(n=10):
    d = json.load(open(os.path.join(A38R, "l1_a38.json")))
    und = [r for r in d["matrix"] if r["status"] == "undecided"]
    und.sort(key=lambda r: r["idx"])
    step = max(1, len(und) // n)
    pick = und[::step][:n]
    out = []
    for r in pick:
        nj = os.path.join(A38R, "l1_nodes", "node_%03d.json" % r["idx"])
        stj = os.path.join(A38R, "l1_nodes", "node_%03d_state.json" % r["idx"])
        if not os.path.exists(nj):
            continue
        out.append(dict(cid="l1_%03d" % r["idx"], box=r["box"], budget=10, node=nj,
                        state=(stj if os.path.exists(stj) else None),
                        a38_status=r["status"], a38_tau=r["tau"], a38_seconds=r["seconds"],
                        stratum="l1_undecided", depth=1))
    return out


# ------------------------------------------------------------------------------------- stages
def stage_a(job):
    item, jobs, depth, max_w, outdir = job
    import earlycert as ec
    pre = os.path.join(outdir, item["cid"] + "_A")
    t0 = time.time()
    try:
        r = ec.certify_cached(item["node"], S0, out_prefix=pre, rounds=0, jobs=jobs, depth=depth,
                              max_w=max_w, log=lambda *a: None)
        res = dict(item, stage="A", result=r["result"], rounds=r["rounds"],
                   t_marginal=time.time() - t0)
    except Exception as e:
        import traceback
        res = dict(item, stage="A", result="ERROR", error=repr(e),
                   tb=traceback.format_exc()[-800:], t_marginal=time.time() - t0)
    return res


def stage_b(job):
    item, jobs, depth, max_w, outdir, time_limit, cold = job
    import earlycert as ec
    from caselp import Box
    pre = os.path.join(outdir, item["cid"] + ("_C" if cold else "_B"))
    b = item["box"]
    box = Box(b["x0"], b["x1"], b["y0"], b["y1"], b["th0"], b["th1"])
    warm = None
    if not cold and item.get("state"):
        st = json.load(open(item["state"]))
        warm = dict(atoms=[tuple(o) for o in st["orbits"]], rows=[tuple(r) for r in st["rows"]])
    t0 = time.time()
    try:
        rec = ec.solve_node_early(S0, [box], item["budget"], time_limit=time_limit,
                                  out=pre + ".rec.json", log=lambda *a: None, warm=warm,
                                  jobs=jobs, depth=depth, max_w=max_w, every=1, first=0,
                                  tag=item["cid"], eps_geo=1e-4)
        res = dict(item, stage=("C" if cold else "B"), result=rec["status"],
                   decided=rec.get("decided"), certified=rec.get("certified"),
                   tau=rec.get("tau"), status_a27=rec.get("status_a27"),
                   n_cert_attempts=rec.get("n_cert_attempts"),
                   cert_verify_s=rec.get("cert_verify_s"),
                   rows_fed_back=rec.get("rows_fed_back"),
                   t_decide=rec.get("t_decide"), t_marginal=time.time() - t0,
                   attempts=rec.get("cert_attempts"))
    except Exception as e:
        import traceback
        res = dict(item, stage=("C" if cold else "B"), result="ERROR", error=repr(e),
                   tb=traceback.format_exc()[-800:], t_marginal=time.time() - t0)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", default="l2", choices=["l2", "l1u"])
    ap.add_argument("--stage", default="AB", help="subset of ABC")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--max_w", type=int, default=48)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--time_limit", type=float, default=300)
    ap.add_argument("--n_cold", type=int, default=6)
    ap.add_argument("--n", type=int, default=10, help="l1u sample size")
    ap.add_argument("--only", default=None, help="comma list of cids to run")
    ap.add_argument("--suffix", default="", help="output subdir suffix (separate ledger)")
    a = ap.parse_args()
    outdir = os.path.join(OUT, a.pop + a.suffix)
    os.makedirs(outdir, exist_ok=True)
    items = pop_l2() if a.pop == "l2" else pop_l1u(a.n)
    if a.only:
        keep = set(a.only.split(","))
        items = [it for it in items if it["cid"] in keep]
    print("population %s: %d nodes" % (a.pop, len(items)), flush=True)
    ledger = dict(when=time.strftime("%FT%T"), pop=a.pop, n=len(items),
                  time_limit=a.time_limit, depth=a.depth, max_w=a.max_w, A=[], B=[], C=[])
    lp = os.path.join(outdir, "ledger.json")
    t0 = time.time()

    todo = items
    if "A" not in a.stage and os.path.exists(lp):        # resume: reuse a previous stage A
        prev = json.load(open(lp))
        ledger["A"] = prev.get("A", [])
        done_ok = {r["cid"] for r in ledger["A"] if r.get("result") == "PASS"}
        todo = [it for it in items if it["cid"] not in done_ok]
        print("resumed stage A from ledger: %d certified, %d to do" % (len(done_ok), len(todo)),
              flush=True)
    if "A" in a.stage:
        jobs = [(it, a.jobs, a.depth, a.max_w, outdir) for it in items]
        done = []
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for r in ex.map(stage_a, jobs):
                done.append(r)
                print("  A %-16s %-5s %5.1fs" % (r["cid"], r["result"], r["t_marginal"]), flush=True)
                ledger["A"] = done
                json.dump(ledger, open(lp, "w"), indent=1)
        todo = [r for r in done if r["result"] != "PASS"]
        print("stage A: %d/%d certified from the CACHED LP (%.0fs)"
              % (len(done) - len(todo), len(done), time.time() - t0), flush=True)

    if "B" in a.stage and todo:
        jobs = [(it, a.jobs, a.depth, a.max_w, outdir, a.time_limit, False) for it in todo]
        done = []
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for r in ex.map(stage_b, jobs):
                done.append(r)
                print("  B %-16s %-16s %6.1fs attempts=%s fed=%s"
                      % (r["cid"], r["result"], r["t_marginal"], r.get("n_cert_attempts"),
                         r.get("rows_fed_back")), flush=True)
                ledger["B"] = done
                json.dump(ledger, open(lp, "w"), indent=1)

    if "C" in a.stage:
        cold = items[:a.n_cold]
        jobs = [(it, a.jobs, a.depth, a.max_w, outdir, a.time_limit, True) for it in cold]
        done = []
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for r in ex.map(stage_b, jobs):
                done.append(r)
                print("  C %-16s %-16s %6.1fs attempts=%s"
                      % (r["cid"], r["result"], r["t_marginal"], r.get("n_cert_attempts")),
                      flush=True)
                ledger["C"] = done
                json.dump(ledger, open(lp, "w"), indent=1)

    ledger["wall"] = time.time() - t0
    json.dump(ledger, open(lp, "w"), indent=1)
    print("done %.0fs -> %s" % (time.time() - t0, lp), flush=True)


if __name__ == "__main__":
    main()
