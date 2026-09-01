"""
A55/k3_ext — ladder.py (A54 rung 1+2) re-based on attempts/A55-k4-sweep/k3_ext/ for ONE node (k3_00).

Identical to attempts/A55-k4-sweep/code/ladder.py except that
  * BASE (where results/, certs/, logs/ are written) is k3_ext/, so A55's own artefacts are
    read-only, and
  * merged_warm ALSO globs the A55 scout's artefacts for this node (node json, its resolve*.json
    re-solves and its witness placements) in addition to k3_ext's own accumulating ones.
Everything else — solver flags, pruning discipline, certification loop — is A55 code, unmodified.
A53/A55 results are read, never written.  A29 untouched.
"""
import argparse, glob, json, math, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))                     # .../A55-k4-sweep/k3_ext
A55 = os.path.abspath(os.path.join(BASE, ".."))                      # .../A55-k4-sweep
A53 = os.path.abspath(os.path.join(A55, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A55, "code"))
import caselp
from caselp import Hyp, solve_node
from run_skel import hyp_from_slots, S0F

S_RAT = "969271/250000"


def merged_warm(name, extra_sources=()):
    """union of atoms and rows over every artefact for this node (A53, A55 scout, k3_ext passes)
    + the exact verifier's witness placements, jittered."""
    srcs = [os.path.join(A53, "results", "nodes", f"{name}.json"),
            os.path.join(A55, "results", "nodes", f"{name}.json")]
    srcs += sorted(glob.glob(os.path.join(A53, "certs_wip", f"{name}.resolve*.json")))
    srcs += sorted(glob.glob(os.path.join(A55, "certs", f"{name}.resolve*.json")))
    srcs += sorted(glob.glob(os.path.join(A55, "results", "nodes", f"{name}.prev*.json")))
    srcs += sorted(glob.glob(os.path.join(BASE, "results", "nodes", f"{name}.json")))
    srcs += sorted(glob.glob(os.path.join(BASE, "results", "nodes", f"{name}.prev*.json")))
    srcs += sorted(glob.glob(os.path.join(BASE, "certs", f"{name}.resolve*.json")))
    # checkpoints of interrupted passes: {"orbits": [[x,y]], "rows": [[cx,cy,th]]}
    srcs += sorted(glob.glob(os.path.join(BASE, "results", "nodes", f"{name}_state*.json")))
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
        for o in d.get("orbits", []):           # checkpoint columns
            k = (round(o[0], 7), round(o[1], 7))
            if k not in seen_a:
                seen_a.add(k); atoms.append((o[0], o[1]))
        for r in d.get("rows", []):             # checkpoint rows
            if not (isinstance(r, (list, tuple)) and len(r) == 3):
                continue
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k); rows.append((r[0], r[1], r[2]))
        for a in d.get("atoms_all", []):
            k = (round(a[0], 7), round(a[1], 7))
            if k not in seen_a:
                seen_a.add(k); atoms.append((a[0], a[1]))
        for r in d.get("rows_all", []):
            k = (round(r[0], 6), round(r[1], 6), round(r[2], 7))
            if k not in seen_r:
                seen_r.add(k); rows.append((r[0], r[1], r[2]))
    for wf in glob.glob(os.path.join(A53, "certs_wip", f"{name}.witnesses.json")) + \
              glob.glob(os.path.join(A55, "certs", f"{name}*.witnesses.json")) + \
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
    ap.add_argument("--name", default="k3_00")
    ap.add_argument("--time_limit", type=float, default=1800)
    ap.add_argument("--max_iter", type=int, default=4000)
    ap.add_argument("--rounds", type=int, default=6)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--scale_cap", type=float, default=1.4)
    ap.add_argument("--cert_time", type=float, default=600)
    ap.add_argument("--no_cert", action="store_true")
    ap.add_argument("--tag", default="e1")
    ap.add_argument("--max_cols_add", type=int, default=350)
    ap.add_argument("--prune_cols", type=int, default=3)
    ap.add_argument("--col_stop_cov", type=float, default=1.002)
    ap.add_argument("--plain_resolve", action="store_true")
    ap.add_argument("--cert_only", action="store_true",
                    help="skip rung 1; certify the node json already in k3_ext/results/nodes")
    a = ap.parse_args()

    nts = os.path.join(BASE, "results", "name_to_slots.json")
    if not os.path.exists(nts):
        nts = os.path.join(A55, "results", "name_to_slots.json")
    slots = [tuple(p) for p in json.load(open(nts))[a.name]]
    k = len(slots)
    budget = 11 - k
    hyp = hyp_from_slots(slots)
    logp = os.path.join(BASE, "logs", f"{a.name}_{a.tag}.log")
    lf = open(logp, "a", buffering=1)
    def log(*x):
        print(*x, file=lf, flush=True)
    node_out = os.path.join(BASE, "results", "nodes", f"{a.name}.json")
    log(f"=== k3_ext {a.name} {a.tag} {time.strftime('%Y-%m-%d %H:%M:%S')} k={k} budget={budget} "
        f"cert_only={a.cert_only}")
    t0 = time.time()
    if a.cert_only:
        res = json.load(open(node_out))
        dt = 0.0
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
        log(f"    rung1 done tau={res['tau']:.6f} budget={budget} conv={res['converged']} "
            f"minmass={res['minmass']:.6f} maxcov={res['maxcov']:.6f} ({dt:.0f}s)")
    rec = dict(name=a.name, k=k, budget=budget, tau=res["tau"], converged=res["converged"],
               minmass=res["minmass"], maxcov=res["maxcov"], eta=res["tau"] - budget,
               lp_seconds=dt, rung="1", tag=a.tag,
               n_rows=res["n_rows"], n_orbits=res["n_orbits"],
               scale_ceiling=budget / res["tau"])

    if a.no_cert:
        rec["cert"] = "n/a"
    elif res["tau"] >= budget:
        rec["cert"] = "impossible (tau >= budget)"
    else:
        rec["scale_cap"] = a.scale_cap
        cert_out = os.path.join(BASE, "certs", f"{a.name}.json")
        cmd = [sys.executable, os.path.join(A55, "code", "certify.py"), node_out,
               "--s_rat", S_RAT, "--rounds", str(a.rounds), "--jobs", str(a.jobs),
               "--depth", str(a.depth), "--time_limit", str(a.cert_time),
               "--out", cert_out, "--scale", "0", "--scale_cap", f"{a.scale_cap:.5f}",
               "--max_w", "96"]
        if not a.plain_resolve:
            cmd.append("--loop_cols")
        log("    " + " ".join(cmd))
        t1 = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True)
        log(p.stdout[-20000:]); log(p.stderr[-3000:])
        rec["cert"] = "PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"
        rec["cert_seconds"] = time.time() - t1
        if p.returncode == 0:
            open(cert_out + ".PASS", "w").write("ok")
    json.dump(rec, open(os.path.join(BASE, "results", f"{a.name}_{a.tag}.json"), "w"), indent=1)
    log("    " + json.dumps(rec))
    print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
