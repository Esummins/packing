import cProfile, pstats, json, sys
sys.argv=['x']
import caselp, lpbox
from caselp import *
res = json.load(open('../A07-lp-dual/results/v2_s3.80_rowonly.json'))
warm = warm_from_result(res)
hyp = Hyp()
pr = cProfile.Profile(); pr.enable()
r = solve_node(3.80, hyp, 11, sym_kind='C1', warm=warm, time_limit=60, max_iter=4, fine=False)
pr.disable()
pstats.Stats(pr).sort_stats('cumulative').print_stats(25)
