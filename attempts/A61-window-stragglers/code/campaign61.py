#!/usr/bin/env python3
"""
campaign61.py -- the A61 queue driver.  Runs resolve61.py over the 12 s0-only strata of
G-A56-1 with a hard cap of --heavy concurrent heavy processes, a resumable progress file
and ONE consolidated exit.  Priority order = descending predicted slack0 (the A56 resolve
records extrapolated back to the baseline shrink with dtau/deps ~ 1.4e2), so the cheapest
conversions land first and a truncated campaign is still maximally informative.

Usage: python campaign61.py [--heavy 2] [--only k5_05,k6_21] [--restart]
"""
import os

# A57 T18: single-thread BLAS per worker (see resolve61.py's header).  Set here too so that
# every child inherits it even if invoked through a shell that drops the parent's environment.
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse                                                       # noqa: E402
import json                                                           # noqa: E402
import subprocess                                                     # noqa: E402
import sys                                                            # noqa: E402
import time                                                           # noqa: E402
from concurrent.futures import ThreadPoolExecutor, as_completed       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
A61 = os.path.abspath(os.path.join(HERE, ".."))
RESULTS = os.path.join(A61, "results")
LOGS = os.path.join(A61, "logs")
PROG = os.path.join(RESULTS, "campaign61_progress.json")

# name, predicted slack0, note
QUEUE = [
    ("k5_05", 1.40, "A56 eps 0.002948 tau 5.000; certify PASSed, 4D open -> L1 leak suspect"),
    ("k5_17", 0.85, "A56 eps 0.001846 tau 5.400"),
    ("k5_10", 0.54, "A56 eps 0.001 (sub-threshold) tau 5.588"),
    ("k6_21", 0.50, "A56 eps 0.001286 (sub-threshold) tau 4.600; A61 probe: tau0 = 4.500"),
    ("k6_20", 0.50, "A56 eps 0.001286 (sub-threshold) tau 4.667"),
    ("k6_29", 0.48, "A56 eps 0.0015 tau 4.718"),
    ("k6_27", 0.46, "A56 eps 0.001 (sub-threshold) tau 4.671"),
    ("k5_02", 0.46, "A56: LP infeasible at 0.003 (tau -> budget); thinnest row in the library"),
    ("k5_03", 0.16, "never resolved in A56; column pool only 276"),
    ("k5_12", 0.16, "never resolved in A56; column pool only 85"),
    ("k5_14", 0.14, "never resolved in A56; column pool only 218"),
    ("k5_13", 0.04, "never resolved in A56; 106-atom cert, thinnest of the four"),
]


def load():
    if os.path.exists(PROG):
        try:
            return json.load(open(PROG))
        except Exception:
            pass
    return {"rows": {}, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}


def one(name, pred, note, a, st):
    t0 = time.time()
    cmd = [sys.executable, os.path.join(HERE, "resolve61.py"), "--name", name,
           "--eps_geo", str(a.eps_geo), "--gate", str(a.gate),
           "--lp_time", str(a.lp_time), "--lp_time_b", str(a.lp_time_b),
           "--cert_time", str(a.cert_time), "--cert_rounds", str(a.cert_rounds),
           "--depth", str(a.depth), "--jobs", str(a.jobs),
           "--param_timeout", str(a.param_timeout),
           "--max_atoms", str(a.max_atoms), "--max_cols_add", str(a.max_cols_add)]
    lp = os.path.join(LOGS, f"campaign_{name}.out")
    env = dict(os.environ)
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = "1"
    with open(lp, "w", encoding="utf-8") as fh:
        p = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, text=True, env=env)
    rec = {}
    rp = os.path.join(RESULTS, f"resolve61_{name}.json")
    if os.path.exists(rp):
        try:
            rec = json.load(open(rp))
        except Exception:
            rec = {}
    row = {"name": name, "predicted_slack0": pred, "note": note, "rc": p.returncode,
           "wall_s": round(time.time() - t0, 1),
           "verdict": rec.get("verdict"),
           "slack0": (rec.get("stageA") or {}).get("slack0"),
           "tau0": (rec.get("stageA") or {}).get("tau0"),
           "tau_eps": (rec.get("stageB") or {}).get("tau"),
           "certify": rec.get("certify"),
           "cert_margin": (rec.get("new_cert") or {}).get("margin"),
           "anchoring": rec.get("anchoring"),
           "record": rp}
    return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--heavy", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--eps_geo", type=float, default=0.003)
    ap.add_argument("--gate", type=float, default=0.5)
    ap.add_argument("--lp_time", type=float, default=1200)
    ap.add_argument("--lp_time_b", type=float, default=900)
    ap.add_argument("--cert_time", type=float, default=300)
    ap.add_argument("--cert_rounds", type=int, default=3)
    ap.add_argument("--depth", type=int, default=48)
    ap.add_argument("--param_timeout", type=int, default=900)
    ap.add_argument("--max_atoms", type=int, default=3000)
    ap.add_argument("--max_cols_add", type=int, default=800)
    ap.add_argument("--only", default=None)
    ap.add_argument("--restart", action="store_true")
    a = ap.parse_args(argv)

    st = {"rows": {}, "started": time.strftime("%Y-%m-%dT%H:%M:%S")} if a.restart else load()
    todo = list(QUEUE)
    if a.only:
        keep = set(a.only.split(","))
        todo = [q for q in todo if q[0] in keep]
    # resume off the per-name RECORD files, not just the progress file: a killed driver may
    # have finished strata whose rows never got written (results land as they complete).
    for (n, p, nt) in list(QUEUE):
        rp = os.path.join(RESULTS, f"resolve61_{n}.json")
        if n in st["rows"] or not os.path.exists(rp):
            continue
        try:
            rec = json.load(open(rp))
        except Exception:
            continue
        if rec.get("verdict"):
            st["rows"][n] = {"name": n, "predicted_slack0": p, "note": nt, "rc": None,
                             "wall_s": rec.get("total_seconds"),
                             "verdict": rec.get("verdict"),
                             "slack0": (rec.get("stageA") or {}).get("slack0"),
                             "tau0": (rec.get("stageA") or {}).get("tau0"),
                             "tau_eps": (rec.get("stageB") or {}).get("tau"),
                             "certify": rec.get("certify"),
                             "cert_margin": (rec.get("new_cert") or {}).get("margin"),
                             "anchoring": rec.get("anchoring"), "record": rp,
                             "recovered": True}
    json.dump(st, open(PROG, "w"), indent=1)
    todo = [q for q in todo if q[0] not in st["rows"]]
    print(f"campaign61: {len(todo)} strata, {a.heavy} concurrent, gate {a.gate}, "
          f"eps_geo {a.eps_geo}", flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=a.heavy) as ex:
        futs = {ex.submit(one, n, p, nt, a, st): n for (n, p, nt) in todo}
        for f in as_completed(futs):
            nm = futs[f]
            row = f.result()
            st["rows"][nm] = row
            st["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            json.dump(st, open(PROG, "w"), indent=1)
            done += 1
            print(f"  [{done}/{len(futs)}] {nm:7s} rc={row['rc']} slack0="
                  f"{row['slack0']} verdict={row['verdict']} ({row['wall_s']}s)", flush=True)
    summ = {}
    for r in st["rows"].values():
        v = (r.get("verdict") or "unknown").split("(")[0].strip()
        summ[v] = summ.get(v, 0) + 1
    st["summary"] = summ
    json.dump(st, open(PROG, "w"), indent=1)
    print("campaign61 summary:", json.dumps(summ), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
