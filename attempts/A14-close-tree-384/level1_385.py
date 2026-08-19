"""
A14 level1_385.py: root (D4) + first corner level (NO all corners [D4] + 12 corner-0 boxes [C1]) at s = 3.85, fixed oracle,
pruned alternating LPs, pool of workers.   python level1_385.py --workers 10 --time_limit 600
Writes results/l1_385/node_<k>.json/.log and results/l1_385/summary.json.
"""
import argparse, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, NoFam, Hyp
A13 = os.path.join(os.path.dirname(HERE), "A13-case-lp-bnb")
sys.path.insert(0, A13)
from bnb import make_zones, zone_family, initial_boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, default=3.85)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--time_limit", type=float, default=600)
    ap.add_argument("--root_time", type=float, default=900)
    ap.add_argument("--only", default=None, help="comma-separated node indices to run")
    a = ap.parse_args()
    s = a.s
    zones = make_zones(s, 0.6)
    outdir = os.path.join(HERE, "results", f"l1_{str(s).replace('.', '')}")
    os.makedirs(outdir, exist_ok=True); os.makedirs(os.path.join(HERE, "logs", os.path.basename(outdir)), exist_ok=True)
    nodes = [dict(k=0, branch="root", hyp=Hyp().to_json(), budget=11, warm=os.path.join(os.path.dirname(HERE), "A07-lp-dual", "results", f"v2_s{s:.2f}.json"), tl=a.root_time),
             dict(k=1, branch="NO(all corners) [D4]", hyp=Hyp([], [zone_family(n, zones[n]) for n in ("corner0", "corner1", "corner2", "corner3")]).to_json(), budget=11,
                  warm=os.path.join(A13, "results", "t384c", "node_1.json"), tl=a.time_limit)]
    for b in initial_boxes(zones["corner0"], s, 2, 2, 3):
        nodes.append(dict(k=len(nodes), branch=f"YES corner0 {b!r} [WLOG]", hyp=Hyp([b]).to_json(), budget=10,
                          warm=os.path.join(A13, "results", "t384c", "node_2.json"), tl=a.time_limit))
    for nd in nodes:
        json.dump(nd["hyp"], open(os.path.join(outdir, f"hyp_{nd['k']}.json"), "w"))
    sel = None if a.only is None else {int(x) for x in a.only.split(",")}
    todo = [nd for nd in nodes if sel is None or nd["k"] in sel]
    print(f"s={s}: {len(todo)} nodes", flush=True)
    procs = {}
    while todo or procs:
        while todo and len(procs) < a.workers:
            nd = todo.pop(0)
            tag = f"{os.path.basename(outdir)}/node_{nd['k']}"
            cmd = [sys.executable, os.path.join(HERE, "run_node.py"), "--node", "0", "--s", str(s), "--tag", tag, "--hyp_json", os.path.join(outdir, f"hyp_{nd['k']}.json"),
                   "--budget", str(nd["budget"]), "--warm", nd["warm"], "--time_limit", str(nd["tl"]), "--prune_rows", "6", "--prune_cols", "2"]
            procs[nd["k"]] = (subprocess.Popen(cmd, stdout=open(os.path.join(HERE, "logs", tag + ".stdout"), "w"), stderr=subprocess.STDOUT), nd)
            print(f"  launched node {nd['k']}: {nd['branch']} (budget {nd['budget']})", flush=True)
        for k in list(procs):
            p, nd = procs[k]
            if p.poll() is not None:
                del procs[k]
                rp = os.path.join(outdir, f"node_{k}.json")
                if os.path.exists(rp):
                    r = json.load(open(rp))
                    nd.update(tau=r["tau"], converged=r["converged"], minmass=r["minmass"], maxcov=r["maxcov"], slack=r["tau"] - nd["budget"], time=r["time"])
                    print(f"  node {k} done: tau={r['tau']:.4f} budget={nd['budget']} slack={r['tau']-nd['budget']:+.4f} conv={r['converged']} mm={r['minmass']:.3f} mc={r['maxcov']:.3f} t={r['time']:.0f}s | {nd['branch']}", flush=True)
                else:
                    nd.update(error=True); print(f"  node {k} ERROR", flush=True)
                json.dump(dict(s=s, nodes=nodes), open(os.path.join(outdir, "summary.json"), "w"), indent=1)
        time.sleep(3)
    print("done")


if __name__ == "__main__":
    main()
