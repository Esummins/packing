"""Pinned-corner variant: corner orbit fixed at (1,1) etc. (so corner boxes are handled by Stromquist's Lemma 1),
squares within delta of a wall exempt (WALL_DELTA), optimise the remaining 3 parameters (v,v,h) for max s0."""
import sys, json, numpy as np
import unavoid
from unavoid import *
from unavoid import _transfer
from holes import hole_analysis
from plot_set import plot
delta = float(sys.argv[1])
unavoid.WALL_DELTA = delta
s_init = 3.76
param = Param('axes', ['G', 'v', 'v', 'h'], s_init)
z0 = np.array([0.575, 1.45, 1.0]) * 1.0
z0[0] = 1.5 - s_init / 4; z0[1] = 0.5 + s_init / 4
if len(sys.argv) > 2:   # resume: s0 and P given from a previous run's log
    s_best = float(sys.argv[2]); p_best = Param('axes', ['G', 'v', 'v', 'h'], s_best)
    z_best = p_best.z_from_P(np.array(json.loads(sys.argv[3]))); g_best = float('nan')
else:
    s_best, z_best, g_best, p_best = find_max_s0('axes', ['G', 'v', 'v', 'h'], z0, s_init, m_target=0.0, tol_s=2e-5,
                                                slp_kw=dict(iters=250, nth=90, nc=100, K=40))
P = p_best.P(z_best)
print(f"delta={delta} pinned corners: s0={s_best:.5f} g={g_best:.6f}", flush=True)
print(np.round(P, 4).tolist(), flush=True)
out = dict(delta=delta, s0=float(s_best), g=float(g_best), P=P.tolist(), holes={})
for s0 in [3.7889, 3.80, s_best]:
    pm = Param('axes', ['G', 'v', 'v', 'h'], s0)
    z = _transfer(p_best, z_best, pm)
    unavoid.WALL_DELTA = delta
    z, g, _, _ = slp(pm, z, s0, iters=250, nth=90, nc=100, K=40)
    unavoid.WALL_DELTA = 0.0
    P = pm.P(z)
    H = hole_analysis(P, s0); H['P'] = P.tolist(); H['interior_max_d'] = float(g)
    wc = worst_configs(P, s0, nth=180, nc=200, K=30, polish=8); H['worst'] = [[float(x) for x in w] for w in wc[:12]]
    plot(P, s0, f'pinned_holes_s{s0:.3f}.png', title=f'corners pinned at (1,1), wall-exempt {delta}: s0={s0:.4f}, interior max d={g:+.4f}, full max d={H["max_d"]:+.4f}', worst=wc)
    print(f"s0={s0:.4f}: interior max d = {g:+.5f}; full-domain max d = {H['max_d']:+.5f}; uncovered vol frac = {H['vol_frac_uncovered']:.3e}; comps={H['n_components']}", flush=True)
    for c in H['components'][:8]:
        print("   comp: max_d=%.4f at c=(%.3f,%.3f) th=%.1f deg; theta range %s; wall=%s; vol=%.2e" % (
            c['max_d'], c['worst']['cx'], c['worst']['cy'], c['worst']['theta_deg'], c['theta_deg_range'], c['touches_wall'], c['vol_frac']), flush=True)
    print(np.round(P, 4).tolist(), flush=True)
    out['holes'][f'{s0:.4f}'] = H
json.dump(out, open(f'pinned_delta{delta}.json', 'w'), indent=1)
