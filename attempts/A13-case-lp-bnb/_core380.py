import json, sys
from caselp import *
s = 3.80
hyp = Hyp([Box(0.5, 0.8, 0.5, 0.8, 0, 30)], [])
warm = warm_from_result(json.load(open('../A07-lp-dual/results/v2_s3.80_rowonly.json')))
res = solve_node(s, hyp, 10, sym_kind="C1", warm=warm, time_limit=700, out="results/core380_node.json",
                 max_cols_add=400, col_stop_iter=60, col_stop_cov=1.01)
print("RESULT tau", res["tau"], "conv", res["converged"], "minmass", res["minmass"], "maxcov", res["maxcov"])
