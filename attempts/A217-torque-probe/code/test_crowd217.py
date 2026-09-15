import sys, os, json, time, math, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geom217 as G, opt217 as O, crowd217 as C, search217 as S
delta = 0.05
rng = np.random.default_rng(5)
seeds = S.load_cp85()
for tag, z0 in [('cp85_0', seeds[0]), ('cp85_12', seeds[12]), ('rand', O.random_start(rng, 4.8)), ('rand2', O.random_start(rng, 4.8))]:
    t0 = time.time()
    desq = C.designate_fixed(z0)
    z1, ok = C.crowd_feasible_start(z0, desq, delta)
    z, h = O.local_opt(z1, extra=C.make_extra_fixed(desq, delta))
    sm = O.summary(z, extra_active=C.active_crowd_fixed(z, desq, delta))
    n2 = sum(1 for c, m in sm['meeters'].items() if len(m) >= 2)
    print('%s feas %s s0 %.3f -> s %.6f res %.1e rows %d crowd_active %d lam %s settled %d n2 %d gaps %.1e %.1e outer %d status %s %.1fs' % (tag, ok, z1[33], sm['s'], sm['fj_res'], sm['n_rows'], sm['n_crowd_active'], [round(v, 4) for v in sm['crowd_lam']], sm['n_settled'], n2, sm['min_pair_gap'], sm['min_wall_gap'], len(h), [x[3] for x in h[-3:]], time.time() - t0), flush=True)
