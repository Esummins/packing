"""
A53 leg (b) campaign: residual guard LPs over skeleton classes, cheap-cert in the loop.

Tier 1 (PI): all k = 6 Young classes (killing the pin-hypothesis of every k = 6 class
caps every k >= 6 stratum, since each k >= 7 Young tuple contains a k = 6 sub-tuple).
Tier 2: the 21 non-Trump k = 5 classes.

Sharded: run two instances with --shard 0/2 and --shard 1/2 (each is one heavy process;
machine also carries A50/A51/A52). Checkpointed: existing node jsons are skipped.
A39 cheap-cert rule: attempt exact certification (certify.py -> verify_case.py, exact
rational B&B) as soon as the LP's tau leaves margin: tau * 1.03 < budget.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import run_skel

S_RAT = "969271/250000"


def job_list():
    d = json.load(open(os.path.join(BASE, "results", "skeletons_young.json")))
    jobs = []
    i6 = i5 = 0
    for cl in d["classes"]:
        if cl["k"] == 6:
            jobs.append((f"k6_{i6:02d}", cl["slots_float"])); i6 += 1
    for cl in d["classes"]:
        if cl["k"] == 5 and not cl["is_trump"]:
            jobs.append((f"k5_{i5:02d}", cl["slots_float"])); i5 += 1
    return jobs


def certify(name, node_path, log):
    out = os.path.join(BASE, "certs_wip", f"{name}.json")
    cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_path, "--s_rat", S_RAT,
           "--rounds", "3", "--jobs", "2", "--depth", "56", "--time_limit", "240",
           "--out", out]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=2400)
    ok = "PASS" in (p.stdout + p.stderr)
    log(f"  cert {name}: {'PASS' if ok else 'FAIL'} ({time.time()-t0:.0f}s)")
    return ok, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1", help="i/n")
    ap.add_argument("--time_limit", type=float, default=240)
    ap.add_argument("--only_k", type=int, default=None)
    a = ap.parse_args()
    si, sn = map(int, a.shard.split("/"))
    jobs = job_list()
    if a.only_k:
        jobs = [j for j in jobs if j[0].startswith(f"k{a.only_k}")]
    jobs = [j for i, j in enumerate(jobs) if i % sn == si]
    outdir = os.path.join(BASE, "results", "nodes")
    os.makedirs(outdir, exist_ok=True)
    summary_path = os.path.join(BASE, "results", f"campaign_shard{si}.jsonl")
    logf = open(os.path.join(BASE, "logs", f"campaign_shard{si}.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=logf, flush=True)
    for name, slots in jobs:
        node_path = os.path.join(outdir, f"{name}.json")
        if os.path.exists(node_path):
            res = json.load(open(node_path))
        else:
            t0 = time.time()
            log(f"[{time.strftime('%H:%M:%S')}] LP {name} k={len(slots)} budget={11-len(slots)}")
            res = run_skel.run(name, [tuple(p) for p in slots], outdir,
                               time_limit=a.time_limit, max_iter=300,
                               log_path=os.path.join(BASE, "logs", f"{name}.log"))
            log(f"  tau={res['tau']:.6f} budget={res['budget']} conv={res['converged']} ({time.time()-t0:.0f}s)")
        rec = dict(name=name, k=res["k"], budget=res["budget"], tau=res["tau"],
                   eta_residual=res["tau"] - res["budget"], converged=res["converged"])
        if res["tau"] * 1.03 < res["budget"]:
            cert_path = os.path.join(BASE, "certs_wip", f"{name}.json")
            if os.path.exists(cert_path + ".PASS"):
                rec["cert"] = "PASS"
            else:
                ok, dt = certify(name, node_path, log)
                rec["cert"] = "PASS" if ok else "FAIL"
                rec["cert_time"] = dt
                if ok:
                    open(cert_path + ".PASS", "w").write("ok")
        else:
            rec["cert"] = "not_attempted (no margin)"
        with open(summary_path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)   # stdout heartbeat (keeps background task alive)
    log("shard done")
    print("shard done", flush=True)


if __name__ == "__main__":
    main()
