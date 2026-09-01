"""
A54 rung 1+2 driver for ONE straggler stratum.

Rung 1 (CONVERGE): re-solve the residual guard LP warm-started from the UNION of every row
and atom A53 ever produced for this node (node json, all certify re-solves, and the witness
placements of the failed exact verifications), with row pruning OFF (so tau is monotone in the
row set and the measure only gets more feasible) and column generation ON without a wall cap.
Rung 2 (TIGHTER SEAL): certify with the LARGEST scale the budget allows (A53 capped at 1.03 and
never used the headroom of the loose nodes), witness-feedback rounds as in A39/certify.py.

Everything is a copy of A53 code (unmodified); A53's own results are read, never written.
"""
import argparse, glob, json, math, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, HERE)
import caselp
from caselp import Hyp, solve_node
from run_skel import hyp_from_slots, S0F

S_RAT = "969271/250000"


def merged_warm(name, extra_sources=()):
    """union of atoms and rows over every A53 artefact for this node (+ witness placements)"""
    srcs = [os.path.join(A53, "results", "nodes", f"{name}.json"),
            os.path.join(A53, "results", "nodes", f"{name}.json.v1")]
    srcs += sorted(glob.glob(os.path.join(A53, "certs_wip", f"{name}.resolve*.json")))
    srcs += sorted(glob.glob(os.path.join(BASE, "results", "nodes", f"{name}.prev*.json")))
    srcs += sorted(glob.glob(os.path.join(BASE, "certs", f"{name}.resolve*.json")))
    srcs += list(extra_sources)
    atoms, rows, seen_a, seen_r = [], [], set(), set()
    used = []
    for p in srcs:
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        used.append(os.path.basename(p))
        for a in d.get("atoms_all", []):
            k = (round(a[0], 7), round(a[1], 7))
            if k not in seen_a:
                seen_a.add(k); atoms.append((a[0], a[1]))
        for r in d.get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k); rows.append((r[0], r[1], r[2]))
    # witness placements (the exact verifier's holes) from A53 and from A54
    for wf in glob.glob(os.path.join(A53, "certs_wip", f"{name}.witnesses.json")) + \
              glob.glob(os.path.join(BASE, "certs", f"{name}*.witnesses.json")):
        try:
            W = json.load(open(wf))["witnesses"]
        except Exception:
            continue
        used.append(os.path.basename(wf))
        for w in W:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            for dx, dy in ((0, 0), (0.003, 0), (-0.003, 0), (0, 0.003), (0, -0.003),
                           (0.006, 0.006), (-0.006, -0.006), (0.006, -0.006), (-0.006, 0.006)):
                for dth in (0.0, 0.004, -0.004):
                    rows.append((p["cx_float"] + dx, p["cy_float"] + dy, th + dth))
    return dict(atoms=atoms, rows=rows), used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--time_limit", type=float, default=1800)
    ap.add_argument("--max_iter", type=int, default=4000)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.06)
    ap.add_argument("--cert_time", type=float, default=420)
    ap.add_argument("--no_cert", action="store_true", help="canary mode: never attempt a kill")
    ap.add_argument("--tag", default="r1")
    ap.add_argument("--max_cols_add", type=int, default=1200)
    ap.add_argument("--prune_cols", type=int, default=0, help="drop zero-weight columns with positive reduced cost after this many strikes (memory control; raises tau, never lowers it)")
    ap.add_argument("--col_stop_cov", type=float, default=1.002)
    ap.add_argument("--plain_resolve", action="store_true", help="witness re-solves keep every row (no --loop_cols pruning)")
    a = ap.parse_args()

    slots_map = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    slots = [tuple(p) for p in slots_map[a.name]]
    k = len(slots)
    budget = 11 - k
    hyp = hyp_from_slots(slots)
    warm, used = merged_warm(a.name)
    logp = os.path.join(BASE, "logs", f"{a.name}_{a.tag}.log")
    lf = open(logp, "a", buffering=1)
    def log(*x):
        print(*x, file=lf, flush=True)
    log(f"=== A54 {a.name} rung1 {time.strftime('%Y-%m-%d %H:%M:%S')} k={k} budget={budget}")
    log(f"    merged warm: {len(warm['atoms'])} atoms, {len(warm['rows'])} rows from {used}")
    t0 = time.time()
    node_out = os.path.join(BASE, "results", "nodes", f"{a.name}.json")
    if os.path.exists(node_out):        # checkpoint: keep the previous run as a warm source
        os.replace(node_out, os.path.join(BASE, "results", "nodes", f"{a.name}.prev{int(time.time())}.json"))
    res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.time_limit,
                     max_iter=a.max_iter, out=None, log=log,
                     prune=0, prune_cols=a.prune_cols,      # never drop rows: tau monotone up
                     col_stop_iter=10 ** 6, col_stop_cov=a.col_stop_cov,
                     max_cols_add=a.max_cols_add, max_rows_add=2500,
                     fine_slack=99.0, alternate=True,
                     checkpoint=os.path.join(BASE, "results", "nodes", f"{a.name}_state.json"))
    res["skeleton_name"] = a.name; res["skeleton_slots"] = [[x, y] for (x, y) in slots]; res["k"] = k
    json.dump(res, open(node_out, "w"))
    dt = time.time() - t0
    log(f"    rung1 done tau={res['tau']:.6f} budget={budget} conv={res['converged']} "
        f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} ({dt:.0f}s)")
    rec = dict(name=a.name, k=k, budget=budget, tau=res["tau"], converged=res["converged"],
               minmass=res["minmass"], maxcov=res["maxcov"], eta=res["tau"] - budget,
               lp_seconds=dt, rung="1", n_rows=res["n_rows"], n_orbits=res["n_orbits"])

    if a.no_cert:
        rec["cert"] = "n/a (canary: never certified)"
    elif res["tau"] >= budget:
        rec["cert"] = "impossible (tau >= budget)"
    else:
        rec["scale_cap"] = a.scale_cap
        cert_out = os.path.join(BASE, "certs", f"{a.name}.json")
        cmd = [sys.executable, os.path.join(HERE, "certify.py"), node_out, "--s_rat", S_RAT,
               "--rounds", str(a.rounds), "--jobs", str(a.jobs), "--depth", str(a.depth),
               "--time_limit", str(a.cert_time), "--out", cert_out, "--scale", "0",
               "--scale_cap", f"{a.scale_cap:.5f}", "--max_w", "96"]
        if not a.plain_resolve:      # --loop_cols prunes rows (strikes 6) in the witness re-solves
            cmd.append("--loop_cols")
        log("    " + " ".join(cmd))
        t1 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        log(p.stdout[-8000:]); log(p.stderr[-3000:])
        rec["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
        rec["cert_seconds"] = time.time() - t1
        if p.returncode == 0:
            open(cert_out + ".PASS", "w").write("ok")
    json.dump(rec, open(os.path.join(BASE, "results", f"{a.name}_{a.tag}.json"), "w"), indent=1)
    log("    " + json.dumps(rec))
    print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
