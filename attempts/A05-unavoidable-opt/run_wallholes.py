"""Holes of the 'wall-exempt' optimised set: re-optimise the 3-4-3 set at s0 in {3.7889, 3.80} requiring
coverage only of squares whose centre is >= delta from the boundary of D(theta) (WALL_DELTA=delta), then
analyse the holes on the FULL domain (WALL_DELTA=0).  Output: wall_holes.json, wall_holes_s*.png"""
import sys, json, numpy as np
import unavoid
from unavoid import *
from holes import hole_analysis
from plot_set import plot
delta = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
recs = [json.loads(l) for l in open('wall_delta.jsonl')]
r = [x for x in recs if abs(x['delta'] - delta) < 1e-9][0]
P0 = np.array(r['P']); s_from = r['s0']
out = []
for s0 in [3.7889, 3.80]:
    param = Param('axes', ['g', 'v', 'v', 'h'], s0)
    P1 = (P0 - s_from / 2) * (s0 / s_from) + s0 / 2
    z = param.z_from_P(P1)
    unavoid.WALL_DELTA = delta
    z, g, _, _ = slp(param, z, s0, iters=250, nth=90, nc=100, K=40)
    unavoid.WALL_DELTA = 0.0
    P = param.P(z)
    H = hole_analysis(P, s0)
    H['P'] = P.tolist(); H['wall_delta_used_in_optimisation'] = delta; H['max_d_interior(delta)'] = float(g)
    wc = worst_configs(P, s0, nth=180, nc=200, K=30, polish=8)
    H['worst'] = [[float(x) for x in w] for w in wc[:12]]
    plot(P, s0, f'wall_holes_s{s0:.3f}.png', title=f'3-4-3 set optimised for interior squares (wall exempt {delta}) at s0={s0}: max d={H["max_d"]:+.4f}, uncovered vol frac={H["vol_frac_uncovered"]:.1e}', worst=wc)
    print(f"s0={s0}: interior max d (delta={delta}) = {g:+.5f}; full-domain max d = {H['max_d']:+.5f}; uncovered vol frac = {H['vol_frac_uncovered']:.3e}; comps={H['n_components']}", flush=True)
    for c in H['components'][:10]:
        print("   comp: max_d=%.4f at c=(%.3f,%.3f) th=%.1f deg; theta range %s; wall=%s; vol=%.2e" % (
            c['max_d'], c['worst']['cx'], c['worst']['cy'], c['worst']['theta_deg'], c['theta_deg_range'], c['touches_wall'], c['vol_frac']), flush=True)
    print(np.round(P, 4).tolist(), flush=True)
    out.append(H)
json.dump(out, open('wall_holes.json', 'w'), indent=1)
