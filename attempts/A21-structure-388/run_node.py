"""
A14 run_node.py: (re-)solve one node of A13's t384c tree to convergence.
  python run_node.py --node 2 --tag n2 --time_limit 3600 [--max_cols 1500] [--warm path] [--eps_geo 1e-4]
Node hypotheses/budget/sym are read from A13's results/t384c/tree.json; warm start = A13's node_<id>.json (atoms + rows)
unless --warm is given (an A14 result json is also accepted).  Writes results/<tag>.json (final), results/<tag>_state.json
(checkpoint every iteration) and logs/<tag>.log.
"""
import argparse, json, os, sys, time
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lpbox
import caselp
from caselp import Hyp, solve_node, warm_from_result

A13 = os.path.join(os.path.dirname(HERE), "A13-case-lp-bnb")
TREE = os.path.join(A13, "results", "t384c", "tree.json")


def node_from_tree(nid, tree_path=TREE):
    t = json.load(open(tree_path))
    for n in t["nodes"]:
        if n["id"] == nid:
            return n, t["s"]
    raise KeyError(nid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", type=int, required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--time_limit", type=float, default=3600)
    ap.add_argument("--max_cols", type=int, default=1500)
    ap.add_argument("--max_rows", type=int, default=1500)
    ap.add_argument("--max_iter", type=int, default=1000)
    ap.add_argument("--col_stop_cov", type=float, default=1.01)
    ap.add_argument("--warm", default=None)
    ap.add_argument("--no_warm", action="store_true")
    ap.add_argument("--eps_geo", type=float, default=None)
    ap.add_argument("--fine_slack", type=float, default=99.0)
    ap.add_argument("--hyp_json", default=None, help="override hypotheses (Hyp.to_json format) and use --budget")
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--s", type=float, default=None)
    ap.add_argument("--prune_rows", type=int, default=3, help="delete rows non-binding for this many consecutive solves (0 = never)")
    ap.add_argument("--prune_cols", type=int, default=2, help="delete zero-weight columns with positive reduced cost for this many solves (0 = never)")
    ap.add_argument("--no_alternate", action="store_true", help="add rows and columns in the same iteration (A13 behaviour)")
    ap.add_argument("--warm_state", default=None, help="A14 checkpoint *_state.json (all orbits + rows) to warm start from")
    a = ap.parse_args()
    if a.eps_geo is not None:
        lpbox.EPS_GEO = a.eps_geo
    rec, s = node_from_tree(a.node)
    if a.s is not None:
        s = a.s
    if a.hyp_json:
        hyp = Hyp.from_json(json.load(open(a.hyp_json)))
        budget = a.budget if a.budget is not None else 11 - hyp.m()
    else:
        hyp = Hyp.from_json(rec["hyp"]); budget = rec["budget"]
    sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
    warm = None
    if not a.no_warm:
        wp = a.warm or os.path.join(A13, "results", "t384c", f"node_{a.node}.json")
        if os.path.exists(wp):
            warm = warm_from_result(json.load(open(wp)))
    if a.warm_state:      # union with the checkpoint's orbits and rows
        st = json.load(open(a.warm_state))
        w2 = dict(atoms=[tuple(o) for o in st["orbits"]], rows=[tuple(r) for r in st["rows"]])
        if warm is None:
            warm = w2
        else:
            warm = dict(atoms=list(warm["atoms"]) + w2["atoms"], rows=list(warm["rows"]) + w2["rows"])
    log_path = os.path.join(HERE, "logs", a.tag + ".log")
    out = os.path.join(HERE, "results", a.tag + ".json")

    def log(*x):
        msg = " ".join(str(v) for v in x)
        print(msg, flush=True)
        with open(log_path, "a") as f:
            f.write(msg + "\n")
    log(f"### A14 node {a.node} tag={a.tag} s={s} sym={sym} budget={budget} EPS_GEO={lpbox.EPS_GEO} max_cols={a.max_cols} "
        f"prune_rows={a.prune_rows} prune_cols={a.prune_cols} alternate={not a.no_alternate} "
        f"time_limit={a.time_limit} warm={'yes' if warm else 'no'} hyp: {hyp.describe()}")
    t0 = time.time()
    res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=a.time_limit, max_iter=a.max_iter, out=out, log=log,
                     max_rows_add=a.max_rows, max_cols_add=a.max_cols, col_stop_iter=10 ** 6, col_stop_cov=a.col_stop_cov,
                     fine_slack=a.fine_slack, checkpoint=out.replace(".json", "_state.json"),
                     prune=a.prune_rows, prune_cols=a.prune_cols, alternate=not a.no_alternate)
    log(f"RESULT node {a.node} tag={a.tag}: tau={res['tau']:.6f} budget={budget} slack={res['tau']-budget:+.6f} "
        f"conv={res['converged']} minmass={res['minmass']:.4f} maxcov={res['maxcov']:.4f} rows={res['n_rows']} "
        f"orbits={res['n_orbits']} time={time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
