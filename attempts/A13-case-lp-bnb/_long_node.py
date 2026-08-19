"""long, better-converged re-solve of one node's LP: python _long_node.py <node_json> <time_limit> <out>"""
import json, sys
from caselp import *
res = json.load(open(sys.argv[1]))
hyp = Hyp.from_json(res["hyp"]); s = res["s"]; budget = res["budget"]
sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
warm = warm_from_result(res)
r = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=float(sys.argv[2]), out=sys.argv[3],
               max_cols_add=400, col_stop_iter=100, col_stop_cov=1.01, max_iter=400)
print("RESULT tau", r["tau"], "budget", budget, "conv", r["converged"], "minmass", r["minmass"], "maxcov", r["maxcov"])
