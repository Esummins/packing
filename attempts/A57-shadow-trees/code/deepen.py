"""
A57 depth 2: refine the YES children that resisted level 1.

A level-1 child C = pins + box B at budget 11-k-1 that converges to tau >= budget is not a
counterexample to anything -- it is a box that is too coarse.  Replacing B by a closed cover
{B_1 .. B_m} of B refines the SAME disjunction:

    "some square has (centre, theta) in B"  ==  OR_j "some square has (centre, theta) in B_j"

so C is empty as soon as every C_j = pins + B_j is, and every C_j carries the SAME budget as C
(no further budget is spent -- this is a refinement, not a new branch, which is why depth 2 is
affordable where a second zone would not be).  Splitting also RAISES the core half-side
a = (1/2 - hd)/(1 + (t1-t0)): three bisections take a from 0.3566 to about 0.42.

Each B_j is re-checked by `pinguard.classify` (a sub-box can be contradictory even when its
parent was not -- another free kill) and by `substrat.trump_realizes`.  Depth is capped at 2
levels total, per the A57 brief: `--levels 1` = the 8 boxes of one round of bisection.

Usage:
    python code/deepen.py --key k5_16_interior_L1     # every ALIVE-at-LP / cert-FAIL record
    python code/deepen.py --key k5_16_interior_L1 --id k5_16_interior_Y0017
"""
import argparse, glob, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
import caselp
from caselp import Box, Hyp, solve_node
from run_skel import S0F
from substrat import trump_realizes
from pinguard import classify
from warm57 import merged_warm

S_RAT = "969271/250000"

# T19: every extra Python process costs ~628 MB of COMMIT before it does any work (measured:
# bare `python -c "import numpy"` = 27 MB working set, 628 MB commit).  verify_case.py spawns an
# mp.Pool of --jobs workers ON TOP of itself and its parent, so a certify at --jobs 2 was four
# processes ~= 2.5 GB of commit in baselines alone.  At --jobs 1 verify_case takes its in-process
# branch and spawns nothing.  The machine's binding constraint is the commit limit (61 GB), not
# RAM, and A60 lost a shard to a 38 MiB allocation while A57 held reservations.
VERIFY_JOBS_CAP = 1


def split_n(box, levels):
    out = [box]
    for _ in range(levels):
        out = [h for b in out for h in b.split()]
    return out


def defer(kid_id, exc, log, base, key, stats):
    """T19 (A60's tree60.defer, adopted).  A transient COMMIT spike must not destroy the queue:
    record the node, sleep, continue -- and do NOT append a summary record, so the node stays
    absent from `done` and is retried next pass.  Deferring only postpones work, never asserts a
    verdict."""
    import json as _json, time as _time, gc as _gc
    _gc.collect()
    p = os.path.join(base, "results", f"deferred_{key}.jsonl")
    try:
        with open(p, "a") as f:
            f.write(_json.dumps(dict(id=kid_id, error=repr(exc)[:200],
                                     when=_time.strftime("%Y-%m-%d %H:%M:%S"))) + chr(10))
    except Exception:
        pass
    stats["deferred"] = stats.get("deferred", 0) + 1
    log(f"    DEFERRED {kid_id}: {repr(exc)[:120]} -- sleeping 30 s, node left NOT done")
    _time.sleep(30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True, help="e.g. k5_16_interior_L1")
    ap.add_argument("--id", default=None,
                    help="one child id (default: every ALIVE-at-LP and cert-FAIL record)")
    ap.add_argument("--levels", type=int, default=3, help="bisections (3 -> 8 sub-boxes)")
    ap.add_argument("--time_limit", type=float, default=240)
    ap.add_argument("--cert_time", type=float, default=240)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.40)
    ap.add_argument("--wall_seconds", type=float, default=10 ** 9)
    a = ap.parse_args()

    name = a.key.split("_interior")[0].split("_side")[0].split("_corner")[0]
    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[name]]
    pins = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    alive = []
    for p in glob.glob(os.path.join(BASE, "results", f"tree_{a.key}_s*.jsonl")):
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            cert = str(r.get("cert", ""))
            # everything that level 1 could not kill and that is not a logic/canary/unsound
            # verdict: ALIVE-at-LP, and FAIL (incl. certify.py rc=3, "total >= budget")
            eligible = (cert.startswith("ALIVE") or cert.startswith("FAIL")) and r.get("box")
            if eligible and (a.id is None or r["id"] == a.id):
                alive.append(r)
    if not alive:
        print(json.dumps(dict(key=a.key, alive=0, note="nothing to deepen"))); return

    outdir = os.path.join(BASE, "results", "tree", a.key + "_D2")
    certdir = os.path.join(BASE, "certs", "tree", a.key + "_D2")
    os.makedirs(outdir, exist_ok=True); os.makedirs(certdir, exist_ok=True)
    summary = os.path.join(BASE, "results", f"tree_{a.key}_D2.jsonl")
    progress = os.path.join(BASE, "progress", f"{a.key}_D2.json")
    logf = open(os.path.join(BASE, "logs", f"{a.key}_D2.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=logf, flush=True)
    done = set()
    if os.path.exists(summary):
        for line in open(summary):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
    W, _ = merged_warm(name)
    pool = list(W["atoms"])
    budget = 11 - len(slots) - 1
    stats = dict(key=a.key + "_D2", parents=len(alive), total=0, done=0, killed=0,
                 killed_logic=0, alive_lp=0, cert_fail=0, started=time.strftime("%Y-%m-%d %H:%M:%S"))
    t_start = time.time()
    log(f"=== A57 deepen {a.key} {time.strftime('%Y-%m-%d %H:%M:%S')} parents={len(alive)} "
        f"levels={a.levels} budget={budget}")

    for par in alive:
        B = Box.from_json(par["box"])
        subs = [b for b in split_n(B, a.levels) if not b.vacuous(S0F)]
        stats["total"] += len(subs)
        log(f"  parent {par['id']} tau={par.get('tau')} -> {len(subs)} sub-boxes")
        for j, b in enumerate(subs):
            cid = f"{par['id']}_D{j:02d}"
            if cid in done:
                continue
            if time.time() - t_start > a.wall_seconds:
                log("    wall_seconds reached; stopping cleanly"); break
            c = b.core()
            rec = dict(id=cid, parent=par["id"], kind="YES-D2", budget=budget,
                       box=b.to_json(), a=(float(c.a) if c else None))
            st, info = classify(b, pins, slots)
            rec["pin"] = st; rec["pin_info"] = info
            hyp = Hyp(pins + [b], [])
            rec["trump_realizes"] = trump_realizes(hyp, slots)
            if st == "contradictory":
                rec["cert"] = "KILL-BY-LOGIC (core meets pin core)"
                stats["killed"] += 1; stats["killed_logic"] += 1
            elif st == "parent":
                rec["cert"] = "UNSOUND-AT-REDUCED-BUDGET (box realises a pin)"
            elif rec["trump_realizes"]:
                rec["cert"] = "CANARY (Trump-realizable: never certified)"
            else:
                npth = os.path.join(outdir, cid + ".json")
                t0 = time.time()
                try:
                    if os.path.exists(npth):
                        res = json.load(open(npth))
                    else:
                        res = solve_node(S0F, hyp, budget, sym_kind="C1",
                                         warm=dict(atoms=pool, rows=[]),
                                         time_limit=a.time_limit, max_iter=900, out=None, log=log,
                                         prune=0, prune_cols=3, col_stop_iter=10 ** 6,
                                         col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000,
                                         fine_slack=0.05, alternate=True)
                        json.dump(res, open(npth, "w"))
                except MemoryError as e:
                    defer(cid, e, log, BASE, a.key + "_D2", stats)
                    continue
                rec.update(tau=res["tau"], eta=res["tau"] - budget, converged=res["converged"],
                           minmass=res["minmass"], maxcov=res["maxcov"],
                           lp_seconds=round(time.time() - t0, 1))
                if res["tau"] >= budget:
                    rec["cert"] = "ALIVE-at-LP at depth 2"; stats["alive_lp"] += 1
                else:
                    cert_out = os.path.join(certdir, cid + ".json")
                    cmd = [sys.executable, os.path.join(HERE, "certify.py"), npth, "--s_rat", S_RAT,
                           "--rounds", str(a.rounds), "--jobs", str(min(a.jobs, VERIFY_JOBS_CAP)), "--depth", str(a.depth),
                           "--time_limit", str(a.cert_time), "--out", cert_out, "--scale", "0",
                           "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "64", "--loop_cols"]
                    t1 = time.time()
                    p = subprocess.run(cmd, capture_output=True, text=True)
                    log(p.stdout[-2500:])
                    ok = (p.returncode == 0)
                    rec["cert"] = "PASS" if ok else f"FAIL(rc={p.returncode})"
                    rec["cert_seconds"] = round(time.time() - t1, 1)
                    if ok:
                        open(cert_out + ".PASS", "w").write("ok")
                        stats["killed"] += 1
                    else:
                        stats["cert_fail"] += 1
            stats["done"] += 1
            log("    " + json.dumps(rec))
            with open(summary, "a") as f:
                f.write(json.dumps(rec) + "\n")
            stats["elapsed_s"] = round(time.time() - t_start, 1)
            stats["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            json.dump(stats, open(progress, "w"), indent=1)
    stats["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(stats, open(progress, "w"), indent=1)
    print(json.dumps(stats), flush=True)


if __name__ == "__main__":
    main()
