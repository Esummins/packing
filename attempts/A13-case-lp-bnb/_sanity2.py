import json, sys, time
from caselp import *
s = 3.86
e = 1e-6
boxes = [Box(0.5-e, 0.5+e, 0.5-e, 0.5+e, 0, 0.001), Box(s-0.5-e, s-0.5+e, 0.5-e, 0.5+e, 0, 0.001),
         Box(0.5-e, 0.5+e, s-0.5-e, s-0.5+e, 0, 0.001), Box(s-0.5-e, s-0.5+e, s-0.5-e, s-0.5+e, 0, 0.001)]
z = (0.5, 0.75, 1.2, s - 1.2)
x0, x1, y0, y1 = z
zones = [z, (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]
which = sys.argv[1]
nof = [NoFam(*zz, [(0, 90)]) for zz in zones] if which == "noside" else []
hyp = Hyp(boxes, nof)
print([c.to_json()['float'] for c in hyp.cores])
res = solve_node(s, hyp, 7, sym_kind="C1", warm=None, time_limit=900, theta_box="0-2,32-36", out=f"results/sanity2_{which}_b.json", max_cols_add=1500, col_stop_iter=200, col_stop_cov=1.005, max_iter=400)
print("RESULT", which, "tau", res["tau"], "budget 7", "conv", res["converged"], "minmass", res["minmass"], "maxcov", res["maxcov"])
