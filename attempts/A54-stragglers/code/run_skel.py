"""
A53: residual-region guard LP for one pinned skeleton.

Pins each skeleton slot EXACTLY (degenerate core box x0=x1, y0=y1, th0=th1=0; caselp's
core machinery gives a rational core square of half-side 1/2 - O(1e-7) inside the true
square -- sound, conservative). Budget = 11 - k. The node LP is the guard LP on the
residual region: min mu(total) s.t. mu(Q) >= 1 for every admissible placement not
provably meeting a pinned core. tau < budget => stratum "skeleton contains S" is DEAD
(kills every skeleton superset of S; exact certification via certify.py is the arbiter).
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import caselp
from caselp import Hyp, Box, solve_node

S0F = 969271 / 250000  # 3.877084


def hyp_from_slots(slots):
    boxes = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    return Hyp(boxes, [])


def run(name, slots, outdir, time_limit=300, max_iter=300, log_path=None, warm_from=None):
    k = len(slots)
    budget = 11 - k
    hyp = hyp_from_slots(slots)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"{name}.json")
    lf = open(log_path, "a", buffering=1) if log_path else None
    log = (lambda *a: print(*a, file=lf, flush=True)) if lf else (lambda *a: None)
    warm = None
    if warm_from and os.path.exists(warm_from):
        from caselp import warm_from_result
        warm = warm_from_result(json.load(open(warm_from)))
    res = solve_node(S0F, hyp, budget, sym_kind="C1", time_limit=time_limit,
                     max_iter=max_iter, out=None, log=log, warm=warm)
    res["skeleton_name"] = name
    res["skeleton_slots"] = [[x, y] for (x, y) in slots]
    res["k"] = k
    with open(out, "w") as f:
        json.dump(res, f)
    if lf:
        lf.close()
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--slots", required=True, help="json list [[x,y],...] (floats)")
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "nodes"))
    ap.add_argument("--time_limit", type=float, default=300)
    ap.add_argument("--max_iter", type=int, default=300)
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    slots = [tuple(p) for p in json.loads(a.slots)]
    res = run(a.name, slots, a.outdir, a.time_limit, a.max_iter, a.log)
    print(json.dumps(dict(name=a.name, k=res["k"], budget=res["budget"], tau=res["tau"],
                          converged=res["converged"], dead=res["dead"],
                          dead_unconverged=res["dead_unconverged"])))
