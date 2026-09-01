#!/usr/bin/env python3
"""
final_sweep.py -- A56 last compute: run resolve_margin.py over every remaining OPEN row with a
per-certificate robustness margin, checkpointing the scoreboard after each row.

eps_geo SCHEDULE (the validated budget-slack rule).  Measured cost of the row shrink:
eps_geo = 0.003 raised tau by 0.5 on k6_28/k6_32 and by 0.337 on k5_02, i.e. d(tau)/d(eps) is of
order 1.1e2-1.7e2.  So a certificate can afford eps_geo only in proportion to its LP slack
budget - tau_0, and we spend at most about a third of that slack:

    eps_geo(cert) = clamp( 0.003 * min(1, (budget - tau_0) / 1.0), 0.0002, 0.003 )

with tau_0 read from the A53 node json (read-only).  Rows are attempted in ascending order of the
A53 row count, which is the best available proxy for LP cost, so the cheap ones land first.

Per row: solve_node (prune off, columns on, --time_limit fair share) -> A54 certify.py at the
largest affordable weight scale -> make_param (gap anchoring) -> verify_param depth 48 over the
whole window -> canary C2 with the unmodified A53 verify_case.py.  A row whose LP does not
converge inside its fair share is left OPEN with its witness data and the sweep moves on.

Usage:  python final_sweep.py [--budget 12000] [--time_limit 420] [--param_timeout 600]
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sweep as SW                                              # noqa: E402
import close_a56                                                # noqa: E402

A53 = os.path.join(SW.ATTEMPTS, "A53-simple-strata")


def schedule():
    sb = json.load(open(os.path.join(SW.RESULTS, "scoreboard.json")))
    out = []
    for n, r in sb["rows"].items():
        if r["result"] not in ("OPEN", "TIMEOUT"):
            continue
        p = os.path.join(A53, "results", "nodes", f"{n}.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        tau = d["tau"]
        budget = 11 - r["k"]
        slack = budget - tau
        eps = min(0.003, max(0.0002, 0.003 * min(1.0, slack / 1.0)))
        out.append({"name": n, "k": r["k"], "budget": budget, "tau": tau,
                    "slack": round(slack, 6), "eps_geo": round(eps, 6),
                    "a53_rows": len(d.get("rows_all", []))})
    out.sort(key=lambda z: z["a53_rows"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budget", type=float, default=12000, help="total seconds for the sweep")
    ap.add_argument("--time_limit", type=float, default=420, help="LP fair share per row")
    ap.add_argument("--cert_time", type=float, default=300)
    ap.add_argument("--param_timeout", type=int, default=600)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--only", default=None)
    a = ap.parse_args(argv)

    sch = schedule()
    if a.only:
        keep = set(a.only.split(","))
        sch = [z for z in sch if z["name"] in keep]
    json.dump(sch, open(os.path.join(SW.RESULTS, "final_sweep_schedule.json"), "w"), indent=1)
    print(f"final sweep: {len(sch)} rows, budget {a.budget/3600:.1f} h, "
          f"LP fair share {a.time_limit}s")
    for z in sch:
        print(f"  {z['name']:7s} k{z['k']} tau={z['tau']:.4f} slack={z['slack']:.4f} "
              f"eps_geo={z['eps_geo']:.6f} a53rows={z['a53_rows']}")

    t0 = time.time()
    done = []
    for z in sch:
        if time.time() - t0 > a.budget:
            print(f"STOP: sweep budget spent; {len(sch)-len(done)} rows remain", flush=True)
            break
        n = z["name"]
        cmd = [sys.executable, os.path.join(HERE, "resolve_margin.py"), "--name", n,
               "--eps_geo", str(z["eps_geo"]), "--time_limit", str(a.time_limit),
               "--cert_time", str(a.cert_time), "--depth", str(a.depth),
               "--param_timeout", str(a.param_timeout)]
        t1 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t1
        rp = os.path.join(SW.RESULTS, f"resolve_{n}.json")
        verdict = "no record"
        if os.path.exists(rp):
            try:
                verdict = json.load(open(rp)).get("verdict", "?")
            except Exception:
                pass
        done.append(n)
        close_a56.main()                                        # checkpoint after every row
        print(f"  [{len(done)}/{len(sch)}] {n:7s} eps={z['eps_geo']:.6f} -> {verdict}  "
              f"{dt:.0f}s  (elapsed {(time.time()-t0)/60:.1f} min)", flush=True)
    sb = json.load(open(os.path.join(SW.RESULTS, "scoreboard.json")))
    print(json.dumps(sb["summary"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
