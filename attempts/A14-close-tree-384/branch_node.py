"""
A14 branch_node.py: branch an ALIVE depth-1 node once with A13's wall-first heuristic (NO child on the next corner zone +
coarse 2x2x3 YES boxes on that zone) and solve all children (fixed oracle, pruned alternating LP) with a process pool.
  python branch_node.py --node 2 --parent_result results/n2.json --zone corner3 --workers 8 --time_limit 600
Writes results/br<node>_<zone>/child_<k>.json/.log and results/br<node>_<zone>/children.json (summary).
"""
import argparse, json, math, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, NoFam, Hyp
A13 = os.path.join(os.path.dirname(HERE), "A13-case-lp-bnb")
sys.path.insert(0, A13)
from bnb import make_zones, zone_family, initial_boxes, boxes_compatible, rect_weight   # A13's branching helpers (unchanged)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", type=int, required=True)
    ap.add_argument("--parent_result", required=True)
    ap.add_argument("--zone", default=None, help="corner1/2/3 or side0..3; default = corner with the largest fractional weight")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--time_limit", type=float, default=600)
    ap.add_argument("--s", type=float, default=3.84)
    a = ap.parse_args()
    s = a.s
    res = json.load(open(a.parent_result))
    hyp = Hyp.from_json(res["hyp"])
    packing = [tuple(p) for p in res["packing_images"] if p[3] > 1e-6]
    zones = make_zones(s, 0.6)
    zw = {n: rect_weight(r, packing) for n, r in zones.items()}
    if a.zone is None:
        used = [n for n, r in zones.items() if any(r[0] - 1e-9 <= b.x0 and b.x1 <= r[1] + 1e-9 and r[2] - 1e-9 <= b.y0 and b.y1 <= r[3] + 1e-9 for b in hyp.boxes)]
        cand = [(w, n) for n, w in zw.items() if n.startswith("corner") and n not in used]
        a.zone = max(cand)[1]
    rect = zones[a.zone]
    kind = "corner" if a.zone.startswith("corner") else "side"
    split = (2, 2, 3) if kind == "corner" else (2, 3, 3)
    outdir = os.path.join(HERE, "results", f"br{a.node}_{a.zone}")
    os.makedirs(outdir, exist_ok=True)
    children = [dict(k=0, branch=f"NO {a.zone}", hyp=Hyp(hyp.boxes, list(hyp.nofams) + [zone_family(a.zone, rect)]).to_json(), budget=11 - hyp.m())]
    for b in initial_boxes(rect, s, *split):
        if all(boxes_compatible(b, b2) for b2 in hyp.boxes):
            children.append(dict(k=len(children), branch=f"YES {a.zone} {b!r}", hyp=Hyp(list(hyp.boxes) + [b], hyp.nofams).to_json(), budget=11 - hyp.m() - 1))
    json.dump(dict(node=a.node, zone=a.zone, zone_weights=zw, children=children), open(os.path.join(outdir, "children.json"), "w"), indent=1)
    print(f"node {a.node}: branch on {a.zone} (zone weights {dict((k, round(v, 3)) for k, v in zw.items())}) -> {len(children)} children", flush=True)
    for c in children:
        json.dump(c["hyp"], open(os.path.join(outdir, f"hyp_{c['k']}.json"), "w"))
    procs = {}
    todo = list(children)
    while todo or procs:
        while todo and len(procs) < a.workers:
            c = todo.pop(0)
            tag = f"br{a.node}_{a.zone}/child_{c['k']}"
            cmd = [sys.executable, os.path.join(HERE, "run_node.py"), "--node", str(a.node), "--tag", tag, "--hyp_json", os.path.join(outdir, f"hyp_{c['k']}.json"),
                   "--budget", str(c["budget"]), "--warm", a.parent_result, "--time_limit", str(a.time_limit), "--prune_rows", "6", "--prune_cols", "2"]
            os.makedirs(os.path.join(HERE, "logs", f"br{a.node}_{a.zone}"), exist_ok=True)
            procs[c["k"]] = (subprocess.Popen(cmd, stdout=open(os.path.join(HERE, "logs", tag + ".stdout"), "w"), stderr=subprocess.STDOUT), c)
            print(f"  launched child {c['k']}: {c['branch']} (budget {c['budget']})", flush=True)
        for k in list(procs):
            p, c = procs[k]
            if p.poll() is not None:
                del procs[k]
                rp = os.path.join(outdir, f"child_{k}.json")
                if os.path.exists(rp):
                    r = json.load(open(rp))
                    c.update(tau=r["tau"], converged=r["converged"], minmass=r["minmass"], maxcov=r["maxcov"], slack=r["tau"] - c["budget"], time=r["time"])
                    print(f"  child {k} done: tau={r['tau']:.4f} budget={c['budget']} slack={r['tau']-c['budget']:+.4f} conv={r['converged']} mm={r['minmass']:.3f} mc={r['maxcov']:.3f} t={r['time']:.0f}s | {c['branch']}", flush=True)
                else:
                    c.update(error=True); print(f"  child {k} ERROR", flush=True)
                json.dump(dict(node=a.node, zone=a.zone, zone_weights=zw, children=children), open(os.path.join(outdir, "children.json"), "w"), indent=1)
        time.sleep(3)
    print("all children done")


if __name__ == "__main__":
    main()
