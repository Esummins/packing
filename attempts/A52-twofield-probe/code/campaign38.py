#!/usr/bin/env python3
"""A38 task 2: the LEVEL-1 campaign at s0 = 969271/250000, budget 10, 216 cover nodes.

Config (design.md AMENDMENT 1):
  * W1 as an LP ROW FILTER is OFF (it costs +50% wall for delta-tau = 0).
  * W1/W2 stay as the cheap NODE-KILL test: c_j = mlow_box(core inflated by one grid cell);
    kill if c_j > thr_cert (W1) or c_j > thr_node from the other cores (W2).  ~ms per node.
  * Then A27's level-1 case LP (solve_node verbatim through node38.solve_a38_node with w1=0).

Order: interior-first (distance of the cell centre from the container centre, ascending).
Hard wall cap: no NEW node is started more than --wall minutes after the campaign start;
those nodes are recorded 'notrun'.  Resumable: per-node results/l1_nodes/node_XXX.rec.json.

    python campaign38.py --workers 6 --time_limit 480 --wall 150
"""
from __future__ import annotations

import argparse, json, math, os, sys, time, traceback
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import concurrent.futures as cf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")
LOGS = os.path.join(HERE, "..", "logs")
NODEDIR = os.path.join(RES, "l1_nodes")
NODELOGS = os.path.join(LOGS, "l1")

S0F = 3.877084
S0_STR = "969271/250000"


def _work(args):
    (idx, bjson, budget, tl, eps_geo, deadline, keep_full) = args
    t0 = time.time()
    rec = dict(idx=idx, box=bjson)
    rp = os.path.join(NODEDIR, "node_%03d.rec.json" % idx)
    try:
        if time.time() >= deadline:
            rec.update(status="notrun", seconds=0.0)
            json.dump(rec, open(rp, "w"), indent=1)
            return rec
        import lpbox, fieldcut as fc, node38
        from caselp import Box
        B = Box.from_json(bjson)
        mk = node38.mask()
        # ---- cheap W1/W2 node-kill test (always, filter-independent)
        verdict, det = node38.w1_node_scan([B], mk)
        rec["c_core"] = det["core_mlow"][0]
        rec["thr_cert"] = det["thr_cert"]
        rec["thr_node"] = det.get("thr_node")
        rec["w1_verdict"] = verdict
        if verdict is not None:
            rec.update(status="w1kill", w1kind=verdict, kill_thr=det.get("kill_thr"),
                       seconds=time.time() - t0)
            json.dump(rec, open(rp, "w"), indent=1)
            return rec
        # ---- the LP (W1 row filter OFF)
        out = os.path.join(NODEDIR, "node_%03d.json" % idx)
        lg = os.path.join(NODELOGS, "n%03d.log" % idx)

        def log(*a):
            with open(lg, "a") as f:
                f.write(" ".join(str(x) for x in a) + "\n")
        log("### A38 L1 node %d %r budget=%d eps_geo=%g w1_filter=OFF c_core=%.9f"
            % (idx, B, budget, eps_geo, rec["c_core"]))
        r = node38.solve_a38_node(S0F, [B], budget, w1=False, w2=False, time_limit=tl,
                                  out=(out if keep_full else None), log=log, eps_geo=eps_geo,
                                  sym_kind="C1", theta_box="0-90",
                                  checkpoint=out.replace(".json", "_state.json"))
        st = r["status"]
        maxcov = r.get("maxcov")
        if st == "dead(T1)":
            status = "dead(T1)"
        elif st == "alive" and maxcov is not None and maxcov <= 1 + 1e-3:
            status = "alive(LP)"
        else:
            status = "undecided"
        rec.update(status=status, lp_status=st, tau=r["tau"], slack=r["slack"],
                   converged=r["converged"], minmass=r["minmass"], maxcov=maxcov,
                   rows=r["n_rows"], orbits=r["n_orbits"], iters=r.get("iters"),
                   last_added_rows=r.get("last_added_rows"),
                   last_added_cols=r.get("last_added_cols"), seconds=time.time() - t0)
        log("RESULT " + json.dumps({k: v for k, v in rec.items() if k != "box"}))
        json.dump(rec, open(rp, "w"), indent=1)
        return rec
    except Exception:
        rec.update(status="error", error=traceback.format_exc()[-1500:], seconds=time.time() - t0)
        try:
            json.dump(rec, open(rp, "w"), indent=1)
        except Exception:
            pass
        return rec


def order_nodes(nodes, s=S0F):
    """interior-first: distance of the cell centre from the container centre, ascending."""
    m = s / 2.0
    def key(nd):
        b = nd["box"]
        cx, cy = (b["x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0
        return (math.hypot(cx - m, cy - m), nd["idx"])
    return sorted(nodes, key=key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--time_limit", type=float, default=480)
    ap.add_argument("--wall", type=float, default=150, help="minutes; stop LAUNCHING after this")
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--eps_geo", type=float, default=1e-4)
    ap.add_argument("--cover", default=os.path.join(RES, "cover_l1.json"))
    ap.add_argument("--limit", type=int, default=0, help="debug: only the first N in order")
    ap.add_argument("--no_full", action="store_true", help="do not keep the full node json")
    a = ap.parse_args()
    os.makedirs(NODEDIR, exist_ok=True)
    os.makedirs(NODELOGS, exist_ok=True)
    cov = json.load(open(a.cover))
    assert cov["s"] == S0_STR and cov["budget"] == a.budget, (cov["s"], cov["budget"])
    nodes = order_nodes(cov["nodes"])
    if a.limit:
        nodes = nodes[:a.limit]
    t_start = time.time()
    deadline = t_start + a.wall * 60.0
    jobs, done = [], {}
    for nd in nodes:
        rp = os.path.join(NODEDIR, "node_%03d.rec.json" % nd["idx"])
        if os.path.exists(rp):
            try:
                r = json.load(open(rp))
                if r.get("status") not in (None, "notrun", "error"):
                    done[nd["idx"]] = r
                    continue
            except Exception:
                pass
        jobs.append((nd["idx"], nd["box"], a.budget, a.time_limit, a.eps_geo, deadline,
                     not a.no_full))
    print("A38 L1 campaign: %d nodes, %d already done, %d to run, %d workers, "
          "time_limit %.0fs, wall cap %.0f min" % (len(nodes), len(done), len(jobs),
                                                   a.workers, a.time_limit, a.wall), flush=True)
    order = {nd["idx"]: p for p, nd in enumerate(nodes)}
    n_done = 0
    with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(_work, j): j[0] for j in jobs}
        for fu in cf.as_completed(futs):
            r = fu.result()
            done[r["idx"]] = r
            n_done += 1
            print("[%4.0fs %3d/%3d] node %3d (rank %3d) %-10s tau=%s c=%s %.0fs"
                  % (time.time() - t_start, n_done, len(jobs), r["idx"], order.get(r["idx"], -1),
                     r["status"], ("%.4f" % r["tau"]) if r.get("tau") is not None else "-",
                     ("%.3f" % r["c_core"]) if r.get("c_core") is not None else "-",
                     r.get("seconds", 0)), flush=True)
    out = os.path.join(RES, "l1_campaign_raw.json")
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), s=S0_STR, budget=a.budget,
                   workers=a.workers, time_limit=a.time_limit, wall_min=a.wall,
                   eps_geo=a.eps_geo, w1_row_filter=False, seconds=time.time() - t_start,
                   order="interior-first (|cell centre - container centre|)",
                   records=[done[i] for i in sorted(done)]), open(out, "w"), indent=1)
    print("wrote", out, "wall %.1f min" % ((time.time() - t_start) / 60.0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
