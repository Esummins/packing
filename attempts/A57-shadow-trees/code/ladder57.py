"""
A57 rung-1/2 extension pass for ONE shadow stratum, re-based on A57 (A54 ladder.py + the
A55/k3_ext E3 lever: the warm start is the UNION of every column this lab ever generated for
the node, checkpoints of interrupted passes included, and the pass writes its own checkpoint so
an interruption loses nothing).  Row pruning OFF (tau monotone up), columns pruned only.
A53/A54/A55/A56 artefacts are read, never written.  trump5 is never a target.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
from caselp import solve_node
from run_skel import hyp_from_slots, S0F
from warm57 import merged_warm

S_RAT = "969271/250000"

# T19/T27: cap the verifier fan-out.  verify_case.py spawns an mp.Pool of --jobs workers on top of
# itself and its parent, and every Python process costs ~628 MB of COMMIT before it does any work.
# These entry points are not currently in the campaign, but an uncapped --jobs here is exactly how
# a 3-worker certify reaches 5-9 GB of commit (measured on A61's copies, which lack this cap).
VERIFY_JOBS_CAP = 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--time_limit", type=float, default=3000)
    ap.add_argument("--max_iter", type=int, default=4000)
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.40)
    ap.add_argument("--cert_time", type=float, default=600)
    ap.add_argument("--tag", default="e1")
    ap.add_argument("--max_cols_add", type=int, default=350)
    ap.add_argument("--prune_cols", type=int, default=3)
    ap.add_argument("--col_stop_cov", type=float, default=1.002)
    ap.add_argument("--cert_only", action="store_true")
    ap.add_argument("--no_cert", action="store_true")
    a = ap.parse_args()

    if a.name == "trump5":
        print("REFUSED: trump5 is the canary and is never certified"); sys.exit(5)
    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
    k = len(slots); budget = 11 - k
    hyp = hyp_from_slots(slots)
    for d in ("results/nodes", "certs", "logs", "results"):
        os.makedirs(os.path.join(BASE, d), exist_ok=True)
    lf = open(os.path.join(BASE, "logs", f"{a.name}_{a.tag}.log"), "a", buffering=1)
    def log(*x):
        print(*x, file=lf, flush=True)
    node_out = os.path.join(BASE, "results", "nodes", f"{a.name}.json")
    log(f"=== A57 ladder {a.name} {a.tag} {time.strftime('%Y-%m-%d %H:%M:%S')} k={k} budget={budget}")
    t0 = time.time()
    if a.cert_only:
        res = json.load(open(node_out)); dt = 0.0
    else:
        warm, used = merged_warm(a.name)
        log(f"    merged warm: {len(warm['atoms'])} atoms, {len(warm['rows'])} rows from {used}")
        if os.path.exists(node_out):
            os.replace(node_out, os.path.join(BASE, "results", "nodes",
                                              f"{a.name}.prev{int(time.time())}.json"))
        res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.time_limit,
                         max_iter=a.max_iter, out=None, log=log,
                         prune=0, prune_cols=a.prune_cols,
                         col_stop_iter=10 ** 6, col_stop_cov=a.col_stop_cov,
                         max_cols_add=a.max_cols_add, max_rows_add=2500,
                         fine_slack=99.0, alternate=True,
                         checkpoint=os.path.join(BASE, "results", "nodes", f"{a.name}_state.json"))
        res["skeleton_name"] = a.name
        res["skeleton_slots"] = [[x, y] for (x, y) in slots]
        res["k"] = k
        json.dump(res, open(node_out, "w"))
        dt = time.time() - t0
        log(f"    rung1 tau={res['tau']:.6f} budget={budget} conv={res['converged']} "
            f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} ({dt:.0f}s)")
    rec = dict(name=a.name, k=k, budget=budget, tau=res["tau"], converged=res["converged"],
               minmass=res["minmass"], maxcov=res["maxcov"], eta=res["tau"] - budget,
               lp_seconds=round(dt, 1), tag=a.tag, n_rows=res["n_rows"], n_orbits=res["n_orbits"],
               scale_ceiling=budget / res["tau"])
    if a.no_cert:
        rec["cert"] = "n/a"
    elif res["tau"] >= budget:
        rec["cert"] = "impossible (tau >= budget)"
    else:
        cert_out = os.path.join(BASE, "certs", f"{a.name}.json")
        cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_out, "--s_rat", S_RAT,
               "--rounds", str(a.rounds), "--jobs", str(min(a.jobs, VERIFY_JOBS_CAP)), "--depth", str(a.depth),
               "--time_limit", str(a.cert_time), "--out", cert_out, "--scale", "0",
               "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "96", "--loop_cols"]
        log("    " + " ".join(cmd))
        t1 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        log(p.stdout[-20000:]); log(p.stderr[-3000:])
        rec["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
        rec["cert_seconds"] = round(time.time() - t1, 1)
        rec["worst"] = [l for l in p.stdout.splitlines() if l.strip().startswith("worst")][-3:]
        if p.returncode == 0:
            open(cert_out + ".PASS", "w").write("ok")
    json.dump(rec, open(os.path.join(BASE, "results", f"{a.name}_{a.tag}.json"), "w"), indent=1)
    log("    " + json.dumps(rec))
    print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
