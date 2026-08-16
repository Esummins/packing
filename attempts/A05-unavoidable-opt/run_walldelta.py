"""Experiment: how large can s0 be if squares whose centre lies within delta of the boundary of the
centre domain D(theta) are exempt from coverage (i.e. only 'interior' squares must be hit)?  This
quantifies how much a Stromquist-style wall case-argument could buy on top of a 10-point set."""
import sys, json, numpy as np
import unavoid
from unavoid import *
recs = [json.loads(l) for l in open('resB10_m0v2.jsonl')]; recs.sort(key=lambda r: -r['s0']); r = recs[0]
p0 = Param(r['group'], r['spec'], r['s0']); z0 = np.array(r['z'])
out = open('wall_delta.jsonl', 'a')
for delta in [float(x) for x in sys.argv[1:]]:
    unavoid.WALL_DELTA = delta
    s_best, z_best, g_best, p_best = find_max_s0(r['group'], r['spec'], z0, r['s0'], m_target=0.0, tol_s=2e-5,
                                                slp_kw=dict(iters=250, nth=90, nc=100, K=40))
    P = p_best.P(z_best)
    wc = worst_configs(P, s_best, nth=180, nc=200, K=20, polish=6)
    rec = dict(delta=delta, s0=float(s_best), g=float(g_best), g_fine=float(wc[0][3]), P=P.tolist(),
               worst=[[float(x) for x in w] for w in wc[:8]])
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(f"delta={delta}: s0={s_best:.5f} g={g_best:.6f} g_fine={wc[0][3]:.6f}", flush=True)
    print(np.round(P, 4).tolist(), flush=True)
