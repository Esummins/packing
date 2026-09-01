"""
A53 phase 2: straggler re-solves (warm, long) + certify with witness rounds.

Jobs: the open k6/k5 nodes + the trump5 headline refinement. Sharded like campaign53.
Each job: warm re-solve at time_limit TL (long), overwrite node json (old json kept as
.v1), then certify (rounds 4) if margin. trump5 is re-solved but never certified (it is
provably alive, tau* >= 6); its purpose is a converged eta_residual + tight variety.
"""
import argparse, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import run_skel
from campaign53 import certify

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--jobs", default="k6_22,k6_23,k6_29,k5_03,k5_07,k5_11,k5_12,k5_13,k5_14,k5_16,trump5")
    a = ap.parse_args()
    si, sn = map(int, a.shard.split("/"))
    names = [n for i, n in enumerate(a.jobs.split(",")) if i % sn == si]
    slots_map = json.load(open(os.path.join(BASE, "results", "name_to_slots.json")))
    outdir = os.path.join(BASE, "results", "nodes")
    logf = open(os.path.join(BASE, "logs", f"phase2_shard{si}.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=logf, flush=True)
    summary = os.path.join(BASE, "results", f"phase2_shard{si}.jsonl")
    for name in names:
        node_path = os.path.join(outdir, f"{name}.json")
        v2_marker = node_path + ".v2done"
        if os.path.exists(v2_marker):
            res = json.load(open(node_path))
        else:
            if os.path.exists(node_path):
                shutil.copy(node_path, node_path + ".v1")
            t0 = time.time()
            log(f"[{time.strftime('%H:%M:%S')}] re-solve {name} TL={a.time_limit}")
            res = run_skel.run(name, [tuple(p) for p in slots_map[name]], outdir,
                               time_limit=a.time_limit, max_iter=600,
                               log_path=os.path.join(BASE, "logs", f"{name}_v2.log"),
                               warm_from=node_path + ".v1" if os.path.exists(node_path + ".v1") else None)
            log(f"  tau={res['tau']:.6f} budget={res['budget']} conv={res['converged']} ({time.time()-t0:.0f}s)")
            open(v2_marker, "w").write("ok")
        rec = dict(name=name, k=res["k"], budget=res["budget"], tau=res["tau"],
                   eta_residual=res["tau"] - res["budget"], converged=res["converged"], phase=2)
        if name != "trump5" and res["tau"] * 1.03 < res["budget"]:
            cp = os.path.join(BASE, "certs_wip", f"{name}.json")
            if os.path.exists(cp + ".PASS"):
                rec["cert"] = "PASS"
            else:
                ok, dt = certify(name, node_path, log)
                rec["cert"] = "PASS" if ok else "FAIL"
                rec["cert_time"] = dt
                if ok:
                    open(cp + ".PASS", "w").write("ok")
        else:
            rec["cert"] = "n/a" if name == "trump5" else "not_attempted (no margin)"
        with open(summary, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
    print("phase2 shard done", flush=True)

if __name__ == "__main__":
    main()
