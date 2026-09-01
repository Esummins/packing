"""A57 calibration probe: cost of ONE YES child under different warm/oracle settings."""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, Hyp, solve_node
from run_skel import S0F
from tree57 import build_children
from warm57 import merged_warm

name = sys.argv[1] if len(sys.argv) > 1 else "k5_16"
idx = int(sys.argv[2]) if len(sys.argv) > 2 else 1
mode = sys.argv[3] if len(sys.argv) > 3 else "atoms"      # atoms | atoms+rows | cold
tl = float(sys.argv[4]) if len(sys.argv) > 4 else 150.0
fs = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
ncols = int(sys.argv[6]) if len(sys.argv) > 6 else 400

kids, bad, slots, rect, grid = build_children(name, "interior", 0.15, 8, 0.6, 0.34)
kid = kids[idx]
W, _ = merged_warm(name, max_rows=30000)
if mode == "atoms":
    warm = dict(atoms=W["atoms"], rows=[])
elif mode == "cold":
    warm = None
elif mode == "small":                      # positive-weight atoms of the parent node only
    A54 = os.path.abspath(os.path.join(HERE, "..", "..", "A54-stragglers"))
    d = json.load(open(os.path.join(A54, "results", "nodes", f"{name}.json")))
    warm = dict(atoms=[(a[0], a[1]) for a in d["atoms_all"]], rows=[])
elif mode == "smallrows":
    A54 = os.path.abspath(os.path.join(HERE, "..", "..", "A54-stragglers"))
    d = json.load(open(os.path.join(A54, "results", "nodes", f"{name}.json")))
    warm = dict(atoms=[(a[0], a[1]) for a in d["atoms_all"]],
                rows=[tuple(r) for r in d["rows_all"]])
else:
    warm = W
t0 = time.time()
res = solve_node(S0F, kid["hyp"], kid["budget"], sym_kind="C1", warm=warm,
                 time_limit=tl, max_iter=900, out=None,
                 log=lambda *x: print(*x, flush=True),
                 prune=0, prune_cols=3, col_stop_iter=10**6, col_stop_cov=1.002,
                 max_cols_add=ncols, max_rows_add=2000, fine_slack=fs, alternate=True)
print(json.dumps(dict(id=kid["id"], mode=mode, tl=tl, fine_slack=fs, budget=kid["budget"],
                      tau=res["tau"], eta=res["tau"] - kid["budget"], conv=res["converged"],
                      minmass=res["minmass"], maxcov=res["maxcov"], rows=res["n_rows"],
                      orbits=res["n_orbits"], wall=round(time.time() - t0, 1))))
json.dump(res, open(os.path.join(HERE, "..", "results", f"probe_{name}_{idx}_{mode}.json"), "w"))
